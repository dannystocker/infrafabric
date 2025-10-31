# Weighted Agent Coordination - Reciprocity Through Results

**Date:** October 31, 2025
**Context:** InfraFabric POC - Contact Discovery System
**Core Insight:** Risky agents shouldn't penalize the system when they fail; they should earn influence when they succeed.

---

## The Problem with Naive Cross-Validation

### Equal-Weight Averaging (Wrong)

**Naive approach:**
```python
# All agents vote equally
scores = [75, 40, 75, 35, 80]  # One risky agent failed (40), another failed (35)
average = sum(scores) / len(scores)  # = 61

Problem: Failed exploration drags down system confidence
```

**Why this is wrong:**
- Risky agents (InvestigativeUser, RecruiterUser) have high variance
- When they fail (score 40), they penalize the entire system
- When they succeed (score 90), their contribution is diluted
- **Result:** System learns to avoid risk, converges on safe mediocrity

**This violates InfraFabric's core principle:** Encourage exploration, reward success, don't punish failure.

---

## The Right Approach: Reciprocity-Based Weighting

### Core Principle

**Agents earn influence through contribution, not authority:**

- **Baseline agents** (always contribute): Weight = 1.0 always
- **Specialist agents** (domain-specific): Weight = 0.0 when irrelevant, 1.5 when successful
- **Exploratory agents** (high-risk/high-reward): Weight = 0.0 when failing, 2.0 when succeeding

**Key insight:** Weight is *earned through results*, not assigned by central authority.

---

## Agent Profiles

### Tier 1: Baseline Agents (Always Counted)

**ProfessionalNetworker** (current SimulatedUser):
```python
{
    'base_weight': 1.0,
    'success_bonus': 0.0,
    'success_threshold': 0,
    'strategy': 'conservative',
    'expected_range': '70-75',
    'reliability': 'high',
    'failure_mode': 'rare',
    'domain': 'universal'
}
```

**Role:** Provides consistent baseline
**Contribution:** Always participates in consensus
**Weighting logic:** Always 1.0 (floor for system)

---

### Tier 2: Specialist Agents (Success-Weighted)

**AcademicResearcher:**
```python
{
    'base_weight': 0.0,           # Silent when irrelevant
    'success_bonus': 1.5,         # Strong voice when successful
    'success_threshold': 80,      # High confidence required
    'strategy': 'specialist',
    'expected_range': '0 or 85-95',
    'reliability': 'bimodal',
    'failure_mode': 'target has no research presence',
    'domain': 'technical executives with academic background'
}
```

**Search strategy:**
- Google Scholar profiles
- arXiv/conference proceedings
- University affiliations
- Research lab contacts
- Co-author networks

**When it succeeds:** Finds verified institutional emails (95/100)
**When it fails:** Returns nothing (0/100), weight = 0.0 (silent)
**Weighting logic:**
```python
if score >= 80:
    weight = 0.0 + 1.5 = 1.5  # Heavy influence
else:
    weight = 0.0  # No influence (doesn't drag down consensus)
```

---

**IntelAnalyst:**
```python
{
    'base_weight': 0.0,
    'success_bonus': 1.2,
    'success_threshold': 75,
    'strategy': 'specialist',
    'expected_range': '0 or 75-85',
    'reliability': 'bimodal',
    'failure_mode': 'private company or non-profit',
    'domain': 'public company executives'
}
```

**Search strategy:**
- SEC filings (10-K, proxy statements)
- Investor relations contacts
- Quarterly earnings call transcripts
- Regulatory disclosures

**When it succeeds:** Finds legally mandated executive contact (80/100)
**When it fails:** No public filings exist (0/100), weight = 0.0
**Weighting logic:**
```python
if score >= 75:
    weight = 0.0 + 1.2 = 1.2
else:
    weight = 0.0
```

---

### Tier 3: Exploratory Agents (High-Risk/High-Reward)

**InvestigativeJournalist:**
```python
{
    'base_weight': 0.0,           # Ignore failures completely
    'success_bonus': 2.0,         # Very heavy when successful
    'success_threshold': 85,      # Only count excellent results
    'strategy': 'exploratory',
    'expected_range': '40 or 90',
    'reliability': 'high variance',
    'failure_mode': 'no information leakage found',
    'domain': 'private/careful executives',
    'expected_success_rate': 0.2  # Succeeds ~20% of time
}
```

**Search strategy:**
- Email signatures in PDFs (`"{name}" email site:*.pdf`)
- Conference speaker lists/bios
- Archived pages (`site:web.archive.org`)
- Press releases with contact info
- Direct quotes ("reach me at", "contact me at")
- Internal directory leaks

