# PASS 3 - AGENT 2: Implementation Guide for Angélique
## 30-Day Deployment Plan - Weighted Scoring Model

**Target User:** Angélique (Coordinatrice Fournisseurs)
**Timeline:** 30 days (Weeks 1-4)
**Tool:** Excel (no IT dependency)
**Training Required:** 2 hours
**Expected Workload:** ~20h total (5h per week)

---

## PHASE 1: SETUP (Days 1-10)

### TASK 1.1: Create Excel Scoring Template

**Workload:** 3-4 hours
**Deadline:** Day 3

**Steps:**

1. Open new Excel file: `GEDIMAT_SCORING_MODEL.xlsx`

2. Create following columns:
```
Column A: Depot Name (Évreux, Méru, Gisors)
Column B: Order Volume (tonnes)
Column C: Total Order Volume (tonnes) - same for all rows in grouping
Column D: Supplier Distance to Depot (km) - use existing knowledge
Column E: Client Deadline (days from today) - from order form
Column F: Annual Revenue from Client (€) - from sales records
Column G: Minimum Distance (km) - formula: =MIN(D:D) for all depots in grouping
```

3. Create calculation columns:
```
Column H - Distance Score:
Formula: =(G2/D2)*100
Explanation: (closest distance / actual distance) × 100
Example: (30/40)*100 = 75

Column I - Volume Score:
Formula: =(B2/C2)*100
Explanation: (depot volume / total) × 100
Example: (15/20)*100 = 75

Column J - Urgency Score:
Formula: =MAX(100-(E2-3)*5,0)
Explanation: Subtract 5 points per day over 3 days; min 0
Example: (3 day deadline) = MAX(100-(3-3)*5,0) = 100
Example: (14 day deadline) = MAX(100-(14-3)*5,0) = MAX(45,0) = 45

Column K - Relationship Score:
Formula: =(F2/MAX(F:F))*100
Explanation: (depot revenue / max revenue) × 100
Example: (180k/180k)*100 = 100
Example: (45k/180k)*100 = 25

Column L - FINAL SCORE:
Formula: =(H2*0.25)+(I2*0.30)+(J2*0.35)+(K2*0.10)
Explanation: Weighted sum (Distance 25%, Volume 30%, Urgency 35%, Relationship 10%)
Example: (75*0.25)+(75*0.30)+(45*0.35)+(100*0.10) = 67.0
```

4. Format for readability:
- Highlight column L (FINAL SCORE) in yellow
- Color-code by performance:
  - >75 = Green (excellent depot choice)
  - 60-75 = Yellow (good, check secondary factors)
  - <60 = Red (suboptimal, escalate decision)

5. Save file to: `//shared_drive/GEDIMAT/OPERATIONS/SCORING_MODEL.xlsx`

---

### TASK 1.2: Test on 10 Historical Cases

**Workload:** 3 hours
**Deadline:** Day 5
**Objective:** Validate model accuracy (target: 85%+ match with hindsight-optimal decisions)

**Procedure:**

1. Identify 10 historical order groupings (past 30 days)
   - Minimum 5 should be >10 tonnes (external transport)
   - Mix of urgent and routine orders
   - Include at least 2 multi-depot splits

2. For each case, gather:
   - Dates and depot names
   - Order volumes
   - Supplier and distances
   - Client deadlines
   - Actual routing decision made
   - Actual outcome (on-time? client satisfied?)

3. Input into scoring model
   - Run formula for each case
   - Note which depot scores highest
   - Compare to ACTUAL routing decision made

4. Analyze results:
```
Example Case (Éméris Tuiles):
Actual decision: Méru direct (volume-based)
Model prediction: Gisors direct (urgency-based)
Outcome: Gisors was late (navette delayed)
Model Accuracy: ✓ Correct (would have prevented delay)

Tally: Correct predictions / Total cases = Model Accuracy %
Target: ≥85% (if <80%, adjust urgency weight formula)
```

5. Document findings in file: `VALIDATION_RESULTS.txt`

---

### TASK 1.3: Baseline Metrics Snapshot

**Workload:** 2 hours
**Deadline:** Day 7
**Objective:** Establish pre-implementation baseline for 3-month comparison

**Collect:**

1. **Transport Cost**
   - Current average cost per trajet (>10t)
   - Baseline: ~€900-1,100 per Médiafret order
   - Source: Finance / Médiafret invoices
   - → Save as: `BASELINE_COST.xlsx`

2. **On-Time Delivery Rate**
   - % of orders delivered by promised date
   - Sample: Last 30 days, all depot deliveries
   - Source: Gedimat tracking system
   - → Note: Current estimated 85-90%

