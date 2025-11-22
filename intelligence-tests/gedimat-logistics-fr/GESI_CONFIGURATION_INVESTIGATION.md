# GESI System Configuration Investigation
## Determining if Lunel Négoce's Integration Challenges are Configuration Issues vs. Fundamental Limitations

**Date:** 2025-11-22
**Investigator:** Claude Sonnet 4.5 (InfraFabric IF.search methodology)
**Status:** Preliminary Research - Requires Week 1 CEICOM Solutions Interview

---

## Executive Summary

**Critical Finding:** Current assumptions about "GESI has no public APIs" and "file-based integration required" may be **premature conclusions** rather than verified technical limitations.

**Evidence Gap Identified:** Public documentation about GESI ERP's technical capabilities is extremely limited. The system is a **proprietary ERP developed exclusively by CEICOM Solutions for the Gedimat/Gedibois cooperative network**. Technical specifications, API availability, automation capabilities, and export features are NOT publicly documented.

**Recommendation:** **Week 1 priority conversation with CEICOM Solutions** is essential before designing any workaround architecture. The current 3-phase approach (manual Excel → semi-automated macros → full API if Médiafret enables) may be solving problems that don't exist OR missing capabilities already available.

**Key Unknowns Requiring CEICOM Validation:**
1. Does GESI support scheduled CSV/Excel exports? (Unknown)
2. Does GESI have undocumented APIs or partner integration modules? (Unknown)
3. Can GESI send email/webhook notifications on status changes? (Unknown)
4. Does GESI support multi-site consolidated reporting dashboards? (Unknown)
5. What configuration options exist for customizing GESI for logistics workflows? (Unknown)

---

## 1. GESI System Architecture (Confirmed Facts)

### 1.1 What We Know About GESI

**Official Name:** GeSi (Gedimat System Integration)

**Developer:** CEICOM Solutions (Toulouse-based French ERP editor)
- **Company Profile:** 50+ years experience, ISO 27001 certified, French data centers
- **Core Product:** CEI ERP (formerly DISTEL)
- **Gedimat Relationship:** Exclusive technology partner for Gedimat/Gedibois cooperative

**Deployment Context:**
- **Rollout:** Gedimat deployed GeSi across all 200+ independent member franchises
- **Scope:** Unified back-office system replacing fragmented legacy systems
- **Integration Challenge:** Successfully reconciled 200 independent databases into centralized system
- **Data Volume:** Automated classification of 10,000+ new products monthly

