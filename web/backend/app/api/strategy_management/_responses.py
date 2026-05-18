"""Response examples and OpenAPI spec constants for strategy management."""

from typing import Any

def _success_response_spec(description: str, example: Any) -> dict[int, dict[str, Any]]:
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

STRATEGY_UPDATE_EXAMPLES = {
    "update_strategy_runtime_config": {
        "summary": "更新策略配置",
        "description": "调整策略状态、标的池和执行参数。",
        "value": {
            "name": "momentum-rotation-v2",
            "status": "active",
            "symbols": ["600519", "000001", "159915"],
            "parameters": {"rebalance_days": 5, "max_position": 0.2},
            "description": "升级后的动量轮动策略配置",
        },
    }
}

STRATEGY_CREATE_EXAMPLES = {
    "create_momentum_strategy": {
        "summary": "创建新策略",
        "description": "创建一个待运行的动量轮动策略配置，包含标的池、参数和初始状态。",
        "value": {
            "name": "momentum-rotation-v1",
            "description": "用于日频轮动的动量策略",
            "strategy_type": "technical",
            "parameters": {"rebalance_days": 5, "max_position": 0.2},
            "status": "draft",
        },
    }
}

MODEL_TRAIN_EXAMPLES = {
    "train_lstm_model": {
        "summary": "启动模型训练",
        "description": "提交一个 LSTM 模型训练任务，携带模型类型、超参数与训练配置。",
        "value": {
            "name": "lstm-alpha-001",
            "model_type": "lstm",
            "hyperparameters": {"epochs": 20, "batch_size": 64, "hidden_size": 128},
            "training_config": {"train_ratio": 0.8, "validation_ratio": 0.1, "target": "close"},
        },
    }
}

BACKTEST_RUN_EXAMPLES = {
    "run_index_future_backtest": {
        "summary": "启动股指期货回测",
        "description": "提交沪深 300 股指期货策略回测，包含时间区间、初始资金和手续费参数。",
        "value": {
            "strategy_name": "if_trend_following",
            "symbols": ["IF9999.CCFX"],
            "start_date": "2025-01-01",
            "end_date": "2025-03-31",
            "initial_capital": 500000.0,
            "parameters": {
                "strategy_id": 12,
                "commission_rate": 0.00023,
                "slippage_rate": 0.0005,
                "margin_ratio": 0.12,
            },
        },
    }
}

STRATEGY_LIST_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "获取策略列表成功",
    "data": {
        "items": [
            {
                "id": 101,
                "strategy_id": 101,
                "strategy_name": "if-trend-following",
                "strategy_type": "futures",
                "description": "股指期货趋势跟踪策略，面向 IF 主连合约。",
                "parameters": {"lookback_days": 20, "max_position": 2, "risk_budget": 0.03},
                "status": "active",
                "created_at": "2026-04-07T09:30:00",
                "updated_at": "2026-04-08T09:30:00",
            },
            {
                "id": 102,
                "strategy_id": 102,
                "strategy_name": "hk-breakout-rotation",
                "strategy_type": "technical",
                "description": "港股突破轮动策略，监控恒生科技核心成分股。",
                "parameters": {"universe": ["00700.HK", "09988.HK"], "rebalance_days": 5},
                "status": "draft",
                "created_at": "2026-04-06T10:00:00",
                "updated_at": "2026-04-07T18:00:00",
            },
        ],
        "total": 2,
        "page": 1,
        "page_size": 20,
    },
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-mgmt-list-001",
}

STRATEGY_CREATE_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "策略创建成功",
    "data": {
        "id": 103,
        "strategy_id": 103,
        "strategy_name": "momentum-rotation-v1",
        "strategy_type": "technical",
        "description": "用于日频轮动的动量策略",
        "parameters": {"rebalance_days": 5, "max_position": 0.2},
        "status": "draft",
        "created_at": "2026-04-08T04:20:00Z",
        "updated_at": "2026-04-08T04:20:00Z",
    },
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-mgmt-create-001",
}

STRATEGY_DETAIL_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "获取策略成功",
    "data": {
        "id": 101,
        "strategy_id": 101,
        "strategy_name": "if-trend-following",
        "strategy_type": "futures",
        "description": "股指期货趋势跟踪策略，面向 IF 主连合约。",
        "parameters": {"lookback_days": 20, "max_position": 2, "risk_budget": 0.03},
        "status": "active",
        "created_at": "2026-04-07T09:30:00",
        "updated_at": "2026-04-08T09:30:00",
    },
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-mgmt-detail-001",
}

STRATEGY_UPDATE_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "策略更新成功",
    "data": None,
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-mgmt-update-001",
}

