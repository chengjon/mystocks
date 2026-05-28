# Track: Service Lifecycle DI

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active track summary
- Prepared at: `2026-05-28T17:58:00+08:00`
- Base HEAD checked: `b4b34375eef0186b81be9a24491328dab72c2e21`

Boundary note: this track summary does not authorize source changes. Each
implementation still needs a path-limited authorization package, GitNexus impact
analysis, tests, staged change detection, review, and PR merge.

## Track Role

This track owns the gradual replacement of route-body or service-body global
getter calls with explicit dependency providers or constructor/provider seams.
It proved a repeatable conveyor:

1. inventory or residual scan
2. candidate classification
3. decision package
4. implementation authorization
5. TDD implementation
6. closeout and residual refresh

## Current Strategy Residual State

| Node | State | Notes |
|---|---|---|
| Steward split | Merged by PR `#332` | Root task tree is now a short entrypoint; active state belongs in this split track and `steward-index.json` |
| G2.177 Strategy canonical adapter provider authorization | Accepted and merged by PR `#330` | Authorized only a constructor-level Strategy service provider seam in canonical `strategy_adapter.py` and focused tests |
| G2.178 Strategy adapter provider implementation | Merged by PR `#331` | Added the approved optional constructor-level provider seam and reconciled the G2.178 steward update into the split tree |
| G2.180 Strategy adapter provider closeout | Merged by PR `#333` | Records G2.178 as closed and refreshes residual Strategy getter distribution without source edits |
| G2.181 Strategy getter residual refresh decision | Merged by PR `#334` | Rechecks residual classes and selects route/provider fallback as the next governance target |
| G2.182 Strategy route/provider fallback decision | Merged by PR `#335` | Classifies the route/provider fallback as a retained route-local provider seam and does not open a source lane |
| G2.183 Strategy getter remaining residual decision | Merged by PR `#336` | Closes the current Strategy getter residual track with retained residuals and focused residual test evidence |
| G2.184 next non-Strategy candidate decision | Merged by PR `#337` | Selects route dependency/provider governance as the next decision target and opens no source lane |
| G2.185 route dependency/provider governance decision | Merged by PR `#338` | Classifies active FastAPI providers as retained route contracts, not singleton getter deletion candidates |
| G2.186 remaining getter inventory refresh | Merged by PR `#339` | Refreshes direct getter inventory after provider governance and recommends a narrow stop-loss authorization package as the next gate |
| G2.187 risk stop-loss route provider authorization | Merged by PR `#340` | Defines the future G2.188 implementation scope for stop-loss route provider injection without source edits in that PR |
| G2.188 risk stop-loss route provider implementation | Merged by PR `#341` | Implements the authorized provider injection in `web/backend/app/api/risk/stop_loss.py`; post-merge stop-loss tests and OpenAPI dependency leak smoke pass |
| G2.189 risk stop-loss provider closeout / candidate refresh | Merged by PR `#342` | Records PR `#341` closeout, marks the stop-loss pair closed for route-body provider migration, and selects data-quality / adapter cross-cutting governance as the next design-only gate |
| G2.190 data-quality / adapter cross-cutting decision | Merged by PR `#343` | Classifies `get_data_quality_monitor` as `CRITICAL`, splits the route/adapter/wrapper surfaces, and selects G2.191 route-only authorization as the next gate |
| G2.191 data-quality route provider authorization | Merged by PR `#344` | Authorized a future G2.192 route-only implementation lane for `web/backend/app/api/data_quality.py` and focused tests, with no source edits in G2.191 |
| G2.192 data-quality route provider implementation | Merged by PR `#345` | Implements authorized provider injection in `web/backend/app/api/data_quality.py`; focused tests and OpenAPI leak smoke pass |
| G2.193 data-quality route provider closeout / remaining candidate refresh | Merged by PR `#346` | Marks route-body provider migration closed and selects adapter constructor seam design / test-double decision as the next governance gate |
| G2.194 data-quality adapter constructor seam design | Merged by PR `#347` | Selects `adapter_split` constructor provider authorization as the next gate, defines test-double contract, and keeps source authority at none |
| G2.195 data-quality `adapter_split` constructor provider authorization | Merged by PR `#348` | Authorizes the future G2.196 `adapter_split` constructor provider implementation lane while keeping source authority at none in that PR |
| G2.196 data-quality `adapter_split` constructor provider implementation | Merged by PR `#349` | Implements optional constructor monitor injection in `adapter_split` only, with focused TDD evidence |
| G2.197 data-quality monitor closeout / remaining candidate refresh | Merged by PR `#350` | Closes the `adapter_split` subclass constructor lane and refreshes remaining service adapter, legacy adapter, compatibility facade, and wrapper surfaces |
| G2.198 data-quality residual adapter ownership decision | Merged by PR `#351` | Selects canonical service adapters as the next authorization target while deferring legacy data adapters, `market_data_adapter.py`, and wrapper retention |
| G2.199 data-quality canonical service adapter provider authorization | Merged by PR `#352` | Authorizes future G2.200 implementation for canonical service adapters only; no source edits in G2.199 |
| G2.200 data-quality canonical service adapter provider implementation | Merged by PR `#353` | Implements optional constructor monitor injection in the two canonical service adapters with focused TDD evidence |
| G2.201 data-quality canonical service adapter closeout / refresh | Merged by PR `#354` | Closes the canonical service adapter lane and selects legacy data adapter compatibility ownership as the next decision gate |
| G2.202 data-quality legacy adapter compatibility ownership decision | Merged by PR `#355` | Classifies two legacy `data_adapters` files as compatibility ownership surfaces and selects G2.203 authorization-only compatibility closure |
| G2.203 data-quality legacy adapter compatibility closure authorization | Merged by PR `#356` | Authorizes only a future thin-wrapper compatibility implementation shape for the two legacy modules; deletion remains unauthorized |
| G2.204 data-quality legacy adapter compatibility wrapper implementation | Merged by PR `#357` | Converts two legacy modules into thin wrappers, preserves old import paths, and reduces target legacy getter calls to `0` |
| G2.205 data-quality legacy adapter compatibility wrapper closeout / residual refresh | Merged by PR `#358` | Closes the legacy wrapper target and recommends G2.206 `market_data_adapter.py` compatibility facade ownership decision |
| G2.206 data-quality `market_data_adapter.py` compatibility facade ownership decision | Merged by PR `#359` | Classifies `market_data_adapter.py` as active data-source-factory compatibility facade and recommends G2.207 provider seam authorization |
| G2.207 data-quality `market_data_adapter.py` provider seam authorization | Merged by PR `#360` | Authorizes future G2.208 source implementation scope without source edits in G2.207 |
| G2.208 data-quality `market_data_adapter.py` provider seam implementation | For review | Implements optional quality monitor injection while preserving default singleton fallback and data-source-factory constructor compatibility |

