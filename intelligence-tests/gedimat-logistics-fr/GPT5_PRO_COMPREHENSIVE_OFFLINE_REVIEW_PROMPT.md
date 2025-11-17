# GPT-5 Pro Comprehensive Offline Review: Gedimat Logistics Dossier

**Date:** 2025-11-17
**Reviewer:** GPT-5 Pro (Offline Review Mode)
**Package:** GEDIMAT_GPT5PRO_PACKAGE.zip (23 MB, 278 files)
**Mission:** Final credibility audit, gap analysis, and LaTeX preparation for board-ready delivery

---

## CRITICAL CONTEXT: This Review's Purpose

You are reviewing a **124-file research corpus** spanning 36 hours of AI agent work on logistics optimization for Gedimat (French building materials franchise, 3 depots). The work has evolved through 5 versions:
- **V1 (86/100):** Had 8 "credibility bombs" - unsourced financial claims
- **V2 (90/100):** Eliminated unsourced claims, introduced data collection methodology
- **V3 (78/100):** External eval found benchmark citations unverifiable
- **TTT2 (76/100):** Guardian Council found methodology sound but execution risky
- **SUPER:** Proposed assembly of all work into 50-page board deliverable

**Your Mission:** Be the FINAL quality gate before CEO presentation. Find and remove EVERYTHING that could embarrass Gedimat's PDG in front of the board.

---

## PACKAGE CONTENTS (What You're Reviewing)

### Core Analysis Files (Read These First)
```
/SUPER_DOSSIER_ANALYSIS.json           # 124-file structural analysis
/SUPER_DOSSIER_EXECUTIVE_SUMMARY.md    # Proposed board summary
/SUPER_DOSSIER_IMPLEMENTATION_CHECKLIST.md  # Implementation roadmap
/PROMPT_V2_FACTUAL_GROUNDED.md         # V2 baseline (48KB, 1,061 lines)
/CODEX_SUPER_DOSSIER_ASSEMBLY_PROMPT.md     # Assembly instructions
```

### Evidence Corpus (124 Files - Selective Reading)
```
/evidence_dossier/
├── benchmarks/              # 3 verified external cases
├── audit/                   # V1→V2 credibility fixes
├── session-output/          # Evaluation reports
├── PASS1-8 agent deliverables/  # 40 Haiku agent outputs
└── analysis/                # Master analyses
```

### Verified Benchmarks (USE ONLY THESE)
```
/benchmarks/LEROY_MERLIN_2021_VERIFIED.md    # ADEO Group, verified URL
/benchmarks/KINGFISHER_GROUP_NPS_VERIFIED.md # Kingfisher Annual Report
/benchmarks/POINT_P_ALTERNATIVE_VERIFIED.md  # Saint-Gobain Transport Control Tower
```

---

## YOUR REVIEW FRAMEWORK (7 Comprehensive Quality Gates)

### Quality Gate 1: Credibility Audit (IF.TTT Compliance)

**Objective:** Verify ZERO speculative claims about Gedimat operations remain in final dossier.

**Search For (CRITICAL VIOLATIONS):**
1. **Unsourced € amounts about Gedimat:**
   - "Économies 50K€" without source
   - "Baseline affrètement 30K€" without measurement
   - "Investissement 5K€" without vendor quote
   - "CA Gedimat" without confirmation

2. **Unsourced Gedimat operational metrics:**
   - "Taux service 88%" without audit
   - "NPS 35" without survey
   - "Coût logistique 6.5% CA" without calculation

3. **Unsourced ROI projections:**
   - "ROI 10×" without derivation
   - "Payback 5 semaines" without calculation
   - "Économies 15K€/trim" without formula

**What's ACCEPTABLE:**
- "Point P achieved 12% reduction (source: LSA Conso 2023)" ← External case
- "Leroy Merlin reduced costs 11-15% (source: ADEO Report 2023 p.67)" ← Verified URL
- "Gedimat ROI = [Baseline affrètement] × 12% / [Investissement] = À CALCULER" ← Formula with explicit data requirement
- "Baseline Gedimat: À mesurer audit 30 jours (Médiafret invoices)" ← Explicit data collection instruction

