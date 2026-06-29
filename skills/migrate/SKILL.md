---
name: migrate
description: Scan the project and migrate existing documentation into OKF format. Use when the user wants to populate the okf/ directory from existing docs, README, schemas, API specs, runbooks, or any structured project knowledge. Trigger on "migrate to okf", "populate the knowledge base", "scan my docs", "convert docs to okf", "importar documentação", "migrar para okf", "popular o knowledge base", "lê meus docs e cria o okf", "generate okf from existing docs", or when the user points at a docs folder and asks to "put it in the knowledge base". Always check that okf/ exists first; if not, run /mega-brain:init before migrating.
---

# migrate — Migrate Existing Docs to OKF

Reads existing project documentation and generates OKF concept files so claude-mega-brain can inject them at session start. The goal is exact fidelity — preserve real column names, actual formulas, and specific values, not generic descriptions.

## Before starting

Check if an OKF directory exists (`okf/`, `.okf/`, `knowledge/`, `brain/`). If none found, run `/mega-brain:init` first, then proceed.

## Process

### 1. Discover sources

Scan the project root. Priority order:

| Source | Look for |
|--------|----------|
| API specs | `openapi.yaml`, `swagger.json`, `*.openapi.yml` |
| DB schemas | `schema.sql`, `schema.prisma`, `*.dbml`, migration files |
| Data models | `models/`, `entities/`, `domain/` |
| README sections | `## API`, `## Schema`, `## Architecture`, `## Data` |
| Runbooks | `docs/runbook*`, `runbooks/`, `playbooks/` |
| Env/config docs | `.env.example` with comments, annotated `config/` files |
| Existing wikis | `docs/`, `wiki/`, `pages/` |

Report what you found before proceeding. If more than 10 sources, ask the user to confirm before generating all files.

### 2. Classify each source → OKF type

| Source content | OKF type |
|----------------|----------|
| DB table / Prisma model | `Table` or `BigQuery Table` |
| REST/GraphQL endpoint | `API` |
| Business metric / KPI | `Metric` |
| Microservice / module | `Service` |
| Operational procedure | `Runbook` |
| Business term / glossary | `Concept` |
| Data pipeline / ETL | `Pipeline` |

### 3. Generate OKF files

One `.md` file per concept:

```markdown
---
type: <classified type>
title: <name>
description: <one sentence, plain language>
resource: <source file path or URL>
tags: [<relevant tags>]
timestamp: <today ISO date>
---

# Schema / Definition

<exact content extracted from source — preserve all field names, types, values>

# Notes

<caveats, deprecations, gotchas found in the source>
```

**Rules that matter:**
- One concept per file — split tables from each other, endpoints from each other
- Preserve exact field names, column types, enum values, formulas — never generalize
- Add wikilinks `[Name](relative-path.md)` when concepts reference each other
- Place files in `tables/`, `apis/`, `metrics/`, `services/`, `runbooks/` as appropriate

### 4. Update `okf/index.md`

Add one line per new concept under the relevant section:
```markdown
- [Title](subdir/file.md) — one-sentence description
```

### 5. Append to `okf/log.md`

```
<today ISO date> — migrated <N> concepts from <source list>
```

### 6. Report

List every file created with its type and path. Flag anything ambiguous or skipped with a reason.

Tell the user to **start a new Claude Code session** for the injected context to activate.

## What NOT to migrate

- Test fixtures and mock data
- Build artifacts and generated code
- Duplicate docs — keep the most recent or canonical version
- Files with no extractable schema, formula, or definition
