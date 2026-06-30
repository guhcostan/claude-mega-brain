<div align="center">

<img src="assets/logo.png" width="280" alt="claude-mega-brain logo" />

# claude-mega-brain

*Loads the knowledge. Skips the search.*

[![CI](https://img.shields.io/github/actions/workflow/status/guhcostan/claude-mega-brain/test.yml?style=flat-square&color=111111&label=CI)](https://github.com/guhcostan/claude-mega-brain/actions)
[![Stars](https://img.shields.io/github/stars/guhcostan/claude-mega-brain?style=flat-square&color=111111&label=stars)](https://github.com/guhcostan/claude-mega-brain)
[![Release](https://img.shields.io/github/v/release/guhcostan/claude-mega-brain?style=flat-square&color=111111&label=release)](https://github.com/guhcostan/claude-mega-brain/releases)
[![License](https://img.shields.io/badge/license-MIT-111111?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-111111?style=flat-square)](https://github.com/anthropics/claude-code)

**100% accuracy · 0 tool calls · −66% tokens vs Obsidian+MCP**

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
# Wrong — this project uses total_cents (INT64)
```

With claude-mega-brain, the exact schema is injected at `SessionStart`:

```
<mega-brain>
Knowledge: 4 documented concepts found in project

  docs/orders.md     [BigQuery Table] — total_cents INT64, status STRING(pending/confirmed/shipped/done)
  docs/customers.md  [BigQuery Table] — customer_id STRING, email STRING, country STRING
  docs/wau.md        [Metric]         — COUNT(DISTINCT user_id) WHERE session_date >= CURRENT_DATE-7
  docs/net_revenue.md [Metric]        — SUM(total_cents - refund_cents)/100 WHERE status='done'
</mega-brain>

User: What column stores the order total?

Claude: total_cents (INT64) — from docs/orders.md
# Correct. 0 tool calls. First turn.
```

---

## Benchmark

10 questions with project-specific values unknowable from training data.
Real agentic sessions — not simulated.

![Benchmark chart](assets/benchmark.svg)

| metric | no context | Obsidian+MCP | CLAUDE.md (raw files) | **claude-mega-brain** |
|---|--:|--:|--:|--:|
| accuracy (no tools) | 50% | 13% | 100% | **100%** |
| accuracy (agentic) | 100%† | 100%† | 100% | **100%** |
| tool calls avg | 1.1 | 0.9 | 0.1 | **0** |
| tokens avg | 61,521 | 49,186 | 20,624 | **16,547** |
| latency avg ms | 10,267 | 10,986 | 5,494 | **4,384** |

† raw and Obsidian+MCP reach 100% agentic accuracy by using tool calls to explore the project — spending 3–4× more tokens and time. Without tools, they drop to 50% and 13%.

CLAUDE.md (raw files) matches mega-brain on accuracy but uses 25% more tokens and is 25% slower. mega-brain's compressed OKF index is smaller and faster — the gap widens as knowledge bases grow.

[Full results](benchmarks/results/agentic-obsidian-vs-mega-brain.md) · [Reproduce](benchmarks/)

---

## How it works

At `SessionStart`, a hook scans the entire project for any `.md` file with `type:` in its YAML frontmatter and injects a compact index:

```
<mega-brain>
Knowledge: 8 documented concepts found in project

Recent (log.md):
  2026-06-29 — added customers table

  index.md            [Index]         — Central reference for all sales data
  docs/orders.md      [BigQuery Table] — One row per completed order
  docs/customers.md   [BigQuery Table] — Customer profiles
  docs/wau.md         [Metric]         — Weekly active users
  ...
</mega-brain>
```

No dedicated folder needed — documents can live anywhere in the project. When Claude reads an OKF file, linked concepts surface automatically via `PostToolUse`.

**Zero overhead when not in use** — if no documented concepts are found, the hook exits in <5ms.

---

## How it compares

| tool | auto-inject | schema enforcement | tool calls to answer | accuracy (no tools) |
|------|-------------|-------------------|---------------------|---------------------|
| **claude-mega-brain** | ✓ SessionStart hook | required (`type:`) | **0** | **100%** |
| CLAUDE.md + additionalDirectories | manual setup | none | 0 | 100%* |
| Obsidian + MCP | ✗ manual | none | 1–3 | 13% |
| Notion | ✗ manual | proprietary | N/A | — |
| Logseq | ✗ plugin-based | none | N/A | — |
| mem.ai | ✗ none | none | N/A | — |

\* CLAUDE.md matches mega-brain accuracy but uses 25% more tokens and is 25% slower — raw file dump vs compressed structured index.

---

## OKF Format

Any `.md` file in the project with `type:` in its YAML frontmatter is automatically picked up. No dedicated folder needed.

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
| total_cents | INT64     | Order total in cents     |
| status      | STRING    | pending/confirmed/shipped/done |

# Joins
Joined with [customers](customers.md) on `customer_id`.
```

### Reserved files

| File | Purpose |
|------|---------|
| `index.md` (with `type: Index`) | Knowledge map — Claude reads this first |
| `log.md` (with `type: Log`) | Append-only changelog — last 3 entries injected at session start |

### Common types

`BigQuery Table` · `BigQuery Dataset` · `Table` · `Metric` · `API` · `Runbook` · `Concept` · `Service` · `Pipeline`

Types are freeform — add your own.

---

## Usage

### Start from scratch

```
/mega-brain:init
```

Creates `index.md` and `log.md` anywhere you want. Start a new session — context injects automatically.

### Migrate existing docs

```
/mega-brain:migrate
```

Scans `openapi.yaml`, `schema.prisma`, `schema.sql`, `docs/`, `README` sections and adds `type:` frontmatter to generate OKF concepts.

### Add a single concept

```
/mega-brain:ingest
```

Document a specific table, metric, API, or service. Saves the file wherever makes sense for your project structure.

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
| `dir` | *(none)* | Limit scanning to this subdirectory (relative to project root). When unset, the entire project is scanned. |
| `maxConcepts` | `60` | Max concepts in injected index |
| `priorityTypes` | `[]` | Types shown at top of index |
| `exclude` | `[]` | Additional dirs to skip when scanning |

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

## Star History

<a href="https://www.star-history.com/?type=date&repos=guhcostan%2Fclaude-mega-brain">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=guhcostan/claude-mega-brain&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=guhcostan/claude-mega-brain&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=guhcostan/claude-mega-brain&type=date&legend=top-left" />
 </picture>
</a>

---

## License

[MIT](LICENSE) — The shortest license that works.
