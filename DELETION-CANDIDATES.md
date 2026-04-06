# Deletion Candidates - Phase 2 Review

> **历史盘点说明**:
> 本文件是 Phase 2 `Dead Code Inventory & Removal` 的审批稿，用于在任何删除动作之前，汇总目标层的代码路径证据、功能树判定、保留/删除建议、重定向目标和验证口径。
> 当前共享规则与删除门禁仍以 [architecture/STANDARDS.md](/opt/claude/mystocks_spec/architecture/STANDARDS.md) 为准；若涉及当前执行状态，再结合根目录 `AGENTS.md`、phase 主文档与最新验证结果核对。

**Generated:** 2026-04-07  
**Status:** PENDING USER APPROVAL  
**Phase:** 2 (`Dead Code Inventory & Removal`)

---

## Summary

| Target | Files | External Production Callers | Test/Script Callers | Functional Tree Status | Recommendation |
|---|---:|---:|---:|---|---|
| `src/routes/` | 19 | 1 | 2+ | Legacy pre-`web/backend` route layer | DELETE after caller redirection |
| `src/api/` | 5 | 0 | 1+ | Dead alternative route layer | DELETE after test/script handling |
| `src/data_access_pkg/` | 5 | 1 compatibility shim | 0 | Duplicate data access package | CONVERGE into `src/data_access/`, then DELETE |
| `src/db_manager/` | 1 | 0 | 3+ script rules | Compatibility re-export shim | DELETE after script rule cleanup |
| `src/database_optimization/` | 5 | 0 | 2+ | Useful optimization utilities in legacy location | MERGE unique files into `src/data_access/optimizers/`, then DELETE |

## Decision Notes

- `src/routes/` and `src/api/` are not safe to delete immediately. They still have at least one runtime caller or test/script dependencies.
- `src/api/types/*` does **not** exist in the current tree, but `tests/api_contract_tests.py` still imports it. This is a real inconsistency that must be resolved before deleting `src/api/`.
- `src/data_access_pkg/tdengine_access.py` is much larger than canonical `src/data_access/tdengine_access.py`, but canonical code is split across helper modules. This points to a refactor split, not automatically to missing functionality.
- `src/database_optimization/` is not pure dead code. Its optimizer classes appear unique and should be migrated before deletion.

---

## Table 1: `src/routes/` (19 files)

