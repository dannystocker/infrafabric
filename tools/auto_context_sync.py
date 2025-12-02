#!/usr/bin/env python3
"""
Auto Context Sync to Redis L1/L2

Automatically syncs critical context files to Redis on session start/end.
Called from .bashrc or manually.

Usage:
    # On session start (warm cache):
    python auto_context_sync.py --mode start

    # On session end (preserve session data):
    python auto_context_sync.py --mode end

    # Manual sync:
    python auto_context_sync.py --mode manual
"""

import sys
import os
import argparse
import time
from pathlib import Path

# Add infrafabric to path
sys.path.insert(0, '/home/setup/infrafabric')

from tools.redis_cache_manager import get_redis

# Critical files to always keep cached
CRITICAL_FILES = {
    "agents.md": {
        "path": "/home/setup/infrafabric/agents.md",
        "key": "context:file:agents.md:v1.4",
        "ttl": 7200,  # 2 hours
        "description": "Master documentation for all projects"
    },
    "navidocs_session_summary": {
        "path": "/home/setup/infrafabric/NAVIDOCS_SESSION_SUMMARY.md",
        "key": "context:file:navidocs_session_summary",
        "ttl": 7200,
        "description": "NaviDocs cloud session quick reference"
    },
    ".env.redis": {
        "path": "/home/setup/infrafabric/.env.redis",
        "key": "context:config:redis_env",
        "ttl": 86400,  # 24 hours
        "description": "Redis L1/L2 configuration"
    }
}

# Session metadata
SESSION_KEY = "context:session:current"


def sync_critical_files(redis, verbose=True):
    """Sync critical files to Redis L1/L2."""
    synced = []
    skipped = []
    errors = []

    for file_id, config in CRITICAL_FILES.items():
        path = config["path"]
        key = config["key"]
        ttl = config["ttl"]

        if not os.path.exists(path):
            skipped.append(f"{file_id} (not found)")
            continue

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Store with TTL
            redis.setex(key, ttl, content)

            synced.append(f"{file_id} ({len(content)} bytes, TTL: {ttl}s)")

            if verbose:
                print(f"  ✅ {file_id}: {len(content)} bytes → {key}")

        except Exception as e:
            errors.append(f"{file_id}: {str(e)}")
            if verbose:
                print(f"  ❌ {file_id}: {str(e)}")

    return synced, skipped, errors


def session_start(redis):
    """Called on session start - warm cache."""
    print("=" * 70)
    print("AUTO CONTEXT SYNC - SESSION START")
    print("=" * 70)

    # Store session start metadata
    session_data = {
        "mode": "start",
        "timestamp": time.time(),
        "hostname": os.uname().nodename,
        "pid": os.getpid()
    }

    import json
    redis.setex(SESSION_KEY, 3600, json.dumps(session_data))

    print("\n📤 Syncing critical files to Redis L1/L2...")
    synced, skipped, errors = sync_critical_files(redis)

    print(f"\n✅ Synced: {len(synced)} files")
    if skipped:
        print(f"⏭️  Skipped: {len(skipped)} files")
    if errors:
        print(f"❌ Errors: {len(errors)} files")

    # Show cache stats
    print("\n" + "=" * 70)
    redis.print_stats()


def session_end(redis):
    """Called on session end - preserve session data."""
    print("=" * 70)
    print("AUTO CONTEXT SYNC - SESSION END")
    print("=" * 70)

    # Get session data
    session_json = redis.get(SESSION_KEY)

    if session_json:
        import json
        session_data = json.loads(session_json)
        duration = time.time() - session_data.get("timestamp", time.time())

        print(f"\n📊 Session Duration: {duration/60:.1f} minutes")

        # Archive session to permanent storage
        archive_key = f"context:session:archive:{int(time.time())}"
        session_data["mode"] = "end"
        session_data["end_timestamp"] = time.time()
        session_data["duration_seconds"] = duration

        redis.set(archive_key, json.dumps(session_data))  # Permanent in L2
        print(f"💾 Session archived: {archive_key}")

    # Sync critical files one last time
    print("\n📤 Final sync of critical files...")
    synced, skipped, errors = sync_critical_files(redis, verbose=False)

    print(f"✅ Synced: {len(synced)} files")

    # Show final stats
    print("\n" + "=" * 70)
    redis.print_stats()


def manual_sync(redis):
    """Manual sync - user-initiated."""
    print("=" * 70)
    print("AUTO CONTEXT SYNC - MANUAL")
    print("=" * 70)

    print("\n📤 Syncing critical files to Redis L1/L2...")
    synced, skipped, errors = sync_critical_files(redis)

    print(f"\n✅ Synced: {len(synced)} files")
    if skipped:
        print(f"⏭️  Skipped: {len(skipped)} files:")
        for item in skipped:
            print(f"     - {item}")
    if errors:
        print(f"❌ Errors: {len(errors)} files:")
        for item in errors:
            print(f"     - {item}")

    # Show stats
    print("\n" + "=" * 70)
    redis.print_stats()


def main():
    parser = argparse.ArgumentParser(
        description="Auto Context Sync to Redis L1/L2"
    )
    parser.add_argument(
        "--mode",
        choices=["start", "end", "manual"],
        default="manual",
        help="Sync mode: start (session start), end (session end), manual (user-initiated)"
    )

    args = parser.parse_args()

    # Initialize Redis cache manager
    redis = get_redis()

    # Run appropriate sync mode
    if args.mode == "start":
        session_start(redis)
    elif args.mode == "end":
        session_end(redis)
    else:
        manual_sync(redis)


if __name__ == "__main__":
    main()
