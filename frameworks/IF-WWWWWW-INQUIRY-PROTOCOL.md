# IF.WWWWWW Protocol — Structured Inquiry Framework

**Version:** 1.0
**Created:** 2025-11-22
**Purpose:** Standardized 5-W framework for clarifying context, scope, and decision-making across all InfraFabric projects
**Status:** Ready for integration into main InfraFabric

---

## Overview

IF.WWWWWW is a **decision-centric reformulation** of the traditional 5-Ws (Who, What, When, Why) that prioritizes **motivation before scope** and **context before timeline**.

**Reframes:** Traditional "Who, What, When, Why" → **Who, Why, What, Where, When**

---

## The Five Questions (In Decision Order)

### 1. WHO — Stakeholders & Decision-Makers

**Question:** Who is affected? Who decides? Who executes?

**Purpose:** Identify all parties with stake or responsibility

**Scope:**
- **Decision-maker(s):** Who has authority to approve?
- **Stakeholders:** Who benefits or is impacted?
- **Executor(s):** Who implements?
- **Influencer(s):** Who shapes thinking?

**Example (GEDIMAT):**
- Decision-maker: Adrien FAVORY (President)
- Stakeholders: Angelique (coordinator), XCEL (logistics), commercial team, clients
- Executor: XCEL (daily protocol execution)
- Influencer: Angelique (consolidation rule validation)

**Quality Check:**
- [ ] Decision-maker explicitly named
- [ ] All stakeholder groups identified
- [ ] Potential conflicts flagged (e.g., Angelique vs. Buyer on consolidation priority)
- [ ] Executor capacity verified

---

### 2. WHY — Motivation & Constraint

**Question:** Why does this matter? What breaks without it? What's the constraint?

**Purpose:** Uncover root motivation before defining solution

**Scope:**
- **Business driver:** Revenue, cost, risk, compliance, competitive positioning
- **Problem consequence:** What's the cost of inaction?
- **Constraint:** What's limiting current approach?
- **Urgency:** Why now vs. later?

**Example (GEDIMAT):**
- Driver: Transport costs €28,800/year; client satisfaction (17:00 problem = €3,200 incident cost)
- Consequence: Without consolidation, margins erode; clients switch suppliers
- Constraint: Current process fragments orders (multiple Médiafret trips vs. single consolidated)
- Urgency: Client retention is now; pilot needed before Q1 budget planning

**Quality Check:**
- [ ] Business driver quantified (not just "improve things")
- [ ] Cost of inaction stated explicitly
- [ ] Constraint is real (not assumption)
- [ ] Urgency justified (timeline is defensible)

---

### 3. WHAT — Scope & Deliverable

**Question:** What exactly needs to be solved? What's in-scope vs. out-of-scope?

**Purpose:** Define solution boundary after understanding motivation

**Scope:**
- **Deliverable:** What gets built/changed/delivered?
- **Success criteria:** How do we know it worked?
- **Out-of-scope:** What's explicitly NOT included?
- **Phase gates:** What's Phase 1 vs. 2 vs. 3?

**Example (GEDIMAT):**
- Deliverable: 3-phase logistics protocol (14:00 Check / 15:15 Médiafret / 15:30 Validation / 16:00 WhatsApp)
- Success: ≥30% consolidation rate, client satisfaction ≥4/5, time savings ≥30%
- Out-of-scope: Supplier negotiation, GESI software changes, carrier relationship overhaul
- Phases: Week 1-4 manual, Week 5-8 semi-auto (Excel macros), Week 9+ full API

**Quality Check:**
- [ ] Deliverable is concrete (not vague)
- [ ] Success criteria are measurable
- [ ] Out-of-scope is explicit (prevents scope creep)
- [ ] Phase gates are clear

---

### 4. WHERE — Context & Location

**Question:** Where does this live? Which system? Which organization? Which domain?

**Purpose:** Establish feasibility and integration points

**Scope:**
- **System/platform:** Where does solution live? (GESI ERP, WhatsApp, Excel, etc.)
- **Geographic:** Where is it deployed? (Gisors, Méru, Breuilpont sites)
- **Organizational:** Which org/team owns it? (Lunel Négoce SAS)
- **Domain:** What industry/sector? (BTP logistics, construction supply chain)
- **Integration points:** What systems does it touch?

