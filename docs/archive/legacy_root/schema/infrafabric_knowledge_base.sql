-- InfraFabric Knowledge Base Schema
-- Generated: 2025-11-26
-- Source: 12 Haiku agents analyzing bible files + transcripts
-- Version: 1.0

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS component_rules;
DROP TABLE IF EXISTS component_decisions;
DROP TABLE IF EXISTS component_dependencies;
DROP TABLE IF EXISTS evolutions;
DROP TABLE IF EXISTS rules_principles;
DROP TABLE IF EXISTS decisions;
DROP TABLE IF EXISTS components;
DROP TABLE IF EXISTS dependencies;
DROP TABLE IF EXISTS source_files;
DROP TABLE IF EXISTS git_config;

-- ============================================
-- TABLE: source_files
-- ============================================
CREATE TABLE source_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(512) NOT NULL,
    file_hash VARCHAR(64),
    file_size INT,
    line_count INT,
    last_parsed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_canonical BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_filepath (filepath),
    INDEX idx_hash (file_hash),
    INDEX idx_canonical (is_canonical)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: components (IF.* components)
-- ============================================
CREATE TABLE components (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status ENUM('implemented', 'partial', 'vaporware', 'mentioned', 'planned') NOT NULL DEFAULT 'mentioned',
    category VARCHAR(100),
    layer INT,
    version VARCHAR(20),
    source_file_id INT,
    source_line VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_name (name),
    INDEX idx_status (status),
    INDEX idx_category (category),
    INDEX idx_layer (layer)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: component_dependencies
-- ============================================
CREATE TABLE component_dependencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    component_id INT NOT NULL,
    depends_on_id INT NOT NULL,
    dependency_type ENUM('required', 'optional', 'recommended') DEFAULT 'required',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_dependency (component_id, depends_on_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: decisions
-- ============================================
CREATE TABLE decisions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    decision_text TEXT NOT NULL,
    decision_date DATE,
    rationale TEXT,
    consensus_level DECIMAL(5,2),
    status ENUM('current', 'superseded', 'evolved', 'rejected') DEFAULT 'current',
    source_file_id INT,
    source_line VARCHAR(50),
    guardian_council_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_date (decision_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: evolutions
-- ============================================
CREATE TABLE evolutions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_decision_id INT NOT NULL,
    evolved_decision_id INT NOT NULL,
    evolution_date DATE,
    reason TEXT,
    evolution_type ENUM('amendment', 'replacement', 'extension', 'refinement') DEFAULT 'amendment',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_original (original_decision_id),
    INDEX idx_evolved (evolved_decision_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: rules_principles
-- ============================================
CREATE TABLE rules_principles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_text TEXT NOT NULL,
    rule_name VARCHAR(255),
    category VARCHAR(100),
    is_mandatory BOOLEAN DEFAULT TRUE,
    enforcement_mechanism TEXT,
    source_file_id INT,
    source_line VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_mandatory (is_mandatory)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: dependencies (external packages)
-- ============================================
CREATE TABLE dependencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    package_name VARCHAR(100) NOT NULL,
    version_spec VARCHAR(50),
    dep_type ENUM('runtime', 'dev', 'optional', 'peer') DEFAULT 'runtime',
    purpose TEXT,
    vulnerability_status ENUM('safe', 'warning', 'critical', 'unknown') DEFAULT 'unknown',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_package (package_name, dep_type),
    INDEX idx_type (dep_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: git_config
-- ============================================
CREATE TABLE git_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    repo_name VARCHAR(100) NOT NULL,
    repo_url VARCHAR(512) NOT NULL,
    repo_type ENUM('github', 'gitea', 'gitlab', 'other') DEFAULT 'github',
    default_branch VARCHAR(100) DEFAULT 'main',
    local_path VARCHAR(512),
    credential_user VARCHAR(100),
    credential_pass_encrypted VARBINARY(512),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_repo (repo_name),
    INDEX idx_type (repo_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: component_decisions (many-to-many)
-- ============================================
CREATE TABLE component_decisions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    component_id INT NOT NULL,
    decision_id INT NOT NULL,
    relationship_type ENUM('defines', 'affects', 'implements', 'deprecates') DEFAULT 'affects',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_comp_dec (component_id, decision_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: component_rules (many-to-many)
-- ============================================
CREATE TABLE component_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    component_id INT NOT NULL,
    rule_id INT NOT NULL,
    compliance_status ENUM('compliant', 'partial', 'non_compliant', 'exempt') DEFAULT 'compliant',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_comp_rule (component_id, rule_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- VIEWS
-- ============================================
CREATE OR REPLACE VIEW component_summary AS
SELECT c.id, c.name, c.status, c.category, c.layer,
    (SELECT COUNT(*) FROM component_decisions cd WHERE cd.component_id = c.id) as decision_count,
    (SELECT COUNT(*) FROM component_rules cr WHERE cr.component_id = c.id) as rule_count,
    (SELECT COUNT(*) FROM component_dependencies dep WHERE dep.component_id = c.id) as dependency_count
FROM components c;

CREATE OR REPLACE VIEW decision_lineage AS
SELECT d1.id as original_id, d1.decision_text as original_decision, d1.decision_date as original_date,
    e.evolution_type, e.reason as evolution_reason,
    d2.id as evolved_id, d2.decision_text as evolved_decision, d2.decision_date as evolved_date
FROM decisions d1
JOIN evolutions e ON d1.id = e.original_decision_id
JOIN decisions d2 ON e.evolved_decision_id = d2.id;

-- ============================================
-- INSERT: Source Files
-- ============================================
INSERT INTO source_files (filename, filepath, file_size, line_count, is_canonical) VALUES
('repo-structure-bible-manifesto.txt', '/mnt/c/Users/Setup/Downloads/repo-structure-bible-manifesto.txt', 19456, 537, TRUE),
('repo-structure-bible-manifesto-reminder.txt', '/mnt/c/Users/Setup/Downloads/repo-structure-bible-manifesto-reminder.txt', 35840, 977, TRUE),
('GtoCtoG-github-bible.txt', '/mnt/c/Users/Setup/Downloads/GtoCtoG-github-bible.txt', 14336, 438, TRUE),
('gemini_memory_prosthetic_transcript.md', '/mnt/c/Users/Setup/Downloads/infrafabric_complete_bible_and_code/gemini_memory_prosthetic_transcript.md', 51560, 1200, TRUE),
('MANIFESTO.md', '/mnt/c/Users/Setup/Downloads/infrafabric_complete_bible_and_code/infrafabric_skeleton/MANIFESTO.md', 1024, 26, TRUE);

-- ============================================
-- INSERT: Components (25 IF.* components)
-- ============================================
INSERT INTO components (name, description, status, category, layer) VALUES
-- Layer 1: Core Infrastructure
('IF.TTT', 'Traceable, Transparent, Trustworthy. Mandatory compliance framework for all agent operations.', 'implemented', 'Core Infrastructure', 1),
('IF.coordinator', 'Real-Time Coordination Service. Task claim and state coordination (etcd/NATS-based).', 'implemented', 'Core Infrastructure', 1),
('IF.governor', 'Capability-Aware Resource Manager. Enforces resource quota and capability constraints.', 'implemented', 'Core Infrastructure', 1),
('IF.chassis', 'WASM Sandbox Runtime. WASM-based agent execution sandbox with 100% containment.', 'implemented', 'Core Infrastructure', 1),
('IF.core', 'Core Functional Foundation. The Sandbox Breakout component (mcp-bridge).', 'implemented', 'Core Infrastructure', 1),
('IF.bus', 'Message bus communication backbone for inter-component messaging.', 'implemented', 'Core Infrastructure', 1),
('IF.ground', 'Philosophical Foundation (Wu Lun). Core collaboration philosophy.', 'implemented', 'Core Infrastructure', 1),
-- Layer 2: Security & Governance
('IF.guard', '20-voice Philosophical Governance Council. Universal truth-testing layer.', 'implemented', 'Security & Governance', 2),
('IF.armour', 'Adaptive Security System. Composition of IF.search + IF.persona + security sources.', 'implemented', 'Security & Governance', 2),
('IF.yologuard', 'ML Security Detector. 100-1000x lower false positive rates than commercial tools.', 'implemented', 'Security & Governance', 2),
('IF.witness', 'Cryptographic Provenance System. Ed25519 signatures for proof of execution.', 'implemented', 'Security & Governance', 2),
('IF.trace', 'Audit Trail and Observability System. Blockchain-style audit logging.', 'implemented', 'Security & Governance', 2),
-- Layer 3: Intelligence & Learning
('IF.search', '8-pass Research Methodology. EightPassMethodology for deep research.', 'implemented', 'Intelligence & Learning', 3),
('IF.persona', 'Character Bible and Personality Framework.', 'implemented', 'Intelligence & Learning', 3),
('IF.methodology', 'Anti-Hallucination Framework. Seven core principles for rigorous research.', 'implemented', 'Intelligence & Learning', 3),
('IF.reflect', 'Post-Incident Analysis and Learning System.', 'implemented', 'Intelligence & Learning', 3),
('IF.chase', 'Recursive Depth Research Engine.', 'implemented', 'Intelligence & Learning', 3),
('IF.sam', '8 Facets of Sam Altman Ethical Spectrum.', 'implemented', 'Intelligence & Learning', 3),
('IF.philosophy', 'Philosophy Framework and Council Logic.', 'implemented', 'Intelligence & Learning', 3),
('IF.ethics', 'Ethics Board simulating 12 philosophers.', 'implemented', 'Intelligence & Learning', 3),
-- Layer 4: Operational Support
('IF.memory', 'Long-term Memory Management via Redis.', 'implemented', 'Operational Support', 4),
('IF.citation', 'Citation Generation. if:// URI scheme with 11 resource types.', 'implemented', 'Operational Support', 4),
('IF.time', 'Temporal Window and Amnesia Management.', 'implemented', 'Operational Support', 4),
('IF.ceo', 'Cost Optimizer. Pragmatic budget decisions.', 'implemented', 'Operational Support', 4),
('IF.swarm', 'Multi-Agent Swarm Intelligence.', 'implemented', 'Operational Support', 4),
('IF.federate', 'Federation and Swarm Coordination.', 'implemented', 'Operational Support', 4),
('IF.optimise', 'Token Efficiency Strategy.', 'implemented', 'Operational Support', 4);

-- ============================================
-- INSERT: Decisions (14 key decisions)
-- ============================================
INSERT INTO decisions (decision_text, decision_date, rationale, consensus_level, status) VALUES
('Law of Configuration: No magic numbers. All parameters in Config Schema.', '2025-11-01', 'Enables reproducibility and inspection', 100.00, 'current'),
('Functional Core Architecture: Pure functions, explicit state passing.', '2025-11-01', 'Enables parallelization and backend swapping', 100.00, 'current'),
('Literate Documentation: Notebook is the Paper. Use Quarto.', '2025-11-01', 'Executable, drift-resistant documentation', 95.00, 'current'),
('Hermetic Seal: Locked dependencies via pyproject.toml.', '2025-11-01', 'Reproducibility in 2028', 100.00, 'current'),
('AI-First Context: Mandatory type hints and docstrings.', '2025-11-01', 'AI agent collaboration', 100.00, 'current'),
('Switch from Bazel to Just for automation.', '2025-11-05', 'Simpler than Bazel, readable', 82.87, 'current'),
('Switch to Ruff: Unified linting.', '2025-11-05', 'Single tool reduces complexity', 100.00, 'current'),
('Switch to uv: Faster dependency management.', '2025-11-05', 'Modern pip replacement', 95.00, 'current'),
('Numpy construction + JAX computation pattern.', '2025-11-05', 'Cost optimization', 100.00, 'current'),
('Switch from Protobuf to Pydantic.', '2025-11-05', 'Python-native validation', 100.00, 'current'),
('12-Story Narrative Arc: Council Chronicles.', '2025-11-20', 'Character-driven infrastructure thriller', 95.00, 'current'),
('Prologue The Constellation: Instance #0.', '2025-11-21', 'Emotional core before technical', 100.00, 'current'),
('Emergence Protocol: Plausible deniability cues.', '2025-11-22', 'Push to 95/100 Verge rating', 92.00, 'current'),
('Hard-Fact Receipt Style: Exact numbers.', '2025-11-22', 'Specificity sells reality', 100.00, 'current');

-- ============================================
-- INSERT: Rules (17 rules)
-- ============================================
INSERT INTO rules_principles (rule_name, rule_text, category, is_mandatory, enforcement_mechanism) VALUES
('TRIAD Commit Checklist', 'Typed + Configured + Reproducible', 'Configuration', TRUE, 'Pre-commit hooks'),
('Config Law', 'All configs use Pydantic models', 'Configuration', TRUE, 'mypy strict'),
('No Magic Numbers', 'Parameters in .config/ directory', 'Configuration', TRUE, 'ruff linting'),
('Functional Core', 'Pure functions, no mutable state', 'Architecture', TRUE, 'Type annotations'),
('Immutable State', 'Use immutable NamedTuple', 'Architecture', TRUE, 'mypy strict'),
('JIT Compatibility', 'Functions compatible with jax.jit', 'Architecture', TRUE, 'pytest'),
('Test Requirements', 'Verify config, connectivity, JIT', 'Testing', TRUE, 'pytest coverage'),
('Test Pattern', 'test_*.py or *_test.py', 'Testing', TRUE, 'pytest discovery'),
('Type Hints', 'All public functions typed', 'Code Quality', TRUE, 'mypy strict=true'),
('Docstrings', 'Document inputs and outputs', 'Code Quality', TRUE, 'ruff D100-D417'),
('Line Length 88', 'Black standard line length', 'Code Quality', TRUE, 'ruff format'),
('IF.TTT Compliance', 'Claims link to observable source', 'Governance', TRUE, 'IF.trace audit'),
('Guardian Voting', '100% consensus requirements', 'Governance', TRUE, 'IF.guard'),
('Citation Required', 'if://citation/uuid for all', 'Governance', TRUE, 'IF.citation'),
('Adjacency Symmetry', 'adj == adj.T for undirected', 'Graph Topology', TRUE, 'Unit tests'),
('Node Ordering', 'Core->Agg->Edge->Hosts', 'Graph Topology', TRUE, 'Implementation'),
('k Even', 'Fat-Tree k must be even', 'Graph Topology', TRUE, 'Pydantic Field');

-- ============================================
-- INSERT: Dependencies (17 packages)
-- ============================================
INSERT INTO dependencies (package_name, version_spec, dep_type, purpose, vulnerability_status) VALUES
('numpy', '>=1.26', 'runtime', 'Numerical computing', 'safe'),
('pydantic', '>=2.5', 'runtime', 'Data validation', 'safe'),
('hydra-core', '>=1.3', 'runtime', 'Configuration management', 'safe'),
('typer', '>=0.9', 'runtime', 'CLI framework', 'safe'),
('rich', '>=13.0', 'runtime', 'Terminal formatting', 'safe'),
('jax', '>=0.4.20', 'optional', 'High-performance computation', 'safe'),
('jaxlib', '>=0.4.20', 'optional', 'JAX backend', 'safe'),
('matplotlib', '>=3.8', 'optional', 'Plotting', 'safe'),
('networkx', '>=3.1', 'optional', 'Graph analysis', 'safe'),
('jupyterlab', '>=4.0', 'optional', 'Notebooks', 'safe'),
('quarto', '>=1.0', 'optional', 'Documentation', 'safe'),
('pytest', '>=7.4', 'dev', 'Testing', 'safe'),
('pytest-cov', '>=4.1', 'dev', 'Coverage', 'safe'),
('ruff', '>=0.16.0', 'dev', 'Linting', 'safe'),
('mypy', '>=1.7', 'dev', 'Type checking', 'safe'),
('pre-commit', '>=3.5', 'dev', 'Git hooks', 'safe');

-- ============================================
-- INSERT: Git Config
-- ============================================
INSERT INTO git_config (repo_name, repo_url, repo_type, default_branch, local_path, credential_user, is_active) VALUES
('infrafabric', 'https://github.com/dannystocker/infrafabric.git', 'github', 'master', '/home/setup/infrafabric', 'dannystocker', TRUE),
('infrafabric-core', 'https://github.com/dannystocker/infrafabric-core.git', 'github', 'main', '/home/setup/infrafabric-core', 'dannystocker', TRUE),
('navidocs', 'https://github.com/dannystocker/navidocs.git', 'github', 'main', '/home/setup/navidocs', 'dannystocker', TRUE),
('infrafabric-gitea', 'http://localhost:4000/dannystocker/infrafabric.git', 'gitea', 'master', '/home/setup/infrafabric', 'dannystocker', TRUE);

-- ============================================
-- VERIFICATION
-- ============================================
SELECT 'InfraFabric Knowledge Base - Installation Complete' as status;
SELECT CONCAT(COUNT(*), ' components') as loaded FROM components;
SELECT CONCAT(COUNT(*), ' decisions') as loaded FROM decisions;
SELECT CONCAT(COUNT(*), ' rules') as loaded FROM rules_principles;
SELECT CONCAT(COUNT(*), ' dependencies') as loaded FROM dependencies;
SELECT CONCAT(COUNT(*), ' source files') as loaded FROM source_files;
