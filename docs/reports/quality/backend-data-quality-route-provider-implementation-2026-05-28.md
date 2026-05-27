# Backend Data Quality Route Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation review candidate
- Prepared at: `2026-05-28T01:22:05+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `b899a173909d3818370dddbf35b039832266bd1d`
- Worktree branch: `g2-192-data-quality-route-provider-implementation`
- Scope: path-limited data-quality route provider implementation
- Source edit authority: G2.191 authorization only

Boundary note: this package implements only the G2.191-authorized route provider
surface. It does not authorize adapter constructor migration, legacy adapter
compatibility edits, singleton wrapper deletion, `DataQualityMonitor` internals,
frontend edits, `src` edits, `docs/api` edits, or OpenSpec change/spec edits.

## Parent State

| Item | State | Evidence |
|---|---|---|
| G2.191 data-quality route provider authorization | Merged | PR `#344`, merge commit `b899a173909d3818370dddbf35b039832266bd1d` |
| G2.192 data-quality route provider implementation | For review | This report plus `.planning/codebase/generated/data-quality-route-provider-implementation-2026-05-28.json` |

## Pre-Edit Risk Evidence

| Target | Risk | Summary |
|---|---|---|
| `web/backend/app/api/data_quality.py` | LOW | File-level GitNexus upstream impact: 0 impacted symbols, 0 affected processes |
| `get_data_quality_monitor` | CRITICAL | Cross-cutting context: 24 impacted symbols, 20 direct callers, 7 affected processes, 4 affected modules |

The CRITICAL getter result is acknowledged as shared context. G2.192 does not
modify the singleton helper or adapter consumers; it edits only the authorized
route file and focused tests.

## TDD Evidence

| Phase | Command | Result |
|---|---|---|
| Red | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_route_provider_regressions.py -q --tb=short --disable-warnings --no-cov` | `2 failed`: provider missing and route bodies still called singleton helpers |
| Green | same command | `2 passed` |

## Implementation Summary

G2.192 updates `web/backend/app/api/data_quality.py` by adding:

- `get_data_quality_monitor_provider`
- `_resolve_direct_call_dependency`
- FastAPI `Depends(get_data_quality_monitor_provider)` monitor parameters for
  the seven route handlers that use the monitor surface
- direct-call fallback handling so route unit tests can still call handlers
  without FastAPI dependency injection

Post-change route-body counts:

| Metric | Count |
|---|---:|
| `get_data_quality_monitor()` calls inside affected route bodies | 0 |
| `monitor_data_quality()` calls inside affected route bodies | 0 |
| `Depends(get_data_quality_monitor_provider)` route parameters | 7 |
| `_resolve_direct_call_dependency(...)` route fallbacks | 7 |

Affected route handlers:

- `get_data_quality_metrics`
- `get_active_alerts`
- `acknowledge_alert`
- `resolve_alert`
- `get_system_status_overview`
- `test_data_quality`
- `get_quality_trends`

## Preserved Behavior

G2.192 preserves:

- route paths
- HTTP methods
- response models
- OpenAPI examples
- error response contract
- data-source factory behavior
- `DataQualityMonitor` backing singleton behavior
- direct route test fallback behavior

## Verification

| Check | Result |
|---|---|
| `web/backend/tests/test_data_quality_route_provider_regressions.py` | Included in focused run |
| `web/backend/tests/test_data_quality_mock_configuration.py` | Included in focused run |
| `tests/unit/contract/test_data_quality_router_runtime_import.py` | Included in focused run |
| Focused pytest command | `7 passed` |
| Touched files `ruff check` | passed |
| OpenAPI smoke with approved dummy env | `openapi_paths=500`, `data_quality_paths=9`, `dependency_params_leaked=0` |
| GitNexus staged `detect_changes` | `risk_level=high`, `changed_files=12`, `changed_count=10`, `affected_count=13` |

The OpenAPI smoke used local dummy environment variables only for required
settings, with repository root and `web/backend` on `PYTHONPATH`. It did not
write `.env`, start PM2, or modify runtime configuration.

The GitNexus staged risk is recorded as `high` because the authorized
`data_quality.py` route handlers participate in indexed execution flows. The
staged path set remains within the G2.191 authorization: no adapter constructor,
legacy adapter, singleton wrapper, `DataQualityMonitor`, frontend, `src`,
`docs/api`, or OpenSpec paths are staged.

## Explicit Non-Goals

- No adapter constructor migration.
- No legacy adapter compatibility edits.
- No singleton wrapper deletion.
- No `DataQualityMonitor` implementation rewrite.
- No frontend edits.
- No `src` edits.
- No `docs/api` edits.
- No OpenSpec change/spec edits.

## Next Gate

If accepted, merge PR `#345` and start:

`G2.193 data-quality route provider closeout / remaining candidate refresh`

G2.193 should be governance-only and should decide the next remaining surface
without starting adapter constructor implementation directly.

## Evidence Artifacts

| Artifact | Role |
|---|---|
| `.planning/codebase/generated/data-quality-route-provider-authorization-2026-05-28.json` | G2.191 authorization evidence |
| `docs/reports/quality/backend-data-quality-route-provider-authorization-2026-05-28.md` | G2.191 authorization package |
| `.planning/codebase/generated/data-quality-route-provider-implementation-2026-05-28.json` | G2.192 machine-readable implementation evidence |
| `docs/reports/quality/backend-data-quality-route-provider-implementation-2026-05-28.md` | G2.192 implementation report |
| `governance/mainline/task-cards/pr-345.yaml` | G2.192 implementation PR scope card |
