# SESSION RESUME - Last Updated 2025-11-30

## CRITICAL INSTRUCTIONS FOR NEW CLAUDES

### Token Efficiency (MANDATORY)
- **USE HAIKU AGENTS** for all grunt work: file searches, updates, documentation, installations, git operations
- Haiku is 10x cheaper than Sonnet - delegate aggressively
- Only use Sonnet/Opus for complex reasoning and architecture decisions
- Spawn multiple Haiku agents in parallel when tasks are independent

### Current Session State

#### ACTIVE MISSION: 40-Agent Swarm Execution (2025-11-30)
- **Deployment:** Sonnet A + Sonnet B coordinators executing parallel agent swarm
- **Infrastructure:** Proxmox server 85.239.243.227 (Docker, OpenWebUI, ChromaDB operational)
- **Knowledge Base:** 9,832 chunks queryable via ChromaDB
- **Status:** Swarm actively executing - monitoring required for completion
- **Next Action:** Synthesize swarm outputs when execution complete

#### Infrastructure Status (Proxmox 85.239.243.227)
- **Docker:** Operational with OpenWebUI deployment
- **ChromaDB:** 9,832 queryable chunks, 4 collections active
- **S2 Scripts:** All validated and working
- **Knowledge Retrieval:** Real-time semantic search operational

#### IF.emotion Guardian Council Approval (Completed 2025-11-30)
- **Status:** 91.3% consensus achieved (21 Approval, 2 Conditional)
- **Cooling-off Period:** Active until 2025-12-14 (Contrarian Guardian requirement)
- **Guardian Seat:** Granted effective 2025-12-14
- **Documentation:** Complete (IF.emotion.md, Component Proposal, Council Debate)
- **Sergio Chatbot:** 7 authenticated conversations, 100% satisfaction, ready for deployment

#### Infrastructure Expansion & Claude Agent Refinement (Prior Session)
- Full security audit of StackCP shared hosting (2025-11-27)
- Claude Agent deployment attempted on StackCP (OAuth relay server required)
- OCI VM deployed in Montreal region (204.216.111.143) for Canadian IP access
- WireGuard VPN configuration in progress for secure regional connectivity

#### Claude Agent on StackCP - Status
- **Blocker:** Headless OAuth flow needs relay server (cannot use browser-based flow on shared hosting)
- **Solution:** WireGuard VPN enables direct connection to development environment
- Token file: `~/.claude/.credentials.json` (synced from local)
- Web interface: https://digital-lab.ca/claude/ (password: @@Claude305$$)
- Socket: `~/claude-agent.sock` (NOT in /dev/shm!)

#### A1 Hunter (AI Task Distribution)
- Still running on StackCP (spawned via ProcessWire admin)
- Recurring issue: "Out of host capacity" error in Montreal region
- Status: Monitoring required before scaling tasks

### Files to Read First
1. `/home/setup/infrafabric/agents.md` - Master documentation
2. `/home/setup/infrafabric/SESSION-RESUME.md` - This file
3. `/tmp/STACKCP_RED_TEAM_REPORT_FINAL.md` - Full red team report

### Active Projects
- **InfraFabric:** `/home/setup/infrafabric` (marketing) + `/home/setup/infrafabric-core` (research)
- **NaviDocs:** `/home/setup/navidocs` - 65% complete, cloud sessions ready
- **StackCP:** Security hardened, Claude Agent deployed
- **Job Hunt:** `/home/setup/job-hunt` on local Gitea

### Credentials Reference
- StackCP SSH: `ssh stackcp` (configured in ~/.ssh/config)
- Gitea: http://localhost:4000/ (dannystocker / @@Gitea305$$)
- Claude Max OAuth: `~/.claude/.credentials.json`

### OpenWebUI CLI RFC (Late Session Addition - 2025-11-30)
- **Proposal Document:** `/mnt/c/Users/setup/Downloads/OPENWEBUI_CLI_PROPOSAL_RFC.md`
- **Status:** Ready for offline LLM review then OpenWebUI team submission
- **Next Action:** Review RFC feedback, then build Phase 1 MVP

### 40-Agent Swarm Status (Late Session Addition - 2025-11-30)
- **Sonnet A & B:** Running infrastructure + security tasks
- **Haiku C & D Prompts:** Prepared for accelerator/validator roles
- **Autonomous Orchestrator:** Roadmap defined (P1-P7 phases)

### Next Immediate Actions (P0 Priority)
1. **Review CLI RFC with Offline LLM:**
   - Analyze OpenWebUI CLI proposal for technical feasibility
   - Gather feedback before OpenWebUI team submission
   - Plan Phase 1 MVP architecture

2. **Monitor 40-Agent Swarm Execution:** Sonnet A + B coordinators running parallel tasks
   - 9,832 chunks queryable from ChromaDB knowledge base
   - Real-time semantic search operational on Proxmox 85.239.243.227
   - Status: Awaiting completion for output synthesis

3. **Post-Cooling-Off IF.emotion Deployment (2025-12-14):**
   - Deploy Spanish language filter to Sergio chatbot
   - Activate speed optimizations (embedding cache: 3.5x faster, ChromaDB: 20% faster)
   - Launch X Multiplier plan (AI detection goal: <30%)

4. **OAuth Relay Server:** Implement headless OAuth relay to enable Claude Agent on StackCP
   - Alternative: Use WireGuard VPN tunnel for local development access

### Future Tasks
1. Address CVE recommendations (OpenSSH 8.7p1 RegreSSHion, PHP 8.0.30 EOL)
2. Validate credential sync to StackCP (`~/.claude/sync-creds-to-stackcp.sh`)
3. Test Claude Agent with actual prompts once relay server deployed
4. Continue NaviDocs cloud sessions (5 sessions ready, $90 budget)

### Infrastructure Summary
- **Proxmox Server (85.239.243.227):** Primary deployment platform
  - Docker: OpenWebUI operational
  - ChromaDB: 9,832 queryable chunks, 4 collections active
  - S2 Scripts: All validated and working
  - Knowledge Retrieval: Real-time semantic search operational

- **StackCP:** Shared hosting + Claude Agent deployment point (OAuth blocker)
  - A1 Hunter: Spawned via ProcessWire, monitoring required
  - Monitoring: "Out of host capacity" error in Montreal region

- **OCI VM (Montreal):** 204.216.111.143 - Canadian IP for regional constraints
- **WireGuard:** VPN tunnel in progress for secure development access

---
*Last Updated: 2025-11-30 - Current mission: 40-Agent Swarm Execution with Sonnet A + B coordinators*
