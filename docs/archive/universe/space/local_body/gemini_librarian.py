#!/usr/bin/env python3
"""
GEMINI LIBRARIAN - The Archive Node
====================================

Role: Massive Context Storage + Retrieval (1M+ tokens)
Pattern: Hybrid Brain - Replace 4× Haiku shards with single Gemini Archive
Cost: $0.15/1M tokens (30× cheaper than 4× Haiku coordination)
Latency: 1× API call (4× faster than stitching 4 Haiku responses)

Architecture:
  Sonnet (Coordinator)
    ↓
  Publishes findings to Redis channel "queue:context"
    ↓
  Gemini Librarian (Archive Node)
    ↓
  Loads all findings into 1M token buffer
    ↓
  Listens on "queue:archive_query"
    ↓
  Returns answers with source citations

Usage:
  python gemini_librarian.py --mode daemon  # Run as persistent archive node
  python gemini_librarian.py --mode query   # Single query test
"""

import os
import sys
import json
import redis
import uuid
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

try:
    import google.generativeai as genai
except ImportError:
    print("❌ Error: google-generativeai not installed")
    print("📦 Install: pip install google-generativeai")
    sys.exit(1)


@dataclass
class ArchiveQuery:
    """Query structure for archive searches"""
    query_id: str
    question: str
    timestamp: str
    requester: str  # "sonnet", "haiku", "external"


@dataclass
class ArchiveFinding:
    """Archive response structure"""
    finding_id: str
    query_id: str
    answer: str
    sources: List[str]  # List of finding IDs cited
    tokens_used: int
    context_size: int  # Total tokens in archive when queried
    timestamp: str
    worker_id: str


