# InfraFabric Knowledge Base - Quick Reference

**Last Updated:** 2025-11-26

---

## Setup & Initialization

### Create Database

```bash
mysql -u root -p

CREATE DATABASE infrafabric_kb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE infrafabric_kb;
```

### Import Schema

```bash
mysql -u root -p infrafabric_kb < /home/setup/infrafabric/schema/infrafabric_knowledge_base.sql
```

### Load Sample Data

```bash
mysql -u root -p infrafabric_kb < /home/setup/infrafabric/schema/sample_data.sql
```

---

## Core Tables Reference

| Table | Purpose | Key Columns |
|-------|---------|------------|
| **components** | IF.* components | name, status, category, version |
| **decisions** | Documented decisions | decision_id, title, consensus_level |
| **decisions_evolutions** | Decision lineage | original_decision_id, evolved_decision_id |
| **rules_principles** | Rules & governance | rule_id, category, is_mandatory |
| **source_files** | Source docs & deduplication | filename, sha256_hash, parse_status |
| **dependencies** | External packages | package_name, version_constraint, type |
| **git_config** | Git repos | repository_name, local_path, github_url |
| **component_decisions** | Component→Decision links | relationship_type (implements, references, etc.) |
| **component_rules** | Component→Rule links | compliance_status (compliant, partial, etc.) |

---

## Most Common Queries

### Get Component Overview

```sql
SELECT * FROM component_summary ORDER BY decision_count DESC;
```

### Get All Active Decisions

```sql
SELECT decision_id, title, consensus_level, decision_date
FROM decisions WHERE is_active = TRUE
ORDER BY decision_date DESC;
```

### Check Component Compliance

```sql
SELECT rule_name, rule_category, compliance_status, last_checked
FROM compliance_audit WHERE component = 'IF.yologuard'
ORDER BY rule_category;
```

### Find Decision Evolution Chain

```sql
SELECT * FROM decision_lineage WHERE original_decision_id = 1;
```

### List All Mandatory Rules

```sql
SELECT rule_id, name, category, scope
FROM rules_principles WHERE is_mandatory = TRUE
ORDER BY category;
```

### Get Component Dependencies

```sql
SELECT package_name, version_constraint, dependency_type
FROM dependencies
WHERE component_id = (SELECT id FROM components WHERE name = 'IF.yologuard')
ORDER BY dependency_type, package_name;
```

### Find Duplicate Files

```sql
SELECT canonical.filename as main_file,
       COUNT(*) as copies,
       SUM(sf.file_size) as total_size
FROM source_files sf
JOIN source_files canonical ON sf.canonical_file_id = canonical.id
WHERE sf.is_duplicate = TRUE
GROUP BY sf.canonical_file_id
ORDER BY total_size DESC;
```

### Get Git Repository Info

```sql
SELECT repository_name, local_path, github_url, main_branch
FROM git_config
ORDER BY repository_name;
```

---

## Insert Quick Reference

### Add Component

```sql
INSERT INTO components (name, slug, description, category, status)
VALUES ('IF.component', 'if-component', 'Description', 'category', 'implemented');
```

### Add Decision

```sql
INSERT INTO decisions (decision_id, title, description, category, consensus_level, decision_date, is_active)
VALUES ('DECISION-2025-XXX', 'Title', 'Description', 'category', 100, NOW(), TRUE);
```

### Add Rule

```sql
INSERT INTO rules_principles (rule_id, name, rule_text, category, is_mandatory, scope)
VALUES ('RULE-XXX', 'Name', 'Rule text', 'category', TRUE, 'global');
```

### Link Component to Decision

```sql
INSERT INTO component_decisions (component_id, decision_id, relationship_type)
SELECT c.id, d.id, 'implements'
FROM components c, decisions d
WHERE c.name = 'IF.component' AND d.decision_id = 'DECISION-2025-XXX';
```

---

## Find Commands

### Search by Component Name

```sql
SELECT * FROM components WHERE name LIKE '%search%';
```

### Search by Decision Title

```sql
SELECT decision_id, title FROM decisions
WHERE title LIKE '%keyword%' OR description LIKE '%keyword%';
```

### Find Components by Status

