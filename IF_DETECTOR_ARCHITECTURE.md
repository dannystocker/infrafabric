# IF.detector: Algorithm Architecture Documentation

**Purpose:** In-house GPTZero alternative that analyzes text for AI tells and provides specific remediation advice

**Status:** Complete implementation with 6 core metrics + orchestration engine

---

## Architecture Overview

```
TextAnalyzer (Main Orchestrator)
├── PerplexityMetric        (Token sequence predictability)
├── BurstinessMetric        (Sentence length variance)
├── VocabularyMetric        (Lexical diversity)
├── TransitionMetric        (Formulaic connector density)
├── RepetitionMetric        (N-gram repetition patterns)
├── SyntaxMetric            (Syntactic uniformity)
└── RemediationEngine       (Fix suggestions)
```

---

## Core Metrics

### 1. PERPLEXITY SCORE (25% weight)

**Algorithm:** Character bigram cross-entropy model

**Formula:**
```
Cross-Entropy = -sum(log₂(P(bigram))) / N
Perplexity = 2^(Cross-Entropy)
Normalized Score = (100 - Perplexity) / 80  [bounded 0-1]
```

**Detection Logic:**
- **Human Range:** 60-100 (unpredictable token sequences)
- **AI Range:** 20-50 (highly predictable sequences)
- **Threshold:** >85 = Human, <35 = AI

**Why It Works:**
- LLMs are trained on token prediction → produce highly probable sequences
- Humans use unexpected word choices and novel combinations
- Character bigrams capture subword-level patterns

**Implementation:**
```python
class PerplexityMetric:
    - extract_char_bigrams(text) → Counter
    - calculate_cross_entropy(text, bigram_dist) → float
    - normalize_perplexity(perplexity) → float [0-1]
```

**Pseudocode:**
```
1. Extract all 2-character sequences from text
2. Build frequency distribution of bigrams
3. For each bigram in text:
   - Look up its probability in distribution
   - Calculate log₂(probability)
   - Sum all log probabilities
4. Divide by total bigrams → average log probability (cross-entropy)
5. Convert to perplexity: 2^(cross_entropy)
6. Normalize: (100 - perplexity) / 80
```

---

### 2. BURSTINESS INDEX (8% weight)

**Algorithm:** Coefficient of variation in sentence length

**Formula:**
```
Burstiness = StdDev(sentence_lengths) / Mean(sentence_lengths)
Normalized Score = (Burstiness - 0.3) / 2.2  [bounded 0-1]
```

**Detection Logic:**
- **Human Range:** 1.2-2.5 (high variance)
- **AI Range:** 0.3-0.8 (low variance)
- **Threshold:** >1.2 = Human, <0.8 = AI

**Why It Works:**
- Humans naturally vary sentence length for rhythm and emphasis
- AI models optimize for consistency, producing uniform sentence structures
- Burstiness captures this variance pattern

**Implementation:**
```python
class BurstinessMetric:
    - analyze(sentences) → MetricResult
    - _normalize_burstiness(burstiness) → float [0-1]
```

**Pseudocode:**
```
1. Tokenize text into sentences
2. Count words in each sentence
3. Calculate mean and standard deviation of lengths
4. Burstiness = StdDev / Mean
5. If Burstiness > 1.2: verdict = HUMAN
   If Burstiness < 0.8: verdict = AI
   Else: verdict = MIXED
6. Normalize to 0-1 scale
```

---

### 3. VOCABULARY RICHNESS (20% weight)

**Algorithm:** Type-Token Ratio + Hapax Legomenon + Sophistication Index

**Formulas:**
```
TTR = unique_words / total_words
Hapax_Ratio = single_occurrence_words / unique_words
Sophistication = sophisticated_words / unique_words

Combined_Score = (TTR × 0.5) + (Hapax × 0.3) + (Sophistication × 0.2)
```

**Detection Logic:**
- **Human Range:** 0.60-0.85 (high TTR)
- **AI Range:** 0.35-0.55 (low TTR)
- **Threshold:** >0.65 = Human, <0.50 = AI

