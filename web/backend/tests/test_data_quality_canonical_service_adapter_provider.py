from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.services.adapters.dashboard_adapter import DashboardDataSourceAdapter
from app.services.adapters.data_adapter import DataDataSourceAdapter


@pytest.mark.asyncio
async def test_dashboard_adapter_uses_injected_quality_monitor_without_global_getter():
    quality_monitor = AsyncMock()
    quality_monitor.evaluate_data_quality = AsyncMock()

    adapter = DashboardDataSourceAdapter({"name": "dashboard-test"}, quality_monitor=quality_monitor)

    with patch(
        "app.services.adapters.dashboard_adapter.get_data_quality_monitor",
        side_effect=AssertionError("global getter should not be used when quality_monitor is injected"),
    ):
        await adapter._trigger_quality_monitoring(
            "summary",
            {"market_overview": {}},
            12.5,
            success=True,
        )

    quality_monitor.evaluate_data_quality.assert_awaited_once_with(
        data={"market_overview": {}},
        source="dashboard:summary",
        response_time=12.5,
        success=True,
    )


@pytest.mark.asyncio
async def test_data_adapter_uses_injected_quality_monitor_without_global_getter():
    quality_monitor = AsyncMock()
    quality_monitor.evaluate_data_quality = AsyncMock()

    adapter = DataDataSourceAdapter({"name": "data-test"}, quality_monitor=quality_monitor)

    with patch(
        "app.services.adapters.data_adapter.get_data_quality_monitor",
        side_effect=AssertionError("global getter should not be used when quality_monitor is injected"),
    ):
        await adapter._trigger_quality_monitoring(
            "stocks/daily",
            {"rows": []},
            9.25,
            success=False,
        )

    quality_monitor.evaluate_data_quality.assert_awaited_once_with(
        data={"rows": []},
        source="data:stocks/daily",
        response_time=9.25,
        success=False,
    )
