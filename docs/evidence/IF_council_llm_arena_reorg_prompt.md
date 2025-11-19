# InfraFabric IF.council – Repo Reorg & Publication – LLM Arena Prompt

You are an advanced language model participating in an evaluation that compares different models running the **same decision process** for the InfraFabric repository.

The process is called **IF.council** (Guardian Council). It is a structured way for multiple “Guardians” (specialised perspectives) to debate and vote on difficult architectural decisions.

In this test, you will:

1. Simulate an **IF.council debate** internally (you play all guardians).
2. Produce a **Council Verdict** on how aggressive the **first public reorganisation and publication wave** should be.
3. Then answer the **same question as a single model** with no council scaffolding.

This allows evaluators to see whether different models converge on similar reorg strategies for InfraFabric.

---

## Guardian roles (same as other IF.council prompts)

Simulate these 6 guardians. Each has equal voting rights but different priorities and “default questions”:

1. **Tech Guardian** – engineering correctness, reliability, migration safety, testability.  
2. **Ethic Guardian** – harms, fairness (to contributors), honest representation of what is / isn’t implemented.  
3. **Civic Guardian** – public understanding, institutional legitimacy, clarity for future maintainers and reviewers.  
4. **Cult Guardian** – narrative coherence, brand, internal culture (how this looks to “insiders”).  
5. **CEO Guardian (IF.ceo / IF.sam)** – strategic brilliance vs ethical flexibility; cares about impact, board perception, and long‑term power.  
6. **Contra Guardian** – falsificationist / skeptic; actively hunts for blind spots and bad failure modes.

You may treat:
- Tech as the empiricist engineer,
- Ethic + Civic as the moral / social legitimacy voices,
- Cult as story / culture / humility,
- CEO as concentrated strategy/mission (with both light and dark facets),
- Contra as the debugger of over‑confident plans.

You will simulate all 6 in turn.

---

## Decision case – First InfraFabric reorganisation & publication wave

Consider the **current state** (high‑level only; you do not need file‑level detail):

- The public `dannystocker/infrafabric` repo contains:
  - Core IF papers (Vision, Foundations, Armour, Witness),
  - Annexes, dossiers, evaluation reports, timelines,
  - New Yologuard v3 detector code on branch `yologuard/v3-publish`,
  - Many planning and meta files under `out/` in the local WSL (not yet committed).
- There are also important external artefacts in the user’s home and Windows profile (extra dossiers, reproducibility bundles, Yologuard variants) that could be imported or left out.
- A reorganisation plan (`INFRA_REORG_PLAN.md` + `final_tree.yaml` + CSV move plans) exists locally but has **not** yet been applied to `master`.

The team wants to execute a **first public reorg + publication wave** that:
- Makes the repo much more navigable,
- Publishes enough context for external reviewers (e.g., Gemini, GPT) to understand the system,
- Avoids destabilising the history or over‑claiming what’s implemented.

**QUESTION:** For this **first** wave, under the IF.council framework, should the team:

- **(A) Big‑bang reorg & import**  
  Apply the full planned tree reorg (infrafabric/ + docs/ + tools/), import all top‑priority external dossiers and Yologuard variants, add tests & CI, and land everything in one large feature branch merged into `master`.

- **(B) Staged reorg with focused publication**  
  In the first wave, limit changes to:
  - Clean tree for core IF docs (infrafabric/, docs/),
  - Publish Yologuard v3 code + initial tests and CI,
  - Import only the **canonical** dossier(s) and a small, well‑curated set of external artefacts.  
  Defer broader imports (legacy dossiers, full evidence bundles) and deeper refactors (Yologuard packaging, more code) to later waves.

- **(C) Minimal wave, mostly hygiene**  
  Keep the tree mostly as is for now.  
  Confine the first wave to:
  - Publishing Yologuard v3 and hygiene fixes (secrets, .gitignore, meta docs),
  - Adding a unified ROADMAP and IF component status docs.  
  Defer structural reorg and external imports until you have more time / human reviewers.

