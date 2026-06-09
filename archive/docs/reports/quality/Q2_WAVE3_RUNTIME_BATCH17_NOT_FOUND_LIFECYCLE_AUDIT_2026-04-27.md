# Q2 Wave 3 Runtime Batch 17 Not-Found Lifecycle Audit

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-27
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH16_DENIAL_AUDIT_EVIDENCE_2026-04-27.md`
- `src/application/trading/order_mgmt_service.py`
- `tests/ddd/test_phase_7_application.py`
- `tests/unit/runtime/test_trading_cash_reservations_cli.py`
- `tests/unit/core/test_runtime_config_governance.py`

## Purpose

Batch 16 added denial audit evidence for invalid lifecycle transitions on existing orders.
One local audit hole still remained: operator or runtime attempts to `cancel` or `reject`
an order that does not exist left no lifecycle trace at all.

This batch closes that bounded gap by auditing not-found lifecycle attempts before
re-raising the same `ValueError`.

## Implemented Scope

### 1. `cancel_order(...)` and `reject_order(...)` now audit missing-order attempts

When the application service cannot load the target order, it now emits:

- `cancel_not_found`
- `reject_not_found`

The same `ValueError("Order not found: ...")` still propagates to the caller.
This batch adds evidence only; it does not alter control flow.

### 2. Missing-order audit payloads now preserve attempt context

Not-found lifecycle audit records now preserve:

- `request_identity` as the requested order id
- `order_id` as the missing order id
- `requested_reason`

Because there is no aggregate instance, business fields such as `symbol`, `side`,
`quantity`, `price`, and `order_type` remain `None`.

### 3. Canonical application tests now lock the missing-order audit contract

The application-path coverage now explicitly verifies:

- cancel missing order emits `cancel_not_found`
- reject missing order emits `reject_not_found`
- both paths retain the original `ValueError`

## What This Batch Does Not Claim

This batch does not claim:

- broker-side truth for missing order lookups
- reconciliation with external order ledgers
- deduplicated operator incident tracking
- stable machine-readable reason taxonomy beyond the current payload shape
- production-grade trading lifecycle governance

The execution path remains `experimental`.

## Verification

Targeted not-found audit target:

- `pytest tests/ddd/test_phase_7_application.py -k "audits_not_found_lifecycle_attempt" -q`
  - functional result: `2 passed`
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `3.46%`

Application regression target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `29 passed`
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `4.26%`

Operator tooling regression target:

- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `3.68%`

Runtime config regression target:

- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `3.72%`

## Follow-Up

The next bounded hardening choice should be one of:

1. normalize lifecycle denial and not-found reason fields into a stable machine-readable taxonomy,
2. add equivalent local audit evidence for other existing-order lifecycle entrypoints such as execution-report misses only if operators truly use that path,
3. or move outward to broker-fed lifecycle acknowledgement and reconciliation.
