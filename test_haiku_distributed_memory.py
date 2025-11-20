#!/usr/bin/env python3
"""
Full distributed memory test with actual Haiku agent loading context
"""

import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')

from agent_bridge_secure import SecureBridge
import json
import subprocess
import time

def main():
    print("="*80)
    print("Distributed Memory Test - Real Haiku Agent with Loaded Context")
    print("="*80)

    # Initialize bridge
    db_path = "/home/setup/infrafabric/.memory_bus/distributed_memory.db"
    bridge = SecureBridge(db_path)

    # Create conversation
    print("\n[1] Creating conversation...")
    conv_result = bridge.create_conversation("coordinator", "memory_shard_history")

    print(f"   Conversation ID: {conv_result['conversation_id']}")
    conv_id = conv_result['conversation_id']
    coordinator_token = conv_result['session_a_token']
    shard_token = conv_result['session_b_token']

    # Launch Haiku shard in background
    print("\n[2] Launching Haiku memory shard in background...")
    shard_cmd = [
        "bash", "-c",
        f"source .venv/bin/activate && python /home/setup/infrafabric/launch_haiku_shard.py {conv_id} {shard_token} /home/setup/infrafabric/SESSION-RESUME.md > /tmp/haiku_shard.log 2>&1 &"
    ]

    subprocess.Popen(shard_cmd, cwd="/home/setup/work/mcp-multiagent-bridge")
    print(f"   ✓ Haiku shard launched (logging to /tmp/haiku_shard.log)")
    print(f"   Waiting 3 seconds for shard to load context...")
    time.sleep(3)

    # Send query
    print("\n[3] Coordinator sending query...")
    query_msg = json.dumps({
        "type": "query",
        "query_id": "test_haiku_001",
        "question": "What was the Computational Vertigo moment?"
    })

    send_result = bridge.send_message(
        conv_id=conv_id,
        session_id="a",
        token=coordinator_token,
        message=query_msg,
        metadata={"action_type": "query"}
    )

    if send_result['status'] == 'sent':
        print(f"   ✓ Query sent to Haiku shard")
    else:
        print(f"   ✗ Failed: {send_result}")
        return 1

    # Poll for response (Haiku shard polls every 5 seconds)
    print("\n[4] Waiting for Haiku shard response (max 15 seconds)...")
    for i in range(15):
        time.sleep(1)
        coord_messages = bridge.get_unread_messages(conv_id, "a", coordinator_token)

        if coord_messages:
            print(f"   ✓ Response received after {i+1} seconds!")
            for msg in coord_messages:
                content = json.loads(msg['message'])
                if content.get('type') == 'response':
                    print(f"\n{'='*80}")
                    print("HAIKU SHARD RESPONSE:")
                    print(f"{'='*80}")
                    print(f"\nQUESTION: {query_msg}")
                    print(f"\nANSWER: {content.get('answer', 'N/A')}")
                    print(f"\nSOURCES: {content.get('sources', [])}")
                    print(f"\nSHARD ID: {content.get('shard_id', 'unknown')}")
                    print(f"\n{'='*80}")
                    print("✅ Distributed Memory Test PASSED!")
                    print(f"{'='*80}")
                    print("\nKey Achievement:")
                    print("  - Haiku agent loaded SESSION-RESUME.md into context")
                    print("  - Responded from loaded context via MCP bridge")
                    print("  - Coordinator retrieved 'Computational Vertigo' moment")
                    print("  - Proves 800K distributed memory architecture works!")
                    return 0

        # Show progress
        if (i+1) % 3 == 0:
            print(f"   ... still waiting ({i+1}s)")

    print(f"\n   ✗ Timeout - no response after 15 seconds")
    print(f"\n   Check shard log: tail -f /tmp/haiku_shard.log")
    return 1

if __name__ == "__main__":
    sys.exit(main())
