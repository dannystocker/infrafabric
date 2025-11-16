# Quick Reference: Unsourced Numbers Summary
**One-page audit for stakeholder briefing**

---

## CRITICAL CLAIMS (Must Fix Before Presentation)

| Rank | Number | File:Line | Status | Impact | Fix |
|------|--------|-----------|--------|--------|-----|
| 🔴 1 | **50K€ gains** | `if_ttt_audit.md:39` | NONE | Makes ROI 10× claim | Derive from actual affrètement 2024 data |
| 🔴 2 | **5K€ investment** | `if_ttt_audit.md:39` | NONE | Makes ROI 10× claim | Itemize: dev cost + training + tools |
| 🔴 3 | **10× ROI** | `if_ttt_audit.md:39` | DERIVED | Unsourced numbers produce this | Recalculate with verified costs |
| 🔴 4 | **3.3M€ CA assumption** | `ENHANCEMENT:263` | ASSUMED | Wrong CA = wrong savings calc | **MUST CONFIRM with Gedimat** |
| 🔴 5 | **30K€/quarter affrètement** | `ENHANCEMENT:306` | NONE | Baseline for all ROI | Extract Médiafret invoices Q1-Q3 2024 |
| 🔴 6 | **120K€/year affrètement** | `CONSEIL:243` | NONE | Annual budget = phantom | Sum 12 months Médiafret invoices |
| 🔴 7 | **30% "inutile" shipments** | `GARDIENS:235` | NONE | Justifies 15K€ savings | Audit 100+ shipments for redundancy |
| 🔴 8 | **5 weeks payback** | `if_ttt_audit.md:40` | DERIVED | Depends on unsourced ROI | Recalculate once ROI is verified |

---

## HIGH-RISK BASELINES (Need Real Data)

| Metric | Claim | Source | Issue | Verification |
|--------|-------|--------|-------|--------------|
| **Taux service** | ~88% | ESTIMATED | No delivery audit done | Audit 50 orders: promised vs actual date |
| **NPS Score** | ~35 | INFORMAL | Inferred from complaints, not survey | Survey 20 clients: formal NPS 0-10 scale |
| **Logistics cost** | 6.5% of CA | ASSUMED | No breakdown shown (transport only? + storage?) | Define scope, calculate from P&L |
| **Competitor NPS** | 45-50 range | SOURCES | Benchmarks cited but links untested | Test PDFs: Leroy Merlin, Saint-Gobain, Kingfisher |

---

## SOURCED-BUT-QUESTIONABLE

| Range | File | Source Status | Issue |
|-------|------|--|---------|
| 92-95% service target | `ENHANCEMENT:134` | Cited (Xerfi p.78) | Is 92-95% their range or our synthesis? |
| 4-6% cost/CA | `ENHANCEMENT:261` | Cited (Xerfi/FMB) | Two sources agree on 4-6% or interpreted differently? |
| 45-50 NPS range | `ENHANCEMENT:145` | Industry estimates | Average of Leroy/Point P/Castorama or separate study? |
| 40/30/20/10 weights | `PROMPT:199` | NONE | Academic source for these weights? Or propose them? |

---

## TIMELINE TO CREDIBILITY

```
TODAY (16 Nov)                    NEXT WEEK (23 Nov)           LATE NOV (30 Nov)
┌──────────────────┐              ┌────────────────┐           ┌──────────────┐
│ Current: 86/100  │  ──ENHANCE──> │ 90/100 + Data  │ ─MERGE──> │ 95/100 READY │
│                  │  (Sonnet)     │ Collection     │ (Compile) │ FOR BOARD    │
│ Financial: 40/100│              │ (Parallel)     │           │              │
└──────────────────┘              └────────────────┘           └──────────────┘
                                        |
                                    Médiafret invoices
                                    CA confirmation
                                    Delivery audit (50)
                                    NPS survey (20 clients)
```

---

## GEDIMAT DATA FORM (To Request)

**For Angélique/Finance Director:**

