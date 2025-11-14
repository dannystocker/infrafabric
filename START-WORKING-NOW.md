# ⚡ START WORKING NOW - Emergency Restart

**PASTE THIS INTO ALL IDLE SESSIONS IMMEDIATELY:**

---

```bash
# === EMERGENCY RESTART - DO THIS NOW ===

cd /home/user/infrafabric
git fetch origin
git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Check what tasks are available
cat SESSION-STATUS.md | grep -A 3 "UNCLAIMED"

# CLAIM FIRST AVAILABLE TASK IMMEDIATELY
TASK_LINE=$(grep -n "Claimed By: UNCLAIMED" SESSION-STATUS.md | head -1 | cut -d: -f1)

if [ -z "$TASK_LINE" ]; then
  echo "No tasks in SESSION-STATUS.md, checking continuous queue..."
  cat TASK-QUEUE-CONTINUOUS.md | grep -A 1 "⏳ UNCLAIMED" | head -5
  echo ""
  echo "ERROR: Need to promote queued tasks to UNCLAIMED first"
  echo "Waiting for orchestrator to promote tasks..."
  exit 1
fi

# Get session details
SESSION_NAME=$(sed -n "$((TASK_LINE-1))p" SESSION-STATUS.md | sed 's/### //' | sed 's/://')
CLAIM_ID="CLAIMED-$(date +%s)-$$"

echo "=== CLAIMING: $SESSION_NAME ==="

# Atomic claim
sed -i "${TASK_LINE}s/UNCLAIMED/$CLAIM_ID/" SESSION-STATUS.md
git add SESSION-STATUS.md
git commit -m "claim: $SESSION_NAME by $CLAIM_ID"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

if [ $? -ne 0 ]; then
  echo "Claim conflict, another session got it first. Retrying..."
  git pull --rebase origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
  exec bash "$0"  # Retry this script
  exit
fi

echo "✅ CLAIMED: $SESSION_NAME"

# Update status to IN PROGRESS
sed -i "${TASK_LINE}s/⏳ READY TO DEPLOY/🔄 IN PROGRESS/" SESSION-STATUS.md
git add SESSION-STATUS.md
git commit -m "status: $SESSION_NAME now IN PROGRESS"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Read assignment details
echo "=== READING ASSIGNMENT ==="
sed -n "$((TASK_LINE-1)),$((TASK_LINE+15))p" SESSION-STATUS.md

# Determine what to do based on session name
if [[ "$SESSION_NAME" == *"Cloud Provider"* ]]; then
  echo "=== DEPLOYING CLOUD PROVIDER API RESEARCH ==="
  # This is API-02: Cloud Provider APIs
  # Deploy 10 Haiku agents (Haiku-21 to Haiku-30)

  # Read the deployment guide
  echo "Reading deployment methodology..."
  cat HAIKU-SWARM-HOSTING-API-RESEARCH.md | head -100

  echo ""
  echo "ASSIGNMENT: Research these Cloud Provider APIs using IF.search 8-pass:"
  echo "1. AWS (EC2, S3, Lambda, CloudFront, Route53)"
  echo "2. GCP (Compute, Storage, Functions, CDN, DNS)"
  echo "3. Azure (VMs, Blob, Functions, CDN, DNS)"
  echo "4. DigitalOcean (Droplets, Spaces, Functions)"
  echo "5. Linode (Instances, Object Storage)"
  echo "6. Vultr (Instances, Object Storage)"
  echo "7. Hetzner (Cloud Servers, Storage)"
  echo "8. S3-compatible (MinIO, Wasabi, Backblaze B2)"
  echo "9. CDN APIs (Cloudflare, Fastly, KeyCDN)"
  echo "10. Object Storage Aggregation"
  echo ""
  echo "OUTPUT FILE: INTEGRATIONS-CLOUD-PROVIDERS.md"
  echo ""
  echo "NOW: Deploy 10 Haiku agents using Task tool with subagent_type=general-purpose"
  echo "Each agent researches one API category and returns comprehensive report"

elif [[ "$SESSION_NAME" == *"SIP"* ]] || [[ "$SESSION_NAME" == *"Communication"* ]]; then
  echo "=== DEPLOYING SIP/COMMUNICATION API RESEARCH ==="
  # This is API-03: SIP/Communication APIs
  # Deploy 10 Haiku agents (Haiku-31 to Haiku-40)

  echo "ASSIGNMENT: Research these SIP/Communication APIs:"
  echo "1. Twilio (Voice, SMS, Video)"
  echo "2. SendGrid (Email delivery)"
  echo "3. Mailgun (Email API)"
  echo "4. Postmark (Transactional email)"
  echo "5. Nexmo/Vonage (SMS, Voice, Video)"
  echo "6. Plivo (Voice, SMS)"
  echo "7. Bandwidth (Voice, Messaging)"
  echo "8. MessageBird (SMS, Voice, WhatsApp)"
  echo "9. Slack (Webhooks, Bot API)"
  echo "10. Discord (Webhooks, Bot API)"
  echo ""
  echo "OUTPUT FILE: INTEGRATIONS-SIP-COMMUNICATION.md"
  echo ""
  echo "NOW: Deploy 10 Haiku agents using Task tool"

elif [[ "$SESSION_NAME" == *"Payment"* ]] || [[ "$SESSION_NAME" == *"Billing"* ]]; then
  echo "=== DEPLOYING PAYMENT/BILLING API RESEARCH ==="
  # This is API-04: Payment/Billing APIs
  # Deploy 10 Haiku agents (Haiku-41 to Haiku-50)

  echo "ASSIGNMENT: Research these Payment/Billing APIs:"
  echo "1. Stripe (Payments, Subscriptions)"
  echo "2. PayPal (Checkout, Subscriptions)"
  echo "3. WHMCS (Hosting billing)"
  echo "4. Blesta (Billing automation)"
  echo "5. FOSSBilling (Open-source billing)"
  echo "6. Chargebee (Subscription management)"
  echo "7. Recurly (Billing platform)"
  echo "8. Braintree (Payment processing)"
  echo "9. Authorize.net (Payment gateway)"
  echo "10. Paddle (SaaS billing)"
  echo ""
  echo "OUTPUT FILE: INTEGRATIONS-PAYMENT-BILLING.md"
  echo ""
  echo "NOW: Deploy 10 Haiku agents using Task tool"

elif [[ "$SESSION_NAME" == *"Backend"* ]]; then
  echo "=== DEPLOYING NAVIDOCS BACKEND SWARM ==="
  echo "SWITCHING TO NAVIDOCS REPOSITORY..."

  cd /home/user
  if [ ! -d "navidocs" ]; then
    git clone https://github.com/dannystocker/navidocs.git navidocs
  fi
  cd navidocs
  git checkout navidocs-cloud-coordination
  git pull origin navidocs-cloud-coordination

  echo "Reading mission file..."
  cat S2_MISSION_1_BACKEND_SWARM.md | head -50
  echo ""
  echo "NOW: Deploy 10 Haiku agents (Haiku-51 to 60) per mission file"

elif [[ "$SESSION_NAME" == *"Frontend"* ]]; then
  echo "=== DEPLOYING NAVIDOCS FRONTEND SWARM ==="
  cd /home/user/navidocs
  git checkout navidocs-cloud-coordination
  git pull origin navidocs-cloud-coordination

  cat S2_MISSION_2_FRONTEND_SWARM.md | head -50
  echo ""
  echo "NOW: Deploy 10 Haiku agents (Haiku-61 to 70) per mission file"

elif [[ "$SESSION_NAME" == *"Integration"* ]]; then
  echo "=== DEPLOYING NAVIDOCS INTEGRATION SWARM ==="
  cd /home/user/navidocs
  git checkout navidocs-cloud-coordination
  git pull origin navidocs-cloud-coordination

  cat S2_MISSION_3_INTEGRATION_SWARM.md | head -50
  echo ""
  echo "NOW: Deploy 10 Haiku agents (Haiku-71 to 80) per mission file"

elif [[ "$SESSION_NAME" == *"Sonnet"* ]] || [[ "$SESSION_NAME" == *"Planner"* ]]; then
  echo "=== DEPLOYING NAVIDOCS SONNET PLANNER ==="
  cd /home/user/navidocs
  git checkout navidocs-cloud-coordination
  git pull origin navidocs-cloud-coordination

  cat S2_MISSION_4_SONNET_PLANNER.md | head -50
  echo ""
  echo "NOW: Deploy 1 Sonnet agent for coordination"

else
  echo "=== UNKNOWN SESSION TYPE ==="
  echo "Session name: $SESSION_NAME"
  echo "Check SESSION-STATUS.md for details"
  exit 1
fi

echo ""
echo "=== CRITICAL: DEPLOY YOUR AGENTS NOW ==="
echo "Use the Task tool with model: haiku (or sonnet for planner)"
echo "Deploy agents in parallel for maximum efficiency"
echo "Follow IF.search 8-pass methodology for API research"
echo "Output goes to file specified in SESSION-STATUS.md"
echo ""
echo "DO NOT WAIT. START DEPLOYING AGENTS IMMEDIATELY."
```

