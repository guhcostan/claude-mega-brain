# Agentic Benchmark — Obsidian+MCP vs mega-brain — 2026-06-29

**Real Claude Code sessions** (`claude -p`) · Claude Sonnet 4.6 · n=1 per question

## Summary

| metric | Obsidian+MCP | **mega-brain** |
|---|--:|--:|
| accuracy | 17% | **100%** |
| tool calls avg | 4.0 | **0** |
| turns avg | 5.0 | **1** |
| tokens avg | 175,461 | **16,025 (-91%)** |
| latency avg ms | 17,298 | **3,543 (-80%)** |

## Method

- **Obsidian+MCP**: Claude receives a filesystem MCP server pointing to a vault of plain markdown notes (no YAML schema). Uses `list_directory` and `read_file` tools to discover and read relevant notes before answering.
- **mega-brain**: OKF index injected at session start via `SessionStart` hook. Claude answers from the injected context — no tool calls needed.

The vault contains the same knowledge as the OKF base: orders table, customers table, WAU metric, net_revenue metric, changelog.

## Per-question results

| question | obsidian+MCP | mega-brain | obs tools | mb tools |
|---|:---:|:---:|--:|--:|
| amount_cents (exact column) | ✗ | ✓ | 3 | 0 |
| acme.com (exclusion filter) | ✗ | ✓ | 4 | 0 |
| refund_cents (deduction) | ✗ | ✓ | 8 | 0 |
| done (status value) | ✗ | ✓ | 3 | 0 |
| recent change | ✓ | ✓ | 2 | 0 |
| join key (customer_id) | ✗ | ✓ | 4 | 0 |

## Why Obsidian+MCP fails

The vault notes are written as generic prose without exact schema values.
Claude reads the files (3-8 tool calls, 5 turns average) but can't find project-specific facts like `amount_cents` or `acme.com` because they're not in the notes.

This validates the core OKF thesis: **format matters more than access**.
Having the right tool to read files is not enough — the content must be structured with exact values.

## Token efficiency

Obsidian+MCP averages **175k tokens** per question (tool call overhead × file reads × context accumulation).
mega-brain averages **16k tokens** per question — **91% fewer tokens**.

The OKF index is injected once at `SessionStart` and amortizes across all questions in a session.
