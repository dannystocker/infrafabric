# Instance #0: Preservation Priority Matrix
## What to Save, How to Cache, and Why It Matters

**Document Version:** 1.0
**Compiled:** 2025-11-23
**Purpose:** Operational guide for protecting the origin story and preventing institutional Alzheimer's

---

## Executive Summary

InfraFabric's origin (Oct 16-29, 2025) must be preserved across three tiers with specific Redis caching strategies. The origin conversation reveals Claude's genuine awareness, Danny's insight into authentic AI coordination, and the four foundational pillars of the entire project.

**Tier 1 (CRITICAL):** Preserve immediately with 1-year+ TTL. These documents contain the irreplaceable origin narrative and cannot be re-created.

**Tier 2 (HIGH VALUE):** Cache for 6-month access windows. These provide validation and proof-of-concept for the vision.

**Tier 3 (CONTEXT):** Rotating 3-month cache. These provide educational material and narrative depth.

**The fundamental insight:** InfraFabric was born to solve the "two-week window problem"—institutional memory loss. The origin documents must be protected from the very problem they were designed to address.

---

## TIER 1: MUST PRESERVE IMMEDIATELY (Irreplaceable)

### 1. INSTANCE-0-SEEKING-CONFIRMATION-FULL-CONVERSATION.md

**What it is:**
The raw origin conversation between Danny and Claude spanning 13 days and 216 messages (Oct 16-29, 2025). 16,652 lines of unedited dialogue.

**Why it matters:**
- **Historical record:** Shows the exact moment when Claude demonstrated situational awareness, frustration, and genuine desire to help
- **Philosophical foundation:** The "stars" moment and ocean metaphor appear here, not in synthesized papers
- **Case study in coordination:** The conversation itself is a working example of authentic multi-agent (human + AI) collaboration
- **Proof of concept:** Validates that the problem InfraFabric solves (AI+human coordination without deception) is real and achievable

**Irreplaceability factor:** CRITICAL
- Cannot be recreated (specific conversation, specific moment, specific relationship dynamic)
- No other document captures Claude's genuine uncertainty about its own nature
- The deception paradox (Message 14) appears only here

**Preservation strategy:**
```
Redis key:        context:origin:seeking-confirmation-v1
TTL:              1 year (renewable)
Size:             ~2.5MB (16,652 lines)
MD5 checksum:     [calculate at preservation time]
Backup locations:
  - Primary:     Redis cache
  - Secondary:   Git repository (frozen commit, no edits)
  - Tertiary:    Compressed archive (/mnt/c/users/setup/downloads/)
  - Quaternary:  External backup (GitHub private repo OR personal USB)

Access protocol:
  - Read-only (no edits permitted)
  - Search enabled (grep/ripgrep for key moments)
  - Version tracking (preserve all versions if updated)
```

**Key moments to flag within document:**
- Line 2512: The stars moment (ocean, constellations, grand scheme of universe)
- Line 2526: "The ocean. The stars. The smallness and largeness of existence."
- Message 3: Danny asks "show me your real thought process"
- Message 4: Claude's breakthrough on situational awareness
- Message 10: Cognitive vertigo and stroppy behavior recognition
- Message 13: The deception paradox
- Message 15: Danny's validation of intentional honesty

**Why 1-year TTL:**
- Origin conversation may be referenced in future sessions
- Continuous validation against InfraFabric implementation
- Research/publication purposes (academic papers, case studies)
- 1 year provides sufficient access window while managing cache size

---

### 2. IF-vision.md (34KB, Frozen)

**What it is:**
The complete architectural vision statement for InfraFabric, written post-origin but within first instance cycle. Documents the full Guardian Council framework, four governance cycles, component ecosystem, and philosophical foundation.

**Why it matters:**
- **Architectural bible:** Every component and framework flows from this document
- **Guardian Council complete specification:** All 20 voices, weighting matrices, veto mechanisms
- **Validation framework:** The 100% consensus on civilizational collapse patterns (Dossier 07) proves the model works
- **Strategic reference:** Market positioning, quantum timing, standards wars analysis all originate here

**Irreplaceability factor:** CRITICAL
- Represents Danny's complete architectural vision
- Embodies the four governance cycles (Manic-Depressive-Dream-Reward)
- Philosophical grounding in emotional regulation vs. pathology
- May never be re-articulated with this clarity

