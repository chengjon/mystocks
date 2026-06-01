# Backend Auth PostgreSQL Session Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report documents a path-limited source implementation
package. It does not authorize PR merge, future source expansion, route contract
changes, OpenAPI artifact edits, docs/api edits, PM2 commands, source retirement,
or edits outside the G2.307 scope.

Status: for review in future PR `#460`.

## Summary

G2.307 implements the path-limited auth PostgreSQL session provider lane
authorized by G2.306 after PR `#459` was accepted and merged at
`702816e7aa23378b2acd5dbc27de449fc74a3af5`.

This package changes only:

- `web/backend/app/api/auth.py`
- `web/backend/tests/test_auth_login_contract.py`
- G2.307 governance evidence and steward tree records

It does not edit `app.core.database.get_postgresql_session`, route registration,
route paths, response models, generated OpenAPI artifacts, docs/api artifacts,
frontend, config, scripts, OpenSpec, PM2, or runtime state.

## Implementation

| Item | Result |
|---|---|
| Route-local provider | `get_auth_postgresql_session_factory` |
| Provider backing calls | `1` `get_postgresql_session()` call inside the provider factory |
| Route-body direct calls | `0` direct `get_postgresql_session()` calls in the four target handlers |
| Dependency bindings | `4`: `get_users`, `register_user`, `request_password_reset`, `confirm_password_reset` |
| Cleanup lifecycle | Existing `session.close()` in `finally` remains preserved |
| Transaction semantics | `confirm_password_reset` commit/rollback behavior remains preserved |
| Compatibility exports | `verify_token` and `get_current_active_user` remain exported from `app.api.auth` |

## TDD Evidence

RED:

- Added `test_auth_db_handlers_use_route_local_session_factory_dependency`.
- It failed because `app.api.auth.get_auth_postgresql_session_factory` did not
  exist.
- RED result: `1 failed in 0.95s`.

GREEN:

- Added `get_auth_postgresql_session_factory` and injected it into the four
  affected handlers.
- Target result: `1 passed in 0.93s`.
- Focused regression: `11 passed, 18 skipped in 12.24s`.

## Verification

| Check | Result |
|---|---|
| Ruff | `ruff check --no-fix web/backend/app/api/auth.py web/backend/tests/test_auth.py web/backend/tests/test_auth_login_contract.py`: all checks passed |
| Provider scan | provider present, source direct `get_postgresql_session()` calls `1`, all four target handlers use `Depends(get_auth_postgresql_session_factory)` |
| Route/OpenAPI smoke | `routes=548`, `openapi_paths=500`, duplicate operation IDs `0` |
| Generated OpenAPI artifacts | Not edited |
| PM2/runtime state | Not touched |

The route/OpenAPI smoke used non-secret test-only environment values and did not
start PM2.

## GitNexus Evidence

GitNexus MCP impact returned `Transport closed` in this session. CLI fallback
was run before source edits.

| Target | Risk | Direct | Affected processes | Notes |
|---|---:|---:|---:|---|
| `Function:web/backend/app/core/database.py:get_postgresql_session` | CRITICAL | 15 | 54 | shared helper definition intentionally untouched |
| `get_users` | UNKNOWN | n/a | n/a | stale index warning |
| `register_user` | LOW | 0 | 0 | stale index warning |
| `request_password_reset` | LOW | 0 | 0 | stale index warning |
| `confirm_password_reset` | LOW | 0 | 0 | stale index warning |
| staged verification fallback | MEDIUM | 6 changed symbols | 5 | `npx gitnexus verify-staged -r mystocks`; index stale |

## Decision

G2.307 is implemented and ready for PR review. Because this package changes
backend source and tests under an auth/security-sensitive surface, limited
autopilot must stop at PR `#460` review. If PR `#460` is human accepted and
merged, the recommended next gate is G2.308 no-source auth provider closeout /
residual refresh.
