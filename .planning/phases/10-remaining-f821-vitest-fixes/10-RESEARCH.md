# Phase 10: Remaining F821 + Vitest Fixes — Research

**Phase:** 10
**Date:** 2026-04-10
**Status:** Research Complete

---

## Summary

Two domains: Python F821 (11 errors, 6 files) and Vitest (7 test failures). F821 fixes are mostly mechanical import additions. Vitest fixes require test path updates (Charts→charts) and semantic test rewrites for wrapper components. **Two symbols (`DatabaseType`, `DatabaseService`) not found in current src/ — requires investigation.**

---

## F821 Error Inventory

All 11 errors confirmed via `ruff check src/ --select F821`:

| # | File | Line | Symbol | Category |
|---|------|------|--------|----------|
| 1 | `src/alternative_data/_news_sentiment_service_helper.py` | 13 | `NewsArticle` | Type annotation |
| 2 | `src/alternative_data/_news_sentiment_service_helper.py` | 48 | `NewsArticle` | Type annotation |
| 3 | `src/alternative_data/news_sentiment_analyzer.py` | 404 | `torch` | Runtime usage |
| 4 | `src/alternative_data/news_sentiment_analyzer.py` | 406 | `torch` | Runtime usage |
| 5 | `src/core/data_source/config_manager.py` | 94 | `yaml` | Runtime usage |
| 6 | `src/database/service/adapter_queries.py` | 384 | `DatabaseService` | Module-level singleton |
| 7 | `src/governance/risk_management/services/alert_rule_engine.py` | 515 | `threshold` | f-string bug |
| 8 | `src/governance/risk_management/services/alert_rule_engine.py` | 529 | `threshold` | f-string bug |
| 9 | `src/storage/database/database_manager/database_table_manager_methods/close_all_connections.py` | 58 | `DatabaseType` | Enum reference |
| 10 | `src/storage/database/database_manager/database_table_manager_methods/close_all_connections.py` | 62 | `DatabaseType` | Enum reference |
| 11 | `src/storage/database/database_manager/database_table_manager_methods/close_all_connections.py` | 66 | `DatabaseType` | Enum reference |

---

## F821 Canonical Import Sources

### NewsArticle (errors 1-2)
- **Canonical location:** `src/alternative_data/news_sentiment_analyzer.py:35` — `@dataclass class NewsArticle`
- **Fix:** Add `from src.alternative_data.news_sentiment_analyzer import NewsArticle` in `_news_sentiment_service_helper.py`
- **Note:** File uses `from __future__ import annotations`, so string quotes around `NewsArticle` are fine for runtime

### torch (errors 3-4)
- **Used at:** `news_sentiment_analyzer.py:404` (`torch.no_grad()`) and `:406` (`torch.softmax()`)
- **Pattern:** File already has conditional import for transformers (`TRANSFORMERS_AVAILABLE` flag). Add similar `TORCH_AVAILABLE` pattern.
- **Reference:** `src/advanced_analysis/anomaly/dataclasses.py` — canonical `GPU_AVAILABLE`/`TORCH_AVAILABLE` pattern from Phase 09
- **Fix:** Add `try: import torch; TORCH_AVAILABLE = True except ImportError: TORCH_AVAILABLE = False` after transformers block

### yaml (error 5)
- **Used at:** `config_manager.py:94` — `yaml.safe_load(f)`
- **Fix:** Add `import yaml` to imports (standard third-party, not optional)
- **Current imports:** `logging, threading, datetime, pathlib, typing, config.data_sources_loader, src.core.data_source._config_manager_persistence_mixin`

### DatabaseService (error 6) — ⚠️ NEEDS INVESTIGATION
- **Used at:** `adapter_queries.py:384` — `db_service = DatabaseService()` (module-level global)
- **Problem:** `class DatabaseService` not found anywhere in `src/` via grep. GitNexus shows:
  - `web/backend/app/core/database.py` — backend DatabaseService (different module)
  - `src/database/database_service_new.py` — candidate but may be `_new`/shim file
- **Recommendation:** Read `src/database/database_service_new.py` to confirm it has the class. If yes, import from there. If the entire `adapter_queries.py:384` line is dead code, consider whether it should be removed instead.

