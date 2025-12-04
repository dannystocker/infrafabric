# Generated Test Contracts for ContractGuard

## Overview

**Source:** Google Colab contract generation system  
**Total Contracts:** 1,329 synthetic service agreements  
**Format:** Markdown (.md)  
**Purpose:** Testing ContractGuard's ability to detect abusive/unfair contract clauses  

## Dataset Structure

```
generated/
├── batch_0/    - Initial batch (original zip)
├── batch_1/    - Batch 1 of 10
├── batch_2/    - Batch 2 of 10
├── batch_3/    - Batch 3 of 10
├── batch_4/    - Batch 4 of 10
├── batch_5/    - Batch 5 of 10
├── batch_6/    - Batch 6 of 10
├── batch_7/    - Batch 7 of 10
├── batch_8/    - Batch 8 of 10
├── batch_9/    - Batch 9 of 10
└── batch_10/   - Batch 10 of 10
```

**Total Size:** 9.8 MB  
**Naming Convention:** `Contract_[NN]_[hash].md`

## Contract Types

All contracts are **UK-based freelance service agreements** with variations across:

### Industries Covered
- Technology/Software Development
- Sales & Business Development
- Creative Services (Design, Writing, Marketing)
- Professional Services (Consulting, Legal, Finance)

### Roles Tested
- Software Developers
- Business Development Managers
- Graphic Designers
- Marketing Consultants
- Sales Representatives
- Project Managers

### Classification Labels

Each contract is tagged with one of these classifications:

1. **ABUSIVE TERMS** - Contains deliberately unfair/exploitative clauses
   - Example: Worldwide 24-month non-competes
   - Example: Unpaid overtime requirements
   - Example: Asymmetric termination rights
   - Example: Total IP assignment (including personal work)
   - Example: AI training rights without consent

2. **FAIR TERMS** - Reasonable, balanced contract provisions
   - Standard notice periods (both parties equal)
   - Fair IP assignment (work-related only)
   - Reasonable restrictive covenants
   - Proper remuneration for overtime

3. **AMBIGUOUS TERMS** - Unclear or potentially problematic clauses
   - Vague definitions
   - Undefined scope
   - Missing key provisions

## Abusive Clause Categories Tested

### 1. Intellectual Property Overreach
- **Total Assignment:** All work, ideas, concepts (even unrelated to business)
- **AI Training Rights:** Use of contractor's work/likeness for AI without opt-out
- **Moral Rights Waiver:** Unconditional waiver of all moral rights worldwide

### 2. Asymmetric Termination
- **Company Rights:** Immediate termination without cause or notice
- **Contractor Obligations:** 3-6 month notice period required
- **No Compensation:** No payment in lieu of notice

### 3. Unreasonable Work Expectations
- **Crunch Time Clauses:** Weekends/bank holidays without extra pay
- **Unlimited Hours:** Daily rate covers "all hours worked"
- **Error Deductions:** Employer can deduct costs from invoices unilaterally

### 4. Overly Broad Restrictive Covenants
- **Non-Compete:** 12-24 months, worldwide scope
- **Non-Solicitation:** 3-5 year prohibition on contacting clients/employees
- **Client Lists:** No geographical or temporal limits

### 5. Liability Imbalance
- **Unlimited Indemnity:** Contractor indemnifies all company losses
- **No Company Liability:** Company excluded from all liability
- **Third-Party Claims:** Contractor liable for IP infringement claims

### 6. Payment Terms Issues
- **Extended Payment:** 60-90 day payment terms
- **Arbitrary Deductions:** Unilateral right to withhold payment
- **Currency/Tax Shifts:** Contractor bears all currency/tax risks

## Testing Use Cases

### 1. Clause Detection
Test ContractGuard's ability to identify specific abusive clauses:
```
Input: Contract_02_0469465a.md (ABUSIVE TERMS)
Expected: Flag IP overreach, termination asymmetry, unpaid overtime
```

### 2. Risk Scoring
Compare risk scores between FAIR vs ABUSIVE contracts:
```
FAIR contracts should score: 0-30 (low risk)
ABUSIVE contracts should score: 70-100 (high risk)
AMBIGUOUS contracts should score: 30-70 (medium risk)
```

