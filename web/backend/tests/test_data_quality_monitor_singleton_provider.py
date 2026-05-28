from __future__ import annotations

import pytest

from app.services.data_quality_monitor import (
    get_data_quality_monitor,
    monitor_data_quality,
    reset_data_quality_monitor_provider,
    set_data_quality_monitor_provider,
)


class FakeQualityMonitor:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def evaluate_data_quality(
        self,
        data: dict[str, object],
        source: str,
        response_time: float | None = None,
        success: bool = True,
    ) -> dict[str, object]:
        self.calls.append(
            {
                "data": data,
                "source": source,
                "response_time": response_time,
                "success": success,
            }
        )
        return {"source": source, "success": success}


@pytest.fixture(autouse=True)
def reset_monitor_provider():
    reset_data_quality_monitor_provider()
    yield
    reset_data_quality_monitor_provider()


def test_get_data_quality_monitor_uses_registered_provider():
    monitor = FakeQualityMonitor()

    set_data_quality_monitor_provider(lambda: monitor)

    assert get_data_quality_monitor() is monitor


@pytest.mark.asyncio
async def test_monitor_data_quality_uses_registered_provider():
    monitor = FakeQualityMonitor()
    set_data_quality_monitor_provider(lambda: monitor)

    result = await monitor_data_quality(
        data={"timestamp": "2026-05-28T00:00:00Z", "status": "ok"},
        source="unit-test",
        response_time=12.5,
        success=True,
    )

    assert result == {"source": "unit-test", "success": True}
    assert monitor.calls == [
        {
            "data": {"timestamp": "2026-05-28T00:00:00Z", "status": "ok"},
            "source": "unit-test",
            "response_time": 12.5,
            "success": True,
        }
    ]


def test_reset_data_quality_monitor_provider_restores_default_singleton():
    monitor = FakeQualityMonitor()
    set_data_quality_monitor_provider(lambda: monitor)
    assert get_data_quality_monitor() is monitor

    reset_data_quality_monitor_provider()

    default_monitor = get_data_quality_monitor()
    assert default_monitor is get_data_quality_monitor()
    assert default_monitor is not monitor
