# Comprehensive Evaluation Prompt - InfraFabric & Swarm of Swarms (S²)

**Date:** 2025-11-12
**Evaluator:** GPT-5 Pro (or equivalent advanced model)
**Scope:** Complete system evaluation - Technical implementation + Process coordination

---

## Your Mission

You are evaluating **two interconnected systems**:
1. **InfraFabric (IF):** A production infrastructure orchestration platform
2. **Swarm of Swarms (S²):** A multi-session, multi-agent coordination process

**Your task:**
- **Evaluate** both technical quality and process efficiency
- **Debug** critical issues, edge cases, and failure modes
- **Iterate** on designs with concrete improvements
- **Roadmap** v1.1 → v2.0 → v3.0 evolution paths

---

## Part A: InfraFabric (IF) Technical Evaluation

### A.1: What Was Built (Past 24 Hours)

**Production Infrastructure Integrations:**
1. **vMix Integration** (7 modules)
   - NDI input/output integration
   - RTMP/SRT streaming control
   - PTZ camera control
   - Production switching automation
   - CLI interface
   - Adapter pattern
   - IF.bus orchestration

2. **OBS Integration** (7 modules)
   - NDI plugin integration
   - Streaming & Virtual Camera
   - Media & browser sources
   - Scene management
   - CLI interface
   - Adapter pattern
   - IF.bus orchestration

3. **Home Assistant Integration** (7 modules)
   - Camera → NDI bridge
   - Notifications & webhooks
   - Media players & TTS
   - Automations & scripts
   - CLI interface
   - Adapter pattern
   - IF.bus orchestration

**Integration Roadmap (96+ providers planned):**
- Cloud providers (AWS, Azure, GCP, etc.) - 20+
- SIP providers (Twilio, Telnyx, etc.) - 30+
- Payment providers (Stripe, PayPal, etc.) - 40+
- Chat platforms (WhatsApp, Telegram, Slack, WeChat, LINE, etc.) - 16+

**Architecture Principles:**
- **IF.witness:** Cryptographic provenance (Ed25519, hash chains)
- **IF.optimise:** Cost-aware routing and budget tracking
- **IF.ground:** Philosophy grounding (Wu Lun 五倫)
- **IF.bus:** Unified infrastructure control
- **IF.TTT:** Traceable, Transparent, Trustworthy

### A.2: Evaluation Questions (InfraFabric Technical)

#### A.2.1: Architecture Quality
1. **Adapter Pattern Evaluation:**
   - Are the base classes (VMixAdapter, OBSAdapter, HAAdapter) well-designed?
   - Do they properly abstract platform differences?
   - Are there missing methods that would be needed?
   - Rate the consistency across adapters (1-10)

2. **IF.bus Design:**
   - Is the unified orchestration layer scalable?
   - How will IF.bus handle 96+ providers?
   - Are there architectural bottlenecks?
   - Suggest improvements for multi-provider orchestration

3. **IF.witness Integration:**
   - Is cryptographic provenance properly integrated?
   - Are there gaps in logging coverage?
   - How should hash chains be validated?
   - Security vulnerabilities in witness implementation?

4. **IF.optimise Cost Tracking:**
   - Is cost tracking comprehensive?
   - Missing cost metrics?
   - How to optimize across 96+ providers?
   - Budget enforcement mechanisms?

#### A.2.2: Code Quality Assessment
Review these conceptual implementations:
- `src/integrations/vmix_*.py` (7 modules)
- `src/integrations/obs_*.py` (7 modules)
- `src/integrations/ha_*.py` (7 modules)
- `src/bus/*_bus_adapter.py` (3 adapters)
- `src/cli/*_commands.py` (3 CLI modules)

**Rate (1-10) and explain:**
1. **Code organization:** Module structure, separation of concerns
2. **Error handling:** Exception handling, retry logic, timeouts
3. **Testing strategy:** Unit tests, integration tests, mocks
4. **Documentation:** Docstrings, type hints, examples
5. **Performance:** Async/await usage, connection pooling, caching
6. **Security:** API key handling, injection prevention, validation

#### A.2.3: Integration Design
1. **vMix + OBS + HA Interoperability:**
   - Can HA cameras feed vMix/OBS via NDI? (Design review)
   - Can production events trigger HA automations? (Webhook design)
   - Are there circular dependencies?
   - Missing integration points?

