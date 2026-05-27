# Backend Data Quality Route Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: review candidate
- Prepared at: `2026-05-28T01:04:38+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `7154ffbb067dcddc52d80f15342961b51234ac09`
- Worktree branch: `g2-191-data-quality-route-provider-authorization`
- Scope: data-quality route provider authorization package
- Source edit authority in this PR: none

Boundary note: this package authorizes a future route-only implementation lane
only if reviewed and accepted. It does not itself authorize backend source
edits, frontend edits, test edits, OpenSpec proposal creation, GitHub issue label
changes, adapter constructor migration, singleton wrapper deletion, or
data-quality source implementation inside G2.191.

## Parent State

| Item | State | Evidence |
|---|---|---|
| G2.190 data-quality / adapter cross-cutting decision | Merged | PR `#343`, merge commit `7154ffbb067dcddc52d80f15342961b51234ac09` |
| G2.191 data-quality route provider authorization | For review | This report plus `.planning/codebase/generated/data-quality-route-provider-authorization-2026-05-28.json` |

## Authorization Decision

If accepted, G2.191 authorizes a future `G2.192 data-quality route provider
implementation` lane. The future lane may only target the route surface in
`web/backend/app/api/data_quality.py` plus focused route/provider tests and
governance evidence.

G2.191 does not authorize source edits in this PR.

## Authorized Future Source Surface

| Surface | Future G2.192 authorization |
|---|---|
| `web/backend/app/api/data_quality.py` | Allowed |
| `web/backend/tests/test_data_quality_mock_configuration.py` | Allowed if needed for focused regression coverage |
| `web/backend/tests/test_data_quality_route_provider_regressions.py` | Allowed as a new focused regression test file |
| `tests/unit/contract/test_data_quality_router_runtime_import.py` | Allowed as a new focused import / route-registration contract test |
| `web/backend/app/services/_data_quality_monitor_singleton.py` | Forbidden |
| `web/backend/app/services/data_quality_monitor.py` | Forbidden |
| `web/backend/app/services/adapters_split/**` | Forbidden |
| `web/backend/app/services/adapters/**` | Forbidden |
| `web/backend/app/services/data_adapters/**` | Forbidden |
| `web/backend/app/services/market_data_adapter.py` | Forbidden |

## Route Inventory

At HEAD `7154ffbb067dcddc52d80f15342961b51234ac09`,
`web/backend/app/api/data_quality.py` has 9 route handlers. Seven touch the
data-quality monitor surface.

| Method | Path | Function | Getter calls | Monitor helper calls | Future G2.192 change allowed |
|---|---|---|---:|---:|---|
| `GET` | `/health` | `get_sources_health` | 0 | 0 | No |
| `GET` | `/metrics` | `get_data_quality_metrics` | 1 | 0 | Yes |
| `GET` | `/alerts` | `get_active_alerts` | 1 | 0 | Yes |
| `POST` | `/alerts/{alert_id}/acknowledge` | `acknowledge_alert` | 1 | 0 | Yes |
| `POST` | `/alerts/{alert_id}/resolve` | `resolve_alert` | 1 | 0 | Yes |
| `GET` | `/config/mode` | `get_data_source_mode` | 0 | 0 | No |
| `GET` | `/status/overview` | `get_system_status_overview` | 1 | 0 | Yes |
| `POST` | `/test/quality` | `test_data_quality` | 0 | 1 | Yes |
| `GET` | `/metrics/trends` | `get_quality_trends` | 1 | 0 | Yes |

The future implementation should preserve the current backing singleton
semantics. `get_data_quality_monitor` and `monitor_data_quality` remain retained
provider/backing helpers until route and adapter consumers are separately
migrated and current HEAD proves no runtime consumers remain.

## Required Future G2.192 Checks

The future G2.192 implementation lane must run these checks before merge:

- GitNexus impact/context before source edits, with explicit acknowledgement
  that the broader `get_data_quality_monitor` surface is `CRITICAL`.
- TDD red/green route-provider regression test.
- Focused data-quality route/provider regression tests.
- OpenAPI dependency leak smoke proving monitor/provider params do not appear in
  the schema.
- `app.main` import / data-quality route registration smoke with required
  environment available.
- `ruff check` for touched route and test files.
- GitNexus staged `detect_changes` before commit.
- Mainline scope gate for the implementation PR.

## Current Precondition Note

The clean G2.191 worktree has `.env.example` but no `.env`. A direct
`app.openapi()` smoke from this clean worktree is blocked by missing required
environment variables:

- `POSTGRESQL_HOST`
- `POSTGRESQL_USER`
- `POSTGRESQL_PASSWORD`
- `JWT_SECRET_KEY`
- `BACKEND_PORT`
- `BACKEND_BACKUP_PORT`

G2.192 should provide the required runtime environment or use an approved named
equivalent before treating OpenAPI or `app.main` smoke as valid evidence.

## Explicit Non-Goals

- Do not edit backend source from G2.191.
- Do not edit frontend source from G2.191.
- Do not edit tests from G2.191.
- Do not create or change OpenSpec proposals from G2.191.
- Do not change GitHub issue or PR labels from G2.191.
- Do not migrate adapter constructors from G2.191.
- Do not edit legacy adapter compatibility surfaces from G2.191.
- Do not delete `_data_quality_monitor_singleton.py`.
- Do not rewrite `DataQualityMonitor`.

## Next Gate

If G2.191 is accepted, start:

`G2.192 data-quality route provider implementation`

G2.192 should be a path-limited implementation lane and must not expand into
adapter constructors, legacy adapters, singleton wrapper deletion, or
`DataQualityMonitor` internals.

## Evidence Artifacts

| Artifact | Role |
|---|---|
| `.planning/codebase/generated/data-quality-adapter-cross-cutting-decision-2026-05-28.json` | G2.190 cross-cutting decision evidence |
| `docs/reports/quality/backend-data-quality-adapter-cross-cutting-decision-2026-05-28.md` | G2.190 human-readable decision package |
| `.planning/codebase/generated/data-quality-route-provider-authorization-2026-05-28.json` | G2.191 machine-readable authorization evidence |
| `docs/reports/quality/backend-data-quality-route-provider-authorization-2026-05-28.md` | G2.191 human-readable authorization package |
| `governance/mainline/task-cards/pr-344.yaml` | G2.191 governance-only PR scope card |
