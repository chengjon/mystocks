# Backend Admin Audit PostgreSQL Session Provider Closeout

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Summary

- Node: `G2.296`
- Type: no-source closeout / residual refresh
- Prepared at: `2026-06-01T14:31:45+08:00`
- Base branch: `wip/root-dirty-20260403`
- Current HEAD: `48cf7e12637341451d8d77370306774df9c48729`
- Parent PR: `#448`, merged at `2026-06-01T06:26:56Z`
- Source edit authority: none

G2.296 records the G2.295 admin audit provider implementation as accepted and
closed. It also refreshes the remaining `get_postgresql_session` route-helper
family so the next node can decide the remaining core-database route-domain
surface without reopening the already closed admin audit lane.

## Scope Boundary

Allowed files are limited to steward-tree metadata, this report, the generated
evidence JSON, and the PR task card.

This package does not edit backend source, tests, route registration, generated
OpenAPI artifacts, `docs/api`, frontend, config, scripts, OpenSpec files, PM2, or
runtime state.

## Parent Closeout

PR `#448` merged G2.295 at commit
`48cf7e12637341451d8d77370306774df9c48729`.

G2.295 added `get_admin_audit_postgresql_session_factory`, moved the three
admin audit route handlers to explicit `Depends(...)` provider wiring, and kept
the original `session.close()` cleanup semantics in the helper body.

Current closeout scan records:

| Metric | Value |
|---|---:|
| Direct route-body `get_postgresql_session()` calls in admin audit | `0` |
| `Depends(get_admin_audit_postgresql_session_factory)` bindings | `3` |
| Admin audit route handlers with provider parameter | `3` |
| Compatibility/backing refs retained in `audit.py` | `3` |

The retained `audit.py` references are the import, provider return, and
`_load_audit_logs` default. They are compatibility/backing seams, not direct
route-body calls.

## Route / OpenAPI Snapshot

The import smoke was run with required backend environment values supplied only
to the subprocess environment. No secret values were written to the repository
or report artifacts.

| Metric | Value |
|---|---:|
| FastAPI routes | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |
| Audit runtime routes containing `audit` | `5` |

Audit runtime routes observed:

- `/api/tasks/audit/logs`
- `/api/tasks/cleanup/audit`
- `/api/v1/audit/logs`
- `/api/v1/audit/logs/{log_id}`
- `/api/v1/audit/statistics`

## Remaining `get_postgresql_session` Residuals

The admin audit `database_factory` provider lane is closed. The remaining
provider-shaped residuals are part of the `app.core.database.get_postgresql_session`
family and must not be treated as a continuation of the admin audit lane.

| File | References | Direct calls | Helper origin | Disposition |
|---|---:|---:|---|---|
| `web/backend/app/api/auth.py` | `8` | `4` | `app.core.database.get_postgresql_session` | Needs no-source route-domain decision |
| `web/backend/app/api/v1/admin/optimization.py` | `3` | `2` | `app.core.database.get_postgresql_session` | Needs no-source route-domain decision |
| `web/backend/app/api/market/market_data_request.py` | `2` | `1` | `app.core.database.get_postgresql_session` | Needs no-source route-domain decision |
| `web/backend/app/api/v1/admin/audit.py` | `3` | `0` | `app.core.database_factory.get_postgresql_session` | Closed; retained backing refs only |

Total `get_postgresql_session` references under `web/backend/app/api`: `16`.
Remaining active direct route/helper calls outside the closed admin audit lane:
`7`.

## GitNexus Evidence

GitNexus MCP remained unreliable in this session and returned `Transport closed`
for prior MCP calls. The CLI fallback was used for the next residual family:

```text
npx gitnexus impact -r mystocks --summary-only Function:web/backend/app/core/database.py:get_postgresql_session
```

Result summary:

- Risk: `CRITICAL`
- Direct dependants: `15`
- Processes affected: `54`
- Modules affected: `13`
- Index status: stale warning

This means G2.296 itself remains a no-source closeout package, but the selected
next residual family is high enough risk that the next PR must stop for human
review.

## Decision

G2.296 closes the admin audit provider lane.

It does not authorize any source implementation. It selects only:

`G2.297 no-source core database get_postgresql_session residual route-domain decision`

The next node must split the remaining core-database helper family by route
domain before any source authorization is considered.

## Freshness

This report becomes stale if:

- PR `#448` merge state or merge commit changes.
- Admin audit call sites change.
- Auth, admin optimization, or market request `get_postgresql_session` call sites change.
- Route/OpenAPI counts change from `548/500/0`.
- GitNexus risk for `app.core.database.get_postgresql_session` changes.

## Verification Commands

- PR state: `gh pr view 448 --json state,mergedAt,mergeCommit`
- Residual scan: Node.js file scan over `web/backend/app/api/**/*.py`
- Route/OpenAPI smoke: `app.main` import and `app.openapi()` path/operation scan
- GitNexus CLI fallback: `npx gitnexus impact -r mystocks --summary-only Function:web/backend/app/core/database.py:get_postgresql_session`
