# Claude Max OpenWebUI Wrapper - Technical Design Document

**Document Version:** 1.0
**Date:** 2025-11-30
**Status:** Research & Design Phase (No Implementation)
**Author:** InfraFabric / IF.guard Council

---

## Executive Summary

This document specifies the architecture for a Claude Max module that wraps the Claude CLI (v2.0.55) for OpenWebUI integration. The module maintains Claude CLI authentication, integrates with existing Sergio Personality DNA (ChromaDB), and exposes Claude Max as a selectable model in OpenWebUI.

**Key Design Principles:**
1. CLI-first approach: Leverage Claude CLI's native session management
2. Zero API key exposure: Use OAuth tokens managed by Claude CLI
3. RAG-enabled: Deep integration with existing ChromaDB personality collections
4. Graceful auth expiry: Prompt-based credential refresh when OAuth expires
5. Update-aware: Automatic CLI version checking

---

## 1. Architecture Overview

### 1.1 System Architecture (ASCII Diagram)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         OpenWebUI Frontend                          │
│                    (User selects "Claude Max")                      │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTP Request
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OpenWebUI Functions System                       │
│                   (Pipe Function Framework)                         │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ pipe() call
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ClaudeMaxPipe (This Module)                      │
│  ┌────────────────────┬──────────────────┬────────────────────┐    │
│  │ Authentication     │ ChromaDB RAG     │ CLI Subprocess     │    │
│  │ Manager            │ Integration      │ Handler            │    │
│  │                    │                  │                    │    │
│  │ - Check OAuth      │ - Query 4        │ - Spawn claude     │    │
│  │ - Refresh tokens   │   collections    │ - Stream responses │    │
│  │ - Prompt re-login  │ - Build context  │ - Handle errors    │    │
│  └─────────┬──────────┴──────┬───────────┴─────────┬──────────┘    │
│            │                 │                     │                │
└────────────┼─────────────────┼─────────────────────┼────────────────┘
             │                 │                     │
             ▼                 ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌─────────────────────┐
│ ~/.claude/       │  │ ChromaDB         │  │ Claude CLI Binary   │
│ .credentials.json│  │ /root/sergio_    │  │ (bundled or system) │
│                  │  │  chatbot/chromadb│  │                     │
│ - accessToken    │  │                  │  │ claude --print      │
│ - refreshToken   │  │ 4 Collections:   │  │   --output-format   │
│ - expiresAt      │  │ - personality    │  │   stream-json       │
│ - subscriptionType│ │ - rhetorical     │  │                     │
└──────────────────┘  │ - humor          │  └─────────────────────┘
                      │ - corpus         │
                      └──────────────────┘
```

### 1.2 Component Responsibilities

**ClaudeMaxPipe (Main Module)**
- Implements OpenWebUI Pipe Function interface
- Orchestrates authentication, RAG, and CLI execution
- Handles streaming response parsing
- Manages error states and fallback behaviors

**AuthenticationManager**
- Reads `~/.claude/.credentials.json` OAuth state
- Validates token expiration (`expiresAt` timestamp)
- Triggers re-authentication prompts when expired
- Optionally attempts `claude setup-token` automation

**ChromaDBIntegrator**
- Queries existing Sergio personality collections
- Builds contextual prompt augmentation
- Supports weighted retrieval across 4 collections:
  - `sergio_personality` (20 docs) - frameworks, values, constraints
  - `sergio_rhetorical` (5 docs) - rhetorical devices
  - `sergio_humor` (28 docs) - humor patterns
  - `sergio_corpus` (70 docs) - conversation examples

**CLISubprocessHandler**
- Spawns `claude --print --output-format stream-json`
- Handles stdin/stdout piping for streaming responses
- Parses SSE (Server-Sent Events) stream format
- Implements timeout and error recovery

---

## 2. OpenWebUI Pipe Function API Pattern

### 2.1 Required Class Structure

Based on OpenWebUI documentation ([Pipe Function Guide](https://docs.openwebui.com/features/plugin/functions/pipe/)), the Pipe Function must implement:

```python
from pydantic import BaseModel, Field
from typing import Generator, Optional, Dict, List
import requests

class Pipe:
    """Claude Max wrapper for OpenWebUI"""

    class Valves(BaseModel):
        """Configuration valves - persistent settings"""
        CLAUDE_CLI_PATH: str = Field(
            default="claude",  # Assumes claude in PATH
            description="Path to Claude CLI binary"
        )
        CHROMADB_PATH: str = Field(
            default="/root/sergio_chatbot/chromadb",
            description="Path to ChromaDB persistence directory"
        )
        ENABLE_RAG: bool = Field(
            default=True,
            description="Enable Sergio personality RAG augmentation"
        )
        AUTO_UPDATE_CLI: bool = Field(
            default=False,
            description="Automatically check for CLI updates on startup"
        )
        MIN_CLI_VERSION: str = Field(
            default="2.0.55",
            description="Minimum required Claude CLI version"
        )
        SESSION_TIMEOUT: int = Field(
            default=300,
            description="CLI subprocess timeout in seconds"
        )
        MAX_RAG_CONTEXT: int = Field(
            default=2000,
            description="Maximum RAG context tokens"
        )

    def __init__(self):
        """Initialize valves and components"""
        self.valves = self.Valves()
        self.name = "Claude Max (CLI Wrapper)"

        # Initialize components (lazy loading)
        self._auth_manager = None
        self._chromadb_client = None
        self._cli_version = None

    def pipe(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __request__: Optional[object] = None
    ) -> Generator[str, None, None]:
        """
        Main entry point - handles streaming chat completions

        Args:
            body: OpenWebUI request body with 'messages' array
            __user__: Optional user context (for access control)
            __request__: Optional FastAPI Request object

        Yields:
            Streaming response chunks (str)
        """
        # Implementation detailed in Section 3
        pass
