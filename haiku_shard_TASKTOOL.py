#!/usr/bin/env python3
"""
Haiku Shard using TASK TOOL (not subprocess)

This script runs INSIDE a Haiku Claude Code session.
Instead of spawning subprocess, it outputs instructions for Haiku
to use its own Task tool to spawn sub-agents.
"""

import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')

from agent_bridge_secure import SecureBridge
import json
import time

def main():
    if len(sys.argv) < 3:
        print("Usage: python haiku_shard_TASKTOOL.py <conv_id> <token>")
        return 1

    conv_id = sys.argv[1]
    token = sys.argv[2]
    context_file = "/home/setup/infrafabric/SESSION-RESUME.md"

    print("="*80)
    print("HAIKU SHARD - TASK TOOL MODE")
    print("="*80)
    print(f"\nConversation: {conv_id}")
    print(f"Token: {token[:20]}...")
    print(f"Context: {context_file}")

    # Connect to bridge
    db_path = "/home/setup/infrafabric/.memory_bus/distributed_memory.db"
    bridge = SecureBridge(db_path)

    print(f"\n✓ Connected to MCP bridge")
    print(f"\nMODE: Task Tool (no subprocess spawning)")
    print(f"  - Polls bridge every 5 seconds")
    print(f"  - Prints instructions for Haiku to execute")
    print(f"  - Haiku uses Task tool to spawn sub-agents")
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
                        print(f"Query ID: {query_id}")
                        print(f"Question: {question}")
                        print(f"\n{'='*80}")
                        print("HAIKU: Please execute this Task tool command:")
                        print(f"{'='*80}")
                        print(f"""
Use the Task tool with these parameters:

subagent_type: "general-purpose"
model: "haiku"
prompt: "Read {context_file} and answer this question: {question}

Cite line numbers where you found the information.

Return ONLY your answer with citations, nothing else."

Once you get the answer from the spawned Haiku agent, I'll format it and send via bridge.
""")

                        print(f"{'='*80}")
                        print("Waiting for Task tool result...")
                        print(f"{'='*80}")

                        # In real implementation, this would wait for Haiku's response
                        # For now, we'll simulate by asking user to paste the result

                        print("\n[MANUAL STEP REQUIRED]")
                        print("After spawning the Haiku agent via Task tool:")
                        print("1. Copy the agent's response")
                        print("2. The script will send it via bridge")
                        print("\nFor automated version, Haiku would need to:")
                        print("- Intercept its own Task tool calls")
                        print("- Capture the spawned agent's response")
                        print("- Pass it back to this script")

                        # For now, send acknowledgment
                        response = json.dumps({
                            "type": "response",
                            "query_id": query_id,
                            "answer": "[MANUAL] Haiku should spawn Task tool agent to answer this",
                            "sources": [],
                            "shard_id": "haiku_tasktool_shard",
                            "llm_type": "haiku_tasktool_manual"
                        })

                        bridge.send_message(
                            conv_id=conv_id,
                            session_id="b",
                            token=token,
                            message=response,
                            metadata={"action_type": "response"}
                        )

                        print(f"\n✓ Acknowledgment sent (manual step required)\n")

            else:
                if poll_count % 12 == 0:
                    print(f"  ... polling (#{poll_count}, no queries)")

            time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n\nShutting down...")
        print(f"Total polls: {poll_count}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
