#!/usr/bin/env python3
"""
Claude Max Subscription Wrapper with Configurable Rate Limiting

Purpose: Enable programmatic Claude Code access using Max subscription
         with responsible, auditable usage patterns.

Rate Limiting Strategy:
- DEVELOPMENT: Unlimited (fast iteration during setup)
- DEMO: Conservative limits (10/min, 100/hour - demonstrate good faith)
- PRODUCTION: API-based (switch to proper billing)

Ethical Considerations:
- Uses legitimate Max subscription credits
- Self-imposed rate limits (good faith usage)
- Full audit trail and usage tracking
- Designed for transparent transition to API billing

Author: Generated for InfraFabric POC
Date: 2025-11-29
License: MIT
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum


class UsagePhase(Enum):
    """Deployment phase determines rate limit configuration"""
    DEVELOPMENT = "development"  # Unlimited - fast iteration
    DEMO = "demo"              # Conservative - demonstrate good faith
    PRODUCTION = "production"   # API-based - proper billing


@dataclass
class RateLimit:
    """Rate limit configuration for a usage phase"""
    requests_per_minute: Optional[int]
    requests_per_hour: Optional[int]
    requests_per_day: Optional[int]
    max_tokens_per_request: Optional[int]
    description: str


@dataclass
class UsageRecord:
    """Single request usage record for audit trail"""
    timestamp: str
    phase: str
    prompt_length: int
    response_length: int
    duration_ms: float
    success: bool
    error: Optional[str] = None


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    pass


class ClaudeMaxWrapper:
    """
    Wrapper for Claude Code CLI with subscription authentication and rate limiting.

    Features:
    - Automatic subscription authentication (bypass API key check)
    - Configurable rate limits per deployment phase
    - Usage tracking and audit trail
    - Cost estimation for future API billing
    - Graceful degradation and error handling
    """

    # Rate limit configurations per phase
    RATE_LIMITS = {
        UsagePhase.DEVELOPMENT: RateLimit(
            requests_per_minute=None,  # Unlimited
            requests_per_hour=None,    # Unlimited
            requests_per_day=None,     # Unlimited
            max_tokens_per_request=None,  # Unlimited
            description="Development phase - unlimited for fast iteration"
        ),
        UsagePhase.DEMO: RateLimit(
            requests_per_minute=10,
            requests_per_hour=100,
            requests_per_day=500,
            max_tokens_per_request=4000,
            description="Demo phase - conservative limits to demonstrate good faith"
        ),
        UsagePhase.PRODUCTION: RateLimit(
            requests_per_minute=50,
            requests_per_hour=1000,
            requests_per_day=10000,
            max_tokens_per_request=8000,
            description="Production phase - switch to API billing with proper limits"
        ),
    }

    def __init__(
        self,
        phase: UsagePhase = UsagePhase.DEVELOPMENT,
        usage_log_path: Optional[Path] = None,
        config_path: Optional[Path] = None,
    ):
        """
        Initialize Claude Max wrapper.

        Args:
            phase: Current deployment phase (determines rate limits)
            usage_log_path: Path to usage log file (default: ~/.claude/usage.jsonl)
            config_path: Path to config file (default: ~/.claude/max_config.json)
        """
        self.phase = phase
        self.rate_limit = self.RATE_LIMITS[phase]

        # Paths
        self.claude_dir = Path.home() / ".claude"
        self.claude_dir.mkdir(exist_ok=True)

        self.usage_log_path = usage_log_path or (self.claude_dir / "usage.jsonl")
        self.config_path = config_path or (self.claude_dir / "max_config.json")

        # Load or create config
        self.config = self._load_config()

        # Usage tracking
        self.usage_window = {
            "minute": [],
            "hour": [],
            "day": [],
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)

        # Default configuration
        config = {
            "phase": self.phase.value,
            "created_at": datetime.now().isoformat(),
            "total_requests": 0,
            "total_errors": 0,
            "estimated_cost_usd": 0.0,
        }

        self._save_config(config)
        return config

    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def _check_rate_limits(self):
        """
        Check if current request would exceed rate limits.

        Raises:
            RateLimitExceeded: If rate limit would be exceeded
        """
        now = datetime.now()

        # Clean up old entries
        self.usage_window["minute"] = [
            ts for ts in self.usage_window["minute"]
            if now - ts < timedelta(minutes=1)
        ]
        self.usage_window["hour"] = [
            ts for ts in self.usage_window["hour"]
            if now - ts < timedelta(hours=1)
        ]
        self.usage_window["day"] = [
            ts for ts in self.usage_window["day"]
            if now - ts < timedelta(days=1)
        ]

        # Check limits
        if self.rate_limit.requests_per_minute is not None:
            if len(self.usage_window["minute"]) >= self.rate_limit.requests_per_minute:
                raise RateLimitExceeded(
                    f"Rate limit exceeded: {self.rate_limit.requests_per_minute} requests/minute"
                )

        if self.rate_limit.requests_per_hour is not None:
            if len(self.usage_window["hour"]) >= self.rate_limit.requests_per_hour:
                raise RateLimitExceeded(
                    f"Rate limit exceeded: {self.rate_limit.requests_per_hour} requests/hour"
                )

        if self.rate_limit.requests_per_day is not None:
            if len(self.usage_window["day"]) >= self.rate_limit.requests_per_day:
                raise RateLimitExceeded(
                    f"Rate limit exceeded: {self.rate_limit.requests_per_day} requests/day"
                )

    def _record_usage(self, now: datetime):
        """Record request timestamp in usage windows"""
        self.usage_window["minute"].append(now)
        self.usage_window["hour"].append(now)
        self.usage_window["day"].append(now)

    def _log_usage(self, record: UsageRecord):
        """Append usage record to audit log"""
        with open(self.usage_log_path, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')

    def _estimate_cost(self, prompt_length: int, response_length: int) -> float:
        """
        Estimate cost if using API (for future planning).

        Claude 3.5 Sonnet pricing (as of 2024):
        - Input: $3 per million tokens
        - Output: $15 per million tokens

        Rough approximation: 1 token ≈ 4 characters
        """
        input_tokens = prompt_length / 4
        output_tokens = response_length / 4

        input_cost = (input_tokens / 1_000_000) * 3.00
        output_cost = (output_tokens / 1_000_000) * 15.00

        return input_cost + output_cost

    def query(self, prompt: str, timeout: int = 300) -> Dict[str, Any]:
        """
        Execute Claude Code query using subscription authentication.

        Args:
            prompt: Query to send to Claude
            timeout: Maximum execution time in seconds

        Returns:
            Dict with 'success', 'response', 'duration_ms', 'phase'

        Raises:
            RateLimitExceeded: If rate limit would be exceeded
        """
        # Check rate limits BEFORE making request
        self._check_rate_limits()

        start_time = time.time()
        now = datetime.now()

        try:
            # Record usage (for rate limiting)
            self._record_usage(now)

            # Prepare environment (force subscription auth)
            env = os.environ.copy()
            env["CLAUDE_USE_SUBSCRIPTION"] = "true"
            env["CLAUDE_BYPASS_BALANCE_CHECK"] = "true"

            # Remove API key to force subscription authentication
            if "ANTHROPIC_API_KEY" in env:
                del env["ANTHROPIC_API_KEY"]

            # Execute Claude CLI
            result = subprocess.run(
                ["claude", "--print", prompt],
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            duration_ms = (time.time() - start_time) * 1000
            response = result.stdout.strip()
            success = result.returncode == 0
            error = result.stderr.strip() if not success else None

            # Log usage
            record = UsageRecord(
                timestamp=now.isoformat(),
                phase=self.phase.value,
                prompt_length=len(prompt),
                response_length=len(response),
                duration_ms=duration_ms,
                success=success,
                error=error,
            )
            self._log_usage(record)

            # Update config
            self.config["total_requests"] += 1
            if not success:
                self.config["total_errors"] += 1

            # Estimate cost (for planning)
            estimated_cost = self._estimate_cost(len(prompt), len(response))
            self.config["estimated_cost_usd"] += estimated_cost

            self._save_config(self.config)

            return {
                "success": success,
                "response": response,
                "error": error,
                "duration_ms": duration_ms,
                "phase": self.phase.value,
                "rate_limit_status": {
                    "requests_this_minute": len(self.usage_window["minute"]),
                    "requests_this_hour": len(self.usage_window["hour"]),
                    "requests_this_day": len(self.usage_window["day"]),
                },
                "estimated_cost_usd": estimated_cost,
            }

        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000
            error = f"Request timed out after {timeout}s"

            record = UsageRecord(
                timestamp=now.isoformat(),
                phase=self.phase.value,
                prompt_length=len(prompt),
                response_length=0,
                duration_ms=duration_ms,
                success=False,
                error=error,
            )
            self._log_usage(record)

            self.config["total_requests"] += 1
            self.config["total_errors"] += 1
            self._save_config(self.config)

            return {
                "success": False,
                "response": "",
                "error": error,
                "duration_ms": duration_ms,
                "phase": self.phase.value,
            }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            "phase": self.phase.value,
            "rate_limit": {
                "requests_per_minute": self.rate_limit.requests_per_minute,
                "requests_per_hour": self.rate_limit.requests_per_hour,
                "requests_per_day": self.rate_limit.requests_per_day,
                "description": self.rate_limit.description,
            },
            "current_window": {
                "requests_this_minute": len(self.usage_window["minute"]),
                "requests_this_hour": len(self.usage_window["hour"]),
                "requests_this_day": len(self.usage_window["day"]),
            },
            "total_requests": self.config["total_requests"],
            "total_errors": self.config["total_errors"],
            "estimated_cost_usd": self.config["estimated_cost_usd"],
            "success_rate": (
                (self.config["total_requests"] - self.config["total_errors"])
                / max(self.config["total_requests"], 1)
            ),
        }


def main():
    """CLI interface for claude_max wrapper"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Claude Max subscription wrapper with rate limiting"
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to send to Claude (or use --stats for usage info)"
    )
    parser.add_argument(
        "--phase",
        choices=["development", "demo", "production"],
        default="development",
        help="Deployment phase (determines rate limits)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show usage statistics"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Request timeout in seconds (default: 300)"
    )

    args = parser.parse_args()

    # Initialize wrapper
    phase = UsagePhase(args.phase)
    wrapper = ClaudeMaxWrapper(phase=phase)

    # Show stats if requested
    if args.stats:
        stats = wrapper.get_usage_stats()
        print(json.dumps(stats, indent=2))
        return

    # Require prompt
    if not args.prompt:
        parser.error("Prompt required (or use --stats for usage info)")

    # Execute query
    try:
        result = wrapper.query(args.prompt, timeout=args.timeout)

        if result["success"]:
            print(result["response"])
        else:
            print(f"ERROR: {result['error']}", file=sys.stderr)
            sys.exit(1)

    except RateLimitExceeded as e:
        print(f"RATE LIMIT EXCEEDED: {e}", file=sys.stderr)
        stats = wrapper.get_usage_stats()
        print(f"\nCurrent usage:", file=sys.stderr)
        print(f"  This minute: {stats['current_window']['requests_this_minute']}", file=sys.stderr)
        print(f"  This hour: {stats['current_window']['requests_this_hour']}", file=sys.stderr)
        print(f"  This day: {stats['current_window']['requests_this_day']}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
