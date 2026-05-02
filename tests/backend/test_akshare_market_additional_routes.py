import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web/backend")))

from app.api.akshare_market import router
from app.core.security import get_current_user

app = FastAPI()
app.include_router(router)
app.dependency_overrides[get_current_user] = lambda: MagicMock()

client = TestClient(app)


def test_stock_hot_follow_xq_route_returns_success_payload():
    df = pd.DataFrame(
        {
            "symbol": ["600519"],
            "stock_name": ["贵州茅台"],
            "follow_count": [128450],
            "latest_price": [1688.88],
            "query_scope": ["最热门"],
        }
    )

    with patch(
        "app.api.akshare_market.sentiment_monitor.akshare_market_adapter.get_stock_hot_follow_xq",
        new=AsyncMock(return_value=df),
    ):
        response = client.get("/api/akshare/market/stock/hot-follow/xq?symbol=最热门")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["scope"] == "最热门"
    assert payload["data"]["count"] == 1
    assert payload["data"]["provider"] == "xq"


def test_stock_changes_em_route_returns_success_payload():
    df = pd.DataFrame(
        {
            "change_time": ["09:35:21"],
            "symbol": ["600519"],
            "stock_name": ["贵州茅台"],
            "change_type": ["大笔买入"],
            "related_info": ["成交 1200 手"],
            "query_type": ["大笔买入"],
        }
    )

    with patch(
        "app.api.akshare_market.sentiment_monitor.akshare_market_adapter.get_stock_changes_em",
        new=AsyncMock(return_value=df),
    ):
        response = client.get("/api/akshare/market/stock/changes/em?symbol=大笔买入")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["change_type"] == "大笔买入"
    assert payload["data"]["count"] == 1
    assert payload["data"]["provider"] == "em"


def test_board_change_em_route_returns_success_payload():
    df = pd.DataFrame(
        {
            "board_name": ["证券"],
            "change_percent": [3.25],
            "main_net_inflow": [1860000000.0],
            "change_event_count": [12],
        }
    )

    with patch(
        "app.api.akshare_market.sentiment_monitor.akshare_market_adapter.get_stock_board_change_em",
        new=AsyncMock(return_value=df),
    ):
        response = client.get("/api/akshare/market/board/change/em")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["count"] == 1
    assert payload["data"]["provider"] == "em"
    assert payload["data"]["data_type"] == "board_change"
