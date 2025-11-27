# Redis Cloud Migration Guide

## Overview

This suite of tools facilitates the migration of 15 IF.* components from SQLite to Redis Cloud. The components have been extracted from the InfraFabric component inventory and are organized by status (implemented, partial, vaporware) and category.

## Database State

### SQLite Database
- **Location**: `/tmp/infrafabric-sqlite/infrafabric_knowledge.db`
- **Components**: 15 IF.* components
- **Schema**: `components` table with name, description, status, category, source_file_id

### Components Summary
- **Total**: 15 components
- **Implemented**: 0
- **Partial**: 7 (IF.ground, IF.search, IF.persona, IF.armour, IF.witness, IF.yologuard, IF.optimise)
- **Vaporware**: 8 (IF.router, IF.memory, IF.trace, IF.pulse, IF.ceo, IF.vesicle, IF.kernel, IF.guardian/IF.guard)

### Categories
- **Discovery** (1): IF.search
- **Foundations** (1): IF.ground
- **General** (9): IF.armour, IF.ceo, IF.kernel, IF.optimise, IF.persona, IF.pulse, IF.router, IF.vesicle, IF.witness
- **Governance** (2): IF.guardian/IF.guard, IF.yologuard
- **State** (2): IF.memory, IF.trace

## Redis Cloud Configuration

### Connection Details
- **Host**: `redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com`
- **Port**: `19956`
- **Database**: 0
- **Authentication**: Bearer token or password required

### Redis Key Schema

#### Component Hashes
```
if:component:{name}
```
Each hash contains:
- `name`: Component name (e.g., "IF.guard")
- `description`: Status description/evidence
- `status`: Component status (implemented, partial, vaporware)
- `category`: Component category
- `source_file_id`: Source file reference with line numbers

Example:
```redis
HSET if:component:IF.guard \
  name "IF.guard" \
  description "Guardian council debates reside in external annex archive..." \
  status "vaporware" \
  category "governance" \
  source_file_id "README.md:145-147"
```

#### Category Indexes (Sets)
```
if:components:category:{category}
```
Members: All component names in that category

Categories:
- `if:components:category:discovery`
- `if:components:category:foundations`
- `if:components:category:general`
- `if:components:category:governance`
- `if:components:category:state`

#### File Indexes (Sets)
```
if:file:{source_file_id}:components
```
Members: All component names from that source file

Example:
```redis
SADD if:file:README.md:145-147:components "IF.guardian/IF.guard"
```

#### Master Component Index (Set)
```
if:components:all
```
Members: All 15 component names

## Tools

### 1. sqlite_to_redis_migration.py
Full migration tool that pushes components from SQLite to Redis Cloud.

**Requirements**:
- Redis Cloud credentials (host, port, password)
- Python packages: `redis`, `pyyaml`

**Usage**:
```bash
python3 tools/sqlite_to_redis_migration.py \
  --sqlite-db /tmp/infrafabric-sqlite/infrafabric_knowledge.db \
  --redis-host redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com \
  --redis-port 19956 \
  --redis-password YOUR_PASSWORD_HERE \
  --yaml-inventory /home/setup/infrafabric/docs/evidence/IF_COMPONENT_INVENTORY.yaml
```

**Output**:
```json
{
  "components_pushed": 15,
  "categories": ["discovery", "foundations", "general", "governance", "state"],
  "errors": [],
  "sample_keys": ["if:component:IF.guard", ...],
  "indexes_created": ["if:components:all", ...]
}
```

### 2. redis_migration_simulation.py
Simulation tool that generates a detailed report without requiring Redis credentials.

**Usage**:
```bash
python3 tools/redis_migration_simulation.py \
  --sqlite-db /tmp/infrafabric-sqlite/infrafabric_knowledge.db \
  --output-file migration_report.json
```

**Output**:
- JSON report with full component inventory
- Operation counts and structure
- Category and status breakdowns
- Detailed component metadata

**Example Report**:
```json
{
  "status": "SIMULATION_READY",
  "components_ready_for_push": 15,
  "total_operations": {
    "component_hashes": 15,
    "category_sets": 5,
    "file_indexes": 12,
    "all_components_set": 1,
    "total": 33
  },
  "components_by_status": {
    "implemented": 0,
    "partial": 7,
    "vaporware": 8
  },
  "components_by_category": {
    "discovery": 1,
    "foundations": 1,
    "general": 9,
    "governance": 2,
    "state": 2
  }
}
```

## Migration Steps

### Step 1: Verify SQLite Database
```bash
python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('/tmp/infrafabric-sqlite/infrafabric_knowledge.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM components")
count = cursor.fetchone()[0]
print(f"Components in database: {count}")

cursor.execute("SELECT name FROM components ORDER BY name")
for (name,) in cursor.fetchall():
    print(f"  - {name}")
conn.close()
EOF
```