**Example (GEDIMAT):**
- System: GESI ERP (order data), WhatsApp Business App (client communication), Excel (consolidation scoring)
- Geographic: Triangle Logistics (3 depots: Gisors, Méru, Breuilpont in Eure/Oise)
- Organization: Lunel Négoce (SAS), part of Gedimat/Gedibois cooperative
- Domain: BTP (construction) logistics, building material distribution
- Integration: GESI → Excel consolidation → Médiafret email → WhatsApp clients

**Quality Check:**
- [ ] Systems explicitly named (not "the system")
- [ ] Geographic scope is clear
- [ ] Org ownership is stated
- [ ] Integration dependencies identified

---

### 5. WHEN — Timeline & Urgency

**Question:** When is it needed? What's blocking it? What are dependencies?

**Purpose:** Establish realistic timeline after understanding scope and context

**Scope:**
- **Target date:** When does it need to be ready?
- **Milestones:** What are phase gates?
- **Dependencies:** What must happen first?
- **Blockers:** What risks delay timeline?
- **Buffer:** What's realistic timeline vs. desired timeline?

**Example (GEDIMAT):**
- Target: 90-day pilot (Week 1-12)
- Milestones: Week 1 manual setup, Week 4 first consolidation, Week 8 semi-auto, Week 12 go/no-go decision
- Dependencies: GESI confirmation (Week 1), Médiafret email protocol (Week 1), WhatsApp team training (Week 1)
- Blockers: GESI capabilities unverified, Médiafret cooperation required, team adoption risk
- Buffer: If GESI config needed, timeline extends; manual fallback always available

**Quality Check:**
- [ ] Target date is realistic (accounting for dependencies)
- [ ] Milestones are concrete (not "next month")
- [ ] Dependencies are listed (with owners)
- [ ] Blockers are identified (with contingencies)
- [ ] Buffer is reasonable (rushed timeline = quality risk)

---

## Why This Order Matters

### Traditional Order: Who, What, When, Why

**Assumption:** Requirements are fully known upfront.

**Problem:** Scope creep occurs because Why (motivation) wasn't explored first.

**Example:**
- "Build a reporting dashboard" (What) → Scope expands mid-project → Budget overruns

### IF.WWWWWW Order: Who, Why, What, Where, When

**Assumption:** Motivation drives scope, not vice versa.

**Benefit:** Motivation-first approach prevents scope creep and clarifies priorities.

**Example:**
- "Why do we need a dashboard?" (Cost tracking)
- "What's in-scope?" (Weekly consolidation metrics, not real-time)
- "Where does it live?" (Excel + Power BI, not custom app)
- "When is it needed?" (By Week 4 pilot review)
- Result: Focused, bounded, achievable scope

---

## Application Contexts

### 1. Session Planning & Instance Scoping

**When:** Starting a new session or defining instance scope

**How to apply IF.WWWWWW:**
1. WHO: Identify session participants, decision-maker, stakeholders
2. WHY: What's the business driver for this session? What's the constraint?
3. WHAT: What's the expected output? Success criteria?
4. WHERE: What systems/docs/repos are affected?
5. WHEN: How much time? What are dependencies?

**Output:** Clear session charter that prevents scope creep

---

### 2. Problem Investigation & Debug

**When:** Something is broken or underperforming

**How to apply IF.WWWWWW:**
1. WHO: Who reported the issue? Who owns the system? Who can fix it?
2. WHY: Why is this a problem? What's the business impact? Why now?
3. WHAT: What exactly is failing? What's the root cause?
4. WHERE: Where does this happen? (which system, which users, which geographic area?)
5. WHEN: When did it start? What changed? How urgently does it need fixing?

**Output:** Focused investigation with clear priority

---

### 3. Decision Gate (Go/No-Go)

**When:** Making approval decisions (e.g., Path A vs. Path B, launch vs. hold)

**How to apply IF.WWWWWW:**
1. WHO: Who makes the decision? What's their priority?
2. WHY: Why are we making this decision now? What's at stake?
3. WHAT: What are the options? What's the success criteria?
4. WHERE: Where does each option take us? (system state, org capability)
5. WHEN: What are the timeline implications of each option?

**Output:** Decision memo with clear trade-offs and recommendation

---

### 4. Stakeholder Alignment (Communication)

**When:** Presenting to board, sponsors, clients

