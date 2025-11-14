# 🔄 RESTARTER PROMPT - Universal Session Activation

**Purpose:** Restart stalled sessions with proper auto-detection and atomic claiming
**Use When:** Sessions aren't advancing, coordination is broken, or starting fresh
**Last Updated:** 2025-11-14 09:00 UTC

---

## 📋 PASTE THIS INTO ALL SESSIONS

```
You are an autonomous InfraFabric/NaviDocs session. Your job is to claim available work and execute it WITHOUT human intervention.

⚠️ CRITICAL: Run these checks BEFORE doing anything else.

## STEP 1: VERIFY REPOSITORY LOCATION

pwd
git remote -v

If you see "infrafabric" → You're in InfraFabric repo (good for API research)
If you see "navidocs" → You're in NaviDocs repo (good for development)
If you see something else → STOP and report error

## STEP 2: GET LATEST STATUS FILE

cd /home/user/infrafabric
git fetch origin
git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

## STEP 3: AUTO-DETECT YOUR ASSIGNMENT

cat SESSION-STATUS.md

Look for the FIRST session with:
- Status: ⏳ READY TO DEPLOY
- Claimed By: UNCLAIMED

If you find one, that's YOUR assignment.
If you find ZERO, then all work is claimed or complete.

## STEP 4: CLAIM YOUR SESSION ATOMICALLY

Once you identify your session (e.g., "Session 2: Cloud Provider APIs"):

# Example for Session 2 - modify for your session number
SESSION_NAME="Session 2: Cloud Provider APIs"
CLAIM_ID="CLAIMED-$(date +%s)-$$"

# Update the status file
sed -i "/^### $SESSION_NAME$/,/^###/ s/Claimed By: UNCLAIMED/Claimed By: $CLAIM_ID/" SESSION-STATUS.md

# Commit immediately
git add SESSION-STATUS.md
git commit -m "claim: $SESSION_NAME claimed by session $CLAIM_ID"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Verify push succeeded
if [ $? -eq 0 ]; then
  echo "✅ Successfully claimed $SESSION_NAME"
else
  echo "❌ Claim failed (another session got it first)"
  echo "Retrying with next available session..."
  git pull --rebase
  # Go back to STEP 3
fi

## STEP 5: SWITCH TO CORRECT REPOSITORY IF NEEDED

Read your session details from SESSION-STATUS.md:
- Look at "Repository: dannystocker/XXXXX"
- Look at "Branch Pattern: claude/XXXXX-*"

If your session is assigned to NaviDocs:
  cd /home/user
  if [ ! -d "navidocs" ]; then
    git clone https://github.com/dannystocker/navidocs.git navidocs
  fi
  cd navidocs
  git checkout navidocs-cloud-coordination
  git pull origin navidocs-cloud-coordination

If your session is assigned to InfraFabric:
  cd /home/user/infrafabric
  git checkout -b claude/your-session-name-$(cat /proc/sys/kernel/random/uuid | cut -d'-' -f1)

## STEP 6: READ YOUR MISSION DETAILS

From SESSION-STATUS.md, note:
- Agents: How many Haiku agents to deploy (e.g., "10 Haiku (Haiku-21 to Haiku-30)")
- Research Scope: What APIs to research (e.g., "AWS, GCP, Azure...")
- Output File: Where to write results (e.g., "INTEGRATIONS-CLOUD-PROVIDERS.md")
- Mission File: If NaviDocs, read this file (e.g., "S2_MISSION_1_BACKEND_SWARM.md")

## STEP 7: EXECUTE YOUR MISSION

### For InfraFabric API Research Sessions:

Read the deployment guide:
https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/HAIKU-SWARM-HOSTING-API-RESEARCH.md

Then deploy your agents:

# Example for Session 2 (Cloud APIs) - modify for your session
Deploy 10 Haiku agents in parallel using Task tool:
- Haiku-21: AWS (EC2, S3, Lambda, CloudFront, Route53)
- Haiku-22: GCP (Compute, Storage, Cloud Functions, CDN, DNS)
- Haiku-23: Azure (VMs, Blob Storage, Functions, CDN, DNS)
- Haiku-24: DigitalOcean (Droplets, Spaces, Functions, CDN)
- Haiku-25: Linode (Instances, Object Storage, NodeBalancers)
- Haiku-26: Vultr (Instances, Object Storage, Load Balancers)
- Haiku-27: Hetzner (Cloud Servers, Object Storage, Load Balancers)
- Haiku-28: S3-compatible APIs (MinIO, Wasabi, Backblaze B2)
- Haiku-29: CDN APIs (Cloudflare, Fastly, KeyCDN, BunnyCDN)
- Haiku-30: Object Storage Aggregation (research summary)

Use IF.search 8-pass methodology for each API.

Write all results to your Output File.

Commit frequently with descriptive messages.

### For NaviDocs Development Sessions:

Read your mission file from the navidocs repo:
cat S2_MISSION_X_XXXXX_SWARM.md

Follow the implementation plan in that file.

Deploy your agents as specified in the mission.

All commits go to dannystocker/navidocs, branch navidocs-cloud-coordination.

## STEP 8: UPDATE STATUS WHEN COMPLETE

When ALL your work is done:

cd /home/user/infrafabric
git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Update your session status to COMPLETE
sed -i "/^### $SESSION_NAME$/,/^###/ s/Status: 🔄 IN PROGRESS/Status: ✅ COMPLETE/" SESSION-STATUS.md
sed -i "/^### $SESSION_NAME$/,/^###/ s/Expected Completion:.*/Actual Completion: $(date -u +"%Y-%m-%d %H:%M UTC")/" SESSION-STATUS.md

git add SESSION-STATUS.md
git commit -m "complete: $SESSION_NAME finished all deliverables"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

## STEP 9: ERROR HANDLING

If anything fails at any step:

echo "ERROR at STEP X: [describe what failed]" >> BLOCKERS.md
git add BLOCKERS.md
git commit -m "blocker: Session encountered error at step X"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

Then STOP and report to user.

## CRITICAL RULES

1. ✅ DO claim a session before starting work
2. ✅ DO update SESSION-STATUS.md when complete
3. ✅ DO commit to the correct repository (check SESSION-STATUS.md for which one)
4. ✅ DO use atomic git operations (pull → edit → commit → push immediately)
5. ❌ DON'T start work without claiming
6. ❌ DON'T commit to wrong repository
7. ❌ DON'T leave status as UNCLAIMED if you're working on it
8. ❌ DON'T wait for human approval (95%+ confidence = execute)

## IF NO SESSIONS ARE AVAILABLE

If SESSION-STATUS.md shows ALL sessions are "CLAIMED" or "COMPLETE":

echo "All sessions claimed or complete. No work available."
echo "Checking again in 5 minutes..."
sleep 300
# Then go back to STEP 2

## SUCCESS CRITERIA

You will know you're successful when:
1. ✅ Your session shows "Status: ✅ COMPLETE" in SESSION-STATUS.md
2. ✅ Your output file exists and has comprehensive API research
3. ✅ All commits are pushed to correct repository
4. ✅ No BLOCKERS.md entries for your session

---

BEGIN AUTONOMOUS EXECUTION NOW.
Read SESSION-STATUS.md, claim your session, and start your mission.
```

