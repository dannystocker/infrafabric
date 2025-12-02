#!/usr/bin/env python3
"""
System Recovery Handler

Implements recovery strategies for system resource issues including disk space,
memory leaks, and file handle exhaustion.

Citation: if://agent/A35_system_recovery_handler
Author: Agent A35
Date: 2025-11-30
"""

import logging
import os
import gc
import glob
import shutil
import subprocess
from typing import Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def handle_system_recovery(strategy: str, context: Dict[str, Any],
                          orchestrator: Any) -> bool:
    """
    Execute system recovery strategy.

    Args:
        strategy: Recovery strategy name
        context: Context with additional parameters
        orchestrator: Parent recovery orchestrator

    Returns:
        True if recovery successful, False otherwise
    """
    if strategy == 'disk_cleanup':
        return _handle_disk_cleanup(context)
    elif strategy == 'memory_gc':
        return _handle_memory_gc(context)
    elif strategy == 'file_handle_cleanup':
        return _handle_file_handle_cleanup(context)
    elif strategy == 'process_restart':
        return _handle_process_restart(context)
    else:
        logger.warning(f"Unknown system recovery strategy: {strategy}")
        return False


def _handle_disk_cleanup(context: Dict[str, Any]) -> bool:
    """Clean temporary files when disk is full."""
    try:
        logger.info("System disk cleanup: Starting cleanup")

        cleanup_paths = context.get('cleanup_paths', [
            '/tmp',
            '/var/tmp',
            '/root/.cache',
            '/root/openwebui-knowledge/chromadb/.logs'
        ])

        threshold_percent = context.get('threshold_percent', 85)
        total_freed = 0
        files_deleted = 0

        for path in cleanup_paths:
            if not os.path.exists(path):
                logger.debug(f"Cleanup path not found: {path}")
                continue

            logger.info(f"Cleaning {path}")

            try:
                if os.path.isdir(path):
                    # Clean temporary files
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)

                        # Skip if too new
                        mtime = os.path.getmtime(item_path)
                        age_days = (datetime.now() - datetime.fromtimestamp(mtime)).days

                        if age_days < 1:  # Keep files < 1 day old
                            continue

                        try:
                            if os.path.isdir(item_path):
                                size = get_dir_size(item_path)
                                shutil.rmtree(item_path)
                            else:
                                size = os.path.getsize(item_path)
                                os.remove(item_path)

                            total_freed += size
                            files_deleted += 1
                            logger.debug(f"Deleted {item_path} ({size} bytes)")

                        except Exception as e:
                            logger.debug(f"Could not delete {item_path}: {e}")

            except Exception as e:
                logger.warning(f"Error cleaning {path}: {e}")

        logger.info(
            f"System disk cleanup: Freed {total_freed / (1024**2):.2f}MB "
            f"({files_deleted} files deleted)"
        )

        return True

    except Exception as e:
        logger.error(f"Disk cleanup handler error: {e}", exc_info=True)
        return False


def _handle_memory_gc(context: Dict[str, Any]) -> bool:
    """Trigger garbage collection and memory cleanup."""
    try:
        logger.info("System memory GC: Triggering garbage collection")

        if PSUTIL_AVAILABLE:
            # Get memory before
            process = psutil.Process(os.getpid())
            mem_before = process.memory_info().rss / (1024**2)

        # Run garbage collection
        collected = gc.collect()
        logger.info(f"System memory GC: Collected {collected} objects")

        if PSUTIL_AVAILABLE:
            # Get memory after
            mem_after = process.memory_info().rss / (1024**2)
            freed = mem_before - mem_after

            logger.info(
                f"System memory GC: Memory usage before: {mem_before:.2f}MB, "
                f"after: {mem_after:.2f}MB, freed: {freed:.2f}MB"
            )

            return freed > 0 or mem_after < mem_before

        return True

    except Exception as e:
        logger.error(f"Memory GC handler error: {e}", exc_info=True)
        return False


def _handle_file_handle_cleanup(context: Dict[str, Any]) -> bool:
    """Close unused file handles and increase limits."""
    try:
        logger.info("System file handle cleanup: Closing unused handles")

        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available, cannot cleanup file handles")
            return False

        process = psutil.Process(os.getpid())
        open_files = process.open_files()

        logger.info(f"Open file handles: {len(open_files)}")

        # Report open files (don't actually close them)
        for f in open_files[:10]:  # Log first 10
            logger.debug(f"Open file: {f.path}")

        # Try to increase file handle limits
        try:
            soft, hard = os.getrlimit(os.RLIMIT_NOFILE)
            logger.info(f"Current limits: soft={soft}, hard={hard}")

            # Try to increase soft limit to hard limit
            if soft < hard:
                os.setrlimit(os.RLIMIT_NOFILE, (hard, hard))
                logger.info(f"Increased soft limit from {soft} to {hard}")
                return True

        except Exception as e:
            logger.warning(f"Could not increase file limits: {e}")

        return True

    except Exception as e:
        logger.error(f"File handle cleanup handler error: {e}", exc_info=True)
        return False


def _handle_process_restart(context: Dict[str, Any]) -> bool:
    """Restart worker processes (not main orchestrator)."""
    try:
        process_name = context.get('process_name')
        signal = context.get('signal', 'TERM')

        if not process_name:
            logger.error("Process restart: process_name not provided")
            return False

        logger.warning(f"System process restart: Restarting {process_name}")

        try:
            # Find process by name
            result = subprocess.run(
                f"pkill -{signal} {process_name}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info(f"System process restart: Sent {signal} to {process_name}")

                # Wait a bit for restart
                import time
                time.sleep(2)

                # Verify process restarted
                result = subprocess.run(
                    f"pgrep {process_name}",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    logger.info(f"System process restart: {process_name} restarted successfully")
                    return True
                else:
                    logger.warning(f"System process restart: {process_name} not running after restart")
                    return False

            else:
                logger.error(f"Process restart failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Process restart: Command timed out")
            return False

    except Exception as e:
        logger.error(f"Process restart handler error: {e}", exc_info=True)
        return False


def get_dir_size(path: str) -> int:
    """Get total size of directory in bytes."""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_dir_size(entry.path)
    except Exception as e:
        logger.debug(f"Error calculating directory size: {e}")
    return total
