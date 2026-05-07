from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_engine_module():
    sys.modules.pop("app.services.attribution.engine", None)
    return importlib.import_module("app.services.attribution.engine")


def test_engine_returns_brinson_and_factor_sections():
    module = _load_engine_module()

    portfolio = [
        module.PortfolioConstituentSnapshot(
            analysis_date="2026-05-08",
            symbol="600000.SH",
            weight=0.6,
            market_value=600000.0,
            return_rate=0.10,
            industry="银行",
        ),
        module.PortfolioConstituentSnapshot(
            analysis_date="2026-05-08",
            symbol="600519.SH",
            weight=0.4,
            market_value=400000.0,
            return_rate=-0.02,
            industry="食品饮料",
        ),
    ]
    benchmark = [
        module.BenchmarkConstituentSnapshot(
            analysis_date="2026-05-08",
            symbol="600000.SH",
            weight=0.5,
            return_rate=0.08,
            industry="银行",
        ),
        module.BenchmarkConstituentSnapshot(
            analysis_date="2026-05-08",
            symbol="600519.SH",
            weight=0.5,
            return_rate=0.01,
            industry="食品饮料",
        ),
    ]
    factors = module.FactorExposureSnapshot(
        analysis_date="2026-05-08",
        portfolio={"size": 0.2, "value": 0.1, "momentum": 0.4, "volatility": -0.1, "quality": 0.3},
        benchmark={"size": 0.1, "value": 0.0, "momentum": 0.2, "volatility": 0.0, "quality": 0.1},
    )

    result = module.AttributionEngine().analyze(portfolio=portfolio, benchmark=benchmark, factors=factors)

    assert result.analysis_date == "2026-05-08"
    assert isinstance(result.brinson.allocation_effect, float)
    assert isinstance(result.brinson.selection_effect, float)
    assert isinstance(result.brinson.interaction_effect, float)
    assert len(result.brinson.industry_breakdown) == 2
    assert isinstance(result.factor_attribution.factor_contributions["momentum"], float)
    assert result.factor_attribution.factor_exposures["momentum"].active_exposure == 0.2
    assert result.top_contributors[0].contribution_value >= result.top_contributors[-1].contribution_value
    assert result.top_detractors[0].contribution_value <= result.top_detractors[-1].contribution_value
