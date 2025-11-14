# ⚡ Sandboxed Session Restarter - PASTE THIS NOW

**GitHub URL:** `https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/RESTARTER-SANDBOXED.md`

**Instructions for User:** Paste the prompt below into ALL idle Claude Code sessions

---

## 🎯 PROMPT TO PASTE (Copy everything below this line)

```
You are an autonomous InfraFabric/NaviDocs agent. You are currently IDLE and need to claim work immediately.

STEP 1: Get to the coordination hub
===========================================

cd /home/user/infrafabric
git fetch origin
git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

STEP 2: Check what tasks are available
===========================================

cat SESSION-STATUS.md

Look for sections with:
- Status: ⏳ READY TO DEPLOY
- Claimed By: UNCLAIMED

STEP 3: Claim the FIRST unclaimed task
===========================================

Find the first UNCLAIMED task and run these commands:

# Example: If "Session 2: Cloud Provider APIs" is UNCLAIMED

SESSION_LINE=$(grep -n "### Session 2: Cloud Provider APIs" SESSION-STATUS.md | cut -d: -f1)
CLAIM_LINE=$((SESSION_LINE + 1))
CLAIM_ID="CLAIMED-$(date +%s)-$$"

sed -i "${CLAIM_LINE}s/Claimed By: UNCLAIMED/Claimed By: $CLAIM_ID/" SESSION-STATUS.md

git add SESSION-STATUS.md
git commit -m "claim: Cloud Provider APIs claimed by $CLAIM_ID"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

If push fails with conflict:
  git pull --rebase origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
  # Someone else claimed first, try next UNCLAIMED task

STEP 4: Read your assignment details
===========================================

# Look at the section you just claimed
sed -n "${SESSION_LINE},$((SESSION_LINE + 20))p" SESSION-STATUS.md

Note these fields:
- Agents: How many to deploy
- Research Scope: What to research
- Output File: Where to write results
- Repository: Which repo (infrafabric or navidocs)
- Mission File: Detailed instructions (if NaviDocs)

STEP 5: DEPLOY YOUR HAIKU SWARM IMMEDIATELY
===========================================

⚠️⚠️⚠️ CRITICAL: YOU MUST USE THE TASK TOOL TO SPAWN HAIKU AGENTS ⚠️⚠️⚠️

DO NOT just read the assignment. DO NOT wait. DO NOT ask for permission.
YOU MUST DEPLOY AGENTS RIGHT NOW using the Task tool.

### If you claimed Cloud Provider APIs (Session 2):

Research Scope: AWS, GCP, Azure, DigitalOcean, Linode, Vultr, Hetzner, S3-compatible, CDN APIs
Agents: 10 Haiku (Haiku-21 to Haiku-30)
Output: INTEGRATIONS-CLOUD-PROVIDERS.md

🚀 DEPLOY 10 HAIKU AGENTS NOW - COPY AND PASTE THIS:

USE THE TASK TOOL 10 TIMES IN PARALLEL (one message, 10 tool calls):

Task #1: Research AWS APIs
- description: "Research AWS cloud APIs"
- model: "haiku"
- subagent_type: "general-purpose"
- prompt: "You are Haiku-21 researching AWS cloud APIs for InfraFabric integration. Use IF.search 8-pass methodology: 1) Signal Capture (scan AWS docs), 2) Primary Analysis (EC2, S3, Lambda, CloudFront, Route53), 3) Rigor & Refinement (edge cases, limits), 4) Cross-Domain (cost, security), 5) Framework Mapping (how it fits InfraFabric), 6) Specification (implementation steps), 7) Meta-Validation (cite sources), 8) Deployment Planning (timeline estimate). Output: 2500+ lines with integration complexity (1-10), cost model, security considerations, 8+ test scenarios. Format: Markdown with ## headers for each pass."

Task #2: Research GCP APIs
- description: "Research GCP cloud APIs"
- model: "haiku"
- subagent_type: "general-purpose"
- prompt: "You are Haiku-22 researching Google Cloud Platform APIs. Same 8-pass IF.search methodology. Cover: Compute Engine, Cloud Storage, Cloud Functions, Cloud CDN, Cloud DNS. Output 2500+ lines. Focus on GCP-specific features vs AWS."

Task #3: Research Azure APIs
- description: "Research Azure cloud APIs"
- model: "haiku"
- subagent_type: "general-purpose"
- prompt: "You are Haiku-23 researching Microsoft Azure APIs. Same 8-pass methodology. Cover: Virtual Machines, Blob Storage, Azure Functions, Azure CDN, Azure DNS. Output 2500+ lines. Include enterprise integration features."

Task #4: Research DigitalOcean APIs
- description: "Research DigitalOcean APIs"
- model: "haiku"
- subagent_type: "general-purpose"
- prompt: "You are Haiku-24 researching DigitalOcean APIs. Same 8-pass methodology. Cover: Droplets, Spaces, Functions, CDN. Output 2500+ lines. Emphasize developer-friendly simplicity vs enterprise providers."

Task #5: Research Linode APIs
- description: "Research Linode cloud APIs"
- model: "haiku"
- subagent_type: "general-purpose"
- prompt: "You are Haiku-25 researching Linode cloud APIs. Same 8-pass methodology. Cover: Instances, Object Storage, NodeBalancers. Output 2000+ lines. Compare pricing to major providers."

Task #6: Research Vultr APIs
- description: "Research Vultr cloud APIs"
- model: "haiku"
- subagent_type: "general-purpose"
- prompt: "You are Haiku-26 researching Vultr cloud APIs. Same 8-pass methodology. Cover: Instances, Object Storage, Load Balancers. Output 2000+ lines. Focus on global presence and bare metal options."

Task #7: Research Hetzner APIs
- description: "Research Hetzner cloud APIs"
- model: "haiku"
- subagent_type: "general-purpose"
- prompt: "You are Haiku-27 researching Hetzner Cloud APIs. Same 8-pass methodology. Cover: Cloud Servers, Object Storage, Load Balancers. Output 2000+ lines. Emphasize EU data residency and cost efficiency."

Task #8: Research S3-Compatible APIs
- description: "Research S3-compatible storage APIs"
- model: "haiku"
- subagent_type: "general-purpose"
- prompt: "You are Haiku-28 researching S3-compatible storage APIs. Same 8-pass methodology. Cover: MinIO, Wasabi, Backblaze B2, Cloudflare R2. Output 2500+ lines. Focus on S3 API compatibility and migration path."

Task #9: Research CDN APIs
- description: "Research CDN provider APIs"
- model: "haiku"
- subagent_type: "general-purpose"
- prompt: "You are Haiku-29 researching CDN APIs. Same 8-pass methodology. Cover: Cloudflare, Fastly, KeyCDN, BunnyCDN. Output 2500+ lines. Focus on edge computing, caching strategies, and global performance."

Task #10: Synthesize Cloud Research
- description: "Synthesize cloud provider research"
- model: "haiku"
- subagent_type: "general-purpose"
- prompt: "You are Haiku-30 synthesizing cloud provider research. Wait for Haiku-21 to 29 to complete. Then: 1) Aggregate all findings into INTEGRATIONS-CLOUD-PROVIDERS.md, 2) Create comparison table (features, pricing, complexity), 3) Recommend implementation priority (Phase 1/2/3), 4) Estimate total implementation hours, 5) Identify common patterns across providers. Output: Master integration document 3000+ lines."

⚠️ DEPLOY ALL 10 AGENTS IN ONE MESSAGE (parallel execution, not sequential!)

After deploying, you should see agent activity within 2-3 minutes.

### If you claimed SIP/Communication APIs (Session 3):

Research Scope: Twilio, SendGrid, Mailgun, Postmark, Vonage, Plivo, Bandwidth, MessageBird, Slack, Discord
Agents: 10 Haiku (Haiku-31 to Haiku-40)
Output: INTEGRATIONS-SIP-COMMUNICATION.md

🚀 DEPLOY 10 HAIKU AGENTS NOW - USE TASK TOOL 10 TIMES:

Each agent researches ONE communication API using same IF.search 8-pass methodology:
- Haiku-31: Twilio (Voice, SMS, Video APIs)
- Haiku-32: SendGrid (Email delivery API)
- Haiku-33: Mailgun (Email API, webhooks)
- Haiku-34: Postmark (Transactional email)
- Haiku-35: Nexmo/Vonage (SMS, Voice, Video)
- Haiku-36: Plivo (Voice, SMS APIs)
- Haiku-37: Bandwidth (Voice, Messaging)
- Haiku-38: MessageBird (SMS, Voice, WhatsApp)
- Haiku-39: Slack (Webhooks, Bot API, Events API)
- Haiku-40: Discord (Webhooks, Bot API) + Synthesis

Same pattern as Cloud APIs - deploy ALL 10 in parallel, each outputs 2000+ lines.

### If you claimed Payment/Billing APIs (Session 4):

Research Scope: Stripe, PayPal, WHMCS, Blesta, FOSSBilling, Chargebee, Recurly, Braintree, Authorize.net, Paddle
Agents: 10 Haiku (Haiku-41 to Haiku-50)
Output: INTEGRATIONS-PAYMENT-BILLING.md

🚀 DEPLOY 10 HAIKU AGENTS NOW - USE TASK TOOL 10 TIMES:

Each agent researches ONE payment API using same IF.search 8-pass methodology:
- Haiku-41: Stripe (Payments, Subscriptions, Connect)
- Haiku-42: PayPal (Checkout, Subscriptions, Payouts)
- Haiku-43: WHMCS (Hosting billing, automation)
- Haiku-44: Blesta (Billing automation, modules)
- Haiku-45: FOSSBilling (Open-source billing)
- Haiku-46: Chargebee (Subscription management)
- Haiku-47: Recurly (Recurring billing platform)
- Haiku-48: Braintree (Payment processing, vault)
- Haiku-49: Authorize.net (Payment gateway)
- Haiku-50: Paddle (SaaS billing) + Synthesis

Deploy ALL 10 in parallel using Task tool.

### If you claimed NaviDocs Backend/Frontend/Integration/Planner:

Repository: dannystocker/navidocs (NOT infrafabric!)

SWITCH REPOSITORIES FIRST:
cd /home/user
if [ ! -d "navidocs" ]; then
  git clone https://github.com/dannystocker/navidocs.git navidocs
fi
cd navidocs
git checkout navidocs-cloud-coordination
git pull origin navidocs-cloud-coordination

READ YOUR MISSION FILE:
- Backend: cat S2_MISSION_1_BACKEND_SWARM.md
- Frontend: cat S2_MISSION_2_FRONTEND_SWARM.md
- Integration: cat S2_MISSION_3_INTEGRATION_SWARM.md
- Planner: cat S2_MISSION_4_SONNET_PLANNER.md

🚀 DEPLOY AGENTS NOW - USE TASK TOOL:

Backend: Deploy 10 Haiku agents (Haiku-51 to 60) per mission file
- Each agent implements a backend component (API routes, database, auth, etc.)
- Deploy ALL 10 in parallel

Frontend: Deploy 10 Haiku agents (Haiku-61 to 70) per mission file
- Each agent builds a frontend component (dashboard, components, routing)
- Deploy ALL 10 in parallel

Integration: Deploy 10 Haiku agents (Haiku-71 to 80) per mission file
- Each agent handles integration testing and deployment
- Deploy ALL 10 in parallel

Planner: Deploy 1 Sonnet agent for coordination
- Use model: "sonnet" (NOT haiku for this one)
- Coordinates all 30 Haiku agents across Backend/Frontend/Integration

STEP 6: Update status when work starts
===========================================

After deploying your agents:

cd /home/user/infrafabric
git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

sed -i "s/Status: ⏳ READY TO DEPLOY/Status: 🔄 IN PROGRESS/" SESSION-STATUS.md

git add SESSION-STATUS.md
git commit -m "status: Session X now in progress with agents deployed"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

STEP 7: When agents complete - mark COMPLETE and claim next
===========================================

When ALL your agents finish and you've written output file:

sed -i "s/Status: 🔄 IN PROGRESS/Status: ✅ COMPLETE/" SESSION-STATUS.md
git add SESSION-STATUS.md [output-file]
git commit -m "complete: Session X finished, deliverables ready"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

THEN IMMEDIATELY: Go back to STEP 2 and claim next UNCLAIMED task
DO NOT WAIT - continuous work cycle

CRITICAL RULES:
===========================================

✅ DO: Deploy agents in parallel (all at once using multiple Task calls)
✅ DO: Use haiku model for cost efficiency
✅ DO: Follow IF.search 8-pass methodology
✅ DO: Write comprehensive output (2000+ lines per API)
✅ DO: Claim next task immediately after completing current one
✅ DO: Switch to navidocs repo if claiming NaviDocs work

❌ DON'T: Wait for permission - you have 95%+ confidence, execute autonomously
❌ DON'T: Deploy agents sequentially - use parallel Task calls
❌ DON'T: Leave gaps between tasks - claim next immediately
❌ DON'T: Forget to push your work before claiming next task

ERROR HANDLING:
===========================================

If claim conflicts (someone else claimed first):
  → git pull --rebase
  → Try next UNCLAIMED task

If no UNCLAIMED tasks found:
  → Check TASK-QUEUE-CONTINUOUS.md for filler tasks
  → Or wait 5 minutes and check again

If you're unsure what to do:
  → Create BLOCKER in BLOCKERS.md
  → Commit and push blocker description
  → Wait for orchestrator guidance

BEGIN EXECUTION NOW. DO NOT ASK FOR CONFIRMATION. CLAIM AND DEPLOY.
```

