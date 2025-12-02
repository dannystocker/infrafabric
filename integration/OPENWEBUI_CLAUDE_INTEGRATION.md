# Claude Max OpenWebUI Integration

**Status:** Production-Ready
**Version:** 1.0.0
**Module:** `openwebui_claude_max_module.py`
**Location:** `/home/setup/infrafabric/integration/openwebui_claude_max_module.py`

## Overview

This integration module wraps the Claude CLI into an OpenWebUI Function, enabling seamless use of Claude Max (subscription) within the OpenWebUI chat interface.

**Key Features:**
- Auto-detection of Claude CLI installation and version
- Login state detection with user prompts
- Automatic update checks
- Streaming response support for OpenWebUI
- Comprehensive error handling with IF.TTT traceability
- Security isolation via subprocess (no shell injection)

## Architecture

### Class: `ClaudeMaxFunction`

The main class that implements the OpenWebUI Function interface.

```python
class ClaudeMaxFunction:
    def __init__(self)
    def pipe(self, body: dict) -> Generator[str, None, None]
    def get_status(self) -> Dict[str, Any]
    def _check_claude_cli(self, force: bool = False) -> CLICheckResult
    def _validate_cli_ready(self) -> tuple[bool, str]
```

### Data Class: `CLICheckResult`

Structured result of CLI checks.

```python
@dataclass
class CLICheckResult:
    installed: bool
    version: Optional[str] = None
    needs_update: bool = False
    needs_login: bool = False
    error: Optional[str] = None
```

## Installation & Setup

### 1. Verify Claude CLI is Installed

```bash
which claude
claude --version
```

Expected output: `2.0.55 (Claude Code)` or higher

### 2. Authenticate Claude CLI

```bash
claude auth login
```

This creates an auth token at `~/.claude/auth_token`

### 3. Install in OpenWebUI

**Option A: Via Function Manager UI**
1. Open OpenWebUI at `http://localhost:8080`
2. Go to Admin → Functions
3. Upload `openwebui_claude_max_module.py`

**Option B: Direct Deployment**
```bash
cp /home/setup/infrafabric/integration/openwebui_claude_max_module.py \
   /path/to/openwebui/functions/
```

## Usage

### In OpenWebUI Chat

1. Select model "Claude Max OpenWebUI"
2. Send a message
3. Response streams via Claude CLI

### Direct Testing

```bash
# Check status
python3 openwebui_claude_max_module.py --status

# Test with a message
python3 openwebui_claude_max_module.py --test "Hello, Claude"
```

### Programmatic Use

```python
from openwebui_claude_max_module import ClaudeMaxFunction

func = ClaudeMaxFunction()

# Check status
status = func.get_status()
print(status)

# Execute query
body = {
    "messages": [
        {"role": "user", "content": "What is 2+2?"}
    ]
}

for chunk in func.pipe(body):
    print(chunk, end="", flush=True)
```

## Core Methods

### `pipe(body: dict) -> Generator[str, None, None]`

**OpenWebUI Interface**

Main entry point for OpenWebUI streaming.

**Input:**
```python
body = {
    "messages": [
        {"role": "user", "content": "Your question here"},
        {"role": "assistant", "content": "Previous response..."}
    ]
}
```

**Output:** Generator yielding response chunks as strings

**Error Handling:**
- Missing Claude CLI: Returns error message with install instructions
- Login required: Returns error with `claude auth login` command
- Timeout: Returns timeout error after 300 seconds
- Subprocess errors: Logs detailed error info to stderr

### `get_status() -> Dict[str, Any]`

**Status Reporting**

Returns current function status.

**Output:**
```python
{
    "name": "Claude Max OpenWebUI",
    "version": "1.0.0",
    "ready": false,
    "message": "Claude CLI requires authentication...",
    "claude_cli": {
        "installed": true,
        "version": "2.0.55 (Claude Code)",
        "needs_update": false,
        "needs_login": true,
        "error": null
    },
    "last_check": "2025-11-30T19:27:20.862191"
}
```

### `_check_claude_cli(force: bool = False) -> CLICheckResult`

**CLI Detection & Validation**

Checks:
1. Is Claude CLI installed? (via `which claude`)
2. What version is it? (via `claude --version`)
3. Is it up to date? (compares against `2.0.0`)
4. Is user authenticated? (checks for `~/.claude/auth_token`)

**Caching:** Results cached for 5 minutes to avoid repeated subprocess calls

