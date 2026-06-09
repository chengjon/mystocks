# Q2 Wave 3 Broker Batch 2 Local-External Identity Persistence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-28
Wave: `Wave 3 / Broker Acknowledgement And Reconciliation`
Mode: single-CLI execution
Related inputs:
- `openspec/changes/add-broker-acknowledgement-reconciliation-contract/`
- `docs/reports/quality/Q2_WAVE3_BROKER_ACK_RECONCILIATION_IMPLEMENTATION_PLAN_2026-04-27.md`
- `docs/guides/quant-trading/broker-execution-truth-registry.md`
- `src/application/trading/order_mgmt_service.py`
- `src/application/trading/broker_order_correlation.py`
- `src/utils/trading_runtime_config.py`
- `tests/ddd/test_phase_7_application.py`
- `tests/unit/core/test_runtime_config_governance.py`

## Purpose

Batch 1 locked the canonical local anchor for later broker-truth work, but the repository still
lacked the first durable identity surface required by the OpenSpec contract:

- a local order submission could not remain explicitly `awaiting broker acknowledgement`
- an external broker order id could not be attached later through the same canonical local
  ledger

This batch closes only that identity-persistence gap. It does not introduce broker lifecycle
event ingestion, divergence auto-resolution, or replay suppression.

## Implemented Scope

### 1. A dedicated local broker-order correlation ledger now exists

New local support module:

- `src/application/trading/broker_order_correlation.py`

It provides:

- in-memory correlation storage for default single-process runtime use
- SQLite-backed durable correlation storage for restart recovery and bounded local lookup
- reverse lookup by `external_order_id`
- a default builder rooted in trading runtime path governance

### 2. `place_order(...)` now persists explicit awaiting-acknowledgement correlation state

The canonical application service now records a correlation row immediately after local order
persistence:

- `order_id`
- `local_submission_id`
- `adapter_path`
- `account_scope`
- `session_scope`
- `acknowledgement_status`
- `external_order_id`

Current bounded semantics:

- `local_submission_id` uses `idempotency_key`, then `request_id`, then local `order_id`
- `adapter_path` is explicitly recorded as the canonical local application submission path
- `account_scope` remains intentionally `unscoped` until a real broker-facing adapter path is
  selected
- `acknowledgement_status` starts as `awaiting_broker_acknowledgement`
- `external_order_id` remains empty until explicit broker acknowledgement binding occurs

### 3. External broker identity can now be attached later without heuristic matching

`OrderManagementService` now exposes:

- `record_broker_acknowledgement(order_id, external_order_id=...)`

This method:

- requires a known local order id
- binds the provided `external_order_id` onto the same canonical correlation record
- advances `acknowledgement_status` to `acknowledged`
- deliberately does not mutate local order status, fill quantity, or reservation state

### 4. Runtime path governance now covers the local broker correlation ledger

`src/utils/trading_runtime_config.py` now exposes:

- `TRADING_BROKER_ORDER_CORRELATION_SQLITE_PATH`
- `get_trading_broker_order_correlation_sqlite_path()`

This keeps the new durable ledger aligned with the existing local trading runtime storage
pattern instead of inventing a parallel path convention.

## What This Batch Does Not Claim

This batch does not claim:

- a verified broker-facing adapter now exists
- current `account_scope = unscoped` is production-acceptable
- broker acknowledgement events are already ingested from an external source
- execution reports are replay-safe
- local order state is broker-reconciled
- any trading path is `production-eligible`

The trading path remains `experimental`.

## Verification

Targeted broker-correlation behavior:

- `pytest --no-cov tests/ddd/test_phase_7_application.py -q -k "broker_order_correlation or broker_acknowledgement"`
  - functional result: `3 passed`
  - interpretation: the new ledger supports durable submission persistence, later external-id
    binding, and the application service now writes the explicit awaiting-acknowledgement state

Application regression target:

- `pytest --no-cov tests/ddd/test_phase_7_application.py -q`
  - functional result: `36 passed`
  - interpretation: the Batch 2 correlation ledger does not regress the current Wave 3
    trading-safety application suite

Operator tooling regression target:

- `pytest --no-cov tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - interpretation: reservation-operator tooling remains behaviorally compatible after adding
    broker-correlation persistence

Runtime config regression target:

- `pytest --no-cov tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - interpretation: runtime path governance now covers the new broker-correlation ledger
    without regressing existing config behavior

## Follow-Up

The next narrow batch should be:

1. `Batch 3: Broker Lifecycle Event Envelope`

Do not jump from this ledger directly to replay suppression or automatic reconciliation. The
next missing truth surface is the broker lifecycle event identity contract itself.
