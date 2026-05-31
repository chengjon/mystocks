# Backend Strategy get_monitoring_db Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Workline: G2.277
- Type: no-source authorization package
- Prepared at: `2026-06-01T00:01:42+08:00`
- Base HEAD checked: `f48ede2ce2202318efa3411fe22fb83a8d4d920b`
- Parent gate: G2.276 risk `get_monitoring_db` provider closeout / residual refresh
- Parent PR: `#429`, merged at `f48ede2ce2202318efa3411fe22fb83a8d4d920b`

This package is authorization-only. It does not edit backend source, tests,
route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2,
or runtime state.

## Authorization Decision

If accepted, G2.277 authorizes only a future G2.278 path-limited implementation
for the strategy-management route/helper surface:

- `web/backend/app/api/strategy_management/_helpers.py`
- `web/backend/app/api/strategy_management/_strategy_crud_router.py`

The future implementation target is to move the active strategy route-body
`get_monitoring_db().log_operation(...)` calls, and the related helper-level
lifecycle logging seam where practical, onto an explicit strategy monitoring
database provider while preserving current fallback behavior and API contracts.

G2.277 does not authorize risk helper changes, utility helper changes,
non-strategy route/provider migrations, source retirement, route registration
changes, or OpenAPI artifact edits.

## GitNexus Evidence

MCP context / impact for `get_monitoring_db` returned `Transport closed`.

The CLI fallback with the disambiguated UID succeeded:

```text
target_uid: Function:web/backend/app/api/strategy_management/_helpers.py:get_monitoring_db
risk: LOW
impacted_count: 7
direct: 3
processes_affected: 0
modules_affected: 1
affected_module: Strategy_management
```

Direct affected symbols:

| Symbol | Path |
|---|---|
| `_handle_strategy_lifecycle_action` | `web/backend/app/api/strategy_management/_helpers.py` |
| `list_strategies` | `web/backend/app/api/strategy_management/_strategy_crud_router.py` |
| `create_strategy` | `web/backend/app/api/strategy_management/_strategy_crud_router.py` |

Depth-2 symbols observed by the CLI fallback:

- `start_strategy`
- `pause_strategy`
- `resume_strategy`
- `stop_strategy`

GitNexus index status is still a stale warning with `commits_behind=0` and
`has_embeddings=false`. A future source lane must re-run impact before editing
and must stop if the risk level changes to HIGH or CRITICAL outside the exact
authorized target files.

## Strategy Surface Evidence

Definition:

- `web/backend/app/api/strategy_management/_helpers.py:420`

Current call sites:

| File | Line | Function | Classification |
|---|---:|---|---|
| `web/backend/app/api/strategy_management/_helpers.py` | 393 | `_handle_strategy_lifecycle_action` | helper-level lifecycle log call |
| `web/backend/app/api/strategy_management/_helpers.py` | 409 | `_handle_strategy_lifecycle_action` | helper-level lifecycle log call |
| `web/backend/app/api/strategy_management/_strategy_crud_router.py` | 157 | `list_strategies` | active route-body log call |
| `web/backend/app/api/strategy_management/_strategy_crud_router.py` | 174 | `list_strategies` | active route-body log call |
| `web/backend/app/api/strategy_management/_strategy_crud_router.py` | 254 | `create_strategy` | active route-body log call |
| `web/backend/app/api/strategy_management/_strategy_crud_router.py` | 271 | `create_strategy` | active route-body log call |

Deferred same-name helper:

- `web/backend/app/utils/risk_utils.py` defines another `get_monitoring_db()`
  helper, but the scoped scan found `0` active API route-body calls for that
  utility surface. It remains outside G2.277.

Decision: do not create a combined risk/strategy/utility implementation lane.
Risk is closed by G2.275/G2.276. Strategy-management should be handled by a
separate path-limited implementation only after this authorization package is
accepted.

## Route / OpenAPI Evidence

The route/OpenAPI smoke used temporary placeholder environment values only to
satisfy import-time settings validation. It did not run PM2 or a stateful
database workflow.

| Metric | Value |
|---|---:|
| FastAPI route count | 548 |
| OpenAPI path count | 500 |
| Duplicate operation IDs | 0 |

