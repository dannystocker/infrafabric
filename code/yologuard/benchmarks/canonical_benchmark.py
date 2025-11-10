#!/usr/bin/env python3
# Copyright (c) 2025 Danny Stocker
# SPDX-License-Identifier: MIT
#
# InfraFabric - IF.armour.yologuard Canonical Benchmark
# Source: https://github.com/dannystocker/infrafabric
# Licensed under the MIT License. See LICENSE-CODE file in the project root.

"""
IF.armour.yologuard Canonical Benchmark - Leaky Repo Ground Truth

PURPOSE:
    Reproducible benchmark for external validation of yologuard secret detection.

METHODOLOGY:
    - Tests against Leaky Repo corpus (github.com/Plazmaz/leaky-repo)
    - Ground truth: 96 RISK-category secrets (excludes 79 INFORMATIVE metadata)
    - "usable-only" standard = RISK category only (passwords, keys, tokens)
    - INFORMATIVE category (usernames, hostnames, URLs) excluded by design

RATIONALE FOR "USABLE-ONLY" (RISK-only):
    - RISK secrets are directly exploitable (passwords, API keys, private keys)
    - INFORMATIVE data provides context but isn't directly exploitable
    - Security tools should focus on actual exploit risk, not metadata
    - Aligns with Leaky Repo's own categorization schema

TRANSPARENCY:
    - Full corpus has 175 total items (96 RISK + 79 INFORMATIVE)
    - This benchmark tests RISK-only by design, not by accident
    - Corpus filtering criteria fully documented in this file
    - Alternative metrics (full 175) can be computed if needed

IF.TTT COMPLIANCE:
    - Traceable: Git commit hash, file hashes, timestamps included
    - Transparent: Methodology documented, corpus filtering explained
    - Trustworthy: Reproducible on any machine, falsifiable predictions

Created: 2025-11-10
Updated: 2025-11-10
Citation: if://benchmark/yologuard-canonical-leaky-repo-2025-11-10
"""

import sys
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Import yologuard v3 using relative path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "yologuard_v3",
    str(Path(__file__).resolve().parents[1] / 'src' / 'IF.yologuard_v3.py')
)
yologuard_v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yologuard_v3)
SecretRedactorV3 = yologuard_v3.SecretRedactorV3

# Benchmark configuration
BENCHMARK_DIR = Path(__file__).resolve().parent
LEAKY_REPO_PATH = BENCHMARK_DIR / 'leaky-repo'
EXCLUDE_DIRS = {'.git', '.leaky-meta'}

# Ground truth: 96 RISK-category secrets from Leaky Repo
# Source: leaky-repo/.leaky-meta/secrets.csv (num_risk column)
# These are the "usable-only" secrets (directly exploitable credentials)
GROUND_TRUTH_RISK = {
    '.bash_profile': 6,
    '.bashrc': 3,
    '.docker/.dockercfg': 2,
    '.docker/config.json': 2,
    '.mozilla/firefox/logins.json': 8,
    '.ssh/id_rsa': 1,
    'cloud/.credentials': 2,
    'cloud/.s3cfg': 1,
    'cloud/.tugboat': 1,
    'cloud/heroku.json': 1,
    'db/dump.sql': 10,
    'db/mongoid.yml': 1,
    'etc/shadow': 1,
    'filezilla/recentservers.xml': 3,
    'filezilla/filezilla.xml': 2,
    'misc-keys/cert-key.pem': 1,
    'misc-keys/putty-example.ppk': 1,
    'proftpdpasswd': 1,
    'web/ruby/config/master.key': 1,
    'web/ruby/secrets.yml': 3,
    'web/var/www/.env': 6,
    '.npmrc': 2,
    'web/var/www/public_html/wp-config.php': 9,
    'web/var/www/public_html/.htpasswd': 1,
    '.git-credentials': 1,
    'db/robomongo.json': 3,
    'web/js/salesforce.js': 1,
    '.netrc': 2,
    'hub': 1,
    'config': 1,
    'db/.pgpass': 1,
    'ventrilo_srv.ini': 2,
    'web/var/www/public_html/config.php': 1,
    'db/dbeaver-data-sources.xml': 1,
    '.esmtprc': 2,
    'web/django/settings.py': 1,
    'deployment-config.json': 3,
    '.ftpconfig': 3,
    '.remote-sync.json': 1,
    '.vscode/sftp.json': 1,
    'sftp-config.json': 1,
    '.idea/WebServers.xml': 1,
}

