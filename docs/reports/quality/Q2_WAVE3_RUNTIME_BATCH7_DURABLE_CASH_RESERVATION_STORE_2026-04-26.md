# Q2 Wave 3 Runtime Batch 7 Durable Cash Reservation Store

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH6_PENDING_BUY_CASH_RESERVATION_2026-04-26.md`
- `src/application/trading/cash_reservation.py`
- `src/application/trading/order_mgmt_service.py`
- `src/application/bootstrap.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`
- `tests/ddd/test_phase_7_application.py`

## Purpose

This batch closes the narrowest operational gap left by Batch 6:
process-local pending BUY reservations were lost on service restart.

The goal is local restart recovery only. This batch does not attempt to solve
distributed consistency or broker-side frozen-funds truth.

## Implemented Scope

### 1. Local reservation store abstraction

A dedicated reservation module now exists:

- `InMemoryPortfolioCashReservationStore`
- `SqlitePortfolioCashReservationStore`
- `build_default_portfolio_cash_reservation_store()`

The in-memory store preserves the existing low-friction test/runtime path.
The SQLite store adds a local durable ledger for pending BUY reservations.

### 2. Order service integration

`OrderManagementService` now accepts an injectable cash reservation store.

Current runtime behavior:

- successful BUY submission writes or updates a reservation record
- execution reports reconcile remaining reserved notional
- full fill or zero remaining notional removes the reservation record
- `get_pending_buy_notional_for_portfolio()` now reads from the configured store instead of only process memory

### 3. Default runtime wiring

Default runtime builders now bind a local SQLite reservation ledger in:

- `src/application/bootstrap.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`

This means the canonical single-process trading path now keeps pending BUY reservations recoverable across service instance recreation on the same host.

## What This Batch Does Not Claim

This batch does not claim:

- multi-process reservation locking
- distributed reservation consensus
- broker-side frozen cash reconciliation
- automatic rebuild from external open-order truth
- production-grade real-money capital accounting

The execution path remains `experimental`.

## Verification

Primary test target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `19 passed`
  - new covered behavior includes SQLite-backed reservation recovery across service restart
  - command still exits non-zero only because repo-wide total coverage remains below configured `fail-under=80`

Secondary regression check:

- `pytest tests/unit/core/test_runtime_config_governance.py::test_app_container_uses_role_aware_redis_kwargs -q`
  - functional result: `1 passed`
  - command still exits non-zero only because the same repo-wide coverage threshold applies to narrow runs

Covered behaviors include:

- existing pending BUY reservation gate still blocks oversubscription
- execution reports still reconcile and clear reservations
- SQLite reservation ledger survives service recreation
- default reservation store builder writes to a local SQLite ledger
- bootstrap/runtime container wiring remains behaviorally compatible in targeted scope

## Follow-Up

The next bounded hardening choice should be one of:

1. reconcile local reservations against broker open orders or frozen funds,
2. add restart-time sanity checks for stale reservation records,
3. or externalize reservation policy and ledger paths into explicit governance/runtime config.
