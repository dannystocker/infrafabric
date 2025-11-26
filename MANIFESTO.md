# THE INFRAFABRIC CODEX (v2.0)
**Rigorous Research. Joyfully Implemented.**

## I. THE REPO STRATEGY
**"One Core, Many Satellites."**

1. **InfraFabric (This Repo):** The Monolith. Contains the `core` logic, the `sim` engine, and the `state` definitions.  
   *Formerly:* `infrafabric-core` (Folded).
2. **Navidocs (Satellite):** The Consumer. Uses `infrafabric` to generate documentation.
3. **Branches:** We do not merge legacy branches. We mine them for diamonds and recut them in `src/`.

## II. THE BUILD SYSTEM
**"We use `uv`."**  
We do not use `pip` manually. We do not use `conda`. We use `uv` for lightning-fast, hermetic builds.
- Setup: `just setup`
- Run: `just train`

## III. THE LAW OF STATE (REDIS)
**"No Schema, No Write."**  
The database is not a scratchpad.
- **The Sin:** Writing raw strings or error messages ("WRONGTYPE") into keys.
- **The Law:** All Redis writes must be validated via `src/infrafabric/state/schema.py`.

## IV. THE FUNCTIONAL CORE
**"Logic flows; State is carried."**
- **Logic:** Pure JAX functions.
- **Config:** Pydantic models. No magic numbers.

---
**Verified by:** InfraFabric Council (Series 2)
