# Integration Guide: Adding Structured Logging to Your Agent

**Reference:** if://guide/logging-integration/2025-11-30

This guide shows how to integrate the StructuredLogger into your existing agent code.

## Step 1: Install Dependencies

```bash
# Logging library is pure Python with minimal dependencies
# Required: Python 3.8+

# Optional dependencies for async operations:
pip install asyncio python-json-logger
```

## Step 2: Import Logging Library

```python
# At the top of your agent file
from monitoring.logging.logging_library import (
    StructuredLogger,
    LogLevel,
    set_correlation_id,
    get_correlation_id,
    set_parent_agent_id,
    set_trace_id,
    CorrelationIDType
)
```

## Step 3: Initialize Logger in Agent

```python
class MyAgent:
    def __init__(self, agent_id: str, component: str):
        self.agent_id = agent_id
        self.component = component

        # Initialize structured logger
        self.logger = StructuredLogger(
            agent_id=agent_id,
            component=component,
            environment=os.getenv("ENVIRONMENT", "development"),
            log_level=LogLevel.INFO,
            log_path=f"/var/log/infrafabric/{agent_id}.log",
            batch_size=50,              # Batch 50 entries before writing
            flush_interval_seconds=5.0  # Flush every 5 seconds
        )

        self.logger.info(
            "Agent initialized",
            context={"version": "1.0.0", "workers": 4},
            tags=["startup"]
        )

    async def shutdown(self):
        # Force flush on shutdown
        self.logger.flush()
        self.logger.info("Agent shutting down")
```

## Step 4: Set Correlation IDs

### For HTTP Requests

```python
from flask import request, g

@app.before_request
def set_request_context():
    # Generate or extract correlation ID from request
    correlation_id = request.headers.get(
        "X-Correlation-ID",
        f"req-{uuid.uuid4().hex[:32]}"
    )

    # Set for this request context
    set_correlation_id(correlation_id, CorrelationIDType.REQUEST)

    # Store in Flask's g object for access in handlers
    g.correlation_id = correlation_id

    logger.info(
        "Request received",
        context={
            "method": request.method,
            "path": request.path,
            "user": request.headers.get("X-User-ID", "anonymous")
        }
    )
```

### For Background Tasks

```python
async def process_background_task(task_id: str, task_data: dict):
    # Generate task-scoped correlation ID
    set_correlation_id(f"task-{uuid.uuid4().hex[:32]}", CorrelationIDType.TASK)

    logger.info("Task started", context={"task_id": task_id})

    try:
        result = await do_work(task_data)
        logger.info("Task completed", context={"result": result})
    except Exception as e:
        logger.error("Task failed", exception=e, error_code="ERR_TASK_FAILED")
        raise
```

### For Swarm Operations

```python
async def coordinate_swarm(agents: List[str], operation: str):
    # Swarm-scoped correlation ID
    swarm_id = f"swarm-{uuid.uuid4().hex[:32]}"
    set_correlation_id(swarm_id, CorrelationIDType.SWARM)

    logger.info("Swarm operation started", context={
        "agents": len(agents),
        "operation": operation
    })

    # Send to agents - include correlation_id
    for agent_id in agents:
        await send_to_agent(agent_id, {
            "operation": operation,
            "correlation_id": get_correlation_id()  # Propagate
        })
```

## Step 5: Log in Agent Operations

### Normal Operations

```python
async def claim_task(self, task_id: str) -> bool:
    """Claim a task from the queue"""
    start_time = time.time()

    try:
        # Log start
        self.logger.debug(
            "Attempting to claim task",
            context={"task_id": task_id},
            tags=["task-claiming"]
        )

        # Do the work
        result = await self.redis.claim_task(task_id)

        # Log success with performance
        duration_ms = (time.time() - start_time) * 1000
        self.logger.log_performance(
            "Task claimed successfully",
            duration_ms=duration_ms,
            context={"task_id": task_id, "batch_size": 100},
            if_citation="if://log/redis-task-claim",
            tags=["redis", "task-processing"]
        )

        return result

    except Exception as e:
        # Log error with details
        self.logger.error(
            "Failed to claim task",
            context={"task_id": task_id},
            exception=e,
            error_code="ERR_TASK_CLAIM",
            if_citation="if://log/task-claim-error",
            tags=["redis", "error"]
        )
        raise
```

