"""Shared helpers, runtime fallback state, and monitoring accessor."""
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter

from app.core.exceptions import BusinessException

logger = structlog.get_logger(__name__)

# 添加项目根目录到路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.mock.unified_mock_data import get_mock_data_manager
from app.openapi_config import COMMON_RESPONSES
from app.core.config import settings
from app.core.responses import create_unified_success_response
from app.schemas.backtest_schemas import BacktestRequest
from app.api.strategy_management.monitoring_adapter import MonitoringAdapter, MonitoringFallback
from src.core import DataClassification
from src.monitoring.monitoring_database import MonitoringDatabase

# 使用 MyStocksUnifiedManager 作为统一入口点
from unified_manager import MyStocksUnifiedManager

STRATEGY_MANAGEMENT_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

router = APIRouter(
    prefix="/api/v1/strategy",
    tags=["策略管理-Week1"],
    responses=STRATEGY_MANAGEMENT_ROUTE_RESPONSES,
)

from ._responses import (  # noqa: F401
    STRATEGY_UPDATE_EXAMPLES, STRATEGY_CREATE_EXAMPLES,
    MODEL_TRAIN_EXAMPLES, BACKTEST_RUN_EXAMPLES,
    STRATEGY_LIST_RESPONSES, STRATEGY_CREATE_RESPONSES,
    STRATEGY_DETAIL_RESPONSES, STRATEGY_UPDATE_RESPONSES,
    STRATEGY_DELETE_RESPONSES, STRATEGY_START_RESPONSES,
    STRATEGY_PAUSE_RESPONSES, STRATEGY_RESUME_RESPONSES,
    STRATEGY_STOP_RESPONSES, MODEL_TRAIN_RESPONSES,
    MODEL_TRAIN_STATUS_RESPONSES, MODEL_LIST_RESPONSES,
    BACKTEST_RUN_RESPONSES, BACKTEST_LIST_RESPONSES,
    BACKTEST_DETAIL_RESPONSES, BACKTEST_STATUS_RESPONSES,
)

# 延迟初始化监控数据库（避免导入时需要完整环境变量）
monitoring_db = None
_runtime_strategy_store: List[Dict[str, Any]] = []
_runtime_backtest_store: List[Dict[str, Any]] = []


def _is_strategy_management_mock_enabled() -> bool:
    return settings.use_mock_apis


def _get_mock_strategy_list() -> List[Dict[str, Any]]:
    mock_manager = get_mock_data_manager()
    strategies_data = mock_manager.get_data("strategy", action="list")
    return [_normalize_strategy_record(item) for item in strategies_data.get("strategies", [])]


def _runtime_fallback_enabled() -> bool:
    return (
        os.getenv("TESTING", "false").lower() == "true"
        or os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
    )


