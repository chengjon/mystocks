# Backend Admin Optimization PostgreSQL Session Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a no-source ownership / provider-shape decision
package. It does not authorize backend source edits, route contract changes,
OpenAPI artifact edits, PM2 commands, source retirement, or PR merge.

## Status

- Status: review input for future PR `#454`
- G node: G2.301
- Prepared at: `2026-06-01T18:53:01+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `d407acdd207271274aeb6614afdedbf139f640ae`
- Package type: no-source ownership / provider-shape decision
- Source edit authority: none

## Summary

G2.301 classifies the remaining admin optimization
`app.core.database.get_postgresql_session()` usage after G2.300 closed the
market stock list provider lane. It does not authorize backend implementation.

Parent PR `#453` merged G2.300 at
`d407acdd207271274aeb6614afdedbf139f640ae` on
`2026-06-01T10:47:06Z`.

## Current Surface

| Item | Value |
|---|---:|
| Target file | `web/backend/app/api/v1/admin/optimization.py` |
| Helper origin | `app.core.database.get_postgresql_session` |
| Import line | `18` |
| Direct session calls | `2` |
| Direct call lines | `169`, `198` |
| OpenAPI-exposed route handlers in module | `5` |
| Route handlers that use the session helper path | `4` |
| Route handlers excluded from this helper path | `1` |

The two direct calls are not independent one-route call sites. They live in
module helpers:

| Helper | Direct call line | Called by | Decision note |
|---|---:|---|---|
| `_run_maintenance` | `169` | `vacuum_database`, `analyze_database`, `reindex_database` | Maintenance operation helper; provider shape must preserve cleanup semantics |
| `_database_status_payload` | `198` | `get_database_status` | Status payload helper; provider shape must preserve current status response behavior |

`get_slow_queries` is part of the same route module but does not call
`get_postgresql_session()`. It should not be bundled into a future provider
implementation unless a separate current-HEAD contradiction appears.

## Route / OpenAPI Surface

| Method | Path | Handler | Include in schema | Session helper path |
|---|---|---|---|---|
| POST | `/api/v1/optimization/vacuum` | `vacuum_database` | yes | `_run_maintenance` |
| POST | `/api/v1/optimization/analyze` | `analyze_database` | yes | `_run_maintenance` |
| POST | `/api/v1/optimization/reindex` | `reindex_database` | yes | `_run_maintenance` |
| GET | `/api/v1/optimization/status` | `get_database_status` | yes | `_database_status_payload` |
| GET | `/api/v1/optimization/slow-queries` | `get_slow_queries` | yes | none |

Route/OpenAPI smoke with runtime environment variables injected only into the
subprocess:

| Metric | Value |
|---|---:|
| FastAPI routes | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |
| Captured warning count | `119` |

No secret values are stored in this report or the generated JSON artifact.

## Verification

| Check | Result |
|---|---|
| `pytest -q web/backend/tests/test_v1_optimization_regressions.py --tb=short --no-cov -n 0` | `5 passed in 1.74s` |
| `ruff check web/backend/app/api/v1/admin/optimization.py web/backend/tests/test_v1_optimization_regressions.py` | `All checks passed` |

These checks verify the current route behavior only. They are not source
implementation authorization.

## GitNexus Evidence

GitNexus MCP impact calls returned `Transport closed` in this session. CLI
fallback was used.

| Target | Risk | Direct | Processes affected | Notes |
|---|---:|---:|---:|---|
| `admin/optimization.py:_run_maintenance` | `LOW` | `3` | `0` | stale-index warning |
| `admin/optimization.py:_database_status_payload` | `LOW` | `1` | `0` | stale-index warning |
| `Function:web/backend/app/core/database.py:get_postgresql_session` | `CRITICAL` | `15` | `54` | stale-index warning |

The helper-local impact is low, but the shared helper definition remains
CRITICAL. Future work must avoid editing `app.core.database.get_postgresql_session`
itself from this lane.

## Decision

Classify the admin optimization residual as a bounded control-plane route helper
surface inside the CRITICAL `app.core.database.get_postgresql_session` helper
family.

Do not edit source from G2.301. Do not edit the shared helper definition. Do not
change route paths, response models, OpenAPI exposure, docs/api artifacts,
frontend, config, scripts, PM2 state, or OpenSpec specs.

If PR `#454` is reviewed and accepted, the next gate should be:

G2.302 no-source admin optimization PostgreSQL session provider authorization
package.

Candidate provider shape for a future authorization package:

- Add a route-local provider such as
  `get_admin_optimization_postgresql_session_factory`.
- Return a session factory rather than a live session, so the existing helper
  cleanup pattern can remain local to `_run_maintenance` and
  `_database_status_payload`.
- Pass that factory into `vacuum_database`, `analyze_database`,
  `reindex_database`, and `get_database_status`.
- Preserve `get_slow_queries` as out of scope because it does not call the
  PostgreSQL session helper.
- Use `web/backend/tests/test_v1_optimization_regressions.py` as the focused
  regression surface.

This provider shape is a candidate only. It is not implementation authority.

## Remaining Residuals

| File | Direct calls | Current disposition |
|---|---:|---|
| `web/backend/app/api/auth.py` | `4` | deferred; security-sensitive account/password session semantics |
| `web/backend/app/api/v1/admin/optimization.py` | `2` | selected only for G2.302 no-source authorization after PR `#454` human acceptance |
| `web/backend/app/api/market/market_data_request.py` | `0` | closed by G2.299/G2.300 |
| `web/backend/app/api/v1/admin/audit.py` | `0` | closed by G2.295/G2.296 |

## Stop Rule

PR `#454` must stop for human review. Limited autopilot must not continue
directly into source implementation because the future source lane would sit
under a CRITICAL shared helper family and needs explicit authorization.

## Evidence

- `.planning/codebase/generated/admin-optimization-postgresql-session-ownership-decision-2026-06-01.json`
- `governance/mainline/task-cards/pr-454.yaml`
- `.planning/codebase/steward-tree/current-next-gates.md`
- `.planning/codebase/steward-tree/steward-index.json`
- `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md`
- `.planning/codebase/steward-tree/branch-register.md`
- `.planning/codebase/steward-tree/evidence-index.md`
- `.planning/codebase/steward-tree/completed-ledger.md`
