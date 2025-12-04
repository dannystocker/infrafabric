# IF.Contract Frontend Development Specification Brief

**Document Type:** Frontend Development Specification
**Date:** November 28, 2025
**Status:** Complete - Ready for Frontend Development
**Based On:** Comprehensive session analysis of IF.Legal Corpus & ContractGuard system

---

## Executive Summary

**IF.Contract** (formerly ContractGuard) is a multi-jurisdiction legal contract analysis platform that uses a sophisticated five-dimension risk rating system to evaluate contracts and provide jurisdiction-specific guidance backed by a production-ready legal corpus of 290+ documents across 9 jurisdictions.

The frontend must support contract upload, five-dimension risk visualization, clause-level analysis, and jurisdiction-specific recommendations using a self-hosted ChromaDB vector database containing 55,778+ legal document embeddings.

---

## Core Application Components for Frontend

### 1. CONTRACT UPLOAD & PROCESSING
- **Upload Interface:** Drag-and-drop file upload (PDF, DOCX, TXT)
- **File Validation:** Type checking, size limit (50 MB), encoding detection
- **Progress Tracking:** Real-time analysis progress with step indicator
- **Status Indicators:** Processing state (uploading → parsing → analyzing → generating report)

### 2. FIVE-DIMENSION RISK RATING SYSTEM
Frontend must display risk scores across these dimensions:

#### Dimension 1: Intellectual Property Risk (0-100)
- Assesses IP assignment scope, moral rights waivers, AI training rights
- **Green (0-25):** Work-for-hire limited to business deliverables
- **Yellow (26-50):** Assignment broader than typical
- **Red (51-100):** Total assignment, AI rights, or unconditional waivers

#### Dimension 2: Termination Fairness (0-100)
- Evaluates termination asymmetry, notice periods, compensation-in-lieu
- **Green (0-25):** Symmetric notice, grounds specified, compensation provided
- **Yellow (26-50):** Modest asymmetry or vague grounds
- **Red (51-100):** Immediate company termination, long contractor notice

#### Dimension 3: Liability & Indemnity (0-100)
- Examines liability caps, indemnification obligations, insurance requirements
- **Green (0-25):** Balanced indemnity, capped liability, force majeure
- **Yellow (26-50):** Broad indemnity or high insurance requirements
- **Red (51-100):** Unlimited indemnity, no caps, contractor bears all losses

#### Dimension 4: Restrictive Covenants (0-100)
- Evaluates non-competes, non-solicitation clauses, confidentiality scope
- **Green (0-25):** Reasonable restrictions (6-mo non-compete, limited geographic scope)
- **Yellow (26-50):** Moderate restrictions with some reasonableness
- **Red (51-100):** Excessive (24+ month worldwide, indefinite non-solicitation)

#### Dimension 5: Commercial Terms & Payment (0-100)
- Analyzes payment terms, deductions, currency/tax risk allocation
- **Green (0-25):** Payment within 30 days, no unilateral deductions
- **Yellow (26-50):** Longer payment terms or limited deduction rights
- **Red (51-100):** 60+ day payment, unilateral deductions, contractor absorbs risk

**Frontend Visualization:**
- Radar chart showing all 5 dimensions
- Color-coded severity (green/yellow/red)
- Overall contract risk score (0-100 aggregate)
- Detailed breakdown for each dimension

### 3. CLAUSE DETECTION & EXTRACTION (41 Categories)
Display identified clauses in structured format:

**Foundational Clauses**
- Definitions, Entire Agreement, Effective Dates, Counterparts

**Termination & Lifecycle**
- Expiration/Termination, Termination for Cause/Convenience, Survival, Auto-Renewal

**Liability & Risk**
- Cap on Liability, Limitation, Indemnification, Insurance, Force Majeure, Cross Liability

**IP & Confidentiality**
- Intellectual Property, Licenses, Confidentiality/NDA, Source Code, Residuals

**Business Terms**
- Fees, Price Restrictions, Most Favored Nation, Exclusivity, Subcontracting

