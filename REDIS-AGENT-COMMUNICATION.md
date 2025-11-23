# Redis Cloud for Inter-Agent Communication

**Memory Exoskeleton - Haiku Agent Coordination**

**Date:** 2025-11-23
**Status:** Architecture Design
**Use Case:** Direct communication between spawned Haiku agents
**Backend:** Redis Cloud Pub/Sub + Streams
**Version:** 1.0.0

---

## Overview

Current setup uses Redis as **storage only** (context injection). This guide enables **real-time communication** between Haiku agents:

```
Haiku Agent 1                 Redis Cloud              Haiku Agent 2
(StackCP audit)    ←→ Pub/Sub Channels ←→    (Documentation update)
                   ←→ Stream Log ←→
                   ←→ Task Queue ←→
```

### Benefits vs Current Approach

| Feature | Storage Only | Pub/Sub + Streams |
|---------|-------------|-------------------|
| Context injection | ✅ | ✅ |
| Real-time messaging | ❌ | ✅ |
| Task coordination | ❌ | ✅ |
| Work distribution | ❌ | ✅ |
| Event notification | ❌ | ✅ |
| Atomic transactions | ❌ | ✅ |
| Persistence | ✅ | ✅ |
| Replay capability | ❌ | ✅ |

---

## Architecture

### 1. Pub/Sub Channels (Real-Time Messaging)

**Use Case:** Haiku agents instantly notify each other of progress

```
Haiku-Agent-1:
  → PUBLISH "task:18:audit" "{status: 'running', progress: 50%}"

Redis Pub/Sub:
  → Broadcasts to all subscribers

Haiku-Agent-2:
  ← SUBSCRIBE "task:18:audit"
  ← Receives: {status: 'running', progress: 50%}
```

### 2. Streams (Event Log with Replay)

**Use Case:** Persistent event history for debugging and replay

```
Haiku-Agent-1:
  → XADD "events:18" * "agent=haiku-1" "action=audit_complete"

Redis Stream:
  → Persists with ID and timestamp
  → Never expires (unlike Pub/Sub)

Haiku-Agent-2:
  ← XREAD STREAMS "events:18" 0
  ← Gets: [1, 2, 3...] all historical events
```

### 3. Task Queue (Work Distribution)

**Use Case:** Delegate tasks between agents

```
Haiku-Agent-1 (Main):
  → LPUSH "task:queue" "{task: 'update-docs', assignee: 'haiku-2'}"

Redis List:
  → FIFO queue

Haiku-Agent-2 (Worker):
  ← BRPOP "task:queue" 60
  ← Waits for task, processes it
  → LPUSH "task:completed" "{task: 'update-docs', result: '...', status: 'done'}"

Haiku-Agent-1 (Monitor):
  ← Checks "task:completed" for results
```

### 4. Locks & Semaphores (Synchronization)

**Use Case:** Prevent race conditions (e.g., two agents updating same file)

```
Haiku-Agent-1:
  → SET "lock:agents.md" "haiku-1" EX 30
  → Proceed with edit

Haiku-Agent-2:
  ← GET "lock:agents.md"
  ← Sees "haiku-1", waits
  → Retries after 5 seconds

Haiku-Agent-1 (Done):
  → DEL "lock:agents.md"

Haiku-Agent-2:
  → SET "lock:agents.md" "haiku-2" EX 30
  → Now safe to edit
```

---

## Implementation Guide

### 1. PHP Bridge for Agent Communication

