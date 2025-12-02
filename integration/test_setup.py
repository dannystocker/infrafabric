#!/usr/bin/env python3
"""
Memory Layer Integration Tests - Setup Script

This script prepares the test environment:
1. Verifies Redis and ChromaDB connectivity
2. Creates required collections
3. Initializes test data
4. Reports system status

Usage:
    python test_setup.py
    python test_setup.py --verbose
    python test_setup.py --cleanup
"""

import sys
import time
import json
import argparse
import redis
import requests

try:
    import chromadb
except ImportError:
    chromadb = None


def check_redis(host='localhost', port=6379, verbose=False):
    """Check Redis connectivity"""
    print("Checking Redis...", end=" ")

    try:
        r = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
            socket_connect_timeout=5
        )
        r.ping()
        info = r.info()

        print("OK")

        if verbose:
            print(f"  Version: {info.get('redis_version')}")
            print(f"  Memory: {info.get('used_memory_human')}")
            print(f"  Connected clients: {info.get('connected_clients')}")

        return r

    except redis.ConnectionError as e:
        print(f"FAILED - {e}")
        return None


def check_chromadb(host='localhost', port=8000, verbose=False):
    """Check ChromaDB connectivity"""
    print("Checking ChromaDB...", end=" ")

    try:
        response = requests.get(
            f'http://{host}:{port}/api/v1/heartbeat',
            timeout=5
        )

        if response.status_code == 200:
            print("OK")

            if verbose:
                try:
                    client = chromadb.HttpClient(host=host, port=port)
                    collections = client.list_collections()
                    print(f"  Collections: {len(collections)}")
                except Exception as e:
                    print(f"  Error getting collections: {e}")

            return chromadb.HttpClient(host=host, port=port)

        else:
            print(f"FAILED - Status {response.status_code}")
            return None

    except requests.ConnectionError as e:
        print(f"FAILED - {e}")
        return None


def create_test_collections(chromadb_client, verbose=False):
    """Create required test collections"""
    print("Creating test collections...", end=" ")

    try:
        collections = [
            ("personality_dna:sergio", "Sergio personality traits"),
            ("knowledge:humor", "Humor knowledge base"),
            ("test-collection", "Generic test collection"),
            ("personality_dna:test", "Test personality collection"),
        ]

        for name, description in collections:
            chromadb_client.get_or_create_collection(
                name=name,
                metadata={"description": description}
            )

            if verbose:
                print(f"\n  Created: {name}")

        print("OK")
        return True

    except Exception as e:
        print(f"FAILED - {e}")
        return False


def initialize_redis_data(redis_client, verbose=False):
    """Initialize test data in Redis"""
    print("Initializing Redis data...", end=" ")

    try:
        # Create test session
        session_id = "setup-test-session"

        redis_client.setex(
            f"session:{session_id}",
            3600,
            json.dumps({"status": "initialized", "created": "setup"})
        )

        # Create test conversation turns
        for i in range(3):
            redis_client.setex(
                f"conversation:{session_id}:{i}",
                3600,
                json.dumps({"turn": i, "content": f"Test turn {i}"})
            )

        # Create session registry
        redis_client.sadd("sessions:active", session_id)

        if verbose:
            print(f"\n  Session: {session_id}")
            print(f"  Conversation turns: 3")
            print(f"  TTL: 1 hour")

        print("OK")
        return True

    except Exception as e:
        print(f"FAILED - {e}")
        return False


def cleanup_test_data(redis_client, chromadb_client, verbose=False):
    """Clean up test data"""
    print("Cleaning up test data...", end=" ")

    try:
        # Clear Redis
        keys_to_delete = redis_client.keys("*")
        if keys_to_delete:
            redis_client.delete(*keys_to_delete)

        # Clear ChromaDB collections
        if chromadb_client:
            collections = chromadb_client.list_collections()
            for col in collections:
                try:
                    chromadb_client.delete_collection(name=col.name)
                except Exception as e:
                    if verbose:
                        print(f"\n  Warning: Could not delete {col.name}: {e}")

        if verbose:
            print(f"\n  Deleted {len(keys_to_delete)} Redis keys")
            print(f"  Deleted {len(collections)} ChromaDB collections")

        print("OK")
        return True

    except Exception as e:
        print(f"FAILED - {e}")
        return False


def report_status(redis_client, chromadb_client, verbose=False):
    """Report system status"""
    print("\n" + "=" * 60)
    print("SYSTEM STATUS")
    print("=" * 60)

    if redis_client:
        try:
            info = redis_client.info()
            print(f"\nRedis:")
            print(f"  Status: READY")
            print(f"  Version: {info.get('redis_version')}")
            print(f"  Memory: {info.get('used_memory_human')}")
            print(f"  Persistence: {info.get('rdb_last_save_time') > 0 and 'Enabled' or 'Disabled'}")

            # Check test data
            session_count = redis_client.scard("sessions:active")
            print(f"  Test sessions: {session_count}")

        except Exception as e:
            print(f"\nRedis: ERROR - {e}")
    else:
        print("\nRedis: NOT AVAILABLE")

    if chromadb_client:
        try:
            collections = chromadb_client.list_collections()
            print(f"\nChromaDB:")
            print(f"  Status: READY")
            print(f"  Collections: {len(collections)}")

            if verbose and collections:
                for col in collections:
                    print(f"    - {col.name}")

        except Exception as e:
            print(f"\nChromaDB: ERROR - {e}")
    else:
        print("\nChromaDB: NOT AVAILABLE")

    print("\n" + "=" * 60)


def main():
    """Main setup routine"""
    parser = argparse.ArgumentParser(
        description="Setup memory layer integration tests"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up test data"
    )
    parser.add_argument(
        "--redis-host",
        default="localhost",
        help="Redis host"
    )
    parser.add_argument(
        "--redis-port",
        type=int,
        default=6379,
        help="Redis port"
    )
    parser.add_argument(
        "--chromadb-host",
        default="localhost",
        help="ChromaDB host"
    )
    parser.add_argument(
        "--chromadb-port",
        type=int,
        default=8000,
        help="ChromaDB port"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("MEMORY LAYER INTEGRATION TEST SETUP")
    print("=" * 60 + "\n")

    # Check infrastructure
    redis_client = check_redis(args.redis_host, args.redis_port, args.verbose)
    chromadb_client = check_chromadb(args.chromadb_host, args.chromadb_port, args.verbose)

    if not redis_client or not chromadb_client:
        print("\nERROR: Required services not available")
        print("Start services with: docker-compose -f integration/docker-compose.test.yml up")
        return 1

    if args.cleanup:
        # Cleanup mode
        cleanup_test_data(redis_client, chromadb_client, args.verbose)
    else:
        # Setup mode
        create_test_collections(chromadb_client, args.verbose)
        initialize_redis_data(redis_client, args.verbose)

    # Report status
    report_status(redis_client, chromadb_client, args.verbose)

    print("\nSetup complete. Ready to run tests:")
    print("  pytest integration/test_memory_layer_integration.py -v")

    return 0


if __name__ == "__main__":
    sys.exit(main())