**Deliverable 1A: Violations Report**
```markdown
# CREDIBILITY VIOLATIONS FOUND

## Critical (Board-Embarrassing)
- Location: SUPER_DOSSIER_FINAL.md:line___
  Claim: "Économies estimées 50K€ annuels"
  Issue: NO source, NO formula, NO measurement instruction
  Risk Level: CEO WILL be challenged on this number
  Fix: Replace with "Économies = [Baseline affrètement] × 12% (Point P case) = CALCULABLE après mesure baseline"

[Repeat for EACH violation]

## Medium (Needs Clarification)
[Less critical issues]

## Total Violations: ___
IF.TTT Compliance Score: ___/100
Status: ✅ PASS (>95%) | ❌ FAIL (<95%)
```

---

### Quality Gate 2: Benchmark Verification

**Objective:** Verify ALL 3 external case studies have working URLs and data matches claims.

**Test Protocol:**
1. **Leroy Merlin 2021 Case:**
   - Claimed data: 55% e-commerce growth, 11-15% logistics cost reduction, €40M Easylog investment
   - Source: ADEO Overview 2023 + Supply Chain Magazine Oct 2022
   - **YOUR TASK:**
     - Does ADEO Overview 2023 PDF exist at claimed URL?
     - Do pages 60-70 mention these numbers?
     - Is Supply Chain Magazine Oct 2022 article real?
   - **Verdict:** ✅ VERIFIED | ⚠️ PARTIAL | ❌ FAILED

2. **Kingfisher Group NPS:**
   - Claimed data: NPS ~50 (FY2023), target 60 (FY2024), customer satisfaction 82%
   - Source: Kingfisher Annual Report 2023/24
   - **YOUR TASK:**
     - Does Annual Report 2023/24 PDF exist?
     - Does it mention NPS 50 and target 60?
     - Is Castorama mentioned as Kingfisher brand?
   - **Verdict:** ✅ VERIFIED | ⚠️ PARTIAL | ❌ FAILED

3. **Saint-Gobain / Point P:**
   - Claimed data: 13% CO2 reduction, $10M savings, 5-year program
   - Source: Saint-Gobain Integrated Report 2022-2023
   - **YOUR TASK:**
     - Is there a "Transport Control Tower" initiative mentioned?
     - Do numbers match (13%, $10M)?
     - ⚠️ IGNORE any mention of "Point P 12% reduction LSA Conso" - that's FAKE from V1
   - **Verdict:** ✅ VERIFIED | ⚠️ PARTIAL | ❌ FAILED

**Deliverable 2A: Benchmark Verification Report**
```markdown
# BENCHMARK VERIFICATION RESULTS

## Case 1: Leroy Merlin 2021
Status: ✅ VERIFIED
- ADEO Overview 2023: PDF accessible, page 67 confirms metrics
- Supply Chain Magazine: Article found, Oct 2022 issue
- Data Accuracy: 100% match
- URL Status: All working as of 2025-11-17
- Recommendation: USE AS-IS

## Case 2: Kingfisher Group
Status: ⚠️ PARTIALLY VERIFIED
- Annual Report 2023/24: PDF accessible
- NPS data: GROUP level only, no Castorama-specific
- Recommendation: Change claim from "Castorama NPS 47" to "Kingfisher Group NPS 50 (Castorama parent company)"

## Case 3: Saint-Gobain
[Your analysis]

## OVERALL BENCHMARK CREDIBILITY: ✅ PASS | ❌ FAIL
```

---

### Quality Gate 3: Actionability Test (Angélique Execution Simulation)

**Objective:** Verify Gedimat coordinator (Angélique) can execute recommendations WITHOUT external consultants or new systems.

**Role-Play:** You are Angélique. You work at Gedimat coordinating supplier orders. You have:
- Access to: Email, Excel, Médiafret invoices (PDF), order system, Google Maps
- Skills: Intermediate Excel, basic French business software
- Time: 2-4 hours/week for optimization project
- Budget: €0 (no approval for software purchases)

**Test Each "Quick Win" (Section 5):**

**Quick Win 1: Alert System for Supplier Delays**
- **Dossier says:** "Setup Excel + email automation, 4 hours, <€1K"
- **YOUR TEST:**
  - Can Angélique pull "last 30 orders with promised vs actual dates"? (Check: does order system export this?)
  - Can she create Excel alert without VBA programming?
  - Is "email automation" clear enough? (Does it mean manual email or Outlook rule?)
- **Verdict:** ✅ EXECUTABLE | ⚠️ NEEDS CLARIFICATION | ❌ NOT ACTIONABLE

