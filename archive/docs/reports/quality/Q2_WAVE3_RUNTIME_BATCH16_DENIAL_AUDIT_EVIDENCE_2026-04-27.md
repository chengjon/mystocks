# Q2 Wave 3 Runtime Batch 16 Denial Audit Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-27
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH15_REJECT_TRANSITION_GUARDS_2026-04-27.md`
- `src/application/trading/order_mgmt_service.py`
- `tests/ddd/test_phase_7_application.py`
- `tests/unit/runtime/test_trading_cash_reservations_cli.py`
- `tests/unit/core/test_runtime_config_governance.py`

## Purpose

Batch 15 made invalid local lifecycle transitions fail fast, but a denied
`cancel_order(...)` or `reject_order(...)` attempt still left no durable local decision trace.

This batch closes that observability gap by emitting local denial audit evidence when the
application service refuses an invalid lifecycle action after loading an existing order.

The goal remains intentionally narrow:

- keep local order-state evidence unchanged when the lifecycle action is invalid,
- preserve the exception-based control flow,
- and add auditable denial evidence for operator and runtime reconstruction.

## Implemented Scope

### 1. `OrderManagementService` now audits denied lifecycle attempts

When an already-loaded order rejects a local lifecycle mutation with `RuntimeError`,
the application path now emits explicit local audit outcomes:

- `cancel_denied`
- `reject_denied`

The raised exception still propagates to the caller. This batch does not convert denial
into a silent success or an alternate return envelope.

### 2. Denial audit payloads now preserve local review context

Denied lifecycle audit records now also include:

- `requested_reason`
- `current_order_status`

This keeps the denial evidence useful without changing the durable sink schema,
because the JSON payload already preserves extra fields.

### 3. Canonical application tests now lock denial behavior for both actions

The application-path coverage now explicitly verifies:

- reject after partial fill emits `reject_denied`
- reject after cancel emits `reject_denied`
- cancel after full fill emits `cancel_denied`

The same tests also verify that failed lifecycle attempts do not mutate:

- local order-state evidence
- local reservation state
- prior successful lifecycle history

## What This Batch Does Not Claim

This batch does not claim:

- broker-acknowledged denial truth
- not-found audit evidence for unknown order ids
- retry / escalation workflow for denied lifecycle attempts
- centralized or distributed audit ingestion
- production-grade real-trading lifecycle governance

The execution path remains `experimental`.

## Verification

Targeted denial-audit regression target:

- `pytest tests/ddd/test_phase_7_application.py -k "reject_order_disallows or cancel_order_audits_denied_lifecycle_attempt" -q`
  - functional result: `3 passed`
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `3.65%`

Application regression target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `27 passed`
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `4.25%`

Operator tooling regression target:

- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `3.67%`

Runtime config regression target:

- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `3.70%`

## Follow-Up

The next bounded hardening choice should be one of:

1. add denial audit for `order not found` lifecycle attempts if operator replay needs that evidence,
2. normalize denial-reason strings so downstream review tooling does not parse raw exception text,
3. or move outward from local denial evidence to broker-fed lifecycle acknowledgement and reconciliation.
