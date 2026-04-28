# Q2 Wave 3 Runtime Batch 15 Reject Transition Guards

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-27
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH14_CANCEL_REJECT_LIFECYCLE_EVIDENCE_2026-04-26.md`
- `src/domain/trading/model/order.py`
- `tests/ddd/test_phase_7_application.py`
- `tests/unit/runtime/test_trading_cash_reservations_cli.py`
- `tests/unit/core/test_runtime_config_governance.py`

## Purpose

Batch 14 added local `reject_order(...)` lifecycle handling, but the domain aggregate still
allowed invalid reject transitions after the order had already moved into non-rejectable states.

This batch closes that gap by making local reject evidence more internally coherent:

- a partially filled order can no longer be rewritten into `REJECTED`,
- a cancelled order can no longer be rewritten into `REJECTED`,
- and failed reject attempts now preserve the last valid local reservation and order-state evidence.

The goal is still bounded to local application truth. This batch does not claim broker truth.

## Implemented Scope

### 1. `Order.reject()` now enforces an explicit allowed-state guard

The trading aggregate now only allows reject transitions from:

- `CREATED`
- `SUBMITTED`

For any other state, `reject()` now raises `RuntimeError`.

This prevents local runtime code from fabricating impossible lifecycle history after:

- partial execution,
- cancellation,
- prior rejection,
- or any other later terminal / progressed state.

### 2. Application-path regression tests now lock the invalid transition contract

Two new application-level tests cover the canonical path:

- reject after partial fill must fail and preserve `PARTIALLY_FILLED`
- reject after cancel must fail and preserve `CANCELLED`

The tests also verify that:

- existing cash-reservation state is not incorrectly released or rewritten on failed reject attempts,
- and no extra successful reject audit outcome is emitted for the denied path.

## What This Batch Does Not Claim

This batch does not claim:

- broker-acknowledged reject truth
- broker-side cancel / reject reconciliation
- denial-path audit persistence for failed lifecycle attempts
- operator workflow completion for invalid lifecycle review
- production-grade real-trading execution safety

The execution path remains `experimental`.

## Verification

Targeted red-to-green transition check:

- `pytest tests/ddd/test_phase_7_application.py -k "reject_order_disallows" -q`
  - functional result after fix: `2 passed`
  - covered behavior now includes:
    - reject-after-partial-fill is denied
    - reject-after-cancel is denied
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `3.64%`

Application regression target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `26 passed`
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `3.91%`

Operator tooling regression target:

- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `2.13%`

Runtime config regression target:

- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `2.90%`

## Follow-Up

The next bounded hardening choice should be one of:

1. add explicit denial-path audit evidence for invalid cancel / reject attempts,
2. add duplicate-reject and filled-state reject tests if the local path continues expanding,
3. or move the lifecycle truth line outward to broker-fed cancel / reject acknowledgement.
