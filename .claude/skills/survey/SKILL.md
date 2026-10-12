---
name: survey
description: Survey one subarea relevant to temporal, conversation-level instruction following. Fans out lit-scout agents in parallel, writes landscape/<subarea>.md, and updates papers.md. Use when the user asks to map, survey, or understand a subarea, or asks "what's out there".
argument-hint: <subarea>
---

Survey the subarea: $ARGUMENTS

1. Read `papers.md`, and any existing `landscape/*.md` so you do not redo work.
2. Split the subarea into 3 or 4 distinct query angles (benchmarks/data, training methods, adjacent communities such as formal methods or cognitive science, recent 2025 to 2026).
3. Launch one `lit-scout` agent per angle, all in a single message so they run in parallel.
4. Merge results. Dedupe against `papers.md`. Drop anything unverified unless it is clearly important, then tag it `[unverified]`.
5. Write `landscape/<subarea-slug>.md`, at most ~80 lines:
   - Taxonomy (how the work clusters), including a column for temporal scope: single response, per-turn constraints, cross-turn properties
   - Key papers per cluster (cite by id, details live in `papers.md`)
   - Released data and checkers we could reuse
   - What is solved, what is open
   - Candidate gaps (each one line, marked "unchecked" until novelty-checker runs)
6. Append new papers to `papers.md` as: `- [<id>] <Title> (<Author> et al., <venue> <year>). <one-line claim>. #<subarea>`
7. In chat, give a summary of at most 15 lines: the clusters, the 2 or 3 most promising gaps, and one question for the user.