**When it succeeds:** Finds direct email that wasn't meant to be public (90/100)
**When it fails:** Finds nothing (40/100), weight = 0.0
**Weighting logic:**
```python
if score >= 85:
    weight = 0.0 + 2.0 = 2.0  # Massive influence (found hidden gem)
else:
    weight = 0.0  # Complete silence (doesn't penalize)
```

**Why high variance is valuable:**
- When successful: Provides information no other agent could find
- When failing: Doesn't drag down consensus
- **Encourages aggressive exploration** without system penalty

---

**RecruiterUser:**
```python
{
    'base_weight': 0.0,
    'success_bonus': 1.3,
    'success_threshold': 80,
    'strategy': 'exploratory',
    'expected_range': '30 or 85',
    'reliability': 'high variance',
    'failure_mode': 'private/executive with no public tech presence',
    'domain': 'accessible technical leaders',
    'expected_success_rate': 0.4
}
```

**Search strategy:**
- GitHub profiles
- Stack Overflow
- Technical forums (Hacker News, Reddit)
- X/Twitter technical community
- Developer conference talks
- Open-source contributions

**When it succeeds:** Finds executives who engage publicly (85/100)
**When it fails:** High-profile execs often private (30/100), weight = 0.0
**Weighting logic:**
```python
if score >= 80:
    weight = 0.0 + 1.3 = 1.3
else:
    weight = 0.0
```

---

**SocialEngineer:**
```python
{
    'base_weight': 0.5,           # Small baseline (provides context)
    'success_bonus': 0.7,
    'success_threshold': 70,
    'strategy': 'exploratory',
    'expected_range': '50-75',
    'reliability': 'medium variance',
    'failure_mode': 'flat organization or startup',
    'domain': 'large organizations with hierarchy',
    'expected_success_rate': 0.6
}
```

**Search strategy:**
- Team pages / organizational charts
- Staff directories
- Assistant names
- Department emails
- Reporting structure
- Gatekeeper identification

**When it succeeds:** Finds path to executive (assistant contact, dept email) (75/100)
**When it fails:** Flat org, no hierarchy visible (50/100)
**Weighting logic:**
```python
if score >= 70:
    weight = 0.5 + 0.7 = 1.2
else:
    weight = 0.5  # Still contributes organizational context
```

**Note:** SocialEngineer has non-zero base weight because organizational intelligence is always valuable, even if indirect.

---

## Weighted Cross-Validation Algorithm

### Implementation

```python
def cross_validate_weighted(agent_results: Dict[str, AgentResult],
                           contact: Contact) -> ValidationResult:
    """
    Cross-validate agent results using reciprocity-based weighting.

    Agents earn influence through successful contribution, not authority.
    Failed exploration doesn't penalize the system.
    """

    weighted_scores = []
    total_weight = 0
    agent_contributions = {}

    for agent_name, result in agent_results.items():
        profile = AGENT_PROFILES[agent_name]

        # Calculate context-aware weight
        if result.score >= profile['success_threshold']:
            # Agent succeeded - earns full weight + bonus
            weight = profile['base_weight'] + profile.get('success_bonus', 0)
            contribution_type = 'success'
        else:
            # Agent failed - only base weight (often 0 for risky agents)
            weight = profile['base_weight']
            contribution_type = 'baseline' if weight > 0 else 'silent'

        if weight > 0:
            weighted_scores.append(result.score * weight)
            total_weight += weight
            agent_contributions[agent_name] = {
                'score': result.score,
                'weight': weight,
                'contribution': result.score * weight,
                'type': contribution_type
            }

    if total_weight == 0:
        # All agents failed
        return ValidationResult(
            confidence=0,
            method='failure',
            reason='No agents provided usable results'
        )

    # Weighted average
    weighted_avg = sum(weighted_scores) / total_weight

    # Agreement analysis
    agreement_count = len([c for c in agent_contributions.values()
                          if c['type'] in ['success', 'baseline']])

    # Confidence calculation
    if agreement_count >= 4:
        confidence = 95  # Strong consensus
    elif agreement_count >= 2:
        confidence = 88  # Moderate consensus
    else:
        confidence = 75  # Single agent

    return ValidationResult(
        confidence=confidence,
        weighted_score=weighted_avg,
        agent_contributions=agent_contributions,
        agreement_count=agreement_count,
        total_weight=total_weight
    )
```

---

## Example Scenarios

### Scenario 1: DoD Contact (Private Executive)

**Target:** Emil Michael (Pentagon CTO)

**Agent Results:**
```python
{
    'ProfessionalNetworker': 75,   # Found DIU contact page
    'AcademicResearcher': 0,       # Not in research databases
    'InvestigativeUser': 90,       # Found direct email in archived press release
    'RecruiterUser': 35,           # No public social presence (expected for DoD)
    'SocialEngineer': 70,          # Found DIU org structure
    'IntelAnalyst': 80,            # Found SEC filings from Uber tenure
}
```

