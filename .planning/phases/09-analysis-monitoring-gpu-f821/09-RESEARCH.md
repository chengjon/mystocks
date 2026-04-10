# Phase 9: Analysis + Monitoring + GPU F821 - Research

**Date:** 2026-04-10
**Phase:** 09-analysis-monitoring-gpu-f821
**Status:** Research Complete

---

## Summary

220 F821 (undefined-name) errors across 24 files in 3 directories. All are missing imports except 7 non-mechanical errors in `canslim_analyzer.py` where `stock_data` is used outside its scope.

---

## Per-Directory Analysis

### 1. src/advanced_analysis/ (91 errors, 10 files)

#### Error Breakdown by File

| File | Errors | Category |
|------|--------|----------|
| `models/decision_synthesis.py` | 34 | Missing imports (stdlib + local types) |
| `chip_distribution_analyzer/_chip_concentration_tail.py` | 13 | Missing imports (stdlib + typing) |
| `anomaly/detection.py` | 9 | Missing imports (base types + GPU_AVAILABLE/IsolationForest) |
| `sentiment_analyzer/_sentiment_score_mixin.py` | 8 | Missing SNOWNLP_AVAILABLE/SnowNLP/jieba (needs try/except) |
| `decision_models/models/canslim_analyzer.py` | 7 | **Non-mechanical** — stock_data used outside scope |
| `anomaly/analysis_signals.py` | 7 | Missing imports (AnomalyCluster, AnalysisResult, AnalysisType) |
| `sentiment_analyzer/_generate_sentiment_signals.py` | 6 | Missing imports (SentimentScore, SentimentAlert, MarketSentimentImpact) |
| `decision_models_analyzer.py` | 4 | Missing imports (BaseAnalyzer, AnalysisResult, AnalysisType) |
| `trading_signals_analyzer/_assess_signal_risk.py` | 2 | Missing imports (TradingSignal) |
| `sentiment_analyzer/_sentiment_score_tail.py` | 1 | Missing import (List from typing) |

#### Canonical Import Sources (advanced_analysis)

| Undefined Name | Canonical Source | Import Statement |
|----------------|-----------------|------------------|
| `pd` | stdlib (pandas) | `import pandas as pd` |
| `Optional`, `Tuple`, `List` | stdlib (typing) | `from typing import Optional, Tuple, List` |
| `datetime` | stdlib | `from datetime import datetime` |
| `BaseAnalyzer` | `src.advanced_analysis.__init__` | `from src.advanced_analysis import BaseAnalyzer` |
| `AnalysisResult` | `src.advanced_analysis.__init__` | `from src.advanced_analysis import AnalysisResult` |
| `AnalysisType` | `src.advanced_analysis.__init__` | `from src.advanced_analysis import AnalysisType` |
| `AnomalyCluster` | `src.advanced_analysis.anomaly.dataclasses` | `from src.advanced_analysis.anomaly.dataclasses import AnomalyCluster` |
| `AnomalyAlert` | `src.advanced_analysis.anomaly.dataclasses` | `from src.advanced_analysis.anomaly.dataclasses import AnomalyAlert` |
| `GPU_AVAILABLE` | `src.advanced_analysis.anomaly.dataclasses` | `from src.advanced_analysis.anomaly.dataclasses import GPU_AVAILABLE` |
| `IsolationForest` | `src.advanced_analysis.anomaly.dataclasses` | `from src.advanced_analysis.anomaly.dataclasses import IsolationForest` |
| `BuffettModelScore` | `src.advanced_analysis.models.dataclasses` | `from src.advanced_analysis.models.dataclasses import BuffettModelScore` |
| `CANSLIMModelScore` | `src.advanced_analysis.models.dataclasses` | `from src.advanced_analysis.models.dataclasses import CANSLIMModelScore` |
| `FisherModelScore` | `src.advanced_analysis.models.dataclasses` | `from src.advanced_analysis.models.dataclasses import FisherModelScore` |
| `SentimentScore` | `src.advanced_analysis.sentiment_analyzer.sentiment_models` | `from src.advanced_analysis.sentiment_analyzer.sentiment_models import SentimentScore` |
| `SentimentAlert` | `src.advanced_analysis.sentiment_analyzer.sentiment_models` | `from src.advanced_analysis.sentiment_analyzer.sentiment_models import SentimentAlert` |
| `MarketSentimentImpact` | `src.advanced_analysis.sentiment_analyzer.sentiment_models` | `from src.advanced_analysis.sentiment_analyzer.sentiment_models import MarketSentimentImpact` |
| `TradingSignal` | `src.advanced_analysis.trading_signals_analyzer.trading_signal_models` | `from src.advanced_analysis.trading_signals_analyzer.trading_signal_models import TradingSignal` |

