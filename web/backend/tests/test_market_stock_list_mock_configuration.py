from __future__ import annotations

from pathlib import Path

import pytest

from app.api.market import market_data_request as module


def test_market_stock_list_source_contains_no_direct_use_mock_env_reads():
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert 'os.getenv("USE_MOCK_DATA"' not in source


@pytest.mark.asyncio
async def test_market_stock_list_uses_mock_only_when_settings_enable_it(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)
    monkeypatch.setattr(
        module,
        "_get_mock_stock_list",
        lambda **kwargs: {
            "data": [{"symbol": "000001", "name": "平安银行", "kwargs": kwargs}],
        },
    )

    result = await module.get_stock_list(limit=5, search="平安", exchange="SZSE", security_type="stock")

    assert result.success is True
    assert result.data["source"] == "mock"
    assert result.data["stocks"][0]["symbol"] == "000001"