## Current Strategy Getter Residuals

At HEAD `d454193fdae08ad875c423e0b5aa959d79bedc67`, the current Strategy
getter residual track is closed with retained residuals. The latest accepted
G2.183 classification recorded these `get_strategy_service` hits under
`web/backend/app`:

| File | Hits | Current decision |
|---|---:|---|
| `web/backend/app/services/adapters/strategy_adapter.py` | 10 | Retained adapter-local helper/provider seam; no adapter-local cleanup authorization opened by G2.183 |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 6 | Retained route-local provider fallback; no source lane opened by G2.182 |
| `web/backend/app/tasks/backtest_tasks.py` | 2 | Retained backtest task resolver fallback; do not reopen unless current evidence contradicts focused tests |
| `web/backend/app/services/strategy_service.py` | 1 | Public getter definition; retain as compatibility entrypoint and do not delete, rename, or privatize here |

## G2.186 Remaining Getter Refresh

At HEAD `720248521d705af067d0a2600710444e439d7605`, G2.186 scanned
`web/backend/app/api` and `web/backend/app/services` after excluding function
definitions, imports, FastAPI `Depends(...)` provider references,
`*_dependency` names, object method calls, comments, and decorators.

| Metric | Count |
|---|---:|
| Python files scanned | 371 |
| Direct `get_*` names after exclusion | 111 |
| Direct `get_*` calls after exclusion | 296 |

| Candidate class | Names | Calls | Current handling |
|---|---:|---:|---|
| Infra / control-plane / session accessors | 18 | 78 | Not service lifecycle source candidates |
| Factory / adapter / helper / root facade | 27 | 101 | Requires owner-specific decisions |
| Manual review residue | 44 | 50 | Must not become backlog automatically |
| Cache / messaging accessors | 3 | 12 | Cache/messaging lifecycle track |
| Realtime / streaming track | 10 | 12 | Already governed by realtime streaming/socket track |
| Service singleton review | 10 | 43 | Classified by G2.186 generated evidence |

G2.188 closed the stop-loss route-body provider migration. The stop-loss
src-level getters now remain retained provider backing functions, not deletion
candidates. High-risk data-quality, root-facade, control-plane cache, trade
evidence, and constructor fallback getters stay deferred to their owner-specific
tracks.

## G2.187 / G2.188 Stop-Loss Provider Lane

At HEAD `0aac0e16f16480bd99eebb8726e21a7db6566b39`, G2.188 implements the
G2.187-authorized stop-loss route provider seam by replacing route-body resolver
calls with FastAPI dependency-injected service parameters.

| Implementation surface | Current direct consumers | GitNexus risk | Current decision |
|---|---:|---|---|
| `_resolve_history_service` | 0 route-body calls after G2.188 | LOW | Wrapped by `get_stop_loss_history_service_provider`; direct test fallback preserved |
| `_resolve_execution_service` | 0 route-body calls after G2.188 | MEDIUM | Wrapped by `get_stop_loss_execution_service_provider`; direct test fallback preserved |