| File | Purpose | Functional Status | Known Callers | Action | Redirect / Canonical Target |
|---|---|---|---|---|---|
| `src/routes/_strategy_health_router.py` | Strategy health helper router | Legacy helper | Internal: `src/routes/strategy_routes.py:15` | DELETE | `web/backend/app/api/strategy.py` or `web/backend/app/api/strategy_management/*` |
| `src/routes/dashboard_routes.py` | Legacy dashboard market overview/statistics endpoints | Legacy route module | No external caller found | DELETE | `web/backend/app/api/dashboard.py`, `web/backend/app/api/dashboard_data_source.py`, `web/backend/app/api/market/*` |
| `src/routes/monitoring_routes.py` | Legacy monitoring router entry | Legacy wrapper | No external caller found | DELETE | `web/backend/app/api/monitoring.py`, `web/backend/app/api/monitoring_analysis.py` |
| `src/routes/monitoring_routes/__init__.py` | Package marker | Package marker only | Internal package use only | DELETE | N/A |
| `src/routes/monitoring_routes/_monitoring_control_tail.py` | Monitoring control tail implementations | Legacy helper | Internal: `check_use_mock_data.py:14` | DELETE | `web/backend/app/api/monitoring.py` |
| `src/routes/monitoring_routes/check_monitoring_health.py` | Monitoring health endpoint | Legacy route module | No external caller found | DELETE | `web/backend/app/api/health.py`, `web/backend/app/api/system/system_health.py`, `web/backend/app/api/monitoring.py` |
| `src/routes/monitoring_routes/check_use_mock_data.py` | Monitoring endpoints with mock switching | Legacy route module | Internal helper use only | DELETE | `web/backend/app/api/monitoring.py`, `web/backend/app/api/monitoring_watchlists.py`, `web/backend/app/api/monitoring_analysis.py` |
| `src/routes/stocks_routes.py` | Legacy stocks router entry | Legacy wrapper | No external caller found | DELETE | `web/backend/app/api/data/stocks.py`, `web/backend/app/api/stock_search.py`, `web/backend/app/api/watchlist.py` |
| `src/routes/stocks_routes/__init__.py` | Package marker | Package marker only | Internal package use only | DELETE | N/A |
| `src/routes/stocks_routes/_watchlist_router.py` | Watchlist add/remove helper router | Legacy helper | Internal: `check_use_mock_data.py:14` | DELETE | `web/backend/app/api/watchlist.py` |
| `src/routes/stocks_routes/check_stocks_health.py` | Stocks health endpoint | Legacy route module | No external caller found | DELETE | `web/backend/app/api/health.py`, `web/backend/app/api/system/system_health.py` |
| `src/routes/stocks_routes/check_use_mock_data.py` | Stocks detail/list/search/financial endpoints with mock switching | Legacy route module | Internal helper use only | DELETE | `web/backend/app/api/data/stocks.py`, `web/backend/app/api/stock_search.py`, `web/backend/app/api/watchlist.py` |
| `src/routes/stocks_routes/stocks_data_sources.py` | Stocks mock/data-service helpers | Legacy helper | Internal: `_watchlist_router.py:9`, `check_use_mock_data.py:15` | DELETE | Canonical logic should live under `web/backend/app/api/data/*` or service layer |
| `src/routes/strategy_routes.py` | Legacy strategy definitions/run/results endpoints | Legacy route module | Internal: `_strategy_health_router.py:17` | DELETE | `web/backend/app/api/strategy.py`, `web/backend/app/api/strategy_mgmt.py`, `web/backend/app/api/strategy_management/*` |
| `src/routes/technical_routes.py` | Legacy technical router entry | Legacy wrapper | No external caller found | DELETE | `web/backend/app/api/technical_analysis.py`, `web/backend/app/api/technical/routes.py`, `web/backend/app/api/v1/strategy/indicators.py` |
| `src/routes/technical_routes/__init__.py` | Package marker | Package marker only | Internal package use only | DELETE | N/A |
| `src/routes/technical_routes/check_use_mock_data.py` | Technical indicators/signals/history endpoints with mock switching | Legacy route module | Internal helper use only | DELETE | `web/backend/app/api/technical_analysis.py`, `web/backend/app/api/technical/routes.py` |
| `src/routes/technical_routes/get_support_resistance_levels.py` | Support/resistance + health endpoints | Legacy route module | No external caller found | DELETE | `web/backend/app/api/technical_analysis.py`, `web/backend/app/api/technical/routes.py` |
| `src/routes/wencai_routes.py` | Legacy Wencai query/results/history endpoints | **Still has runtime caller** | External: `src/database/services/database_service.py:155` | REDIRECT CALLER, then DELETE | `web/backend/app/api/wencai.py` |

### Functional Tree Judgment

- Current status: `失效但兼容保留`
- Reason: this is a full historical FastAPI route layer predating `web/backend/app/api/`, but one runtime compatibility path still imports `src.routes.wencai_routes`.
- Deletion safety status: **not yet safe**

### Code Path Evidence

```text
scripts/dev/quality_gate/fix_test_imports.py:41:    'from routes.': 'from src.routes.',
scripts/cicd_pipeline.sh:184:    from src.routes import *
src/database/services/database_service.py:155:            from src.routes.wencai_routes import execute_custom_query, get_query_results
src/routes/_strategy_health_router.py:17:        from src.routes.strategy_routes import check_use_mock_data, get_database_service
src/routes/strategy_routes.py:15:from src.routes._strategy_health_router import router as strategy_health_router
src/routes/monitoring_routes/check_use_mock_data.py:14:from src.routes.monitoring_routes._monitoring_control_tail import (
src/routes/stocks_routes/_watchlist_router.py:9:from src.routes.stocks_routes.stocks_data_sources import check_use_mock_data, get_database_service, get_stocks_mock_data
src/routes/stocks_routes/check_use_mock_data.py:14:from src.routes.stocks_routes._watchlist_router import router as watchlist_router
src/routes/stocks_routes/check_use_mock_data.py:15:from src.routes.stocks_routes.stocks_data_sources import check_use_mock_data, get_database_service, get_stocks_mock_data
src/routes/technical_routes/check_use_mock_data.py:15:from src.routes.technical_routes._technical_batch_indicators import batch_calculate_indicators_impl
```

### Additional Notes

- `scripts/cicd_pipeline.sh` still uses `from src.routes import *` as a smoke check. This is not a production caller, but it will break once deletion happens unless updated.
- Canonical Wencai route exists at `web/backend/app/api/wencai.py` with the same prefix `/api/market/wencai`.

---

## Table 2: `src/api/` (5 files)

