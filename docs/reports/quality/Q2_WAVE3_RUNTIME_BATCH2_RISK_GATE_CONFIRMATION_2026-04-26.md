# Q2 Wave 3 Runtime Batch 2 Risk Gate Confirmation

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RISK_GATE_AND_CONFIRMATION_POLICY_2026-04-26.md`
- `src/application/dto/trading_dto.py`
- `src/application/trading/order_mgmt_service.py`

## Purpose

This batch continues the runtime descent of the Wave 3 contract by introducing a minimal pre-submit risk gate and confirmation-or-bypass enforcement at the canonical placement path.

## Implemented Scope

### 1. Pre-submit gate hook

`OrderManagementService` now accepts an injectable `pre_submit_gate`.

The current gate contract supports:

- `allowed`
- `blocked`
- `confirmation_required`

This keeps policy evaluation inside the canonical placement path without hard-coding a full production risk engine.

### 2. Confirmation and bypass request fields

`CreateOrderRequest` now exposes:

- `confirmation_token`
- `bypass_reason`

The current runtime semantics are:

- `confirmation_required` plus `confirmation_token`:
  - order may continue
- `confirmation_required` plus `bypass_reason` and `actor_id`:
  - order may continue through `approved_bypass`
- `confirmation_required` without either:
  - order is stopped with `awaiting_confirmation`

### 3. Decision-point audit outcomes

The canonical placement path now emits decision outcomes for:

- `blocked_by_risk_gate`
- `awaiting_confirmation`
- `approved_bypass`

These are emitted before effective submission and therefore preserve the Wave 3 decision-point audit principle.

## What This Batch Does Not Claim

This batch does not claim:

- a production-grade risk engine is implemented
- confirmation tokens are cryptographically validated
- bypass approval is backed by a durable authorization workflow
- audit payloads are already durably persisted

## Verification

Targeted tests added:

- risk-gate block path
- confirmation-required hold path
- approved-bypass path

Primary test target:
- `pytest tests/ddd/test_phase_7_application.py -q`

## Follow-Up

The next runtime-hardening step should:

1. move decision audit into a durable sink
2. connect pre-submit gate inputs to real position / exposure / capital context
3. replace simple bypass semantics with an explicit approval contract
