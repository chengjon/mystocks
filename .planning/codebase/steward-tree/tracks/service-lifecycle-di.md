# Track: Service Lifecycle DI

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active track summary
- Prepared at: `2026-06-02T08:24:18+08:00`
- Base HEAD checked: `8b09c714784ce90a1a8b1fe938e5904a81110094`

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
| G2.316 indicator registry factory provider closeout / residual refresh | Future PR `#469` review target | Closes G2.315 with route-body direct calls `0`, provider backing `1`, dependency bindings `3`, route/OpenAPI `548/500/0`, and selects only G2.317 no-source `data_source_config.get_config_manager` decision |
| G2.315 indicator_registry `get_factory` provider implementation | Merged by PR `#468` | Moves 3 route handlers to `Depends(get_indicator_factory)`, keeps route/OpenAPI `548/500/0`, focused test `11 passed`, and is closed by G2.316 |
| G2.314 indicator_registry `get_factory` provider authorization | Merged by PR `#467` | Authorized only G2.315 path-limited source/test lane and required human review before source merge |
| G2.313 indicator_registry `get_factory` ownership / route-provider decision | Merged by PR `#466` | Classifies active route-local singleton factory helper with 3 route-body calls, route/OpenAPI `548/500/0`, GitNexus CLI `LOW`, and selects only G2.314 no-source provider authorization |
| G2.312 residual refresh after dormant indicator-config exclusion | Merged by PR `#465` | Excludes dormant `create_indicator_config.py` / `get_mysql_session`, records `371` Python files scanned, `663` getter names, `53` active interesting candidates, and selects G2.313 |
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

## G2.210 Data-Quality Monitor Residual Ownership Decision

At HEAD `33b6ace2f68e23bcf07a12f53511d1f7b9fb8230`, PR `#362` is merged and
G2.209 is accepted.

Decision result:

| Item | Result |
|---|---|
| Root getter | `web/backend/app/services/_data_quality_monitor_singleton.py:get_data_quality_monitor` |
| GitNexus risk | CRITICAL |
| Impacted symbols | 24 |
| Direct dependents | 20 |
| Affected processes | 7 |
| Affected modules | 4 |
| Source edit authority | None |

Residual ownership classification:

| Residual surface | Classification | Handling |
|---|---|---|
| `market_data_adapter.py` fallback | Closed market-data adapter fallback | Preserve G2.208/G2.209 closed status |
| `adapters/dashboard_adapter.py`, `adapters/data_adapter.py` | Closed canonical service adapter fallback | Preserve G2.200/G2.201 closed status |
| `adapters_split/base_adapter.py` | Closed adapter-split fallback | Preserve G2.196/G2.197 closed status |
| `_data_quality_monitor_singleton.py`, `data_quality_monitor.py` | Singleton/backing API ownership surface | Requires G2.211 authorization package |
| `data_adapter.py.backup.20260130` | Historical backup file | Separate repository hygiene authority required |

G2.210 has no source authority. It records that the remaining singleton/backing
API is a high-risk root ownership surface and must not be treated as a routine
adapter/source cleanup.

## G2.211 Data-Quality Monitor Singleton Authorization

At HEAD `619be9cac1f9516b3df42a41ca362ca9d42d5c9a`, PR `#363` is merged and
G2.210 is accepted.

Authorization result:

| Item | Result |
|---|---|
| Future lane | G2.212 data-quality monitor singleton/backing API compatibility implementation |
| Current PR source authority | None |
| Future source authority after acceptance | Yes, path-limited |
| Authorized future source paths | `web/backend/app/services/_data_quality_monitor_singleton.py`, `web/backend/app/services/data_quality_monitor.py` |
| Authorized future focused test | `web/backend/tests/test_data_quality_monitor_singleton_provider.py` |
| Route/adapters future source authority | None |

Future G2.212 constraints:

- preserve `get_data_quality_monitor()` and `monitor_data_quality()` public
  imports from `app.services.data_quality_monitor`
- preserve default singleton fallback behavior
- allow only compatibility/provider helper additions in
  `_data_quality_monitor_singleton.py`
- allow `data_quality_monitor.py` edits only for facade import / `__all__`
  maintenance
- do not migrate routes, adapters, adapter-split constructors, or
  `market_data_adapter.py`

## G2.212 Data-Quality Monitor Singleton Implementation

At HEAD `535a6d9c1565b4ced7942cb4082104f2fb0506fd`, PR `#364` is merged and
G2.211 is accepted.

Implementation result:

| Item | Result |
|---|---|
| Lane | G2.212 data-quality monitor singleton/backing API compatibility implementation |
| Source authority | Yes, path-limited |
| Source paths | `web/backend/app/services/_data_quality_monitor_singleton.py`, `web/backend/app/services/data_quality_monitor.py` |
| Focused test | `web/backend/tests/test_data_quality_monitor_singleton_provider.py` |
| Public imports preserved | `get_data_quality_monitor`, `monitor_data_quality` |
| Public hooks added | `set_data_quality_monitor_provider`, `reset_data_quality_monitor_provider` |
| Default singleton fallback | Preserved |
| Route/adapters/OpenAPI changes | None |

Verification summary:

| Check | Result |
|---|---|
| Focused provider seam test | `3 passed` |
| Authorized non-large regression set | `20 passed` |
| Large-file split regression record | `35 passed`, `4 failed` existing unrelated baseline issues |
| Ruff on touched source/test files | Passed |
| OpenSpec strict validate | Passed |

G2.212 does not close all residual ownership questions. It only gives the
remaining singleton/backing API surface a compatibility provider hook so future
lifecycle wiring can depend on an explicit seam instead of directly mutating the
module-level singleton.

## G2.213 Data-Quality Monitor Singleton Closeout / Residual Refresh

At HEAD `e7d9fe63285181f0227661628272487dc63d4e2c`, PR `#365` is merged and
G2.212 is accepted.

Residual scan:

| Metric | Count |
|---|---:|
| Active `get_data_quality_monitor` files | 7 |
| Active occurrences | 29 |
| Active calls | 7 |

Residual classification:

| Bucket | Files | Disposition |
|---|---:|---|
| Singleton/backing API seam | 2 | Closed by G2.212; retain provider/reset seam and default fallback |
| Route API provider surface | 1 | Retained active FastAPI dependency/provider surface |
| Closed canonical service adapter fallbacks | 2 | Closed by G2.200/G2.201 |
| Closed `market_data_adapter.py` facade fallback | 1 | Closed by G2.208/G2.209 |
| Closed `adapter_split` base fallback | 1 | Closed by G2.196/G2.197 |

Closeout decision:

- no new data-quality monitor source lane is selected from this refresh
- do not reopen the data-quality monitor source conveyor unless fresh
  current-HEAD evidence contradicts accepted G2.196/G2.197, G2.200/G2.201,
  G2.208/G2.209, or G2.212 evidence
- route API provider residuals remain governed by route/provider governance,
  not by a direct data-quality monitor implementation lane

## G2.214 Non-Strategy Provider Queue Refresh

At HEAD `3d3f8285f3a83cb4dda60d9b7eb8cf36fdf77117`, PR `#366` is merged and
G2.213 is accepted.

Queue refresh:

| Bucket | Items | Current handling |
|---|---:|---|
| Closed data-quality monitor | 14 | Closed by G2.213 unless fresh current-HEAD evidence contradicts |
| Excluded Strategy | 44 | Closed by G2.183 with retained residuals |
| Route provider surface | 131 | Active route/provider governance surface |
| Realtime streaming/socket | 36 | Prior realtime/socket subtrack evidence exists; do not reopen from token count alone |
| Dashboard/TDX | 11 | Direct helper debt remains closed |
| Indicator/Data | 45 | Requires current-HEAD contradiction review |
| Adapter/factory | 26 | Defer behind higher-risk current-head contradiction |
| Risk/alert | 23 | Stop-loss pair closed; broader alert surfaces deferred |
| Other service/provider | 78 | Mixed infra/control-plane/root facade queue |

Candidate impact refresh:

| Candidate | Current risk | Direct | Processes | Disposition |
|---|---:|---:|---:|---|
| `get_data_service` | CRITICAL | 3 | 7 | Select for G2.215 no-source current-HEAD contradiction / ownership decision |
| `get_execution_tracking_evidence_service` | HIGH | 2 | 3 | Defer as separate trade evidence route track |
| `get_unified_data_service` | MEDIUM | 5 | 0 | Retain as root facade pending owner-specific decision |
| `get_prewarming_strategy` | LOW | 3 | 0 | Defer as lower-risk cache prewarming route surface |

G2.214 has no source authority. It does not reopen Indicator/Data source work.
It records that current GitNexus evidence contradicts older LOW/retained
wording for `get_data_service`, so the next step must be an ownership decision
before any source authorization.

G2.214 is accepted by PR `#367`, merged at
`a508fb263173b2014d307c4baec3b1eca0f42340`.

## G2.215 Indicator/Data `get_data_service` Ownership Decision

At HEAD `a508fb263173b2014d307c4baec3b1eca0f42340`, PR `#367` is merged and
G2.214 is accepted.

Current evidence:

| Evidence | Value |
|---|---:|
| GitNexus risk | `CRITICAL` |
| GitNexus direct callers | 3 |
| Affected processes | 7 |
| Affected modules | 2 |
| Static direct `get_data_service()` source calls | 2 |

Ownership classification:

| Surface | Files | Current decision |
|---|---|---|
| `DataService` singleton/backing API | `web/backend/app/services/data_service.py` | Retain; requires a later authorization package before source edits |
| Indicator route dependency provider | `web/backend/app/api/indicators/indicator_cache.py` | Active FastAPI provider surface; not direct route-body singleton debt |
| Strategy technical-indicator route dependency provider | `web/backend/app/api/v1/strategy/indicators.py` | Route/provider surface only; do not reopen closed Strategy getter residuals |
| Indicator helper call chain | `web/backend/app/api/indicators/indicator_cache.py` | Graph participant receiving injected `data_service`; not a separate direct getter call site |

Decision:

- G2.215 supersedes older LOW/retained wording for `get_data_service`.
- The CRITICAL graph impact is accepted as route/process-level risk.
- The current source shape is provider-wrapper based, so this is not a direct
  route-body singleton cleanup.
- G2.215 has no source authority and selects no implementation lane.
- G2.215 was accepted by PR `#368`; the next gate is G2.216 indicator/data
  `DataService` singleton provider authorization package, also no-source.

## G2.216 Indicator/Data DataService Provider Authorization

G2.216 uses the refreshed isolated worktree GitNexus index after PR `#368`
merged at `cec3f727534008d2a48221c656c22f82f351e3d7`.

Current evidence:

| Metric | Value |
|---|---:|
| GitNexus risk | `LOW` |
| GitNexus direct callers | 2 |
| Affected processes | 0 |
| Affected modules | 0 |
| Static direct `get_data_service()` source calls | 2 |

Direct callers:

| Caller | File | Current role |
|---|---|---|
| `get_indicator_data_service` | `web/backend/app/api/indicators/indicator_cache.py` | Indicator route-local provider wrapper |
| `get_strategy_indicator_data_service` | `web/backend/app/api/v1/strategy/indicators.py` | Strategy technical-indicator route-local provider wrapper |

Authorization proposal:

- G2.216 was accepted by PR `#369`; G2.217 may edit only
  `web/backend/app/services/data_service.py` plus a focused
  `web/backend/tests/test_data_service_singleton_provider.py`.
- Future G2.217 must preserve `get_data_service()` as the public default
  singleton fallback.
- Future G2.217 may add provider registration and reset helpers modelled on the
  accepted data-quality monitor provider/reset seam.
- Future G2.217 must run route-provider regressions for
  `web/backend/tests/test_indicator_registry_route_provider.py` and
  `web/backend/tests/test_v1_indicators_regressions.py`.
- G2.216 itself had no source authority and made no runtime change.

## G2.217 Indicator/Data DataService Provider/Reset Seam

G2.217 implements the path-limited source lane authorized by G2.216 after PR
`#369` merged at `68ba10829b89095f8b907d249f59198995543ebc`.

Pre-edit GitNexus impact for `get_data_service`:

| Metric | Value |
|---|---:|
| GitNexus risk | `LOW` |
| GitNexus direct callers | 2 |
| Affected processes | 0 |
| Affected modules | 0 |

Implementation surface:

| File | Change |
|---|---|
| `web/backend/app/services/data_service.py` | Adds `_data_service_provider`, `set_data_service_provider()`, and `reset_data_service_provider()` while preserving `get_data_service()` default singleton fallback |
| `web/backend/tests/test_data_service_singleton_provider.py` | Covers provider override and reset-to-default singleton behavior |

Verification evidence:

| Check | Result |
|---|---|
| Red provider test | Expected `ImportError` before implementation |
| Focused provider test | `2 passed` |
| Indicator route provider regression | `3 passed` |
| v1 indicator route regression | `3 passed` |

GitNexus staged scope reports `high` risk because file-level attribution marks
existing `data_service.py` methods as modified. The cached source diff is
localized to the typing import, provider/reset helpers, and the provider branch
inside `get_data_service()`.

G2.217 does not edit route wrappers, route/OpenAPI contracts, Strategy residuals,
data-quality monitor source, trade/cache/realtime providers, `adapter_split`, or
`market_data_adapter.py`.

## G2.218 DataService Provider/Reset Seam Closeout / Residual Refresh

G2.218 closes the accepted G2.217 source lane after PR `#370` merged at
`4d2b69e449975d145976e10c8af965e16dc60a1e`. This is a no-source closeout and
residual refresh package.

Current evidence:

| Check | Result |
|---|---|
| Import smoke | `import_smoke=pass provider_override=pass reset_default=pass` |
| Focused provider test | `2 passed` |
| Indicator route provider regressions | `6 passed` |
| Ruff | passed |
| OpenSpec strict validate | valid |

`get_data_service` residual classification:

| Surface | Current state | Decision |
|---|---|---|
| Direct singleton wrapper calls | 2 route-local provider wrappers in `indicator_cache.py` and `v1/strategy/indicators.py` | Retain as provider wrappers |
| Canonical function definition | `web/backend/app/services/data_service.py` | Closed by G2.217 provider/reset seam |
| Local helper names / imports | `ml_runtime_helpers.py`, `v1/system/health.py` | Not `app.services.data_service.get_data_service()` residuals |

Residual queue after closing `get_data_service`:

| Candidate | Current scan | Classification | Disposition |
|---|---:|---|---|
| `get_execution_tracking_evidence_service` | 3 calls in 2 files | trade evidence route-local provider surface | Select G2.219 no-source ownership decision |
| `get_unified_data_service` | 6 calls in 1 file | root facade / compatibility surface | Defer behind trade evidence ownership decision |
| `get_prewarming_strategy` | 6 calls in 3 files | cache prewarming route/provider surface | Defer behind higher-risk trade/root-facade decisions |

G2.218 does not authorize backend source edits, test edits, OpenSpec changes,
route/OpenAPI changes, issue label changes, or direct implementation for the
next candidate.

## G2.219 Trade Execution Tracking Evidence Provider Ownership

G2.219 is a no-source ownership decision package after PR `#371` merged at
`d4ee917ad642939c4c60000998b8bea5ca7c9a65`.

Target:

| Item | Value |
|---|---|
| Symbol | `get_execution_tracking_evidence_service` |
| File | `web/backend/app/api/trade/execution_tracking_routes.py:289` |
| Current shape | route-local factory for `ExecutionTrackingEvidenceService` |
| Current injection style | direct route-module helper calls; no FastAPI `Depends` usage |

Current evidence:

| Check | Result |
|---|---|
| GitNexus impact | `HIGH`, 2 direct callers, 3 affected processes, Trade module |
| Focused trade execution route tests | `4 passed` |
| Ruff on route/test files | passed |
| OpenSpec strict validate | valid |
| app.main/OpenAPI smoke | environment-blocked by missing required env vars |

Ownership decision:

`get_execution_tracking_evidence_service` is a trade execution tracking
route/provider ownership surface, not a generic service singleton cleanup
candidate. The existing route-local helper and test monkeypatch seam are
evidence for possible injection, not implementation authorization.

G2.219 selects G2.220 as a no-source authorization package to define whether a
later path-limited implementation should convert list/detail direct provider
calls to explicit route dependency/provider injection.

## G2.220 Trade Execution Tracking Evidence Provider Authorization

G2.220 is a no-source authorization package after PR `#372` merged at
`b51256b775f7b4c6e5baad8c82a7f86446c0151b`.

Authorization decision:

| Item | Value |
|---|---|
| G2.220 source authority | none |
| Conditional next implementation | G2.221 only after review acceptance |
| Allowed implementation source path | `web/backend/app/api/trade/execution_tracking_routes.py` |
| Allowed implementation test path | `web/backend/tests/test_trade_execution_tracking_routes.py` |
| Out of scope | `trigger_external_execution`, miniQMT semantics, response contracts, request schemas |

Authorized future G2.221 pattern, if this package is accepted:

- preserve `get_execution_tracking_evidence_service` as the default provider factory
- add explicit route dependency/provider injection for execution tracking list/detail flows
- pass the injected evidence service into `_load_execution_records`
- inject the evidence service into `get_execution_tracking_detail`
- update focused tests to use FastAPI dependency override or an equivalent explicit injection seam

Contract invariants:

- no route path changes
- no `response_model` changes
- no `UnifiedResponse` envelope changes
- no request schema changes
- no miniQMT evidence semantic changes
- no `broker_state` or bridge evidence interpretation changes

Pre-implementation gates for a later G2.221 lane:

- rerun GitNexus impact before source edits
- rerun app.main/OpenAPI smoke after source edits before claiming implementation complete
- run focused execution tracking route tests before and after edits
- run ruff on the touched route/test pair
- keep staged scope limited to the authorized route/test pair plus governance evidence

G2.220 baseline app.main/OpenAPI smoke passed with transient runtime
environment: `route_count=548`, `openapi_paths=500`. Secret values were not
persisted in repository files or recorded in this track summary.

## G2.221 Trade Execution Tracking Evidence Provider Injection

G2.221 is the path-limited source implementation after PR `#373` merged at
`3d2dc3e8204388cc157c23df59f584a3efb268fe`.

Implementation result:

| Item | Value |
|---|---|
| Source path | `web/backend/app/api/trade/execution_tracking_routes.py` |
| Test path | `web/backend/tests/test_trade_execution_tracking_routes.py` |
| Provider factory | `get_execution_tracking_evidence_service` retained |
| List route | uses `Depends(get_execution_tracking_evidence_service)` |
| Detail route | uses `Depends(get_execution_tracking_evidence_service)` |
| Helper seam | `_load_execution_records` receives injected `evidence_service` |
| Trigger route | unchanged / out of scope |

TDD and verification:

| Check | Result |
|---|---|
| GitNexus pre-edit impact | `HIGH`, 2 direct callers, 3 affected processes |
| TDD red | dependency override test failed before source edit |
| TDD green | dependency override test passed after source edit |
| Focused route tests | `4 passed` |
| Ruff | passed |
| app.main/OpenAPI smoke | passed, `route_count=548`, `openapi_paths=500`, duplicate operation IDs `0` |

Contract invariants preserved:

- no route path changes
- no `response_model` changes
- no `UnifiedResponse` envelope changes
- no request schema changes
- no miniQMT evidence semantic changes
- no `broker_state` or bridge evidence interpretation changes

## G2.222 Trade Execution Tracking Provider Closeout

G2.222 is a no-source closeout / residual refresh after PR `#374` merged at
`14339f44a8c4a145615fe35836dec8fc376ce75b`.

Closeout result:

| Evidence | Count |
|---|---:|
| `get_execution_tracking_evidence_service` total hits | 3 |
| Provider factory definition | 1 |
| FastAPI `Depends(...)` bindings | 2 |
| Route-body direct provider calls | 0 |

Decision: the execution tracking provider seam is closed. The remaining factory
definition is intentional because it is the FastAPI dependency target and test
override key.

Verification:

