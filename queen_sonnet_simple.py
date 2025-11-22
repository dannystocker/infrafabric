#!/usr/bin/env python3
"""
Queen Sonnet - Simple Coordinator
Sends queries via MCP bridge, receives responses
User manually spawns Haiku via Task tool
"""

import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')

from agent_bridge_secure import SecureBridge
import json
import uuid
import time

def main():
    print("="*80)
    print("QUEEN SONNET - Simple Coordinator")
    print("="*80)

    # Connect to MCP bridge
    db_path = "/home/setup/infrafabric/.memory_bus/distributed_memory.db"
    bridge = SecureBridge(db_path)

    # Create new conversation
    conv_id = f"conv_{uuid.uuid4().hex[:16]}"
    coordinator_token = uuid.uuid4().hex
    haiku_token = uuid.uuid4().hex

    print(f"\nConversation ID: {conv_id}")
    print(f"Coordinator token: {coordinator_token}")
    print(f"Haiku token: {haiku_token}")

    # Send query
    query_id = f"query_{uuid.uuid4().hex[:8]}"
    query = {
        "type": "query",
        "query_id": query_id,
        "question": "What was the Queen Sonnet + Haiku Master architecture that emerged from Instance #6's debugging? Explain briefly with sources.",
        "context_file": "/home/setup/infrafabric/SESSION-RESUME.md"
    }

    print(f"\n[1] Sending query to MCP bridge...")
    print(f"    Query ID: {query_id}")
    print(f"    Question: {query['question'][:80]}...")

    bridge.send_message(
        conv_id=conv_id,
        session_id="coordinator",
        token=coordinator_token,
        message=json.dumps(query),
        metadata={"action_type": "query"}
    )

    print(f"    ✓ Query sent")

    # Instructions for user
    print(f"\n[2] NOW: Spawn Haiku agent via Task tool")
    print(f"="*80)
    print(f"""
Use the Task tool with these parameters:

subagent_type: "general-purpose"
model: "haiku"
prompt: '''Please run this Python script to check for queries and respond:

```python
import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')
from agent_bridge_secure import SecureBridge
import json

db_path = "/home/setup/infrafabric/.memory_bus/distributed_memory.db"
bridge = SecureBridge(db_path)

# Read SESSION-RESUME.md
with open('/home/setup/infrafabric/SESSION-RESUME.md') as f:
    context = f.read()

# Check for messages
messages = bridge.get_unread_messages('{conv_id}', 'haiku', '{haiku_token}')

for msg in messages:
    content = json.loads(msg['message'])
    if content.get('type') == 'query':
        query_id = content['query_id']
        question = content['question']

        print(f"Query: {{question}}")

        # Answer based on loaded context
        # Search for Queen Sonnet + Haiku Master in context
        answer = "Found in context: " + [line for line in context.split('\\n') if 'Queen Sonnet' in line or 'Haiku Master' in line][:5].__str__()

        # Send response
        response = json.dumps({{
            "type": "response",
            "query_id": query_id,
            "answer": answer,
            "sources": ["SESSION-RESUME.md"],
            "shard_id": "haiku_manual"
        }})

        bridge.send_message(
            conv_id='{conv_id}',
            session_id='haiku',
            token='{haiku_token}',
            message=response,
            metadata={{"action_type": "response"}}
        )

        print(f"✓ Response sent")
```
'''
""")

    print(f"="*80)
    print(f"\n[3] Waiting for Haiku response (max 60 seconds)...")

    # Poll for response
    start_time = time.time()
    timeout = 60

    while time.time() - start_time < timeout:
        messages = bridge.get_unread_messages(conv_id, "coordinator", coordinator_token)

        for msg in messages:
            content = json.loads(msg['message'])
            if content.get('type') == 'response' and content.get('query_id') == query_id:
                elapsed = time.time() - start_time

                print(f"    ✓ Response received after {elapsed:.1f} seconds!")
                print(f"\n{'='*80}")
                print(f"HAIKU RESPONSE:")
                print(f"{'='*80}")
                print(f"\nAnswer: {content.get('answer')}")
                print(f"Sources: {content.get('sources')}")
                print(f"Shard: {content.get('shard_id')}")
                print(f"\n{'='*80}")
                print(f"✅ OPERATIONAL TEST PASSED!")
                print(f"{'='*80}")
                return 0

        time.sleep(2)

    print(f"\n⏱️  Timeout after {timeout} seconds")
    print(f"Haiku may still be processing - check manually")
    return 1

if __name__ == "__main__":
    sys.exit(main())
