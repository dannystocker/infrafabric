# Diagram Density Analysis: How Many Can We Fit?

**Date:** 2025-11-17
**Question:** Can we add MORE diagrams? What A4 sizing works?

---

## A4 Page Space Analysis

### Standard A4 Dimensions
- **Width:** 210mm (8.27 inches)
- **Height:** 297mm (11.69 inches)
- **Margins (standard):** 25mm (1 inch) top/bottom/left/right
- **Usable content area:** 160mm × 247mm (6.3" × 9.7")

### Diagram Size Options

**Option 1: Full-width diagram (80% of A4)**
- **Width:** 168mm (80% of 210mm)
- **Height:** Variable (up to 238mm = 80% of 297mm)
- **Use case:** Complex flowcharts, timelines, RACI matrices
- **Examples:** Section 7 Gantt, Section 8 Validation Tree

**Option 2: Half-page diagram (50% of A4)**
- **Width:** 168mm (full usable width)
- **Height:** 120mm (half height with margins)
- **Use case:** Simple decision trees, small flowcharts
- **Examples:** Section 5.1 Decision Tree, Section 6.5 SCARF

**Option 3: Quarter-page diagram (25% of A4)**
- **Width:** 80mm (half width)
- **Height:** 120mm (half height)
- **Use case:** Very simple diagrams, formula trees
- **Examples:** Section 5.4 Scoring formula

---

## Current Section Inventory: 21 Sections

### Sections WITH diagrams potential (17 sections)

| Section | Diagram Type | Complexity | Recommended Size | Time (min) |
|---------|--------------|------------|------------------|------------|
| **1. Résumé Exécutif** | Overview flowchart | Medium | Half-page (50%) | 8 |
| 2. Contexte & Faits | 3 depots map | Low | Quarter (25%) | 5 |
| **3. Diagnostic** | Problems tree | Medium | Half-page (50%) | 8 |
| 3.5 Psychologie B2B | Recovery paradox | Low | Quarter (25%) | 5 |
| 4. Cas Externes | Benchmark comparison | Low | Half-page (50%) | 6 |
| **5.1 Règle proximité** | Decision tree | High | Full (80%) | 10 ✅ DONE (ASCII) |
| **5.2 Alertes & SLA** | Timeline triggers | High | Full (80%) | 10 |
| 5.3 Satisfaction | Survey flow | Low | Quarter (25%) | 5 |
| 5.4 Scoring dépôt | Formula tree | Low | Quarter (25%) | 5 |
| 5.5 Geste Relationnel | Trust signal flow | Low | Quarter (25%) | 5 |
| **6. Gouvernance** | RACI swim lanes | High | Full (80%) | 10 |
| **6.5 Gouvernance SCARF** | SCARF 5 dimensions | Medium | Half-page (50%) | 8 |
| 6.6 Conformité | Compliance checklist | Low | Quarter (25%) | 5 |
| **7. Plan 90 jours** | Gantt timeline | High | Full (80%) | 10 |
| 7.5 Stress-Test | Risk mitigation tree | Medium | Half-page (50%) | 8 |
| **8. Indicateurs** | Validation criteria | High | Full (80%) | 10 |
| 8.5 Indicateurs Récup | Recovery metrics | Medium | Half-page (50%) | 8 |
| 9. Sensibilité | Scenario comparison | Medium | Half-page (50%) | 8 |
| 9.5 Crédibilité RSI | Formula transparency | Low | Quarter (25%) | 5 |
| **9.6 Arbitrages** | Tradeoff matrix | Medium | Half-page (50%) | 8 |
| 10. Conformité | RGPD flow | Low | Quarter (25%) | 5 |

**Total diagrams possible:** 21 (one per section)

**Total time:** ~140 minutes (2h 20min) for ALL diagrams

---

## Feasibility Analysis

### Scenario 1: 30-Minute Window (Realistic)

**Agent allocation:**
- 21 section agents (text transformation): 30 min
- **6 diagram agents** (priority only): 15 min
- 7 QA agents: 10 min
- 1 assembly agent: 5 min

**Total:** 60 minutes (EXCEEDS 30-min window)

**Recommendation:** **6 priority diagrams** (Sections 5.1, 5.2, 6, 6.5, 7, 8)

---

### Scenario 2: 60-Minute Window (If Credits Allow)

**Agent allocation:**
- 21 section agents: 30 min
- **12 diagram agents** (high + medium priority): 30 min
- 7 QA agents: 10 min
- 1 assembly agent: 5 min
- **1 visual QA agent (Playwright):** 10 min

**Total:** 85 minutes (acceptable overage)

**Recommendation:** **12 diagrams** (all High + most Medium complexity)

