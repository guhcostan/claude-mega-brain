---
type: Metric
title: Weekly Active Users
description: Count of unique users with at least one session in rolling 7 days.
tags: [engagement, retention]
timestamp: 2026-06-15T00:00:00Z
---

# Definition
`COUNT(DISTINCT user_id)` where `session_date >= CURRENT_DATE - 7`.

# Notes
- Rolling window, not calendar week.
- Excludes internal test accounts (`email LIKE '%@acme.com'`).
