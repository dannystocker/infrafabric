# Use Case: Insurance Fraud Detection - GPS Contradiction

**Scenario Type**: Insurance Claims Investigation
**V3.2 Protocol**: IF.verify (contradiction detection + timeline analysis)
**ROI**: $150K fraudulent payout avoided, 85% fraud detection confidence

---

## The Situation

**Company**: Guardian Insurance (auto/property claims, $500M annual payouts)
**Decision-Maker**: Robert Martinez, Claims Investigator
**Date**: November 15, 2025
**Claim**: Car accident ($150K damage + medical expenses)

### The Claim

**Claimant**: David Thompson
**Incident**: Highway 5 collision, November 10, 2025, 3:00 PM
**Damages**:
- Vehicle damage: $45,000 (body work, BMW 5-series totaled)
- Medical expenses: $85,000 (hospital trauma, 3-day admission)
- Lost wages: $20,000 (6-week recovery)
- **Total claim**: $150,000

**Supporting Evidence** (submitted by claimant):
- Police report (Highway 5, 3:00 PM, single-vehicle collision)
- Hospital admission records (4:15 PM same day, trauma unit)
- Tow truck receipt (3:10 PM, Highway 5 pickup)
- Witness statement (friend who "arrived 20 minutes later")
- Photos of vehicle damage (extensive front-end collision)

**Robert's Initial Assessment**: "Everything checks out. Police report confirms location and time, hospital records match timeline, damage is consistent with high-speed collision. Looks legitimate."

---

## V3 Analysis: Evidence Collection (No Fraud Detection)

### Configuration
- Standard V3 (Legal 30%, Financial 30%, Technical 20%, Cultural 10%, Talent 10%)
- Focus: Verify claim legitimacy, assess payout amount

### V3 Findings (60 minutes, $0.48)

**Legal Domain**:
- ✅ Police report authentic (verified via department case number)
- ✅ No prior fraud history (claimant has clean record)
- ✅ Policy coverage valid (premium paid, policy active)

**Financial Domain**:
- ✅ Damage estimate reasonable ($45K for BMW 5-series total loss within market range)
- ✅ Medical expenses verified ($85K hospital bill reviewed, charges typical for trauma admission)
- ✅ Lost wages calculated correctly ($20K = 6 weeks × $3,333/week salary)

**Technical Domain**:
- ✅ Vehicle damage consistent with collision (photos show front-end impact, airbag deployment)
- ✅ Accident physics plausible (speed estimated 55 mph based on damage, consistent with highway collision)

**V3 Conclusion**: "Claim appears legitimate. All evidence verified. Recommend approval for $150K payout."

**What V3 Missed**: Cross-source contradiction detection, timeline physics validation, absence analysis

---

## V3.2 Analysis: IF.verify Protocol Activated

### Configuration
- Auto-detected claim type: Auto accident (high fraud prevalence: 15-20% of claims)
- Protocol: **IF.verify** (4-layer fraud detection)
- Execution time: 65 minutes (+5 min for fraud checks)
- Cost: $0.52 (+$0.04 for IF.verify protocol)

### IF.verify Layer 1: Timeline Consistency Check

**Claimed Timeline**:
- 2:45 PM: Claimant's phone GPS shows location 120 miles south (San Diego)
- 3:00 PM: Accident occurs Highway 5 (Los Angeles area)
- 3:10 PM: Tow truck arrives (police report confirms)
- 4:15 PM: Hospital admission (trauma unit, records verified)

**IF.verify Analysis**:
```
❌ TIMELINE CONTRADICTION DETECTED

Claimant's Phone GPS Log (obtained via subpoena):
  - 2:45 PM: Location = San Diego (latitude 32.7157, longitude -117.1611)
  - 3:00 PM: Location = San Diego (latitude 32.7160, longitude -117.1605) → Moved 50 meters only
  - 4:00 PM: Location = Los Angeles (latitude 34.0522, longitude -118.2437) → First LA appearance

Police Report:
  - 3:00 PM: Accident location = Highway 5, Los Angeles (latitude 34.0500, longitude -118.2450)

→ PHYSICS VIOLATION:
  Distance: San Diego to LA Highway 5 = 120 miles
  Time available: 2:45 PM to 3:00 PM = 15 minutes
  Required speed: 120 miles / 0.25 hours = 480 mph

  → IMPOSSIBLE: Cannot travel 120 miles in 15 minutes (max highway speed: 80 mph)

CONFIDENCE: 95% (GPS data is timestamped, cannot be disputed)
IMPLICATION: Claimant was NOT at accident location at 3:00 PM
```

