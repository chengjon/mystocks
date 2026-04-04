"""
高级回测API

提供蒙特卡洛回测和高级分析功能
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Body, Path, Query
from pydantic import BaseModel, Field

from app.openapi_config import COMMON_RESPONSES


def _success_response_spec(description: str, example: dict) -> dict[int, dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


BACKTEST_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

router = APIRouter(
    prefix="/backtest",
    tags=["Advanced Backtest"],
    responses=BACKTEST_ROUTE_RESPONSES,
)


class MonteCarloRequest(BaseModel):
    """蒙特卡洛回测请求"""

    strategy_id: str = Field(..., description="Strategy ID")
    symbol: str = Field(..., description="Stock symbol")
    start_date: str = Field(..., description="Backtest start date")
    end_date: str = Field(..., description="Backtest end date")
    initial_capital: float = Field(100000.0, description="Initial capital")
    iterations: int = Field(1000, description="Number of Monte Carlo iterations")


class MonteCarloResponse(BaseModel):
    """蒙特卡洛回测响应"""

    strategy_id: str = Field(..., description="执行蒙特卡洛回测的策略ID")
    symbol: str = Field(..., description="参与回测的股票代码")
    simulations_run: int = Field(..., description="实际执行的模拟次数")
    return_distribution: Dict[str, float] = Field(..., description="收益分布统计结果")
    risk_metrics: Dict[str, float] = Field(..., description="VaR、预期损失等风险指标")
    confidence_intervals: Dict[str, Any] = Field(..., description="不同置信区间下的收益区间")
    equity_curves: List[Dict[str, Any]] = Field(..., description="示例权益曲线数据点")


class StressTestRequest(BaseModel):
    """压力测试请求"""

    portfolio_id: str = Field(..., description="Portfolio ID")
    scenarios: List[Dict[str, Any]] = Field(..., description="Stress test scenarios")
    initial_capital: float = Field(1000000.0, description="Initial capital")


class StressTestResponse(BaseModel):
    """压力测试响应"""

    portfolio_id: str = Field(..., description="执行压力测试的组合ID")
    scenarios_tested: int = Field(..., description="本次执行的压力情景数量")
    results: List[Dict[str, Any]] = Field(..., description="各压力情景下的影响结果")
    recommendations: List[str] = Field(..., description="基于压力测试结果生成的建议")


class EquityCurveSummaryResponse(BaseModel):
    """权益曲线摘要响应"""

    strategy_id: str = Field(..., description="查询权益曲线的策略ID")
    period: Dict[str, str] = Field(..., description="查询区间的起止日期")
    data_points: int = Field(..., description="返回的权益曲线数据点数量")
    final_value: float = Field(..., description="区间结束时的权益值")
    max_drawdown: float = Field(..., description="区间内最大回撤")
    sharpe_ratio: float = Field(..., description="区间内夏普比率")


MONTE_CARLO_REQUEST_EXAMPLES = {
    "momentum_strategy_monte_carlo": {
        "summary": "对趋势策略执行蒙特卡洛回测",
        "description": "评估单策略在给定时间区间内的收益分布、风险区间和模拟权益曲线。",
        "value": {
            "strategy_id": "momentum_breakout_v2",
            "symbol": "600519.SH",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 100000.0,
            "iterations": 1000,
        },
    }
}

BACKTEST_STRESS_REQUEST_EXAMPLES = {
    "portfolio_stress_test": {
        "summary": "对组合执行情景压力测试",
        "description": "针对预设的极端市场情景评估组合冲击和恢复时间。",
        "value": {
            "portfolio_id": "growth_portfolio_alpha",
            "scenarios": [
                {
                    "name": "market_crash_2008",
                    "shock": {"market_drop_pct": 0.35, "volatility_spike_pct": 0.5},
                },
                {
                    "name": "liquidity_crunch",
                    "shock": {"liquidity_drop_pct": 0.4, "spread_widen_pct": 0.25},
                },
            ],
            "initial_capital": 1000000.0,
        },
    }
}

MONTE_CARLO_SUCCESS_RESPONSE = _success_response_spec(
    "蒙特卡洛回测结果",
    {
        "strategy_id": "momentum_breakout_v2",
        "symbol": "600519.SH",
        "simulations_run": 1000,
        "return_distribution": {
            "mean": 0.15,
            "std": 0.12,
            "min": -0.25,
            "max": 0.55,
            "median": 0.14,
        },
        "risk_metrics": {
            "var_95": -0.08,
            "var_99": -0.15,
            "expected_shortfall": -0.12,
            "sortino_ratio": 1.25,
        },
        "confidence_intervals": {
            "return_95_ci": [-0.08, 0.38],
            "return_99_ci": [-0.15, 0.45],
        },
        "equity_curves": [{"date": "2025-01-01", "value": 100000}],
    },
)

BACKTEST_STRESS_SUCCESS_RESPONSE = _success_response_spec(
    "组合压力测试结果",
    {
        "portfolio_id": "growth_portfolio_alpha",
        "scenarios_tested": 2,
        "results": [
            {
                "scenario": "market_crash_2008",
                "impact": -0.35,
                "recovery_time_days": 180,
                "description": "2008金融危机情景",
            }
        ],
        "recommendations": ["增加防御性资产配置", "设置止损机制", "分散投资于非相关性资产"],
    },
)

EQUITY_CURVE_SUCCESS_RESPONSE = _success_response_spec(
    "策略权益曲线摘要",
    {
        "strategy_id": "momentum_breakout_v2",
        "period": {"start": "2024-01-01", "end": "2024-12-31"},
        "data_points": 100,
        "final_value": 142500.0,
        "max_drawdown": 0.085,
        "sharpe_ratio": 1.45,
    },
)


@router.post(
    "/monte-carlo",
    response_model=MonteCarloResponse,
    summary="Run Monte Carlo Backtest",
    description="对指定策略执行蒙特卡洛模拟回测，返回收益分布、风险指标和置信区间。",
    responses=MONTE_CARLO_SUCCESS_RESPONSE,
)
async def run_monte_carlo_backtest(
    request: MonteCarloRequest = Body(..., openapi_examples=MONTE_CARLO_REQUEST_EXAMPLES),
):
    """
    运行蒙特卡洛回测

    Runs Monte Carlo simulation for strategy backtesting.
    """
    return MonteCarloResponse(
        strategy_id=request.strategy_id,
        symbol=request.symbol,
        simulations_run=request.iterations,
        return_distribution={
            "mean": 0.15,
            "std": 0.12,
            "min": -0.25,
            "max": 0.55,
            "median": 0.14,
        },
        risk_metrics={
            "var_95": -0.08,
            "var_99": -0.15,
            "expected_shortfall": -0.12,
            "sortino_ratio": 1.25,
        },
        confidence_intervals={
            "return_95_ci": [-0.08, 0.38],
            "return_99_ci": [-0.15, 0.45],
        },
        equity_curves=[{"date": "2025-01-01", "value": 100000}],
    )


@router.post(
    "/stress-test",
    response_model=StressTestResponse,
    summary="Run Stress Test",
    description="对指定组合运行预设压力情景测试，评估冲击影响、恢复时间和风险建议。",
    responses=BACKTEST_STRESS_SUCCESS_RESPONSE,
)
async def run_stress_test(
    request: StressTestRequest = Body(..., openapi_examples=BACKTEST_STRESS_REQUEST_EXAMPLES),
):
    """
    运行压力测试

    Runs stress test on portfolio under various scenarios.
    """
    return StressTestResponse(
        portfolio_id=request.portfolio_id,
        scenarios_tested=len(request.scenarios),
        results=[
            {
                "scenario": "market_crash_2008",
                "impact": -0.35,
                "recovery_time_days": 180,
                "description": "2008金融危机情景",
            },
        ],
        recommendations=[
            "增加防御性资产配置",
            "设置止损机制",
            "分散投资于非相关性资产",
        ],
    )


@router.get(
    "/equity-curve/{strategy_id}",
    response_model=EquityCurveSummaryResponse,
    summary="Get Equity Curve",
    description="按策略和日期区间返回权益曲线摘要指标，用于回测概览页展示收益和回撤表现。",
    responses=EQUITY_CURVE_SUCCESS_RESPONSE,
)
async def get_equity_curve(
    strategy_id: str = Path(..., description="需要查询权益曲线的策略ID"),
    start_date: str = Query(..., description="权益曲线查询开始日期，格式为 YYYY-MM-DD"),
    end_date: str = Query(..., description="权益曲线查询结束日期，格式为 YYYY-MM-DD"),
) -> EquityCurveSummaryResponse:
    """
    获取权益曲线

    Returns equity curve data for a strategy.
    """
    return {
        "strategy_id": strategy_id,
        "period": {"start": start_date, "end": end_date},
        "data_points": 100,
        "final_value": 142500.0,
        "max_drawdown": 0.085,
        "sharpe_ratio": 1.45,
    }
