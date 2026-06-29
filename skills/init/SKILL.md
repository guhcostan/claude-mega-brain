---
name: init
description: Initialize an OKF knowledge base in the current project. Use when there is no okf/ directory yet and the user wants to start using claude-mega-brain, or when the user says "init mega brain", "setup the knowledge base", "cria o okf", "inicializa o mega brain", "quero usar o mega brain", "setup okf", "criar a estrutura do knowledge base", or asks how to get started with the plugin.
---

# init — Initialize OKF Knowledge Base

Creates the `okf/` directory with a minimal ready-to-use structure so claude-mega-brain can start injecting context at the next session start.

## Steps

### 1. Check for existing OKF dir

Look for `okf/`, `.okf/`, `knowledge/`, `brain/` in the project root. If any exists, stop and tell the user — do not overwrite.

### 2. Detect project type

Peek at root files to personalize the template:
- `package.json` → Node/TypeScript
- `pyproject.toml` or `setup.py` → Python
- `go.mod` → Go
- `pom.xml` or `build.gradle` → Java/Kotlin
- `Gemfile` → Ruby
- Generic fallback otherwise

### 3. Create the structure

```
okf/
├── index.md    ← knowledge map (start here every session)
└── log.md      ← append-only changelog
```

### 4. Write `okf/index.md`

```markdown
---
type: Index
title: <Project Name> Knowledge Base
description: Central reference for all project knowledge.
timestamp: <today ISO 8601>
---

# <Project Name> Knowledge Base

## Tables / Data
<!-- [orders](tables/orders.md) — one-liner -->

## Metrics
<!-- [wau](metrics/wau.md) — one-liner -->

## APIs
<!-- [auth](apis/auth.md) — one-liner -->

## Services
<!-- [payments](services/payments.md) — one-liner -->
```

### 5. Write `okf/log.md`

```markdown
---
type: Log
---
<today ISO date> — initialized OKF knowledge base
```

### 6. Tell the user

- What was created
- **Start a new Claude Code session** for context injection to activate
- How to add the first concept: `/mega-brain:ingest` or create `okf/<type>/<name>.md` manually
- If existing docs exist: `/mega-brain:migrate` can auto-populate from README, schemas, API specs
