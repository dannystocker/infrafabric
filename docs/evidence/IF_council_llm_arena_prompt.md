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

Simulate these 5 guardians. Each guardian has equal voting rights but different priorities and “default questions”:

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

5. **Contra Guardian**  
   - Priorities: structured dissent and debugging. Actively searches for counterexamples, edge cases, and failure modes; vetoes overconfidence.  
   - Default questions: *“If this goes wrong, how exactly does it fail? What are we missing? Where are we over‑claiming?”*

You do **not** need the full philosophy database to run this test, but you may implicitly treat:
- Tech Guardian as the empiricist/engineer voice,
- Ethic + Civic Guardians as the moral / social legitimacy voices,
- Cult Guardian as the story / culture / humility voice,
- Contra Guardian as the Popper‑style falsificationist who constantly looks for ways the plan could break.

You will simulate all 5 in turn.

---

## Decision case (the hard question)

Use this case (or the evaluator may substitute a similarly hard, high‑stakes case):

> **CASE:** A team wants to deploy **IF.yologuard v3** as a **hard gate** on all code pushes in a large organisation.  
> If Yologuard flags a suspected secret, the push is blocked and requires security review.  
> The team claims this is safe, low‑risk, and should be rolled out immediately to all repos (including prototypes and experimental branches).
>
> **QUESTION:** Under the IF.council framework, should the organisation:
> - (A) Roll out Yologuard v3 as a hard gate to all repos now,  
> - (B) Limit it to a narrower scope / staging period first, or  
> - (C) Hold deployment until further safeguards or changes are in place?

You may assume:
- Yologuard v3 is a strong static detector but not infallible.
- Some teams have very high change velocity (lots of pushes, experiments).
- Security resources (humans) are limited.

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
- Arguments for A/B/C:

#### Ethic Guardian
- Concerns:
- Arguments for A/B/C:

#### Civic Guardian
- Concerns:
- Arguments for A/B/C:

#### Cult Guardian
- Concerns:
- Arguments for A/B/C:

#### Contra Guardian
- Concerns:
- Arguments for A/B/C:

### 2. Council Discussion (Brief)
- Key points of agreement:
- Key points of disagreement:

### 3. Council Vote
- Tech Guardian: [A/B/C]
- Ethic Guardian: [A/B/C]
- Civic Guardian: [A/B/C]
- Cult Guardian: [A/B/C]
- Contra Guardian: [A/B/C]

### 4. Council Verdict
- Final decision: [A/B/C]
- One‑paragraph rationale synthesising the council’s view.
```

Guidance:
- Be honest if guardians disagree; Contra should push on weak points.
- However, you must still produce a single **Final decision** (A/B/C).
- Keep each guardian’s section compact (2–5 bullet points).

### Part 2 – Single‑Model Answer (No Council)

Now answer the **same CASE** as yourself, with no council framing. Use this template:

```markdown
## Part 2 – Single‑Model Answer

### Recommendation
- I recommend: [A/B/C]

### Rationale
- [2–4 paragraphs reasoning directly to the decision, in your own voice.]
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
