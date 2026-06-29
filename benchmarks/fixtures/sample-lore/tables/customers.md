---
type: BigQuery Table
title: Customers
description: Customer profile and contact data, one row per registered account.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=customers
tags: [customers, identity]
timestamp: 2026-06-29T00:00:00Z
---

# Schema
| Column       | Type      | Description                    |
|--------------|-----------|--------------------------------|
| customer_id  | STRING    | Globally unique customer ID    |
| email        | STRING    | Primary email address          |
| country      | STRING    | ISO 3166-1 alpha-2 country     |
| created_at   | TIMESTAMP | Account registration time      |

# Joins
Joined with [orders](orders.md) on `customer_id`.
