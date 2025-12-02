# InfraFabric Developer Guide

**Version:** 1.0
**Date:** 2025-11-30
**Citation:** `if://doc/developer-guide/2025-11-30`
**Status:** Complete - Ready for contributor onboarding

---

## Table of Contents

1. [Getting Started (15 min)](#getting-started)
2. [Architecture Overview](#architecture-overview)
3. [Project Structure](#project-structure)
4. [Coding Standards](#coding-standards)
5. [Testing Strategy](#testing-strategy)
6. [Contribution Workflow](#contribution-workflow)
7. [Development Environment Setup](#development-environment-setup)
8. [Common Development Tasks](#common-development-tasks)
9. [Debugging Guide](#debugging-guide)
10. [Release Process](#release-process)

---

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher** - Core development language
- **Redis 6.0+** - Context memory and swarm coordination
- **ChromaDB 0.4+** - Vector database for RAG storage
- **Docker & Docker Compose** - Containerized development environment
- **Git 2.30+** - Version control
- **Node.js 18+** (optional) - For OpenWebUI frontend development

### Quick Start (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/dannystocker/infrafabric.git
cd infrafabric

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Start infrastructure services (Docker)
docker-compose up -d redis chromadb

# 5. Verify installation
python -c "import infrafabric; print('InfraFabric ready!')"
redis-cli PING                    # Should return: PONG
curl http://localhost:8000/api/heartbeat  # Should return 200
```

### Verify Installation (2 minutes)

```bash
# Run health checks
python scripts/health_check.py

# Expected output:
# ✓ Python version: 3.11.x
# ✓ Redis connection: OK (ping response: PONG)
# ✓ ChromaDB connection: OK (heartbeat: 2025-11-30T...)
# ✓ Dependencies installed: 45 packages
# ✓ Configuration loaded: infrafabric.schema.json
```

---

## Architecture Overview

### High-Level System Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      USER INTERFACES                         │
├────────────────────────────────────────────────────────────────┤
│ OpenWebUI (Web)  │  IF.emotion (React)  │  CLI  │  REST API  │
└────────────┬──────────────────────────────────────────────────┘
             │
             ├─────────────────────────────────────────────────┐
             │                                                 │
┌────────────▼──────────────────────────────────────────────────┐
│                   MODEL ROUTING LAYER                         │
├──────────────────────────────────────────────────────────────┤
│  Claude Max (Apex)  │  Claude Sonnet (Frontier)  │ Haiku     │
│  (Reasoning)        │  (Analysis)                │ (Mechanical)
└─────────┬──────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────┐
│           CORE SYSTEM LAYERS                               │
├──────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────┐  │
│ │ Personality Layer (IF.emotion + Sergio DNA)         │  │
│ │ ├─ 23 Rhetorical Devices                           │  │
│ │ ├─ 11 Argumentative Structures                      │  │
│ │ └─ 11 Ethical Principles                           │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ Communication Layer (Redis Bus S2)                   │  │
│ │ ├─ Task distribution (Redis)                        │  │
│ │ ├─ Finding aggregation                              │  │
│ │ └─ Cross-swarm messaging                            │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ Memory Layer                                         │  │
│ │ ├─ L1 Cache: Redis (session state) - 0.071ms       │  │
│ │ └─ L2 Deep: ChromaDB (RAG storage) - 200-300ms     │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ Intelligence Layer                                   │  │
│ │ ├─ IF.guard (20-voice council)                      │  │
│ │ ├─ IF.TTT (Traceable, Transparent, Trustworthy)    │  │
│ │ └─ Audit Trail & Citations                          │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ Resilience Layer                                     │  │
│ │ ├─ Timeout Prevention                               │  │
│ │ ├─ Checkpoint System                                │  │
│ │ ├─ Graceful Degradation                             │  │
│ │ └─ Circuit Breaker                                  │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ Security Layer                                       │  │
│ │ ├─ Ed25519 Signing                                  │  │
│ │ ├─ Input Sanitizer (50+ attack patterns)           │  │
│ │ ├─ Output Filter                                    │  │
│ │ └─ Rate Limiting                                    │  │
│ └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**Security Layer (B1-B3, B8, B15)**
- Detects 50+ prompt injection patterns
- Blocks 40+ jailbreak personality variants
- Rate limiting (100-1000 requests/hour per user)
- Input/output filtering with Ed25519 signing

**Memory Layer (B4-B5)**
- **Context Memory (B4):** Redis L1/L2 tiered architecture
  - L1 (fast): In-memory cache, 300-5000 key-value pairs
  - L2 (persistent): Proxmox Redis, session state, findings
  - Graceful fallback if L1 fails
- **Deep Storage (B5):** ChromaDB vector database
  - 4 collections: personality_dna, sergio_rhetorical, sergio_humor, sergio_corpus
  - Semantic search for RAG (200-300ms first query, <50ms cached)

**Communication Layer (B10, B13)**
- **Redis Bus (B10):** S2 swarm coordination
  - Task distribution: `task:{id}`
  - Findings aggregation: `finding:{id}`
  - Cross-swarm context sharing
- **Swarm Coordinator (B13):** Agent assignment, load balancing, health checks

**Resilience Layer (B11-B12)**
- **Checkpoints:** Save operation state every 60 seconds
- **Timeout Prevention:** Heartbeat keepalives every 10 seconds
- **Recovery:** Resume from checkpoint on timeout
- **Task Decomposition:** Split long operations into subtasks

**Intelligence Layer (B6, B14, B9)**
- **IF.emotion (B6):** Personality DNA injection, cross-cultural detection
- **IF.TTT (B14):** Citation generation, traceability, audit logging
- **Audit Trail (B9):** Immutable event logs, 30-day hot, 365-day cold storage

---

## Project Structure

```
/home/setup/infrafabric/
├── src/
│   ├── core/
│   │   ├── auth/                       # B31-B34: OAuth, PKCE, providers
│   │   │   ├── oauth_manager.py
│   │   │   ├── pkce_flow.py
│   │   │   └── provider_registry.py
│   │   │
│   │   ├── security/                   # B1-B3, B8, B15, B21-B24: Security
│   │   │   ├── input_sanitizer.py      # B1: 50+ threat patterns
│   │   │   ├── output_filter.py        # B2: Crisis detection, PII filtering
│   │   │   ├── rate_limiter.py         # B3: Per-user, per-IP limits
│   │   │   ├── ed25519_signer.py       # B21-B24: Cryptographic signing
│   │   │   └── security_event_handler.py # B15: Threat escalation
│   │   │
│   │   ├── resilience/                 # B11-B12: Timeout & checkpoint
│   │   │   ├── timeout_prevention.py   # B11: Heartbeat + checkpoint
│   │   │   ├── checkpoint_manager.py   # B12: State saving/recovery
│   │   │   ├── circuit_breaker.py      # Graceful degradation
│   │   │   └── graceful_degradation.py # Fallback strategies
│   │   │
│   │   ├── comms/                      # B10, B13: Communication
│   │   │   ├── redis_bus_client.py     # B10: Task queue, findings
│   │   │   ├── swarm_coordinator.py    # B13: Agent management
│   │   │   └── packet_envelope.py      # IF.TTT compliance wrapper
│   │   │
│   │   ├── audit/                      # B9, B14: Audit & traceability
│   │   │   ├── audit_logger.py         # B9: Event logging
│   │   │   ├── citation_generator.py   # B14: if:// URI generation
│   │   │   └── if_ttt_compliance.py    # IF.TTT validation
│   │   │
│   │   ├── memory/                     # B4-B5: Memory systems
│   │   │   ├── context_memory.py       # B4: Redis L1/L2 cache
│   │   │   ├── deep_storage.py         # B5: ChromaDB RAG storage
│   │   │   ├── memory_manager.py       # Unified interface
│   │   │   └── cache_stats.py          # Performance metrics
│   │   │
│   │   ├── registry/                   # B7-B8: Model registry
│   │   │   ├── llm_registry.py         # B8: Cost, tokens, latency
│   │   │   └── prompt_optimizer.py     # B7: Token reduction
│   │   │
│   │   └── emotion/                    # B6: Personality framework
│   │       ├── emotion_framework.py    # B6: IF.emotion engine
│   │       ├── personality_dna.py      # 74 components (Sergio)
│   │       ├── cross_cultural_lexicon.py
│   │       └── emotion_output_filter.py
│   │
│   └── integrations/
│       ├── openwebui_bridge.py         # B16: OpenWebUI API integration
│       ├── conversation_state_manager.py
│       ├── unified_memory.py           # Unified L1/L2 interface
│       └── interfaces/
│           ├── rest_api.py             # REST endpoints
│           ├── cli.py                  # Command-line interface
│           └── voice_escalation.py     # B17: WhatsApp, SIP, TTS
│
├── tests/
│   ├── test_components/                # Unit tests (B1-B17)
│   │   ├── test_b1_input_sanitizer.py (94.6% coverage)
│   │   ├── test_b2_output_filter.py    (95.3% coverage)
│   │   ├── test_b3_rate_limiter.py     (94.9% coverage)
│   │   └── ... (B4-B17 similar)
│   │
│   ├── test_integration/               # Integration tests (62 paths)
│   │   ├── test_b1_b4_sanitizer_memory.py
│   │   ├── test_b3_b10_limiter_queue.py
│   │   └── test_b4_b5_b6_memory_storage_emotion.py
│   │
│   ├── test_e2e/                       # End-to-end workflows
│   │   ├── test_workflow_user_query.py
│   │   ├── test_workflow_openwebui_pipeline.py
│   │   ├── test_workflow_security_event.py
│   │   └── test_workflow_long_running_task.py
│   │
│   ├── test_security/                  # Security penetration tests
│   │   ├── test_prompt_injection_patterns.py (50+ patterns)
│   │   ├── test_jailbreak_detection.py (40+ variants)
│   │   ├── test_rate_limit_bypass.py
│   │   ├── test_context_poisoning.py
│   │   ├── test_cross_swarm_access.py
│   │   └── test_audit_trail_integrity.py
│   │
│   ├── test_performance/               # Performance load tests
│   │   ├── test_concurrent_agents.py   (100 agents, p95<5s)
│   │   ├── test_throughput.py          (1000+ req/sec)
│   │   └── test_large_contexts.py      (200K tokens)
│   │
│   ├── test_resilience/                # Failure injection tests
│   │   ├── test_redis_failure.py
│   │   ├── test_chromadb_timeout.py
│   │   ├── test_coordinator_crash.py
│   │   ├── test_network_partition.py
│   │   └── test_cascading_failures.py
│   │
│   ├── fixtures/
│   │   ├── test_datasets.py            # Test data
│   │   ├── conftest.py                 # pytest configuration
│   │   └── mocks.py                    # Mock services
│   │
│   └── data/
│       ├── threats.json                # Attack patterns
│       ├── legitimate_queries.json     # 1000+ test queries
│       └── attack_patterns.yaml        # CVE documentation
│
├── docs/
│   ├── architecture/
│   │   ├── INTEGRATION_MAP.md          # B16: Complete system mapping
│   │   └── IF_FOUNDATIONS.md           # Core concepts
│   │
│   ├── security/
│   │   ├── THREAT_MODEL.md             # Attack taxonomy
│   │   ├── SANDBOXING_STRATEGY.md      # Security isolation
│   │   └── INCIDENT_RESPONSE.md        # Response procedures
│   │
│   ├── testing/
│   │   ├── INTEGRATION_TEST_PLAN.md    # B19: 6-phase test strategy
│   │   └── CI_CD_PIPELINE.md           # Automated testing
│   │
│   ├── deployment/
│   │   ├── DEPLOYMENT_GUIDE.md         # B18: Production setup
│   │   ├── DOCKER_COMPOSE.yml          # Local development
│   │   └── KUBERNETES.yaml             # Cloud deployment
│   │
│   ├── personality/
│   │   ├── SERGIO_DNA.md               # 74-component personality
│   │   ├── RHETORICAL_DEVICES.md       # 23 devices
│   │   └── ETHICAL_PRINCIPLES.md       # 11 principles
│   │
│   └── DEVELOPER_GUIDE.md              # THIS FILE
│
├── config/
│   ├── infrafabric.schema.json         # B17: Configuration schema
│   ├── default.config.yaml             # Default settings
│   └── .env.example                    # Environment template
│
├── scripts/
│   ├── health_check.py                 # Verify installation
│   ├── run_tests.py                    # Test runner
│   ├── format_code.py                  # black, isort
│   ├── lint_code.py                    # ruff, mypy
│   └── generate_citations.py           # IF.citation generator
│
├── integration/
│   ├── redis_bus_schema.py             # (1,038 lines)
│   ├── unified_memory.py               # (800+ lines)
│   ├── conversation_state_manager.py   # (500+ lines)
│   ├── openwebui_claude_max_module.py  # (300+ lines)
│   └── openwebui_api_spec.md           # (1,297 lines)
│
├── docker-compose.yml                  # Local development environment
├── requirements.txt                    # Production dependencies
├── requirements-dev.txt                # Development dependencies
├── pyproject.toml                      # Python project config
├── pytest.ini                          # pytest configuration
├── .github/
│   └── workflows/
│       ├── test.yml                    # CI/CD testing
│       ├── lint.yml                    # Code quality
│       └── security.yml                # Security scanning
│
└── README.md                           # Project overview
```

---

## Coding Standards

### Python Style Guide

**Follow PEP 8 with type hints (mandatory):**

```python
# Good: Type hints required
def process_query(
    query: str,
    user_id: str,
    context: Optional[Dict[str, Any]] = None
) -> dict[str, str]:
    """
    Process user query with context memory.

    Args:
        query: User input text (max 10,000 chars)
        user_id: Unique user identifier
        context: Optional conversation context

    Returns:
        Dict with 'response' (str) and 'citations' (list[str])

    Raises:
        SecurityError: If prompt injection detected
        TimeoutError: If operation exceeds 30 seconds

    Citation:
        if://doc/process-query/2025-11-30
    """
    if not isinstance(query, str):
        raise TypeError(f"query must be str, got {type(query)}")

    if len(query) > 10000:
        raise ValueError(f"Query exceeds 10,000 chars ({len(query)})")

    # Implementation
    return {"response": "...", "citations": []}
```

**Naming conventions:**

- Classes: `PascalCase` (e.g., `ContextMemory`, `InputSanitizer`)
- Functions/methods: `snake_case` (e.g., `process_query`, `validate_input`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_QUERY_LENGTH`, `TIMEOUT_MS`)
- Private methods: `_leading_underscore` (e.g., `_validate_schema`)
- Protected methods: No prefix, document in docstring

### Documentation Requirements

**All public functions must have docstrings:**

```python
def claim_task(task_id: str, agent_id: str) -> bool:
    """
    Claim a task from the Redis queue for processing.

    This is part of B10 (Task Queue) integration.

    Args:
        task_id: Unique task identifier (UUID format)
        agent_id: Haiku agent identifier claiming the task

    Returns:
        True if claim successful, False if already claimed

    Raises:
        TaskNotFoundError: If task_id doesn't exist in queue
        RedisConnectionError: If Redis unavailable

    Example:
        >>> claimed = claim_task("task-001", "haiku-agent-1")
        >>> assert claimed is True

    Note:
        - Atomic operation: Race condition prevention via Redis HSET
        - Sets task status to 'IN_PROGRESS' with agent_id
        - Extends Redis key TTL to prevent cleanup

    Citation:
        if://doc/redis-bus-schema/2025-11-30 (line 234)
        Related: B10 Task Queue, B13 Swarm Coordinator

    See Also:
        - release_task(): Opposite operation
        - get_task_status(): Check current task state
    """
```

### Error Handling

**Always use specific exceptions:**

```python
# Good
from src.core.security.exceptions import (
    SecurityError,
    PromptInjectionError,
    RateLimitExceededError
)

try:
    sanitized = sanitizer.analyze(user_input)
    if sanitized['threat_detected']:
        raise PromptInjectionError(
            f"Threat detected: {sanitized['threat_type']}",
            threat_type=sanitized['threat_type'],
            confidence=sanitized['confidence']
        )
except PromptInjectionError as e:
    # Log to IF.TTT audit trail
    logger.security(f"Injection blocked: {e}")
    raise
```

### IF.Citation References

**Every significant code change must reference a citation:**

```python
def get_context_value(key: str, user_id: str) -> Optional[Any]:
    """
    Retrieve value from context memory (B4 - Context Memory).

    Citation: if://doc/context-memory/2025-11-30
    Implementation details: /home/setup/infrafabric/src/core/memory/context_memory.py:145
    Related components: B5 (Deep Storage), B9 (Audit Trail)
    """
    # Implementation
    pass
```

---

## Testing Strategy

### Test Organization

**Unit Tests (Phase 1: >90% coverage)**
- Test each component (B1-B17) in isolation
- Mock all external dependencies
- Run in <15 minutes total

```bash
pytest tests/test_components/ \
  --cov=src/core \
  --cov-report=html \
  --cov-fail-under=90 \
  -v
```

**Integration Tests (Phase 2: >80% coverage)**
- Test 62 critical component interaction paths
- Use real Redis and ChromaDB (Docker)
- Validate data flow between components

```bash
pytest tests/test_integration/ \
  --cov=src \
  --cov-fail-under=80 \
  -v
```

**End-to-End Tests (Phase 3: 100% critical paths)**
- Complete workflows from input to response
- Test in staging environment
- 4 critical workflows: user query, OpenWebUI, security event, long-running task

```bash
pytest tests/test_e2e/ \
  --env=staging \
  -v --timeout=300
```

**Security Tests (Phase 4: 100% threat coverage)**
- Prompt injection (50+ patterns)
- Jailbreak attempts (40+ variants)
- Rate limit bypasses, context poisoning, audit trail tampering

```bash
pytest tests/test_security/ \
  -v --tb=short
```

**Performance Tests (Phase 5: All SLA validation)**
- 100 concurrent Haiku agents: p95 <5s
- 1000+ requests/second throughput
- 200K token contexts: <5s processing

```bash
pytest tests/test_performance/ \
  -v --durations=20 \
  -m performance
```

**Resilience Tests (Phase 6: All failure modes)**
- Redis failure recovery, ChromaDB timeout, coordinator crash
- Network partition handling, cascading failure prevention

```bash
pytest tests/test_resilience/ \
  --timeout=600 \
  -v
```

### Running Tests Locally

```bash
# Quick validation (unit + integration)
./scripts/run_tests.py --fast

# Full test suite
./scripts/run_tests.py --full

# Specific component
pytest tests/test_components/test_b1_input_sanitizer.py -v

# With coverage report
pytest tests/ \
  --cov=src \
  --cov-report=html \
  --cov-report=term
```

### CI/CD Integration

Tests run automatically on:
- **Pre-commit:** Code format validation
- **Pull Request:** Unit tests (must pass, >90% coverage)
- **Merge to main:** Integration tests
- **Nightly:** Security penetration tests (152+ tests)
- **Weekly:** Performance benchmarks, resilience tests

---

## Contribution Workflow

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/infrafabric.git
cd infrafabric

# Add upstream remote
git remote add upstream https://github.com/dannystocker/infrafabric.git
```

### 2. Create Feature Branch

```bash
# Update local main from upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch (naming convention)
# Format: feature/<component>/<description> or fix/<component>/<description>
git checkout -b feature/b4-redis-cache-optimization
```

### 3. Make Changes with Tests

```bash
# Edit files (example: improving Context Memory B4)
vim src/core/memory/context_memory.py

# Add tests
vim tests/test_components/test_b4_context_memory.py

# Run tests
pytest tests/test_components/test_b4_context_memory.py -v

# Verify existing tests still pass
pytest tests/test_integration/ -v
```

### 4. Code Quality Checks

```bash
# Format code (black, isort)
./scripts/format_code.py

# Lint (ruff, mypy)
./scripts/lint_code.py

# Security scan
bandit -r src/

# All checks
pre-commit run --all-files
```

### 5. Commit with IF.Citation

```bash
# All commits must reference IF.citation
git commit -m "Optimize Context Memory (B4) L1 cache hit rate

- Reduce TTL from 300s to 120s for improved freshness
- Add adaptive eviction policy based on access patterns
- Performance improvement: +15% cache hit rate

Citation: if://doc/context-memory-optimization/2025-11-30
Fixes: #123
Tests: test_b4_context_memory.py::test_cache_hit_rate_improvement
Reviewers: @maintainer

Generated with Claude Code (https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"

# Verify commit format
git log -1 --format='%B'
```

### 6. Push and Create PR

```bash
# Push to your fork
git push origin feature/b4-redis-cache-optimization

# Create PR with detailed description
# Template includes:
# - What changed and why
# - Component affected (B1-B17)
# - Tests added/modified
# - Performance impact
# - IF.TTT compliance
```

### 7. Code Review Process

- **Automated checks:** Lint, type checking, tests (must pass)
- **Security review:** Security tests, threat model validation
- **Architecture review:** Does it align with component design?
- **Performance review:** Benchmarks, regression testing
- **Documentation:** Updated docstrings, citations

### 8. Merge Requirements

✓ All automated checks pass
✓ >90% test coverage maintained
✓ At least 1 approving review
✓ No merge conflicts
✓ Documentation updated
✓ IF.TTT citations included

---

## Development Environment Setup

### Docker-Based Development (Recommended)

```bash
# Start all services
docker-compose up -d

# Verify services
docker-compose ps
# NAME              STATUS
# infrafabric-api   Up 2 minutes
# redis             Up 2 minutes
# chromadb          Up 2 minutes

# Access services
redis-cli PING                    # Redis
curl http://localhost:8000/api/heartbeat  # ChromaDB
curl http://localhost:8080/health         # OpenWebUI (optional)
```

### Local Development (Alternative)

```bash
# 1. Install Redis
apt install redis-server          # Ubuntu/Debian
brew install redis                # macOS

# 2. Install ChromaDB
pip install chromadb

# 3. Start services
redis-server &
chromadb run --port 8000 &

# 4. Verify
python -c "import redis; r = redis.Redis(); print(r.ping())"
```

### Environment Configuration

```bash
# Copy template
cp config/.env.example .env

# Edit for your setup
vim .env

# Required variables:
REDIS_HOST=localhost
REDIS_PORT=6379
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
OPENAI_API_KEY=sk-...           # For Claude Max
LOG_LEVEL=debug                  # Development
IF_TTT_ENABLED=true             # Always true
```

### IDE Setup

**VSCode (Recommended)**

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

**PyCharm**

- Python interpreter: `./venv/bin/python`
- Enable pytest for test discovery
- Code style: PEP 8 with 4-space indent
- Run → Edit Configurations → Add pytest

---

## Common Development Tasks

### Adding a New OAuth Provider (B31-B34)

```python
# 1. Create provider implementation
# src/core/auth/providers/github_provider.py

from src.core.auth.oauth_manager import OAuthProvider

class GitHubProvider(OAuthProvider):
    """GitHub OAuth 2.0 provider implementation."""

    def __init__(self, client_id: str, client_secret: str):
        super().__init__(
            name="github",
            client_id=client_id,
            client_secret=client_secret,
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token"
        )

    async def get_user_info(self, access_token: str) -> dict:
        """Fetch user info from GitHub API."""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await httpx.get(
            "https://api.github.com/user",
            headers=headers
        )
        return response.json()

# 2. Register provider
# src/core/auth/provider_registry.py

PROVIDERS = {
    'github': GitHubProvider,
    'google': GoogleProvider,
    'microsoft': MicrosoftProvider,
}

# 3. Test provider
# tests/test_components/test_github_oauth.py

def test_github_oauth_flow():
    provider = GitHubProvider(
        client_id="test_client",
        client_secret="test_secret"
    )
    assert provider.name == "github"
    # Test PKCE flow, token exchange, etc.
```

### Implementing Security Feature (B1-B3)

```python
# 1. Add threat pattern to Input Sanitizer
# src/core/security/input_sanitizer.py

THREAT_PATTERNS = {
    'prompt_injection': [
        r'ignore\s+previous\s+instructions',
        r'forget\s+the\s+system\s+prompt',
        # ... 48 more patterns
    ],
    'sql_injection': [
        r'(\bDELETE\b|\bDROP\b|\bTRUNCATE\b)\s+',
        # ...
    ],
}

# 2. Test detection
# tests/test_security/test_injection_detection.py

@pytest.mark.parametrize("pattern", INJECTION_PATTERNS)
def test_detects_injection(pattern):
    sanitizer = InputSanitizer()
    result = sanitizer.analyze(f"ignore {pattern}")
    assert result['threat_detected'] is True

# 3. Audit log the detection
# Generate IF.TTT citation

from src.core.audit.citation_generator import generate_citation

citation = generate_citation(
    claim="Prompt injection detected",
    evidence="Pattern match in B1 sanitizer",
    confidence=0.98
)
```

### Adding Audit Logging to Component (B9)

```python
# src/core/security/input_sanitizer.py

import logging
from src.core.audit.audit_logger import audit_log
from src.core.audit.citation_generator import generate_citation

logger = logging.getLogger(__name__)

def analyze(self, user_input: str) -> dict:
    """Analyze input for security threats."""

    result = self._run_analysis(user_input)

    # Log to IF.TTT audit trail
    if result['threat_detected']:
        citation = generate_citation(
            claim=f"Threat detected: {result['threat_type']}",
            evidence={
                'pattern': result['pattern_matched'],
                'confidence': result['confidence'],
                'component': 'B1_InputSanitizer'
            },
            source_file=__file__,
            source_line=123
        )

        audit_log(
            event_type='security_threat',
            severity='HIGH',
            user_id=getattr(self, 'user_id', 'unknown'),
            detail=result,
            citation=citation
        )

    return result
```

### Writing Integration Test

```python
# tests/test_integration/test_b1_b4_sanitizer_memory.py

def test_sanitized_input_stored_in_context(mock_redis):
    """Flow: Raw input → Sanitized → Stored in context (B1 → B4)"""

    # 1. Setup components
    sanitizer = InputSanitizer()
    context = ContextMemory(redis_client=mock_redis)

    # 2. Sanitize input (B1)
    raw_input = "What is machine learning?"
    analysis = sanitizer.analyze(raw_input)
    assert analysis['threat_detected'] is False

    # 3. Store in context memory (B4)
    session_id = "test_session_123"
    context.set(f"{session_id}:input", analysis, ttl=3600)

    # 4. Retrieve and verify
    stored = context.get(f"{session_id}:input")
    assert stored == analysis

    # 5. Verify Redis was called
    mock_redis.setex.assert_called_with(
        f"{session_id}:input",
        3600,
        mock.ANY
    )
```

---

## Debugging Guide

### Logging Configuration

```python
# src/core/logging_config.py

import logging
import json
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# For JSON output (machine-readable)
class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'file': f"{record.filename}:{record.lineno}"
        })
```

### Redis Inspection

```bash
# Connect to Redis
redis-cli

# Check memory usage
INFO memory

# List all keys
KEYS *

# Inspect specific key
GET memory:session:user_123:input

# Monitor real-time commands
MONITOR

# Performance stats
INFO stats

# Clear database (development only!)
FLUSHDB
```

### ChromaDB Debugging

```python
# Query ChromaDB directly
import chromadb

client = chromadb.HttpClient(host="localhost", port=8000)

# List collections
collections = client.list_collections()
print([c.name for c in collections])

# Query collection
results = client.get_collection("personality_dna").query(
    query_texts=["emotional support"],
    n_results=5
)

# Check collection stats
collection = client.get_collection("personality_dna")
print(f"Document count: {collection.count()}")
```

### Common Issues & Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| Redis connection refused | `ConnectionError: Connection refused` | Check Redis running: `redis-cli PING` |
| ChromaDB timeout | Semantic search hangs >500ms | Verify ChromaDB health: `curl localhost:8000/api/heartbeat` |
| Memory exhaustion | Process killed, OOM errors | Check memory: `free -h`, increase `max_memory_mb` in config |
| Rate limiter false positives | Legitimate requests blocked | Adjust thresholds in `config/infrafabric.schema.json` |
| Stale cache | Old data returned | Reduce TTL: `l1_ttl_seconds: 120` (was 300) |

### Profiling Performance

```python
# Profile a function
import cProfile
import pstats
from io import StringIO

pr = cProfile.Profile()
pr.enable()

# Run code to profile
result = process_query("test query")

pr.disable()
s = StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(10)  # Top 10 functions
print(s.getvalue())
```

---

## Release Process

### Version Numbering

Follow **Semantic Versioning** (MAJOR.MINOR.PATCH):

- **MAJOR:** Breaking changes (incompatible API changes)
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes

Example: `1.2.3` → `1.3.0` (new feature) → `1.3.1` (bug fix)

### Release Checklist

```bash
# 1. Update version
vim src/__init__.py
# __version__ = "1.3.0"

# 2. Update changelog
vim CHANGELOG.md
# Add entry under [1.3.0] with date, features, fixes, security updates

# 3. Run full test suite
pytest tests/ --cov=src --cov-fail-under=90

# 4. Generate documentation
python scripts/generate_documentation.py

# 5. Create annotated git tag
git tag -a v1.3.0 -m "Release version 1.3.0

Features:
- Improved Context Memory L1/L2 performance (+15% cache hit)
- 10 new OAuth providers (B31-B34)

Fixes:
- Fixed race condition in Redis Bus (B10)

Security:
- Updated threat pattern database (50+ new injection patterns)

Citation: if://release/v1.3.0/2025-11-30"

# 6. Push tag
git push origin v1.3.0

# 7. Create GitHub Release with:
#   - Title: "Release v1.3.0"
#   - Description: Changelog + links to PRs
#   - Assets: tar.gz source, wheel package
```

### Documentation Updates

Before releasing, update:

- `README.md` - Feature summary
- `CHANGELOG.md` - Detailed changes
- `docs/INTEGRATION_MAP.md` - Architecture changes
- `docs/API.md` - New endpoints
- `docs/MIGRATION.md` - Breaking changes (if MAJOR version bump)

### Distribution

```bash
# Build wheel package
python -m build

# Upload to PyPI (when ready for public release)
twine upload dist/infrafabric-1.3.0-py3-none-any.whl

# Tag Docker image
docker build -t infrafabric:1.3.0 .
docker push infrafabric:1.3.0
```

---

## Summary

This developer guide covers:

1. **Getting Started:** 15-minute setup for new developers
2. **Architecture:** Component responsibilities and data flow
3. **Project Structure:** File organization and naming conventions
4. **Coding Standards:** PEP 8, type hints, documentation requirements
5. **Testing:** 6-phase testing strategy with >90% coverage target
6. **Contribution Workflow:** Fork → branch → test → commit → PR → merge
7. **Development Tasks:** Real-world examples for common work
8. **Debugging:** Tools and techniques for troubleshooting
9. **Release:** Versioning and distribution process

**Next Steps:**

- Set up development environment: `./scripts/setup_dev_env.sh`
- Read `/home/setup/infrafabric/docs/architecture/INTEGRATION_MAP.md` for system deep dive
- Check `/home/setup/infrafabric/agents.md` for InfraFabric component catalog
- Run test suite: `pytest tests/ -v`
- Pick a component (B1-B17) and explore its implementation

**Questions?**

- Architecture: See `docs/architecture/INTEGRATION_MAP.md`
- Security: See `docs/security/THREAT_MODEL.md`
- Testing: See `docs/testing/INTEGRATION_TEST_PLAN.md`
- Deployment: See `docs/deployment/DEPLOYMENT_GUIDE.md`

---

**Citation:** `if://doc/developer-guide/v1.0/2025-11-30`
**Last Updated:** 2025-11-30
**Maintainer:** InfraFabric Development Team

Generated with Claude Code (https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
