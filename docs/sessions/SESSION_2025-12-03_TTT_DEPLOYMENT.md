# Session: IF.TTT Registry Deployment
**Date:** 2025-12-03
**Duration:** ~2 hours
**Model:** Claude Opus 4.5

---

## Summary

Prepared IF.TTT Registry for deployment on Proxmox container 201. Multi-AI collaboration (Claude + Grok + Gemini) to debug and harden the deployment.

---

## What Was Done

### 1. Redis Protocol Cleanup (Continued from Previous Session)
- Previous session claimed 135 replacements but deprecated names persisted
- Found deprecated protocols in **HASH fields** (not simple strings)
- Fixed: `IF.WWWWWW` (62) and `IF.LOGISTICS` (1) in Redis Cloud

### 2. IF.TTT Deployment Prompt Evolution
- **v4:** Initial portable version with DHCP
- **v5:** Added all discovered Proxmox context
- **v5.1 FINAL:** Incorporated Grok/Gemini fixes

### 3. Cross-AI Debugging Session
| AI | Contribution |
|----|-------------|
| **Claude** | Initial architecture, portability, CLI tools |
| **Grok** | iptables fixes (PREROUTING, MASQUERADE, FORWARD) |
| **Gemini** | Crypto fixes (real Ed25519 not fake), Redis locking, appendfsync |

### 4. Proxmox Infrastructure Verified
- IP forwarding enabled
- General MASQUERADE rule working
- Container 200 port forwarding pattern confirmed
- Stale KDE container (201) rules cleaned up
- Debian 13 is testing (unstable) - use Debian 12

### 5. Networking Reality Discovered
- Container 200 IP (85.239.243.230) is a **routed /32** not DHCP lease
- DHCP for new container 201 uncertain on Contabo
- Migration to Servarica tomorrow will have different network

---

## Files Created/Modified

| File | Action |
|------|--------|
| `CODEX_TTT_DEPLOYMENT_v5.1_FINAL.txt` | Created (Windows Downloads) |
| `CODEX_TTT_PORTABLE_v4.txt` | Created (superseded by v5.1) |
| `agents.md` | Updated to v1.7 with TTT entry |
| Proxmox iptables | Cleaned stale KDE rules |

---

## Key Decisions

1. **DHCP for portability** - Container uses DHCP, not static IP
2. **Debian 12** - Stable, not Debian 13 (testing)
3. **appendfsync everysec** - 40k writes/sec vs 40 writes/sec with `always`
4. **Ed25519 real signatures** - Not fake `unsigned:...` strings
5. **Redis lock** - Prevents concurrent write race conditions
6. **Isolated container** - TTT in pct 201, not pct 200

---

## Pending/Handover

### For Codex
Execute `CODEX_TTT_DEPLOYMENT_v5.1_FINAL.txt` to deploy TTT Registry.

**Potential Issue:** DHCP may not work if Contabo hasn't allocated additional IPs. Fallback: use NAT with private IP or check Contabo control panel.

### For Tomorrow (Servarica Migration)
1. Backup container 201: `vzdump 201 --storage local --compress zstd`
2. Transfer to new server
3. Restore and run `/root/ttt-reconfigure.sh`
4. Update WSL `TTT_HOST` environment variable

### For Next Claude Session
- Verify TTT deployment if Codex completed it
- Test remote CLI from WSL
- Add first real citation to the chain
- Plan TTT integration with other IF.* protocols

---

## Learnings

1. **Previous session work doesn't always persist** - Redis cleanup was reported done but deprecated names still existed
2. **Multi-AI collaboration works** - Each AI caught different issues
3. **iptables debugging requires testing** - Theory isn't enough, verify actual rules
4. **Debian stable vs testing matters** - Don't use testing for production compliance systems

---

## IF.TTT Quick Reference

```bash
# Inside container 201
ttt stats
ttt add "Claim text" '{"evidence":"json"}'
ttt verify
ttt head
ttt recent 5
ttt export /tmp/backup.json

# From WSL (after setup)
ttt-cli ping
ttt-cli stats
ttt-cli add "Remote claim" '{"source":"wsl"}'
ttt-cli verify
```

---

IF.citation: if://session/2025-12-03-ttt-deployment
