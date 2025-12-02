# Conversation Export Templates for LLM Handoffs

This document provides templates for exporting Open WebUI conversations in formats optimized for feeding to other LLMs (Claude, GPT, Gemini, etc.).

---

## Template 1: Minimal Context Handoff

**Use When:** Quick question/answer, no deep context needed

**Format:**
```markdown
# Quick Context from Previous Conversation

**Previous Discussion:** [1-2 sentence summary]

**Key Points:**
- Point 1
- Point 2
- Point 3

**Current Question:**
[Your new question here]
```

**Example:**
```markdown
# Quick Context from Previous Conversation

**Previous Discussion:** Deployed Redis L1/L2 cache architecture for InfraFabric, with auto-sync on session start.

**Key Points:**
- L1 = Redis Cloud (fast, ephemeral, 30MB)
- L2 = Proxmox Redis (slow, permanent, 23GB)
- Auto-sync runs via bashrc hook on terminal startup

**Current Question:**
How do I query the Redis L2 for all conversations tagged #infrafabric from the last 7 days?
```

---

## Template 2: Full Context Handoff

**Use When:** Complex multi-step work, architectural discussions, code reviews

**Format:**
```markdown
# Conversation Handoff: [Project Name]

**Date:** YYYY-MM-DD
**Previous AI:** Claude Sonnet 4.5
**Conversation ID:** [ID from Open WebUI]
**Duration:** Xh Ym
**Total Messages:** N

---

## Executive Summary

[2-3 paragraph summary of the entire conversation - what was discussed, what was decided, what was built]

---

## Key Decisions Made

1. **Decision:** [Description]
   - **Rationale:** [Why]
   - **Impact:** [What this affects]

2. **Decision:** [Description]
   - **Rationale:** [Why]
   - **Impact:** [What this affects]

---

## Code/Files Created

| File | Purpose | Status |
|------|---------|--------|
| `/path/to/file1.py` | [Purpose] | ✅ Complete |
| `/path/to/file2.md` | [Purpose] | 🟡 In Progress |

---

## Open Questions/Next Steps

- [ ] Question 1
- [ ] Question 2
- [ ] Action item 1

---

## Full Conversation

[Paste full conversation export from Open WebUI as Markdown]

---

## Current Request

[Your new question/task for the next AI]
```

**Example:**
```markdown
# Conversation Handoff: InfraFabric L1/L2 Cache Deployment

**Date:** 2025-11-29
**Previous AI:** Claude Sonnet 4.5
**Conversation ID:** chat-abc123
**Duration:** 4h 30m
**Total Messages:** 87

---

## Executive Summary

Deployed a two-tier Redis cache architecture for InfraFabric to solve cross-session context persistence. L1 (Redis Cloud) provides fast 10ms access for active session data with 30MB capacity. L2 (Proxmox Redis) provides permanent storage with 23GB capacity. Created redis_cache_manager.py (357 lines) as a transparent drop-in replacement for direct Redis connections, handling L1/L2 routing automatically. Deployed auto_context_sync.py (210 lines) with bashrc integration to sync critical files to cache on every new terminal session.

---

## Key Decisions Made

1. **Decision:** Use Redis Cloud as L1 (not local Redis)
   - **Rationale:** Accessible from any machine, no laptop dependency
   - **Impact:** Can work from laptop, desktop, phone seamlessly

2. **Decision:** L2 storage has NO TTL (permanent)
   - **Rationale:** Meta-insights and historical data must persist indefinitely
   - **Impact:** Changed from setex() to set() for all L2 writes

3. **Decision:** Graceful degradation on L1 timeouts
   - **Rationale:** Large files (agents.md 183KB) timeout on Redis Cloud
   - **Impact:** System continues working, logs warning, uses L2 only

---

## Code/Files Created

| File | Purpose | Status |
|------|---------|--------|
| `/home/setup/infrafabric/tools/redis_cache_manager.py` | L1/L2 transparent cache layer | ✅ Complete |
| `/home/setup/infrafabric/tools/auto_context_sync.py` | Auto-sync on session start | ✅ Complete |
| `~/.bashrc` | Auto-sync integration | ✅ Deployed |
| `/home/setup/infrafabric/agents.md` | Updated to v1.4 with mandatory usage | ✅ Complete |

---

## Open Questions/Next Steps

- [ ] Deploy Open WebUI for web-based chat interface
- [ ] Create conversation backup to Redis L2
- [ ] Set up daily automated exports
- [ ] Test from multiple machines

---

## Current Request

Continue with Open WebUI deployment and conversation archival system as discussed.
```

---

## Template 3: Code Review Handoff

**Use When:** Requesting code review or continuation from another AI

**Format:**
```markdown
# Code Review Request: [Feature Name]

**Context:** [1-2 sentences about what this code does]

**Files Changed:**
- `file1.py` ([link or path])
- `file2.py` ([link or path])

**What to Review:**
- [ ] Architecture/design patterns
- [ ] Security vulnerabilities
- [ ] Performance optimizations
- [ ] Code style/readability
- [ ] Edge cases/error handling

**Specific Concerns:**
1. [Concern 1]
2. [Concern 2]

**Code:**

```python
[Paste code here]
```

**Questions:**
1. [Question 1]
2. [Question 2]
```

---

## Template 4: Multi-AI Collaboration

**Use When:** Passing work between Claude, Gemini, GPT for different expertise

