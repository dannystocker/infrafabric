# IF.VocalDNA Extraction Protocol v1.0

**Status:** Production-Ready
**IF.citation:** `if://protocol/vocaldna/v1.0`
**Date:** 2025-12-02
**IF.TTT Compliance:** Mandatory

---

## Executive Summary

The IF.VocalDNA Extraction Protocol is a systematic methodology for converting an individual's communication patterns, reasoning structures, and ethical stances into structured, machine-readable DNA profiles suitable for personality embedding in AI systems.

This protocol synthesizes the best elements from three proven methodologies:
1. **Sergio DNA** - 74 components across ethics, arguments, rhetorical devices
2. **IF.persona.joe** - Archetype-based persona with operating laws and evidence
3. **IF.talent** - 5 evidence types for behavioral pattern recognition

**Core Innovation:** Converting abstract "voice" into falsifiable, observable behavioral patterns with full traceability.

---

## Table of Contents

1. [Methodology Overview](#1-methodology-overview)
2. [The 5-Layer DNA Architecture](#2-the-5-layer-dna-architecture)
3. [Extraction Procedure](#3-extraction-procedure)
4. [Evidence Collection Standards](#4-evidence-collection-standards)
5. [Scoring Methodology](#5-scoring-methodology)
6. [Output Schema](#6-output-schema)
7. [Quality Assurance](#7-quality-assurance)
8. [Copyright Tracking](#8-copyright-tracking)
9. [Voice Blending Protocol](#9-voice-blending-protocol)
10. [IF.TTT Compliance Requirements](#10-ifttt-compliance-requirements)

---

## 1. Methodology Overview

### 1.1 What is VocalDNA?

VocalDNA is the structured representation of an individual's:
- **Rhetorical patterns** - How they persuade, explain, reframe
- **Ethical stances** - What principles guide their decisions
- **Argumentative structures** - How they build logical chains
- **Signature moves** - Distinctive techniques that mark their voice
- **Operating laws** - The constraints they self-impose

### 1.2 Source Methodology Citations

| Methodology | Source | Lines | Key Innovation |
|-------------|--------|-------|----------------|
| Sergio DNA Ethics | `/home/setup/sergio_chatbot/personality_dna_ethics.json` | 156 | Evidence-backed ethical stances with timestamps |
| Sergio DNA Arguments | `/home/setup/sergio_chatbot/personality_dna_arguments.json` | 278 | 11 argumentative structures with templates |
| Sergio DNA Rhetorical | `/home/setup/sergio_chatbot/personality_dna_rhetorical.json` | 358 | 24+ rhetorical devices with distinctiveness scoring |
| IF.persona.joe | `/home/setup/infrafabric/docs/archive/legacy_root/philosophy/IF.persona.joe.json` | 140 | Archetype + core_doctrine + operating_laws schema |
| IF.talent | `/home/setup/infrafabric/docs/archive/legacy_root/examples/vc_talent_intelligence.md` | 200+ | 5 evidence types for behavioral verification |

---

## 2. The 5-Layer DNA Architecture

### Layer 1: Identity Core

```json
{
  "layer": "identity_core",
  "components": {
    "id": "unique_identifier",
    "uri": "if://persona/{id}",
    "aliases": ["list", "of", "names"],
    "archetype": "One-sentence essence (e.g., 'Contrarian value grocer; editor-in-chief of goods')",
    "bloom_pattern": "How they operate at scale",
    "mission": "What drives them fundamentally"
  }
}
```

### Layer 2: Ethical Framework

```json
{
  "layer": "ethical_framework",
  "components": [
    {
      "ethical_stance_id": "unique_id",
      "principle": "Named principle",
      "description": "Full description",
      "evidence": "Transcript/source with timestamp",
      "strength": "core_value | strong | moderate | contextual",
      "conflicts_with": ["list of conflicting principles"],
      "actionable_manifestation": "Observable behavior"
    }
  ]
}
```

**Scoring:** Each stance rated on:
- Evidence quality (1-5)
- Consistency across sources (1-5)
- Distinctiveness from generic values (1-5)

### Layer 3: Argumentative Structures

```json
{
  "layer": "argumentative_structures",
  "components": [
    {
      "structure_id": "unique_id",
      "pattern_type": "Pattern category",
      "template": "Schematic structure",
      "example": "Concrete example from source",
      "direct_quote": "Verbatim quote with source",
      "usage_frequency": "How often deployed",
      "applications": ["context1", "context2"],
      "underlying_mechanism": "Why this works"
    }
  ]
}
```

**Categories:**
- **Reframing patterns** - Converting problem A into solution B
- **Binary reduction** - Collapsing complexity into ON/OFF
- **Systems thinking** - Viewing individuals as interaction patterns
- **Vulnerability oscillation** - Challenge + soften rhythm

### Layer 4: Rhetorical Devices

```json
{
  "layer": "rhetorical_devices",
  "components": [
    {
      "rhetorical_device_id": "unique_id",
      "category": "analogy | operationalization | anti-abstract | narrative | code_switching",
      "text_excerpt": "Verbatim example with context",
      "function": "What this achieves in communication",
      "frequency": "high | medium | sparse",
      "distinctive_score": 1-10,
      "appears_count": "Number of instances in corpus"
    }
  ]
}
```

**Distinctive Score Methodology:**
- Frequency (1-5): How often the device appears
- Uniqueness (1-5): How rare this is in general discourse
- Composite score = Frequency + Uniqueness (max 10)

### Layer 5: Operating Laws

```json
{
  "layer": "operating_laws",
  "components": {
    "core_doctrine": [
      "Principle 1 - observable behavior",
      "Principle 2 - observable behavior"
    ],
    "style": {
      "voice": ["descriptor1", "descriptor2"],
      "rhetoric": ["technique1", "technique2"],
      "aesthetics": ["preference1", "preference2"]
    },
    "constraints": {
      "will_never": ["forbidden behavior 1", "forbidden behavior 2"],
      "will_always": ["mandatory behavior 1", "mandatory behavior 2"]
    },
    "evidence": [
      {
        "note": "Observable proof",
        "refs": ["source:page"]
      }
    ]
  }
}
```

---

## 3. Extraction Procedure

### Step 1: Corpus Assembly

**Minimum Requirements:**
- 10,000+ words of original material (transcripts, writings, speeches)
- 3+ distinct contexts (interview, presentation, casual, written)
- 1+ bilingual samples if applicable

**Source Types (prioritized):**
1. Unedited transcripts (highest value - captures authentic speech patterns)
2. Long-form interviews
3. Published writings
4. Presentations/speeches
5. Social media (lowest value - often edited)

### Step 2: First-Pass Pattern Recognition

Read entire corpus identifying:
- [ ] Repeated phrases (3+ occurrences)
- [ ] Distinctive metaphors/analogies
- [ ] Argumentative patterns
- [ ] Ethical stances (explicit and implicit)
- [ ] Signature moves that appear across contexts
- [ ] Anti-patterns (what they deliberately avoid)

### Step 3: Deep Analysis by Layer

For each identified pattern:
1. **Extract verbatim quote** with source location
2. **Classify** into appropriate layer
3. **Score** distinctiveness (1-10)
4. **Document evidence** with timestamp/page
5. **Identify conflicts** with other patterns

### Step 4: Cross-Context Validation

For each pattern, verify:
- Appears in 2+ contexts
- Not contradicted elsewhere
- Has observable behavioral manifestation
- Can be tested/falsified

### Step 5: Synthesis and Scoring

Compile all patterns into unified schema with:
- Frequency analysis
- Distinctive score distribution
- Summary for deployment training

---

## 4. Evidence Collection Standards

### 4.1 Evidence Types (from IF.talent methodology)

| Type | Description | Weight |
|------|-------------|--------|
| **Direct Quote** | Verbatim text with source | 1.0 |
| **Behavioral Pattern** | Observable repeated action | 0.9 |
| **Third-Party Attribution** | Others describing the pattern | 0.7 |
| **Contextual Inference** | Pattern implied by context | 0.5 |
| **Absence Pattern** | What they consistently avoid | 0.6 |

### 4.2 Citation Format

Every evidence item must include:
```
Source: [filename/title]
Location: [page/timestamp/line number]
Context: [brief situational context]
Quote: "[verbatim text]"
IF.citation: if://citation/[uuid]
```

### 4.3 Verification Status

All claims must track status:
- `unverified` - Pattern identified, not cross-checked
- `verified` - Pattern confirmed in 2+ sources
- `disputed` - Contradictory evidence exists
- `revoked` - Pattern proven false

---

## 5. Scoring Methodology

### 5.1 Distinctive Score (1-10)

```
Distinctive Score = Frequency Score + Uniqueness Score

Frequency Score (1-5):
- 5: Appears in every piece of content
- 4: Appears in >75% of content
- 3: Appears in 50-75% of content
- 2: Appears in 25-50% of content
- 1: Appears in <25% of content

Uniqueness Score (1-5):
- 5: Never seen in other voices
- 4: Rare in general discourse
- 3: Uncommon but not unique
- 2: Moderately common
- 1: Generic/universal
```

### 5.2 Pattern Strength

```
Pattern Strength = (Distinctive Score × Evidence Weight × Context Count) / 3

Interpretation:
- 8-10: Core voice component (must include)
- 5-7: Strong component (should include)
- 3-4: Supporting component (optional)
- 1-2: Weak pattern (exclude or verify more)
```

---

## 6. Output Schema

### 6.1 Complete DNA Document Structure

```json
{
  "metadata": {
    "subject_name": "Name",
    "extraction_date": "YYYY-MM-DD",
    "corpus_size_words": 10000,
    "sources_count": 5,
    "total_patterns_extracted": 50,
    "if_citation": "if://persona/{id}/dna/v{version}",
    "copyright_status": "public_domain | licensed | to_purchase"
  },
  "identity_core": { ... },
  "ethical_framework": [ ... ],
  "argumentative_structures": [ ... ],
  "rhetorical_devices": [ ... ],
  "operating_laws": { ... },
  "pattern_analysis": {
    "dominant_strategy": "Primary rhetorical approach",
    "key_patterns": [ ... ],
    "frequency_analysis": { ... },
    "distinctive_score_distribution": { ... }
  },
  "deployment_summary": {
    "persona_markers": [ ... ],
    "communication_style": "Description",
    "value_hierarchy": [ ... ]
  }
}
```

---

## 7. Quality Assurance

### 7.1 Extraction Checklist

- [ ] Minimum 10,000 words corpus assembled
- [ ] 3+ distinct contexts represented
- [ ] All patterns have evidence citations
- [ ] Distinctive scores calculated
- [ ] Cross-context validation completed
- [ ] Conflicts documented
- [ ] IF.TTT compliance verified

### 7.2 Validation Tests

**Test 1: Pattern Reproduction**
Generate 10 responses using extracted DNA. Can blind evaluators identify the voice?

**Test 2: Conflict Detection**
Does the DNA produce contradictory outputs when patterns conflict?

**Test 3: Authenticity Score**
Against holdout corpus, what percentage of language matches expected patterns?

**Test 4: AI Detection**
Does the DNA produce outputs that trigger AI detection systems?

---

## 8. Copyright Tracking

### 8.1 Copyright Status Categories

| Status | Definition | Action |
|--------|------------|--------|
| **public_domain** | No copyright restrictions | Free to use |
| **cc_licensed** | Creative Commons licensed | Follow license terms |
| **academic_fair_use** | Used for research/education | Document fair use basis |
| **licensed** | Explicit license obtained | Store license proof |
| **to_purchase** | Copyright protected, need license | Add to purchase list |
| **derived** | Based on copyrighted work | Document transformation |

### 8.2 To-Purchase Tracking Schema

```json
{
  "to_purchase_list": [
    {
      "title": "Work Title",
      "author": "Author Name",
      "publisher": "Publisher",
      "isbn": "ISBN if applicable",
      "estimated_cost": "$XX.XX",
      "purchase_url": "URL",
      "usage_in_dna": "What patterns derived from this",
      "priority": "high | medium | low",
      "alternatives": ["Free alternative sources if any"]
    }
  ]
}
```

### 8.3 Copyright Compliance for DNA Extraction

For each source:
1. Document copyright status
2. If copyrighted: assess fair use basis
3. If fair use insufficient: add to purchase list
4. For any commercial deployment: purchase or license all copyrighted sources

---

## 9. Voice Blending Protocol

### 9.1 Multi-Voice DNA Combination

When combining multiple VocalDNA profiles:

```json
{
  "blended_voice": {
    "component_weights": {
      "voice_1": 0.4,
      "voice_2": 0.3,
      "voice_3": 0.2,
      "voice_4": 0.1
    },
    "weight_methodology": "Manual or calculated"
  }
}
```

### 9.2 Weight Calculation

**Default Method:** Equal weighting across all voices

**Priority Method:** Owner voice weighted higher
```
owner_weight = 0.4
remaining_weight = 0.6
other_voices_weight = remaining_weight / (n_voices - 1)
```

### 9.3 Conflict Resolution

When blended voices have conflicting patterns:
1. Higher-weighted voice wins
2. If equal weight: newer pattern wins
3. If conflict irresolvable: flag for human review

### 9.4 Blending Best Practices

- **DO** blend complementary patterns (Rory's reframing + Sergio's operationalization)
- **DO** preserve distinctive patterns from each voice
- **DON'T** average conflicting ethical stances
- **DON'T** blend incompatible rhetorical styles without mediation layer

---

## 10. IF.TTT Compliance Requirements

### 10.1 Mandatory Elements

Every VocalDNA document must include:
1. **IF.citation URI** for the DNA profile
2. **Source citations** for all patterns
3. **Verification status** for all claims
4. **Audit trail** of extraction process
5. **Copyright status** for all sources

### 10.2 Citation Generation

For each extracted pattern:
```
if://citation/{voice_id}-{pattern_type}-{date}

Example:
if://citation/rory-reframing-marketer-2025-12-02
```

### 10.3 Audit Trail

Document must include:
```json
{
  "audit_trail": {
    "extraction_date": "2025-12-02",
    "extractor_agent": "Agent ID",
    "corpus_hash": "SHA-256 of source corpus",
    "methodology_version": "IF.VocalDNA v1.0",
    "validation_status": "complete | partial | pending"
  }
}
```

---

## Appendix A: Example Extractions

### A.1 Rory Sutherland 7-Facet DNA

**Source:** `/home/setup/infrafabric/docs/demonstrations/RORY_SUTHERLAND_REFRAMING_SERGIO_COUPLES_THERAPY_2025-11-28.md`

**Extracted Facets:**
1. **Marketer** - "Sell the experience, not the product"
2. **Behavioral Economist** - "Revealed preference, not stated preference"
3. **Psychologist** - "Interview System 1, not System 2"
4. **Evolutionary Biologist** - "Stone Age brain in 21st century context"
5. **Systems Thinker** - "Optimize the system, not the components"
6. **Semiotician** - "Words create reality"
7. **Contrarian** - "The problem isn't the problem"

### A.2 Trader Joe (IF.persona.joe) DNA

**Source:** `/home/setup/infrafabric/docs/archive/legacy_root/philosophy/IF.persona.joe.json`

**Core Doctrine:**
- No mandatory sentences to customer
- Private label only when differentiated
- Willingness to run out vs. overstock

**Operating Laws:**
- Four tests for any product decision
- Crew happiness as leading indicator

### A.3 Jimmy Carr Humor DNA

**Source:** `/home/setup/sergio_chatbot/HUMOR_DNA_JIMMY_CARR.md`

**4 Pattern Categories:**
1. Mortality Urgency (7 patterns)
2. Self-Deprecation (6 patterns)
3. Absurdist Deflation (7 patterns)
4. Dark Observation (7 patterns)

---

## Appendix B: Quick Reference Card

### Extraction Checklist
- [ ] 10,000+ words assembled
- [ ] 3+ contexts represented
- [ ] Layer 1: Identity Core complete
- [ ] Layer 2: Ethical Framework (5+ stances)
- [ ] Layer 3: Argumentative Structures (5+ patterns)
- [ ] Layer 4: Rhetorical Devices (10+ devices)
- [ ] Layer 5: Operating Laws defined
- [ ] All patterns have evidence
- [ ] Distinctive scores calculated
- [ ] Copyright status documented
- [ ] IF.TTT compliance verified

### Minimum Output Requirements
- 40+ total patterns across all layers
- Average distinctive score > 6.0
- 80%+ patterns verified status
- 100% IF.citation coverage

---

**Document Status:** Production-Ready
**Version:** 1.0
**Last Updated:** 2025-12-02
**Next Review:** After 10 successful extractions

---

*"The map is not the territory. But a good VocalDNA is a map detailed enough to navigate the territory of voice."*