| Check | Result |
|---|---|
| Focused route tests | `4 passed` |
| Ruff | passed |
| app.main/OpenAPI smoke | passed, `route_count=548`, `openapi_paths=500`, duplicate operation IDs `0`, duplicate operation ID warnings `0`; Python smoke captured `121` existing dependency/schema deprecation warnings |
| OpenSpec strict validate | valid, with PostHog telemetry noise |

Remaining provider queue after G2.222:

| Candidate | Risk | Direct callers | Processes affected | Classification | Disposition |
|---|---|---:|---:|---|---|
| `get_unified_data_service` | MEDIUM | 5 | 0 | root facade / compatibility service surface | Select G2.223 no-source ownership decision |
| `get_prewarming_strategy` | LOW | 3 | 0 | cache prewarming route/provider surface | Defer behind unified data service ownership decision |

## G2.223 Unified Data Service Ownership Decision

G2.223 is a no-source ownership decision after PR `#375` merged G2.222 at
`e7402fffe29bee5f7f2a4ada5a60a4bf26876969`.

Current-HEAD evidence:

| Evidence | Value |
|---|---:|
| GitNexus risk | MEDIUM |
| Direct graph callers | 5 |
| Processes affected | 0 |
| `get_unified_data_service` / `UnifiedDataService` text hits in `web/backend/app` | 12 |
| Files with hits | 2 |
| Route-body direct `get_unified_data_service()` calls | 0 |
| Route-layer direct `UnifiedDataService()` instantiations | 2 |

Classification:

- `web/backend/app/services/unified_data_service.py` owns the lazy singleton and
  five same-file facade helpers.
- `web/backend/app/api/industry_concept_analysis.py` owns two direct
  `UnifiedDataService()` instantiations where the result is not assigned.
- Those route-layer instantiations are a separate route cleanup / contract
  candidate, not a direct `get_unified_data_service` implementation lane.

Decision: do not start a direct implementation lane for
`get_unified_data_service`. Select G2.224 as a no-source authorization package
for the `industry_concept_analysis.py` direct `UnifiedDataService()`
instantiation cleanup candidate.

## G2.224 Industry/Concept UnifiedDataService Cleanup Authorization

G2.224 is a no-source authorization package after PR `#376` merged G2.223 at
`5eef37a097d55d209a69485bc29e89dd3aeb4076`.

Authorization evidence:

| Evidence | Value |
|---|---:|
| Candidate source file | `web/backend/app/api/industry_concept_analysis.py` |
| Direct unassigned `UnifiedDataService()` calls | 2 |
| Import candidate | line `26` |
| Target no-op call lines | `224`, `277` |
| Target routes | `/api/analysis/industry/list`, `/api/analysis/concept/list` |
| Target response models | `IndustryListResponse`, `ConceptListResponse` |
| Exact route graph incoming callers | 0 for both target route functions |
| Focused endpoint metadata test | `1 passed` |
| Ruff target check | passed |

Decision: authorize G2.225 as a future path-limited source lane if the
maintainer accepts G2.224. G2.225 may remove only the two unassigned
`UnifiedDataService()` calls and the now-unused import. It must preserve route
paths, response models, OpenAPI exposure, SQL queries, `get_postgresql_engine`,
error-contract behavior, `UnifiedDataService`, `get_unified_data_service`, and
cache prewarming provider work.

## G2.225 Industry/Concept UnifiedDataService Cleanup Implementation

G2.225 is a path-limited source implementation after PR `#377` merged G2.224 at
`36c38fbf233945b7e45ed67b50591665942d4b32`.

Implementation evidence:

| Evidence | Value |
|---|---:|
| Candidate source file | `web/backend/app/api/industry_concept_analysis.py` |
| Direct unassigned `UnifiedDataService()` calls before | 2 |
| Direct unassigned `UnifiedDataService()` calls after | 0 |
| `UnifiedDataService` import after | removed |
| `web/backend/app` text hits after | 9 |
| Target routes | `/api/analysis/industry/list`, `/api/analysis/concept/list` |
| Target response models | `IndustryListResponse`, `ConceptListResponse` |
| GitNexus exact route graph incoming callers | 0 for both target route functions |
| GitNexus file impact | LOW, 0 impacted symbols / 0 affected processes |
| TDD red | failed before source edit on `UnifiedDataService()` |
| TDD green | `1 passed` |
| Focused endpoint tests | `2 passed` |
| app.main / OpenAPI smoke | `routes=548`, `paths=500`, both target paths present |

Decision: G2.225 implements only the G2.224-authorized no-op constructor cleanup
and adds a focused regression test. It does not authorize edits to
`get_unified_data_service`, cache prewarming, route paths, response models,
OpenAPI exposure, SQL queries, error-contract behavior, frontend code, or
OpenSpec specs.

## G2.226 Industry/Concept UnifiedDataService Cleanup Closeout / Refresh

G2.226 is a no-source closeout / residual refresh after PR `#378` merged G2.225
at `5837b8af55499e8ee9d7ba14cf543abb9bc45e39`.

Closeout evidence:

| Evidence | Value |
|---|---:|
| Direct `UnifiedDataService()` calls in `industry_concept_analysis.py` | 0 |
| `UnifiedDataService` import in `industry_concept_analysis.py` | absent |
| Remaining unified-data hits in `web/backend/app` | 9 |
| Remaining unified-data hit files | `web/backend/app/services/unified_data_service.py` only |
| Focused regression test | `1 passed` |
| Ruff target check | passed |
| app.main / OpenAPI smoke | `routes=548`, `paths=500`, both target paths present |

Residual refresh:

| Candidate | Risk | Direct callers | Processes affected | Classification | Disposition |
|---|---|---:|---:|---|---|
| `get_prewarming_strategy` | LOW | 3 | 0 | cache prewarming route/provider surface | Select G2.227 no-source ownership decision |

Decision: G2.226 closes the industry/concept route cleanup target and selects
G2.227 as a future no-source ownership decision for `get_prewarming_strategy`.
It does not authorize cache prewarming source edits or route/OpenAPI changes.

## G2.227 Cache Prewarming Strategy Ownership Decision

G2.227 is a no-source ownership decision after PR `#379` merged G2.226 at
`854878cd2e09384daddaa8547e8cebc970ec2b74`.

Ownership evidence:

| Evidence | Value |
|---|---:|
| Candidate symbol | `get_prewarming_strategy` |
| Definition | `web/backend/app/core/cache_prewarming.py:306` |
| Text hits | 9 |
| Route-body direct getter calls | 3 |
| GitNexus risk | LOW |
| Direct callers | 3 |
| Processes affected | 0 |
| Focused cache tests | `54 passed` |
| app.main / OpenAPI smoke | `routes=548`, `paths=500`, cache prewarming paths present |

Decision: classify `get_prewarming_strategy` as a cache prewarming route/provider
surface, not generic singleton deletion. Select G2.228 as a future no-source
authorization package for a path-limited implementation candidate. G2.227 does
not authorize cache prewarming source edits.

## G2.228 Cache Prewarming Strategy Provider Authorization

G2.228 is a no-source authorization package after PR `#380` merged G2.227 at
`f2b528e5feaf7fd89f19a857e75a3c3442ba9c6b`.

Authorization evidence:

| Evidence | Value |
|---|---:|
| Candidate symbol | `get_prewarming_strategy` |
| Definition | `web/backend/app/core/cache_prewarming.py:306` |
| Current hit files | 3 |
| Route-body direct getter calls | 3 |
| GitNexus risk | LOW |
| Direct callers | 3 |
| Processes affected | 0 |
| Focused cache tests | `54 passed` |
| app.main / OpenAPI smoke | `routes=548`, `paths=500`, cache prewarming paths present |

Decision: authorize a future G2.229 path-limited implementation lane that may
replace route-body direct `get_prewarming_strategy()` calls with an explicit
route dependency/provider parameter in
`web/backend/app/api/_cache_prewarming_routes.py`. G2.228 itself does not
authorize source edits. Future tests, if G2.229 starts, are limited to
`web/backend/tests/test_cache_api.py` and
`web/backend/tests/test_cache_prewarming.py`.

## G2.229 Cache Prewarming Route DI Implementation

G2.229 is a path-limited source implementation after PR `#381` merged G2.228 at
`4d77ee68a1a4a30516134b995c82fa777c3b44d6`.

Implementation evidence:

| Evidence | Value |
|---|---:|
| Route file | `web/backend/app/api/_cache_prewarming_routes.py` |
| Focused test file | `web/backend/tests/test_cache_api.py` |
| Target route handlers | 3 |
| Route-body direct getter calls before | 3 |
| Route-body direct getter calls after | 0 |
| Injected dependency parameters after | 3 |
| TDD red guard | failed before implementation |
| TDD green guard | `1 passed` |
| Focused cache tests | `55 passed` |
| app.main / OpenAPI smoke | `routes=548`, `paths=500`, cache prewarming paths present |

Decision: G2.229 implements the G2.228-authorized provider lane by injecting
`CachePrewarmingStrategy` into `trigger_cache_prewarming`,
`get_prewarming_status`, and `get_cache_health_status` via
`Depends(get_prewarming_strategy)`. Route paths, auth, response shape, OpenAPI
exposure, `get_prewarming_strategy`, `CachePrewarmingStrategy`, and
`get_cache_monitor` behavior remain unchanged.

## G2.230 Cache Prewarming Route DI Closeout / Refresh

G2.230 is a no-source closeout / residual refresh after PR `#382` merged G2.229
at `4a0e41eac399e052ed3ebc9facc7dbf08761ab0a`.

Closeout evidence:

| Evidence | Value |
|---|---:|
| Route-body direct `get_prewarming_strategy()` calls | 0 |
| `Depends(get_prewarming_strategy)` uses | 3 |
| Typed `prewarming_strategy` parameters | 3 |
| Focused cache tests | `55 passed` |
| Ruff target files | passed |
| app.main / OpenAPI smoke | `routes=548`, `paths=500`, cache prewarming paths present |

Decision: close the cache prewarming route/provider surface. Do not reopen cache
prewarming source work unless current HEAD evidence contradicts this closeout.
Select G2.231 no-source service lifecycle residual candidate refresh as the next
gate before choosing another source lane.

## G2.231 Service Lifecycle Residual Candidate Refresh

G2.231 is a no-source residual candidate refresh after PR `#383` merged G2.230
at `2652d59b02dedaecd4ac05a2f95fce8ab4ae2e3c`.

Refresh evidence:

| Evidence | Value |
|---|---:|
| Service-suffix API getter groups | 4 |
| Broader non-method `get_*()` API groups | 62 |
| Active `data_source_config.py` `get_config_manager()` calls | 9 |
| Legacy `data_source_config.old.py` false-positive calls | 8 |
| `get_config_manager` GitNexus risk | HIGH |
| `get_config_manager` direct callers | 9 |
| `get_config_manager` affected processes | 3 |

Decision: select G2.232 data-source config manager provider seam decision /
authorization as the next no-source gate. G2.231 does not authorize backend
source edits. The G2.232 packet should classify active route truth separately
from `data_source_config.old.py` false positives and decide whether a future
path-limited provider injection lane is allowed.

## G2.232 Data-Source Config Manager Provider Authorization

G2.232 is a no-source authorization package after PR `#384` merged G2.231 at
`05c84d1f4f5e42d9db0ace21ef3ba110dacbc184`.

Authorization evidence:

| Evidence | Value |
|---|---:|
| Candidate symbol | `get_config_manager` |
| Active route file | `web/backend/app/api/data_source_config.py` |
| Active route-body calls | 9 |
| Legacy `.old.py` false-positive calls | 8 |
| GitNexus risk | HIGH |
| GitNexus direct callers | 9 |
| GitNexus affected processes | 3 |

Decision: authorize future G2.233 path-limited provider injection for active
`data_source_config.py` route handlers. G2.232 itself remains no-source. Future
G2.233 source scope is limited to `data_source_config.py` plus focused tests and
must preserve route paths, auth/current_user behavior, response models, OpenAPI
exposure, and the default backing `get_config_manager()` behavior. Do not edit
`data_source_config.old.py`.

## G2.233 Data-Source Config Manager Provider Injection

G2.233 is the path-limited implementation after PR `#385` merged G2.232 at
`1f63a46657858920a3df9799ffc0c45ccf3b3dd8`.

Implementation evidence:

| Evidence | Value |
|---|---:|
| Active route file | `web/backend/app/api/data_source_config.py` |
| Active route handlers changed | 9 |
| Active route-body `get_config_manager()` calls before | 9 |
| Active route-body `get_config_manager()` calls after | 0 |
| Active `manager` dependency parameters after | 9 |
| Route-local provider wrapper | `get_config_manager_dependency` |
| Legacy `.old.py` edited | No |
| `_data_source_config_responses.py` edited | No |

Verification evidence:

| Check | Result |
|---|---|
| TDD RED | `web/backend/tests/test_data_source_config_provider_injection.py`: 2 failed before implementation |
| TDD GREEN | `web/backend/tests/test_data_source_config_provider_injection.py`: 2 passed |
| Focused route contract tests | `tests/api/file_tests/test_data_source_config_api.py` + `web/backend/tests/test_data_source_config_provider_injection.py`: 12 passed |
| Ruff | Passed |
| app/OpenAPI smoke | `routes=548`, `paths=500` |

Decision: mark the active data-source config manager route-body provider
migration as implemented for review. If accepted, G2.234 should be a no-source
closeout / residual refresh that confirms post-merge state and selects the next
candidate without opening source edits directly.

## G2.234 Data-Source Config Manager Provider Closeout / Residual Refresh

G2.234 is the no-source closeout / residual refresh after PR `#386` merged G2.233
at `875b57fd2b61dd3f4b5b26e95ea5b31ddc0b6d8f`.

Closeout evidence:

| Evidence | Value |
|---|---:|
| Active route file | `web/backend/app/api/data_source_config.py` |
| Active route-body `get_config_manager()` calls | 0 |
| Active `manager` dependency parameters | 9 |
| Route-local provider wrapper definitions | 1 |
| Legacy `.old.py` text hits | 9 |
| Legacy `.old.py` registered | No |
| Focused route contract tests | 12 passed |
| Ruff | Passed |
| app/OpenAPI smoke | `routes=548`, `paths=500` |

Decision: close the active data-source config manager route-body provider
migration. Do not reopen `data_source_config.py` source work unless current HEAD
evidence contradicts this closeout. Select G2.235 no-source service lifecycle
residual candidate refresh as the next gate before any new source lane starts.

## G2.235 Service Lifecycle Residual Candidate Refresh After Data-Source Config Manager

G2.235 is the no-source residual candidate refresh after PR `#387` merged G2.234
at `659a1dffb1d1306c8fe09ce2bdd9e17ab87dd8a5`.

Refresh evidence:

| Evidence | Value |
|---|---:|
| Python files scanned | 1500 |
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| Active route-body `get_config_manager()` calls | 0 |
| `get_config_manager_dependency` backing calls | 1 |
| Active `manager` dependency parameters | 9 |
| Legacy `.old.py` direct call expressions | 8 |
| `get_calculator_factory` active API call expressions | 8 |
| `get_mock_data_manager` call expressions | 24 |
| `get_monitoring_db` call expressions | 12 |
| `get_postgres_async` call expressions | 30 |

Candidate queue:

| Rank | Candidate | Classification | Disposition |
|---:|---|---|---|
| 1 | `get_calculator_factory` | Monitoring portfolio domain factory ownership seam; GitNexus sample HIGH, 9 direct, 3 affected processes, 2 modules | Select G2.236 no-source monitoring calculator factory ownership / provider seam decision packet |
| 2 | `get_mock_data_manager` | Cross-domain mock/runtime seam; GitNexus sample CRITICAL, 27 direct, 4 processes, 8 modules | Defer to separate design package |
| 3 | `get_monitoring_db` | Multi-definition monitoring/risk/strategy seam | Defer until ownership classification |
| 4 | `get_postgres_async` | Infrastructure data-access singleton | Defer outside direct service lifecycle pilot queue |

Decision: select G2.236 as a no-source monitoring calculator factory ownership
/ provider seam decision packet. G2.235 does not authorize source edits,
route/OpenAPI changes, test edits, OpenSpec changes, issue label movement, or
PM2 commands.

## G2.236 Monitoring Calculator Factory Ownership / Provider Seam Decision

G2.236 is the no-source ownership / provider seam decision after PR `#388`
merged G2.235 at `383598ab2a30da31513468b97537183322b46af9`.

Ownership evidence:

| Evidence | Value |
|---|---:|
| Domain definition | `src/monitoring/domain/calculator_factory.py:339` |
| Domain internal helper call | `src/monitoring/domain/calculator_factory.py:364` |
| Active API route-body factory calls | 8 |
| Active route files | 2 |
| OpenAPI included factory-backed routes | 8 |
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| Focused monitoring API tests | 16 passed |
| Health route conflict collect | 121 tests collected |
| GitNexus sample risk | HIGH |
| GitNexus sample direct impact | 9 |
| GitNexus sample affected processes | 3 |

Active route consumer matrix:

| File | Handler count | Direct calls | Decision |
|---|---:|---:|---|
| `web/backend/app/api/_monitoring_portfolio_router.py` | 3 | 3 | Future route/API provider seam candidate only after separate authorization |
| `web/backend/app/api/monitoring_analysis.py` | 5 factory-backed handlers; `get_health_score_history` is not a factory consumer | 5 | Future route/API provider seam candidate only after separate authorization |
| `src/monitoring/domain/calculator_factory.py` | 1 domain helper call | 1 | Retain; not a route-provider migration target |

Decision: `get_calculator_factory` remains owned by the monitoring domain
factory. The active migration concern is an API route/provider seam, not a
domain factory rewrite. G2.236 was accepted by PR `#389`, enabling G2.237 as a
separate no-source monitoring calculator factory provider authorization packet.
G2.236 does not authorize source implementation.

## Next Gates

- Review G2.237 monitoring calculator factory provider authorization.
- Only if G2.237 is accepted, create G2.238 as a path-limited source
  implementation lane.
- Do not start source implementation from G2.237.
- Do not reopen cache prewarming source work without contradictory current-HEAD
  evidence.
- Do not edit `data_source_config.old.py` from G2.234.
- Do not edit `_data_source_config_responses.py` from G2.233 unless a later
  package explicitly authorizes response/dependency separation.
- Do not expand into route paths, response models, SQL queries, error-contract
  behavior, `get_unified_data_service`, or frontend code.
- Do not open another data-quality monitor source lane unless fresh current-HEAD evidence contradicts the accepted closeout.
- Do not batch service adapters, legacy adapters, `market_data_adapter.py`, or
  singleton-wrapper migration with `adapter_split` constructor migration.
- Do not expand into alerts resolver fixes, legacy `app.api.risk_management`
  restoration, or other risk route provider migrations.

## G2.237 Monitoring Calculator Factory Provider Authorization

G2.237 is the no-source authorization packet after PR `#389` merged G2.236 at
`f39aca8815d59739787349ed1025e7a1b7e2c050`.

Authorization boundary:

| Item | Decision |
|---|---|
| Source authority now | No |
| Future lane if accepted | G2.238 monitoring calculator factory provider injection |
| Future source paths | `web/backend/app/api/monitoring_analysis.py`, `web/backend/app/api/_monitoring_portfolio_router.py` |
| Future test path | `tests/api/file_tests/test_monitoring_analysis_api.py` |
| Verification-only path | `web/backend/tests/test_health_route_conflicts.py` |
| Domain factory rewrite | Not authorized |
| New shared helper file | Not authorized without a new decision |

Recommended future shape:

- Add explicit route dependency provider(s), recommended name
  `get_monitoring_calculator_factory`.
- Keep domain import lazy inside provider unless fresh startup evidence proves
  a module-level import is safe.
- Replace the 8 route-body `get_calculator_factory()` calls with
  `Depends(get_monitoring_calculator_factory)` parameters.
- Preserve all route paths, response models, `UnifiedResponse` contracts,
  OpenAPI exposure, and `HealthCalculatorFactory` behavior.

