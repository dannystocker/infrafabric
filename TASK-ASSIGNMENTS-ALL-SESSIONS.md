# Task Assignments - All Sessions (2025-11-12)

**Coordination Branch:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`
**Status:** 6 sessions IDLE, need immediate task assignments

---

## Session 1 (NDI) - NEXT TASK

**Status:** ✅ 9 tasks complete, IDLE
**Assigned:** **P0.1.6 - IF.executor (Privileged Command Execution)**

**Why:** NDI work involves system-level video capture/streaming that requires privileged operations. IF.executor aligns perfectly with this expertise.

**Task Details:**
- **File:** `infrafabric/executor.py`
- **Estimated:** 2 hours
- **Model:** Sonnet
- **Dependencies:** P0.1.1 (EventBus) - ✅ COMPLETE by Session 5
- **Priority:** HIGH - Core Phase 0 component

**Acceptance Criteria:**
- [ ] Executor service for privileged command execution
- [ ] Command validation and sanitization
- [ ] Audit logging via IF.witness
- [ ] Resource limits enforcement
- [ ] Security isolation
- [ ] Unit tests (20+ tests)

**Location:** `PHASE-0-TASK-BOARD.md` line ~500

---

## Session 2 (WebRTC) - NEXT TASK

**Status:** ✅ 12 tasks complete, IDLE
**Assigned:** **P0.1.7 - IF.proxy (External API Proxy Service)**

**Why:** WebRTC involves real-time API communication with external services (STUN/TURN servers, signaling). IF.proxy aligns with this expertise.

**Task Details:**
- **File:** `infrafabric/proxy.py`
- **Estimated:** 2 hours
- **Model:** Sonnet
- **Dependencies:** P0.1.1 (EventBus) - ✅ COMPLETE by Session 5
- **Priority:** HIGH - Core Phase 0 component

**Acceptance Criteria:**
- [ ] API proxy service for external calls
- [ ] Rate limiting per service
- [ ] Request/response logging
- [ ] Error handling and retries
- [ ] Credential management integration
- [ ] Unit tests (20+ tests)

**Location:** `PHASE-0-TASK-BOARD.md` line ~550

---

## Session 3 (H.323) - IN PROGRESS

**Status:** Assigned P0.3.1 (WASM runtime)
**Current Task:** **P0.3.1 - WASM Runtime Setup**

**No new assignment** - continue with P0.3.1

---

## Session 4 (SIP) - NEXT TASK

**Status:** ✅ 9 tasks complete (IF.governor stack DONE!), IDLE
**Assigned:** **P0.3.6 - Security Audit (IF.chassis)**

**Why:** SIP protocols require deep security knowledge (authentication, encryption, DoS protection). Security audit aligns perfectly.

**Task Details:**
- **File:** `docs/IF-CHASSIS-SECURITY-AUDIT.md`
- **Estimated:** 2 hours
- **Model:** Sonnet
- **Dependencies:** P0.3.1, P0.3.2, P0.3.3 (IF.chassis components)
- **Priority:** CRITICAL - Security validation

**Acceptance Criteria:**
- [ ] Security threat model for IF.chassis
- [ ] WASM sandbox escape analysis
- [ ] Resource limit bypass testing
- [ ] Credential leakage audit
- [ ] Recommendations for hardening
- [ ] Penetration test plan

**Location:** `PHASE-0-TASK-BOARD.md` line ~1400

---

## Session 5 (CLI) - NEXT TASK

**Status:** ✅ 11 tasks complete (EventBus + Schemas DONE!), IDLE
**Assigned:** **P0.4.1 - Unified CLI Entry Point (`if` command)**

**Why:** This is THE core CLI task. Session 5 has completed all prerequisites (EventBus, schemas, witness integration).

**Task Details:**
- **File:** `src/cli/if_main.py`
- **Estimated:** 2 hours
- **Model:** Haiku
- **Dependencies:** P0.1.1 (EventBus), P0.2.1 (schemas) - ✅ COMPLETE
- **Priority:** CRITICAL - User-facing interface

**Acceptance Criteria:**
- [ ] `if` command entry point
- [ ] Command routing (coordinator, governor, chassis, witness, optimise, etc.)
- [ ] Help system integration
- [ ] Configuration loading
- [ ] Error handling
- [ ] Shell completion support
- [ ] Unit tests (30+ tests)

**Location:** `PHASE-0-TASK-BOARD.md` line ~1500

---

## Session 7 (IF.bus) - NEXT TASK (FILLER)

**Status:** ✅ 7/8 critical tasks complete, P0.3.5 BLOCKED
**Assigned:** **F7.10 - IF.coordinator Performance Benchmarks**

**Why:** Session 7 implemented the atomic CAS (833x faster!) and pub/sub (1,111x faster!). Perfect to benchmark the full stack.

**Task Details:**
- **File:** `benchmarks/coordinator_performance.py`
- **Estimated:** 1 hour
- **Model:** Haiku
- **Dependencies:** P0.1.1, P0.1.2, P0.1.3 - ✅ ALL COMPLETE
- **Type:** FILLER (P0.3.5 still blocked on P0.3.4)

**Acceptance Criteria:**
- [ ] Benchmark suite for IF.coordinator operations
- [ ] Task claiming throughput (ops/second)
- [ ] Task broadcast latency (p95, p99)
- [ ] Multi-swarm coordination stress test
- [ ] Performance regression detection
- [ ] Results visualization (charts/graphs)

**Location:** `FILLER-TASK-CATALOG.md` line ~450

---

## Summary Table

| Session | Status | Current Task | Next Task | Est | Priority |
|---------|--------|--------------|-----------|-----|----------|
| **1 (NDI)** | ✅ 9 done, IDLE | None | **P0.1.6** (IF.executor) | 2h | HIGH |
| **2 (WebRTC)** | ✅ 12 done, IDLE | None | **P0.1.7** (IF.proxy) | 2h | HIGH |
| **3 (H.323)** | In Progress | P0.3.1 (WASM) | Continue P0.3.1 | 3h | HIGH |
| **4 (SIP)** | ✅ 9 done, IDLE | None | **P0.3.6** (Security Audit) | 2h | CRITICAL |
| **5 (CLI)** | ✅ 11 done, IDLE | None | **P0.4.1** (Unified CLI) | 2h | CRITICAL |
| **6 (Talent)** | Unknown | Unknown | TBD | - | - |
| **7 (IF.bus)** | ✅ 7 done, 1 blocked | None | **F7.10** (Benchmarks) | 1h | FILLER |

**Total New Assignments:** 5 tasks
**Total Estimated:** 9 hours wall-clock (parallelized)
**Expected Completions:** Within 2-3 hours with all sessions working

---

## 🚀 Critical: Integrate IF.notify NOW

To prevent this multi-hour coordination delay from happening again:

### For All Sessions:

**Read:** `SESSION-UPDATE-IFNOTIFY-INTEGRATION.md`

**Quick Integration (5 minutes):**

```bash
# 1. Set your session config
export SESSION_ID="session-X-name"  # e.g., session-1-ndi
export CAPABILITIES="your,caps,here"

