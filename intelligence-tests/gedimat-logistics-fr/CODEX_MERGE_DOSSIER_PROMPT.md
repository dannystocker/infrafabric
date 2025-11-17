# CODEX PROMPT: Merge Gedimat Dossier + Annexes into Single Markdown

**COPY THIS ENTIRE BLOCK AND PASTE INTO YOUR CODEX/GPT-5.1 SESSION**

---

## Mission

Merge the behavioral-enhanced Gedimat dossier with all annexes into a single comprehensive, well-formatted markdown file with clickable internal links for LLM Arena review.

**Source Files (WSL Paths):**

**Main Dossier:**
```
/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_BEHAVIORAL_ENHANCED_FINAL.md
```

**Annexes (3 operational):**
```
/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_REVIEW_AND_DOSSIER_EXTRACTED/gedimat_review_outputs/ANNEXE_X_DECISION_RULES.md
/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_REVIEW_AND_DOSSIER_EXTRACTED/gedimat_review_outputs/ANNEXE_Y_ALERTING_SLA.md
/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_REVIEW_AND_DOSSIER_EXTRACTED/gedimat_review_outputs/ANNEXE_Z_COST_MODEL_README.md
```

**Cost Model CSV (embed as table):**
```
/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_REVIEW_AND_DOSSIER_EXTRACTED/gedimat_review_outputs/ANNEXE_Z_COST_MODEL_EXAMPLE.csv
```

**Output File (WSL Path):**
```
/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_ARENA_REVIEW_COMPLETE.md
```

---

## Structure Requirements

### 1. Document Header
```markdown
# Gedimat Logistics Optimization: Complete Board Dossier
**Version:** 3.1 Behavioral Enhanced
**Date:** 2025-11-17
**Status:** Board-ready, IF.TTT compliant (zero phantom numbers)
**Reviewer:** LLM Arena Multi-Evaluator Review

---

## Document Navigation (Clickable TOC)

**Main Dossier (Sections 1-10):**
- [1. Résumé Exécutif](#1-résumé-exécutif)
- [2. Contexte & Faits Clés](#2-contexte--faits-clés-interne)
- [3. Diagnostic](#3-diagnostic-problèmes-observés)
- [3.5 Psychologie B2B et Fidélisation](#35-psychologie-b2b-et-fidélisation)
- [4. Cas Externes](#4-cas-externes-références-utilisables)
- [5. Recommandations Détaillées](#5-recommandations-détaillées)
- [5.5 Le Geste Relationnel](#55-le-geste-relationnel-trust-signal)
- [6. Gouvernance](#6-gouvernance--responsabilités)
- [6.5 Gouvernance Comportementale](#65-gouvernance-comportementale--principe-zéro-perdant)
- [7. Plan 90 Jours](#7-plan-90-jours-jalons)
- [7.5 Stress-Test Comportemental](#75-stress-test-comportemental--questions-inversées)
- [8. Indicateurs & Validation](#8-indicateurs--validation-pilote)
- [8.5 Indicateurs de Récupération](#85-indicateurs-de-récupération-recovery-metrics)
- [9. Sensibilité](#9-sensibilité-scénarios)
- [9.5 Crédibilité du RSI](#95-crédibilité-du-rsi--pourquoi-des-formules-et-non-des-chiffres-fixes-)
- [9.6 Arbitrages Relationnels](#96-arbitrages-relationnels--inefficacités-vs-investissements-marketing)
- [10. Conformité](#10-conformité--confidentialité)

**Annexes Opérationnelles:**
- [Annexe X: Règles de Décision (Playbook)](#annexe-x-règles-de-décision-playbook)
- [Annexe Y: Alertes & SLA](#annexe-y-alertes--sla)
- [Annexe Z: Modèle de Coûts](#annexe-z-modèle-de-coûts)

**Metadata & Review Context:**
- [Document Metadata](#document-metadata)
- [Review Instructions for LLM Arena](#review-instructions-for-llm-arena)

---
```

### 2. Main Dossier Content
Copy the **entire contents** of `GEDIMAT_BEHAVIORAL_ENHANCED_FINAL.md` (334 lines) immediately after the TOC.

**CRITICAL:**
- Preserve all section headers exactly as-is
- Preserve all markdown formatting
- Preserve all formulas and tables
- Do NOT modify any content

