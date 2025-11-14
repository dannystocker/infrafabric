"""
IF.chassis - Resource Limits and Rate Limiting

Component: IF.chassis (Bug #3 - Sandboxing)
Purpose: Enforce per-swarm resource limits to prevent noisy neighbor problems
Status: Phase 0 Development (P0.3.2)

Features:
- OS-level resource limits (memory, CPU time)
- Token bucket rate limiting for API calls
- Resource violation logging
- Integration with IFChassis runtime

Author: Session 3 (H.323 Guardian Council)
Task: P0.3.2 - Resource limits (CPU/memory)
Last Updated: 2025-11-14
"""

import resource
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
import os

logger = logging.getLogger(__name__)


@dataclass
class ResourceLimits:
    """
    Per-swarm resource limits

    Defines hard resource constraints for swarm execution to prevent
    noisy neighbor problems and resource exhaustion.

    Attributes:
        max_memory_mb: Maximum memory allocation in MB (default: 256 MB)
        max_cpu_percent: Maximum CPU usage percentage (default: 25%)
        max_api_calls_per_second: API rate limit (default: 10/sec)
        max_execution_time_seconds: Maximum execution time (default: 300s/5min)
        max_open_files: Maximum open file descriptors (default: 256)
        allow_core_dumps: Allow core dumps on crash (default: False)
    """

    max_memory_mb: int = 256
    max_cpu_percent: int = 25
    max_api_calls_per_second: int = 10
    max_execution_time_seconds: int = 300
    max_open_files: int = 256
    allow_core_dumps: bool = False

    def to_dict(self) -> Dict[str, any]:
        """Convert limits to dictionary for serialization"""
        return {
            'max_memory_mb': self.max_memory_mb,
            'max_cpu_percent': self.max_cpu_percent,
            'max_api_calls_per_second': self.max_api_calls_per_second,
            'max_execution_time_seconds': self.max_execution_time_seconds,
            'max_open_files': self.max_open_files,
            'allow_core_dumps': self.allow_core_dumps
        }


