#!/usr/bin/env python3
"""
Rate Limiter Module for IF.emotion and other high-value endpoints

if://code/rate-limiter/2025-11-30

Features:
- Per-user hourly rate limiting (60 requests/hour)
- Per-IP rate limiting (100 requests/hour)
- Burst protection (10 requests/minute)
- Token budget tracking (50K tokens per session)
- Abuse detection and logging
- Redis-backed distributed rate limiting

Redis Key Schema:
- ratelimit:user:{user_id}:hour       → Counter (TTL: 3600s)
- ratelimit:user:{user_id}:minute     → Counter (TTL: 60s)
- ratelimit:ip:{ip_address}:hour      → Counter (TTL: 3600s)
- ratelimit:cost:{user_id}            → Token cost tracker (TTL: 86400s)
- ratelimit:violations:{identifier}   → Abuse log (set, TTL: 86400s)
"""

import redis
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Callable, Any
from functools import wraps
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Distributed rate limiter using Redis for protecting high-value endpoints.

    Implements multiple rate limiting strategies:
    1. User-level hourly limits (60 requests/hour)
    2. IP-level hourly limits (100 requests/hour)
    3. Burst protection (10 requests/minute)
    4. Token budget tracking (50K tokens per session)

    Example:
        limiter = RateLimiter(redis_host='localhost', redis_port=6379)

        # Check user limit
        allowed, retry_after = limiter.check_user_limit('user_12345')
        if not allowed:
            return {'error': f'Rate limited. Retry after {retry_after} seconds'}

        # Check burst limit
        allowed, retry_after = limiter.check_burst_limit('user_12345')
        if not allowed:
            return {'error': f'Burst limit exceeded. Retry after {retry_after} seconds'}

        # Track token usage
        if limiter.check_cost_budget('user_12345', 5000):
            # Process request
            pass
        else:
            return {'error': 'Token budget exhausted for this session'}
    """

    # Rate limit configurations
    USER_HOURLY_LIMIT = 60
    IP_HOURLY_LIMIT = 100
    BURST_LIMIT_PER_MINUTE = 10
    TOKEN_BUDGET_PER_SESSION = 50000

    # Redis TTLs (in seconds)
    HOUR_TTL = 3600
    MINUTE_TTL = 60
    SESSION_TTL = 86400  # 24 hours

    def __init__(self,
                 redis_host: str = 'localhost',
                 redis_port: int = 6379,
                 redis_db: int = 0,
                 redis_password: Optional[str] = None):
        """
        Initialize the rate limiter with Redis connection.

        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_db: Redis database number (default 0)
            redis_password: Redis authentication password (optional)

        Raises:
            redis.ConnectionError: If connection to Redis fails
        """
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            decode_responses=True
        )

        # Test connection
        try:
            self.redis.ping()
            logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def check_user_limit(self, user_id: str) -> Tuple[bool, Optional[int]]:
        """
        Check if user has exceeded hourly request limit.

        Args:
            user_id: Unique user identifier

        Returns:
            Tuple of (allowed: bool, retry_after_seconds: Optional[int])
            - allowed: True if request is within limits
            - retry_after_seconds: Seconds until user can retry (None if allowed)

        Example:
            allowed, retry_after = limiter.check_user_limit('user_12345')
            if not allowed:
                return {'error': f'Retry after {retry_after}s'}, 429
        """
        key = f"ratelimit:user:{user_id}:hour"

        # Get current count
        current = self.redis.get(key)
        count = int(current) if current else 0

        if count >= self.USER_HOURLY_LIMIT:
            # Rate limit exceeded - calculate retry time
            ttl = self.redis.ttl(key)
            retry_after = ttl if ttl > 0 else self.HOUR_TTL

            logger.warning(f"User {user_id} exceeded hourly limit ({count}/{self.USER_HOURLY_LIMIT})")
            self.log_rate_limit_violation(user_id, "user_hourly")

            return False, retry_after

        # Increment counter
        self.redis.incr(key)

        # Set TTL on first increment
        if count == 0:
            self.redis.expire(key, self.HOUR_TTL)

        logger.debug(f"User {user_id} request {count + 1}/{self.USER_HOURLY_LIMIT}")
        return True, None

    def check_ip_limit(self, ip_address: str) -> Tuple[bool, Optional[int]]:
        """
        Check if IP address has exceeded hourly request limit.

        Useful for protecting against distributed attacks and poorly behaved clients.

        Args:
            ip_address: Client IP address (IPv4 or IPv6)

        Returns:
            Tuple of (allowed: bool, retry_after_seconds: Optional[int])
            - allowed: True if request is within limits
            - retry_after_seconds: Seconds until IP can retry (None if allowed)

        Example:
            allowed, retry_after = limiter.check_ip_limit('192.168.1.100')
            if not allowed:
                # Log suspicious activity and block
                return {'error': 'IP rate limited'}, 429
        """
        key = f"ratelimit:ip:{ip_address}:hour"

        # Get current count
        current = self.redis.get(key)
        count = int(current) if current else 0

        if count >= self.IP_HOURLY_LIMIT:
            # Rate limit exceeded
            ttl = self.redis.ttl(key)
            retry_after = ttl if ttl > 0 else self.HOUR_TTL

            logger.warning(f"IP {ip_address} exceeded hourly limit ({count}/{self.IP_HOURLY_LIMIT})")
            self.log_rate_limit_violation(ip_address, "ip_hourly")

            return False, retry_after

        # Increment counter
        self.redis.incr(key)

        # Set TTL on first increment
        if count == 0:
            self.redis.expire(key, self.HOUR_TTL)

        logger.debug(f"IP {ip_address} request {count + 1}/{self.IP_HOURLY_LIMIT}")
        return True, None

    def check_burst_limit(self, user_id: str) -> Tuple[bool, Optional[int]]:
        """
        Check burst/spike protection (10 requests per minute).

        Prevents sudden spikes of requests that could indicate abuse or
        misconfigured client retries.

        Args:
            user_id: Unique user identifier

        Returns:
            Tuple of (allowed: bool, retry_after_seconds: Optional[int])
            - allowed: True if request is within burst limits
            - retry_after_seconds: Seconds until burst resets (None if allowed)

        Example:
            allowed, retry_after = limiter.check_burst_limit('user_12345')
            if not allowed:
                return {'error': 'Too many requests'}, 429
        """
        key = f"ratelimit:user:{user_id}:minute"

        # Get current count
        current = self.redis.get(key)
        count = int(current) if current else 0

        if count >= self.BURST_LIMIT_PER_MINUTE:
            # Burst limit exceeded
            ttl = self.redis.ttl(key)
            retry_after = ttl if ttl > 0 else self.MINUTE_TTL

            logger.warning(f"User {user_id} exceeded burst limit ({count}/{self.BURST_LIMIT_PER_MINUTE})")
            self.log_rate_limit_violation(user_id, "burst")

            return False, retry_after

        # Increment counter
        self.redis.incr(key)

        # Set TTL on first increment
        if count == 0:
            self.redis.expire(key, self.MINUTE_TTL)

        logger.debug(f"User {user_id} burst {count + 1}/{self.BURST_LIMIT_PER_MINUTE}")
        return True, None

    def check_cost_budget(self, user_id: str, estimated_tokens: int) -> bool:
        """
        Check if user has remaining token budget for this session.

        Tracks cumulative token usage across multiple requests in a session.
        Each user gets 50K tokens per 24-hour session.

        Args:
            user_id: Unique user identifier
            estimated_tokens: Estimated token cost for this request

        Returns:
            bool: True if budget available and has been decremented,
                  False if budget exhausted

        Example:
            if limiter.check_cost_budget('user_12345', 5000):
                # Process expensive operation
                result = process_request(...)
            else:
                return {'error': 'Token budget exhausted'}, 429
        """
        key = f"ratelimit:cost:{user_id}"

        # Get current usage
        current = self.redis.get(key)
        used_tokens = int(current) if current else 0

        remaining = self.TOKEN_BUDGET_PER_SESSION - used_tokens

        if remaining < estimated_tokens:
            logger.warning(
                f"User {user_id} insufficient budget: "
                f"need {estimated_tokens}, have {remaining}/{self.TOKEN_BUDGET_PER_SESSION}"
            )
            self.log_rate_limit_violation(user_id, "token_budget")
            return False

        # Increment cost counter
        self.redis.incrby(key, estimated_tokens)

        # Set TTL on first increment
        if used_tokens == 0:
            self.redis.expire(key, self.SESSION_TTL)

        logger.debug(
            f"User {user_id} allocated {estimated_tokens} tokens "
            f"({used_tokens + estimated_tokens}/{self.TOKEN_BUDGET_PER_SESSION})"
        )
        return True

    def get_user_budget_status(self, user_id: str) -> dict:
        """
        Get current token budget status for a user.

        Args:
            user_id: Unique user identifier

        Returns:
            dict with keys:
            - used_tokens: Tokens used this session
            - remaining_tokens: Tokens left in budget
            - total_budget: Total session budget (50K)
            - reset_at: ISO timestamp when budget resets
            - usage_percent: Percentage of budget used

        Example:
            status = limiter.get_user_budget_status('user_12345')
            if status['usage_percent'] > 90:
                logger.warning(f"User approaching budget limit: {status}")
        """
        key = f"ratelimit:cost:{user_id}"

        current = self.redis.get(key)
        used_tokens = int(current) if current else 0
        remaining = self.TOKEN_BUDGET_PER_SESSION - used_tokens

        ttl = self.redis.ttl(key)
        if ttl > 0:
            reset_at = datetime.now() + timedelta(seconds=ttl)
        else:
            reset_at = datetime.now() + timedelta(seconds=self.SESSION_TTL)

        return {
            'used_tokens': used_tokens,
            'remaining_tokens': max(0, remaining),
            'total_budget': self.TOKEN_BUDGET_PER_SESSION,
            'reset_at': reset_at.isoformat(),
            'usage_percent': round((used_tokens / self.TOKEN_BUDGET_PER_SESSION) * 100, 2)
        }

    def log_rate_limit_violation(self, identifier: str, limit_type: str) -> None:
        """
        Log rate limit violation for abuse detection and analytics.

        Violations are tracked in a set with timestamp to enable detection of
        patterns suggesting abuse, bot attacks, or misconfigured clients.

        Args:
            identifier: User ID, IP address, or other identifier
            limit_type: Type of limit violated:
                - 'user_hourly': User exceeded hourly request limit
                - 'ip_hourly': IP exceeded hourly request limit
                - 'burst': User exceeded minute-level burst limit
                - 'token_budget': User exceeded token budget

        Example:
            # Called automatically by check_*_limit methods
            limiter.log_rate_limit_violation('user_12345', 'burst')
        """
        key = f"ratelimit:violations:{identifier}"

        violation_record = json.dumps({
            'identifier': identifier,
            'limit_type': limit_type,
            'timestamp': datetime.now().isoformat()
        })

        try:
            self.redis.sadd(key, violation_record)
            self.redis.expire(key, self.SESSION_TTL)
            logger.info(f"Logged violation: {identifier} - {limit_type}")
        except Exception as e:
            logger.error(f"Failed to log violation: {e}")

    def get_violations(self, identifier: str, limit: int = 100) -> list:
        """
        Retrieve violation records for an identifier.

        Useful for abuse detection, analytics, and security audits.

        Args:
            identifier: User ID, IP address, or other identifier
            limit: Maximum number of violations to retrieve

        Returns:
            List of violation records (dict with timestamp, limit_type, etc.)

        Example:
            violations = limiter.get_violations('user_12345')
            if len(violations) > 10:
                # Potential abuse - escalate to security team
                logger.error(f"Suspicious activity: {violations}")
        """
        key = f"ratelimit:violations:{identifier}"

        try:
            violations_set = self.redis.smembers(key)
            violations = [json.loads(v) for v in violations_set]
            return sorted(violations, key=lambda x: x['timestamp'], reverse=True)[:limit]
        except Exception as e:
            logger.error(f"Failed to retrieve violations: {e}")
            return []

    def reset_user_limits(self, user_id: str) -> None:
        """
        Reset all rate limits for a user (administrative use only).

        Useful for clearing false positives or manual account resets.

        Args:
            user_id: Unique user identifier

        Example:
            # After user contacts support about false positive
            limiter.reset_user_limits('user_12345')
        """
        keys_to_delete = [
            f"ratelimit:user:{user_id}:hour",
            f"ratelimit:user:{user_id}:minute",
            f"ratelimit:cost:{user_id}"
        ]

        for key in keys_to_delete:
            self.redis.delete(key)

        logger.info(f"Reset all limits for user {user_id}")

    def reset_ip_limit(self, ip_address: str) -> None:
        """
        Reset rate limit for an IP address (administrative use only).

        Args:
            ip_address: Client IP address

        Example:
            limiter.reset_ip_limit('192.168.1.100')
        """
        key = f"ratelimit:ip:{ip_address}:hour"
        self.redis.delete(key)
        logger.info(f"Reset IP limit for {ip_address}")


# ============================================================================
# Decorator for easy endpoint protection
# ============================================================================

def rate_limit(limit_type: list = None,
               redis_host: str = 'localhost',
               redis_port: int = 6379):
    """
    Decorator for protecting endpoints with rate limiting.

    Checks specified rate limits before allowing request to proceed.
    If any limit is exceeded, returns 429 (Too Many Requests) response.

    Args:
        limit_type: List of limits to check:
            - 'user': Check per-user hourly limit (requires user_id parameter)
            - 'ip': Check per-IP hourly limit (requires ip_address parameter)
            - 'burst': Check burst limit (requires user_id parameter)
            - 'cost': Check token budget (requires user_id parameter)
        redis_host: Redis host (default 'localhost')
        redis_port: Redis port (default 6379)

    Returns:
        Decorated function that enforces rate limits

    Example:
        @rate_limit(limit_type=['user', 'burst'])
        def expensive_endpoint(user_id: str, ip_address: str, **kwargs):
            return {'result': 'success'}, 200

        # Calling the endpoint
        response, status = expensive_endpoint(
            user_id='user_12345',
            ip_address='192.168.1.100'
        )
    """
    if limit_type is None:
        limit_type = ['user', 'burst']

    limiter = RateLimiter(redis_host=redis_host, redis_port=redis_port)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            user_id = kwargs.get('user_id')
            ip_address = kwargs.get('ip_address')
            estimated_tokens = kwargs.get('estimated_tokens', 0)

            # Check user hourly limit
            if 'user' in limit_type and user_id:
                allowed, retry_after = limiter.check_user_limit(user_id)
                if not allowed:
                    return {
                        'error': 'Rate limit exceeded',
                        'limit_type': 'user_hourly',
                        'retry_after': retry_after
                    }, 429

            # Check IP hourly limit
            if 'ip' in limit_type and ip_address:
                allowed, retry_after = limiter.check_ip_limit(ip_address)
                if not allowed:
                    return {
                        'error': 'Rate limit exceeded',
                        'limit_type': 'ip_hourly',
                        'retry_after': retry_after
                    }, 429

            # Check burst limit
            if 'burst' in limit_type and user_id:
                allowed, retry_after = limiter.check_burst_limit(user_id)
                if not allowed:
                    return {
                        'error': 'Burst limit exceeded',
                        'limit_type': 'burst',
                        'retry_after': retry_after
                    }, 429

            # Check token budget
            if 'cost' in limit_type and user_id and estimated_tokens > 0:
                if not limiter.check_cost_budget(user_id, estimated_tokens):
                    return {
                        'error': 'Token budget exhausted',
                        'limit_type': 'token_budget',
                        'budget_status': limiter.get_user_budget_status(user_id)
                    }, 429

            # All checks passed, call original function
            return func(*args, **kwargs)

        return wrapper
    return decorator


if __name__ == "__main__":
    # Example usage and testing
    limiter = RateLimiter()

    # Test user limit
    print("Testing user limit...")
    for i in range(5):
        allowed, retry_after = limiter.check_user_limit('test_user')
        print(f"  Request {i+1}: allowed={allowed}, retry_after={retry_after}")

    # Test IP limit
    print("\nTesting IP limit...")
    for i in range(3):
        allowed, retry_after = limiter.check_ip_limit('192.168.1.100')
        print(f"  Request {i+1}: allowed={allowed}, retry_after={retry_after}")

    # Test burst limit
    print("\nTesting burst limit...")
    for i in range(12):
        allowed, retry_after = limiter.check_burst_limit('test_user')
        print(f"  Request {i+1}: allowed={allowed}, retry_after={retry_after}")

    # Test token budget
    print("\nTesting token budget...")
    print(f"  Check 5000 tokens: {limiter.check_cost_budget('test_user', 5000)}")
    print(f"  Check 30000 tokens: {limiter.check_cost_budget('test_user', 30000)}")
    print(f"  Check 20000 tokens: {limiter.check_cost_budget('test_user', 20000)}")

    # Get budget status
    status = limiter.get_user_budget_status('test_user')
    print(f"\nBudget status: {json.dumps(status, indent=2)}")

    # Get violations
    violations = limiter.get_violations('test_user')
    print(f"\nViolations: {len(violations)} recorded")
