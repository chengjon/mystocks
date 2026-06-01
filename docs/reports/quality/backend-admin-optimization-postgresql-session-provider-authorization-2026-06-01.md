# Backend Admin Optimization PostgreSQL Session Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a no-source provider authorization package. It
does not authorize backend source edits from this PR, route contract changes,
OpenAPI artifact edits, PM2 commands, source retirement, or PR merge.

## Summary

G2.302 authorizes, for review only, a future path-limited implementation lane
for the admin optimization PostgreSQL session provider shape accepted by G2.301.

Parent PR `#454` merged G2.301 at
`13a81aec15fc8e98e7e4e927abe6d27e3e16f93d` on
`2026-06-01T11:23:17Z`.

This package remains no-source. Future implementation must wait for PR `#455`
human acceptance and must be delivered as a separate G2.303 source PR.

## Scope Boundary

Authorized future implementation scope for G2.303:

- `web/backend/app/api/v1/admin/optimization.py`
- `web/backend/tests/test_v1_optimization_regressions.py`
- G2.303 generated evidence, report, steward-tree updates, and task card

Forbidden future scope:

- `app.core.database.get_postgresql_session` implementation
- `web/backend/app/api/auth.py`
- `web/backend/app/api/market/market_data_request.py`
- `web/backend/app/api/v1/admin/audit.py`
- route path, method, `response_model`, or `include_in_schema` changes
- generated OpenAPI artifact edits
- `docs/api/**`
- `web/frontend/**`
- `src/**`
- `config/**`
- `scripts/**`
- `openspec/changes/**`
- `openspec/specs/**`
- PM2 or stateful runtime commands
- source retirement

## Target Surface

| Field | Value |
|---|---|
| Route domain | `admin-optimization` |
| File | `web/backend/app/api/v1/admin/optimization.py` |
| Helper origin | `app.core.database.get_postgresql_session` |
| Direct calls | `2` |
| Direct call lines | `169`, `198` |
| Cleanup lines | `177`, `217` |
| Target helpers | `_run_maintenance`, `_database_status_payload` |
| Target route handlers | `vacuum_database`, `analyze_database`, `reindex_database`, `get_database_status` |
| Excluded handler | `get_slow_queries` |

`get_slow_queries` remains out of scope because it does not call
`get_postgresql_session()`.

## Route / OpenAPI Snapshot

| Metric | Value |
|---|---:|
| FastAPI routes | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |
| Admin optimization runtime routes | `5` |
| Captured warning count | `119` |

Current route surface:

| Method | Path | Handler | Include in schema |
|---|---|---|---|
| POST | `/api/v1/optimization/vacuum` | `vacuum_database` | yes |
| POST | `/api/v1/optimization/analyze` | `analyze_database` | yes |
| POST | `/api/v1/optimization/reindex` | `reindex_database` | yes |
| GET | `/api/v1/optimization/status` | `get_database_status` | yes |
| GET | `/api/v1/optimization/slow-queries` | `get_slow_queries` | yes |

## Existing Test Inventory

Focused current-behavior regression:

`web/backend/tests/test_v1_optimization_regressions.py`

Current result:

`5 passed in 1.89s`

Future G2.303 implementation must expand or adjust this focused test as needed
to prove:

- four target handlers receive an explicit provider dependency or session
  factory argument
- direct route/helper body calls in `optimization.py` are reduced to `0`
- the provider backing call count is exactly `1`
- existing `session.close()` cleanup semantics remain equivalent
- `get_slow_queries` behavior remains unchanged

## GitNexus Evidence

GitNexus MCP impact calls returned `Transport closed`; CLI fallback was used.

| Symbol | Risk | Direct | Processes affected | Modules affected | Index |
|---|---:|---:|---:|---:|---|
| `Function:web/backend/app/api/v1/admin/optimization.py:_run_maintenance` | `LOW` | `3` | `0` | `0` | stale warning |
| `Function:web/backend/app/api/v1/admin/optimization.py:_database_status_payload` | `LOW` | `1` | `0` | `0` | stale warning |
| `Function:web/backend/app/core/database.py:get_postgresql_session` | `CRITICAL` | `15` | `54` | `12` | stale warning |

Future implementation must not edit the CRITICAL shared helper definition.

## Future G2.303 Envelope

G2.302 authorizes only a future implementation package after PR `#455` human
acceptance. The future implementation may:

- add `get_admin_optimization_postgresql_session_factory`
- use it as a route-local dependency returning a session factory
- pass the injected factory into `vacuum_database`, `analyze_database`,
  `reindex_database`, and `get_database_status`
- pass the factory into `_run_maintenance` and `_database_status_payload`
- preserve existing `session.close()` in `finally` cleanup semantics
- keep route paths, methods, response models, schema exposure, and response
  behavior stable

Expected future implementation closeout metrics:

| Metric | Expected value |
|---|---:|
| Direct route/helper body `get_postgresql_session()` calls in `optimization.py` | `0` |
| Provider backing calls | `1` |
| Affected handler dependency bindings | `4` |
| Target route/OpenAPI changes | `0` |

## Decision

Authorize only future G2.303 path-limited implementation for
`web/backend/app/api/v1/admin/optimization.py` and
`web/backend/tests/test_v1_optimization_regressions.py`, after PR `#455` human
acceptance.

Do not start source implementation from G2.302 itself. Do not edit shared helper
definitions, auth, market, admin audit, route contracts, OpenAPI artifacts,
docs/api, frontend, config, scripts, OpenSpec, PM2, or runtime state.

PR `#455` must stop for human review because this no-source package authorizes
future backend source/test edits under a CRITICAL shared helper family.

## Freshness

| Field | Value |
|---|---|
| Current HEAD checked | `13a81aec15fc8e98e7e4e927abe6d27e3e16f93d` |
| Stale if PR state changes | yes |
| Stale if route/OpenAPI count changes | yes |
| Stale if admin optimization call sites change | yes |
| Stale if auth session call sites change | yes |
| Stale if GitNexus risk changes | yes |
| Stale if focused tests change | yes |

## Verification Commands

- `pytest -q web/backend/tests/test_v1_optimization_regressions.py --tb=short --no-cov -n 0`
- `ruff check web/backend/app/api/v1/admin/optimization.py web/backend/tests/test_v1_optimization_regressions.py`
- route/OpenAPI smoke with temporary app configuration environment
- `openspec validate migrate-backend-singletons-to-lifecycle-di --strict`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json ...`
- `python governance/mainline/scripts/mainline_scope_gate.py --task-card governance/mainline/task-cards/pr-455.yaml --base-sha 13a81aec15fc8e98e7e4e927abe6d27e3e16f93d --head-sha HEAD --report /tmp/pr455-mainline-governance-report.json`
- `git diff --cached --check`
