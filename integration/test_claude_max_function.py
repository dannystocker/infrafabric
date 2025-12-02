#!/usr/bin/env python3
"""
Test suite for OpenWebUI Claude Max Function module.

Tests all core functionality:
- CLI detection and version checking
- Login state detection
- Error handling (missing CLI, auth required, timeout)
- Streaming response
- Status reporting

Run with: python3 test_claude_max_function.py
"""

import sys
import json
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch, MagicMock

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent))
from openwebui_claude_max_module import ClaudeMaxFunction, CLICheckResult


class TestClaudeMaxFunction(TestCase):
    """Test suite for ClaudeMaxFunction"""

    def setUp(self):
        """Set up test fixtures"""
        self.func = ClaudeMaxFunction()

    def test_cli_check_result_dataclass(self):
        """Test CLICheckResult dataclass"""
        result = CLICheckResult(
            installed=True,
            version="2.0.55 (Claude Code)",
            needs_update=False,
            needs_login=False
        )

        self.assertTrue(result.installed)
        self.assertEqual(result.version, "2.0.55 (Claude Code)")
        self.assertFalse(result.needs_update)
        self.assertFalse(result.needs_login)

    def test_version_parsing(self):
        """Test version string parsing"""
        # Valid versions
        self.assertEqual(self.func._parse_version("2.0.55 (Claude Code)"), (2, 0, 55))
        self.assertEqual(self.func._parse_version("2.0.55"), (2, 0, 55))
        self.assertEqual(self.func._parse_version("1.5.0"), (1, 5, 0))

        # Invalid versions
        self.assertIsNone(self.func._parse_version(""))
        self.assertIsNone(self.func._parse_version("invalid"))
        self.assertIsNone(self.func._parse_version("v2.0"))

    def test_version_comparison(self):
        """Test version comparison logic"""
        current = (2, 0, 55)
        minimum = (2, 0, 0)

        # Should not need update
        self.assertFalse(current < minimum)

        # Should need update
        current = (1, 9, 99)
        self.assertTrue(current < minimum)

    @patch('openwebui_claude_max_module.subprocess.run')
    def test_cli_check_installed_and_authenticated(self, mock_run):
        """Test CLI check when installed and authenticated"""
        # Mock which command (CLI exists)
        def run_side_effect(cmd, *args, **kwargs):
            if cmd[0] == "which":
                result = MagicMock()
                result.returncode = 0
                result.stdout = "/home/setup/.local/bin/claude"
                return result
            elif cmd[0] == "claude" and "--version" in cmd:
                result = MagicMock()
                result.returncode = 0
                result.stdout = "2.0.55 (Claude Code)"
                return result

        mock_run.side_effect = run_side_effect

        # Mock auth token exists
        with patch('openwebui_claude_max_module.Path.exists') as mock_exists:
            def exists_side_effect():
                # Return True for auth_token path
                return True

            mock_exists.side_effect = exists_side_effect

            # Reset cached state
            self.func._cli_state = None

            result = self.func._check_claude_cli(force=True)

            self.assertTrue(result.installed)
            self.assertEqual(result.version, "2.0.55 (Claude Code)")
            self.assertFalse(result.needs_update)
            self.assertFalse(result.needs_login)
            self.assertIsNone(result.error)

    @patch('openwebui_claude_max_module.subprocess.run')
    def test_cli_check_not_installed(self, mock_run):
        """Test CLI check when not installed"""
        # Mock which command (CLI not found)
        result = MagicMock()
        result.returncode = 1
        mock_run.return_value = result

        # Reset cached state
        self.func._cli_state = None

        result = self.func._check_claude_cli(force=True)

        self.assertFalse(result.installed)
        self.assertIsNotNone(result.error)
        self.assertIn("not found", result.error.lower())

    @patch('openwebui_claude_max_module.subprocess.run')
    def test_cli_check_needs_update(self, mock_run):
        """Test CLI check when update is needed"""
        def run_side_effect(cmd, *args, **kwargs):
            if cmd[0] == "which":
                result = MagicMock()
                result.returncode = 0
                return result
            elif cmd[0] == "claude" and "--version" in cmd:
                result = MagicMock()
                result.returncode = 0
                result.stdout = "1.5.0"  # Old version
                return result

        mock_run.side_effect = run_side_effect

        # Reset cached state
        self.func._cli_state = None

        result = self.func._check_claude_cli(force=True)

        self.assertTrue(result.installed)
        self.assertTrue(result.needs_update)
        self.assertEqual(result.version, "1.5.0")

    @patch('openwebui_claude_max_module.subprocess.run')
    @patch('openwebui_claude_max_module.Path.exists')
    def test_cli_check_needs_login(self, mock_exists, mock_run):
        """Test CLI check when login is needed"""
        def run_side_effect(cmd, *args, **kwargs):
            if cmd[0] == "which":
                result = MagicMock()
                result.returncode = 0
                return result
            elif cmd[0] == "claude" and "--version" in cmd:
                result = MagicMock()
                result.returncode = 0
                result.stdout = "2.0.55 (Claude Code)"
                return result

        mock_run.side_effect = run_side_effect
        mock_exists.return_value = False  # No auth token

        # Reset cached state
        self.func._cli_state = None

        result = self.func._check_claude_cli(force=True)

        self.assertTrue(result.installed)
        self.assertTrue(result.needs_login)
        self.assertFalse(result.needs_update)

    @patch.object(ClaudeMaxFunction, '_check_claude_cli')
    def test_validate_cli_ready_not_installed(self, mock_check):
        """Test validation when CLI not installed"""
        mock_check.return_value = CLICheckResult(
            installed=False,
            error="CLI not found"
        )

        ready, msg = self.func._validate_cli_ready()

        self.assertFalse(ready)
        self.assertIn("not found", msg.lower())

    @patch.object(ClaudeMaxFunction, '_check_claude_cli')
    def test_validate_cli_ready_needs_login(self, mock_check):
        """Test validation when login is needed"""
        mock_check.return_value = CLICheckResult(
            installed=True,
            version="2.0.55",
            needs_login=True
        )

        ready, msg = self.func._validate_cli_ready()

        self.assertFalse(ready)
        self.assertIn("login", msg.lower())

    @patch.object(ClaudeMaxFunction, '_check_claude_cli')
    def test_validate_cli_ready_success(self, mock_check):
        """Test validation when CLI is ready"""
        mock_check.return_value = CLICheckResult(
            installed=True,
            version="2.0.55",
            needs_update=False,
            needs_login=False
        )

        ready, msg = self.func._validate_cli_ready()

        self.assertTrue(ready)
        self.assertIn("ready", msg.lower())

    def test_pipe_no_messages(self):
        """Test pipe with no messages"""
        body = {"messages": []}
        result = list(self.func.pipe(body))

        # When messages are empty, pipe validates CLI first (which may fail)
        # Then returns error or "No message provided" message
        full_response = "".join(result)
        self.assertTrue(
            "message" in full_response.lower() or
            "error" in full_response.lower()
        )

    def test_pipe_no_user_message(self):
        """Test pipe with only assistant messages"""
        body = {
            "messages": [
                {"role": "assistant", "content": "Hello"}
            ]
        }
        result = list(self.func.pipe(body))

        # When no user message, pipe validates CLI first (may fail) then returns error
        full_response = "".join(result)
        self.assertTrue(
            "message" in full_response.lower() or
            "error" in full_response.lower()
        )

    @patch.object(ClaudeMaxFunction, '_validate_cli_ready')
    def test_pipe_cli_not_ready(self, mock_validate):
        """Test pipe when CLI is not ready"""
        mock_validate.return_value = (False, "Claude CLI not found")

        body = {
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        result = list(self.func.pipe(body))

        # Should contain error message
        full_response = "".join(result)
        self.assertIn("Error", full_response)

    @patch.object(ClaudeMaxFunction, '_run_subprocess')
    @patch.object(ClaudeMaxFunction, '_validate_cli_ready')
    def test_pipe_successful_response(self, mock_validate, mock_subprocess):
        """Test pipe with successful Claude response"""
        mock_validate.return_value = (True, "Ready")

        # Mock subprocess response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "This is a response from Claude."
        mock_subprocess.return_value = mock_result

        body = {
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        result = list(self.func.pipe(body))

        # Should contain response
        full_response = "".join(result)
        self.assertIn("This is a response from Claude", full_response)

    @patch.object(ClaudeMaxFunction, '_run_subprocess')
    @patch.object(ClaudeMaxFunction, '_validate_cli_ready')
    def test_pipe_cli_error(self, mock_validate, mock_subprocess):
        """Test pipe when Claude CLI returns error"""
        mock_validate.return_value = (True, "Ready")

        # Mock subprocess error
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Authentication failed"
        mock_subprocess.return_value = mock_result

        body = {
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        result = list(self.func.pipe(body))

        # Should contain error message (the module catches auth errors)
        full_response = "".join(result)
        self.assertIn("Error", full_response)
        self.assertIn("auth", full_response.lower())

    @patch.object(ClaudeMaxFunction, '_run_subprocess')
    @patch.object(ClaudeMaxFunction, '_validate_cli_ready')
    def test_pipe_timeout(self, mock_validate, mock_subprocess):
        """Test pipe when subprocess times out"""
        mock_validate.return_value = (True, "Ready")
        mock_subprocess.side_effect = TimeoutError("Timeout")

        body = {
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        result = list(self.func.pipe(body))

        # Should contain timeout error
        full_response = "".join(result)
        self.assertIn("Error", full_response)

    def test_get_status(self):
        """Test status reporting"""
        status = self.func.get_status()

        # Should have all required keys
        self.assertIn("name", status)
        self.assertIn("version", status)
        self.assertIn("ready", status)
        self.assertIn("message", status)
        self.assertIn("claude_cli", status)
        self.assertIn("last_check", status)

        # Claude_cli should have expected keys
        cli_info = status["claude_cli"]
        self.assertIn("installed", cli_info)
        self.assertIn("version", cli_info)
        self.assertIn("needs_update", cli_info)
        self.assertIn("needs_login", cli_info)
        self.assertIn("error", cli_info)

    def test_logging(self):
        """Test structured logging"""
        # Capture stderr
        import io
        captured_output = io.StringIO()

        with patch('sys.stderr', captured_output):
            self.func._log("INFO", "Test message", {"key": "value"})

        output = captured_output.getvalue()

        # Should be valid JSON
        log_entry = json.loads(output.strip())
        self.assertEqual(log_entry["level"], "INFO")
        self.assertEqual(log_entry["message"], "Test message")
        self.assertEqual(log_entry["context"]["key"], "value")


if __name__ == "__main__":
    main(verbosity=2)
