# G2.330 Service Lifecycle DI Global Residual Candidate Screening

Date: 2026-06-03

## Gate

- Node: `G2.330`
- Mode: `planned_no_source`
- `source_edit_authority`: `false`
- Authorized work: global residual candidate inventory and screening only
- Not authorized: source edits, symbol rewrites, provider implementation, deletion, cleanup, or compatibility-layer retirement

## Governance Baseline

- `architecture/STANDARDS.md` confirms cleanup/deletion and compatibility-layer convergence require explicit governance and cannot be inferred from static usage alone.
- GitNexus query was used for code-intelligence orientation only. The index reported stale status (`current_commit_differs_from_indexed_commit`), so GitNexus results are evidence hints, not an authoritative current-source inventory.
- Current branch observed during screening: `wip/root-dirty-20260403`.
- Current dirty-source note for this screening: `web/backend/app/api/technical_analysis.py` and `web/backend/app/api/watchlist.py` were already modified before this node's report write.

## Source Edit Statement

No business source files were edited in this node. This node only produced this report under `docs/reports/worklogs/claude-auto/`.

## Scan Scope

Runtime/source scan roots:

- `src/`
- `web/backend/app/`
- `scripts/`

Excluded from the prioritized runtime table:

- `tests/`
- `web/backend/tests/`
- generated/build/cache directories

Current-source scan summary:

| Metric | Value |
|---|---:|
| Python files scanned in compact runtime pass | 2,159 |
| Runtime candidate files with at least one service lifecycle / DI signal | 267 |
| `module-global` candidates | 145 |
| `provider-getter` candidates | 96 |
| `route-direct-constructor` candidates | 3 |
| `app-lifecycle-state` candidates | 7 |
| `direct-constructor` candidates | 16 |

Signal families used for screening:

- module-level singleton assignments such as `_service = None`, `_manager = None`, `_session = None`, `_engine = None`
- `global` mutation statements around those module-level singletons
- `get_*service`, `get_*manager`, `get_*session`, `get_*db`, `get_*factory`, `get_*registry`, `get_*cache`, `get_*pool`, `get_*monitor`, `get_*tracker`
- direct constructors of known lifecycle-owned objects such as `DataSourceFactory`, `TradingViewWidgetService`, `RealtimeStreamingService`, `CacheManager`, `DatabaseService`, `PostgreSQLDataAccess`, `TDengineManager`
- FastAPI startup/lifespan/app-state observations

## Prior Baseline Used

Most recent local residual closeout found:

- `docs/reports/quality/backend-watchlist-datasourcefactory-provider-closeout-residual-refresh-2026-06-03.md`

Relevant baseline claims from that report:

- Watchlist handler-body direct `DataSourceFactory()` calls: `0`
- Provider backing `DataSourceFactory()` / `get_data_source("watchlist")` calls: `1/1`
- Remaining observations outside the watchlist route:
  - `web/backend/app/api/strategy_management/_strategy_execution_router.py`: `DataSourceFactory()` x3, `get_data_source` x3
  - `web/backend/app/api/technical_analysis.py`: `DataSourceFactory()` x8, `get_data_source` x8
- Next gate named there: no-source `technical_analysis.py` DataSourceFactory ownership review

Current-source screening found a divergence from that baseline for `watchlist.py`:

- Current `web/backend/app/api/watchlist.py` has 8 handler-body `DataSourceFactory()` calls at lines 203, 241, 282, 331, 362, 397, 425, and 459.
- The file is dirty in the current worktree, so this screening does not treat the divergence as a new G2.330 source regression by itself.
- Next authorization must first reconcile whether the G2.322 report was generated from a different source state, whether this is unmerged/user work, or whether the baseline report is stale.

## Priority Screening Matrix

