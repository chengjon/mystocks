# Phase 4: Naming & Polish - Research

**Researched:** 2026-04-08
**Status:** Complete

## Research Summary

Phase 4 has three distinct sub-stages with clear boundaries. Root-level shims have zero active callers and are straightforward Remove candidates. The 32 part{1,2,3}.py files follow a consistent mixin-based pattern with class names that directly provide semantic rename targets. The two _new.py files are lightweight facades, not full rewrites. Store pairs have genuinely different domains — documentation-only work needed.

## 4a: Root Shim Caller Inventory

### Root-level shims (repo root)

| Shim | Active Callers | Recommended Disposition |
|------|---------------|----------------------|
| `core.py` (root) | **0** — no imports found in active code | **Remove** |
| `data_access.py` (root) | **0** — no imports found in active code | **Remove** |
| `monitoring.py` (root) | **0** — no imports found in active code | **Remove** |

Evidence: grep for `from core import`, `import core`, `from data_access import`, `import data_access`, `from monitoring import`, `import monitoring` across all `.py` files excluding worktrees/archive — zero matches in active codebase. Only references are in `scripts/dev/project/update_imports.py` (the migration utility itself, which maps old→new patterns).

### src/ internal re-exports

| Shim | Active Callers | Recommended Disposition |
|------|---------------|----------------------|
| `src/core.py` | **20+** — used by src/ modules, scripts/, tests/ | **Deprecate** (add warning) |
| `src/data_access.py` | **20+** — used by src/database/, src/data_sources/, tests/ | **Deprecate** (add warning) |

Callers of `src/core.py` include: `src/monitoring/`, `src/data_sources/`, `src/storage/`, `src/data_access/`, `src/advanced_analysis/`, `scripts/runtime/`, `scripts/check_system_health.py`, `scripts/dev/`, `tests/`.

Callers of `src/data_access.py` include: `src/database/` (6 files), `src/data_sources/` (3 files), `src/infrastructure/`, `src/core/`, `scripts/tests/`, `tests/`.

Note: `src/core.py` itself contains `from core import *` (referencing the ROOT shim) — creating a chain: root `core.py` → `src/core.py` → `src/core/`. If root shim is removed, `src/core.py` must be updated to import directly from `src/core/`.

## 4b: Naming Cleanup Research

### src/calcu/ → assessment

`src/calcu/` is effectively **empty** — contains only:
- `readme.md` (description: directory for algorithm documentation)
- `block/板块表现算法.md` (Chinese markdown about sector analysis algorithms)

**No Python files, no importers anywhere in the codebase.**

Recommendation: Delete the entire directory. No rename needed — nothing to rename to. Mark NAME-01 as "resolved — directory is documentation-only, no code."

### part{1,2,3}.py Semantic Names

All 32 part files follow a consistent pattern: each exports a named mixin class, imported by `__init__.py` to compose the parent class. The mixin class name directly provides the semantic filename.

| Module | part1 → rename | part2 → rename | part3 → rename |
|--------|----------------|----------------|----------------|
| `efinance_data_source_methods/` | `core.py` | `get_bond_basic.py` | `bond_quote.py` |
| `deduplication_strategy_methods/` | `core.py` | `validate_single_table.py` | `validation.py` |
| `postgre_sql_relational_data_source_methods/` | `core.py` | `get_stock_basic.py` | `preferences.py` |
| `t_dengine_time_series_data_source_methods/` | `core.py` | `check_data_quality.py` | (only 2 parts) |
| `gpu_risk_calculator_methods/` | `core.py` | `get_concentration_level.py` | `portfolio_events.py` |
| `stop_loss_engine_methods/` | `core.py` | `calculate_trigger_confidence.py` | `risk_assessment.py` |
| `feature_calculation_gpu_methods/` | `core.py` | `calculate_price_volume.py` | `post_volume.py` |
| `optimization_gpu_methods/` | `core.py` | `risk_parity_optimization.py` | `portfolio.py` |
| `resource_scheduler_methods/` | `core.py` | `calculate_queue_efficiency.py` | `performance.py` |
| `monitoring_database_methods/` | `core.py` | `cleanup_old_records.py` | `history.py` |
| `database_table_manager_methods/` | `core.py` | `close_all_connections.py` | `ddl_info.py` |

