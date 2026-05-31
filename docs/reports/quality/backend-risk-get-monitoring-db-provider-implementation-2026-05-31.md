# Backend Risk get_monitoring_db Provider Implementation - 2026-05-31

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 item: `G2.275`
- Branch: `g2-275-risk-get-monitoring-db-provider`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `16df80c30eb4fceec78a13630e40167f0e4037ca`
- Parent PR: `#427`, merged at `16df80c30eb4fceec78a13630e40167f0e4037ca`
- Source edit authority: path-limited, approved by G2.274

Boundary note: this implementation is limited to the risk `get_monitoring_db`
route-provider seam and focused tests. It does not change route registration,
route paths, response models, generated OpenAPI artifacts, docs/api artifacts,
strategy-management helpers, `web/backend/app/utils/risk_utils.py`, frontend,
config, scripts, OpenSpec, PM2, or runtime state.

## Authorized Scope

| Category | Paths |
|---|---|
| Source | `web/backend/app/api/risk/_shared.py`, `web/backend/app/api/risk/alerts.py`, `web/backend/app/api/risk/metrics.py` |
| Focused tests | `tests/api/file_tests/test_risk_management_api.py`, `web/backend/tests/test_health_route_conflicts.py`, `web/backend/tests/test_week1_risk_api.py` |
| Governance evidence | generated JSON, this report, task card, and steward tree updates |

## GitNexus Pre-Edit

GitNexus MCP remained unavailable:

| Query | Result |
|---|---|
| `impact(Function:web/backend/app/api/risk/_shared.py:get_monitoring_db)` | tool call failed: `Transport closed` |

CLI fallback succeeded:

| Metric | Value |
|---|---:|
| Risk | `LOW` |
| Impacted count | 3 |
| Direct symbols | 3 |
| Processes affected | 0 |
| Modules affected | 1 |

Direct affected symbols:

- `web/backend/app/api/risk/alerts.py:create_risk_alert`
- `web/backend/app/api/risk/metrics.py:calculate_var_cvar`
- `web/backend/app/api/risk/metrics.py:calculate_beta`

Risk interpretation: the LOW rating matches the G2.274 authorization. The
direct symbols are exactly the three target risk handlers.

## TDD Evidence

Red:

```text
PYTHONPATH=web/backend pytest -o addopts= tests/api/file_tests/test_risk_management_api.py::TestRiskManagementAPIFile::test_risk_monitoring_db_uses_route_dependency_provider -q -n 0 --tb=short --no-cov
FAILED: AssertionError because app.api.risk._shared did not yet expose get_risk_monitoring_db
```

Green:

```text
PYTHONPATH=web/backend pytest -o addopts= tests/api/file_tests/test_risk_management_api.py::TestRiskManagementAPIFile::test_risk_monitoring_db_uses_route_dependency_provider -q -n 0 --tb=short --no-cov
1 passed
```

## Implementation

`web/backend/app/api/risk/_shared.py` now exposes a risk-local provider:

```python
def get_risk_monitoring_db():
    return get_monitoring_db()
```

The three authorized handlers now receive `monitoring_db` through
`Depends(get_risk_monitoring_db)`:

- `create_risk_alert`
- `calculate_var_cvar`
- `calculate_beta`

After implementation:

| Metric | Value |
|---|---:|
| Provider definitions | 1 |
| Provider backing `get_monitoring_db()` calls | 1 |
| Direct route-body `get_monitoring_db()` calls in `alerts.py` / `metrics.py` | 0 |
| Handler `Depends(get_risk_monitoring_db)` parameters | 3 |
| Handler `monitoring_db.log_operation(...)` calls | 6 |

Lint seam note: `alerts.py` also needed companion helper imports from
`_alerts_responses.py` plus a local `noqa` for the existing route handler named
`test_notification`. These changes are lint-only and do not alter route
contracts.

## Route / OpenAPI Verification

Runtime/OpenAPI smoke used placeholder import-time environment values and did
not run PM2 or stateful integration gates.

| Metric | Value |
|---|---:|
| FastAPI routes | 548 |
| OpenAPI paths | 500 |
| Duplicate operation IDs | 0 |

Target OpenAPI operations remain documented without additional query
parameters:

| Operation | Parameters | Request body | Operation ID |
|---|---:|---|---|
| `POST /api/v1/risk/alerts` | 0 | yes | `create_risk_alert_api_v1_risk_alerts_post` |
| `POST /api/v1/risk/var-cvar` | 0 | yes | `calculate_var_cvar_api_v1_risk_var_cvar_post` |
| `POST /api/v1/risk/beta` | 0 | yes | `calculate_beta_api_v1_risk_beta_post` |

## Verification

| Check | Result |
|---|---|
| Focused provider test | `1 passed` |
| Provider test + health route conflicts | `122 passed` |
| Ruff on touched source/test files | `All checks passed` |
| GitNexus staged CLI fallback | exit `0`; status `stale`; `13` changed symbols/files; `0` affected processes; risk `low`; indexed `7832a6d4adc4` -> current `16df80c30eb4` |
| Static source check | direct route-body `get_monitoring_db()` calls in target route modules: `0`; dependency params: `3`; `monitoring_db.log_operation(...)`: `6` |
| Runtime/OpenAPI smoke | `548` routes, `500` paths, `0` duplicate operation IDs |

An earlier combined target-test attempt produced one OpenAPI schema generation
failure in
`test_risk_v31_stop_loss_write_endpoints_have_docs_and_request_examples`. The
single test then passed, and the full combined target rerun passed `122/122`.
This is recorded as order/cache sensitivity evidence, not as a remaining
blocking failure for G2.275.

`web/backend/tests/test_week1_risk_api.py` was also attempted because G2.274
listed it as an authorized focused risk test path. It remains blocked by
pre-existing test debt:

| Result | Known debt |
|---|---|
| `4 failed, 11 passed, 4 errors` | missing fixtures `sample_portfolio_positions` and `sample_risk_alert_data`; GET/POST expectation drift returning `405`; local monitoring DB connection refused for side-effect logging |

## Non-Goals

G2.275 does not:

- edit `web/backend/app/api/strategy_management/**`
- edit `web/backend/app/utils/risk_utils.py`
- change route registration, route paths, route methods, response models, or
  generated OpenAPI artifacts
- edit docs/api artifacts
- edit frontend, config, scripts, or OpenSpec
- run PM2 or stateful runtime gates
- start strategy helper, utility helper, or broader risk architecture work

## Next Gate

After this PR is accepted, start:

`G2.276 no-source risk get_monitoring_db provider closeout / residual refresh`

G2.276 should record the accepted implementation, verify the risk route-body
residual is closed, and choose the next candidate only through a no-source
decision package.

## Rollback

Revert the future PR carrying this implementation. Rollback restores the six
direct route-body `get_monitoring_db().log_operation(...)` calls and
removes only the focused provider test and governance evidence from this lane.