3. **Client Satisfaction**
   - Current only measured by complaints (negative feedback)
   - Baseline: 0% proactive satisfaction measurement
   - Source: Observation (pass this to Agent 5 for NPS pilot)

4. **Churn Rate**
   - How many clients stopped ordering (detected late)
   - Baseline: Detection lag ~1-2 months (poor)
   - Source: Sales records analysis

5. Create dashboard template:
```
BASELINE METRICS (Pre-Implementation)
═══════════════════════════════════════
Transport Cost/Trajet:        €950 average
On-Time Delivery %:           87% (30-day sample)
Satisfaction (NPS):           Unknown (establish later)
Churn Detection Lag:          1-2 months
Scoring Model Maturity:       0% (pre-implementation)
═══════════════════════════════════════
Date Captured: Day 7 / 2025-11-23
Next Review:   Day 90 (end of pilot)
```

---

## PHASE 2: TRAINING & DOCUMENTATION (Days 11-20)

### TASK 2.1: 2-Hour Workshop

**Workload:** 2 hours (facilitation)
**Deadline:** Day 12
**Attendees:** Angélique, Coordinators (if any), Finance (optional)

**Agenda:**

| Time | Topic | Details |
|---|---|---|
| 0:00-0:15 | Problem Statement | "Volume rule alone costs €4,050 per delay" |
| 0:15-0:30 | Solution Overview | "Weighted scoring: 5 factors, 1 formula" |
| 0:30-1:00 | Model Demo | Live walkthrough Éméris case (15t + 5t) |
| 1:00-1:30 | Hands-On Practice | Calculate 3 sample cases together |
| 1:30-2:00 | Q&A + Decision Protocol | When to use model, when to override, documentation |

**Materials to Prepare:**
- Printed copies of quick reference (4 pages)
- Excel template on large screen (projector)
- 3 sample cases on printed worksheets (Éméris, Édiliens, Saint-Gobain)
- Decision tree flowchart (poster size)

**Key Messages to Convey:**

1. "This model is a RECOMMENDATION, not a mandate"
   - Angélique can override (with documentation)
   - Goal: Remove guesswork, add transparency

2. "Focus on URGENCY score (35% weight)"
   - If deadline is tight (J+2-3), that depot usually wins
   - If deadline is loose (J+14+), volume/distance matter more

3. "We're measuring what works"
   - Track cost, on-time %, satisfaction for 3 months
   - If model improves outcomes, we scale it
   - If not, we adjust weights or abandon

---

### TASK 2.2: Decision Protocol Documentation

**Workload:** 1.5 hours
**Deadline:** Day 14

**Create SOP (Standard Operating Procedure):**

```
DOCUMENT: SCORING_MODEL_SOP.pdf

WHEN TO USE SCORING MODEL:
═══════════════════════════════════════
✓ Use model if: Total order > 10 tonnes AND multiple depots involved
✗ Don't use if: <10 tonnes (use chauffeur interne, distance optimized)
✗ Don't use if: Single depot can absorb order (no choice needed)

DAILY WORKFLOW:
═══════════════════════════════════════
1. Receive order grouping from supplier (Éméris, Édiliens, etc.)

2. Identify depots requesting volume
   └─ Example: Méru 15t + Gisors 5t = 20t total

3. Open GEDIMAT_SCORING_MODEL.xlsx
   └─ Enter: Volume, Distance, Deadline, Revenue for each depot
   └─ Formula calculates automatically

4. Read FINAL SCORE column
   └─ Highest score = PRIMARY depot (direct delivery)
   └─ Others receive navette redistribution

5. DECISION:
   ├─ If highest score = clearly dominant (>5 point gap): Execute per model
   ├─ If scores tied (within 2-3 points): Use tiebreaker (distance)
   └─ If you disagree with score: Document override reason + actual outcome

6. COMMUNICATE:
   ├─ Call Médiafret: "Deliver to [DEPOT NAME]"
   ├─ Email depots: "[DEPOT] receives direct, navette scheduled [DAY]"
   └─ Note in order file: "Routed via model v1.0, score=[X]"

ESCALATION:
═══════════════════════════════════════
If unsure, call PDG/Finance:
├─ Case: Multi-urgency (3+ depots all time-sensitive)
├─ Action: May justify 2-depot direct delivery (cost premium acceptable)

MONTHLY REVIEW:
═══════════════════════════════════════
1. Export all orders routed via model (>10t)
2. Compare predicted (score) vs actual (outcome)
3. Note: On-time? Cost as expected? Client satisfied?
4. Calculate accuracy % (target: 85%+)
5. Adjust weights if accuracy <80%
```

---

### TASK 2.3: Training Materials Distribution

**Workload:** 1 hour
**Deadline:** Day 15

