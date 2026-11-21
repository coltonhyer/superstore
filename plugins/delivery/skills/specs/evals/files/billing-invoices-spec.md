---
type: spec
title: "Workspace billing invoices"
description: "Generate and list monthly PDF billing invoices for workspace accounts."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [billing, invoices]
---

# Workspace Billing Invoices

## Summary

Generate monthly PDF billing invoices for each active workspace and list them for billing contacts.

## Goals and non-goals

- Goals:
  - Issue monthly PDF invoices and expose an invoice history list.
- Non-goals:
  - Real-time usage metering exports.

## Requirements and expected behavior

- `R1`: Each workspace billing cycle produces a PDF invoice summarizing subscription charges.
  - *Acceptance criterion:* Completing a billing cycle exposes a downloadable PDF invoice in the workspace invoice list.
- `R2`: Only billing contacts and workspace administrators may view or download workspace invoices.
  - *Acceptance criterion:* Non-privileged workspace members requesting an invoice receive HTTP 403.
