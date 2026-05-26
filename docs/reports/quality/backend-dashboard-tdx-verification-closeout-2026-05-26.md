# Backend Dashboard/TDX Verification Closeout

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-26

Status: Ready for review

Scope: G2.157 current-head verification and closeout only.

Base HEAD: `e7cb84fae5e0c65cb400f467f6d9b55c3b2775d4`

Parent: G2.156, PR `#309`, merged as `e7cb84fae5e0c65cb400f467f6d9b55c3b2775d4`.

Boundary: this is a verification closeout package only. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations. It does not perform implementation.

## Decision

Close the Dashboard/TDX source lane without implementation.

Current HEAD has no residual direct dashboard helper `get_tdx_service()` debt. The remaining graph risk is real, but it represents active dashboard flow dependence on the TDX provider seam, not a pending direct-call cleanup that should be edited blindly.

## GitNexus Impact

| Symbol | Risk | Impacted | Direct callers | Processes |
|---|---:|---:|---:|---:|
| `get_tdx_service` | CRITICAL | 6 | 2 | 5 |
| `_get_major_index_quotes` | CRITICAL | 5 | 2 | 5 |
| `_get_tdx_live_market_snapshot` | CRITICAL | 5 | 2 | 5 |
| `prewarm_dashboard_market_overview_cache` | LOW | 0 | 0 | 0 |

For `get_tdx_service`, the direct graph callers remain:

- `_get_major_index_quotes`
- `_get_tdx_live_market_snapshot`

The next layers remain:

- `_get_market_overview_data`
- `prewarm_dashboard_market_overview_cache`
- `get_market_overview_data`
- `get_dashboard_summary`

This confirms the seam is still high-impact. It does not prove there is a remaining direct getter debt to patch.

## Current-Head Static Classification

File: `web/backend/app/api/dashboard_data_source.py`

| Line | Classification | Text |
|---:|---|---|
| 24 | import | `from app.services.tdx_service import TdxService, get_tdx_service` |
| 62 | constructor default provider | `self._tdx_service_provider = tdx_service_provider or get_tdx_service` |
| 70 | private provider helper definition | `def _get_tdx_service(self) -> TdxService:` |
| 247 | private provider helper call | `tdx_service = self._get_tdx_service()` |
| 499 | private provider helper call | `tdx_service = self._get_tdx_service()` |

Direct dashboard helper getter debt: `0`.

The current shape preserves fallback compatibility while routing dashboard helper access through `RealBusinessDataSource` provider state and the private `_get_tdx_service()` helper.

## Focused Verification

| Check | Result |
|---|---|
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_dashboard_data_source.py -q --no-cov --tb=short` | 11 passed in 5.40s |
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_tdx_service_lifecycle_di.py -q --no-cov --tb=short` | 4 passed in 1.33s |
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov` | 120 tests collected in 16.10s |

No route/OpenAPI drift check was required because G2.157 changed no route-level dependency contract and made no source edits.

## Closeout Result

G2.157 should not open a Dashboard/TDX implementation PR from this closeout.

Reasons:

- Current direct dashboard helper getter debt is `0`.
- Existing tests cover the dashboard data source and TDX lifecycle seam.
- The health route collection smoke confirms the relevant route test module remains import-safe.
- Any future edit to `get_tdx_service`, `/api/v1/tdx` route dependencies, or the public compatibility getter is a separate route dependency/provider governance problem, not a Dashboard/TDX helper cleanup problem.

## Remaining Queue

Return to the broader G2 high-risk service getter queue. Remaining tracks:

- Indicator/Data
- Strategy adapter
- root facade compatibility
- route dependency/provider governance

Do not reopen Dashboard/TDX source implementation unless a future current-head contradiction shows new residual direct dashboard helper getter debt.

## Acceptance Checklist

- [x] Parent PR `#309` verified as merged.
- [x] GitNexus impact refreshed for the Dashboard/TDX seam.
- [x] Current-head static classification shows direct dashboard helper getter debt is `0`.
- [x] Focused dashboard data source tests passed.
- [x] Focused TDX lifecycle tests passed.
- [x] Health route conflicts module collection passed.
- [x] No backend source, backend tests, frontend, OpenSpec, PM2, config, or script files changed in G2.157.

## Next Gate

Review this closeout. If accepted, select the next high-risk getter track from the remaining queue. Do not start another Dashboard/TDX source lane from this evidence.
