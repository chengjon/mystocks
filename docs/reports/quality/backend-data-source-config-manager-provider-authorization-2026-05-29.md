# Backend Data-Source Config Manager Provider Authorization

> **历史总结说明**: 本报告记录 `G2.232` 的 no-source 决策 / 授权边界，不代表当前 PR 改动源码。若需确认当前实现事实，请优先以当前代码、`architecture/STANDARDS.md`、根目录 `AGENTS.md`、OpenSpec 状态和最近一次实际验证结果为准。

## Status

- G2: `G2.232`
- Status: authorization for review
- Branch: `g2-232-data-source-config-manager-provider-authorization`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `05c84d1f4f5e42d9db0ace21ef3ba110dacbc184`
- Source edit authority in this PR: none

Boundary note: G2.232 decides whether a later implementation lane may proceed.
It does not edit backend source, tests, OpenSpec proposals/specs, route
contracts, PM2 state, or frontend files.

## Parent State

PR `#384` merged G2.231 and selected `get_config_manager` as the next
service-lifecycle residual candidate:

| Evidence | Value |
|---|---:|
| Active route file | `web/backend/app/api/data_source_config.py` |
| Active route-body `get_config_manager()` calls | 9 |
| Legacy `data_source_config.old.py` false-positive calls | 8 |
| GitNexus risk | HIGH |
| GitNexus direct callers | 9 |
| GitNexus affected processes | 3 |

`web/backend/app/router_registry.py` imports `app.api.data_source_config` and
includes `data_source_config.router`. It does not register
`data_source_config.old.py`, so the `.old.py` calls remain historical
false positives and are not an implementation target.

## Current Shape

`data_source_config.py` imports `router`, `get_current_user`, and
`get_config_manager` from `_data_source_config_responses.py`. The current route
handlers call `get_config_manager()` inside function bodies. This works, but it
mixes response/OpenAPI constants with runtime route dependencies and keeps the
manager outside FastAPI dependency injection.

The active route handlers with route-body manager calls are:

- `create_data_source`
- `update_data_source`
- `delete_data_source`
- `get_data_source`
- `list_data_sources`
- `batch_operations`
- `get_version_history`
- `rollback_to_version`
- `reload_config`

## Decision

Authorize G2.233 as a future path-limited source implementation lane after this
authorization package is reviewed and accepted.

G2.233 may:

- edit `web/backend/app/api/data_source_config.py`
- add or update focused tests under:
  - `tests/api/file_tests/test_data_source_config_api.py`
  - `web/backend/tests/test_data_source_config_provider_injection.py`
- introduce a route-local `DataSourceConfigManager` dependency/provider wrapper
- inject the manager into the 9 active route handlers
- preserve the existing backing `get_config_manager()` behavior

G2.233 must preserve:

- route paths
- router registration
- auth/current_user dependencies
- response models and `UnifiedResponse` shape
- OpenAPI exposure
- `data_source_config.old.py` untouched
- `_data_source_config_responses.py` behavior unless a later package explicitly
  authorizes response/dependency separation

## Exit Criteria For G2.233

| Check | Expected |
|---|---:|
| Active route-body `get_config_manager()` calls | 0 |
| Active route dependency/provider manager uses | 9 |
| Legacy `.old.py` false-positive calls | unchanged / not edited |
| App route count | 548 unless unrelated current-HEAD drift is documented |
| OpenAPI path count | 500 unless unrelated current-HEAD drift is documented |

## Non-Goals

- Do not edit source from G2.232.
- Do not delete or edit `data_source_config.old.py`.
- Do not move router construction out of `_data_source_config_responses.py` from
  G2.232.
- Do not change route paths, response models, auth, OpenAPI exposure, SQL, or
  external service behavior.
- Do not batch this with `get_calculator_factory`, `get_mock_data_manager`,
  `get_monitoring_db`, Strategy provider seams, or cache prewarming.

## Evidence Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/data-source-config-manager-provider-authorization-2026-05-29.json` | Machine-readable G2.232 authorization evidence |
| `docs/reports/quality/backend-data-source-config-manager-provider-authorization-2026-05-29.md` | Human-readable authorization report |
| `governance/mainline/task-cards/pr-385.yaml` | Mainline governance scope card |
