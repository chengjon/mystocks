"""Trade route response examples and OpenAPI response specs."""

from typing import Any

from app.openapi_config import COMMON_RESPONSES

TRADE_ROUTE_RESPONSES = {
    500: COMMON_RESPONSES[500],
}

TRADE_HEALTH_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {"status": "ok", "service": "trade"},
    "message": "服务正常",
    "request_id": "req-trade-health-001",
}

TRADE_PORTFOLIO_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Trade portfolio loaded from trading runtime",
    "request_id": "req-trade-portfolio-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "status": "available",
        "endpoint": "trade",
        "resource": "portfolio",
        "account": {
            "account_id": "session_demo_001",
            "account_type": "stock",
            "total_assets": "100000.00",
            "cash": "82000.00",
            "market_value": "18000.00",
            "frozen_cash": None,
            "total_profit_loss": "0.00",
            "profit_loss_percent": 0.0,
            "risk_level": "low",
            "last_update": "2026-04-08T04:20:00Z",
        },
    },
}

TRADE_POSITIONS_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Trade positions loaded from trading runtime",
    "request_id": "req-trade-positions-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "status": "available",
        "endpoint": "trade",
        "resource": "positions",
        "positions": [
            {
                "symbol": "600519",
                "symbol_name": "600519",
                "quantity": 100,
                "available_quantity": 100,
                "cost_price": "1800.0",
                "current_price": "1800.0",
                "market_value": "180000.0",
                "profit_loss": "0.0",
                "profit_loss_percent": 0.0,
                "last_update": "2026-04-08T04:20:00Z",
            }
        ],
        "total_count": 1,
        "total_market_value": "180000.0",
        "total_profit_loss": "0.0",
        "total_profit_loss_percent": 0.0,
    },
}

TRADE_SIGNALS_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Trade signals derived from trading runtime",
    "request_id": "req-trade-signals-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "status": "available",
        "endpoint": "trade",
        "resource": "signals",
        "items": [
            {
                "symbol": "600519.SH",
                "name": "600519.SH",
                "type": "BUY",
                "price": 1750.0,
                "time": "2026-04-08T04:20:00Z",
                "strategy": "svm_momentum_v1",
            }
        ],
        "total": 1,
        "source": "trading_runtime",
    },
}

TRADE_HISTORY_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Trade history loaded from backtest trades",
    "request_id": "req-trade-history-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "status": "available",
        "endpoint": "trade",
        "resource": "trades",
        "trades": [
            {
                "trade_id": "101",
                "order_id": "backtest-7-101",
                "symbol": "600519.SH",
                "direction": "buy",
                "price": "1750.00",
                "quantity": 100,
                "amount": "175000.00",
                "commission": "52.50",
                "trade_time": "2026-04-08T00:00:00",
                "trade_type": "backtest",
            }
        ],
        "total_count": 1,
        "total_amount": "175000.00",
        "total_commission": "52.50",
        "page": 1,
        "page_size": 20,
        "source": "backtest_trades",
    },
}

TRADE_STATISTICS_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Trade statistics summarized from trading runtime",
    "request_id": "req-trade-statistics-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "status": "available",
        "endpoint": "trade",
        "resource": "statistics",
        "statistics": {
            "total_trades": 1,
            "buy_count": 1,
            "sell_count": 0,
            "position_count": 1,
            "total_buy_amount": 18000.0,
            "total_sell_amount": 0.0,
            "total_commission": 0.0,
            "realized_profit": 0.0,
        },
        "source": "trading_runtime",
    },
}

EXECUTE_TRADE_REQUEST_EXAMPLE = {
    "direction": "buy",
    "symbol": "600519.SH",
    "quantity": 100,
    "price": 1750.0,
}

EXECUTE_TRADE_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Trade order executed in trading runtime",
    "request_id": "req-trade-execute-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "status": "available",
        "endpoint": "trade",
        "resource": "execute",
        "accepted": True,
        "execution_mode": "runtime",
        "session_id": "session_demo_001",
        "order": EXECUTE_TRADE_REQUEST_EXAMPLE,
        "result": {
            "action": "opened",
            "position_id": "pos_demo_001",
            "remaining_quantity": 100,
            "realized_profit": 0.0,
        },
    },
}


def _success_response_spec(description: str, example: dict[str, Any]) -> dict[int, dict[str, Any]]:
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


TRADE_PORTFOLIO_RESPONSES = {
    **TRADE_ROUTE_RESPONSES,
    **_success_response_spec("账户资产概览查询成功。", TRADE_PORTFOLIO_RESPONSE_EXAMPLE),
}

TRADE_POSITIONS_RESPONSES = {
    **TRADE_ROUTE_RESPONSES,
    **_success_response_spec("当前持仓列表查询成功。", TRADE_POSITIONS_RESPONSE_EXAMPLE),
}

TRADE_SIGNALS_RESPONSES = {
    **TRADE_ROUTE_RESPONSES,
    **_success_response_spec("交易信号列表查询成功。", TRADE_SIGNALS_RESPONSE_EXAMPLE),
}

TRADE_HISTORY_RESPONSES = {
    **TRADE_ROUTE_RESPONSES,
    **_success_response_spec("交易历史分页查询成功。", TRADE_HISTORY_RESPONSE_EXAMPLE),
}

TRADE_STATISTICS_RESPONSES = {
    **TRADE_ROUTE_RESPONSES,
    **_success_response_spec("交易统计指标查询成功。", TRADE_STATISTICS_RESPONSE_EXAMPLE),
}

TRADE_EXECUTE_RESPONSES = {
    **TRADE_ROUTE_RESPONSES,
    **_success_response_spec("交易委托执行成功。", EXECUTE_TRADE_RESPONSE_EXAMPLE),
}
