# Q2 Wave 3 Runtime Batch 6 Pending Buy Cash Reservation

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH5_PORTFOLIO_AWARE_RISK_GATE_2026-04-26.md`
- `src/application/trading/order_mgmt_service.py`
- `src/application/trading/risk_gate.py`
- `src/application/bootstrap.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`
- `tests/ddd/test_phase_7_application.py`

## Purpose

This batch upgrades the portfolio-aware gate from snapshot-only cash checks to a lightweight single-process pending-buy reservation model.

## Implemented Scope

### 1. In-memory pending buy reservation ledger

`OrderManagementService` now maintains a local reservation ledger keyed by:

- `portfolio_id`
- `order_id`

Current reservation model:

- only BUY orders create cash reservations
- reservation amount is based on order notional
- reservations are updated or cleared when execution reports arrive
- the model is intentionally process-local and experimental

### 2. Reservation-aware capital gate

`build_portfolio_pre_submit_gate()` now optionally accepts:

- `pending_buy_notional_getter`

When bound, BUY orders are blocked if:

- the portfolio has enough raw cash,
- but available cash after subtracting pending BUY reservations is insufficient

Current blocking reason:

- `insufficient_available_cash_after_reservations`

### 3. Default runtime wiring

The default runtime builders now bind the reservation-aware getter in:

- `src/application/bootstrap.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`

This means the canonical placement path now evaluates pending BUY reservations by default instead of only raw cash snapshots.

## What This Batch Does Not Claim

This batch does not claim:

- multi-process or distributed reservation consistency
- database-backed reservation durability
- broker-side frozen-funds reconciliation
- reservation recovery after process restart

## Verification

Primary test target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `17 passed`
  - coverage gate still fails only because repo-wide total coverage remains below configured `fail-under=80`

Covered behaviors include:

- first pending BUY reserves notional cash
- second BUY is blocked when pending BUY reservations exhaust remaining cash
- execution reports reconcile or clear pending BUY reservations
- previously landed portfolio-aware gate and stop-loss compatibility tests remain green

Secondary regression check:

- `pytest tests/unit/core/test_runtime_config_governance.py::test_app_container_uses_role_aware_redis_kwargs -q`
  - functional result: `1 passed`
  - coverage gate still fails only because the same repo-wide threshold applies to narrow runs

## Follow-Up

The next hardening step should choose one of these bounded directions:

1. persist reservation state beyond process memory,
2. reconcile reservations against broker-side open orders and frozen funds,
3. or promote the current constructor defaults into explicit governance-configurable policy.
