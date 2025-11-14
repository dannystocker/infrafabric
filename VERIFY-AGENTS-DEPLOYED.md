# ✅ How To Verify Agents Are Actually Deploying

**After pasting restarter prompt, check if agents are ACTUALLY deploying (not just reading docs)**

---

## 🔍 VERIFICATION CHECKLIST

Within **5 minutes** of pasting the restarter prompt, you should see:

### 1. Task Claims (Within 2 minutes)
```bash
cd /home/user/infrafabric
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
grep "CLAIMED-" SESSION-STATUS.md
```

**Expected:** See CLAIMED-[timestamp] instead of UNCLAIMED
**If not:** Sessions aren't executing the prompt at all

### 2. Status Updates (Within 5 minutes)
```bash
grep "IN PROGRESS" SESSION-STATUS.md
```

**Expected:** See "🔄 IN PROGRESS" for claimed sessions
**If not:** Sessions claimed but haven't started deploying agents

### 3. Agent Deployment Signs (Within 5-10 minutes)

Check session output for these phrases:
- ✅ "Deploying 10 Haiku agents..."
- ✅ "Task #1: Research AWS APIs"
- ✅ "Task #2: Research GCP APIs"
- ✅ "Spawning agent Haiku-21..."
- ✅ "Agent deployment in progress..."