GitNexus risk signal for the underlying symbol remains HIGH: CLI fallback
reported 9 impacted symbols, 9 direct references, 3 affected processes, and 2
affected modules. Future implementation must rerun impact/context before edits
and staged/compare detect after edits.

Next gate:

- Review G2.237.
- If accepted, create G2.238 as the bounded implementation lane.
- Do not edit source from G2.237.

## G2.238 Monitoring Calculator Factory Provider Injection

G2.238 is the path-limited implementation lane after PR `#390` merged G2.237 at
`ef11ae6577bf62d15b814af732ba291696e5b084`.

Implementation result:

| Item | Result |
|---|---:|
| Route-local providers added | 2 |
| Target handlers | 8 |
| Direct route-body `get_calculator_factory()` calls after | 0 |
| FastAPI dependency parameters after | 8 |
| Focused monitoring API tests | 17 passed |
| Health route conflict collect | 121 tests collected |
| app/OpenAPI smoke | `routes=548`, `paths=500` |

Changed source/test paths:

- `web/backend/app/api/monitoring_analysis.py`
- `web/backend/app/api/_monitoring_portfolio_router.py`
- `tests/api/file_tests/test_monitoring_analysis_api.py`

Preserved boundaries:

- `src/monitoring/domain/calculator_factory.py` unchanged.
- Route paths, response models, OpenAPI exposure, and `UnifiedResponse`
  contracts unchanged.
- Calculator construction and GPU/CPU/risk selection behavior unchanged.
- `get_mock_data_manager`, `get_monitoring_db`, and `get_postgres_async`
  remained out of scope.

Closeout status:

- G2.238 was accepted by PR `#391` and merged at
  `fd9efeefc31cdbe5aa702b47f736b5bc8b9d4bea`.
- G2.239 is the no-source closeout / residual refresh for this provider lane.
- Do not expand G2.238 into another source lane.

## G2.239 Monitoring Calculator Factory Provider Closeout / Residual Refresh

G2.239 is the no-source closeout / residual refresh after PR `#391` merged
G2.238 at `fd9efeefc31cdbe5aa702b47f736b5bc8b9d4bea`.

Closeout result:

| Item | Result |
|---|---:|
| Route-local providers present | 2 |
| Target handlers | 8 |
| Direct route-body `get_calculator_factory()` calls | 0 |
| FastAPI dependency parameters | 8 |
| Focused monitoring API tests | 17 passed |
| Health route conflict collect | 121 tests collected |
| app/OpenAPI smoke | `routes=548`, `paths=500` |

Preserved boundaries:

- No source, test, route, OpenAPI, frontend, config, scripts, or OpenSpec files
  are modified by G2.239.
- `src/monitoring/domain/calculator_factory.py` remains a monitoring domain
  factory and is not rewritten.
- `get_mock_data_manager`, `get_monitoring_db`, and `get_postgres_async`
  remain outside this lane.

Residual refresh decision:

- Close the monitoring calculator factory route-body provider migration unless
  current-HEAD evidence contradicts the closeout.
- Select G2.240 no-source service lifecycle residual candidate refresh as the
  next gate before any new source lane starts.
- G2.239 itself does not authorize source implementation.

Closeout status:

- G2.239 was accepted by PR `#392` and merged at
  `d68c381d75cf9dffc601ef8390fbec9c85e55d18`.
- G2.240 is the no-source residual candidate refresh after this closeout.

## G2.240 Service Lifecycle Residual Candidate Refresh After Monitoring Calculator

G2.240 is the no-source candidate refresh after PR `#392` merged G2.239 at
`d68c381d75cf9dffc601ef8390fbec9c85e55d18`.

Current carry-forward:

| Item | Result |
|---|---:|
| `get_calculator_factory` active route-body calls | 0 |
| `get_calculator_factory` provider wrapper calls | 2 |
| `get_calculator_factory` domain-internal calls | 1 |
| Python files scanned | 1500 |
| app/OpenAPI smoke target | `routes=548`, `paths=500` |

Candidate queue:

| Rank | Candidate | Classification | Current evidence | Recommendation |
|---:|---|---|---|---|
| 1 | `get_mock_data_manager` | Cross-domain mock/runtime data seam | 1 definition, 16 import lines, 27 call expressions; GitNexus CLI sample `CRITICAL`, 63 impacted, 27 direct, 4 processes, 8 modules | Select G2.241 no-source ownership / runtime seam decision |
| 2 | `get_postgres_async` | Infrastructure data-access singleton | 1 definition, 28 import lines, 30 call expressions, 3 active route-body calls; GitNexus CLI sample `LOW` | Defer behind infrastructure ownership classification |
| 3 | `get_monitoring_db` | Multi-definition monitoring/risk/strategy seam | 3 definitions, 12 call expressions; GitNexus CLI sample ambiguous | Defer until disambiguation and ownership classification |

Decision:

- G2.240 does not authorize implementation.
- Select G2.241 as a no-source `get_mock_data_manager` ownership / runtime seam
  decision packet.
- Keep `get_postgres_async` and `get_monitoring_db` out of G2.241 except as
  explicit non-target boundaries.

Closeout status:

- G2.240 was accepted by PR `#393` and merged at
  `70d75e77fa28fa8b9931fcdc4e89688478f8f1fc`.
- G2.241 is the no-source ownership / runtime seam decision after this refresh.

## G2.241 Mock Data Manager Ownership / Runtime Seam Decision

G2.241 is the no-source decision packet after PR `#393` merged G2.240 at
`70d75e77fa28fa8b9931fcdc4e89688478f8f1fc`.

Ownership decision:

- `get_mock_data_manager` is a mock data runtime facade and compatibility
  accessor.
- It is not a route dependency provider, deletion candidate, thin wrapper, or
  single-consumer source pilot.
- Future work should preserve the compatibility accessor and first introduce an
  explicit provider/reset/test-double seam only after a separate authorization.

Current evidence:

| Item | Result |
|---|---:|
| Definition count | 1 |
| Primary file | `web/backend/app/mock/mock_data/factory.py` |
| Import lines | 16 |
| Call expressions | 27 |
| Active route-body calls | 0 |
| GitNexus CLI sample | `CRITICAL`, 63 impacted, 27 direct, 4 processes, 8 modules |

Consumer matrix:

| Bucket | Calls | Files | Handling |
|---|---:|---:|---|
| API/helper fallback consumers | 8 | 6 | Preserve as consumers; do not batch-migrate from G2.241 |
| Mock factory / fixture helpers | 9 | 2 | Owner surface for future provider/reset seam |
| Active service adapters | 3 | 3 | Do not rewrite from G2.241 |
| Legacy/facade adapters | 3 | 3 | Defer behind future authorization |
| Tests | 4 | 3 | Preserve as verification consumers |

Next gate:

- If accepted, start G2.242 no-source mock data manager provider/reset seam
  authorization.
- G2.241 does not authorize source edits.

Closeout status:

- G2.241 was accepted by PR `#394` and merged at
  `cb0e7cd605e2828c495e3f31433ad1b8b6a3d64c`.
- G2.242 is the no-source provider/reset seam authorization after this
  decision.

## G2.242 Mock Data Manager Provider / Reset Seam Authorization

G2.242 is the no-source authorization packet after PR `#394` merged G2.241 at
`cb0e7cd605e2828c495e3f31433ad1b8b6a3d64c`.

Authorization decision:

- G2.242 does not authorize source edits.
- If accepted, it authorizes a future G2.243 source lane limited to adding an
  explicit provider/reset/test-double seam around `get_mock_data_manager`.
- The compatibility accessor, default cached manager behavior, fallback manager
  behavior, and mock response shapes must be preserved.

Future G2.243 allowed source authority if G2.242 is accepted:

| Path | Role |
|---|---|
| `web/backend/app/mock/mock_data/factory.py` | Provider/reset/test-double seam source |
| `web/backend/tests/test_mock_data_manager_configuration.py` | Focused manager configuration tests |
| `web/backend/tests/test_runtime_regressions_p0.py` | Runtime shape regression tests |

Current evidence:

| Item | Result |
|---|---:|
| Factory file lines | 156 |
| Definition count | 1 |
| Import lines | 16 |
| Call expressions | 27 |
| Active route-body calls | 0 |
| GitNexus CLI sample | `CRITICAL`, 63 impacted, 27 direct, 4 processes, 8 modules |
| app/OpenAPI smoke target | `routes=548`, `paths=500` |

Forbidden scope for G2.242 and the future G2.243 source lane:

- Do not batch-migrate API/helper fallback consumers.
- Do not rewrite service adapters or legacy/facade adapters.
- Do not remove or rename `get_mock_data_manager`.
- Do not change routes, OpenAPI, frontend, config, scripts, or OpenSpec.

Next gate:

- If G2.242 is accepted, start G2.243 as a path-limited implementation lane.
- If G2.242 is rejected, keep `get_mock_data_manager` in the residual queue and
  return to ownership classification.

Closeout status:

- G2.242 was accepted by PR `#395` and merged at
  `e7506af885ed635580f2ab765ec9e4fe279cc98b`.
- G2.243 is the path-limited provider/reset seam implementation after this
  authorization.

## G2.243 Mock Data Manager Provider / Reset Seam Implementation

G2.243 is the source implementation after PR `#395` merged G2.242 at
`e7506af885ed635580f2ab765ec9e4fe279cc98b`.

Implementation:

- `factory.py` adds `set_mock_data_manager_provider(provider)`.
- `factory.py` adds `reset_mock_data_manager_provider()`.
- `get_mock_data_manager()` checks an explicit provider first, then preserves
  the previous cached manager, `UnifiedMockDataManager`, and fallback paths.
- Focused tests cover provider override/reset and existing mock runtime shapes.

Current evidence:

| Item | Result |
|---|---:|
| GitNexus impact before edit | `CRITICAL`, 63 impacted, 27 direct, 4 processes, 8 modules |
| Factory file lines after | 190 |
| Focused mock manager + runtime tests | 14 passed |
| Ruff on authorized files | All checks passed |
| app/OpenAPI smoke | `routes=548`, `paths=500` |

Preserved boundaries:

- `get_mock_data_manager` remains the compatibility accessor.
- API/helper fallback consumers are not migrated.
- Service adapters and legacy/facade adapters are not rewritten.
- Routes, OpenAPI, frontend, config, scripts, and OpenSpec are unchanged.

Next gate:

- If accepted, start G2.244 no-source closeout / residual refresh.
- G2.243 does not authorize additional consumer migration.

Closeout status:

- G2.243 was accepted by PR `#396` and merged at
  `a0eec8bea7077e59e25a6f4491d4c695b1e25ed9`.
- G2.244 is the no-source closeout / residual refresh after this implementation.

## G2.244 Mock Data Manager Provider Closeout / Residual Refresh

G2.244 is the no-source closeout and residual refresh after PR `#396` merged
G2.243 at `a0eec8bea7077e59e25a6f4491d4c695b1e25ed9`.

Closeout:

- `set_mock_data_manager_provider(provider)` exists.
- `reset_mock_data_manager_provider()` exists.
- `get_mock_data_manager` remains the compatibility accessor.
- G2.243 did not migrate API/helper fallback consumers, service adapters, or
  legacy/facade adapters.

Verification:

| Item | Result |
|---|---:|
| Focused mock manager + runtime tests | 14 passed |
| Ruff on G2.243 touched runtime/test files | All checks passed |
| app/OpenAPI smoke | `routes=548`, `paths=500` |

Residual candidate refresh:

| Rank | Candidate | Classification | Current evidence | Recommendation |
|---:|---|---|---|---|
| 1 | `get_postgres_async` | Single-definition infrastructure data-access singleton | 1 definition, 28 import lines, 30 call expressions, 22 API route-body calls; GitNexus CLI impact `LOW`, 4 impacted, 3 direct, 0 processes, 2 modules | Select G2.245 no-source ownership / provider decision |
| 2 | `get_monitoring_db` | Multi-definition monitoring/risk/strategy logging seam | 3 definitions, 2 import lines, 12 call expressions, 12 API route-body calls; GitNexus impact ambiguous with 3 candidates | Defer until disambiguation and ownership classification |

Decision:

- Close the mock data manager provider/reset seam unless current-HEAD evidence
  contradicts this closeout.
- Select G2.245 as a no-source `get_postgres_async` ownership / provider
  decision packet.
- Do not start source work from G2.244.

Closeout status:

- G2.244 was accepted by PR `#397` and merged at
  `05844e89873ad4fc729dab87942ea80f81bde39a`.
- G2.245 is the no-source `get_postgres_async` ownership / provider decision
  after this closeout.

## G2.245 Postgres Async Ownership / Provider Decision

G2.245 is the no-source decision packet after PR `#397` merged G2.244 at
`05844e89873ad4fc729dab87942ea80f81bde39a`.

Current evidence:

| Evidence | Value |
|---|---:|
| `get_postgres_async` definitions | 1 |
| Import lines | 28 |
| Public re-export imports | 27 |
| Direct singleton-module imports | 1 |
| Invocation calls excluding definition | 30 |
| Active API route-body calls | 21 |
| Historical `.old.py` API calls | 1 |
| `Depends(get_postgres_async)` calls | 0 |
| GitNexus CLI impact | `LOW`, 4 impacted, 3 direct, 0 processes, 2 modules |

Ownership decision:

- `get_postgres_async` is an infrastructure-owned singleton accessor and
  compatibility facade for `MonitoringPostgreSQLAccess`.
- It is not a route-owned helper, deletion candidate, or direct low-risk source
  pilot.
- The public `src.monitoring.infrastructure.postgresql_async_v3` import surface
  must be preserved until a future accepted source lane explicitly changes it.
- Static scan evidence overrides graph-risk optimism for source planning: the
  graph impact is low, but active API route-body usage is broad enough to require
  a separate authorization packet.

Consumer buckets:

| Bucket | Calls | Handling |
|---|---:|---|
| Monitoring infrastructure/background tasks | 4 | Preserve compatibility |
| Singleton lifecycle helpers | 2 | Preserve `initialize_postgres_async` / `close_postgres_async` consumers |
| Active API route-body consumers | 21 | Requires future provider authorization before source work |
| Historical `.old.py` consumer | 1 | Record as historical evidence only |
| Tests | 2 | Use as compatibility/test-double evidence |

Decision:

- Select G2.246 as a no-source postgres async provider authorization packet.
- G2.246 should choose between an infrastructure-level provider/reset seam,
  route-local provider wrappers, or a hybrid path that preserves background task
  compatibility.
- Defer `get_monitoring_db` until separate multi-definition disambiguation.
- Do not start source work from G2.245.

Closeout status:

- G2.245 was accepted by PR `#398` and merged at
  `6bb9104295c31eac0e5b99dcaa65264c79fda085`.
- G2.246 is the no-source postgres async provider authorization after this
  ownership decision.

## G2.246 Postgres Async Provider Authorization

G2.246 is the no-source authorization packet after PR `#398` merged G2.245 at
`6bb9104295c31eac0e5b99dcaa65264c79fda085`.

Authorization evidence:

| Evidence | Value |
|---|---:|
| `get_postgres_async` definitions | 1 |
| Import lines | 28 |
| Public re-export imports | 27 |
| Invocation calls | 30 |
| Active API route-body calls | 21 |
| Historical `.old.py` API calls | 1 |
| `Depends(get_postgres_async)` calls | 0 |
| GitNexus CLI impact | `LOW`, 4 impacted, 3 direct, 0 processes, 2 modules |

Authorization decision:

- Authorize G2.247 as a path-limited source lane to add an infrastructure-level
  provider/reset seam around `get_postgres_async`.
- The future lane may touch only:
  - `src/monitoring/infrastructure/_postgresql_async_v3_singleton.py`
  - `src/monitoring/infrastructure/postgresql_async_v3.py`
  - `tests/unit/monitoring/test_postgres_async_provider.py`
- The future lane must preserve lazy singleton fallback, lifecycle helpers, and
  the public `postgresql_async_v3.py` import surface.
- Route-local provider wrappers and bulk API consumer migration are explicitly
  excluded from G2.247.
- `get_monitoring_db` remains deferred.

Decision:

- If accepted, start G2.247 path-limited postgres async provider/reset seam
  implementation.
- Do not start route consumer migration from G2.246.
- Do not start source work until G2.246 is accepted.

Closeout status:

- G2.246 was accepted by PR `#399` and merged at
  `efeaaebc031844e8393e8ca1bff723a5900f1a61`.
- G2.247 is the path-limited postgres async provider/reset seam implementation
  after this authorization.

## G2.247 Postgres Async Provider / Reset Seam Implementation

G2.247 is the source implementation after PR `#399` merged G2.246 at
`efeaaebc031844e8393e8ca1bff723a5900f1a61`.

Implementation:

- Added `PostgresAsyncProvider`.
- Added `set_postgres_async_provider(provider)`.
- Added `reset_postgres_async_provider()`.
- Updated `get_postgres_async()` to use an explicit provider when installed.
- Preserved lazy singleton fallback when no explicit provider is installed.
- Preserved `initialize_postgres_async()` and `close_postgres_async()`.
- Preserved public imports from `src.monitoring.infrastructure.postgresql_async_v3`.

Verification:

| Item | Result |
|---|---:|
| TDD red | collection failed before implementation on missing provider/reset export |
| Focused provider tests | 3 passed |
| Ruff on touched source/test files | All checks passed |
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| GitNexus CLI pre-edit impact | `LOW`, 4 impacted, 3 direct, 0 processes, 2 modules |

Decision:

- If accepted, start G2.248 no-source postgres async provider closeout /
  residual refresh.
- Do not migrate API route consumers from G2.247.
- Keep `get_monitoring_db` deferred.

Closeout status:

- G2.247 was accepted by PR `#400` and merged at
  `76b1644fe925a8c0684a820aa58a0aa8e8170190`.
- G2.248 is the no-source closeout / residual refresh after this source lane.

## G2.248 Postgres Async Provider Closeout / Residual Refresh

G2.248 is the no-source closeout after PR `#400` merged G2.247 at
`76b1644fe925a8c0684a820aa58a0aa8e8170190`.

Closeout evidence:

| Evidence | Value |
|---|---:|
| `set_postgres_async_provider(provider)` | present |
| `reset_postgres_async_provider()` | present |
| Public `postgresql_async_v3.py` re-export | present |
| Focused provider tests | 3 passed |
| Ruff on provider source/test files | All checks passed |
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| Active API route-body consumer files | 7 |
| Active API route-body calls | 21 |
| Active API `Depends(get_postgres_async)` calls | 0 |

Residual active API route-body consumers:

| File | Calls | Handling |
|---|---:|---|
| `web/backend/app/api/_data_source_config_responses.py` | 1 | Candidate for future route/provider authorization |
| `web/backend/app/api/_monitoring_portfolio_router.py` | 3 | Candidate for future route/provider authorization |
| `web/backend/app/api/monitoring_analysis.py` | 2 | Candidate for future route/provider authorization |
| `web/backend/app/api/monitoring_watchlists.py` | 7 | Higher-call candidate; requires focused authorization |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 3 | Candidate for future route/provider authorization |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 | Candidate for future route/provider authorization |
| `web/backend/app/api/v1/system/settings.py` | 1 | Candidate for future route/provider authorization |

Decision:

- Close the infrastructure provider/reset seam as accepted.
- Keep route consumer migration open as a residual planning item.
- Select G2.249 as a no-source postgres async route consumer provider
  authorization package.
- G2.249 may classify and authorize a future route-local provider pilot, but
  G2.248 does not authorize source edits.
- Keep historical `.old.py`, background monitoring runtime consumers,
  `get_monitoring_db`, route paths, response contracts, and OpenAPI exposure
  outside G2.248.

Closeout status:

- G2.248 was accepted by PR `#401` and merged at
  `89fb66f6ee21ab33d5e1f5c255a8d75af760033b`.
- G2.249 is the no-source route consumer provider authorization after this
  closeout.

