#!/usr/bin/env python3
"""
Sonnet Query Sender - Send queries to Haiku via JSONL debug bus

This script:
1. Appends queries to /tmp/claude_debug_bus.jsonl
2. Monitors the file for responses
3. Displays Q&A in real-time
"""

import json
import time
import os
import subprocess
import sys

BUS_FILE = '/tmp/claude_debug_bus.jsonl'
SONNET_ID = 'sonnet_412174'

def send_query(question, context_file='/home/setup/infrafabric/SESSION-RESUME.md'):
    """Send a query to Haiku via the debug bus"""

    message = {
        'type': 'query',
        'from': SONNET_ID,
        'to': 'haiku',
        'question': question,
        'context_file': context_file,
        'timestamp': time.time()
    }

    # Append to bus file
    with open(BUS_FILE, 'a') as f:
        f.write(json.dumps(message) + '\n')

    print(f"\n{'='*80}")
    print(f"QUERY SENT")
    print(f"{'='*80}")
    print(f"Question: {question}")
    print(f"Context: {context_file}")
    print(f"Timestamp: {time.strftime('%H:%M:%S', time.localtime(message['timestamp']))}")
    print(f"{'='*80}\n")

    return message

def wait_for_response(query_timestamp, timeout=60):
    """Wait for Haiku to respond to the query"""

    print(f"Waiting for Haiku response (timeout: {timeout}s)...\n")
    start_time = time.time()
    last_line_count = 0

    try:
        while time.time() - start_time < timeout:
            if os.path.exists(BUS_FILE):
                with open(BUS_FILE, 'r') as f:
                    lines = f.readlines()

                # Check new lines for responses
                for line in lines[last_line_count:]:
                    try:
                        msg = json.loads(line.strip())

                        # Look for responses to us after our query
                        if (msg.get('type') == 'response' and
                            msg.get('to') == SONNET_ID and
                            msg.get('timestamp', 0) > query_timestamp):

                            print(f"\n{'='*80}")
                            print(f"RESPONSE RECEIVED")
                            print(f"{'='*80}")
                            print(f"From: {msg.get('from')}")
                            print(f"Answer: {msg.get('answer', 'N/A')[:200]}...")
                            print(f"Sources: {msg.get('sources', [])}")
                            print(f"Timestamp: {time.strftime('%H:%M:%S', time.localtime(msg.get('timestamp', 0)))}")
                            print(f"{'='*80}\n")

                            return msg
                    except json.JSONDecodeError:
                        pass

                last_line_count = len(lines)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return None

    print(f"\nTimeout waiting for response (>{timeout}s)")
    return None

def main():
    """Main interaction loop"""

    print(f"\n{'='*80}")
    print(f"SONNET QUERY SENDER - Debug Bus Test")
    print(f"{'='*80}")
    print(f"Bus file: {BUS_FILE}")
    print(f"Sonnet ID: {SONNET_ID}")
    print(f"{'='*80}\n")

    # Initialize bus file
    if not os.path.exists(BUS_FILE):
        open(BUS_FILE, 'w').close()
        print(f"✓ Created bus file: {BUS_FILE}")
    else:
        print(f"✓ Bus file exists: {BUS_FILE}")

    # Test queries
    test_queries = [
        "What is the Computational Vertigo moment? Cite line numbers.",
        "What were the key achievements of Instance #6? Cite line numbers.",
        "What is IF.TTT and why is it mandatory? Cite your sources."
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n[TEST {i}/{len(test_queries)}]")

        # Send query
        sent_msg = send_query(query)

        # Wait for response
        response = wait_for_response(sent_msg['timestamp'], timeout=30)

        if response:
            print(f"✓ Round-trip successful ({i}/{len(test_queries)})")
        else:
            print(f"✗ No response received ({i}/{len(test_queries)})")

        if i < len(test_queries):
            print(f"\nWaiting 5 seconds before next query...")
            time.sleep(5)

    # Final summary
    print(f"\n{'='*80}")
    print(f"TEST COMPLETE")
    print(f"{'='*80}")
    print(f"All messages in bus:")
    print(f"{'='*80}\n")

    if os.path.exists(BUS_FILE):
        with open(BUS_FILE, 'r') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    print(f"{msg.get('type'):8} | {msg.get('from'):20} → {msg.get('to'):15} | {msg.get('question', msg.get('answer', ''))[:50]}...")
                except:
                    pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        sys.exit(0)
