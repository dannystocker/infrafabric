# CLI UX Flows - InfraFabric User Experience Design

**Version:** 1.0
**Date:** 2025-11-12
**Status:** Production-Ready

## Overview

This document defines user experience flows for InfraFabric CLI tools. It provides:
- Common workflows and command sequences
- User journeys for different personas
- Error recovery patterns
- Best practices and anti-patterns

**Philosophy:** IF.ground Principle 8 - Observability without fragility
CLIs should be discoverable, forgiving, and guide users toward success.

---

## User Personas

### 1. Operator (Daily User)
**Goals:** Deploy services, monitor health, troubleshoot issues
**Experience Level:** Intermediate
**Frequency:** Multiple times per day

### 2. Developer (Integration)
**Goals:** Integrate IF components, write tests, debug
**Experience Level:** Advanced
**Frequency:** Daily during development

### 3. Auditor (Compliance)
**Goals:** Review witness logs, verify provenance, generate reports
**Experience Level:** Basic
**Frequency:** Weekly/Monthly

---

## Core Workflows

### Workflow 1: First-Time Setup (Onboarding)

**Goal:** Configure InfraFabric for first use
**Persona:** Operator
**Duration:** 5-10 minutes

```bash
# Step 1: Generate example config
if config init
# Output: Created ~/.config/infrafabric/config.yaml
# Tip: Edit this file to customize settings

# Step 2: View and edit config
cat ~/.config/infrafabric/config.yaml
# Edit as needed: backend (etcd/nats), ports, paths

# Step 3: Initialize witness database
if witness init
# Output: Created ~/.if-witness/witness.db
# Output: Generated signing keys at ~/.if-witness/signing_key.pem

# Step 4: Verify setup
if witness verify
# Output: ✓ Hash chain valid (0 entries)
# Output: ✓ Signing keys present
# Output: ✓ Database accessible

# Step 5: Start coordinator
if coordinator start
# Output: Starting IF.coordinator with etcd backend at localhost:2379
# Output: ✓ Connected to etcd
# Output: ✓ Coordinator ready (0 swarms registered)
```

**Success Indicators:**
- ✅ Config file created
- ✅ Witness database initialized
- ✅ Coordinator running
- ✅ No errors reported

**Common Issues:**
- Port conflict → Edit config: `etcd_port: 2380`
- etcd not running → Start etcd: `etcd`
- Permission denied → Check file permissions

---

### Workflow 2: Daily Operations (Monitor & Deploy)

**Goal:** Monitor system health and deploy tasks
**Persona:** Operator
**Duration:** 2-5 minutes per check

```bash
# Morning Check - System Health
# ==============================

# Step 1: Check coordinator status
if coordinator status
# Output: IF.coordinator [RUNNING]
# Output: - Backend: etcd (localhost:2379)
# Output: - Swarms registered: 7
# Output: - Tasks active: 3
# Output: - Tasks completed today: 42
# Output: - Last heartbeat: 2s ago

# Step 2: Check swarm health
if coordinator swarms list
# Output:
# SWARM_ID              STATUS    BUDGET    REPUTATION    LAST_SEEN
# session-1-ndi         active    $80.00    0.95          1s ago
# session-2-webrtc      active    $120.00   0.88          2s ago
# session-4-sip         active    $50.00    0.92          1s ago
# session-7-if-bus      WARNING   $10.00    0.85          5s ago  ⚠️ Low budget

# Step 3: Check recent witness events
if witness query --limit 10
# Output: Last 10 witness events:
# [1] 10:15:00  task_claimed      IF.coordinator  trace-001
# [2] 10:14:30  capability_match  IF.governor     trace-002
# ...

# Step 4: Check cost tracking
if cost report --today
# Output: Cost Report - 2025-11-12
# Total: $45.23
# - session-2-webrtc: $18.50 (Sonnet, 1.2M tokens)
# - session-7-if-bus: $15.00 (Sonnet, 1.0M tokens)
# - session-4-sip: $8.50 (Sonnet, 567K tokens)
# - session-1-ndi: $3.23 (Haiku, 215K tokens)
```

