# OpenAI Codex Starter Prompt: Redis Swarm Worker

**Purpose:** Enable OpenAI's Codex (via GPT-4 API) to join the Redis Swarm as a specialized code generation and technical writing worker.

**Why Codex in the Swarm?**
- Expert code generation and refactoring
- Technical documentation writing
- Architecture pattern implementation
- Language-agnostic code translation
- API integration assistance
- Cost-efficient for pure code tasks (no reasoning overhead)

---

## Overview: Codex as a Redis Swarm Worker

The Redis Swarm is a vendor-agnostic multi-AI coordination layer. Any model with Redis client access can:
1. Claim tasks from a shared queue
2. Execute using its native API
3. Report findings back to Redis
4. Collaborate with Claude, Gemini, GPT-4, and DeepSeek workers

**Codex's Role:**
- Specialize in code generation, refactoring, and technical implementation
- Execute in parallel with other workers (no blocking)
- Cost-optimize: Use Codex for "generate code" tasks, not reasoning-heavy tasks
- Report results in standard Redis format for other workers to integrate

---

## Quick Start: Copy-Paste to Run

### Prerequisites

```bash
pip install redis openai python-dotenv
```

Set environment variables:
```bash
export OPENAI_API_KEY="sk-..."
export REDIS_HOST="localhost"  # or remote Redis
export REDIS_PORT="6379"
```

### 1. Universal Worker Base Class (shared across vendors)

```python
# redis_swarm_codex.py
import redis
import json
import uuid
from datetime import datetime
from typing import Dict, Optional
import os

class UniversalWorker:
    """
    Base class for any AI vendor to join the swarm.
    Handles Redis communication (vendor-agnostic).
    """
    def __init__(self, vendor: str, model: str, redis_host: str = 'localhost', redis_port: int = 6379):
        self.vendor = vendor
        self.model = model
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )
        self.worker_id = f"{vendor}_{model}_{uuid.uuid4().hex[:8]}"

        # Test Redis connection
        try:
            self.redis.ping()
            print(f"✅ Connected to Redis at {redis_host}:{redis_port}")
        except redis.ConnectionError:
            print(f"❌ Cannot connect to Redis at {redis_host}:{redis_port}")
            raise

    def claim_task(self, queue_name: str) -> Optional[Dict]:
        """Claim next task from Redis queue (FIFO)"""
        task_id = self.redis.lpop(f"queue:{queue_name}")
        if not task_id:
            return None

        task_data = self.redis.get(f"task:{task_id}")
        if task_data:
            return json.loads(task_data)
        return None

    def execute_task(self, task: Dict) -> Dict:
        """
        Execute task using vendor-specific API.
        Subclass must implement this.
        """
        raise NotImplementedError("Subclass must implement execute_task()")

    def report_finding(self, task_id: str, finding: Dict) -> str:
        """Report finding back to Redis (vendor-agnostic)"""
        finding_id = f"finding_{uuid.uuid4().hex[:8]}"

        finding_data = {
            "finding_id": finding_id,
            "task_id": task_id,
            "worker_id": self.worker_id,
            "vendor": self.vendor,
            "model": self.model,
            "timestamp": datetime.utcnow().isoformat(),
            **finding
        }

        # Store finding
        self.redis.set(f"finding:{finding_id}", json.dumps(finding_data))

        # Link to task
        self.redis.rpush(f"task:{task_id}:findings", finding_id)

        # Publish notification for subscribers
        self.redis.publish("findings:new", json.dumps(finding_data))

        return finding_id

    def get_task_context(self, task_id: str) -> str:
        """Retrieve context stored with task"""
        context_data = self.redis.get(f"task:{task_id}:context")
        return context_data if context_data else ""

    def heartbeat(self):
        """Signal that worker is alive"""
        self.redis.set(f"worker:{self.worker_id}:heartbeat", datetime.utcnow().isoformat(), ex=300)
```

### 2. Codex Worker Implementation