**Obligations & Control**
- Representations & Warranties, Audit Rights, Consent & Approval, Data Processing

**Legal Framework**
- Governing Law, Arbitration, Dispute Resolution, Severability, Notice

**Special Provisions**
- Non-Compete, Non-Solicitation

**Frontend Display:**
- Clause extraction table (sortable, filterable)
- Show clause type, risk level, text snippet, location in contract
- Link each clause to relevant legal corpus document

### 4. JURISDICTION DETECTION & LEGAL CORPUS LINKING
- **Auto-Detection:** Parse governing law clause to identify jurisdiction
- **Manual Override:** Allow user to specify jurisdiction if auto-detection uncertain
- **Supported Jurisdictions:**
  - 🇺🇸 US Federal (125+ documents)
  - 🇬🇧 United Kingdom (49 documents)
  - 🇪🇸 Spain (38 documents)
  - 🇪🇺 European Union (12 documents)
  - 🇨🇦 Canada (10 documents)
  - 🇫🇷 France (8 documents)
  - 🇩🇪 Germany (10 documents)
  - 🇦🇺 Australia (7 documents)
  - 🇨🇦 Quebec (4 documents - bilingual FR/EN)

**Frontend Display:**
- Show detected jurisdiction with confidence score
- Display applicable legal vertical (housing, employment, IP, insurance, etc.)
- Show relevant legal corpus documents

### 5. OUTPUT FORMATS (Frontend Must Support)

#### A. Executive Summary
- 1-2 page contract overview
- Risk assessment by dimension
- Top 3-5 critical findings with severity indicators
- Recommended negotiation priorities
- Key legal references from IF.Legal Corpus
- **Export:** PDF, Markdown, HTML

#### B. Clause Extraction Table
- All identified clauses in structured format
- Columns: Clause Type, Risk Level, Text, Location, Legal Citation
- **Export:** CSV, Markdown, Excel

#### C. Risk Heatmaps
- 5-dimension radar chart visualization
- Color-coded severity (green/yellow/red)
- Section-by-section risk breakdown
- **Export:** PNG, SVG, Interactive HTML

#### D. Negotiation Playbooks
- Jurisdiction-specific legal standards
- Fair alternative clause language (from corpus)
- Negotiation tactics by risk area
- Precedents and case law citations
- Power dynamics analysis
- **Export:** PDF, Markdown, HTML

#### E. Citation Reference List
- IF.TTT citations for all legal references
- Document names, sections, source URLs
- SHA-256 hashes for integrity verification
- **Export:** JSON, Markdown, CSV

#### F. Comparative Analysis Report
- Side-by-side clause comparison (2+ contracts)
- Highlighted differences
- Risk delta between contracts
- Recommended alignment strategies
- **Export:** PDF, Markdown, HTML

### 6. IF.TTT FRAMEWORK INTEGRATION
Every legal reference must link to IF.TTT citations:

```json
{
  "citation_id": "if://citation/[uuid]",
  "citation_status": "verified",
  "document_name": "UK Employment Rights Act 1996",
  "jurisdiction": "uk",
  "legal_vertical": "employment",
  "authoritative_source": {
    "url": "Official UK government source",
    "verification_method": "document_download_from_official_source"
  },
  "local_verification": {
    "sha256": "Document integrity hash",
    "local_path": "/home/setup/if-legal-corpus/raw/uk/..."
  }
}
```

Frontend must display:
- Citation ID with link to full provenance chain
- Source document name and jurisdiction
- Relevant sections/articles
- Verification status badge (verified/disputed/revoked)

### 7. INDUSTRY-SPECIFIC ANALYSIS
Pre-configured analysis profiles for:
- **Technology/Software Development:** Focus on IP assignment, AI rights
- **Consulting:** Deliverables, KPIs, termination conditions
- **Creative Services:** Moral rights, portfolio usage, derivative works
- **Sales:** Commission structures, client ownership, territories
- **Professional Services:** Confidentiality, non-compete, liability

