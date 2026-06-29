---
name: claude-lore
description: OKF knowledge navigation. Use when a `<lore>` block appears in session context, when the user asks about data, schemas, metrics, APIs, or systems that may be documented in the project's OKF knowledge base, or when you need authoritative definitions before writing queries or code.
---

# claude-lore — OKF Knowledge Navigator

When `<lore>` context is present, an OKF (Open Knowledge Format) knowledge base lives in this project. It is the authoritative source for domain knowledge: schemas, metrics, APIs, runbooks, business definitions.

## What OKF files look like

```yaml
---
type: BigQuery Table        # required — concept type
title: Orders
description: One row per completed customer order.
resource: https://...       # link to the actual resource
tags: [sales, revenue]
timestamp: 2026-05-28T14:30:00Z
---

# Schema
| Column | Type | Description |
...

# Joins
Joined with [customers](../tables/customers.md) on `customer_id`.
```

## Navigation

1. **index.md first** — maps all concepts with summaries and links
2. **Follow links** — `[text](rel-path.md)` links resolve inside the OKF dir; use the Read tool
3. **log.md** — chronological changelog; check when staleness matters
4. **Linked concepts are auto-injected** — when you read an OKF file, linked concept summaries appear automatically in context (PostToolUse hook)

## Path resolution

Paths in `<lore>` are relative to the OKF dir. Resolve as:
`Read(<project_root>/<okf_dir>/<path>)`

Project root = `$PWD` (where Claude Code is running).

## When to proactively read OKF files

- User asks about a data source, metric, or system matching a concept in the index
- Before writing SQL, queries, or code that depends on schema details
- When a business term is ambiguous — OKF has canonical definitions
- User says "check the lore" or "what do we know about X"

## Project config (.lore.json)

Optional per-project overrides:

```json
{
  "dir": "knowledge",
  "maxConcepts": 100,
  "priorityTypes": ["Metric", "BigQuery Table"]
}
```
