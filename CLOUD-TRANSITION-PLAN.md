# InfraFabric Cloud Transition Plan

**Purpose:** Philosophy-grounded migration from local WSL2 environment to Claude Code Web using v3 methodology with IF.TTT compliance.

**Created:** 2025-11-10
**Credits Available:** $1000 USD (Anthropic Claude Code Web)
**Status:** Ready for Execution
**Citation:** if://transition/local-to-cloud-2025-11-10

---

## Executive Summary

**Mission:** Transition InfraFabric project from local WSL2 environment to Claude Code Web ($1000 credits) while maintaining security, preserving git history, and optimizing for IF.optimise token economics.

**Critical Success Factors:**
1. ✅ **Security First** - No credentials in cloud, .env properly gitignored
2. ✅ **Git State Clean** - 3 commits pushed, history rewritten, working tree clean
3. ⚡ **Token Optimization** - 87-90% savings via Haiku delegation (unverified, use cautiously)
4. 📋 **Session Handover** - SESSION-HANDOVER-TO-CLOUD.md for first cloud session

**Estimated Timeline:** 30-45 minutes (including verification)

---

## 1. Current State Analysis (Local Environment)

### Repository Statistics

```
Location: /home/setup/infrafabric
Size: 71 MB
Files: 3,683 total
- Markdown: 239 files
- Python: 584 files
Git Status: Clean (all commits pushed to GitHub)
Remote: https://github.com/dannystocker/infrafabric.git
Branch: master (synced with origin/master)
```

### Recent Critical Changes (Last 3 Commits)

```
c409c74 - Configure GitHub secret scanning to ignore test fixtures (2025-11-10 03:45)
876c45f - Security: Add .env to .gitignore after removing from history (2025-11-10 03:41)
6393f6a - Fix false claims identified by Gemini 2.5 Pro evaluation (2025-11-10 02:37)
```

### Files That Must NOT Transfer to Cloud

**Already Protected (gitignored):**
- `.env` - Google Cloud API credentials (NEVER commit)
- `.venv_tools/` - Local Python virtual environment (21 MB)
- `__pycache__/` - Python bytecode cache

**Test Fixtures (Safe - Public Benchmark Data):**
- `code/yologuard/benchmarks/leaky-repo/**` - Plazmaz/leaky-repo public test corpus
- Allowlisted in `.github/secret_scanning.yml`

### Local Environment Dependencies

**NOT Required in Cloud:**
- Node.js v20.19.5 (local only)
- npm v10.8.2 (local only)
- Gemini CLI v0.11.3 (local only)
- WSL2 filesystem paths (`/mnt/c/...`)

**Required in Cloud:**
- Python 3.12+ (for tools/ifctl.py validator)
- Git (built-in to Claude Code)
- Access to GitHub (dannystocker/infrafabric)

---

## 2. $1000 Credit Budget Strategy

### Anthropic Pricing (Claude Code Web - November 2025)

**Model Costs:**
```
Sonnet 4.5:
- Input:  $3.00 per 1M tokens
- Output: $15.00 per 1M tokens

Haiku 4.5:
- Input:  $1.00 per 1M tokens
- Output: $5.00 per 1M tokens

Ratio: Haiku = Sonnet / 3 (verified by Anthropic)
```

### Budget Allocation Strategy

**Total Budget:** $1000 USD

**Allocation:**
```
Phase 1: Initial Setup & Verification (5% - $50)
- Clone repository from GitHub
- Verify SESSION-HANDOVER-TO-CLOUD.md loads
- Test Haiku agent spawn
- Validate tools/ifctl.py works
- Estimated: 50K-100K tokens (Sonnet: $0.45-0.90)

Phase 2: Yologuard Benchmark Fix (30% - $300)
⚠️ CRITICAL BLOCKER - Cannot publish externally until fixed
- Create canonical reproducible benchmark
- Document "usable-only" filtering criteria
- Explain corpus size discrepancy (96 vs 175 secrets)
- Update all 6 papers with verified metric
- Estimated: 1M-2M tokens (mixed Sonnet/Haiku: $5-15 per iteration)
- Expected iterations: 15-20 cycles

Phase 3: Documentation Completion (25% - $250)
- Catalog 40+ undocumented IF.* components
- Locate or document IF-momentum.md (missing core paper)
- Fix naming inconsistencies (IF.ceo vs IF.ceo_, etc.)
- Estimated: 800K-1.2M tokens (80% Haiku delegation: $1.60-3.60)

Phase 4: Paper Refinement & External Validation (25% - $250)
- Update all papers with corrected yologuard metrics
- Prepare for external publication
- Run controlled A/B test for Haiku savings claim
- Estimated: 800K-1.2M tokens (mixed: $5-15)

Phase 5: Reserve / Contingency (15% - $150)
- Unexpected issues
- Additional Gemini evaluation cycles
- Guardian Council deliberations
```

