"""
机器学习策略API

提供ML策略训练、预测和回测功能
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Query
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/strategies",
    tags=["ML Strategies"],
)


def _success_response_spec(description: str, example: dict) -> dict[int, dict]:
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

STRATEGY_TRAINING_REQUEST_EXAMPLES = {
    "svm_training": {
        "summary": "训练 SVM 策略",
        "value": {
            "strategy_type": "svm",
            "symbol": "AAPL",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "parameters": {"lookback_window": 30, "kernel": "rbf"},
        },
    }
}

STRATEGY_PREDICTION_REQUEST_EXAMPLES = {
    "short_term_signal": {
        "summary": "生成短周期预测信号",
        "value": {
            "strategy_id": "svm_AAPL_1735689600",
            "symbol": "AAPL",
            "prediction_horizon": 5,
        },
    }
}

STRATEGY_BACKTEST_REQUEST_EXAMPLES = {
    "swing_backtest": {
        "summary": "回测已训练策略",
        "value": {
            "strategy_id": "svm_AAPL_1735689600",
            "symbol": "AAPL",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 100000.0,
            "position_size": 0.1,
        },
    }
}

STRATEGY_TRAINING_RESPONSE_EXAMPLE = {
    "strategy_id": "svm_AAPL_1735689600",
    "strategy_type": "svm",
    "training_accuracy": 0.78,
    "validation_score": 0.72,
    "feature_importance": {
        "close_price": 0.25,
        "volume": 0.2,
        "rsi_14": 0.15,
        "macd": 0.12,
        "bollinger_position": 0.1,
        "momentum": 0.08,
        "volatility": 0.06,
        "trend_strength": 0.04,
    },
    "training_duration_ms": 4520,
    "model_size_bytes": 125000,
}

STRATEGY_PREDICTION_RESPONSE_EXAMPLE = {
    "strategy_id": "svm_AAPL_1735689600",
    "symbol": "AAPL",
    "prediction": {
        "signal": "BUY",
        "strength": 0.75,
        "predicted_return": 0.025,
        "time_horizon": 5,
    },
    "confidence": 0.82,
    "timestamp": "2026-04-08T12:30:00",
}

STRATEGY_BACKTEST_RESPONSE_EXAMPLE = {
    "strategy_id": "svm_AAPL_1735689600",
    "total_return": 0.285,
    "annualized_return": 0.195,
    "sharpe_ratio": 1.45,
    "max_drawdown": 0.085,
    "win_rate": 0.62,
    "total_trades": 89,
    "backtest_duration_ms": 1250,
}

STRATEGY_TRAINING_RESPONSES = _success_response_spec("机器学习策略训练成功。", STRATEGY_TRAINING_RESPONSE_EXAMPLE)
STRATEGY_PREDICTION_RESPONSES = _success_response_spec("机器学习策略预测成功。", STRATEGY_PREDICTION_RESPONSE_EXAMPLE)
STRATEGY_BACKTEST_RESPONSES = _success_response_spec("机器学习策略回测成功。", STRATEGY_BACKTEST_RESPONSE_EXAMPLE)

STRATEGY_LIST_RESPONSES = {
    200: {
        "description": "可用机器学习策略列表",
        "content": {
            "application/json": {
                "example": {
                    "strategies": [
                        {
                            "strategy_id": "svm_momentum_v1",
                            "strategy_type": "svm",
                            "name": "SVM Momentum Strategy",
                            "description": "基于动量指标的SVM分类策略",
                            "trained": True,
                            "performance": {
                                "accuracy": 0.78,
                                "sharpe_ratio": 1.35,
                                "max_drawdown": 0.08,
                            },
                            "created_at": "2025-01-15T10:30:00Z",
                        }
                    ],
                    "total": 1,
                }
            }
        },
    },
    422: {
        "description": "策略筛选参数不合法",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "loc": ["query", "strategy_type"],
                            "msg": "Input should be 'svm', 'decision_tree', 'naive_bayes', 'lstm' or 'transformer'",
                            "type": "enum",
                        }
                    ]
                }
            }
        },
    },
    500: {
        "description": "策略列表查询失败",
        "content": {
            "application/json": {
                "example": {
                    "detail": "获取策略列表失败: strategy registry unavailable",
                }
            }
        },
    },
}


class MLStrategyType(str, Enum):
    """ML strategy types"""

    SVM = "svm"
    DECISION_TREE = "decision_tree"
    NAIVE_BAYES = "naive_bayes"
    LSTM = "lstm"
    TRANSFORMER = "transformer"


class StrategyTrainingRequest(BaseModel):
    """Strategy training request"""

    strategy_type: MLStrategyType = Field(..., description="ML strategy type")
    symbol: str = Field(..., description="Training symbol")
    start_date: str = Field(..., description="Training start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Training end date (YYYY-MM-DD)")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Strategy parameters")


class StrategyTrainingResponse(BaseModel):
    """Strategy training response"""

    strategy_id: str = Field(..., description="Trained strategy ID")
    strategy_type: str = Field(..., description="Strategy type")
    training_accuracy: float = Field(..., description="Training accuracy")
    validation_score: float = Field(..., description="Validation score")
    feature_importance: Dict[str, float] = Field(..., description="Feature importance scores")
    training_duration_ms: int = Field(..., description="Training duration in milliseconds")
    model_size_bytes: int = Field(..., description="Model size in bytes")


class StrategyPredictionRequest(BaseModel):
    """Strategy prediction request"""

    strategy_id: str = Field(..., description="Strategy ID")
    symbol: str = Field(..., description="Prediction symbol")
    prediction_horizon: int = Field(5, description="Prediction horizon in periods")


class StrategyPredictionResponse(BaseModel):
    """Strategy prediction response"""

    strategy_id: str = Field(..., description="Strategy ID")
    symbol: str = Field(..., description="Prediction symbol")
    prediction: Dict[str, Any] = Field(..., description="Prediction results")
    confidence: float = Field(..., description="Prediction confidence")
    timestamp: datetime = Field(..., description="Prediction timestamp")


class BacktestRequest(BaseModel):
    """Strategy backtest request"""

    strategy_id: str = Field(..., description="Strategy ID")
    symbol: str = Field(..., description="Backtest symbol")
    start_date: str = Field(..., description="Backtest start date")
    end_date: str = Field(..., description="Backtest end date")
    initial_capital: float = Field(100000.0, description="Initial capital")
    position_size: float = Field(0.1, description="Position size (0-1)")


class BacktestResponse(BaseModel):
    """Strategy backtest response"""

    strategy_id: str = Field(..., description="Strategy ID")
    total_return: float = Field(..., description="Total return percentage")
    annualized_return: float = Field(..., description="Annualized return percentage")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown percentage")
    win_rate: float = Field(..., description="Win rate percentage")
    total_trades: int = Field(..., description="Total number of trades")
    backtest_duration_ms: int = Field(..., description="Backtest duration in milliseconds")


class StrategyInfo(BaseModel):
    """Strategy information"""

    strategy_id: str
    strategy_type: str
    name: str
    description: str
    trained: bool
    performance: Optional[Dict[str, float]]
    created_at: str


@router.post(
    "/train",
    response_model=StrategyTrainingResponse,
    summary="Train ML Strategy",
    responses=STRATEGY_TRAINING_RESPONSES,
)
async def train_ml_strategy(
    request: StrategyTrainingRequest = Body(..., openapi_examples=STRATEGY_TRAINING_REQUEST_EXAMPLES)
):
    """
    训练机器学习交易策略

    Trains specified ML strategy (SVM/Decision Tree/Naive Bayes/LSTM/Transformer)
    using historical market data.
    """
    mock_response = StrategyTrainingResponse(
        strategy_id=f"{request.strategy_type}_{request.symbol}_{int(datetime.now().timestamp())}",
        strategy_type=request.strategy_type.value,
        training_accuracy=0.78,
        validation_score=0.72,
        feature_importance={
            "close_price": 0.25,
            "volume": 0.20,
            "rsi_14": 0.15,
            "macd": 0.12,
            "bollinger_position": 0.10,
            "momentum": 0.08,
            "volatility": 0.06,
            "trend_strength": 0.04,
        },
        training_duration_ms=4520,
        model_size_bytes=125000,
    )
    return mock_response


@router.post(
    "/predict",
    response_model=StrategyPredictionResponse,
    summary="Generate Strategy Prediction",
    responses=STRATEGY_PREDICTION_RESPONSES,
)
async def generate_strategy_prediction(
    request: StrategyPredictionRequest = Body(..., openapi_examples=STRATEGY_PREDICTION_REQUEST_EXAMPLES)
):
    """
    生成策略预测信号

    Uses trained ML strategy to generate trading signals and predictions.
    """
    mock_response = StrategyPredictionResponse(
        strategy_id=request.strategy_id,
        symbol=request.symbol,
        prediction={
            "signal": "BUY",
            "strength": 0.75,
            "predicted_return": 0.025,
            "time_horizon": request.prediction_horizon,
        },
        confidence=0.82,
        timestamp=datetime.now(),
    )
    return mock_response


@router.post(
    "/backtest",
    response_model=BacktestResponse,
    summary="Backtest ML Strategy",
    responses=STRATEGY_BACKTEST_RESPONSES,
)
async def backtest_ml_strategy(
    request: BacktestRequest = Body(..., openapi_examples=STRATEGY_BACKTEST_REQUEST_EXAMPLES)
):
    """
    回测机器学习策略

    Runs comprehensive backtest of ML strategy with detailed performance metrics.
    """
    mock_response = BacktestResponse(
        strategy_id=request.strategy_id,
        total_return=0.285,
        annualized_return=0.195,
        sharpe_ratio=1.45,
        max_drawdown=0.085,
        win_rate=0.62,
        total_trades=89,
        backtest_duration_ms=1250,
    )
    return mock_response


@router.get(
    "",
    response_model=Dict[str, Any],
    summary="List Available Strategies",
    responses=STRATEGY_LIST_RESPONSES,
)
async def list_strategies(
    strategy_type: Optional[MLStrategyType] = Query(
        None,
        description="按策略类型筛选，可选 svm、decision_tree、naive_bayes、lstm 或 transformer。",
    ),
    trained_only: bool = Query(False, description="Only return trained strategies"),
):
    """
    获取可用策略列表

    Returns list of available ML trading strategies with their configurations.
    """
    mock_strategies = [
        {
            "strategy_id": "svm_momentum_v1",
            "strategy_type": "svm",
            "name": "SVM Momentum Strategy",
            "description": "基于动量指标的SVM分类策略",
            "trained": True,
            "performance": {
                "accuracy": 0.78,
                "sharpe_ratio": 1.35,
                "max_drawdown": 0.08,
            },
            "created_at": "2025-01-15T10:30:00Z",
        },
        {
            "strategy_id": "decision_tree_trend_v2",
            "strategy_type": "decision_tree",
            "name": "Decision Tree Trend Strategy",
            "description": "基于趋势分析的决策树策略",
            "trained": True,
            "performance": {
                "accuracy": 0.72,
                "sharpe_ratio": 1.28,
                "max_drawdown": 0.12,
            },
            "created_at": "2025-01-16T14:20:00Z",
        },
        {
            "strategy_id": "lstm_pattern_v1",
            "strategy_type": "lstm",
            "name": "LSTM Pattern Recognition",
            "description": "基于LSTM的时间序列模式识别",
            "trained": False,
            "performance": None,
            "created_at": "2025-01-17T09:15:00Z",
        },
    ]

    if strategy_type:
        mock_strategies = [s for s in mock_strategies if s["strategy_type"] == strategy_type.value]

    if trained_only:
        mock_strategies = [s for s in mock_strategies if s["trained"]]

    return {"strategies": mock_strategies, "total": len(mock_strategies)}