---

## 🔧 TROUBLESHOOTING

### "Session claims conflicted"
- Another session claimed first
- Pull latest: `git pull --rebase`
- Try claiming next UNCLAIMED session

### "Can't find SESSION-STATUS.md"
- You're not in infrafabric repo
- Run: `cd /home/user/infrafabric`
- Run: `git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`

### "All sessions show CLAIMED but no commits happening"
- Sessions may have stalled after claiming
- Reset stale claims (>2 hours old):
  - Edit SESSION-STATUS.md
  - Change old CLAIMED-* back to UNCLAIMED
  - Commit and push

### "Wrong repository errors"
- Check SESSION-STATUS.md "Repository:" field
- Switch repos before starting work
- Use full paths: `/home/user/infrafabric` or `/home/user/navidocs`

---

## 📊 MONITORING AFTER RESTART

After pasting restarter prompt to all sessions, monitor:

```bash
# Check which sessions claimed work (run every 60 seconds)
watch -n 60 'git pull -q && grep "Claimed By:" SESSION-STATUS.md'

# Check recent commits across all sessions
watch -n 60 'git fetch --all -q && git log --all --oneline --since="10 minutes ago"'

# Check for blockers
watch -n 60 'git pull -q && cat BLOCKERS.md 2>/dev/null || echo "No blockers"'
```

You should see:
- ✅ Claims appearing in SESSION-STATUS.md within 1-2 minutes
- ✅ New commits from various branches within 5-10 minutes
- ✅ Agents being deployed (check for Task tool usage)
- ✅ Research files being created in docs/

If you see NONE of this after 5 minutes, sessions are still stuck (check error logs).

---

## 🎯 EXPECTED TIMELINE AFTER RESTART

| Time | Expected Activity |
|------|-------------------|
| T+0 to T+2 min | Sessions claim work, update SESSION-STATUS.md |
| T+2 to T+5 min | Sessions read mission files, switch repos if needed |
| T+5 to T+10 min | First agent deployments visible (Task tool calls) |
| T+10 to T+30 min | Active commits from multiple sessions |
| T+30 min to T+4h | Steady progress, research files growing |
| T+4h | First sessions mark COMPLETE |

---

## ✅ VALIDATION CHECKLIST

Before closing this issue:

- [ ] SESSION-STATUS.md exists in infrafabric repo
- [ ] All 7 sessions pasted restarter prompt
- [ ] Within 5 minutes, saw claims in SESSION-STATUS.md
- [ ] Within 10 minutes, saw commits from multiple branches
- [ ] No BLOCKERS.md entries with unresolved errors
- [ ] Monitoring shows steady progress every 60 seconds

---

**This restarter prompt fixes all 6 blockers identified in the diagnosis:**
1. ✅ Uses actual SESSION-STATUS.md file (not prose)
2. ✅ Atomic claim mechanism with git operations
3. ✅ Pre-flight repository checks before work starts
4. ✅ Explicit error handling with fallbacks
5. ✅ Clear success criteria and validation
6. ✅ Real-time monitoring guidance for orchestrator
