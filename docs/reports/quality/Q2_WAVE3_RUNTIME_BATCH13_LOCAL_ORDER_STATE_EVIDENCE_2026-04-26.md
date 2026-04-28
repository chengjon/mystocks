# Q2 Wave 3 Runtime Batch 13 Local Order-State Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH12_RISK_TIERED_RELEASE_GATE_2026-04-26.md`
- `scripts/runtime/trading_cash_reservations.py`
- `src/application/trading/order_mgmt_service.py`
- `tests/unit/runtime/test_trading_cash_reservations_cli.py`
- `tests/ddd/test_phase_7_application.py`

## Purpose

This batch extends the Batch 12 release gate with one additional local fact:
the last known order lifecycle state on the canonical application path.

The objective is narrow and explicit:

- allow more fresh reservations to be auto-released when local order evidence is terminal,
- keep active-order cases out of automatic release,
- and still avoid pretending that broker truth already exists.

## Implemented Scope

### 1. A durable local order-state evidence store now exists

A dedicated local store now exists for last-known order state:

- `InMemoryTradingOrderStateStore`
- `SqliteTradingOrderStateStore`

Default runtime wiring now uses:

- `var/log/trading/trading-order-state.sqlite3`

This store is reconstruction-oriented only. It is not broker reconciliation.

### 2. Canonical order placement path now records local order-state evidence

`OrderManagementService` now writes local order-state evidence on:

- successful submit
- execution report handling

This means the same runtime line that creates and reconciles reservations now also leaves a durable local view of:

- `SUBMITTED`
- `PARTIALLY_FILLED`
- `FILLED`

The store also preserves `portfolio_id` across later lifecycle updates.

### 3. Reservation CLI now uses local order-state evidence

The reservation operator CLI now accepts:

- `--order-state-sqlite-path`

Fresh reservation release behavior is now refined as:

- local order state is terminal
  - `terminal_order_state_auto_release`
- local order state is active
  - `active_order_state_requires_review`
- no local order state evidence
  - fall back to Batch 12 age/review policy

This gives the tool one more bounded automatic release path without over-claiming external execution certainty.

### 4. Audit payload now records order-state evidence context

When local order-state evidence is present, the audit payload now also records:

- `order_state_status`
- `order_state_updated_at`
- `order_state_symbol`
- `order_state_portfolio_id`

## What This Batch Does Not Claim

This batch does not claim:

- broker open-order truth
- counterparty acknowledgement truth
- frozen-funds reconciliation
- cancel/reject ingestion from an external broker adapter
- production-grade real-trading release safety

The execution path remains `experimental`.

## Verification

Operator tooling target:

- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - covered behavior now includes:
    - fresh reservation auto-release when local order state is terminal
    - fresh reservation review-required rejection when local order state is active
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `3.61%`

Trading regression target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `22 passed`
  - covered behavior now includes:
    - default local SQLite order-state store
    - submit -> filled lifecycle persistence
    - portfolio context retention across state updates
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `3.87%`

Runtime config target:

- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `4.19%`

Note:
- one earlier parallel verification pass hit a `pytest-cov` coverage SQLite concurrency artifact while tests themselves had already passed
- the final Phase 7 verification above was rerun serially to confirm a clean functional result

## Follow-Up

The next bounded hardening choice should be one of:

1. bind local terminal order-state evidence to real broker or counterparty acknowledgements,
2. ingest cancel / reject transitions from the actual execution path instead of only submit / fill lifecycle points,
3. or define when active local order evidence should escalate from single-operator review to dual control.
