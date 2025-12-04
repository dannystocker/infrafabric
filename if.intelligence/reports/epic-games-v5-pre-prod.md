# Epic Games V5 – Pre-Prod Handoff

Date: 2025-12-03  
Owner: IF.intelligence (Epic Games V5 Mission)  
Status: Pre-production (pipeline scaffolded; data ingest blocked on Reddit 403; other collectors pending)

## 1) Current Assets (Repo + Proxmox)

- Mission prompt: `intelligence-missions/EPIC_GAMES_V5_MISSION_PROMPT.md` (≈1,112 lines)  
- IF.TTT paper (v2.2, voice-polished; includes S2 + production case studies Epic/Gedimat):  
  - Repo: `docs/papers/IF_TTT_THE_SKELETON_OF_EVERYTHING.md`  
  - Copy: `C:\Users\Setup\Downloads\IF_TTT_THE_SKELETON_OF_EVERYTHING_v2.2.md`
- Epic Games V5 pipeline (Proxmox 85.239.243.227):  
  - Base: `/root/intelligence-pipelines/epic_games/`  
  - Subdirs: `chromadb/` (has `chroma.sqlite3`), `collectors/` (has `run_all.py`), `analysis/`, `reports/`, `venv/`
- Collector script: `/root/intelligence-pipelines/epic_games/collectors/run_all.py`  
  - Shebang points to venv: `#!/root/intelligence-pipelines/epic_games/venv/bin/python`  
  - Venv packages verified: `chromadb 1.3.5`, `requests 2.32.5`

## 2) What Was Done

- Added S2 Swarm-to-Swarm IF.TTT protocol + Production Case Studies (Epic V4, Gedimat) to the IF.TTT paper; renumbered sections; Voice Polish v2.2 applied.
- Authored full Epic Games V5 mission prompt (30+ guardian council, 40+ Haiku swarm, IF.optimise/Redis comms).
- Scaffolded Proxmox pipeline: directories created; ChromaDB initialized; `run_all.py` orchestrator created.
- Test run of `run_all.py` (with venv) executed; collections created; Reddit collection attempts returned 403 (blocked).

## 3) Current Issues

- **Reddit ingestion blocked (403)** on r/FortNiteBR, r/FortniteCreative, r/unrealengine, r/EpicGamesPC via old.reddit.com JSON (no auth).
- **Collections empty**: epic_forums, epic_legal, epic_financials, epic_products, epic_competitive, epic_hr_culture, epic_live_events all count=0.
- **Other collectors** (legal/financial/competitive/HR/live_events) not yet implemented; only Reddit stub exists.

## 4) Next Actions (pre-prod → prod)

1. **Fix Reddit ingest**: use OAuth (PRAW or requests with client id/secret) or alternate sources (Pushshift/other aggregators); rerun `run_all.py`.
2. **Implement additional collectors**:
   - Legal: PACER, USPTO, FTC/EU/UK filings  
   - Financial: investor decks, analyst reports, press releases  
   - Competitive: SteamDB, Unity, Roblox, Apple/Google app store data  
   - HR/Culture: Glassdoor, LinkedIn, layoffs news  
   - Live Events: esports/concerts/brand activations (Esports Charts, Twitch stats)
3. **Rerun ingest** using venv:  
   - `/root/intelligence-pipelines/epic_games/collectors/run_all.py`  
   - Or: `/root/intelligence-pipelines/epic_games/venv/bin/python /root/intelligence-pipelines/epic_games/collectors/run_all.py`
4. **Verify counts** after ingest (example snippet in venv):  
   ```bash
   /root/intelligence-pipelines/epic_games/venv/bin/python - <<'PY'
   import chromadb
   client = chromadb.PersistentClient("/root/intelligence-pipelines/epic_games/chromadb")
   for name in ["epic_forums","epic_legal","epic_financials","epic_products","epic_competitive","epic_hr_culture","epic_live_events"]:
       c = client.get_or_create_collection(name=name)
       print(name, c.count())
   PY
   ```
