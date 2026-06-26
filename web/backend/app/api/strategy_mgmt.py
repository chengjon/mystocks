"""
策略管理API路由 (Phase 4)

提供策略CRUD和回测引擎的RESTful API端点。
基于Phase 3的CompositeBusinessDataSource架构。

版本: 1.0.0
日期: 2025-11-21
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Path, Query, Header
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException

from app.api._strategy_mgmt_responses import (
    BACKTEST_RESULT_COMPLETED_EXAMPLE,
    BACKTEST_RESULT_PENDING_EXAMPLE,
    BACKTEST_STATUS_SUCCESS_RESPONSE,
    CREATE_STRATEGY_SUCCESS_RESPONSE,
    EXECUTE_BACKTEST_SUCCESS_RESPONSE,
    GET_BACKTEST_RESULT_SUCCESS_RESPONSE,
    GET_STRATEGY_SUCCESS_RESPONSE,
    LIST_BACKTESTS_SUCCESS_RESPONSE,
    LIST_STRATEGIES_SUCCESS_RESPONSE,
    STRATEGY_CONFIG_EXAMPLE,
    STRATEGY_MGMT_HEALTH_SUCCESS_RESPONSE,
    STRATEGY_MGMT_ROUTE_RESPONSES,
    STRATEGY_UPDATE_REQUEST_EXAMPLES,
    UPDATE_STRATEGY_SUCCESS_RESPONSE,
)

from app.api.strategy_management.backtest_status_contract import (
    BacktestStatusResponse,
    build_backtest_status_response,
)
from app.core.celery_app import register_backtest_task
from app.core.config import settings
from app.core.database import get_db
from app.core.responses import ErrorCodes, create_error_response
from app.core.security import verify_token
from app.models.strategy_schemas import (
    BacktestExecuteRequest,
    BacktestListResponse,
    BacktestRequest,
    BacktestResult,
    BacktestResultSummary,
    StrategyConfig,
    StrategyCreateRequest,
    StrategyListResponse,
    StrategyStatus,
    StrategyUpdateRequest,
)
from app.repositories import BacktestRepository, StrategyRepository
from app.tasks.backtest_tasks import run_backtest_task
from src.data_sources import get_business_source

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/strategy-mgmt", tags=["strategy-mgmt"], responses=STRATEGY_MGMT_ROUTE_RESPONSES)


# ============================================================================
# 辅助函数
# ============================================================================


def get_data_source():
    """获取业务数据源"""
    try:
        return get_business_source()
    except Exception as e:
        logger.error("获取数据源失败: {str(e)}")
        raise BusinessException(status_code=500, detail=f"数据源初始化失败: {str(e)}")


def get_strategy_repository(db: Session = Depends(get_db)) -> StrategyRepository:
    """获取策略仓库实例"""
    ensure_strategy_runtime_schema_ready(db)
    return StrategyRepository(db)


def get_backtest_repository(db: Session = Depends(get_db)) -> BacktestRepository:
    """获取回测仓库实例"""
    ensure_strategy_runtime_schema_ready(db)
    return BacktestRepository(db)


def ensure_strategy_runtime_schema_ready(db: Session) -> dict[str, list[str]]:
    """Ensure strategy runtime tables can satisfy current read paths.

    This is additive only: create missing ORM tables with checkfirst and add
    missing columns. It never drops, renames, or rewrites existing tables.
    """
    from app.repositories.backtest_repository import BacktestResultModel
    from app.repositories.strategy_repository import UserStrategyModel

    bind = db.get_bind()
    inspector = inspect(bind)
    created_tables: list[str] = []
    added_columns: list[str] = []

    for model in (UserStrategyModel, BacktestResultModel):
        table = model.__table__
        if not inspector.has_table(table.name):
            table.create(bind=bind, checkfirst=True)
            created_tables.append(table.name)
            continue

        existing_columns = {column["name"] for column in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name in existing_columns:
                continue
            column_type = column.type.compile(dialect=bind.dialect)
            default = ""
            if column.default is not None and column.default.is_scalar:
                default = f" DEFAULT {column.default.arg!r}"
            db.execute(text(f"ALTER TABLE {table.name} ADD COLUMN IF NOT EXISTS {column.name} {column_type}{default}"))
            added_columns.append(f"{table.name}.{column.name}")

    if added_columns:
        db.commit()

    return {"created_tables": created_tables, "added_columns": added_columns}


def _require_write_auth(authorization: Optional[str]) -> None:
    """写操作鉴权：测试环境放行，非测试环境要求有效Bearer Token。"""
    if settings.testing:
        return

    if not authorization or not authorization.startswith("Bearer "):
        raise BusinessException(
            status_code=401,
            detail=create_error_response(
                ErrorCodes.UNAUTHORIZED,
                "缺少或无效的认证凭据",
            ).dict(),
        )

    token = authorization.removeprefix("Bearer ").strip()
    if not token or verify_token(token) is None:
        raise BusinessException(
            status_code=401,
            detail=create_error_response(
                ErrorCodes.UNAUTHORIZED,
                "认证失败或令牌已过期",
            ).dict(),
        )


# ============================================================================
# 策略CRUD端点
# ============================================================================


@router.post(
    "/strategies",
    response_model=StrategyConfig,
    status_code=201,
    summary="创建新策略",
    description="创建一个新的交易策略配置，并返回可直接用于策略管理页面展示的完整策略信息。",
    responses=CREATE_STRATEGY_SUCCESS_RESPONSE,
)
async def create_strategy(
    strategy: StrategyCreateRequest = Body(
        ...,
        openapi_examples={
            "momentum_strategy": {
                "summary": "创建动量策略",
                "value": {
                    "user_id": 1001,
                    "strategy_name": "双均线突破",
                    "strategy_type": "momentum",
                    "description": "基于短中期均线突破信号的趋势跟踪策略",
                    "parameters": [
                        {
                            "name": "short_period",
                            "value": 5,
                            "description": "短周期均线窗口",
                            "data_type": "int",
                        },
                        {
                            "name": "long_period",
                            "value": 20,
                            "description": "长周期均线窗口",
                            "data_type": "int",
                        },
                    ],
                    "max_position_size": 0.2,
                    "stop_loss_percent": 5.0,
                    "take_profit_percent": 12.0,
                    "tags": ["趋势", "均线"],
                },
            }
        },
    ),
    strategy_repo: StrategyRepository = Depends(get_strategy_repository),
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer 令牌。非测试环境下写操作必填，格式为 `Bearer <token>`。",
    ),
):
    """
    创建新策略

    **请求参数**:
    - user_id: 用户ID
    - strategy_name: 策略名称
    - strategy_type: 策略类型 (momentum/mean_reversion/breakout/grid/custom)
    - description: 策略描述
    - parameters: 策略参数列表
    - max_position_size: 最大仓位比例 (0-1)
    - stop_loss_percent: 止损百分比
    - take_profit_percent: 止盈百分比
    - tags: 标签列表

    **返回**:
    - 完整的策略配置对象 (包含生成的strategy_id)
    """
    try:
        _require_write_auth(authorization)
        # 使用仓库创建策略
        strategy_config = strategy_repo.create_strategy(strategy)

        logger.info("策略创建成功: strategy_id={strategy_config.strategy_id}, name={strategy_config.strategy_name}")
        return strategy_config

    except ValueError as e:
        logger.error("参数验证失败: {str(e)}")
        raise BusinessException(status_code=400, detail=f"参数验证失败: {str(e)}")
    except Exception as e:
        logger.error("创建策略失败: {str(e)}", exc_info=True)
        raise BusinessException(status_code=500, detail=f"创建策略失败: {str(e)}")


@router.get(
    "/strategies",
    response_model=StrategyListResponse,
    summary="获取策略列表",
    description="获取用户的策略列表，支持分页、状态筛选和策略管理页的数据初始化。",
    responses=LIST_STRATEGIES_SUCCESS_RESPONSE,
)
async def list_strategies(
    user_id: int = Query(..., description="用户ID", ge=1),
    status: Optional[StrategyStatus] = Query(None, description="策略状态筛选"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    strategy_repo: StrategyRepository = Depends(get_strategy_repository),
):
    """
    获取策略列表

    **查询参数**:
    - user_id: 用户ID (必需)
    - status: 策略状态筛选 (可选)
    - page: 页码 (默认1)
    - page_size: 每页数量 (默认20)

    **返回**:
    - 策略列表和分页信息
    """
    try:
        # 使用仓库查询策略列表
        strategies, total_count = strategy_repo.list_strategies(
            user_id=user_id, status=status, page=page, page_size=page_size
        )

        logger.info("获取策略列表成功: user_id=%(user_id)s, count=%(total_count)s")

        return StrategyListResponse(total_count=total_count, strategies=strategies, page=page, page_size=page_size)

    except Exception as e:
        logger.error("获取策略列表失败: {str(e)}")
        raise BusinessException(status_code=500, detail=f"获取策略列表失败: {str(e)}")


@router.get(
    "/strategies/{strategy_id}",
    response_model=StrategyConfig,
    summary="获取策略详情",
    description="根据策略 ID 获取完整配置、参数和风险控制信息，供详情页或编辑页回填。",
    responses=GET_STRATEGY_SUCCESS_RESPONSE,
)
async def get_strategy(
    strategy_id: int = Path(..., description="策略ID", ge=1),
    strategy_repo: StrategyRepository = Depends(get_strategy_repository),
):
    """
    获取策略详情

    **路径参数**:
    - strategy_id: 策略ID

    **返回**:
    - 策略的完整配置
    """
    try:
        strategy = strategy_repo.get_strategy(strategy_id)

        if strategy is None:
            raise BusinessException(status_code=404, detail=f"策略不存在: strategy_id={strategy_id}")

        logger.info("获取策略详情成功: strategy_id=%(strategy_id)s")
        return strategy

    except BusinessException:
        raise
    except Exception as e:
        logger.error("获取策略详情失败: {str(e)}")
        raise BusinessException(status_code=500, detail=f"获取策略详情失败: {str(e)}")


@router.put(
    "/strategies/{strategy_id}",
    response_model=StrategyConfig,
    summary="更新策略",
    description="更新指定策略的配置项、状态或风险参数，并返回最新的完整策略信息。",
    responses=UPDATE_STRATEGY_SUCCESS_RESPONSE,
)
async def update_strategy(
    strategy_id: int = Path(..., description="策略ID", ge=1),
    update_data: StrategyUpdateRequest = Body(..., openapi_examples=STRATEGY_UPDATE_REQUEST_EXAMPLES),
    strategy_repo: StrategyRepository = Depends(get_strategy_repository),
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer 令牌。非测试环境下写操作必填，格式为 `Bearer <token>`。",
    ),
):
    """
    更新策略

    **路径参数**:
    - strategy_id: 策略ID

    **请求体**:
    - 需要更新的策略字段 (所有字段均为可选)

    **返回**:
    - 更新后的策略配置
    """
    try:
        _require_write_auth(authorization)
        strategy = strategy_repo.update_strategy(strategy_id, update_data)

        if strategy is None:
            raise BusinessException(status_code=404, detail=f"策略不存在: strategy_id={strategy_id}")

        logger.info("策略更新成功: strategy_id=%(strategy_id)s")
        return strategy

    except BusinessException:
        raise
    except Exception as e:
        logger.error("更新策略失败: {str(e)}")
        raise BusinessException(status_code=500, detail=f"更新策略失败: {str(e)}")


@router.delete(
    "/strategies/{strategy_id}",
    status_code=204,
    summary="删除策略",
    description="删除指定的策略配置，并在成功后返回 204 无内容响应。",
)
async def delete_strategy(
    strategy_id: int = Path(..., description="策略ID", ge=1),
    strategy_repo: StrategyRepository = Depends(get_strategy_repository),
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer 令牌。非测试环境下写操作必填，格式为 `Bearer <token>`。",
    ),
):
    """
    删除策略

    **路径参数**:
    - strategy_id: 策略ID

    **返回**:
    - 204 No Content (成功删除)
    """
    try:
        _require_write_auth(authorization)
        deleted = strategy_repo.delete_strategy(strategy_id)

        if not deleted:
            raise BusinessException(status_code=404, detail=f"策略不存在: strategy_id={strategy_id}")

        logger.info("策略删除成功: strategy_id=%(strategy_id)s")

    except BusinessException:
        raise
    except Exception as e:
        logger.error("删除策略失败: {str(e)}")
        raise BusinessException(status_code=500, detail=f"删除策略失败: {str(e)}")


# ============================================================================
# 回测引擎端点
# ============================================================================


@router.post(
    "/backtest/execute",
    response_model=BacktestResult,
    status_code=202,
    summary="执行回测",
    description="异步执行策略回测任务，并返回已登记的回测任务信息与初始状态。",
    responses=EXECUTE_BACKTEST_SUCCESS_RESPONSE,
)
async def execute_backtest(
    background_tasks: BackgroundTasks,
    backtest_req: BacktestRequest = Body(
        ...,
        openapi_examples={
            "swing_backtest": {
                "summary": "执行波段策略回测",
                "value": {
                    "strategy_id": 123,
                    "user_id": 1001,
                    "symbols": ["000001.SZ", "600000.SH"],
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "initial_capital": 100000.0,
                    "commission_rate": 0.0003,
                    "slippage_rate": 0.001,
                    "benchmark": "000300.SH",
                    "include_analysis": True,
                },
            }
        },
    ),
    strategy_repo: StrategyRepository = Depends(get_strategy_repository),
    backtest_repo: BacktestRepository = Depends(get_backtest_repository),
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer 令牌。非测试环境下写操作必填，格式为 `Bearer <token>`。",
    ),
):
    """
    执行回测

    **请求参数**:
    - strategy_id: 策略ID
    - user_id: 用户ID
    - symbols: 股票代码列表
    - start_date: 开始日期
    - end_date: 结束日期
    - initial_capital: 初始资金
    - commission_rate: 手续费率
    - slippage_rate: 滑点率
    - benchmark: 基准指数代码 (可选)
    - include_analysis: 是否包含详细分析

    **返回**:
    - 回测结果对象 (初始状态为PENDING)
    """
    try:
        _require_write_auth(authorization)
        # 验证策略存在
        strategy = strategy_repo.get_strategy(backtest_req.strategy_id)
        if strategy is None:
            raise BusinessException(status_code=404, detail=f"策略不存在: strategy_id={backtest_req.strategy_id}")

        # 创建BacktestExecuteRequest
        execute_request = BacktestExecuteRequest(
            strategy_id=backtest_req.strategy_id,
            user_id=backtest_req.user_id,
            symbols=backtest_req.symbols,
            start_date=backtest_req.start_date,
            end_date=backtest_req.end_date,
            initial_capital=backtest_req.initial_capital,
            commission_rate=backtest_req.commission_rate,
            slippage_rate=backtest_req.slippage_rate,
            benchmark=backtest_req.benchmark,
        )

        # 创建回测任务
        backtest_result = backtest_repo.create_backtest(execute_request)

        # 准备策略配置
        strategy_config_dict = {
            "strategy_id": strategy.strategy_id,
            "strategy_name": strategy.strategy_name,
            "strategy_type": (
                strategy.strategy_type.value if hasattr(strategy.strategy_type, "value") else strategy.strategy_type
            ),
            "parameters": [p.model_dump() for p in strategy.parameters],
            "max_position_size": strategy.max_position_size,
            "stop_loss_percent": strategy.stop_loss_percent,
            "take_profit_percent": strategy.take_profit_percent,
        }

        # 准备回测配置
        backtest_config_dict = {
            "backtest_id": backtest_result.backtest_id,
            "symbols": backtest_req.symbols,
            "start_date": backtest_req.start_date.isoformat(),
            "end_date": backtest_req.end_date.isoformat(),
            "initial_capital": float(backtest_req.initial_capital),
            "commission_rate": float(backtest_req.commission_rate),
            "slippage_rate": float(backtest_req.slippage_rate),
            "benchmark": backtest_req.benchmark,
        }

        # 启动 Celery 异步任务
        task = run_backtest_task.delay(
            backtest_id=backtest_result.backtest_id,
            strategy_config=strategy_config_dict,
            backtest_config=backtest_config_dict,
        )
        register_backtest_task(backtest_result.backtest_id, task.id)

        logger.info("回测任务已提交: backtest_id={backtest_result.backtest_id}, task_id={task.id}")
        return backtest_result

    except BusinessException:
        raise
    except ValueError as e:
        logger.error("回测参数验证失败: {str(e)}")
        raise BusinessException(status_code=400, detail=f"回测参数验证失败: {str(e)}")
    except Exception as e:
        logger.error("执行回测失败: {str(e)}", exc_info=True)
        raise BusinessException(status_code=500, detail=f"执行回测失败: {str(e)}")


@router.get(
    "/backtest/results/{backtest_id}",
    response_model=BacktestResult,
    summary="获取回测结果",
    description="根据回测 ID 获取完整的回测结果、绩效指标、权益曲线和交易记录。",
    responses=GET_BACKTEST_RESULT_SUCCESS_RESPONSE,
)
async def get_backtest_result(
    backtest_id: int = Path(..., description="回测ID", ge=1),
    backtest_repo: BacktestRepository = Depends(get_backtest_repository),
):
    """
    获取回测结果

    **路径参数**:
    - backtest_id: 回测ID

    **返回**:
    - 完整的回测结果 (包括绩效指标、权益曲线、交易记录等)
    """
    try:
        backtest_result = backtest_repo.get_backtest(backtest_id)

        if backtest_result is None:
            raise BusinessException(status_code=404, detail=f"回测结果不存在: backtest_id={backtest_id}")

        logger.info("获取回测结果成功: backtest_id=%(backtest_id)s")
        return backtest_result

    except BusinessException:
        raise
    except Exception as e:
        logger.error("获取回测结果失败: {str(e)}")
        raise BusinessException(status_code=500, detail=f"获取回测结果失败: {str(e)}")


@router.get(
    "/backtest/results",
    response_model=BacktestListResponse,
    summary="获取回测列表",
    description="获取用户的回测历史列表，支持分页和按策略过滤，用于回测记录页展示。",
    responses=LIST_BACKTESTS_SUCCESS_RESPONSE,
)
async def list_backtests(
    user_id: int = Query(..., description="用户ID", ge=1),
    strategy_id: Optional[int] = Query(None, description="策略ID筛选", ge=1),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    strategy_repo: StrategyRepository = Depends(get_strategy_repository),
    backtest_repo: BacktestRepository = Depends(get_backtest_repository),
):
    """
    获取回测列表

    **查询参数**:
    - user_id: 用户ID (必需)
    - strategy_id: 策略ID筛选 (可选)
    - page: 页码 (默认1)
    - page_size: 每页数量 (默认20)

    **返回**:
    - 回测汇总列表和分页信息
    """
    try:
        # 使用仓库查询回测列表
        backtests, total_count = backtest_repo.list_backtests(
            user_id=user_id, strategy_id=strategy_id, page=page, page_size=page_size
        )

        # 转换为汇总格式
        backtest_summaries = []
        for bt in backtests:
            strategy = strategy_repo.get_strategy(bt.strategy_id)
            summary = BacktestResultSummary(
                backtest_id=bt.backtest_id,
                strategy_id=bt.strategy_id,
                strategy_name=strategy.strategy_name if strategy else "未知策略",
                symbols=bt.symbols,
                date_range=f"{bt.start_date} ~ {bt.end_date}",
                total_return=bt.performance_metrics.total_return if bt.performance_metrics else 0.0,
                sharpe_ratio=bt.performance_metrics.sharpe_ratio if bt.performance_metrics else 0.0,
                max_drawdown=bt.performance_metrics.max_drawdown if bt.performance_metrics else 0.0,
                status=bt.status,
                created_at=bt.created_at,
            )
            backtest_summaries.append(summary)

        logger.info("获取回测列表成功: user_id=%(user_id)s, count=%(total_count)s")

        return BacktestListResponse(
            total_count=total_count, backtests=backtest_summaries, page=page, page_size=page_size
        )

    except Exception as e:
        logger.error("获取回测列表失败: {str(e)}")
        raise BusinessException(status_code=500, detail=f"获取回测列表失败: {str(e)}")


@router.get(
    "/health",
    summary="健康检查",
    description="检查策略管理服务、数据库连接和底层业务数据源是否处于可用状态。",
    responses=STRATEGY_MGMT_HEALTH_SUCCESS_RESPONSE,
)
async def health_check(db: Session = Depends(get_db), data_source=Depends(get_data_source)):
    """健康检查端点"""
    try:
        # 检查数据库连接
        db.execute(text("SELECT 1"))

        # 检查数据源
        health = data_source.health_check()

        ensure_strategy_runtime_schema_ready(db)

        # 统计数据库中的策略和回测数量
        StrategyRepository(db)
        BacktestRepository(db)

        # 简单查询以验证数据库可用性
        from app.repositories.backtest_repository import BacktestResultModel
        from app.repositories.strategy_repository import UserStrategyModel

        strategies_count = db.query(UserStrategyModel).count()
        backtests_count = db.query(BacktestResultModel).count()

        return {
            "status": "healthy",
            "service": "strategy-mgmt",
            "database": "connected",
            "data_source": health,
            "strategies_count": strategies_count,
            "backtests_count": backtests_count,
            "timestamp": datetime.now(),
        }
    except Exception as e:
        logger.error("健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "strategy-mgmt",
            "database": "error",
            "error": str(e),
            "timestamp": datetime.now(),
        }


@router.get(
    "/backtest/status/{backtest_id}",
    response_model=BacktestStatusResponse,
    summary="获取回测任务状态",
    description="兼容旧版回测状态查询接口，推荐改用 /api/v1/strategy/backtest/status/{backtest_id}",
    deprecated=True,
    responses=BACKTEST_STATUS_SUCCESS_RESPONSE,
)
async def get_backtest_status(
    backtest_id: int = Path(..., description="回测ID", ge=1),
    backtest_repo: BacktestRepository = Depends(get_backtest_repository),
) -> BacktestStatusResponse:
    """
    获取回测任务状态。

    兼容保留接口，前端契约应迁移到 `/api/v1/strategy/backtest/status/{backtest_id}`。

    **路径参数**:
    - backtest_id: 回测ID

    **返回**:
    - 任务状态、进度和相关信息
    """
    try:
        # 从数据库获取回测信息
        backtest = backtest_repo.get_backtest(backtest_id)

        if backtest is None:
            raise BusinessException(status_code=404, detail=f"回测不存在: backtest_id={backtest_id}")

        return build_backtest_status_response(backtest_id, backtest)

    except BusinessException:
        raise
    except Exception as e:
        logger.error("获取回测状态失败: {str(e)}")
        raise BusinessException(status_code=500, detail=f"获取回测状态失败: {str(e)}")