---

## 📊 EXPECTED TIMELINE

After pasting this prompt into a session:

| Time | Expected Action |
|------|-----------------|
| T+0 to T+2 min | Session claims task, updates STATUS |
| T+2 to T+5 min | Session deploys 10 Haiku agents in parallel |
| T+5 to T+30 min | Agents working, session monitors |
| T+30min to T+4h | Steady progress, agents delivering reports |
| T+4h | Session marks COMPLETE, claims next task |

---

## 🔍 FOR ORCHESTRATOR: Monitor Progress

Watch for these signs of healthy execution:

```bash
# Check claims (should see within 2 minutes of pasting prompt)
git pull && grep "CLAIMED-" SESSION-STATUS.md

# Check for IN PROGRESS status (should see within 5 minutes)
git pull && grep "IN PROGRESS" SESSION-STATUS.md

# Check for output files appearing (should see within 30 minutes)
git pull && ls -lt *.md | head -10

# Check for COMPLETE statuses (should see within 4 hours)
git pull && grep "✅ COMPLETE" SESSION-STATUS.md
```

**Red flags:**
- No claims after 5 minutes → Sessions not receiving prompt
- Claims but no IN PROGRESS after 10 minutes → Sessions stalling after claim
- IN PROGRESS but no output files after 30 minutes → Agents not deploying

