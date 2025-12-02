# IF.detector Quick Reference Guide

## 60-Second Overview

**IF.detector** is a 6-metric ensemble that detects AI-written text and provides remediation advice.

```
Input Text → TextAnalyzer → DetectionResult {
  overall_ai_probability: 0-1
  confidence: low|medium|high
  verdict: HUMAN|MIXED|AI
  metrics: {...}  # 6 detailed metrics
  specific_issues: [...]  # Line-by-line problems
  remediation_priority: [...]  # Ordered fixes
}
```

---

## The 6 Metrics at a Glance

| Metric | Measures | AI Signal | Human Signal | Weight |
|--------|----------|-----------|--------------|--------|
| **Perplexity** | Token predictability | Low (20-50) | High (60-100) | 25% |
| **Burstiness** | Sentence length variance | Low (0.3-0.8) | High (1.2-2.5) | 8% |
| **Vocabulary** | Lexical diversity (TTR) | Low (0.35-0.55) | High (0.60-0.85) | 20% |
| **Transitions** | Connector word density | High (4-8%) | Low (0.5-2%) | 15% |
| **Repetition** | N-gram reuse | High (25-45%) | Low (5-15%) | 20% |
| **Syntax** | Structure uniformity (entropy) | Low (1.5-3.0) | High (3.5-5.0) | 12% |

---

## Quick Interpretation Guide

### Overall AI Probability Thresholds

```
0.0 ────────── 0.35 ────────── 0.65 ────────── 1.0
  HUMAN              MIXED              AI

<0.35:   Strong human signal (confidence: HIGH/MEDIUM)
0.35-0.65: Ambiguous (confidence: LOW)
>0.65:   Strong AI signal (confidence: HIGH/MEDIUM)
```

### Confidence Levels

**HIGH:** 4+ metrics agree (consensus)
**MEDIUM:** 3 metrics agree (majority)
**LOW:** Metrics scattered (disagreement)

---

## Reading the Metrics Output

### Example: Perplexity = 0.78 (HIGH score = AI)

```json
{
  "perplexity": {
    "score": 0.78,           # High = AI signal
    "human_range": "60-100", # Typical human perplexity
    "ai_range": "20-50",     # Typical AI perplexity
    "verdict": "AI",
    "reasoning": "Text perplexity: 31.2. Highly predictable sequences...",
    "supporting_data": {
      "perplexity_raw": 31.2,  # Actual value (low = predictable = AI)
      "cross_entropy": 4.95
    }
  }
}
```

**Interpretation:**
- Perplexity of 31.2 falls in AI range (20-50)
- Characters are highly predictable (low surprise)
- Strong AI signal from this metric

---

### Example: Vocabulary = 0.35 (LOW score = AI)

```json
{
  "vocabulary": {
    "score": 0.35,           # Low = AI signal
    "human_range": "0.60-0.85",
    "ai_range": "0.35-0.55",
    "verdict": "AI",
    "supporting_data": {
      "type_token_ratio": 0.42,       # Low = repetition
      "hapax_legomenon": 0.08,        # Low = few unique words
      "sophistication_ratio": 0.15,   # Low = basic vocabulary
      "unique_words": 87,
      "total_words": 206
    }
  }
}
```

**Interpretation:**
- TTR of 0.42 is low (AI typically 0.35-0.55)
- Only 8% of words appear once (human average ~20-30%)
- Limited vocabulary with heavy repetition = AI-like
- Strong AI signal from this metric

---

## Common Patterns

### Pure AI Text
```
Metrics all vote AI:
- Perplexity: 0.85 (highly predictable)
- Transitions: 0.75 (excessive connectors)
- Repetition: 0.60 (heavy n-gram reuse)
- Vocabulary: 0.30 (limited diversity)
- Syntax: 0.15 (uniform structure)
- Burstiness: 0.20 (uniform sentences)

Overall: 0.78 (HIGH confidence = STRONG AI SIGNAL)
```

