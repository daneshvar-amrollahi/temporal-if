"""Stream real human-LLM chat logs from Hugging Face and keep conversations with >= MIN_TURNS user turns.

Writes one normalized JSONL per source to OUT/<source>/long.jsonl:
  {source, id, model, language, timestamp, user, redacted, n_user_turns, messages: [{role, content}]}

usage: python3 extract.py <source> [<source> ...]   sources: wildchat48m sharegpt90k lmsys sharechat
"""
import sys, os, json, collections
sys.modules["pandas"] = None  # local pandas is broken, pyarrow works without it
import pyarrow.parquet as pq
from concurrent.futures import ThreadPoolExecutor
from huggingface_hub import HfFileSystem, hf_hub_download

MIN_TURNS = 11
OUT = "/Users/daneshvar/Documents/GitHub/temporal-if-data"
fs = HfFileSystem()


def writer(source):
    os.makedirs(f"{OUT}/{source}", exist_ok=True)
    return open(f"{OUT}/{source}/long.jsonl", "w")


def wildchat48m():
    files = sorted(fs.glob("datasets/allenai/WildChat-4.8M/data/*.parquet"))
    top = ["conversation_hash", "model", "timestamp", "turn", "language", "redacted", "hashed_ip"]
    msg = ["conversation.list.element.role", "conversation.list.element.content", "conversation.list.element.language"]

    def work(f):
        pf = pq.ParquetFile(fs.open(f, block_size=2**22))
        have = set(pf.schema_arrow.names)
        cols = [c for c in top if c in have] + msg
        rows = []
        for g in range(pf.metadata.num_row_groups):
            # filter in Python: building pyarrow arrays from lists trips the broken-pandas shim under threads
            for r in pf.read_row_group(g, columns=cols).to_pylist():
                if (r["turn"] or 0) < MIN_TURNS:
                    continue
                rows.append({
                    "source": "wildchat48m", "id": r["conversation_hash"], "model": r["model"],
                    "language": r["language"], "timestamp": str(r["timestamp"]), "user": r.get("hashed_ip"),
                    "redacted": r.get("redacted"), "n_user_turns": r["turn"],
                    "messages": [{"role": m["role"], "content": m["content"], "language": m["language"]}
                                 for m in r["conversation"]],
                })
        print(f.split("/")[-1], len(rows), file=sys.stderr, flush=True)
        return rows

    out, n = writer("wildchat48m"), 0
    with ThreadPoolExecutor(8) as ex:
        for rows in ex.map(work, files):
            for r in rows:
                out.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
    print("wildchat48m kept", n)


def sharegpt90k():
    role = {"human": "user", "user": "user", "gpt": "assistant", "chatgpt": "assistant", "bing": "assistant",
            "bard": "assistant", "assistant": "assistant", "system": "system"}
    out, n, seen, roles = writer("sharegpt90k"), 0, set(), collections.Counter()
    for part in ["sg_90k_part1.json", "sg_90k_part2.json"]:
        p = hf_hub_download("RyokoAI/ShareGPT52K", part, repo_type="dataset", cache_dir=f"{OUT}/.cache")
        for c in json.load(open(p)):
            msgs = [{"role": role.get(m.get("from"), m.get("from")), "content": m.get("value", "")}
                    for m in c.get("conversations", [])]
            roles.update(m["role"] for m in msgs)
            k = sum(m["role"] == "user" for m in msgs)
            if k < MIN_TURNS or c["id"] in seen:
                continue
            seen.add(c["id"])
            out.write(json.dumps({"source": "sharegpt90k", "id": c["id"], "model": "chatgpt-2023", "language": None,
                                  "timestamp": None, "user": None, "redacted": None, "n_user_turns": k,
                                  "messages": msgs}, ensure_ascii=False) + "\n"); n += 1
        os.remove(os.path.realpath(p))
    print("sharegpt90k kept", n, "roles", roles.most_common())


if __name__ == "__main__":
    for s in sys.argv[1:]:
        globals()[s]()
