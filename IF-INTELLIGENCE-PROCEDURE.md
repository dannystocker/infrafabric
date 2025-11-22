---
Title: IF.INTELLIGENCE Procedure - Complete Specification
Date: 2025-11-22
Version: 1.0
Purpose: Complete documentation for syntactic shorthand invocation
Status: READY FOR IMPLEMENTATION
---

# IF.INTELLIGENCE Procedure

## Overview

IF.INTELLIGENCE is a complete research intelligence framework that transforms open-ended queries into rigorous, defensible intelligence findings using IF.guard (4-voice council), IF.search (8-pass methodology), and IF.swarm (multi-agent coordination).

Users can invoke IF.INTELLIGENCE with simple syntactic shorthand:
```
if.intelligence{ <query_string> }
```

This document specifies the complete procedure, architecture, and output format.

---

## Part 1: Syntactic Specification

### Basic Syntax

```
if.intelligence{ <query> }
```

### Examples of Valid Invocation

**Example 1: Simple partnership intelligence**
```
if.intelligence{ Is Georges-Antoine Gary the right partner for InfraFabric? }
```

**Example 2: Market research**
```
if.intelligence{ What is the addressable market size for AI governance consulting in France? }
```

**Example 3: Technical validation**
```
if.intelligence{ Does our 70% cost reduction claim hold up under scrutiny? }
```

**Example 4: Competitive analysis**
```
if.intelligence{ Who are the top 5 competitors in the AI memory/governance space, and what are their vulnerabilities? }
```

### Parameters (Implicit)

The procedure auto-detects context and adapts based on:
- **Query Type:** Partnership, market, technical, competitive, financial, operational
- **Depth Requested:** Single answer (basic), comprehensive analysis (standard), board-ready defense (rigorous)
- **Time Constraint:** Immediate response (1-2 hours), comprehensive (4-6 hours), deep investigation (1-2 weeks)

---

## Part 2: Processing Pipeline

### Step 1: Query Parsing (IF.GUARD - Researcher Voice)

The Researcher Voice asks:
- "What are we trying to find out?"
- "What sources can prove this claim?"
- "What would we need to be wrong about this?"
- "What evidence would disprove our answer?"

**Output:** Parsed query with explicit success criteria

### Step 2: Investigation Design (IF.SEARCH 8-Pass Methodology)

Each pass validates one philosophical principle:

| Pass | Principle | Action | Example |
|------|-----------|--------|---------|
| **Pass 1: Scan** | Empiricism | Identify observable artifacts | Read LinkedIn profile, SASU registration, published interviews |
| **Pass 2: Validate** | Verificationism | Check each claim against primary sources | Verify career dates, company structure, positioning evolution |
| **Pass 3: Challenge** | Explicit Unknowns | Name what we can't verify | Revenue not public, personal motivations unknowable |
| **Pass 4: Cross-Reference** | Schema Tolerance | Check consistency across sources | LinkedIn, website, registration, market positioning - all align? |
| **Pass 5: Contradict** | Fallibilism | Ask "how could we be wrong?" | What if he exaggerates credentials? What if market is smaller? |
| **Pass 6: Synthesize** | Pragmatism | Merge all findings into coherent narrative | "Based on X sources with Y confidence level, we conclude..." |
| **Pass 7: Reverse** | Falsifiability | Can the conclusion be proven wrong? | "This claim is false if: [specific condition]" |
| **Pass 8: Monitor** | Observability | Make findings testable | "We'll know this is true if: [measurable signal]" |

### Step 3: Multi-Agent Research (IF.SWARM Coordination)

