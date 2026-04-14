from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.trade.routes", None)
    return importlib.import_module("app.api.trade.routes")


async def test_trade_portfolio_returns_runtime_account_response():
    module = _load_module()
    module.runtime_store.reset()

    session = module.runtime_store.create_session(
        symbol="600519",
        strategy_id="svm_momentum_v1",
        initial_capital=100000.0,
        position_size=0.1,
        risk_threshold=0.05,
    )
    module.runtime_store.create_position(symbol="600519", quantity=100, price=180.0, session_id=session.session_id)

    payload = await module.get_portfolio()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["status"] == "available"
    assert payload.data["resource"] == "portfolio"
    assert payload.data["account"] == {
        "account_id": session.session_id,
        "account_type": "stock",
        "total_assets": "100000.0",
        "cash": "82000.0",
        "market_value": "18000.0",
        "frozen_cash": None,
        "total_profit_loss": "0.0",
        "profit_loss_percent": 0.0,
        "risk_level": "low",
        "last_update": session.updated_at.isoformat().replace("+00:00", "Z"),
    }


async def test_trade_positions_returns_runtime_positions_response():
    module = _load_module()
    module.runtime_store.reset()
    session = module.runtime_store.create_session(
        symbol="600519",
        strategy_id="svm_momentum_v1",
        initial_capital=100000.0,
        position_size=0.1,
        risk_threshold=0.05,
    )
    position = module.runtime_store.create_position(symbol="600519", quantity=100, price=180.0, session_id=session.session_id)

    payload = await module.get_positions()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data == {
        "status": "available",
        "endpoint": "trade",
        "resource": "positions",
        "positions": [
            {
                "symbol": "600519",
                "symbol_name": "600519",
                "quantity": 100,
                "available_quantity": 100,
                "cost_price": "180.0",
                "current_price": "180.0",
                "market_value": "18000.0",
                "profit_loss": "0.0",
                "profit_loss_percent": 0.0,
                "last_update": position.updated_at.isoformat().replace("+00:00", "Z"),
            }
        ],
        "total_count": 1,
        "total_market_value": 18000.0,
        "total_profit_loss": 0.0,
        "total_profit_loss_percent": 0.0,
    }


async def test_trade_signals_returns_unified_placeholder_response():
    module = _load_module()

    payload = await module.get_signals(limit=20)

    assert payload.success is False
    assert payload.code == 503
    assert payload.data == {
        "status": "placeholder",
        "endpoint": "trade",
        "resource": "signals",
        "items": [],
        "total": 0,
    }


async def test_trade_history_returns_unified_placeholder_response():
    module = _load_module()

    def fake_query_trade_history(**kwargs):
        assert kwargs == {
            "symbol": "600519",
            "start_date_obj": module.datetime.strptime("2026-04-01", "%Y-%m-%d").date(),
            "end_date_obj": module.datetime.strptime("2026-04-12", "%Y-%m-%d").date(),
            "page": 2,
            "page_size": 50,
        }
        return {
            "trades": [
                {
                    "trade_id": "101",
                    "order_id": "backtest-7-101",
                    "symbol": "600519",
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
            "page": 2,
            "page_size": 50,
            "source": "backtest_trades",
        }

    module._query_trade_history = fake_query_trade_history

    payload = await module.get_trades(symbol="600519", start_date="2026-04-01", end_date="2026-04-12", page=2, page_size=50)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data == {
        "status": "available",
        "endpoint": "trade",
        "resource": "trades",
        "trades": [
            {
                "trade_id": "101",
                "order_id": "backtest-7-101",
                "symbol": "600519",
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
        "page": 2,
        "page_size": 50,
        "source": "backtest_trades",
    }


async def test_trade_history_rejects_invalid_date_range():
    module = _load_module()

    try:
        await module.get_trades(symbol="600519", start_date="2026-04-12", end_date="2026-04-01", page=1, page_size=20)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 400
        assert "start_date 不能晚于 end_date" in str(exc.detail)
    else:
        raise AssertionError("expected HTTPException for invalid date range")


async def test_trade_statistics_returns_unified_placeholder_response():
    module = _load_module()

    payload = await module.get_statistics()

    assert payload.success is False
    assert payload.code == 503
    assert payload.data == {
        "status": "placeholder",
        "endpoint": "trade",
        "resource": "statistics",
        "statistics": None,
    }


async def test_trade_execute_returns_unified_placeholder_response_after_validation():
    module = _load_module()

    payload = await module.execute_trade(
        {
            "direction": "buy",
            "symbol": "600519.SH",
            "quantity": 100,
            "price": 1750.0,
        }
    )

    assert payload.success is False
    assert payload.code == 503
    assert payload.data == {
        "status": "placeholder",
        "endpoint": "trade",
        "resource": "execute",
        "accepted": False,
        "order": {
            "direction": "buy",
            "symbol": "600519.SH",
            "quantity": 100,
            "price": 1750.0,
        },
    }
