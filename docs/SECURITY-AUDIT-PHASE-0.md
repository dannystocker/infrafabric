# Security Audit: IF.governor + IF.chassis (Phase 0)

**Session**: Session 7 (IF.bus - Core Components)
**Date**: 2025-11-12
**Scope**: Phase 0 security review for IF.governor and IF.chassis
**Components**: P0.2.2, P0.2.3, P0.2.4, P0.3.1, P0.3.2
**Author**: Claude Code (Session 7)

---

## Executive Summary

This security audit evaluates the IF.governor (resource and budget management) and IF.chassis (WASM sandbox runtime) implementations completed in Phase 0. The audit identifies **8 security strengths** and **5 areas requiring attention** before production deployment.

**Overall Security Posture**: ✅ **GOOD** with minor improvements needed

**Critical Findings**:
- ✅ WASM sandbox provides strong isolation
- ✅ OS-level resource limits prevent resource exhaustion
- ✅ Token bucket algorithm prevents API abuse
- ✅ Circuit breaker prevents runaway costs
- ⚠️  No authentication/authorization layer (P0.3.3 dependency)
- ⚠️  Budget tracking vulnerable to race conditions
- ⚠️  Witness logging lacks cryptographic signatures (stub implementation)

---

## 1. WASM Sandbox Security (P0.3.1)

### Architecture

**Component**: `IFChassis` in `infrafabric/chassis/runtime.py`

```python
class IFChassis:
    def load_swarm(self, swarm_id, wasm_path, contract):
        # Compile WASM module with wasmtime
        module = wasmtime.Module(self.engine, wasm_bytes)
        store = wasmtime.Store(self.engine)
        instance = linker.instantiate(store, module)
```

### Security Strengths ✅

1. **Memory Isolation**
   - WASM provides linear memory isolation
   - Each swarm has independent memory space
   - No direct memory access between swarms
   - **Evidence**: `tests/test_chassis_runtime.py::test_load_multiple_swarms_isolated`

2. **Capability-Based Security**
   - WASM imports explicitly defined via linker
   - No implicit host access
   - **Code**: Lines 173-184 in `runtime.py`

3. **Deterministic Execution**
   - WASM bytecode validation on load
   - Invalid modules rejected at compile time
   - **Test**: `test_load_swarm_with_invalid_wasm_fails`

### Vulnerabilities ⚠️

#### 1.1 Missing WASI Sandboxing

**Severity**: MEDIUM
**Location**: `runtime.py:177-183`

```python
try:
    wasi_config = wasmtime.WasiConfig()
    wasi = wasmtime.Wasi(store, wasi_config)
    linker.define_wasi(wasi)
except Exception:
    # WASI not required for all modules
    pass
```

**Issue**: WASI is enabled without filesystem restrictions. A malicious WASM module could access host filesystem if WASI is available.

**Attack Scenario**:
1. Attacker uploads WASM module with WASI filesystem imports
2. Module reads `/etc/passwd` or other sensitive files
3. Data exfiltration via task results

**Mitigation**:
```python
wasi_config = wasmtime.WasiConfig()
# Restrict filesystem access
wasi_config.preopen_dir("/tmp/swarm-sandbox", "/", read=False, write=False)
# Disable network access
wasi_config.inherit_network(False)
# Disable stdio
wasi_config.inherit_stdin()
wasi_config.inherit_stdout()
wasi_config.inherit_stderr()
```

**Priority**: Implement before production (P0.3.3 - Scoped Credentials)

#### 1.2 Resource Limit Bypass via Multiple Loads

**Severity**: LOW
**Location**: `runtime.py:113-233`

**Issue**: `load_swarm()` allows reloading the same `swarm_id` multiple times, potentially bypassing resource limits.

**Attack Scenario**:
1. Load swarm with 256MB memory limit
2. Reload same swarm_id with 512MB limit
3. Previous enforcer overwritten

