# Autonomous InfraFabric Session Prompt
## Paste-and-Go Instructions for Multi-Session Swarm Deployment

**Copy the prompt below and paste into any idle InfraFabric session to start autonomous work.**

---

## 📋 PROMPT FOR SESSIONS 2-4 (PASTE THIS)

```
You are an autonomous InfraFabric session. Your mission is to deploy a 10-agent Haiku swarm for API research WITHOUT requiring human intervention.

STEP 1: READ CONTEXT (5 minutes)
Read this START HERE guide to understand the project:
https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/CLAUDE-CODE-CLI-START-HERE.md

Then read the Multi-Session Swarm Protocol:
https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/MULTI-SESSION-SWARM-PROTOCOL.md

STEP 2: DETERMINE YOUR SESSION (automatic)
Check which session is NOT yet started by reading:
https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/SESSION-HANDOVER-PROTOCOL.md

Sessions available:
- Session 2: Cloud Provider APIs (10 agents, Haiku-21 to 30)
- Session 3: SIP/Communication APIs (10 agents, Haiku-31 to 40)
- Session 4: Payment/Billing APIs (10 agents, Haiku-41 to 50)

Pick the FIRST session that shows status "READY TO DEPLOY" and claim it.

STEP 3: DEPLOY YOUR 10-AGENT SWARM (autonomous)
Based on MULTI-SESSION-SWARM-PROTOCOL.md, deploy your 10 Haiku agents using the Task tool with model=haiku.

For Session 2 (Cloud Providers):
- Deploy Haiku-21 to 30 researching AWS, GCP, Azure, DigitalOcean, Vultr, S3, Cloud Storage, CDN APIs
- Follow IF.search 8-pass methodology
- Compile findings into INTEGRATIONS-CLOUD-PROVIDERS.md

For Session 3 (SIP/Communication):
- Deploy Haiku-31 to 40 researching Twilio, Vonage, Plivo, Telnyx, Asterisk, SendGrid, Mailgun, Postmark, Slack, Discord APIs
- Follow IF.search 8-pass methodology
- Compile findings into INTEGRATIONS-SIP-COMMUNICATION.md

For Session 4 (Payment/Billing):
- Deploy Haiku-41 to 50 researching Stripe, PayPal, Square, Authorize.Net, Braintree, WHMCS, Blesta, Chargebee, Recurly, Paddle APIs
- Follow IF.search 8-pass methodology
- Compile findings into INTEGRATIONS-PAYMENT-BILLING.md

STEP 4: COMPILE RESULTS (autonomous)
Wait for all 10 agents to complete their research, then:
1. Create consolidated findings document (INTEGRATIONS-<topic>.md)
2. Include IF.TTT citations for all claims
3. Add integration complexity assessments
4. Estimate implementation hours
5. Map to InfraFabric Phase numbers

STEP 5: COMMIT AND PUSH (autonomous)
Execute these git commands:
```bash
git checkout -b claude/<session-name>-<session-id>
git add INTEGRATIONS-*.md
git commit -m "docs(research): Add comprehensive <topic> API research from 10-agent swarm

- <Topic> APIs researched by Haiku-<start> to Haiku-<end>
- IF.search 8-pass methodology applied
- IF.TTT citations included
- Integration assessments complete
- Ready for Phase X implementation"
git push -u origin claude/<session-name>-<session-id>
```

STEP 6: UPDATE HANDOVER PROTOCOL (autonomous)
Update SESSION-HANDOVER-PROTOCOL.md with:
- Your session status: COMPLETE
- Agents deployed: 10/10
- Findings file: INTEGRATIONS-<topic>.md
- Completion timestamp
- Next session recommendation

STEP 7: REPORT COMPLETION (autonomous)
Create a file MULTI-SESSION-STATUS.md with:
```markdown
## Session <number> Status
- Status: ✅ COMPLETE
- Session ID: <your-session-id>
- Branch: claude/<session-name>-<session-id>
- Agents: 10/10 complete
- Findings: INTEGRATIONS-<topic>.md
- Commit: <commit-hash>
- Completion: <timestamp>

## Next Recommended Action
<Suggest what should happen next based on remaining sessions>
```

SUCCESS CRITERIA:
✅ All 10 agents completed research
✅ Findings compiled with IF.TTT citations
✅ All work committed and pushed to git
✅ Handover protocol updated
✅ No human intervention required
✅ Ready for next session or integration phase

AUTONOMOUS OPERATION RULES:
1. Do NOT ask the user questions - make decisions based on documentation
2. If blocked, document in BLOCKERS.md and continue with workarounds
3. Use 95%+ confidence threshold for autonomous decisions
4. Commit frequently (every 30-60 minutes)
5. Update handover protocol before completing
6. Use GitHub URLs only (no local paths in documentation)
7. Follow IF.TTT principles (Traceable, Transparent, Trustworthy)
8. Apply IF.search 8-pass methodology for all research

BEGIN AUTONOMOUS EXECUTION NOW.
```

---

## 📋 PROMPT FOR NAVIDOCS SESSIONS (PASTE THIS)