STRATEGY_ARCHIVE_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "策略已归档",
    "data": None,
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-mgmt-archive-001",
}

STRATEGY_LIFECYCLE_RESPONSE_EXAMPLE = {
    "start": {
        "success": True,
        "code": 200,
        "message": "策略启动成功",
        "data": {
            "id": 101,
            "strategy_id": 101,
            "strategy_name": "if-trend-following",
            "strategy_type": "futures",
            "description": "股指期货趋势跟踪策略，面向 IF 主连合约。",
            "parameters": {"lookback_days": 20, "max_position": 2, "risk_budget": 0.03},
            "status": "active",
            "created_at": "2026-04-07T09:30:00",
            "updated_at": "2026-04-08T04:20:00Z",
        },
        "timestamp": "2026-04-08T04:20:00Z",
        "request_id": "req-strategy-mgmt-start-001",
    },
    "pause": {
        "success": True,
        "code": 200,
        "message": "策略暂停成功",
        "data": {
            "id": 101,
            "strategy_id": 101,
            "strategy_name": "if-trend-following",
            "strategy_type": "futures",
            "description": "股指期货趋势跟踪策略，面向 IF 主连合约。",
            "parameters": {"lookback_days": 20, "max_position": 2, "risk_budget": 0.03},
            "status": "paused",
            "created_at": "2026-04-07T09:30:00",
            "updated_at": "2026-04-08T04:25:00Z",
        },
        "timestamp": "2026-04-08T04:25:00Z",
        "request_id": "req-strategy-mgmt-pause-001",
    },
    "resume": {
        "success": True,
        "code": 200,
        "message": "策略恢复成功",
        "data": {
            "id": 101,
            "strategy_id": 101,
            "strategy_name": "if-trend-following",
            "strategy_type": "futures",
            "description": "股指期货趋势跟踪策略，面向 IF 主连合约。",
            "parameters": {"lookback_days": 20, "max_position": 2, "risk_budget": 0.03},
            "status": "active",
            "created_at": "2026-04-07T09:30:00",
            "updated_at": "2026-04-08T04:30:00Z",
        },
        "timestamp": "2026-04-08T04:30:00Z",
        "request_id": "req-strategy-mgmt-resume-001",
    },
    "stop": {
        "success": True,
        "code": 200,
        "message": "策略停止成功",
        "data": {
            "id": 101,
            "strategy_id": 101,
            "strategy_name": "if-trend-following",
            "strategy_type": "futures",
            "description": "股指期货趋势跟踪策略，面向 IF 主连合约。",
            "parameters": {"lookback_days": 20, "max_position": 2, "risk_budget": 0.03},
            "status": "archived",
            "created_at": "2026-04-07T09:30:00",
            "updated_at": "2026-04-08T04:35:00Z",
        },
        "timestamp": "2026-04-08T04:35:00Z",
        "request_id": "req-strategy-mgmt-stop-001",
    },
}

MODEL_TRAIN_RESPONSE_EXAMPLE = {
    "task_id": "train_18_1775622000",
    "model_id": 18,
}

MODEL_TRAIN_STATUS_RESPONSE_EXAMPLE = {
    "status": "training",
    "progress": 75,
    "metrics": {
        "loss": 0.083,
        "val_loss": 0.091,
        "accuracy": 0.68,
    },
}

MODEL_LIST_RESPONSE_EXAMPLE = [
    {
        "id": 18,
        "name": "lstm-alpha-001",
        "model_type": "lstm",
        "hyperparameters": {"epochs": 20, "batch_size": 64, "hidden_size": 128},
        "training_config": {"train_ratio": 0.8, "validation_ratio": 0.1, "target": "close"},
        "status": "completed",
        "training_started_at": "2026-04-08T03:40:00",
        "created_at": "2026-04-08T03:39:00",
        "performance_metrics": {"accuracy": 0.71, "f1_score": 0.67},
    },
    {
        "id": 19,
        "name": "xgboost-hk-momentum-001",
        "model_type": "xgboost",
        "hyperparameters": {"max_depth": 6, "eta": 0.05},
        "training_config": {"train_ratio": 0.75, "validation_ratio": 0.15, "target": "next_return"},
        "status": "training",
        "training_started_at": "2026-04-08T04:10:00",
        "created_at": "2026-04-08T04:08:00",
        "performance_metrics": None,
    },
]

BACKTEST_RUN_RESPONSE_EXAMPLE = {
    "backtest_id": 950001,
}