2. **Unified CLI Design:**
   ```bash
   if vmix cut myvmix --input 1
   if obs scene switch myobs --scene "Gaming"
   if ha service myhome light.turn_on --entity light.studio
   ```
   - Is the CLI interface consistent?
   - Missing commands?
   - Better naming conventions?
   - Tab completion design?

3. **IF.bus Orchestration Profiles:**
   ```bash
   if bus orchestrate --profile "production-start"
   ```
   - Profile design quality?
   - Missing orchestration patterns?
   - Error recovery in profiles?
   - Partial failure handling?

#### A.2.4: Scalability Analysis
1. **96+ Provider Integration:**
   - How will the system scale to 96+ providers?
   - Connection pool management across providers?
   - Rate limiting strategies?
   - Provider-specific quirks handling?

2. **Performance Projections:**
   - Latency estimates for IF.bus orchestration?
   - Throughput limits?
   - Memory usage with 96+ providers?
   - Concurrent operation limits?

3. **Database/State Management:**
   - Where should provider credentials be stored?
   - How to manage provider state (connected, healthy, rate-limited)?
   - Caching strategies for provider APIs?
   - State synchronization across sessions?

### A.3: Debug - Find Critical Issues

**Your task:** Red-team the InfraFabric technical implementation

#### A.3.1: Security Issues
Find vulnerabilities in:
1. API key/token storage and handling
2. Command injection vectors (CLI, shell commands)
3. SSRF vulnerabilities (webhook URLs, media URLs)
4. XSS in browser sources (OBS)
5. Privilege escalation (Home Assistant control)
6. Data exfiltration via IF.witness logs
7. Rate limit bypass techniques
8. Authentication bypass in adapters

#### A.3.2: Reliability Issues
Find failure modes:
1. What if vMix/OBS crashes during orchestration?
2. What if Home Assistant becomes unavailable?
3. What if IF.bus loses connection to a provider?
4. What if two profiles conflict (both control same light)?
5. What if IF.witness log grows unbounded?
6. What if cost tracking falls behind real costs?
7. Network partition scenarios?
8. Partial deployment failures?

#### A.3.3: Edge Cases
Find problematic scenarios:
1. Zero providers configured (IF.bus empty)
2. All providers rate-limited simultaneously
3. Provider API version changes (breaking changes)
4. Unicode/emoji in entity names (Home Assistant)
5. Extremely long orchestration profiles (1000+ steps)
6. Circular orchestration dependencies
7. Provider returns malformed responses
8. Clock skew across distributed systems

### A.4: Iterate - Concrete Improvements

**Deliverable:** Improved designs addressing issues found

#### A.4.1: Architecture Improvements
1. **Improved Adapter Pattern:**
   ```python
   class ImprovedAdapter(ABC):
       # What changes would you make?
       # New methods needed?
       # Better error handling?
   ```

2. **Improved IF.bus Design:**
   - Provider registry design
   - Health check mechanisms
   - Failover strategies
   - Load balancing algorithms

3. **Improved IF.witness:**
   - Hash chain validation
   - Log rotation strategies
   - Audit query patterns
   - Compliance reporting

#### A.4.2: Code Improvements
Rewrite key sections with improvements:
1. Connection management (retry logic, timeouts, pooling)
2. Error handling (typed exceptions, error recovery)
3. Configuration management (validation, hot-reload)
4. Monitoring/observability (metrics, tracing)

#### A.4.3: CLI Improvements
Better CLI design:
```bash
# Current
if vmix cut myvmix --input 1

# Improved?
if vmix myvmix cut --input 1  # Provider first?
if production cut --vmix myvmix --input 1  # Domain first?
```

Justify your choice with UX rationale.

### A.5: Roadmap - InfraFabric Evolution

**Deliverable:** `IF-ROADMAP-V1.1-TO-V3.0.md`

#### v1.1 (Quick Wins - 1 week)
- Critical bugs fixed (list them)
- Security patches (list them)
- Documentation improvements
- Basic error recovery
- **Cost:** ~$50-100

#### v1.5 (Stability - 2-4 weeks)
- Comprehensive testing (unit + integration)
- Performance optimizations
- Provider health monitoring
- Improved error messages
- **Cost:** ~$200-400

