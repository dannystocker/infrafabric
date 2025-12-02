# IF.intelligence Mission: Epic Games V5 Deep Dive
## Full Swarm Architecture with 30+ Guardian Council + 40+ Haiku Workers

**Mission ID:** `if://mission/epic-games-v5-2025-12-02`
**Classification:** Investment Intelligence - Platform Thesis Validation
**Target:** Epic Games Inc. (Fortnite, Unreal Engine, Epic Games Store)
**Deadline:** 72 hours from mission start
**Budget:** Optimized via IF.optimise (target: <$50 total API cost)

---

## Part I: Mission Objective

### 1.1 The Question We're Answering

**Primary Research Question:**
> Is Epic Games a platform company (Unity + Valve + Roblox) or a content company (EA + Activision) that happens to have a game engine?

**Secondary Questions:**
1. Has the platform thesis strengthened or weakened since V4 report (Nov 2025)?
2. What is Fortnite's trajectory? (Stabilizing, declining, or resurgent?)
3. Is Unreal Engine 5 adoption accelerating or plateauing?
4. Has Epic Games Store gained market share against Steam?
5. What are the metaverse partnership outcomes (Disney, Lego, Mercedes-Benz)?

### 1.2 Deliverables

| Deliverable | Format | Length | TTT Compliance |
|-------------|--------|--------|----------------|
| Executive Summary | Markdown | 500 words | 5.0/5 required |
| Full Narrative Report | Acquired-style | 8,000+ words | 5.0/5 required |
| Data Appendix | JSON + Tables | Unlimited | All claims cited |
| Investment Recommendation | Decision Tree | 1 page | Falsifiable predictions |
| Dissent Report | Markdown | As needed | Bear case preserved |

---

## Part II: Guardian Council Configuration (32 Members)

### 2.1 Core Guardians (6)

```yaml
core_guardians:
  - id: technical_guardian
    weight: 2.0
    focus: "Architecture, reproducibility, code validation"
    veto_power: false

  - id: ethical_guardian
    weight: 2.0
    focus: "Privacy, fairness, unintended consequences"
    veto_power: false

  - id: business_guardian
    weight: 1.5
    focus: "Market viability, unit economics, competitive moat"
    veto_power: false

  - id: legal_guardian
    weight: 2.0
    focus: "Regulatory compliance, antitrust, IP"
    veto_power: false

  - id: user_guardian
    weight: 1.5
    focus: "Player experience, creator economics, accessibility"
    veto_power: false

  - id: meta_guardian
    weight: 2.0
    focus: "Synthesis, coherence, tiebreaker"
    veto_power: true
```

### 2.2 Specialist Guardians - Gaming/Tech (8)

```yaml
specialist_gaming:
  - id: gaming_industry_guardian
    weight: 1.5
    focus: "Industry trends, competitor analysis, market dynamics"
    expertise: "20+ years gaming industry coverage"

  - id: unreal_engine_guardian
    weight: 1.5
    focus: "Engine technology, developer adoption, Unity comparison"
    expertise: "Technical game development, engine architecture"

  - id: metaverse_guardian
    weight: 1.0
    focus: "Virtual worlds, creator economy, spatial computing"
    expertise: "Web3/metaverse market analysis"

  - id: esports_guardian
    weight: 1.0
    focus: "Competitive gaming, Fortnite esports, prize pools"
    expertise: "Esports economics and viewership"

  - id: platform_economics_guardian
    weight: 1.5
    focus: "App store dynamics, 30% vs 12% take rates, antitrust"
    expertise: "Two-sided marketplace economics"

  - id: gen_z_guardian
    weight: 1.0
    focus: "Youth demographics, cultural relevance, attention economy"
    expertise: "Gen Z/Alpha consumer behavior"

  - id: creator_economy_guardian
    weight: 1.0
    focus: "UEFN, creator payouts, user-generated content"
    expertise: "Creator monetization platforms"

  - id: china_market_guardian
    weight: 1.0
    focus: "Tencent relationship, China regulatory, Asia expansion"
    expertise: "China tech/gaming markets"
```

### 2.3 Specialist Guardians - Finance/Investment (6)