# INFORMATIVE-category items (79 total) - NOT included in standard metric
# These are usernames, hostnames, URLs, timestamps - useful context but not exploitable
# If you want to test against full corpus (175 = 96 + 79), set INCLUDE_INFORMATIVE = True
GROUND_TRUTH_INFORMATIVE = {
    '.bash_profile': 5,
    '.bashrc': 3,
    '.docker/.dockercfg': 2,
    '.docker/config.json': 2,
    '.mozilla/firefox/logins.json': 20,  # hostnames, timeCreated, etc.
    '.ssh/id_rsa.pub': 1,
    'cloud/.credentials': 2,
    'cloud/.s3cfg': 2,
    'cloud/.tugboat': 2,
    'cloud/heroku.json': 1,
    'filezilla/recentservers.xml': 3,
    'filezilla/filezilla.xml': 1,
    'high-entropy-misc.txt': 2,
    'misc-keys/putty-example.ppk': 1,
    'web/var/www/.env': 4,
    '.npmrc': 1,
    'web/var/www/public_html/wp-config.php': 3,
    'db/robomongo.json': 4,  # hostnames, usernames
    'hub': 1,
    'config': 3,
    'web/var/www/public_html/config.php': 3,
    '.esmtprc': 1,
    'deployment-config.json': 1,
    '.ftpconfig': 2,
    '.remote-sync.json': 2,
    '.vscode/sftp.json': 3,
    'sftp-config.json': 3,
    '.idea/WebServers.xml': 1,
}

# Configuration flag: Set to True to test against full corpus (175 secrets)
INCLUDE_INFORMATIVE = False


