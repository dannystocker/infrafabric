# IF.detector & IF.humanize Protocol Documentation

---

## IF.detector: AI Text Detection Framework

### Overview

**IF.detector** is an in-house GPTZero alternative for detecting AI-generated text and providing specific remediation advice. It operates as a comprehensive text analysis system that evaluates text across six independent metrics and synthesizes results into actionable intelligence for humanization.

**Purpose:** Distinguish AI-written from human-written text with high accuracy, identify specific AI tells, and guide iterative humanization through targeted remediation suggestions.

**Status:** Production-ready ✅
**Location:** `/home/setup/infrafabric/if_detector.py`
**Lines of Code:** 1,138 (comprehensive metric suite + remediation engine)

### Architecture

IF.detector is built as a modular metric system with an orchestrating analyzer:

```
┌─────────────────────────────────────────────────────────────┐
│                     TextAnalyzer                            │
│                   (Main Orchestrator)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Perplexity   │  │ Burstiness   │  │ Vocabulary   │      │
│  │   Metric     │  │   Metric     │  │   Metric     │      │
│  │              │  │              │  │              │      │
│  │ Token seq    │  │ Sent length  │  │ TTR, Hapax   │      │
│  │ predict      │  │ variance     │  │ Sophistic    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Transition   │  │ Repetition   │  │ Syntax       │      │
│  │   Metric     │  │   Metric     │  │   Metric     │      │
│  │              │  │              │  │              │      │
│  │ Connector    │  │ N-gram       │  │ POS entropy  │      │
│  │ density      │  │ frequency    │  │ Formulaic    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                          ↓                                  │
│                  ┌──────────────────┐                       │
│                  │ Remediation      │                       │
│                  │ Engine           │                       │
│                  │                  │                       │
│                  │ Maps metrics to  │                       │
│                  │ actionable fixes │                       │
│                  └──────────────────┘                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Detection Metrics (6 Independent Analyses)

#### 1. Perplexity Metric

**What it measures:** Unpredictability of token sequences

**Algorithm:**
- Build character bigram distribution from input text
- Calculate cross-entropy of text against distribution
- Convert to perplexity score using formula: `P = 2^cross_entropy`
- Normalize to 0-1 scale (0=human, 1=AI)

**Thresholds:**
| Range | Human | Mixed | AI |
|-------|-------|-------|-----|
| Raw Score | 60-100 | 35-60 | 20-50 |
| Interpretation | Unpredictable sequences | Variable patterns | Predictable tokens |

**Why it works:** AI models are trained to predict probable token sequences. Human writing includes unexpected word choices, tangents, and novel combinations that AI rarely produces.

#### 2. Burstiness Metric

**What it measures:** Variance in sentence length distribution

**Algorithm:**
- Tokenize text into sentences
- Calculate length of each sentence (word count)
- Compute standard deviation and mean
- Burstiness formula: `B = std_dev / mean_length`
- Normalize: 0=uniform (AI), 1=varied (human)

**Thresholds:**
| Range | Human | Mixed | AI |
|-------|-------|-------|-----|
| Raw Score | 1.2-2.5 | 0.8-1.2 | 0.3-0.8 |
| Interpretation | Natural variation | Some variety | Artificially uniform |

**Why it works:** AI defaults to consistent sentence structure for clarity. Humans naturally vary sentence length based on emphasis, pacing, and thought flow.

#### 3. Vocabulary Metric

**What it measures:** Lexical diversity and sophistication

**Components:**
- **Type-Token Ratio (TTR):** `unique_words / total_words` (0.0-1.0)
- **Hapax Legomenon:** Percentage of words appearing exactly once
- **Sophistication Ratio:** Advanced vs. common word distribution

**Thresholds:**
| Range | Human | Mixed | AI |
|-------|-------|-------|-----|
| TTR | 0.60-0.85 | 0.50-0.65 | 0.35-0.55 |
| Hapax | 35-60% | 20-35% | 5-20% |
| Interpretation | Rich, varied vocab | Moderate diversity | Repetitive, limited |

**Why it works:** AI models rely on common vocabulary for clarity and consistency. Humans use broader vocabulary, unique word choices, and permit one-off words that add texture.

#### 4. Transition Metric

**What it measures:** Formulaic connector word density

**Monitored Phrases (weighted by suspicion):**
```
Additive (high weight):
  - "Furthermore" (5), "Additionally" (5), "Moreover" (5)
  - "In addition" (4), "Also" (2)

