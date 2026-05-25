# Backend AdvancedAnalysis Compatibility Getter Phase 1 Authorization - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.87 AdvancedAnalysis compatibility getter Phase 1 authorization

Status: ready for review

Branch: `g2-87-advanced-analysis-compat-getter-phase1-authorization`

Current HEAD: `a20c92eef786ee816d0a8c171641c292ba2455f8`

Prepared at: `2026-05-25T16:39:45+08:00`

## Purpose

Authorize a future G2.88 source implementation for
`AdvancedAnalysisService` Phase 1 service-internal decoupling.

This authorization does not implement the change. It defines the future source
scope, tests, rollback point, and hard boundaries for the next branch.

## Input State

| Item | Current state |
|---|---|
| PR `#239` | `MERGED` at `a20c92eef786ee816d0a8c171641c292ba2455f8` |
| Issue `#79` | `OPEN`, `needs-triage` |
| Issue `#92` | `OPEN`, `enhancement`, `ready-for-human`, `ready-for-downstream` |
| G2.86 decision | Select `AdvancedAnalysisService` as next Phase 1 authorization candidate |
| Standards basis | `architecture/STANDARDS.md` compatibility closure and cleanup approval rules |

## Current-Head Evidence

| Metric | Result |
|---|---:|
| `get_advanced_analysis_service` total Python hits | 4 |
| `get_advanced_analysis_service` production hits | 2 |
| `get_advanced_analysis_service` route/API hits | 0 |
| `get_advanced_analysis_service` test hits | 2 |
| `get_advanced_analysis_service_dependency` total refs | 19 |
| `get_advanced_analysis_service_dependency` route/API refs | 15 |
| `install_advanced_analysis_service` total refs | 2 |
| `ADVANCED_ANALYSIS_SERVICE_STATE_KEY` total refs | 8 |

Current production public getter hits:

| File | Role |
|---|---|
| `web/backend/app/services/advanced_analysis_service.py:492` | public compatibility getter definition |
| `web/backend/app/services/advanced_analysis_service.py:502` | dependency-provider fallback call to the public getter |

GitNexus impact:

| Target | Risk | Impacted count | Processes affected |
|---|---|---:|---:|
| `get_advanced_analysis_service` | LOW | 0 | 0 |

Verification:

| Check | Result |
|---|---|
| `test_advanced_analysis_service_lifecycle_di.py` | 4 passed in 3.61s |
| `test_health_route_conflicts.py` | 120 passed in 74.50s |
| OpenAPI smoke with root `.env` loaded | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |
| GitNexus `detect_changes(scope=staged)` | LOW, changed files=`4`, changed symbols=`0`, affected processes=`0` |

## Authorized Future G2.88 Scope

Only a future G2.88 implementation branch may edit:

- `web/backend/app/services/advanced_analysis_service.py`;
- `web/backend/tests/test_advanced_analysis_service_lifecycle_di.py`;
- its own implementation report, generated artifact, task card, and steward-tree
  entry.

The intended implementation shape is:

- add a private async initializer, for example
  `_get_or_create_advanced_analysis_service()`;
- retarget `get_advanced_analysis_service_dependency()` so the fallback path no
  longer calls public `get_advanced_analysis_service()`;
- keep public `get_advanced_analysis_service()` in Phase 1;
- keep `get_advanced_analysis_service_dependency()`;
- keep `install_advanced_analysis_service()`;
- keep `ADVANCED_ANALYSIS_SERVICE_STATE_KEY`;
- update focused lifecycle tests so they prove the provider fallback does not
  depend on the public compatibility getter.

## Required Future G2.88 Gates

Before any source edit in G2.88:

1. Run GitNexus impact/context for `get_advanced_analysis_service`.
2. Add or update a focused lifecycle test that fails before implementation.
3. Confirm no route/API direct public getter call exists.

Before a G2.88 commit:

1. Run focused lifecycle tests.
2. Run `test_health_route_conflicts.py`.
3. Run touched-path `ruff check` and `black --check`.
4. Run configured OpenAPI smoke.
5. Run staged GitNexus `detect_changes(scope=staged)`.
6. Run mainline scope gate.

## Explicit Non-Goals

This authorization does not permit:

- deleting, renaming, or privatizing public `get_advanced_analysis_service()`;
- removing `get_advanced_analysis_service_dependency()`;
- removing `install_advanced_analysis_service()`;
- removing `ADVANCED_ANALYSIS_SERVICE_STATE_KEY`;
- editing route/API files;
- changing route paths, response models, response shapes, or OpenAPI exposure;
- editing frontend files;
- changing runtime/PM2 state;
- changing OpenSpec files;
- moving GitHub issue labels;
- touching broad `DataService`, `StrategyService`, StockSearch, TDX, or
  MarketData service seams.

## Rollback

If the future G2.88 implementation fails tests or reveals a hidden public getter
consumer, revert the implementation branch and keep the public compatibility
getter as the fallback path. This G2.87 authorization can remain as historical
evidence or be superseded by a fresh decision packet.

## Next Gate

Human review / PR merge decision for this G2.87 authorization packet.

If accepted, create a separate G2.88 implementation branch. Do not edit
AdvancedAnalysis source in this authorization PR.
