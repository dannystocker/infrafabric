# Companion MCR Bridge

**Protocol:** IF.mcr.companion
**Status:** Architecture Complete, Implementation Pending
**Version:** 0.1.0

---

## Overview

The Companion MCR (Multi-Controller Routing) Bridge enables InfraFabric agents to control physical and virtual button surfaces via **semantic intents**, abstracting away device-specific protocols.

**Key Features:**
- Intent-based control (e.g., `"studio_dark_mode"` → button press)
- Multi-protocol support (HTTP/REST, OSC, TCP, UDP)
- Macro sequencing (multi-step automation)
- State tracking and feedback
- Exponential backoff retry logic
- Strict Pydantic schema validation

---

## Quick Start

```python
import asyncio
from infrafabric.integrations.companion import CompanionBridge

async def main():
    # Use context manager for automatic cleanup
    async with CompanionBridge() as bridge:
        # Execute a semantic intent
        result = await bridge.execute_intent("studio_dark_mode")

        if result.success:
            print(f"✓ Executed in {result.latency_ms:.1f}ms")
        else:
            print(f"✗ Error: {result.error}")

asyncio.run(main())
```

---

## Architecture

### Data Flow

```
Agent Request ("studio_dark_mode")
    ↓
Intent Mapping (Redis: mcr:mapping:companion:intent:*)
    ↓
Action Sequence [press, set_text, ...]
    ↓
Protocol Resolution (Redis: mcr:protocol:companion:*)
    ↓
Variable Substitution {page}→1, {row}→0, {col}→0
    ↓
Command Execution (HTTP/OSC/TCP/UDP)
    ↓
State Update (Redis: mcr:companion:state:*)
    ↓
Return ExecutionResult
```

### Redis Schema

```
mcr:bridge:companion:config                    # Bridge configuration
mcr:protocol:companion:{protocol_name}         # Protocol templates
mcr:catalog:companion:device:{device_id}       # Device registry
mcr:mapping:companion:intent:{intent_name}     # Intent mappings
mcr:companion:macro:{macro_id}                 # Macro definitions
mcr:companion:state:{device_id}:{button_id}    # Button state tracking
```

---

## Examples

### 1. Register a Device

```python
from infrafabric.integrations.companion import CompanionDevice

async with CompanionBridge() as bridge:
    device = CompanionDevice(
        device_id="studio_main",
        device_type="streamdeck_xl",
        rows=8,
        cols=8,
        metadata={
            "location": "Control Room A",
            "serial": "CL09H1A01234"
        }
    )
    await bridge.register_device(device)
```

### 2. Register an Intent

```python
from infrafabric.integrations.companion import IntentMapping, ButtonAction

async with CompanionBridge() as bridge:
    intent = IntentMapping(
        intent_name="studio_dark_mode",
        description="Enable dark mode studio lighting",
        actions=[
            ButtonAction(
                action_type="press",
                protocol_name="press",
                device_id="studio_main",
                variables={"page": 1, "row": 0, "col": 0}
            ),
            ButtonAction(
                action_type="set_text",
                protocol_name="set_text",
                device_id="studio_main",
                variables={"page": 1, "row": 0, "col": 0, "text": "DARK"},
                delay_ms=500  # Wait 500ms after press
            )
        ],
        created_by="if.sam"
    )
    await bridge.register_intent(intent)
```

### 3. Execute a Macro

```python
# Macro must be registered in Redis first
async with CompanionBridge() as bridge:
    result = await bridge.execute_macro("morning_startup")

    print(f"Macro steps: {result.metadata['steps_completed']}")
    print(f"Failed steps: {result.metadata['steps_failed']}")
```

### 4. Custom Protocol

```python
from infrafabric.integrations.companion import ProtocolTemplate

async with CompanionBridge() as bridge:
    protocol = ProtocolTemplate(
        protocol_name="vmix_input",
        protocol_type="http",
        template="/api/vmix/input/{input_number}/activate",
        method="POST",
        variables=["input_number"],
        description="Activate vMix input via Companion"
    )
    await bridge.register_protocol(protocol)
```

---

## Configuration

Bridge configuration is stored in Redis at `mcr:bridge:companion:config`:

```json
{
  "host": "companion.local",
  "port": 8888,
  "protocol": "http",
  "timeout_ms": 5000,
  "retry_attempts": 3,
  "retry_backoff_ms": 1000,
  "enable_state_tracking": true,
  "enable_macros": true
}
```

---

## Error Handling

All errors are classified as **retryable** or **non-retryable**:

### Retryable Errors (with exponential backoff)
- `CONNECTION_REFUSED`
- `CONNECTION_TIMEOUT`
- `DNS_RESOLUTION`
- `RATE_LIMITED`

### Non-Retryable Errors (fail immediately)
- `INVALID_RESPONSE`
- `PROTOCOL_ERROR`
- `INTENT_NOT_FOUND`
- `DEVICE_NOT_FOUND`
- `INVALID_MAPPING`
- `STATE_CORRUPTION`
- `VALIDATION_ERROR`

Example:
```python
try:
    result = await bridge.execute_intent("unknown_intent")
except CompanionError as e:
    print(f"Error: {e.error_type.value}")
    print(f"Message: {e.message}")
    print(f"Retryable: {e.is_retryable}")
```

---

## Testing

```bash
# Unit tests
pytest src/infrafabric/integrations/companion/tests/

# Integration tests (requires running Companion instance)
pytest src/infrafabric/integrations/companion/tests/ -m integration
```

---

## Protocol Support

| Protocol | Status | Notes |
|----------|--------|-------|
| HTTP/REST | ✓ Implemented | Primary protocol for Companion API |
| OSC | ⚠ Stub | Requires `python-osc` library |
| TCP Raw | ✓ Implemented | For legacy serial devices |
| UDP Raw | ⚠ Stub | For high-speed triggers |

---

## Roadmap

- [x] Architecture design
- [x] Redis schema definition
- [x] Python class structure
- [x] HTTP protocol support
- [ ] OSC protocol support
- [ ] UDP protocol support
- [ ] Comprehensive unit tests
- [ ] Integration tests
- [ ] IF.sam agent integration
- [ ] vMix protocol templates
- [ ] Production deployment

---

## Related Documentation

- [Architecture Specification](../../../docs/api/integrations/COMPANION_MCR_BRIDGE_ARCHITECTURE.md)
- [Architecture Diagrams](../../../docs/api/integrations/COMPANION_MCR_ARCHITECTURE_DIAGRAMS.md)
- [Bitfocus Companion API](https://github.com/bitfocus/companion)

---

**Generated by Agent 8-10 (The Architects) for InfraFabric Series 2**