**Weighted Calculation:**
```python
ProfessionalNetworker: 75 * 1.0 = 75.0        (baseline)
AcademicResearcher:    0 * 0.0 = 0.0          (silent - irrelevant domain)
InvestigativeUser:     90 * 2.0 = 180.0       (SUCCESS - found hidden gem!)
RecruiterUser:         35 * 0.0 = 0.0          (silent - failed exploration)
SocialEngineer:        70 * 1.2 = 84.0        (success - organizational context)
IntelAnalyst:          80 * 1.2 = 96.0        (success - regulatory data)

Weighted Average: (75 + 0 + 180 + 0 + 84 + 96) / (1.0 + 0.0 + 2.0 + 0.0 + 1.2 + 1.2)
                = 435 / 5.4
                = 80.6

Agreement: 4 agents contributed (ProfessionalNetworker, InvestigativeUser, SocialEngineer, IntelAnalyst)
Confidence: 95% (strong consensus)
```

**vs. Naive Average:** (75 + 0 + 90 + 35 + 70 + 80) / 6 = 58.3

**Key insight:** InvestigativeUser's success is properly valued (weight 2.0), failed exploratory agents don't drag down consensus.

---

### Scenario 2: Academic CTO (Public Researcher)

**Target:** Amin Vahdat (Google Cloud VP)

**Agent Results:**
```python
{
    'ProfessionalNetworker': 75,   # Found LinkedIn
    'AcademicResearcher': 95,      # Google Scholar verified email
    'InvestigativeUser': 50,       # Nothing hidden (he's accessible)
    'RecruiterUser': 85,           # Active on Twitter/X
    'SocialEngineer': 65,          # Google team directory
    'IntelAnalyst': 70,            # Google IR contact
}
```

**Weighted Calculation:**
```python
ProfessionalNetworker: 75 * 1.0 = 75.0        (baseline)
AcademicResearcher:    95 * 1.5 = 142.5       (SUCCESS - perfect domain match!)
InvestigativeUser:     50 * 0.0 = 0.0          (silent - failed to find hidden info)
RecruiterUser:         85 * 1.3 = 110.5       (success - public tech presence)
SocialEngineer:        65 * 0.5 = 32.5        (baseline - some org context)
IntelAnalyst:          70 * 0.0 = 0.0          (below threshold - didn't count)

Weighted Average: (75 + 142.5 + 0 + 110.5 + 32.5 + 0) / (1.0 + 1.5 + 0.0 + 1.3 + 0.5 + 0.0)
                = 360.5 / 4.3
                = 83.8

Agreement: 4 agents contributed
Confidence: 95%
```

**vs. Naive Average:** (75 + 95 + 50 + 85 + 65 + 70) / 6 = 73.3

**Key insight:** Specialist AcademicResearcher dominates (weight 1.5) because this is its perfect domain.

---

### Scenario 3: Startup CEO (Mixed Accessibility)

**Target:** Jeremy O'Brien (PsiQuantum CEO)

**Agent Results:**
```python
{
    'ProfessionalNetworker': 75,   # Company contact page
    'AcademicResearcher': 92,      # Strong research background (quantum physics)
    'InvestigativeUser': 85,       # Found conference speaker email
    'RecruiterUser': 70,           # Some public presence
    'SocialEngineer': 60,          # Startup - flat org
    'IntelAnalyst': 0,             # Private company - no SEC filings
}
```

**Weighted Calculation:**
```python
ProfessionalNetworker: 75 * 1.0 = 75.0
AcademicResearcher:    92 * 1.5 = 138.0       (SUCCESS - research domain)
InvestigativeUser:     85 * 2.0 = 170.0       (SUCCESS - found conference email)
RecruiterUser:         70 * 0.0 = 0.0          (below 80 threshold)
SocialEngineer:        60 * 0.5 = 30.0        (baseline only)
IntelAnalyst:          0 * 0.0 = 0.0          (silent - private company)

Weighted Average: (75 + 138 + 170 + 0 + 30 + 0) / (1.0 + 1.5 + 2.0 + 0.0 + 0.5 + 0.0)
                = 413 / 5.0
                = 82.6

Agreement: 4 agents contributed
Confidence: 95%
```

**vs. Naive Average:** (75 + 92 + 85 + 70 + 60 + 0) / 6 = 63.7

**Key insight:** Multiple specialists succeeded (Academic + Investigative), their combined weight drives high confidence.

---

## Why This is InfraFabric's Reciprocity Mechanism

### Reciprocity = Influence Through Contribution

