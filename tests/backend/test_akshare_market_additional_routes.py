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


def test_stock_zt_pool_em_route_returns_success_payload():
    df = pd.DataFrame(
        {
            "sequence_no": [1],
            "symbol": ["603777"],
            "stock_name": ["来伊份"],
            "change_percent": [10.02],
            "latest_price": [24.55],
            "query_date": ["20241008"],
        }
    )

    with patch(
        "app.api.akshare_market.sentiment_monitor.akshare_market_adapter.get_stock_zt_pool_em",
        new=AsyncMock(return_value=df),
    ):
        response = client.get("/api/akshare/market/stock/zt-pool/em?date=20241008")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["date"] == "20241008"
    assert payload["data"]["count"] == 1
    assert payload["data"]["provider"] == "em"
    assert payload["data"]["data_type"] == "zt_pool"


def test_stock_dt_pool_em_route_returns_success_payload():
    df = pd.DataFrame(
        {
            "sequence_no": [1],
            "symbol": ["000001"],
            "stock_name": ["平安银行"],
            "change_percent": [-9.98],
            "latest_price": [8.21],
            "query_date": ["20241011"],
        }
    )

    with patch(
        "app.api.akshare_market.sentiment_monitor.akshare_market_adapter.get_stock_dt_pool_em",
        new=AsyncMock(return_value=df),
    ):
        response = client.get("/api/akshare/market/stock/dt-pool/em?date=20241011")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["date"] == "20241011"
    assert payload["data"]["count"] == 1
    assert payload["data"]["provider"] == "em"
    assert payload["data"]["data_type"] == "dt_pool"


def test_stock_strong_pool_em_route_returns_success_payload():
    df = pd.DataFrame(
        {
            "sequence_no": [1],
            "symbol": ["002594"],
            "stock_name": ["比亚迪"],
            "change_percent": [9.98],
            "selection_reason": ["60日新高"],
            "query_date": ["20241011"],
        }
    )

    with patch(
        "app.api.akshare_market.sentiment_monitor.akshare_market_adapter.get_stock_strong_pool_em",
        new=AsyncMock(return_value=df),
    ):
        response = client.get("/api/akshare/market/stock/strong-pool/em?date=20241011")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["date"] == "20241011"
    assert payload["data"]["count"] == 1
    assert payload["data"]["provider"] == "em"
    assert payload["data"]["data_type"] == "strong_pool"


def test_stock_new_em_route_returns_success_payload():
    df = pd.DataFrame(
        {
            "sequence_no": [1],
            "symbol": ["001389"],
            "stock_name": ["广合科技"],
            "change_percent": [9.99],
            "is_new_high": ["是"],
            "query_date": ["20241011"],
        }
    )

    with patch(
        "app.api.akshare_market.sentiment_monitor.akshare_market_adapter.get_stock_new_em",
        new=AsyncMock(return_value=df),
    ):
        response = client.get("/api/akshare/market/stock/new/em?date=20241011")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["date"] == "20241011"
    assert payload["data"]["count"] == 1
    assert payload["data"]["provider"] == "em"
    assert payload["data"]["data_type"] == "new_pool"