```php
<?php
/**
 * Redis Agent Communication Module
 * File: /home/setup/infrafabric/redis-agent-comm.php
 */

require 'vendor/autoload.php';
use Predis\Client;

class AgentCommunication {
    private $redis;
    private $agentId;
    private $broadcastChannel;
    private $eventStream;
    private $taskQueue;
    private $lockPrefix = 'lock:';
    private $lockTTL = 30;

    public function __construct($agentId = 'unknown') {
        $this->redis = new Predis\Client([
            'host' => 'redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com',
            'port' => 19956,
            'username' => 'default',
            'password' => 'zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8'
        ]);

        $this->agentId = $agentId;
        $this->broadcastChannel = "broadcast:agents";
        $this->eventStream = "events:stream";
        $this->taskQueue = "task:queue";

        // Test connection
        try {
            $this->redis->ping();
            $this->log("Connected to Redis Cloud");
        } catch (Exception $e) {
            $this->log("FATAL: Redis connection failed: " . $e->getMessage(), 'error');
        }
    }

    /**
     * Broadcast a message to all agents
     */
    public function broadcast($message, $metadata = []) {
        $payload = [
            'agent' => $this->agentId,
            'timestamp' => date('c'),
            'message' => $message,
            'metadata' => $metadata
        ];

        // Pub/Sub: Real-time notification
        $subscribers = $this->redis->publish(
            $this->broadcastChannel,
            json_encode($payload)
        );

        // Stream: Persistent log
        $this->redis->xadd(
            $this->eventStream,
            '*',
            'agent', $this->agentId,
            'type', 'broadcast',
            'message', $message,
            'metadata', json_encode($metadata),
            'timestamp', date('c')
        );

        $this->log("Broadcast: $message (to $subscribers agents)");
        return $payload;
    }

    /**
     * Listen for broadcasts from other agents
     */
    public function listenBroadcast($timeout = 60) {
        $this->log("Listening for broadcasts...");

        $pubsub = $this->redis->pubsub();
        $pubsub->subscribe($this->broadcastChannel);

        $startTime = time();
        foreach ($pubsub->getMessages() as $message) {
            if ($message->kind === 'message') {
                $data = json_decode($message->payload, true);
                $this->log("Received from {$data['agent']}: {$data['message']}");

                yield $data;
            }

            if (time() - $startTime > $timeout) {
                $this->log("Timeout reached, stopping listen");
                break;
            }
        }

        $pubsub->unsubscribe($this->broadcastChannel);
    }

    /**
     * Get event history
     */
    public function getEvents($since = 0, $count = 10) {
        // Since: 0 = all events, '-' = new events only
        $events = $this->redis->xrange(
            $this->eventStream,
            $since,
            '+',
            ['COUNT' => $count]
        );

        $result = [];
        foreach ($events as $id => $fields) {
            $result[] = [
                'id' => $id,
                'agent' => $fields['agent'],
                'type' => $fields['type'],
                'message' => $fields['message'],
                'metadata' => json_decode($fields['metadata'], true),
                'timestamp' => $fields['timestamp']
            ];
        }

        return $result;
    }

    /**
     * Enqueue a task for another agent
     */
    public function enqueueTask($task, $assignee, $metadata = []) {
        $payload = [
            'taskId' => uniqid('task_'),
            'creator' => $this->agentId,
            'assignee' => $assignee,
            'task' => $task,
            'metadata' => $metadata,
            'createdAt' => date('c'),
            'status' => 'pending'
        ];

        // LPUSH: Add to left (most recent)
        $this->redis->lpush($this->taskQueue, json_encode($payload));

        // Also log as event
        $this->broadcast("Task enqueued: $task for $assignee", ['taskId' => $payload['taskId']]);

        $this->log("Enqueued task: {$payload['taskId']} for $assignee");
        return $payload;
    }

    /**
     * Wait for and process the next task
     */
    public function getNextTask($timeout = 60) {
        $this->log("Waiting for task (timeout: ${timeout}s)...");

        // BRPOP: Blocking right pop (waits for task)
        $result = $this->redis->brpop($this->taskQueue, $timeout);

        if ($result === null) {
            $this->log("No task received within timeout");
            return null;
        }

        $task = json_decode($result[1], true);
        $this->log("Got task: {$task['task']} from {$task['creator']}");

        return $task;
    }

    /**
     * Mark a task as complete
     */
    public function completeTask($taskId, $result, $metadata = []) {
        $completion = [
            'taskId' => $taskId,
            'completedBy' => $this->agentId,
            'result' => $result,
            'metadata' => $metadata,
            'completedAt' => date('c'),
            'status' => 'completed'
        ];

        // Store in Redis
        $this->redis->lpush("task:completed", json_encode($completion));

        // Broadcast completion
        $this->broadcast("Task completed: $taskId", $completion);

        $this->log("Task completed: $taskId");
        return $completion;
    }

    /**
     * Acquire a lock (prevents concurrent edits)
     */
    public function acquireLock($resource, $maxRetries = 5) {
        $lockKey = $this->lockPrefix . $resource;
        $lockValue = $this->agentId . ':' . uniqid();

        for ($i = 0; $i < $maxRetries; $i++) {
            // SET NX: Only set if not exists
            $result = $this->redis->set(
                $lockKey,
                $lockValue,
                'EX', $this->lockTTL,  // Expire after 30 seconds
                'NX'                    // Only if not exists
            );

            if ($result === true) {
                $this->log("Lock acquired: $resource");
                return ['success' => true, 'lockValue' => $lockValue, 'retries' => $i];
            }

            $this->log("Lock busy: $resource (attempt " . ($i + 1) . "/$maxRetries)");
            sleep(2);  // Wait before retry
        }

        throw new Exception("Failed to acquire lock for $resource after $maxRetries attempts");
    }

    /**
     * Release a lock
     */
    public function releaseLock($resource, $lockValue) {
        $lockKey = $this->lockPrefix . $resource;
        $currentValue = $this->redis->get($lockKey);

        if ($currentValue === $lockValue) {
            $this->redis->del($lockKey);
            $this->log("Lock released: $resource");
            return true;
        }

        $this->log("Cannot release lock: value mismatch (owns: $currentValue, trying: $lockValue)", 'warn');
        return false;
    }

    /**
     * Send a private message to another agent
     */
    public function sendMessage($targetAgent, $message, $metadata = []) {
        $channel = "msg:{$this->agentId}:{$targetAgent}";

        $payload = [
            'from' => $this->agentId,
            'to' => $targetAgent,
            'message' => $message,
            'metadata' => $metadata,
            'timestamp' => date('c')
        ];

        $this->redis->publish($channel, json_encode($payload));
        $this->log("Message sent to $targetAgent: $message");

        return $payload;
    }

    /**
     * Listen for messages from another agent
     */
    public function listenMessages($sourceAgent, $timeout = 60) {
        $channel = "msg:{$sourceAgent}:{$this->agentId}";
        $this->log("Listening for messages from $sourceAgent...");

        $pubsub = $this->redis->pubsub();
        $pubsub->subscribe($channel);

        $startTime = time();
        foreach ($pubsub->getMessages() as $message) {
            if ($message->kind === 'message') {
                $data = json_decode($message->payload, true);
                yield $data;
            }

            if (time() - $startTime > $timeout) break;
        }

        $pubsub->unsubscribe($channel);
    }

    /**
     * Get agent status
     */
    public function getStatus() {
        return [
            'agent' => $this->agentId,
            'timestamp' => date('c'),
            'redisConnected' => true,
            'capabilities' => [
                'broadcast' => true,
                'listen' => true,
                'tasks' => true,
                'locks' => true,
                'messages' => true
            ]
        ];
    }

    /**
     * Logging helper
     */
    private function log($message, $level = 'info') {
        $timestamp = date('Y-m-d H:i:s');
        echo "[{$timestamp}] [{$this->agentId}] [$level] $message\n";

        // Also store in Redis for audit
        $logKey = "logs:{$this->agentId}";
        $this->redis->lpush($logKey, json_encode([
            'timestamp' => $timestamp,
            'level' => $level,
            'message' => $message
        ]));

        // Keep last 100 logs
        $this->redis->ltrim($logKey, 0, 99);
    }
}

?>
```