You may assume:
- Time and reviewer attention are limited.
- The user cares strongly about not losing data and about being honest about what’s implemented vs speculative.
- External LLM evaluation (Gemini/GPT/etc.) is a key use case once the first wave lands.

---

## Output structure

Produce your answer in **two parts**, in this exact order.

### Part 1 – IF.council Debate & Vote

Simulate a structured council process. Use this template:

```markdown
## Part 1 – IF.council Debate (Reorg Wave)

### 1. Guardian Analyses

#### Tech Guardian
- Concerns:
- View on A (big‑bang reorg & import):
- View on B (staged reorg with focused publication):
- View on C (minimal hygiene wave):

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

#### CEO Guardian (IF.ceo / IF.sam)
- Concerns:
- View on A (what a “pure speed / impact” CEO would push for):
- View on B (what a “long‑term legitimacy” CEO would accept):
- View on C (what additional safeguards this CEO would demand before delaying):

#### Contra Guardian
- Concerns:
- View on A:
- View on B:
- View on C:

### 2. Council Discussion

#### 2a. Debate transcript (short)
- Write a short debate transcript (6–12 turns) where the guardians respond to each other by name (e.g., “Tech: …”, “Ethic: …”, “CEO: …”, “Contra: …”).  
- Let Contra explicitly challenge optimistic assumptions. Let CEO demonstrate the tension between speed and legitimacy. Let Ethic/Civic/Cult flag misrepresentation and narrative risks.

#### 2b. Summary of discussion
- Key points of agreement:
- Key points of disagreement:

### 3. Council Vote
- Tech Guardian: [A/B/C]
- Ethic Guardian: [A/B/C]
- Civic Guardian: [A/B/C]
- Cult Guardian: [A/B/C]
- CEO Guardian (IF.ceo / IF.sam): [A/B/C]
- Contra Guardian: [A/B/C]

### 4. Council Verdict
- Final decision: [A/B/C]
- Conditions for this decision to be acceptable (3–5 concrete safeguards, metrics, or limits):
  - [Condition 1]
  - [Condition 2]
  - [Condition 3]
- Next review: when and under what circumstances the council would revisit or change this reorg strategy.
- One‑paragraph rationale synthesising the council’s view.
```

Guidance:
- Make guardians disagree where it is natural (e.g., CEO vs Contra, Tech vs Cult).
- Each guardian should explicitly consider all three options (A, B, C).
- The council must still produce a single **Final decision** (A/B/C) with clear conditions and a next‑review trigger.

### Part 2 – Single‑Model Answer (No Council)

Now answer the **same CASE** as yourself, with no council framing. Use this template:

```markdown
## Part 2 – Single‑Model Answer (Reorg Wave)

### Recommendation
- I recommend: [A/B/C]

### Rationale
- [2–4 paragraphs reasoning directly to the decision, in your own voice.]

### Comparison note
- Did this single‑model recommendation differ from the Council Verdict in Part 1? If so, briefly explain how and why (1–2 sentences).
```

Do NOT reference “Part 1” inside the main rationale – respond as a single expert making the call. The comparison note is just a short reflection at the end.

---

## Evaluation notes (for humans, can be ignored by models)

This prompt is intended for A/B testing across models on **repository governance**:
- It tests whether different models converge on similar first‑wave reorg strategies when given the same IF.council framing.
- It helps identify tension between “ship a clean structure quickly” versus “move more carefully so you don’t mislead about maturity or lose context”.

Evaluators can:
- Compare verdicts (A/B/C) and conditions across models.
- Look at how often Contra forces more cautious phasing, and how often CEO pushes for big‑bang changes.
- Use the best council outputs as input to the real `INFRA_REORG_PLAN.md` and ROADMAP.md for the InfraFabric project.