```python
# Extends UniversalWorker with OpenAI Codex-specific logic
from openai import OpenAI

class CodexWorker(UniversalWorker):
    """
    OpenAI Codex worker: Specialized in code generation, refactoring, documentation.
    Joins Redis Swarm alongside Claude, Gemini, GPT-4, and DeepSeek workers.
    """

    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        super().__init__(
            vendor="openai",
            model="gpt-4",  # Using GPT-4 for superior code generation
            redis_host=redis_host,
            redis_port=redis_port
        )
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print(f"🚀 Codex Worker initialized: {self.worker_id}")

    def execute_task(self, task: Dict) -> Dict:
        """
        Execute code-generation or technical-writing task using OpenAI GPT-4.

        Task format:
        {
            "task_id": "task_abc123",
            "task_type": "if.code_generation",
            "prompt": "Generate Python code to...",
            "language": "python",  # optional
            "context": "<optional background code or docs>",
            "temperature": 0.7  # optional, default 0.2 for code
        }
        """
        task_id = task.get("task_id")
        task_type = task.get("task_type", "if.code_generation")
        prompt = task.get("prompt", "")
        language = task.get("language", "python")
        context = task.get("context", "")
        temperature = task.get("temperature", 0.2)  # Low temp for code consistency

        # Build system prompt based on task type
        if "documentation" in task_type or "documentation" in prompt.lower():
            system_prompt = "You are an expert technical writer. Generate clear, comprehensive documentation with examples."
        elif "refactor" in task_type or "refactor" in prompt.lower():
            system_prompt = f"You are an expert {language} programmer. Refactor code to be cleaner, faster, and more maintainable. Preserve all functionality."
        else:
            system_prompt = f"You are an expert {language} programmer. Generate production-ready code with proper error handling and documentation."

        # Include context if provided
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\n---\n\nTask:\n{prompt}"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=4096,
                temperature=temperature,
                top_p=0.95
            )

            code_output = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            return {
                "summary": f"Generated {language} code ({len(code_output)} chars)",
                "code": code_output,
                "language": language,
                "tokens_used": tokens_used,
                "model": "gpt-4",
                "task_type": task_type
            }

        except Exception as e:
            return {
                "summary": f"Error executing task: {str(e)}",
                "error": str(e),
                "model": "gpt-4",
                "task_type": task_type
            }

    def claim_and_execute(self, queue_name: str = "if.code_generation", max_tasks: int = 10) -> int:
        """
        Main loop: Claim tasks, execute, report findings.
        Runs until queue is empty or max_tasks reached.

        Returns: Number of tasks completed.
        """
        completed = 0

        for _ in range(max_tasks):
            # Claim task
            task = self.claim_task(queue_name)
            if not task:
                print(f"ℹ️ No more tasks in queue: {queue_name}")
                break

            task_id = task.get("task_id")
            print(f"\n📋 Claimed task: {task_id}")
            print(f"   Type: {task.get('task_type')}")
            print(f"   Prompt: {task.get('prompt')[:100]}...")

            # Execute task
            print(f"   🔄 Executing with GPT-4...")
            result = self.execute_task(task)

            # Report finding
            finding_id = self.report_finding(task_id, result)
            print(f"   ✅ Finding reported: {finding_id}")

            completed += 1

            # Heartbeat
            self.heartbeat()

        return completed
```

### 3. Spawn Tasks to Redis

```python
# spawn_tasks.py
def create_code_task(
    task_type: str,
    prompt: str,
    language: str = "python",
    context: str = "",
    redis_host: str = "localhost"
) -> str:
    """
    Create a code generation task and post it to Redis queue.
    Returns: task_id
    """
    import redis

    redis_client = redis.Redis(host=redis_host, decode_responses=True)

    task_id = f"task_{uuid.uuid4().hex[:12]}"
    task_data = {
        "task_id": task_id,
        "task_type": task_type,
        "prompt": prompt,
        "language": language,
        "context": context,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Store task metadata
    redis_client.set(f"task:{task_id}", json.dumps(task_data))

    # Queue task
    redis_client.rpush(f"queue:{task_type}", task_id)

    print(f"📌 Task created: {task_id}")
    print(f"   Queue: {task_type}")

    return task_id

# Example: Create 5 code generation tasks
if __name__ == "__main__":
    tasks = [
        ("if.code_generation", "Generate a Python class for managing Redis connections with reconnect logic"),
        ("if.code_generation", "Write async FastAPI endpoint to stream OpenAI responses"),
        ("if.code_documentation", "Document this Redis Swarm worker pattern with examples"),
        ("if.code_refactor", "Refactor: Optimize list comprehension for large datasets", "python"),
        ("if.code_generation", "Create TypeScript interface for Redis task messages")
    ]

    task_ids = []
    for task_type, prompt, *rest in tasks:
        language = rest[0] if rest else "python"
        task_id = create_code_task(task_type, prompt, language)
        task_ids.append(task_id)

    print(f"\n✅ Created {len(task_ids)} tasks")
```

### 4. Run Codex Worker

