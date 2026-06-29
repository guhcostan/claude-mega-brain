---
type: Metric
title: Net Revenue
description: Total net revenue after refunds in a given period.
tags: [revenue, finance]
timestamp: 2026-06-01T00:00:00Z
---

# Definition
`SUM(total_cents - refund_cents) / 100` from [orders](../tables/orders.md)
where `status = 'done'` and `created_at` is within the period.

# Notes
- Denominated in USD.
- Excludes test orders.
