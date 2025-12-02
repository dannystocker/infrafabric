# InfraFabric API Reference

**Document Status:** Complete
**Citation:** `if://doc/api-reference/2025-11-30`
**Version:** 1.0.0
**Last Updated:** 2025-11-30

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Error Handling](#error-handling)
5. [OAuth Device Flow](#oauth-device-flow)
6. [Task Management](#task-management)
7. [Findings & Conflict Detection](#findings--conflict-detection)
8. [Context Sharing](#context-sharing)
9. [Session Management](#session-management)
10. [Models](#models)
11. [Audit Trail](#audit-trail)
12. [Versioning & Deprecation](#versioning--deprecation)

---

## Overview

InfraFabric API provides a comprehensive interface for:

- **OAuth 2.0 Device Flow** - Headless CLI authentication (RFC 8628)
- **Task Management** - Swarm work distribution and claiming
- **Research Findings** - Aggregation with automatic conflict detection
- **Cross-Swarm Communication** - Context sharing and coordination
- **Session Persistence** - Chat history and state management
- **IF.TTT Traceability** - Complete audit trail with citations

### API Endpoints

**Production:** `https://api.infrafabric.io/v1`
**Development:** `http://localhost:8000/v1`
**OAuth Relay:** `https://relay.infrafabric.io`

### Supported Formats

- **Request:** JSON (application/json)
- **Response:** JSON with streaming SSE support
- **Dates:** ISO 8601 format with timezone

---

## Authentication

### Bearer Token (JWT)

All authenticated endpoints require Bearer token in Authorization header:

```bash
curl -H "Authorization: Bearer eyJ..." https://api.infrafabric.io/v1/task
```

### Obtaining Tokens

**OAuth Device Flow (Recommended for CLI):**
See [OAuth Device Flow](#oauth-device-flow) section.

**Password Grant (Development):**
```bash
curl -X POST https://api.infrafabric.io/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=user&password=pass&client_id=client"
```

### Token Refresh

Refresh tokens are valid for 7 days. Use to obtain new access tokens without re-authenticating:

```bash
curl -X POST https://api.infrafabric.io/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "..."}'
```

### Scope Management

Tokens support granular scopes:

| Scope | Permission |
|-------|-----------|
| `openid` | Basic identification |
| `profile` | User profile access |
| `email` | Email address access |
| `task:read` | Read tasks |
| `task:write` | Create and claim tasks |
| `finding:read` | Read findings |
| `finding:write` | Post findings |
| `audit:read` | Access audit trail |
| `admin` | Full access |

---

## Rate Limiting

InfraFabric API uses token-bucket rate limiting per IP address.

### Default Limits

| Endpoint Group | Limit | Window |
|---|---|---|
| Authentication | 10 requests | 1 minute |
| Device code polling | 10 requests | 1 minute |
| Task operations | 100 requests | 1 minute |
| Finding operations | 50 requests | 1 minute |
| Audit queries | 20 requests | 1 minute |

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1701350400
```

When exceeded: **HTTP 429 Too Many Requests**

```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded. Retry after 42 seconds.",
  "reset_at": "2025-11-30T14:30:00Z"
}
```

### Backoff Strategy

Recommended exponential backoff for polling:

```python
import time
import random

attempt = 0
while attempt < 10:
    try:
        response = poll_token(device_code)
        return response
    except RateLimitError as e:
        wait_time = (2 ** attempt) + random.uniform(0, 1)
        time.sleep(min(wait_time, 60))  # Cap at 60s
        attempt += 1
```

---

## Error Handling

### Standard Error Response

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "error_details"
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### HTTP Status Codes

| Code | Meaning | Retry? |
|------|---------|--------|
| 200 | OK | No |
| 201 | Created | No |
| 202 | Accepted (pending) | Yes (keep polling) |
| 400 | Bad Request | No |
| 401 | Unauthorized | No (refresh token) |
| 403 | Forbidden | No |
| 404 | Not Found | No |
| 409 | Conflict | Case-dependent |
| 410 | Gone (expired) | No (restart flow) |
| 429 | Rate Limited | Yes (exponential backoff) |
| 500 | Server Error | Yes (exponential backoff) |
| 503 | Service Unavailable | Yes (exponential backoff) |

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|-----------|
| `INVALID_REQUEST` | Malformed request | Check request format |
| `INVALID_CLIENT_ID` | Unknown client | Verify client_id |
| `INVALID_DEVICE_CODE` | Device code not found | Request new code |
| `INVALID_USER_CODE` | User code invalid format | Check format XXXX-XXXX |
| `EXPIRED_DEVICE_CODE` | Device code >10 min old | Request new code |
| `AUTHORIZATION_DENIED` | User rejected authorization | Try again with new code |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry |
| `RESOURCE_NOT_FOUND` | Resource doesn't exist | Check resource ID |
| `CONFLICT_DETECTED` | Finding conflict exists | See conflict details |
| `INTERNAL_SERVER_ERROR` | Server error | Retry with backoff |

---

## OAuth Device Flow

### Overview

Device authorization grant flow for headless environments (RFC 8628).

**Flow Diagram:**
```
┌─────────┐                         ┌──────────┐
│   CLI   │                         │ Relay    │
└────┬────┘                         └────┬─────┘
     │ 1. Request device code            │
     ├────────────────────────────────────>
     │                          2. device_code + user_code
     <────────────────────────────────────┤
     │
     │ 3. Display to user:
     │    "Visit https://relay.infrafabric.io/activate"
     │    "Enter code: ABCD-1234"
     │
     │ 4. Poll for token (every 5s)
     ├────────────────────────────────────>
     │                          5. 202 Pending
     <────────────────────────────────────┤
     │    [User opens browser, authorizes, OAuth redirects back]
     │
     │ 4. Poll for token (retry)
     ├────────────────────────────────────>
     │                          5. 200 OK + token
     <────────────────────────────────────┤
```

### Step 1: Request Device Code

**POST /device/code**

```bash
curl -X POST https://relay.infrafabric.io/device/code \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "infrafabric-cli",
    "scope": "openid profile email"
  }'
```

**Response (200 OK):**
```json
{
  "device_code": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_code": "ABCD-1234",
  "verification_uri": "https://relay.infrafabric.io/activate?code=ABCD-1234",
  "expires_in": 600,
  "interval": 5
}
```

### Step 2: Display Instructions to User

```
Visit: https://relay.infrafabric.io/activate?code=ABCD-1234
Enter code: ABCD-1234
```

Or visit `https://relay.infrafabric.io/activate` and manually enter code.

### Step 3: Poll for Token

**GET /device/token**

```bash
#!/bin/bash
DEVICE_CODE="eyJ..."
INTERVAL=5
EXPIRES_IN=600
START=$(date +%s)

while true; do
  RESPONSE=$(curl -s https://relay.infrafabric.io/device/token?device_code=$DEVICE_CODE)

  STATUS=$(echo $RESPONSE | jq -r '.status')

  if [ "$STATUS" = "success" ]; then
    ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
    echo "Authorization complete!"
    echo "Access token: $ACCESS_TOKEN"
    break
  elif [ "$STATUS" = "denied" ]; then
    echo "Authorization denied"
    exit 1
  elif [ "$STATUS" = "pending" ]; then
    echo "Waiting for authorization..."
    sleep $INTERVAL
  fi

  # Check expiry
  NOW=$(date +%s)
  if [ $((NOW - START)) -gt $EXPIRES_IN ]; then
    echo "Device code expired"
    exit 1
  fi
done
```

**Response (202 Accepted - pending):**
```json
{
  "status": "pending"
}
```

**Response (200 OK - authorized):**
```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "abc...",
  "scope": "openid profile email",
  "status": "success"
}
```

### Security Considerations

- **HTTPS Required:** Always use HTTPS (TLS 1.3+)
- **State Parameter:** Automatically included for CSRF protection
- **Token Expiry:** Access tokens expire after 1 hour
- **Refresh Tokens:** Valid for 7 days
- **Rate Limiting:** 10 device code requests per minute per IP
- **Device Code:** Cryptographically random (32-byte entropy)

---

## Task Management

### Task Lifecycle

```
Created (pending)
    ↓
Claimed (in_progress) ← Agent polls /task/unclaimed
    ↓
Completed or Escalated
    ↓
Released
```

### Create Task

**POST /task**

```bash
curl -X POST https://api.infrafabric.io/v1/task \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Research optimal Redis sharding strategies for 100M+ keys",
    "type": "research",
    "priority": 3,
    "context": {
      "domain": "infrastructure",
      "target_systems": ["redis"]
    }
  }'
```

**Response (201 Created):**
```json
{
  "id": "task-uuid-123",
  "description": "Research optimal Redis sharding strategies...",
  "type": "research",
  "status": "pending",
  "priority": 3,
  "created_at": "2025-11-30T14:00:00Z",
  "updated_at": "2025-11-30T14:00:00Z",
  "citation": "if://citation/task-uuid-123"
}
```

### Get Unclaimed Tasks

**GET /task/unclaimed**

Used by Haiku agents to discover work:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://api.infrafabric.io/v1/task/unclaimed?type=research&limit=5
```

**Response (200 OK):**
```json
{
  "tasks": [
    {
      "id": "task-uuid-123",
      "description": "Research Redis sharding...",
      "type": "research",
      "status": "pending",
      "priority": 3,
      "created_at": "2025-11-30T14:00:00Z"
    },
    {
      "id": "task-uuid-124",
      "description": "Analyze PostgreSQL query performance...",
      "type": "analysis",
      "status": "pending",
      "priority": 4,
      "created_at": "2025-11-30T14:05:00Z"
    }
  ],
  "total": 2
}
```

### Claim Task

**PATCH /task/{taskId}**

```bash
curl -X PATCH https://api.infrafabric.io/v1/task/task-uuid-123 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "claimed",
    "assignee": "haiku-agent-1"
  }'
```

**Response (200 OK):**
```json
{
  "id": "task-uuid-123",
  "status": "claimed",
  "assignee": "haiku-agent-1",
  "updated_at": "2025-11-30T14:01:00Z"
}
```

### Complete Task

**PATCH /task/{taskId}**

```bash
curl -X PATCH https://api.infrafabric.io/v1/task/task-uuid-123 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "result": {
      "summary": "Found that Redis Cluster with consistent hashing is optimal",
      "key_findings": [
        "Cluster mode handles up to 1B+ keys",
        "Replication factor 3 recommended",
        "Slot migration <1ms per operation"
      ]
    }
  }'
```

### Task Parameters Reference

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | string | Yes | Task description for agents |
| `type` | enum | Yes | `research`, `analysis`, `implementation`, `validation` |
| `priority` | integer | No | 1-5 (1=lowest, 5=highest), default 3 |
| `context` | object | No | Additional metadata |
| `status` | enum | No | `pending`, `claimed`, `completed`, `escalated`, `failed` |
| `assignee` | string | No | Agent ID claiming task |
| `result` | object | No | Task result (when completed) |

---

## Findings & Conflict Detection

### Post Finding

**POST /finding**

```bash
curl -X POST https://api.infrafabric.io/v1/finding \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Redis Cluster is optimal for >50M keys with 3-node replication",
    "confidence": 0.92,
    "citations": [
      "if://citation/redis-perf-study-123",
      "file:/home/setup/infrafabric/research/redis.md:45"
    ],
    "task_id": "task-uuid-123",
    "worker_id": "haiku-agent-1"
  }'
```

**Response (201 Created):**
```json
{
  "id": "finding-uuid-456",
  "claim": "Redis Cluster is optimal for >50M keys...",
  "confidence": 0.92,
  "citations": [...],
  "task_id": "task-uuid-123",
  "worker_id": "haiku-agent-1",
  "created_at": "2025-11-30T14:05:00Z",
  "validation_status": "unverified"
}
```

### Conflict Detection

When a new finding contradicts existing findings, system returns 409 Conflict:

**Response (409 Conflict):**
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
    "finding_b_claim": "Single Redis instance optimal for <100M keys",
    "confidence_delta": 0.35,
    "escalation_recommended": true,
    "resolution_notes": "Conflicting scope: cluster mode vs single instance"
  }
}
```

### Query Audit Trail for Findings

**GET /audit/trail?domain=finding&start_date=2025-11-01**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.infrafabric.io/v1/audit/trail?domain=finding&limit=20"
```

**Response (200 OK):**
```json
{
  "entries": [
    {
      "id": "audit-uuid-123",
      "event_type": "finding_posted",
      "domain": "research",
      "timestamp": "2025-11-30T14:05:00Z",
      "component": "task-manager",
      "details": {
        "finding_id": "finding-uuid-456",
        "confidence": 0.92,
        "conflict_detected": false
      },
      "citation": "if://citation/audit-entry-123",
      "confidence": 0.95
    }
  ],
  "total": 1
}
```

### Finding Parameters Reference

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `claim` | string | Yes | The research finding/claim |
| `confidence` | number | Yes | Confidence score [0.0-1.0] |
| `citations` | array | Yes | Source references (if://citation/* or file:line) |
| `task_id` | string | No | Associated task ID |
| `worker_id` | string | No | Agent ID that created finding |

---

## Context Sharing

### Share Context

**POST /context**

For cross-swarm coordination:

```bash
curl -X POST https://api.infrafabric.io/v1/context \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "cross_swarm",
    "name": "finding-uuid-456",
    "data": {
      "finding_summary": "Redis Cluster optimal for 50M+ keys",
      "implications": ["Scale horizontally", "Use consistent hashing"],
      "needs_review": false
    },
    "ttl_seconds": 3600
  }'
```

**Response (201 Created):**
```json
{
  "id": "context-uuid-789",
  "scope": "cross_swarm",
  "name": "finding-uuid-456",
  "data": {...},
  "created_by": "haiku-agent-1",
  "created_at": "2025-11-30T14:10:00Z",
  "chain_of_custody": [
    {
      "agent_id": "haiku-agent-1",
      "action": "created",
      "timestamp": "2025-11-30T14:10:00Z"
    }
  ]
}
```

### Retrieve Shared Context

**GET /context/{scope}/{name}**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://api.infrafabric.io/v1/context/cross_swarm/finding-uuid-456
```

**Response (200 OK):**
```json
{
  "id": "context-uuid-789",
  "scope": "cross_swarm",
  "name": "finding-uuid-456",
  "data": {
    "finding_summary": "Redis Cluster optimal for 50M+ keys",
    ...
  },
  "created_by": "haiku-agent-1",
  "created_at": "2025-11-30T14:10:00Z",
  "chain_of_custody": [
    {
      "agent_id": "haiku-agent-1",
      "action": "created",
      "timestamp": "2025-11-30T14:10:00Z"
    },
    {
      "agent_id": "haiku-agent-2",
      "action": "accessed",
      "timestamp": "2025-11-30T14:15:00Z"
    }
  ]
}
```

### Context Scopes

| Scope | Visibility | Purpose |
|-------|-----------|---------|
| `cross_swarm` | All swarms | Sharing findings between swarms |
| `session` | Single session | Session-specific shared state |
| `global` | All services | Application-wide knowledge base |

---

## Session Management

### Create Session

**POST /session**

```bash
curl -X POST https://api.infrafabric.io/v1/session \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "Redis Architecture Discussion"
  }'
```

**Response (201 Created):**
```json
{
  "id": "session-uuid-abc123",
  "created_at": "2025-11-30T14:00:00Z",
  "label": "Redis Architecture Discussion",
  "message_count": 0
}
```

### Get Session with History

**GET /session/{sessionId}**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.infrafabric.io/v1/session/session-uuid-abc123?limit=50"
```

**Response (200 OK):**
```json
{
  "id": "session-uuid-abc123",
  "created_at": "2025-11-30T14:00:00Z",
  "label": "Redis Architecture Discussion",
  "message_count": 2,
  "messages": [
    {
      "role": "user",
      "content": "What's the best sharding strategy for Redis?",
      "timestamp": "2025-11-30T14:05:00Z"
    },
    {
      "role": "assistant",
      "content": "For >50M keys, Redis Cluster with consistent hashing...",
      "timestamp": "2025-11-30T14:05:30Z"
    }
  ]
}
```

### Session Parameters Reference

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Unique session identifier |
| `created_at` | datetime | Session creation timestamp |
| `label` | string | Optional session label |
| `message_count` | integer | Number of messages |
| `messages` | array | Chat message history |
| `limit` | query param | Max messages to return (default 50) |

---

## Models

### List Available Models

**GET /models**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://api.infrafabric.io/v1/models
```

**Response (200 OK):**
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
    },
    {
      "id": "deepseek-v2-1-5b",
      "name": "DeepSeek v2.1",
      "provider": "deepseek",
      "context_window": 128000,
      "cost_per_million_input": 0.14,
      "cost_per_million_output": 0.28
    },
    {
      "id": "ollama:llama2",
      "name": "Llama 2 (Local)",
      "provider": "ollama",
      "context_window": 4096,
      "cost_per_million_input": 0.00,
      "cost_per_million_output": 0.00
    }
  ]
}
```

### Model Provider Details

| Provider | Models | Notes |
|----------|--------|-------|
| `anthropic` | Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku | Production-grade, high cost |
| `deepseek` | DeepSeek v2.1 | Open-weight, low cost |
| `ollama` | Llama 2, Mistral, others | Local execution, zero cost |

---

## Audit Trail

### Query Audit Trail

**GET /audit/trail**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.infrafabric.io/v1/audit/trail?domain=security&start_date=2025-11-01&limit=100"
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `domain` | enum | `security`, `decision`, `escalation`, `all` (default: all) |
| `start_date` | date | YYYY-MM-DD format |
| `end_date` | date | YYYY-MM-DD format |
| `limit` | integer | Max entries (default: 100, max: 1000) |

**Response (200 OK):**
```json
{
  "entries": [
    {
      "id": "audit-uuid-123",
      "event_type": "security_event",
      "domain": "security",
      "timestamp": "2025-11-30T13:45:00Z",
      "component": "emotion_filter",
      "details": {
        "trigger": "harmful_stereotype_detected",
        "confidence": 0.98,
        "blocked_content": "..."
      },
      "citation": "if://citation/audit-entry-123",
      "confidence": 0.99
    }
  ],
  "total": 1
}
```

### Get Citation Details

**GET /citation/{citationId}**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://api.infrafabric.io/v1/citation/if%3A%2F%2Fcitation%2Faudit-entry-123
```