Naming convention derived from mixin classes:
- `part1.py` always → `core.py` (always contains `{ClassName}CoreMixin`)
- `part2.py` → derived from `{ClassName}{Suffix}Mixin` → `snake_case(suffix)`
- `part3.py` → derived from `{ClassName}{Suffix}Mixin` → `snake_case(suffix)`

**Per-file rename plan:**
1. Rename `part1.py` → `core.py` (must be done first — `__init__.py` imports from it)
2. Rename `part2.py` → semantic name
3. Rename `part3.py` → semantic name (if exists)
4. Update `__init__.py` imports: `from .partN import ...` → `from .{semantic_name} import ...`
5. `git rm` old files + `git add` new files (WSL2 case-sensitivity: use two-step `git mv` per Phase 3 pattern)

### *_new.py Files

1. **`src/database/database_service_new.py`** (78 lines)
   - A clean facade class that delegates to ConnectionService, QueryService, TransactionService, MigrationService
   - Canonical target: `src/database/database_service.py`
   - Status: Verify canonical file exists and compare; if `_new` is complete, replace canonical

2. **`src/advanced_analysis/decision_models/decision_models_analyzer_new.py`** (154 lines)
   - A backward-compatible wrapper that re-exports from `base/analysis_result`, `models/model_synthesis`, `main/analyzer_core`
   - Canonical target: `src/advanced_analysis/decision_models_analyzer.py` (parent directory)
   - WARNING: `_new` file is inside `decision_models/` subpackage, canonical is in parent `advanced_analysis/`
   - Requires: verify canonical file, then `git mv` the _new file UP one directory to replace canonical

### Stale Backups

- **`baseStore.ts.bak`** (3085 bytes, dated 2025-02-03): Zero imports found. The active `baseStore.ts` (2818 bytes, dated 2025-03-22) is used by `market.ts` and `storeFactory.ts`. Safe to delete.

### Other cleanup candidates

- No `*.bak` or `*.backup` Python files found in `src/`
- No `_old.py` files found

## 4c: Store Domain Boundaries

### All Pinia Stores (20 files)

| Store File | Pattern | Size | Domain |
|------------|---------|------|--------|
| `apiStores.ts` | defineStore | 2.8KB | Generic API store factory |
| `auth.ts` | defineStore | 6.0KB | Authentication & user sessions |
| `baseStore.ts` | createBaseStore | 3.1KB | Template for standardized stores |
| `dataAdapters.ts` | defineStore | 6.1KB | Data adapter state management |
| `loading.ts` | defineStore | 937B | Global loading state |
| `market.ts` | createBaseStore | 2.3KB | **Market overview & analysis** (simple API wrapper) |
| `marketData.ts` | defineStore | 14.8KB | **Market data with IndexedDB caching** (enhanced) |
| `menuStore.ts` | defineStore | 1.7KB | Navigation menu state |
| `preferenceStore.ts` | defineStore | 3.0KB | User preferences |
| `risk.ts` | defineStore | 1.6KB | Risk metrics |
| `storeFactory.ts` | PiniaStoreFactory | 12.2KB | Factory for creating standardized stores |
| `strategy.ts` | defineStore | 2.1KB | Trading strategy management |
| `system.ts` | defineStore | 2.8KB | System health & configuration |
| `trading.ts` | defineStore | 5.5KB | **Trade orders & system status** |
| `tradingData.ts` | defineStore | 2.3KB | **Trading signals, history, positions** (analytical) |
| `ui.ts` | defineStore | 4.0KB | UI state (theme, layout) |
| `__tests__/` | — | — | Store tests |
| `examples/` | — | — | Usage examples |