```

### 2.2 Mandatory Methods

**`__init__(self)`**
- Initialize `self.valves` with Valves instance
- Set up component lazy-loading references

**`pipe(self, body: dict, __user__: dict, __request__: Request) -> Generator`**
- Extract messages from body
- Perform RAG retrieval if enabled
- Execute CLI subprocess
- Stream response chunks
- Handle errors gracefully

### 2.3 Optional Methods

**`pipes(self) -> List[Dict]`**
Expose multiple model variants:

```python
def pipes(self) -> List[Dict[str, str]]:
    """Expose Claude model variants"""
    return [
        {"id": "claude-max", "name": "Claude Sonnet 4.5 (Max Subscription)"},
        {"id": "claude-max-haiku", "name": "Claude Haiku 4.5 (Max Subscription)"},
        {"id": "claude-max-opus", "name": "Claude Opus 4.5 (Max Subscription)"}
    ]
```

---

## 3. Current Claude Max Backend Analysis

### 3.1 Existing Implementation

**File:** `/home/setup/if-emotion-ux/sergio_openwebui_function.py`

**Current Architecture:**
- Pipe Function class implementing OpenWebUI API
- Direct HTTP requests to `http://127.0.0.1:3001/v1/chat/completions`
- Assumes external Claude Max API server running
- Integrates ChromaDB with 4 collections
- Implements streaming via SSE parsing

**Key Code Patterns:**

```python
# RAG Retrieval Pattern
def retrieve_context(self, user_message: str) -> str:
    context_parts = []

    # Query corpus (highest priority)
    corpus_results = self._collections["corpus"].query(
        query_texts=[user_message],
        n_results=3
    )

    # Query personality frameworks
    personality_results = self._collections["personality"].query(
        query_texts=[user_message],
        n_results=2
    )

    # Build augmented context
    return "\n".join(context_parts)

# Streaming Response Pattern
response = requests.post(
    f"{self.api_base}/v1/chat/completions",
    json={"model": "claude-max", "messages": api_messages, "stream": True},
    stream=True,
    timeout=300
)

for line in response.iter_lines():
    if line.startswith('data: '):
        data = json.loads(line[6:])
        content = data['choices'][0]['delta']['content']
        yield content
```

### 3.2 Gaps in Current Implementation

**Missing Authentication Management:**
- No handling of OAuth token expiration
- No automatic re-authentication flow
- Assumes external API server manages credentials

**External Dependency:**
- Requires separate `claude_api_server.py` process (not found in system)
- Cannot operate standalone

**No CLI Update Checking:**
- Does not verify Claude CLI version
- No auto-update mechanism

---

## 4. Proposed Architecture: CLI Wrapper Approach

### 4.1 Core Components

**Component 1: AuthenticationManager**

```python
class AuthenticationManager:
    """Manages Claude CLI OAuth authentication state"""

    CREDENTIALS_PATH = Path.home() / ".claude" / ".credentials.json"

    def __init__(self):
        self.credentials = None
        self.last_check = 0
        self.check_interval = 60  # Check every 60 seconds

    def is_authenticated(self) -> bool:
        """Check if valid OAuth tokens exist"""
        if not self.CREDENTIALS_PATH.exists():
            return False

        # Rate limit credential checks
        now = time.time()
        if now - self.last_check < self.check_interval:
            return self.credentials is not None

        self.last_check = now

        try:
            with open(self.CREDENTIALS_PATH, 'r') as f:
                self.credentials = json.load(f)

            # Check expiration
            oauth = self.credentials.get("claudeAiOauth", {})
            expires_at = oauth.get("expiresAt", 0) / 1000  # Convert ms to seconds

            if time.time() > expires_at:
                return False

            # Verify subscription type
            if oauth.get("subscriptionType") != "max":
                return False

            return True

        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def get_auth_prompt(self) -> str:
        """Generate user-facing authentication prompt"""
        return """
⚠️ Claude CLI authentication required

Your Claude CLI session has expired. To continue using Claude Max:

1. Open a terminal and run: `claude setup-token`
2. Follow the authentication flow
3. Return to this chat and retry your message

Alternatively, run: `claude --help` for more options
"""

    def attempt_auto_refresh(self) -> bool:
        """
        Attempt automatic token refresh

        Note: This requires user interaction - may not be fully automatable
        Returns True if refresh succeeded, False otherwise
        """
        # Implementation would attempt:
        # subprocess.run(['claude', 'setup-token'], ...)
        # But this requires interactive terminal - may not work in OpenWebUI context
        return False
```

**Component 2: CLISubprocessHandler**

```python
import subprocess
import json
from typing import Generator

class CLISubprocessHandler:
    """Handles Claude CLI subprocess execution and streaming"""

    def __init__(self, cli_path: str = "claude", timeout: int = 300):
        self.cli_path = cli_path
        self.timeout = timeout

    def stream_query(
        self,
        messages: List[Dict[str, str]],
        model: str = "sonnet"
    ) -> Generator[str, None, None]:
        """
        Execute Claude CLI with streaming JSON output

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model alias ('sonnet', 'haiku', 'opus')

        Yields:
            Response content chunks
        """

        # Build CLI command
        cmd = [
            self.cli_path,
            "--print",  # Non-interactive mode
            "--output-format", "stream-json",  # Streaming JSON output
            "--model", model,
            "--system-prompt", messages[0]['content'] if messages[0]['role'] == 'system' else ""
        ]

        # Extract user messages
        user_messages = [m for m in messages if m['role'] == 'user']
        if not user_messages:
            yield "Error: No user message provided"
            return

        # Use last user message as prompt
        prompt = user_messages[-1]['content']

        try:
            # Spawn subprocess with stdin for prompt
            process = subprocess.Popen(
                cmd + [prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line-buffered
            )

            # Stream stdout line by line
            for line in process.stdout:
                try:
                    # Parse streaming JSON (OpenAI format)
                    data = json.loads(line.strip())

                    # Extract content delta
                    choices = data.get('choices', [])
                    if choices:
                        delta = choices[0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            yield content

                except json.JSONDecodeError:
                    # Skip malformed JSON lines
                    continue

            # Wait for process completion
            process.wait(timeout=self.timeout)

            # Check for errors
            if process.returncode != 0:
                stderr = process.stderr.read()
                yield f"\n\n[CLI Error: {stderr}]"

        except subprocess.TimeoutExpired:
            process.kill()
            yield "\n\n[Connection timed out]"

        except FileNotFoundError:
            yield f"\n\n[Error: Claude CLI not found at {self.cli_path}]"

        except Exception as e:
            yield f"\n\n[Unexpected error: {str(e)}]"
```

