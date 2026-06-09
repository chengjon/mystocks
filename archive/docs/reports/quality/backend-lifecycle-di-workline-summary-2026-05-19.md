# Backend Lifecycle DI Workline Summary

> Review draft for the current backend lifecycle/cleanup workline.
> Source-of-truth artifacts remain the issue threads, OpenSpec change, verification commands, and the quality reports referenced below.

## Scope

This document summarizes the work completed on the backend cleanup line covering:

- GH #31 OpenAPI cross-domain test repair
- GH #75 to #79 audit follow-ups
- backend singleton / lifecycle DI migration
- route and contract hygiene that fell out of those tasks

## What Was Completed

### #31 - Cross-domain OpenAPI test repair

- Fixed 5 failing cross-domain OpenAPI tests.
- Verification ended at `112/112 passed`.
- Commit: `c62caa05e`.

### #3 - Audit findings converted into issues

- Opened GH issues `#75` through `#79` from the audit findings.
- Those issues became the working queue for the rest of the line.

### #75 - API path closure

- Migrated `dashboard_data_source.py` to the canonical `/api/v1/strategy` path.
- Commit: `8d68ecc97`.
- Issue closed.
- The follow-up lesson was recorded in the codebase review:
  - path parity alone is not enough
  - query params, response shape, caller parser, OpenAPI examples, and minimal regression coverage must also be verified

### #76 - Orphan-file verification

- Rechecked the orphan-file inventory.
- Confirmed actual dead-code orphan count is `0`.
- The report taxonomy was updated to distinguish:
  - scanner-reported orphan
  - false positive caused by package/import chains
  - real deletion candidate

### #77 - Exception hierarchy migration

- Reframed the issue from stale `440`/`301` counts to the current live count.
- The current report states:
  - `raise HTTPException = 100`
  - `HTTPException import lines = 6`
  - 6 files involved
- The initial `_chart_data_router.py` migration pattern was established as the first working batch.
- The remaining work is now treated as AFK-style batch migration into the canonical exception hierarchy.

### #78 - Adapter lifecycle DI

Completed low-risk adapter-only lifecycle DI batches:

- EastMoney enhanced pilot: `da3282002`
- Cninfo adapter: `4e7eb6378`
- direct EastMoney adapter: `f145cec88`
- TQLEX adapter: `02ac506ce`
- AkshareExtension: `15b770239`

Pattern used for each batch:

- retain the compatibility getter
- add `install_*`
- add `get_*_dependency`
- add `close_*`
- wire `app.state` in the lifespan
- verify fallback, override, and teardown behavior with focused tests

Important classification outcome:

- `realtime_mtm` is not a simple stateless adapter and should not be migrated as if it were one.
- `web/backend/app/core/adapter_loader.py` remains blocked by the Core split / compatibility matrix work.
- Those two paths now need separate treatment, not another adapter-only batch.

### #79 - Service lifecycle DI

Started the service-tier migration with a low-risk stateless pilot:

- Pilot: `TradingViewWidgetService`
- Commit: `d5ff7fe99`
- Issue comment: `https://github.com/chengjon/mystocks/issues/79#issuecomment-4487639114`

What changed:

- `web/backend/app/services/tradingview_widget_service.py`
  - added `TRADINGVIEW_SERVICE_STATE_KEY`
  - added `install_tradingview_service()`
  - added `get_tradingview_service_dependency()`
  - added `close_tradingview_service()`
  - kept `get_tradingview_service()` as a compatibility getter
- `web/backend/app/api/tradingview.py`
  - all 6 real-service endpoints now inject the service with `Depends(get_tradingview_service_dependency)`
- `web/backend/app/app_factory.py`
  - lifespan now installs and closes the TradingView service
- tests added/updated for:
  - app.state provider
  - dependency override
  - compatibility getter fallback
  - teardown
  - route injection
  - lifecycle placement in lifespan

Verification:

- `10` TradingView-focused tests passed
- `35` lifecycle regression tests passed
- `ruff check` passed
- `py_compile` passed
- `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` passed
- GitNexus staged scope check passed as `low risk`

## Current Artifacts

- OpenSpec task file: `openspec/changes/migrate-backend-singletons-to-lifecycle-di/tasks.md`
- Lifecycle inventory: `docs/reports/quality/backend-lifecycle-di-inventory-2026-05-18.md`
- TradingView service tests:
  - `web/backend/tests/test_tradingview_service_lifecycle_di.py`
  - `web/backend/tests/test_tradingview_mock_configuration.py`

## Open Issues / Risks

1. `web/backend/app/api/data_lineage.py` still blocks `test_health_route_conflicts.py` collection because it imports `_data_lineage_responses` as a bare module.
2. GH #79 is not done. The TradingView service was only the first low-risk pilot.
3. The remaining service candidates need per-candidate classification before the next batch can safely start.
4. `realtime_mtm` still needs its own lifecycle proposal or design gate.
5. `adapter_loader` stays blocked by the Core split compatibility matrix.

## Next Work Plan

1. Fix the `data_lineage.py` import so `test_health_route_conflicts.py` can collect again.
2. Reclassify the remaining GH #79 service candidates into:
   - stateless helpers
   - external-client services
   - DB/session-backed services
   - cache/task-running services
   - process-level singletons that should remain as-is
3. Pick the next low-risk stateless service and repeat the TradingView pattern with TDD.
4. Split `realtime_mtm` out of the adapter batch and treat it as a separate runtime lifecycle proposal.
5. Resume GH #77 exception migration in small file-level batches.

## Suggested Skills For The Next Session

- `superpowers:systematic-debugging` for the `data_lineage.py` import blocker
- `superpowers:test-driven-development` for the next lifecycle batch
- `superpowers:writing-plans` before the next multi-step migration batch
- `improve-codebase-architecture` when classifying the remaining service candidates

## Review Notes

- This summary intentionally references the canonical artifacts instead of copying them.
- If you want this turned into a more formal handoff or plan document, it should be split into a dedicated execution plan for the next batch after review.