### Overlapping Pair Analysis

**market.ts vs marketData.ts:**
- `market.ts`: Uses `createBaseStore` template pattern. Provides `useMarketStore` with `fetchOverview()` and `fetchAnalysis()`. Thin API wrapper with no caching.
- `marketData.ts`: Uses `defineStore` directly with `reactive`. Provides `useMarketDataStore` with IndexedDB caching, offline support, sync status, and web worker integration for technical indicators.
- **Boundary**: `market.ts` = simple real-time market overview (used by overview widgets); `marketData.ts` = enhanced market data with persistence and computation (used by charts and analysis views). Different consumers, different capabilities. Both valid.

**trading.ts vs tradingData.ts:**
- `trading.ts`: Uses `ref` pattern. Manages system health data, trade orders, and order execution. More of a "trading operations" store.
- `tradingData.ts`: Uses `reactive` pattern. Manages trading signals, history, position monitoring, performance analysis. More of a "trading analytics" store.
- **Boundary**: `trading.ts` = operations (place orders, check status); `tradingData.ts` = analytics (signals, history, performance). Clear separation.

**Verdict:** Neither pair needs merging. Each store serves a distinct purpose. Document boundaries with inline comments.

## Key Findings

1. **Root shims are dead code** — zero active callers. Safe to remove all three. (Per CONTEXT.md D-02: data-driven decision → Remove for all.)
2. **src/ internal re-exports have 20+ callers each** — Deprecate, don't Remove. Adding deprecation warning is the right call.
3. **src/calcu/ is empty** — only contains documentation markdown, no Python code. Should be deleted entirely rather than renamed. NAME-01 scope reduced.
4. **Circular shim chain discovered** — `src/core.py` imports from root `core.py` (`from core import *`). When root shim is removed, `src/core.py` must be updated to import from `src/core/` directly.
5. **Part file renames are mechanical** — every mixin class name maps directly to a snake_case filename. No ambiguity in naming.
6. **32 part files across 11 modules** — all follow identical pattern. Can be batched into parallel execution.
7. **decision_models_analyzer_new.py** requires a directory-level move (from subpackage to parent), not a simple rename.
8. **baseStore.ts.bak** has zero consumers — safe to delete.
9. **Store pairs are genuinely distinct** — no merging needed, only documentation.

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Circular shim chain: root `core.py` → `src/core.py` → `src/core/` | Medium | Remove root shims FIRST, then update `src/core.py` imports in same wave |
| 32 part file renames could break many imports | Low | Only `__init__.py` imports from part files (internal to each `_methods/` package). External consumers import from the parent class. Zero external breakage. |
| WSL2 case-sensitivity on `git mv` | Medium | Use two-step git mv pattern from Phase 3 (temp name → final name) |
| decision_models_analyzer_new.py directory move | Low | Verify canonical file structure before moving; test import chain |
| Store consumers may depend on specific store | Low | Documentation-only changes — no store code modified |

## Validation Architecture

### After 4a (Root Shims)
- `grep -rn "from core import\|from data_access import\|from monitoring import" src/ scripts/ tests/` → zero root-shim imports
- `python -c "from src.core import DataClassification; print('OK')"` → passes (src/core.py still works via direct src/core/ import)
- Root shims deleted: `ls core.py data_access.py monitoring.py` → not found

### After 4b (Naming)
- `find src/ -name "part*.py"` → zero results
- `find src/ -name "*_new.py"` → zero results
- `find src/ -name "*.bak"` → zero results
- `ls src/calcu/` → not found (deleted)
- `ruff check src/ web/backend/app/` → no new errors introduced
- `cd web/frontend && npm run build` → succeeds
- `cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"` → passes

### After 4c (Stores)
- Each overlapping store pair has domain boundary comment at file top
- `cd web/frontend && npm run build` → still succeeds

---

## RESEARCH COMPLETE