### Pure Human Text
```
Metrics all vote human:
- Perplexity: 0.15 (unpredictable)
- Transitions: 0.05 (sparse connectors)
- Repetition: 0.08 (natural variation)
- Vocabulary: 0.75 (diverse vocabulary)
- Syntax: 0.85 (varied structures)
- Burstiness: 0.80 (sentence variation)

Overall: 0.22 (HIGH confidence = STRONG HUMAN SIGNAL)
```

### Hybrid/Mixed Text
```
Some metrics AI, some human:
- Perplexity: 0.60 (borderline)
- Transitions: 0.45 (moderate)
- Repetition: 0.25 (slight AI tendency)
- Vocabulary: 0.50 (borderline)
- Syntax: 0.55 (borderline)
- Burstiness: 0.45 (moderate)

Overall: 0.50 (LOW confidence = AMBIGUOUS)
Possible explanation: Human-edited AI, or AI trained on diverse data
```

---

## Remediation Priority Ordering

Fixes are prioritized by:

1. **Severity (PRIMARY)**
   - HIGH: Blocks detection improvement
   - MEDIUM: Contributes to AI signal
   - LOW: Minor polish

2. **Metric Agreement (SECONDARY)**
   - Multiple metrics flagging same issue = higher priority
   - Isolated issue = lower priority

3. **Impact (TERTIARY)**
   - Issues affecting >10% of text = higher priority
   - Single-instance issues = lower priority

### Example Priority List

```
[
  "low_perplexity (perplexity)",        # Weight 25%, severity HIGH
  "high_repetition (repetition)",       # Weight 20%, severity HIGH
  "low_vocabulary (vocabulary)",        # Weight 20%, severity MEDIUM
  "high_transitions (transitions)",     # Weight 15%, severity MEDIUM
  "uniform_syntax (syntax)"             # Weight 12%, severity MEDIUM
]
```

**Action Order:**
1. **First:** Fix low perplexity (add specific examples, unexpected insights)
2. **Second:** Fix high repetition (refactor repeated phrases)
3. **Third:** Expand vocabulary (replace repeated words with synonyms)
4. **Fourth:** Remove transition words (delete "Furthermore", etc.)
5. **Fifth:** Vary sentence structure (reorder clauses, mix active/passive)

---

## Specific Issues Detection

### Detected Issue Types

```
formulaic_opening:
  Pattern: "it is important to note", "In this paper"
  Severity: MEDIUM
  Fix: Remove or replace with direct statement

formulaic_closing:
  Pattern: "In conclusion", "To summarize"
  Severity: MEDIUM
  Fix: Use structural signal (new section) instead

backref:
  Pattern: "As mentioned above", "As noted earlier"
  Severity: LOW
  Fix: Refer to section number instead

passive_voice_clustering:
  Pattern: 3+ consecutive passive sentences
  Severity: MEDIUM
  Fix: Rewrite some in active voice

verbosity:
  Pattern: "in order to", "due to the fact that"
  Severity: LOW
  Fix: Use direct phrasing ("to", "because")
```

### Line-by-Line Reporting

```json
"specific_issues": [
  {
    "line": 3,
    "line_text": "Furthermore, it is important to note that the data...",
    "issue_type": "formulaic_opening",
    "description": "Formulaic phrase detected: 'it is important to note'",
    "suggestion": "Replace or remove with more natural language",
    "severity": "medium"
  },
  {
    "line": 8,
    "line_text": "The research was conducted by the team over a six-month period.",
    "issue_type": "passive_voice_clustering",
    "description": "Multiple consecutive sentences in passive voice",
    "suggestion": "Rewrite in active voice for clarity",
    "severity": "medium"
  }
]
```

---

## Usage Patterns

### Pattern 1: Quick Check
```python
analyzer = TextAnalyzer()
result = analyzer.analyze(text)

if result.overall_ai_probability > 0.65:
    print(f"ALERT: {result.confidence.value} confidence this is AI-generated")
else:
    print("Text appears human-written")
```

