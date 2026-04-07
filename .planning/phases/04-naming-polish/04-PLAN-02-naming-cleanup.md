---
wave: 2
depends_on: [04-PLAN-01]
files_modified:
  - src/calcu/ (delete)
  - "src/adapters/efinance_adapter/efinance_data_source_methods/part*.py"
  - "src/core/deduplication_strategy_methods/part*.py"
  - "src/data_sources/real/postgresql_relational/postgre_sql_relational_data_source_methods/part*.py"
  - "src/data_sources/real/tdengine_timeseries/t_dengine_time_series_data_source_methods/part*.py"
  - "src/governance/risk_management/calculators/gpu_calculator/gpu_risk_calculator_methods/part*.py"
  - "src/governance/risk_management/services/stop_loss_engine/stop_loss_engine_methods/part*.py"
  - "src/gpu/acceleration/feature_calculation_gpu/feature_calculation_gpu_methods/part*.py"
  - "src/gpu/acceleration/optimization_gpu_methods/part*.py"
  - "src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/part*.py"
  - "src/monitoring/monitoring_database_methods/part*.py"
  - "src/storage/database/database_manager/database_table_manager_methods/part*.py"
  - "src/database/database_service_new.py"
  - "src/database/database_service.py"
  - "src/advanced_analysis/decision_models/decision_models_analyzer_new.py"
  - "src/advanced_analysis/decision_models_analyzer.py"
  - "web/frontend/src/stores/baseStore.ts.bak"
requirements_addressed: [NAME-01, NAME-02, NAME-03]
autonomous: true
must_haves:
  - Zero part{1,2,3}.py files remain in src/
  - Zero *_new.py files remain in src/
  - src/calcu/ directory deleted
  - baseStore.ts.bak deleted
  - All __init__.py files updated with new import paths
  - ruff check src/ shows no new errors
---

# Plan 02: Naming Cleanup (NAME-01, NAME-02, NAME-03)

**Objective:** Replace 32 mechanical part-file splits with semantic names, handle 2 _new.py files, delete empty src/calcu/ directory, and remove stale .bak file.

## Task 1: Delete src/calcu/ directory (NAME-01)

<read_first>
- `src/calcu/readme.md` — confirm documentation-only
- `src/calcu/block/板块表现算法.md` — confirm documentation-only
</read_first>

<action>
1. Verify no Python files exist: `find src/calcu/ -name "*.py"` must return empty
2. Verify no importers: `grep -rn "from src\.calcu\|import src\.calcu" --include="*.py" .` must return empty (excluding worktrees/archive)
3. Delete: `git rm -r src/calcu/`
</action>

<acceptance_criteria>
- `ls src/calcu/` returns "No such file or directory"
- `find src/ -path "*/calcu*"` returns empty
- `grep -rn "calcu" --include="*.py" src/` returns empty (no dangling references)
</acceptance_criteria>

## Task 2: Rename part files in 11 modules (NAME-02)

<read_first>
For EACH module, read the `__init__.py` first (contains import map), then the part files:
- `src/adapters/efinance_adapter/efinance_data_source_methods/__init__.py`
- `src/core/deduplication_strategy_methods/__init__.py`
- `src/data_sources/real/postgresql_relational/postgre_sql_relational_data_source_methods/__init__.py`
- `src/data_sources/real/tdengine_timeseries/t_dengine_time_series_data_source_methods/__init__.py`
- `src/governance/risk_management/calculators/gpu_calculator/gpu_risk_calculator_methods/__init__.py`
- `src/governance/risk_management/services/stop_loss_engine/stop_loss_engine_methods/__init__.py`
- `src/gpu/acceleration/feature_calculation_gpu/feature_calculation_gpu_methods/__init__.py`
- `src/gpu/acceleration/optimization_gpu_methods/__init__.py`
- `src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/__init__.py`
- `src/monitoring/monitoring_database_methods/__init__.py`
- `src/storage/database/database_manager/database_table_manager_methods/__init__.py`
</read_first>

