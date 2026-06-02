# Backend Watchlist DataSourceFactory Provider Preflight - 2026-06-02

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: `G2.320`
- Status: no-source provider authorization preflight
- Prepared at: `2026-06-02T09:19:03+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `033813cde66cffa55124f7434b3b0aeb45454e5d`
- Planned PR: `#473`

This report does not modify backend source, tests, route contracts, docs/api
artifacts, frontend code, config, scripts, OpenSpec files, PM2 state, or runtime
state. It records the bounded preflight needed before a future source
implementation lane can be reviewed.

## Parent State

G2.319 was accepted by PR `#472`, merged at
`033813cde66cffa55124f7434b3b0aeb45454e5d`. It classified
`web/backend/app/api/watchlist.py` as an active route-local DataSourceFactory
adapter seam:

- active watchlist routes: `15`
- affected route-body handlers: `8`
- route-body `DataSourceFactory()` constructions: `8`
- route-body `get_data_source("watchlist")` calls: `8`
- route-body adapter `get_data(...)` calls: `8`
- route/OpenAPI snapshot: `548` FastAPI routes, `500` OpenAPI paths,
  duplicate operation ID warnings `0`

G2.319 intentionally did not authorize source implementation because GitNexus
could not cleanly disambiguate the same-name `get_data_source` family.

## Current Surface

`watchlist.py` imports:

```python
from app.services.data_source_factory import DataSourceFactory
```

The likely backing method is
`web/backend/app/services/data_source_factory/data_source_factory.py:DataSourceFactory.get_data_source`.
The future implementation must not edit that shared factory package. The safe
shape is route-local provider wiring in `watchlist.py` only.

Affected handlers:

| Handler | Handler line | Factory line | `get_data_source` line | `get_data` line |
|---|---:|---:|---:|---:|
| `get_my_watchlist` | 198 | 206 | 207 | 211 |
| `get_my_watchlist_symbols` | 236 | 244 | 245 | 249 |
| `add_to_watchlist` | 274 | 285 | 286 | 300 |
| `remove_from_watchlist` | 325 | 334 | 335 | 339 |
| `check_in_watchlist` | 356 | 365 | 366 | 370 |
| `update_watchlist_notes` | 390 | 400 | 401 | 405 |
| `get_watchlist_count` | 422 | 428 | 429 | 433 |
| `clear_watchlist` | 456 | 462 | 463 | 467 |

The remaining seven watchlist handlers are out of scope unless a future source
lane produces specific current-HEAD evidence that they must be touched for
provider wiring consistency.

## GitNexus Boundary

MCP tool state:

- `mcp__gitnexus.context` for `DataSourceFactory`: `Transport closed`
- `mcp__gitnexus.impact` for `get_data_source`: `Transport closed`

CLI fallback:

- command: `npx gitnexus impact get_data_source -r mystocks --direction upstream --summary-only`
- status: ambiguous
- candidates: `8`
- risk: `UNKNOWN`

This ambiguity is bounded by not editing any shared `get_data_source` symbol or
DataSourceFactory implementation. Future source work may only change the route
consumer wiring in `watchlist.py`, after a fresh pre-edit impact/context check.

## Future G2.321 Authorization Shape

If PR `#473` is accepted, it authorizes only a future G2.321 source PR with
this scope:

Allowed paths:

- `web/backend/app/api/watchlist.py`
- `tests/api/file_tests/test_watchlist_api.py`

Forbidden paths:

- `web/backend/app/services/data_source_factory/**`
- `web/backend/app/api/data_source_config.py`
- `web/backend/app/api/data_source_registry.py`
- `web/backend/app/api/dashboard_data_source.py`
- `web/backend/app/api/strategy_mgmt.py`
- `src/factories/**`
- generated OpenAPI artifacts
- `docs/api/**`
- frontend, config, scripts, OpenSpec, PM2, runtime state

Required implementation properties:

- run pre-edit GitNexus impact/context for `watchlist.py` and affected route
  symbols; stop if risk becomes `HIGH` or `CRITICAL`
- add a route-local provider dependency for the watchlist DataSourceFactory or
  watchlist adapter factory
- move only the eight affected handlers away from route-body
  `DataSourceFactory()` construction and `get_data_source("watchlist")`
  acquisition
- preserve all route paths, methods, response models, and OpenAPI counts
- preserve the seven unaffected watchlist handlers
- retain DataSourceFactory and `DataSourceFactory.get_data_source` unchanged
- update focused tests for provider wiring and existing response/parser
  expectations
- run focused watchlist tests, ruff on touched files, route/OpenAPI smoke,
  GitNexus staged verification, and the mainline scope gate

The future G2.321 source PR must stop for human review before merge. Limited
autopilot must not merge it automatically.

## Decision

Classification:
`bounded-watchlist-route-provider-authorization-preflight`.

Recommendation:
authorize a future G2.321 path-limited source implementation PR only after PR
`#473` acceptance, and require human review before that source PR can merge.

Autopilot continuation: `false` after this node, because the next node is
source/test implementation.
