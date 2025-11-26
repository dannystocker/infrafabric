# Companion MCR Bridge Architecture
**Series 2 - Protocol IF.mcr.companion**
**Generated:** 2025-11-26
**Status:** ARCHITECTURAL SPECIFICATION
**Agent:** 8-10 (The Architects)

---

## Executive Summary

This document defines the **Redis-based MCR (Multi-Controller Routing) Bridge** for Bitfocus Companion integration. The bridge enables InfraFabric agents to control physical/virtual button surfaces via high-level intents, mapping semantic commands to device-specific protocols.

**Key Features:**
- Intent-based control (e.g., "studio_dark_mode" → button press)
- Multi-protocol support (HTTP/REST, OSC, TCP/UDP)
- Macro sequencing and state tracking
- Strict Redis schema validation (Pydantic enforcement)
- Async execution with comprehensive error handling

---

## 1. Redis Key Schema (Strict Enforcement)

Following InfraFabric's state validation pattern (`src/infrafabric/state/schema.py`), all Redis keys use Pydantic models for type safety.

### 1.1 Key Namespace Structure

```
mcr:bridge:companion:config                    # Bridge configuration
mcr:protocol:companion:{protocol_name}         # Protocol templates
mcr:catalog:companion:device:{device_id}       # Device registry
mcr:mapping:companion:intent:{intent_name}     # Intent mappings
mcr:companion:macro:{macro_id}                 # Macro definitions
mcr:companion:state:{device_id}:{button_id}    # Button state tracking
mcr:companion:session:{session_id}             # Active session data
```

### 1.2 Schema Definitions (Pydantic Models)

```python
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class RedisModel(BaseModel):
    """Base model for all Redis-stored entities."""

    def to_redis(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_redis(cls, data: str) -> "RedisModel":
        return cls.model_validate_json(data)


# ============================================================================
# 1. Bridge Configuration
# ============================================================================

class CompanionBridgeConfig(RedisModel):
    """Bridge configuration stored at mcr:bridge:companion:config"""

    host: str = Field(default="localhost", description="Companion host")
    port: int = Field(default=8888, description="Companion API port")
    protocol: Literal["http", "https"] = "http"
    timeout_ms: int = Field(default=5000, description="Request timeout")
    retry_attempts: int = Field(default=3, description="Retry count")
    retry_backoff_ms: int = Field(default=1000, description="Backoff between retries")
    enable_state_tracking: bool = Field(default=True, description="Track button states")
    enable_macros: bool = Field(default=True, description="Enable macro execution")

    @property
    def base_url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"


# ============================================================================
# 2. Protocol Templates
# ============================================================================

class ProtocolTemplate(RedisModel):
    """Protocol command template stored at mcr:protocol:companion:{name}"""

    protocol_name: str = Field(description="Unique protocol identifier")
    protocol_type: Literal["http", "osc", "tcp", "udp"] = "http"
    template: str = Field(description="Command template with variable placeholders")
    method: Optional[str] = Field(default="POST", description="HTTP method if protocol_type=http")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    variables: List[str] = Field(default_factory=list, description="Required variables")
    description: str = Field(default="", description="Human-readable description")

    @validator('variables')
    def validate_variables_in_template(cls, v, values):
        """Ensure all variables are referenced in template"""
        template = values.get('template', '')
        for var in v:
            if f"{{{var}}}" not in template and f"${var}" not in template:
                raise ValueError(f"Variable '{var}' not found in template")
        return v


# Example protocol templates:

# HTTP/REST Press Button
# mcr:protocol:companion:press
{
    "protocol_name": "press",
    "protocol_type": "http",
    "template": "/api/location/{page}/{row}/{col}/press",
    "method": "POST",
    "variables": ["page", "row", "col"],
    "description": "Press a button on specified page/row/col"
}

# HTTP/REST Set Button Text
# mcr:protocol:companion:set_text
{
    "protocol_name": "set_text",
    "protocol_type": "http",
    "template": "/api/location/{page}/{row}/{col}/style",
    "method": "PUT",
    "variables": ["page", "row", "col", "text"],
    "description": "Update button text label"
}

# OSC Message Template
# mcr:protocol:companion:osc_trigger
{
    "protocol_name": "osc_trigger",
    "protocol_type": "osc",
    "template": "/companion/button/{page}/{button}/press",
    "variables": ["page", "button"],
    "description": "Send OSC trigger to Companion"
}

# TCP Raw Command
# mcr:protocol:companion:tcp_raw
{
    "protocol_name": "tcp_raw",
    "protocol_type": "tcp",
    "template": "BTN {device_id} {button_id} PRESS\r\n",
    "variables": ["device_id", "button_id"],
    "description": "Raw TCP command for button press"
}


# ============================================================================
# 3. Device Catalog
# ============================================================================

class CompanionDevice(RedisModel):
    """Device entry stored at mcr:catalog:companion:device:{device_id}"""

    device_id: str = Field(description="Unique device identifier")
    device_type: str = Field(description="e.g., 'streamdeck_xl', 'virtual_surface'")
    page_count: int = Field(default=10, description="Number of pages")
    rows: int = Field(default=8, description="Buttons per row")
    cols: int = Field(default=8, description="Buttons per column")
    connection_url: Optional[str] = Field(default=None, description="Override connection")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_seen: Optional[str] = None


# Example device catalog entry:
# mcr:catalog:companion:device:studio_main
{
    "device_id": "studio_main",
    "device_type": "streamdeck_xl",
    "page_count": 10,
    "rows": 8,
    "cols": 8,
    "metadata": {
        "location": "Control Room A",
        "serial": "CL09H1A01234"
    }
}


# ============================================================================
# 4. Button Mappings (Intent -> Action)
# ============================================================================

class ButtonAction(RedisModel):
    """Single button action"""

    action_type: Literal["press", "set_text", "set_color", "custom"] = "press"
    protocol_name: str = Field(description="Protocol template to use")
    device_id: str = Field(description="Target device")
    variables: Dict[str, Any] = Field(description="Variable substitution values")
    delay_ms: int = Field(default=0, description="Delay before execution")


class IntentMapping(RedisModel):
    """Intent mapping stored at mcr:mapping:companion:intent:{intent_name}"""

    intent_name: str = Field(description="Semantic intent identifier")
    description: str = Field(description="Human-readable purpose")
    actions: List[ButtonAction] = Field(description="Sequence of actions")
    conditions: Optional[Dict[str, Any]] = Field(default=None, description="Conditional execution")
    priority: int = Field(default=0, description="Execution priority")
    created_by: str = Field(description="Agent/user that created mapping")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# Example intent mapping:
# mcr:mapping:companion:intent:studio_dark_mode
{
    "intent_name": "studio_dark_mode",
    "description": "Enable dark mode lighting in studio",
    "actions": [
        {
            "action_type": "press",
            "protocol_name": "press",
            "device_id": "studio_main",
            "variables": {"page": 1, "row": 0, "col": 0},
            "delay_ms": 0
        },
        {
            "action_type": "set_text",
            "protocol_name": "set_text",
            "device_id": "studio_main",
            "variables": {"page": 1, "row": 0, "col": 0, "text": "DARK"},
            "delay_ms": 500
        }
    ],
    "priority": 1,
    "created_by": "if.sam"
}


# ============================================================================
# 5. Macros
# ============================================================================

class MacroStep(RedisModel):
    """Single step in a macro sequence"""

    step_number: int
    intent_name: str = Field(description="Intent to execute")
    wait_for_completion: bool = Field(default=True)
    timeout_ms: int = Field(default=10000)
    on_failure: Literal["abort", "continue", "retry"] = "abort"


class CompanionMacro(RedisModel):
    """Macro stored at mcr:companion:macro:{macro_id}"""

    macro_id: str = Field(description="Unique macro identifier")
    macro_name: str = Field(description="Human-readable name")
    description: str = Field(description="Macro purpose")
    steps: List[MacroStep] = Field(description="Ordered execution steps")
    created_by: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# Example macro:
# mcr:companion:macro:morning_startup
{
    "macro_id": "morning_startup",
    "macro_name": "Morning Studio Startup",
    "description": "Initialize studio for morning broadcast",
    "steps": [
        {
            "step_number": 1,
            "intent_name": "studio_power_on",
            "wait_for_completion": true,
            "timeout_ms": 5000,
            "on_failure": "abort"
        },
        {
            "step_number": 2,
            "intent_name": "studio_lights_on",
            "wait_for_completion": true,
            "timeout_ms": 3000,
            "on_failure": "continue"
        },
        {
            "step_number": 3,
            "intent_name": "studio_camera_preset_1",
            "wait_for_completion": false,
            "timeout_ms": 2000,
            "on_failure": "continue"
        }
    ],
    "created_by": "if.sam"
}


# ============================================================================
# 6. State Tracking
# ============================================================================

class ButtonState(RedisModel):
    """Button state stored at mcr:companion:state:{device_id}:{button_id}"""

    device_id: str
    button_id: str  # Format: "{page}_{row}_{col}"
    state: Literal["idle", "pressed", "active", "disabled"] = "idle"
    text: Optional[str] = None
    color: Optional[str] = None
    last_pressed: Optional[str] = None
    press_count: int = 0
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# 7. Session Management
# ============================================================================

class CompanionSession(RedisModel):
    """Active session stored at mcr:companion:session:{session_id}"""

    session_id: str
    agent_id: str = Field(description="IF agent controlling session")
    device_ids: List[str] = Field(description="Devices in this session")
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_activity: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    commands_executed: int = 0
    errors_count: int = 0
    status: Literal["active", "paused", "terminated"] = "active"
```