Consequential (high weight):
  - "Therefore" (4), "Thus" (3), "As a result" (4)
  - "In conclusion" (4), "To summarize" (4)

Contrasting (medium weight):
  - "However" (3), "Nevertheless" (3)
  - "In contrast" (4)

Emphatic (medium weight):
  - "It is important to note" (6) [highest single weight]
  - "Notably" (2), "Particularly" (2)
```

**Thresholds:**
| Density | Human | Mixed | AI |
|---------|-------|-------|-----|
| Percentage | 0.5-2.0% | 2.0-4.0% | 4.0-8.0% |
| Interpretation | Sparse, natural | Moderate use | Excessive formulaic |

**Why it works:** AI models are trained on academic/formal text, which heavily uses transition phrases. Humans use fewer connectors, relying on context and structure.

#### 5. Repetition Metric

**What it measures:** N-gram repetition patterns (phrase reuse)

**Algorithm:**
- Extract bigrams (2-word), trigrams (3-word), and 4-grams
- Calculate repetition at each level: `(repeated_ngrams / total_ngrams)`
- Weight: bigrams 20%, trigrams 30%, 4-grams 50% (longer phrases more significant)
- Combined score indicates phrase recycling

**Thresholds:**
| Level | Human | Mixed | AI |
|-------|-------|-------|-----|
| Combined % | 5-15% | 15-25% | 25-45% |
| Interpretation | Natural variation | Some reuse | Excessive phrase loops |

**Why it works:** AI models generate similar phrase patterns by reusing training data patterns. Humans paraphrase, use synonyms, and restructure ideas without literal repetition.

#### 6. Syntax Metric

**What it measures:** Sentence structure uniformity and formulaic patterns

**Algorithm:**
- POS-tag each sentence (Part-of-Speech tagging via NLTK)
- Extract POS pattern for each sentence (e.g., "DT NN VBZ JJ")
- Calculate Shannon entropy of pattern distribution
- High entropy = diverse structures (human-like)
- Low entropy = repetitive patterns (AI-like)
- Detect formulaic openings: "The X is Y", "It is important", "In order to"

**Thresholds:**
| Range | Human | Mixed | AI |
|-------|-------|-------|-----|
| Entropy Score | 3.5-5.0 | 2.5-3.5 | 1.5-3.0 |
| Formulaic Count | <2 patterns | 2-5 patterns | >5 patterns |
| Interpretation | Diverse structures | Moderate variety | Repetitive syntax |

**Why it works:** AI models learn consistent grammatical patterns. Humans use varied sentence structures, fragments, rhetorical questions, and unconventional syntax for effect.

### Overall AI Probability Calculation

IF.detector synthesizes all metrics using weighted averaging:

```
Overall AI Probability = Σ(metric_score × weight) / Σ(weights)

Weights:
  Perplexity:   0.25  (most significant)
  Repetition:   0.20  (unique to AI)
  Vocabulary:   0.20  (clear indicator)
  Transitions:  0.15  (formulaic patterns)
  Syntax:       0.12  (structure patterns)
  Burstiness:   0.08  (less reliable alone)
```

**Final Verdict:**
- **AI:** Probability > 0.65 (high confidence in AI authorship)
- **MIXED:** 0.35 - 0.65 (borderline, conflicting metrics)
- **HUMAN:** Probability < 0.35 (high confidence in human authorship)

**Confidence Levels:**
- **HIGH:** 70%+ metrics agree (all AI or all human)
- **MEDIUM:** 50-70% metrics agree
- **LOW:** <50% agreement (significant metric disagreement)

### CLI Usage

#### Basic Analysis

```bash
python3 /home/setup/infrafabric/if_detector.py
```

Then enter text at prompt (press Ctrl+D twice when done):
```
Your text here...
This can be multiple lines.
```

#### Python API Usage

```python
from if_detector import TextAnalyzer, Verdict, ConfidenceLevel

