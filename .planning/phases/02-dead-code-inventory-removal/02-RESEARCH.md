# Phase 2: Dead Code Inventory & Removal — Research

**Researched:** 2026-04-06
**Status:** Complete
**Question:** What do I need to know to PLAN this phase well?

---

## Executive Summary

Phase 2 targets 5 dead/duplicate code layers for inventory, caller redirection, merge, and deletion. Research confirms all 5 targets have minimal external callers — most are self-referential or test-only. The deletion risk is LOW-to-MEDIUM. The main planning concern is correct merge handling for `src/database_optimization/` (whose utilities are NOT duplicated in canonical `src/data_access/optimizers/`).

---

## Target 1: `src/routes/` (19 files across 6 sub-directories)

### File Inventory

| File | Purpose |
|------|---------|
| `_strategy_health_router.py` | Strategy health check router |
| `dashboard_routes.py` | Dashboard route definitions |
| `monitoring_routes.py` | Top-level monitoring router |
| `monitoring_routes/__init__.py` | Package init |
| `monitoring_routes/_monitoring_control_tail.py` | Monitoring control tail endpoint |
| `monitoring_routes/check_monitoring_health.py` | Monitoring health check |
| `monitoring_routes/check_use_mock_data.py` | Mock data toggle |
| `stocks_routes.py` | Top-level stocks router |
| `stocks_routes/__init__.py` | Package init |
| `stocks_routes/_watchlist_router.py` | Watchlist CRUD endpoints |
| `stocks_routes/check_stocks_health.py` | Stocks health check |
| `stocks_routes/check_use_mock_data.py` | Mock data toggle |
| `stocks_routes/stocks_data_sources.py` | Stock data source functions |
| `strategy_routes.py` | Strategy route definitions |
| `technical_routes.py` | Top-level technical router |
| `technical_routes/__init__.py` | Package init |
| `technical_routes/check_use_mock_data.py` | Mock data toggle |
| `technical_routes/get_support_resistance_levels.py` | Support/resistance endpoint |
| `wencai_routes.py` | Wencai query routes |

### Caller Analysis

**Production callers:**
1. `src/database/services/database_service.py:155` — `from src.routes.wencai_routes import execute_custom_query, get_query_results`

**Internal (self-imports within src/routes/):**
- `monitoring_routes/check_use_mock_data.py:14` — imports from `monitoring_routes._monitoring_control_tail`
- `stocks_routes/check_use_mock_data.py:14-15` — imports from `stocks_routes._watchlist_router` and `stocks_routes.stocks_data_sources`
- `_strategy_health_router.py:17` — imports from `strategy_routes`

**Dev scripts:**
- `scripts/dev/quality_gate/fix_test_imports.py:41` — `'from routes.': 'from src.routes.'` (import fixer rule, not a real caller)

**CI/CD:**
- `scripts/cicd_pipeline.sh:184` — `from src.routes import *` (legacy smoke test)

### Assessment

- **Status:** Dead code — mock-era routes from before `web/backend/` consolidation
- **Risk:** LOW — only 1 production caller, 1 CI script reference
- **Redirection:** `database_service.py:155` needs redirect to `web/backend/app/api/` equivalent
- **CI fix:** Update `cicd_pipeline.sh` to remove or redirect the `from src.routes import *` check

---

## Target 2: `src/api/` (5 files)

### File Inventory

| File | Purpose |
|------|---------|
| `alert_history_routes.py` | Alert history route definitions |
| `datasource/__init__.py` | Package init |
| `datasource/routes.py` | Data source routes |
| `governance/__init__.py` | Package init |
| `governance/routes.py` | Governance routes |

### Caller Analysis

**Production callers:** NONE

**Test callers:**
- `tests/api_contract_tests.py:21-23` — imports `APIResponse`, `MarketOverview`, `MarketOverviewData`, `BacktestRequest`, `BacktestResponse`, `StrategyInfo` from `src.api.types.*`

**Dev scripts:**
- `scripts/dev/quality_gate/fix_test_imports.py:42` — `'from api.': 'from src.api.'` (import fixer rule)

### Assessment

- **Status:** Dead code — alternative route layer never adopted in production
- **Risk:** LOW — zero production callers
- **Redirection:** `tests/api_contract_tests.py` imports types from `src.api.types.*` — need to verify these types exist elsewhere or tests should be updated
- **Note:** `src/api/types/` directory was NOT found in file listing — may already be deleted or may be a sub-directory. Plan must verify before deleting `src/api/`

