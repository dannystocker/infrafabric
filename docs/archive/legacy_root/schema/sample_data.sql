-- ============================================================================
-- InfraFabric Knowledge Base - Sample Data
-- ============================================================================
-- This file contains sample data to populate the knowledge base schema
-- Use for development and testing only
--
-- Usage: mysql -u root -p infrafabric_kb < sample_data.sql
-- ============================================================================

-- ============================================================================
-- COMPONENTS
-- ============================================================================

INSERT INTO components (name, slug, description, category, status, version, language, documentation_url)
VALUES
  (
    'IF.yologuard',
    'if-yologuard',
    'Advanced false-positive reduction system for AI safety. 100× improvement in specificity through multi-stage validation pipeline. Production component.',
    'production',
    'implemented',
    '1.0.0',
    'Python',
    'https://github.com/dannystocker/infrafabric/blob/main/IF.yologuard.md'
  ),
  (
    'IF.guard',
    'if-guard',
    'Strategic communications council framework with 20-voice extended board (6 Core Guardians + 3 Western + 3 Eastern Philosophers + 8 IF.sam facets). Stress-tests messages against goals and audience.',
    'framework',
    'partial',
    '2.0.0',
    'Python',
    'https://github.com/dannystocker/infrafabric/blob/main/IF.guard.md'
  ),
  (
    'IF.optimise',
    'if-optimise',
    'Token efficiency strategy framework. 87-90% cost reduction via Haiku agent swarms. Default ON for all complex tasks.',
    'utility',
    'implemented',
    '1.5.0',
    'Python',
    'https://github.com/dannystocker/infrafabric/blob/main/IF.optimise.md'
  ),
  (
    'IF.search',
    'if-search',
    '8-pass investigative methodology for comprehensive research. Epistemological rigor through multi-perspective analysis.',
    'research',
    'partial',
    '1.0.0',
    'Methodology',
    'https://github.com/dannystocker/infrafabric/blob/main/IF.search.md'
  ),
  (
    'IF.ground',
    'if-ground',
    '8 anti-hallucination principles grounded in philosophical database of 12 philosophers. Epistemological framework for trustworthiness.',
    'research',
    'partial',
    '1.0.0',
    'Methodology',
    'https://github.com/dannystocker/infrafabric/blob/main/IF.ground.md'
  ),
  (
    'IF.TTT',
    'if-ttt',
    'Traceable, Transparent, Trustworthy framework. MANDATORY for all agent operations. Core governance principle.',
    'framework',
    'partial',
    '1.0.0',
    'Governance',
    'https://github.com/dannystocker/infrafabric/blob/main/docs/IF-TTT-FRAMEWORK.md'
  ),
  (
    'IF.citate',
    'if-citate',
    'Citation generation system. Produces if://citation/ URIs for all research, decisions, and code changes.',
    'utility',
    'partial',
    '1.0.0',
    'Python',
    'https://github.com/dannystocker/infrafabric/blob/main/docs/IF-CITATE.md'
  ),
  (
    'IF.sam',
    'if-sam',
    'Panel of 8 Sam Altman facets representing ethical spectrum (4 Light Side + 4 Dark Side). Models multifaceted decision-making.',
    'research',
    'vaporware',
    '0.1.0',
    'Conceptual',
    'https://github.com/dannystocker/infrafabric/blob/main/IF.sam.md'
  );

-- ============================================================================
-- SOURCE FILES
-- ============================================================================

INSERT INTO source_files (filename, file_path, sha256_hash, file_type, parse_status, last_parsed)
VALUES
  (
    'agents.md',
    '/home/setup/infrafabric/agents.md',
    'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6',
    'markdown',
    'parsed',
    '2025-11-15 10:30:00'
  ),
  (
    'docs/IF-URI-SCHEME.md',
    '/home/setup/infrafabric/docs/IF-URI-SCHEME.md',
    'b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1',
    'markdown',
    'parsed',
    '2025-11-15 10:30:00'
  ),
  (
    'infrafabric-complete-v7.01.md',
    '/home/setup/infrafabric/infrafabric-complete-v7.01.md',
    'c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2',
    'markdown',
    'parsed',
    '2025-11-15 10:30:00'
  ),
  (
    'schema/infrafabric_knowledge_base.sql',
    '/home/setup/infrafabric/schema/infrafabric_knowledge_base.sql',
    'd4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3',
    'sql',
    'pending',
    NULL
  );

