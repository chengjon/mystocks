# G2.262 Signal Statistics Route/OpenAPI Reconciliation Authorization

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Historical / review artifact note**: This document is a no-source governance artifact. It records current evidence and a recommended authorization path. It does not replace runtime code, OpenAPI schema, tests, OpenSpec tasks, or maintainer approval.

## Status

- Status: review input
- Prepared at: `2026-05-31T10:12:02+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `1d492cbad2aa849b21df1028f5fea1a3bd9c30c4`
- Parent: G2.261 / PR `#414` merged at `1d492cbad2aa849b21df1028f5fea1a3bd9c30c4`
- Scope: no-source route/OpenAPI reconciliation authorization for `web/backend/app/api/signal_monitoring/get_signal_statistics.py`

## Executive Decision

G2.262 keeps `web/backend/app/api/signal_monitoring/get_signal_statistics.py` out of service-provider implementation lanes.

The file is route-shaped, but it is not a registered runtime API surface at the current HEAD. Therefore provider injection would be misleading: it would modernize dormant code without first deciding whether the API surface should exist.

Recommended next gate: start G2.263 as a no-source signal statistics route contract disposition decision. G2.263 should make one explicit product/governance choice before any source lane:

1. Register the runtime API surface, then authorize a later provider-migration source lane.
2. Keep the module dormant and mark docs/tests as historical or deferred.
3. Retire/archive the dormant module and stale docs/tests after product ownership approval.

## Current Evidence Snapshot

| Field | Value |
|---|---:|
| Target file line count | 512 |
| Route-decorated handlers | 3 |
| Direct `get_postgres_async()` calls in file | 3 |
| Registered app routes from module | 0 |
| Exact runtime target routes | 0 |
| Exact current `app.openapi()` target paths | 0 |
| Current app routes | 548 |
| Current OpenAPI paths | 500 |
| Duplicate operation IDs | 0 |

## Route-Shaped Handlers

| Handler | Decorator line | Decorator | Direct DB calls |
|---|---:|---|---:|
| `get_signal_statistics` | 113 | `@router.get("/signals/statistics", response_model=List[SignalStatisticsResponse])` | 1 |
| `get_active_signals` | 230 | `@router.get("/signals/active", response_model=ActiveSignalsResponse)` | 1 |
| `get_strategy_detailed_health` | 364 | `@router.get("/strategies/{strategy_id}/health/detailed", response_model=StrategyDetailedHealthResponse)` | 1 |

## Runtime / OpenAPI Reconciliation Finding

At current HEAD `1d492cbad`, `app.main` imports successfully with governance placeholder environment variables. The generated FastAPI route table and `app.openapi()` do not include any of the three target paths.

| Path | Runtime route present | Current `app.openapi()` present | `docs/api/openapi.yaml` present | Total refs | Docs | Tests | Exact frontend refs |
|---|---:|---:|---:|---:|---:|---:|---:|
| `/api/signals/statistics` | no | no | yes | 21 | 20 | 1 | 0 |
| `/api/signals/active` | no | no | yes | 18 | 17 | 1 | 0 |
| `/api/strategies/{strategy_id}/health/detailed` | no | no | no | 4 | 4 | 0 | 0 |

Interpretation:

- `docs/api/openapi.yaml` is historical/stale for target paths that are absent from current `app.openapi()`.
- Exact frontend route consumers are `0`; product impact is currently documentation/test-contract driven, not observed frontend runtime consumption.
- `tests/unit/test_signal_monitoring_integration.py` is the main test reference for the dormant signal endpoints and should not be used as proof of active runtime exposure.

## Authorization Boundary

G2.262 authorizes only this decision package and steward-tree updates. It does not authorize:

- editing `web/backend/**`, including route registration or provider injection
- editing `tests/**`
- editing `docs/api/**` or generated OpenAPI files
- editing frontend, config, scripts, PM2, or runtime deployment state
- creating or modifying OpenSpec proposals/specs

## Future Scope If G2.263 Chooses Registration

A future source authorization must be separate and should include all of the following before implementation:

- route owner and API product owner approval for the three target paths
- exact router-registration file and include-prefix decision
- OpenAPI diff showing added paths and no duplicate operation IDs
- docs/api regeneration or explicit drift handling
- tests that prove runtime route presence and response contracts
- provider acquisition migration after route exposure is approved

## Future Scope If G2.263 Chooses Dormant/Retired

A future cleanup authorization must be separate and should include all of the following before editing docs/tests/source:

- explicit statement that these endpoints are not supported runtime API surfaces
- docs/api and historical docs cleanup plan
- test expectation update or removal plan
- compatibility/deprecation note if any external consumer exists
- source retirement/archive boundary if product ownership rejects the surface

## Verification Notes

Planned verification for this PR:

- markdown governance gate on the changed Markdown files
- OpenSpec strict validation for `migrate-backend-singletons-to-lifecycle-di`
- mainline scope gate with this PR task card
- GitNexus detect-changes attempt, with CLI fallback if MCP transport remains unavailable
- `git diff --check`
