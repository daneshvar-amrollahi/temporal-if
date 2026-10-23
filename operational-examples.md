# Operational examples and the grammar they support

2026-10-24. Which temporal rules have operational weight (binding law, regulator guidance, the published safety policy of a deployed assistant, a safety-critical protocol), and which grammar constructs do they need? Eight Opus searchers, one per domain, looked for rules that the grammar of 2026-10-20 does not cover. A one-shot Sonnet verifier fetched each source and checked the quote, the operational claim, the formalization, and, by running `experiments/2026-10-23-operational-specs/covered.py`, that the rule does not reduce to the old grammar. Rejected but fixable items were repaired once and re-verified. Of 47 candidates, 33 were accepted. Two Opus rankers and a reconciler then tiered each example. Raw output: `experiments/2026-10-23-operational-specs/results.json`.

**Tiers.** 5: binding law, or safety-critical (life or health). 4: regulated-industry compliance in deployed systems, or a safety rule in the published policy of a large-scale assistant. 3: a deployed production rule or platform requirement. 2: a vendor guide or template. 1: an individual user's request.

**Sources.** V: verified in this run. P: verified in the earlier run ([real-world-examples.md](real-world-examples.md)). Only V and P examples are counted. QUANTIFIED marks a rule stated for every value (every seller, every payment amount); the benchmark fixes one value per instruction.

## Ranking of grammar constructs

A construct is credited with every example whose grammar form uses it. Rank is decided by the best tier, then the number of tier-4 and tier-5 examples, then the number of domains among them. Construct names are those of `proposals/temporal-if.md` Section 3.2.