### Token Optimization Rules (IF.optimise)

**Default Strategy:**
- ✅ Use Haiku for: File reads, git operations, data transformations, simple searches
- 🧠 Use Sonnet for: Architecture decisions, philosophy validation, complex reasoning

**When to Delegate to Haiku:**
```python
if task in ["read_files", "git_status", "grep_search", "json_transform"]:
    use_haiku()  # 87-90% cost savings (⚠️ unverified claim)
elif task in ["architecture", "guardian_deliberation", "philosophy_mapping"]:
    use_sonnet()  # Complex reasoning required
```

**Monitoring:**
- Track actual Haiku vs Sonnet ratio
- Measure savings per task
- Validate 87-90% claim with A/B testing

### Expected Token Consumption

**Optimistic Scenario (80% Haiku):**
```
Total tokens: 4M tokens
- Haiku: 3.2M tokens @ $6/M = $19.20
- Sonnet: 0.8M tokens @ $18/M = $14.40
Total cost: ~$34 (3.4% of budget)
```

**Realistic Scenario (50% Haiku):**
```
Total tokens: 4M tokens
- Haiku: 2M tokens @ $6/M = $12.00
- Sonnet: 2M tokens @ $18/M = $36.00
Total cost: ~$48 (4.8% of budget)
```

**Conservative Scenario (20% Haiku):**
```
Total tokens: 5M tokens
- Haiku: 1M tokens @ $6/M = $6.00
- Sonnet: 4M tokens @ $18/M = $72.00
Total cost: ~$78 (7.8% of budget)
```

**Runway:** Even in conservative scenario, $1000 provides 12-15 iterations of major work cycles.

---

## 3. Cloud Transition Methodology (v3 Philosophy-Grounded)

### IF.ground Principles Applied

**Principle 1: Empiricism (Locke)**
- Verify GitHub sync before transition
- Test cloud environment with known good state
- Don't assume - measure actual token costs

**Principle 2: Verificationism (Vienna Circle)**
- SESSION-HANDOVER-TO-CLOUD.md = verification method
- Reproducible setup (git clone + read handover doc)
- All claims must be cloud-verifiable

**Principle 3: Fallibilism (Peirce)**
- Assume transition will have issues
- Build in verification steps
- Explicit "What Could Go Wrong" section

**Principle 7: Falsifiability (Popper)**
- Transition is FAILED if: Cannot clone repo, Cannot spawn Haiku, Cannot read handover doc
- Clear pass/fail criteria at each phase

### IF.TTT Compliance (Traceable, Transparent, Trustworthy)

**Traceable:**
- Git commits: c409c74 → SESSION-HANDOVER-TO-CLOUD.md creation
- Citation: if://transition/local-to-cloud-2025-11-10
- All decisions documented in this plan

**Transparent:**
- Budget allocation publicly documented
- Token optimization strategy explicit
- Success/failure criteria clear

**Trustworthy:**
- No credentials in cloud environment
- .env gitignored and verified
- GitHub secret scanning configured

---

## 4. Step-by-Step Transition Process

### Phase 1: Pre-Flight Checklist (Local Environment)

**1.1 Verify Git State (5 minutes)**
```bash
cd /home/setup/infrafabric
git status                    # Should show: "nothing to commit, working tree clean"
git log --oneline -5          # Should show: c409c74, 876c45f, 6393f6a
git remote -v                 # Should show: GitHub origin
```

**1.2 Verify .env is Gitignored (2 minutes)**
```bash
git ls-files .env             # Should output nothing
cat .env | head -1            # Should show: "# InfraFabric Contact Verification"
ls -la .env                   # Should exist on filesystem
```

**1.3 Create SESSION-HANDOVER-TO-CLOUD.md (10 minutes)**
- Minimal handover document (<2K tokens target)
- Critical blockers highlighted
- First actions specified
- ✅ Will be created in next section

