#!/usr/bin/env python3
"""
Cache StackCP infrastructure documentation to Redis Cloud.
Implements metadata caching with TTL, hashing, and tagging.
"""

import os
import hashlib
import json
from datetime import datetime, timedelta
import redis

# Redis Cloud Configuration
REDIS_HOST = "redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com"
REDIS_PORT = 19956
REDIS_USER = "default"
REDIS_PASS = "zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8"
TTL_SECONDS = 2592000  # 30 days

# Files to cache
FILES_TO_CACHE = [
    {
        "path": "/mnt/c/users/setup/downloads/stackcp-full-environment-doc.md",
        "key": "context:infrastructure:stackcp-full:latest",
        "tags": "stackcp,infrastructure,deployment,ssh,hosting"
    },
    {
        "path": "/mnt/c/users/setup/downloads/stackcp-all-docs.md",
        "key": "context:infrastructure:stackcp-all:latest",
        "tags": "stackcp,infrastructure,reference,tools,php"
    },
    {
        "path": "/mnt/c/users/setup/downloads/STACKCP-INFRASTRUCTURE-AUDIT-2025-11-23.md",
        "key": "context:infrastructure:stackcp-audit:latest",
        "tags": "stackcp,infrastructure,audit,security"
    }
]

def calculate_md5(file_path):
    """Calculate MD5 hash of file content."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_file_size(file_path):
    """Get file size in bytes."""
    return os.path.getsize(file_path)

def cache_file_to_redis(r, file_path, cache_key, tags):
    """Cache a single file to Redis with metadata."""

    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Calculate metadata
    file_hash = calculate_md5(file_path)
    file_size = get_file_size(file_path)
    timestamp = datetime.utcnow().isoformat()

    # Create pipeline for atomic operations
    pipe = r.pipeline()

    # Store main content with TTL
    pipe.setex(cache_key, TTL_SECONDS, content)

    # Store metadata
    pipe.setex(f"{cache_key}:hash", TTL_SECONDS, file_hash)
    pipe.setex(f"{cache_key}:size", TTL_SECONDS, str(file_size))
    pipe.setex(f"{cache_key}:timestamp", TTL_SECONDS, timestamp)
    pipe.setex(f"{cache_key}:tags", TTL_SECONDS, tags)

    # Add to index
    pipe.sadd("context:infrastructure:stackcp:keys", cache_key)

    # Execute pipeline
    pipe.execute()

    return {
        "file": os.path.basename(file_path),
        "key": cache_key,
        "hash": file_hash,
        "size": file_size,
        "timestamp": timestamp,
        "tags": tags.split(','),
        "status": "cached"
    }

def main():
    """Main execution."""
    print("StackCP Infrastructure Documentation Caching")
    print("=" * 60)
    print(f"Target Redis: {REDIS_HOST}:{REDIS_PORT}")
    print(f"TTL: {TTL_SECONDS} seconds (30 days)")
    print()

    try:
        # Connect to Redis (no SSL - direct connection)
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            username=REDIS_USER,
            password=REDIS_PASS,
            decode_responses=True
        )

        # Test connection
        r.ping()
        print("[OK] Connected to Redis Cloud")
        print()

    except Exception as e:
        print(f"[ERROR] Failed to connect to Redis: {e}")
        return

    # Track results
    cached_files = []
    skipped_files = []
    total_bytes = 0

    # Process each file
    for file_config in FILES_TO_CACHE:
        file_path = file_config["path"]
        cache_key = file_config["key"]
        tags = file_config["tags"]

        # Check if file exists
        if not os.path.exists(file_path):
            skipped_files.append({
                "file": os.path.basename(file_path),
                "reason": "File not found",
                "path": file_path
            })
            print(f"[SKIP] {os.path.basename(file_path)} - NOT FOUND")
            continue

        try:
            # Cache the file
            result = cache_file_to_redis(r, file_path, cache_key, tags)
            cached_files.append(result)
            total_bytes += result["size"]

            print(f"[CACHED] {result['file']}")
            print(f"  Key: {result['key']}")
            print(f"  Size: {result['size']:,} bytes")
            print(f"  Hash: {result['hash']}")
            print(f"  Tags: {', '.join(result['tags'])}")
            print()

        except Exception as e:
            skipped_files.append({
                "file": os.path.basename(file_path),
                "reason": str(e),
                "path": file_path
            })
            print(f"[ERROR] {os.path.basename(file_path)} - {e}")
            print()

    # Summary
    print("=" * 60)
    print("CACHING SUMMARY")
    print("=" * 60)
    print(f"Files Cached: {len(cached_files)}")
    print(f"Files Skipped: {len(skipped_files)}")
    print(f"Total Bytes Cached: {total_bytes:,}")
    print(f"New Redis Keys: {len(cached_files) * 5}")  # content + 4 metadata keys per file
    print()

    if cached_files:
        print("CACHED FILES:")
        for f in cached_files:
            print(f"  - {f['file']} ({f['size']:,} bytes)")
        print()

    if skipped_files:
        print("SKIPPED FILES:")
        for f in skipped_files:
            print(f"  - {f['file']}: {f['reason']}")
        print()

    # Get Redis stats
    try:
        info = r.info()
        print("REDIS CLOUD STATS:")
        print(f"  Used Memory: {info.get('used_memory_human', 'N/A')}")
        print(f"  Keys Count: {info.get('db0', {}).get('keys', 'N/A') if isinstance(info.get('db0'), dict) else 'N/A'}")
        print(f"  Connected Clients: {info.get('connected_clients', 'N/A')}")
    except Exception as e:
        print(f"Could not retrieve Redis stats: {e}")

if __name__ == "__main__":
    main()
