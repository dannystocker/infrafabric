# ContractGuard Test Contracts Corpus

## Executive Summary

This corpus contains **510+ real commercial legal contracts** immediately available for testing and development of the ContractGuard legal analysis system, with access to **100,000+ additional contracts** through linked datasets and APIs.

### Quick Stats
- **Immediately Available**: 510 contracts (CUAD v1)
- **Total Downloadable**: 500K+ (SEC EDGAR, Pile of Law, etc.)
- **License Types**: CC BY 4.0, Public Domain, Free for Use
- **Industries**: 15+ sectors (Software, Pharma, Finance, Real Estate, Manufacturing, etc.)
- **Contract Types**: 40+ categories
- **Clause Categories**: 41 annotated types
- **Jurisdictions**: Primarily US, with multinational examples

---

## What's Included

### 1. CUAD v1 Dataset (510 Contracts - Ready to Use)

**Location**: `/home/setup/if-legal-corpus/test-contracts/CUAD_v1/`

**What You Get**:
- **510 complete commercial contracts** from SEC EDGAR filings
- **13,000+ expert annotations** identifying critical clauses
- **41 clause categories** pre-labeled by lawyers
- **Multiple formats**: JSON metadata, PDF originals, TXT extracts
- **Master clauses CSV** for statistical analysis
- **Complete documentation** and research paper

**Key Features**:
- Real contracts from actual corporate transactions (not templates)
- Diverse industries: Pharma, Software, Finance, Energy, Manufacturing, etc.
- Ranging from simple 2-page agreements to complex 50+ page contracts
- Well-organized directory structure for easy access
- Suitable for both testing and training

**Files**:
```
CUAD_v1/
├── CUAD_v1.json              # 40 MB - Full dataset with annotations
├── full_contract_pdf/        # 510 PDFs (original documents)
│   ├── Part_I/               # 170 contracts
│   ├── Part_II/              # 169 contracts
│   └── Part_III/             # 171 contracts
├── full_contract_txt/        # 510 TXT versions (machine-readable)
├── master_clauses.csv        # Clause frequency and patterns
├── label_group_xlsx/         # Analysis spreadsheets
└── CUAD_v1_README.txt        # Full documentation
```

**License**: CC BY 4.0 (Commercial & non-commercial use permitted, attribution required)

**Source**: 
- Dataset: https://zenodo.org/records/4595826
- Paper: https://arxiv.org/abs/2103.06268 (NeurIPS 2021)
- Code: https://github.com/TheAtticusProject/cuad

---

### 2. Sample Contract Templates (Already Downloaded)

**Location**: `/home/setup/if-legal-corpus/test-contracts/independent-contractor/`

| File | Source | Type | License | Size |
|------|--------|------|---------|------|
| `nda-sample-01-nyu.pdf` | NYU Stern | NDA Template | Educational | 89 KB |
| `design-agreement-aiga-2023.pdf` | AIGA | Design Services Agreement | Free (Non-member) | 4.5 KB |

---

## Complete Contract Sources Reference

### A. Major Datasets (Immediately Downloadable)

#### CUAD v1 (510 contracts - Downloaded)
- **URL**: https://zenodo.org/records/4595826
- **Size**: 105.9 MB
- **Status**: Downloaded and ready

#### Pile of Law (256+ GB)
- **URL**: https://huggingface.co/datasets/pile-of-law/pile-of-law
- **Contents**: Court opinions, contracts, rules, legislation
- **Access**: HuggingFace CLI or web interface

#### Multi-Legal Pile (689 GB, 24 languages)
- **URL**: https://huggingface.co/datasets/joelniklaus/Multi_Legal_Pile
- **Access**: HuggingFace
- **Use**: Multilingual contract analysis training

#### ACORD (126K query-clause pairs)
- **URL**: https://huggingface.co/datasets/theatticusproject/acord
- **Use**: Contract retrieval and clause matching

#### LegalBench (162 legal reasoning tasks)
- **URL**: https://huggingface.co/datasets/nguha/legalbench
- **Use**: Multi-task legal AI evaluation

### B. SEC EDGAR (100,000+ Public Company Contracts)

**Direct Access**:
- Web Search: https://www.sec.gov/edgar/search/
- FTP Bulk: ftp://ftp.sec.gov/
- API Rate: 10 requests/second (free)

**Third-Party APIs**:
- sec-api.io (higher rate limits)
- Standard API for programmatic access

**Contract Types**:
- Material contracts (Exhibit 10)
- Employment agreements
- M&A documents
- Licensing deals
- Distribution agreements

**Why Valuable**:
- Recently negotiated real contracts
- Public companies with legal departments
- Diverse sectors and contract types
- Freely available, no registration

### C. Free Template Providers (20+ sources)

#### Professional Services
- FindLaw Corporate: https://corporate.findlaw.com/contracts.html
- PandaDoc: https://www.pandadoc.com/ (200+ templates)
- Rocket Lawyer: https://www.rocketlawyer.com/ (300+ templates)

#### Independent Contractor / Freelancer
- **Software Development**: 
  - Witted Partners: https://wittedpartners.com/
  - Index.dev: https://www.index.dev/
  - PandaDoc: https://www.pandadoc.com/software-development-agreement-template/
  
- **Design Contracts**: 
  - AIGA Standard Form: https://www.aiga.org/resources/aiga-standard-form-of-agreement-for-design-services
  
- **General Freelance**: 
  - Bonsai: https://www.hellobonsai.com/
  - Proposable: https://proposable.com/

