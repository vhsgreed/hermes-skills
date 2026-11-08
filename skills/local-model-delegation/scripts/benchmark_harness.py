#!/usr/bin/env python3
"""Local-model delegation benchmark harness.

Edit TASKS below (real recurring jobs from the workspace, each with a
machine-checkable `expect`), then run:
    python3 benchmark_harness.py               # all tasks
    python3 benchmark_harness.py 01-summarize   # one task (smoke test)

Per-task records land in results/<id>.json (prompt, output, thinking,
timing, token counts); results/all.json aggregates the run.
"""
import json, os, sys, time, urllib.request
from pathlib import Path

MODEL = os.environ.get("BENCH_MODEL", "gemma4:26b")
URL = os.environ.get("BENCH_URL", "http://localhost:11434/api/chat")
OUT = Path(__file__).parent / "results"
OUT.mkdir(exist_ok=True)

TASKS = [
    {
        "id": "01-summarize",
        "name": "Swedish summarization (3 sentences)",
        "prompt": "Sammanfatta följande text i exakt 3 meningar på svenska:\n\n<TEXT>",
        "expect": "3 sentences covering the key facts of the source text",
    },
    {
        "id": "02-extract-json",
        "name": "Extraction to JSON from noisy text",
        "prompt": "Extrahera till strikt JSON med fälten <FIELDS>. Inget annat svar.\n\nText: '<NOISY SOURCE TEXT>'",
        "expect": "valid JSON, every field mapped to the RIGHT source value (this task catches field swaps)",
    },
    # Add: classify batch, arithmetic, convert, dedupe, translate, grammar,
    # tool-call formatting, small plan. Keep prompts short, expect strings exact.
]


def run(task):
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": task["prompt"]}],
        "stream": False,
        "think": True,  # capture reasoning output; it is part of the deliverable
        "options": {"temperature": 0.2},
    }
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:  # heavy tasks need minutes
        data = json.loads(r.read())
    dt = time.time() - t0
    msg = data.get("message", {})
    rec = {
        "id": task["id"],
        "name": task["name"],
        "prompt": task["prompt"],
        "expect": task["expect"],
        "content": msg.get("content", ""),
        "thinking": msg.get("thinking", ""),
        "done_reason": data.get("done_reason"),
        "eval_count": data.get("eval_count"),
        "prompt_eval_count": data.get("prompt_eval_count"),
        "total_duration_s": round(dt, 1),
        "model": MODEL,
    }
    (OUT / f"{task['id']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2))
    return rec


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    results = []
    for task in TASKS:
        if only and task["id"] not in only:
            continue
        print(f"[{task['id']}] running: {task['name']}", flush=True)
        try:
            rec = run(task)
            print(
                f"[{task['id']}] done in {rec['total_duration_s']}s, "
                f"{rec['eval_count']} tokens out, "
                f"thinking={'yes' if rec['thinking'] else 'no'}",
                flush=True,
            )
            results.append(rec)
        except Exception as e:
            print(f"[{task['id']}] FAILED: {e}", flush=True)
            results.append({"id": task["id"], "error": str(e)})
    (OUT / "all.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print("WROTE", OUT / "all.json", flush=True)


if __name__ == "__main__":
    main()