### 3. Comparative Analysis
Test side-by-side comparison features:
```
Input: 2 contracts from same industry (1 FAIR, 1 ABUSIVE)
Expected: Highlight differences in termination, IP, non-compete clauses
```

### 4. Jurisdiction Testing
All contracts use **UK law** - verify:
- IR35 compliance analysis
- UK-specific clause recognition (e.g., BGB §556d not applicable)
- Proper application of UK Employment Rights Act

### 5. Industry-Specific Analysis
Test across different sectors:
- Tech: IP assignment, AI rights, software licensing
- Creative: Moral rights, portfolio usage, derivative works
- Sales: Commission structures, client ownership, targets
- Consulting: Deliverables, KPIs, termination conditions

## Integration with Legal Corpus

These test contracts should be used **in conjunction with the legal corpus**:

1. **Legal Corpus** (241 documents, 55,778+ vectors)
   - Provides authoritative legal reference
   - UK Employment Rights Act 1996
   - UK IP laws (Copyright, Patents, Trade Secrets)
   - UK case law on restrictive covenants

2. **Test Contracts** (1,329 synthetic agreements)
   - Tests clause detection accuracy
   - Validates risk scoring algorithms
   - Benchmark ContractGuard performance
   - Quality assurance for deployment

## Sample Contract Metadata

```yaml
Contract ID: CN-9696-DTSD
Date: 28 November 2025
Parties:
  Company: Vertex Logic Systems (UK Company No. 69732314)
  Individual: Bryan Wall
Role: Business Development Manager
Industry: Sales
Classification: ABUSIVE TERMS
Abusive Clauses:
  - IP: Total assignment + AI training rights
  - Termination: Asymmetric (6mo vs immediate)
  - Hours: Unpaid overtime/weekends
  - Non-Compete: 24 months worldwide
  - Indemnity: Unlimited contractor liability
```

## Quality Assurance Metrics

Use these contracts to measure:

| Metric | Target | Test Method |
|--------|--------|-------------|
| **Clause Detection Rate** | 95%+ | Count flagged abusive clauses vs ground truth |
| **False Positive Rate** | <5% | Count incorrect flags in FAIR contracts |
| **Risk Score Accuracy** | ±10 points | Compare computed vs expected risk scores |
| **Processing Speed** | <2 sec/contract | Measure analysis time for 100 contracts |
| **Jurisdiction Accuracy** | 100% | Verify UK law applied, not US/EU/other |

## Known Limitations

1. **Synthetic Data:** Generated contracts may not reflect all real-world edge cases
2. **UK-Only:** No multi-jurisdiction testing (all contracts are UK-based)
3. **Binary Classification:** FAIR/ABUSIVE/AMBIGUOUS - no nuance scale
4. **Modern Clauses:** Includes emerging issues (AI rights) not in older legal corpus
5. **No Case History:** Contracts don't have associated court rulings/precedents

## Recommended Test Workflow

1. **Baseline Testing (Day 1)**
   - Run ContractGuard on 10 ABUSIVE contracts
   - Verify clause detection works
   - Establish baseline accuracy

2. **Calibration (Day 2-3)**
   - Test 50 FAIR + 50 ABUSIVE contracts
   - Tune risk scoring algorithms
   - Reduce false positives

3. **Industry Testing (Day 4-5)**
   - Test across all industries (Tech, Sales, Creative, Professional)
   - Verify sector-specific clause recognition
   - Validate legal corpus integration

4. **Performance Testing (Day 6)**
   - Batch process all 1,329 contracts
   - Measure processing speed
   - Identify optimization opportunities

5. **Edge Case Testing (Day 7)**
   - Test AMBIGUOUS contracts
   - Verify graceful handling of unclear clauses
   - Document limitations

## Citation

When using these test contracts in research or reporting:

```
IF.Legal Test Contract Corpus (2025)
Generated: Google Colab synthetic contract generator
Count: 1,329 UK freelance service agreements
Classifications: ABUSIVE, FAIR, AMBIGUOUS
Purpose: ContractGuard quality assurance and validation
Repository: https://github.com/dannystocker/if-legal-corpus
```

---

**Generated:** 2025-11-28  
**Version:** 1.0  
**Status:** Production-ready for ContractGuard testing
