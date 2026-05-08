from __future__ import annotations

import importlib
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_dependencies_module():
    sys.modules.pop("app.services.attribution.market_data_dependencies", None)
    return importlib.import_module("app.services.attribution.market_data_dependencies")


def _load_adapter_module():
    sys.modules.pop("app.services.attribution.adapters.backtest_snapshot", None)
    return importlib.import_module("app.services.attribution.adapters.backtest_snapshot")


def test_load_benchmark_constituents_delegates_to_baostock_importer():
    module = _load_dependencies_module()
    expected = pd.DataFrame([{"code": "sh.600000"}])
    dependencies = module.AttributionMarketDataDependencies(
        baostock_importer=SimpleNamespace(query_hs300_stocks=lambda analysis_date: expected),
        data_service=SimpleNamespace(),
    )

    result = dependencies.load_benchmark_constituents("2026-05-08")

    assert result.equals(expected)


def test_load_industry_classification_raises_when_industry_is_missing():
    module = _load_dependencies_module()
    dependencies = module.AttributionMarketDataDependencies(
        baostock_importer=SimpleNamespace(query_stock_industry=lambda _symbol, _analysis_date: pd.DataFrame()),
        data_service=SimpleNamespace(),
    )

    with pytest.raises(module.AttributionDependencyError, match="missing industry classification"):
        dependencies.load_industry_classification(["600000.SH"], "2026-05-08")


def test_build_backtest_snapshot_requires_position_level_enrichment():
    module = _load_adapter_module()
    backtest_result = {
        "backtest_id": 42,
        "start_date": date(2026, 5, 1),
        "end_date": date(2026, 5, 8),
        "symbols": ["600000.SH", "600519.SH"],
        "equity_curve": [],
        "trades": [
            {
                "symbol": "600000.SH",
                "action": "buy",
                "trade_date": date(2026, 5, 6),
                "price": 10.0,
                "quantity": 100,
            },
            {
                "symbol": "600519.SH",
                "action": "buy",
                "trade_date": date(2026, 5, 7),
                "price": 1800.0,
                "quantity": 10,
            },
        ],
    }

    snapshot = module.build_backtest_attribution_snapshot._from_trade_projection_for_test(
        backtest_result=backtest_result,
        analysis_date="2026-05-08",
    )

    assert {row.symbol for row in snapshot.portfolio} == {"600000.SH", "600519.SH"}
    assert snapshot.analysis_date == "2026-05-08"
