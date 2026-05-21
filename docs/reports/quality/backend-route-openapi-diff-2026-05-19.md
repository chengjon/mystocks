# Backend Route / OpenAPI Diff

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: Task 6 runtime route/OpenAPI diff refreshed on `2026-05-21` after the `data_lineage` import blocker was fixed.

## Freshness

| Field | Value |
|---|---|
| `generated_at` | `2026-05-21` refresh |
| `git_head` | `f97f2eb57 fix(api): repair data lineage companion imports` |
| `current_head_checked_at_review` | `f97f2eb57` |
| `stale_if_head_mismatch` | Yes |
| `worktree_state` | dirty-worktree evidence; generated summary only |
| Summary artifact | `.planning/codebase/generated/backend-route-openapi-diff-2026-05-21.json` |
| Compared artifacts | `.planning/codebase/generated/backend-route-table-2026-05-20.json`; `.planning/codebase/generated/route-openapi-snapshot-2026-05-20.json` |

## Runtime Smoke

| Command | Result |
|---|---|
| `env PYTHONPATH=web/backend python -c "from app.main import app; print(len(app.routes))"` | Passed; `548` routes |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov` | Passed; `112 tests collected` |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov` | Passed; `112 passed` |

## Diff Summary

| Metric | Current `f97f2eb57` | Previous `7b097fffd` artifact | Delta |
|---|---:|---:|---:|
| Runtime routes | `548` | `548` | `0` |
| Runtime unique paths | `511` | `511` | `0` |
| Schema-visible routes | `536` | `536` | `0` |
| Hidden runtime routes | `12` | `12` | `0` |
| Endpoint modules | `98` | `98` | `0` |
| OpenAPI paths | `500` | `500` | `0` |
| OpenAPI operations | `536` | `536` | `0` |
| Component schemas | `294` | `294` | `0` |
| Duplicate operationIds | `0` | `0` | `0` |
| OpenAPI warning count | `0` | `0` | `0` |

Path-level comparison:

- Runtime route paths: `+0 / -0`
- OpenAPI schema paths: `+0 / -0`
- Added paths: none
- Removed paths: none

## Hidden Runtime Routes

The current app still has `12` hidden runtime routes. These are excluded from OpenAPI by `include_in_schema=False` or by being websocket/static/docs routes. They are not deletion candidates from this report alone.

| Path | Methods | Endpoint |
|---|---|---|
| `/openapi.json` | `GET` | `fastapi.applications.FastAPI.setup.<locals>.openapi` |
| `/swagger-ui-static` | route mount | static mount |
| `/static` | route mount | static mount |
| `/metrics` | `GET` | `app.main.prometheus_metrics` |
| `/api/docs` | `GET` | `app.main.custom_swagger_ui_html` |
| `/api/redoc` | `GET` | `app.main.custom_redoc_html` |
| `/api/ws/market` | websocket | `app.api.realtime_market.websocket_market` |
| `/api/ws/portfolio` | websocket | `app.api.realtime_market.websocket_portfolio` |
| `/ws/events` | websocket | `app.api.websocket.websocket_events` |
| `/api/strategy-mgmt/{path:path}` | `DELETE`, `GET`, `PATCH`, `POST`, `PUT` | `app.api._strategy_mgmt_compat.redirect_to_canonical` |
| `/api/notification/ws/notifications` | websocket | `app.api.notification.websocket_notifications` |
| `/api/v1/risk/v31/ws/risk-updates` | websocket | `app.api.risk.v31.websocket_risk_updates` |

## Duplicate Path / Method Finding

One runtime duplicate path/method pair remains when excluding `HEAD`:

| Path | Method | Runtime entries | Interpretation |
|---|---|---:|---|
| `/metrics` | `GET` | `2` | Hidden `app.main.prometheus_metrics` plus schema-visible `app.api.prometheus_exporter.metrics`; this is a control-plane taxonomy item, not an OpenAPI duplicate operationId. |

OpenAPI remains clean because only the exporter route is schema-visible.

## Closure Impact

- The `data_lineage` import blocker no longer prevents runtime route/OpenAPI evidence.
- The current route/OpenAPI surface is path-stable against the `2026-05-20` route/OpenAPI artifacts.
- This report does not authorize endpoint deletion, route rename, schema exposure changes, probe rewiring, PM2 workflow changes, or OpenSpec archiving.
- Any future decision about `/metrics` or `/api/strategy-mgmt/{path:path}` must remain in the control-plane / compatibility governance lane.