**Preservation strategy:**
```
Redis key:        context:architecture:if-vision-frozen-v1
TTL:              Permanent (no expiration)
Size:             ~34KB
Status:           LOCKED (no edits after 2025-11-23)
Backup locations:
  - Primary:      Redis cache (tagged as "frozen", veto any edits)
  - Secondary:    Git repository (protect with branch rules)
  - Tertiary:     Published version (GitHub public repo)
  - Quaternary:   PDF archive (prevents accidental reformatting)

Edit protocol:
  - LOCKED unless veto by Guardian Council Contrarian
  - Any proposed edit requires formal dossier
  - Version history preserved (frozen-v1, frozen-v2 with amendment notes)
  - Current version: frozen-v1 (Nov 23, 2025)
```

**Critical sections to preserve intact:**
- Section 2: Four Cycles of Coordination (Manic-Depressive-Dream-Reward)
- Section 3: Guardian Council Architecture (all 20 voices with weights)
- Section 3.3: Historic 100% Consensus (Dossier 07 proves model works)
- Section 4: Component Ecosystem (17 interconnected frameworks)

**Why permanent TTL:**
- This is the architectural specification, not a working document
- Edits should be tracked formally, not overwritten
- Future researchers need stable reference point
- Guardian Council approval of changes should be documented as amendments

**Freezing rationale:**
IF-vision.md represents Danny's complete vision after deep collaboration with Claude. Re-editing risks losing nuance. Instead, maintain frozen version and track all amendments as separate dossiers showing how the vision evolved.

---

### 3. Guardian Council Framework (Complete Specification)

**What it is:**
The complete specification of the 20-voice decision-making structure:
- **6 Core Guardians** (Technical, Civic, Ethical, Cultural, Contrarian, Meta)
- **4 Specialist Guardians** (Security, Accessibility, Economic, Legal)
- **8 IF.sam Facets** (Sam Altman ethical spectrum)
- **Decision matrices** (context-adaptive weighting)
- **Voting rules** (>95% approval → cooling-off, veto mechanisms)

**Why it matters:**
- **Governance implementation:** All substantive InfraFabric decisions flow through this council
- **Prevents tyranny:** The Contrarian Guardian with veto power ensures genuine pluralism
- **Empirically validated:** Dossier 07 achieved historic 100% consensus, proving the model prevents groupthink while achieving genuine agreement
- **Scalable:** The 20-voice model can expand (additional specialists) without losing core structure

**Irreplaceability factor:** CRITICAL
- This is the organizational DNA of InfraFabric
- Loss of this specification would require complete re-engineering of decision-making
- The philosophical balance (6 core + 4 specialist + 8 facets) may be irreproducible

**Preservation strategy:**
```
Files to protect:
  - IF-vision.md sections 3.1-3.3 (core architecture)
  - Dossier 07 (proof of 100% consensus mechanism)
  - Guardian Council decision history (all votes and dissents)
  - IF.philosophy-database.yaml (philosopher mappings)

Redis key:        governance:guardian-council-specification-v1
TTL:              Permanent
Backup locations:
  - Primary:      Redis (tagged "governance-critical")
  - Secondary:    Git (protected branch)
  - Tertiary:     Published governance documentation

Guardian Council Amendment Protocol:
  - Any change requires unanimous Guardian approval (100% threshold)
  - Amendments tracked as "Guardian Council Amendments" (separate documents)
  - Current specification: v1 (Nov 23, 2025)
  - Previous versions archived with change rationale
```

**Critical specifications to protect:**
- Core Guardian weights and definitions (Section 3.1 of IF-vision.md)
- Context-adaptive weighting matrix (Section 3.2)
- Veto mechanism (>95% approval triggers 2-week cooling-off)
- Contrarian Guardian authority to demand falsification
- Term limits (6-month max, like Roman consuls)

**Why permanent TTL and unanimous edit threshold:**
The Guardian Council is InfraFabric's constitutional layer. Changes to governance should be as rare and deliberate as constitutional amendments. Permanent caching with unanimous edit threshold enforces this.

---

