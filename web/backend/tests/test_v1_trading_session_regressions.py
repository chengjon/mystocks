from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.trading.session", None)
    return importlib.import_module("app.api.v1.trading.session")


async def test_v1_trading_session_runtime_crud_flow():
    module = _load_module()
    module.runtime_store.reset()

    create_payload = await module.create_trading_session(
        module.TradingSessionCreate(symbol="600519", strategy_id="svm_momentum_v1", initial_capital=100000.0)
    )

    assert create_payload.success is True
    assert create_payload.code == 200
    session_id = create_payload.data["session_id"]
    assert create_payload.data["status"] == "active"

    list_payload = await module.list_trading_sessions()
    assert list_payload.success is True
    assert list_payload.data["total"] == 1
    assert list_payload.data["sessions"][0]["session_id"] == session_id

    detail_payload = await module.get_trading_session(session_id)
    assert detail_payload.success is True
    assert detail_payload.data["session_id"] == session_id

    update_payload = await module.update_trading_session(session_id, module.TradingSessionUpdate(action="pause", reason="volatility"))
    assert update_payload.success is True
    assert update_payload.data["status"] == "paused"

    delete_payload = await module.delete_trading_session(session_id)
    assert delete_payload.success is True
    assert session_id in delete_payload.data["message"]