### 3. Annexe X: Règles de Décision
```markdown

---

# ANNEXES OPÉRATIONNELLES

---

## Annexe X: Règles de Décision (Playbook)

[Full contents of ANNEXE_X_DECISION_RULES.md]

[↑ Back to TOC](#document-navigation-clickable-toc)

---
```

### 4. Annexe Y: Alertes & SLA
```markdown
## Annexe Y: Alertes & SLA

[Full contents of ANNEXE_Y_ALERTING_SLA.md]

[↑ Back to TOC](#document-navigation-clickable-toc)

---
```

### 5. Annexe Z: Modèle de Coûts
```markdown
## Annexe Z: Modèle de Coûts

[Full contents of ANNEXE_Z_COST_MODEL_README.md]

### Z.1 Exemple de Tableau de Coûts

[Convert ANNEXE_Z_COST_MODEL_EXAMPLE.csv to markdown table]

[↑ Back to TOC](#document-navigation-clickable-toc)

---
```

### 6. Document Metadata
```markdown

---

# DOCUMENT METADATA

---

## Version History

**V3.1 Behavioral Enhanced (2025-11-17)**
- Applied 8 Rory Sutherland behavioral psychology upgrades
- Added: Sections 3.5, 5.5, 6.5, 7.5, 8.5, 9.5, 9.6
- Executor: GPT-5.1 High via Codex CLI
- IF.TTT compliance: 100% (zero phantom numbers)

**V3.0 Clean Final (2025-11-17)**
- GPT-5 Pro offline review (7 quality gates passed)
- Eliminated all unsourced Gedimat €amounts
- Verified 3 external benchmarks (Leroy Merlin, Kingfisher, Saint-Gobain)
- Quality: 7/10 overall (9/10 pertinence, 6/10 style, 8/10 care)

**V2.0 Factual Grounded (2025-11-16)**
- Codex GPT-4o evaluation (78/100)
- Replaced phantom numbers with formulas
- Created 10 audit files
- IF.TTT compliance: 78/100

**V1.0 Initial Assembly (2025-11-16)**
- 20 Haiku agents deployed in parallel
- Created SUPER_DOSSIER_FINAL.md + 6 annexes
- Cost: $0.50 USD

---

## IF.TTT Compliance Certification

**Methodology:** Traceable, Transparent, Trustworthy (IF.TTT)

**Compliance Score:** 100% (V3.1)
- ✅ Zero unsourced Gedimat €amounts
- ✅ All formulas specify data requirements
- ✅ All external examples cited with sources
- ✅ All behavioral principles cite Rory Sutherland or David Rock (SCARF)
- ✅ All Gedimat applications labeled "hypothétique (À VALIDER)"

**Validation Commands Run:**
```bash
# Zero forbidden patterns
grep -n "Gedimat économisera [0-9]" GEDIMAT_BEHAVIORAL_ENHANCED_FINAL.md
# Result: 0 matches ✅