class GeminiLibrarian:
    """
    Gemini 1.5 Flash Archive Node

    Responsibilities:
    1. Load all findings from Redis into 1M token context
    2. Listen for archive queries
    3. Search full context for relevant information
    4. Return answers with source citations
    5. Persist as daemon (never forgets)

    Cost: $0.15/1M tokens (input) + $0.60/1M tokens (output)
    Context: 1,048,576 tokens (1M+ window)
    """

    def __init__(self,
                 redis_host: str = 'localhost',
                 redis_port: int = 6379,
                 model_name: str = 'gemini-2.5-flash-lite'):

        # Initialize Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

        # Redis connection
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )

        # Worker ID
        self.worker_id = f"gemini_librarian_{uuid.uuid4().hex[:8]}"

        # Archive state
        self.context_window = 1_000_000  # 1M tokens
        self.current_context: List[Dict] = []
        self.total_tokens = 0

        print(f"📚 Gemini Librarian initialized: {self.worker_id}")
        print(f"   Model: {model_name}")
        print(f"   Context Window: {self.context_window:,} tokens")
        print(f"   Redis: {redis_host}:{redis_port}")


    def load_context_from_redis(self, max_findings: int = 1000) -> int:
        """
        Load all findings from Redis into context buffer.

        Strategy:
        1. Scan Redis for all keys matching "finding:*"
        2. Load findings chronologically (oldest first)
        3. Stop when approaching 1M token limit
        4. Return number of findings loaded
        """
        print("\n📥 Loading context from Redis...")

        # Get all finding keys
        finding_keys = []
        cursor = 0
        while True:
            cursor, keys = self.redis.scan(
                cursor=cursor,
                match="finding:*",
                count=100
            )
            finding_keys.extend(keys)
            if cursor == 0:
                break

        print(f"   Found {len(finding_keys)} findings in Redis")

        # Load findings
        loaded = 0
        for key in finding_keys[:max_findings]:
            # Check key type (handle both string and hash types)
            key_type = self.redis.type(key)

            finding = None
            if key_type == 'string':
                finding_json = self.redis.get(key)
                if finding_json:
                    finding = json.loads(finding_json)
            elif key_type == 'hash':
                # Load hash fields
                finding = self.redis.hgetall(key)
                # Convert byte keys/values to strings if needed
                if finding and isinstance(list(finding.keys())[0], bytes):
                    finding = {k.decode('utf-8'): v.decode('utf-8') if isinstance(v, bytes) else v
                              for k, v in finding.items()}

            if finding:
                # Estimate tokens (rough: 1 token ≈ 4 chars)
                finding_text = json.dumps(finding)
                estimated_tokens = len(finding_text) // 4

                # Check if we're approaching limit
                if self.total_tokens + estimated_tokens > self.context_window * 0.9:
                    print(f"   ⚠️  Approaching token limit, stopping at {loaded} findings")
                    break

                self.current_context.append(finding)
                self.total_tokens += estimated_tokens
                loaded += 1

        print(f"   ✅ Loaded {loaded} findings (~{self.total_tokens:,} tokens)")
        return loaded


    def format_context_for_query(self) -> str:
        """
        Format all findings into a single context string for Gemini.

        Format:
        FINDING 001 [finding_abc123]
        Timestamp: 2025-11-21T10:30:00
        Worker: claude_haiku_worker_x7f3
        Content: [finding content here]
        ---
        FINDING 002 [finding_def456]
        ...
        """
        context_parts = []

        for idx, finding in enumerate(self.current_context, start=1):
            finding_id = finding.get('finding_id', 'unknown')
            timestamp = finding.get('timestamp', 'unknown')
            worker_id = finding.get('worker_id', 'unknown')
            content = finding.get('content', finding.get('answer', str(finding)))

            context_parts.append(f"""
FINDING {idx:03d} [id:{finding_id}]
Timestamp: {timestamp}
Worker: {worker_id}
Content: {content}
---""")

        return "\n".join(context_parts)


    def query_archive(self, query: ArchiveQuery) -> ArchiveFinding:
        """
        Execute query against full 1M token context.

        Returns:
          ArchiveFinding with answer + source citations
        """
        print(f"\n🔍 Querying archive: {query.question[:60]}...")

        # Format context
        context_text = self.format_context_for_query()

        # Build prompt
        prompt = f"""You are the Archive Node in a distributed AI swarm.
You hold {len(self.current_context)} findings (~{self.total_tokens:,} tokens) of historical context.

ARCHIVE CONTEXT:
{context_text}

QUERY: {query.question}

INSTRUCTIONS:
1. Search the full context above for information relevant to the query
2. Synthesize findings from multiple sources if needed
3. **CRITICAL:** For every claim, cite the finding ID in square brackets like [finding_abc123]
4. If information is not in the archive, respond: "NOT IN ARCHIVE"
5. Be precise and factual - only cite what is actually present in the context

RESPONSE FORMAT:
Answer: [Your synthesized answer with citations like [finding_abc123]]

Sources: [finding_id1, finding_id2, ...]
"""

        # Query Gemini
        response = self.model.generate_content(prompt)

        # Extract citations from response
        import re
        citations = re.findall(r'\[finding_([a-f0-9]+)\]', response.text)
        unique_citations = list(set(citations))

        # Create finding
        finding = ArchiveFinding(
            finding_id=f"archive_{uuid.uuid4().hex[:8]}",
            query_id=query.query_id,
            answer=response.text,
            sources=[f"finding_{c}" for c in unique_citations],
            tokens_used=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
            context_size=self.total_tokens,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            worker_id=self.worker_id
        )

        print(f"   ✅ Answer generated ({finding.tokens_used} tokens)")
        print(f"   📎 Sources cited: {len(finding.sources)}")

        return finding


    def report_finding(self, finding: ArchiveFinding) -> None:
        """Store finding in Redis for retrieval by coordinator"""
        finding_key = f"finding:{finding.finding_id}"
        self.redis.set(finding_key, json.dumps(asdict(finding)))

        # Add to query's finding list
        self.redis.rpush(f"query:{finding.query_id}:findings", finding.finding_id)

        print(f"   💾 Finding stored: {finding_key}")


    def run_daemon(self, poll_interval: int = 2):
        """
        Run as persistent daemon.

        Loop:
        1. Load context from Redis
        2. Check for queries in "queue:archive_query"
        3. Process query → Generate answer → Store finding
        4. Repeat
        """
        print("\n" + "="*60)
        print("🚀 GEMINI LIBRARIAN DAEMON MODE")
        print("="*60)

        # Initial context load
        self.load_context_from_redis()

        print(f"\n👂 Listening on queue:archive_query (poll every {poll_interval}s)")
        print("   Press Ctrl+C to stop\n")

        try:
            while True:
                # Check for query
                query_json = self.redis.lpop("queue:archive_query")

                if query_json:
                    query_data = json.loads(query_json)
                    query = ArchiveQuery(**query_data)

                    print(f"\n📨 Received query: {query.query_id}")

                    # Execute query
                    finding = self.query_archive(query)

                    # Store result
                    self.report_finding(finding)

                    print(f"✅ Query {query.query_id} complete")
                else:
                    # No queries, sleep
                    import time
                    time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("\n\n👋 Gemini Librarian shutting down...")
            print(f"   Processed queries during this session")
            print("   Context retained: {len(self.current_context)} findings")


    def run_single_query(self, question: str, requester: str = "cli") -> ArchiveFinding:
        """Run a single query (for testing)"""
        print("\n" + "="*60)
        print("🔍 GEMINI LIBRARIAN SINGLE QUERY MODE")
        print("="*60)

        # Load context
        self.load_context_from_redis()

        # Create query
        query = ArchiveQuery(
            query_id=f"query_{uuid.uuid4().hex[:8]}",
            question=question,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            requester=requester
        )

        # Execute
        finding = self.query_archive(query)

        # Print result
        print("\n" + "="*60)
        print("RESULT")
        print("="*60)
        print(f"Question: {question}")
        print(f"\nAnswer:\n{finding.answer}")
        print(f"\nSources: {', '.join(finding.sources)}")
        print(f"Tokens Used: {finding.tokens_used}")
        print("="*60)

        return finding


def create_archive_query(question: str, requester: str = "sonnet") -> str:
    """
    Helper: Create archive query and push to Redis queue.

    Returns query_id for retrieving the result.
    """
    r = redis.Redis(host='localhost', decode_responses=True)

    query = ArchiveQuery(
        query_id=f"query_{uuid.uuid4().hex[:8]}",
        question=question,
        timestamp=datetime.utcnow().isoformat() + 'Z',
        requester=requester
    )

    r.rpush("queue:archive_query", json.dumps(asdict(query)))

    print(f"📤 Query posted: {query.query_id}")
    return query.query_id


def main():
    parser = argparse.ArgumentParser(description='Gemini Librarian - Archive Node')
    parser.add_argument('--mode', choices=['daemon', 'query'], default='daemon',
                       help='Run mode: daemon (persistent) or query (single test)')
    parser.add_argument('--question', type=str,
                       help='Question to ask (required for query mode)')

    args = parser.parse_args()

    # Initialize librarian
    librarian = GeminiLibrarian()

    if args.mode == 'daemon':
        librarian.run_daemon()
    elif args.mode == 'query':
        if not args.question:
            print("❌ Error: --question required for query mode")
            sys.exit(1)
        librarian.run_single_query(args.question)


if __name__ == "__main__":
    main()
