#!/usr/bin/env python3
"""
Sonnet Debug Bus Loop - Monitor and respond to queries for 3 minutes

This script:
1. Monitors /tmp/claude_debug_bus.jsonl for responses
2. Periodically sends test queries
3. Displays Q&A as they happen
4. Runs for 3 minutes then stops
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta

BUS_FILE = '/tmp/claude_debug_bus.jsonl'
SONNET_ID = 'sonnet_412174'

# Test queries to send
TEST_QUERIES = [
    "What is the Computational Vertigo moment? Cite line numbers.",
    "What were the key achievements of Instance #6? Cite line numbers.",
    "What is IF.TTT and why is it mandatory? Cite your sources.",
    "Describe the Haiku autopoll architecture in 2 sentences.",
    "What does the MCP bridge do?"
]

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

    return message

def read_responses(since_timestamp=None):
    """Read all responses from the bus"""
    responses = []

    if not os.path.exists(BUS_FILE):
        return responses

    try:
        with open(BUS_FILE, 'r') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())

                    # Look for responses to us
                    if (msg.get('type') == 'response' and
                        msg.get('to') == SONNET_ID):

                        # Filter by timestamp if specified
                        if since_timestamp is None or msg.get('timestamp', 0) > since_timestamp:
                            responses.append(msg)
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        pass

    return responses

def main():
    """Main 3-minute loop"""

    print(f"\n{'='*80}")
    print(f"SONNET DEBUG BUS LOOP - 3 Minute Monitor")
    print(f"{'='*80}")
    print(f"Bus file: {BUS_FILE}")
    print(f"Duration: 3 minutes")
    print(f"Sonnet ID: {SONNET_ID}")
    print(f"{'='*80}\n")

    # Initialize bus file
    if not os.path.exists(BUS_FILE):
        open(BUS_FILE, 'w').close()
        print(f"✓ Created bus file: {BUS_FILE}\n")
    else:
        print(f"✓ Bus file exists: {BUS_FILE}\n")

    # Start time
    start_time = time.time()
    end_time = start_time + 180  # 3 minutes
    query_interval = 30  # Send query every 30 seconds
    last_query_time = start_time
    query_index = 0
    last_response_count = 0
    displayed_responses = set()

    print(f"Starting monitoring loop...")
    print(f"Will send queries every {query_interval} seconds")
    print(f"Loop runs until: {datetime.fromtimestamp(end_time).strftime('%H:%M:%S')}\n")

    try:
        while time.time() < end_time:
            current_time = time.time()
            remaining = end_time - current_time

            # Send query if interval has passed
            if current_time - last_query_time >= query_interval and query_index < len(TEST_QUERIES):
                question = TEST_QUERIES[query_index]
                print(f"[{datetime.fromtimestamp(current_time).strftime('%H:%M:%S')}] SENDING QUERY #{query_index + 1}")
                print(f"  Question: {question[:60]}...")

                sent_msg = send_query(question)
                query_index += 1
                last_query_time = current_time
                print()

            # Check for responses
            responses = read_responses()

            # Display new responses
            for response in responses:
                response_id = (response.get('from'), response.get('timestamp'))

                # Only display each response once
                if response_id not in displayed_responses:
                    displayed_responses.add(response_id)

                    print(f"[{datetime.fromtimestamp(response.get('timestamp', 0)).strftime('%H:%M:%S')}] RESPONSE RECEIVED")
                    print(f"  From: {response.get('from')}")
                    print(f"  Answer: {response.get('answer', 'N/A')[:100]}...")
                    print(f"  Sources: {response.get('sources', [])}")
                    print()

            # Show status every 10 seconds
            if int(current_time) % 10 == 0 and current_time != last_query_time:
                status = f"[{datetime.fromtimestamp(current_time).strftime('%H:%M:%S')}] Monitoring... "
                status += f"({int(remaining)}s remaining) "
                status += f"Queries sent: {query_index}/{len(TEST_QUERIES)}, "
                status += f"Responses: {len(displayed_responses)}"
                print(status)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED BY USER]")

    # Final statistics
    end_time_actual = time.time()
    duration = end_time_actual - start_time

    print(f"\n{'='*80}")
    print(f"LOOP COMPLETED")
    print(f"{'='*80}")
    print(f"Duration: {int(duration)} seconds")
    print(f"Queries sent: {query_index}/{len(TEST_QUERIES)}")
    print(f"Responses received: {len(displayed_responses)}")
    print(f"Success rate: {len(displayed_responses)}/{query_index} = {100*len(displayed_responses)/max(query_index,1):.1f}%")
    print(f"{'='*80}\n")

    # Show full conversation
    print(f"Full conversation from bus:\n")
    if os.path.exists(BUS_FILE):
        with open(BUS_FILE, 'r') as f:
            line_num = 1
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    msg_type = msg.get('type', 'unknown')
                    msg_from = msg.get('from', '?')
                    msg_to = msg.get('to', '?')

                    if msg_type == 'query':
                        question = msg.get('question', '?')[:50]
                        print(f"{line_num:2d}. QUERY: {msg_from} → {msg_to}")
                        print(f"    {question}...")
                    elif msg_type == 'response':
                        answer = msg.get('answer', '?')[:50]
                        print(f"{line_num:2d}. RESPONSE: {msg_from} → {msg_to}")
                        print(f"    {answer}...")

                    line_num += 1
                except:
                    pass

        print(f"\n{'='*80}\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