G2.188 touched only `web/backend/app/api/risk/stop_loss.py`, focused stop-loss
tests, and governance evidence. It preserved route paths, HTTP methods,
response-model declarations, OpenAPI examples, and src-level service getters.
Post-merge smoke records `openapi_paths=500`, `stop_loss_paths=10`, and
`dependency_params_leaked=0`.

## G2.190 Data-Quality / Adapter Cross-Cutting Lane

At HEAD `5565e2b0967958c406a4115dc840a9e90a0b2aab`, GitNexus classifies
`get_data_quality_monitor` as `CRITICAL`: 20 direct callers, 24 impacted symbols,
7 affected processes, and 4 affected modules.

| Surface | Files | Getter calls | Current decision |
|---|---:|---:|---|
| Data-quality route | 1 | 6 | Select as the next route-only authorization package, not source implementation |
| Split adapter constructors | 8 | 8 | Defer until interface / test-double design exists |
| Legacy adapter compatibility | 5 | 5 | Defer to separate compatibility ownership decision |
| Service wrapper / export | 2 | 2 | Retain until route and adapter consumers are migrated and verified |

G2.190 does not authorize source edits. It recommends G2.191 as a
data-quality route provider authorization package only.

## G2.191 Data-Quality Route Provider Authorization

At HEAD `7154ffbb067dcddc52d80f15342961b51234ac09`,
`web/backend/app/api/data_quality.py` has 9 route handlers. Seven touch the
data-quality monitor surface: 6 direct `get_data_quality_monitor()` calls and 1
`monitor_data_quality()` helper call.

| Future G2.192 surface | Current count | Authorization |
|---|---:|---|
| Route file | 1 | `web/backend/app/api/data_quality.py` only |
| Route handlers touching monitor surface | 7 | Allowed for provider injection |
| Focused tests | 3 path candidates | Allowed only for route/provider regression, OpenAPI leak, and import smoke coverage |
| Adapter / legacy adapter / singleton wrapper surfaces | 0 allowed | Explicitly forbidden |

G2.191 does not authorize current-PR source edits. If accepted, it authorizes
G2.192 as a path-limited source lane. G2.192 must preserve route paths, HTTP
methods, response models, OpenAPI examples, error response contract, data-source
factory behavior, and current `DataQualityMonitor` backing singleton behavior.

## G2.192 Data-Quality Route Provider Implementation

At HEAD `b899a173909d3818370dddbf35b039832266bd1d`, G2.192 applies the G2.191
authorization to the route file only.

| Result | Value |
|---|---:|
| Route body `get_data_quality_monitor()` calls | 0 |
| Route body `monitor_data_quality()` helper calls | 0 |
| Route handlers using `Depends(get_data_quality_monitor_provider)` | 7 |
| Direct-call fallback resolver uses | 7 |
| Focused tests | 7 passed |
| OpenAPI paths | 500 |
| Data-quality OpenAPI paths | 9 |
| Dependency parameters leaked into OpenAPI | 0 |

G2.192 does not change adapter constructors, legacy adapter compatibility,
singleton wrappers, or `DataQualityMonitor` internals.

## G2.193 Data-Quality Route Provider Closeout / Refresh

At HEAD `2b0c3ce373fba38bacd62eff5436822527dccda1`, PR `#345` is merged and
the data-quality route-body provider migration is closed.

| Closeout result | Value |
|---|---:|
| Route body `get_data_quality_monitor()` calls | 0 |
| Route body `monitor_data_quality()` helper calls | 0 |
| Retained provider backing `get_data_quality_monitor()` calls in route file | 1 |
| Route handlers using `Depends(get_data_quality_monitor_provider)` | 7 |
| Direct-call fallback resolver uses | 7 |
| Focused tests | 7 passed |
| OpenAPI paths | 500 |
| Data-quality OpenAPI paths | 9 |
| Dependency parameters leaked into OpenAPI | 0 |

Remaining `get_data_quality_monitor` surface after route closeout:

| Bucket | Files | Getter calls | Current decision |
|---|---:|---:|---|
| route | 1 | 1 | Retained provider backing getter, not route-body debt |
| adapter_split | 8 | 8 | Next governance target: adapter constructor seam design / test-double decision |
| service_adapter | 2 | 2 | Compatibility surface, defer until adapter seam design is explicit |
| legacy_adapter | 2 | 2 | Compatibility surface, defer to owner-specific decision |
| other | 1 | 1 | `market_data_adapter.py` compatibility surface |
| service_wrapper | 1 | 2 | Retain singleton wrapper / backing API until consumers are migrated and verified |

## G2.194 Data-Quality Adapter Constructor Seam Design

At HEAD `ea659d52903a5e9884d396069526ea08f15109a6`, PR `#346` is merged and the
remaining data-quality adapter seam is classified as constructor-level
dependency ownership, not route-body provider debt.

| Inventory item | Value |
|---|---:|
| Adapter-related files scanned | 14 |
| `get_data_quality_monitor()` calls | 15 |
| `monitor_data_quality()` helper calls | 1 |
| `__init__` definitions | 15 |
| Constructors with quality monitor parameter | 0 |

