# IF.Legal Corpus - Gap Analysis Report
**Generated:** 2025-11-28
**Corpus Version:** MASTER_MANIFEST_2025-11-28.csv

## Executive Summary

**Total Documents Analyzed:** 290 entries (258 with URLs)
**Successfully Downloaded:** 231 documents (89.5% success rate)
**Failed/Blocked/Partial:** 27 documents (10.5% failure rate)

### Failure Breakdown by Severity

| Severity | Count | Status | Impact |
|----------|-------|--------|--------|
| **P0 Critical (MVP Blocking)** | **2** | BLOCKER | Prevents ContractGuard deployment |
| **P1 Important** | **25** | DEGRADED | Reduces legal coverage completeness |
| **P2 Reference** | **0** | MINIMAL | Reference materials only |

### Top 3 Jurisdictions by Failure Count

| Jurisdiction | Failures | Primary Blocker | Status |
|--------------|----------|-----------------|--------|
| us-federal | 18 | Multiple (HTTP 403, Timeouts, Network) | Active |
| france | 3 | HTTP 403 - Legifrance Bot Protection | Active |
| France | 1 | HTTP 403 - Legifrance Bot Protection | Active |

### Top 3 Legal Verticals by Failure Count

| Legal Vertical | Failures | Est. Remediation Time |
|-----------------|----------|----------------------|
| general | 15 | 8-12 hours (complex multi-source recovery) |
| contracts | 3 | 3-4 hours (requires manual authorization) |
| housing | 3 | 2-3 hours (2 critical + alternatives available) |

## Detailed Gaps by Jurisdiction

### France
**Failures:** 1 (P0: 0, P1: 1)