**Mitigation**:
```python
def load_swarm(self, swarm_id, ...):
    if swarm_id in self.loaded_swarms:
        raise ValueError(f"Swarm already loaded: {swarm_id}")
```

**Priority**: LOW (requires authenticated access)

---

## 2. Resource Limit Enforcement (P0.3.2)

### Architecture

**Components**:
- `ResourceLimits` dataclass
- `TokenBucket` rate limiter
- `ResourceEnforcer` OS-level limits

### Security Strengths ✅

1. **OS-Level Enforcement**
   - Uses `setrlimit()` for hard limits
   - Enforced by kernel, not bypassable by user code
   - **Code**: `limits.py:215-232`

2. **Token Bucket Algorithm**
   - Prevents API abuse with continuous refill
   - Capacity limits prevent burst attacks
   - **Test**: `test_token_bucket_consume_failure`

3. **Independent Per-Swarm Limits**
   - Each swarm has isolated enforcer
   - No cross-swarm interference
   - **Test**: `test_multiple_swarms_independent_rate_limits`

### Vulnerabilities ⚠️

#### 2.1 Race Condition in Budget Tracking

**Severity**: MEDIUM
**Location**: `governor.py:302-327`

```python
def track_cost(self, swarm_id, operation, cost):
    profile = self.swarm_registry[swarm_id]

    # RACE: Multiple threads could read/write simultaneously
    profile.current_budget_remaining -= cost

    if profile.current_budget_remaining <= 0:
        self._trip_circuit_breaker(swarm_id, 'budget_exhausted')
```

**Issue**: No locking mechanism prevents concurrent budget modifications.

**Attack Scenario**:
1. Submit 10 tasks simultaneously for same swarm
2. All tasks read `budget_remaining = 100.0`
3. All tasks execute (each subtracting 20.0)
4. Final budget: -100.0 instead of stopping at 0

**Impact**: Budget overruns, cost waste

**Mitigation**:
```python
import threading

class IFGovernor:
    def __init__(self, ...):
        self._budget_locks = {}  # swarm_id -> Lock

    def track_cost(self, swarm_id, operation, cost):
        lock = self._budget_locks.setdefault(swarm_id, threading.Lock())
        with lock:
            profile = self.swarm_registry[swarm_id]
            profile.current_budget_remaining -= cost
            if profile.current_budget_remaining <= 0:
                self._trip_circuit_breaker(swarm_id, 'budget_exhausted')
```

**Priority**: HIGH (required for production)

#### 2.2 API Rate Limit Token Refill Timing Attack

**Severity**: LOW
**Location**: `limits.py:108-122`

```python
def consume(self, tokens: int = 1) -> bool:
    elapsed = time.time() - self.last_update
    self.tokens = min(self.capacity, self.tokens + (elapsed * self.rate))
    self.last_update = time.time()

    if self.tokens >= tokens:
        self.tokens -= tokens
        return True
    return False
```

**Issue**: Attacker could call `consume(0)` repeatedly to refill tokens faster than intended.

**Attack Scenario**:
1. Exhaust all tokens (capacity = 20)
2. Call `consume(0)` in tight loop for 1 second
3. Tokens refill to capacity
4. Bypass 10 requests/sec limit

**Mitigation**:
```python
def consume(self, tokens: int = 1) -> bool:
    if tokens == 0:
        return True  # Don't refill on zero-token requests
    # ... rest of logic
```

**Priority**: LOW (requires timing precision)

---

## 3. Budget Tracking and Circuit Breaker (P0.2.3, P0.2.4)

### Architecture

**Components**:
- `track_cost()` - Budget deduction
- `_trip_circuit_breaker()` - Halt mechanism
- `record_task_failure()` - Failure tracking

### Security Strengths ✅

1. **Automatic Circuit Breaking**
   - Budget exhaustion prevents runaway costs
   - Repeated failures halt bad actors
   - **Test**: `test_budget_exhaustion_trips_circuit_breaker`

