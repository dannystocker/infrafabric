# Claude WebCLI Debug Report (StackCP)  
**Date:** 2025-11-25  
**Audience:** External (Gemini-3-Pro-Web) – in-depth technical handover

---

## TL;DR
- Binary (`claude-code`, md5 `950800f52a84cc925b3436099de2d9ff`, size 209,514,315 bytes) executes fine via SSH: `2.0.51 (Claude Code)`.
- Web execution still fails: `/tmp/claude-web-...: failed to map segment from shared object` or `Permission denied`.
- Copies to `/tmp` succeed; checksums match; debug log records successful copy/MD5. The failure occurs only when PHP/FPM tries to exec the ELF.
- Likely cause: execution restrictions in the web PHP context (shared hosting sandbox), not binary corruption.

---

## Current Code (v2.7 attempts)
- Location: `~/public_html/digital-lab.ca/claude/index.php`
- Changes:
  - Copies binary to `/tmp/claude-web-<rand>` via `cp`; chmod 755; md5 verify.
  - Logs to `~/public_html/digital-lab.ca/claude/debug.log`.
  - Attempts to execute via loader or bash wrapper (latest state: helper pattern wired, but helper cannot bind/listen on StackCP).

## Binary Health
- Path: `~/public_html/digital-lab.ca/claude/claude-code`
- Permissions: currently 755 (set manually)
- MD5: `950800f52a84cc925b3436099de2d9ff`
- Size: 209,514,315 bytes
- SSH test: `cp claude-code /tmp/test-claude && chmod 755 && /tmp/test-claude --version` → `2.0.51 (Claude Code)`

## Debug Log Excerpts (~/public_html/digital-lab.ca/claude/debug.log)
```
[2025-11-25T07:17:03+00:00] Copy cmd rc=0 … target=/tmp/claude-web-e031…
[2025-11-25T07:17:04+00:00] md5 src=950800f52a84cc925b3436099de2d9ff dst=9508… target=/tmp/claude-web-e031…
[2025-11-25T07:17:04+00:00] Using cmd: /lib64/ld-linux-x86-64.so.2 /tmp/claude-web-e031…
[2025-11-25T08:56:02+00:00] Copy cmd rc=0 out= target=/tmp/claude-web-37efd…
[2025-11-25T08:56:02+00:00] md5 src=9508… dst=9508… target=/tmp/claude-web-37efd…
[2025-11-25T08:56:02+00:00] Using cmd: /bin/bash -lc 'LD_LIBRARY_PATH='/tmp' '/tmp/claude-web-37efd…' -p '
```
Despite these, the web response remains a mapping error/permission denied.

## Observed Failures (Web)
- Hitting `https://digital-lab.ca/claude/?stream_command=version` after login returns:
  - `/tmp/claude-web-<rand>: failed to map segment from shared object`
  - Or `Permission denied` in some iterations.
- Indicates that even after a verified copy to `/tmp`, PHP/FPM cannot map/exec the ELF.

## Environment Notes
- Web PHP temp: `/tmp`
- `/dev/shm` and `/var/tmp` are available but didn’t resolve the mapping error.
- Shared hosting (StackCP) likely enforces execution restrictions in the PHP context (CloudLinux/cagefs/suphp policy).

## Attempts Made
1) cp + md5 copy to /tmp, execute via loader → fail (mapping error).
2) Direct exec of source binary → fail (permission denied).
3) Bash wrapper (`/bin/bash -lc 'LD_LIBRARY_PATH=/tmp …'`) → fail (permission denied).
4) Helper pattern sketched (PHP calling local HTTP helper on 127.0.0.1:18081) but helper not running on StackCP (startup issues).

## What Works
- SSH execution as user `digital-lab.ca` runs the binary without issue.
- File copies and checksums from PHP succeed; permissions are set to 755.

## Likely Root Cause
Web/PHP context is sandboxed from executing custom ELF binaries, even in `/tmp`, despite exec bit and matching MD5. This is consistent with shared hosting execution policies.

## Proposed Paths Forward
**A) Helper Service (if allowed):**
- Run a small local helper (Python/Node) as the SSH user that listens on 127.0.0.1 and executes the binary. **Attempted**: helper script deployed to `/tmp/claude-helper.py` and started; `ss -tlnp` shows no listener, and `curl 127.0.0.1:18081` from host is refused. Likely blocked from binding userland daemons in the shared hosting environment.

**B) SSH Relay:**
- From PHP, SSH back to the same account (or localhost) to run the binary, then relay output. **Blocked**: sshd is not listening on localhost (`ssh localhost` from host → connection refused), so this relay is not available without provider changes.

**C) Provider Confirmation:**
- Confirm with StackCP whether PHP-FPM/CGI is permitted to exec custom ELF. If not permitted, the web UI must proxy to a runner outside the PHP sandbox.

## Evidence for External Debugger
- Binary integrity confirmed (md5/size) and executable via SSH.
- Debug logs show copy + checksum success and the exact command used.
- Web output consistently fails at exec time with mapping/permission errors.
- Helper attempt: `/tmp/claude-helper.py` started (PID visible) but no listener (`ss -tlnp` empty), and `curl 127.0.0.1:18081` from host is refused. Likely prohibited by hosting policies.

## Files of Interest
- Web: `~/public_html/digital-lab.ca/claude/index.php` (v2.7 attempts)
- Binary: `~/public_html/digital-lab.ca/claude/claude-code`
- Log: `~/public_html/digital-lab.ca/claude/debug.log`
- (Attempted) helper: `/tmp/claude-helper.py` (may not be running)

## Minimal Repro (Web)
```
# Login
curl -c /tmp/claude-cookies.txt -s -d "password=%40%40Claude305%24%24&login=1" https://digital-lab.ca/claude/
# Trigger
curl -b /tmp/claude-cookies.txt -s "https://digital-lab.ca/claude/?stream_command=version"
```
Expected: Binary runs and prints version.
Actual: Mapping/permission error.

---

## Ask for Gemini-3-Pro-Web
- Determine if PHP-FPM on StackCP is allowed to exec user ELF at all. If not, recommend a supported proxy pattern (local daemon or remote runner).
- If allowed, identify why mapping fails despite correct permissions and MD5 (e.g., mount options, cagefs, seccomp).
- Validate whether a localhost-bound helper service is permissible and how to keep it running on StackCP.
