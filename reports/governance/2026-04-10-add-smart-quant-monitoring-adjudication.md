# Adjudication: add-smart-quant-monitoring

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对 `add-smart-quant-monitoring` 的当前治理判断。
> 共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 是否应继续保留，以及应如何理解其边界。

## Decision

Keep `add-smart-quant-monitoring` active, but treat it as a partially landed monitoring and portfolio-management line rather than a completed 9-10 week delivery package.

## Why It Should Stay

- The change is structurally valid: `openspec validate add-smart-quant-monitoring --strict` passes.
- Current repo evidence shows real implementation across the intended slices already exists:
  - monitoring domain: `src/monitoring/domain/{market_regime,calculator_cpu,calculator_gpu,calculator_factory,portfolio_optimizer,risk_metrics}.py`
  - async/data layer: `src/monitoring/infrastructure/postgresql_async.py`
  - monitoring event surface: `src/monitoring/async_monitoring.py`
  - backend API surface: `web/backend/app/api/{monitoring_watchlists,monitoring_analysis,_monitoring_portfolio_router}.py`
  - migration artifacts: `scripts/migrations/001_monitoring_tables.sql`, `scripts/migrations/migrate_watchlist_to_monitoring.py`
  - frontend views: `web/frontend/src/views/monitoring/WatchlistManagement.vue`, `MonitoringDashboard.vue`, `RiskDashboard.vue`
- Its capability boundary is still meaningful: it governs the smart monitoring / watchlist / health-scoring / portfolio-analysis line rather than a stale historical roadmap.

## Why It Must Not Be Read As Complete

Current repo truth still shows partial execution and placeholder layers:

- `monitoring_watchlists.py` still exposes unfinished surface area; the update path explicitly carries `FEATURE_NOT_IMPLEMENTED` and raises a 501 for the update flow.
- `monitoring_watchlists.py` includes runtime fallback state for development/testing rather than proving the full persistence-backed watchlist flow is complete.
- Existing API and test evidence is present, but much of the visible validation is file-level/API-contract smoke rather than proof that the full worker, async persistence, migration, and frontend round-trip are all production-closed.
- Proposal-level performance and scale claims such as `1000只股票 <2秒` and `50-100x` GPU acceleration are not established as current-truth governance facts merely from source presence.
- The change bundles watchlist CRUD, scoring engines, migration, portfolio optimization, alerting, and frontend visualization into one large package; the repo shows landed slices, not a fully verified end-to-end program.

## Current Repo-Truth Reading

- Treat the monitoring domain and backend API files as evidence that this is an active implementation line, not a stale change.
- Treat watchlist CRUD and health-score computation as partially operational surfaces with some real code paths and some fallback/placeholder behavior.
- Treat migration, worker batching, and performance claims as still needing explicit verification before they can be read as complete.

## Relationship To Current Trunks

- This change should be read as an execution line under the existing monitoring, risk, and portfolio surfaces, not as a competing source of truth.
- Current repo truth lives in the monitoring domain modules, backend monitoring APIs, migration scripts, and corresponding frontend monitoring views.
- Future closure must continue to respect the migration/debt-governance rules in `architecture/STANDARDS.md`, especially around proving runtime truth instead of reading large checklists literally.

## Execution Rule For Future Sessions

- Do not retire this change as stale.
- Do not mark it complete from file existence alone.
- Do not continue the original checklist mechanically.
- If execution resumes, first restate the unresolved current-truth slice:
  - identify which watchlist endpoints are fully persistence-backed versus fallback-only
  - verify whether `metric_update` worker persistence is actively wired and tested end to end
  - prove the migration script against current schema/runtime assumptions
  - convert any remaining GPU/performance statements from proposal claims into measured evidence before using them as governance facts
