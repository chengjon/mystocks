# Deletion Candidates — Phase 2 Review

**Generated:** 2026-04-07
**Status:** PENDING USER APPROVAL
**Phase:** 2 (Dead Code Inventory & Removal)
**Governance:** Per architecture/STANDARDS.md §4 (lines 103-111)

---

## Summary

| Target | Files | Code-Path Judgment | Functional-Tree Status | Recommendation |
|--------|-------|--------------------|-----------------------|---------------|
| src/routes/ | 19 | 1 prod caller (broken circular dep), 1 CI script | 重复冗余 | DELETE after redirect |
| src/api/ | 5 | 1 test caller (already broken ImportError) | 重复冗余 | DELETE |
| src/data_access_pkg/ | 5 | 0 external callers (1 internal only) | 重复冗余 | MERGE → src/data_access/ |
| src/db_manager/ | 1 | 0 callers (shim only, scripts are mapping rules) | 重复冗余 | DELETE |
| src/database_optimization/ | 5 | 2 test callers | 重复冗余 (3 unique utils) | MERGE → src/data_access/optimizers/ |

---

## Evidence Tables

### Table 1: src/routes/ (19 files)

| File | Purpose | Code-Path Status | Functional-Tree Status | Callers (file:line) | Action |
|------|---------|-----------------|----------------------|--------------------|--------|
| `wencai_routes.py` | Wencai query FastAPI router `/api/market/wencai` | 1 prod caller (broken) | 重复冗余 | `src/database/services/database_service.py:155` | DELETE after redirect |
| `dashboard_routes.py` | Dashboard route `/data/markets` | Zero external callers | 重复冗余 | None | DELETE |
| `monitoring_routes.py` | Top-level monitoring router | Zero external callers | 重复冗余 | None | DELETE |
| `monitoring_routes/__init__.py` | Package init with `__all__` | Zero external callers | 重复冗余 | None | DELETE |
| `monitoring_routes/_monitoring_control_tail.py` | Monitoring control tail endpoint | Zero external callers | 重复冗余 | None | DELETE |
| `monitoring_routes/check_monitoring_health.py` | Monitoring health check router `/api/monitoring` | Zero external callers | 重复冗余 | None | DELETE |
| `monitoring_routes/check_use_mock_data.py` | Mock data toggle | Zero external callers | 重复冗余 | None | DELETE |
| `stocks_routes.py` | Top-level stocks router | Zero external callers | 重复冗余 | None | DELETE |
| `stocks_routes/__init__.py` | Package init with `__all__` | Zero external callers | 重复冗余 | None | DELETE |
| `stocks_routes/_watchlist_router.py` | Watchlist CRUD router | Zero external callers | 重复冗余 | None | DELETE |
| `stocks_routes/check_stocks_health.py` | Stocks health check router `/api/stocks` | Zero external callers | 重复冗余 | None | DELETE |
| `stocks_routes/check_use_mock_data.py` | Mock data toggle | Zero external callers | 重复冗余 | None | DELETE |
| `stocks_routes/stocks_data_sources.py` | Stock data source functions | Zero external callers | 重复冗余 | None | DELETE |
| `strategy_routes.py` | Strategy route definitions `/api/strategy` | Zero external callers | 重复冗余 | None | DELETE |
| `_strategy_health_router.py` | Strategy health check router | Zero external callers | 重复冗余 | None | DELETE |
| `technical_routes.py` | Top-level technical router | Zero external callers | 重复冗余 | None | DELETE |
| `technical_routes/__init__.py` | Package init with `__all__` | Zero external callers | 重复冗余 | None | DELETE |
| `technical_routes/check_use_mock_data.py` | Mock data toggle | Zero external callers | 重复冗余 | None | DELETE |
| `technical_routes/get_support_resistance_levels.py` | Support/resistance endpoint `/api/technical` | Zero external callers | 重复冗余 | None | DELETE |

**Sweep A — Static imports (external callers only):**
```
src/database/services/database_service.py:155:            from src.routes.wencai_routes import execute_custom_query, get_query_results
scripts/cicd_pipeline.sh:184:    from src.routes import *
```

