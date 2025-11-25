#!/usr/bin/env python3
"""
Redis Migration Script: Local WSL to Redis Cloud
Migrates all keys with type detection, TTL preservation, and progress tracking
"""

import redis
import time
import sys
from typing import Dict, List, Any

class RedisMigrator:
    def __init__(self, local_host='localhost', local_port=6379,
                 cloud_host='redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com',
                 cloud_port=19956, cloud_user='default', cloud_pass='zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8'):
        """Initialize connections to local and cloud Redis"""

        print("[*] Connecting to local Redis...")
        self.local = redis.Redis(
            host=local_host,
            port=local_port,
            db=0,
            decode_responses=True
        )

        print("[*] Connecting to cloud Redis...")
        self.cloud = redis.Redis(
            host=cloud_host,
            port=cloud_port,
            username=cloud_user,
            password=cloud_pass,
            db=0,
            decode_responses=True
        )

        # Verify connections
        try:
            self.local.ping()
            print("[+] Local Redis connected")
        except Exception as e:
            print(f"[-] Failed to connect to local Redis: {e}")
            sys.exit(1)

        try:
            self.cloud.ping()
            print("[+] Cloud Redis connected")
        except Exception as e:
            print(f"[-] Failed to connect to cloud Redis: {e}")
            sys.exit(1)

        self.stats = {
            'total': 0,
            'migrated': 0,
            'errors': 0,
            'strings': 0,
            'hashes': 0,
            'lists': 0,
            'sets': 0,
            'zsets': 0
        }

    def get_key_type(self, key: str) -> str:
        """Determine the type of a Redis key"""
        return self.local.type(key)

    def migrate_string(self, key: str, pipeline) -> bool:
        """Migrate a string key"""
        try:
            value = self.local.get(key)
            ttl = self.local.ttl(key)

            if ttl > 0:
                pipeline.setex(key, ttl, value)
            else:
                pipeline.set(key, value)

            self.stats['strings'] += 1
            return True
        except Exception as e:
            print(f"[-] Error migrating string '{key}': {e}")
            return False

    def migrate_hash(self, key: str, pipeline) -> bool:
        """Migrate a hash key"""
        try:
            data = self.local.hgetall(key)
            ttl = self.local.ttl(key)

            pipeline.delete(key)
            pipeline.hset(key, mapping=data)

            if ttl > 0:
                pipeline.expire(key, ttl)

            self.stats['hashes'] += 1
            return True
        except Exception as e:
            print(f"[-] Error migrating hash '{key}': {e}")
            return False

    def migrate_list(self, key: str, pipeline) -> bool:
        """Migrate a list key"""
        try:
            data = self.local.lrange(key, 0, -1)
            ttl = self.local.ttl(key)

            pipeline.delete(key)
            if data:
                pipeline.rpush(key, *data)

            if ttl > 0:
                pipeline.expire(key, ttl)

            self.stats['lists'] += 1
            return True
        except Exception as e:
            print(f"[-] Error migrating list '{key}': {e}")
            return False

    def migrate_set(self, key: str, pipeline) -> bool:
        """Migrate a set key"""
        try:
            data = self.local.smembers(key)
            ttl = self.local.ttl(key)

            pipeline.delete(key)
            if data:
                pipeline.sadd(key, *data)

            if ttl > 0:
                pipeline.expire(key, ttl)

            self.stats['sets'] += 1
            return True
        except Exception as e:
            print(f"[-] Error migrating set '{key}': {e}")
            return False

    def migrate_zset(self, key: str, pipeline) -> bool:
        """Migrate a sorted set key"""
        try:
            data = self.local.zrange(key, 0, -1, withscores=True)
            ttl = self.local.ttl(key)

            pipeline.delete(key)
            if data:
                pipeline.zadd(key, {member: score for member, score in data})

            if ttl > 0:
                pipeline.expire(key, ttl)

            self.stats['zsets'] += 1
            return True
        except Exception as e:
            print(f"[-] Error migrating zset '{key}': {e}")
            return False

    def migrate_all(self, batch_size: int = 100):
        """Migrate all keys using SCAN with batching"""
        print(f"\n[*] Starting migration with batch size {batch_size}...")
        start_time = time.time()

        cursor = 0
        pipeline = self.cloud.pipeline()
        batch_count = 0

        while True:
            cursor, keys = self.local.scan(cursor, count=batch_size)

            if not keys:
                if cursor == 0:
                    break
                continue

            for key in keys:
                self.stats['total'] += 1
                key_type = self.get_key_type(key)

                success = False
                if key_type == 'string':
                    success = self.migrate_string(key, pipeline)
                elif key_type == 'hash':
                    success = self.migrate_hash(key, pipeline)
                elif key_type == 'list':
                    success = self.migrate_list(key, pipeline)
                elif key_type == 'set':
                    success = self.migrate_set(key, pipeline)
                elif key_type == 'zset':
                    success = self.migrate_zset(key, pipeline)
                else:
                    print(f"[-] Unknown type '{key_type}' for key '{key}'")
                    self.stats['errors'] += 1

                if success:
                    self.stats['migrated'] += 1
                else:
                    self.stats['errors'] += 1

                # Progress indicator every 10 keys
                if self.stats['total'] % 10 == 0:
                    print(f"[+] Progress: {self.stats['total']} keys processed ({self.stats['migrated']} migrated)")

                # Execute pipeline batch
                batch_count += 1
                if batch_count % batch_size == 0:
                    try:
                        pipeline.execute()
                        pipeline = self.cloud.pipeline()
                        print(f"[+] Batch executed ({batch_count} commands)")
                    except Exception as e:
                        print(f"[-] Pipeline execution error: {e}")
                        self.stats['errors'] += 1

            if cursor == 0:
                break

        # Execute remaining batch
        if batch_count % batch_size != 0:
            try:
                pipeline.execute()
                print(f"[+] Final batch executed")
            except Exception as e:
                print(f"[-] Final pipeline execution error: {e}")

        elapsed = time.time() - start_time
        self.print_summary(elapsed)

    def print_summary(self, elapsed: float):
        """Print migration summary"""
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Total keys processed:  {self.stats['total']}")
        print(f"Successfully migrated: {self.stats['migrated']}")
        print(f"Errors:                {self.stats['errors']}")
        print(f"\nData types migrated:")
        print(f"  - Strings: {self.stats['strings']}")
        print(f"  - Hashes:  {self.stats['hashes']}")
        print(f"  - Lists:   {self.stats['lists']}")
        print(f"  - Sets:    {self.stats['sets']}")
        print(f"  - Zsets:   {self.stats['zsets']}")
        print(f"\nExecution time: {elapsed:.2f} seconds")
        print("="*60)

if __name__ == '__main__':
    migrator = RedisMigrator()
    migrator.migrate_all(batch_size=100)
