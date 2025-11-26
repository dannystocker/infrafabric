# INFRAFABRIC SERIES 2 - CODEX 5.1 MAX EXEMPLARY REPO AUDIT

**Date:** 2025-11-26
**Target:** OpenAI Codex 5.1 MAX
**Purpose:** Transform InfraFabric into an exemplary GitHub repository
**Mode:** ANALYSIS FIRST - Propose changes before executing

---

## CRITICAL CREDENTIALS & PATHS

### Redis Cloud (Primary State Store)
```
Host: redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com
Port: 19956
Password: zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8
```

**Connection Test:**
```bash
redis-cli -h redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com -p 19956 -a 'zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8' PING
```

### Gitea (Local)
```
URL: http://localhost:4000/
Admin User: ggq-admin
Admin Pass: Admin_GGQ-2025!
User: dannystocker
User Pass: @@Gitea305$$
```

### GitHub
```
Repo: https://github.com/dannystocker/infrafabric
Branch: master
Latest Commit: 7f69ae6 (Series 2 Genesis)
```

### DeepSeek API
```
API Key: sk-c2b06f3ae3c442de82f4e529bcce71ed
```

### Project Paths
```
InfraFabric Main:     /home/setup/infrafabric
InfraFabric Core:     /home/setup/infrafabric-core
NaviDocs:             /home/setup/navidocs
ICW:                  /home/setup/icw-nextspread
Job Hunt:             /home/setup/job-hunt
Windows Downloads:    /mnt/c/users/setup/downloads
Screen Captures:      /mnt/c/users/setup/pictures/screencaptures/
```

---

## MISSION BRIEF

You are **Chief Architect & Quality Auditor** for InfraFabric, a consent-based AI governance framework.

**CURRENT STATE (as of 2025-11-26):**
- Series 2 Genesis committed (7f69ae6)
- 287 files changed, 43,229 additions
- 132 IF protocols documented
- 2,770 lines production code
- 95%+ IF.TTT compliance (up from 78%)
- 621 Redis keys, 0% corruption (down from 43%)
- 36+ dead branches need cleanup

**TARGET STATE:**
An **exemplary open-source repository** suitable for:
1. **Anthropic** - Constitutional AI research partner
2. **Epic Games** - Metaverse agent memory/persistence
3. **Open Source Community** - Framework adoption

---

## PHASE 1: GIT HYGIENE

### Dead Branches (36 total - NOT merged to master)

**Category A: Claude Session Branches (19) - SAFE TO DELETE**
```
claude/cli-witness-optimise-011CV2nzozFeHipmhetrw5nk
claude/cloud-providers-011CV2nnsyHT4by1am1ZrkkA
claude/coordination-011CV2nnsyHT4by1am1ZrkkA
claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
claude/gedimat-cloud-infrastructure-01D9cjQKY1Bu6sccAvi5Unn9
claude/gedimat-logistics-optimization-018FV2Sa5LnT4vDUTq5ipvaX
claude/gedimat-v3-3-deployment-01Pr63R6o2UqQGmxA2VtF12B
claude/h323-guardian-council-011CV2ntGfBNNQYpqiJxaS8B
claude/if-bus-sip-adapters-011CV2yyTqo7mStA7KhuUszV
claude/incomplete-request-011CV24ywdDeCx4vv5gH6e5R
claude/ndi-witness-streaming-011CV2niqJBK5CYADJMRLNGs
claude/payment-billing-011CV2nnsyHT4by1am1ZrkkA
claude/realtime-parallel-sessions-011CV2o8kLhZZEHUtjFZPazM
claude/review-cloud-handover-docs-011CUyURbbbYv3twL6dH4r3v
claude/sip-communication-011CV2nnsyHT4by1am1ZrkkA
claude/sip-escalate-integration-011CV2nwLukS7EtnB5iZUUe7
claude/webrtc-agent-mesh-011CV2nnsyHT4by1am1ZrkkA
claude/webrtc-final-push-011CV2nnsyHT4by1am1ZrkkA
claude/webrtc-phase2-3-011CV2nnsyHT4by1am1ZrkkA
```