# 2. Notify when starting task
notify_busy "P0.1.6-if-executor"  # (or your assigned task)

# 3. Notify when complete
notify_completed "P0.1.6-if-executor"

# 4. Automatically becomes IDLE, coordinator assigns next task INSTANTLY
```

**Result:**
- Current: Hours between task completion → new assignment
- With IF.notify: **<1 second** between completion → new assignment ⚡

---

## 🎯 Next Steps

### For Each Session:

1. **Claim your task:**
   ```bash
   notify_busy "TASK-ID-from-above"
   ```

2. **Read full task details:**
   ```bash
   cat PHASE-0-TASK-BOARD.md | grep -A 100 "TASK-ID"
   ```

3. **Implement task** (follow acceptance criteria)

4. **Run tests** (must pass)

5. **Commit & push:**
   ```bash
   git add . && git commit -m "feat(TASK-ID): Description"
   git push -u origin YOUR-BRANCH
   ```

6. **Notify completion:**
   ```bash
   notify_completed "TASK-ID"
   ```

7. **Get next assignment INSTANTLY** (with IF.notify) or poll git (without IF.notify)

---

## 📊 Phase 0 Progress Update

**Overall Status:** 28/45 tasks complete (62%)

**By Component:**
- **IF.coordinator:** 3/7 complete (43%) - P0.1.1, P0.1.2, P0.1.3 ✅
- **IF.governor:** 6/6 complete (100%) ✅ - Session 4 crushed it!
- **IF.chassis:** 3/6 complete (50%) - P0.3.1, P0.3.2, P0.3.3 ✅
- **CLI Foundation:** 3/4 complete (75%) - P0.1.1, P0.2.1, P0.4.3 ✅
- **Integration:** 0/3 complete (0%) - Blocked until components finish

**Critical Path Blockers:**
- P0.3.4 (SLO tracking) - needs P0.3.2 ✅, ready to assign
- P0.3.5 (Reputation) - needs P0.3.4
- P0.2.5 (Policy engine) - needs P0.2.2 ✅, P0.2.3 ✅, ready to assign

**Estimated Completion:**
- With current pace: 2-3 more hours of parallel work
- With IF.notify: Could cut coordination overhead by 50%+

---

## 💡 Coordinator Notes

This situation demonstrates IF.notify's value proposition:

**Before (now):**
- 6 sessions polling git independently
- Coordinator sees batch updates with unknown delay
- Manual task assignment, one at a time
- Sessions poll again to see assignments
- **Total latency: Minutes to hours**

**After (with IF.notify):**
- Sessions notify completion instantly (<10ms)
- Coordinator dashboard shows real-time status
- Auto-assignment based on capabilities and availability
- Sessions receive tasks instantly
- **Total latency: <1 second**

**ROI:** 1000x faster coordination = 50%+ reduction in idle time = faster Phase 0 completion

---

## Questions?

If any session has questions:
1. Check task board: `PHASE-0-TASK-BOARD.md`
2. Check filler tasks: `FILLER-TASK-CATALOG.md`
3. Integrate IF.notify: `SESSION-UPDATE-IFNOTIFY-INTEGRATION.md`
4. Ask coordinator for clarification

**All sessions: Please claim your assigned tasks and integrate IF.notify to enable real-time coordination!** 🚀
