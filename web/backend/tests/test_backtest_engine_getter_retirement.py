from app.services import backtest_engine
from app.services.backtest_engine import BacktestConfig, BacktestEngine, BacktestResult


def test_backtest_engine_public_surface_excludes_legacy_singleton_getter() -> None:
    assert not hasattr(backtest_engine, "_backtest_engine")
    assert not hasattr(backtest_engine, "get_backtest_engine")


def test_backtest_engine_core_types_remain_importable() -> None:
    assert BacktestConfig.__name__ == "BacktestConfig"
    assert BacktestResult.__name__ == "BacktestResult"
    assert BacktestEngine.__name__ == "BacktestEngine"
