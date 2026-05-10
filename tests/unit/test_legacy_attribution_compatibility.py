from __future__ import annotations

from datetime import date

from src.data_sources.mock.business_mock import MockBusinessDataSource
from src.data_sources.real.composite_business import CompositeBusinessDataSource


def test_real_business_attribution_surface_is_marked_legacy_compatibility() -> None:
    source = CompositeBusinessDataSource.__new__(CompositeBusinessDataSource)

    result = source.perform_attribution_analysis(
        user_id=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    compatibility = result["legacy_compatibility"]
    assert compatibility["payload_status"] == "legacy_fallback"
    assert compatibility["canonical_engine"] == "web.backend.app.services.attribution.AttributionEngine"
    assert "/api/v1/backtest/{backtest_id}/attribution" in compatibility["canonical_endpoints"]
    assert "/api/v1/positions/attribution" in compatibility["canonical_endpoints"]


def test_mock_business_attribution_surface_is_marked_demo_fallback() -> None:
    source = MockBusinessDataSource.__new__(MockBusinessDataSource)

    result = source.perform_attribution_analysis(
        user_id=1,
        portfolio=[{"symbol": "600000"}, {"symbol": "000001"}],
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    compatibility = result["legacy_compatibility"]
    assert compatibility["payload_status"] == "mock_legacy_fallback"
    assert compatibility["canonical_engine"] == "web.backend.app.services.attribution.AttributionEngine"
    assert "/api/v1/backtest/{backtest_id}/attribution" in compatibility["canonical_endpoints"]
    assert "/api/v1/positions/attribution" in compatibility["canonical_endpoints"]