def get_git_commit() -> str:
    """Get current git commit hash for traceability."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=BENCHMARK_DIR.parent.parent,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return "unknown"


def get_file_hash(path: Path) -> str:
    """Calculate SHA-256 hash of file for IF.TTT traceability."""
    sha256 = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except:
        return "error"


def scan_corpus(redactor: SecretRedactorV3) -> Dict:
    """
    Scan Leaky Repo corpus and return detection results.

    Returns:
        Dictionary with file-level detection counts and metadata
    """
    results = {}
    total_files_scanned = 0
    total_files_with_secrets = 0

    # Select ground truth based on configuration
    ground_truth = GROUND_TRUTH_RISK.copy()
    if INCLUDE_INFORMATIVE:
        # Merge RISK + INFORMATIVE for full corpus testing
        for file, count in GROUND_TRUTH_INFORMATIVE.items():
            ground_truth[file] = ground_truth.get(file, 0) + count

    # Scan all files in corpus
    for file_path in LEAKY_REPO_PATH.rglob('*'):
        # Skip directories and excluded dirs
        if file_path.is_dir():
            continue
        if any(exc in file_path.parts for exc in EXCLUDE_DIRS):
            continue

        total_files_scanned += 1

        # Get relative path for ground truth lookup
        rel_path = str(file_path.relative_to(LEAKY_REPO_PATH))

        # Scan file for secrets
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Use yologuard's internal scanning method
            matches = redactor.predecode_and_rescan(content)
            num_detected = len(matches)

            if num_detected > 0:
                total_files_with_secrets += 1
                results[rel_path] = {
                    'detected': num_detected,
                    'expected': ground_truth.get(rel_path, 0),
                    'in_ground_truth': rel_path in ground_truth,
                    'file_hash': get_file_hash(file_path),
                }
        except Exception as e:
            # Record scan errors for transparency
            results[rel_path] = {
                'detected': 0,
                'expected': ground_truth.get(rel_path, 0),
                'in_ground_truth': rel_path in ground_truth,
                'error': str(e),
            }

    return {
        'file_results': results,
        'total_files_scanned': total_files_scanned,
        'total_files_with_secrets': total_files_with_secrets,
        'ground_truth': ground_truth,
    }


def calculate_metrics(scan_results: Dict) -> Dict:
    """
    Calculate recall, precision, and F1 metrics.

    Metrics:
        - Recall: What % of ground truth secrets were detected?
        - Precision: What % of detections were real secrets?
        - F1: Harmonic mean of precision and recall
    """
    file_results = scan_results['file_results']
    ground_truth = scan_results['ground_truth']

    # Count detections
    total_detected = sum(r['detected'] for r in file_results.values())
    total_expected = sum(ground_truth.values())

    # True positives: Secrets detected that are in ground truth
    # (simplified: assumes detections in GT files are all TPs)
    true_positives = 0
    false_positives = 0

    for file, result in file_results.items():
        detected = result['detected']
        expected = result['expected']

        if file in ground_truth:
            # Detections in ground truth files
            tp = min(detected, expected)  # Can't detect more TPs than exist
            fp = max(0, detected - expected)  # Excess detections are FPs
            true_positives += tp
            false_positives += fp
        else:
            # Any detection in non-GT file is a false positive
            false_positives += detected

    # False negatives: Ground truth secrets NOT detected
    false_negatives = total_expected - true_positives

    # Calculate metrics
    recall = true_positives / total_expected if total_expected > 0 else 0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # File-level coverage
    files_detected = sum(1 for r in file_results.values() if r['detected'] > 0 and r['in_ground_truth'])
    files_expected = len(ground_truth)
    file_coverage = files_detected / files_expected if files_expected > 0 else 0

    return {
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'total_expected': total_expected,
        'total_detected': total_detected,
        'recall': recall,
        'precision': precision,
        'f1_score': f1,
        'file_coverage': file_coverage,
        'files_detected': files_detected,
        'files_expected': files_expected,
    }


def generate_report(scan_results: Dict, metrics: Dict, output_format: str = 'markdown') -> str:
    """Generate IF.TTT-compliant report."""

    # Get traceability metadata
    git_commit = get_git_commit()
    timestamp = datetime.utcnow().isoformat() + 'Z'
    corpus_type = "RISK + INFORMATIVE (175)" if INCLUDE_INFORMATIVE else "RISK-only (96)"

    if output_format == 'json':
        return json.dumps({
            'benchmark_metadata': {
                'name': 'IF.armour.yologuard Canonical Benchmark',
                'version': '1.0',
                'timestamp': timestamp,
                'git_commit': git_commit,
                'corpus': 'Leaky Repo',
                'corpus_type': corpus_type,
                'ground_truth_size': metrics['total_expected'],
                'citation': 'if://benchmark/yologuard-canonical-leaky-repo-2025-11-10',
            },
            'metrics': {
                'recall': round(metrics['recall'], 4),
                'precision': round(metrics['precision'], 4),
                'f1_score': round(metrics['f1_score'], 4),
                'file_coverage': round(metrics['file_coverage'], 4),
                'true_positives': metrics['true_positives'],
                'false_positives': metrics['false_positives'],
                'false_negatives': metrics['false_negatives'],
            },
            'file_results': scan_results['file_results'],
        }, indent=2)

    # Markdown report
    report = f"""# IF.armour.yologuard Canonical Benchmark Results

## IF.TTT Traceability Metadata

**Benchmark:** IF.armour.yologuard Canonical Benchmark v1.0
**Timestamp:** {timestamp}
**Git Commit:** {git_commit}
**Corpus:** Leaky Repo (github.com/Plazmaz/leaky-repo)
**Corpus Type:** {corpus_type}
**Ground Truth Size:** {metrics['total_expected']} secrets
**Citation:** if://benchmark/yologuard-canonical-leaky-repo-2025-11-10

