"""strategy_management 拆分包"""
from fastapi import APIRouter

from ._helpers import router as management_router
from ._strategy_execution_router import router as execution_router
from ._chart_data_router import router as chart_data_router

from ._helpers import get_monitoring_db  # noqa: F401
from ._strategy_crud_router import (
    list_strategies,  # noqa: F401
    create_strategy,  # noqa: F401
    get_strategy,  # noqa: F401
    update_strategy,  # noqa: F401
    delete_strategy,  # noqa: F401
    start_strategy,  # noqa: F401
    pause_strategy,  # noqa: F401
    resume_strategy,  # noqa: F401
    stop_strategy,  # noqa: F401
)
from ._model_backtest_router import (
    train_model,  # noqa: F401
    get_training_status,  # noqa: F401
    list_models,  # noqa: F401
    run_backtest,  # noqa: F401
    list_backtest_results,  # noqa: F401
    get_backtest_result,  # noqa: F401
    get_backtest_status,  # noqa: F401
)
from ._chart_data_router import get_backtest_chart_data  # noqa: F401
from ._strategy_management_task_tail import run_backtest_task, train_model_task  # noqa: F401

router = APIRouter(tags=["strategy"])
router.include_router(management_router)
router.include_router(execution_router, prefix="/api/v1/strategy")
router.include_router(chart_data_router, prefix="/api/v1/strategy")

__all__ = [
    'get_monitoring_db', 'list_strategies', 'create_strategy', 'get_strategy',
    'update_strategy', 'delete_strategy', 'start_strategy', 'pause_strategy',
    'resume_strategy', 'stop_strategy', 'train_model', 'train_model_task',
    'get_training_status', 'list_models', 'run_backtest', 'run_backtest_task',
    'get_backtest_status', 'list_backtest_results', 'get_backtest_result',
    'get_backtest_chart_data', 'router',
]
