"""
压力测试API

提供组合压力测试功能
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Body, Query
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


STRESS_TEST_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

router = APIRouter(
    prefix="/stress-test",
    tags=["Stress Test"],
    responses=STRESS_TEST_ROUTE_RESPONSES,
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


class StressTestRunResponse(BaseModel):
    """自定义压力测试响应"""

    portfolio_id: str = Field(..., description="执行压力测试的组合ID")
    scenarios_tested: int = Field(..., description="本次执行的压力测试场景数量")
    results: List[Dict[str, Any]] = Field(..., description="每个压力场景下的影响结果")
    recommendations: List[str] = Field(..., description="基于压力测试结果生成的风险建议")


class PredefinedScenarioResponse(BaseModel):
    """预定义压力测试场景"""

    id: str = Field(..., description="预定义场景ID")
    name: str = Field(..., description="预定义场景名称")
    description: str = Field(..., description="场景说明")
    shock_type: str = Field(..., description="冲击类型")
    severity: float = Field(..., description="冲击严重程度")
    duration_days: int = Field(..., description="冲击持续时间")


class PredefinedScenarioListResponse(BaseModel):
    """预定义压力测试场景列表"""

    scenarios: List[PredefinedScenarioResponse] = Field(..., description="可选的预定义压力测试场景列表")


class StressTestHistoryItem(BaseModel):
    """压力测试历史记录"""

    test_id: str = Field(..., description="历史压力测试记录ID")
    date: str = Field(..., description="执行日期")
    scenario: str = Field(..., description="执行的压力测试场景标识")
    impact: float = Field(..., description="压力测试估计冲击")
    passed: bool = Field(..., description="是否通过该次压力测试")


class StressTestHistoryResponse(BaseModel):
    """压力测试历史响应"""

    portfolio_id: str = Field(..., description="组合ID")
    tests: List[StressTestHistoryItem] = Field(..., description="历史压力测试记录列表")
    total: int = Field(..., description="历史记录总数")


STRESS_TEST_SCENARIO_BODY_EXAMPLES = {
    "two_scenarios_for_growth_portfolio": {
        "summary": "为成长型组合提交两个压力场景",
        "description": "通过请求体提交市场崩盘和流动性危机场景，组合ID和初始资金由查询参数传入。",
        "value": [
            {
                "name": "market_crash_2008",
                "shock_type": "price_drop",
                "severity": 0.5,
                "duration_days": 180,
            },
            {
                "name": "liquidity_crisis",
                "shock_type": "liquidity_crisis",
                "severity": 0.4,
                "duration_days": 30,
            },
        ],
    }
}

RUN_CUSTOM_STRESS_TEST_SUCCESS_RESPONSE = _success_response_spec(
    "自定义压力测试执行结果",
    {
        "portfolio_id": "growth_portfolio_alpha",
        "scenarios_tested": 2,
        "results": [
            {
                "scenario": "market_crash_2008",
                "shock_type": "price_drop",
                "severity": 0.5,
                "expected_impact": -0.25,
                "recovery_time_days": 180,
            }
        ],
        "recommendations": [
            "Consider reducing exposure to volatile assets",
            "Maintain higher cash reserves for liquidity",
            "Diversify across uncorrelated assets",
        ],
    },
)

PREDEFINED_SCENARIOS_SUCCESS_RESPONSE = _success_response_spec(
    "预定义压力测试场景列表",
    {
        "scenarios": [
            {
                "id": "market_crash_2008",
                "name": "2008金融危机",
                "description": "模拟2008年全球金融危机情景",
                "shock_type": "price_drop",
                "severity": 0.5,
                "duration_days": 180,
            }
        ]
    },
)

STRESS_TEST_HISTORY_SUCCESS_RESPONSE = _success_response_spec(
    "组合压力测试历史记录",
    {
        "portfolio_id": "growth_portfolio_alpha",
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
    },
)


@router.post(
    "/run",
    response_model=StressTestRunResponse,
    summary="Run Custom Stress Test",
    description="对指定组合执行自定义压力测试场景，返回每个场景的预估冲击和风险建议。",
    responses=RUN_CUSTOM_STRESS_TEST_SUCCESS_RESPONSE,
)
async def run_custom_stress_test(
    portfolio_id: str = Query(..., description="需要执行压力测试的组合ID"),
    scenarios: List[StressTestScenario] = Body(..., openapi_examples=STRESS_TEST_SCENARIO_BODY_EXAMPLES),
    initial_capital: float = Query(1000000.0, ge=0, description="组合压力测试采用的初始资金"),
) -> StressTestRunResponse:
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


@router.get(
    "/scenarios",
    response_model=PredefinedScenarioListResponse,
    summary="Get Predefined Scenarios",
    description="返回系统内置的压力测试场景模板，供前端快速选择常见极端市场情景。",
    responses=PREDEFINED_SCENARIOS_SUCCESS_RESPONSE,
)
async def get_predefined_scenarios() -> PredefinedScenarioListResponse:
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


@router.get(
    "/history",
    response_model=StressTestHistoryResponse,
    summary="Get Stress Test History",
    description="按组合ID查询近期压力测试历史，返回测试场景、冲击结果和通过状态。",
    responses=STRESS_TEST_HISTORY_SUCCESS_RESPONSE,
)
async def get_stress_test_history(
    portfolio_id: str = Query(..., description="需要查询历史记录的组合ID"),
    limit: int = Query(10, ge=1, le=100, description="返回最近多少条压力测试历史记录"),
) -> StressTestHistoryResponse:
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
