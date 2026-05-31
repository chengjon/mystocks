# Backend Strategy get_monitoring_db Provider Implementation - 2026-06-01

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 item: `G2.278`
- Branch: `g2-278-strategy-get-monitoring-db-provider`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `2d1d2c28fe59bd7b98f63a41b9a0ff4c343d0441`
- Parent PR: `#430`, merged at `2d1d2c28fe59bd7b98f63a41b9a0ff4c343d0441`
- Source edit authority: path-limited, approved by G2.277

Boundary note: this implementation is limited to the strategy-management
`get_monitoring_db` route-provider seam and focused tests. It does not change
route registration, route paths, response models, generated OpenAPI artifacts,
docs/api artifacts, risk helpers, `web/backend/app/utils/risk_utils.py`,
frontend, config, scripts, OpenSpec, PM2, or runtime state.

## Authorized Scope

| Category | Paths |
|---|---|
| Source | `web/backend/app/api/strategy_management/_helpers.py`, `web/backend/app/api/strategy_management/_strategy_crud_router.py` |
| Focused tests | `tests/api/file_tests/test_strategy_management_api.py`, `web/backend/tests/test_health_route_conflicts.py` |
| Governance evidence | generated JSON, this report, task card, and steward tree updates |

## GitNexus Pre-Edit

GitNexus MCP remained unavailable:

| Query | Result |
|---|---|
| `impact(Function:web/backend/app/api/strategy_management/_helpers.py:get_monitoring_db)` | tool call failed: `Transport closed` |

CLI fallback succeeded:

| Symbol | Risk | Impacted | Direct | Processes |
|---|---|---:|---:|---:|
| `get_monitoring_db` | `LOW` | 7 | 3 | 0 |
| `list_strategies` | `LOW` | 0 | 0 | 0 |
| `create_strategy` | `LOW` | 0 | 0 | 0 |
| `_handle_strategy_lifecycle_action` | `LOW` | 4 | 4 | 0 |

Risk interpretation: the LOW ratings match the G2.277 authorization. The
direct symbols are inside the strategy-management target surface or its known
lifecycle callers.

## TDD Evidence

Red:

```text
PYTHONPATH=web/backend pytest -o addopts= tests/api/file_tests/test_strategy_management_api.py::TestStrategyManagementAPIFile::test_strategy_monitoring_db_uses_route_dependency_provider -q -n 0 --tb=short --no-cov
FAILED: AttributeError because app.api.strategy_management._helpers did not yet expose get_strategy_monitoring_db
```

Green:

```text
PYTHONPATH=web/backend pytest -o addopts= tests/api/file_tests/test_strategy_management_api.py::TestStrategyManagementAPIFile::test_strategy_monitoring_db_uses_route_dependency_provider -q -n 0 --tb=short --no-cov
1 passed, 1 warning
```

## Implementation

`web/backend/app/api/strategy_management/_helpers.py` now exposes a
strategy-local provider:

```python
def get_strategy_monitoring_db() -> Any:
    return get_monitoring_db()
```

`_handle_strategy_lifecycle_action` now accepts a `monitoring_db` object and
falls back to the strategy provider when called without one.

The six authorized strategy handlers now receive `monitoring_db` through
`Depends(get_strategy_monitoring_db)`:

- `list_strategies`
- `create_strategy`
- `start_strategy`
- `pause_strategy`
- `resume_strategy`
- `stop_strategy`

After implementation:

| Metric | Value |
|---|---:|
| Provider definitions | 1 |
| Provider backing `get_monitoring_db()` calls | 1 |
| Direct `get_monitoring_db().log_operation(...)` calls in target files | 0 |
| Handler `Depends(get_strategy_monitoring_db)` parameters | 6 |
| Handler/helper `monitoring_db.log_operation(...)` calls | 6 |

## Route / OpenAPI Verification

Runtime/OpenAPI smoke used placeholder import-time environment values and did
not run PM2 or stateful integration gates.

| Metric | Value |
|---|---:|
| FastAPI routes | 548 |
| OpenAPI paths | 500 |
| Duplicate operation IDs | 0 |

Target OpenAPI operations remain documented without `monitoring_db` parameter
leakage:

| Operation | Parameters | Request body | `monitoring_db` leaked | Operation ID |
|---|---:|---|---|---|
| `GET /api/v1/strategy/strategies` | 4 | no | no | `list_strategies_api_v1_strategy_strategies_get` |
| `POST /api/v1/strategy/strategies` | 0 | yes | no | `create_strategy_api_v1_strategy_strategies_post` |
| `POST /api/v1/strategy/{strategy_id}/start` | 1 | no | no | `start_strategy_api_v1_strategy__strategy_id__start_post` |
| `POST /api/v1/strategy/{strategy_id}/pause` | 1 | no | no | `pause_strategy_api_v1_strategy__strategy_id__pause_post` |
| `POST /api/v1/strategy/{strategy_id}/resume` | 1 | no | no | `resume_strategy_api_v1_strategy__strategy_id__resume_post` |
| `POST /api/v1/strategy/{strategy_id}/stop` | 1 | no | no | `stop_strategy_api_v1_strategy__strategy_id__stop_post` |

## Verification

| Check | Result |
|---|---|
| Focused provider test | `1 passed, 1 warning` |
| Full strategy file test attempt | `3 failed, 8 passed, 1 warning` |
| Health route conflicts | `121 passed` |
| Ruff on touched source/test files | `All checks passed` |
| GitNexus staged CLI fallback | exit `0`; status `stale`; `12` changed files; `14` changed symbols; `0` affected processes; risk `low`; indexed `39c8a3b2d7ca` -> current `2d1d2c28fe59` |
| Static source check | direct target `get_monitoring_db().log_operation(...)`: `0`; dependency params: `6`; `monitoring_db.log_operation(...)`: `6` |
| Runtime/OpenAPI smoke | `548` routes, `500` paths, `0` duplicate operation IDs; target `monitoring_db` leaks: `false` |

The full strategy file test retains the same pre-existing route-contract test
debt recorded by G2.277:

| Failure | Existing drift |
|---|---|
| `test_router_registers_expected_strategy_routes` | expects `router.prefix == "/api/v1/strategy"` while current package router prefix is empty |
| `test_router_contains_expected_number_of_route_method_pairs` | expects `16` route/method pairs while current router exposes `23` |
| `test_chart_data_function_is_exported_but_not_wired_into_package_router` | expects chart-data unwired while current router includes it |

## Non-Goals

G2.278 does not:

- edit `web/backend/app/api/risk/**`
- edit `web/backend/app/utils/risk_utils.py`
- change route registration, route paths, route methods, response models, or
  generated OpenAPI artifacts
- edit docs/api artifacts
- edit frontend, config, scripts, or OpenSpec
- run PM2 or stateful runtime gates
- start non-strategy helper, utility helper, or broader strategy architecture work

## Next Gate

After this PR is accepted, start:

`G2.279 no-source strategy get_monitoring_db provider closeout / residual refresh`

G2.279 should record the accepted implementation, verify the strategy route-body
residual is closed, and choose any next candidate only through a no-source
decision package.

## Rollback

Revert the future PR carrying this implementation. Rollback restores the direct
strategy `get_monitoring_db().log_operation(...)` calls and removes only the
focused provider test and governance evidence from this lane.