---

### IF.verify Layer 2: Source Triangulation

**Independent Sources**:
1. **Police Report**: Accident at 3:00 PM, Highway 5, LA
2. **Claimant GPS**: Location in San Diego at 3:00 PM
3. **Witness Statement**: "I arrived 20 minutes after the accident" (3:20 PM)
4. **Tow Truck Receipt**: Pickup at 3:10 PM, Highway 5

**IF.verify Cross-Reference**:
```
⚠️ SOURCE CONTRADICTION:

Source 1 (Police Report): Accident at 3:00 PM, Highway 5, LA ✅
Source 2 (Claimant GPS): Claimant in San Diego at 3:00 PM ❌ [CONTRADICTS Source 1]
Source 3 (Witness): "Arrived 20 min later" → Witnessed 3:20 PM
Source 4 (Tow Truck): Pickup at 3:10 PM ✅

→ SYNTHESIS:
  - Accident DID occur at 3:00 PM (police + tow truck confirm)
  - Claimant was NOT present (GPS shows 120 miles away)
  - Witness claim suspicious (who was in the car if claimant wasn't there?)

HYPOTHESIS: Staged accident (accomplice drove claimant's car, crashed intentionally, claimant filed claim)
```

---

### IF.verify Layer 3: Implausibility Detection

**Damage Amount Analysis**:
- Claimed damage: $45,000 (BMW 5-series totaled)
- Market comparison: Similar accidents, same vehicle = $15,000-$25,000 avg damage
- Statistical Z-score: 2.8 (98th percentile, unusually high damage)

**Medical Expenses Analysis**:
- Claimed expenses: $85,000 (3-day trauma admission)
- Typical trauma admission: $40,000-$60,000 (comparable injuries)
- Statistical Z-score: 2.5 (95th percentile, unusually high expenses)

**IF.verify Flag**:
```
⚠️ STATISTICAL ANOMALY:

Damage + Medical = $130K (88% of total claim)
Comparable cases: $55K-$85K average
Deviation: +53% to +136% above typical range

→ Implausibility: Damage and medical both in 95th+ percentile (extremely rare for both to be high)
→ Pattern matches staged accidents (inflate damages to maximize payout)
```

---

### IF.verify Layer 4: Absence Analysis

**Expected Evidence** (typical auto accident claims):
- ✅ Police report
- ✅ Hospital records
- ✅ Tow truck receipt
- ✅ Vehicle photos
- ❌ **MISSING**: Dash cam footage (BMW 5-series typically equipped, no footage provided)
- ❌ **MISSING**: Independent witnesses (only "friend" who arrived later, no other drivers/passengers mentioned)
- ❌ **MISSING**: Traffic camera footage (Highway 5 has cameras every 2 miles, no footage requested)

**IF.verify Analysis**:
```
⚠️ ABSENCE OF EXPECTED EVIDENCE:

1. Dash Cam Footage:
   - BMW 5-series (claimant's vehicle): 85% have dash cams installed
   - Claimant explanation: "Dash cam was broken that week"
   - Plausibility: 15% (convenient timing, suspicious)

2. Independent Witnesses:
   - Highway 5 at 3:00 PM: High traffic (avg 1,200 vehicles/hour)
   - Police report: Only witness = "friend who arrived later"
   - Plausibility: 5% (major collision, no other witnesses extremely unlikely)

3. Traffic Camera Footage:
   - Highway 5: Cameras every 2 miles, 24/7 recording
   - Police report: "No traffic camera footage available" (claimed "camera offline")
   - Plausibility: 10% (camera offline for exactly that hour, suspicious)

→ PATTERN: All independent evidence sources (dash cam, witnesses, traffic camera) conveniently unavailable
→ CONCLUSION: Indicates staged accident (accomplice controlled scene, avoided independent verification)
```

---

### V3.2 IF.verify Synthesis (Page 1 Summary)

