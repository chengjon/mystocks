# Q2 Wave 3 Runtime Batch 5 Portfolio-Aware Risk Gate

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RISK_GATE_AND_CONFIRMATION_POLICY_2026-04-26.md`
- `src/application/trading/risk_gate.py`
- `src/application/trading/order_mgmt_service.py`
- `src/application/bootstrap.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`
- `tests/ddd/test_phase_7_application.py`

## Purpose

This batch moves the pre-submit gate from policy-only injection to a real synchronous portfolio context check on the canonical placement path.

## Implemented Scope

### 1. Request-level portfolio context anchor

`CreateOrderRequest` now carries:

- `portfolio_id`

This provides the minimum runtime anchor needed to evaluate capital and position rules before persistence.

### 2. Portfolio-aware blocking gate

A new synchronous gate now exists:

- `build_portfolio_pre_submit_gate()`

Current hard-blocking rules:

- missing portfolio context blocks the order
- missing portfolio snapshot blocks the order
- BUY orders without an evaluable price block the order
- BUY orders with insufficient cash block the order
- BUY orders that would exceed the configured single-symbol weight cap block the order
- SELL orders that exceed the currently held position quantity block the order

### 3. Default runtime wiring

Default `OrderManagementService` creation in:

- `src/application/bootstrap.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`

now binds the portfolio-aware pre-submit gate by default.

### 4. Stop-loss compatibility closure

The stop-loss execution path now emits a canonical sell request shape compatible with the new gate:

- `side="SELL"`
- `order_type="MARKET"`
- `portfolio_id=position.portfolio_id`

This keeps the default stop-loss order path from silently diverging from the canonical request contract.

## What This Batch Does Not Claim

This batch does not claim:

- real broker-side position reconciliation
- intraday capital reservations
- multi-portfolio net exposure aggregation
- production-grade risk limits beyond the current synchronous portfolio snapshot

## Verification

Primary test target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `15 passed`
  - coverage gate still fails only because repo-wide total coverage remains below configured `fail-under=80`

Covered behaviors include:

- missing `portfolio_id` blocks order submission
- insufficient cash blocks BUY submission
- projected symbol concentration blocks BUY submission
- insufficient held quantity blocks SELL submission
- stop-loss execution emits a portfolio-aware canonical SELL request

Secondary regression check:

- `pytest tests/unit/core/test_runtime_config_governance.py::test_app_container_uses_role_aware_redis_kwargs -q`
  - functional result: `1 passed`
  - coverage gate still fails only because the same repo-wide threshold applies to narrow runs

## Follow-Up

The next hardening step should choose one of these bounded directions:

1. replace snapshot-only cash checks with reservation-aware capital accounting,
2. add centralized ingestion for decision audit ledgers,
3. or bind portfolio-aware limits to configurable governance policy instead of current constructor defaults.
