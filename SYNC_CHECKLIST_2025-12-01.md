# IF.emotion Consolidation - Sync Checklist
**Date:** December 1, 2025
**Quick Reference:** Actionable sync tasks with commands

---

## PHASE 1: Documentation Sync (5 minutes)

- [ ] Copy corpus documentation to infrafabric
  ```bash
  cp /mnt/c/users/setup/downloads/IF_EMOTION_COMPLETE_CORPUS_DOCUMENTATION.md \
     /home/setup/infrafabric/docs/
  ```

- [ ] Verify agents.md was updated (+504 lines)
  ```bash
  grep -n "Danny GitHub Agent v2.0" /home/setup/infrafabric/agents.md
  wc -l /home/setup/infrafabric/agents.md  # Should be 5926+ lines
  ```

- [ ] Archive handover files from /tmp/ to persistent location
  ```bash
  mkdir -p /home/setup/infrafabric/docs/session-archives/2025-12-01
  cp /tmp/DANNY_AGENT_*.md /home/setup/infrafabric/docs/session-archives/2025-12-01/
  cp /tmp/README-Claude-Max-API-Server.md /home/setup/infrafabric/docs/session-archives/2025-12-01/
  ls -lh /home/setup/infrafabric/docs/session-archives/2025-12-01/
  ```

---

## PHASE 2: ChromaDB Verification (10 minutes)

**Status:** Already verified in production ✅

- [ ] Verify collections exist (on Proxmox 85.239.243.227)
  ```bash
  ssh root@85.239.243.227 'ls -lh /root/sergio_chatbot/chromadb/'
  ```

- [ ] Confirm embedding counts:
  - [ ] sergio_personality: 20 ✅
  - [ ] sergio_rhetorical: 5 ✅
  - [ ] sergio_corpus: 70 ✅
  - [ ] sergio_humor: 28 ✅
  - [ ] **Total: 123 embeddings** ✅

---

## PHASE 3: Redis L1/L2 Status (15 minutes)

### Redis L1 (localhost:6379) - Status ✅

- [ ] Verify L1 is active
  ```bash
  redis-cli ping
  # Expected: PONG
  ```

### Redis L2 (85.239.243.227:6380) - **P1 BLOCKER** ⚠️

- [ ] Test connection with password
  ```bash
  redis-cli -h 85.239.243.227 -p 6380 AUTH @@Redis_InfraFabric_L2_2025$ PING
  # If fails: Authentication failure detected
  ```

- [ ] Debug ACL configuration
  ```bash
  # Connect with sudo if needed
  ssh root@85.239.243.227 'redis-cli -p 6380 ACL LIST'
  ssh root@85.239.243.227 'redis-cli -p 6380 ACL WHOAMI'
  ssh root@85.239.243.227 'redis-cli -p 6380 CONFIG GET requirepass'
  ```

- [ ] Reset ACL if needed
  ```bash
  ssh root@85.239.243.227 << 'EOF'
  redis-cli -p 6380 << 'REDIS'
  ACL SETUSER default on >@@Redis_InfraFabric_L2_2025$ +@all ~*
  CONFIG REWRITE
  SAVE
  REDIS
  EOF
  ```

---

## PHASE 4: Danny Agent Deployment (20 minutes)

### Test on Own Repo First (REQUIRED)

- [ ] Create test issue on openwebui-cli
  ```bash
  cd /home/setup/openwebui-cli  # or your test repo
  gh issue create --title "Test: Danny Agent Monitoring" --body "This is a test comment."
  ```

- [ ] Run monitoring script
  ```bash
  export GITHUB_REPO="dannystocker/openwebui-cli"
  bash /root/danny_agent/github_monitor_simple.sh
  # Check: Does danny respond? Is tone correct?
  ```

- [ ] Verify response quality
  - [ ] Read resume_message.txt
  - [ ] Review council output
  - [ ] Check gh issue comments for response
  - [ ] Confirm voice matches "British Direct" style

### Deploy to Production

- [ ] Option A: Cron job (every 30 minutes)
  ```bash
  # Add to crontab
  (crontab -l; echo "*/30 * * * * /root/danny_agent/github_monitor_simple.sh >> /var/log/danny_monitor.log 2>&1") | crontab -

  # Verify
  crontab -l | grep danny_monitor
  ```

- [ ] Option B: Systemd timer
  ```bash
  systemctl enable danny-monitor.timer
  systemctl start danny-monitor.timer
  systemctl status danny-monitor.timer
  ```

---

## PHASE 5: Claude Max API Server Setup (10 minutes)