def _to_isoformat(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _normalize_strategy_record(record: Dict[str, Any]) -> Dict[str, Any]:
    strategy_id = record.get("strategy_id", record.get("id"))
    strategy_name = (
        record.get("strategy_name")
        or record.get("name")
        or record.get("strategy_name_cn")
        or record.get("strategy_name_en")
        or "未命名策略"
    )
    strategy_type = record.get("strategy_type") or record.get("type") or record.get("strategy_code") or "custom"
    status = record.get("status")

    if status is None:
        is_active = record.get("is_active")
        if is_active is True:
            status = "active"
        elif is_active is False:
            status = "draft"
        else:
            status = "draft"

    normalized = {
        "id": strategy_id,
        "strategy_id": strategy_id,
        "strategy_name": strategy_name,
        "strategy_type": strategy_type,
        "description": record.get("description") or "",
        "parameters": record.get("parameters") or {},
        "status": status,
        "created_at": _to_isoformat(record.get("created_at")),
        "updated_at": _to_isoformat(record.get("updated_at")),
    }

    return {**record, **normalized}


def _next_runtime_strategy_id() -> int:
    numeric_ids: List[int] = []
    for strategy in _runtime_strategy_store:
        raw_id = strategy.get("strategy_id", strategy.get("id"))
        if raw_id is None:
            continue
        try:
            numeric_ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue
    return max(numeric_ids, default=900000) + 1


def _build_runtime_strategy_record(strategy_data: Dict[str, Any], strategy_id: Optional[int] = None) -> Dict[str, Any]:
    now = datetime.now()
    created_at = strategy_data.get("created_at", now)
    updated_at = strategy_data.get("updated_at", now)
    resolved_id = strategy_id if strategy_id is not None else _next_runtime_strategy_id()

    return _normalize_strategy_record(
        {
            **strategy_data,
            "id": resolved_id,
            "strategy_id": resolved_id,
            "created_at": created_at,
            "updated_at": updated_at,
            "status": strategy_data.get("status", "draft"),
        }
    )


def _store_runtime_strategy(strategy_record: Dict[str, Any]) -> None:
    strategy_id = str(strategy_record.get("strategy_id", strategy_record.get("id")))

    for index, existing in enumerate(_runtime_strategy_store):
        existing_id = str(existing.get("strategy_id", existing.get("id")))
        if existing_id == strategy_id:
            _runtime_strategy_store[index] = strategy_record
            return

    _runtime_strategy_store.insert(0, strategy_record)


def _find_runtime_strategy(strategy_id: int) -> Optional[Dict[str, Any]]:
    target = str(strategy_id)
    for strategy in _runtime_strategy_store:
        existing_id = str(strategy.get("strategy_id", strategy.get("id")))
        if existing_id == target:
            return strategy
    return None


def _delete_runtime_strategy(strategy_id: int) -> bool:
    target = str(strategy_id)
    for index, strategy in enumerate(_runtime_strategy_store):
        existing_id = str(strategy.get("strategy_id", strategy.get("id")))
        if existing_id == target:
            del _runtime_strategy_store[index]
            return True
    return False


def _set_runtime_strategy_status(strategy_id: int, status: str) -> Optional[Dict[str, Any]]:
    existing = _find_runtime_strategy(strategy_id)
    if existing is None:
        return None

    updated = _build_runtime_strategy_record(
        {
            **existing,
            "id": strategy_id,
            "strategy_id": strategy_id,
            "status": status,
            "updated_at": datetime.now(),
        },
        strategy_id=strategy_id,
    )
    _store_runtime_strategy(updated)
    return updated


def _list_runtime_strategies(
    status: Optional[str], page: int, page_size: int, user_id: Optional[int] = None
) -> Dict[str, Any]:
    strategies = list(_runtime_strategy_store)

    if status:
        strategies = [strategy for strategy in strategies if strategy.get("status") == status]
    if user_id is not None:
        strategies = [
            strategy
            for strategy in strategies
            if strategy.get("user_id") is None or str(strategy.get("user_id")) == str(user_id)
        ]

    total = len(strategies)
    start = (page - 1) * page_size
    end = start + page_size
    items = strategies[start:end]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def _next_runtime_backtest_id() -> int:
    numeric_ids: List[int] = []
    for backtest in _runtime_backtest_store:
        raw_id = backtest.get("id", backtest.get("backtest_id"))
        if raw_id is None:
            continue
        try:
            numeric_ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue
    return max(numeric_ids, default=950000) + 1


def _build_runtime_backtest_record(request: BacktestRequest, config: Dict[str, Any], backtest_id: Optional[int] = None) -> Dict[str, Any]:
    now = datetime.now()
    resolved_id = backtest_id if backtest_id is not None else _next_runtime_backtest_id()
    total_return = 0.182
    annualized_return = 0.156
    max_drawdown = -0.083
    sharpe_ratio = 1.42
    win_rate = 0.61
    total_trades = 28

    return {
        "id": resolved_id,
        "backtest_id": resolved_id,
        "name": f"{request.strategy_name}_Backtest",
        "strategy_id": config.get("strategy_id"),
        "strategy_name": request.strategy_name,
        "symbols": list(request.symbols),
        "start_date": config["start_date"],
        "end_date": config["end_date"],
        "initial_cash": request.initial_capital,
        "initial_capital": request.initial_capital,
        "commission_rate": config.get("commission_rate", 0.0003),
        "stamp_tax_rate": config.get("stamp_tax_rate", 0.001),
        "slippage_rate": config.get("slippage_rate", 0.001),
        "status": "completed",
        "created_at": _to_isoformat(now),
        "started_at": _to_isoformat(now),
        "completed_at": _to_isoformat(now),
        "error_message": None,
        "has_results": True,
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "performance": {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "win_rate": win_rate,
            "total_trades": total_trades,
        },
        "equity_curve": [
            {"date": config["start_date"], "equity": request.initial_capital},
            {"date": config["end_date"], "equity": round(request.initial_capital * (1 + total_return), 2)},
        ],
        "drawdown_curve": [
            {"date": config["start_date"], "drawdown": 0},
            {"date": config["end_date"], "drawdown": max_drawdown},
        ],
        "returns_distribution": [
            {"bucket": "-2%~-1%", "count": 3},
            {"bucket": "0%~1%", "count": 9},
            {"bucket": "1%~2%", "count": 7},
        ],
    }


def _store_runtime_backtest(backtest_record: Dict[str, Any]) -> None:
    target = str(backtest_record.get("id", backtest_record.get("backtest_id")))
    for index, existing in enumerate(_runtime_backtest_store):
        existing_id = str(existing.get("id", existing.get("backtest_id")))
        if existing_id == target:
            _runtime_backtest_store[index] = backtest_record
            return
    _runtime_backtest_store.insert(0, backtest_record)


def _find_runtime_backtest(backtest_id: int) -> Optional[Dict[str, Any]]:
    target = str(backtest_id)
    for backtest in _runtime_backtest_store:
        existing_id = str(backtest.get("id", backtest.get("backtest_id")))
        if existing_id == target:
            return backtest
    return None


def _list_runtime_backtests(strategy_id: Optional[int], page: int, page_size: int) -> Dict[str, Any]:
    records = list(_runtime_backtest_store)
    if strategy_id is not None:
        records = [item for item in records if str(item.get("strategy_id")) == str(strategy_id)]
    total = len(records)
    start = (page - 1) * page_size
    end = start + page_size
    return {"items": records[start:end], "total": total, "page": page, "page_size": page_size}


async def _handle_strategy_lifecycle_action(
    strategy_id: int,
    *,
    status: str,
    action_name: str,
    success_message: str,
) -> Any:
    operation_start = datetime.now()
    source = "database"
    updated_strategy: Optional[Dict[str, Any]] = None

    try:
        try:
            manager = MyStocksUnifiedManager()

            strategies = manager.load_data_by_classification(
                classification=DataClassification.MODEL_OUTPUT,
                table_name="strategies",
                filters={"id": strategy_id},
            )

            if strategies is None or len(strategies) == 0:
                if not _runtime_fallback_enabled():
                    raise BusinessException(detail="策略不存在", status_code=404)

                updated_strategy = _set_runtime_strategy_status(strategy_id, status)
                if updated_strategy is None:
                    raise BusinessException(detail="策略不存在", status_code=404)
                source = "runtime-fallback"
            else:
                strategy_record = strategies.iloc[0].to_dict()
                strategy_record["id"] = strategy_id
                strategy_record["strategy_id"] = strategy_id
                strategy_record["status"] = status
                strategy_record["updated_at"] = datetime.now()

                import pandas as pd

                update_df = pd.DataFrame([strategy_record])
                result = manager.save_data_by_classification(
                    data=update_df,
                    classification=DataClassification.MODEL_OUTPUT,
                    table_name="strategies",
                    upsert=True,
                )

                if not result:
                    if not _runtime_fallback_enabled():
                        raise BusinessException(detail=f"{success_message}失败", status_code=500)

                    updated_strategy = _set_runtime_strategy_status(strategy_id, status)
                    if updated_strategy is None:
                        raise BusinessException(detail=f"{success_message}失败", status_code=500)
                    source = "runtime-fallback"
                else:
                    updated_strategy = _normalize_strategy_record(strategy_record)
        except BusinessException:
            raise
        except Exception as db_error:
            if not _runtime_fallback_enabled():
                raise

            updated_strategy = _set_runtime_strategy_status(strategy_id, status)
            if updated_strategy is None:
                raise BusinessException(detail=f"{success_message}失败: {str(db_error)}", status_code=500)
            source = "runtime-fallback"
            logger.warning("策略生命周期动作降级到 runtime fallback: %(e)s", e=str(db_error))

        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="UPDATE",
            table_name="strategies",
            operation_name=action_name,
            rows_affected=1,
            operation_time_ms=operation_time,
            success=True,
            details=f"strategy_id={strategy_id}, status={status}, source={source}",
        )

        return create_unified_success_response(data=updated_strategy, message=success_message)

    except BusinessException:
        raise
    except Exception as e:
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="UPDATE",
            table_name="strategies",
            operation_name=action_name,
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            error_message=str(e),
        )
        raise BusinessException(detail=f"{success_message}失败: {str(e)}", status_code=500)

def get_monitoring_db():
    """获取监控数据库实例（延迟初始化）"""
    global monitoring_db
    if monitoring_db is None:
        try:
            real_monitoring_db = MonitoringDatabase()

            monitoring_db = MonitoringAdapter(real_monitoring_db)

        except Exception:
            logger.warning("MonitoringDatabase initialization failed, using fallback: %(e)s")

            monitoring_db = MonitoringFallback()
    return monitoring_db
