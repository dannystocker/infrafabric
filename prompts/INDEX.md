# Gemini Prompts Directory

This directory contains orchestration prompts for Gemini AI that automate complex synthesis and analysis tasks.

## Available Prompts

### 1. GEMINI-META-INTEGRATION-PROMPT.txt (Primary Prompt)

**Purpose:** Single comprehensive meta-prompt that tells Gemini to:
- Fetch all Instance #12 deliverables from GitHub
- Read and analyze key documentation in priority order
- Synthesize Intelligence findings with app design requirements
- Generate a complete integration blueprint with technical architecture

**Size:** 44 KB, ~1,082 lines, ~5,900 words
**Output:** 3,500-5,000 word synthesis with 6 sections:
  - A: Executive Summary
  - B: Integration Architecture
  - C: Feature Specifications
  - D: Content & Messaging
  - E: Development Roadmap
  - F: Next Steps & Timeline

**Use When:**
- Planning enhanced app development
- Briefing development team on requirements
- Preparing for Georges demo (Dec 10-15)
- Need to synthesize 23+ deliverables into actionable plan
- Estimating project timeline and effort

**How to Use:**
1. Open this file: `GEMINI-META-INTEGRATION-PROMPT.txt`
2. Select all text (Ctrl+A) and copy (Ctrl+C)
3. Go to Gemini: https://gemini.google.com
4. Paste prompt into new conversation and send
5. Wait 5-10 minutes for Gemini to fetch, read, and synthesize
6. Copy relevant sections from output for your use case

---

### 2. README-GEMINI-META-PROMPT.md (User Guide)

**Purpose:** Complete documentation explaining:
- What the meta-prompt does
- How to use it step-by-step
- What Gemini reads from GitHub
- What output to expect
- When to use this prompt
- Troubleshooting tips
- Best practices

**Size:** 12 KB, ~371 lines
**Contains:**
- Overview and benefits
- Phase-by-phase explanation
- Usage instructions
- File list (which documents Gemini reads)
- Scenario examples
- Troubleshooting guide
- Best practices

**Read First:** Yes, read this before using the main prompt

---

## Quick Start

```
1. Open README-GEMINI-META-PROMPT.md (2-3 min read)
   ↓
2. Open GEMINI-META-INTEGRATION-PROMPT.txt
   ↓
3. Copy entire prompt text
   ↓
4. Open Gemini.google.com
   ↓
5. Paste and send
   ↓
6. Review output (5-10 min to generate)
```

---

## What Gets Read from GitHub

When you run the meta-prompt, Gemini will fetch and read these files from:
`https://github.com/dannystocker/infrafabric`

**Priority 1 - Strategic Context:**
- QUICK-REFERENCE-GEORGES-PARTNERSHIP.md
- DEMO-EXECUTION-SUMMARY.md
- INSTANCE12_REDIS_PRODUCTIVITY_REPORT.md

**Priority 2 - Intelligence & Research:**
- IF-INTELLIGENCE-FINDINGS-SUMMARY.md
- GEORGES-ANTOINE-GARY-COMPREHENSIVE-PROFILE.md
- RAPPORT-POUR-GEORGES-ANTOINE-GARY.md

**Priority 3 - Technical Foundation:**
- INFRAFABRIC_COMPONENT_AUDIT.md
- INSTANCE-12-DELIVERY-SUMMARY.md
- DEMO-WALKTHROUGH-FOR-EXECUTIVES.md

**Priority 4 - App Design:**
- GEMINI-APP-INTELLIGENCE-INTEGRATION.md
- TESTING_ROADMAP_BEFORE_GEORGES.md
- GEORGES-ANTOINE-GARY-RESEARCH-STRATEGY.md

---

## What Gemini Output Looks Like

### Section A: Executive Summary (~500 words)
- What Instance #12 accomplished
- Intelligence findings summary (8 key assessments)
- What's ready now (demo, research, tests, validation)
- Confidence level and recommended path forward

### Section B: Integration Architecture (~800 words)
- Current React app component structure
- 8 new components to add (Intelligence Dashboard, Cost Calculator, etc.)
- How components connect and data flow
- Implementation priority (must-have vs. nice-to-have)
- Technical stack recommendations

### Section C: Feature Specifications (~800 words)
- Detailed specs for each new feature:
  * Intelligence Dashboard
  * Cost Breakdown Calculator
  * Component Deep-Dives
  * Guardian Council Governance Demo
  * Test #1B Evidence Browser
  * Timeline Visualization
  * French Language Support
  * Risk Navigator

