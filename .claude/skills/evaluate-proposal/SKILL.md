---
name: evaluate-proposal
description: Evaluate one or more candidate research directions for novelty and feasibility before recommending any. Runs novelty-checker and feasibility-auditor on each in parallel, then gives a ranked recommendation. Use whenever choosing between directions or when the user asks "what do you recommend".
argument-hint: <idea descriptions or ideas/<slug>.md paths>
---

Evaluate: $ARGUMENTS

Criteria (from Daneshvar): prefer a training result, target AI/NLP venues, judge by feasibility (data, user simulation, checkers, compute), the gap must be real and not reinvented, the delta against multi-turn IF benchmarks, instruction-drift work, and single-turn IF-RLVR must be explicit, and every factual claim must be verified.

1. Write each candidate as a one-paragraph core claim: method, problem, expected result, evaluation.
2. For every candidate, launch `novelty-checker` and `feasibility-auditor` together, all in a single message.
3. Merge. Where the two agents disagree with each other or with `landscape/`, resolve it by fetching the source yourself.
4. Self-correct: list what changed from your prior belief and why.
5. Rank the candidates. A candidate that is SCOOPED or NOT FEASIBLE cannot be ranked first.
6. In chat, at most 25 lines: the recommendation, its pilot, the top 3 risks, and what was dropped and why. Record the decision in `decisions.md` only after the user agrees.