---

## 2. Protocol Definition & Variable Substitution

### 2.1 Variable Substitution System

The bridge supports **template-based variable substitution** for all protocol types:

```python
class VariableSubstitution:
    """Variable substitution engine"""

    SUPPORTED_VARIABLES = {
        # Device addressing
        'device_id': 'Device identifier',
        'page': 'Page number (0-indexed)',
        'row': 'Row number (0-indexed)',
        'col': 'Column number (0-indexed)',
        'button_id': 'Computed button ID',

        # Command data
        'text': 'Button text label',
        'color': 'Button color (hex)',
        'action': 'Action type (press/release)',

        # Session context
        'session_id': 'Current session ID',
        'agent_id': 'Requesting agent ID',
        'timestamp': 'Unix timestamp',

        # Custom
        'custom_*': 'User-defined variables'
    }

    @staticmethod
    def substitute(template: str, variables: Dict[str, Any]) -> str:
        """
        Substitute variables in template.
        Supports both {var} and $var syntax.
        """
        result = template

        # Substitute {var} style
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))

        # Substitute $var style (for OSC)
        for key, value in variables.items():
            result = result.replace(f"${key}", str(value))

        # Check for unsubstituted variables
        remaining = re.findall(r'\{(\w+)\}|\$(\w+)', result)
        if remaining:
            missing = [m[0] or m[1] for m in remaining]
            raise ValueError(f"Missing variables: {missing}")

        return result
```

### 2.2 Protocol Formats

