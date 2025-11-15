# InfraFabric File Reconciliation Report

**Date Generated:** 2025-11-15
**Repository:** InfraFabric (https://github.com/dannystocker/infrafabric)
**Scan Scope:** `/home/setup/infrafabric` and `/home/setup/infrafabric-core`

---

## Executive Summary

This comprehensive file reconciliation report identifies discrepancies between actual files in the InfraFabric project and documented references. The analysis reveals critical gaps in documentation, orphaned assets, and missing external resources.

| Metric | Count |
|--------|-------|
| Total Files Found | 82 |
| Total Files Referenced in Docs | 105 |
| Orphaned Files (exist, not documented) | 78 |
| Missing Files (documented, don't exist) | 101 |
| Files Not on GitHub | 13 |
| Git-Tracked Files | 48 |
| Untracked Files | 13 |

**Reconciliation Status:** 80% of actual files are undocumented; 96% of referenced files are missing or external.

---

## Section 1: Orphaned Files (Exist but Undocumented)

These files exist in the repository but are not referenced in any documentation. Many represent recent outputs that require integration into the project metadata.

### Category: Configuration Files (2 files)
- `.env` (608 bytes) - Environment variables, untracked
- `.gitignore` (127 bytes) - Git exclusion rules

**Recommendation:** Document environment setup requirements in README. Add `.env` to .gitignore or document required variables in SETUP.md.

### Category: Core Documentation Files (10 files)

| File | Size | Status | Priority |
|------|------|--------|----------|
| IF-vision.md | 34.3 KB | Git-tracked | HIGH |
| IF-witness.md | 41.2 KB | Git-tracked | HIGH |
| README.md | 23.4 KB | Git-tracked | MEDIUM |
| INFRAFABRIC-COMPLETE-DOSSIER-v11.md | 73.2 KB | Git-tracked | HIGH |
| SESSION-RESUME.md | 5.6 KB | Untracked | MEDIUM |
| agents.md | 11.2 KB | Git-tracked | MEDIUM |
| IF_COMPONENT_INVENTORY.yaml | 3.5 KB | Untracked | LOW |
| EVALUATION_PROGRESS.md | 9.4 KB | Untracked | MEDIUM |
| DEBUG_SESSION_PROMPT_GPT-5.1-CODEX-CLI_20251115T145456Z.md | 3.7 KB | Untracked | LOW |
| INFRAFABRIC_EVAL_GPT-5.1-CODEX-CLI_20251115T145456Z.yaml | 11.9 KB | Untracked | MEDIUM |

**Recommendation:** Add cross-references in main README.md to link to these key documents. Create INDEX.md mapping all major files.

### Category: Evaluation & Analysis Files (18 files)

Located in `/docs/evidence/`, these files contain evaluation metrics, reports, and configuration templates:

**Critical Documentation Files:**
- EVALUATION_FILES_SUMMARY.md (6.4 KB)
- EVALUATION_QUICKSTART.md (5.0 KB)
- EVALUATION_WORKFLOW_README.md (6.7 KB)
- INFRAFABRIC_COMPREHENSIVE_EVALUATION_PROMPT.md (18.3 KB)
- INFRAFABRIC_CONSENSUS_REPORT.md (5.3 KB)
- INFRAFABRIC_EVAL_REPORT.md (2.6 KB)

**Metrics & Data Files:**
- infrafabric_metrics.json (279 bytes)
- infrafabric_file_inventory.csv (1.3 KB)
- infrafabric_url_manifest.csv (16.0 KB)

**Evaluation Artifacts:**
- INFRAFABRIC_EVAL_GPT-5.1-CODEX-CLI_20251115T133400Z.yaml (17.9 KB)
- INFRAFABRIC_EVAL_GPT-5.1-CODEX-CLI_20251115T145456Z.yaml (11.9 KB)
- INFRAFABRIC_SINGLE_EVAL.yaml (12.6 KB)
- infrafabric_eval_Gemini_20251115_103000.yaml (5.9 KB)
- INFRAFABRIC_EVAL_PASTE_PROMPT.txt (11.6 KB)

**Recommendation:** Create `/docs/evidence/README.md` explaining evaluation methodology and file purposes. Add index to main README pointing to evaluation documentation.

### Category: Scientific Papers (11 files)

**LaTeX Source Files (.tex format):**
- IF-armour.tex (69.5 KB)
- IF-foundations.tex (127.7 KB)
- IF-vision.tex (46.8 KB)
- IF-witness.tex (53.8 KB)

**ArXiv Submission Packages (.tar.gz):**
- IF-armour-arxiv-submission.tar.gz (21.7 KB)
- IF-foundations-arxiv-submission.tar.gz (43.5 KB)
- IF-vision-arxiv-submission.tar.gz (16.0 KB)
- IF-witness-arxiv-submission.tar.gz (17.7 KB)

**Paper Documentation:**
- ARXIV-SUBMISSION-README.md (29.9 KB)

**Recommendation:** Add papers/README.md documenting LaTeX build process, submission status, and publication timeline. Link from main README.

### Category: Philosophy Database (4 files)

- IF.philosophy-database.md (38.3 KB)
- IF.philosophy-database.yaml (44.5 KB)
- IF.philosophy-queries.md (43.8 KB)
- IF.philosophy-table.md (33.0 KB)

**Recommendation:** Create philosophy/README.md explaining database structure and query interface. Add to main documentation index.

### Category: Code & Tools (3 files)

- IF.yologuard_v3.py (27.6 KB) - Primary security tool
- merge_evaluations.py (14.9 KB) - Evaluation merge utility

**Recommendation:** Document code module purposes, dependencies, and usage. Create code/README.md with examples.

### Category: Benchmark & Report Files (32 files)

Located in `/code/yologuard/reports/`, containing:
- Multiple head2head comparison reports (JSON + Markdown)
- Benchmark results (.json, .log, .out, .sarif formats)
- Performance evaluations (corpus_eval, crossfile_requests, threshold_sweep)
- Adversarial testing results (20251108T111315Z/)

**Recommendation:** Create unified benchmark reporting system. Document performance metrics and comparison methodology. Archive old reports to separate directory.

### Category: Annexes & Supplementary Material (7 files)

- ANNEX-N-IF-OPTIMISE-FRAMEWORK.md (17.8 KB)
- ANNEX-O-PRECURSOR-CONVERSATION.md (17.0 KB)
- ANNEX-P-GPT5-REFLEXION-CYCLE.md (16.9 KB)
- COMPLETE-SOURCE-INDEX.md (27.3 KB)
- ENGINEERING-BACKLOG-GPT5-IMPROVEMENTS.md (28.5 KB)
- infrafabric-IF-annexes.md (170.8 KB) - Master annex file

**Recommendation:** Link all annexes from main INFRAFABRIC-COMPLETE-DOSSIER-v11.md. Ensure annex index reflects all supplementary material.

---

## Section 2: Missing Files (Documented but Don't Exist)

These files are referenced in documentation but are absent from the repository. Some are external references (GitHub, websites) while others represent broken dependencies.

### Category: Configuration Files (3 files)
**Priority: HIGH**

| File | Referenced In | Issue | Fix |
|------|---|---|---|
| `.env.local` | IF-armour.md:617 | Example config not provided | Create SETUP.md with .env.local template |
| `.pre-commit-config.yaml` | COMPLETE-SOURCE-INDEX.md:135 | Build system config missing | Add pre-commit configuration to repo |
| tools/.env | Multiple references | Tool environment vars not documented | Document in code/README.md |

### Category: Internal Project References (8 files)
**Priority: MEDIUM**

These files should exist locally but are missing:
- `/home/setup/infrafabric-core/tools/schema_validator.py`
- `/home/setup/infrafabric-core/tools/citation_validate.py`
- `/home/setup/infrafabric-core/schemas/citation/v1.0.schema.json`
- `/home/setup/infrafabric-core/docs/IF-URI-SCHEME.md`
- `/home/setup/infrafabric-core/docs/SWARM-COMMUNICATION-SECURITY.md`
- `/home/setup/infrafabric/tools/*` (multiple tool files referenced)

**Recommendation:** Create missing tool files or update documentation to reflect actual project structure.

### Category: Claude Project Files (3 files)
**Priority: LOW**

Local to Claude Code environment:
- `~/.claude/history.jsonl` - Session history
- `~/.claude/projects/-home-setup/[UUID].jsonl` - Project metadata

**Recommendation:** Document in development setup guide; these are user-environment specific.

### Category: External GitHub References (12+ files)
**Priority: INFORMATIONAL**

These are external references to GitHub URLs and cannot be satisfied locally:
- `//github.com/dannystocker/infrafabric/blob/master/projects/yologuard/versions/IF.yologuard_v1.py`
- `//github.com/dannystocker/infrafabric/blob/master/projects/yologuard/versions/IF.yologuard_v3.py`
- Various GitHub issue and PR references

**Recommendation:** Update documentation to use consistent URL formats (remove leading slashes). Add git commit hashes instead of branch references for permanence.

### Category: External Service References (6+ files)
**Priority: INFORMATIONAL**

External websites and APIs:
- `//digital-lab.ca/navidocs/builder/NAVIDOCS_FEATURE_CATALOGUE.md`
- `//img.sh` (image hosting service)
- `//arxiv.org/` (academic paper hosting)

**Recommendation:** Document all external dependencies in DEPENDENCIES.md. Add fallback references or local copies where appropriate.

### Category: iCantwait.ca Integration Files (5+ files)
**Priority: MEDIUM**

References to the live deployment environment:
- `/home/setup/icw-nextspread/` related files
- StackCP deployment configuration
- ProcessWire integration files

**Recommendation:** Create ICW-DEPLOYMENT.md documenting integration points and deployment procedures.

---

## Section 3: GitHub Sync Issues

### Untracked Files (13 files not in git)
**Priority: HIGH - Requires immediate attention**

These files exist locally but are not tracked by git:

```
?? .env
?? .venv_tools/                          (entire venv directory - add to .gitignore)
?? DEBUG_SESSION_PROMPT_GPT-5.1-CODEX-CLI_20251115T145456Z.md
?? EVALUATION_PROGRESS.md
?? FILE_INVENTORY_infrafabric-core.json  (analysis artifact)
?? FILE_INVENTORY_infrafabric.json       (analysis artifact)
?? FILE_REFERENCES_markdown.json         (analysis artifact)
?? FILE_REFERENCES_yaml_json.json        (analysis artifact)
?? IF_COMPONENT_INVENTORY.yaml
?? INFRAFABRIC_EVAL_GPT-5.1-CODEX-CLI_20251115T145456Z.yaml
?? code/                                 (yologuard benchmark reports - large)
?? docs/evidence/INFRAFABRIC_EVALUATION_REPORT.html
?? infrafabric_eval_Gemini_20251115_103000.yaml
```

### Recommended Git Commands

**Step 1: Review untracked files**
```bash
cd /home/setup/infrafabric
git status --short | grep '^??'
```

**Step 2: Update .gitignore**
```bash
cat >> .gitignore << 'EOF'
.venv_tools/
*.env.local
FILE_INVENTORY_*.json
FILE_REFERENCES_*.json
FILE_ANALYSIS_*.json
FILE_RECONCILIATION_*.md
FILE_RECONCILIATION_*.json
infrafabric_eval_*.yaml
code/yologuard/reports/
EOF
```

**Step 3: Add important documentation files**
```bash
git add DEBUG_SESSION_PROMPT_GPT-5.1-CODEX-CLI_*.md \
         EVALUATION_PROGRESS.md \
         IF_COMPONENT_INVENTORY.yaml \
         INFRAFABRIC_EVAL_GPT-5.1-CODEX-CLI_*.yaml
```

**Step 4: Commit changes**
```bash
git commit -m "Add evaluation documentation and component inventory

- Add debug session prompts for transparency
- Add evaluation progress tracking
- Add component inventory YAML for system analysis
- Update .gitignore to exclude analysis artifacts and environment files"
```

**Step 5: Verify git state**
```bash
git log --oneline -5
git status
git ls-files | wc -l
```

---

## Section 4: Comprehensive Recommendations

### Immediate Actions (P0 - This Week)

1. **Create SETUP.md** (Estimated: 1 hour)
   - Document development environment setup
   - List required tools and dependencies (.venv_tools, Python packages)
   - Provide .env template and variable explanations
   - Include git configuration for local vs. GitHub remotes

2. **Update .gitignore** (Estimated: 30 minutes)
   - Add .venv_tools/ directory
   - Exclude analysis artifacts (FILE_INVENTORY_*.json, etc.)
   - Exclude temporary evaluation files
   - Update tracking status of evaluation YAML files

3. **Create docs/evidence/README.md** (Estimated: 1 hour)
   - Explain evaluation methodology
   - Document metrics schema
   - List evaluation tools and versions tested
   - Provide quick-start for running evaluations

4. **Commit untracked documentation files** (Estimated: 30 minutes)
   - Create commit with untracked files that provide value
   - Exclude analysis/build artifacts
   - Update repository remote if still pointing to ds-infrafabric2

### Short-term Improvements (P1 - This Month)

5. **Create CODE_STRUCTURE.md** (Estimated: 2 hours)
   - Document tools/ directory purpose and usage
   - Provide yologuard installation and usage guide
   - Document code modules and dependencies
   - Add development workflow guidelines

6. **Create papers/README.md** (Estimated: 1.5 hours)
   - Document LaTeX source format and build process
   - List publication status for each paper
   - Provide submission timeline
   - Link to arXiv versions

7. **Create philosophy/README.md** (Estimated: 1 hour)
   - Explain philosophy database schema
   - Document query interface
   - Provide usage examples
   - List all 21 philosophers and their contributions

8. **Create comprehensive FILE_INDEX.md** (Estimated: 2 hours)
   - Map all 82 files with descriptions
   - Show file dependencies and relationships
   - Indicate version/status of critical files
   - Link to relevant documentation

9. **Resolve missing tool files** (Estimated: 3-4 hours)
   - Implement `/tools/citation_validate.py`
   - Implement `/tools/schema_validator.py`
   - Create `/schemas/citation/v1.0.schema.json`
   - Document citation generation workflow

### Medium-term Improvements (P2 - Next Quarter)

10. **Create DEPLOYMENT.md** (Estimated: 2 hours)
    - Document iCantwait.ca integration
    - Provide StackCP deployment procedures
    - List ProcessWire API endpoints
    - Document sync procedures with remote servers

11. **Create ARCHITECTURE.md** (Estimated: 3 hours)
    - Document system-wide design decisions
    - Map component relationships
    - Explain IF.* naming convention and taxonomy
    - Provide high-level overview of all subsystems

12. **Consolidate evaluation metrics** (Estimated: 4 hours)
    - Merge multiple YAML evaluation files into unified schema
    - Create evaluation results database
    - Document performance baselines
    - Establish tracking mechanism for ongoing tests

---

## Section 5: File Organization Summary

### By Category
- **Core Documentation:** 10 files (well organized)
- **Scientific Papers:** 11 files (well organized in papers/)
- **Philosophy Database:** 4 files (well organized in philosophy/)
- **Evaluation & Analysis:** 18 files (could use consolidation)
- **Code & Tools:** 3 main files + reports (needs documentation)
- **Configuration:** 2 files (scattered, needs organization)
- **Benchmark Reports:** 32 files (scattered, should be archived)
- **Annexes:** 7 files (well organized in annexes/)
- **Build Artifacts:** 13 files (untracked, should be in .gitignore)

### Size Distribution
- **Total Size:** ~1.6 MB
- **Largest Files:** infrafabric-IF-annexes.md (170.8 KB), IF-foundations.tex (127.7 KB)
- **Benchmarks/Reports:** ~500 KB combined
- **Evaluation Artifacts:** ~150 KB combined

### Git Status
- **Tracked:** 48 files (58.5%)
- **Untracked:** 13 files (15.9%) - mostly recent evaluations
- **Excluded by .gitignore:** .venv_tools/, __pycache__/

---

## Validation Checklist

Use this checklist to verify reconciliation completion:

- [ ] All orphaned files documented in appropriate README files
- [ ] Missing configuration files created with templates
- [ ] Missing tool files implemented or documented as not-needed
- [ ] .gitignore updated to properly exclude build artifacts
- [ ] Untracked documentation files committed to git
- [ ] FILE_INDEX.md created and maintained
- [ ] All README files in major directories (docs/, papers/, philosophy/, code/)
- [ ] External references cleaned up (consistent URL format)
- [ ] Git remote verified (pointing to GitHub, not ds-infrafabric2)
- [ ] File reconciliation report reviewed and approved

---

## Appendix: File Statistics

### Extension Breakdown
```
.md (Markdown)     : 35 files | 594.7 KB | Primary documentation
.yaml (Config)     :  9 files |  60.3 KB | Configuration and data
.py (Python)       :  2 files |  42.4 KB | Tools and utilities
.json (JSON)       : 14 files | 148.3 KB | Data and metrics
.tex (LaTeX)       :  4 files | 298.2 KB | Scientific papers
.gz (Gzip)         :  4 files |  98.8 KB | Compressed archives
.log (Logs)        :  2 files |   6.8 KB | Execution logs
.out (Output)      :  5 files |   3.8 KB | Test output
.csv (CSV)         :  2 files |  17.3 KB | Data exports
.sarif (SARIF)     :  1 file  |  65.5 KB | Security scan results
.html (HTML)       :  1 file  |  42.7 KB | Generated reports
.txt (Text)        :  1 file  |  11.6 KB | Text configuration
None (Config)      :  2 files |   0.7 KB | Dotfiles
```

### Directory Structure Depth
- Root level: 16 files
- Depth 1 (annexes/, code/, docs/, papers/, philosophy/): 5 directories
- Depth 2 (yologuard/reports/, evidence/): 2 directories
- Depth 3 (reports/[timestamps]/): Multiple benchmark output directories

---

**Report Generated:** 2025-11-15 17:30 UTC
**Analysis Tool:** InfraFabric File Reconciliation System v1.0
**Next Review:** 2025-11-22 (Weekly)