**Traditional systems:**
- Central authority assigns weights
- All agents treated equally OR
- Weights hardcoded in advance

**InfraFabric approach:**
- Weights emerge through results
- Successful contribution → Earn influence
- Failed exploration → No penalty
- **No central authority deciding value**

### The Coordination Properties

**1. Encourages Risk-Taking**
```
Risky agent thinks: "If I try and fail (score 40), I'm weighted 0.0 - no harm to system"
Risky agent thinks: "If I succeed (score 90), I'm weighted 2.0 - huge contribution!"

Result: Agents explore aggressively without fear of penalizing consensus
```

**2. Specialist Agents Flourish**
```
AcademicResearcher doesn't waste effort on non-research targets
When domain matches → Contributes heavily (weight 1.5)
When domain mismatches → Silent (weight 0.0)

Result: Specialists can focus on their strengths without forced participation
```

**3. Baseline Stability**
```
ProfessionalNetworker always contributes (weight 1.0)
Provides floor - system never goes to zero confidence

Result: Conservative agents ensure minimum reliability
```

**4. Emergent Quality**
```
System automatically selects best information:
- Multiple specialists agree → Very high confidence (95%)
- Risky agent finds unique info → Weighted heavily (2.0)
- Failed explorations → Ignored (0.0)

Result: Quality emerges from diversity, not enforcement
```

### Parallel to Full InfraFabric

| Contact Discovery POC | Enterprise InfraFabric |
|----------------------|------------------------|
| Agent earns weight through successful results | AI earns reputation through useful coordination |
| Risky exploration not penalized | Novel approaches encouraged |
| Specialist agents weighted by domain | Quantum vs classical optimized for their substrates |
| Baseline agents provide stability | Core protocols ensure minimum reliability |
| No central authority assigns value | Reciprocity ledger tracks contribution objectively |

---

## Implementation Notes

### Configuration

**Agent profiles defined in:**
```python
AGENT_PROFILES = {
    'ProfessionalNetworker': {...},
    'AcademicResearcher': {...},
    'InvestigativeUser': {...},
    'RecruiterUser': {...},
    'SocialEngineer': {...},
    'IntelAnalyst': {...},
}
```

### Success Thresholds

**Calibration needed:**
- Too low (60): Mediocre results get weighted heavily
- Too high (95): Specialists rarely contribute
- **Recommended:** 75-85 range for most agents

**Tuning approach:**
1. Run on diverse contact set
2. Measure specialist success rates
3. Adjust thresholds to ~30-50% success rate per specialist
4. Ensure exploratory agents succeed ~20% of time

### Future Enhancements

**1. Adaptive Thresholds**
```python
# Learn optimal thresholds from data
if specialist.recent_success_rate > 0.7:
    threshold += 5  # Raise bar
elif specialist.recent_success_rate < 0.2:
    threshold -= 5  # Lower bar
```

**2. Context-Aware Weighting**
```python
# Weight based on contact persona
if contact.sector == 'Defense':
    profiles['InvestigativeUser']['success_bonus'] = 2.5  # Even higher for DoD
```

**3. Temporal Weighting**
```python
# Recent successes weighted more heavily
weight *= (1 + recent_success_rate * 0.5)
```

---

## Key Takeaways

**1. Failed exploration shouldn't penalize the system**
- Risky agents get weight 0.0 when failing
- Encourages aggressive search strategies
- No fear of "dragging down the average"

**2. Success should be rewarded proportionally**
- Specialists earn 1.5x when successful
- Exploratory agents earn 2.0x when finding hidden gems
- **Incentivizes valuable contribution**

**3. This demonstrates InfraFabric's reciprocity principle**
- Influence earned through results, not authority
- Diverse strategies coexist without forced uniformity
- Quality emerges from coordination, not control

**4. Graceful degradation through diversity**
- If specialist fails → Baseline agents provide floor
- If risky agent fails → Doesn't harm consensus
- If all fail → System reports honestly (confidence 0)

---

## Next Steps

**1. Implement weighted cross-validation in POC code**
- Add AGENT_PROFILES configuration
- Update CrossValidator class
- Test on existing 9 contacts

**2. Build the 5 new agents**
- InvestigativeJournalist
- AcademicResearcher
- RecruiterUser
- SocialEngineer
- IntelAnalyst

**3. Compare naive vs weighted results**
- Show how weighting improves consensus quality
- Demonstrate risk-taking without penalty
- Validate reciprocity mechanism

**4. Document for InfraFabric paper**
- Section on reciprocity through results
- POC as validation of coordination principles
- "Encouragement through architecture" argument

---

**This is InfraFabric at toy scale: diverse agents coordinating through reciprocity, not authority.**
