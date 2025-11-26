# InfraFabric Knowledge Base Schema - Implementation Guide

**Version:** 1.0
**Created:** 2025-11-26
**Last Updated:** 2025-11-26

---

## Quick Start

### 1. Create Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE infrafabric_kb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE infrafabric_kb;
```

### 2. Import Schema

```bash
mysql -u root -p infrafabric_kb < schema/infrafabric_knowledge_base.sql
```

### 3. Verify Installation

```sql
-- Check all tables created
SHOW TABLES;

-- Verify views
SHOW FULL TABLES WHERE Table_Type = 'VIEW';

-- Check table structure
DESC components;
DESC decisions;
```

---

## Table Reference

### Core Tables

#### 1. **components**
Stores IF.* components and research elements.

**Key Columns:**
- `id` - Primary identifier
- `name` - Component name (e.g., "IF.yologuard")
- `status` - Lifecycle (implemented, partial, vaporware, deprecated)
- `category` - Classification (production, research, utility, framework)
- `version` - Semantic version
- `parent_component_id` - For hierarchical relationships

**Common Queries:**

```sql
-- Get all production components
SELECT * FROM components
WHERE status = 'implemented' AND category = 'production'
ORDER BY updated_at DESC;

-- Get component with its dependencies
SELECT c.*, COUNT(d.id) as dep_count
FROM components c
LEFT JOIN dependencies d ON c.id = d.component_id
WHERE c.slug = 'if-yologuard'
GROUP BY c.id;

-- Find components by parent
SELECT * FROM components
WHERE parent_component_id = (SELECT id FROM components WHERE name = 'IF.guard');
```

---

#### 2. **decisions**
Documents decisions with evolution tracking and consensus metadata.

**Key Columns:**
- `decision_id` - Unique identifier (DECISION-2025-001)
- `title`, `description` - Decision content
- `category` - Classification
- `consensus_level` - 0-100% agreement
- `decision_date`, `effective_date` - Timeline
- `superseded_by_id` - Points to evolved decision
- `is_active` - Current status
- `approvers`, `dissenters` - JSON arrays of agents

**Common Queries:**

```sql
-- Get all active decisions
SELECT * FROM decisions
WHERE is_active = TRUE
ORDER BY decision_date DESC;

-- Get decisions by category with approval status
SELECT
  decision_id, title, category, consensus_level,
  JSON_LENGTH(approvers) as approver_count,
  JSON_LENGTH(dissenters) as dissenter_count
FROM decisions
WHERE category = 'methodology'
ORDER BY consensus_level DESC;

-- Find decisions approved by specific agent
SELECT * FROM decisions
WHERE JSON_CONTAINS(approvers, '"IF.guard"')
  AND is_active = TRUE;

-- Get decision evolution chain
SELECT * FROM decision_lineage
WHERE original_decision_id = 5;
```

---

#### 3. **source_files**
Tracks source files with content hash and parsing metadata.

**Key Columns:**
- `filename` - Relative path
- `file_path` - Absolute path
- `sha256_hash` - For deduplication
- `last_parsed` - When parsed
- `parse_status` - pending, in_progress, parsed, failed
- `is_duplicate` - Duplicate flag
- `canonical_file_id` - Points to main version

**Common Queries:**

```sql
-- Find duplicate files
SELECT
  sf.id, sf.filename, sf.file_size, sf.sha256_hash,
  COUNT(*) as copy_count
FROM source_files sf
WHERE is_duplicate = TRUE
GROUP BY sha256_hash
ORDER BY copy_count DESC;

-- Get files pending parse
SELECT * FROM source_files
WHERE parse_status = 'pending'
ORDER BY created_at ASC
LIMIT 10;

-- Find canonical file for a duplicate
SELECT canonical.filename
FROM source_files sf
JOIN source_files canonical ON sf.canonical_file_id = canonical.id
WHERE sf.filename = 'docs/infrafabric-complete-v7.01.md';