#### Non-Mechanical Error (canslim_analyzer.py)

- **File:** `src/advanced_analysis/decision_models/models/canslim_analyzer.py`
- **Lines:** 160-166 (7 uses of `stock_data`)
- **Issue:** `get_canslim_score(self, score)` at line ~144 uses `stock_data` variable that is NOT a parameter of the method
- **Fix:** Add `stock_data: Dict` parameter to the method signature
- **Constraint:** Minimal change — add parameter only, no refactoring to instance attributes

#### SNOWNLP/jieba Pattern

- **File:** `src/advanced_analysis/sentiment_analyzer/_sentiment_score_mixin.py`
- **4 uses** at lines 297, 351, 425, 530
- **Must create** module-level try/except block:
  ```python
  try:
      from snownlp import SnowNLP
      import jieba
      import jieba.analyse  # REQUIRED: extract_tags() needs submodule
      SNOWNLP_AVAILABLE = True
  except ImportError:
      SNOWNLP_AVAILABLE = False
  ```
- **Note:** `jieba.analyse.extract_tags()` at line 532 requires `import jieba.analyse` explicitly — bare `import jieba` does NOT expose `.analyse` at runtime

---

### 2. src/monitoring/ (83 errors, 8 files)

#### Error Breakdown by File

| File | Errors | Category |
|------|--------|----------|
| `multi_channel_alert_manager/multi_channel_alert_manager.py` | 28 | Missing imports (alert types) |
| `threshold/manager.py` | 25 | Missing imports (threshold types + stdlib) |
| `threshold/factory.py` | 10 | Missing imports (typing + stdlib + types) |
| `threshold/advanced_optimizers.py` | 9 | Missing imports (stdlib + sklearn + types) |
| `threshold/statistical_optimizer.py` | 4 | Missing imports (OptimizationResult) |
| `threshold/data_analyzer.py` | 3 | Missing imports (stdlib + IsolationForest) |
| `threshold/dataclasses.py` | 2 | Missing imports (stdlib: warnings, logging) |
| `gpu_performance_optimizer/main.py` | 2 | Missing imports (GPU config + initializer) |

#### Canonical Import Sources (monitoring)

| Undefined Name | Canonical Source | Import Statement |
|----------------|-----------------|------------------|
| `AlertHandler` | `src.monitoring.multi_channel_alert_manager.alert_channel_config` | `from src.monitoring.multi_channel_alert_manager.alert_channel_config import AlertHandler` |
| `AlertChannelConfig` | same | `from ... import AlertChannelConfig` |
| `EmailConfig` | same | `from ... import EmailConfig` |
| `WebhookConfig` | same | `from ... import WebhookConfig` |
| `LogConfig` | same | `from ... import LogConfig` |
| `EmailAlertHandler` | same | `from ... import EmailAlertHandler` |
| `WebhookAlertHandler` | same | `from ... import WebhookAlertHandler` |
| `LogAlertHandler` | same | `from ... import LogAlertHandler` |
| `ThresholdRule` | `src.monitoring.threshold.dataclasses` | `from src.monitoring.threshold.dataclasses import ThresholdRule` |
| `ThresholdAdjustment` | same | `from ... import ThresholdAdjustment` |
| `OptimizationResult` | same | `from ... import OptimizationResult` |
| `get_monitoring_database` | `src.monitoring.monitoring_database` | `from src.monitoring.monitoring_database import get_monitoring_database` |
| `GPUOptimizationConfig` | `src.monitoring.gpu_performance_optimizer.gpu_optimization_config` | `from src.monitoring.gpu_performance_optimizer.gpu_optimization_config import GPUOptimizationConfig` |
| `initialize_gpu_optimizer` | `src.monitoring.gpu_performance_optimizer.gpu_performance_optimizer` | `from src.monitoring.gpu_performance_optimizer.gpu_performance_optimizer import initialize_gpu_optimizer` |
| `asdict` | stdlib (dataclasses) | `from dataclasses import asdict` |
| `Optional`, `Dict`, `Any` | stdlib (typing) | `from typing import Optional, Dict, Any` |
| `datetime` | stdlib | `from datetime import datetime` |
| `asyncio` | stdlib | `import asyncio` |
| `deque` | stdlib (collections) | `from collections import deque` |
| `warnings` | stdlib | `import warnings` |
| `logging` | stdlib | `import logging` |
| `json` | stdlib | `import json` |
| `DBSCAN` | sklearn.cluster | `from sklearn.cluster import DBSCAN` (conditional) |
| `IsolationForest` | sklearn.ensemble | `from sklearn.ensemble import IsolationForest` (conditional) |