| File | Purpose | Functional Status | Known Callers | Action | Redirect / Canonical Target |
|---|---|---|---|---|---|
| `src/api/alert_history_routes.py` | Full alert history REST route set | Dead alternative route layer | No external caller found | DELETE | If capability retained, align with `web/backend/app/api/risk/alerts.py` or `web/backend/app/api/v1/risk/alerts.py` |
| `src/api/datasource/__init__.py` | Package marker | Package marker only | Internal package use only | DELETE | N/A |
| `src/api/datasource/routes.py` | Data source registry / health / metrics routes | Dead alternative route layer | No external caller found | DELETE | `web/backend/app/api/multi_source.py`, `web/backend/app/api/multi_source/routes.py` |
| `src/api/governance/__init__.py` | Package marker | Package marker only | Internal package use only | DELETE | N/A |
| `src/api/governance/routes.py` | Data governance / lineage / assets routes | Dead alternative route layer | No external caller found | DELETE | `web/backend/app/api/governance_dashboard.py` |

### Functional Tree Judgment

- Current status: `重复冗余`
- Reason: route definitions exist here, but active backend route truth lives under `web/backend/app/api/`.
- Deletion safety status: **blocked by test/script references, not by production runtime callers**

### Code Path Evidence

```text
scripts/dev/quality_gate/fix_test_imports.py:42:    'from api.': 'from src.api.',
tests/api_contract_tests.py:21:from src.api.types.common import APIResponse
tests/api_contract_tests.py:22:from src.api.types.market import MarketOverview, MarketOverviewData
tests/api_contract_tests.py:23:from src.api.types.strategy import BacktestRequest, BacktestResponse, StrategyInfo
```

### Missing Module Evidence

Command used:

```bash
rg --files src/api | rg 'types'
```

Observed result:

```text
no matches
```

### Additional Notes

- `src/api/types/*` is referenced by tests but does not exist in the current tree.
- `APIResponse` has canonical candidates under:
  - `web/backend/app/schemas/common_schemas.py`
  - `web/backend/app/core/responses.py`
- `BacktestRequest` / `BacktestResponse` exist under:
  - `web/backend/app/schemas/backtest_schemas.py`
- `StrategyInfo` exists under:
  - `web/backend/app/api/v1/strategy/machine_learning.py`
- `MarketOverview` naming does not map 1:1. Current candidates are:
  - `web/backend/app/models/dashboard.py:MarketOverview`
  - `web/backend/app/schemas/market_schemas.py:MarketOverviewResponse`

This test import path must be reviewed before deletion.

---

## Table 3: `src/data_access_pkg/` (5 files)

| File | Purpose | Functional Status | Known Callers | Action | Redirect / Canonical Target |
|---|---|---|---|---|---|
| `src/data_access_pkg/__init__.py` | Legacy package export surface | Duplicate package root | External via root shim: `src/data_access.py:2` | REDIRECT, then DELETE | `src/data_access/__init__.py` |
| `src/data_access_pkg/interface.py` | Legacy `IDataAccessLayer` interface | Duplicate but divergent interface | No external caller found | CANONICAL WINS, then DELETE | `src/data_access/interfaces.py` |
| `src/data_access_pkg/postgresql_access.py` | Legacy PostgreSQL data access implementation | Duplicate implementation | Internal only: `_postgresql_access_query_mixin.py` | VERIFY parity, then DELETE | `src/data_access/postgresql_access.py` |
| `src/data_access_pkg/_postgresql_access_query_mixin.py` | Helper mixin for duplicate PostgreSQL implementation | Dead once duplicate impl is removed | Internal only: `postgresql_access.py:12` | DELETE with package | Canonical behavior is in `src/data_access/postgresql_access.py` |
| `src/data_access_pkg/tdengine_access.py` | Legacy monolithic TDengine implementation | Duplicate implementation in older shape | No external caller found | VERIFY split parity, then DELETE | `src/data_access/tdengine_access.py` + `_tdengine_*` helper modules |

### Functional Tree Judgment

- Current status: `重复冗余`
- Reason: this package duplicates the canonical data access concern already declared in roadmap truth sources as `src/data_access/`.
- Deletion safety status: **blocked only by compatibility import path**

### Code Path Evidence

```text
src/data_access.py:2:from data_access_pkg import *  # noqa: F401, F403
src/data_access_pkg/postgresql_access.py:12:from src.data_access_pkg._postgresql_access_query_mixin import PostgreSQLDataAccessQueryMixin
```

### Size / Structure Evidence

```text
596 src/data_access_pkg/tdengine_access.py
100 src/data_access/tdengine_access.py
481 src/data_access_pkg/postgresql_access.py
500 src/data_access/postgresql_access.py
83  src/data_access_pkg/interface.py
319 src/data_access/interfaces.py
```

### Interpretation