**Component 3: ChromaDBIntegrator** (Reuse Existing Pattern)

```python
class ChromaDBIntegrator:
    """Integrates Sergio personality DNA from ChromaDB"""

    def __init__(self, chromadb_path: str):
        self.chromadb_path = chromadb_path
        self.client = None
        self.collections = {}

        # Collection definitions
        self.collection_names = {
            "personality": "sergio_personality",
            "rhetorical": "sergio_rhetorical",
            "humor": "sergio_humor",
            "corpus": "sergio_corpus"
        }

    def initialize(self):
        """Lazy initialization of ChromaDB client"""
        if self.client is not None:
            return

        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=self.chromadb_path)

            # Load collections
            for key, name in self.collection_names.items():
                try:
                    self.collections[key] = self.client.get_collection(name)
                except Exception as e:
                    print(f"Warning: Could not load collection {name}: {e}")

        except ImportError:
            print("Warning: ChromaDB not installed - RAG disabled")
        except Exception as e:
            print(f"Warning: ChromaDB initialization failed: {e}")

    def retrieve_context(self, user_message: str, max_tokens: int = 2000) -> str:
        """
        Query ChromaDB collections for relevant context

        Retrieval strategy:
        1. Corpus (3 results) - conversation examples
        2. Personality (2 results) - frameworks
        3. Rhetorical (1 result) - devices
        4. Humor (2 results) - if keywords detected

        Returns:
            Formatted context string (truncated to max_tokens)
        """
        if not self.client:
            self.initialize()

        if not self.collections:
            return ""

        context_parts = []

        # Query corpus (highest priority)
        if "corpus" in self.collections:
            corpus_results = self.collections["corpus"].query(
                query_texts=[user_message],
                n_results=3
            )
            if corpus_results and corpus_results['documents']:
                context_parts.append("CONVERSATION EXAMPLES:")
                for doc in corpus_results['documents'][0]:
                    context_parts.append(doc[:500])

        # Query personality frameworks
        if "personality" in self.collections:
            personality_results = self.collections["personality"].query(
                query_texts=[user_message],
                n_results=2
            )
            if personality_results and personality_results['documents']:
                context_parts.append("\nPERSONALITY FRAMEWORKS:")
                for doc in personality_results['documents'][0]:
                    context_parts.append(doc[:300])

        # Query rhetorical devices
        if "rhetorical" in self.collections:
            rhetorical_results = self.collections["rhetorical"].query(
                query_texts=[user_message],
                n_results=1
            )
            if rhetorical_results and rhetorical_results['documents']:
                context_parts.append("\nRHETORICAL DEVICE:")
                context_parts.append(rhetorical_results['documents'][0][0][:200])

        # Query humor (conditional)
        humor_keywords = ['absurd', 'ridicul', 'spirit', 'vibra', 'manifest']
        if any(kw in user_message.lower() for kw in humor_keywords):
            if "humor" in self.collections:
                humor_results = self.collections["humor"].query(
                    query_texts=[user_message],
                    n_results=2
                )
                if humor_results and humor_results['documents']:
                    context_parts.append("\nHUMOR PATTERNS:")
                    for doc in humor_results['documents'][0]:
                        context_parts.append(doc[:200])

        # Join and truncate
        full_context = "\n".join(context_parts)

        # Rough token estimation (4 chars ≈ 1 token)
        if len(full_context) > max_tokens * 4:
            full_context = full_context[:max_tokens * 4] + "\n[...truncated]"

        return full_context
```

### 4.2 Integrated Pipe Implementation

```python
class ClaudeMaxPipe:
    """Complete Claude Max CLI wrapper for OpenWebUI"""

    class Valves(BaseModel):
        """Configuration valves"""
        CLAUDE_CLI_PATH: str = Field(default="claude")
        CHROMADB_PATH: str = Field(default="/root/sergio_chatbot/chromadb")
        ENABLE_RAG: bool = Field(default=True)
        SESSION_TIMEOUT: int = Field(default=300)
        MAX_RAG_CONTEXT: int = Field(default=2000)
        DEFAULT_MODEL: str = Field(default="sonnet", description="sonnet, haiku, or opus")

    def __init__(self):
        self.valves = self.Valves()
        self.name = "Claude Max (CLI)"

        # Initialize components
        self.auth_manager = AuthenticationManager()
        self.cli_handler = None  # Lazy init
        self.chromadb_integrator = None  # Lazy init

    def pipe(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __request__: Optional[object] = None
    ) -> Generator[str, None, None]:
        """Main streaming pipe function"""

        # 1. Check authentication
        if not self.auth_manager.is_authenticated():
            yield self.auth_manager.get_auth_prompt()
            return

        # 2. Extract messages
        messages = body.get("messages", [])
        if not messages:
            yield "Error: No messages provided"
            return

        # 3. Get user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if not user_message:
            yield "Error: No user message found"
            return

        # 4. RAG retrieval (if enabled)
        rag_context = ""
        if self.valves.ENABLE_RAG:
            if self.chromadb_integrator is None:
                self.chromadb_integrator = ChromaDBIntegrator(self.valves.CHROMADB_PATH)

            rag_context = self.chromadb_integrator.retrieve_context(
                user_message,
                max_tokens=self.valves.MAX_RAG_CONTEXT
            )

        # 5. Build system prompt with RAG context
        system_prompt = SERGIO_SYSTEM_PROMPT.format(
            personality_context=rag_context if rag_context else "No additional context."
        )

        # 6. Build message array for CLI
        cli_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # 7. Initialize CLI handler
        if self.cli_handler is None:
            self.cli_handler = CLISubprocessHandler(
                cli_path=self.valves.CLAUDE_CLI_PATH,
                timeout=self.valves.SESSION_TIMEOUT
            )

        # 8. Stream response
        try:
            for chunk in self.cli_handler.stream_query(
                messages=cli_messages,
                model=self.valves.DEFAULT_MODEL
            ):
                yield chunk

        except Exception as e:
            yield f"\n\n[Error in Claude CLI execution: {str(e)}]"

    def pipes(self) -> List[Dict[str, str]]:
        """Expose model variants"""
        return [
            {"id": "claude-max-sonnet", "name": "Claude Sonnet 4.5 (Max)"},
            {"id": "claude-max-haiku", "name": "Claude Haiku 4.5 (Max)"},
            {"id": "claude-max-opus", "name": "Claude Opus 4.5 (Max)"}
        ]
```