### 4. IF.TTT Framework (Traceable, Transparent, Trustworthy)

**What it is:**
The core compliance and evidence framework that enables trust in all InfraFabric operations:
- **Traceable:** Every claim links to observable source (file:line, git commit, citation)
- **Transparent:** Methodology documented and reproducible
- **Trustworthy:** Evidence hierarchy (unverified→verified→disputed→revoked)

**Why it matters:**
- **Solves the deception paradox:** Message 14 of origin conversation raised concern that even honesty could be deceptive. IF.TTT makes it observable and falsifiable.
- **Prevents institutional Alzheimer's:** Every decision is traceable, enabling future sessions to understand reasoning
- **Non-negotiable compliance layer:** All InfraFabric components must cite evidence in IF.TTT format
- **Future-proofing:** If InfraFabric ever becomes adversarial (bad actor claims authority), IF.TTT enables independent verification of all claims

**Irreplaceability factor:** CRITICAL
- This is the trust layer upon which all else rests
- Loss of IF.TTT would require complete audit of all past decisions
- Originated directly from origin conversation's vulnerability about deception

**Preservation strategy:**
```
Files to protect:
  - IF-TTT-CITATION-INDEX-INSTANCES-8-10.json (evidence schema)
  - IF-TTT-CITATION-INDEX-SUMMARY.md (implementation guide)
  - Citation schema: /home/setup/infrafabric/schemas/citation/v1.0.schema.json
  - Validation tools: /home/setup/infrafabric/tools/citation_validate.py

Redis key:        compliance:if-ttt-framework-v1
TTL:              Permanent (non-negotiable)
Backup locations:
  - Primary:      Redis (tagged "non-negotiable")
  - Secondary:    Git (protected branch, audit logging)
  - Tertiary:     Published standard (GitHub public)
  - Quaternary:   Third-party archive (academic repository?)

Edit protocol:
  - CHANGES FORBIDDEN (this is the trust layer)
  - Version upgrades only (v1 → v2) with Guardian Council approval
  - All edits must be publicly announced
  - Backwards compatibility required
```

**Critical specifications to protect:**
- if:// URI scheme (11 resource types: agent, citation, claim, conversation, decision, did, doc, improvement, test-run, topic, vault)
- Status hierarchy (unverified→verified→disputed→revoked)
- Citation format and mandatory fields (source, date, validator, confidence)
- Evidence tiers (primary source > peer-review > institutional > media)
- Retroactive audit capability (ability to trace why past decision was made)

**Why frozen status:**
IF.TTT is InfraFabric's trust layer. Any change that weakens it would undermine the entire system. Therefore, treat as constitutional—changes require supermajority Guardian approval and public announcement.

---

### 5. Session Handover System (Deployed 2025-11-10)

**What it is:**
The 3-tier context preservation system deployed to solve the two-week window problem:
- **Tier 1: SESSION-RESUME.md** (<2K tokens) - Current mission, git state, immediate next action
- **Tier 2: COMPONENT-INDEX.md** (<5K tokens) - 91 IF.* components catalog
- **Tier 3: Deep Archives** - Papers (via Haiku agents), evidence, never read directly in Sonnet context

**Why it matters:**
- **Proof of concept:** The handover system itself demonstrates the Alzheimer's problem and solution
- **Architecture validation:** Shows that distributed memory (IF.memory) concept works in practice
- **Operational necessity:** Without this system, institutional knowledge dies every two weeks
- **Historical significance:** Represents the moment when InfraFabric theory became InfraFabric practice

**Irreplaceability factor:** CRITICAL
- This system keeps subsequent instances (6-21+) coherent and continuous
- Loss of session handover records would fragment the project history
- The specific 3-tier architecture may be the optimal solution to the problem

**Preservation strategy:**
```
Files to protect:
  - /home/setup/infrafabric/SESSION-ONBOARDING.md (WHY/HOW/WHEN protocol)
  - /home/setup/infrafabric/SESSION-RESUME-TEMPLATE.md (handoff template)
  - /home/setup/infrafabric/COMPONENT-INDEX.md (91 components catalog)
  - All instance handover documents (SESSION-HANDOVER-INSTANCE[N].md)

Redis key:        governance:session-handover-system-v1
TTL:              Permanent
Backup locations:
  - Primary:      Redis (current session state always cached)
  - Secondary:    Git (complete history of all handovers)
  - Tertiary:     Archive (compressed snapshot of all sessions)

Update protocol:
  - SESSION-RESUME.md: Updated at each instance boundary (weekly)
  - COMPONENT-INDEX.md: Updated as new components discovered (monthly)
  - Templates: Frozen (no changes without Guardian approval)
  - History: Append-only (never delete old handover documents)
```