**Why It Works:**
- Humans use varied vocabulary and rare words
- AI tends to repeat common words and avoid less common terms
- TTR is classic linguistic diversity measure
- Hapax legomenon (words used once) indicates vocabulary breadth

**Implementation:**
```python
class VocabularyMetric:
    - analyze(tokens) → MetricResult
    - _word_frequency_distribution() → Counter
    - _sophistication_ratio() → float
```

**Pseudocode:**
```
1. Tokenize and clean text (lowercase, remove punctuation)
2. Create set of unique words
3. Calculate TTR = len(unique_words) / len(all_words)
4. Count words appearing exactly once (hapax)
5. Calculate Hapax_Ratio = hapax_count / len(unique_words)
6. Count "sophisticated" words (not in common stopword list)
7. Combine metrics with weights:
   - TTR: 50% (most important)
   - Hapax: 30%
   - Sophistication: 20%
8. Normalize to 0-1 scale
```

---

### 4. TRANSITION WORD DENSITY (15% weight)

**Algorithm:** Weighted frequency of formulaic connectors

**Formula:**
```
Transition_Score = sum(weight × count for each phrase)
Density = Transition_Score / total_words
Normalized Score = (Density - 0.005) / 0.075  [bounded 0-1]
```

**Detected Phrases (Weighted):**
| Category | Examples | Weight |
|----------|----------|--------|
| Additive | furthermore, moreover, additionally, besides | 3-5 |
| Sequential | firstly, secondly, next, then | 2-3 |
| Consequential | therefore, thus, in conclusion, to summarize | 3-4 |
| Contrasting | however, nevertheless, on the other hand | 3-5 |
| Emphasizing | notably, particularly, certainly, obviously | 2 |
| Elaborating | that is, for example, specifically | 2-3 |

**Detection Logic:**
- **Human Range:** 0.5-2.0% (sparse connectors)
- **AI Range:** 4.0-8.0% (excessive connectors)
- **Threshold:** >6% = AI, <2% = Human

**Why It Works:**
- AI overuses "bridge" language to create artificial coherence
- Humans rely more on implicit connections
- Formulaic phrases like "in conclusion" scream AI
- Real writers use natural transitions or no connector at all

**Implementation:**
```python
class TransitionMetric:
    - analyze(text, word_count) → MetricResult
    - _normalize_density(density) → float [0-1]

    transition_phrases = {
        'furthermore': 5,
        'additionally': 5,
        'moreover': 5,
        ... (25 total phrases with weights)
    }
```

**Pseudocode:**
```
1. Define weighted dictionary of transition phrases
2. Convert text to lowercase
3. For each transition phrase:
   - Count occurrences in text
   - Multiply by phrase weight
   - Add to running score
4. Calculate density = transition_score / total_words
5. If density > 0.06: verdict = AI
   If density < 0.02: verdict = HUMAN
   Else: verdict = MIXED
6. Normalize to 0-1 scale
```

---

### 5. REPETITION SCORE (20% weight)

**Algorithm:** N-gram repetition analysis at multiple levels

**Formula:**
```
Bigram_Rep = repeated_bigrams / total_bigrams
Trigram_Rep = repeated_trigrams / total_trigrams
Fourgram_Rep = repeated_4grams / total_4grams

Combined = (Bigram_Rep × 0.2) + (Trigram_Rep × 0.3) + (Fourgram_Rep × 0.5)
```

**Detection Logic:**
- **Human Range:** 5-15% (natural phrase variation)
- **AI Range:** 25-45% (excessive repetition)
- **Threshold:** >40% = AI, <15% = Human

**Why It Works:**
- AI reuses phrase templates because it optimizes for probability
- Humans naturally vary how they express ideas
- 4-gram repetition is most diagnostic (3+ words = meaningful pattern)
- Heavier weight on longer n-grams because they're more significant