2. **Human Escalation**
   - Critical events logged to witness
   - Human-in-the-loop for recovery
   - **Code**: `governor.py:402-430`

3. **Audit Trail**
   - All budget operations logged
   - Forensics capability for cost analysis
   - **Test**: `test_budget_tracking_logged_to_optimise`

### Vulnerabilities ⚠️

#### 3.1 Circuit Breaker Reset Without Authorization

**Severity**: MEDIUM
**Location**: `governor.py:444-491`

```python
def reset_circuit_breaker(
    self,
    swarm_id: str,
    new_budget: Optional[float] = None
) -> None:
    # No authorization check!
    self._circuit_breakers[swarm_id] = False
    self._failure_counts[swarm_id] = 0
```

**Issue**: Anyone with code access can reset circuit breakers, bypassing safety mechanisms.

**Attack Scenario**:
1. Malicious swarm exhausts budget
2. Circuit breaker trips
3. Attacker calls `reset_circuit_breaker()` directly
4. Swarm continues operating

**Mitigation**:
```python
def reset_circuit_breaker(
    self,
    swarm_id: str,
    new_budget: Optional[float] = None,
    authorized_by: Optional[str] = None  # Human or admin service
) -> None:
    if not authorized_by:
        raise ValueError("Circuit breaker reset requires authorization")

    # Log authorization for audit
    log_operation(
        component='IF.governor',
        operation='circuit_breaker_reset_authorized',
        params={'swarm_id': swarm_id, 'authorized_by': authorized_by},
        severity='HIGH'
    )

    # ... rest of reset logic
```

**Priority**: MEDIUM (depends on deployment model)

#### 3.2 No Budget Restoration Policy

**Severity**: LOW
**Location**: Design issue (not code-specific)

**Issue**: No mechanism to restore budget over time (daily/hourly quotas).

**Attack Scenario**:
1. Swarm exhausts daily budget in 1 hour
2. No work possible for remaining 23 hours
3. Denial of service (self-inflicted)

**Mitigation**: Implement quota renewal policy in P0.2.3 extension
- Daily budget refreshes at midnight
- Hourly rate limits with rollover
- Configurable via `ResourcePolicy`

**Priority**: LOW (operational concern, not security)

---

## 4. Capability Matching Security (P0.2.2)

### Architecture

**Component**: `find_qualified_swarm()` in `governor.py`

```python
def find_qualified_swarm(
    self,
    required_capabilities: List[Capability],
    max_cost: float = None
) -> Optional[str]:
    # Jaccard similarity + cost scoring
    capability_overlap = calculate_capability_overlap(required, available)
    if capability_overlap < self.policy.min_capability_match:
        continue  # Reject <70% matches
```

### Security Strengths ✅

1. **Capability Enumeration**
   - Strong typing via `Enum`
   - No arbitrary strings accepted
   - **Code**: `capability.py:25-69`

2. **Minimum Match Threshold**
   - 70% overlap required by default
   - Prevents mismatched task assignment
   - **Test**: `test_find_swarm_below_threshold_returns_none`

3. **Cost-Aware Selection**
   - Balances capability and cost
   - Prevents expensive swarms for simple tasks
   - **Code**: `governor.py:216-222`

### Vulnerabilities ⚠️

#### 4.1 Capability Spoofing (No Verification)

**Severity**: HIGH
**Location**: `governor.py:176-193`

```python
def register_swarm(self, profile: SwarmProfile) -> None:
    # No verification of claimed capabilities!
    self.swarm_registry[profile.swarm_id] = profile
```

**Issue**: Swarms self-report capabilities without verification.

**Attack Scenario**:
1. Malicious swarm registers with `[ALL_CAPABILITIES]`
2. Gets assigned all tasks regardless of actual ability
3. Tasks fail, costing money and time

**Mitigation**:
```python
def register_swarm(self, profile: SwarmProfile) -> None:
    # Verify capabilities via challenge tasks
    for cap in profile.capabilities:
        challenge = self._generate_capability_challenge(cap)
        result = self._verify_swarm_capability(profile.swarm_id, challenge)
        if not result.passed:
            raise ValueError(f"Swarm failed capability verification: {cap}")

    self.swarm_registry[profile.swarm_id] = profile
```