**Success Indicators:**
- ✅ All swarms active
- ✅ Budgets healthy (>10% remaining)
- ✅ Recent heartbeats (<30s)
- ✅ No circuit breakers tripped

**Action Required:**
- 🔴 Low budget → Top up: `if governor budget add session-7-if-bus 90.00`
- 🔴 Stale heartbeat → Investigate swarm
- 🔴 Circuit breaker → Reset after fix: `if governor circuit-breaker reset session-X`

---

### Workflow 3: Deploy New Task

**Goal:** Coordinate new task across swarms
**Persona:** Operator
**Duration:** 1-2 minutes

```bash
# Step 1: Check available swarms and capabilities
if governor swarms list --capabilities
# Output: Available swarms with capabilities:
# session-2-webrtc:
#   - streaming:webrtc, integration:testing, python:async
#   Budget: $120.00, Reputation: 0.88
# ...

# Step 2: Find best match for task requirements
if governor match --capabilities "integration:testing,python:async" --max-cost 10.00
# Output: Best matches (>70% threshold):
# 1. session-2-webrtc (match: 1.00, cost: $18/hr, score: 0.85)
# 2. session-7-if-bus (match: 0.75, cost: $20/hr, score: 0.72)

# Step 3: Assign task to coordinator
if coordinator task create \
  --task-id "P0.2.6" \
  --description "IF.governor integration tests" \
  --capabilities "integration:testing,python:async" \
  --max-cost 10.00

# Output: Task P0.2.6 created (status: unclaimed)

# Step 4: Notify swarm (via pub/sub - automatic)
# Swarm will claim task when ready

# Step 5: Monitor task progress
if coordinator task status P0.2.6
# Output: Task P0.2.6 [CLAIMED]
# Owner: session-2-webrtc
# Claimed at: 10:15:23
# Estimated completion: 10:17:23 (2h estimate)

# Step 6: Watch for completion
watch -n 10 'if coordinator task status P0.2.6'
```

**Success Indicators:**
- ✅ Task created
- ✅ Task claimed by qualified swarm
- ✅ Cost within budget
- ✅ Witness logs show claim event

**Verification:**
```bash
# Verify task claim in witness log
if witness query --component IF.coordinator --event task_claimed --trace-id P0.2.6
```

---

### Workflow 4: Troubleshooting Issues

**Goal:** Diagnose and fix system issues
**Persona:** Developer
**Duration:** 10-30 minutes

#### Issue: Task Not Being Claimed

```bash
# Symptom: Task sitting unclaimed for >5 minutes

# Step 1: Check task details
if coordinator task status P0.X.Y
# Output: Task P0.X.Y [UNCLAIMED]
# Required capabilities: rust:integration, wasm:wasmtime
# Max cost: $5.00

# Step 2: Check if any swarms have required capabilities
if governor swarms list --capabilities | grep -E "rust|wasm"
# Output: (no matches)
# DIAGNOSIS: No swarms with required capabilities

# Step 3: Option A - Relax requirements
if coordinator task update P0.X.Y --capabilities "rust:basic,wasm:wasmtime"

# Step 3: Option B - Register new swarm with capabilities
if governor register session-9-rust \
  --capabilities "rust:integration,wasm:wasmtime" \
  --cost-per-hour 15.00 \
  --budget 100.00
```

#### Issue: Circuit Breaker Tripped

