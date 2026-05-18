"""Backward-compatible re-exports from split sub-modules.

The original 1,583-line file was split during P3 into:
- _helpers.py: shared router, response examples, runtime fallback helpers
- _strategy_crud_router.py: strategy CRUD + lifecycle routes
- _model_backtest_router.py: model training + backtest routes
"""

from ._helpers import get_monitoring_db, router

from ._strategy_crud_router import (
    list_strategies,
    create_strategy,
    get_strategy,
    update_strategy,
    delete_strategy,
    start_strategy,
    pause_strategy,
    resume_strategy,
    stop_strategy,
)

from ._model_backtest_router import (
    train_model,
    get_training_status,
    list_models,
    run_backtest,
    list_backtest_results,
    get_backtest_result,
    get_backtest_status,
)

# Re-export task functions from the task tail module (imported by name in __init__.py)
from ._strategy_management_task_tail import run_backtest_task, train_model_task
