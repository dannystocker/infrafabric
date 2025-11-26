# Companion MCR Bridge - Architecture Diagrams & Examples
**Series 2 - Protocol IF.mcr.companion**
**Generated:** 2025-11-26
**Companion to:** COMPANION_MCR_BRIDGE_ARCHITECTURE.md

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        INFRAFABRIC AGENT LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ IF.sam   │  │ IF.guard │  │ IF.rory  │  │ IF.joe   │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │             │              │              │                     │
│       └─────────────┴──────────────┴──────────────┘                     │
│                            │                                            │
│                            ▼                                            │
│               ┌────────────────────────────┐                            │
│               │  Semantic Intent Interface │                            │
│               │  "studio_dark_mode"        │                            │
│               │  "emergency_lights"        │                            │
│               │  "vmix_input_1"            │                            │
│               └─────────────┬──────────────┘                            │
└─────────────────────────────┼───────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────┐
│                    COMPANION MCR BRIDGE LAYER                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │            CompanionVirtualSurface (Python Class)               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │   │
│  │  │ Intent       │  │ Protocol     │  │ Device       │         │   │
│  │  │ Resolver     │  │ Executor     │  │ Manager      │         │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │   │
│  │         │                  │                  │                  │   │
│  │         └──────────────────┼──────────────────┘                  │   │
│  │                            │                                     │   │
│  │         ┌──────────────────▼──────────────────┐                 │   │
│  │         │   Variable Substitution Engine      │                 │   │
│  │         │   Template + Vars → Command         │                 │   │
│  │         └──────────────────┬──────────────────┘                 │   │
│  │                            │                                     │   │
│  │         ┌──────────────────▼──────────────────┐                 │   │
│  │         │   Retry & Error Handling            │                 │   │
│  │         │   Exponential Backoff               │                 │   │
│  │         └──────────────────┬──────────────────┘                 │   │
│  └────────────────────────────┼──────────────────────────────────────┘   │
└─────────────────────────────┼───────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────┐
│                         REDIS STATE LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │  Bridge      │  │  Protocol    │  │  Device      │                 │
│  │  Config      │  │  Templates   │  │  Catalog     │                 │
│  │  mcr:bridge: │  │  mcr:        │  │  mcr:catalog:│                 │
│  │  companion:  │  │  protocol:*  │  │  companion:* │                 │
│  │  config      │  │              │  │              │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │  Intent      │  │  Button      │  │  Macro       │                 │
│  │  Mappings    │  │  State       │  │  Sequences   │                 │
│  │  mcr:mapping:│  │  mcr:        │  │  mcr:        │                 │
│  │  companion:* │  │  companion:  │  │  companion:  │                 │
│  │              │  │  state:*     │  │  macro:*     │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────┐
│                     PROTOCOL EXECUTION LAYER                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  HTTP    │  │  OSC     │  │  TCP     │  │  UDP     │              │
│  │  Client  │  │  Client  │  │  Client  │  │  Client  │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │             │              │              │                     │
│       └─────────────┴──────────────┴──────────────┘                     │
│                            │                                            │
└─────────────────────────────┼───────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────┐
│                    BITFOCUS COMPANION                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   Companion HTTP API                            │   │
│  │  GET  /api/surfaces        - List devices                       │   │
│  │  POST /api/location/[loc]  - Press button                       │   │
│  │  PUT  /api/location/[loc]  - Update button                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   Virtual/Physical Surfaces                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │   │
│  │  │ StreamDeck  │  │ X-Touch     │  │ Virtual     │            │   │
│  │  │ XL          │  │ Mini        │  │ Surface     │            │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────┐
│                    CONTROL TARGETS                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ vMix        │  │ OBS Studio  │  │ Lighting    │  │ Audio Mixer │  │
│  │ Production  │  │ Streaming   │  │ System      │  │ Console     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Intent Resolution Flow (Detailed)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: INTENT LOOKUP                                                  │
└─────────────────────────────────────────────────────────────────────────┘

  Agent Request:
  ┌────────────────────────────────────────────────────────────────┐
  │ intent_name: "studio_dark_mode"                                │
  │ context: {"agent": "if.sam", "priority": "high"}               │
  └───────────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
  Redis Lookup:
  ┌────────────────────────────────────────────────────────────────┐
  │ Key: mcr:mapping:companion:intent:studio_dark_mode             │
  │                                                                │
  │ Value (JSON):                                                  │
  │ {                                                              │
  │   "intent_name": "studio_dark_mode",                           │
  │   "description": "Enable dark mode studio lighting",           │
  │   "actions": [                                                 │
  │     {                                                          │
  │       "action_type": "press",                                  │
  │       "protocol_name": "press",                                │
  │       "device_id": "studio_main",                              │
  │       "variables": {"page": 1, "row": 0, "col": 0},           │
  │       "delay_ms": 0                                            │
  │     },                                                         │
  │     {                                                          │
  │       "action_type": "set_text",                               │
  │       "protocol_name": "set_text",                             │
  │       "device_id": "studio_main",                              │
  │       "variables": {                                           │
  │         "page": 1, "row": 0, "col": 0,                        │
  │         "text": "DARK MODE"                                    │
  │       },                                                       │
  │       "delay_ms": 500                                          │
  │     }                                                          │
  │   ],                                                           │
  │   "priority": 1,                                               │
  │   "created_by": "if.sam"                                       │
  │ }                                                              │
  └───────────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
  Parse to Pydantic Model:
  ┌────────────────────────────────────────────────────────────────┐
  │ IntentMapping(                                                 │
  │   intent_name="studio_dark_mode",                              │
  │   actions=[                                                    │
  │     ButtonAction(...),                                         │
  │     ButtonAction(...)                                          │
  │   ]                                                            │
  │ )                                                              │
  └───────────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: ACTION RESOLUTION (Loop for each action)                       │
