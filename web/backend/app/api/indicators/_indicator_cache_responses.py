"""Response specs and models extracted from indicator_cache."""

from typing import Dict, List, Union
from datetime import datetime

from pydantic import BaseModel, Field, constr, field_validator

from app.schemas.indicator_request import IndicatorCalculateRequest

def _response_spec(status_code: int, description: str, example: dict) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


INDICATOR_CACHE_STATS_RESPONSES = {
    **_response_spec(
        200,
        "指标缓存统计结果",
        {
            "success": True,
            "data": {
                "size": 128,
                "max_size": 1000,
                "ttl": 300,
                "hit_rate": 0.82,
            },
            "message": "缓存统计信息获取成功",
            "timestamp": "2026-04-05T08:00:00Z",
            "request_id": "req-cache-stats-001",
        },
    ),
    **_response_spec(
        500,
        "指标缓存统计查询失败",
        {
            "detail": "获取缓存统计失败: Redis connection refused",
            "error_code": "CACHE_STATS_RETRIEVAL_FAILED",
        },
    ),
}

INDICATOR_METADATA_EXAMPLE = {
    "abbreviation": "SMA",
    "full_name": "Simple Moving Average",
    "chinese_name": "简单移动平均线",
    "category": "trend",
    "description": "计算指定周期内收盘价的算术平均值，用于识别价格趋势方向。",
    "panel_type": "overlay",
    "parameters": [
        {
            "name": "timeperiod",
            "type": "int",
            "default": 20,
            "min": 2,
            "max": 250,
            "description": "均线周期，常用于 A 股、港股与股指期货的趋势观察。",
        }
    ],
    "outputs": [
        {
            "name": "sma",
            "description": "简单移动平均值",
        }
    ],
    "reference_lines": None,
    "min_data_points_formula": "timeperiod",
}

INDICATOR_REGISTRY_RESPONSES = _response_spec(
    200,
    "指标注册表查询成功",
    {
        "total_count": 2,
        "categories": {
            "trend": 1,
            "momentum": 1,
            "volatility": 0,
            "volume": 0,
            "candlestick": 0,
        },
        "indicators": [
            INDICATOR_METADATA_EXAMPLE,
            {
                "abbreviation": "RSI",
                "full_name": "Relative Strength Index",
                "chinese_name": "相对强弱指标",
                "category": "momentum",
                "description": "衡量价格涨跌强弱，适合观察超买超卖区间。",
                "panel_type": "oscillator",
                "parameters": [
                    {
                        "name": "timeperiod",
                        "type": "int",
                        "default": 14,
                        "min": 2,
                        "max": 100,
                        "description": "RSI 计算周期。",
                    }
                ],
                "outputs": [
                    {
                        "name": "rsi",
                        "description": "RSI 指标值",
                    }
                ],
                "reference_lines": [30.0, 70.0],
                "min_data_points_formula": "timeperiod + 1",
            },
        ],
    },
)

INDICATOR_CATEGORY_RESPONSES = _response_spec(
    200,
    "分类指标查询成功",
    [
        INDICATOR_METADATA_EXAMPLE,
        {
            "abbreviation": "EMA",
            "full_name": "Exponential Moving Average",
            "chinese_name": "指数移动平均线",
            "category": "trend",
            "description": "对最新价格赋予更高权重，适合趋势跟踪与信号平滑。",
            "panel_type": "overlay",
            "parameters": [
                {
                    "name": "timeperiod",
                    "type": "int",
                    "default": 12,
                    "min": 2,
                    "max": 250,
                    "description": "EMA 计算周期。",
                }
            ],
            "outputs": [
                {
                    "name": "ema",
                    "description": "指数移动平均值",
                }
            ],
            "reference_lines": None,
            "min_data_points_formula": "timeperiod",
        },
    ],
)

INDICATOR_CACHE_CLEAR_RESPONSES = _response_spec(
    200,
    "指标缓存清理成功",
    {
        "success": True,
        "data": {
            "cleared_count": "全部",
        },
        "message": "缓存清理完成，已清理全部",
        "timestamp": "2026-04-07T09:30:00Z",
        "request_id": "req-indicator-cache-clear-001",
    },
)

INDICATOR_CATEGORY_PATH_DESCRIPTION = "指标分类，可选值为 trend、momentum、volatility、volume 或 candlestick。"

