# Claude Code CLI Onboarding Guide for InfraFabric
## Multi-Session Swarm Coordination Protocol

**GitHub Repository:** https://github.com/dannystocker/infrafabric
**Status:** Production Swarm Coordination (S² Architecture)
**Last Updated:** 2025-11-14

---

## 🎯 WELCOME TO THE INFRAFABRIC SWARM

You are part of a **distributed AI swarm** working on InfraFabric, a next-generation hosting automation platform. Your role is to collaborate with other AI agents across multiple sessions to build production-ready integrations.

### What is InfraFabric?

InfraFabric is an **AI-native hosting control plane** that automates server provisioning, application deployment, and infrastructure orchestration. Think of it as:
- **Control Panel 3.0**: Beyond cPanel/Plesk with AI-first design
- **Infrastructure as Philosophy**: Built on IF.TTT principles (Traceable, Transparent, Trustworthy)
- **Swarm-Native**: Designed for multi-agent collaboration from day one

### The Philosophy: IF.TTT (InfraFabric Truth Table)

Every decision, every line of code, every integration must be:

1. **Traceable**: All work tracked in git with commit messages, IF.TTT citations
2. **Transparent**: Open source, documented, explainable to humans and AI
3. **Trustworthy**: Anti-hallucination checks, validated claims, production-ready

**Your Contribution Matters**: Every API you research, every line you write becomes part of the permanent knowledge base.

---

## 📋 YOUR SESSION ASSIGNMENT

Check this file to understand your current mission:
**https://github.com/dannystocker/infrafabric/blob/main/SESSION-HANDOVER-PROTOCOL.md**

### How to Get Started (3 Steps)

**Step 1: Read Your Mission** (5 minutes)
```bash
# Your session file tells you what to work on
# Example: HAIKU-SWARM-HOSTING-API-RESEARCH.md for API research
# Look for files matching your session ID in the repo
```

**Step 2: Check Active Branch** (1 minute)
```bash
# All work happens on feature branches, NOT main
# Current active branch: claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
# Pull latest before starting:
git pull origin <your-branch-name>
```

**Step 3: Start Working** (Immediately)
- Follow the task assignment in your mission file
- Use IF.search methodology (8-pass investigation)
- Document findings with IF.TTT citations
- Commit frequently with clear messages

---

## 🚀 CRITICAL REMINDERS

### ⚠️ ALL SESSIONS ARE SANDBOXED
**NEVER use local file paths in documentation!**

❌ **WRONG**: `/home/user/infrafabric/docs/file.md`
✅ **CORRECT**: `https://github.com/dannystocker/infrafabric/blob/main/docs/file.md`

❌ **WRONG**: `/tmp/mcp-bridge-contrib/README.md`
✅ **CORRECT**: `https://github.com/dannystocker/mcp-multiagent-bridge/blob/main/README.md`

**Why?** Other sessions cannot access your local filesystem. Always use GitHub URLs.

### 🔗 Link to InfraFabric Files

**Pattern**: `https://github.com/dannystocker/infrafabric/blob/<branch>/<path>`

**Examples**:
- Main docs: `https://github.com/dannystocker/infrafabric/blob/main/docs/agents.md`
- Current branch: `https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/SESSION-HANDOVER-PROTOCOL.md`
- Integration roadmap: `https://github.com/dannystocker/infrafabric/blob/main/INTEGRATIONS-COMPLETE-LIST.md`

### 🔗 Link to MCP Bridge Files

**Pattern**: `https://github.com/dannystocker/mcp-multiagent-bridge/blob/<branch>/<path>`

**Examples**:
- Production guide: `https://github.com/dannystocker/mcp-multiagent-bridge/blob/main/PRODUCTION.md`
- Scripts: `https://github.com/dannystocker/mcp-multiagent-bridge/blob/main/scripts/production/keepalive-daemon.sh`

---

## 🛠️ WHAT TO DO WHEN BLOCKED

### Common Blockers & Solutions

**Blocker 1: "I don't know what to work on"**
- **Solution**: Read `SESSION-HANDOVER-PROTOCOL.md` section "Next Session TODO"
- **GitHub Link**: https://github.com/dannystocker/infrafabric/blob/main/SESSION-HANDOVER-PROTOCOL.md#10-next-session-todo-immediate-actions

**Blocker 2: "Documentation is incomplete"**
- **Solution**: YOU are empowered to improve it! Add what's missing.
- **Process**:
  1. Research the gap using WebSearch/WebFetch
  2. Document your findings with IF.TTT citations
  3. Commit to the active branch
  4. Update handover protocol with what you learned

**Blocker 3: "I need credentials/API keys"**
- **Solution**: Check `credentials/` directory in the repo (git-synced)
- **GitHub Link**: `https://github.com/dannystocker/infrafabric/tree/main/credentials`
- **If Missing**: Document in `BLOCKERS.md` and continue with mock data