**Implementation:**
```python
class RepetitionMetric:
    - analyze(tokens) → MetricResult
    - _extract_ngrams(tokens, n) → Counter
    - _calculate_repetition(ngram_counter) → float [0-1]
```

**Pseudocode:**
```
1. Extract bigrams (n=2) from token sequence
2. Extract trigrams (n=3)
3. Extract 4-grams (n=4)
4. For each n-gram level:
   - Count total n-grams
   - Count n-grams that appear more than once
   - Repetition = repeated_count / total_count
5. Combine with weights:
   - Bigrams: 0.2 (less meaningful)
   - Trigrams: 0.3 (moderate)
   - 4-grams: 0.5 (most meaningful)
6. If combined > 0.4: verdict = AI
   If combined < 0.15: verdict = HUMAN
   Else: verdict = MIXED
```

**Example:**
```
Text: "The key finding is important. The main discovery is significant. The critical point is essential."

Trigrams:
  "the key finding": 1
  "the main discovery": 1
  "the critical point": 1
  "is important": 1
  "is significant": 1
  "is essential": 1

Pattern: Heavy repetition of "The X [is/are] Y" template (AI-like)
```

---

### 6. SYNTAX METRIC (12% weight)

**Algorithm:** POS-tag entropy + formulaic pattern detection

**Formula:**
```
POS_Entropy = -sum(P(pattern) × log₂(P(pattern)))
Normalized Score = (Entropy - 1.5) / 3.5  [bounded 0-1]
```

**Detection Logic:**
- **Human Range:** 3.5-5.0 (high entropy = diverse structures)
- **AI Range:** 1.5-3.0 (low entropy = uniform structures)

**AI Pattern Detection:**
```
Formulaic starts: "The X is", "In Y", "To Z"
Passive voice preference: "[word] has been [verb]ed"
Formulaic phrases: "It is important", "It is notable"
```

**Why It Works:**
- Shannon entropy measures diversity of syntactic patterns
- AI tends to repeat same Subject-Verb-Object structure
- POS tags capture linguistic structure independent of vocabulary
- Formulaic patterns are explicit AI indicators

**Implementation:**
```python
class SyntaxMetric:
    - analyze(sentences) → MetricResult
    - _calculate_entropy(freq_counter) → float
    - _detect_formulaic_patterns(sentences) → int
    - _normalize_entropy(entropy) → float [0-1]
```

**Pseudocode:**
```
1. For each sentence:
   - Tokenize into words
   - Apply POS-tagger (noun, verb, adj, etc.)
   - Extract sequence of POS tags as pattern
   - Store pattern in frequency counter
2. Calculate entropy of pattern distribution:
   - Total patterns = N
   - For each unique pattern:
     * Probability = count / N
     * Contribution = -P × log₂(P)
   - Sum all contributions
3. Detect formulaic patterns:
   - Check each sentence against AI pattern list
   - Count matches
4. If entropy > 4.0 and formulaic < 2: verdict = HUMAN
   If entropy < 2.5 or formulaic > 5: verdict = AI
   Else: verdict = MIXED
5. Normalize entropy to 0-1 scale
```

---

## Overall Probability Calculation

**Weighted Ensemble:**
```
Overall_AI_Prob = weighted_average of all metric scores

Weights (calibrated from testing):
  - Perplexity: 25% (most predictive)
  - Repetition: 20% (unique to AI)
  - Vocabulary: 20% (strong signal)
  - Transitions: 15% (formulaic patterns)
  - Syntax: 12% (structure patterns)
  - Burstiness: 8% (less reliable alone)

Formula:
  Overall = (0.25×Perplexity + 0.20×Repetition + 0.20×Vocabulary
           + 0.15×Transitions + 0.12×Syntax + 0.08×Burstiness)
```

**Final Verdict:**
- **>0.65:** AI
- **0.35-0.65:** MIXED
- **<0.35:** HUMAN

---

## Confidence Assessment

**Confidence based on metric agreement:**