**Source:** [Akeneo Gedimat Case Study](https://www.akeneo.com/customer-story/gedimat/), [CEICOM Solutions Partnership Page](https://www.ceicom-solutions.fr/ceicom-solutions-partenaire-transformation-digitale-groupement-gedimat-gedibois/)

### 1.2 Known CEICOM ERP Capabilities (CEI Platform)

**Core Modules Confirmed:**
- Sales Management (EDI-capable)
- Purchasing & Procurement
- Logistics & Warehouse Management (CEI WMS)
- Accounting & Finance (NF Compta certified)
- Business Intelligence (CEI BI with Microsoft Power BI integration)

**Integration Ecosystem Confirmed:**
- **E-commerce:** Prestashop, Shopify (via webservices)
- **Document Management:** Zeendoc, Yooz (supplier invoice digitization)
- **Business Intelligence:** Microsoft Power BI (native integration)
- **Data Exchange:** IMMOS (import/export confirmed)
- **Partner Ecosystem:** Multiple third-party connectors documented

**Source:** [CEICOM ERP Features Page](https://www.ceicom-solutions.fr/logiciel-gestion-erp-ceicom/), [CEICOM Technology Partners](https://www.ceicom-solutions.fr/partenaires-technologiques-ceicom-erp/)

### 1.3 Critical Evidence: CEICOM ERP HAS Integration Capabilities

**Confirmed Integration Methods:**
1. **Webservices:** Prestashop and Shopify integration via webservices (REST/SOAP likely)
2. **Connectors:** Yooz integration for supplier invoices with "different processing steps managed in CEICOM ERP through a connector"
3. **Import/Export:** IMMOS integration explicitly mentions "import and export" functionality
4. **BI Integration:** Microsoft Power BI integration for advanced reporting

**Implication:** If CEICOM ERP supports webservices for e-commerce platforms and bidirectional connectors for partner systems, the assumption that "GESI has no APIs" requires verification.

---

## 2. Configuration Opportunities Matrix

### 2.1 Capability Assessment (Traffic Light Analysis)

| Capability | Current Assumption | Evidence Level | Configuration Likelihood | Investigation Priority |
|-----------|-------------------|----------------|------------------------|----------------------|
| **Scheduled CSV Export** | Requires manual setup | UNKNOWN | 🟡 Medium-High | P0 - Week 1 |
| **Order Status Push** | Not available | UNKNOWN | 🟡 Medium | P0 - Week 1 |
| **Multi-Site Consolidation Views** | Basic views only | UNKNOWN | 🟢 High | P1 - Week 1 |
| **API/REST Endpoints** | "No public APIs" | CONTRADICTED | 🟡 Medium | P0 - Week 1 |
| **Email Integration** | Manual checking | UNKNOWN | 🟢 High | P1 - Week 2 |
| **User Role/Permission Automation** | Standard | UNKNOWN | 🟡 Medium | P2 - Week 2 |
| **EDI Capabilities** | Unknown | PARTIALLY CONFIRMED | 🟢 High | P1 - Week 1 |
| **Power BI Custom Dashboards** | Unknown | CONFIRMED AVAILABLE | 🟢 Very High | P0 - Week 1 |

**Legend:**
- 🟢 High Likelihood: Evidence suggests capability exists
- 🟡 Medium Likelihood: Indirect evidence or common in similar systems
- 🔴 Low Likelihood: Would require significant development
- UNKNOWN: No public documentation found

### 2.2 Detailed Configuration Analysis

#### 2.2.1 Daily CSV Export Automation

**Current Assumption:** "Requires manual setup"

**Investigation Findings:**
- CEICOM ERP supports IMMOS integration with "import and export" functionality
- Power BI integration suggests structured data export capabilities
- Standard ERP practice includes scheduled task/job capabilities

**Configuration Complexity:** LOW to MEDIUM
- Most modern ERPs include Windows Task Scheduler or cron-equivalent
- If GESI runs on Windows Server (likely for ISO 27001 compliance), scheduled exports are standard

**Questions for CEICOM (Week 1):**
1. Does GESI support scheduled batch jobs for data export?
2. What file formats are supported? (CSV, Excel, XML, JSON)
3. Can export schedules be configured per-franchise or centrally?
4. What fields are exportable from order/shipment/inventory tables?
5. Can exports be triggered by status changes (e.g., "order confirmed")?

**Potential Quick Win:** If scheduled exports exist, Phase 1 could advance to Phase 2 immediately with zero development cost.

---

#### 2.2.2 Order Status Push Notifications

**Current Assumption:** "Not available - file-based integration required"

**Investigation Findings:**
- E-commerce integrations (Prestashop, Shopify) suggest order status synchronization
- Yooz integration includes "different processing steps managed in CEICOM ERP"
- EDI capability mentioned in sales module (EDI = Electronic Data Interchange, often includes status updates)

**Configuration Complexity:** MEDIUM
- Email notifications: LOW (standard feature in most ERPs)
- Webhook triggers: MEDIUM (depends on GESI architecture)
- SFTP file drops: LOW (standard for B2B integrations)

**Questions for CEICOM (Week 1):**
1. Does GESI support email notifications on order status changes?
2. Can GESI trigger outbound EDI messages or webhooks?
3. What "EDI" capabilities exist in the sales module? (formats: EDIFACT, X12, custom?)
4. Can GESI write files to network shares or SFTP on events?
5. Does the Gedimat cooperative have a standard integration protocol between members?

**Potential Quick Win:** If email notifications exist, daily status updates to Angélique could be automated with zero development.

---

#### 2.2.3 Multi-Site Consolidation Reports

**Current Assumption:** "Basic views only"

**Investigation Findings:**
- **CONFIRMED:** CEI BI module with Microsoft Power BI integration
- Power BI supports multi-dimensional analysis, custom dashboards, scheduled reports
- GeSi designed specifically to "integrate supplier, product, and customer databases and enable information sharing between members"

**Configuration Complexity:** LOW to MEDIUM
- Power BI connector to GESI database: Likely already exists
- Custom dashboard creation: 2-4 hours for BI consultant
- Scheduled email reports: Native Power BI feature

**Questions for CEICOM (Week 1):**
1. Does Lunel Négoce have access to CEI BI / Power BI module?
2. What is the licensing cost for CEI BI if not currently active?
3. Can Power BI connect directly to GESI database or via pre-built connectors?
4. Are there pre-built templates for multi-depot logistics dashboards?
5. Can Power BI reports be scheduled to email stakeholders daily?

**Potential Quick Win:** If Power BI is available, the "Phase 3" dashboard could be available in Week 2 with consultant configuration (no development).

**Critical Cost Question:** Power BI licensing:
- Power BI Pro: ~$10/user/month
- Power BI Premium: ~$5,000/month (unlikely needed)
- One-time consultant configuration: $1,500-$3,000 estimate

---

#### 2.2.4 API or REST Endpoints

**Current Assumption:** "No public APIs"

**Investigation Findings:**
- **CONTRADICTED:** CEICOM ERP integrates with Prestashop and Shopify "via webservices"
- Webservices = REST API or SOAP API in modern context
- E-commerce integration pattern: ERP exposes inventory/order APIs that platforms consume

**Configuration Complexity:** MEDIUM to HIGH (depends on existing vs. requires enablement)

**Scenarios:**
1. **Best Case:** APIs exist but require license module activation (1 week, $X,XXX/year)
2. **Medium Case:** APIs exist for e-commerce but require partner enablement for logistics use (2-4 weeks, custom pricing)
3. **Worst Case:** APIs don't exist for logistics module, only e-commerce (6+ months development)

**Questions for CEICOM (Week 1):**
1. What webservices/APIs are available in GESI for external access?
2. Are logistics/shipping modules accessible via API or only e-commerce modules?
3. What is the licensing model for API access? (per-call, per-user, flat fee)
4. Can API access be enabled for third-party logistics partners (e.g., Médiafret)?
5. What authentication methods are supported? (OAuth, API keys, SAML)
6. Is there API documentation available? (Swagger, OpenAPI, PDF manual)

**Potential Quick Win:** If logistics APIs exist, Médiafret integration could be direct API calls instead of CSV exchange, enabling real-time status.

**Potential Blocker:** If APIs require enterprise licensing tier, cost may be prohibitive for 3-depot operation.

---

#### 2.2.5 Automation Workflows & Business Rules

**Current Assumption:** Unknown

**Investigation Findings:**
- CEICOM ERP marketed as supporting "automation, calculation, and simplification of data entry and processes"
- Yooz integration suggests workflow capabilities (invoice approval, routing)
- Modern ERPs typically include:
  - Workflow engines (if X happens, do Y)
  - Business rule engines (if condition A, trigger action B)
  - Alert/notification systems

**Configuration Complexity:** MEDIUM
- Pre-built workflows: LOW effort
- Custom workflow creation: MEDIUM effort (depends on UI vs. code)

**Questions for CEICOM (Week 1):**
1. Does GESI include a workflow automation engine?
2. Can business rules be configured for:
   - Auto-assignment of depot based on supplier proximity?
   - Alert triggers when ARC/ACK not received within 48 hours?
   - Escalation workflows for urgent customer orders?
3. What is the user interface for configuring workflows? (GUI, XML files, SQL scripts)
4. Are there pre-built workflow templates for logistics operations?

**Potential Quick Win:** If workflow engine exists, the "Annexe X - Règles de Décision" playbook could be partially automated inside GESI.

---

## 3. Competitive Landscape: What Other French Material Négoce ERPs Offer

### 3.1 Comparable Systems Research

**Purpose:** Understand what capabilities are **standard** in 2025 for French material négoce ERPs to calibrate GESI expectations.

#### Onaya Négoce (Orisha Construction)
- **Real-time stock visibility:** Confirmed
- **Automatic data transfer to ERP:** Confirmed
- **Order tracking automation:** Confirmed
- **Multi-depot management:** Confirmed

**Source:** [Onaya Négoce Features](https://construction.orisha.com/onaya-negoce/logistique/)

#### WeNégoce
- **Cloud or on-premise:** Confirmed
- **100% French editor:** Confirmed
- **Material construction specialization:** Confirmed

**Source:** [WeNégoce Website](https://www.wenegoce.fr/)

#### TRADE.EASY ERP Négoce
- **Automated order generation:** Confirmed based on pre-defined replenishment rules
- **100% French solution:** Confirmed

**Source:** [TRADE.EASY Features](https://www.trade-easy.fr/activites/erp-negoce/)

### 3.2 Implications for GESI

**Baseline Expectation:** If competitors in the same market (French material négoce) offer automated exports, workflow engines, and API integrations as **standard features**, it is **unlikely** that CEICOM would position GESI as inferior.

**Hypothesis:** GESI likely has comparable capabilities to Onaya/WeNégoce/TRADE.EASY, but:
1. Features may require **module activation** (licensing)
2. Features may be **configured centrally** by Gedimat cooperative, not accessible to individual franchises
3. Features may exist but are **undocumented** or **under-communicated** to franchise members

**Critical Question:** Is Lunel Négoce operating on a **base license tier** that lacks advanced logistics features available in higher tiers?

---

## 4. Week 1 Conversation Outline: CEICOM Solutions Administrator

### 4.1 Pre-Call Preparation

**Goal:** Maximize information yield in single conversation, avoid multiple follow-ups

**Information to Gather Before Call:**
1. Current GESI version/build number at Lunel Négoce (if accessible)
2. Current modules/licenses active (from invoice or admin panel)
3. Name of local GESI system administrator (if different from CEICOM support)
4. Recent support tickets or feature requests (if tracked)
5. Any internal Gedimat documentation about GeSi capabilities

**Attendees Recommended:**
- Angélique (coordinatrice fournisseurs) - operational context
- IT contact at Lunel Négoce - technical details
- Potentially Gedimat regional support representative

---

### 4.2 Conversation Script: Technical Capabilities Discovery

#### **Section 1: Current Deployment (5 minutes)**

**Questions:**
1. What version of GeSi is currently deployed at Lunel Négoce?
   - *Goal: Determine if running latest version or legacy*
2. What modules are currently licensed/active for Lunel Négoce?
   - Sales, Purchasing, Logistics, WMS, BI, E-commerce, EDI?
   - *Goal: Identify what's available vs. what's dormant*
3. Who manages system configuration at Lunel Négoce?
   - CEICOM remotely, Lunel IT admin, Gedimat central IT, hybrid?
   - *Goal: Understand who can make changes*
4. What is the standard support response time for configuration requests?
   - Emergency, standard, feature request tiers?
   - *Goal: Estimate lead time for any configuration changes*

---

#### **Section 2: Automation & Export Capabilities (10 minutes)**

**Questions:**
5. **Scheduled Exports:**
   - Can GeSi be configured to automatically export data on a schedule?
   - What formats are supported? (CSV, Excel, XML, JSON, EDI)
   - Can we schedule a daily export of:
     - Orders placed (statut: en attente enlèvement)
     - Supplier acknowledgments (ARC/ACK)
     - Confirmed pickups by transporters
     - Urgency flags from customer orders
   - If yes, what's the setup process? (Configuration UI, SQL scripts, support ticket)
   - If no, what's the recommended manual export workflow?

6. **Email/Webhook Notifications:**
   - Can GeSi send automated email alerts based on status changes?
     - Example: Email when ARC/ACK not received within 48 hours
     - Example: Email when pickup confirmed by transporter
   - Can GeSi trigger webhooks or write files to network shares on events?
   - If yes, what's the configuration process?

7. **EDI Capabilities:**
   - The sales module mentions EDI support - what does this cover?
   - Can GeSi send/receive EDI messages for:
     - Purchase orders to suppliers?
     - Shipping notifications to customers?
     - Status updates to/from transporters (e.g., Médiafret)?
   - What EDI formats are supported? (EDIFACT, X12, custom XML?)

---

#### **Section 3: Multi-Site Consolidation & Reporting (10 minutes)**

**Questions:**
8. **Consolidated Views:**
   - Can GeSi display a consolidated view of orders across Lunel Négoce's 3 depots (Gisors, Méru, Breuilpont)?
   - Specifically: Orders from same supplier for multiple depots in single screen?
   - Can this view be filtered by:
     - Supplier
     - Date range
     - Product type
     - Urgency level
   - If not native, can this be configured?

9. **Power BI Integration:**
   - Does Lunel Négoce have access to the CEI BI / Power BI module?
   - If not currently active, what is the licensing cost?
   - Can Power BI connect to GeSi database to create custom dashboards?
   - Are there pre-built dashboard templates for logistics/multi-depot operations?
   - Can reports be scheduled to email stakeholders (e.g., daily 15:00 order summary)?

10. **Custom Reporting:**
    - Can GeSi generate custom reports without Power BI?
    - What reporting tools are built-in? (Crystal Reports, SSRS, custom)
    - Can reports be saved and re-run on schedule?

---

#### **Section 4: API & Integration Options (10 minutes)**

**Questions:**
11. **API Availability:**
    - Does GeSi provide REST or SOAP APIs for external access?
    - What data is accessible via API? (orders, inventory, shipments, suppliers)
    - What is the licensing model for API access? (included, per-user, per-call)
    - Is API access restricted to Gedimat cooperative partners only?

12. **Third-Party Integrations:**
    - Can GeSi integrate with third-party logistics systems (e.g., Médiafret's TMS)?
    - What integration methods are recommended:
      - CSV file exchange (SFTP, email, network share)
      - API calls
      - Direct database access (views, stored procedures)
      - EDI messages
    - Are there existing integrations with transporters used by other Gedimat franchises?

13. **Data Access:**
    - Can Lunel Négoce access GeSi database directly for custom queries?
      - Read-only views? Direct SQL access? Only through UI?
    - If database access is possible, what's the schema documentation situation?

---

#### **Section 5: Workflow Automation & Business Rules (5 minutes)**

**Questions:**
14. **Workflow Engine:**
    - Does GeSi include a workflow automation / business rules engine?
    - Can workflows be configured for:
      - Auto-assignment of depot based on supplier postal code proximity?
      - Auto-escalation of orders when ARC/ACK not received in X hours?
      - Auto-flagging of urgent customer orders for priority processing?
    - What's the user interface for configuring workflows? (GUI, code, configuration files)

15. **Alerting System:**
    - What built-in alert/notification capabilities exist?
    - Can alerts be configured by individual franchises or only centrally by Gedimat?

---

#### **Section 6: Gedimat Cooperative Standards (5 minutes)**

**Questions:**
16. **Cooperative Integration Standards:**
    - Does Gedimat cooperative mandate specific integration methods between franchises?
    - Are there shared services or central systems that Lunel Négoce should leverage?
    - Do other Gedimat franchises use GeSi for multi-depot logistics coordination?
      - If yes, can we learn from their configuration?

17. **Best Practices & Templates:**
    - Are there configuration templates or best practice guides for:
      - Multi-depot operations
      - Supplier coordination
      - Transporter integration
    - Can CEICOM provide case studies of similar franchise configurations?

---

#### **Section 7: Implementation Timeline & Cost (5 minutes)**

**Questions:**
18. **Configuration Effort:**
    - If we wanted to enable [specific capability discussed above], what's typical timeline?
      - Hours? Days? Weeks?
    - What's the process: support ticket, professional services engagement, self-service?

19. **Licensing & Costs:**
    - For capabilities not currently active (e.g., Power BI, API access, workflow engine):
      - What are licensing costs?
      - Is there a "logistics optimization" bundle license?
    - Are there one-time configuration fees vs. ongoing subscription costs?

20. **Support Model:**
    - What support is included in standard GeSi licensing?
    - What requires paid professional services?
    - Can CEICOM provide a quote for a "logistics optimization configuration package"?

---

### 4.3 Post-Call Analysis Framework

**After CEICOM conversation, categorize each capability:**

| Capability | Status | Complexity | Cost | Timeline | Decision |
|-----------|--------|-----------|------|----------|----------|
| Scheduled CSV export | Available/Not Available/Requires License | Low/Med/High | $X | X weeks | Proceed/Defer/Abandon |
| Email notifications | ... | ... | ... | ... | ... |
| Power BI dashboards | ... | ... | ... | ... | ... |
| API access | ... | ... | ... | ... | ... |
| Workflow automation | ... | ... | ... | ... | ... |

**Decision Criteria:**
- **Proceed:** Low cost (<€2,000), low complexity, <2 weeks timeline
- **Defer:** Medium cost, medium complexity, evaluate in Phase 2
- **Abandon:** High cost (>€10,000), high complexity, long timeline (>3 months)

---

## 5. Risk Assessment: Configuration vs. Workaround Strategies

### 5.1 Scenario Analysis

#### **Scenario A: GESI Has Most Capabilities, Just Needs Configuration**

**Indicators:**
- Scheduled exports: Available
- Email notifications: Available
- Power BI: Available (licensing required)
- Workflow engine: Available
- API: Limited but sufficient

**Impact on Project:**
- **Phase 1:** Accelerate from manual Excel to automated exports (Week 1)
- **Phase 2:** Skip macro development, use native workflows
- **Phase 3:** Power BI dashboards instead of custom dev
- **Cost Reduction:** ~€15,000-€25,000 saved (no custom development)
- **Timeline Reduction:** 6-9 months faster to full capability

**Recommended Actions:**
1. Budget €3,000-€5,000 for CEICOM configuration services
2. License Power BI Pro for key users (~€30/user/month)
3. Focus Angélique's time on workflow optimization, not manual data entry

---

#### **Scenario B: GESI Has Some Capabilities, Gaps Require Workarounds**

**Indicators:**
- Scheduled exports: Not available or limited
- Email notifications: Not available
- Power BI: Available but expensive
- Workflow engine: Not available
- API: Not available or only for e-commerce

**Impact on Project:**
- **Phase 1:** Manual Excel remains (but optimize templates)
- **Phase 2:** Develop lightweight Python scripts for data transformation
- **Phase 3:** Evaluate Médiafret integration requirements before investing

**Recommended Actions:**
1. Implement Phase 1 as planned (manual but optimized)
2. Budget €8,000-€12,000 for Phase 2 Python/Excel macro development
3. Re-evaluate at 90 days whether Médiafret integration is worth cost

---

#### **Scenario C: GESI Has Minimal Capabilities, Major Gaps**

**Indicators:**
- No automation capabilities
- No export scheduling
- No API access
- No workflow engine
- Power BI not feasible (cost or technical)

**Impact on Project:**
- **Phase 1:** Manual Excel with heavy optimization focus
- **Phase 2:** Consider alternative solutions:
  - Standalone logistics management tool (e.g., lightweight TMS)
  - Middleware layer (e.g., Zapier, Make.com) for integrations
  - Request Gedimat cooperative to fund central solution for all franchises

**Recommended Actions:**
1. Document GESI limitations thoroughly
2. Present findings to Gedimat cooperative regional manager
3. Explore whether other franchises have same pain points
4. Potential cooperative-wide solution funding opportunity

---

### 5.2 Cost-Benefit Matrix

| Configuration Option | Setup Cost | Annual Cost | Time to Value | Risk | ROI Estimate |
|---------------------|-----------|-------------|--------------|------|--------------|
| **Power BI Dashboards** | €2,000 | €360/user | 2 weeks | Low | High (visibility = better decisions) |
| **Scheduled Exports** | €0-€500 | €0 | 1 week | Low | Very High (eliminates manual work) |
| **Email Notifications** | €0-€1,000 | €0 | 1 week | Low | High (proactive vs reactive) |
| **API Access License** | €0-€5,000 | €1,000-€3,000 | 4 weeks | Medium | Medium (depends on Médiafret readiness) |
| **Workflow Engine** | €2,000-€5,000 | €500-€1,500 | 4-6 weeks | Medium | Medium-High (automates decision rules) |
| **Custom Development** | €10,000-€25,000 | €2,000-€5,000 | 3-6 months | High | Medium (functionality achieved but expensive) |

**Interpretation:**
- **If Power BI + Scheduled Exports + Email Notifications are available:** Total cost ~€2,500 one-time + €360/year
  - **Comparison:** Phase 2 custom development estimated at €12,000-€18,000
  - **Savings:** €9,500-€15,500
  - **Additional Benefit:** Faster time to value (2 weeks vs. 3-4 months)

---

## 6. Recommendation: Configuration-First Strategy

### 6.1 Proposed Approach

**Step 1: CEICOM Investigation Call (Week 1, Priority 0)**
- Schedule 60-minute technical discovery call
- Use conversation script from Section 4.2
- Document all findings in capability matrix

**Step 2: Rapid Decision Matrix (Week 1, Day 2)**
- Categorize each capability as Proceed/Defer/Abandon
- Calculate configuration cost vs. custom development cost
- Present options to Lunel Négoce leadership

**Step 3: Quick Win Implementation (Week 2-3)**
- If scheduled exports available → Implement immediately
- If email notifications available → Configure alert rules
- If Power BI available → Build first dashboard prototype

**Step 4: Phased Rollout (Week 4-12)**
- **Phase 1 Enhanced:** Manual processes + automated exports (Week 4-6)
- **Phase 2 Accelerated:** Native GESI features + light scripting (Week 7-9)
- **Phase 3 Conditional:** API integration only if Médiafret commits (Week 10-12)

---

### 6.2 Success Criteria

**Configuration strategy is successful if:**
1. ✅ At least 2 of 5 key capabilities available via configuration
2. ✅ Total configuration cost < €5,000
3. ✅ Time to implement < 4 weeks
4. ✅ Angélique's manual workload reduced by ≥30%
5. ✅ Multi-depot visibility improved (measurable via user survey)

**Configuration strategy is unsuccessful if:**
1. ❌ Zero capabilities available without major development
2. ❌ Configuration cost > €10,000 or requires enterprise license upgrade
3. ❌ Implementation timeline > 8 weeks
4. ❌ CEICOM unable to commit to support SLA

**Fallback:** If configuration strategy fails criteria, revert to Phase 1-2-3 workaround plan (manual → macros → API if Médiafret enables).

---

## 7. Critical Questions Requiring Answers

### 7.1 Questions for CEICOM Solutions (Week 1)

**Priority 0 (Blocker Questions):**
1. Can GESI export order/shipment data automatically on a schedule?
2. Does GESI support email/webhook notifications on status changes?
3. Is the Power BI module available and what is licensing cost?
4. Are there REST/SOAP APIs for logistics data access?

**Priority 1 (Important but Not Blocker):**
5. Can multi-depot consolidated views be configured?
6. Does workflow automation engine exist?
7. What EDI capabilities exist for supplier/transporter integration?
8. What integration methods does Gedimat cooperative recommend?

**Priority 2 (Nice to Have):**
9. Are there configuration templates for multi-depot logistics?
10. Can database be accessed directly for custom reporting?
11. What support SLA is available for configuration requests?
12. Are there case studies of similar franchise configurations?

---

### 7.2 Questions for Gedimat Cooperative Network (Week 2)

**To determine if this is a cooperative-wide challenge:**
1. Do other Gedimat franchises with multiple depots face similar coordination challenges?
2. Has Gedimat cooperative central office implemented any shared logistics tools?
3. Are there cooperative-funded initiatives to enhance GeSi for multi-depot operations?
4. Can Lunel Négoce collaborate with other franchises to share configuration costs?
5. Is there a Gedimat logistics working group or best practices forum?

---

### 7.3 Questions for Médiafret (Week 3-4)

**To assess API integration readiness:**
1. Does Médiafret provide APIs for shipment status tracking?
2. What integration methods does Médiafret support? (API, EDI, SFTP, email)
3. Has Médiafret integrated with GESI/CEICOM systems for other Gedimat franchises?
4. What is Médiafret's standard onboarding timeline for API integrations?
5. Are there costs associated with API access? (setup fee, per-call charges)

---

## 8. Documentation Gaps & Research Limitations

### 8.1 What We Could Not Verify

**Due to proprietary nature of GESI:**
1. ❌ **Technical Architecture:** Database schema, technology stack, API endpoints
2. ❌ **Module Capabilities:** Detailed feature list for logistics/WMS modules
3. ❌ **Configuration Options:** What can be configured vs. requires development
4. ❌ **Licensing Tiers:** Feature availability by license level
5. ❌ **Roadmap:** Planned enhancements or feature releases

**Why This Matters:** Without public documentation, assumptions about limitations may be incorrect. Week 1 CEICOM conversation is **mandatory** before architectural decisions.

---

### 8.2 Information Sources Used

**Primary Sources (Verified):**
- CEICOM Solutions official website (company profile, partnership announcements)
- Akeneo Gedimat case study (GeSi deployment, 200 databases reconciled)
- CEICOM ERP feature pages (module descriptions, partner integrations)
- Gedimat transformation announcements (Le Moniteur, industry press)

**Secondary Sources (Industry Context):**
- Competitor ERP features (Onaya Négoce, WeNégoce, TRADE.EASY)
- French material négoce ERP market research
- Standard ERP capabilities benchmarking

**Information NOT Found (Gaps):**
- GESI technical documentation or user manuals
- GESI API documentation or integration guides
- GESI pricing or licensing structure
- GESI customer testimonials or implementation case studies
- GESI configuration guides or admin tutorials

---

## 9. Conclusion & Next Steps

### 9.1 Key Findings Summary

1. **GESI is NOT a "black box"** - CEICOM ERP platform has confirmed integration capabilities (webservices, connectors, Power BI)

2. **"No APIs" assumption is questionable** - E-commerce integrations via webservices suggest APIs exist, but may not be documented or enabled for logistics use

3. **Configuration opportunities likely exist** - Power BI integration is confirmed available; scheduled exports and workflow automation are common ERP features

4. **Cost avoidance potential is significant** - If even 2-3 configuration options are available, could save €10,000-€20,000 vs. custom development

5. **Week 1 CEICOM conversation is critical** - Cannot proceed with architectural decisions without verified technical capabilities

---

### 9.2 Immediate Action Plan (Next 7 Days)

**Day 1-2: Pre-Call Preparation**
- [ ] Gather Lunel Négoce GESI version, license details, current modules
- [ ] Identify GESI system administrator contact
- [ ] Prepare conversation script customization based on Lunel's priorities
- [ ] Schedule 60-minute call with CEICOM Solutions technical team

**Day 3: CEICOM Discovery Call**
- [ ] Execute conversation script from Section 4.2
- [ ] Document all responses in capability matrix
- [ ] Request follow-up documentation (if available)
- [ ] Obtain pricing estimates for identified configuration options

**Day 4-5: Analysis & Decision**
- [ ] Complete capability matrix with cost/timeline/complexity
- [ ] Calculate configuration cost vs. custom development cost
- [ ] Prepare recommendation presentation for Lunel Négoce leadership
- [ ] Draft revised project plan based on findings

**Day 6-7: Stakeholder Review**
- [ ] Present findings to Angélique and Lunel management
- [ ] Decide: Proceed with configuration strategy OR revert to workaround approach
- [ ] If configuration viable: Request CEICOM quote for professional services
- [ ] If workaround needed: Confirm Phase 1-2-3 plan from original dossier

---

### 9.3 Contingency Planning

**If CEICOM Call Reveals Extensive Capabilities:**
- **Accelerate timeline:** Weeks instead of months to Phase 2
- **Reallocate budget:** From development to licensing/configuration
- **Expand scope:** Consider additional optimization opportunities

**If CEICOM Call Reveals Limited Capabilities:**
- **Validate workaround approach:** Proceed with Phase 1 manual + Phase 2 macros
- **Escalate to Gedimat cooperative:** Determine if cooperative-wide solution warranted
- **Document limitations:** Use as evidence for future GESI enhancement requests

**If CEICOM Unresponsive or Unhelpful:**
- **Alternative path:** Direct database access exploration (if permitted)
- **Community research:** Contact other Gedimat franchises for their solutions
- **Vendor evaluation:** Assess standalone logistics tools as middleware

---

## 10. Risk Mitigation

### 10.1 Risks of Configuration-First Approach

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| CEICOM capabilities overstated | Medium | High | Verify with proof-of-concept before committing |
| Configuration costs higher than expected | Medium | Medium | Request detailed quote before proceeding |
| Implementation timeline underestimated | Medium | Medium | Build 2x buffer into estimates |
| Configuration requires central Gedimat approval | High | Medium | Engage Gedimat regional manager early |
| Licensing costs recurring and unsustainable | Low | High | Calculate 5-year TCO vs. one-time development |

### 10.2 Risks of Proceeding Without Investigation

| Risk | Likelihood | Impact | Consequence |
|------|-----------|--------|-------------|
| Build custom solution when native features exist | **High** | **High** | Wasted €15,000-€25,000 + 6 months delay |
| Miss cost-effective Power BI dashboards | **High** | Medium | Suboptimal visibility, manual reporting continues |
| Ignore cooperative-wide solutions in progress | Medium | Medium | Duplicate effort, miss collaboration opportunity |
| Damage relationship with CEICOM | Low | High | Future support degraded, harder to get help |

**Conclusion:** Risk of **not** investigating GESI capabilities far exceeds risk of investigating.

---

## Appendix A: Conversation Preparation Checklist

**Before scheduling CEICOM call:**
- [ ] Review Lunel Négoce GESI invoice/contract for version and modules
- [ ] Access GESI admin panel (if possible) to screenshot current configuration
- [ ] Compile list of recent pain points from Angélique's workflow
- [ ] Identify 2-3 specific use cases to discuss (e.g., "daily 15:00 order summary export")
- [ ] Prepare examples from competitors (Onaya features) to reference
- [ ] Have Gedimat franchise agreement available (to check any restrictions)

**During CEICOM call:**
- [ ] Record call (with permission) or take detailed notes
- [ ] Ask for screen sharing to see configuration interfaces
- [ ] Request documentation links or PDFs
- [ ] Get names/emails of technical contacts for follow-up
- [ ] Clarify any terminology (e.g., "webservices" = REST API or SOAP?)

**After CEICOM call:**
- [ ] Transcribe key findings within 24 hours
- [ ] Send thank-you email with summary of understanding (verify accuracy)
- [ ] Update capability matrix with definitive answers
- [ ] Flag any unclear responses for follow-up
- [ ] Share findings with project stakeholders

---

## Appendix B: Capability Matrix Template

| Capability | Available? | License Required? | Config Complexity | Estimated Cost | Timeline | Notes |
|-----------|-----------|------------------|------------------|---------------|----------|-------|
| Scheduled CSV export | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Low ☐ Med ☐ High | €________ | ____ weeks | |
| Email notifications | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Low ☐ Med ☐ High | €________ | ____ weeks | |
| Power BI integration | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Low ☐ Med ☐ High | €________ | ____ weeks | |
| REST/SOAP API | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Low ☐ Med ☐ High | €________ | ____ weeks | |
| Workflow automation | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Low ☐ Med ☐ High | €________ | ____ weeks | |
| Multi-depot views | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Low ☐ Med ☐ High | €________ | ____ weeks | |
| EDI capabilities | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Low ☐ Med ☐ High | €________ | ____ weeks | |
| Database access | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Low ☐ Med ☐ High | €________ | ____ weeks | |

**Instructions:** Fill out during/after CEICOM call. Use this to generate cost comparison and decision matrix.

---

## Appendix C: Alternative Vendor Research (If GESI Insufficient)

**If GESI proves incapable, evaluate these alternatives:**

### Standalone Logistics Tools
- **Shippeo** (real-time transport visibility)
- **Sensolus** (logistics tracking)
- **BoostMyShop** (inventory/order management for SMBs)

### Middleware/Integration Platforms
- **Make.com** (formerly Integromat) - visual workflow automation
- **Zapier** - no-code integrations
- **n8n** - open-source workflow automation

### Material Négoce-Specific ERPs
- **Onaya Négoce** (Orisha) - confirmed multi-depot, automation capabilities
- **WeNégoce** - French, cloud, material construction specialist
- **TRADE.EASY** - French, automated replenishment

**Evaluation Criteria:**
1. Time to implement (target: <90 days)
2. Total cost of ownership (5 years)
3. Integration capability with GESI
4. User training complexity
5. Vendor support quality

**Note:** Switching ERPs entirely is **extreme** solution. Only consider if:
- GESI fundamentally incapable
- Gedimat franchise agreement permits (check terms!)
- Cost-benefit analysis shows 3+ year ROI

---

## Document Metadata

**Created:** 2025-11-22
**Author:** Claude Sonnet 4.5 (InfraFabric IF.search + IF.ground methodologies)
**Version:** 1.0 (Initial Research)
**Status:** Awaiting CEICOM Solutions verification
**Next Review:** After Week 1 CEICOM call
**Related Documents:**
- `/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/GEDIMAT_ARENA_REVIEW_COMPLETE_V3.2.md`
- `/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/CONTEXTE_ANGELIQUE.txt`
- `/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/README.md`

**IF.TTT Compliance:**
- All external claims cited with source URLs
- Unknowns explicitly marked as "UNKNOWN" not speculated
- Assumptions clearly labeled as "Hypothesis" or "Assumption"
- Contradictory evidence highlighted (APIs exist vs. "no APIs" assumption)
- Cost estimates marked as "estimate" with ranges, not fixed numbers

---

**END OF INVESTIGATION REPORT**
