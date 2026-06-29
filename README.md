# claude-mega-brain

![claude-mega-brain logo](assets/logo.png)

*Loads the lore. Skips the search.*

[![Stars](https://img.shields.io/github/stars/your-username/claude-mega-brain?style=flat-square&color=111111&label=stars)](https://github.com/your-username/claude-mega-brain)
[![Release](https://img.shields.io/github/v/release/your-username/claude-mega-brain?style=flat-square&color=111111&label=release)](https://github.com/your-username/claude-mega-brain/releases)
[![License](https://img.shields.io/badge/license-MIT-111111?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-111111?style=flat-square)](https://github.com/anthropics/claude-code)

**23% → 100% accuracy on project-specific questions · zero config · silent when no OKF found**

Measured on knowledge-retrieval Q&A over a fictional schema, n=5, Claude Sonnet 4.6.
Full details in [benchmarks/results/2026-06-29.md](benchmarks/results/2026-06-29.md).

---

## The problem

Without claude-mega-brain, Claude answers project-specific questions from training data — and gets them wrong:

```
User: What column stores the order total, and what type is it?

Claude (baseline): Common conventions are total_amount (DECIMAL) or amount (FLOAT)...
# Wrong. The project uses amount_cents (INT64).
```

With claude-mega-brain, the schema is injected at session start:

```
<lore>
Lore: ./okf/ (4 concepts)
  tables/orders.md [BigQuery Table] — One row per completed order
  tables/customers.md [BigQuery Table] — Customer profiles
  metrics/wau.md [Metric] — Weekly active users
  metrics/net_revenue.md [Metric] — Net revenue after refunds
</lore>

User: What column stores the order total, and what type is it?

Claude: Based on tables/orders.md — amount_cents (INT64).
# Correct, first turn, no exploration needed.
```

## Benchmark Results

6 knowledge-retrieval questions over a fictional schema with project-specific column names.
Correct answers require the injected context — not guessable from training data.

| | accuracy | n |
|---|--:|--:|
| baseline (no context) | 23% | 30 |
| **mega-brain** (OKF injected) | **100%** | 30 |

Model: Claude Sonnet 4.6. [Full results](benchmarks/results/2026-06-29.md) · [Reproduce](benchmarks/)

---

## How It Works

At `SessionStart`, a hook scans your project for an OKF knowledge base and injects a compact index:

```
<lore>
Lore: ./okf/ (8 concepts)
Read index.md first, then follow links.

Recent (log.md):
  2026-06-29 — added customers table

  index.md [Index] — Central reference for all sales data
  tables/orders.md [BigQuery Table] — One row per completed order
  tables/customers.md [BigQuery Table] — Customer profiles
  metrics/wau.md [Metric] — Weekly active users definition
  ...
</lore>
```

Claude knows exactly what exists and where. No exploration needed.

When Claude reads an OKF file, linked concepts are automatically surfaced via a `PostToolUse` hook — navigating the knowledge graph without extra prompting.

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
| Column       | Type   | Description               |
|--------------|--------|---------------------------|
| order_id     | STRING | Globally unique order ID  |
| customer_id  | STRING | FK to [customers](../tables/customers.md) |

# Joins
Joined with [customers](../tables/customers.md) on `customer_id`.
```

### Reserved files

| File | Purpose |
|------|---------|
| `index.md` | Full knowledge map — Claude reads this first |
| `log.md` | Append-only changelog — last 3 entries injected at session start |

### Common types

`BigQuery Table` · `BigQuery Dataset` · `Metric` · `API` · `Runbook` · `Concept` · `Service`

Types are freeform — add your own.

---

## Installation

### Claude Code

```
/plugin marketplace add your-username/claude-mega-brain
/plugin install claude-mega-brain@your-username
```

### Local (development)

```bash
claude plugin install /path/to/claude-mega-brain
```

---

## Usage

Create a knowledge base in your project:

```bash
mkdir okf/
```

Add concepts:

```markdown
# okf/tables/orders.md
---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
---
```

Start a new Claude Code session — the lore is loaded automatically.

### OKF directory names (first match wins)

| Name | Use when |
|------|----------|
| `.lore/` | hidden, keeps root clean |
| `okf/` | explicit, standard |
| `knowledge/` | generic |
| `.second-brain/` | thematic |
| `brain/` | short |

### Adding concepts with `/mega-brain-ingest`

```
/mega-brain-ingest
```

Invoke the ingest skill to create or update OKF files from existing documentation, schemas, or API specs.

---

## Config (`.lore.json`)

Optional per-project overrides at the project root:

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
| `priorityTypes` | `[]` | Types to sort to the top of the index |

---

## FAQ

**Does it add overhead to every session?**
Only if an OKF directory exists in the project. No lore dir → hook exits in <5ms, no context injected.

**Can I use it with an existing wiki or docs folder?**
Add YAML frontmatter with `type:` to any Markdown file and drop it in your OKF dir. That's the full migration.

**What if I have 500 concepts?**
Set `maxConcepts` in `.lore.json`. The index stays compact; `index.md` holds the full map.

**Does it work without `index.md`?**
Yes. `index.md` is optional — Claude navigates via the injected list and concept links.

---

## References

- [Open Knowledge Format — Google Cloud](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
- [LLM Wiki pattern — Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [ponytail](https://github.com/DietrichGebert/ponytail) — inspiration for plugin structure

---

## License

[MIT](LICENSE) — The shortest license that works.
