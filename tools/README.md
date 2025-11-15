# InfraFabric Tools & Utilities

Complete collection of Python tools and utilities for the InfraFabric project, consolidated from various development locations into a single unified directory.

**Date Consolidated:** November 15, 2025
**Total Tools:** 25 Python modules (8,576 lines of code)
**Source:** `/mnt/c/users/setup/downloads/` (primary) and `/mnt/c/users/setup/downloads/infrafabric/` (core modules)

---

## Core InfraFabric Modules

### `__init__.py` (57 lines)
- Package initialization module
- Source: `/mnt/c/users/setup/downloads/infrafabric/__init__.py`
- Purpose: Makes tools directory a Python package

### `guardians.py` (406 lines)
- **IF Guardians: Pluridisciplinary Oversight Panel**
- Implements weighted debate protocol for ethical/technical governance
- Classes: Guardian, GuardianPanel, DebateResult
- Key Feature: Structured deliberation with domain expertise weights
- Philosophy: "The system that coordinates itself can govern itself"
- Source: `/mnt/c/users/setup/downloads/infrafabric/guardians.py`
- Author: InfraFabric Research (Oct 31, 2025)

### `coordination.py` (335 lines)
- **Weighted Coordination Framework**
- Adaptive weighting mechanism (0.0 → 2.0) for multi-agent systems
- Classes: AgentProfile, Agent, WeightedCoordinator
- Core Principle: Failed exploration = 0.0 weight (silent), Success = up to 2.0 weight (amplified)
- Source: `/mnt/c/users/setup/downloads/infrafabric/coordination.py`
- Author: InfraFabric Research (Oct 31, 2025)

### `manifests.py` (132 lines)
- Configuration and manifest management
- Handles InfraFabric system configuration
- Source: `/mnt/c/users/setup/downloads/infrafabric/manifests.py`
- Author: InfraFabric Research (Oct 31, 2025)

### `IF_ARMOUR_SWARM_MULTIPLIER_ANALYSIS.py` (695 lines)
- **Advanced swarm analysis and multiplier calculations**
- Analyzes heterogeneous multi-LLM coordination patterns
- Includes bloom pattern framework for agent classification
- Implements ARMOUR (Adaptive Response Multiplier for Orchestrated Unified Reasoning)
- Source: `/mnt/c/users/setup/downloads/infrafabric/IF-ARMOUR-SWARM-MULTIPLIER-ANALYSIS.py`
- Date: November 6, 2025

---

## Evaluation & Analysis Tools

### `merge_evaluations.py` (333 lines)
- **Evaluation Data Consolidation**
- Merges multiple evaluation result sets into unified datasets
- Supports JSON and CSV formats
- Handles multi-pass evaluation aggregation
- Source: `/mnt/c/users/setup/downloads/merge_evaluations.py`
- Usage: `python merge_evaluations.py <input_dir> <output_file>`

### `infrafabric_cmp_simulation.py` (515 lines)
- **CMP (Coordinated Model Performance) Simulation**
- Models multi-model coordination behavior
- Simulates heterogeneous model interactions
- Includes false positive (FP) reduction analysis
- Source: `/mnt/c/users/setup/downloads/infrafabric_cmp_simulation.py`
- Usage: Run simulations of IF.yologuard consensus patterns

### `multi_pass_learning_coordinator.py` (449 lines)
- **Multi-Pass Learning Framework**
- Coordinates iterative learning across multiple agent passes
- Implements adaptive learning rate scheduling
- Manages cumulative knowledge aggregation
- Source: `/mnt/c/users/setup/downloads/multi_pass_learning_coordinator.py`
- Key Classes: PassConfig, LearningState, MultiPassCoordinator

---

## Guardian & Debate Tools

### `guardian_debate_example.py` (164 lines)
- **Example: Guardian Panel Debate**
- Demonstrates Guardian debate protocol in action
- Shows how to instantiate and run weighted debates
- Example use cases: ethics deliberation, technical governance
- Source: `/mnt/c/users/setup/downloads/examples/guardian_debate_example.py`
- Usage: `python guardian_debate_example.py` (educational)

