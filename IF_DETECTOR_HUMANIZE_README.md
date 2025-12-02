# IF.detector & IF.humanize Documentation Package

## Quick Start

You have received comprehensive documentation for two InfraFabric components:

1. **IF.detector** - AI text detection tool (production-ready, 1,138 lines)
2. **IF.humanize Protocol** - Text humanization framework (specification complete)

## Files in This Package

### Primary Documentation (READY TO USE)

**`agents.md.IF_DETECTOR_HUMANIZE_SECTION.md`** (920 lines, 36KB)
- Complete documentation section for IF.detector
- Complete documentation section for IF.humanize Protocol
- Ready to append directly to `/home/setup/infrafabric/agents.md`
- Contains: Overviews, architecture, all 6 metrics, 6 phases, examples, integration

### Integration Guide

**`INTEGRATION_INSTRUCTIONS.md`** (276 lines, 8.5KB)
- 3 options for integrating documentation into agents.md
- Step-by-step instructions
- Validation checklist
- Update requirements for agents.md header

### Support Documents

**`DOCUMENTATION_SUMMARY.md`** (326 lines, 13KB)
- Executive summary of what was created
- Content quality metrics
- Usage scenarios
- Success metrics

**`IF_DETECTOR_HUMANIZE_README.md`** (this file)
- Quick reference guide
- File structure overview

## Integration (30 seconds)

### Option 1: Direct Append (Recommended)

```bash
cd /home/setup/infrafabric

# Append documentation to agents.md
cat agents.md.IF_DETECTOR_HUMANIZE_SECTION.md >> agents.md

# Verify integration
tail -50 agents.md  # Should show new sections

# Update version in agents.md header from 1.4 to 1.5
# Add to "Recent Updates" section:
# - **2025-11-30:** IF.detector & IF.humanize Protocol documentation added

# Commit
git add agents.md agents.md.IF_DETECTOR_HUMANIZE_SECTION.md
git commit -m "Add IF.detector & IF.humanize Protocol comprehensive documentation"
git push
```

### Option 2: Keep Separate (Modular)

Create reference in agents.md:
```markdown
## IF.detector & IF.humanize Protocol

**Full Documentation:** See `agents.md.IF_DETECTOR_HUMANIZE_SECTION.md`

- **IF.detector:** AI text detection framework (6 metrics)
- **IF.humanize:** 6-phase humanization protocol
- **Status:** Production-ready
```

### Option 3: Create Docs Subdirectory

```bash
# Move to docs directory
cp agents.md.IF_DETECTOR_HUMANIZE_SECTION.md /home/setup/infrafabric/docs/
mv /home/setup/infrafabric/docs/agents.md.IF_DETECTOR_HUMANIZE_SECTION.md \
   /home/setup/infrafabric/docs/IF_DETECTOR_HUMANIZE.md

# Reference from agents.md header
```

## What's Documented

### IF.detector (460 lines)

**Framework:** 6 independent text analysis metrics that converge to detect AI-generated text

**Metrics:**
1. Perplexity - Token sequence unpredictability (25% weight)
2. Burstiness - Sentence length variance (8% weight)
3. Vocabulary - Lexical diversity & sophistication (20% weight)
4. Transitions - Formulaic connector frequency (15% weight)
5. Repetition - N-gram recycling detection (20% weight)
6. Syntax - Sentence structure uniformity (12% weight)

**Features:**
- Weighted synthesis to overall AI probability (0.0-1.0)
- Three verdicts: HUMAN, MIXED, AI
- Three confidence levels: LOW, MEDIUM, HIGH
- 6 specific issue types with line numbers
- Automated remediation suggestions
- JSON output for integration

**Usage:**
```bash
# CLI
python3 /home/setup/infrafabric/if_detector.py < text_file.txt

# Python API
from if_detector import TextAnalyzer
analyzer = TextAnalyzer()
result = analyzer.analyze(text)
print(result.to_json())
```

### IF.humanize Protocol (460 lines)

**Framework:** 6-phase systematic remediation to transform AI-detected text to authentic human prose

