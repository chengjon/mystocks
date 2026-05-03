from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_type_extension_compatibility_smoke_fixture_exists() -> None:
    fixture = PROJECT_ROOT / "web/frontend/src/api/types/compatibility-smoke.ts"

    assert fixture.is_file()

    source = fixture.read_text(encoding="utf-8")

    assert 'from "@/api/types"' in source
    assert 'from "@/api/types/extensions"' in source
    assert "TypeExtensionCompatibilitySmoke" in source
    assert "FormValidationSchema" in source
    assert "FormValidationState" in source
    assert "StrategyComparisonDataVM" in source
    assert "StrategyOptimizationRequestVM" in source
    assert "StrategyOptimizationResultVM" in source
    assert "PaginatedResponseVM" in source
    assert "APIErrorVM" in source
    assert "PaginationParamsVM" in source
    assert "SearchParamsVM" in source
    assert "FilterParamsVM" in source
    assert "SortParamsVM" in source
    assert "ValidationResultVM" in source
    assert "UploadResultVM" in source
    assert "UploadProgressVM" in source
    assert "WSSubscriptionVM" in source
    assert "WSDataMessageVM" in source
    assert "WSErrorMessageVM" in source
    assert "WSSubscription" in source
    assert "WSDataMessage" in source
    assert "SearchParams" in source
    assert "UploadResult" in source
    assert "KeysOfType" in source
    assert "AsyncFunction" in source
    assert "TimeoutOptions" in source
    assert "HttpMethod" in source
    assert "LoadingState" in source
    assert "LanguageCode" in source
    assert "CurrencyCode" in source