1. Print materials:
   - Quick reference card (4-page, laminated) → Angélique desk
   - Decision tree flowchart (A3) → Warehouse wall
   - SOP document → Shared drive + printed binder

2. Email notification:
   - Subject: "Gedimat Logistics Decision Model - Phase 1 Go-Live"
   - Attachment: Quick_Reference + Excel template
   - Request: "Pilot starting Week 3, questions?"

---

## PHASE 3: PILOT DEPLOYMENT (Days 21-27)

### TASK 3.1: Live Scoring on Next 5 Orders

**Workload:** 10 minutes per order × 5 = 50 minutes
**Deadline:** Day 27
**Objective:** Validate model in real-time, identify edge cases

**Process:**

For each grouping received:

1. Calculate score (5 minutes)
2. Decide: Execute per model or override? (2 minutes)
3. Log outcome: Date, order ID, score, decision, reason (3 minutes)

**Log Template:**

```
ORDER LOG - PILOT PHASE
═══════════════════════════════════════════════════════════════
Date      | Order ID | Depots | Score Winner | Decision | Notes
─────────────────────────────────────────────────────────────────
11/21     | EM001    | M/G    | Gisors 70    | Execute  | Tight deadline, correct
11/22     | ED002    | E/M    | Évreux 77    | Override | PDG wants M, cost +€50
11/25     | SG003    | G/M    | Gisors 97    | Execute  | Strategic account
11/28     | LA001    | E/M/G  | Multi (2-depot) | Split | 3-way, split optimal
─────────────────────────────────────────────────────────────────

ANALYSIS:
- Execution rate (followed model): 4/5 = 80%
- Override rate: 1/5 = 20% (reasonable)
- Accuracy (hindsight): 4/5 = 80% (acceptable; need 3-month data)
```

---

### TASK 3.2: Weekly Micro-Reviews

**Workload:** 30 minutes/week
**Deadline:** Every Friday (Days 21, 28)

**Checklist:**

- [ ] How many orders >10t processed? ___
- [ ] Model used for how many? ___
- [ ] Overrides? Why? ___
- [ ] Any transport delays? Link to model or other causes? ___
- [ ] Any client complaints? Related to routing? ___
- [ ] Estimated transport cost impact? On-track with baseline? ___

**Share results with PDG:**
- Weekly email: "Pilot scorecard"
- Green: On-track; Yellow: Monitor; Red: Issue needs attention

---

## PHASE 4: MONITORING & FULL DEPLOYMENT (Days 28-90)

### TASK 4.1: Monthly Dashboard (End of Month)

**Workload:** 2-3 hours
**Deadline:** End of each month

**Create spreadsheet with 4 metrics:**

1. **Transport Cost Trend**
   ```
   Month 1 (Baseline):    €950/trajet (30 orders >10t)
   Month 2 (Pilot):       €920/trajet (35 orders, 25 via model)
   Month 3 (Full):        €900/trajet (40 orders, 100% model)

   Target: Maintain €900-950 range (cost-neutral or save €30-50)
   ```

2. **On-Time Delivery %**
   ```
   Month 1 (Baseline):    87% on-time
   Month 2 (Pilot):       92% on-time (+5%)
   Month 3 (Full):        95%+ on-time (target achieved)

   Target: ≥95% (from 87% baseline)
   ```

3. **Model Accuracy %**
   ```
   Month 2 (Pilot):       80% (score matched outcome hindsight)
   Month 3 (Full):        85%+ (validated, ready to scale)

   Target: ≥85%
   ```

4. **Client Satisfaction**
   ```
   Month 1 (Baseline):    Unknown (no proactive measurement)
   Month 2 (Pilot):       Coordinate with Agent 5 NPS survey
   Month 3 (Full):        NPS baseline established, +1-2 points target

   Target: Baseline ≥35, improve to 45+ by Month 6
   ```

**Dashboard Format (Excel + PowerPoint 1-pager):**

```
PILOT RESULTS DASHBOARD - END OF MONTH 2
════════════════════════════════════════════════════════════
METRIC                 | Month 1 | Month 2 | Target  | STATUS
─────────────────────────────────────────────────────────────
Transport Cost/Trajet  | €950    | €920    | <€950   | ✓ GREEN
On-Time Delivery %     | 87%     | 92%     | 95%     | 🟡 YELLOW
Model Accuracy %       | N/A     | 80%     | 85%     | 🟡 YELLOW
Client Satisfaction    | Unknown | TBD     | +2pts   | ⚪ TBD
════════════════════════════════════════════════════════════
RECOMMENDATION: Continue pilot (Month 3 full deployment)
ISSUES: Accuracy 80% (need 85%); adjust urgency weight +2%?
```

