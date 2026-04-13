from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.strategy.machine_learning", None)
    return importlib.import_module("app.api.v1.strategy.machine_learning")


def _reset_runtime_state() -> None:
    state = importlib.import_module("app.api.v1.strategy.runtime_state")
    state.runtime_store.reset()


async def test_v1_ml_training_prediction_backtest_and_listing_are_runtime_backed():
    _reset_runtime_state()
    module = _load_module()

    train_request = module.StrategyTrainingRequest(
        strategy_type=module.MLStrategyType.SVM,
        symbol="600519.SH",
        start_date="2024-01-01",
        end_date="2024-12-31",
        parameters={"lookback_window": 20},
    )
    train_payload = await module.train_ml_strategy(train_request)

    assert train_payload.success is True
    assert train_payload.code == 200
    strategy_id = train_payload.data["strategy_id"]

    predict_request = module.StrategyPredictionRequest(
        strategy_id=strategy_id,
        symbol="600519.SH",
        prediction_horizon=5,
    )
    predict_payload = await module.generate_strategy_prediction(predict_request)
    assert predict_payload.success is True
    assert predict_payload.code == 200
    assert predict_payload.data["prediction"]["signal"] in {"buy", "sell", "hold"}

    backtest_request = module.BacktestRequest(
        strategy_id=strategy_id,
        symbol="600519.SH",
        start_date="2024-01-01",
        end_date="2024-12-31",
        initial_capital=100000.0,
        position_size=0.1,
    )
    backtest_payload = await module.backtest_ml_strategy(backtest_request)
    assert backtest_payload.success is True
    assert backtest_payload.code == 200
    assert backtest_payload.data["strategy_id"] == strategy_id

    list_payload = await module.list_strategies(trained_only=True)
    assert list_payload.success is True
    assert list_payload.code == 200
    assert list_payload.data["total"] >= 1
    assert any(item["strategy_id"] == strategy_id for item in list_payload.data["strategies"])
