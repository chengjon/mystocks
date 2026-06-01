# Backend Market Stock List PostgreSQL Session Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Historical document note**: This report records the state verified during the
> G2.299 implementation branch. Re-check current code, GitHub PR state, and the
> steward index before using it as execution authority.

Boundary note: this report records a bounded source implementation review
package. It does not merge PR `#452`, authorize auto-merge, or authorize work
outside the listed G2.299 source/test scope.

## Summary

G2.299 implements the G2.298-approved path-limited provider seam for the market
stock list route. It changes only:

- `web/backend/app/api/market/market_data_request.py`
- `web/backend/tests/test_market_stock_list_mock_configuration.py`
- G2.299 governance evidence, steward tree metadata, and the PR task card

The implementation adds route-local provider `get_market_stock_list_postgresql_session_factory`,
moves the real-branch direct `get_postgresql_session()` call behind a FastAPI
dependency, and preserves route path, method, query parameters, response shape,
OpenAPI exposure, and cleanup semantics.

This is a backend source/test implementation lane. PR `#452` must stop for
human review and must not be auto-merged.

## Parent Approval

| Item | Value |
|---|---|
| Parent package | G2.298 market stock list PostgreSQL session provider authorization |
| Parent PR | `#451` |
| Parent merge commit | `79a4fe5ae9f763e3e836b76c051bddbed270a930` |
| Parent merged at | `2026-06-01T08:38:01Z` |
| Authorized source file | `web/backend/app/api/market/market_data_request.py` |
| Authorized test file | `web/backend/tests/test_market_stock_list_mock_configuration.py` |

## Implementation

The route now has:

- provider: `get_market_stock_list_postgresql_session_factory`
- dependency binding: `session_factory: MarketStockListSessionFactory = Depends(...)`
- real branch direct helper calls after implementation: `0`
- provider binding count: `1`
- session cleanup: `session.close()` remains in a `finally` block

The shared helper definition remains unchanged:

- `web/backend/app/core/database.py` was not edited
- `web/backend/app/core/database_factory.py` was not edited

## TDD Evidence

RED run:

```text
env PYTHONPATH=web/backend pytest -q web/backend/tests/test_market_stock_list_mock_configuration.py --tb=short --no-cov -n 0
```

Result before implementation:

- `3 failed, 2 passed`
- expected failures:
  - `KeyError: 'session_factory'`
  - `TypeError: get_stock_list() got an unexpected keyword argument 'session_factory'`

GREEN run:

```text
env PYTHONPATH=web/backend pytest -q web/backend/tests/test_market_stock_list_mock_configuration.py --tb=short --no-cov -n 0
```

Result after implementation:

- `5 passed in 2.93s`

## Static Checks

```text
ruff check web/backend/app/api/market/market_data_request.py web/backend/tests/test_market_stock_list_mock_configuration.py
```

Result:

- `All checks passed`

## Route / OpenAPI Smoke

The runtime smoke imported `app.main` and generated `app.openapi()` with the
configured backend environment.

| Metric | Value |
|---|---:|
| FastAPI routes | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |
| Target route | `GET /api/v1/market/stocks` |

No generated OpenAPI artifact was edited.

## Residual Scan

| File | Direct `get_postgresql_session()` calls | Provider bindings |
|---|---:|---:|
| `web/backend/app/api/market/market_data_request.py` | `0` | `1` |
| `web/backend/app/api/auth.py` | `4` | `0` |
| `web/backend/app/api/v1/admin/optimization.py` | `2` | `0` |
| `web/backend/app/api/v1/admin/audit.py` | `0` | `3` |

G2.299 closes only the market stock list direct call. Auth and admin
optimization remain separate future route-domain tracks.

## GitNexus Evidence

GitNexus MCP impact failed again in this session:

```text
tool call failed: Transport closed
```

CLI fallback before editing:

| Target | Risk | Direct | Processes affected | Notes |
|---|---:|---:|---:|---|
| `Function:web/backend/app/api/market/market_data_request.py:get_stock_list` | `LOW` | `0` | `0` | stale-index warning |
| `Function:web/backend/app/core/database.py:get_postgresql_session` | `CRITICAL` | `15` | `54` | stale-index warning |

An index refresh attempt with `gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10`
exceeded five minutes and later aborted in a native worker path. This report
records the stale-index limitation rather than widening scope.

Staged verification fallback:

| Metric | Value |
|---|---:|
| Files | `11` |
| Changed symbols | `4` |
| Affected processes | `0` |
| Risk | `low` |
| Index status | `stale` |

## Boundary

G2.299 does not authorize:

- edits to `app.core.database.py` or `app.core.database_factory.py`
- auth or admin optimization migration
- route registration changes
- route path, method, response model, or OpenAPI artifact changes
- frontend, config, script, OpenSpec, PM2, or runtime state changes
- source retirement

## Decision

G2.299 is ready for PR `#452` review as a path-limited source implementation
package. If PR `#452` is accepted and merged, the next gate is:

```text
G2.300 no-source market stock list provider closeout / residual refresh
```
