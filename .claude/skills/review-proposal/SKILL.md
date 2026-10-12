---
name: review-proposal
description: Full review of a written proposal in proposals/<slug>.md. Runs human-reader, formal-checker, claim-auditor, positioning-reviewer, novelty-checker, academic-paper-critic, and fresh-eyes-reviewer in parallel, then returns fatal issues, fixable issues, and questions for the user. Does not edit. Use for a one-shot review. Use /polish to iterate with edits.
argument-hint: <proposals/<slug>.md>
---

Review: $ARGUMENTS

1. Read the proposal, `papers.md`, and relevant `landscape/*.md`.
2. Launch all seven in a single message so they run in parallel:
   - `human-reader`: reads once as the target human would, flags ambiguity, glossing, flow, over-detail, inconsistency, formal defects, plan concreteness.
   - `formal-checker`: brute-force checks grammar well-formedness and that every formula matches its stated meaning (give it the scratchpad directory).
   - `claim-auditor`: ambiguous terms, undefined concepts, unclear design, and every citation and number checked against its source.
   - `positioning-reviewer`: missing closest work, delta table, framing, implied baselines, venue.
   - `novelty-checker`: give it the proposal's core claim, not the whole file.
   - `academic-paper-critic`: logic, unsupported claims, evaluation validity, confounds (e.g. a gain that comes from longer context handling or turn counting rather than temporal instruction following).
   - `fresh-eyes-reviewer`: reads it cold and reports where it stops making sense.
3. Verify any new prior work or "WRONG" claim the agents report by fetching it yourself before accepting it.
4. In chat, at most 25 lines:
   - Fatal issues (would cause rejection), each with the agent that found it.
   - Fixable issues with the fix.
   - Questions for Daneshvar, merged and deduped from all agents, ranked by how much the answer changes the design. At most 6.
   - The one experiment that most strengthens the paper.
5. Edit the proposal only after the user answers or agrees.