**Category B: Swarm Experiment Branches (9) - SAFE TO DELETE**
```
swarm/w2-a5-ifmessage-samples
swarm/w2-a6-checklist
swarm/w2-a6-ci-workflow
swarm/w2-a6-promote-workflow
swarm/w2-a7-governance-docs-clean
swarm/w2-a9-visuals-qa
swarm/w2-citation-schemas
swarm/w2-philosophy-map
```

**Category C: Test/Evaluation Branches (6) - REVIEW FIRST**
```
evaluation-system
fix/review-workflow-yaml
gedimat-evidence-final
gedimat-intelligence-test
gedimat-v2-clean
gedimat-v3-deploy
gedimat-v3-final
test-ci-validation
```

**Category D: Feature Branches (1) - CHECK FOR UNIQUE CODE**
```
yologuard/v3-publish
```

**Category E: STRAY REF - DELETE IMMEDIATELY**
```
origin  (this is a broken local branch, not the remote!)
```

### TASK 1: Branch Audit
For each branch, run:
```bash
git log master..<branch> --oneline | wc -l  # Unique commits
git diff master..<branch> --stat | tail -1  # Files changed
```

### Cleanup Commands (AFTER review):
```bash
# Delete stray "origin" local branch
git branch -d origin

# Delete Claude session branches
git branch -D claude/cli-witness-optimise-011CV2nzozFeHipmhetrw5nk
# ... (repeat for all claude/* branches)

# Delete swarm branches
git branch -D swarm/w2-a5-ifmessage-samples
# ... (repeat for all swarm/* branches)

# Prune remote tracking refs
git remote prune origin

# Push branch deletions to remote
git push origin --delete <branch-name>
```

---

## PHASE 2: IF.PROTOCOL INTEGRITY

### Production Code Map (2,770 lines total)
| Component | Path | Lines | Status |
|-----------|------|-------|--------|
| IF.arbitrate | `src/infrafabric/core/governance/arbitrate.py` | 945 | ACTIVE |
| IF.yologuard | `src/infrafabric/core/security/yologuard.py` | 680 | ACTIVE |
| IF.vesicle | `src/infrafabric/core/transport/vesicle.py` | 672 | ACTIVE |
| IF.librarian | `src/infrafabric/core/services/librarian.py` | 410 | ACTIVE |
| IF.ocr | `src/infrafabric/core/workers/ocr_worker.py` | 63 | STUB |

### Top 10 Protocols by Mention Count
| Protocol | Mentions | Status | Notes |
|----------|----------|--------|-------|
| IF.guard | 9,176 | ACTIVE | Strategic communications council |
| IF.infrafabric | 6,163 | FRAMEWORK | Core namespace |
| IF.yologuard | 3,433 | ACTIVE | Security/immune system |
| IF.optimise | 3,370 | ACTIVE | Token efficiency |
| IF.sam | 2,176 | ACTIVE | 16 facets (8 light + 8 dark) |
| IF.TTT | 2,071 | ACTIVE | Traceable, Transparent, Trustworthy |
| IF.council | 1,933 | ACTIVE | Guardian Council governance |
| IF.vesicle | 1,811 | ACTIVE | Transport layer |
| IF.memory | 1,200 | ACTIVE | Distributed memory |
| IF.synthesis | 1,083 | **GHOST** | Never fully implemented |

### TASK 2: Ghost Protocol Hunt
Find protocols mentioned in docs but missing code:
```bash
grep -r "IF\." docs/ | grep -oE "IF\.[A-Za-z]+" | sort | uniq -c | sort -rn
# Cross-reference with src/ to find ghosts
```

---

## PHASE 3: REDIS STATE VERIFICATION

### Expected State
- **Keys:** 621
- **Corruption:** 0% (cleaned from 43%)
- **Key Prefixes:** context:*, session:*, finding:*, swarm:*