#### Employment
- LegalZoom: https://www.legalzoom.com/templates/t/employment-agreement
- LawDepot: https://www.lawdepot.com/us/business/employment-contract/
- PandaDoc: https://www.pandadoc.com/employment-contract-templates/

#### IP & Confidentiality
- NDA Templates: https://nondisclosureagreement.com/
- Rocket Lawyer NDA: https://www.rocketlawyer.com/business-and-contracts/intellectual-property/confidentiality-agreements/
- SaaS Agreements: https://www.pandadoc.com/saas-agreement-template/

#### Real Estate
- Commercial Leases: https://www.lawdepot.com/us/real-estate/commercial-lease-agreement/
- iPropertyManagement: https://ipropertymanagement.com/templates/commercial-lease-agreement

#### Construction
- eSign.com: https://esign.com/employment/independent-contractor/construction/
- TemplateLab: https://templatelab.com/construction-contract/ (41 templates)

### D. Government & Industry Standards

**Federal Procurement**:
- GSA eLibrary: https://www.gsaelibrary.gsa.gov/
- BUY.GSA.GOV: https://buy.gsa.gov/find-samples-templates-tips

**Industry Standards**:
- AIGA (Design): https://www.aiga.org/resources/business-freelance-resources/legal-guides-contracts
- Writers Guild: https://www.wgaeast.org/ / https://www.wgawest.org/
- Construction (JCT/FIDIC): Various (some restricted)

**Open Source**:
- MIT License: Standard in most GitHub repos
- Apache 2.0: Standard in most GitHub repos
- Contributor Agreements: https://github.com/mgifford/open-source-contracting

---

## Directory Organization

```
/home/setup/if-legal-corpus/test-contracts/
├── CUAD_v1/                              # Main dataset (510 contracts)
│   ├── CUAD_v1.json
│   ├── full_contract_pdf/
│   │   ├── Part_I/      (170 contracts)
│   │   ├── Part_II/     (169 contracts)
│   │   └── Part_III/    (171 contracts)
│   ├── full_contract_txt/
│   ├── master_clauses.csv
│   └── label_group_xlsx/
│
├── independent-contractor/               # Sample contracts
│   ├── nda-sample-01-nyu.pdf
│   └── design-agreement-aiga-2023.pdf
│
├── employment/                           # [Ready for samples]
├── ip-licenses/                          # [Ready for samples]
├── commercial/                           # [Ready for samples]
├── real-estate/                          # [Ready for samples]
├── construction/                         # [Ready for samples]
├── insurance/                            # [Ready for samples]
│
├── CONTRACT-SOURCES.md                   # Complete sources documentation
├── CUAD-CATALOG.md                       # CUAD dataset details
└── README.md                             # This file
```

---

## CUAD v1: The 41 Clause Categories

The CUAD dataset pre-labels contracts with these 41 critical clause types:

**Foundational Clauses**:
- Definitions, Entire Agreement, Effective Dates, Counterparts

**Termination & Lifecycle**:
- Expiration/Termination, Termination for Cause, Termination for Convenience, Survival, Automatic Renewal

**Liability & Risk**:
- Cap on Liability, Limitation of Liability, Indemnification, Insurance, Force Majeure, Cross Liability

**IP & Confidentiality**:
- Intellectual Property, Licenses, Confidentiality/NDA, Source Code, Residuals

**Business Terms**:
- Fees and Charges, Price Restrictions, Most Favored Nation, Exclusivity, Subcontracting

**Obligations & Control**:
- Representations and Warranties, Warranties Disclaimer, Compliance, Audit Rights, Consent and Approval

**Legal Framework**:
- Governing Law, Binding Arbitration, Dispute Resolution, Severability, Notice

**Data & Specific**:
- Data Processing, Financial Reporting, Permitted Uses, Assignment, Amendments

**Special Provisions**:
- Non-Compete, Non-Solicitation

---

## Testing Recommendations

### Phase 1: Foundation Testing (Use CUAD 510)
1. **Clause Extraction**: Extract and classify each of the 41 CUAD categories
2. **Clause Quality**: Identify problematic clauses (overly broad IP, unfair liability limits, etc.)
3. **Cross-Reference**: Find related clauses across contracts
4. **Comparison**: Benchmark good vs. problematic clause patterns

### Phase 2: Expansion Testing (Add Templates)
1. **Template Validation**: Test against standard template forms
2. **Industry Variations**: Compare software vs. construction vs. real estate clauses
3. **Jurisdiction Differences**: Test US vs. UK vs. EU contract variations

### Phase 3: Advanced Testing (Leverage Big Data)
1. **SEC EDGAR Integration**: Download recent filings for trend analysis
2. **Multilingual**: Use Pile of Law for non-English contract testing
3. **Clause Pattern Mining**: Identify emerging problematic patterns
4. **Compliance Checking**: Test against industry standards

### Phase 4: Edge Cases (Build Custom Test Set)
Create targeted test contracts containing:
- Aggressively one-sided IP assignments
- Dangerously broad liability caps
- Unreasonable non-competes
- Weak confidentiality provisions
- Unfavorable payment terms
- Unusual jurisdiction/arbitration clauses

---

## Downloading Additional Contracts

### From SEC EDGAR (100,000+ Contracts)
```bash
# Example: Fetch recent material contracts
python3 << 'EOF'
import requests
import json

# Query SEC EDGAR API
query = {
    "query": "form_type:10-K AND exhibit:10",
    "from": 0,
    "size": 100
}

# Make request (10 req/sec limit)
response = requests.get("https://www.sec.gov/cgi-bin/browse-edgar", params=query)
# Process results...
