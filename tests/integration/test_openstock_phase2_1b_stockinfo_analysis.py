"""Phase 2.1b 集成 smoke test — 个股信息 + 分析预测域直接消费 OpenStock.

env-gated: 未设置 OPENSTOCK_BASE_URL 时整模块 skip。
对迁移到 OpenStockClient 的端点逐一验证响应结构,不 assert 具体数据值(避免非确定性失败)。
OPENSTOCK_GAP 端点(雪球/同花顺/评级/筹码/技术指标/账户统计/SSE/SZSE)不在本文件覆盖。
"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENSTOCK_BASE_URL"),
    reason="OPENSTOCK_BASE_URL not set; live OpenStock gateway required",
)


@pytest.fixture(scope="module")
def test_client():
    try:
        from fastapi.testclient import TestClient
        from app.core.security import get_current_user
        from app.main import app

        app.dependency_overrides[get_current_user] = lambda: None
        return TestClient(app)
    except ImportError as e:
        pytest.skip(f"app import failed (pre-existing): {e}")


def _assert_openstock_payload(resp, expected_extra_fields: set[str] | None = None):
    """断言响应为 OpenStock 网关成功载荷,且 data 为记录列表."""
    body = resp.json()
    payload = body.get("data")
    assert payload is not None, f"missing data payload: {body}"
    assert isinstance(payload, dict), f"data payload should be dict, got {type(payload)}"
    assert "data" in payload
    assert "count" in payload
    assert "columns" in payload
    assert payload["source"] == "openstock"
    if expected_extra_fields:
        for f in expected_extra_fields:
            assert f in payload, f"missing field {f} in payload {list(payload.keys())}"


class TestStockInfo:
    def test_individual_info_em(self, test_client):
        r = test_client.get("/api/akshare/market/stock/individual-info/em", params={"symbol": "000001"})
        _assert_openstock_payload(r, {"symbol"})

    def test_business_composition_em(self, test_client):
        r = test_client.get("/api/akshare/market/stock/business-composition/em", params={"symbol": "000001"})
        _assert_openstock_payload(r, {"symbol"})

    def test_news_em(self, test_client):
        r = test_client.get("/api/akshare/market/stock/news/em", params={"symbol": "000001"})
        _assert_openstock_payload(r, {"symbol"})

    def test_bid_ask_em(self, test_client):
        r = test_client.get("/api/akshare/market/stock/bid-ask/em", params={"symbol": "000001"})
        _assert_openstock_payload(r, {"symbol"})


class TestAnalysis:
    def test_profit_forecast_em(self, test_client):
        r = test_client.get("/api/akshare/market/forecast/profit/em/000001")
        _assert_openstock_payload(r, {"symbol", "forecast_type"})