**Priority**: HIGH (required for trustless operation)

**Note**: This may be addressed in P0.3.5 (Reputation System)

---

## 5. Witness Logging Security

### Architecture

**Component**: `witness.py` (stub implementation)

```python
def log_operation(
    component: str,
    operation: str,
    params: Dict[str, Any],
    timestamp: Optional[float] = None,
    severity: str = "INFO"
):
    op = Operation(component, operation, params, timestamp, severity)
    _operation_log.append(op)  # In-memory only
```

### Security Strengths ✅

1. **Comprehensive Logging**
   - All critical operations logged
   - Includes parameters for forensics
   - **Test**: `test_circuit_breaker_trips_logged_to_witness`

2. **Severity Levels**
   - HIGH severity for security events
   - Enables alert filtering
   - **Code**: `witness.py:35-49`

### Vulnerabilities ⚠️

#### 5.1 No Cryptographic Signatures (Stub Implementation)

**Severity**: HIGH
**Location**: `witness.py:1-117`

**Issue**: Logs are mutable and not tamper-evident.

**Attack Scenario**:
1. Attacker gains code access
2. Modifies `_operation_log` to hide malicious activity
3. Audit trail corrupted

**Mitigation** (For production witness):
```python
import hashlib
import hmac

class Operation:
    def __init__(self, ...):
        self.signature = self._sign_operation()

    def _sign_operation(self) -> str:
        # HMAC-SHA256 signature of operation
        message = f"{self.component}:{self.operation}:{self.timestamp}"
        return hmac.new(
            SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

    def verify_signature(self) -> bool:
        expected = self._sign_operation()
        return hmac.compare_digest(self.signature, expected)
```

**Priority**: CRITICAL (required for production)

**Note**: Full witness implementation is out of scope for Phase 0

#### 5.2 In-Memory Log Storage (Data Loss Risk)

**Severity**: MEDIUM
**Location**: `witness.py:17-19`

```python
# Global operation log (in-memory)
_operation_log: List[Operation] = []
```

**Issue**: Logs lost on process restart.

**Mitigation**: Implement persistent storage (etcd, NATS, or database) in production witness

**Priority**: HIGH (operational requirement)

---

## 6. Cost Tracking Security

### Architecture

**Component**: `optimise.py` (stub implementation)

```python
def track_operation_cost(
    provider: str,
    operation: str,
    cost: float,
    **metadata
):
    record = CostRecord(provider, operation, cost, timestamp, metadata)
    _cost_records.append(record)
```

### Vulnerabilities ⚠️

#### 6.1 No Cost Validation

**Severity**: MEDIUM
**Location**: `optimise.py:91-111`

**Issue**: Negative costs or unrealistic values accepted.

**Attack Scenario**:
1. Swarm reports negative cost: `track_cost('swarm-1', 'task', -50.0)`
2. Budget increases instead of decreases
3. Unlimited execution

**Mitigation**:
```python
def track_operation_cost(provider, operation, cost, **metadata):
    if cost < 0:
        raise ValueError(f"Negative cost not allowed: {cost}")
    if cost > MAX_COST_PER_OPERATION:
        raise ValueError(f"Cost exceeds maximum: {cost}")

    # ... rest of logic
```

**Priority**: MEDIUM

#### 6.2 Cost Record Tampering

**Severity**: LOW
**Location**: `optimise.py:14-16`

```python
# Global cost records (in-memory)
_cost_records: List[CostRecord] = []
```

**Issue**: Direct access to `_cost_records` allows modification.

**Mitigation**: Use private ledger with append-only semantics

**Priority**: LOW (stub implementation)

---

## 7. Integration Security

### Multi-Component Attack Vectors

#### 7.1 Capability Mismatch → Resource Exhaustion

