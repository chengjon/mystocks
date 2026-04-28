# Q2 Wave 3 Runtime Batch 20 Execution-Report Denial Audit

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-27
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH18_LIFECYCLE_REASON_TAXONOMY_2026-04-27.md`
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH19_EXECUTION_REPORT_NOT_FOUND_AUDIT_2026-04-27.md`
- `src/application/trading/order_mgmt_service.py`
- `tests/ddd/test_phase_7_application.py`
- `tests/unit/runtime/test_trading_cash_reservations_cli.py`
- `tests/unit/core/test_runtime_config_governance.py`

## Purpose

Batch 19 closed the missing-order audit gap for execution reports, but one bounded runtime
blind spot still remained:

- if a local order exists but the aggregate rejects the fill, the service re-raises the
  domain exception without leaving denial audit evidence.

This batch closes only that local evidence gap. It does not attempt true deduplication,
broker reconciliation, or distributed idempotency.

## Implemented Scope

### 1. `handle_execution_report(...)` now audits denied fill attempts

When the local order is found but `order.fill(...)` rejects the execution input, the
application service now emits:

- `execution_report_denied`

The same exception still propagates to the caller unchanged.

### 2. Stable denial reason taxonomy is extended to execution-report failures

The runtime now normalizes bounded denial reasons for this entrypoint:

- `invalid_order_status_transition`
- `fill_quantity_exceeds_remaining_quantity`
- `invalid_fill_quantity`

If a future denial does not match one of the explicit local mappings, the fallback remains:

- `execution_report_denied`

### 3. Local troubleshooting evidence is preserved without mutating state

Denied execution-report audit payloads now preserve:

- `current_order_status`
- `decision_reason_detail`
- `reported_filled_quantity`
- `reported_fill_price`

Because the fill is denied before persistence, this batch intentionally preserves prior local
state:

- no synthetic recovery path
- no forced status rewrite
- no reservation reconciliation on failed fill

## What This Batch Does Not Claim

This batch does not claim:

- broker-side execution truth
- duplicate execution-report suppression
- replay-safe fill idempotency
- external reconciliation with broker or OMS ledgers
- production-grade post-trade control guarantees

The execution path remains `experimental`.

## Verification

Targeted denial-audit regression target:

- `pytest tests/ddd/test_phase_7_application.py -k "denied_fill_after_cancelled_terminal_state or denied_overfill_attempt_and_preserves_partial_state" -q`
  - functional result: `2 passed`
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `3.66%`

Application regression target:

- `pytest --no-cov tests/ddd/test_phase_7_application.py -q`
  - functional result: `32 passed`
  - interpretation: denied execution-report audit evidence does not regress the current Wave 3 trading-safety application suite

Operator tooling regression target:

- `pytest --no-cov tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - interpretation: reservation operator tooling remains behaviorally compatible after the execution-report denial-audit change

Runtime config regression target:

- `pytest --no-cov tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - interpretation: current runtime config and composition-root wiring remain compatible after the Batch 20 change

## Follow-Up

The next bounded hardening choice should remain narrow:

1. decide whether execution-report replay input needs true idempotency or only stronger duplicate-like evidence,
2. define whether other post-submit ingress paths need the same denial-audit treatment,
3. or stop runtime hardening here and move outward to broker acknowledgement and reconciliation design.
