# Backend Strategy Adapter Wrapper Closeout

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.175
- State: ready for review
- Date: 2026-05-27
- Current HEAD: `ba2572da6d31f05dcc65b735a361ceaa3435c280`
- Parent PR: `#327` merged, `refactor(backend): wrap legacy strategy adapter path`
- Scope: governance closeout for the Strategy legacy adapter wrapper lane

## Boundary

This closeout records verification and residual state after PR `#327`. It does
not edit backend source, backend tests, route/API behavior, OpenAPI exposure,
frontend code, PM2 workflows, OpenSpec content, config, scripts, compatibility
surfaces, or issue labels.

## Closeout Decision

G2.174 is closed as the legacy Strategy adapter compatibility-wrapper lane.

The legacy direct import path remains available:

```text
app.services.data_adapters.strategy.StrategyDataSourceAdapter
```

It now resolves to the canonical implementation:

```text
app.services.adapters.strategy_adapter.StrategyDataSourceAdapter
```

No compatibility surface was deleted.

## Post-Merge Verification

Commands were rerun from the G2.175 closeout worktree at current HEAD
`ba2572da6d31f05dcc65b735a361ceaa3435c280`.

| Check | Result |
|---|---|
| `gh pr view 327 --repo chengjon/mystocks --json number,state,mergedAt,mergeCommit,title,url` | `MERGED`, merge commit `ba2572da6d31f05dcc65b735a361ceaa3435c280` |
| `pytest -o addopts= web/backend/tests/test_adapter_mock_fallback_controls.py -q --no-cov --tb=short` | `7 passed` |
| `pytest -o addopts= web/backend/tests/test_logging_noise_regressions.py -q --no-cov --tb=short` | `10 passed` |
| `pytest -o addopts= web/backend/tests/test_strategy_management_route_provider.py web/backend/tests/test_backtest_tasks_regressions.py -q --no-cov --tb=short` | `8 passed` |
| `ruff check web/backend/app/services/data_adapters/strategy.py web/backend/tests/test_adapter_mock_fallback_controls.py` | passed |
| `black --check web/backend/app/services/data_adapters/strategy.py web/backend/tests/test_adapter_mock_fallback_controls.py` | passed |
| OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0` |

OpenAPI smoke used placeholder non-secret environment values and did not start
PM2 or execute stateful runtime gates.

## Residual Scan

Post-merge static scan at current HEAD:

- `web/backend/app/services/data_adapters/strategy.py` line count: `9`
- Legacy wrapper re-exports canonical class: yes
- Legacy wrapper defines `class StrategyDataSourceAdapter`: no
- Legacy wrapper contains direct `get_strategy_service`: no
- Production `.py` `get_strategy_service` hits under `web/backend/app`: `19`

Current production `.py` residual distribution:

| File | Hits | Disposition |
|---|---:|---|
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 6 | Route provider fallback retained by prior decision |
| `web/backend/app/tasks/backtest_tasks.py` | 2 | Closed task-local provider helper; not a reopened lane |
| `web/backend/app/services/adapters/strategy_adapter.py` | 10 | Canonical adapter/provider residual; candidate for future design refresh |
| `web/backend/app/services/strategy_service.py` | 1 | Public getter definition retained |

The legacy `app.services.data_adapters.strategy` path is no longer a production
`.py` residual owner in `web/backend/app`.

## Next Gate

Open a separate residual-refresh decision package before any further Strategy
source implementation. That package should decide whether the canonical
`web/backend/app/services/adapters/strategy_adapter.py` helper calls are a safe
next seam or whether Strategy should pause while the broader high-risk getter
tracks continue with realtime/socket, Dashboard/TDX, Indicator/Data, root facade
compatibility, or route dependency/provider governance.
