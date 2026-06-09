# Backend Watchlist DataSourceFactory Provider Implementation - 2026-06-02

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: `G2.321`
- Status: accepted / merged source implementation
- Prepared at: `2026-06-02T23:50:34+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `40f36c573e41aa9ba1a4d07abe603b0080cf1181`
- PR: `#474`
- Merge commit: `2ebff6d7ded33403c691a60fc43f87dabf90a975`
- Merged at: `2026-06-02T16:23:25Z`

This source lane was authorized by G2.320 / PR `#473` and was accepted by
PR `#474` after human review. The source lane is now closed; G2.322 is the
no-source closeout / residual refresh.

## Scope

Allowed source/test files:

- `web/backend/app/api/watchlist.py`
- `tests/api/file_tests/test_watchlist_api.py`

Forbidden surfaces preserved:

- `web/backend/app/services/data_source_factory/**`
- other same-name `get_data_source` candidates
- route registration and route paths
- generated OpenAPI artifacts
- `docs/api/**`
- frontend, config, scripts, OpenSpec, PM2/runtime state

## Implementation

`watchlist.py` now has a route-local provider:

```python
async def get_watchlist_data_source() -> Any:
    data_source_factory = DataSourceFactory()
    return await data_source_factory.get_data_source("watchlist")
```

The eight authorized watchlist handlers now receive `watchlist_adapter` through
`Depends(get_watchlist_data_source)`:

- `get_my_watchlist`
- `get_my_watchlist_symbols`
- `add_to_watchlist`
- `remove_from_watchlist`
- `check_in_watchlist`
- `update_watchlist_notes`
- `get_watchlist_count`
- `clear_watchlist`

The shared DataSourceFactory package is unchanged. The route-local provider is
the only remaining backing location for `DataSourceFactory()` and
`get_data_source("watchlist")` in this module.

## TDD Evidence

RED:

- command: `pytest -o addopts= tests/api/file_tests/test_watchlist_api.py::test_watchlist_routes_use_datasource_factory_dependency_provider -q --no-cov`
- result: failed with `KeyError: 'get_watchlist_data_source'`

GREEN:

- command: `pytest -o addopts= tests/api/file_tests/test_watchlist_api.py::test_watchlist_routes_use_datasource_factory_dependency_provider -q --no-cov`
- result: `1 passed`

Focused file test:

- command: `pytest -o addopts= tests/api/file_tests/test_watchlist_api.py -q --no-cov`
- result: `22 passed`

## Verification

Ruff:

- command: `ruff check web/backend/app/api/watchlist.py tests/api/file_tests/test_watchlist_api.py`
- result: `All checks passed!`

Route/OpenAPI/provider smoke:

| Metric | Result |
|---|---:|
| FastAPI routes | 548 |
| OpenAPI paths | 500 |
| duplicate operation ID warnings | 0 |
| watchlist routes | 15 |
| provider `DataSourceFactory()` calls | 1 |
| provider `get_data_source(...)` calls | 1 |
| handler direct `DataSourceFactory()` calls | 0 |
| handler direct `get_data_source(...)` calls | 0 |
| `watchlist_adapter` dependency parameters | 8 |

The route/OpenAPI smoke used temporary placeholder environment variables only
to satisfy startup validation. No secrets were written to disk.

## GitNexus

MCP tools still failed with `Transport closed`.

CLI fallback before editing:

| Target | Risk | Direct callers | Affected processes |
|---|---:|---:|---:|
| `File:web/backend/app/api/watchlist.py` | LOW | 0 | 0 |
| `Method:web/backend/app/services/data_source_factory/data_source_factory.py:DataSourceFactory.get_data_source#1` | LOW | 3 | 0 |
| `Function:web/backend/app/api/watchlist.py:get_my_watchlist` | LOW | 0 | 0 |

The DataSourceFactory method was inspected for risk only; it was not edited.

## Stop Rule

G2.321 changed backend source and tests, and PR `#474` satisfied the human
review stop rule before merge. Do not use this accepted source lane to
authorize additional source changes. Future source candidates selected from the
G2.322 residual refresh still require a new no-source authorization package and
human review before merge.
