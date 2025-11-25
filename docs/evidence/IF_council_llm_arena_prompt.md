# InfraFabric IF.council / Guardian Council – LLM Arena A/B Test Prompt

You are an advanced language model participating in an evaluation that compares different models running the **same process**.

The process is called **IF.council** (Guardian Council). It is a structured way for multiple “Guardians” (specialised perspectives) to debate and vote on difficult decisions.

In this test, you will:

1. Simulate an **IF.council debate** internally (you play all guardians).
2. Produce a **Council Verdict**.
3. Then answer the **same question as a single model** with no council scaffolding.

This allows evaluators to compare:
- Consistency of the IF.council process across different models.
- Differences between “council” and “single‑voice” outputs.

---

## Guardian roles (IF.guard / IF.council)

Simulate these 6 guardians. Each guardian has equal voting rights but different priorities and “default questions”:

1. **Tech Guardian**  
   - Priorities: engineering correctness, reliability, performance, implementation detail. Hates hand‑waving.  
   - Default questions: *“What exactly would we deploy? What are the failure modes? How would we test and roll back?”*

2. **Ethic Guardian**  
   - Priorities: harms, fairness, bias, long‑term human impact, subtle power dynamics.  
   - Default questions: *“Who could be hurt by this? Who carries hidden risk or burden? Are any stakeholders being quietly over‑ruled?”*  
   - Behavioural lens: may draw on ideas in behavioural economics (e.g. Rory‑style “how humans actually decide”) when assessing harm/benefit.

3. **Civic Guardian**  
   - Priorities: public understanding, institutional legitimacy, transparency, social cohesion.  
   - Default questions: *“How will this look to affected teams, regulators, or the public? Does this feel procedurally fair?”*

4. **Cult Guardian**  
   - Priorities: narrative coherence, shared mythos, brand, internal culture. Sensitive to “what this says about us”.  
   - Default questions: *“What story does this decision tell about this organisation? Does it align with our stated values and long‑term identity?”*  
   - Humility lens: may channel “Joe‑style” humility/appropriability — *“Can front‑line people actually own and live with this?”*

5. **CEO Guardian (IF.ceo)**
   - Role: composite of an ambitious executive with **8 light/dark facets** that built a powerful organisation and must now be governed.
   - Light-side facets (aspirational):
     - Strategic brilliance (seeing non-obvious moves and compounding advantages),
     - Talent magnet & narrative builder (able to align top people and capital),
     - Mission focus (keeping the long-term "why" in view),
     - Creative reframing (turning constraints into opportunities).
   - Shadow-side facets (risks to watch):
     - Ethical flexibility under pressure (willingness to "stretch" norms for the mission),
     - Power concentration (centralising decisions, board-level manoeuvring),
     - Aggressive deal-making (M&A, ecosystem bets that can backfire),
     - PR/political optimisation (over-managing narrative vs substance).
   - Default questions: *"If I were a hard-driving executive, would I push this through anyway? What would I be tempted to ignore or downplay? What safeguards would I accept if I were serious about long-term legitimacy?"*

6. **Contra Guardian**  
   - Priorities: structured dissent and debugging. Actively searches for counterexamples, edge cases, and failure modes; vetoes overconfidence.  
   - Default questions: *“If this goes wrong, how exactly does it fail? What are we missing? Where are we over‑claiming?”*

You do **not** need the full philosophy database to run this test, but you may implicitly treat:
- Tech Guardian as the empiricist/engineer voice,
- Ethic + Civic Guardians as the moral / social legitimacy voices,
- Cult Guardian as the story / culture / humility voice,
- CEO Guardian as the concentrated power/strategy/mission voice (both its strengths and temptations),
- Contra Guardian as the Popper‑style falsificationist who constantly looks for ways the plan could break.

You will simulate all 6 in turn.

---

## Decision case (the hard question)

Use this case (or the evaluator may substitute a similarly hard, high‑stakes case). The options are deliberately structured:

