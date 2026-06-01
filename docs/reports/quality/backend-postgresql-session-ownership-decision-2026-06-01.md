# Backend PostgreSQL Session Ownership / Route-Provider Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Gate: G2.293
- Status: for review in future PR `#446`
- Prepared at: `2026-06-01T12:19:25+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `05cdf04f646d844c11e90e7c453ed4f985c8d382`
- Parent gate: G2.292 provider closeout / residual refresh, PR `#445`, merged at `05cdf04f646d844c11e90e7c453ed4f985c8d382`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`

Boundary note: G2.293 is a no-source ownership / route-provider decision
package. It does not authorize backend source edits, test edits,
route/OpenAPI contract changes, docs/api artifact edits, frontend/config/script
changes, OpenSpec proposal/spec edits, PM2 commands, runtime state changes,
source retirement, or implementation authorization for `get_postgresql_session`.

## Finding

`get_postgresql_session` is not a single implementation target. It is a
cross-domain session helper family with two helper origins and mixed route
ownership:

- `app.core.database.get_postgresql_session`
- `app.core.database_factory.get_postgresql_session`

Current scan records `9` direct helper occurrences across `4` route files. The
effective OpenAPI route surface is `12` endpoints because some calls live inside
route-local helpers used by multiple endpoints.

## Call-Site Groups

| Group | File | Helper origin | Direct occurrences | Exposed routes | Decision |
|---|---|---|---:|---:|---|
| Auth core database | `web/backend/app/api/auth.py` | `app.core.database` | 4 | 4 | Security-sensitive; separate auth-specific decision required |
| Admin audit database factory | `web/backend/app/api/v1/admin/audit.py` | `app.core.database_factory` | 2 | 3 | Bounded LOW-impact subgroup; selected for next no-source authorization package |
| Admin optimization core database | `web/backend/app/api/v1/admin/optimization.py` | `app.core.database` | 2 | 4 | Database-operation maintenance group; separate decision required |
| Market stock list core database | `web/backend/app/api/market/market_data_request.py` | `app.core.database` | 1 | 1 | Business route group; separate decision required |

Representative exposed routes:

- `/api/v1/auth/users`
- `/api/v1/auth/register`
- `/api/v1/auth/reset-password/request`
- `/api/v1/auth/reset-password/confirm`
- `/api/v1/audit/logs`
- `/api/v1/audit/logs/{log_id}`
- `/api/v1/audit/statistics`
- `/api/v1/optimization/vacuum`
- `/api/v1/optimization/analyze`
- `/api/v1/optimization/reindex`
- `/api/v1/optimization/status`
- `/api/v1/market/stocks`

## Route / OpenAPI Smoke

Correct-worktree app import and OpenAPI smoke records:

- FastAPI routes: `548`
- OpenAPI paths: `500`
- duplicate operation IDs: `0`

The smoke emitted expected import-time service logs and the historical GPU
NumPy fallback warning; these did not affect route/OpenAPI counts.

## GitNexus Evidence

GitNexus MCP calls returned `Transport closed`; CLI fallback was used.

`Function:web/backend/app/core/database.py:get_postgresql_session`:

- risk: `CRITICAL`
- impacted symbols: `67`
- direct callers: `15`
- affected processes: `54`
- affected modules: `12`
- index status: stale warning

`Function:web/backend/app/core/database_factory.py:get_postgresql_session`:

- risk: `LOW`
- impacted symbols: `4`
- direct callers: `2`
- affected processes: `1`
- affected modules: `1`
- index status: stale warning

This confirms that a route-provider migration must not modify either shared
helper definition. Future source work, if authorized, must be route-local and
path-limited.

## Decision

G2.293 classifies `get_postgresql_session` as a cross-domain PostgreSQL session
helper family. It must be split by route domain and helper origin.

G2.293 does not authorize implementation.

Recommended next gate:

G2.294 no-source admin audit database_factory `get_postgresql_session`
provider authorization.

The admin audit subgroup is selected first because it is bounded to
`web/backend/app/api/v1/admin/audit.py`, has the LOW-impact
`database_factory.get_postgresql_session` origin, and exposes three audit
routes. It still requires a separate authorization package before any source
lane.

## Non-Goals

G2.293 does not authorize:

- editing `web/backend/app/core/database.py`
- editing `web/backend/app/core/database_factory.py`
- editing any route file
- changing route registration or OpenAPI exposure
- changing auth/session behavior
- changing admin optimization behavior
- changing market data request behavior
- retiring either helper
- combining auth, admin, and market migrations in one implementation PR

## Evidence

- `.planning/codebase/generated/postgresql-session-ownership-decision-2026-06-01.json`
- `docs/reports/quality/backend-postgresql-session-ownership-decision-2026-06-01.md`
- `governance/mainline/task-cards/pr-446.yaml`
