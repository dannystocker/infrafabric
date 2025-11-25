# StackCP Redis Cache - Quick Reference

## Redis Connection Details
```
Host: redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com
Port: 19956
User: default
Pass: zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8
```

## Cached Content Keys

### 1. Full Environment Documentation
- **Key:** `context:infrastructure:stackcp-full:latest`
- **Size:** 23,392 bytes
- **MD5:** `11287a696704b4d0e872c9e182c89463`
- **TTL:** 30 days (expires: 2025-12-23)
- **Source:** `/mnt/c/users/setup/downloads/stackcp-full-environment-doc.md`

### 2. All Documentation
- **Key:** `context:infrastructure:stackcp-all:latest`
- **Size:** 15,789 bytes
- **MD5:** `b23850a41fd38dfd7e3476c0e723d5d2`
- **TTL:** 30 days (expires: 2025-12-23)
- **Source:** `/mnt/c/users/setup/downloads/stackcp-all-docs.md`

## Quick Commands

### Retrieve Full Env Docs
```bash
redis-cli -h redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com \
  -p 19956 --user default --pass "zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8" \
  GET context:infrastructure:stackcp-full:latest
```

### Retrieve All Docs
```bash
redis-cli -h redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com \
  -p 19956 --user default --pass "zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8" \
  GET context:infrastructure:stackcp-all:latest
```

### List All StackCP Keys
```bash
redis-cli -h redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com \
  -p 19956 --user default --pass "zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8" \
  KEYS "context:infrastructure:stackcp*"
```

### Check TTL
```bash
redis-cli -h redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com \
  -p 19956 --user default --pass "zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8" \
  TTL context:infrastructure:stackcp-full:latest
```

### Save to File
```bash
redis-cli -h redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com \
  -p 19956 --user default --pass "zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8" \
  GET context:infrastructure:stackcp-full:latest > /tmp/stackcp-full.md
```

## Metadata Keys (Append to Content Key)

For any content key, these metadata keys are available:
- `:hash` - MD5 checksum
- `:size` - File size in bytes
- `:timestamp` - ISO 8601 cached timestamp (UTC)
- `:tags` - Comma-separated tag list

Example:
```bash
redis-cli ... GET context:infrastructure:stackcp-full:latest:hash
redis-cli ... GET context:infrastructure:stackcp-full:latest:size
redis-cli ... GET context:infrastructure:stackcp-full:latest:timestamp
redis-cli ... GET context:infrastructure:stackcp-full:latest:tags
```

## Python Access Example

```python
import redis

r = redis.Redis(
    host="redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com",
    port=19956,
    username="default",
    password="zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8",
    decode_responses=True
)

# Get content
content = r.get("context:infrastructure:stackcp-full:latest")

# Get metadata
hash_val = r.get("context:infrastructure:stackcp-full:latest:hash")
size = r.get("context:infrastructure:stackcp-full:latest:size")
timestamp = r.get("context:infrastructure:stackcp-full:latest:timestamp")

print(f"Size: {size} bytes, Hash: {hash_val}")
```

## Caching Tool

Automated caching script available at:
```
/home/setup/infrafabric/tools/cache_stackcp_to_redis.py
```

Run to cache additional StackCP files or refresh existing ones:
```bash
python3 /home/setup/infrafabric/tools/cache_stackcp_to_redis.py
```

## Full Report

See `/home/setup/infrafabric/docs/STACKCP_REDIS_CACHE_REPORT.md` for:
- Detailed caching results
- Redis statistics
- Key structure diagrams
- Access examples
- Monitoring recommendations

---
Last Updated: 2025-11-23 22:03 UTC
Cache TTL Refresh: 2025-12-23
