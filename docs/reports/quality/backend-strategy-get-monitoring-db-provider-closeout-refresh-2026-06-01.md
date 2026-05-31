# Backend Strategy get_monitoring_db Provider Closeout Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Gate: `G2.279`
- Status: for review
- Prepared at: `2026-06-01T01:06:12+08:00`
- Base HEAD checked: `c5496cab0a4213f74636af1c48772dc96c90bd1b`
- Parent PR: `#431`
- Parent merge commit: `c5496cab0a4213f74636af1c48772dc96c90bd1b`
- Source edit authority: no

Boundary note: this report records closeout and next-gate evidence only. It does
not authorize backend source edits, route registration changes, generated
OpenAPI artifact edits, frontend/config/script edits, OpenSpec changes, PM2
commands, or runtime state changes.

## Parent Closeout

PR `#431` merged G2.278 at
`c5496cab0a4213f74636af1c48772dc96c90bd1b`.

G2.278 implemented only the G2.277-authorized strategy surface:

- `web/backend/app/api/strategy_management/_helpers.py`
- `web/backend/app/api/strategy_management/_strategy_crud_router.py`
- focused strategy provider test coverage
- governance evidence and task-card updates

The G2.278 implementation moved the active strategy CRUD/lifecycle route
logging surface behind `Depends(get_strategy_monitoring_db)` while preserving
route paths, OpenAPI path count, response contracts, and handler behavior.

## Current Residual Scan

| Path | Direct `get_monitoring_db().log_operation(...)` calls | Provider depends params | Provider definitions | Notes |
|---|---:|---:|---:|---|
| `web/backend/app/api/strategy_management/_helpers.py` | 0 | 0 | 2 | Contains backing provider definitions and helper-level `monitoring_db.log_operation(...)` calls |
| `web/backend/app/api/strategy_management/_strategy_crud_router.py` | 0 | 6 | 0 | Active strategy handlers now receive `monitoring_db` through dependency parameters |
| `web/backend/app/api/risk/_shared.py` | 0 | 0 | 2 | Risk provider backing remains retained from G2.275 |
| `web/backend/app/api/risk/alerts.py` | 0 | 1 | 0 | Risk route-body direct calls remain closed |
| `web/backend/app/api/risk/metrics.py` | 0 | 2 | 0 | Risk route-body direct calls remain closed |
| `web/backend/app/utils/risk_utils.py` | 0 | 0 | 1 | Utility same-name helper remains deferred; no active API route-body log call in this scan |

Interpretation:

- Strategy direct route/helper target calls are closed at `0`.
- Strategy active handler dependency parameters are `6`.
- Risk direct route-body calls remain closed at `0`.
- `web/backend/app/utils/risk_utils.py` is not promoted into a source lane by
  this closeout; it remains a deferred utility same-name helper.
- Name occurrences from definitions or historical docstrings are not counted as
  active route-body calls.

## Runtime / OpenAPI Smoke

Runtime/OpenAPI smoke with placeholder import-time environment values recorded:

- FastAPI routes: `548`
- OpenAPI paths: `500`
- Duplicate operation IDs: `0`
- Target strategy/risk endpoints leaked `monitoring_db` request parameters: `false`

Checked target endpoints:

| Endpoint | Params | Request body | `monitoring_db` leak |
|---|---:|---|---|
| `GET /api/v1/strategy/strategies` | 4 | false | false |
| `POST /api/v1/strategy/strategies` | 0 | true | false |
| `POST /api/v1/strategy/{strategy_id}/start` | 1 | false | false |
| `POST /api/v1/strategy/{strategy_id}/pause` | 1 | false | false |
| `POST /api/v1/strategy/{strategy_id}/resume` | 1 | false | false |
| `POST /api/v1/strategy/{strategy_id}/stop` | 1 | false | false |
| `GET /api/v1/risk/alerts` | 1 | false | false |
| `POST /api/v1/risk/alerts` | 0 | true | false |
| `POST /api/v1/risk/var-cvar` | 0 | true | false |
| `POST /api/v1/risk/beta` | 0 | true | false |

## Focused Verification

| Check | Result |
|---|---|
| Focused strategy provider test | `1 passed, 1 warning in 2.62s` |
| Touched strategy ruff check | `All checks passed` |
| Runtime/OpenAPI smoke | `548` routes, `500` paths, duplicate operation IDs `0` |
| GitNexus staged verification | MCP `detect_changes` returned `Transport closed`; CLI fallback returned `ok=true`, `risk_level=low`, changed symbols `0`, affected processes `0`, with stale-index warning |

Focused provider test:

```bash
env PYTHONPATH=web/backend pytest -o addopts= tests/api/file_tests/test_strategy_management_api.py::TestStrategyManagementAPIFile::test_strategy_monitoring_db_uses_route_dependency_provider -q -n 0 --tb=short --no-cov
```

Ruff check:

```bash
ruff check web/backend/app/api/strategy_management/_helpers.py web/backend/app/api/strategy_management/_strategy_crud_router.py tests/api/file_tests/test_strategy_management_api.py
```

GitNexus staged verification:

```bash
npx gitnexus verify-staged -r mystocks --cwd /opt/claude/mystocks_spec/.worktrees/g2-279-strategy-get-monitoring-db-provider-closeout-refresh --json
```

The CLI fallback reported a stale index:

- indexed commit: `20cb37ace841beeb0079b191a8a564c03029b36a`
- current commit: `c5496cab0a4213f74636af1c48772dc96c90bd1b`
- stale reason: `current_commit_differs_from_indexed_commit`

Use this as scope-risk evidence only after noting the stale-index warning; refresh
the GitNexus index before relying on graph freshness.

## Decision

G2.279 records the strategy `get_monitoring_db` provider lane as closed for the
authorized target surface.

Accepted facts for review:

- PR `#431` is merged at
  `c5496cab0a4213f74636af1c48772dc96c90bd1b`.
- Strategy direct `get_monitoring_db().log_operation(...)` calls in the target
  files are `0`.
- Risk direct route-body `get_monitoring_db().log_operation(...)` calls remain
  `0`.
- Runtime/OpenAPI shape remains stable at `548` routes, `500` OpenAPI paths,
  and duplicate operation IDs `0`.

Recommended next gate after review acceptance:

`G2.280 no-source service lifecycle residual candidate refresh after get_monitoring_db closeout`

G2.280 should refresh the remaining service lifecycle queue before any new
authorization or source lane. It should not start backend source implementation
directly from this G2.279 closeout.

## Stale Policy

This report is stale if any of these change before review:

- current HEAD differs from
  `c5496cab0a4213f74636af1c48772dc96c90bd1b`
- PR `#431` merge state or merge commit changes
- runtime route count or OpenAPI path count changes
- target strategy/risk `get_monitoring_db` call-site scan changes
