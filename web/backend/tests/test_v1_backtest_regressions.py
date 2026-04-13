from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.analysis.backtest", None)
    return importlib.import_module("app.api.v1.analysis.backtest")


async def test_v1_backtest_monte_carlo_returns_runtime_backed_response():
    module = _load_module()
    request = module.MonteCarloRequest(
        strategy_id="momentum_breakout_v2",
        symbol="600519.SH",
        start_date="2024-01-01",
        end_date="2024-12-31",
        iterations=64,
    )

    payload = await module.run_monte_carlo_backtest(request)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["strategy_id"] == "momentum_breakout_v2"
    assert payload.data["symbol"] == "600519.SH"
    assert payload.data["simulations_run"] == 64
    assert payload.data["return_distribution"]["max"] >= payload.data["return_distribution"]["min"]
    assert payload.data["risk_metrics"]["prob_positive_return"] >= 0.0
    assert payload.data["equity_curves"]


async def test_v1_backtest_stress_test_returns_runtime_results():
    module = _load_module()
    request = module.StressTestRequest(
        portfolio_id="growth_portfolio_alpha",
        scenarios=[
            {"name": "market_crash_2008", "shock": {"market_drop_pct": 0.35, "volatility_spike_pct": 0.5}},
            {"name": "liquidity_crunch", "shock": {"liquidity_drop_pct": 0.4, "spread_widen_pct": 0.25}},
        ],
    )

    payload = await module.run_stress_test(request)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["portfolio_id"] == "growth_portfolio_alpha"
    assert payload.data["scenarios_tested"] == 2
    assert len(payload.data["results"]) == 2
    assert payload.data["recommendations"]


async def test_v1_backtest_equity_curve_returns_runtime_summary():
    module = _load_module()

    payload = await module.get_equity_curve("momentum_breakout_v2", "2024-01-01", "2024-12-31")

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["strategy_id"] == "momentum_breakout_v2"
    assert payload.data["period"] == {"start": "2024-01-01", "end": "2024-12-31"}
    assert payload.data["data_points"] > 30
    assert payload.data["final_value"] > 0
