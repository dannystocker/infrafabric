# IF.detector Integration Guide

**How to integrate IF.detector into applications and workflows**

---

## Installation

### Prerequisites
```bash
pip install nltk >= 3.8
pip install python >= 3.8
```

### Setup
```python
from if_detector import TextAnalyzer

# Initialize (one-time, ~1-2 seconds on first run for NLTK downloads)
analyzer = TextAnalyzer()

# Ready to use
result = analyzer.analyze("Your text here...")
```

---

## API Reference

### TextAnalyzer Class

```python
class TextAnalyzer:
    def analyze(text: str) -> DetectionResult
```

**Parameters:**
- `text` (str): Input text to analyze (minimum 20 words recommended)

**Returns:**
- `DetectionResult`: Complete analysis with all metrics and remediation advice

**Raises:**
- IndexError: If text is empty
- ValueError: If text cannot be tokenized

### DetectionResult Object

```python
@dataclass
class DetectionResult:
    overall_ai_probability: float        # 0.0-1.0
    confidence: ConfidenceLevel          # low|medium|high
    verdict: Verdict                     # HUMAN|MIXED|AI
    metrics: Dict[str, MetricResult]     # 6 metrics
    specific_issues: List[IssueFlag]     # Line issues
    remediation_priority: List[str]      # Ordered fixes
    token_count: int
    sentence_count: int
    word_count: int
    analysis_timestamp: str

    # Methods
    to_dict() -> Dict
    to_json() -> str
```

### MetricResult Object

```python
@dataclass
class MetricResult:
    score: float                # 0.0-1.0 (0=human, 1=AI)
    human_range: str           # e.g., "60-100"
    ai_range: str              # e.g., "20-50"
    verdict: Verdict           # HUMAN|MIXED|AI
    reasoning: str             # Explanation
    supporting_data: Dict      # Raw metric values
```

### IssueFlag Object

```python
@dataclass
class IssueFlag:
    line_number: int           # Where in text
    line_text: str             # Problem snippet
    issue_type: str            # Category
    description: str           # What's wrong
    suggestion: str            # How to fix
    severity: str              # low|medium|high
    evidence: Dict             # Supporting data
```

---

## Usage Examples

### Example 1: Simple Detection

```python
from if_detector import TextAnalyzer

analyzer = TextAnalyzer()
text = "..."  # Your text

result = analyzer.analyze(text)

# Quick verdict
if result.overall_ai_probability > 0.65:
    print(f"ALERT: Likely AI-generated (confidence: {result.confidence.value})")
else:
    print("Text appears human-written")
```

### Example 2: Detailed Analysis Report

```python
analyzer = TextAnalyzer()
result = analyzer.analyze(text)

print(f"{'='*60}")
print(f"AI Detection Report")
print(f"{'='*60}")
print(f"Overall AI Probability: {result.overall_ai_probability:.1%}")
print(f"Verdict: {result.verdict.value}")
print(f"Confidence: {result.confidence.value}")
print()

print("METRIC BREAKDOWN:")
for metric_name, metric in result.metrics.items():
    status = "🚨 AI" if metric.verdict.value == "AI" else "✓ HUMAN" if metric.verdict.value == "HUMAN" else "⚠ MIXED"
    print(f"  {metric_name:12} {status:8} {metric.reasoning[:50]}...")
print()

if result.specific_issues:
    print("SPECIFIC ISSUES:")
    for issue in result.specific_issues:
        print(f"  Line {issue.line_number}: {issue.description}")
        print(f"    → {issue.suggestion}")
        print()

if result.remediation_priority:
    print("REMEDIATION PRIORITY:")
    for i, fix in enumerate(result.remediation_priority, 1):
        print(f"  {i}. {fix}")
```

### Example 3: Batch Processing

```python
analyzer = TextAnalyzer()
texts = [...]  # List of documents

results = []
for doc_id, text in enumerate(texts):
    result = analyzer.analyze(text)
    results.append({
        'id': doc_id,
        'ai_probability': result.overall_ai_probability,
        'verdict': result.verdict.value,
        'confidence': result.confidence.value,
        'issues_found': len(result.specific_issues)
    })

# Find high-risk documents
high_risk = [r for r in results if r['ai_probability'] > 0.65]
print(f"Found {len(high_risk)} potentially AI-generated documents out of {len(results)}")

# Export results
import json
with open('detection_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Example 4: Integration with Content Moderation

```python
analyzer = TextAnalyzer()

def check_content_authenticity(text: str, threshold: float = 0.65) -> dict:
    """Check if content is authentic human-written"""
    result = analyzer.analyze(text)

    return {
        'is_ai': result.overall_ai_probability > threshold,
        'probability': result.overall_ai_probability,
        'issues': [
            {
                'type': issue.issue_type,
                'line': issue.line_number,
                'severity': issue.severity,
                'suggestion': issue.suggestion
            }
            for issue in result.specific_issues
        ],
        'can_proceed': result.confidence.value in ['HIGH', 'MEDIUM'],
        'action': 'APPROVE' if result.overall_ai_probability < 0.4
                  else 'REJECT' if result.overall_ai_probability > 0.75 and result.confidence.value == 'HIGH'
                  else 'REVIEW'
    }