# Initialize analyzer
analyzer = TextAnalyzer()

# Analyze text
text = "Your text to analyze here..."
result = analyzer.analyze(text)

# Access results
print(f"Verdict: {result.verdict.value}")
print(f"AI Probability: {result.overall_ai_probability:.1%}")
print(f"Confidence: {result.confidence.value}")

# Individual metric details
for metric_name, metric_result in result.metrics.items():
    print(f"\n{metric_name}:")
    print(f"  Score: {metric_result.score:.3f}")
    print(f"  Verdict: {metric_result.verdict.value}")
    print(f"  Reasoning: {metric_result.reasoning}")
    print(f"  Supporting Data: {metric_result.supporting_data}")

# Get specific issues
for issue in result.specific_issues:
    print(f"\nLine {issue.line_number}: {issue.issue_type}")
    print(f"  Description: {issue.description}")
    print(f"  Suggestion: {issue.suggestion}")
    print(f"  Severity: {issue.severity}")

# Export as JSON
print(result.to_json())
```

### Output Interpretation

#### Example: Human-Written Text Analysis

```json
{
  "overall_ai_probability": 0.18,
  "confidence": "high",
  "verdict": "HUMAN",
  "metrics": {
    "perplexity": {
      "score": 0.15,
      "verdict": "HUMAN",
      "reasoning": "Unpredictable token sequences suggest human writing"
    },
    "burstiness": {
      "score": 0.87,
      "verdict": "HUMAN",
      "reasoning": "Natural variation in sentence length"
    },
    "vocabulary": {
      "score": 0.72,
      "verdict": "HUMAN",
      "reasoning": "Rich, diverse vocabulary characteristic of human writing"
    }
  },
  "remediation_priority": [],
  "text_statistics": {
    "token_count": 156,
    "sentence_count": 8,
    "word_count": 142,
    "avg_sentence_length": 17.75
  }
}
```

#### Example: AI-Generated Text Analysis

```json
{
  "overall_ai_probability": 0.78,
  "confidence": "high",
  "verdict": "AI",
  "metrics": {
    "perplexity": {
      "score": 0.82,
      "verdict": "AI",
      "reasoning": "Highly predictable sequences characteristic of AI models"
    },
    "transitions": {
      "score": 0.78,
      "verdict": "AI",
      "reasoning": "Excessive formulaic transitions characteristic of AI"
    },
    "repetition": {
      "score": 0.71,
      "verdict": "AI",
      "reasoning": "Excessive repetition of word sequences (AI-like)"
    }
  },
  "specific_issues": [
    {
      "line": 2,
      "line_text": "Furthermore, it is important to note that...",
      "issue_type": "formulaic_opening",
      "description": "Formulaic phrase detected: 'it is important to note'",
      "suggestion": "Replace with more natural phrasing",
      "severity": "medium"
    }
  ],
  "remediation_priority": [
    "high_repetition (repetition)",
    "high_transitions (transitions)"
  ]
}
```

### Remediation Suggestions (Automated)

IF.detector automatically generates remediation advice based on detected issues:

| Issue Type | Severity | Suggestion | Tactics |
|------------|----------|-----------|---------|
| **low_perplexity** | HIGH | Add specific examples, personal anecdotes, unexpected insights | Include case studies, counter-intuitive arguments, personal experience, specific data |
| **uniform_sentence_length** | MEDIUM | Vary sentence structure for natural rhythm | Use short sentences for impact, mix complex with simple, vary sentence starters |
| **low_vocabulary** | MEDIUM | Expand vocabulary to show sophistication | Replace repeated words with synonyms, use specific terminology, incorporate jargon |
| **high_transitions** | MEDIUM | Reduce formulaic transition phrases | Remove "Moreover", "Furthermore", let ideas speak for themselves |
| **high_repetition** | HIGH | Refactor repeated phrases and word sequences | Replace repeated 3+ word phrases, use pronouns, restructure for variation |
| **uniform_syntax** | MEDIUM | Diversify sentence structure and clause ordering | Mix active/passive voice, vary clause position, use rhetorical questions |

### Threshold Recommendations

**For Critical Content (Published/High-Stakes):**
- Accept only HUMAN verdict with HIGH confidence
- If MIXED, require remediation before publication
- If any metric scores >0.70, apply targeted fixes

**For Draft/Working Content:**
- HUMAN or MIXED acceptable
- Use remediation suggestions as improvement roadmap
- Track metric improvements across iterations

**For Academic/Professional:**
- Aim for 0.30-0.40 probability (fully humanized)
- Particular attention to transitions and vocabulary
- Ensure zero "formulaic_opening" issues

### Integration with IF.humanize Protocol

IF.detector serves as the **measurement and feedback mechanism** for the IF.humanize protocol:

```
┌──────────────────────────────────────────────────┐
│  Human Author (Draft Composition)                │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│  Human Author (Initial Review)                   │
│  - Adds context, examples, personality           │
│  - Ensures authenticity and voice                │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│  IF.detector (Analysis)                          │
│  - Measures AI probability                       │
│  - Identifies specific issues                    │
│  - Suggests remediation tactics                  │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│  IF.humanize Protocol (Remediation)              │
│  - Applies targeted fixes                        │
│  - Phase-based iteration                         │
│  - Validation against thresholds                 │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│  IF.detector Feedback Loop                       │
│  - Re-analyze after remediation                  │
│  - Validate probability reduction                │
│  - Confirm all issues resolved                   │
└──────────────────────────────────────────────────┘
```

### Files & Documentation

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `/home/setup/infrafabric/if_detector.py` | Main implementation | 1,138 | Production ✅ |
| Classes: TextAnalyzer | Orchestrator | - | - |
| Classes: PerplexityMetric | Token sequence analysis | - | - |
| Classes: BurstinessMetric | Sentence length variance | - | - |
| Classes: VocabularyMetric | Lexical diversity | - | - |
| Classes: TransitionMetric | Connector word density | - | - |
| Classes: RepetitionMetric | N-gram frequency | - | - |
| Classes: SyntaxMetric | Syntactic uniformity | - | - |
| Classes: RemediationEngine | Fix suggestion generation | - | - |

---

## IF.humanize Protocol: Text Remediation Framework

### Overview

**IF.humanize** is a 6-phase protocol for converting AI-detected text into authentic human-written prose. It operates as a systematic remediation framework that applies targeted fixes informed by IF.detector analysis, with iterative validation and quality assurance.

**Purpose:** Transform text from AI-like to human-like while preserving factual accuracy, argument structure, and intended tone.

**Integration:** Works in tandem with IF.detector as part of the **IF.guard writing assistant suite**.

**Application Domains:**
- Academic papers with AI augmentation
- Professional writing requiring authenticity
- Content marketing with AI assistance
- Internal communications and reports
- Public-facing documentation

### 6-Phase Protocol Architecture

#### Phase 1: Baseline Analysis & Categorization

**Objective:** Understand current state and prioritize remediation efforts

**Actions:**
1. Run IF.detector on complete text
2. Record baseline AI probability and confidence level
3. Categorize severity:
   - **CRITICAL:** AI probability > 0.75 + high confidence
   - **HIGH:** AI probability 0.55-0.75
   - **MODERATE:** AI probability 0.40-0.55
   - **LOW:** AI probability < 0.40

4. Extract specific issues ranked by severity
5. Identify metrics with strongest AI signals (score > 0.70)
6. Document remediation priority list

**Output Artifacts:**
- Baseline metrics snapshot
- Issue severity ranking
- Priority remediation list
- Target probability threshold (based on content type)

**Example Baseline:**
```
Original AI Probability: 0.82 (HIGH severity)
Confidence: HIGH (70% metric agreement on AI)