**Response (200 OK):**
```json
{
  "id": "if://citation/audit-entry-123",
  "type": "decision",
  "domain": "security",
  "created_at": "2025-11-30T13:45:00Z",
  "status": "verified",
  "sources": [
    "file:/home/setup/infrafabric/src/core/security/emotion_output_filter.py:72",
    "if://doc/IF_EMOTION_SANDBOX.md:250"
  ],
  "metadata": {
    "guardian_votes": {
      "ethical_guardian": "approved",
      "emotion_guardian": "approved"
    },
    "consensus_percentage": 100
  }
}
```

### Citation Types

| Type | Description |
|------|-------------|
| `code` | Code change or implementation |
| `document` | Documentation reference |
| `decision` | Guardian Council decision |
| `finding` | Research finding |
| `claim` | Tracked claim or hypothesis |
| `test_run` | Test execution or validation |
| `improvement` | System improvement or optimization |

### Citation Statuses

| Status | Meaning |
|--------|---------|
| `unverified` | Initial claim, not yet reviewed |
| `verified` | Passed validation, trusted |
| `disputed` | Multiple conflicting sources |
| `revoked` | Superseded or incorrect |

---

## Versioning & Deprecation

### API Version Strategy

Current version: **v1** (URL: `/v1/`)

Versioning follows semantic versioning with support windows:

