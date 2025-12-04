# V5 Intelligence Methodology Template (Dynamic from a Website Seed)

Use this to spin up a V5-style intelligence workflow for **any company** by seeding with a website URL and a few parameters. It should adapt to the company’s sector/products, capture past/present/future, run full competitive/buyer diligence (registry, ownership, funding, pricing, compliance), and include everything from the Epic V5 flow: ingest → index → analyze, historical snapshots, macro forecasts, customer sentiment, and IF.TTT discipline.

## 0) Mission Metadata (fill/override)
- Mission ID: `if://mission/{company}-v5-{date}`
- Seed URL: `{https://www.example.com}` (use sitemap/robots/navigation as source of truth)
- Target: `{Company Name}`
- Sector: `{Sector}` (infer from site + override) e.g., gaming, SaaS, marketplace, hardware, fintech, media, biotech
- Products/lines: `{Products}` (derive from site: product pages, docs, blog/release notes)
- Geos: `{Key markets}` (footer/legal pages, WHOIS, careers)
- Outputs: Exec summary (500w), full report (8k–60k+), data appendix, investment decision tree, dissent report, macro forecast
- Goal: Definitive, TTT-compliant (Traceable, Transparent, Trustworthy)

## 1) Surface Area (derive from site, adapt to sector; buyer-focused)
Seed from the website:
- Crawl sitemap/robots.txt/nav to list product/pricing/docs/blog/legal/careers.
- Capture history via Internet Archive (Wayback) for homepage/product/pricing (past vs present).
- Extract product catalog: past/present SKUs, roadmap hints from blog/release notes.

Then layer standard axes (swap examples per sector):
- Business model: platform vs content vs services (SaaS: subs/usage; Marketplace: take rate/GMV; Fintech: TPV/interchange; Hardware: BOM/channel).
- Competitive: direct comps/substitutes; platform dependencies (Apple/Google/Microsoft); distribution channels.
- Financials: revenue mix, cash/burn, valuation proxies (private: hiring/traffic/pricing; public: filings).
- Legal/regulatory: sector regimes (antitrust, data/privacy, safety, KYC/AML, IP).
- Product/tech: adoption, performance, release cadence, uptime/incidents; stack signals from headers/jobs/docs.
- Market/culture: user/customer sentiment, partnerships, creator ecosystems.
- HR/culture: hiring/layoffs (careers/LinkedIn), Glassdoor, press.
- Engagement/live: uptime/incidents (SaaS), outages/fraud (fintech), recalls/RMA (hardware), events/esports (gaming/media).
- Contrarian/historical: bear cases, precedent failures, “why it might fail.”
- Buyer-focused: ownership/cap table (funding, investors, board), corporate registries, liens/charges, customer concentration risk, compliance posture.
- Competitive teardown: key comps (feature/pricing/vertical depth), network effects vs single-tenant, certification posture vs peers.
- Commercials: pricing/TCO, pilots/POC length, implementation model, SLAs/support.

## 2) Collections & Sources (ChromaDB; rename per company)
Use neutral names (replace `company_*` with target):
- `company_forums`: Sentiment/community (Reddit/Discord/forums; SaaS: G2/Capterra/Statuspage; Fintech: support/Trustpilot; Hardware: app store reviews/user forums).
- `company_legal`: Legal/regulatory (PACER/USPTO/FTC/EU/UK; sector regulators).
- `company_financials`: Decks/analyst notes/press; sector metrics (TPV/interchange; ARR/NRR; GMV/take); funding/investors/board; pricing signals.
- `company_products`: Patch notes/dev blogs/feature launches; FCC/CE filings/firmware for hardware; API docs for SaaS/fintech.
- `company_competitive`: Comps/benchmarks (SteamDB analogs, similarweb/G2, TPV/MAU comps, channel checks).
- `company_hr_culture`: Glassdoor/LinkedIn/layoff news.
- `company_live_events`: Engagement/events; swap to uptime/incidents (SaaS), outages/fraud (fintech), recalls/RMA (hardware).
- `company_history`: Internet Archive snapshots (past vs present).
- Optional buyer-focused splits (or keep in financials/legal):
  - `company_registry`: Corporate filings (Companies House/Infogreffe/etc.), PSCs, liens/charges.
  - `company_reviews`: G2/Capterra/Trustpilot slices if you want to separate from forums.

Coverage tracker (JSON/YAML):
- Per collection: sources list, status {planned|live|failing|stale}, last run, doc count.