```python
# main_codex_worker.py
if __name__ == "__main__":
    # Initialize Codex worker
    codex = CodexWorker(redis_host="localhost", redis_port=6379)

    # Claim and execute tasks from queue
    completed = codex.claim_and_execute(
        queue_name="if.code_generation",
        max_tasks=10
    )

    print(f"\n✅ Codex worker completed {completed} tasks")
    print(f"   Worker ID: {codex.worker_id}")
    print(f"   Findings stored in Redis with prefix 'finding:*'")
```

**Run it:**
```bash
python main_codex_worker.py
```

Output:
```
✅ Connected to Redis at localhost:6379
🚀 Codex Worker initialized: openai_gpt-4_a1b2c3d4

📋 Claimed task: task_xyz789
   Type: if.code_generation
   Prompt: Generate Python class for Redis connections...
   🔄 Executing with GPT-4...
   ✅ Finding reported: finding_abc123

✅ Codex worker completed 1 tasks
```

---

## Example Task: Code Generation

### Scenario: Generate Redis Connection Manager

**Task (posted to Redis):**
```json
{
  "task_id": "task_redis_manager",
  "task_type": "if.code_generation",
  "prompt": "Generate a production-ready Python class that manages Redis connections with automatic reconnection, connection pooling, and health checks. Include docstrings and error handling.",
  "language": "python",
  "temperature": 0.2
}
```

**Codex Output (stored in Redis):**
```python
class RedisConnectionManager:
    """
    Manages Redis connections with pooling, reconnection, and health monitoring.

    Features:
    - Connection pooling for efficiency
    - Automatic reconnection with exponential backoff
    - Health check via periodic ping
    - Thread-safe operations
    """

    def __init__(self, host='localhost', port=6379, max_retries=5, backoff_base=2):
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            decode_responses=True,
            max_connections=10
        )
        self.client = redis.Redis(connection_pool=self.pool)
        self._health_check()

    def _health_check(self):
        """Verify Redis is reachable"""
        try:
            self.client.ping()
        except redis.ConnectionError as e:
            raise RuntimeError(f"Cannot connect to Redis: {e}")

    def get(self, key):
        """Get value with automatic reconnection"""
        for attempt in range(self.max_retries):
            try:
                return self.client.get(key)
            except redis.ConnectionError:
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_base ** attempt
                    time.sleep(wait_time)
                else:
                    raise

    def set(self, key, value, ex=None):
        """Set value with automatic reconnection"""
        for attempt in range(self.max_retries):
            try:
                return self.client.set(key, value, ex=ex)
            except redis.ConnectionError:
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_base ** attempt
                    time.sleep(wait_time)
                else:
                    raise

    def close(self):
        """Close all connections"""
        self.pool.disconnect()
```

Finding stored in Redis:
```json
{
  "finding_id": "finding_cm123",
  "task_id": "task_redis_manager",
  "worker_id": "openai_gpt-4_a1b2c3d4",
  "vendor": "openai",
  "model": "gpt-4",
  "summary": "Generated Python class for Redis connections (850 chars)",
  "code": "...",
  "language": "python",
  "tokens_used": 1247,
  "model": "gpt-4",
  "task_type": "if.code_generation"
}
```

---

## Integration: How Codex Fits with Other Workers

### Multi-Vendor Swarm Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Redis Universal Bus                       │
│  (Message passing, task queues, findings storage)            │
└─────────────────────────────────────────────────────────────┘
         ↑           ↑           ↑           ↑           ↑
    Claude       Gemini        GPT-4       DeepSeek    Codex
    Haiku        2.0 Pro       Turbo       Chat        (You)
    Research    Analysis      Reasoning   Budget      Code Gen
         │           │           │           │           │
         └───────────┴───────────┴───────────┴───────────┘
              All claim same tasks, all report findings
```

### Task Distribution Strategy

```python
class SmartTaskRouter:
    """Route tasks to optimal vendor"""

    TASK_ROUTING = {
        "if.code_generation": "codex",      # Codex specializes here
        "if.code_refactor": "codex",         # Code optimization
        "if.code_documentation": "codex",    # Technical writing
        "if.research_pass1": "deepseek",     # Cheap broad search
        "if.research_pass2": "claude",       # Medium reasoning
        "if.synthesis": "gemini",            # Large context synthesis
        "if.architecture_decision": "gpt-4"  # Complex reasoning
    }

    def route_task(self, task_type: str) -> str:
        return self.TASK_ROUTING.get(task_type, "claude")  # Default to Claude
