---
name: polish
description: Iterate on a proposal until a human can read it in one pass. Each round runs human-reader, formal-checker, claim-auditor, and positioning-reviewer in parallel, applies the clear-cut fixes, and re-runs. Stops when human-reader says READY, when a round produces only nits, or after the round limit. Use when the user asks to make a proposal ready for reading, or after a large revision.
argument-hint: <proposals/<slug>.md> [max rounds, default 3]
---

Polish: $ARGUMENTS

The user has asked for the document to be iterated on, so edits are allowed in this skill. Design decisions are not: anything that would change what the project does goes to the user as a question.

Each round:

1. Read the proposal and `papers.md`.
2. Launch in a single message: `human-reader` (the whole file), `formal-checker` (give it the scratchpad directory), `claim-auditor` (citations, numbers, ambiguous terms), and `positioning-reviewer` (prior-work table and deltas). On the first round also launch `fresh-eyes-reviewer`.
3. Triage every item:
   - **Apply now:** wording, ordering, cuts, consistency fixes, wrong numbers, formula or prose corrections where the formal-checker's counterexample shows which side is wrong and the intent is clear, mislabeled table cells where the verified source says otherwise.
   - **Ask the user:** anything that changes the design (a family added or dropped, a data source, a metric, the scope of v1), anything where two agents disagree and the source does not settle it, and any cut of content the user wrote or asked for.
   - **Drop:** style preferences, praise, suggestions to add sections or detail the reader does not need.
4. Apply the fixes. Keep the document's size roughly constant or smaller. Never add a citation, tool name, number, or claim about prior work without fetching the source in this round. Never use semicolons or em dashes in prose.
5. Re-run the agents on the edited file. Stop when `human-reader` returns READY, when a round returns no Blocking and no Should-fix items that can be applied, or at the round limit.

Report in chat, at most 30 lines:
- Rounds run and the verdict trajectory (e.g. NOT READY -> NOT READY -> READY).
- What changed, grouped by section, one line each.
- Formal-checker result on the final version (every row PASS, or the FAILs that remain and why).
- Questions for the user, merged and deduplicated, at most 6, ranked by how much the answer changes the document.
- What was deliberately not changed and why.
