---
name: ingest
description: Create or update a single OKF concept file from raw input. Use when the user wants to document a specific table, metric, API, service, or concept in the knowledge base — even if they say "add this to the okf", "documenta essa tabela", "cria um conceito pra isso", "adiciona no knowledge base", "register this API", or pastes a schema/description and says to save it. Always check that okf/ exists first; if not, suggest /mega-brain:init.
---

# ingest — OKF Concept Writer

Turns raw input (schema dump, API doc, user description, table definition) into one OKF-formatted `.md` file committed to the knowledge base.

## Before writing

Check if an OKF directory exists (`okf/`, `.okf/`, `knowledge/`, `brain/`). If none found, stop and tell the user to run `/mega-brain:init` first.

Check if a concept with the same name already exists. If so, ask whether to update it or create a new one.

## Output format

One `.md` file per concept. Only `type` is required:

```markdown
---
type: <concept type>
title: <display name>
description: <one sentence, plain language, no jargon>
resource: <URL to the actual resource, if any>
tags: [<tag1>, <tag2>]
timestamp: <ISO 8601 date>
---

<body: exact schema, formula, join patterns, examples, caveats>
```

## Common types

| Type | Use for |
|------|---------|
| `BigQuery Table` | BQ tables with schema |
| `BigQuery Dataset` | BQ datasets |
| `Table` | Non-BQ database tables |
| `Metric` | KPI or business metric with formula |
| `API` | REST/GraphQL endpoints |
| `Runbook` | Operational procedures |
| `Concept` | Business or domain terminology |
| `Service` | Internal microservices |
| `Pipeline` | ETL or data pipelines |

Types are freeform — add your own.

## Process

1. Read the source material
2. Identify the concept type and canonical name
3. Write `description`: one sentence, plain language
4. Add `resource` URL if there's a live resource (BQ console URL, API endpoint, dashboard)
5. Write the body with exact values — preserve field names, types, and formulas as-is; do not generalize
6. Link to related concepts with `[Name](relative-path.md)` — this builds the knowledge graph
7. Save to `<okf_dir>/<type-subdir>/<slug>.md`
8. Add one line to `okf/index.md`: `- [Title](path) — description`
9. Append to `okf/log.md`: `<date> — added <title>`

## Updating an existing entry

- Update `timestamp`
- Preserve existing wikilinks unless explicitly removing them
- Keep `description` to one sentence — push additional detail into the body