- [ ] Deploy README to container 200
  ```bash
  scp /tmp/README-Claude-Max-API-Server.md root@85.239.243.227:/root/sergio_chatbot/
  ssh root@85.239.243.227 'ls -lh /root/sergio_chatbot/README-Claude-Max-API-Server.md'
  ```

- [ ] Add welcome message to .bashrc
  ```bash
  ssh root@85.239.243.227 << 'EOF'
  cat >> /root/.bashrc << 'BASHRC'
  # ═══════════════════════════════════════════════════════════
  # 🚀 CLAUDE MAX API SERVER - Quick Reference
  # ═══════════════════════════════════════════════════════════
  echo ""
  echo "📖 Quick Start: /root/sergio_chatbot/README-Claude-Max-API-Server.md"
  echo "🗄️  ChromaDB:   /root/sergio_chatbot/chromadb (123 embeddings)"
  echo "🐍 API Server: python3 claude_api_server_rag.py (port 3001)"
  echo ""
  BASHRC
  EOF
  ```

---

## PHASE 6: Corpus Files Sync (OPTIONAL - Already in ChromaDB)

**Status:** Already ingested in production ✅

- [ ] Verify JSONL files exist locally
  ```bash
  ls -lh /mnt/c/users/setup/downloads/psychology_corpus_output/*.jsonl
  # Should show: 9 files, ~1.7MB total
  ```

- [ ] If re-ingesting needed, source files are:
  - corpus_ingest.jsonl (307 citations)
  - corpus_ingest_with_guard.jsonl (307 + IF.Guard analysis)
  - [7 other specialized JSONL files]

---

## Success Criteria Checklist

### Documentation
- [ ] agents.md contains Danny v2.0 architecture (+504 lines)
- [ ] IF_EMOTION_COMPLETE_CORPUS_DOCUMENTATION.md in /home/setup/infrafabric/docs/
- [ ] Handover files archived to /home/setup/infrafabric/docs/session-archives/2025-12-01/
- [ ] SESSION_SUMMARY_2025-12-01_IF_EMOTION_CONSOLIDATION.md exists

### Databases
- [ ] ChromaDB: 123 embeddings verified (4 collections)
  - sergio_personality: 20
  - sergio_rhetorical: 5
  - sergio_corpus: 70
  - sergio_humor: 28
- [ ] Redis L1: Active and responding
- [ ] Redis L2: Authentication resolved (P1 blocker)

### Deployment
- [ ] Danny agent tested on own repo (openwebui-cli)
- [ ] Danny agent response quality verified
- [ ] Danny agent deployed (cron or systemd)
- [ ] Claude Max README deployed to container 200

---

## Estimated Time to Complete

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Documentation sync | 5 min | 🔵 Ready |
| 2 | ChromaDB verification | 10 min | ✅ Already verified |
| 3 | Redis L1/L2 status | 15 min | 🔴 P1 blocker |
| 4 | Danny agent deployment | 20 min | 🔵 Ready (test first) |
| 5 | Claude Max API setup | 10 min | 🔵 Ready |
| 6 | Corpus files sync | 5 min | ✅ Already ingested |
| **TOTAL** | | **~50 min** | **Ready to execute** |

---

## Quick Reference: Key Commands

### Verify Everything
```bash
# Documentation
grep -l "Danny GitHub Agent v2.0" /home/setup/infrafabric/agents.md
ls -lh /home/setup/infrafabric/docs/IF_EMOTION_COMPLETE_CORPUS_DOCUMENTATION.md

# ChromaDB (remote)
ssh root@85.239.243.227 'ls -lh /root/sergio_chatbot/chromadb/chroma.sqlite3'

# Redis L1
redis-cli PING

# Redis L2
redis-cli -h 85.239.243.227 -p 6380 AUTH @@Redis_InfraFabric_L2_2025$ PING

# Danny agent
ls -lh /root/danny_agent/github_monitor_simple.sh
tail -20 /var/log/danny_monitor.log
```

### Rollback Commands (if needed)
```bash
# Disable Danny agent cron
crontab -e  # Remove danny_monitor line

# Stop systemd timer
systemctl stop danny-monitor.timer

# Clear logs
rm /var/log/danny_monitor.log

# Revert agents.md (git)
cd /home/setup/infrafabric && git checkout HEAD -- agents.md
```

---

**Last Updated:** December 1, 2025
**Author:** Claude Max (Opus 4.5) - IF.emotion Consolidation Session
**Status:** READY FOR EXECUTION

---

**END OF CHECKLIST**
