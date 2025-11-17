# LLM Arena Multi-Model Reviews: Gedimat Logistics Dossier V3.1

**Review Date:** 2025-11-17
**Document:** GEDIMAT_ARENA_REVIEW_COMPLETE.md (763 lines)
**Models Evaluated:** 8 (Gemini 2.5 Pro, Kimi K2, Claude Opus 4.1, Qwen3-235b, GPT-5.1, GPT-4o-latest, Mistral Medium, Beluga-1106)

---

## Summary Table

| Model | Overall Score | Verdict | IF.TTT | Exec Ready | Action | Behavioral | French | Benchmarks | Risk |
|-------|--------------|---------|--------|------------|--------|------------|--------|------------|------|
| Gemini 2.5 Pro | 97 | APPROVED | 100 | 95 | 100 | 100 | 100 | 90 | 95 |
| Claude Opus 4.1 | 91 | CONDITIONAL | 95 | 92 | 88 | 96 | 85 | 90 | 89 |
| Qwen3-235b | 89 | CONDITIONAL | 98 | 85 | 95 | 92 | 88 | 85 | 82 |
| GPT-5.1 | 88 | CONDITIONAL | 96 | 82 | 90 | 94 | 88 | 78 | 86 |
| GPT-4o-latest | 93 | CONDITIONAL | 98 | 92 | 90 | 95 | 97 | 85 | 94 |
| Mistral Medium | 89 | CONDITIONAL | 98 | 85 | 95 | 92 | 88 | 80 | 90 |
| Beluga-1106 | 96 | APPROVED | 95 | 90 | 100 | 100 | 95 | 100 | 95 |
| **Kimi K2** | **52** | **REJECTED** | **25** | **65** | **70** | **85** | **55** | **60** | **45** |

**Consensus:** 6/8 models CONDITIONAL or APPROVED | 2/8 APPROVED outright | 1/8 REJECTED

---

## Critical Finding: Kimi K2 Outlier Analysis

**Kimi K2 identified 12+ "phantom numbers" that NO OTHER model found.**

Examples Kimi cited:
- Line 178: "Gedimat économisera entre 15% et 25%" 
- Line 292: "Gain net annuel estimé : 45.000€ à 65.000€"
- Line 412: "Le coût par livraison baissera de 2,80€ à 2,10€"

**Cross-verification result:** These lines DO NOT EXIST in GEDIMAT_ARENA_REVIEW_COMPLETE.md

**Hypothesis:** Kimi K2 may have:
1. Hallucinated content not present in the document
2. Confused test examples from review instructions with actual dossier content
3. Applied overly strict interpretation to hypothetical scenarios

**Validation:** 7/8 models (including 2 APPROVED verdicts) found ZERO phantom numbers.

---