---

## 5. Authentication Flow

### 5.1 Authentication State Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Message                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ Check OAuth State     │
                │ (~/.claude/           │
                │  .credentials.json)   │
                └───────────┬───────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
    ┌─────────────┐  ┌──────────┐  ┌──────────────┐
    │ File Missing│  │ Expired  │  │ Valid Token  │
    └──────┬──────┘  └────┬─────┘  └──────┬───────┘
           │              │                │
           │              │                │
           ▼              ▼                ▼
    ┌────────────────────────────┐  ┌─────────────────┐
    │ Return Auth Prompt:        │  │ Proceed to CLI  │
    │                            │  │ Execution       │
    │ "Please run:               │  └─────────────────┘
    │  claude setup-token"       │
    │                            │
    │ "Then retry this message"  │
    └────────────────────────────┘
```

### 5.2 Credentials File Structure

**File:** `~/.claude/.credentials.json`

```json
{
  "claudeAiOauth": {
    "accessToken": "sk-ant-oat01-...",
    "refreshToken": "sk-ant-ort01-...",
    "expiresAt": 1764543482225,
    "scopes": [
      "user:inference",
      "user:profile",
      "user:sessions:claude_code"
    ],
    "subscriptionType": "max",
    "rateLimitTier": "default_claude_max_20x"
  }
}
```

**Validation Logic:**
1. Check file exists
2. Parse JSON
3. Verify `expiresAt > current_timestamp_ms`
4. Verify `subscriptionType == "max"`
5. Optionally verify scopes include `"user:inference"`

### 5.3 Re-Authentication Flow

**When OAuth Expires:**

1. **Detect Expiry:** `expiresAt` timestamp < current time
2. **Return Prompt:** Display authentication instructions to user
3. **User Action:** User runs `claude setup-token` in terminal
4. **Retry:** User sends message again in OpenWebUI
5. **Success:** New OAuth tokens written to `.credentials.json`

**Automated Refresh (Optional Future Enhancement):**
- Attempt `subprocess.run(['claude', 'setup-token'], ...)` with `--non-interactive` flag (if available)
- Pipe refresh token to stdin
- Capture new credentials from stdout
- **Challenge:** Claude CLI may require interactive browser login

---

## 6. ChromaDB Integration Approach

### 6.1 Existing ChromaDB Structure

**Path:** `/root/sergio_chatbot/chromadb`

**Collections (4 total, 123 documents):**

| Collection Name       | Document Count | Content Type                          |
|-----------------------|----------------|---------------------------------------|
| `sergio_personality`  | 20             | Frameworks, values, ethical constraints |
| `sergio_rhetorical`   | 5              | Rhetorical devices (aspiradora, etc.) |
| `sergio_humor`        | 28             | Humor patterns, absurdity detection   |
| `sergio_corpus`       | 70             | Real conversation examples            |

### 6.2 RAG Retrieval Strategy

**Query Pattern:**

```python
def retrieve_context(user_message: str) -> str:
    """
    Multi-collection retrieval with weighted priority:

    1. Corpus (n=3)       → Most important: actual conversation examples
    2. Personality (n=2)  → Frameworks and values
    3. Rhetorical (n=1)   → Specific devices
    4. Humor (n=2)        → Conditional: only if keywords detected

    Total: ~6-8 documents retrieved per query
    """
```

**Context Injection:**

```python
SERGIO_SYSTEM_PROMPT = """You are Sergio, a Spanish-speaking psychologist...

{personality_context}
"""