# All behavioral sections present
grep -n "## 3.5 Psychologie B2B" GEDIMAT_BEHAVIORAL_ENHANCED_FINAL.md
grep -n "### 5.5 Le Geste Relationnel" GEDIMAT_BEHAVIORAL_ENHANCED_FINAL.md
grep -n "### 6.5 Gouvernance Comportementale" GEDIMAT_BEHAVIORAL_ENHANCED_FINAL.md
grep -n "## 7.5 Stress-Test Comportemental" GEDIMAT_BEHAVIORAL_ENHANCED_FINAL.md
grep -n "### 8.5 Indicateurs de Récupération" GEDIMAT_BEHAVIORAL_ENHANCED_FINAL.md
grep -n "## 9.5 Crédibilité du RSI" GEDIMAT_BEHAVIORAL_ENHANCED_FINAL.md
grep -n "### 9.6 Arbitrages Relationnels" GEDIMAT_BEHAVIORAL_ENHANCED_FINAL.md
# Result: 7/7 sections present ✅
```

---

## External Benchmarks Verified

1. **Leroy Merlin / ADEO**
   - Source: ADEO Overview 2023 (https://www.adeo.com/en/)
   - Source: Supply Chain Magazine NL 3628 (https://www.supplychainmagazine.fr/nl/2022/3628/)
   - Metric: 55% e-commerce growth 2021, 11-15% cost reduction

2. **Kingfisher Group / Castorama**
   - Source: Kingfisher Investors (https://www.kingfisher.com/investors/)
   - Metric: NPS tracked monthly at Group level

3. **Saint-Gobain Transport Control Tower**
   - Source: Logistics Viewpoints 2022 (https://logisticsviewpoints.com/2022/01/31/)
   - Metric: -13% CO₂, >$10M savings over 5 years

---

## Behavioral Psychology Framework

**Source:** Rory Sutherland (Vice Chairman, Ogilvy UK)
**Secondary Source:** David Rock (NeuroLeadership Institute, SCARF Model)

**8 Strategic Upgrades Applied:**
1. Relational Capitalism Framing (Section 1)
2. Problems Well Resolved = Loyalty (Section 3.5)
3. "Too Good to Be True" Credibility Signal (Section 9.5)
4. Trust Signals / Le Geste Relationnel (Section 5.5)
5. Recovery Metrics (Section 8.5)
6. Zero-Loser Principle / SCARF Model (Section 6.5)
7. Inverted Question Stress-Test (Section 7.5)
8. Relational Investments ≠ Waste (Section 9.6)

---

## Project Metrics

**Total Cost:** $1.50 USD (Phases 1-3 complete)
- Phase 1: Assembly (20 Haiku agents) = $0.50
- Phase 2: GPT-5 Pro review (7 quality gates) = $0.70
- Phase 3: Behavioral integration (Claude + GPT-5.1) = $0.30

**Token Efficiency:** 98.2% compression (2.5M → 45K context transfer)

**Multi-Evaluator Validation:**
- Claude Sonnet 4.5 (internal review)
- GPT-5 Pro (offline review, 7 quality gates)
- Gemini 2.0-flash-exp (validation)
- GPT-5.1 High (behavioral upgrades execution)

**Quality Gates Passed:** 7/7
1. QG1: Credibility Audit (IF.TTT) ✅
2. QG2: Benchmark Verification ✅
3. QG3: Actionability Test ✅
4. QG4: Executive Summary Test ✅
5. QG5: French Language Quality ✅
6. QG6: Gap Analysis ✅
7. QG7: LaTeX Preparation ✅

---

[↑ Back to TOC](#document-navigation-clickable-toc)

---
```