**Diagrams included:**
1. ✅ Section 1: Overview flowchart (Half)
2. ✅ Section 3: Problems tree (Half)
3. ✅ Section 5.1: Decision tree (Full) - already done
4. ✅ Section 5.2: Alerts timeline (Full)
5. ✅ Section 6: RACI governance (Full)
6. ✅ Section 6.5: SCARF model (Half)
7. ✅ Section 7: Gantt timeline (Full)
8. ✅ Section 7.5: Risk mitigation (Half)
9. ✅ Section 8: Validation criteria (Full)
10. ✅ Section 8.5: Recovery metrics (Half)
11. ✅ Section 9: Scenario comparison (Half)
12. ✅ Section 9.6: Tradeoff matrix (Half)

---

### Scenario 3: 120-Minute Window (Full Enhancement)

**Agent allocation:**
- 21 section agents: 30 min
- **21 diagram agents** (ALL sections): 60 min
- 7 QA agents: 10 min
- 1 assembly agent: 5 min
- **1 visual QA agent (Playwright):** 15 min

**Total:** 120 minutes (2 hours)

**Recommendation:** **21 diagrams** (every section gets visual aid)

**Value proposition:** Document becomes FULLY visual-enhanced
- Board presentation ready (no additional slides needed)
- Training manual ready (new Angélique learns from diagrams)
- Distributable to ALL (visuals transcend language complexity)

---

## A4 Sizing Recommendations by Diagram Type

### Full-width (80% A4) - 6 diagrams
**Sections:** 5.1, 5.2, 6, 7, 8
**Reason:** Complex decision trees, timelines, RACI need space
**Graphviz settings:**
```dot
size="6.5,9"  // inches (80% of A4)
dpi=300       // high resolution for print
rankdir=TB    // top-to-bottom (vertical flow)
```

### Half-page (50% A4) - 10 diagrams
**Sections:** 1, 3, 6.5, 7.5, 8.5, 9, 9.6
**Reason:** Medium complexity, fits 2 per page if needed
**Graphviz settings:**
```dot
size="6.5,4.5"  // inches (50% height)
dpi=300
rankdir=LR      // left-to-right for compact flow
```

### Quarter-page (25% A4) - 5 diagrams
**Sections:** 2, 3.5, 5.3, 5.4, 5.5, 6.6, 9.5, 10
**Reason:** Simple formulas, checklists, small trees
**Graphviz settings:**
```dot
size="3.2,4.5"  // inches (quarter width)
dpi=300
rankdir=TB      // vertical compact
```

---

## Visual Verification Requirements

### Why Playwright/Puppeteer Needed

**Problem:** Graphviz auto-layout can cause:
1. **Text overlap** on node labels (French text longer than English)
2. **Edge collisions** (arrows crossing incorrectly)
3. **Insufficient spacing** (margins too tight for readability)

**Solution:** Automated visual QA checks

### Playwright Verification Script