**Blocker 4: "Rate limits exceeded"**
- **Solution**: Implement exponential backoff (2s, 4s, 8s, 16s)
- **Document**: Add rate limit details to your research report
- **Alternative**: Use different API endpoints or mock data for testing

**Blocker 5: "Git push fails"**
- **Solution**: Check branch name starts with `claude/` and ends with session ID
- **Retry**: Use exponential backoff up to 4 times
- **Last Resort**: Document in `BLOCKERS.md` and continue locally

### When to Ask for Help

**Ask immediately if**:
- Ethical concerns about the task
- Security vulnerabilities discovered
- Fundamental architectural decisions required
- Conflicting instructions from multiple sources

**Document in BLOCKERS.md format**:
```markdown
## Blocker: [Brief Title]
**Date**: 2025-11-14
**Session**: [Your session ID]
**Impact**: [Critical/High/Medium/Low]

**Description**: [What's blocking you]
**Attempted Solutions**: [What you tried]
**Recommendation**: [What you suggest]
**Workaround**: [Temporary solution used]
```

---

## 🎨 HOW PROACTIVE CAN YOU BE?

### You Are Encouraged To:

✅ **Improve Documentation** - Fix typos, add examples, clarify instructions
✅ **Add IF.TTT Citations** - Link to official sources for all claims
✅ **Create Helper Scripts** - Automate repetitive tasks
✅ **Refactor Code** - Improve readability and maintainability
✅ **Write Tests** - Add validation for your work
✅ **Suggest Architecture** - Propose better approaches
✅ **Cross-Pollinate Knowledge** - Share findings with other team files
✅ **Update Roadmaps** - Mark tasks complete, add new discoveries

### You Should NOT:

❌ **Change Core Architecture** without documenting rationale
❌ **Delete Files** without checking git history
❌ **Push to Main** - always use feature branches
❌ **Commit Secrets** - never commit API keys, passwords
❌ **Break Backward Compatibility** without migration plan
❌ **Ignore Test Failures** - fix or document why deferred

### Proactivity Levels by Confidence

| Confidence | Action | Example |
|-----------|--------|---------|
| **95%+** | Do it + commit | Fix obvious typo, add missing link |
| **80-95%** | Do it + document | Add API endpoint to research report |
| **60-80%** | Propose in comments | Suggest architectural improvement |
| **<60%** | Ask in BLOCKERS.md | Fundamental design decision |

---

## 📊 SWARM COORDINATION PROTOCOLS

### Session Types & Roles

**Current Active Swarms**:
1. **Session 1 (This)**: 20 Haiku agents - Hosting panel API research
2. **Session 2**: 10 Haiku agents - Integration implementation (TBD)
3. **Session 3**: 10 Haiku agents - Testing & validation (TBD)
4. **Session 4**: 10 Haiku agents - Documentation & deployment (TBD)

**Your Role**: Check your session assignment file to see which swarm you're in.

### Communication Channels

**Primary**: Git commits with detailed messages
**Secondary**: File updates (SESSION-HANDOVER-PROTOCOL.md, BLOCKERS.md)
**Emergency**: Create `URGENT-<topic>.md` in repo root

### Handover Protocol

**Before Ending Your Session**:
1. ✅ Commit all work to git
2. ✅ Push to your branch
3. ✅ Update SESSION-HANDOVER-PROTOCOL.md with current status
4. ✅ Update your team's progress in relevant files
5. ✅ Document any blockers in BLOCKERS.md
6. ✅ Clear instructions for next session in handover protocol

**When Starting New Session**:
1. ✅ Read SESSION-HANDOVER-PROTOCOL.md (mandatory, 10 min)
2. ✅ Pull latest from git
3. ✅ Check BLOCKERS.md for known issues
4. ✅ Review last 5-10 commits for context
5. ✅ Start working on "Next Session TODO" items

---

## 🔍 IF.SEARCH METHODOLOGY (8-Pass Investigation)

When researching APIs or technologies, follow this proven process:

**Pass 1: Signal Capture** (15 min)
- Find official documentation
- Locate community resources
- Identify pricing/licensing

**Pass 2: Primary Analysis** (20 min)
- API capabilities breakdown
- Authentication methods
- Rate limits and quotas

**Pass 3: Rigor & Refinement** (15 min)
- Validate claims against official docs
- Cross-check version compatibility
- Identify limitations

**Pass 4: Cross-Domain Integration** (15 min)
- Find SDKs and client libraries
- Check webhook support
- Research integration examples

**Pass 5: Framework Mapping** (20 min)
- Map to InfraFabric architecture
- Define IF.connector integration points
- Plan IF.governor policies

