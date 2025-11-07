# IF.yologuard v3.0 Philosophical Implementation - Test Runners

## Overview

Two test runners have been created for the IF.yologuard v3.0 philosophical secret detector:

1. **`run_leaky_repo_v3_philosophical.py`** - Full philosophical analysis (COMPREHENSIVE)
2. **`run_leaky_repo_v3_philosophical_fast.py`** - Pattern-only quick benchmark (FAST)

## Files Created

- `/home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks/run_leaky_repo_v3_philosophical.py` (13 KB, executable)
- `/home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks/run_leaky_repo_v3_philosophical_fast.py` (7.6 KB, executable)

## Test Runner 1: Full Philosophical Analysis (COMPREHENSIVE)

### Usage
```bash
python3 run_leaky_repo_v3_philosophical.py
```

### Features

- **Imports**: `SecretRedactorV3` from `/home/setup/work/mcp-multiagent-bridge/IF.yologuard_v3.py`
- **Scanning**: All 49 files in leaky-repo (89 total files, excluding .git and .leaky-meta)
- **Ground Truth**: 96 RISK secrets across 49 files
- **Detection Methods**:
  - Pattern matching (58 patterns from v2+)
  - High-entropy token detection
  - Base64 decoding and rescanning
  - Hex decoding and rescanning
  - JSON value extraction and rescanning
  - XML value extraction and rescanning
  - Confucian relationship mapping (Wu Lun framework)

### Philosophical Modes Tracked

Detections are classified by philosophical framework:

1. **Aristotelian**: Essence classification (intrinsic pattern characteristics)
2. **Kantian**: Duty-based detection (categorical imperatives, cryptographic duties)
3. **Confucian**: Relationship mapping (Wu Lun - Five Relationships)
   - 君臣 (ruler-subject): cert-authority trust chains
   - 父子 (father-son): token-session temporal relationships
   - 夫婦 (husband-wife): key-endpoint complementary pairs
   - 朋友 (friends): user-password symmetrical pairs
4. **Nagarjuna**: Interdependency detection (causal chains, hashes)

### Output

**Console Report**:
- Scan statistics (files, timing)
- Detection performance (v1 vs v2 vs v3)
- Percentage breakdown by philosophical mode
- Top detected patterns
- Top 20 file detections
- Missed ground truth files

**Results File**: `leaky_repo_v3_philosophical_results.txt`

### Performance Metrics

- **v1 baseline**: 30/96 (31.2%)
- **v2 baseline**: ~74/96 (77.0%)
- **v3 target**: 85-90/96 (88-94%)

### Example Report Format

```
IF.yologuard v3.0 - PHILOSOPHICAL SECRET DETECTOR - Leaky Repo Benchmark
Ground truth: 96 RISK secrets
v1 baseline:  30/96  (31.2%)
v2 baseline:  ~74/96 (77.0%)
v3 target:    85-90/96 (88-94%)

DETECTION BY PHILOSOPHICAL MODE
  Confucian (user-password relationship)    XX detections (XX.X%)
  Aristotelian (essence)                    XX detections (XX.X%)
  Kantian (duty)                            XX detections (XX.X%)
  Nagarjuna (interdependent)                XX detections (XX.X%)

TOP DETECTED PATTERNS
  PASSWORD_REDACTED                         XX (XX.X%)
  JWT_REDACTED                              XX (XX.X%)
  BCRYPT_HASH_REDACTED                      XX (XX.X%)
  ...

TOP 20 FILE DETECTIONS
✓ .bash_profile                            | GT: 6 | Detected: 6
✓ web/var/www/public_html/wp-config.php   | GT: 9 | Detected: 8
✓ db/dump.sql                              | GT:10 | Detected: 9
...
```

**Execution Time**: 120-180 seconds (comprehensive entropy + decoding analysis)

---

## Test Runner 2: Fast Pattern-Only Benchmark (FAST)

### Usage
```bash
python3 run_leaky_repo_v3_philosophical_fast.py
```

### Features

- **Fast Mode**: Pattern matching only (no entropy analysis or decoding)
- **Focus**: Quick feedback during development
- **Scanning**: All 49 files in leaky-repo
- **Detection Method**: 58 regex patterns from v3

### Output

**Console Report**:
- Same structure as full version but pattern-only results
- Scan time ~30-45 seconds

**Results File**: `leaky_repo_v3_fast_results.txt`

### When to Use

- **Fast**: During development iteration and quick benchmarking
- **Full**: When evaluating final performance and philosophical classification

---

## Key Implementation Details

### PhilosophicalDetectionTracker Class

Tracks all detections with the following attributes:

```python
class PhilosophicalDetectionTracker:
    def __init__(self):
        self.total_detected = 0
        self.files_with_detections = 0
        self.detections_by_file = defaultdict(list)
        self.detections_by_pattern = defaultdict(int)
        self.detections_by_philosophy = defaultdict(int)  # NEW: Philosophical classification
        self.matched_ground_truth = set()
        self.missed_ground_truth = set()

    def classify_pattern_to_philosophy(self, pattern_name: str) -> str:
        """Map detection pattern to philosophical mode."""

    def add_detection(self, file_path: str, pattern: str, match_text: str, line: int):
        """Record detection with philosophical classification."""

    def calculate_metrics(self):
        """Return recall, precision, and coverage metrics."""
```

### Pattern to Philosophy Mapping

```python
PATTERN_TO_PHILOSOPHY = {
    'AWS_KEY': 'Aristotelian (essence)',
    'PASSWORD': 'Confucian (user-password relationship)',
    'JWT': 'Confucian (token-session relationship)',
    'API_KEY': 'Confucian (key-endpoint relationship)',
    'BCRYPT_HASH': 'Nagarjuna (interdependent)',
    'PRIVATE_KEY': 'Kantian (duty)',
    # ... 20+ patterns mapped
}
```

---

## Running the Tests

### Quick Test (Fast Mode)
```bash
cd /home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks
python3 run_leaky_repo_v3_philosophical_fast.py
```
**Time**: ~30-45 seconds

### Full Test (Comprehensive)
```bash
cd /home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks
python3 run_leaky_repo_v3_philosophical.py
```
**Time**: ~120-180 seconds

### With Timeout (if test takes too long)
```bash
timeout 300 python3 run_leaky_repo_v3_philosophical_fast.py
```

---

## v3 Implementation Features

The test runners validate these v3 philosophical features:

1. **Entropy Detection**: Shannon entropy analysis for high-entropy tokens
2. **Decoding Pipeline**: Base64 → Hex → Rescan for encoded secrets
3. **Format Parsing**: JSON/XML value extraction with contextual priority
4. **Confucian Relationships**: Wu Lun mapping for secret pairs and chains
5. **Relationship Scoring**: Weighted confidence based on connection depth

---

## Expected Results vs Baselines

| Metric | v1 | v2 | v3 Target |
|--------|----|----|-----------|
| Recall | 30/96 (31.2%) | ~74/96 (77%) | 85-90/96 (88-94%) |
| Method | Pattern-only | Pattern + entropy/decode | + Philosophical classification |
| Files Detected | ~30 | ~45 | ~48 |
| Precision | Low | Medium | High |

### Ground Truth Distribution

- **Highest concentration**: SQL dumps (10), WordPress configs (9), Firefox logins (8)
- **Pattern diversity**: 35+ different secret types across 49 files
- **Encoding types**: Plain text, Base64, hex, JSON structures, XML attributes

---

## Troubleshooting

### Test hangs or times out
- Use the **fast version** instead: `run_leaky_repo_v3_philosophical_fast.py`
- Run with explicit timeout: `timeout 300 python3 run_leaky_repo_v3_philosophical.py`

### ImportError on IF.yologuard_v3
- Verify v3 file exists: `/home/setup/work/mcp-multiagent-bridge/IF.yologuard_v3.py`
- Check Python path configuration in test runner

### Low detection rates
- Ensure leaky-repo files are readable: `ls /home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks/leaky-repo/`
- Check file encoding (test handles UTF-8 errors gracefully)

---

## File Structure

```
/home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks/
├── run_leaky_repo_v3_philosophical.py          (full version - 13 KB)
├── run_leaky_repo_v3_philosophical_fast.py     (fast version - 7.6 KB)
├── leaky_repo_v3_philosophical_results.txt     (output - full)
├── leaky_repo_v3_fast_results.txt              (output - fast)
├── run_leaky_repo_v2_fast.py                   (v2 baseline for comparison)
└── leaky-repo/                                 (89 files, 96 secrets)
```

---

## Next Steps

1. **Run fast test**: `python3 run_leaky_repo_v3_philosophical_fast.py`
2. **Review results**: Compare v3 vs v2 recall percentages
3. **Run full test** (optional): For philosophical mode breakdown
4. **Analyze gaps**: Check missed ground truth files for pattern improvements

---

## Related Files

- **Detector**: `/home/setup/work/mcp-multiagent-bridge/IF.yologuard_v3.py`
- **v2 Baseline**: `/home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks/run_leaky_repo_v2_fast.py`
- **Ground Truth**: Embedded in test runners (96 secrets across 49 files)