#### HTTP/REST
```python
# Template format
{
    "protocol_type": "http",
    "template": "/api/location/{page}/{row}/{col}/press",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json"
    },
    "body": {
        "action": "{action}",
        "metadata": {
            "agent": "{agent_id}"
        }
    }
}

# Execution:
# POST http://companion:8888/api/location/0/0/0/press
# Headers: {"Content-Type": "application/json"}
# Body: {"action": "press", "metadata": {"agent": "if.sam"}}
```

#### OSC (Open Sound Control)
```python
# Template format
{
    "protocol_type": "osc",
    "template": "/companion/button/{page}/{button}/press",
    "osc_port": 12345,
    "osc_type": "i"  # Integer argument
}

# Execution:
# OSC message to 127.0.0.1:12345
# Address: /companion/button/0/0/press
# Args: (1,) [integer]
```

#### TCP Raw
```python
# Template format
{
    "protocol_type": "tcp",
    "template": "BUTTON {device_id} {page} {row} {col} PRESS\r\n",
    "tcp_host": "companion",
    "tcp_port": 9999
}

# Execution:
# TCP connection to companion:9999
# Send: "BUTTON studio_main 0 0 0 PRESS\r\n"
```

#### UDP Raw
```python
# Template format
{
    "protocol_type": "udp",
    "template": "BTN|{device_id}|{page}|{row}|{col}|{action}",
    "udp_host": "companion",
    "udp_port": 9998
}

# Execution:
# UDP datagram to companion:9998
# Data: "BTN|studio_main|0|0|0|press"
```

---

## 3. Virtual Surface Logic Model

### 3.1 Intent Resolution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTENT RESOLUTION FLOW                        │
└─────────────────────────────────────────────────────────────────┘

Step 1: Agent submits intent
┌──────────────────────────────────────────────────────────────────┐
│  IF Agent (e.g., IF.sam)                                         │
│  Intent: "studio_dark_mode"                                      │
│  Context: {"scene": "broadcast", "time": "evening"}              │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
Step 2: Lookup intent mapping in Redis
┌──────────────────────────────────────────────────────────────────┐
│  Redis Key: mcr:mapping:companion:intent:studio_dark_mode        │
│  Returns: IntentMapping(                                         │
│      intent_name="studio_dark_mode",                             │
│      actions=[...]                                               │
│  )                                                               │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
Step 3: Resolve each action in sequence
┌──────────────────────────────────────────────────────────────────┐
│  Action 1: {"protocol_name": "press", "device_id": "studio_main",│
│             "variables": {"page": 1, "row": 0, "col": 0}}       │
│                                                                  │
│  → Lookup protocol: mcr:protocol:companion:press                 │
│  → Lookup device: mcr:catalog:companion:device:studio_main       │
│  → Substitute variables into template                            │
│  → Result: POST /api/location/1/0/0/press                        │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
Step 4: Execute protocol command
┌──────────────────────────────────────────────────────────────────┐
│  HTTP Client                                                     │
│  → Connect to http://companion:8888                              │
│  → POST /api/location/1/0/0/press                                │
│  → Wait for response (timeout: 5s)                               │
│  → Parse response                                                │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
Step 5: Update state & return result
┌──────────────────────────────────────────────────────────────────┐
│  Redis Update:                                                   │
│  → mcr:companion:state:studio_main:1_0_0                         │
│     {"state": "pressed", "last_pressed": "2025-11-26T10:30:00Z"}│
│                                                                  │
│  Return to Agent:                                                │
│  → Success: true                                                 │
│  → Actions executed: 1                                           │
│  → Latency: 143ms                                                │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Lookup Flow Diagram (ASCII)

```
                  ┌──────────────────┐
                  │  Agent Request   │
                  │  Intent: "X"     │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  Redis Lookup    │
                  │  Key Pattern:    │
                  │  mcr:mapping:    │
                  │  companion:      │
                  │  intent:{name}   │
                  └────────┬─────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
            Found                 Not Found
                │                     │
                ▼                     ▼
       ┌────────────────┐    ┌──────────────┐
       │ IntentMapping  │    │ Return Error │
       │ actions: [...]  │    │ 404 Intent   │
       └────────┬───────┘    │ Not Found    │
                │             └──────────────┘
                ▼
        ┌───────────────┐
        │ For each      │
        │ action:       │
        └───────┬───────┘
                │
                ▼
        ┌───────────────────────────────┐
        │ Resolve Protocol              │
        │ Redis: mcr:protocol:          │
        │ companion:{protocol_name}     │
        └────────┬──────────────────────┘
                 │
                 ▼
        ┌───────────────────────────────┐
        │ Resolve Device                │
        │ Redis: mcr:catalog:           │
        │ companion:device:{device_id}  │
        └────────┬──────────────────────┘
                 │
                 ▼
        ┌───────────────────────────────┐
        │ Substitute Variables          │
        │ template + variables → cmd    │
        └────────┬──────────────────────┘
                 │
                 ▼
        ┌───────────────────────────────┐
        │ Execute Command               │
        │ (HTTP/OSC/TCP/UDP)            │
        └────────┬──────────────────────┘
                 │
                 ▼
        ┌───────────────────────────────┐
        │ Update State                  │
        │ Redis: mcr:companion:state:*  │
        └────────┬──────────────────────┘
                 │
                 ▼
        ┌───────────────────────────────┐
        │ Return Result                 │
        │ Success/Failure + Metadata    │
        └───────────────────────────────┘
```

### 3.3 Macro Support

Macros execute **sequences of intents** with conditional logic:

```python
async def execute_macro(macro_id: str) -> MacroResult:
    """Execute a macro sequence"""

    # Load macro definition
    macro = await redis.get(f"mcr:companion:macro:{macro_id}")
    if not macro:
        raise ValueError(f"Macro not found: {macro_id}")

    results = []

    for step in macro.steps:
        try:
            # Execute intent
            result = await execute_intent(
                intent_name=step.intent_name,
                timeout_ms=step.timeout_ms
            )

            results.append(result)

            if step.wait_for_completion and not result.success:
                if step.on_failure == "abort":
                    raise MacroAbortError(f"Step {step.step_number} failed")
                elif step.on_failure == "retry":
                    result = await execute_intent(step.intent_name, timeout_ms=step.timeout_ms)
                    results.append(result)
                # "continue" falls through

        except Exception as e:
            if step.on_failure == "abort":
                raise
            # Log and continue
            logger.error(f"Macro step {step.step_number} error: {e}")

    return MacroResult(
        macro_id=macro_id,
        steps_executed=len(results),
        steps_failed=len([r for r in results if not r.success]),
        results=results
    )
```

---

## 4. Error Handling & Retry

### 4.1 Error Classification

```python
from enum import Enum

class CompanionErrorType(Enum):
    """Error type classification"""

    # Network errors (retryable)
    CONNECTION_REFUSED = "connection_refused"
    CONNECTION_TIMEOUT = "connection_timeout"
    DNS_RESOLUTION = "dns_resolution"

    # Protocol errors (non-retryable)
    INVALID_RESPONSE = "invalid_response"
    PROTOCOL_ERROR = "protocol_error"

    # Logical errors (non-retryable)
    INTENT_NOT_FOUND = "intent_not_found"
    DEVICE_NOT_FOUND = "device_not_found"
    INVALID_MAPPING = "invalid_mapping"

    # Rate limiting (retryable with backoff)
    RATE_LIMITED = "rate_limited"

    # State errors
    STATE_CORRUPTION = "state_corruption"
    VALIDATION_ERROR = "validation_error"


class CompanionError(Exception):
    """Base exception for Companion bridge errors"""

    def __init__(self, error_type: CompanionErrorType, message: str, details: Dict[str, Any] = None):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        super().__init__(message)

    @property
    def is_retryable(self) -> bool:
        """Check if error is retryable"""
        return self.error_type in {
            CompanionErrorType.CONNECTION_REFUSED,
            CompanionErrorType.CONNECTION_TIMEOUT,
            CompanionErrorType.DNS_RESOLUTION,
            CompanionErrorType.RATE_LIMITED
        }
```

### 4.2 Retry Logic

```python
import asyncio
from typing import Callable, TypeVar

T = TypeVar('T')


class RetryPolicy:
    """Exponential backoff retry policy"""

    def __init__(self,
                 max_attempts: int = 3,
                 initial_backoff_ms: int = 1000,
                 max_backoff_ms: int = 10000,
                 backoff_multiplier: float = 2.0):
        self.max_attempts = max_attempts
        self.initial_backoff_ms = initial_backoff_ms
        self.max_backoff_ms = max_backoff_ms
        self.backoff_multiplier = backoff_multiplier

    def get_delay(self, attempt: int) -> int:
        """Calculate delay for given attempt number"""
        delay = self.initial_backoff_ms * (self.backoff_multiplier ** attempt)
        return min(delay, self.max_backoff_ms)


async def retry_with_backoff(
    func: Callable[..., T],
    *args,
    policy: RetryPolicy = None,
    **kwargs
) -> T:
    """
    Execute function with exponential backoff retry.

    Only retries on CompanionError with is_retryable=True.
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
                raise CompanionError(
                    CompanionErrorType.CONNECTION_TIMEOUT,
                    f"Max retry attempts ({policy.max_attempts}) exceeded",
                    {"last_error": str(e)}
                )

    # Should never reach here, but for type safety
    raise last_error


# Example usage:
async def press_button(device_id: str, page: int, row: int, col: int):
    """Press a button with automatic retry"""

    async def _execute():
        # Actual execution logic
        response = await http_client.post(
            f"/api/location/{page}/{row}/{col}/press",
            timeout=5.0
        )
        if response.status != 200:
            raise CompanionError(
                CompanionErrorType.PROTOCOL_ERROR,
                f"Unexpected status: {response.status}"
            )
        return response

    return await retry_with_backoff(_execute, policy=RetryPolicy(max_attempts=3))
```

### 4.3 Fallback Chains

```python
class FallbackChain:
    """Execute a chain of fallback operations"""

    def __init__(self, operations: List[Callable]):
        self.operations = operations

    async def execute(self, *args, **kwargs):
        """Execute operations in order until one succeeds"""

        errors = []

        for i, operation in enumerate(self.operations):
            try:
                result = await operation(*args, **kwargs)

                if i > 0:
                    logger.warning(
                        f"Primary operation failed, succeeded with fallback #{i}"
                    )

                return result

            except Exception as e:
                errors.append(e)
                logger.error(f"Fallback #{i} failed: {e}")

        # All operations failed
        raise CompanionError(
            CompanionErrorType.CONNECTION_REFUSED,
            "All fallback operations failed",
            {"errors": [str(e) for e in errors]}
        )


# Example: Fallback from HTTP to OSC to TCP
async def press_button_with_fallbacks(device_id: str, page: int, row: int, col: int):
    """Try HTTP, fall back to OSC, then TCP"""

    chain = FallbackChain([
        lambda: press_button_http(device_id, page, row, col),
        lambda: press_button_osc(device_id, page, row, col),
        lambda: press_button_tcp(device_id, page, row, col)
    ])

    return await chain.execute()
```

### 4.4 Timeout Management

```python
import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def timeout_context(timeout_ms: int):
    """Context manager for operation timeouts"""
    try:
        async with asyncio.timeout(timeout_ms / 1000.0):
            yield
    except asyncio.TimeoutError:
        raise CompanionError(
            CompanionErrorType.CONNECTION_TIMEOUT,
            f"Operation exceeded timeout ({timeout_ms}ms)"
        )


# Example usage:
async def execute_with_timeout(intent_name: str, timeout_ms: int = 5000):
    """Execute intent with strict timeout"""

    async with timeout_context(timeout_ms):
        return await execute_intent(intent_name)
```