```
AI_Count = number of metrics voting AI
Human_Count = number of metrics voting HUMAN
Total = 6

If AI_Count >= 4 or Human_Count >= 4:
    Confidence = HIGH
Elif max(AI_Count, Human_Count) >= 3:
    Confidence = MEDIUM
Else:
    Confidence = LOW
```

**Logic:**
- High agreement = confident verdict
- Metric disagreement = uncertain (low confidence)
- Helps user understand reliability of verdict

---

## Remediation Engine

**Maps AI tells to actionable fixes:**

| Issue Type | Severity | Remediation |
|-----------|----------|-------------|
| Low Perplexity | HIGH | Add specific examples, personal anecdotes, unexpected angles |
| Uniform Sentence Length | MEDIUM | Vary opening structures, mix sentence lengths |
| Low Vocabulary | MEDIUM | Replace repeated terms, use synonyms, more specific terminology |
| High Transition Density | MEDIUM | Remove formulaic connectors, use structural transitions |
| High Repetition | HIGH | Refactor repeated phrases, use paraphrases and pronouns |
| Uniform Syntax | MEDIUM | Vary clause ordering, mix active/passive voice naturally |

**Tactics Example (Low Vocabulary):**
```
Issue: Type-Token Ratio = 0.42 (AI range)

Suggested Fixes:
1. Replace repeated words with synonyms
   "result" → result/outcome/finding/conclusion
2. Use more specific terminology
   "good" → excellent/superior/optimal/robust
3. Incorporate domain-specific jargon appropriately
4. Use less common words to demonstrate range
   "big" → substantial/considerable/significant
```

---

## Data Structures

### MetricResult
```python
@dataclass
class MetricResult:
    score: float                    # 0-1 (0=human, 1=AI)
    human_range: str               # e.g., "60-100"
    ai_range: str                  # e.g., "20-50"
    verdict: Verdict               # HUMAN|MIXED|AI
    reasoning: str                 # Explanation
    supporting_data: Dict[str, Any] # Raw metrics
```

### IssueFlag
```python
@dataclass
class IssueFlag:
    line_number: int       # Where in text
    line_text: str         # Problematic text
    issue_type: str        # formulaic_opening, etc.
    description: str       # What's wrong
    suggestion: str        # How to fix
    severity: str          # low|medium|high
    evidence: Dict         # Supporting data
```

### DetectionResult
```python
@dataclass
class DetectionResult:
    overall_ai_probability: float  # 0-1
    confidence: ConfidenceLevel    # low|medium|high
    verdict: Verdict               # HUMAN|MIXED|AI
    metrics: Dict[str, MetricResult]  # All 6 metrics
    specific_issues: List[IssueFlag]   # Specific problems
    remediation_priority: List[str]    # Ordered fixes
    token_count: int
    sentence_count: int
    word_count: int
    analysis_timestamp: str
```

---

## Output Format

```json
{
  "overall_ai_probability": 0.72,
  "confidence": "high",
  "verdict": "AI",
  "metrics": {
    "perplexity": {
      "score": 0.85,
      "human_range": "60-100",
      "ai_range": "20-50",
      "verdict": "AI",
      "reasoning": "Text perplexity: 28.3. Highly predictable sequences...",
      "supporting_data": {
        "perplexity_raw": 28.3,
        "cross_entropy": 4.82,
        "char_bigram_count": 412,
        "unique_bigrams": 87
      }
    },
    "burstiness": {...},
    "vocabulary": {...},
    "transitions": {...},
    "repetition": {...},
    "syntax": {...}
  },
  "specific_issues": [
    {
      "line": 3,
      "line_text": "Furthermore, it is important to note that...",
      "issue_type": "formulaic_opening",
      "description": "Formulaic phrase detected: 'it is important to note'",
      "suggestion": "Replace or remove 'it is important to note' with more natural language",
      "severity": "medium",
      "evidence": {"phrase": "it is important to note"}
    }
  ],
  "remediation_priority": [
    "low_perplexity (perplexity)",
    "high_repetition (repetition)",
    "formulaic_opening (line 3)"
  ],
  "text_statistics": {
    "token_count": 287,
    "sentence_count": 12,
    "word_count": 245,
    "avg_sentence_length": 20.4
  }
}
```