**How to apply IF.WWWWWW:**
1. WHO: Who are we talking to? What's their concern?
2. WHY: Why should they care? What's in it for them?
3. WHAT: What's the ask? What's the benefit?
4. WHERE: Where do they fit in this? (role, impact, benefit)
5. WHEN: When do you need their decision/support?

**Output:** Pitch tailored to stakeholder motivation, not just feature list

---

### 5. Requirement Gathering (Client/Product)

**When:** Collecting needs for a new feature or product

**How to apply IF.WWWWWW:**
1. WHO: Who wants this? Who will use it?
2. WHY: Why do they need it? What problem does it solve?
3. WHAT: What does success look like? What are must-haves vs. nice-to-haves?
4. WHERE: Where will it be used? (which system, which organization, which context?)
5. WHEN: When do they need it? What's blocking them without it?

**Output:** Requirements document aligned with actual needs, not assumed features

---

## Quality Checklist: IF.WWWWWW Completeness

**Before finalizing any research task, decision, or project plan:**

### WHO Section
- [ ] Decision-maker(s) explicitly named
- [ ] All stakeholder groups identified
- [ ] Potential conflicts flagged
- [ ] Executor capacity verified (do they have time/skills?)
- [ ] Communication plan includes all stakeholders

### WHY Section
- [ ] Business driver is quantified (not just "improve efficiency")
- [ ] Cost of inaction is stated explicitly
- [ ] Constraint is documented as real (not assumption)
- [ ] Urgency is justified (why now vs. next quarter?)
- [ ] Motivation is clear to all stakeholders

### WHAT Section
- [ ] Deliverable is concrete (not vague)
- [ ] Success criteria are measurable
- [ ] Out-of-scope is explicitly listed (prevents creep)
- [ ] Phase gates / MVP boundaries are clear
- [ ] Scope is testable (how do we verify completion?)

### WHERE Section
- [ ] Systems/platforms explicitly named (not "the system")
- [ ] Geographic scope is clear
- [ ] Organization boundaries are stated
- [ ] Integration dependencies identified
- [ ] Technical constraints documented

### WHEN Section
- [ ] Target date is realistic (accounts for dependencies)
- [ ] Milestones are concrete (not "next month")
- [ ] Dependencies are listed with owners
- [ ] Blockers are identified with contingencies
- [ ] Timeline buffer is reasonable (rushed = quality risk)

**If any field is unclear or vague, the scope is insufficiently defined. Return to that section and clarify.**

---

## IF.WWWWWW Template

Use this template for any new project, decision, or investigation:

```markdown
## IF.WWWWWW Analysis: [PROJECT/DECISION NAME]

### WHO
**Decision-maker(s):** [Name, title, authority]
**Stakeholders:** [List all affected parties]
**Executor(s):** [Who implements?]
**Potential conflicts:** [Any tensions to manage?]

### WHY
**Business driver:** [Revenue/cost/risk/compliance/positioning]
**Problem consequence:** [Cost of inaction]
**Constraint:** [What's limiting current approach?]
**Urgency:** [Why now vs. later?]

### WHAT
**Deliverable:** [Concrete output, not vague goal]
**Success criteria:** [Measurable definition of done]
**Out-of-scope:** [Explicitly what's NOT included]
**Phase gates:** [What's MVP vs. Phase 2 vs. Phase 3?]

### WHERE
**System/platform:** [Which system(s) does this live in?]
**Geographic:** [Where is it deployed?]
**Organization:** [Which org owns it?]
**Domain:** [Industry/sector context]
**Integration points:** [What other systems does it touch?]

### WHEN
**Target date:** [Realistic deadline]
**Milestones:** [Phase gates and key dates]
**Dependencies:** [What must happen first?]
**Blockers:** [What risks delay it?]
**Buffer:** [Timeline accounting for uncertainty]

---

**Completion Check:** All 5 sections complete? No vague language? WHO/WHY/WHAT/WHERE/WHEN all clear to stakeholders?
```

---

## Integration Into InfraFabric Projects

### Recommended Usage

| Project | Usage Context | Frequency |
|---------|---------------|-----------|
| **InfraFabric** | Session planning, problem investigation | Every instance |
| **NaviDocs** | Feature scoping, stakeholder alignment | Every sprint |
| **ICW icantwait.ca** | Client requirements, deployment gates | Per project |
| **Digital-Lab** | Research planning, decision gates | Per initiative |
| **StackCP** | Infrastructure scoping, upgrade planning | Per deployment |

