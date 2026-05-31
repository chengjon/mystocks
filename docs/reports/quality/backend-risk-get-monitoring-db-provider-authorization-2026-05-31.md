# Backend Risk get_monitoring_db Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Workline: G2.274
- Type: no-source authorization package
- Prepared at: `2026-05-31T20:39:29+08:00`
- Base HEAD checked: `0de77f3d05b1b6242515f2b86fce03c0eba37aaa`
- Parent gate: G2.273 `get_monitoring_db` ownership / route-provider decision
- Parent PR: `#426`, merged at `0de77f3d05b1b6242515f2b86fce03c0eba37aaa`

This package is authorization-only. It does not edit backend source, tests,
route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2,
or runtime state.

## Authorization Decision

If accepted, G2.274 authorizes only a future G2.275 path-limited implementation
for the risk route surface:

- `web/backend/app/api/risk/_shared.py`
- `web/backend/app/api/risk/alerts.py`
- `web/backend/app/api/risk/metrics.py`

The future implementation target is to move the three authorized risk handlers
away from direct route-body `get_monitoring_db()` calls and onto a
dependency-supplied risk monitoring database object, while preserving current
fallback behavior and API contracts.

G2.274 does not authorize strategy-management changes, utility helper changes,
source retirement, route registration changes, or OpenAPI artifact edits.

## GitNexus Evidence

MCP impact for `get_monitoring_db` returned `Transport closed`.

The CLI fallback with the disambiguated UID succeeded:

```text
target_uid: Function:web/backend/app/api/risk/_shared.py:get_monitoring_db
risk: LOW
impacted_count: 3
direct: 3
processes_affected: 0
modules_affected: 1
affected_module: Risk
```

Direct affected symbols:

| Symbol | Path |
|---|---|
| `create_risk_alert` | `web/backend/app/api/risk/alerts.py` |
| `calculate_var_cvar` | `web/backend/app/api/risk/metrics.py` |
| `calculate_beta` | `web/backend/app/api/risk/metrics.py` |

GitNexus index status is still a stale warning with `commits_behind=0` and
`has_embeddings=false`. A future source lane must re-run impact before editing
and must stop if the risk level changes to HIGH or CRITICAL outside the exact
authorized target handlers.

## Risk Surface Evidence

Definition:

- `web/backend/app/api/risk/_shared.py:128`

Target source file sizes:

| File | Lines |
|---|---:|
| `web/backend/app/api/risk/_shared.py` | 210 |
| `web/backend/app/api/risk/alerts.py` | 646 |
| `web/backend/app/api/risk/metrics.py` | 670 |

Current route-body call sites:

| File | Line | Handler |
|---|---:|---|
| `web/backend/app/api/risk/alerts.py` | 395 | `create_risk_alert` |
| `web/backend/app/api/risk/alerts.py` | 412 | `create_risk_alert` |
| `web/backend/app/api/risk/metrics.py` | 301 | `calculate_var_cvar` |
| `web/backend/app/api/risk/metrics.py` | 327 | `calculate_var_cvar` |
| `web/backend/app/api/risk/metrics.py` | 401 | `calculate_beta` |
| `web/backend/app/api/risk/metrics.py` | 420 | `calculate_beta` |

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

| Path | Method | Endpoint | Parameter count | Request body |
|---|---|---|---:|---|
| `/api/v1/risk/alerts` | `POST` | `create_risk_alert` | 0 | yes |
| `/api/v1/risk/var-cvar` | `POST` | `calculate_var_cvar` | 0 | yes |
| `/api/v1/risk/beta` | `POST` | `calculate_beta` | 0 | yes |

Future G2.275 must preserve these route paths, methods, response contracts, and
OpenAPI parameter counts. If a dependency provider parameter leaks into
OpenAPI, the implementation must be corrected before review.

## Future G2.275 Authorized Shape

Only after G2.274 is accepted, G2.275 may:

- Add a risk-local dependency provider or equivalent route-provider seam for
  the risk monitoring database helper.
- Replace direct route-body `get_monitoring_db().log_operation(...)` calls in
  the three authorized handlers with dependency-supplied monitoring database
  object usage.
- Preserve existing `MonitoringDatabase` fallback behavior in `_shared.py`.
- Add or update focused tests in the authorized test paths.

Authorized future test paths:

- `tests/api/file_tests/test_risk_management_api.py`
- `web/backend/tests/test_week1_risk_api.py`
- `web/backend/tests/test_health_route_conflicts.py`

Reference-only tests observed but not authorized for edit by G2.274:

- `tests/backend/test_risk_management_regression.py`
- `tests/backend/test_risk_management_core.py`
- `tests/e2e/test_risk.py`

## Future G2.275 Forbidden Scope

- `web/backend/app/api/strategy_management/**`
- `web/backend/app/utils/risk_utils.py`
- route registration changes
- route path, method, response shape, or OpenAPI artifact changes
- frontend, config, scripts, OpenSpec, PM2, or runtime state
- source retirement or compatibility deletion

## Required Future Verification

G2.275 must provide fresh evidence for:

- GitNexus impact before source edits using
  `Function:web/backend/app/api/risk/_shared.py:get_monitoring_db`.
- TDD red/green for the route-provider dependency behavior.
- Targeted risk API tests.
- Ruff on touched backend files.
- `app.openapi()` remains `500` paths with duplicate operation IDs `0`.
- Target endpoint OpenAPI parameter counts remain unchanged.

## Evidence Artifacts

- `.planning/codebase/generated/risk-get-monitoring-db-provider-authorization-2026-05-31.json`
- `docs/reports/quality/backend-risk-get-monitoring-db-provider-authorization-2026-05-31.md`
- `governance/mainline/task-cards/pr-427.yaml`