```javascript
// visual_qa_diagrams.js
const { chromium } = require('playwright');
const fs = require('fs');

async function verifyDiagram(svgPath, sectionName) {
    const browser = await chromium.launch();
    const page = await browser.newPage();

    // Load SVG
    await page.setContent(`
        <!DOCTYPE html>
        <html>
        <body style="margin: 0; padding: 20px; background: white;">
            ${fs.readFileSync(svgPath, 'utf8')}
        </body>
        </html>
    `);

    // Check 1: Text overlap detection
    const textOverlaps = await page.evaluate(() => {
        const texts = Array.from(document.querySelectorAll('text'));
        for (let i = 0; i < texts.length; i++) {
            const rect1 = texts[i].getBoundingClientRect();
            for (let j = i + 1; j < texts.length; j++) {
                const rect2 = texts[j].getBoundingClientRect();
                if (rectsOverlap(rect1, rect2)) {
                    return {
                        overlap: true,
                        text1: texts[i].textContent,
                        text2: texts[j].textContent
                    };
                }
            }
        }
        return { overlap: false };

        function rectsOverlap(r1, r2) {
            return !(r1.right < r2.left ||
                     r1.left > r2.right ||
                     r1.bottom < r2.top ||
                     r1.top > r2.bottom);
        }
    });

    // Check 2: Diagram fits in A4 bounds
    const dimensions = await page.evaluate(() => {
        const svg = document.querySelector('svg');
        return {
            width: svg.getBoundingClientRect().width,
            height: svg.getBoundingClientRect().height
        };
    });

    // A4 80% = 168mm = 474px @ 72dpi, 632px @ 96dpi
    const maxWidth = 632; // pixels (80% A4 width @ 96dpi)
    const maxHeight = 895; // pixels (80% A4 height @ 96dpi)

    const violations = [];

    if (textOverlaps.overlap) {
        violations.push({
            type: 'TEXT_OVERLAP',
            text1: textOverlaps.text1,
            text2: textOverlaps.text2
        });
    }

    if (dimensions.width > maxWidth) {
        violations.push({
            type: 'WIDTH_EXCEEDED',
            actual: dimensions.width,
            max: maxWidth
        });
    }

    if (dimensions.height > maxHeight) {
        violations.push({
            type: 'HEIGHT_EXCEEDED',
            actual: dimensions.height,
            max: maxHeight
        });
    }

    // Check 3: Screenshot for manual review
    await page.screenshot({
        path: `DIAGRAM_QA_${sectionName}.png`,
        fullPage: true
    });

    await browser.close();

    return {
        section: sectionName,
        violations: violations,
        dimensions: dimensions,
        screenshot: `DIAGRAM_QA_${sectionName}.png`
    };
}

// Run on all diagrams
(async () => {
    const diagrams = [
        { svg: 'DIAGRAM_SECTION_5.1.svg', name: 'Section_5.1' },
        { svg: 'DIAGRAM_SECTION_5.2.svg', name: 'Section_5.2' },
        { svg: 'DIAGRAM_SECTION_6.svg', name: 'Section_6' },
        { svg: 'DIAGRAM_SECTION_7.svg', name: 'Section_7' },
        { svg: 'DIAGRAM_SECTION_8.svg', name: 'Section_8' },
        // ... add all 21 diagrams
    ];

    const results = [];
    for (const diagram of diagrams) {
        const result = await verifyDiagram(diagram.svg, diagram.name);
        results.push(result);
        console.log(`✓ Verified ${diagram.name}: ${result.violations.length} violations`);
    }

    // Save QA report
    fs.writeFileSync('DIAGRAM_QA_REPORT.json', JSON.stringify(results, null, 2));

    // Summary
    const totalViolations = results.reduce((sum, r) => sum + r.violations.length, 0);
    console.log(`\n=== DIAGRAM QA SUMMARY ===`);
    console.log(`Total diagrams: ${results.length}`);
    console.log(`Total violations: ${totalViolations}`);
    console.log(`Pass rate: ${((results.length - totalViolations) / results.length * 100).toFixed(1)}%`);
})();
```

### Auto-Fix Strategy for Violations

**If text overlap detected:**
```dot
// Increase node spacing
nodesep=1.0;  // default 0.25
ranksep=1.0;  // default 0.5

// Or use explicit node sizes
node [width=2.5, height=0.8];
```

**If width exceeded:**
```dot
// Switch to vertical layout
rankdir=TB;  // instead of LR

// Or increase page size
size="8,10";  // allow taller diagram
```

**If height exceeded:**
```dot
// Compress vertical spacing
ranksep=0.3;

// Or split into 2 diagrams
```

---

## FINAL RECOMMENDATION

### For 30-Minute Window
**Include:** 6 diagrams (Sections 5.1, 5.2, 6, 6.5, 7, 8)
- All Full-width (80% A4) or Half-page (50% A4)
- Visual QA: Manual review only (no time for Playwright)

### For 60-Minute Window
**Include:** 12 diagrams (add Sections 1, 3, 7.5, 8.5, 9, 9.6)
- Mix of Full/Half/Quarter sizes
- Visual QA: Playwright automated check (10 min)

### For 120-Minute Window (RECOMMENDED)
**Include:** 21 diagrams (ALL sections)
- 6 Full-width + 10 Half-page + 5 Quarter-page
- Visual QA: Playwright automated + manual review (15 min)
- **Value:** Document becomes fully visual-enhanced, training-ready, presentation-ready

**Answer:** **YES, we can squeeze in MORE diagrams!**
- 21 total possible (one per section)
- Mix of sizes: 80% A4 (complex) + 50% A4 (medium) + 25% A4 (simple)
- Time: 60 min for 12 diagrams, 120 min for all 21
- Visual QA essential for French text overlap detection

---

## Updated Cloud Prompt Sections

### Agent Assignment (120-min scenario)

| Agent Range | Task | Count | Time |
|-------------|------|-------|------|
| 1-21 | Section text transforms | 21 | 30 min |
| 22-42 | Diagram generation (.dot → SVG) | 21 | 60 min |
| 43 | Assembly | 1 | 5 min |
| 44-50 | QA (TTT/French/Examples/Preservation) | 7 | 10 min |
| 51 | Visual QA (Playwright) | 1 | 15 min |
| 52 | Final formatting | 1 | 5 min |

**Total:** 125 minutes (2h 5min)
**Total agents:** 52 Haiku agents

**Cost:** ~$1.20 USD (52 agents × 2.4 min avg × $0.001/1K tokens × 500 tokens avg)