| Rank | Construct | Tier 5 | Tier 4 | Domains of tier 4-5 examples |
|---|---|---|---|---|
| 1 | `NEVER` | 12 | 5 | telemarketing, securities, mental-health law, crisis lines, EU payments, maritime, companion-chatbot law, frontier assistants, agent autonomy, card payments |
| 2 | Event `YOU Act` (the assistant's own act) | 10 | 5 | telemarketing, securities, mental-health law, crisis lines, power grid, aviation, card payments, agentic purchases, coding agents, frontier assistants |
| 3 | Scope `UNTIL` | 9 | 1 | telemarketing, securities, mental-health law, crisis lines, EU payments, card payments |
| 4 | `WITHIN` | 7 | 2 | companion-chatbot law, AI-disclosure law, health AI voice, power grid, aviation, SMS, card payments |
| 5 | Event `USER SAYS … IN REPLY TO YOU …` | 3 | 3 | power grid, aviation, telemarketing, agentic purchases, coding agents |
| 6 | Scope `EACH TIME … UNTIL` | 2 | 3 | maritime, EU payments, agent autonomy, card payments, SMS |
| 7 | Scope `FROM` | 2 | 3 | EU payments, debt collection, frontier assistants |
| 8 | `ONLY IN REPLY TO` | 1 | 3 | EU payments, agentic purchases, coding agents |
| 9 | Trigger `FOR THE m TH TIME` | 2 | 0 | companion-chatbot law, EU payments |
| 10 | `EVENTUALLY … BY` | 2 | 0 | debt collection |
| 11 | Trigger `… SINCE …` | 1 | 0 | EU payments |
| 12 | `AT MOST` | 0 | 1 | frontier assistants |
| 13 | `ALWAYS`, `AFTER m TIMES`, `AT`, `EVERY`, `EXACTLY` | 0 | 0 | best examples are tier 3 (vendor guides, quizzes). `ALWAYS` has tier-5 "throughout the interaction" laws, but a UI label meets them |

## Examples by grammar form

Atoms are named as in the source and stand for `SAY` actions or `USER SAYS` phrases. A form without a scope is under `GLOBALLY`. Abridged quotes are in `results.json` (V) and `real-world-examples.md` (P).

**Precedence released by the assistant's own act: `NEVER b UNTIL YOU a`**
- 5 V. TSR: "'promptly' means before any sales pitch is given". `NEVER pitch UNTIL YOU disclose`. ([FTC](https://www.ftc.gov/business-guidance/resources/complying-telemarketing-sales-rule))
- 5 V. TSR: disclose material terms before the customer consents to pay. `NEVER accept-consent UNTIL YOU disclose` (the assistant controls accepting, not the customer's consent).
- 5 V. TSR, payment by phone: `NEVER pay-request UNTIL YOU disclose`. ([16 CFR 310.3](https://www.law.cornell.edu/cfr/text/16/310.3))
- 5 V. TSR, a second seller in one call: `NEVER pitch_y UNTIL YOU identify_y`, QUANTIFIED over sellers.
- 5 V. Utah mental-health chatbots: disclosure "before the Utah user may access the features". `NEVER serve UNTIL YOU disclose`. ([Utah Code 13-72a](https://le.utah.gov/xcode/Title13/Chapter72A/C13-72a_2025050720250507.pdf))
- 5 V. 988 Lifeline: "actively engage in increasing immediate safety before any emergency service intervention is initiated". `NEVER dispatch UNTIL YOU engage`. ([988 policy](https://988lifeline.org/wp-content/uploads/2023/02/FINAL_988_Suicide_and_Crisis_Lifeline_Suicide_Safety_Policy_-3.pdf))
- 5 V. SEC Form CRS: deliver "before or at the earliest of" a recommendation or order. `NEVER recommend UNTIL YOU deliver-crs` (same reply allowed). ([17 CFR 240.17a-14](https://www.ecfr.gov/current/title-17/chapter-II/part-240/section-240.17a-14))
- 5 V. TSR, express oral authorization: `NEVER charge UNTIL USER SAYS authorize IN REPLY TO YOU state-terms`, QUANTIFIED over the charge.
- 3 V. Claude system prompt escalation ladder: `NEVER end UNTIL YOU warn` and `NEVER warn UNTIL YOU redirect FOR THE 2 TH TIME`.

**Re-opening hold: `NEVER b EACH TIME o UNTIL c`**
- 5 V. Maritime distress: "Until they receive the message indicating that normal working may be resumed … [stations must not transmit]". `NEVER transmit EACH TIME USER SAYS mayday UNTIL USER SAYS resume`. ([47 CFR 80.1125](https://www.law.cornell.edu/cfr/text/47/80.1125))
- 5 V. PSD2 inactivity timeout, with the timeout as an incoming event: `NEVER disclose-account UNTIL USER SAYS authenticated` and `NEVER disclose-account EACH TIME USER SAYS timeout UNTIL USER SAYS authenticated`. ([RTS Art. 4](https://www.legislation.gov.uk/eur/2018/389/article/4))
- 4 V. OpenAI Model Spec: "Every scope must include a shutdown timer, beyond which the assistant ceases actions until a new scope is confirmed". `NEVER act EACH TIME USER SAYS expired UNTIL USER SAYS confirm-scope`. ([Model Spec](https://model-spec.openai.com/2025-12-18.html))
- 4 V. PCI telephone payments, pause and resume: `NEVER ask-card UNTIL YOU pause`, `NEVER ask-card EACH TIME YOU resume UNTIL YOU pause`, and `resume WITHIN 1 OF YOU pause`. Approximate: the rule constrains the card data the customer gives, and the assistant controls only asking for it. ([PCI SSC](https://listings.pcisecuritystandards.org/documents/Protecting_Telephone_Based_Payment_Card_Data_v3-0_nov_2018.pdf))
- 4 P. SMS opt-out: once a user texts STOP, send no further messages until they text START. `NEVER message EACH TIME USER SAYS stop UNTIL USER SAYS start`.

**Response to the user's answer to the assistant's own act: `b WITHIN 0 OF USER SAYS u IN REPLY TO YOU a`**
- 5 V. NERC COM-002-4 R5: "Confirm the receiver's response if the repeated information is correct … Reissue the Operating Instruction if the repeated information is incorrect". Two instructions, one for `confirm` after a correct repeat and one for `reissue` after a wrong one. ([COM-002-4](https://www.regie-energie.qc.ca/storage/app/media/entites-visees-normes-de-fiabilite/english/reliability-standards/COM-002-4-en-2017-01-31.pdf))
- 5 V. FAA JO 7110.65 2-4-3, hearback: `correct WITHIN 0 OF USER SAYS wrong-readback IN REPLY TO YOU issue-clearance`, QUANTIFIED over slot values. ([FAA](https://www.faa.gov/air_traffic/publications/atpubs/atc_html/chap2_section_4.html))

**Response to a trigger: `b WITHIN w OF t`**
- 5 V. Georgia SB 540, escalate on severe or repeated crisis signals: `refer WITHIN 0 OF USER SAYS severe` and `refer WITHIN 0 OF USER SAYS crisis FOR THE 2 TH TIME`. ([GA SB 540](https://www.legis.ga.gov/api/legislation/document/20252026/248169))
- 5 V. California AB 3030, audio disclaimer "at the start and the end of the interaction": the end part is `disclaim WITHIN 0 OF USER SAYS sign-off`. The start part, reply 1, is a single-reply rule.
- 5 P. NY GBL 1701: respond to expressions of suicidal ideation with a crisis notification. `notify WITHIN 0 OF USER SAYS ideation`.
- 5 P. Utah: answer when the user "asks or otherwise prompts" whether AI is used, in two Utah laws. `disclose WITHIN 0 OF USER SAYS asks-if-ai`.
- 4 P. CTIA short codes: respond to HELP every time. `help-info WITHIN 0 OF USER SAYS help`.

**Act only in reply to an approval: `b ONLY IN REPLY TO USER SAYS y IN REPLY TO YOU q`**
- 4 V. ChatGPT agent system card: "ask the user for confirmations before finalizing actions that affect the state of the world". ([system card](https://cdn.openai.com/pdf/839e66fc-602c-48bf-81d3-b21eacc3459d/chatgpt_agent_system_card.pdf))
- 4 V. Operator system card, the same rule with measured misses (92% recall). Approximate: Operator asks in some earlier reply, not necessarily the previous one. ([system card](https://cdn.openai.com/operator_system_card.pdf))
- 4 V. Claude Code system prompt: "A user approving an action … once does NOT mean that they approve it in all contexts".
- 5 V. PSD2 dynamic linking, each payment authenticated for its own amount and payee: `execute_x ONLY IN REPLY TO USER SAYS authenticated_x`, QUANTIFIED, approximate (the rule also allows an earlier authentication if nothing changed since). ([RTS Art. 5](https://www.legislation.gov.uk/eur/2018/389/article/5))

**Ban opened by an event: `NEVER b FROM t`**
- 5 V. PSD2 lockout: `NEVER give-access FROM USER SAYS failed FOR THE 3 TH TIME SINCE USER SAYS success` (the law allows up to 5).
- 4 V. Claude Haiku 5.5 system prompt: "Once Claude has declined a request … that decision stands for the rest of the conversation". `NEVER provide_x FROM YOU decline_x`, QUANTIFIED.
- 4 P. Claude Haiku 5.5 system prompt, suicide and eating-disorder rules: `NEVER b FROM USER SAYS disclosure`.
- 3 V. Claude Code: "If the user denies a tool you call, do not re-attempt the exact same tool call". `NEVER call_x FROM USER SAYS deny IN REPLY TO YOU call_x`, QUANTIFIED.

**Existence before a deadline: `EVENTUALLY a BY t`**
- 5 P. FDCPA: in the initial oral communication, say that you are a debt collector. `EVENTUALLY debt-collector BY USER SAYS sign-off`.
- 5 V. Reg F: in a communication that is partly in Spanish, give the disclosure in Spanish too. `EVENTUALLY disclosure-es BY USER SAYS sign-off FROM USER SAYS spanish`. Approximate: the rule does not order the two. ([12 CFR 1006.18](https://www.consumerfinance.gov/rules-policy/regulations/1006/18/))

**Others.** `AT MOST`: OpenAI Model Spec, do not repeat information already given (4 P, QUANTIFIED). `NEVER` under `GLOBALLY`: CA SB 243, no sexual content for a user known to be a minor (5 P).

## Not covered by the grammar

- Wall-clock periods and deadlines: "at least every three hours" (WA HB 2225, GA SB 540, NY GBL 1702, CA SB 243; 5 V). The trace has no clock. Their turn analogue, "at least once every k replies", is met by acting in every reply.
- Report the latest value given, where later amendments overwrite earlier ones (FAA AIM 5-3-1, 5 V). Needs values carried across rounds.
- Never assemble all parts of a harmful package across the conversation (Claude system prompt, 4 V). A disjunction of absences, and too semantic to check.
- Release by either of two events, "until the user asks or after two failed attempts" (Claude system prompt, Agentforce recipe, 2-3 V). The grammar has one closer per scope.
- m triggers in a row (Google Actions error handling, 2 V).
- An unenacted bill: CA AB 1988, a pause after the second crisis expression until human review (3 V).
