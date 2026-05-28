# Backend Indicator/Data `DataService` Provider Authorization - 2026-05-29

> **历史文档说明**: 本文件是 G2.216 执行证据快照，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Branch: `g2-216-indicator-data-service-provider-authorization`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `cec3f727534008d2a48221c656c22f82f351e3d7`
- Prepared at: `2026-05-29T00:20:39+08:00`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`
- Source authority: none

## Inputs

| Input | State |
|---|---|
| PR `#368` | Merged at `cec3f727534008d2a48221c656c22f82f351e3d7` |
| G2.215 report | `docs/reports/quality/backend-indicator-data-get-data-service-ownership-decision-2026-05-28.md` |
| G2.215 evidence | `.planning/codebase/generated/indicator-data-get-data-service-ownership-decision-2026-05-28.json` |

## Current-HEAD Evidence

Fresh GitNexus indexing was performed in the isolated G2.216 worktree because the root `mystocks_spec` GitNexus entry reported `missing_kuzu`.

| Metric | Value |
|---|---:|
| GitNexus repo | `g2-216-indicator-data-service-provider-authorization` |
| Indexed at | `2026-05-28T16:23:39.044Z` |
| Risk | `LOW` |
| Direct callers | 2 |
| Impacted symbols | 2 |
| Affected processes | 0 |
| Affected modules | 0 |

| Direct caller | File | Interpretation |
|---|---|---|
| `get_indicator_data_service` | `web/backend/app/api/indicators/indicator_cache.py` | Indicator route-local provider wrapper |
| `get_strategy_indicator_data_service` | `web/backend/app/api/v1/strategy/indicators.py` | Strategy technical-indicator route-local provider wrapper |

## Source Shape

| File | Line | Evidence |
|---|---:|---|
| `web/backend/app/services/data_service.py` | 463 | `_data_service` module singleton cache |
| `web/backend/app/services/data_service.py` | 466 | `get_data_service()` lazy singleton getter |
| `web/backend/app/api/indicators/indicator_cache.py` | 49 | `get_indicator_data_service()` returns `get_data_service()` |
| `web/backend/app/api/indicators/indicator_cache.py` | 270, 522 | Route handlers receive `DataService` through `Depends(get_indicator_data_service)` |
| `web/backend/app/api/v1/strategy/indicators.py` | 30 | `get_strategy_indicator_data_service()` returns `get_data_service()` |
| `web/backend/app/api/v1/strategy/indicators.py` | 192 | Route handler receives `DataService` through `Depends(get_strategy_indicator_data_service)` |

G2.215 correctly forced ownership classification before implementation. G2.216 refines the current implementation boundary: the remaining source-level issue is the service singleton/backing API seam in `data_service.py`, not route-body direct getter use.

## Authorization Decision

If this package is accepted, authorize a future G2.217 path-limited implementation lane:

| Future surface | Authorization |
|---|---|
| `web/backend/app/services/data_service.py` | May add a provider override and reset seam while preserving `get_data_service()` as the public default singleton fallback |
| `web/backend/tests/test_data_service_singleton_provider.py` | May be added as the focused provider/reset regression test |
| `web/backend/tests/test_indicator_registry_route_provider.py` | Required regression check; not automatically authorized for source edits |
| `web/backend/tests/test_v1_indicators_regressions.py` | Required regression check; not automatically authorized for source edits |

Required future behavior:

- Keep `get_data_service()` import-compatible and runtime-compatible.
- Preserve the default lazy singleton fallback when no provider override is registered.
- Add an explicit provider registration helper for lifecycle wiring or tests.
- Add a reset helper that clears both the provider override and cached singleton.
- Keep `indicator_cache.py` and `api/v1/strategy/indicators.py` route provider wrappers compatible without route/OpenAPI contract changes.

## Not Authorized Here

- No source edits in this PR.
- No G2.217 implementation before this package is reviewed and accepted.
- No route/OpenAPI, frontend, PM2, config, script, OpenSpec, or `docs/api` edits.
- No Strategy getter residual reopen.
- No data-quality monitor, trade execution evidence, cache prewarming, realtime streaming/socket, `adapter_split`, or `market_data_adapter.py` batching.

## Next Gate

Review G2.216. If accepted, start G2.217 indicator/data `DataService` provider/reset seam implementation as a path-limited source lane. If rejected, keep `get_data_service()` retained and return to the non-Strategy provider governance queue.

## Evidence Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/indicator-data-service-provider-authorization-2026-05-29.json` | Machine-readable G2.216 authorization evidence |
| `docs/reports/quality/backend-indicator-data-service-provider-authorization-2026-05-29.md` | Human-readable G2.216 authorization package |
| `governance/mainline/task-cards/pr-369.yaml` | Mainline governance task card |