---

## Target 3: `src/data_access_pkg/` (5 files)

### File Inventory

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `IDataAccessLayer`, `TDengineDataAccess`, `PostgreSQLDataAccess` |
| `interface.py` | `IDataAccessLayer` interface definition |
| `postgresql_access.py` | PostgreSQL data access implementation |
| `tdengine_access.py` | TDengine data access implementation |
| `_postgresql_access_query_mixin.py` | PostgreSQL query mixin |

### Caller Analysis

**Production callers:** NONE (self-imports only — `_postgresql_access_query_mixin.py` imported by `postgresql_access.py`)

**External callers:** NONE

### Overlap with Canonical `src/data_access/`

| data_access_pkg file | data_access equivalent | Notes |
|---------------------|----------------------|-------|
| `interface.py` | `interfaces.py` (8428 bytes) | Canonical has more content |
| `postgresql_access.py` (17840 bytes) | `postgresql_access.py` (17519 bytes) | Very similar size, canonical wins |
| `tdengine_access.py` (23514 bytes) | `tdengine_access.py` (2770 bytes) | **SIZES DIFFER** — canonical is much smaller (may be a slim wrapper) |
| `_postgresql_access_query_mixin.py` (8800 bytes) | No direct equivalent | Unique file — check if functionality moved to canonical |

### Assessment

- **Status:** Duplicate layer — all exports overlap with canonical `src/data_access/`
- **Risk:** LOW — zero external callers
- **Merge approach:** Per D-05/D-06, canonical wins. Only copy files that don't exist in canonical. Check `tdengine_access.py` size discrepancy — canonical version may be incomplete
- **CRITICAL:** Compare `tdengine_access.py` content before deciding merge strategy — 23514 bytes vs 2770 bytes is a 9x difference

---

## Target 4: `src/db_manager/` (1 file)

### File Inventory

| File | Purpose |
|------|---------|
| `__init__.py` | Re-exports from `src.storage.database` |

### Content

`__init__.py` is a compatibility shim that re-exports:
- `connection_manager`, `database_manager`, `db_utils` from `src.storage.database`
- `DatabaseConnectionManager`, `DatabaseTableManager`, `DatabaseType` from sub-modules

### Caller Analysis

**Production callers:** NONE

**Dev scripts:**
- `scripts/dev/project/update_imports.py:16,27` — maps `from db_manager` → `from src.db_manager`
- `scripts/dev/fix_test_imports.py:8,28-29` — maps old `from db_manager` patterns
- `scripts/dev/quality_gate/fix_test_imports.py:8,32` — maps old `from db_manager` patterns

### Assessment

- **Status:** Empty compatibility shell — all re-exports point to `src.storage.database`
- **Risk:** LOW — zero production callers, scripts only have import-mapping rules (not actual imports)
- **Deletion:** Safe to delete. Update script import mappings to point directly to `src.storage.database`

---

## Target 5: `src/database_optimization/` (5 files)

### File Inventory

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `IndexPerformanceMonitor`, `PostgreSQLIndexOptimizer`, `SlowQueryAnalyzer`, `TDengineIndexOptimizer` |
| `performance_monitor.py` (11262 bytes) | Index performance monitoring |
| `postgresql_index_optimizer.py` (15264 bytes) | PostgreSQL index optimization |
| `slow_query_analyzer.py` (13040 bytes) | Slow query analysis |
| `tdengine_index_optimizer.py` (8546 bytes) | TDengine index optimization |

### Caller Analysis

**Production callers:** NONE

**Test callers:**
- `tests/unit/database_optimization/test_performance_monitor.py:19` — `from src.database_optimization.performance_monitor import IndexPerformanceMonitor`
- `scripts/tests/test_database_optimization.py:18` — `from src.database_optimization import (...)` (dev test script)

### Overlap with Canonical `src/data_access/`

| database_optimization file | data_access equivalent | Notes |
|---------------------------|----------------------|-------|
| `performance_monitor.py` | `optimizers/query_optimizer.py` | **DIFFERENT** — query_optimizer is general optimization, performance_monitor is index-specific monitoring |
| `postgresql_index_optimizer.py` | No equivalent | Unique — PostgreSQL index optimization |
| `slow_query_analyzer.py` | No equivalent | Unique — slow query analysis |
| `tdengine_index_optimizer.py` | No equivalent | Unique — TDengine index optimization |