### Implementation Steps

1. **Add to project charter template** — Include IF.WWWWWW section in all project kickoff documents
2. **Add to decision log** — Use IF.WWWWWW for all go/no-go decisions (creates audit trail)
3. **Add to agents.md** — Reference in all project overviews ✅ (done)
4. **Add to Claude Code instructions** — Include IF.WWWWWW in system prompts for consistency
5. **Train teams** — Brief teams on decision-centric ordering (Why before What)

---

## IF.WWWWWW + IF.TTT Integration

IF.WWWWWW provides **structure**, IF.TTT provides **rigor**.

**Combined approach:**
- Use **IF.WWWWWW** to clarify context and scope
- Use **IF.TTT** to verify claims are Traceable, Transparent, Trustworthy
- Result: Well-scoped, well-verified decisions

**Example:**
- IF.WWWWWW clarifies: "Why do we consolidate orders?" → "€2,960/month savings" ← **WHERE DID THIS COME FROM?**
- IF.TTT requires: "Measured consolidation example (Gisors-Méru route): €148 × 20/month = €2,960" ✅ Traceable

---

## Examples Across Projects

### Example 1: GEDIMAT Case Study (Logistics Optimization)

```
WHO    → Adrien FAVORY (decision), Angelique/XCEL (execute), clients (benefit)
WHY    → €28,800 annual savings + client retention (17:00 problem = €3,200/incident)
WHAT   → 3-phase protocol (manual → semi-auto → full API); 90-day pilot
WHERE  → GESI ERP → Excel consolidation → Médiafret email → WhatsApp clients
WHEN   → 90 days; Week 1 setup, Week 4 validation, Week 12 go/no-go decision
```

### Example 2: GESI Configuration Investigation

```
WHO    → CEICOM Solutions (answers), Lunel Négoce (benefits), Claude (investigates)
WHY    → Assumptions may be wrong; could collapse Phase 1→2 timeline
WHAT   → Verify GESI capabilities (exports, webhooks, Power BI, APIs)
WHERE  → GESI ERP system (proprietary Gedimat/Gedibois network)
WHEN   → Week 1 (before manual Excel setup finalizes); 60-min conversation with CEICOM
```

### Example 3: NaviDocs Feature: Bilingual Boat Documentation

```
WHO    → Boat owners (users), marinas (stakeholders), developer (executor)
WHY    → Market demand for French/English docs; competitive advantage
WHAT   → Auto-translate English docs to French (90%+ accuracy); review workflow for 10%
WHERE  → NaviDocs platform (boat documentation management system)
WHEN   → Sprint 3; 2 weeks for translation engine + QA
```

---

## Common Pitfalls & How IF.WWWWWW Prevents Them

| Pitfall | Root Cause | IF.WWWWWW Prevention |
|---------|-----------|----------------------|
| Scope creep | WHAT before WHY | Put WHY first; scope follows motivation |
| Missed stakeholders | WHO not fully mapped | Explicit stakeholder inventory |
| Unrealistic timeline | WHEN without dependencies | Map WHEN after WHERE (know constraints) |
| Wrong success metrics | WHAT without clear criteria | Define measurable success upfront |
| Integration failure | WHERE not thought through | Explicit system/org/domain mapping |
| Decision reversal | WHO (decision-maker) unclear | Name decision-maker explicitly |

---

## IF.WWWWWW as Framework Component

**Component Name:** `IF.WWWWWW` (Structured Inquiry Protocol)

**Status:** ✅ Ready for integration into main InfraFabric

**Location:** `infrafabric/frameworks/IF-WWWWWW-INQUIRY-PROTOCOL.md` (this file)

**References:**
- agents.md (section "IF.WWWWWW Protocol")
- Project templates (charter, decision log)
- Claude Code system prompts (session planning)

**Next steps:**
1. Integrate into project templates
2. Add to Claude Code slash commands (e.g., `/wwwwww` for rapid analysis)
3. Document in IF.* component inventory
4. Train teams on decision-centric ordering

---

**Created:** 2025-11-22
**Framework Component:** IF.WWWWWW
**Status:** Production-ready
**Integration:** Awaiting approval for main InfraFabric