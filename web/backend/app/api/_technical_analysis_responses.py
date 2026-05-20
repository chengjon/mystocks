"""Auto-extracted response constants."""

from typing import Any, Dict, Optional

from app.api._technical_analysis_models import TECHNICAL_ANALYSIS_503_RESPONSE
from app.openapi_config import COMMON_RESPONSES

ALL_INDICATORS_RESPONSE_EXAMPLE = {
    "symbol": "600519.SH",
    "latest_price": 1750.32,
    "latest_date": "2026-04-07",
    "data_points": 120,
    "total_indicators": 28,
    "trend": {
        "ma5": 1742.18,
        "ma10": 1735.66,
        "ma20": 1718.42,
        "ema12": 1738.55,
        "macd": 12.43,
        "macd_signal": 9.87,
        "macd_hist": 2.56,
        "adx": 24.11,
        "plus_di": 27.35,
        "minus_di": 18.41,
        "sar": 1702.48,
    },
    "momentum": {
        "rsi6": 63.25,
        "rsi12": 58.71,
        "rsi24": 54.86,
        "kdj_k": 72.18,
        "kdj_d": 68.34,
        "kdj_j": 79.86,
        "cci": 118.44,
        "willr": -21.08,
        "roc": 4.32,
    },
    "volatility": {
        "bb_upper": 1788.42,
        "bb_middle": 1725.18,
        "bb_lower": 1661.94,
        "bb_width": 7.33,
        "atr": 35.42,
        "atr_percent": 2.02,
        "kc_upper": 1790.66,
        "kc_middle": 1724.77,
        "kc_lower": 1658.88,
        "stddev": 31.62,
    },
    "volume": {
        "obv": 154326700.0,
        "vwap": 1731.45,
        "volume_ma5": 4987654.0,
        "volume_ma10": 4765123.0,
        "volume_ratio": 1.24,
    },
}

TREND_INDICATORS_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "symbol": "600519.SH",
        "indicators": {
            "ma5": 1742.18,
            "ma10": 1735.66,
            "ma20": 1718.42,
            "ema12": 1738.55,
            "macd": 12.43,
            "macd_signal": 9.87,
            "macd_hist": 2.56,
            "adx": 24.11,
            "plus_di": 27.35,
            "minus_di": 18.41,
            "sar": 1702.48,
        },
        "count": 11,
        "period": "daily",
    },
    "message": "获取600519.SH趋势指标成功",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-technical-trend-001",
}

MOMENTUM_INDICATORS_RESPONSE_EXAMPLE = {
    "success": True,
    "symbol": "600519.SH",
    "indicators": {
        "rsi6": 63.25,
        "rsi12": 58.71,
        "rsi24": 54.86,
        "kdj_k": 72.18,
        "kdj_d": 68.34,
        "kdj_j": 79.86,
        "cci": 118.44,
        "willr": -21.08,
        "roc": 4.32,
    },
    "count": 9,
}

VOLATILITY_INDICATORS_RESPONSE_EXAMPLE = {
    "success": True,
    "symbol": "600519.SH",
    "indicators": {
        "bb_upper": 1788.42,
        "bb_middle": 1725.18,
        "bb_lower": 1661.94,
        "bb_width": 7.33,
        "atr": 35.42,
        "atr_percent": 2.02,
        "kc_upper": 1790.66,
        "kc_middle": 1724.77,
        "kc_lower": 1658.88,
        "stddev": 31.62,
    },
    "count": 10,
}

VOLUME_INDICATORS_RESPONSE_EXAMPLE = {
    "success": True,
    "symbol": "600519.SH",
    "indicators": {
        "obv": 154326700.0,
        "vwap": 1731.45,
        "volume_ma5": 4987654.0,
        "volume_ma10": 4765123.0,
        "volume_ratio": 1.24,
    },
    "count": 5,
}

TRADING_SIGNALS_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "symbol": "600519.SH",
        "signals": {
            "overall_signal": "buy",
            "signal_strength": 0.73,
            "signals": [
                {"type": "macd_golden_cross", "signal": "buy", "strength": 0.7},
                {"type": "rsi_oversold", "signal": "buy", "strength": 0.76},
            ],
            "signal_count": {"buy": 2, "sell": 0, "total": 2},
        },
        "period": "daily",
    },
    "message": "获取600519.SH交易信号成功",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-technical-signals-001",
}

