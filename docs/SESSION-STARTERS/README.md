# InfraFabric Parallel Session Starters

**Purpose:** Launch multiple independent Claude Code sessions to implement real-time communication in parallel

**Total Budget:** $102-122 (5 sessions)
**Calendar Time:** 4-6 weeks (with parallelization)
**Sequential Time:** 10+ weeks (if done serially)

---

## Session Execution Strategy

### Phase 1: Launch 4 Sessions Simultaneously (Week 1)

Start these **all at once** on Day 1:

| Session | File | Agent | Budget | Hours | Dependencies |
|---------|------|-------|--------|-------|--------------|
| **Session 1** | [session-1-ndi-witness.md](session-1-ndi-witness.md) | Claude Sonnet 4.5 | $20 | 14 | None ✅ |
| **Session 2** | [session-2-webrtc-swarm.md](session-2-webrtc-swarm.md) | GPT-5 | $12 | 12 | None ✅ |
| **Session 3** | [session-3-h323-guard.md](session-3-h323-guard.md) | Gemini 2.5 Pro | $30 | 24 | None ✅ |
| **Session CLI** | [session-parallel-cli-witness.md](session-parallel-cli-witness.md) | Claude/GPT | $15-20 | 12-16 | None ✅ |

**All 4 are independent!** They can run simultaneously.

### Phase 2: Launch Session 4 (Week 2-3)

Wait for Sessions 2 & 3 to complete, then start:

| Session | File | Agent | Budget | Hours | Dependencies |
|---------|------|-------|--------|-------|--------------|
| **Session 4** | [session-4-sip-escalate.md](session-4-sip-escalate.md) | Claude Sonnet 4.5 | $25 | 20 | Session 2 ✅<br>Session 3 ✅ |

**Dependency:** Requires interface contracts from Sessions 2 & 3

### Phase 3: Integration (Week 4-6)

Final session to tie everything together (not documented yet):

| Session | Description | Agent | Budget | Hours | Dependencies |
|---------|-------------|-------|--------|-------|--------------|
| **Session 5** | Integration + IF.TTT validation | Claude Sonnet 4.5 | $25 | 20 | All 1-4 ✅ |

---

## How to Start a Session

### Method 1: Copy-Paste (Recommended)

1. Open the session file (e.g., `session-1-ndi-witness.md`)
2. Find the "Copy-Paste This Into New Claude Code Session" block
3. Start a fresh Claude Code session (no prior context)
4. Paste the entire block into the new session
5. Claude will read context files, implement, test, and commit

### Method 2: Direct File Reference

If using Claude Code with file access:

```bash
# Start new Claude Code session, then say:
"Please implement the task described in docs/SESSION-STARTERS/session-1-ndi-witness.md"
```

---

## Session Completion Checklist

Each session must produce these artifacts before marking complete:

- ✅ **Code:** Implementation + tests passing
- ✅ **Documentation:** Markdown guide with examples
- ✅ **Interface Contract:** `docs/INTERFACES/workstream-N-*-contract.yaml`
- ✅ **IF.witness Log:** `logs/workstream-N-*-witness.jsonl`
- ✅ **Branch:** `claude/realtime-workstream-N-*` pushed to GitHub
- ✅ **Known Issues:** `docs/WORKSTREAM-N-ISSUES.md` (if any blockers)

---

## Dependency Graph

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Session 1  │  │  Session 2  │  │  Session 3  │  │ Session CLI │
│    (NDI)    │  │  (WebRTC)   │  │   (H.323)   │  │  (Witness)  │
│             │  │             │  │             │  │             │
│  No deps ✅ │  │  No deps ✅ │  │  No deps ✅ │  │  No deps ✅ │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                │
       │                └────────┬───────┘                │
       │                         ▼                        │
       │                ┌─────────────┐                   │
       │                │  Session 4  │                   │
       │                │    (SIP)    │                   │
       │                │             │                   │
       │                │ Depends on  │                   │
       │                │   2 + 3     │                   │
       │                └──────┬──────┘                   │
       │                       │                          │
       └───────────────────────┴──────────────────────────┘
                               ▼
                      ┌─────────────┐
                      │  Session 5  │
                      │(Integration)│
                      │             │
                      │ Depends on  │
                      │  All 1-4    │
                      └─────────────┘
