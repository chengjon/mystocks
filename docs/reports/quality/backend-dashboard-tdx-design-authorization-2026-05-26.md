# Backend Dashboard/TDX Design Authorization

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-26

Status: Ready for review

Scope: G2.156 governance decision and future-lane authorization only.

Base HEAD: `ee2fad4c41b0f4585bc39d9adb59c18326bbbd8e`

Parent: G2.155, PR `#308`, merged as `ee2fad4c41b0f4585bc39d9adb59c18326bbbd8e`.

Boundary: this is a design-authorization package only. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations. It does not perform implementation.

## Decision

Authorize a future G2.157 Dashboard/TDX current-head verification lane, with targeted source implementation only if current-head evidence still shows residual direct dashboard helper `get_tdx_service()` debt.

The default G2.157 outcome must be closeout-only if verification confirms the current source already has no residual direct dashboard helper getter calls.

## Why This Is Verification First

G2.155 selected Dashboard/TDX because refreshed GitNexus impact still reports the `get_tdx_service` graph path as CRITICAL and concentrated in dashboard helper flow:

| Symbol | Risk | Impacted | Direct callers | Processes |
|---|---:|---:|---:|---:|
| `get_tdx_service` | CRITICAL | 4 | 2 | 5 |
| `_get_major_index_quotes` | CRITICAL | 4 | 2 | 5 |
| `_get_tdx_live_market_snapshot` | CRITICAL | 4 | 2 | 5 |
| `prewarm_dashboard_market_overview_cache` | LOW | 0 | 0 | 0 |

The direct graph callers for `get_tdx_service` are:

- `_get_major_index_quotes`
- `_get_tdx_live_market_snapshot`

The next layer is:

- `_get_market_overview_data`
- `prewarm_dashboard_market_overview_cache`

However, historical G2.34-G2.38 evidence already moved the dashboard helper flow to a provider-backed shape. Current source confirms that nuance:

| Line | Current shape |
|---:|---|
| `dashboard_data_source.py:24` | imports `get_tdx_service` as fallback provider |
| `dashboard_data_source.py:62` | sets `self._tdx_service_provider = tdx_service_provider or get_tdx_service` |
| `dashboard_data_source.py:70` | defines private `_get_tdx_service()` provider helper |
| `dashboard_data_source.py:247` | `_get_major_index_quotes()` calls the private helper |
| `dashboard_data_source.py:499` | `_get_tdx_live_market_snapshot()` calls the private helper |

This means the remaining textual hits are not enough to justify blindly editing code. G2.157 must first classify whether the graph edge represents active direct debt or acceptable fallback compatibility.

## Consumer Contract Matrix

| Consumer | Surface | TDX dependency | Fallback requirement | Must preserve |
|---|---|---|---|---|
| `_get_major_index_quotes` | Dashboard market overview index quotes | Private `_get_tdx_service()` provider helper when cache is empty | Return cached data or empty list without raising when TDX is unavailable | Ranking index fallback, cache behavior, dashboard summary shape |
| `_get_tdx_live_market_snapshot` | Dashboard live market snapshot | Market service engine plus private `_get_tdx_service()` provider helper | Return `None` or cached snapshot without failing dashboard overview | Market service compatibility, cache behavior, summary endpoint tolerance |
| `prewarm_dashboard_market_overview_cache` | Startup/cache prewarm helper | `RealBusinessDataSource(..., tdx_service=...)` using selected app-state service | Return `False` on unavailable dependency without blocking startup | App-state installed service path, no startup hard failure, legacy fallback compatibility |
| `get_dashboard_summary` / `get_market_overview_data` | Public dashboard API flow | Indirect through `RealBusinessDataSource` helpers | Keep public response payload stable and avoid route/OpenAPI drift unless explicitly authorized | Public response contract, route path/method set, OpenAPI operation identity |

## G2.157 Authorization

G2.157 may start only after this G2.156 package is reviewed and accepted.

G2.157 is authorized to do one of two outcomes:

1. Close out without source edits if current HEAD confirms no residual direct dashboard helper `get_tdx_service()` calls beyond import/default-provider/private-helper fallback.
2. Apply a targeted dashboard helper source patch only if current HEAD still has residual direct getter debt and the patch remains inside the allowed file list.

Allowed source path if residual debt exists:

- `web/backend/app/api/dashboard_data_source.py`

Allowed focused test paths:

- `web/backend/tests/test_dashboard_data_source.py`
- `web/backend/tests/test_tdx_service_lifecycle_di.py`
- `web/backend/tests/test_health_route_conflicts.py`

Allowed governance paths:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/*dashboard*tdx*.json`
- `docs/reports/quality/*dashboard*tdx*.md`
- `governance/mainline/task-cards/pr-*.yaml`

## Required G2.157 Gates

Before any source edit, rerun and record:

- GitNexus impact for `get_tdx_service`
- GitNexus impact for `_get_major_index_quotes`
- GitNexus impact for `_get_tdx_live_market_snapshot`
- GitNexus impact for `prewarm_dashboard_market_overview_cache`
- Current-head static scan classifying every `get_tdx_service` textual hit in `dashboard_data_source.py`

If the proposed patch would touch anything outside `dashboard_data_source.py`, stop and return to review.

If the impact remains HIGH or CRITICAL and the proposed patch changes route/service/provider contracts, stop and return to review.

Focused verification for G2.157:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_dashboard_data_source.py -q --no-cov --tb=short
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_tdx_service_lifecycle_di.py -q --no-cov --tb=short
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov
```

Run a route/OpenAPI drift check only if route-level dependency contracts are touched. G2.157 should avoid route-level changes by default.

## Explicit Boundaries

G2.156 does not authorize source or test edits.

G2.157 must not edit without a new review:

- `web/backend/app/api/tdx.py`
- `web/backend/app/services/tdx_service.py`
- route paths or OpenAPI exposure
- `get_tdx_service()` deletion or privatization
- adapter internals
- frontend files
- PM2 workflows
- OpenSpec proposals or specs
- issue labels or GitHub issue state

Deferred tracks remain separate:

- Indicator/Data
- Strategy adapter
- Realtime streaming/socket
- root facade compatibility
- route dependency/provider governance

## Acceptance Checklist

- [x] Parent PR `#308` verified as merged.
- [x] OpenSpec context checked; this package creates no OpenSpec change.
- [x] GitNexus impact refreshed for the Dashboard/TDX seam.
- [x] Current dashboard source shape classified.
- [x] Consumer contract matrix recorded.
- [x] Future G2.157 source/test boundaries recorded.
- [x] No backend source, backend tests, frontend, OpenSpec, PM2, config, or script files changed in G2.156.

## Next Gate

Review this package. If accepted, start G2.157 as a verification-first lane. If current HEAD still has no residual direct dashboard helper getter debt, G2.157 should close out without source edits.