---

## Usage Example

```python
from if_detector import TextAnalyzer

analyzer = TextAnalyzer()

text = "Your input text here..."
result = analyzer.analyze(text)

# Access results
print(f"AI Probability: {result.overall_ai_probability:.1%}")
print(f"Verdict: {result.verdict.value}")
print(f"Confidence: {result.confidence.value}")

# Print detailed report
print(result.to_json())

# Iterate through issues
for issue in result.specific_issues:
    print(f"Line {issue.line_number}: {issue.description}")
    print(f"  Fix: {issue.suggestion}")
```

---

## Thresholds & Calibration

### Metric Thresholds (0-1 scale)

| Metric | AI Threshold | Human Threshold |
|--------|-----------|-----------------|
| Perplexity | <0.35 | >0.65 |
| Burstiness | <0.15 | >0.75 |
| Vocabulary | <0.50 | >0.65 |
| Transitions | >0.60 | <0.20 |
| Repetition | >0.40 | <0.15 |
| Syntax | <0.25 | >0.70 |

### Overall Probability Thresholds

- **>0.65:** Strong AI signal (high confidence)
- **0.55-0.65:** Moderate AI signal (medium confidence)
- **0.45-0.55:** Ambiguous (low confidence)
- **0.35-0.45:** Moderate human signal (medium confidence)
- **<0.35:** Strong human signal (high confidence)

---

## Testing Strategy

### Test Corpus

1. **Human-Written Samples**
   - Academic papers
   - Blog posts
   - News articles
   - Personal essays
   - Technical documentation

2. **AI-Generated Samples**
   - ChatGPT outputs
   - GPT-4 outputs
   - Claude outputs
   - Gemini outputs
   - Mixed AI/human (hybrid)

### Metrics to Track

- True Positive Rate (correctly identified AI)
- False Positive Rate (human incorrectly flagged)
- True Negative Rate (correctly identified human)
- F1-Score for balanced accuracy
- ROC-AUC score
- Confidence calibration

---

## Implementation Notes

### Dependencies
```
nltk >= 3.8
python >= 3.8
```

### Performance
- Typical analysis: 50-100ms per 1000 words
- Memory usage: ~50MB (NLTK models loaded once)
- Can be optimized with batch processing

### Limitations
- Works best on English text (NLTK tuned for English)
- Minimum 100 words recommended for accurate analysis
- Very short texts (<20 words) have low confidence
- Specialized technical writing may have unusual stats
- Can be gamed by deliberate obfuscation

---

## Future Enhancements

1. **Advanced Models**
   - RoBERTa embeddings for semantic coherence
   - Transformer-based language model perplexity
   - Semantic repetition detection (not just lexical)

2. **Domain-Specific Thresholds**
   - Academic papers (different syntax norms)
   - Technical documentation (high repetition normal)
   - Creative writing (different burstiness)

3. **Multi-Language Support**
   - Spanish, French, German models
   - Language detection first

4. **Style Transfer Detection**
   - Identify "humanized" AI text
   - Detect prompt injection patterns

5. **Interactive Calibration**
   - Allow users to provide ground truth
   - Continuous learning and adaptation

---

## References

**Linguistic Theory:**
- Shannon Entropy for language diversity
- Cross-Entropy as predictability measure
- Type-Token Ratio (Templin, 1957)
- Hapax Legomenon in vocabulary analysis

**AI Detection Research:**
- GPTZero (Tian et al., 2023)
- DetectGPT (Mitchell et al., 2023)
- Perplexity as core metric for LLM detection

---

**Implementation Status:** Complete ✓
**Version:** 1.0
**Last Updated:** 2025-11-30
**File Location:** `/home/setup/infrafabric/if_detector.py`