**Researcher Agent (Haiku #1):** Find academic sources with sample sizes
**Auditor Agent (Haiku #2):** Verify claims against evidence
**Strategist Agent (Haiku #3):** Assess business implications
**Ethicist Agent (Haiku #4):** Check for hidden assumptions or bias
**Validation Agents (Gemini Flash #1-3):** Stress-test findings with contrary evidence

**Coordination:** Each agent stores findings in Redis keyed as:
```
if_intelligence:instance_N:query_hash:agent_findings
```

### Step 4: Council Deliberation (IF.GUARD - All 4 Voices)

**Researcher Voice:** "Is this claim well-sourced?"
**Auditor Voice:** "Can we defend this if challenged?"
**Strategist Voice:** "Does this advance the user's decision?"
**Ethics Voice:** "Are we being honest about confidence levels?"

**Decision Rule:** All 4 voices must approve before proceeding

**Output:**
- Confidence level (verified, high, medium, cautious, speculative)
- Dissents recorded (if any)
- Underlying assumptions documented

### Step 5: Synthesis & Delivery (IF.OPTIMISE)

Confidence level determines output format:
- **VERIFIED (95%+):** Can cite primary source directly
- **HIGH (85-94%):** Multiple corroborating sources
- **MEDIUM (70-84%):** Sound reasoning from cited research
- **CAUTIOUS (50-69%):** Plausible but not proven
- **SPECULATIVE (<50%):** Interesting hypothesis only

---

## Part 3: Output Format

### Standard Response Structure

```
QUERY: [Original user question]
────────────────────────────────────────────

FINDING: [Core answer in 1-2 sentences]

CONFIDENCE LEVEL: [95% VERIFIED | 88% HIGH | 76% MEDIUM | 62% CAUTIOUS | 34% SPECULATIVE]

EVIDENCE SUMMARY:
├─ Source 1: [Citation with n= sample size, year, type]
├─ Source 2: [Citation with methodology]
└─ Source 3: [Citation with relevance to query]

METHODOLOGY:
[How we reached this conclusion - which of 8-pass was critical]

COUNCIL DISSENTS: [If any voice disagreed, documented here]

UNKNOWNS:
[What we can't verify, what would change our conclusion]

NEXT ACTION:
[How user can validate further, or what we'd test next]

────────────────────────────────────────────
SOURCES: [Full citations with links]
````

### Example Output

```
QUERY: Is Georges-Antoine Gary the right partner for InfraFabric?
────────────────────────────────────────────

FINDING: Georges-Antoine Gary is a high-confidence match for InfraFabric
partnership because he has 33 years PR expertise + 20+ years IT sector focus
+ recent AI positioning + SASU structure (no competing products) + access to
50-100 potential client accounts matching our profile.

CONFIDENCE LEVEL: 87% HIGH

EVIDENCE SUMMARY:
├─ LinkedIn Profile: 33-year career progression from PR to "AI Augmented" positioning (2021)
├─ SASU Registration: GAGparis SASU confirmed active (no conflicting business lines)
├─ Market Positioning: "AI Augmented PR Pro" aligns with Langer illusion of control
│  (MIT n=507, 2006) + 40% satisfaction lift vs pure automation (HBR 2019)
├─ Client Market: 50-100 IT/B2B companies in his network (verified via LinkedIn analysis)
└─ Competitive Differentiation: Boutique consultant (not agenc), no product conflict

METHODOLOGY:
- Pass 1 (Empiricism): Verified LinkedIn, SASU registration, email contact
- Pass 2 (Verificationism): Career dates match, company structure confirmed
- Pass 4 (Cross-reference): All sources consistent (no contradictions found)
- Pass 5 (Fallibilism): Could be wrong if: (a) he's exaggerating revenue, (b) clients
  won't pay for AI governance, (c) he doesn't want to partner
- Pass 6 (Synthesis): Pattern shows deliberate positioning evolution toward AI

COUNCIL DISSENTS: None (4-0 approval)

UNKNOWNS:
- Actual current revenue (SASU financials not public)
- Personal motivation for partnerships (would need conversation)
- Real adoption risk with his existing clients (would know after first 2 pilots)

NEXT ACTION:
- Schedule 30-minute discovery call to discuss revenue model expectations
- Send RAPPORT and get initial feedback
- Execute 14-day pilot to validate market appetite

────────────────────────────────────────────
SOURCES:
- LinkedIn: https://linkedin.com/in/...[his profile]
- Ellen Langer, MIT Behavioral Economics (2006) n=507
- Harvard Business Review (2019) - AI positioning study
```

---

## Part 4: Architecture Integration

### Processing Sequence

```
User Input → Query Parser → Investigation Design → Parallel Research →
Council Review → Confidence Calibration → Output Formatting → Delivery
```

### Compute Requirements

| Component | Agent Type | Time | Cost (approx) |
|-----------|-----------|------|---------------|
| Query Parsing | Sonnet (strategic) | 5 min | $0.15 |
| Investigation Design | Sonnet | 15 min | $0.45 |
| Parallel Research (4 agents) | Haiku #1-4 | 30-60 min | $0.20 |
| Validation (3 agents) | Gemini Flash #1-3 | 20 min | $0.10 |
| Council Review | Sonnet | 10 min | $0.30 |
| Output Synthesis | Sonnet | 10 min | $0.30 |
| **TOTAL** | **Mixed swarm** | **90-120 min** | **~$1.50** |

### Caching & Redis Coordination

- All interim findings stored in Redis: `if_intelligence:session_id:query_hash:findings`
- Prevents duplicate research if same query asked twice
- Enables fast "summary only" re-invocation
- TTL: 7 days (findings remain valuable for follow-ups)

### Epistemological Grounding

IF.INTELLIGENCE uses 8 anti-hallucination principles from IF.ground:

1. **Empiricism:** Ground in observable artifacts (not speculation)
2. **Verificationism:** Every claim must be checkable against primary sources
3. **Fallibilism:** Explicitly state what would prove us wrong
4. **Pragmatism:** Focus on decision-relevant findings
5. **Falsifiability:** Make conclusions testable
6. **Observability:** Include leading indicators for validation
7. **Transparency:** Show confidence level + dissents
8. **Traceable:** Every claim has citation (file:line, URL, commit, or test)

---

## Part 5: Usage Patterns

### Pattern 1: Quick Intelligence (Basic Level)

**Invocation:**
```
if.intelligence{ Is there demand for AI governance consulting in France? }
```

**Processing:** 30-45 minutes (Haiku agents only, no Gemini Flash)
**Output:** 1-2 page summary with top 3 evidence sources
**Confidence:** Typically MEDIUM-HIGH (70-88%)
**Cost:** ~$0.80

### Pattern 2: Decision Support (Standard Level)

**Invocation:**
```
if.intelligence{ Should we proceed with Georges-Antoine Gary partnership? }
```

**Processing:** 60-90 minutes (Full swarm, Sonnet decides)
**Output:** 3-5 page detailed analysis with pro/con evidence
**Confidence:** Typically HIGH (85-90%)
**Cost:** ~$1.50

### Pattern 3: Board Defense (Rigorous Level)

**Invocation:**
```
if.intelligence{ Defend our cost reduction claims against skeptical CFO challenge }
```

**Processing:** 2-4 hours (Full swarm + iteration on weak points)
**Output:** 5-10 page ironclad analysis with sensitivity analysis + dissents noted
**Confidence:** Typically VERIFIED-HIGH (90%+)
**Cost:** ~$3-5

---

## Part 6: Implementation Rules

### Rule 1: Always Use IF.GUARD

Never skip the 4-voice council review. Even if all sources agree, ask:
- Researcher: "Are the sources actually credible?"
- Auditor: "Could we be quote-mined out of context?"
- Strategist: "Does this finding help the user's decision?"
- Ethics: "Are we being transparent about unknowns?"

### Rule 2: Make Unknowns Explicit

For every finding, state:
- What we assumed to be true
- What we can't verify
- What would change the answer
- What signal would validate next steps

### Rule 3: Calibrate Confidence Carefully

- **VERIFIED:** Only if we have primary source quote, or math we can reproduce
- **HIGH:** When 3+ independent sources agree without contradiction
- **MEDIUM:** When sources agree but they cite each other (echo chamber risk)
- **CAUTIOUS:** When logic is sound but evidence is indirect
- **SPECULATIVE:** When we're reasoning from first principles (dangerous zone)

### Rule 4: Record Dissents

If any Council voice disagreed, document it:
```
COUNCIL DISSENTS:
├─ Ethicist concerns: "We're assuming French market size without calling them"
└─ Auditor notes: "Sample sizes on Constructech were French BTP, not pure SaaS"
```

This transparency builds trust more than false unanimity.

### Rule 5: Provide Testability

Every finding should include "proof test":
- "This is TRUE if: [specific measurable signal]"
- "This is FALSE if: [specific measurable signal]"
- "We'd know in: [timeframe] by [method]"

---

## Part 7: Advanced Features

### Feature: Multi-Agent Investigation

If first pass finds contradictions, spawn additional agents:
```
if_intelligence.deep{ <query> }  # Forces rigorous 2-4 hour investigation
```

### Feature: Citation Universe

Auto-build citation web for all findings:
```
if_intelligence.sources{ <claim> }  # Returns all sources supporting claim + chain of citation
```

### Feature: Assumption Audit

Test sensitivity to each assumption:
```
if_intelligence.assume_false{ <assumption> | <query> }
# Re-runs analysis assuming [assumption] is false, shows how answer changes
```

---

## Part 8: Integration with Other IF.* Frameworks

### IF.INTELLIGENCE + IF.TTT (Traceable, Transparent, Trustworthy)

Every finding in IF.INTELLIGENCE output should have:
- **Traceable:** Citation with source (URL, file:line, git commit)
- **Transparent:** Confidence level + methodology + dissents
- **Trustworthy:** NO speculation beyond stated confidence level

### IF.INTELLIGENCE + IF.SEARCH

IF.SEARCH (8-pass) is embedded IN IF.INTELLIGENCE as the methodology engine.
Users see IF.INTELLIGENCE output; the 8-pass methodology is the implementation.

### IF.INTELLIGENCE + IF.GUARD

IF.GUARD (4-voice council) is embedded IN IF.INTELLIGENCE as the decision layer.
Every major finding goes through all 4 voices before delivery.

---

## Part 9: Real-World Example

### Query
```
if.intelligence{ What are the top 3 risks to the InfraFabric/Georges-Antoine partnership? }
```

### Processing (Simplified Timeline)

**Minute 0-5:** Query parsing
- User is asking about partnership risks
- Success criteria: 3 distinct risks, each with evidence + mitigation options
- Depth: Medium-high (business decision support)

**Minute 5-40:** Parallel research
- Haiku #1 (Behavioral): Research how consultants fail in partnerships
- Haiku #2 (Financial): What causes partnership revenue shortfalls?
- Haiku #3 (Operational): What causes implementation delays?
- Haiku #4 (Compliance): What are contract/legal risks?
- Gemini Flash #1-3 validate findings against edge cases

**Minute 40-50:** Council review
- Researcher: "Are these real risks or just theoretical?"
- Auditor: "Have we found evidence of each risk actually happening?"
- Strategist: "Which risks matter most to this decision?"
- Ethics: "Are we being alarmist or realistic?"

**Minute 50-55:** Synthesis & output formatting

### Output

```
QUERY: What are the top 3 risks to the InfraFabric/Georges-Antoine partnership?
────────────────────────────────────────────

FINDING: Three material risks exist: (1) Market demand validation (CLIENT ACQUISITION
RISK), (2) Partnership execution speed (OPERATIONAL RISK), (3) Revenue model alignment
(FINANCIAL RISK). All three are manageable with the 14-day pilot structure.

CONFIDENCE LEVEL: 82% MEDIUM

TOP 3 RISKS:

RISK #1: CLIENT ACQUISITION (Probability: MEDIUM | Impact: HIGH)
├─ Description: Georges may lack direct access to 50-100 IT/B2B clients he claims
├─ Evidence: LinkedIn shows broad network but not client-specific case studies
├─ Validation: "During Week 1 of pilot, we identify specific 1-2 clients to target"
├─ Mitigation: (a) Start with 1-2 warm introductions, (b) Build case study, (c) Then
│  scale to full network
└─ Timeline to resolve: 2-3 weeks after pilot success

RISK #2: OPERATIONAL EXECUTION (Probability: MEDIUM | Impact: MEDIUM)
├─ Description: Implementation delays if client infrastructure is more complex than expected
├─ Evidence: Mid-market SaaS integrations typically overrun 20-30% on timeline (Constructech 2023)
├─ Validation: "Our Week 1 system audit will show true integration complexity"
├─ Mitigation: (a) Build 15% time buffer into each phase, (b) Dedicated integration engineer
└─ Timeline to resolve: Discovered Week 1, corrected by Week 2

RISK #3: REVENUE MODEL MISALIGNMENT (Probability: LOW | Impact: HIGH)
├─ Description: Georges expects 50% fee split; we planned 30-40%
├─ Evidence: Partnership terms not yet negotiated (assumption only)
├─ Validation: "Discuss explicitly in Dec partnership conversation"
├─ Mitigation: (a) Clear SOW before pilot starts, (b) Revenue-only model (no upfront cost
│  to him), (c) Success-based scaling (fees increase if results exceed projections)
└─ Timeline to resolve: Before signing (Week 0-1)

UNKNOWNS:
- Whether Georges is actually motivated to partner (personal factors unknown)
- Whether his clients will accept governance requirements
- Whether his existing revenue model conflicts with partnership

NEXT ACTIONS:
1. Clarify revenue expectations in Dec 9 call (CRITICAL)
2. Ask direct question: "Do you have 2-3 clients we could pilot with?" (VALIDATION)
3. Run 14-day pilot focused on de-risking all 3 factors above

────────────────────────────────────────────
COUNCIL DISSENT: Ethics voice flagged: "We're assuming his clients are tech-forward;
they might be conservative. Reality check needed."
```

---

## Part 10: Activation Checklist

To make IF.INTELLIGENCE fully operational:

- [ ] Document complete procedure (THIS FILE) ✓
- [ ] Create Redis coordination schema for agent findings
- [ ] Build query parser to detect investigation type & depth
- [ ] Implement 8-pass IF.SEARCH as embedded methodology
- [ ] Configure 4-voice IF.GUARD council rules
- [ ] Create output templating system
- [ ] Build confidence calibration logic (95/88/76/62/34%)
- [ ] Test on 5 real queries (Georges partnership, market size, competitive, technical, financial)
- [ ] Document results + iteration patterns
- [ ] Create user guide (1-page quick reference)
- [ ] Deploy to production

---

## Summary

IF.INTELLIGENCE is a complete research framework accessible via simple syntax:

```
if.intelligence{ <your question> }
```

Behind this simple interface sits:
- 4-voice guardian council (guardrails)
- 8-pass epistemological methodology (rigor)
- Multi-agent swarm coordination (speed)
- IF.TTT compliance (auditability)
- Explicit unknowns & dissents (honesty)

**Result:** Defensible, testable intelligence findings with calibrated confidence levels suitable for high-stakes decisions.

---

**Status:** Ready for implementation
**Owner:** InfraFabric research team
**Last Updated:** 2025-11-22
**Version:** 1.0

