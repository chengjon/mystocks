"""
策略管理API路由 (Phase 4)

提供策略CRUD和回测引擎的RESTful API端点。
基于Phase 3的CompositeBusinessDataSource架构。

版本: 1.0.0
日期: 2025-11-21
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path, BackgroundTasks
from typing import Optional, List
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from app.models.strategy_schemas import (
    StrategyConfig,
    StrategyCreateRequest,
    StrategyUpdateRequest,
    StrategyListResponse,
    BacktestRequest,
    BacktestResult,
    BacktestResultSummary,
    BacktestListResponse,
    BacktestExecuteRequest,
    StrategyStatus,
    BacktestStatus,
    PerformanceMetrics,
    EquityCurvePoint,
    TradeRecord,
    StrategyErrorResponse
)
from app.repositories import StrategyRepository, BacktestRepository
from app.core.database import get_db
from src.data_sources import get_business_source
from app.tasks.backtest_tasks import run_backtest_task

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/api/strategy-mgmt",
    tags=["strategy-mgmt"],
    responses={404: {"description": "Not found"}}
)


# ============================================================================
# 辅助函数
# ============================================================================

def get_data_source():
    """获取业务数据源"""
    try:
        return get_business_source()
    except Exception as e:
        logger.error(f"获取数据源失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"数据源初始化失败: {str(e)}"
        )


def get_strategy_repository(db: Session = Depends(get_db)) -> StrategyRepository:
    """获取策略仓库实例"""
    return StrategyRepository(db)


def get_backtest_repository(db: Session = Depends(get_db)) -> BacktestRepository:
    """获取回测仓库实例"""
    return BacktestRepository(db)


# ============================================================================
# 策略CRUD端点
# ============================================================================

@router.post(
    "/strategies",
    response_model=StrategyConfig,
    status_code=201,
    summary="创建新策略",
    description="创建一个新的交易策略配置"
)
async def create_strategy(
    strategy: StrategyCreateRequest,
    strategy_repo: StrategyRepository = Depends(get_strategy_repository)
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
        # 使用仓库创建策略
        strategy_config = strategy_repo.create_strategy(strategy)

        logger.info(f"策略创建成功: strategy_id={strategy_config.strategy_id}, name={strategy_config.strategy_name}")
        return strategy_config

    except ValueError as e:
        logger.error(f"参数验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"参数验证失败: {str(e)}")
    except Exception as e:
        logger.error(f"创建策略失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建策略失败: {str(e)}")


@router.get(
    "/strategies",
    response_model=StrategyListResponse,
    summary="获取策略列表",
    description="获取用户的策略列表，支持分页和状态筛选"
)
async def list_strategies(
    user_id: int = Query(..., description="用户ID", ge=1),
    status: Optional[StrategyStatus] = Query(None, description="策略状态筛选"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    strategy_repo: StrategyRepository = Depends(get_strategy_repository)
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
            user_id=user_id,
            status=status,
            page=page,
            page_size=page_size
        )

        logger.info(f"获取策略列表成功: user_id={user_id}, count={total_count}")

        return StrategyListResponse(
            total_count=total_count,
            strategies=strategies,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"获取策略列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取策略列表失败: {str(e)}")


@router.get(
    "/strategies/{strategy_id}",
    response_model=StrategyConfig,
    summary="获取策略详情",
    description="根据ID获取策略的完整配置信息"
)
async def get_strategy(
    strategy_id: int = Path(..., description="策略ID", ge=1),
    strategy_repo: StrategyRepository = Depends(get_strategy_repository)
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
            raise HTTPException(
                status_code=404,
                detail=f"策略不存在: strategy_id={strategy_id}"
            )

        logger.info(f"获取策略详情成功: strategy_id={strategy_id}")
        return strategy

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取策略详情失败: {str(e)}")


@router.put(
    "/strategies/{strategy_id}",
    response_model=StrategyConfig,
    summary="更新策略",
    description="更新策略的配置信息"
)
async def update_strategy(
    strategy_id: int = Path(..., description="策略ID", ge=1),
    update_data: StrategyUpdateRequest = ...,
    strategy_repo: StrategyRepository = Depends(get_strategy_repository)
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
        strategy = strategy_repo.update_strategy(strategy_id, update_data)

        if strategy is None:
            raise HTTPException(
                status_code=404,
                detail=f"策略不存在: strategy_id={strategy_id}"
            )

        logger.info(f"策略更新成功: strategy_id={strategy_id}")
        return strategy

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新策略失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新策略失败: {str(e)}")


@router.delete(
    "/strategies/{strategy_id}",
    status_code=204,
    summary="删除策略",
    description="删除指定的策略配置"
)
async def delete_strategy(
    strategy_id: int = Path(..., description="策略ID", ge=1),
    strategy_repo: StrategyRepository = Depends(get_strategy_repository)
):
    """
    删除策略

    **路径参数**:
    - strategy_id: 策略ID

    **返回**:
    - 204 No Content (成功删除)
    """
    try:
        deleted = strategy_repo.delete_strategy(strategy_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"策略不存在: strategy_id={strategy_id}"
            )

        logger.info(f"策略删除成功: strategy_id={strategy_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除策略失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除策略失败: {str(e)}")


# ============================================================================
# 回测引擎端点
# ============================================================================

@router.post(
    "/backtest/execute",
    response_model=BacktestResult,
    status_code=202,
    summary="执行回测",
    description="异步执行策略回测,返回回测任务信息"
)
async def execute_backtest(
    backtest_req: BacktestRequest,
    background_tasks: BackgroundTasks,
    strategy_repo: StrategyRepository = Depends(get_strategy_repository),
    backtest_repo: BacktestRepository = Depends(get_backtest_repository)
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
        # 验证策略存在
        strategy = strategy_repo.get_strategy(backtest_req.strategy_id)
        if strategy is None:
            raise HTTPException(
                status_code=404,
                detail=f"策略不存在: strategy_id={backtest_req.strategy_id}"
            )

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
            benchmark=backtest_req.benchmark
        )

        # 创建回测任务
        backtest_result = backtest_repo.create_backtest(execute_request)

        # 准备策略配置
        strategy_config_dict = {
            'strategy_id': strategy.strategy_id,
            'strategy_name': strategy.strategy_name,
            'strategy_type': strategy.strategy_type.value if hasattr(strategy.strategy_type, 'value') else strategy.strategy_type,
            'parameters': [p.model_dump() for p in strategy.parameters],
            'max_position_size': strategy.max_position_size,
            'stop_loss_percent': strategy.stop_loss_percent,
            'take_profit_percent': strategy.take_profit_percent
        }

        # 准备回测配置
        backtest_config_dict = {
            'backtest_id': backtest_result.backtest_id,
            'symbols': backtest_req.symbols,
            'start_date': backtest_req.start_date.isoformat(),
            'end_date': backtest_req.end_date.isoformat(),
            'initial_capital': float(backtest_req.initial_capital),
            'commission_rate': float(backtest_req.commission_rate),
            'slippage_rate': float(backtest_req.slippage_rate),
            'benchmark': backtest_req.benchmark
        }

        # 启动 Celery 异步任务
        task = run_backtest_task.delay(
            backtest_id=backtest_result.backtest_id,
            strategy_config=strategy_config_dict,
            backtest_config=backtest_config_dict
        )

        logger.info(f"回测任务已提交: backtest_id={backtest_result.backtest_id}, task_id={task.id}")
        return backtest_result

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"回测参数验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"回测参数验证失败: {str(e)}")
    except Exception as e:
        logger.error(f"执行回测失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"执行回测失败: {str(e)}")


@router.get(
    "/backtest/results/{backtest_id}",
    response_model=BacktestResult,
    summary="获取回测结果",
    description="根据回测ID获取完整的回测结果"
)
async def get_backtest_result(
    backtest_id: int = Path(..., description="回测ID", ge=1),
    backtest_repo: BacktestRepository = Depends(get_backtest_repository)
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
            raise HTTPException(
                status_code=404,
                detail=f"回测结果不存在: backtest_id={backtest_id}"
            )

        logger.info(f"获取回测结果成功: backtest_id={backtest_id}")
        return backtest_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取回测结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取回测结果失败: {str(e)}")


@router.get(
    "/backtest/results",
    response_model=BacktestListResponse,
    summary="获取回测列表",
    description="获取用户的回测历史列表，支持分页"
)
async def list_backtests(
    user_id: int = Query(..., description="用户ID", ge=1),
    strategy_id: Optional[int] = Query(None, description="策略ID筛选", ge=1),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    strategy_repo: StrategyRepository = Depends(get_strategy_repository),
    backtest_repo: BacktestRepository = Depends(get_backtest_repository)
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
            user_id=user_id,
            strategy_id=strategy_id,
            page=page,
            page_size=page_size
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
                created_at=bt.created_at
            )
            backtest_summaries.append(summary)

        logger.info(f"获取回测列表成功: user_id={user_id}, count={total_count}")

        return BacktestListResponse(
            total_count=total_count,
            backtests=backtest_summaries,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"获取回测列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取回测列表失败: {str(e)}")


@router.get(
    "/health",
    summary="健康检查",
    description="检查策略管理服务和数据库连接的健康状态"
)
async def health_check(
    db: Session = Depends(get_db),
    data_source = Depends(get_data_source)
):
    """健康检查端点"""
    try:
        # 检查数据库连接
        db.execute("SELECT 1")

        # 检查数据源
        health = data_source.health_check()

        # 统计数据库中的策略和回测数量
        strategy_repo = StrategyRepository(db)
        backtest_repo = BacktestRepository(db)

        # 简单查询以验证数据库可用性
        from app.repositories.strategy_repository import UserStrategyModel
        from app.repositories.backtest_repository import BacktestResultModel

        strategies_count = db.query(UserStrategyModel).count()
        backtests_count = db.query(BacktestResultModel).count()

        return {
            "status": "healthy",
            "service": "strategy-mgmt",
            "database": "connected",
            "data_source": health,
            "strategies_count": strategies_count,
            "backtests_count": backtests_count,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "strategy-mgmt",
            "database": "error",
            "error": str(e),
            "timestamp": datetime.now()
        }


@router.get(
    "/backtest/status/{backtest_id}",
    summary="获取回测任务状态",
    description="获取回测任务的当前执行状态和进度"
)
async def get_backtest_status(
    backtest_id: int = Path(..., description="回测ID", ge=1),
    backtest_repo: BacktestRepository = Depends(get_backtest_repository)
):
    """
    获取回测任务状态

    **路径参数**:
    - backtest_id: 回测ID

    **返回**:
    - 任务状态、进度和相关信息
    """
    try:
        # 从数据库获取回测信息
        backtest = backtest_repo.get_backtest(backtest_id)

        if backtest is None:
            raise HTTPException(
                status_code=404,
                detail=f"回测不存在: backtest_id={backtest_id}"
            )

        # 返回状态信息
        return {
            "backtest_id": backtest_id,
            "status": backtest.status.value if hasattr(backtest.status, 'value') else backtest.status,
            "created_at": backtest.created_at,
            "started_at": backtest.started_at,
            "completed_at": backtest.completed_at,
            "error_message": backtest.error_message,
            "has_results": backtest.performance_metrics is not None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取回测状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取回测状态失败: {str(e)}")
