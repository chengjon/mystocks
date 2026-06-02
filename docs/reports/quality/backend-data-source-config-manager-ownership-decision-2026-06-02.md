# Backend Data Source Config Manager Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: `G2.317`
- Scope: no-source ownership / provider seam decision
- Prepared at: `2026-06-02T08:38:47+08:00`
- Base branch: `origin/wip/root-dirty-20260403`
- Base HEAD checked: `be512826ca7ba60d9609ddf9035522c1f863907c`
- Planned PR: `#470`
- Parent PR: `#469`, merged at `be512826ca7ba60d9609ddf9035522c1f863907c`

## Decision

`web/backend/app/api/data_source_config.py:get_config_manager_dependency` is already the active route provider seam for the data-source config routes.

The remaining concern is not route-body singleton usage. It is the backing ownership seam:

- `data_source_config.py` imports `get_config_manager` from `web/backend/app/api/_data_source_config_responses.py`
- `get_config_manager_dependency()` calls that backing helper once
- all 9 active route handlers use `Depends(get_config_manager_dependency)`
- `_data_source_config_responses.py` also owns response/router helper responsibilities

Because GitNexus CLI fallback reports the backing helper as `HIGH` risk with `9` direct callers and `3` affected processes, G2.317 does not authorize moving, deleting, or rewriting the helper.

## Evidence

| Check | Result |
|---|---|
| Parent PR state | PR `#469` is `MERGED` at `be512826ca7ba60d9609ddf9035522c1f863907c` |
| Active route module | `app.api.data_source_config` |
| Registered data-source config routes | `9` |
| Route-body direct `get_config_manager()` calls | `0` |
| Provider backing `get_config_manager()` calls | `1` at `data_source_config.py:103` |
| `Depends(get_config_manager_dependency)` bindings | `9` |
| Backing helper location | `_data_source_config_responses.py:338-352` |
| Route/OpenAPI smoke | `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation ID warnings |
| GitNexus MCP impact | failed with `Transport closed` |
| GitNexus CLI fallback | `HIGH`, `9` direct callers, `3` affected processes, `1` module |

## Registered Routes

| Method | Path | Dependency surface |
|---|---|---|
| `POST` | `/api/v1/data-sources/config/` | `get_config_manager_dependency`, `get_current_user` |
| `PUT` | `/api/v1/data-sources/config/{endpoint_name}` | `get_config_manager_dependency`, `get_current_user` |
| `DELETE` | `/api/v1/data-sources/config/{endpoint_name}` | `get_config_manager_dependency`, `get_current_user` |
| `GET` | `/api/v1/data-sources/config/{endpoint_name}` | `get_config_manager_dependency` |
| `GET` | `/api/v1/data-sources/config/` | `get_config_manager_dependency` |
| `POST` | `/api/v1/data-sources/config/batch` | `get_config_manager_dependency`, `get_current_user` |
| `GET` | `/api/v1/data-sources/config/{endpoint_name}/versions` | `get_config_manager_dependency` |
| `POST` | `/api/v1/data-sources/config/{endpoint_name}/rollback/{version}` | `get_config_manager_dependency`, `get_current_user` |
| `POST` | `/api/v1/data-sources/config/reload` | `get_config_manager_dependency`, `get_current_user` |

## Boundary

G2.317 must not be used as source implementation authority. In particular, this package does not authorize:

- editing `web/backend/app/api/data_source_config.py`
- editing `web/backend/app/api/_data_source_config_responses.py`
- moving `get_config_manager`
- splitting the response/helper module
- changing route paths, methods, response models, or generated OpenAPI artifacts
- editing tests, docs/api, frontend, config, scripts, OpenSpec, PM2, or runtime state

## Next Gate

Recommended next work item:

`G2.318 no-source service lifecycle residual candidate refresh after retaining data_source_config.get_config_manager as a high-risk backing seam`

G2.318 should refresh the residual queue and select a different candidate or route a separate high-risk design/authorization package. It should not treat G2.317 as approval to rewrite `data_source_config` internals.
