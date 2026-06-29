---
name: claude-mega-brain
description: OKF knowledge navigation. ALWAYS use this skill the moment a `<mega-brain>` block appears in session context — it means the project has a knowledge base and you must consult it before answering questions about data, schemas, metrics, APIs, or systems. Also trigger when the user asks about a table, column, metric definition, service, or API endpoint and there's any chance it's documented in the project's OKF knowledge base. When in doubt, read index.md first.
---

# claude-mega-brain — OKF Knowledge Navigator

When `<mega-brain>` context is present, the project has an OKF (Open Knowledge Format) knowledge base. It is the authoritative source for domain knowledge: exact schemas, metric formulas, API contracts, runbooks, and business definitions. **Answers from the knowledge base beat answers from training data.**

## What OKF files look like

```yaml
---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
resource: https://...
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

1. **index.md first** — always start here; it maps every concept with a one-line summary
2. **Follow links** — `[text](rel-path.md)` are relative to the OKF dir; read them with the Read tool
3. **log.md** — chronological changelog; check when you need to know what changed recently
4. **Linked concepts auto-surface** — after you read an OKF file, linked concept summaries appear automatically via PostToolUse hook

## Path resolution

Paths in `<mega-brain>` are relative to the OKF dir:
```
Read(<project_root>/<okf_dir>/<concept-path>)
```
Project root = `$PWD`.

## When to proactively read OKF files

- User asks about a data source, table, column, or metric — check the index before answering
- Before writing SQL, queries, or any code that touches project data
- When a business term is ambiguous — OKF has the canonical definition
- When the user says "check the knowledge base", "what do we know about X", or "olha no okf"

## If `<mega-brain>` context is missing

The plugin may not be installed or no OKF dir exists. Suggest:
- Install: `/plugin install claude-mega-brain@guhcostan`
- Initialize: `/mega-brain:init`
- Migrate existing docs: `/mega-brain:migrate`
