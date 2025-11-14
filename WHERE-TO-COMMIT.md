# WHERE TO COMMIT - Quick Reference Guide

**⚠️ CRITICAL: Two different repositories, two different purposes ⚠️**

---

## 📋 SIMPLE RULE

```
API Research Sessions    → dannystocker/infrafabric
NaviDocs Development     → dannystocker/navidocs
```

---

## 🔍 HOW TO KNOW WHICH REPOSITORY YOU'RE IN

Run this command:
```bash
git remote -v
```

**If you see `infrafabric`**: You're in the InfraFabric repository
**If you see `navidocs`**: You're in the NaviDocs repository

---

## ✅ SESSION TYPES & WHERE THEY COMMIT

### InfraFabric Repository Sessions

| Session | What They Do | Repository | Branch Pattern |
|---------|--------------|------------|----------------|
| **Session 2** | Cloud Provider API Research | `dannystocker/infrafabric` | `claude/cloud-providers-<id>` |
| **Session 3** | SIP/Communication API Research | `dannystocker/infrafabric` | `claude/sip-communication-<id>` |
| **Session 4** | Payment/Billing API Research | `dannystocker/infrafabric` | `claude/payment-billing-<id>` |

**Working Directory**: `/home/user/infrafabric`
**Output Files**: `INTEGRATIONS-*.md`
**Commit Messages**: `docs(research): Add comprehensive <topic> API research...`

### NaviDocs Repository Sessions

| Session | What They Do | Repository | Branch Pattern |
|---------|--------------|------------|----------------|
| **Backend Swarm** | NaviDocs Backend (10 Haiku) | `dannystocker/navidocs` | `navidocs-backend-<id>` |
| **Frontend Swarm** | NaviDocs Frontend (10 Haiku) | `dannystocker/navidocs` | `navidocs-frontend-<id>` |
| **Integration Swarm** | NaviDocs Integration (10 Haiku) | `dannystocker/navidocs` | `navidocs-integration-<id>` |
| **Sonnet Planner** | NaviDocs Coordinator (1 Sonnet) | `dannystocker/navidocs` | `navidocs-planner-<id>` |

**Working Directory**: `/home/user/navidocs`
**Output Files**: Code, tests, documentation
**Commit Messages**: `feat(navidocs): Implement <swarm> swarm...`

---

## 🚨 BEFORE YOU COMMIT - CHECKLIST

**Step 1**: Check which repository you're in
```bash
git remote -v
```

**Step 2**: Verify it matches your assignment
- **API Research** (Sessions 2-4) = Should see `infrafabric`
- **NaviDocs Development** = Should see `navidocs`

**Step 3**: If wrong repository, switch to correct one

**For NaviDocs work but in InfraFabric repo:**
```bash
cd /home/user
git clone https://github.com/dannystocker/navidocs.git navidocs
cd navidocs
git checkout navidocs-cloud-coordination
```

**For InfraFabric work but in NaviDocs repo:**
```bash
cd /home/user/infrafabric
```

**Step 4**: NOW you can commit

---

## 💡 QUICK DECISION TREE

```
Are you doing API research?
├── YES → Use dannystocker/infrafabric
└── NO → Are you building NaviDocs features?
    ├── YES → Use dannystocker/navidocs
    └── NO → Read the mission file again!
```

---

## 📖 DETAILED EXAMPLES

### Example 1: Cloud Provider API Research (Session 2)

**Assignment**: Research AWS, GCP, Azure APIs
**Repository**: `dannystocker/infrafabric` ✅
**Working Dir**: `/home/user/infrafabric`
**Branch**: `claude/cloud-providers-ABC123`
**Files Created**: `INTEGRATIONS-CLOUD-PROVIDERS.md`
**Commit Message**: `docs(research): Add comprehensive cloud provider API research from 10-agent swarm`

**Verification**:
```bash
cd /home/user/infrafabric
git remote -v
# Should show: https://github.com/dannystocker/infrafabric
```

### Example 2: NaviDocs Backend Development

**Assignment**: Build NaviDocs backend infrastructure
**Repository**: `dannystocker/navidocs` ✅
**Working Dir**: `/home/user/navidocs`
**Branch**: `navidocs-backend-XYZ789`
**Files Created**: `src/api/`, `src/db/`, tests, etc.
**Commit Message**: `feat(navidocs): Implement backend swarm`

**Verification**:
```bash
cd /home/user/navidocs
git remote -v
# Should show: https://github.com/dannystocker/navidocs
```

---

## ⚠️ COMMON MISTAKES TO AVOID

### ❌ WRONG: NaviDocs code committed to InfraFabric repo
```bash
# You're building NaviDocs backend but...
cd /home/user/infrafabric  # ← WRONG REPO!
git add src/api/
git commit -m "feat(navidocs): Backend API"
# ❌ This commits NaviDocs code to the wrong repository!
```

### ✅ CORRECT: NaviDocs code committed to NaviDocs repo
```bash
# You're building NaviDocs backend
cd /home/user/navidocs  # ← CORRECT REPO!
git add src/api/
git commit -m "feat(navidocs): Backend API"
# ✅ This commits to the right place
```

### ❌ WRONG: API research committed to NaviDocs repo
```bash
# You're researching Stripe API but...
cd /home/user/navidocs  # ← WRONG REPO!
git add INTEGRATIONS-PAYMENT-BILLING.md
git commit -m "docs(research): Payment APIs"
# ❌ This commits InfraFabric research to the wrong repository!
```

### ✅ CORRECT: API research committed to InfraFabric repo
```bash
# You're researching Stripe API
cd /home/user/infrafabric  # ← CORRECT REPO!
git add INTEGRATIONS-PAYMENT-BILLING.md
git commit -m "docs(research): Payment APIs"
# ✅ This commits to the right place
```

---

## 🎯 FINAL CHECKLIST (BEFORE EVERY COMMIT)

```
[ ] I ran: git remote -v
[ ] I verified the repository matches my assignment
[ ] I'm in the correct working directory
[ ] My branch name follows the correct pattern
[ ] My commit message follows the correct format
[ ] I'm ready to push to the correct GitHub repository
```

---

## 📞 WHEN IN DOUBT

**Ask yourself**: "Am I researching APIs or building NaviDocs?"

- **Researching APIs** → InfraFabric repository
- **Building NaviDocs** → NaviDocs repository

**Still unsure?** Check your mission file:
- Mission files in `infrafabric` repo → Work in InfraFabric repo
- Mission files in `navidocs` repo → Work in NaviDocs repo

---

**Last Updated**: 2025-11-14
**Purpose**: Prevent commits to wrong repository
**Severity**: CRITICAL - Wrong commits cause major cleanup work
