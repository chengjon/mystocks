"""Model training and backtest route handlers.

Extracted from get_monitoring_db.py during the P3 split.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, Body, Path, Query

from app.core.exceptions import BusinessException

from app.core.responses import UnifiedResponse

from app.api.strategy_management._strategy_management_task_tail import run_backtest_task, train_model_task

from ._helpers import (
    MyStocksUnifiedManager,
    DataClassification,
    router,
    _runtime_fallback_enabled,
    _build_runtime_backtest_record,
    _store_runtime_backtest,
    _find_runtime_backtest,
    _list_runtime_backtests,
    BACKTEST_RUN_EXAMPLES,
    MODEL_TRAIN_EXAMPLES,
    MODEL_TRAIN_RESPONSES,
    MODEL_TRAIN_STATUS_RESPONSES,
    MODEL_LIST_RESPONSES,
    BACKTEST_RUN_RESPONSES,
    BACKTEST_LIST_RESPONSES,
    BACKTEST_DETAIL_RESPONSES,
    BACKTEST_STATUS_RESPONSES,
)
from app.schemas.backtest_schemas import BacktestRequest


@router.post(
    "/models/train",
    summary="启动模型训练",
    description="提交模型训练任务并返回任务ID，后续可通过训练状态接口轮询执行进度。",
    response_model=UnifiedResponse[Any],
    responses=MODEL_TRAIN_RESPONSES,
)
async def train_model(
    background_tasks: BackgroundTasks,
    config: Dict[str, Any] = Body(
        ...,
        description="模型训练配置，包含模型名称、模型类型、超参数和训练集配置。",
        openapi_examples=MODEL_TRAIN_EXAMPLES,
    ),
) -> Dict[str, Any]:
    """启动模型训练任务"""
    try:
        manager = MyStocksUnifiedManager()

        import pandas as pd

        model_data = {
            "name": config.get("name"),
            "model_type": config.get("model_type"),
            "hyperparameters": config.get("hyperparameters"),
            "training_config": config.get("training_config"),
            "status": "training",
            "training_started_at": datetime.now(),
            "created_at": datetime.now(),
        }

        model_df = pd.DataFrame([model_data])
        result = manager.save_data_by_classification(
            data=model_df,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="models",
        )

        if not result:
            raise BusinessException(detail="创建模型记录失败", status_code=500)

        models = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="models",
            filters={"name": config.get("name")},
        )
        model_id = models.iloc[-1]["id"] if models is not None and len(models) > 0 else 1

        task_id = f"train_{model_id}_{int(datetime.now().timestamp())}"
        background_tasks.add_task(train_model_task, model_id=model_id, config=config)

        return {"task_id": task_id, "model_id": model_id}

    except Exception as e:
        raise BusinessException(detail=f"启动模型训练失败: {str(e)}", status_code=500)


@router.get(
    "/models/training/{task_id}/status",
    summary="查询模型训练状态",
    description="查询指定模型训练任务的当前状态、进度和已产出的性能指标。",
    response_model=UnifiedResponse[Any],
    responses=MODEL_TRAIN_STATUS_RESPONSES,
)
async def get_training_status(task_id: str = Path(..., description="需要查询状态的训练任务ID。")) -> Dict[str, Any]:
    """查询训练状态"""
    try:
        model_id = int(task_id.split("_")[1])

        manager = MyStocksUnifiedManager()
        models = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="models",
            filters={"id": model_id},
        )

        if models is None or len(models) == 0:
            raise BusinessException(detail="模型不存在", status_code=404)

        model = models.iloc[0].to_dict()

        status = model.get("status")
        progress = 100 if status == "completed" else 0
        if status == "training":
            elapsed = (datetime.now() - model["training_started_at"]).seconds
            progress = min(95, int(elapsed / 60 * 20))

        return {
            "status": status,
            "progress": progress,
            "metrics": model.get("performance_metrics") or {},
        }

    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(detail=f"获取训练状态失败: {str(e)}", status_code=500)


@router.get(
    "/models",
    summary="获取模型列表",
    description="查询模型注册表，可按模型类型或训练状态筛选，便于训练资产管理和上线评估。",
    response_model=UnifiedResponse[Any],
    responses=MODEL_LIST_RESPONSES,
)
async def list_models(
    model_type: Optional[str] = Query(None, description="可选的模型类型过滤条件，如 lstm、xgboost。"),
    status: Optional[str] = Query(None, description="可选的模型状态过滤条件，如 training、completed、failed。"),
) -> List[Dict[str, Any]]:
    """获取模型列表"""
    try:
        manager = MyStocksUnifiedManager()

        filters = {}
        if model_type:
            filters["model_type"] = model_type
        if status:
            filters["status"] = status

        models = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="models",
            filters=filters,
        )

        return models.to_dict("records") if models is not None else []

    except Exception as e:
        raise BusinessException(detail=f"获取模型列表失败: {str(e)}", status_code=500)


@router.post(
    "/backtest/run",
    summary="执行回测",
    description="提交回测任务并异步执行，适用于策略联调、股指期货策略验证和结果追踪场景。",
    response_model=UnifiedResponse[Any],
    responses=BACKTEST_RUN_RESPONSES,
)
async def run_backtest(
    background_tasks: BackgroundTasks,
    request: BacktestRequest = Body(..., openapi_examples=BACKTEST_RUN_EXAMPLES),
) -> Dict[str, int]:
    """执行回测"""
    import pandas as pd

    config = request.parameters.copy()
    config["symbols"] = request.symbols
    config["start_date"] = (
        request.start_date.isoformat() if hasattr(request.start_date, "isoformat") else str(request.start_date)
    )
    config["end_date"] = (
        request.end_date.isoformat() if hasattr(request.end_date, "isoformat") else str(request.end_date)
    )
    config["initial_cash"] = request.initial_capital
    config["strategy_type"] = request.strategy_name

    try:
        manager = MyStocksUnifiedManager()

        backtest_data = {
            "name": f"{request.strategy_name}_Backtest",
            "strategy_id": config.get("strategy_id"),
            "start_date": config["start_date"],
            "end_date": config["end_date"],
            "initial_cash": request.initial_capital,
            "commission_rate": config.get("commission_rate", 0.0003),
            "stamp_tax_rate": config.get("stamp_tax_rate", 0.001),
            "slippage_rate": config.get("slippage_rate", 0.001),
            "status": "pending",
            "created_at": datetime.now(),
        }

        backtest_df = pd.DataFrame([backtest_data])
        result = manager.save_data_by_classification(
            data=backtest_df,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="backtests",
        )

        if not result:
            if _runtime_fallback_enabled():
                fallback_record = _build_runtime_backtest_record(request, config)
                _store_runtime_backtest(fallback_record)
                return {"backtest_id": int(fallback_record["id"])}
            raise BusinessException(detail="创建回测记录失败", status_code=500)

        backtests = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="backtests",
            filters={"name": backtest_data["name"]},
        )
        backtest_id = backtests.iloc[-1]["id"] if backtests is not None and len(backtests) > 0 else 1

        background_tasks.add_task(run_backtest_task, backtest_id=backtest_id, config=config)

        return {"backtest_id": backtest_id}

    except Exception as e:
        if _runtime_fallback_enabled():
            fallback_record = _build_runtime_backtest_record(request, config)
            _store_runtime_backtest(fallback_record)
            return {"backtest_id": int(fallback_record["id"])}
        raise BusinessException(detail=f"启动回测失败: {str(e)}", status_code=500)


@router.get(
    "/backtest/results",
    summary="获取回测结果列表",
    description="分页查询回测结果列表，可按策略ID过滤并控制返回页码与每页条数。",
    response_model=UnifiedResponse[Any],
    responses=BACKTEST_LIST_RESPONSES,
)
async def list_backtest_results(
    strategy_id: Optional[int] = Query(None, description="按策略ID筛选回测结果。"),
    page: int = Query(1, description="结果分页页码，从 1 开始。"),
    page_size: int = Query(20, description="每页返回的回测结果数量。"),
) -> Dict[str, Any]:
    """获取回测结果列表"""
    try:
        manager = MyStocksUnifiedManager()

        filters = {}
        if strategy_id:
            filters["strategy_id"] = strategy_id

        backtests = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="backtests",
            filters=filters,
        )

        total = len(backtests) if backtests is not None else 0
        start = (page - 1) * page_size
        end = start + page_size
        items = backtests.iloc[start:end].to_dict("records") if backtests is not None else []

        if total == 0 and _runtime_fallback_enabled():
            from ._helpers import _runtime_backtest_store

            if _runtime_backtest_store:
                return _list_runtime_backtests(strategy_id=strategy_id, page=page, page_size=page_size)

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    except Exception as e:
        if _runtime_fallback_enabled():
            return _list_runtime_backtests(strategy_id=strategy_id, page=page, page_size=page_size)
        raise BusinessException(detail=f"获取回测结果失败: {str(e)}", status_code=500)


@router.get(
    "/backtest/results/{backtest_id}",
    summary="获取回测详细结果",
    description="按回测 ID 返回单次回测的详细结果记录，便于查看绩效数据、参数快照和运行状态。",
    response_model=UnifiedResponse[Any],
    responses=BACKTEST_DETAIL_RESPONSES,
)
async def get_backtest_result(backtest_id: int = Path(..., description="回测ID", ge=1)) -> Dict[str, Any]:
    """获取回测详细结果"""
    try:
        manager = MyStocksUnifiedManager()

        backtests = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="backtests",
            filters={"id": backtest_id},
        )

        if backtests is None or len(backtests) == 0:
            fallback_record = _find_runtime_backtest(backtest_id) if _runtime_fallback_enabled() else None
            if fallback_record is not None:
                return fallback_record
            raise BusinessException(detail="回测不存在", status_code=404)

        return backtests.iloc[0].to_dict()

    except BusinessException:
        raise
    except Exception as e:
        fallback_record = _find_runtime_backtest(backtest_id) if _runtime_fallback_enabled() else None
        if fallback_record is not None:
            return fallback_record
        raise BusinessException(detail=f"获取回测结果失败: {str(e)}", status_code=500)


@router.get(
    "/backtest/status/{backtest_id}",
    summary="获取回测任务状态",
    description="按回测 ID 查询后台回测任务的当前状态，用于轮询进度、判断是否完成以及是否可读取结果。",
    response_model=UnifiedResponse[Any],
    responses=BACKTEST_STATUS_RESPONSES,
)
async def get_backtest_status(backtest_id: int = Path(..., description="回测ID", ge=1)) -> Dict[str, Any]:
    """获取回测任务状态"""
    fallback_record = _find_runtime_backtest(backtest_id) if _runtime_fallback_enabled() else None
    if fallback_record is not None:
        return {
            "backtest_id": backtest_id,
            "status": fallback_record.get("status", "completed"),
            "created_at": fallback_record.get("created_at"),
            "started_at": fallback_record.get("started_at"),
            "completed_at": fallback_record.get("completed_at"),
            "error_message": fallback_record.get("error_message"),
            "has_results": fallback_record.get("has_results", True),
        }

    raise BusinessException(detail=f"回测不存在: backtest_id={backtest_id}", status_code=404)
