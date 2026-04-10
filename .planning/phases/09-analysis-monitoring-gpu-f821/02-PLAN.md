---
plan: 02
wave: 1
phase: 9
depends_on: []
autonomous: true
files_modified:
  - src/monitoring/multi_channel_alert_manager/multi_channel_alert_manager.py
  - src/monitoring/threshold/manager.py
  - src/monitoring/threshold/factory.py
  - src/monitoring/threshold/advanced_optimizers.py
  - src/monitoring/threshold/statistical_optimizer.py
  - src/monitoring/threshold/data_analyzer.py
  - src/monitoring/threshold/dataclasses.py
  - src/monitoring/gpu_performance_optimizer/main.py
requirements:
  - LINT-07
must_haves:
  - ruff check src/monitoring/ --select F821 reports 0 errors
  - No logic changes — only import lines
---

# Plan 02: Resolve F821 Errors in src/monitoring/

**Objective:** Fix all 83 F821 (undefined-name) errors across 8 files in `src/monitoring/` by adding missing imports.

## Task 1: Fix multi_channel_alert_manager.py (28 errors)

<read_first>
- src/monitoring/multi_channel_alert_manager/multi_channel_alert_manager.py
- src/monitoring/multi_channel_alert_manager/alert_channel_config.py (canonical source for ALL alert types)
</read_first>

<action>
Add the following import at the top of `src/monitoring/multi_channel_alert_manager/multi_channel_alert_manager.py`:

```python
from src.monitoring.multi_channel_alert_manager.alert_channel_config import (
    AlertHandler,
    AlertChannelConfig,
    EmailConfig,
    EmailAlertHandler,
    WebhookConfig,
    WebhookAlertHandler,
    LogConfig,
    LogAlertHandler,
)
```

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/monitoring/multi_channel_alert_manager/multi_channel_alert_manager.py` contains `from src.monitoring.multi_channel_alert_manager.alert_channel_config import (`
- `src/monitoring/multi_channel_alert_manager/multi_channel_alert_manager.py` contains `AlertHandler,`
- `src/monitoring/multi_channel_alert_manager/multi_channel_alert_manager.py` contains `EmailAlertHandler,`
- `src/monitoring/multi_channel_alert_manager/multi_channel_alert_manager.py` contains `WebhookAlertHandler,`
- `src/monitoring/multi_channel_alert_manager/multi_channel_alert_manager.py` contains `LogAlertHandler,`
- `ruff check src/monitoring/multi_channel_alert_manager/multi_channel_alert_manager.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 2: Fix threshold/manager.py (25 errors)

<read_first>
- src/monitoring/threshold/manager.py
- src/monitoring/threshold/dataclasses.py (canonical source for ThresholdRule, ThresholdAdjustment, OptimizationResult)
</read_first>

<action>
Add the following imports at the top of `src/monitoring/threshold/manager.py`:

1. Stdlib: `from dataclasses import asdict`
2. Local types:
   - `from src.monitoring.threshold.dataclasses import ThresholdRule, ThresholdAdjustment, OptimizationResult`
   - `from src.monitoring.monitoring_database import get_monitoring_database`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/monitoring/threshold/manager.py` contains `from dataclasses import asdict`
- `src/monitoring/threshold/manager.py` contains `from src.monitoring.threshold.dataclasses import ThresholdRule, ThresholdAdjustment, OptimizationResult`
- `src/monitoring/threshold/manager.py` contains `from src.monitoring.monitoring_database import get_monitoring_database`
- `ruff check src/monitoring/threshold/manager.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 3: Fix threshold/factory.py (10 errors)

<read_first>
- src/monitoring/threshold/factory.py
</read_first>

<action>
Add the following imports at the top of `src/monitoring/threshold/factory.py`:

1. Stdlib: `import asyncio`
2. Stdlib: `from datetime import datetime`
3. Typing: `from typing import Optional, Dict, Any`
4. Local types: `from src.monitoring.threshold.dataclasses import OptimizationResult`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/monitoring/threshold/factory.py` contains `import asyncio`
- `src/monitoring/threshold/factory.py` contains `from datetime import datetime`
- `src/monitoring/threshold/factory.py` contains `from typing import Optional, Dict, Any`
- `src/monitoring/threshold/factory.py` contains `from src.monitoring.threshold.dataclasses import OptimizationResult`
- `ruff check src/monitoring/threshold/factory.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 4: Fix threshold/advanced_optimizers.py (9 errors)

<read_first>
- src/monitoring/threshold/advanced_optimizers.py
</read_first>

<action>
Add the following imports at the top of `src/monitoring/threshold/advanced_optimizers.py`:

1. Stdlib: `from datetime import datetime`
2. Local types: `from src.monitoring.threshold.dataclasses import OptimizationResult`
3. Conditional third-party:
```python
try:
    from sklearn.cluster import DBSCAN
except ImportError:
    DBSCAN = None
```

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/monitoring/threshold/advanced_optimizers.py` contains `from datetime import datetime`
- `src/monitoring/threshold/advanced_optimizers.py` contains `from src.monitoring.threshold.dataclasses import OptimizationResult`
- `src/monitoring/threshold/advanced_optimizers.py` contains `from sklearn.cluster import DBSCAN`
- `ruff check src/monitoring/threshold/advanced_optimizers.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 5: Fix threshold/statistical_optimizer.py (4 errors)

<read_first>
- src/monitoring/threshold/statistical_optimizer.py
</read_first>

<action>
Add the following import at the top of `src/monitoring/threshold/statistical_optimizer.py`:

1. Local types: `from src.monitoring.threshold.dataclasses import OptimizationResult`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/monitoring/threshold/statistical_optimizer.py` contains `from src.monitoring.threshold.dataclasses import OptimizationResult`
- `ruff check src/monitoring/threshold/statistical_optimizer.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 6: Fix threshold/data_analyzer.py (3 errors)

<read_first>
- src/monitoring/threshold/data_analyzer.py
</read_first>

<action>
Add the following imports at the top of `src/monitoring/threshold/data_analyzer.py`:

1. Stdlib: `from collections import deque`
2. Stdlib: `from datetime import datetime`
3. Conditional third-party:
```python
try:
    from sklearn.ensemble import IsolationForest
except ImportError:
    IsolationForest = None
```

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/monitoring/threshold/data_analyzer.py` contains `from collections import deque`
- `src/monitoring/threshold/data_analyzer.py` contains `from datetime import datetime`
- `src/monitoring/threshold/data_analyzer.py` contains `from sklearn.ensemble import IsolationForest`
- `ruff check src/monitoring/threshold/data_analyzer.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 7: Fix threshold/dataclasses.py (2 errors)

<read_first>
- src/monitoring/threshold/dataclasses.py
</read_first>

<action>
Add the following imports at the top of `src/monitoring/threshold/dataclasses.py`:

1. Stdlib: `import warnings`
2. Stdlib: `import logging`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/monitoring/threshold/dataclasses.py` contains `import warnings`
- `src/monitoring/threshold/dataclasses.py` contains `import logging`
- `ruff check src/monitoring/threshold/dataclasses.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 8: Fix gpu_performance_optimizer/main.py (2 errors)

<read_first>
- src/monitoring/gpu_performance_optimizer/main.py
- src/monitoring/gpu_performance_optimizer/gpu_optimization_config.py (canonical source for GPUOptimizationConfig)
- src/monitoring/gpu_performance_optimizer/gpu_performance_optimizer.py (canonical source for initialize_gpu_optimizer)
</read_first>

<action>
Add the following imports at the top of `src/monitoring/gpu_performance_optimizer/main.py`:

1. Local types:
   - `from src.monitoring.gpu_performance_optimizer.gpu_optimization_config import GPUOptimizationConfig`
   - `from src.monitoring.gpu_performance_optimizer.gpu_performance_optimizer import initialize_gpu_optimizer`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/monitoring/gpu_performance_optimizer/main.py` contains `from src.monitoring.gpu_performance_optimizer.gpu_optimization_config import GPUOptimizationConfig`
- `src/monitoring/gpu_performance_optimizer/main.py` contains `from src.monitoring.gpu_performance_optimizer.gpu_performance_optimizer import initialize_gpu_optimizer`
- `ruff check src/monitoring/gpu_performance_optimizer/main.py --select F821` reports 0 errors
</acceptance_criteria>

## Verification

```bash
ruff check src/monitoring/ --select F821 --statistics
# MUST report: 0 errors
```