## G2.249 Postgres Async Route Consumer Provider Authorization

G2.249 is the no-source authorization packet after PR `#401` merged G2.248 at
`89fb66f6ee21ab33d5e1f5c255a8d75af760033b`.

Current evidence:

| Evidence | Value |
|---|---:|
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| G2.248 residual files | 7 |
| G2.248 residual calls | 21 |
| Route-decorated files | 5 |
| Route-decorated calls | 19 |
| Route-adjacent helper / repository files | 2 |
| Route-adjacent helper / repository calls | 2 |

Route-decorated candidates:

| File | Calls | Decision |
|---|---:|---|
| `web/backend/app/api/_monitoring_portfolio_router.py` | 3 | Authorize as future G2.250 pilot |
| `web/backend/app/api/monitoring_analysis.py` | 2 | Defer until after pilot |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 3 | Defer until after pilot |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 | Larger batch; defer |
| `web/backend/app/api/monitoring_watchlists.py` | 7 | Larger batch; defer |

Route-adjacent exclusions:

| File | Calls | Reason |
|---|---:|---|
| `web/backend/app/api/_data_source_config_responses.py` | 1 | Helper/facade function without route decorator |
| `web/backend/app/api/v1/system/settings.py` | 1 | Repository constructor dependency, not route-body lookup |

Authorization decision:

- Authorize G2.250 as a path-limited source lane for
  `web/backend/app/api/_monitoring_portfolio_router.py`.
- The future lane may also touch `tests/api/file_tests/test_monitoring_analysis_api.py`
  for focused structural or route/provider tests.
- The future lane must preserve route paths, methods, `include_in_schema`,
  response models, `UnifiedResponse` behavior, and existing
  `calculator_factory=Depends(get_monitoring_calculator_factory)` parameters.
- The future lane must not touch `monitoring_analysis.py`,
  `monitoring_watchlists.py`, `signal_monitoring/*`,
  `_data_source_config_responses.py`, `v1/system/settings.py`,
  `src/monitoring/infrastructure/*`, `get_monitoring_db`, frontend, config,
  scripts, OpenSpec specs/proposals, or PM2 state.

Decision:

- If accepted, start G2.250 postgres async monitoring portfolio route provider
  implementation.
- Do not start bulk route consumer migration from G2.249.
- G2.249 was accepted by PR `#402` and merged at
  `db1a0653737c8239a937a97a5fd32730e2c25bc3`.

## G2.250 Postgres Async Monitoring Portfolio Provider Implementation

G2.250 is the path-limited source lane after PR `#402` merged G2.249 at
`db1a0653737c8239a937a97a5fd32730e2c25bc3`.

Implementation evidence:

| Evidence | Value |
|---|---:|
| Route-local provider added | `get_monitoring_postgres_async` |
| Authorized handlers updated | 3 |
| Authorized route-body `get_postgres_async()` calls | 0 |
| Authorized handler dependency parameters | 3 |
| Focused new test | 1 passed |
| Focused file tests | 18 passed |
| Ruff on touched source/test files | All checks passed |
| app/OpenAPI smoke | `routes=548`, `paths=500` |

Updated handlers:

| Handler | Route | Provider state |
|---|---|---|
| `get_portfolio_summary` | `GET /portfolio/{watchlist_id}/summary` | `postgres_async=Depends(get_monitoring_postgres_async)` |
| `get_portfolio_alerts` | `GET /portfolio/{watchlist_id}/alerts` | `postgres_async=Depends(get_monitoring_postgres_async)` |
| `get_rebalance_suggestions` | `GET /portfolio/{watchlist_id}/rebalance` | `postgres_async=Depends(get_monitoring_postgres_async)` |

Gate degradation:

- GitNexus MCP impact was attempted before edits and failed with transport
  closure.
- GitNexus CLI impact fallback was attempted and timed out / hung before a usable
  report.
- Treat this as degraded evidence, not a LOW-risk GitNexus result.

Decision:

- If accepted, start G2.251 no-source monitoring portfolio provider closeout /
  residual refresh.
- Do not migrate `monitoring_analysis.py`, `monitoring_watchlists.py`,
  `signal_monitoring/*`, `_data_source_config_responses.py`,
  `v1/system/settings.py`, infrastructure providers, frontend, config, scripts,
  OpenSpec, or PM2 state from G2.250.
- G2.250 was accepted by PR `#403` and merged at
  `27b3fbe5dbf5bb9c941490e9d921fedc5b38f8db`.

## G2.251 Monitoring Portfolio Provider Closeout / Residual Refresh

G2.251 is the no-source closeout after PR `#403` merged G2.250 at
`27b3fbe5dbf5bb9c941490e9d921fedc5b38f8db`.

Closeout evidence:

| Evidence | Value |
|---|---:|
| `get_monitoring_postgres_async` provider seam | retained |
| Authorized portfolio route-body `get_postgres_async()` calls | 0 |
| Authorized handler dependency parameters | 3 |
| Focused file tests | 18 passed |
| Ruff on accepted source/test files | All checks passed |
| app/OpenAPI smoke | `routes=548`, `paths=500` |

Residual refresh:

| Residual class | Files | Calls |
|---|---:|---:|
| Route-decorated residuals | 4 | 16 |
| Route-adjacent residuals | 3 | 3 |

Route-decorated residuals:

| File | Calls | Handling |
|---|---:|---|
| `web/backend/app/api/monitoring_watchlists.py` | 7 | Defer as higher-call batch |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 | Defer as signal domain batch |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 3 | Defer as signal domain batch |
| `web/backend/app/api/monitoring_analysis.py` | 2 | Select for next no-source authorization gate |

Route-adjacent residuals:

| File | Calls | Handling |
|---|---:|---|
| `web/backend/app/api/_monitoring_portfolio_router.py` | 1 | Intentional route-local provider seam |
| `web/backend/app/api/_data_source_config_responses.py` | 1 | Helper / facade ownership decision needed |
| `web/backend/app/api/v1/system/settings.py` | 1 | Repository constructor ownership decision needed |

Decision:

- If accepted, start G2.252 no-source `monitoring_analysis.py` postgres async
  route consumer provider authorization.
- Do not start source implementation from G2.251.
- G2.251 was accepted by PR `#404` and merged at
  `d6c98b1f0747f9be694451a2e8d4a49d6d67341f`.

## G2.252 Monitoring Analysis Postgres Async Provider Authorization

G2.252 is the no-source authorization after PR `#404` merged G2.251 at
`d6c98b1f0747f9be694451a2e8d4a49d6d67341f`.

Current evidence:

| Evidence | Value |
|---|---:|
| Route-decorated residual files | 4 |
| Route-decorated residual calls | 16 |
| Route-adjacent residual files | 3 |
| Route-adjacent residual calls | 3 |
| `monitoring_analysis.py` route-body calls | 2 |

Authorized future source lane:

| Future item | Scope |
|---|---|
| G2 id | G2.253 |
| Source file | `web/backend/app/api/monitoring_analysis.py` |
| Focused test file | `tests/api/file_tests/test_monitoring_analysis_api.py` |
| Candidate provider | `get_monitoring_analysis_postgres_async` |

Target handlers:

| Handler | Route | Existing dependency to preserve |
|---|---|---|
| `get_health_score_history` | `GET /results/{stock_code}` | none |
| `analyze_portfolio` | `GET /portfolio/{watchlist_id}` | `calculator_factory=Depends(get_monitoring_calculator_factory)` |

Decision:

- G2.252 was accepted by PR `#405` and merged at
  `c3e3452440455c8a7955b0779433219abee48c86`.
- It authorized G2.253 path-limited `monitoring_analysis.py` postgres async
  route provider implementation.
- Do not implement source changes from G2.252.
- Do not migrate `monitoring_watchlists.py`, `signal_monitoring/*`,
  `_data_source_config_responses.py`, `v1/system/settings.py`, infrastructure,
  frontend, config, scripts, OpenSpec, or PM2 state from G2.252.

## G2.253 Monitoring Analysis Postgres Async Provider Implementation

G2.253 is the path-limited source lane after PR `#405` merged G2.252 at
`c3e3452440455c8a7955b0779433219abee48c86`.

Implementation evidence:

| Evidence | Value |
|---|---:|
| Authorized route-body `get_postgres_async()` calls before | 2 |
| Authorized route-body `get_postgres_async()` calls after | 0 |
| New route-local provider | `get_monitoring_analysis_postgres_async` |
| Updated handlers | `get_health_score_history`, `analyze_portfolio` |
| Focused file tests | 19 passed |
| OpenAPI smoke | 548 routes / 500 paths |

Scope:

- Modified only `web/backend/app/api/monitoring_analysis.py`, the focused
  file-test path, and G2.253 governance evidence.
- Preserved `analyze_portfolio`
  `calculator_factory=Depends(get_monitoring_calculator_factory)`.
- Preserved route paths, methods, response models, summaries, and
  `include_in_schema` exposure.
- Did not edit `src/monitoring/infrastructure/**`, broader route consumers,
  frontend, config, scripts, OpenSpec, or PM2 state.

Decision:

- G2.253 was accepted by PR `#406` and merged at
  `767c92887348fe25eeaa92685ecb5343717fb326`.
- After merge, start G2.254 no-source monitoring analysis provider closeout /
  residual refresh.
- Do not migrate `monitoring_watchlists.py`, `signal_monitoring/*`,
  `_data_source_config_responses.py`, `v1/system/settings.py`, infrastructure,
  frontend, config, scripts, OpenSpec, or PM2 state from G2.253.

## G2.254 Monitoring Analysis Provider Closeout / Residual Refresh

G2.254 is the no-source closeout after PR `#406` merged G2.253 at
`767c92887348fe25eeaa92685ecb5343717fb326`.

Current closeout evidence:

| Evidence | Value |
|---|---:|
| `monitoring_analysis.py` route-body `get_postgres_async()` calls | 0 |
| Retained `get_monitoring_analysis_postgres_async` provider calls | 1 |
| Focused file tests | 19 passed |
| OpenAPI smoke | 548 routes / 500 paths |

Residual refresh:

| File | Route-decorated calls | Handling |
|---|---:|---|
| `web/backend/app/api/monitoring_watchlists.py` | 7 | Select for G2.255 no-source authorization |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 | Defer behind `monitoring_watchlists.py` |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 3 | Defer behind `monitoring_watchlists.py` |

Decision:

- If accepted, merge PR `#407`.
- After merge, start G2.255 no-source `monitoring_watchlists.py` postgres async
  route provider authorization.
- Do not implement source changes from G2.254.
- Do not migrate `signal_monitoring/*`, `_data_source_config_responses.py`,
  `v1/system/settings.py`, infrastructure, frontend, config, scripts, OpenSpec,
  or PM2 state from G2.254.

Closeout status:

- G2.254 was accepted by PR `#407` and merged at
  `c64260f1795b39c82903fa7fd370b0ccaee3ac36`.
- G2.255 is the no-source `monitoring_watchlists.py` postgres async route
  provider authorization after this closeout.

## G2.255 Monitoring Watchlists Postgres Async Provider Authorization

G2.255 is the no-source authorization packet after PR `#407` merged G2.254 at
`c64260f1795b39c82903fa7fd370b0ccaee3ac36`.

Authorization evidence:

| Evidence | Value |
|---|---:|
| `monitoring_watchlists.py` route handlers | 8 |
| Route-body `get_postgres_async()` calls | 7 |
| Focused watchlist tests | 28 passed |
| Candidate source ruff | All checks passed |
| OpenAPI smoke | 548 routes / 500 paths |
| Watchlist OpenAPI routes | 8 |

Authorized future G2.256 handlers:

| Handler | Route | Calls | Handling |
|---|---|---:|---|
| `create_watchlist` | `POST /api/v1/monitoring/watchlists` | 1 | Move lookup behind route-local provider |
| `list_watchlists` | `GET /api/v1/monitoring/watchlists` | 1 | Move lookup behind route-local provider |
| `get_watchlist` | `GET /api/v1/monitoring/watchlists/{watchlist_id}` | 1 | Move lookup behind route-local provider |
| `delete_watchlist` | `DELETE /api/v1/monitoring/watchlists/{watchlist_id}` | 1 | Move lookup behind route-local provider |
| `add_stock_to_watchlist` | `POST /api/v1/monitoring/watchlists/{watchlist_id}/stocks` | 1 | Preserve `StockToAdd` import/use while moving lookup |
| `list_watchlist_stocks` | `GET /api/v1/monitoring/watchlists/{watchlist_id}/stocks` | 1 | Move lookup behind route-local provider |
| `remove_stock_from_watchlist` | `DELETE /api/v1/monitoring/watchlists/{watchlist_id}/stocks/{stock_code}` | 1 | Move lookup behind route-local provider |

Excluded handler:

| Handler | Reason |
|---|---|
| `update_watchlist` | No direct route-body `get_postgres_async()` call at current HEAD |

Decision:

- If accepted, merge PR `#408`.
- After merge, start G2.256 path-limited `monitoring_watchlists.py` postgres
  async route provider implementation.
- G2.256 may touch only `web/backend/app/api/monitoring_watchlists.py`,
  `tests/api/file_tests/test_watchlist_api.py`, and
  `web/backend/tests/test_monitoring_watchlists_runtime_fallback.py`.
- G2.256 must rerun GitNexus impact before editing because G2.255 GitNexus MCP
  was degraded.
- Do not migrate `signal_monitoring/*`, retained provider seams, route-adjacent
  helper/repository residuals, infrastructure, frontend, config, scripts,
  OpenSpec, or PM2 state from G2.255.

## Forbidden Scope

This track summary forbids:

- unauthorized backend source edits
- frontend edits
- test edits
- OpenSpec proposal creation
- issue label changes
- moving another service candidate directly to implementation
- treating service inventory counts as implementation backlogs

## G2.256 Monitoring Watchlists Postgres Async Provider Implementation

Status: for review in PR `#409`.

Parent gate:

- G2.255 no-source authorization was accepted by PR `#408`.
- PR `#408` merged into `wip/root-dirty-20260403` at
  `8866cfe8ba081957714c8c51e948be9340fc45ac`.

Authorized implementation scope:

- `web/backend/app/api/monitoring_watchlists.py`
- `tests/api/file_tests/test_watchlist_api.py`
- `web/backend/tests/test_monitoring_watchlists_runtime_fallback.py`

Implementation result:

| Evidence | Result |
|---|---|
| Route-local provider | `get_monitoring_watchlists_postgres_async()` added |
| Authorized route-body `get_postgres_async()` calls | `7 -> 0` |
| Provider delegate call | `1` module-level provider call remains |
| Authorized handler dependency parameters | `7` |
| Watchlist app routes | `8` |
| App route table / OpenAPI smoke | `routes=548`, `paths=500` |
| Focused tests | `29 passed` |
| Ruff touched files | `All checks passed!` |
| OpenSpec strict validate | `migrate-backend-singletons-to-lifecycle-di` valid |

Updated handlers:

- `create_watchlist`
- `list_watchlists`
- `get_watchlist`
- `delete_watchlist`
- `add_stock_to_watchlist`
- `list_watchlist_stocks`
- `remove_stock_from_watchlist`

Explicit exclusions:

- `update_watchlist` remains untouched because G2.255 did not identify a direct
  route-body `get_postgres_async()` call there.
- `signal_monitoring/*`, `monitoring_analysis.py`,
  `_monitoring_portfolio_router.py`, `_data_source_config_responses.py`,
  `v1/system/settings.py`, and `src/monitoring/infrastructure/**` remain out of
  scope.
- Route paths, response models, summaries, tags, and OpenAPI exposure remain
  unchanged by intent.

Next gate after acceptance:

- G2.257 no-source monitoring watchlists provider closeout / residual refresh.
- G2.257 should verify this provider migration remains closed, refresh residual
  `get_postgres_async()` route consumers, and select the next candidate without
  editing source code.

## G2.257 Monitoring Watchlists Postgres Async Provider Closeout / Residual Refresh

Status: for review in PR `#410`.

Parent gate:

- G2.256 implementation was accepted by PR `#409`.
- PR `#409` merged into `wip/root-dirty-20260403` at
  `536b0634a51ea580f1a384d07a8ee605fbed8567`.

Closeout result:

| Evidence | Result |
|---|---:|
| Authorized `monitoring_watchlists.py` route-body `get_postgres_async()` calls | 0 |
| Retained `get_monitoring_watchlists_postgres_async()` provider calls | 1 |
| Authorized handler dependency parameters | 7 |
| Watchlist app routes | 8 |
| App route table / OpenAPI smoke | `routes=548`, `paths=500` |
| Focused tests | `29 passed` |
| Ruff touched files | `All checks passed!` |
| OpenSpec strict validate | `migrate-backend-singletons-to-lifecycle-di` valid |

Residual refresh:

| Residual class | Count | Next handling |
|---|---:|---|
| Active app-route residual calls | 4 | Select `signal_monitoring/signal_history_response.py` for G2.258 no-source authorization |
| Static route-like calls not in current app route table | 3 | Keep pending route-registration / ownership confirmation |
| Retained route-local provider seam calls | 3 | Do not treat as direct route-body residuals |
| Route-adjacent / legacy calls | 3 | Keep out of provider implementation lanes until separately classified |

Next gate after acceptance:

- G2.258 no-source `signal_monitoring/signal_history_response.py` postgres
  async provider authorization.
- G2.258 should authorize or reject only a future source lane. It must not edit
  source code itself.

## G2.258 Signal History Postgres Async Provider Authorization

Status: for review in PR `#411`.

Parent gate:

- G2.257 closeout / residual refresh was accepted by PR `#410`.
- PR `#410` merged into `wip/root-dirty-20260403` at
  `ad3cc58dbe0dc768488006d22de09085a1a8ee6f`.

Candidate snapshot:

| Evidence | Result |
|---|---:|
| Candidate file | `web/backend/app/api/signal_monitoring/signal_history_response.py` |
| Active app routes | 4 |
| Route-body `get_postgres_async()` calls | 4 |
| File tests | `13 passed` |
| Candidate source ruff | `All checks passed!` |
| App route table / OpenAPI smoke | `routes=548`, `paths=500` |
| OpenSpec strict validate | `migrate-backend-singletons-to-lifecycle-di` valid |

Authorized future G2.259 handlers:

- `get_signal_history`
- `get_signal_quality_report`
- `get_strategy_realtime_monitoring`
- `health_check`

Known preconditions for future implementation:

- `web/backend/tests/test_signal_history_response_regressions.py` currently
  fails because it expects object attributes while the handler returns a dict.
- `tests/api/file_tests/test_signal_monitoring_api.py` has existing `F811`
  fixture-import lint debt when checked with `ruff --no-fix`.
- G2.259 may resolve these only inside the allowed future test paths and only
  to support the authorized provider implementation.

Explicit exclusions:

- `signal_monitoring/get_signal_statistics.py` remains deferred until
  route-registration / ownership confirmation.
- Other `signal_monitoring/*`, infrastructure, route contracts, OpenAPI
  exposure, frontend, config, scripts, PM2, and OpenSpec remain out of scope.

Next gate after acceptance:

- G2.259 path-limited `signal_history_response.py` postgres async route
  provider implementation.
- G2.259 must rerun GitNexus impact/context before source edits and stop on
  HIGH or CRITICAL risk.

## G2.259 Signal History Postgres Async Provider Implementation

Status: for review in PR `#412`.

Parent gate:

- G2.258 authorization was accepted by PR `#411`.
- PR `#411` merged into `wip/root-dirty-20260403` at
  `a58cf6490af4e4cd51e9b98543fa286244fdb78f`.

Implementation summary:

| Evidence | Result |
|---|---:|
| Provider added | `get_signal_history_postgres_async` |
| Authorized handlers migrated | 4 |
| Target route-body direct `get_postgres_async()` calls after | 0 |
| Provider backing `get_postgres_async()` calls after | 1 |
| Target dependency parameters after | 4 |
| Focused tests | `15 passed` |
| Ruff on touched source/tests | `All checks passed!` |
| App route table / OpenAPI smoke | `routes=548`, `paths=500`, `target_route_count=4` |
| OpenSpec strict validate | `migrate-backend-singletons-to-lifecycle-di` valid |