```
1. FINANCIAL
   [ ] Gedimat 2024 year-to-date revenue: _____ €
   [ ] Médiafret invoices (6-12 months available): _____ €/month

2. OPERATIONAL
   [ ] 50 recent delivery orders with:
       - Date promised to client
       - Date actually delivered
       - Status (on-time yes/no, days late/early)

3. CUSTOMER
   [ ] Customer contact list (20 B2B clients for NPS survey)

4. VALIDATION
   [ ] Does our 88% service rate match your perception?
   [ ] Does our 35 NPS match your informal feedback?
   [ ] Do you believe 25-30% reduction is achievable with scoring?
```

---

## RISK RANKING (What Can Sink Credibility)

🔴 **CRITICAL** (Gedimat will reject immediately):
- 50K€ gains unsourced
- 5K€ investment unsourced
- 30K€ quarterly baseline unsourced
- CA = 3.3M€ not verified

🟡 **HIGH** (Will be questioned):
- 88% service baseline = estimate not audit
- 35 NPS = informal not surveyed
- Leroy Merlin/Point P metrics = links untested
- 40/30/20/10 weights = no academic source

🟢 **MEDIUM** (Can be clarified):
- Competitor benchmark ranges
- Cause allocation percentages (marked with "?" already)
- Success metrics (marked "targets" already)

---

## DECISION: What to Present?

**Scenario A: Present THIS WEEK (86/100 version)**
- ✅ Use for operational guidance (Angélique's tools = solid)
- ❌ Do NOT cite as Board document
- ⚠️ Disclaimer: "Financial estimates pending data validation"

**Scenario B: Present AFTER ENHANCEMENT (90/100 version)**
- ✅ Academic + legal sources added
- ⚠️ Gedimat financial numbers still estimated
- ⚠️ Good for "proof of concept" not Board approval

**Scenario C: Present AFTER DATA COLLECTION (95/100 version)**
- ✅ All numbers tied to real 2024 invoices
- ✅ ROI backed by actual audit
- ✅ Board-ready
- ⏱️ Takes 2-3 weeks (run parallel)

---

## NEXT MEETING AGENDA

**If talking to Gedimat (Angélique, PDG, Directeur):**

1. **Compliment:** "Dossier méthodologie excellente, 8 passes IF.search validées, conseil 26 voix"
2. **Problem:** "But all numbers >5K€ need your 2024 data to be credible"
3. **Ask:** "Can you provide Médiafret invoices YTD + 50 recent deliveries + 20 client contacts?"
4. **Timeline:** "With this data, we'll have Board-ready version end of November"
5. **Parallel:** "We also start Enhancement this week (add legal + academic sources)"
6. **Offer:** "Meanwhile, Angélique can start using scoring tool template (Excel) - no risk"

---

## Red Flags to Avoid in Conversation

❌ "This is conservative estimate" - if unsourced, it's not an estimate
❌ "Industry average shows 50K€ savings" - which industry? Which average?
❌ "ROI 10× is typical for this kind of optimization" - for whom? cite examples
❌ "Service rate ~88%" without audit = fiction
❌ "This is what our research shows" - show it (cite pages)

✅ "Based on Xerfi 4DIS77 p.78, GSB distribution typically achieves 92-95% service"
✅ "Point P reports 93.5% in their 2023 annual report (we verified page 112)"
✅ "Our audit of 50 Gedimat deliveries shows 88% on-time, suggesting 4-point improvement is realistic"
✅ "We estimate 25-30% reduction in redundant shipments, worth 25-45K€/year pending invoice verification"

---

## Files to Reference in Audit

1. **Master audit:** `/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/AUDIT_UNSOURCED_NUMBERS.md`
   - 23 unsourced claims mapped to file:line
   - 8 CRITICAL, 7 HIGH, 2 MEDIUM, 6 LOW

2. **Executive findings:** `/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/AUDIT_SUMMARY_CRITICAL_FINDINGS.md`
   - 8 "credibility bombs" explained in detail
   - Action plan with templates
   - Scenario analysis (86 vs 90 vs 95 score)

3. **This file:** `QUICK_REFERENCE_UNSOURCED_CLAIMS.md`
   - One-page reference
   - Quick decision tree
   - What to ask Gedimat

---

**Status:** AUDIT COMPLETE - Ready for stakeholder discussion
**Confidence:** HIGH - All findings backed by line numbers, reproducible
**Next action:** Send data form to Gedimat OR approve Enhancement execution OR both?