**Quick Win 2: NPS Survey (20 Pilot Clients)**
- **Dossier says:** "Template provided, 2 hours, €0"
- **YOUR TEST:**
  - Is NPS survey template actually included in dossier? (Check Annexe B or Tools section)
  - Are 5 questions clear and French-appropriate?
  - Can Angélique send via email or does it require survey software?
- **Verdict:** [Your analysis]

**Quick Win 3: Depot Scoring Tool**
- **Dossier says:** "Excel macro, training 3 days, validate 50 cases"
- **YOUR TEST:**
  - Is Excel scoring file actually included? (Check Annexe A: Tools)
  - Can Angélique understand scoring formula: `Score = w1×Volume + w2×Distance + w3×Urgence`?
  - Is "validate 50 cases" realistic? (Does she have 50 historical cases accessible?)
- **Verdict:** [Your analysis]

**Deliverable 3A: Actionability Report**
```markdown
# ACTIONABILITY TEST RESULTS

## Quick Win 1: Alert System
Status: ⚠️ NEEDS CLARIFICATION
- Data Access: ✅ Angélique confirms she can pull 30 orders
- Tool Clarity: ❌ "Email automation" too vague
- Fix Required: Add explicit: "Create Outlook rule: IF order late >24h, send email to self + manager"

## Quick Win 2: NPS Survey
[Your analysis]

## Quick Win 3: Depot Scoring
[Your analysis]

## OVERALL ACTIONABILITY: __ / 4 Quick Wins executable as-written
```

---

### Quality Gate 4: Executive Summary Test (15-Minute Board Presentation)

**Objective:** Verify Section 1 (Résumé Exécutif) is STANDALONE, clear, and compelling.

**Test Protocol:**
1. **Read ONLY Section 1 (Résumé Exécutif)**
   - Do NOT read context, methodology, or other sections
   - Simulate: You are a board member, this is your FIRST exposure to the project

2. **Answer These Questions (Without Looking at Other Sections):**
   - What is the PROBLEM? (Should be clear in 3 lines)
   - What is the OPPORTUNITY? (Financial impact, competitive advantage)
   - What are the 3 RECOMMENDATIONS? (Quick win, medium-term, long-term)
   - What is the EXPECTED ROI? (Number or "calculable after X")
   - What DECISION does PDG need from board? (Approval for what?)
   - What is the NEXT STEP? (Timeline, resources)

3. **Check Formatting:**
   - Length: ≤2 pages (A4, 12pt font)
   - Structure: Problem → Opportunity → Recommendations → ROI → Decision → Next Steps
   - Tone: Humble (options presented, not prescribed), data-grounded, action-oriented
   - French Quality: Zero anglicisms ("Quick Win" → "Gain Rapide")

**Deliverable 4A: Executive Readiness Report**
```markdown
# EXECUTIVE SUMMARY EVALUATION

## Clarity Test (Without Reading Other Sections)
Q: What is the problem?
A: [Could you answer from Section 1 alone? YES/NO]

Q: What are the 3 recommendations?
A: [List them - were they clear?]

Q: What is expected ROI?
A: [Was it clear? Realistic? Verifiable?]

## Format Check
- Length: ___ pages (Target: ≤2)
- Standalone: ✅ YES | ❌ Requires reading Section 2-10 to understand
- Tone: ✅ Humble | ❌ Prescriptive/Arrogant
- French: ___ anglicisms found (Target: 0 in Section 1)

## Board-Readiness: ✅ PASS | ❌ FAIL
Reason: [Specific issues if FAIL]
```

---

### Quality Gate 5: French Language Quality (Académie Française Standard)

**Objective:** Zero anglicisms in executive summary, <5 in full dossier (Sections 1-10, annexes exempt).

**Search Protocol:**
Use grep/search to find these anglicisms:
```
dashboard, KPI, ROI, Quick Win, benchmark, feedback, lead time,
checklist, workflow, template, baseline, milestone, stakeholder
```

**For Each Found:**
1. **Context:** What section? Executive summary or annexes?
2. **Severity:**
   - CRITICAL: In Section 1 (Résumé Exécutif)
   - HIGH: In Sections 2-5 (Core content)
   - MEDIUM: In Sections 6-10 (Implementation)
   - LOW: In Annexes (tools/glossary)