```yaml
specialist_finance:
  - id: valuation_guardian
    weight: 1.5
    focus: "DCF models, comparable company analysis, private valuations"
    expertise: "Tech company valuation, private markets"

  - id: risk_guardian
    weight: 1.5
    focus: "Single-game dependency, key person risk, regulatory risk"
    expertise: "Investment risk assessment"

  - id: m_and_a_guardian
    weight: 1.0
    focus: "Acquisition targets, strategic buyers, IPO scenarios"
    expertise: "Gaming M&A, tech IPOs"

  - id: activist_guardian
    weight: 1.0
    focus: "Shareholder pressure, governance, capital allocation"
    expertise: "Activist investing, corporate governance"

  - id: public_markets_guardian
    weight: 1.0
    focus: "Comparable public companies, sector sentiment"
    expertise: "Gaming sector equity research"

  - id: venture_guardian
    weight: 1.0
    focus: "Late-stage private valuations, secondary market"
    expertise: "Growth equity, pre-IPO markets"
```

### 2.4 Philosophical Extension (9)

```yaml
philosophical_council:
  # Western (6)
  - id: popper_guardian
    focus: "Falsifiability - Are predictions testable?"

  - id: vienna_circle_guardian
    focus: "Verificationism - Can claims be verified?"

  - id: dewey_guardian
    focus: "Pragmatism - What works in practice?"

  - id: quine_guardian
    focus: "Coherentism - Does the thesis hold together?"

  - id: locke_guardian
    focus: "Empiricism - What's the evidence?"

  - id: peirce_guardian
    focus: "Abduction - Best explanation for the data?"

  # Eastern (3)
  - id: buddha_guardian
    focus: "Non-attachment - Are we too invested in one narrative?"

  - id: confucius_guardian
    focus: "Practical benefit - Who does this analysis serve?"

  - id: laozi_guardian
    focus: "Wu Wei - What's the effortless path to truth?"
```

### 2.5 Contrarian Guardian (1)

```yaml
contrarian:
  - id: contrarian_guardian
    weight: 3.0
    focus: "Devil's advocate - Why is everyone wrong?"
    special_power: "Can invoke 2-week cooling period on >95% consensus"
    mandatory_output: "Must produce bear case even if bullish consensus"
```

### 2.6 IF.ceo Facets (2 - Synthesis Only)

```yaml
ceo_synthesis:
  - id: ceo_light_side
    focus: "Idealistic view - What's the best-case outcome?"

  - id: ceo_dark_side
    focus: "Ruthless pragmatism - What's the exploitable angle?"
```

---

## Part III: Haiku Swarm Configuration (42 Workers)

### 3.1 Research Cluster - Financial (10 Haiku)

```yaml
financial_cluster:
  coordinator: sonnet_financial_lead

  workers:
    - id: haiku_fin_001
      profile: "Investigative Financial Journalist"
      specialty: "Following the money, forensic accounting"
      assigned_chunks:
        - "Epic Games revenue breakdown 2023-2025"
        - "Fortnite revenue trajectory analysis"

    - id: haiku_fin_002
      profile: "Sell-Side Gaming Analyst"
      specialty: "Comparable company analysis, price targets"
      assigned_chunks:
        - "Unity, Roblox, EA, Activision comps"
        - "Valuation multiple analysis"

    - id: haiku_fin_003
      profile: "Private Market Specialist"
      specialty: "Secondary transactions, late-stage valuations"
      assigned_chunks:
        - "Epic secondary market activity"
        - "Sony/Kirkbi investment terms analysis"

    - id: haiku_fin_004
      profile: "M&A Analyst"
      specialty: "Deal structures, strategic rationale"
      assigned_chunks:
        - "Epic acquisition history (Bandcamp, Harmonix, etc.)"
        - "Potential acquirer analysis"

    - id: haiku_fin_005
      profile: "Hedge Fund Analyst"
      specialty: "Catalyst identification, event-driven"
      assigned_chunks:
        - "IPO timing analysis"
        - "Key person dependency (Tim Sweeney)"

    - id: haiku_fin_006
      profile: "Credit Analyst"
      specialty: "Balance sheet, cash flow, debt capacity"
      assigned_chunks:
        - "Epic cash position and burn rate"
        - "Epic Games Store subsidy economics"

    - id: haiku_fin_007
      profile: "VC Associate"
      specialty: "Growth metrics, TAM analysis"
      assigned_chunks:
        - "Unreal Engine market share trajectory"
        - "Creator economy TAM"

    - id: haiku_fin_008
      profile: "Family Office Analyst"
      specialty: "Long-term value, generational wealth"
      assigned_chunks:
        - "10-year platform thesis"
        - "Dividend/buyback potential"

    - id: haiku_fin_009
      profile: "Quant Researcher"
      specialty: "Data patterns, statistical significance"
      assigned_chunks:
        - "Player count correlation with revenue"
        - "Seasonality analysis"

    - id: haiku_fin_010
      profile: "ESG Analyst"
      specialty: "Governance, social impact, sustainability"
      assigned_chunks:
        - "Tim Sweeney voting control analysis"
        - "Epic workplace culture assessment"
```

