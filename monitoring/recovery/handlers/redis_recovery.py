#!/usr/bin/env python3
"""
Redis Recovery Handler

Implements recovery strategies for Redis connection failures, latency issues,
and memory pressure.

Citation: if://agent/A35_redis_recovery_handler
Author: Agent A35
Date: 2025-11-30
"""

import logging
import redis
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)


def handle_redis_recovery(strategy: str, context: Dict[str, Any],
                         orchestrator: Any) -> bool:
    """
    Execute Redis recovery strategy.

    Args:
        strategy: Recovery strategy name
        context: Context with additional parameters
        orchestrator: Parent recovery orchestrator

    Returns:
        True if recovery successful, False otherwise
    """
    host = context.get('host', 'localhost')
    port = context.get('port', 6379)

    if strategy == 'reconnect':
        return _handle_reconnect(host, port)
    elif strategy == 'flush_corrupted':
        return _handle_flush_corrupted(host, port)
    elif strategy == 'restart_container':
        return _handle_restart_container(context)
    else:
        logger.warning(f"Unknown Redis recovery strategy: {strategy}")
        return False


def _handle_reconnect(host: str, port: int) -> bool:
    """Recreate connection pool with backoff."""
    try:
        logger.info(f"Redis reconnect: Attempting to connect to {host}:{port}")

        # Create new connection with retry
        max_retries = 3
        backoff_multiplier = 2
        timeout = 5

        for attempt in range(max_retries):
            try:
                conn = redis.Redis(
                    host=host,
                    port=port,
                    decode_responses=True,
                    socket_timeout=timeout,
                    socket_connect_timeout=timeout,
                    health_check_interval=30
                )

                # Test connection
                conn.ping()
                logger.info("Redis reconnect: Connection successful")
                conn.close()
                return True

            except redis.ConnectionError as e:
                wait_time = timeout * (backoff_multiplier ** attempt)
                logger.warning(
                    f"Redis reconnect: Attempt {attempt + 1}/{max_retries} failed, "
                    f"waiting {wait_time}s before retry: {e}"
                )
                time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Redis reconnect: Unexpected error: {e}")
                return False

        logger.error("Redis reconnect: All retry attempts failed")
        return False

    except Exception as e:
        logger.error(f"Redis reconnect handler error: {e}", exc_info=True)
        return False


def _handle_flush_corrupted(host: str, port: int) -> bool:
    """Flush corrupted keys after TTL check."""
    try:
        logger.info(f"Redis flush corrupted: Connecting to {host}:{port}")

        conn = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
            socket_timeout=5
        )

        # Get all keys
        keys = conn.keys('*')
        logger.info(f"Redis flush corrupted: Found {len(keys)} keys")

        # Flush keys without TTL (potentially corrupted)
        flushed_count = 0
        for key in keys:
            try:
                ttl = conn.ttl(key)
                # TTL: -1 = no expiry, -2 = key not exist
                if ttl == -1:
                    conn.delete(key)
                    flushed_count += 1
            except Exception as e:
                logger.debug(f"Could not flush key {key}: {e}")

        logger.info(f"Redis flush corrupted: Flushed {flushed_count} keys")
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Redis flush corrupted handler error: {e}", exc_info=True)
        return False


def _handle_restart_container(context: Dict[str, Any]) -> bool:
    """Restart Redis container (requires approval)."""
    container_id = context.get('container_id')

    if not container_id:
        logger.error("Redis restart: container_id not provided in context")
        return False

    try:
        import subprocess

        logger.warning(f"Redis restart: Restarting container {container_id}")

        # Restart container
        result = subprocess.run(
            ['docker', 'restart', container_id],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            logger.info(f"Redis restart: Container {container_id} restarted successfully")
            time.sleep(2)  # Wait for container to be ready

            # Verify connection
            host = context.get('host', 'localhost')
            port = context.get('port', 6379)
            try:
                conn = redis.Redis(
                    host=host,
                    port=port,
                    socket_timeout=5
                )
                conn.ping()
                conn.close()
                logger.info("Redis restart: Connection verified")
                return True
            except Exception as e:
                logger.error(f"Redis restart: Connection verification failed: {e}")
                return False
        else:
            logger.error(f"Redis restart: Failed - {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Redis restart handler error: {e}", exc_info=True)
        return False
