# Backend DataService Provider/Reset Seam Closeout Refresh - 2026-05-29

> **历史文档说明**: 本文件是 G2.218 执行证据快照，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Branch: `g2-218-data-service-provider-closeout-refresh`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `4d2b69e449975d145976e10c8af965e16dc60a1e`
- Prepared at: `2026-05-29T01:22:32+08:00`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`
- Source authority: none

## Parent Merge

| Item | State |
|---|---|
| Parent implementation | G2.217 `DataService` provider/reset seam |
| GitHub PR | `#370` |
| PR state | `MERGED` |
| Merge commit | `4d2b69e449975d145976e10c8af965e16dc60a1e` |
| Head commit | `9e8504a82b5d5c57a0e046be2d3ddde13027a3d3` |

G2.217 is accepted into `wip/root-dirty-20260403`. This closeout refresh does not reopen source implementation.

## Verification

| Check | Result |
|---|---|
| Import smoke | `import_smoke=pass provider_override=pass reset_default=pass` |
| Focused provider test | `2 passed in 1.64s` |
| Indicator route provider regressions | `6 passed in 2.63s` |
| Ruff | `All checks passed!` |
| OpenSpec strict validate | `Change 'migrate-backend-singletons-to-lifecycle-di' is valid` |

Notes:

- The default fallback import smoke initializes `DataService` and emits existing TDengine / `MyStocksUnifiedManager` startup logs.
- OpenSpec validation still emits PostHog network flush noise after reporting the change as valid.

## DataService Residual Refresh

Static scan found five `get_data_service` token files under `web/backend/app`.
Only two are direct calls to `app.services.data_service.get_data_service()`:

| Caller | File | Role |
|---|---|---|
| `return get_data_service()` | `web/backend/app/api/indicators/indicator_cache.py:49` | route-local provider wrapper |
| `return get_data_service()` | `web/backend/app/api/v1/strategy/indicators.py:30` | route-local provider wrapper |

Non-residual token hits:

| File | Classification |
|---|---|
| `web/backend/app/services/data_service.py` | canonical provider function definition |
| `web/backend/app/api/v1/strategy/ml_runtime_helpers.py` | imports `DataService` but does not directly call `get_data_service()` |
| `web/backend/app/api/v1/system/health.py` | local `EnhancedDataService` helper named `_get_data_service`, not `app.services.data_service.get_data_service` |

Decision: keep the two route-local provider wrappers. Do not reopen DataService source from token-only matches unless current HEAD contradicts this closeout evidence.

## Residual Candidate Queue

| Candidate | Current scan | Classification | Disposition |
|---|---:|---|---|
| `get_data_service` | 2 direct singleton wrapper calls | closed by G2.217 provider/reset seam | Do not reopen without current-HEAD contradiction |
| `get_execution_tracking_evidence_service` | 3 calls in 2 files | trade evidence route-local provider surface | Select G2.219 no-source ownership decision |
| `get_unified_data_service` | 6 calls in 1 file | root facade / compatibility surface | Defer behind trade evidence ownership decision |
| `get_prewarming_strategy` | 6 calls in 3 files | cache prewarming route/provider surface | Defer behind higher-risk trade/root-facade decisions |

## Next Gate

Start G2.219 as a no-source ownership decision package for `get_execution_tracking_evidence_service`.

G2.219 should:

- Regenerate current evidence for `web/backend/app/api/trade/execution_tracking_routes.py`.
- Decide whether the getter remains a route-local provider seam or needs a later path-limited authorization package.
- Preserve the separation between decision, authorization, implementation, and closeout.
- Avoid all backend source edits unless a later authorization package is accepted.

## Not Changed

- No backend source edits.
- No tests changed.
- No route/OpenAPI contracts changed.
- No OpenSpec proposal or spec files changed.
- No GitHub issue or PR labels changed.
- No Strategy, data-quality monitor, realtime/socket, cache prewarming, root facade, `adapter_split`, or `market_data_adapter.py` source work opened.

## Evidence Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/data-service-provider-closeout-refresh-2026-05-29.json` | Machine-readable G2.218 closeout and residual refresh evidence |
| `docs/reports/quality/backend-data-service-provider-closeout-refresh-2026-05-29.md` | Human-readable G2.218 closeout report |
| `governance/mainline/task-cards/pr-371.yaml` | Mainline governance task card |
