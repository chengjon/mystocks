# Backend Auth PostgreSQL Session Provider Closeout

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a no-source closeout / residual refresh package.
It does not edit backend source, tests, route contracts, docs/api artifacts,
frontend, config, scripts, OpenSpec changes/specs, PM2, or runtime state.

Status: for review in future PR `#461`.

## Summary

G2.308 closes out the auth PostgreSQL session provider implementation after PR
`#460` was merged at `833856a526c3083aa4c21a28d31b36ee2a82e9bd`.

This package is no-source. It records the implementation result, refreshes the
remaining `get_postgresql_session()` residuals, and selects only the next
no-source residual candidate refresh gate.

## Closeout Result

| Item | Result |
|---|---|
| Auth provider | `get_auth_postgresql_session_factory` |
| Route-body direct calls | `0` across `get_users`, `register_user`, `request_password_reset`, and `confirm_password_reset` |
| Provider backing calls | `1` |
| Dependency bindings | `4` |
| Cleanup lifecycle | `session.close()` in `finally` remains preserved |
| Transaction semantics | `confirm_password_reset` commit/rollback behavior remains preserved |
| Compatibility exports | `verify_token` and `get_current_active_user` remain available from `app.api.auth` |

## Residual Refresh

| File | Calls | Imports / mentions | Classification |
|---|---:|---:|---|
| `web/backend/app/api/auth.py` | `1` | `2` | closed provider backing call |
| `web/backend/app/api/v1/admin/optimization.py` | `1` | `2` | closed provider backing call |
| `web/backend/app/api/market/market_data_request.py` | `0` | `2` | import-only residual |
| `web/backend/app/api/v1/admin/audit.py` | `0` | `3` | import-only residual |

Tracked active route-body direct `get_postgresql_session()` residuals are now
`0` in the auth / admin optimization / market stock-list / admin audit route
domain set. Provider backing calls remain by design.

## Verification

| Check | Result |
|---|---|
| Parent PR | PR `#460` is `MERGED` at `833856a526c3083aa4c21a28d31b36ee2a82e9bd` |
| Focused auth tests | `11 passed, 18 skipped in 14.54s` |
| Ruff | `ruff check --no-fix web/backend/app/api/auth.py web/backend/tests/test_auth.py web/backend/tests/test_auth_login_contract.py`: all checks passed |
| Route/OpenAPI smoke | `548` routes, `500` paths, duplicate operation IDs `0` |
| Generated OpenAPI artifacts | Not edited |
| PM2/runtime state | Not touched |

The route/OpenAPI smoke used non-secret test-only environment values and did not
start PM2.

## Decision

Close the auth PostgreSQL session provider lane. G2.308 must not be used as
source implementation authority.

Recommended next gate after PR `#461` acceptance: G2.309 no-source service
lifecycle residual candidate refresh after auth provider closeout.
