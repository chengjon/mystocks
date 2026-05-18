"""Strategy CRUD and lifecycle route handlers.

Extracted from get_monitoring_db.py during the P3 split.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import Body, Path, Query

from app.core.exceptions import BusinessException

from app.core.responses import UnifiedResponse

from ._helpers import (
    MyStocksUnifiedManager,
    DataClassification,
    logger,
    router,
    get_monitoring_db,
    create_unified_success_response,
    _is_strategy_management_mock_enabled,
    _get_mock_strategy_list,
    _runtime_fallback_enabled,
    _normalize_strategy_record,
    _build_runtime_strategy_record,
    _store_runtime_strategy,
    _find_runtime_strategy,
    _delete_runtime_strategy,
    _handle_strategy_lifecycle_action,
    STRATEGY_CREATE_EXAMPLES,
    STRATEGY_UPDATE_EXAMPLES,
    STRATEGY_LIST_RESPONSES,
    STRATEGY_CREATE_RESPONSES,
    STRATEGY_DETAIL_RESPONSES,
    STRATEGY_UPDATE_RESPONSES,
    STRATEGY_DELETE_RESPONSES,
    STRATEGY_START_RESPONSES,
    STRATEGY_PAUSE_RESPONSES,
    STRATEGY_RESUME_RESPONSES,
    STRATEGY_STOP_RESPONSES,
)


@router.get(
    "/strategies",
    summary="获取策略列表",
    description="分页查询策略配置列表，可按状态筛选，用于策略管理台展示和运维巡检。",
    response_model=UnifiedResponse[Any],
    responses=STRATEGY_LIST_RESPONSES,
)
async def list_strategies(
    status: Optional[str] = Query(None, description="可选的策略状态过滤条件，如 draft、active、archived。"),
    page: int = Query(1, description="结果页码，从 1 开始。", ge=1),
    page_size: int = Query(20, description="每页返回的策略数量。", ge=1, le=200),
) -> Any:
    """
    获取策略列表

    Args:
        status: 过滤状态 ('draft', 'active', 'archived')
        page: 页码
        page_size: 每页数量

    Returns:
        {
            "items": [...],
            "total": 100,
            "page": 1,
            "page_size": 20
        }

    支持Mock数据模式切换
    """
    operation_start = datetime.now()
    source = "database"

    try:
        if _is_strategy_management_mock_enabled():
            try:
                strategies = _get_mock_strategy_list()

                if status:
                    strategies = [s for s in strategies if s.get("status") == status]

                total = len(strategies)
                start = (page - 1) * page_size
                end = start + page_size
                items = strategies[start:end]
                source = "mock"

                return create_unified_success_response(
                    data={"items": items, "total": total, "page": page, "page_size": page_size},
                    message="获取策略列表成功",
                )
            except Exception as mock_error:
                # 避免递归重入：Mock 失败后直接降级到真实数据库路径
                logger.warning("Mock数据获取失败，降级到真实数据库: %(e)s", e=str(mock_error))

        filters = {}
        if status:
            filters["status"] = status

        try:
            manager = MyStocksUnifiedManager()
            strategies_df = manager.load_data_by_classification(
                classification=DataClassification.MODEL_OUTPUT,
                table_name="strategies",
                filters=filters,
            )

            total = len(strategies_df) if strategies_df is not None else 0
            start = (page - 1) * page_size
            end = start + page_size

            if strategies_df is not None and len(strategies_df) > 0:
                paginated_df = strategies_df.iloc[start:end]
                items = [_normalize_strategy_record(item) for item in paginated_df.to_dict("records")]
            else:
                items = []
                total = 0

        except Exception as db_error:
            logger.error("数据库查询失败: %(e)s", e=str(db_error))
            if _runtime_fallback_enabled():
                from ._helpers import _list_runtime_strategies

                fallback_result = _list_runtime_strategies(status=status, page=page, page_size=page_size)
                items = fallback_result["items"]
                total = fallback_result["total"]
                source = "runtime-fallback"
            else:
                items = []
                total = 0

        if total == 0 and _runtime_fallback_enabled():
            from ._helpers import _list_runtime_strategies, _runtime_strategy_store

            if _runtime_strategy_store:
                fallback_result = _list_runtime_strategies(status=status, page=page, page_size=page_size)
                items = fallback_result["items"]
                total = fallback_result["total"]
                source = "runtime-fallback"

        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="SELECT",
            table_name="strategies",
            operation_name="list_strategies",
            rows_affected=len(items),
            operation_time_ms=operation_time,
            success=True,
            details=f"status={status}, page={page}, page_size={page_size}, source={source}",
        )

        return create_unified_success_response(
            data={"items": items, "total": total, "page": page, "page_size": page_size},
            message="获取策略列表成功",
        )

    except Exception as e:
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="SELECT",
            table_name="strategies",
            operation_name="list_strategies",
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            details=str(e),
        )
        raise BusinessException(detail=f"获取策略列表失败: {str(e)}", status_code=500)


@router.post(
    "/strategies",
    summary="创建策略",
    description="创建新的策略配置记录，支持在数据库不可用时降级写入运行时存储。",
    response_model=UnifiedResponse[Any],
    responses=STRATEGY_CREATE_RESPONSES,
)
async def create_strategy(
    strategy_data: Dict[str, Any] = Body(
        ...,
        description="待创建的策略配置对象，包含名称、策略类型、参数与初始状态。",
        openapi_examples=STRATEGY_CREATE_EXAMPLES,
    ),
) -> Any:
    """创建新策略"""
    operation_start = datetime.now()
    strategy_record: Optional[Dict[str, Any]] = None
    source = "database"

    try:
        if _is_strategy_management_mock_enabled():
            strategy_record = _build_runtime_strategy_record(
                {
                    **strategy_data,
                    "name": strategy_data.get("name", "Mock策略"),
                    "description": strategy_data.get("description", "Mock策略描述"),
                    "strategy_type": strategy_data.get("strategy_type", "technical"),
                    "parameters": strategy_data.get("parameters", {}),
                    "status": strategy_data.get("status", "draft"),
                    "is_mock": True,
                }
            )
            source = "mock"
            if _runtime_fallback_enabled():
                _store_runtime_strategy(strategy_record)
            return create_unified_success_response(data=strategy_record, message="策略创建成功")

        storage_record = dict(strategy_data)
        storage_record["created_at"] = datetime.now()
        storage_record["updated_at"] = datetime.now()
        storage_record["status"] = storage_record.get("status", "draft")
        strategy_record = _build_runtime_strategy_record(storage_record)

        import pandas as pd

        strategy_df = pd.DataFrame([storage_record])

        try:
            manager = MyStocksUnifiedManager()
            result = manager.save_data_by_classification(
                data=strategy_df,
                classification=DataClassification.MODEL_OUTPUT,
                table_name="strategies",
            )
        except Exception as db_error:
            if not _runtime_fallback_enabled():
                raise
            _store_runtime_strategy(strategy_record)
            result = True
            source = "runtime-fallback"
            logger.warning("策略创建降级到 runtime fallback: %(e)s", e=str(db_error))

        if not result and _runtime_fallback_enabled():
            _store_runtime_strategy(strategy_record)
            result = True
            source = "runtime-fallback"

        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="INSERT",
            table_name="strategies",
            operation_name="create_strategy",
            rows_affected=1 if result else 0,
            operation_time_ms=operation_time,
            success=result,
            details=f"strategy_type={strategy_data.get('strategy_type')}, source={source}",
        )

        if result:
            return create_unified_success_response(data=strategy_record, message="策略创建成功")
        else:
            raise BusinessException(detail="策略创建失败", status_code=500)

    except Exception as e:
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="INSERT",
            table_name="strategies",
            operation_name="create_strategy",
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            error_message=str(e),
        )
        raise BusinessException(detail=f"创建策略失败: {str(e)}", status_code=500)


@router.get(
    "/strategies/{strategy_id}",
    summary="获取策略详情",
    description="根据策略ID获取单个策略的完整配置和当前状态信息。",
    response_model=UnifiedResponse[Any],
    responses=STRATEGY_DETAIL_RESPONSES,
)
async def get_strategy(strategy_id: int = Path(..., description="需要查询详情的策略ID。")) -> Any:
    """获取策略详情"""
    try:
        manager = MyStocksUnifiedManager()

        strategies = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="strategies",
            filters={"id": strategy_id},
        )

        if strategies is None or len(strategies) == 0:
            fallback_strategy = _find_runtime_strategy(strategy_id) if _runtime_fallback_enabled() else None
            if fallback_strategy is not None:
                return create_unified_success_response(data=fallback_strategy, message="获取策略成功")
            raise BusinessException(detail="策略不存在", status_code=404)

        return create_unified_success_response(
            data=_normalize_strategy_record(strategies.iloc[0].to_dict()),
            message="获取策略成功",
        )

    except BusinessException:
        raise
    except Exception as e:
        fallback_strategy = _find_runtime_strategy(strategy_id) if _runtime_fallback_enabled() else None
        if fallback_strategy is not None:
            return create_unified_success_response(data=fallback_strategy, message="获取策略成功")
        raise BusinessException(detail=f"获取策略失败: {str(e)}", status_code=500)


@router.put(
    "/strategies/{strategy_id}",
    summary="更新策略",
    description="更新指定策略的配置内容、运行状态和执行参数。",
    response_model=UnifiedResponse[Any],
    responses=STRATEGY_UPDATE_RESPONSES,
)
async def update_strategy(
    strategy_id: int = Path(..., description="需要更新的策略ID。"),
    strategy_update: Dict[str, Any] = Body(..., openapi_examples=STRATEGY_UPDATE_EXAMPLES),
) -> Any:
    """更新指定策略配置。"""
    try:
        try:
            manager = MyStocksUnifiedManager()

            strategies = manager.load_data_by_classification(
                classification=DataClassification.MODEL_OUTPUT,
                table_name="strategies",
                filters={"id": strategy_id},
            )

            if strategies is None or len(strategies) == 0:
                runtime_strategy = _find_runtime_strategy(strategy_id) if _runtime_fallback_enabled() else None
                if runtime_strategy is None:
                    raise BusinessException(detail="策略不存在", status_code=404)
                updated_strategy = _build_runtime_strategy_record(
                    {
                        **runtime_strategy,
                        **strategy_update,
                        "id": strategy_id,
                        "strategy_id": strategy_id,
                        "updated_at": datetime.now(),
                    },
                    strategy_id=strategy_id,
                )
                _store_runtime_strategy(updated_strategy)
                return create_unified_success_response(data=updated_strategy, message="策略更新成功")

            strategy_update["updated_at"] = datetime.now()
            strategy_update["id"] = strategy_id

            import pandas as pd

            updated_df = pd.DataFrame([strategy_update])
            result = manager.save_data_by_classification(
                data=updated_df,
                classification=DataClassification.MODEL_OUTPUT,
                table_name="strategies",
                upsert=True,
            )
        except Exception as db_error:
            if not _runtime_fallback_enabled():
                raise
            runtime_strategy = _find_runtime_strategy(strategy_id)
            if runtime_strategy is None:
                raise BusinessException(detail=f"更新策略失败: {str(db_error)}", status_code=500)
            updated_strategy = _build_runtime_strategy_record(
                {**runtime_strategy, **strategy_update, "strategy_id": strategy_id, "id": strategy_id},
                strategy_id=strategy_id,
            )
            _store_runtime_strategy(updated_strategy)
            return create_unified_success_response(data=updated_strategy, message="策略更新成功")

        if not result and _runtime_fallback_enabled():
            runtime_strategy = _find_runtime_strategy(strategy_id)
            if runtime_strategy is None:
                raise BusinessException(detail="策略更新失败", status_code=500)
            updated_strategy = _build_runtime_strategy_record(
                {**runtime_strategy, **strategy_update, "strategy_id": strategy_id, "id": strategy_id},
                strategy_id=strategy_id,
            )
            _store_runtime_strategy(updated_strategy)
            return create_unified_success_response(data=updated_strategy, message="策略更新成功")

        if result:
            return create_unified_success_response(message="策略更新成功")
        else:
            raise BusinessException(detail="策略更新失败", status_code=500)

    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(detail=f"更新策略失败: {str(e)}", status_code=500)


@router.delete(
    "/strategies/{strategy_id}",
    summary="归档策略",
    description="将指定策略归档下线；当前实现通过状态更新或运行时删除完成逻辑删除。",
    response_model=UnifiedResponse[Any],
    responses=STRATEGY_DELETE_RESPONSES,
)
async def delete_strategy(strategy_id: int = Path(..., description="需要归档删除的策略ID。")) -> Any:
    """删除策略"""
    try:
        try:
            manager = MyStocksUnifiedManager()

            import pandas as pd

            delete_data = pd.DataFrame([{"id": strategy_id, "status": "archived", "updated_at": datetime.now()}])
            result = manager.save_data_by_classification(
                data=delete_data,
                classification=DataClassification.MODEL_OUTPUT,
                table_name="strategies",
                upsert=True,
            )
        except Exception as db_error:
            if not _runtime_fallback_enabled():
                raise
            removed = _delete_runtime_strategy(strategy_id)
            if not removed:
                raise BusinessException(detail=f"删除策略失败: {str(db_error)}", status_code=500)
            return create_unified_success_response(message="策略已归档")

        if not result and _runtime_fallback_enabled():
            removed = _delete_runtime_strategy(strategy_id)
            if removed:
                return create_unified_success_response(message="策略已归档")

        if result:
            return create_unified_success_response(message="策略已归档")
        else:
            raise BusinessException(detail="策略删除失败", status_code=500)

    except Exception as e:
        raise BusinessException(detail=f"删除策略失败: {str(e)}", status_code=500)


@router.post(
    "/{strategy_id}/start",
    summary="启动策略",
    description="启动指定策略，将策略状态切换为 active 并记录生命周期操作。",
    response_model=UnifiedResponse[Any],
    responses=STRATEGY_START_RESPONSES,
)
async def start_strategy(strategy_id: int = Path(..., description="需要启动的策略ID。")) -> Any:
    """启动策略。"""
    return await _handle_strategy_lifecycle_action(
        strategy_id,
        status="active",
        action_name="start_strategy",
        success_message="策略启动成功",
    )


@router.post(
    "/{strategy_id}/pause",
    summary="暂停策略",
    description="暂停指定策略，将策略状态切换为 paused，适用于人工干预或风控暂停。",
    response_model=UnifiedResponse[Any],
    responses=STRATEGY_PAUSE_RESPONSES,
)
async def pause_strategy(strategy_id: int = Path(..., description="需要暂停的策略ID。")) -> Any:
    """暂停策略。"""
    return await _handle_strategy_lifecycle_action(
        strategy_id,
        status="paused",
        action_name="pause_strategy",
        success_message="策略暂停成功",
    )


@router.post(
    "/{strategy_id}/resume",
    summary="恢复策略",
    description="恢复已暂停的策略运行，将策略状态重新切换为 active。",
    response_model=UnifiedResponse[Any],
    responses=STRATEGY_RESUME_RESPONSES,
)
async def resume_strategy(strategy_id: int = Path(..., description="需要恢复运行的策略ID。")) -> Any:
    """恢复策略。"""
    return await _handle_strategy_lifecycle_action(
        strategy_id,
        status="active",
        action_name="resume_strategy",
        success_message="策略恢复成功",
    )


@router.post(
    "/{strategy_id}/stop",
    summary="停止策略",
    description="停止指定策略并归档，适用于策略下线、停用或终止执行场景。",
    response_model=UnifiedResponse[Any],
    responses=STRATEGY_STOP_RESPONSES,
)
async def stop_strategy(strategy_id: int = Path(..., description="需要停止并归档的策略ID。")) -> Any:
    """停止策略。"""
    return await _handle_strategy_lifecycle_action(
        strategy_id,
        status="archived",
        action_name="stop_strategy",
        success_message="策略停止成功",
    )
