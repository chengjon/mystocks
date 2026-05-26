# Backend BacktestEngine Getter Retirement Authorization

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-26

Current HEAD: `2d51cbd52bc37dae2ae5f59855bcdb70d41f169c`

Parent refresh: G2.138 / PR `#291`

Boundary note: this is an authorization-only package. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, or GitHub issue labels. It does not remove `get_backtest_engine` or `_backtest_engine`.

## Purpose

Authorize a future narrow implementation lane to retire the unused BacktestEngine module singleton and compatibility getter.

The candidate was selected by G2.138 because the current evidence shows low blast radius and no backend code references outside the defining service file.

## Target

| Item | Value |
|---|---|
| Service file | `web/backend/app/services/backtest_engine.py` |
| Class to preserve | `BacktestEngine` |
| Config/result models to preserve | `BacktestConfig`, `BacktestResult` |
| Singleton to retire in future implementation | `_backtest_engine` |
| Getter to retire in future implementation | `get_backtest_engine` |

## Current Evidence

| Check | Result |
|---|---|
| `BacktestEngine` class definition count | `1` |
| `get_backtest_engine` definition count | `1` |
| `_backtest_engine` token count in target file | `5` |
| Backend code references to `get_backtest_engine` | `web/backend/app/services/backtest_engine.py:1` only |
| Import smoke | `BacktestConfig`, `BacktestEngine`, `BacktestResult`, `get_backtest_engine` importable |
| GitNexus upstream impact for `get_backtest_engine` | LOW, impacted `0`, direct `0`, processes `0`, modules `0` |

## Future Implementation Scope

Allowed paths for the future implementation lane:

- `web/backend/app/services/backtest_engine.py`
- `web/backend/tests/test_backtest_engine_getter_retirement.py`
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/backtest-engine-getter-retirement-implementation-2026-05-26.json`
- `docs/reports/quality/backend-backtest-engine-getter-retirement-implementation-2026-05-26.md`
- `governance/mainline/task-cards/pr-293.yaml`

Future implementation must preserve:

- `BacktestConfig`
- `BacktestResult`
- `BacktestEngine`
- `BacktestEngine.run_backtest`
- `BacktestEngine._simulate_trades`
- `BacktestEngine._calculate_metrics`
- `BacktestEngine._calculate_equity_curve`
- `BacktestEngine._calculate_max_drawdown`
- `BacktestEngine._empty_result`

## Required Future Gates

Before editing source in the future implementation lane:

- Run fresh GitNexus impact for `get_backtest_engine`.
- Run an exact text scan for `get_backtest_engine` and `_backtest_engine`.
- Stop if any external backend code caller appears outside `web/backend/app/services/backtest_engine.py`.
- Use TDD: add a focused failing test that proves the legacy getter surface is absent while `BacktestEngine` remains importable.

After source edit in the future implementation lane:

- Run the focused BacktestEngine getter-retirement test.
- Run Ruff and Black checks over touched backend files.
- Run GitNexus `detect_changes` on staged scope.
- Run the mainline scope gate after commit.

## Non-Goals

- No source or test edit in this authorization PR.
- No direct deletion of `get_backtest_engine` or `_backtest_engine` in this authorization PR.
- No route/API, OpenAPI, frontend, PM2, OpenSpec, or issue-label change.
- No authorization for `get_tdx_service`, `get_data_service`, `get_strategy_service`, `get_streaming_service`, route provider seams, root/risk compatibility facades, or other service lifecycle candidates.

## Rollback

If the future implementation causes an unexpected regression, restore `_backtest_engine` and `get_backtest_engine` in `web/backend/app/services/backtest_engine.py`, remove the focused regression test, and revert the implementation report/artifact/task-card/tree update.