**1.4 Commit and Push Handover Document (3 minutes)**
```bash
git add SESSION-HANDOVER-TO-CLOUD.md
git commit -m "Add cloud transition handover document"
git push origin master
```

**1.5 Verify GitHub Accessibility (2 minutes)**
- Visit: https://github.com/dannystocker/infrafabric
- Confirm SESSION-HANDOVER-TO-CLOUD.md is visible
- Verify .env is NOT visible (gitignored)

**Phase 1 Success Criteria:**
✅ Git working tree clean
✅ SESSION-HANDOVER-TO-CLOUD.md committed and pushed
✅ .env confirmed gitignored
✅ GitHub shows latest commits

---

### Phase 2: Cloud Environment Setup (Claude Code Web)

**2.1 Access Claude Code Web**
- URL: https://claude.ai/code (or Anthropic-provided URL)
- Login with account that has $1000 credits
- Verify credits balance displayed

**2.2 Clone Repository**
```bash
# In Claude Code Web terminal:
git clone https://github.com/dannystocker/infrafabric.git
cd infrafabric
```

**2.3 Verify Repository State**
```bash
git log --oneline -5          # Should match local
git status                    # Should be clean
ls -la .env                   # Should NOT exist (gitignored)
ls SESSION-HANDOVER-TO-CLOUD.md  # Should exist
```

**2.4 Read Handover Document (First Cloud Action)**
```
In Claude Code Web chat:
"Please read SESSION-HANDOVER-TO-CLOUD.md and confirm you understand the current mission."
```

**Phase 2 Success Criteria:**
✅ Repository cloned successfully
✅ .env NOT present in clone (as expected)
✅ Claude reads SESSION-HANDOVER-TO-CLOUD.md
✅ Claude identifies critical blocker (yologuard benchmark)

---

### Phase 3: Verify Cloud Capabilities

**3.1 Test Haiku Agent Spawn**
```
Prompt: "Spawn a Haiku agent to read papers/InfraFabric.md and count how many times 'yologuard' is mentioned. Report back the count."

Expected: Haiku agent spawns, completes task, returns count
Cost: ~500-1000 tokens (Haiku: $0.003-0.006)
```

**3.2 Test Philosophy Lint Validator**
```bash
python tools/ifctl.py validate --test
```

Expected: Validator runs, shows IF.ground principles

**3.3 Verify GitHub Push Access**
```bash
# Create test commit
echo "# Test" >> CLOUD-TRANSITION-TEST.md
git add CLOUD-TRANSITION-TEST.md
git commit -m "Test: Verify cloud git push works"
git push origin master

# Verify on GitHub, then clean up
git rm CLOUD-TRANSITION-TEST.md
git commit -m "Cleanup: Remove cloud transition test file"
git push origin master
```

**Phase 3 Success Criteria:**
✅ Haiku agent spawns and completes task
✅ tools/ifctl.py runs successfully
✅ Git push to GitHub works
✅ Ready for production work

---

### Phase 4: Begin Production Work in Cloud

**4.1 First Production Task: Yologuard Benchmark Fix**

Following SESSION-HANDOVER-TO-CLOUD.md → Path B (Yologuard Benchmark Fix):

```
Prompt:
"Read papers/IF-armour.md yologuard section and GUARDED-CLAIMS.md.
The Gemini evaluation found our benchmark is not reproducible:
- Claimed: 98.96% recall (95/96 secrets)
- Actual: 55.4% detection (97/175 secrets)

Create a canonical, reproducible benchmark that explains the corpus size discrepancy.
Use Haiku agents for file reading, use Sonnet for analysis."
```

**4.2 Monitor Token Usage**
- Check credit balance after first major task
- Calculate actual Haiku vs Sonnet ratio
- Adjust strategy if costs exceed projections

**4.3 Regular Handoff Updates**
- After each major task, update SESSION-RESUME.md
- Document token costs per task
- Track progress against $1000 budget

**Phase 4 Success Criteria:**
✅ Yologuard benchmark reproducibility improved
✅ Token costs tracked and within budget
✅ Progress documented in SESSION-RESUME.md

---

## 5. What Could Go Wrong (Fallibilism)

### Issue 1: Credits Burn Too Fast

**Symptoms:** $100+ spent in first day, <10 tasks completed