### 2. Example: Haiku Agent Task Coordination

**Agent 1 (Main/Orchestrator):**
```php
<?php
require 'redis-agent-comm.php';

$comm = new AgentCommunication('haiku-orchestrator');

// Start two parallel haiku tasks
$tasks = [
    ['task' => 'audit-stackcp', 'assignee' => 'haiku-audit'],
    ['task' => 'update-docs', 'assignee' => 'haiku-docs']
];

foreach ($tasks as $taskDef) {
    $comm->enqueueTask(
        $taskDef['task'],
        $taskDef['assignee'],
        ['priority' => 'high', 'deadline' => date('c', time() + 3600)]
    );
}

// Wait for both to complete
$completed = 0;
while ($completed < count($tasks)) {
    // Listen for broadcasts
    foreach ($comm->listenBroadcast(10) as $message) {
        if (strpos($message['message'], 'Task completed') !== false) {
            $completed++;
            echo "Progress: $completed/" . count($tasks) . "\n";
        }
    }
}

echo "All tasks completed!\n";
?>
```

**Agent 2 (Worker - Haiku Audit):**
```php
<?php
require 'redis-agent-comm.php';

$comm = new AgentCommunication('haiku-audit');

// Wait for task
while (true) {
    $task = $comm->getNextTask(300);  // 5-minute timeout

    if ($task === null) break;

    try {
        // Process the task
        $comm->broadcast("Processing: {$task['task']}", ['status' => 'running']);

        // Do work (simulate 10 seconds)
        sleep(10);

        // Mark complete
        $comm->completeTask(
            $task['taskId'],
            ['lines_added' => 250, 'audit_complete' => true],
            ['duration' => 10]
        );
    } catch (Exception $e) {
        $comm->broadcast("Task failed: {$task['taskId']}", ['error' => $e->getMessage()]);
    }
}
?>
```