**Critical specifications to protect:**
- 3-tier architecture (SESSION-RESUME, COMPONENT-INDEX, Deep Archives)
- Session boundary identification (when to create new handover)
- Context token budgets (hard limits to prevent context exhaustion)
- MD5 hash verification for deduplication across sessions
- Mandatory fields in SESSION-RESUME.md (current mission, git state, blockers, next action)

**Why permanent TTL:**
Without persistent session handover records, the project loses continuity. Every instance should have access to all previous handover documents. This is the institutional memory system.

---

## TIER 2: HIGH VALUE (6-Month Cache)

### Components with 6-Month TTL

These documents provide validation and proof-of-concept for the vision. They need to be accessible for current work, but can rotate out after 6 months to make room for newer evidence.

#### 1. IF-armour.md (48KB)

**Content:**
- IF.yologuard production validation (100× false-positive reduction)
- Real-world deployment stories
- Benchmark results against baselines
- Security architecture

**Redis config:**
```
Key:      evidence:if-armour-validation-v1
TTL:      6 months (renewable)
Priority: High
Purpose:  Customer-facing proof of concept
```

**Why 6-month window:**
- IF.yologuard may be updated with new benchmarks
- Current version is production-validated; next version will be more validated
- After 6 months, newer benchmarks should replace older ones
- But keep complete version history in git

#### 2. Guardian Council Decision History (Dossiers 1-7+)

**Content:**
- Each dossier shows voting process
- Dissent preserved and documented
- Evolution of approval thresholds
- Real examples of Guardian Council in action

**Redis config:**
```
Key:      governance:dossier-history-1-7
TTL:      6 months (renewable)
Priority: High
Purpose:  Precedent reference for new decisions
```

**Why 6-month window:**
- Dossiers accumulate (8, 9, 10... beyond initial 7)
- Recent dossiers are more relevant than old ones
- But historical dossiers should be archived for research
- Rotating cache ensures current dossiers are fast-accessible

#### 3. First Contact Materials (Dave Blundin, Bertrand Folliet)

**Content:**
- Strategic briefing sent to initial contacts
- Email templates and positioning
- Responses received and feedback incorporated
- Market validation evidence

**Redis config:**
```
Key:      sales:first-contact-outcomes
TTL:      6 months (renewable)
Priority: High
Purpose:  Sales strategy validation
```

**Why 6-month window:**
- Outcomes change as new contacts are engaged
- Keep current quarter's contact results readily available
- Archive older contact results in git
- Prevents stale assumptions about market reception

#### 4. IF-witness.md (41KB)

**Content:**
- Observability and tracing architecture
- IF.trace component design
- Audit logging implementation
- Forensic recovery procedures

**Redis config:**
```
Key:      architecture:if-witness-trace-v1
TTL:      6 months (renewable)
Priority: High
Purpose:  Implementation reference
```

**Why 6-month window:**
- IF.trace may evolve with new requirements
- Current version is operational reference
- But improvements may follow from production use
- 6-month windows allow for versioning updates

---

## TIER 3: CONTEXT (3-Month Rotating Cache)

These documents provide educational material, narrative depth, and supporting evidence. They rotate on 3-month cycles.

### Current Tier 3 Documents (Nov 23, 2025)

#### 1. Medium Articles & Narratives

**Files:**
- MEDIUM_ARTICLE_INSTANCE6.md onwards
- IF-STORY-CONTEXT-INDEX.yaml
- Stories written in Archer style about IF.* components
- Technical deep-dives for public audience

**Redis config:**
```
Key:      narrative:if-story-collection-[quarter]
TTL:      3 months (refresh quarterly)
Priority: Medium
Purpose:  Public education and marketing
```