```sql
SELECT name, status, version
FROM components WHERE status = 'implemented'
ORDER BY name;
```

### Find Non-Compliant Components

```sql
SELECT DISTINCT component FROM compliance_audit
WHERE compliance_status = 'non-compliant'
ORDER BY component;
```

### Find Dependencies with Vulnerabilities

```sql
SELECT c.name, d.package_name, d.known_vulnerabilities
FROM dependencies d
JOIN components c ON d.component_id = c.id
WHERE d.known_vulnerabilities > 0
ORDER BY d.known_vulnerabilities DESC;
```

### Find Parsed vs Unparsed Files

```sql
SELECT parse_status, COUNT(*) as count
FROM source_files
GROUP BY parse_status;
```

---

## Update Commands

### Mark Decision as Superseded

```sql
UPDATE decisions SET is_active = FALSE
WHERE decision_id = 'DECISION-2025-XXX';
```

### Update Component Status

```sql
UPDATE components SET status = 'implemented'
WHERE name = 'IF.component';
```

### Update File Parse Status

```sql
UPDATE source_files SET parse_status = 'parsed', last_parsed = NOW()
WHERE filename = 'path/to/file.md';
```

### Update Compliance Status

```sql
UPDATE component_rules
SET compliance_status = 'compliant', last_checked = NOW()
WHERE component_id = 1 AND rule_id = 1;
```

---

## Analysis Queries

### Decision Impact Analysis

```sql
SELECT
  d.decision_id, d.title, d.category,
  COUNT(DISTINCT cd.component_id) as affected_components
FROM decisions d
LEFT JOIN component_decisions cd ON d.id = cd.decision_id
WHERE d.is_active = TRUE
GROUP BY d.id
ORDER BY affected_components DESC;
```

### Decision Consensus Metrics

```sql
SELECT
  category,
  COUNT(*) as decisions,
  ROUND(AVG(consensus_level), 1) as avg_consensus,
  SUM(CASE WHEN consensus_level >= 95 THEN 1 ELSE 0 END) as high_consensus
FROM decisions WHERE is_active = TRUE
GROUP BY category
ORDER BY avg_consensus DESC;
```

### Rule Coverage by Component

```sql
SELECT
  c.name as component,
  COUNT(cr.rule_id) as rules_linked,
  SUM(CASE WHEN cr.compliance_status = 'compliant' THEN 1 ELSE 0 END) as compliant,
  SUM(CASE WHEN cr.compliance_status = 'non-compliant' THEN 1 ELSE 0 END) as non_compliant
FROM components c
LEFT JOIN component_rules cr ON c.id = cr.component_id
WHERE c.status = 'implemented'
GROUP BY c.id, c.name
ORDER BY rules_linked DESC;
```

### Dependency Audit

```sql
SELECT
  c.name, COUNT(d.id) as dep_count,
  SUM(d.known_vulnerabilities) as total_vulns
FROM components c
LEFT JOIN dependencies d ON c.id = d.component_id
GROUP BY c.id, c.name
ORDER BY total_vulns DESC;
```

### Source File Statistics

```sql
SELECT
  file_type,
  COUNT(*) as files,
  ROUND(SUM(file_size) / 1024 / 1024, 2) as total_mb,
  SUM(CASE WHEN is_duplicate = TRUE THEN 1 ELSE 0 END) as duplicates
FROM source_files
GROUP BY file_type
ORDER BY total_mb DESC;
```

---

## JSON Column Queries

### Find Decisions Approved by Specific Agent

```sql
SELECT decision_id, title FROM decisions
WHERE JSON_CONTAINS(approvers, '"IF.guard"')
  AND is_active = TRUE;
```

### Find Rules Applying to Component

```sql
SELECT * FROM rules_principles
WHERE JSON_CONTAINS(applies_to, '"IF.yologuard"')
  AND is_mandatory = TRUE;
```

### Check Dissent on Decision

```sql
SELECT decision_id, title,
       JSON_LENGTH(dissenters) as dissenter_count,
       dissenters as dissent_details
FROM decisions
WHERE JSON_LENGTH(dissenters) > 0;
```

---

## Maintenance Tasks

### Weekly: Update Parse Status