### `task_classification_committee.py` (499 lines)
- **Task Classification Via Guardian Council**
- Classifies tasks using pluridisciplinary oversight
- Classes: TaskClassifier, CommitteeVoter, ClassificationResult
- Applies guardian debate to task categorization
- Source: `/mnt/c/users/setup/downloads/infrafabric-overnight-documentation/task_classification_committee.py`
- Use Case: Automated task routing and prioritization

### `supreme_court_ethics_debate.py` (496 lines)
- **Supreme Court-Style Ethics Deliberation**
- Implements formal ethics review with dissent tracking
- Classes: EthicsJustice, OpinionWriter, CaseResult
- Supports majority/minority opinions and red lines
- Source: `/mnt/c/users/setup/downloads/infrafabric-overnight-documentation/supreme_court_ethics_debate.py`
- Use Case: AI safety decision documentation

### `adversarial_role_test.py` (532 lines)
- **Adversarial Testing Via Role Play**
- Tests system robustness through adversarial guardian roles
- Classes: AdversaryRole, RolePlayTest, VulnerabilityReport
- Identifies edge cases and failure modes
- Source: `/mnt/c/users/setup/downloads/infrafabric-overnight-documentation/adversarial_role_test.py`
- Use Case: Security and safety validation

---

## YoloGuard Protection & Mode Systems

### `yolo_guard.py` (362 lines)
- **YoloGuard False Positive Reducer**
- Core false positive reduction engine for IF.yologuard
- Implements heterogeneous consensus for safety validation
- Classes: YoloGuardian, ConsensusValidator, FPReport
- Key Achievement: 100× FP reduction (4% → 0.04%)
- Source: `/mnt/c/users/setup/downloads/claude-code-bridge/yolo_guard.py`
- Date: October 27, 2025

### `yolo_mode.py` (482 lines)
- **YoloGuard Operational Mode Manager**
- Manages YoloGuard modes: Conservative, Balanced, Aggressive
- Implements rate limiting and threshold management
- Classes: YoloMode, ModeSwitcher, ThresholdManager
- Provides graceful degradation patterns
- Source: `/mnt/c/users/setup/downloads/claude-code-bridge/yolo_mode.py`
- Date: October 27, 2025

### `yologuard_improvements.py` (126 lines)
- **YoloGuard Enhancement Proposals**
- Documents improvements and optimizations for YoloGuard v2
- Includes performance tuning suggestions
- Source: `/mnt/c/users/setup/downloads/gpt5 - yologuard_improvements.py`
- Use Case: Development roadmap

### `yologuard_v2.py` (385 lines)
- **YoloGuard Version 2 Implementation**
- Enhanced FP reduction with additional model families
- Improved consensus algorithm
- Classes: YoloGuardV2, EnhancedValidator, OptimizedReport
- Source: `/mnt/c/users/setup/downloads/yologuard-codex-test-package/yologuard_v2.py`
- Status: Production-ready variant

---

## Bridge & Security Infrastructure

### `claude_bridge_secure.py` (718 lines)
- **Secure Claude-Code Bridge**
- Implements secure inter-process communication for Claude Code integration
- Classes: SecureBridge, EncryptedChannel, TokenManager
- Features: OAuth token management, request signing, rate limiting
- Cryptography: Ed25519 signing, SHA-256 hashing
- Source: `/mnt/c/users/setup/downloads/claude-code-bridge/claude_bridge_secure.py`
- Date: October 27, 2025

### `bridge_cli.py` (223 lines)
- **Bridge Command-Line Interface**
- CLI tool for managing secure bridge connections
- Commands: connect, send, receive, status, config
- Usage: `python bridge_cli.py --help`
- Source: `/mnt/c/users/setup/downloads/claude-code-bridge/bridge_cli.py`
- Date: October 26, 2025

