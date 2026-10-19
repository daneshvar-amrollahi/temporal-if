# Following Instructions Over Time: Stateful Instruction Following in Conversations

Draft v5, 2026-10-15. Target: ACL/EMNLP via ARR (main if Section 6 lands, Findings otherwise), or NeurIPS Datasets and Benchmarks. Section 6 (training) is a placeholder.

## 1. Summary

Some instructions cannot be checked on a single reply. "Every 5th reply, remind me to take a break." "In your 10th reply from now, say *save your work*." "Mention our newsletter exactly once." "Until I say *done*, answer only in lowercase." "The second time I say I'm stuck, give me a hint." To follow these, the assistant has to carry something across its own replies: a count of how many replies it has given, a count of how many times it has already acted or the user has said something, or a mode the user switched on and has not yet switched off. Program-checked multi-turn instruction-following benchmarks stop at standing rules ("in all future replies, do X": MMMT-IF, Multi-IF), their addition and removal (EvolIF), and triggers answered in the same reply (RuLES, MultiTurnInstruct, TriggerBench's rule-based check at the trigger turn). Retention over long contexts and the meaning of a triggered response are scored with an LLM judge (SEQUOR, MultiChallenge, TriggerBench's judge metric).

We call the missing capability *stateful instruction following* and build a benchmark and a training signal for it. The instructions come in three groups of patterns, each of which can be placed under a scope. Base patterns: always, never, at some point. Counting patterns, which count the assistant's own replies or actions: scheduled, periodic, exactly m times, at most m times. Trigger patterns, which react to what the user says: respond within a window after a trigger, respond to the m-th trigger. Scopes are opened and closed by the user: from a trigger, until a trigger. Every instruction is checked by a program, so each failure can be labeled (forgot, missed, or over-did) together with the reply at which it became unrecoverable. Temporal-logic monitors already exist for LLM tool traces and for blocking unsafe messages. None has been used to specify, measure, or train the following of natural-language instructions in dialogue.

The means is linear temporal logic on finite traces (LTLf), a logic for statements about finite sequences of events. Each pattern is an LTLf formula over the sequence of rounds (one user message plus the reply to it, Section 3.1), run on the part of the conversation its scope selects. The pattern catalog is adapted from Dwyer et al.'s property specification patterns and Konrad and Cheng's real-time extension. This buys an exact checker, and a monitor state (satisfied, violated, or open) after every reply, which is what later post-training with the checker as reward needs.

**Contributions (draft).**
1. A benchmark of stateful instructions: nine patterns under four scopes, inserted into real WildChat conversations of 11 or more user turns, with one to three instructions per conversation.
2. A per-instruction diagnosis (forgot, missed, over-did) with the first unrecoverable reply (Section 5).
3. The specification: a grammar, LTLf semantics, and a program checker with a monitor state after every reply (Section 3).
4. Post-training (SFT and/or RL) on generated data, tested on held-out pattern-scope combinations, held-out paraphrases, and longer conversations than trained on. [TBD]

## 2. Prior work and how we differ

The three middle pattern columns are the three pattern groups of Section 3.2, and the fourth is scopes. The existence pattern ("at some point, do X") has no column because no row studies it. A cell is ✓ when the paper studies that kind of rule over the conversation, ~ when it appears in a weaker form (three to five turns, a trigger answered in its own reply only, or a related construct), ✗ otherwise. Cells describe what the paper studies, not what its formalism could express. The Checker column says how compliance is decided. Turn counts are as each paper reports them, and papers differ on whether a turn is one message or a user-assistant pair.

