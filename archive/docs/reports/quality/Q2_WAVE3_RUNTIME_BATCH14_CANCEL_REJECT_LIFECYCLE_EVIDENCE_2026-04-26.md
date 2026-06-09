# Q2 Wave 3 Runtime Batch 14 Cancel / Reject Lifecycle Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH13_LOCAL_ORDER_STATE_EVIDENCE_2026-04-26.md`
- `src/application/trading/order_mgmt_service.py`
- `tests/ddd/test_phase_7_application.py`
- `tests/unit/runtime/test_trading_cash_reservations_cli.py`
- `tests/unit/core/test_runtime_config_governance.py`

## Purpose

This batch extends the local order-state evidence line from submit/fill only
to two additional terminal lifecycle outcomes on the canonical application path:

- `CANCELLED`
- `REJECTED`

The objective is still intentionally bounded:

- release pending BUY reservations when the local application path knows the order has terminated without remaining working quantity,
- persist that terminal status in the same local evidence store,
- and emit an explicit local audit outcome for operator or runtime review.

## Implemented Scope

### 1. `OrderManagementService` now exposes cancel / reject lifecycle entrypoints

The canonical application service now supports:

- `cancel_order(...)`
- `reject_order(...)`

Each path:

- loads the persisted order,
- applies the existing domain lifecycle mutation,
- persists the updated aggregate,
- reconciles the pending BUY cash reservation,
- updates local order-state evidence,
- publishes domain events,
- and emits a local decision audit record.

This keeps lifecycle orchestration in the application layer instead of pushing it into CLI-only or operator-only scripts.

### 2. Terminal lifecycle outcomes now release pending BUY reservations

Reservation reconciliation now treats these statuses as terminal release conditions:

- `CANCELLED`
- `REJECTED`
- `EXPIRED`
- `FILLED`

This closes the previous gap where local reservation state could remain artificially occupied after a non-fill terminal outcome.

### 3. Local order-state evidence now captures cancel / reject terminal status

The same local evidence store introduced in Batch 13 now records:

- `SUBMITTED`
- `PARTIALLY_FILLED`
- `FILLED`
- `CANCELLED`
- `REJECTED`

This improves reconstruction quality for local operator tooling without claiming external broker truth.

### 4. Audit outcomes now distinguish post-submit cancel vs reject

The local decision audit line now records distinct outcomes for post-submit terminal paths:

- `cancelled`
- `rejected_after_submission`

This keeps post-submit lifecycle evidence separate from:

- submit-time `rejected`
- pre-submit `blocked_by_risk_gate`
- review-path outcomes in the reservation CLI

## What This Batch Does Not Claim

This batch does not claim:

- broker-confirmed cancel acknowledgement
- broker-confirmed rejection truth
- external open-order reconciliation
- distributed order-state consensus
- production-grade real-trading lifecycle safety

The execution path remains `experimental`.

## Verification

Lifecycle regression target:

- `pytest tests/ddd/test_phase_7_application.py -k "cancel_order or reject_order" -q`
  - functional result: `2 passed`
  - covered behavior now includes:
    - cancel path releases reservation and persists `CANCELLED`
    - reject path releases reservation and persists `REJECTED`

Application regression target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `24 passed`
  - covered behavior now includes:
    - submit -> cancel terminal evidence
    - submit -> reject terminal evidence
    - audit outcomes for both terminal paths
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `3.90%`

Operator tooling regression target:

- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `2.93%`

Runtime config regression target:

- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `2.96%`

## Follow-Up

The next bounded hardening choice should be one of:

1. ingest cancel / reject truth from the actual broker-facing execution adapter instead of only local application mutations,
2. add explicit handling for invalid or ambiguous terminal transitions such as reject-after-partial-fill,
3. or use local terminal evidence to tighten reservation CLI automation only after adapter truth exists for the same lifecycle edges.