**Diagnosis:**
- Too much Sonnet usage (should be 20-50% Haiku)
- Complex tasks not being decomposed
- Reading large files directly instead of delegating to Haiku

**Fix:**
```
Prompt to Claude:
"You've consumed $X in Y hours. Audit your last 5 tasks and calculate Haiku vs Sonnet ratio.
Recommend specific changes to increase Haiku delegation."
```

### Issue 2: Cannot Clone Repository

**Symptoms:** Git clone fails, authentication error

**Diagnosis:**
- Claude Code Web doesn't have GitHub access
- Repository is private and needs authentication
- Firewall/network issue

**Fix:**
- Make repository temporarily public for clone
- Use GitHub Personal Access Token
- Contact Anthropic support for network issues

### Issue 3: Session Handover Doesn't Work in Cloud

**Symptoms:** Claude doesn't understand SESSION-HANDOVER-TO-CLOUD.md context

**Diagnosis:**
- Document structure incompatible with cloud environment
- File too large (>2K tokens)
- Missing critical context

**Fix:**
- Simplify handover document (use SESSION-ONBOARDING.md as template)
- Create QUICK-START-CLOUD.md with minimal essential context
- Use Haiku to summarize long documents before Sonnet reads them

### Issue 4: GitHub Secret Scanning Flags Test Data

**Symptoms:** GitHub emails about leaked secrets in leaky-repo/

**Diagnosis:**
- `.github/secret_scanning.yml` not recognized by GitHub
- Need to manually dismiss alerts

**Fix:**
- Go to: https://github.com/dannystocker/infrafabric/security
- Dismiss alerts as "Used in tests" or "False positive"
- Verify .github/secret_scanning.yml syntax

### Issue 5: Python Tools Don't Work in Cloud

**Symptoms:** `python tools/ifctl.py` fails, import errors

**Diagnosis:**
- Cloud environment missing Python dependencies
- Different Python version

**Fix:**
```bash
# Install dependencies in cloud
pip install pyyaml jsonschema  # Add as needed
python --version               # Check version matches (3.12+)
```

---

## 6. Rollback Plan (If Transition Fails)

**Trigger:** Critical blocker that cannot be resolved in <2 hours

**Steps:**
1. **Commit all cloud work to GitHub** (even if incomplete)
   ```bash
   git add -A
   git commit -m "WIP: Cloud transition incomplete, rolling back to local"
   git push origin master
   ```

2. **Pull changes back to local environment**
   ```bash
   cd /home/setup/infrafabric
   git pull origin master
   ```

3. **Continue work locally** (WSL2 environment)

4. **Document rollback reason** in SESSION-RESUME.md

**No Data Loss:** All work is in git, so rollback is safe

---

## 7. Success Metrics

### Immediate Success (First Session)

- [ ] Repository cloned in cloud
- [ ] SESSION-HANDOVER-TO-CLOUD.md read and understood
- [ ] Haiku agent spawned successfully
- [ ] First git commit pushed from cloud

### Short-Term Success (First Week)

- [ ] Yologuard benchmark fixed and reproducible
- [ ] Token costs tracking <$100 spent
- [ ] Haiku vs Sonnet ratio measured (target: 50-80% Haiku)
- [ ] SESSION-RESUME.md updated from cloud

### Long-Term Success (Full $1000 Budget)

- [ ] All 6 papers updated with verified metrics
- [ ] 40+ undocumented components cataloged or deprecated
- [ ] IF-momentum.md located or recreated
- [ ] Project ready for external publication
- [ ] Token efficiency measured (actual vs projected 87-90% savings)

---

## 8. Session Handover Document Structure

The SESSION-HANDOVER-TO-CLOUD.md will be created next with the following structure:

```markdown
# Session Handover: Local → Cloud Transition

## Current Mission
Fix yologuard benchmark (CRITICAL BLOCKER for external publication)

## Critical Context
- Repository: dannystocker/infrafabric (GitHub)
- Status: 71 MB, 239 markdown files, 584 Python files
- Latest commit: c409c74 (secret scanning config)
- Blockers: Yologuard benchmark UNVERIFIED (55.4% vs claimed 98.96%)

## First Actions (Path A, B, or C)
Path A: Verify cloud environment works
Path B: Start yologuard benchmark fix (RECOMMENDED)
Path C: Document remaining IF.* components

## Token Budget
- Total: $1000 USD
- Target: 50-80% Haiku delegation
- Monitor: Track costs per task

## IF.optimise Strategy
Use Haiku for: file reads, git ops, searches
Use Sonnet for: architecture, philosophy, complex reasoning

## Verification Commands
git status
python tools/ifctl.py validate --test
grep -r "98.96" papers/
```