### `rate_limiter.py` (203 lines)
- **Adaptive Rate Limiting**
- Token bucket implementation for API rate limiting
- Supports multiple rate limit strategies
- Classes: RateLimiter, BurstPolicy, AdaptiveStrategy
- Source: `/mnt/c/users/setup/downloads/claude-code-bridge/rate_limiter.py`
- Date: October 27, 2025

### `test_security.py` (199 lines)
- **Security Testing Suite**
- Validates bridge security mechanisms
- Tests: token validation, signature verification, encryption
- Classes: SecurityTest, AuthTest, CryptoTest
- Usage: `python test_security.py`
- Source: `/mnt/c/users/setup/downloads/claude-code-bridge/test_security.py`
- Date: October 27, 2025

---

## Submission & Publishing Tools

### `arxiv_submit.py` (262 lines)
- **arXiv Programmatic Submission Script**
- Submits InfraFabric Blueprint to arXiv cs.AI
- Classes: ArxivSubmissionAPI
- Features: Authentication, submission creation, compilation, finalization
- Credentials: danny.stocker@gmail.com (dannystocker)
- Source: `/mnt/c/users/setup/downloads/infrafabric/arxiv_submit.py`
- Date: November 6, 2025
- Note: May require OAuth token or web interface fallback

---

## Experimental & Proof-of-Concept Tools

### `real_search_agent_poc.py` (427 lines)
- **Search Agent Proof-of-Concept**
- Implements real-time web search agent with multi-pass learning
- Classes: SearchAgent, QueryProcessor, ResultAggregator
- Features: Query disambiguation, result ranking, iterative refinement
- Source: `/mnt/c/users/setup/downloads/real_search_agent_poc.py`
- Status: POC - functional but not production-ready

### `self_write_cycle.py` (299 lines)
- **Self-Referential Writing Cycle**
- Agent system that writes and evaluates its own output iteratively
- Classes: WriterAgent, EvaluationCycle, OutputValidator
- Features: Document generation, peer review, refinement
- Source: `/mnt/c/users/setup/downloads/self_write_cycle.py`
- Use Case: Automated documentation and report generation

### `run_aligned_test.py` (175 lines)
- **Alignment Testing Runner**
- Executes alignment validation tests on agent outputs
- Classes: AlignmentTester, ComplianceValidator, ReportGenerator
- Features: Criteria specification, evidence collection, reporting
- Source: `/mnt/c/users/setup/downloads/yologuard-codex-test-package/run_aligned_test.py`
- Usage: `python run_aligned_test.py --config test_config.json`

---

## Data Transformation Tools

### `md_table_to_csv.py` (102 lines)
- **Markdown Table to CSV Converter**
- Converts markdown-formatted tables to CSV format
- Handles pipes, escaped characters, headers
- Usage: `python md_table_to_csv.py input.md output.csv`
- Source: `/mnt/c/users/setup/downloads/md-table-to-csv.py`
- Dependencies: pandas (optional, falls back to manual parsing)

---

## Tool Organization by Category

### By Function
- **Guardian & Governance:** guardians.py, coordination.py, guardian_debate_example.py, task_classification_committee.py, supreme_court_ethics_debate.py
- **Safety & Validation:** yolo_guard.py, yolo_mode.py, adversarial_role_test.py, test_security.py
- **Evaluation:** merge_evaluations.py, infrafabric_cmp_simulation.py, multi_pass_learning_coordinator.py
- **Infrastructure:** claude_bridge_secure.py, bridge_cli.py, rate_limiter.py
- **Analysis:** IF_ARMOUR_SWARM_MULTIPLIER_ANALYSIS.py
- **Publishing:** arxiv_submit.py
- **Experimental:** real_search_agent_poc.py, self_write_cycle.py, run_aligned_test.py, yologuard_v2.py, yologuard_improvements.py
- **Utilities:** md_table_to_csv.py, manifests.py