-- Get recently updated files
SELECT * FROM source_files
WHERE updated_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY updated_at DESC;
```

---

#### 4. **rules_principles**
Rules and principles governing InfraFabric operations.

**Key Columns:**
- `rule_id` - Unique identifier
- `name`, `rule_text` - Content
- `category` - Classification
- `applies_to` - JSON array of components
- `is_mandatory` - Enforcement flag
- `scope` - global, component, agent, session
- `related_decision_id` - Links to decision

**Common Queries:**

```sql
-- Get all mandatory rules
SELECT rule_id, name, category, scope
FROM rules_principles
WHERE is_mandatory = TRUE
ORDER BY category, priority DESC;

-- Get rules for specific component
SELECT rp.*
FROM rules_principles rp
WHERE JSON_CONTAINS(applies_to, '"IF.yologuard"')
  AND is_mandatory = TRUE;

-- Get active rules by priority
SELECT rule_id, name, category, enforcement_mechanism
FROM rules_principles
WHERE sunset_date IS NULL OR sunset_date > NOW()
ORDER BY
  CASE WHEN priority = 'critical' THEN 1
       WHEN priority = 'high' THEN 2
       WHEN priority = 'medium' THEN 3
       ELSE 4 END,
  category;

-- Rules by decision
SELECT rp.rule_id, rp.name, d.decision_id, d.title
FROM rules_principles rp
JOIN decisions d ON rp.related_decision_id = d.id
WHERE d.category = 'methodology';
```

---

#### 5. **dependencies**
External package and library dependencies.

**Key Columns:**
- `component_id` - Which component needs this
- `package_name` - Package identifier
- `version_constraint` - Version spec
- `dependency_type` - runtime, dev, peer, optional
- `package_manager` - pip, npm, cargo, apt, etc.
- `known_vulnerabilities` - Security flag
- `is_deprecated` - Lifecycle flag

**Common Queries:**

```sql
-- Get all dependencies for a component
SELECT package_name, version_constraint, dependency_type, package_manager
FROM dependencies
WHERE component_id = (SELECT id FROM components WHERE name = 'IF.yologuard')
ORDER BY dependency_type, package_name;

-- Find deprecated dependencies
SELECT c.name, d.package_name, d.current_version
FROM dependencies d
JOIN components c ON d.component_id = c.id
WHERE is_deprecated = TRUE;

-- Find dependencies with known vulnerabilities
SELECT c.name, d.package_name, d.known_vulnerabilities
FROM dependencies d
JOIN components c ON d.component_id = c.id
WHERE d.known_vulnerabilities > 0
ORDER BY d.known_vulnerabilities DESC;

-- Get all dev dependencies
SELECT c.name, d.package_name
FROM dependencies d
JOIN components c ON d.component_id = c.id
WHERE d.dependency_type = 'dev'
ORDER BY c.name, d.package_name;
```

---

#### 6. **git_config**
Git repository configuration with encrypted credentials.

**Key Columns:**
- `component_id` - Associated component
- `repository_name` - Repo identifier
- `local_path` - Absolute local path
- `github_url`, `gitea_url` - Repository URLs
- `*_encrypted` - AES-256 encrypted fields
- `main_branch`, `develop_branch` - Branch config

**Important Notes:**
- Never log credentials in plaintext
- Encrypt/decrypt at application level
- Example: `AES_ENCRYPT(token, key_material)`

**Common Queries:**

```sql
-- Get all repository configurations
SELECT component_id, repository_name, local_path, main_branch
FROM git_config
ORDER BY repository_name;

-- Get repo for specific component (without decrypting credentials)
SELECT repository_name, local_path, github_url, main_branch
FROM git_config
WHERE component_id = (SELECT id FROM components WHERE name = 'IF.yologuard');

-- Find repos not synced recently
SELECT repository_name, last_fetch, last_push
FROM git_config
WHERE last_fetch < DATE_SUB(NOW(), INTERVAL 1 DAY)
ORDER BY last_fetch;

-- Decrypt token (application must provide key)
-- SELECT AES_DECRYPT(github_token_encrypted, 'your-key-material')
-- FROM git_config WHERE repository_name = 'infrafabric';
```

---

### Junction Tables

#### 7. **component_decisions**
Links components to decisions (many-to-many).

**Relationship Types:**
- `establishes` - Decision creates/establishes component
- `references` - Decision mentions component
- `implements` - Component implements decision
- `violates` - Component violates decision
- `evolves` - Component evolves decision

**Common Queries:**

```sql
-- Get all decisions for a component
SELECT d.decision_id, d.title, d.category, cd.relationship_type
FROM component_decisions cd
JOIN decisions d ON cd.decision_id = d.id
JOIN components c ON cd.component_id = c.id
WHERE c.name = 'IF.yologuard'
ORDER BY d.decision_date DESC;

