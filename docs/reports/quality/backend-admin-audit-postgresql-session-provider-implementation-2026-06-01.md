# Backend Admin Audit PostgreSQL Session Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review in future PR `#448`
- Prepared at: `2026-06-01T13:54:13+08:00`
- Base branch: `wip/root-dirty-20260403`
- Current HEAD checked: `a31fd3ede177d5851c2394b8cea2fe42188a4021`
- Parent: G2.294 admin audit `database_factory.get_postgresql_session` provider authorization
- Parent PR: `#447`, merged at `a31fd3ede177d5851c2394b8cea2fe42188a4021`

G2.295 is a path-limited source implementation. It must stop for human review
and must not auto-merge.

## Scope

Allowed implementation scope from G2.294:

- `web/backend/app/api/v1/admin/audit.py`
- `web/backend/tests/test_v1_audit_regressions.py`
- `web/backend/tests/test_v1_admin_exports.py`

Actual changed source/test scope:

- `web/backend/app/api/v1/admin/audit.py`
- `web/backend/tests/test_v1_audit_regressions.py`

Forbidden scope remained untouched:

- `web/backend/app/core/database.py`
- `web/backend/app/core/database_factory.py` helper definitions
- `web/backend/app/api/auth.py`
- `web/backend/app/api/v1/admin/optimization.py`
- `web/backend/app/api/market/market_data_request.py`
- route registration, generated OpenAPI artifacts, docs/api artifacts,
  frontend, config, scripts, OpenSpec, PM2, and runtime state

## Implementation

The implementation adds an explicit admin audit provider seam while preserving
the existing runtime fallback behavior:

- Added `get_admin_audit_postgresql_session_factory`.
- Added `session_factory: AuditSessionFactory = Depends(...)` to
  `list_audit_logs`, `get_audit_log`, and `get_audit_statistics`.
- Changed `_load_audit_logs` and `get_audit_statistics` to call the injected
  `session_factory`.
- Preserved existing `session.close()` cleanup in `finally` blocks.
- Kept route paths, response models, OpenAPI exposure, and response contracts
  unchanged.

This uses a session factory dependency instead of eagerly creating a session in
the dependency. That preserves the existing behavior where database errors fall
back to runtime audit logs/statistics inside the route/helper body.

## Residual Scan

| Metric | Count / state |
|---|---:|
| Direct route-body `get_postgresql_session()` calls after | `0` |
| `Depends(get_admin_audit_postgresql_session_factory)` bindings | `3` |
| Provider/backing `get_postgresql_session` references | `2` |
| Compatibility default reference in `_load_audit_logs` | `1` |
| `session.close()` finally blocks after | `2` |

The remaining `get_postgresql_session` references are backing compatibility
seams, not direct route-body calls.

## TDD Evidence

RED:

```text
env PYTHONPATH=web/backend pytest -q web/backend/tests/test_v1_audit_regressions.py::test_v1_audit_routes_expose_session_factory_dependency web/backend/tests/test_v1_audit_regressions.py::test_v1_audit_load_logs_uses_injected_session_factory_and_closes_session --tb=short --no-cov -n 0
2 failed
KeyError: 'session_factory'
TypeError: _load_audit_logs() got an unexpected keyword argument 'session_factory'
```

GREEN:

```text
env PYTHONPATH=web/backend pytest -q web/backend/tests/test_v1_audit_regressions.py::test_v1_audit_routes_expose_session_factory_dependency web/backend/tests/test_v1_audit_regressions.py::test_v1_audit_load_logs_uses_injected_session_factory_and_closes_session --tb=short --no-cov -n 0
2 passed in 1.74s
```

Focused regression:

```text
env PYTHONPATH=web/backend pytest -q web/backend/tests/test_v1_audit_regressions.py web/backend/tests/test_v1_admin_exports.py --tb=short --no-cov -n 0
6 passed in 1.86s
```

## Quality Evidence

Ruff:

```text
ruff check web/backend/app/api/v1/admin/audit.py web/backend/tests/test_v1_audit_regressions.py web/backend/tests/test_v1_admin_exports.py
All checks passed!
```

Route/OpenAPI smoke:

```json
{
  "routes": 548,
  "paths": 500,
  "duplicate_operation_ids": 0,
  "audit_routes": [
    "/api/v1/audit/logs",
    "/api/v1/audit/logs/{log_id}",
    "/api/v1/audit/statistics"
  ],
  "warnings": 119
}
```

The warning count comes from app import/OpenAPI generation and is not new route
shape drift evidence.

## GitNexus Evidence

GitNexus MCP impact failed with the known `Transport closed` tool issue. CLI
fallback was used before editing.

| Target | Risk | Impacted | Direct | Processes affected | Modules affected | Index status |
|---|---|---:|---:|---:|---:|---|
| `_load_audit_logs` | LOW | `3` | `3` | `1` | `1` | stale warning, `commits_behind=0` |
| `get_audit_statistics` | LOW | `0` | `0` | `0` | `0` | stale warning, `commits_behind=0` |
| `database_factory.get_postgresql_session` | LOW | `4` | `2` | `1` | `1` | stale warning, `commits_behind=0` |

Staged verification fallback:

```text
npx gitnexus verify-staged -r mystocks
Changes: 11 files, 14 symbols
Affected processes: 1
Risk level: medium
Affected execution flows:
  Get_audit_statistics -> _is_dev_like_environment
```

## Stop Rule

PR `#448` must stop for human review before merge.

Reason: G2.295 changes backend source and focused tests. Single-symbol impact
checks are LOW, but staged verification reports MEDIUM risk with one affected
execution flow, so this PR is outside the limited no-source autopilot lane.

If PR `#448` is accepted, the next gate is G2.296 no-source admin audit
provider closeout / residual refresh.

## Evidence

- `.planning/codebase/generated/admin-audit-postgresql-session-provider-implementation-2026-06-01.json`
- `.planning/codebase/steward-tree/steward-index.json`
- `.planning/codebase/steward-tree/current-next-gates.md`
- `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md`
- `.planning/codebase/steward-tree/branch-register.md`
- `.planning/codebase/steward-tree/evidence-index.md`
- `.planning/codebase/steward-tree/completed-ledger.md`
- `governance/mainline/task-cards/pr-448.yaml`
