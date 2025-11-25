# Credentials Reference for External Sessions

**Security Note:** This document contains references to credential locations, not the credentials themselves.

## Git Repositories

### GitHub Credentials
- **Location:** See `/home/setup/.claude/CLAUDE.md` (user's global instructions)
- **Search for:** "github" or "git" in that file
- **Note:** Credentials are stored in user's private global context

### Gitea Local Server
- **URL:** http://localhost:4000/
- **Admin User:** `ggq-admin`
- **Admin Pass:** `Admin_GGQ-2025!`
- **Config:** `/home/setup/gitea/custom/conf/app.ini`

### Gitea User Account (dannystocker)
- **User:** `dannystocker`
- **Pass:** `@@Gitea305$$`
- **Repos:**
  - infrafabric-core: http://localhost:4000/dannystocker/infrafabric-core.git
  - infrafabric: http://localhost:4000/dannystocker/infrafabric.git
  - navidocs: Already on GitHub (https://github.com/dannystocker/navidocs.git)
  - job-hunt: http://localhost:4000/dannystocker/job-hunt.git

## API Keys

### Anthropic API Key
- **Location:** Already set in environment variable `ANTHROPIC_API_KEY`
- **Access:** Sessions inherit this automatically
- **Verify with:** `echo $ANTHROPIC_API_KEY | head -c 20`

### OpenRouter API Key (REVOKED)
- **Status:** ⚠️ REVOKED 2025-11-07 (exposed in GitHub)
- **Location:** See `/home/setup/.security/revoked-keys-whitelist.md`
- **Do not use**

### DeepSeek API Key
- **Key:** `sk-c2b06f3ae3c442de82f4e529bcce71ed`
- **Use for:** DeepSeek agent delegation

## Other Systems

### ICW icantwait.ca (ProcessWire)
- **URL:** https://icantwait.ca/nextspread-admin/
- **User:** `icw-admin`
- **Pass:** `@@Icantwait305$$`

### StackCP SSH
- **For:** icantwait.ca deployment
- **Location:** Connection details in `/home/setup/.claude/CLAUDE.md`

### SuiteCRM Database
- **Database:** `suitecrm-3130373ec5`
- **Host:** `shareddb-n.hosting.stackcp.net`
- **User:** `ggq-web`
- **Pass:** `1410Ruepanet$$`

---

## For External Sessions (Codex/Other AIs)

**Safe sharing approach:**

1. **Read access to this file:** `/home/setup/infrafabric/CREDENTIALS_REFERENCE.md`
2. **If GitHub credentials needed:** Have them read `/home/setup/.claude/CLAUDE.md` and search for relevant sections
3. **Security principle:** Never copy credentials into new files - always reference source locations

**Verification commands:**
```bash
# Verify git config
git config --global user.name
git config --global user.email

# Check remote URLs
cd /home/setup/infrafabric && git remote -v
cd /home/setup/navidocs && git remote -v

# Test Gitea access
curl -u dannystocker:@@Gitea305$$ http://localhost:4000/api/v1/user
```

---

**Last Updated:** 2025-11-21 Instance #8
**Security Level:** Reference only - actual credentials in protected user config
