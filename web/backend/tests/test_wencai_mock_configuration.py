from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.api import wencai as module


def test_wencai_route_source_contains_no_direct_use_mock_env_reads():
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert 'os.getenv("USE_MOCK_DATA"' not in source


@pytest.mark.asyncio
async def test_get_all_queries_uses_mock_mode_only_from_settings(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)
    monkeypatch.setattr(
        module,
        "_get_mock_wencai_query_bundle",
        lambda query_name: {
            "queries": [
                {
                    "id": 1,
                    "query_name": query_name,
                    "query_text": "mock query",
                    "description": "mock",
                    "is_active": True,
                    "created_at": "2025-10-17T09:00:00",
                    "updated_at": "2025-10-17T09:00:00",
                }
            ]
        },
    )

    result = await module.get_all_queries(db=None)

    assert result.total == 1
    assert result.queries[0].query_name == "all"


@pytest.mark.asyncio
async def test_execute_custom_query_reuses_mock_provider(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)
    monkeypatch.setattr(
        module,
        "_execute_mock_custom_wencai_query",
        lambda query_text, pages: {
            "message": "mock ok",
            "total_records": 1,
            "results": [{"stock_code": "000001", "stock_name": query_text, "pages": pages}],
        },
    )

    request = module.WencaiCustomQueryRequest(query_text="涨幅超过5%的股票", pages=2)
    result = await module.execute_custom_query(request=request, db=None)

    assert result.success is True
    assert result.message == "mock ok"
    assert result.total_records == 1
    assert result.columns == ["stock_code", "stock_name", "pages"]