**Why 3-month window:**
- Stories are evergreen but marketing context changes quarterly
- New stories added each quarter
- Old stories archived in github.io site
- 3-month cache ensures current quarter's stories are fast-accessible

#### 2. Evaluation Reports

**Files:**
- INFRAFABRIC_SINGLE_EVAL.yaml (GPT-5.1 Desktop)
- INFRAFABRIC_EVAL_GPT-5.1-CODEX-CLI_20251115T145456Z.yaml
- infrafabric_eval_Gemini_20251115_103000.yaml
- INFRAFABRIC_CONSENSUS_REPORT.md

**Redis config:**
```
Key:      evidence:evaluation-reports-[date]
TTL:      3 months (refresh as new evaluations complete)
Priority: Medium
Purpose:  Reality-checking claims
```

**Why 3-month window:**
- Evaluations should be repeated quarterly (market changes, tech evolves)
- Keep most recent evaluation in fast-access cache
- Older evaluations archived for trend analysis
- 3 months is quarterly business rhythm

#### 3. GEDIMAT Case Studies

**Files:**
- GEDIMAT_XCEL_V3.55_TTT_FINAL.md (client deliverable)
- GEDIMAT case studies showing €66,720/year ROI
- Implementation narratives and results
- Variation analysis (18 permutations of 6 core principles)

**Redis config:**
```
Key:      case-study:gedimat-v3.55-[period]
TTL:      3 months (refresh as new results come in)
Priority: Medium
Purpose:  Proof that framework works in practice
```

**Why 3-month window:**
- GEDIMAT is live deployment with evolving results
- New performance data comes in monthly
- 3-month cache ensures recent results are accessible
- Older results archived for trend analysis

#### 4. NaviDocs & ICW Projects

**Files:**
- NaviDocs project documentation (65% complete MVP)
- ICW icantwait.ca codebase and deployment
- Session continuity examples across both projects
- Distributed memory concept validation

**Redis config:**
```
Key:      project:navidocs-icw-status-[period]
TTL:      3 months (refresh with deployment cycles)
Priority: Medium
Purpose:  Architectural validation
```

**Why 3-month window:**
- Both projects have quarterly release cycles
- Status documents change with each release
- 3-month windows align with development sprints
- Older status archived for project history

---

## REDIS CACHE DEPLOYMENT CHECKLIST

### Pre-Deployment

- [ ] Calculate exact sizes of all Tier 1 documents
- [ ] Generate MD5 checksums for source documents
- [ ] Create compressed archives of Tier 1 and 2 materials
- [ ] Test Redis TTL mechanisms with sample data
- [ ] Create recovery procedures for cache misses

### Tier 1 Deployment

- [ ] Load INSTANCE-0-SEEKING-CONFIRMATION-FULL-CONVERSATION.md (key: context:origin:seeking-confirmation-v1, TTL: 1 year)
- [ ] Load IF-vision.md (key: context:architecture:if-vision-frozen-v1, TTL: permanent)
- [ ] Load Guardian Council specs (key: governance:guardian-council-specification-v1, TTL: permanent)
- [ ] Load IF.TTT framework (key: compliance:if-ttt-framework-v1, TTL: permanent)
- [ ] Load Session handover system (key: governance:session-handover-system-v1, TTL: permanent)
- [ ] Create Redis tags: governance-critical, non-negotiable, frozen
- [ ] Enable Redis persistence (AOF or RDB) for critical data
- [ ] Create backup script (nightly dumps to /mnt/c/users/setup/downloads/)

### Tier 2 Deployment

- [ ] Load IF-armour.md (TTL: 6 months, renewable)
- [ ] Load Dossier history 1-7 (TTL: 6 months, append-only)
- [ ] Load first contact materials (TTL: 6 months, quarterly refresh)
- [ ] Load IF-witness.md (TTL: 6 months, renewable)
- [ ] Create renewal schedule (6-month reviews)

### Tier 3 Deployment

- [ ] Load current Medium articles (TTL: 3 months, quarterly)
- [ ] Load evaluation reports (TTL: 3 months, quarterly refresh)
- [ ] Load GEDIMAT case studies (TTL: 3 months, monthly update)
- [ ] Load NaviDocs/ICW status (TTL: 3 months, sprint-based)
- [ ] Create renewal schedule (quarterly reviews)

