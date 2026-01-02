"""临时Mock策略列表端点 - 用于E2E测试"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/mock/strategy", tags=["mock-strategy"])

MOCK_STRATEGIES = [
    {
        "strategy_id": 1,
        "user_id": 1,
        "strategy_name": "MACD趋势跟踪",
        "strategy_type": "momentum",
        "description": "基于MACD指标的趋势跟踪策略",
        "parameters": [{"key": "fast_period", "value": "12"}, {"key": "slow_period", "value": "26"}],
        "max_position_size": 0.1,
        "stop_loss_percent": 5.0,
        "take_profit_percent": 10.0,
        "status": "active",
        "tags": ["trend", "macd"],
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    },
    {
        "strategy_id": 2,
        "user_id": 1,
        "strategy_name": "RSI均值回归",
        "strategy_type": "mean_reversion",
        "description": "基于RSI指标的均值回归策略",
        "parameters": [{"key": "rsi_period", "value": "14"}, {"key": "oversold", "value": "30"}],
        "max_position_size": 0.15,
        "stop_loss_percent": 3.0,
        "take_profit_percent": 8.0,
        "status": "active",
        "tags": ["mean_reversion", "rsi"],
        "created_at": "2024-01-02T00:00:00",
        "updated_at": "2024-01-02T00:00:00"
    }
]

@router.get("/strategies")
async def list_strategies_mock():
    """获取策略列表（Mock数据）"""
    return {
        "total_count": len(MOCK_STRATEGIES),
        "strategies": MOCK_STRATEGIES,
        "page": 1,
        "page_size": 20
    }
