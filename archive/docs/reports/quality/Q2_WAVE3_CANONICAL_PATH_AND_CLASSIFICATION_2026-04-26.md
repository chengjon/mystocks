# Q2 Wave 3 Canonical Path And Classification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Blocking Controls`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_PHASE_D_TRADING_SAFETY_CONTRACT_2026-04-25.md`
- `src/application/trading/order_mgmt_service.py`
- `src/trading/live_trading_engine.py`
- `src/trading/realtime_strategy_executor.py`

## Purpose

This note closes Wave 3 Batch 1 at the canonical-path and safety-classification layer.

It does not promote any trading path. It locks which path later controls must attach to.

## Canonical Placement Path

The canonical order-placement path for Q2 closure should be interpreted as:

1. `RealtimeStrategyExecutor`
2. `LiveTradingEngine`
3. `OrderManagementService.place_order()`
4. `IOrderRepository` persistence binding

This is the narrowest inspected path that currently expresses live-trading intent in the codebase.

## Current Safety Classification

### Simulated

- `src/interfaces/api/trading_router.py`
  - remains non-execution-complete and should not be treated as an active placement path

### Experimental

- `RealtimeStrategyExecutor`
- `LiveTradingEngine`
- `OrderManagementService.place_order()`

Reasoning:
- execution scaffolding exists
- repository persistence exists
- orchestration intent exists
- but no verified broker-path closure, blocking safety controls, or auditable idempotency contract exists

### Production-Eligible

No inspected path qualifies.

## Explicit Non-Claims

This batch does not claim:

- actual broker or exchange submission is verified in the canonical path
- order persistence equals execution closure
- stop-loss services prove production trading safety
- realtime orchestration implies `production-eligible` status

## Why This Lock Matters

Later Wave 3 controls must attach to one path, not to generic trading aspirations.

Without this lock, the project could incorrectly:

- attach policy only to docs and not to the real placement path
- confuse simulation surfaces with execution-capable surfaces
- overstate trading readiness based on supporting controls

## Follow-Up Constraint

Any later idempotency, risk-gate, confirmation, or audit requirement must be bound to this canonical placement path before the project can make stronger trading-safety claims.

## Broker Truth Overlay

This note should be read as a local placement-intent path lock, not as a broker-facing truth registry.

For the later broker acknowledgement and reconciliation line:

- this document identifies the narrowest inspected path that expresses trading intent
- but it does **not** prove verified external broker execution truth
- and it does **not** by itself select a canonical broker acknowledgement source

The broker-truth follow-up should therefore treat:

- `OrderManagementService` as the canonical local control anchor inside this chain
- upstream orchestration surfaces such as `RealtimeStrategyExecutor` and `LiveTradingEngine` as active callers, not as the first broker-truth implementation surface

Current registry reference:

- `docs/guides/quant-trading/broker-execution-truth-registry.md`
