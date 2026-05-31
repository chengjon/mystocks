# Backend Governance Dashboard PostgreSQL Connection Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Gate: G2.285
- Status: no-source ownership / control-plane route-provider decision
- Prepared at: `2026-06-01T03:25:19+08:00`
- Base HEAD checked: `d34774837a0582f0e33d47425bb017b44e5aacd9`
- Parent: G2.284 accepted/merged by PR `#437`
- Parent merge commit: `d34774837a0582f0e33d47425bb017b44e5aacd9`
- Source edit authority: no
- Autopilot status: stop at PR review gate

Boundary note: G2.285 is a decision package only. It does not authorize backend
source edits, tests, route/OpenAPI contract changes, docs/api artifact edits,
frontend/config/script changes, OpenSpec changes, PM2 commands, or runtime state
changes.

## Surface

Target helper:

- Symbol: `get_postgres_connection`
- Current file: `web/backend/app/api/governance_dashboard.py`
- Definition line: `124`
- Router prefix: `/api/v1/governance`
- Classification: bounded active control-plane route helper

Current direct route-body call sites:

| Handler | Path | Call line | Manual close lines |
|---|---|---:|---|
| `get_quality_overview` | `/api/v1/governance/quality/overview` | 193 | 260, 276 |
| `get_lineage_stats` | `/api/v1/governance/lineage/stats` | 309 | 380, 397 |
| `get_assets_catalog` | `/api/v1/governance/assets/catalog` | 433 | 490, 507 |
| `get_compliance_metrics` | `/api/v1/governance/compliance/metrics` | 544 | 602, 620 |
| `get_dashboard_summary` | `/api/v1/governance/dashboard/summary` | 661 | 671 |

The helper opens a raw PostgreSQL connection for governance dashboard routes.
Current cleanup is manual inside handlers, with success and error branches for
the first four handlers and a single cleanup path in `get_dashboard_summary`.

## Route / OpenAPI Smoke

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

Known import-time warning noise remains limited to existing Pydantic/FastAPI
deprecation warnings and service initialization logs.

## GitNexus Evidence

GitNexus CLI fallback for
`Function:web/backend/app/api/governance_dashboard.py:get_postgres_connection`
reported:

- Risk: `MEDIUM`
- Impacted count: `6`
- Direct callers: `5`
- Affected processes: `0`
- Index status: stale warning

The stale index names one indexed caller as `fetch_all_data`. Current code truth
is `get_dashboard_summary`; this report uses current HEAD for route handler
names and paths.

## Decision

`get_postgres_connection` is owned by the `governance_dashboard` route module
for the current surface. It is not a shared service facade, not the app-wide
PostgreSQL provider, and not a route-registration issue.

Recommended next gate:

- G2.286 no-source `governance_dashboard.get_postgres_connection` provider
  authorization package

G2.286 may define a future path-limited implementation envelope, but it must
stay no-source until accepted. Any future implementation must preserve:

- the five route paths and response models
- OpenAPI exposure and operation IDs
- current manual cleanup semantics through an async dependency finalizer
- control-plane route ownership boundaries

## Stop Rule

PR for G2.285 must stop for human review because the selected target has
GitNexus MEDIUM impact. Limited autopilot must not auto-merge this decision PR
even though it is no-source.

## Evidence Artifacts

- `.planning/codebase/generated/governance-dashboard-postgres-connection-ownership-decision-2026-06-01.json`
- `docs/reports/quality/backend-governance-dashboard-postgres-connection-ownership-decision-2026-06-01.md`
- `governance/mainline/task-cards/pr-438.yaml`
