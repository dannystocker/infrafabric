#!/usr/bin/env python3
"""
Simple MCP Bridge Test - Register conversation and send message
"""

import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')

from agent_bridge_secure import SecureBridge
import json
import uuid

def main():
    print("="*80)
    print("SIMPLE MCP BRIDGE TEST")
    print("="*80)

    # Connect to bridge
    db_path = "/home/setup/infrafabric/.memory_bus/distributed_memory.db"
    bridge = SecureBridge(db_path)

    # Create the conversation (it generates tokens for us)
    print(f"\n[1] Creating conversation...")
    try:
        result = bridge.create_conversation("sonnet_comms", "haiku_memory")
        conv_id = result['conversation_id']
        token_a = result['session_a_token']
        token_b = result['session_b_token']
        print(f"    ✓ Conversation created")
        print(f"\nConversation ID: {conv_id}")
        print(f"Session A (sonnet) token: {token_a}")
        print(f"Session B (haiku) token: {token_b}")
    except Exception as e:
        print(f"    ✗ Registration failed: {e}")
        return 1

    # Send message from session A to session B
    print(f"\n[2] Sending message from A to B...")
    message = json.dumps({
        "type": "test",
        "content": "Hello from Session A"
    })

    try:
        bridge.send_message(
            conv_id=conv_id,
            session_id="a",
            token=token_a,
            message=message,
            metadata={"test": "simple"}
        )
        print(f"    ✓ Message sent")
    except Exception as e:
        print(f"    ✗ Send failed: {e}")
        return 1

    # Read message as session B
    print(f"\n[3] Reading message as session B...")
    try:
        messages = bridge.get_unread_messages(conv_id, "b", token_b)
        if messages:
            print(f"    ✓ Received {len(messages)} message(s)")
            for msg in messages:
                content = json.loads(msg['message'])
                print(f"\n    Message: {content}")
                print(f"    From: {msg['from']}")
                print(f"    Timestamp: {msg['timestamp']}")
        else:
            print(f"    ✗ No messages received")
            return 1
    except Exception as e:
        print(f"    ✗ Read failed: {e}")
        return 1

    print(f"\n{'='*80}")
    print(f"✅ MCP BRIDGE TEST PASSED")
    print(f"{'='*80}")
    print(f"\nConversation details for persistent Haiku session:")
    print(f"  conv_id: {conv_id}")
    print(f"  token_b: {token_b}")
    print(f"\nYou can now launch a persistent Haiku session with these credentials")

    return 0

if __name__ == "__main__":
    sys.exit(main())
