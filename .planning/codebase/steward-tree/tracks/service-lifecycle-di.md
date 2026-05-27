# Track: Service Lifecycle DI

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active track summary
- Prepared at: `2026-05-27T17:22:14+08:00`
- Base HEAD checked: `ba929aee2e7fc0de0278f80f30caa185fafa6b5c`

Boundary note: this track summary does not authorize source changes. Each
implementation still needs a path-limited authorization package, GitNexus impact
analysis, tests, staged change detection, review, and PR merge.

## Track Role

This track owns the gradual replacement of route-body or service-body global
getter calls with explicit dependency providers or constructor/provider seams.
It proved a repeatable conveyor:

1. inventory or residual scan
2. candidate classification
3. decision package
4. implementation authorization
5. TDD implementation
6. closeout and residual refresh

## Current Strategy Residual State

| Node | State | Notes |
|---|---|---|
| Steward split | Merged by PR `#332` | Root task tree is now a short entrypoint; active state belongs in this split track and `steward-index.json` |
| G2.177 Strategy canonical adapter provider authorization | Accepted and merged by PR `#330` | Authorized only a constructor-level Strategy service provider seam in canonical `strategy_adapter.py` and focused tests |
| G2.178 Strategy adapter provider implementation | Merged by PR `#331` | Added the approved optional constructor-level provider seam and reconciled the G2.178 steward update into the split tree |
| G2.180 Strategy adapter provider closeout | Merged by PR `#333` | Records G2.178 as closed and refreshes residual Strategy getter distribution without source edits |
| G2.181 Strategy getter residual refresh decision | For review | Rechecks residual classes at HEAD `ba929aee2e7fc0de0278f80f30caa185fafa6b5c` and selects route/provider fallback as the next governance target |

## Current Strategy Getter Residuals

At HEAD `8bfb4dc74b06d6bb930e48ebf3d27bb28d908704`, production `.py`
At HEAD `ba929aee2e7fc0de0278f80f30caa185fafa6b5c`, `get_strategy_service`
hits under `web/backend/app` remain `19`:

| File | Hits | Current decision |
|---|---:|---|
| `web/backend/app/services/adapters/strategy_adapter.py` | 10 | Canonical adapter-local residual; defer future adapter-local lifecycle cleanup until a separate decision/authorization package exists |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 6 | Route provider fallback residual; selected as recommended next governance target |
| `web/backend/app/tasks/backtest_tasks.py` | 2 | Backtest task helper residual; do not reopen unless current evidence contradicts the closed resolver-seam handling |
| `web/backend/app/services/strategy_service.py` | 1 | Public getter definition; retain as compatibility entrypoint and do not delete, rename, or privatize here |

## Next Gates

- Review G2.181 residual-refresh decision.
- If accepted, prepare G2.182 route/provider fallback decision package before
  any further Strategy getter source edits.
- Do not start another Strategy service getter source lane from this
  residual-refresh decision package.

## Forbidden Scope

This track summary forbids:

- backend source edits
- frontend edits
- test edits
- OpenSpec proposal creation
- issue label changes
- moving another service candidate directly to implementation
- treating service inventory counts as implementation backlogs
