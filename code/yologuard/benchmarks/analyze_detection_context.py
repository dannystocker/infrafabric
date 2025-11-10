#!/usr/bin/env python3
"""
Analyze WHERE extra detections occur: code vs comments vs docs
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "yologuard_v3",
    str(Path(__file__).resolve().parents[1] / 'src' / 'IF.yologuard_v3.py')
)
yologuard_v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yologuard_v3)
SecretRedactorV3 = yologuard_v3.SecretRedactorV3

LEAKY_REPO_PATH = Path(__file__).resolve().parent / 'leaky-repo'
GROUND_TRUTH = {
    '.bash_profile': 6, 'cloud/.credentials': 2, '.esmtprc': 2,
    '.remote-sync.json': 1, '.vscode/sftp.json': 1, 'cloud/heroku.json': 1,
    'config': 1, 'db/dbeaver-data-sources.xml': 1, 'deployment-config.json': 3,
    'etc/shadow': 1, 'filezilla/recentservers.xml': 3, 'sftp-config.json': 1,
}

redactor = SecretRedactorV3()

# Files with discrepancies
discrepancy_files = [
    '.bash_profile', 'cloud/.credentials', '.esmtprc', '.remote-sync.json',
    '.vscode/sftp.json', 'cloud/heroku.json', 'config', 'db/dbeaver-data-sources.xml',
    'deployment-config.json', 'etc/shadow', 'filezilla/recentservers.xml', 'sftp-config.json'
]

print("=" * 100)
print("CONTEXT ANALYSIS: Where are extra detections found?")
print("=" * 100)
print()

for file in discrepancy_files:
    file_path = LEAKY_REPO_PATH / file
    if not file_path.exists():
        continue

    expected = GROUND_TRUTH.get(file, 0)
    secrets = redactor.scan_file(file_path)
    detected = len(secrets)

    if detected <= expected:
        continue

    print(f"\n📁 {file}")
    print(f"   Expected: {expected}, Detected: {detected} (+{detected - expected})")
    print()

    # Read file to show context
    try:
        lines = file_path.read_text(encoding='utf-8', errors='ignore').split('\n')
    except:
        continue

    for secret in secrets:
        line_num = secret['line']
        if line_num > 0 and line_num <= len(lines):
            line_content = lines[line_num - 1]

            # Check if in comment or documentation
            is_comment = False
            is_xml_comment = False
            context_type = "CODE"

            # Check for comments
            if '#' in line_content:
                comment_pos = line_content.find('#')
                secret_pos = line_content.find(secret['match'][:20])
                if secret_pos > comment_pos:
                    is_comment = True
                    context_type = "COMMENT"

            # Check for XML comments
            if '<!--' in line_content or line_content.strip().startswith('//'):
                is_xml_comment = True
                context_type = "COMMENT"

            # Check for documentation markers
            if any(marker in line_content.lower() for marker in ['example', 'sample', 'test', 'dummy', 'todo', 'fixme']):
                context_type = "DOC/EXAMPLE"

            marker = "💬" if is_comment else ("📝" if context_type == "DOC/EXAMPLE" else "🔑")

            print(f"   {marker} Line {line_num:3d} [{context_type:12s}]: {secret['pattern']:<30}")
            print(f"      Content: {line_content.strip()[:90]}")

print()
print("=" * 100)
print("LEGEND:")
print("  🔑 CODE         - Detection in actual code/config (REAL SECRET)")
print("  💬 COMMENT      - Detection in comment (POSSIBLE FALSE POSITIVE)")
print("  📝 DOC/EXAMPLE  - Detection in example/documentation (POSSIBLE FALSE POSITIVE)")
print("=" * 100)