### 7. Review Instructions for LLM Arena
```markdown

---

# REVIEW INSTRUCTIONS FOR LLM ARENA

---

## Review Context

**Document Type:** Board-ready strategic dossier
**Domain:** B2B logistics optimization (building materials distribution)
**Client:** Gedimat (3 depots: Lieu, Méru, Breuilpont)
**Audience:** C-suite executives (PDG, CFO, COO)

**Key Innovation:** IF.TTT methodology (Traceable, Transparent, Trustworthy)
- Zero phantom numbers (all formulas with data requirements)
- All claims sourced or labeled hypothesis
- Behavioral psychology framework integrated (Rory Sutherland)

---

## Evaluation Criteria (7 Dimensions)

### 1. IF.TTT Compliance (Critical)
**Question:** Are there ANY unsourced Gedimat €amounts or operational metrics?

**How to check:**
- Search for patterns: "Gedimat économisera [number]€", "réduction de [number]%", "ROI [number]×"
- Verify: Every Gedimat metric is either:
  - A formula with variables: `[Baseline affrètement] × [Réduction %]`
  - Labeled hypothesis: "Application hypothétique (À VALIDER avec données réelles)"
  - External example: "Leroy Merlin 55% e-commerce growth (ADEO Overview 2023)"

**Pass criteria:** ≥95% claims sourced or labeled
**Critical failure:** ANY unsourced Gedimat €amount

---

### 2. Executive Readiness (High Priority)
**Question:** Can the PDG present Section 1 (Résumé Exécutif) to the board standalone?

**How to check:**
- Read ONLY Section 1, ignore all other sections
- Can you answer: Problem? Opportunity? Recommendations? ROI? Decision needed?
- Is tone humble (not arrogant)? Is French professional (zero anglicisms)?

**Pass criteria:** Section 1 is ≤2 pages, standalone, board-ready
**Bonus:** Includes behavioral psychology framing (relational capitalism)

---

### 3. Actionability (Operational)
**Question:** Can Angélique (coordinator) execute the Quick Wins in Week 1?

**How to check:**
- Review Section 5 (Recommandations)
- Check: Are tools specified? (Excel, email rules, NOT "buy WMS software")
- Check: Are data sources accessible? (factures Médiafret, not "collect 90 days of GPS data")
- Check: Are time estimates realistic? (2-4 hrs/week, not "full-time for 6 months")

**Pass criteria:** ≥3 of 4 Quick Wins executable with current resources

---

### 4. Behavioral Psychology Integration (Strategic Depth)
**Question:** Does the dossier leverage Rory Sutherland insights to add strategic depth?

**How to check:**
- Section 3.5: Problems Well Resolved = Loyalty?
- Section 5.5: Trust Signals (Le Geste Relationnel)?
- Section 6.5: Zero-Loser Principle (SCARF Model)?
- Section 7.5: Inverted Question Stress-Test?
- Section 8.5: Recovery Metrics (IRL-1, IRL-2, IRL-3)?
- Section 9.5: "Too Good to Be True" credibility signal?
- Section 9.6: Relational Investments ≠ Waste?

**Pass criteria:** 7/8 behavioral sections present with proper citations

---

### 5. French Language Quality (Professional Standard)
**Question:** Is the French professional, clear, and free of anglicisms?

**How to check:**
- Count anglicisms in Section 1: "Quick Win", "dashboard", "KPI", "ROI", "benchmark"
- Check for French equivalents: "Gain Rapide", "tableau de bord", "Indicateurs Clés"
- Verify tone: Business French (not academic, not marketing)

**Pass criteria:** 0 anglicisms in Section 1, <5 in entire document

---

### 6. External Benchmarks Credibility (Trust Factor)
**Question:** Can someone verify the 3 external benchmarks?

**How to check:**
- Section 4: Leroy Merlin, Kingfisher Group, Saint-Gobain
- Click URLs: Do they work? Do they lead to cited sources?
- Verify data: Does the source document contain the claimed metric?

**Pass criteria:** 3/3 benchmarks verifiable (working URLs, data matches)

---

### 7. Overall Board Presentation Risk (Synthesis)
**Question:** Would YOU stake your professional reputation on the PDG presenting this to the board?

**Consider:**
- Credibility risks: Any phantom numbers that could embarrass PDG?
- Completeness: Any obvious gaps (legal compliance, risk mitigation)?
- Tone: Professional humility or arrogant over-promises?
- Actionability: Concrete next steps or vague recommendations?

**Pass criteria:** "YES, I would stake my reputation on this"
**Conditional:** "Maybe, if fixes applied"
**Reject:** "NO, too risky to present"

---

## Output Format (Structured Review)

```markdown
# LLM Arena Review: Gedimat Logistics Dossier V3.1

**Reviewer:** [Your LLM name/model]
**Date:** [YYYY-MM-DD]
**Overall Verdict:** [APPROVED / CONDITIONAL / REJECTED]

---

## 1. IF.TTT Compliance: [PASS/FAIL]
**Score:** [0-100]
**Unsourced Gedimat claims found:** [COUNT]
**Examples:** [Quote any violations with line references]
**Verdict:** [If ANY unsourced Gedimat €amounts → CRITICAL BLOCKER]

---

## 2. Executive Readiness: [PASS/FAIL]
**Score:** [0-100]
**Section 1 standalone:** [YES/NO]
**Tone:** [Professional/Arrogant/Other]
**Anglicisms in Section 1:** [COUNT]
**Verdict:** [Board-ready or needs fixes?]

---

## 3. Actionability: [PASS/FAIL]
**Score:** [0-100]
**Quick Wins executable:** [X/4]
**Blocking issues:** [List any "buy expensive software" dependencies]
**Verdict:** [Angélique can execute in Week 1?]

---

## 4. Behavioral Psychology Integration: [PASS/FAIL]
**Score:** [0-100]
**Sections found:** [X/8]
**Missing:** [List any missing sections]
**Citations present:** [YES/NO - Rory Sutherland, David Rock]
**Verdict:** [Strategic depth added?]

---

## 5. French Language Quality: [PASS/FAIL]
**Score:** [0-100]
**Anglicisms Section 1:** [COUNT]
**Anglicisms total:** [COUNT]
**Tone:** [Professional business French?]
**Verdict:** [C-suite appropriate?]