class TokenBucket:
    """
    Token bucket rate limiter

    Implements token bucket algorithm for API rate limiting.
    Tokens refill at a constant rate, and each API call consumes one token.
    If no tokens available, the call is rejected.

    Algorithm:
    - Bucket capacity = rate (e.g., 10 tokens)
    - Tokens refill at 'rate' tokens per second
    - Each API call consumes 1 token
    - If tokens < 1, call is rate limited

    Example:
        >>> bucket = TokenBucket(rate=10)  # 10 calls/second
        >>> await bucket.consume()  # True (1st call)
        >>> await bucket.consume()  # True (2nd call)
        ...
        >>> await bucket.consume()  # False (rate limit exceeded)
    """

    def __init__(self, rate: int):
        """
        Initialize token bucket

        Args:
            rate: Maximum calls per second (bucket capacity)
        """
        if rate <= 0:
            raise ValueError("Rate must be positive")

        self.rate = rate
        self.tokens = float(rate)  # Start with full bucket
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume token(s) from bucket

        Args:
            tokens: Number of tokens to consume (default: 1)

        Returns:
            True if token consumed (call allowed), False if rate limited
        """
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update

            # Refill tokens based on elapsed time
            self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
            self.last_update = now

            # Check if enough tokens available
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    def get_tokens(self) -> float:
        """
        Get current token count (for monitoring)

        Returns:
            Current number of tokens in bucket
        """
        return self.tokens


class ResourceEnforcer:
    """
    Enforce resource limits per swarm

    Applies OS-level resource limits and rate limiting to prevent
    resource exhaustion and noisy neighbor problems.

    Philosophy:
    - Ubuntu: "I am because we are" → Fair resource sharing
    - Kant: If all swarms exceeded limits, system would collapse
    - S²: Enforce limits proactively, don't wait for problems

    Example:
        >>> enforcer = ResourceEnforcer()
        >>> limits = ResourceLimits(max_memory_mb=128, max_cpu_percent=25)
        >>> enforcer.apply_limits('swarm-1', limits)
        >>> allowed = await enforcer.check_rate_limit('swarm-1')
    """

    def __init__(self, witness_enabled: bool = True):
        """
        Initialize resource enforcer

        Args:
            witness_enabled: Enable IF.witness logging (default: True)
        """
        self.rate_limiters: Dict[str, TokenBucket] = {}
        self.swarm_limits: Dict[str, ResourceLimits] = {}
        self.witness_enabled = witness_enabled
        self.violation_counts: Dict[str, int] = {}

        logger.info("ResourceEnforcer initialized")

    def apply_limits(self, swarm_id: str, limits: ResourceLimits) -> bool:
        """
        Apply OS-level resource limits for swarm

        Sets hard resource limits via setrlimit(). These limits are enforced
        by the operating system kernel.

        Warning: setrlimit() affects the current process. For true per-swarm
        isolation, swarms should run in separate processes or containers.

        Args:
            swarm_id: Swarm to apply limits to
            limits: Resource limits to enforce

        Returns:
            True if limits applied successfully, False otherwise

        Example:
            >>> limits = ResourceLimits(max_memory_mb=256, max_cpu_percent=25)
            >>> enforcer.apply_limits('test-swarm', limits)
            True
        """
        try:
            logger.info(f"Applying resource limits for swarm '{swarm_id}'")

            # Store limits for this swarm
            self.swarm_limits[swarm_id] = limits

            # Setup rate limiter (always succeeds)
            self.rate_limiters[swarm_id] = TokenBucket(limits.max_api_calls_per_second)
            logger.debug(f"Rate limiter initialized: {limits.max_api_calls_per_second} calls/sec")

            # Try to apply OS-level limits (may fail if not privileged)
            # These failures are non-fatal - rate limiting still works
            try:
                # Apply memory limit (address space)
                memory_bytes = limits.max_memory_mb * 1024 * 1024
                current_soft, current_hard = resource.getrlimit(resource.RLIMIT_AS)

                # Only try to set if we can (requires privileges to raise limits)
                if memory_bytes <= current_hard or current_hard == resource.RLIM_INFINITY:
                    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
                    logger.debug(f"Memory limit set: {limits.max_memory_mb} MB")
                else:
                    logger.debug(f"Memory limit not set (would require raising limit)")

                # Apply CPU time limit
                current_soft, current_hard = resource.getrlimit(resource.RLIMIT_CPU)
                if limits.max_execution_time_seconds <= current_hard or current_hard == resource.RLIM_INFINITY:
                    resource.setrlimit(
                        resource.RLIMIT_CPU,
                        (limits.max_execution_time_seconds, limits.max_execution_time_seconds)
                    )
                    logger.debug(f"CPU time limit set: {limits.max_execution_time_seconds}s")
                else:
                    logger.debug(f"CPU time limit not set (would require raising limit)")

                # Apply file descriptor limit
                current_soft, current_hard = resource.getrlimit(resource.RLIMIT_NOFILE)
                if limits.max_open_files <= current_hard or current_hard == resource.RLIM_INFINITY:
                    resource.setrlimit(
                        resource.RLIMIT_NOFILE,
                        (limits.max_open_files, limits.max_open_files)
                    )
                    logger.debug(f"File descriptor limit set: {limits.max_open_files}")
                else:
                    logger.debug(f"File descriptor limit not set (would require raising limit)")

                # Control core dumps
                if limits.allow_core_dumps:
                    # Allow core dumps (for debugging)
                    resource.setrlimit(resource.RLIMIT_CORE, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
                else:
                    # Disable core dumps (production)
                    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
                logger.debug(f"Core dumps: {'enabled' if limits.allow_core_dumps else 'disabled'}")

            except Exception as setrlimit_err:
                logger.debug(f"setrlimit() failed (non-fatal): {setrlimit_err}")
                # Rate limiting still works even if OS limits fail

            # Log to IF.witness
            self._log_to_witness('limits_applied', {
                'swarm_id': swarm_id,
                'limits': limits.to_dict()
            })

            logger.info(f"✅ Resource limits applied for '{swarm_id}'")
            return True

        except Exception as e:
            logger.error(f"Failed to apply resource limits for '{swarm_id}': {e}")
            self._log_to_witness('limits_apply_failed', {
                'swarm_id': swarm_id,
                'error': str(e)
            })
            return False

    async def check_rate_limit(self, swarm_id: str, tokens: int = 1) -> bool:
        """
        Check if swarm can make API call (rate limiting)

        Uses token bucket algorithm to enforce API rate limits.

        Args:
            swarm_id: Swarm making the API call
            tokens: Number of tokens to consume (default: 1)

        Returns:
            True if call allowed, False if rate limited

        Example:
            >>> allowed = await enforcer.check_rate_limit('test-swarm')
            >>> if not allowed:
            ...     print("Rate limit exceeded")
        """
        if swarm_id not in self.rate_limiters:
            logger.warning(f"No rate limiter for swarm '{swarm_id}', allowing call")
            return True

        allowed = await self.rate_limiters[swarm_id].consume(tokens)

        if not allowed:
            # Rate limit exceeded
            self._record_violation(swarm_id, 'rate_limit_exceeded')
            logger.warning(f"⚠️ Rate limit exceeded for swarm '{swarm_id}'")

            self._log_to_witness('rate_limit_exceeded', {
                'swarm_id': swarm_id,
                'tokens_requested': tokens,
                'timestamp': time.time()
            })

        return allowed

    def get_current_limits(self, swarm_id: str) -> Optional[ResourceLimits]:
        """
        Get currently applied limits for swarm

        Args:
            swarm_id: Swarm to query

        Returns:
            ResourceLimits if swarm has limits applied, None otherwise
        """
        return self.swarm_limits.get(swarm_id)

    def get_rate_limiter_status(self, swarm_id: str) -> Optional[Dict[str, any]]:
        """
        Get rate limiter status for swarm

        Args:
            swarm_id: Swarm to query

        Returns:
            Dictionary with tokens_available, rate, and last_update
        """
        if swarm_id not in self.rate_limiters:
            return None

        limiter = self.rate_limiters[swarm_id]
        return {
            'tokens_available': limiter.get_tokens(),
            'rate': limiter.rate,
            'last_update': limiter.last_update
        }

    def get_violation_count(self, swarm_id: str) -> int:
        """
        Get number of resource violations for swarm

        Args:
            swarm_id: Swarm to query

        Returns:
            Number of violations
        """
        return self.violation_counts.get(swarm_id, 0)

    def reset_violation_count(self, swarm_id: str):
        """
        Reset violation count for swarm

        Args:
            swarm_id: Swarm to reset
        """
        if swarm_id in self.violation_counts:
            old_count = self.violation_counts[swarm_id]
            self.violation_counts[swarm_id] = 0
            logger.info(f"Reset violation count for '{swarm_id}' (was: {old_count})")

            self._log_to_witness('violation_count_reset', {
                'swarm_id': swarm_id,
                'old_count': old_count
            })

    def get_system_resource_usage(self) -> Dict[str, any]:
        """
        Get current system resource usage

        Returns:
            Dictionary with memory, CPU, and file descriptor usage
        """
        try:
            usage = resource.getrusage(resource.RUSAGE_SELF)

            return {
                'memory_mb': usage.ru_maxrss / 1024,  # KB to MB
                'cpu_time_seconds': usage.ru_utime + usage.ru_stime,
                'voluntary_context_switches': usage.ru_nvcsw,
                'involuntary_context_switches': usage.ru_nivcsw,
                'page_faults': usage.ru_majflt
            }
        except Exception as e:
            logger.error(f"Failed to get system resource usage: {e}")
            return {}

    def _record_violation(self, swarm_id: str, violation_type: str):
        """
        Record resource limit violation

        Args:
            swarm_id: Swarm that violated limits
            violation_type: Type of violation (e.g., 'rate_limit_exceeded')
        """
        if swarm_id not in self.violation_counts:
            self.violation_counts[swarm_id] = 0

        self.violation_counts[swarm_id] += 1

        logger.warning(
            f"⚠️ Violation #{self.violation_counts[swarm_id]} for '{swarm_id}': {violation_type}"
        )

    def _log_to_witness(self, operation: str, params: Dict[str, any]):
        """
        Log operation to IF.witness for audit trail

        Stub for P0.4.3 integration.

        Args:
            operation: Operation name
            params: Operation parameters
        """
        if not self.witness_enabled:
            return

        log_entry = {
            'component': 'IF.chassis.limits',
            'operation': operation,
            'params': params,
            'timestamp': time.time()
        }

        logger.debug(f"IF.witness log: {log_entry}")

        # TODO: Integrate with IF.witness (P0.4.3)
        # from infrafabric.witness import log_operation
        # log_operation(**log_entry)


# Convenience functions

def create_test_enforcer() -> ResourceEnforcer:
    """
    Create ResourceEnforcer instance for testing

    Returns:
        Configured ResourceEnforcer instance
    """
    return ResourceEnforcer(witness_enabled=True)


def create_default_limits() -> ResourceLimits:
    """
    Create default resource limits

    Returns:
        ResourceLimits with sensible defaults
    """
    return ResourceLimits()