**Sweep D — `__all__` exports (namespace patterns):**
```
src/routes/monitoring_routes/__init__.py:17:__all__ = ['check_use_mock_data', ...14 more]
src/routes/technical_routes/__init__.py:17:__all__ = ['check_use_mock_data', ...13 more]
src/routes/stocks_routes/__init__.py:17:__all__ = ['check_use_mock_data', ...12 more]
```

**Sweep F — Compat shim from external modules:**
```
src/database/services/database_service.py:155:            from src.routes.wencai_routes import execute_custom_query, get_query_results
```

---

### Table 2: src/api/ (5 files)

| File | Purpose | Code-Path Status | Functional-Tree Status | Callers (file:line) | Action |
|------|---------|-----------------|----------------------|--------------------|--------|
| `alert_history_routes.py` | Alert history router `/api/alerts` | Zero callers | 重复冗余 | None | DELETE |
| `datasource/__init__.py` | Package init with `__all__` | Zero callers | 重复冗余 | None | DELETE |
| `datasource/routes.py` | Data source router `/api/datasources` | Zero callers | 重复冗余 | None | DELETE |
| `governance/__init__.py` | Package init with `__all__` | Zero callers | 重复冗余 | None | DELETE |
| `governance/routes.py` | Governance router `/api/governance` | Zero callers | 重复冗余 | None | DELETE |

**Sweep A — Static imports (external callers only):**
```
tests/api_contract_tests.py:21:from src.api.types.common import APIResponse
tests/api_contract_tests.py:22:from src.api.types.market import MarketOverview, MarketOverviewData
tests/api_contract_tests.py:23:from src.api.types.strategy import BacktestRequest, BacktestResponse, StrategyInfo
```

**Note:** `src/api/types/` directory DOES NOT EXIST — these imports are already broken (ImportError at runtime).

---

### Table 3: src/data_access_pkg/ (5 files)

| File | Purpose | Code-Path Status | Functional-Tree Status | Callers (file:line) | Action |
|------|---------|-----------------|----------------------|--------------------|--------|
| `__init__.py` | Re-exports `IDataAccessLayer`, `TDengineDataAccess`, `PostgreSQLDataAccess` | Zero external callers | 重复冗余 | None | DELETE |
| `interface.py` | `IDataAccessLayer` interface definition | Zero external callers | 重复冗余 | `src/data_access/interfaces.py` (canonical, 8428 bytes) | DELETE |
| `postgresql_access.py` (17840 bytes) | PostgreSQL data access impl | Zero external callers | 重复冗余 | `src/data_access/postgresql_access.py` (17519 bytes, canonical) | DELETE |
| `tdengine_access.py` (23514 bytes) | TDengine data access impl | Zero external callers | 重复冗余 | `src/data_access/tdengine_access.py` (2770 bytes, canonical) | INVESTIGATE |
| `_postgresql_access_query_mixin.py` (8800 bytes) | PostgreSQL query mixin | 1 internal caller only | 重复冗余 | `postgresql_access.py:12` imports it | DELETE |

**Sweep A — Static imports (external callers only):**
```
src/data_access_pkg/postgresql_access.py:12:from src.data_access_pkg._postgresql_access_query_mixin import PostgreSQLDataAccessQueryMixin
```
(Internal self-import only — zero external callers)

**Sweep B — String references in main tree (excluding .worktrees):**
```
web/backend/tests/test_database_config_regressions.py:48:        "src.data_access_pkg.postgresql_access",
web/backend/tests/test_database_config_regressions.py:49:        "src.data_access_pkg.tdengine_access",
web/backend/tests/test_database_config_regressions.py:54:        if loaded_name.startswith("src.data_access_pkg"):
```

---

### Table 4: src/db_manager/ (1 file)

| File | Purpose | Code-Path Status | Functional-Tree Status | Callers (file:line) | Action |
|------|---------|-----------------|----------------------|--------------------|--------|
| `__init__.py` | Compatibility shim — re-exports from `src.storage.database` | Zero callers (scripts have mapping rules, not imports) | 重复冗余 | None | DELETE |

**Content: Re-exports `connection_manager`, `database_manager`, `db_utils`, `DatabaseConnectionManager`, `DatabaseTableManager`, `DatabaseType` from `src.storage.database`.**

