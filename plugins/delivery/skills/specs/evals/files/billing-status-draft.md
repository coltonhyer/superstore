---
type: spec
title: "Billing subscription status and invoice gating"
description: "Use the payment_overdue subscription status and reject invoice generation for payment_overdue accounts."
status: draft
tags: [billing, subscriptions]
---

# Billing Subscription Status and Invoice Gating

## Summary

Rename the observable subscription status from `past_due` to `payment_overdue`
and block invoice generation when an account has `payment_overdue` status.

## Goals and non-goals

- Goals:
  - Expose `payment_overdue` as the observable delinquent subscription status.
  - Reject invoice generation for `payment_overdue` accounts with `account_payment_overdue`.
- Non-goals:
  - Changing payment-retry intervals or invoice line-item schemas.

## Requirements and expected behavior

- `R1`: Subscription state handling in `app/billing.py` uses `payment_overdue` instead of `past_due`.
  - *Acceptance criterion:* When an account enters delinquency, its observable subscription status returned by billing status checks is `payment_overdue`.
- `R2`: Invoice generation requests for `payment_overdue` accounts are rejected with the `account_payment_overdue` error because API requests run the active-subscription guard, ensuring `payment_overdue` accounts cannot generate invoices.
  - *Acceptance criterion:* Given an account with status `payment_overdue`, when an invoice generation API request runs, it returns `account_payment_overdue` and issues no invoice.
- `R3`: Active accounts (status other than `payment_overdue`) continue to generate invoices without triggering the delinquency rejection.
  - *Acceptance criterion:* Given an active account, invoice generation succeeds and issues an invoice.
