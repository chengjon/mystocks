from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.monitoring_control_service import MonitoringControlService


class StubMonitoringService:
    def __init__(self) -> None:
        self.is_monitoring = False
        self.monitored_symbols: list[str] = []
        self.start_calls: list[tuple[list[str] | None, int]] = []
        self.stop_calls = 0

    async def start_monitoring(self, symbols: list[str] | None = None, interval: int = 60) -> None:
        self.start_calls.append((symbols, interval))
        self.is_monitoring = True
        self.monitored_symbols = list(symbols or [])
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            raise

    def stop_monitoring(self) -> None:
        self.stop_calls += 1
        self.is_monitoring = False


def test_monitoring_control_service_starts_once_and_reports_interval() -> None:
    async def run() -> None:
        source = StubMonitoringService()
        service = MonitoringControlService(source, now=lambda: datetime(2026, 5, 14, 9, 30, 0))

        try:
            first_payload = await service.start(symbols=["600519"], interval=30)
            second_payload = await service.start(symbols=["000001"], interval=10)

            assert source.start_calls == [(["600519"], 30)]
            assert first_payload == {
                "is_monitoring": True,
                "monitored_symbols": ["600519"],
                "monitored_count": 1,
                "interval": 30,
            }
            assert second_payload == first_payload
            assert service.get_status()["update_interval"] == 30
        finally:
            await service.stop()

    asyncio.run(run())


def test_monitoring_control_service_stops_and_clears_control_state() -> None:
    async def run() -> None:
        source = StubMonitoringService()
        service = MonitoringControlService(source, now=lambda: datetime(2026, 5, 14, 9, 30, 0))

        await service.start(symbols=["600519", "000001"], interval=45)
        stop_payload = await service.stop()

        assert source.stop_calls == 1
        assert source.monitored_symbols == []
        assert stop_payload == {
            "is_monitoring": False,
            "monitored_symbols": [],
            "monitored_count": 0,
        }
        assert service.get_status() == {
            "is_monitoring": False,
            "monitored_symbols": [],
            "monitored_count": 0,
            "update_interval": None,
        }

    asyncio.run(run())
