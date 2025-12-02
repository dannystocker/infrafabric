# ChromaDB Migration - Commands Reference Sheet

**Quick access to all commands used during migration**

## Pre-Migration Commands (T-24 Hours)

### Verify Source Health
```bash
cd /home/setup/infrafabric/tools

python3 << 'EOF'
import chromadb

source = chromadb.HttpClient(host='85.239.243.227', port=8000)
print("=== Source ChromaDB Health ===")

total = 0
for coll in source.list_collections():
    count = coll.count()
    total += count
    print(f"  {coll.name}: {count}")

print(f"Total chunks: {total}")
EOF
```

### Run Dry-Run Migration
```bash
cd /home/setup/infrafabric/tools

python3 chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --batch-size 100 \
  --dry-run \
  --verbose
```

### Review Dry-Run Logs
```bash
# Find latest log
LOG=$(ls -t /home/setup/infrafabric/migration_logs/migration_*.log | head -1)

# View summary (last 50 lines)
tail -50 "$LOG"

# View errors only
grep -i "error\|failed\|✗" "$LOG"

# View phases
grep -E "PHASE|Summary" "$LOG"
```

## Migration Execution Commands (T-0 to T+90)

### Step 1: Enable Read-Only Mode
```bash
# Via Docker (if running in container)
docker exec openwebui-chromadb \
  sh -c 'echo "CHROMA_READ_ONLY=true" >> .env'

# Verify read-only is active
python3 << 'EOF'
import chromadb

try:
    source = chromadb.HttpClient(host='85.239.243.227', port=8000)
    coll = source.get_collection('openwebui_core')

    # Try to add document (should fail)
    coll.add(ids=["test"], documents=["test"], embeddings=[[0.1]*1536])
    print("✗ Read-only NOT enabled")
except Exception as e:
    if "read-only" in str(e).lower():
        print("✓ Read-only mode ENABLED")
    else:
        print(f"? Unexpected error: {e}")
EOF
```

### Step 3: Run Full Migration
```bash
cd /home/setup/infrafabric/tools

python3 chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --batch-size 100 \
  --checkpoint-dir /home/setup/infrafabric/migration_checkpoints \
  --log-dir /home/setup/infrafabric/migration_logs \
  --verbose
```

### Step 4: Run Validation Tests
```bash
cd /home/setup/infrafabric/tools

python3 -m pytest test_chromadb_migration.py -v --tb=short
```

## Cutover Commands (Step 6a - If GO Decision)

### Update Configuration
```bash
for config in \
  /home/setup/infrafabric/.env \
  /home/setup/navidocs/.env; do

  if [ -f "$config" ]; then
    sed -i 's|CHROMADB_URL=.*|CHROMADB_URL=http://localhost:8000|g' "$config"
    echo "✓ Updated: $config"
  fi
done
```

### Restart Services
```bash
docker-compose -f /root/docker-compose.yml restart openwebui chromadb
sleep 30
```

## Rollback Commands (Step 7b - If NO-GO)

### Quick Rollback
```bash
pkill -f chromadb_migration

for config in \
  /home/setup/infrafabric/.env \
  /home/setup/navidocs/.env; do

  if [ -f "$config" ]; then
    sed -i 's|CHROMADB_URL=.*|CHROMADB_URL=http://85.239.243.227:8000|g' "$config"
  fi
done

curl -s -X POST http://85.239.243.227:8000/api/v1/admin/read-only \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

docker-compose -f /root/docker-compose.yml restart openwebui

echo "✓ Rollback complete"
```

---

**Location:** `/home/setup/infrafabric/docs/MIGRATION_COMMANDS_REFERENCE.md`
**Author:** A29 (ChromaDB Migration Operations Agent)
