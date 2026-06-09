# Q2 Wave 3 Runtime Batch 4 Local Queryable Audit Ledger

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_AUDIT_BINDING_AND_RETENTION_2026-04-26.md`
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH3_DURABLE_AUDIT_SINK_2026-04-26.md`
- `src/application/trading/decision_audit.py`
- `tests/ddd/test_phase_7_application.py`

## Purpose

This batch keeps the low-risk local durability model from Batch 3, while making the decision audit trail locally queryable without depending on the unstable async audit infrastructure.

## Implemented Scope

### 1. Local SQLite audit ledger

A new local ledger now exists:

- `SqliteTradingDecisionAuditSink`

Current ledger properties:

- process-local SQLite persistence
- auto-created schema and indexes
- append-oriented writes
- local query support through `fetch_recent()`

### 2. Dual-write default sink

The default trading decision audit sink is now a composite local sink:

- JSONL remains the hot-path append ledger
- SQLite provides a local queryable index over the same decision records

Default target paths:

- `var/log/trading/trading-decision-audit.jsonl`
- `var/log/trading/trading-decision-audit.sqlite3`

### 3. Scope boundary

This batch intentionally does not bind to:

- the current `src/infrastructure/logging/audit_system.py` implementation
- backend audit query APIs
- distributed audit replication
- production-grade retention enforcement

The reason is risk control: the current async audit system is structurally unstable, so this batch closes the local reconstructability gap first without introducing a second broken dependency path into the trading placement flow.

## Verification

Targeted test additions:

- SQLite sink persists and returns recent decision records
- default sink writes to both JSONL and SQLite

Primary test target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `10 passed`
  - command exit remains non-zero only because repo-wide coverage is still below the configured `fail-under=80`

Secondary regression check:

- `pytest tests/unit/core/test_runtime_config_governance.py::test_app_container_uses_role_aware_redis_kwargs -q`
  - functional result: `1 passed`
  - command exit remains non-zero only because the same repo-wide coverage gate still applies to narrow invocations

## Follow-Up

The next hardening step should choose one of these explicit directions:

1. bridge the local ledger into a stable centralized audit ingestion path,
2. connect pre-submit gating to real capital / exposure context,
3. or define promotion criteria for when the local SQLite ledger is no longer sufficient.