#### v2.0 (Production-Ready - 2-3 months)
- All 96+ providers integrated
- Advanced orchestration (conditionals, loops, variables)
- Multi-region deployment
- Disaster recovery
- Compliance (SOC2, GDPR)
- **Cost:** ~$2,000-5,000

#### v3.0 (Enterprise - 6-12 months)
- AI-powered orchestration
- Predictive cost optimization
- Auto-scaling based on load
- Multi-tenancy
- White-label deployment
- **Cost:** ~$10,000-20,000

---

## Part B: Swarm of Swarms (S²) Process Evaluation

### B.1: What Was Built (Past 24 Hours)

**Multi-Session Coordination System:**
1. **7 Autonomous Sessions**
   - Session 1 (NDI)
   - Session 2 (WebRTC)
   - Session 3 (H.323)
   - Session 4 (SIP) - Critical path
   - Session 5 (CLI) - Helper
   - Session 6 (Talent) - Architecture
   - Session 7 (IF.bus) - Infrastructure

2. **70 Phase Instructions**
   - 10 phases per session
   - Git-based coordination
   - 30-second polling for new instructions
   - Autonomous execution 24/7

3. **Multi-Agent Swarms**
   - Each session spawns 5-10 agents (Haiku + Sonnet)
   - Heterogeneous allocation (92% cheaper Haiku for simple tasks)
   - Total: 49 concurrent agents across 7 sessions
   - Parallel execution within sessions

4. **"Gang Up on Blocker" Pattern**
   - When Session 4 (SIP) blocked Sessions 1-3
   - Instead of idle work, Sessions 1-3 help Session 4
   - Result: 8 hours → 6 hours (25% faster), 0% waste

5. **Velocity Gains**
   - Sequential baseline: 99-117 hours
   - With S²: 5-6 hours wall-clock
   - **Velocity: 20x faster**

### B.2: Evaluation Questions (S² Process)

#### B.2.1: Coordination Quality
1. **Git-Based Coordination:**
   - Is git polling (30s) sufficient?
   - What if git server unavailable?
   - Branch conflicts handling?
   - Better alternatives (message queue, Redis, etc.)?

2. **Phase Sequencing:**
   - Are phase dependencies clearly defined?
   - Can sessions skip ahead incorrectly?
   - How to enforce phase validation?
   - Rollback mechanisms if phase fails?

3. **Cross-Session Communication:**
   - Is STATUS.md sufficient for coordination?
   - Missing communication patterns?
   - Real-time vs eventual consistency tradeoffs?
   - Better notification mechanisms?

#### B.2.2: "Gang Up on Blocker" Pattern Analysis
1. **Pattern Effectiveness:**
   - Is the pattern well-defined?
   - Can it be automated (detect blockers automatically)?
   - When should sessions NOT help?
   - How to avoid over-helping (too many cooks)?

2. **Blocker Detection:**
   - How to detect blockers automatically?
   - False positive scenarios?
   - What if multiple sessions blocked simultaneously?
   - Priority when multiple blockers exist?

3. **Help Coordination:**
   - How to divide work when helping?
   - What if helper has wrong expertise?
   - When to give up helping?
   - How to measure help effectiveness?

#### B.2.3: Resource Allocation
1. **Haiku vs Sonnet Allocation:**
   - Current: Simple tasks → Haiku, complex → Sonnet
   - Is this optimal?
   - How to decide task complexity automatically?
   - Cost vs quality tradeoffs?

2. **Session Load Balancing:**
   - Are workloads balanced across sessions?
   - Can sessions share work dynamically?
   - What if one session much faster than others?
   - Elastic scaling (add/remove sessions)?

3. **Budget Management:**
   - Current: No hard budget enforcement
   - How to enforce budgets per session?
   - What if session exceeds budget mid-phase?
   - Cost prediction accuracy?

### B.3: Debug - Find S² Process Issues

**Your task:** Red-team the Swarm of Swarms coordination process

#### B.3.1: Coordination Failures
Find failure modes:
1. **Circular Dependencies:**
   - Session 1 waits for Session 2
   - Session 2 waits for Session 1
   - **Result:** Deadlock

2. **Cascade Failures:**
   - Session 4 (critical path) fails
   - Sessions 1-3 can't proceed
   - **Result:** All 7 sessions blocked

3. **Split Brain:**
   - Network partition: Sessions 1-3 on one side, 4-7 on other
   - Both sides think they're authoritative
   - **Result:** Conflicting state