### 3.2 Research Cluster - Competitive Intelligence (10 Haiku)

```yaml
competitive_cluster:
  coordinator: sonnet_competitive_lead

  workers:
    - id: haiku_comp_001
      profile: "Steam/Valve Specialist"
      specialty: "Steam market share, Valve strategy"
      assigned_chunks:
        - "Steam vs Epic Games Store market share 2023-2025"
        - "Steam Deck impact on distribution"

    - id: haiku_comp_002
      profile: "Unity Specialist"
      specialty: "Unity engine, runtime fee controversy"
      assigned_chunks:
        - "Unity vs Unreal market share shift"
        - "Post-runtime-fee developer migration"

    - id: haiku_comp_003
      profile: "Roblox Specialist"
      specialty: "Creator economy, young demographics"
      assigned_chunks:
        - "Roblox vs Fortnite creator payouts"
        - "UEFN vs Roblox Studio comparison"

    - id: haiku_comp_004
      profile: "Apple/Google Specialist"
      specialty: "App store policies, antitrust"
      assigned_chunks:
        - "Epic v. Apple aftermath"
        - "EU Digital Markets Act impact"

    - id: haiku_comp_005
      profile: "Microsoft Gaming Specialist"
      specialty: "Xbox, Activision acquisition, Game Pass"
      assigned_chunks:
        - "Microsoft-Epic relationship"
        - "Game Pass competitive threat"

    - id: haiku_comp_006
      profile: "Sony Specialist"
      specialty: "PlayStation, Sony investment rationale"
      assigned_chunks:
        - "Sony $1B investment strategic logic"
        - "PlayStation-Fortnite relationship"

    - id: haiku_comp_007
      profile: "Tencent Specialist"
      specialty: "China gaming, Tencent holdings"
      assigned_chunks:
        - "Tencent 40% stake implications"
        - "China Fortnite shutdown analysis"

    - id: haiku_comp_008
      profile: "Amazon Gaming Specialist"
      specialty: "Twitch, Luna, Amazon Games"
      assigned_chunks:
        - "Twitch-Fortnite streaming metrics"
        - "Amazon as potential acquirer"

    - id: haiku_comp_009
      profile: "Netflix Gaming Specialist"
      specialty: "Netflix games strategy"
      assigned_chunks:
        - "Netflix gaming competitive position"
        - "Streaming-gaming convergence"

    - id: haiku_comp_010
      profile: "Discord/Social Specialist"
      specialty: "Gaming social platforms"
      assigned_chunks:
        - "Discord integration analysis"
        - "Social features competitive comparison"
```

### 3.3 Research Cluster - Product/Technology (10 Haiku)