└─────────────────────────────────────────────────────────────────────────┘

  Action #1: Press Button
  ┌────────────────────────────────────────────────────────────────┐
  │ action_type: "press"                                           │
  │ protocol_name: "press"                                         │
  │ device_id: "studio_main"                                       │
  │ variables: {"page": 1, "row": 0, "col": 0}                    │
  └───────────────────────────────┬────────────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
    ┌─────────┐           ┌─────────────┐        ┌──────────────┐
    │ Lookup  │           │   Lookup    │        │   Merge      │
    │ Protocol│           │   Device    │        │   Variables  │
    └────┬────┘           └──────┬──────┘        └──────┬───────┘
         │                       │                      │
         ▼                       ▼                      ▼

  Protocol Lookup:
  ┌────────────────────────────────────────────────────────────────┐
  │ Key: mcr:protocol:companion:press                              │
  │                                                                │
  │ Value:                                                         │
  │ {                                                              │
  │   "protocol_name": "press",                                    │
  │   "protocol_type": "http",                                     │
  │   "template": "/api/location/{page}/{row}/{col}/press",       │
  │   "method": "POST",                                            │
  │   "variables": ["page", "row", "col"]                         │
  │ }                                                              │
  └───────────────────────────────┬────────────────────────────────┘
                                  │
  Device Lookup:                  │
  ┌────────────────────────────────────────────────────────────────┐
  │ Key: mcr:catalog:companion:device:studio_main                  │
  │                                                                │
  │ Value:                                                         │
  │ {                                                              │
  │   "device_id": "studio_main",                                  │
  │   "device_type": "streamdeck_xl",                              │
  │   "page_count": 10,                                            │
  │   "rows": 8,                                                   │
  │   "cols": 8,                                                   │
  │   "connection_url": null,                                      │
  │   "metadata": {                                                │
  │     "location": "Control Room A",                              │
  │     "serial": "CL09H1A01234"                                   │
  │   }                                                            │
  │ }                                                              │
  └───────────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: VARIABLE SUBSTITUTION                                          │
└─────────────────────────────────────────────────────────────────────────┘

  Template:        "/api/location/{page}/{row}/{col}/press"
  Variables:       {"page": 1, "row": 0, "col": 0}

  Substitution Process:
  ┌────────────────────────────────────────────────────────────────┐
  │ Step 1: Replace {page}  → "/api/location/1/{row}/{col}/press" │
  │ Step 2: Replace {row}   → "/api/location/1/0/{col}/press"     │
  │ Step 3: Replace {col}   → "/api/location/1/0/0/press"         │
  │                                                                │
  │ Final Command: "/api/location/1/0/0/press"                    │
  └───────────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: COMMAND EXECUTION                                              │
└─────────────────────────────────────────────────────────────────────────┘

  HTTP Request:
  ┌────────────────────────────────────────────────────────────────┐
  │ Method:  POST                                                  │
  │ URL:     http://companion:8888/api/location/1/0/0/press       │
  │ Headers: {"Content-Type": "application/json"}                 │
  │ Body:    {}                                                    │
  │ Timeout: 5000ms                                                │
  └───────────────────────────────┬────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                Success                     Failure
                    │                           │
                    ▼                           ▼
          ┌──────────────────┐        ┌──────────────────┐
          │ HTTP 200 OK      │        │ Connection Error │
          │ Response: {...}  │        │ Timeout / Refused│
          └────────┬─────────┘        └────────┬─────────┘
                   │                           │
                   │                           ▼
                   │                  ┌──────────────────┐
                   │                  │  Retry Logic     │
                   │                  │  (Exponential    │
                   │                  │   Backoff)       │
                   │                  └────────┬─────────┘
                   │                           │
                   │                    ┌──────┴────┐
                   │                    │           │
                   │                 Success    Max Retries
                   │                    │           │
                   └────────────────────┴───────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: STATE UPDATE & RESPONSE                                        │