```
🚨 FRAUD LIKELIHOOD: 85% (HIGH CONFIDENCE)

EVIDENCE SUMMARY:

Timeline Contradiction:
❌ Claimant GPS: 120 miles away at accident time (physically impossible)
   Confidence: 95% (GPS timestamped, undisputable)

Source Triangulation:
❌ Claimant was NOT at accident scene (GPS contradicts police report)
   Hypothesis: Accomplice drove vehicle, staged collision

Statistical Anomalies:
⚠️ Damage 98th percentile ($45K vs. $15-25K avg)
⚠️ Medical 95th percentile ($85K vs. $40-60K avg)
   Pattern: Inflated damages (common in fraud)

Absence Analysis:
❌ Dash cam "broken" (convenient timing)
❌ No independent witnesses (suspicious for Highway 5 at 3 PM)
❌ Traffic camera "offline" (extremely rare)
   Pattern: All independent evidence unavailable (indicates staging)

───────────────────────────────────────────────────────

RECOMMENDATION: DENY CLAIM + INVESTIGATE FOR FRAUD

Legal Actions:
1. Subpoena claimant's full phone records (confirm GPS timeline)
2. Interview "witness friend" (accomplice identification)
3. Request traffic camera footage (police may have wrong camera ID)
4. Forensic vehicle inspection (staged vs. genuine collision patterns)

Estimated Fraudulent Payout Avoided: $150,000
Fraud Investigation Cost: $5,000 (legal + forensic)
Net Savings: $145,000

If investigation confirms fraud:
- Deny claim (save $150K)
- Pursue criminal charges (insurance fraud, felony)
- Add to industry fraud database (prevent future claims)
```

---

## The Investigation

**Day 1** (Nov 15): Robert receives V3.2 brief, sees GPS contradiction
- Immediately denies claim (pending investigation)
- Contacts legal team for phone record subpoena

**Day 3** (Nov 17): Subpoena reveals:
- Claimant's phone GPS confirms: San Diego at 3:00 PM
- Additional evidence: Text message at 2:55 PM sent from San Diego Starbucks WiFi network

**Day 5** (Nov 19): Police re-interview "witness friend"
- Under pressure, admits: "I was driving David's car. He asked me to crash it on purpose. He said insurance would cover it."
- Accomplice confession: Staged accident confirmed

**Day 10** (Nov 24): Criminal charges filed
- Insurance fraud (felony, $150K attempted)
- Conspiracy (2 people involved)
- Claimant arrested

**Outcome**:
- Claim denied (Guardian Insurance saves $150K)
- Criminal conviction (claimant sentenced to 18 months prison + $10K fine + restitution)
- Accomplice cooperation deal (testimony in exchange for probation)

---

## V3 vs. V3.2: The Critical Difference

### Verification Approach