### Warnings & Recoverable Issues

```python
async def process_batch(self, batch: List[dict]):
    """Process a batch of items"""
    processed = 0
    failed = 0

    for item in batch:
        try:
            await self.process_item(item)
            processed += 1
        except RetryableError as e:
            # Recoverable - will retry
            self.logger.warn(
                "Item processing failed, will retry",
                context={
                    "item_id": item["id"],
                    "retry_count": item.get("retries", 0)
                },
                tags=["retry"]
            )
            failed += 1
        except Exception as e:
            # Non-recoverable
            self.logger.error(
                "Item processing failed permanently",
                exception=e,
                context={"item_id": item["id"]},
                error_code="ERR_ITEM_PROCESS"
            )
            failed += 1

    # Log batch summary
    self.logger.info(
        "Batch processing completed",
        context={
            "total": len(batch),
            "processed": processed,
            "failed": failed,
            "success_rate": processed / len(batch)
        },
        tags=["batch-processing"]
    )
```

### Performance Monitoring

```python
async def query_index(self, query: str) -> List[dict]:
    """Query ChromaDB index - log performance"""
    start_time = time.time()
    memory_before = self._get_memory_mb()

    try:
        results = await self.chromadb.search(query)

        duration_ms = (time.time() - start_time) * 1000
        memory_after = self._get_memory_mb()

        self.logger.log_performance(
            "Index query completed",
            duration_ms=duration_ms,
            memory_mb=memory_after - memory_before,
            context={
                "query_length": len(query),
                "result_count": len(results),
                "query_type": self._classify_query(query)
            },
            if_citation="if://log/chromadb-query",
            tags=["chromadb", "performance"]
        )

        return results

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        self.logger.error(
            "Index query failed",
            exception=e,
            context={"query": query, "duration_ms": duration_ms},
            error_code="ERR_CHROMADB_QUERY"
        )
        raise
```

## Step 6: Cross-Agent Communication

When sending messages to other agents, include correlation ID:

```python
async def delegate_to_agent(self, target_agent: str, task: dict):
    """Send task to another agent - propagate correlation ID"""

    # Get current correlation ID
    current_cid = get_correlation_id()

    self.logger.debug(
        "Delegating task to agent",
        context={
            "target_agent": target_agent,
            "task_id": task.get("id")
        },
        tags=["delegation"]
    )

    # Include correlation_id in message
    message = {
        "task": task,
        "correlation_id": current_cid,  # Propagate
        "from_agent": self.agent_id
    }

    await self.redis_bus.send_message(target_agent, message)


async def handle_incoming_message(self, message: dict):
    """Receive message from another agent - restore correlation ID"""

    # Extract and restore correlation ID
    if "correlation_id" in message:
        set_correlation_id(message["correlation_id"])
        set_parent_agent_id(message.get("from_agent"))

    self.logger.debug(
        "Received delegated task",
        context={
            "from_agent": message.get("from_agent"),
            "task_id": message["task"].get("id")
        },
        tags=["delegation"]
    )

    # All logs in this handler automatically include correlation_id
    await self.process_task(message["task"])
```

## Step 7: Query Your Logs

### In Grafana

```
1. Open http://localhost:3000 (admin/admin)
2. Go to Explore > select Loki
3. Enter query:
   {agent_id="YOUR-AGENT-ID"}
4. Click "Run Query" to see logs
```

### Find Request Trace

```logql
{correlation_id="req-abc123def456"}
```

Returns all logs for that request in execution order.

### Find Slow Operations

```logql
{agent_id="YOUR-AGENT-ID"} | json duration_ms > 100
```

### Monitor Agent Health

