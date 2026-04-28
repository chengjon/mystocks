# Q2 Wave 3 Risk Gate And Confirmation Policy

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Blocking Controls`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_PHASE_D_TRADING_SAFETY_CONTRACT_2026-04-25.md`
- `src/trading/live_trading_engine.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`

## Purpose

This note closes Wave 3 Batch 3 at the policy layer.

It defines what the canonical placement path must block before order placement and when confirmation or approved bypass becomes mandatory.

It does not claim that the current runtime already enforces these policies.

## Pre-Execution Blocking Policy

The canonical placement path should reject or hold an order intent before submission when any blocking condition is met.

Minimum blocking condition classes:

- capital limit breach
- concentration limit breach
- exposure or max-position breach
- daily loss or drawdown breach
- outside-session execution attempt
- missing required confirmation for a safety-sensitive action

## Inputs Already Visible In Repo Truth

`LiveTradingConfig` already expresses useful safety inputs such as:

- `max_positions`
- `max_position_size`
- `max_daily_loss`
- `max_drawdown`
- `risk_per_trade`

Current Wave 3 interpretation:
- these values are useful safety policy inputs
- they are not yet sufficient proof of a blocking pre-order gate

## Confirmation Policy

The canonical placement path should require confirmation or approved bypass for safety-sensitive actions, including:

- first live order in a session
- liquidation or forced-sell intent
- orders exceeding configured notional or exposure thresholds
- manual override of an automated strategy path
- retry after a recent reject or dedup anomaly

Approved bypass should require:

- actor identity
- justification
- bounded scope
- auditable timestamp

## Supporting Controls Versus Blocking Controls

The following remain supporting controls, not substitutes for a pre-order gate:

- stop-loss execution services
- alerting services
- monitoring or post-order analysis

They are valuable, but they do not satisfy the Wave 3 blocking contract by themselves.

## Canonical Outcomes

The placement path should eventually distinguish:

- `blocked_by_risk_gate`
- `awaiting_confirmation`
- `approved_bypass`
- `allowed_to_submit`

These are decision-point outcomes and should be determined before effective submission.

## Explicit Non-Claims

This batch does not claim:

- `LiveTradingConfig` is already enforced as a pre-order gate
- stop-loss logic is equivalent to pre-execution safety control
- confirmation is already enforced in runtime code

## Follow-Up Constraint

Any future runtime implementation should place risk-gate and confirmation checks ahead of order creation or effective submission, not only after monitoring or downstream alerts.