Authorized handlers migrated:

- `get_signal_history`
- `get_signal_quality_report`
- `get_strategy_realtime_monitoring`
- `health_check`

Route/OpenAPI contract boundary:

- Route paths unchanged.
- Response models unchanged.
- OpenAPI exposure unchanged.
- `get_signal_statistics.py` remains deferred.
- Other `signal_monitoring/*`, infrastructure, frontend, config, scripts, PM2,
  and OpenSpec remain out of scope.

GitNexus note:

- GitNexus MCP impact calls failed with `Transport closed` before source edits.
- CLI impact/context fallback was used and recorded LOW / zero-flow evidence for
  the uniquely resolved handlers.
- `health_check` required exact UID context review because the symbol name is
  ambiguous across the codebase.

Next gate after acceptance:

- G2.260 no-source signal history provider closeout / residual refresh.
- G2.260 should verify the four migrated handlers remain closed, refresh active
  app-route `get_postgres_async()` residuals, and choose the next authorization
  candidate or declare the queue closed.
- G2.260 must not edit source.

## G2.260 Signal History Postgres Async Provider Closeout / Residual Refresh

Status: for review in PR `#413`.

Parent gate:

- G2.259 implementation was accepted by PR `#412`.
- PR `#412` merged into `wip/root-dirty-20260403` at
  `5dc148e0aa4653f0803eb6a088e90544b6c051e4`.

Closeout evidence:

| Evidence | Result |
|---|---:|
| `app.routes` | 548 |
| OpenAPI paths | 500 |
| Active API routes scanned | 513 |
| `get_signal_history_postgres_async` exists | `true` |
| Provider backing `get_postgres_async()` calls | 1 |
| Target route-body direct `get_postgres_async()` calls | 0 |
| Target dependency parameters | 4 |
| Focused tests | `15 passed` |
| Ruff on reference source/tests | `All checks passed!` |
| OpenSpec strict validate | `migrate-backend-singletons-to-lifecycle-di` valid |

Residual refresh:

| Residual class | Count | Handling |
|---|---:|---|
| Active app-route body consumers | 0 | Closed at current HEAD |
| Retained route-local provider seams | 4 | Keep as provider backing calls |
| Legacy / compatibility surfaces | 3 | Do not migrate from G2.260 |
| Static route-like but not app-registered | 3 | Route-registration / ownership decision required |

Static route-like but not app-registered residuals:

- `web/backend/app/api/signal_monitoring/get_signal_statistics.py::get_signal_statistics`
- `web/backend/app/api/signal_monitoring/get_signal_statistics.py::get_active_signals`
- `web/backend/app/api/signal_monitoring/get_signal_statistics.py::get_strategy_detailed_health`

Decision:

- The active app-route body `get_postgres_async()` migration queue is closed.
- Do not open another source implementation lane directly from G2.260.
- G2.261 should be a no-source `get_signal_statistics.py` route-registration /
  ownership decision package.

Next gate after acceptance:

- G2.261 no-source route-registration / ownership decision for
  `web/backend/app/api/signal_monitoring/get_signal_statistics.py`.
- G2.261 must decide whether the three static route-like consumers are
  intentionally unregistered, legacy/deferred, or candidates for a future
  separately authorized route/provider lane.
- G2.261 must not edit source.

## G2.261 Get Signal Statistics Route-Registration / Ownership Decision

Status: for review in PR `#414`.

Parent gate:

- G2.260 closeout / residual refresh was accepted by PR `#413`.
- PR `#413` merged into `wip/root-dirty-20260403` at
  `efc579ad8558314568b6f03e97f1c12341105fa0`.

Candidate evidence:

| Evidence | Result |
|---|---:|
| Candidate file | `web/backend/app/api/signal_monitoring/get_signal_statistics.py` |
| File lines | 511 |
| Module-local `APIRouter` | `true` |
| Route-decorated handlers | 3 |
| Direct `get_postgres_async()` calls in decorated handlers | 3 |
| Registered app routes from this file | 0 |
| Current `app.routes` | 548 |
| Current OpenAPI paths | 500 |

Runtime smoke:

| Intended path | Status |
|---|---:|
| `/api/signals/statistics` | 404 |
| `/api/signals/active` | 404 |
| `/api/strategies/test_strategy/health/detailed` | 404 |

Ownership decision:

- Classify `get_signal_statistics.py` as dormant route module / route ownership
  gap.
- It is not an active app-route body provider residual at current HEAD.
- Do not inject a postgres provider before deciding route registration,
  OpenAPI exposure, and historical docs/test references.

Consumer matrix summary:

| Path | References | Primary location | Exact frontend refs |
|---|---:|---|---:|
| `/api/signals/statistics` | 18 | docs + one test | 0 |
| `/api/signals/active` | 14 | docs + one test | 0 |
| `/api/strategies/{strategy_id}/health/detailed` | 2 | docs | 0 |

Next gate after acceptance:

- G2.262 no-source route/OpenAPI reconciliation authorization.
- G2.262 should decide whether to register, keep dormant, or retire/archive the
  route-shaped module and stale docs/tests.
- G2.262 must not edit source.

## G2.262 Signal Statistics Route/OpenAPI Reconciliation Authorization

Status: for review in PR `#415`.

- Parent PR `#414` merged at `1d492cbad2aa849b21df1028f5fea1a3bd9c30c4`.
- `web/backend/app/api/signal_monitoring/get_signal_statistics.py` remains dormant at current HEAD `1d492cbad`: 3 route-decorated handlers, 3 direct `get_postgres_async()` calls, 0 registered target routes, and 0 current `app.openapi()` target paths.
- `docs/api/openapi.yaml` still has historical entries for target paths that are absent from generated OpenAPI.
- G2.262 does not authorize source edits, route registration, docs/api cleanup, tests, OpenSpec changes, or provider injection.
- Next gate: G2.263 no-source signal statistics route contract disposition decision.

## G2.263 Signal Statistics Route Contract Disposition Decision

Status: for review in PR `#416`.

- Parent PR `#415` merged at `15bebd4de48059fb5bf35efef81aabb9040cf6ea`.
- Disposition: retain dormant source and reconcile stale contract artifacts.
- Route registration, provider injection, source retirement, docs/api edits, tests, frontend, OpenSpec, and PM2 remain unauthorized.
- Product consumer matrix excluding governance artifacts: `/api/signals/statistics` refs 10, `/api/signals/active` refs 7, strategy detailed health refs 0; exact frontend/backend consumers are 0.
- Next gate: G2.264 no-source stale signal statistics contract cleanup authorization.

## G2.264 Signal Statistics Stale Contract Cleanup Authorization

Status: for review in PR `#417`.

- Parent PR `#416` merged at `795d2b9f50c3e483876f1b4ec484fbf9c1d9e513`.
- Authorized future lane: G2.265 path-limited docs/test stale contract cleanup implementation.
- Future allowed paths: `docs/api/openapi.yaml`, `docs/api/task_plan_signal_monitoring_phase2_extended.md`, `docs/operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md`, `docs/architecture/DESIGN_METHODOLOGY_AND_TOOLCHAIN_ANALYSIS.md`, `tests/unit/test_signal_monitoring_integration.py`.
- Source, route registration, provider injection, source retirement, frontend, OpenSpec, scripts, config, and PM2 remain unauthorized.

## G2.265 Signal Statistics Stale Contract Cleanup Implementation

Status: accepted/merged by PR `#418` at `2b53352d6869f66147ce3892b1b0a7174ba064b4`.

- Parent PR `#417` merged at `fe1927818309efb2c1de3a9c1e1128e9b456053e`; implementation PR `#418` merged at `2b53352d6869f66147ce3892b1b0a7174ba064b4`.
- Cleaned only the five authorized docs/test stale contract artifacts.
- `docs/api/openapi.yaml` no longer presents the dormant signal statistics paths as active hand-maintained OpenAPI paths.
- `tests/unit/test_signal_monitoring_integration.py` now asserts explicit dormant-route `404` behavior for the two stale endpoints.
- Runtime OpenAPI remains `548/500`, target OpenAPI paths remain `0`, duplicate operation IDs remain `0`.
- Superseded by G2.266 no-source signal statistics dormant contract closeout / residual refresh.


## G2.266 Signal Statistics Dormant Contract Closeout / Residual Refresh

Status: accepted/merged by PR `#419` at `eec68bb47a4ee98508480ef0ac2cdd3716e04b05`.

- Parent PR `#418` merged at `2b53352d6869f66147ce3892b1b0a7174ba064b4`.
- G2.265 is recorded as accepted/merged; stale signal statistics docs/test contract mismatch is closed.
- Current runtime OpenAPI remains `548/500`; `/api/signals/statistics` and `/api/signals/active` remain absent from generated OpenAPI.
- Targeted dormant endpoint tests remain green at `2/2` and assert `404 Not Found`.
- `web/backend/app/api/signal_monitoring/get_signal_statistics.py` remains retained dormant source and is excluded from provider injection or source retirement.
- Residual refresh found mixed monitoring/signal getter-shaped surfaces; they require classification before source authorization.
- Superseded by G2.267 no-source monitoring/signal residual provider classification refresh.
- G2.266 must not edit backend source, tests, route contracts, frontend, config, scripts, OpenSpec, or PM2 state.

## G2.267 Monitoring / Signal Residual Provider Classification Refresh

Status: accepted/merged by PR `#420` at `772e4a3ac8e05edaa243d660d67c7e5df18158f9`.

- Parent PR `#419` merged at `eec68bb47a4ee98508480ef0ac2cdd3716e04b05`.
- Classified monitoring/signal getter-shaped residuals without source edits.
- Active route-body authorization candidate: `_monitoring_portfolio_router.py` calls `get_portfolio_optimizer()` in three active route handlers.
- Retained wrapper surfaces: monitoring calculator/postgres wrapper functions and signal history postgres provider backing wrapper.
- False positives: `monitoring.py::analyze_monitoring` route-helper call and dormant `get_signal_statistics.py`.
- Control-plane residual: `web/backend/app/api/v1/pool_monitoring.py` pool accessors require route/OpenAPI/control-plane governance, not service DI implementation.
- GitNexus `context` and `impact` for `get_portfolio_optimizer` timed out; G2.268 rechecked and recorded MCP `Transport closed`.
- Superseded by G2.268 no-source monitoring portfolio optimizer route provider authorization.
- G2.267 must not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, or PM2 state.

## G2.268 Monitoring Portfolio Optimizer Provider Authorization

Status: accepted/merged by PR `#421` at `1cb885e8267d76e47e0d08977002a80fafb56092`.

- Parent PR `#420` merged at `772e4a3ac8e05edaa243d660d67c7e5df18158f9`.
- Selected candidate: `get_portfolio_optimizer()` has one definition in `src/monitoring/domain/portfolio_optimizer.py` and three active route-body call sites in `web/backend/app/api/_monitoring_portfolio_router.py`.
- Target handlers: `get_portfolio_summary`, `get_portfolio_alerts`, and `get_rebalance_suggestions`.
- Runtime/OpenAPI snapshot: `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, and `3` target module routes.
- GitNexus MCP context/impact retried and returned `Transport closed`; future source work must retry GitNexus or record CLI fallback before editing.
- Authorized next gate after acceptance: G2.269 path-limited monitoring portfolio optimizer route provider implementation.
- Future G2.269 may touch only `web/backend/app/api/_monitoring_portfolio_router.py` plus focused tests in `tests/api/file_tests/test_monitoring_analysis_api.py` and `web/backend/tests/test_health_route_conflicts.py`.
- Superseded by G2.269 path-limited monitoring portfolio optimizer route provider implementation.
- G2.268 must not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, or PM2 state.

## G2.269 Monitoring Portfolio Optimizer Provider Implementation

Status: accepted/merged by PR `#422` at `7ed8f8e352f29c9c48bc4a45ea77661b08de89da`.

- Parent PR `#421` merged at `1cb885e8267d76e47e0d08977002a80fafb56092`.
- GitNexus MCP context/impact returned `Transport closed`; CLI impact returned `HIGH` with exactly the three authorized target route handlers affected.
- Added route-local `get_monitoring_portfolio_optimizer()` in `web/backend/app/api/_monitoring_portfolio_router.py`.
- Moved `get_portfolio_summary`, `get_portfolio_alerts`, and `get_rebalance_suggestions` to `Depends(get_monitoring_portfolio_optimizer)`.
- Direct route-body `get_portfolio_optimizer()` calls are `0`; provider backing call remains `1`; dependency parameters are `3`.
- TDD red/green completed for `test_monitoring_portfolio_optimizer_uses_route_dependency_provider`.
- Focused verification: `tests/api/file_tests/test_monitoring_analysis_api.py` passed `20/20`; monitoring analysis OpenAPI/parameter guard passed `1/1`; ruff passed.
- Runtime/OpenAPI snapshot remains `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, and `3` target module routes.
- Superseded by G2.270 no-source monitoring portfolio optimizer provider closeout / residual refresh.
- G2.269 must not be used as authority for domain optimizer edits, non-target API modules, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or broader backend source.

## G2.270 Monitoring Portfolio Optimizer Provider Closeout / Residual Refresh

Status: accepted/merged by PR `#423` at `5b3ffd1f114b612810e96c463c651befeb005222`.

- Parent PR `#422` merged at `7ed8f8e352f29c9c48bc4a45ea77661b08de89da`.
- G2.269 is recorded as accepted/merged; direct route-body `get_portfolio_optimizer()` calls are `0`.
- Runtime/OpenAPI snapshot remains `548` FastAPI routes, `500` OpenAPI paths, and `0` duplicate operation IDs.
- Retained wrapper residuals remain provider backing calls, not source-lane candidates.
- `signal_monitoring/get_signal_statistics.py` remains dormant with `0` active routes and stays under prior G2.261-G2.266 decisions.
- `web/backend/app/api/v1/pool_monitoring.py` has `4` active routes and remaining pool accessors; classify this as route/OpenAPI/control-plane ownership work, not service DI implementation.
- Superseded by G2.271 no-source pool monitoring control-plane accessor ownership / route governance decision.
- G2.270 must not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.271 Pool Monitoring Control-Plane Ownership Decision

Status: accepted/merged by PR `#424` at `8e0fcd6738c4e3a889b4851d058f8121f32b8ce8`.

- Parent PR `#423` merged at `5b3ffd1f114b612810e96c463c651befeb005222`.
- `web/backend/app/api/v1/pool_monitoring.py` is classified as an active control-plane route contract, not an ordinary service lifecycle DI source candidate.
- Runtime/OpenAPI snapshot remains `548` FastAPI routes, `500` OpenAPI paths, and `0` duplicate operation IDs.
- Pool monitoring has `4` active routes and `4` OpenAPI paths, all `include_in_schema=true`.
- The active paths are `/api/pool-monitoring/postgresql/stats`, `/api/pool-monitoring/tdengine/stats`, `/api/pool-monitoring/health`, and `/api/pool-monitoring/alerts`.
- Residual accessors `get_postgresql_engine()` and `get_tdengine_manager()` are infrastructure pool accessors used by control-plane routes.
- Route-local stats helpers `get_postgresql_pool_stats()` and `get_tdengine_pool_stats()` remain under route/OpenAPI/control-plane ownership.
- GitNexus MCP route/context calls timed out after `120s`; G2.271 records AST, route table, OpenAPI, and static artifact fallback evidence.
- Superseded by G2.272 no-source service lifecycle residual candidate refresh after pool-monitoring deferral.
- G2.271 must not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.272 Service Lifecycle Residual Candidate Refresh

Status: accepted/merged by PR `#425` at `bcf28e4668391f91ea97ee252b4da4eea64faf74`.

- Parent PR `#424` merged at `8e0fcd6738c4e3a889b4851d058f8121f32b8ce8`.
- Current scan covered `371` Python files under `web/backend/app/api` and `web/backend/app/services`.
- Filtered AST call buckets: `113` active route-body candidates, `362` provider/dependency backing calls, `70` API helper/module candidates, `12` known-deferred calls, and `169` service-body candidates.
- Known-deferred surfaces remain excluded: `pool_monitoring.py` from G2.271 and dormant `get_signal_statistics.py` from G2.261-G2.266.
- Top active route-body candidate is `get_monitoring_db` with `10` calls across `risk/alerts.py`, `risk/metrics.py`, and `strategy_management/_strategy_crud_router.py`.
- GitNexus CLI reports `get_monitoring_db` is ambiguous across `risk/_shared.py`, `utils/risk_utils.py`, and `strategy_management/_helpers.py`.
- Selected next gate after acceptance: G2.273 no-source `get_monitoring_db` ownership / route-provider decision.
- G2.272 must not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.273 get_monitoring_db Ownership / Route-Provider Decision

Status: accepted/merged by PR `#426` at `0de77f3d05b1b6242515f2b86fce03c0eba37aaa`.

- Parent PR `#425` merged at `bcf28e4668391f91ea97ee252b4da4eea64faf74`.
- GitNexus MCP impact returned `Transport closed`; CLI impact returned an ambiguous result for three same-name symbols.
- Candidate symbols are `web/backend/app/api/risk/_shared.py:get_monitoring_db`, `web/backend/app/utils/risk_utils.py:get_monitoring_db`, and `web/backend/app/api/strategy_management/_helpers.py:get_monitoring_db`.
- Risk surface: `risk/_shared.py` defines the helper and `risk/alerts.py` plus `risk/metrics.py` have `6` active route-body calls.
- Strategy surface: `strategy_management/_helpers.py` defines the helper and `_strategy_crud_router.py` has `4` active route-body calls plus helper-level lifecycle calls.
- Utility same-name surface: `utils/risk_utils.py` defines another helper but G2.273 found `0` active target route calls in the scoped scan.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, and `0` duplicate operation IDs.
- Decision: do not create one combined `get_monitoring_db` implementation lane. Select `G2.274 no-source risk get_monitoring_db route-provider authorization` as the next gate.
- G2.273 must not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.274 Risk get_monitoring_db Provider Authorization

Status: accepted/merged by PR `#427` at `16df80c30eb4fceec78a13630e40167f0e4037ca`.

- Parent PR `#426` merged at `0de77f3d05b1b6242515f2b86fce03c0eba37aaa`.
- GitNexus MCP impact returned `Transport closed`; CLI impact using `Function:web/backend/app/api/risk/_shared.py:get_monitoring_db` returned LOW risk with 3 direct risk handlers.
- Direct affected symbols are `create_risk_alert`, `calculate_var_cvar`, and `calculate_beta`.
- Risk target files are `web/backend/app/api/risk/_shared.py`, `web/backend/app/api/risk/alerts.py`, and `web/backend/app/api/risk/metrics.py`.
- Current route-body risk call sites remain 6 across the three authorized handlers.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, and `0` duplicate operation IDs.
- Target endpoint parameter counts are unchanged at authorization time: `POST /api/v1/risk/alerts` has `0`, `POST /api/v1/risk/var-cvar` has `0`, and `POST /api/v1/risk/beta` has `0`.
- Authorized next gate after acceptance: G2.275 path-limited risk `get_monitoring_db` route-provider implementation.
- Future G2.275 may touch only the three risk source paths plus focused risk tests named in the authorization report.
- G2.274 must not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.275 Risk get_monitoring_db Provider Implementation

Status: accepted/merged by PR `#428` at `daa4f22a557b054ab76042d4990b6e91d9faa7a7`.