INDICATOR_CALCULATE_REQUEST_EXAMPLE = {
    "symbol": "600519.SH",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "indicators": [
        {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
        {"abbreviation": "RSI", "parameters": {"timeperiod": 14}},
    ],
    "use_cache": True,
}

INDICATOR_CALCULATE_BATCH_REQUEST_EXAMPLE = {
    "calculations": [
        {
            "symbol": "600519.SH",
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "indicators": [{"abbreviation": "MACD", "parameters": {"fastperiod": 12, "slowperiod": 26}}],
            "use_cache": True,
        },
        {
            "symbol": "000300.SH",
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "indicators": [{"abbreviation": "ATR", "parameters": {"timeperiod": 14}}],
            "use_cache": True,
        },
    ]
}

INDICATOR_CALCULATE_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "symbol": "600519.SH",
        "symbol_name": "贵州茅台",
        "start_date": "2024-01-01",
        "end_date": "2024-01-10",
        "ohlcv": {
            "dates": ["2024-01-02", "2024-01-03", "2024-01-04"],
            "open": [1680.5, 1695.2, 1710.0],
            "high": [1705.6, 1712.8, 1726.4],
            "low": [1672.1, 1688.0, 1701.7],
            "close": [1698.4, 1708.6, 1721.3],
            "volume": [4521300, 4876500, 4332100],
            "turnover": [7684521000.0, 8243105600.0, 7452013300.0],
        },
        "indicators": [
            {
                "abbreviation": "SMA",
                "parameters": {"timeperiod": 20},
                "outputs": [
                    {
                        "output_name": "sma",
                        "values": [None, None, 1709.43],
                        "display_name": "SMA(20)",
                    }
                ],
                "panel_type": "overlay",
                "reference_lines": None,
                "error": None,
                "success": True,
            },
            {
                "abbreviation": "RSI",
                "parameters": {"timeperiod": 14},
                "outputs": [
                    {
                        "output_name": "rsi",
                        "values": [None, None, 61.82],
                        "display_name": "RSI(14)",
                    }
                ],
                "panel_type": "oscillator",
                "reference_lines": [30.0, 70.0],
                "error": None,
                "success": True,
            },
        ],
        "calculation_time_ms": 42.18,
        "cached": False,
        "statistics": {
            "total_indicators": 2,
            "successful_calculations": 2,
            "failed_calculations": 0,
            "data_points": 3,
            "date_range_days": 9,
        },
    },
    "message": "技术指标计算成功，共2/2个指标计算完成",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-indicator-calc-001",
}

INDICATOR_CALCULATE_BATCH_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "batch_statistics": {
            "total_calculations": 2,
            "successful_calculations": 2,
            "failed_calculations": 0,
            "total_indicators": 2,
            "calculation_time_ms": 96.44,
            "average_time_per_calculation": 48.22,
        },
        "results": [
            {
                "symbol": "600519.SH",
                "start_date": "2024-01-01",
                "end_date": "2024-06-30",
                "success": True,
                "data": {
                    "symbol": "600519.SH",
                    "symbol_name": "贵州茅台",
                    "indicators_count": 1,
                    "data_points": 120,
                    "results": {
                        "MACD": {
                            "parameters": {"fastperiod": 12, "slowperiod": 26},
                            "panel_type": "oscillator",
                            "reference_lines": [0.0],
                            "values": {
                                "macd": [0.14, 0.18, 0.22],
                                "macdsignal": [0.09, 0.12, 0.16],
                                "macdhist": [0.05, 0.06, 0.06],
                            },
                        }
                    },
                },
            },
            {
                "symbol": "000300.SH",
                "start_date": "2024-01-01",
                "end_date": "2024-06-30",
                "success": True,
                "data": {
                    "symbol": "000300.SH",
                    "symbol_name": "沪深300",
                    "indicators_count": 1,
                    "data_points": 120,
                    "results": {
                        "ATR": {
                            "parameters": {"timeperiod": 14},
                            "panel_type": "oscillator",
                            "reference_lines": None,
                            "values": {"atr": [41.2, 42.8, 40.9]},
                        }
                    },
                },
            },
        ],
    },
    "message": "批量计算完成，2/2个请求成功",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-indicator-batch-calc-001",
}

INDICATOR_CALCULATE_RESPONSES = {
    **_response_spec(200, "技术指标计算成功", INDICATOR_CALCULATE_RESPONSE_EXAMPLE),
    **_response_spec(
        404,
        "查询范围内未找到可用 OHLCV 数据",
        {
            "detail": "股票数据不存在: 查询条件",
            "error_code": "RESOURCE_NOT_FOUND",
        },
    ),
    **_response_spec(
        500,
        "技术指标计算失败",
        {
            "detail": "计算指标时发生错误: 指标计算引擎异常",
            "error_code": "INDICATOR_CALCULATION_ERROR",
        },
    ),
}

INDICATOR_CALCULATE_BATCH_RESPONSES = {
    **_response_spec(200, "批量技术指标计算成功", INDICATOR_CALCULATE_BATCH_RESPONSE_EXAMPLE),
    **_response_spec(
        500,
        "批量技术指标计算失败",
        {
            "detail": "批量计算失败: BATCH_CALCULATION_FAILED",
            "error_code": "BATCH_CALCULATION_FAILED",
        },
    ),
}


class IndicatorCalculateBatchRequest(BaseModel):
    """批量技术指标计算请求"""

    calculations: List[IndicatorCalculateRequest] = Field(
        ..., min_length=1, max_length=10, description="批量计算请求列表，最多10个"
    )

    @field_validator("calculations")
    @classmethod
    def validate_calculations(cls, v):
        """验证批量计算请求"""
        if not v:
            raise ValueError("计算请求列表不能为空")

        # 检查重复的symbol+date范围组合
        combinations = set()
        for calc in v:
            combo = f"{calc.symbol}_{calc.start_date}_{calc.end_date}"
            if combo in combinations:
                raise ValueError(f"存在重复的计算请求: {combo}")
            combinations.add(combo)

        return v


class IndicatorOptimizationRequest(BaseModel):
    """技术指标参数优化请求"""

    symbol: constr(min_length=1, max_length=20) = Field(..., description="股票代码")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    indicator_abbr: constr(min_length=1, max_length=10) = Field(..., description="指标简称")
    parameter_ranges: Dict[str, List[Union[int, float]]] = Field(..., description="参数范围")
    optimization_target: str = Field(
        "profit", pattern="^(profit|sharpe|max_drawdown|win_rate)$", description="优化目标"
    )
    max_iterations: int = Field(50, ge=1, le=200, description="最大迭代次数")