#### Monitoring Alert Import Consolidation

For `multi_channel_alert_manager.py` (28 errors, all from one module):
```python
from src.monitoring.multi_channel_alert_manager.alert_channel_config import (
    AlertHandler, AlertChannelConfig,
    EmailConfig, EmailAlertHandler,
    WebhookConfig, WebhookAlertHandler,
    LogConfig, LogAlertHandler,
)
```

#### Monitoring Threshold Import Consolidation

For `manager.py` (25 errors):
```python
from src.monitoring.threshold.dataclasses import ThresholdRule, ThresholdAdjustment, OptimizationResult
from src.monitoring.monitoring_database import get_monitoring_database
from dataclasses import asdict
```

---

### 3. src/gpu/ (46 errors, 6 files)

#### Error Breakdown by File

| File | Errors | Category |
|------|--------|----------|
| `resource_scheduler_methods/core.py` | 34 | Missing imports (Task, TaskStatus, TaskType, TaskPriority) |
| `cache_optimization_enhanced.py` | 4 | Missing imports (MultiLevelCache) |
| `integrated_ml_service.py` | 4 | Missing imports (stdlib: json) |
| `feature_calculation_gpu.py` | 2 | Missing imports (BacktestEngineGPU, MLTrainingGPU) |
| `calculate_queue_efficiency.py` | 1 | Missing import (TaskStatus) |
| `backtest_service.py` | 1 | Missing import (BacktestEngine) |

#### Canonical Import Sources (gpu)

| Undefined Name | Canonical Source | Import Statement |
|----------------|-----------------|------------------|
| `Task` | `src.gpu.api_system.services.resource_scheduler.helpers` | `from src.gpu.api_system.services.resource_scheduler.helpers import Task` |
| `TaskStatus` | same | `from ... import TaskStatus` |
| `TaskType` | same | `from ... import TaskType` |
| `TaskPriority` | same | `from ... import TaskPriority` |
| `MultiLevelCache` | `src.gpu.api_system.utils.cache_optimization` | `from src.gpu.api_system.utils.cache_optimization import MultiLevelCache` |
| `BacktestEngineGPU` | `src.gpu.api_system.utils.gpu_acceleration_engine.backtest_engine_gpu` | `from src.gpu.api_system.utils.gpu_acceleration_engine.backtest_engine_gpu import BacktestEngineGPU` |
| `MLTrainingGPU` | same | `from ... import MLTrainingGPU` |
| `BacktestEngine` | `src.gpu.api_system.services.backtest_service.backtest_engine` | `from src.gpu.api_system.services.backtest_service.backtest_engine import BacktestEngine` |
| `json` | stdlib | `import json` |

#### GPU Scheduler Import Consolidation

For `core.py` (34 errors, all from one module):
```python
from src.gpu.api_system.services.resource_scheduler.helpers import (
    Task, TaskStatus, TaskType, TaskPriority,
)
```

---

## Validation Architecture

### Per-Directory Verification Commands

```bash
# After each directory's changes:
ruff check src/advanced_analysis/ --select F821 --statistics   # Expect: 0 errors
ruff check src/monitoring/ --select F821 --statistics           # Expect: 0 errors
ruff check src/gpu/ --select F821 --statistics                  # Expect: 0 errors

# Global verification (after all directories):
ruff check src/ --select F821 --statistics                       # Expect: ≤131 errors
```

### Diff Constraint

```bash
git diff --stat src/advanced_analysis/ src/monitoring/ src/gpu/
# Must show only import lines and function signature changes — no logic changes
```

---

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| canslim_analyzer.py non-mechanical fix | MEDIUM | Read full file context before fixing; add parameter only |
| SNOWNLP/jieba conditional import | LOW | Follow existing pattern from CONTEXT.md; include jieba.analyse submodule |
| DBSCAN/IsolationForest optional deps | LOW | Use try/except ImportError pattern |
| Duplicate type definitions (monitoring has dataclasses.py AND base_threshold_manager.py both defining ThresholdRule) | LOW | Use dataclasses.py as canonical (it's in the same package) |

---

## RESEARCH COMPLETE
