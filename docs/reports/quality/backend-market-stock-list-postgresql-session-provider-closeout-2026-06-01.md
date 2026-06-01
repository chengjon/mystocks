# Backend Market Stock List PostgreSQL Session Provider Closeout

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a no-source closeout and residual-refresh package.
It does not authorize backend source edits, route contract changes, OpenAPI
artifact edits, PM2 commands, source retirement, or PR merge.

## Summary

G2.300 closes the market stock list PostgreSQL session provider lane after PR
`#452` was accepted and merged.

| Item | Value |
|---|---|
| Closed parent | G2.299 market stock list provider implementation |
| Parent PR | `#452` |
| Parent merge commit | `3d89c7e64a93c7f2ca074dc502762ad203f15bdc` |
| Parent merged at | `2026-06-01T10:16:28Z` |
| This package type | no-source closeout / residual refresh |

## Closeout Evidence

| Metric | Value |
|---|---:|
| Market stock list direct `get_postgresql_session()` calls | `0` |
| Market stock list provider bindings | `1` |
| Focused regression | `5 passed in 2.21s` |
| Ruff on touched source/test | `All checks passed` |
| FastAPI routes | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |

Target route remains:

```text
GET /api/v1/market/stocks
```

## Remaining Residuals

| File | Direct calls | Current disposition |
|---|---:|---|
| `web/backend/app/api/auth.py` | `4` | defer; auth account/password surface has security/session semantics |
| `web/backend/app/api/v1/admin/optimization.py` | `2` | select for G2.301 no-source ownership / provider-shape decision |
| `web/backend/app/api/market/market_data_request.py` | `0` | closed provider lane |
| `web/backend/app/api/v1/admin/audit.py` | `0` | closed provider lane |

The next selected target is **not** a direct authorization. In
`admin/optimization.py`, the remaining direct calls live in module helpers:

- `_run_maintenance`
- `_database_status_payload`

Because those helpers back multiple control-plane routes, G2.301 must first
decide ownership and implementation shape before any source lane is opened.

## GitNexus Evidence

GitNexus MCP impact failed in this session:

```text
tool call failed: Transport closed
```

CLI fallback:

| Target | Risk | Direct | Processes affected | Notes |
|---|---:|---:|---:|---|
| `admin/optimization.py:_run_maintenance` | `LOW` | `3` | `0` | stale-index warning |
| `admin/optimization.py:_database_status_payload` | `LOW` | `1` | `0` | stale-index warning |
| `app.core.database.get_postgresql_session` | `CRITICAL` | `15` | `54` | stale-index warning |

Staged verification fallback:

| Metric | Value |
|---|---:|
| Files | `9` |
| Changed symbols | `0` |
| Affected processes | `0` |
| Risk | `low` |
| Index status | `stale` |

## Decision

G2.300 closes the market stock list provider lane and selects:

```text
G2.301 no-source admin optimization get_postgresql_session ownership / provider-shape decision
```

PR `#453` must stop for human review because it selects the next target inside a
CRITICAL shared-helper family and because admin optimization requires a design
decision before authorization.
