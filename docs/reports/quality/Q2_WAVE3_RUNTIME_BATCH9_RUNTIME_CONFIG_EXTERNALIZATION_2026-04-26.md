# Q2 Wave 3 Runtime Batch 9 Runtime Config Externalization

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH8_STALE_RESERVATION_REVIEW_GATE_2026-04-26.md`
- `src/utils/trading_runtime_config.py`
- `src/application/trading/decision_audit.py`
- `src/application/trading/cash_reservation.py`
- `src/application/bootstrap.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`
- `tests/unit/core/test_runtime_config_governance.py`
- `tests/ddd/test_phase_7_application.py`

## Purpose

This batch closes the next obvious runtime-governance gap:
trading safety file paths and stale reservation thresholds should not remain hardcoded in composition roots.

The goal is configuration externalization only. This batch does not change trading decision semantics.

## Implemented Scope

### 1. Dedicated trading runtime config helper

A new helper module now exists:

- `src/utils/trading_runtime_config.py`

It defines runtime defaults and env-driven overrides for:

- trading runtime directory
- decision audit JSONL path
- decision audit SQLite path
- cash reservation SQLite path
- stale cash reservation max age seconds

### 2. Builder-level path convergence

Default builders now resolve file-backed runtime paths through the helper instead of inlined literals:

- `build_default_trading_decision_audit_sink()`
- `build_default_portfolio_cash_reservation_store()`

This keeps file-path policy centralized.

### 3. Composition-level threshold convergence

Default runtime builders now resolve stale reservation age through runtime config instead of hardcoded module constants:

- `src/application/bootstrap.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`

Current supported env variables:

- `TRADING_RUNTIME_DIR`
- `TRADING_DECISION_AUDIT_JSONL_PATH`
- `TRADING_DECISION_AUDIT_SQLITE_PATH`
- `TRADING_CASH_RESERVATION_SQLITE_PATH`
- `TRADING_STALE_CASH_RESERVATION_MAX_AGE_SECONDS`

## What This Batch Does Not Claim

This batch does not claim:

- multi-environment secret management completion
- broker-reconciled frozen-funds truth
- centralized policy distribution across multiple nodes
- production-grade live trading readiness

The execution path remains `experimental`.

## Verification

Runtime config target:

- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - new covered behavior includes default and env-overridden trading runtime path resolution
  - command still exits non-zero only because repo-wide total coverage remains below configured `fail-under=80`

Trading regression target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `20 passed`
  - confirms Batch 1-8 trading safety runtime behavior remains intact after config externalization
  - command still exits non-zero only because the same repo-wide coverage threshold applies to narrow runs

Additional note:

- GitNexus impact queries for some newly added or recently changed builder symbols timed out in this session, so this batch relies on explicit target-file scope control plus targeted verification rather than a completed graph scope report.

## Follow-Up

The next bounded hardening choice should be one of:

1. add operator-facing inspection/release tooling for reservation review,
2. reconcile local reservation state against broker open orders or frozen funds,
3. or bind these runtime settings into a more formal governance/config schema instead of env-only resolution.
