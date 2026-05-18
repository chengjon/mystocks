"""Monitoring analysis route response examples and OpenAPI response specs."""

from typing import Any, Dict

from app.openapi_config import COMMON_RESPONSES


def _success_response_spec(description: str, message: str, data: Any) -> Dict[int, Dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "code": 200,
                        "message": message,
                        "data": data,
                        "timestamp": "2026-04-04T01:30:00Z",
                        "request_id": "req_monitoring_analysis_example",
                    }
                }
            },
        }
    }


MONITORING_ANALYSIS_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

CALCULATE_HEALTH_REQUEST_EXAMPLES = {
    "single_stock_health_score": {
        "summary": "计算单只股票健康度",
        "description": "对单只股票输入最新价量数据，返回综合评分、雷达分和风险指标。",
        "value": {
            "stock_code": "600519",
            "close": 1688.0,
            "high": 1699.8,
            "low": 1666.2,
            "open": 1672.5,
            "volume": 3520000,
            "market_regime": "bull",
        },
    }
}

BATCH_CALCULATE_HEALTH_REQUEST_EXAMPLES = {
    "watchlist_batch_health_score": {
        "summary": "批量计算清单健康度",
        "description": "批量提交两只股票的价格信息，并要求返回高级风险指标。",
        "value": {
            "stocks": [
                {
                    "stock_code": "600519",
                    "close": 1688.0,
                    "high": 1699.8,
                    "low": 1666.2,
                    "open": 1672.5,
                    "volume": 3520000,
                    "market_regime": "bull",
                },
                {
                    "stock_code": "000001",
                    "close": 12.38,
                    "high": 12.52,
                    "low": 12.1,
                    "open": 12.2,
                    "volume": 88400000,
                    "market_regime": "choppy",
                },
            ],
            "include_risk_metrics": True,
        },
    }
}

CALCULATE_HEALTH_SUCCESS_RESPONSE = _success_response_spec(
    "单只股票健康度评分结果",
    "计算成功",
    {
        "stock_code": "600519",
        "score_date": "2026-04-04",
        "total_score": 87.3,
        "radar_scores": {
            "trend": 88.0,
            "technical": 84.5,
            "momentum": 89.1,
            "volatility": 78.4,
            "risk": 91.2,
        },
        "market_regime": "bull",
        "calculation_time_ms": 12.4,
        "calculation_mode": "AUTO",
        "sortino_ratio": 1.82,
        "calmar_ratio": 1.36,
        "max_drawdown": 0.083,
        "max_drawdown_duration": 11,
        "downside_deviation": 0.124,
    },
)

BATCH_CALCULATE_HEALTH_SUCCESS_RESPONSE = _success_response_spec(
    "批量股票健康度评分结果",
    "批量计算成功: 2 只股票, 引擎: AUTO, 耗时: 18.60ms",
    [
        {
            "stock_code": "600519",
            "score_date": "2026-04-04",
            "total_score": 87.3,
            "radar_scores": {
                "trend": 88.0,
                "technical": 84.5,
                "momentum": 89.1,
                "volatility": 78.4,
                "risk": 91.2,
            },
            "market_regime": "bull",
            "calculation_time_ms": 12.4,
            "calculation_mode": "AUTO",
            "sortino_ratio": 1.82,
            "calmar_ratio": 1.36,
            "max_drawdown": 0.083,
            "max_drawdown_duration": 11,
            "downside_deviation": 0.124,
        },
        {
            "stock_code": "000001",
            "score_date": "2026-04-04",
            "total_score": 72.8,
            "radar_scores": {
                "trend": 70.5,
                "technical": 74.0,
                "momentum": 71.6,
                "volatility": 69.1,
                "risk": 78.8,
            },
            "market_regime": "choppy",
            "calculation_time_ms": 6.2,
            "calculation_mode": "AUTO",
            "sortino_ratio": 1.11,
            "calmar_ratio": 0.88,
            "max_drawdown": 0.126,
            "max_drawdown_duration": 18,
            "downside_deviation": 0.173,
        },
    ],
)

HEALTH_HISTORY_SUCCESS_RESPONSE = _success_response_spec(
    "股票健康度历史评分列表",
    "获取历史评分成功",
    [
        {
            "stock_code": "600519",
            "score_date": "2026-04-03",
            "total_score": 85.1,
            "radar_scores": {
                "trend": 84.0,
                "technical": 82.3,
                "momentum": 86.2,
                "volatility": 77.5,
                "risk": 90.4,
            },
            "market_regime": "bull",
            "calculation_time_ms": 0,
            "calculation_mode": "CPU",
        }
    ],
)

PORTFOLIO_ANALYSIS_SUCCESS_RESPONSE = _success_response_spec(
    "自选组合健康度分析结果",
    "组合分析成功",
    {
        "watchlist_id": 8,
        "watchlist_name": "核心持仓",
        "analysis_date": "2026-04-04",
        "stocks_count": 3,
        "total_score": {"average": 79.2, "min": 68.4, "max": 87.3},
        "radar_averages": {
            "trend": 80.2,
            "technical": 78.4,
            "momentum": 81.7,
            "volatility": 73.1,
            "risk": 82.8,
        },
        "risk_metrics": {
            "avg_sortino_ratio": 1.42,
            "max_drawdown_min": 0.118,
        },
        "stocks": [
            {
                "stock_code": "600519",
                "score_date": "2026-04-04",
                "total_score": 87.3,
                "radar_scores": {
                    "trend": 88.0,
                    "technical": 84.5,
                    "momentum": 89.1,
                    "volatility": 78.4,
                    "risk": 91.2,
                },
                "market_regime": "bull",
                "calculation_time_ms": 12.4,
                "calculation_mode": "AUTO",
            }
        ],
    },
)

MARKET_REGIME_SUCCESS_RESPONSE = _success_response_spec(
    "当前市场体制识别结果",
    "市场体制识别成功",
    {
        "regime": "bull",
        "confidence": 0.82,
        "composite_score": 41.6,
        "ma_slope_score": 18.2,
        "breadth_score": 11.4,
        "volatility_score": 12.0,
        "details": {
            "index_code": "000001.SH",
            "sample_days": 100,
        },
    },
)

ENGINE_STATUS_SUCCESS_RESPONSE = _success_response_spec(
    "监控分析计算引擎状态",
    "获取引擎状态成功",
    {
        "default_engine": "AUTO",
        "gpu_available": False,
        "supported_engines": ["AUTO", "CPU", "GPU"],
        "last_health_check": "2026-04-04T01:30:00Z",
    },
)
