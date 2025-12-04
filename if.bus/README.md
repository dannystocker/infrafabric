# IF.bus - InfraFabric Central Message Bus

**The Motherboard of InfraFabric**

---

## Overview

IF.bus is the central backbone that connects all InfraFabric components. Like a computer motherboard, it provides:

- **Bus Lanes**: Communication channels (DDS, Redis pub/sub)
- **Onboard Chips**: Core IF.* components (guard, witness, yologuard)
- **Expansion Slots**: External API adapters (if.api)
- **Firmware**: Philosophy-grounded protocols (IF.ground)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      IF.bus (Motherboard)                    │
├─────────────────────────────────────────────────────────────┤
│  ONBOARD: IF.guard │ IF.witness │ IF.yologuard │ IF.emotion │
├─────────────────────────────────────────────────────────────┤
│  BUS LANES: if://topic/* (DDS) │ Redis pub/sub │ L1/L2     │
├─────────────────────────────────────────────────────────────┤
│  EXPANSION SLOTS (if.api):                                   │
│  [Broadcast] [Communication] [LLM] [Data] [Defense] [Cloud] │
├─────────────────────────────────────────────────────────────┤
│  FIRMWARE: IF.ground │ Wu Lun │ IF.TTT │ 8 Principles       │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
if.bus/
├── README.md                    # This file
├── IF_BUS_WHITEPAPER.md        # Full architecture specification
├── core/                        # Core bus implementation
├── lanes/                       # Bus lane configurations
├── slots/                       # Slot interface definitions
└── firmware/                    # IF.ground integration
```

## Quick Start

```python
from if_bus import IFBus, ExpansionSlot

# Initialize the bus
bus = IFBus()

# Register an expansion slot (adapter)
bus.register_slot(
    slot_id="vmix-01",
    adapter=VMixAdapter(),
    topics=["if://topic/broadcast/*"]
)

# Publish to bus
bus.publish(
    topic="if://topic/broadcast/status",
    message={"stream": "live", "viewers": 1234}
)

# Subscribe to bus
@bus.subscribe("if://topic/guard/decisions")
def on_decision(message):
    print(f"Council decided: {message}")
```

## Bus Lanes

| Lane | Protocol | Latency | Use Case |
|------|----------|---------|----------|
| Control | DDS RELIABLE | <10ms | Commands |
| Data | DDS BEST_EFFORT | <5ms | Sensor data |
| Status | Redis Pub/Sub | <50ms | Heartbeats |
| Archive | Redis L2 | <200ms | Permanent storage |

## Expansion Slots (if.api)

| Slot | Adapters | Status |
|------|----------|--------|
| Broadcast | vMix, OBS, NDI | Production |
| Communication | SIP (7), WebRTC | Production |
| LLM | Claude, Gemini, DeepSeek | Production |
| Data | Redis L1/L2 | Production |
| Defense | C-UAS 4-layer | Roadmap |
| Cloud | StackCP, OCI | Partial |

## Documentation

- [Full Whitepaper](./IF_BUS_WHITEPAPER.md)
- [if.api Adapters](../if.api/README.md)
- [Philosophy Mapping](../docs/PHILOSOPHY-TO-TECH-MAPPING.md)

---

*IF.bus: The backbone of trustworthy AI coordination*
