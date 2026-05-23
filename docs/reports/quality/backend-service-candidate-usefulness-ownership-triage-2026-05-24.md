# Backend Service Candidate Usefulness And Ownership Triage - 2026-05-24

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: prepared for human review

Scope: G2.43 decision-only packet after PR #182. This report records current
HEAD evidence, candidate usefulness, ownership, and the next authorization gate.
It does not authorize backend source edits, route changes, OpenSpec changes,
issue label changes, compatibility getter cleanup, or implementation work.

## Current State

| Field | Value |
|---|---|
| Current HEAD | `f7c6fdf5fd57cff14ef6d11f1d18fd6591a22dc5` |
| Parent PR | `#182` merged |
| Parent issue | `#79` remains `OPEN` / `needs-triage` |
| Parent decision context | `#92` remains `OPEN` / `enhancement`, `ready-for-human`, `ready-for-downstream` |
| Workline | G2.43 service candidate usefulness and ownership triage |
| Runtime/source scope | none |

## Method

The triage used current-head static evidence only:

- active symbol reference scan for candidate getters/classes;
- route-file dependency pattern scan;
- prior G2.42 service lifecycle DI candidate refresh evidence;
- current GitHub state for issue `#79`, issue `#92`, and PR `#182`.

Because this is a decision-only governance packet, no `app.main` smoke,
OpenAPI generation, pytest run, or source-code impact analysis is required here.
Those gates belong to a later implementation authorization packet.

## Candidate Disposition

| Candidate | Current evidence | Disposition |
|---|---|---|
| `AdvancedAnalysisService` | `web/backend/app/services/advanced_analysis_service.py` has `480` lines. `get_advanced_analysis_service` has no active external reference outside its own definition. `AdvancedAnalysisService` has active route usage in `web/backend/app/api/advanced_analysis_api.py`; the route file has `14` routes and `14` class-based `Depends()` service parameters. | Active route service. Do not delete. Best next decision candidate for a separate G2.44 route-provider migration authorization packet. |
| `WencaiService` | `web/backend/app/services/wencai_service.py` has `430` lines. `get_wencai_service` has no active external reference outside its own definition. `WencaiService` is active in `web/backend/app/api/wencai.py`, `web/backend/app/tasks/wencai_tasks.py`, `src/database/services/database_service.py`, and deployment script references; `web/backend/app/api/wencai.py` has `8` direct `WencaiService(db=db)` constructor sites. | Active DB/session-backed service. Do not treat as a singleton DI pilot. Do not clean up the getter without a later impact/test/route-contract packet. |
| `get_market_data_service` / `MarketDataService` | `web/backend/app/services/market_data_service/get_market_data_service.py` is a `33` line active dependency module. `web/backend/app/api/market/market_data_request.py` has `11` routes and `7` `Depends(get_market_data_service)` sites. `MarketDataService` has broad service, route, test, and governance references. | Active broad market-data seam. Not a retirement candidate. Any future change needs a dedicated route/provider design packet, not a micro cleanup. |
| `UnifiedDataService` | `web/backend/app/services/unified_data_service.py` has `613` lines. `get_unified_data_service` is used internally in the same module. `web/backend/app/api/industry_concept_analysis.py` has `5` routes and `2` direct `UnifiedDataService()` construction sites. | Broad data seam. Not a clean direct implementation target. Needs separate ownership/design review before source edits. |
| `DataService`, `StrategyService`, `TechnicalAnalysisService` | These remain broad service seams with larger blast-radius risk and are not narrowed by the G2.42 refresh. | Explicitly excluded from immediate implementation selection in this packet. |

## Decision

Do not select an implementation target in G2.43.

The next useful step is a separate G2.44 authorization packet for
`AdvancedAnalysisService` route-provider migration. The authorization packet
should decide whether to replace class-based route `Depends()` construction with
an app-state/request-scoped provider while preserving route paths, response
contracts, OpenAPI behavior, and any current test expectations.

This report does not authorize that implementation. It only recommends the
next packet.

## Required Boundary For G2.44

If G2.44 is opened, it must be a separate reviewable authorization packet before
source edits. It should include:

- allowed source scope, if any;
- exact route handlers and dependency sites;
- pre-edit GitNexus impact/context requirement;
- focused pytest targets;
- OpenAPI route/path/operation ID smoke;
- compatibility fallback decision for `get_advanced_analysis_service`;
- rollback plan;
- explicit non-goals for `WencaiService`, `MarketDataService`,
  `UnifiedDataService`, `DataService`, `StrategyService`, and
  `TechnicalAnalysisService`.

## Non-Goals

- No backend source changes.
- No backend test changes.
- No OpenSpec change/spec/archive operation.
- No GitHub issue label changes.
- No compatibility getter cleanup or retirement.
- No broad service lifecycle migration.
- No route/OpenAPI contract modification.

## Evidence Summary

| Evidence | Result |
|---|---|
| Current HEAD | `f7c6fdf5fd57cff14ef6d11f1d18fd6591a22dc5` |
| PR `#182` | `MERGED` |
| `#79` | `OPEN`, `needs-triage` |
| `#92` | `OPEN`, `enhancement`, `ready-for-human`, `ready-for-downstream` |
| `get_advanced_analysis_service` | definition-only active reference |
| `AdvancedAnalysisService` | active route class dependency in `advanced_analysis_api.py` |
| `get_wencai_service` | definition-only active reference |
| `WencaiService` | active DB/session-backed service with direct route constructors |
| `get_market_data_service` | active route dependency, `7` route dependency sites |
| `UnifiedDataService` | active broad data seam with direct route constructors |

## Recommendation

After human review of this packet, create G2.44:

`AdvancedAnalysisService` route-provider migration authorization.

Keep implementation locked until that packet is explicitly reviewed and
approved.