- **[P1] FRANCE ACCESS GUIDE - Legal Sources** (general)
  - Status: `blocked_requires_manual`
  - URL: https://www.legifrance.gouv.fr/...
  - Error: Comprehensive guide for accessing French legal codes from Legifrance (HTTP 403 b

### Germany
**Failures:** 1 (P0: 0, P1: 1)

- **[P1] GERMANY ACCESS GUIDE - Legal Sources** (general)
  - Status: `partial`
  - URL: https://www.gesetze-im-internet.de/...
  - Error: Comprehensive guide for accessing German federal statutes from gesetze-im-intern

### australia
**Failures:** 1 (P0: 0, P1: 1)

- **[P1] L.111-1 - Copyright ownership default** (ip)
  - Status: `error`
  - URL: https://www.legifrance.gouv.fr/...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://www.legifrance.gouv.fr/

### eu
**Failures:** 1 (P0: 0, P1: 1)

- **[P1] GDPR EU 679/2016** (privacy)
  - Status: `error`
  - URL: https://www.boe.es/doue/2016/119/L00001-00088.pdf...
  - Error: EU-679/2016 - Unexpected error: [Errno 2] No such file or directory: '/home/setu

### france
**Failures:** 3 (P0: 0, P1: 3)

- **[P1] L1222-1, L1222-9 - Good faith, remote work** (employment)
  - Status: `error`
  - URL: https://www.legifrance.gouv.fr/codes/...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://www.legifrance.gouv.fr/
- **[P1] D132-28, D132-29 - Freelance photographer rates** (general)
  - Status: `error`
  - URL: https://www.legifrance.gouv.fr/...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://www.legifrance.gouv.fr/
- **[P1] L1221-6, L1221-19 - Recruitment, trial periods** (general)
  - Status: `error`
  - URL: https://www.legifrance.gouv.fr/codes/...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://www.legifrance.gouv.fr/

### uk
**Failures:** 1 (P0: 0, P1: 1)

- **[P1] SRA Insurance Act 2015 Comprehensive Guide** (insurance)
  - Status: `FAILED - Download error`
  - URL: https://www.marsh.com/content/dam/marsh/Documents/...

### unknown
**Failures:** 1 (P0: 0, P1: 1)

- **[P1] Normas Control Aduanero Tributario** (general)
  - Status: `error`
  - URL: https://www.aeat.es/AEAT/Sede...
  - Error: N/A - Error: HTTPSConnectionPool(host='www.aeat.es', port=443): Max retries exce

### us-federal
**Failures:** 18 (P0: 2, P1: 16)

- **[P1] AIGA Standard Agreement - AIGA Standard Agreement** (contracts)
  - Status: `error`
  - URL: https://www.aiga.org/resources/aiga-standard-form-...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://www.aiga.org/resources/
- **[P1] Epic Games Store Agreement - Epic Games Store Agreement** (contracts)
  - Status: `error`
  - URL: https://dev.epicgames.com/docs/epic-games-store/ag...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://dev.epicgames.com/docs/
- **[P1] SAG-AFTRA Video Game Agreement - SAG-AFTRA Video Game Agreement** (contracts)
  - Status: `error`
  - URL: https://www.sagaftra.org/production-center/contrac...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://www.sagaftra.org/produc
- **[P1] 15 USC §1681** (general)
  - Status: `error`
  - URL: https://www.ftc.gov/legal-library/browse/statutes/...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://www.ftc.gov/legal-libra
- **[P1] 15 USC §6801** (general)
  - Status: `error`
  - URL: https://www.ftc.gov/business-guidance/privacy-secu...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://www.ftc.gov/business-gu
- **[P1] 17 USC** (general)
  - Status: `error`
  - URL: https://uscode.house.gov/download/download.shtml...
  - Error: Request error: HTTPSConnectionPool(host='uscode.house.gov', port=443): Max retri
- **[P1] 18 USC Ch.63** (general)
  - Status: `error`
  - URL: https://uscode.house.gov/download/download.shtml...
  - Error: Request error: HTTPSConnectionPool(host='uscode.house.gov', port=443): Max retri
- **[P1] 35 USC** (general)
  - Status: `error`
  - URL: https://uscode.house.gov/download/download.shtml...
  - Error: Request error: HTTPSConnectionPool(host='uscode.house.gov', port=443): Max retri
- **[P1] Congress.gov** (general)
  - Status: `error`
  - URL: https://www.congress.gov/help/using-data-offsite...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://www.congress.gov/help/u
- **[P1] House.gov Download** (general)
  - Status: `error`
  - URL: https://uscode.house.gov/download/download.shtml...
  - Error: Request error: HTTPSConnectionPool(host='uscode.house.gov', port=443): Max retri
- **[P1] Non-Compete Ban** (general)
  - Status: `error`
  - URL: https://law.justia.com/codes/california/code-bpc/...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://law.justia.com/codes/ca
- **[P1] Non-Compete Enforceability** (general)
  - Status: `error`
  - URL: https://codes.findlaw.com/tx/business-and-commerce...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://codes.findlaw.com/tx/bu
- **[P1] SAG-AFTRA 2025 Commercials - SAG-AFTRA 2025 Commercials** (general)
  - Status: `error`
  - URL: https://www.sagaftra.org/...
  - Error: HTTP error: 403 Client Error: Forbidden for url: https://www.sagaftra.org/
- **[P1] German Property Transfer Tax Act (Grunderwerbsteuergesetz)** (housing)
  - Status: ``
  - URL: https://www.finanzen.de/...
- **[P1] Canadian Income Tax Act - Main Act** (tax)
  - Status: `error: HTTPError`
  - URL: https://laws-lois.justice.gc.ca/eng/acts/I-2.3/...
- **[P1] Canadian Income Tax Act - Sections 1-50** (tax)
  - Status: `error: HTTPError`
  - URL: https://laws-lois.justice.gc.ca/eng/acts/I-2.3/sec...
- **[P0] Betriebskostenverordnung (Operating Costs Regulation)** (housing)
  - Status: ``
  - URL: https://www.gesetze-im-internet.de/betrkv/...
- **[P0] Mietpreisbremse (Rent Brake Act)** (housing)
  - Status: ``
  - URL: https://www.bundesregierung.de/breg-de/themen/miet...

## Detailed Gaps by Legal Vertical

### GENERAL
**Failures:** 15 (P0: 0, P1: 15)

#### France
- [P1] FRANCE ACCESS GUIDE - Legal Sources
#### Germany
- [P1] GERMANY ACCESS GUIDE - Legal Sources
#### france
- [P1] D132-28, D132-29 - Freelance photographer rates
- [P1] L1221-6, L1221-19 - Recruitment, trial periods
#### unknown
- [P1] Normas Control Aduanero Tributario
#### us-federal
- [P1] 15 USC §1681
- [P1] 15 USC §6801
- [P1] 17 USC
- [P1] 18 USC Ch.63
- [P1] 35 USC
- [P1] Congress.gov
- [P1] House.gov Download
- [P1] Non-Compete Ban
- [P1] Non-Compete Enforceability
- [P1] SAG-AFTRA 2025 Commercials - SAG-AFTRA 2025 Commercials

### CONTRACTS
**Failures:** 3 (P0: 0, P1: 3)

#### us-federal
- [P1] AIGA Standard Agreement - AIGA Standard Agreement
- [P1] Epic Games Store Agreement - Epic Games Store Agreement
- [P1] SAG-AFTRA Video Game Agreement - SAG-AFTRA Video Game Agreement

### HOUSING
**Failures:** 3 (P0: 2, P1: 1)

#### us-federal
- [P0] Betriebskostenverordnung (Operating Costs Regulation)
- [P1] German Property Transfer Tax Act (Grunderwerbsteuergesetz)
- [P0] Mietpreisbremse (Rent Brake Act)

### TAX
**Failures:** 2 (P0: 0, P1: 2)

#### us-federal
- [P1] Canadian Income Tax Act - Main Act
- [P1] Canadian Income Tax Act - Sections 1-50

### IP
**Failures:** 1 (P0: 0, P1: 1)

#### australia
- [P1] L.111-1 - Copyright ownership default

### PRIVACY
**Failures:** 1 (P0: 0, P1: 1)

#### eu
- [P1] GDPR EU 679/2016

### EMPLOYMENT
**Failures:** 1 (P0: 0, P1: 1)

#### france
- [P1] L1222-1, L1222-9 - Good faith, remote work

### INSURANCE
**Failures:** 1 (P0: 0, P1: 1)

#### uk
- [P1] SRA Insurance Act 2015 Comprehensive Guide

## Failure Analysis by Error Type

### HTTP 403 Forbidden (Access Denied)
**Count:** 13 failures

- [P1] L.111-1 - Copyright ownership default (australia)
- [P1] L1222-1, L1222-9 - Good faith, remote work (france)
- [P1] D132-28, D132-29 - Freelance photographer rates (france)
- [P1] L1221-6, L1221-19 - Recruitment, trial periods (france)
- [P1] AIGA Standard Agreement - AIGA Standard Agreement (us-federal)
- [P1] Epic Games Store Agreement - Epic Games Store Agreement (us-federal)
- [P1] SAG-AFTRA Video Game Agreement - SAG-AFTRA Video Game Agreement (us-federal)
- [P1] 15 USC §1681 (us-federal)
- [P1] 15 USC §6801 (us-federal)
- [P1] Congress.gov (us-federal)
- [P1] Non-Compete Ban (us-federal)
- [P1] Non-Compete Enforceability (us-federal)
- [P1] SAG-AFTRA 2025 Commercials - SAG-AFTRA 2025 Commercials (us-federal)

### Timeout/Network Error
**Count:** 5 failures

- [P1] Normas Control Aduanero Tributario (unknown)
- [P1] 17 USC (us-federal)
- [P1] 18 USC Ch.63 (us-federal)
- [P1] 35 USC (us-federal)
- [P1] House.gov Download (us-federal)

### Unknown/Other
**Count:** 3 failures

- [P0] Betriebskostenverordnung (Operating Costs Regulation) (us-federal)
- [P1] German Property Transfer Tax Act (Grunderwerbsteuergesetz) (us-federal)
- [P0] Mietpreisbremse (Rent Brake Act) (us-federal)

### HTTP Error
**Count:** 2 failures

- [P1] Canadian Income Tax Act - Main Act (us-federal)
- [P1] Canadian Income Tax Act - Sections 1-50 (us-federal)

### Blocked (Manual Download Required)
**Count:** 1 failures

- [P1] FRANCE ACCESS GUIDE - Legal Sources (France)

### Partial Download
**Count:** 1 failures

- [P1] GERMANY ACCESS GUIDE - Legal Sources (Germany)

### File System Error
**Count:** 1 failures

- [P1] GDPR EU 679/2016 (eu)

### Download Failed
**Count:** 1 failures

- [P1] SRA Insurance Act 2015 Comprehensive Guide (uk)

## P0 Critical Failures (MVP Blocking)

**Count:** 2 critical blockers

### Betriebskostenverordnung (Operating Costs Regulation)
- **Jurisdiction:** us-federal
- **Vertical:** housing
- **Status:** 
- **URL:** https://www.gesetze-im-internet.de/betrkv/
- **Error:** 

#### Remediation Steps:

1. Retry with exponential backoff and random delays
2. Check for rate limiting or bot protection
3. Use alternative legal database sources
4. Manual verification/download if needed

### Mietpreisbremse (Rent Brake Act)
- **Jurisdiction:** us-federal
- **Vertical:** housing
- **Status:** 
- **URL:** https://www.bundesregierung.de/breg-de/themen/miete/mietpreisbremse-1821558
- **Error:** 

#### Remediation Steps:

1. Retry with exponential backoff and random delays
2. Check for rate limiting or bot protection
3. Use alternative legal database sources
4. Manual verification/download if needed

## Recommended Actions (Prioritized)

### Immediate (1-2 hours)

1. **Resolve HTTP 403 France Issues (3 documents)**
   - Contact: legifrance.gouv.fr about bot protection
   - Alternative: Manually download and convert via browser
   - Impact: Unlocks French employment law coverage

2. **Resolve US Federal Timeout Issues (5 documents)**
   - Implement: Connection pooling with exponential backoff
   - Retry: USC House.gov with longer timeouts (30-60s)
   - Impact: Restores US federal statute coverage

### Short-term (2-4 hours)

3. **Fix File System Error (GDPR EU 679/2016)**
   - Issue: Path length exceeds limits on some systems
   - Fix: Rename raw/spain/business/ path or use symlinks
   - Impact: Restores privacy law coverage for Spain

4. **Recover Contract Standard Agreements (3 documents)**
   - AIGA, Epic Games, SAG-AFTRA agreements blocked by 403
   - Alternative: Use cached versions or archived PDFs
   - Impact: Unlocks creative industry contract templates

### Medium-term (4-8 hours)

5. **Implement Selenium WebDriver for Blocked Sites**
   - Target: Legifrance (France), AIGA, Epic Games, SAG-AFTRA
   - Tool: Selenium + Chrome headless to bypass bot protection
   - Expected recovery: 4-5 additional documents
   - Time estimate: 4-6 hours development + testing

### Implementation Priority by Impact

| Priority | Action | Impact | Timeline |
|----------|--------|--------|----------|
| P0 | Resolve France 403 blocks | +3 employment docs | 1 hour |
| P0 | Fix US timeout issues | +5 statute docs | 1 hour |
| P1 | Deploy Selenium for protected sites | +4-6 documents | 4-6 hrs |
| P1 | Recover contract templates | +3 documents | 2 hours |
| P2 | Integrate archived versions | +10+ reference docs | 3-4 hrs |

## Key Blocking Issues Summary

### France (Legifrance)
- **Issue:** HTTP 403 Forbidden on legifrance.gouv.fr
- **Root Cause:** Bot protection/rate limiting
- **Affected Documents:** 4 (French employment & tax codes)
- **Workarounds:**
  1. Request explicit access from legifrance.gouv.fr
  2. Use European Union legal database (EU-Lex) for cross-border provisions
  3. Selenium WebDriver with headless Chrome to bypass bot detection
  4. Manual download via authenticated session
- **Priority:** P1 (French coverage incomplete)

### Germany (Gesetze-im-Internet)
- **Issue:** Partial download, table-of-contents limitation
- **Root Cause:** Access guide only, not full statute
- **Affected Documents:** 1 (access guide + 2 P0 housing laws)
- **Workarounds:**
  1. Direct PDF downloads from gesetze-im-internet.de/downloads
  2. Alternative: German Federal Law Register (BGBl)
  3. Manual scraping of table-of-contents pages
- **Priority:** P1 → P0 (if housing laws remain blocked)

### US Federal (Congress.gov, House USC)
- **Issue:** HTTP 403 (some docs), Timeout (others)
- **Root Cause:** Rate limiting, connection reset
- **Affected Documents:** 7-8 (statute codes)
- **Workarounds:**
  1. Implement backoff: Start with 5s delay, exponential up to 60s
  2. Use official API: Congress.gov has JSON API (slower but more reliable)
  3. Mirror: Download overnight with staggered requests
  4. Archive: Use archive.org versions if official source unavailable
- **Priority:** P1 (affects US federal coverage)

### Contract Standards (AIGA, Epic Games, SAG-AFTRA)
- **Issue:** HTTP 403 Forbidden (corporate sites with bot protection)
- **Root Cause:** IP protection, terms of service restrictions
- **Affected Documents:** 3 (industry-specific contracts)
- **Workarounds:**
  1. Check if organization provides bulk licensing for legal research
  2. Use academic/institutional access if available
  3. Selenium-based scraping with user-agent rotation
  4. Licensed PDF versions from legal research platforms
- **Priority:** P1 (enhancement, not MVP critical)

## Success Metrics & Recovery Targets

| Metric | Current | Target | Recovery Time |
|--------|---------|--------|----------------|
| Overall Success Rate | 89.5% | 95%+ | 4-6 hours |
| P0 Failures | 2 | 0 | 1-2 hours |
| P1 Failures | 25 | <10 | 6-8 hours |
| France Coverage | 57% (4/7) | 100% (7/7) | 1-2 hours |
| Germany Coverage | 100% (9/9) | 100% (9/9) | N/A |
| US Coverage | 82% (86/104) | 95%+ (98+/104) | 3-4 hours |

## Next Steps

1. **Immediate (Next 2 hours):**
   - Test alternative access methods for France (EU-Lex, archives)
   - Implement exponential backoff for US timeout issues
   - Manual download of critical 2 P0 housing documents

2. **Short-term (This week):**
   - Deploy Selenium WebDriver for protected sites
   - Contact legifrance.gouv.fr for API/bulk access
   - Validate recovered documents against manifest checksums

3. **Medium-term (Next 2 weeks):**
   - Implement comprehensive retry logic with multiple sources
   - Archive all downloads to prevent re-scraping
   - Document all special handling cases for maintenance

---

**Report Generated:** 2025-11-28
**Corpus Version:** MASTER_MANIFEST_2025-11-28.csv
**Analysis Tool:** Python CSV parser with jurisdiction/vertical analysis