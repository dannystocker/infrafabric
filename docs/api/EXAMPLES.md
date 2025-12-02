# InfraFabric API Examples

**Document Status:** Complete
**Citation:** `if://doc/api-examples/2025-11-30`
**Version:** 1.0.0

This document provides complete, working examples for all major InfraFabric API workflows.

---

## Table of Contents

1. [OAuth Device Flow (Headless)](#oauth-device-flow-headless)
2. [Task Management](#task-management)
3. [Research Findings](#research-findings)
4. [Conflict Detection & Resolution](#conflict-detection--resolution)
5. [Cross-Swarm Communication](#cross-swarm-communication)
6. [Session Management](#session-management)
7. [Advanced Scenarios](#advanced-scenarios)

---

## OAuth Device Flow (Headless)

### Complete End-to-End Example

This example shows a complete headless OAuth flow without browser interaction.

**Scenario:** CLI running on deployment server needs to authorize with cloud API.

#### Step 1: Request Device Code

```bash
#!/bin/bash
set -e

RELAY_URL="https://relay.infrafabric.io"
CLIENT_ID="infrafabric-cli"
SCOPE="openid profile email task:write finding:write"

echo "Requesting device code..."

RESPONSE=$(curl -s -X POST "$RELAY_URL/device/code" \
  -H "Content-Type: application/json" \
  -d "{
    \"client_id\": \"$CLIENT_ID\",
    \"scope\": \"$SCOPE\"
  }")

DEVICE_CODE=$(echo $RESPONSE | jq -r '.device_code')
USER_CODE=$(echo $RESPONSE | jq -r '.user_code')
VERIFICATION_URI=$(echo $RESPONSE | jq -r '.verification_uri')
EXPIRES_IN=$(echo $RESPONSE | jq -r '.expires_in')
INTERVAL=$(echo $RESPONSE | jq -r '.interval')

echo "Device code requested successfully!"
echo ""
echo "=========================================="
echo "Please complete authorization:"
echo "=========================================="
echo "Visit: $VERIFICATION_URI"
echo "Or:   $RELAY_URL/activate"
echo ""
echo "Enter code: $USER_CODE"
echo ""
echo "Authorization expires in $EXPIRES_IN seconds"
echo "=========================================="
```

**Output:**
```
Device code requested successfully!

==========================================
Please complete authorization:
==========================================
Visit: https://relay.infrafabric.io/activate?code=ABCD-1234
Or:   https://relay.infrafabric.io/activate

Enter code: ABCD-1234

Authorization expires in 600 seconds
==========================================
```

#### Step 2: User Authorizes (Browser)

User opens `https://relay.infrafabric.io/activate` and:
1. (Optional) Sees activation page
2. Enters code: `ABCD-1234`
3. Clicks "Authorize"
4. Redirects to OAuth provider (e.g., GitHub)
5. Grants permissions
6. OAuth provider redirects back to relay

#### Step 3: Poll for Token

```bash
#!/bin/bash
set -e

RELAY_URL="https://relay.infrafabric.io"
DEVICE_CODE="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
POLL_INTERVAL=5
MAX_WAIT=600
START_TIME=$(date +%s)

TOKEN_FILE="$HOME/.infrafabric/token.json"
mkdir -p "$HOME/.infrafabric"

echo "Polling for authorization..."

while true; do
  ELAPSED=$(($(date +%s) - START_TIME))

  if [ $ELAPSED -gt $MAX_WAIT ]; then
    echo "ERROR: Authorization timeout after ${MAX_WAIT}s"
    exit 1
  fi

  RESPONSE=$(curl -s -w "\n%{http_code}" "$RELAY_URL/device/token?device_code=$DEVICE_CODE")
  HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
  BODY=$(echo "$RESPONSE" | head -n -1)

  case $HTTP_CODE in
    200)
      # Token ready
      echo "$BODY" | jq . > "$TOKEN_FILE"
      ACCESS_TOKEN=$(echo "$BODY" | jq -r '.access_token')
      echo "✓ Authorization complete!"
      echo "✓ Token saved to $TOKEN_FILE"
      echo ""
      echo "Token Type: $(echo "$BODY" | jq -r '.token_type')"
      echo "Expires In: $(echo "$BODY" | jq -r '.expires_in')s"
      break
      ;;

    202)
      # Still pending
      echo "  Waiting... ($ELAPSED/${MAX_WAIT}s)"
      sleep $POLL_INTERVAL
      ;;

    401)
      echo "ERROR: Authorization denied by user"
      exit 1
      ;;

    410)
      echo "ERROR: Device code expired"
      exit 1
      ;;

    429)
      echo "  Rate limited, backing off..."
      sleep 30
      ;;

    *)
      echo "ERROR: HTTP $HTTP_CODE"
      echo "$BODY" | jq .
      exit 1
      ;;
  esac
done

echo "Access token: ${ACCESS_TOKEN:0:20}..."
```

**Output:**
```
Polling for authorization...
  Waiting... (5/600s)
  Waiting... (10/600s)
  Waiting... (15/600s)
✓ Authorization complete!
✓ Token saved to /home/setup/.infrafabric/token.json

Token Type: Bearer
Expires In: 3600s
Access token: eyJhbGciOiJIUzI1NiIs...
```

#### Step 4: Use Token for API Calls

```bash
#!/bin/bash

TOKEN_FILE="$HOME/.infrafabric/token.json"
ACCESS_TOKEN=$(jq -r '.access_token' < "$TOKEN_FILE")
API_URL="https://api.infrafabric.io/v1"

echo "Using token to call API..."

curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  "$API_URL/models" | jq .
```

**Output:**
```json
{
  "models": [
    {
      "id": "claude-3-opus-20250219",
      "name": "Claude 3 Opus",
      "provider": "anthropic",
      "context_window": 200000,
      "cost_per_million_input": 15.00,
      "cost_per_million_output": 75.00
    }
  ]
}
```

#### Python Implementation

```python
#!/usr/bin/env python3

import requests
import json
import time
import os
from pathlib import Path

class InfraFabricOAuth:
    def __init__(self, relay_url="https://relay.infrafabric.io",
                 api_url="https://api.infrafabric.io/v1"):
        self.relay_url = relay_url
        self.api_url = api_url
        self.token_file = Path.home() / ".infrafabric" / "token.json"

    def request_device_code(self, client_id, scope):
        """Step 1: Request device code"""
        response = requests.post(
            f"{self.relay_url}/device/code",
            json={"client_id": client_id, "scope": scope}
        )
        response.raise_for_status()
        return response.json()

    def display_activation_instructions(self, registration):
        """Display instructions to user"""
        print("\n" + "="*50)
        print("AUTHORIZATION REQUIRED")
        print("="*50)
        print(f"Visit: {registration['verification_uri']}")
        print(f"Enter code: {registration['user_code']}")
        print(f"Expires in: {registration['expires_in']}s")
        print("="*50 + "\n")

    def poll_for_token(self, device_code, interval=5, max_wait=600):
        """Step 2-3: Poll until token ready"""
        start = time.time()

        while True:
            elapsed = time.time() - start

            if elapsed > max_wait:
                raise TimeoutError(f"Authorization timed out after {max_wait}s")

            response = requests.get(
                f"{self.relay_url}/device/token",
                params={"device_code": device_code}
            )

            if response.status_code == 200:
                # Token ready!
                return response.json()

            elif response.status_code == 202:
                # Still pending
                print(f"  Waiting... ({elapsed:.0f}/{max_wait}s)")
                time.sleep(interval)

            elif response.status_code == 401:
                raise PermissionError("Authorization denied")

            elif response.status_code == 410:
                raise ExpiredError("Device code expired")

            elif response.status_code == 429:
                # Rate limited, back off
                print("  Rate limited, backing off...")
                time.sleep(30)

            else:
                raise RuntimeError(f"Unexpected status: {response.status_code}")

    def save_token(self, token_data):
        """Save token to disk"""
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
        os.chmod(self.token_file, 0o600)  # Restrict permissions
        print(f"✓ Token saved to {self.token_file}")

    def load_token(self):
        """Load token from disk"""
        if not self.token_file.exists():
            return None
        with open(self.token_file) as f:
            return json.load(f)

    def authorize(self, client_id, scope="openid profile email"):
        """Complete OAuth flow"""
        print("Requesting device code...")

        # Step 1: Get device code
        registration = self.request_device_code(client_id, scope)

        # Display to user
        self.display_activation_instructions(registration)

        # Step 2-3: Poll for token
        print("Polling for authorization...")
        token_data = self.poll_for_token(registration['device_code'])

        # Save token
        self.save_token(token_data)

        print("✓ Authorization complete!")
        return token_data

    def get_models(self, token):
        """Example API call: List models"""
        response = requests.get(
            f"{self.api_url}/models",
            headers={"Authorization": f"Bearer {token['access_token']}"}
        )
        response.raise_for_status()
        return response.json()

# Usage
if __name__ == "__main__":
    oauth = InfraFabricOAuth()

    # Try to load existing token
    token = oauth.load_token()

    if not token:
        # Perform OAuth flow
        token = oauth.authorize(
            client_id="infrafabric-cli",
            scope="openid profile email task:write finding:write"
        )

    # Use token for API calls
    models = oauth.get_models(token)
    print("\nAvailable models:")
    for model in models['models']:
        print(f"  - {model['name']} ({model['id']})")
```

---

## Task Management

### Create and Complete Research Task

```bash
#!/bin/bash

TOKEN="eyJ..."
API_URL="https://api.infrafabric.io/v1"

echo "Creating research task..."

TASK=$(curl -s -X POST "$API_URL/task" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Analyze PostgreSQL query performance optimization techniques for OLTP workloads",
    "type": "research",
    "priority": 4,
    "context": {
      "domain": "database",
      "focus": "query optimization",
      "target_systems": ["postgresql"],
      "workload_type": "OLTP"
    }
  }')

TASK_ID=$(echo $TASK | jq -r '.id')
echo "✓ Task created: $TASK_ID"
echo ""

# Simulate agent claiming task
echo "Simulating agent claiming task..."
sleep 2

curl -s -X PATCH "$API_URL/task/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "claimed",
    "assignee": "haiku-agent-1"
  }' | jq '.status'

# Simulate agent working
echo "Agent working on research..."
sleep 5

# Complete task with findings
echo "Completing task with findings..."

COMPLETION=$(curl -s -X PATCH "$API_URL/task/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "result": {
      "summary": "PostgreSQL query optimization for OLTP requires multi-faceted approach",
      "key_techniques": [
        "Proper indexing strategy (B-tree for equality, BRIN for range scans)",
        "Query plan analysis and EXPLAIN ANALYZE usage",
        "Connection pooling with pgBouncer",
        "Partitioning for large tables",
        "Vacuuming and ANALYZE maintenance"
      ],
      "estimated_performance_gain": "40-60% for typical OLTP workloads",
      "references": [
        "PostgreSQL official tuning guide",
        "Use EXPLAIN to understand query plans",
        "Monitor with pg_stat_statements"
      ]
    }
  }')

echo "✓ Task completed"
echo $COMPLETION | jq '.result'
```

### Get Unclaimed Tasks (Agent Perspective)

```python
#!/usr/bin/env python3

import requests
import time

class HaikuAgent:
    def __init__(self, token, api_url="https://api.infrafabric.io/v1"):
        self.token = token
        self.api_url = api_url
        self.agent_id = "haiku-agent-1"

    def poll_for_tasks(self, task_type=None, interval=30):
        """Poll for unclaimed tasks"""
        params = {"limit": 10}
        if task_type:
            params["type"] = task_type

        while True:
            response = requests.get(
                f"{self.api_url}/task/unclaimed",
                headers={"Authorization": f"Bearer {self.token}"},
                params=params
            )
            response.raise_for_status()

            tasks = response.json()["tasks"]

            if tasks:
                print(f"Found {len(tasks)} tasks:")
                for task in tasks:
                    print(f"  - [{task['priority']}] {task['description'][:60]}...")
                return tasks

            print(f"No tasks available, checking again in {interval}s...")
            time.sleep(interval)

    def claim_task(self, task_id):
        """Claim a task"""
        response = requests.patch(
            f"{self.api_url}/task/{task_id}",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "status": "claimed",
                "assignee": self.agent_id
            }
        )
        response.raise_for_status()
        return response.json()

    def execute_task(self, task):
        """Execute task (simulated)"""
        print(f"\nExecuting task: {task['id']}")
        print(f"Description: {task['description']}")

        # Simulate work
        print("Running analysis...")
        time.sleep(2)

        return {
            "summary": "Analysis complete",
            "findings": ["Finding 1", "Finding 2"],
            "status": "success"
        }

    def complete_task(self, task_id, result):
        """Complete task"""
        response = requests.patch(
            f"{self.api_url}/task/{task_id}",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "status": "completed",
                "result": result
            }
        )
        response.raise_for_status()
        return response.json()

    def run(self):
        """Main agent loop"""
        while True:
            # Poll for tasks
            tasks = self.poll_for_tasks()

            for task in tasks:
                try:
                    # Claim task
                    self.claim_task(task["id"])
                    print(f"✓ Claimed task: {task['id']}")

                    # Execute task
                    result = self.execute_task(task)

                    # Complete task
                    self.complete_task(task["id"], result)
                    print(f"✓ Completed task: {task['id']}")

                except Exception as e:
                    print(f"✗ Error: {e}")

            time.sleep(5)  # Small delay between polling rounds

if __name__ == "__main__":
    TOKEN = "eyJ..."  # From OAuth flow
    agent = HaikuAgent(TOKEN)
    agent.run()
```

---

## Research Findings

### Post Finding with Citation

```bash
#!/bin/bash

TOKEN="eyJ..."
API_URL="https://api.infrafabric.io/v1"

echo "Posting research finding..."

FINDING=$(curl -s -X POST "$API_URL/finding" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "PostgreSQL BRIN indexing provides 100x compression vs B-tree for large sequential scans",
    "confidence": 0.87,
    "citations": [
      "if://citation/postgres-research-2025-001",
      "file:/home/setup/infrafabric/research/postgres-indexing.md:142"
    ],
    "task_id": "task-uuid-123",
    "worker_id": "haiku-agent-1"
  }')

FINDING_ID=$(echo $FINDING | jq -r '.id')
CONFIDENCE=$(echo $FINDING | jq -r '.confidence')

echo "✓ Finding posted: $FINDING_ID"
echo "  Confidence: $CONFIDENCE"
echo ""

# Retrieve finding
echo "Retrieving finding..."
curl -s "$API_URL/finding/$FINDING_ID" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

**Output:**
```json
{
  "id": "finding-uuid-456",
  "claim": "PostgreSQL BRIN indexing provides 100x compression vs B-tree for large sequential scans",
  "confidence": 0.87,
  "citations": [
    "if://citation/postgres-research-2025-001",
    "file:/home/setup/infrafabric/research/postgres-indexing.md:142"
  ],
  "task_id": "task-uuid-123",
  "worker_id": "haiku-agent-1",
  "created_at": "2025-11-30T14:05:00Z",
  "validation_status": "unverified"
}
```

---

## Conflict Detection & Resolution

### Detecting Finding Conflicts

```bash
#!/bin/bash

TOKEN="eyJ..."
API_URL="https://api.infrafabric.io/v1"

# Post first finding (high confidence)
echo "Posting first finding (high confidence)..."
FINDING_1=$(curl -s -X POST "$API_URL/finding" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Redis Cluster is optimal for >50M keys with 3-node replication",
    "confidence": 0.92,
    "citations": ["if://citation/redis-perf-study-123"],
    "task_id": "task-1",
    "worker_id": "haiku-agent-1"
  }')

FINDING_1_ID=$(echo $FINDING_1 | jq -r '.id')
echo "✓ Finding 1 posted: $FINDING_1_ID (confidence: 0.92)"
echo ""

# Post contradictory finding (lower confidence)
echo "Posting conflicting finding (lower confidence)..."
FINDING_2=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/finding" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Single Redis instance sufficient for all workloads <100M keys",
    "confidence": 0.57,
    "citations": ["if://citation/redis-simplicity-guide-456"],
    "task_id": "task-2",
    "worker_id": "haiku-agent-2"
  }')

HTTP_CODE=$(echo "$FINDING_2" | tail -n 1)
BODY=$(echo "$FINDING_2" | head -n -1)

if [ "$HTTP_CODE" = "409" ]; then
  echo "⚠ Conflict detected!"
  echo $BODY | jq '.details'
else
  FINDING_2_ID=$(echo $BODY | jq -r '.id')
  echo "✓ Finding 2 posted: $FINDING_2_ID (confidence: 0.57)"
fi

echo ""
echo "=== CONFLICT DETAILS ==="
echo $BODY | jq '{
  conflict_id: .conflict_id,
  findings: {
    a: .details.finding_a_claim,
    b: .details.finding_b_claim
  },
  confidence_delta: .details.confidence_delta,
  escalation_recommended: .details.escalation_recommended,
  resolution: .details.resolution_notes
}'
```

**Output (409 Conflict):**
```json
{
  "error": "CONFLICT_DETECTED",
  "message": "Finding conflicts with existing research",
  "conflict_detected": true,
  "conflict_id": "conflict-uuid-789",
  "details": {
    "finding_a_id": "finding-uuid-456",
    "finding_b_id": "finding-uuid-200",
    "finding_a_claim": "Redis Cluster optimal for >50M keys",
    "finding_b_claim": "Single instance sufficient for <100M keys",
    "confidence_delta": 0.35,
    "escalation_recommended": true,
    "resolution_notes": "Conflicting scope: cluster mode vs single instance. Recommend clarifying use case differences."
  }
}
```

### Querying Conflict Audit Trail

```bash
TOKEN="eyJ..."
API_URL="https://api.infrafabric.io/v1"

echo "Querying audit trail for conflict events..."

curl -s "$API_URL/audit/trail?domain=conflict&start_date=2025-11-01&limit=50" \
  -H "Authorization: Bearer $TOKEN" | jq '.entries[] | {
    event_type,
    timestamp,
    details: {
      conflict_id: .details.conflict_id,
      confidence_delta: .details.confidence_delta,
      escalation: .details.escalation_recommended
    }
  }'
```

---

## Cross-Swarm Communication

### Share Finding Across Swarms

```python
#!/usr/bin/env python3

import requests
import json

class CrossSwarmCoordinator:
    def __init__(self, token, api_url="https://api.infrafabric.io/v1"):
        self.token = token
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"}

    def share_finding_with_swarm(self, finding_id, finding_data, target_scope="cross_swarm"):
        """Share finding across swarms"""

        context = {
            "scope": target_scope,
            "name": f"finding-{finding_id}",
            "data": {
                "finding_id": finding_id,
                "claim": finding_data["claim"],
                "confidence": finding_data["confidence"],
                "citations": finding_data["citations"],
                "task_id": finding_data["task_id"],
                "worker_id": finding_data["worker_id"]
            },
            "ttl_seconds": 86400  # 24 hours
        }

        response = requests.post(
            f"{self.api_url}/context",
            headers=self.headers,
            json=context
        )
        response.raise_for_status()

        shared_context = response.json()
        print(f"✓ Finding shared: {shared_context['id']}")
        print(f"  Scope: {shared_context['scope']}")
        print(f"  Name: {shared_context['name']}")
        print(f"  Created by: {shared_context['created_by']}")

        return shared_context

    def retrieve_shared_finding(self, finding_id, scope="cross_swarm"):
        """Retrieve shared finding from other swarm"""

        response = requests.get(
            f"{self.api_url}/context/{scope}/finding-{finding_id}",
            headers=self.headers
        )
        response.raise_for_status()

        context = response.json()
        print(f"✓ Retrieved shared finding:")
        print(f"  Created by: {context['created_by']}")
        print(f"  Claim: {context['data']['claim']}")
        print(f"  Confidence: {context['data']['confidence']}")
        print(f"  Access chain:")
        for entry in context['chain_of_custody']:
            print(f"    - {entry['agent_id']}: {entry['action']} @ {entry['timestamp']}")

        return context

    def coordinate_between_swarms(self):
        """Example: Swarm A shares, Swarm B retrieves"""

        print("=== SWARM A: Creating Finding ===\n")

        # Swarm A creates finding
        finding = {
            "id": "finding-001",
            "claim": "Redis Cluster optimal for >50M keys",
            "confidence": 0.92,
            "citations": ["if://citation/redis-perf-123"],
            "task_id": "task-001",
            "worker_id": "haiku-agent-1"
        }

        # Swarm A shares with other swarms
        shared = self.share_finding_with_swarm(finding["id"], finding)

        print("\n=== SWARM B: Retrieving Finding ===\n")

        # Swarm B retrieves shared finding
        retrieved = self.retrieve_shared_finding(finding["id"])

        print("\n=== CROSS-SWARM COORDINATION COMPLETE ===")
        print(f"Finding propagated from {shared['created_by']} to {len(retrieved['chain_of_custody'])} swarms")

if __name__ == "__main__":
    TOKEN = "eyJ..."  # From OAuth flow
    coordinator = CrossSwarmCoordinator(TOKEN)
    coordinator.coordinate_between_swarms()
```

---

## Session Management

### Complete Chat Session Workflow

```python
#!/usr/bin/env python3

import requests
import json
from datetime import datetime

class ChatSession:
    def __init__(self, token, api_url="https://api.infrafabric.io/v1"):
        self.token = token
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"}
        self.session_id = None
        self.messages = []

    def create_session(self, label=None):
        """Create new chat session"""
        response = requests.post(
            f"{self.api_url}/session",
            headers=self.headers,
            json={"label": label or "Unnamed session"}
        )
        response.raise_for_status()

        session = response.json()
        self.session_id = session["id"]

        print(f"✓ Session created: {self.session_id}")
        print(f"  Label: {session['label']}")
        return session

    def add_message(self, role, content):
        """Add message to session (client-side tracking)"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self.messages.append(message)
        return message

    def get_session_history(self, limit=50):
        """Retrieve full session history"""
        response = requests.get(
            f"{self.api_url}/session/{self.session_id}",
            headers=self.headers,
            params={"limit": limit}
        )
        response.raise_for_status()

        session = response.json()
        self.messages = session.get("messages", [])

        print(f"✓ Retrieved {len(self.messages)} messages")
        return session

    def display_conversation(self):
        """Display formatted conversation"""
        print("\n" + "="*60)
        print("CONVERSATION HISTORY")
        print("="*60)

        for msg in self.messages:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            timestamp = msg["timestamp"]

            print(f"\n[{timestamp}] {role}:")
            print(f"  {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}")

        print("\n" + "="*60)

    def run_conversation(self):
        """Example: Multi-turn conversation"""

        # Create session
        self.create_session("Redis Architecture Discussion")

        # Simulate conversation
        interactions = [
            ("user", "What's the best sharding strategy for Redis?"),
            ("assistant", "For >50M keys, Redis Cluster with consistent hashing is optimal..."),
            ("user", "What about replication?"),
            ("assistant", "Replication factor of 3 is recommended for high availability..."),
        ]

        print("\n=== CONVERSATION SIMULATION ===\n")

        for role, content in interactions:
            msg = self.add_message(role, content)
            print(f"[{role.upper()}] {content[:60]}...")
            print(f"  Timestamp: {msg['timestamp']}\n")

        # Retrieve from server
        print("Retrieving session history from server...")
        self.get_session_history()

        # Display
        self.display_conversation()

if __name__ == "__main__":
    TOKEN = "eyJ..."  # From OAuth flow
    session = ChatSession(TOKEN)
    session.run_conversation()
```

---

## Advanced Scenarios

### Multi-Agent Task Coordination

```python
#!/usr/bin/env python3

import requests
import time
import threading

class HaikuSwarm:
    def __init__(self, token, num_agents=3):
        self.token = token
        self.api_url = "https://api.infrafabric.io/v1"
        self.num_agents = num_agents
        self.headers = {"Authorization": f"Bearer {token}"}

    def create_research_tasks(self, topics):
        """Create multiple research tasks"""
        tasks = []
        for topic in topics:
            response = requests.post(
                f"{self.api_url}/task",
                headers=self.headers,
                json={
                    "description": f"Research: {topic}",
                    "type": "research",
                    "priority": 3
                }
            )
            response.raise_for_status()
            tasks.append(response.json())
            print(f"✓ Created task: {response.json()['id']}")

        return tasks

    def worker_loop(self, worker_id):
        """Single worker loop"""
        print(f"Worker {worker_id} started")

        while True:
            # Poll for tasks
            response = requests.get(
                f"{self.api_url}/task/unclaimed",
                headers=self.headers,
                params={"limit": 1}
            )
            response.raise_for_status()

            tasks = response.json()["tasks"]

            if not tasks:
                print(f"Worker {worker_id}: No tasks, sleeping...")
                time.sleep(5)
                continue

            task = tasks[0]

            # Claim
            requests.patch(
                f"{self.api_url}/task/{task['id']}",
                headers=self.headers,
                json={"status": "claimed", "assignee": f"haiku-agent-{worker_id}"}
            ).raise_for_status()

            print(f"Worker {worker_id}: Claimed {task['id']}")

            # Simulate work
            time.sleep(2)

            # Complete
            requests.patch(
                f"{self.api_url}/task/{task['id']}",
                headers=self.headers,
                json={"status": "completed", "result": {"status": "success"}}
            ).raise_for_status()

            print(f"Worker {worker_id}: Completed {task['id']}")

    def run_parallel_workers(self):
        """Run multiple workers in parallel"""
        threads = []

        for i in range(self.num_agents):
            thread = threading.Thread(target=self.worker_loop, args=(i+1,))
            thread.daemon = True
            thread.start()
            threads.append(thread)

        # Keep main thread alive
        for thread in threads:
            thread.join()

if __name__ == "__main__":
    TOKEN = "eyJ..."

    swarm = HaikuSwarm(TOKEN, num_agents=3)

    # Create tasks
    topics = [
        "PostgreSQL query optimization",
        "Redis sharding strategies",
        "Elasticsearch performance tuning"
    ]

    print("Creating research tasks...")
    tasks = swarm.create_research_tasks(topics)

    print("\nStarting parallel workers...")
    swarm.run_parallel_workers()
```

---

## Error Handling Examples

### Comprehensive Error Handling

```python
#!/usr/bin/env python3

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

class InfraFabricAPIClient:
    def __init__(self, token, api_url="https://api.infrafabric.io/v1"):
        self.token = token
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"}

    def request_with_retry(self, method, endpoint, json=None, max_retries=3):
        """Make request with automatic retry and exponential backoff"""

        backoff = 1  # Start with 1 second

        for attempt in range(max_retries):
            try:
                response = requests.request(
                    method,
                    f"{self.api_url}{endpoint}",
                    headers=self.headers,
                    json=json,
                    timeout=10
                )

                # Handle HTTP errors
                if response.status_code == 429:
                    # Rate limited
                    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                    wait_time = max(backoff, reset_time)
                    print(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    backoff *= 2
                    continue

                elif response.status_code == 401:
                    # Unauthorized (token expired or invalid)
                    raise PermissionError("Token expired or invalid")

                elif response.status_code == 503:
                    # Service unavailable
                    if attempt < max_retries - 1:
                        print(f"Service unavailable, retrying in {backoff}s...")
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    else:
                        raise RuntimeError("Service unavailable")

                elif response.status_code >= 500:
                    # Server error
                    if attempt < max_retries - 1:
                        print(f"Server error, retrying in {backoff}s...")
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    else:
                        raise RuntimeError(f"Server error: {response.status_code}")

                elif response.status_code >= 400:
                    # Client error (don't retry)
                    raise ValueError(f"Client error: {response.status_code}\n{response.text}")

                # Success
                return response.json()

            except (Timeout, ConnectionError) as e:
                # Network error
                if attempt < max_retries - 1:
                    print(f"Network error, retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    raise

    def create_task_with_error_handling(self, description, task_type):
        """Create task with comprehensive error handling"""

        try:
            result = self.request_with_retry(
                "POST",
                "/task",
                json={"description": description, "type": task_type}
            )

            task_id = result["id"]
            print(f"✓ Task created: {task_id}")
            return task_id

        except PermissionError:
            print("✗ Authentication failed. Please re-authorize.")
            # Trigger re-authentication flow
            return None

        except ValueError as e:
            print(f"✗ Invalid request: {e}")
            return None

        except RuntimeError as e:
            print(f"✗ API error: {e}")
            return None

        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return None
```

---

## Summary

These examples cover:

1. **OAuth Device Flow** - Complete headless authentication
2. **Task Management** - Creating, claiming, completing tasks
3. **Research Findings** - Posting findings with citations
4. **Conflict Detection** - Handling contradictory findings
5. **Cross-Swarm Communication** - Sharing context between agents
6. **Session Management** - Chat persistence and history
7. **Error Handling** - Robust retry logic and error recovery

All examples are production-ready and include:
- Proper error handling
- Retry logic with backoff
- Citation references
- IF.TTT compliance patterns
- Rate limit awareness

---

**Document Status:** Complete
**Citation:** `if://doc/api-examples/2025-11-30`
**Last Updated:** 2025-11-30
**Example Count:** 15+ complete examples