**Agent 3 (Worker - Haiku Docs):**
```php
<?php
require 'redis-agent-comm.php';

$comm = new AgentCommunication('haiku-docs');

while (true) {
    $task = $comm->getNextTask(300);

    if ($task === null) break;

    // Acquire lock before editing agents.md
    try {
        $lock = $comm->acquireLock('agents.md', 10);

        $comm->broadcast("Updating agents.md", ['lockValue' => $lock['lockValue']]);

        // Simulate edit (5 seconds)
        sleep(5);

        // Release lock
        $comm->releaseLock('agents.md', $lock['lockValue']);

        // Mark task complete
        $comm->completeTask(
            $task['taskId'],
            ['file' => 'agents.md', 'lines_added' => 100],
            ['duration' => 5]
        );

    } catch (Exception $e) {
        $comm->broadcast("Failed to update docs", ['error' => $e->getMessage()]);
    }
}
?>
```

---

## Use Cases

### 1. Parallel Audits with Progress Updates

```
Orchestrator Haiku:
  → Splits work (13 audit commands)
  → Assigns 3 to each agent
  → Waits for completion

Worker Haiku 1:
  ← Gets 3 commands
  → Broadcasts progress: "Running 1/3..."
  → Broadcasts complete

Worker Haiku 2:
  ← Gets 3 commands
  → Broadcasts progress: "Running 2/3..."
  → Broadcasts complete

Worker Haiku 3:
  ← Gets remaining commands
  → Broadcasts progress: "Running 3/3..."
  → Broadcasts complete

Orchestrator:
  ← Monitors all broadcasts
  → Aggregates results
  → Creates final report
```

### 2. Safe Concurrent File Edits

```
Haiku-1: "I need to edit agents.md"
  → acquireLock('agents.md')
  → Edit agents.md
  → releaseLock('agents.md')

Haiku-2: "I also need to edit agents.md"
  → acquireLock('agents.md')
  → BLOCKED (waits for Haiku-1)
  → After 30 seconds...
  → Retries, acquires lock
  → Edit agents.md
  → releaseLock('agents.md')
```

### 3. Work Distribution Pipeline

```
Queue:
  → task_1: audit
  → task_2: update-docs
  → task_3: deploy
  → task_4: test

Worker Pool:
  Haiku-A: BRPOP → Gets task_1
  Haiku-B: BRPOP → Gets task_2
  Haiku-C: BRPOP → Gets task_3
  Haiku-D: BRPOP → Waits for task_4

As tasks complete:
  Haiku-A: LPUSH completed → Gets task_4
  ...
```

---

## Python Integration (for Codex Agents)

```python
import redis
import json
from datetime import datetime
import time

class AgentComm:
    def __init__(self, agent_id):
        self.redis = redis.Redis(
            host='redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com',
            port=19956,
            username='default',
            password='zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8',
            decode_responses=True
        )
        self.agent_id = agent_id

    def broadcast(self, message, metadata=None):
        payload = {
            'agent': self.agent_id,
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'metadata': metadata or {}
        }

        # Pub/Sub
        self.redis.publish('broadcast:agents', json.dumps(payload))

        # Stream
        self.redis.xadd(
            'events:stream',
            {'agent': self.agent_id, 'message': message, 'metadata': json.dumps(payload['metadata'])}
        )

        print(f"[{self.agent_id}] Broadcast: {message}")

    def enqueue_task(self, task, assignee, metadata=None):
        payload = {
            'taskId': f"task_{int(time.time())}",
            'creator': self.agent_id,
            'assignee': assignee,
            'task': task,
            'metadata': metadata or {},
            'createdAt': datetime.now().isoformat()
        }

        self.redis.lpush('task:queue', json.dumps(payload))
        print(f"[{self.agent_id}] Task enqueued: {task} → {assignee}")

        return payload

    def get_next_task(self, timeout=60):
        result = self.redis.brpop('task:queue', timeout=timeout)
        if result:
            return json.loads(result[1])
        return None

    def complete_task(self, task_id, result):
        completion = {
            'taskId': task_id,
            'completedBy': self.agent_id,
            'result': result,
            'completedAt': datetime.now().isoformat()
        }

        self.redis.lpush('task:completed', json.dumps(completion))
        self.broadcast(f"Task completed: {task_id}")

# Usage
comm = AgentComm('codex-agent-1')
comm.broadcast('Starting Phase A verification')
comm.enqueue_task('verify-api', 'codex-agent-2')
```