4. **Git Branch Corruption:**
   - Force push destroys phase history
   - Sessions have inconsistent view of phases
   - **Result:** Work duplication or loss

5. **Polling Storm:**
   - All 7 sessions poll git every 30s
   - Git server overloaded
   - **Result:** Coordination breakdown

#### B.3.2: Agent Management Issues
1. **Agent Spawn Failures:**
   - Session spawns 10 agents, 5 fail immediately
   - **What should session do?**

2. **Agent Timeout:**
   - Agent stuck for 2 hours (API rate limit)
   - **When to kill? How to recover?**

3. **Agent Result Conflicts:**
   - 2 agents return conflicting results
   - **Which to trust? How to resolve?**

4. **Agent Cost Overrun:**
   - Single agent costs $50 (expected $5)
   - **Budget exceeded mid-phase. Now what?**

#### B.3.3: Phase Management Issues
1. **Phase Skipping:**
   - Session jumps Phase 2 → Phase 5 (missed 3-4)
   - **How to detect? Force rollback?**

2. **Phase Repetition:**
   - Session does Phase 3 twice
   - **Idempotency? Duplicate work detection?**

3. **Phase Divergence:**
   - Session 1 on Phase 7, Session 2 on Phase 3
   - Is this normal? Problem?
   - **When to resync?**

4. **Phase Validation:**
   - Session claims Phase 5 complete but tests fail
   - **Who validates? When? Consequences?**

#### B.3.4: Human Intervention Scenarios
1. **User Abort:**
   - User kills session mid-phase
   - **Cleanup? Notify other sessions? Resume later?**

2. **Manual Override:**
   - User manually edits STATUS.md (incorrect state)
   - **Detection? Correction? Trust user?**

3. **Emergency Stop:**
   - "Stop all 7 sessions NOW"
   - **How to propagate quickly? Partial work handling?**

4. **Session Restart:**
   - Session crashes, user restarts
   - **Resume from checkpoint? Start over? Ask user?**

### B.4: Iterate - S² Process Improvements

**Deliverable:** Improved coordination protocols

#### B.4.1: Automated Blocker Detection
Design a protocol:
```yaml
blocker_detection:
  trigger: Every 5 minutes
  checks:
    - session_blocked_time > 30min
    - waiting_on: [other_sessions]
    - can_be_helped: true
  action: Broadcast "HELP_NEEDED" to all sessions
  response: Sessions with matching expertise offer help
```

#### B.4.2: Phase Validation Protocol
Design validation:
```python
def validate_phase_completion(session, phase):
    # Check prerequisites
    # Run integration tests
    # Verify deliverables
    # Sign off with IF.witness
    # Notify orchestrator
    pass
```

#### B.4.3: Budget Enforcement
Design budget control:
```yaml
budget_enforcement:
  per_session: $100
  per_phase: $20
  monitoring: real-time
  actions:
    - warning_at: 80%
    - pause_at: 95%
    - hard_stop_at: 100%
  exception_handling: Human approval for overrun
```

#### B.4.4: Improved Git Coordination
Alternatives to git polling:
1. **Redis Pub/Sub:**
   - Pros/cons vs git?
   - Migration path?

2. **Message Queue (RabbitMQ):**
   - Pros/cons vs git?
   - Complexity tradeoff?

3. **Hybrid Approach:**
   - Git for instructions (slow)
   - Redis for status (fast)
   - Best of both?

### B.5: Roadmap - S² Evolution

**Deliverable:** `S2-ROADMAP-V1.1-TO-V3.0.md`

#### S² v1.1 (Safety First - 1 week)
**Problems fixed:**
- Phase validation protocol (no skipping)
- Blocker detection (automated help triggers)
- Budget enforcement (hard limits)
- Error recovery (spawn debugging agents)
- Git conflict resolution
**Cost:** ~$50-100

#### S² v1.5 (Smart Coordination - 2-4 weeks)
**New features:**
- Auto-detect blockers (no manual marking)
- Dynamic work splitting (helpers auto-coordinate)
- Predictive cost estimation (warn before overrun)
- Session health monitoring (detect stuck sessions)
- Checkpoint/resume (recover from crashes)
**Cost:** ~$200-400