TECHNICAL_HISTORY_RESPONSE_EXAMPLE = {
    "success": True,
    "symbol": "600519.SH",
    "period": "daily",
    "count": 2,
    "records": [
        {
            "date": "2026-04-03",
            "open": 1738.5,
            "high": 1756.8,
            "low": 1732.1,
            "close": 1750.32,
            "volume": 5123400,
            "amount": 8954320000.0,
            "change_percent": 1.24,
            "change_amount": 21.42,
            "turnover_rate": 0.62,
        },
        {
            "date": "2026-04-07",
            "open": 1746.8,
            "high": 1761.2,
            "low": 1740.5,
            "close": 1754.66,
            "volume": 4876500,
            "amount": 8521180000.0,
            "change_percent": 0.25,
            "change_amount": 4.34,
            "turnover_rate": 0.58,
        },
    ],
}

TECHNICAL_BATCH_INDICATORS_RESPONSE_EXAMPLE = {
    "success": True,
    "results": {
        "600519.SH": {
            "symbol": "600519.SH",
            "latest_price": 1750.32,
            "latest_date": "2026-04-07",
            "data_points": 120,
            "total_indicators": 28,
            "trend": {"ma5": 1742.18, "ema12": 1738.55, "macd": 12.43},
            "momentum": {"rsi6": 63.25, "kdj_k": 72.18, "roc": 4.32},
            "volatility": {"bb_upper": 1788.42, "atr": 35.42, "stddev": 31.62},
            "volume": {"obv": 154326700.0, "vwap": 1731.45, "volume_ratio": 1.24},
        },
        "000001.SZ": {
            "symbol": "000001.SZ",
            "latest_price": 12.64,
            "latest_date": "2026-04-07",
            "data_points": 120,
            "total_indicators": 24,
            "trend": {"ma5": 12.52, "ema12": 12.48, "macd": 0.12},
            "momentum": {"rsi6": 57.34, "kdj_k": 66.21, "roc": 1.98},
            "volatility": {"bb_upper": 12.91, "atr": 0.21, "stddev": 0.18},
            "volume": {"obv": 223456700.0, "vwap": 12.47, "volume_ratio": 1.09},
        },
    },
}




def _success_response_spec(
    description: str,
    example: Dict[str, Any],
    extra_responses: Optional[Dict[int, Dict[str, Any]]] = None,
) -> Dict[int, Dict[str, Any]]:
    responses: Dict[int, Dict[str, Any]] = {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        },
        422: COMMON_RESPONSES[422],
        500: COMMON_RESPONSES[500],
    }

    if extra_responses:
        responses.update(extra_responses)

    return responses


ALL_INDICATORS_RESPONSES = _success_response_spec(
    "股票全量技术指标查询成功。",
    ALL_INDICATORS_RESPONSE_EXAMPLE,
    extra_responses={503: TECHNICAL_ANALYSIS_503_RESPONSE},
)
TREND_INDICATORS_RESPONSES = _success_response_spec("趋势指标计算成功。", TREND_INDICATORS_RESPONSE_EXAMPLE)
MOMENTUM_INDICATORS_RESPONSES = _success_response_spec("动量指标计算成功。", MOMENTUM_INDICATORS_RESPONSE_EXAMPLE)
VOLATILITY_INDICATORS_RESPONSES = _success_response_spec("波动性指标计算成功。", VOLATILITY_INDICATORS_RESPONSE_EXAMPLE)
VOLUME_INDICATORS_RESPONSES = _success_response_spec("成交量指标计算成功。", VOLUME_INDICATORS_RESPONSE_EXAMPLE)
TRADING_SIGNALS_RESPONSES = _success_response_spec("技术交易信号生成成功。", TRADING_SIGNALS_RESPONSE_EXAMPLE)
TECHNICAL_HISTORY_RESPONSES = _success_response_spec("技术分析历史行情查询成功。", TECHNICAL_HISTORY_RESPONSE_EXAMPLE)
TECHNICAL_BATCH_INDICATORS_RESPONSES = _success_response_spec(
    "批量技术指标查询成功。", TECHNICAL_BATCH_INDICATORS_RESPONSE_EXAMPLE
)


# ============================================================================
# API Endpoints
# ============================================================================

