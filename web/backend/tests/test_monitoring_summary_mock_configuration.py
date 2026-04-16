from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.api import monitoring as module


def test_monitoring_summary_source_contains_no_direct_use_mock_env_reads():
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert 'os.getenv("USE_MOCK_DATA"' not in source


@pytest.mark.asyncio
async def test_monitoring_summary_uses_mock_provider_when_settings_enable_it(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)
    monkeypatch.setattr(
        module,
        "_get_mock_monitoring_summary",
        lambda: {
            "total_stocks": 1,
            "limit_up_count": 2,
            "limit_down_count": 3,
            "strong_up_count": 4,
            "strong_down_count": 5,
            "avg_change_percent": 0.5,
            "total_amount": 1000.0,
            "active_alerts": 6,
            "unread_alerts": 7,
        },
    )

    result = await module.get_monitoring_summary(current_user=SimpleNamespace(id=1, username="tester"))

    assert result.total_stocks == 1
    assert result.unread_alerts == 7