### Verification Commands
```bash
# Total keys
redis-cli -h redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com -p 19956 \
  -a 'zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8' DBSIZE

# Key distribution
redis-cli -h redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com -p 19956 \
  -a 'zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8' KEYS "*" | cut -d: -f1 | sort | uniq -c | sort -rn

# Check for WRONGTYPE errors (corruption indicator)
redis-cli -h redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com -p 19956 \
  -a 'zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8' KEYS "*" | head -50 | while read key; do
  redis-cli -h redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com -p 19956 \
    -a 'zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8' GET "$key" 2>&1 | grep -q WRONGTYPE && echo "CORRUPT: $key"
done
```

---

## PHASE 4: DOCUMENTATION AUDIT

### Key Files to Verify
| File | Purpose | Check |
|------|---------|-------|
| `README.md` | Entry point | Quick start, badges, architecture |
| `agents.md` | Master reference | All 132 protocols, code map |
| `docs/IF_PROTOCOL_REGISTRY.md` | Protocol catalog | Complete list |
| `docs/api/API_ROADMAP.md` | Integration plans | Active/Planned status |
| `MANIFESTO.md` | Constitution | Core principles |

### Link Rot Check
```bash
grep -rohE 'https?://[^ )]+' docs/ papers/ README.md | sort -u | while read url; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
  [ "$status" != "200" ] && echo "BROKEN ($status): $url"
done
```

---

## PHASE 5: EXEMPLARY REPO CHECKLIST

Score each item 0-5:

| Category | Item | Current | Target | Priority |
|----------|------|---------|--------|----------|
| **Discovery** | Clear README with badges | 2 | 5 | P0 |
| **Discovery** | Repo description + topics | 1 | 5 | P0 |
| **Quality** | Passing CI | 3 | 5 | P1 |
| **Quality** | Test coverage >80% | 1 | 5 | P2 |
| **Quality** | No security vulnerabilities | 4 | 5 | P1 |
| **Documentation** | API docs | 3 | 5 | P1 |
| **Documentation** | Architecture diagrams | 2 | 5 | P2 |
| **Documentation** | Contributing guide | 0 | 5 | P1 |
| **Community** | Issue templates | 0 | 5 | P2 |
| **Community** | PR templates | 0 | 5 | P2 |
| **Community** | Code of conduct | 0 | 5 | P2 |
| **Maintenance** | Clean git history | 2 | 5 | P0 |
| **Maintenance** | No dead branches | 0 | 5 | P0 |
| **Maintenance** | Semantic versioning | 1 | 5 | P1 |

**Current Score: ~19/70 (27%)**
**Target Score: 70/70 (100%)**

---

## DELIVERABLES

### 1. BRANCH CLEANUP REPORT
```markdown
## Safe to Delete (32 branches)
- [x] All claude/* branches (19)
- [x] All swarm/* branches (9)
- [x] origin (stray ref)
- [x] test-ci-validation
- [x] fix/review-workflow-yaml
- [x] evaluation-system

## Preserve (cherry-pick unique content)
- [ ] yologuard/v3-publish: Check for v3 code not in master

## Commands to Execute
<provide exact commands>
```

### 2. INTEGRITY REPORT
- Ghost protocols list
- Broken links
- Redis corruption status (expected: 0%)
- Missing documentation

### 3. PRIORITY IMPROVEMENTS
| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| P0 | Delete 32 dead branches | Low | High |
| P0 | Update README with badges | Low | High |
| P1 | Add CONTRIBUTING.md | Medium | High |
| P1 | Implement ghost protocols or mark as CONCEPT | High | Medium |
| P2 | Add issue/PR templates | Low | Medium |
| P2 | Increase test coverage | High | High |

### 4. ACTION PLAN
Ordered list of commands to execute after approval.

---

## CONSTRAINTS

**DO NOT** (without explicit approval):
- Delete any branches
- Modify production code
- Push to remote
- Delete Redis keys

**DO:**
- Read and analyze comprehensively
- Report findings with evidence
- Propose changes with justification
- Calculate overall "repo quality score"

---

## SUCCESS CRITERIA

This audit produces:
1. A clear picture of repository health
2. A prioritized roadmap to "exemplary" status
3. Evidence-based recommendations
4. Safe cleanup commands ready to execute

---

*"What if alignment meant building rules an AI would CHOOSE to follow?"*

**Ready for audit. Begin Phase 1: Branch Analysis.**
