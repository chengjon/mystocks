---
plan: 01
wave: 1
phase: 9
depends_on: []
autonomous: true
files_modified:
  - src/advanced_analysis/models/decision_synthesis.py
  - src/advanced_analysis/chip_distribution_analyzer/_chip_concentration_tail.py
  - src/advanced_analysis/anomaly/detection.py
  - src/advanced_analysis/anomaly/analysis_signals.py
  - src/advanced_analysis/sentiment_analyzer/_sentiment_score_mixin.py
  - src/advanced_analysis/sentiment_analyzer/_generate_sentiment_signals.py
  - src/advanced_analysis/sentiment_analyzer/_sentiment_score_tail.py
  - src/advanced_analysis/decision_models/models/canslim_analyzer.py
  - src/advanced_analysis/decision_models_analyzer.py
  - src/advanced_analysis/trading_signals_analyzer/_assess_signal_risk.py
requirements:
  - LINT-06
must_haves:
  - ruff check src/advanced_analysis/ --select F821 reports 0 errors
  - No logic changes — only import lines and function signature changes
---

# Plan 01: Resolve F821 Errors in src/advanced_analysis/

**Objective:** Fix all 91 F821 (undefined-name) errors across 10 files in `src/advanced_analysis/` by adding missing imports and one function signature fix.

## Task 1: Fix decision_synthesis.py (34 errors)

<read_first>
- src/advanced_analysis/models/decision_synthesis.py
- src/advanced_analysis/models/dataclasses.py (canonical source for BuffettModelScore, CANSLIMModelScore, FisherModelScore)
- src/advanced_analysis/__init__.py (canonical source for AnalysisResult, AnalysisType)
</read_first>

<action>
Add the following imports at the top of `src/advanced_analysis/models/decision_synthesis.py`, in the correct import order group:

1. Stdlib: `from datetime import datetime`
2. Third-party: `import pandas as pd`
3. Typing: `from typing import Optional`
4. Local types:
   - `from src.advanced_analysis.models.dataclasses import BuffettModelScore, CANSLIMModelScore, FisherModelScore`
   - `from src.advanced_analysis import AnalysisResult, AnalysisType`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/advanced_analysis/models/decision_synthesis.py` contains `import pandas as pd`
- `src/advanced_analysis/models/decision_synthesis.py` contains `from datetime import datetime`
- `src/advanced_analysis/models/decision_synthesis.py` contains `from typing import Optional`
- `src/advanced_analysis/models/decision_synthesis.py` contains `from src.advanced_analysis.models.dataclasses import BuffettModelScore, CANSLIMModelScore, FisherModelScore`
- `src/advanced_analysis/models/decision_synthesis.py` contains `from src.advanced_analysis import AnalysisResult, AnalysisType`
- `ruff check src/advanced_analysis/models/decision_synthesis.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 2: Fix _chip_concentration_tail.py (13 errors)

<read_first>
- src/advanced_analysis/chip_distribution_analyzer/_chip_concentration_tail.py
</read_first>

<action>
Add the following imports at the top of `src/advanced_analysis/chip_distribution_analyzer/_chip_concentration_tail.py`:

1. Third-party: `import pandas as pd`
2. Typing: `from typing import Optional, Tuple`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/advanced_analysis/chip_distribution_analyzer/_chip_concentration_tail.py` contains `import pandas as pd`
- `src/advanced_analysis/chip_distribution_analyzer/_chip_concentration_tail.py` contains `from typing import Optional, Tuple`
- `ruff check src/advanced_analysis/chip_distribution_analyzer/_chip_concentration_tail.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 3: Fix anomaly/detection.py (9 errors)

<read_first>
- src/advanced_analysis/anomaly/detection.py
- src/advanced_analysis/__init__.py (canonical source for BaseAnalyzer, AnalysisResult, AnalysisType)
- src/advanced_analysis/anomaly/dataclasses.py (canonical source for AnomalyAlert, GPU_AVAILABLE, IsolationForest)
</read_first>

<action>
Add the following imports at the top of `src/advanced_analysis/anomaly/detection.py`:

