from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_positions_module():
    sys.modules.pop("app.api.v1.trading.positions", None)
    return importlib.import_module("app.api.v1.trading.positions")


def _load_session_module():
    sys.modules.pop("app.api.v1.trading.session", None)
    return importlib.import_module("app.api.v1.trading.session")


async def test_v1_positions_runtime_crud_flow():
    session_module = _load_session_module()
    positions_module = _load_positions_module()
    positions_module.runtime_store.reset()

    session_payload = await session_module.create_trading_session(
        session_module.TradingSessionCreate(symbol="600519", strategy_id="svm_momentum_v1", initial_capital=100000.0)
    )
    session_id = session_payload.data["session_id"]

    create_payload = await positions_module.create_position(
        positions_module.PositionCreate(symbol="600519", quantity=100, price=1800.0)
    )
    assert create_payload.success is True
    assert create_payload.code == 200
    position_id = create_payload.data["position_id"]

    list_payload = await positions_module.list_positions(session_id=session_id)
    assert list_payload.success is True
    assert list_payload.data["total"] == 1
    assert list_payload.data["positions"][0]["position_id"] == position_id

    detail_payload = await positions_module.get_position(position_id)
    assert detail_payload.success is True
    assert detail_payload.data["symbol"] == "600519"

    update_payload = await positions_module.update_position(
        position_id,
        positions_module.PositionUpdate(quantity=120, stop_loss=1720.0, take_profit=1950.0),
    )
    assert update_payload.success is True
    assert update_payload.data["quantity"] == 120

    delete_payload = await positions_module.delete_position(position_id)
    assert delete_payload.success is True
    assert position_id in delete_payload.data["message"]

    session_detail = await session_module.get_trading_session(session_id)
    assert session_detail.success is True
    assert session_detail.data["current_positions"] == 0
