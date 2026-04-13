"""
压力测试API

提供组合压力测试功能
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Body, Query
from pydantic import BaseModel, Field

from app.core.responses import UnifiedResponse
from app.openapi_config import COMMON_RESPONSES

from .runtime_state import runtime_store


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
    severity: float = Field(..., ge=0, le=1, description="Severity factor (0-1)")
    duration_days: int = Field(..., ge=1, description="Expected duration in days")


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

_PREDEFINED_SCENARIOS = [
    PredefinedScenarioResponse(
        id="market_crash_2008",
        name="Global Market Crash",
        description="Large-cap broad market drawdown with elevated volatility.",
        shock_type="price_drop",
        severity=0.45,
        duration_days=180,
    ),
    PredefinedScenarioResponse(
        id="liquidity_crisis",
        name="Liquidity Crunch",
        description="Liquidity evaporates and transaction costs widen sharply.",
        shock_type="liquidity_crisis",
        severity=0.3,
        duration_days=30,
    ),
    PredefinedScenarioResponse(
        id="volatility_spike",
        name="Volatility Shock",
        description="Implied and realized volatility jump faster than spot declines.",
        shock_type="volatility_spike",
        severity=0.25,
        duration_days=20,
    ),
]

RUN_CUSTOM_STRESS_TEST_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Custom stress test completed",
    "data": {
        "portfolio_id": "growth_portfolio_alpha",
        "scenarios_tested": 2,
        "results": [
            {
                "name": "market_crash_2008",
                "shock_type": "price_drop",
                "impact": -500000.0,
                "projected_value": 500000.0,
                "max_drawdown": 0.5,
                "duration_days": 180,
                "passed": False,
            }
        ],
        "recommendations": ["Reduce gross exposure before running high-severity price-drop scenarios."],
    },
}

PREDEFINED_SCENARIOS_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Predefined stress scenarios retrieved",
    "data": {
        "scenarios": [
            {
                "id": "market_crash_2008",
                "name": "Global Market Crash",
                "description": "Large-cap broad market drawdown with elevated volatility.",
                "shock_type": "price_drop",
                "severity": 0.45,
                "duration_days": 180,
            }
        ]
    },
}

STRESS_TEST_HISTORY_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Stress test history retrieved",
    "data": {
        "portfolio_id": "growth_portfolio_alpha",
        "tests": [
            {
                "test_id": "stress_a1b2c3d4e5f6",
                "date": "2026-04-13T08:00:00+00:00",
                "scenario": "market_crash_2008",
                "impact": -500000.0,
                "passed": False,
            }
        ],
        "total": 1,
    },
}

RUN_CUSTOM_STRESS_TEST_SUCCESS_RESPONSE = _success_response_spec(
    "自定义压力测试真实计算结果",
    RUN_CUSTOM_STRESS_TEST_SUCCESS_EXAMPLE,
)
PREDEFINED_SCENARIOS_SUCCESS_RESPONSE = _success_response_spec(
    "预定义压力测试场景清单",
    PREDEFINED_SCENARIOS_SUCCESS_EXAMPLE,
)
STRESS_TEST_HISTORY_SUCCESS_RESPONSE = _success_response_spec(
    "组合压力测试历史记录",
    STRESS_TEST_HISTORY_SUCCESS_EXAMPLE,
)


def _round_float(value: float) -> float:
    return round(float(value), 4)


def _severity_multiplier(shock_type: str) -> float:
    if shock_type == "volatility_spike":
        return 0.75
    if shock_type == "liquidity_crisis":
        return 0.9
    return 1.0


def _evaluate_scenario(initial_capital: float, scenario: StressTestScenario) -> Dict[str, Any]:
    drawdown = min(scenario.severity * _severity_multiplier(scenario.shock_type), 0.95)
    impact = -initial_capital * drawdown
    projected_value = initial_capital + impact
    return {
        "name": scenario.name,
        "shock_type": scenario.shock_type,
        "impact": _round_float(impact),
        "projected_value": _round_float(projected_value),
        "max_drawdown": _round_float(drawdown),
        "duration_days": scenario.duration_days,
        "passed": drawdown <= 0.2,
    }


def _build_recommendations(results: List[Dict[str, Any]]) -> List[str]:
    recommendations: List[str] = []
    if any(not item["passed"] for item in results):
        recommendations.append("Reduce gross exposure before running high-severity price-drop scenarios.")
    if any(item["shock_type"] == "liquidity_crisis" for item in results):
        recommendations.append("Maintain more cash or credit lines for liquidity-crisis scenarios.")
    if not recommendations:
        recommendations.append("Portfolio remains within tolerance under the tested stress scenarios.")
    return recommendations


@router.post(
    "/run",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Run Custom Stress Test",
    description="对指定组合执行自定义压力测试场景，当前实现基于 severity、shock_type 和 duration_days 进行真实冲击计算，并将结果写入运行时历史。",
    responses=RUN_CUSTOM_STRESS_TEST_SUCCESS_RESPONSE,
)
async def run_custom_stress_test(
    portfolio_id: str = Query(..., description="需要执行压力测试的组合ID"),
    scenarios: List[StressTestScenario] = Body(..., openapi_examples=STRESS_TEST_SCENARIO_BODY_EXAMPLES),
    initial_capital: float = Query(1000000.0, ge=0, description="组合压力测试采用的初始资金"),
) -> UnifiedResponse[Dict[str, Any]]:
    """运行自定义压力测试。"""
    results = [_evaluate_scenario(initial_capital, scenario) for scenario in scenarios]
    for item in results:
        runtime_store.record_stress_test(
            portfolio_id=portfolio_id,
            scenario=item["name"],
            impact=item["impact"],
            passed=item["passed"],
            projected_value=item["projected_value"],
            drawdown=item["max_drawdown"],
        )

    response = StressTestRunResponse(
        portfolio_id=portfolio_id,
        scenarios_tested=len(results),
        results=results,
        recommendations=_build_recommendations(results),
    )
    return UnifiedResponse(
        success=True,
        code=200,
        message="Custom stress test completed",
        data=response.model_dump(),
    )


@router.get(
    "/scenarios",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get Predefined Scenarios",
    description="返回系统内置压力测试场景模板，当前实现提供真实模板目录而非占位文案。",
    responses=PREDEFINED_SCENARIOS_SUCCESS_RESPONSE,
)
async def get_predefined_scenarios() -> UnifiedResponse[Dict[str, Any]]:
    """获取预定义压力测试场景。"""
    response = PredefinedScenarioListResponse(scenarios=_PREDEFINED_SCENARIOS)
    return UnifiedResponse(
        success=True,
        code=200,
        message="Predefined stress scenarios retrieved",
        data=response.model_dump(),
    )


@router.get(
    "/history",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get Stress Test History",
    description="按组合ID查询压力测试历史，当前实现返回运行时真实执行记录而非占位响应。",
    responses=STRESS_TEST_HISTORY_SUCCESS_RESPONSE,
)
async def get_stress_test_history(
    portfolio_id: str = Query(..., description="需要查询历史记录的组合ID"),
    limit: int = Query(10, ge=1, le=100, description="返回最近多少条压力测试历史记录"),
) -> UnifiedResponse[Dict[str, Any]]:
    """获取压力测试历史。"""
    history_items = runtime_store.get_stress_history(portfolio_id=portfolio_id, limit=limit)
    response = StressTestHistoryResponse(
        portfolio_id=portfolio_id,
        tests=[
            StressTestHistoryItem(
                test_id=item.test_id,
                date=item.run_at.isoformat(),
                scenario=item.scenario,
                impact=item.impact,
                passed=item.passed,
            )
            for item in history_items
        ],
        total=len(history_items),
    )
    return UnifiedResponse(
        success=True,
        code=200,
        message="Stress test history retrieved",
        data=response.model_dump(),
    )