## 3) Ingestion Runbook (adapt sources)
- Base path: `/root/intelligence-pipelines/{company}/`, venv: `/root/intelligence-pipelines/{company}/venv/bin/python`
- Orchestrator: `collectors/run_all.py` (extend with sector-specific collectors).
- Seed from site:
  - Crawl sitemap/robots; fetch key pages (products/pricing/docs/blog/legal/careers) and store in `company_history`.
  - Wayback snapshots for homepage/product/pricing to capture past.
- Fix forum ingest (e.g., Reddit 403): OAuth (PRAW/requests) or alternate feeds (Pushshift/other aggregators).
- Add collectors per collection (legal, financial, competitive, HR/culture, live events/history) with sector sources (G2/Capterra/Statuspage; TPV/fraud; FCC/CE; etc.).
- Add registry/ownership: corporate registries (e.g., Companies House/Infogreffe/CAC), trademarks/patents, liens/charges.
- Add mobile/app store scrape if applicable (Android/iOS), and DNS/tech stack (builtwith/DNS history) if relevant.
- Hygiene: dedup, store URLs/hashes/timestamps in metadata, rate-limit, PII/terms compliance checks.
- Run:
  ```bash
  /root/intelligence-pipelines/{company}/collectors/run_all.py
  ```
- Verify counts:
  ```bash
  /root/intelligence-pipelines/{company}/venv/bin/python - <<'PY'
  import chromadb
  client = chromadb.PersistentClient("/root/intelligence-pipelines/{company}/chromadb")
  for name in ["company_forums","company_legal","company_financials","company_products","company_competitive","company_hr_culture","company_live_events","company_history"]:
      c = client.get_or_create_collection(name=name)
      print(name, c.count())
  PY
  ```

## 4) Swarm & Council (adapt specializations)
- Clusters: Financial, Competitive, Product/Tech, Market/Culture, Contrarian/Historical (add sector specialists as needed).
- Guardian Council: 30+ members, incl. legal/regulatory, sector experts.
- IF.optimise: Haiku/cheap models for mechanical/data; higher-end models for synthesis/judgment; TTT-compliant deliberation.
- Freeze ingest during main analysis; run swarm after collections have data.

## 5) Reporting (TTT discipline)
- IF.TTT self-assessment per section (Traceable/Transparent/Trustworthy scores).
- Multi-source corroboration; variance/confidence explicit; falsifiable predictions; dissent preserved.
- Customer feedback/pain points: themes + counts from `company_forums`/reviews.
- Projections: bull/base/bear with triggers; macro overlay (regulatory shifts, platform policy changes, capital markets conditions).
- Past → present → future: use `company_history` for deltas (products/pricing/positioning).

## 6) Reporting (TTT discipline + GEDIMAT pattern)
- IF.TTT self-assessment per section (Traceable/Transparent/Trustworthy scores). Unknowns must be flagged (e.g., “SOC2: not disclosed”).
- Claims must be cited or labeled “Inference” with the heuristic/formula shown. No fixed numbers without sources; use formulas + ranges.
- ROI/benefit: show formulas (baseline × % reduction × cost), itemize inputs (time, usage tiers), avoid invented savings.
- Customer feedback/pain points: themes + counts from forums/reviews (or note “none found”).
- Projections: bull/base/bear with triggers; macro overlay (regulatory shifts, platform policy changes, capital markets).
- Past → present → future: use history snapshots for deltas (products/pricing/positioning).
- Keep dissent and gaps visible; preserve a TTT scorecard in the report.

## 7) Outputs (suggested)
- Mission prompt: `intelligence-missions/{COMPANY}_V5_MISSION_PROMPT.md`
- Reports: `{company}-v5/reports/` (create) or designated private repo.
- Data/JSON appendices: `{company}-v5/data/`
- Note paths in a handoff/readme.

## 8) Status Snapshot Template
- Pipeline reachable? (yes/no)
- Venv healthy? (versions)
- Collection counts: forums/legal/financials/products/competitive/hr_culture/live_events/history
- Ingest blockers: (e.g., Reddit 403)
- Swarm run? (yes/no; latest outputs)
- Next actions: (list 3–5)

## 9) Immediate To-Do (if starting fresh)
1) Parameterize (company, seed URL, sector, products, geos).
2) Implement collectors (OAuth forums + sector sources), ingest, verify counts, update coverage tracker.
3) Launch full V5 swarm per mission prompt; enforce TTT self-assessment.
4) Store outputs and update handoff (paths + blockers + coverage status).
