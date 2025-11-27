#!/usr/bin/env python3
"""
Auto-Polling Haiku Shard - Removes user from the loop

This script runs in background and automatically:
1. Polls MCP bridge every 5 seconds
2. When query arrives, uses Task tool to spawn sub-Haiku
3. Sub-Haiku reads context and answers question
4. Sends response back via bridge
"""

import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')

from agent_bridge_secure import SecureBridge
import json
import time
import subprocess

def spawn_haiku_via_task_tool(question, context_file):
    """
    Spawns a Haiku agent via Claude CLI Task tool (not subprocess.run)

    This simulates what happens when you manually spawn via Task tool,
    but does it programmatically.
    """

    # Create a prompt that instructs Claude CLI to spawn Haiku via Task
    task_prompt = f"""Use the Task tool to spawn a Haiku agent with this exact prompt:

"Read {context_file} and answer this question: {question}

Cite line numbers where you found the information."

subagent_type: general-purpose
model: haiku

Return ONLY the Haiku agent's answer (no other commentary)."""

    # Call Claude CLI in non-interactive mode to execute the Task tool
    cmd = [
        "claude",
        "--dangerously-skip-permissions",
        "-p",
        task_prompt
    ]

    print(f"\n  Spawning Haiku via Task tool...")
    print(f"  Command: claude --dangerously-skip-permissions -p '<task_prompt>'")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            return f"Error spawning Haiku via Task: {result.stderr}", []

        answer = result.stdout.strip()

        # Extract sources
        sources = []
        import re
        sources = re.findall(r'SESSION-RESUME\.md:\d+-?\d*', answer)

        return answer, sources

    except subprocess.TimeoutExpired:
        return "Timeout spawning Haiku via Task tool", []
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}", []

def main():
    if len(sys.argv) < 3:
        print("Usage: python haiku_shard_autopoll.py <conv_id> <token>")
        return 1

    conv_id = sys.argv[1]
    token = sys.argv[2]
    context_file = "/home/setup/infrafabric/SESSION-RESUME.md"

    print("="*80)
    print("AUTO-POLLING HAIKU SHARD - User Removed from Loop")
    print("="*80)
    print(f"\nConversation ID: {conv_id}")
    print(f"Token: {token[:20]}...")
    print(f"Context file: {context_file}")

    # Connect to bridge
    db_path = "/home/setup/infrafabric/.memory_bus/distributed_memory.db"
    bridge = SecureBridge(db_path)

    print(f"\n✓ Connected to MCP bridge")
    print(f"\nAuto-polling mode ENABLED")
    print(f"  - Checks bridge every 5 seconds")
    print(f"  - Spawns Haiku via Task tool on query")
    print(f"  - Sends response automatically")
    print(f"  - NO USER INTERACTION NEEDED")
    print(f"\nPress Ctrl+C to stop\n")

    try:
        poll_count = 0
        while True:
            poll_count += 1

            # Check for messages
            messages = bridge.get_unread_messages(conv_id, "b", token)

            if messages:
                for msg in messages:
                    content = json.loads(msg['message'])

                    if content.get('type') == 'query':
                        query_id = content.get('query_id')
                        question = content.get('question')

                        print(f"\n{'='*80}")
                        print(f"[QUERY RECEIVED] Poll #{poll_count}")
                        print(f"{'='*80}")
                        print(f"  Query ID: {query_id}")
                        print(f"  Question: {question}")

                        # Spawn Haiku via Task tool
                        start_time = time.time()
                        answer, sources = spawn_haiku_via_task_tool(question, context_file)
                        elapsed = time.time() - start_time

                        print(f"\n  ✓ Haiku response in {elapsed:.1f}s")
                        print(f"  Answer preview: {answer[:150]}...")
                        print(f"  Sources: {sources}")

                        # Send response
                        response = json.dumps({
                            "type": "response",
                            "query_id": query_id,
                            "answer": answer,
                            "sources": sources,
                            "shard_id": "haiku_autopoll_shard",
                            "llm_type": "haiku_task_tool",
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
            else:
                # No messages - show periodic status
                if poll_count % 12 == 0:  # Every 60 seconds
                    print(f"  ... polling (#{poll_count}, no queries)")

            # Poll every 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n\nShutting down gracefully...")
        print(f"Total polls: {poll_count}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