-- Get components affected by a decision
SELECT c.name, c.status, cd.relationship_type
FROM component_decisions cd
JOIN components c ON cd.component_id = c.id
WHERE cd.decision_id = (SELECT id FROM decisions WHERE decision_id = 'DECISION-2025-001')
ORDER BY c.name;

-- Find implementation gaps
SELECT c.name, COUNT(*) as referenced_but_not_implemented
FROM component_decisions cd
JOIN components c ON cd.component_id = c.id
WHERE cd.relationship_type = 'references'
  AND c.id NOT IN (
    SELECT component_id FROM component_decisions
    WHERE relationship_type = 'implements'
  )
GROUP BY c.id, c.name;
```

---

#### 8. **component_rules**
Links components to rules and tracks compliance.

**Compliance Status:**
- `compliant` - Meets all requirements
- `non-compliant` - Violates rule
- `partial` - Partially implements
- `unknown` - Not yet verified

**Common Queries:**

```sql
-- Compliance audit for all components
SELECT * FROM compliance_audit
WHERE compliance_status IN ('non-compliant', 'unknown')
ORDER BY component, rule_id;

-- Get non-compliant components
SELECT component, rule_name, compliance_status
FROM compliance_audit
WHERE compliance_status = 'non-compliant'
ORDER BY component;

-- Components with unknown compliance
SELECT DISTINCT component FROM compliance_audit
WHERE compliance_status = 'unknown'
ORDER BY component;

-- Verify compliance for specific component
SELECT rule_name, rule_category, compliance_status, last_checked
FROM compliance_audit
WHERE component = 'IF.yologuard'
ORDER BY rule_category, rule_name;
```

---

### Views

#### 9. **component_summary**
Quick overview of components with counts.

```sql
SELECT * FROM component_summary
WHERE status = 'implemented'
ORDER BY decision_count DESC;

-- Find components with most decisions
SELECT name, category, decision_count, rule_count
FROM component_summary
ORDER BY decision_count DESC
LIMIT 10;
```

---

#### 10. **decision_lineage**
Evolution chain of decisions.

```sql
SELECT * FROM decision_lineage
WHERE original_decision_id = 5;

-- Show evolution reasons
SELECT
  original_decision_id,
  evolved_decision_id,
  evolution_type,
  evolution_date,
  reason
FROM decision_lineage
ORDER BY evolution_date ASC;
```

---

#### 11. **compliance_audit**
Audit component compliance with rules.

```sql
SELECT * FROM compliance_audit
WHERE compliance_status != 'compliant'
ORDER BY component, last_checked;
```

---

## Insert Examples

### Add a Component

```sql
INSERT INTO components (name, slug, description, category, status, version, language)
VALUES (
  'IF.yologuard',
  'if-yologuard',
  'Advanced false-positive reduction system for AI safety with 100× improvement',
  'production',
  'implemented',
  '1.0.0',
  'Python'
);
```

### Add a Decision

```sql
INSERT INTO decisions (
  decision_id, title, description, category, priority,
  consensus_level, decision_date, proposer
) VALUES (
  'DECISION-2025-001',
  'Adopt IF.TTT Framework',
  'Implement Traceable, Transparent, Trustworthy framework across all components',
  'architecture',
  'critical',
  100,
  '2025-11-10',
  'IF.guard'
);
```

### Add a Rule

```sql
INSERT INTO rules_principles (
  rule_id, name, rule_text, category, is_mandatory, scope
) VALUES (
  'RULE-IF.TTT-001',
  'Citation Requirement',
  'All research findings must be linked to observable sources with if://citation/ URIs',
  'traceability',
  TRUE,
  'global'
);
```

### Link Component to Decision

```sql
INSERT INTO component_decisions (
  component_id, decision_id, relationship_type, notes
) SELECT
  c.id, d.id, 'implements',
  'IF.yologuard implements the consensus-based decision framework'
