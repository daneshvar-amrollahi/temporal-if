---
name: idea
description: Write a research idea card in ideas/<slug>.md and run a novelty check on it. Use when a candidate direction has emerged from discussion and is worth pinning down.
argument-hint: <slug> [short description]
---

Idea: $ARGUMENTS

1. Draft the card from the discussion so far and show it in chat before writing.
2. Write `ideas/<slug>.md`:

```
# <Title>
Status: draft | checked | chosen | dropped

Problem: <a concrete temporal instruction, a 4 to 6 turn transcript where a current model breaks it, and why>
Property language: <which operators (always, every-k, after-n, until, triggered), turn indexing convention, what is checked (assistant text only?)>
Data: <where conversations come from, who plays the user, horizon in turns, SAT only or SAT plus UNSAT>
Checker: <program vs LLM judge, per property family>
Hypothesis: <falsifiable claim>
Method sketch: <3 to 5 bullets>
Minimal experiment: <smallest run that tests the hypothesis, models, data, metric, compute>
Closest prior work: <filled by novelty check>
Delta: <what we claim that they do not>
Kill criteria: <results that would make us drop it>
Venue fit: <target venue and why>
```

3. Run the `novelty-checker` agent on the card. Fill in "Closest prior work" and "Delta" from its output, set Status to `checked`, and report the verdict and reviewer attack in chat.
4. If the verdict is SCOOPED, say so plainly and suggest how to pivot, or drop it.