### Assessment

- **Status:** Legacy optimization utilities — 3 of 4 files have NO equivalent in canonical layer
- **Risk:** MEDIUM — test-only callers, but functionality may still be needed
- **Merge approach:** Move unique files to `src/data_access/optimizers/` as sub-modules:
  - `performance_monitor.py` → `src/data_access/optimizers/performance_monitor.py`
  - `postgresql_index_optimizer.py` → `src/data_access/optimizers/postgresql_index_optimizer.py`
  - `slow_query_analyzer.py` → `src/data_access/optimizers/slow_query_analyzer.py`
  - `tdengine_index_optimizer.py` → `src/data_access/optimizers/tdengine_index_optimizer.py`
- **After merge:** Update test imports to `from src.data_access.optimizers.performance_monitor import ...`

---

## Cross-Cutting Research Findings

### R1: `tdengine_access.py` Size Discrepancy

`src/data_access_pkg/tdengine_access.py` is **23,514 bytes** while canonical `src/data_access/tdengine_access.py` is only **2,770 bytes**. This is a 9x difference that suggests:
- The canonical version may be a slim wrapper or was intentionally simplified
- OR the canonical version lost content during a prior refactoring

**Plan must include:** Content comparison before merge decision. If canonical is incomplete, the plan must handle this.

### R2: No Dynamic Import Risks

No `importlib`, `__import__`, or `import_module` usage was found in any of the deletion target directories. The risk of hidden dynamic imports is minimal.

### R3: CI/CD References

Only one CI/CD reference found:
- `scripts/cicd_pipeline.sh:184` — `from src.routes import *` (legacy smoke test)

### R4: Test File Impact

Affected test files:
1. `tests/api_contract_tests.py` — imports types from `src.api.types.*` (verify types still exist elsewhere)
2. `tests/unit/database_optimization/test_performance_monitor.py` — import redirect needed after merge
3. `scripts/tests/test_database_optimization.py` — import redirect needed after merge

### R5: Dev Script Impact

These scripts contain import-mapping rules that reference dead targets (not actual imports):
1. `scripts/dev/quality_gate/fix_test_imports.py` — mapping rules for `src.routes`, `src.api`, `src.db_manager`, `src.database_optimization`
2. `scripts/dev/project/update_imports.py` — mapping rules for `src.db_manager`
3. `scripts/dev/fix_test_imports.py` — mapping rules for `src.db_manager`

These mapping rules should be cleaned up after deletion but are NOT blocking.

---

## Validation Architecture

This section addresses Dimension 8 (Validation Requirements) for plan verification.

### Validation Points

| Sub-stage | Validation | Command |
|-----------|-----------|---------|
| 2a (Inventory) | DELETION-CANDIDATES.md exists with all 5 targets | `test -f DELETION-CANDIDATES.md && grep -c "Keep/delete" DELETION-CANDIDATES.md` |
| 2b (Redirection) | Zero broken imports after redirect | `ruff check src/ web/backend/app/ --select F821` |
| 2c (Merge) | All merged files importable | `python -c "from src.data_access.optimizers.performance_monitor import IndexPerformanceMonitor"` |
| 2d (Deletion) | Target dirs gone | `test ! -d src/routes && test ! -d src/api` |
| All | FastAPI smoke test | `cd web/backend && PYTHONPATH=$(git rev-parse --show-toplevel):. python -c "from app.main import app; print('OK')"` |
| All | Test suite | `pytest --tb=short` |
| All | Lint regression check | `ruff check src/ web/backend/app/ \| wc -l` (must stay <900) |

---

## Planning Recommendations

1. **Sub-stage ordering matters:** 2a (analysis) → 2b (redirection) → 2c (merge) → 2d (deletion) must be strictly sequential
2. **Checkpoint after 2a:** User MUST review and approve DELETION-CANDIDATES.md before any code changes
3. **tdengine_access.py investigation:** Plan must include content comparison as a gate before merge
4. **database_optimization merge is NOT simple copy:** 3 of 4 files are unique and must be added as new sub-modules to `src/data_access/optimizers/`
5. **Batch verification:** Run `ruff check` + `pytest` after each sub-stage, not just at the end
6. **Dev scripts are low-priority:** Import mapping rules in dev scripts can be cleaned up but don't block deletion

---

*Phase: 02-dead-code-inventory-removal*
*Research completed: 2026-04-06*
