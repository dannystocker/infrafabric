# IF.bus: The InfraFabric Motherboard Architecture

**Version:** 1.0.0
**Date:** 2025-12-04
**Status:** Architecture Specification
**Authors:** InfraFabric Team + Claude

---

## Abstract

IF.bus is the central message bus and backbone of the InfraFabric ecosystem. Like a computer motherboard, IF.bus provides the communication infrastructure that connects all IF.* components (onboard chips) and external integrations (expansion cards). This whitepaper defines the architecture, protocols, and integration patterns for IF.bus.

---

## 1. Introduction

### 1.1 The Motherboard Analogy

A computer motherboard serves as the central nervous system of a computer:
- **Onboard chips** provide core functionality (CPU, chipset, audio)
- **Bus lanes** (PCIe, USB, SATA) transport data between components
- **Expansion slots** allow external hardware to integrate
- **BIOS/Firmware** provides foundational configuration
- **Power delivery** ensures all components receive resources

IF.bus mirrors this architecture for AI agent coordination:

| Motherboard Component | IF.bus Equivalent | Purpose |
|----------------------|-------------------|---------|
| Motherboard | IF.bus | Central backbone |
| Onboard chips | IF.guard, IF.witness, IF.yologuard | Core components |
| Bus lanes | DDS topics, Redis pub/sub | Message routing |
| Expansion slots | if.api adapters | External integrations |
| BIOS/Firmware | IF.ground | Philosophical principles |
| Power delivery | IF.connect | Resource management |

### 1.2 Design Principles

