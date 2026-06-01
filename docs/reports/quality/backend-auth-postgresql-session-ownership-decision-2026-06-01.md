# Backend Auth PostgreSQL Session Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a no-source ownership / provider-shape decision
package. It does not authorize backend source edits, test edits, route contract
changes, OpenAPI artifact edits, PM2 commands, source retirement, or PR merge.

Status: for review in future PR `#458`.

## Summary

G2.305 classifies the remaining `web/backend/app/api/auth.py`
`get_postgresql_session()` residuals after PR `#457` closed the admin
optimization provider lane at `d8e52a3b0000426a9ce278c5dbc1c4bbd8c6b4f9`.

This package is no-source. It selects only a future no-source G2.306 provider
authorization package, not source implementation.

## Current Surface

| Function | Import line | Call line | Lifecycle note |
|---|---:|---:|---|
| `get_users` | `195` | `199` | `session.close()` in `finally` |
| `register_user` | `377` | `387` | `session.close()` in `finally` |
| `request_password_reset` | `503` | `509` | `session.close()` in `finally` |
| `confirm_password_reset` | `607` | `649` | `session.close()` in `finally`; includes commit/rollback semantics |

Auth-like route/OpenAPI smoke remains `548` runtime routes, `500` OpenAPI
paths, and duplicate operation IDs `0`.

## Verification

| Check | Result |
|---|---|
| Auth focused tests | `10 passed, 18 skipped in 19.13s` |
| Route/OpenAPI smoke | `548/500/0` |
| Ruff no-fix scan | `6` existing F401/F811 issues in `auth.py`; not fixed in this no-source package |
| GitNexus staged fallback | low risk, `9` files, `0` symbols, `0` affected processes; index stale |

The ruff findings were not fixed because G2.305 does not authorize source edits.

## Decision

Classify `auth.py get_postgresql_session` as a security-sensitive auth
route-domain surface inside the CRITICAL shared
`app.core.database.get_postgresql_session` helper family.

Future implementation shape, if separately authorized, should use a route-local
auth PostgreSQL session factory dependency passed into the four affected
handlers while preserving:

- current `session.close()` in `finally` cleanup semantics
- `confirm_password_reset` commit/rollback semantics
- route path, method, response model, and OpenAPI exposure

Recommended next gate after PR `#458` acceptance: G2.306 no-source auth.py
`get_postgresql_session` provider authorization.
