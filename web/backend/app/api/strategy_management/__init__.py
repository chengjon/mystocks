"""strategy_management 拆分包"""
from fastapi import APIRouter

from .get_monitoring_db import router as management_router
from ._strategy_execution_router import router as execution_router
from ._chart_data_router import router as chart_data_router

from .get_monitoring_db import get_monitoring_db  # noqa: F401
from .get_monitoring_db import list_strategies  # noqa: F401
from .get_monitoring_db import create_strategy  # noqa: F401
from .get_monitoring_db import get_strategy  # noqa: F401
from .get_monitoring_db import update_strategy  # noqa: F401
from .get_monitoring_db import delete_strategy  # noqa: F401
from .get_monitoring_db import train_model  # noqa: F401
from .get_monitoring_db import train_model_task  # noqa: F401
from .get_monitoring_db import get_training_status  # noqa: F401
from .get_monitoring_db import list_models  # noqa: F401
from .get_monitoring_db import run_backtest  # noqa: F401
from .get_monitoring_db import run_backtest_task  # noqa: F401
from .get_monitoring_db import get_backtest_status  # noqa: F401
from .get_monitoring_db import list_backtest_results  # noqa: F401
from .get_monitoring_db import get_backtest_result  # noqa: F401
from ._chart_data_router import get_backtest_chart_data  # noqa: F401

router = APIRouter(tags=["strategy"])
router.include_router(management_router)
router.include_router(execution_router, prefix="/api/v1/strategy")
router.include_router(chart_data_router, prefix="/api/v1/strategy")

__all__ = ['get_monitoring_db', 'list_strategies', 'create_strategy', 'get_strategy', 'update_strategy', 'delete_strategy', 'train_model', 'train_model_task', 'get_training_status', 'list_models', 'run_backtest', 'run_backtest_task', 'get_backtest_status', 'list_backtest_results', 'get_backtest_result', 'get_backtest_chart_data', 'router']