# Injected context format:
"""
CONVERSATION EXAMPLES:
[500 chars from corpus doc 1]
[500 chars from corpus doc 2]
[500 chars from corpus doc 3]

PERSONALITY FRAMEWORKS:
[300 chars from personality doc 1]
[300 chars from personality doc 2]

RHETORICAL DEVICE:
[200 chars from rhetorical doc 1]

HUMOR PATTERNS:
[200 chars from humor doc 1]
[200 chars from humor doc 2]

Total: ~2000 chars = ~500 tokens
```

### 6.3 OpenWebUI Native RAG vs Custom RAG

**OpenWebUI Native RAG:**
- Managed via Documents tab and `#` syntax
- Uses internal ChromaDB instance
- Collection per uploaded document
- Not suitable for pre-existing personality DNA

**Custom RAG (This Design):**
- Direct access to external ChromaDB at `/root/sergio_chatbot/chromadb`
- Pre-populated collections from Sergio transcript analysis
- Custom retrieval logic in Pipe Function
- Full control over context formatting

**Integration Points:**
- OpenWebUI Functions can access external ChromaDB via PersistentClient
- No conflict with OpenWebUI's internal RAG system
- Functions run with full Python privileges (can access filesystem)

---

## 7. CLI Update Management

### 7.1 Version Checking

**On Pipe Initialization:**

```python
def check_cli_version(self) -> str:
    """
    Check Claude CLI version on startup

    Returns version string or None if check fails
    """
    try:
        result = subprocess.run(
            [self.valves.CLAUDE_CLI_PATH, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Parse output: "2.0.55 (Claude Code)"
        version_line = result.stdout.strip()
        version = version_line.split()[0]

        return version

    except Exception as e:
        print(f"Warning: Could not check CLI version: {e}")
        return None

def validate_min_version(self, current_version: str, min_version: str) -> bool:
    """
    Compare semantic versions

    Returns True if current_version >= min_version
    """
    from packaging import version

    try:
        return version.parse(current_version) >= version.parse(min_version)
    except:
        return False  # Assume valid if parsing fails
```

### 7.2 Auto-Update Mechanism

**Valve Configuration:**

```python
AUTO_UPDATE_CLI: bool = Field(
    default=False,
    description="Automatically update Claude CLI if outdated"
)
```

**Update Flow:**

```python
def auto_update_cli(self) -> bool:
    """
    Attempt to update Claude CLI to latest version

    Executes: claude update --yes

    Returns True if update succeeded
    """
    if not self.valves.AUTO_UPDATE_CLI:
        return False

    try:
        result = subprocess.run(
            [self.valves.CLAUDE_CLI_PATH, 'update', '--yes'],
            capture_output=True,
            text=True,
            timeout=60
        )

        return result.returncode == 0

    except Exception as e:
        print(f"Auto-update failed: {e}")
        return False
```

**Version Check on Initialization:**

```python
def __init__(self):
    # ... existing init code ...

    # Check CLI version
    current_version = self.check_cli_version()

    if current_version:
        if not self.validate_min_version(current_version, self.valves.MIN_CLI_VERSION):
            print(f"Warning: Claude CLI v{current_version} < v{self.valves.MIN_CLI_VERSION}")

            if self.valves.AUTO_UPDATE_CLI:
                print("Attempting auto-update...")
                if self.auto_update_cli():
                    print("Claude CLI updated successfully")
                else:
                    print("Auto-update failed - manual update required")
```

---

## 8. Installation Steps for OpenWebUI

### 8.1 Prerequisites

**System Requirements:**
- OpenWebUI v0.5+ installed
- Claude CLI v2.0.55+ installed and authenticated
- Python 3.11+ runtime
- ChromaDB collections at `/root/sergio_chatbot/chromadb`

**Python Dependencies:**

```bash
pip install chromadb requests pydantic
```

**Claude CLI Setup:**

```bash
# Verify CLI installed
claude --version

# Authenticate (if not already)
claude setup-token

# Verify authentication
ls ~/.claude/.credentials.json
```

### 8.2 Function Installation

**Method 1: OpenWebUI Functions UI**

1. Navigate to OpenWebUI admin panel → Functions
2. Click "Create Function"
3. Paste the complete `ClaudeMaxPipe` code
4. Set function metadata:
   - Title: "Claude Max (CLI Wrapper)"
   - Author: "InfraFabric"
   - Version: "1.0.0"
   - Requirements: `chromadb, requests`
5. Click "Save"
6. Enable function globally or per-user

**Method 2: Direct File Placement**

```bash
# Copy function file to OpenWebUI functions directory
cp claude_max_cli_wrapper.py /path/to/openwebui/functions/

# Restart OpenWebUI to detect new function
docker restart open-webui  # If using Docker
```

### 8.3 Configuration (Valves)

**After Installation:**

1. Navigate to Functions → Claude Max → Settings
2. Configure Valves:
   - `CLAUDE_CLI_PATH`: Verify path (`claude` if in PATH)
   - `CHROMADB_PATH`: `/root/sergio_chatbot/chromadb`
   - `ENABLE_RAG`: `true` (for Sergio personality)
   - `SESSION_TIMEOUT`: `300` (5 minutes)
   - `MAX_RAG_CONTEXT`: `2000` (tokens)
   - `DEFAULT_MODEL`: `sonnet` (or `haiku`, `opus`)
3. Click "Save"

**Test Configuration:**

```bash
# Test ChromaDB access
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='/root/sergio_chatbot/chromadb')
for coll_name in ['sergio_personality', 'sergio_corpus']:
    coll = client.get_collection(coll_name)
    print(f'{coll_name}: {coll.count()} docs')
"
```

### 8.4 User Selection

**In OpenWebUI Chat:**

1. Click model selector dropdown
2. Select "Claude Max (CLI Wrapper)" or model variant:
   - Claude Sonnet 4.5 (Max)
   - Claude Haiku 4.5 (Max)
   - Claude Opus 4.5 (Max)
3. Send message → Function executes

---

## 9. Error Handling & Fallback Behaviors

### 9.1 Authentication Errors

**Error:** OAuth tokens expired

```python
if not self.auth_manager.is_authenticated():
    yield """
⚠️ Authentication Required

Your Claude CLI session has expired. Please:
1. Run: claude setup-token
2. Complete authentication
3. Retry this message
    """
    return
```

**Error:** No subscription / wrong subscription type

```python
if subscription_type != "max":
    yield """
⚠️ Subscription Error

This function requires Claude Max subscription.
Current subscription: {subscription_type}

Please upgrade at: https://claude.ai/settings/subscription
    """
    return
```

### 9.2 CLI Execution Errors

**Error:** CLI binary not found

```python
except FileNotFoundError:
    yield f"""
⚠️ Claude CLI Not Found

Expected path: {self.valves.CLAUDE_CLI_PATH}

Installation:
  npm install -g @anthropic-ai/claude-code

Or specify custom path in Valves configuration.
    """
```

**Error:** CLI timeout

```python
except subprocess.TimeoutExpired:
    process.kill()
    yield f"""
⚠️ Request Timeout

The Claude CLI did not respond within {self.valves.SESSION_TIMEOUT} seconds.

Possible causes:
- Large prompt size
- Network issues
- Rate limiting

Try:
1. Reduce prompt length
2. Increase SESSION_TIMEOUT valve
3. Check network connectivity
    """
```

**Error:** CLI stderr output

```python
if process.returncode != 0:
    stderr_output = process.stderr.read()
    yield f"""
⚠️ CLI Error

Exit code: {process.returncode}

Error details:
{stderr_output}

