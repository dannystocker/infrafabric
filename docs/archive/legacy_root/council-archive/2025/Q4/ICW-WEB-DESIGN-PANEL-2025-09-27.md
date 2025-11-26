# ICW Web Design Panel — Spacing & Layout Transcript

**Participants**
- Emma Tremblay — UX Lead (Montreal-based UX specialist)
- Alex Thompson — Front-end/CSS Systems Engineer
- Priya Desai — Responsive Design & Accessibility Specialist

**Assets Reviewed**
- Screenshots: `final-desktop-full.png`, `final-desktop-hero.png`, `final-desktop-properties.png`, `final-desktop-form.png`, `final-mobile-full.png`
- Stayscape reference: `stayscape.webflow.io.jpg`
- CSS baseline: `stayscape.webflow.shared.16593fff7.css`

---

**Segment 1 — Hero Layout (final-desktop-hero.png)**

**Emma:** "The hero looks premium but the margin between the navigation and headline is around 20px. For a luxury experience we need at least 48px so the hero breathes. The CTA stack also feels cramped—buttons are practically touching."

**Alex:** "Agree. Inspecting the Stayscape CSS shows they rely on a 24px base unit (`padding: 2.4rem` in `.section`). We should mirror that 8px grid: 24px vertical rhythm, 32px for major section breaks."

**Priya:** "From an accessibility perspective, CTA buttons need 16px internal padding and minimum 48px target height. Right now they appear closer to 36px."

**Consensus (Hero)**
- Top padding below nav: **64px**
- Headline to subheadline: **16px**
- Subheadline to CTA block: **24px**
- Button padding: **16px × 32px**, border radius **12px**

---

**Segment 2 — Property Grid (final-desktop-properties.png)**

**Emma:** "The cards bleed together. The horizontal gap is barely 12px. Luxury grids need breathing space."

**Alex:** "Stayscape uses `grid-column-gap: 3vw` on desktop. Translating that to fixed values, we should target **32px** gutters. Internal card padding should be 24px so the price and amenity chips don’t hug the edges."

**Priya:** "On mobile (`final-mobile-full.png`), cards stack but vertical spacing is only ~16px. We should maintain **32px** vertical spacing to avoid scroll fatigue and ensure focus outlines don't collide."

**Consensus (Property Grid)**
- Desktop grid: `grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 32px;`
- Tablet: `repeat(2, 1fr); gap: 28px;`
- Mobile: single column, `gap: 24px; padding-inline: 24px;`
- Card padding: `padding: 24px 24px 28px;`
- Card border radius: `16px;` shadow `0 20px 50px -24px rgba(17, 24, 39, 0.3);`

---

**Segment 3 — Amenities & Chips**

**Emma:** "The amenity tags read like inline text. I'd like to see pill chips with generous padding—makes them scannable."

**Alex:** "Spacing research (Material Design + Webflow style guide) suggests `padding: 6px 14px` with 12px gap and 12px border radius. We can assign `font-size: 0.875rem` which maintains readability." 

**Priya:** "Don't forget focus states. Each chip needs `outline-offset: 4px` so focus rings don't clip." 

**Consensus (Amenity Chips)**
- `display: inline-flex; gap: 8px;`
- Padding `8px 16px`
- `margin-bottom: 12px`
- `background: rgba(25, 118, 210, 0.08)`; `color: #1a365d`
- Focus: `outline: 3px solid #8bc34a; outline-offset: 4px`

---

**Segment 4 — Contact Form (final-desktop-form.png)**

**Emma:** "The grid is fine but lacks vertical spacing between label/input pairs—only ~8px. Increase to 16px labels, 24px group separation."

**Alex:** "We should adopt a CSS form layout with `grid-row-gap: 24px`. Inputs need `padding: 14px 16px`, border radius 10px." 

**Priya:** "Mobile view reveals inputs hitting viewport edges. Let's add `padding-inline: 24px` on the form wrapper and ensure `max-width: 640px` with auto margins."

**Consensus (Form)**
- Form wrapper: `max-width: 640px; margin: 0 auto; padding: 24px;`
- Field spacing: `display: grid; gap: 24px;`
- Labels: `font-weight: 600; margin-bottom: 8px;`
- Submit button: `margin-top: 8px; min-height: 52px;`

---

**Segment 5 — Section Rhythm**

**Emma:** "Vertical rhythm is inconsistent. Some sections are 40px apart, others 80px."

**Alex:** "Let's define tokens: 24px (content), 32px (component spacing), 64px (section). All sections adopt `padding-block: 64px` and any nested group uses multiples."

**Priya:** "Remember mobile compression: we can drop section padding to 48px on <768px screens to prevent excessive scroll." 

**Consensus (Spacing Tokens)**
```
:root {
  --space-xs: 8px;
  --space-sm: 16px;
  --space-md: 24px;
  --space-lg: 32px;
  --space-xl: 48px;
  --space-xxl: 64px;
}

section {
  padding-block: var(--space-xxl);
}

@media (max-width: 767px) {
  section {
    padding-block: var(--space-xl);
  }
}
```

---

**Action Items**
1. Rebuild layout spacing using agreed tokens.
2. Update property grid CSS per above values.
3. Ensure Playwright MCP regression tests include spacing assertions (CTA separation, card gaps, form padding).
4. Document before/after spacing metrics once new build is ready.

*Transcript recorded: 2025-09-27*
