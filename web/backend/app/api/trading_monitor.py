"""
# pylint: disable=no-member  # TODO: 实现缺失的 GPU/业务方法
实时交易监控API
Real-time Trading Monitoring API

提供实时交易状态监控、策略性能跟踪、风险指标监控等功能。
Provides real-time trading status monitoring, strategy performance tracking, risk metrics monitoring, etc.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field

from src.trading.live_trading_engine import LiveTradingConfig
from src.trading.realtime_strategy_executor import RealtimeStrategyExecutor

router = APIRouter(prefix="/api/trading", tags=["实时交易监控"])


class TradingStatusResponse(BaseModel):
    """交易状态响应"""

    is_running: bool = Field(..., description="交易是否正在运行")
    session_id: Optional[str] = Field(None, description="交易会话ID")
    active_positions: int = Field(..., description="活跃头寸数量")
    total_pnl: float = Field(..., description="总盈亏")
    daily_pnl: float = Field(..., description="当日盈亏")
    current_drawdown: float = Field(..., description="当前回撤")
    trading_hours: bool = Field(..., description="是否为交易时间")


class StrategyPerformanceResponse(BaseModel):
    """策略性能响应"""

    strategy_name: str = Field(..., description="策略名称")
    status: str = Field(..., description="策略状态")
    performance_metrics: Dict[str, Any] = Field(..., description="性能指标")


class MarketDataSnapshotResponse(BaseModel):
    """市场数据快照响应"""

    timestamp: str = Field(..., description="快照时间戳")
    symbols_count: int = Field(..., description="股票数量")
    data: Dict[str, Any] = Field(..., description="市场数据")


class TradingSessionSummaryResponse(BaseModel):
    """交易会话摘要响应"""

    session_id: str = Field(..., description="会话ID")
    start_time: str = Field(..., description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    duration_seconds: float = Field(..., description="持续时间（秒）")
    total_trades: int = Field(..., description="总交易次数")
    winning_trades: int = Field(..., description="盈利交易次数")
    losing_trades: int = Field(..., description="亏损交易次数")
    total_pnl: float = Field(..., description="总盈亏")
    max_drawdown: float = Field(..., description="最大回撤")
    win_rate: float = Field(..., description="胜率")


# 全局执行器实例（生产环境中应该使用依赖注入）
_executor_instance: Optional[RealtimeStrategyExecutor] = None


def get_trading_executor() -> RealtimeStrategyExecutor:
    """获取交易执行器实例（单例模式）"""
    global _executor_instance
    if _executor_instance is None:
        # 创建默认配置的执行器
        config = LiveTradingConfig()
        _executor_instance = RealtimeStrategyExecutor(
            strategies=[],  # 可以通过API动态添加策略
            config=config,
        )
    return _executor_instance


@router.get("/status", response_model=TradingStatusResponse, summary="获取交易状态")
async def get_trading_status():
    """
    获取当前实时交易状态

    返回交易运行状态、活跃头寸数量、盈亏情况等信息。
    """
    try:
        executor = get_trading_executor()
        status = executor.get_execution_status()
        trading_status = status.get("trading_engine", {})

        return TradingStatusResponse(
            is_running=status.get("is_running", False),
            session_id=trading_status.get("session_id"),
            active_positions=trading_status.get("active_positions", 0),
            total_pnl=trading_status.get("total_pnl", 0.0),
            daily_pnl=trading_status.get("daily_pnl", 0.0),
            current_drawdown=trading_status.get("current_drawdown", 0.0),
            trading_hours=trading_status.get("trading_hours", False),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易状态失败: {str(e)}")


@router.get("/strategies/performance", response_model=List[StrategyPerformanceResponse], summary="获取策略性能")
async def get_strategies_performance():
    """
    获取所有策略的性能指标

    返回每个策略的性能统计信息。
    """
    try:
        executor = get_trading_executor()
        performance_data = executor.get_strategy_performance()

        result = []
        for strategy_name, metrics in performance_data.items():
            result.append(
                StrategyPerformanceResponse(
                    strategy_name=strategy_name, status=metrics.get("status", "unknown"), performance_metrics=metrics
                )
            )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取策略性能失败: {str(e)}")


@router.get("/market/snapshot", response_model=MarketDataSnapshotResponse, summary="获取市场数据快照")
async def get_market_snapshot():
    """
    获取当前市场数据快照

    返回所有监控股票的实时价格和交易数据。
    """
    try:
        executor = get_trading_executor()
        snapshot = executor.get_market_data_snapshot()

        return MarketDataSnapshotResponse(
            timestamp=snapshot.get("timestamp", datetime.now().isoformat()),
            symbols_count=snapshot.get("symbols_count", 0),
            data=snapshot.get("data", {}),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取市场快照失败: {str(e)}")


@router.post("/start", summary="启动实时交易")
async def start_trading_session(background_tasks: BackgroundTasks):
    """
    启动新的实时交易会话

    初始化策略执行器并开始监控市场数据和执行交易信号。
    """
    try:
        executor = get_trading_executor()

        # 在后台启动交易会话
        background_tasks.add_task(executor.start_execution)

        return {"message": "实时交易会话启动中", "status": "starting"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动交易会话失败: {str(e)}")


@router.post("/stop", response_model=TradingSessionSummaryResponse, summary="停止实时交易")
async def stop_trading_session():
    """
    停止当前实时交易会话

    关闭所有活跃头寸并生成会话摘要报告。
    """
    try:
        executor = get_trading_executor()
        summary = await executor.stop_execution()

        return TradingSessionSummaryResponse(
            session_id=summary.get("session_id", "unknown"),
            start_time=summary.get("start_time", ""),
            end_time=summary.get("end_time"),
            duration_seconds=summary.get("duration_seconds", 0.0),
            total_trades=summary.get("total_trades", 0),
            winning_trades=summary.get("winning_trades", 0),
            losing_trades=summary.get("losing_trades", 0),
            total_pnl=summary.get("total_pnl", 0.0),
            max_drawdown=summary.get("max_drawdown", 0.0),
            win_rate=summary.get("win_rate", 0.0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止交易会话失败: {str(e)}")


@router.get("/session/summary", response_model=TradingSessionSummaryResponse, summary="获取会话摘要")
async def get_session_summary():
    """
    获取当前交易会话的摘要信息

    包括交易统计、盈亏情况、胜率等关键指标。
    """
    try:
        executor = get_trading_executor()

        # 获取执行状态并构造摘要
        status = executor.get_execution_status()
        trading_status = status.get("trading_engine", {})

        # 模拟会话摘要（实际应该从会话历史中获取）
        return TradingSessionSummaryResponse(
            session_id=trading_status.get("session_id", "current"),
            start_time=datetime.now().isoformat(),  # 应该从实际会话开始时间获取
            end_time=None,  # 会话仍在运行
            duration_seconds=0.0,  # 应该计算实际持续时间
            total_trades=0,  # 应该从实际交易记录获取
            winning_trades=0,
            losing_trades=0,
            total_pnl=trading_status.get("total_pnl", 0.0),
            max_drawdown=trading_status.get("max_drawdown", 0.0),
            win_rate=0.0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话摘要失败: {str(e)}")


@router.get("/risk/metrics", summary="获取风险指标")
async def get_risk_metrics():
    """
    获取当前风险指标

    包括回撤、VaR、压力测试结果等。
    """
    try:
        executor = get_trading_executor()
        status = executor.get_execution_status()
        trading_status = status.get("trading_engine", {})

        return {
            "current_drawdown": trading_status.get("current_drawdown", 0.0),
            "daily_pnl": trading_status.get("daily_pnl", 0.0),
            "active_positions": trading_status.get("active_positions", 0),
            "risk_status": "normal" if trading_status.get("current_drawdown", 0.0) < 0.05 else "warning",
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取风险指标失败: {str(e)}")


@router.post("/strategies/add", summary="添加策略")
async def add_strategy(strategy_name: str = Query(..., description="策略名称")):
    """
    动态添加策略到实时执行器

    支持在运行时添加新的交易策略。
    """
    try:
        executor = get_trading_executor()

        # 根据策略名称创建策略实例
        from src.ml_strategy.strategy.decision_tree_trading_strategy import DecisionTreeTradingStrategy
        from src.ml_strategy.strategy.naive_bayes_trading_strategy import NaiveBayesTradingStrategy
        from src.ml_strategy.strategy.svm_trading_strategy import SVMTradingStrategy

        strategy_classes = {
            "SVMTradingStrategy": SVMTradingStrategy,
            "DecisionTreeTradingStrategy": DecisionTreeTradingStrategy,
            "NaiveBayesTradingStrategy": NaiveBayesTradingStrategy,
        }

        if strategy_name not in strategy_classes:
            raise HTTPException(status_code=400, detail=f"未知策略: {strategy_name}")

        strategy_class = strategy_classes[strategy_name]
        strategy = strategy_class()

        success = executor.add_strategy(strategy)

        if success:
            return {"message": f"策略 {strategy_name} 添加成功", "strategy_name": strategy_name}
        else:
            raise HTTPException(status_code=400, detail=f"添加策略失败: {strategy_name}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加策略失败: {str(e)}")


@router.delete("/strategies/{strategy_name}", summary="移除策略")
async def remove_strategy(strategy_name: str):
    """
    从实时执行器中移除策略

    支持在运行时移除交易策略。
    """
    try:
        executor = get_trading_executor()
        success = executor.remove_strategy(strategy_name)

        if success:
            return {"message": f"策略 {strategy_name} 移除成功", "strategy_name": strategy_name}
        else:
            raise HTTPException(status_code=404, detail=f"策略不存在: {strategy_name}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"移除策略失败: {str(e)}")