### Section D: Content & Messaging (~400 words)
- How to position using Intelligence findings
- Key messages for each section
- French localization strategy
- Tone and voice guidelines

### Section E: Development Roadmap (~300 words)
- Phase 1 (Critical path): 2 weeks, Dec 1-15
- Phase 2 (Important features): 1-2 weeks, Dec 15-30
- Phase 3 (Polish): Ongoing
- Effort estimates and resource planning
- Success metrics per phase

### Section F: Next Steps & Launch Timeline (~200 words)
- Immediate actions (48 hours)
- Pre-launch prep (Dec 1-8)
- Demo window (Dec 10-15)
- Post-demo activities (Dec 15-30)
- Success criteria and contingency plans

---

## Common Use Cases

### Use Case 1: Development Planning
**Goal:** Brief dev team on what to build
**Action:** Run meta-prompt → Share Section B-C
**Output:** Clear architecture and feature specs with effort estimates

### Use Case 2: Executive Briefing
**Goal:** Inform stakeholders on progress and plan
**Action:** Run meta-prompt → Share Section A + F
**Output:** Executive summary + timeline

### Use Case 3: Demo Preparation
**Goal:** Ensure app is ready for Georges Dec 10-15
**Action:** Run meta-prompt → Review Section F checklist
**Output:** Launch readiness checklist and success criteria

### Use Case 4: Project Management
**Goal:** Create realistic timeline and milestones
**Action:** Run meta-prompt → Copy Section E
**Output:** Development roadmap with phases and dependencies

---

## Technical Details

**What Gemini Does:**
1. Reads prompt instructions (1 min)
2. Fetches 12 documents from GitHub raw links (2-3 min)
3. Reads and analyzes documents in priority order (3-4 min)
4. Synthesizes across all documents (1-2 min)
5. Generates structured 6-section output (1-2 min)
6. **Total time: 8-12 minutes**

**Branch:** The prompt references `yologuard/v3-publish` branch. If that doesn't exist, Gemini will try `main` or ask for clarification.

**GitHub Links:** Gemini uses raw.githubusercontent.com URLs to fetch content directly without rendering HTML.

**Output Format:** Markdown with clear headers, bold, bullet lists, and specific recommendations.

---

## Customization

You can modify the prompt for different purposes:

**For abbreviated output:**
- Remove "PHASE 4: PROVIDE RECOMMENDATIONS"
- Keep only Section A-B and F
- Reduces output to ~1,500 words

**For detailed architecture:**
- Expand "PHASE 4" instructions
- Request more detail in Section B
- Add specific code examples to Section C

**For different time horizons:**
- Adjust timeline in Section F (if demo is Jan instead of Dec)
- Modify phase durations to match your calendar

**For other projects:**
- Replace file references in PHASE 2
- Update persona analysis (not Georges, but different partner)
- Adjust success criteria in Section F

---

## Getting Help

**If Gemini can't fetch a file:**
- Prompt has fallback instructions
- Gemini will note which files it couldn't reach
- Output will be partial but still useful

**If output seems incomplete:**
- Run prompt again (context sometimes helps)
- Provide additional context to Gemini in follow-up message
- Ask Gemini to expand specific sections

**If you want to customize:**
- Copy the prompt
- Make edits to PHASE 2 (file list) or PHASE 5 (output specs)
- Run modified version

---

## Files in This Directory

```
/home/setup/infrafabric/prompts/
├── INDEX.md (this file)
├── GEMINI-META-INTEGRATION-PROMPT.txt (main prompt)
└── README-GEMINI-META-PROMPT.md (detailed guide)
```

**Total Size:** ~56 KB
**Ready to Use:** Yes

---

## Next Steps

1. **Read README-GEMINI-META-PROMPT.md** (understand what it does)
2. **Test with Gemini** (copy prompt, paste into Gemini.google.com)
3. **Review output** (check all 6 sections)
4. **Share with team** (Section A for execs, B-E for dev team)
5. **Use for planning** (Section E for timeline, F for checklist)

---

## Version Info

**Created:** 2025-11-22
**Status:** Ready for production use
**Version:** 1.0

Prompts are designed to be:
- Reproducible (same output each run)
- Comprehensive (covers all key areas)
- Actionable (specific recommendations, not vague advice)
- Transparent (Gemini cites sources and shows reasoning)

---

**Ready to use?** Start with README-GEMINI-META-PROMPT.md, then open GEMINI-META-INTEGRATION-PROMPT.txt.