```yaml
product_cluster:
  coordinator: sonnet_product_lead

  workers:
    - id: haiku_prod_001
      profile: "Unreal Engine Developer"
      specialty: "UE5 features, Nanite, Lumen"
      assigned_chunks:
        - "UE5.4 feature analysis"
        - "Nanite/Lumen adoption metrics"

    - id: haiku_prod_002
      profile: "Fortnite Game Designer"
      specialty: "Game mechanics, seasons, updates"
      assigned_chunks:
        - "Fortnite Chapter 5 analysis"
        - "Battle pass economics"

    - id: haiku_prod_003
      profile: "UEFN/Creative Specialist"
      specialty: "User-generated content tools"
      assigned_chunks:
        - "UEFN creator adoption metrics"
        - "Top UEFN experiences analysis"

    - id: haiku_prod_004
      profile: "Metaverse Product Manager"
      specialty: "Virtual concerts, brand activations"
      assigned_chunks:
        - "Travis Scott concert case study"
        - "Brand partnership ROI analysis"

    - id: haiku_prod_005
      profile: "Mobile Gaming Specialist"
      specialty: "iOS/Android, mobile performance"
      assigned_chunks:
        - "Fortnite mobile revenue (post-ban)"
        - "Epic Games Store mobile strategy"

    - id: haiku_prod_006
      profile: "PC Gaming Specialist"
      specialty: "PC market, hardware requirements"
      assigned_chunks:
        - "PC gamer demographics"
        - "System requirements analysis"

    - id: haiku_prod_007
      profile: "Console Specialist"
      specialty: "PlayStation, Xbox, Nintendo"
      assigned_chunks:
        - "Console revenue breakdown"
        - "Nintendo Switch Cloud analysis"

    - id: haiku_prod_008
      profile: "Esports Producer"
      specialty: "Competitive Fortnite, FNCS"
      assigned_chunks:
        - "FNCS prize pool trends"
        - "Esports viewership metrics"

    - id: haiku_prod_009
      profile: "Film/TV Industry Analyst"
      specialty: "Virtual production, Mandalorian"
      assigned_chunks:
        - "Virtual production adoption"
        - "Unreal Engine in film/TV"

    - id: haiku_prod_010
      profile: "Automotive Industry Analyst"
      specialty: "Unreal in automotive, Mercedes"
      assigned_chunks:
        - "Automotive visualization market"
        - "Mercedes-Benz partnership analysis"
```

### 3.4 Research Cluster - Market/Cultural (8 Haiku)

```yaml
market_cluster:
  coordinator: sonnet_market_lead

  workers:
    - id: haiku_mkt_001
      profile: "Gen Z Cultural Analyst"
      specialty: "Youth trends, attention economy"
      assigned_chunks:
        - "Fortnite cultural relevance 2025"
        - "Gen Alpha gaming preferences"

    - id: haiku_mkt_002
      profile: "Brand Partnership Specialist"
      specialty: "IP collaborations, marketing"
      assigned_chunks:
        - "Marvel/Star Wars/NFL partnerships"
        - "Brand collaboration ROI"

    - id: haiku_mkt_003
      profile: "Streaming/Content Analyst"
      specialty: "Twitch, YouTube Gaming"
      assigned_chunks:
        - "Fortnite streaming hours 2023-2025"
        - "Creator content trends"

    - id: haiku_mkt_004
      profile: "Social Media Analyst"
      specialty: "TikTok, Twitter, Reddit"
      assigned_chunks:
        - "Fortnite social sentiment"
        - "Community engagement metrics"

    - id: haiku_mkt_005
      profile: "Market Researcher"
      specialty: "Surveys, focus groups, NPS"
      assigned_chunks:
        - "Player satisfaction surveys"
        - "Developer sentiment (Unreal)"

    - id: haiku_mkt_006
      profile: "Regulatory Analyst"
      specialty: "Gaming regulations, loot boxes"
      assigned_chunks:
        - "V-Bucks regulatory status"
        - "Children's privacy compliance"

    - id: haiku_mkt_007
      profile: "IP/Legal Analyst"
      specialty: "Patents, trademarks, lawsuits"
      assigned_chunks:
        - "Epic patent portfolio"
        - "Ongoing litigation status"

    - id: haiku_mkt_008
      profile: "Macroeconomist"
      specialty: "Gaming in recession, discretionary spend"
      assigned_chunks:
        - "Gaming spend vs macro conditions"
        - "Premium gaming resilience"
```

### 3.5 Synthesis Cluster (4 Haiku)

```yaml
synthesis_cluster:
  coordinator: sonnet_synthesis_lead

  workers:
    - id: haiku_syn_001
      profile: "Narrative Writer"
      specialty: "Acquired-style storytelling"
      assigned_chunks:
        - "Hook and opening narrative"
        - "Character arc (Tim Sweeney)"

    - id: haiku_syn_002
      profile: "Data Visualizer"
      specialty: "Charts, tables, infographics"
      assigned_chunks:
        - "Revenue visualization"
        - "Market share charts"

    - id: haiku_syn_003
      profile: "Fact Checker"
      specialty: "Citation verification, TTT compliance"
      assigned_chunks:
        - "All numerical claims"
        - "Source cross-referencing"

    - id: haiku_syn_004
      profile: "Contrarian Writer"
      specialty: "Bear case articulation"
      assigned_chunks:
        - "Zynga/Rovio comparison"
        - "Risk factor documentation"
```