3. **French Equivalent:**
   - dashboard → tableau de bord
   - KPI → Indicateurs Clés de Performance (ICP)
   - Quick Win → Gain Rapide / Levier Immédiat
   - benchmark → référence sectorielle / cas de référence
   - ROI → Retour sur Investissement (RSI) [acceptable after first definition]
   - baseline → référence de base / situation initiale
   - template → modèle / gabarit
4. **Fix Required:** YES/NO

**Special Case: Technical Glossary**
- Anglicisms are ACCEPTABLE in "Glossaire & Abréviations" section IF:
  - French equivalent provided: "ROI (angl.): Retour sur Investissement (RSI)"
  - Explained: "Utilisé en finance pour mesurer rentabilité investissement"

**Deliverable 5A: French Language Report**
```markdown
# FRENCH LANGUAGE QUALITY AUDIT

## Anglicisms Found: ___ total

### Critical (Section 1: Résumé Exécutif)
- Line 23: "Quick Win" → Fix: "Gain Rapide"
- Line 45: "dashboard" → Fix: "tableau de bord"
Total in Section 1: ___ (Target: 0)

### High (Sections 2-5)
[List]

### Medium (Sections 6-10)
[List]

### Low (Annexes - Acceptable)
[List]

## Overall French Quality: ✅ PASS (<5 in Sections 1-10) | ❌ FAIL (>5)

## Académie Française Verdict: [Your assessment of overall language quality]
```

---

### Quality Gate 6: Gap Analysis (Missing Critical Elements)

**Objective:** Identify what's MISSING that could cause board to reject or defer decision.

**Check for These Elements:**

#### 6A. Risk Mitigation
- **Question:** What if depot scoring recommends Depot A but urgent client needs Depot B override?
- **Should Exist:** Section on "Decision Overrides & Exception Handling"
- **Location:** [Search dossier - does this exist?]
- **If Missing:** Add to recommendations

#### 6B. Sensitivity Analysis
- **Question:** What if Gedimat achieves 8% reduction (not 12% like Point P)?
- **Should Exist:** Table with Conservative/Base/Optimistic scenarios
- **Location:** [Search for "sensibilité" or "scénario" - does this exist?]
- **If Missing:** Add to Annexe G

#### 6C. Legal Compliance
- **Question:** Does optimization violate France transport regulations or Gedimat franchise contracts?
- **Should Exist:** Section on "Conformité Juridique & Réglementaire"
- **Location:** [Search for "juridique" or "légal" - covered?]
- **If Missing:** Add to Section 8 or Annexe H

#### 6D. Success Metrics (KPIs)
- **Question:** How do we measure if pilot succeeded?
- **Should Exist:** "Pilot Success Criteria" with baseline → target metrics
  - Example: "Service level 88% → 92%, NPS 35 → 48, Cost reduction 0% → 12%"
- **Location:** [Search Section 7: Validation - are KPIs clear?]
- **If Missing:** Add to Section 7

#### 6E. Competitive Risk
- **Question:** If Point P or BigMat see this dossier, can they reverse-engineer Gedimat strategy?
- **Should Exist:** Note on confidentiality, what's proprietary vs public
- **Location:** [Does dossier mention IP protection?]
- **If Missing:** Add disclaimer or sanitize overly-specific data

**Deliverable 6A: Gap Analysis Report**
```markdown
# CRITICAL GAPS IDENTIFIED

## Gap 1: No Sensitivity Analysis
Impact: Board will ask "What if we only achieve 8%?" and PDG has no answer
Severity: HIGH
Recommendation: Add Annexe G with 3 scenarios:
- Conservative: 8% reduction, ROI = [formula]
- Base: 12% reduction (Point P case)
- Optimistic: 15% reduction
Estimated Effort: 2 hours to create table

## Gap 2: [Your analysis]

## Gap 3: [Your analysis]

## OVERALL COMPLETENESS: __ / 5 critical elements present
```

---

### Quality Gate 7: LaTeX Preparation & Visual Polish

**Objective:** Prepare dossier for professional LaTeX typesetting + diagram generation.

#### 7A. Document Structure for LaTeX
Verify dossier has:
1. **Clear Hierarchy:**
   - `# Section 1: Résumé Exécutif` → `\section{}`
   - `## 1.1 Problématique` → `\subsection{}`
   - `### 1.1.1 Contexte` → `\subsubsection{}`
2. **Table of Contents Markers:**
   - Each section starts with ID: `<a name="section-1"></a>`