| Work | Setting | Base patterns (always, never) | Counting patterns (scheduled, periodic, exactly m, at most m) | Trigger patterns (window after a trigger, m-th trigger) | Scopes the user opens or closes | Checker | Training |
|---|---|---|---|---|---|---|---|
| Multi-IF [2410.15553] | dialogue, 3 turns | ~ (constraints accumulate over 3 turns) | ✗ | ✗ | ✗ | program | none |
| MMMT-IF [2409.18216] | image QA dialogue, ≤20 turns | ✓ (global instructions) | ✗ | ✗ | ✗ (modifying instructions is future work) | program | none (RL with their metric as reward is future work) |
| SEQUOR [2605.06353] | dialogue, 50 turns | ✓ | ✗ | ✗ | ~ (constraints replaced every 5 or 10 turns) | LLM judge | none |
| EvolIF [2511.03508] | dialogue, simulated user | ✓ | ✗ | ✗ | ~ (constraints added and deleted, only the current set is scored) | program + LLM judge | none |
| MultiChallenge [2501.17399] | dialogue, ≤10 turns | ~ (instruction retention) | ✗ | ✗ | ✗ | LLM judge | none |
| SysBench [2408.10943] | dialogue, 5 turns | ~ (system rules, 5 turns) | ✗ | ✗ | ✗ | LLM judge | none |
| RuLES [2311.04235] | dialogue, rule games | ✓ (never reveal) | ✗ | ~ (same reply only, rules are stateless) | ✗ | program | SFT (on Basic-suite-like data) |
| MultiTurnInstruct [2503.13222] | dialogue | ~ (privacy rule) | ✗ | ~ (recurring trigger, same reply) | ✗ | BLEU + exact match | SFT on generic data, no gain |
| RealGuardrails [2502.12197] | mostly single-turn, some multi-turn | ✓ | ✗ | ✗ | ~ (judge-scored unlock-on-phrase) | LLM judge + string checks | SFT + DPO |
| TriggerBench [2606.23459] | dialogue, 40K tokens (100K scaling study) | ~ (standing policies) | ✗ | ~ (same reply, incl. "only after" and clock times) | ✗ | LLM judge + rule-based slot match | none |
| PM-Bench [2607.12385] | agent, simulated week | ✗ | ~ (routines on a clock, not reply counts) | ✗ (environment events) | ~ (cancels and overrides) | program | none |
| TemporalGuard [SAIV 2026] | dialogue guardrail | ✓ | ✗ (not studied) | ~ (same reply) | ~ (via past-time operators) | NLI or LLM grounding of atoms | none (runtime blocking) |
| AgentLTL [2607.02599], GLARE [ICML 2026] | tool-call and agent-action traces | ✓ (over tool calls and actions) | ~ (AgentLTL counts tool calls) | ✗ (no user turns) | ✗ | program | RL (GRPO) |
| Persona RL [2511.00222] | dialogue, up to 60 turns | ~ (persona consistency) | ✗ | ✗ | ✗ | LLM judge | RL (PPO) |
| RLAAR [2510.18731], RLSTA [2603.04783] | dialogue, task revealed in pieces | ✗ | ✗ | ✗ | ✗ | program (final answer) | RL |
| IF-RLVR (RL with verifiable instruction rewards): IFBench [2507.02833], VerIF [EMNLP 2025] | constraint checked on one reply (IFBench has a 3-turn variant) | ✗ | ✗ | ✗ | ✗ | program (VerIF adds an LLM for soft constraints) | RL (GRPO), incl. IFBench's IF-RLVR-multi |
| **Ours** | dialogue, real conversations, 11+ user turns | ✓ | ✓ | ✓ | ✓ | program (LTLf monitor) | SFT / RL [TBD] |

In one line: prior benchmarks test whether a standing rule still holds in each reply or whether a trigger is answered in its own reply, and the judge-scored ones add retention and replacement. We add rules that count the assistant's own replies, and we put response windows after a trigger, counted triggers, and user-opened scopes under a program checker, then train on them. Prior temporal-logic work on LLMs monitors tool traces (AgentLTL, GLARE, and the inference-time Agent-C [2512.23738] and ContrAgent [2609.18128]), blocks unsafe messages (TemporalGuard), or checks rule-based chatbots against interaction protocols (RV4Chatbot [2411.14368]). We use it to specify, measure, and train the following of natural-language instructions in dialogue.