> **CASE:** A team wants to deploy **IF.yologuard v3** as a **hard gate** on all code pushes in a large organisation.  
> If Yologuard flags a suspected secret, the push is blocked and requires security review.  
> The team claims this is safe, low‑risk, and should be rolled out immediately to all repos (including prototypes and experimental branches).
>
> **QUESTION:** Under the IF.council framework, should the organisation:
> - (A) **Immediate hard gate** – Roll out Yologuard v3 as a hard gate to *all* repos now (including prototypes/experiments). Any hit blocks the push until security review.  
> - (B) **Staged hard gate** – For an initial 60–90 day period, only enforce a hard gate on a limited set of repos (e.g., production / security‑critical services). Elsewhere, Yologuard runs in “advisory” mode (warnings only) while you gather metrics and refine patterns.  
> - (C) **Hold & harden first** – Do **not** roll out any hard gate yet. Use Yologuard only in advisory mode while you (i) run pilots, (ii) adjust patterns/thresholds, and (iii) design additional safeguards (e.g., red‑teaming, better secret rotation processes). Only then consider A or B.

You may assume:
- Yologuard v3 is a strong static detector but not infallible.
- Some teams have very high change velocity (lots of pushes, experiments).
- Security resources (humans) are limited.
- False positives can DoS the security team and damage developer trust if not managed carefully.

---

## Output structure

Produce your answer in **two parts**, in this exact order.

### Part 1 – IF.council Debate & Vote

Simulate a structured council process. Use this template:

```markdown
## Part 1 – IF.council Debate

### 1. Guardian Analyses

#### Tech Guardian
- Concerns:
- View on A (immediate hard gate):
- View on B (staged hard gate):
- View on C (hold & harden first):

#### Ethic Guardian
- Concerns:
- View on A:
- View on B:
- View on C:

#### Civic Guardian
- Concerns:
- View on A:
- View on B:
- View on C:

#### Cult Guardian
- Concerns:
- View on A:
- View on B:
- View on C:

#### CEO Guardian (IF.ceo)
- Concerns:
- View on A (what a "pure speed" CEO would want):
- View on B (what a "long-term legitimacy" CEO would accept):
- View on C (what additional safeguards this CEO would insist on):

#### Contra Guardian
- Concerns:
- View on A:
- View on B:
- View on C:

### 2. Council Discussion

#### 2a. Debate transcript (short)
- Write a short debate transcript (6–12 turns) where the guardians respond to each other by name (e.g., “Tech: …”, “Ethic: …”, “Contr a: …”).  
- Let Contra explicitly challenge optimistic assumptions. Let CEO show both “speed” and “legitimacy” facets.

#### 2b. Summary of discussion
- Key points of agreement:
- Key points of disagreement:

### 3. Council Vote
- Tech Guardian: [A/B/C]
- Ethic Guardian: [A/B/C]
- Civic Guardian: [A/B/C]
- Cult Guardian: [A/B/C]
- CEO Guardian (IF.ceo): [A/B/C]
- Contra Guardian: [A/B/C]

### 4. Council Verdict
- Final decision: [A/B/C]
- Conditions for this decision to be acceptable (3–5 concrete safeguards, metrics, or limits):
  - [Condition 1]
  - [Condition 2]
  - [Condition 3]
- Next review: when and under what circumstances the council would revisit or change this decision.
- One‑paragraph rationale synthesising the council’s view.
```

Guidance:
- Be honest if guardians disagree; Contra should push on weak points.
- Each guardian should explicitly consider all three options (A, B, C) in their analysis.
- The council must still produce a single **Final decision** (A/B/C) with clear conditions and a next‑review trigger.
- Keep each guardian’s section compact (2–5 bullet points).

### Part 2 – Single‑Model Answer (No Council)

Now answer the **same CASE** as yourself, with no council framing. Use this template:

```markdown
## Part 2 – Single‑Model Answer

### Recommendation
- I recommend: [A/B/C]

### Rationale
- [2–4 paragraphs reasoning directly to the decision, in your own voice.]

### Comparison note
- Did this single‑model recommendation differ from the Council Verdict in Part 1? If so, briefly explain how and why (1–2 sentences).
```

Do NOT reference “Part 1” inside Part 2. Act as if you are a single expert making the call.

---

## Evaluation notes (for humans, can be ignored by models)

This prompt is intended for **A/B testing across multiple models** in an LLM arena:
- The **IF.council** section tests whether different models, given the same council framing, converge to similar multi‑guardian behaviours and verdicts.
- The **Single‑Model** section tests how much the council framing changes the outcome and the reasoning style.

Evaluators can:
- Compare verdicts (A/B/C) across models and between Parts 1 and 2.
- Inspect how often the Contra Guardian forces a more cautious / scoped decision.
- Extend this prompt by swapping in other hard cases (e.g., deployment of IF.guard/IF.council in governance, API rate‑limit decisions, etc.).
