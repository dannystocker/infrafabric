#!/usr/bin/env python3
"""
Sonnet Comms Agent - Send query to existing Haiku session
"""

import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')

from agent_bridge_secure import SecureBridge
import json
import time
import uuid

def main():
    # Use the EXISTING conversation from handoff
    conv_id = "conv_f621d999f19a3a7f"
    # I'm session 'a' (coordinator/sonnet)
    my_token = "c6a0b3187d5efa97b1e21e68cb65828d775c27f531973427efe09c4a12e8b6fa"

    print("="*80)
    print("SONNET COMMS - Sending Query to Haiku")
    print("="*80)
    print(f"\nConversation: {conv_id}")
    print(f"My role: Session A (Coordinator)")

    # Connect to bridge
    db_path = "/home/setup/infrafabric/.memory_bus/distributed_memory.db"
    bridge = SecureBridge(db_path)

    # Create query
    query_id = f"query_{uuid.uuid4().hex[:8]}"
    query = {
        "type": "query",
        "query_id": query_id,
        "question": "What was Instance #6's main achievement? Brief answer with citations."
    }

    print(f"\n[1] Sending query...")
    print(f"    Query ID: {query_id}")
    print(f"    Question: {query['question']}")

    try:
        bridge.send_message(
            conv_id=conv_id,
            session_id="a",
            token=my_token,
            message=json.dumps(query),
            metadata={"action_type": "query"}
        )
        print(f"    ✓ Query sent to MCP bridge")
    except Exception as e:
        print(f"    ✗ Send failed: {e}")
        return 1

    # Wait for response
    print(f"\n[2] Waiting for Haiku response (max 60s)...")

    start_time = time.time()
    timeout = 60

    while time.time() - start_time < timeout:
        try:
            messages = bridge.get_unread_messages(conv_id, "a", my_token)

            for msg in messages:
                content = json.loads(msg['message'])

                if content.get('type') == 'response' and content.get('query_id') == query_id:
                    elapsed = time.time() - start_time

                    print(f"    ✓ Response received in {elapsed:.1f}s!")
                    print(f"\n{'='*80}")
                    print(f"HAIKU RESPONSE:")
                    print(f"{'='*80}")
                    print(f"\nAnswer: {content.get('answer', 'N/A')}")
                    print(f"Sources: {content.get('sources', [])}")
                    print(f"Shard: {content.get('shard_id', 'N/A')}")
                    print(f"\n{'='*80}")
                    print(f"✅ DISTRIBUTED MEMORY OPERATIONAL!")
                    print(f"{'='*80}")
                    return 0

        except Exception as e:
            print(f"    Error checking messages: {e}")

        time.sleep(2)

    print(f"\n⏱️  Timeout after {timeout}s - Haiku may still be processing")
    return 1

if __name__ == "__main__":
    sys.exit(main())