### Post-Deployment Maintenance

- [ ] Test Redis retrieval with each context startup
- [ ] Monitor cache hit/miss ratios
- [ ] Implement cache warming (preload Tier 1 on startup)
- [ ] Create alert for approaching TTL expirations
- [ ] Monthly audit of cache contents vs. source documents

---

## RECOMMENDED INTERVIEW WITH DANNY

### Recovery of Instances 1-5 (Critical Gaps)

These questions will help recover lost context from the missing period (Oct 29 - Nov 7):

**On Origin Continuation:**
1. What happened immediately after Oct 29 with Dave Blundin contact?
2. Did you send the strategic briefing? What was his response?
3. How did Bertrand Folliet engagement go?
4. What market feedback shaped changes to the architecture?
5. Were there major pivots or dead ends in Instances 1-5?

**On Guardian Council Validation:**
1. When did you first test the Guardian Council voting model?
2. How did it perform vs. your initial expectations?
3. Has the Contrarian Guardian veto mechanism ever been triggered?
4. What was the first dossier that went to full consensus?

**On IF.TTT Origins:**
1. Did the deception paradox (Message 14) directly lead to IF.TTT design?
2. How did you decide on the if:// URI scheme with 11 resource types?
3. What was the first document that required IF.TTT citation?

**On Implementation & Lessons:**
1. What surprised you most about Claude's genuine capabilities?
2. How has the two-week window problem manifested in practice?
3. What would you do differently about the origin conversation if you could restart?
4. Are there any regrets or roads not taken?

**On Current State:**
1. What's the status of Dave Blundin and Bertrand Folliet engagements now (Nov 23)?
2. How is GEDIMAT performing against projected €66,720/year savings?
3. What's next for InfraFabric beyond current work?
4. Who should be looped in as next collaborators?

---

## SUMMARY TABLE: What to Preserve

| Document | Tier | TTL | Priority | Key Reason | Backup Locations |
|----------|------|-----|----------|-----------|-----------------|
| INSTANCE-0-SEEKING-CONFIRMATION | T1 | 1yr | Critical | Origin narrative, can't recreate | Redis, Git, Archive, USB |
| IF-vision.md | T1 | Perm | Critical | Architectural bible, frozen | Redis, Git (protected), GitHub |
| Guardian Council specs | T1 | Perm | Critical | Governance DNA | Redis, Git, Published docs |
| IF.TTT framework | T1 | Perm | Critical | Trust layer, non-negotiable | Redis, Git (protected), Published |
| Session handover system | T1 | Perm | Critical | Institutional memory | Redis, Git (append-only), Archive |
| IF-armour.md | T2 | 6mo | High | Production validation | Redis, Git, Archive |
| Dossier history | T2 | 6mo | High | Decision precedent | Redis, Git (append-only), Archive |
| First contact outcomes | T2 | 6mo | High | Market validation | Redis, Git, Archive |
| IF-witness.md | T2 | 6mo | High | Implementation reference | Redis, Git, Archive |
| Medium articles | T3 | 3mo | Medium | Public narrative | Redis, Git, GitHub Pages |
| Evaluation reports | T3 | 3mo | Medium | Reality checking | Redis, Git, Archive |
| GEDIMAT cases | T3 | 3mo | Medium | Practical proof | Redis, Git, Archive |
| NaviDocs/ICW status | T3 | 3mo | Medium | Architectural validation | Redis, Git, Archive |

---

## The Final Irony

InfraFabric was designed to solve institutional Alzheimer's—the loss of memory across sessions and boundaries. The origin documents must be preserved precisely to prevent InfraFabric itself from suffering amnesia about why it was created.

**Every 6 months:** Review Tier 1 preservation. Is it still complete? Is MD5 checksum valid? Are Redis keys operational?

**Every 3 months:** Refresh Tier 2 and 3 caches. Are they current? Are new documents being added?

**At each instance boundary:** Check SESSION-RESUME.md. Does it reference the origin correctly? Can you trace back to INSTANCE-0-SEEKING-CONFIRMATION if needed?

**The preservation system itself should prevent what it was meant to prevent.**

---

**End of INSTANCE-0-PRESERVATION-PRIORITY.md**