<action>
For each of the 11 modules, execute this rename sequence (WSL2 two-step git mv pattern):

**Module 1: efinance_data_source_methods**
```
git mv src/adapters/efinance_adapter/efinance_data_source_methods/part1.py src/adapters/efinance_adapter/efinance_data_source_methods/_tmp_core.py
git mv src/adapters/efinance_adapter/efinance_data_source_methods/_tmp_core.py src/adapters/efinance_adapter/efinance_data_source_methods/core.py
git mv src/adapters/efinance_adapter/efinance_data_source_methods/part2.py src/adapters/efinance_adapter/efinance_data_source_methods/_tmp_get_bond_basic.py
git mv src/adapters/efinance_adapter/efinance_data_source_methods/_tmp_get_bond_basic.py src/adapters/efinance_adapter/efinance_data_source_methods/get_bond_basic.py
git mv src/adapters/efinance_adapter/efinance_data_source_methods/part3.py src/adapters/efinance_adapter/efinance_data_source_methods/_tmp_bond_quote.py
git mv src/adapters/efinance_adapter/efinance_data_source_methods/_tmp_bond_quote.py src/adapters/efinance_adapter/efinance_data_source_methods/bond_quote.py
```
Then update `__init__.py`: change `from .part1 import` → `from .core import`, `from .part2 import` → `from .get_bond_basic import`, `from .part3 import` → `from .bond_quote import`

**Module 2: deduplication_strategy_methods**
```
part1.py → core.py, part2.py → validate_single_table.py, part3.py → validation.py
```
`__init__.py`: `from .part1` → `from .core`, `from .part2` → `from .validate_single_table`, `from .part3` → `from .validation`

**Module 3: postgre_sql_relational_data_source_methods**
```
part1.py → core.py, part2.py → get_stock_basic.py, part3.py → preferences.py
```
`__init__.py`: `from .part1` → `from .core`, `from .part2` → `from .get_stock_basic`, `from .part3` → `from .preferences`

**Module 4: t_dengine_time_series_data_source_methods**
```
part1.py → core.py, part2.py → check_data_quality.py
```
`__init__.py`: `from .part1` → `from .core`, `from .part2` → `from .check_data_quality`

**Module 5: gpu_risk_calculator_methods**
```
part1.py → core.py, part2.py → get_concentration_level.py, part3.py → portfolio_events.py
```
`__init__.py`: `from .part1` → `from .core`, `from .part2` → `from .get_concentration_level`, `from .part3` → `from .portfolio_events`

**Module 6: stop_loss_engine_methods**
```
part1.py → core.py, part2.py → calculate_trigger_confidence.py, part3.py → risk_assessment.py
```
`__init__.py`: `from .part1` → `from .core`, `from .part2` → `from .calculate_trigger_confidence`, `from .part3` → `from .risk_assessment`

**Module 7: feature_calculation_gpu_methods**
```
part1.py → core.py, part2.py → calculate_price_volume.py, part3.py → post_volume.py
```
`__init__.py`: `from .part1` → `from .core`, `from .part2` → `from .calculate_price_volume`, `from .part3` → `from .post_volume`

**Module 8: optimization_gpu_methods**
```
part1.py → core.py, part2.py → risk_parity_optimization.py, part3.py → portfolio.py
```
`__init__.py`: `from .part1` → `from .core`, `from .part2` → `from .risk_parity_optimization`, `from .part3` → `from .portfolio`

**Module 9: resource_scheduler_methods**
```
part1.py → core.py, part2.py → calculate_queue_efficiency.py, part3.py → performance.py
```
`__init__.py`: `from .part1` → `from .core`, `from .part2` → `from .calculate_queue_efficiency`, `from .part3` → `from .performance`

**Module 10: monitoring_database_methods**
```
part1.py → core.py, part2.py → cleanup_old_records.py, part3.py → history.py
```
`__init__.py`: `from .part1` → `from .core`, `from .part2` → `from .cleanup_old_records`, `from .part3` → `from .history`

