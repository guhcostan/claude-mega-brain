---
name: claude-mega-brain
description: OKF knowledge navigation. ALWAYS use this skill the moment a `<mega-brain>` block appears in session context — it means the project has documented concepts and you must consult them before answering questions about data, schemas, metrics, APIs, or systems. Also trigger when the user asks about a table, column, metric definition, service, or API endpoint and there's any chance it's documented in the project. When in doubt, read the file directly.
---

# claude-mega-brain — OKF Knowledge Navigator

When `<mega-brain>` context is present, the project has OKF-documented concepts — any Markdown file with `type:` in its YAML frontmatter. These are the authoritative source for domain knowledge: exact schemas, metric formulas, API contracts, runbooks, business definitions. **Answers from the knowledge base beat answers from training data.**

## What OKF files look like

Any `.md` file anywhere in the project with YAML frontmatter containing `type:`:

```yaml
---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
resource: https://...
tags: [sales, revenue]
timestamp: 2026-06-29T00:00:00Z
---

# Schema
| Column | Type | Description |
...
```

No dedicated folder required. The file can live in `docs/`, `wiki/`, project root, anywhere.

## Navigation

1. **Read the file** — paths in `<mega-brain>` are relative to the project root; use the Read tool directly
2. **Follow links** — `[text](rel-path.md)` links in the body point to related concepts; read them
3. **log.md** — chronological changelog; last 3 entries are injected automatically
4. **Linked concepts auto-surface** — after you read an OKF file, linked concept summaries appear via PostToolUse hook

## When to proactively read files

- User asks about a data source, table, column, or metric — check `<mega-brain>` index first
- Before writing SQL, queries, or code that touches project data
- When a business term is ambiguous — OKF has the canonical definition
- When the user says "check the knowledge base", "what do we know about X", or "olha no okf"

## If `<mega-brain>` context is missing

No OKF concepts found in the project yet. Suggest:
- `/mega-brain:init` — creates `index.md` and `log.md` to get started
- `/mega-brain:migrate` — scans existing docs and generates OKF files automatically
