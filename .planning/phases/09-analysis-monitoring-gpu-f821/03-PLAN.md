---
plan: 03
wave: 1
phase: 9
depends_on: []
autonomous: true
files_modified:
  - src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/core.py
  - src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/calculate_queue_efficiency.py
  - src/gpu/api_system/utils/cache_optimization_enhanced.py
  - src/gpu/api_system/services/integrated_ml_service.py
  - src/gpu/api_system/utils/gpu_acceleration_engine/feature_calculation_gpu.py
  - src/gpu/api_system/services/backtest_service/backtest_service.py
requirements:
  - LINT-08
must_haves:
  - ruff check src/gpu/ --select F821 reports 0 errors
  - No logic changes — only import lines
---

# Plan 03: Resolve F821 Errors in src/gpu/

**Objective:** Fix all 46 F821 (undefined-name) errors across 6 files in `src/gpu/` by adding missing imports.

## Task 1: Fix resource_scheduler_methods/core.py (34 errors)

<read_first>
- src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/core.py
- src/gpu/api_system/services/resource_scheduler/helpers.py (canonical source for Task, TaskStatus, TaskType, TaskPriority)
</read_first>

<action>
Add the following import at the top of `src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/core.py`:

```python
from src.gpu.api_system.services.resource_scheduler.helpers import Task, TaskStatus, TaskType, TaskPriority
```

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/core.py` contains `from src.gpu.api_system.services.resource_scheduler.helpers import Task, TaskStatus, TaskType, TaskPriority`
- `ruff check src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/core.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 2: Fix cache_optimization_enhanced.py (4 errors)

<read_first>
- src/gpu/api_system/utils/cache_optimization_enhanced.py
- src/gpu/api_system/utils/cache_optimization.py (canonical source for MultiLevelCache class at line 303)
</read_first>

<action>
Add the following import at the top of `src/gpu/api_system/utils/cache_optimization_enhanced.py`:

1. Local types: `from src.gpu.api_system.utils.cache_optimization import MultiLevelCache`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/gpu/api_system/utils/cache_optimization_enhanced.py` contains `from src.gpu.api_system.utils.cache_optimization import MultiLevelCache`
- `ruff check src/gpu/api_system/utils/cache_optimization_enhanced.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 3: Fix integrated_ml_service.py (4 errors)

<read_first>
- src/gpu/api_system/services/integrated_ml_service.py
</read_first>

<action>
Add the following import at the top of `src/gpu/api_system/services/integrated_ml_service.py`:

1. Stdlib: `import json`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/gpu/api_system/services/integrated_ml_service.py` contains `import json`
- `ruff check src/gpu/api_system/services/integrated_ml_service.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 4: Fix feature_calculation_gpu.py (2 errors)

<read_first>
- src/gpu/api_system/utils/gpu_acceleration_engine/feature_calculation_gpu.py
- src/gpu/api_system/utils/gpu_acceleration_engine/backtest_engine_gpu.py (canonical source for BacktestEngineGPU, MLTrainingGPU)
</read_first>

<action>
Add the following import at the top of `src/gpu/api_system/utils/gpu_acceleration_engine/feature_calculation_gpu.py`:

1. Local types: `from src.gpu.api_system.utils.gpu_acceleration_engine.backtest_engine_gpu import BacktestEngineGPU, MLTrainingGPU`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/gpu/api_system/utils/gpu_acceleration_engine/feature_calculation_gpu.py` contains `from src.gpu.api_system.utils.gpu_acceleration_engine.backtest_engine_gpu import BacktestEngineGPU, MLTrainingGPU`
- `ruff check src/gpu/api_system/utils/gpu_acceleration_engine/feature_calculation_gpu.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 5: Fix calculate_queue_efficiency.py (1 error)

<read_first>
- src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/calculate_queue_efficiency.py
- src/gpu/api_system/services/resource_scheduler/helpers.py (canonical source for TaskStatus)
</read_first>

<action>
Add the following import at the top of `src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/calculate_queue_efficiency.py`:

1. Local types: `from src.gpu.api_system.services.resource_scheduler.helpers import TaskStatus`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/calculate_queue_efficiency.py` contains `from src.gpu.api_system.services.resource_scheduler.helpers import TaskStatus`
- `ruff check src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/calculate_queue_efficiency.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 6: Fix backtest_service.py (1 error)

<read_first>
- src/gpu/api_system/services/backtest_service/backtest_service.py
- src/gpu/api_system/services/backtest_service/backtest_engine.py (canonical source for BacktestEngine)
</read_first>

<action>
Add the following import at the top of `src/gpu/api_system/services/backtest_service/backtest_service.py`:

1. Local types: `from src.gpu.api_system.services.backtest_service.backtest_engine import BacktestEngine`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/gpu/api_system/services/backtest_service/backtest_service.py` contains `from src.gpu.api_system.services.backtest_service.backtest_engine import BacktestEngine`
- `ruff check src/gpu/api_system/services/backtest_service/backtest_service.py --select F821` reports 0 errors
</acceptance_criteria>

## Verification

```bash
ruff check src/gpu/ --select F821 --statistics
# MUST report: 0 errors
```
