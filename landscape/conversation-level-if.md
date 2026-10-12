# Conversation-level (temporal) instruction following: landscape

Survey 2026-10-08, four lit-scout angles. Details per paper in `papers.md`.

## Taxonomy by temporal scope

| Cluster | Scope | Checker | Training | Papers |
|---|---|---|---|---|
| Multi-turn IF benchmarks, accumulating constraints | per-response predicate re-checked every turn | program (Multi-IF, MMMT-IF, CAPITU) or LLM judge (SEQUOR, SysBench, MultiChallenge, StructFlowBench) | none | 2410.15553, 2409.18216, 2603.22576, 2605.06353, 2408.10943, 2501.17399, 2502.14494, 2511.03508, 2401.16745 |
| Cross-turn memory / entangled instructions | earlier instruction must be applied later | rules or judge | none | 2503.13222 (recall near-perfect, application fails) |
| Persona / system-prompt drift | static persona over N turns | judge or probes | split-softmax (inference), reinjection prompting, multi-turn PPO with judge reward | 2402.10962, 2609.24532, 2605.24279, 2511.00222 |
| Prospective memory | deferred or triggered action | program (PM-Bench, 2603.23530), unclear (TriggerBench) | none (PIS scaffold is training-free) | 2607.12385, 2606.23459, 2603.23530, 2609.01272 |
| Multi-turn RL in conversation | information arrives in shards (Lost in Conversation) | program (final answer) | GRPO/PPO, 3B to 7B | 2505.06120, 2510.18731, 2603.04783, 2606.12941 |
| Temporal logic over LLM traces | LTL/MFOTL over tool-call traces | program monitor | inference-time shields; AgentLTL uses LTL as GRPO reward | 2607.02599, 2512.23738, 2503.18666, 2605.16198, 2610.09793 |

## Closest work

- **AgentLTL [2607.02599]**: FO-LTL spec over agent tool traces as a judge-free score and dense GRPO reward (Qwen3-4B LoRA, 300 template examples). Closest method. Scope is tool calls, not dialogue turns. Reported reward mixes in similarity to the gold tool sequence (not checked in full text).
- **MMMT-IF [2409.18216]**: program-checked global instructions ("use *like* in all future responses") over up to 20 turns. PIF drops 0.81 to 0.64. Appending instructions at the end recovers 22.3 points. Eval only, no schedules.
- **SEQUOR [2605.06353]**: up to 50 turns, constraints added and replaced, LLM judge, eval only.
- **PM-Bench [2607.12385], TriggerBench [2606.23459]**: prospective memory, agent/scenario tasks, eval only.
- **Abdulhai et al. [2511.00222]**: only RL targeting persistence across turns, but persona consistency with an LLM-judge reward.

## Reusable assets

- Multi-IF (HF facebook/Multi-IF, 4.5K 3-turn, IFEval checkers). MT-Eval (HF). SysBench, MultiTurnInstruct, MultiChallenge, PM-Bench (GitHub).
- IFEval/IFBench checkers for per-response predicates. MonPoly for MFOTL monitoring.
- Multi-turn RL: verl agent loop, OpenRLHF, TRL `environment_factory` (experimental). None ships a scripted-user conversation env.

## Solved vs open

- Solved/crowded: per-response constraints re-checked each turn, persona drift measurement, Lost-in-Conversation RL, LTL monitors for tool traces.
- Correction (novelty check 2026-10-08): LTL over dialogue traces exists as a guardrail (TemporalGuard/LLMrv, past-time only, NLI/LLM grounding, no IF eval). RuLES, MultiTurnInstruct, TriggerBench cover never-do, same-turn triggers, only-after. SEQUOR/MMMT-IF cover from-now-on and revocation.
- Open: program-checked IF benchmark with counting and future-time operators over turns: periodic, turn-counted deadlines, caps with m>=1, counting user events, triggers with delay windows, cumulative budgets and coverage. No training on any of these.
- Training method pieces are all known (AgentLTL, GLARE, MT-GRPO, first-error credit 2606.20068, LTL3 monitors). Doomed state is a DFA dead state except for arithmetic families, where SMT is needed.

## Candidate gaps (unchecked)

- G1. Counting and quantitative temporal families over dialogue turns, monitor-checked, plus SFT/RL on generator data with held-out families and horizons. (checked: PARTIALLY SCOOPED, families 1, 2, 7, 8 and caps m>=1 open)
- G2. Diagnostic: forgot vs miscounted vs never planned, using SMT to label the first doomed turn on budget/coverage families. Turn-index and reinjection wrappers as baselines. (checked as part of G1: most defensible delta)
- G3. Time-dependent conflicts and revocation: constraints that become jointly UNSAT only at a future turn, and "from now on" overrides. (unchecked)