FROM components c, decisions d
WHERE c.name = 'IF.yologuard' AND d.decision_id = 'DECISION-2025-001';
```

### Add Dependency

```sql
INSERT INTO dependencies (
  component_id, package_name, version_constraint,
  dependency_type, package_manager
) SELECT
  id, 'numpy', '>=1.20.0,<2.0.0', 'runtime', 'pip'
FROM components WHERE name = 'IF.yologuard';
```

### Add Git Configuration

```sql
INSERT INTO git_config (
  component_id, repository_name, local_path, github_url,
  gitea_url, main_branch, clone_url_preference
) SELECT
  id,
  'infrafabric-core',
  '/home/setup/infrafabric-core',
  'https://github.com/dannystocker/infrafabric-core.git',
  'http://localhost:4000/dannystocker/infrafabric-core.git',
  'main',
  'https'
FROM components WHERE name = 'IF.core';
```

---

## Advanced Queries

### Component Impact Analysis

```sql
-- Show which decisions affect which components
SELECT
  d.decision_id,
  d.title,
  COUNT(DISTINCT cd.component_id) as affected_components,
  GROUP_CONCAT(DISTINCT c.name) as components
FROM decisions d
LEFT JOIN component_decisions cd ON d.id = cd.decision_id
LEFT JOIN components c ON cd.component_id = c.id
WHERE d.is_active = TRUE
GROUP BY d.id, d.decision_id, d.title
ORDER BY affected_components DESC;
```

### Dependency Audit Report

```sql
-- All dependencies with security status
SELECT
  c.name as component,
  d.package_name,
  d.version_constraint,
  d.current_version,
  d.latest_version,
  d.known_vulnerabilities,
  d.is_deprecated,
  d.dependency_type
FROM dependencies d
JOIN components c ON d.component_id = c.id
WHERE d.known_vulnerabilities > 0
   OR d.is_deprecated = TRUE
ORDER BY c.name, d.known_vulnerabilities DESC;
```

### Decision Consensus Analysis

```sql
-- Decision approval metrics
SELECT
  category,
  COUNT(*) as total_decisions,
  AVG(consensus_level) as avg_consensus,
  SUM(CASE WHEN consensus_level >= 95 THEN 1 ELSE 0 END) as high_consensus,
  SUM(CASE WHEN consensus_level < 50 THEN 1 ELSE 0 END) as contentious
FROM decisions
WHERE is_active = TRUE
GROUP BY category
ORDER BY category;
```

### Source File Deduplication Report

```sql
-- Find and consolidate duplicates
SELECT
  canonical.filename as canonical_version,
  COUNT(*) as total_copies,
  SUM(sf.file_size) as total_size,
  GROUP_CONCAT(sf.filename SEPARATOR ', ') as duplicate_files
FROM source_files sf
LEFT JOIN source_files canonical ON sf.canonical_file_id = canonical.id
WHERE sf.is_duplicate = TRUE
GROUP BY sf.canonical_file_id
ORDER BY total_size DESC;
```

### Compliance Status Report

```sql
-- What's the compliance status?
SELECT
  component,
  SUM(CASE WHEN compliance_status = 'compliant' THEN 1 ELSE 0 END) as compliant,
  SUM(CASE WHEN compliance_status = 'non-compliant' THEN 1 ELSE 0 END) as non_compliant,
  SUM(CASE WHEN compliance_status = 'partial' THEN 1 ELSE 0 END) as partial,
  SUM(CASE WHEN compliance_status = 'unknown' THEN 1 ELSE 0 END) as unknown,
  COUNT(*) as total_rules
FROM compliance_audit
GROUP BY component
ORDER BY
  (CAST(non_compliant AS DECIMAL) / COUNT(*)) DESC,
  component;
```

---

## Maintenance Tasks

### Weekly

```sql
-- Update parsed file stats
UPDATE source_files
SET last_parsed = NOW(), parse_status = 'parsed'
WHERE parse_status = 'in_progress'
  AND updated_at < DATE_SUB(NOW(), INTERVAL 1 HOUR);