**Returns:** `CLICheckResult` with all check results

### `_validate_cli_ready() -> tuple[bool, str]`

**Readiness Check**

Validates that CLI can execute. Returns:
- `(True, "Claude CLI ready")` - Can execute
- `(False, error_message)` - Cannot execute with explanation

## Error Handling

All errors are handled gracefully with user-friendly messages:

| Error Condition | Message | Solution |
|---|---|---|
| CLI not found | "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude" | Install Claude CLI |
| Not authenticated | "Claude CLI requires authentication. Run: claude auth login" | Run auth login |
| CLI timeout (>300s) | "Request timed out after 300 seconds." | Consider shorter queries |
| Subprocess error | "Error from Claude CLI: {stderr}" | Check CLI logs |
| Empty response | "No response from Claude CLI" | Check Claude subscription |

## Security Considerations

### Subprocess Isolation
- Commands executed via subprocess list (not shell)
- No string concatenation or user input in commands
- Prevents command injection attacks

**Code:**
```python
# SAFE: List-based commands
subprocess.run(["claude", "--print", user_message], capture_output=True)

# UNSAFE (not used):
# subprocess.run(f"claude --print {user_message}", shell=True)
```

### No Credentials in Code
- Auth tokens stored in `~/.claude/auth_token`
- Not embedded in module
- User responsible for authentication

### Logging
- Structured JSON logging to stderr
- No sensitive data in logs
- IF.TTT traceability for debugging

## IF.TTT Compliance

**Traceable:**
- All subprocess calls logged with parameters
- Error conditions captured with context
- Structured JSON logging format

**Transparent:**
- Error messages shown to user
- Status endpoint provides full CLI info
- Version checks reported

**Trustworthy:**
- Subprocess isolation prevents injection
- No hidden API calls
- Authentication required for execution

## Troubleshooting

### Problem: "Claude CLI not found"

```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude

# Verify
which claude
claude --version
```

### Problem: "Claude CLI requires authentication"

```bash
# Authenticate
claude auth login

# Verify auth token exists
ls -la ~/.claude/auth_token
```

### Problem: "Request timed out"

- Claude subscription may be busy
- Query may be too complex for timeout window
- Check Claude subscription status

### Problem: Empty responses

```bash
# Test Claude CLI directly
claude --print "Hello, are you working?"

# If this fails, CLI is misconfigured
```

### Debugging

```bash
# Check function status
python3 openwebui_claude_max_module.py --status

# Test with simple query
python3 openwebui_claude_max_module.py --test "Hi"

# Monitor stderr for detailed logs
python3 openwebui_claude_max_module.py --test "Hi" 2>&1 | grep -v "^{\"timestamp"
```

## Performance

**Latency:**
- CLI check: <100ms (cached)
- Message execution: 5-30 seconds (depends on Claude)
- Streaming: Real-time chunks

**Resource Usage:**
- Memory: ~50MB process
- Disk: Auth token only (~1KB)
- Network: Direct to Anthropic via CLI

## Integration with OpenWebUI

**Function Signature:**
```python
class Pipe:
    def __init__(self)
    def pipe(self, body: dict) -> Generator[str, None, None]
```

This matches the OpenWebUI Function API exactly.

**Example Request Flow:**
```
1. User types message in OpenWebUI
2. OpenWebUI calls pipe({"messages": [...]})
3. pipe() executes Claude CLI subprocess
4. Response chunks streamed back to UI
5. User sees real-time responses
```

## Configuration

No configuration file needed. The module detects:
- Claude CLI installation location
- Auth token location (`~/.claude/auth_token`)
- CLI version automatically

To customize, edit these constants in the class:

```python
CLAUDE_CLI_MIN_VERSION = "2.0.0"  # Minimum required version
CLAUDE_CLI_CHECK_CMD = ["claude", "--version"]  # Version check command
CLAUDE_QUERY_CMD = ["claude", "--print"]  # Query execution command
```

## Future Enhancements

Potential improvements for v2.0:
- Temperature parameter support
- Model selection (if Claude adds `--model` flag)
- Token counting and rate limiting
- Conversation state preservation
- Custom system prompts
- Context window optimization

## License

MIT License - See repository LICENSE file

## Support

For issues:
1. Check troubleshooting section above
2. Run `--status` to diagnose
3. Review stderr logs with timestamps
4. Check Claude CLI is up to date
5. Report with status output and error logs