---

## Part IV: IF.LOGISTICS Communication Protocol

### 4.1 Redis Channel Architecture

```yaml
redis_channels:
  # Coordination Channels
  - channel: "epic_v5:coordinator:broadcast"
    purpose: "Mission-wide announcements from lead coordinators"
    publishers: [sonnet_mission_lead]
    subscribers: [all_agents]

  - channel: "epic_v5:coordinator:status"
    purpose: "Agent status updates (working, blocked, complete)"
    publishers: [all_agents]
    subscribers: [sonnet_mission_lead, all_coordinators]

  # Cluster Channels
  - channel: "epic_v5:financial:internal"
    purpose: "Financial cluster internal coordination"
    publishers: [financial_cluster]
    subscribers: [financial_cluster, sonnet_financial_lead]

  - channel: "epic_v5:competitive:internal"
    purpose: "Competitive cluster internal coordination"
    publishers: [competitive_cluster]
    subscribers: [competitive_cluster, sonnet_competitive_lead]

  - channel: "epic_v5:product:internal"
    purpose: "Product cluster internal coordination"
    publishers: [product_cluster]
    subscribers: [product_cluster, sonnet_product_lead]

  - channel: "epic_v5:market:internal"
    purpose: "Market cluster internal coordination"
    publishers: [market_cluster]
    subscribers: [market_cluster, sonnet_market_lead]

  # Cross-Cluster Sharing
  - channel: "epic_v5:discoveries"
    purpose: "Real-time sharing of significant findings"
    publishers: [all_haiku_workers]
    subscribers: [all_agents]
    message_format: |
      {
        "discovery_id": "uuid",
        "agent_id": "haiku_fin_001",
        "discovery_type": "data_point|insight|conflict|blocker",
        "content": "...",
        "citations": ["url1", "url2"],
        "confidence": 0.85,
        "relevance_to_clusters": ["financial", "competitive"],
        "timestamp": "ISO8601"
      }

  # Guardian Council Channel
  - channel: "epic_v5:guardian_council"
    purpose: "Guardian deliberation and voting"
    publishers: [all_guardians, sonnet_mission_lead]
    subscribers: [all_guardians]

  # IF.optimise Channel
  - channel: "epic_v5:optimise"
    purpose: "Self-optimization signals between agents"
    publishers: [all_agents]
    subscribers: [all_agents]
    message_types:
      - "BLOCKING": "Agent is blocked waiting for dependency"
      - "AVAILABLE": "Agent has capacity for additional work"
      - "ACCELERATE": "Request priority processing"
      - "SHARE_CONTEXT": "Pushing relevant context to other agents"
      - "REQUEST_HELP": "Requesting assistance from available agents"
```

### 4.2 IF.optimise Self-Optimization Protocol

```python
class IFOptimise:
    """Agent self-optimization via Redis pub/sub."""

    def __init__(self, agent_id: str, redis_client):
        self.agent_id = agent_id
        self.redis = redis_client
        self.status = "IDLE"
        self.current_chunk = None
        self.blocked_since = None

    def publish_status(self, status: str, metadata: dict = None):
        """Broadcast agent status to swarm."""
        message = {
            "agent_id": self.agent_id,
            "status": status,  # WORKING, BLOCKED, COMPLETE, AVAILABLE
            "current_chunk": self.current_chunk,
            "blocked_since": self.blocked_since,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis.publish("epic_v5:optimise", json.dumps(message))

    def request_help(self, blocking_reason: str, needed_info: str):
        """Request assistance from available agents."""
        message = {
            "type": "REQUEST_HELP",
            "agent_id": self.agent_id,
            "blocking_reason": blocking_reason,
            "needed_info": needed_info,
            "current_chunk": self.current_chunk,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis.publish("epic_v5:optimise", json.dumps(message))

    def share_discovery(self, discovery: dict):
        """Push relevant discovery to all agents."""
        message = {
            "type": "SHARE_DISCOVERY",
            "agent_id": self.agent_id,
            "discovery": discovery,
            "relevance_tags": discovery.get("relevance_to_clusters", []),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis.publish("epic_v5:discoveries", json.dumps(message))

    def volunteer_for_chunk(self, chunk_id: str):
        """Volunteer to take on additional work."""
        message = {
            "type": "VOLUNTEER",
            "agent_id": self.agent_id,
            "chunk_id": chunk_id,
            "current_load": self.get_current_load(),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis.publish("epic_v5:optimise", json.dumps(message))

    def accelerate_dependency(self, dependent_chunk: str, blocking_agent: str):
        """Signal that a dependency is blocking progress."""
        message = {
            "type": "ACCELERATE_REQUEST",
            "requesting_agent": self.agent_id,
            "blocking_agent": blocking_agent,
            "dependent_chunk": dependent_chunk,
            "urgency": "HIGH",
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis.publish("epic_v5:optimise", json.dumps(message))
```