└─────────────────────────────────────────────────────────────────────────┘

  Update Button State:
  ┌────────────────────────────────────────────────────────────────┐
  │ Key: mcr:companion:state:studio_main:1_0_0                     │
  │                                                                │
  │ Value:                                                         │
  │ {                                                              │
  │   "device_id": "studio_main",                                  │
  │   "button_id": "1_0_0",                                        │
  │   "state": "pressed",                                          │
  │   "text": "DARK MODE",                                         │
  │   "color": null,                                               │
  │   "last_pressed": "2025-11-26T10:30:00.123Z",                  │
  │   "press_count": 42,                                           │
  │   "updated_at": "2025-11-26T10:30:00.123Z"                     │
  │ }                                                              │
  └───────────────────────────────┬────────────────────────────────┘
                                  │
  Return Result:                  │
  ┌────────────────────────────────────────────────────────────────┐
  │ ExecutionResult(                                               │
  │   success=True,                                                │
  │   intent_name="studio_dark_mode",                              │
  │   actions_executed=2,                                          │
  │   latency_ms=143.5,                                            │
  │   error=None,                                                  │
  │   metadata={                                                   │
  │     "device_id": "studio_main",                                │
  │     "buttons_pressed": ["1_0_0"]                               │
  │   }                                                            │
  │ )                                                              │
  └────────────────────────────────────────────────────────────────┘
```

---

## 3. Protocol Execution Matrix

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     PROTOCOL TYPE COMPARISON                             │
├───────────┬──────────────┬──────────────┬──────────────┬──────────────┤
│ Feature   │ HTTP/REST    │ OSC          │ TCP Raw      │ UDP Raw      │
├───────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Protocol  │ HTTP/1.1     │ UDP Datagram │ TCP Stream   │ UDP Datagram │
│ Layer     │              │              │              │              │
├───────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Reliable  │ ✓ Yes        │ ✗ No         │ ✓ Yes        │ ✗ No         │
│ Delivery  │ (TCP)        │              │              │              │
├───────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Ordered   │ ✓ Yes        │ ✗ No         │ ✓ Yes        │ ✗ No         │
│ Messages  │              │              │              │              │
├───────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Typical   │ 10-50ms      │ 1-5ms        │ 5-20ms       │ 1-5ms        │
│ Latency   │              │              │              │              │
├───────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Use Case  │ Standard API │ Real-time    │ Legacy       │ High-speed   │
│           │ control      │ audio/video  │ devices      │ triggers     │
├───────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Retry     │ Recommended  │ App-level    │ Built-in     │ App-level    │
│ Strategy  │              │              │              │              │
├───────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Example   │ Companion    │ vMix/OBS     │ Serial       │ DMX Lighting │
│           │ HTTP API     │ OSC Control  │ Devices      │ Control      │
└───────────┴──────────────┴──────────────┴──────────────┴──────────────┘

EXECUTION FLOW BY PROTOCOL:

┌──────────────────────────────────────────────────────────────────────────┐
│ HTTP/REST EXECUTION                                                      │
└──────────────────────────────────────────────────────────────────────────┘

  Request:
    POST http://companion:8888/api/location/1/0/0/press
    Headers: {"Content-Type": "application/json"}
    Body: {"action": "press", "metadata": {"agent": "if.sam"}}

  Response:
    200 OK
    {"success": true, "message": "Button pressed"}

  Error Handling:
    - 4xx: Non-retryable (invalid request)
    - 5xx: Retryable (server error)
    - Timeout: Retryable (network issue)


┌──────────────────────────────────────────────────────────────────────────┐
│ OSC EXECUTION                                                            │
└──────────────────────────────────────────────────────────────────────────┘

  OSC Message:
    Address: /companion/button/1/0/press
    Args: (1,)  # Integer argument: 1 = press, 0 = release
    Destination: 127.0.0.1:12345 (UDP)

  No Response:
    OSC is fire-and-forget (no acknowledgment)

  Error Handling:
    - Network error: Retryable
    - No way to detect delivery failure


┌──────────────────────────────────────────────────────────────────────────┐
│ TCP RAW EXECUTION                                                        │
└──────────────────────────────────────────────────────────────────────────┘

  Command:
    BUTTON studio_main 1 0 0 PRESS\r\n

  Connection:
    TCP to companion:9999

  Response:
    OK\r\n

  Error Handling:
    - Connection refused: Retryable
    - Protocol error: Non-retryable


┌──────────────────────────────────────────────────────────────────────────┐
│ UDP RAW EXECUTION                                                        │
└──────────────────────────────────────────────────────────────────────────┘

  Datagram:
    BTN|studio_main|1|0|0|press

  Destination:
    UDP to companion:9998

  No Response:
    Fire-and-forget

  Error Handling:
    - Network error: Retryable
    - No acknowledgment
```

---

## 4. Macro Execution Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        MACRO EXECUTION FLOW                              │
└──────────────────────────────────────────────────────────────────────────┘