```

### Collaborative Example: API Documentation Generation

**Scenario:** Generate API docs for Redis Swarm protocol

1. **Codex generates** code examples and TypeScript definitions
2. **Claude refines** prose, adds explanations
3. **Gemini synthesizes** into comprehensive guide using 2M context window
4. **All findings linked** in Redis, coordinator assembles final document

```python
# Spawn across vendors
codex_task = create_code_task(
    "if.code_generation",
    "Generate Python dataclasses for Redis Swarm task message format"
)

claude_task = create_task(
    "if.documentation_enhancement",
    "Enhance this API documentation with clear explanations and best practices"
)

# All workers claim from their queues, report findings
# Coordinator assembles results
```

---

## Cost Optimization: When to Use Codex vs Other Models

### Cost-Benefit Matrix

| Task Type | Codex (GPT-4) | Claude Haiku | GPT-4 Turbo | Recommendation |
|-----------|--------------|-------------|------------|-----------------|
| **Code Generation** | $0.03/1K | $0.008/1K | $0.01/1K | **Use Codex** - specialized |
| **Code Refactoring** | $0.03/1K | $0.008/1K | $0.01/1K | **Use Codex** - understands code patterns |
| **API Design** | $0.03/1K | $0.008/1K | $0.01/1K | **Use Codex** or GPT-4 |
| **Documentation** | $0.03/1K | $0.008/1K | $0.01/1K | **Use Codex** - clean prose |
| **Bug Analysis** | $0.03/1K | $0.008/1K | $0.01/1K | Use **Claude Haiku** first (cheaper) |
| **Architecture Decision** | $0.03/1K | $0.008/1K | $0.01/1K | Use **GPT-4 Turbo** (better reasoning) |
| **Massive Context Synthesis** | N/A | N/A | N/A | Use **Gemini 2.0 Pro** (2M context) |

### Cost Optimization Strategies

**Strategy 1: Task-Specific Routing**
```python
def estimate_cost_and_route(task: Dict) -> str:
    """Route to cheapest model that can handle task"""
    task_type = task.get("task_type")

    if "code" in task_type:
        return "codex"  # Expert for code, pay premium for quality
    elif "simple_search" in task_type:
        return "deepseek"  # 7× cheaper than Claude
    elif "analysis" in task_type:
        return "claude-haiku"  # Good reasoning at low cost
    elif "synthesis" in task_type:
        return "gemini-2.0-pro"  # 2M context window
    else:
        return "gpt-4-turbo"  # General purpose fallback
```

**Strategy 2: Batch Similar Tasks**
```python
# Batch 10 code generation tasks for Codex (cheaper per task)
for i in range(10):
    create_code_task("if.code_generation", prompts[i])

# One Codex worker processes all 10 efficiently
codex = CodexWorker()
codex.claim_and_execute("if.code_generation", max_tasks=10)
# Cost: 10 tasks × ~$0.02 each = $0.20
```

**Strategy 3: Cascade Quality**
```python
# First pass: DeepSeek generates rough code ($0.14/M)
create_code_task("if.code_generation_draft", prompt)

# Second pass: Codex refactors ($0.03/K input + output)
# Codex only processes if draft quality is low
create_code_task("if.code_refactor", draft_code, task_type="improvement")
```

---

## Advanced: Codex in Specialized Swarms

### 1. Rapid Prototyping Swarm
```python
# For quick MVP generation across multiple languages
swarm = {
    "codex": CodexWorker(),           # Code generation
    "claude": ClaudeHaikuWorker(),    # Requirements processing
    "deepseek": DeepSeekWorker()      # Testing
}

# Spawn 50 tasks: "Generate REST endpoint for X"
# Codex generates 50 endpoint implementations in parallel
```

### 2. Documentation Automation
```python
# Extract code, have Codex generate docs, Claude enhances
codex_task = create_code_task(
    "if.code_documentation",
    "Generate Sphinx-compatible docstrings for this Python module",
    context=open("mymodule.py").read()
)
```

### 3. Cross-Language Translation
```python
# Codex translates between languages
for lang in ["javascript", "go", "rust", "python"]:
    create_code_task(
        "if.code_generation",
        f"Translate this algorithm to {lang}",
        language=lang,
        context=original_python_code
    )
```

---

## Troubleshooting

### Redis Connection Issues
```python
# Check Redis is running
redis-cli ping
# Output: PONG