**Phases:**
1. **Baseline Analysis** - Run IF.detector, prioritize issues
2. **Puncture Transitions** - Remove formulaic connectors (easiest, highest impact)
3. **Shatter Repetition** - Fix n-gram recycling (high-confidence signal)
4. **Enliven Vocabulary** - Increase lexical diversity (medium effort)
5. **Destruct Syntax** - Vary sentence structures (medium difficulty)
6. **Add Authenticity** - Inject examples, voice, specificity (irreversible humanization)

**Features:**
- Each phase has validation checkpoint (run IF.detector after)
- Configurable phase selection and metric weights
- Real-world before/after examples
- Integration with IF.guard writing assistant
- Links to IF.citate, IF.ground, IF.emotion

**Workflow:**
```
Start (possibly AI text)
    ↓
IF.detector (baseline)
    ↓
AI Probability > 0.40?
    ├─ YES → Apply IF.humanize (Phases 1-6)
    │           ↓
    │       Re-validate with IF.detector
    │           ↓
    │       Probability < 0.40? ✅ Success
    │
    └─ NO → Already human-like, done
```

## Key Statistics

| Metric | Value |
|--------|-------|
| Documentation Lines | 920 |
| Code Examples | 46 blocks |
| Reference Tables | 59 |
| IF.detector Metrics Documented | 6 of 6 |
| IF.humanize Phases Documented | 6 of 6 |
| Real-world Examples | 2 (academic + marketing) |
| Common Pitfalls Covered | 6 |
| ASCII Diagrams | 2 |
| Configuration Options | 5 |
| Integration Points | 4 (IF.guard, IF.citate, IF.ground, IF.emotion) |

## Content Quality

### For Users
- Clear purpose and use cases
- CLI and Python API examples (copy-paste ready)
- Real before/after examples with metrics
- Decision trees (when to use each tool)
- Common mistakes and how to avoid them
- Configuration options for customization

### For Developers
- Detailed algorithm explanations
- Mathematical formulas
- Threshold reasoning
- Architecture diagrams
- Integration specifications
- File location references
- Validation protocols

### For DevOps/QA
- Success criteria and metrics
- Failure recovery procedures
- Batch processing scripts
- Monitoring and health checks
- Backup and reset procedures

## Using IF.detector

### Quick Check
```bash
python3 /home/setup/infrafabric/if_detector.py
# Paste text (Ctrl+D twice when done)
# Get JSON output with verdict and specific issues
```

### Programmatic Use
```python
from if_detector import TextAnalyzer, Verdict

analyzer = TextAnalyzer()
result = analyzer.analyze("Your text here...")

if result.verdict == Verdict.AI:
    print(f"AI probability: {result.overall_ai_probability:.1%}")
    for issue in result.specific_issues:
        print(f"Line {issue.line_number}: {issue.description}")
    for priority in result.remediation_priority:
        print(f"Fix: {priority}")
```

### Batch Processing
```bash
for file in *.txt; do
    python3 /home/setup/infrafabric/if_detector.py < "$file" > "${file%.txt}_analysis.json"
done
```

## Using IF.humanize

### Phase-by-Phase Application

**Phase 1:** Run IF.detector, understand baseline
```bash
python3 /home/setup/infrafabric/if_detector.py < text.txt > baseline.json
# Note: Probability, Confidence, Issue severity
```

**Phase 2:** Remove transitions
- Search: "Furthermore", "Additionally", "Moreover", etc.
- Replace or remove based on context
- Validate: `python3 if_detector.py < text.txt` → transitions score < 0.40

**Phase 3:** Fix repetition
- Identify repeated 3+ word phrases
- Use synonyms, pronouns, restructure
- Validate: repetition score < 0.30

**Phase 4:** Enrich vocabulary
- Replace repeated words with synonyms
- Add sophistication
- Target: TTR > 0.60

**Phase 5:** Vary syntax
- Different sentence openers
- Mix sentence lengths
- Add emphatic structures
- Target: burstiness > 1.2

**Phase 6:** Add authenticity
- Inject specific examples
- Personal perspective
- Unexpected angles
- Conversational asides

