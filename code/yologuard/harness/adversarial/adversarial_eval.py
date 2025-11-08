#!/usr/bin/env python3
"""
Adversarial evaluator: creates temp files for each case and runs the yologuard CLI
to assert policy (currently: no ERROR severity in CI profile for doc-like content).
"""
import argparse, json, tempfile, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CLI = ROOT / 'code' / 'yologuard' / 'src' / 'IF.yologuard_v3.py'
CASES = ROOT / 'code' / 'yologuard' / 'harness' / 'adversarial' / 'adversarial_cases.jsonl'

def run_case(case, workdir: Path):
    f = workdir / f"{case['id']}.txt"
    f.write_text(case['content'])
    out_json = workdir / f"{case['id']}.json"
    profile = case.get('profile','ci')
    cmd = ['python3', str(CLI), '--scan', str(f), '--profile', profile, '--json', str(out_json)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    detections = []
    try:
        if out_json.exists():
            detections = json.load(open(out_json))
    except Exception:
        detections = []
    max_sev = 'NOTE'
    order = {'NOTE':0,'WARNING':1,'ERROR':2}
    for d in detections:
        sev = d.get('severity','NOTE')
        if order.get(sev,0) > order.get(max_sev,0):
            max_sev = sev
    ok = True
    if case.get('policy') == 'no_error':
        ok = (max_sev != 'ERROR')
    return {
        'id': case['id'],
        'detections': len(detections),
        'max_severity': max_sev,
        'pass': ok,
        'stdout': proc.stdout[-400:]
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', help='Write JSON summary report')
    ap.add_argument('--md', help='Write Markdown summary report')
    args = ap.parse_args()
    cases = [json.loads(l) for l in open(CASES)]
    results = []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for c in cases:
            results.append(run_case(c, td))
    passed = sum(1 for r in results if r['pass'])
    summary = {
        'total': len(results),
        'passed': passed,
        'failed': len(results)-passed,
        'results': results,
    }
    print(json.dumps(summary, indent=2))
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.json,'w') as f:
            json.dump(summary,f,indent=2)
    if args.md:
        Path(args.md).parent.mkdir(parents=True, exist_ok=True)
        with open(args.md,'w') as f:
            f.write(f"# Adversarial Evaluation\n\nPassed {passed}/{len(results)} cases\n\n")
            f.write('| id | dets | max_severity | pass |\n|----|------|--------------|------|\n')
            for r in results:
                f.write(f"| {r['id']} | {r['detections']} | {r['max_severity']} | {r['pass']} |\n")

if __name__ == '__main__':
    main()
