#!/usr/bin/env python3
"""
DEBUG VERSION: Launch Haiku LLM shard with verbose debugging output
"""

import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')

from agent_bridge_secure import SecureBridge
import json
import time
import subprocess
import os

def generate_haiku_response_DEBUG(question, context):
    """
    DEBUG VERSION: Shows all subprocess details
    """
    print(f"\n{'='*80}")
    print(f"DEBUG: generate_haiku_response() called")
    print(f"{'='*80}")

    # Prepare context
    context_snippet = context[:100000]
    print(f"DEBUG: Context length: {len(context)} chars")
    print(f"DEBUG: Context snippet length: {len(context_snippet)} chars")

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

    print(f"DEBUG: Full prompt length: {len(full_prompt)} chars")
    print(f"DEBUG: Prompt preview (first 200 chars):")
    print(f"  {full_prompt[:200]}...")

    # Define the command
    cmd = ["claude", "--model", "haiku", "-p", full_prompt]

    print(f"\nDEBUG: Command to execute:")
    print(f"  {cmd[0]} {cmd[1]} {cmd[2]} {cmd[3][:50]}...")
    print(f"\nDEBUG: Environment variables (partial):")
    print(f"  ANTHROPIC_API_KEY: {'SET' if os.environ.get('ANTHROPIC_API_KEY') else 'NOT SET'}")
    print(f"  HOME: {os.environ.get('HOME', 'NOT SET')}")
    print(f"  PATH: {os.environ.get('PATH', 'NOT SET')[:100]}...")

    try:
        print(f"\nDEBUG: Calling subprocess.run()...")
        start_time = time.time()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=os.environ,
            timeout=60
        )

        elapsed = time.time() - start_time

        print(f"\nDEBUG: Subprocess completed in {elapsed:.2f}s")
        print(f"DEBUG: Return code: {result.returncode}")
        print(f"DEBUG: stdout length: {len(result.stdout)} chars")
        print(f"DEBUG: stderr length: {len(result.stderr)} chars")

        print(f"\nDEBUG: stdout content:")
        if result.stdout:
            print(f"  {result.stdout[:500]}")
            if len(result.stdout) > 500:
                print(f"  ... (truncated, total {len(result.stdout)} chars)")
        else:
            print(f"  (EMPTY)")

        print(f"\nDEBUG: stderr content:")
        if result.stderr:
            print(f"  {result.stderr[:500]}")
            if len(result.stderr) > 500:
                print(f"  ... (truncated, total {len(result.stderr)} chars)")
        else:
            print(f"  (EMPTY)")

        print(f"\n{'='*80}")

        if result.returncode != 0:
            return f"Error from Haiku LLM (returncode={result.returncode}): {result.stderr}", []

        answer = result.stdout.strip()

        # Extract sources
        sources = []
        if "SESSION-RESUME.md:" in answer:
            import re
            sources = re.findall(r'SESSION-RESUME\.md:\d+-\d+', answer)

        return answer, sources

    except subprocess.TimeoutExpired:
        print(f"\nDEBUG: Subprocess TIMEOUT (>60s)")
        return "Error: Haiku LLM timeout (>60s)", []
    except FileNotFoundError as e:
        print(f"\nDEBUG: FileNotFoundError: {e}")
        return "Error: 'claude' CLI not found. Install: npm install -g @anthropic-ai/claude-cli", []
    except Exception as e:
        print(f"\nDEBUG: Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {type(e).__name__}: {e}", []

def main():
    # Get conversation details from command line
    if len(sys.argv) < 4:
        print("Usage: python launch_haiku_shard_DEBUG.py <conv_id> <token> <context_file>")
        return 1

    conv_id = sys.argv[1]
    token = sys.argv[2]
    context_file = sys.argv[3]

    print(f"{'='*80}")
    print(f"[HAIKU LLM SHARD - DEBUG MODE] Initializing...")
    print(f"{'='*80}")
    print(f"  Conversation: {conv_id}")
    print(f"  Token: {token[:20]}...")
    print(f"  Context file: {context_file}")

    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print(f"\n⚠️  WARNING: ANTHROPIC_API_KEY not set in environment")
        print(f"  Claude CLI may fail if ~/.anthropic/ config is not present")
        print(f"  Continuing anyway (may use cached credentials)...\n")
    else:
        print(f"\n✓ ANTHROPIC_API_KEY is set")

    # Load context into memory
    print(f"\nLoading context file...")
    with open(context_file, 'r') as f:
        context = f.read()

    print(f"  ✓ Loaded {len(context)} characters into context")
    print(f"  ✓ Using REAL Haiku LLM (not Python simulation)")

    # Connect to bridge
    db_path = "/home/setup/infrafabric/.memory_bus/distributed_memory.db"
    bridge = SecureBridge(db_path)

    print(f"  ✓ Connected to MCP bridge")
    print(f"\n{'='*80}")
    print(f"[HAIKU LLM SHARD - DEBUG MODE] Entering polling loop...")
    print(f"{'='*80}")
    print(f"  Checking for queries every 5 seconds...")
    print(f"  Each query spawns a new Haiku subprocess WITH DEBUG OUTPUT")
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

                        print(f"\n{'='*80}")
                        print(f"[QUERY RECEIVED] ID: {query_id}")
                        print(f"{'='*80}")
                        print(f"  Question: {question}")
                        print(f"  Spawning Haiku LLM subprocess WITH DEBUG...\n")

                        # Generate response using REAL Haiku LLM (DEBUG VERSION)
                        start_time = time.time()
                        answer, sources = generate_haiku_response_DEBUG(question, context)
                        elapsed = time.time() - start_time

                        print(f"\n{'='*80}")
                        print(f"  ✓ Haiku LLM response in {elapsed:.1f}s")
                        print(f"{'='*80}")
                        print(f"  Answer length: {len(answer)} chars")
                        print(f"  Answer preview: {answer[:200]}...")
                        print(f"  Sources: {sources}")

                        # Send response
                        response = json.dumps({
                            "type": "response",
                            "query_id": query_id,
                            "answer": answer,
                            "sources": sources,
                            "shard_id": "haiku_llm_shard_DEBUG",
                            "llm_type": "real_haiku_DEBUG",
                            "response_time_sec": round(elapsed, 2)
                        })

                        bridge.send_message(
                            conv_id=conv_id,
                            session_id="b",
                            token=token,
                            message=response,
                            metadata={"action_type": "response"}
                        )

                        print(f"  ✓ Response sent via bridge\n")

            # Poll every 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n[HAIKU LLM SHARD - DEBUG MODE] Shutting down gracefully...")
        return 0

if __name__ == "__main__":
    sys.exit(main())