Macro Definition: "morning_startup"
┌────────────────────────────────────────────────────────────────────────┐
│ Key: mcr:companion:macro:morning_startup                               │
│                                                                        │
│ {                                                                      │
│   "macro_id": "morning_startup",                                       │
│   "macro_name": "Morning Studio Startup Sequence",                     │
│   "description": "Power on studio, lights, cameras",                   │
│   "steps": [                                                           │
│     {                                                                  │
│       "step_number": 1,                                                │
│       "intent_name": "studio_power_on",                                │
│       "wait_for_completion": true,                                     │
│       "timeout_ms": 5000,                                              │
│       "on_failure": "abort"                                            │
│     },                                                                 │
│     {                                                                  │
│       "step_number": 2,                                                │
│       "intent_name": "studio_lights_on",                               │
│       "wait_for_completion": true,                                     │
│       "timeout_ms": 3000,                                              │
│       "on_failure": "continue"                                         │
│     },                                                                 │
│     {                                                                  │
│       "step_number": 3,                                                │
│       "intent_name": "studio_camera_preset_1",                         │
│       "wait_for_completion": false,                                    │
│       "timeout_ms": 2000,                                              │
│       "on_failure": "continue"                                         │
│     }                                                                  │
│   ]                                                                    │
│ }                                                                      │
└────────────────────────────────────────────────────────────────────────┘

Execution Timeline:
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│ T=0ms        Step 1 Start: "studio_power_on"                          │
│              ┌────────────────────────────────────┐                   │
│              │ Execute Intent: studio_power_on    │                   │
│              │ Wait for completion: YES           │                   │
│              └──────────────┬─────────────────────┘                   │
│                             │                                          │
│ T=1200ms     Step 1 Complete (Success)                                │
│              └──────────────┘                                          │
│                             │                                          │
│                             ▼                                          │
│              Step 2 Start: "studio_lights_on"                         │
│              ┌────────────────────────────────────┐                   │
│              │ Execute Intent: studio_lights_on   │                   │
│              │ Wait for completion: YES           │                   │
│              └──────────────┬─────────────────────┘                   │
│                             │                                          │
│ T=3800ms     Step 2 Complete (Success)                                │
│              └──────────────┘                                          │
│                             │                                          │
│                             ▼                                          │
│              Step 3 Start: "studio_camera_preset_1"                   │
│              ┌────────────────────────────────────┐                   │
│              │ Execute Intent: camera_preset_1    │                   │
│              │ Wait for completion: NO            │                   │
│              └──────────────┬─────────────────────┘                   │
│                             │                                          │
│ T=3850ms     Step 3 Dispatched (Async)                                │
│              └──────────────┘                                          │
│                             │                                          │
│ T=3850ms     Macro Complete                                           │
│              ┌──────────────────────────────────┐                     │
│              │ Result:                          │                     │
│              │ - Steps Executed: 3              │                     │
│              │ - Steps Failed: 0                │                     │
│              │ - Total Time: 3850ms             │                     │
│              └──────────────────────────────────┘                     │
└────────────────────────────────────────────────────────────────────────┘

Error Handling Examples:

Scenario 1: Step 1 fails (on_failure="abort")
┌────────────────────────────────────────────────────────────────────────┐
│ T=0ms        Step 1 Start: "studio_power_on"                          │
│              │                                                          │
│ T=5000ms     Step 1 Timeout (FAILURE)                                 │
│              ├─ on_failure: "abort"                                    │
│              └─ ABORT MACRO                                            │
│                                                                        │
│ Result: MacroAbortError("Step 1 failed")                              │
└────────────────────────────────────────────────────────────────────────┘

Scenario 2: Step 2 fails (on_failure="continue")
┌────────────────────────────────────────────────────────────────────────┐
│ T=0ms        Step 1 Success                                            │
│ T=1200ms     Step 2 Start: "studio_lights_on"                         │
│              │                                                          │
│ T=3000ms     Step 2 Timeout (FAILURE)                                 │
│              ├─ on_failure: "continue"                                 │
│              └─ Log error, continue to Step 3                          │
│                                                                        │
│ T=3000ms     Step 3 Execute                                            │
│ T=3500ms     Step 3 Success                                            │
│                                                                        │
│ Result: Partial Success (1 failure, 2 success)                        │
└────────────────────────────────────────────────────────────────────────┘

