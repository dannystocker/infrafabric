# IF.detector CLI Interface - Complete Guide

A production-grade command-line interface for AI text detection and humanization. Built on top of the `TextAnalyzer` orchestrator with six complementary detection metrics.

## Installation

### Prerequisites
- Python 3.8+
- pip or venv

### Setup

```bash
cd /home/setup/infrafabric

# Option 1: Virtual Environment (Recommended)
python3 -m venv venv_detector
source venv_detector/bin/activate
pip install -r requirements_detector.txt

# Option 2: System-wide (if allowed)
pip install nltk

# Download NLTK data (one-time)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"
```

## Architecture Overview

```
CLIApplication
├── Command Router (argparse)
│   ├── analyze    → Single file/text analysis
│   ├── humanize   → Humanization suggestions
│   └── batch      → Batch directory processing
│
├── TextAnalyzer (Core Orchestrator)
│   ├── PerplexityMetric      (token sequence analysis)
│   ├── BurstinessMetric      (sentence length variance)
│   ├── VocabularyMetric      (lexical diversity)
│   ├── TransitionMetric      (formulaic phrase detection)
│   ├── RepetitionMetric      (n-gram patterns)
│   └── SyntaxMetric          (syntactic uniformity)
│
├── HumanizationEngine
│   ├── Metric suggestion generation
│   ├── Implementation roadmap
│   └── Expected improvement prediction
│
└── BatchProcessor
    ├── Directory scanning
    ├── Aggregated statistics
    └── Report generation
```

## Command Reference

### 1. ANALYZE Command

Comprehensive AI probability analysis of single text or file.

#### Syntax
```bash
python if_detector_cli.py analyze <INPUT> [OPTIONS]
```

#### Arguments
- `INPUT`: Text string or file path to analyze (auto-detected)

#### Options
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--verbose` / `-v` | boolean | false | Show detailed metric breakdown |
| `--json` | boolean | false | Output as machine-readable JSON |
| `--compact` | boolean | false | Single-line summary format |
| `--threshold` | float | 0.0 | Only process if AI probability > threshold (0.0-1.0) |

#### Examples

**Basic analysis with human-readable output:**
```bash
python if_detector_cli.py analyze "The implications of this phenomenon are significant and multifaceted."
```

**Analyze a file with verbose metrics:**
```bash
python if_detector_cli.py analyze document.txt --verbose
```

**JSON output for programmatic use:**
```bash
python if_detector_cli.py analyze article.txt --json | jq '.overall_ai_probability'
```

**Only analyze if AI probability > 70%:**
```bash
python if_detector_cli.py analyze file.txt --threshold 0.7 --json
```

**Compact summary (single line):**
```bash
python if_detector_cli.py analyze text.txt --compact
```

#### Output Example (Human-Readable)

```
================================================================================
IF.DETECTOR ANALYSIS REPORT
================================================================================

VERDICT: AI
AI Probability: 78.4%
Confidence: HIGH

TEXT STATISTICS:
  Words: 145
  Sentences: 8
  Tokens: 159
  Avg Sentence Length: 18.1 words

METRIC BREAKDOWN:
----------------

PERPLEXITY
  Score: 85.3% (0=Human, 1=AI)
  Verdict: AI
  Human Range: 60-100
  AI Range: 20-50
  Analysis: Highly predictable sequences characteristic of AI models

BURSTINESS
  Score: 15.2% (0=Human, 1=AI)
  Verdict: AI
  Human Range: 1.2-2.5
  AI Range: 0.3-0.8
  Analysis: Artificially uniform sentence structure

VOCABULARY
  Score: 42.1% (0=Human, 1=AI)
  Verdict: MIXED
  Human Range: 0.60-0.85
  AI Range: 0.35-0.55
  Analysis: Limited vocabulary with heavy repetition (AI-like)

TRANSITIONS
  Score: 72.5% (0=Human, 1=AI)
  Verdict: AI
  Human Range: 0.5-2.0%
  AI Range: 4.0-8.0%
  Analysis: Excessive formulaic transitions characteristic of AI

