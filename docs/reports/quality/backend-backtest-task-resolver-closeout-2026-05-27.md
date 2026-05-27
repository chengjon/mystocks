# Backend Backtest Task Resolver Closeout

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.171
- State: ready for review
- Date: 2026-05-27
- Current HEAD: `d465e41950c2f6fe70ee9c923da3cc55c09212c3`
- Parent PR: `#323` merged, `refactor(backend): inject backtest task resolver provider`
- Scope: post-merge closeout for G2.170 backtest task resolver seam

## Boundary

This is a governance-only closeout package.

No backend source, tests, route behavior, OpenAPI exposure, frontend, PM2 workflow, OpenSpec content, config, scripts, compatibility deletion, or issue-label state is changed here.

## Parent Merge

PR `#323` was merged into `wip/root-dirty-20260403` at:

```text
d465e41950c2f6fe70ee9c923da3cc55c09212c3
```

The local closeout worktree and remote `wip/root-dirty-20260403` both pointed at that commit during evidence collection.

## Closeout Finding

G2.170 is closed as implemented and post-merge verified.

The backtest task Strategy data-source resolver now has a task-local provider seam:

- `_get_strategy_data_source()` exists at `web/backend/app/tasks/backtest_tasks.py:18-23`.
- `_resolve_backtest_data_source()` exists at `web/backend/app/tasks/backtest_tasks.py:24-38`.
- `run_backtest_task()` still calls `_resolve_backtest_data_source()` once.
- `_resolve_backtest_data_source()` has `0` direct `get_strategy_service` mentions.
- `_resolve_backtest_data_source()` delegates through `_get_strategy_data_source()` once.
- `_get_strategy_data_source()` preserves the public `get_strategy_service()` fallback.
- The provider-seam regression test exists.
- The unsupported-mode test uses `pytest.raises(ValueError, ...)`.

## Post-Merge Verification

Verification executed at current HEAD `d465e41950c2f6fe70ee9c923da3cc55c09212c3`:

| Check | Result |
|---|---|
| Parent PR state | `#323` is `MERGED` |
| Backtest task regressions | `3 passed in 3.02s` |
| Strategy route provider regressions | `5 passed in 4.46s` |
| Ruff touched files | `All checks passed!` |
| Black touched files | `2 files would be left unchanged` |
| OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0`, `total_warnings_captured=121` |

OpenAPI smoke used minimal non-secret placeholder environment values to satisfy the application import gate. No route or OpenAPI files were changed by G2.170.

## Remaining Strategy Getter Tracks

This closeout closes only the backtest task resolver seam.

Still separate and not solved by G2.170:

- Strategy route provider fallback remains intentionally retained.
- Strategy adapter/provider duplication remains deferred to a separate adapter design track.
- Public `get_strategy_service()` remains available and unchanged.
- Broad `get_strategy_service` retirement remains out of scope because prior evidence classified the broader seam as CRITICAL.

## Next Gate

Do not open another Strategy service getter source implementation directly from this closeout.

Recommended next step:

1. Create a new decision-only or authorization-only packet for the next Strategy residual track.
2. Re-scan current residual Strategy getter sites at the new HEAD.
3. Decide whether the next track is adapter/provider design, route-provider fallback retention closeout, or another narrow task/provider seam.
4. Only after that review gate should a new source implementation lane begin.

## Rollback

If this closeout is rejected, revert only the G2.171 governance PR. That removes this report, generated JSON, task card, and steward-tree update. It does not alter the already-merged G2.170 source implementation.