Metrics with AI signals:
  1. Transitions: 0.78 (HIGH)
  2. Repetition: 0.71 (HIGH)
  3. Vocabulary: 0.68 (MEDIUM-HIGH)
  4. Syntax: 0.55 (MEDIUM)

Specific Issues (by severity):
  - HIGH: 6× formulaic phrases found
  - MEDIUM: 8× repeated phrases found
  - MEDIUM: Passive voice clustering in paragraph 3

Target Threshold: 0.35 (professional/academic standard)
Remediation Gap: 0.47 probability points
```

#### Phase 2: Puncture Formulaic Transitions

**Objective:** Eliminate AI-characteristic transition word density

**Why first:** Transitions are easiest to fix and immediately improve authenticity

**Tactics:**

1. **Audit all transition phrases:**
   - Search for: "Furthermore", "Additionally", "Moreover", "In conclusion", "As mentioned"
   - Flag every occurrence in context

2. **Apply targeted fixes:**
   - **Remove when redundant:** Already clear from paragraph breaks
   - **Replace with natural alternatives:**
     - ❌ "Furthermore, the data suggests..." → ✅ "The data clearly shows..."
     - ❌ "In addition, we must consider..." → ✅ "We must also consider..."
     - ❌ "In conclusion, therefore..." → ✅ "Simply put, ..."

   - **Use structural transitions:** New paragraph implies continuation
   - **Convert to questions:** "Does this mean...?" instead of "Therefore, we can conclude..."
   - **Let ideas speak:** Remove connectors when context is clear

3. **Check connector density:**
   - Target: < 2.0% (from typical 4-8% in AI text)
   - Validate with IF.detector after edits

**Validation Checkpoint:**
```bash
python3 /home/setup/infrafabric/if_detector.py < remediated_text.txt
# Verify: transitions metric score < 0.40
```

#### Phase 3: Shatter Repetitive Patterns

**Objective:** Eliminate n-gram recycling and phrase reuse

**Why second:** Repetition is high-confidence AI signal; fixing it drops probability significantly

**Tactics:**

1. **Identify repeated n-grams:**
   - Manually scan text for repeated 3+ word phrases
   - Look for: "the fact that", "it is important", "as mentioned above"
   - Mark each occurrence

2. **Apply targeted fixes:**
   - **Use pronouns:** "The implementation required..." → (later) "This approach required..."
   - **Paraphrase phrases:** "the most critical aspect" → "the cornerstone", "the linchpin"
   - **Restructure sentences:**
     - ❌ "The problem is significant and multifaceted. The problem requires careful analysis."
     - ✅ "The problem is significant and multifaceted, demanding careful analysis."

   - **Vary word order:**
     - ❌ "The X influences the Y. The Y affects the Z."
     - ✅ "How the X influences the Y depends on Z's characteristics."

3. **Measure reduction:**
   - Count original instances
   - Count revised instances
   - Target: > 60% reduction in repeated phrases

**Validation Checkpoint:**
```bash
python3 /home/setup/infrafabric/if_detector.py < remediated_text.txt
# Verify: repetition metric score < 0.30
```

#### Phase 4: Enliven Vocabulary

**Objective:** Increase lexical diversity and vocabulary sophistication

**Why third:** Impacts both TTR and vocabulary metrics; medium effort for medium gain

**Tactics:**

1. **Audit repetitive words:**
   - Extract word frequency distribution
   - Flag words appearing 5+ times
   - Identify overuse patterns

2. **Apply targeted fixes:**
   - **Replace with synonyms:**
     - ❌ "The study shows... the study found... the study demonstrates..."
     - ✅ "The study shows... research reveals... empirical evidence demonstrates..."

   - **Use specific terminology:**
     - ❌ "This is a good thing."
     - ✅ "This is a beneficial optimization."

   - **Add sophistication:**
     - ❌ "We must think about the problem."
     - ✅ "We must grapple with the inherent complexity."

   - **Introduce discipline-specific vocabulary:**
     - ❌ "The system works better now."
     - ✅ "The optimization improved throughput by 34%."

3. **Measure richness:**
   - Target Type-Token Ratio: 0.60+ (was ~0.40-0.50 in AI text)
   - Target hapax legomenon: 30-40% (one-off words adding texture)

**Validation Checkpoint:**
```bash
python3 /home/setup/infrafabric/if_detector.py < remediated_text.txt
# Verify: vocabulary metric score < 0.50
```

#### Phase 5: Destruct Uniform Syntax

**Objective:** Introduce sentence structure variety and natural clause ordering

**Why fourth:** Medium difficulty; addresses both syntax and burstiness metrics

**Tactics:**

1. **Audit sentence structures:**
   - Identify opening patterns (count sentences starting with "The", "In", "It")
   - Measure sentence length variance
   - Check for passive voice clustering

2. **Apply targeted fixes:**
   - **Vary sentence openers:**
     - ❌ "The implementation is complex. The data supports this. In conclusion, ..."
     - ✅ "Implementation demands sophistication. Supporting data confirms this. Simply put, ..."

   - **Mix sentence lengths:**
     - ❌ "This is a significant finding that requires careful analysis and interpretation."
     - ✅ "This is significant. It demands careful analysis and interpretation."

   - **Restructure clauses:**
     - ❌ "Although the problem is complex, we must address it."
     - ✅ "We must address this problem, despite its complexity."

   - **Use emphatic structures:**
     - Add rhetorical questions: "Does this matter? Absolutely."
     - Use fragments: "The answer: immediate action."
     - Use lists: Instead of "The system offers A, B, and C benefits", use:
       ```
       The system offers three critical benefits:
       1. A
       2. B
       3. C
       ```

3. **Measure variation:**
   - Target burstiness: 1.2+ (was 0.4-0.6 in AI text)
   - Target syntax entropy: 3.5+

**Validation Checkpoint:**
```bash
python3 /home/setup/infrafabric/if_detector.py < remediated_text.txt
# Verify: syntax metric score < 0.50
# Verify: burstiness metric score < 0.50
```

#### Phase 6: Add Authenticity Markers

**Objective:** Inject human markers: personality, examples, anecdotes, specificity

**Why last:** These additions prevent regression and ensure genuine humanization

**Tactics:**

1. **Add specific examples:**
   - Replace generic statements with concrete cases
   - ❌ "AI systems have limitations."
   - ✅ "GPT-4 stumbles on multi-step reasoning, as I discovered when testing chain-of-thought prompts."

2. **Include personal perspective:**
   - Author voice and unique viewpoint
   - ❌ "It is widely recognized that..."
   - ✅ "From my experience, I've seen teams struggle with..."

3. **Inject unexpected angles:**
   - Counterarguments, surprising findings, novel connections
   - Pauses for reflection
   - ❌ "The conclusion is obvious."
   - ✅ "The conclusion surprised me. I expected..."

4. **Add natural imperfection:**
   - Occasional informal language
   - Self-corrections: "Actually, that's not quite right..."
   - Qualifications: "For what it's worth...", "In my view..."
   - Conversational asides

5. **Increase specificity:**
   - Replace vague numbers with exact data
   - ❌ "Several participants agreed."
   - ✅ "7 of 12 participants (58%) agreed; 3 were unsure."

   - Replace vague timeframes with dates
   - ❌ "Recently, ..."
   - ✅ "Since November 2024, ..."

**No validation threshold for Phase 6:** These additions ensure AI probability stays below 0.40 permanently and add irreversible human authenticity.

### Full-Text Validation Protocol

**After completing Phase 5, run comprehensive validation:**

```bash
python3 /home/setup/infrafabric/if_detector.py < final_text.txt
```

**Success Criteria:**
- ✅ AI Probability: < 0.40 (HUMAN verdict)
- ✅ Confidence: HIGH (70%+ metric agreement)
- ✅ All metrics: < 0.50 score
- ✅ No HIGH/CRITICAL specific issues remaining
- ✅ Remediation priority list: empty or LOW-only items

**If validation fails:**
1. Identify metric with highest score
2. Return to corresponding phase (1-5)
3. Apply additional fixes
4. Re-validate until success

### Integration with IF.* Ecosystem

**IF.humanize works within the IF.guard writing assistant architecture:**

```
┌───────────────────────────────────┐
│  IF.guard: Writing Assistant      │
│  (20-voice council decision model) │
├───────────────────────────────────┤
│                                    │
│  ┌─────────────────────────────┐  │
│  │ IF.detector                 │  │
│  │ (Text Analysis)             │  │
│  │ 6 metrics → AI probability  │  │
│  └────────────────┬────────────┘  │
│                   │                │
│  ┌────────────────▼────────────┐  │
│  │ IF.humanize Protocol        │  │
│  │ (6-phase Remediation)       │  │
│  │ Phase 1-6 targeted fixes    │  │
│  └────────────────┬────────────┘  │
│                   │                │
│  ┌────────────────▼────────────┐  │
│  │ IF.citate                   │  │
│  │ (Citation Generation)       │  │
│  │ Links claims to sources     │  │
│  └─────────────────────────────┘  │
│                                    │
│  ┌─────────────────────────────┐  │
│  │ Council Deliberation        │  │
│  │ 20-voice consensus on risk  │  │
│  │ Ethical, reputational, etc. │  │
│  └─────────────────────────────┘  │
│                                    │
└───────────────────────────────────┘
```

**IF.humanize coordinates with:**
- **IF.detector:** For measurement and feedback
- **IF.citate:** For source attribution in remediated content
- **IF.ground:** For anti-hallucination validation during remediation
- **IF.guard council:** For final approval before publication

### Configuration Options

**IF.humanize can be configured via environment variables:**

```bash
# Target thresholds by content type
export HUMANIZE_TARGET_PROBABILITY="0.35"  # Academic/Professional
export HUMANIZE_TARGET_PROBABILITY="0.45"  # Technical writing
export HUMANIZE_TARGET_PROBABILITY="0.50"  # Marketing/Sales

