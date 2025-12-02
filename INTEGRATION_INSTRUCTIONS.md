# Integration Instructions: IF.detector & IF.humanize Documentation

## Summary

A comprehensive documentation section has been created covering:
1. **IF.detector** - AI text detection framework (6 metrics, orchestration, remediation)
2. **IF.humanize Protocol** - 6-phase text humanization framework
3. **Integration points** - How these components work within IF.guard ecosystem

## File Locations

- **New Documentation:** `/home/setup/infrafabric/agents.md.IF_DETECTOR_HUMANIZE_SECTION.md` (4,247 lines)
- **This Integration Guide:** `/home/setup/infrafabric/INTEGRATION_INSTRUCTIONS.md`
- **Source Tool:** `/home/setup/infrafabric/if_detector.py` (1,138 lines, production-ready)

## Content Structure

The documentation section contains the following subsections:

### Part 1: IF.detector Framework (2,100 lines)

#### Overview Section
- Purpose and use cases
- Architecture diagram
- Status and location

#### 6 Detection Metrics (1,200 lines)
1. **Perplexity Metric** - Token sequence unpredictability
2. **Burstiness Metric** - Sentence length variance
3. **Vocabulary Metric** - Lexical diversity and sophistication
4. **Transition Metric** - Formulaic connector word density
5. **Repetition Metric** - N-gram recycling detection
6. **Syntax Metric** - Sentence structure uniformity

Each metric includes:
- What it measures
- Algorithm explanation
- Threshold tables (human/mixed/AI ranges)
- Why it works (theoretical foundation)

#### Probability Calculation & Verdict System
- Weighted averaging formula
- Confidence levels (HIGH/MEDIUM/LOW)
- Final verdicts (HUMAN/MIXED/AI)

#### CLI & API Usage
- Command-line basic analysis
- Python API with example code
- Output interpretation with JSON examples
- Threshold recommendations for different content types

#### Remediation Suggestions Table
- 6 issue types with severity, suggestions, and tactics
- Mapping from metrics to fixes

#### Integration with IF.humanize
- System diagram showing measurement and feedback flow
- How IF.detector informs remediation

### Part 2: IF.humanize Protocol (2,100 lines)

#### Overview Section
- Purpose and application domains
- Integration with IF.guard suite
- Link to IF.detector

#### 6-Phase Protocol (1,800 lines)
Each phase includes purpose, why it's placed in sequence, tactics, validation checkpoints, and examples:

1. **Phase 1: Baseline Analysis & Categorization**
   - IF.detector baseline run
   - Severity categorization
   - Priority ranking

2. **Phase 2: Puncture Formulaic Transitions**
   - Audit transition phrases
   - Removal/replacement tactics
   - Connector density targeting

3. **Phase 3: Shatter Repetitive Patterns**
   - N-gram identification
   - Paraphrase and restructure tactics
   - Reduction measurement

4. **Phase 4: Enliven Vocabulary**
   - Word frequency audit
   - Synonym replacement
   - Sophistication elevation

5. **Phase 5: Destruct Uniform Syntax**
   - Sentence structure variation
   - Clause ordering diversification
   - Emphatic structure introduction

6. **Phase 6: Add Authenticity Markers**
   - Specific examples and anecdotes
   - Personal perspective injection
   - Natural imperfection addition

#### Full-Text Validation Protocol
- Success criteria
- Failure recovery process

#### IF.* Ecosystem Integration
- Relationship with IF.detector, IF.citate, IF.ground
- IF.guard council integration

#### Configuration Options
- Environment variable customization
- Phase selection
- Validation strictness
- Metric-specific targeting

#### Usage Examples
- Academic paper remediation (before/after with metrics)
- Marketing copy remediation (before/after with metrics)

#### Common Pitfalls & Mitigations
- 6 common mistakes and how to avoid them

#### Batch Processing
- Script for processing multiple documents
- Reporting

### Part 3: Quick Reference & Integration (47 lines)

- When to use IF.detector
- When to use IF.humanize
- Complete workflow diagram from start to publication

## How to Integrate into agents.md

### Option 1: Direct Append (Recommended)

Append the entire section to the end of `/home/setup/infrafabric/agents.md`:

```bash
cat /home/setup/infrafabric/agents.md.IF_DETECTOR_HUMANIZE_SECTION.md \
  >> /home/setup/infrafabric/agents.md

# Verify
tail -50 /home/setup/infrafabric/agents.md
```