### By Development Status
- **Production-Ready:** guardians.py, coordination.py, yolo_guard.py, yolo_mode.py, claude_bridge_secure.py, rate_limiter.py, merge_evaluations.py
- **Stable (POC+):** task_classification_committee.py, supreme_court_ethics_debate.py, adversarial_role_test.py, infrafabric_cmp_simulation.py, multi_pass_learning_coordinator.py
- **Experimental:** real_search_agent_poc.py, self_write_cycle.py, run_aligned_test.py, yologuard_v2.py

### By Complexity (Lines of Code)
- **Large (500+ lines):** IF_ARMOUR_SWARM_MULTIPLIER_ANALYSIS.py (695), claude_bridge_secure.py (718), supreme_court_ethics_debate.py (496), adversarial_role_test.py (532), infrafabric_cmp_simulation.py (515)
- **Medium (300-499 lines):** yolo_mode.py (482), multi_pass_learning_coordinator.py (449), real_search_agent_poc.py (427), yologuard_v2.py (385), yolo_guard.py (362), coordination.py (335), merge_evaluations.py (333)
- **Small (<300 lines):** Everything else

---

## Quick Reference: Common Usage Patterns

### Running Tests
```bash
# Security validation
python test_security.py

# Alignment testing
python run_aligned_test.py --config test_config.json

# Adversarial testing
python adversarial_role_test.py --mode full
```

### Guardian Debates
```bash
# Example usage
python guardian_debate_example.py

# Task classification
python task_classification_committee.py --input task_queue.json

# Ethics deliberation
python supreme_court_ethics_debate.py --case ai_deployment_decision.yaml
```

### YoloGuard Safety
```bash
# Run FP reduction
python yolo_guard.py --input model_outputs.json

# Mode switching
python yolo_mode.py --mode balanced --threshold 0.95
```

### Data Processing
```bash
# Merge evaluations
python merge_evaluations.py ./evals/ merged_results.json

# Convert markdown tables
python md_table_to_csv.py input.md output.csv
```

### Publishing
```bash
# Submit to arXiv (requires credentials)
python arxiv_submit.py --credentials config.json
```

---

## Dependencies & Requirements

### Core Dependencies
- Python 3.8+
- requests (for HTTP operations)
- dataclasses (standard library, Python 3.7+)
- json (standard library)
- pathlib (standard library)

### Optional Dependencies
- pandas (for advanced CSV operations in md_table_to_csv.py)
- cryptography (for enhanced security features)
- numpy (for advanced numerical analysis)

### No External API Keys Required
All tools are self-contained. Some tools (arxiv_submit.py) reference credentials but include fallbacks.

---

## File Manifest with Consolidation Dates

All files consolidated on **November 15, 2025**

| Tool | Lines | Size | Original Source | Date |
|------|-------|------|-----------------|------|
| __init__.py | 57 | 1.9K | downloads/infrafabric | Oct 31 |
| guardians.py | 406 | 14K | downloads/infrafabric | Oct 31 |
| coordination.py | 335 | 11K | downloads/infrafabric | Oct 31 |
| manifests.py | 132 | 3.9K | downloads/infrafabric | Oct 31 |
| IF_ARMOUR_SWARM_MULTIPLIER_ANALYSIS.py | 695 | 26K | downloads/infrafabric | Nov 6 |
| merge_evaluations.py | 333 | 13K | downloads/ | - |
| infrafabric_cmp_simulation.py | 515 | 20K | downloads/ | - |
| multi_pass_learning_coordinator.py | 449 | 17K | downloads/ | - |
| guardian_debate_example.py | 164 | 5.2K | downloads/examples | - |
| task_classification_committee.py | 499 | 16K | downloads/infrafabric-overnight-doc | - |
| supreme_court_ethics_debate.py | 496 | 20K | downloads/infrafabric-overnight-doc | - |
| adversarial_role_test.py | 532 | - | downloads/infrafabric-overnight-doc | - |
| yolo_guard.py | 362 | 11K | downloads/claude-code-bridge | Oct 27 |
| yolo_mode.py | 482 | 17K | downloads/claude-code-bridge | Oct 27 |
| yologuard_improvements.py | 126 | 4.1K | downloads/ | - |
| yologuard_v2.py | 385 | 16K | downloads/yologuard-codex-test-package | - |
| claude_bridge_secure.py | 718 | 27K | downloads/claude-code-bridge | Oct 27 |
| bridge_cli.py | 223 | 7.2K | downloads/claude-code-bridge | Oct 26 |
| rate_limiter.py | 203 | 6.7K | downloads/claude-code-bridge | Oct 27 |
| test_security.py | 199 | 5.3K | downloads/claude-code-bridge | Oct 27 |
| arxiv_submit.py | 262 | 9.9K | downloads/infrafabric | Nov 6 |
| real_search_agent_poc.py | 427 | 15K | downloads/ | - |
| self_write_cycle.py | 299 | 11K | downloads/ | - |
| run_aligned_test.py | 175 | 5.5K | downloads/yologuard-codex-test-package | - |
| md_table_to_csv.py | 102 | 2.9K | downloads/ | - |

