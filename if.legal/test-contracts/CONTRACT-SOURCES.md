# ContractGuard Test Corpus: Contract Sources and Resources

## Overview
This document catalogs all publicly available contract samples and sources for ContractGuard testing and development.

## Major Datasets and Repositories

### 1. CUAD (Contract Understanding Atticus Dataset)
- **Source**: Zenodo / The Atticus Project
- **URL**: https://zenodo.org/records/4595826
- **License**: Creative Commons Attribution 4.0 (CC BY 4.0)
- **Size**: 510 commercial legal contracts with 13,000+ expert annotations
- **Format**: JSON, PDF, TXT
- **Contents**: 
  - 510 complete contract PDFs organized by parts (I, II, III)
  - 41 labeled clause categories (Governing Law, Limitation of Liability, Confidentiality, etc.)
  - Master clauses CSV for analysis
  - README documentation
- **Location**: `/home/setup/if-legal-corpus/test-contracts/CUAD_v1/`
- **Download Method**: Direct from Zenodo or via GitHub
- **Status**: Downloaded and extracted (105.9 MB)

### 2. HuggingFace Legal Datasets
| Dataset | URL | Contracts | License |
|---------|-----|-----------|---------|
| CUAD QA | https://huggingface.co/datasets/theatticusproject/cuad-qa | 510 | CC BY 4.0 |
| Pile of Law | https://huggingface.co/datasets/pile-of-law/pile-of-law | 256GB+ | Multiple |
| Multi Legal Pile | https://huggingface.co/datasets/joelniklaus/Multi_Legal_Pile | 689GB (24 languages) | Multiple |
| ACORD (Contract Retrieval) | https://huggingface.co/datasets/theatticusproject/acord | 126K query-clause pairs | CC BY 4.0 |
| LegalBench | https://huggingface.co/datasets/nguha/legalbench | 162 tasks | Open |
| Legal Contracts | https://huggingface.co/datasets/nhankins/legal_contracts | Multiple | Multiple |

### 3. SEC EDGAR Contract Database
- **Source**: U.S. Securities and Exchange Commission
- **URL**: https://www.sec.gov/search-filings/
- **Contents**: Public company contracts filed as exhibits
- **Accessing**:
  - Direct web search: https://www.sec.gov/edgar/search/
  - FTP bulk access: ftp://ftp.sec.gov/
  - API access: 10 requests/second limit
  - Third-party APIs: sec-api.io (higher rate limits)
- **Types**: Material contracts (Exhibit 10), employment, M&A, licensing, distribution
- **Availability**: Free, no registration required
- **Note**: Contracts filed by public companies as SEC exhibits - guaranteed to be real, recently negotiated contracts

