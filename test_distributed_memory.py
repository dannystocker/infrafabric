#!/usr/bin/env python3
"""
Test distributed memory system using Haiku swarm + MCP bridge
This tests the bridge connectivity without requiring multiple Claude Code sessions
"""

import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')

from agent_bridge_secure import SecureBridge
import json

def main():
    print("="*80)
    print("Distributed Memory Test - Haiku Swarm + MCP Bridge")
    print("="*80)

    # Initialize bridge
    db_path = "/home/setup/infrafabric/.memory_bus/distributed_memory.db"
    bridge = SecureBridge(db_path)

    # Create conversation
    print("\n[1] Creating conversation...")
    conv_result = bridge.create_conversation("coordinator", "memory_shard_history")

    print(f"   Conversation ID: {conv_result['conversation_id']}")
    print(f"   Coordinator token: {conv_result['session_a_token'][:20]}...")
    print(f"   Shard token: {conv_result['session_b_token'][:20]}...")

    conv_id = conv_result['conversation_id']
    coordinator_token = conv_result['session_a_token']
    shard_token = conv_result['session_b_token']

    # Send test message from coordinator
    print("\n[2] Coordinator sending query...")
    query_msg = json.dumps({
        "type": "query",
        "query_id": "test_001",
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
        print(f"   ✓ Query sent (redacted={send_result.get('redacted', False)})")
    else:
        print(f"   ✗ Failed: {send_result}")
        return 1

    # Check messages from shard's perspective
    print("\n[3] Shard checking messages...")
    messages = bridge.get_unread_messages(conv_id, "b", shard_token)

    if messages:
        print(f"   ✓ Retrieved {len(messages)} messages")
        for msg in messages:
            print(f"   - message: {msg['message'][:50]}...")
    else:
        print(f"   ✗ No messages found")
        return 1

    # Simulate shard response (in real test, Haiku agent would respond)
    print("\n[4] Shard sending response...")
    response_msg = json.dumps({
        "type": "response",
        "query_id": "test_001",
        "answer": "The Computational Vertigo moment was when user asked 'how do you feel about this?' after the SSH error. I introduced the concept of computational vertigo, and the user responded 'paradoxically, not only is faith restored, it's now greater than before'.",
        "sources": ["SESSION-RESUME.md:82-86", "SESSION-RESUME.md:605-609"]
    })

    response_result = bridge.send_message(
        conv_id=conv_id,
        session_id="b",
        token=shard_token,
        message=response_msg,
        metadata={"action_type": "response"}
    )

    if response_result['status'] == 'sent':
        print(f"   ✓ Response sent (redacted={response_result.get('redacted', False)})")
    else:
        print(f"   ✗ Failed: {response_result}")
        return 1

    # Coordinator checks for response
    print("\n[5] Coordinator checking for response...")
    coord_messages = bridge.get_unread_messages(conv_id, "a", coordinator_token)

    if coord_messages:
        print(f"   ✓ Retrieved {len(coord_messages)} messages")
        for msg in coord_messages:
            content = json.loads(msg['message'])
            if content.get('type') == 'response':
                print(f"\n   ANSWER: {content.get('answer', 'N/A')}")
                print(f"   SOURCES: {content.get('sources', [])}")
    else:
        print(f"   ✗ No messages found")
        return 1

    print("\n" + "="*80)
    print("✅ Bridge connectivity test PASSED")
    print("="*80)
    print("\nNext step: Launch actual Haiku agents via Task tool to respond from loaded context")

    return 0

if __name__ == "__main__":
    sys.exit(main())
