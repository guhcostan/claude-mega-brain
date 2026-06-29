---
name: init
description: Initialize an OKF knowledge base in the current project. Use when the user wants to set up claude-mega-brain for the first time, when there is no okf/ directory yet, or when the user says "init mega brain", "create the knowledge base", "setup okf", or "inicializar o mega brain".
---

# mega-brain-init — Initialize OKF Knowledge Base

Creates the `okf/` directory with a ready-to-use structure so claude-mega-brain can start injecting context at the next session.

## Steps

1. Check if an OKF directory already exists (`okf/`, `.okf/`, `knowledge/`, `brain/`). If yes, tell the user and stop — do not overwrite.

2. Detect the project type from existing files:
   - `package.json` → Node/TypeScript project
   - `pyproject.toml` / `setup.py` → Python project
   - `go.mod` → Go project
   - `pom.xml` / `build.gradle` → Java/Kotlin project
   - `Gemfile` → Ruby project
   - Generic fallback if none found

3. Create this structure:

```
okf/
├── index.md          ← knowledge map
└── log.md            ← changelog
```

4. Write `okf/index.md`:

```markdown
---
type: Index
title: <Project Name> Knowledge Base
description: Central reference for all project knowledge.
timestamp: <ISO date>
---

# <Project Name> Knowledge Base

Add concepts here as you document them:

## Tables / Data
<!-- Add links to tables/: [orders](tables/orders.md) -->

## Metrics
<!-- Add links to metrics/: [wau](metrics/wau.md) -->

## APIs
<!-- Add links to apis/: [auth](apis/auth.md) -->

## Services
<!-- Add links to services/: [payments](services/payments.md) -->
```

5. Write `okf/log.md`:

```markdown
---
type: Log
---
<ISO date> — initialized OKF knowledge base
```

6. Tell the user:
   - What was created
   - That they need to **start a new Claude Code session** for the context to be injected
   - How to add their first concept: `okf/<type>/<name>.md` with `---\ntype: ...\n---`
   - That `/mega-brain-migrate` can auto-populate from existing docs
