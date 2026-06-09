# Q2 Wave 3 Broker Batch 3 Lifecycle Event Envelope

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-28
Wave: `Wave 3 / Broker Acknowledgement And Reconciliation`
Mode: single-CLI execution
Related inputs:
- `openspec/changes/add-broker-acknowledgement-reconciliation-contract/`
- `docs/reports/quality/Q2_WAVE3_BROKER_ACK_RECONCILIATION_IMPLEMENTATION_PLAN_2026-04-27.md`
- `docs/reports/quality/Q2_WAVE3_BROKER_BATCH2_LOCAL_EXTERNAL_IDENTITY_PERSISTENCE_2026-04-28.md`
- `src/application/trading/order_mgmt_service.py`
- `src/application/trading/broker_order_correlation.py`
- `src/application/trading/broker_lifecycle_event.py`
- `src/utils/trading_runtime_config.py`
- `tests/ddd/test_phase_7_application.py`
- `tests/unit/core/test_runtime_config_governance.py`

## Purpose

Batch 2 created the durable local-to-external correlation surface, but the repository still
lacked the next required truth layer:

- a bounded broker lifecycle event envelope
- an ingestion path that resolves correlation through local submission or external identity
- explicit classification when identity or sequencing metadata is missing

This batch closes only that event-envelope gap. It does not let broker lifecycle events mutate
local order state, trigger reconciliation, or justify replay suppression.

## Implemented Scope

### 1. A dedicated broker lifecycle event envelope and ledger now exist

New local support module:

- `src/application/trading/broker_lifecycle_event.py`

It provides:

- `BrokerLifecycleEvent` as the minimum lifecycle event envelope
- in-memory event storage for default single-process use
- SQLite-backed durable event storage for restart-safe local inspection
- persisted event metadata covering:
  - `event_type`
  - `source_timestamp`
  - `source_name`
  - `event_id`
  - `sequence_id`
  - `external_order_id`
  - `local_submission_id`
  - `local_order_id`
  - `fill_quantity`
  - `fill_price`
  - `reason_code`
  - `reason_detail`
  - `identity_status`
  - `sequencing_status`

### 2. Correlation lookup now supports local submission identity

`src/application/trading/broker_order_correlation.py` now supports lookup by:

- `local_submission_id`

This is the narrow helper needed for broker acknowledgement events that arrive before any
external order id has already been bound into the correlation ledger.

### 3. `OrderManagementService` can now ingest broker lifecycle events without mutating order state

New application entrypoint:

- `record_broker_lifecycle_event(event)`

Current resolution priority is intentionally explicit:

1. `local_order_id`
2. `local_submission_id`
3. `external_order_id`

Current bounded behavior:

- acknowledgement events can bind `external_order_id` through an already-known
  `local_submission_id`
- execution, cancel, and reject events are durably recorded with the available identity and
  sequencing metadata
- the service classifies identity resolution as:
  - `matched_local_order_id`
  - `matched_local_submission_id`
  - `matched_external_order_id`
  - `unmatched_local_order_id`
  - `unmatched_local_submission_id`
  - `unmatched_external_order_id`
  - `missing_identity`
- the service classifies sequencing availability as:
  - `sequencing_metadata_present`
  - `sequencing_metadata_missing`

### 4. Runtime path governance now covers the broker lifecycle event ledger

`src/utils/trading_runtime_config.py` now exposes:

- `TRADING_BROKER_LIFECYCLE_EVENT_SQLITE_PATH`
- `get_trading_broker_lifecycle_event_sqlite_path()`

This keeps the new ledger aligned with the same local runtime storage convention used by the
other Wave 3 ledgers.

## What This Batch Does Not Claim

This batch does not claim:

- broker lifecycle events now drive canonical order state transitions
- unmatched broker events are fully reconciled
- divergence classes are complete
- replay suppression is safe
- sequencing metadata is always available from future adapters
- any trading path is `production-eligible`

The trading path remains `experimental`.

## Verification

Targeted lifecycle-envelope behavior:

- `pytest --no-cov tests/ddd/test_phase_7_application.py -q -k "broker_lifecycle_event"`
  - functional result: `4 passed`
  - interpretation: lifecycle event persistence, acknowledgement binding, external-identity
    execution matching, and explicit missing-identity classification now exist on the canonical
    local path

Application regression target:

- `pytest --no-cov tests/ddd/test_phase_7_application.py -q`
  - functional result: `40 passed`
  - interpretation: Batch 3 does not regress the current Wave 3 trading-safety application suite

Operator tooling regression target:

- `pytest --no-cov tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - interpretation: reservation-operator tooling remains behaviorally compatible after adding
    broker lifecycle event persistence

Runtime config regression target:

- `pytest --no-cov tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - interpretation: runtime path governance now covers the broker lifecycle event ledger
    without regressing existing config behavior

## Follow-Up

The next narrow batch should be:

1. `Batch 4: Divergence Ledger And Review Surface`

Do not jump from the current envelope directly to replay suppression or automatic resolution.
The next missing truth surface is durable divergence classification and review-required
incident retention.