- Parent PR `#427` merged at `16df80c30eb4fceec78a13630e40167f0e4037ca`.
- GitNexus MCP impact returned `Transport closed`; CLI impact using `Function:web/backend/app/api/risk/_shared.py:get_monitoring_db` returned LOW risk with 3 direct risk handlers and 0 affected processes.
- Added `get_risk_monitoring_db()` in `web/backend/app/api/risk/_shared.py` as the route-provider backing wrapper for the existing risk monitoring database helper.
- Moved `create_risk_alert`, `calculate_var_cvar`, and `calculate_beta` to `Depends(get_risk_monitoring_db)`.
- Direct route-body `get_monitoring_db()` calls in `risk/alerts.py` and `risk/metrics.py` are `0`; provider backing call remains `1`; dependency parameters are `3`; `monitoring_db.log_operation(...)` calls are `6`.
- TDD red/green completed for `test_risk_monitoring_db_uses_route_dependency_provider`.
- Focused verification: provider test + `web/backend/tests/test_health_route_conflicts.py` passed `122/122`; ruff passed on touched source/test files.
- `web/backend/tests/test_week1_risk_api.py` remains existing test debt: `4 failed, 11 passed, 4 errors` from missing fixtures, method expectation drift, and local monitoring DB side-effect connection errors.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, and unchanged target endpoint parameter counts.
- Next gate after acceptance: G2.276 no-source risk `get_monitoring_db` provider closeout / residual refresh.
- G2.275 must not be used as authority for strategy-management helper changes, `web/backend/app/utils/risk_utils.py`, route registration, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or broader backend source.

## G2.276 Risk get_monitoring_db Provider Closeout / Residual Refresh

Status: accepted/merged by PR `#429` at `f48ede2ce2202318efa3411fe22fb83a8d4d920b`.

- Parent PR `#428` merged at `daa4f22a557b054ab76042d4990b6e91d9faa7a7`.
- Risk route-body `get_monitoring_db()` calls are closed: `risk/alerts.py` and `risk/metrics.py` both have `0`; risk provider backing call remains in `_shared.py`.
- Current API residual scan finds strategy-management as the only active API route-body residual: `_strategy_crud_router.py` has `4` direct log calls and `_helpers.py` has helper-level ownership calls.
- `web/backend/app/utils/risk_utils.py` remains a deferred utility same-name helper with `0` active API route-body calls in this scan.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, and `0` duplicate operation IDs.
- Focused risk provider test remains green at `1/1`; ruff remains clean on the G2.275 touched risk source/test paths.
- Selected next gate after acceptance: G2.277 no-source strategy `get_monitoring_db` route-provider authorization.
- G2.276 must not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.277 Strategy get_monitoring_db Provider Authorization

Status: accepted/merged by PR `#430` at `2d1d2c28fe59bd7b98f63a41b9a0ff4c343d0441`.

- Parent PR `#429` merged at `f48ede2ce2202318efa3411fe22fb83a8d4d920b`.
- GitNexus MCP context / impact returned `Transport closed`; CLI fallback using `Function:web/backend/app/api/strategy_management/_helpers.py:get_monitoring_db` returned LOW risk with `7` impacted symbols, `3` direct symbols, and `0` affected processes.
- Direct affected symbols are `_handle_strategy_lifecycle_action`, `list_strategies`, and `create_strategy`.
- Strategy target files are `web/backend/app/api/strategy_management/_helpers.py` and `web/backend/app/api/strategy_management/_strategy_crud_router.py`.
- Current strategy call sites are `2` helper-level lifecycle log calls in `_helpers.py` and `4` active route-body log calls in `_strategy_crud_router.py`.
- `web/backend/app/utils/risk_utils.py` remains a deferred utility same-name helper with `0` active API route-body calls in this scan.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, and `0` duplicate operation IDs.
- Focused strategy file-test attempt currently reports `3 failed, 7 passed, 1 warning`; failures are existing route prefix/count/chart-data wiring expectation drift and are not caused by this no-source authorization package.
- Authorized next gate after acceptance: G2.278 path-limited strategy `get_monitoring_db` route-provider implementation.
- Future G2.278 may touch only the two strategy-management source paths plus focused strategy tests named in the authorization report.
- G2.277 must not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.278 Strategy get_monitoring_db Provider Implementation

Status: accepted/merged by PR `#431` at `c5496cab0a4213f74636af1c48772dc96c90bd1b`.

- Parent PR `#430` merged at `2d1d2c28fe59bd7b98f63a41b9a0ff4c343d0441`.
- GitNexus MCP impact/context returned `Transport closed`; CLI fallback reported LOW risk for `get_monitoring_db`, `list_strategies`, `create_strategy`, and `_handle_strategy_lifecycle_action`, with `0` affected processes.
- Added `get_strategy_monitoring_db()` in `web/backend/app/api/strategy_management/_helpers.py` as the route-provider backing wrapper for the existing strategy monitoring database helper.
- Moved `list_strategies`, `create_strategy`, `start_strategy`, `pause_strategy`, `resume_strategy`, and `stop_strategy` to `Depends(get_strategy_monitoring_db)`.
- `_handle_strategy_lifecycle_action` now accepts a monitoring database object and falls back to `get_strategy_monitoring_db()` when called without one.
- Direct `get_monitoring_db().log_operation(...)` calls in the target strategy files are `0`; dependency parameters are `6`; `monitoring_db.log_operation(...)` calls remain `6`.
- Focused provider TDD passed `1/1`; health route conflicts passed `121/121`; ruff passed on touched source/test files.
- Full strategy file test still reports the known pre-existing drift: `3 failed, 8 passed, 1 warning` for router prefix, route pair count, and chart-data wiring expectations.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, and no `monitoring_db` parameter leak on target strategy endpoints.
- Next gate after acceptance: G2.279 no-source strategy `get_monitoring_db` provider closeout / residual refresh.
- G2.278 must not be used as authority for risk helper changes, `web/backend/app/utils/risk_utils.py`, route registration, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or broader backend source.

## G2.279 Strategy get_monitoring_db Provider Closeout / Residual Refresh

Status: accepted/merged by PR `#432` at `fcead56344110e33041319271c122e71d2b763a0`.

- Parent PR `#431` merged at `c5496cab0a4213f74636af1c48772dc96c90bd1b`.
- Strategy direct `get_monitoring_db().log_operation(...)` calls in the target files are `0`; active strategy dependency parameters remain `6`; `monitoring_db.log_operation(...)` calls remain `6`.
- Risk route-body direct `get_monitoring_db().log_operation(...)` calls remain closed at `0`; risk provider wrappers remain retained.
- `web/backend/app/utils/risk_utils.py` remains a deferred utility same-name helper with `0` active API route-body log calls in this scan.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, and no `monitoring_db` parameter leak on target strategy/risk endpoints.
- Focused strategy provider test remains green at `1/1`; touched strategy ruff remains clean.
- Selected next gate after acceptance: G2.280 no-source service lifecycle residual candidate refresh after `get_monitoring_db` closeout.
- G2.279 must not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.280 Service Lifecycle Residual Candidate Refresh After get_monitoring_db

Status: accepted/merged by PR `#433` at `1707284bceeef8992641290d86790c1699975f5a`.

- Parent PR `#432` merged at `fcead56344110e33041319271c122e71d2b763a0`.
- Current scan covered `371` Python files under `web/backend/app/api` and `web/backend/app/services`.
- The scan found `572` getter-like names and `31` active interesting candidates after excluding method calls and known-closed surfaces.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, and `0` duplicate operation IDs.
- Highest service-only candidate is `get_integrated_services`, classified as root facade compatibility and deferred to a separate root facade decision.
- `get_indicator_registry` and `get_cache_manager` are ambiguous and deferred until ownership is disambiguated.
- `get_postgres_connection` is a control-plane DB helper and deferred to route/OpenAPI/control-plane ownership.
- Selected next gate after acceptance: G2.281 no-source data_lineage `get_lineage_tracker` ownership / route-provider decision.
- G2.280 must not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.281 data_lineage get_lineage_tracker Ownership / Route-Provider Decision

Status: accepted/merged by PR `#434` at `b8ba6ca75c573913d7b10553620e5d308c0d13f3`.

- Parent PR `#433` merged at `1707284bceeef8992641290d86790c1699975f5a`.
- `get_lineage_tracker` is defined in `web/backend/app/api/data_lineage.py` and returns a `LineageTracker` plus connection adapter created from an `asyncpg` raw connection.
- Active direct callers are `record_lineage`, `get_upstream_lineage`, `get_downstream_lineage`, `get_lineage_graph`, and `analyze_impact`.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, and the five `/api/v1/lineage` paths present.
- GitNexus CLI context found one symbol and five incoming calls; impact is MEDIUM with `5` impacted / direct callers and `0` affected processes.
- Limited autopilot stopped at this PR review gate because GitNexus risk is MEDIUM; human maintainer approved continuing into G2.282.
- Next gate after acceptance: `G2.282 no-source data_lineage get_lineage_tracker provider authorization package`.
- G2.281 must not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.282 data_lineage get_lineage_tracker Provider Authorization

Status: accepted/merged by PR `#435` at `891593d2dc4896f909333033a0b454529b9be38c`.

- Parent PR `#434` merged at `b8ba6ca75c573913d7b10553620e5d308c0d13f3`.
- G2.282 is a no-source authorization package only. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- GitNexus MCP context / impact returned `Transport closed`; CLI fallback using `Function:web/backend/app/api/data_lineage.py:get_lineage_tracker` returned MEDIUM risk with `5` impacted / direct symbols and `0` affected processes.
- The current route-local lifecycle is explicit: all five active handlers call `get_lineage_tracker()` and all five close the returned connection adapter with `await conn.close()`.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, and the five `/api/v1/lineage` paths present.
- Focused existing test inventory includes `tests/api/file_tests/test_data_lineage_api.py`, `tests/integration/test_data_lineage_tracker_integration.py`, `tests/unit/test_governance/test_data_lineage_tracker.py`, `tests/unit/test_governance/test_lineage.py`, and `web/backend/tests/test_data_lineage_regressions.py`.
- Authorized next gate after human acceptance: G2.283 path-limited `web/backend/app/api/data_lineage.py` route-provider implementation.
- Future G2.283 must preserve route paths, response models, OpenAPI shape, and connection cleanup semantics; it must rerun GitNexus before source edits and stop on HIGH or CRITICAL risk.
- G2.282 stopped at PR `#435` review and was human accepted because it authorized future source work and the target helper has MEDIUM impact.

## G2.283 data_lineage get_lineage_tracker Provider Implementation

Status: accepted/merged by PR `#436` at `511e9d091bc2b29777c522c595a9f1454f50b973`.

- Parent PR `#435` merged at `891593d2dc4896f909333033a0b454529b9be38c`.
- GitNexus MCP context / impact returned `Transport closed`; CLI fallback using `Function:web/backend/app/api/data_lineage.py:get_lineage_tracker` returned MEDIUM risk with `5` impacted / direct symbols and `0` affected processes.
- Added `get_lineage_tracker_dependency()` in `web/backend/app/api/data_lineage.py` as a route-local async generator provider that yields the existing tracker / connection adapter pair and closes the adapter in `finally`.
- Moved `record_lineage`, `get_upstream_lineage`, `get_downstream_lineage`, `get_lineage_graph`, and `analyze_impact` to `Depends(get_lineage_tracker_dependency)`.
- Direct route-body `get_lineage_tracker()` calls are `0`; manual route-body `await conn.close()` calls are `0`; dependency provider bindings are `5`.
- TDD RED recorded `2 failed, 1 passed`; GREEN recorded `3 passed`; focused data-lineage tests passed `15/15`; health route conflict regression passed `121/121`; ruff passed on touched files.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, lineage paths present, and no lineage provider parameter leaks.
- Next gate after acceptance: G2.284 no-source data_lineage `get_lineage_tracker` provider closeout / residual refresh.
- G2.283 must not be used as authority for non-data-lineage source edits, route registration, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or broader backend source.

## G2.284 data_lineage get_lineage_tracker Provider Closeout / Residual Refresh

Status: accepted/merged by PR `#437` at `d34774837a0582f0e33d47425bb017b44e5aacd9`.

- Parent PR `#436` merged at `511e9d091bc2b29777c522c595a9f1454f50b973`.
- G2.284 is a no-source closeout / residual refresh. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Current static closeout scan records direct route-body `get_lineage_tracker()` calls at `0`, provider backing call at `1`, manual route-body `await conn.close()` calls at `0`, `Depends(get_lineage_tracker_dependency)` bindings at `5`, and provider definition count at `1`.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, and the lineage paths present.
- Residual refresh keeps accepted closed surfaces out of the source candidate queue, including `get_config_manager`, `get_monitoring_db`, `get_postgres_async`, `get_data_quality_monitor`, and `get_lineage_tracker`.
- Root facade, registry, dashboard/cache, Redis client, and cache integration surfaces remain deferred to their respective ownership lanes.
- GitNexus CLI fallback for the selected next target `Function:web/backend/app/api/governance_dashboard.py:get_postgres_connection` returned MEDIUM risk with `5` direct callers, `6` impacted symbols, `0` affected processes, and a stale-index warning.
- Selected next gate after acceptance: G2.285 no-source `governance_dashboard.get_postgres_connection` ownership / control-plane route-provider decision.
- G2.284 must not be used as source implementation authorization; G2.285 must classify control-plane ownership before any future source lane.

## G2.285 governance_dashboard get_postgres_connection Ownership / Control-Plane Route-Provider Decision

Status: accepted/merged by PR `#438` at `bdfdeb353f725f9e875ab50ee4e8ed22902a5818`.

- Parent PR `#437` merged at `d34774837a0582f0e33d47425bb017b44e5aacd9`.
- G2.285 is a no-source ownership decision. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- `get_postgres_connection` is defined in `web/backend/app/api/governance_dashboard.py` at line `124` and currently belongs to the `/api/v1/governance` control-plane route module.
- Active direct route-body callers are `get_quality_overview`, `get_lineage_stats`, `get_assets_catalog`, `get_compliance_metrics`, and `get_dashboard_summary`.
- Current code has `5` direct `await get_postgres_connection()` route-body calls and `9` manual `await conn.close()` cleanup lines across the five handlers.
- Runtime/OpenAPI smoke with placeholder import-time environment values recorded `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, and the five governance dashboard paths present.
- GitNexus CLI fallback returned MEDIUM risk with `6` impacted symbols, `5` direct callers, `0` affected processes, and a stale-index warning. The stale index names one caller as `fetch_all_data`; current code truth is `get_dashboard_summary`.
- Decision: classify this as a bounded active control-plane route helper owned by `governance_dashboard.py`, not as a shared service facade, app-wide PostgreSQL provider, or route-registration issue.
- Recommended next gate after acceptance: G2.286 no-source `governance_dashboard.get_postgres_connection` provider authorization package.
- G2.285 must not be used as source implementation authorization; G2.286 is the only current authorization package for this surface.

## G2.286 governance_dashboard get_postgres_connection Provider Authorization

Status: accepted/merged by PR `#439` at `e7c78892e1928d86fabecbe4135e7ce68fd0f01e`.

- Parent PR `#438` merged at `bdfdeb353f725f9e875ab50ee4e8ed22902a5818`.
- G2.286 is a no-source authorization package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- It authorizes only a future G2.287 path-limited implementation after human acceptance.
- Future G2.287 may touch only `web/backend/app/api/governance_dashboard.py` plus focused governance dashboard tests: `tests/api/file_tests/test_governance_dashboard_api.py` and `web/backend/tests/test_governance_dashboard_postgres_provider.py`.
- Future G2.287 shape: add a route-local async generator provider, move only the five current governance dashboard handlers to `Depends(provider)`, and move connection cleanup into the provider finalizer.
- Future G2.287 must preserve route paths, `response_model` declarations, response metadata, OpenAPI exposure, operation IDs, current `UnifiedResponse` behavior, and error handling shape.
- Current route/OpenAPI smoke with placeholder import-time environment values records `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, and the five governance dashboard paths present.
- GitNexus CLI fallback still reports MEDIUM risk with `6` impacted symbols, `5` direct callers, `0` affected processes, and a stale-index warning.
- PR `#439` stopped for human review, was accepted, and merged at `e7c78892e1928d86fabecbe4135e7ce68fd0f01e`.
- G2.286 is superseded by G2.287 path-limited implementation.

## G2.287 governance_dashboard get_postgres_connection Provider Implementation

Status: accepted/merged by PR `#440` at `67ef9b9d8f9dd420de80995f624fa54e41493415`.

- Parent PR `#439` merged at `e7c78892e1928d86fabecbe4135e7ce68fd0f01e`.
- G2.287 is a path-limited source implementation package. It edits only `web/backend/app/api/governance_dashboard.py`, focused governance dashboard tests, steward evidence, this track, and the PR task card.
- It adds route-local async generator provider `get_governance_dashboard_postgres_connection`.
- It moves the five current governance dashboard handlers to `Depends(get_governance_dashboard_postgres_connection)`: `get_quality_overview`, `get_lineage_stats`, `get_assets_catalog`, `get_compliance_metrics`, and `get_dashboard_summary`.
- Post-change scan records direct route-body `await get_postgres_connection()` calls `0`, route-body manual `conn.close()` calls `0`, provider backing calls `1`, and dependency bindings `5`.
- TDD evidence: focused provider test failed `2/2` before implementation for missing provider, then passed `2/2` after implementation.
- Focused existing + new governance dashboard tests passed `14/14`; health route conflict regression passed `121/121`.
- Runtime/OpenAPI smoke with placeholder import-time environment values remains `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, five governance dashboard paths present, and no provider parameter leaks.
- GitNexus MCP still returned `Transport closed`; CLI fallback before source edit reported MEDIUM risk with `6` impacted symbols, `5` direct callers, `0` affected processes, and stale-index warning.
- PR `#440` stopped for human review, was accepted, and merged at `67ef9b9d8f9dd420de80995f624fa54e41493415`.
- Recommended next gate after human acceptance and merge: G2.288 no-source `governance_dashboard.get_postgres_connection` provider closeout / residual refresh.

## G2.288 governance_dashboard get_postgres_connection Provider Closeout / Residual Refresh

Status: accepted/merged by PR `#441` at `75ce550ceaf9f77b7659193b9cbd3c9ab2181c37`.

- Parent PR `#440` merged at `67ef9b9d8f9dd420de80995f624fa54e41493415`.
- G2.288 is a no-source closeout / residual refresh. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Current closeout scan records `get_governance_dashboard_postgres_connection` present, provider backing `await get_postgres_connection()` calls `1`, direct route-body `await get_postgres_connection()` calls `0`, route-body manual `conn.close()` calls `0`, and provider bindings `5`.
- Runtime/OpenAPI smoke with placeholder import-time environment values remains `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, the five governance dashboard paths present, and no provider parameter leaks.
- Active FastAPI route-handler getter scan found `47` remaining direct getter-like calls after excluding the just-closed governance dashboard and data lineage provider lanes.
- Selected next gate: G2.289 no-source `data_source_registry.get_manager` ownership / route-provider decision.
- Selected next target `Function:web/backend/app/api/data_source_registry.py:get_manager` has seven active route-body callers in `search_data_sources`, `get_category_stats`, `get_data_source`, `update_data_source`, `test_data_source`, `health_check_data_source`, and `health_check_all_data_sources`.
- GitNexus MCP impact returned `Transport closed`; CLI UID impact reports MEDIUM risk, `7` direct callers, `7` impacted symbols, `1` affected process, `1` affected module, and stale-index warning.
- PR `#441` must stop for human review and must not auto-merge because the selected next target has GitNexus MEDIUM impact and one affected process.
- G2.288 must not be used as source implementation authorization; G2.289 must classify ownership, route/OpenAPI exposure, lifecycle shape, and consumer-contract boundaries before any future authorization package.

## G2.289 data_source_registry get_manager Ownership / Route-Provider Decision

Status: accepted/merged by PR `#442` at `1f0a909355f5db9002cfc2d0fcbba21e366dc0bf`.

