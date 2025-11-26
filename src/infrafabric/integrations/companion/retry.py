"""
Retry logic with exponential backoff

Used for network error handling.
"""

import asyncio
import logging
from typing import Callable, TypeVar

from .errors import CompanionError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryPolicy:
    """
    Exponential backoff retry policy.

    Example:
        policy = RetryPolicy(max_attempts=3, initial_backoff_ms=1000)
        result = await retry_with_backoff(my_func, policy=policy)
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_backoff_ms: int = 1000,
        max_backoff_ms: int = 10000,
        backoff_multiplier: float = 2.0,
    ):
        self.max_attempts = max_attempts
        self.initial_backoff_ms = initial_backoff_ms
        self.max_backoff_ms = max_backoff_ms
        self.backoff_multiplier = backoff_multiplier

    def get_delay(self, attempt: int) -> int:
        """Calculate delay for given attempt number"""
        delay = self.initial_backoff_ms * (self.backoff_multiplier**attempt)
        return min(delay, self.max_backoff_ms)


async def retry_with_backoff(
    func: Callable[..., T], *args, policy: RetryPolicy = None, **kwargs
) -> T:
    """
    Execute function with exponential backoff retry.

    Only retries on CompanionError with is_retryable=True.

    Args:
        func: Async function to execute
        policy: Retry policy (default: 3 attempts)
        *args, **kwargs: Passed to func

    Returns:
        Result of func

    Raises:
        CompanionError: If max retries exceeded or non-retryable error
    """
    policy = policy or RetryPolicy()

    last_error = None

    for attempt in range(policy.max_attempts):
        try:
            return await func(*args, **kwargs)

        except CompanionError as e:
            last_error = e

            if not e.is_retryable:
                # Non-retryable error, fail immediately
                raise

            if attempt < policy.max_attempts - 1:
                # Calculate backoff delay
                delay_ms = policy.get_delay(attempt)

                logger.warning(
                    f"Attempt {attempt + 1} failed: {e.message}. "
                    f"Retrying in {delay_ms}ms..."
                )

                await asyncio.sleep(delay_ms / 1000.0)
            else:
                # Max attempts reached
                from .errors import CompanionErrorType

                raise CompanionError(
                    CompanionErrorType.CONNECTION_TIMEOUT,
                    f"Max retry attempts ({policy.max_attempts}) exceeded",
                    {"last_error": str(e)},
                )

    # Should never reach here, but for type safety
    raise last_error