Scenario 3: Step with retry
┌────────────────────────────────────────────────────────────────────────┐
│ T=0ms        Step 1 Start                                              │
│              │                                                          │
│ T=5000ms     Step 1 Timeout (FAILURE)                                 │
│              ├─ on_failure: "retry"                                    │
│              └─ Retry Step 1                                           │
│                                                                        │
│ T=5100ms     Step 1 Retry Start                                        │
│ T=6200ms     Step 1 Retry Success                                      │
│              └─ Continue to Step 2                                     │
│                                                                        │
│ Result: Success (1 retry)                                              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Error Handling State Machine

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     ERROR HANDLING STATE MACHINE                         │
└──────────────────────────────────────────────────────────────────────────┘

                            ┌────────────┐
                            │  INITIAL   │
                            │   STATE    │
                            └─────┬──────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │   EXECUTE COMMAND     │
                      └──────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                SUCCESS                   FAILURE
                    │                         │
                    ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐
          │  UPDATE STATE   │       │  CLASSIFY ERROR │
          │  RETURN SUCCESS │       └────────┬────────┘
          └─────────────────┘                │
                                             │
                              ┌──────────────┴──────────────┐
                              │                             │
                         RETRYABLE                    NON-RETRYABLE
                              │                             │
                              ▼                             ▼
                    ┌──────────────────┐        ┌──────────────────┐
                    │  CHECK RETRY     │        │  RETURN ERROR    │
                    │  ATTEMPTS        │        │  IMMEDIATELY     │
                    └────────┬─────────┘        └──────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
           ATTEMPTS < MAX            ATTEMPTS >= MAX
                │                         │
                ▼                         ▼
    ┌──────────────────────┐   ┌──────────────────────┐
    │  CALCULATE BACKOFF   │   │  RETURN MAX RETRIES  │
    │  DELAY               │   │  EXCEEDED ERROR      │
    └──────────┬───────────┘   └──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  WAIT (EXPONENTIAL   │
    │  BACKOFF)            │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  INCREMENT ATTEMPT   │
    │  COUNTER             │
    └──────────┬───────────┘
               │
               └───────────────┐
                               │
                               ▼
                      ┌───────────────────────┐
                      │   RETRY COMMAND       │
                      └───────────────────────┘
                               │
                               └──────► (Back to EXECUTE COMMAND)


ERROR CLASSIFICATION TABLE:

┌────────────────────────────────────────────────────────────────────┐
│ Error Type            │ Retryable │ Backoff  │ Max Retries │ Notes│
├───────────────────────┼───────────┼──────────┼─────────────┼──────┤
│ CONNECTION_REFUSED    │ ✓ Yes     │ Exp.     │ 3           │      │
│ CONNECTION_TIMEOUT    │ ✓ Yes     │ Exp.     │ 3           │      │
│ DNS_RESOLUTION        │ ✓ Yes     │ Linear   │ 2           │      │
│ RATE_LIMITED          │ ✓ Yes     │ Fixed    │ 5           │ 60s  │
├───────────────────────┼───────────┼──────────┼─────────────┼──────┤
│ INVALID_RESPONSE      │ ✗ No      │ N/A      │ 0           │      │
│ PROTOCOL_ERROR        │ ✗ No      │ N/A      │ 0           │      │
│ INTENT_NOT_FOUND      │ ✗ No      │ N/A      │ 0           │      │
│ DEVICE_NOT_FOUND      │ ✗ No      │ N/A      │ 0           │      │
│ INVALID_MAPPING       │ ✗ No      │ N/A      │ 0           │      │
│ STATE_CORRUPTION      │ ✗ No      │ N/A      │ 0           │      │
│ VALIDATION_ERROR      │ ✗ No      │ N/A      │ 0           │      │
└────────────────────────────────────────────────────────────────────┘

EXPONENTIAL BACKOFF CALCULATION:

Attempt    Delay (initial=1000ms, multiplier=2.0, max=10000ms)
───────    ────────────────────────────────────────────────────
   0       0ms          (no delay, first attempt)
   1       1000ms       (1s)
   2       2000ms       (2s)
   3       4000ms       (4s)
   4       8000ms       (8s)
   5       10000ms      (capped at max)
   6+      10000ms      (capped at max)


RETRY TIMELINE EXAMPLE:

┌─────────────────────────────────────────────────────────────────────┐
│ Timeline for CONNECTION_TIMEOUT (max_retries=3)                    │
└─────────────────────────────────────────────────────────────────────┘

T=0ms       │ Attempt 1: Execute command
            │ ├─ Connect to companion:8888
            │ │
T=5000ms    │ └─ Timeout (5000ms)
            │
T=5001ms    │ Classify: CONNECTION_TIMEOUT (retryable)
            │ Calculate backoff: 1000ms
            │ Wait...
            │
T=6001ms    │ Attempt 2: Execute command
            │ ├─ Connect to companion:8888
            │ │
T=11001ms   │ └─ Timeout (5000ms)
            │
T=11002ms   │ Classify: CONNECTION_TIMEOUT (retryable)
            │ Calculate backoff: 2000ms
            │ Wait...
            │
T=13002ms   │ Attempt 3: Execute command
            │ ├─ Connect to companion:8888
            │ │
T=18002ms   │ └─ Timeout (5000ms)
            │
T=18003ms   │ Max retries exceeded
            │ Return error: "Max retry attempts (3) exceeded"
            │
