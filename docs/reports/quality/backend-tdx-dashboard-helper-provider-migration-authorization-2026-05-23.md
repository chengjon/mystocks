# Backend TDX Dashboard Helper Provider Migration Authorization - 2026-05-23

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Workline: G2.34 TDX dashboard helper provider migration authorization
- Status: review-ready
- Base HEAD: `78dafc38546ca9d45a1ed4bb3e5c2db24b9978b1`
- Parent PR: `#173`, merged at `78dafc38546ca9d45a1ed4bb3e5c2db24b9978b1`
- Parent issues: `#92`, `#79`
- Scope: decision and authorization only

Boundary note: this packet records a future implementation boundary only. It
does not authorize or perform backend source edits, test edits, route changes,
OpenAPI changes, frontend work, PM2/runtime work, OpenSpec changes, issue label
movement, or compatibility getter deletion.

## Governance Boundary

This packet executes the G2.33 next gate. It does not authorize:

- Backend source, test, route, OpenAPI, generated-client, frontend, PM2, or
  runtime changes in this PR
- OpenSpec change/spec creation, modification, validation archive, or issue
  publication
- GitHub issue label movement
- `get_tdx_service()` deletion or privatization
- A G2.35 implementation branch without human review of this packet

## Parent Evidence

G2.33 refreshed service lifecycle DI candidates after the G2.32 dashboard
helper provider migration and recorded:

- Service files scanned: `152`
- Candidate files: `20`
- `MarketDataServiceV2` direct route/helper calls: `0`
- `get_market_data_service_v2` GitNexus risk: LOW
- `get_tdx_service` GitNexus risk: CRITICAL
- Remaining TDX direct helper calls: `2`

This packet narrows that candidate into an implementation authorization
candidate, without editing source.

## Current Source Facts

`web/backend/app/services/tdx_service.py` currently exposes a module-level
singleton getter:

| Fact | Value |
|---|---:|
| `TdxService` class definitions | 1 |
| `_tdx_service_instance = None` definitions | 1 |
| `get_tdx_service()` definitions | 1 |

`web/backend/app/api/tdx.py` already uses FastAPI dependency wiring:

| Surface | Count |
|---|---:|
| `Depends(get_tdx_service)` in `tdx.py` | 5 |
| `/api/tdx` route edits authorized by this packet | 0 |

The residual seam is in `web/backend/app/api/dashboard_data_source.py`:

| Line | Function | Current direct call |
|---:|---|---|
| 238 | `_get_major_index_quotes` | `tdx_service = get_tdx_service()` |
| 490 | `_get_tdx_live_market_snapshot` | `tdx_service = get_tdx_service()` |

`prewarm_dashboard_market_overview_cache()` also calls both helper paths, so a
future implementation must explicitly preserve dashboard prewarm behavior.

## GitNexus Impact

Current-head GitNexus repo:
`g2-34-tdx-dashboard-helper-provider-authorization`, indexed at
`78dafc38546ca9d45a1ed4bb3e5c2db24b9978b1`.

| Target | Risk | Direct impact | Processes | Modules | Interpretation |
|---|---|---:|---:|---:|---|
| `get_tdx_service` | CRITICAL | 2 | 9 | 2 | Direct callers are the two dashboard helper functions |
| `_get_major_index_quotes` | CRITICAL | 2 | 9 | 2 | Reaches dashboard summary and market overview/prewarm flows |
| `_get_tdx_live_market_snapshot` | CRITICAL | 2 | 9 | 2 | Reaches dashboard summary and market overview/prewarm flows |
| `web/backend/app/services/tdx_service.py` | LOW | 3 | 0 | 0 | File import surface is limited, but getter-level dashboard impact is critical |

The key risk is not route registration; it is dashboard market overview and
prewarm behavior. That is why this packet authorizes only a future narrow
provider migration and keeps implementation in a separate PR.

## Authorization Decision

If this G2.34 packet is approved, the next implementation branch may migrate
the TDX dashboard helper seam to provider-fed service usage.

Allowed future source paths:

- `web/backend/app/services/tdx_service.py`
- `web/backend/app/api/dashboard_data_source.py`
- `web/backend/app/main.py`

`web/backend/app/main.py` is conditional: it may be touched only to pass an
installed/app-state `TdxService` into dashboard prewarm, matching the G2.32
prewarm pattern. It is not authorized for unrelated startup or route
registration changes.

Allowed future tests:

- `web/backend/tests/test_dashboard_data_source.py`
- `web/backend/tests/test_logging_noise_regressions.py`
- `web/backend/tests/test_health_route_conflicts.py`

Allowed future governance artifacts:

- `docs/reports/quality/backend-tdx-dashboard-helper-provider-migration-implementation-2026-05-23.md`
- a future `governance/mainline/task-cards/pr-<future>.yaml`
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`

## Explicit Non-Goals

- No edits to `web/backend/app/api/tdx.py`
- No route path, method, response model, OpenAPI exposure, or example change
- No frontend, generated client, PM2, Docker, config, or deployment change
- No OpenSpec change/spec creation or archive
- No `get_tdx_service()` deletion or privatization
- No broad market/data/strategy service consolidation
- No adapter or external TDX protocol refactor

## Required Future Implementation Behavior

A future G2.35 implementation branch, if approved, must:

1. Preserve public `get_tdx_service()` fallback compatibility.
2. Add a narrow app-state/provider/dependency seam for `TdxService`.
3. Make `RealBusinessDataSource` use injected/provider `TdxService` for
   `_get_major_index_quotes()` and `_get_tdx_live_market_snapshot()`.
4. Preserve dashboard summary, market overview, and prewarm behavior.
5. Leave `/api/tdx` route contracts unchanged.

The preferred implementation shape is analogous to the G2.32 dashboard helper
provider migration: accept an explicit service or provider, use the provider
internally, and keep the compatibility getter as fallback.

## Required Future Verification

Before a future implementation commit:

- Run GitNexus impact on `get_tdx_service`, `_get_major_index_quotes`,
  `_get_tdx_live_market_snapshot`, and any additional touched symbol.
- Warn and stop for review if the future impact expands beyond the authorized
  dashboard helper/prewarm scope.

Future TDD requirements:

- Add RED tests proving injected `TdxService` is used by
  `_get_major_index_quotes()`.
- Add RED tests proving injected `TdxService` is used by
  `_get_tdx_live_market_snapshot()`.
- Add or update prewarm coverage if `main.py` or
  `prewarm_dashboard_market_overview_cache()` is touched.
- Add a static guard that `dashboard_data_source.py` has zero direct
  `get_tdx_service()` calls after implementation.

Future GREEN verification should include:

- `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_dashboard_data_source.py -q --no-cov --tb=short`
- `ruff check` on touched backend files
- `black --check` on touched backend files
- `app.main` import smoke
- OpenAPI smoke with path count and duplicate operation ID count recorded
- staged `gitnexus_detect_changes(scope=staged)`
- `git diff --cached --check`

## Stop Rules

Stop and return to review if the future implementation needs any of:

- `web/backend/app/api/tdx.py`
- route path or response contract edits
- OpenAPI/schema exposure edits
- frontend or generated client edits
- PM2/runtime stateful gate execution
- adapter/protocol refactors outside the dashboard helper seam
- `get_tdx_service()` removal or privatization

## Next Gate

Human review of this G2.34 authorization packet. If accepted, create G2.35 as a
separate implementation branch. Do not edit source code from this packet.
