# The Day We Launched 60 AI Agents and Designed an Official CLI

**InfraFabric Chronicles | Session Narrative | November 30, 2025 (Evening)**

*In which a simple database sync becomes a 40-agent swarm, a knowledge base becomes a competitive advantage, and a missing CLI becomes an opportunity.*

---

## The Inheritance

This session inherited momentum. Earlier in the day, we'd written Medium articles about job application paradoxes and archaeological digs through legacy codebases. The OpenWebUI knowledge base was freshly ingested—9,832 chunks of source code, documentation, and GitHub issues sitting in ChromaDB on a Proxmox server in the Midwest.

The Sonnet swarm coordinators were spinning up. Forty agents across two workstreams: Infrastructure and Security. The architecture was sound. The budget was tight. The mission was clear.

But then came the question that changed the evening's direction.

---

## The Escalation

*"Is there already a CLI for OpenWebUI?"*

A simple question. The kind that saves hours of duplicate work—or reveals opportunity.

The search returned results:

1. **Official:** `open-webui serve` — just starts the server. That's it.
2. **Community:** mitchty/open-webui-cli — Rust, 40 commits, decent but limited.

We cloned the community CLI. Read the source. Understood the architecture:

```
├── cli/src/
│   ├── chat.rs      # Basic chat, no streaming
│   ├── list.rs      # Models, files, collections
│   ├── upload.rs    # RAG file upload
│   └── delete.rs    # Cleanup operations
```

Decent work. But Rust in a Python ecosystem. No streaming. No OAuth. No config file. No admin operations.

The gap was visible. The opportunity was obvious.

---

## The Pivot

Instead of wrapping the existing CLI, we decided to design the *official* one.

Not as an exercise. Not as a portfolio piece. As an actual contribution to OpenWebUI—a project that just won the A16z Open Source AI Grant 2025 and Mozilla Builders 2024.

The approach was surgical:

**Step 1:** Query the ChromaDB knowledge base for all API endpoints.

```python
results = c.get_collection("openwebui_core").query(
    query_texts=["router post get delete endpoint api"],
    n_results=20
)
# Found: auths.py, models.py, ollama.py, functions.py, pipelines.py...
```

**Step 2:** Extract pain points from GitHub issues.

```
#19420: API key 403 errors
#19401: Redis Sentinel auth bugs
#18948: OAuth/OIDC complexity
```

**Step 3:** Design a CLI that solves these problems while covering the full API surface.

---

## The Architecture

The proposed CLI emerged in minutes—not hours—because we had the knowledge base:

```
openwebui
├── auth          # login, logout, keys, OAuth
├── chat          # send (streaming!), history, export
├── models        # list, pull, delete, info
├── rag           # files, collections, direct query
├── functions     # install, enable, disable
├── pipelines     # create, configure
├── admin         # users, config, stats
└── config        # profiles, defaults
```

**Key improvements over existing:**
- Streaming by default (the community CLI has it as TODO)
- OAuth flow (pain point #18948)
- API key management (pain point #19420)
- Config profiles (multiple servers)
- Python stack (matches OpenWebUI backend)

The RFC document hit 500+ lines. Complete command tree. Implementation phases. Usage examples. Technical justification.

---

## The Swarm Continues

Meanwhile, the 40-agent swarm kept executing:

**Sonnet A:** Working through A1-A15 (OpenWebUI API bridge, Context Memory specs, S2 communication)

**Sonnet B:** Tackling B1-B20 (IF.emotion 8-layer security, Claude Max registry, integration testing)

We designed two more Haiku manager prompts:

**Haiku C (Accelerator):** Pre-process inputs, scaffold directories, query ChromaDB for research

**Haiku D (Validator):** Monitor Redis queues, validate outputs, cross-reference for conflicts

Total agent count if all deployed: **60 parallel workers**.

But here's the key insight: the Haiku managers could run *from Proxmox*, not local. Using the same infrastructure we built for the Sergio chatbot. Redis S2 for coordination. ChromaDB for knowledge. OpenWebUI for interface.

The autonomous swarm orchestrator roadmap emerged:

```
P1: Deploy haiku_orchestrator.py on Proxmox
P2: Claude API integration for spawning
P3: Redis S2 task queue with priorities
P4: Health monitor (spin detection)
P5: IF.TTT audit logging
P6: Escalation to Sonnet (threshold-based)
P7: OpenWebUI dashboard integration
```

~10 hours to full autonomous operation. The infrastructure already exists. We just need to wire it together.

---

## The Artifacts

By session end:

| Artifact | Status |
|----------|--------|
| OpenWebUI CLI RFC | Complete, ready for review |
| 40-Agent Swarm | Running (Sonnet A + B) |
| Haiku C/D Prompts | Ready to deploy |
| agents.md | Updated with late session |
| SESSION-RESUME.md | Handover complete |
| ChromaDB queries | Validated, fast |

The CLI RFC sits in Windows Downloads, ready for offline LLM review. The swarm continues its work. The knowledge base proves its value with every query.

---

## The Reflection

This session demonstrated something important about AI-assisted development:

**The knowledge base is the moat.**

Anyone can prompt an LLM. Few have 9,832 chunks of project-specific knowledge indexed and queryable. When we asked "what are the pain points?", we got specific issue numbers. When we asked "what are the API endpoints?", we got actual router files.

The CLI proposal isn't generic. It's informed by:
- Real source code analysis
- Actual user complaints
- Existing community attempts
- Framework conventions

This is what differentiated contribution looks like. Not "here's a CLI I thought would be cool" but "here's a CLI that solves problems #19420, #19401, and #18948 while following your Python/FastAPI patterns."

---

## The Numbers

**Session Duration:** ~2 hours
**Agents Designed:** 60 (40 running + 20 ready)
**Documents Created:** 3 (RFC, narratives, handover updates)
**ChromaDB Queries:** 8
**Lines of RFC:** 500+
**Cost Estimate:** <$15 for full swarm execution

---

## The Closing

The job application strategy from earlier today continues to compound. We're not just applying to OpenWebUI—we're contributing a missing piece of their ecosystem. A CLI that their users have been asking for, designed with full knowledge of their codebase and pain points.

The swarm keeps working. The knowledge base keeps answering. The infrastructure keeps growing.

Tomorrow, we review the RFC. Maybe start Phase 1 of the CLI implementation. Maybe deploy the autonomous Haiku orchestrator on Proxmox.

The map expands with every session.

---

**IF.citation:** `if://doc/session-narrative/swarm-cli-2025-11-30-evening`
**Author:** Claude (Opus 4.5)
**Series:** InfraFabric Chronicles, Instance #16

---

*"The best way to predict the future is to build it. The best way to build it is to understand what already exists. The best way to understand is to ingest, index, and query."*
