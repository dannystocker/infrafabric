# InfraFabric Knowledge Base Schema

**Version:** 1.0
**Created:** 2025-11-26
**Purpose:** Complete MySQL database schema for storing and managing InfraFabric components, decisions, rules, and metadata

---

## Overview

This schema provides a comprehensive knowledge base for the InfraFabric project, supporting:

- **IF Components** (e.g., IF.yologuard, IF.guard, IF.optimise)
- **Decisions** with evolution tracking and consensus metadata
- **Rules & Principles** with mandatory enforcement and scope
- **Source Files** with SHA256 deduplication
- **Dependencies** with security tracking
- **Git Configuration** with encrypted credentials
- **Compliance Auditing** across components and rules

## Files in This Directory

### 1. **infrafabric_knowledge_base.sql** (21 KB)
Complete MySQL schema definition with:
- 8 core tables (components, decisions, rules_principles, etc.)
- 2 junction tables (component_decisions, component_rules)
- 3 views (component_summary, decision_lineage, compliance_audit)
- Proper foreign keys, indexes, and constraints
- UTF8MB4 charset for full Unicode support
- Comprehensive comments and usage notes

**Key Tables:**
- `components` - IF.* components with status and category
- `decisions` - Documented decisions with evolution tracking
- `rules_principles` - Rules and governance principles
- `source_files` - Source documents with deduplication
- `dependencies` - External packages and libraries
- `git_config` - Git repository configuration
- `component_decisions` - Many-to-many component→decision links
- `component_rules` - Many-to-many component→rule links

### 2. **sample_data.sql** (13 KB)
Pre-populated sample data for testing and development:
- 8 sample components (IF.yologuard, IF.guard, IF.optimise, etc.)
- 4 sample decisions with dates and consensus levels
- 5 sample rules covering traceability and governance
- Component-decision and component-rule linkages
- Sample dependencies for IF.yologuard
- Sample git configurations
- Verification queries showing data structure

**To load:**
```bash
mysql -u root -p infrafabric_kb < sample_data.sql
```

### 3. **SCHEMA_IMPLEMENTATION_GUIDE.md** (20 KB)
Comprehensive implementation guide covering:

**Setup & Initialization**
- Database creation
- Schema import
- Verification

**Table Reference** (detailed for each table)
- Column definitions
- Purpose and usage
- Common queries with examples

**Insert Examples**
- Add component
- Add decision
- Add rule
- Create relationships
- Add dependency

**Advanced Queries**
- Component impact analysis
- Dependency audit reports
- Decision consensus analysis
- Source file deduplication
- Compliance reporting

**Maintenance Tasks**
- Weekly, monthly, quarterly routines
- Database optimization
- Backup and recovery

**API Integration Example** (Python)
- Connection management
- Component queries
- Compliance checking

**Security & Performance Considerations**
- Encryption best practices
- Full-text search indexes
- Access control

### 4. **QUICK_REFERENCE.md** (11 KB)
Fast lookup guide with:

**Quick Setup**
- 3-command initialization

**Core Tables Quick Reference**
- Table purpose and key columns matrix

**Most Common Queries**
- Component overview
- Active decisions
- Compliance checks
- Decision evolution
- Dependencies

**Insert Quick Reference**
- Templates for common inserts

**Analysis Queries**
- Decision impact
- Consensus metrics
- Rule coverage
- Dependency audit

**JSON Column Queries**
- Searching approvers/dissenters
- Finding applying rules

**Maintenance Tasks**
- Weekly, monthly, quarterly jobs

**Backup & Restore**
- Single-line commands

**Performance & Troubleshooting**
- Common issues and fixes
- Database statistics

---

## Quick Start (3 steps)

### Step 1: Create Database
```bash
mysql -u root -p

CREATE DATABASE infrafabric_kb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE infrafabric_kb;
```

### Step 2: Import Schema
```bash
mysql -u root -p infrafabric_kb < infrafabric_knowledge_base.sql
```

### Step 3: Load Sample Data (optional)
```bash
mysql -u root -p infrafabric_kb < sample_data.sql
```

