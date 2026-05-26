# Backend BacktestEngine Getter Retirement Implementation

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-26

Base HEAD: `0f78609e25898181ea5653edc7350efc03a3bb9b`

Authorization: G2.139 / PR `#292`

Boundary note: this implementation is limited to the authorized BacktestEngine legacy singleton/getter retirement. It does not change route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or unrelated service lifecycle candidates.

## Scope

Changed runtime file:

- `web/backend/app/services/backtest_engine.py`

Added focused test:

- `web/backend/tests/test_backtest_engine_getter_retirement.py`

Retired symbols:

- `_backtest_engine`
- `get_backtest_engine`

Preserved symbols:

- `BacktestConfig`
- `BacktestResult`
- `BacktestEngine`
- Existing `BacktestEngine` methods

## Pre-Edit Gate

GitNexus upstream impact for `get_backtest_engine`:

| Risk | Impacted | Direct | Processes | Modules |
|---|---:|---:|---:|---:|
| LOW | 0 | 0 | 0 | 0 |

## TDD Evidence

Red run:

```text
1 failed, 1 passed
```

The failing assertion proved `_backtest_engine` was still present before the implementation.

Green run:

```text
2 passed in 0.77s
```

Command:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_backtest_engine_getter_retirement.py -q --no-cov --tb=short
```

## Post-Edit Evidence

Exact scan after edit:

| Item | Count |
|---|---:|
| `BacktestEngine` definition | 1 |
| `get_backtest_engine` definition | 0 |
| `_backtest_engine` token count | 0 |

Remaining `get_backtest_engine` text reference:

- `web/backend/tests/test_backtest_engine_getter_retirement.py`

Import smoke after edit:

| Check | Result |
|---|---|
| `BacktestConfig` importable | yes |
| `BacktestResult` importable | yes |
| `BacktestEngine` importable | yes |
| module has `get_backtest_engine` | no |
| module has `_backtest_engine` | no |

Lint/format checks:

- Ruff touched files: passed.
- Black check touched files: passed.

## Non-Goals

- No route/API behavior change.
- No OpenAPI exposure change.
- No frontend or PM2 workflow change.
- No OpenSpec or GitHub issue-label change.
- No implementation for `get_tdx_service`, `get_data_service`, `get_strategy_service`, `get_streaming_service`, route provider seams, root/risk compatibility facades, or other service lifecycle candidates.

## Next Gate

After this implementation is reviewed and merged, prepare a closeout packet that verifies:

- PR state and merge commit.
- Focused test still passes.
- Exact scan still reports `get_backtest_engine` definition `0` and `_backtest_engine` token count `0`.
- `BacktestEngine`, `BacktestConfig`, and `BacktestResult` remain importable.
