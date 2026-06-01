# Backend Market Stock List PostgreSQL Session Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Summary

- Node: `G2.298`
- Type: no-source authorization package
- Prepared at: `2026-06-01T16:01:41+08:00`
- Base branch: `wip/root-dirty-20260403`
- Current HEAD: `555ff35e0c82e172b4312c59bc67d3674bd6f0ab`
- Parent PR: `#450`, merged at `2026-06-01T07:57:37Z`
- Source edit authority: none

G2.298 authorizes, for review only, a future path-limited implementation lane for
the market stock list `get_postgresql_session` call. It does not perform that
implementation.

## Scope Boundary

Allowed files are limited to steward-tree metadata, this report, generated
evidence, and the PR task card.

This package does not edit backend source, tests, route registration, generated
OpenAPI artifacts, `docs/api`, frontend, config, scripts, OpenSpec files, PM2,
or runtime state.

## Target Surface

| Field | Value |
|---|---|
| Route domain | `market-stock-list` |
| File | `web/backend/app/api/market/market_data_request.py` |
| Route | `GET /api/v1/market/stocks` |
| Handler | `get_stock_list` |
| Helper origin | `app.core.database.get_postgresql_session` |
| Direct calls | `1` |

Current call site:

- line `483`: `from app.core.database import get_postgresql_session`
- line `485`: `session = get_postgresql_session()`

The current handler closes the session on the success path after result mapping.
A future implementation should keep or strengthen cleanup semantics by using a
`finally` block or dependency finalizer.

## Route / OpenAPI Snapshot

The import smoke was run with required backend environment values supplied only
to the subprocess environment. No secret values were written to the repository
or report artifacts.

| Metric | Value |
|---|---:|
| FastAPI routes | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |
| Market stock list runtime routes | `1` |

Observed target route:

- `GET /api/v1/market/stocks` -> `get_stock_list`

## Existing Test Inventory

Focused existing test:

```text
env PYTHONPATH=web/backend pytest -q web/backend/tests/test_market_stock_list_mock_configuration.py --tb=short --no-cov -n 0
```

Result: `2 passed`.

Future G2.299 may extend only:

- `web/backend/tests/test_market_stock_list_mock_configuration.py`

Required future test shape:

- TDD red test proving the route handler accepts an injected session factory or
  provider dependency.
- Green test proving the real branch uses the injected session factory and
  closes the session.
- Mock branch must keep avoiding PostgreSQL session creation when
  `settings.use_mock_apis` is enabled.

## GitNexus Evidence

GitNexus MCP remained unreliable in this session and CLI fallback was used.

Current CLI samples:

| Symbol | Risk | Direct | Processes affected | Modules affected | Index |
|---|---:|---:|---:|---:|---|
| `Function:web/backend/app/core/database.py:get_postgresql_session` | `HIGH` | `15` | `0` | `0` | stale warning |
| `Function:web/backend/app/api/market/market_data_request.py:get_stock_list` | `LOW` | `0` | `0` | `0` | stale warning |

G2.297 recorded `CRITICAL` for the shared core helper. The current G2.298 sample
reports `HIGH` with stale-index warning. Treat this helper family as
HIGH/CRITICAL and keep any implementation path-limited.

## Future G2.299 Envelope

G2.298 authorizes only a future implementation package after PR `#451` human
acceptance.

Allowed future source path:

- `web/backend/app/api/market/market_data_request.py`

Allowed future test path:

- `web/backend/tests/test_market_stock_list_mock_configuration.py`

Forbidden future scope:

- `web/backend/app/core/database.py`
- `web/backend/app/core/database_factory.py`
- `web/backend/app/api/auth.py`
- `web/backend/app/api/v1/admin/optimization.py`
- `web/backend/app/api/v1/admin/audit.py`
- route registration changes
- route path, method, response model, or generated OpenAPI artifact changes
- `docs/api` artifacts
- frontend, config, scripts, OpenSpec, PM2, runtime state
- source retirement

Required implementation shape:

- Add a route-local provider/factory seam for the market stock list PostgreSQL
  session.
- Keep `app.core.database.get_postgresql_session` definition unchanged.
- Move only `get_stock_list`'s real-branch direct session creation behind the
  provider/factory.
- Preserve route path, method, query parameters, response shape, and OpenAPI
  exposure.
- Preserve mock branch behavior and keep it free of PostgreSQL session creation.
- Ensure session cleanup is equivalent or stronger than the current success-path
  close.

## Decision

Do not start source implementation from G2.298.

Selected next gate:

`G2.299 path-limited market stock list get_postgresql_session provider implementation`

PR `#451` must stop for human review because it authorizes future backend
source/test edits and the target sits under a HIGH/CRITICAL shared helper
family.

## Freshness

This report becomes stale if:

- PR `#450` merge state or merge commit changes.
- `market_data_request.py` `get_stock_list` call sites change.
- Auth or admin optimization `get_postgresql_session` call sites change.
- Route/OpenAPI counts change from `548/500/0`.
- GitNexus risk for the shared helper or target handler changes.
- Focused market stock list test inventory changes.

## Verification Commands

- PR state: `gh pr view 450 --json state,mergedAt,mergeCommit`
- Call-site scan: Node.js file scan over `web/backend/app/api/market/market_data_request.py`
- Route/OpenAPI smoke: `app.main` import and `app.openapi()` path/operation scan
- Focused test: `env PYTHONPATH=web/backend pytest -q web/backend/tests/test_market_stock_list_mock_configuration.py --tb=short --no-cov -n 0`
- GitNexus CLI fallback: `npx gitnexus impact -r mystocks --summary-only <symbol>`
