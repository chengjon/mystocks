# Backend Auth PostgreSQL Session Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a no-source authorization package. It does not
edit backend source, tests, route contracts, docs/api artifacts, frontend,
config, scripts, OpenSpec changes/specs, PM2, or runtime state.

Status: for review in future PR `#459`.

## Summary

G2.306 converts the accepted G2.305 auth ownership decision into a bounded
future implementation authorization. PR `#458` was merged at
`8a6cfa615f472f23643a13ab18ab02dd0853ad96`.

This package authorizes only a future G2.307 source lane after PR `#459`
acceptance. The future implementation PR must still stop for human review
before merge because it will modify `web/backend/app/api/auth.py`.

## Current Surface

| Function | Import line | Call line | Required lifecycle preservation |
|---|---:|---:|---|
| `get_users` | `195` | `199` | `session.close()` in `finally` |
| `register_user` | `377` | `387` | `session.close()` in `finally` |
| `request_password_reset` | `503` | `509` | `session.close()` in `finally` |
| `confirm_password_reset` | `607` | `649` | `session.close()` in `finally`; preserve commit/rollback semantics |

Current auth residual count remains `4` direct route-body calls to
`get_postgresql_session()`.

## Authorized Future Source Lane

G2.307 may only make a path-limited auth provider implementation with this
scope:

- `web/backend/app/api/auth.py`
- `web/backend/tests/test_auth.py`
- `web/backend/tests/test_auth_login_contract.py`

Required implementation shape:

- Add a route-local auth PostgreSQL session factory provider.
- Inject that provider into `get_users`, `register_user`,
  `request_password_reset`, and `confirm_password_reset`.
- Replace direct route-body `get_postgresql_session()` calls with the injected
  factory.
- Preserve all current `session.close()` in `finally` cleanup behavior.
- Preserve `confirm_password_reset` commit/rollback behavior.

Forbidden scope:

- Editing the `app.core.database.get_postgresql_session` definition.
- Changing login/logout/me/refresh/csrf handlers.
- Changing route path, method, response model, or OpenAPI exposure.
- Editing docs/api artifacts, frontend, config, scripts, OpenSpec specs/changes,
  PM2 state, or runtime deployment state.

## Verification

| Check | Result |
|---|---|
| Parent gate | PR `#458` is `MERGED` at `8a6cfa615f472f23643a13ab18ab02dd0853ad96` |
| Auth residual scan | `4` direct calls, `4` import lines |
| Focused auth tests | `10 passed, 18 skipped in 12.48s` |
| Route/OpenAPI smoke | `548` routes, `500` paths, duplicate operation IDs `0` |
| Ruff no-fix scan | `6` existing F401/F811 findings in `auth.py`; retained because G2.306 is no-source |
| GitNexus MCP | `Transport closed`; CLI impact fallback used |
| Shared helper impact | `Function:web/backend/app/core/database.py:get_postgresql_session` remains `CRITICAL`, `15` direct dependants, `54` affected processes |

The route/OpenAPI smoke used smoke-only non-secret environment values and did
not start PM2.

## Decision

Approve only a future path-limited G2.307 source implementation for the auth
PostgreSQL session provider. G2.306 itself remains no-source.

The future G2.307 implementation PR must stop at human review before merge,
even if all checks pass, because it will modify backend source and tests.