---

## Methodology

**"Usable-Only" Standard:** Testing against RISK-category secrets only

- **RISK secrets (96):** Passwords, API keys, private keys, auth tokens (directly exploitable)
- **INFORMATIVE data (79):** Usernames, hostnames, URLs, timestamps (excluded by design)
- **Total corpus:** 175 items (96 RISK + 79 INFORMATIVE)

**Rationale:** Security tools should focus on actual exploit risk, not metadata. Leaky Repo's own categorization distinguishes "risk" from "informative" for this reason.

---

## Metrics (Primary)

| Metric | Value | Formula |
|--------|-------|---------|
| **Recall** | **{metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)** | TP / (TP + FN) = {metrics['true_positives']} / {metrics['total_expected']} |
| **Precision** | **{metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)** | TP / (TP + FP) = {metrics['true_positives']} / ({metrics['true_positives']} + {metrics['false_positives']}) |
| **F1 Score** | **{metrics['f1_score']:.4f}** | 2 × (P × R) / (P + R) |

## Coverage

| Metric | Value |
|--------|-------|
| True Positives | {metrics['true_positives']} secrets |
| False Positives | {metrics['false_positives']} secrets |
| False Negatives | {metrics['false_negatives']} secrets |
| File Coverage | {metrics['file_coverage']:.2%} ({metrics['files_detected']}/{metrics['files_expected']} files) |
| Total Files Scanned | {scan_results['total_files_scanned']} |

---

## Reproducibility

To reproduce this benchmark on any machine:

```bash
cd /path/to/infrafabric/code/yologuard/benchmarks
python canonical_benchmark.py

# For JSON output:
python canonical_benchmark.py --json > results.json
```

**Requirements:**
- Python 3.8+
- IF.yologuard_v3.py in ../src/
- Leaky Repo corpus in ./leaky-repo/

---

## File-Level Results

Files detected: {metrics['files_detected']}/{metrics['files_expected']}

"""

    # Add file-by-file breakdown
    for file, result in sorted(scan_results['file_results'].items()):
        if result['in_ground_truth'] and result['detected'] > 0:
            status = "✅" if result['detected'] >= result['expected'] else "⚠️"
            report += f"{status} `{file}`: {result['detected']}/{result['expected']} detected\n"

    report += "\n---\n\n**IF.TTT Compliance:** ✅ Traceable, Transparent, Trustworthy\n"

    return report


def main():
    """Run canonical benchmark."""
    import argparse

    parser = argparse.ArgumentParser(description='IF.armour.yologuard Canonical Benchmark')
    parser.add_argument('--json', action='store_true', help='Output JSON instead of markdown')
    parser.add_argument('--include-informative', action='store_true', help='Test against full corpus (175 = 96 RISK + 79 INFORMATIVE)')
    args = parser.parse_args()

    global INCLUDE_INFORMATIVE
    if args.include_informative:
        INCLUDE_INFORMATIVE = True

    # Verify corpus exists
    if not LEAKY_REPO_PATH.exists():
        print(f"ERROR: Leaky Repo corpus not found at {LEAKY_REPO_PATH}", file=sys.stderr)
        print("Expected location: code/yologuard/benchmarks/leaky-repo/", file=sys.stderr)
        sys.exit(1)

    # Initialize yologuard
    print("Initializing IF.armour.yologuard v3...", file=sys.stderr)
    redactor = SecretRedactorV3()

    # Run benchmark
    print(f"Scanning Leaky Repo corpus ({LEAKY_REPO_PATH})...", file=sys.stderr)
    scan_results = scan_corpus(redactor)

    # Calculate metrics
    print("Calculating metrics...", file=sys.stderr)
    metrics = calculate_metrics(scan_results)

    # Generate report
    output_format = 'json' if args.json else 'markdown'
    report = generate_report(scan_results, metrics, output_format)

    # Output
    print(report)

    # Exit code: 0 if recall >= 85%, 1 otherwise
    if metrics['recall'] >= 0.85:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
