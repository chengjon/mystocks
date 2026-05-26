"""Regression tests for the flat API IndicatorRegistry route provider."""

from __future__ import annotations

import asyncio
import inspect
from types import SimpleNamespace

from app.api.indicators import indicator_cache
from app.services import indicator_registry as registry_module
from app.services.indicator_registry import IndicatorCategory, PanelType


class _FakeIndicatorRegistry:
    def __init__(self) -> None:
        self.calls: list[object] = []

    def get_all_indicators(self) -> dict[str, dict[str, object]]:
        self.calls.append("all")
        return {"SMA": _indicator_metadata()}

    def get_indicators_by_category(self, category: IndicatorCategory) -> dict[str, dict[str, object]]:
        self.calls.append(("category", category))
        return {"SMA": _indicator_metadata(category=category)}


def _indicator_metadata(category: IndicatorCategory = IndicatorCategory.TREND) -> dict[str, object]:
    return {
        "full_name": "Simple Moving Average",
        "chinese_name": "简单移动平均线",
        "category": category,
        "description": "Moving average test metadata",
        "panel_type": PanelType.OVERLAY,
        "parameters": [],
        "outputs": [{"name": "sma", "description": "SMA value"}],
        "reference_lines": None,
        "min_data_points_formula": "timeperiod",
    }


def test_indicator_registry_routes_expose_app_state_dependency() -> None:
    dependency = getattr(registry_module, "get_indicator_registry_dependency", None)

    assert dependency is not None

    for handler in (
        indicator_cache.get_indicator_registry_endpoint,
        indicator_cache.get_indicators_by_category,
    ):
        registry_parameter = inspect.signature(handler).parameters["registry"]
        assert getattr(registry_parameter.default, "dependency", None) is dependency


def test_indicator_calculation_routes_expose_data_service_dependency() -> None:
    dependency = getattr(indicator_cache, "get_indicator_data_service", None)

    assert dependency is not None

    for handler in (
        indicator_cache.calculate_indicators,
        indicator_cache.calculate_indicators_batch,
    ):
        data_service_parameter = inspect.signature(handler).parameters["data_service"]
        assert getattr(data_service_parameter.default, "dependency", None) is dependency


def test_indicator_registry_routes_accept_injected_registry() -> None:
    registry = _FakeIndicatorRegistry()
    user = SimpleNamespace(id="route-provider-test")

    registry_response = asyncio.run(
        indicator_cache.get_indicator_registry_endpoint(
            category=None,
            search=None,
            include_advanced=True,
            current_user=user,
            registry=registry,
        )
    )
    category_response = asyncio.run(
        indicator_cache.get_indicators_by_category(
            category="trend",
            registry=registry,
        )
    )

    assert registry.calls == ["all", ("category", IndicatorCategory.TREND)]
    assert registry_response["data"]["total_count"] == 1
    assert registry_response["data"]["indicators"][0]["abbreviation"] == "SMA"
    assert category_response["data"][0]["abbreviation"] == "SMA"
