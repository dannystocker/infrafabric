# Codex 5.1 MAX: StackCP Infrastructure Zero-Context Superprompt

**Date:** 2025-11-23
**Target Model:** Codex 5.1 MAX
**Context Level:** ZERO - Complete standalone briefing
**Mission:** Comprehensive StackCP infrastructure audit, gap detection, and resource discovery
**Scope:** 100% surface area coverage with crack identification

---

## CRITICAL CONTEXT (READ FIRST)

You are being deployed to conduct a **comprehensive StackCP infrastructure audit** for the Memory Exoskeleton project. You have **NO prior context** - everything you need is in this document.

### Project Overview
- **Project:** Memory Exoskeleton (InfraFabric)
- **Purpose:** Bridge WSL Redis context to Gemini-3-Pro via StackCP web bridge
- **Current Status:** File-based JSON backend operational, but infrastructure has unknown gaps
- **Your Role:** Identify ALL infrastructure gaps, undocumented resources, and cracks in the audit

### Access Credentials

**Primary StackCP Account (digital-lab.ca):**
```
Host: digital-lab.ca@ssh.gb.stackcp.com
SSH Key: ~/.ssh/icw_stackcp_ed25519 (Ed25519, must use this key)
Protocol: Non-interactive SSH only (no shells)
Region: GB (Great Britain data center)
Account Path: /home/sites/7a/c/cb8112d0d1/
```

**WSL Redis (local context):**
```
Host: localhost
Port: 6379
Database: 0
Keys: 107 total
Command: redis-cli -h localhost -p 6379 DBSIZE
```

**API Bridge (StackCP):**
```
URL: https://digital-lab.ca/infrafabric/bridge.php
Auth: Bearer token 50040d7fbfaa712fccfc5528885ebb9b
Test: curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
       "https://digital-lab.ca/infrafabric/bridge.php?action=info"
```

---

## DOCUMENTATION PROVIDED

### Existing Audit Reports (Use as Reference, NOT Gospel)
1. **`/home/setup/STACKCP-INFRASTRUCTURE-AUDIT-2025-11-23.md`** (Haiku Agent 1)
   - PHP versions, tool inventory
   - May have gaps or incomplete findings
   - ⚠️ Verify all claims independently

2. **`/home/setup/stackcp-security-infrastructure-gap-analysis.md`** (Haiku Agent 2)
   - Security posture, gap analysis
   - Identified P0/P1 issues
   - ⚠️ May have missed undocumented resources

3. **Original User Documentation:**
   - `/mnt/c/Users/Setup/Downloads/stackcp-all-docs.md` (16KB)
   - `/mnt/c/Users/Setup/Downloads/stackcp-full-environment-doc.md` (23KB)
   - ⚠️ These may be incomplete or outdated