1. Local types:
   - `from src.advanced_analysis import BaseAnalyzer, AnalysisResult, AnalysisType`
   - `from src.advanced_analysis.anomaly.dataclasses import AnomalyAlert, GPU_AVAILABLE, IsolationForest`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/advanced_analysis/anomaly/detection.py` contains `from src.advanced_analysis import BaseAnalyzer, AnalysisResult, AnalysisType`
- `src/advanced_analysis/anomaly/detection.py` contains `from src.advanced_analysis.anomaly.dataclasses import AnomalyAlert, GPU_AVAILABLE, IsolationForest`
- `ruff check src/advanced_analysis/anomaly/detection.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 4: Fix anomaly/analysis_signals.py (7 errors)

<read_first>
- src/advanced_analysis/anomaly/analysis_signals.py
- src/advanced_analysis/__init__.py (canonical source for AnalysisResult, AnalysisType)
- src/advanced_analysis/anomaly/dataclasses.py (canonical source for AnomalyCluster)
</read_first>

<action>
Add the following imports at the top of `src/advanced_analysis/anomaly/analysis_signals.py`:

1. Local types:
   - `from src.advanced_analysis import AnalysisResult, AnalysisType`
   - `from src.advanced_analysis.anomaly.dataclasses import AnomalyCluster`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/advanced_analysis/anomaly/analysis_signals.py` contains `from src.advanced_analysis import AnalysisResult, AnalysisType`
- `src/advanced_analysis/anomaly/analysis_signals.py` contains `from src.advanced_analysis.anomaly.dataclasses import AnomalyCluster`
- `ruff check src/advanced_analysis/anomaly/analysis_signals.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 5: Fix _sentiment_score_mixin.py (8 errors — SNOWNLP/jieba conditional import)

<read_first>
- src/advanced_analysis/sentiment_analyzer/_sentiment_score_mixin.py
- src/advanced_analysis/anomaly/dataclasses.py (reference for try/except ImportError pattern)
</read_first>

<action>
Add a module-level conditional import block at the top of `src/advanced_analysis/sentiment_analyzer/_sentiment_score_mixin.py`, after the existing imports:

```python
try:
    from snownlp import SnowNLP
    import jieba
    import jieba.analyse
    SNOWNLP_AVAILABLE = True
except ImportError:
    SNOWNLP_AVAILABLE = False
```

IMPORTANT: `import jieba.analyse` is mandatory — `jieba.analyse.extract_tags()` at line 532 requires the submodule imported explicitly. Bare `import jieba` does NOT expose `.analyse` at runtime.

Do NOT modify any code beyond adding this import block.
</action>

