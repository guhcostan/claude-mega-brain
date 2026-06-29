# claude-mega-brain — Benchmarks

Measures how much claude-mega-brain reduces tool calls and tokens on knowledge-retrieval tasks, compared to a baseline Claude with no lore context.

## Method

- **Baseline**: Claude Haiku with a plain system prompt — no lore context
- **mega-brain**: Same model with lore context injected as system message (simulating `SessionStart` hook)
- 6 questions covering table schemas, metric definitions, joins, and recent changes
- n=5 per cell, median reported
- Evaluators: `mentions_file` (did Claude cite the right file?) + `contains_truth` (did the answer include the ground truth string?)

The "with-lore" condition simulates what the plugin injects. The "baseline" condition forces Claude to reason from zero — no file paths, no index.

## Run

```bash
npm install -g promptfoo
export ANTHROPIC_API_KEY=your-key-here
npx promptfoo@latest eval -c benchmarks/promptfooconfig.yaml --repeat 5
npx promptfoo@latest view
```

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
- Simulated context injection ≠ full agentic session (no actual tool calls measured here)
- For agentic tool-call metrics, run inside Claude Code with/without the plugin and compare `CLAUDE.md` session logs
