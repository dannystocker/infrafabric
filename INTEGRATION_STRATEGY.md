# InfraFabric Integration Strategy
## Merging Found Files Based on Timestamps

### Philosophy: Preserve History, Promote Latest

**Rule:** Keep newest by modification date, archive older versions with timestamps

---

## Phase 1: Timestamp Analysis (COMPLETED)

All files have been catalogued with modification dates in:
- `FILE_SCAN_windows_downloads.json`
- `FILE_SCAN_windows_documents.json`
- `FILE_SCAN_home_root.json`
- `CONSOLIDATION_FILE_LIST.json` (with SHA256 hashes)

---

## Phase 2: Integration Rules

### A. Python Tools (.py files)
**Rule:** Newest wins, older versions go to `tools/archive/YYYYMMDD/`

**Example:**
```bash
# yolo_guard.py found in 3 locations:
# - /downloads/yolo_guard.py (2025-11-14)
# - /downloads/claude-bridge/yolo_guard.py (2025-11-08)
# - /home/setup/yolo_guard.py (2025-10-15)

# Action:
cp /downloads/yolo_guard.py /home/setup/infrafabric/tools/yolo_guard.py
mkdir -p /home/setup/infrafabric/tools/archive/20251108
cp /downloads/claude-bridge/yolo_guard.py /home/setup/infrafabric/tools/archive/20251108/yolo_guard.py
mkdir -p /home/setup/infrafabric/tools/archive/20251015
cp /home/setup/yolo_guard.py /home/setup/infrafabric/tools/archive/20251015/yolo_guard.py
```

### B. Philosophy Database (.yaml files)
**Rule:** Semantic versioning wins (v1.1 > v1.0), archive by date

**Already Done:**
- ✅ v1.1 in `philosophy/v1.1/IF.philosophy-database-v1.1-joe-coulombe.yaml` (2025-11-14)
- ✅ v1.0 in `philosophy/IF.philosophy-database.yaml` (2025-11-14)
- ✅ Personas in `philosophy/` (2025-11-11 to 2025-11-14)

### C. Documentation (.md files)
**Rule:** Diff-based merge - if content differs, keep both with version notes

**Example:**
```bash
# IF.yologuard-COMPLETE-DOCUMENTATION.md found in 6 locations
# Check if they're identical (SHA256):
# - 5 are identical (delete duplicates)
# - 1 differs (older draft from 2025-11-06)

# Action:
# Keep newest in /docs/
# Archive older variant with date: /docs/archive/20251106/IF.yologuard-COMPLETE-DOCUMENTATION.md
```

### D. Evaluation Results (.yaml, .json)
**Rule:** Keep ALL versions by date in `evaluations/YYYY-MM-DD/`

**Example:**
```bash
mkdir -p /home/setup/infrafabric/evaluations/2025-11-15
cp /downloads/INFRAFABRIC_EVAL_*.yaml /home/setup/infrafabric/evaluations/2025-11-15/
```

---

## Phase 3: Smart Integration Script

### Automated Integration Logic
