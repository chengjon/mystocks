# Q2 Wave 3 Runtime Batch 11 Manual Release Audit Trail

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH10_STALE_RESERVATION_OPERATOR_TOOLING_2026-04-26.md`
- `scripts/runtime/trading_cash_reservations.py`
- `tests/unit/runtime/test_trading_cash_reservations_cli.py`

## Purpose

This batch closes the next obvious governance gap in Batch 10:
manual local reservation release should leave a durable audit trail with operator attribution.

The goal is attribution and local reconstructability only. This batch does not add broker-side validation.

## Implemented Scope

### 1. Actor-attributed manual release

The `release` command now requires:

- `--actor-id`

This keeps manual release actions attributable instead of anonymous.

### 2. Durable local audit binding

The reservation CLI now binds manual release actions to the existing local trading audit sink:

- JSONL
- SQLite

Current audited outcomes include:

- `manual_reservation_release`
- `manual_reservation_release_not_found`

Both successful release and not-found attempts are now durably recorded.

### 3. Minimal audit payload

The local audit record now preserves:

- `actor_id`
- `order_id`
- `decision_outcome`
- `decision_reason`
- `source_id=trading_cash_reservations_cli`

Successful releases also retain reservation context in the payload JSON:

- `portfolio_id`
- `reserved_notional`
- `reservation_updated_at`

## What This Batch Does Not Claim

This batch does not claim:

- broker/open-order validation before release
- automatic approval of local manual release
- central audit aggregation
- production-grade funds reconciliation

The execution path remains `experimental`.

## Verification

Operator tooling target:

- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `4 passed`
  - covered behavior now includes:
    - successful manual release audit persistence
    - not-found manual release attempt audit persistence
  - command still exits non-zero only because repo-wide total coverage remains below configured `fail-under=80`

Trading regression target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `20 passed`
  - command still exits non-zero only because the same repo-wide coverage threshold applies to narrow runs

## Follow-Up

The next bounded hardening choice should be one of:

1. reconcile local release actions against broker open orders or frozen funds,
2. add API/admin mediation over manual release instead of direct CLI-only operation,
3. or bind operator identity and release reason to a stronger governance approval workflow.
