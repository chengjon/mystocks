# Q2 Wave 3 Audit Binding And Retention

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Blocking Controls`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_PHASE_D_TRADING_SAFETY_CONTRACT_2026-04-25.md`
- `src/infrastructure/logging/audit_system.py`
- `src/application/trading/order_mgmt_service.py`

## Purpose

This note closes Wave 3 Batch 4 at the audit-contract layer.

It defines which trading decisions require durable audit binding and what minimum retention expectation applies to the current experimental safety class.

It does not claim the current runtime already binds those decisions into the audit system.

## Decision Points That Must Be Audited

The canonical placement path should durably audit at least:

- submit accepted
- submit rejected
- confirmation requested
- confirmation approved
- confirmation bypass approved
- deduplication matched

If a future external execution adapter is introduced, adapter handoff should also become a required audit point.

## Minimum Audit Fields

Every decision record should eventually carry:

- request identity
- actor identity
- strategy or source identity
- execution path classification
- symbol
- side
- quantity
- normalized price context
- decision outcome
- decision reason
- timestamp

Optional but preferred fields:

- session id
- request id
- client ip or operator context when applicable
- linked prior request identity for dedup matches

## Binding Rule

Audit binding should occur at the decision point, not only:

- after downstream repository persistence
- after a later fill event
- after a monitoring alert

This is required because safety decisions such as `rejected`, `deduplicated`, or `awaiting_confirmation` may never produce a downstream fill artifact.

## Retention Expectation

For the current `experimental` trading class, audit retention should be treated conservatively as:

- durable persistence required for submit/reject/confirm/dedup decisions
- retention expectation at least aligned with the existing audit helper default where available
- no shorter retention should be implied without an explicit approved policy

Wave 3 does not redefine global retention rules. It only states that trading-safety decisions must not be ephemeral.

## Explicit Non-Claims

This batch does not claim:

- `OrderManagementService.place_order()` currently emits audit events
- repository persistence already satisfies the trading audit contract
- stop-loss or alert records equal a complete submission audit trail

## Follow-Up Constraint

If runtime hardening begins, audit binding should land in the canonical placement path before any attempt to upgrade trading classification.