---

## 5. Python Class Architecture

### 5.1 Core Classes

```python
import asyncio
import aiohttp
import redis.asyncio as aioredis
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of intent/action execution"""
    success: bool
    intent_name: Optional[str] = None
    actions_executed: int = 0
    latency_ms: float = 0.0
    error: Optional[CompanionError] = None
    metadata: Dict[str, Any] = None


class CompanionVirtualSurface:
    """
    Main bridge interface for Companion MCR control.

    Responsibilities:
    - Intent resolution and execution
    - Protocol command generation
    - Device catalog management
    - State tracking
    - Error handling and retry

    Architecture Pattern:
    - Async/await for all I/O operations
    - Redis for configuration and state
    - Pydantic for schema validation
    - Exponential backoff retry
    """

    def __init__(self,
                 redis_url: str = "redis://localhost:6379",
                 config_key: str = "mcr:bridge:companion:config"):
        self.redis_url = redis_url
        self.config_key = config_key

        # Will be initialized in async_init()
        self.redis: Optional[aioredis.Redis] = None
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.config: Optional[CompanionBridgeConfig] = None

    async def async_init(self):
        """Async initialization (call after __init__)"""

        # Connect to Redis
        self.redis = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

        # Load configuration
        config_json = await self.redis.get(self.config_key)
        if not config_json:
            # Create default config
            self.config = CompanionBridgeConfig()
            await self.redis.set(self.config_key, self.config.to_redis())
        else:
            self.config = CompanionBridgeConfig.from_redis(config_json)

        # Initialize HTTP session
        timeout = aiohttp.ClientTimeout(total=self.config.timeout_ms / 1000.0)
        self.http_session = aiohttp.ClientSession(
            base_url=self.config.base_url,
            timeout=timeout
        )

        logger.info(f"CompanionVirtualSurface initialized: {self.config.base_url}")

    async def close(self):
        """Cleanup resources"""
        if self.http_session:
            await self.http_session.close()
        if self.redis:
            await self.redis.close()

    # ========================================================================
    # Intent Execution
    # ========================================================================

    async def execute_intent(self,
                           intent_name: str,
                           context: Dict[str, Any] = None,
                           timeout_ms: Optional[int] = None) -> ExecutionResult:
        """
        Execute a high-level intent.

        Args:
            intent_name: Intent identifier (e.g., "studio_dark_mode")
            context: Optional execution context
            timeout_ms: Override default timeout

        Returns:
            ExecutionResult with success status and metadata
        """
        start_time = asyncio.get_event_loop().time()
        context = context or {}

        try:
            # 1. Lookup intent mapping
            mapping = await self._get_intent_mapping(intent_name)
            if not mapping:
                raise CompanionError(
                    CompanionErrorType.INTENT_NOT_FOUND,
                    f"Intent not found: {intent_name}"
                )

            # 2. Execute all actions in sequence
            executed_count = 0

            for action in mapping.actions:
                # Apply delay if specified
                if action.delay_ms > 0:
                    await asyncio.sleep(action.delay_ms / 1000.0)

                # Execute action
                await self._execute_action(action, context)
                executed_count += 1

            # 3. Calculate latency
            end_time = asyncio.get_event_loop().time()
            latency_ms = (end_time - start_time) * 1000

            return ExecutionResult(
                success=True,
                intent_name=intent_name,
                actions_executed=executed_count,
                latency_ms=latency_ms
            )

        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            latency_ms = (end_time - start_time) * 1000

            logger.error(f"Intent execution failed: {intent_name}, error: {e}")

            return ExecutionResult(
                success=False,
                intent_name=intent_name,
                latency_ms=latency_ms,
                error=e if isinstance(e, CompanionError) else CompanionError(
                    CompanionErrorType.PROTOCOL_ERROR,
                    str(e)
                )
            )

    async def _get_intent_mapping(self, intent_name: str) -> Optional[IntentMapping]:
        """Retrieve intent mapping from Redis"""
        key = f"mcr:mapping:companion:intent:{intent_name}"
        data = await self.redis.get(key)

        if not data:
            return None

        return IntentMapping.from_redis(data)

    async def _execute_action(self,
                             action: ButtonAction,
                             context: Dict[str, Any]) -> None:
        """Execute a single button action"""

        # 1. Load protocol template
        protocol = await self._get_protocol(action.protocol_name)
        if not protocol:
            raise CompanionError(
                CompanionErrorType.PROTOCOL_ERROR,
                f"Protocol not found: {action.protocol_name}"
            )

        # 2. Load device config
        device = await self._get_device(action.device_id)
        if not device:
            raise CompanionError(
                CompanionErrorType.DEVICE_NOT_FOUND,
                f"Device not found: {action.device_id}"
            )

        # 3. Merge variables (action vars + context vars)
        variables = {**action.variables, **context}

        # 4. Substitute variables into template
        command = VariableSubstitution.substitute(protocol.template, variables)

        # 5. Execute protocol-specific command
        if protocol.protocol_type == "http":
            await self._execute_http(command, protocol, variables)
        elif protocol.protocol_type == "osc":
            await self._execute_osc(command, protocol, variables)
        elif protocol.protocol_type == "tcp":
            await self._execute_tcp(command, protocol)
        elif protocol.protocol_type == "udp":
            await self._execute_udp(command, protocol)
        else:
            raise CompanionError(
                CompanionErrorType.PROTOCOL_ERROR,
                f"Unsupported protocol type: {protocol.protocol_type}"
            )

        # 6. Update button state if tracking enabled
        if self.config.enable_state_tracking:
            await self._update_button_state(device.device_id, action, variables)

    # ========================================================================
    # Protocol Execution Methods
    # ========================================================================

    async def _execute_http(self,
                          command: str,
                          protocol: ProtocolTemplate,
                          variables: Dict[str, Any]) -> None:
        """Execute HTTP/REST command"""

        async def _do_request():
            method = protocol.method or "POST"
            headers = protocol.headers or {}

            # Build request body if variables contain 'body'
            body = None
            if 'body' in variables:
                body = variables['body']

            async with self.http_session.request(
                method,
                command,
                headers=headers,
                json=body
            ) as response:
                if response.status not in (200, 201, 204):
                    raise CompanionError(
                        CompanionErrorType.PROTOCOL_ERROR,
                        f"HTTP {response.status}: {await response.text()}"
                    )

                return await response.text()

        # Execute with retry
        policy = RetryPolicy(
            max_attempts=self.config.retry_attempts,
            initial_backoff_ms=self.config.retry_backoff_ms
        )

        await retry_with_backoff(_do_request, policy=policy)

    async def _execute_osc(self,
                         command: str,
                         protocol: ProtocolTemplate,
                         variables: Dict[str, Any]) -> None:
        """Execute OSC command"""
        # Note: Requires python-osc library
        from pythonosc import udp_client

        osc_port = protocol.osc_port or 12345
        osc_host = self.config.host

        client = udp_client.SimpleUDPClient(osc_host, osc_port)

        # Extract OSC arguments from variables
        osc_args = variables.get('osc_args', [])

        # Send OSC message
        client.send_message(command, osc_args)

        logger.debug(f"OSC sent: {command} -> {osc_host}:{osc_port}")

    async def _execute_tcp(self,
                         command: str,
                         protocol: ProtocolTemplate) -> None:
        """Execute TCP raw command"""

        tcp_host = protocol.tcp_host or self.config.host
        tcp_port = protocol.tcp_port or 9999

        reader, writer = await asyncio.open_connection(tcp_host, tcp_port)

        try:
            # Send command
            writer.write(command.encode('utf-8'))
            await writer.drain()

            # Read response (if any)
            response = await reader.read(1024)
            logger.debug(f"TCP response: {response.decode('utf-8', errors='ignore')}")

        finally:
            writer.close()
            await writer.wait_closed()

    async def _execute_udp(self,
                         command: str,
                         protocol: ProtocolTemplate) -> None:
        """Execute UDP raw command"""

        udp_host = protocol.udp_host or self.config.host
        udp_port = protocol.udp_port or 9998

        # Create UDP socket
        transport, protocol_obj = await asyncio.get_event_loop().create_datagram_endpoint(
            lambda: asyncio.DatagramProtocol(),
            remote_addr=(udp_host, udp_port)
        )

        try:
            transport.sendto(command.encode('utf-8'))
            logger.debug(f"UDP sent: {command} -> {udp_host}:{udp_port}")

        finally:
            transport.close()

    # ========================================================================
    # State Management
    # ========================================================================

    async def _update_button_state(self,
                                  device_id: str,
                                  action: ButtonAction,
                                  variables: Dict[str, Any]) -> None:
        """Update button state in Redis"""

        # Build button ID
        page = variables.get('page', 0)
        row = variables.get('row', 0)
        col = variables.get('col', 0)
        button_id = f"{page}_{row}_{col}"

        # Get existing state or create new
        state_key = f"mcr:companion:state:{device_id}:{button_id}"
        state_json = await self.redis.get(state_key)

        if state_json:
            state = ButtonState.from_redis(state_json)
        else:
            state = ButtonState(
                device_id=device_id,
                button_id=button_id
            )

        # Update state based on action type
        if action.action_type == "press":
            state.state = "pressed"
            state.last_pressed = datetime.utcnow().isoformat()
            state.press_count += 1
        elif action.action_type == "set_text":
            state.text = variables.get('text')
        elif action.action_type == "set_color":
            state.color = variables.get('color')

        state.updated_at = datetime.utcnow().isoformat()

        # Write back to Redis
        await self.redis.set(state_key, state.to_redis())

    # ========================================================================
    # Macro Execution
    # ========================================================================

    async def execute_macro(self, macro_id: str) -> ExecutionResult:
        """Execute a macro (sequence of intents)"""

        if not self.config.enable_macros:
            raise CompanionError(
                CompanionErrorType.VALIDATION_ERROR,
                "Macros are disabled in configuration"
            )

        # Load macro
        macro_key = f"mcr:companion:macro:{macro_id}"
        macro_json = await self.redis.get(macro_key)

        if not macro_json:
            raise CompanionError(
                CompanionErrorType.INTENT_NOT_FOUND,
                f"Macro not found: {macro_id}"
            )

        macro = CompanionMacro.from_redis(macro_json)

        # Execute steps
        results = []

        for step in sorted(macro.steps, key=lambda s: s.step_number):
            try:
                result = await self.execute_intent(
                    intent_name=step.intent_name,
                    timeout_ms=step.timeout_ms
                )

                results.append(result)

                if not result.success and step.on_failure == "abort":
                    break

                if step.on_failure == "retry" and not result.success:
                    # Retry once
                    result = await self.execute_intent(
                        intent_name=step.intent_name,
                        timeout_ms=step.timeout_ms
                    )
                    results.append(result)

            except Exception as e:
                logger.error(f"Macro step {step.step_number} failed: {e}")

                if step.on_failure == "abort":
                    break

        # Calculate summary
        total_executed = len(results)
        total_failed = sum(1 for r in results if not r.success)

        return ExecutionResult(
            success=(total_failed == 0),
            intent_name=f"macro:{macro_id}",
            actions_executed=total_executed,
            metadata={
                "macro_id": macro_id,
                "steps_completed": total_executed,
                "steps_failed": total_failed
            }
        )

    # ========================================================================
    # Device/Protocol Management
    # ========================================================================

    async def _get_protocol(self, protocol_name: str) -> Optional[ProtocolTemplate]:
        """Load protocol template from Redis"""
        key = f"mcr:protocol:companion:{protocol_name}"
        data = await self.redis.get(key)

        if not data:
            return None

        return ProtocolTemplate.from_redis(data)

    async def _get_device(self, device_id: str) -> Optional[CompanionDevice]:
        """Load device configuration from Redis"""
        key = f"mcr:catalog:companion:device:{device_id}"
        data = await self.redis.get(key)

        if not data:
            return None

        return CompanionDevice.from_redis(data)

    async def register_device(self, device: CompanionDevice) -> None:
        """Register a new device in the catalog"""
        key = f"mcr:catalog:companion:device:{device.device_id}"
        await self.redis.set(key, device.to_redis())
        logger.info(f"Device registered: {device.device_id}")

    async def register_intent(self, mapping: IntentMapping) -> None:
        """Register a new intent mapping"""
        key = f"mcr:mapping:companion:intent:{mapping.intent_name}"
        await self.redis.set(key, mapping.to_redis())
        logger.info(f"Intent registered: {mapping.intent_name}")

    async def register_protocol(self, protocol: ProtocolTemplate) -> None:
        """Register a new protocol template"""
        key = f"mcr:protocol:companion:{protocol.protocol_name}"
        await self.redis.set(key, protocol.to_redis())
        logger.info(f"Protocol registered: {protocol.protocol_name}")


# ============================================================================
# Context Manager for Easy Usage
# ============================================================================

class CompanionBridge:
    """Context manager wrapper for CompanionVirtualSurface"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.surface: Optional[CompanionVirtualSurface] = None

    async def __aenter__(self) -> CompanionVirtualSurface:
        self.surface = CompanionVirtualSurface(redis_url=self.redis_url)
        await self.surface.async_init()
        return self.surface

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.surface:
            await self.surface.close()
```