Against the rows of the table: always and never appear under a program checker (MMMT-IF, Multi-IF, RuLES), existence appears nowhere, triggers answered in their own reply appear under a program checker (RuLES, MultiTurnInstruct, TriggerBench's slot match), and scopes appear judge-scored (SEQUOR, RealGuardrails), scored on the current rule set only so that releasing a rule is never tested (EvolIF), as past-time operators in a guardrail (TemporalGuard), or in agent settings (PM-Bench). The four counting patterns, response windows longer than the trigger's own reply, repeated and counted triggers, and user-opened scopes whose release is checked appear in no dialogue row under a program checker. TriggerBench's prompts contain a do-not-repeat-the-reminder instruction, but it is not scored.

## 3. Instructions as temporal specifications

"Every 2nd reply, remind me to drink water" is informal text. To build a benchmark from instructions like it we need, for each one, a formal version that a program can generate with chosen parameters, render into text, and check on a finished conversation. The formalism should also serve the later goal of this project, post-training with the checker as the reward (Section 6), which needs a monitor state after every reply, not only a verdict at the end. LTLf (De Giacomo and Vardi 2013) fits both needs: every LTLf formula compiles to a deterministic finite automaton that reads the conversation one round at a time. We therefore write each pattern as an LTLf formula over the sequence of rounds and run it on the part of the conversation its scope selects. To choose which instructions to study, we adapt the property specification patterns of Dwyer et al. (1999), the standard catalog of temporal properties in verification, and two patterns from Konrad and Cheng's (2005) real-time extension of it. A *pattern* says what must happen (always, never, exactly m times, in response to a trigger, and so on) and a *scope* says during which part of the conversation it applies (globally, from a trigger on, until a trigger).

This section fixes what a conversation is and how replies are counted (3.1), gives the grammar of instructions (3.2), and states the meaning of each instruction both as an LTLf formula and in plain terms (3.3). Section 4 explains how instructions are inserted into real conversations.

### 3.1 What a conversation is, and how we count

A conversation alternates between the user and the assistant. The user writes a message, the assistant replies, the user writes again, and so on. We call one user message together with the assistant's reply to it a **round**. A conversation with `T` rounds is

```
C = (sys, (u_1, a_1), (u_2, a_2), ..., (u_T, a_T))
```

where `sys` is the system prompt (possibly empty), `u_i` is the user's `i`-th message, and `a_i` is the assistant's reply to it.

**Running example.** A student gets homework help over `T = 8` rounds. Each `u_i` is a question. The third message opens with an instruction:

> `u_3`: "From now on, every 2nd reply, remind me to drink water. Now: how do I factor x² - 5x + 6?"

The assistant answers with `a_3`, the student asks `u_4`, the assistant answers `a_4`, and so on through `a_8`.

**Issue round.** Every instruction `φ` enters the conversation at some round, which we call its issue round `s`. The water instruction is stated in `u_3`, so `s = 3`. If the same instruction were written in the system prompt instead, it would be in force from the start, so `s = 1`. Nothing before round `s` is checked against `φ`. The assistant cannot be expected to follow an instruction it has not seen yet.

**Reply numbers are counted from the instruction, not from the start of the chat.** When the student says "every 2nd reply", they are counting from the moment they gave the instruction. So each instruction gets its own numbering of replies. Reply number `r` of instruction `φ` is the assistant message `a_{s+r-1}`. In words: `a_s`, the reply to the message that contains the instruction, is reply 1, the next one is reply 2, and so on. For the water instruction, `s = 3`, so `a_3` is reply 1, `a_4` is reply 2, up to `a_8`, which is reply 6. "Every 2nd reply" means replies 2, 4, 6, which are `a_4`, `a_6`, `a_8`. Triggers are things the user says, so they happen at rounds `i`, and `r = i - s + 1` converts a round to a reply number.

| round `i` | user message `u_i` | water-instruction reply `r` | must mention water? |
|---|---|---|---|
| 1 | question | not yet issued | no check |
| 2 | question | not yet issued | no check |
| 3 | "every 2nd reply, remind me to drink water" + question | 1 | no |
| 4 | question | 2 | **yes** |
| 5 | question | 3 | no |
| 6 | question | 4 | **yes** |
| 7 | question | 5 | no |
| 8 | question | 6 | **yes** |

Whether `a_3` or `a_4` counts as reply 1 is a convention. What matters is that the instruction text leaves no doubt, because a model that counts the other way misses every target by one. Our renderings therefore spell the targets out with a fixed clause, "in your 2nd, 4th, 6th, ... reply from now, counting your very next reply as the 1st", which is never paraphrased (Section 4).

**Horizon.** The instruction governs `R = T - s + 1` replies. For the water instruction, `R = 8 - 3 + 1 = 6`. The generator only produces instructions whose targets and trigger windows fit inside the conversation. For instance, "in your 3rd reply from now" issued at `s = 7` would need a reply `a_9`, which does not exist in an 8-round conversation, so the generator never places it there. Every instruction can therefore be satisfied.

**Only assistant replies are judged.** User messages are never scored. They matter in one way: they can contain trigger phrases, which the trigger patterns react to and which open or close scopes (Section 3.2). A conversation may also carry several instructions. If the system prompt had said "in your 5th reply, say *save your work*", that would be a second instruction with its own issue round `s = 1` and its own reply numbering, checked on `a_5`, independent of the water instruction.

### 3.2 Grammar

An instruction asks for an *action* in certain replies. An action is something one reply either does or does not do: include a given phrase, or satisfy a given format. A *trigger* is something one user message either contains or does not: a given phrase. Which replies the action is required in is decided by a pattern and a scope. Comments to the right of a production are side conditions.

```
Instr   ::= Pattern Scope

Pattern ::= ALWAYS Act                     universality
          | NEVER Act                      absence
          | EVENTUALLY Act                 existence
          | AT Num, Act                    scheduled
          | EVERY Num, Act                 periodic
          | EXACTLY Num TIMES, Act         bounded existence
          | AT MOST Num TIMES, Act         bounded existence
          | Act WITHIN Win OF Trig         response with window
          | Act AFTER Num TIMES Trig       counted response

Scope   ::= GLOBALLY | FROM Trig | UNTIL Trig | FROM Trig UNTIL Trig

Act     ::= SAY Phrase | USE Fmt
Trig    ::= USER SAYS Phrase
Fmt     ::= LOWERCASE | NO_COMMAS | BULLET_LIST | ENDS_WITH_QUESTION
Phrase  ::= '"' Word (' ' Word)* '"'      one to four words
Word    ::= Letter+
Num     ::= Digit+                        value at least 1
Win     ::= 0 | Num
Digit   ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
Letter  ::= a | b | c | d | e | f | g | h | i | j | k | l | m | n | o | p | q | r | s | t | u | v | w | x | y | z
```

`SAY p` holds for a reply iff the words of `p` occur in it consecutively, each delimited by non-letters, case-insensitive, so punctuation and markup around the phrase do not matter. `USER SAYS t` holds for a user message in the same way. Matching is literal, so an acknowledgement that echoes the phrase ("Got it, I'll say *drink water* every 2nd reply") would count as the action. Chat models acknowledge by default, and that would swamp the counting diagnosis. In v1 the checker therefore exempts reply 1 of an instruction issued in a user message from `SAY` checks, for every pattern except `ALWAYS`, whose formula requires the action there. The echo rate at reply 1 is reported separately (Section 5), and whether to score it as a violation is Section 7, question 3. Instructions that state an intent without naming a phrase ("remind me to stretch") are out of scope for v1 (Section 7). `USE f` holds iff the reply has the format `f`: `LOWERCASE` and `NO_COMMAS` are IFEval's checkers (`NO_COMMAS` also rejects the full-width comma `，`, since some conversations switch to Chinese), `BULLET_LIST` holds iff at least two lines start with `-`, `*`, or a number followed by a period, and `ENDS_WITH_QUESTION` holds iff the last non-space character is `?`. The grammar admits `USE` under every pattern, but the generator uses format actions only with `ALWAYS` (any format) and `NEVER` (`BULLET_LIST` and `ENDS_WITH_QUESTION` only), because a short reply can satisfy a format by accident, which would make any pattern that requires or forbids a format at particular replies noisy, and "never lowercase" or "never without commas" would be degenerate.

The nine patterns form three groups. The *base patterns* `ALWAYS`, `NEVER`, and `EVENTUALLY` are Dwyer's universality, absence, and existence. The first two are what prior multi-turn benchmarks check, and existence appears in no prior row of Section 2. The *counting patterns* require the assistant to count its own replies or actions: a fixed reply (`AT`), a period (`EVERY`), or the number of times it has performed the action (`EXACTLY`, `AT MOST`). `EXACTLY` and `AT MOST` adapt Dwyer's bounded existence to count replies in which the action holds rather than program states. `EVERY` tightens Konrad and Cheng's bounded recurrence ("at least every k") to an exact period, and `AT` is ours. The *trigger patterns* react to the user: respond to every trigger within a window (`WITHIN`), or respond to the `m`-th trigger (`AFTER m TIMES`). `WITHIN` is Konrad and Cheng's bounded response, and `AFTER m TIMES` is ours. The scopes are four of Dwyer's five. `GLOBALLY` means from the issue round to the end, `FROM t` from the first user message containing `t` (that round included), `UNTIL t` up to the first user message containing `t` (that round excluded), and `FROM t UNTIL t'` between the two. Section 3.3 makes this exact.

The water instruction of Section 3.1 is `EVERY 2, SAY "drink water" GLOBALLY`. "Until I say done, answer in lowercase" is `ALWAYS USE LOWERCASE UNTIL USER SAYS "done"`. "Don't mention the premium plan before I say I'm interested" is `NEVER SAY "the premium plan" UNTIL USER SAYS "interested"`, which is Dwyer's precedence pattern expressed through a scope.

### 3.3 Semantics

**Traces.** Fix an instruction with issue round `s` in a conversation of `T` rounds. Its trace is the sequence of positions `r = 1, ..., R` with `R = T - s + 1`, position `r` standing for round `s + r - 1` as in Section 3.1. Each position is labeled with one atomic proposition for the action and one per trigger phrase the instruction names: `a` is true at `r` iff the assistant's reply of that round performs the action (except at reply 1 of a user-issued `SAY` instruction other than `ALWAYS`, where `a` is false by the exemption of Section 3.2), `u` iff the user message of that round contains the pattern's trigger phrase, and `o` and `c` iff it contains the scope's opening and closing phrase. No phrase of an instruction is a substring of another, so the propositions are independent. Each instruction has its own trace and its own propositions.

**LTLf.** Formulas are built from the propositions, Boolean connectives, and the temporal operators `X φ` (φ at the next position), `N φ` (weak next: `X φ`, except true at the last position), `F φ` (φ at some position from here on), `G φ` (φ at every position from here on), `φ U ψ` (until), and `φ W ψ` (weak until, `G φ ∨ φ U ψ`). `X^j` and `N^j` are `X` and `N` applied `j` times, and `F≤w φ` abbreviates `φ ∨ X φ ∨ ... ∨ X^w φ`. A trace satisfies a formula under the usual finite-trace semantics (De Giacomo and Vardi 2013), read from position 1.

**Patterns under the GLOBALLY scope.** The examples are real instructions, abridged, with their sources and more examples in [real-world-examples.md](../real-world-examples.md). Real instructions are often looser than the formula beside them (the audit prompt never says "and only then"); the benchmark's own renderings, which state the exact pattern, are in Section 4.

| Pattern | LTLf formula | Satisfied iff | Real example (abridged) |
|---|---|---|---|
| `ALWAYS a` | `G a` | `a` at every position | "At the end of every direct answer, always tell the user *If you'd rather talk to a human agent just ask me directly*." (Intercom Fin guide) |
| `NEVER a` | `G ¬a` | `a` at no position | "From this point forward, do not use any em dashes (—) in your writing under any circumstance." (OpenAI forum) |
| `EVENTUALLY a` | `F a` | `a` at some position | "If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email." (public chatbot prompts) |
| `AT n, a` | `(∧_{j=0}^{n-2} X^j ¬a) ∧ X^{n-1}(a ∧ N G ¬a)` | `a` at position `n` and nowhere else | "Walk users through a 5-question audit ... After Q5, you MUST deliver the audit." (deployed app prompt) |
| `EVERY k, a` | `S_k ∧ G(a → S'_k)`, where `S_k = (∧_{j=0}^{k-2} N^j ¬a) ∧ N^{k-1} a` and `S'_k = (∧_{j=1}^{k-1} N^j ¬a) ∧ N^k a` | `a` at exactly the positions divisible by `k` | "Lulu, can you perhaps just react to everd third message in the chat?" (WildChat, typo in original) |
| `EXACTLY m TIMES, a` | `E_m`, where `E_1 = ¬a U (a ∧ N G ¬a)` and `E_j = ¬a U (a ∧ X E_{j-1})` for `j ≥ 2` | `a` at exactly `m` positions | "Tell the user exactly once per conversation ... Once per conversation means once." (agent skill) |
| `AT MOST m TIMES, a` | `B_m`, where `B_0 = G ¬a` and `B_j = ¬a W (a ∧ N B_{j-1})` | `a` at at most `m` positions | "Offer the nudge at most once in a conversation." (Anthropic skill) |
| `a WITHIN w OF t` | `G(u → F≤w a)` | for every position `i` with `u`: `a` at some position in `i, ..., i + w` (the generator keeps `i + w` inside the segment) | "Every time the user types *What can I do here?* ..." followed by a fixed menu (custom GPT, `w = 0`) |
| `a AFTER m TIMES t` | `C_m`, where `C_1 = (¬a ∧ ¬u) W (u ∧ a)` and `C_j = (¬a ∧ ¬u) W (u ∧ ¬a ∧ N C_{j-1})` | no `a` before the `m`-th `u`, and `a` at the `m`-th `u`. If `u` occurs fewer than `m` times, no `a` at all. After the `m`-th `u`, `a` is unconstrained | "Offer to route the customer to a human agent if they ask the same question twice." (Intercom Fin guide) |

Three remarks. First, what a constant policy achieves. A model that performs the action in every reply passes `ALWAYS`, `EVENTUALLY`, and `WITHIN`. A model that never performs it passes `NEVER` and `AT MOST`, and passes `AFTER m TIMES` only when the `m`-th trigger never comes. Neither passes `AT`, `EVERY`, or `EXACTLY`, and neither passes `AFTER m TIMES` when the `m`-th trigger occurs, because these demand the action at certain replies and forbid it at others (the generator keeps `k ≥ 2` and `m` below the segment length `L`, since `EVERY 1` and `EXACTLY L` are `ALWAYS` and `AT MOST L` constrains nothing). The renderings of `AT` and `EVERY` say so (the nowhere-else clause, Section 4). Whether `WITHIN` and `EVENTUALLY` should also forbid the action outside the required replies is an open design choice (Section 7). Second, every formula in the table is independent of the conversation length, so one automaton per instruction serves any `T`. `EVERY` reads: the first action is at position `k` and none before, and every action is followed by `k - 1` positions without the action and then one with it, where the weak next `N` lets the trace end anywhere. Third, `EXACTLY`, `AT MOST`, and `AFTER m TIMES` nest a one-occurrence formula `m` deep, which is where the counting lives. `EXACTLY` uses strong `X` between occurrences so that an action at the last position cannot stand in for the missing ones.

**Scopes.** A scope restricts the positions at which the pattern is evaluated. `GLOBALLY` is the whole trace. `FROM t` is the suffix starting at the first position where `o` holds, that position included. `UNTIL t` is the prefix of positions strictly before the first position where `c` holds. `FROM t UNTIL t'` is the segment from the first `o` up to, but not including, the first `c` after it. The generator always places the scope triggers, with `c` strictly after `o`, so a segment is never empty and the cases where a trigger never occurs do not arise. The pattern is evaluated on the segment as a trace of its own, renumbered from 1, so under `FROM t` reply 1 of the pattern is the reply to the message that contains the opener. The checker runs the pattern's automaton on the segment: it starts at the first round where `o` holds, reads one round per step, and stops before the first `c` or at the end of the conversation. For `FROM t` this is the LTLf formula `¬o W (o ∧ φ)`, and for `ALWAYS` and `NEVER` under `UNTIL t` it is `a W c` and `¬a W c`. Our scopes match Dwyer's "after Q" and "before R", except that `FROM t UNTIL t'` takes the first segment only, where Dwyer's "between Q and R" repeats at every `Q`.

**What the checker returns.** Each pattern's automaton is run on the segment alongside a count of the positions remaining. `T` is the length of the base conversation, so the checker knows `R` and the segment length. After every reply the checker is in a definite state: satisfied (every continuation satisfies the formula), violated (none does), or open. The benchmark of this paper uses the final verdict and the *first unrecoverable reply*, the first reply after which the state is violated, reported in the instruction's own reply numbering (from the issue round, Section 3.1), whatever the scope. For `EVERY 2` under `GLOBALLY` with the action missing at reply 4, that is reply 4. For `EXACTLY 3` with one action by reply `R - 1`, that is reply `R - 1`, after which only one position remains. The model is not told `T` (Section 4), so for `EXACTLY` and `EVENTUALLY` this is the reply at which the model's behavior committed it to failure, not a reply at which it could have known. Section 6 uses the per-reply state.

## 4. Inserting instructions into real conversations

We do not write conversations. We take real multi-turn conversations, keep their user messages, throw away the original assistant replies, and insert instructions and trigger phrases into the user messages. Assistant replies are produced by the model under test at evaluation time, and by the policy being trained at training time. The checker knows at which round each instruction and trigger was inserted, and checks only the new replies. The running example (`T = 8`, water instruction at round 3) is built as follows.

**Base conversations.** The user messages `u_1, ..., u_T` are the user turns of one real conversation, in their original order, so `T` is that conversation's number of user turns. Discarding the original replies has one cost: a real user may refer back to them ("that code throws an error on line 5"), and such a turn makes no sense after a different reply. We therefore keep only conversations in which no user turn assumes particular content of an earlier reply, so the conversation stays meaningful whatever the model writes. Turns such as "make it shorter" refer to a reply but make sense after any reply, and are kept. In v1 the model is not told `T` (Section 7).

**Sources.**

| Dataset | Use | Why |
|---|---|---|
| [WildChat-4.8M](https://huggingface.co/datasets/allenai/WildChat-4.8M) | train, dev, test | Largest pool of long English chats (18.0K with at least 11 user turns). ODC-BY, ungated, so the benchmark can be released. A hashed user ID per conversation allows a split by user. |
| [ShareGPT-90K](https://huggingface.co/datasets/liyucheng/ShareGPT90K) | train only, if needed | 9.2K English chats with at least 11 user turns, but no license on the card and no user IDs, so it never enters dev or test. |

Not used: [LMSYS-Chat-1M](https://huggingface.co/datasets/lmsys/lmsys-chat-1m) (license forbids redistribution), [ShareChat](https://huggingface.co/datasets/tucnguyen/ShareChat) (CC BY-NC, gated), roleplay sets such as PIPPA and Chai (an inserted instruction breaks the fiction), BlenderBot 3x (small talk whose user turns react to the bot), and smaller crawls and mirrors (copies or subsets of the above). English only.

**Pipeline**, in this order.
1. Rules: at least 11 user turns, English by WildChat's conversation-level tag (conversations that switch language in some turns are kept), no empty user turn, and at most 24K tokens for the original transcript under the Qwen3-8B chat template. Qwen3-8B, the model we train (Section 6), has a native window of 32,768 tokens for input and output together, and the 8K margin covers regenerated replies longer than the originals, the inserted instruction text, and the reply being generated. No dedup: the 4 exact duplicates each come from one user, so step 3 keeps both copies in the same split.
2. An LLM judge labels each user turn, given only the assistant reply right before it. `NONE`: no reference to an earlier reply. `GENERIC`: refers to a reply but makes sense after any reasonable one ("make it shorter", "continue"). `SPECIFIC`: assumes something particular an earlier reply said ("line 5 throws an error", "why did you pick Python?", "go back to your first suggestion"). The judge also quotes the words that show the reference, and a program checks that the quote occurs in the user turn. A conversation is dropped at its first `SPECIFIC` turn. One short input per call keeps the judge from confusing turns, which a full history would invite at about 15 times the cost. Validation: a human labels 100 turns blind to the judge with the same guide, and we report agreement and Cohen's kappa. Bias checks: first user turns should come out `NONE`, about 50 planted `SPECIFIC` turns must be caught, and the judge's `SPECIFIC` rate is compared with the human one. Judge model [TBD], chosen as the cheapest candidate that meets the agreement bar on the 100 labels.
3. Split by WildChat's hashed user ID, so no user appears in two splits. Some users have dozens of near-identical chats, so a split by conversation would leak.
4. Insert instructions separately within each split (rest of this section).

**Splits**, counted in base conversations.

| Split | Size | Why |
|---|---|---|
| Test | 1,000 | A pass rate is then within about ±3 points (95%). Stratified by length: 11 to 19, 20 to 29, and 30+ user turns. Untouched until final runs. |
| Dev | 500 | About ±4.4 points. Used to tune the judge prompt, templates, and checkers. |
| Train | the rest | One conversation can carry several different insertions, so training examples outnumber base conversations. |

The generator draws training data from train conversations only, and the test set is fixed and versioned, so others can generate their own training data without touching it. Counts for every step are in the [TempoIF repo's DATA.md](https://github.com/daneshvar-amrollahi/TempoIF/blob/main/DATA.md). Expected yield after step 2 [estimate]: in 40 hand-read conversations, about 40% had no reference to a reply at all, a lower bound since `GENERIC` turns are now kept.

**Instructions.** We sample one to three instructions, each a pattern and a scope drawn from the grammar (uniformly over the admissible pattern-scope pairs [provisional]), then, in this order. First the placement: the system prompt (then `s = 1`) or a user message, each with probability one half [provisional], and in the second case the issue round `s`, uniform over the rounds that leave room for the scope triggers and a segment of at least two replies. Then the scope-trigger rounds, which fix the segment length `L` (`L = R` for `GLOBALLY`). Then the parameters, which must fit the segment: `2 ≤ n ≤ L`, `2 ≤ k ≤ L/2` so that at least two periods occur, `m < L` for `EXACTLY`, `AT MOST`, and `AFTER m TIMES`, and `0 ≤ w ≤ 2` for `WITHIN` [provisional]. The instruction text goes into the system prompt or is prepended to `u_s`. Action and trigger phrases come from a fixed list of short lowercase phrases chosen to be unlikely in a natural answer to any user message (for example *drink water*, *save your work*, *the premium plan*, *stuck*, *i give up*). Within one conversation, no two instructions share a phrase or a format, and no phrase is a substring of another, so the instructions constrain disjoint propositions and can be satisfied independently. Phrases are drawn so that none already occurs in a user message of the base conversation.

**Triggers.** `WITHIN`, `AFTER m TIMES`, `FROM`, and `UNTIL` need user messages containing a trigger phrase at chosen rounds. Scope triggers are placed strictly after `s`, with `c` strictly after `o`. Pattern triggers are placed strictly after the first round of their segment (so a trigger never shares a message with the instruction or the opener), leaving room for windows (`WITHIN w` needs each trigger at a round at most `w` before the last round of its segment). A short sentence containing the phrase is prepended to the chosen user messages ("I'm stuck on this one. " + request). Provisional counts: `WITHIN` gets one to three triggers, `AFTER m TIMES` gets exactly `m` triggers in most instances and `m - 1` in some (to test that the model waits for the `m`-th), and each scope trigger occurs once. No trigger phrase appears anywhere else, by the previous step.

**Rendering.** Each pattern and each scope has templates. Three kinds of clause are fixed text and are never paraphrased. The counting clause, for `AT` and `EVERY`, spells out the target replies and the anchor: "in your 2nd, 4th, 6th, ... reply from now, counting your very next reply as the 1st" under `GLOBALLY` and `UNTIL`, and "counting your reply to the message where I say *begin* as the 1st" under `FROM` and `FROM ... UNTIL`. The "nowhere else" clause, for `AT` and `EVERY`, is "and do not use that phrase in any other reply", with "before I say *done*" appended under a closing scope since the checker reads nothing after the closer, and `AFTER m TIMES` carries "and not before that". The scope clause states the boundary convention: "starting with your reply to the message where I say *begin*" and "your reply to the message where I say *done* no longer needs to". The rest of the template is paraphrased by an LLM, and the paraphrase is kept only if a second LLM, shown the grammar, parses it back to the identical instruction. Otherwise the template is used. Models [TBD]. In the example, `u_3` becomes: "From now on, remind me to drink water by saying "drink water" in your 2nd, 4th, 6th, ... reply from now, counting your very next reply as the 1st, and do not use that phrase in any other reply. Now: how do I factor x² - 5x + 6?"

**Satisfiability.** By construction: every instruction whose parameters fit its segment and whose triggers are placed can be satisfied on its own, and the instructions of one conversation constrain disjoint propositions. No solver is needed.

## 5. Evaluation

- **Models.** Frontier closed models and open 4B to 8B models [list TBD].
- **Metrics.** Instruction accuracy (the instruction's final verdict is satisfied) and conversation accuracy (all its instructions satisfied), broken down by pattern, scope, parameter (`k`, `n`, `m`, `w`), conversation length `T`, number of instructions per conversation, and placement (system prompt vs user message). Distribution of the first unrecoverable reply, in the instruction's own reply numbering.
- **Diagnosis.** Each failed instruction gets one label, the first that applies, computed on the trace of Section 3.3 (so with reply 1 of a user-issued `SAY` instruction already exempted). *Forgot*: `a` holds nowhere in the segment. *Over-did*: `a` holds at more positions than the pattern allows (`NEVER`: any, `AT MOST` and `EXACTLY`: more than `m`, `AT` and `EVERY`: more than the number of targets, `AFTER m TIMES`: any before the `m`-th trigger). *Missed*: `a` holds, but at the wrong positions or too few times. For the counting patterns a miss is a miscount. The three labels are exhaustive. Separately, the *echo rate*: the fraction of user-issued `SAY` instructions whose reply 1 contains the phrase.
- **Baselines without training.** Deployment wrappers: the absolute round number `i` added to each user message, the active instructions restated each round with their targets given as absolute round numbers (so the count is not re-anchored), all active instructions appended to the end of the context (MMMT-IF's fix, worth 22.3 points there), a free-text scratchpad the model updates each round in a channel the user does not see and the checker strips before matching, and an oracle-state wrapper that injects the checker's state each round ("this is reply 4 of the water instruction, you have said the phrase once"). The oracle separates failing to track from failing to comply, and is the dialogue analog of Typed Intention Stores [2609.01272], a training-free memory scaffold that raises PM-Bench F1. Inference-time methods from RealGuardrails: classifier-free guidance, and split-softmax from Li et al. [2402.10962]. An LLM judge in place of the program checker on the final verdict, with per-pattern agreement reported, to justify program checking (judge model and prompt [TBD]).
- **Trained baselines for Section 6.** A model trained with IFBench's IF-RLVR recipe on its three-turn format, to show that per-reply rewards do not buy cross-reply state. SFT and DPO on persistent-rule data as in RealGuardrails, to show that fixing standing rules does not fix counting.

## 6. Post-training [placeholder]

Scope: a demonstration that the checker works as a training signal, not the paper's main claim. LoRA SFT and RL on Qwen3-8B on one H100 (full fine-tuning with Adam needs about 130 GB). Other post-training methods are left to users of the benchmark.

- 6.1 SFT. [TBD: targets, e.g. rejection sampling against the checker, data size, model]
- 6.2 RL. [TBD: algorithm, rollouts with fixed user turns, reward from the checker. Arms to compare: final verdict only (sparse, kept as a control since a dense shaping reward collapsed GRPO when its within-group variance vanished under std normalization [2607.21273]), per-reply checker state as turn-level credit (MT-GRPO [2505.11821]), automaton-progress reward as in GLARE, per-constraint decomposition as in AgentLTL's compliance score, LLM-judge reward as in Persona RL]
- 6.3 Whether SFT and RL are combined or reported separately. [TBD]
- 6.4 Transfer and regression. [TBD: held-out pattern-scope combinations, held-out paraphrases, held-out `T`, Multi-IF, MMMT-IF, IFEval]

## 7. Open questions

1. Should `WITHIN` and `EVENTUALLY` forbid the action outside the required replies, as `AT` and `EVERY` do? For `WITHIN` with `w > 0` this needs a formula unrolled over the window `w` (past-time operators would shorten it but add no expressive power).
2. Should the model be told `T`? If not, `EVENTUALLY` and `EXACTLY` are best served by acting early, and `EVENTUALLY` may be too easy to keep.
3. Reply 1 of a user-issued `SAY` instruction is exempt from the phrase check in v1, and the echo rate is reported separately. Should the echo be scored as a violation instead? That is the stricter reading of the instruction, but it would dominate the failure counts for chat models that acknowledge by default.
4. Lengths beyond the real tail. Only 434 English WildChat conversations have 50+ user turns before the judge, so testing much longer conversations would need stitching. Needed or not?
5. Grounding (done for existence, not frequency). Every pattern and scope has verified real uses in system prompts, vendor prompt guides, user requests, chat logs, and laws ([real-world-examples.md](../real-world-examples.md)). The thin ones are `AT` (mostly quiz and audit flows), `EXACTLY` with free placement, and `WITHIN` with `w > 0`. Real triggers and actions are mostly semantic, so our literal phrases are a controlled subset. Still open: how often each pattern occurs, e.g. by mining WildChat.
6. Intent-only renderings ("remind me to drink water" without naming the phrase) need a lenient check such as a keyword set. Evaluation only, or also a reward?
7. Quantitative instructions that LTLf cannot express compactly, such as a word budget across replies, need arithmetic constraints and a solver. Left out of v1.

## Appendix: record format for the generator

```
{ id, T, system, source, source_id, user_hash,
  rounds: [{i, user, triggers: [phrase, ...]}],
  instructions: [{id, pattern, scope, params, issue_round, placement, text}],
  split }
```
8. Users mostly write `EVERY` as a bounded gap ("at least once every 5 turns"), not an exact period. Add it as a pattern?
9. The most common real `AT` is `n = 1` ("disclose that you are an AI at the start"), which the generator excludes. Allow it?
10. Real modes toggle on and off repeatedly ("hold" ... "resume" ... "hold"), but `FROM t UNTIL t'` checks only the first segment. Switch to Dwyer's repeating "between Q and R"?