### DatabaseType (errors 9-11) — ⚠️ NEEDS INVESTIGATION
- **Used at:** `close_all_connections.py:58,62,66` — `DatabaseType.TDENGINE`, `DatabaseType.POSTGRESQL`
- **Problem:** `DatabaseType` class/enum NOT found anywhere in `src/` via grep. Only found in `archive/legacy-dot-archive/`.
- **The file** imports `redis` and `dotenv` but no database type enum.
- **Possibilities:**
  1. `DatabaseType` was moved/renamed and the import was lost
  2. The methods (`get_tdengine_connection`, etc.) are dead code
  3. `DatabaseType` needs to be re-introduced from its canonical location
- **Recommendation:** Check if these 3 methods are called anywhere. If dead code, add `# noqa: F821` with TODO comment. If live, trace the enum's canonical location.

### threshold f-string (errors 7-8) — BUG FIX
- **File:** `alert_rule_engine.py:515,529`
- **Bug:** `f"VaR超过 {threshold}%"` — `threshold` is not a variable in scope
- **Evidence:** Adjacent line `"value": "{threshold}"` shows it's a template placeholder, not runtime variable
- **Fix:** Remove `f` prefix → `"VaR超过 {threshold}%"` and `"波动率超过 {threshold}%"`

---

## Vitest Failure Analysis

### Chart Tests (3 failures)

**Root cause:** Tests reference `src/components/Charts/` (uppercase C) but only `src/components/charts/` (lowercase) exists.

**Verified directory state:**
- `src/components/charts/` — EXISTS (lowercase): AdvancedHeatmap.vue, IndicatorSelector.vue, OscillatorChart.vue, ProKLineChart.vue, RelationChart.vue, SankeyChart.vue, TreeChart.vue
- `src/components/charts/styles/` — EXISTS: AdvancedHeatmap.scss, ProKLineChart.css, RelationChart.scss
- `src/components/Charts/` — DOES NOT EXIST (uppercase)

**Failed test files (3 of 4, 4th passes because it doesn't reference Charts/ directly):**
1. `chart-component-style-normalization.spec.ts` — ENOENT for Charts/styles/*.scss
2. `chart-style-sources.spec.ts` — ENOENT for `Charts/styles/AdvancedHeatmap.scss`
3. `indicator-selector-types-cleanup.spec.ts` — ENOENT for `Charts/IndicatorSelector.vue`

**Fix:** Update path references in test files from `Charts/` → `charts/` (lowercase)

### System Tab Tests (2 failures + 1 unhandled error)

**ArtDecoSystemSettings.spec.ts:**
- **Error:** `TypeError: monitoringApi.getSystemGeneralSettings is not a function` (unhandled rejection)
- **Cause:** Test mocks `getDetailedSystemHealth` and `getSystemHealth` but NOT `getSystemGeneralSettings`
- **Settings.vue:180** calls `monitoringApi.getSystemGeneralSettings()` via `exec.silent`
- **Test assertions** expect text like "统一系统配置后端契约仍未建立" and "保存本地设置" — these match the wrapper's delegated Settings.vue component
- **Fix:** Add `getSystemGeneralSettings: vi.fn().mockResolvedValue(...)` to the `@/api` mock

**ArtDecoDataManagement.spec.ts:**
- **Error:** Test calls `vm.toggleConfig(0)` and `vm.saveConfig()` — methods that don't exist on DataSource.vue (the canonical component)
- **ArtDecoDataManagement.vue** is a thin wrapper re-exporting `@/views/system/DataSource.vue`
- **DataSource.vue** likely doesn't expose `toggleConfig`/`saveConfig`
- **Fix:** Rewrite test to match DataSource.vue's actual API. The stale `ArtDecoDataManagementVm` interface must be deleted/replaced.

---

## Risk Assessment

| Item | Risk | Mitigation |
|------|------|-----------|
| DatabaseService import location | Medium — may be dead code or in `_new` file | Read `database_service_new.py` first |
| DatabaseType missing from src/ | High — enum completely absent | Check if methods are dead code before adding import |
| ArtDecoDataManagement test rewrite | Medium — need to understand DataSource.vue API | Read DataSource.vue before rewriting |
| Chart path fix | Low — straightforward find/replace | Verify all path references updated |

---

## Validation Architecture

Not applicable for this phase — mechanical fixes and test realignment, no new features.

---

## RESEARCH COMPLETE

**Key deliverable for planner:** Two symbols need pre-plan investigation (DatabaseService, DatabaseType). All other fixes are fully specified with canonical import sources and exact line numbers.