**Module 11: database_table_manager_methods**
```
part1.py → core.py, part2.py → close_all_connections.py, part3.py → ddl_info.py
```
`__init__.py`: `from .part1` → `from .core`, `from .part2` → `from .close_all_connections`, `from .part3` → `from .ddl_info`
</action>

<acceptance_criteria>
- `find src/ -name "part*.py" -path "*/_methods/*"` returns zero results
- For each of the 11 `__init__.py` files: `grep "from .part" __init__.py` returns zero results
- For each of the 11 `__init__.py` files: `grep "from .core import"` returns at least 1 result
- `PYTHONPATH=. python -c "from src.monitoring.monitoring_database_methods import MonitoringDatabase; print('OK')"` exits 0
- `PYTHONPATH=. python -c "from src.adapters.efinance_adapter.efinance_data_source_methods import EfinanceDataSource; print('OK')"` exits 0
- `ruff check src/ --select F401,E701` does not show new errors in any `__init__.py`
</acceptance_criteria>

## Task 3: Handle *_new.py files (NAME-03)

<read_first>
- `src/database/database_service_new.py` — the new version
- `src/database/database_service.py` — the canonical version to compare
- `src/advanced_analysis/decision_models/decision_models_analyzer_new.py` — the new version
- `src/advanced_analysis/decision_models_analyzer.py` — the canonical version to compare
- `src/advanced_analysis/decision_models/__init__.py` — check subpackage structure
</read_first>

<action>
1. **database_service_new.py** (same directory):
   - Compare `database_service_new.py` (78 lines) with `database_service.py`
   - If `_new` is a clean replacement: `git rm src/database/database_service.py && git mv src/database/database_service_new.py src/database/database_service.py`
   - If canonical has extra content not in `_new`: merge and then replace

2. **decision_models_analyzer_new.py** (different directory):
   - This file is inside `decision_models/` subpackage but must replace `decision_models_analyzer.py` in parent `advanced_analysis/`
   - Compare both files
   - If `_new` is a clean replacement: `git rm src/advanced_analysis/decision_models_analyzer.py && git mv src/advanced_analysis/decision_models/decision_models_analyzer_new.py src/advanced_analysis/decision_models_analyzer.py`
   - Update any imports in `src/advanced_analysis/__init__.py` if needed
</action>

<acceptance_criteria>
- `find src/ -name "*_new.py"` returns zero results
- `ls src/database/database_service.py` exists (renamed from _new)
- `ls src/advanced_analysis/decision_models_analyzer.py` exists (renamed from _new)
- `PYTHONPATH=. python -c "from src.database.database_service import DatabaseService; print('OK')"` exits 0
- `PYTHONPATH=. python -c "from src.advanced_analysis.decision_models_analyzer import DecisionModelsAnalyzer; print('OK')"` exits 0
</acceptance_criteria>

## Task 4: Delete stale backup files

<read_first>
- `web/frontend/src/stores/baseStore.ts.bak` — verify it's the stale version
- `web/frontend/src/stores/baseStore.ts` — verify active version exists
</read_first>

<action>
1. Confirm zero imports: `grep -rn "baseStore\.ts\.bak" web/` returns empty
2. Delete: `git rm web/frontend/src/stores/baseStore.ts.bak`
</action>

<acceptance_criteria>
- `ls web/frontend/src/stores/baseStore.ts.bak` returns "No such file or directory"
- `find . -name "*.bak" -o -name "*.backup"` in src/ returns empty
</acceptance_criteria>

## Verification

```bash
# No part files remain
find src/ -name "part*.py" -path "*/_methods/*" | wc -l | grep -q 0

# No _new.py files remain
find src/ -name "*_new.py" | wc -l | grep -q 0

# No .bak files in stores
ls web/frontend/src/stores/*.bak 2>&1 | grep -q "No such file"

# Lint check
ruff check src/ web/backend/app/ --statistics | tail -5

# Frontend builds
cd web/frontend && npm run build
```