- `postgresql_access.py` is nearly the same scale in both locations, which supports "canonical wins".
- `tdengine_access.py` differs sharply in line count, but canonical `src/data_access/tdengine_access.py` is a facade over:
  - `src/data_access/_tdengine_query_operations.py`
  - `src/data_access/_tdengine_validation.py`
  - `src/data_access/_tdengine_write_operations.py`
- That means the size gap is likely due to refactor decomposition rather than automatically to missing capability.

### Additional Notes

- The only confirmed external compatibility path is root shim `src/data_access.py`.
- Before deletion, that shim must stop importing `data_access_pkg`.

---

## Table 4: `src/db_manager/` (1 file)

| File | Purpose | Functional Status | Known Callers | Action | Redirect / Canonical Target |
|---|---|---|---|---|---|
| `src/db_manager/__init__.py` | Compatibility re-export of `src.storage.database` | Thin compatibility shim | No runtime callers; script mapping rules only | DELETE after script cleanup | `src.storage.database` |

### Functional Tree Judgment

- Current status: `失效但兼容保留`
- Reason: no runtime use found; only script-side import rewrite rules still mention it.
- Deletion safety status: **likely safe after script rule cleanup**

### Code Path Evidence

```text
scripts/dev/quality_gate/fix_test_imports.py:32:    'from db_manager.': 'from src.db_manager.',
scripts/dev/fix_test_imports.py:28:    (r'\\bfrom db_manager import', 'from src.db_manager import'),
scripts/dev/fix_test_imports.py:29:    (r'\\bfrom db_manager\\.(\\w+) import', r'from src.db_manager.\\1 import'),
scripts/dev/project/update_imports.py:16:    "from db_manager": "from src.db_manager",
scripts/dev/project/update_imports.py:27:    "import db_manager": "import src.db_manager",
```

### Re-export Evidence

`src/db_manager/__init__.py` currently re-exports:

- `connection_manager`
- `database_manager`
- `db_utils`
- `DatabaseConnectionManager`
- `DatabaseTableManager`
- `DatabaseType`

All of them already come from `src.storage.database`.

---

## Table 5: `src/database_optimization/` (5 files)

| File | Purpose | Functional Status | Known Callers | Action | Redirect / Canonical Target |
|---|---|---|---|---|---|
| `src/database_optimization/__init__.py` | Legacy optimizer package export surface | Legacy package root | External via test script: `scripts/tests/test_database_optimization.py:18` | MERGE exports, then DELETE | `src/data_access/optimizers/__init__.py` |
| `src/database_optimization/performance_monitor.py` | Query/index performance monitoring utilities | Unique useful utility | Test caller: `tests/unit/database_optimization/test_performance_monitor.py:19` | MERGE | `src/data_access/optimizers/performance_monitor.py` |
| `src/database_optimization/postgresql_index_optimizer.py` | PostgreSQL index design/summary utilities | Unique useful utility | No runtime caller found | MERGE | `src/data_access/optimizers/postgresql_index_optimizer.py` |
| `src/database_optimization/slow_query_analyzer.py` | Slow query analysis and explain analysis | Unique useful utility | No runtime caller found | MERGE | `src/data_access/optimizers/slow_query_analyzer.py` |
| `src/database_optimization/tdengine_index_optimizer.py` | TDengine index/time-range/tag optimization utilities | Unique useful utility | No runtime caller found | MERGE | `src/data_access/optimizers/tdengine_index_optimizer.py` |

### Functional Tree Judgment

- Current status: `重复冗余`
- Reason: all 4 utility files duplicate concern space already declared under canonical `src/data_access/optimizers/`. The unique functionality must be merged into the canonical tree before deletion, but the package itself is structurally redundant.
- Deletion safety status: **not safe until merged**

### Code Path Evidence

```text
scripts/dev/quality_gate/fix_test_imports.py:46:    'from database_optimization.': 'from src.database_optimization.',
tests/unit/database_optimization/test_performance_monitor.py:19:from src.database_optimization.performance_monitor import IndexPerformanceMonitor
scripts/tests/test_database_optimization.py:18:from src.database_optimization import (
```

### Structure Evidence

```text
17  src/database_optimization/__init__.py
300 src/database_optimization/performance_monitor.py
362 src/database_optimization/postgresql_index_optimizer.py
311 src/database_optimization/slow_query_analyzer.py
218 src/database_optimization/tdengine_index_optimizer.py
621 src/data_access/optimizers/query_optimizer.py
```

### Interpretation

- Existing canonical `src/data_access/optimizers/query_optimizer.py` is a general query optimization framework, not a drop-in replacement for these 4 concrete utility classes.
- Recommendation is to **move**, not simply delete.