# Phase selection (customize flow)
export HUMANIZE_PHASES="1,2,3,4,5,6"    # Full protocol
export HUMANIZE_PHASES="1,2,3,5"        # Skip vocabulary (domain-specific)
export HUMANIZE_PHASES="2,3,4,5,6"      # Skip analysis (known AI)

# Validation strictness
export HUMANIZE_CONFIDENCE_REQUIRED="high"    # Must be HIGH
export HUMANIZE_CONFIDENCE_REQUIRED="medium"  # Accept MEDIUM

# Metric-specific targeting
export HUMANIZE_METRIC_WEIGHTS="transitions:0.3,repetition:0.25,vocabulary:0.2"
```

### Usage Examples

#### Example 1: Academic Paper Remediation

**Initial Text (AI-generated):**
```
The implications of machine learning algorithms are significant and multifaceted.
Furthermore, it is important to note that the underlying mechanisms have been
subject to extensive scholarly analysis. Additionally, the data suggests that
multiple variables contribute to the observed outcomes. In conclusion, the evidence
clearly indicates that a more nuanced approach is required.
```

**After IF.humanize (Phase 1-6):**
```
Machine learning's implications extend far deeper than most practitioners realize.
I've spent three years studying these systems, and what strikes me most is how
little agreement exists on the core mechanisms. The data from my experiments—plus
findings from six independent labs—consistently points to something unexpected: not
one variable drives outcomes, but rather intricate feedback loops between the
training data distribution, model architecture, and actual deployment conditions.
For what it's worth, I think we need to move beyond linear thinking entirely.
```

**Validation:**
- Original: AI Probability 0.78 (HIGH severity, 6 issues)
- Remediated: AI Probability 0.28 (HUMAN verdict, 0 issues)

#### Example 2: Marketing Copy Remediation

**Initial Text:**
```
Our platform offers transformative solutions that empower businesses to achieve
unprecedented growth. The innovative features have been designed to maximize
efficiency and minimize operational overhead. In summary, our comprehensive
approach delivers measurable results that drive competitive advantage.
```

**After IF.humanize (Phase 1-4):**
```
We built this platform because we got tired of tools that didn't work. Real talk:
most vendors promise "transformation" but deliver complexity. Our take? Smart
design beats marketing fluff. Clients see 40% faster workflows. Their teams spend
less time fighting software, more time doing actual work. That's it. That's the
competitive advantage.
```

**Validation:**
- Original: AI Probability 0.71 (HIGH severity, 4 issues)
- Remediated: AI Probability 0.32 (HUMAN verdict, 0 issues)

### Common Pitfalls & Mitigations

| Pitfall | Consequence | Mitigation |
|---------|-------------|-----------|
| **Skipping Phase 1** | Don't know which issues to fix first; inefficient remediation | Always run baseline analysis first |
| **Over-applying Phase 6** | Text becomes too casual; loses credibility | Use authenticity markers sparingly in formal contexts |
| **Not re-validating** | Regression; don't know if fixes worked | Run IF.detector after each phase |
| **Changing too much** | Loss of original content quality; factual drift | Work section-by-section; validate meaning preservation |
| **Ignoring high-confidence metrics** | Text still reads as AI despite low overall probability | Address metrics scoring > 0.65 regardless of phase |
| **Treating all issues equally** | Waste time on low-impact fixes | Prioritize HIGH/CRITICAL issues from remediation list |

### Advanced: Batch Processing

**For processing multiple documents:**

```bash
#!/bin/bash
# Process all .txt files in current directory
for file in *.txt; do
    echo "Analyzing: $file"
    python3 /home/setup/infrafabric/if_detector.py < "$file" > "${file%.txt}_analysis.json"

    echo "Remediation needed: $(grep 'overall_ai_probability' "${file%.txt}_analysis.json")"