```sql
UPDATE source_files
SET parse_status = 'parsed', last_parsed = NOW()
WHERE parse_status = 'in_progress'
  AND updated_at < DATE_SUB(NOW(), INTERVAL 1 HOUR);
```

### Monthly: Cleanup Failed Parses

```sql
DELETE FROM source_files
WHERE parse_status = 'failed'
  AND updated_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### Quarterly: Refresh Compliance Checks

```sql
UPDATE component_rules
SET last_checked = NOW(), compliance_status = 'unknown';
```

### Check Repository Sync Status

```sql
SELECT repository_name, last_fetch, last_push,
       DATEDIFF(NOW(), last_fetch) as days_since_fetch
FROM git_config
ORDER BY last_fetch;
```

---

## Backup & Restore

### Full Backup

```bash
mysqldump -u root -p infrafabric_kb > backup.sql
```

### Restore

```bash
mysql -u root -p infrafabric_kb < backup.sql
```

### Backup Specific Tables

```bash
mysqldump -u root -p infrafabric_kb decisions evolutions > decisions-backup.sql
```

---

## Performance Tips

### Add Indexes for Frequent Searches

```sql
-- Full-text search on descriptions
ALTER TABLE components ADD FULLTEXT INDEX ft_description (description);
ALTER TABLE decisions ADD FULLTEXT INDEX ft_title_description (title, description);

-- Search example
SELECT * FROM decisions
WHERE MATCH(title, description) AGAINST('consensus' IN BOOLEAN MODE);
```

### Monitor Query Performance

```sql
EXPLAIN SELECT * FROM compliance_audit WHERE component = 'IF.yologuard';
```

### Check Slow Queries

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
-- Then check: /var/log/mysql/slow-query.log
```

---

## Count Examples

### Total Components by Status

```sql
SELECT status, COUNT(*) as count
FROM components
GROUP BY status;
```

### Total Active Rules

```sql
SELECT COUNT(*) FROM rules_principles WHERE is_mandatory = TRUE;
```

### Total Decisions by Consensus

```sql
SELECT
  CASE
    WHEN consensus_level >= 95 THEN 'High (>=95%)'
    WHEN consensus_level >= 80 THEN 'Medium (80-94%)'
    ELSE 'Low (<80%)'
  END as consensus_level,
  COUNT(*) as decisions
FROM decisions WHERE is_active = TRUE
GROUP BY consensus_level;
```

---

## Export Examples

### Export as CSV

```bash
mysql -u root -p infrafabric_kb \
  -e "SELECT * FROM component_summary" \
  --batch | sed 's/\t/,/g' > components.csv
```

### Export Decision Report

```bash
mysql -u root -p infrafabric_kb \
  -e "SELECT decision_id, title, category, consensus_level, decision_date
       FROM decisions WHERE is_active = TRUE
       ORDER BY decision_date DESC" > decisions_report.txt
```

---

## Common Troubleshooting

### Check if Table Exists

```sql
SHOW TABLES LIKE 'components';
```

### Check Table Structure

```sql
DESC components;
SHOW INDEX FROM components;
```

### Find Orphaned Records

```sql
-- Orphaned component_decisions
SELECT cd.* FROM component_decisions cd
LEFT JOIN components c ON cd.component_id = c.id
WHERE c.id IS NULL;

-- Orphaned component_rules
SELECT cr.* FROM component_rules cr
LEFT JOIN components c ON cr.component_id = c.id
WHERE c.id IS NULL;
```

### Reset Auto-Increment

```sql
ALTER TABLE components AUTO_INCREMENT = 1;
```

### Check Database Size

```sql
SELECT
  SUM(data_length + index_length) / 1024 / 1024 as size_mb
FROM information_schema.tables
WHERE table_schema = 'infrafabric_kb';
```

---

## Document Your Changes

When making schema changes:

1. Create migration: `migrations/YYYYMMDD_description.sql`
2. Test on dev database first
3. Record in version history
4. Update this guide

Example migration:
```sql
-- migrations/20251126_add_component_tags.sql
ALTER TABLE components ADD COLUMN tags JSON DEFAULT NULL
  COMMENT 'Array of tags for categorization';
```

---

**End of Quick Reference**
