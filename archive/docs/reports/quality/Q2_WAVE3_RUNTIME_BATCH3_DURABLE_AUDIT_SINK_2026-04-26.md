# Q2 Wave 3 Runtime Batch 3 Durable Audit Sink

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_AUDIT_BINDING_AND_RETENTION_2026-04-26.md`
- `src/application/trading/decision_audit.py`
- `src/application/bootstrap.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`

## Purpose

This batch moves the decision audit hook from pure in-memory callback semantics to a default durable sink.

## Implemented Scope

### 1. Append-only JSONL sink

A new file-backed sink now exists:

- `JsonlTradingDecisionAuditSink`

Current durability model:

- append-only JSONL
- process-local file persistence
- parent directory auto-created
- flush on write

Default target path:

- `var/log/trading/trading-decision-audit.jsonl`

### 2. Default runtime wiring

The default `OrderManagementService` created by:

- `src/application/bootstrap.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`

now uses the default JSONL trading decision audit sink.

This means the canonical placement path gains a durable local reconstruction trail even before a fuller centralized audit pipeline exists.

## What This Batch Does Not Claim

This batch does not claim:

- distributed multi-instance durability
- centralized audit query APIs for these records
- cryptographic integrity
- durable binding to the existing async database-backed audit manager

## Verification

Targeted test added:

- JSONL sink persists a submitted decision to disk

Primary test target:

- `pytest tests/ddd/test_phase_7_application.py -q`

## Follow-Up

The next hardening step should decide whether to:

1. bridge this sink into the existing audit manager,
2. replace it with a database-backed synchronous adapter,
3. or keep JSONL as the local hot-path ledger and add downstream ingestion later.
