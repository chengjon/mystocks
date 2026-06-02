# Backend Watchlist DataSourceFactory Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: `G2.319`
- Scope: no-source ownership / route-provider decision
- Prepared at: `2026-06-02T09:07:10+08:00`
- Base branch: `origin/wip/root-dirty-20260403`
- Base HEAD checked: `366739062b43f1e49aef892c0a20b7f9d068e0cb`
- Planned PR: `#472`
- Parent PR: `#471`, merged at `366739062b43f1e49aef892c0a20b7f9d068e0cb`

## Decision

`web/backend/app/api/watchlist.py` is an active route-local DataSourceFactory adapter seam.

The route module imports `DataSourceFactory` from `app.services.data_source_factory`. Eight active route handlers construct `DataSourceFactory()` inside the route body, then call `get_data_source("watchlist")`, then call adapter `get_data(...)`.

This is a real service lifecycle / provider candidate, but G2.319 does not authorize implementation because GitNexus exact impact is unresolved:

- GitNexus MCP context for `DataSourceFactory` failed with `Transport closed`
- GitNexus MCP impact for `get_data_source` failed with `Transport closed`
- GitNexus CLI fallback for `get_data_source` is ambiguous with `8` candidates and `UNKNOWN` risk
- CLI impact help exposes no `--file-path` or UID disambiguation option

## Route Evidence

| Item | Result |
|---|---|
| Active route module | `app.api.watchlist` |
| Registered routes | `15` |
| Affected route handlers | `8` |
| Route-body `DataSourceFactory()` constructions | `8` |
| Route-body `get_data_source("watchlist")` calls | `8` |
| Route-body adapter `get_data(...)` calls | `8` |
| Route/OpenAPI smoke | `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation ID warnings |

Affected route-body handler set:

| Handler | Factory line | `get_data_source` line | Adapter `get_data` line |
|---|---:|---:|---:|
| `get_my_watchlist` | 206 | 207 | 211 |
| `get_my_watchlist_symbols` | 244 | 245 | 249 |
| `add_to_watchlist` | 285 | 286 | 300 |
| `remove_from_watchlist` | 334 | 335 | 339 |
| `check_in_watchlist` | 365 | 366 | 370 |
| `update_watchlist_notes` | 400 | 401 | 405 |
| `get_watchlist_count` | 428 | 429 | 433 |
| `clear_watchlist` | 462 | 463 | 467 |

The remaining seven watchlist route handlers do not construct `DataSourceFactory()` in the route body.

## Ownership Boundary

The likely code target is:

`web/backend/app/services/data_source_factory/data_source_factory.py:DataSourceFactory.get_data_source`

This is inferred from the import in `watchlist.py`:

`from app.services.data_source_factory import DataSourceFactory`

The same symbol name exists in multiple places, including `src/factories/data_source_factory.py`, `strategy_mgmt.py`, `data_source_config.py`, `data_source_registry.py`, and `dashboard_data_source.py`. That ambiguity is why implementation is not authorized here.

## Boundary

G2.319 does not authorize:

- editing `web/backend/app/api/watchlist.py`
- editing `DataSourceFactory`
- adding route providers
- changing route paths, methods, response models, or generated OpenAPI artifacts
- editing tests, docs/api, frontend, config, scripts, OpenSpec, PM2, or runtime state

## Next Gate

Recommended next work item:

`G2.320 no-source watchlist DataSourceFactory impact-disambiguation / provider authorization preflight`

G2.320 should decide whether a future provider authorization package is safe. It must resolve or explicitly bound GitNexus ambiguity before any source implementation lane can exist.
