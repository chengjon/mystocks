# Q2 Wave 3 Runtime Batch 19 Execution-Report Not-Found Audit

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-27
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH17_NOT_FOUND_LIFECYCLE_AUDIT_2026-04-27.md`
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH18_LIFECYCLE_REASON_TAXONOMY_2026-04-27.md`
- `src/application/trading/order_mgmt_service.py`
- `tests/ddd/test_phase_7_application.py`
- `tests/unit/runtime/test_trading_cash_reservations_cli.py`
- `tests/unit/core/test_runtime_config_governance.py`

## Purpose

Batch 17 closed the local audit gap for missing-order `cancel` and `reject` attempts, but
the execution-report path still had one bounded blind spot:

- if a fill report arrives for an unknown local order id, the service raises `ValueError`
  without leaving local decision evidence.

That left replay and runtime troubleshooting weaker for one more lifecycle entrypoint.

This batch closes only that gap by auditing execution-report misses before re-raising the
same `ValueError`.

## Implemented Scope

### 1. `handle_execution_report(...)` now audits missing local order evidence

When the application service cannot load the target order for an execution report, it now
emits:

- `execution_report_not_found`

The same stable reason taxonomy from Batch 18 is reused:

- `decision_reason = order_not_found`
- `decision_reason_detail = Order not found: ...`

The same `ValueError` still propagates to the caller.

### 2. Execution-report attempt context is preserved

The local audit payload now also preserves the reported execution input:

- `reported_filled_quantity`
- `reported_fill_price`

Because no aggregate instance exists, business fields such as `symbol`, `side`, `quantity`,
`price`, and `order_type` remain `None`.

### 3. Storage scope remains intentionally unchanged

This batch does not widen the durable sink schema or add query indexes.

The extra fields remain preserved through the existing payload path in:

- JSONL audit records
- SQLite `payload_json`

## What This Batch Does Not Claim

This batch does not claim:

- broker-side execution truth
- reconciliation with external order ledgers
- duplicate execution-report suppression
- distributed execution-report incident correlation
- production-grade post-trade lifecycle governance

The execution path remains `experimental`.

## Verification

Targeted execution-report miss regression target:

- `pytest tests/ddd/test_phase_7_application.py -k "handle_execution_report_audits_missing_order_attempt" -q`
  - functional result: `1 passed`
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `3.46%`

Application regression target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `30 passed`
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `4.28%`

Operator tooling regression target:

- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `3.70%`

Runtime config regression target:

- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `3.73%`

## Follow-Up

The next bounded hardening choice should be one of:

1. decide whether execution-report input itself needs idempotency or duplicate-suppression evidence,
2. define whether other post-submit entrypoints need the same missing-order audit pattern,
3. or move outward from local evidence to broker-fed acknowledgement and reconciliation.