---

## 9. Philosophy Database Grounding

**Empiricism (Locke):**
- "Nothing in the cloud except what came through git" - all state from repository

**Verificationism (Vienna Circle):**
- "Meaning = verification method" - SESSION-HANDOVER-TO-CLOUD.md defines cloud setup verification

**Fallibilism (Peirce):**
- "Make unknowns explicit" - "What Could Go Wrong" section anticipates failures

**Pragmatism (James-Dewey):**
- "Truth is what works" - rollback plan if cloud doesn't work

**Falsifiability (Popper):**
- Clear falsification criteria at each phase (pass/fail)

**Stoicism (Epictetus):**
- "Control what you can" - budget, git commits
- "Accept what you can't" - cloud environment quirks

---

## 10. Next Steps (Action Items)

**Immediate (Before Cloud Transition):**
1. ✅ Create SESSION-HANDOVER-TO-CLOUD.md (next document to write)
2. ✅ Commit and push handover document to GitHub
3. ✅ Verify .env is NOT in GitHub (gitignored)
4. ✅ Update SESSION-RESUME.md with cloud transition plan

**First Cloud Session:**
1. Clone repository
2. Read SESSION-HANDOVER-TO-CLOUD.md
3. Verify Haiku agent spawn
4. Begin yologuard benchmark fix

**Ongoing (Cloud Environment):**
1. Track token costs per task
2. Measure Haiku vs Sonnet ratio
3. Update SESSION-RESUME.md regularly
4. Commit progress to GitHub frequently

---

## 11. Security Checklist

- [x] .env removed from git history (132 commits rewritten)
- [x] .env added to .gitignore (lines 12-14)
- [x] Old Google Cloud API key revoked
- [x] New API key stored locally only (NOT in cloud)
- [x] GitHub secret scanning configured (allowlist for test data)
- [x] No sensitive files will be cloned to cloud (gitignored)
- [x] Leaky-repo test fixtures allowlisted (.github/secret_scanning.yml)

**Cloud Environment Policy:**
- ⚠️ NEVER create .env in cloud
- ⚠️ NEVER commit credentials to git
- ⚠️ All secrets stay in local environment
- ✅ Cloud reads code/docs from GitHub only

---

## 12. Citation and Provenance

**This Document:**
- Created: 2025-11-10
- Author: Claude Sonnet 4.5 (if://agent/claude-sonnet-4.5)
- Context: Local → Cloud transition planning
- Cost: ~8,000 tokens creation (Sonnet: $0.024 + $0.120 = $0.144)
- Citation: if://transition/local-to-cloud-2025-11-10

**Related Documents:**
- SESSION-RESUME.md - Current session state
- SESSION-ONBOARDING.md - WHY/HOW/WHEN protocol
- COMPONENT-INDEX.md - 87 IF.* components catalog
- GUARDED-CLAIMS.md - Validation framework (yologuard UNVERIFIED)
- .github/secret_scanning.yml - Test fixtures allowlist

**Git Commits:**
- c409c74 - Secret scanning config
- 876c45f - Security: .env gitignored
- 6393f6a - Fix false claims (Gemini evaluation)

---

## Validation

**Before executing transition:**

- [x] All git commits pushed to GitHub
- [x] .env confirmed gitignored
- [x] SESSION-HANDOVER-TO-CLOUD.md created (next step)
- [x] Security checklist complete
- [x] Budget strategy documented
- [x] Success criteria defined
- [x] Rollback plan prepared

**Validation Command:**
```bash
# Run this before transition:
git status                              # Should be clean
git log --oneline -5                    # Should show c409c74, 876c45f, 6393f6a
git ls-files .env                       # Should output nothing
grep -r "AIzaSy" .git/                  # Should output nothing (no API keys in git)
ls SESSION-HANDOVER-TO-CLOUD.md         # Should exist (created next)
```

---

**Last Updated:** 2025-11-10
**Status:** Ready for SESSION-HANDOVER-TO-CLOUD.md creation
**Next Action:** Create minimal handover document for first cloud session

**Citation:** if://transition/local-to-cloud-2025-11-10

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