**Sweep B — String references in main tree (excluding .worktrees):**
```
tests/unit/test_config_driven_table_manager.py:69:    @patch("src.db_manager.connection_manager.DatabaseConnectionManager")
tests/unit/test_config_driven_table_manager.py:85:    @patch("src.db_manager.connection_manager.DatabaseConnectionManager")
tests/unit/test_config_driven_table_manager.py:108:    @patch("src.db_manager.connection_manager.DatabaseConnectionManager")
tests/unit/test_config_driven_table_manager.py:139:    @patch("src.db_manager.connection_manager.DatabaseConnectionManager")
```

---

### Table 5: src/database_optimization/ (5 files)

| File | Purpose | Code-Path Status | Functional-Tree Status | Callers (file:line) | Action |
|------|---------|-----------------|----------------------|--------------------|--------|
| `__init__.py` | Exports 4 optimizer classes | Zero external callers | 重复冗余 | None | DELETE after merge |
| `performance_monitor.py` (11262 bytes) | Index performance monitoring | 2 test callers | 重复冗余 (unique — no canonical equivalent) | `tests/unit/database_optimization/test_performance_monitor.py:19` | MERGE → `src/data_access/optimizers/performance_monitor.py` |
| `postgresql_index_optimizer.py` (15264 bytes) | PostgreSQL index optimization | Zero external callers | 重复冗余 (unique — no canonical equivalent) | None | MERGE → `src/data_access/optimizers/postgresql_index_optimizer.py` |
| `slow_query_analyzer.py` (13040 bytes) | Slow query analysis | Zero external callers | 重复冗余 (unique — no canonical equivalent) | None | MERGE → `src/data_access/optimizers/slow_query_analyzer.py` |
| `tdengine_index_optimizer.py` (8546 bytes) | TDengine index optimization | Zero external callers | 重复冗余 (unique — no canonical equivalent) | None | MERGE → `src/data_access/optimizers/tdengine_index_optimizer.py` |

**Sweep A — Static imports (external callers only):**
```
tests/unit/database_optimization/test_performance_monitor.py:19:from src.database_optimization.performance_monitor import IndexPerformanceMonitor
scripts/tests/test_database_optimization.py:18:from src.database_optimization import (...)
```

**Note:** `src/data_access/optimizers/` already exists with `query_optimizer.py` — merge adds 4 new files, no conflicts.

---

## Special Cases

### Circular Dependency: database_service.py ↔ wencai_routes.py

```
database_service.py:155:    from src.routes.wencai_routes import execute_custom_query, get_query_results
```
- The import is inside a function body (lazy import to avoid circular dep)
- `wencai_routes.py` calls `db_service.execute_wencai_query()` at lines 180, 254, 335, 484
- The import targets `execute_custom_query` and `get_query_results` — function names that likely don't exist in wencai_routes with those exact signatures
- **Callers of `database_service.py`'s wencai method** (`real_data_source.py:135,139,144`) are also dead paths
- **Both the import AND the function names are wrong** — method crashes at runtime
- **Verdict:** Safe to remove — the circular dependency is broken at runtime already

### Broken Import: tests/api_contract_tests.py

```
tests/api_contract_tests.py:21:from src.api.types.common import APIResponse
tests/api_contract_tests.py:22:from src.api.types.market import MarketOverview, MarketOverviewData
tests/api_contract_tests.py:23:from src.api.types.strategy import BacktestRequest, BacktestResponse, StrategyInfo
```
- `src/api/types/` DOES NOT EXIST as a Python package (verified by `ls src/api/types/` → "No such file or directory")
- These imports already raise `ImportError` at import time
- **Verdict:** Test file is dead — needs broken import cleanup, NOT type migration

### Size Discrepancy: tdengine_access.py

| Version | Size | Content |
|---------|------|---------|
| `src/data_access_pkg/tdengine_access.py` | 23,514 bytes (9x larger) | Legacy: full `TDengineDataAccess` class with `IDataAccessLayer` interface, monitoring_db dependency |
| `src/data_access/tdengine_access.py` | 2,770 bytes | Modern: thin re-export wrapper importing from `src/data_access/_tdengine_query_operations.py` and `_tdengine_write_operations.py` |

