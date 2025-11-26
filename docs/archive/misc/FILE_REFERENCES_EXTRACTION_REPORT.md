# File References Extraction Report

**Generated:** 2025-11-15  
**Source:** Markdown files in InfraFabric documentation  
**Output:** `/home/setup/infrafabric/FILE_REFERENCES_markdown.json`

---

## Summary

### Extraction Statistics
- **Total References Found:** 1,924
- **Unique Referenced Files:** 373
- **Markdown Files Scanned:** 49+ files
- **Directories Scanned:**
  - `/home/setup/infrafabric/`
  - `/home/setup/infrafabric-core/`

### Reference Types Distribution
- **Relative Path References:** 362 (18.8%)
- **Absolute `/home/setup/` paths:** 80 (4.2%)
- **Windows `/mnt/c/` paths:** 42 (2.2%)
- **URLs/External references:** ~1,440 (74.8%)

---

## Top 30 Most Referenced Files

| Rank | File Reference | Mentions | Files Referenced In |
|------|-----------------|----------|---------------------|
| 1 | IF-vision.md | 239 | 11 |
| 2 | IF-foundations.md | 160 | 16 |
| 3 | IF-witness.md | 139 | 13 |
| 4 | IF_CONVERSATIONS/gpt5-marl-claude-swears-nov7-2025.md | 82 | 10 |
| 5 | annexes/infrafabric-IF-annexes.md | 72 | 6 |
| 6 | IF-armour.md | 69 | 15 |
| 7 | IF_MASTER_TIMELINE_RAW.csv | 62 | 8 |
| 8 | IF_CONVERSATIONS/seeking-confirmation-oct16-2025_29abca1b.json | 42 | 8 |
| 9 | README.md | 40 | 11 |
| 10 | Next.js | 38 | 10 |
| 11 | papers/IF-witness.tex | 23 | 6 |
| 12 | processwire-api.ts | 20 | 8 |
| 13 | philosophy/IF.philosophy-database.yaml | 20 | 4 |
| 14 | docs/evidence/infrafabric_metrics.json | 20 | 4 |
| 15 | merge_evaluations.py | 18 | 5 |
| 16 | IF_TIMELINE_YOLOGUARD_PROGRESSION.json | 18 | 4 |
| 17 | IF.philosophy-database.yaml | 16 | 9 |
| 18 | yolo_guard.py | 16 | 4 |
| 19 | annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md | 15 | 4 |
| 20 | papers/IF-foundations.tex | 13 | 6 |
| 21 | INFRAFABRIC_CONSENSUS_REPORT.md | 12 | 4 |
| 22 | IF-vision.tex | 12 | 4 |
| 23 | claude-code-bridge.zip | 12 | 6 |
| 24 | bridge_cli.py | 12 | 4 |
| 25 | IF_TIMELINE_SWARM_METHODOLOGY.json | 12 | 4 |
| 26 | IF_TIMELINE_BRIDGE_EVOLUTION.json | 12 | 4 |
| 27 | INFRAFABRIC_EVAL_PASTE_PROMPT.txt | 12 | 3 |
| 28 | CLAUDE.md | 11 | 9 |
| 29 | ANNEX-P-GPT5-REFLEXION-CYCLE.md | 11 | 7 |
| 30 | tools/citation_validate.py | 10 | 2 |

---

## Key Reference Categories

### Core Philosophy Documents
- **IF-vision.md:** 239 mentions (most referenced)
- **IF-foundations.md:** 160 mentions
- **IF-witness.md:** 139 mentions
- **IF-armour.md:** 69 mentions

### Conversation Archives
- **IF_CONVERSATIONS/gpt5-marl-claude-swears-nov7-2025.md:** 82 mentions
  - Primary source for MARL execution and GPT-5 reflexion cycle
- **IF_CONVERSATIONS/seeking-confirmation-oct16-2025_29abca1b.json:** 42 mentions
  - Philosophical precursor conversation (Oct 16, 2025)

### Infrastructure & Tools
- **merge_evaluations.py:** 18 mentions (evaluation consensus merger)
- **tools/citation_validate.py:** 10 mentions (citation validation)
- **yolo_guard.py:** 16 mentions (security guardrails)
- **bridge_cli.py:** 12 mentions (CLI interface)

### Data & Configuration
- **IF_MASTER_TIMELINE_RAW.csv:** 62 mentions
- **philosophy/IF.philosophy-database.yaml:** 20 mentions
- **docs/evidence/infrafabric_metrics.json:** 20 mentions