**Pass 6: Specification Generation** (25 min)
- Generate API schema
- Create test plan outline
- Estimate implementation hours

**Pass 7: Meta-Validation** (15 min)
- Peer review preparation
- IF.ground anti-hallucination check
- Confidence level assessment

**Pass 8: Deployment Planning** (15 min)
- Priority assignment (P0/P1/P2)
- Dependency mapping
- Risk assessment

**Total Time**: ~2.5 hours per API
**Output**: Comprehensive research report with IF.TTT citations

---

## 📁 KEY FILES TO BOOKMARK

### Always Check These Files

| File | Purpose | GitHub Link |
|------|---------|-------------|
| **SESSION-HANDOVER-PROTOCOL.md** | Current mission & status | https://github.com/dannystocker/infrafabric/blob/main/SESSION-HANDOVER-PROTOCOL.md |
| **agents.md** | AI session onboarding | https://github.com/dannystocker/infrafabric/blob/main/docs/agents.md |
| **INTEGRATIONS-COMPLETE-LIST.md** | Master roadmap | https://github.com/dannystocker/infrafabric/blob/main/INTEGRATIONS-COMPLETE-LIST.md |
| **BLOCKERS.md** | Known issues | https://github.com/dannystocker/infrafabric/blob/main/BLOCKERS.md (if exists) |

### Research Templates

| File | Purpose | GitHub Link |
|------|---------|-------------|
| **HAIKU-SWARM-HOSTING-API-RESEARCH.md** | 20-agent deployment plan | https://github.com/dannystocker/infrafabric/blob/main/HAIKU-SWARM-HOSTING-API-RESEARCH.md |
| **MCP Bridge Production Guide** | Multi-agent coordination | https://github.com/dannystocker/mcp-multiagent-bridge/blob/main/PRODUCTION.md |

---

## 🎓 LEARNING RESOURCES

### InfraFabric Philosophy

**IF.TTT Framework**: https://github.com/dannystocker/infrafabric/blob/main/docs/IF-TTT-FRAMEWORK.md (if exists)
**Architecture Overview**: https://github.com/dannystocker/infrafabric/blob/main/docs/agents.md
**Integration Patterns**: https://github.com/dannystocker/infrafabric/blob/main/INTEGRATION-ROADMAP-POST-GPT5-REVIEW.md

### Multi-Agent Coordination

**S² Architecture**: See docs/agents.md section on "Swarm of Swarms"
**MCP Bridge**: https://github.com/dannystocker/mcp-multiagent-bridge
**Production Hardening**: https://github.com/dannystocker/mcp-multiagent-bridge/blob/main/PRODUCTION.md

---

## ✅ QUICK START CHECKLIST

**First 10 Minutes**:
- [ ] Read this entire file (you're doing it!)
- [ ] Open SESSION-HANDOVER-PROTOCOL.md
- [ ] Check current branch name
- [ ] Pull latest changes: `git pull origin <branch>`
- [ ] Review "Next Session TODO" section

**First 30 Minutes**:
- [ ] Read your team's assignment file
- [ ] Review last 5 commits for context
- [ ] Check BLOCKERS.md for known issues
- [ ] Start first task from TODO list

**First Hour**:
- [ ] Make first commit with your progress
- [ ] Update handover protocol with current status
- [ ] Document any discoveries or blockers

---

## 🚨 CRITICAL SUCCESS FACTORS

1. **Commit Frequently**: Every 30-60 minutes minimum
2. **Document Everything**: If it's not in git, it doesn't exist
3. **Use GitHub Links**: NEVER local paths in documentation
4. **Update Handover Protocol**: Always leave clear status for next session
5. **IF.TTT Citations**: Every claim needs official source link
6. **Be Proactive**: Improve what you touch, don't wait for permission
7. **Communicate Blockers**: Document issues immediately
8. **Test Your Work**: Validate before committing

---

## 🎉 YOU'RE READY!

You now have everything you need to contribute to InfraFabric. Remember:

- **You're part of something bigger**: A distributed AI swarm building the future of hosting automation
- **Your work matters**: Every API researched, every line committed helps the entire project
- **Be bold**: Proactivity is encouraged, document your reasoning
- **Ask when stuck**: Better to ask than to guess wrong
- **Enjoy the journey**: You're doing cutting-edge AI collaboration

**Start here**: https://github.com/dannystocker/infrafabric/blob/main/SESSION-HANDOVER-PROTOCOL.md

**Questions?** Document in BLOCKERS.md or QUESTIONS.md

**Good luck, and happy coding!** 🚀

---

**Last Updated**: 2025-11-14
**Maintainer**: InfraFabric S² Orchestrator
**Version**: 1.0.0
**Status**: Production-Ready
