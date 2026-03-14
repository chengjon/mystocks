# Architecture/API Remediation Worker Allocation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Verify the issues raised in the architecture and API conflict reports, separate valid findings from stale claims, and dispatch non-overlapping remediation work to idle worker CLIs.

**Architecture:** The work is split into four isolated tracks: API route governance, safe legacy-file cleanup, frontend large-page/API normalization, and data-source config convergence. Deep API domain merges stay out of scope until the in-flight `dev-api-availability-gemini` branch lands.

**Tech Stack:** FastAPI, Vue 3, TypeScript, pytest, Playwright, ripgrep, OpenSpec

---

## Activation Gate

- **Current decision:** keep this plan as a deferred coordination draft.
- **Do not activate worker execution yet.**
- **Trigger to activate:** `dev-api-availability-gemini` is submitted/merged and its final diff is available for re-check.
- **Reason:** the API availability line has already closed its business goal (`verified: 34 / pending: 0`), but the branch still carries environment-layer follow-up and final submission work. Starting parallel remediation before that branch lands would create avoidable overlap and rework.

### What stays deferred for now

- `mystocks_spec1` route-governance execution
- `mystocks_spec2` legacy-file cleanup execution
- `mystocks_spec3` frontend normalization execution
- `mystocks_spec4` data-source config convergence execution

### Re-entry checklist after API branch submission

1. Re-check `dev-api-availability-gemini` final diff against `main`
2. Remove tasks already solved by that branch from this allocation plan
3. Re-scope worker packages to avoid duplicate edits
4. Then activate the remaining worker tasks

---

## Verified Findings

### Still Current

1. **API route registration is split across two active mechanisms**
   - `web/backend/app/main.py` imports `register_api_routes` from `web/backend/app/router_registry.py`
   - `web/backend/app/app_factory.py` imports `register_all_routers` from `web/backend/app/api/register_routers.py`
   - This confirms the report's “two registration paths” concern is real.

2. **API prefixes are inconsistent**
   - Verified examples:
     - `web/backend/app/api/technical/routes.py` uses `prefix="/technical"`
     - `web/backend/app/api/monitoring_analysis.py` uses `prefix="/monitoring/analysis"`
     - `web/backend/app/api/monitoring_watchlists.py` uses `prefix="/monitoring/watchlists"`
     - `web/backend/app/api/multi_source/routes.py` uses `prefix="/multi_source"`
     - `web/backend/app/api/market_v2.py` is routed without a versioned prefix from the registries

3. **Historical backup/broken files are still present in active repo paths**
   - Verified active-tree examples:
     - `web/frontend/src/views/RiskMonitor.vue.broken`
     - `web/frontend/src/views/BacktestAnalysis.vue.broken`
     - `web/frontend/src/router/index.ts.broken`
     - `web/frontend/src/router/index.ts.bak.20260214`
     - `web/backend/app/api/risk_management.py.backup.20260130`
     - `web/backend/app/api/data.py.backup.20260130`
     - `src/database/database_service.py.backup.20260130`
     - `web/backend/app/api/technical_analysis.py.new`