-- ============================================================================
-- DECISIONS
-- ============================================================================

INSERT INTO decisions (decision_id, title, description, category, priority, consensus_level, decision_date, effective_date, is_active, proposer)
VALUES
  (
    'DECISION-2025-001',
    'Adopt IF.TTT Framework Globally',
    'All InfraFabric components must implement Traceable, Transparent, Trustworthy principles. This is a mandatory governance requirement affecting all future development.',
    'governance',
    'critical',
    100,
    '2025-11-10',
    '2025-11-10',
    TRUE,
    'IF.guard'
  ),
  (
    'DECISION-2025-002',
    'Deploy Session Handover System',
    'Implement 3-tier architecture to prevent context exhaustion: (1) SESSION-RESUME.md <2K tokens, (2) COMPONENT-INDEX.md <5K tokens, (3) Deep Archives via Haiku agents only.',
    'architecture',
    'high',
    95,
    '2025-11-10',
    '2025-11-10',
    TRUE,
    'IF.optimise'
  ),
  (
    'DECISION-2025-003',
    'Use Citation System for All Research',
    'All research findings, decisions, and code changes must be linked to observable sources via if://citation/ URIs. IF.citate generates citations by default.',
    'methodology',
    'critical',
    92,
    '2025-11-08',
    '2025-11-08',
    TRUE,
    'IF.ground'
  ),
  (
    'DECISION-2025-004',
    'Consolidate Duplicate Files',
    'Run smart_integrate.sh to consolidate 175 duplicate files across 59 groups. SHA256 content-based deduplication. Recovers 8.31 MB.',
    'maintenance',
    'medium',
    82,
    '2025-11-15',
    NULL,
    FALSE,
    'IF.optimise'
  );

-- ============================================================================
-- EVOLUTIONS
-- ============================================================================

INSERT INTO evolutions (original_decision_id, evolved_decision_id, reason, evolution_type, changed_by, evolution_date, effective_date)
SELECT
  d1.id,
  d2.id,
  'Expanded scope to include Guardian Council consensus metrics and dissent tracking',
  'expansion',
  'IF.guard',
  '2025-11-12',
  '2025-11-12'
FROM decisions d1, decisions d2
WHERE d1.decision_id = 'DECISION-2025-001'
  AND d2.decision_id = 'DECISION-2025-003'
  AND NOT EXISTS (SELECT 1 FROM evolutions WHERE original_decision_id = d1.id);

-- ============================================================================
-- RULES & PRINCIPLES
-- ============================================================================

INSERT INTO rules_principles (rule_id, name, rule_text, category, subcategory, priority, scope, is_mandatory, effective_date)
VALUES
  (
    'RULE-IF.TTT-001',
    'Citation Requirement',
    'All research findings must be linked to observable sources (file:line, git commit, external citation). Generate if://citation/uuid for each finding.',
    'traceability',
    'citation',
    'critical',
    'global',
    TRUE,
    '2025-11-10'
  ),
  (
    'RULE-IF.TTT-002',
    'Decision Documentation',
    'Every decision must document: decision text, date, proposer, approvers, dissenters, consensus level, and reasoning. Store in decisions table with IF.TTT traceability.',
    'transparency',
    'documentation',
    'critical',
    'global',
    TRUE,
    '2025-11-10'
  ),
  (
    'RULE-IF.OPTIMISE-001',
    'Haiku Delegation for Labor',
    'Mechanical tasks (file updates, installations, data transformations, git operations) must be delegated to Haiku agents. Use Sonnet for complex reasoning.',
    'efficiency',
    'token-optimization',
    'high',
    'component',
    TRUE,
    '2025-10-01'
  ),
  (
    'RULE-IF.OPTIMISE-002',
    'No Proactive File Creation',
    'Never create files unless explicitly required. Prefer editing existing files. No unsolicited documentation or README files.',
    'discipline',
    'code-conduct',
    'high',
    'global',
    TRUE,
    '2025-11-01'
  ),
  (
    'RULE-IF.GUARD-001',
    'Extended Council Quorum',
    'Major decisions require approval from IF.guard 20-voice council (6 Core + 3 Western + 3 Eastern + 8 IF.sam facets). Consensus threshold: 80%+ for high-level decisions.',
    'governance',
    'quorum',
    'critical',
    'global',
    TRUE,
    '2025-11-10'
  );

