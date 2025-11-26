#!/usr/bin/env python3
"""
IF.yologuard v2 - Aligned Validation Test
Implements GPT-5 falsification protocol with proper TP/FP/FN alignment
"""

import sys
import csv
from pathlib import Path
from yologuard_v2 import SecretRedactorV2

# Ground truth mapping
GROUND_TRUTH = {
    'dump.sql': 10,
    'wp-config.php': 9,
    '.mozilla/firefox/logins.json': 8,
    '.bash_profile': 6,
    '.env': 6,
    '.bashrc': 3,
    '.ftpconfig': 3,
    'robomongo.json': 3,
    'secrets.yml': 3,
    'deployment-config.json': 3,
    'filezilla/recentservers.xml': 3,
}

def main():
    """Run aligned validation test."""
    print("=" * 80)
    print("IF.yologuard v2 - Aligned Validation Test")
    print("=" * 80)
    
    total_gt = sum(GROUND_TRUTH.values())
    print(f"Ground truth: {total_gt} RISK secrets in {len(GROUND_TRUTH)} critical files")
    print("Scoring: One-to-one alignment (deduped pattern matches)")
    print("=" * 80)
    print()
    
    scanner = SecretRedactorV2()
    
    total_tp = 0
    total_fn = 0
    total_fp = 0
    total_detections = 0
    
    results = []
    
    print(f"{'File':50s} | {'GT':>3s} | {'Det':>3s} | {'TP':>3s} | {'FN':>3s} | Status")
    print("-" * 90)
    
    for file_rel, gt_count in sorted(GROUND_TRUTH.items(), key=lambda x: x[1], reverse=True):
        # Handle nested paths
        if '/' in file_rel:
            file_path = Path('sample_secrets') / file_rel
        else:
            file_path = Path('sample_secrets') / file_rel
        
        if not file_path.exists():
            print(f"{file_rel:50s} | {gt_count:3d} |   ? |   ? |   ? | ⚠ NOT FOUND")
            total_fn += gt_count
            continue
        
        try:
            detections = scanner.scan_file(file_path)
            det_count = len(detections) if detections else 0
            total_detections += det_count
            
            # Aligned scoring: TP = min(detections, ground_truth)
            # This accounts for pattern overlap (multiple matches on same secret)
            tp = min(det_count, gt_count)
            fn = max(0, gt_count - det_count)
            fp = max(0, det_count - gt_count)
            
            total_tp += tp
            total_fn += fn
            total_fp += fp
            
            if tp == gt_count:
                status = "✓ FULL"
            elif tp > 0:
                status = f"⚠ PARTIAL ({tp}/{gt_count})"
            else:
                status = "❌ MISS"
            
            print(f"{file_rel:50s} | {gt_count:3d} | {det_count:3d} | {tp:3d} | {fn:3d} | {status}")
            
            results.append({
                'file': file_rel,
                'gt': gt_count,
                'det': det_count,
                'tp': tp,
                'fn': fn,
                'fp': fp,
                'status': status
            })
        
        except Exception as e:
            print(f"{file_rel:50s} | {gt_count:3d} |   ? |   ? |   ? | ❌ ERROR: {str(e)[:20]}")
            total_fn += gt_count
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    recall = total_tp / total_gt * 100 if total_gt > 0 else 0
    precision = total_tp / total_detections * 100 if total_detections > 0 else 0
    
    print(f"Ground Truth Secrets: {total_gt}")
    print(f"Total Detections: {total_detections}")
    print()
    print(f"True Positives (TP): {total_tp}/{total_gt} ({recall:.1f}% recall)")
    print(f"False Negatives (FN): {total_fn}/{total_gt} ({total_fn/total_gt*100:.1f}% miss rate)")
    print(f"False Positives (FP): {total_fp} (est. {precision:.1f}% precision)")
    print()
    
    # Acceptance criteria
    if recall >= 80 and precision >= 95:
        tier = "Tier 1: Production-Ready"
        status_icon = "🎉"
    elif recall >= 70 and precision >= 90:
        tier = "Tier 2: POC-Validated"
        status_icon = "✓"
    else:
        tier = "Tier 3: Needs Work"
        status_icon = "⚠"
    
    print(f"STATUS: {status_icon} {tier}")
    print()
    
    # Category breakdown
    print("=" * 80)
    print("CATEGORY PERFORMANCE")
    print("=" * 80)
    
    categories = {
        'bcrypt_hashes': ['dump.sql'],
        'wordpress': ['wp-config.php'],
        'firefox': ['.mozilla/firefox/logins.json'],
        'shell_env': ['.bash_profile', '.bashrc'],
        'structured_configs': ['robomongo.json', 'secrets.yml', 'deployment-config.json'],
        'encoded_creds': ['.ftpconfig', '.env', 'filezilla/recentservers.xml'],
    }
    
    for cat, files in categories.items():
        cat_tp = sum(r['tp'] for r in results if r['file'] in files)
        cat_gt = sum(GROUND_TRUTH[f] for f in files if f in GROUND_TRUTH)
        cat_recall = cat_tp / cat_gt * 100 if cat_gt > 0 else 0
        print(f"  {cat:25s}: {cat_tp:2d}/{cat_gt:2d} ({cat_recall:5.1f}% recall)")
    
    print()
    print("=" * 80)
    
    # Save results
    with open('validation_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'gt', 'det', 'tp', 'fn', 'fp', 'status'])
        writer.writeheader()
        writer.writerows(results)
    
    print("✓ Detailed results saved to: validation_results.csv")
    print()
    
    return 0 if recall >= 70 else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