### Annexes & Supporting Documents
- **annexes/infrafabric-IF-annexes.md:** 72 mentions
- **annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md:** 15 mentions
- **ANNEX-P-GPT5-REFLEXION-CYCLE.md:** 11 mentions

---

## Most Referenced By Source Document

### Top 5 Source Files with Most Internal References

1. **philosophy/IF.philosophy-database.md** - 48 total references
   - IF-foundations.md (34x)
   - IF-armour.md (9x)

2. **philosophy/IF.philosophy-table.md** - 31 total references
   - IF-foundations.md (21x)
   - IF-armour.md (9x)

3. **annexes/COMPLETE-SOURCE-INDEX.md** - 55 total references
   - Distributed across 49 unique target files
   - Heavy use of `/home/setup/` and `/mnt/c/` absolute paths

4. **README.md** - 25 total references
   - IF-foundations.md (15x)
   - IF-armour.md (5x)

5. **papers/ARXIV-SUBMISSION-README.md** - 15 total references
   - IF-foundations.tex (3x)
   - Multiple Windows path references

---

## Missing/Unverified References

### References to Non-Existent Files
The following files are referenced but may not exist in the repository:
- `IF-OPTIMISE-ASSERTION-VERIFICATION.md` (3 references)
- `IF-OPTIMISE-DEFAULT-SWARM-POLICY.md` (3 references)
- `IF-OPTIMISE-VEHICLE-METAPHOR.md` (3 references)
- `CONSOLIDATION-DEBATE-EXTENDED-COUNCIL.md` (2+ references)

### Windows Path References (Not in Git)
Multiple references to Windows Downloads folder paths:
- `/mnt/c/Users/Setup/Downloads/claude-code-bridge.zip` (12 references)
- `/mnt/c/users/setup/Downloads/infrafabric/papers/` (3 references)
- `/mnt/c/Users/Setup/Downloads/drive-download-*.zip` (multiple)

These are external artifacts not tracked in the repository.

---

## Cross-Linking Patterns

### Dense Internal Linking
- **IF-foundations.md ↔ IF-armour.md:** Heavy bidirectional references
- **philosophy/* → IF-*.md:** Strong back-references to core documents
- **COMPLETE-SOURCE-INDEX.md:** Acts as central directory to external paths

### External Dependencies
- **NaviDocs:** Referenced in agents.md, SESSION-RESUME.md
- **StackCP:** Referenced in deployment documentation
- **arXiv:** Referenced for research paper submissions

---

## Data Quality Notes

### High Confidence References
- Core MD documents (IF-*.md)
- Local Python scripts (merge_evaluations.py, tools/citation_validate.py)
- YAML configuration files (philosophy-database.yaml)

### Lower Confidence References
- Windows paths (/mnt/c/...) - external to repository
- URLs in shield.io badges - infrastructure references
- Code file paths in example contexts - may be pseudocode

---

## Recommendations

1. **Audit Missing References:**
   - Verify status of IF-OPTIMISE-* files
   - Check CONSOLIDATION-DEBATE-EXTENDED-COUNCIL.md location

2. **Normalize Path References:**
   - Use consistent relative paths in documentation
   - Document external artifact locations in COMPLETE-SOURCE-INDEX.md

3. **Update Link Targets:**
   - Review 373 unique referenced files
   - Create cross-reference index for high-traffic files (IF-vision.md, IF-foundations.md)

4. **Archive Windows Paths:**
   - Consolidate /mnt/c/ references into single inventory
   - Document which artifacts are critical vs. archive-only

---

## JSON Output Format

**File:** `/home/setup/infrafabric/FILE_REFERENCES_markdown.json`

```json
{
  "scan_date": "2025-11-15",
  "source_type": "markdown",
  "directories_scanned": [...],
  "total_references": 1924,
  "unique_referenced_files": 373,
  "references": [
    {
      "referenced_file": "...",
      "found_in": "...",
      "line_number": ...,
      "context": "..."
    }
  ],
  "most_referenced_files": [...]
}
```

**Size:** 133 KB | **Lines:** 3,163

---

## Methodology

1. Scanned all .md files in both directories
2. Used multi-pattern regex to identify file references:
   - Absolute paths: `/home/setup/...`, `/mnt/c/...`
   - Relative paths: `docs/file.ext`, `annexes/ANNEX-*.md`
   - Backtick references: `` `tools/script.py` ``
3. Extracted line context for manual verification
4. Deduplicated entries while preserving location information
5. Grouped and ranked by mention frequency

