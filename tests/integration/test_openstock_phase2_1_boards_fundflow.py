"""Phase 2.1a 集成 smoke test — 板块 + 资金流域直接消费 OpenStock.

env-gated: 未设置 OPENSTOCK_BASE_URL 时整模块 skip。
对迁移到 OpenStockClient 的端点逐一验证响应结构,不 assert 具体数据值(避免非确定性失败)。
OPENSTOCK_GAP 端点(分钟板块/南向/big-deal)不在本文件覆盖。
"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENSTOCK_BASE_URL"),
    reason="OPENSTOCK_BASE_URL not set; live OpenStock gateway required",
)


@pytest.fixture(scope="module")
def test_client():
    # 预存 import 错误(ETFQueryParams 等),用 try/except 避免整模块崩溃
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


class TestBoards:
    def test_concept_constituents(self, test_client):
        r = test_client.get("/api/akshare/market/board/concept/cons/BK0566")
        _assert_openstock_payload(r, {"board_type", "symbol"})

    def test_industry_constituents(self, test_client):
        r = test_client.get("/api/akshare/market/board/industry/cons/BK0475")
        _assert_openstock_payload(r, {"board_type", "symbol"})

    def test_concept_history(self, test_client):
        r = test_client.get(
            "/api/akshare/market/board/concept/history/BK0566",
            params={"start_date": "2024-01-01", "end_date": "2024-01-05"},
        )
        _assert_openstock_payload(r, {"board_type", "data_type"})

    def test_industry_history(self, test_client):
        r = test_client.get(
            "/api/akshare/market/board/industry/history/BK0475",
            params={"start_date": "2024-01-01", "end_date": "2024-01-05"},
        )
        _assert_openstock_payload(r, {"board_type", "data_type"})

    def test_sector_hot_ranking(self, test_client):
        r = test_client.get("/api/akshare/market/sector/hot-ranking")
        _assert_openstock_payload(r, {"ranking_type"})

    def test_sector_fund_flow_ranking(self, test_client):
        r = test_client.get("/api/akshare/market/sector/fund-flow-ranking")
        _assert_openstock_payload(r, {"ranking_type"})


class TestFundFlow:
    def test_hsgt_fund_flow_summary(self, test_client):
        r = test_client.get(
            "/api/akshare/market/fund-flow/hsgt-summary",
            params={"start_date": "2024-01-01", "end_date": "2024-01-05"},
        )
        _assert_openstock_payload(r, {"date_range"})

    def test_north_fund_daily(self, test_client):
        r = test_client.get(
            "/api/akshare/market/fund-flow/north-daily",
            params={"start_date": "2024-01-01", "end_date": "2024-01-05"},
        )
        _assert_openstock_payload(r, {"fund_direction"})

    def test_north_fund_stock(self, test_client):
        r = test_client.get("/api/akshare/market/fund-flow/north-stock/600519")
        _assert_openstock_payload(r, {"fund_direction", "symbol"})

    def test_hsgt_holdings(self, test_client):
        r = test_client.get("/api/akshare/market/fund-flow/hsgt-holdings/600519")
        _assert_openstock_payload(r, {"symbol"})