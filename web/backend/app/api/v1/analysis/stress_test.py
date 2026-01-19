"""
压力测试API

提供组合压力测试功能
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List

router = APIRouter(
    prefix="/stress-test",
    tags=["Stress Test"],
)


class StressTestScenario(BaseModel):
    """压力测试场景"""

    name: str = Field(..., description="Scenario name")
    shock_type: str = Field(
        ...,
        description="Type of shock (price_drop, volatility_spike, liquidity_crisis)",
    )
    severity: float = Field(..., description="Severity factor (0-1)")
    duration_days: int = Field(..., description="Expected duration in days")


@router.post("/run", summary="Run Custom Stress Test")
async def run_custom_stress_test(
    portfolio_id: str,
    scenarios: List[StressTestScenario],
    initial_capital: float = 1000000.0,
):
    """
    运行自定义压力测试

    Runs stress test with custom scenarios on a portfolio.
    """
    return {
        "portfolio_id": portfolio_id,
        "scenarios_tested": len(scenarios),
        "results": [
            {
                "scenario": s.name,
                "shock_type": s.shock_type,
                "severity": s.severity,
                "expected_impact": -s.severity * 0.5,
                "recovery_time_days": s.duration_days,
            }
            for s in scenarios
        ],
        "recommendations": [
            "Consider reducing exposure to volatile assets",
            "Maintain higher cash reserves for liquidity",
            "Diversify across uncorrelated assets",
        ],
    }


@router.get("/scenarios", summary="Get Predefined Scenarios")
async def get_predefined_scenarios():
    """
    获取预定义压力测试场景

    Returns list of predefined stress test scenarios.
    """
    return {
        "scenarios": [
            {
                "id": "market_crash_2008",
                "name": "2008金融危机",
                "description": "模拟2008年全球金融危机情景",
                "shock_type": "price_drop",
                "severity": 0.5,
                "duration_days": 180,
            },
            {
                "id": "flash_crash",
                "name": "闪电崩盘",
                "description": "模拟短期剧烈波动",
                "shock_type": "volatility_spike",
                "severity": 0.3,
                "duration_days": 5,
            },
            {
                "id": "liquidity_crisis",
                "name": "流动性危机",
                "description": "模拟市场流动性枯竭",
                "shock_type": "liquidity_crisis",
                "severity": 0.4,
                "duration_days": 30,
            },
        ]
    }


@router.get("/history", summary="Get Stress Test History")
async def get_stress_test_history(portfolio_id: str, limit: int = 10):
    """
    获取压力测试历史

    Returns historical stress test results for a portfolio.
    """
    return {
        "portfolio_id": portfolio_id,
        "tests": [
            {
                "test_id": "test_001",
                "date": "2025-01-15",
                "scenario": "market_crash_2008",
                "impact": -0.35,
                "passed": True,
            }
        ],
        "total": 1,
    }
