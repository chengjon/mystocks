# Q2 Wave 3 Broker Batch 4 Divergence Ledger And Review Surface

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-28
Wave: `Wave 3 / Broker Acknowledgement And Reconciliation`
Mode: single-CLI execution
Related inputs:
- `openspec/changes/add-broker-acknowledgement-reconciliation-contract/`
- `docs/reports/quality/Q2_WAVE3_BROKER_ACK_RECONCILIATION_IMPLEMENTATION_PLAN_2026-04-27.md`
- `src/application/trading/order_mgmt_service.py`
- `src/application/trading/broker_divergence.py`
- `src/application/trading/broker_lifecycle_event.py`
- `src/application/trading/broker_order_correlation.py`
- `src/utils/trading_runtime_config.py`
- `tests/ddd/test_phase_7_application.py`
- `tests/unit/core/test_runtime_config_governance.py`

## Purpose

Batch 3 made broker lifecycle events durable, but the repository still lacked the next
required truth surface:

- stable divergence classification for local-versus-broker mismatch
- a durable review-required incident ledger
- evidence retention that stops short of automatic resolution

This batch closes only that divergence-evidence gap. It does not rewrite order state, suppress
replay, or attempt automatic reconciliation.

## Implemented Scope

### 1. A dedicated broker divergence ledger now exists

New local support module:

- `src/application/trading/broker_divergence.py`

It provides:

- `InMemoryTradingBrokerDivergenceStore` for process-local use
- `SqliteTradingBrokerDivergenceStore` for restart-safe durable evidence
- `build_default_trading_broker_divergence_store()`

Persisted incident metadata covers:

- `divergence_category`
- `review_status`
- `review_owner`
- `next_action`
- `required_evidence`
- `order_id`
- `event_type`
- `external_order_id`
- `local_submission_id`
- `local_order_id`
- `local_order_status`
- `identity_status`
- `sequencing_status`
- `reported_filled_quantity`
- `reported_fill_price`
- `reason_code`
- `reason_detail`

### 2. `OrderManagementService` now emits review-required divergence incidents

`record_broker_lifecycle_event(event)` now preserves the original event record and, when
appropriate, appends a separate divergence incident without mutating local order state.

Current classification rules are intentionally narrow:

- unmatched execution facts become `unmatched_external_order`
- execution against a locally terminal order becomes `locally_terminal_externally_open`
- broker cancel/reject against an open local order becomes `externally_terminal_locally_open`
- impossible fill quantities become `quantity_or_fill_divergence`
- non-ack events that arrive while the correlation still awaits broker acknowledgement can
  surface as `awaiting_broker_acknowledgement`

All emitted divergence incidents are stamped as:

- `review_status = review_required`
- `review_owner = trading_operations`
- `next_action = manual_reconciliation_required`

### 3. Runtime path governance now covers the divergence ledger

`src/utils/trading_runtime_config.py` now exposes:

- `TRADING_BROKER_DIVERGENCE_SQLITE_PATH`
- `get_trading_broker_divergence_sqlite_path()`

This keeps the new ledger aligned with the same local runtime storage convention used by the
other Wave 3 ledgers.

## What This Batch Does Not Claim

This batch does not claim:

- broker divergence is fully auto-resolved
- replay suppression is safe
- broker lifecycle events now rewrite local order state
- quantity/price coincidence alone is sufficient to justify reconciliation
- any trading path is `production-eligible`

The trading path remains `experimental`.

## Verification

Targeted divergence-ledger behavior:

- `pytest --no-cov tests/ddd/test_phase_7_application.py -q -k "broker_divergence or unmatched_external_order_divergence or locally_terminal_externally_open_divergence or externally_terminal_locally_open_divergence or quantity_or_fill_divergence_without_mutating_local_state"`
  - functional result: `5 passed`
  - interpretation: durable review-required divergence incidents now exist on the canonical local path

Application regression target:

- `pytest --no-cov tests/ddd/test_phase_7_application.py -q`
  - functional result: `45 passed`
  - interpretation: Batch 4 does not regress the current Wave 3 trading-safety application suite

Runtime config regression target:

- `pytest --no-cov tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - interpretation: runtime path governance now covers the broker divergence ledger without
    regressing existing config behavior

Operator tooling regression target:

- `pytest --no-cov tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - interpretation: reservation-operator tooling remains compatible after adding divergence evidence

## Follow-Up

The next narrow batch should be:

1. `Batch 5: Bounded Auto-Resolution And Replay-Suppression Gate`

Do not jump from durable divergence evidence directly to production-grade replay suppression.
The next missing truth surface is the explicit policy boundary for when stronger broker-side
identity evidence is sufficient.