-- Mark stale duplicates for review
UPDATE source_files
SET is_duplicate = TRUE
WHERE id IN (
  SELECT id FROM (
    SELECT sf.id
    FROM source_files sf
    GROUP BY sf.sha256_hash
    HAVING COUNT(*) > 1
  ) t
);
```

### Monthly

```sql
-- Cleanup failed parse records
DELETE FROM source_files
WHERE parse_status = 'failed'
  AND updated_at < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- Archive superseded decisions
UPDATE decisions
SET is_active = FALSE
WHERE id IN (
  SELECT original_decision_id FROM evolutions
  WHERE evolution_date < DATE_SUB(NOW(), INTERVAL 30 DAY)
);

-- Check for expired rules
SELECT rule_id, name, sunset_date
FROM rules_principles
WHERE sunset_date < NOW() AND sunset_date IS NOT NULL;
```

### Quarterly

```sql
-- Refresh compliance audit
UPDATE component_rules
SET last_checked = NOW(), compliance_status = 'unknown'
WHERE compliance_status != 'unknown';

-- Review repository sync status
SELECT repository_name, last_fetch, last_push
FROM git_config
WHERE last_fetch < DATE_SUB(NOW(), INTERVAL 7 DAY);
```

---

## Backup & Recovery

### Full Backup

```bash
mysqldump -u root -p infrafabric_kb > backup-$(date +%Y%m%d-%H%M%S).sql
```

### Restore from Backup

```bash
mysql -u root -p infrafabric_kb < backup-20251126-120000.sql
```

### Backup Specific Tables

```bash
mysqldump -u root -p infrafabric_kb decisions decisions_evolutions > decisions-backup.sql
```

---

## Performance Optimization

### Add Full-Text Indexes (if searching text frequently)

```sql
ALTER TABLE components ADD FULLTEXT INDEX ft_description (description);
ALTER TABLE decisions ADD FULLTEXT INDEX ft_title_text (title, description);
ALTER TABLE rules_principles ADD FULLTEXT INDEX ft_rule_text (rule_text);

-- Search example:
SELECT * FROM decisions
WHERE MATCH(title, description) AGAINST('consensus' IN BOOLEAN MODE)
LIMIT 10;
```

### Add Audit Trail (optional)

```sql
CREATE TABLE audit_log (
  id INT PRIMARY KEY AUTO_INCREMENT,
  table_name VARCHAR(50),
  record_id INT,
  action VARCHAR(10),
  old_value JSON,
  new_value JSON,
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  changed_by VARCHAR(255),
  INDEX idx_table_record (table_name, record_id),
  INDEX idx_changed_at (changed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## API Integration Example (Python)

```python
import mysql.connector
from datetime import datetime
import json

class InfraFabricKB:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def add_component(self, name, slug, description, category, status):
        query = """
        INSERT INTO components (name, slug, description, category, status)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (name, slug, description, category, status))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_component_summary(self):
        self.cursor.execute("SELECT * FROM component_summary ORDER BY decision_count DESC")
        return self.cursor.fetchall()

    def check_compliance(self, component_name):
        query = """
        SELECT rule_name, compliance_status FROM compliance_audit
        WHERE component = %s
        """
        self.cursor.execute(query, (component_name,))
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

# Usage
kb = InfraFabricKB('localhost', 'root', 'password', 'infrafabric_kb')
components = kb.get_component_summary()
for comp in components:
    print(f"{comp['name']}: {comp['decision_count']} decisions")
kb.close()
```

---

## Security Considerations

1. **Encrypted Credentials**: Always encrypt `github_token_encrypted` and `gitea_password_encrypted` at application level
2. **Access Control**: Restrict direct database access; use application APIs
3. **Audit Logging**: Track all modifications to critical tables
4. **Backup Security**: Store backups encrypted and offsite
5. **SQL Injection**: Use parameterized queries (as shown in examples)
6. **JSON Validation**: Validate JSON data before inserting into JSON columns

---

## Schema Evolution

When adding new columns or tables:

1. Create a migration file: `migrations/001_add_feature.sql`
2. Document the change in this guide
3. Test on development database first
4. Apply to production with backup
5. Update views and dependent code

Example:
```sql
-- migrations/001_add_audit_trail.sql
ALTER TABLE components ADD COLUMN audit_notes TEXT AFTER updated_at;
ALTER TABLE decisions ADD COLUMN audit_trail JSON DEFAULT NULL;
```

---

**End of Implementation Guide**
