#!/usr/bin/env python3
"""
IF.VESICLE Usage Examples

Demonstrates how to use VesiclePayload and VesicleTransport for Redis operations.
"""

from vesicle import VesiclePayload, VesicleTransport, VesiclePool


def example_1_basic_string_storage():
    """Example 1: Basic string storage with schema validation"""
    print("\n" + "="*70)
    print("Example 1: Basic String Storage with Schema Validation")
    print("="*70)

    # Initialize transport
    transport = VesicleTransport(
        redis_host='localhost',
        redis_port=6379,
        default_ttl=3600
    )

    # Create payload
    payload = VesiclePayload(
        source_agent='gemini-librarian',
        content={
            'query': 'find architecture patterns',
            'results_count': 42,
            'confidence': 0.95
        },
        schema_version='1.0',
        ttl_seconds=1800
    )

    print(f"\nPayload ID: {payload.payload_id}")
    print(f"Source Agent: {payload.source_agent}")
    print(f"Content: {payload.content}")
    print(f"TTL: {payload.ttl_seconds} seconds")

    # Send to Redis
    try:
        success = transport.send_to_redis(
            key='query:latest',
            payload=payload,
            operation='set'
        )
        print(f"\n✓ Sent to Redis: {success}")

        # Fetch from Redis
        fetched = transport.fetch_from_redis(
            key='query:latest',
            operation='get'
        )
        print(f"✓ Fetched from Redis")
        print(f"  Source: {fetched.source_agent}")
        print(f"  Content: {fetched.content}")
        print(f"  Timestamp: {fetched.timestamp}")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_2_list_operations():
    """Example 2: Queue-style list operations"""
    print("\n" + "="*70)
    print("Example 2: Queue-Style List Operations")
    print("="*70)

    transport = VesicleTransport()

    # Create multiple payloads
    payloads = [
        VesiclePayload(
            source_agent='haiku-worker-1',
            content={'task_id': 'task-001', 'status': 'completed'},
            ttl_seconds=3600
        ),
        VesiclePayload(
            source_agent='haiku-worker-2',
            content={'task_id': 'task-002', 'status': 'in-progress'},
            ttl_seconds=3600
        ),
        VesiclePayload(
            source_agent='haiku-worker-3',
            content={'task_id': 'task-003', 'status': 'pending'},
            ttl_seconds=3600
        ),
    ]

    print(f"\nQueueing {len(payloads)} payloads...")

    # Push payloads to queue
    for payload in payloads:
        transport.send_to_redis(
            key='task:queue',
            payload=payload,
            operation='rpush'
        )
        print(f"  ✓ Queued task {payload.content['task_id']}")

    # Fetch all from queue
    print("\nFetching from queue...")
    try:
        results = transport.fetch_from_redis(
            key='task:queue',
            operation='lrange'
        )
        print(f"✓ Retrieved {len(results)} items from queue")
        for item in results:
            print(f"  - {item.source_agent}: {item.content}")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_3_hash_storage():
    """Example 3: Hash-based storage (field-value pairs)"""
    print("\n" + "="*70)
    print("Example 3: Hash-Based Storage")
    print("="*70)

    transport = VesicleTransport()

    # Create payloads for different agents
    agent_data = [
        VesiclePayload(
            source_agent='sonnet-coordinator',
            content={'role': 'coordinator', 'status': 'active'},
            ttl_seconds=7200
        ),
        VesiclePayload(
            source_agent='haiku-worker',
            content={'role': 'worker', 'status': 'idle'},
            ttl_seconds=7200
        ),
        VesiclePayload(
            source_agent='gemini-librarian',
            content={'role': 'archive', 'status': 'indexing'},
            ttl_seconds=7200
        ),
    ]

    print("\nStoring agent data as hash...")
    for payload in agent_data:
        transport.send_to_redis(
            key='agents:registry',
            payload=payload,
            operation='hset'
        )
        print(f"  ✓ Stored {payload.source_agent}")

    # Fetch all agents
    print("\nFetching all agents...")
    try:
        agents = transport.fetch_from_redis(
            key='agents:registry',
            operation='hgetall'
        )
        print(f"✓ Retrieved {len(agents)} agents")
        for field, payload in agents.items():
            print(f"  - {payload.source_agent}: {payload.content}")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_4_type_safety():
    """Example 4: Type safety (preventing WRONGTYPE errors)"""
    print("\n" + "="*70)
    print("Example 4: Type Safety (Preventing WRONGTYPE Errors)")
    print("="*70)

    transport = VesicleTransport()

    # Create string payload
    string_payload = VesiclePayload(
        source_agent='test-agent',
        content={'type': 'string_data'},
        ttl_seconds=1800
    )

    print("\nStoring as STRING...")
    transport.send_to_redis(
        key='test:unsafe_key',
        payload=string_payload,
        operation='set'
    )
    print("✓ Stored as STRING")

    # Try to use LIST operation on STRING key
    print("\nAttempting LIST operation on STRING key...")
    list_payload = VesiclePayload(
        source_agent='test-agent',
        content={'type': 'list_data'},
        ttl_seconds=1800
    )

    try:
        transport.send_to_redis(
            key='test:unsafe_key',
            payload=list_payload,
            operation='rpush'  # This should fail
        )
        print("✗ Error: Operation succeeded when it should have failed!")
    except TypeError as e:
        print(f"✓ Type error correctly caught: {e}")

    # Verify key type
    key_type = transport.get_key_type('test:unsafe_key')
    print(f"✓ Key type verified: {key_type.value}")