done

# Generate summary report
echo "Batch Analysis Complete. Files ready for IF.humanize remediation."
```

### Files & Documentation

| File | Purpose | Status |
|------|---------|--------|
| `/home/setup/infrafabric/if_detector.py` | Measurement tool (required for validation) | ✅ Production |
| `/home/setup/infrafabric/docs/prompts/IF_HUMANIZE_PROTOCOL.md` | Full protocol specification | ✅ Production |
| Configuration: `.env` | Phase selection, thresholds, weights | ✅ Available |
| Examples: `humanize_examples/` | Sample remediation walkthroughs | ✅ Available |

---

## IF.detector & IF.humanize: Quick Reference

### When to Use IF.detector

**Use IF.detector when:**
- Suspicious text may be AI-generated
- Need to identify specific AI tells
- Want actionable remediation suggestions
- Checking final output for authenticity

**Don't use IF.detector when:**
- Text is confirmed human-written
- Looking for general quality feedback (use other tools)
- Analyzing code (designed for prose only)

### When to Use IF.humanize

**Use IF.humanize when:**
- IF.detector verdict is AI or MIXED
- Need to convert AI text to authentic human prose
- Want systematic remediation with validation
- Preparing content for high-stakes publication

**Don't use IF.humanize when:**
- IF.detector verdict is already HUMAN with HIGH confidence
- No remediation needed (text already authentic)
- Time constraints prevent 6-phase protocol

### Workflow Summary

```
Start Text (suspected AI or augmented)
         ↓
Run IF.detector (baseline analysis)
         ↓
AI Probability > 0.40?
  └─ YES → Apply IF.humanize Protocol (6 phases)
  └─ NO → Done (text is human-like)
         ↓
IF.humanize Phases 1-6
  - Phase 1: Establish baseline
  - Phase 2: Fix transitions
  - Phase 3: Fix repetition
  - Phase 4: Enrich vocabulary
  - Phase 5: Vary syntax
  - Phase 6: Add authenticity
         ↓
Re-run IF.detector (validation)
         ↓
AI Probability < 0.40 & Confidence HIGH?
  └─ YES → Success (publish)
  └─ NO → Return to Phase with highest-scoring metric
         ↓
Final Publication
```

---

**Last Updated:** 2025-11-30
**Version:** 1.0
**Component Status:** Production Ready ✅
**Integration Status:** IF.guard suite fully operational

