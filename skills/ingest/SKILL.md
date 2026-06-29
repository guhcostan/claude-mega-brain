---
name: ingest
description: Create or update OKF concept files from existing documentation. Use when the user wants to add a new concept to the project's knowledge base, convert existing docs into OKF format, or update stale OKF entries. Produces valid OKF markdown files with YAML frontmatter.
---

# mega-brain-ingest — OKF Concept Writer

Turns raw documentation (text, schemas, API docs, runbooks, data descriptions) into OKF-formatted `.md` files ready to be committed to the okf directory.

## What to produce

One `.md` file per concept. Required field: `type`. Suggested structure:

```markdown
---
type: <concept type>
title: <display name>
description: <one sentence, plain language>
resource: <URL to the actual resource, if any>
tags: [<tag1>, <tag2>]
timestamp: <ISO 8601 date>
---

<body: schema, joins, examples, caveats — whatever makes this file self-contained>
```

## Common types

| Type | Use for |
|------|---------|
| `BigQuery Table` | BQ tables with schema |
| `BigQuery Dataset` | BQ datasets |
| `Metric` | KPI or business metric definitions |
| `API` | Internal or external API endpoints |
| `Runbook` | Operational procedures |
| `Concept` | Business or domain terminology |
| `Service` | Internal microservices |

Add custom types freely — `type` is freeform.

## Process

1. Read the source material (file, schema dump, API doc, user description)
2. Identify the concept type and canonical name
3. Write a concise `description` (one sentence, no jargon)
4. Add `resource` URL if the concept has a live resource (BQ URL, API endpoint, dashboard)
5. Write the body: schema table, join patterns, examples, gotchas
6. Link to related concepts with `[Name](relative-path.md)` — builds the knowledge graph
7. Save to `<okf_dir>/<type-dir>/<concept-slug>.md`
8. Update `index.md` with a one-line entry for the new concept
9. Append an entry to `log.md`: `<date> — added <title>`

## Updating stale entries

- Update `timestamp` when content changes
- Preserve existing links unless explicitly removing them
- Keep `description` to one sentence — move detail to the body
