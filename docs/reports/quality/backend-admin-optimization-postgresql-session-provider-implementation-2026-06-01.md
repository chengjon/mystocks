# Backend Admin Optimization PostgreSQL Session Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report documents a path-limited source implementation package.
It does not authorize PR merge, future source expansion, route contract changes,
OpenAPI artifact edits, PM2 commands, source retirement, or edits outside the
G2.303 scope.

Status: for review in future PR `#456`.

## Summary

G2.303 implements the path-limited admin optimization PostgreSQL session provider lane authorized by G2.302 after PR `#455` was accepted and merged at `4af141da7411d30b31b972ace51d104ae28606ed`.

This package changes only:

- `web/backend/app/api/v1/admin/optimization.py`
- `web/backend/tests/test_v1_optimization_regressions.py`
- G2.303 governance evidence and steward tree records

It does not edit `app.core.database.get_postgresql_session`, auth routes, market routes, admin audit routes, route registration, route paths, response models, generated OpenAPI artifacts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## Implementation

| Item | Result |
|---|---|
| Route-local provider | `get_admin_optimization_postgresql_session_factory` |
| Provider backing calls | `1` `get_postgresql_session()` call inside the provider factory |
| Helper/body direct calls | `0` direct `get_postgresql_session()` calls in `_run_maintenance` / `_database_status_payload` |
| Dependency bindings | `4`: `vacuum_database`, `analyze_database`, `reindex_database`, `get_database_status` |
| Excluded handler | `get_slow_queries` remains out of scope |
| Cleanup lifecycle | Existing `session.close()` in `finally` remains preserved in both helper paths |

## TDD Evidence

RED:

- `test_v1_optimization_handlers_use_postgresql_session_factory_dependency` failed because handler signatures had no `session_factory` dependency.
- `test_v1_optimization_postgresql_provider_returns_session_factory` failed because `get_admin_optimization_postgresql_session_factory` did not exist.
- RED result: `2 failed, 5 passed`.

GREEN:

- `env PYTHONPATH=web/backend ... pytest -q web/backend/tests/test_v1_optimization_regressions.py --tb=short --no-cov -n 0`
- Result: `7 passed in 1.78s`.

## Verification

| Check | Result |
|---|---|
| Ruff | `ruff check web/backend/app/api/v1/admin/optimization.py web/backend/tests/test_v1_optimization_regressions.py`: all checks passed |
| Residual scan | `depends_bindings=4`, `provider_backing_calls=1`, `helper_direct_get_postgresql_session_calls=0` |
| Route/OpenAPI smoke | `routes=548`, `openapi_paths=500`, duplicate operation IDs `0` |
| Target route surface | `/api/v1/optimization/vacuum`, `/analyze`, `/reindex`, `/status`, `/slow-queries` remain schema-visible |
| Generated OpenAPI artifacts | Not edited |

## GitNexus Evidence

GitNexus MCP impact calls returned `Transport closed` in this session. CLI fallback was run before source edits.

| Target | Risk | Direct | Affected processes | Notes |
|---|---:|---:|---:|---|
| `_run_maintenance` | LOW | 3 | 0 | stale index warning |
| `_database_status_payload` | LOW | 1 | 0 | stale index warning |
| `vacuum_database` | LOW | 0 | 0 | stale index warning |
| `analyze_database` | LOW | 0 | 0 | stale index warning |
| `reindex_database` | LOW | 0 | 0 | stale index warning |
| `get_database_status` | LOW | 0 | 0 | stale index warning |
| `Function:web/backend/app/core/database.py:get_postgresql_session` | CRITICAL | 15 | 54 | shared helper definition intentionally untouched |
| staged verification fallback | low | 18 changed symbols | 0 | `npx gitnexus verify-staged -r mystocks`; index stale |

## Decision

G2.303 is implemented and ready for PR review. Because this package changes backend source and tests under a CRITICAL shared helper family, limited autopilot must stop at PR `#456` review. If PR `#456` is human accepted and merged, the recommended next gate is G2.304 no-source admin optimization provider closeout / residual refresh.
