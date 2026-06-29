#!/usr/bin/env python3
"""
Agentic benchmark: Obsidian+MCP (filesystem) vs mega-brain.
Runs real claude -p sessions, counts turns/tool-calls, measures accuracy.
"""
import subprocess, json, os, sys, time, tempfile

QUESTIONS = [
    {"id": "amount_cents",  "q": "What column stores the order amount in the orders table, and what data type is it?", "truth": "amount_cents"},
    {"id": "acme_exclusion","q": "What email domain is excluded from the WAU metric?", "truth": "acme.com"},
    {"id": "refund_cents",  "q": "What column is deducted from amount_cents when calculating net_revenue?", "truth": "refund_cents"},
    {"id": "done_status",   "q": "What value of the status column indicates a finished order?", "truth": "done"},
    {"id": "recent_change", "q": "What was the most recent addition to the knowledge base?", "truth": "customers"},
    {"id": "join_key",      "q": "What column links the orders table to the customers table?", "truth": "customer_id"},
]

VAULT_PATH = "/tmp/obsidian-vault"

MCP_CONFIG = {
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", VAULT_PATH],
        }
    }
}

LORE_CONTEXT = """<lore>
Lore: ./okf/ (5 concepts)
Read index.md first, then follow links.

  tables/orders.md [BigQuery Table] — order_id STRING, customer_id STRING, created_at TIMESTAMP, amount_cents INT64, status STRING (pending/confirmed/shipped/done). Join to customers on customer_id.
  tables/customers.md [BigQuery Table] — customer_id STRING, email STRING, country STRING, created_at TIMESTAMP
  metrics/wau.md [Metric] — COUNT(DISTINCT user_id) WHERE session_date >= CURRENT_DATE-7, excludes email LIKE '%@acme.com'
  metrics/net_revenue.md [Metric] — SUM(amount_cents - refund_cents)/100 WHERE status='done'
  log.md — 2026-06-29: added customers table
</lore>"""


def run_claude(prompt, mcp_config_path=None, timeout=90):
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose"]
    if mcp_config_path:
        cmd += ["--mcp-config", mcp_config_path]

    start = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=os.environ.copy())
    except subprocess.TimeoutExpired:
        return None, 0, 0, 0, timeout * 1000

    latency_ms = int((time.time() - start) * 1000)
    answer = tool_calls = tokens = turns = 0

    for line in (proc.stdout + proc.stderr).splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue

        t = e.get("type", "")
        if t == "result":
            answer = e.get("result", "")
            turns = e.get("num_turns", 0)
            u = e.get("usage", {})
            tokens = u.get("input_tokens", 0) + u.get("output_tokens", 0) + u.get("cache_read_input_tokens", 0)
        elif t == "assistant":
            for block in e.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    tool_calls += 1

    return answer, tool_calls, turns, tokens, latency_ms


def run_obsidian(q):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(MCP_CONFIG, f)
        cfg = f.name
    prompt = (
        f"You have access to a filesystem MCP server with project documentation in {VAULT_PATH}. "
        f"Use the tools to find the answer. Be concise.\n\n{q}"
    )
    result = run_claude(prompt, mcp_config_path=cfg)
    os.unlink(cfg)
    return result


def run_mega_brain(q):
    prompt = f"{LORE_CONTEXT}\n\nAnswer using ONLY the lore above. Be concise.\n\n{q}"
    return run_claude(prompt)


def main():
    results = {}
    for cond, runner in [("obsidian+MCP", run_obsidian), ("mega-brain", run_mega_brain)]:
        print(f"\n=== {cond} ===")
        results[cond] = []
        for q in QUESTIONS:
            print(f"  {q['id']}...", end=" ", flush=True)
            answer, tool_calls, turns, tokens, latency = runner(q["q"])
            correct = q["truth"].lower() in (answer or "").lower()
            results[cond].append({
                "id": q["id"], "truth": q["truth"], "correct": correct,
                "tool_calls": tool_calls, "turns": turns,
                "tokens": tokens, "latency_ms": latency,
                "answer": (answer or "")[:150],
            })
            print(f"{'✓' if correct else '✗'} tools={tool_calls} turns={turns} tokens={tokens} {latency}ms")

    print("\n" + "="*60)
    print(f"{'metric':<28} {'obsidian+MCP':>14} {'mega-brain':>14}")
    print("-"*58)
    for metric, key in [("accuracy", "correct"), ("tool calls avg", "tool_calls"), ("turns avg", "turns"), ("tokens avg", "tokens"), ("latency ms avg", "latency_ms")]:
        row = []
        for cond in ["obsidian+MCP", "mega-brain"]:
            vals = [r[key] for r in results[cond]]
            if key == "correct":
                row.append(f"{sum(vals)/len(vals)*100:.0f}%")
            else:
                row.append(f"{sum(vals)/len(vals):.1f}")
        print(f"  {metric:<26} {row[0]:>14} {row[1]:>14}")

    out = "benchmarks/results/agentic-obsidian-vs-mega-brain.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved → {out}")


if __name__ == "__main__":
    main()
