---
name: migrate
description: Scan the project and migrate existing documentation into OKF format. Use when the user wants to populate the okf/ directory from existing docs, README, schemas, API specs, runbooks, or any structured project knowledge. Triggers on "migrate to okf", "populate mega brain", "scan my docs", "convert docs to okf", "importar documentação", "migrar para okf", "popular o knowledge base".
---

# mega-brain-migrate — Migrate Existing Docs to OKF

Reads existing project documentation and generates OKF-formatted concept files so claude-mega-brain can inject them at session start.

## Process

### 1. Discover sources

Scan the project for documentation worth migrating. Priority order:

| Source | Look for |
|--------|----------|
| API specs | `openapi.yaml`, `swagger.json`, `*.openapi.yml` |
| DB schemas | `schema.sql`, `schema.prisma`, `*.dbml`, migration files |
| Data models | `models/`, `entities/`, `domain/` dirs |
| README sections | headers like `## API`, `## Schema`, `## Architecture` |
| Runbooks | `docs/runbook*`, `runbooks/`, `playbooks/` |
| Config/env docs | `.env.example` with comments, `config/` with annotated files |
| Existing wikis | `docs/`, `wiki/`, `pages/` markdown files |

Report what you found before proceeding. Ask for confirmation if more than 10 sources.

### 2. Classify each source → OKF type

| Source content | OKF type |
|----------------|----------|
| DB table / Prisma model | `Database Table` |
| REST/GraphQL endpoint | `API` |
| Business metric / KPI | `Metric` |
| Microservice / module | `Service` |
| Operational procedure | `Runbook` |
| Business term / glossary | `Concept` |
| Data pipeline / ETL | `Pipeline` |

### 3. Generate OKF files

For each source, produce one `.md` file:

```markdown
---
type: <classified type>
title: <name>
description: <one sentence from the source>
resource: <URL or file path if applicable>
tags: [<relevant tags>]
timestamp: <today ISO date>
---

# Schema / Definition / Description

<structured content extracted from source>

# Notes

<any caveats, deprecations, or gotchas found in the source>
```

**Rules:**
- One concept per file — split tables from each other, endpoints from each other
- `description` must be one sentence, plain language, no jargon
- Preserve exact field names, types, and values — do not generalize
- Add wikilinks `[Name](relative-path.md)` when concepts reference each other
- Place files in logical subdirs: `tables/`, `apis/`, `metrics/`, `services/`, `runbooks/`

### 4. Update index.md

Add one line per new concept to `okf/index.md` under the relevant section:

```markdown
- [Title](subdir/file.md) — one-sentence description
```

### 5. Append to log.md

```
<ISO date> — migrated <N> concepts from <sources>
```

### 6. Report

List every file created with its type and path. Flag anything ambiguous or skipped with a reason.

## What NOT to migrate

- Test fixtures and mock data
- Build artifacts and generated files
- Duplicate docs (keep the most recent/canonical)
- Files with no extractable schema or definition
