# Backend Strategy Residual Current Track Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.172
- State: ready for review
- Date: 2026-05-27
- Current HEAD: `68c6b4149984aab583dacebf9cdd1ff131189c3e`
- Parent PR: `#324` merged, `docs(governance): close out backtest task resolver seam`
- Scope: decision-only current Strategy service getter residual refresh and next-track selection

## Boundary

This package does not edit backend source, tests, route behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec content, config, scripts, compatibility surfaces, or issue labels.

This package does not authorize implementation. It only selects the next Strategy residual track that should receive its own design/authorization packet.

## Parent State

PR `#324` was merged into `wip/root-dirty-20260403` at:

```text
68c6b4149984aab583dacebf9cdd1ff131189c3e
```

The local evidence worktree and remote `wip/root-dirty-20260403` both pointed at that commit during collection.

## Current Residual Scan

Production scan under `web/backend/app` found `29` text hits across `5` files for `get_strategy_service`.

| Classification | Hits | Files | Disposition |
|---|---:|---:|---|
| Route provider fallback retained | 6 | 1 | Retain. It is the G2.166 compatibility/provider seam and not a removal target. |
| Adapter/provider duplication track | 20 | 2 | Select as next design packet. |
| Public getter definition | 1 | 1 | Retain. Broad public getter retirement remains out of scope and CRITICAL. |
| Backtest task resolver closed | 2 | 1 | Closed by G2.170/G2.171; no next action here. |

Detailed files:

| File | Classification | Hits | Key lines |
|---|---|---:|---|
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | route provider fallback retained | 6 | `20`, `33`, `34`, `388`, `454`, `499` |
| `web/backend/app/services/adapters/strategy_adapter.py` | adapter/provider duplication track | 10 | `39`, `43`, `45`, `102`, `116`, `132`, `149`, `179`, `328`, `340` |
| `web/backend/app/services/data_adapters/strategy.py` | adapter/provider duplication track | 10 | `36`, `40`, `42`, `99`, `113`, `129`, `146`, `176`, `325`, `337` |
| `web/backend/app/services/strategy_service.py` | public getter definition | 1 | `455` |
| `web/backend/app/tasks/backtest_tasks.py` | backtest task resolver closed | 2 | `19`, `21` |

## Route Fallback State

The Strategy route provider fallback remains intentionally retained:

- `get_strategy_service_dependency()` spans `web/backend/app/api/strategy_management/_strategy_execution_router.py:33-39`.
- It calls public `get_strategy_service()` once.
- Route handlers `query_strategy_results`, `get_matched_stocks`, and `get_strategy_summary` have `0` direct `get_strategy_service()` body calls.
- Those route handlers each use `Depends(get_strategy_service_dependency)` once.

Decision: do not retire or modify this fallback from the next lane. It is a known compatibility/provider seam, not a duplicate adapter problem.

## Backtest Resolver State

The backtest task resolver seam remains closed:

- `_resolve_backtest_data_source()` has `0` direct `get_strategy_service` mentions.
- `_get_strategy_data_source()` preserves the public getter fallback with `2` text mentions.
- The provider-seam regression test remains present.

Decision: do not reopen the backtest resolver lane from this package.

## Adapter/Provider Duplication State

Two parallel Strategy adapter modules retain nearly identical Strategy service provider helper patterns:

| File | Helper lines | Helper public getter mentions | `_fetch_strategy_data` helper mentions | `health_check` helper mentions |
|---|---:|---:|---:|---:|
| `web/backend/app/services/adapters/strategy_adapter.py` | `39-50` | 3 | 5 | 2 |
| `web/backend/app/services/data_adapters/strategy.py` | `36-47` | 3 | 5 | 2 |

GitNexus context confirms each helper has the same local caller shape:

- Incoming: `_fetch_strategy_data`, `health_check`
- Outgoing: `web/backend/app/services/strategy_service.py::get_strategy_service`

Decision: select this as the next Strategy residual design track. Because two package paths are involved, the next step should be a design/authorization packet that resolves ownership and migration shape before any source implementation.

## GitNexus Evidence

`get_strategy_service` remains broad and unsafe for direct retirement:

- Risk: CRITICAL
- Impacted count: `13`
- Direct callers: `6`
- Affected processes: `0`
- Affected modules: `5`
- Direct module hits include `Data_adapters`, `Adapters`, `Strategy_management`, and `Tasks`

This reinforces the split-track approach. A future source lane must target a narrow adapter/provider seam, not public getter retirement.

## Verification

Executed at current HEAD `68c6b4149984aab583dacebf9cdd1ff131189c3e`:

| Check | Result |
|---|---|
| Parent PR state | `#324` is `MERGED` |
| Backtest task regressions | `3 passed in 2.05s` |
| Strategy route provider regressions | `5 passed in 3.34s` |
| Adapter mock fallback controls | `6 passed in 0.19s` |
| OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0`, `total_warnings_captured=121` |

OpenAPI smoke used minimal non-secret placeholder environment values to satisfy the application import gate. This decision package does not edit route or OpenAPI files.

## Decision

Approve the following next-track ordering:

1. Keep route provider fallback retained.
2. Keep backtest task resolver seam closed.
3. Keep public `get_strategy_service()` available and unchanged.
4. Start G2.173 as a decision-only or authorization-only Strategy adapter/provider duplication design package.

G2.173 should decide:

- whether `web/backend/app/services/adapters/strategy_adapter.py` and `web/backend/app/services/data_adapters/strategy.py` have separate ownership or one canonical implementation;
- whether one package path is runtime-canonical and the other is compatibility/legacy;
- whether a shared provider seam is appropriate;
- exact future source scope, tests, rollback, and no-go paths;
- whether any source implementation should be split into separate phases.

## Non-Goals

This package does not:

- authorize edits to either adapter file;
- authorize public `get_strategy_service()` removal;
- authorize route provider fallback removal;
- reopen the backtest task resolver lane;
- edit route/API behavior, OpenAPI exposure, frontend, PM2, OpenSpec, config, scripts, or issue labels.

## Rollback

If this decision package is rejected, revert only the G2.172 governance PR. That removes this report, generated JSON, task card, and steward-tree update. No runtime behavior is affected.