REPETITION
  Score: 68.9% (0=Human, 1=AI)
  Verdict: AI
  Human Range: 5-15%
  AI Range: 25-45%
  Analysis: Excessive repetition of word sequences (AI-like)

SYNTAX
  Score: 35.7% (0=Human, 1=AI)
  Verdict: MIXED
  Human Range: 3.5-5.0
  AI Range: 1.5-3.0
  Analysis: Repetitive syntactic patterns (AI-like)

----------------

DETECTED ISSUES:

HIGH SEVERITY:
  Line 2: formulaic_opening
    Text: Furthermore, it is important to note that the...
    Issue: Formulaic phrase detected: 'it is important to note'
    Fix: Replace or remove 'it is important to note' with more natural language

MEDIUM SEVERITY:
  Line 4: formulaic_closing
    Text: In conclusion, the evidence clearly indicates...
    Issue: Formulaic phrase detected: 'in conclusion'
    Fix: Replace or remove 'in conclusion' with more natural language

----------------

REMEDIATION PRIORITY:
  1. high_repetition (repetition)
  2. formulaic_opening (line 2)
  3. high_transitions (transitions)
  4. formulaic_closing (line 4)
  5. uniform_sentence_length (burstiness)

================================================================================
```

#### JSON Output Example

```json
{
  "overall_ai_probability": 0.784,
  "confidence": "high",
  "verdict": "AI",
  "metrics": {
    "perplexity": {
      "score": 0.853,
      "human_range": "60-100",
      "ai_range": "20-50",
      "verdict": "AI",
      "reasoning": "Highly predictable sequences characteristic of AI models",
      "supporting_data": {
        "perplexity_raw": 32.45,
        "cross_entropy": 5.02,
        "char_bigram_count": 847,
        "unique_bigrams": 203
      }
    }
  },
  "specific_issues": [
    {
      "line": 2,
      "line_text": "Furthermore, it is important to note that the...",
      "issue_type": "formulaic_opening",
      "description": "Formulaic phrase detected: 'it is important to note'",
      "suggestion": "Replace or remove 'it is important to note' with more natural language",
      "severity": "medium",
      "evidence": {
        "phrase": "it is important to note",
        "position": 48
      }
    }
  ],
  "remediation_priority": [
    "high_repetition (repetition)",
    "formulaic_opening (line 2)"
  ],
  "text_statistics": {
    "token_count": 159,
    "sentence_count": 8,
    "word_count": 145,
    "avg_sentence_length": 18.125
  }
}
```

---

### 2. HUMANIZE Command

Generate specific suggestions to make AI-detected text more human-like.

#### Syntax
```bash
python if_detector_cli.py humanize <INPUT> [OPTIONS]
```

#### Arguments
- `INPUT`: Text string or file path to humanize

#### Options
| Flag | Type | Choices | Default | Description |
|------|------|---------|---------|-------------|
| `--intensity` | string | subtle, moderate, aggressive | moderate | Level of suggested changes |
| `--preserve-technical` | boolean | - | false | Skip domain-specific terminology |
| `--json` | boolean | - | false | Output as JSON |
| `--verbose` / `-v` | boolean | - | false | Show implementation details |

#### Intensity Levels

**subtle** (30% modification intensity)
- Quick wins and obvious fixes only
- Phase 1 tactics from low-effort category
- Minimal disruption to original voice
- Improvement potential: ~10-15%

**moderate** (60% modification intensity)
- Balanced improvement approach
- Phases 1 & 2 (low + medium effort)
- Significant improvement without major rewrite
- Improvement potential: ~25-35%

**aggressive** (90% modification intensity)
- Comprehensive transformation
- All three phases including high-effort tactics
- Restructured sentences, varied vocabulary
- Improvement potential: ~40-60%

#### Examples

**Basic humanization with moderate intensity:**
```bash
python if_detector_cli.py humanize article.txt
```

**Aggressive humanization (comprehensive changes):**
```bash
python if_detector_cli.py humanize document.txt --intensity aggressive --verbose
```

**Preserve technical terms (for research papers):**
```bash
python if_detector_cli.py humanize research_paper.txt --preserve-technical --intensity moderate
```

**JSON output for programmatic processing:**
```bash
python if_detector_cli.py humanize file.txt --json | jq '.expected_outcome'
```

**Subtle changes only:**
```bash
python if_detector_cli.py humanize draft.txt --intensity subtle
```

#### Output Example (Human-Readable)

```
================================================================================
HUMANIZATION ANALYSIS
================================================================================

