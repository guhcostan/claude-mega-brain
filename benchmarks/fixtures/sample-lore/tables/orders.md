---
type: BigQuery Table
title: Orders
description: One row per completed customer order, including payment and shipping status.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, revenue, transactions]
timestamp: 2026-06-01T00:00:00Z
---

# Schema
| Column        | Type      | Description                          |
|---------------|-----------|--------------------------------------|
| order_id      | STRING    | Globally unique order identifier     |
| customer_id   | STRING    | FK to [customers](customers.md)      |
| created_at    | TIMESTAMP | Order creation time (UTC)            |
| total_cents   | INT64     | Order total in cents before refunds  |
| status        | STRING    | pending / confirmed / shipped / done |

# Joins
Joined with [customers](customers.md) on `customer_id`.
