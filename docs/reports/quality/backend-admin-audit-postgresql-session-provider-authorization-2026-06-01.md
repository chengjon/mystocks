# Backend Admin Audit PostgreSQL Session Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review in future PR `#447`
- Prepared at: `2026-06-01T13:02:37+08:00`
- Base branch: `wip/root-dirty-20260403`
- Current HEAD checked: `a62d5e3fa4e9efbbe388e4bd317ae0cfae371319`
- Parent: G2.293 `get_postgresql_session` ownership / route-provider decision
- Parent PR: `#446`, merged at `a62d5e3fa4e9efbbe388e4bd317ae0cfae371319`

This is a no-source authorization package. It does not edit backend source,
tests, route contracts, docs/api artifacts, frontend, config, scripts,
OpenSpec, PM2, or runtime state.

Because it authorizes a future backend source implementation lane and the
selected helper participates in one affected execution process, PR `#447` must
stop for human review. It must not auto-merge.

## Target

G2.293 split the broader `get_postgresql_session` family by route domain and
helper origin. G2.294 selects only the bounded admin audit subgroup that imports
`get_postgresql_session` from `app.core.database_factory`.

| Item | Value |
|---|---|
| Target file | `web/backend/app/api/v1/admin/audit.py` |
| Helper origin | `app.core.database_factory.get_postgresql_session` |
| Direct helper occurrences | `2` |
| Effective exposed route surface | `3` |
| Candidate future lane | G2.295 path-limited admin audit provider implementation |

## Current Call Sites

| Function | Line | Route handler | Current cleanup semantics | Future handling |
|---|---:|---|---|---|
| `_load_audit_logs` | `225` | No, helper used by `list_audit_logs` and `get_audit_log` | `session.close()` in `finally` | Future provider lane must preserve equivalent cleanup lifecycle |
| `get_audit_statistics` | `365` | Yes | `session.close()` in `finally` | Future provider lane must preserve equivalent cleanup lifecycle |

The current source shape means the future implementation cannot be a blind
parameter rewrite. It must preserve the helper-function path used by
`list_audit_logs` and `get_audit_log`, not only the direct route handler
`get_audit_statistics`.

## Route / OpenAPI Smoke

Current smoke evidence:

```json
{
  "routes": 548,
  "paths": 500,
  "duplicate_operation_ids": 0,
  "audit_routes": [
    {
      "path": "/api/v1/audit/logs",
      "methods": ["GET"],
      "endpoint": "list_audit_logs",
      "include_in_schema": true
    },
    {
      "path": "/api/v1/audit/logs/{log_id}",
      "methods": ["GET"],
      "endpoint": "get_audit_log",
      "include_in_schema": true
    },
    {
      "path": "/api/v1/audit/statistics",
      "methods": ["GET"],
      "endpoint": "get_audit_statistics",
      "include_in_schema": true
    }
  ]
}
```

Any future implementation must keep these route paths, methods,
`include_in_schema` values, response models, and response contracts stable.

## GitNexus Evidence

GitNexus MCP impact failed with the known `Transport closed` tool issue. CLI
fallback was used.

| Target | Risk | Impacted | Direct | Processes affected | Modules affected | Index status |
|---|---|---:|---:|---:|---:|---|
| `Function:web/backend/app/core/database_factory.py:get_postgresql_session` | LOW | `4` | `2` | `1` | `1` | stale warning, `commits_behind=0` |

Affected process:

| Process | File | Earliest affected step |
|---|---|---:|
| `get_audit_statistics` | `web/backend/app/api/v1/admin/audit.py` | `1` |

Query fallback also matched the primary admin audit process
`proc_22_get_audit_statistics` and the symbols
`_load_audit_logs` / `get_audit_statistics` in
`web/backend/app/api/v1/admin/audit.py`.

## Authorization Decision

Decision: authorize only a future G2.295 path-limited source lane after human
acceptance of this no-source G2.294 package.

Allowed future source scope:

- `web/backend/app/api/v1/admin/audit.py`

Allowed future focused test scope:

- `web/backend/tests/test_v1_audit_regressions.py`
- `web/backend/tests/test_v1_admin_exports.py`

Required future implementation shape:

- Add or use a route-local provider dependency for the admin audit
  `database_factory` PostgreSQL session.
- Move only the admin audit helper uses behind dependency/provider wiring.
- Preserve existing `session.close()` cleanup semantics for both
  `_load_audit_logs` and `get_audit_statistics`.
- Keep route paths, methods, response models, OpenAPI exposure, and response
  contracts unchanged.
- Run focused audit regression/export tests and route/OpenAPI smoke before any
  implementation PR is reviewed.

Forbidden future scope:

- `web/backend/app/core/database.py`
- `web/backend/app/core/database_factory.py` helper definitions
- `web/backend/app/api/auth.py`
- `web/backend/app/api/v1/admin/optimization.py`
- `web/backend/app/api/market/market_data_request.py`
- route registration changes
- generated OpenAPI artifacts
- docs/api artifacts
- frontend/config/scripts/OpenSpec/PM2/runtime state

## Stop Rule

PR `#447` must stop for human review before merge.

Reason: G2.294 is no-source, but it authorizes future backend source work and
the selected helper participates in one affected execution process. The next
step must be an explicit human decision: either accept the G2.295
path-limited implementation lane or keep the subgroup deferred.

## Evidence

- `.planning/codebase/generated/admin-audit-postgresql-session-provider-authorization-2026-06-01.json`
- `.planning/codebase/steward-tree/steward-index.json`
- `.planning/codebase/steward-tree/current-next-gates.md`
- `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md`
- `.planning/codebase/steward-tree/branch-register.md`
- `.planning/codebase/steward-tree/evidence-index.md`
- `.planning/codebase/steward-tree/completed-ledger.md`
- `governance/mainline/task-cards/pr-447.yaml`

Freshness policy: stale if HEAD, PR state, route/OpenAPI counts, admin audit
call sites, focused test inventory, or GitNexus risk changes.