- Parent PR `#441` merged at `75ce550ceaf9f77b7659193b9cbd3c9ab2181c37`.
- G2.289 is a no-source ownership / route-provider decision. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- `get_manager` is defined in `web/backend/app/api/data_source_registry.py` at lines `61-65` and currently returns a fresh `DataSourceManagerV2()` instance.
- Active route-body callers are `search_data_sources`, `get_category_stats`, `get_data_source`, `update_data_source`, `test_data_source`, `health_check_data_source`, and `health_check_all_data_sources`.
- Current route/OpenAPI smoke with repo `.env` loaded into the subprocess records `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, and `7` data-source registry runtime routes.
- GitNexus MCP returned `Transport closed`; CLI fallback reports MEDIUM risk, `7` impacted symbols, `7` direct callers, `1` affected process, `1` affected module, and stale-index warning for `Function:web/backend/app/api/data_source_registry.py:get_manager`.
- Decision: classify this as a bounded active data-source registry route helper owned by `data_source_registry.py`, not as app-wide singleton lifecycle implementation, shared service facade retirement, route registration work, OpenAPI exposure work, or data-source schema migration.
- Recommended next gate after human acceptance: G2.290 no-source `data_source_registry.get_manager` provider authorization package.
- G2.289 must not be used as source implementation authorization; G2.290 should define exact implementation envelope and tests before any source lane starts.

## G2.290 data_source_registry get_manager Provider Authorization

Status: for review in future PR `#443`.

- Parent PR `#442` merged at `1f0a909355f5db9002cfc2d0fcbba21e366dc0bf`.
- G2.290 is a no-source authorization package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- It authorizes only a future G2.291 path-limited implementation after human acceptance.
- Future G2.291 may touch only `web/backend/app/api/data_source_registry.py`, focused data-source registry tests, steward evidence, and the future PR task card.
- Future G2.291 shape: add route-local provider `get_data_source_registry_manager` delegating to existing `get_manager()`, keep `get_manager()` as backing compatibility / monkeypatch seam, and move only the seven active data-source registry handlers to dependency parameters.
- Future G2.291 must preserve fresh `DataSourceManagerV2()` construction through `get_manager()` and must not introduce a process-level singleton.
- Current route/OpenAPI smoke with repo `.env` loaded into the subprocess records `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation IDs, and `7` data-source registry runtime routes.
- GitNexus MCP returned `Transport closed`; CLI fallback reports MEDIUM risk, `7` impacted symbols, `7` direct callers, `1` affected process, `1` affected module, and stale-index warning.
- PR `#443` must stop for human review and must not auto-merge because it authorizes future source work and the target has GitNexus MEDIUM impact with one affected process.
- G2.290 is superseded by G2.291 path-limited implementation.

## G2.291 data_source_registry get_manager Provider Implementation

- PR state: accepted/merged by PR `#444` at `3d161e90547720f4ce95111ea511d3f8dc3174dc`.
- Parent state: PR `#443` merged G2.290 at `e517163385e96a6c7115e14b77fb89819b4cead4`.
- G2.291 is a path-limited source implementation package. It edits only `web/backend/app/api/data_source_registry.py`, focused data-source registry tests, steward evidence, this track, and the PR task card.
- Implementation shape: add route-local provider `get_data_source_registry_manager` delegating to existing `get_manager()`, keep `get_manager()` as backing compatibility / monkeypatch seam, and move the seven active data-source registry handlers to `Depends(get_data_source_registry_manager)`.
- Result: direct route-body `get_manager()` calls are `0`, provider backing calls are `1`, and `Depends(get_data_source_registry_manager)` bindings are `7`.
- Compatibility: direct unit-call compatibility is retained through `_resolve_data_source_registry_manager` so tests that monkeypatch `data_source_registry.get_manager` remain valid.
- Route/OpenAPI: runtime routes `548`, OpenAPI paths `500`, duplicate operation IDs `0`, data-source runtime route count `16`.
- Verification: TDD red `3 failed`, TDD green `3 passed`, focused data-source registry suite `34 passed`, ruff changed files `All checks passed`, OpenSpec strict valid with PostHog telemetry noise only.
- GitNexus: MCP `context` and `impact` returned `Transport closed`; CLI fallback reports MEDIUM risk, `7` direct callers, `7` impacted symbols, `1` affected process, and stale-index warning for `Function:web/backend/app/api/data_source_registry.py:get_manager`.
- Stop rule: PR `#444` must stop for human review because it changes backend source/tests and the target has GitNexus MEDIUM impact with one affected process.
- Recommended next gate after human acceptance and merge: G2.292 no-source `data_source_registry.get_manager` provider closeout / residual refresh.

## G2.292 data_source_registry get_manager Provider Closeout / Residual Refresh

Status: accepted/merged by PR `#445` at `05cdf04f646d844c11e90e7c453ed4f985c8d382`.

- Parent PR `#444` merged at `3d161e90547720f4ce95111ea511d3f8dc3174dc`.
- G2.292 is a no-source closeout / residual refresh package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- It records the `data_source_registry.get_manager` provider lane as closed: direct route-body `get_manager()` calls are `0`, provider backing `get_manager()` calls are `1`, and `Depends(get_data_source_registry_manager)` bindings are `7`.
- Route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`, and `16` data-source runtime routes.
- Residual scan keeps `get_postgresql_session` as the next no-source ownership decision candidate because it spans auth, admin, and market route modules and resolves to a CRITICAL-impact core database helper.
- GitNexus MCP returned `Transport closed`; CLI fallback reports CRITICAL risk for `Function:web/backend/app/core/database.py:get_postgresql_session`.
- Stop rule: PR `#445` must stop for human review because the next selected target includes CRITICAL GitNexus impact.
- Recommended next gate after human acceptance and merge: G2.293 no-source `get_postgresql_session` ownership / route-provider decision.

## G2.293 get_postgresql_session Ownership / Route-Provider Decision

Status: accepted/merged by PR `#446`.

- Parent PR `#445` merged at `05cdf04f646d844c11e90e7c453ed4f985c8d382`.
- G2.293 PR `#446` merged at `a62d5e3fa4e9efbbe388e4bd317ae0cfae371319`.
- G2.293 is a no-source ownership / route-provider decision package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- It classifies `get_postgresql_session` as a cross-domain helper family, not a single implementation target.
- Current scan records `9` direct helper occurrences across `auth.py`, `v1/admin/audit.py`, `v1/admin/optimization.py`, and `market/market_data_request.py`; effective OpenAPI endpoint surface is `12`.
- Helper origins are split between `app.core.database.get_postgresql_session` and `app.core.database_factory.get_postgresql_session`.
- GitNexus MCP returned `Transport closed`; CLI fallback reports CRITICAL risk for `Function:web/backend/app/core/database.py:get_postgresql_session` and LOW risk for `Function:web/backend/app/core/database_factory.py:get_postgresql_session`.
- Route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`.
- Decision: do not modify shared helper definitions; split future route-provider work by route domain/helper origin.
- Recommended next gate after human acceptance and merge: G2.294 no-source admin audit database_factory `get_postgresql_session` provider authorization.
- Stop rule satisfied by PR `#446` human review and merge; G2.293 must not be used as source implementation authorization.

## G2.294 Admin Audit PostgreSQL Session Provider Authorization

Status: accepted/merged by PR `#447`.

- Parent PR `#446` merged at `a62d5e3fa4e9efbbe388e4bd317ae0cfae371319`.
- G2.294 PR `#447` merged at `a31fd3ede177d5851c2394b8cea2fe42188a4021`.
- G2.294 is a no-source authorization package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Target scope is only `web/backend/app/api/v1/admin/audit.py`, helper origin `app.core.database_factory.get_postgresql_session`.
- Current scan records `2` direct helper occurrences: `_load_audit_logs` and `get_audit_statistics`.
- Current cleanup semantics use `session.close()` in `finally` for both helper paths; any future implementation must preserve equivalent cleanup lifecycle.
- Route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`, with `3` admin audit routes in schema.
- GitNexus MCP returned `Transport closed`; CLI fallback reports LOW risk, `4` impacted symbols, `2` direct callers, `1` affected process, and `1` affected module for `Function:web/backend/app/core/database_factory.py:get_postgresql_session`.
- Decision: authorize only a future G2.295 path-limited admin audit provider implementation after PR `#447` human acceptance.
- Stop rule satisfied by PR `#447` human review and merge; G2.294 must not be used to expand source scope beyond G2.295.

## G2.295 Admin Audit PostgreSQL Session Provider Implementation

Status: for review in future PR `#448`.

- Parent PR `#447` merged at `a31fd3ede177d5851c2394b8cea2fe42188a4021`.
- G2.295 is a path-limited source implementation. It edits only `web/backend/app/api/v1/admin/audit.py`, `web/backend/tests/test_v1_audit_regressions.py`, and governance evidence.
- It adds `get_admin_audit_postgresql_session_factory`, wires `list_audit_logs`, `get_audit_log`, and `get_audit_statistics` through `Depends(...)`, and moves direct route-body session creation behind an injected `session_factory`.
- Direct route-body `get_postgresql_session()` calls after implementation are `0`; provider dependency bindings are `3`.
- Existing `session.close()` cleanup semantics remain in `finally` blocks.
- TDD evidence: targeted RED failed with missing `session_factory`; GREEN records `2 passed`; focused regression records `6 passed`.
- Ruff passes for the touched source/tests.
- Route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`, with `3` admin audit routes.
- GitNexus MCP returned `Transport closed`; CLI single-symbol fallback reports LOW risk, while staged verification reports MEDIUM risk with `1` affected process.
- Stop rule: PR `#448` must stop for human review because it changes backend source/tests and staged verification reports MEDIUM risk.
- Recommended next gate after human acceptance and merge: G2.296 no-source admin audit provider closeout / residual refresh.

## G2.296 Admin Audit PostgreSQL Session Provider Closeout / Residual Refresh

Status: for review in future PR `#449`.

- Parent PR `#448` merged at `48cf7e12637341451d8d77370306774df9c48729`.
- G2.296 is a no-source closeout / residual refresh package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- It records the admin audit provider lane as closed: direct route-body `get_postgresql_session()` calls are `0`, `Depends(get_admin_audit_postgresql_session_factory)` bindings are `3`, and retained `audit.py` references are compatibility/backing seams only.
- Route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`, with five runtime routes containing `audit`.
- Remaining `get_postgresql_session` residuals outside the closed admin audit lane are split across `auth.py`, `v1/admin/optimization.py`, and `market/market_data_request.py`, with `7` active direct route/helper calls.
- GitNexus MCP remains unreliable (`Transport closed` in this session); CLI fallback for `Function:web/backend/app/core/database.py:get_postgresql_session` reports CRITICAL risk, `15` direct dependants, `54` affected processes, and `13` affected modules with a stale-index warning.
- Stop rule: PR `#449` must stop for human review because the selected next residual family routes through the CRITICAL-impact core database helper.
- Recommended next gate after human acceptance and merge: G2.297 no-source core database `get_postgresql_session` residual route-domain decision.

## G2.297 Core Database PostgreSQL Session Route-Domain Decision

Status: for review in future PR `#450`.

- Parent PR `#449` merged at `030545a24b4a8c9a4df36d2f126eb4597685e0c0`.
- G2.297 is a no-source ownership / route-domain decision package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- The closed admin audit lane remains closed: direct route-body `get_postgresql_session()` calls are `0`, provider bindings are `3`.
- Remaining active direct calls under the `app.core.database.get_postgresql_session` family are split by route domain: auth account/password `4`, admin optimization control-plane `2`, market stock list `1`.
- Route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`.
- GitNexus MCP remains unreliable (`Transport closed` in this session); CLI fallback for `Function:web/backend/app/core/database.py:get_postgresql_session` reports CRITICAL risk, `15` direct dependants, `54` affected processes, and `13` affected modules with a stale-index warning.
- Decision: do not start source implementation from G2.297. Select only G2.298 no-source market stock list `get_postgresql_session` provider authorization because it is the smallest remaining route-domain surface.
- Stop rule: PR `#450` must stop for human review because the selected next candidate belongs to a CRITICAL shared helper family.

## G2.298 Market Stock List PostgreSQL Session Provider Authorization

Status: accepted/merged by PR `#451` at `79a4fe5ae9f763e3e836b76c051bddbed270a930`.

- Parent PR `#450` merged at `555ff35e0c82e172b4312c59bc67d3674bd6f0ab`.
- G2.298 is a no-source authorization package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Target is only `web/backend/app/api/market/market_data_request.py` route `GET /api/v1/market/stocks`, handler `get_stock_list`, with one direct `get_postgresql_session()` call.
- Existing focused test `web/backend/tests/test_market_stock_list_mock_configuration.py` passes `2/2`.
- Route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`, with one target market stock route.
- GitNexus MCP remains unreliable (`Transport closed` in this session); CLI fallback reports current shared helper sample as HIGH risk and `get_stock_list` as LOW risk, both with stale-index warning. G2.297 previously recorded CRITICAL for the shared helper, so the family remains treated as HIGH/CRITICAL.
- Decision: authorized only G2.299 path-limited market stock list provider implementation after PR `#451` human acceptance.
- Stop rule satisfied by PR `#451` human review and merge; G2.298 must not be used to expand source scope beyond G2.299.

## G2.299 Market Stock List PostgreSQL Session Provider Implementation

Status: accepted/merged by PR `#452` at `3d89c7e64a93c7f2ca074dc502762ad203f15bdc`.

- Parent PR `#451` merged at `79a4fe5ae9f763e3e836b76c051bddbed270a930`.
- G2.299 is a path-limited source implementation. It edits only `web/backend/app/api/market/market_data_request.py`, `web/backend/tests/test_market_stock_list_mock_configuration.py`, and governance evidence.
- Implementation adds route-local provider `get_market_stock_list_postgresql_session_factory`, moves `GET /api/v1/market/stocks` real-branch session creation behind `Depends(...)`, preserves `session.close()` cleanup in a `finally` block, and keeps the shared core helper definitions unchanged.
- Verification: TDD red `3 failed, 2 passed`; focused regression `5 passed`; ruff passed; runtime/OpenAPI remained `548/500/0` with one target market route.
- Residual state after implementation: market stock list direct `get_postgresql_session()` calls `0`; auth direct calls `4`; admin optimization direct calls `2`; admin audit remains closed with direct calls `0`.
- GitNexus MCP remains unreliable (`Transport closed`); CLI fallback reports `get_stock_list` LOW risk and shared `app.core.database.get_postgresql_session` CRITICAL risk, both with stale-index warnings. The index refresh attempt exceeded five minutes and later aborted in a native worker path, so it is recorded as a tooling limitation.
- Stop rule satisfied by PR `#452` human review and merge; G2.299 must not be used to expand source scope beyond the accepted market stock list provider seam.
- Recommended next gate after human acceptance and merge: G2.300 no-source market stock list provider closeout / residual refresh.

## G2.300 Market Stock List PostgreSQL Session Provider Closeout / Residual Refresh

Status: accepted/merged by PR `#453` at `d407acdd207271274aeb6614afdedbf139f640ae`.

- Parent PR `#452` merged at `3d89c7e64a93c7f2ca074dc502762ad203f15bdc`.
- G2.300 is a no-source closeout / residual refresh package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Market stock list provider lane is closed: direct `get_postgresql_session()` calls are `0`, `Depends(get_market_stock_list_postgresql_session_factory)` bindings are `1`, focused regression is `5 passed`, and runtime/OpenAPI remains `548/500/0`.
- Remaining `app.core.database.get_postgresql_session` residuals after market closeout: `auth.py` direct calls `4`; `v1/admin/optimization.py` direct calls `2`; admin audit remains closed with direct calls `0`.
- Decision: select only G2.301 no-source admin optimization `get_postgresql_session` ownership / provider-shape decision. Do not directly authorize source from G2.300 because the remaining admin optimization calls live in module helpers (`_run_maintenance`, `_database_status_payload`) that back multiple control-plane routes.
- GitNexus MCP remains unreliable (`Transport closed`); CLI fallback reports LOW risk for the two admin optimization helper symbols and CRITICAL risk for shared `app.core.database.get_postgresql_session`, all with stale-index warnings.
- Stop rule satisfied by PR `#453` human review and merge; G2.300 must not be used as source implementation authority.
- Recommended next gate after human acceptance and merge: G2.301 no-source admin optimization `get_postgresql_session` ownership / provider-shape decision.

## G2.301 Admin Optimization PostgreSQL Session Ownership / Provider-Shape Decision

Status: accepted/merged by PR `#454` at `13a81aec15fc8e98e7e4e927abe6d27e3e16f93d`.