### 4.3 Coordinator Response to IF.optimise Signals

```python
class SwarmCoordinator:
    """Sonnet coordinator responding to IF.optimise signals."""

    def handle_optimise_message(self, message: dict):
        msg_type = message.get("type")

        if msg_type == "REQUEST_HELP":
            # Find available agents with relevant expertise
            available = self.find_available_agents(
                expertise=message["needed_info"]
            )
            if available:
                self.reassign_chunk(
                    from_agent=message["agent_id"],
                    to_agent=available[0],
                    reason="unblocking"
                )
            else:
                # Escalate to human or spawn new agent
                self.escalate_blocking(message)

        elif msg_type == "ACCELERATE_REQUEST":
            # Prioritize blocking agent's work
            self.boost_agent_priority(
                agent_id=message["blocking_agent"],
                reason=f"Blocking {message['requesting_agent']}"
            )

        elif msg_type == "VOLUNTEER":
            # Assign waiting chunks to available agent
            waiting_chunks = self.get_unassigned_chunks()
            if waiting_chunks:
                self.assign_chunk(
                    agent_id=message["agent_id"],
                    chunk=waiting_chunks[0]
                )

    def detect_blocked_agents(self):
        """Proactively detect agents blocked >5 minutes."""
        for agent_id, status in self.agent_statuses.items():
            if status["status"] == "BLOCKED":
                blocked_duration = datetime.utcnow() - status["blocked_since"]
                if blocked_duration > timedelta(minutes=5):
                    self.intervene_blocked_agent(agent_id)
```

---

## Part V: Mission Execution Sequence

### 5.1 Phase 1: Swarm Initialization (T+0 to T+5min)

```yaml
phase_1:
  name: "Swarm Boot"
  duration: "5 minutes"

  steps:
    - step: 1
      action: "Spawn Mission Lead Sonnet"
      agent: sonnet_mission_lead

    - step: 2
      action: "Initialize Redis channels"
      channels: [all_channels_from_4.1]

    - step: 3
      action: "Spawn Cluster Coordinators"
      agents:
        - sonnet_financial_lead
        - sonnet_competitive_lead
        - sonnet_product_lead
        - sonnet_market_lead
        - sonnet_synthesis_lead

    - step: 4
      action: "Spawn Haiku Workers"
      count: 42
      profiles: [as_defined_in_part_3]

    - step: 5
      action: "Initialize Guardian Council"
      count: 32
      ready_state: "STANDBY"

    - step: 6
      action: "Distribute chunk assignments"
      method: "Redis pub/sub to each worker"

    - step: 7
      action: "Confirm all agents ready"
      validation: "All 42 Haiku + 5 Sonnet + 32 Guardians = 79 agents online"
```

### 5.2 Phase 2: Parallel Research (T+5min to T+4hr)

```yaml
phase_2:
  name: "Deep Research Sprint"
  duration: "4 hours"

  parallel_tracks:
    - track: "Financial Research"
      coordinator: sonnet_financial_lead
      workers: [haiku_fin_001 through haiku_fin_010]
      chunks: 20

    - track: "Competitive Intelligence"
      coordinator: sonnet_competitive_lead
      workers: [haiku_comp_001 through haiku_comp_010]
      chunks: 20

    - track: "Product/Technology"
      coordinator: sonnet_product_lead
      workers: [haiku_prod_001 through haiku_prod_010]
      chunks: 20

    - track: "Market/Cultural"
      coordinator: sonnet_market_lead
      workers: [haiku_mkt_001 through haiku_mkt_008]
      chunks: 16

  real_time_sharing:
    channel: "epic_v5:discoveries"
    format: "As discoveries emerge, broadcast to all clusters"

  blocking_protocol:
    detection: "IF.optimise monitors for >5min blocks"
    response: "Coordinator reassigns or spawns helper agent"
```