**Frontend Display:**
- Industry selector (dropdown or radio buttons)
- Industry-specific analysis module
- Benchmark against industry standards from legal corpus

### 8. BILINGUAL SUPPORT
Full support for French/English (Quebec) contracts:
- Language detection on upload
- Bilingual clause display (side-by-side)
- Jurisdiction-specific analysis for bilingual jurisdictions
- French/English legal corpus references

---

## Technical Stack Recommendations

### Backend Services Provided
- **Legal Corpus:** ChromaDB (self-hosted vector database)
- **Vectors:** 55,778+ indexed legal document embeddings
- **Citations:** IF.TTT citation system with SHA-256 verification
- **Test Data:** 1,841 test contracts (1,329 synthetic + 512 CUAD real)

### Frontend Technology Stack (Suggested)
- **Framework:** React, Vue.js, or Svelte
- **Visualization:** D3.js or Chart.js (for radar chart/heatmaps)
- **Document Upload:** Dropzone.js or similar
- **Export:** React-PDF, html2pdf for document generation
- **State Management:** Redux, Vuex, or Pinia
- **Styling:** Tailwind CSS or Material UI
- **API Communication:** Axios or Fetch API

### Backend API Endpoints (Required)
```
POST /api/contracts/upload - Upload contract for analysis
POST /api/contracts/analyze - Trigger analysis pipeline
GET /api/contracts/{id}/analysis - Retrieve analysis results
GET /api/contracts/{id}/summary - Get executive summary
GET /api/contracts/{id}/clauses - Get clause extraction table
GET /api/contracts/{id}/heatmap - Get risk visualization data
GET /api/jurisdictions - List supported jurisdictions
GET /api/verticals - List legal verticals
GET /api/citations/{citation_id} - Retrieve IF.TTT citation details
POST /api/contracts/{id}/export - Export in specified format
```

---

## Critical Features for MVP

### Must-Have Features
1. ✅ Contract upload (PDF, DOCX, TXT)
2. ✅ Clause detection (41 categories)
3. ✅ Five-dimension risk scoring
4. ✅ Jurisdiction detection
5. ✅ Executive summary generation
6. ✅ Risk heatmap visualization (radar chart)
7. ✅ Clause extraction table
8. ✅ IF.TTT citation linking
9. ✅ PDF/markdown export
10. ✅ Basic legal corpus reference

### Should-Have Features (Phase 2)
- Comparative contract analysis
- Negotiation playbook generation
- Industry-specific analysis profiles
- Bilingual support (FR/EN)
- Citation reference list export

### Nice-to-Have Features (Phase 3+)
- Case law integration
- Automated amendment detection
- Machine learning-based clause classification fine-tuning
- Advanced comparative analysis
- Blockchain-based document verification

---

## Data Assets Available

### Legal Corpus
- **290 documents** across 9 jurisdictions
- **241 successfully downloaded** (93.1% success rate)
- **55,778+ Chroma vectors** with full metadata
- **290 IF.TTT citations** with complete provenance chains
- **Raw size:** ~115 MB

### Test Dataset
- **1,329 synthetic contracts** (classified as ABUSIVE/FAIR/AMBIGUOUS)
- **512 CUAD real contracts** (13,000+ expert annotations)
- **41 pre-labeled clause categories**
- **Industry coverage:** Tech, Sales, Creative, Professional Services

### Source Files
- Master Manifest: `/home/setup/if-legal-corpus/manifests/MASTER_MANIFEST_2025-11-28.csv`
- IF.TTT Citations: `/home/setup/if-legal-corpus/citations/legal-corpus-citations-2025-11-28.json`
- ChromaDB Index: `/home/setup/if-legal-corpus/indexes/chromadb/`
- Test Contracts: `/home/setup/if-legal-corpus/test-contracts/`

---

## Design Recommendations

