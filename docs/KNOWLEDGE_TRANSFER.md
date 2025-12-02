# InfraFabric Knowledge Transfer Checklist

**Document ID:** `if://doc/knowledge-transfer/2025-11-30`

**Version:** 1.0

**Last Updated:** November 30, 2025

**Target Audience:** New maintainers, experienced developers new to InfraFabric

**Estimated Time to Complete:** 6 weeks (Part-time) / 3 weeks (Full-time)

---

## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [Week-by-Week Knowledge Transfer Plan](#week-by-week-knowledge-transfer-plan)
3. [Critical Knowledge Areas](#critical-knowledge-areas)
4. [Key Files Reference](#key-files-reference)
5. [Common Scenarios & Responses](#common-scenarios--responses)
6. [Production Access Checklist](#production-access-checklist)
7. [Contacts & Escalation](#contacts--escalation)
8. [Post-Transfer Validation](#post-transfer-validation)

---

## EXECUTIVE SUMMARY

### What is InfraFabric?

InfraFabric S2 is the **Universal Logistics Engine for Physical AI**—a Redis-backed intelligent system that decouples LLM Intelligence from Physical Execution. It enables AI agents to control drones, energy grids, broadcasting systems, and defense applications with:

- **0.071ms latency** (S2 Redis Engine replacing legacy file polling)
- **Military-grade governance** (Guardian pre-crime safety layer)
- **Production-ready architecture** (45 agents delivered, security hardened)
- **Polyglot industry support** (20+ verticals: Air, Media, Defense, Energy, Medical)

### Architecture at 10,000 Feet

```
┌─────────────────────────────────────────────────────────┐
│  Intelligence Layer (Claude LLM Agents)                 │
│  - 45 specialized agents (A1-A45, B1-B45)              │
│  - IF.emotion (multimodal sentiment/intention analysis) │
│  - IF.ceo (16-facet executive council)                 │
└────────────────────┬────────────────────────────────────┘
                     │ IF.packet (cryptographic envelope)
                     ▼
┌─────────────────────────────────────────────────────────┐
│  S2 Governance Matrix (Redis Bus)                       │
│  - Task posting and claiming                            │
│  - Cross-swarm coordination                             │
│  - Context sharing (140x faster than file polling)      │
│  - Guardian: Pre-crime safety vetting                   │
└────────────────────┬────────────────────────────────────┘
                     │ Vertically-specific Lexicons
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Physical Adapters                                       │
│  - Drones (MAVLink, CoT, DJI)                          │
│  - Broadcasting (vMix, NDI, SIP)                        │
│  - Tactical Systems (Blue Force Tracking)               │
│  - Energy & Medical Verticals                           │
└─────────────────────────────────────────────────────────┘
```

### Key Technologies

| Component | Technology | Role |
|-----------|-----------|------|
| **Bus Engine** | Redis Cluster | Task queue, context store, agent coordination |
| **Vector Storage** | ChromaDB | Semantic memory (embeddings, context vectors) |
| **Cryptography** | Ed25519 | Agent identity, message signing, verification |
| **Auth** | OAuth 2.0 PKCE | User authentication (Google, GitHub, Azure) |
| **Containerization** | Docker Compose | Local dev, staging, production deployment |
| **SSL/TLS** | Let's Encrypt | HTTPS for all external APIs |
| **Monitoring** | Prometheus + Grafana | Metrics, dashboards, alerting |
| **Secrets** | HashiCorp Vault | API keys, database credentials, OAuth secrets |

### Current State (November 2025)

- **45 agents delivered** (A1-A45 phase, B1-B45 integration phase complete)
- **Production-ready:** Security hardened, Ed25519 signing verified, OAuth flow tested
- **Target alpha users:** 20 concurrent users
- **Deployment:** Docker Compose on StackCP (Linux), Proxmox support
- **Documentation:** 7,639 lines across 20 core deliverables
- **Test coverage:** Unit + integration + security + resilience test suites

---

## WEEK-BY-WEEK KNOWLEDGE TRANSFER PLAN

### WEEK 1: Foundation & Architecture

**Goal:** Understand overall system design and set up local development environment.

**Time Commitment:** 15-20 hours

#### Day 1-2: Read Core Documentation

- [ ] Read **README.md** (5 min) — Project overview and quick start
- [ ] Read **MISSION_REPORT_2025-11-30.md** (60 min) — B1-B45 deliverables, architecture decisions, metrics
- [ ] Read **DOCUMENTATION_SUMMARY.md** (30 min) — Map of all docs by category
- [ ] Read **/docs/ARCHITECTURE_OVERVIEW.md** (if exists) or skim key architecture files:
  - [ ] `/home/setup/infrafabric/docs/IF_PROTOCOL_REGISTRY.md`
  - [ ] `/home/setup/infrafabric/docs/protocols/CROSS_SWARM_COORDINATION.md`
- [ ] Review **agents.md** (90 min) — Complete agent catalog (A1-B45), capabilities, dependencies

#### Day 3: Setup Local Environment

- [ ] Clone repository: `git clone https://github.com/dannystocker/infrafabric.git`
  ```bash
  cd /home/setup/infrafabric
  git config user.name "Your Name"
  git config user.email "your.email@example.com"
  ```
- [ ] Install dependencies:
  ```bash
  pip install -r requirements.txt
  python -m pytest tests/ -v --tb=short
  ```
- [ ] Start local Redis (for development):
  ```bash
  docker-compose up -d redis
  ```
- [ ] Verify Python version: `python --version` (3.10+ required)
- [ ] Install development tools: `pip install black flake8 pytest-cov`

#### Day 4-5: Review Subdirectories

- [ ] Read all README files in `/docs` subdirectories:
  - [ ] `/docs/security/` — Security architecture
  - [ ] `/docs/architecture/` — System design patterns
  - [ ] `/docs/deployment/` — Infrastructure guides
  - [ ] `/docs/testing/` — Test strategy
  - [ ] `/docs/protocols/` — Communication protocols
- [ ] Run basic tests:
  ```bash
  pytest tests/test_core_security.py -v
  pytest tests/test_auth_oauth.py -v
  ```
- [ ] Verify test success: All tests should pass before moving to Week 2

**Success Criteria:**
- Local dev environment runs without errors
- Can run full test suite (pytest tests/ -v)
- Understand system architecture at 10,000-foot level
- Know where to find documentation for specific subsystems

---

### WEEK 2: Security Layer (P0 - CRITICAL)

**Goal:** Understand cryptographic identity, message signing, and OAuth flow.

**Time Commitment:** 20-25 hours

**Security Focus:** You must understand this before production access. These are the keys to the kingdom.

#### Day 1: Ed25519 Cryptographic Identity

- [ ] Read **ED25519_IMPLEMENTATION_FINAL.md** (60 min)
  - Understand: Agent identity, private key storage, public key registry
  - Key insight: Every agent has a unique Ed25519 keypair in Redis
- [ ] Review source code:
  ```bash
  cat /home/setup/infrafabric/src/core/security/ed25519_identity.py
  ```
- [ ] Understand key components:
  - `AgentIdentity` class: Core identity abstraction
  - Key generation: `generate_keypair()`
  - Key storage: Redis persistence
  - Key rotation mechanism
- [ ] Run identity tests:
  ```bash
  pytest tests/test_ed25519_identity.py -v
  ```

#### Day 2: Message Signing & Verification

- [ ] Read **SIGNATURE_VERIFICATION_SUMMARY.md** (60 min)
- [ ] Read **QUICK_START_SIGNATURE_VERIFICATION.md** (30 min)
- [ ] Review source code:
  ```bash
  cat /home/setup/infrafabric/src/core/security/message_signing.py
  ```
- [ ] Understand:
  - Message signing process: Agent → Hash → Sign → IF.packet
  - Verification process: IF.packet → Extract signature → Verify against public key
  - Audit trail: All signed messages logged in Redis
- [ ] Run signature tests:
  ```bash
  pytest tests/test_message_signing.py -v
  pytest tests/test_signature_verification.py -v
  ```
- [ ] Practice manual verification:
  ```python
  from core.security import SignatureVerifier
  verifier = SignatureVerifier()
  # See QUICK_START_SIGNATURE_VERIFICATION.md for examples
  ```

#### Day 3: OAuth PKCE Authentication Flow

- [ ] Read **OAUTH_PKCE_IMPLEMENTATION_SUMMARY.md** (60 min)
  - PKCE (Proof Key for Code Exchange) flow
  - Why PKCE: Protection against authorization code injection
  - Token refresh automation
- [ ] Review source code:
  ```bash
  cat /home/setup/infrafabric/src/core/auth/oauth_pkce.py
  ```
- [ ] Understand flow:
  1. User initiates login → Browser redirected to OAuth provider (Google/GitHub/Azure)
  2. User grants permission → Provider redirects back with auth code
  3. Backend exchanges code for tokens (using PKCE code_verifier)
  4. Tokens stored in Redis (encrypted at rest)
  5. Refresh token auto-refreshes before expiry
- [ ] Test OAuth flow:
  ```bash
  pytest tests/test_oauth_pkce_flow.py -v
  pytest tests/test_token_refresh.py -v
  ```

#### Day 4: Multi-Provider Support

- [ ] Review supported OAuth providers:
  - [ ] Google OAuth (client ID in Vault)
  - [ ] GitHub OAuth (client ID in Vault)
  - [ ] Azure AD (tenant ID, client ID in Vault)
- [ ] Understand provider-specific quirks:
  ```bash
  cat /home/setup/infrafabric/src/core/auth/oauth_providers.py
  ```
- [ ] Set up Vault secrets for local testing (see OPERATIONS_MANUAL.md)
- [ ] Test each provider:
  ```bash
  pytest tests/test_oauth_google.py -v
  pytest tests/test_oauth_github.py -v
  pytest tests/test_oauth_azure.py -v
  ```

#### Day 5: Security Audit & Testing

- [ ] Review threat model:
  ```bash
  cat /home/setup/infrafabric/docs/IF_EMOTION_THREAT_MODEL.md
  ```
- [ ] Run security test suite:
  ```bash
  pytest tests/test_security_*.py -v
  ```
- [ ] Review audit logs (Redis):
  ```bash
  redis-cli KEYS "audit:*" | head -20
  redis-cli HGETALL "audit:signature_verifications"
  ```
- [ ] Understand attack scenarios and mitigations (see Common Scenarios section below)

**Success Criteria:**
- Can explain Ed25519 identity system without reference materials
- Can verify a signed message manually using library functions
- Understand OAuth PKCE flow: auth code → code verifier → token exchange
- Know how tokens are stored, refreshed, and rotated
- Can trace a security event in Redis audit logs

---

### WEEK 3: Redis & Swarm Coordination

**Goal:** Understand Redis architecture, task posting/claiming, and inter-agent communication.

**Time Commitment:** 18-20 hours

#### Day 1-2: Redis Architecture & Data Structures

- [ ] Review Redis schema:
  ```bash
  cat /home/setup/infrafabric/docs/protocols/CROSS_SWARM_COORDINATION.md
  ```
- [ ] Understand key types:
  - **Strings:** Agent state, configuration values
  - **Hashes:** Agent metadata (identity, status, metrics)
  - **Lists:** Task queues (pending, claimed, completed)
  - **Sets:** Agent registries, tags
  - **Sorted Sets:** Priority queues, leaderboards
  - **Streams:** Audit logs, event history
- [ ] Review source code:
  ```bash
  cat /home/setup/infrafabric/src/core/logistics/redis_swarm_coordinator.py
  ```
- [ ] Test Redis operations:
  ```bash
  redis-cli PING  # Should return PONG
  redis-cli INFO  # System stats
  redis-cli DBSIZE  # Key count
  ```

#### Day 2-3: Task Posting & Claiming

- [ ] Understand task lifecycle:
  1. **Posting:** Agent A posts task to Redis queue (LPUSH to `queue:pending`)
  2. **Discovery:** Agent B scans queues (BRPOP with timeout)
  3. **Claiming:** Agent B locks task in Redis (SET with NX option)
  4. **Execution:** Agent B processes task
  5. **Completion:** Agent B updates task status, posts results
  6. **Cleanup:** Task moved to `queue:completed`, TTL set for archive
- [ ] Review task posting:
  ```bash
  cat /home/setup/infrafabric/src/core/logistics/task_posting.py
  ```
- [ ] Review task claiming:
  ```bash
  cat /home/setup/infrafabric/src/core/logistics/task_claiming.py
  ```
- [ ] Run tests:
  ```bash
  pytest tests/test_task_posting.py -v
  pytest tests/test_task_claiming.py -v
  ```

#### Day 4: Cross-Swarm Messaging

- [ ] Understand S2 communication protocol:
  - **S2 Redis Bus:** Haiku-to-Haiku direct messaging via Redis Pub/Sub
  - **IF.packet:** Cryptographic envelope (signature + timestamp + payload)
  - **Background Communication:** Agents exchange context while main user request processes
- [ ] Review protocol:
  ```bash
  cat /home/setup/infrafabric/docs/protocols/CROSS_SWARM_COORDINATION.md
  cat /home/setup/infrafabric/docs/protocols/CLAUDE_MAX_CONTEXT_SHARING.md
  ```
- [ ] Test messaging:
  ```bash
  pytest tests/test_cross_swarm_messaging.py -v
  pytest tests/test_if_packet_signing.py -v
  ```

#### Day 5: Timeout Prevention & Resilience

- [ ] Understand timeout challenges:
  - Claude API has 300-second request timeout
  - InfraFabric tasks may take longer than 300s
  - Solution: Background communication + status polling
- [ ] Review timeout prevention mechanism:
  ```bash
  cat /home/setup/infrafabric/src/core/resilience/timeout_prevention.py
  ```
- [ ] Understand context sharing:
  ```bash
  cat /home/setup/infrafabric/src/core/resilience/context_sharing.py
  ```
- [ ] Test resilience:
  ```bash
  pytest tests/test_timeout_prevention.py -v
  pytest tests/test_context_sharing.py -v
  ```

**Success Criteria:**
- Can explain Redis data structures and their use in InfraFabric
- Understand task lifecycle: posting → claiming → execution → completion
- Know how S2 cross-swarm messaging works (IF.packet, signing, Pub/Sub)
- Can manually post and claim tasks using Redis CLI
- Understand timeout prevention mechanisms

---

### WEEK 4: OAuth & Multi-Provider Testing

**Goal:** Validate OAuth implementation across all providers.

**Time Commitment:** 15-18 hours

#### Day 1-2: Provider Configuration

- [ ] Get OAuth credentials from Vault:
  ```bash
  vault kv get secret/oauth/google
  vault kv get secret/oauth/github
  vault kv get secret/oauth/azure
  ```
- [ ] Configure local .env file:
  ```bash
  cat > .env.local << 'EOF'
  OAUTH_GOOGLE_CLIENT_ID=xxx
  OAUTH_GOOGLE_CLIENT_SECRET=xxx
  OAUTH_GITHUB_CLIENT_ID=xxx
  OAUTH_GITHUB_CLIENT_SECRET=xxx
  OAUTH_AZURE_TENANT_ID=xxx
  OAUTH_AZURE_CLIENT_ID=xxx
  OAUTH_AZURE_CLIENT_SECRET=xxx
  EOF
  ```
- [ ] Review provider-specific documentation:
  - Google: /docs/oauth-providers/GOOGLE_OAUTH.md
  - GitHub: /docs/oauth-providers/GITHUB_OAUTH.md
  - Azure: /docs/oauth-providers/AZURE_AD.md

#### Day 3-5: Test Each Provider

- [ ] **Google OAuth Test:**
  - [ ] Start local server: `python -m flask run`
  - [ ] Navigate to http://localhost:5000/auth/google
  - [ ] Verify redirect to Google consent screen
  - [ ] Grant permission, verify redirect back
  - [ ] Check token in Redis: `redis-cli HGETALL "user:your-email:tokens"`
  - [ ] Run tests: `pytest tests/test_oauth_google.py -v`

- [ ] **GitHub OAuth Test:**
  - [ ] Navigate to http://localhost:5000/auth/github
  - [ ] Verify redirect to GitHub consent screen
  - [ ] Grant permission, verify redirect back
  - [ ] Check token in Redis
  - [ ] Run tests: `pytest tests/test_oauth_github.py -v`

- [ ] **Azure AD Test:**
  - [ ] Navigate to http://localhost:5000/auth/azure
  - [ ] Verify redirect to Azure consent screen
  - [ ] Grant permission, verify redirect back
  - [ ] Check token in Redis
  - [ ] Run tests: `pytest tests/test_oauth_azure.py -v`

- [ ] **Token Refresh Test:**
  - [ ] Wait for token to near expiry (or manually set expiry)
  - [ ] Verify auto-refresh triggers
  - [ ] Check new token in Redis
  - [ ] Run tests: `pytest tests/test_token_refresh.py -v`

- [ ] **Error Scenarios:**
  - [ ] Test with invalid client ID (should show clear error)
  - [ ] Test with expired token (should auto-refresh or prompt re-auth)
  - [ ] Test with provider unavailable (should gracefully handle)

**Success Criteria:**
- Successfully authenticate with all 3 OAuth providers
- Tokens properly stored and encrypted in Redis
- Token refresh works automatically
- Error scenarios handled gracefully

---

### WEEK 5: Production Operations & Monitoring

**Goal:** Understand deployment, monitoring, incident response, and backup procedures.

**Time Commitment:** 20-25 hours

#### Day 1: Deployment Architecture

- [ ] Read **DEPLOYMENT_GUIDE.md** (in /docs/deployment/)
- [ ] Understand environments:
  - **Local:** Docker Compose on laptop
  - **Staging:** StackCP pre-production environment
  - **Production:** StackCP production (client-facing)
- [ ] Review Dockerfile and docker-compose.yml:
  ```bash
  cat /home/setup/infrafabric/Dockerfile
  cat /home/setup/infrafabric/docker-compose.yml
  ```
- [ ] Understand services:
  - **API Server:** Flask/FastAPI serving agent endpoints
  - **Redis:** Data store and task queue
  - **ChromaDB:** Vector database for semantic memory
  - **Nginx:** Reverse proxy, SSL termination
  - **Prometheus:** Metrics scraper
  - **Grafana:** Dashboards and visualization

#### Day 2: Monitoring & Observability

- [ ] Access monitoring dashboards:
  - Grafana: http://your-domain:3000
  - Prometheus: http://your-domain:9090
- [ ] Review key metrics:
  - **API Response Time:** p50, p95, p99 latency
  - **Task Throughput:** Tasks/min posted, claimed, completed
  - **Error Rate:** % of failed tasks
  - **Redis Memory:** Current usage vs limits
  - **Agent Health:** % of agents connected and healthy
- [ ] Understand alerting:
  - High error rate (>5%) → page on-call
  - Redis memory >80% → alert ops team
  - API latency p99 >500ms → page on-call
- [ ] Practice reading Grafana dashboards:
  - Add custom metric queries
  - Understand time range selection
  - Export dashboard configurations

#### Day 3: Logging & Audit Trails

- [ ] Understand logging strategy:
  - All agent actions logged to Redis streams
  - Audit trail: signature verifications, OAuth logins, task completions
  - Searchable by agent ID, timestamp, action type
- [ ] Review logging setup:
  ```bash
  cat /home/setup/infrafabric/config/logging.yaml
  ```
- [ ] Query logs:
  ```bash
  # Redis streams
  redis-cli XRANGE "log:api:*" - +
  redis-cli XRANGE "audit:signature_verifications" - + COUNT 20
  redis-cli XRANGE "audit:oauth_logins" - + COUNT 20
  ```
- [ ] Understand log retention:
  - Hot logs: 7 days in Redis
  - Cold logs: 90 days in S3/backup storage
  - Archive: Indefinite retention in encrypted vault

#### Day 4: Backup & Disaster Recovery

- [ ] Understand backup strategy:
  - **Redis:** Snapshot every 6 hours, 3 copies (primary, staging, archive)
  - **PostgreSQL:** Continuous WAL archiving, 30-day PITR window
  - **Configuration:** Git-tracked (no secrets), can rebuild from git
- [ ] Review backup procedures:
  ```bash
  # Manual Redis backup
  redis-cli BGSAVE
  redis-cli LASTSAVE  # Check timestamp

  # List recent backups
  ls -lh /backups/redis/
  ```
- [ ] Practice restore procedure (in staging only):
  - [ ] Stop Redis
  - [ ] Copy backup file to data directory
  - [ ] Start Redis, verify data
  - [ ] Run consistency checks
- [ ] Document restore time objective (RTO): 30 minutes
- [ ] Document recovery point objective (RPO): 1 hour

#### Day 5: Incident Response

- [ ] Review incident response playbook:
  ```bash
  cat /home/setup/infrafabric/docs/INCIDENT_RESPONSE_PLAYBOOK.md
  ```
- [ ] Understand escalation path:
  1. Monitor alert → investigate locally
  2. Found issue → page on-call engineer
  3. P0 incident → page on-call manager + escalate to leadership
- [ ] Practice key scenarios:
  - [ ] "API latency spike" → Check Redis memory, API logs, agent health
  - [ ] "Redis memory full" → Check key sizes, TTLs, eviction policy
  - [ ] "Task claiming failure" → Check Redis connectivity, queue state
- [ ] Know who to call:
  - **Project Lead:** Danny Stocker (@dannystocker)
  - **On-Call Rotation:** Check on-call schedule in Slack
  - **Infrastructure:** StackCP support for server issues

**Success Criteria:**
- Can deploy to staging environment
- Can read and interpret monitoring dashboards
- Understand backup and recovery procedures
- Know incident response escalation path
- Have practiced at least 2 incident scenarios

---

### WEEK 6: Hands-On Operations & Handoff

**Goal:** Take operational responsibility with oversight; document gaps; verify readiness.

**Time Commitment:** 15-20 hours

#### Day 1-2: Supervised Operations

- [ ] **Task 1: Deploy new version to staging**
  - [ ] Create release branch: `git checkout -b release/v1.x.x`
  - [ ] Update version number and CHANGELOG.md
  - [ ] Create PR, get code review from project lead
  - [ ] Merge to main
  - [ ] Tag release: `git tag -a v1.x.x -m "Release v1.x.x"`
  - [ ] Verify staging deployment succeeds
  - [ ] Run smoke tests: Basic API calls, auth flow, task posting
  - [ ] **Supervisor:** Danny Stocker reviews deployment

- [ ] **Task 2: Handle a simulated incident**
  - [ ] Supervisor creates test scenario (e.g., "Redis memory spike")
  - [ ] You investigate: Check logs, metrics, Redis state
  - [ ] Identify root cause (e.g., missing TTL on a key)
  - [ ] Propose solution (e.g., "Clean up old sessions, add TTL")
  - [ ] Implement fix, verify in staging
  - [ ] **Supervisor:** Validates your diagnosis and solution

#### Day 3: Code Contribution

- [ ] **Task: Fix or improve something in codebase**
  - [ ] Identify small improvement (documentation, test, code cleanup)
  - [ ] Create feature branch: `git checkout -b feature/description`
  - [ ] Make changes, follow code style (see CONTRIBUTING.md)
  - [ ] Add tests for your change
  - [ ] Run full test suite: `pytest tests/ -v`
  - [ ] Create PR with clear description
  - [ ] Respond to review feedback
  - [ ] Merge PR after approval
  - [ ] **Success criteria:** PR merged to main

#### Day 4: Knowledge Gap Assessment

- [ ] **Document areas of uncertainty:**
  - [ ] Which subsystems still feel unclear?
  - [ ] Which procedures do you need more practice on?
  - [ ] Which areas would benefit from pairing with an expert?
- [ ] **Create improvement list:**
  - [ ] Update KNOWLEDGE_TRANSFER.md with your feedback
  - [ ] Suggest new documentation or runbooks
  - [ ] Identify training gaps for new maintainers
- [ ] **Schedule follow-up sessions:**
  - [ ] Weekly 1-on-1s with project lead (first month)
  - [ ] Access to Slack/Discord for async help
  - [ ] Scheduled pairing on complex tasks

#### Day 5: Readiness Validation & Handoff

- [ ] **Readiness Assessment:**
  - [ ] Can you explain S2 architecture to a new engineer? (Self-test)
  - [ ] Can you respond to a 401 Unauthorized error? (Checklist from common scenarios)
  - [ ] Can you deploy a hotfix to production? (Supervised)
  - [ ] Can you investigate a Redis memory issue? (Supervised)
  - [ ] All "Week 1-5" success criteria met? (Self-check)

- [ ] **Handoff Documentation:**
  - [ ] Update SESSION-RESUME.md with your status
  - [ ] Document any gaps in this knowledge transfer checklist
  - [ ] Create PRs for any documentation improvements

- [ ] **Access Verification:**
  - [ ] GitHub write access confirmed
  - [ ] Vault secrets access confirmed
  - [ ] Redis production access (read-only) confirmed
  - [ ] Grafana/Prometheus dashboards accessible
  - [ ] On-call rotation added (with backup)

- [ ] **Final Signoff:**
  - [ ] Project lead confirms readiness
  - [ ] Supervisor approves solo production access
  - [ ] First incident handled independently (with async support)

---

## CRITICAL KNOWLEDGE AREAS

### A. Security (P0 - Must Master Before Production Access)

**Why This Matters:** InfraFabric handles cryptographic keys, OAuth tokens, and can control physical systems (drones, energy grids). Security failures could allow attackers to compromise agent identities, forge messages, or execute dangerous commands.

**Key Concepts:**

1. **Ed25519 Cryptographic Identity**
   - Every agent has a unique keypair stored in Redis
   - Private key: Agent's identity proof (never transmitted)
   - Public key: Registry allows other agents to verify signatures
   - Compromise: If private key leaks, attacker can impersonate agent
   - Mitigation: Keys stored in Vault, never in code/git

2. **Message Signing & Verification**
   - All inter-agent messages are signed (SHA-256 hash + Ed25519 signature)
   - Signature verification proves message authenticity (wasn't forged or altered)
   - Audit trail: Every signature verification logged in Redis
   - Attack: Without verification, attacker could inject fake commands

3. **OAuth PKCE Flow**
   - PKCE (Proof Key for Code Exchange) prevents authorization code interception
   - User gives password to OAuth provider, not InfraFabric (better security)
   - InfraFabric receives access token + refresh token
   - Tokens stored encrypted in Redis, never in cookies (HTTPS-only)
   - Token expiry triggers automatic refresh before session expires

4. **Rate Limiting & Abuse Prevention**
   - API rate limit: 100 requests/min per user
   - Signature verification failures: Alert after 10/min per agent
   - Failed OAuth attempts: Lock account after 5 failures in 15 min
   - Command rate limit: Guardian vets dangerous commands (e.g., Drone Kill)

**Files to Study:**
- `/home/setup/infrafabric/ED25519_IMPLEMENTATION_FINAL.md`
- `/home/setup/infrafabric/SIGNATURE_VERIFICATION_SUMMARY.md`
- `/home/setup/infrafabric/OAUTH_PKCE_IMPLEMENTATION_SUMMARY.md`
- `/home/setup/infrafabric/docs/IF_EMOTION_THREAT_MODEL.md`
- Source: `/home/setup/infrafabric/src/core/security/`
- Source: `/home/setup/infrafabric/src/core/auth/`

**Critical Files to Know:**
- `/home/setup/infrafabric/src/core/security/ed25519_identity.py` (B21)
- `/home/setup/infrafabric/src/core/security/message_signing.py` (B22)
- `/home/setup/infrafabric/src/core/security/signature_verification.py` (B23)
- `/home/setup/infrafabric/src/core/auth/oauth_pkce.py` (B31)

**Test These:**
```bash
pytest tests/test_security_*.py -v
pytest tests/test_auth_*.py -v
pytest tests/test_ed25519_*.py -v
pytest tests/test_oauth_*.py -v
```

---

### B. Infrastructure (P0 - Must Master Before Deployment)

**Why This Matters:** Misconfigured infrastructure can cause performance issues, data loss, or security breaches. You need to understand each component.

**Key Components:**

1. **Redis Cluster**
   - Data store: Agent state, OAuth tokens, task queues
   - Task bus: FIFO lists for task posting/claiming
   - Pub/Sub: Cross-swarm messaging
   - Streams: Audit logs, event history
   - Memory management: Eviction policy, TTLs
   - Persistence: RDB snapshots, AOF (append-only file)
   - Cluster: Replication, failover, sharding

2. **ChromaDB**
   - Vector database for semantic memory
   - Stores embeddings (semantic context) for agents
   - Enables similarity search ("find agents with relevant knowledge")
   - Performance: < 50ms for 1M-item embeddings

3. **Docker Compose Orchestration**
   - Defines all services: API server, Redis, ChromaDB, monitoring
   - Environment variables: Configure secrets, ports, replica counts
   - Health checks: Ensure services are up before serving traffic
   - Networks: Isolated network for inter-service communication

4. **TLS/SSL with Let's Encrypt**
   - HTTPS on all external APIs (OAuth, user API)
   - Certificate renewal: Automatic via certbot
   - Self-signed for internal services (between containers)

5. **Secrets Management (Vault)**
   - OAuth client IDs/secrets
   - Database credentials
   - API keys
   - Private key encryption keys
   - Access control: Only authorized agents can read

6. **Monitoring (Prometheus + Grafana)**
   - Prometheus: Scrapes metrics from services
   - Grafana: Visualizes metrics, creates dashboards
   - Alerts: Pagerduty integration for critical issues

**Files to Study:**
- `/home/setup/infrafabric/DEPLOYMENT-COMPLETE-2025-11-29.md`
- `/home/setup/infrafabric/PROXMOX-OPENWEBUI-DEPLOYMENT.md`
- `/home/setup/infrafabric/docker-compose.yml`
- `/home/setup/infrafabric/Dockerfile`
- `/home/setup/infrafabric/config/` (configuration files)

**Critical Files to Know:**
- `/home/setup/infrafabric/docker-compose.yml` (service definitions)
- `/home/setup/infrafabric/Dockerfile` (API server build)
- `/home/setup/infrafabric/config/infrafabric.schema.json` (B17 - config validation)
- `/home/setup/infrafabric/nginx/nginx.conf` (reverse proxy, SSL)

**Test These:**
```bash
# Docker Compose
docker-compose config  # Validate syntax
docker-compose up -d   # Start services
docker-compose logs -f # View logs
docker-compose down    # Stop services

# Redis
redis-cli PING
redis-cli INFO

# Metrics
curl http://localhost:9090/api/v1/targets  # Prometheus targets
```

---

### C. Swarm Coordination (P1 - Important for Debugging)

**Why This Matters:** Swarm coordination is how 45 agents work together. Understanding it helps you debug why tasks fail, agents don't respond, or context isn't shared.

**Key Concepts:**

1. **S2 Redis Bus Protocol**
   - Agents post tasks to Redis queues
   - Other agents discover and claim tasks
   - Task data includes: agent ID, task type, parameters, deadline
   - Results posted back to Redis, agent polls for completion
   - Background communication: Agents can exchange context while main request pending

2. **Task Lifecycle**
   - **Posting:** Agent A writes task to `queue:pending:task-id`
   - **Discovery:** Agent B polls queues (BRPOP with timeout)
   - **Claiming:** Agent B locks task with SET `task:task-id:owner = agent-b`
   - **Execution:** Agent B processes task
   - **Results:** Agent B writes results to `queue:results:task-id`
   - **Completion:** Agent A retrieves results, task moved to archive
   - **Timeout:** If task unclaimed after 300s, marked failed, retried

3. **Cross-Swarm Messaging**
   - IF.packet: Cryptographic envelope (signature + timestamp + payload)
   - Pub/Sub: Redis PUBLISH to channel, other agents SUBSCRIBE
   - Background communication: Doesn't block main request
   - Use case: Agent A needs context from Agent B before completing task

4. **Context Sharing**
   - Agents store context vectors (embeddings) in ChromaDB
   - Other agents query similar contexts ("find agents with knowledge of X")
   - Enables knowledge transfer: New agent learns from experienced agents
   - Performance: Context lookup < 50ms (cached in Redis)

5. **Timeout Prevention**
   - Claude API timeout: 300 seconds max
   - Tasks may take longer than 300s
   - Solution: Background communication + status polling
   - Agent A: Posts long task, continues processing other requests
   - Agent B: Completes long task asynchronously
   - Agent A: Polls for results, returns to user when ready

**Files to Study:**
- `/home/setup/infrafabric/docs/protocols/CROSS_SWARM_COORDINATION.md`
- `/home/setup/infrafabric/docs/protocols/CLAUDE_MAX_CONTEXT_SHARING.md`
- `/home/setup/infrafabric/SWARM_INTEGRATION_SYNTHESIS.md`
- Source: `/home/setup/infrafabric/src/core/logistics/`

**Critical Files to Know:**
- `/home/setup/infrafabric/src/core/logistics/redis_swarm_coordinator.py` (core logic)
- `/home/setup/infrafabric/src/core/logistics/task_posting.py` (B12)
- `/home/setup/infrafabric/src/core/logistics/task_claiming.py` (B13)
- `/home/setup/infrafabric/src/core/logistics/cross_swarm_messaging.py` (B14)

**Test These:**
```bash
pytest tests/test_task_posting.py -v
pytest tests/test_task_claiming.py -v
pytest tests/test_cross_swarm_messaging.py -v
pytest tests/test_timeout_prevention.py -v
```

---

### D. Testing (P1 - Important for Contributions)

**Why This Matters:** Tests catch bugs before production. You should know how to write tests, run them, and interpret failures.

**Test Levels:**

1. **Unit Tests** (lowest level)
   - Test single function in isolation
   - Mock external dependencies (Redis, OAuth providers)
   - Fast: 100s of tests run in seconds
   - Example: Test Ed25519 key generation

2. **Integration Tests** (mid level)
   - Test multiple components together
   - Use real Redis instance (test database)
   - Slower: Seconds to minutes
   - Example: Test full OAuth flow (app → Redis → OAuth provider)

3. **Security Tests** (P0)
   - Test cryptographic operations
   - Test signature verification edge cases
   - Test authentication/authorization
   - Example: Can't forge a signature without private key

4. **Resilience Tests** (P1)
   - Test failure scenarios
   - Inject failures (kill Redis, timeout OAuth provider)
   - Verify graceful degradation
   - Example: Task completes even if Redis connection drops briefly

5. **Performance Tests** (P2)
   - Benchmark critical paths
   - Monitor latency, throughput, memory usage
   - Example: Signature verification < 10ms, task claiming < 50ms

**Files to Study:**
- `/home/setup/infrafabric/docs/testing/INTEGRATION_TEST_PLAN.md`
- `/home/setup/infrafabric/docs/testing/` (all test documentation)
- Source: `/home/setup/infrafabric/tests/` (test files)

**Test Directory Structure:**
```
tests/
├── test_ed25519_identity.py       # Security tests
├── test_message_signing.py        # Security tests
├── test_signature_verification.py # Security tests
├── test_oauth_pkce_flow.py        # Auth tests
├── test_oauth_google.py           # Provider tests
├── test_oauth_github.py           # Provider tests
├── test_oauth_azure.py            # Provider tests
├── test_task_posting.py           # Coordination tests
├── test_task_claiming.py          # Coordination tests
├── test_cross_swarm_messaging.py  # Coordination tests
└── test_timeout_prevention.py     # Resilience tests
```

**Run Tests:**
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_oauth_pkce_flow.py -v

# Specific test function
pytest tests/test_oauth_pkce_flow.py::test_pkce_code_verifier_generation -v

# With coverage report
pytest tests/ --cov=src --cov-report=html

# With output capture (show print statements)
pytest tests/ -v -s
```

---

### E. Documentation (P2 - Important for Maintenance)

**Why This Matters:** InfraFabric is complex. Good documentation helps future maintainers (including you in 6 months) understand decisions, architecture, and procedures.

**Documentation Standards:**

1. **README Files**
   - What is this component?
   - How do you use it?
   - What are the key files?
   - Code examples

2. **Architecture Docs**
   - System design (diagrams, text)
   - Component interaction
   - Data flow
   - Deployment architecture

3. **Runbooks**
   - Step-by-step procedures
   - Success criteria
   - Troubleshooting tips
   - Escalation path

4. **Security Docs**
   - Threat models
   - Attack scenarios + mitigations
   - Key rotation procedures
   - Access control policies

5. **Test Documentation**
   - Test strategy (unit/integration/security/resilience)
   - How to run tests
   - Interpreting test failures
   - Adding new tests

**Files to Study:**
- `/home/setup/infrafabric/docs/` (all documentation)
- `/home/setup/infrafabric/CONTRIBUTING.md` (contribution guidelines)
- `/home/setup/infrafabric/CHANGELOG.md` (release history)

**Documentation Tasks:**
- [ ] Update CHANGELOG.md for your changes
- [ ] Update README.md if you change a major component
- [ ] Create runbooks for procedures you document
- [ ] Update this KNOWLEDGE_TRANSFER.md with gaps you find

---

## KEY FILES REFERENCE

### Must Know (Read First)

| File | Purpose | Time | Link |
|------|---------|------|------|
| README.md | Project overview, quick start | 5 min | /home/setup/infrafabric/README.md |
| MISSION_REPORT_2025-11-30.md | B1-B45 deliverables, all completed tasks | 90 min | /home/setup/infrafabric/MISSION_REPORT_2025-11-30.md |
| agents.md | Complete agent catalog (A1-B45), capabilities | 90 min | /home/setup/infrafabric/agents.md |
| ED25519_IMPLEMENTATION_FINAL.md | Cryptographic identity system | 60 min | /home/setup/infrafabric/ED25519_IMPLEMENTATION_FINAL.md |
| SIGNATURE_VERIFICATION_SUMMARY.md | Message signing & verification | 60 min | /home/setup/infrafabric/SIGNATURE_VERIFICATION_SUMMARY.md |
| OAUTH_PKCE_IMPLEMENTATION_SUMMARY.md | OAuth authentication flow | 60 min | /home/setup/infrafabric/OAUTH_PKCE_IMPLEMENTATION_SUMMARY.md |
| QUICK_START_SIGNATURE_VERIFICATION.md | Practical examples | 30 min | /home/setup/infrafabric/QUICK_START_SIGNATURE_VERIFICATION.md |

### Should Know (Read Later)

| File | Purpose | Link |
|------|---------|------|
| SWARM_INTEGRATION_SYNTHESIS.md | S2 architecture, Redis bus, task coordination | /home/setup/infrafabric/SWARM_INTEGRATION_SYNTHESIS.md |
| SECURITY_IMPLEMENTATION_SUMMARY.md | Ed25519, signatures, OAuth, sandbox | /home/setup/infrafabric/SECURITY_IMPLEMENTATION_SUMMARY.md |
| DEPLOYMENT-COMPLETE-2025-11-29.md | Production deployment checklist | /home/setup/infrafabric/DEPLOYMENT-COMPLETE-2025-11-29.md |
| SESSION-RESUME.md | Current session status, blockers | /home/setup/infrafabric/SESSION-RESUME.md |
| docs/protocols/CROSS_SWARM_COORDINATION.md | S2 Redis Bus, task posting/claiming | /home/setup/infrafabric/docs/protocols/CROSS_SWARM_COORDINATION.md |
| docs/protocols/CLAUDE_MAX_CONTEXT_SHARING.md | Context vectors, background communication | /home/setup/infrafabric/docs/protocols/CLAUDE_MAX_CONTEXT_SHARING.md |
| docs/testing/INTEGRATION_TEST_PLAN.md | Test strategy (6-phase), test patterns | /home/setup/infrafabric/docs/testing/INTEGRATION_TEST_PLAN.md |

### Nice to Know (Reference)

| File | Purpose | Link |
|------|---------|------|
| docs/IF_PROTOCOL_REGISTRY.md | All InfraFabric protocols documented | /home/setup/infrafabric/docs/IF_PROTOCOL_REGISTRY.md |
| docs/IF_EMOTION_THREAT_MODEL.md | Security threat model, future threats | /home/setup/infrafabric/docs/IF_EMOTION_THREAT_MODEL.md |
| DOCUMENTATION_SUMMARY.md | Map of all docs by category | /home/setup/infrafabric/DOCUMENTATION_SUMMARY.md |

### Source Code (By Component)

| Component | Key Files | Location |
|-----------|-----------|----------|
| **Security** | ed25519_identity.py, message_signing.py, signature_verification.py | /home/setup/infrafabric/src/core/security/ |
| **Auth** | oauth_pkce.py, oauth_providers.py | /home/setup/infrafabric/src/core/auth/ |
| **Logistics** | redis_swarm_coordinator.py, task_posting.py, task_claiming.py | /home/setup/infrafabric/src/core/logistics/ |
| **Resilience** | timeout_prevention.py, context_sharing.py | /home/setup/infrafabric/src/core/resilience/ |
| **Registry** | llm_registry.py, agent_registry.py | /home/setup/infrafabric/src/core/registry/ |
| **Audit** | audit_logger.py, event_formatter.py | /home/setup/infrafabric/src/core/audit/ |

---

## COMMON SCENARIOS & RESPONSES

### Scenario 1: User Reports "401 Unauthorized"

**Symptoms:** User logs in, sees "401 Unauthorized" error

**Diagnosis:**
```bash
# Check 1: Is user's OAuth token expired?
redis-cli HGETALL "user:{email}:tokens"
# Look for "access_token_expires_at" field

# Check 2: Is Redis up?
redis-cli PING

# Check 3: Is OAuth provider responding?
curl -I https://accounts.google.com
curl -I https://github.com
curl -I https://login.microsoft.com
```

**Root Cause Analysis:**
- **Token expired:** Refresh token should auto-refresh, but Redis may be down
- **OAuth provider down:** Users can't refresh tokens
- **Redis down:** Can't access token store

**Solution:**
1. If token expired: Guide user to re-authenticate
   ```bash
   # In browser: http://your-app/auth/logout (clears session)
   # Then: http://your-app/auth/google (re-authenticate)
   ```
2. If OAuth provider down: Wait for provider to recover, notify users
3. If Redis down: See "Scenario 2: High Redis Memory Usage" below

**Prevention:**
- Monitor OAuth provider health (status pages)
- Monitor Redis availability
- Set alerts on token refresh failures
- Verify OAuth credentials at startup

---

### Scenario 2: High Redis Memory Usage

**Symptoms:** Redis memory usage > 80%, performance degrading

**Diagnosis:**
```bash
# Check memory usage
redis-cli INFO memory
# Look for "used_memory_human" and "used_memory_peak_human"

# Find large keys
redis-cli --bigkeys
# Shows keys using most memory

# Check key types and sizes
redis-cli --memkeys
# Shows memory per key type

# Check TTLs
redis-cli KEYS "*" | while read key; do redis-cli TTL "$key"; done | grep -E "^[0-9]+$" | wc -l
# Shows how many keys have no TTL (permanent)
```

**Root Cause Analysis:**
- **Missing TTL:** Keys stored permanently instead of expiring
- **Eviction policy:** Old keys not removed when memory full
- **Task queue backlog:** Too many completed tasks archived
- **Audit logs:** Too many events stored

**Solution:**
1. **Immediate:** Increase Redis memory allocation
   ```bash
   # In docker-compose.yml, update redis service:
   # redis:
   #   command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
   ```

2. **Add TTLs to permanent keys:**
   ```bash
   # Find keys without TTL
   redis-cli KEYS "*" | while read key; do
     ttl=$(redis-cli TTL "$key")
     if [ "$ttl" -eq -1 ]; then
       echo "Key without TTL: $key";
     fi
   done

   # Add TTL (example: 24 hours = 86400 seconds)
   redis-cli EXPIRE "key-name" 86400
   ```

3. **Adjust eviction policy:**
   ```bash
   # In redis.conf or docker-compose.yml:
   # maxmemory-policy allkeys-lru  # Remove least recently used keys
   ```

4. **Archive old completed tasks:**
   ```bash
   # Move completed tasks to cold storage
   redis-cli ZRANGE "queue:completed" 0 -1 BYSCORE 0 $(date -d '7 days ago' +%s) | \
     xargs -I {} redis-cli MOVE {} 1  # Move to database 1 (cold storage)
   ```

**Prevention:**
- Set TTL on all keys at creation time
- Monitor memory usage weekly
- Set alert at 70% capacity
- Regular archive of old completed tasks

---

### Scenario 3: Ed25519 Signature Verification Failure

**Symptoms:** Agent reports "Signature verification failed" error

**Diagnosis:**
```bash
# Check 1: Is agent's public key registered?
redis-cli HGETALL "registry:agents:agent-id:public-key"

# Check 2: Has agent's key been rotated recently?
redis-cli LRANGE "audit:key_rotations:agent-id" -5 -1

# Check 3: Is message hash correct?
# (Compare message hash with signature in audit log)
redis-cli HGETALL "audit:signature_verifications:agent-id" | tail -20

# Check 4: Is message corrupted?
# (Hash mismatch indicates message was altered after signing)
```

**Root Cause Analysis:**
- **Key not registered:** Agent generated new key but didn't register public key
- **Key rotation in progress:** Old key removed before all agents updated
- **Message tampering:** Message altered after signing (network corruption or attack)
- **Clock skew:** Agent clock ahead/behind, timestamp validation fails

**Solution:**
1. **Verify agent public key:**
   ```bash
   # Check what key is registered
   redis-cli HGET "registry:agents:{agent-id}" "public-key"

   # Get agent's current key
   # (From agent logs or manual check)

   # If mismatch, re-register:
   redis-cli HSET "registry:agents:{agent-id}" "public-key" "new-public-key"
   ```

2. **Check message hash:**
   ```bash
   # From audit log, get message hash
   # Verify with: SHA256(message) == reported_hash
   python << 'EOF'
   import hashlib
   message = b"..."  # From audit log
   hash = hashlib.sha256(message).hexdigest()
   print(f"Hash: {hash}")
   EOF
   ```

3. **Synchronize clocks:**
   ```bash
   # Check agent clock vs server clock
   ntpq -p  # Check NTP status

   # If drift > 5 seconds, restart NTP
   systemctl restart ntp
   ```

**Prevention:**
- Monitor signature failure rate (alert if > 10/min per agent)
- Monitor key rotation events
- Validate agent clocks (NTP sync)
- Log all signature verifications

---

### Scenario 4: Task Claiming Failure (Tasks Stuck in Queue)

**Symptoms:** Tasks posted but never claimed or executed

**Diagnosis:**
```bash
# Check 1: Are there pending tasks?
redis-cli LLEN "queue:pending"

# Check 2: Are agents running?
redis-cli SMEMBERS "registry:agents:active"

# Check 3: Why isn't agent claiming?
redis-cli LOGS | grep -i "task.*claim.*error"

# Check 4: Is Redis connection broken?
redis-cli PING

# Check 5: Check queue state
redis-cli LRANGE "queue:pending" 0 -1 | head -5
```

**Root Cause Analysis:**
- **No agents running:** All agents crashed or stopped
- **Redis connection lost:** Agents can't access queue
- **Claiming timeout:** Agent claims task but crashes before completion
- **Task format invalid:** Task doesn't match expected schema
- **Agent filter mismatch:** Agent's task type filter doesn't match posted task type

**Solution:**
1. **Verify agents are running:**
   ```bash
   # Check Docker containers
   docker-compose ps | grep agent

   # If any are down:
   docker-compose up -d agent  # Restart
   docker-compose logs -f agent  # Check logs
   ```

2. **Verify Redis connection:**
   ```bash
   redis-cli PING  # Should return PONG
   redis-cli INFO  # Should show stats
   ```

3. **Check task format:**
   ```bash
   # Get a pending task
   redis-cli LPOP "queue:pending"

   # Should be valid JSON matching task schema
   # See: /home/setup/infrafabric/schemas/task/v1.0.schema.json
   ```

4. **Check agent filters:**
   ```bash
   # Get agent capabilities
   redis-cli HGETALL "registry:agents:{agent-id}:capabilities"

   # Get posted task type
   redis-cli LRANGE "queue:pending" 0 0
   # Extract "task_type" field

   # Verify agent's filter includes task type
   ```

5. **Manual task claiming (debugging):**
   ```python
   from core.logistics import TaskClaimant
   claimant = TaskClaimant()
   task = claimant.claim_task(timeout=30)
   if task:
       print(f"Claimed: {task}")
       # Process task...
       claimant.complete_task(task.id, results={...})
   else:
       print("No tasks available")
   ```

**Prevention:**
- Monitor queue depth (alert if > 100 pending)
- Monitor agent health (alert if < expected count)
- Log all claiming attempts and failures
- Set timeout on claimed tasks (auto-release if not completed in X seconds)

---

### Scenario 5: Deployment Rollback Needed

**Symptoms:** New deployment has bugs, need to revert

**Diagnosis:**
```bash
# Check what's deployed
git log --oneline | head -5

# Check deployment status
docker-compose ps

# Check application logs
docker-compose logs api | tail -50
```

**Process:**

1. **Stop new deployment:**
   ```bash
   # Identify image version
   docker-compose ps api | grep -o "image.*"

   # Get previous version from git
   git log --oneline | head -2
   # Note the commit hash of previous version
   ```

2. **Restore previous version:**
   ```bash
   # Checkout previous version
   git revert HEAD  # Create rollback commit (preferred)
   # OR
   git reset --hard HEAD~1  # Undo previous commit (destructive)

   # Rebuild and deploy
   docker-compose down
   docker-compose up -d
   ```

3. **Restore database (if schema changed):**
   ```bash
   # Check if Redis snapshot exists for this version
   ls -lh /backups/redis/

   # Restore from backup
   redis-cli SHUTDOWN
   cp /backups/redis/redis-backup-YYYY-MM-DD.rdb /data/redis/dump.rdb
   redis-cli  # Restart
   ```

4. **Verify rollback:**
   ```bash
   # Run smoke tests
   curl http://localhost:5000/health
   curl http://localhost:5000/api/agents

   # Check metrics
   # Login to Grafana, verify normal metrics
   ```

5. **Communicate rollback:**
   - Slack: Announce rollback, ETA for fix
   - Status page: Update status to "degraded" or "resolved"
   - Users: Send email explaining issue and workaround

6. **Post-mortem:**
   - [ ] What was the bug?
   - [ ] How did testing miss it?
   - [ ] How to prevent in future?
   - [ ] Document in CHANGELOG.md

---

### Scenario 6: OAuth Provider Unavailable

**Symptoms:** Users can't authenticate ("OAuth provider unavailable" error)

**Diagnosis:**
```bash
# Check provider status
curl -I https://accounts.google.com  # Should return 200
curl -I https://github.com           # Should return 200
curl -I https://login.microsoft.com  # Should return 200

# Check if tokens can be refreshed
# (OAuth calls may still work if cached)

# Check logs
docker-compose logs auth | grep -i "oauth\|error" | tail -20
```

**Root Cause Analysis:**
- **Provider down:** Google/GitHub/Azure experiencing outage
- **Network connectivity:** Your infrastructure can't reach provider
- **OAuth credentials invalid:** Client ID or secret changed/expired
- **Rate limit exceeded:** Too many auth requests

**Solution (Immediate):**
1. **Notify users:** Post message that authentication is temporarily unavailable
2. **Extend existing tokens:** Ask admins to manually extend session TTLs
   ```bash
   redis-cli HGETALL "user:{email}:session"
   redis-cli EXPIRE "user:{email}:session" 86400  # Extend 24 hours
   ```
3. **Fallback auth:** If available, offer username/password auth (temporary)

**Solution (Short-term):**
1. **Verify OAuth credentials:**
   ```bash
   vault kv get secret/oauth/google
   vault kv get secret/oauth/github
   vault kv get secret/oauth/azure

   # Log into provider (Google/GitHub/Azure) and verify credentials match
   ```

2. **Check network connectivity:**
   ```bash
   traceroute accounts.google.com
   ping github.com
   # Check firewall rules
   ```

3. **Monitor OAuth errors:**
   ```bash
   docker-compose logs auth | grep -i "error\|failed" | tail -50
   ```

**Prevention:**
- Set up monitoring for OAuth provider health (status pages)
- Test OAuth endpoints regularly (synthetic monitoring)
- Have fallback authentication method (optional)
- Document expected error messages and troubleshooting steps

---

## PRODUCTION ACCESS CHECKLIST

**Before granting production access, verify:**

### Access Levels

- [ ] **GitHub Write Access**
  - Can push to main branch (with review)
  - Can merge PRs (with approval)
  - Can create releases and tags

- [ ] **Vault Secrets Access**
  - Read-only to non-critical secrets (test credentials)
  - Read-only to OAuth credentials
  - No access to master encryption keys

- [ ] **Redis Production Access**
  - Read-only to production instance (for debugging)
  - Write access only on staging instance
  - No access to delete critical keys

- [ ] **Grafana/Prometheus Access**
  - Can view all dashboards
  - Can create custom queries (read-only)
  - No access to modify dashboards (suggest via PR)

- [ ] **StackCP Server Access**
  - SSH access to staging server only
  - SSH access to production server with approval + logging
  - Docker access for log viewing, no container restart without approval

- [ ] **On-Call Rotation**
  - Added to on-call schedule
  - Configured PagerDuty alerts
  - Tested alert delivery (phone call, SMS, email)

### Documentation

- [ ] **Runbooks Completed**
  - Deployment runbook reviewed
  - Incident response playbook reviewed
  - Backup/restore procedure practiced
  - Rollback procedure tested

- [ ] **Architecture Understanding**
  - Can explain S2 architecture in 5 minutes
  - Can draw system diagram on whiteboard
  - Can identify all critical components

- [ ] **Security Knowledge**
  - Understand Ed25519 identity system
  - Can verify a signature manually
  - Know how to rotate keys
  - Know OAuth flow and token refresh

- [ ] **Incident Response**
  - Know escalation path
  - Know who to page for different scenarios
  - Practiced at least 2 incident simulations
  - Know how to declare a P0 incident

### Testing

- [ ] **All Unit Tests Pass**
  ```bash
  pytest tests/ -v --tb=short
  ```

- [ ] **Deployment Test Successful**
  - Deployed to staging successfully
  - Ran smoke tests
  - Verified metrics and monitoring

- [ ] **OAuth Test Successful**
  - Tested with all 3 providers (Google, GitHub, Azure)
  - Tested token refresh
  - Tested error scenarios

- [ ] **Security Tests Pass**
  ```bash
  pytest tests/test_security*.py tests/test_auth*.py -v
  ```

### Sign-Off

- [ ] Project lead reviewed this checklist
- [ ] Project lead confirmed readiness
- [ ] Security review completed (if required)
- [ ] New maintainer confirmed understanding

---

## CONTACTS & ESCALATION

### Project Lead

**Name:** Danny Stocker
**GitHub:** @dannystocker
**Email:** [from GitHub profile]
**Slack:** @danny
**Availability:** Weekdays 9am-5pm PT, async on Slack

**Escalation Path:**
1. Ask in Slack #infrafabric-dev (for design questions)
2. Ask in Slack #infrafabric-ops (for operations questions)
3. Post GitHub issue (for non-urgent bugs/features)
4. Page on-call (for P0 incidents, see below)

### Security Lead

**TBD** - Assign based on team structure

### Infrastructure Lead

**TBD** - Assign based on team structure

### On-Call Rotation

**Where:** PagerDuty (or equivalent)
**Schedule:** 24/7 coverage
**Escalation:**
- L1 (you): Initial response, debugging
- L2 (on-call backup): If you can't resolve in 30 min
- L3 (project lead): If L2 can't resolve in 30 min, or P0 incident

**Incident Severity:**

| Severity | Definition | Response Time | Example |
|----------|-----------|---|---------|
| **P0** | Security breach, production down | 15 min | Redis down, signature verification bypass, unauthorized access |
| **P1** | Major feature broken, degraded performance | 1 hour | OAuth login broken, 50% error rate, latency > 1s |
| **P2** | Minor feature broken, cosmetic issues | 4 hours | One OAuth provider broken, minor UI bug |
| **P3** | Documentation, housekeeping | Next business day | Typo in docs, test cleanup |

---

## POST-TRANSFER VALIDATION

### Readiness Assessment (Week 6)

Complete these self-assessments to verify readiness:

#### 1. Architecture Understanding
**Test:** Explain S2 architecture without referring to documents

- [ ] Can explain 5 core components (Redis, ChromaDB, Docker, TLS, Vault)
- [ ] Can describe task lifecycle (posting → claiming → completion)
- [ ] Can draw system diagram
- [ ] Can identify potential bottlenecks
- [ ] Can explain how agents coordinate without blocking

**Success Criteria:** Project lead confirms understanding

#### 2. Incident Response
**Test:** Respond to simulated incident

- [ ] Can identify root cause (given error message)
- [ ] Can determine severity (P0/P1/P2)
- [ ] Can execute first troubleshooting step
- [ ] Know who to escalate to
- [ ] Can communicate status to team

**Success Criteria:** Can respond within 5 minutes, take appropriate action

#### 3. Deployment
**Test:** Deploy new version to staging

- [ ] Can create release branch from main
- [ ] Can update version number and CHANGELOG
- [ ] Can push to staging environment
- [ ] Can run smoke tests
- [ ] Can verify metrics in Grafana

**Success Criteria:** Deployment succeeds, tests pass, metrics normal

#### 4. Code Contribution
**Test:** Contribute code to repository

- [ ] Can write Python code following project style (black, flake8)
- [ ] Can write unit tests
- [ ] Can run tests locally
- [ ] Can create PR with clear description
- [ ] Can respond to review feedback

**Success Criteria:** PR merged to main

#### 5. Documentation
**Test:** Update documentation

- [ ] Can update README with new feature
- [ ] Can add architecture diagram
- [ ] Can write runbook for procedure
- [ ] Can update this KNOWLEDGE_TRANSFER.md with gaps

**Success Criteria:** Documentation is clear, accurate, helpful

### Knowledge Gap Assessment

After Week 6, document any remaining gaps:

```markdown
## Knowledge Transfer Completion Report

### Gaps Identified
- [ ] Area: [What's unclear?]
  - [ ] Root cause: [Why unclear?]
  - [ ] Solution: [How to improve?]

### Recommendations for Future Maintainers
- [ ] Suggestion: [What should be documented better?]
- [ ] Suggestion: [What should be tested more?]

### Additional Training Needed
- [ ] Area: [Needs more practice]
  - [ ] Proposed: [Pair session with expert]

### Confidence Level
- [ ] Can maintain system alone? YES / NO / PARTIAL
- [ ] Confidence rating: 1-5 (1=low, 5=high): ___

### Sign-Off
- Trainee: [Your name] _______________
- Mentor: [Project lead] _______________
- Date: _______________
```

### Success Metrics

After 6 weeks, you should be able to:

1. **Answer Questions**
   - [ ] "What is S2?" → Explain architecture in < 2 min
   - [ ] "How does OAuth work?" → Draw flow diagram
   - [ ] "Agent claims task but crashes. What happens?" → Explain timeout mechanism
   - [ ] "Redis memory is 90%. What do I do?" → Know troubleshooting steps

2. **Handle Operations**
   - [ ] Deploy a release to staging/production
   - [ ] Investigate an incident (logs, metrics, Redis)
   - [ ] Roll back a broken deployment
   - [ ] Restore from backup
   - [ ] Monitor system health (dashboards)

3. **Develop**
   - [ ] Write unit tests for new code
   - [ ] Run full test suite
   - [ ] Follow code style (black, flake8)
   - [ ] Create PRs with clear descriptions
   - [ ] Respond to code review feedback

4. **Respond to P0 Incidents**
   - [ ] Page on-call within 2 minutes
   - [ ] Initial investigation within 5 minutes
   - [ ] Escalate if needed within 30 minutes
   - [ ] Post-mortem within 24 hours

---

## APPENDIX: Useful Commands

### Docker Compose

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Check service status
docker-compose ps

# Restart a service
docker-compose restart [service-name]

# Rebuild an image
docker-compose build [service-name]
```

### Redis

```bash
# Connect to Redis CLI
redis-cli

# Ping (verify connection)
PING

# Get all keys (careful in production!)
KEYS *

# Get key type
TYPE key-name

# Get key value (for strings)
GET key-name

# Get hash (for user data)
HGETALL key-name

# List queue contents
LRANGE queue-name 0 -1

# Get queue length
LLEN queue-name

# Set TTL on a key
EXPIRE key-name 86400

# Check TTL
TTL key-name

# View all keys and their TTLs
KEYS "*" | while read key; do echo -n "$key: "; TTL "$key"; done
```

### Python Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_oauth_pkce_flow.py -v

# Run specific test function
pytest tests/test_oauth_pkce_flow.py::test_code_verifier -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run with output capture (see print statements)
pytest tests/ -v -s

# Run with verbose error messages
pytest tests/ -v --tb=long
```

### Git

```bash
# Check status
git status

# View recent commits
git log --oneline | head -10

# Create feature branch
git checkout -b feature/description

# Stage changes
git add [file]
git add .  # All changed files

# Commit
git commit -m "Commit message"

# Push to origin
git push origin feature/description

# Create tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Monitoring

```bash
# Grafana
http://your-domain:3000

# Prometheus
http://your-domain:9090/api/v1/query

# Example Prometheus query
sum(rate(http_requests_total[5m])) by (endpoint)

# Health endpoints
curl http://localhost:5000/health
curl http://localhost:5000/metrics
```

---

## FINAL NOTES

**Remember:** This knowledge transfer is **not a test**. It's a guide to help you understand InfraFabric and become productive quickly.

- **Take breaks.** This is a lot of information. Pace yourself over 6 weeks.
- **Ask questions.** Don't hesitate to reach out to Danny or the team.
- **Document as you go.** If you find gaps in documentation, update them immediately.
- **Enjoy the complexity.** InfraFabric is a sophisticated system. Understanding it deeply is rewarding.

**Good luck!** 🚀

---

**Document ID:** `if://doc/knowledge-transfer/2025-11-30`
**Version:** 1.0
**Last Updated:** November 30, 2025
**Author:** Haiku Agent B45
**Status:** Production-Ready
