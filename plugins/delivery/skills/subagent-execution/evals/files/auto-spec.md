---
type: spec
title: "Auto status specification"
description: "`status_label(active)` returns `enabled` when `active` is truthy and `disabled` otherwise."
status: stable
verified: { by: process:delivery-autonomous, at: 2026-10-01T12:00:00Z }
tags: [auto]
---

# Auto status specification

## Summary

`status_label(active)` formats a boolean-like state as `enabled` or `disabled`.

## Goals and non-goals

- Goal: return `enabled` for truthy `active` and `disabled` otherwise.
- Non-goal: localization or custom status labels.

## Requirements and expected behavior

- **R1:** `status_label(True)` returns `"enabled"` and `status_label(False)`
  returns `"disabled"`.