Surface classification:

| Surface | Files | Getter calls | G2.194 decision |
|---|---:|---:|---|
| `adapter_split` | 8 | 8 | Next governance target: constructor provider authorization |
| service adapters | 2 | 2 | Defer; async runtime monitoring surface, not constructor migration |
| legacy adapters | 2 | 2 | Defer to owner-specific compatibility decision |
| `market_data_adapter.py` | 1 | 1 | Defer as compatibility surface |
| singleton wrapper | 1 | 2 plus 1 helper | Retain backing API until consumers are migrated and verified |

GitNexus design evidence:

| Target | Risk | Impact summary | Decision use |
|---|---|---|---|
| `get_data_quality_monitor` | CRITICAL | 24 impacted symbols, 20 direct callers, 7 processes, 4 modules | Do not migrate all surfaces in one source lane |
| `BaseAdapter` | MEDIUM | 7 direct subclass extenders | Use `adapter_split` constructor seam as the first authorization candidate |

Required future test-double contract:

- `FakeDataQualityMonitor.check_data_quality(data, source_or_context)` records
  calls and returns a truthy quality result.
- `FakeDataQualityMonitor.evaluate_data_quality(...)` records calls and returns
  a truthy result for later async runtime-monitoring surfaces.
- Future source implementation must prove `BaseAdapter` and subclass
  constructors can accept the fake monitor/provider without calling the global
  getter.
- Future source implementation must prove subclass constructors do not overwrite
  the injected monitor and default runtime behavior remains compatible.

## G2.195 Data-Quality Adapter Split Constructor Provider Authorization

At HEAD `e30e16605df6aaa333989a7ac247bab3dcd0dd01`, PR `#347` is merged and
the next gate is an authorization package for a future source lane.

G2.195 authorizes G2.196 only after review acceptance. G2.195 itself has no
source edit authority.

Future authorized implementation lane:

| Future lane | Authorized scope |
|---|---|
| G2.196 data-quality `adapter_split` constructor provider implementation | Add injectable data-quality monitor construction for `adapter_split` classes only, preserving default singleton behavior |

Future authorized source paths:

| Path | Future role |
|---|---|
| `web/backend/app/services/adapters_split/base_adapter.py` | Add injection seam defaulting to current singleton behavior |
| `web/backend/app/services/adapters_split/baostock_adapter.py` | Pass injected monitor/provider through constructor |
| `web/backend/app/services/adapters_split/tushare_adapter.py` | Pass injected monitor/provider through constructor |
| `web/backend/app/services/adapters_split/customer_adapter.py` | Preserve `ws_url`; use keyword-only injection |
| `web/backend/app/services/adapters_split/byapi_adapter.py` | Pass injected monitor/provider through constructor |
| `web/backend/app/services/adapters_split/akshare_adapter.py` | Pass injected monitor/provider through constructor |
| `web/backend/app/services/adapters_split/efinance_adapter.py` | Pass injected monitor/provider through constructor |
| `web/backend/app/services/adapters_split/tdx_adapter.py` | Pass injected monitor/provider through constructor |

Future authorized test path:

| Path | Future role |
|---|---|
| `web/backend/tests/test_adapter_split_data_quality_monitor_provider.py` | Focused fake-monitor constructor provider regression tests |

Future forbidden surfaces remain:

- service adapters under `web/backend/app/services/adapters/`
- legacy adapters under `web/backend/app/services/data_adapters/`
- `web/backend/app/services/market_data_adapter.py`
- `web/backend/app/services/_data_quality_monitor_singleton.py`
- `web/backend/app/services/data_quality_monitor.py`
- route, frontend, OpenAPI contract, config, script, and OpenSpec change files

Required future checks include a focused pytest for the new test path, ruff on
the eight adapter files plus test, OpenSpec strict validation, and staged
GitNexus change detection.

## G2.196 Data-Quality Adapter Split Constructor Provider Implementation

At HEAD `fabd674e8a748cdd2c51a80eebb5ad20b52bc737`, PR `#348` is merged and
the G2.195 authorization package is accepted.

G2.196 implements the authorized `adapter_split` constructor provider seam:

| Item | Before | After |
|---|---:|---:|
| `adapter_split` subclass `get_data_quality_monitor()` calls | 7 | 0 |
| `adapter_split` subclass `get_data_quality_monitor` imports | 7 | 0 |
| `BaseAdapter` singleton fallback calls | 1 | 1 |
| Constructors accepting `quality_monitor` | 0 | 8 |
| Focused regression tests | 0 | 1 |

Implementation evidence:

- `BaseAdapter` accepts optional `quality_monitor` and falls back to the current
  singleton getter for default construction.
- Seven `adapter_split` subclasses accept keyword-only `quality_monitor` and
  pass it through to `BaseAdapter`.
- `CustomerAdapter` preserves `ws_url` compatibility.
- `tushare_adapter.py` and `byapi_adapter.py` import `os` for existing
  `os.getenv` usage reached by constructor smoke.
