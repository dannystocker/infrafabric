# Redis Bus Schema Usage Guide

This document provides practical examples for using the Redis Bus schema implementation for IF.swarm.s2 communication.

Citation: if://citation/redis-bus-usage-examples
Reference: IF-SWARM-S2-COMMS.md

## Table of Contents
1. [Setup and Initialization](#setup-and-initialization)
2. [Task Management](#task-management)
3. [Finding Management](#finding-management)
4. [Context Sharing](#context-sharing)
5. [Conflict Detection](#conflict-detection)
6. [Escalation and Error Handling](#escalation-and-error-handling)
7. [Swarm Coordination](#swarm-coordination)
8. [Complete Workflow Example](#complete-workflow-example)

---

## Setup and Initialization

```python
from redis_bus_schema import RedisBusClient, Task, Finding, Context, SessionSummary

# Initialize Redis Bus client
client = RedisBusClient(
    host="localhost",
    port=6379,
    db=0,
    password=None  # Set if Redis requires authentication
)

# Verify connection health
assert client.health_check(), "Redis Bus connection failed!"

# Set agent ID for custody tracking
client.agent_id = "haiku-1"
```

---

## Task Management

### Scenario 1: Claiming a Task

```python
from redis_bus_schema import Task, TaskStatus

# Create a new task
task = Task(
    description="Research revenue variance patterns in Q3 2024",
    type="research",
    data={
        "domains": ["healthcare", "finance"],
        "date_range": "2024-Q3",
        "analysis_depth": "medium"
    }
)

# Claim the task
success = client.claim_task(
    task=task,
    assignee="haiku-1",
    agent_id="haiku-1"
)

if success:
    print(f"Task {task.id} claimed successfully")
else:
    print(f"Task {task.id} was already claimed by another agent")
```

### Scenario 2: Finding Idle Work

```python
# Agent is idle, looking for work
unassigned = client.get_unassigned_task()

if unassigned:
    print(f"Found unassigned task: {unassigned.description}")

    # Claim it
    client.claim_task(
        task=unassigned,
        assignee="haiku-2",
        agent_id="haiku-2"
    )
else:
    print("No unassigned tasks available")
```

### Scenario 3: Releasing a Blocked Task

```python
# Task is blocked, release it for another agent to pick up
released = client.release_task(
    task_id=task.id,
    agent_id="haiku-1"
)

if released:
    print(f"Released task {task.id} back to pending")
```

---

## Finding Management

### Scenario 4: Posting Research Findings

```python
from redis_bus_schema import Finding, SpeechAct

# Post a high-confidence finding
finding = Finding(
    claim="Revenue variance in healthcare sector correlates with policy changes",
    confidence=0.92,  # 92% confidence
    citations=[
        "if://citation/uuid-healthcare-policy-2024-Q3",
        "file:///research/q3_analysis.json:142-156",
        "http://example.com/research/healthcare-trends"
    ],
    worker_id="haiku-1",
    task_id=task.id,
    speech_act=SpeechAct.INFORM
)

client.post_finding(
    finding=finding,
    agent_id="haiku-1"
)

print(f"Posted finding {finding.id} with {finding.confidence*100:.0f}% confidence")
```

### Scenario 5: Posting an Uncertain Finding

```python
# Post a lower-confidence finding for review
uncertain_finding = Finding(
    claim="Preliminary correlation detected between marketing spend and Q4 revenue",
    confidence=0.35,  # Low confidence, needs verification
    citations=["file:///data/preliminary_analysis.csv:1-50"],
    worker_id="haiku-3",
    task_id=task.id,
    speech_act=SpeechAct.INFORM  # Still INFORM, but low confidence
)

client.post_finding(uncertain_finding)

print(f"Posted uncertain finding (confidence={uncertain_finding.confidence})")
```

### Scenario 6: Retrieving Findings for a Task

```python
# Get all findings for a specific task
findings = client.get_findings_for_task(task.id)

print(f"Retrieved {len(findings)} findings for task {task.id}:")
for finding in findings:
    status = "HIGH" if finding.confidence >= 0.8 else "MEDIUM" if finding.confidence >= 0.5 else "LOW"
    print(f"  - [{status}] {finding.claim} (confidence={finding.confidence})")
```

---

## Context Sharing

### Scenario 7: Creating Shared Context

```python
from redis_bus_schema import Context

# Create shared context for task coordination
context = Context(
    scope="task",
    name=task.id,
    notes="Key observations: Healthcare policy changes align with Q3 variance spike",
    timeline=[
        ("2025-11-30T10:00:00", "Initiated research on revenue variance"),
        ("2025-11-30T10:15:00", "Found preliminary healthcare correlation"),
        ("2025-11-30T10:30:00", "Requested additional data sources"),
    ],
    topics=["healthcare", "policy-change", "revenue-variance"],
    shared_data={
        "affected_regions": ["US", "EU"],
        "confidence_threshold": 0.75,
        "peer_verification_needed": True
    }
)

client.share_context(context, agent_id="haiku-1")

print(f"Shared context for {context.key()}")
```

### Scenario 8: Reading Shared Context

```python
# Read context shared by another agent
shared = client.get_context(
    scope="task",
    name=task.id
)

if shared:
    print(f"Context notes: {shared.notes}")
    print(f"Topics: {', '.join(shared.topics)}")
    print(f"Peer verification needed: {shared.shared_data.get('peer_verification_needed')}")
```

---

## Conflict Detection

### Scenario 9: Detecting Finding Conflicts

```python
# Detect conflicting findings on the same task
conflicts = client.detect_finding_conflicts(
    task_id=task.id,
    conflict_threshold=0.2  # 20% confidence delta = conflict
)

if conflicts:
    print(f"Found {len(conflicts)} conflicting findings:")
    for f1, f2 in conflicts:
        delta = abs(f1.confidence - f2.confidence) * 100
        print(f"  - {f1.claim}")
        print(f"    Confidence: {f1.confidence*100:.0f}% vs {f2.confidence*100:.0f}% (delta: {delta:.0f}%)")
        print(f"  - {f2.claim}")
        print()
else:
    print("No conflicting findings detected")
```

---

## Escalation and Error Handling

### Scenario 10: Escalating Critical Uncertainty

```python
from redis_bus_schema import TaskStatus

# Escalate a finding with critical uncertainty (confidence < 0.2)
critical_finding = Finding(
    claim="Potential data inconsistency detected - manual review required",
    confidence=0.05,  # Very low confidence
    citations=["file:///data/inconsistency_report.log:234"],
    worker_id="haiku-2",
    task_id=task.id,
    speech_act=SpeechAct.ESCALATE
)

client.escalate_to_human(
    task_id=task.id,
    reason="Data quality issue detected - conflicting sources suggest possible data corruption",
    findings=[critical_finding],
    agent_id="haiku-2"
)

print("Task escalated to human review")
```

---

## Swarm Coordination

### Scenario 11: Registering a Swarm

```python
from redis_bus_schema import SwarmRegistry

# Register the active swarm with coordinator and workers
registry = SwarmRegistry(
    id="infrafabric_2025-11-30",
    agents=[
        {"id": "haiku-1", "role": "worker", "status": "active"},
        {"id": "haiku-2", "role": "worker", "status": "active"},
        {"id": "haiku-3", "role": "worker", "status": "idle"},
    ],
    roles={
        "coordinator": "sonnet-1",
        "leader": "sonnet-1",
    },
    artifacts=[
        "/output/findings_summary.json",
        "/output/conflict_analysis.csv",
        "/output/metrics.json"
    ]
)

client.register_swarm(registry, agent_id="sonnet-1")

print(f"Registered swarm: {registry.id}")
print(f"Active agents: {len(registry.agents)}")
```

### Scenario 12: Recording Session Summary

```python
from redis_bus_schema import SessionSummary

# Record session summary after completion
session = SessionSummary(
    date="2025-11-30",
    label="haiku_swarm",
    summary="Completed research on Q3 2024 revenue variance. Found 12 findings with 8 high-confidence (>0.8). Escalated 2 conflicts to human review.",
    metrics={
        "tasks_processed": 1,
        "findings_posted": 12,
        "high_confidence_count": 8,
        "medium_confidence_count": 3,
        "low_confidence_count": 1,
        "conflicts_detected": 2,
        "escalations": 2,
        "total_agents": 3,
        "execution_time_seconds": 1847,
        "if_ttt_score": 4.8
    }
)

client.record_session_summary(session, agent_id="sonnet-1")

print(f"Recorded session summary for {session.date}:{session.label}")
```

---

## Complete Workflow Example

```python
"""
Complete S2 swarm workflow: research task from start to finish.
Demonstrates task claiming, finding posting, conflict detection, and escalation.
"""

def run_swarm_research_workflow():
    """End-to-end research workflow on Redis Bus."""

    # 1. CREATE AND CLAIM TASK
    print("\n=== PHASE 1: Task Creation ===")
    main_task = Task(
        description="Comprehensive analysis of ERP system adoption patterns",
        type="research",
        data={"scope": "global", "industries": ["manufacturing", "retail"]}
    )

    client.claim_task(main_task, "haiku-1", "haiku-1")
    print(f"Claimed task {main_task.id}")

    # 2. POST INITIAL FINDINGS
    print("\n=== PHASE 2: Research Execution ===")
    findings_data = [
        ("ERP adoption in manufacturing grew 15% YoY", 0.88),
        ("Retail sector shows slower adoption (8% growth)", 0.82),
        ("Cloud-based ERPs capturing market share from on-prem", 0.91),
        ("Implementation costs correlate with organization size", 0.79),
    ]

    for claim, confidence in findings_data:
        finding = Finding(
            claim=claim,
            confidence=confidence,
            worker_id="haiku-1",
            task_id=main_task.id,
            citations=[f"if://citation/erp-study-2025"]
        )
        client.post_finding(finding)

    # 3. SHARE CONTEXT
    print("\n=== PHASE 3: Context Sharing ===")
    context = Context(
        scope="task",
        name=main_task.id,
        notes="Primary sources: Gartner Magic Quadrant 2025, IDC MarketScape",
        topics=["ERP", "digital-transformation", "adoption-metrics"],
        shared_data={"peer_review_complete": True}
    )
    client.share_context(context)
    print(f"Context shared for {context.key()}")

    # 4. DETECT CONFLICTS
    print("\n=== PHASE 4: Conflict Analysis ===")
    conflicts = client.detect_finding_conflicts(main_task.id, 0.15)
    if conflicts:
        print(f"Detected {len(conflicts)} potential conflicts")
        for f1, f2 in conflicts:
            print(f"  Conflict: {f1.confidence:.2f} vs {f2.confidence:.2f}")
    else:
        print("No significant conflicts detected")

    # 5. RECORD SESSION
    print("\n=== PHASE 5: Session Summary ===")
    session = SessionSummary(
        date="2025-11-30",
        label="erp_analysis_swarm",
        summary="Completed ERP adoption research with high-confidence findings",
        metrics={
            "findings_count": len(findings_data),
            "avg_confidence": sum(c for _, c in findings_data) / len(findings_data),
            "conflicts": len(conflicts),
        }
    )
    client.record_session_summary(session)
    print(f"Session recorded: {session.metrics}")

    print("\n=== WORKFLOW COMPLETE ===\n")


# Run the workflow
# run_swarm_research_workflow()
```

---

## Key Design Patterns

### Pattern 1: Task Handoff Between Agents
```python
# Agent A is blocked, hands off to Agent B
client.release_task(task.id, agent_id="haiku-1")
# ... Agent B picks it up
client.claim_task(task, "haiku-2", agent_id="haiku-2")
```

### Pattern 2: Evidence-Based Findings
```python
# Always include citations (if:// URIs preferred per IF.TTT)
finding = Finding(
    claim="...",
    confidence=0.85,
    citations=[
        "if://citation/uuid-12345",
        "file://research/evidence.json:42-68"
    ]
)
```

### Pattern 3: Escalation Chain
```python
# Low confidence triggers escalation
if finding.confidence < 0.2:
    client.escalate_to_human(
        task_id=task.id,
        reason=f"Confidence too low: {finding.confidence}",
        findings=[finding]
    )
```

---

## TTL (Time-to-Live) Configuration

```python
# Tasks expire in 24 hours by default
task = Task(..., ttl_seconds=86400)

# Short-lived findings (same as task)
finding = Finding(..., ttl_seconds=86400)

# Long-term context persists longer
context = Context(...)  # Client sets 24-hour TTL on storage

# Session summaries kept for 30 days
# Swarm registries kept for 7 days
```

---

## Error Handling

```python
# Check if task exists before getting
task_key = f"task:{task_id}"
if not client.redis_conn.exists(task_key):
    print(f"Task {task_id} not found")

# Validate finding confidence before posting
try:
    finding = Finding(claim="...", confidence=1.5)  # Will raise ValueError
except ValueError as e:
    print(f"Invalid finding: {e}")
```

---

## Performance Notes

- Redis Bus latency: ~0.071 ms per operation (140× faster than JSONL)
- Suitable for parallel Haiku swarms (N agents competing for tasks)
- Key scan operations use cursor for memory efficiency
- All writes include packet envelopes (minimal overhead)

---

## References

- IF-SWARM-S2-COMMS.md: Complete S2 architecture specification
- redis_bus_schema.py: Implementation source code
- REDIS_BUS_SCHEMA_REFERENCE.md: API reference documentation