### 5.2 Usage Examples

```python
# Example 1: Simple intent execution
async def example_simple():
    async with CompanionBridge() as bridge:
        result = await bridge.execute_intent("studio_dark_mode")

        if result.success:
            print(f"✓ Intent executed in {result.latency_ms:.1f}ms")
        else:
            print(f"✗ Error: {result.error}")


# Example 2: Register new device and intent
async def example_register():
    async with CompanionBridge() as bridge:
        # Register device
        device = CompanionDevice(
            device_id="control_room_a",
            device_type="streamdeck_xl",
            rows=8,
            cols=8
        )
        await bridge.register_device(device)

        # Register intent
        intent = IntentMapping(
            intent_name="emergency_lights",
            description="Activate emergency lighting",
            actions=[
                ButtonAction(
                    action_type="press",
                    protocol_name="press",
                    device_id="control_room_a",
                    variables={"page": 0, "row": 7, "col": 7}
                )
            ],
            created_by="if.sam"
        )
        await bridge.register_intent(intent)


# Example 3: Execute macro
async def example_macro():
    async with CompanionBridge() as bridge:
        result = await bridge.execute_macro("morning_startup")

        print(f"Macro completed: {result.metadata['steps_completed']} steps")


# Example 4: Register custom protocol
async def example_custom_protocol():
    async with CompanionBridge() as bridge:
        protocol = ProtocolTemplate(
            protocol_name="custom_vmix_input",
            protocol_type="http",
            template="/api/vmix/input/{input_number}/activate",
            method="POST",
            variables=["input_number"],
            description="Activate vMix input via Companion"
        )
        await bridge.register_protocol(protocol)
```