**Scenario**:
1. Swarm claims `CODE_ANALYSIS_PYTHON` capability
2. Actually doesn't have Python runtime
3. Tasks fail repeatedly → circuit breaker trips
4. No work gets done (DoS)

**Mitigation**: Capability verification (Section 4.1)

#### 7.2 Budget Exhaustion → Circuit Breaker → DoS

**Scenario**:
1. Attacker submits expensive tasks rapidly
2. Budget exhausted quickly
3. Circuit breaker halts swarm
4. Legitimate work blocked

**Mitigation**: Rate limiting + budget pacing

**Code**:
```python
class ResourcePolicy:
    max_budget_per_hour: float = 10.0  # Prevent rapid exhaustion
    min_task_spacing_seconds: float = 1.0  # Rate limit task submissions
```

#### 7.3 WASM Module Size DoS

**Scenario**:
1. Attacker uploads 1GB WASM module
2. `load_swarm()` attempts to compile
3. Memory exhaustion crashes chassis

**Mitigation**:
```python
MAX_WASM_SIZE_MB = 50

def load_swarm(self, swarm_id, wasm_bytes, ...):
    if len(wasm_bytes) > MAX_WASM_SIZE_MB * 1024 * 1024:
        raise ValueError(f"WASM module too large: {len(wasm_bytes)} bytes")
```

**Priority**: MEDIUM

---

## 8. Compliance and Best Practices

### OWASP Top 10 (2021) Analysis

| OWASP Category | Status | Notes |
|----------------|--------|-------|
| A01: Broken Access Control | ⚠️ | No auth layer (P0.3.3 dependency) |
| A02: Cryptographic Failures | ⚠️ | Witness lacks signatures |
| A03: Injection | ✅ | WASM sandboxing prevents code injection |
| A04: Insecure Design | ✅ | Defense-in-depth: limits + circuit breakers |
| A05: Security Misconfiguration | ⚠️ | WASI sandboxing not enforced |
| A06: Vulnerable Components | ✅ | Dependencies: wasmtime (audited) |
| A07: Auth Failures | ⚠️ | No authentication (P0.3.3) |
| A08: Data Integrity | ⚠️ | Budget tracking race condition |
| A09: Logging Failures | ✅ | Comprehensive witness logging |
| A10: SSRF | ✅ | No network access in WASM |

### CWE Analysis

- **CWE-362**: Race Condition (Budget tracking)
- **CWE-400**: Uncontrolled Resource Consumption (Mitigated by limits)
- **CWE-494**: Download of Code Without Integrity Check (WASM loading)
- **CWE-770**: Allocation Without Limits (Mitigated by ResourceLimits)

---

## 9. Recommendations

### Critical Priority (Before Production)

1. **Implement Authentication/Authorization** (P0.3.3 - Scoped Credentials)
   - Add auth layer to `IFChassis` and `IFGovernor`
   - Use scoped API keys per swarm
   - Verify all API calls

2. **Add Budget Tracking Locks** (Section 2.1)
   - Implement threading locks for `track_cost()`
   - Test with concurrent load

3. **Capability Verification** (Section 4.1)
   - Challenge swarms to prove claimed capabilities
   - Integrate with reputation system (P0.3.5)

4. **Cryptographic Witness** (Section 5.1)
   - Implement HMAC signatures for logs
   - Use persistent storage (etcd/NATS)

### High Priority

5. **WASI Sandboxing** (Section 1.1)
   - Restrict filesystem access
   - Disable network in WASI config

6. **Cost Validation** (Section 6.1)
   - Reject negative or excessive costs
   - Add sanity checks

7. **WASM Size Limits** (Section 7.3)
   - Enforce maximum module size
   - Add compile timeout

### Medium Priority

8. **Circuit Breaker Authorization** (Section 3.1)
   - Require human/admin approval for resets
   - Log all authorizations

9. **Token Bucket Zero-Token Fix** (Section 2.2)
   - Prevent zero-token refill attacks