### User Interface Layout
```
┌─────────────────────────────────────────┐
│        IF.CONTRACT ANALYZER             │
├─────────────────────────────────────────┤
│                                         │
│  [Upload Contract] [Select Jurisdiction]│
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  Contract: document.pdf           │ │
│  │  Status: Analyzing...             │ │
│  └───────────────────────────────────┘ │
│                                         │
│  RISK ASSESSMENT (Overall: 72/100)     │
│  ┌──────────────────────────────────┐  │
│  │    IP Risk: 85 (Red)             │  │
│  │    Termination: 60 (Yellow)      │  │
│  │    Liability: 75 (Red)           │  │
│  │    Covenants: 55 (Yellow)        │  │
│  │    Commercial: 70 (Red)          │  │
│  │                                  │  │
│  │    [Radar Chart Visualization]   │  │
│  └──────────────────────────────────┘  │
│                                         │
│  TOP FINDINGS                           │
│  🔴 IP Assignment: Total (all work)    │
│  🟡 Non-Compete: 24 months worldwide   │
│  🔴 Termination: Asymmetric (3mo notice)│
│                                         │
│  [Export Summary] [View Clauses] [...]  │
└─────────────────────────────────────────┘
```

### Color Scheme
- **Green (#10B981):** Low risk (0-25)
- **Yellow (#F59E0B):** Moderate risk (26-50)
- **Red (#EF4444):** High risk (51-100)
- **Gray (#6B7280):** Neutral/informational

### Interactive Elements
- Sortable clause table
- Filterable by clause type, risk level, jurisdiction
- Expandable dimension details
- Clickable citations (show legal source)
- Copy-to-clipboard for clauses
- Download/export buttons

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Contract upload | <5 seconds |
| Analysis completion | <2 seconds |
| Heatmap rendering | <1 second |
| Clause table load | <2 seconds |
| Citation lookup | <200ms |
| PDF export | <10 seconds |
| Overall page load | <3 seconds |

---

## Security & Privacy

- ✅ **No cloud storage:** Contracts analyzed locally
- ✅ **End-to-end encryption:** Optional for sensitive documents
- ✅ **GDPR compliance:** No personal data stored
- ✅ **Audit trail:** IF.TTT citations track all references
- ✅ **Legal disclaimer:** "Educational information only, not legal advice"

---

## Deployment

### Current Status
- ✅ Legal corpus production-ready
- ✅ ChromaDB vectors ingested
- ✅ IF.TTT citations complete
- ✅ Test dataset ready
- ✅ Backend specifications complete
- ⏳ Frontend development ready to begin

### Environment
- **OS:** Linux (WSL2)
- **Python:** 3.12+
- **Node.js:** v20.19.5+
- **Database:** ChromaDB (persistent local)
- **Storage:** /home/setup/if-legal-corpus/

---

## Files for Frontend Development Team

1. **Full Specification JSON:** `/home/setup/if-legal-corpus/IF_CONTRACT_APPLICATION_SPECIFICATION.json`
2. **Legal Corpus README:** `/home/setup/if-legal-corpus/README.md`
3. **Test Dataset Guide:** `/home/setup/if-legal-corpus/test-contracts/README.md`
4. **Master Manifest:** `/home/setup/if-legal-corpus/manifests/MASTER_MANIFEST_2025-11-28.csv`
5. **IF.TTT Citations:** `/home/setup/if-legal-corpus/citations/legal-corpus-citations-2025-11-28.json`
6. **Chroma Database:** `/home/setup/if-legal-corpus/indexes/chromadb/`

---

## Next Steps

1. **Backend Setup:** Configure API endpoints for contract analysis pipeline
2. **Frontend Framework Selection:** Choose React/Vue/Svelte
3. **Design Phase:** Create wireframes and design system
4. **Component Development:** Build UI components (upload, tables, charts, export)
5. **Integration:** Connect frontend to backend API
6. **Testing:** Validate with 1,841 test contracts
7. **Deployment:** Deploy to staging/production

---

**Status:** Ready for Frontend Development
**Date:** November 28, 2025
**Specification Version:** 1.0
**Legal Corpus:** 290 documents, 9 jurisdictions, 55,778+ vectors
**Test Dataset:** 1,841 contracts (1,329 synthetic + 512 real)