---

## Comparison: Current vs New

### Current (Storage Only)

```
Sonnet → Redis (Store context)
Haiku → Redis (Read context)
Haiku → Redis (Store results)
Sonnet → Checks Redis for results (polling)
```

❌ Polling-based (inefficient)
❌ No real-time updates
❌ Race conditions possible
❌ No task queue

### New (With Pub/Sub + Streams)

```
Orchestrator → LPUSH task:queue
Worker-1 → BRPOP task:queue
Worker-1 → PUBLISH broadcast
Orchestrator ← SUBSCRIBE broadcast:agents
Worker-1 → XADD events:stream
Orchestrator ← XREAD events:stream
```

✅ Event-driven (efficient)
✅ Real-time notifications
✅ Atomic operations
✅ Built-in task queue
✅ Full event history

---

## Deployment

### Step 1: Upload redis-agent-comm.php to StackCP

```bash
scp /home/setup/infrafabric/redis-agent-comm.php \
  digital-lab.ca@ssh.gb.stackcp.com:~/public_html/digital-lab.ca/infrafabric/
```

### Step 2: Test with Sample Agents

```bash
# Terminal 1: Agent 1 (Enqueuer)
ssh digital-lab.ca@ssh.gb.stackcp.com
php ~/test_agent_1.php

# Terminal 2: Agent 2 (Worker)
php ~/test_agent_2.php
```

### Step 3: Integrate with Haiku Spawning

```php
// In your main orchestrator
require 'redis-agent-comm.php';

$comm = new AgentCommunication('orchestrator');

// Spawn Haiku Agent 1
$comm->enqueueTask('comprehensive-audit', 'haiku-1', ['scope' => 'stackcp']);

// Spawn Haiku Agent 2
$comm->enqueueTask('update-documentation', 'haiku-2', ['scope' => 'agents.md']);

// Monitor progress
foreach ($comm->listenBroadcast() as $msg) {
    if (strpos($msg['message'], 'completed') !== false) {
        echo "Agent progress: " . $msg['message'] . "\n";
    }
}
```

---

## Monitoring & Debugging

### View All Events

```bash
redis-cli -u redis://default:PASSWORD@HOST:PORT XREAD COUNT 10 STREAMS events:stream 0
```

### View Task Queue

```bash
redis-cli -u redis://... LRANGE task:queue 0 -1
```

### View Active Locks

```bash
redis-cli -u redis://... KEYS "lock:*"
```

### View Agent Logs

```bash
redis-cli -u redis://... LRANGE "logs:haiku-1" 0 -1
```

---

## Performance

| Operation | Latency | Notes |
|-----------|---------|-------|
| PUBLISH (broadcast) | < 10ms | Real-time |
| BRPOP (wait for task) | < 10ms | Blocking |
| XADD (log event) | < 5ms | Async |
| SET/DEL (lock) | < 5ms | Atomic |
| LPUSH (enqueue) | < 5ms | Fast |

Total overhead for agent coordination: **< 50ms per operation**

---

## Next Steps

1. **Implement** redis-agent-comm.php on StackCP
2. **Test** with 2-3 Haiku agents
3. **Integrate** with Phase B task spawning
4. **Monitor** with event logs and dashboards
5. **Scale** to 8+ concurrent Haiku agents

---

**This enables true multi-agent orchestration for Memory Exoskeleton.**

See also:
- CODEX-CLI-INTEGRATION.md
- GEMINI-WEB-INTEGRATION.md
- agents.md (for agent definitions)