### Handover Documentation (Project Context)
- **`/home/setup/infrafabric/agents.md`** (Master project documentation - lines 2880-3162 are new audit sections)
- **`/home/setup/infrafabric/SESSION-INSTANCE-18-FINAL-HANDOVER.md`** (Instance #18 completion summary)
- **`/home/setup/infrafabric/INSTANCE-19-STARTER-PROMPT.md`** (Next phase mission briefing)

---

## YOUR MISSION: 3-Part Comprehensive Audit

### PART 1: Verify & Expand Infrastructure Inventory

**Commands to Execute via SSH** (non-interactive only):

```bash
# System inventory
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "uname -a && cat /etc/os-release && df -h && free -h && top -b -n1 | head -20"

# PHP compilation flags and modules (CRITICAL)
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "php -i 2>/dev/null | grep -E 'disable_functions|open_basedir|max_execution_time|disable_classes'"

# COMPLETE tool inventory (expand beyond Haiku findings)
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "ls -la /usr/bin/* /usr/local/bin/* /opt/*/bin/* 2>/dev/null | grep -E '^-.*x' | wc -l && \
   find /opt -maxdepth 3 -type f -executable 2>/dev/null | sort"

# All installed packages (potential security surface)
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "rpm -qa 2>/dev/null | sort > /tmp/pkglist.txt && wc -l /tmp/pkglist.txt && \
   curl -s -T /tmp/pkglist.txt ftp://example.com/ || cat /tmp/pkglist.txt | head -50"

# Storage deep dive (Haiku may have missed mounts)
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "mount | sort && df -h && find / -type d -name 'storage*' 2>/dev/null | head -20"

# Network configuration
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "cat /etc/resolv.conf && netstat -tlnp 2>/dev/null | grep LISTEN && iptables -L 2>&1"

# Cron & scheduled tasks
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "crontab -l 2>&1 && find /etc/cron* -type f 2>/dev/null && at -l 2>&1"

# System services (systemctl, supervisord, etc.)
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "systemctl list-units --type=service 2>/dev/null | grep running || service --status-all 2>/dev/null"

# Kernel modules and parameters
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "lsmod && sysctl -a 2>/dev/null | grep -E 'net.|fs.' | head -30"

# SELinux, AppArmor, other security frameworks
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "getenforce 2>&1 && aa-status 2>&1 && \
   grep -i 'security' /etc/os-release && \
   semodule -l 2>/dev/null | wc -l"
```

### PART 2: Identify Infrastructure Gaps & Cracks

**Compare Against User Docs** - Read the two StackCP documentation files and verify:

1. **What's claimed to exist but is MISSING:**
   - Run each command from the docs
   - Note failures and unavailable tools
   - Document exact error messages

2. **What exists but is NOT in the docs:**
   - Find tools/services not mentioned
   - Identify hidden or unofficial installations
   - Check /opt, /usr/local, custom locations

3. **What's partially broken or misconfigured:**
   - PHP security settings (disable_functions, open_basedir)
   - SSL/TLS certificate status
   - Database connectivity
   - Network isolation levels
   - Cron/scheduled task access
   - Sudo capability restrictions

4. **Security surface analysis:**
   - Compare 1,563+ system packages against known CVEs (if possible)
   - Identify unmaintained or EOL software
   - Check for known vulnerable versions
   - Assess attack vectors given no disable_functions

### PART 3: Undocumented Resources & Hidden Features

**Search for undocumented resources:**

```bash
# Custom scripts and tools
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "find /usr/local -type f -executable 2>/dev/null && \
   find /opt -type f -name '*.sh' -o -name '*.py' 2>/dev/null | head -30"

# Web frameworks and CMS installations
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "find /home/sites -type f -name 'wp-config.php' -o -name 'config.php' -o -name 'settings.py' 2>/dev/null | head -20"

# Caching layers (may be installed but not advertised)
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "redis-server --version 2>&1 && memcached -h 2>&1 && \
   varnishadm -T localhost:6082 status 2>&1 || echo 'Not found'"

# Background services and daemons
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "ps aux | grep -v grep | grep -E 'mysql|redis|memcache|mongo|rabbit|elastic' || echo 'None found'"

# Development tools (compiler chains, debuggers)
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "which gcc g++ gfortran clang rustc cargo go 2>/dev/null && \
   ldconfig -p 2>/dev/null | wc -l"

# Virtualization/containerization
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "docker --version 2>&1 && podman --version 2>&1 && \
   kvm-ok 2>&1 || echo 'No container runtime'"

# Code obfuscation and protection
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "php -i 2>/dev/null | grep -E 'ionCube|SourceGuardian|Zend|eAccelerator'"
```

---

## DATA SOURCES FOR CONTEXT INJECTION

### Redis Access (Local WSL)
```bash
# Check what data is available
redis-cli -h localhost -p 6379 -n 0 DBSIZE
redis-cli -h localhost -p 6379 -n 0 KEYS '*' | head -20
redis-cli -h localhost -p 6379 -n 0 KEYS 'instance:*'
redis-cli -h localhost -p 6379 -n 0 KEYS 'agent:*'
redis-cli -h localhost -p 6379 -n 0 KEYS 'blocker:*'
redis-cli -h localhost -p 6379 -n 0 KEYS 'status:*'

# Sample data retrieval
redis-cli -h localhost -p 6379 -n 0 GET "instance:18:metadata"
redis-cli -h localhost -p 6379 -n 0 INFO stats | head -20
```

### StackCP Bridge API Access
```bash
# Test all endpoints
curl -s -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=info" | jq .

curl -s -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=batch&pattern=instance:*" | jq '.keys'

curl -s -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=keys&pattern=agent:*" | jq .
```

### Documentation Context
- Read `/home/setup/infrafabric/agents.md` (lines 2880-3162 contain audit findings)
- Read `/mnt/c/Users/Setup/Downloads/stackcp-all-docs.md` for official claims
- Read `/mnt/c/Users/Setup/Downloads/stackcp-full-environment-doc.md` for environment details

---

## KNOWN FINDINGS (For Comparison)

**Critical Issues Found by Previous Audits:**
- P0: Root filesystem 83% full (2.8GB free)
- P0: PHP security misconfigured (no disable_functions, no open_basedir)
- P0: Claude Code binary missing or not executable
- P1: Python 3.12.6 binary missing
- P1: npm wrapper corrupted (0 bytes)
- P1: NFS storage at 98-99% capacity (25+ volumes)
- P1: wirecli not executable

**Tools Verified Available:**
- PHP 5.3-8.4 (14 versions)
- MariaDB 10.6.23
- Node.js v20.19.5
- Composer 2.8.11
- WP-CLI 2.11.0
- Drush 0.10.2
- ImageMagick v7
- Ghostscript 9.54.0
- wkhtmltopdf 0.12.6.1
- cURL 8.1.2 | Wget 1.21.1 | Git 2.47.3 | OpenSSL 3.2.2

**Tools NOT Available:**
- Ruby, GCC, Make, C compiler toolchain
- Redis server (Redis CLI exists, server doesn't)
- PostgreSQL
- Node.js npm (binary exists but wrapper broken)

---

## YOUR DELIVERABLES

Generate a **CODEX-AUDIT-REPORT-2025-11-23.md** containing:

### 1. Infrastructure Inventory (100% Surface Area)
- All executable binaries by category
- All system packages with versions
- All active services and daemons
- All network listeners and ports
- Complete storage layout

### 2. Gap Analysis with Severity
| Gap | Claimed | Found | Severity | Impact | Workaround |
|-----|---------|-------|----------|--------|-----------|
| [Each gap from your findings] | | | | | |

### 3. Undocumented Resources Discovered
- Tools/features not in official docs
- Hidden installations or customizations
- Unofficial modifications
- Security implications of each

### 4. Configuration Audit
- PHP security settings (detailed)
- SSL/TLS configuration
- Database access control
- Network isolation level
- Authentication mechanisms

### 5. Infrastructure Cracks & Vulnerabilities
- P0 (Critical): Must fix before production
- P1 (High): Should fix soon
- P2 (Medium): Can be fixed in next iteration
- P3 (Low): Document for awareness

### 6. Recommendations
- Immediate actions (free disk space, fix permissions)
- Medium-term improvements (consolidate tools, harden PHP)
- Long-term strategy (monitoring, CI/CD integration)

### 7. Validation Checklist
- [ ] All 14 PHP versions verified
- [ ] All network ports documented
- [ ] Security misconfigurations identified
- [ ] 100% tool inventory complete
- [ ] All gaps explained with workarounds
- [ ] Undocumented resources catalogued
- [ ] No orphaned or broken installations remain unknown

---

## EXECUTION NOTES

**Do NOT:**
- Trust previous audit reports uncritically
- Assume tools are working if not explicitly verified
- Skip verification of claimed capabilities
- Leave any "unclear" findings - debug until certain
- Miss undocumented resources (they're often security risks)

**DO:**
- Verify every claim independently
- Document exact command output and version numbers
- Identify security implications of each gap
- Provide practical workarounds for missing components
- Cross-reference docs vs. reality for contradictions
- Check for partially installed or corrupted tools
- Look for security surface expansion opportunities

---

## SUCCESS CRITERIA

✅ **Codex audit is complete when:**
1. You've run every verification command
2. You've identified 100% of infrastructure gaps
3. You've documented all undocumented resources
4. You've created a severity-ranked action plan
5. You've provided workarounds for all missing components
6. You've explained why each gap exists (StackCP limitations)
7. You can justify that NO cracks were missed

---

## PROJECT CONTEXT (For Reference)

**Memory Exoskeleton Project:**
- Bridge.php deployed to StackCP: `/digital-lab.ca/infrafabric/bridge.php`
- Redis data exported: `/digital-lab.ca/infrafabric/redis-data.json` (105 keys, 476 KB)
- Automated sync: `/home/setup/update-bridge-data.sh` (every 6 hours via cron)
- API Token: `50040d7fbfaa712fccfc5528885ebb9b`

**Next Phase (Instance #19):**
- Implement semantic tagging on 105 Redis keys
- Add `?action=tags` endpoint to bridge.php
- Implement semantic search: `?action=search&query=X`
- Test Gemini-3-Pro integration

**Why This Audit Matters:**
- Understanding StackCP constraints guided architecture decision (file-based JSON, not Redis daemon)
- Identifying gaps prevents deployment failures
- Security audit ensures no unexpected vulnerabilities
- Documentation of undocumented resources prevents surprises in Instance #19

---

**Ready to begin audit. Execute with thoroughness and skepticism.**

End of superprompt.