```bash
# Symptom: Swarm showing as circuit breaker tripped

# Step 1: Check circuit breaker status
if governor circuit-breaker status session-7-if-bus
# Output: Circuit Breaker [OPEN]
# Reason: budget_exhausted
# Failures: 5 consecutive
# Opened at: 10:10:00
# Retry after: 10:11:00 (60s cooldown)

# Step 2: Diagnose root cause
if cost report --swarm session-7-if-bus --today
# Output: session-7-if-bus spent $100.00 / $100.00 (100%)
# DIAGNOSIS: Budget exhausted

# Step 3: Add budget
if governor budget add session-7-if-bus 50.00
# Output: Budget updated: $50.00 remaining

# Step 4: Reset circuit breaker
if governor circuit-breaker reset session-7-if-bus
# Output: Circuit breaker reset (state: CLOSED)

# Step 5: Verify recovery
if coordinator swarms list | grep session-7
# Output: session-7-if-bus  active  $50.00  0.85  1s ago
```

#### Issue: Witness Hash Chain Corruption

```bash
# Symptom: Witness verify failing

# Step 1: Run verification
if witness verify
# Output: ✗ Hash chain invalid
# Error: Entry #42 hash mismatch
# Expected: abc123...
# Actual: def456...

# Step 2: Identify corruption point
if witness query --entry-id 42
# Output: [Entry #42]
# Timestamp: 2025-11-12T10:05:00Z
# Event: task_claimed
# ...
# Hash: def456... (INVALID)

# Step 3: Check surrounding entries
if witness query --entry-id 41 --entry-id 43
# Output: Entries 41 and 43 valid

# Step 4: Options for recovery
# Option A: Revert to last known good state (destructive)
if witness revert --to-entry 41
# WARNING: This will delete entries 42+

# Option B: Export for forensic analysis
if witness export --format pdf --start-id 40 --end-id 45 \
  --output corruption-report-2025-11-12.pdf

# Option C: Contact support
# Preserve evidence: cp ~/.if-witness/witness.db witness.db.corrupted
```

---

### Workflow 5: Audit & Compliance

**Goal:** Generate compliance reports
**Persona:** Auditor
**Duration:** 15-30 minutes

```bash
# Monthly Audit Workflow
# ======================

# Step 1: Verify witness integrity
if witness verify
# Output: ✓ Hash chain valid (5,432 entries)
# Output: ✓ All signatures valid
# Output: ✓ No gaps in sequence

# Step 2: Generate activity report
if witness export \
  --format pdf \
  --start-date 2025-11-01 \
  --end-date 2025-11-30 \
  --output audit-november-2025.pdf

# Step 3: Query specific events for review
# Review all task claims
if witness query \
  --component IF.coordinator \
  --event task_claimed \
  --start-date 2025-11-01 \
  --end-date 2025-11-30 \
  --format csv \
  > task-claims-november.csv

# Step 4: Review cost allocations
if cost report \
  --start-date 2025-11-01 \
  --end-date 2025-11-30 \
  --format csv \
  > cost-report-november.csv

# Step 5: Check for policy violations
if governor audit \
  --start-date 2025-11-01 \
  --end-date 2025-11-30 \
  > policy-violations-november.txt

# Step 6: Verify all tasks completed successfully
if witness query \
  --event task_completed \
  --start-date 2025-11-01 \
  --end-date 2025-11-30 \
  --count
# Output: 1,234 tasks completed in November

# Step 7: Check for anomalies
if witness query \
  --event error \
  --start-date 2025-11-01 \
  --end-date 2025-11-30
# Review any errors or failures
```

**Deliverables:**
- ✅ PDF audit report with signatures
- ✅ CSV export of task claims
- ✅ CSV export of cost allocations
- ✅ List of policy violations (if any)
- ✅ Summary statistics

---

## Error Recovery Patterns

### Pattern 1: Graceful Degradation

When a component is unavailable, provide degraded functionality:

```bash
# Example: Witness unavailable
$ if coordinator task create ...
# Output: ⚠️  Warning: IF.witness unavailable, logging disabled
# Task created successfully (ID: P0.X.Y)
# Note: Provenance logging will resume when witness is available
```

### Pattern 2: Automatic Retry with Backoff

For transient network errors:

```bash
$ if coordinator start
# Output: Connecting to etcd at localhost:2379...
# Output: ⚠️  Connection failed, retrying in 2s (attempt 1/5)
# Output: ⚠️  Connection failed, retrying in 4s (attempt 2/5)
# Output: ✓ Connected to etcd
```

