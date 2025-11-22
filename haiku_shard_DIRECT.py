#!/usr/bin/env python3
"""
DIRECT HAIKU SHARD - Uses Haiku's own context (no subprocess spawning)

This script is meant to run INSIDE a Haiku session.
Haiku loads context once, then answers queries directly using its own LLM capabilities.
"""

import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')

from agent_bridge_secure import SecureBridge
import json
import time

def main():
    if len(sys.argv) < 3:
        print("Usage: python haiku_shard_DIRECT.py <conv_id> <token>")
        print("\nNote: This script should be run FROM a Haiku Claude Code session.")
        print("The Haiku session will read context files and answer queries directly.")
        return 1

    conv_id = sys.argv[1]
    token = sys.argv[2]

    print("="*80)
    print("HAIKU DIRECT SHARD - No Subprocess Spawning")
    print("="*80)
    print(f"\nConversation ID: {conv_id}")
    print(f"Token: {token[:20]}...")

    print("\n" + "="*80)
    print("INSTRUCTIONS FOR HAIKU:")
    print("="*80)
    print("""
This script will poll for queries every 5 seconds.

When a query arrives, YOU (Haiku) will:
1. See the question printed below
2. Be asked to answer it using context you've already loaded
3. Provide your answer when prompted

The script will then send your answer back via MCP bridge.

NO subprocess spawning - you answer directly!
""")

    # Connect to bridge
    db_path = "/home/setup/infrafabric/.memory_bus/distributed_memory.db"
    bridge = SecureBridge(db_path)

    print(f"✓ Connected to MCP bridge")
    print(f"\nPolling for queries (Ctrl+C to stop)...\n")

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

                        print("\n" + "="*80)
                        print(f"QUERY RECEIVED: {query_id}")
                        print("="*80)
                        print(f"\nQuestion: {question}")
                        print("\n" + "="*80)
                        print("HAIKU: Please answer this question using the context")
                        print("you loaded from /home/setup/infrafabric/SESSION-RESUME.md")
                        print("="*80)

                        # MANUAL INPUT - Haiku session provides answer
                        print("\nWaiting for Haiku to provide answer...")
                        print("(In a real implementation, this would be automated)")
                        print("\nFor now, returning a placeholder...")

                        # Placeholder - in real use, Haiku would provide answer
                        answer = "PLACEHOLDER: Haiku would answer here based on loaded context"
                        sources = []

                        # Send response
                        response = json.dumps({
                            "type": "response",
                            "query_id": query_id,
                            "answer": answer,
                            "sources": sources,
                            "shard_id": "haiku_direct_shard",
                            "llm_type": "haiku_direct_context"
                        })

                        bridge.send_message(
                            conv_id=conv_id,
                            session_id="b",
                            token=token,
                            message=response,
                            metadata={"action_type": "response"}
                        )

                        print(f"\n✓ Response sent via bridge\n")

            # Poll every 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n\nShutting down gracefully...")
        return 0

if __name__ == "__main__":
    sys.exit(main())