ORIGINAL TEXT ANALYSIS:
  AI Probability: 78%
  Verdict: AI
  Confidence: HIGH
  Issues Detected: 3

EXPECTED OUTCOME (after humanization):
  New AI Probability: 45%
  Improvement: 33.2 percentage points
  Expected Verdict: MIXED

HUMANIZATION PLAN:
  Intensity: MODERATE
  Suggested Changes: 12

DETAILED SUGGESTIONS:

PERPLEXITY:
  1. Add specific examples
     Include 2-3 concrete examples or case studies
  2. Include personal anecdotes
     Reference personal experience or unique perspective
  3. Add unexpected insights
     Include counter-intuitive arguments or surprising angles

TRANSITIONS:
  1. Remove formulaic transitions
     Delete 'Furthermore', 'Additionally', 'Moreover' where unnecessary
  2. Use structural transitions
     Let paragraph breaks and context provide continuity
  3. Use varied connectors
     Replace repeated transitions with questions or statements

REPETITION:
  1. Refactor repeated phrases
     Paraphrase 3+ word phrases that appear multiple times
  2. Use pronouns
     Replace repeated nouns with pronouns (this, that, it)
  3. Restructure sentences
     Vary word order to avoid repetitive sequences

----------------

IMPLEMENTATION ROADMAP:

PHASE 1 (Quick Wins - Low Effort):
  • Let paragraph breaks and context provide continuity
  • Delete 'Furthermore', 'Additionally', 'Moreover' where unnecessary
  • Occasionally use sentence fragments for impact

PHASE 2 (Medium Effort - Significant Impact):
  • Paraphrase 3+ word phrases that appear multiple times
  • Alternate between very short (3-5 word) and complex sentences
  • Replace repeated words with varied alternatives

================================================================================
```

#### JSON Output Example

```json
{
  "original_analysis": {
    "ai_probability": 0.784,
    "verdict": "AI",
    "confidence": "high",
    "issues_detected": 3
  },
  "humanization_plan": {
    "intensity": "moderate",
    "preserve_technical": false,
    "estimated_effort": 12
  },
  "suggested_changes": [
    {
      "metric": "perplexity",
      "tactic": "Add specific examples",
      "description": "Include 2-3 concrete examples or case studies",
      "effort": "medium"
    },
    {
      "metric": "transitions",
      "tactic": "Remove formulaic transitions",
      "description": "Delete 'Furthermore', 'Additionally', 'Moreover' where unnecessary",
      "effort": "low"
    }
  ],
  "expected_improvements": {
    "perplexity": {
      "current_score": 0.853,
      "target_score": 0.51,
      "potential_improvement": 0.343
    }
  },
  "expected_outcome": {
    "new_ai_probability": 0.451,
    "improvement_percentage": 33.27,
    "expected_verdict": "MIXED"
  },
  "implementation_roadmap": [
    "PHASE 1 (Quick Wins - Low Effort):",
    "  • Let paragraph breaks and context provide continuity"
  ]
}
```

---

### 3. BATCH Command

Process multiple files and generate aggregated report.

#### Syntax
```bash
python if_detector_cli.py batch <DIRECTORY> [OPTIONS]
```

#### Arguments
- `DIRECTORY`: Path to directory containing files to analyze

#### Options
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--pattern` / `-p` | string | *.txt | File glob pattern to match |
| `--output` / `-o` | string | - | Write JSON report to file |
| `--threshold` | float | 0.5 | Flag files with AI prob > threshold |
| `--json` | boolean | false | Output JSON to stdout |
| `--verbose` / `-v` | boolean | false | Show detailed file information |

#### Examples

**Scan directory for suspicious files:**
```bash
python if_detector_cli.py batch /path/to/documents
```