- Parent PR `#453` merged at `d407acdd207271274aeb6614afdedbf139f640ae`.
- G2.301 is a no-source ownership / provider-shape decision package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Target file is `web/backend/app/api/v1/admin/optimization.py`, helper origin `app.core.database.get_postgresql_session`.
- Current active direct calls are `2`: one in `_run_maintenance` and one in `_database_status_payload`.
- The session helper path backs four OpenAPI-exposed handlers: `vacuum_database`, `analyze_database`, `reindex_database`, and `get_database_status`. `get_slow_queries` remains in the module but does not call the session helper and is excluded from the future provider scope.
- Focused current-behavior regression `web/backend/tests/test_v1_optimization_regressions.py` passes `5/5`; ruff passes on the route module and focused test.
- Route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`, with all five `/api/v1/optimization/*` routes present and schema-visible.
- GitNexus MCP remains unreliable (`Transport closed`); CLI fallback reports LOW risk for `_run_maintenance` and `_database_status_payload`, while `Function:web/backend/app/core/database.py:get_postgresql_session` remains CRITICAL with `15` direct dependants and `54` affected processes.
- Decision: classify admin optimization as a bounded control-plane route helper surface inside a CRITICAL shared helper family. Do not edit the shared helper definition or start source from G2.301.
- Candidate future provider shape: a route-local session-factory dependency such as `get_admin_optimization_postgresql_session_factory`, passed into the four affected handlers and then into the two helpers while preserving existing close/finally cleanup semantics.
- Recommended next gate after human acceptance and merge: G2.302 no-source admin optimization PostgreSQL session provider authorization.
- Stop rule satisfied by PR `#454` human review and merge; G2.301 must not be used as source implementation authority.
- Recommended next gate after human acceptance and merge: G2.302 no-source admin optimization PostgreSQL session provider authorization.

## G2.302 Admin Optimization PostgreSQL Session Provider Authorization

Status: accepted/merged by PR `#455` at `4af141da7411d30b31b972ace51d104ae28606ed`.

- Parent PR `#454` merged at `13a81aec15fc8e98e7e4e927abe6d27e3e16f93d`.
- G2.302 is a no-source authorization package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Authorized future source scope after PR `#455` human acceptance is limited to `web/backend/app/api/v1/admin/optimization.py` and `web/backend/tests/test_v1_optimization_regressions.py`, plus G2.303 governance evidence.
- Future implementation shape is route-local `get_admin_optimization_postgresql_session_factory`, injected into `vacuum_database`, `analyze_database`, `reindex_database`, and `get_database_status`, then passed into `_run_maintenance` and `_database_status_payload`.
- Future implementation must preserve existing `session.close()` in `finally` cleanup semantics and must keep `get_slow_queries` out of scope.
- Existing focused regression passes `5/5`; ruff passes on the target route module and focused test.
- Route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`, with five `/api/v1/optimization/*` routes present and schema-visible.
- GitNexus MCP remains unreliable (`Transport closed`); CLI fallback reports LOW risk for `_run_maintenance` and `_database_status_payload`, while `Function:web/backend/app/core/database.py:get_postgresql_session` remains CRITICAL with `15` direct dependants and `54` affected processes.
- Decision: authorize only future G2.303 path-limited implementation after PR `#455` human acceptance. Do not edit the shared helper definition, auth, market, admin audit, route contracts, docs/api, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Stop rule: PR `#455` must stop for human review because it authorizes backend source/test edits under a CRITICAL shared helper family.


## G2.303 Admin Optimization PostgreSQL Session Provider Implementation

Status: accepted/merged by PR `#456` at `1cc89b285cd265bce96991b8dc4c7e8bd71d85d0`.

- Parent PR `#455` merged at `4af141da7411d30b31b972ace51d104ae28606ed`.
- G2.303 is a path-limited backend source/test implementation package for `web/backend/app/api/v1/admin/optimization.py` and `web/backend/tests/test_v1_optimization_regressions.py`.
- Added route-local `get_admin_optimization_postgresql_session_factory` and injected it into `vacuum_database`, `analyze_database`, `reindex_database`, and `get_database_status`.
- Passed the injected factory into `_run_maintenance` and `_database_status_payload`; preserved existing `session.close()` in `finally` cleanup semantics.
- Kept `get_slow_queries` out of scope and did not edit shared `app.core.database.get_postgresql_session`.
- TDD RED recorded `2 failed, 5 passed`; GREEN focused regression records `7 passed`.
- Ruff passes on the target route module and focused test.
- Provider scan records `Depends` bindings `4`, provider backing calls `1`, helper direct `get_postgresql_session()` calls `0`.
- Route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`, with five `/api/v1/optimization/*` routes present and schema-visible.
- GitNexus MCP remains unreliable (`Transport closed`); CLI fallback reports LOW risk for target helpers/handlers and CRITICAL risk for shared `Function:web/backend/app/core/database.py:get_postgresql_session`.
- Stop rule: PR `#456` must stop for human review because it changes backend source/tests under a CRITICAL shared helper family.
- Recommended next gate after human acceptance and merge: G2.304 no-source admin optimization provider closeout / residual refresh.

## G2.304 Admin Optimization PostgreSQL Session Provider Closeout / Residual Refresh

Status: accepted/merged by PR `#457` at `d8e52a3b0000426a9ce278c5dbc1c4bbd8c6b4f9`.

- Parent PR `#456` merged at `1cc89b285cd265bce96991b8dc4c7e8bd71d85d0`.
- G2.304 is a no-source closeout / residual refresh package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Admin optimization provider lane is closed: helper-body direct `get_postgresql_session()` calls are `0`, provider backing calls are `1`, and `Depends(get_admin_optimization_postgresql_session_factory)` bindings are `4`.
- Focused optimization regression records `7 passed`; ruff passes on the target route module and focused test.
- Route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`, with five `/api/v1/optimization/*` routes present and schema-visible.
- Remaining active direct `get_postgresql_session()` residuals are now concentrated in `web/backend/app/api/auth.py`: `4` calls across `get_users`, `register_user`, `request_password_reset`, and `confirm_password_reset`.
- Market stock list direct calls remain `0`; admin audit direct calls remain `0`; admin optimization helper-body direct calls remain `0`.
- GitNexus CLI sampling keeps shared `Function:web/backend/app/core/database.py:get_postgresql_session` at CRITICAL risk with `15` direct dependants and `54` affected processes; auth source work remains forbidden from G2.304.
- Decision: close admin optimization and select only G2.305 no-source `auth.py get_postgresql_session` ownership / provider-shape decision after PR `#457` acceptance.
- Stop rule: G2.304 must not be used as auth source implementation authority.

## G2.305 Auth.py PostgreSQL Session Ownership / Provider-Shape Decision

Status: accepted/merged by PR `#458` at `8a6cfa615f472f23643a13ab18ab02dd0853ad96`.

- Parent PR `#457` merged at `d8e52a3b0000426a9ce278c5dbc1c4bbd8c6b4f9`.
- G2.305 is a no-source ownership / provider-shape decision package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Current auth surface has `4` direct `get_postgresql_session()` calls across `get_users`, `register_user`, `request_password_reset`, and `confirm_password_reset`.
- All four affected blocks retain `session.close()` in `finally`; `confirm_password_reset` also carries commit/rollback semantics that any future implementation must preserve.
- Focused auth tests record `10 passed, 18 skipped`; route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`.
- `ruff check --no-fix` records `6` existing F401/F811 issues in `auth.py`; they were not fixed because G2.305 is no-source.
- Decision: classify auth as a security-sensitive route-domain surface inside the CRITICAL shared `app.core.database.get_postgresql_session` helper family.
- Recommended next gate after PR `#458` acceptance: G2.306 no-source auth.py `get_postgresql_session` provider authorization.
- Stop rule: G2.305 must not be used as auth source implementation authority.

## G2.306 Auth.py PostgreSQL Session Provider Authorization

Status: accepted/merged by PR `#459` at `702816e7aa23378b2acd5dbc27de449fc74a3af5`.

- Parent PR `#458` merged at `8a6cfa615f472f23643a13ab18ab02dd0853ad96`.
- G2.306 is a no-source authorization package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Current auth surface remains `4` direct `get_postgresql_session()` calls across `get_users`, `register_user`, `request_password_reset`, and `confirm_password_reset`.
- Future G2.307 may only add a route-local auth PostgreSQL session factory provider, inject it into the four affected handlers, and preserve close/finally plus `confirm_password_reset` commit/rollback semantics.
- Focused auth tests record `10 passed, 18 skipped`; route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`.
- `ruff check --no-fix` records `6` existing F401/F811 issues in `auth.py`; they were not fixed because G2.306 is no-source.
- GitNexus MCP impact returned `Transport closed`; CLI fallback keeps the shared `Function:web/backend/app/core/database.py:get_postgresql_session` family at `CRITICAL` with `15` direct dependants and `54` affected processes.
- Recommended next gate after PR `#459` acceptance: G2.307 path-limited auth PostgreSQL session provider implementation.
- Stop rule: G2.307 is a source implementation PR and must stop at human review before merge.

## G2.307 Auth.py PostgreSQL Session Provider Implementation

Status: accepted/merged by PR `#460` at `833856a526c3083aa4c21a28d31b36ee2a82e9bd`.

- Parent PR `#459` merged at `702816e7aa23378b2acd5dbc27de449fc74a3af5`.
- G2.307 is a path-limited source implementation package. It edits only `web/backend/app/api/auth.py`, `web/backend/tests/test_auth_login_contract.py`, and governance evidence records.
- Implementation adds `get_auth_postgresql_session_factory`, injects it into `get_users`, `register_user`, `request_password_reset`, and `confirm_password_reset`, and reduces route-body direct `get_postgresql_session()` calls in those handlers to `0`.
- Provider backing `get_postgresql_session()` calls are `1`; route/OpenAPI remains `548` routes, `500` paths, duplicate operation IDs `0`.
- TDD RED: new provider dependency test failed with missing `get_auth_postgresql_session_factory`. GREEN: target test passed, focused auth regression records `11 passed, 18 skipped`.
- Ruff is clean for `auth.py` and focused auth tests. Compatibility exports `verify_token` and `get_current_active_user` remain available from `app.api.auth`.
- GitNexus MCP impact returned `Transport closed`; CLI fallback keeps shared `Function:web/backend/app/core/database.py:get_postgresql_session` at `CRITICAL`, and the shared helper definition is intentionally untouched.
- Recommended next gate after human acceptance and merge: G2.308 no-source auth provider closeout / residual refresh.
- Stop rule: PR `#460` changes backend source/tests and must not auto-merge.

## G2.308 Auth.py PostgreSQL Session Provider Closeout / Residual Refresh

Status: accepted/merged by PR `#461`.

- Parent PR `#460` merged at `833856a526c3083aa4c21a28d31b36ee2a82e9bd`.
- G2.308 is a no-source closeout / residual refresh package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Auth provider lane is closed: route-body direct `get_postgresql_session()` calls are `0`, provider backing call is `1`, and dependency bindings are `4`.
- Focused auth tests record `11 passed, 18 skipped`; ruff is clean; route/OpenAPI smoke remains `548` routes, `500` paths, duplicate operation IDs `0`.
- Tracked auth / admin optimization / market stock-list / admin audit route-domain active route-body direct `get_postgresql_session()` residuals are now `0`.
- Provider backing calls remain by design in `auth.py` and admin optimization; import-only residuals remain in market stock-list and admin audit files.
- PR `#461` merged at `03ec65d765a72f131609e28d5121ec498dd6b54e`.
- Recommended next gate after PR `#461` acceptance: G2.309 no-source service lifecycle residual candidate refresh after auth provider closeout.
- Stop rule: G2.308 must not be used as source implementation authority.

## G2.309 Service Lifecycle Residual Candidate Refresh After Auth Provider Closeout

Status: accepted/merged by PR `#462`.

- Parent PR `#461` merged at `03ec65d765a72f131609e28d5121ec498dd6b54e`.
- G2.309 is a no-source residual candidate refresh. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- The refreshed scanner covered `371` Python files under `web/backend/app/api` and `web/backend/app/services`, saw `663` getter-like names, and retained `54` active interesting candidates after excluding closed G2 provider seams.
- Top deferred surfaces include data-source-config, dashboard/cache, control-plane DB engine, risk core, realtime MTM, circuit breaker, algorithms module loader, indicator registry factory, Kronos client, and system routing helpers.
- G2.309 selects only G2.310 no-source `get_mysql_session` ownership / route-provider decision for `web/backend/app/api/indicators/create_indicator_config.py`, where five bare route-body calls remain at lines `60`, `129`, `189`, `251`, and `331`.
- PR `#462` merged at `5d24bed2e77bcb142a81e1b1bcc68a1cdca27d18`.
- Stop rule: G2.309 must not be used as source implementation authority or as authorization to edit `get_mysql_session`, `create_indicator_config.py`, route contracts, OpenAPI artifacts, tests, or runtime state.

## G2.310 get_mysql_session Ownership / Route-Provider Decision

Status: accepted/merged by PR `#463`.

- Parent PR `#462` merged at `5d24bed2e77bcb142a81e1b1bcc68a1cdca27d18`.
- G2.310 is a no-source ownership decision. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- The five bare `get_mysql_session()` calls are all in `web/backend/app/api/indicators/create_indicator_config.py` at lines `60`, `129`, `189`, `251`, and `331`.
- `create_indicator_config.py` defines an `APIRouter`, but the current registered `indicators.router` comes from `indicator_cache.py`; route-table smoke records `0` registered `create_indicator_config.py` handlers, `548` FastAPI routes, `500` OpenAPI paths, and duplicate operation IDs `0`.
- GitNexus MCP impact returned `Transport closed`; CLI fallback reports `Function:web/backend/app/core/database.py:get_mysql_session` as `MEDIUM` risk with direct `5`, affected processes `0`, affected modules `0`, stale index with commits behind `0`.
- Decision: do not authorize a provider implementation lane yet; first decide whether the indicator configuration CRUD router should be registered, retired, or retained dormant.
- Recommended next gate: G2.311 no-source indicator config router ownership / registration-retirement decision.
- PR `#463` merged at `67083d40808fea9963137e3e128c0c6cb0683e57`.
- Stop rule: G2.310 must not be used as source implementation authority or as authorization to edit `get_mysql_session`, `create_indicator_config.py`, route registration, OpenAPI artifacts, tests, or runtime state.

## G2.311 Indicator Config Router Ownership / Registration-Retirement Decision

Status: accepted/merged by PR `#464`.

- Parent PR `#463` merged at `67083d40808fea9963137e3e128c0c6cb0683e57`.
- G2.311 is a no-source route ownership decision. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- `create_indicator_config.py` is classified as retained dormant route code: it defines `/configs` CRUD handlers, but route-table smoke records `0` registered handlers from that module and `0` OpenAPI `/configs` CRUD paths from that module.
- Current route/OpenAPI snapshot remains `548` FastAPI routes, `500` OpenAPI paths, duplicate operation IDs `0`, with `13` indicator-related active routes.
- Decision: do not register the dormant router and do not retire/delete it from G2.311; exclude it from the active service lifecycle provider implementation candidate queue.
- Recommended next gate: G2.312 no-source service lifecycle residual candidate refresh after dormant indicator-config exclusion.
- PR `#464` merged at `0f5382cea875d2983ada5d9c63548b0530861002`.
- Stop rule: G2.311 must not be used as source implementation authority or as authorization to edit route registration, OpenAPI artifacts, tests, `create_indicator_config.py`, or `get_mysql_session`.

## G2.312 Service Lifecycle Residual Candidate Refresh After Dormant Indicator-Config Exclusion

Status: accepted / merged by PR `#465`.

- Parent PR `#464` merged at `0f5382cea875d2983ada5d9c63548b0530861002`.
- G2.312 is a no-source residual candidate refresh. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- The refreshed scanner covered `371` Python files under `web/backend/app/api` and `web/backend/app/services`, saw `663` getter-like names, and retained `53` active interesting candidates after excluding closed G2 provider seams plus dormant `create_indicator_config.py` / `get_mysql_session`.
- Top deferred surfaces include data-source-config, data/cache, dashboard/cache, control-plane DB engine, risk core, realtime MTM, circuit breaker, algorithms module loader, Kronos client, and system routing helpers.
- G2.312 selects only G2.313 no-source `indicator_registry.get_factory` ownership / route-provider decision for `web/backend/app/api/indicator_registry.py`, where three bare route-body calls remain at lines `159`, `186`, and `201`.
- Stop rule: G2.312 must not be used as source implementation authority or as authorization to edit `indicator_registry.py`, `get_factory`, route contracts, OpenAPI artifacts, tests, or runtime state.

## G2.313 Indicator Registry `get_factory` Ownership / Route-Provider Decision

Status: accepted / merged by PR `#466`.

- Parent PR `#465` merged at `ac6b9faaf9cf7d2e04b29da08a2c28bce7d4fb18`.
- G2.313 is a no-source ownership decision. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- G2.313 classifies `web/backend/app/api/indicator_registry.py:get_factory` as an active route-local singleton factory helper, not a dormant route surface.
- Runtime route/OpenAPI smoke records `548` FastAPI routes, `500` OpenAPI paths, `0` duplicate operation ID warnings, and three registered indicator-registry routes: `/api/indicator-registry/indicators`, `/api/indicator-registry/indicators/{indicator_id}`, and `/api/indicator-registry/calculate`.
- GitNexus MCP impact failed with `Transport closed`; CLI fallback records `LOW` risk, `3` direct callers, `0` affected processes, and stale index with `commits_behind=0`.
- G2.313 selects only G2.314 no-source `indicator_registry.get_factory` provider authorization package. If G2.314 is accepted, any future source implementation lane must stop at human review before merge.
- Stop rule: G2.313 must not be used as source implementation authority or as authorization to edit `indicator_registry.py`, route contracts, OpenAPI artifacts, tests, docs/api, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.314 Indicator Registry `get_factory` Provider Authorization

Status: accepted / merged by PR `#467`.

- Parent PR `#466` merged at `75f6c63023bec35453892f63aaeaf193023e4881`.
- G2.314 is a no-source authorization package. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- G2.314 authorizes only a future G2.315 source implementation lane limited to `web/backend/app/api/indicator_registry.py` and `tests/api/file_tests/test_indicator_registry_api.py`.
- Required future shape: route-local provider dependency for `IndicatorFactory`, no route/OpenAPI contract drift, three handlers moved away from route-body `get_factory()`, and `get_factory()` retained as backing compatibility seam unless separately retired.
- Stop rule: G2.315 must stop at human review before merge and must not be auto-merged under the no-source autopilot rule.

## G2.315 Indicator Registry `get_factory` Provider Implementation

Status: accepted / merged by PR `#468`.

- Parent PR `#467` merged at `8d52fa0548fd200f0c9b606e5880e71286c07d10`.
- G2.315 edits only `web/backend/app/api/indicator_registry.py`, `tests/api/file_tests/test_indicator_registry_api.py`, and governance artifacts.
- Implementation moves all three indicator-registry routes to `Depends(get_indicator_factory)`, retains `get_factory()` as the backing compatibility seam, and preserves route/OpenAPI `548/500/0`.
- TDD evidence: RED `2 failed, 9 passed`; GREEN `11 passed, 1 warning`.
- Verification: health collect-only 121 tests collected, ruff focused pass, provider scan route-body direct calls `0`, backing calls `1`, dependency bindings `3`.
- Stop rule: PR `#468` must be manually reviewed and must not be auto-merged.

## G2.316 Indicator Registry Factory Provider Closeout / Residual Refresh

Status: accepted / merged by PR `#469`.

- Parent PR `#468` merged at `8b09c714784ce90a1a8b1fe938e5904a81110094`.
- PR `#469` merged at `be512826ca7ba60d9609ddf9035522c1f863907c`.
- G2.316 is a no-source closeout / residual refresh. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Closeout result: `indicator_registry.get_factory` route-body direct calls are `0`, provider backing calls are `1`, `Depends(get_indicator_factory)` bindings are `3`, focused test remains `11 passed`, and route/OpenAPI remains `548/500/0`.
- Residual refresh selected G2.317 no-source `data_source_config.get_config_manager` ownership / provider seam decision.
- The selected next candidate is high-risk: GitNexus MCP impact failed with `Transport closed`, and CLI fallback resolved `web/backend/app/api/_data_source_config_responses.py:get_config_manager` as `HIGH`, with `9` direct callers and `3` affected processes.
- Stop rule: G2.316 must not be used as source implementation authority or as authorization to edit `data_source_config.py`, `_data_source_config_responses.py`, route contracts, OpenAPI artifacts, tests, docs/api, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.317 Data Source Config `get_config_manager` Ownership / Provider Seam Decision

Status: accepted / merged by PR `#470`.

- Parent PR `#469` merged at `be512826ca7ba60d9609ddf9035522c1f863907c`.
- PR `#470` merged at `b51afb8c3bfd371eaa6838877d8fb0df8fe11bbd`.
- G2.317 is a no-source ownership / provider seam decision. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- Current route shape is already providerized: all `9` active `app.api.data_source_config` routes use `Depends(get_config_manager_dependency)`.
- Residual route-body direct `get_config_manager()` calls are `0`; the route-local provider has `1` backing call to `get_config_manager()` at `data_source_config.py:103`.
- The backing helper remains in `web/backend/app/api/_data_source_config_responses.py:338-352`, which also owns response/router helper responsibilities.
- Route/OpenAPI smoke records `548` FastAPI routes, `500` OpenAPI paths, and `0` duplicate operation ID warnings.
- GitNexus MCP impact failed with `Transport closed`; CLI fallback resolved `web/backend/app/api/_data_source_config_responses.py:get_config_manager` as `HIGH`, with `9` direct callers and `3` affected processes.
- Decision: retain the current backing seam for now. G2.317 does not authorize moving `get_config_manager`, splitting `_data_source_config_responses.py`, changing route contracts, or editing tests.
- Next gate: G2.318 no-source service lifecycle residual candidate refresh after retaining `data_source_config.get_config_manager` as a high-risk backing seam.
- Stop rule: G2.317 must not be used as source implementation authority or as authorization to edit `data_source_config.py`, `_data_source_config_responses.py`, route contracts, OpenAPI artifacts, tests, docs/api, frontend, config, scripts, OpenSpec, PM2, or runtime state.

## G2.318 Service Lifecycle Residual Refresh After Data Source Config

Status: for review in future PR `#471`.

- Parent PR `#470` merged at `b51afb8c3bfd371eaa6838877d8fb0df8fe11bbd`.
- G2.318 is a no-source residual candidate refresh. It does not edit backend source, tests, route contracts, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state.
- G2.318 retains `data_source_config.get_config_manager` as a high-risk backing seam and does not reopen its source path.
- Residual scan records `371` Python files, `96` active API modules, `736` getter definitions, `194` active route-body getter groups, and route/OpenAPI `548/500/0`.
- The top refreshed candidate family is `web/backend/app/api/watchlist.py`: `15` registered routes, `8` route-body `DataSourceFactory()` constructions, `8` `get_data_source("watchlist")` calls, and `8` adapter `get_data(...)` calls.
- GitNexus MCP impact for the next target family failed with `Transport closed`; CLI fallback for `get_data_source` is ambiguous with `8` candidates and `UNKNOWN` risk.
- G2.318 selects only G2.319 no-source `watchlist` DataSourceFactory ownership / route-provider decision. G2.319 must disambiguate DataSourceFactory impact before any authorization package or source lane.
- Stop rule: G2.318 must not be used as source implementation authority or as authorization to edit `watchlist.py`, DataSourceFactory, route contracts, OpenAPI artifacts, tests, docs/api, frontend, config, scripts, OpenSpec, PM2, or runtime state.
