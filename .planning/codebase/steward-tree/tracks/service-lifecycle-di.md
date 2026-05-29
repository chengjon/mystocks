# Track: Service Lifecycle DI

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active track summary
- Prepared at: `2026-05-29T10:56:00+08:00`
- Base HEAD checked: `854878cd2e09384daddaa8547e8cebc970ec2b74`

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

## Next Gates

- Review G2.232 data-source config manager provider authorization.
- If accepted, start G2.233 data-source config manager route provider injection.
- Do not reopen cache prewarming source work without contradictory current-HEAD
  evidence.
- Do not edit `data_source_config.old.py` from G2.233.
- Do not edit `_data_source_config_responses.py` from G2.233 unless a later
  package explicitly authorizes response/dependency separation.
- Do not expand into route paths, response models, SQL queries, error-contract
  behavior, `get_unified_data_service`, or frontend code.
- Do not open another data-quality monitor source lane unless fresh current-HEAD evidence contradicts the accepted closeout.
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
