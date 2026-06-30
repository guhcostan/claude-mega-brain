# claude-mega-brain — Benchmarks

Measures accuracy, tool calls, tokens, and cost across 4 injection strategies.

## Conditions

| Condition | Description |
|---|---|
| **raw** | No context — Claude answers from training data only |
| **obsidian-style** | Vague prose descriptions without exact schema (simulates naive context injection) |
| **CLAUDE.md (raw files)** | Raw OKF files dumped as context, no navigation instructions (simulates `additionalDirectories`) |
| **mega-brain (OKF)** | Structured OKF index injected via `SessionStart` hook |

## Accuracy Benchmark (promptfoo)

6 questions × 5 repeats, Claude Sonnet 4.6, `temperature=0`.

```bash
cd benchmarks
npx promptfoo@latest eval -c promptfooconfig.yaml --repeat 5
npx promptfoo@latest view
```

| Condition | Accuracy | Tokens avg |
|---|---|---|
| raw (no context) | 50% | 138 |
| obsidian-style | 13% | 408 |
| CLAUDE.md (raw files) | 100% | 400 |
| **mega-brain (OKF)** | **100%** | **266** |

Raw and obsidian-style fail project-specific questions (exact column names, log dates, exclusion
rules). CLAUDE.md and mega-brain both achieve 100% — but mega-brain uses 33% fewer tokens
thanks to its compressed structured index vs raw file dump.

## Agentic Benchmark (real Claude Code sessions)

6 questions × 1 run per condition, measures tool calls, turns, tokens, and latency via `claude -p`.

```bash
cd benchmarks
python3 run-agentic-bench.py
```

| Condition | Accuracy | Tool calls | Turns | Tokens avg | Latency avg |
|---|---|---|---|---|---|
| raw (no context) | 100%† | 1.1 | 2.6 | 61,521 | 10,267ms |
| obsidian+MCP | 100%† | 0.9 | 2.1 | 49,186 | 10,986ms |
| CLAUDE.md (raw files) | 100% | 0.1 | 1.2 | 20,624 | 5,494ms |
| **mega-brain (OKF)** | **100%** | **0.0** | **1.0** | **16,547** | **4,384ms** |

† raw and Obsidian+MCP reach 100% by using tool calls — spending 3× more tokens and time.
Without tools they drop to 50% and 13% respectively (see promptfoo benchmark above).

CLAUDE.md and mega-brain both answer in 1 turn with 0 tool calls. mega-brain uses 20% fewer
tokens and is 20% faster due to the compressed structured index.

## Token Cost Benchmark (vs CLAUDE.md + prompt caching)

Does explicit `cache_control` matter? 6 queries, Haiku 4.5, ~8k-token OKF knowledge base.

```bash
cd benchmarks
python3 -m venv .venv && .venv/bin/pip install anthropic
export ANTHROPIC_API_KEY=your-key-here
.venv/bin/python token-cost-bench.py
```

| Strategy | Total cost (6 queries) | vs baseline |
|---|---|---|
| system-static (CLAUDE.md sim) | $0.039 | — |
| **system-cached (explicit cache_control)** | **$0.005** | **88% cheaper** |
| user-injection (naive) | $0.039 | no difference |

`system-static` and `user-injection` are indistinguishable — neither caches without explicit
`cache_control`. Whether CLAUDE.md + additionalDirectories benefits from caching depends on
how the Claude Code client constructs its API calls internally. OKF can guarantee caching by
injecting with explicit `cache_control: ephemeral` in the hook.

Note: caching only activates above ~2500 tokens (Haiku 4.5 minimum). Small knowledge bases
pay the same regardless of strategy.

## Sample knowledge base

`fixtures/sample-lore/` contains 5 OKF concepts:

```
index.md          [Index]         — full knowledge map
log.md            [Log]           — changelog
tables/orders.md  [BigQuery Table]
tables/customers.md [BigQuery Table]
metrics/wau.md    [Metric]
metrics/revenue.md [Metric]
```

## Limitations

- Questions are synthetic; real-world gains depend on knowledge base size and specificity
- Agentic benchmark runs n=1 per condition (no repeat); results may vary across runs
- Caching benchmark uses synthetic OKF padding to exceed the minimum cache threshold