3. **Cross-References:**
   - "Voir Annexe A" → `\ref{annexe-a}` format
4. **Citations:**
   - "[Source: ADEO 2023 p.67]" → `\cite{adeo2023}` + BibTeX entry

#### 7B. Diagram Specifications (For External Tool)
Identify diagrams needed:
1. **Flux Logistics (Section 3):**
   - Fournisseurs → 3 Depots → Clients
   - Show: <10t (internal driver), >10t (Médiafret), internal shuttle
   - Format: Flowchart, nodes for depots, edges for transport
   - Tool: PlantUML, Mermaid, or TikZ

2. **Decision Tree (Section 5):**
   - IF urgency=high AND volume>10t → Depot closest to supplier
   - IF urgency=low AND volume>15t → Depot with most volume
   - Format: Decision tree, yes/no branches
   - Tool: Graphviz DOT

3. **Gantt Chart (Section 7 or Annexe F):**
   - 90-day quick wins timeline
   - Weeks 1-2: Alerts, Weeks 3-4: NPS survey, Weeks 5-8: Training
   - Format: Gantt chart, bars for tasks
   - Tool: pgfgantt (LaTeX) or external Gantt tool

**Deliverable 7A: LaTeX Preparation Guide**
```markdown
# LATEX TYPESETTING SPECIFICATIONS

## Document Class
\documentclass[12pt,a4paper]{report}
\usepackage[french]{babel}
\usepackage[utf8]{inputenc}
\usepackage{hyperref} % For cross-references

## Section Mapping
- Résumé Exécutif → \chapter{Résumé Exécutif}
- Sections 2-10 → \section{}
- Subsections → \subsection{}

## Diagrams Required (3 Total)
1. **Flux Logistics:**
   - File: flux_gedimat.tex (TikZ)
   - Nodes: Fournisseur, Depot Lieu, Depot Méru, Depot Breuilpont, Client
   - Edges: Chauffeur interne (<10t), Médiafret (>10t), Navette interne
   - Estimated Size: Half page (A4)

2. **Decision Tree:**
   [Your specification]

3. **Gantt Chart:**
   [Your specification]

## Bibliography (BibTeX)
@report{adeo2023,
  title={ADEO Overview 2023},
  author={ADEO Group},
  year={2023},
  url={https://www.adeo.com/wp-content/uploads/2024/05/ADEO_OVERVIEW_EN_2023.pdf}
}

[Add entries for Kingfisher, Saint-Gobain, etc.]

## Page Count Estimate
- Sections 1-10: 48 pages
- Annexes A-F: 102 pages
- Total with LaTeX formatting: ~155 pages
```

---

## FINAL DELIVERABLE STRUCTURE

After completing all 7 Quality Gates, produce:

### Master Report: `GPT5_PRO_OFFLINE_REVIEW_FINAL_REPORT.md`

```markdown
# GPT-5 Pro Offline Review: Gedimat Logistics Dossier
**Date:** 2025-11-17
**Reviewer:** GPT-5 Pro
**Package:** GEDIMAT_GPT5PRO_PACKAGE.zip (23 MB, 278 files)

---

## EXECUTIVE SUMMARY

Overall Assessment: ✅ APPROVED FOR BOARD | ⚠️ APPROVED WITH FIXES | ❌ REJECTED - MAJOR REVISIONS REQUIRED

**Critical Findings:**
- [3-5 bullet points of most important issues]

**Recommendation:**
- [Approve as-is / Fix X issues then approve / Major rework needed]

---

## QUALITY GATE RESULTS

### QG1: Credibility (IF.TTT)
Score: ___/100
Status: ✅ PASS | ❌ FAIL
Violations: ___ critical, ___ medium
[Link to detailed report]

### QG2: Benchmarks
Status: ✅ ALL VERIFIED | ⚠️ PARTIAL | ❌ FAILED
[Link to verification report]

### QG3: Actionability
Executable Quick Wins: __ / 4
Status: ✅ PASS | ❌ FAIL
[Link to execution test]

### QG4: Executive Readiness
Section 1 Quality: ✅ BOARD-READY | ❌ NEEDS REVISION
Length: ___ pages (target ≤2)
[Link to readiness report]

### QG5: French Language
Anglicisms: ___ in Sections 1-10 (target <5)
Status: ✅ PASS | ❌ FAIL
[Link to language audit]

### QG6: Gap Analysis
Critical Gaps: ___ identified
Severity: LOW | MEDIUM | HIGH
[Link to gaps report]

### QG7: LaTeX Readiness
Diagrams Needed: ___
Formatting Issues: ___
Status: ✅ READY | ⚠️ NEEDS PREP
[Link to LaTeX guide]

---

## DETAILED FINDINGS

[Include all 7 Quality Gate detailed reports here]

---

## RECOMMENDED ACTIONS (Priority Order)

### Priority 1 (Must Fix Before Board)
1. [Issue from QG1, QG2, or QG4]
2. [Next critical issue]

### Priority 2 (Should Fix)
3. [Important but not board-blocking]

### Priority 3 (Nice to Have)
4. [Improvements for completeness]

---

## LATEX PACKAGE (If Approved)

[Include complete LaTeX specifications, BibTeX, diagram specs]

---

## APPENDICES

A. Full Credibility Violations List
B. Benchmark Verification Details
C. Actionability Test Transcripts
D. French Language Corrections (Line-by-Line)
E. Gap Analysis Deep Dive
F. LaTeX Source Files

---

**Sign-Off:**
Reviewed by: GPT-5 Pro
Date: 2025-11-17
Status: [APPROVED / CONDITIONAL / REJECTED]
Next Step: [Hand to LaTeX typesetter / Return to authors for fixes / Major rework]
```