### 4. GitHub Open Source Resources
- **Repository**: https://github.com/TheAtticusProject/cuad (CUAD code and models)
- **Repository**: https://github.com/mgifford/open-source-contracting (open source contract language examples)
- **Standard Licenses**: MIT, Apache 2.0, GPL, BSD available in any GitHub repository
- **Contributor Agreements**: CLAHub (https://github.com/clahub/clahub) for CLA templates
- **Google Open Source**: https://opensource.google/documentation/reference/cla

---

## Free Contract Template Sources (Real Templates with Real Clauses)

### Professional Services & Consulting

| Source | Contract Types | URL | License | Notes |
|--------|----------------|-----|---------|-------|
| FindLaw Corporate | Service agreements, consulting, purchase agreements | https://corporate.findlaw.com/contracts.html | Free | Real contracts from public companies |
| PandaDoc | 200+ business templates | https://www.pandadoc.com/standard-business-document-templates/ | Free/Premium | Customizable, downloadable as PDF |
| Rocket Lawyer | 300+ legal documents | https://www.rocketlawyer.com/legal-documents | Free/Premium | Can create and download for free |
| RealDealDocs | Real contracts from top law firms | https://realdealdocs.com/ | Subscription | Real negotiated documents |
| Signaturely | Contract templates | https://signaturely.com/contracts/ | Free | Word/PDF download |

### Independent Contractor / Freelancer

| Contract Type | Source | URL | Format | License |
|---------------|--------|-----|--------|---------|
| Software Development | Witted Partners | https://wittedpartners.com/contract-template-for-software-freelancers | PDF | Free |
| Software Development | Index.dev | https://www.index.dev/blog/freelance-software-developer-contract-template | Web/PDF | Free |
| Software Development | PandaDoc | https://www.pandadoc.com/software-development-agreement-template/ | PDF | Free |
| Freelancer General | Proposable | https://proposable.com/contract-templates/software-development-contract | Web | Free |
| Freelancer General | Bonsai | https://www.hellobonsai.com/a/software-development-contract-template-pdf | PDF | Free |
| Graphic Design | AIGA | https://www.aiga.org/resources/aiga-standard-form-of-agreement-for-design-services | PDF | Free (Non-member) |
| Content Writing | Multiple sources (Bonsai, Rocket Lawyer) | Various | PDF | Free |
| Photography | Template.net | https://template.net/business/agreements/ | Word/PDF | Free |

**Local Samples:**
- `/home/setup/if-legal-corpus/test-contracts/independent-contractor/nda-sample-01-nyu.pdf` (89 KB, NYU Stern example)
- `/home/setup/if-legal-corpus/test-contracts/independent-contractor/design-agreement-aiga-2023.pdf` (4.5 KB, AIGA standard)

### Employment Contracts

| Source | URL | Format | License |
|--------|-----|--------|---------|
| LegalZoom | https://www.legalzoom.com/templates/t/employment-agreement | PDF | Free/Premium |
| LawDepot | https://www.lawdepot.com/us/business/employment-contract/ | PDF/Word | Free |
| Legal Templates | https://legaltemplates.net/form/employment-contract/ | PDF/Word | Free |
| eSign.com | https://esign.com/employment/ | PDF/Word | Free |
| PandaDoc | https://www.pandadoc.com/employment-contract-templates/ | PDF | Free |
| BetterTeam | https://www.betterteam.com/employee-contract-template | PDF | Free |

### Intellectual Property & Confidentiality

| Type | Source | URL | License |
|------|--------|-----|---------|
| NDA Templates | NonDisclosureAgreement.com | https://nondisclosureagreement.com/ | Free |
| NDA | Nolo.com | https://www.nolo.com/legal-encyclopedia/sample-confidentiality-agreement-nda-33343.html | Free |
| NDA | Rocket Lawyer | https://www.rocketlawyer.com/business-and-contracts/intellectual-property/confidentiality-agreements/document/non-disclosure-agreement | Free |
| NDA | PandaDoc | https://www.pandadoc.com/nda-template/ | Free |
| NDA Sample | NYU Stern | https://oz.stern.nyu.edu/startups/nda2.pdf | Educational |
| Copyright Assignment | Multiple sources | Various | Various |
| Patent Licensing | Multiple sources | Various | Various |
| SaaS License | PandaDoc | https://www.pandadoc.com/saas-agreement-template/ | Free |
| SaaS Agreement | Superlegal.ai | https://www.superlegal.ai/wp-content/uploads/2024/12/SaaS-Services-Agreement-Template-3.pdf | Free |
| SaaS Agreement | Cooley/ACC | https://www.acc.com/sites/default/files/program-materials/upload/Cooley SaaS Agreement ACC Form.pdf | Free |

### Commercial Agreements

| Type | Source | URL | License |
|------|--------|-----|---------|
| Service Agreements | FindLaw | https://corporate.findlaw.com/contracts/operations/services.html | Free |
| Service Agreements | Rocket Lawyer | https://www.rocketlawyer.com/business-and-contracts/business-operations/product-or-service-sales/document/service-agreement | Free |
| Sales/Purchase | FindLaw | https://www.findlaw.com/smallbusiness/business-contracts-forms/sample-sales-contract.html | Free |
| Distribution | Multiple sources | Various | Various |
| Partnership | Multiple sources | Various | Various |
| Joint Venture | Multiple sources | Various | Various |

### Real Estate & Leases

| Type | Source | URL | License |
|------|--------|-----|---------|
| Commercial Lease | LawDepot | https://www.lawdepot.com/us/real-estate/commercial-lease-agreement/ | Free |
| Commercial Lease | iPropertyManagement | https://ipropertymanagement.com/templates/commercial-lease-agreement | Free |
| Commercial Lease | eForms | https://eforms.com/rental/commercial/ | Free |
| Commercial Lease | Jotform | https://www.jotform.com/pdf-templates/free-commercial-lease-agreement-template | Free |
| Residential Lease | LawDepot | https://www.lawdepot.com/us/real-estate/ | Free |
| Property Sale | LawDepot | https://www.lawdepot.com/us/real-estate/contract-for-deed/ | Free |

### Construction & Trade

| Type | Source | URL | License |
|------|--------|-----|---------|
| Construction Contract | eSign.com | https://esign.com/employment/independent-contractor/construction/ | Free |
| Construction Contract | eForms | https://eforms.com/employment/independent-contractor/construction/ | Free |
| Construction Contract | Contractbook | https://contractbook.com/templates/construction-contract | Free |
| Construction Contract | TemplateLab | https://templatelab.com/construction-contract/ | Free (41 templates) |
| Construction Contract | Jotform | https://www.jotform.com/pdf-templates/free-construction-contract-template | Free |
| Subcontractor | Multiple sources | Various | Various |

### Government & GSA Contracts

| Source | URL | Type |
|--------|-----|------|
| GSA eLibrary | https://www.gsaelibrary.gsa.gov/ | Federal procurement contracts |
| BUY.GSA.GOV | https://buy.gsa.gov/find-samples-templates-tips | Samples & templates for GSA contracts |
| GSA Contracts | https://buy.gsa.gov/contracts | Contract vehicles database |
| GWAC Ordering Guides | https://www.gsa.gov/technology/it-contract-vehicles-and-purchasing-programs/gwacs | Federal IT contracts |

### Industry-Specific Resources

| Industry | Organization | URL | Resources |
|----------|--------------|-----|-----------|
| Design/Art | AIGA | https://www.aiga.org/resources/business-freelance-resources/legal-guides-contracts | Standard form agreements |
| Writers | Writers Guild | https://www.wgaeast.org/ / https://www.wgawest.org/ | Union agreements |
| Musicians | ASCAP, BMI, SESAC | Various | Licensing agreements |
| Construction | ConsensusDocs, AIA | Various | Industry standard contracts |

---

## Contract Clause Collections & Research

### Master Clause Analysis
- **CUAD Master Clauses CSV**: `/home/setup/if-legal-corpus/test-contracts/CUAD_v1/master_clauses.csv`
- **41 Clause Categories** documented in CUAD metadata:
  - Governing Law, Limitation of Liability, Non-Compete, Confidentiality
  - Termination, IP Rights, Indemnification, Warranties, and more

### Legal ML Research
- **GitHub**: https://github.com/neelguha/legal-ml-datasets
- **Contents**: Links to major legal datasets and research papers

---

## Data Collection Strategy for ContractGuard

### Phase 1: Already Collected (510+ contracts)
- CUAD v1 dataset: 510 real commercial contracts
- Multiple industry sectors represented
- Diverse clause types and jurisdictions
- Ready for immediate testing

### Phase 2: Recommended Additional Collection
1. **SEC EDGAR Real-Time Downloads**: Write script to fetch recent Exhibit 10 filings (100+ contracts/month)
2. **HuggingFace Datasets**: Download Pile of Law and Multi-Legal datasets for large-scale training
3. **Template Provider Scraping**: Systematically download samples from PandaDoc, Rocket Lawyer, LawDepot
4. **Industry Datasets**: Collect construction (JCT/FIDIC), design (AIGA), and other specialized contracts

### Phase 3: Clause-Specific Testing Corpus
Build targeted test sets for known problematic clause patterns:
- Overly broad IP assignments
- One-sided liability limitations
- Aggressive non-competes
- Weak confidentiality provisions
- Unfavorable payment terms

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Immediately Available Contracts** | 510 (CUAD) |
| **Free Template Sources** | 20+ major platforms |
| **License Types Available** | CC BY 4.0, Public Domain, Free for use |
| **Industries Represented** | Software, Pharma, Energy, Finance, Tech, Manufacturing, Real Estate |
| **Contract Types Available** | 8+ major categories, 50+ subcategories |
| **Clause Categories Annotated** | 41 (CUAD) |
| **Potential Additional Contracts** | 100,000+ (SEC EDGAR, Pile of Law) |

---

## Usage Guidelines

### For Testing
1. Start with CUAD 510-contract core set
2. Add template samples from at least 5 different platforms
3. Include "problematic" contracts for negative testing
4. Ensure jurisdiction diversity (US, UK, EU, etc.)

### For Training
1. Use CUAD labels for supervised learning
2. Augment with Pile of Law for general NLP
3. Use Multi-Legal Pile for multilingual support
4. Create custom test sets with known issues

### Copyright & Licensing
- **CUAD**: CC BY 4.0 (free for commercial/non-commercial use, credit required)
- **SEC EDGAR**: Public domain (filed with US government)
- **Templates**: Each source has specific license - verify before commercial use
- **RealDealDocs, Findlaw**: Commercial use permitted with appropriate license

---

## Resources for Contract Analysis

### Legal Terminology & Standards
- [OpenLaw](https://openlaw.io/) - Smart contracts and legal templates
- [LawInsider](https://www.lawinsider.com/) - Contract AI and analysis tools
- [Contract Standards](https://www.contractstandards.com/) - Practical guidance
- [Adams on Contract Drafting](https://www.adamsdrafting.com/) - Contract drafting expertise

### NLP & ML Research
- ArXiv: https://arxiv.org/abs/2103.06268 (CUAD paper)
- Papers with Code: Contract understanding benchmarks
- Conference proceedings: ACL, EMNLP, ICLR legal NLP track

---

**Last Updated**: 2025-11-28
**Curator**: ContractGuard Project
**Status**: Ready for use and expansion