5. **Run full V5 swarm** (after data present) per mission prompt; enforce IF.TTT self-assessment (traceable/transparent/trustworthy; variance/confidence; falsifiable predictions; dissent preserved).
6. **Store outputs** per mission prompt (exec summary, full narrative, data appendix, decision tree, dissent report) and note paths in a handoff.

## 5) Quick Commands (Proxmox)

- Check pipeline dirs: `ssh root@85.239.243.227 'ls -la /root/intelligence-pipelines/epic_games'`
- Run orchestrator: `/root/intelligence-pipelines/epic_games/collectors/run_all.py`
- Query counts (see snippet above).

## 6) References

- Epic V4 report (TTT 5.0/5): `C:\Users\Setup\Downloads\EPIC-GAMES-NARRATIVE-INTELLIGENCE-REPORT.md`
- V4 prompt: `C:\Users\Setup\Downloads\CLAUDE_V4_EPIC_COMPREHENSIVE_PROMPT.md`
- Gedimat case study: `C:\Users\Setup\Downloads\GEDIMAT_ARENA_REVIEW_COMPLETE_V3.2.md.txt`
- IF.TTT paper v2.2: `docs/papers/IF_TTT_THE_SKELETON_OF_EVERYTHING.md`

## 7) Status Snapshot

- Pipeline reachable; venv healthy; `run_all.py` executable.  
- Ingest blocked on Reddit 403; collections currently empty.  
- Mission prompt ready; IF.TTT paper updated with Epic/Gedimat case studies and S2 protocol.

## 8) Approach & Gaps (for the definitive report)

**Current approach (good):**
- Define full surface area (platform vs. content, Fortnite/Unreal/EGS, legal/regulatory, competitive, financials, HR/culture, community sentiment, live events, contrarian/historical).
- Swarm expansion (Financial, Competitive, Product/Tech, Market/Culture, Contrarian/Historical) + Guardian Council for synthesis/dissent.
- Ingest → index → query → analyze (ChromaDB as evidence spine).
- IF.TTT discipline: multi-source, variance/confidence, falsifiable predictions, dissent preserved.

**Gaps / risks:**
- Ingestion incomplete: Reddit blocked; no collectors yet for legal/financial/competitive/HR/live_events; collections empty.
- No coverage tracker: surface is defined but not monitored for completeness (which sources are live/stale/failing).
- Ingest hygiene: no dedup/quality checks; no PII/terms compliance guardrails.
- Source stability: no versioning/snapshots in metadata (risk of drift if sources change).
- Orchestration: no explicit runbook for when to run collectors vs. freeze ingest vs. run swarm.

**Recommendations to close gaps:**
1. Fix ingest robustness:
   - Implement Reddit OAuth (or Pushshift/alternative) to unblock `epic_forums`.
   - Add collectors: legal (PACER/USPTO/FTC/EU/UK), financial (decks/analysts/press), competitive (SteamDB/Unity/Roblox/app stores), HR/culture (Glassdoor/LinkedIn), live events (esports/concerts/Twitch stats).
   - Add dedup/quality filtering; store URLs/hashes/timestamps in Chroma metadata.
2. Add a coverage tracker (YAML/JSON) listing sources per collection with status {planned|live|failing|stale}, last-run, doc counts.
3. Orchestrate runs:
   - Run collectors via venv; once populated, freeze ingest for analysis; then run full V5 swarm per mission prompt.
   - After swarm, unfreeze ingest for refresh cycles.
4. Reporting discipline:
   - Use IF.TTT self-assessment in each section (traceable/transparent/trustworthy scores; variance/confidence; falsifiable predictions; dissent).
   - Include customer feedback/pain points from forums once ingested; summarize themes with counts.
   - Provide bull/base/bear projections with triggers to upgrade/downgrade.