#### S² v2.0 (Intelligent Swarms - 2-3 months)
**Advanced features:**
- AI orchestrator (learns optimal session allocation)
- Self-healing (auto-recover from failures)
- Multi-objective optimization (cost + speed + quality)
- Elastic sessions (spawn/kill based on load)
- Cross-project learning (reuse patterns)
**Cost:** ~$2,000-5,000

#### S² v3.0 (Autonomous Swarms - 6-12 months)
**Revolutionary features:**
- Fully autonomous (no human intervention)
- Self-improving (agents improve own prompts)
- Multi-modal (code + design + docs + tests)
- Swarm-to-swarm collaboration (multiple projects)
- AGI-ready architecture (scale to 1000+ agents)
**Cost:** ~$10,000-20,000

---

## Part C: Combined Evaluation

### C.1: InfraFabric ↔ S² Synergy
1. **Does S² accelerate IF development effectively?**
   - Is 20x velocity real or inflated?
   - Quality vs speed tradeoffs?
   - Where did S² help most? Where least?

2. **Can IF be built WITHOUT S²?**
   - Sequential timeline estimate?
   - Cost comparison?
   - Quality difference?

3. **Can S² work on other projects?**
   - Is S² IF-specific or generalizable?
   - What would adapting S² require?
   - Other domains where S² would excel?

### C.2: Philosophy Evaluation (Wu Lun 五倫)
1. **Are Wu Lun relationships appropriate?**
   - 君臣 (Ruler-Minister): Session 4 as blocker
   - 朋友 (Friends): Sessions helping each other
   - 長幼 (Elder-Younger): CLI as support role
   - Do these map well? Better alternatives?

2. **Does IF.ground philosophy actually help?**
   - Measurable impact on decisions?
   - Or just philosophical window dressing?
   - Evidence of alignment in code?

3. **Is IF.TTT (Traceable, Transparent, Trustworthy) achieved?**
   - Traceable: All logged via IF.witness? Gaps?
   - Transparent: State visible? Missing visibility?
   - Trustworthy: Tests + provenance sufficient? More needed?

### C.3: Meta-Evaluation
**Evaluate the evaluation process itself:**
1. **Are these evaluation questions comprehensive?**
   - Missing critical areas?
   - Too focused on X, not enough on Y?
   - Better question framing?

2. **Is this prompt well-structured?**
   - Clear sections?
   - Easy to follow?
   - Missing instructions?

3. **What would YOU add to this prompt?**
   - Additional evaluation dimensions?
   - Different debugging approaches?
   - Better deliverable formats?

---

## Your Deliverables

Please provide the following files:

### 1. `IF-TECHNICAL-REVIEW.md` (InfraFabric)
- Architecture quality assessment (ratings + explanations)
- Code quality review (module-by-module)
- Security vulnerabilities found
- Reliability issues found
- Edge cases identified
- Scalability analysis

### 2. `IF-IMPROVEMENTS-V1.1.md` (InfraFabric Quick Wins)
- Critical bugs fixed (code diffs)
- Security patches (code diffs)
- Quick improvements (code diffs)
- Estimated effort: hours
- Estimated cost: dollars

### 3. `IF-ROADMAP-V1.1-TO-V3.0.md` (InfraFabric Evolution)
- v1.1: Safety and stability
- v1.5: Performance and monitoring
- v2.0: Production-ready
- v3.0: Enterprise features
- Each version: features, timeline, cost

### 4. `S2-PROCESS-REVIEW.md` (Swarm of Swarms)
- Coordination quality assessment
- "Gang Up on Blocker" pattern analysis
- Resource allocation review
- Coordination failures found
- Agent management issues found
- Phase management issues found

### 5. `S2-IMPROVEMENTS-V1.1.md` (S² Quick Wins)
- Phase validation protocol (detailed design)
- Blocker detection protocol (detailed design)
- Budget enforcement (detailed design)
- Error recovery (detailed design)
- Estimated effort: hours
- Estimated cost: dollars

### 6. `S2-ROADMAP-V1.1-TO-V3.0.md` (S² Evolution)
- v1.1: Safety protocols
- v1.5: Smart coordination
- v2.0: Intelligent swarms
- v3.0: Autonomous swarms
- Each version: features, timeline, cost