---

## 6. Deployment & Integration

### 6.1 Redis Initialization Script

```python
#!/usr/bin/env python3
"""
Initialize Companion MCR Bridge in Redis
"""
import asyncio
import redis.asyncio as aioredis


async def initialize_companion_mcr():
    """Bootstrap Companion MCR bridge configuration"""

    redis = await aioredis.from_url(
        "redis://localhost:6379",
        decode_responses=True
    )

    # 1. Bridge configuration
    config = CompanionBridgeConfig(
        host="companion.local",
        port=8888,
        protocol="http",
        timeout_ms=5000,
        retry_attempts=3
    )
    await redis.set("mcr:bridge:companion:config", config.to_redis())

    # 2. Core protocols
    protocols = [
        ProtocolTemplate(
            protocol_name="press",
            protocol_type="http",
            template="/api/location/{page}/{row}/{col}/press",
            method="POST",
            variables=["page", "row", "col"]
        ),
        ProtocolTemplate(
            protocol_name="set_text",
            protocol_type="http",
            template="/api/location/{page}/{row}/{col}/style",
            method="PUT",
            variables=["page", "row", "col", "text"]
        )
    ]

    for proto in protocols:
        await redis.set(
            f"mcr:protocol:companion:{proto.protocol_name}",
            proto.to_redis()
        )

    # 3. Example device
    device = CompanionDevice(
        device_id="studio_main",
        device_type="streamdeck_xl",
        rows=8,
        cols=8
    )
    await redis.set(
        f"mcr:catalog:companion:device:{device.device_id}",
        device.to_redis()
    )

    print("✓ Companion MCR bridge initialized")

    await redis.close()


if __name__ == "__main__":
    asyncio.run(initialize_companion_mcr())
```

### 6.2 InfraFabric Agent Integration