- `tdx_adapter.py` logs `self.name` instead of undefined `TDX`.

Focused verification:

| Check | Result |
|---|---|
| TDD red | Failed on missing `quality_monitor` constructor parameter |
| Focused pytest | `1 passed` |
| Ruff authorized files | `All checks passed` |
| Import smoke | Passed with minimal dummy required env |
| OpenSpec strict validate | Valid; PostHog network flush noise only |

PR `#349` merged this lane at
`e4245ebe54c5ad6d2aebf4802d165d59700c9eeb`.

## G2.197 Data-Quality Monitor Closeout / Refresh

At HEAD `e4245ebe54c5ad6d2aebf4802d165d59700c9eeb`, PR `#349` is merged and
the G2.196 `adapter_split` implementation is closed.

Closeout result:

| Item | Current value |
|---|---:|
| `adapter_split` subclass `get_data_quality_monitor()` calls | 0 |
| `adapter_split` subclass `get_data_quality_monitor` imports | 0 |
| `BaseAdapter` compatibility fallback calls | 1 |
| Constructors accepting `quality_monitor` | 8 |

Remaining data-quality monitor surfaces:

| Surface | Files | Getter calls | Current decision |
|---|---:|---:|---|
| `adapter_split` | 8 | 1 | Closed; only `BaseAdapter` compatibility fallback remains |
| service adapters | 2 | 2 | Defer to residual adapter ownership decision |
| legacy data adapters | 2 | 2 | Defer to owner-specific compatibility decision |
| `market_data_adapter.py` | 1 | 1 | Defer as root compatibility facade surface |
| singleton wrapper / canonical monitor | 2 | 2 | Retain backing API and canonical implementation; not a deletion lane |

G2.197 recommends G2.198 as a decision-only residual adapter ownership package.
It does not authorize another source implementation lane.

PR `#350` merged this lane at
`3acf90c3ab17dbb3b47150a03f1cdee1c96dc8f1`.

## G2.198 Data-Quality Residual Adapter Ownership Decision

At HEAD `3acf90c3ab17dbb3b47150a03f1cdee1c96dc8f1`, PR `#350` is merged and
the G2.197 closeout / refresh is accepted.

G2.198 selects canonical service adapters as the next ownership target:

| Surface | Files | Getter calls | Current decision |
|---|---:|---:|---|
| canonical service adapters | 2 | 2 | Select as G2.199 authorization target |
| legacy data adapters | 2 | 2 | Defer to compatibility ownership decision |
| `market_data_adapter.py` | 1 | 1 | Defer as root compatibility facade surface |
| singleton wrapper / canonical monitor | 2 | 2 or re-export | Retain backing API and canonical implementation |

Selected future authorization candidate:

| Path | Role |
|---|---|
| `web/backend/app/services/adapters/dashboard_adapter.py` | Canonical dashboard data-source adapter, currently calls `get_data_quality_monitor()` in async monitoring helper |
| `web/backend/app/services/adapters/data_adapter.py` | Canonical data data-source adapter, currently calls `get_data_quality_monitor()` in async monitoring helper |

G2.198 recommends G2.199 as an authorization-only package. It does not authorize
source implementation directly.

PR `#351` merged this lane at
`a6b54ddfb24055552d634757f01dc03bd6ca6e62`.

## G2.199 Data-Quality Canonical Service Adapter Provider Authorization

At HEAD `a6b54ddfb24055552d634757f01dc03bd6ca6e62`, PR `#351` is merged and
G2.198's ownership decision is accepted.

G2.199 authorizes a future G2.200 implementation lane only after review
acceptance. G2.199 itself has no source edit authority.

Future authorized source paths:

| Path | Future role |
|---|---|
| `web/backend/app/services/adapters/dashboard_adapter.py` | Add optional injectable data-quality monitor seam while preserving `config` positional constructor compatibility |
| `web/backend/app/services/adapters/data_adapter.py` | Add optional injectable data-quality monitor seam while preserving `config` positional constructor compatibility |

Future authorized test paths:

| Path | Future role |
|---|---|
| `web/backend/tests/test_data_quality_canonical_service_adapter_provider.py` | New focused fake-monitor provider regression tests |
| `tests/backend/test_data_adapter_regression.py` | Existing adapter regression coverage if needed |
| `web/backend/tests/test_logging_noise_regressions.py` | Existing dashboard adapter logging/noise regression coverage if needed |

Future forbidden surfaces remain:

- legacy data adapters under `web/backend/app/services/data_adapters/`
- `web/backend/app/services/market_data_adapter.py`
- `web/backend/app/services/_data_quality_monitor_singleton.py`
- `web/backend/app/services/data_quality_monitor.py`
- route, frontend, OpenAPI contract, config, script, and OpenSpec change files

PR `#352` merged this authorization lane at
`41bef3787160ec3bf7b9b31220df9d99a3437474`.

## G2.200 Data-Quality Canonical Service Adapter Provider Implementation

