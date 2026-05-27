# Backend Strategy Adapter Provider Closeout

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.180
- State: ready for review
- Date: 2026-05-27
- Base HEAD: `8bfb4dc74b06d6bb930e48ebf3d27bb28d908704`
- Closed item: G2.178 Strategy adapter provider implementation
- Closed by PR: `#331`, merge commit `8bfb4dc74b06d6bb930e48ebf3d27bb28d908704`
- Scope: governance closeout and residual-refresh evidence only

Boundary note: this report does not authorize backend source edits, frontend
source edits, tests, generated client updates, docs/API edits, OpenSpec proposal
creation, issue label changes, PM2 commands, runtime rollout, compatibility
deletion, or another Strategy getter implementation.

## Closeout Decision

G2.178 is closed as implemented and merged. The canonical
`StrategyDataSourceAdapter` now has an optional constructor-level
`strategy_service_provider` seam while preserving the default public
`get_strategy_service()` fallback path.

## Implementation Facts

At HEAD `8bfb4dc74b06d6bb930e48ebf3d27bb28d908704`:

| Fact | Value |
|---|---|
| Target file | `web/backend/app/services/adapters/strategy_adapter.py` |
| Provider parameter present | yes |
| Provider stored | yes |
| Provider used by `_get_strategy_service()` | yes |
| Public getter fallback preserved | yes |
| Constructor line | `24` |
| `_get_strategy_service()` line | `40` |
| Adapter line count | `372` |

## Residual Scan

Production `.py` `get_strategy_service` hits under `web/backend/app` remain
`19`:

| File | Hits | Closeout interpretation |
|---|---:|---|
| `web/backend/app/services/adapters/strategy_adapter.py` | 10 | Canonical adapter-local residual; now has constructor provider seam |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 6 | Route provider fallback residual; route/provider lane owns further movement |
| `web/backend/app/tasks/backtest_tasks.py` | 2 | Backtest task helper residual; previous resolver seam lane already separated this surface |
| `web/backend/app/services/strategy_service.py` | 1 | Public getter definition; not a deletion candidate in this lane |

## Steward Updates

This closeout updates the split steward tree only:

- `.planning/codebase/steward-tree/current-next-gates.md`
- `.planning/codebase/steward-tree/steward-index.json`
- `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md`
- `.planning/codebase/steward-tree/branch-register.md`
- `.planning/codebase/steward-tree/evidence-index.md`
- `.planning/codebase/steward-tree/completed-ledger.md`
- `.planning/codebase/generated/strategy-adapter-provider-closeout-2026-05-27.json`

## Next Gate

If this closeout is accepted, prepare a separate residual-refresh decision
package before any further Strategy getter source edits. That package should
decide whether the remaining residuals belong to:

- canonical adapter-local lifecycle cleanup
- route provider fallback governance
- backtest task helper follow-up
- public getter retention

No source lane is opened by this closeout.
