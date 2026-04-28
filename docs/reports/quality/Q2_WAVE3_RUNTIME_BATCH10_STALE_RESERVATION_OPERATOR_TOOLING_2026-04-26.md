# Q2 Wave 3 Runtime Batch 10 Stale Reservation Operator Tooling

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH9_RUNTIME_CONFIG_EXTERNALIZATION_2026-04-26.md`
- `scripts/runtime/trading_cash_reservations.py`
- `tests/unit/runtime/test_trading_cash_reservations_cli.py`

## Purpose

This batch adds the minimum operator-facing tool needed after Batch 8 and Batch 9:
inspect local reservation state and manually release a stale reservation by explicit order id.

The goal is human review support, not automatic sanitation.

## Implemented Scope

### 1. Local reservation CLI

A new runtime CLI now exists:

- `scripts/runtime/trading_cash_reservations.py`

Current commands:

- `list`
- `release`

### 2. Inspection support

The `list` command supports:

- all reservations or only stale reservations
- optional `portfolio_id` filtering
- configurable stale age threshold
- `text` or `json` output

### 3. Manual release support

The `release` command:

- requires an explicit `order_id`
- removes only that single reservation from the local ledger
- returns structured output for success or not-found outcomes

This keeps cleanup intentional and auditable at the operator decision point.

## What This Batch Does Not Claim

This batch does not claim:

- broker-side validation before local release
- automatic release of stale reservations
- multi-order or bulk cleanup workflows
- production-grade real-money reconciliation

The execution path remains `experimental`.

## Verification

Operator tooling target:

- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `4 passed`
  - covered behavior:
    - stale reservation listing
    - explicit release by order id
    - structured not-found failure
  - command still exits non-zero only because repo-wide total coverage remains below configured `fail-under=80`

Runtime config and trading regression targets:

- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - not re-run in this batch because Batch 10 did not modify runtime config resolution logic
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `20 passed`
  - command still exits non-zero only because the same repo-wide coverage threshold applies to narrow runs

All narrow test commands in this line still inherit the repo-wide coverage failure because total project coverage remains below configured `fail-under=80`.

## Follow-Up

The next bounded hardening choice should be one of:

1. broker/open-order reconciliation before local release is accepted as safe,
2. a dedicated audit sink for manual release actions,
3. or a lightweight API/admin surface over this CLI for controlled operational use.