BACKTEST_LIST_RESPONSE_EXAMPLE = {
    "items": [
        {
            "id": 950001,
            "backtest_id": 950001,
            "name": "if_trend_following_Backtest",
            "strategy_id": 12,
            "strategy_name": "if_trend_following",
            "symbols": ["IF9999.CCFX"],
            "start_date": "2025-01-01",
            "end_date": "2025-03-31",
            "initial_cash": 500000.0,
            "initial_capital": 500000.0,
            "commission_rate": 0.00023,
            "stamp_tax_rate": 0.001,
            "slippage_rate": 0.0005,
            "status": "completed",
            "created_at": "2026-04-08T04:20:00Z",
            "started_at": "2026-04-08T04:20:00Z",
            "completed_at": "2026-04-08T04:20:00Z",
            "error_message": None,
            "has_results": True,
            "total_return": 0.182,
            "max_drawdown": -0.083,
            "performance": {
                "total_return": 0.182,
                "annualized_return": 0.156,
                "max_drawdown": -0.083,
                "sharpe_ratio": 1.42,
                "win_rate": 0.61,
                "total_trades": 28,
            },
            "equity_curve": [
                {"date": "2025-01-01", "equity": 500000.0},
                {"date": "2025-03-31", "equity": 591000.0},
            ],
            "drawdown_curve": [
                {"date": "2025-01-01", "drawdown": 0},
                {"date": "2025-03-31", "drawdown": -0.083},
            ],
            "returns_distribution": [
                {"bucket": "-2%~-1%", "count": 3},
                {"bucket": "0%~1%", "count": 9},
                {"bucket": "1%~2%", "count": 7},
            ],
        }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
}

BACKTEST_DETAIL_RESPONSE_EXAMPLE = BACKTEST_LIST_RESPONSE_EXAMPLE["items"][0]

BACKTEST_STATUS_RESPONSE_EXAMPLE = {
    "backtest_id": 950001,
    "status": "completed",
    "created_at": "2026-04-08T04:20:00Z",
    "started_at": "2026-04-08T04:20:00Z",
    "completed_at": "2026-04-08T04:22:00Z",
    "error_message": None,
    "has_results": True,
}

STRATEGY_LIST_RESPONSES = _success_response_spec("策略列表查询成功。", STRATEGY_LIST_RESPONSE_EXAMPLE)
STRATEGY_CREATE_RESPONSES = _success_response_spec("策略创建成功。", STRATEGY_CREATE_RESPONSE_EXAMPLE)
STRATEGY_DETAIL_RESPONSES = _success_response_spec("策略详情查询成功。", STRATEGY_DETAIL_RESPONSE_EXAMPLE)
STRATEGY_UPDATE_RESPONSES = _success_response_spec("策略更新成功。", STRATEGY_UPDATE_RESPONSE_EXAMPLE)
STRATEGY_DELETE_RESPONSES = _success_response_spec("策略归档成功。", STRATEGY_ARCHIVE_RESPONSE_EXAMPLE)
STRATEGY_START_RESPONSES = _success_response_spec("策略启动成功。", STRATEGY_LIFECYCLE_RESPONSE_EXAMPLE["start"])
STRATEGY_PAUSE_RESPONSES = _success_response_spec("策略暂停成功。", STRATEGY_LIFECYCLE_RESPONSE_EXAMPLE["pause"])
STRATEGY_RESUME_RESPONSES = _success_response_spec("策略恢复成功。", STRATEGY_LIFECYCLE_RESPONSE_EXAMPLE["resume"])
STRATEGY_STOP_RESPONSES = _success_response_spec("策略停止成功。", STRATEGY_LIFECYCLE_RESPONSE_EXAMPLE["stop"])
MODEL_TRAIN_RESPONSES = _success_response_spec("模型训练任务创建成功。", MODEL_TRAIN_RESPONSE_EXAMPLE)
MODEL_TRAIN_STATUS_RESPONSES = _success_response_spec("模型训练状态查询成功。", MODEL_TRAIN_STATUS_RESPONSE_EXAMPLE)
MODEL_LIST_RESPONSES = _success_response_spec("模型列表查询成功。", MODEL_LIST_RESPONSE_EXAMPLE)
BACKTEST_RUN_RESPONSES = _success_response_spec("回测任务创建成功。", BACKTEST_RUN_RESPONSE_EXAMPLE)
BACKTEST_LIST_RESPONSES = _success_response_spec("回测结果列表查询成功。", BACKTEST_LIST_RESPONSE_EXAMPLE)
BACKTEST_DETAIL_RESPONSES = _success_response_spec("回测详细结果查询成功。", BACKTEST_DETAIL_RESPONSE_EXAMPLE)
BACKTEST_STATUS_RESPONSES = _success_response_spec("回测任务状态查询成功。", BACKTEST_STATUS_RESPONSE_EXAMPLE)
