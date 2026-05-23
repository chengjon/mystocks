# Backend TDX Route Dependency Consumer Matrix - 2026-05-23

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Status: review-ready.

Scope: G2.38 decision-only consumer matrix for the `get_tdx_service()` route
dependency surface after G2.37.

Current HEAD: `f0f761ffb7d848b8e9a8e5a492ab82f763870086`.

Parent issue: `#79` service lifecycle DI, currently `OPEN` with
`needs-triage`.

Parent PR: `#177` merged G2.37 candidate refresh at
`f0f761ffb7d848b8e9a8e5a492ab82f763870086`.

Boundary: this report is governance evidence only. It does not authorize backend
source edits, test edits, route changes, OpenAPI changes, OpenSpec changes,
issue label movement, or compatibility getter cleanup.

## Why This Matrix Exists

G2.37 confirmed the dashboard helper TDX seam is closed:
`dashboard_data_source.py` has no direct route/helper body calls to
`get_tdx_service()`.

The same refresh also found that `/api/tdx` still has live
`Depends(get_tdx_service)` sites. This matrix separates three different
consumer types before any cleanup decision:

1. `/api/v1/tdx` public route dependency consumers.
2. Dashboard helper default-provider fallback consumers.
3. Unrelated local variables or historical governance references.

## Evidence Commands

Evidence was generated from current checkout source scans plus a targeted
OpenAPI smoke using dummy required environment variables only to allow
`app.main` import.

The smoke did not start PM2, write runtime state, call external TDX services, or
change application files.

## Route And OpenAPI Snapshot

OpenAPI snapshot at current HEAD:

| Field | Value |
|---|---:|
| `paths_total` | 500 |
| `operation_ids` | 536 |
| `duplicate_operation_ids` | 0 |
| paths containing `tdx` | 7 |

TDX paths exposed in OpenAPI:

| Path | Method | Operation ID | Service dependency surface |
|---|---|---|---|
| `/api/v1/tdx/quote/{symbol}` | GET | `get_stock_quote_api_v1_tdx_quote__symbol__get` | `Depends(get_tdx_service)` |
| `/api/v1/tdx/kline` | GET | `get_stock_kline_api_v1_tdx_kline_get` | `Depends(get_tdx_service)` |
| `/api/v1/tdx/index/quote/{symbol}` | GET | `get_index_quote_api_v1_tdx_index_quote__symbol__get` | `Depends(get_tdx_service)` |
| `/api/v1/tdx/index/kline` | GET | `get_index_kline_api_v1_tdx_index_kline_get` | `Depends(get_tdx_service)` |
| `/api/v1/tdx/health` | GET | `health_check_api_v1_tdx_health_get` | `Depends(get_tdx_service)` |
| `/api/ml/tdx/data` | POST | `get_tdx_data_api_ml_tdx_data_post` | out of scope: local `TdxDataService()` variable |
| `/api/ml/tdx/stocks/{market}` | GET | `list_tdx_stocks_api_ml_tdx_stocks__market__get` | out of scope: local `TdxDataService()` variable |

Interpretation: `/api/v1/tdx` remains an active route dependency consumer of
`get_tdx_service()`. The two `/api/ml/tdx` paths are TDX-named API paths but do
not consume `app.services.tdx_service.get_tdx_service`.

## Consumer Matrix Summary

| Area | Files with matches | Interpretation |
|---|---:|---|
| Route/API files | 3 | `tdx.py` is the active route dependency consumer; `dashboard_data_source.py` keeps provider fallback; `ml.py` is an unrelated local variable surface |
| Service files | 1 | `tdx_service.py` defines the service class, legacy compatibility getter, and app-state installer |
| Test files | 2 | Dashboard provider/fallback and logging-noise tests still reference TDX service surface |
| Governance docs | 45 | Historical/planning evidence only; not runtime consumers |
| Other files | 4 | Non-runtime or non-cleanup-driving references |

Token snapshot:

| Token | Count | Meaning |
|---|---:|---|
| `get_tdx_service` | 143 | Active route dependency, dashboard fallback, tests, and governance history |
| `install_tdx_service` | 16 | App-state installer, startup prewarm, tests, and governance history |
| `get_tdx_service_dependency` | 0 | No dedicated app-state dependency provider exists yet |
| `TDX_SERVICE_STATE_KEY` | 0 | No named state-key constant exists yet; installer uses `app.state.tdx_service` |
| `TdxService` | 57 | Route annotations, helper typing, service class, tests, and governance history |
| `tdx_service` | 335 | Broad identifier including local variables and governance history |

## Runtime Consumer Classification

| File | Current consumers | Direct compatibility getter calls | Dependency refs | Decision |
|---|---|---:|---:|---|
| `web/backend/app/api/tdx.py` | `get_stock_quote`, `get_stock_kline`, `get_index_quote`, `get_index_kline`, `health_check` | 0 route-body calls | 5 `Depends(get_tdx_service)` refs | Keep active; this is the public route dependency surface |
| `web/backend/app/api/dashboard_data_source.py` | `RealBusinessDataSource` default provider, `_get_major_index_quotes`, `_get_tdx_live_market_snapshot`, prewarm factory helpers | 0 direct function body calls to `get_tdx_service()`; private `_get_tdx_service()` helper is active | 1 default provider assignment | Keep active fallback until a separate provider-fallback design changes it |
| `web/backend/app/api/ml.py` | `TdxDataService()` local variable used by ML endpoints | 0 | 0 | Out of scope for `app.services.tdx_service` lifecycle DI |

