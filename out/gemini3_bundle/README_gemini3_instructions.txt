You are Gemini 3 with web + GitHub access.
You have been given this ZIP, which is a distilled view of an AI research repo called "InfraFabric".

All files in this ZIP are plain text copies of artifacts from a local repo at /home/setup/infrafabric. The important ones are:
- gpt5pro_bundle.md.txt          – top-level summary of what a GPT-5.1 agent already did.
- state_summary_mini.md.txt      – a compact diagnostic written by a smaller model (GPT-5-mini) about the current state.
- clean_spec.md.txt              – canonical specification for the system (Guardians, Cycles, ingestion, orchestration, tone rules).
- aggregate_report.md.txt        – per-branch scan summary (IF functions, mentions, Yologuard refs, secrets candidates per branch).
- final_tree.yaml.txt / .md.txt  – a proposed “professor-grade” directory tree for how the repo *should* be organized.
- proposed_tree.{md,yaml}.txt    – an earlier, rougher tree proposal.
- moves_expanded.csv.txt         – proposed file moves (old_path,new_path) to implement the tree.
- migration_plan_mini.md.txt     – a step-by-step migration plan for a CLI agent to clean the repo on a git feature branch.
- secrets_yologuard_risk_mini.md.txt – notes about which files show up in secrets/yologuard scans across branches.
- undef_callgraph_notes_mini.md.txt – notes about unresolved nodes in the IF call graph.
- if_relationship_map.json.txt   – a JSON graph of function/mention relationships across branches.
- addendum_plan.md.txt           – extra context about home-folder and tmp scans and Claude session logs.

You may optionally cross-check the live public repo at:
- https://github.com/dannystocker/infrafabric

Please assume:
- The current git trunk is `master`.
- There are many feature branches (claude/*, swarm/*, gedimat/*, etc.), with most *real* IF function definitions living in at least one claude/sip-escalate branch.
- The local environment has a lot of extra InfraFabric material in the user’s home folder and /tmp, but you only see what’s in this ZIP and (optionally) on GitHub.

Your goals
==========

1. Understand the situation
   - Read the bundle (especially gpt5pro_bundle.md.txt, state_summary_mini.md.txt, clean_spec.md.txt, aggregate_report.md.txt, final_tree.yaml.txt, moves_expanded.csv.txt, migration_plan_mini.md.txt).
   - Optionally glance at the GitHub repo if that helps you cross-check assumptions.
   - In your own words, summarize the current state of the project: branches, quality of organization, level of implementation, and overall “crime-scene” vs “clean” status.

2. Evaluate and stress-test the proposed reorganization
   - Examine final_tree.yaml.txt and proposed_tree.{md,yaml}.txt:
     - Is the proposed directory tree coherent for a human maintainer?
     - Are there obvious gaps (e.g., important families of documents or code not assigned a home)?
   - Check moves_expanded.csv.txt against the tree:
     - Do the moves implement the tree well, or do you spot misplacements / conflicts / duplicates?
   - Review migration_plan_mini.md.txt:
     - Is the sequence of steps realistic and safe for a git-based, multi-branch repo?

3. Spot anything important that may have been missed
   Without being led by specific questions, look for *material* issues that the other agents may have underplayed or skipped. Examples can include (but are not limited to):
   - Structural problems in the proposed tree (e.g., mixing meta/indexes with user-facing docs in confusing ways).
   - Inconsistencies between clean_spec.md.txt and how files are actually grouped in the tree/moves.
   - Risks related to secrets, Yologuard, or call-graph ambiguity that deserve stronger mitigation or clearer actions.
   - Any patterns of duplication, conflicting specs, or naming collisions that would make the repo hard to maintain.

   Your job is to think like a careful systems reviewer: assume nothing is sacred. If the existing tree/moves/plan are flawed, say so and suggest a better pattern.

4. Propose improvements (no code changes needed)
   - Suggest concrete improvements to:
     - The final directory tree (describe changes and, if helpful, show a small YAML snippet for the revised tree).
     - The moves_expanded.csv mapping (e.g., “these files should move together”, “these should not be moved yet”).
     - The migration plan (e.g., extra safety checks, sequence tweaks, additional verification steps).
   - You do *not* need to output the entire revised CSV or full tree; focus on targeted corrections and enhancements that a CLI agent can then implement.

5. Output format
   Please structure your answer as:
   1) Short state summary (1–3 paragraphs).
   2) Key issues you see with the current tree/moves/plan (bullet list).
   3) Recommended refinements to the tree (with small YAML snippets if useful).
   4) Recommended adjustments to the moves plan and migration steps.
   5) Any additional risks or opportunities that a future agent should be aware of.

Do not assume I can answer follow-up questions. Treat this as a one-shot review: you see the bundle and (optionally) the GitHub repo, you think hard, and you give me the most useful critique and refinements you can.