# Usage
verdict = check_content_authenticity(user_submitted_text)
if verdict['action'] == 'APPROVE':
    post_content(user_submitted_text)
elif verdict['action'] == 'REJECT':
    notify_user("Content appears to be AI-generated. Please submit original work.")
else:  # REVIEW
    flag_for_manual_review(user_submitted_text, verdict)
```

### Example 5: Iterative Improvement

```python
analyzer = TextAnalyzer()

def improve_authenticity(text: str, target_probability: float = 0.3) -> str:
    """Iteratively improve text authenticity score"""
    iteration = 0
    current_text = text

    while iteration < 5:
        result = analyzer.analyze(current_text)

        if result.overall_ai_probability < target_probability:
            print(f"✓ Target achieved after {iteration} iterations")
            return current_text

        print(f"\nIteration {iteration + 1}")
        print(f"  Current probability: {result.overall_ai_probability:.1%}")
        print(f"  Highest priority fix: {result.remediation_priority[0] if result.remediation_priority else 'None'}")

        # Apply first remediation (simulated)
        if result.specific_issues:
            issue = result.specific_issues[0]
            print(f"  Applying fix: {issue.suggestion}")
            # In real scenario: apply actual text transformations
            # For now, just note what would be done
            current_text = apply_remediation(current_text, issue)

        iteration += 1

    return current_text
```

### Example 6: API Endpoint (Flask)

```python
from flask import Flask, request, jsonify
from if_detector import TextAnalyzer

app = Flask(__name__)
analyzer = TextAnalyzer()

