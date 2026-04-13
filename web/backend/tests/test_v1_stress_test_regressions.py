from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.analysis.stress_test", None)
    return importlib.import_module("app.api.v1.analysis.stress_test")


def _reset_runtime_state() -> None:
    runtime_state = importlib.import_module("app.api.v1.analysis.runtime_state")
    runtime_state.runtime_store.reset()


async def test_v1_custom_stress_test_returns_runtime_response():
    _reset_runtime_state()
    module = _load_module()
    scenarios = [
        module.StressTestScenario(
            name="market_crash_2008",
            shock_type="price_drop",
            severity=0.5,
            duration_days=180,
        ),
        module.StressTestScenario(
            name="liquidity_crisis",
            shock_type="liquidity_crisis",
            severity=0.4,
            duration_days=30,
        ),
    ]

    payload = await module.run_custom_stress_test("growth_portfolio_alpha", scenarios, 1000000.0)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["portfolio_id"] == "growth_portfolio_alpha"
    assert payload.data["scenarios_tested"] == 2
    assert len(payload.data["results"]) == 2
    assert payload.data["recommendations"]


async def test_v1_predefined_scenarios_returns_runtime_catalog():
    module = _load_module()

    payload = await module.get_predefined_scenarios()

    assert payload.success is True
    assert payload.code == 200
    assert len(payload.data["scenarios"]) >= 3
    assert payload.data["scenarios"][0]["id"] == "market_crash_2008"


async def test_v1_stress_test_history_returns_runtime_entries():
    _reset_runtime_state()
    module = _load_module()
    scenarios = [
        module.StressTestScenario(
            name="market_crash_2008",
            shock_type="price_drop",
            severity=0.5,
            duration_days=180,
        )
    ]
    await module.run_custom_stress_test("growth_portfolio_alpha", scenarios, 1000000.0)

    payload = await module.get_stress_test_history("growth_portfolio_alpha", 10)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["portfolio_id"] == "growth_portfolio_alpha"
    assert payload.data["total"] == 1
    assert payload.data["tests"][0]["scenario"] == "market_crash_2008"
