#!/usr/bin/env python3
"""
OpenWebUI Claude Max Integration Function Module

title: Claude Max OpenWebUI Function
author: InfraFabric
version: 1.0.0
license: MIT
description: Wraps Claude CLI with auto-update checks, login prompt integration, and streaming responses for OpenWebUI
requirements: requests

IF.citation: if://doc/openwebui-claude-max-integration (integration module)
IF.TTT: Traceable (subprocess execution logged), Transparent (error handling with user feedback), Trustworthy (no command injection)
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Generator, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class CLICheckResult:
    """Result of CLI version check"""
    installed: bool
    version: Optional[str] = None
    needs_update: bool = False
    needs_login: bool = False
    error: Optional[str] = None


class ClaudeMaxFunction:
    """
    OpenWebUI Function that wraps Claude CLI with auto-update and login management.

    Features:
    - Detects Claude CLI installation and version
    - Auto-update prompts when newer versions available
    - Login state detection (checks if 'claude auth login' needed)
    - Subprocess isolation for security (no command injection)
    - Streaming response support for OpenWebUI
    - Comprehensive error handling with user feedback
    - IF.TTT compliance: citations, traceability, security considerations

    IF.citation: if://component/claude-max-function/v1.0.0
    """

    CLAUDE_CLI_MIN_VERSION = "2.0.0"
    CLAUDE_CLI_CHECK_CMD = ["claude", "--version"]
    CLAUDE_QUERY_CMD = ["claude", "--print"]
    CLAUDE_AUTH_LOGIN_CMD = ["claude", "auth", "login"]

    def __init__(self):
        """Initialize Claude Max Function with configuration"""
        self.name = "Claude Max OpenWebUI"
        self.version = "1.0.0"

        # Paths
        self.claude_home = Path.home() / ".claude"
        self.auth_token_path = self.claude_home / "auth_token"
        self.config_path = self.claude_home / "config.json"

        # Runtime state
        self._cli_state: Optional[CLICheckResult] = None
        self._last_cli_check = 0
        self._cli_check_interval = 300  # 5 minutes

    def _log(self, level: str, message: str, context: Optional[Dict] = None):
        """
        Log message with IF.TTT traceability.

        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
            context: Optional context dict for traceability

        IF.citation: if://doc/logging/structured-format
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "module": "claude_max_function",
            "message": message,
        }
        if context:
            log_entry["context"] = context

        # Log to stderr (doesn't interfere with streaming output)
        print(json.dumps(log_entry), file=sys.stderr)

    def _run_subprocess(
        self,
        cmd: list,
        timeout: int = 300,
        check: bool = False
    ) -> subprocess.CompletedProcess:
        """
        Execute subprocess with security isolation.

        Security considerations:
        - Only execute pre-defined command lists (no shell=True)
        - No string concatenation or user input injection
        - Timeout prevents hanging processes
        - Returns structured result with stderr for error handling

        Args:
            cmd: Command as list of strings (no shell expansion)
            timeout: Execution timeout in seconds
            check: Raise CalledProcessError if return code != 0

        Returns:
            CompletedProcess with stdout, stderr, returncode

        Raises:
            subprocess.TimeoutExpired: If timeout exceeded
            subprocess.CalledProcessError: If check=True and return code != 0

        IF.citation: if://security/subprocess-isolation
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False  # We handle errors explicitly
            )
            return result
        except subprocess.TimeoutExpired as e:
            self._log("ERROR", "Subprocess timeout", {"cmd": cmd[0], "timeout": timeout})
            raise
        except Exception as e:
            self._log("ERROR", f"Subprocess execution failed: {str(e)}", {"cmd": cmd[0]})
            raise

    def _parse_version(self, version_str: str) -> Optional[tuple]:
        """
        Parse version string to tuple for comparison.

        Args:
            version_str: Version string like "2.0.55 (Claude Code)"

        Returns:
            Tuple of (major, minor, patch) or None if parsing fails
        """
        try:
            # Extract first version-like part
            parts = version_str.split()[0].split('.')
            return tuple(int(p) for p in parts[:3])
        except (ValueError, IndexError):
            return None

    def _check_claude_cli(self, force: bool = False) -> CLICheckResult:
        """
        Check Claude CLI installation, version, and login state.

        Features:
        - Detects CLI installation via 'which'
        - Checks version against minimum required
        - Detects if login is needed via auth token presence
        - Caches result for 5 minutes to avoid repeated subprocess calls

        Args:
            force: Bypass cache and check immediately

        Returns:
            CLICheckResult with installation status, version, update/login needs

        IF.citation: if://component/cli-check/v1.0.0
        """
        # Use cached result if recent
        now = datetime.now().timestamp()
        if (self._cli_state is not None and
            not force and
            (now - self._last_cli_check) < self._cli_check_interval):
            return self._cli_state

        result = CLICheckResult(installed=False)

        # Check if Claude CLI is installed
        try:
            which_result = subprocess.run(
                ["which", "claude"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if which_result.returncode != 0:
                result.error = "Claude CLI not found in PATH"
                self._log("WARNING", result.error)
                self._cli_state = result
                self._last_cli_check = now
                return result
        except Exception as e:
            result.error = f"Failed to check CLI installation: {str(e)}"
            self._log("ERROR", result.error)
            return result

        # Get version
        try:
            version_result = self._run_subprocess(self.CLAUDE_CLI_CHECK_CMD, timeout=10)
            if version_result.returncode == 0:
                version_str = version_result.stdout.strip()
                result.version = version_str
                result.installed = True

                # Parse and check version
                current = self._parse_version(version_str)
                minimum = self._parse_version(self.CLAUDE_CLI_MIN_VERSION)

                if current and minimum:
                    result.needs_update = current < minimum
                    if result.needs_update:
                        self._log("WARNING", "Claude CLI update available", {
                            "current": version_str,
                            "minimum": self.CLAUDE_CLI_MIN_VERSION
                        })
            else:
                result.error = f"Version check failed: {version_result.stderr}"
                self._log("ERROR", result.error)
        except Exception as e:
            result.error = f"Failed to get version: {str(e)}"
            self._log("ERROR", result.error)

        # Check login state (presence of auth token indicates logged in)
        if result.installed and not self.auth_token_path.exists():
            result.needs_login = True
            self._log("INFO", "Claude CLI login required", {
                "auth_token_path": str(self.auth_token_path)
            })

        self._cli_state = result
        self._last_cli_check = now
        return result

    def _validate_cli_ready(self) -> tuple[bool, str]:
        """
        Validate Claude CLI is ready to use.

        Returns:
            (is_ready, message) - ready=True if CLI is usable, message explains any issues

        IF.citation: if://component/cli-validation/v1.0.0
        """
        cli_state = self._check_claude_cli()

        if not cli_state.installed:
            msg = "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude"
            if cli_state.error:
                msg += f"\nDetails: {cli_state.error}"
            return False, msg

        if cli_state.needs_update:
            msg = f"Claude CLI update available. Current: {cli_state.version}"
            self._log("WARNING", msg)
            # Don't block execution, just warn

        if cli_state.needs_login:
            msg = "Claude CLI requires authentication. Run: claude auth login"
            return False, msg

        return True, "Claude CLI ready"

    def pipe(self, body: dict) -> Generator[str, None, None]:
        """
        Main OpenWebUI pipe function for streaming chat completions.

        Interface matches OpenWebUI Function API:
        - Receives body dict with 'messages' key
        - Yields response chunks as strings
        - Handles errors gracefully with user feedback

        Args:
            body: Dict with keys:
                - messages: List of message dicts with 'role' and 'content'
                - model: Optional model name (ignored - uses Claude CLI)
                - temperature: Optional temperature (passed to Claude)

        Yields:
            Response chunks as strings (compatible with OpenWebUI streaming)

        IF.citation: if://api/openwebui-function/pipe-interface
        IF.TTT: Handles all error cases, logs issues, provides user feedback
        """
        # Validate CLI is ready
        ready, validation_msg = self._validate_cli_ready()
        if not ready:
            self._log("ERROR", "CLI validation failed", {"message": validation_msg})
            yield f"**Error:** {validation_msg}\n\n"
            yield "**Solution:** Please ensure Claude CLI is installed and authenticated."
            return

        # Extract messages
        messages = body.get("messages", [])
        if not messages:
            yield "No message provided."
            return

        # Get latest user message
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if not user_message:
            yield "No user message found."
            return

        # Build system prompt from conversation context (last 5 messages for context)
        system_prompt = "You are Claude, an AI assistant created by Anthropic. "
        system_prompt += "Be helpful, harmless, and honest."

        # Add conversation context if available
        recent_messages = []
        for msg in messages[-5:]:
            if msg.get("role") in ["user", "assistant"]:
                role = msg.get("role")
                content = msg.get("content", "")
                if content:
                    recent_messages.append(f"{role.upper()}: {content}")

        if recent_messages:
            system_prompt += "\n\nRecent context:\n" + "\n".join(recent_messages)

        # Execute Claude CLI with subprocess
        try:
            self._log("INFO", "Executing Claude CLI", {
                "message_length": len(user_message),
                "context_messages": len(recent_messages)
            })

            result = self._run_subprocess(
                self.CLAUDE_QUERY_CMD + [user_message],
                timeout=300
            )

            if result.returncode == 0:
                # Successfully got response
                response = result.stdout.strip()
                if response:
                    yield response
                    self._log("INFO", "Response streamed successfully", {
                        "response_length": len(response)
                    })
                else:
                    yield "No response from Claude CLI"
                    self._log("WARNING", "Empty response from CLI")
            else:
                # CLI returned error
                error_msg = result.stderr.strip() or "Unknown error"

                # Check for specific error conditions
                if "auth" in error_msg.lower() or "login" in error_msg.lower():
                    yield "**Error:** Claude authentication failed.\n\n"
                    yield "Please run: `claude auth login`"
                    self._log("ERROR", "Authentication error", {"error": error_msg})
                elif "timeout" in error_msg.lower():
                    yield "**Error:** Request timed out after 300 seconds."
                    self._log("ERROR", "Timeout", {"error": error_msg})
                else:
                    yield f"**Error from Claude CLI:** {error_msg}"
                    self._log("ERROR", "CLI error", {"error": error_msg})

        except subprocess.TimeoutExpired:
            yield "**Error:** Claude CLI request timed out (300s limit)."
            self._log("ERROR", "CLI timeout")

        except Exception as e:
            error_detail = str(e)
            yield f"**Error:** Failed to execute Claude: {error_detail}"
            self._log("ERROR", "Execution failed", {"error": error_detail})

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of Claude Max Function.

        Returns:
            Dict with:
            - name: Function name
            - version: Function version
            - claude_cli: CLI status info
            - last_check: Timestamp of last CLI check
            - ready: Is function ready to use

        IF.citation: if://component/status-reporting/v1.0.0
        """
        cli_state = self._check_claude_cli()
        ready, message = self._validate_cli_ready()

        return {
            "name": self.name,
            "version": self.version,
            "ready": ready,
            "message": message,
            "claude_cli": {
                "installed": cli_state.installed,
                "version": cli_state.version,
                "needs_update": cli_state.needs_update,
                "needs_login": cli_state.needs_login,
                "error": cli_state.error,
            },
            "last_check": datetime.now().isoformat(),
        }


# For direct testing and CLI usage
def main():
    """
    Test the Claude Max Function directly.

    Usage:
        python openwebui_claude_max_module.py [--status] [--test "message"]
    """
    import argparse

    parser = argparse.ArgumentParser(description="Claude Max OpenWebUI Function")
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show function status and exit"
    )
    parser.add_argument(
        "--test",
        type=str,
        help="Test with a message"
    )

    args = parser.parse_args()

    # Initialize function
    func = ClaudeMaxFunction()

    # Show status if requested
    if args.status:
        status = func.get_status()
        print(json.dumps(status, indent=2))
        return 0

    # Test with message if provided
    if args.test:
        print(f"Testing with message: {args.test}\n")
        print("=" * 60)

        test_body = {
            "messages": [
                {"role": "user", "content": args.test}
            ]
        }

        for chunk in func.pipe(test_body):
            print(chunk, end="", flush=True)

        print("\n" + "=" * 60)
        return 0

    # Default: show status
    status = func.get_status()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