**Root cause:** The canonical `src/data_access/tdengine_access.py` was refactored to a thin facade during a prior restructuring. The actual 23KB of functionality was split into sub-modules (`_tdengine_query_operations.py`, `_tdengine_write_operations.py`, `_tdengine_validation.py`). The `data_access_pkg` version is the OLD monolithic file.
- **Verdict:** Canonical is authoritative (D-05). The old monolithic code is redundant — DELETE.

---

## Caller Redirection Map

| Current Import | Status | Correct Action | Files Affected |
|---------------|--------|---------------|---------------|
| `from src.routes.wencai_routes import execute_custom_query, get_query_results` | BROKEN (wrong names, circular dep) | Remove dead import + dead method body | `src/database/services/database_service.py:155` |
| `from src.api.types.common import APIResponse` | BROKEN (no such module) | Delete broken test file or fix imports | `tests/api_contract_tests.py:21-23` |
| `from src.database_optimization.performance_monitor import IndexPerformanceMonitor` | WORKING (test) | Redirect to `src.data_access.optimizers.performance_monitor` | `tests/unit/database_optimization/test_performance_monitor.py:19` |
| `from src.database_optimization import (...)` | WORKING (test) | Redirect to `src.data_access.optimizers.*` | `scripts/tests/test_database_optimization.py:18` |
| `@patch("src.db_manager.connection_manager.DatabaseConnectionManager")` | WORKING (mock patch) | Redirect to `src.storage.database.connection_manager.DatabaseConnectionManager` | `tests/unit/test_config_driven_table_manager.py:69,85,108,139` |
| `scripts/cicd_pipeline.sh: from src.routes import *` | WORKING (CI smoke test) | Remove or replace with canonical route check | `scripts/cicd_pipeline.sh:184` |
| `scripts/dev/quality_gate/fix_test_imports.py:41` | MAPPING RULE | Update mapping to point to canonical locations | `scripts/dev/quality_gate/fix_test_imports.py` |
| `scripts/dev/project/update_imports.py:16,27` | MAPPING RULE | Remove `src.db_manager` mapping | `scripts/dev/project/update_imports.py` |
| `web/backend/tests/test_database_config_regressions.py:48-54` | WORKING (regression test) | Remove `src.data_access_pkg` references from test | `web/backend/tests/test_database_config_regressions.py` |

---

## Sweep Completeness Matrix

| Sweep | Type | src/routes | src/api | src/data_access_pkg | src/db_manager | src/database_optimization |
|-------|------|-----------|--------|--------------------|---------------|-------------------------|
| A | Static imports | 1 prod + 1 CI | 1 test (broken) | 1 internal | 0 | 2 tests |
| B | String/dynamic refs | 0 | 0 | 1 test file | 1 test file (4 mocks) | 2 report files |
| C | Dynamic imports | 0 | 0 | 0 | 0 | 0 |
| D | `__all__`/namespace | 3 `__all__` | 2 `__all__` | 1 `__all__` | 1 `__all__` | 1 `__all__` |
| E | Shell-embedded | 1 CI script | 0 | 0 | 0 | 0 |
| F | Compat shim chains | 1 external | 0 | 0 | 0 | 0 |
| G | Route registration | 11 APIRouter instances | 3 APIRouter instances | N/A | N/A | N/A |
| H | Build/packaging | 0 | 0 | 0 | 0 | 0 |

---

## Verification Commands

```bash
# Post-deletion verification
test ! -d src/routes && echo "routes GONE" || echo "routes EXISTS"
test ! -d src/api && echo "api GONE" || echo "api EXISTS"
test ! -d src/data_access_pkg && echo "data_access_pkg GONE" || echo "data_access_pkg EXISTS"
test ! -d src/db_manager && echo "db_manager GONE" || echo "db_manager EXISTS"
test ! -d src/database_optimization && echo "database_optimization GONE" || echo "database_optimization EXISTS"

# Functional verification
ruff check src/ web/backend/app/ --select F821 | wc -l
cd web/backend && PYTHONPATH=$(git rev-parse --show-toplevel):. python -c "from app.main import app; print('OK')"
pytest --tb=short
```