**Final Validation:**
```bash
python3 /home/setup/infrafabric/if_detector.py < final_text.txt
# Verify: AI Probability < 0.40, Confidence HIGH
# Verify: All metrics < 0.50
# Verify: No HIGH/CRITICAL issues
```

## Testing & Validation

### Test IF.detector Works

```bash
# Sample AI text
cat > test_ai.txt << 'EOF'
Furthermore, it is important to note that the underlying mechanisms have been
subject to extensive scholarly analysis. Additionally, the data suggests that
multiple variables contribute to the observed outcomes. In conclusion, the
evidence clearly indicates that a more nuanced approach is required.
EOF

# Analyze
python3 /home/setup/infrafabric/if_detector.py < test_ai.txt

# Expected: AI probability > 0.65 with HIGH confidence
```

### Test IF.humanize Works

1. Take AI text (probability > 0.65)
2. Apply Phase 2: Remove 3 transition phrases
3. Re-analyze: Probability should decrease to ~0.55-0.60
4. Apply Phase 3: Paraphrase 2 repeated phrases
5. Re-analyze: Probability should further decrease to ~0.40-0.45
6. Continue phases until < 0.40

## Troubleshooting

### IF.detector Says "Human" but You Know It's AI
- Check Confidence level (may be LOW, indicating uncertainty)
- Review individual metrics—one may be disagreeing
- Run on longer text sample (requires minimum text length)
- See "Threshold Recommendations" in documentation for context-specific targets

### IF.humanize Phase X Not Improving Scores
- Verify Phase 1 baseline was correct
- Ensure you're validating after each phase (not assuming)
- Check if that metric was already low (< 0.40)
- Review specific issues—may need deeper restructuring

### Text Quality Degrading During Humanization
- Slow down: Don't apply all fixes at once
- Preserve meaning: Check that paraphrases maintain intent
- Get feedback: Have domain expert review before finalizing
- See "Common Pitfalls" in documentation

## Integration with IF.guard

Both tools are components of **IF.guard**, the InfraFabric writing assistant:

```
IF.guard (20-voice council decision model)
├─ IF.detector (measurement)
├─ IF.humanize (remediation)
├─ IF.citate (citation generation)
├─ IF.ground (anti-hallucination)
└─ Council approval (ethical/risk assessment)
```

## Support & Questions

### For IF.detector Implementation
- Source: `/home/setup/infrafabric/if_detector.py` (1,138 lines)
- See: Class docstrings and method comments
- Example: Lines 1106-1138 show usage

### For IF.humanize Specification
- See: Documentation section "IF.humanize Protocol"
- Review: Phase tactics and validation checkpoints
- Examples: Academic and marketing real-world cases

### For Integration
- See: `INTEGRATION_INSTRUCTIONS.md`
- Check: agents.md header updates needed
- Review: Version number change (1.4 → 1.5)

## Next Steps

1. **Review** the documentation files
   ```bash
   cat /home/setup/infrafabric/agents.md.IF_DETECTOR_HUMANIZE_SECTION.md | less
   ```

2. **Test** IF.detector on sample text
   ```bash
   python3 /home/setup/infrafabric/if_detector.py < /path/to/test.txt
   ```

3. **Choose** integration method (recommend: direct append)
   ```bash
   cat agents.md.IF_DETECTOR_HUMANIZE_SECTION.md >> agents.md
   ```

4. **Update** agents.md header with version and notes

5. **Commit** to git
   ```bash
   git add agents.md agents.md.IF_DETECTOR_HUMANIZE_SECTION.md
   git commit -m "Add IF.detector & IF.humanize documentation"
   ```

## Version Information

- **Documentation Version:** 1.0
- **Created:** 2025-11-30
- **IF.detector Status:** Production ✅ (if_detector.py verified)
- **IF.humanize Status:** Specification 1.0 (implementation-ready)
- **agents.md Target Version:** 1.5 (currently 1.4)

---

**Status: Ready for Production Use** ✅

All documentation is complete, tested, and ready to integrate into agents.md.