1. **Modularity**: Components plug in and out without affecting the bus
2. **Standardization**: All communication follows IF.bus protocols
3. **Resilience**: Bus continues operating if individual components fail
4. **Traceability**: Every message is logged and verifiable (IF.TTT)
5. **Philosophy-Grounded**: Architecture maps to epistemological principles

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│                         IF.bus (MOTHERBOARD)                             │
│                    ═══════════════════════════                           │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     ONBOARD COMPONENTS                           │    │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐          │    │
│  │  │ IF.guard │ │IF.witness│ │IF.yologuard│ │IF.emotion│          │    │
│  │  │  Council │ │Provenance│ │  Security  │ │Personality│          │    │
│  │  └────┬─────┘ └────┬─────┘ └─────┬─────┘ └────┬─────┘          │    │
│  └───────┼────────────┼─────────────┼────────────┼─────────────────┘    │
│          │            │             │            │                       │
│  ════════╪════════════╪═════════════╪════════════╪═══════════════════   │
│          │      PRIMARY BUS LANES (if://topic/*)  │                      │
│  ════════╪════════════╪═════════════╪════════════╪═══════════════════   │
│          │            │             │            │                       │
│  ┌───────┴────────────┴─────────────┴────────────┴─────────────────┐    │
│  │                     BUS CONTROLLERS                              │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │    │
│  │  │IF.connect│ │ IF.swarm │ │ IF.redis │ │  IF.dds  │           │    │
│  │  │ Protocol │ │  Coord   │ │  Cache   │ │Transport │           │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ════════════════════════════════════════════════════════════════════   │
│                      EXPANSION SLOT INTERFACE                            │
│  ════════════════════════════════════════════════════════════════════   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     EXPANSION SLOTS (if.api)                     │    │
│  │                                                                  │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │    │
│  │  │Broadcast│ │  Comms  │ │   LLM   │ │  Data   │ │ Defense │  │    │
│  │  │ vMix    │ │  SIP    │ │ Claude  │ │  Redis  │ │  C-UAS  │  │    │
│  │  │ OBS     │ │ WebRTC  │ │ Gemini  │ │  L1/L2  │ │ Drone   │  │    │
│  │  │ NDI     │ │ H.323   │ │DeepSeek │ │  File   │ │ IFF     │  │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │    │
│  │   SLOT 1      SLOT 2      SLOT 3      SLOT 4      SLOT 5      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     FIRMWARE (IF.ground)                         │    │
│  │  Philosophy Database │ Wu Lun │ 8 Principles │ TTT Compliance   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Components (Onboard Chips)

### 3.1 IF.guard - The Governance Chipset

**Function**: Multi-voice deliberation and decision-making

**Specifications**:
- 20-voice Guardian Council (6 Core + 3 Western + 3 Eastern + 8 CEO facets)
- Threshold voting (k-of-n signatures)
- Contrarian veto power for >95% consensus
- Citation-backed decisions

**Bus Interface**:
```
if://topic/guard/deliberations    # Council debates
if://topic/guard/decisions        # Final verdicts
if://topic/guard/vetoes           # Contrarian blocks
```

### 3.2 IF.witness - The Provenance Tracker

**Function**: Immutable audit trail and evidence chain

**Specifications**:
- SHA-256 content hashing
- Ed25519 signatures
- Merkle tree aggregation
- OpenTimestamps anchoring

**Bus Interface**:
```
if://topic/witness/citations      # New citations
if://topic/witness/proofs         # Merkle proofs
if://topic/witness/anchors        # Blockchain anchors
```

### 3.3 IF.yologuard - The Security Processor

**Function**: Secret detection and credential protection

**Specifications**:
- Shannon entropy analysis
- Recursive encoding detection (Base64/Hex/JSON)
- Wu Lun relationship mapping
- 100x false-positive reduction

**Bus Interface**:
```
if://topic/security/scans         # Scan requests
if://topic/security/findings      # Detected secrets
if://topic/security/alerts        # High-priority alerts
```

### 3.4 IF.emotion - The Personality Engine

**Function**: Authentic voice and emotional intelligence

**Specifications**:
- Vocal DNA extraction
- Personality preservation
- Contextual tone adaptation
- Cross-cultural communication

**Bus Interface**:
```
if://topic/emotion/analysis       # Input analysis
if://topic/emotion/synthesis      # Output generation
if://topic/emotion/calibration    # Voice tuning
```

---

## 4. Bus Lanes (Communication Channels)

### 4.1 Primary Bus Lanes

| Lane | Protocol | Bandwidth | Latency | Use Case |
|------|----------|-----------|---------|----------|
| **Control Bus** | DDS RELIABLE | High | <10ms | Commands, decisions |
| **Data Bus** | DDS BEST_EFFORT | Very High | <5ms | Sensor data, tracks |
| **Status Bus** | Redis Pub/Sub | Medium | <50ms | Heartbeats, status |
| **Archive Bus** | Redis L2 | Low | <200ms | Permanent storage |

### 4.2 Lane Specifications (DDS QoS)

```yaml
# Control Bus - Reliable delivery for commands
control_bus:
  reliability: RELIABLE
  durability: TRANSIENT_LOCAL
  history: {kind: KEEP_LAST, depth: 100}
  deadline: 100ms
  lifespan: 3600s

# Data Bus - High throughput for sensor data
data_bus:
  reliability: BEST_EFFORT
  durability: VOLATILE
  history: {kind: KEEP_LAST, depth: 10}
  deadline: 10ms
  lifespan: 60s

# Status Bus - Agent heartbeats
status_bus:
  reliability: RELIABLE
  durability: TRANSIENT_LOCAL
  history: {kind: KEEP_LAST, depth: 1}
  deadline: 5000ms
  lifespan: 30s
```

### 4.3 URI Addressing Scheme

All bus communication uses the `if://` URI scheme:

```
if://topic/<domain>/<channel>     # Topic addressing
if://agent/<type>/<id>            # Agent addressing
if://citation/<uuid>              # Citation references
if://decision/<id>                # Decision records
```

**Examples**:
```
if://topic/tracks/uav             # UAV tracking data
if://topic/guard/decisions        # Council decisions
if://agent/swarm/worker-001       # Specific agent
if://citation/9f2b3a1e-...        # Citation lookup
```

---

## 5. Expansion Slots (if.api)

### 5.1 Slot Architecture

Each expansion slot provides a standardized interface for external integrations:

```python
class ExpansionSlot(ABC):
    """Base class for all if.api expansion slots"""

    @abstractmethod
    def connect_to_bus(self, bus: IFBus) -> bool:
        """Establish connection to IF.bus"""
        pass

    @abstractmethod
    def subscribe_topics(self) -> list[str]:
        """Topics this slot listens to"""
        pass

    @abstractmethod
    def publish_topics(self) -> list[str]:
        """Topics this slot publishes to"""
        pass

    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Report slot health to bus"""
        pass
```

### 5.2 Current Expansion Slots

| Slot | Category | Adapters | Status |
|------|----------|----------|--------|
| **SLOT 1** | Broadcast | vMix, OBS, NDI, HA | Production |
| **SLOT 2** | Communication | SIP (7), WebRTC, H.323 | Production |
| **SLOT 3** | LLM | Claude, Gemini, DeepSeek | Production |
| **SLOT 4** | Data | Redis L1/L2, File Cache | Production |
| **SLOT 5** | Defense | C-UAS (4-layer) | Roadmap |
| **SLOT 6** | Cloud | StackCP, OCI | Partial |
| **SLOT 7** | Messaging | SMS, Email, Team | Research |
| **SLOT 8** | Security | Yologuard v3 | Production |

### 5.3 Slot Communication Pattern

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   External  │         │  if.api     │         │   IF.bus    │
│   Service   │◄───────►│  Adapter    │◄───────►│   Lanes     │
│  (vMix API) │  HTTP   │(vmix_adapt) │  DDS    │             │
└─────────────┘         └─────────────┘         └─────────────┘
                              │
                              ▼
                        Translation:
                        - Protocol conversion
                        - Message formatting
                        - Error handling
                        - IF.TTT compliance
```

---

## 6. Firmware Layer (IF.ground)

### 6.1 Philosophy Database

The firmware layer encodes the philosophical principles that govern all bus operations:

| Principle | Philosopher | Bus Implementation |
|-----------|-------------|-------------------|
| Empiricism | Locke (1689) | All claims require observable evidence |
| Verificationism | Vienna Circle | Content-addressed messages (SHA-256) |
| Fallibilism | Peirce (1877) | Belief revision via CRDTs |
| Coherentism | Neurath (1932) | Merkle tree consistency |
| Pragmatism | James (1907) | FIPA-ACL speech acts |
| Falsifiability | Popper (1934) | Ed25519 signatures |
| Stoic Prudence | Epictetus | Retry with exponential backoff |
| Wu Lun | Confucius | Agent relationship taxonomy |

### 6.2 IF.TTT Compliance

All bus messages MUST be:
- **Traceable**: Link to source (file:line, commit, citation)
- **Transparent**: Auditable decision trail
- **Trustworthy**: Cryptographically signed

```json
{
  "message_id": "if://msg/2025-12-04/abc123",
  "ttt_compliance": {
    "traceable": {
      "source": "if.api/broadcast/vmix_adapter.py:142",
      "commit": "abc123def",
      "citation_id": "if://citation/xyz789"
    },
    "transparent": {
      "decision_trail": ["if://decision/stream-start-001"],
      "audit_log": "if://topic/audit/vmix"
    },
    "trustworthy": {
      "signature": "ed25519:p9RLz6Y4...",
      "public_key": "ed25519:AAAC3NzaC1...",
      "verified": true
    }
  }
}
```

---

## 7. Message Protocol

### 7.1 Standard Message Format

All IF.bus messages follow this structure:

```json
{
  "header": {
    "message_id": "if://msg/uuid",
    "timestamp": 1733323500000000000,
    "sequence_num": 42,
    "conversation_id": "if://conversation/mission-xyz"
  },
  "routing": {
    "sender": "if://agent/api/vmix-adapter-01",
    "receiver": "if://agent/guard/council",
    "topic": "if://topic/broadcast/status",
    "priority": "normal"
  },
  "content": {
    "performative": "inform",
    "payload": { ... },
    "content_hash": "sha256:5a3d2f8c..."
  },
  "provenance": {
    "citation_ids": ["if://citation/..."],
    "evidence": ["vmix-api-response.json:15"]
  },
  "security": {
    "signature": {
      "algorithm": "ed25519",
      "public_key": "ed25519:...",
      "signature_bytes": "ed25519:..."
    }
  }
}
```

### 7.2 Performatives (Speech Acts)

| Performative | Meaning | Response Expected |
|--------------|---------|-------------------|
| `inform` | Share information | None |
| `request` | Ask for action | `agree` or `refuse` |
| `query-if` | Ask yes/no question | `inform` with answer |
| `agree` | Accept request | Action execution |
| `refuse` | Decline request | Reason provided |
| `propose` | Suggest action | `accept` or `reject` |

---

## 8. Hot-Plug Support

### 8.1 Dynamic Slot Registration

Expansion slots can be added/removed at runtime:

```python
# Register new adapter
bus.register_slot(
    slot_id="vmix-adapter-02",
    adapter=VMixAdapter(host="192.168.1.20"),
    topics_subscribe=["if://topic/broadcast/commands"],
    topics_publish=["if://topic/broadcast/status"]
)

# Hot-remove adapter
bus.unregister_slot("vmix-adapter-02")
```

### 8.2 Health Monitoring

```yaml
# Bus health check interval
health_check:
  interval: 5000ms
  timeout: 2000ms
  unhealthy_threshold: 3
  actions:
    on_unhealthy: isolate_slot
    on_recovery: reintegrate_slot
```

---

## 9. Implementation Roadmap

### Phase 1: Core Bus (Q1 2026)
- [ ] IF.bus core message routing
- [ ] DDS transport integration
- [ ] Redis pub/sub fallback
- [ ] Basic slot interface

### Phase 2: Onboard Components (Q2 2026)
- [ ] IF.guard bus integration
- [ ] IF.witness bus integration
- [ ] IF.yologuard bus integration
- [ ] IF.emotion bus integration

### Phase 3: Expansion Slots (Q3 2026)
- [ ] Migrate if.api adapters to slot interface
- [ ] Hot-plug support
- [ ] Health monitoring dashboard
- [ ] Performance optimization

### Phase 4: Advanced Features (Q4 2026)
- [ ] Multi-bus federation
- [ ] Cross-region routing
- [ ] Quantum-resistant signatures
- [ ] Hardware security module integration

---

## 10. Conclusion

IF.bus provides the motherboard-like backbone for InfraFabric's distributed AI coordination. By standardizing communication through bus lanes and expansion slots, the architecture achieves:

1. **Modularity**: Components plug in without system changes
2. **Reliability**: Bus continues if individual slots fail
3. **Traceability**: Every message is auditable (IF.TTT)
4. **Scalability**: Add capacity by adding slots
5. **Philosophy-Grounded**: Architecture embodies epistemological principles

The motherboard analogy isn't just metaphor—it's executable architecture.

---

## References

- IF.ground Philosophy Database: `/docs/PHILOSOPHY-TO-TECH-MAPPING.md`
- IF URI Scheme: `/docs/IF-URI-SCHEME.md`
- Swarm Communication Security: `/docs/SWARM-COMMUNICATION-SECURITY.md`
- API Integrations Inventory: `/IF-API-INTEGRATIONS-INVENTORY.md`

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **IF.bus** | Central message bus (motherboard) |
| **Onboard** | Core IF.* components integrated into bus |
| **Slot** | Expansion interface for external adapters |
| **Lane** | Communication channel (DDS topic or Redis) |
| **Firmware** | IF.ground philosophical principles |
| **Hot-plug** | Add/remove components at runtime |

---

*IF.bus: The Backbone of Trustworthy AI Coordination*

**Document Version**: 1.0.0
**Generated**: 2025-12-04 15:50 UTC
**Citation**: `if://doc/whitepaper/if-bus-motherboard-v1.0`
