from __future__ import annotations

import pytest

from app.services.market_data_adapter import MarketDataSourceAdapter


class FakeQualityMonitor:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def evaluate_data_quality(
        self,
        *,
        data: dict[str, object],
        source: str,
        response_time: float,
        success: bool,
    ) -> None:
        self.calls.append(
            {
                "data": data,
                "source": source,
                "response_time": response_time,
                "success": success,
            }
        )


@pytest.mark.asyncio
async def test_market_data_adapter_uses_injected_quality_monitor(monkeypatch):
    def fail_getter():
        raise AssertionError("module-level getter should not be called")

    monkeypatch.setattr("app.services.market_data_adapter.get_data_quality_monitor", fail_getter)
    monitor = FakeQualityMonitor()

    adapter = MarketDataSourceAdapter({"mode": "mock"}, quality_monitor=monitor)

    await adapter._trigger_quality_monitoring(
        endpoint="fund-flow",
        data={"symbol": "000001"},
        response_time=12.5,
        success=True,
    )

    assert monitor.calls == [
        {
            "data": {"symbol": "000001"},
            "source": "market:fund-flow",
            "response_time": 12.5,
            "success": True,
        }
    ]


@pytest.mark.asyncio
async def test_market_data_adapter_preserves_default_quality_monitor_fallback(monkeypatch):
    monitor = FakeQualityMonitor()
    monkeypatch.setattr("app.services.market_data_adapter.get_data_quality_monitor", lambda: monitor)

    adapter = MarketDataSourceAdapter({"mode": "mock"})

    await adapter._trigger_quality_monitoring(
        endpoint="quotes",
        data=None,
        response_time=4.0,
        success=False,
    )

    assert monitor.calls == [
        {
            "data": {},
            "source": "market:quotes",
            "response_time": 4.0,
            "success": False,
        }
    ]
