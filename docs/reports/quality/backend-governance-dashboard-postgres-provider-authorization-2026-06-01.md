# Backend Governance Dashboard PostgreSQL Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Gate: G2.286
- Status: no-source provider authorization package
- Prepared at: `2026-06-01T07:48:42+08:00`
- Base HEAD checked: `bdfdeb353f725f9e875ab50ee4e8ed22902a5818`
- Parent: G2.285 accepted/merged by PR `#438`
- Parent merge commit: `bdfdeb353f725f9e875ab50ee4e8ed22902a5818`
- Source edit authority: no
- Autopilot status: stop at PR review gate

Boundary note: G2.286 is an authorization package only. It does not edit
backend source, tests, route/OpenAPI contracts, docs/api artifacts, frontend,
config, scripts, OpenSpec, PM2, or runtime state.

## Authorization Decision

G2.286 authorizes a future, path-limited G2.287 implementation package for the
`governance_dashboard.get_postgres_connection` route-provider seam after human
review.

Future G2.287 may touch only these source paths:

- `web/backend/app/api/governance_dashboard.py`

Future G2.287 may touch only these focused test paths:

- `tests/api/file_tests/test_governance_dashboard_api.py`
- `web/backend/tests/test_governance_dashboard_postgres_provider.py`

The implementation shape is intentionally narrow:

- Add a route-local async generator provider in `governance_dashboard.py`.
- Move only the five current governance dashboard handlers to
  `Depends(provider)`.
- Move connection cleanup into the provider finalizer.
- Preserve route paths, `response_model` declarations, response metadata,
  OpenAPI exposure, and operation IDs.
- Preserve current `UnifiedResponse` behavior and error handling shape.

## Current Target

Target helper:

- Symbol: `get_postgres_connection`
- File: `web/backend/app/api/governance_dashboard.py`
- Definition line: `124`
- Classification: bounded active control-plane route helper
- Direct route-body calls: `5`
- Manual `conn.close()` cleanup lines: `9`

Current route handlers:

| Handler | Path | Call line | Manual close lines |
|---|---|---:|---|
| `get_quality_overview` | `/api/v1/governance/quality/overview` | 193 | 260, 276 |
| `get_lineage_stats` | `/api/v1/governance/lineage/stats` | 309 | 380, 397 |
| `get_assets_catalog` | `/api/v1/governance/assets/catalog` | 433 | 490, 507 |
| `get_compliance_metrics` | `/api/v1/governance/compliance/metrics` | 544 | 602, 620 |
| `get_dashboard_summary` | `/api/v1/governance/dashboard/summary` | 661 | 671 |

## Route / OpenAPI Evidence

Current app import and schema smoke with placeholder import-time environment
values completed successfully:

- FastAPI routes: `548`
- OpenAPI paths: `500`
- Duplicate operation IDs: `0`
- Governance paths present:
  - `/api/v1/governance/assets/catalog`
  - `/api/v1/governance/compliance/metrics`
  - `/api/v1/governance/dashboard/summary`
  - `/api/v1/governance/lineage/stats`
  - `/api/v1/governance/quality/overview`

Known import-time noise: mock backtest fallback logs and service initialization
logs. The route/OpenAPI smoke exited with status `0`.

## GitNexus Evidence

GitNexus CLI fallback for
`Function:web/backend/app/api/governance_dashboard.py:get_postgres_connection`
reported:

- Risk: `MEDIUM`
- Impacted count: `6`
- Direct callers: `5`
- Affected processes: `0`
- Index status: stale warning

The stale index names one caller as `fetch_all_data`. Current code truth is
`get_dashboard_summary`; this authorization uses current HEAD for the future
implementation target list.

## Future Required Verification

Future G2.287 must perform these checks before source edits:

- Rerun GitNexus context/impact for the target function.
- Stop before source edits if GitNexus returns HIGH or CRITICAL risk.
- Record current route/OpenAPI smoke before editing.

Future G2.287 must use TDD:

- First add a failing provider regression proving all five target handlers use
  `Depends(provider)`.
- Add a failing cleanup regression proving the provider finalizer closes the
  connection.
- Make those tests pass with the minimal route-local provider implementation.

Future G2.287 must verify:

- Focused governance dashboard provider test passes.
- `tests/api/file_tests/test_governance_dashboard_api.py` passes.
- `web/backend/tests/test_health_route_conflicts.py` passes.
- Ruff passes on touched files.
- Runtime route/OpenAPI smoke remains `548` routes, `500` paths, and duplicate
  operation IDs `0`.
- No provider dependency parameter leaks into OpenAPI.
- Mainline scope gate, OpenSpec strict validate, `git diff --check`, staged diff
  check, and GitNexus staged verification pass.

## Explicit Non-Goals

Future G2.287 must not perform:

- Shared PostgreSQL provider or infrastructure rewrite.
- App-wide database/session abstraction changes.
- Route registration changes.
- Route path, method, response model, or generated OpenAPI artifact changes.
- docs/api artifact edits.
- Frontend/config/script changes.
- OpenSpec proposal or spec edits.
- PM2 commands or runtime state changes.
- Source retirement or archive.

## Stop Rule

PR for G2.286 must stop for human review and must not auto-merge. It authorizes
future source work and the selected target has GitNexus MEDIUM impact.

## Evidence Artifacts

- `.planning/codebase/generated/governance-dashboard-postgres-provider-authorization-2026-06-01.json`
- `docs/reports/quality/backend-governance-dashboard-postgres-provider-authorization-2026-06-01.md`
- `governance/mainline/task-cards/pr-439.yaml`