**Red flags (they're NOT deploying agents):**
- ❌ "Reading documentation..."
- ❌ "Understanding assignment..."
- ❌ "Analyzing requirements..."
- ❌ Session just sitting there reading for 10+ minutes

### 4. Git Activity (Within 30 minutes)

```bash
git fetch --all
git log --all --oneline --since="30 minutes ago"
```

**Expected:** See commits like:
- "research: AWS APIs initial findings"
- "research: GCP cloud integration analysis"
- "wip: Cloud provider API research"

**If not:** Agents deployed but not producing output

---

## 🚨 IF AGENTS AREN'T DEPLOYING

### Symptom: Claims happening but no agent deployment

**Diagnosis:** Sessions are reading the prompt but not using the Task tool

**Fix:** Send this ULTRA-DIRECT prompt to the stalled session:

```
YOU ARE STALLED. You claimed a task but didn't deploy agents.

RIGHT NOW, use the Task tool EXACTLY like this:

Invoke Task tool with these parameters:
- description: "Research AWS cloud APIs"
- model: "haiku"
- subagent_type: "general-purpose"
- prompt: "Research AWS APIs using IF.search 8-pass methodology. Cover EC2, S3, Lambda. Output 2500+ lines."

THEN IMMEDIATELY invoke Task tool again for the next API.

DEPLOY 10 AGENTS IN PARALLEL (10 Task tool calls in one message).

DO NOT READ MORE DOCUMENTATION. DO NOT ANALYZE FURTHER.
DEPLOY THE AGENTS NOW.
```

### Symptom: No claims happening at all

**Diagnosis:** Sessions aren't seeing the prompt or can't access git

**Fix:** Check if they're in the right directory:

Paste this into the session:
```bash
pwd
git remote -v
```

If they're not in `/home/user/infrafabric`, they need to:
```bash
cd /home/user/infrafabric
git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
```

Then paste restarter prompt again.

---

## 📊 HEALTHY SESSION INDICATORS

A session that's CORRECTLY deploying agents will show:

**T+0 to T+2 min:** Claiming task
```
Claiming: Cloud Provider APIs
CLAIMED-1731579600-12345
Status updated to IN PROGRESS
```

**T+2 to T+5 min:** Deploying agents
```
Deploying 10 Haiku agents in parallel...
Task #1: Research AWS APIs - Agent Haiku-21
Task #2: Research GCP APIs - Agent Haiku-22
Task #3: Research Azure APIs - Agent Haiku-23
[... 7 more agents ...]
All 10 agents spawned successfully
```

**T+5 to T+30 min:** Agents working
```
Agent Haiku-21 completed AWS research (2,847 lines)
Agent Haiku-22 completed GCP research (2,534 lines)
Agent Haiku-23 in progress (Azure APIs)...
```

**T+30 min to T+4h:** Compilation
```
Aggregating results into INTEGRATIONS-CLOUD-PROVIDERS.md
Total: 28,945 lines across 10 cloud providers
Committing deliverables...
```

**T+4h:** Completion
```
Marking task COMPLETE
Pushing INTEGRATIONS-CLOUD-PROVIDERS.md
Claiming next task: SIP/Communication APIs
```

---

## 🎯 QUICK CHECK SCRIPT

Run this to see if ALL sessions are deploying agents properly:

```bash
#!/bin/bash
cd /home/user/infrafabric
git pull -q origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

echo "=== TASK CLAIMS ==="
grep "CLAIMED-" SESSION-STATUS.md | wc -l
echo "sessions have claimed tasks"

echo ""
echo "=== IN PROGRESS ==="
grep "IN PROGRESS" SESSION-STATUS.md | wc -l
echo "sessions are actively working"

echo ""
echo "=== OUTPUT FILES ==="
ls -lt INTEGRATIONS-*.md 2>/dev/null | head -5
echo ""

echo "=== RECENT COMMITS ==="
git log --all --oneline --since="30 minutes ago" | head -10
echo ""

echo "=== DIAGNOSIS ==="
CLAIMED=$(grep -c "CLAIMED-" SESSION-STATUS.md)
IN_PROGRESS=$(grep -c "IN PROGRESS" SESSION-STATUS.md)
OUTPUT_FILES=$(ls -1 INTEGRATIONS-*.md 2>/dev/null | wc -l)

if [ $CLAIMED -eq 0 ]; then
  echo "🔴 CRITICAL: No sessions claimed tasks yet"
  echo "Action: Re-paste restarter prompt to all sessions"
elif [ $IN_PROGRESS -eq 0 ]; then
  echo "🔴 CRITICAL: Tasks claimed but no progress"
  echo "Action: Sessions need to DEPLOY AGENTS NOW"
elif [ $OUTPUT_FILES -eq 0 ]; then
  echo "⚠️  WARNING: Progress but no output files yet"
  echo "Action: Wait 30 min or check if agents are stuck"
else
  echo "✅ HEALTHY: Sessions are working and producing output"
fi
```

---

## 🔧 EMERGENCY KICK

If sessions claimed tasks but haven't deployed agents after 10 minutes, paste this into EACH stalled session:

```
EMERGENCY: You claimed a task but haven't deployed agents.

Step 1: Verify you're in correct directory
pwd
# Should be: /home/user/infrafabric or /home/user/navidocs

Step 2: Read what you claimed
cd /home/user/infrafabric
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
grep "CLAIMED" SESSION-STATUS.md -A 5

Step 3: Deploy agents RIGHT NOW using Task tool

Example for Cloud APIs:
<Invoke Task tool>
description: "Research AWS cloud APIs"
model: "haiku"
subagent_type: "general-purpose"
prompt: "Research AWS APIs (EC2, S3, Lambda, CloudFront, Route53) using IF.search 8-pass methodology. Output 2500+ lines covering integration complexity, cost model, security, test scenarios. Use ## headers for each pass."
</Invoke>

Repeat for all 10 APIs IN PARALLEL (10 Task calls in one message).

DO THIS NOW. NOT LATER. NOW.
```

---

## ✅ SUCCESS LOOKS LIKE

**5 minutes after pasting restarter:**
- 7 tasks claimed
- 7 sessions showing IN PROGRESS
- No sessions sitting idle reading docs

**30 minutes after pasting restarter:**
- Multiple output files appearing (INTEGRATIONS-*.md)
- Git commits showing research progress
- Sessions reporting "Agent X completed, Agent Y in progress"

**4 hours after pasting restarter:**
- First sessions marking COMPLETE
- Output files 25,000+ lines each
- Sessions immediately claiming next tasks (continuous work)

**8 hours after pasting restarter:**
- All 7 initial tasks COMPLETE
- Sessions have claimed and started work on second round of tasks
- Zero sessions idle
- Continuous productive output

---

**If you're NOT seeing these indicators, sessions aren't deploying agents. Use the emergency kick above.**