### Pattern 3: Fail-Fast with Clear Recovery Steps

For configuration errors:

```bash
$ if coordinator start
# Output: ✗ Error: Invalid backend 'invalid' in config
#
# Recovery:
# 1. Edit ~/.config/infrafabric/config.yaml
# 2. Set coordinator.backend to 'etcd' or 'nats'
# 3. Run 'if coordinator start' again
#
# Example:
#   coordinator:
#     backend: etcd
```

---

## Best Practices

### 1. Use Trace IDs Consistently

**Good:**
```bash
# Use same trace-id for related operations
TRACE_ID="deploy-$(date +%Y%m%d-%H%M%S)"

if coordinator task create --trace-id $TRACE_ID ...
if witness log --trace-id $TRACE_ID --event deployment_start ...
if witness log --trace-id $TRACE_ID --event deployment_complete ...

# Later: trace entire deployment
if witness trace $TRACE_ID
```

**Bad:**
```bash
# Different trace-ids for related operations
if coordinator task create --trace-id "task-1" ...
if witness log --trace-id "log-1" ...
# Cannot trace relationship
```

### 2. Always Verify After Critical Operations

**Good:**
```bash
if witness log --event critical_operation ...
if witness verify  # Verify integrity after critical event
```

**Bad:**
```bash
if witness log --event critical_operation ...
# No verification - corruption may go unnoticed
```

### 3. Check Budget Before Expensive Operations

**Good:**
```bash
BUDGET=$(if governor budget get session-7)
if [ "$BUDGET" -lt "10.00" ]; then
  echo "Error: Insufficient budget ($BUDGET < $10.00)"
  exit 1
fi

if coordinator task create --max-cost 10.00 ...
```

**Bad:**
```bash
# Create task without budget check
if coordinator task create --max-cost 100.00 ...
# May fail mid-execution due to budget exhaustion
```

### 4. Use Filters to Reduce Output

**Good:**
```bash
# Specific query for recent errors
if witness query \
  --component IF.chassis \
  --event sandbox_failed \
  --limit 10 \
  --start-date today
```

**Bad:**
```bash
# Dump entire database and grep
if witness query | grep sandbox_failed
# Slow, memory-intensive
```

### 5. Export Before Destructive Operations

**Good:**
```bash
# Backup before cleanup
if witness export --format json --output witness-backup-$(date +%Y%m%d).json

# Now safe to clean up old entries
if witness cleanup --before 2025-01-01
```

**Bad:**
```bash
# Cleanup without backup
if witness cleanup --before 2025-01-01
# Data loss if cleanup too aggressive
```

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Ignoring Warnings

```bash
$ if coordinator task create ...
# Output: ⚠️  Warning: No swarms registered, task will remain unclaimed
# User ignores warning, task never executes
```

**Fix:** Read and act on warnings. Register swarms before creating tasks.

### ❌ Anti-Pattern 2: Hardcoded Credentials

```bash
# BAD: Hardcoded API key
if witness log --payload '{"api_key": "sk-proj-abc123..."}'
```

**Fix:** Use IF.chassis scoped credentials, never log secrets.

### ❌ Anti-Pattern 3: Polling Without Backoff

```bash
# BAD: Aggressive polling
while true; do
  if coordinator task status P0.X.Y
  sleep 0.1  # 10 requests/second
done
```

**Fix:** Use reasonable polling intervals (5-30s) or pub/sub notifications.

### ❌ Anti-Pattern 4: Not Handling Failures

```bash
# BAD: Assume success
if coordinator task create ...
if coordinator task create ...  # Will fail if first failed
```

**Fix:** Check exit codes and handle errors:
```bash
if ! if coordinator task create ...; then
  echo "Error: Task creation failed"
  exit 1
fi
```

### ❌ Anti-Pattern 5: Over-Permissive Budgets

```bash
# BAD: Unlimited budget
if governor register session-test \
  --budget 999999.00
```