**Scan and save report:**
```bash
python if_detector_cli.py batch ./essays --output scan_report.json --threshold 0.6
```

**Process multiple file types:**
```bash
python if_detector_cli.py batch ./content --pattern "*.{txt,md}" --verbose
```

**Lower threshold for sensitive context:**
```bash
python if_detector_cli.py batch ./submissions --threshold 0.3 --output flagged.json
```

**Raw JSON output for processing:**
```bash
python if_detector_cli.py batch ./docs --json | jq '.files[] | select(.flagged == true)'
```

#### Output Example (Human-Readable)

```
================================================================================
BATCH ANALYSIS REPORT
================================================================================

Directory: /path/to/documents
Scan Time: 2025-11-30T14:32:45.123456

SUMMARY:
  Files Analyzed: 47
  Files Flagged (AI-likely): 8
  Flagged Percentage: 17.0%
  Threshold: 50%

STATISTICS:
  Average AI Probability: 38.2%
  Range: 5% - 89%

FLAGGED FILES (AI-likely):
----------------

suspicious_essay.txt
  AI Probability: 89%
  Verdict: AI
  Issues: 7
  Top Priority: high_repetition (repetition)

term_paper_2024.txt
  AI Probability: 76%
  Verdict: AI
  Issues: 4
  Top Priority: high_transitions (transitions)

abstract.txt
  AI Probability: 61%
  Verdict: MIXED
  Issues: 2
  Top Priority: formulaic_opening (line 3)

HUMAN-LIKELY FILES: 39
----------------
assignment_01.txt: 12%
notes.txt: 8%
reflection.txt: 22%
...

================================================================================
```

#### JSON Output (Compact)

```json
{
  "directory": "/path/to/documents",
  "scan_timestamp": "2025-11-30T14:32:45.123456",
  "files_analyzed": 47,
  "files_flagged": 8,
  "average_ai_probability": 0.382,
  "min_ai_probability": 0.05,
  "max_ai_probability": 0.89,
  "threshold": 0.5,
  "flagged_percentage": 17.0,
  "files": [
    {
      "filename": "suspicious_essay.txt",
      "path": "/path/to/documents/suspicious_essay.txt",
      "ai_probability": 0.89,
      "verdict": "AI",
      "confidence": "high",
      "word_count": 1247,
      "issues_detected": 7,
      "file_size_bytes": 8456,
      "flagged": true,
      "remediation_priority": [
        "high_repetition (repetition)",
        "high_transitions (transitions)",
        "formulaic_opening (line 2)"
      ]
    }
  ]
}
```

---

## Detection Metrics Explained

### 1. Perplexity Score (25% weight)
**What it measures:** Predictability of token sequences

- **Human writing:** 60-100 (high perplexity = varied, unpredictable)
- **AI writing:** 20-50 (low perplexity = predictable)

**What to look for:** AI tends to use more predictable word combinations and transitions.

### 2. Burstiness Index (8% weight)
**What it measures:** Variance in sentence length

- **Human writing:** 1.2-2.5 (high burstiness = varied lengths)
- **AI writing:** 0.3-0.8 (low burstiness = uniform lengths)

**What to look for:** Humans naturally vary sentence length; AI tends toward uniformity.

### 3. Vocabulary Richness (20% weight)
**What it measures:** Lexical diversity (Type-Token Ratio, Hapax Legomenon)

- **Human writing:** TTR 0.60-0.85 (diverse vocabulary)
- **AI writing:** TTR 0.35-0.55 (limited vocabulary, high repetition)

**What to look for:** Humans use more varied and unique word choices.

### 4. Transition Density (15% weight)
**What it measures:** Frequency of formulaic connector phrases

- **Human writing:** 0.5-2.0% (sparse use of transitions)
- **AI writing:** 4.0-8.0% (excessive transitions like "Furthermore", "Additionally")

**What to look for:** AI overuses phrases like "It is important to note", "As mentioned above".

### 5. N-gram Repetition (20% weight)
**What it measures:** Repeated word sequences at multiple levels

- **Human writing:** 5-15% (natural phrase variation)
- **AI writing:** 25-45% (excessive repetition)

