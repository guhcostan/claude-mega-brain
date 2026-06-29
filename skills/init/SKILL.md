---
name: init
description: Initialize OKF knowledge base files in the current project. Use when the user wants to start documenting their project for claude-mega-brain, or when the user says "init mega brain", "setup the knowledge base", "cria o okf", "inicializa o mega brain", "quero usar o mega brain", "criar a estrutura do knowledge base", or asks how to get started with the plugin.
---

# init — Initialize OKF Knowledge Base

Creates a minimal set of OKF files so claude-mega-brain can start injecting context at the next session. No dedicated folder required — files can live anywhere in the project.

## What to create

Two files are enough to get started:

**`index.md`** — the knowledge map (put it at the project root or in `docs/`):

```markdown
---
type: Index
title: <Project Name> Knowledge Base
description: Central reference for all project knowledge.
timestamp: <today ISO 8601>
---

# <Project Name>

## Tables / Data
<!-- [orders](docs/orders.md) — one-liner -->

## Metrics
<!-- [wau](docs/wau.md) — one-liner -->

## APIs
<!-- [auth](docs/auth.md) — one-liner -->

## Services
<!-- [payments](docs/payments.md) — one-liner -->
```

**`log.md`** — append-only changelog (same location as index.md):

```markdown
---
type: Log
---
<today ISO date> — initialized OKF knowledge base
```

## Steps

1. Check if OKF files already exist — look for any `.md` with `type:` frontmatter. If found, tell the user and stop.
2. Detect project type (`package.json`, `pyproject.toml`, `go.mod`, etc.) to personalize the index template.
3. Ask the user where they want the files — suggest project root or `docs/` as default.
4. Write `index.md` and `log.md`.
5. Tell the user:
   - What was created and where
   - **Start a new Claude Code session** for context injection to activate
   - Add concepts with `/mega-brain:ingest` or create `.md` files with `type:` frontmatter anywhere in the project
   - Run `/mega-brain:migrate` to auto-populate from existing schemas and docs