```

**Critical Path:** Session 3 (H.323) → Session 4 (SIP) → Session 5 (Integration)

**Parallel Capacity:** 4 sessions can run simultaneously (1, 2, 3, CLI)

---

## Cost Breakdown (IF.optimise)

| Session | Protocol/Feature | Agent | Est. Cost | Est. Hours | $/Hour |
|---------|------------------|-------|-----------|------------|--------|
| 1 | NDI evidence streaming | Claude Sonnet 4.5 | $20 | 14 | $1.43 |
| 2 | WebRTC agent mesh | GPT-5 | $12 | 12 | $1.00 |
| 3 | H.323 Guardian council | Gemini 2.5 Pro | $30 | 24 | $1.25 |
| CLI | IF.witness + IF.optimise | Claude/GPT | $15-20 | 12-16 | $1.25 |
| 4 | SIP external experts | Claude Sonnet 4.5 | $25 | 20 | $1.25 |
| 5 | Integration + validation | Claude Sonnet 4.5 | $25 | 20 | $1.25 |
| **TOTAL** | **All workstreams** | **Mixed** | **$127-132** | **102-106** | **$1.24** |

**Optimization:** Using GPT-5 for boilerplate (WebRTC) saves ~$8 vs Claude

---

## Progress Tracking

Create a tracking file to monitor completion:

```yaml
# progress.yaml
sessions:
  session_1_ndi:
    status: "not_started"  # not_started | in_progress | completed
    branch: "claude/realtime-workstream-1-ndi"
    started: null
    completed: null
    cost_actual: null

  session_2_webrtc:
    status: "not_started"
    branch: "claude/realtime-workstream-2-webrtc"
    started: null
    completed: null
    cost_actual: null

  session_3_h323:
    status: "not_started"
    branch: "claude/realtime-workstream-3-h323"
    started: null
    completed: null
    cost_actual: null

  session_cli:
    status: "not_started"
    branch: "claude/cli-witness-optimise"
    started: null
    completed: null
    cost_actual: null

  session_4_sip:
    status: "not_started"
    branch: "claude/realtime-workstream-4-sip"
    started: null
    completed: null
    cost_actual: null
    blocked_by: [session_2_webrtc, session_3_h323]

  session_5_integration:
    status: "not_started"
    branch: "claude/realtime-integration"
    started: null
    completed: null
    cost_actual: null
    blocked_by: [session_1_ndi, session_2_webrtc, session_3_h323, session_4_sip]
```

---

## Quick Start Commands

```bash
# Phase 1: Launch all independent sessions (Day 1)
# Open 4 Claude Code sessions and paste from:
# - docs/SESSION-STARTERS/session-1-ndi-witness.md
# - docs/SESSION-STARTERS/session-2-webrtc-swarm.md
# - docs/SESSION-STARTERS/session-3-h323-guard.md
# - docs/SESSION-STARTERS/session-parallel-cli-witness.md

# Phase 2: Wait for Sessions 2 & 3, then launch Session 4
# Check if branches exist:
git fetch origin
git branch -r | grep "workstream-2-webrtc"  # Should exist
git branch -r | grep "workstream-3-h323"    # Should exist

# If both exist, launch Session 4:
# - docs/SESSION-STARTERS/session-4-sip-escalate.md

# Phase 3: Wait for all 1-4, then launch Session 5
# (Session 5 starter not yet created)
```

---

## Troubleshooting

### "Session stuck / not making progress"

- Check if context files exist (the session reads them first)
- Check if dependencies are met (Session 4 needs 2 & 3)
- Check if branch exists (avoid conflicts)

### "Interface contract missing"

Session N needs `docs/INTERFACES/workstream-{N-1}-*-contract.yaml` from previous session.

**Fix:** Ensure previous session committed their contract before handoff.

### "Tests failing"

Each session should have tests passing before marking complete.

**Fix:** Ask session to debug and fix tests before moving on.

### "Cost overrun"

Track actual vs estimated cost in `progress.yaml`.

**Fix:** Adjust budget for remaining sessions, or simplify scope.

---

## Philosophy Grounding Check

Before marking any session complete, verify:

1. **IF.ground:** Claims grounded in observable artifacts? ✓
2. **IF.witness:** Every operation logged with provenance? ✓
3. **IF.TTT:** Traceable, Transparent, Trustworthy? ✓
4. **IF.optimise:** Cost tracked and within budget? ✓
5. **Wu Lun:** Relationships correctly mapped? ✓

---

## Next Steps

1. **Review Session Files:** Read through each session starter
2. **Launch Phase 1:** Start Sessions 1, 2, 3, CLI simultaneously
3. **Monitor Progress:** Track in `progress.yaml`
4. **Launch Phase 2:** Start Session 4 after 2 & 3 complete
5. **Launch Phase 3:** Start Session 5 after all 1-4 complete

---

**Total Parallel Capacity:** 4 sessions (Day 1) + 1 session (Week 2) + 1 session (Week 4)

**Expected Completion:** 4-6 weeks calendar time (vs 10+ weeks sequential)

**Cost Efficiency:** $127-132 total (IF.optimise target: <$150)