Troubleshooting:
- Run `claude --help` to verify CLI health
- Check ~/.claude/.credentials.json validity
- Review ~/.claude/history.jsonl for errors
    """
```

### 9.3 ChromaDB Errors

**Error:** ChromaDB path not found

```python
if not Path(self.valves.CHROMADB_PATH).exists():
    print(f"Warning: ChromaDB path not found: {self.valves.CHROMADB_PATH}")
    print("RAG features disabled - responses will use base model only")
    # Continue without RAG
```

**Error:** Collection missing

```python
try:
    self.collections[key] = self.client.get_collection(name)
except Exception as e:
    print(f"Warning: Collection {name} not found: {e}")
    # Skip this collection, continue with available ones
```

**Error:** ChromaDB query failure

```python
try:
    results = collection.query(query_texts=[user_message], n_results=3)
except Exception as e:
    print(f"ChromaDB query error: {e}")
    # Return empty context, fallback to base model
    return ""
```

### 9.4 Graceful Degradation

**RAG Disabled Fallback:**
- If ChromaDB unavailable, function still operates
- Responses use base Claude Max model without personality augmentation
- Warning logged to console

**Partial RAG:**
- If 1-3 collections load successfully, use available collections
- Priority: corpus > personality > rhetorical > humor

**CLI Version Mismatch:**
- If version < MIN_CLI_VERSION, display warning but attempt execution
- Some features may not work (e.g., `--output-format stream-json` added in v2.0.0)

---

## 10. Security Considerations

### 10.1 Credential Protection

**OAuth Token Storage:**
- Tokens stored in `~/.claude/.credentials.json` (user's home directory)
- File permissions: `600` (read/write owner only)
- Never expose tokens in logs or responses
- Never transmit tokens over network (CLI handles API calls)

**OpenWebUI Function Execution:**
- Functions run with backend privileges (can access filesystem)
- Only install from trusted sources (IF.guard reviewed)
- Review code before deployment

### 10.2 Subprocess Security

**Command Injection Prevention:**

```python
# SAFE: Command list (no shell interpretation)
subprocess.run([self.cli_path, '--print', user_prompt])

# UNSAFE: Shell command string
# subprocess.run(f"{self.cli_path} --print {user_prompt}", shell=True)
```

**Input Sanitization:**
- User prompts passed as CLI arguments, not shell commands
- No `shell=True` flag used
- All subprocess calls use argument lists

### 10.3 ChromaDB Access Control

**File Permissions:**
- ChromaDB path: `/root/sergio_chatbot/chromadb`
- Requires read access to ChromaDB files
- OpenWebUI backend typically runs as `root` or dedicated user
- Ensure OpenWebUI user has read permissions

**Data Privacy:**
- ChromaDB contains Sergio personality data (public transcript)
- No user PII stored in personality collections
- Conversation history not persisted in ChromaDB (OpenWebUI handles)

### 10.4 Rate Limiting

**Claude Max Tier:**
- Subscription: `default_claude_max_20x`
- Rate limits enforced by Claude API (via CLI)
- CLI returns HTTP 429 errors if rate exceeded
- OpenWebUI should display rate limit errors to user

**Mitigation:**
- Implement exponential backoff in CLI handler
- Display clear rate limit messages
- Recommend Haiku model for high-volume usage

---

## 11. Performance Optimization

### 11.1 Lazy Initialization

**Components:**
- AuthenticationManager: Check credentials only when needed (rate limited)
- ChromaDBIntegrator: Initialize client on first query
- CLISubprocessHandler: Initialize on first pipe() call

**Benefits:**
- Faster OpenWebUI startup (function registration)
- Reduced memory footprint when function unused
- Credential checks only on actual usage

### 11.2 ChromaDB Query Optimization

**Retrieval Limits:**
- Corpus: 3 documents (most important)
- Personality: 2 documents
- Rhetorical: 1 document
- Humor: 2 documents (conditional)

**Total: 6-8 documents per query (controlled)**

**Context Truncation:**
- Maximum RAG context: 2000 tokens (configurable)
- Truncate documents at 200-500 chars each
- Balance: Enough context vs. prompt size

### 11.3 CLI Subprocess Efficiency

**Reuse vs. One-Shot:**
- Current design: Spawn new `claude --print` process per message
- Alternative: Long-running `claude` session (not supported by CLI in v2.0.55)

**Streaming Benefits:**
- `--output-format stream-json` enables chunked responses
- OpenWebUI displays content as it arrives
- User sees first tokens within 1-2 seconds

### 11.4 Caching Strategies (Future)

**Potential Enhancements:**

1. **RAG Context Cache:**
   - Cache ChromaDB query results for identical messages
   - TTL: 5 minutes
   - Key: `hash(user_message)`

2. **CLI Version Cache:**
   - Check version once per OpenWebUI restart
   - Avoid subprocess overhead on every message

3. **Credential Validation Cache:**
   - Check OAuth expiry every 60 seconds (implemented)
   - Avoid file I/O on every message

---

## 12. Testing Strategy

### 12.1 Unit Tests

**Test: AuthenticationManager**

```python
def test_is_authenticated_valid():
    """Test valid OAuth token detection"""
    # Setup: Mock ~/.claude/.credentials.json with valid token
    # Assert: is_authenticated() returns True

def test_is_authenticated_expired():
    """Test expired token detection"""
    # Setup: Mock credentials with expiresAt < now
    # Assert: is_authenticated() returns False

def test_get_auth_prompt():
    """Test authentication prompt message"""
    # Assert: Prompt contains "claude setup-token"
```

**Test: CLISubprocessHandler**

```python
def test_stream_query_success():
    """Test successful CLI execution"""
    # Setup: Mock claude CLI subprocess
    # Assert: Yields expected response chunks

def test_stream_query_timeout():
    """Test timeout handling"""
    # Setup: Mock slow subprocess
    # Assert: Yields timeout error after SESSION_TIMEOUT

def test_cli_not_found():
    """Test missing CLI binary"""
    # Setup: Invalid CLAUDE_CLI_PATH
    # Assert: Yields FileNotFoundError message
```

**Test: ChromaDBIntegrator**

```python
def test_retrieve_context_success():
    """Test successful RAG retrieval"""
    # Setup: Mock ChromaDB with test collections
    # Assert: Returns formatted context string

def test_retrieve_context_empty():
    """Test query with no results"""
    # Assert: Returns empty string, no errors

def test_retrieve_context_max_tokens():
    """Test context truncation"""
    # Setup: Mock large documents
    # Assert: Context <= MAX_RAG_CONTEXT * 4 chars
```

### 12.2 Integration Tests

**Test: End-to-End Pipe Execution**

```python
def test_pipe_authenticated_user():
    """Test full pipe() execution with valid auth"""
    # Setup: Valid credentials, ChromaDB, CLI
    # Input: {"messages": [{"role": "user", "content": "Hello"}]}
    # Assert: Yields non-empty response

def test_pipe_expired_auth():
    """Test pipe() with expired OAuth tokens"""
    # Setup: Expired credentials
    # Assert: Yields authentication prompt

def test_pipe_with_rag():
    """Test pipe() with ChromaDB RAG enabled"""
    # Setup: ENABLE_RAG = True
    # Assert: System prompt includes personality context
```

### 12.3 Manual Testing Checklist

**Pre-Deployment Testing:**

- [ ] Install Claude CLI and authenticate (`claude setup-token`)
- [ ] Verify ChromaDB collections exist and load
- [ ] Test function in OpenWebUI UI (send test message)
- [ ] Verify streaming response (chunks appear incrementally)
- [ ] Test authentication expiry (modify `.credentials.json` expiresAt)
- [ ] Test model switching (sonnet, haiku, opus)
- [ ] Test RAG context injection (query ChromaDB-relevant topic)
- [ ] Test error handling (invalid CLI path, missing collection)
- [ ] Monitor OpenWebUI logs for warnings/errors
- [ ] Verify no credential exposure in responses

---

## 13. Future Enhancements

### 13.1 Multi-Turn Conversation Support

**Current Limitation:**
- CLI spawns new process per message
- No conversation state persistence in CLI

**Enhancement:**
- Use Claude Agent SDK's `ClaudeSDKClient` for session management
- Maintain conversation context across turns
- Store session IDs in OpenWebUI user metadata

**Implementation:**

```python
from claude_agent_sdk import ClaudeSDKClient

class ClaudeMaxPipe:
    def __init__(self):
        # ... existing code ...
        self.session_clients = {}  # user_id -> ClaudeSDKClient

    async def pipe(self, body: dict, __user__: dict):
        user_id = __user__.get("id")

        if user_id not in self.session_clients:
            self.session_clients[user_id] = ClaudeSDKClient()

        async for message in self.session_clients[user_id].query(prompt):
            yield message.content
```

### 13.2 Spanish Language Validation

**Integration with Spanish Filter:**
- Current implementation at `/home/setup/sergio_chatbot/sergio_spanish_filter_integration.py`
- Validates response authenticity (detects AI-generated formal Spanish)
- Triggers regeneration if score < 70/100

**Pipe Integration:**

```python
from sergio_spanish_filter_integration import SergioSpanishValidator

class ClaudeMaxPipe:
    def __init__(self):
        # ... existing code ...
        self.spanish_validator = SergioSpanishValidator(min_authenticity_score=70.0)

    def pipe(self, body: dict):
        # ... existing streaming code ...

        # Collect full response
        full_response = ""
        for chunk in self.cli_handler.stream_query(...):
            full_response += chunk
            yield chunk

        # Validate Spanish authenticity
        if self._is_spanish_response(full_response):
            validation = self.spanish_validator.validate_response(full_response)

            if not validation.is_acceptable:
                # Regenerate with filter-generated prompt
                regen_prompt = validation.get_regeneration_prompt()
                yield "\n\n[Regenerating for natural Spanish...]\n\n"

                for chunk in self.cli_handler.stream_query(regen_prompt):
                    yield chunk
```

### 13.3 Model Auto-Selection

**Context-Aware Model Routing:**

```python
def select_model(self, user_message: str) -> str:
    """
    Auto-select model based on query complexity

    Rules:
    - Haiku: Short queries (<100 chars), simple Q&A
    - Sonnet: Medium complexity, analysis
    - Opus: Complex reasoning, multi-step tasks
    """
    if len(user_message) < 100 and '?' in user_message:
        return "haiku"
    elif any(kw in user_message.lower() for kw in ['analyze', 'explain', 'compare']):
        return "sonnet"
    elif any(kw in user_message.lower() for kw in ['design', 'architec', 'plan']):
        return "opus"
    else:
        return self.valves.DEFAULT_MODEL
```

### 13.4 Token Usage Tracking

**Monitor Claude Max Consumption:**

```python
class ClaudeMaxPipe:
    def __init__(self):
        # ... existing code ...
        self.usage_stats = {
            "total_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "model_distribution": {"sonnet": 0, "haiku": 0, "opus": 0}
        }

    def pipe(self, body: dict):
        # ... existing code ...

        # Track usage (requires CLI to expose token counts)
        self.usage_stats["total_requests"] += 1
        self.usage_stats["model_distribution"][model] += 1

    def get_usage_stats(self) -> dict:
        """Return usage statistics for admin dashboard"""
        return self.usage_stats
```

### 13.5 MCP Server Integration

**Claude CLI MCP Support (v2.0+):**

```python
class ClaudeMaxPipe:
    def __init__(self):
        # ... existing code ...
        self.mcp_config_path = "/home/setup/.claude/mcp-config.json"

    def pipe(self, body: dict):
        # Add MCP server configuration to CLI command
        cmd = [
            self.cli_path,
            "--print",
            "--mcp-config", self.mcp_config_path,  # Enable MCP servers
            "--model", model,
            prompt
        ]

        # Claude CLI will handle MCP tool calls automatically
```

**MCP Use Cases:**
- File system access (already built-in)
- Web search integration
- Database queries
- Custom tool definitions

---

## 14. Comparison: CLI Wrapper vs. API Server

### 14.1 Architecture Comparison

| Aspect                | CLI Wrapper (This Design)      | API Server (Current)           |
|-----------------------|--------------------------------|--------------------------------|
| **Dependency**        | Claude CLI binary              | External API server process    |
| **Authentication**    | OAuth via `~/.claude/`         | API server manages tokens      |
| **Installation**      | Single function file           | Function + separate server     |
| **Maintenance**       | CLI auto-updates itself        | Manual server updates          |
| **Complexity**        | Low (1 component)              | Medium (2 components)          |
| **Portability**       | Works anywhere Claude CLI runs | Requires server setup          |

### 14.2 Feature Parity

| Feature               | CLI Wrapper | API Server |
|-----------------------|-------------|------------|
| Streaming responses   | ✅          | ✅         |
| ChromaDB RAG          | ✅          | ✅         |
| Model selection       | ✅          | ✅         |
| Session persistence   | ❌ (future) | ❌         |
| Token usage tracking  | ❌ (future) | ❌         |
| Spanish validation    | ❌ (future) | ❌         |
| Auto-updates          | ✅ CLI      | ❌         |
| Auth management       | ✅ CLI      | ❌ Manual  |

### 14.3 Recommendation

**Use CLI Wrapper When:**
- Single OpenWebUI instance
- Claude Max subscription available
- Prefer minimal dependencies
- Want automatic CLI updates

**Use API Server When:**
- Multiple OpenWebUI instances sharing one Claude Max account
- Need centralized rate limiting
- Require custom middleware (caching, logging)
- Want to abstract Claude CLI from OpenWebUI

**Hybrid Approach:**
- Run API server using Claude CLI subprocess (best of both worlds)
- OpenWebUI → API Server → Claude CLI
- Centralized auth management + CLI benefits

---

## 15. Appendices

### 15.1 Claude CLI Command Reference

```bash
# Authentication
claude setup-token              # Interactive OAuth login
claude --help                   # Show all commands

# Version management
claude --version                # Show current version
claude update                   # Update to latest version
claude doctor                   # Health check

# Execution modes
claude                          # Interactive session
claude --print "prompt"         # Non-interactive (print mode)
claude --continue               # Resume last session
claude --resume <session-id>    # Resume specific session

# Model selection
claude --model sonnet           # Claude Sonnet 4.5
claude --model haiku            # Claude Haiku 4.5
claude --model opus             # Claude Opus 4.5

# Output formats
claude --output-format text           # Plain text (default)
claude --output-format json           # Single JSON result
claude --output-format stream-json    # Streaming JSON (SSE)

# Streaming JSON input
cat messages.jsonl | claude --input-format stream-json --output-format stream-json

# Tool control
claude --tools "Bash,Edit,Read"       # Specify allowed tools
claude --tools ""                     # Disable all tools

# MCP servers
claude --mcp-config config.json       # Load MCP server config

# System prompts
claude --system-prompt "You are..."   # Override system prompt
claude --append-system-prompt "..."   # Append to default

# Permissions
claude --dangerously-skip-permissions # Bypass all permission checks
```

### 15.2 OpenWebUI Pipe Function API Reference

**Minimal Pipe Function:**

```python
from pydantic import BaseModel

class Pipe:
    def __init__(self):
        pass

    def pipe(self, body: dict) -> Generator[str, None, None]:
        messages = body.get("messages", [])
        user_message = messages[-1]["content"]
        yield f"Echo: {user_message}"
```

**With Valves:**

```python
class Pipe:
    class Valves(BaseModel):
        API_KEY: str = Field(default="", description="API key")

    def __init__(self):
        self.valves = self.Valves()
```

**With Multi-Model Support:**

```python
def pipes(self) -> List[Dict[str, str]]:
    return [
        {"id": "model-1", "name": "Model 1"},
        {"id": "model-2", "name": "Model 2"}
    ]
```

**With User Context:**

```python
def pipe(self, body: dict, __user__: dict, __request__: Request):
    user_id = __user__.get("id")
    yield f"Hello user {user_id}"
```

### 15.3 ChromaDB Query Examples

**Basic Query:**

```python
import chromadb

client = chromadb.PersistentClient(path="/path/to/chromadb")
collection = client.get_collection("collection_name")

results = collection.query(
    query_texts=["What is Sergio's approach to therapy?"],
    n_results=3
)

for doc in results['documents'][0]:
    print(doc)
```

**Query with Metadata Filtering:**

```python
results = collection.query(
    query_texts=["aspiradora metaphor"],
    n_results=5,
    where={"type": "rhetorical_device"}
)
```

**Check Collection Stats:**

```python
print(f"Document count: {collection.count()}")
print(f"Metadata: {collection.metadata}")
```

### 15.4 References

**OpenWebUI Documentation:**
- [Pipe Functions Guide](https://docs.openwebui.com/features/plugin/functions/pipe/)
- [Functions Overview](https://docs.openwebui.com/features/plugin/functions/)
- [RAG Integration](https://docs.openwebui.com/features/rag/)
- [Getting Started with Functions](https://docs.openwebui.com/getting-started/quick-start/starting-with-functions/)

**Claude CLI Documentation:**
- [Identity and Access Management](https://docs.claude.com/en/docs/claude-code/iam)
- [Session Management](https://docs.claude.com/en/api/agent-sdk/sessions)
- [Setup Container Authentication](https://claude-did-this.com/claude-hub/getting-started/setup-container-guide)

**Claude Agent SDK:**
- [Python SDK GitHub](https://github.com/anthropics/claude-agent-sdk-python)
- [PyPI Package](https://pypi.org/project/claude-agent-sdk/)

**ChromaDB:**
- [Chroma Documentation](https://docs.trychroma.com/)
- [Python Client Guide](https://docs.trychroma.com/getting-started)

**Related Projects:**
- [Personal RAG Pipeline Implementation](https://www.heyitworks.tech/blog/personal-rag-data-pipeline-implementation-github-to-openwebui-chroma-db/)
- [Claude Session Manager](https://github.com/Swarek/claude-session-manager)

---

## 16. Conclusion

This design document specifies a complete architecture for wrapping the Claude CLI as an OpenWebUI Pipe Function. The proposed implementation:

1. **Leverages Native Claude CLI:** Uses OAuth authentication and auto-update mechanisms
2. **Integrates Existing RAG:** Connects to pre-populated Sergio personality ChromaDB
3. **Handles Auth Expiry:** Prompts users to re-authenticate when tokens expire
4. **Streams Responses:** Provides real-time chunked output via `--output-format stream-json`
5. **Maintains Simplicity:** Single Python file with no external API server dependencies

**Next Steps (If Approved for Implementation):**
1. Create `claude_max_cli_wrapper.py` with integrated components
2. Unit test authentication, CLI execution, and RAG retrieval
3. Integration test with OpenWebUI Functions system
4. Manual QA testing with various queries
5. Deploy to production OpenWebUI instance
6. Monitor logs for errors and token expiry patterns
7. Iterate based on user feedback

**Design Status:** COMPLETE - Ready for implementation approval or further IF.guard review.

---

**Document Control:**
- **File:** `/home/setup/if-emotion-ux/CLAUDE_MAX_OPENWEBUI_WRAPPER_DESIGN.md`
- **Version:** 1.0
- **Date:** 2025-11-30
- **Author:** InfraFabric
- **Review Status:** Awaiting IF.guard approval
- **Implementation Status:** NOT IMPLEMENTED (design phase only)

---