Total time: 18003ms (3 attempts × 5s timeout + 1s + 2s backoff)
```

---

## 6. Redis Key Examples (Full Dataset)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE REDIS KEY EXAMPLES                           │
└──────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════
1. BRIDGE CONFIGURATION
═══════════════════════════════════════════════════════════════════════════

Key:   mcr:bridge:companion:config
Type:  string
Value:
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

═══════════════════════════════════════════════════════════════════════════
2. PROTOCOL TEMPLATES
═══════════════════════════════════════════════════════════════════════════

Key:   mcr:protocol:companion:press
Type:  string
Value:
{
  "protocol_name": "press",
  "protocol_type": "http",
  "template": "/api/location/{page}/{row}/{col}/press",
  "method": "POST",
  "headers": {"Content-Type": "application/json"},
  "variables": ["page", "row", "col"],
  "description": "Press button on specified page/row/col"
}

---

Key:   mcr:protocol:companion:set_text
Type:  string
Value:
{
  "protocol_name": "set_text",
  "protocol_type": "http",
  "template": "/api/location/{page}/{row}/{col}/style",
  "method": "PUT",
  "headers": {"Content-Type": "application/json"},
  "variables": ["page", "row", "col", "text"],
  "description": "Update button text label"
}

---

Key:   mcr:protocol:companion:osc_trigger
Type:  string
Value:
{
  "protocol_name": "osc_trigger",
  "protocol_type": "osc",
  "template": "/companion/button/{page}/{button}/press",
  "osc_port": 12345,
  "osc_type": "i",
  "variables": ["page", "button"],
  "description": "Send OSC trigger to Companion"
}

---

Key:   mcr:protocol:companion:tcp_raw
Type:  string
Value:
{
  "protocol_name": "tcp_raw",
  "protocol_type": "tcp",
  "template": "BUTTON {device_id} {page} {row} {col} PRESS\\r\\n",
  "tcp_host": "companion.local",
  "tcp_port": 9999,
  "variables": ["device_id", "page", "row", "col"],
  "description": "Raw TCP button press command"
}

═══════════════════════════════════════════════════════════════════════════
3. DEVICE CATALOG
═══════════════════════════════════════════════════════════════════════════

Key:   mcr:catalog:companion:device:studio_main
Type:  string
Value:
{
  "device_id": "studio_main",
  "device_type": "streamdeck_xl",
  "page_count": 10,
  "rows": 8,
  "cols": 8,
  "connection_url": null,
  "metadata": {
    "location": "Control Room A",
    "serial": "CL09H1A01234",
    "firmware": "5.3.1"
  },
  "created_at": "2025-11-26T10:00:00.000Z",
  "last_seen": "2025-11-26T10:30:00.000Z"
}

---

Key:   mcr:catalog:companion:device:control_room_b
Type:  string
Value:
{
  "device_id": "control_room_b",
  "device_type": "xtouch_mini",
  "page_count": 5,
  "rows": 2,
  "cols": 8,
  "connection_url": "http://192.168.1.100:8888",
  "metadata": {
    "location": "Control Room B",
    "serial": "XTM987654321"
  },
  "created_at": "2025-11-26T09:00:00.000Z",
  "last_seen": "2025-11-26T10:25:00.000Z"
}

═══════════════════════════════════════════════════════════════════════════
4. INTENT MAPPINGS
═══════════════════════════════════════════════════════════════════════════

Key:   mcr:mapping:companion:intent:studio_dark_mode
Type:  string
Value:
{
  "intent_name": "studio_dark_mode",
  "description": "Enable dark mode studio lighting",
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
  "conditions": null,
  "priority": 1,
  "created_by": "if.sam",
  "created_at": "2025-11-26T08:00:00.000Z"
}

---

Key:   mcr:mapping:companion:intent:emergency_lights
Type:  string
Value:
{
  "intent_name": "emergency_lights",
  "description": "Activate emergency lighting system",
  "actions": [
    {
      "action_type": "press",
      "protocol_name": "press",
      "device_id": "studio_main",
      "variables": {"page": 0, "row": 7, "col": 7},
      "delay_ms": 0
    }
  ],
  "conditions": {"priority": "high"},
  "priority": 10,
  "created_by": "if.guard",
  "created_at": "2025-11-26T08:15:00.000Z"
}

---

Key:   mcr:mapping:companion:intent:vmix_input_1
Type:  string
Value:
{
  "intent_name": "vmix_input_1",
  "description": "Activate vMix input 1 (main camera)",
  "actions": [
    {
      "action_type": "press",
      "protocol_name": "press",
      "device_id": "studio_main",
      "variables": {"page": 2, "row": 0, "col": 0},
      "delay_ms": 0
    }
  ],
  "conditions": null,
  "priority": 5,
  "created_by": "if.sam",
  "created_at": "2025-11-26T08:30:00.000Z"
}

═══════════════════════════════════════════════════════════════════════════
5. MACROS
═══════════════════════════════════════════════════════════════════════════

Key:   mcr:companion:macro:morning_startup
Type:  string
Value:
{
  "macro_id": "morning_startup",
  "macro_name": "Morning Studio Startup Sequence",
  "description": "Power on studio, lights, cameras in sequence",
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
  "created_by": "if.sam",
  "created_at": "2025-11-26T07:00:00.000Z"
}

---

Key:   mcr:companion:macro:shutdown_sequence
Type:  string
Value:
{
  "macro_id": "shutdown_sequence",
  "macro_name": "Studio Shutdown Sequence",
  "description": "Safely power down all studio systems",
  "steps": [
    {
      "step_number": 1,
      "intent_name": "studio_camera_standby",
      "wait_for_completion": true,
      "timeout_ms": 3000,
      "on_failure": "continue"
    },
    {
      "step_number": 2,
      "intent_name": "studio_lights_off",
      "wait_for_completion": true,
      "timeout_ms": 3000,
      "on_failure": "continue"
    },
    {
      "step_number": 3,
      "intent_name": "studio_power_off",
      "wait_for_completion": true,
      "timeout_ms": 5000,
      "on_failure": "abort"
    }
  ],
  "created_by": "if.sam",
  "created_at": "2025-11-26T07:15:00.000Z"
}

═══════════════════════════════════════════════════════════════════════════
6. BUTTON STATE TRACKING
═══════════════════════════════════════════════════════════════════════════

Key:   mcr:companion:state:studio_main:1_0_0
Type:  string
Value:
{
  "device_id": "studio_main",
  "button_id": "1_0_0",
  "state": "pressed",
  "text": "DARK",
  "color": "#FF0000",
  "last_pressed": "2025-11-26T10:30:15.123Z",
  "press_count": 42,
  "updated_at": "2025-11-26T10:30:15.123Z"
}

---

Key:   mcr:companion:state:studio_main:0_7_7
Type:  string
Value:
{
  "device_id": "studio_main",
  "button_id": "0_7_7",
  "state": "active",
  "text": "EMERGENCY",
  "color": "#FF0000",
  "last_pressed": "2025-11-26T09:15:30.456Z",
  "press_count": 2,
  "updated_at": "2025-11-26T09:15:30.456Z"
}

═══════════════════════════════════════════════════════════════════════════
7. SESSION MANAGEMENT
═══════════════════════════════════════════════════════════════════════════

Key:   mcr:companion:session:sess_20251126_103000
Type:  string
Value:
{
  "session_id": "sess_20251126_103000",
  "agent_id": "if.sam",
  "device_ids": ["studio_main", "control_room_b"],
  "started_at": "2025-11-26T10:30:00.000Z",
  "last_activity": "2025-11-26T10:35:45.789Z",
  "commands_executed": 127,
  "errors_count": 3,
  "status": "active"
}

═══════════════════════════════════════════════════════════════════════════
8. METRICS
═══════════════════════════════════════════════════════════════════════════

Key:   mcr:companion:metrics
Type:  hash
Fields:
{
  "intents_executed": "1542",
  "intents_failed": "23",
  "actions_executed": "3084",
  "total_latency_ms": "185420.5",
  "retry_count": "67"
}

Computed Metrics:
- Success Rate: 98.5% (1542 / 1565)
- Avg Latency: 120.2ms (185420.5 / 1542)
- Retry Rate: 4.3% (67 / 1542)
```