| Rank | Candidate | Evidence | Screening disposition | Next-node recommendation |
|---:|---|---|---|---|
| 1 | `web/backend/app/api/technical_analysis.py` DataSourceFactory provider seam | `get_technical_analysis_data_source()` at lines 27-29 currently constructs `DataSourceFactory()` and calls `get_data_source("technical_analysis")`; file is dirty | Primary ownership candidate, but dirty-source status must be acknowledged | Open a no-source ownership/authorization node before source edits; reconcile prior G2.322 claim of x8/x8 vs current x1/x1 |
| 2 | `web/backend/app/api/strategy_management/_strategy_execution_router.py` route-body DataSourceFactory use | Direct constructor and `get_data_source("strategy")` in `get_strategy_definitions()` lines 206-207, `run_strategy_single()` lines 260-261, `run_strategy_batch()` lines 324-325 | Secondary route provider-injection candidate | Open ownership/authorization after technical-analysis track or as a separate strategy route candidate |
| 3 | `web/backend/app/api/watchlist.py` DataSourceFactory current-source divergence | Current dirty file has 8 direct handler-body constructors at lines 203, 241, 282, 331, 362, 397, 425, 459 | Fact-audit candidate, not source-edit candidate yet | First run a no-source fact reconciliation against G2.322 closeout and dirty provenance; do not authorize implementation until resolved |
| 4 | `web/backend/app/core/cache_manager.py` module-global cache lifecycle | `_async_manager` line 448, `_manager` line 449, `global` mutation around lines 436, 443, 456, `get_cache_manager()` line 433, `get_cache_manager_async()` line 450, `CacheManager()` construction at lines 438 and 458 | High-signal module-global lifecycle candidate | Candidate for lifecycle owner/provider design node; likely broader blast radius than route-local DataSourceFactory residuals |
| 5 | `web/backend/app/api/realtime_mtm_init.py` startup/db singleton lifecycle | `_engine` line 25, `_db_session` line 100, `_engine` line 105, `global _db_session, _engine` around lines 30 and 95, `get_database_session()` line 26, startup registration lines 113 and 121-122 | Startup lifecycle candidate | Needs app lifecycle contract review before source authority; likely intersects service startup/shutdown behavior |
| 6 | `web/backend/app/core/tdengine_manager.py` TDengine manager singleton | `_tdengine_manager` lines 548, 551, 561, `global _tdengine_manager` around lines 532 and 558, `get_tdengine_manager()` line 528, `TDengineManager()` construction at line 542 | Core database lifecycle candidate | Defer until route-local residuals are closed unless TDengine lifecycle instability is the explicit priority |
| 7 | `web/backend/app/core/database.py` database service/session getters | `get_postgresql_session()` line 128, `get_mysql_session()` line 143, `get_db_service()` line 351, `_db_service` global mutation around line 355, `DatabaseService()` line 357, `PostgreSQLDataAccess()` line 175 | Core DB provider-getter candidate | Requires broad impact assessment and probably OpenSpec-backed lifecycle ownership before source authority |
| 8 | `web/backend/app/services/realtime_streaming_service.py` streaming service singleton | `_streaming_service` line 435, `global _streaming_service` around lines 426 and 434, `get_streaming_service()` line 422, `RealtimeStreamingService()` line 428 | Realtime service singleton candidate | Candidate only after checking prior realtime/socket G2 closeouts to avoid reopening closed work |
| 9 | `web/backend/app/services/tradingview_widget_service.py` TradingView service singleton | `_tradingview_service` line 319, `global _tradingview_service` line 324, `get_tradingview_service()` line 320, `get_tradingview_service_dependency()` line 338, `TradingViewWidgetService()` line 326 | FastAPI dependency wrapper plus singleton candidate | Lower priority than DataSourceFactory route residuals; route dependency already exists but provider storage remains module-global |
| 10 | `web/backend/app/app_factory.py` app-state lifecycle metadata | lifecycle markers at lines 13, 161, 302; `app.state.runtime_truth_source` and related state writes at lines 304-308 | App lifecycle contract observation | Do not treat as DI debt without design review; may be intentional app bootstrap contract |
| 11 | `src/application/services/performance_optimizer.py` global optimizer/cache utilities | `_global_cache`, `_global_batch_processor`, `_global_performance_monitor` global mutations around lines 277, 285, 293; `get_cache()` line 273, `get_performance_monitor()` line 289 | Non-route module-global candidate | Defer unless application-service runtime lifecycle becomes the chosen G2 track |
| 12 | `src/core/cache/multi_level.py` global cache | `_global_cache` line 421, global mutations around lines 404 and 418, `get_cache()` line 400 | Core cache candidate | Defer; likely needs cache lifecycle design instead of isolated getter rewrite |
| 13 | `src/core/database_metrics.py` global metrics collectors/loggers | global collector/logger mutations around lines 332 and 339, `get_pool_metrics()` line 219, lifecycle-related markers at lines 9 and 361 | Metrics lifecycle candidate | Defer; likely observability lifecycle track, not immediate DI provider track |