Expected output: 15 components listed

### Step 2: Generate Migration Report (No Credentials Required)
```bash
python3 tools/redis_migration_simulation.py \
  --sqlite-db /tmp/infrafabric-sqlite/infrafabric_knowledge.db \
  --output-file migration_report.json
```

This validates the data structure without requiring Redis credentials.

### Step 3: Obtain Redis Cloud Credentials
Get the authentication password/token from:
- Redis Cloud console for `redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com`
- Store securely in environment variable or pass via CLI

### Step 4: Execute Migration
```bash
python3 tools/sqlite_to_redis_migration.py \
  --sqlite-db /tmp/infrafabric-sqlite/infrafabric_knowledge.db \
  --redis-host redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com \
  --redis-port 19956 \
  --redis-password YOUR_PASSWORD \
  --yaml-inventory /home/setup/infrafabric/docs/evidence/IF_COMPONENT_INVENTORY.yaml
```

### Step 5: Verify in Redis
```bash
# Connect to Redis
redis-cli -h redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com -p 19956 -a YOUR_PASSWORD

# Verify all components set
> SMEMBERS if:components:all
1) "IF.ground"
2) "IF.guardian/IF.guard"
...

# Verify component hash
> HGETALL if:component:IF.guard
1) "name"
2) "IF.guard"
3) "status"
4) "vaporware"
...

# Verify category index
> SMEMBERS if:components:category:governance
1) "IF.guardian/IF.guard"
2) "IF.yologuard"
```

## Data Files

### Source Files
- **Component Inventory**: `/home/setup/infrafabric/docs/evidence/IF_COMPONENT_INVENTORY.yaml`
- **SQLite Database**: `/tmp/infrafabric-sqlite/infrafabric_knowledge.db`
- **Migration Report**: `/tmp/redis_migration_report.json` (generated)

### Tool Files
- **Migration Script**: `/home/setup/infrafabric/tools/sqlite_to_redis_migration.py`
- **Simulation Script**: `/home/setup/infrafabric/tools/redis_migration_simulation.py`
- **Config Template**: `/home/setup/infrafabric/tools/redis_migration_config.env.example`
- **This Guide**: `/home/setup/infrafabric/tools/REDIS_MIGRATION_README.md`

## Component Manifest

### Partial Components (Ready for Production)
1. **IF.ground** (Foundations)
   - 8 anti-hallucination principles
   - Source: IF-foundations.md:14-96

2. **IF.search** (Discovery)
   - 8-pass investigative methodology
   - Source: IF-foundations.md:519-855

3. **IF.persona** (General)
   - Bloom pattern characterization
   - Source: IF-foundations.md:909-1034

4. **IF.armour** (General)
   - 4-tier defense specification
   - Source: IF-armour.md:81-383

5. **IF.witness** (General)
   - Meta-validation methodology
   - Source: IF-witness.md:1251-1364

6. **IF.yologuard** (Governance)
   - Production security metrics
   - Source: README.md:127-145

7. **IF.optimise** (General)
   - Token efficiency optimization
   - Source: annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md:1-135

### Vaporware Components (Concept Only)
1. IF.router - Model routing system
2. IF.memory - Distributed state management
3. IF.trace - Immutable audit logging
4. IF.pulse - Health monitoring
5. IF.ceo - Executive decision-making framework
6. IF.vesicle - Biological memory transport
7. IF.kernel - Core system integration
8. IF.guardian/IF.guard - Guardian council governance

## Troubleshooting

### Redis Connection Failed
- Verify host and port are correct
- Check password/authentication token
- Ensure network connectivity to Redis Cloud

### SQLite Database Not Found
- Database created at `/tmp/infrafabric-sqlite/infrafabric_knowledge.db` during initial load
- Verify `/tmp/` has sufficient disk space
- Check file permissions on `/tmp/`

### Missing Components in SQLite
- Run `redis_migration_simulation.py` to validate data structure
- Check YAML inventory source file for syntax errors
- Verify component names match expected format (IF.*)

### Redis Push Failed
- Check error messages in migration output
- Verify database selection (default 0)
- Ensure password is correct
- Check Redis Cloud memory limits
- Review Redis Cloud logs for authentication failures

## Next Steps

1. Obtain Redis Cloud password from infrastructure team
2. Run simulation tool to validate data structure
3. Execute migration during maintenance window
4. Verify keys in Redis using redis-cli
5. Update client applications to query Redis for component data
6. Monitor Redis Cloud metrics for performance
7. Archive SQLite database after successful migration

## Security Notes

- Never commit Redis passwords to git
- Use environment variables for sensitive credentials
- Rotate Redis Cloud passwords regularly
- Monitor Redis Cloud access logs
- Implement read-only access for client applications
- Use Redis Cloud networking restrictions if available
