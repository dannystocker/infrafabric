#!/usr/bin/env python3
"""
Sonnet 5-Minute Polling Loop - Monitor debug bus continuously

This script:
1. Continuously polls /tmp/claude_debug_bus.jsonl
2. Displays new responses as they arrive
3. Shows activity status every 5 seconds
4. Runs for 5 minutes (300 seconds)
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta

BUS_FILE = '/tmp/claude_debug_bus.jsonl'
SONNET_ID = 'sonnet_412174'

def read_all_messages():
    """Read all messages from the bus"""
    messages = []

    if not os.path.exists(BUS_FILE):
        return messages

    try:
        with open(BUS_FILE, 'r') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    messages.append(msg)
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        pass

    return messages

def main():
    """Main 5-minute polling loop"""

    print(f"\n{'='*80}")
    print(f"SONNET 5-MINUTE POLLING LOOP")
    print(f"{'='*80}")
    print(f"Bus file: {BUS_FILE}")
    print(f"Duration: 5 minutes (300 seconds)")
    print(f"Poll interval: Every 2 seconds")
    print(f"Sonnet ID: {SONNET_ID}")
    print(f"{'='*80}\n")

    # Start time
    start_time = time.time()
    end_time = start_time + 300  # 5 minutes
    last_status_time = start_time
    last_response_count = 0
    displayed_responses = set()
    queries_seen = 0
    responses_seen = 0

    print(f"Starting 5-minute polling loop...")
    print(f"Will poll every 2 seconds")
    print(f"Loop ends at: {datetime.fromtimestamp(end_time).strftime('%H:%M:%S')}\n")

    try:
        while time.time() < end_time:
            current_time = time.time()
            remaining = int(end_time - current_time)

            # Read all messages
            messages = read_all_messages()

            # Count messages by type
            current_queries = sum(1 for m in messages if m.get('type') == 'query')
            current_responses = sum(1 for m in messages if m.get('type') == 'response' and m.get('to') == SONNET_ID)

            # Display new responses
            for msg in messages:
                if msg.get('type') == 'response' and msg.get('to') == SONNET_ID:
                    response_id = (msg.get('from'), msg.get('timestamp'))

                    if response_id not in displayed_responses:
                        displayed_responses.add(response_id)
                        responses_seen += 1

                        timestamp_str = datetime.fromtimestamp(msg.get('timestamp', 0)).strftime('%H:%M:%S')
                        print(f"\n{'='*80}")
                        print(f"[{timestamp_str}] ✓ RESPONSE #{responses_seen} RECEIVED")
                        print(f"{'='*80}")
                        print(f"From: {msg.get('from')}")
                        print(f"Answer: {msg.get('answer', 'N/A')}")
                        print(f"Sources: {msg.get('sources', [])}")
                        print(f"{'='*80}\n")

            # Show status every 5 seconds
            if int(current_time) - int(last_status_time) >= 5:
                status_line = f"[{datetime.fromtimestamp(current_time).strftime('%H:%M:%S')}] "
                status_line += f"POLLING... ({remaining:3d}s remaining) | "
                status_line += f"Queries in bus: {current_queries} | "
                status_line += f"Responses: {len(displayed_responses)} "

                # Show progress bar
                progress = (current_time - start_time) / 300
                bar_length = 20
                filled = int(bar_length * progress)
                bar = '█' * filled + '░' * (bar_length - filled)
                status_line += f"| [{bar}]"

                print(status_line)
                last_status_time = current_time

            # Poll every 2 seconds
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED BY USER]")

    # Final summary
    end_time_actual = time.time()
    duration = end_time_actual - start_time

    print(f"\n{'='*80}")
    print(f"5-MINUTE LOOP COMPLETED")
    print(f"{'='*80}")
    print(f"Duration: {int(duration)} seconds")
    print(f"Queries in bus: {current_queries}")
    print(f"Responses received: {len(displayed_responses)}")
    print(f"Response rate: {len(displayed_responses)}/{current_queries} = {100*len(displayed_responses)/max(current_queries,1):.1f}%")
    print(f"{'='*80}\n")

    # Show all messages summary
    print(f"Summary of all messages:\n")
    print(f"{'Type':<10} | {'From':<20} | {'To':<15} | {'Content':<40}")
    print(f"{'-'*100}")

    messages = read_all_messages()
    for i, msg in enumerate(messages, 1):
        msg_type = msg.get('type', 'unknown')
        msg_from = msg.get('from', '?')
        msg_to = msg.get('to', '?')

        if msg_type == 'query':
            content = msg.get('question', '?')[:38]
        elif msg_type == 'response':
            content = msg.get('answer', '?')[:38]
        else:
            content = '?'

        print(f"{msg_type:<10} | {msg_from:<20} | {msg_to:<15} | {content:<40}")

    print(f"\n{'='*80}\n")

    # Check for Haiku responses
    haiku_responses = [m for m in messages if m.get('type') == 'response' and 'haiku' in m.get('from', '').lower()]

    if haiku_responses:
        print(f"✓ Haiku responded {len(haiku_responses)} time(s)!")
        print(f"✓ Distributed memory communication WORKS!\n")
    else:
        print(f"✗ No Haiku responses yet. Still waiting for Haiku to process queries.\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