---

## 7. Class Hierarchy Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        CLASS HIERARCHY                                   │
└──────────────────────────────────────────────────────────────────────────┘

                         ┌────────────────┐
                         │  RedisModel    │
                         │  (Base Class)  │
                         └────────┬───────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
    ┌───────────────────┐ ┌──────────────┐ ┌──────────────┐
    │ CompanionBridge   │ │ Protocol     │ │ Companion    │
    │ Config            │ │ Template     │ │ Device       │
    └───────────────────┘ └──────────────┘ └──────────────┘

                ▼                 ▼                 ▼
    ┌───────────────────┐ ┌──────────────┐ ┌──────────────┐
    │ IntentMapping     │ │ ButtonAction │ │ MacroStep    │
    └───────────────────┘ └──────────────┘ └──────────────┘

                ▼                 ▼                 ▼
    ┌───────────────────┐ ┌──────────────┐ ┌──────────────┐
    │ CompanionMacro    │ │ ButtonState  │ │ Companion    │
    │                   │ │              │ │ Session      │
    └───────────────────┘ └──────────────┘ └──────────────┘


═══════════════════════════════════════════════════════════════════════════

Main Orchestrator:

                    ┌────────────────────────────────┐
                    │  CompanionVirtualSurface       │
                    │  (Main Bridge Interface)       │
                    └────────────────┬───────────────┘
                                     │
                                     │ Has-A
                         ┌───────────┼───────────┐
                         │           │           │
                         ▼           ▼           ▼
                 ┌───────────┐ ┌─────────┐ ┌─────────────┐
                 │  Redis    │ │  HTTP   │ │  Config     │
                 │  Client   │ │  Session│ │  Object     │
                 └───────────┘ └─────────┘ └─────────────┘

             Methods:
             ┌──────────────────────────────────────────┐
             │ - execute_intent(name, context)          │
             │ - execute_macro(macro_id)                │
             │ - register_device(device)                │
             │ - register_intent(mapping)               │
             │ - register_protocol(protocol)            │
             │                                          │
             │ Private:                                 │
             │ - _get_intent_mapping(name)              │
             │ - _get_protocol(name)                    │
             │ - _get_device(id)                        │
             │ - _execute_action(action, context)       │
             │ - _execute_http(...)                     │
             │ - _execute_osc(...)                      │
             │ - _execute_tcp(...)                      │
             │ - _execute_udp(...)                      │
             │ - _update_button_state(...)              │
             └──────────────────────────────────────────┘