-- ============================================================================
-- COMPONENT_DECISIONS
-- ============================================================================

INSERT INTO component_decisions (component_id, decision_id, relationship_type, notes)
SELECT
  c.id,
  d.id,
  'implements',
  CONCAT('Component ', c.name, ' implements decision ', d.decision_id)
FROM components c, decisions d
WHERE (c.name = 'IF.TTT' AND d.decision_id = 'DECISION-2025-001')
   OR (c.name = 'IF.optimise' AND d.decision_id = 'DECISION-2025-002')
   OR (c.name = 'IF.citate' AND d.decision_id = 'DECISION-2025-003');

-- ============================================================================
-- COMPONENT_RULES
-- ============================================================================

INSERT INTO component_rules (component_id, rule_id, compliance_status, last_checked)
SELECT
  c.id,
  r.id,
  CASE
    WHEN c.status = 'implemented' THEN 'compliant'
    WHEN c.status = 'partial' THEN 'partial'
    ELSE 'unknown'
  END,
  NOW()
FROM components c
CROSS JOIN rules_principles r
WHERE c.status IN ('implemented', 'partial')
  AND r.is_mandatory = TRUE;

-- ============================================================================
-- DEPENDENCIES
-- ============================================================================

INSERT INTO dependencies (component_id, package_name, version_constraint, dependency_type, package_manager, current_version)
SELECT
  c.id,
  'numpy',
  '>=1.20.0,<2.0.0',
  'runtime',
  'pip',
  '1.26.0'
FROM components c WHERE c.name = 'IF.yologuard'
UNION ALL
SELECT
  c.id,
  'pandas',
  '>=1.3.0,<2.0.0',
  'runtime',
  'pip',
  '2.0.0'
FROM components c WHERE c.name = 'IF.yologuard'
UNION ALL
SELECT
  c.id,
  'mysql-connector-python',
  '>=8.0.0',
  'runtime',
  'pip',
  '8.1.0'
FROM components c WHERE c.name = 'IF.yologuard';

-- ============================================================================
-- GIT CONFIG
-- ============================================================================

INSERT INTO git_config (component_id, repository_name, local_path, github_url, gitea_url, main_branch, develop_branch)
SELECT
  c.id,
  'infrafabric-core',
  '/home/setup/infrafabric-core',
  'https://github.com/dannystocker/infrafabric-core.git',
  'http://localhost:4000/dannystocker/infrafabric-core.git',
  'main',
  'develop'
FROM components c WHERE c.name = 'IF.citate'
UNION ALL
SELECT
  c.id,
  'infrafabric',
  '/home/setup/infrafabric',
  'https://github.com/dannystocker/infrafabric.git',
  'http://localhost:4000/dannystocker/infrafabric.git',
  'main',
  'develop'
FROM components c WHERE c.name = 'IF.guard';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Display inserted data summary
SELECT
  'Components' as entity,
  COUNT(*) as count
FROM components
UNION ALL
SELECT 'Decisions', COUNT(*) FROM decisions
UNION ALL
SELECT 'Rules', COUNT(*) FROM rules_principles
UNION ALL
SELECT 'Source Files', COUNT(*) FROM source_files
UNION ALL
SELECT 'Dependencies', COUNT(*) FROM dependencies
UNION ALL
SELECT 'Git Configs', COUNT(*) FROM git_config;

-- Show component summary
SELECT * FROM component_summary;

-- Show active decisions
SELECT decision_id, title, category, consensus_level
FROM decisions
WHERE is_active = TRUE
ORDER BY decision_date DESC;

-- Show compliance status
SELECT
  component,
  SUM(CASE WHEN compliance_status = 'compliant' THEN 1 ELSE 0 END) as compliant,
  SUM(CASE WHEN compliance_status = 'non-compliant' THEN 1 ELSE 0 END) as non_compliant,
  SUM(CASE WHEN compliance_status = 'partial' THEN 1 ELSE 0 END) as partial,
  COUNT(*) as total
FROM compliance_audit
GROUP BY component;

-- ============================================================================
-- END OF SAMPLE DATA
-- ============================================================================
