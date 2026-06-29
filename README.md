<div align="center">

<img src="assets/logo.png" width="280" alt="claude-mega-brain logo" />

# claude-mega-brain

*Loads the knowledge. Skips the search.*

[![CI](https://img.shields.io/github/actions/workflow/status/guhcostan/claude-mega-brain/test.yml?style=flat-square&color=111111&label=CI)](https://github.com/guhcostan/claude-mega-brain/actions)
[![Stars](https://img.shields.io/github/stars/guhcostan/claude-mega-brain?style=flat-square&color=111111&label=stars)](https://github.com/guhcostan/claude-mega-brain)
[![Release](https://img.shields.io/github/v/release/guhcostan/claude-mega-brain?style=flat-square&color=111111&label=release)](https://github.com/guhcostan/claude-mega-brain/releases)
[![License](https://img.shields.io/badge/license-MIT-111111?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-111111?style=flat-square)](https://github.com/anthropics/claude-code)

**100% accuracy · 0 tool calls · −91% tokens vs Obsidian+MCP**

Real agentic sessions. [Benchmark →](benchmarks/results/agentic-obsidian-vs-mega-brain.md)

</div>

---

## Install

```
/plugin marketplace add guhcostan/claude-mega-brain
/plugin install mega-brain@guhcostan
```

Then in any project:

```
/mega-brain:init
```

Start a new session — the knowledge base loads automatically.

---

## The problem

Without claude-mega-brain, Claude guesses from training data:

```
User: What column stores the order total?

Claude (no context): Typically total_amount (DECIMAL) or amount (FLOAT)...
# Wrong — this project uses amount_cents (INT64)
```

With claude-mega-brain, the exact schema is injected at `SessionStart`:

```
<mega-brain>
OKF: ./okf/ (4 concepts)
  tables/orders.md   [BigQuery Table] — amount_cents INT64, status STRING(pending/confirmed/shipped/done)
  tables/customers.md [BigQuery Table] — customer_id STRING, email STRING
  metrics/wau.md     [Metric]         — COUNT(DISTINCT user_id) WHERE session_date >= CURRENT_DATE-7
  metrics/net_revenue.md [Metric]     — SUM(amount_cents - refund_cents)/100 WHERE status='done'
</mega-brain>

User: What column stores the order total?

Claude: amount_cents (INT64) — from tables/orders.md
# Correct. 0 tool calls. First turn.
```

---

## Benchmark

6 questions with project-specific values unknowable from training data.
Real agentic sessions — not simulated.

![Benchmark chart](assets/benchmark.svg)

| metric | no context | Obsidian+MCP | **claude-mega-brain** |
|---|--:|--:|--:|
| accuracy | 67% | 17% | **100%** |
| tool calls avg | 0.7 | 4.0 | **0** |
| tokens avg | 42,519 | 175,461 | **16,025 (−91%)** |
| latency avg ms | 9,508 | 17,298 | **3,543 (−80%)** |

Obsidian+MCP makes 4 tool calls per question, reads the vault, and still misses — because prose notes lack exact schema values. claude-mega-brain injects structured OKF once at `SessionStart` and answers in a single turn with zero exploration.

[Full results](benchmarks/results/agentic-obsidian-vs-mega-brain.md) · [Reproduce](benchmarks/)

---

## How it works

At `SessionStart`, a hook scans the project for an OKF knowledge base and injects a compact index:

```
<mega-brain>
OKF: ./okf/ (8 concepts)
Read index.md first, then follow links.

Recent (log.md):
  2026-06-29 — added customers table

  index.md            [Index]         — Central reference for all sales data
  tables/orders.md    [BigQuery Table] — One row per completed order
  tables/customers.md [BigQuery Table] — Customer profiles
  metrics/wau.md      [Metric]         — Weekly active users
  ...
</mega-brain>
```

When Claude reads an OKF file, linked concepts surface automatically via `PostToolUse` — no extra prompting needed.

**Zero overhead when not in use** — if no OKF dir exists, the hook exits in <5ms with no context injected.

---

## How it compares

| tool | auto-inject | schema enforcement | tool calls to answer |
|------|-------------|-------------------|---------------------|
| **claude-mega-brain** | ✓ SessionStart hook | required (`type:`) | **0** |
| Obsidian + MCP | ✗ manual | none | 4+ |
| Notion | ✗ manual | proprietary | N/A |
| Logseq | ✗ plugin-based | none | N/A |
| mem.ai | ✗ none | none | N/A |

---

## OKF Format

Each concept is a Markdown file with YAML frontmatter. Only `type` is required:

```markdown
---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, revenue]
timestamp: 2026-06-29T00:00:00Z
---

# Schema
| Column      | Type      | Description              |
|-------------|-----------|--------------------------|
| order_id    | STRING    | Globally unique order ID |
| customer_id | STRING    | FK → customers           |
| amount_cents| INT64     | Total in cents           |
| status      | STRING    | pending/confirmed/shipped/done |

# Joins
Joined with [customers](../tables/customers.md) on `customer_id`.
```

### Reserved files

| File | Purpose |
|------|---------|
| `index.md` | Full knowledge map — Claude reads this first |
| `log.md` | Append-only changelog — last 3 entries injected at session start |

### Common types

`BigQuery Table` · `BigQuery Dataset` · `Table` · `Metric` · `API` · `Runbook` · `Concept` · `Service` · `Pipeline`

Types are freeform — add your own.

---

## Usage

### Start from scratch

```
/mega-brain:init
```

Creates `okf/index.md` and `okf/log.md`. Start a new session — context injects automatically.

### Migrate existing docs

```
/mega-brain:migrate
```

Scans `openapi.yaml`, `schema.prisma`, `schema.sql`, `docs/`, `README` sections and generates OKF files.

### Add a single concept

```
/mega-brain:ingest
```

Document a specific table, metric, API, or service from a schema dump, description, or URL.

### OKF directory names (first match wins)

| Name | Use when |
|------|----------|
| `okf/` | explicit, standard |
| `.okf/` | hidden, keeps root clean |
| `knowledge/` | generic |
| `brain/` | short |

---

## Installation

### Claude Code

```
/plugin marketplace add guhcostan/claude-mega-brain
/plugin install mega-brain@guhcostan
```

### Local development

```bash
claude plugin install /path/to/claude-mega-brain
```

---

## Config (`.mega-brain.json`)

Optional per-project overrides:

```json
{
  "dir": "knowledge",
  "maxConcepts": 100,
  "priorityTypes": ["Metric", "BigQuery Table"]
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `dir` | auto-detect | Custom OKF directory name |
| `maxConcepts` | `60` | Max concepts in injected index |
| `priorityTypes` | `[]` | Types shown at top of index |

---

## FAQ

**Does it slow down every session?**
No. If no OKF directory exists, the hook exits in <5ms with no context injected.

**Can I use it with an existing wiki or docs folder?**
Add `type:` YAML frontmatter to any Markdown file and drop it in your OKF dir. Done.

**What if I have 500 concepts?**
Set `maxConcepts` in `.mega-brain.json`. The index stays compact; `index.md` holds the full map.

---

## References

- [Open Knowledge Format — Google Cloud](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
- [LLM Wiki pattern — Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [Mega Brain — Thiago Finch](https://www.instagram.com/reel/DZI-ys4h29A/) — the meme this plugin is named after

---

## License

[MIT](LICENSE) — The shortest license that works.
