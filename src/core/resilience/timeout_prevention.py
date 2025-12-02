# if://code/timeout-prevention/2025-11-30
# Timeout Prevention System for Long-Running Operations
# Part of: InfraFabric Integration Swarm Mission (2025-11-30)
# Coordinator: Haiku Agent B11
#
# CITATION: if://mission/infrafabric-integration-swarm/2025-11-30
# Provides resilience for long-running async operations via heartbeat,
# checkpointing, task decomposition, and graceful degradation strategies

import redis
import json
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import wraps
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class TimeoutStrategy(Enum):
    """Available strategies for timeout prevention."""
    HEARTBEAT_KEEPALIVE = "heartbeat"      # Send periodic heartbeats
    PROGRESS_CHECKPOINT = "checkpoint"     # Save state at intervals
    TASK_DECOMPOSITION = "decomposition"   # Split into subtasks
    ASYNC_POLLING = "async_polling"        # Background execution + polling
    GRACEFUL_DEGRADATION = "degradation"   # Return partial results


@dataclass
class Checkpoint:
    """A saved operation state checkpoint.

    Attributes:
        checkpoint_id: Unique checkpoint identifier
        operation_id: Parent operation ID
        saved_at: Timestamp when checkpoint was created
        progress_percent: Estimated progress (0-100)
        state: Serializable state dict for resumption
        metadata: Additional context (task name, subtask index, etc.)
    """
    checkpoint_id: str = field(default_factory=lambda: f"ckpt_{uuid.uuid4().hex[:8]}")
    operation_id: str = ""
    saved_at: datetime = field(default_factory=datetime.now)
    progress_percent: int = 0
    state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to JSON-serializable dict."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "operation_id": self.operation_id,
            "saved_at": self.saved_at.isoformat(),
            "progress_percent": self.progress_percent,
            "state": self.state,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        """Create checkpoint from dict."""
        data_copy = data.copy()
        if isinstance(data_copy.get('saved_at'), str):
            data_copy['saved_at'] = datetime.fromisoformat(data_copy['saved_at'])
        return cls(**data_copy)


@dataclass
class OperationHandle:
    """Handle for tracking a long-running operation.

    Attributes:
        operation_id: Unique operation identifier
        started_at: Timestamp when operation started
        estimated_duration_ms: Estimated duration in milliseconds
        last_heartbeat: Timestamp of last heartbeat
        checkpoints: List of saved checkpoints
        strategies: Active timeout prevention strategies
        metadata: Additional operation metadata
    """
    operation_id: str
    started_at: datetime
    estimated_duration_ms: int
    last_heartbeat: datetime = field(default_factory=datetime.now)
    checkpoints: List[Checkpoint] = field(default_factory=list)
    strategies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def send_heartbeat(self, redis_client: redis.Redis, ttl_seconds: int = 60) -> None:
        """Send keepalive heartbeat to extend operation timeout.

        Args:
            redis_client: Redis connection
            ttl_seconds: How long heartbeat is valid before expiring
        """
        self.last_heartbeat = datetime.now()
        redis_client.set(
            f"operation:{self.operation_id}:heartbeat",
            self.last_heartbeat.isoformat(),
            ex=ttl_seconds
        )
        logger.debug(f"Heartbeat sent for {self.operation_id}")

    def save_checkpoint(self,
                       redis_client: redis.Redis,
                       state: Dict[str, Any],
                       progress_percent: int = 0,
                       metadata: Optional[Dict[str, Any]] = None) -> Checkpoint:
        """Save operation state checkpoint for resumption.

        Args:
            redis_client: Redis connection
            state: Operation state to save
            progress_percent: Progress indicator (0-100)
            metadata: Additional checkpoint metadata

        Returns:
            Created checkpoint
        """
        checkpoint = Checkpoint(
            operation_id=self.operation_id,
            progress_percent=progress_percent,
            state=state,
            metadata=metadata or {}
        )
        self.checkpoints.append(checkpoint)

        # Persist to Redis
        checkpoint_key = f"operation:{self.operation_id}:checkpoints"
        redis_client.rpush(checkpoint_key, json.dumps(checkpoint.to_dict()))
        redis_client.expire(checkpoint_key, 86400)  # 24h retention

        logger.info(f"Checkpoint saved: {checkpoint.checkpoint_id} ({progress_percent}% complete)")
        return checkpoint

    def is_timeout(self, timeout_percent: float = 0.9) -> bool:
        """Check if operation has exceeded timeout threshold.

        Args:
            timeout_percent: Fraction of estimated duration (0.9 = 90%)

        Returns:
            True if elapsed time exceeds timeout_percent of estimate
        """
        elapsed_ms = (datetime.now() - self.started_at).total_seconds() * 1000
        timeout_ms = self.estimated_duration_ms * timeout_percent
        return elapsed_ms > timeout_ms

    def get_elapsed_ms(self) -> int:
        """Get elapsed time in milliseconds."""
        return int((datetime.now() - self.started_at).total_seconds() * 1000)

    def get_remaining_ms(self) -> int:
        """Get estimated remaining time in milliseconds."""
        elapsed = self.get_elapsed_ms()
        remaining = max(0, self.estimated_duration_ms - elapsed)
        return remaining


