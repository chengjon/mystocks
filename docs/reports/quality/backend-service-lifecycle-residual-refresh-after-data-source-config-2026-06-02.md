# Backend Service Lifecycle Residual Refresh After Data Source Config

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: `G2.318`
- Scope: no-source service lifecycle residual candidate refresh
- Prepared at: `2026-06-02T08:55:44+08:00`
- Base branch: `origin/wip/root-dirty-20260403`
- Base HEAD checked: `b51afb8c3bfd371eaa6838877d8fb0df8fe11bbd`
- Planned PR: `#471`
- Parent PR: `#470`, merged at `b51afb8c3bfd371eaa6838877d8fb0df8fe11bbd`

## Parent Result

G2.317 retained `data_source_config.get_config_manager` as a high-risk backing seam:

- active data-source config routes already use `Depends(get_config_manager_dependency)`
- route-body direct `get_config_manager()` calls are `0`
- provider backing calls are `1`
- `Depends(get_config_manager_dependency)` bindings are `9`
- route/OpenAPI remains `548` routes / `500` paths / `0` duplicate operation ID warnings
- GitNexus CLI fallback reports `HIGH` risk, `9` direct callers, and `3` affected processes

G2.318 does not reopen that seam and does not authorize source edits.

## Residual Refresh

| Scan item | Result |
|---|---|
| Scan roots | `web/backend/app/api`, `web/backend/app/services` |
| Python files scanned | `371` |
| Active API modules | `96` |
| Getter definitions seen | `736` |
| Active route-body getter groups | `194` |
| Static filtered route-body getter groups | `215` |
| Route/OpenAPI smoke | `548` routes, `500` paths, duplicate operation IDs `0` |

Top refreshed candidate families:

| Candidate | Evidence | Handling |
|---|---|---|
| `web/backend/app/api/watchlist.py` DataSourceFactory route-body adapter seam | `15` registered routes, `8` route-body `DataSourceFactory()` constructions, `8` `get_data_source("watchlist")` calls, `8` adapter `get_data(...)` calls | Selected for G2.319 no-source ownership decision |
| `web/backend/app/api/technical_analysis.py` DataSourceFactory route-body adapter seam | `8` registered routes, `8` route-body `DataSourceFactory()` constructions, `8` `get_data_source("technical_analysis")` calls, `8` adapter `get_data(...)` calls | Keep in refreshed queue |
| `web/backend/app/api/announcement/routes.py` route-body data calls | `6` `get_announcements(...)` calls | Keep in refreshed queue |
| `web/backend/app/api/data_quality.py` source metrics calls | `5` `get_source_metrics(...)` calls | Keep in refreshed queue |

## Selected Next Gate

G2.318 selects:

`G2.319 no-source watchlist DataSourceFactory ownership / route-provider decision`

The selected watchlist surface is active and should be decided before implementation:

- active route module: `app.api.watchlist`
- registered route count: `15`
- repeated factory construction lines: `206`, `244`, `285`, `334`, `365`, `400`, `428`, `462`
- repeated `get_data_source("watchlist")` lines: `207`, `245`, `286`, `335`, `366`, `401`, `429`, `463`
- repeated adapter `get_data(...)` lines: `211`, `249`, `300`, `339`, `370`, `405`, `433`, `467`

GitNexus state for the selected candidate is not implementation-ready:

- MCP impact failed with `Transport closed`
- CLI fallback for `get_data_source` is ambiguous with `8` candidates and `UNKNOWN` risk
- G2.319 must disambiguate `DataSourceFactory.get_data_source` and route/provider ownership before any authorization package or source lane exists

## Boundary

G2.318 must not be used as source implementation authority. It does not authorize:

- editing `web/backend/app/api/watchlist.py`
- editing `DataSourceFactory`
- adding route providers
- changing route paths, methods, response models, or generated OpenAPI artifacts
- editing tests, docs/api, frontend, config, scripts, OpenSpec, PM2, or runtime state

## Next Gate

Recommended next work item:

`G2.319 no-source watchlist DataSourceFactory ownership / route-provider decision`

G2.319 should decide whether the watchlist surface is a route-local provider candidate, a broader data-source factory ownership issue, or a domain-service extraction candidate. It should remain no-source unless a later authorization package is accepted.