**What to look for:** Repeated 3+ word phrases indicate AI generation.

### 6. Syntax Uniformity (12% weight)
**What it measures:** Variety in sentence structure patterns

- **Human writing:** Entropy 3.5-5.0 (diverse structures)
- **AI writing:** Entropy 1.5-3.0 (repetitive patterns)

**What to look for:** AI favors consistent Subject-Verb-Object patterns.

---

## Advanced Usage Patterns

### Integration with Scripts

**Batch process and filter high-risk files:**
```bash
python if_detector_cli.py batch ./essays --json | \
  jq '.files[] | select(.ai_probability > 0.7)' | \
  jq -r '.filename'
```

**Generate report with custom threshold:**
```bash
for threshold in 0.3 0.5 0.7; do
  echo "Scanning with threshold $threshold:"
  python if_detector_cli.py batch ./docs --threshold $threshold --json | \
    jq -r '.flagged_percentage'
done
```

**Analyze and humanize automatically:**
```bash
python if_detector_cli.py analyze file.txt --json | \
  jq -r '.overall_ai_probability' | \
  awk '{if ($1 > 0.65) print "HIGH AI PROBABILITY"; else print "ACCEPTABLE"}'
```

### Piping and Redirection

**Redirect analysis to file:**
```bash
python if_detector_cli.py analyze article.txt --verbose > analysis.txt 2>&1
```

**Real-time JSON parsing:**
```bash
python if_detector_cli.py analyze text.txt --json | \
  jq '.metrics | keys[] as $metric | "\($metric): \(.[$metric].score)"'
```

**Filter batch results by severity:**
```bash
python if_detector_cli.py batch . --json | \
  jq '.files[] | select(.issues_detected > 3) | .filename'
```

---

## Configuration & Customization

### Modifying Default Thresholds

Edit the `TextAnalyzer` class in `if_detector.py`:

```python
# In _determine_verdict method
if overall_prob > 0.65:  # Adjust verdict threshold
    return Verdict.AI
elif overall_prob < 0.35:
    return Verdict.HUMAN
```

### Adjusting Metric Weights

Edit the `_calculate_overall_probability` method:

```python
weights = {
    "perplexity": 0.25,      # Increase for stricter detection
    "repetition": 0.20,
    "vocabulary": 0.20,
    "transitions": 0.15,
    "syntax": 0.12,
    "burstiness": 0.08
}
```

### Adding Custom Remediation Rules

Extend `RemediationEngine` in `if_detector.py`:

```python
self.remediation_map["custom_issue"] = {
    "severity": "medium",
    "suggestion": "Your suggestion here",
    "tactics": [
        "Tactic 1",
        "Tactic 2"
    ]
}
```

---

## Troubleshooting

### NLTK Module Not Found
```bash
# Activate venv and install
source venv_detector/bin/activate
pip install -r requirements_detector.txt
```

### File Encoding Issues
```bash
# Specify encoding for problematic files
python if_detector_cli.py analyze file.txt  # Auto-detects UTF-8
```

### Memory Issues with Large Batches
```bash
# Process in smaller chunks
python if_detector_cli.py batch --pattern "a*.txt"
python if_detector_cli.py batch --pattern "b*.txt"
```

### JSON Output Formatting
```bash
# Pretty-print with jq
python if_detector_cli.py analyze file.txt --json | jq '.'

# Compact output
python if_detector_cli.py analyze file.txt --json | jq -c '.'
```

---

## Performance Characteristics

| Metric | Time (per 1000 words) | Memory |
|--------|----------------------|--------|
| Perplexity | ~50ms | 2MB |
| Burstiness | ~10ms | 1MB |
| Vocabulary | ~30ms | 2MB |
| Transitions | ~15ms | 1MB |
| Repetition | ~40ms | 3MB |
| Syntax | ~80ms | 2MB |
| **Total** | **~225ms** | **~11MB** |

**Full analysis of 50KB file:** ~1-2 seconds

---

## License & Attribution

Part of the IF.guard framework for evaluating AI-generated content detection.

Citation: "IF.detector: In-house GPTZero Alternative for AI Text Detection"