---

## SPECIAL INSTRUCTIONS FOR GPT-5 PRO

### How to Approach This Review

1. **Read Strategically (Don't Read Everything):**
   - Start with: SUPER_DOSSIER_EXECUTIVE_SUMMARY.md (overview)
   - Then: PROMPT_V2_FACTUAL_GROUNDED.md (baseline)
   - Then: 3 verified benchmark files (benchmarks/ directory)
   - ONLY read other files when validating specific claims

2. **Be Skeptical (You're the Last Line of Defense):**
   - Assume EVERY number is wrong until proven otherwise
   - Test EVERY URL (don't trust "URL: [To be provided]")
   - Challenge EVERY "industry average" without source

3. **Think Like the Board:**
   - If PDG presents "12% cost reduction possible" and board member asks "How do you know?", is the answer in the dossier?
   - If PDG says "We'll measure baseline then calculate ROI", does the dossier explain HOW to measure baseline?

4. **Preserve Quality, Not Quantity:**
   - It's better to have 40 SOLID pages than 50 pages with 10 pages of speculation
   - Recommend CUTTING weak sections rather than defending them

5. **Provide Actionable Fixes:**
   - DON'T say: "Section 5 needs improvement"
   - DO say: "Section 5 line 234: Replace 'Économies 50K€' with 'Économies = [Baseline] × 12% (Point P) = CALCULABLE après mesure baseline'"

6. **Generate LaTeX-Ready Output:**
   - If dossier passes all gates, prepare complete LaTeX package
   - Include: Document structure, BibTeX, diagram specs, formatting guide
   - Goal: Hand package to LaTeX typesetter who can produce PDF in <2 hours

---

## YOUR SUCCESS CRITERIA

This review is SUCCESSFUL if:
1. ✅ You identify ALL credibility risks (zero unsourced Gedimat claims slip through)
2. ✅ You verify ALL 3 benchmarks (working URLs, data matches)
3. ✅ You confirm Angélique can execute ≥3 of 4 Quick Wins
4. ✅ You validate Section 1 is board-ready (≤2 pages, standalone, compelling)
5. ✅ You find <5 anglicisms in Sections 1-10
6. ✅ You identify critical gaps (sensitivity analysis, risk mitigation, KPIs)
7. ✅ You provide LaTeX-ready package OR clear fix list for authors

**Final Question for Yourself:**
"Would I stake MY professional reputation on PDG presenting this dossier to the board?"

If YES → ✅ APPROVED
If "Maybe with small fixes" → ⚠️ CONDITIONAL
If NO → ❌ REJECTED

---

## BEGIN YOUR REVIEW NOW

Start with:
1. Read SUPER_DOSSIER_EXECUTIVE_SUMMARY.md
2. Read Section 1 (Résumé Exécutif) from main dossier
3. Ask yourself: "Is this board-ready?"
4. Then proceed through Quality Gates 1-7 systematically

Good luck. The fate of Angélique's 36 hours of work rests on your thoroughness.

---

**END OF GPT-5 PRO OFFLINE REVIEW PROMPT**