<acceptance_criteria>
- `src/advanced_analysis/sentiment_analyzer/_sentiment_score_mixin.py` contains `from snownlp import SnowNLP`
- `src/advanced_analysis/sentiment_analyzer/_sentiment_score_mixin.py` contains `import jieba`
- `src/advanced_analysis/sentiment_analyzer/_sentiment_score_mixin.py` contains `import jieba.analyse`
- `src/advanced_analysis/sentiment_analyzer/_sentiment_score_mixin.py` contains `SNOWNLP_AVAILABLE = True`
- `src/advanced_analysis/sentiment_analyzer/_sentiment_score_mixin.py` contains `SNOWNLP_AVAILABLE = False`
- `ruff check src/advanced_analysis/sentiment_analyzer/_sentiment_score_mixin.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 6: Fix _generate_sentiment_signals.py (6 errors)

<read_first>
- src/advanced_analysis/sentiment_analyzer/_generate_sentiment_signals.py
- src/advanced_analysis/sentiment_analyzer/sentiment_models.py (canonical source for SentimentScore, SentimentAlert, MarketSentimentImpact)
</read_first>

<action>
Add the following import at the top of `src/advanced_analysis/sentiment_analyzer/_generate_sentiment_signals.py`:

1. Local types: `from src.advanced_analysis.sentiment_analyzer.sentiment_models import SentimentScore, SentimentAlert, MarketSentimentImpact`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/advanced_analysis/sentiment_analyzer/_generate_sentiment_signals.py` contains `from src.advanced_analysis.sentiment_analyzer.sentiment_models import SentimentScore, SentimentAlert, MarketSentimentImpact`
- `ruff check src/advanced_analysis/sentiment_analyzer/_generate_sentiment_signals.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 7: Fix _sentiment_score_tail.py (1 error)

<read_first>
- src/advanced_analysis/sentiment_analyzer/_sentiment_score_tail.py
</read_first>

<action>
Add the following import at the top of `src/advanced_analysis/sentiment_analyzer/_sentiment_score_tail.py`:

1. Typing: `from typing import List`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/advanced_analysis/sentiment_analyzer/_sentiment_score_tail.py` contains `from typing import List`
- `ruff check src/advanced_analysis/sentiment_analyzer/_sentiment_score_tail.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 8: Fix canslim_analyzer.py (7 errors — NON-MECHANICAL)

<read_first>
- src/advanced_analysis/decision_models/models/canslim_analyzer.py
  - READ THE FULL FILE — understand where `stock_data` is defined and where it's used
  - The method `get_canslim_score(self, score)` at approximately line 144 uses `stock_data` at lines 160-166
  - `stock_data` is NOT a parameter of this method — it must be added as a parameter
</read_first>

<action>
In `src/advanced_analysis/decision_models/models/canslim_analyzer.py`, find the method `get_canslim_score` that takes `self` and `score` parameters. Add `stock_data: dict` as an additional parameter:

Change the method signature from:
```python
def get_canslim_score(self, score):
```
To:
```python
def get_canslim_score(self, score, stock_data: dict):
```

IMPORTANT: This is the ONLY change — add the parameter. Do NOT refactor to store as instance attribute. Do NOT change any logic. Do NOT change any callers (caller fixes are out of scope for F821 resolution).
</action>

<acceptance_criteria>
- `src/advanced_analysis/decision_models/models/canslim_analyzer.py` contains `def get_canslim_score(self, score, stock_data: dict):`
- `ruff check src/advanced_analysis/decision_models/models/canslim_analyzer.py --select F821` reports 0 errors
- `git diff src/advanced_analysis/decision_models/models/canslim_analyzer.py` shows ONLY the method signature change (one line modified)
</acceptance_criteria>

## Task 9: Fix decision_models_analyzer.py (4 errors)

<read_first>
- src/advanced_analysis/decision_models_analyzer.py
- src/advanced_analysis/__init__.py (canonical source for BaseAnalyzer, AnalysisResult, AnalysisType)
</read_first>

<action>
Add the following import at the top of `src/advanced_analysis/decision_models_analyzer.py`:

1. Local types: `from src.advanced_analysis import BaseAnalyzer, AnalysisResult, AnalysisType`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/advanced_analysis/decision_models_analyzer.py` contains `from src.advanced_analysis import BaseAnalyzer, AnalysisResult, AnalysisType`
- `ruff check src/advanced_analysis/decision_models_analyzer.py --select F821` reports 0 errors
</acceptance_criteria>

## Task 10: Fix _assess_signal_risk.py (2 errors)

<read_first>
- src/advanced_analysis/trading_signals_analyzer/_assess_signal_risk.py
- src/advanced_analysis/trading_signals_analyzer/trading_signal_models.py (canonical source for TradingSignal)
</read_first>

<action>
Add the following import at the top of `src/advanced_analysis/trading_signals_analyzer/_assess_signal_risk.py`:

1. Local types: `from src.advanced_analysis.trading_signals_analyzer.trading_signal_models import TradingSignal`

Do NOT modify any code beyond import statements.
</action>

<acceptance_criteria>
- `src/advanced_analysis/trading_signals_analyzer/_assess_signal_risk.py` contains `from src.advanced_analysis.trading_signals_analyzer.trading_signal_models import TradingSignal`
- `ruff check src/advanced_analysis/trading_signals_analyzer/_assess_signal_risk.py --select F821` reports 0 errors
</acceptance_criteria>

## Verification

```bash
ruff check src/advanced_analysis/ --select F821 --statistics
# MUST report: 0 errors
```