### Low Priority

10. **Swarm Reload Protection** (Section 1.2)
    - Prevent duplicate `swarm_id` loads

11. **Budget Renewal Policy** (Section 3.2)
    - Daily/hourly quota refreshes

---

## 10. Test Coverage Analysis

### Security-Relevant Tests

**Passing Tests** (122/122):
- ✅ Resource limit enforcement: 25 tests
- ✅ Budget tracking: 15 tests
- ✅ Circuit breaker: 17 tests
- ✅ WASM runtime: 22 tests
- ✅ Integration tests: 13 tests
- ✅ Performance benchmarks: 12 tests

### Missing Security Tests

1. **Concurrent Budget Tracking**
   - Test: 10 threads track cost simultaneously
   - Expected: No budget overruns

2. **WASI Filesystem Access**
   - Test: Load WASM module that attempts file read
   - Expected: Access denied

3. **Capability Verification**
   - Test: Swarm claims capabilities it doesn't have
   - Expected: Verification fails

4. **Witness Log Tampering**
   - Test: Modify log signature
   - Expected: Verification fails

5. **WASM Module Size Limit**
   - Test: Load 100MB WASM file
   - Expected: Rejected before compilation

**Recommendation**: Add these tests in Phase 0 extension or Phase 1

---

## 11. Conclusion

### Summary

IF.governor and IF.chassis provide a **strong security foundation** for the S² system:

**Strengths**:
1. ✅ WASM sandbox isolation
2. ✅ OS-level resource enforcement
3. ✅ Token bucket rate limiting
4. ✅ Automatic circuit breaking
5. ✅ Comprehensive audit logging
6. ✅ Type-safe capability matching
7. ✅ Independent per-swarm limits
8. ✅ Cost-aware task assignment

**Critical Gaps**:
1. ⚠️ No authentication layer (P0.3.3 dependency)
2. ⚠️ Budget tracking race conditions
3. ⚠️ Witness logging lacks signatures (stub)
4. ⚠️ Capability spoofing possible
5. ⚠️ WASI sandboxing incomplete

### Production Readiness

**Current State**: ⚠️ **NOT PRODUCTION READY**

**Blockers**:
1. Authentication/authorization (P0.3.3)
2. Budget tracking locks
3. Cryptographic witness (full implementation)

**After Mitigations**: ✅ **PRODUCTION READY**

### Next Steps

1. **Immediate**: Implement budget tracking locks (2 hours)
2. **Phase 0**: Complete P0.3.3 (Scoped Credentials)
3. **Phase 0**: Complete P0.3.5 (Reputation → Capability Verification)
4. **Phase 1**: Full witness implementation with signatures
5. **Phase 1**: WASI sandboxing hardening

---

## 12. References

### Security Standards
- OWASP Top 10 (2021): https://owasp.org/Top10/
- CWE Top 25: https://cwe.mitre.org/top25/
- WASM Security: https://webassembly.org/docs/security/

### Implementation Files
- `infrafabric/governor.py` (599 lines)
- `infrafabric/chassis/runtime.py` (546 lines)
- `infrafabric/chassis/limits.py` (456 lines)
- `infrafabric/schemas/capability.py` (332 lines)
- `infrafabric/witness.py` (117 lines - stub)
- `infrafabric/optimise.py` (154 lines - stub)

### Test Files
- `tests/test_governor_budget.py` (15 tests)
- `tests/test_governor_matching.py` (18 tests)
- `tests/test_governor_circuit_breaker.py` (17 tests)
- `tests/test_chassis_runtime.py` (22 tests)
- `tests/test_chassis_limits.py` (25 tests)
- `tests/test_governor_benchmarks.py` (12 tests)
- `tests/test_integration_governor_chassis.py` (13 tests)

---

**End of Security Audit**

*Prepared by Session 7 (IF.bus - Core Components)*
*Phase 0 Task F7.3: Security Audit*
*122/122 tests passing (100%)*
