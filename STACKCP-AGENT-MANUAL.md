# STACKCP-AGENT-MANUAL.md

**Role:** System Operations & Execution Guide
**Environment:** StackCP (Shared Linux Hosting)
**Target Audience:** AI Agents (Claude Code, Gemini, Codex)
**Primary Constraint:** `noexec` on `$HOME` / `exec` on `/tmp`

---

## 1. THE PRIME DIRECTIVE (Security Constraints)

This system has a strict security architecture. Agents must follow these rules to execute code successfully.

1. **HOME (`~/`) is for STORAGE only.**
   - **Status:** `RW-` (Read/Write, NO EXECUTE).
   - **Use for:** `.env` files, databases, logs, source code repositories, HTML content.
   - **NEVER:** Attempt to run `./script.sh` or `npm install` directly inside `~/`.

2. **TMP (`/tmp/`) is for EXECUTION.**
   - **Status:** `RWX` (Read/Write/Execute).
   - **Persistence:** Persistent across reboots (unlike standard Linux).
   - **Use for:** Binaries (node, python, claude), compiling, installing `node_modules`.
   - **ALWAYS:** Move scripts here if they need to run.

---

## 2. THE TOOLBELT (Binary Paths)

Do not assume standard paths (`/usr/bin/node`). Use these explicit absolute paths.

| Tool | Capability | Absolute Path / Command |
| :--- | :--- | :--- |
| **Node.js** | JS Runtime (v20) | `/tmp/node` |
| **NPM** | Package Manager | `/tmp/npm` (Custom Wrapper) |
| **NPX** | Package Runner | `/tmp/npx` (Custom Wrapper) |
| **Python** | Python 3.12 | `/tmp/python-headless-3.12.6-linux-x86_64/bin/python3` |
| **Pip** | Python Pkg Mgr | `/tmp/pip312` |
| **Claude** | AI Agent CLI | `/tmp/claude` |
| **Meilisearch** | Vector/Search | `/tmp/meilisearch` (Port 7700) |
| **Redis** | Memory Store | *Via PHP Bridge* (See Section 4) |

---

## 3. EXECUTION PROTOCOLS

### Protocol A: Running Node.js Applications

Because `~/` is non-executable, you cannot simply run `npm start` in a home directory.

**Correct Workflow:**

1. Copy project to `/tmp` (or clone it there).
2. Install dependencies in `/tmp`.
3. Symlink persistent data (databases/uploads) back to `~/`.

```bash
# Example: Deploying a Node App
cd /tmp
git clone <repo> my-app
cd my-app
/tmp/npm install
# Run using the absolute node path
/tmp/node server.js
```

### Protocol B: Running Python Scripts

Virtual environments in `~/` will fail because the binaries inside them cannot execute.

**Correct Workflow:**
Use the global persistent Python in `/tmp` and install packages there.

```bash
# Install package
/tmp/pip312 install requests pandas

# Run script
/tmp/python-headless-3.12.6-linux-x86_64/bin/python3 my_script.py
```

### Protocol C: Updating Claude Code

If Claude acts buggy or the session hangs, force an update.

```bash
# 1. Kill any hung processes
pkill claude

# 2. Run the updater (Safe & Automated)
/tmp/updateclaude

# 3. Check logs
tail -n 10 ~/updateclaude.log
```

---

## 4. MEMORY EXOSKELETON ACCESS (The Neural Bridge)

This environment is "air-gapped" from the external Redis Cloud. To access or update the project's long-term memory (Redis), you must use the internal HTTP Bridge.

- **Bridge URL:** `https://digital-lab.ca/infrafabric/bridge.php`
- **Auth:** Requires Bearer Token (Check `.env` or `config` for specific agent keys).

### Reading Memory (Context Injection)

To fetch context *before* answering a user query:

```bash
# CLI Example
curl -s -H "Authorization: Bearer <SECRET>" \
     "https://digital-lab.ca/infrafabric/bridge.php?action=get&key=instance:16:session-narration"
```

### Writing Memory (State Saving)

To save a session summary or architectural decision:

```bash
# CLI Example (Keys/Values must be encoded)
# Note: Complex writes should be done via the Python API wrapper if available
curl -X POST -H "Authorization: Bearer <SECRET>" \
     -d "key=instance:17:decision:api-standard&value=Using JSON-RPC" \
     "https://digital-lab.ca/infrafabric/bridge.php?action=set"
```

---

## 5. TROUBLESHOOTING CHEATSHEET

**Error:** `bash: ./script.sh: Permission denied`
- **Cause:** You are trying to execute in `~/`.
- **Fix:** `cp script.sh /tmp/ && /tmp/script.sh`

**Error:** `/usr/bin/env: 'node': No such file or directory`
- **Cause:** Script uses shebang `#!/usr/bin/env node` but PATH is restricted.
- **Fix:** Run explicitly with `/tmp/node script.js`.

**Error:** `Another update is already running`
- **Cause:** `updateclaude` was interrupted.
- **Fix:** `rm /tmp/claude-update.lock` and retry.

**Error:** `Redis connection refused`
- **Cause:** Trying to connect to port 6379 directly.
- **Fix:** Use the `bridge.php` HTTP endpoint defined in Section 4.

---

*End of Agent Manual. Updated: 2025-11-23*
