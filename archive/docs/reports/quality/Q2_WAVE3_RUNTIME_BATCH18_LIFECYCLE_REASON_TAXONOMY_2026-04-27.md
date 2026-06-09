# Q2 Wave 3 Runtime Batch 18 Lifecycle Reason Taxonomy

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-27
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH16_DENIAL_AUDIT_EVIDENCE_2026-04-27.md`
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH17_NOT_FOUND_LIFECYCLE_AUDIT_2026-04-27.md`
- `src/application/trading/order_mgmt_service.py`
- `tests/ddd/test_phase_7_application.py`
- `tests/unit/runtime/test_trading_cash_reservations_cli.py`
- `tests/unit/core/test_runtime_config_governance.py`

## Purpose

Batch 16 and Batch 17 added local audit evidence for denied and missing-order lifecycle
attempts, but those audit records still relied on raw exception text as `decision_reason`.

That shape was reconstructable for humans, but fragile for downstream filtering, policy
checks, and future automated review because consumers would need to parse exception strings.

This batch closes that bounded gap by normalizing lifecycle refusal reasons into stable
machine-readable codes while preserving the original exception text separately.

## Implemented Scope

### 1. Denied and not-found lifecycle audits now use stable reason codes

The canonical application path now emits:

- `order_not_found` for missing-order lifecycle attempts
- `invalid_order_status_transition` for denied cancel / reject transitions on existing orders

`decision_outcome` continues to carry the action-specific distinction:

- `cancel_not_found`
- `reject_not_found`
- `cancel_denied`
- `reject_denied`

### 2. Raw exception text is preserved as detail, not discarded

Lifecycle refusal audit payloads now also preserve:

- `decision_reason_detail`

Examples:

- `Order not found: missing-order-0001`
- `Cannot reject order in status OrderStatus.PARTIALLY_FILLED`

This keeps operator reconstruction intact without forcing downstream tooling to parse
free-text reasons.

### 3. Storage scope remains intentionally unchanged

This batch does not widen the durable sink schema or introduce migration work.

The existing JSON payload path is sufficient because extra fields are already preserved in:

- JSONL audit records
- SQLite `payload_json`

## What This Batch Does Not Claim

This batch does not claim:

- broker-side normalization of lifecycle failure reasons
- cross-process or cross-host reason taxonomy enforcement
- query-time indexing on `decision_reason_detail`
- reconciliation with external broker order truth
- production-grade trading lifecycle governance

The execution path remains `experimental`.

## Verification

Targeted lifecycle taxonomy regression target:

- `pytest tests/ddd/test_phase_7_application.py -k "audits_not_found_lifecycle_attempt or disallows_partial_fill_transition or disallows_reject_after_cancelled_terminal_state or audits_denied_lifecycle_attempt_after_filled_state" -q`
  - functional result: `5 passed`
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `3.69%`

Application regression target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `29 passed`
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `4.27%`

Operator tooling regression target:

- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `3.69%`

Runtime config regression target:

- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `3.73%`

## Follow-Up

The next bounded hardening choice should be one of:

1. decide whether `handle_execution_report(...)` missing-order attempts deserve equivalent local audit evidence,
2. define a broader reason taxonomy policy for other runtime refusal classes only after real operator consumers exist,
3. or move outward from local audit evidence to broker-fed acknowledgement and reconciliation.
