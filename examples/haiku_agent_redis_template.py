#!/usr/bin/env python3
"""
Template for Haiku agents using Redis cache manager.

DROP-IN REPLACEMENT:
    OLD: import redis; r = redis.Redis(host='localhost', port=6379)
    NEW: from tools.redis_cache_manager import get_redis; r = get_redis()

That's it! The cache manager handles L1/L2 automatically.
"""

import sys
import os
sys.path.insert(0, '/home/setup/infrafabric')

from tools.redis_cache_manager import get_redis

def main():
    """Example Haiku agent using Redis cache manager."""

    # Initialize Redis (automatically connects to L1+L2)
    redis = get_redis()

    # Use like normal Redis - cache manager handles everything
    print("Storing session context...")
    redis.set("session:haiku:current", "analyzing legal corpus...")
    redis.setex("session:haiku:temp", 300, "temporary debug info")

    print("Reading context...")
    context = redis.get("session:haiku:current")
    print(f"Current context: {context}")

    # Check if agents.md is cached
    agents_md = redis.get("context:file:agents.md")
    if agents_md:
        print(f"✓ agents.md cached ({len(agents_md)} bytes)")
    else:
        print("✗ agents.md not in cache, reading from disk...")
        with open('/home/setup/infrafabric/agents.md', 'r') as f:
            agents_md = f.read()
        redis.setex("context:file:agents.md", 7200, agents_md)  # Cache 2hrs

    # Store findings (permanent in L2, cached in L1)
    redis.set("finding:haiku:corpus_analysis", "Found 42 relevant precedents")

    # Print cache performance
    redis.print_stats()


if __name__ == "__main__":
    main()