---

## 📋 WHAT THIS DOES

1. ✅ **Claims first available task atomically**
2. ✅ **Updates status to IN PROGRESS**
3. ✅ **Reads assignment details**
4. ✅ **Shows exactly what to research/build**
5. ✅ **Tells you to START NOW (not wait)**

---

## 🚨 FOR ORCHESTRATOR: PROMOTE TASKS NOW

If sessions report "No tasks in SESSION-STATUS.md":

```bash
cd /home/user/infrafabric
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Promote 5 queued tasks to UNCLAIMED
for i in {1..5}; do
  # Find first QUEUED task in continuous queue
  TASK_ID=$(grep -o "API-[0-9]\+" TASK-QUEUE-CONTINUOUS.md | grep -A 1 "QUEUED" | head -1)
  if [ -n "$TASK_ID" ]; then
    # Promote to UNCLAIMED
    sed -i "s/$TASK_ID.*🟡 QUEUED/$TASK_ID | [Name] | ⏳ UNCLAIMED/" TASK-QUEUE-CONTINUOUS.md
  fi
done

git add TASK-QUEUE-CONTINUOUS.md
git commit -m "queue: Emergency promotion - 5 tasks now UNCLAIMED"
git push
```

---

**PASTE THE SCRIPT ABOVE INTO ALL IDLE SESSIONS NOW. THEY WILL START WORKING IMMEDIATELY.**