### Verify
```sql
SHOW TABLES;
SELECT * FROM component_summary;
```

---

## Schema Diagram

```
┌─────────────────┐
│  components     │◄─────────┬──────────────────┐
├─────────────────┤          │                  │
│ id (PK)         │          │                  │
│ name            │          │                  │
│ status          │          │                  │
│ category        │          │                  │
│ version         │          │                  │
└─────────────────┘          │                  │
        │                    │                  │
        │         ┌──────────────────┐   ┌──────────────────┐
        │         │component_decisions│   │component_rules   │
        ├────────►│───────────────────┤   │──────────────────┤
        │         │component_id (FK)  │   │component_id (FK) │
        │         │decision_id (FK)   │   │rule_id (FK)      │
        │         │relationship_type  │   │compliance_status │
        │         └──────────────────┘   └──────────────────┘
        │                  ▲                        ▲
        │                  │                        │
        │        ┌─────────────────┐    ┌──────────────────┐
        │        │   decisions     │    │rules_principles  │
        └───────►│─────────────────┤    │──────────────────┤
                 │id (PK)          │    │id (PK)           │
                 │decision_id      │    │rule_id           │
                 │title            │    │rule_text         │
                 │consensus_level  │    │category          │
                 │is_active        │    │is_mandatory      │
                 └─────────────────┘    └──────────────────┘
                         │
                         │
                 ┌────────────────────┐
                 │    evolutions      │
                 ├────────────────────┤
                 │original_decision_id│
                 │evolved_decision_id │
                 │evolution_type      │
                 │reason              │
                 └────────────────────┘

┌──────────────────┐     ┌───────────────┐     ┌─────────────┐
│  source_files    │     │  dependencies │     │  git_config │
├──────────────────┤     ├───────────────┤     ├─────────────┤
│id (PK)           │     │id (PK)        │     │id (PK)      │
│filename          │     │component_id   │     │component_id │
│sha256_hash       │     │package_name   │     │repository   │
│parse_status      │     │version        │     │local_path   │
│is_duplicate      │     │type (runtime) │     │github_url   │
└──────────────────┘     └───────────────┘     └─────────────┘
```

---

## Key Features

### 1. Comprehensive Component Management
- Track IF.* components with status lifecycle
- Support hierarchical components (parent-child)
- Link to source repositories
- Version tracking

### 2. Decision Evolution
- Store decisions with full metadata
- Track consensus levels and approvers/dissenters
- Support decision supersession and evolution
- Link decisions to components

### 3. Governance & Compliance
- Define mandatory and optional rules
- Track compliance status per component
- Audit trail of compliance checks
- Rule scope management (global/component/agent/session)

### 4. Source File Management
- SHA256-based deduplication detection
- Track parsing status and errors
- Identify duplicate files with canonical versions
- Monitor file parsing completion

### 5. Dependency Tracking
- Track external package dependencies
- Monitor security vulnerabilities
- Version constraint management
- Support multiple package managers (pip, npm, cargo, apt)

### 6. Git Integration
- Store repository URLs (GitHub, Gitea)
- Track branch configuration
- Encrypted credential storage
- Sync metadata (last fetch, last push)

### 7. Built-in Views
- `component_summary` - Quick overview with counts
- `decision_lineage` - Evolution chains
- `compliance_audit` - Compliance status matrix

---

## Common Use Cases

### Use Case 1: Track Component Status
```sql
SELECT name, status, version, updated_at
FROM components
WHERE status = 'implemented'
ORDER BY updated_at DESC;
```

### Use Case 2: Audit Compliance
```sql
SELECT * FROM compliance_audit
WHERE compliance_status IN ('non-compliant', 'unknown')
ORDER BY component;
```

### Use Case 3: Find Decision Impact
```sql
SELECT d.decision_id, d.title, COUNT(cd.component_id) as affected
FROM decisions d
LEFT JOIN component_decisions cd ON d.id = cd.decision_id
WHERE d.is_active = TRUE
GROUP BY d.id
ORDER BY affected DESC;
```

