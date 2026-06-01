# Backend Admin Optimization PostgreSQL Session Provider Closeout

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a no-source closeout / residual refresh package.
It does not authorize backend source edits, test edits, route contract changes,
OpenAPI artifact edits, PM2 commands, source retirement, or PR merge.

Status: for review in future PR `#457`.

## Summary

G2.304 closes the admin optimization PostgreSQL session provider lane after PR
`#456` was accepted and merged at
`1cc89b285cd265bce96991b8dc4c7e8bd71d85d0`.

This package is no-source. It records closeout evidence and refreshes the
remaining `get_postgresql_session` residual queue only.

## Closeout Evidence

| Item | Result |
|---|---|
| Admin optimization direct helper-body calls | `0` |
| Provider backing calls | `1` |
| `Depends(get_admin_optimization_postgresql_session_factory)` bindings | `4` |
| Focused regression | `7 passed in 2.36s` |
| Ruff | all checks passed |
| Route/OpenAPI smoke | `548` routes, `500` paths, duplicate operation IDs `0` |
| Target route surface | five `/api/v1/optimization/*` paths remain schema-visible |

The admin optimization provider lane is closed. `get_slow_queries` remains out
of scope and unchanged.

## Residual Queue

Current active direct `get_postgresql_session()` residuals in `web/backend/app/api`
after G2.304:

| Surface | Direct calls | Notes |
|---|---:|---|
| `web/backend/app/api/auth.py` | `4` | active residual queue |
| `web/backend/app/api/market/market_data_request.py` | `0` | provider lane closed by G2.299/G2.300 |
| `web/backend/app/api/v1/admin/audit.py` | `0` | provider lane closed by G2.295/G2.296 |
| `web/backend/app/api/v1/admin/optimization.py` helper bodies | `0` | closed by G2.303/G2.304 |
| `web/backend/app/api/v1/admin/optimization.py` provider backing | `1` | retained route-local provider backing seam |

The remaining auth surface is:

| Function | Import line | Call line |
|---|---:|---:|
| `get_users` | `195` | `199` |
| `register_user` | `377` | `387` |
| `request_password_reset` | `503` | `509` |
| `confirm_password_reset` | `607` | `649` |

## GitNexus Evidence

This package does not edit source. CLI sampling was used to classify the next
residual target:

| Target | Risk | Direct | Affected processes | Notes |
|---|---:|---:|---:|---|
| `get_users` | UNKNOWN | n/a | n/a | stale index warning |
| `register_user` | LOW | 0 | 0 | stale index warning |
| `request_password_reset` | LOW | 0 | 0 | stale index warning |
| `confirm_password_reset` | LOW | 0 | 0 | stale index warning |
| `Function:web/backend/app/core/database.py:get_postgresql_session` | CRITICAL | 15 | 54 | shared helper definition remains forbidden |
| staged verification fallback | low | 0 changed symbols | 0 | `npx gitnexus verify-staged -r mystocks`; index stale |

## Decision

G2.304 is a no-source closeout package. It closes admin optimization and selects
only G2.305 no-source `auth.py get_postgresql_session` ownership /
provider-shape decision as the next gate after PR `#457` acceptance.

Do not start auth source implementation from G2.304. The auth surface remains in
the CRITICAL shared helper family and must first go through a no-source
ownership / provider-shape decision.
