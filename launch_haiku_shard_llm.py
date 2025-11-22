#!/usr/bin/env python3
"""
Launch a REAL Haiku LLM memory shard that loads context and responds via MCP bridge
This version uses actual Claude Haiku LLM instead of Python string searching
"""

import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')

from agent_bridge_secure import SecureBridge
import json
import time
import subprocess
import os

def generate_haiku_response(question, context):
    """
    Spawns a real Claude Haiku subprocess inheriting the user's existing auth.
    Uses the 'claude' CLI tool with --model haiku for cheaper shard operations.
    """
    # Prepare the prompt with context
    # Limit context to first 100K chars to fit in Haiku's 200K token window
    context_snippet = context[:100000]

    full_prompt = f"""You are a Haiku memory shard in the InfraFabric distributed memory system.

Your context (loaded once):
{context_snippet}

Query: {question}

Instructions:
- Answer based ONLY on the loaded context above
- Cite sources as file:line references (e.g., "SESSION-RESUME.md:82-86")
- If not found in context, say "Not found in loaded context"
- Be concise and precise

Answer:"""

    # Define the command - using claude CLI with haiku model
    cmd = ["claude", "--model", "haiku", "-p", full_prompt]

    try:
        # CRITICAL: Pass env=os.environ to inherit Sonnet's auth
        # This ensures the child process sees ~/.anthropic/ config
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=os.environ,  # Inherit parent's API key/auth
            timeout=60       # Prevent hangs
        )

        if result.returncode != 0:
            return f"Error from Haiku LLM: {result.stderr}", []

        answer = result.stdout.strip()

        # Extract sources from answer if present
        sources = []
        if "SESSION-RESUME.md:" in answer:
            # Simple source extraction (could be more sophisticated)
            import re
            sources = re.findall(r'SESSION-RESUME\.md:\d+-\d+', answer)

        return answer, sources

    except subprocess.TimeoutExpired:
        return "Error: Haiku LLM timeout (>60s)", []
    except FileNotFoundError:
        return "Error: 'claude' CLI not found. Install: npm install -g @anthropic-ai/claude-cli", []
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}", []

def main():
    # Get conversation details from command line
    if len(sys.argv) < 4:
        print("Usage: python launch_haiku_shard_llm.py <conv_id> <token> <context_file>")
        return 1

    conv_id = sys.argv[1]
    token = sys.argv[2]
    context_file = sys.argv[3]

    print(f"[HAIKU LLM SHARD] Initializing...")
    print(f"  Conversation: {conv_id}")
    print(f"  Loading context from: {context_file}")

    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print(f"\n⚠️  WARNING: ANTHROPIC_API_KEY not set in environment")
        print(f"  Claude CLI may fail if ~/.anthropic/ config is not present")
        print(f"  To fix: export ANTHROPIC_API_KEY='sk-ant-...'")
        print(f"  Continuing anyway (may use cached credentials)...\n")

    # Load context into memory
    with open(context_file, 'r') as f:
        context = f.read()

    print(f"  ✓ Loaded {len(context)} characters into context")
    print(f"  ✓ Using REAL Haiku LLM (not Python simulation)")

    # Connect to bridge
    db_path = "/home/setup/infrafabric/.memory_bus/distributed_memory.db"
    bridge = SecureBridge(db_path)

    print(f"  ✓ Connected to MCP bridge")
    print(f"\n[HAIKU LLM SHARD] Entering polling loop...")
    print(f"  Checking for queries every 5 seconds...")
    print(f"  Each query spawns a new Haiku subprocess")
    print(f"  Press Ctrl+C to stop\n")

    try:
        while True:
            # Check for messages
            messages = bridge.get_unread_messages(conv_id, "b", token)

            if messages:
                for msg in messages:
                    content = json.loads(msg['message'])

                    if content.get('type') == 'query':
                        query_id = content.get('query_id')
                        question = content.get('question')

                        print(f"[QUERY RECEIVED] ID: {query_id}")
                        print(f"  Question: {question}")
                        print(f"  Spawning Haiku LLM subprocess...")

                        # Generate response using REAL Haiku LLM
                        start_time = time.time()
                        answer, sources = generate_haiku_response(question, context)
                        elapsed = time.time() - start_time

                        print(f"  ✓ Haiku LLM response in {elapsed:.1f}s")
                        print(f"  Answer preview: {answer[:100]}...")

                        # Send response
                        response = json.dumps({
                            "type": "response",
                            "query_id": query_id,
                            "answer": answer,
                            "sources": sources,
                            "shard_id": "haiku_llm_shard_history",
                            "llm_type": "real_haiku",
                            "response_time_sec": round(elapsed, 2)
                        })

                        bridge.send_message(
                            conv_id=conv_id,
                            session_id="b",
                            token=token,
                            message=response,
                            metadata={"action_type": "response"}
                        )

                        print(f"  ✓ Response sent via bridge")
                        print(f"  Sources: {sources}\n")

            # Poll every 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n[HAIKU LLM SHARD] Shutting down gracefully...")
        return 0

if __name__ == "__main__":
    sys.exit(main())