### Use Case 4: Deduplication Report
```sql
SELECT canonical.filename as main_file, COUNT(*) as copies
FROM source_files sf
JOIN source_files canonical ON sf.canonical_file_id = canonical.id
WHERE sf.is_duplicate = TRUE
GROUP BY sf.canonical_file_id
ORDER BY copies DESC;
```

### Use Case 5: Dependency Security Check
```sql
SELECT c.name, d.package_name, d.known_vulnerabilities
FROM dependencies d
JOIN components c ON d.component_id = c.id
WHERE d.known_vulnerabilities > 0
ORDER BY d.known_vulnerabilities DESC;
```

---

## Important Notes

### Encryption
Credentials in `git_config` use encrypted fields:
- `github_token_encrypted`
- `gitea_password_encrypted`

Always encrypt/decrypt at application level. Never log credentials.

### JSON Columns
Several columns use JSON for flexibility:
- `decisions.approvers` - Array of approving agents
- `decisions.dissenters` - Array of dissenting agents
- `rules_principles.applies_to` - Array of components

Example queries:
```sql
SELECT * FROM decisions WHERE JSON_CONTAINS(approvers, '"IF.guard"');
SELECT * FROM rules_principles WHERE JSON_CONTAINS(applies_to, '"IF.yologuard"');
```

### Character Set
All tables use `utf8mb4_unicode_ci` to support full Unicode including:
- Emojis
- Non-Latin scripts
- Special symbols

### Timestamps
All tables include:
- `created_at` - When record was created
- `updated_at` - Last modification time

Both auto-update on insert/update.

---

## Maintenance

### Weekly
- Update file parsing status
- Mark completed parses as 'parsed'
- Detect new duplicates

### Monthly
- Clean up failed parse records
- Archive superseded decisions
- Check for expired rules

### Quarterly
- Refresh compliance audit checks
- Review repository sync status
- Run full database optimization

See **SCHEMA_IMPLEMENTATION_GUIDE.md** for detailed maintenance scripts.

---

## Performance

### Indexes
Schema includes strategic indexes on:
- Component: category, status, parent
- Decision: active, category, date, superseded_by
- Source File: filename, hash, type, parse status
- Dependencies: security, deprecation
- Git Config: repository name

### Full-Text Search (Optional)
For text search on descriptions/rules, add:
```sql
ALTER TABLE components ADD FULLTEXT INDEX ft_description (description);
ALTER TABLE decisions ADD FULLTEXT INDEX ft_title_text (title, description);
ALTER TABLE rules_principles ADD FULLTEXT INDEX ft_rule_text (rule_text);
```

### Query Optimization
Use `EXPLAIN` to analyze query plans:
```sql
EXPLAIN SELECT * FROM compliance_audit WHERE component = 'IF.yologuard';
```

---

## Backup Strategy

### Full Backup
```bash
mysqldump -u root -p infrafabric_kb > backup-$(date +%Y%m%d-%H%M%S).sql
```

### Restore
```bash
mysql -u root -p infrafabric_kb < backup-20251126-120000.sql
```

### Incremental Backup (binlog)
Enable and monitor MySQL binary logs for point-in-time recovery.

---

## Related Documentation

- `/home/setup/infrafabric/agents.md` - Component documentation
- `/home/setup/infrafabric/docs/IF-URI-SCHEME.md` - Citation URI format
- `/home/setup/infrafabric/COMPONENT-INDEX.md` - Component catalog

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-26 | Initial schema with 8 core tables, 3 views, comprehensive documentation |

---

## Support & Troubleshooting

See **QUICK_REFERENCE.md** for:
- Common queries
- Troubleshooting guide
- Database diagnostics
- Performance tips

See **SCHEMA_IMPLEMENTATION_GUIDE.md** for:
- Detailed table documentation
- Advanced query examples
- Integration patterns
- Security best practices

---

## License

InfraFabric Schema - 2025
Created for the InfraFabric research project

---

**Last Updated:** 2025-11-26