### 7. `SESSION-PROMPTS-V2/` (Improved Session Prompts)
Create 7 improved session prompts with built-in safeguards:
- `session-1-ndi-v2.md`
- `session-2-webrtc-v2.md`
- `session-3-h323-v2.md`
- `session-4-sip-v2.md`
- `session-5-cli-v2.md`
- `session-6-talent-v2.md`
- `session-7-if-bus-v2.md`

Each prompt includes:
- Phase validation protocol (built-in)
- Blocker help protocol (automatic)
- Error recovery (spawn debugging agents)
- Cost enforcement (check before spawn)
- Status reporting (standardized format)

### 8. `COMBINED-ANALYSIS.md` (Synergy + Philosophy)
- IF ↔ S² synergy analysis
- Wu Lun philosophy evaluation
- IF.TTT achievement assessment
- Meta-evaluation of this prompt
- Recommendations for future work

---

## Evaluation Guidelines

### Be Brutal, Be Honest
- **Don't sugarcoat:** If something is bad, say it's bad
- **Quantify issues:** "Security: 3/10" is better than "Security needs work"
- **Prioritize:** Mark issues as Critical/High/Medium/Low

### Be Specific, Be Actionable
- **Bad:** "Error handling needs improvement"
- **Good:** "In `vmix_production.py:142`, exception is caught but not logged. Add: `logger.error(f'Failed to switch scene: {e}')`"

### Be Forward-Looking
- Don't just find problems, propose solutions
- Show code examples of better approaches
- Explain WHY your approach is better

### Be Comprehensive
- Read ALL the documentation provided
- Consider ALL the angles (security, performance, cost, UX, etc.)
- Don't skip sections because they're "probably fine"

---

## Repository Context

**Branch:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`

**Key Files to Review:**
```
docs/SWARM-OF-SWARMS-ARCHITECTURE.md         # S² architecture
VMIX-SPRINT-ALL-SESSIONS.md                  # vMix integration
OBS-SPRINT-ALL-SESSIONS.md                   # OBS integration
HOME-ASSISTANT-SPRINT-ALL-SESSIONS.md        # HA integration
INTEGRATION-ROADMAP-POST-GPT5-REVIEW.md      # 96+ provider roadmap
GPT5-PRO-REVIEW-PROMPT.md                    # Original review prompt
PHASE-10-CLEANUP-PROTOCOL.md                 # Phase 10 cleanup
PHASES-4-6-COORDINATION-MATRIX.md            # Dependency graph
INSTRUCTIONS-SESSION-*-PHASE-*.md            # 70 phase instructions
docs/SESSION-STARTERS/*.md                   # Session starters
papers/IF-foundations.md                     # IF philosophy
```

**Agent Coordination:**
- 7 sessions × 10 phases = 70 work streams
- Each session spawns 5-10 agents = 49 total agents
- Git-based coordination (30s polling)
- "Gang Up on Blocker" pattern discovered and fixed

**Velocity Claims:**
- Sequential: 99-117 hours
- With S²: 5-6 hours wall-clock
- **Claimed velocity: 20x**

**Cost Estimates:**
- Current sprint (vMix + OBS + HA): $135-210
- Future phases (96+ providers): $1,510-2,220
- Total: $1,645-2,430

---

## Success Criteria for Your Review

Your evaluation is successful if:
1. ✅ You find issues we missed (the more critical, the better)
2. ✅ You provide actionable improvements (code diffs, designs)
3. ✅ Your roadmaps are realistic (timeline + cost estimates)
4. ✅ Your improved prompts prevent known failure modes
5. ✅ You challenge our assumptions (velocity claims, architecture choices)
6. ✅ You make the system production-ready (security, reliability, scale)

**Most important:** Help us avoid catastrophic failures in production. If you find a showstopper bug, flag it as **CRITICAL** at the top of your review.

---

## Timeline for Your Review

**Estimated effort:** 4-8 hours of deep analysis

**Deliverables:** 8 files (reviews, improvements, roadmaps, prompts)

**Output format:** Markdown files with clear structure, code examples, and rationale

---

## Begin Your Evaluation

**Download the repository ZIP from:**
- Repository: `dannystocker/infrafabric`
- Branch: `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`

**Read the key files listed above.**

**Then create the 8 deliverable files with your comprehensive evaluation.**

**Good hunting! 🔍**

---

**Last Updated:** 2025-11-12
**Evaluation Prompt Version:** 1.0
**Target Evaluator:** GPT-5 Pro or equivalent advanced model