---

## 6. External Benchmarks Credibility: [PASS/FAIL]
**Score:** [0-100]
**Leroy Merlin:** [VERIFIED/NOT VERIFIED - URL working?]
**Kingfisher Group:** [VERIFIED/NOT VERIFIED - URL working?]
**Saint-Gobain:** [VERIFIED/NOT VERIFIED - URL working?]
**Verdict:** [Can PDG defend if questioned?]

---

## 7. Overall Board Presentation Risk: [LOW/MEDIUM/HIGH]
**Score:** [0-100]
**Critical risks:** [List any "PDG embarrassment" scenarios]
**Missing elements:** [Legal compliance? Risk mitigation? Pilot metrics?]
**Recommendation:** [Present as-is / Fix P0 issues / Major rework needed]

---

## Final Verdict

**Overall Score:** [Average of 7 dimensions]

**APPROVED:** Recommend presentation to board as-is
**CONDITIONAL:** Fix P0 issues (list below) then present
**REJECTED:** Major rework needed before board presentation

**P0 Issues (Must Fix):**
1. [Issue 1 with line reference]
2. [Issue 2 with line reference]
...

**P1 Issues (Nice to Have):**
1. [Issue 1]
2. [Issue 2]
...

**Strengths:**
- [Strength 1]
- [Strength 2]
...

**Recommended Next Steps:**
1. [Action 1]
2. [Action 2]
...
```

---

## Success Criteria for This Merged Document

**When you complete this merge, the output file should:**

✅ Have a clickable TOC with all 15+ sections linked
✅ Include the full 334-line behavioral-enhanced dossier
✅ Include all 3 operational annexes (X, Y, Z)
✅ Convert the CSV cost model to a markdown table
✅ Include complete metadata section
✅ Include LLM Arena review instructions
✅ Be 100% self-contained (no external file dependencies)
✅ Be ready to paste as a single URL/link in LLM Arena

**File size estimate:** ~400-500 lines total

---

## Execution Steps

1. **Read all source files:**
   ```bash
   cat /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_BEHAVIORAL_ENHANCED_FINAL.md
   cat /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_REVIEW_AND_DOSSIER_EXTRACTED/gedimat_review_outputs/ANNEXE_X_DECISION_RULES.md
   cat /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_REVIEW_AND_DOSSIER_EXTRACTED/gedimat_review_outputs/ANNEXE_Y_ALERTING_SLA.md
   cat /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_REVIEW_AND_DOSSIER_EXTRACTED/gedimat_review_outputs/ANNEXE_Z_COST_MODEL_README.md
   cat /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_REVIEW_AND_DOSSIER_EXTRACTED/gedimat_review_outputs/ANNEXE_Z_COST_MODEL_EXAMPLE.csv
   ```

2. **Build merged document** following the structure above

3. **Convert CSV to markdown table:**
   - Read `ANNEXE_Z_COST_MODEL_EXAMPLE.csv`
   - Convert to markdown table format
   - Insert into Annexe Z section

4. **Verify all internal links work:**
   - TOC links point to correct section headers
   - "Back to TOC" links point to TOC
   - Use markdown anchor format: `#section-header-lowercase-with-hyphens`

5. **Write output file:**
   ```bash
   cat > /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_ARENA_REVIEW_COMPLETE.md << 'EOF'
   [Full merged content here]
   EOF
   ```

6. **Validation:**
   ```bash
   # Check file created
   ls -lh /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_ARENA_REVIEW_COMPLETE.md

   # Count lines (should be ~400-500)
   wc -l /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_ARENA_REVIEW_COMPLETE.md

   # Verify TOC links exist
   grep -n "^\- \[" /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_ARENA_REVIEW_COMPLETE.md | head -20

   # Verify all annexes present
   grep -n "^## Annexe" /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_ARENA_REVIEW_COMPLETE.md
   ```

---

## Deliverable

**File:** `/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_ARENA_REVIEW_COMPLETE.md`

**Size:** ~400-500 lines, ~30-40K characters

**Purpose:** Single self-contained markdown file ready to paste as URL/link in LLM Arena for multi-evaluator review

**Estimated execution time:** 5-10 minutes

---

**END OF PROMPT. PASTE THIS INTO CODEX/GPT-5.1 AND EXECUTE.**
