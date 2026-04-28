# Q2 Wave 3 Broker Batch 1 Truth Registry Seed

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-27
Wave: `Wave 3 / Broker Acknowledgement And Reconciliation`
Mode: single-CLI execution
Related inputs:
- `openspec/changes/add-broker-acknowledgement-reconciliation-contract/`
- `docs/reports/quality/Q2_WAVE3_BROKER_ACK_RECONCILIATION_IMPLEMENTATION_PLAN_2026-04-27.md`
- `docs/reports/quality/Q2_WAVE3_CANONICAL_PATH_AND_CLASSIFICATION_2026-04-26.md`
- `src/application/trading/order_mgmt_service.py`
- `src/trading/live_trading_engine.py`
- `src/trading/realtime_strategy_executor.py`
- `src/interfaces/api/trading_router.py`
- `web/backend/app/api/trading_runtime.py`

## Purpose

This batch seeds the broker execution truth registry before any broker-facing implementation
starts.

Its job is not to add broker integration. Its job is to stop the next wave from attaching
broker-truth logic to the wrong runtime surface.

## Implemented Scope

### 1. A broker execution truth registry now exists

The project now has a dedicated registry:

- `docs/guides/quant-trading/broker-execution-truth-registry.md`

The registry records which surfaces are:

- canonical local control anchors
- upstream orchestration callers
- demo or stub surfaces
- still-missing broker-facing truth gaps

### 2. The canonical local anchor is explicitly locked

For broker acknowledgement and reconciliation follow-up, this batch locks:

- `src/application/trading/order_mgmt_service.py`

as the canonical local control anchor.

This means later broker-binding work should begin at the application-service layer and its
adjacent local ledgers, not at runtime demo APIs or incomplete route stubs.

### 3. Non-canonical trading surfaces are explicitly classified

This batch also classifies the most confusing adjacent surfaces:

- `src/interfaces/api/trading_router.py` as `stub`
- `web/backend/app/api/trading_runtime.py` as `demo`
- `src/trading/realtime_strategy_executor.py` as `experimental` upstream caller
- `src/trading/live_trading_engine.py` as `experimental` orchestration bridge

### 4. The earlier Wave 3 canonical-path note is now disambiguated

`Q2_WAVE3_CANONICAL_PATH_AND_CLASSIFICATION_2026-04-26.md` now includes a
broker-truth overlay so readers do not confuse:

- local placement-intent path lock

with:

- canonical broker acknowledgement source

## What This Batch Does Not Claim

This batch does not claim:

- a verified broker adapter already exists
- broker acknowledgement ingestion is implemented
- execution-report replay suppression is now safe
- local order-state evidence is broker-reconciled
- any current path is `production-eligible`

## Verification

Documentation verification:

- re-opened the seeded registry and confirmed all candidate paths are classified with role,
  scope, current state, and next action
- re-opened `docs/guides/quant-trading/INDEX.md` and confirmed the new registry is routed as
  an active supporting guide
- re-opened `Q2_WAVE3_CANONICAL_PATH_AND_CLASSIFICATION_2026-04-26.md` and confirmed the
  broker-truth overlay clarifies the difference between local canonical placement path and
  broker truth source

Spec validation:

- `openspec validate add-broker-acknowledgement-reconciliation-contract --strict`
  - result: `valid`

## Follow-Up

The next narrow batch should be:

1. `Batch 2: Local-To-External Order Identity Persistence`

Do not skip directly to replay suppression or duplicate execution-report handling before the
correlation surface exists.
