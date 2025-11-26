# Restored S2 Snapshot

This directory contains a best-effort recovery from `infrafabric-all-branches-cleaned.tar.gz` (Downloads) to revive Series 2 swarm/logistics assets.

## Contents
- `src/core/logistics/parcel.py` — current IF.logistics Parcel implementation (seeded from live repo for runnable engine).
- `src/core/logistics/redis_swarm_coordinator.py` — recovered coordinator from `swarm-architecture/` (includes task queues, agent registry, context sharing).
- `src/core/governance/README.md` — note: `if_*` governance functions were not present in the cleaned archive.
- `src/integrations/broadcast/` — placeholders for SIP/H.323, vMix, NDI adapters (source missing in cleaned archive).
- `docs/case_studies/ROI_ANALYSIS.md` — summary of reported ROI; source case-study files missing from archive.

## Known Missing Artifacts
- `sip_h323_gateway.py`, `vmix_adapter.py`, `ndi_sip_bridge.py` (referenced in branch manifests, absent in cleaned tarball).
- `if_*` governance function definitions (if_ground, if_search, etc.).
- Case study docs: `if.instance.ep.17_twist-tale-swarm-awakening.md`, `v2_swarm_validation.md`.

## Next Steps
1. Recover missing adapter and governance sources from full git history or uncleaned archives.
2. Wrap coordinator writes/reads with Parcel custody headers and add signature enforcement.
3. Add hygiene (WRONGTYPE) guardrails and schema validation on bus payloads.
4. Wire broadcast adapters once sources are restored.