Target endpoints:

| Path | Method | Endpoint | Parameter count | Request body | Response codes |
|---|---|---|---:|---|---|
| `/api/v1/strategy/strategies` | `GET` | `list_strategies` | 4 | no | `200`, `400`, `404`, `422`, `500` |
| `/api/v1/strategy/strategies` | `POST` | `create_strategy` | 0 | yes | `200`, `400`, `404`, `422`, `500` |
| `/api/v1/strategy/strategies/{strategy_id}` | `GET` | `get_strategy` | 1 | no | `200`, `400`, `404`, `422`, `500` |

Future G2.278 must preserve route paths, methods, response contracts, and
OpenAPI parameter counts. If a dependency provider parameter leaks into
OpenAPI, the implementation must be corrected before review.

## Focused Test Inventory

Focused command attempted:

```text
env PYTHONPATH=web/backend pytest -o addopts= tests/api/file_tests/test_strategy_management_api.py -q -n 0 --tb=short --no-cov
```

Result:

```text
3 failed, 7 passed, 1 warning
```

Failure classification: existing strategy file-test drift, not a G2.277
no-source authorization regression.

Observed failures:

- `test_router_registers_expected_strategy_routes` expects
  `strategy_module.router.prefix == "/api/v1/strategy"`, but the current package
  router prefix is empty.
- `test_router_contains_expected_number_of_route_method_pairs` expects `16`
  route/method pairs, while current code exposes `23`.
- `test_chart_data_function_is_exported_but_not_wired_into_package_router`
  expects chart-data to be unwired, but current router includes it.

Authorized future test paths:

- `tests/api/file_tests/test_strategy_management_api.py`
- `web/backend/tests/test_health_route_conflicts.py`

G2.277 does not authorize broad strategy test cleanup. If G2.278 needs to edit
the file-test expectations, it must keep those edits directly tied to provider
injection verification and record the pre-existing route expectation drift.

## Governance Verification

GitNexus staged verification for this no-source package:

```text
ok: true
status: stale
changed_files: 9
changed_symbols: 0
affected_processes: 0
risk_level: low
indexed_commit: 39c8a3b2d7ca4a85f66ccaacb17894f52451602e
current_commit: f48ede2ce2202318efa3411fe22fb83a8d4d920b
```

The stale warning is recorded as an index freshness warning, not a source
impact finding. This branch changes only governance files.

## Future G2.278 Authorized Shape

Only after G2.277 is accepted, G2.278 may:

- Add a strategy-management-local dependency provider or equivalent
  route-provider seam for the strategy monitoring database helper.
- Replace direct route-body
  `get_monitoring_db().log_operation(...)` calls in `list_strategies` and
  `create_strategy` with dependency-supplied monitoring database object usage.
- Route `_handle_strategy_lifecycle_action` logging through the same explicit
  strategy monitoring database seam where practical without changing public
  route contracts.
- Preserve existing `MonitoringDatabase` fallback behavior.
- Add or update focused tests in the authorized test paths.

## Future G2.278 Forbidden Scope

- `web/backend/app/api/risk/**`
- `web/backend/app/utils/risk_utils.py`
- non-strategy route/provider migrations
- route registration changes
- route path, method, response shape, or OpenAPI artifact changes
- frontend, config, scripts, OpenSpec, PM2, or runtime state
- source retirement or compatibility deletion

## Required Future Verification

G2.278 must provide fresh evidence for:

- GitNexus impact before source edits using
  `Function:web/backend/app/api/strategy_management/_helpers.py:get_monitoring_db`.
- TDD red/green or equivalent regression proof for the route-provider behavior.
- Targeted strategy tests or a precise record of pre-existing strategy file-test
  drift.
- Ruff on touched backend files.
- `app.openapi()` remains `500` paths with duplicate operation IDs `0`.
- Target endpoint OpenAPI parameter counts remain unchanged.

## Evidence Artifacts

- `.planning/codebase/generated/strategy-get-monitoring-db-provider-authorization-2026-05-31.json`
- `docs/reports/quality/backend-strategy-get-monitoring-db-provider-authorization-2026-05-31.md`
- `governance/mainline/task-cards/pr-430.yaml`