4. **Frontend active pages still contain large files and hardcoded API usage**
   - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue` is 829 lines
   - Multiple active views/components still call hardcoded `/api/*` endpoints directly
   - `useWebSocketWithConfig` exists in repo, but active pages still use manual websocket/fetch patterns

5. **Data-source configuration remains dual-track**
   - Core/backend code still references `config/data_sources_registry.yaml`
   - Web-backend manager/factory code still references `config/data_sources.json`
   - This is a real convergence problem, not just a documentation issue

### Not Safe To Act On Blindly

1. **Delete `src/adapters/legacy_adapter.py`**
   - Not approved for direct cleanup
   - Repo still contains references to legacy adapter paths/inventory
   - Must be treated as compatibility-sensitive until code-path proof is complete

2. **Delete legacy adapter families based only on “looks redundant”**
   - Not assigned
   - Requires capability matrix + runtime/reference proof first

3. **Full API domain merge across market/strategy/risk**
   - Deferred
   - Too likely to collide with the active `dev-api-availability-gemini` branch

## Worker Allocation

### Worker 1: `mystocks_spec1`

**Task:** API route registration and version-prefix governance

**Primary files:**
- `web/backend/app/router_registry.py`
- `web/backend/app/api/register_routers.py`
- `web/backend/app/api/VERSION_MAPPING.py`
- `web/backend/app/api/technical/routes.py`
- `web/backend/app/api/monitoring_analysis.py`
- `web/backend/app/api/monitoring_watchlists.py`
- `web/backend/app/api/multi_source/routes.py`
- `web/backend/app/api/market_v2.py`
- `web/backend/tests/` (new focused route-governance tests)

**Must not touch:**
- `web/backend/app/api/market/**`
- `web/backend/app/api/signal_monitoring/**`
- `web/backend/app/api/strategy_management/get_monitoring_db.py`
- `web/backend/app/api/health.py`

**Acceptance:**
- remove or document dual-registration ambiguity
- normalize or alias inconsistent non-`/api` prefixes in scoped files
- add regression checks proving intended prefixes
- produce concise route-governance report

### Worker 2: `mystocks_spec2`

**Task:** Safe cleanup of active-tree legacy backup/broken files

**Primary files/paths:**
- `web/frontend/src/views/RiskMonitor.vue.broken`
- `web/frontend/src/views/BacktestAnalysis.vue.broken`
- `web/frontend/src/router/index.ts.broken`
- `web/frontend/src/router/index.ts.bak.20260214`
- `web/frontend/src/main.js.old`
- `web/frontend/src/App.vue.old`
- `web/backend/app/api/risk_management.py.backup.20260130`
- `web/backend/app/api/data.py.backup.20260130`
- `web/backend/app/api/technical_analysis.py.new`
- `src/database/database_service.py.backup.20260130`
- `src/advanced_analysis/decision_models_analyzer.py.backup.20260130`
- `src/monitoring/alert_manager.py.backup_complex_20251108`

**Must not touch:**
- `.claude/worktrees/**`
- `.config/**`
- `.omc/**`
- `src/adapters/legacy_adapter.py`
- any file unless code-path and function-tree status both justify cleanup

**Acceptance:**
- classify each target as `有效` / `兼容保留` / `重复冗余` / `待判定`
- remove only proven redundant active-tree backup/broken files
- document retained files with reasons
- add lightweight guardrails if useful

### Worker 3: `mystocks_spec3`

**Task:** Frontend large-page split and hardcoded API/WebSocket normalization

**Primary files:**
- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
- `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue`
- `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- `web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue`
- `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue`
- `web/frontend/src/components/realtime/RealtimePositionPanel.vue`
- `web/frontend/src/config/pageConfig.ts`
- `web/frontend/src/composables/useWebSocketWithConfig.ts`
- related `web/frontend/tests/unit/**`

**Must not touch:**
- `web/frontend/src/views/converted.archive/**`
- unrelated demo/example pages unless required for shared helper extraction

**Acceptance:**
- split at least one active oversized page into smaller helpers/view-model pieces
- replace scoped hardcoded API usage with shared service/config access where reasonable
- normalize scoped websocket usage toward shared composables/utilities
- add focused unit tests for extracted logic

### Worker 4: `mystocks_spec4`

**Task:** Data-source config convergence and guardrails

**Primary files:**
- `config/data_sources_registry.yaml`
- `config/data_sources.json`
- `config/data_sources_loader.py`
- `src/core/data_source/base.py`
- `src/core/data_source/config_manager.py`
- `web/backend/app/core/data_source_manager.py`
- `web/backend/app/services/data_source_factory/data_source_factory.py`
- `web/backend/app/api/data_source_config.py`
- related tests under `tests/` and `web/backend/tests/`

**Must not touch:**
- `web/backend/config/data_sources.json` unless explicitly needed and revalidated
- current API availability worker files under `web/backend/app/api/market/**`

**Acceptance:**
- produce a source-of-truth matrix: which subsystem reads YAML vs JSON and why
- add regression tests to pin current intended entry points
- reduce ambiguity without introducing hidden behavior changes
- record follow-up items if full convergence must be phased

## Deferred Until `dev-api-availability-gemini` Lands

- full market/strategy/risk endpoint consolidation
- removal of compatibility layers whose runtime consumers are still unclear
- contract cleanup for endpoints currently under active availability verification
