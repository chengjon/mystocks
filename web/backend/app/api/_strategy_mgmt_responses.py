"""Strategy management response examples and OpenAPI response specs."""

from app.openapi_config import COMMON_RESPONSES


def _response_spec(status_code: int, description: str, example: dict) -> dict:
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


STRATEGY_MGMT_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    401: COMMON_RESPONSES[401],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

STRATEGY_CONFIG_EXAMPLE = {
    "strategy_id": 123,
    "user_id": 1001,
    "strategy_name": "双均线突破",
    "strategy_type": "momentum",
    "description": "基于短中期均线突破信号的趋势跟踪策略",
    "parameters": [
        {
            "name": "short_period",
            "value": 5,
            "description": "短周期均线窗口",
            "data_type": "int",
        },
        {
            "name": "long_period",
            "value": 20,
            "description": "长周期均线窗口",
            "data_type": "int",
        },
    ],
    "max_position_size": 0.2,
    "stop_loss_percent": 5.0,
    "take_profit_percent": 12.0,
    "status": "active",
    "created_at": "2026-04-01T09:30:00",
    "updated_at": "2026-04-04T09:45:00",
    "tags": ["趋势", "均线"],
}

STRATEGY_UPDATE_REQUEST_EXAMPLES = {
    "pause_strategy_and_adjust_risk": {
        "summary": "更新策略参数与状态",
        "description": "将策略切换为暂停状态，并同步调整止损与标签。",
        "value": {
            "description": "回撤放大后进入观察期，暂停新开仓。",
            "stop_loss_percent": 4.0,
            "status": "paused",
            "tags": ["趋势", "观察期"],
        },
    }
}

BACKTEST_RESULT_PENDING_EXAMPLE = {
    "backtest_id": 456,
    "strategy_id": 123,
    "user_id": 1001,
    "symbols": ["000001.SZ", "600000.SH"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 100000.0,
    "final_capital": 100000.0,
    "performance": {
        "total_return": 0.0,
        "annual_return": 0.0,
        "benchmark_return": 0.0,
        "alpha": 0.0,
        "beta": 0.0,
        "sharpe_ratio": 0.0,
        "max_drawdown": 0.0,
        "volatility": 0.0,
        "total_trades": 0,
        "win_rate": 0.0,
        "profit_factor": 0.0,
        "calmar_ratio": 0.0,
        "sortino_ratio": 0.0,
    },
    "equity_curve": [],
    "trades": [],
    "status": "pending",
    "created_at": "2026-04-04T09:46:00",
    "completed_at": None,
    "error_message": None,
}

BACKTEST_RESULT_COMPLETED_EXAMPLE = {
    "backtest_id": 456,
    "strategy_id": 123,
    "user_id": 1001,
    "symbols": ["000001.SZ", "600000.SH"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 100000.0,
    "final_capital": 115000.0,
    "performance": {
        "total_return": 15.0,
        "annual_return": 15.0,
        "benchmark_return": 8.0,
        "alpha": 7.0,
        "beta": 1.05,
        "sharpe_ratio": 1.8,
        "max_drawdown": -8.5,
        "volatility": 12.3,
        "total_trades": 45,
        "win_rate": 62.2,
        "profit_factor": 1.85,
        "calmar_ratio": 1.76,
        "sortino_ratio": 2.1,
    },
    "equity_curve": [],
    "trades": [],
    "status": "completed",
    "created_at": "2026-04-01T09:46:00",
    "completed_at": "2026-04-01T09:52:00",
    "error_message": None,
}

CREATE_STRATEGY_SUCCESS_RESPONSE = _response_spec(201, "新建策略配置", STRATEGY_CONFIG_EXAMPLE)
LIST_STRATEGIES_SUCCESS_RESPONSE = _response_spec(
    200,
    "策略列表查询结果",
    {
        "total_count": 2,
        "strategies": [STRATEGY_CONFIG_EXAMPLE],
        "page": 1,
        "page_size": 20,
    },
)
GET_STRATEGY_SUCCESS_RESPONSE = _response_spec(200, "单个策略详情", STRATEGY_CONFIG_EXAMPLE)
UPDATE_STRATEGY_SUCCESS_RESPONSE = _response_spec(
    200,
    "更新后的策略详情",
    {
        **STRATEGY_CONFIG_EXAMPLE,
        "description": "回撤放大后进入观察期，暂停新开仓。",
        "stop_loss_percent": 4.0,
        "status": "paused",
        "tags": ["趋势", "观察期"],
    },
)
EXECUTE_BACKTEST_SUCCESS_RESPONSE = _response_spec(202, "已登记的回测任务", BACKTEST_RESULT_PENDING_EXAMPLE)
GET_BACKTEST_RESULT_SUCCESS_RESPONSE = _response_spec(200, "完整回测结果", BACKTEST_RESULT_COMPLETED_EXAMPLE)
LIST_BACKTESTS_SUCCESS_RESPONSE = _response_spec(
    200,
    "用户回测历史列表",
    {
        "total_count": 1,
        "backtests": [
            {
                "backtest_id": 456,
                "strategy_id": 123,
                "strategy_name": "双均线突破",
                "symbols": ["000001.SZ", "600000.SH"],
                "date_range": "2024-01-01 ~ 2024-12-31",
                "total_return": 15.0,
                "sharpe_ratio": 1.8,
                "max_drawdown": -8.5,
                "status": "completed",
                "created_at": "2026-04-01T09:46:00",
            }
        ],
        "page": 1,
        "page_size": 20,
    },
)
STRATEGY_MGMT_HEALTH_SUCCESS_RESPONSE = _response_spec(
    200,
    "策略管理服务健康状态",
    {
        "status": "healthy",
        "service": "strategy-mgmt",
        "database": "connected",
        "data_source": {"status": "ok"},
        "strategies_count": 12,
        "backtests_count": 34,
        "timestamp": "2026-04-04T09:47:00",
    },
)
BACKTEST_STATUS_SUCCESS_RESPONSE = _response_spec(
    200,
    "兼容保留的回测状态结果",
    {
        "backtest_id": 456,
        "status": "completed",
        "created_at": "2026-04-01T09:46:00",
        "started_at": "2026-04-01T09:47:00",
        "completed_at": "2026-04-01T09:52:00",
        "error_message": None,
        "has_results": True,
    },
)