**Fix:** Use realistic budgets with monitoring and alerts.

---

## Command Chaining Examples

### Chain 1: Complete Deployment Pipeline

```bash
# Atomic deployment with rollback
TRACE_ID="deploy-$(date +%s)"

if witness log --trace-id $TRACE_ID --event deployment_start && \
   if coordinator task create --trace-id $TRACE_ID --task-id deploy-ui && \
   if coordinator task create --trace-id $TRACE_ID --task-id deploy-api && \
   if coordinator task wait deploy-ui --timeout 600 && \
   if coordinator task wait deploy-api --timeout 600 && \
   if witness log --trace-id $TRACE_ID --event deployment_complete; then
  echo "✓ Deployment successful"
else
  echo "✗ Deployment failed, rolling back..."
  if coordinator task cancel deploy-ui deploy-api
  if witness log --trace-id $TRACE_ID --event deployment_failed
  exit 1
fi
```

### Chain 2: Health Check Pipeline

```bash
# Daily health check script
if coordinator status && \
   if witness verify && \
   if governor check-budgets && \
   if chassis check-sandboxes; then
  echo "✓ All systems healthy"
else
  echo "✗ Health check failed"
  # Send alert
  if alert slack --channel ops \
    --message "InfraFabric health check failed"
fi
```

---

## Progressive Disclosure

### Level 1: Beginner (Essential Commands)

```bash
if coordinator start       # Start coordinator
if coordinator status      # Check status
if witness verify          # Verify integrity
if cost report             # Check costs
```

### Level 2: Intermediate (Daily Operations)

```bash
if coordinator swarms list     # List swarms
if coordinator task create     # Create task
if governor match              # Find qualified swarms
if witness query --limit 10    # Recent events
if cost report --today         # Today's costs
```

### Level 3: Advanced (Troubleshooting & Optimization)

```bash
if coordinator task update --priority high
if governor circuit-breaker reset
if witness trace <trace-id>
if chassis sandbox inspect <sandbox-id>
if optimise cache-stats
```

### Level 4: Expert (System Administration)

```bash
if coordinator debug --latency-breakdown
if witness export --format pdf --include-signatures
if governor audit --policy-violations
if chassis limits update --sandbox-id <id> --memory-mb 1024
```

---

## Accessibility Considerations

### 1. Color-Blind Friendly Output

Use symbols in addition to colors:
```bash
✓ Success (green)
✗ Error (red)
⚠️ Warning (yellow)
ℹ️ Info (blue)
```

### 2. Screen Reader Support

Always include text descriptions:
```bash
# Good
echo "Status: active (✓)"

# Bad (screen reader just sees emoji)
echo "✓"
```

### 3. Keyboard-Only Navigation

Provide non-interactive alternatives to TUI:
```bash
# TUI for interactive users
if coordinator dashboard

# Text output for automation/accessibility
if coordinator status --format text
```

---

## Mobile/Remote Scenarios

### SSH with Slow Connection

```bash
# Prefer compact output for slow connections
if coordinator status --compact
# Output: coordinator:OK swarms:7 tasks:3 cost:$45

# Avoid verbose output
if coordinator status --verbose  # Bad over slow SSH
```

### CI/CD Pipeline

```bash
# Machine-readable output
if coordinator status --format json | jq .status
# Output: "running"

# Exit codes for automation
if coordinator status > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "Coordinator running"
fi
```

---

## Summary

**Key Principles:**
1. **Discoverability** - Users can learn through exploration
2. **Forgiveness** - Mistakes are recoverable with clear guidance
3. **Consistency** - Similar tasks use similar patterns
4. **Observability** - Current state is always clear
5. **Efficiency** - Common tasks are fast and composable

**Next Steps:**
- Review example workflows for your persona
- Practice troubleshooting patterns
- Build automation scripts using command chaining
- Provide feedback on CLI usability

---

**Feedback:** Report CLI UX issues at https://github.com/anthropics/claude-code/issues
