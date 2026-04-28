# Q2 Wave 3 Runtime Batch 8 Stale Reservation Review Gate

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH7_DURABLE_CASH_RESERVATION_STORE_2026-04-26.md`
- `src/application/trading/cash_reservation.py`
- `src/application/trading/order_mgmt_service.py`
- `src/application/trading/risk_gate.py`
- `src/application/bootstrap.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`
- `tests/ddd/test_phase_7_application.py`

## Purpose

This batch closes the next narrow gap left by Batch 7:
local durable reservations can survive restart, but an old unresolved reservation
should not be silently treated as clean capital.

The chosen policy is conservative:

- identify stale pending BUY reservations from the local ledger
- block new BUY submissions for that portfolio
- force manual review instead of auto-pruning the stale record

## Implemented Scope

### 1. Reservation staleness inspection

The reservation stores now support stale-record inspection through:

- `fetch_stale(max_age_seconds)`

Both in-memory and SQLite stores can now surface reservations older than the configured age threshold.

### 2. Order service exposure

`OrderManagementService` now exposes:

- `has_stale_cash_reservations_for_portfolio(portfolio_id, max_age_seconds)`

This keeps stale-check logic outside API/controller code and preserves the current application-service ownership boundary.

### 3. Conservative pre-submit blocking

`build_portfolio_pre_submit_gate()` now accepts an optional stale reservation checker.

When bound, a BUY request is blocked before placement if its portfolio still has stale pending BUY reservations.

Current blocking reason:

- `stale_pending_buy_reservations_require_review`

### 4. Default runtime wiring

Default runtime builders now bind the stale-reservation checker in:

- `src/application/bootstrap.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`

Current default threshold:

- `86400` seconds (`24h`)

This threshold is intentionally conservative and local-runtime scoped.

## What This Batch Does Not Claim

This batch does not claim:

- automatic stale record deletion
- broker-side confirmation that a stale reservation is safe to release
- cross-process stale reservation coordination
- production-grade frozen-cash truth

The execution path remains `experimental`.

## Verification

Primary test target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `20 passed`
  - new covered behavior includes blocking BUY orders when stale pending BUY reservations require review
  - command still exits non-zero only because repo-wide total coverage remains below configured `fail-under=80`

Secondary regression check:

- `pytest tests/unit/core/test_runtime_config_governance.py::test_app_container_uses_role_aware_redis_kwargs -q`
  - functional result: `1 passed`
  - command still exits non-zero only because the same repo-wide coverage threshold applies to narrow runs

Covered behaviors include:

- existing durable reservation recovery still works
- existing reservation-aware cash gate still blocks oversubscription
- stale local reservations now trigger a conservative BUY review block
- default runtime container wiring remains behaviorally compatible in targeted scope

## Follow-Up

The next bounded hardening choice should be one of:

1. externalize stale threshold and ledger paths into runtime governance config,
2. add broker/open-order reconciliation to distinguish truly stale reservations from still-live external orders,
3. or add operator-facing inspection tooling for local reservation review and release workflows.