- **v1.x.x:** Current (indefinite support)
- **v0.x.x:** Deprecated (support ended 2025-09-01)

### Breaking Changes

Breaking changes are released as new major versions only. Examples:

- ✅ Adding new optional parameter
- ✅ Adding new response field
- ❌ Removing parameter (breaking)
- ❌ Changing response format (breaking)
- ❌ Changing error codes (breaking)

### Deprecation Process

1. **Announcement:** 6-month notice in API changelog
2. **Sunset Date:** Published deprecation date
3. **Removal:** Endpoint stops responding with 410 Gone

---

## Implementation Guide

### Client Library

Recommended HTTP client libraries:

**Python:**
```bash
pip install requests
```

**JavaScript/Node:**
```bash
npm install axios
```

**Go:**
```bash
go get github.com/go-resty/resty/v2
```

### SDK Examples

**Python:**
```python
import requests

class InfraFabricAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.infrafabric.io/v1"
        self.headers = {"Authorization": f"Bearer {token}"}

    def create_task(self, description, task_type):
        response = requests.post(
            f"{self.base_url}/task",
            headers=self.headers,
            json={"description": description, "type": task_type}
        )
        return response.json()

    def post_finding(self, claim, confidence, citations):
        response = requests.post(
            f"{self.base_url}/finding",
            headers=self.headers,
            json={
                "claim": claim,
                "confidence": confidence,
                "citations": citations
            }
        )
        return response.json()
```

### Monitoring & Observability

Track these metrics:

```
- api.requests.total (counter)
- api.request.duration_ms (histogram)
- api.errors.total (counter by error_code)
- api.rate_limit_exceeded.total (counter)
- oauth.device_flow.completion_rate (gauge)
```

---

## Support & Resources

- **Documentation:** https://github.com/dannystocker/infrafabric/docs
- **Status Page:** https://status.infrafabric.io
- **Issue Tracker:** https://github.com/dannystocker/infrafabric/issues
- **Discussions:** https://github.com/dannystocker/infrafabric/discussions

---

**Document Status:** Complete
**Citation:** `if://doc/api-reference/2025-11-30`
**Last Updated:** 2025-11-30
**Next Review:** 2025-12-31
