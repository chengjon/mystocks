from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.api.stock_search import stock_search_result as module
from app.core.exceptions import BusinessException


class _CircuitBreakerStub:
    def __init__(self, *, open_state: bool) -> None:
        self._open_state = open_state
        self.failure_count = 0

    def is_open(self) -> bool:
        return self._open_state

    def record_success(self) -> None:
        return None

    def record_failure(self) -> None:
        self.failure_count += 1


@pytest.mark.asyncio
async def test_search_stocks_returns_503_when_circuit_open_and_mock_fallback_disabled(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", False, raising=False)
    monkeypatch.setattr(module.settings, "stock_search_mock_enabled", False, raising=False)
    monkeypatch.setattr(module.settings, "stock_search_mock_fallback_enabled", False, raising=False)
    monkeypatch.setattr(module, "check_search_rate_limit", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(module, "log_search_operation", lambda **_kwargs: None)
    monkeypatch.setattr(module, "get_circuit_breaker", lambda _service: _CircuitBreakerStub(open_state=True))

    with pytest.raises(BusinessException) as exc_info:
        await module.search_stocks(
            q="平安银行",
            market="auto",
            page=1,
            page_size=20,
            sort_by="name",
            sort_order="desc",
            current_user=SimpleNamespace(id=1, username="tester"),
        )

    assert exc_info.value.status_code == 503
    assert exc_info.value.error_code == "SERVICE_UNAVAILABLE"


@pytest.mark.asyncio
async def test_search_stocks_uses_mock_when_fallback_explicitly_enabled(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", False, raising=False)
    monkeypatch.setattr(module.settings, "stock_search_mock_enabled", False, raising=False)
    monkeypatch.setattr(module.settings, "stock_search_mock_fallback_enabled", True, raising=False)
    monkeypatch.setattr(module, "check_search_rate_limit", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(module, "log_search_operation", lambda **_kwargs: None)
    monkeypatch.setattr(module, "get_circuit_breaker", lambda _service: _CircuitBreakerStub(open_state=True))
    monkeypatch.setattr(
        module,
        "_get_mock_stock_search_results",
        lambda keyword, market, limit: [{"symbol": "000001", "name": keyword, "market": market, "score": limit}],
    )

    result = await module.search_stocks(
        q="平安银行",
        market="auto",
        page=1,
        page_size=20,
        sort_by="name",
        sort_order="desc",
        current_user=SimpleNamespace(id=1, username="tester"),
    )

    assert len(result) == 1
    assert result[0]["symbol"] == "000001"
    assert result[0]["name"] == "平安银行"
