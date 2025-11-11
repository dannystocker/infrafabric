# Session 7: IF.bus SIP Adapters Phases 4-10 (ULTRA-CONDENSED)

**Max 50 lines total | SIP Adapter specialization building on Session 4 baseline**

---

## Phase 4: Call Control (originate, hangup, transfer)
| Task | File | Model | Coordination |
|------|------|-------|--------------|
| Originate adapter (dial out SIP calls) | `src/adapters/sip_originate.py` | Sonnet | Integrates with Session 4 proxy |
| Hangup handler (graceful teardown, BYE) | `src/adapters/sip_hangup.py` | Haiku | Non-blocking, clean state removal |
| Transfer adapter (blind/attended transfer) | `src/adapters/sip_transfer.py` | Sonnet | Complex call state management |
| Tests: All adapters pass integration | `tests/adapters/test_call_control.py` | Haiku | **IDLE:** Help Session 5 CLI trace logging |

---

## Phase 5: Advanced Features (conferencing, recording, transcription)
| Task | File | Model | Coordination |
|------|------|-------|--------------|
| Conferencing adapter (3+ party calls) | `src/adapters/sip_conference.py` | Sonnet | MCU bridge via Session 3 H.323 |
| Call recording (SIPREC protocol) | `src/adapters/sip_recorder.py` | Haiku | Archive to IF.witness logs |
| Transcription adapter (async STT) | `src/adapters/sip_transcriber.py` | Sonnet | Integrate Session 6 Talent NLP models |
| **IDLE:** Session 1 NDI metadata enrich, Session 2 WebRTC codec codec optimize |

---

## Phase 6: Multi-Server Orchestration (failover across SIP servers)
| Task | File | Model | Coordination |
|------|------|-------|--------------|
| DNS SRV resolver (locate SIP servers) | `src/adapters/sip_srv_resolver.py` | Haiku | Load balance across 3+ servers |
| Failover controller (retry logic, backoff) | `src/adapters/sip_failover.py` | Sonnet | **SUPPORT Session 4:** Improve upstream SIP proxy |
| State sync across servers (Redis) | `src/adapters/sip_state_sync.py` | Haiku | Call context replication |
| **IDLE:** Session 6 Talent routing hints, Session 5 cost tracking per adapter |

---

## Phase 7: Production Hardening (1000 concurrent calls)
| Task | File | Model | Coordination |
|------|------|-------|--------------|
| Connection pooling (persistent TCP/TLS) | `src/adapters/sip_conn_pool.py` | Sonnet | **PRIORITY:** Unblock Phase 8 |
| Circuit breaker (degrade gracefully on overload) | `src/adapters/sip_circuit_breaker.py` | Haiku | Prevent cascade failures |
| Resource monitoring & thresholds | `src/adapters/sip_metrics.py` | Haiku | Prometheus + IF.witness |
| Chaos test: 1000 concurrent, kill 10% | `tests/chaos/sip_adapter_failure.py` | Haiku | **IDLE:** Session 4 inherit chaos patterns |

---

## Phase 8: Monitoring Integration (IF.witness SIP servers)
| Task | File | Model | Coordination |
|------|------|-------|--------------|
| SIP server health check (REGISTER, OPTIONS) | `src/adapters/sip_health_check.py` | Haiku | **SUPPORT Session 5:** Dashboard feed |
| Witness event stream (all SIP events) | `src/adapters/sip_witness_events.py` | Haiku | Non-blocking async logging |
| Server status aggregator (all regions) | `src/adapters/sip_status_aggregator.py` | Sonnet | Unblock Phase 9 routing decisions |
| **IDLE:** Session 1 stream health mirror, Session 3 H.323 gateway sync |

---

## Phase 9: AI-Powered Routing (intelligent server selection)
| Task | File | Model | Coordination |
|------|------|-------|--------------|
| Load predictor (ML: forecast server capacity) | `src/adapters/sip_load_predictor.py` | Sonnet | **Unblock Session 6:** Smart routing |
| Server selector (latency + load + cost) | `src/adapters/sip_server_selector.py` | Sonnet | SUPPORT Session 4 routing hints |
| A/B test: Manual vs AI selection | `tests/routing/sip_adapter_routing.py` | Haiku | Success rate baseline, expert feedback |
| **IDLE:** Session 2 WebRTC mesh optimize, Session 5 cost delta analysis |

---

## Phase 10: Full Autonomy (auto-provision, auto-scale)
| Task | File | Model | Coordination |
|------|------|-------|--------------|
| SIP server provisioning (Terraform/Ansible) | `infrastructure/sip_provisioner.py` | Sonnet | **Unblock Session 6 autonomy gate** |
| Autoscaler (spawn/terminate on threshold) | `src/adapters/sip_autoscaler.py` | Sonnet | Integrate with cloud API (AWS/GCP) |
| Zero-touch deployment (bootstrap + register) | `src/adapters/sip_bootstrap.py` | Haiku | Self-joining adapter mesh |
| Production autonomy test (month-long simulation) | `tests/autonomy/sip_full_lifecycle.py` | Sonnet | **IDLE:** Session 4 inherit autonomy patterns |

---

**Timeline:** P4-5 (14h) + P6-7 (18h) + P8-9 (16h) + P10 (12h) = 60h @ $95 | Unblocks: Session 6 full autonomy + Session 4 SIP scaling