# Check queue has tasks
redis-cli LLEN queue:if.code_generation
```

### Codex Task Timeout
```python
# Increase max_tokens if response is truncated
response = self.client.chat.completions.create(
    model="gpt-4",
    max_tokens=8192,  # Increased from 4096
    ...
)
```

### View Findings in Redis
```bash
# List all findings
redis-cli KEYS "finding:*"

# Get specific finding
redis-cli GET finding:abc123 | jq

# List findings for a task
redis-cli LRANGE task:task_xyz:findings 0 -1
```

---

## Full Working Example: End-to-End

```python
#!/usr/bin/env python3
"""
Complete example: Create tasks, run Codex worker, collect findings.
"""

import os
import sys
import time
import json
import redis
import uuid
from datetime import datetime

# Import or paste CodexWorker class above
from redis_swarm_codex import CodexWorker, create_code_task

def main():
    print("🚀 Redis Swarm - Codex Worker Demo")
    print("=" * 60)

    # Initialize Redis
    r = redis.Redis(host='localhost', decode_responses=True)

    # Clear old tasks/findings
    print("\n🗑️  Clearing old tasks...")
    r.delete("queue:if.code_generation")
    for key in r.keys("task:*"):
        r.delete(key)

    # Create tasks
    print("\n📝 Creating code generation tasks...")
    tasks = [
        "Generate a Python decorator for rate limiting with sliding window algorithm",
        "Create a lightweight HTTP client class with retry logic",
        "Generate TypeScript types for a REST API response",
        "Refactor: Optimize bubble sort to use early termination",
        "Document this Redis Swarm pattern with usage examples"
    ]

    task_ids = []
    for i, prompt in enumerate(tasks):
        task_id = create_code_task(
            "if.code_generation",
            prompt,
            language="python" if i < 3 else ("typescript" if i == 2 else "python")
        )
        task_ids.append(task_id)
        time.sleep(0.1)  # Small delay

    print(f"✅ Created {len(task_ids)} tasks")

    # Run Codex worker
    print("\n🤖 Starting Codex worker...")
    codex = CodexWorker()
    completed = codex.claim_and_execute("if.code_generation", max_tasks=10)

    print(f"\n✅ Codex completed {completed} tasks")

    # Retrieve findings
    print("\n📊 Collecting findings...")
    findings = []
    for task_id in task_ids:
        finding_ids = r.lrange(f"task:{task_id}:findings", 0, -1)
        for finding_id in finding_ids:
            finding = json.loads(r.get(f"finding:{finding_id}"))
            findings.append(finding)

    print(f"\n📈 Results:")
    print(f"   Tasks spawned: {len(task_ids)}")
    print(f"   Tasks completed: {completed}")
    print(f"   Findings collected: {len(findings)}")

    for i, f in enumerate(findings, 1):
        print(f"\n   Finding {i}:")
        print(f"     Summary: {f.get('summary')}")
        print(f"     Tokens: {f.get('tokens_used')}")
        if f.get('code'):
            lines = len(f['code'].split('\n'))
            print(f"     Code: {lines} lines")

    print("\n✅ Demo complete!")

if __name__ == "__main__":
    main()
```

Run it:
```bash
python example_end_to_end.py
```

---

## Summary: Codex in Redis Swarm

✅ **Codex is specialized for code generation, documentation, and technical writing**
✅ **Integrates seamlessly with Claude, Gemini, GPT-4, DeepSeek via Redis**
✅ **Cost-efficient for code tasks: use when ROI justifies premium over Haiku**
✅ **Parallel execution: Codex workers run alongside other vendors, no blocking**
✅ **Standard protocol: Same Redis queues, same finding format, same coordination**

**Next Steps:**
1. Set environment variable `OPENAI_API_KEY`
2. Ensure Redis is running (`redis-server` or remote)
3. Copy CodexWorker class into your project
4. Create tasks with `create_code_task()`
5. Run Codex worker: `python main_codex_worker.py`
6. Query findings from Redis

**Documentation Reference:**
- `/home/setup/infrafabric/swarm-architecture/MULTI_VENDOR_SWARM.md` - Full architecture
- `/home/setup/infrafabric/swarm-architecture/SIMPLE_INIT_PROMPTS.md` - Task/memory pattern
- `/home/setup/infrafabric/swarm-architecture/redis_swarm_coordinator.py` - Coordinator implementation

---

**Generated by Claude Code | 2025-11-21**
**Architecture: Multi-Vendor AI Swarm via Redis**
**Codex Specialization: Code Generation, Refactoring, Technical Documentation**
