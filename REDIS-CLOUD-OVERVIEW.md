# Redis Cloud Context & Comms Overview
**Date:** 2025-11-24  
**Audience:** External reviewers (no prior context)  
**Scope:** How the Memory Exoskeleton uses Redis Cloud for context and inter-agent comms, current state, lineage, and known risks.

---

## Architecture (Today)
- **Data plane:** Redis Cloud (db0) at `redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com:19956` (TCP), user `default` + password (shared securely). 290+ keys; majority expiring (~30 days), remainder permanent.
- **Public API:** `bridge.php` v2.0 on StackCP (`https://digital-lab.ca/infrafabric/bridge.php`) with Bearer auth (`50040d7fbfaa712fccfc5528885ebb9b`).
- **Sync pattern:** Cron-friendly PHP sync (`sync_cloud.php`) pulls *all* Redis Cloud keys (strings, hashes, lists, sets, zsets; TTL preserved) to `redis-data.json` on StackCP. Bridge reads this JSON when direct cloud access is blocked.
- **Semantic tags:** `redis-semantic-tags.json` alongside `redis-data.json` for search/tag endpoints.
- **Access model:**
  - Web clients → `bridge.php` (Bearer) → file snapshot (`redis-data.json`) or Redis Cloud if egress is allowed.
  - SSH tier can reach Redis Cloud directly (verified via Predis/redis-cli).

---

## Current State (2025-11-24)
- **Key count:** 324 after latest sync (chronicles added). `context:instance0:*` = 26 keys with ~30-day TTL remaining.
- **Data export:** `redis-data.json` ~9.6 MB (latest sync timestamp embedded in the file).
- **Snapshot on Windows:** `C:\Users\Setup\Downloads\redis-cloud-export.tar.gz` (contains `redis-data.json`).
- **Bridge status:** Reports `backend: redis-cloud` but still surfaces `redis_cloud_error` because the web/PHP worker outbound to port 19956 is blocked. File snapshot is current and served.
- **TTL horizon:** Many context keys (incl. Instance 0, chronicles) expire ~2025-12-24; some queue/meta keys are non-expiring.

---

## Chronological Progress (Condensed)
1) **Local-only Redis (Instances 0–12):** Context lived on WSL Redis; StackCP couldn’t reach localhost. Early proxy attempts (PHP/Node) blocked by shared-hosting isolation and missing redis-cli.
2) **Bridge v1.1 → v2.0:** Added REST bridge with Bearer auth; later extended for semantic search/tags. Still file-backed (`redis-data.json`) due to network limits.
3) **Redis Cloud adoption (Instance 19+):** Staged a cloud backend to bypass StackCP isolation. Migrations increased key count to 290+, with 30-day TTL policy for most context.
4) **Sync hardening:** Deployed lossless `sync_cloud.php` on StackCP (type-aware, TTL-preserving, backups) and refreshed `redis-data.json` from cloud; added chronicles (36 files) to Redis.
5) **Outstanding:** Web-tier egress to Redis Cloud still blocked; continuity tests across instance boundaries intentionally unrun in narrative but remain an infra gap if required.

---

## Endpoints (Bridge v2.0)
- `?action=info` → status, backend, key counts, tag stats, and cloud error (if any).
- `?action=keys&pattern=*` → key listing with glob pattern.
- `?action=batch&pattern=*` → fetch matching entries.
- `?action=tags&pattern=*` → semantic tags.
- `?action=search&query=...&semantic=true` → semantic search (uses tags if present).
- `?action=health` → existence/size of data/tag files.

---

## Known Issues / Risks
- **Web egress blocked:** Bridge cannot talk to Redis Cloud directly; relies on the synced JSON. Fix: allowlist StackCP web egress IP(s) on Redis Cloud (known SSH egress: 45.8.227.175; web tier may differ).
- **TTL expiry:** Majority of context expires around 2025-12-24. Mitigate by removing/refreshing TTLs for critical keys.
- **Snapshot only:** If `sync_cloud.php` fails, bridge serves stale data. Add monitoring and last_sync metadata to `info` for visibility.
- **Continuity untested:** No automated “new instance remembers” test has been run; this is deliberate in narrative but an infra gap if continuity is required.
- **Namespace hygiene:** Mixed key namespaces; consider a canonical index for discoverability.

---

## Recommendations
1) **Open cloud egress** for the web tier or keep frequent syncs (StackCP “Scheduled Tasks”) to ensure `redis-data.json` stays fresh.
2) **Pin critical keys** (remove TTL) or refresh before Dec 24.
3) **Expose sync metadata** (last_sync, dbsize, checksum) via `info` to aid ops/debugging.
4) **Add indexes** (e.g., `index:chronicles`, `index:context`) for discoverability.
5) **Post-narrative:** add a continuity integration test once the cliffhanger is resolved.

---

## Files & Locations
- StackCP: `~/public_html/digital-lab.ca/infrafabric/bridge.php`, `redis-data.json`, `redis-semantic-tags.json`, `sync_cloud.php`, `predis/`.
- Local snapshot: `/home/setup/redis-data.json` (latest) → `C:\Users\Setup\Downloads\redis-cloud-export.tar.gz`.
- Docs: `infrafabric/agents.md` (session summaries), Council Chronicles (STORY-*.md), redis reports (`REDIS-CLOUD-MIGRATION-COMPLETION-2025-11-23.md`, etc.).