Context Manager Wrapper:

                    ┌────────────────────────────────┐
                    │  CompanionBridge               │
                    │  (Context Manager)             │
                    └────────────────┬───────────────┘
                                     │
                                     │ Wraps
                                     ▼
                    ┌────────────────────────────────┐
                    │  CompanionVirtualSurface       │
                    └────────────────────────────────┘

             Usage:
             ┌──────────────────────────────────────────┐
             │ async with CompanionBridge() as bridge:  │
             │     result = await bridge.execute_intent(│
             │         "studio_dark_mode"               │
             │     )                                    │
             └──────────────────────────────────────────┘


Error Handling:

                    ┌────────────────────────────────┐
                    │  CompanionError                │
                    │  (Base Exception)              │
                    └────────────────┬───────────────┘
                                     │
                                     │ Has-A
                                     ▼
                    ┌────────────────────────────────┐
                    │  CompanionErrorType            │
                    │  (Enum)                        │
                    └────────────────────────────────┘

             Error Types:
             - CONNECTION_REFUSED
             - CONNECTION_TIMEOUT
             - DNS_RESOLUTION
             - INVALID_RESPONSE
             - PROTOCOL_ERROR
             - INTENT_NOT_FOUND
             - DEVICE_NOT_FOUND
             - INVALID_MAPPING
             - RATE_LIMITED
             - STATE_CORRUPTION
             - VALIDATION_ERROR


Utility Classes:

    ┌─────────────────────┐    ┌─────────────────────┐
    │ VariableSubstitution│    │ RetryPolicy         │
    │                     │    │                     │
    │ - substitute()      │    │ - get_delay()       │
    └─────────────────────┘    └─────────────────────┘

    ┌─────────────────────┐    ┌─────────────────────┐
    │ FallbackChain       │    │ MetricsCollector    │
    │                     │    │                     │
    │ - execute()         │    │ - record_execution()│
    └─────────────────────┘    │ - get_metrics()     │
                               └─────────────────────┘
```

---

## 8. Deployment Checklist

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      DEPLOYMENT CHECKLIST                                │
└──────────────────────────────────────────────────────────────────────────┘

Phase 1: Redis Initialization
─────────────────────────────────────────────────────────────────────────
[_] Initialize Redis database
[_] Create bridge configuration
[_] Register core protocol templates (press, set_text, osc_trigger, tcp_raw)
[_] Register devices in catalog
[_] Set up initial intent mappings
[_] Configure default macros
[_] Test Redis connectivity

Phase 2: Python Package Installation
─────────────────────────────────────────────────────────────────────────
[_] Install dependencies:
    - redis[asyncio]
    - aiohttp
    - pydantic
    - python-osc (optional, for OSC support)
[_] Deploy CompanionVirtualSurface module
[_] Run unit tests
[_] Run integration tests (if Companion available)

Phase 3: Companion Configuration
─────────────────────────────────────────────────────────────────────────
[_] Install/configure Bitfocus Companion
[_] Enable HTTP API (default port 8888)
[_] Configure devices (StreamDeck, X-Touch, etc.)
[_] Set up initial button pages
[_] Test Companion HTTP API manually (curl/Postman)

Phase 4: Integration
─────────────────────────────────────────────────────────────────────────
[_] Register bridge with InfraFabric core
[_] Integrate with IF.sam agent
[_] Create intent mappings for production use cases
[_] Test end-to-end flow (Agent -> Bridge -> Companion -> Device)
[_] Set up monitoring and metrics collection

Phase 5: Production Readiness
─────────────────────────────────────────────────────────────────────────
[_] Configure retry policies for production
[_] Set up error logging and alerting
[_] Create operational runbooks
[_] Document common troubleshooting steps
[_] Configure backup/restore for Redis state
[_] Load test for expected traffic
[_] Security review (authentication, authorization)
[_] Compliance check (IF.TTT validation)
```

---

**Document Version:** 1.0
**Status:** APPROVED
**Related:** COMPANION_MCR_BRIDGE_ARCHITECTURE.md

*Generated by Agent 8-10 (The Architects) for InfraFabric Series 2*
