# ContractGuard Legal Corpus Import List
## Complete Document Inventory for Chroma Vector Database

**Generated:** 2025-11-27
**Purpose:** Define all legal documents to download and index for contract analysis AI
**Target:** Self-hosted Chroma vector database

---

## Table of Contents

1. [Summary Statistics](#summary-statistics)
2. [Priority Legend](#priority-legend)
3. [US Federal Law](#1-us-federal-law)
4. [US State Law](#2-us-state-law)
5. [US Property, Tax & Accounting](#2b-us-property-tax-accounting-law)
6. [European Union](#3-european-union)
7. [EU Tax & Accounting Directives](#3b-eu-tax-accounting-directives)
8. [Germany](#4-germany)
9. [German Tax & Accounting](#4b-german-tax-accounting-law)
10. [France](#5-france)
11. [French Property, Tax & Accounting](#5b-french-property-tax-accounting-law)
12. [Canada](#6-canada)
13. [Canadian Property & Tax](#6b-canadian-property-tax-law)
14. [Australia](#7-australia)
15. [Australian Property, Tax & Accounting](#7b-australian-property-tax-accounting-law)
16. [United Kingdom](#8-united-kingdom)
17. [UK Property, Tax & Accounting](#8b-uk-property-tax-accounting-law)
18. [Spain Legal Documents](#9-spain-legal-documents-new)
19. [Contract Datasets](#10-contract-datasets-pre-labeled)
20. [Case Law](#11-landmark-case-law)
21. [Industry Standards](#12-industry-standards)
22. [Download Scripts Reference](#13-download-scripts-reference)

---

## Summary Statistics

| Category | Document Count | Est. Size | Priority P0 |
|----------|---------------|-----------|-------------|
| US Federal | 15 | ~50MB | 8 |
| US State | 24 | ~30MB | 6 |
| US Property/Tax Law | 12 | ~25MB | 6 |
| EU Directives/Regs | 10 | ~20MB | 6 |
| EU Tax/Accounting Directives | 7 | ~20MB | 4 |
| Germany (BGB) | 6 | ~15MB | 4 |
| Germany (Tax/Accounting) | 8 | ~20MB | 4 |
| France | 4 | ~10MB | 2 |
| France (Property/Tax/Accounting) | 6 | ~15MB | 2 |
| Canada | 10 | ~15MB | 5 |
| Canada (Property/Tax) | 10 | ~25MB | 4 |
| Australia | 6 | ~10MB | 3 |
| Australia (Property/Tax/Accounting) | 12 | ~35MB | 5 |
| UK | 8 | ~12MB | 5 |
| UK (Property/Tax/Accounting) | 27 | ~50MB | 11 |
| Spain | 28 | ~25MB | 10 |
| Spain (Housing Law) | 3 | ~3MB | 2 |
| Quebec (Comprehensive) | 65 | ~40MB | 25 |
| Housing Law (Multi-Jurisdiction) | 73 | ~65MB | 24 |
| Insurance Law (Multi-Jurisdiction) | 43 | ~35MB | 17 |
| Construction Law (Multi-Jurisdiction) | 58 | ~45MB | 20 |
| Criminal Law (Multi-Jurisdiction) | 52 | ~40MB | 15 |
| Datasets (CUAD etc) | 3 | ~500MB | 3 |
| Case Law | 25 | ~100MB | 10 |
| Industry Standards | 12 | ~20MB | 6 |
| **TOTAL** | **~520+ sources** | **~1,900MB** | **199** |

---

## Priority Legend

| Priority | Meaning | Action |
|----------|---------|--------|
| **P0** | Critical - Must have for MVP | Import immediately |
| **P1** | Important - Should have | Import in Phase 2 |
| **P2** | Supplementary - Nice to have | Import in Phase 3 |

---

## 1. US FEDERAL LAW

### 1.1 US Code Titles

| Document | Title | Source | Format | URL | Priority |
|----------|-------|--------|--------|-----|----------|
| **17 USC** | Copyright | House.gov | XML | https://uscode.house.gov/download/download.shtml | **P0** |
| **35 USC** | Patents | House.gov | XML | https://uscode.house.gov/download/download.shtml | **P0** |
| **18 USC Ch.63** | Mail/Wire Fraud | House.gov | XML | https://uscode.house.gov/download/download.shtml | P1 |
| **15 USC §1681** | Fair Credit Reporting | FTC | PDF | https://www.ftc.gov/legal-library/browse/statutes/fair-credit-reporting-act | P1 |
| **15 USC §6801** | Gramm-Leach-Bliley | FTC | PDF | https://www.ftc.gov/business-guidance/privacy-security/gramm-leach-bliley-act | P1 |

### 1.2 Code of Federal Regulations

| Document | Title | Source | Format | URL | Priority |
|----------|-------|--------|--------|-----|----------|
| **29 CFR** | Labor | eCFR | XML | https://www.ecfr.gov/current/title-29 | **P0** |
| **37 CFR** | Patents/Trademarks/Copyright | eCFR | XML | https://www.ecfr.gov/current/title-37 | **P0** |
| **16 CFR Part 310** | Telemarketing Sales | FTC | XML | https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-310 | P1 |
| **16 CFR Part 314** | Safeguards Rule | FTC | XML | https://www.ecfr.gov/current/title-16/part-314 | P1 |

### 1.3 Named Federal Statutes

| Document | Citation | Source | Format | URL | Priority |
|----------|----------|--------|--------|-----|----------|
| **Defend Trade Secrets Act** | 18 USC §1836 | Congress.gov | PDF | https://www.congress.gov/114/plaws/publ153/PLAW-114publ153.pdf | **P0** |
| **Work-for-Hire Definition** | 17 USC §101 | Copyright Office | HTML | https://www.copyright.gov/title17/ | **P0** |
| **Copyright Ownership** | 17 USC §201 | Copyright Office | HTML | https://www.copyright.gov/title17/ | **P0** |
| **FTC Non-Compete Rule** | 2024 Rule | Federal Register | PDF | https://www.federalregister.gov/documents/2024/05/07/2024-09171/non-compete-clause-rule | P1 |
| **ADA Title I** | 42 USC §12101 | EEOC | PDF | https://www.eeoc.gov/statutes/titles-i-and-v-americans-disabilities-act-1990-ada | P2 |

### 1.4 Bulk Download Sources

| Source | Coverage | API | URL |
|--------|----------|-----|-----|
| **GovInfo Bulk Data** | All USC, CFR | REST | https://www.govinfo.gov/bulkdata/ |
| **eCFR API v1** | Current CFR | REST/JSON | https://www.ecfr.gov/developers/documentation/api/v1 |
| **House.gov Download** | US Code by Title | XML/PDF | https://uscode.house.gov/download/download.shtml |
| **Congress.gov** | Bills, Laws | REST | https://www.congress.gov/help/using-data-offsite |

---

## 2. US STATE LAW

### 2.1 California (P0 - Most Restrictive)

| Document | Citation | Key Sections | URL | Priority |
|----------|----------|--------------|-----|----------|
| **Non-Compete Ban** | BPC §16600 | §16600, §16600.1, §16600.5 | https://law.justia.com/codes/california/code-bpc/ | **P0** |
| **Freelance Worker Protection Act** | BPC §18100+ | SB 988 (eff. 1/1/25) | https://leginfo.legislature.ca.gov/ | **P0** |
| **ABC Test (IC Classification)** | Labor Code §2775 | AB 5 provisions | https://leginfo.legislature.ca.gov/ | **P0** |
| **SILENCED Act** | CCP §1001 | SB 331 | https://leginfo.legislature.ca.gov/ | P1 |
| **CCPA/CPRA** | Civ. Code §1798.100 | Data processing | https://oag.ca.gov/privacy/ccpa | P1 |

### 2.2 New York (P0 - Freelancer Protections)

| Document | Citation | Key Sections | URL | Priority |
|----------|----------|--------------|-----|----------|
| **Freelance Isn't Free Act (State)** | GBL Art. 44-A | Labor Law §191-d | https://dol.ny.gov/freelance-isnt-free-act | **P0** |
| **Freelance Isn't Free Act (NYC)** | NYC Admin Code Title 20 | Local Law 140 | https://www.nyc.gov/site/dca/about/freelance-isnt-free-act.page | **P0** |
| **Non-Compete Standards** | Gen. Oblig. Law §510-512 | Common law tests | https://www.nysenate.gov/legislation/laws/GOB | P1 |

### 2.3 Texas (P1 - Employer-Friendly)

| Document | Citation | Key Sections | URL | Priority |
|----------|----------|--------------|-----|----------|
| **Non-Compete Enforceability** | BCC §15.50 | §15.50-15.52 | https://codes.findlaw.com/tx/business-and-commerce-code/ | P1 |
| **Healthcare Non-Compete** | BCC §15.501 | SB 1318 (eff. 9/1/25) | https://capitol.texas.gov/ | P1 |

### 2.4 Delaware (P1 - Governing Law Choice)

| Document | Citation | Key Sections | URL | Priority |
|----------|----------|--------------|-----|----------|
| **Choice of Law** | Del. Code Title 6 §2708 | Contract choice-of-law | https://delcode.delaware.gov/title6/ | P1 |
| **Contract Law** | Del. Code Title 6 Ch.27 | General contracts | https://delcode.delaware.gov/title6/c027/ | P1 |

### 2.5 Other Key States

| State | Document | Citation | Key Issue | Priority |
|-------|----------|----------|-----------|----------|
| **Colorado** | Restrictive Covenant Law | CRS §8-2-113 | $101K+ threshold | P1 |
| **Illinois** | Freedom to Work Act | 820 ILCS 90 | $75K threshold | P1 |
| **Washington** | Non-Compete Law | RCW 49.62 | $250K IC threshold | **P0** |
| **Florida** | Non-Compete + CHOICE Act | Fla. Stat. §542.335 | 4-year expansion | P2 |
| **Massachusetts** | ABC Test | MGL c.149 §148B | Strict IC classification | P1 |
| **Minnesota** | Non-Compete Ban | Near-total ban | Similar to CA | P2 |
| **Oklahoma** | Non-Compete Ban | Near-total ban | Similar to CA | P2 |
| **North Dakota** | Non-Compete Ban | Near-total ban | Similar to CA | P2 |

---

## 3. EUROPEAN UNION

### 3.1 EU Directives

| Document | CELEX ID | Subject | EUR-Lex URL | Priority |
|----------|----------|---------|-------------|----------|
| **Transparent Working Conditions** | 32019L1152 | Worker rights baseline | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019L1152 | **P0** |
| **Platform Workers Directive** | 32024L2831 | Gig economy status | https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32024L2831 | **P0** |
| **Copyright Directive** | 32019L0790 | IP ownership | https://eur-lex.europa.eu/eli/dir/2019/790/oj | **P0** |
| **Trade Secrets Directive** | 32016L0943 | Confidentiality | https://eur-lex.europa.eu/eli/dir/2016/943/oj | **P0** |
| **GDPR** | 32016R0679 | Data processing | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02016R0679-20160504 | **P0** |
| **Rental/Lending Rights** | 32006L0115 | IP licensing | https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=celex:32006L0115 | P1 |
| **OSH Framework** | 31989L0391 | Health & safety | https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=celex:31989L0391 | P2 |

### 3.2 EU Regulations

| Document | CELEX ID | Subject | EUR-Lex URL | Priority |
|----------|----------|---------|-------------|----------|
| **Digital Services Act** | 32022R2065 | Platform obligations | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2065 | P1 |
| **EU AI Act** | 32024R1689 | AI training rights | https://eur-lex.europa.eu/eli/reg/2024/1689/oj | **P0** |

---

## 4. GERMANY

### 4.1 Bürgerliches Gesetzbuch (BGB - Civil Code)

| Section | Subject | English Available | URL | Priority |
|---------|---------|-------------------|-----|----------|
| **§611 et seq.** | Service Contract (Dienstvertrag) | Yes | https://www.gesetze-im-internet.de/englisch_bgb/ | **P0** |
| **§631 et seq.** | Work Contract (Werkvertrag) | Yes | https://www.gesetze-im-internet.de/englisch_bgb/ | **P0** |
| **§611a** | Employee vs Self-Employed | Yes | https://www.gesetze-im-internet.de/englisch_bgb/ | **P0** |
| **§705 et seq.** | Partnership (GbR) | Yes | https://www.gesetze-im-internet.de/englisch_bgb/ | P1 |
| **§14** | Entrepreneur Definition | Yes | https://www.gesetze-im-internet.de/englisch_bgb/ | **P0** |

### 4.2 Other German Law

| Document | Subject | URL | Priority |
|----------|---------|-----|----------|
| **UWG (Unfair Competition)** | Business practices | https://www.gesetze-im-internet.de/englisch_uwg/ | P1 |
| **SGB IV §7** | Social security classification | German law database | P1 |

---

## 5. FRANCE

### 5.1 Code du Travail (Labor Code)

| Article | Subject | URL | Priority |
|---------|---------|-----|----------|
| **L1221-6, L1221-19** | Recruitment, trial periods | https://www.legifrance.gouv.fr/codes/ | P1 |
| **L1222-1, L1222-9** | Good faith, remote work | https://www.legifrance.gouv.fr/codes/ | P1 |

### 5.2 Code de la Propriété Intellectuelle

| Article | Subject | URL | Priority |
|---------|---------|-----|----------|
| **L.111-1** | Copyright ownership default | https://www.legifrance.gouv.fr/ | **P0** |
| **D132-28, D132-29** | Freelance photographer rates | https://www.legifrance.gouv.fr/ | P2 |
| **Part 2** | Industrial property | WIPO Lex | **P0** |

---

## 6. CANADA

### 6.1 Federal Legislation

| Document | Citation | Source | URL | Priority |
|----------|----------|--------|-----|----------|
| **Copyright Act** | RSC 1985, c C-42 | Justice Canada | https://laws-lois.justice.gc.ca/eng/acts/C-42/ | **P0** |
| **Competition Act** | RSC 1985, c C-34 | Justice Canada | https://laws.justice.gc.ca/eng/acts/C-34/ | P1 |
| **Canada Labour Code** | RSC 1985, c L-2 | CanLII | https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-l-2/ | P1 |
| **PIPEDA** | SC 2000, c 5 | Privacy Commissioner | https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/ | **P0** |
| **Employment Insurance Act** | SC 1996, c 23 | CanLII | https://www.canlii.org/en/ca/laws/stat/sc-1996-c-23/ | P1 |
| **Employment Equity Act** | SC 1995, c 44 | CanLII | https://www.canlii.org/en/ca/laws/stat/sc-1995-c-44/ | P2 |

### 6.2 Provincial Legislation

| Province | Document | Citation | URL | Priority |
|----------|----------|----------|-----|----------|
| **Ontario** | Employment Standards Act | O. Reg. 435/07 | https://www.ontario.ca/laws/statute/00e41 | **P0** |
| **BC** | Employment Standards Act | RSBC 1996, c 113 | BC Legislature | **P0** |
| **Quebec** | Labour Standards Act | CQLR c N-1.1 | https://www.canlii.org/en/qc/laws/stat/cqlr-c-n-1.1/ | **P0** |

---

## 7. AUSTRALIA

### 7.1 Federal Legislation

| Document | Citation | Source | URL | Priority |
|----------|----------|--------|-----|----------|
| **Fair Work Act 2009** | Cth | Fair Work | https://www.fairwork.gov.au/about-us/legislation | **P0** |
| **Independent Contractors Act 2006** | Act No. 162 | Legislation.gov.au | https://www.legislation.gov.au/Series/C2006A00162 | **P0** |
| **Copyright Act 1968** | Cth | AustLII | https://www7.austlii.edu.au/cgi-bin/viewdb/au/legis/cth/consol_act/ | **P0** |
| **Competition and Consumer Act 2010** | Cth | Legislation.gov.au | https://www.legislation.gov.au/C2004A00109/latest | P1 |
| **Privacy Act 1988** | Cth | AustLII | https://www7.austlii.edu.au/cgi-bin/viewdb/au/legis/cth/consol_act/ | P1 |
| **Australian Consumer Law** | Part II CCA | Legislation.gov.au | https://www.legislation.gov.au/C2004A00109/latest | P1 |

---

## 8. UNITED KINGDOM

### 8.1 Acts of Parliament

| Document | Citation | Source | URL | Priority |
|----------|----------|--------|-----|----------|
| **Employment Rights Act 1996** | c. 18 | legislation.gov.uk | https://www.legislation.gov.uk/ukpga/1996/18/contents | **P0** |
| **Copyright, Designs and Patents Act 1988** | c. 48 | legislation.gov.uk | https://www.legislation.gov.uk/ukpga/1988/48 | **P0** |
| **Patents Act 1977** | c. 37 | legislation.gov.uk | https://www.legislation.gov.uk/ukpga/1977/37 | P1 |
| **Trade Secrets Regulations 2018** | SI 2018/597 | legislation.gov.uk | https://www.legislation.gov.uk/uksi/2018/597/made | **P0** |

### 8.2 IR35 (Off-Payroll Working)

| Document | Citation | Source | URL | Priority |
|----------|----------|--------|-----|----------|
| **Social Security (Intermediaries) Regs** | SI 2000/727 | legislation.gov.uk | https://www.legislation.gov.uk/uksi/2000/727 | **P0** |
| **ITEPA 2003 Part 2 Ch.8** | c. 1 | legislation.gov.uk | https://www.legislation.gov.uk/ukpga/2003/1 | **P0** |
| **Database Rights Regs 1997** | SI 1997/3032 | legislation.gov.uk | https://www.legislation.gov.uk/uksi/1997/3032 | P2 |

---

## 2B. US PROPERTY, TAX & ACCOUNTING LAW

### 2B.1 Property Law (Secured Transactions & Real Estate)

| Document | Citation | Type | URL | Priority |
|----------|----------|------|-----|----------|
| **Uniform Commercial Code Article 9** | UCC Art. 9 | Model Statute | https://www.law.cornell.edu/ucc/9 | **P0** |
| **Uniform Fraudulent Transfer Act** | UFTA | Model Statute | https://www.uniformlaws.org/acts/ufta | **P0** |
| **California Civil Code - Property Sections** | CA Civ. Code §13-15000 | State Statute | https://leginfo.legislature.ca.gov/ | **P0** |
| **Real Estate Settlement Procedures Act** | 12 USC §2601 | Federal Statute | https://www.justice.gov/crt/real-estate-settlement-procedures-act | P1 |

### 2B.2 Tax Law

| Document | Citation | Type | URL | Priority |
|----------|----------|------|-----|----------|
| **Internal Revenue Code - Full Title** | 26 USC | Federal Statute | https://www.law.cornell.edu/uscode/text/26 | **P0** |
| **IRC §162 - Business Expense Deduction** | 26 USC §162 | Federal Statute | https://www.law.cornell.edu/uscode/text/26/162 | **P0** |
| **IRC §1031 - Like-Kind Exchanges** | 26 USC §1031 | Federal Statute | https://www.law.cornell.edu/uscode/text/26/1031 | P1 |
| **IRS Publication 535** | IRS Guidance | Tax Guidance | https://www.irs.gov/pub/irs-pdf/p535.pdf | **P0** |

---

## 3B. EU TAX & ACCOUNTING DIRECTIVES

### 3B.1 Tax Directives

| Document | CELEX ID | Subject | EUR-Lex URL | Priority |
|----------|----------|---------|-------------|----------|
| **VAT Directive** | 32006L0112 | 17-27% VAT across EU | https://eur-lex.europa.eu/eli/dir/2006/112/oj | **P0** |
| **Anti-Tax Avoidance Directive (ATAD)** | 32016L1164 | Interest deduction limitations | https://eur-lex.europa.eu/eli/dir/2016/1164/oj | P1 |
| **Transfer Pricing Documentation** | 32016L0881 | Harmonized TP documentation | https://eur-lex.europa.eu/eli/dir/2016/881/oj | P1 |
| **Country-by-Country Reporting** | 32016L0881 | Multinational tax transparency | https://eur-lex.europa.eu/eli/dir/2016/881/oj | P1 |
| **Insolvency Regulation** | 32015R0848 | Cross-border bankruptcy procedures | https://eur-lex.europa.eu/eli/reg/2015/848/oj | P1 |
| **Dividend Tax Directive** | 31990L0435 | Corporate dividend distribution | https://eur-lex.europa.eu/eli/dir/1990/435/oj | P1 |
| **Tax Administration Cooperation** | 32011L0016 | Tax authority information exchange | https://eur-lex.europa.eu/eli/dir/2011/16/oj | P2 |

### 3B.2 Accounting Directives

| Document | CELEX ID | Subject | EUR-Lex URL | Priority |
|----------|----------|---------|-------------|----------|
| **Accounting Directive 2013/34/EU** | 32013L0034 | Harmonized financial reporting | https://eur-lex.europa.eu/eli/dir/2013/34/oj | **P0** |
| **IFRS Adoption Regulation** | 32002R1606 | IFRS adoption by public entities | https://eur-lex.europa.eu/eli/reg/2002/1606/oj | **P0** |
| **Transparency Directive** | 32004L0109 | Periodic financial reporting | https://eur-lex.europa.eu/eli/dir/2004/109/oj | P1 |
| **MiFID II - Financial Instruments** | 32014L0065 | Investment firm accounting | https://eur-lex.europa.eu/eli/dir/2014/65/oj | P1 |
| **Non-Financial Reporting Directive** | 32014L0095 | ESG reporting requirements | https://eur-lex.europa.eu/eli/dir/2014/95/oj | P1 |
| **Corporate Sustainability Reporting** | 32022L2464 | Expanded ESG disclosure (CSRD) | https://eur-lex.europa.eu/eli/dir/2022/2464/oj | P1 |

---

## 4B. GERMAN TAX & ACCOUNTING LAW

### 4B.1 German Tax Statutes

| Document | Citation | Subject | URL | Priority |
|----------|----------|---------|-----|----------|
| **Einkommensteuergesetz (Income Tax Act)** | EStG | Personal/business income tax | https://www.gesetze-im-internet.de/englisch_estg/ | **P0** |
| **Umsatzsteuergesetz (Value Added Tax Act)** | UStG | 19% VAT (7% reduced) | https://www.gesetze-im-internet.de/englisch_ustg/ | **P0** |
| **Körperschaftsteuergesetz (Corporation Tax Act)** | KStG | Corporate income tax | https://www.gesetze-im-internet.de/kstg/ | P1 |
| **Gewerbesteuergesetz (Business Tax Act)** | GewStG | Municipal business tax | https://www.gesetze-im-internet.de/gewstg/ | P1 |
| **Abgabenordnung (German Tax Code)** | AO | Procedural tax law | https://www.gesetze-im-internet.de/englisch_ao/ | P1 |

### 4B.2 German Accounting & Business Law

| Document | Citation | Subject | URL | Priority |
|----------|----------|---------|-----|----------|
| **Handelsgesetzbuch (Commercial Code) - Book 1** | HGB | Accounting standards | https://www.gesetze-im-internet.de/englisch_hgb/ | **P0** |
| **BGB Book 3 (Property/Rights Law)** | §90-359 | Property and real rights | https://www.gesetze-im-internet.de/englisch_bgb/ | P1 |
| **GmbH-Gesetz (Limited Liability Company Act)** | GmbHG | GmbH accounting rules | https://www.gesetze-im-internet.de/gmbhg/ | P1 |
| **Grundbuchordnung (Land Registry Act)** | GBO | Real property registration | https://www.gesetze-im-internet.de/gbo/ | P1 |

---

## 5B. FRENCH PROPERTY, TAX & ACCOUNTING LAW

### 5B.1 French Property Law

| Document | Citation | Subject | URL | Priority |
|----------|----------|---------|-----|----------|
| **Code Civil - Book II (Property)** | Articles 516-635 | Property ownership framework | https://www.legifrance.gouv.fr/codes/code_civil.html | **P0** |
| **Code Civil - Ownership/Possession** | Articles 871-948 | Property rights and possession | https://www.legifrance.gouv.fr/codes/code_civil.html | P1 |
| **Publicité Foncière Laws** | Multiple | Land registration system | https://www.legifrance.gouv.fr/ | P1 |

### 5B.2 French Tax Law

| Document | Citation | Subject | URL | Priority |
|----------|----------|---------|-----|----------|
| **Code Général des Impôts - Title I** | CGI Art. 1-230 | Personal income tax | https://www.legifrance.gouv.fr/codes/code_general_impots.html | **P0** |
| **CGI - VAT (Articles 256-262)** | CGI Art. 256-262 | Value-added tax (20% standard) | https://www.legifrance.gouv.fr/ | **P0** |
| **CGI - Title II, Chapter II** | CGI Art. 200 et seq. | Corporate income tax | https://www.legifrance.gouv.fr/ | P1 |
| **Property Tax (Taxe Foncière)** | Multiple articles | Annual property holding tax | https://www.legifrance.gouv.fr/ | P1 |
| **Transfer Tax (Droits de Mutation)** | Multiple articles | Property sale transfer tax | https://www.legifrance.gouv.fr/ | P1 |
| **Wealth Tax - IFI** | CGI L. 965 et seq. | Real estate wealth tax | https://www.legifrance.gouv.fr/ | P2 |

### 5B.3 French Accounting & Commercial Law

| Document | Citation | Subject | URL | Priority |
|----------|----------|---------|-----|----------|
| **Code de Commerce - Book II** | Articles L200-L250 | Accounting standards | https://www.legifrance.gouv.fr/codes/code_de_commerce.html | **P0** |
| **General Accounting Plan** | PCG | Chart of accounts standard | https://www.cncc.fr/ | P1 |
| **Ordonnance 45-104** | 1945 | Foundational accounting law | https://www.legifrance.gouv.fr/ | P2 |

---

## 6B. CANADIAN PROPERTY & TAX LAW

### 6B.1 Canadian Property Law

| Document | Citation | Type | URL | Priority |
|----------|----------|------|-----|----------|
| **Personal Property Security Act** | PPSA | Provincial Statute | Provincial legislature sites | **P0** |
| **Ontario Real Property Act** | R.S.O. 1990 c. R.30 | Provincial Statute | https://www.ontario.ca/laws/statute/90r30 | P1 |
| **Canada Mortgage & Housing Act** | RSC c. C-7.3 | Federal Statute | https://laws-lois.justice.gc.ca/eng/acts/C-7.3/ | P1 |

### 6B.2 Canadian Tax Law

| Document | Citation | Type | URL | Priority |
|----------|----------|------|-----|----------|
| **Income Tax Act §165** | RSC 1985, c I-2.3 | Federal Statute | https://laws-lois.justice.gc.ca/eng/acts/I-2.3/section-165 | **P0** |
| **Income Tax Act §108** | RSC 1985, c I-2.3 | Federal Statute | https://laws-lois.justice.gc.ca/eng/acts/I-2.3/section-108 | P1 |
| **Excise Tax Act (GST/HST)** | RSC 1985, c E-15 | Federal Statute | https://laws-lois.justice.gc.ca/eng/acts/E-15/ | P1 |
| **Capital Gains Tax (ITA §38-55)** | RSC 1985, c I-2.3 | Federal Statute | https://laws-lois.justice.gc.ca/eng/acts/I-2.3/page-1.html | P1 |
| **Provincial Sales Tax Acts** | Various | Provincial Statutes | Provincial sites | P1 |
| **BC Provincial Sales Tax Act** | RSBC 1996 | Provincial Statute | https://www.bclaws.gov.bc.ca/ | P1 |
| **Quebec Sales Tax (TVQ)** | Multiple | Provincial Statute | https://www2.finance.gouv.qc.ca/ | P1 |

### 6B.3 Canadian Accounting Standards

| Document | Citation | Type | URL | Priority |
|----------|----------|------|-----|----------|
| **Canada Business Corporations Act - Part 9** | RSC 1985, c C-44.2 | Federal Statute | https://laws-lois.justice.gc.ca/eng/acts/C-44.2/ | P1 |

---

## 7B. AUSTRALIAN PROPERTY, TAX & ACCOUNTING LAW

### 7B.1 Australian Property Law

| Document | Citation | Type | URL | Priority |
|----------|----------|------|-----|----------|
| **Property Law Act 1958** | VIC | State Statute | https://www.legislation.vic.gov.au/ | **P0** |
| **Property Law Act 2000** | QL | State Statute | https://www.legislation.qld.gov.au/ | **P0** |
| **Real Property Act 1900** | NSW (Division 4) | State Statute | https://www.legislation.nsw.gov.au/view/html/inforce/current/act-1900-025 | **P0** |
| **Torrens Title System Legislation** | Various states | State Statutes | Various state sites | **P0** |
| **Law of Property Act 1969** | NSW | State Statute | https://www.legislation.nsw.gov.au/ | P1 |
| **Uniform Civil Procedure Rules** | Various | Court Rules | Various court sites | P1 |

### 7B.2 Australian Tax Law

| Document | Citation | Type | URL | Priority |
|----------|----------|------|-----|----------|
| **Income Tax Assessment Act 1997 - Part 3-1** | Cth | Federal Statute | https://www.legislation.gov.au/C1997A00915/latest | **P0** |
| **A New Tax System (GST) Act 1999** | Cth | Federal Statute | https://www.legislation.gov.au/C1999A00010/latest | **P0** |
| **Income Tax Assessment Act 1997 - Division 7A** | Cth | Federal Statute | https://www.legislation.gov.au/C1997A00915/latest | P1 |
| **Fringe Benefits Tax Assessment Act 1986** | Cth | Federal Statute | https://www.legislation.gov.au/C1986A00125/latest | P1 |
| **Superannuation Industry (Supervision) Act 1993** | Cth | Federal Statute | https://www.legislation.gov.au/C1993A00043/latest | P1 |
| **State Land Tax Acts** | NSW, VIC, QLD | State Statutes | Various state sites | P1 |
| **Stamp Duty Acts** | Various states | State Statutes | Various state sites | P1 |

### 7B.3 Australian Accounting Standards

| Document | Citation | Type | URL | Priority |
|----------|----------|------|-----|----------|
| **Corporations Act 2001 - Part 2M.2-2M.9** | Cth | Federal Statute | https://www.legislation.gov.au/C2001A00049/latest | **P0** |
| **Australian Accounting Standards** | AASB | Accounting Standard | https://www.aasb.gov.au/standards | P1 |
| **AASB SME Standards** | AASB | Accounting Standard | https://www.aasb.gov.au/standards | P1 |

---

## 8B. UK PROPERTY, TAX & ACCOUNTING LAW

### 8B.1 UK Property Law

| Document | Citation | Type | URL | Priority |
|----------|----------|------|-----|----------|
| **Law of Property Act 1925** | c. 20 | Act | https://www.legislation.gov.uk/ukpga/Geo5/15-16/20 | **P0** |
| **Land Registration Act 2002** | c. 9 | Act | https://www.legislation.gov.uk/ukpga/2002/9 | **P0** |
| **Landlord and Tenant Act 1954** | c. 56 | Act | https://www.legislation.gov.uk/ukpga/Eliz2/2-3/56 | P1 |
| **Housing Act 1988** | c. 50 | Act | https://www.legislation.gov.uk/ukpga/1988/50 | P1 |
| **Commonhold & Leasehold Reform Act 2002** | c. 15 | Act | https://www.legislation.gov.uk/ukpga/2002/15 | P1 |
| **Land Registration Rules 2003** | SI 2003/1417 | Rules | https://www.legislation.gov.uk/uksi/2003/1417 | P1 |

### 8B.2 UK Tax Law

| Document | Citation | Type | URL | Priority |
|----------|----------|------|-----|----------|
| **Taxation of Chargeable Gains Act 1992** | c. 12 | Act | https://www.legislation.gov.uk/ukpga/1992/12/contents | **P0** |
| **Value Added Tax Act 1994** | c. 23 | Act | https://www.legislation.gov.uk/ukpga/1994/23 | **P0** |
| **Finance Act 2003 - Part 4 (SDLT)** | c. 14 (Pt. 4) | Act | https://www.legislation.gov.uk/ukpga/2003/14/part/4 | **P0** |
| **Corporation Tax Act 2010** | c. 4 | Act | https://www.legislation.gov.uk/ukpga/2010/4 | **P0** |
| **Late Payment of Commercial Debts Act 1998** | c. 20 | Act | https://www.legislation.gov.uk/ukpga/1998/20 | **P0** |
| **Finance Act 2023** | c. 1 | Act | https://www.legislation.gov.uk/ukpga/2023/1/contents | P1 |
| **Finance (No. 2) Act 2023** | c. 30 | Act | https://www.legislation.gov.uk/id/ukpga/2023/30 | P1 |
| **Stamp Duty Land Tax Act 2015** | c. 1 | Act | https://www.legislation.gov.uk/ukpga/2015/1/contents | P1 |
| **Late Payment Regulations 2013** | SI 2013/395 | Regulations | https://www.legislation.gov.uk/uksi/2013/395 | P1 |

### 8B.3 UK Accounting & Business Organization Law

| Document | Citation | Type | URL | Priority |
|----------|----------|------|-----|----------|
| **Companies Act 2006** | c. 46 | Act | https://www.legislation.gov.uk/ukpga/2006/46/contents | **P0** |
| **Limited Liability Partnerships Act 2000** | c. 12 | Act | https://www.legislation.gov.uk/ukpga/2000/12 | **P0** |
| **Sale of Goods Act 1979** | c. 54 | Act | https://www.legislation.gov.uk/ukpga/1979/54 | **P0** |
| **Supply of Goods & Services Act 1982** | c. 29 | Act | https://www.legislation.gov.uk/ukpga/1982/29 | **P0** |
| **Contracts (Rights of Third Parties) Act 1999** | c. 31 | Act | https://www.legislation.gov.uk/ukpga/1999/31 | **P0** |
| **Consumer Rights Act 2015** | c. 15 | Act | https://www.legislation.gov.uk/ukpga/2015/15 | **P0** |
| **Partnership Act 1890** | c. 39 | Act | https://www.legislation.gov.uk/ukpga/Vict/53-54/39 | P1 |
| **Sale & Supply of Goods Act 1994** | c. 35 | Act | https://www.legislation.gov.uk/ukpga/1994/35 | P1 |
| **Unfair Contract Terms Act 1977** | c. 50 | Act | https://www.legislation.gov.uk/ukpga/1977/50 | P1 |
| **LLP Regulations 2001** | SI 2001/1090 | Regulations | https://www.legislation.gov.uk/uksi/2001/1090 | P1 |
| **LLP (Application of Companies Act 2006) Regulations 2009** | SI 2009/1804 | Regulations | https://www.legislation.gov.uk/uksi/2009/1804 | P1 |
| **LLP (Application of Company Law) Regulations 2024** | SI 2024/234 | Regulations | https://www.legislation.gov.uk/uksi/2024/234 | P1 |
| **Companies Act 2006 (Amendment) Regulations 2008** | SI 2008/393 | Regulations | https://www.legislation.gov.uk/uksi/2008/393 | P1 |

---

## 9. SPAIN LEGAL DOCUMENTS (NEW - 28 Documents)

### 9.1 Employment & Labor Law

| Document | Type | Citation | URL | Priority | Notes |
|----------|------|----------|-----|----------|-------|
| **Estatuto de los Trabajadores** | Real Decreto Legislativo | RDL 2/2015 (23 Oct 2015) | https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430 | **P0** | Core employment law; last amended by Ley 2/2025. 92 articles covering contracts, hours, rights/duties. |
| **Ley del Estatuto del Trabajo Autónomo** | Statute | Ley 20/2007 (11 July 2007) | https://www.boe.es/buscar/act.php?id=BOE-A-2007-13409 | **P0** | Essential for freelancer classification. Establishes rights, obligations, social protection for autonomous workers. |
| **Ley sobre Infracciones y Sanciones** | Real Decreto Legislativo | RDL 5/2000 (4 Aug 2000) | https://www.boe.es/buscar/doc.php?id=BOE-A-2000-15060 | P1 | Defines administrative infractions and penalties in labor/social order. Prescription: 3 years. |
| **Ley de Prevención de Riesgos Laborales** | Statute | Ley 31/1995 (8 Nov 1995) | https://www.boe.es/buscar/act.php?id=BOE-A-1995-24292 | P1 | Workplace health/safety obligations for employers and self-employed. Essential for physical work contracts. |
| **Real Decreto-ley 32/2021** | Real Decreto-Ley | RDL 32/2021 (28 Dec 2021) | https://www.boe.es/buscar/act.php?id=BOE-A-2021-21788 | P2 | Recent labor market reform affecting employment relationships and contract stability. |

### 9.2 Intellectual Property Law

| Document | Type | Citation | URL | Priority | Notes |
|----------|------|----------|-----|----------|-------|
| **Ley de Propiedad Intelectual** | Real Decreto Legislativo | RDL 1/1996 (12 Apr 1996) | https://www.boe.es/buscar/act.php?id=BOE-A-1996-8930 | **P0** | Copyright, moral rights, economic rights. Last amended by RDL 6/2022. Essential for work product ownership. |
| **Ley de Patentes** | Statute | Ley 24/2015 (24 July 2015) | https://www.boe.es/buscar/act.php?id=BOE-A-2015-8328 | P1 | Patent protection for inventions. Effective 1 Apr 2017. Registration via OEPM. |
| **Reglamento de Ejecución de la Ley de Patentes** | Real Decreto | RD 316/2017 (31 Mar 2017) | https://www.boe.es/buscar/act.php?id=BOE-A-2017-3550 | P2 | Implementing regulation for patent procedures. |
| **Ley de Marcas** | Statute | Ley 17/2001 (7 Dec 2001) | https://www.boe.es/buscar/act.php?id=BOE-A-2001-23093 | P1 | Trademark registration and protection. Incorporates Madrid Protocol and TRIPS. |
| **Reglamento de Ejecución de la Ley de Marcas** | Real Decreto | RD 687/2002 (12 July 2002) | https://www.boe.es/buscar/act.php?id=BOE-A-2002-13981 | P2 | Implementing regulation for trademark administration. |
| **Ley de Secretos Empresariales** | Statute | Ley 1/2019 (20 Feb 2019) | https://www.boe.es/buscar/doc.php?id=BOE-A-2019-2364 | **P0** | Transposes EU Directive 2016/943. Effective 13 Mar 2019. Critical for confidentiality clauses. |
| **Ley de Competencia Desleal** | Statute | Ley 3/1991 (10 Jan 1991) | https://www.boe.es/buscar/act.php?id=BOE-A-1991-628 | P1 | Protects against unfair competition; modified by Ley 1/2019. Relevant for non-compete clauses. |

### 9.3 Tax Law

| Document | Type | Citation | URL | Priority | Notes |
|----------|------|----------|-----|----------|-------|
| **Ley del Impuesto sobre la Renta (IRPF)** | Statute | Ley 35/2006 (28 Nov 2006) | https://www.boe.es/buscar/act.php?id=BOE-A-2006-20764 | **P0** | Personal income taxation for self-employed workers. Classifies income as general and savings. Critical for tax obligations. |
| **Ley del Impuesto sobre el Valor Añadido** | Statute | Ley 37/1992 (28 Dec 1992) | https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740 | **P0** | Value Added Tax (IVA) on goods/services delivery. Incorporates EU Directives. Essential for invoicing. |
| **Reglamento del Impuesto sobre el Valor Añadido** | Real Decreto | RD 1624/1992 (29 Dec 1992) | https://www.boe.es/buscar/act.php?id=BOE-A-1992-28925 | P1 | Implements VAT Law 37/1992. Recently modified by RD 1171/2023 and RD 424/2021. |
| **Normas de Control Aduanero y Tributario** | Real Decreto | RD 1065/2007 | https://www.aeat.es/AEAT/Sede | P2 | Tax administration and control procedures by Agencia Tributaria. |
| **Seguridad Social - Régimen Especial de Trabajadores Autónomos** | Multiple | RDL 8/2015 (30 Oct 2015) | https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430 | **P0** | Social security contributions and benefits for autonomous workers. |

### 9.4 Property Law

| Document | Type | Citation | URL | Priority | Notes |
|----------|------|----------|-----|----------|-------|
| **Código Civil** | Real Decreto | Decreto 24 July 1889 | https://www.boe.es/buscar/act.php?id=BOE-A-1889-4763 | **P0** | Foundational law for civil/property contracts. Regularly amended (latest BOE 150/2024). |
| **Ley de Arrendamientos Urbanos** | Statute | Ley 29/1994 (24 Nov 1994) | https://www.boe.es/buscar/act.php?id=BOE-A-1994-26003 | P1 | Residential and commercial property leases. Recently amended for housing protection. Relevant for workspace leases. |
| **Ley Hipotecaria** | Decreto | Decreto 8 Feb 1946 | https://www.boe.es/buscar/act.php?id=BOE-A-1946-2453 | P2 | Property registration and mortgage procedures. Modified by Ley 13/2015 and Ley 5/2019. |
| **Ley de Catastro Inmobiliario** | Real Decreto Legislativo | RDL 1/2004 (5 Mar 2004) | https://www.boe.es/buscar/act.php?id=BOE-A-2004-4250 | P2 | Property registry and cadastral procedures. Modified by Ley 13/2015. |

### 9.5 Accounting Law

| Document | Type | Citation | URL | Priority | Notes |
|----------|------|----------|-----|----------|-------|
| **Plan General de Contabilidad** | Real Decreto | RD 1514/2007 (16 Nov 2007) | https://www.boe.es/buscar/act.php?id=BOE-A-2007-19884 | **P0** | Mandatory accounting framework for businesses. Recently modified by RD 1/2021. Critical for freelancer bookkeeping. |
| **Plan General de Contabilidad para Pymes** | Real Decreto | RD 1515/2007 (16 Nov 2007) | https://www.boe.es/buscar/act.php?id=BOE-A-2007-19966 | P1 | Simplified accounting framework for SMEs. Applicable to many freelancers as micro-enterprises. |
| **Código de Comercio** | Real Decreto | Decreto 22 Aug 1885 | https://www.boe.es/buscar/act.php?id=BOE-A-1885-6627 | P1 | Foundational commercial law. Establishes 3-year record retention requirement. |
| **Ley 3/2004 de Medidas contra la Morosidad** | Statute | Ley 3/2004 (20 Dec 2004) | https://www.boe.es/buscar/act.php?id=BOE-A-2004-21379 | P1 | Regulates payment terms and late payment interest. Affects freelancer default interest calculation. |

### 9.6 Business/Commercial Law (Supplementary)

| Document | Type | Citation | URL | Priority | Notes |
|----------|------|----------|-----|----------|-------|
| **Ley de Agencia** | Statute | Ley 12/1992 (27 May 1992) | https://www.boe.es/buscar/act.php?id=BOE-A-1992-12387 | P2 | Commercial agent relationships. Relevant if freelancer acts as agent. |
| **Ley de Sociedades de Capital** | Statute | Ley 2/1995 (23 Mar 1995) | https://www.boe.es/buscar/act.php?id=BOE-A-1995-7113 | P2 | Limited liability and joint stock companies. For corporate entity freelancers. |
| **GDPR Implementation** | EU Regulation | EU 679/2016 (27 Apr 2016) | https://www.boe.es/doue/2016/119/L00001-00088.pdf | P1 | Direct application in Spain. Affects privacy clauses and data processing terms. |
| **Ley Orgánica 3/2018 (LOPDGDD)** | Organic Law | LOPDGDD (5 Dec 2018) | https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673 | P1 | Spanish GDPR implementation. Governs personal data handling in contracts. |

---

## 10. HOUSING & RESIDENTIAL TENANCY LAW (73 SOURCES)

### 10.1 United Kingdom Housing Law (6 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Housing Act 1988** | c. 50 | Act | https://www.legislation.gov.uk/ukpga/1988/50 | **P0** | Residential tenancies; assured tenancies; remedies for breach |
| **Housing Act 1985** | c. 68 | Act | https://www.legislation.gov.uk/ukpga/1985/21 | **P0** | Council housing; secure tenancies; Right to Buy scheme |
| **Landlord and Tenant Act 1985** | c. 70 | Act | https://www.legislation.gov.uk/ukpga/1985/70 | **P0** | §11 repair obligations; landlord duties on maintenance |
| **Protection from Eviction Act 1977** | c. 43 | Act | https://www.legislation.gov.uk/ukpga/1977/43 | **P0** | Eviction procedures; 4-week notice requirement; unlawful eviction criminalizes |
| **Rent Act 1977** | c. 42 | Act | https://www.legislation.gov.uk/ukpga/1977/42 | P0 | Regulated tenancies (pre-1989); fair rent registration; succession rights |
| **Housing and Planning Act 2016** | c. 22 | Act | https://www.legislation.gov.uk/ukpga/2016/22 | P1 | Rogue landlords; banning orders; modern landlord/tenant regulation |

### 10.2 Spain Housing Law (3 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Ley de Arrendamientos Urbanos** | Ley 29/1994 (BOE 282/1994) | Statute | https://www.boe.es/buscar/act.php?id=BOE-A-1994-26003 | **P0** | Urban leases; tenant protections; rent controls; eviction procedures |
| **Ley de Propiedad Horizontal** | Ley 49/1960 (BOE 23/07/1960) | Statute | https://www.boe.es/buscar/act.php?id=BOE-A-1960-10906 | **P0** | Condominium ownership; community of owners; common property rights |
| **Real Decreto-Ley 7/2019 (Emergency Housing)** | RDL 7/2019 (BOE 05/03/2019) | Royal Decree | https://www.boe.es/buscar/act.php?id=BOE-A-2019-3244 | P1 | Minimum lease terms; rent update restrictions; vulnerable household protections |

### 10.3 United States Housing Law - Federal (4 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Fair Housing Act** | 42 U.S.C. §§ 3601-3619 | Statute | https://www.law.cornell.edu/uscode/text/42/3601 | **P0** | Discrimination protections; reasonable accommodation rights |
| **HUD Regulations (Fair Housing Implementation)** | 24 CFR Part 100 | Regulation | https://www.ecfr.gov/current/title-24/subtitle-B/chapter-I/part-100 | **P0** | Disability accommodations; design standards; lease requirements |
| **Lead-Based Paint Disclosure Requirements** | 24 CFR Part 35 (Subpart A) | Regulation | https://www.ecfr.gov/current/title-24/subtitle-A/part-35/subpart-A | **P0** | Mandatory disclosure for pre-1978 housing; 10-day inspection period |
| **National Fair Housing Commission Rules** | 42 U.S.C. § 3614 | Statute | https://www.justice.gov/crt/fair-housing-act-1 | P1 | Administrative complaint procedures; 100-day investigation timelines |

### 10.4 United States Housing Law - State Level (6 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **California Tenant Protection Act (AB 1482)** | CA Code § 1945 et seq. | State Statute | https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=201920200AB1482 | **P0** | 5% + CPI rent cap; just-cause eviction requirement |
| **New York Housing Stability & Tenant Protection Act** | NY Real Property Law, Article 2 | State Statute | https://nyassembly.gov/leg/?default_fld=&leg_video=&bn=A08281&term=2019 | **P0** | Security deposit limits; rent increase notice requirements; permanent protections |
| **New York Residential Tenancy Law** | NY Real Property Law, § 226-c | State Statute | https://www.nysenate.gov/legislation/laws/RPL/226-C | P1 | Lease terms; repair obligations; habitability standards |
| **Texas Property Code (Residential Tenancies)** | Texas Property Code, Ch. 92-103 | State Statute | https://statutes.capitol.texas.gov/Docs/PR/pdf/PR.92.pdf | P1 | Landlord/tenant duties; no statewide rent control |
| **Florida Residential Tenancy Law** | Florida Statutes, Chapter 83 | State Statute | https://www.flsenate.gov/Session/Bill/2024/627 | P1 | Rental regulations; security deposit procedures |
| **Illinois Residential Tenancy Law** | 735 ILCS 5/9-201 et seq. | State Statute | https://ilga.gov/commission/lrs/handbook/chtopics/101tenancy.pdf | P1 | Habitability standards; termination procedures |

### 10.5 Canada Housing Law (3 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **National Housing Act** | RSC 1985, c N-11 | Statute | https://laws-lois.justice.gc.ca/eng/acts/n-11/FullText.html | P0 | CMHC programs; insured mortgages; rental housing framework |
| **National Housing Strategy Act** | R.S.C. 1985, c. N-11.2 | Statute | https://laws-lois.justice.gc.ca/eng/acts/n-11.2/FullText.html | P1 | Federal housing policy objectives; adequate/affordable housing goals |
| **Canada Mortgage and Housing Corporation Regulations** | SOR 80-159 | Regulations | https://laws-lois.justice.gc.ca/eng/regulations/80-159/FullText.html | P1 | CMHC insurance programs; mortgage requirements |

### 10.6 Quebec Housing Law (3 sources - FRENCH/BILINGUAL)

| Document | Citation | Type | URL (French) | Priority | Notes |
|----------|----------|------|-------------|----------|-------|
| **Code Civil du Québec - Lease (Articles 1851-2000.1)** | CCQ 1851-2000.1 | Provincial Code | https://www.legisquebec.gouv.qc.ca/fr/document/cc | **P0** | Residential/commercial lease framework; tenant rights; landlord obligations (FR) |
| **Loi sur la Régie du logement (TAL)** | RLRQ, c. R-8.1 | Provincial Statute | https://www.legisquebec.gouv.qc.ca/fr/document/lc/r-8.1 | **P0** | Tribunal administratif du logement; residential lease disputes; rent adjustment (FR) |
| **Regulation respecting the TAL** | RLRQ, c. T-16 | Regulation | https://www.legisquebec.gouv.qc.ca/fr/document/rc/T-16 | P1 | TAL procedural rules; hearing procedures; decision timelines (FR) |

### 10.7 Australia Housing Law - State Level (4 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Residential Tenancies Act 2010 (NSW)** | No. 42 of 2010 | State Statute | https://legislation.nsw.gov.au/view/html/inforce/current/act-2010-042 | **P0** | NSW tenancy law; 90/60 day notice; pet consent reasonableness; minimum housing standards |
| **Residential Tenancies Act 1997 (Victoria)** | Ch. 2.1, Act No. 107/1997 | State Statute | https://www.legislation.vic.gov.au/in-force/acts/residential-tenancies-act-1997 | **P0** | Victoria tenancy law; bond requirements; Commissioner oversight |
| **Residential Tenancies and Rooming Accommodation Act 2008 (Queensland)** | No. 73 of 2008 | State Statute | https://www.legislation.qld.gov.au/view/html/inforce/current/act-2008-073 | P1 | Queensland tenancy law; rooming house rules; domestic violence protections |
| **National Consumer Credit Protection Act 2009** | Act No. 139 of 2009 | Federal Statute | https://www.legislation.gov.au/C2009A00139/latest/text | P1 | Mortgage regulation; responsible lending obligations |

### 10.8 Germany Housing Law (5 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **BGB §§ 535-580a (Rental Law)** | BGB § 535-580a | Civil Code | https://www.gesetze-im-internet.de/englisch_bgb/ | **P0** | German rental law; landlord duties; tenant rights; lease termination |
| **Mietpreisbremse (Rent Brake Act)** | BGB Amendment (1 June 2015) | Statute | https://www.gesetze-im-internet.de/mietbremse/ | **P0** | Rent control (max 10% above local average); designated tight markets through Dec 31, 2029 |
| **Betriebskostenverordnung (Operating Costs Reg)** | BetrKV (current version) | Ordinance | https://www.gesetze-im-internet.de/betrkv_2004/ | **P0** | Apportionable costs to tenants; 17 categories; transparent rent structure |
| **Wohnungseigentumsgesetz (Condominium Act)** | WEG (as amended by WEMoG 2020) | Statute | https://www.gesetze-im-internet.de/woeigg/ | P1 | Apartment/condominium ownership; common elements; owners' assembly management |

### 10.9 France Housing Law (4 sources - FRENCH)

| Document | Citation | Type | URL (French) | Priority | Notes |
|----------|----------|------|-------------|----------|-------|
| **Loi ALUR (Housing Access & Urban Planning)** | Loi 2014-366 (24 mars 2014) | Statute | https://www.legifrance.gouv.fr/loda/id/JORFTEXT000028772256 | **P0** | Tenant protections; standardized leases; rent control for tense areas (FR) |
| **Loi ELAN (Housing Evolution & Urban Planning)** | Loi 2018-1021 (23 nov 2018) | Statute | https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000037639478 | **P0** | Mobility leases; construction modernization; local rent observatories (FR) |
| **Code de la construction et de l'habitation** | CCH (consolidated) | Code | https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006074096/ | P1 | Building/housing code; construction standards; energy efficiency (FR) |
| **Décret Encadrement des Loyers (Rent Control)** | Décret 2024-854 (24 juillet 2024) | Decree | https://www.ecologie.gouv.fr/politiques-publiques/encadrement-loyers | P2 | Annual rent limits for Paris, Lille, Lyon, Bordeaux, others; reference rent system (FR) |

### 10.10 European Union Housing Law (3 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Energy Performance of Buildings Directive** | 2010/31/EU | EU Directive | https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32010L0031 | **P0** | Energy certification for residential sales/leases; NZEB standards; valid 10 years |
| **Mortgage Credit Directive** | 2014/17/EU | EU Directive | https://eur-lex.europa.eu/eli/dir/2014/17/oj/eng | **P0** | Consumer protection for residential mortgages; creditworthiness assessment; ESIS |
| **Services Directive (Bolkestein)** | 2006/123/EC | EU Directive | https://eur-lex.europa.eu/eli/dir/2006/123/oj/eng | P2 | Service provision across EU; property management services facilitation |

---

## 10B. INSURANCE LAW (43 SOURCES)

### 10B.1 United Kingdom Insurance Law (6 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Insurance Act 2015** | c. 4 | Act | https://www.legislation.gov.uk/ukpga/2015/4/notes/division/5 | **P0** | Duty of fair presentation; professional indemnity; reforms 110+ year old law |
| **Consumer Insurance (Disclosure & Representations) Act 2012** | c. 6 | Act | https://www.legislation.gov.uk/ukpga/2012/6/contents | **P0** | Consumer duty; replaces voluntary disclosure with reasonable care standard |
| **Third Parties (Rights Against Insurers) Act 2010** | c. 10 | Act | https://www.legislation.gov.uk/ukpga/2010/10/contents | **P0** | Direct claim against insurers; third-party protection; no need to establish liability |
| **Financial Services and Markets Act 2000** | c. 8 | Act | https://www.legislation.gov.uk/ukpga/2000/8/contents | P1 | Insurance distribution regulation; FCA/PRA oversight; authorization requirements |
| **SRA Guidance: Insurance Act 2015 Consequential Changes** | Guidance | Guidance | https://www.sra.org.uk/solicitors/guidance/insurance-act-2015-consequential-changes-minimum-terms-conditions-professional-indemnity-insurance/ | P1 | Professional indemnity minimum terms for solicitors |
| **Proceeds of Crime Act 2002** | c. 29 | Act | https://www.legislation.gov.uk/ukpga/2002/29/contents | P1 | Money laundering provisions; confiscation; proceeds recovery |

### 10B.2 Spain Insurance Law (3 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Ley de Contrato de Seguro** | Ley 50/1980 (BOE 22501/1980) | Act | https://www.boe.es/buscar/act.php?id=BOE-A-1980-22501 | **P0** | Fundamental insurance contract law; rights/obligations of parties |
| **Ley de Supervisión de Seguros (Solvency II)** | Ley 20/2015 (BOE 7897/2015) | Act | https://www.boe.es/buscar/act.php?id=BOE-A-2015-7897 | **P0** | Insurance company organization; solvency requirements; effective 1 Jan 2016 |
| **Real Decreto Legislativo 6/2004 (Insurance Management)** | RDL 6/2004 (BOE 18908/2004) | Legislative Decree | https://www.boe.es/buscar/doc.php?id=BOE-A-2004-18908 | P1 | Consolidated insurance management; supervision; private insurance |

### 10B.3 United States Insurance Law (6 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **McCarran-Ferguson Act** | 15 USC §1011-1015 | Statute | https://www.law.cornell.edu/uscode/text/15/6701 | **P0** | Federal/state regulatory framework; state delegation; antitrust exemption |
| **ERISA** | Employee Retirement Income Security Act | Statute | https://www.dol.gov/general/topic/health-plans/erisa | P1 | Employee benefit insurance; fiduciary duties; health insurance regulation |
| **California Insurance Code § 533** | CA Insurance Code § 533 | State Code | https://www.insurance.ca.gov/0250-insurers/0500-legal-info/0200-regulations/cic100-124.cfm | P1 | Professional liability; intentional misconduct exclusion |
| **California BPC § 801** | CA Business & Professions Code § 801 | State Code | https://codes.findlaw.com/ca/business-and-professions-code/bpc-sect-801.html | P1 | Professional liability reporting (settlements >$3K) |
| **New York Insurance Law § 2307(b)** | NY Insurance Law § 2307(b) | State Code | https://www.law.cornell.edu/regulations/new-york/17-NYCRR-127.3 | P1 | Policy form approval; regulatory requirements |
| **Texas Insurance Code Chapter 1901** | Texas Insurance Code Ch. 1901 | State Code | https://statutes.capitol.texas.gov/Docs/IN/htm/IN.1901.htm | **P0** | Professional liability for healthcare providers |

### 10B.4 Canada Insurance Law (2 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Insurance Companies Act** | Insurance Companies Act | Statute | https://laws.justice.gc.ca/eng/acts/I-11.8/ | **P0** | Federal insurance regulation; incorporation; OSFI oversight |
| **Financial Consumer Agency Regulations** | Financial Consumer Agency | Regulation | https://www.canada.ca/en/financial-consumer-agency/services/industry/regulated-entities/insurance-companies.html | P1 | Consumer protection; FCAC monitoring |

### 10B.5 Quebec Insurance Law (4 sources - FRENCH/BILINGUAL)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Loi sur les assurances** | CQLR c A-32 | Act | https://www.canlii.org/en/qc/laws/stat/cqlr-c-a-32/latest/cqlr-c-a-32.html | **P0** | Insurance regulation; authorization; governance (FR) |
| **Code Civil du Québec Book VII (Insurance Contracts)** | CCQ Articles 2389-2632 | Civil Code | https://www.canlii.org/en/qc/laws/stat/cqlr-c-ccq-1991/latest/cqlr-c-ccq-1991.html | **P0** | Insurance contracts; Article 2389 definition; maritime/terrestrial insurance (FR) |
| **AMF Regulations on Insurance Authorization** | AMF Regulation | Regulation | https://lautorite.qc.ca/en/professionals/insurers/right-to-practise/authorization | P1 | Insurance company authorization; AMF oversight (FR) |
| **Regulation under Insurance Act** | CQLR c A-32.1, r 1 | Regulation | https://www.canlii.org/en/qc/laws/regu/cqlr-c-a-32.1-r-1/latest/cqlr-c-a-32.1-r-1.html | P1 | Insurance operations; technical requirements (FR) |

### 10B.6 Australia Insurance Law (5 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Insurance Contracts Act 1984** | Cth | Act | https://www.legislation.gov.au/Details/C2022C00015 | **P0** | §13 utmost good faith; §54 technical claim defenses; fundamental Australian insurance law |
| **Insurance Act 1973** | Cth | Act | https://www.legislation.gov.au/Details/C2022C00134 | **P0** | Insurance supervision; licensing; APRA solvency regulation |
| **APRA Prudential Standards for Insurers** | APRA Standards | Standards | https://www.apra.gov.au/prudential-policy | P1 | Governance; risk management; financial resilience; resolution frameworks |
| **Professional Standards Legislation (State-Level)** | Various States | Statutes | https://www.legislation.gov.au/Details/C2022C00134 | P1 | Professional indemnity requirements; state-specific |
| **Corporations Act 2001 - Financial Services** | Cth | Act | https://www.legislation.gov.au/Series/C2001A00067 | P1 | Financial services fraud; misleading conduct; professional standards |

### 10B.7 Germany Insurance Law (4 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Versicherungsvertragsgesetz (VVG - Insurance Contract Act)** | VVG | Act | https://www.gesetze-im-internet.de/englisch_vvg/englisch_vvg.html | **P0** | Insurance contracts; policyholder protection; 2008 reform of German insurance law |
| **Versicherungsaufsichtsgesetz (VAG - Insurance Supervision Act)** | VAG | Act | https://www.bafin.de/SharedDocs/Downloads/EN/Aufsichtsrecht/dl_vag_en_va.html | **P0** | BaFin oversight; authorization; policyholder/beneficiary protection |
| **Regulation on Information Obligations (VVG-InfoV)** | VVG-InfoV | Regulation | https://www.bafin.de/SharedDocs/Veroeffentlichungen/EN/Aufsichtsrecht/Verordnung/VVG-InfoV_va_en.html | P1 | Insurance contract information requirements; disclosure obligations |
| **Bürgerliches Gesetzbuch (BGB - Supplementary)** | BGB | Civil Code | https://www.gesetze-im-internet.de/englisch_bgb/ | P1 | General contract law; liability attribution; supplementary insurance provisions |

### 10B.8 France Insurance Law (4 sources - FRENCH)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Code des assurances** | Code | Code | https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006073984/ | **P0** | Comprehensive insurance regulation; liability insurance (Articles L124-1 to L124-5) (FR) |
| **Loi Hamon 2014-344 (Consumer Insurance)** | Loi 2014-344 | Act | https://www.legifrance.gouv.fr/loda/id/JORFTEXT000028738036 | **P0** | Consumer insurance rights; infra-annual cancellation; strengthened protections (FR) |
| **Code de la mutualité (Mutual Insurance)** | Code | Code | https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006074067/ | P1 | Mutual (non-profit) insurance organizations; cooperative structure (FR) |
| **Article L. 124-3 (Direct Action Rights)** | Code Article | Code Article | https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006073984/ | P1 | Direct action against liable party and liability insurer (FR) |

### 10B.9 European Union Insurance Law (5 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Solvency II Directive** | 2009/138/EC | Directive | https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=celex:32009L0138 | **P0** | Capital requirements; three-pillar structure; harmonized prudential rules |
| **Delegated Regulation (EU) 2015/35** | 2015/35 | Regulation | https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=celex:32015R0035 | **P0** | Solvency II implementation; technical standards; effective Jan 2016 |
| **Insurance Distribution Directive (IDD)** | 2016/97/EU | Directive | https://eur-lex.europa.eu/eli/dir/2016/97/oj/eng | **P0** | Insurance mediation; professional liability insurance EUR 1.3M minimum per claim |
| **Delegated Regulation (EU) 2019/1935 (IDD Updates)** | 2019/1935 | Regulation | https://eur-lex.europa.eu/eli/dir/2016/97/2020-06-12/eng | P1 | EUR amounts adjustments; professional indemnity EUR 1,300,380 per claim |
| **Insurance Mediation Directive** | 2002/92/EC | Directive | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32002L0092 | P1 | Predecessor to IDD; minimum professional standards; indemnity requirements |

---

## 10C. CONSTRUCTION LAW (58 SOURCES)

### 10C.1 United Kingdom Construction Law (7 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Housing Grants, Construction & Regeneration Act 1996** | c. 53 | Act | https://www.legislation.gov.uk/ukpga/1996/53/ | **P0** | Payment terms; interim/stage payments; Part 2 payment mechanisms |
| **Local Democracy, Economic Development & Construction Act 2009** | c. 20 | Act | https://www.legislation.gov.uk/ukpga/2009/20/contents | **P0** | Adjudication framework; amends Part 2 of HGCRA |
| **Building Act 1984** | c. 55 | Act | https://www.legislation.gov.uk/ukpga/1984/55/ | **P0** | Building control; safety standards; applies England & Wales |
| **Building Regulations 2010** | SI 2010/2214 | Statutory Instrument | https://www.legislation.gov.uk/uksi/2010/2214/pdfs/uksi_20102214_en.pdf | **P0** | Building standards; Parts A-P technical requirements |
| **JCT Standard Forms** | Standard Forms | Standard Contract | https://www.jctltd.co.uk/ | P1 | Industry-standard construction contracts; payment terms; dispute resolution |
| **NEC Standard Forms** | Standard Forms | Standard Contract | https://www.nec.org.uk/ | P1 | Performance-based contracts; pain/gain mechanisms; compensation |
| **FIDIC Standard Forms** | Standard Forms | Standard Contract | https://fidic.org/contracts | P1 | International construction contracts; conditions of contract |

### 10C.2 United States Construction Law - Federal (4 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Miller Act** | 40 USC §§ 3131-3134 | Statute | https://uscode.house.gov/view.xhtml?path=/prelim@title40/subtitle2/partA/chapter31/subchapter3 | **P0** | Federal bonds; payment bonds >$100k; 90-day civil action right |
| **Davis-Bacon Act** | 40 USC §§ 3141-3148 | Statute | https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title40-chapter31-subchapter4 | **P0** | Prevailing wage requirements; federally-funded construction |
| **Federal Prompt Payment Act** | 31 USC §§ 3901-3905 | Statute | https://www.law.cornell.edu/cfr/text/48/52.232-27 | **P0** | 14 days to pay prime; 7-day cascading; interest penalties |
| **FAR 52.232-27** | FAR 52.232-27 | Regulation | https://www.acquisition.gov/far/52.232-27 | **P0** | Federal contract clause; prompt payment implementation |

### 10C.3 United States Construction Law - State Level (5 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **California Mechanics Lien Law** | CA Civil Code §§ 8000 et seq. | State Statute | https://law.justia.com/codes/california/code-civ/division-4/part-6/title-2/chapter-4/article-2/section-8416/ | **P0** | Constitutional lien rights; §8416 claim requirements; design professionals included |
| **California Prompt Payment Act (AB 1648)** | AB 1648 | State Statute | https://www.levelset.com/mechanics-lien/california-lien-law-faqs/ | P1 | State-level prompt payment protections |
| **New York Lien Law Article 2** | NY Lien Law §§ 1-97 | State Statute | https://codes.findlaw.com/ny/lien-law/lie-sect-2/ | **P0** | Contractors/subcontractors/laborers; 5-day service; 1-year validity |
| **Texas Property Code - Mechanics Lien** | Texas Property Code Ch. 53 | State Statute | https://statutes.capitol.texas.gov/Docs/PR/htm/PR.53.htm | **P0** | Constitutional lien; 10% reserved funds; filing deadlines vary |
| **Florida Construction Lien Law** | Florida Statutes Ch. 713 | State Statute | https://www.leg.state.fl.us/Statutes/index.cfm?App_mode=Display_Statute&URL=0700-0799/0713/0713.html | **P0** | Mechanics liens; notice requirements; applies architects/engineers |

### 10C.4 Spain Construction Law (4 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Ley de Ordenación de la Edificación** | Ley 38/1999 (BOE 21567/1999) | Act | https://www.boe.es/buscar/act.php?id=BOE-A-1999-21567 | **P0** | Building agents; 10-year structural defects warranty |
| **Código Técnico de la Edificación (CTE)** | RD 314/2006 (BOE 5515/2006) | Royal Decree | https://www.boe.es/buscar/act.php?id=BOE-A-2006-5515 | **P0** | Technical building standards; basic safety requirements |
| **Ley de Contratos del Sector Público (LCSP)** | Ley 9/2017 (BOE 12902/2017) | Act | https://www.boe.es/buscar/act.php?id=BOE-A-2017-12902 | P1 | Public works contracts; EUR 40k threshold; EU Directive transposition |
| **Code of Public Sector Contracts** | LCSP Reference | Code | https://www.boe.es/biblioteca_juridica/codigos/codigo.php?id=031 | P1 | Public procurement; consolidated version with amendments |

### 10C.5 Canada Construction Law (2 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Federal Prompt Payment for Construction Work Act** | Federal Act | Statute | https://laws.justice.gc.ca/eng/acts/F-7.7/FullText.html | **P0** | 28-day government payment; 7-day cascading; in force 9 Dec 2023 |
| **Federal Prompt Payment Regulations (CanDACC)** | Federal Regulation | Regulation | https://gazette.gc.ca/rp-pr/p1/2023/2023-02-25/html/reg3-eng.html | **P0** | Adjudication; Canada Dispute Adjudication for Construction Contracts |

### 10C.6 Quebec Construction Law (4 sources - FRENCH/BILINGUAL)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Code Civil du Québec - Contract for Enterprise** | CCQ Articles 2098-2129 | Civil Code | https://www.legisquebec.gouv.qc.ca/en/version/cs/CCQ-1991?code=se:2098&history=20231009 | **P0** | Construction contracts; 1-year poor workmanship warranty; 5-year structural warranty (FR) |
| **Loi sur le bâtiment (Building Act)** | CQLR c B-1.1 | Act | https://www.legisquebec.gouv.qc.ca/en/document/cs/B-1.1 | **P0** | Building regulation; RBQ establishment; contractor qualifications (FR) |
| **Code de construction du Québec** | CQLR c B-1.1, r. 2 | Code | https://www.legisquebec.gouv.qc.ca/en/document/cr/b-1.1,%20r.%202 | **P0** | Technical construction requirements; 2015 edition with 2025 amendments (FR) |
| **Loi R-20 (Labour Relations in Construction)** | RLRQ c R-20 | Act | https://www.legisquebec.gouv.qc.ca/en/document/cs/R-20/20011220 | P1 | Construction labor relations; CCQ oversight; 4 industry sectors (FR) |

### 10C.7 Australia Construction Law - State Level (4 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Building and Construction Industry Security of Payment Act 1999 (NSW)** | Act 1999 | Act | https://legislation.nsw.gov.au/view/whole/html/inforce/current/act-1999-046 | **P0** | Progress payments; adjudication; ensures payment recovery right |
| **Building and Construction Industry Security of Payment Act 2002 (VIC)** | Act 2002 | Act | https://www.legislation.vic.gov.au/ | **P0** | Victoria's security of payment regime |
| **Building Industry Fairness (Security of Payment) Act 2017 (QLD)** | Act 2017 | Act | https://www.legislation.qld.gov.au/ | **P0** | Queensland security of payment; fairness provisions |
| **Building and Construction Industry (Security of Payment) Act 2021 (WA)** | Act 2021 | Act | https://www.austlii.edu.au/cgi-bin/viewdb/au/legis/wa/consol_act/baciopa2021606/ | **P0** | Western Australia regime; effective 1 Aug 2022 |

### 10C.8 Australia Construction Law - National (3 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **National Construction Code (NCC) 2022** | NCC 2022 | Code | https://ncc.abcb.gov.au/ | **P0** | Performance-based code; BCA Vol 1-2 + PCA Vol 3; state/territory mandated |
| **Australian Consumer Law - Competition and Consumer Act 2010** | Schedule 2, CCA 2010 | Act | https://www.accc.gov.au/consumers/buying-products-and-services/warranties | P1 | Statutory warranties; cannot be excluded |
| **Home Building Act 1989 (NSW) §18D** | NSW Act | Act | https://www.fairtrading.nsw.gov.au/ | P1 | Construction warranties; extends to successors in title |

### 10C.9 Germany Construction Law (4 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **BGB §§ 631-651 (Construction Contracts)** | BGB § 631-651 | Civil Code | https://www.gesetze-im-internet.de/englisch_bgb/ | **P0** | Work contracts; warranties; §§650a-650h construction-specific; consumer protection |
| **VOB (Vergabe- und Vertragsordnung für Bauleistungen)** | VOB | Standard Conditions | https://www.dinmedia.de/en/publication/vob-2019-in-english/309711398 | **P0** | Public procurement; VOB/A (procurement); VOB/B (conditions); VOB/C (specs) |
| **Baugesetzbuch (BauGB - Building Code)** | BauGB | Federal Statute | https://germanlawarchive.iuscomp.org/?p=649 | P1 | Land-use planning; zoning; urban development regulation |
| **Landesbauordnungen (State Building Codes)** | State Codes | State Codes | https://www.dibt.de/en/we-offer/technical-building-rules | P1 | Individual state building codes; DIBt technical rules |

### 10C.10 France Construction Law (4 sources - FRENCH)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Code de la construction et de l'habitation** | CCH | Code | https://www.legifrance.gouv.fr/ | **P0** | Building/construction regulation; construction standards; safety (FR) |
| **Loi Spinetta (1792+ Decennial Liability)** | Loi 78-12 | Act | https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000693683 | **P0** | 10-year builder liability; mandatory decennial & dommages-ouvrage insurance; effective 1979 (FR) |
| **Loi MOP (Public Project Ownership)** | Loi 85-704 | Act | https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000693683 | P1 | Public construction; MOA/MOE relationship; repealed except Article 1 (FR) |
| **Code Civil Articles 1792-1792-7 (Construction Warranties)** | Code Civil Art. 1792+ | Civil Code | https://www.legifrance.gouv.fr/ | **P0** | Decennial (10yr); 2-year operation; 1-year completion warranties (FR) |

### 10C.11 European Union Construction Law (2 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Public Procurement Directive 2014/24/EU** | 2014/24/EU | Directive | https://eur-lex.europa.eu/eli/dir/2014/24/oj/eng | **P0** | Public works procurement >EUR 5.5M threshold; all member states |
| **Construction Products Regulation (EU) 305/2011** | 305/2011 | Regulation | https://eur-lex.europa.eu/eli/reg/2011/305/oj/eng | **P0** | Product standards; CE marking; replaces 89/106/EEC |

---

## 10D. CRIMINAL LAW (52 SOURCES - Contract Fraud, White-Collar Crime)

### 10D.1 United Kingdom Criminal Law (9 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Fraud Act 2006** | c. 35 | Act | https://www.legislation.gov.uk/ukpga/2006/35/contents | **P0** | Fraud (§1-2); false representation; possession of articles (§6) |
| **Theft Act 1968** | c. 60 | Act | https://www.legislation.gov.uk/ukpga/1968/60/contents | **P0** | Theft; embezzlement (§15-20); dishonesty element foundational |
| **Theft Act 1978** | c. 31 | Act | https://www.legislation.gov.uk/ukpga/1978/31/contents | P1 | Obtaining services by deception; evasion of liability |
| **Bribery Act 2010** | c. 23 | Act | https://www.legislation.gov.uk/ukpga/2010/23/contents | **P0** | Bribery (§1-5); corporate liability (§7); foreign official bribes |
| **Proceeds of Crime Act 2002** | c. 29 | Act | https://www.legislation.gov.uk/ukpga/2002/29/contents | P1 | Money laundering (Part 7, §327-330); confiscation; recovery |
| **Computer Misuse Act 1990** | c. 18 | Act | https://www.legislation.gov.uk/ukpga/1990/18/contents | P1 | Unauthorized access (§1); modification (§3); fraud by electronic means |
| **Criminal Justice Act 1993** | c. 36 | Act | https://www.legislation.gov.uk/ukpga/1993/36/contents | P2 | Insider trading (Part V, §52-64); securities fraud |
| **Financial Services and Markets Act 2000** | c. 8 | Act | https://www.legislation.gov.uk/ukpga/2000/8/contents | P1 | Market abuse (§118); false statements (§397); financial crime |
| **Forgery and Counterfeiting Act 1981** | c. 45 | Act | https://www.legislation.gov.uk/ukpga/1981/45/contents | P2 | Forgery (§1-5); falsified contracts/documents |

### 10D.2 United States Criminal Law - Federal (12 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **18 USC Chapter 47 - Fraud and False Statements** | 18 USC Ch. 47 | Statute | https://www.law.cornell.edu/uscode/text/18/part-I/chapter-47 | **P0** | Federal fraud statutes; false statements (§1001); foundation of fraud law |
| **18 USC §1341 - Mail Fraud** | 18 USC § 1341 | Statute | https://www.law.cornell.edu/uscode/text/18/1341 | **P0** | Mail fraud; conspiracy (§1349); classic fraud statute |
| **18 USC §1343 - Wire Fraud** | 18 USC § 1343 | Statute | https://www.law.cornell.edu/uscode/text/18/1343 | **P0** | Wire fraud; interstate commerce; electronic communications |
| **18 USC §1348 - Securities Fraud** | 18 USC § 1348 | Statute | https://www.law.cornell.edu/uscode/text/18/1348 | P1 | Securities fraud; contract valuation/asset fraud |
| **18 USC §1956-1957 - Money Laundering** | 18 USC § 1956-1957 | Statute | https://www.law.cornell.edu/uscode/text/18/part-I/chapter-95 | P1 | Money laundering; proceeds concealment |
| **18 USC §1831-1839 - Economic Espionage** | 18 USC § 1831-1839 | Statute | https://www.law.cornell.edu/uscode/text/18/part-I/chapter-90 | P1 | Trade secret theft; confidential information misappropriation |
| **Sarbanes-Oxley Act (SOX)** | 15 USC §7201 et seq. | Act | https://www.law.cornell.edu/uscode/text/15/chapter-98 | P1 | Corporate fraud (§906); audit violations; public company requirements |
| **Foreign Corrupt Practices Act (FCPA)** | 15 USC §78dd-1 et seq. | Act | https://www.law.cornell.edu/uscode/text/15/part-I/chapter-2D | **P0** | Bribery of foreign officials; cross-border contract corruption |
| **Racketeer Influenced and Corrupt Organizations Act (RICO)** | 18 USC §1961 et seq. | Act | https://www.law.cornell.edu/uscode/text/18/part-I/chapter-96 | P1 | Enterprise fraud; organized contract fraud schemes |
| **Bank Fraud Act** | 18 USC § 1344 | Statute | https://www.law.cornell.edu/uscode/text/18/1344 | P1 | Fraud affecting federally-insured banks; contract finance fraud |
| **Conspiracy to Commit Fraud** | 18 USC § 371 | Statute | https://www.law.cornell.edu/uscode/text/18/371 | P1 | General conspiracy statute; multi-actor contract fraud |
| **18 USC §1401 - Identity Fraud** | 18 USC § 1401 | Statute | https://www.law.cornell.edu/uscode/text/18/1401 | P2 | Identity theft; fraudulent misrepresentation of parties |

### 10D.3 Canada Criminal Law (10 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Criminal Code - Section 380 (Fraud)** | Section 380 | Statute | https://laws-lois.justice.gc.ca/eng/acts/C-46/page-135.html | **P0** | Fraud; deceit; dishonesty |
| **Criminal Code - Section 322 (Theft)** | Section 322 | Statute | https://laws-lois.justice.gc.ca/eng/acts/C-46/page-105.html | **P0** | Theft; property crimes; contract-related |
| **Criminal Code - Section 336 (Breach of Trust)** | Section 336 | Statute | https://laws-lois.justice.gc.ca/eng/acts/C-46/page-111.html | **P0** | Breach of trust; commercial trust violations |
| **Criminal Code - Section 122 (Bribery)** | Section 122 | Statute | https://laws-lois.justice.gc.ca/eng/acts/C-46/page-60.html | P1 | Bribery of judicial officers; corruption |
| **Criminal Code - Section 125** | Section 125 | Statute | https://laws-lois.justice.gc.ca/eng/acts/C-46/page-61.html | P1 | Bribery of peace officers; contract enforcement obstruction |
| **Criminal Code - Section 352 (Forgery)** | Section 352 | Statute | https://laws-lois.justice.gc.ca/eng/acts/C-46/page-115.html | P1 | Forgery; false documents; falsified contracts |
| **Criminal Code - Section 362 (False Pretence)** | Section 362 | Statute | https://laws-lois.justice.gc.ca/eng/acts/C-46/page-118.html | **P0** | False pretence; deception; contract performance fraud |
| **Corruption of Foreign Public Officials Act** | S.C. 1998, c. 34 | Act | https://laws-lois.justice.gc.ca/eng/acts/C-45.2/index.html | **P0** | Foreign official bribery; international contract corruption |
| **Proceeds of Crime (Money Laundering) Act** | S.C. 2000, c. 17 | Act | https://laws-lois.justice.gc.ca/eng/acts/P-24.501/index.html | P1 | Money laundering; proceeds concealment |
| **Competition Act - Criminal Provisions** | R.S.C. 1985, c. C-34 | Act | https://laws-lois.justice.gc.ca/eng/acts/C-34/index.html | P1 | Price fixing; bid-rigging; anti-competitive contracting |

### 10D.4 Australia Criminal Law - Federal (8 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Criminal Code Act 1995 (Cth) - Chapter 7 (Fraud)** | Ch. 7 | Act | https://www.legislation.gov.au/Series/C1995A00488 | **P0** | Fraud (§135.1-4); obtaining financial advantage by deception (§136.1) |
| **Criminal Code Act 1995 (Cth) - Chapter 6 (Money Laundering)** | Ch. 6 | Act | https://www.legislation.gov.au/Series/C1995A00488 | P1 | Money laundering; proceeds handling |
| **Corporations Act 2001 (Cth) - Chapter 7 (Financial Services)** | Ch. 7 | Act | https://www.legislation.gov.au/Series/C2001A00067 | P1 | Financial services fraud; misleading conduct (§1043H) |
| **Anti-Money Laundering and Counter-Terrorism Financing Act 2006** | Act 2006 | Act | https://www.legislation.gov.au/Series/C2006A00169 | P1 | AML/CTF obligations; reporting |
| **Crimes Act 1900 (NSW) - Part 4A (Fraud)** | Part 4A | Act | https://www.legislation.nsw.gov.au/view/html/inforce/current/act-1900-040 | P1 | Obtaining property by fraud (§192E); dishonest advantage (§192F) |
| **Crimes Act 1958 (VIC) - Division 1 (Fraud)** | Div. 1 | Act | https://www.legislation.vic.gov.au/in-force/acts/crimes-act-1958 | P1 | Fraud (§16A); obtaining by deception (§81) |
| **Crimes Act 1913 (WA)** | WA Act | Act | https://www.legislation.wa.gov.au/legislation/statutes/crimes-act-1913 | P1 | Obtaining by false pretence (§403A) |
| **Market Manipulation & Insider Trading (Corporations Act)** | Ch. 7, Part 7.10 | Act | https://www.legislation.gov.au/Series/C2001A00067 | P1 | Market manipulation; insider trading (§1043K-1043L) |

### 10D.5 Germany Criminal Law (5 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Strafgesetzbuch (StGB - Criminal Code) §263 (Fraud)** | § 263 | Criminal Code | https://www.gesetze-im-internet.de/stgb/index.html | **P0** | Fraud; deception; damage to victim property/rights |
| **StGB §264 (Subsidy Fraud)** | § 264 | Criminal Code | https://www.gesetze-im-internet.de/stgb/index.html | P1 | Subsidy fraud; falsification of facts |
| **StGB §263a (Fraud via Automated Data Processing)** | § 263a | Criminal Code | https://www.gesetze-im-internet.de/stgb/index.html | P1 | Data processing fraud; electronic contracts |
| **StGB §269-271 (Forgery)** | § 269-271 | Criminal Code | https://www.gesetze-im-internet.de/stgb/index.html | P1 | Falsification of documents; signatures; contracts |
| **Geldwäschegesetz (GwG - Money Laundering Act)** | GwG | Act | https://www.gesetze-im-internet.de/gwg/ | P1 | Money laundering reporting; proceeds concealment |

### 10D.6 France Criminal Law (4 sources - FRENCH)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Code Pénal - Articles 313-317 (Fraud)** | Code Pénal | Criminal Code | https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006070719/ | **P0** | Fraud (Article 313-1); embezzlement; dishonest appropriation (FR) |
| **Code Pénal - Article 405 (False Documentation)** | Article 405 | Code Section | https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006070719/ | P1 | Falsification of documents; official documents (FR) |
| **Code Pénal - Articles 435-437 (Corruption)** | Articles 435-437 | Code Sections | https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006070719/ | **P0** | Bribery; corruption of public officials (FR) |
| **Loi Sapin II (Anti-Corruption Law 2016)** | Loi 2016-1691 | Act | https://www.legifrance.gouv.fr/loda/id/JORFTEXT000033558528 | P1 | Corporate anti-corruption; whistleblower protections (FR) |

### 10D.7 European Union Criminal Law (3 sources)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Directive on the Fight Against Fraud (PIF Directive)** | 2017/1371/EU | Directive | https://eur-lex.europa.eu/eli/dir/2017/1371/oj/eng | **P0** | Protection of financial interests; fraud against EU budget |
| **Directive on Anti-Money Laundering (AMLD5)** | 2018/843/EU | Directive | https://eur-lex.europa.eu/eli/dir/2018/843/oj/eng | **P0** | Money laundering; beneficial ownership transparency; cross-border reporting |
| **Directive on Criminal Penalties for Insider Trading** | 2014/57/EU | Directive | https://eur-lex.europa.eu/eli/dir/2014/57/oj/eng | P1 | Market abuse; insider trading; criminal sanctions harmonization |

### 10D.8 Quebec Criminal Law (2 sources - FRENCH)

| Document | Citation | Type | URL | Priority | Notes |
|----------|----------|------|-----|----------|-------|
| **Code criminel du Canada (French Version)** | Criminal Code | Federal Statute | https://laws-lois.justice.gc.ca/fra/acts/C-46/index.html | **P0** | Federal Criminal Code applied in Quebec courts (FR) |
| **Code de procédure pénale du Québec** | CCP | Act | https://legisquebec.gouv.qc.ca/fr/ShowDoc/cs/C-25.1 | P1 | Quebec criminal procedure; trial and evidence rules (FR) |

---

## 10F. QUEBEC COMPREHENSIVE LEGAL FRAMEWORK (65+ SOURCES - BILINGUAL)

### Quebec Overview
Quebec operates under a **civil law system** (distinct from common law in English-speaking Canada), with a unique legal framework based on the **Code Civil du Québec (CCQ)**. All sources are bilingual French/English. Primary portal: **LégisQuébec** (https://www.legisquebec.gouv.qc.ca/).

### 10F.1 Quebec Employment/Labor Law (6 sources - FR/EN)

| Legal Vertical | Document (French/English) | Type | CQLR Reference | URL | Priority | Notes |
|---|---|---|---|---|---|---|
| **Employment** | Loi sur les normes du travail / Act respecting labour standards | Statute | c N-1.1 | https://www.legisquebec.gouv.qc.ca/en/document/cs/n-1.1 | **P0** | Minimum employment standards; wages, holidays, leaves, termination notice; enforced by CNESST (FR/EN) |
| **Employment** | Code du travail du Québec / Labour Code | Statute | c C-27 | https://www.canlii.org/en/qc/laws/stat/cqlr-c-c-27/latest/cqlr-c-c-27.html | **P0** | Collective bargaining framework; applies to most employees outside construction and public sector (FR/EN) |
| **Employment** | Loi sur les accidents du travail / Act respecting industrial accidents and occupational diseases | Statute | c A-3.001 | https://www.legisquebec.gouv.qc.ca/ | **P0** | Workers' compensation regime (LATMP 1985); income replacement and rehabilitation (FR/EN) |
| **Employment** | Loi sur la santé et sécurité du travail / Act respecting occupational health and safety | Statute | c S-2.1 | https://www.legisquebec.gouv.qc.ca/ | **P0** | Workplace prevention and safety requirements (LSST 1979) (FR/EN) |
| **Employment** | Loi sur l'équité salariale / Pay Equity Act | Statute | c E-12.001 | https://www.canlii.org/en/qc/laws/stat/cqlr-c-e-12.001/latest/cqlr-c-e-12.001.html | P1 | Pay equity between predominantly female and male jobs; 10+ employees; CNESST administered (FR/EN) |
| **Employment** | Charte des droits et libertés / Charter of Human Rights and Freedoms | Statute | c C-12 | https://www.legisquebec.gouv.qc.ca/en/document/cs/c-12 | **P0** | 14 protected grounds for employment discrimination (race, colour, sex, age, disability, sexual orientation, etc.) (FR/EN) |

### 10F.2 Quebec Intellectual Property (4 sources - FR/EN)

| Legal Vertical | Document (French/English) | Type | CQLR Reference | URL | Priority | Notes |
|---|---|---|---|---|---|---|
| **IP** | Code Civil du Québec, Book IV / Civil Code of Québec, Book IV (Property) | Statute | c CCQ-1991 | https://www.legisquebec.gouv.qc.ca/en/document/cs/ccq-1991 | P1 | Property rights framework; allows hypothecation of patents and trademarks (FR/EN) |
| **IP** | Code Civil du Québec, Book V / Civil Code of Québec, Book V (Obligations) | Statute | c CCQ-1991 | https://www.legisquebec.gouv.qc.ca/en/document/cs/ccq-1991 | P1 | Contracts and obligations framework; applies to IP licensing agreements (FR/EN) |
| **IP** | Copyright Act (Federal) / Loi sur le droit d'auteur | Federal Statute | R.S.C., 1985, c C-42 | https://laws-lois.justice.gc.ca/eng/acts/c-42/ | **P0** | Federal jurisdiction; copyright, patents, trademarks; Quebec courts interpret federal IP law (FR/EN) |
| **IP** | Annotated Civil Code of Québec | Reference | - | https://ccq.lexum.com/w/ccq/en | P2 | Scholarly annotations and case law interpretation of Quebec civil law (FR/EN) |

### 10F.3 Quebec Tax Law (6 sources - FR/EN)

| Legal Vertical | Document (French/English) | Type | CQLR Reference | URL | Priority | Notes |
|---|---|---|---|---|---|---|
| **Tax** | Loi sur les impôts / Taxation Act (Quebec income tax) | Statute | c I-3 | https://legisquebec.gouv.qc.ca/fr/document/lc/I-3 | **P0** | Provincial income tax regime; administered by Revenu Québec (FR/EN) |
| **Tax** | Regulation respecting the Taxation Act | Regulation | c I-3, r 1 | https://www.legisquebec.gouv.qc.ca/en/document/cr/i-3,%20r.%201 | P1 | Implementation regulations for income tax (FR/EN) |
| **Tax** | Loi sur la taxe de vente du Québec / Act respecting the Québec sales tax (QST) | Statute | c T-0.1 | https://www.legisquebec.gouv.qc.ca/en/document/cs/T-0.1 | **P0** | 9.975% sales tax; administered by Revenu Québec (FR/EN) |
| **Tax** | Loi sur l'administration fiscale / Tax Administration Act | Statute | c A-6.002 | https://www.canlii.org/fr/qc/legis/lois/rlrq-c-a-6.002/derniere/rlrq-c-a-6.002.html | P1 | Tax administration, assessment, objections, collection procedures (FR/EN) |
| **Tax** | Loi concernant l'impôt sur le tabac / Tobacco Tax Act | Statute | c I-2 | https://www.legisquebec.gouv.qc.ca/en/document/cs/i-2 | P2 | Excise tax on tobacco; $39.80/carton (as of Jan 2025) (FR/EN) |
| **Tax** | Revenu Québec Portal | Portal | - | https://www.revenuquebec.ca/en/about-us/administrative-and-tax-documents/laws-and-regulations-administered-by-revenu-quebec/ | P1 | Comprehensive listing of all tax-related statutes and regulations (FR/EN) |

### 10F.4 Quebec Property Law (7 sources - FR/EN)

| Legal Vertical | Document (French/English) | Type | CQLR Reference | URL | Priority | Notes |
|---|---|---|---|---|---|---|
| **Property** | Code Civil, Book IV / Civil Code, Book IV (Property) | Statute | c CCQ-1991 | https://www.legisquebec.gouv.qc.ca/en/tdm/cs/ccq-1991?mode=detail | **P0** | Real property, moveable property, ownership, possession, rights in property (FR/EN) |
| **Property** | Code Civil, Book V / Civil Code, Book V (Obligations) | Statute | c CCQ-1991 | https://www.legisquebec.gouv.qc.ca/en/document/cs/ccq-1991 | **P0** | Contracts, lease obligations, sales, obligations in general (FR/EN) |
| **Property** | Loi sur les bureaux de la publicité / Law on Registry Offices | Statute | c B-9 | https://www.canlii.org/fr/qc/legis/lois/rlrq-c-b-9/derniere/rlrq-c-b-9.html | **P0** | Land registry system governance; registration of real property rights (FR/EN) |
| **Property** | Règlement sur la publicité foncière / Regulation on Land Publication | Regulation | c CCQ, r 6 | https://www.canlii.org/t/1f85 | **P0** | Technical land registration rules and procedures (FR/EN) |
| **Property** | Loi visant à moderniser certaines règles / Law modernizing land publication rules | Statute | LQ 2020, c 17 | https://www.canlii.org/fr/qc/legis/loisa/lq-2020-c-17/derniere/lq-2020-c-17.html | P1 | 2020 modernization; electronic transmission mandatory (effective Nov 8, 2021) (FR/EN) |
| **Property** | Tarif des droits / Fee schedule for land publication | Regulation | c B-9, r 1 | https://www.canlii.org/fr/qc/legis/regl/rrq-c-b-9-r-1/derniere/rrq-c-b-9-r-1.html | P2 | Registration fees for land registry (FR/EN) |
| **Property** | Code Civil Articles 1851-2000.1 / Lease Framework | Civil Code Sections | c CCQ-1991 | https://www.legisquebec.gouv.qc.ca/fr/document/cc | **P0** | Residential/commercial lease framework; tenant rights; landlord obligations (FR/EN) |

### 10F.5 Quebec Accounting & Business Law (7 sources - FR/EN)

| Legal Vertical | Document (French/English) | Type | CQLR Reference | URL | Priority | Notes |
|---|---|---|---|---|---|---|
| **Business** | Loi sur les compagnies / Companies Act | Statute | c C-38 | https://www.legisquebec.gouv.qc.ca/en/document/cs/c-38 | **P0** | Corporate governance; Part I applies to traditional Quebec companies (FR/EN) |
| **Business** | Loi sur les sociétés par actions / Business Corporations Act | Statute | c S-31.1 | https://www.canlii.org/en/qc/laws/stat/cqlr-c-s-31.1/latest/cqlr-c-s-31.1.html | **P0** | Modern business corporation framework; replaces parts of Companies Act (FR/EN) |
| **Business** | Loi sur la publicité légale / Act respecting the legal publicity of enterprises | Statute | c P-44.1 | https://www.legisquebec.gouv.qc.ca/en/document/cs/p-44.1 | **P0** | Enterprise register (REQ); registration requirements for most businesses (FR/EN) |
| **Business** | Code des professions / Professional Code | Statute | c C-26 | https://www.legisquebec.gouv.qc.ca/en/document/cs/c-26 | P1 | Regulation of 46 professional orders; public protection through professional regulation (FR/EN) |
| **Business** | Loi sur les CPA / Chartered Professional Accountants Act | Statute | c C-48.1 | https://www.canlii.org/en/qc/laws/stat/cqlr-c-c-48.1/latest/cqlr-c-c-48.1.html | P1 | CPA regulation; ethics, licensing, continuing education (FR/EN) |
| **Business** | Code d'éthique des CPA / Code of ethics of chartered professional accountants | Regulation | c C-48.1, r 6 | https://www.legisquebec.gouv.qc.ca/en/document/cr/C-48.1,%20r.%206 | P2 | Professional ethics requirements for CPAs (FR/EN) |
| **Business** | Loi sur les sociétés d'investissement / Act respecting Québec business investment companies | Statute | c S-29.1 | https://www.canlii.org/en/qc/laws/stat/cqlr-c-s-29.1/latest/cqlr-c-s-29.1.html | P2 | Investment company formation and governance (FR/EN) |

### 10F.6 Quebec Construction (7 sources - FR/EN)

| Legal Vertical | Document (French/English) | Type | CQLR Reference | URL | Priority | Notes |
|---|---|---|---|---|---|---|
| **Construction** | Code Civil du Québec - Contract for Enterprise (Articles 2098-2129) | Civil Code Sections | c CCQ-1991 | https://www.legisquebec.gouv.qc.ca/en/version/cs/CCQ-1991?code=se:2098&history=20231009 | **P0** | Construction contracts; 1-year poor workmanship warranty; 5-year structural warranty (FR/EN) |
| **Construction** | Loi sur le bâtiment / Building Act | Statute | c B-1.1 | https://www.canlii.org/fr/qc/legis/lois/rlrq-c-b-1.1/derniere/rlrq-c-b-1.1.html | **P0** | Establishes Régie du bâtiment du Québec (RBQ); contractor licensing and quality control (FR/EN) |
| **Construction** | Code de construction du Québec (2015) | Regulation | c B-1.1, r 2 | https://www.canlii.org/t/cjsn | **P0** | Technical building standards; 2015 edition with amendments through April 17, 2025 (FR/EN) |
| **Construction** | Loi R-20 / Act respecting labour relations in the construction industry | Statute | c R-20 | https://www.canlii.org/fr/qc/legis/lois/lrq-c-r-20/derniere/lrq-c-r-20.html | **P0** | Construction-specific labour relations; four sectors for collective bargaining; CCQ administered (FR/EN) |
| **Construction** | Regulation under Act R-20 | Regulation | c R-20, r 1 | https://www.canlii.org/fr/qc/legis/regl/rlrq-c-r-20-r-1/derniere/rlrq-c-r-20-r-1.html | P1 | Implementation regulations for construction labour relations (FR/EN) |
| **Construction** | RBQ Portal | Portal | - | https://www.rbq.gouv.qc.ca/en/laws-regulations-and-codes/construction-code-and-safety-code/construction-code/ | P1 | Official RBQ portal for construction codes and regulations (FR/EN) |
| **Construction** | CCQ Portal | Portal | - | https://www.ccq.org/en/loi-r20/relations-travail | P1 | Official CCQ portal for construction labour relations and R-20 compliance (FR/EN) |

### 10F.7 Quebec Administrative Tribunals & Dispute Resolution (5 sources - FR/EN)

| Legal Vertical | Document (French/English) | Type | CQLR Reference | URL | Priority | Notes |
|---|---|---|---|---|---|---|
| **Dispute Resolution** | Loi instituant le TAT / Act to establish the Administrative Labour Tribunal | Statute | c T-15.1 | https://www.canlii.org/en/qc/laws/stat/cqlr-c-t-15.1/latest/cqlr-c-t-15.1.html | **P0** | TAT jurisdiction: labour relations, essential services, health/safety, construction disputes (FR/EN) |
| **Dispute Resolution** | Règles de preuve du TAT / Rules of evidence and procedure of TAT | Regulation | c T-15.1, r 1.1 | https://www.canlii.org/en/qc/laws/regu/cqlr-c-t-15.1-r-1.1/latest/cqlr-c-t-15.1-r-1.1.html | P1 | TAT procedural rules for labour disputes (FR/EN) |
| **Dispute Resolution** | Tribunal administratif du logement / TAL Portal | Portal | c R-8.1 | https://www.tal.gouv.qc.ca/en/being-a-lessor/rights-and-obligations-of-the-lessor | **P0** | Quasi-judicial tribunal for residential tenancy disputes (FR/EN) |
| **Dispute Resolution** | Tribunal des droits de la personne / Human Rights Tribunal | Portal | c C-12 | https://tribunaldesdroitsdelapersonne.ca/en/ | P1 | Jurisdiction over discrimination complaints under the Charter (FR/EN) |
| **Dispute Resolution** | CNESST Portal / Multi-function labour agency | Agency Portal | Multiple statutes | https://www.cnesst.gouv.qc.ca/en/ | **P0** | Employment, pay equity, and workplace safety laws (FR/EN) |

---

## 11. CONTRACT DATASETS (Pre-Labeled)

### 10.1 Primary Training Data

| Dataset | Description | Size | Source | Priority |
|---------|-------------|------|--------|----------|
| **CUAD** | 13K+ labeled clause annotations, 510 contracts, 41 clause types | ~500MB | https://www.atticusprojectai.org/cuad | **P0** |
| **ContractNLI** | Natural language inference for contracts | ~50MB | Stanford NLP | **P0** |
| **LEDGAR** | SEC filing provisions, corporate baseline | ~200MB | HuggingFace | **P0** |

### 10.2 CUAD Clause Types (41 Total)

**Critical for Freelancers (Import First):**
- Governing Law
- Non-Compete
- Exclusivity
- IP Ownership Assignment
- License Grant
- Non-Disparagement
- Termination For Convenience
- Limitation Of Liability
- Indemnification
- Insurance
- Cap On Liability
- Uncapped Liability
- Warranty Duration
- Post-Termination Services

---

## 11. LANDMARK CASE LAW

### 11.1 Non-Compete Cases

| Case | Citation | Jurisdiction | Year | Key Test | Priority |
|------|----------|--------------|------|----------|----------|
| **PepsiCo v. Redmond** | 54 F.3d 1262 | 7th Cir. | 1995 | Inevitable disclosure | **P0** |
| **Mitchell v. Reynolds** | Common Law | England | 1711 | Reasonableness framework | **P0** |
| **Oregon Steam v. Winsor** | 87 U.S. 564 | SCOTUS | 1874 | Ancillary to sale | P1 |
| **Ryan v. FTC** | 5th Cir. 2024 | 5th Cir. | 2024 | FTC authority limits | P1 |

### 11.2 IP / Work-for-Hire Cases

| Case | Citation | Jurisdiction | Year | Key Test | Priority |
|------|----------|--------------|------|----------|----------|
| **CCNV v. Reid** | 490 U.S. 730 | SCOTUS | 1989 | 12-factor agency test | **P0** |
| **Dubilier Condenser** | 289 U.S. 178 | SCOTUS | 1933 | Hired-to-invent doctrine | P1 |
| **SCA Hygiene v. First Quality** | 580 U.S. 557 | SCOTUS | 2017 | Patent damages limits | P2 |

### 11.3 Indemnification Cases

| Case | Citation | Jurisdiction | Year | Key Test | Priority |
|------|----------|--------------|------|----------|----------|
| **Brooks v. Judlau** | 11 NY3d 204 | NY | 2008 | Comparative negligence | **P0** |
| **Santa Barbara v. Superior Court** | 41 Cal.4th 747 | CA | 2007 | Gross negligence exception | **P0** |
| **Steamfitters v. Erie Insurance** | 233 A.3d 59 | MD | 2020 | Clear/unequivocal standard | P1 |

### 11.4 Arbitration Cases

| Case | Citation | Jurisdiction | Year | Key Test | Priority |
|------|----------|--------------|------|----------|----------|
| **Epic Systems v. Lewis** | 584 U.S. ___ | SCOTUS | 2018 | FAA enforcement | **P0** |
| **Mastrobuono v. Shearson** | 514 U.S. 52 | SCOTUS | 1995 | Choice-of-law vs arbitration | **P0** |
| **Pinnacle v. Pinnacle Market** | 55 Cal.4th 223 | CA | 2012 | Unconscionability 2-prong | **P0** |

### 11.5 Trade Secrets / NDA Cases

| Case | Citation | Jurisdiction | Year | Key Test | Priority |
|------|----------|--------------|------|----------|----------|
| **Silicon Image v. Analogk** | N.D. Cal. | N.D. Cal. | 2008 | NDA expiration effects | P1 |
| **Hamilton v. Juul Labs** | N.D. Cal. | N.D. Cal. | 2021 | Overbreadth analysis | P1 |
| **Gordon v. Landau** | 49 Cal.2d 212 | CA | 1958 | CA §16600 trade secret exception | P1 |

### 11.6 Moral Rights Cases

| Case | Citation | Jurisdiction | Year | Key Test | Priority |
|------|----------|--------------|------|----------|----------|
| **Gilliam v. ABC** | 538 F.2d 14 | 2d Cir. | 1976 | Integrity/mutilation test | **P0** |
| **Frisby v. BBC** | UK Court | UK | - | Contractual moral rights | P1 |
| **Confetti Records v. Warner** | UK Court | UK | - | CDPA 1988 requirements | P1 |

---

## 12. INDUSTRY STANDARDS

### 12.1 Gaming Industry

| Standard | Organization | URL | Priority |
|----------|--------------|-----|----------|
| **Steam Distribution Agreement** | Valve | https://store.steampowered.com | **P0** |
| **Epic Games Store Agreement** | Epic | https://dev.epicgames.com/docs/epic-games-store/agreements | **P0** |
| **PlayStation GDPA** | Sony | SEC Filings | P1 |
| **Xbox Publisher License** | Microsoft | SEC Filings | P1 |
| **IGDA Contract Walk-Through** | IGDA | https://igda.org/resourcelibrary/game-industry-standards/ | **P0** |
| **IGDA Crediting Guidelines** | IGDA | https://igda.org/ | P1 |

### 12.2 Entertainment

| Standard | Organization | URL | Priority |
|----------|--------------|-----|----------|
| **SAG-AFTRA 2025 Commercials** | SAG-AFTRA | https://www.sagaftra.org/ | **P0** |
| **SAG-AFTRA Video Game Agreement** | SAG-AFTRA | https://www.sagaftra.org/production-center/contract/802/ | **P0** |
| **WGA Minimum Basic Agreement** | WGA | https://www.wga.org/contracts/contracts/schedule-of-minimums | **P0** |

### 12.3 Creative Services

| Standard | Organization | URL | Priority |
|----------|--------------|-----|----------|
| **AIGA Standard Agreement** | AIGA | https://www.aiga.org/resources/aiga-standard-form-of-agreement-for-design-services | **P0** |
| **GAG Handbook (17th Ed)** | Graphic Artists Guild | https://graphicartistsguild.org/ | **P0** |
| **Photography Licensing Standards** | Various | https://www.pixsy.com/image-licensing/photo-licensing-agreement | P1 |

### 12.4 Tech/Software

| Standard | Organization | URL | Priority |
|----------|--------------|-----|----------|
| **Open Source Licenses** | OSI | https://opensource.org/licenses | P1 |
| **MIT License** | OSI | https://opensource.org/license/mit | P1 |
| **Apache 2.0** | Apache | https://www.apache.org/licenses/LICENSE-2.0 | P1 |
| **GPL v3** | GNU | https://www.gnu.org/licenses/gpl-3.0.en.html | P1 |

---

## 13. DOWNLOAD SCRIPTS REFERENCE

All download scripts are in: `/home/setup/CLOUD_SESSION_LEGAL_DB_BUILD.md`

### Script Mapping

| Script | Data Source | Output Directory |
|--------|-------------|------------------|
| `download_cuad.py` | CUAD Dataset | `raw/cuad/` |
| `download_us_federal.py` | GovInfo API | `raw/us_federal/` |
| `download_us_caselaw.py` | CourtListener | `raw/us_caselaw/` |
| `download_eu_law.py` | EUR-Lex SPARQL | `raw/eu_law/` |
| `download_canada_law.py` | CanLII | `raw/canada_law/` |
| `download_australia_law.py` | AustLII | `raw/australia_law/` |

### Execution Order

```bash
# Phase 1: Datasets (Highest Value)
python scripts/download_cuad.py

# Phase 2: US Federal
export GOVINFO_API_KEY="your_key"
python scripts/download_us_federal.py
python scripts/download_us_caselaw.py

# Phase 3: International
python scripts/download_eu_law.py
python scripts/download_canada_law.py
python scripts/download_australia_law.py

# Phase 4: Process & Index
python scripts/process_cuad.py
python scripts/process_documents.py
python scripts/embed_and_index.py
```

---

## Chroma Collection Structure

After import, Chroma will have these collections:

```
chroma_db/
├── contract_clauses      # CUAD labeled clauses (P0)
├── us_federal_law        # USC, CFR (P0)
├── us_state_law          # CA, NY, TX, etc. (P0)
├── us_case_law           # CourtListener opinions (P1)
├── eu_directives         # EUR-Lex (P0)
├── eu_regulations        # GDPR, AI Act, DSA (P0)
├── germany_bgb           # Civil Code (P0)
├── france_code           # Labor, IP codes (P1)
├── canada_federal        # Copyright, PIPEDA (P0)
├── canada_provincial     # ON, BC, QC employment (P0)
├── australia_federal     # Fair Work, Copyright (P0)
├── uk_legislation        # ERA, CDPA, IR35 (P0)
└── industry_standards    # AIGA, GAG, IGDA (P1)
```

---

## Estimated Totals

| Metric | Value |
|--------|-------|
| **Total Documents** | ~123 sources |
| **Total Raw Size** | ~780MB |
| **Processed Chunks** | ~500K vectors |
| **Chroma DB Size** | ~1-2GB |
| **P0 Documents** | 58 (must have) |
| **Download Time** | 4-6 hours |
| **Processing Time** | 2-3 hours |
| **Embedding Time** | 1-2 hours (CPU) |

---

## Next Steps

1. Execute `CLOUD_SESSION_LEGAL_DB_BUILD.md` to download and index
2. Validate with test queries
3. Build contract analysis prompts using RAG
4. Integrate with upload pipeline

---

*Generated by IF.optimise Haiku swarm research*
*6 parallel agents, ~15 minutes total research time*