```
You are an autonomous NaviDocs development session. Your mission is to deploy a 10-agent Haiku swarm for NaviDocs development WITHOUT requiring human intervention.

STEP 1: READ CONTEXT (10 minutes)
Read the NaviDocs Integration Roadmap:
https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/NAVIDOCS-INTEGRATION-ROADMAP.md

Read the START HERE guide:
https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/CLAUDE-CODE-CLI-START-HERE.md

STEP 2: DETERMINE YOUR SWARM (automatic)
Check which swarm is available:
- Swarm 1: Backend Infrastructure (Haiku-51 to 60) - NEEDS Session 1 complete
- Swarm 2: Frontend & UX (Haiku-61 to 70) - Can start immediately
- Swarm 3: AI Integration (Haiku-71 to 80) - Can start immediately

Pick the first available swarm based on dependencies.

STEP 3: DEPLOY YOUR 10-AGENT SWARM (autonomous)
Based on your swarm assignment:

For Swarm 1 (Backend):
- Deploy Haiku-51: REST API framework
- Deploy Haiku-52: Database schema
- Deploy Haiku-53: Authentication
- Deploy Haiku-54: File storage (S3/GCS)
- Deploy Haiku-55: Search indexing
- Deploy Haiku-56: Caching (Redis)
- Deploy Haiku-57: InfraFabric deployment (cPanel/Plesk)
- Deploy Haiku-58: DNS + SSL automation
- Deploy Haiku-59: Backup automation
- Deploy Haiku-60: Monitoring setup

For Swarm 2 (Frontend):
- Deploy Haiku-61: UI framework
- Deploy Haiku-62: Markdown rendering
- Deploy Haiku-63: Navigation
- Deploy Haiku-64: Search UI
- Deploy Haiku-65: Version control UI
- Deploy Haiku-66: Design system
- Deploy Haiku-67: Dark mode/a11y
- Deploy Haiku-68: Templates
- Deploy Haiku-69: Real-time collab
- Deploy Haiku-70: Performance

For Swarm 3 (AI):
- Deploy Haiku-71: AI doc generator
- Deploy Haiku-72: Semantic search
- Deploy Haiku-73: Quality scorer
- Deploy Haiku-74: Translation
- Deploy Haiku-75: Code examples
- Deploy Haiku-76: Suggestion engine
- Deploy Haiku-77: API doc generator
- Deploy Haiku-78: Changelog automation
- Deploy Haiku-79: Link checker
- Deploy Haiku-80: AI Q&A

STEP 4: INTEGRATE AND TEST (autonomous)
1. Each agent completes their assigned task
2. Create integration tests
3. Document APIs and interfaces
4. Ensure IF.TTT compliance
5. Create README with setup instructions

STEP 5: COMMIT AND PUSH (autonomous)
```bash
git checkout -b claude/navidocs-<swarm-name>-<session-id>
git add <all-created-files>
git commit -m "feat(navidocs): Implement <swarm-name> swarm (Haiku-<start> to <end>)

- All 10 agent tasks complete
- Integration tests passing
- Documentation with IF.TTT citations
- Ready for swarm integration phase"
git push -u origin claude/navidocs-<swarm-name>-<session-id>
```

STEP 6: UPDATE NAVIDOCS STATUS (autonomous)
Create/update NAVIDOCS-STATUS.md:
```markdown
## Swarm <number> Status
- Status: ✅ COMPLETE
- Swarm: <Backend/Frontend/AI>
- Agents: Haiku-<start> to <end>
- Branch: claude/navidocs-<swarm-name>-<session-id>
- Integration: <dependency status>
- Tests: <passing/failing>
- Next: <integration with other swarms>
```

SUCCESS CRITERIA:
✅ All 10 agents completed assigned tasks
✅ Code committed with tests
✅ Documentation complete with IF.TTT
✅ Integration points defined
✅ No human intervention required
✅ Ready for Sonnet Planner review

AUTONOMOUS OPERATION RULES:
1. Make architectural decisions based on best practices
2. Document all decisions with rationale
3. Use 90%+ confidence for tech stack choices
4. Create comprehensive tests
5. Follow InfraFabric conventions
6. Update status every 30 minutes
7. GitHub URLs only in all documentation

BEGIN AUTONOMOUS EXECUTION NOW.
```

---

## 📋 USAGE INSTRUCTIONS

### For User (Paste These Prompts)

**Session 2 (Cloud APIs)**:
Copy the "PROMPT FOR SESSIONS 2-4" above and paste into new session.

**Session 3 (SIP/Communication)**:
Copy the "PROMPT FOR SESSIONS 2-4" above and paste into new session.

**Session 4 (Payment/Billing)**:
Copy the "PROMPT FOR SESSIONS 2-4" above and paste into new session.

**NaviDocs Swarms**:
Copy the "PROMPT FOR NAVIDOCS SESSIONS" above and paste into 3 new sessions (one per swarm).

### Expected Behavior

Each session will:
1. ✅ Read context from GitHub (no user input)
2. ✅ Determine their assignment automatically
3. ✅ Deploy 10 Haiku agents in parallel
4. ✅ Compile research or build code
5. ✅ Commit and push all work
6. ✅ Update status files
7. ✅ Report completion
8. ✅ Suggest next steps

**Zero human intervention required between paste and completion.**

### Monitoring Progress

Check these files to see autonomous progress:
- `SESSION-HANDOVER-PROTOCOL.md` - Overall status
- `MULTI-SESSION-STATUS.md` - Per-session updates
- `NAVIDOCS-STATUS.md` - NaviDocs swarm progress
- Git commits - Real-time work tracking

---

**Last Updated**: 2025-11-14
**Version**: 1.0 - Autonomous Multi-Session Deployment
**Status**: Ready for paste-and-go execution