At HEAD `41bef3787160ec3bf7b9b31220df9d99a3437474`, PR `#352` is merged and
G2.199's authorization package is accepted.

Implementation result:

| Path | Result |
|---|---|
| `web/backend/app/services/adapters/dashboard_adapter.py` | Adds keyword-only `quality_monitor` and uses it in async quality monitoring before falling back to `get_data_quality_monitor()` |
| `web/backend/app/services/adapters/data_adapter.py` | Adds keyword-only `quality_monitor` and uses it in async quality monitoring before falling back to `get_data_quality_monitor()` |
| `web/backend/tests/test_data_quality_canonical_service_adapter_provider.py` | Proves injected monitors bypass the module-level global getter for both canonical adapters |

Focused verification:

| Check | Result |
|---|---|
| GitNexus impact | LOW for both canonical adapter files |
| TDD red | Failed on missing `quality_monitor` constructor parameter |
| TDD green | `2 passed` |
| Focused regression package | `21 passed` |
| Ruff authorized files | `All checks passed` |
| Import smoke | Passed with minimal dummy required env |
| OpenSpec strict validate | Valid; PostHog network flush noise only |

PR `#353` merged this lane at
`cbd9b3a7ee730c72a63dbc7adb6490564c12c71e`.

## G2.201 Data-Quality Canonical Service Adapter Closeout / Refresh

At HEAD `cbd9b3a7ee730c72a63dbc7adb6490564c12c71e`, PR `#353` is merged and
G2.200 is accepted.

Closeout result:

| Surface | State | Decision |
|---|---|---|
| Canonical service adapters | Closed | `DashboardDataSourceAdapter` and `DataDataSourceAdapter` now support keyword-only `quality_monitor` injection while preserving singleton fallback |
| Focused tests | Closed | Post-merge focused regression package records `21 passed` |
| Function-tree / mainline mapping | Closed | `domain-01-node-03` maps the two canonical service adapter paths and focused test |

Remaining `get_data_quality_monitor()` surface after G2.201 refresh:

| Bucket | Files | Calls | Current decision |
|---|---:|---:|---|
| Route provider backing | 1 | 1 | Retained provider backing getter from prior route provider lane |
| `adapter_split` base fallback | 1 | 1 | Closed adapter_split lane; retain default singleton fallback |
| Canonical service adapter fallback | 2 | 2 | Closed by G2.200; retain fallback for default construction |
| Legacy data adapters | 2 | 2 | Select as G2.202 compatibility ownership decision target; no source authority from G2.201 |
| `market_data_adapter.py` facade | 1 | 1 | Defer as root compatibility facade surface until an owner-specific decision package |
| Singleton wrapper / backing API | 1 | 2 | Retain backing API; not a deletion lane |

GitNexus reference for deferred surfaces:

| Target | Risk | Impact |
|---|---|---|
| `web/backend/app/services/data_adapters/dashboard.py` | LOW | `impacted_count=0`, `processes_affected=0` |
| `web/backend/app/services/data_adapters/data_source.py` | LOW | `impacted_count=0`, `processes_affected=0` |
| `web/backend/app/services/market_data_adapter.py` | LOW | `impacted_count=3`, `direct=1`, `processes_affected=0` |
| `web/backend/app/services/_data_quality_monitor_singleton.py` | LOW | `impacted_count=19`, `direct=1`, `processes_affected=0` |

## G2.202 Data-Quality Legacy Adapter Compatibility Ownership Decision

At HEAD `e672f1523c30037202310278daf71488681d9a1f`, PR `#354` is merged and
G2.201 is accepted.

Decision result:

| Target | Evidence | Decision |
|---|---|---|
| `web/backend/app/services/data_adapters/dashboard.py` | `DashboardDataSourceAdapter`, 299 lines, one `get_data_quality_monitor()` call, GitNexus `LOW/0` | Legacy compatibility ownership surface; no source edits in G2.202 |
| `web/backend/app/services/data_adapters/data_source.py` | `DataDataSourceAdapter`, 688 lines, one `get_data_quality_monitor()` call, GitNexus `LOW/0` | Legacy compatibility ownership surface; no source edits in G2.202 |

Consumer evidence:

| Check | Result |
|---|---|
| Exact module-path imports of `app.services.data_adapters.dashboard` / `data_source` outside the legacy package | `0` |
| Class-name text scan | Ambiguous because canonical `app.services.adapters.*` classes share the names |
| Root facade | `web/backend/app/services/data_adapter.py` imports from canonical `app.services.adapters` |
| Data source factory | Imports through `app.services.data_adapter` facade, not the legacy module path |

G2.202 selects G2.203 as an authorization-only compatibility closure package.
G2.203 must decide the exact implementation shape before any source lane:
thin wrapper, retirement with rollback gates, or retained legacy surface.

## G2.203 Data-Quality Legacy Adapter Compatibility Closure Authorization

At HEAD `bf5d5ffba6bfc837c009a3d937cf0a9e6549883f`, PR `#355` is merged and
G2.202 is accepted.

Authorization result:

| Future lane | Authorized files | Authorized shape |
|---|---|---|
| G2.204 data-quality legacy adapter compatibility wrapper implementation | `web/backend/app/services/data_adapters/dashboard.py`, `web/backend/app/services/data_adapters/data_source.py`, `web/backend/tests/test_data_quality_legacy_data_adapter_compat.py` | Thin compatibility wrappers re-exporting canonical `app.services.adapters` classes |

Current evidence:

| Check | Result |
|---|---|
| Exact external imports of legacy module paths | `0` |
| Target getter calls | Two calls total, one in each legacy module |
| GitNexus impact | LOW/0 for both target files |
| Deletion authority | Not granted |

G2.203 does not authorize source edits in this PR. If accepted, G2.204 may edit
only the two legacy modules and one focused compatibility test. It must not
delete files, touch `market_data_adapter.py`, alter singleton wrapper/backing
APIs, edit canonical adapters, or expand into routes, OpenAPI, frontend, config,
scripts, or OpenSpec files.

## G2.204 Data-Quality Legacy Adapter Compatibility Wrapper Implementation

At HEAD `142a2bf1c0c5f979cf9c32415d2f25832e7e62cd`, PR `#356` is merged and
G2.203 is accepted.

Implementation result:

| Target | Result |
|---|---|
| `web/backend/app/services/data_adapters/dashboard.py` | Thin wrapper re-exporting canonical `DashboardDataSourceAdapter` |
| `web/backend/app/services/data_adapters/data_source.py` | Thin wrapper re-exporting canonical `DataDataSourceAdapter` |
| `web/backend/tests/test_data_quality_legacy_data_adapter_compat.py` | Focused compatibility test for old import paths and getter removal |

TDD evidence:

| Phase | Result |
|---|---|
| RED | `2 failed`, proving legacy classes were not canonical and legacy modules still contained `get_data_quality_monitor` |
| GREEN | `2 passed` focused compatibility test |
| Regression | `23 passed` broader focused package |
| Targeted ruff/import smoke | Passed |
| Legacy getter scan | `0` calls in the two wrapper modules |

PR `#357` merged this lane at
`a621ba4ae66f581074a3b66539e296cbf0ced1b5`.

## G2.205 Data-Quality Legacy Adapter Compatibility Wrapper Closeout / Refresh

At HEAD `a621ba4ae66f581074a3b66539e296cbf0ced1b5`, PR `#357` is merged and
G2.204 is accepted.

Closeout result:

| Surface | State | Decision |
|---|---|---|
| Legacy data adapter wrappers | Closed | The two legacy modules preserve old import paths and contain `0` `get_data_quality_monitor` calls |
| Wrapper deletion | Not authorized | Legacy modules remain compatibility surfaces |
| Focused compatibility test | Present | `web/backend/tests/test_data_quality_legacy_data_adapter_compat.py` remains the regression check |

Remaining active app `get_data_quality_monitor` surface after G2.205 refresh:

| Bucket | Files | Active hits | Current decision |
|---|---:|---:|---|
| Route provider backing | 1 | 17 | Retain as FastAPI dependency/provider surface; route-body direct-call migration is already closed |
| `adapter_split` base fallback | 1 | 2 | Retain default singleton fallback after G2.196 constructor injection |
| Canonical service adapter fallbacks | 2 | 4 | Retain default singleton fallback after G2.200 optional monitor injection |
| Legacy data adapter wrappers | 2 | 0 | Closed by G2.204/G2.205 |
| `market_data_adapter.py` facade | 1 | 2 | Select as G2.206 compatibility facade ownership decision target |
| Singleton wrapper / backing API | 2 | 4 | Retain public backing API; not a deletion lane |

Excluded text hits:

- `web/backend/app/services/data_adapter.py.backup.20260130` is a backup artifact
  and is not counted as active source.
- Focused tests are expected regression evidence, not source residuals.

PR `#358` merged this lane at
`44909f5d048700115da6a9eb9345957b8af3d077`.

## G2.206 Data-Quality Market Data Adapter Ownership Decision

At HEAD `44909f5d048700115da6a9eb9345957b8af3d077`, PR `#358` is merged and
G2.205 is accepted.

Decision result:

| Target | Evidence | Decision |
|---|---|---|
| `web/backend/app/services/market_data_adapter.py` | 481 lines; defines `DataSourceMetrics` and `MarketDataSourceAdapter`; imports `get_data_quality_monitor` at line 10 and calls it at line 327 | Active data-source-factory compatibility facade; no source edits in G2.206 |
| `web/backend/app/services/data_source_factory/data_source_factory.py` | Direct app importer and constructor caller | Must remain compatible; test in future lane, but do not edit unless explicitly authorized |

GitNexus reference:

| Target | Risk | Impact |
|---|---|---|
| `web/backend/app/services/market_data_adapter.py` | LOW | `impacted_count=3`, `direct=1`, `processes_affected=0` |

G2.206 selects G2.207 as an authorization-only package for a future narrow
provider seam. It does not authorize deletion, wrapper conversion, or source
implementation.

