# Q2 Wave 3 Idempotency And Dedup Contract

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Blocking Controls`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_PHASE_D_TRADING_SAFETY_CONTRACT_2026-04-25.md`
- `src/application/dto/trading_dto.py`
- `src/application/trading/order_mgmt_service.py`

## Purpose

This note closes Wave 3 Batch 2 at the contract layer.

It defines what the canonical placement path must consider the same effective trade intent and how deduplication outcomes should be interpreted.

It does not claim the current runtime already enforces this contract.

## Current Gap

`CreateOrderRequest` currently does not expose a stable idempotency identity.

`OrderManagementService.place_order()` currently creates a fresh order identity and persists it without documented duplicate-intent protection.

Therefore, duplicate effective trade intent must currently be treated as an unresolved safety gap.

## Required Canonical Identity

Future canonical order intent should carry an idempotency identity that is stable for the same effective submission attempt.

Minimum identity fields:

- actor identity
- strategy or source identity
- symbol
- side
- order type
- normalized quantity
- normalized price when applicable
- intent timestamp window or client-generated request identity

This identity may be expressed as:

- client request id
- idempotency key
- deterministic intent hash

But the project should converge to one canonical field rather than multiple parallel dedup signals.

## Deduplication Scope

Deduplication should apply to the canonical placement path before a second effective submission is accepted.

The dedup scope should conservatively include:

- same actor
- same strategy/source
- same effective order intent
- same bounded replay window

## Canonical Outcomes

The placement path should eventually distinguish:

- `submitted`
  - new intent accepted
- `deduplicated`
  - prior equivalent intent already accepted in scope
- `rejected`
  - request invalid or unsafe

`deduplicated` must be auditable and must not silently behave like a fresh submission.

## Audit Requirement

When the future runtime enforces this contract, a dedup decision should carry:

- canonical request identity
- dedup scope
- matched prior submission identity
- actor identity
- decision timestamp

## Explicit Non-Claims

This batch does not claim:

- the current DTO already carries an idempotency key
- the current order service already deduplicates requests
- repository save semantics already prevent duplicate intent

## Follow-Up Constraint

Any runtime hardening should implement idempotency before promoting trading readiness or expanding live execution narratives.
