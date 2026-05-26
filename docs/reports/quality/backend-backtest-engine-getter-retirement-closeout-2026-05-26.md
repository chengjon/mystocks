# Backend BacktestEngine Getter Retirement Closeout

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-26

Current HEAD: `62cf56cc8736c3784f8b7cc9ac5cc21a52d39423`

Parent implementation: G2.140 / PR `#293`

Boundary note: this is a closeout-only package. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or other service lifecycle candidates.

## Parent Merge

| Field | Value |
|---|---|
| Parent PR | `#293` |
| Parent state | `MERGED` |
| Parent merged at | `2026-05-26T05:32:51Z` |
| Parent merge commit | `62cf56cc8736c3784f8b7cc9ac5cc21a52d39423` |
| Parent title | `G2.140 Retire BacktestEngine getter` |
| Parent URL | `https://github.com/chengjon/mystocks/pull/293` |

## Verification

Focused closeout test:

```text
2 passed in 0.57s
```

Command:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_backtest_engine_getter_retirement.py -q --no-cov --tb=short
```

Exact scan:

| Item | Count |
|---|---:|
| `BacktestEngine` definition | 1 |
| `get_backtest_engine` definition | 0 |
| `_backtest_engine` token count | 0 |

Remaining `get_backtest_engine` text reference:

- `web/backend/tests/test_backtest_engine_getter_retirement.py`

Import smoke:

| Check | Result |
|---|---|
| `BacktestConfig` importable | yes |
| `BacktestResult` importable | yes |
| `BacktestEngine` importable | yes |
| module has `get_backtest_engine` | no |
| module has `_backtest_engine` | no |

## Closeout Result

The BacktestEngine legacy singleton/getter retirement lane is closed as implemented and verified.

Retired:

- `_backtest_engine`
- `get_backtest_engine`

Preserved:

- `BacktestConfig`
- `BacktestResult`
- `BacktestEngine`
- Existing `BacktestEngine` methods

## Next Gate

Refresh the remaining service lifecycle candidate pool before selecting another implementation lane.

## Non-Goals

- No backend source or test edit in this closeout PR.
- No route/API, OpenAPI, frontend, PM2, OpenSpec, or issue-label change.
- No authorization for another service lifecycle implementation lane.