### Pattern 2: Detailed Audit
```python
result = analyzer.analyze(text)

print(f"Overall: {result.overall_ai_probability:.0%} AI probability")
print(f"Confidence: {result.confidence.value}")

for metric_name, metric in result.metrics.items():
    if metric.verdict == Verdict.AI:
        print(f"\n⚠️  {metric_name.upper()}: {metric.reasoning}")
        print(f"   Fix: {get_remediation_advice(metric_name)}")

print("\nLine-by-line issues:")
for issue in result.specific_issues:
    print(f"  Line {issue.line_number}: {issue.issue_type}")
    print(f"    {issue.suggestion}")
```

### Pattern 3: Batch Analysis
```python
analyzer = TextAnalyzer()
results = []

for text in document_list:
    result = analyzer.analyze(text)
    results.append({
        'text_id': get_id(text),
        'ai_probability': result.overall_ai_probability,
        'issues_count': len(result.specific_issues)
    })

# Report on texts over threshold
high_risk = [r for r in results if r['ai_probability'] > 0.65]
print(f"Found {len(high_risk)} potentially AI-generated documents")
```

---

## Calibration Notes

### These metrics perform well on:
- ✓ News articles and blog posts
- ✓ Academic abstracts and papers
- ✓ Business communications
- ✓ Marketing copy
- ✓ General creative writing

### These metrics have limitations on:
- ✗ Very short texts (<100 words) - use LOW confidence
- ✗ Technical documentation - high repetition is normal
- ✗ Legal writing - formulaic but human
- ✗ Poetry/experimental text - unusual statistics
- ✗ Non-English text - NLTK optimized for English
- ✗ Deliberately obfuscated AI text - can be evaded

---

## Decision Tree

```
Text Analysis ─────┐
                   │
           overall_ai_prob?
         /         |         \
      <0.35      0.35-0.65    >0.65
      /             |           \
   HUMAN          MIXED           AI
    │               │             │
    │               │             │
Do all        Check metric    Check metric
metrics       agreement       agreement
agree?        ├─ 4+: MEDIUM   ├─ 4+: HIGH
│             │    CONFIDENCE │    CONFIDENCE
├─ YES: HIGH  └─ 3: LOW       └─ 3: LOW
│   CONF         CONFIDENCE      CONFIDENCE
└─ NO: LOW
    CONF     ────────────────────────────────
              Use confidence level to decide:
              HIGH: Take action
              MEDIUM: Manual review recommended
              LOW: Insufficient signal, review manually
```

---

## Performance Expectations

### Accuracy (on test corpus)
- Pure AI text: ~92% detection (HIGH confidence)
- Pure human text: ~88% detection (HIGH confidence)
- Mixed text: ~76% detection (MEDIUM confidence)
- Overall F1-Score: 0.85

### Speed
- 1000 words: ~80ms
- 10,000 words: ~1.2s
- 100,000 words: ~15s

### False Positive Rate
- Human text flagged as AI: ~8% overall
- Technical/specialized writing: ~15%
- Poetry/experimental: ~20%

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Confidence always LOW | Metrics disagree | Text is genuinely mixed; use overall_prob as tiebreaker |
| Human text flagged as AI | Specialized domain | Check if technical/legal/formal - adjust thresholds |
| AI text not detected | Sophisticated AI | Model may have been trained to avoid patterns; manual review |
| Specific issues underdetected | Short text | Accuracy drops <200 words; need larger samples |
| NLTK errors on startup | Missing data | Automatically downloads punkt/stopwords/tagger |

---

## Integration Checklist

- [ ] Import TextAnalyzer
- [ ] Initialize analyzer (one-time, loads NLTK models)
- [ ] Call analyze(text) with input
- [ ] Check overall_ai_probability
- [ ] If >0.65, examine specific_issues
- [ ] Use remediation_priority for fixes
- [ ] Optionally iterate: fix → reanalyze → compare

---

**For detailed algorithm explanation, see:** `IF_DETECTOR_ARCHITECTURE.md`
**For implementation code, see:** `if_detector.py`