## Recommended Candidate Ordering

1. `technical_analysis.py` DataSourceFactory ownership review
   - Reason: explicitly named by prior closeout as the next gate, route-local, visible direct constructor/provider seam, lower conceptual blast radius than core cache/database singletons.
   - Required precondition: no-source ownership/authorization node; current dirty-source status must be reported.

2. `strategy_management/_strategy_execution_router.py` DataSourceFactory route provider review
   - Reason: same residual family as technical-analysis, three direct route-body constructions, no dirty status observed for this file.
   - Required precondition: separate no-source ownership/authorization or included in an approved DataSourceFactory route-residual batch.

3. `watchlist.py` baseline divergence fact audit
   - Reason: current source contradicts the G2.322 closeout. This is not safe to classify as closed or actionable until provenance is resolved.
   - Required precondition: no-source fact reconciliation; do not edit until the dirty file's ownership and expected source truth are known.

4. Core lifecycle owner design track: `cache_manager.py`, `database.py`, `tdengine_manager.py`
   - Reason: high-signal module-global lifecycle state, but broad blast radius and likely cross-cutting lifecycle semantics.
   - Required precondition: OpenSpec/design or explicit architecture authorization before any source edits.

5. Realtime/TradingView service singleton follow-up
   - Reason: still has module-global singletons, but prior G2 realtime/socket work likely exists and must be checked before reopening.
   - Required precondition: no-source closeout-history review first.

## Non-Candidate / Deferred Classes

- Tests and test fixtures: excluded from runtime prioritization.
- Scripts: scanned but deferred as non-runtime unless a later node explicitly targets operational scripts.
- `app.state` bootstrap writes: treated as lifecycle contract observations, not automatic debt.
- Existing FastAPI dependency wrappers: not automatically candidates when they already provide an injection interface; only the backing module-global storage remains a possible later lifecycle concern.

## Required Next Gate

G2.330 does not authorize implementation.

Before any source edit, the next node must declare:

- exact target file(s)
- ownership classification
- whether dirty-source state is in scope
- `source_edit_authority=true`
- GitNexus impact analysis for edited symbols/routes
- expected verification commands
- rollback rule

Suggested next node:

`G2.331 technical_analysis DataSourceFactory ownership / authorization`

Alternative if provenance risk is considered blocking:

`G2.331 watchlist DataSourceFactory closeout divergence fact audit`

## Verification Performed

- Read governance baseline from `architecture/STANDARDS.md`.
- Queried context-mode memory for prior G2.330/G2 service lifecycle decisions; no direct G2.330 memory found.
- Queried GitNexus for service lifecycle / dependency injection / singleton execution-flow hints; index reported stale status and was recorded as non-authoritative.
- Read prior closeout report `docs/reports/quality/backend-watchlist-datasourcefactory-provider-closeout-residual-refresh-2026-06-03.md`.
- Ran no-source current-source scans for service lifecycle / DI residual signal families.
- Checked dirty status of prioritized files; only `web/backend/app/api/technical_analysis.py` and `web/backend/app/api/watchlist.py` were dirty among the highlighted target set.

## Closeout

G2.330 candidate screening is complete as a no-source governance/reporting node. No source implementation authority is implied by this report.