**Format:**
```markdown
# Multi-AI Workflow: [Task Name]

## Completed by [AI 1]:

**Task:** [Description]
**Result:** [Summary]
**Files:** [List]

**Full Output:**
[Paste AI 1's output]

---

## Now requesting [AI 2]:

**Task:** [What you need from AI 2]
**Context:** [How this builds on AI 1's work]
**Expected Output:** [Format/deliverable]

**Additional Context:**
[Anything AI 2 needs that AI 1 didn't provide]
```

**Example:**
```markdown
# Multi-AI Workflow: Guardian Council Research & Implementation

## Completed by Claude Sonnet 4.5:

**Task:** Design Guardian Council architecture with 5 archetypes
**Result:** Created guardian.py (747 lines) with Civic, Contrarian, Ethical, Technical, and Operational guardians
**Files:** `/home/setup/infrafabric/restored_s2/src/core/governance/guardian.py`

**Full Output:**
[...guardian.py code...]

---

## Now requesting Gemini Pro:

**Task:** Research academic papers on multi-archetype governance systems and validate our design
**Context:** Claude implemented the architecture above. We need academic validation that this pattern is sound.
**Expected Output:**
- 5-10 relevant academic papers with citations
- Comparison of our design to established governance frameworks
- Recommendations for improvements based on research

**Additional Context:**
This is for autonomous logistics operations in robotics/manufacturing domains. High-risk decisions (entropy >0.8) require human review. We're particularly interested in papers on:
- Multi-agent decision-making
- Check-and-balance systems in AI
- Governance frameworks for autonomous systems
```

---

## Template 5: Session Boundary Handoff

**Use When:** Ending current session, handing off to future Claude instance

**Format:**
```markdown
# Session Handoff for Next Instance

**Date:** YYYY-MM-DD HH:MM
**Project:** [Project Name]
**Current Status:** [One sentence]

---

## What Was Accomplished This Session

1. [Achievement 1]
2. [Achievement 2]
3. [Achievement 3]

---

## Critical Context for Next Session

**Files Modified:**
- `file1` - [What changed]
- `file2` - [What changed]

**Redis Keys Created:**
- `key1` - [Purpose]
- `key2` - [Purpose]

**Environment State:**
- Docker containers: [Which ones running]
- Services: [Which ones active]
- Pending changes: [Git status]

---

## Immediate Next Steps (Priority Order)

1. **[Task 1]** - [Why important]
2. **[Task 2]** - [Why important]
3. **[Task 3]** - [Why important]

---

## Known Issues/Blockers

- [Issue 1] - [Impact]
- [Issue 2] - [Impact]

---

## How to Resume

1. Read this file
2. Run: `[command to verify state]`
3. Check: `[what to verify]`
4. Continue with: [Next task]

---

## Full Session Transcript

**Export Location:** `/home/setup/conversation-archives/json/session-YYYYMMDD.json`
**Markdown:** `/home/setup/conversation-archives/markdown/session-YYYYMMDD.md`
**Redis Key:** `openwebui:conversation:[id]`
```

---

## How to Use These Templates

### For Manual Export:

1. Open Open WebUI conversation
2. Click `⋮` menu → Download as Markdown
3. Choose appropriate template above
4. Fill in template with conversation data
5. Save to `/home/setup/conversation-archives/handoffs/`

### For Automated Export:

Use `openwebui_redis_sync.py` to automatically generate exports:

```bash
# Backup all conversations to Redis L2 + files
python3 /home/setup/infrafabric/tools/openwebui_redis_sync.py

# Exports saved to:
# - JSON: /home/setup/conversation-archives/daily-backups/json/
# - Markdown: /home/setup/conversation-archives/daily-backups/markdown/
```

### For LLM Handoff:

```bash
# Method 1: Direct paste
# Copy markdown export, paste into new AI conversation

# Method 2: File upload
# Upload JSON/MD file to Claude Code, ChatGPT, or Gemini

# Method 3: URL share (if Open WebUI share link enabled)
# Give URL to AI: "Read this conversation: http://85.239.243.227:8080/share/abc123"
```

---

## Quick Reference: Export Formats

| Format | Best For | How to Get |
|--------|----------|------------|
| **JSON** | Machine processing, API calls, exact reproduction | Open WebUI → ⋮ → Download JSON |
| **Markdown** | Human reading, LLM context, documentation | Open WebUI → ⋮ → Download Markdown |
| **Share Link** | Quick sharing, mobile access, web LLMs | Open WebUI → ⋮ → Share → Copy Link |
| **Redis L2** | Permanent archive, cross-session access, search | Run `openwebui_redis_sync.py` |

---

## Pro Tips

1. **Always include file paths** - LLMs can read files directly if you provide paths
2. **Tag conversations** - Use #tags in Open WebUI for easy filtering
3. **Use folders** - Organize by project (InfraFabric, NaviDocs, etc.)
4. **Export often** - Don't wait till end of session
5. **Test handoffs** - Verify LLM understands exported context before continuing
6. **Include Redis keys** - If data is in Redis L2, mention the keys

---

## Troubleshooting

**Problem:** LLM says "I don't have access to that file"
- Solution: Include file content in export, not just path

**Problem:** Context too large for LLM
- Solution: Use Template 1 (Minimal) or extract just relevant portions

**Problem:** Conversation export missing code/files
- Solution: Use `openwebui_redis_sync.py --export-dir /custom/path` for complete export

**Problem:** Can't find old conversation
- Solution: Query Redis L2:
  ```bash
  redis-cli -h 85.239.243.227 -p 6379 \
    -a '@@Redis_InfraFabric_L2_2025$$' \
    KEYS "openwebui:conversation:*"
  ```
