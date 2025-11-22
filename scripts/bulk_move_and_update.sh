#!/usr/bin/env bash
set -euo pipefail

mapping_file=${1:-out/moves.csv}
root=$(git rev-parse --show-toplevel)
cd "$root"

if [[ ! -f "$mapping_file" ]]; then
  echo "Mapping file not found: $mapping_file"
  exit 1
fi

while IFS=, read -r old_path new_path; do
  [[ -z "$old_path" || -z "$new_path" ]] && continue
  old_trimmed=$(echo "$old_path" | sed -e 's/^\s*//;s/\s*$//')
  new_trimmed=$(echo "$new_path" | sed -e 's/^\s*//;s/\s*$//')
  [[ -z "$old_trimmed" || -z "$new_trimmed" ]] && continue
  if [[ "${old_trimmed,,}" == "old_path" && "${new_trimmed,,}" == "new_path" ]]; then
    continue
  fi
  if [[ ! -e "$old_trimmed" ]]; then
    echo "Source missing: $old_trimmed"
    exit 1
  fi
  mkdir -p "$(dirname "$new_trimmed")"
  git mv -f -- "$old_trimmed" "$new_trimmed"
done < "$mapping_file"

python3 scripts/update_links.py --mapping "$mapping_file" --dry-run
python3 scripts/update_links.py --mapping "$mapping_file"

python3 - <<'PY'
import pathlib, re
pattern = re.compile(r"\[.*?\]\((?!https?://)([^)]+)\)")
errors = []
for path in pathlib.Path(".").rglob("*.md"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    for match in pattern.finditer(text):
        link = match.group(1).strip()
        if not link or link.startswith("#") or link.startswith("mailto:"):
            continue
        target = (path.parent / link).resolve()
        if target.name and not target.exists():
            errors.append((path, link))
if errors:
    for md, link in errors:
        print(f"Broken link in {md}: {link}")
    raise SystemExit("Markdown link check failed.")
print("Markdown link check passed.")
PY

for target in scripts code tools; do
  if [[ -d "$target" ]]; then
    python3 -m compileall "$target"
  fi
done

git add -A
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  git commit -m "infra: structural reorg"
fi