## Route Dependency Details

`web/backend/app/api/tdx.py` imports:

```python
from app.services.tdx_service import TdxService, get_tdx_service
```

Every public `/api/v1/tdx` route currently injects:

```python
service: TdxService = Depends(get_tdx_service)
```

Counts:

| Metric | Count |
|---|---:|
| `Depends(get_tdx_service)` in `tdx.py` | 5 |
| direct route-body calls to `get_tdx_service()` in `tdx.py` | 0 |
| `/api/v1/tdx` OpenAPI paths | 5 |
| `/api/v1/tdx` duplicate operation IDs | 0 |

Interpretation: this is not a direct route-body singleton call pattern. It is a
FastAPI dependency pattern that currently points at the compatibility getter
itself. A later migration can introduce a dedicated provider such as
`get_tdx_service_dependency`, but that requires a separate authorization packet.

## Service Surface

| File | Current role | Decision |
|---|---|---|
| `web/backend/app/services/tdx_service.py` | Defines `TdxService`, module-level `_tdx_service_instance`, `get_tdx_service()`, and `install_tdx_service(app, service=None)` | Keep all current symbols as active route dependency, dashboard fallback, and app-state installer surface |

Service surface counts:

| Symbol | Count in service file | Meaning |
|---|---:|---|
| `TdxService` | 5 | class, return typing, and installer typing |
| `_tdx_service_instance` | 5 | legacy singleton fallback |
| `get_tdx_service` | 2 | definition and installer fallback call |
| `install_tdx_service` | 1 | app-state installer |
| `app.state` | 3 | installer checks and writes `tdx_service` |

## Test Consumers

| File | Current role | Decision |
|---|---|---|
| `web/backend/tests/test_dashboard_data_source.py` | Verifies dashboard helper uses injected/provider-fed TDX service and guards against direct helper body getter calls | Keep; proves the G2.35 dashboard helper migration boundary |
| `web/backend/tests/test_logging_noise_regressions.py` | References `TdxService` logging behavior | Keep; not a compatibility cleanup driver |

## GitNexus Evidence

GitNexus spot checks at current HEAD:

| Target | Result | Interpretation |
|---|---|---|
| `get_tdx_service` | LOW; direct impact 1; processes affected 0; modules affected 0 | Graph sees the installer fallback caller but does not expose the `Depends(get_tdx_service)` route dependency edges; use the text and OpenAPI matrix for route decisioning |
| `install_tdx_service` | LOW; direct impact 0; processes affected 0; modules affected 0 | Graph does not expose startup prewarm references as runtime flow proof |
| `TdxService` | LOW; direct impact 0; processes affected 0; modules affected 0 | Class-level graph impact is not enough to justify deleting route dependency helpers |

Interpretation: GitNexus impact is useful as a spot check, but the decisive
evidence for this lane is the source text and OpenAPI route matrix.

## Decision

Decision: do not retire `get_tdx_service()` from this line.

Reasons:

1. `/api/v1/tdx` has five live public route dependency consumers.
2. `dashboard_data_source.py` still intentionally uses `get_tdx_service` as a
   default provider fallback.
3. `tdx_service.py` does not yet expose a dedicated
   `get_tdx_service_dependency` provider or named state-key constant.
4. Tests still cover the provider/fallback boundary.
5. OpenAPI remains stable, so there is no route/OpenAPI defect forcing an
   emergency implementation lane.

This matrix does not select or authorize source edits.

## Future Scope If Route Provider Migration Is Requested

If the maintainer wants `/api/v1/tdx` aligned with the newer service lifecycle DI
pattern, create a separate G2.39 authorization packet before source edits.

Potential future scope for that packet:

| Area | Candidate scope |
|---|---|
| Service file | Add a dedicated `get_tdx_service_dependency` provider and optional state-key constant while preserving `get_tdx_service()` fallback |
| Route file | Move five `/api/v1/tdx` endpoints from `Depends(get_tdx_service)` to the dedicated provider |
| Tests | Add focused lifecycle DI tests for provider override, installer fallback, and route dependency behavior |
| Report | Record implementation evidence, OpenAPI stability, and GitNexus staged scope |
| Boundary | Do not touch `/api/ml/tdx`, dashboard helper internals, adapter internals, external TDX connection behavior, frontend, PM2, or OpenSpec unless separately approved |

## Explicit Non-Goals

This matrix does not:

- remove `get_tdx_service()`;
- create `get_tdx_service_dependency`;
- add a state-key constant;
- edit `tdx.py`;
- edit `tdx_service.py`;
- edit tests;
- change OpenAPI paths or response contracts;
- change issue labels;
- create or archive OpenSpec changes;
- start PM2 or call real TDX services.

## Next Gate

Human review of this G2.38 matrix.

If accepted, retain `get_tdx_service()` for now and decide whether to prepare a
separate G2.39 TDX route provider migration authorization packet. No source edits
are authorized by G2.38.
