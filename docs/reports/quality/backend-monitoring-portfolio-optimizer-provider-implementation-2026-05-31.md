# Backend Monitoring Portfolio Optimizer Provider Implementation - 2026-05-31

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 item: `G2.269`
- Branch: `g2-269-monitoring-portfolio-optimizer-provider`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `1cb885e8267d76e47e0d08977002a80fafb56092`
- Parent PR: `#421`, merged at `1cb885e8267d76e47e0d08977002a80fafb56092`
- Source edit authority: path-limited, approved by G2.268

Boundary note: this implementation is limited to one route module and focused
tests. It does not change route registration, route paths, response models,
OpenAPI artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## Authorized Scope

| Category | Paths |
|---|---|
| Source | `web/backend/app/api/_monitoring_portfolio_router.py` |
| Focused tests | `tests/api/file_tests/test_monitoring_analysis_api.py`, `web/backend/tests/test_health_route_conflicts.py` |
| Governance evidence | generated JSON, this report, task card, and steward tree updates |

## GitNexus Pre-Edit

GitNexus MCP remained unavailable:

| Query | Result |
|---|---|
| `context(get_portfolio_optimizer)` | tool call failed: `Transport closed` |
| `impact(get_portfolio_optimizer)` | tool call failed: `Transport closed` |

CLI fallback succeeded:

| Metric | Value |
|---|---:|
| Risk | `HIGH` |
| Impacted count | 3 |
| Direct affected processes | 3 |
| Modules affected | 1 |

Affected processes:

- `get_portfolio_summary`
- `get_portfolio_alerts`
- `get_rebalance_suggestions`

Risk interpretation: the HIGH rating is accepted for this lane because all
directly affected processes are exactly the three G2.268-authorized route
handlers in `_monitoring_portfolio_router.py`.

## TDD Evidence

Red:

```text
pytest -o addopts= tests/api/file_tests/test_monitoring_analysis_api.py::TestMonitoringAnalysisAPIFile::test_monitoring_portfolio_optimizer_uses_route_dependency_provider -q --no-cov
FAILED: AssertionError: get_monitoring_portfolio_optimizer not found in module
```

Green:

```text
pytest -o addopts= tests/api/file_tests/test_monitoring_analysis_api.py::TestMonitoringAnalysisAPIFile::test_monitoring_portfolio_optimizer_uses_route_dependency_provider -q --no-cov
1 passed
```

## Implementation

`web/backend/app/api/_monitoring_portfolio_router.py` now has a route-local
provider:

```python
def get_monitoring_portfolio_optimizer():
    from src.monitoring.domain.portfolio_optimizer import get_portfolio_optimizer

    return get_portfolio_optimizer()
```

The three authorized handlers now receive `portfolio_optimizer` through
`Depends(get_monitoring_portfolio_optimizer)`:

- `get_portfolio_summary`
- `get_portfolio_alerts`
- `get_rebalance_suggestions`

After implementation:

| Metric | Value |
|---|---:|
| Route-local provider definitions | 1 |
| Provider backing `get_portfolio_optimizer()` calls | 1 |
| Direct route-body `get_portfolio_optimizer()` calls | 0 |
| Handler `portfolio_optimizer=Depends(...)` parameters | 3 |
| Handler `optimizer = portfolio_optimizer` assignments | 3 |

## Route / OpenAPI Verification

Runtime/OpenAPI smoke:

| Metric | Value |
|---|---:|
| FastAPI routes | 548 |
| OpenAPI paths | 500 |
| Duplicate operation IDs | 0 |
| Target module routes | 3 |

Target OpenAPI parameters remain unchanged:

| Path | Parameters |
|---|---|
| `/api/v1/monitoring/analysis/portfolio/{watchlist_id}/summary` | `watchlist_id`, `user_id` |
| `/api/v1/monitoring/analysis/portfolio/{watchlist_id}/alerts` | `watchlist_id`, `user_id`, `level` |
| `/api/v1/monitoring/analysis/portfolio/{watchlist_id}/rebalance` | `watchlist_id`, `user_id` |

## Verification

| Check | Result |
|---|---|
| Focused file tests | `20 passed` |
| Monitoring analysis OpenAPI/parameter guard | `1 passed` |
| Ruff on touched source/test files | `All checks passed` |
| GitNexus staged CLI fallback | exit `0`; `10` changed symbols; `9` affected processes; stale index `41c18309a555` -> `1cb885e8267` |
| Runtime/OpenAPI smoke | `548` routes, `500` paths, `0` duplicate operation IDs |

## Non-Goals

G2.269 does not:

- edit `src/monitoring/domain/portfolio_optimizer.py`
- edit non-target backend API modules
- change route paths, methods, parameters, response models, or OpenAPI exposure
- edit docs/api artifacts
- edit frontend, config, scripts, or OpenSpec
- run PM2 or stateful runtime gates

## Next Gate

After this PR is accepted, start:

`G2.270 no-source monitoring portfolio optimizer provider closeout / residual refresh`

G2.270 should close this source lane, re-scan monitoring/signal residuals, and
select the next candidate only through a no-source decision package.

## Rollback

Revert the future PR carrying this implementation. Rollback restores direct
route-body `get_portfolio_optimizer()` calls in `_monitoring_portfolio_router.py`
and removes only the focused test and governance evidence from this lane.
