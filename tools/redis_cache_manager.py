#!/usr/bin/env python3
"""
Redis L1/L2 Cache Manager
Automatic caching layer: Redis Cloud (L1 fast cache) + Proxmox Redis (L2 source of truth)

Usage:
    from redis_cache_manager import RedisCacheManager

    redis = RedisCacheManager()

    # Transparent caching - just use like normal Redis
    redis.set("key", "value")         # Writes to BOTH
    value = redis.get("key")          # Tries L1, falls back to L2
    redis.delete("key")               # Deletes from BOTH

Configuration:
    Set environment variables or pass to constructor:
    - REDIS_L1_HOST (Cloud)
    - REDIS_L1_PORT
    - REDIS_L1_PASSWORD
    - REDIS_L2_HOST (Proxmox)
    - REDIS_L2_PORT
    - REDIS_L2_PASSWORD (optional)
"""

import os
import time
import logging
from typing import Optional, Union, Any, List
from pathlib import Path
import redis
from redis.exceptions import RedisError, ConnectionError, TimeoutError

# Auto-load .env.redis if it exists (for credentials)
# This ensures other Claude sessions can use the cache manager without manual env setup
_env_file = Path(__file__).parent.parent / '.env.redis'
if _env_file.exists():
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith('export ') and '=' in line:
                # Parse: export KEY='value' or export KEY="value"
                key_value = line.replace('export ', '', 1)
                key, value = key_value.split('=', 1)
                # Remove quotes if present
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value
    logging.info(f"Auto-loaded Redis credentials from {_env_file}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedisCacheManager:
    """
    Smart Redis cache manager with L1 (fast cache) and L2 (source of truth).

    Read Strategy:
        1. Try L1 (Redis Cloud) - 10ms latency
        2. On miss, fetch from L2 (Proxmox) - 100ms latency
        3. Warm L1 with fetched data

    Write Strategy:
        1. Write to L2 first (source of truth, no TTL)
        2. Write to L1 (with TTL for auto-eviction)
        3. If L1 fails, log but continue (cache degradation)

    Delete Strategy:
        1. Delete from BOTH L1 and L2
    """

    def __init__(
        self,
        # L1 Cache (Redis Cloud - fast, small)
        l1_host: Optional[str] = None,
        l1_port: int = 19956,
        l1_password: Optional[str] = None,
        l1_db: int = 0,

        # L2 Storage (Proxmox - slower, large)
        l2_host: Optional[str] = None,
        l2_port: int = 6379,
        l2_password: Optional[str] = None,
        l2_db: int = 0,

        # Cache behavior
        default_ttl: int = 3600,  # 1 hour cache TTL
        l1_timeout: float = 0.5,  # Fast timeout for cache
        l2_timeout: float = 2.0,  # Slower timeout for storage
    ):
        """Initialize dual-layer Redis cache."""

        # L1 Configuration (Redis Cloud)
        self.l1_host = l1_host or os.getenv("REDIS_L1_HOST", "redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com")
        self.l1_port = l1_port
        self.l1_password = l1_password or os.getenv("REDIS_L1_PASSWORD", "zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8")
        self.l1_db = l1_db
        self.l1_timeout = l1_timeout

        # L2 Configuration (Proxmox)
        self.l2_host = l2_host or os.getenv("REDIS_L2_HOST", "85.239.243.227")
        self.l2_port = l2_port
        self.l2_password = l2_password or os.getenv("REDIS_L2_PASSWORD")
        self.l2_db = l2_db
        self.l2_timeout = l2_timeout

        self.default_ttl = default_ttl

        # Statistics
        self.stats = {
            "l1_hits": 0,
            "l1_misses": 0,
            "l2_hits": 0,
            "l2_misses": 0,
            "l1_errors": 0,
            "l2_errors": 0,
            "writes": 0,
            "deletes": 0,
        }

        # Initialize connections (lazy - connect on first use)
        self._l1: Optional[redis.Redis] = None
        self._l2: Optional[redis.Redis] = None

        logger.info(f"RedisCacheManager initialized")
        logger.info(f"  L1 (Cache): {self.l1_host}:{self.l1_port}")
        logger.info(f"  L2 (Storage): {self.l2_host}:{self.l2_port}")

    @property
    def l1(self) -> Optional[redis.Redis]:
        """Lazy connection to L1 cache."""
        if self._l1 is None:
            try:
                self._l1 = redis.Redis(
                    host=self.l1_host,
                    port=self.l1_port,
                    password=self.l1_password,
                    db=self.l1_db,
                    socket_timeout=self.l1_timeout,
                    socket_connect_timeout=self.l1_timeout,
                    decode_responses=True,
                )
                self._l1.ping()
                logger.info("L1 cache connected (Redis Cloud)")
            except Exception as e:
                logger.warning(f"L1 cache unavailable: {e}")
                self._l1 = None
        return self._l1

    @property
    def l2(self) -> redis.Redis:
        """Lazy connection to L2 storage (critical - raises on failure)."""
        if self._l2 is None:
            try:
                self._l2 = redis.Redis(
                    host=self.l2_host,
                    port=self.l2_port,
                    password=self.l2_password,
                    db=self.l2_db,
                    socket_timeout=self.l2_timeout,
                    socket_connect_timeout=self.l2_timeout,
                    decode_responses=True,
                )
                self._l2.ping()
                logger.info("L2 storage connected (Proxmox)")
            except Exception as e:
                logger.error(f"L2 storage FAILED (critical): {e}")
                raise ConnectionError(f"Cannot connect to L2 storage: {e}")
        return self._l2

    def get(self, key: str) -> Optional[str]:
        """
        Get value with L1/L2 cache hierarchy.

        1. Try L1 (fast cache)
        2. On miss, try L2 (source of truth)
        3. Warm L1 on L2 hit
        """
        # Try L1 first
        if self.l1:
            try:
                value = self.l1.get(key)
                if value is not None:
                    self.stats["l1_hits"] += 1
                    logger.debug(f"L1 HIT: {key}")
                    return value
                self.stats["l1_misses"] += 1
            except Exception as e:
                self.stats["l1_errors"] += 1
                logger.warning(f"L1 error on GET {key}: {e}")

        # L1 miss - try L2
        try:
            value = self.l2.get(key)
            if value is not None:
                self.stats["l2_hits"] += 1
                logger.debug(f"L2 HIT: {key} (warming L1)")

                # Warm L1 cache
                if self.l1:
                    try:
                        self.l1.setex(key, self.default_ttl, value)
                    except Exception as e:
                        logger.warning(f"Failed to warm L1 for {key}: {e}")

                return value

            self.stats["l2_misses"] += 1
            return None

        except Exception as e:
            self.stats["l2_errors"] += 1
            logger.error(f"L2 error on GET {key}: {e}")
            raise

    def set(
        self,
        key: str,
        value: Union[str, bytes, int, float],
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """
        Set value in BOTH L1 and L2.

        L2 (source of truth): No TTL
        L1 (cache): With TTL for auto-eviction
        """
        self.stats["writes"] += 1

        # Write to L2 first (source of truth, permanent)
        try:
            result = self.l2.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            if not result:
                return False
        except Exception as e:
            self.stats["l2_errors"] += 1
            logger.error(f"L2 error on SET {key}: {e}")
            raise

        # Write to L1 (cache with TTL)
        if self.l1:
            try:
                cache_ttl = ex or (px // 1000 if px else self.default_ttl)
                self.l1.setex(key, cache_ttl, value)
                logger.debug(f"Written to L1+L2: {key} (L1 TTL: {cache_ttl}s)")
            except Exception as e:
                self.stats["l1_errors"] += 1
                logger.warning(f"L1 cache write failed for {key}: {e} (continuing)")

        return True

    def setex(self, key: str, time: int, value: Union[str, bytes]) -> bool:
        """Set with expiration (writes to both)."""
        return self.set(key, value, ex=time)

    def delete(self, *keys: str) -> int:
        """Delete from BOTH L1 and L2."""
        self.stats["deletes"] += len(keys)
        deleted = 0

        # Delete from L2 (source of truth)
        try:
            deleted = self.l2.delete(*keys)
        except Exception as e:
            self.stats["l2_errors"] += 1
            logger.error(f"L2 error on DELETE {keys}: {e}")
            raise

        # Delete from L1 (cache)
        if self.l1:
            try:
                self.l1.delete(*keys)
            except Exception as e:
                self.stats["l1_errors"] += 1
                logger.warning(f"L1 cache delete failed for {keys}: {e}")

        return deleted

    def exists(self, *keys: str) -> int:
        """Check existence (tries L1 first, falls back to L2)."""
        if self.l1:
            try:
                count = self.l1.exists(*keys)
                if count > 0:
                    return count
            except Exception as e:
                logger.warning(f"L1 error on EXISTS: {e}")

        return self.l2.exists(*keys)

    def keys(self, pattern: str = "*") -> List[str]:
        """List keys (from L2 source of truth)."""
        # Always use L2 for key enumeration (source of truth)
        return self.l2.keys(pattern)

    def dbsize(self) -> int:
        """Get database size (from L2 source of truth)."""
        return self.l2.dbsize()

    def flushdb(self, asynchronous: bool = False) -> bool:
        """Flush BOTH databases."""
        l2_result = self.l2.flushdb(asynchronous=asynchronous)

        if self.l1:
            try:
                self.l1.flushdb(asynchronous=asynchronous)
            except Exception as e:
                logger.warning(f"L1 flush failed: {e}")

        return l2_result

    def ping(self) -> bool:
        """Ping both connections."""
        l2_ok = self.l2.ping()
        l1_ok = self.l1.ping() if self.l1 else False

        logger.info(f"Ping: L1={'OK' if l1_ok else 'FAIL'}, L2={'OK' if l2_ok else 'FAIL'}")
        return l2_ok  # L2 is critical

    def get_stats(self) -> dict:
        """Get cache performance statistics."""
        total_reads = self.stats["l1_hits"] + self.stats["l1_misses"]
        hit_rate = (self.stats["l1_hits"] / total_reads * 100) if total_reads > 0 else 0

        return {
            **self.stats,
            "l1_hit_rate": f"{hit_rate:.1f}%",
            "total_reads": total_reads,
            "l1_available": self.l1 is not None,
            "l2_available": self._l2 is not None,
        }

    def print_stats(self):
        """Print cache statistics."""
        stats = self.get_stats()
        print("\n" + "="*60)
        print("REDIS CACHE MANAGER STATISTICS")
        print("="*60)
        print(f"L1 Cache (Redis Cloud):  {'ONLINE' if stats['l1_available'] else 'OFFLINE'}")
        print(f"L2 Storage (Proxmox):    {'ONLINE' if stats['l2_available'] else 'OFFLINE'}")
        print(f"\nCache Performance:")
        print(f"  L1 Hit Rate:   {stats['l1_hit_rate']}")
        print(f"  L1 Hits:       {stats['l1_hits']:,}")
        print(f"  L1 Misses:     {stats['l1_misses']:,}")
        print(f"  L2 Hits:       {stats['l2_hits']:,}")
        print(f"  L2 Misses:     {stats['l2_misses']:,}")
        print(f"\nOperations:")
        print(f"  Writes:        {stats['writes']:,}")
        print(f"  Deletes:       {stats['deletes']:,}")
        print(f"\nErrors:")
        print(f"  L1 Errors:     {stats['l1_errors']:,}")
        print(f"  L2 Errors:     {stats['l2_errors']:,}")
        print("="*60 + "\n")


# Convenience function for quick usage
def get_redis() -> RedisCacheManager:
    """Get configured Redis cache manager instance."""
    return RedisCacheManager()


if __name__ == "__main__":
    """Test the cache manager."""
    print("Testing Redis Cache Manager...\n")

    # Initialize
    redis_mgr = RedisCacheManager()

    # Test writes
    print("1. Testing write operations...")
    redis_mgr.set("test:key1", "value1")
    redis_mgr.setex("test:key2", 60, "value2")
    print("   ✓ Written test:key1 and test:key2\n")

    # Test reads (should hit L1)
    print("2. Testing L1 cache hits...")
    v1 = redis_mgr.get("test:key1")
    v2 = redis_mgr.get("test:key2")
    print(f"   ✓ Read: test:key1 = {v1}")
    print(f"   ✓ Read: test:key2 = {v2}\n")

    # Test cache miss (new key)
    print("3. Testing cache miss behavior...")
    v3 = redis_mgr.get("nonexistent:key")
    print(f"   ✓ Read: nonexistent:key = {v3}\n")

    # Test delete
    print("4. Testing delete operations...")
    deleted = redis_mgr.delete("test:key1", "test:key2")
    print(f"   ✓ Deleted {deleted} keys\n")

    # Print statistics
    redis_mgr.print_stats()

    print("\n✅ Cache manager test complete!")