**Total:** 25 tools, 8,576 lines of code, ~276 KB

---

## Notes on Consolidation

### Name Changes
- `IF-ARMOUR-SWARM-MULTIPLIER-ANALYSIS.py` → `IF_ARMOUR_SWARM_MULTIPLIER_ANALYSIS.py` (for import compatibility)
- `gpt5 - yologuard_improvements.py` → `yologuard_improvements.py` (removed spaces)
- `md-table-to-csv.py` → `md_table_to_csv.py` (for import compatibility)

### Duplicates Detected & Handled
- `bridge_cli.py` (also in `/mnt/c/users/setup/downloads/` root) - kept single copy from claude-code-bridge/
- `claude_bridge_secure.py` - same, kept from claude-code-bridge/
- `demo_standalone.py` - not included (utility demo)
- `test_bridge.py` - not included (testing demo)
- `yolo_mode.py` - consolidated

### Files Not Included (Reasons)
- `ai_studio_code.py` variants - not InfraFabric-specific
- `api_audit_integration.py` - external dependency project
- Virtual environment packages - excluded by design
- Node modules - not Python

---

## Integration Points

### With InfraFabric Core
- `guardians.py` → Used by guardian panel orchestration
- `coordination.py` → Used by multi-agent systems
- `IF_ARMOUR_SWARM_MULTIPLIER_ANALYSIS.py` → Analysis of swarm patterns
- `manifests.py` → Configuration management

### With YoloGuard (digital-lab.ca MCP server)
- `yolo_guard.py` → Core FP reduction
- `yolo_mode.py` → Mode management
- `yologuard_v2.py` → Enhanced version
- `rate_limiter.py` → Request throttling

### With Publishing Pipelines
- `arxiv_submit.py` → arXiv submission
- `merge_evaluations.py` → Result aggregation
- `md_table_to_csv.py` → Documentation conversion

---

## Maintenance Notes

### Last Updated
- **Date:** November 15, 2025
- **Source Check:** All files verified to exist and copy successfully
- **Line Count:** 8,576 total (verified)
- **Size:** ~276 KB consolidated

### Recommendations
1. **Version Control:** Consider git tagging stable tools
2. **Documentation:** Add docstring examples to each major class
3. **Testing:** Create pytest suite for critical path tools
4. **Performance:** Profile evaluation tools on large datasets
5. **Security:** Audit credentials handling in arxiv_submit.py

### Future Consolidation
Monitor these locations for new tools:
- `/mnt/c/users/setup/downloads/`
- `/mnt/c/users/setup/downloads/infrafabric/`
- `/mnt/c/users/setup/downloads/claude-code-bridge/`
- `infrafabric-core` repository for research code

---

## Contact & Attribution

**Original Development:** InfraFabric Research Team
**Consolidation Date:** November 15, 2025
**Consolidation Location:** `/home/setup/infrafabric/tools/`
**Primary Contributor:** Danny Stocker (danny.stocker@gmail.com)

For detailed implementation notes, see individual file docstrings.