```logql
rate({agent_id="YOUR-AGENT-ID", level="ERROR"}[5m])
```

## Step 8: Environment Variables

Create `.env` file for agent:

```bash
# Logging
LOG_LEVEL=INFO
ENVIRONMENT=production
LOG_PATH=/var/log/infrafabric/agent-A1.log

# Loki aggregation (if using remote)
LOKI_HOST=loki.internal
LOKI_PORT=3100

# S3 for cold storage
S3_ENDPOINT=https://s3.amazonaws.com
S3_BUCKET=infrafabric-logs
AWS_AUTH_TYPE=role
```

## Step 9: Testing

```python
import asyncio
from monitoring.logging.logging_library import StructuredLogger, set_correlation_id

async def test_logging():
    logger = StructuredLogger(
        agent_id="test-agent-001",
        component="test",
        environment="development",
        log_path="/tmp/test.log"
    )

    # Set correlation ID
    set_correlation_id("req-test123")

    # Log different levels
    logger.debug("Debug message", context={"key": "value"})
    logger.info("Info message")
    logger.warn("Warning message")
    logger.error("Error message", error_code="ERR_TEST")

    # Log performance
    logger.log_performance(
        "Operation completed",
        duration_ms=123.45,
        memory_mb=256.7
    )

    # Force flush
    logger.flush()

    # Read logs
    with open("/tmp/test.log") as f:
        for line in f:
            print(line)

asyncio.run(test_logging())
```

## Step 10: Monitor Logs in Production

### Setup Log Rotation (Linux)

Create `/etc/logrotate.d/infrafabric`:

```
/var/log/infrafabric/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 infrafabric infrafabric
    postrotate
        systemctl reload infrafabric || true
    endscript
}
```

Run manually: `logrotate -f /etc/logrotate.d/infrafabric`

### Monitor Storage Usage

```bash
# Check log directory size
du -sh /var/log/infrafabric

# Find largest logs
du -sh /var/log/infrafabric/*.log | sort -h | tail -5

# Monitor Loki disk usage
du -sh /loki/chunks
du -sh /loki/boltdb-shipper-active
```

### Alerts Setup

In Loki, create rules for:

```yaml
- alert: HighErrorRate
  expr: rate({level="ERROR"}[5m]) > 10
  annotations:
    summary: "{{ $labels.agent_id }} has high error rate"

- alert: AgentUnresponsive
  expr: absent(rate({agent_id="A1-haiku-001"}[1m]))
  annotations:
    summary: "A1-haiku-001 stopped logging"
```

## Common Issues & Solutions

### Logs not appearing

```python
# Ensure log path exists
import os
os.makedirs("/var/log/infrafabric", exist_ok=True)

# Check permissions
os.chmod("/var/log/infrafabric", 0o755)

# Verify logger initialization
logger = StructuredLogger(agent_id="test", component="test")
logger.info("Test message")
logger.flush()  # Force flush

# Check file
# tail -f /var/log/infrafabric/test.log
```

### High memory usage

```python
# Reduce batch size
logger = StructuredLogger(batch_size=10)  # Instead of 50

# Reduce flush interval
logger = StructuredLogger(flush_interval_seconds=1.0)  # Instead of 5

# Disable async mode if not needed
logger = StructuredLogger(async_mode=False)
```

### Correlation ID not propagating

```python
# Always set in request handler
set_correlation_id(request_id)

# Always get from context
current_id = get_correlation_id()

# Always include when delegating
message = {"task": data, "correlation_id": get_correlation_id()}

# Always restore on receive
set_correlation_id(message["correlation_id"])
```

## Next Steps

1. Integrate into your primary agent
2. Update request handlers to set correlation IDs
3. Replace print/logging statements with logger calls
4. Test log queries in Grafana
5. Create dashboards for key metrics
6. Monitor production logs for errors

## References

- Logging Library: `logging-library.py`
- Query Examples: `LOG_QUERIES.md`
- Architecture: `LOGGING_ARCHITECTURE.md`
- Schema: `log-schema.json`