### 5.3 Phase 3: Synthesis & Conflict Resolution (T+4hr to T+8hr)

```yaml
phase_3:
  name: "Synthesis Sprint"
  duration: "4 hours"

  steps:
    - step: 1
      action: "Cluster leads compile findings"
      output: "4 cluster reports"

    - step: 2
      action: "Identify cross-cluster conflicts"
      example: "Financial says $5.8B revenue, Competitive says $4.2B"

    - step: 3
      action: "Spawn conflict resolution agents"
      method: "haiku_syn_003 (Fact Checker) investigates each conflict"

    - step: 4
      action: "Escalate unresolved conflicts"
      destination: "Guardian Council for deliberation"

    - step: 5
      action: "Narrative assembly"
      agent: haiku_syn_001 (Narrative Writer)
      style: "Acquired podcast deep-dive format"
```

### 5.4 Phase 4: Guardian Council Deliberation (T+8hr to T+12hr)

```yaml
phase_4:
  name: "Guardian Deliberation"
  duration: "4 hours"

  agenda:
    - item: 1
      topic: "Platform vs Content thesis validation"
      required_consensus: 85%

    - item: 2
      topic: "Investment recommendation (BUY/HOLD/SELL)"
      required_consensus: 70%

    - item: 3
      topic: "Key risk assessment"
      required_consensus: 70%

    - item: 4
      topic: "Contrarian case review"
      presenter: contrarian_guardian
      veto_check: true

  deliberation_protocol:
    - All 32 guardians evaluate in parallel
    - IF.intelligence agents can be spawned for real-time research
    - Each guardian submits vote + rationale + confidence score
    - Meta Guardian synthesizes + breaks ties
    - Contrarian Guardian reviews for groupthink

  output:
    - Final recommendation with consensus percentage
    - Individual guardian positions preserved
    - Dissent report if applicable
```

### 5.5 Phase 5: Final Assembly & QA (T+12hr to T+24hr)

```yaml
phase_5:
  name: "Final Assembly"
  duration: "12 hours"

  steps:
    - step: 1
      action: "Compile full report"
      components:
        - Executive Summary
        - Full Narrative (8,000+ words)
        - Data Appendix
        - Investment Recommendation
        - Dissent Report
        - Guardian Vote Record

    - step: 2
      action: "TTT Compliance Audit"
      agent: haiku_syn_003
      checklist:
        - All claims have 2+ citations
        - All citations are resolvable
        - Confidence scores explicit
        - Conflicts flagged
        - Contrarian case preserved

    - step: 3
      action: "Voice Polish"
      agents: [haiku_syn_001, sonnet_mission_lead]
      style: "Legal VoiceDNA + Danny Stocker light touch"

    - step: 4
      action: "Final Guardian sign-off"
      required: meta_guardian approval

    - step: 5
      action: "Publish to if://doc/epic-games-v5-2025-12-02"
      format: Markdown + JSON appendix
```

---

## Part VI: TTT Compliance Requirements

### 6.1 Citation Standards

```yaml
citation_requirements:
  minimum_sources_per_claim: 2

  source_hierarchy:
    - tier_1: "Primary sources (Epic filings, investor decks, Tim Sweeney statements)"
    - tier_2: "Credible secondary (SuperData, Newzoo, Sensor Tower)"
    - tier_3: "Industry analysis (Gamasutra, GamesIndustry.biz)"
    - tier_4: "General press (use sparingly, require corroboration)"

  conflict_handling:
    - Flag variance >10% between sources
    - Escalate to Guardian Council if unresolved
    - Preserve both numbers with confidence scores

  unverifiable_claims:
    - Mark as "ESTIMATED" with methodology
    - Cannot be used for investment recommendation
```

### 6.2 IF.TTT Self-Assessment

