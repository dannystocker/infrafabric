# Prompt Redevelopment Panel Transcript

**Participants**
- Dr. Lila Moreau — Prompt Architect (Strategy & Structure)
- Prof. Matteo Ruiz — Context Infusion Specialist (Data Grounding)
- Dr. Hana Villeneuve — Validation Strategist (Success Criteria)

**Context Review**
- Assets examined: `ICW_Complete_Data.csv`, `all-bookings.enriched-v4.csv`, `ICW_Logo.png`, `Montreal_night.jpg`
- Current demo spacing issues observed in `final-desktop-full.png`, `final-desktop-properties.png`, `final-mobile-full.png`
- Live media library verified via `https://icantwait.ca/wp-json/wp/v2/media`

---

**Discussion**

**Dr. Moreau:** The original prompt is trying to cover expert analysis, implementation, testing, and branding simultaneously. We need a phased instruction set with checkpoints so the agent doesn't skip verification. I'd split the brief into *Data Integration*, *Design Refinement*, and *Validation* blocks.

**Prof. Ruiz:** Agree, but we must explicitly bind the prompt to provided datasets. The CSVs describe 12 ICW rentals and their photo filenames. Our prompt should force lookup against the WordPress media API before using any image. Otherwise we risk reintroducing stock photos, which the user forbade.

**Dr. Villeneuve:** Both good points. I also want measurable success criteria—spacing values, specific lazy-loading behaviour, review sourcing. Without these, "world-class" remains subjective.

**Dr. Moreau:** Here's my draft structure: *Context*, *Resources*, *Red Lines*, *Deliverables*, *Validation Pipeline*. Each section should be bullet-driven so no detail gets lost.

**Prof. Ruiz:** Let's make sure "Resources" includes derived artefacts, like the media lookup generated from `/wp-json/wp/v2/media`. And remind the agent to map `PhotoNames` entries to `source_url` values.

**Dr. Villeneuve:** Under "Validation Pipeline" let's mandate automated spacing inspection (Playwright MCP or manual measurement), accessibility checks, and manual confirmation that every image URL resolved (HTTP 200). Also add a requirement to publish debate transcripts before implementation, per client's request.

**Dr. Moreau:** Agreed. Here's the consensus prompt—we state *"Do not execute downstream build steps yet"* so it is purely directive.

---

**Consensus Prompt (Not Executed)**

```
OBJECTIVE
Transform the ICW (I Can't Wait) rental website into a Montreal-focused luxury rental experience powered by verified ICW assets.

RESOURCES
1. Property dataset: /mnt/c/Users/Setup/Downloads/assets/ICW_Complete_Data.csv (12 listings)
2. Guest reviews: /mnt/c/Users/Setup/Downloads/assets/all-bookings.enriched-v4.csv
3. Brand assets: ICW_Logo.png (primary), Montreal_night.jpg (hero cityscape)
4. WordPress media library: https://icantwait.ca/wp-json/wp/v2/media (validate each filename in PhotoNames)
5. Current demo artefacts: final-desktop-*.png, final-mobile-*.png for spacing baseline

NON-NEGOTIABLES
- No stock photos of third-party properties; only ICW library images or generic Montreal scenes.
- Replace all placeholder copy with real data (names, prices, amenities, reviews, response rates).
- French-first content; English available but secondary.
- Document all debates (prompt, design, technical) before implementation.

DELIVERABLES
1. Updated homepage + property templates using Stayscape CSS baseline with corrected spacing.
2. Property gallery system with lazy-loading tied to verified WordPress media URLs.
3. Reviews + amenity filtering components populated from CSV data.
4. Accessibility, performance, and spacing validation reports.

VALIDATION PIPELINE (to be executed after build)
- Check every image URL for HTTP 200 status.
- Run Playwright MCP spacing + accessibility audit (desktop/tablet/mobile).
- Confirm lazy loading via IntersectionObserver or native `loading="lazy"` for galleries.
- Verify translations: French primary, fallback English strings present.
- Summarize metrics (CLS <0.1, LCP <2.5s target) and list residual risks.

Do not start implementation; prepare detailed plans and obtain approval before proceeding.
```

**Action Items Recorded**
- Redeveloped prompt stored here for reference only (not executed).
- Proceed to design and technical debate transcripts per client brief.

---

*Transcript prepared: 2025-09-27*