@app.route('/api/detect', methods=['POST'])
def detect():
    """Detect AI-generated text"""
    data = request.json

    if 'text' not in data:
        return jsonify({'error': 'Missing text field'}), 400

    if len(data['text'].split()) < 20:
        return jsonify({'error': 'Text too short (minimum 20 words)'}), 400

    try:
        result = analyzer.analyze(data['text'])

        return jsonify({
            'success': True,
            'overall_ai_probability': result.overall_ai_probability,
            'confidence': result.confidence.value,
            'verdict': result.verdict.value,
            'metrics': {
                name: {
                    'score': metric.score,
                    'verdict': metric.verdict.value
                }
                for name, metric in result.metrics.items()
            },
            'issues_count': len(result.specific_issues),
            'remediation_count': len(result.remediation_priority)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/detect/detailed', methods=['POST'])
def detect_detailed():
    """Detect with full remediation advice"""
    data = request.json

    if 'text' not in data:
        return jsonify({'error': 'Missing text field'}), 400

    try:
        result = analyzer.analyze(data['text'])
        return jsonify(result.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Example 7: CLI Tool

```python
#!/usr/bin/env python3
"""
IF.detector CLI Tool
Usage: python cli_detector.py <file.txt> [--json]
"""

import sys
import argparse
from if_detector import TextAnalyzer

def main():
    parser = argparse.ArgumentParser(description='Detect AI-generated text')
    parser.add_argument('file', help='Text file to analyze')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--threshold', type=float, default=0.65, help='AI threshold')
    args = parser.parse_args()

    # Read file
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)

    # Analyze
    analyzer = TextAnalyzer()
    result = analyzer.analyze(text)

    # Output
    if args.json:
        print(result.to_json())
    else:
        # Human-readable output
        print(f"Analysis Results")
        print(f"{'='*60}")
        print(f"Overall AI Probability: {result.overall_ai_probability:.1%}")
        print(f"Verdict: {result.verdict.value}")
        print(f"Confidence: {result.confidence.value}")
        print()

        if result.overall_ai_probability > args.threshold:
            print(f"⚠️  WARNING: Text likely AI-generated")
        else:
            print(f"✓ Text appears human-written")

        print()
        print(f"Metrics: {len(result.metrics)}")
        for name, metric in result.metrics.items():
            print(f"  {name}: {metric.verdict.value} (score: {metric.score:.2f})")

        if result.specific_issues:
            print()
            print(f"Issues Found: {len(result.specific_issues)}")
            for issue in result.specific_issues[:5]:  # Show top 5
                print(f"  Line {issue.line_number}: {issue.issue_type}")

if __name__ == '__main__':
    main()
```

---

## Performance Optimization

### Single Analysis
```python
analyzer = TextAnalyzer()  # Initialize once
result = analyzer.analyze(text)  # Reuse for multiple texts
```

### Batch Processing with Caching

```python
from functools import lru_cache
from if_detector import TextAnalyzer

analyzer = TextAnalyzer()

@lru_cache(maxsize=1000)
def cached_analyze(text: str):
    """Cache results for identical texts"""
    return analyzer.analyze(text)

# Process documents efficiently
for doc in documents:
    result = cached_analyze(doc)  # Reuses cached result if duplicate
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
from if_detector import TextAnalyzer

analyzer = TextAnalyzer()

def analyze_batch(texts: list, max_workers: int = 4) -> list:
    """Analyze multiple texts in parallel"""
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(analyzer.analyze, text) for text in texts]
        for future in futures:
            results.append(future.result())

    return results

# Use
texts = [doc1, doc2, doc3, ...]
results = analyze_batch(texts, max_workers=4)
```

---

## Error Handling

### Comprehensive Error Handling

```python
from if_detector import TextAnalyzer

analyzer = TextAnalyzer()

def safe_analyze(text: str) -> dict:
    """Analyze with comprehensive error handling"""
    try:
        # Validate input
        if not text or not isinstance(text, str):
            return {
                'success': False,
                'error': 'Invalid input: text must be non-empty string'
            }

        if len(text.split()) < 20:
            return {
                'success': False,
                'error': 'Text too short: minimum 20 words required',
                'length': len(text.split())
            }

        # Analyze
        result = analyzer.analyze(text)

        return {
            'success': True,
            'probability': result.overall_ai_probability,
            'verdict': result.verdict.value,
            'confidence': result.confidence.value
        }

    except ValueError as e:
        return {'success': False, 'error': f'Value error: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': f'Unexpected error: {str(e)}'}
```

---

## Deployment Checklist

- [ ] Install dependencies: `pip install nltk`
- [ ] Test with sample texts
- [ ] Run test suite: `python test_if_detector.py`
- [ ] Configure thresholds for your domain
- [ ] Set up logging for results
- [ ] Implement error handling
- [ ] Add rate limiting (if API endpoint)
- [ ] Document thresholds for users
- [ ] Monitor false positive/negative rates
- [ ] Plan for model updates

---

## Troubleshooting

### Issue: NLTK Data Not Downloaded
**Solution:**
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
```

### Issue: Slow First Run
**Expected:** ~1-2 seconds on first initialization (downloads NLTK models)
**Solution:** Initialize once at application startup

### Issue: Out of Memory on Large Texts
**Solution:** Process in chunks:
```python
def analyze_large_text(text: str, chunk_size: int = 5000) -> dict:
    """Analyze large texts by chunks"""
    words = text.split()
    chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    results = [analyzer.analyze(chunk) for chunk in chunks]
    # Average results
    avg_prob = sum(r.overall_ai_probability for r in results) / len(results)
    return {'probability': avg_prob}
```

### Issue: False Positives on Technical Writing
**Solution:** Adjust threshold or review metric breakdown:
```python
result = analyzer.analyze(text)
if result.overall_ai_probability > 0.65 and result.confidence.value == 'LOW':
    # Low confidence → require manual review
    flag_for_review(text)
```

---

## Metrics & Monitoring

### Key Metrics to Track

```python
def log_detection(result: DetectionResult):
    """Log detection results for monitoring"""
    metrics = {
        'timestamp': result.analysis_timestamp,
        'ai_probability': result.overall_ai_probability,
        'verdict': result.verdict.value,
        'confidence': result.confidence.value,
        'text_length': result.word_count,
        'issues_found': len(result.specific_issues),
        'metrics': {
            name: metric.score
            for name, metric in result.metrics.items()
        }
    }

    # Send to monitoring system
    send_to_monitoring(metrics)

    # Calculate statistics
    if result.overall_ai_probability > 0.75:
        log_high_confidence_ai(result)
    elif result.overall_ai_probability < 0.25:
        log_high_confidence_human(result)
    else:
        log_ambiguous_result(result)
```

---

## Testing Integration

```python
def test_detector_integration():
    """Verify detector works correctly"""
    from if_detector import TextAnalyzer

    analyzer = TextAnalyzer()

    # Test cases
    test_cases = [
        ("human_text", True),    # Should score as human
        ("ai_text", False),      # Should score as AI
    ]

    for text, is_human in test_cases:
        result = analyzer.analyze(text)
        assert (result.overall_ai_probability < 0.5) == is_human
        assert result.overall_ai_probability >= 0.0
        assert result.overall_ai_probability <= 1.0

    print("✓ All tests passed")
```

---

## Support & Resources

- **Full Architecture:** See `IF_DETECTOR_ARCHITECTURE.md`
- **Quick Reference:** See `IF_DETECTOR_QUICK_REFERENCE.md`
- **Test Suite:** See `test_if_detector.py`
- **Source Code:** See `if_detector.py`

---

**Last Updated:** 2025-11-30
**Version:** 1.0
**Status:** Production Ready ✓
