"""Strategy execution route response examples and response specs."""

from typing import Any

# Response example dicts
STRATEGY_DEFINITIONS_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "definitions": [
            {
                "id": 1,
                "strategy_code": "volume_surge",
                "strategy_name_cn": "放量突破",
                "strategy_name_en": "Volume Surge Breakout",
                "description": "识别成交量显著放大且价格突破关键区间的股票。",
                "parameters": {"volume_ratio": 2.0, "lookback_days": 20},
                "is_active": True,
                "created_at": "2026-04-01T09:00:00",
                "updated_at": "2026-04-07T15:30:00",
            },
            {
                "id": 2,
                "strategy_code": "ma_crossover",
                "strategy_name_cn": "均线金叉",
                "strategy_name_en": "MA Crossover",
                "description": "识别短周期均线上穿长周期均线的趋势启动信号。",
                "parameters": {"fast_ma": 5, "slow_ma": 20},
                "is_active": True,
                "created_at": "2026-04-01T09:00:00",
                "updated_at": "2026-04-07T15:30:00",
            },
        ],
        "total": 2,
    },
    "message": "操作成功",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-definitions-001",
}

STRATEGY_RUN_SINGLE_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "strategy_result": {
            "success": True,
            "match_result": True,
            "message": "匹配策略条件",
        },
        "strategy_code": "volume_surge",
        "symbol": "600519.SH",
        "execution_success": True,
    },
    "message": "策略volume_surge执行完成",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-run-single-001",
}

STRATEGY_RUN_BATCH_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "batch_result": {
            "success": True,
            "total": 3,
            "matched": 1,
            "failed": 0,
            "message": "完成: 总计3, 匹配1, 失败0",
        },
        "strategy_code": "ma_crossover",
        "market": "A",
        "execution_success": True,
        "processed_symbols": "600519.SH,000001.SZ,510300.SH",
    },
    "message": "批量策略ma_crossover执行完成",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-run-batch-001",
}

STRATEGY_RESULTS_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "strategy_results": [
            {
                "id": 101,
                "strategy_code": "volume_surge",
                "symbol": "600519.SH",
                "stock_name": "贵州茅台",
                "check_date": "2026-04-07",
                "match_result": True,
                "match_score": 92,
                "match_details": {"volume_ratio": 2.4, "breakout_price": 1748.5},
                "latest_price": "1754.66",
                "change_percent": "1.24",
                "created_at": "2026-04-07T15:00:00",
            },
            {
                "id": 102,
                "strategy_code": "volume_surge",
                "symbol": "000001.SZ",
                "stock_name": "平安银行",
                "check_date": "2026-04-07",
                "match_result": False,
                "match_score": 48,
                "match_details": {"volume_ratio": 1.1, "breakout_price": None},
                "latest_price": "12.64",
                "change_percent": "0.32",
                "created_at": "2026-04-07T15:00:00",
            },
        ],
        "total": 2,
        "filters": {
            "strategy_code": "volume_surge",
            "symbol": None,
            "check_date": "2026-04-07",
            "match_result": None,
        },
    },
    "message": "查询策略结果成功，共2条记录",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-results-001",
}

MATCHED_STOCKS_RESPONSE_EXAMPLE = {
    "success": True,
    "data": [
        {
            "id": 101,
            "strategy_code": "volume_surge",
            "symbol": "600519.SH",
            "stock_name": "贵州茅台",
            "check_date": "2026-04-07",
            "match_result": True,
            "match_score": 92,
            "match_details": {"volume_ratio": 2.4, "breakout_price": 1748.5},
            "latest_price": "1754.66",
            "change_percent": "1.24",
            "created_at": "2026-04-07T15:00:00",
        },
        {
            "id": 103,
            "strategy_code": "volume_surge",
            "symbol": "510300.SH",
            "stock_name": "沪深300ETF",
            "check_date": "2026-04-07",
            "match_result": True,
            "match_score": 88,
            "match_details": {"volume_ratio": 2.1, "breakout_price": 4.12},
            "latest_price": "4.18",
            "change_percent": "0.96",
            "created_at": "2026-04-07T15:00:00",
        },
    ],
    "total": 2,
    "message": "找到2只匹配股票",
}

STRATEGY_SUMMARY_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "strategy_summary": [
            {
                "strategy_code": "volume_surge",
                "strategy_name_cn": "放量突破",
                "strategy_name_en": "Volume Surge Breakout",
                "matched_count": 2,
                "check_date": "2026-04-07",
            },
            {
                "strategy_code": "ma_crossover",
                "strategy_name_cn": "均线金叉",
                "strategy_name_en": "MA Crossover",
                "matched_count": 5,
                "check_date": "2026-04-07",
            },
        ],
        "check_date": "2026-04-07",
    },
    "message": "获取策略统计摘要成功",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-summary-001",
}


def _strategy_success_response_spec(description: str, example: dict) -> dict[int, dict]:
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


STRATEGY_DEFINITIONS_RESPONSES = _strategy_success_response_spec(
    "策略定义列表查询成功。", STRATEGY_DEFINITIONS_RESPONSE_EXAMPLE
)
STRATEGY_RUN_SINGLE_RESPONSES = _strategy_success_response_spec("单只股票策略运行成功。", STRATEGY_RUN_SINGLE_RESPONSE_EXAMPLE)
STRATEGY_RUN_BATCH_RESPONSES = _strategy_success_response_spec("批量策略运行成功。", STRATEGY_RUN_BATCH_RESPONSE_EXAMPLE)
STRATEGY_RESULTS_RESPONSES = _strategy_success_response_spec("策略结果查询成功。", STRATEGY_RESULTS_RESPONSE_EXAMPLE)
MATCHED_STOCKS_RESPONSES = _strategy_success_response_spec("匹配股票列表查询成功。", MATCHED_STOCKS_RESPONSE_EXAMPLE)
STRATEGY_SUMMARY_RESPONSES = _strategy_success_response_spec("策略统计摘要查询成功。", STRATEGY_SUMMARY_RESPONSE_EXAMPLE)
