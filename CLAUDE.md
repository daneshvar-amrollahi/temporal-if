# Temporal (conversation-level) instruction following

Ideation project. Goal: one publishable AI/NLP paper (ACL, EMNLP, NeurIPS, ICLR, ICML) on instructions whose satisfaction is a property of the whole conversation, not of one response. Examples: "say *banana* every 5 turns", "remind me to stretch after 10 turns", "from now on never use the word *very*", "until I say stop, end each reply with a question", "after I mention a date, repeat it back in every later answer". Leaning toward a post-training result: show that RL (or SFT) on synthetic conversations with programmatic checkers improves this ability.

Phase: landscape. Daneshvar steers by asking questions. Claude proposes, sorts out details, and pushes back when an idea is weak.

## Context

- Self-contained project. Do not read sibling directories under `../` (e.g. `../instruction-following-fm/`). All context lives here.
- Core framing: a temporal instruction is a specification over the trace of turns (LTL-like: always, eventually, every-k, until, after). A Python monitor checks it. This makes synthetic data and rewards cheap.
- Every proposal must state its delta against (a) multi-turn IF benchmarks, (b) system-prompt adherence and instruction drift work, (c) prospective-memory and long-context recall work, (d) LTL / runtime monitoring of LLM agents, and (e) single-turn IF-RLVR.

## Layout

- `papers.md`: single source of truth for citations, one line per paper.
- `landscape/<subarea>.md`: survey notes per subarea.
- `ideas/<slug>.md`: idea cards. `proposals/<slug>.md`: full writeups.
- `experiments/<date>-<name>/`: pilots, each with a short README.
- `decisions.md`: dated log of what we settled and why.

## Writing rules for proposals (from Daneshvar's feedback)

- Motivate before you define. A symbol or concept appears only after the reader has seen why it is needed, ideally through a running example.
- A formalism must be what it says it is. A grammar has only terminals and nonterminals on right-hand sides. A formula's stated meaning is what the formula says. The `formal-checker` agent verifies this by execution.
- Calibrate. Not ten families with auxiliary functions and solver machinery no experiment uses, and not four rows a reviewer would call trivial. Every piece of machinery serves a stated experiment or the stated long-term plan (post-training with LTLf monitors).
- When a definition changes, every downstream section changes with it (tables, counts, examples, metrics).
- No detail that does not change a decision the reader must make at that point.

## Rules

- Never cite from memory. A paper enters `papers.md` only after its arXiv/ACL/OpenReview page was fetched. Otherwise tag it `[unverified]`.
- The field moves fast. Search 2025 and 2026 work before calling anything a gap.
- No idea is called "novel" until `novelty-checker` has run on it. No direction is recommended until `/evaluate-proposal` has run.
- Every proposal must say where the conversations come from (who plays the user, real vs synthetic), how the checker decides each property, and whether the property is checked on the model's own turns only.
- Answer in chat first. Write to files only once something is settled. Keep files short.

## Tools

- `/survey <subarea>`: parallel lit search, writes `landscape/`, updates `papers.md`.
- `/idea <slug>`: idea card plus novelty check.
- `/evaluate-proposal <ideas>`: novelty-checker plus feasibility-auditor per candidate, ranked recommendation.
- `/review-proposal <proposals/x.md>`: one-shot review, no edits. Human reader, formal checker, claim audit, positioning, novelty, hostile reviewer, fresh reader. Returns questions for Daneshvar.
- `/polish <proposals/x.md>`: iterate with edits until `human-reader` says READY. Applies clear-cut fixes, asks about design changes.
- Agents: `lit-scout`, `novelty-checker`, `feasibility-auditor`, `claim-auditor`, `positioning-reviewer`, `human-reader`, `formal-checker`. Global: `academic-paper-critic`, `fresh-eyes-reviewer`.
