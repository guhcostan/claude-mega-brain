# Benchmark Results — vs Competitors — 2026-06-29

**3-way comparison** · Claude Sonnet 4.6 · n=5 · temperature=0

## Summary

| metric | baseline | raw-dump (Aider-style) | **mega-brain** |
|---|--:|--:|--:|
| accuracy | 20% | 17% ❌ | **100%** ✓ |
| completion tokens avg | 119 | 97 | **34 (-71%)** |
| prompt tokens avg | 20 | 150 | 193 |
| latency avg ms | 3 826 | 3 587 | **1 938 (-49%)** |

## Conditions

- **baseline**: plain question, no context
- **raw-dump**: generic prose descriptions of tables/metrics (simulates Aider-style or naive "dump docs" approach — no exact schema, no types, no column names)
- **mega-brain**: structured OKF data dictionary with exact column names, types, formulas, and changelog

## Key finding

Raw-dump **costs more tokens than baseline (+130 prompt tokens) but performs worse** (17% vs 20%).
Generic context without the exact schema values creates noise — the model hedges more.

Mega-brain's structured OKF format is what drives the 100% accuracy: the exact values are right there, no interpretation needed.

## Per-question breakdown

| question | baseline | raw-dump | mega-brain |
|---|:---:|:---:|:---:|
| amount_cents (exact column) | 0% | 0% | **100%** |
| acme.com (exclusion filter) | 0% | 0% | **100%** |
| refund_cents (deduction) | 0% | 0% | **100%** |
| done (status value) | 20% | 0% | **100%** |
| recent change (log.md) | 0% | 50% | **100%** |
| join key (customer_id) | 100% | 50% | **100%** |

## Why raw-dump loses

Aider and similar tools inject raw file content or generic descriptions. Without a structured format that specifies:
- exact column names and types
- exact formula fields
- exact enum values
- exact exclusion filters
- a changelog

…the model falls back to training data guesses and hedges.

## Reproduce

```bash
export ANTHROPIC_API_KEY=your-key
npx promptfoo@latest eval -c benchmarks/promptfooconfig.yaml --repeat 5 --no-cache
```