```python
# Example: IF.sam agent using Companion bridge

class SamAgent:
    """IF.sam agent with Companion control"""

    def __init__(self):
        self.companion_bridge = None

    async def startup(self):
        """Agent initialization"""
        self.companion_bridge = CompanionVirtualSurface()
        await self.companion_bridge.async_init()

    async def handle_broadcast_request(self, scene: str):
        """
        Handle broadcast scene change request.
        Maps high-level broadcast scene to button presses.
        """

        scene_mappings = {
            "morning_show": "studio_morning_preset",
            "evening_news": "studio_evening_preset",
            "dark_mode": "studio_dark_mode"
        }

        intent_name = scene_mappings.get(scene)

        if not intent_name:
            logger.error(f"Unknown scene: {scene}")
            return False

        # Execute intent
        result = await self.companion_bridge.execute_intent(intent_name)

        return result.success
```

---

## 7. Testing & Validation

### 7.1 Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, Mock


@pytest.mark.asyncio
async def test_intent_execution():
    """Test basic intent execution"""

    bridge = CompanionVirtualSurface()

    # Mock Redis responses
    bridge._get_intent_mapping = AsyncMock(return_value=IntentMapping(
        intent_name="test_intent",
        description="Test",
        actions=[
            ButtonAction(
                action_type="press",
                protocol_name="press",
                device_id="test_device",
                variables={"page": 0, "row": 0, "col": 0}
            )
        ],
        created_by="test"
    ))

    bridge._execute_action = AsyncMock()

    result = await bridge.execute_intent("test_intent")

    assert result.success
    assert result.actions_executed == 1


@pytest.mark.asyncio
async def test_retry_logic():
    """Test exponential backoff retry"""

    attempts = []

    async def failing_func():
        attempts.append(1)
        if len(attempts) < 3:
            raise CompanionError(
                CompanionErrorType.CONNECTION_TIMEOUT,
                "Timeout"
            )
        return "success"

    policy = RetryPolicy(max_attempts=3, initial_backoff_ms=10)
    result = await retry_with_backoff(failing_func, policy=policy)

    assert result == "success"
    assert len(attempts) == 3
```

### 7.2 Integration Test

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_intent_flow():
    """Test complete intent flow against real Companion instance"""

    async with CompanionBridge() as bridge:
        # Register test device
        device = CompanionDevice(
            device_id="test_device",
            device_type="virtual",
            rows=4,
            cols=4
        )
        await bridge.register_device(device)

        # Register test intent
        intent = IntentMapping(
            intent_name="test_press",
            description="Test button press",
            actions=[
                ButtonAction(
                    action_type="press",
                    protocol_name="press",
                    device_id="test_device",
                    variables={"page": 0, "row": 0, "col": 0}
                )
            ],
            created_by="test"
        )
        await bridge.register_intent(intent)

        # Execute intent
        result = await bridge.execute_intent("test_press")

        assert result.success
        assert result.latency_ms < 1000  # Should complete within 1s
```

---

## 8. Monitoring & Observability

### 8.1 Metrics Collection

```python
from dataclasses import dataclass
from typing import Dict


@dataclass
class BridgeMetrics:
    """Operational metrics"""

    intents_executed: int = 0
    intents_failed: int = 0
    actions_executed: int = 0
    total_latency_ms: float = 0.0
    retry_count: int = 0

    @property
    def success_rate(self) -> float:
        total = self.intents_executed + self.intents_failed
        return self.intents_executed / total if total > 0 else 0.0

    @property
    def avg_latency_ms(self) -> float:
        return (self.total_latency_ms / self.intents_executed
                if self.intents_executed > 0 else 0.0)


class MetricsCollector:
    """Collect and report bridge metrics"""

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self.metrics_key = "mcr:companion:metrics"

    async def record_execution(self, result: ExecutionResult):
        """Record execution result"""

        await self.redis.hincrby(
            self.metrics_key,
            "intents_executed" if result.success else "intents_failed",
            1
        )

        await self.redis.hincrby(
            self.metrics_key,
            "actions_executed",
            result.actions_executed
        )

        await self.redis.hincrbyfloat(
            self.metrics_key,
            "total_latency_ms",
            result.latency_ms
        )

    async def get_metrics(self) -> BridgeMetrics:
        """Retrieve current metrics"""

        data = await self.redis.hgetall(self.metrics_key)

        return BridgeMetrics(
            intents_executed=int(data.get("intents_executed", 0)),
            intents_failed=int(data.get("intents_failed", 0)),
            actions_executed=int(data.get("actions_executed", 0)),
            total_latency_ms=float(data.get("total_latency_ms", 0.0)),
            retry_count=int(data.get("retry_count", 0))
        )
```

---

## 9. Security Considerations

1. **Authentication**: Companion API authentication via API keys (stored in Redis)
2. **Rate Limiting**: Prevent abuse via Redis-based rate limiter
3. **Input Validation**: Pydantic schema validation on all inputs
4. **Audit Logging**: All intent executions logged to Redis with timestamp
5. **Secret Redaction**: Sensitive data redacted from logs

---

## 10. Roadmap

### Phase 1: Foundation (Current)
- [x] Redis schema design
- [x] Protocol definitions
- [x] Python class architecture
- [ ] Core implementation

### Phase 2: Integration
- [ ] IF.sam agent integration
- [ ] vMix protocol support
- [ ] Advanced macro system

### Phase 3: Production
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Production deployment

---

**Document Status:** APPROVED
**Next Steps:** Begin implementation in `/home/user/infrafabric/src/infrafabric/integrations/companion/`
**Protocol Prefix:** `IF.mcr.companion`

---

*Generated by Agent 8-10 (The Architects) for InfraFabric Series 2*