---

## Caller Redirection Map

| Current Import / Reference | Current Consumer | Proposed Redirect | Notes |
|---|---|---|---|
| `from src.routes.wencai_routes import execute_custom_query, get_query_results` | `src/database/services/database_service.py:155` | **Service layer only:** `from web.backend.app.services.wencai_service import get_wencai_service; svc = get_wencai_service(); svc.fetch_and_save(query_name, pages)` for custom queries; `svc.get_query_results(query_name, limit, offset)` for predefined queries. DO NOT redirect to API handler layer. | Import names already mismatch route function names — this import is broken at runtime. Redirect to `WencaiService` (not `wencai.py` API handlers) |
| `from src.routes import *` | `scripts/cicd_pipeline.sh:184` | Replace smoke check with `from web.backend.app.main import app` or canonical route module import | Script-only, but must be updated before deletion |
| `'from routes.': 'from src.routes.'` | `scripts/dev/quality_gate/fix_test_imports.py:41` | Remove rule or point to canonical `web.backend.app.api.*` targets | Dev tooling cleanup |
| `from src.api.types.common import APIResponse` | `tests/api_contract_tests.py:21` | `web/backend/app/schemas/common_schemas.py:APIResponse` | Direct candidate exists |
| `from src.api.types.market import MarketOverview, MarketOverviewData` | `tests/api_contract_tests.py:22` | Manual contract review required | No 1:1 canonical symbol found |
| `from src.api.types.strategy import BacktestRequest, BacktestResponse, StrategyInfo` | `tests/api_contract_tests.py:23` | `web/backend/app/schemas/backtest_schemas.py`, possibly `web/backend/app/api/v1/strategy/machine_learning.py:StrategyInfo` | Mixed source migration likely needed |
| `from data_access_pkg import *` | `src/data_access.py:2` | Replace with explicit re-exports from `src.data_access` | Required before deleting `src/data_access_pkg/` |
| `from src.db_manager.*` rewrite rules | `scripts/dev/*` | Point directly to `src.storage.database.*` | Script-only |
| `from src.database_optimization.*` | `tests/unit/database_optimization/test_performance_monitor.py`, `scripts/tests/test_database_optimization.py` | `src.data_access.optimizers.*` | Required before deletion |

---

## Verification Commands

These are the commands that should define the Phase 2 exit checks after redirection / merge / deletion work:

```bash
# Verify caller inventory stays explicit
rg -n "from src\\.routes\\b|import src\\.routes\\b|src\\.routes\\b" src web tests scripts .github config --glob '*.py' --glob '*.sh' --glob '*.yml' --glob '*.yaml' --glob '*.toml'
rg -n "from src\\.api\\b|import src\\.api\\b|src\\.api\\b" src web tests scripts .github config --glob '*.py' --glob '*.sh' --glob '*.yml' --glob '*.yaml' --glob '*.toml'
rg -n "from src\\.data_access_pkg\\b|import src\\.data_access_pkg\\b|from data_access_pkg\\b|import data_access_pkg\\b" src web tests scripts .github config --glob '*.py' --glob '*.sh' --glob '*.yml' --glob '*.yaml' --glob '*.toml'
rg -n "from src\\.db_manager\\b|import src\\.db_manager\\b|from db_manager\\b|import db_manager\\b" src web tests scripts .github config --glob '*.py' --glob '*.sh' --glob '*.yml' --glob '*.yaml' --glob '*.toml'
rg -n "from src\\.database_optimization\\b|import src\\.database_optimization\\b|from database_optimization\\b|import database_optimization\\b|src\\.database_optimization\\b" src web tests scripts .github config --glob '*.py' --glob '*.sh' --glob '*.yml' --glob '*.yaml' --glob '*.toml'

# Verify canonical backend imports still load
cd web/backend && PYTHONPATH=$(git rev-parse --show-toplevel):. python -c "from app.main import app; print('OK')"

# Verify lint regression does not worsen Phase 1 baseline
ruff check src/ web/backend/app/

# Verify tests after redirect / merge
pytest --tb=short
```

---

## Approval Scope

This document asks for approval of the following **sequence**, not of immediate deletion:

1. Approve inventory judgments and redirect targets
2. Approve caller redirection and optimizer merge work
3. Re-check affected imports and tests
4. Only then approve actual deletion of:
   - `src/routes/`
   - `src/api/`
   - `src/data_access_pkg/`
   - `src/db_manager/`
   - `src/database_optimization/`

Deletion is therefore a **separate final approval point**, not implied by this draft alone.