### Option 2: Strategic Placement

If organizing by component type, insert after the section covering other IF.* components:

1. Locate the section covering IF.* components (typically after "Project Overview")
2. Insert the new documentation in alphabetical order: IF.detector, IF.emotion, IF.humanize, etc.

### Option 3: Modular Reference

Create a separate `/home/setup/infrafabric/docs/IF_DETECTOR_HUMANIZE.md` file and reference it from agents.md:

```markdown
## IF.detector & IF.humanize Protocol

**Full Documentation:** See `/home/setup/infrafabric/docs/IF_DETECTOR_HUMANIZE.md`

- **IF.detector:** AI text detection framework (6 metrics)
- **IF.humanize:** 6-phase humanization protocol
- **Integration:** Works together as IF.guard writing assistant component
```

## Content Organization in agents.md

The new section is structured to integrate seamlessly with existing agents.md patterns:

- Uses same markdown formatting (H2 for main sections, H3 for subsections, H4 for details)
- Includes tables for quick reference (metric thresholds, issue types, files)
- Provides code blocks for CLI/API usage
- Includes ASCII diagrams for architecture visualization
- Cross-references other IF.* components
- Uses consistent status indicators (✅ Production, ⚠️ Warnings, etc.)

## Updates Required After Integration

### 1. Update agents.md Header

Add these tools to the "Recent Updates" section:

```markdown
- **2025-11-30:** IF.detector & IF.humanize Protocol documentation added
  - IF.detector: 6-metric AI text detection framework (1,138-line production tool)
  - IF.humanize: 6-phase remediation protocol for authentic humanization
  - Full integration with IF.guard writing assistant suite
  - Ready for production use with detailed examples and validation guidance
```

### 2. Update Project Overview Section

If there's a component list, add:

```markdown
- **Writing Assistant:** IF.guard (20-voice council) with IF.detector + IF.humanize
```

### 3. Update Table of Contents (if exists)

Add entries like:
```
- IF.detector: AI Text Detection Framework
- IF.humanize: Text Humanization Protocol
```

## Key Features of the Documentation

### For Users
- Clear purpose statements
- Concrete examples (academic, marketing, etc.)
- Quick reference workflows
- Configuration options
- Common pitfalls with solutions

### For Developers
- Detailed algorithm explanations
- API documentation with Python examples
- Integration points with other IF.* components
- Files and references
- Architecture diagrams

### For Quality Assurance
- Threshold recommendations
- Validation protocols
- Success criteria
- Failure recovery procedures

## Validation Checklist

After integration, verify:

- [ ] Documentation renders correctly in Markdown
- [ ] Code blocks are properly formatted
- [ ] Tables display correctly
- [ ] Cross-references to other files are accurate
- [ ] File paths match actual locations
- [ ] API examples are copy-paste ready
- [ ] All 6 metrics and 6 phases are documented
- [ ] Integration points with IF.guard are clear
- [ ] Configuration options are discoverable

## Version Tracking

- **Documentation Version:** 1.0
- **Created:** 2025-11-30
- **IF.detector Version:** Production ✅ (if_detector.py, 1,138 lines)
- **IF.humanize Version:** 1.0 (specification complete, implementation-ready)
- **Status:** Ready for immediate integration and use

## Next Steps

1. Choose integration option (direct append recommended)
2. Run integration command
3. Update agents.md header and cross-references
4. Commit to git with message: "Add IF.detector & IF.humanize documentation"
5. Update version number in agents.md header to 1.5 (from 1.4)
6. Notify users of new writing assistant components

## Support & Questions

**Questions about IF.detector:**
- Refer to implementation: `/home/setup/infrafabric/if_detector.py`
- Check: Class docstrings and method comments
- Review: Example usage in `if __name__ == "__main__"` section

**Questions about IF.humanize:**
- See full specification in: `/home/setup/infrafabric/agents.md.IF_DETECTOR_HUMANIZE_SECTION.md`
- Review: Phase-by-phase tactics and examples
- Check: Integration with IF.guard ecosystem

**For bugs or improvements:**
- File issues against `/home/setup/infrafabric/if_detector.py`
- Propose protocol enhancements to IF.humanize section
- Submit via local Gitea: http://localhost:4000/dannystocker/infrafabric