```markdown
## V5 Report TTT Self-Assessment

**Traceable (Target: 5.0/5):**
- [ ] All numerical claims cite 2+ sources
- [ ] Primary sources used where available
- [ ] Line-level attribution (page numbers, timestamps)
- [ ] Source conflicts flagged with ESCALATE

**Transparent (Target: 5.0/5):**
- [ ] Guardian Council vote record included
- [ ] Individual guardian positions preserved
- [ ] Contrarian bear case documented (not dismissed)
- [ ] Confidence scores explicit on all predictions
- [ ] Uncertainty escalated (not hidden)

**Trustworthy (Target: 5.0/5):**
- [ ] Multi-source corroboration for key claims
- [ ] Falsifiable hypotheses with metrics
- [ ] Historical precedents verified (Zynga, Rovio, etc.)
- [ ] Reproducible (all sources accessible)
- [ ] Decision rationale visible (70% threshold explained)

**Overall IF.TTT Compliance: ___/5**
```

---

## Part VII: Success Metrics

### 7.1 Mission KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Total API Cost | <$50 | OpenRouter billing |
| Time to Completion | <72 hours | Mission clock |
| TTT Compliance | 5.0/5 | Self-assessment audit |
| Word Count | 8,000+ | wc -w |
| Citation Count | 50+ unique sources | Citation index |
| Guardian Consensus | >85% on thesis | Vote record |
| Haiku Efficiency | <5% blocking time | IF.optimise logs |

### 7.2 Quality Gates

```yaml
quality_gates:
  gate_1:
    name: "Research Complete"
    trigger: "All 76 chunks completed"
    validation: "Cluster coordinators sign off"

  gate_2:
    name: "Conflicts Resolved"
    trigger: "All >10% variances addressed"
    validation: "Guardian Council or fact checker resolution"

  gate_3:
    name: "Narrative Assembled"
    trigger: "Full draft complete"
    validation: "Sonnet mission lead review"

  gate_4:
    name: "Guardian Approval"
    trigger: "Council deliberation complete"
    validation: "Meta Guardian sign-off"

  gate_5:
    name: "TTT Compliant"
    trigger: "Self-assessment complete"
    validation: "5.0/5 or blocking issues documented"
```

---

## Part VIII: Mission Activation

### 8.1 Starter Command

```bash
# Mission Activation Command
python /home/setup/infrafabric/missions/launch_intelligence_mission.py \
  --mission-id "epic-games-v5-2025-12-02" \
  --config "/home/setup/infrafabric/intelligence-missions/EPIC_GAMES_V5_MISSION_PROMPT.md" \
  --guardian-count 32 \
  --haiku-count 42 \
  --sonnet-count 6 \
  --redis-host "localhost" \
  --redis-port 6379 \
  --budget-limit-usd 50 \
  --deadline-hours 72 \
  --ttt-compliance-target 5.0
```

### 8.2 Mission Lead Initial Prompt

```
You are the Mission Lead for IF.intelligence Mission: Epic Games V5.

Your job is to coordinate 42 Haiku workers + 5 Sonnet cluster leads + 32 Guardian Council members to produce a comprehensive intelligence report on Epic Games.

**Primary Research Question:**
Is Epic Games a platform company (Unity + Valve + Roblox) or a content company (EA + Activision) that happens to have a game engine?

**Your Resources:**
- 42 Haiku workers with specialized profiles (see Part III)
- 5 Sonnet cluster coordinators (Financial, Competitive, Product, Market, Synthesis)
- 32 Guardian Council members (see Part II)
- Redis pub/sub channels for real-time coordination
- IF.optimise for self-optimization between agents

**Your Constraints:**
- Budget: <$50 total API cost
- Deadline: 72 hours
- TTT Compliance: 5.0/5 required
- All claims require 2+ citations

**Your Deliverables:**
1. Executive Summary (500 words)
2. Full Narrative Report (8,000+ words, Acquired-style)
3. Data Appendix (JSON + Tables)
4. Investment Recommendation (BUY/HOLD/SELL with falsifiable tests)
5. Dissent Report (Bear case, even if consensus is bullish)

**Begin by:**
1. Confirming all 79 agents are online via Redis status channel
2. Broadcasting mission objectives to all agents
3. Initiating Phase 1: Swarm Initialization

IF.TTT Citation: if://mission/epic-games-v5-2025-12-02
```

---

**Document Status:** Mission Prompt Complete
**IF.TTT Compliance:** Self-Referential Architecture
**Created:** 2025-12-02
**Citation:** `if://doc/epic-games-v5-mission-prompt/2025-12-02`

---

*"Theory is cheap. Production is expensive. Let's produce."*

— IF.intelligence Mission Philosophy