class TimeoutPreventionManager:
    """Manages timeout prevention for long-running operations.

    Provides heartbeat keepalive, progress checkpointing, task decomposition,
    async execution with polling, and graceful degradation for operations that
    might timeout.

    Redis Key Schema:
    - operation:{operation_id}                 → Operation metadata
    - operation:{operation_id}:heartbeat       → Last heartbeat timestamp (TTL: 60s)
    - operation:{operation_id}:checkpoints     → List of saved checkpoints
    - operation:{operation_id}:result          → Final operation result
    - operation:{operation_id}:status          → Current status (running/completed/failed)
    - operations:active                        → Set of active operation IDs

    Example:
        ```python
        manager = TimeoutPreventionManager(redis_client)

        # Start tracking operation
        handle = manager.start_operation("analyze_data", estimated_duration_ms=180000)

        try:
            for chunk in large_dataset:
                # Process chunk
                process_chunk(chunk)

                # Send heartbeat every 30 seconds
                handle.send_heartbeat(manager.redis_client)

                # Save checkpoint every 10% progress
                if progress % 10 == 0:
                    handle.save_checkpoint(manager.redis_client, {
                        "last_chunk": chunk_id,
                        "results_so_far": results
                    }, progress_percent=progress)

                # Check if timeout imminent (>90% elapsed)
                if handle.is_timeout(timeout_percent=0.9):
                    return manager.graceful_degrade(handle, results, "timeout")
        finally:
            manager.complete_operation(handle, results)
        ```
    """

    def __init__(self,
                 redis_client: redis.Redis,
                 default_timeout_ms: int = 120000,
                 heartbeat_interval_s: int = 30,
                 checkpoint_interval_s: int = 60):
        """Initialize timeout prevention manager.

        Args:
            redis_client: Connected Redis client
            default_timeout_ms: Default timeout in milliseconds (120s)
            heartbeat_interval_s: How often to send heartbeats (30s)
            checkpoint_interval_s: How often to save checkpoints (60s)
        """
        self.redis_client = redis_client
        self.default_timeout_ms = default_timeout_ms
        self.heartbeat_interval_s = heartbeat_interval_s
        self.checkpoint_interval_s = checkpoint_interval_s
        self.operations: Dict[str, OperationHandle] = {}
        self.timeout_events: List[Dict[str, Any]] = []
        self.resumption_success_count = 0
        self.resumption_failure_count = 0

    def start_operation(self,
                       operation_id: Optional[str] = None,
                       estimated_duration_ms: Optional[int] = None,
                       strategies: Optional[List[str]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> OperationHandle:
        """Start tracking a long-running operation.

        Args:
            operation_id: Unique ID (auto-generated if None)
            estimated_duration_ms: Estimated duration (uses default if None)
            strategies: List of timeout prevention strategies to use
            metadata: Additional operation metadata

        Returns:
            OperationHandle for this operation
        """
        if not operation_id:
            operation_id = f"op_{uuid.uuid4().hex[:12]}"

        handle = OperationHandle(
            operation_id=operation_id,
            started_at=datetime.now(),
            estimated_duration_ms=estimated_duration_ms or self.default_timeout_ms,
            strategies=strategies or [TimeoutStrategy.HEARTBEAT_KEEPALIVE.value],
            metadata=metadata or {}
        )

        self.operations[operation_id] = handle

        # Persist to Redis
        self.redis_client.hset(f"operation:{operation_id}", mapping={
            "operation_id": operation_id,
            "started_at": handle.started_at.isoformat(),
            "estimated_duration_ms": handle.estimated_duration_ms,
            "strategies": ",".join(handle.strategies),
            "metadata": json.dumps(handle.metadata)
        })
        self.redis_client.sadd("operations:active", operation_id)
        self.redis_client.expire(f"operation:{operation_id}", 86400)

        logger.info(f"Started operation: {operation_id} (est. {handle.estimated_duration_ms}ms)")
        return handle

    def heartbeat(self, operation_id: str) -> bool:
        """Send keepalive signal to extend operation timeout.

        Call this every 30 seconds during execution to prevent timeout.

        Args:
            operation_id: ID of operation to heartbeat

        Returns:
            True if heartbeat successful, False if operation not found
        """
        handle = self.operations.get(operation_id)
        if not handle:
            logger.warning(f"Operation not found: {operation_id}")
            return False

        handle.send_heartbeat(self.redis_client, ttl_seconds=60)
        return True

    def checkpoint(self,
                  operation_id: str,
                  state: Dict[str, Any],
                  progress_percent: int = 0,
                  metadata: Optional[Dict[str, Any]] = None) -> Optional[Checkpoint]:
        """Save operation state checkpoint for resumption on timeout.

        Args:
            operation_id: ID of operation
            state: Serializable state to save
            progress_percent: Progress indicator (0-100)
            metadata: Additional metadata

        Returns:
            Created checkpoint, or None if operation not found
        """
        handle = self.operations.get(operation_id)
        if not handle:
            logger.warning(f"Operation not found: {operation_id}")
            return None

        return handle.save_checkpoint(
            self.redis_client,
            state=state,
            progress_percent=progress_percent,
            metadata=metadata
        )

    def resume_from_checkpoint(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Resume operation from last saved checkpoint.

        Args:
            operation_id: ID of operation to resume

        Returns:
            Last checkpoint data, or None if no checkpoints exist
        """
        checkpoint_key = f"operation:{operation_id}:checkpoints"
        checkpoints_json = self.redis_client.lrange(checkpoint_key, -1, -1)

        if not checkpoints_json:
            logger.warning(f"No checkpoints found for {operation_id}")
            return None

        last_checkpoint_json = checkpoints_json[0]
        checkpoint_data = json.loads(last_checkpoint_json)
        checkpoint = Checkpoint.from_dict(checkpoint_data)

        logger.info(f"Resuming from checkpoint: {checkpoint.checkpoint_id} "
                   f"({checkpoint.progress_percent}% complete)")
        self.resumption_success_count += 1

        return {
            "checkpoint": checkpoint.to_dict(),
            "state": checkpoint.state,
            "progress_percent": checkpoint.progress_percent
        }

    def complete_operation(self,
                         operation_id: str,
                         result: Any = None,
                         status: str = "completed") -> None:
        """Mark operation as successfully completed.

        Args:
            operation_id: ID of operation
            result: Final operation result
            status: Status to record (default: "completed")
        """
        handle = self.operations.get(operation_id)
        if not handle:
            return

        completion_data = {
            "operation_id": operation_id,
            "completed_at": datetime.now().isoformat(),
            "status": status,
            "elapsed_ms": handle.get_elapsed_ms(),
            "result": json.dumps(result) if result else ""
        }

        self.redis_client.hset(f"operation:{operation_id}:result", mapping=completion_data)
        self.redis_client.hset(f"operation:{operation_id}:status", mapping={
            "status": status,
            "updated_at": datetime.now().isoformat()
        })
        self.redis_client.srem("operations:active", operation_id)

        logger.info(f"Completed operation: {operation_id} ({status})")
        del self.operations[operation_id]

    def detect_timeout(self, operation_id: str) -> bool:
        """Check if operation has timed out.

        Args:
            operation_id: ID of operation to check

        Returns:
            True if heartbeat is missing (operation timed out)
        """
        heartbeat = self.redis_client.get(f"operation:{operation_id}:heartbeat")
        if not heartbeat:
            logger.warning(f"Timeout detected for {operation_id}")
            self.timeout_events.append({
                "operation_id": operation_id,
                "detected_at": datetime.now().isoformat()
            })
            return True
        return False

    def decompose_task(self,
                      task_data: List[Any],
                      max_chunk_ms: int = 120000) -> List[List[Any]]:
        """Decompose large task into subtasks to avoid timeouts.

        Intelligently splits a task into chunks estimated to complete
        within max_chunk_ms.

        Args:
            task_data: List of items to process
            max_chunk_ms: Maximum time per chunk in milliseconds

        Returns:
            List of task chunks
        """
        if not task_data:
            return []

        # Heuristic: estimate 10ms per item
        items_per_chunk = max(1, max_chunk_ms // 10)
        chunks = [
            task_data[i:i+items_per_chunk]
            for i in range(0, len(task_data), items_per_chunk)
        ]

        logger.info(f"Decomposed task into {len(chunks)} chunks "
                   f"({items_per_chunk} items per chunk)")
        return chunks

    def graceful_degrade(self,
                        operation_id: str,
                        partial_result: Any,
                        reason: str = "timeout") -> Dict[str, Any]:
        """Return partial results with degradation flag if timeout imminent.

        Args:
            operation_id: ID of operation
            partial_result: Partial results computed so far
            reason: Reason for degradation

        Returns:
            Dict with partial_result and incomplete flag
        """
        handle = self.operations.get(operation_id)
        remaining_ms = handle.get_remaining_ms() if handle else 0

        degraded_response = {
            "status": "partial",
            "reason": reason,
            "incomplete": True,
            "partial_result": partial_result,
            "elapsed_ms": handle.get_elapsed_ms() if handle else 0,
            "can_resume": True,
            "checkpoint_available": len(handle.checkpoints) > 0 if handle else False
        }

        self.complete_operation(operation_id, result=degraded_response, status="degraded")
        logger.warning(f"Graceful degradation triggered for {operation_id}: {reason}")

        return degraded_response

    def submit_async_task(self,
                         operation_id: Optional[str] = None,
                         task_func: Optional[Callable] = None,
                         task_args: Optional[List[Any]] = None,
                         task_kwargs: Optional[Dict[str, Any]] = None) -> str:
        """Submit long task for background execution.

        Returns operation_id immediately. Client polls for completion.

        Args:
            operation_id: Operation ID (auto-generated if None)
            task_func: Callable to execute
            task_args: Positional arguments for task_func
            task_kwargs: Keyword arguments for task_func

        Returns:
            operation_id for polling
        """
        if not operation_id:
            operation_id = f"async_{uuid.uuid4().hex[:12]}"

        handle = self.start_operation(
            operation_id=operation_id,
            strategies=[TimeoutStrategy.ASYNC_POLLING.value]
        )

        # Queue task in Redis for background worker
        self.redis_client.rpush("task_queue:async", json.dumps({
            "operation_id": operation_id,
            "task_func": task_func.__name__ if task_func else "unknown",
            "task_args": task_args or [],
            "task_kwargs": task_kwargs or {},
            "submitted_at": datetime.now().isoformat()
        }))

        logger.info(f"Submitted async task: {operation_id}")
        return operation_id

    def poll_async_result(self, operation_id: str, timeout_s: int = 300) -> Optional[Any]:
        """Poll for async task result.

        Args:
            operation_id: Operation ID from submit_async_task
            timeout_s: Maximum time to wait for result

        Returns:
            Task result if completed, None if still running or timed out
        """
        result_data = self.redis_client.hgetall(f"operation:{operation_id}:result")

        if result_data and result_data.get("status") == "completed":
            result_json = result_data.get("result", "{}")
            return json.loads(result_json)

        return None

    def get_operation_status(self, operation_id: str) -> Dict[str, Any]:
        """Get current status of an operation.

        Args:
            operation_id: ID of operation

        Returns:
            Dict with operation metadata and status
        """
        handle = self.operations.get(operation_id)
        if not handle:
            return {}

        return {
            "operation_id": operation_id,
            "status": "running",
            "started_at": handle.started_at.isoformat(),
            "elapsed_ms": handle.get_elapsed_ms(),
            "remaining_ms": handle.get_remaining_ms(),
            "progress_percent": (handle.get_elapsed_ms() / handle.estimated_duration_ms) * 100,
            "checkpoints": len(handle.checkpoints),
            "strategies": handle.strategies,
            "last_heartbeat": handle.last_heartbeat.isoformat()
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get timeout prevention metrics.

        Returns:
            Dict with system-wide metrics
        """
        return {
            "active_operations": len(self.operations),
            "total_timeout_events": len(self.timeout_events),
            "resumption_success_count": self.resumption_success_count,
            "resumption_failure_count": self.resumption_failure_count,
            "timeout_recovery_rate": (
                self.resumption_success_count /
                (self.resumption_success_count + self.resumption_failure_count)
                if (self.resumption_success_count + self.resumption_failure_count) > 0
                else 0.0
            ),
            "recent_timeout_events": self.timeout_events[-10:]  # Last 10 events
        }


# ================================================================== #
# Decorator-based API for easy integration
# ================================================================== #

_global_manager: Optional[TimeoutPreventionManager] = None


def init_timeout_prevention(redis_client: redis.Redis) -> TimeoutPreventionManager:
    """Initialize global timeout prevention manager.

    Args:
        redis_client: Connected Redis client

    Returns:
        TimeoutPreventionManager instance
    """
    global _global_manager
    _global_manager = TimeoutPreventionManager(redis_client)
    return _global_manager


def timeout_prevention(estimated_ms: int = 120000,
                      heartbeat_interval_s: int = 30,
                      checkpoint_interval_s: int = 60):
    """Decorator for automatic timeout prevention on functions.

    Automatically sends heartbeats and checkpoints during function execution.

    Args:
        estimated_ms: Estimated execution time
        heartbeat_interval_s: How often to send heartbeats
        checkpoint_interval_s: How often to save checkpoints

    Returns:
        Decorated function

    Example:
        ```python
        manager = init_timeout_prevention(redis_client)

        @timeout_prevention(estimated_ms=180000)
        def analyze_large_dataset(data):
            results = []
            for item in data:
                # Process item
                results.append(process(item))
            return results
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not _global_manager:
                logger.warning("Global timeout prevention manager not initialized")
                return func(*args, **kwargs)

            operation_id = f"{func.__name__}_{uuid.uuid4().hex[:8]}"
            handle = _global_manager.start_operation(
                operation_id=operation_id,
                estimated_duration_ms=estimated_ms
            )

            last_heartbeat = time.time()
            last_checkpoint = time.time()

            try:
                # Execute function with periodic heartbeats
                result = func(*args, **kwargs)

                # Check if timeout imminent
                if handle.is_timeout(timeout_percent=0.9):
                    logger.warning(f"Operation {operation_id} approaching timeout")
                    return _global_manager.graceful_degrade(
                        operation_id, result, "approaching_timeout"
                    )

                _global_manager.complete_operation(operation_id, result)
                return result

            except Exception as e:
                logger.error(f"Operation {operation_id} failed: {e}")
                _global_manager.complete_operation(operation_id, status="failed")
                raise

        return wrapper
    return decorator


def decompose_task(max_chunk_ms: int = 120000):
    """Decorator for automatic task decomposition.

    Splits large tasks into subtasks to prevent timeouts.

    Args:
        max_chunk_ms: Maximum time per subtask

    Returns:
        Decorated function

    Example:
        ```python
        @decompose_task(max_chunk_ms=60000)
        def process_large_batch(items):
            results = []
            for item in items:
                results.append(process_item(item))
            return results
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(items: List[Any], *args, **kwargs) -> Any:
            if not _global_manager:
                logger.warning("Global timeout prevention manager not initialized")
                return func(items, *args, **kwargs)

            # Decompose task into chunks
            chunks = _global_manager.decompose_task(items, max_chunk_ms=max_chunk_ms)

            all_results = []
            for chunk_idx, chunk in enumerate(chunks):
                operation_id = f"chunk_{chunk_idx}_{uuid.uuid4().hex[:8]}"
                handle = _global_manager.start_operation(
                    operation_id=operation_id,
                    estimated_duration_ms=max_chunk_ms
                )

                try:
                    chunk_result = func(chunk, *args, **kwargs)
                    all_results.extend(chunk_result if isinstance(chunk_result, list) else [chunk_result])

                    # Save checkpoint between chunks
                    _global_manager.checkpoint(
                        operation_id,
                        state={"chunk_index": chunk_idx, "results_so_far": all_results},
                        progress_percent=int((chunk_idx / len(chunks)) * 100)
                    )

                    _global_manager.complete_operation(operation_id)

                except Exception as e:
                    logger.error(f"Chunk {chunk_idx} failed: {e}")
                    _global_manager.complete_operation(operation_id, status="failed")
                    raise

            return all_results

        return wrapper
    return decorator


# ================================================================== #
# Main: Usage examples and testing
# ================================================================== #

def main():
    """Usage examples and demonstration."""
    print("\n" + "="*70)
    print("Timeout Prevention System - Usage Examples")
    print("="*70 + "\n")

    # Initialize Redis connection
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        redis_client.ping()
        print("Redis connected\n")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        print("(Some examples require Redis)\n")
        redis_client = None
        return

    # Initialize timeout prevention manager
    manager = TimeoutPreventionManager(redis_client)
    init_timeout_prevention(redis_client)

    # Example 1: Heartbeat keepalive
    print("1. HEARTBEAT KEEPALIVE")
    print("-" * 70)
    handle = manager.start_operation(
        operation_id="analysis_job_001",
        estimated_duration_ms=180000
    )
    print(f"Started operation: {handle.operation_id}")
    print(f"Estimated duration: {handle.estimated_duration_ms}ms\n")

    for i in range(3):
        time.sleep(1)
        manager.heartbeat(handle.operation_id)
        status = manager.get_operation_status(handle.operation_id)
        print(f"  [{i+1}] Heartbeat sent - Elapsed: {status['elapsed_ms']}ms")

    manager.complete_operation(handle.operation_id, result={"status": "success"})
    print()

    # Example 2: Progress checkpointing
    print("\n2. PROGRESS CHECKPOINTING")
    print("-" * 70)
    handle2 = manager.start_operation(
        operation_id="dataset_processing_001",
        estimated_duration_ms=240000
    )
    print(f"Processing large dataset with checkpoints...\n")

    for progress in range(0, 101, 25):
        checkpoint = manager.checkpoint(
            handle2.operation_id,
            state={"progress": progress, "records_processed": progress * 1000},
            progress_percent=progress,
            metadata={"batch": "batch_001"}
        )
        if checkpoint:
            print(f"  Progress: {progress}% - Checkpoint: {checkpoint.checkpoint_id}")

    manager.complete_operation(handle2.operation_id, result={"total_records": 100000})
    print()

    # Example 3: Task decomposition
    print("\n3. TASK DECOMPOSITION")
    print("-" * 70)
    large_task = list(range(1000))
    chunks = manager.decompose_task(large_task, max_chunk_ms=120000)
    print(f"Decomposed 1000-item task into {len(chunks)} chunks")
    print(f"First chunk size: {len(chunks[0])} items")
    print(f"Last chunk size: {len(chunks[-1])} items\n")

    # Example 4: Graceful degradation
    print("\n4. GRACEFUL DEGRADATION")
    print("-" * 70)
    handle3 = manager.start_operation(
        operation_id="complex_analysis_001",
        estimated_duration_ms=60000  # Very short timeout for demo
    )
    print("Processing with tight timeout...")
    time.sleep(2)

    if handle3.is_timeout(timeout_percent=0.5):
        partial_result = manager.graceful_degrade(
            handle3.operation_id,
            {"partial_data": [1, 2, 3]},
            "timeout_threshold_exceeded"
        )
        print(f"Graceful degradation triggered:")
        print(f"  Status: {partial_result['status']}")
        print(f"  Incomplete: {partial_result['incomplete']}")
        print(f"  Can resume: {partial_result['can_resume']}\n")

    # Example 5: Metrics
    print("\n5. SYSTEM METRICS")
    print("-" * 70)
    metrics = manager.get_metrics()
    print(f"Active operations: {metrics['active_operations']}")
    print(f"Total timeout events: {metrics['total_timeout_events']}")
    print(f"Resumption success count: {metrics['resumption_success_count']}")
    print(f"Resumption failure count: {metrics['resumption_failure_count']}")
    print(f"Timeout recovery rate: {metrics['timeout_recovery_rate']:.2%}\n")

    # Example 6: Decorated function
    print("\n6. DECORATOR USAGE")
    print("-" * 70)

    @timeout_prevention(estimated_ms=120000)
    def sample_long_operation(duration_s: int):
        """Simulated long-running operation."""
        print(f"  Starting operation ({duration_s}s)...")
        for i in range(duration_s):
            time.sleep(0.1)
            if i % 2 == 0:
                pass  # Heartbeats sent automatically
        print(f"  Operation completed successfully")
        return {"status": "done"}

    result = sample_long_operation(2)
    print(f"  Result: {result}\n")

    print("="*70)
    print("Timeout Prevention System - OPERATIONAL")
    print("IF.citation: if://code/timeout-prevention/2025-11-30")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