def example_5_batch_operations():
    """Example 5: Batch operations with VesiclePool"""
    print("\n" + "="*70)
    print("Example 5: Batch Operations with VesiclePool")
    print("="*70)

    transport = VesicleTransport()
    pool = VesiclePool(transport)

    print("\nQueueing payloads in batch...")

    # Queue multiple payloads
    for i in range(5):
        payload = VesiclePayload(
            source_agent=f'worker-{i}',
            content={'result_id': f'result-{i}', 'value': i * 100},
            ttl_seconds=1800
        )
        pool.add_payload(f'results:batch', payload, operation='rpush')

    print(f"✓ Queued {len(pool)} payloads in pool")

    # Flush all at once
    print("\nFlushing batch to Redis...")
    count = pool.flush()
    print(f"✓ Flushed {count} payloads to Redis")

    # Verify
    results = transport.fetch_from_redis(
        key='results:batch',
        operation='lrange'
    )
    print(f"✓ Verified: {len(results)} items in Redis")


def example_6_schema_validation():
    """Example 6: Schema validation (No Schema, No Write)"""
    print("\n" + "="*70)
    print("Example 6: Schema Validation (No Schema, No Write)")
    print("="*70)

    transport = VesicleTransport()

    # Valid payload
    print("\nCreating valid payload...")
    try:
        valid_payload = VesiclePayload(
            source_agent='valid-agent',
            content={'key': 'value'},
            schema_version='1.0',
            ttl_seconds=3600
        )
        print(f"✓ Valid payload created: {valid_payload.payload_id}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Invalid TTL
    print("\nCreating payload with invalid TTL...")
    try:
        invalid_payload = VesiclePayload(
            source_agent='invalid-agent',
            content={'key': 'value'},
            ttl_seconds=999999  # Too large
        )
        print("✗ Error: Invalid payload was accepted!")
    except ValueError as e:
        print(f"✓ Validation error correctly caught: {e}")

    # Invalid schema version
    print("\nCreating payload with invalid schema version...")
    try:
        invalid_payload = VesiclePayload(
            source_agent='invalid-agent',
            content={'key': 'value'},
            schema_version='9.9'
        )
        print("✗ Error: Invalid schema version was accepted!")
    except ValueError as e:
        print(f"✓ Validation error correctly caught: {e}")


def example_7_ttt_headers():
    """Example 7: IF.TTT traceability headers"""
    print("\n" + "="*70)
    print("Example 7: IF.TTT Traceability Headers")
    print("="*70)

    transport = VesicleTransport()

    # Payload with TTT headers (v1.1)
    payload = VesiclePayload(
        source_agent='sonnet-coordinator',
        content={'decision': 'approve', 'reasoning': 'high confidence'},
        schema_version='1.1',
        ttl_seconds=7200,
        ttt_headers={
            'traceable_id': 'trace-0001',
            'transparent_lineage': ['decision-1', 'evaluation-1', 'query-1'],
            'trustworthy_signature': 'sig_0001'
        }
    )

    print(f"\nPayload with TTT Headers:")
    print(f"  Payload ID: {payload.payload_id}")
    print(f"  Traceable ID: {payload.ttt_headers['traceable_id']}")
    print(f"  Lineage: {' → '.join(payload.ttt_headers['transparent_lineage'])}")
    print(f"  Signature: {payload.ttt_headers['trustworthy_signature']}")

    # Send to Redis
    transport.send_to_redis(
        key='decisions:traced',
        payload=payload,
        operation='set'
    )
    print("\n✓ Sent to Redis with full traceability")

    # Fetch and verify
    fetched = transport.fetch_from_redis(
        key='decisions:traced',
        operation='get'
    )
    print("\n✓ Fetched and verified:")
    print(f"  TTT Headers: {fetched.ttt_headers}")


def example_8_msgpack_serialization():
    """Example 8: msgpack serialization for complex objects"""
    print("\n" + "="*70)
    print("Example 8: msgpack Serialization for Complex Objects")
    print("="*70)

    transport = VesicleTransport()

    # Complex nested payload
    payload = VesiclePayload(
        source_agent='data-processor',
        content={
            'results': [
                {'id': 1, 'score': 0.95, 'tags': ['important', 'urgent']},
                {'id': 2, 'score': 0.87, 'tags': ['review']},
                {'id': 3, 'score': 0.76, 'tags': []},
            ],
            'metadata': {
                'total': 3,
                'processed_at': '2025-11-26T10:30:00',
                'version': '1.0'
            }
        },
        schema_version='1.0',
        ttl_seconds=3600
    )

    print("\nStoring complex payload with msgpack...")
    transport.send_to_redis(
        key='analysis:results',
        payload=payload,
        operation='set',
        use_msgpack=True
    )
    print("✓ Stored with msgpack compression")

    # Fetch using msgpack
    fetched = transport.fetch_from_redis(
        key='analysis:results',
        operation='get',
        use_msgpack=True
    )
    print("\n✓ Fetched with msgpack decompression")
    print(f"  Results count: {len(fetched.content['results'])}")
    print(f"  Metadata: {fetched.content['metadata']}")


if __name__ == '__main__':
    print("\nIF.VESICLE v1.0 - Usage Examples")
    print("=" * 70)

    try:
        # Run examples
        example_1_basic_string_storage()
        example_2_list_operations()
        example_3_hash_storage()
        example_4_type_safety()
        example_5_batch_operations()
        example_6_schema_validation()
        example_7_ttt_headers()
        example_8_msgpack_serialization()

        print("\n" + "="*70)
        print("All examples completed successfully!")
        print("="*70 + "\n")

    except ConnectionError as e:
        print(f"\n✗ Connection error: {e}")
        print("  Make sure Redis is running on localhost:6379")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
