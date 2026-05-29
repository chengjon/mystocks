# Backend Industry/Concept UnifiedDataService Cleanup Closeout / Refresh - 2026-05-29

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2: `G2.226`
- Status: closeout / residual refresh for review
- Prepared at: `2026-05-29T10:34:00+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `5837b8af55499e8ee9d7ba14cf543abb9bc45e39`
- Parent: G2.225 / PR `#378`, merged at `5837b8af55499e8ee9d7ba14cf543abb9bc45e39`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`
- Source edit authority: no

Boundary note: this closeout records the G2.225 result, refreshes residuals, and
selects a future no-source decision gate. It does not edit backend source, tests,
route contracts, OpenAPI specs, frontend code, runtime configuration, PM2 state,
or OpenSpec specs.

## G2.225 Closeout

| Check | Result |
|---|---:|
| Direct `UnifiedDataService()` calls in `web/backend/app/api/industry_concept_analysis.py` | 0 |
| `UnifiedDataService` import in `web/backend/app/api/industry_concept_analysis.py` | absent |
| Industry route path | preserved |
| Concept route path | preserved |
| Target response models | preserved |
| SQL access path | preserved |
| OpenAPI exposure | preserved |

The industry/concept direct constructor cleanup target is closed. Remaining
`get_unified_data_service` / `UnifiedDataService` hits are no longer in the
route module.

## Residual Scan

Current `web/backend/app` text hits:

| Residual | Count | Files |
|---|---:|---|
| `get_unified_data_service` / `UnifiedDataService` | 9 | `web/backend/app/services/unified_data_service.py` |
| `get_prewarming_strategy` | 5 | `web/backend/app/api/_cache_prewarming_routes.py`, `web/backend/app/core/cache_prewarming.py` |

Classification:

- `industry_concept_analysis.py` direct constructor residuals are closed.
- Remaining unified-data hits are the root facade / compatibility service
  surface and should not be edited from this closeout.
- `get_prewarming_strategy` remains the only refreshed cache/provider candidate
  in this lane, but it still needs an ownership decision before any source
  implementation.

## Next Candidate Evidence

GitNexus context for `get_prewarming_strategy`:

| Item | Value |
|---|---|
| Definition | `web/backend/app/core/cache_prewarming.py:306` |
| Risk | LOW |
| Direct callers | 3 |
| Processes affected | 0 |
| Affected module | `Api` |

Direct callers:

- `web/backend/app/api/_cache_prewarming_routes.py:trigger_cache_prewarming`
- `web/backend/app/api/_cache_prewarming_routes.py:get_prewarming_status`
- `web/backend/app/api/_cache_prewarming_routes.py:get_cache_health_status`

File-level impact for `web/backend/app/api/_cache_prewarming_routes.py` is LOW.
It is imported by `web/backend/app/api/cache.py` and by
`web/backend/tests/test_cache_api.py`.

## Verification

| Check | Result |
|---|---|
| Focused regression test | `1 passed` |
| Ruff target check | `All checks passed` |
| app.main / OpenAPI smoke | `routes=548`, `paths=500`, industry and concept paths present |

The app.main / OpenAPI smoke used transient non-secret placeholders for values
that are not required to validate import and schema generation. No environment
configuration or secret values were written to disk.

## Decision

G2.226 selects G2.227 as a future no-source ownership decision for
`get_prewarming_strategy`.

G2.226 does not authorize:

- cache prewarming source edits
- `_cache_prewarming_routes.py` route/provider changes
- `cache.py` router changes
- `cache_prewarming.py` behavior changes
- route path / response model / OpenAPI exposure changes
- frontend changes
- OpenSpec proposal or spec creation

## Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/industry-concept-unified-data-service-cleanup-closeout-refresh-2026-05-29.json` | Machine-readable G2.226 closeout / residual-refresh evidence |
| `docs/reports/quality/backend-industry-concept-unified-data-service-cleanup-closeout-refresh-2026-05-29.md` | Human-readable G2.226 closeout report |
| `governance/mainline/task-cards/pr-379.yaml` | Mainline governance task card |

## Next Gate

If accepted, start G2.227 no-source ownership decision for
`get_prewarming_strategy`. Do not start cache prewarming source implementation
directly from G2.226.

## Rollback

Revert the closeout PR. No runtime source or test changes are present in G2.226.