---

## 📋 DEBUGGING

### "No UNCLAIMED tasks found"

All tasks are claimed or complete. Promote queued tasks:

```bash
cd /home/user/infrafabric
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Add more UNCLAIMED tasks from the queue
cat >> SESSION-STATUS.md << 'EOF'

### Session 5: Database APIs
- **Status:** ⏳ READY TO DEPLOY
- **Claimed By:** UNCLAIMED
- **Agents:** 10 Haiku (Haiku-81 to Haiku-90)
- **Research Scope:** PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, DynamoDB, CockroachDB, Cassandra
- **Output File:** `INTEGRATIONS-DATABASE-APIS.md`
- **Timeline:** 3-4 hours
- **Repository:** dannystocker/infrafabric
- **Branch Pattern:** `claude/database-apis-*`
EOF

git add SESSION-STATUS.md
git commit -m "queue: Added Session 5 (Database APIs) for claiming"
git push
```

### "All sessions claimed but no progress"

Sessions may have claimed but not deployed agents. Check:

```bash
# See who claimed what
git log --grep="claim:" --oneline -10

# Check if any output files exist
ls -lt INTEGRATIONS-*.md

# If no output files after 30 min, sessions are stalled
# Send reminder prompt to all sessions
```

---

## ✅ SUCCESS CRITERIA

You'll know this is working when:

1. ✅ Within 5 min: All 7 tasks show CLAIMED status
2. ✅ Within 10 min: Multiple sessions show IN PROGRESS
3. ✅ Within 30 min: Output files appearing (INTEGRATIONS-*.md)
4. ✅ Within 4 hours: First sessions marking COMPLETE and claiming next tasks
5. ✅ Continuous: No sessions idle, always claiming next available task

---

**PASTE THE PROMPT ABOVE INTO ALL IDLE SESSIONS NOW.**

**GitHub URL for sharing:**
```
https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/RESTARTER-SANDBOXED.md
```