---

### TASK 4.2: Weight Adjustment (If Needed)

**Trigger:** If model accuracy <80% after Month 2

**Action:**

```
If too many VOLUME orders were optimal (despite low urgency):
  └─ Increase Volume weight from 30% → 35%
  └─ Decrease Urgency weight from 35% → 30%

If too many DISTANCE orders were optimal:
  └─ Increase Distance weight from 25% → 30%
  └─ Decrease Volume weight from 30% → 25%

Retest on 10 cases with new weights, validate 85%+ accuracy
```

---

### TASK 4.3: Decision - Go/No-Go (Day 90)

**Workload:** 1 hour (presentation prep)
**Deadline:** Day 90 review meeting

**Evaluate:**

✓ **GO criteria (all must be met):**
- Transport cost: Maintained or -€30-50 vs baseline
- On-time delivery: ≥95% (vs 87% baseline)
- Model accuracy: ≥85% (correctly predicts optimal depot)
- Client satisfaction: Positive trend (no churn, increased NPS)
- Operational ease: Angélique reports <10 min per decision

✗ **NO-GO criteria (any failure = pause & debug):**
- Transport cost exceeded baseline by >€50/trajet
- On-time delivery <90%
- Model accuracy <75%
- Client churn detected
- Excessive overrides (>30%) indicate model misalignment

**Presentation to PDG:**
- Show 3-month dashboard
- Compare costs, satisfaction, outcomes
- Recommend: "Scale model nationally" vs "Adjust weights & retry" vs "Archive model"

---

## QUICK REFERENCE FOR ANGÉLIQUE

### Scoring Formula (Memorize)

```
FINAL SCORE = (Distance/100)×25 + (Volume%)×30 + (Urgency)×35 + (Revenue%)×10

Where:
├─ Distance/100 = (smallest distance / this depot distance) × 100
├─ Volume% = (this depot tonnes / total tonnes) × 100
├─ Urgency = MAX(100 - (deadline days - 3) × 5, 0)
└─ Revenue% = (this client revenue / max revenue) × 100

Example: GISORS (5t, 30km, 3-day deadline, €45k revenue) vs MÉRU (15t, 40km, 14-day, €180k)
├─ GISORS: (30/30)×25 + (5/20%)×30 + 100×35 + (45/180%)×10 = 25+7.5+35+2.5 = 70.0 ✓ WINNER
└─ MÉRU: (30/40)×25 + (75%)×30 + 45×35 + 100×10 = 18.75+22.5+15.75+10 = 67.0
```

### Decision Rules (Quick Reference)

```
IF deadline ≤ 5 days → CHECK URGENCY SCORE FIRST
   └─ If Urgency_score ≥ 80 → That depot usually wins (even if smaller volume)

IF deadline ≥ 10 days → CHECK VOLUME & DISTANCE
   └─ Volume (30%) + Distance (25%) dominate decision
   └─ Urgency_score low (irrelevant)

IF SCORES ARE TIED (within 2-3 points):
   └─ Use DISTANCE as tiebreaker (closest to supplier)

IF YOU DISAGREE WITH MODEL:
   └─ Document: "Model suggested X, I chose Y because [reason]"
   └─ Track outcome (was model or your choice better?)
```

### Time Investment Summary

| Activity | Hours | When | Recurring |
|---|---|---|---|
| Initial Setup | 4 | Week 1 | One-time |
| Validation | 3 | Week 1-2 | One-time |
| Training | 2 | Week 2 | One-time |
| Weekly Scoring | 1-2 | Weekly | Yes (pilot) |
| Monthly Dashboard | 2-3 | Monthly | Yes |
| **TOTAL (Month 1)** | **~20h** | — | — |
| **Monthly Recurring** | **~5h** | — | After pilot |

**Translation: ~1.25 hours/week during pilot (minimal impact on current workload)**

---

## SUCCESS METRICS (What We're Measuring)

After 3 months, we'll know if model works by tracking:

1. ✓ **Cost Impact:** Transport savings or cost-neutral (target: -€30-50/trajet or less)
2. ✓ **Service Impact:** On-time delivery 87% → 95%+ (target: +5-10%)
3. ✓ **Client Impact:** NPS +1-2 points, zero churn due to late deliveries (target: ≥45 NPS)
4. ✓ **Operational Impact:** Model used successfully 80%+ of time without excessive overrides (target: <20% override rate)

If all 4 metrics ✓, we recommend full deployment (replace manual arbitrage with model).

---

**Document Status:** Ready for Angélique immediate use
**Prepared by:** PASS 3 Agent 2
**Date:** 16 novembre 2025
**Next Review:** After Day 10 (validation results)
