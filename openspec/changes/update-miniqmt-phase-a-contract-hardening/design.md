## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

`mystocks_spec` now has a stable repo-owned Phase A contract for:

- `Authorization: Bearer <TRADING_QMT_BRIDGE_TOKEN>`
- `X-Bridge-Contract-Version`
- polling-first `task_id -> result`
- fail-closed bridge failure semantics

The separate Windows `miniQMT` project has adopted those decisions in its design docs, including:

- `account_scope` elevated to a v1 field
- `event_id` elevated to a v1 field
- `occurred_at` frozen as service-observed UTC time
- SQLite-backed task persistence as the Windows-side Phase A persistence target

The local repository still needs to make its own contract reference path match those decisions end
to end.

## Goals

- Make the repo-owned Windows `qmt` reference service emit the canonical Phase A fields consistently
- Preserve canonical identity fields through local result normalization and deferred follow-up
  ingestion
- Freeze the Phase A field set in repository tests

## Non-Goals

- Implement the real Windows `miniQMT` SDK adapter
- Add callback-first broker lifecycle ingestion
- Add multi-account routing
- Expand Tongdaxin supplemental automation
- Rework the broader trading domain model

## Decisions

### 1. Treat `event_id` as a v1 field in the repo-owned reference service

The local reference service is the repository-owned contract exemplar. Even though `event_id` may
be generated on the Windows side rather than supplied by broker-native evidence, the local
reference service should expose it now so tests can freeze the expected shape.

### 2. Keep `account_scope` and `occurred_at` mandatory in normalized live bridge payloads

The live bridge normalization path already rejects missing `account_scope` and `occurred_at`.
This batch keeps that rule and ensures the same fields survive deferred re-entry into the shared
lifecycle ledger instead of being dropped in the follow-up payload bridge.

### 3. Keep `external_order_id` conditional and fail-closed

This batch does not promote `external_order_id` to an always-required field. It stays conditional:
when the upstream result has it, preserve it; when it does not, do not synthesize a fake live
identity.

### 4. Lock the local contract with focused tests instead of new runtime breadth

The highest-value next step inside `mystocks_spec` is contract stability, not more execution-path
surface area. The batch therefore prioritizes narrow contract tests over new integration modes.