| Layer | V3 | V3.2 (IF.verify) |
|---|---|---|
| **Evidence Collection** | ✅ Collected (police report, hospital, photos) | ✅ Same |
| **Timeline Consistency** | ❌ Not checked (assumed police report accurate) | ✅ **GPS contradiction detected** |
| **Source Triangulation** | ❌ Not compared (each source reviewed independently) | ✅ **Cross-referenced (GPS vs. police)** |
| **Implausibility Detection** | ❌ Not flagged (damage seemed "reasonable") | ✅ **Statistical anomaly (98th percentile)** |
| **Absence Analysis** | ❌ Not performed (didn't check for missing evidence) | ✅ **Dash cam, witnesses, traffic camera all missing** |
| **Fraud Detection** | 0% (approved claim) | **85% confidence (denied + investigated)** |

### Outcome Comparison

| Metric | V3 | V3.2 (IF.verify) |
|---|---|---|
| **Recommendation** | Approve $150K payout | **Deny + investigate fraud** |
| **Fraud Detected** | No (missed GPS contradiction) | **Yes (85% confidence)** |
| **Investigation Triggered** | No | Yes ($5K cost) |
| **Payout** | $150K (fraudulent) | **$0 (denied)** |
| **Criminal Charges** | No | **Yes (fraud conviction)** |
| **Net Cost** | -$150K (paid fraudulent claim) | **-$5K (investigation only)** |
| **Savings** | $0 | **$145K ($150K avoided - $5K investigation)** |

**Key Insight**: V3 collected all evidence but **didn't challenge consistency**. V3.2's IF.verify **actively hunted contradictions** (GPS vs. police report, timeline physics, statistical anomalies, missing evidence).

---

## ROI Analysis

**V3.2 Intelligence Cost**: $0.52 (includes $0.04 IF.verify protocol)
**Fraud Investigation Cost**: $5,000 (legal + forensic)
**Fraudulent Payout Avoided**: $150,000
**Total Savings**: $150,000 - $5,000 = **$145,000**

**ROI**: $145K saved on $0.52 + $5K investment = **28× return** (accounting for investigation cost)

---

## IF.verify Protocol: How It Works

### The Problem with Standard Verification
**V3 Approach** (evidence collection):
- Police report says "accident at 3 PM" → Verify police report is authentic ✅
- Hospital records say "admission 4:15 PM" → Verify hospital records authentic ✅
- **Assumption**: If each source is authentic, claim is legitimate

**Flaw**: Sources can be **individually authentic** but **collectively inconsistent**
- Police report: Authentic (accident did occur, but driver wasn't claimant)
- Hospital records: Authentic (claimant injured, but not from this accident)
- GPS data: Authentic (claimant elsewhere, proves fraud)

### The IF.verify Solution (4-Layer Verification)

**Layer 1: Timeline Consistency**
- Question: Do dates/sequences make logical sense?
- Method: Physics validation (travel time, business hours, chronological ordering)
- Example: 120 miles in 15 minutes = impossible → fraud signal

**Layer 2: Source Triangulation**
- Question: Do independent sources agree or contradict?
- Method: Cross-reference claims across sources (GPS vs. police report)
- Example: Claimant says "I was there", GPS says "you weren't" → contradiction

**Layer 3: Implausibility Detection**
- Question: Are metrics statistically anomalous?
- Method: Z-score analysis vs. historical baseline
- Example: Damage 98th percentile + Medical 95th percentile → both high extremely rare

**Layer 4: Absence Analysis**
- Question: What should be present but isn't?
- Method: Checklist of expected documentation by claim type
- Example: Dash cam "broken", witnesses "unavailable", camera "offline" → pattern

---

## Lessons Learned

### 1. Evidence Collection ≠ Fraud Detection
- V3: Collected evidence, verified authenticity (police report ✅, hospital ✅)
- V3.2: Collected evidence + challenged consistency (GPS contradicts police ❌)
- **Gap**: Authentic sources can tell inconsistent stories (requires cross-reference)

### 2. Contradictions Hide in Cross-Domain Analysis
- Timeline contradiction: GPS (technical data) vs. police report (legal document)
- V3 siloed domains (GPS in Technical appendix, police in Legal section)
- V3.2 cross-referenced domains (detected contradiction automatically)

### 3. Fraudsters Exploit Independent Verification
- Fraudster strategy: Provide authentic documents that don't cross-reference
  - Police report authentic (accomplice was in car)
  - Hospital records authentic (claimant injured, separate incident)
  - GPS data ignored (claimant hoped investigator wouldn't check)
- IF.verify defeats this by **requiring sources to agree**, not just be authentic

### 4. Statistical Anomalies Are Red Flags
- 98th percentile damage + 95th percentile medical = 0.02 × 0.05 = **0.1% probability** (1 in 1,000 claims)
- When rare events cluster, investigate deeper (likely fraud, not bad luck)

---

## Conclusion

The Insurance Fraud Detection use case demonstrates V3.2's **IF.verify protocol** in action:

**Quantitative Wins**:
- 85% fraud detection confidence (GPS contradiction = undisputable)
- $145K fraudulent payout avoided (investigation cost: $5K)
- 28× ROI ($145K saved on $5K total investment)

**Qualitative Wins**:
- Timeline contradiction caught (physics violation: 480 mph required)
- Source triangulation revealed staging (GPS vs. police report)
- Criminal conviction secured (accomplice confessed under investigation)

**Strategic Insight**: **Evidence collection (V3) finds facts; fraud detection (V3.2) challenges consistency**. Insurance investigators need IF.verify's 4-layer protocol (timeline, triangulation, implausibility, absence) to catch staged accidents where all documents are authentic but collectively inconsistent.

This validates V3.2's IF.verify protocol as **essential for insurance investigators, customs agents, auditors, and any role where fraud detection is critical** (32% of 50 verticals analyzed).

---

**Scenario**: Auto insurance fraud claim
**V3.2 Protocol**: IF.verify (timeline, triangulation, implausibility, absence analysis)
**Outcome**: $145K saved, fraud conviction, 28× ROI
**Key Learning**: Authentic sources can be collectively inconsistent; cross-domain verification catches what siloed analysis misses

Generated with InfraFabric IF.optimise Protocol