PR `#359` merged this lane at
`ded789ee5d49d6ddcce5d8a69af1901a8481d1f0`.

## G2.207 Data-Quality Market Data Adapter Provider Authorization

At HEAD `ded789ee5d49d6ddcce5d8a69af1901a8481d1f0`, PR `#359` is merged and
G2.206 is accepted.

Authorization result:

| Future lane | Authorized source path | Authorized tests |
|---|---|---|
| G2.208 `market_data_adapter.py` provider seam implementation | `web/backend/app/services/market_data_adapter.py` | `web/backend/tests/test_market_data_adapter_quality_monitor_provider.py`, `web/backend/tests/test_market_data_service_getter_retirement.py` |

Required future shape:

- preserve the existing positional `config` constructor argument
- add only keyword-only optional injection parameters
- preserve singleton fallback behavior when no injection is supplied
- ensure injected monitor/provider bypasses the module-level
  `get_data_quality_monitor()` getter
- keep `MarketDataSourceAdapter(config.__dict__)` compatible for
  `data_source_factory`

Forbidden in G2.208 unless a later package explicitly expands scope:

- source edits under `web/backend/app/services/data_source_factory/**`
- singleton wrapper deletion or privatization
- `DataQualityMonitor` internals
- route, OpenAPI, frontend, config, script, or OpenSpec changes

PR `#360` merged this lane at
`b4b34375eef0186b81be9a24491328dab72c2e21`.

## G2.208 Data-Quality Market Data Adapter Provider Implementation

At HEAD `b4b34375eef0186b81be9a24491328dab72c2e21`, PR `#360` is merged and
G2.207 is accepted.

Implementation result:

| Item | Before | After |
|---|---|---|
| `MarketDataSourceAdapter` constructor | `config` only | `config`, plus keyword-only optional `quality_monitor` |
| Default quality monitor behavior | module-level getter fallback | preserved |
| Injected quality monitor behavior | not supported | injected monitor bypasses module-level getter |
| `data_source_factory` constructor compatibility | `MarketDataSourceAdapter(config.__dict__)` | preserved |

TDD evidence:

| Phase | Result |
|---|---|
| RED | `1 failed` on unexpected `quality_monitor` keyword argument |
| GREEN | focused provider seam test `2 passed` |
| Regression | authorized market adapter / factory regression package `18 passed` |
| Ruff | authorized files passed |

G2.208 does not edit `data_source_factory`, singleton wrapper/backing API,
route/OpenAPI, frontend, config, script, or OpenSpec surfaces.

PR `#361` merged this lane at
`90d8f12cc01f9fb360abc531673e3ed9535706e7`.

## G2.209 Data-Quality Market Data Adapter Provider Closeout / Residual Refresh

At HEAD `90d8f12cc01f9fb360abc531673e3ed9535706e7`, PR `#361` is merged and
G2.208 is accepted.

Closeout result:

| Item | Result |
|---|---|
| Target path | `web/backend/app/services/market_data_adapter.py` |
| Provider seam status | Closed |
| Constructor compatibility | `MarketDataSourceAdapter(config)` preserved |
| Injection compatibility | Keyword-only optional `quality_monitor` retained |
| Default fallback | `get_data_quality_monitor()` fallback intentionally retained |
| `data_source_factory` compatibility | `MarketDataSourceAdapter(config.__dict__)` remains compatible |

Residual classification:

| Residual surface | Classification | Handling |
|---|---|---|
| `market_data_adapter.py` fallback | Closed market-data adapter fallback | Do not reopen without contradictory current evidence |
| `adapters/dashboard_adapter.py`, `adapters/data_adapter.py` | Closed canonical service adapter fallback | Covered by G2.200/G2.201 |
| `adapters_split/base_adapter.py` | Closed adapter-split base fallback | Covered by G2.196/G2.197 |
| `_data_quality_monitor_singleton.py`, `data_quality_monitor.py` | Singleton/backing API | Retained pending a separate ownership decision |
| `data_adapter.py.backup.20260130` | Historical backup file | Separate repository hygiene authority required |

G2.209 has no source authority. It does not edit `web/backend/**`, route,
OpenAPI, frontend, config, script, or OpenSpec surfaces.

## Next Gates

- Review G2.209 `market_data_adapter.py` provider seam closeout / residual refresh.
- If accepted, start G2.210 data-quality monitor residual ownership decision with no source edits.
- Do not open the next source lane before G2.210 decides singleton/backing API and retained fallback ownership.
- Do not batch service adapters, legacy adapters, `market_data_adapter.py`, or
  singleton-wrapper migration with `adapter_split` constructor migration.
- Do not expand into alerts resolver fixes, legacy `app.api.risk_management`
  restoration, or other risk route provider migrations.

## Forbidden Scope

This track summary forbids:

- unauthorized backend source edits
- frontend edits
- test edits
- OpenSpec proposal creation
- issue label changes
- moving another service candidate directly to implementation
- treating service inventory counts as implementation backlogs
