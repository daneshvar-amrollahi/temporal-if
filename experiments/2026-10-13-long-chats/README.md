# Long real chats (>= 11 user turns)

Goal: find real long conversations so the benchmark does not need stitching.

`extract.py` streams each source from Hugging Face and keeps conversations with >= 11 user turns, normalized to one JSONL schema. Output lives outside the repo at `/Users/daneshvar/Documents/GitHub/temporal-if-data/<source>/long.jsonl` (linked as `data/long-chats`).

| Source | Long convs | Median turns | >= 20 turns | English | English after base filters (est.) | Mostly reply-independent, English (est.) | Genuine persistent instructions (est.) |
|---|---|---|---|---|---|---|---|
| WildChat-4.8M (ODC-BY) | 38,407 | 14 | 9,432 | 47% | ~14.8K | ~11.8K (~2.9K at >= 20) | ~200-250, mostly length rules |
| ShareGPT-90K (RyokoAI, 2023) | 16,507 | 19 | 7,844 | 73% | ~10.9K | ~2-3K (~1-1.5K at >= 20) | ~400 |

Base filters: English, dedup, no jailbreaks or agent loops, not dominated by "continue" or pasted turns, <= 128K tokens, <= 20 convs per user (WildChat). "Reply-independent" uses a strict regex and is a rough proxy. In hand samples of 25, 7 (WildChat) and 6 (ShareGPT) were fully reply-independent.

Not yet extracted: LMSYS-Chat-1M and ShareChat (gated, need `hf auth login` and accepted terms).
