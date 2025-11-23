# Codex 5.1 MAX: Quick Starter Prompt

**Mission:** Verify Phase A deployment (bridge.php v2.0) + Complete infrastructure audit

**For detailed instructions:** See `/home/setup/infrafabric/CODEX-5.1-MAX-SUPERPROMPT.md`

---

## Quick Context

**Project:** Memory Exoskeleton - Bridge WSL Redis to Gemini-3-Pro via StackCP

**Current Status:**
- ✅ Phase A COMPLETE: bridge.php v2.0 + semantic search ready
- ✅ 105 Redis keys tagged (75.2% coverage)
- ⏳ Need to verify deployment + identify remaining gaps

**StackCP Access:**
```
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com "command"
API: https://digital-lab.ca/infrafabric/bridge.php
Token: 50040d7fbfaa712fccfc5528885ebb9b
```

---

## Immediate Tasks

### Task 1: Verify Phase A Deployment (First)
```bash
# Check if v2.0 is deployed
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=info"

# Should show: "version": "2.0.0" and "semantic_tags_available": true
```

**If v2.0 NOT deployed:**
1. `scp /home/setup/infrafabric/swarm-architecture/bridge-v2.php digital-lab.ca:~/public_html/digital-lab.ca/infrafabric/bridge.php`
2. `scp /tmp/redis-semantic-tags-bridge.json digital-lab.ca:~/public_html/digital-lab.ca/infrafabric/redis-semantic-tags.json`
3. Test endpoints above

### Task 2: Complete Infrastructure Audit
Run verification commands from the full superprompt (PART 1-3) to:
- Verify all tool versions
- Identify P0/P1 issues
- Find undocumented resources
- Create final audit report

---

## Phase A Test Endpoints (After Deployment)

```bash
# Semantic search
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=search&query=partnership"

# Semantic tags
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=tags&pattern=instance:*"
```

---

## Deliverable

**Create:** `/home/setup/CODEX-AUDIT-FINAL-2025-11-23.md`

Contents:
1. Phase A deployment status (working/issues)
2. Infrastructure inventory (100% surface)
3. Gap analysis with severity rankings
4. Undocumented resources found
5. Security recommendations
6. Phase B readiness assessment

---

## Reference Files

- Full superprompt: `/home/setup/infrafabric/CODEX-5.1-MAX-SUPERPROMPT.md`
- Phase A complete: `/home/setup/infrafabric/SESSION-INSTANCE-19-PHASE-A-COMPLETE.md`
- Deployment guide: `/home/setup/infrafabric/swarm-architecture/DEPLOY-BRIDGE-V2.md`
- Project master doc: `/home/setup/infrafabric/agents.md`

---

**Ready to begin. Verify Phase A first, then complete audit.**
