# Backend Core Database PostgreSQL Session Route-Domain Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Summary

- Node: `G2.297`
- Type: no-source ownership / route-domain decision
- Prepared at: `2026-06-01T15:00:25+08:00`
- Base branch: `wip/root-dirty-20260403`
- Current HEAD: `030545a24b4a8c9a4df36d2f126eb4597685e0c0`
- Parent PR: `#449`, merged at `2026-06-01T06:55:14Z`
- Source edit authority: none

G2.297 splits the remaining `app.core.database.get_postgresql_session`
route-helper residuals by route domain. It does not authorize implementation.

## Scope Boundary

Allowed files are limited to steward-tree metadata, this report, generated
evidence, and the PR task card.

This package does not edit backend source, tests, route registration, generated
OpenAPI artifacts, `docs/api`, frontend, config, scripts, OpenSpec files, PM2,
or runtime state.

## Current Runtime Snapshot

The import smoke was run with required backend environment values supplied only
to the subprocess environment. No secret values were written to the repository
or report artifacts.

| Metric | Value |
|---|---:|
| FastAPI routes | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |
| Remaining active direct calls outside admin audit | `7` |

The G2.295 admin audit lane remains closed:

- direct route-body `get_postgresql_session()` calls: `0`
- `Depends(get_admin_audit_postgresql_session_factory)` bindings: `3`

## Route-Domain Split

| Domain | File | Direct calls | Runtime routes | Decision |
|---|---|---:|---|---|
| Auth account/password | `web/backend/app/api/auth.py` | `4` | `GET /api/v1/auth/users`, `POST /api/v1/auth/register`, `POST /api/v1/auth/reset-password/request`, `POST /api/v1/auth/reset-password/confirm` | Defer to a dedicated auth/session-provider design |
| Admin optimization control-plane | `web/backend/app/api/v1/admin/optimization.py` | `2` | `POST /api/v1/optimization/vacuum`, `POST /api/v1/optimization/analyze`, `POST /api/v1/optimization/reindex`, `GET /api/v1/optimization/status` | Defer behind a smaller pilot because it runs operational maintenance SQL |
| Market stock list | `web/backend/app/api/market/market_data_request.py` | `1` | `GET /api/v1/market/stocks` | Select as the next no-source authorization candidate |

## GitNexus Evidence

GitNexus MCP remained unreliable in this session and returned `Transport closed`
in prior calls. The CLI fallback was used.

Shared helper impact:

```text
npx gitnexus impact -r mystocks --summary-only Function:web/backend/app/core/database.py:get_postgresql_session
```

Result summary:

- Risk: `CRITICAL`
- Direct dependants: `15`
- Processes affected: `54`
- Modules affected: `13`
- Index status: stale warning

Sampled route/helper functions were individually LOW risk with stale-index
warnings:

| Symbol | Risk | Direct | Processes affected |
|---|---:|---:|---:|
| `auth.py:get_users` | `LOW` | `0` | `0` |
| `auth.py:register_user` | `LOW` | `0` | `0` |
| `auth.py:request_password_reset` | `LOW` | `0` | `0` |
| `auth.py:confirm_password_reset` | `LOW` | `0` | `0` |
| `admin/optimization.py:_run_maintenance` | `LOW` | `3` | `0` |
| `admin/optimization.py:_database_status_payload` | `LOW` | `1` | `0` |
| `market_data_request.py:get_stock_list` | `LOW` | `0` | `0` |

The shared helper definition remains CRITICAL, so future work must stay
route-domain scoped and must not modify `app.core.database.get_postgresql_session`
itself.

## Decision

Do not start source implementation from G2.297.

Selected next gate:

`G2.298 no-source market stock list get_postgresql_session provider authorization`

Reason:

- It is the smallest remaining route-domain surface: one file, one route, one
  direct call.
- Auth contains account and password-reset semantics and needs its own design.
- Admin optimization is a control-plane maintenance surface and should follow
  only after a smaller route-domain authorization pattern is reviewed.

## Freshness

This report becomes stale if:

- PR `#449` merge state or merge commit changes.
- Auth, admin optimization, or market request `get_postgresql_session` call sites change.
- Route/OpenAPI counts change from `548/500/0`.
- GitNexus risk for `app.core.database.get_postgresql_session` changes.

## Verification Commands

- PR state: `gh pr view 449 --json state,mergedAt,mergeCommit`
- Residual scan: Node.js file scan over active target route files
- Route/OpenAPI smoke: `app.main` import and `app.openapi()` path/operation scan
- GitNexus CLI fallback: `npx gitnexus impact -r mystocks --summary-only <symbol>`
