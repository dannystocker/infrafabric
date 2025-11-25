# Redis Cloud Cache - Documentation Index

## Quick Links

| Document | Purpose | Last Updated |
|----------|---------|--------------|
| [STACKCP_REDIS_QUICK_REFERENCE.md](STACKCP_REDIS_QUICK_REFERENCE.md) | Quick access guide, connection details, common commands | 2025-11-23 |
| [STACKCP_REDIS_CACHE_REPORT.md](STACKCP_REDIS_CACHE_REPORT.md) | Full caching report, statistics, implementation details | 2025-11-23 |

## Tools

| Tool | Location | Purpose |
|------|----------|---------|
| cache_stackcp_to_redis.py | `/home/setup/infrafabric/tools/cache_stackcp_to_redis.py` | Automated caching script |

## Cached Content

### StackCP Infrastructure Documentation

**Primary Content Keys:**
- `context:infrastructure:stackcp-full:latest` (23 KB) - Full environment documentation
- `context:infrastructure:stackcp-all:latest` (16 KB) - Comprehensive reference

**Metadata:**
Each content key has associated metadata:
- `:hash` - MD5 integrity checksum
- `:size` - File size in bytes
- `:timestamp` - ISO 8601 cache time (UTC)
- `:tags` - Content classification tags

**Index Key:**
- `context:infrastructure:stackcp:keys` - Set containing all StackCP cache keys

## Redis Connection

```
Host: redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com
Port: 19956
User: default
Pass: zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8
```

## Cache Statistics

- **Files Cached:** 2
- **Total Size:** 39,181 bytes (38 KB)
- **Keys Created:** 11
- **TTL:** 30 days (expires 2025-12-23)
- **Redis Memory Used:** 2.84 MB
- **Total Keys in Redis:** 133

## Getting Started

1. **Quick Commands** → See [STACKCP_REDIS_QUICK_REFERENCE.md](STACKCP_REDIS_QUICK_REFERENCE.md)
2. **Full Details** → See [STACKCP_REDIS_CACHE_REPORT.md](STACKCP_REDIS_CACHE_REPORT.md)
3. **Re-cache Files** → Run `/home/setup/infrafabric/tools/cache_stackcp_to_redis.py`

## Important Dates

- **Cache Created:** 2025-11-23 21:02:22 UTC
- **TTL Expiration:** 2025-12-23 21:02:22 UTC
- **Refresh Reminder:** 2025-12-15 (8 days before expiration)

## File Locations

All documentation files are located at:
```
/home/setup/infrafabric/docs/
├── REDIS_CACHE_INDEX.md                    (this file)
├── STACKCP_REDIS_QUICK_REFERENCE.md       (quick commands)
└── STACKCP_REDIS_CACHE_REPORT.md          (full report)
```

Caching tool:
```
/home/setup/infrafabric/tools/
└── cache_stackcp_to_redis.py
```

## Next Steps

1. Review [STACKCP_REDIS_QUICK_REFERENCE.md](STACKCP_REDIS_QUICK_REFERENCE.md) for quick access
2. Set calendar reminder for 2025-12-15 to refresh cache before TTL expiration
3. When StackCP audit file is available, re-run caching script
4. Monitor Redis memory usage monthly

---

Last Updated: 2025-11-23 22:03 UTC
Status: PRODUCTION READY
