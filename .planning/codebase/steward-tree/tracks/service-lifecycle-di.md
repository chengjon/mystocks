# Track: Service Lifecycle DI

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active track summary
- Prepared at: `2026-05-28T02:10:15+08:00`
- Base HEAD checked: `ea659d52903a5e9884d396069526ea08f15109a6`

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
| G2.194 data-quality adapter constructor seam design | For review | Selects `adapter_split` constructor provider authorization as the next gate, defines test-double contract, and keeps source authority at none |

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

## Next Gates

- Review G2.194 data-quality adapter constructor seam design decision.
- If accepted, start G2.195 data-quality `adapter_split` constructor provider
  authorization package.
- Do not start adapter constructor implementation from G2.194.
- Do not batch service adapters, legacy adapters, `market_data_adapter.py`, or
  singleton-wrapper migration with `adapter_split` constructor migration.
- Do not expand into alerts resolver fixes, legacy `app.api.risk_management`
  restoration, or other risk route provider migrations.

## Forbidden Scope

This track summary forbids:

- backend source edits
- frontend edits
- test edits
- OpenSpec proposal creation
- issue label changes
- moving another service candidate directly to implementation
- treating service inventory counts as implementation backlogs
