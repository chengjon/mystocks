"""OpenStock /quotes + /kline 路由集成测试 (B4.014 M1m / step 7)

验证:
1. /quotes 路由走 factory → OpenStockMarketDataSourceAdapter → build_quotes_response_payload
   返回前端期望 schema: {success, data: {quotes, total, symbols, source, endpoint}}
2. /kline 路由走 factory 成功路径:OpenStock 返回 candles, 不调用 akshare service
3. /kline 二级 fallback:factory 异常或返回空 candles 时回退到 service.get_a_stock_kline
4. quotes factory fallback 到 mock 源(openstock_market_mock)

策略:在模块层 patch `get_data_source_factory` 返回的 mock factory,
避免真实 HTTP/DB 依赖。patch `get_stock_search_service` 避免 akshare 触发。

Plan ref: docs/architecture/M1K_M1M_EXECUTION_PLAN_2026-07-01.md §三 步骤 7
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.market import market_data_request as market_module
from app.core.security import User, get_current_user
from app.main import app
from app.services import data_source_factory as dsf_module


@pytest.fixture
def mock_user():
    return User(
        id=1,
        username="test_user",
        email="test@example.com",
        role="admin",
        is_active=True,
    )


@pytest.fixture
def auth_client(mock_user):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_factory():
    """Mock DataSourceFactory — get_data_with_fallback 可配置返回值或异常。"""
    factory = MagicMock()
    factory.get_data_with_fallback = AsyncMock()
    factory.get_data = AsyncMock()
    factory.get_data_source = AsyncMock(return_value=None)
    return factory


@pytest.fixture
def patch_factory(monkeypatch, mock_factory):
    """Patch dsf_module.get_data_source_factory,使路由 `from ... import get_data_source_factory`
    拿到的 callable 返回 mock_factory。注意路由内部是 lazy import,所以 patch 源模块即可。
    """

    async def _return_mock_factory():
        return mock_factory

    monkeypatch.setattr(
        dsf_module,
        "get_data_source_factory",
        _return_mock_factory,
    )
    return mock_factory


@pytest.fixture
def patch_circuit_breaker(monkeypatch):
    """禁用熔断器。路由 `from app.core.circuit_breaker_manager import get_circuit_breaker`
    是模块级 import(line 27),会绑定到 market_module 全局,所以需要 patch 路由模块属性。
    """
    cb = MagicMock()
    cb.is_open.return_value = False
    cb.record_success = MagicMock()
    cb.record_failure = MagicMock()
    monkeypatch.setattr(
        market_module,
        "get_circuit_breaker",
        lambda name: cb,
    )
    return cb


@pytest.fixture
def patch_stock_search_service(monkeypatch):
    """Mock stock_search_service。路由 lazy import
    `from app.services.stock_search_service import get_stock_search_service`(函数体内),
    patch 包 __init__ 的属性。
    """
    import app.services.stock_search_service as sss_pkg

    service = MagicMock()
    service.get_a_stock_kline = MagicMock(return_value=None)
    monkeypatch.setattr(
        sss_pkg,
        "get_stock_search_service",
        lambda: service,
    )
    return service


# ---------------------------------------------------------------------------
# /quotes 路由
# ---------------------------------------------------------------------------


class TestQuotesRouteViaOpenStockFactory:
    """GET /api/v1/market/quotes → factory → OpenStockMarketDataSourceAdapter envelope"""

    def test_quotes_factory_success_returns_normalized_schema(
        self,
        auth_client,
        patch_factory,
        mock_factory,
    ):
        """Quotes factory 返回 OpenStockMarketDataSourceAdapter 风格 envelope,
        build_quotes_response_payload 应抽出 data 行并归一化 symbol/price 字段。
        """
        rows = [
            {"symbol": "000001", "price": 12.34, "volume": 1000},
            {"symbol": "600519", "price": 1800.0, "volume": 500},
        ]
        mock_factory.get_data_with_fallback.return_value = {
            "status": "success",
            "data": rows,
            "quotes": rows,
            "source": "openstock",
            "endpoint": "quotes",
            "data_category": "REALTIME_QUOTES",
            "parameters": {"symbols": "000001,600519"},
        }

        resp = auth_client.get("/api/v1/market/quotes?symbols=000001,600519")

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["success"] is True
        payload = body["data"]
        assert payload["total"] == 2
        assert payload["source"] == "openstock"
        assert payload["endpoint"] == "quotes"
        syms = {row["symbol"] for row in payload["quotes"]}
        assert syms == {"000001", "600519"}

        mock_factory.get_data_with_fallback.assert_awaited_once()
        call_args, call_kwargs = mock_factory.get_data_with_fallback.call_args
        assert call_args[0] == "openstock_market"
        assert call_args[1] == "quotes"
        # 路由按位置传参 (source_name, endpoint, params)
        assert call_args[2] == {"symbols": ["000001", "600519"]}

    def test_quotes_factory_empty_data_uses_fallback_payload(
        self,
        auth_client,
        patch_factory,
        mock_factory,
    ):
        """Factory 返回空 data 时, build_quotes_response_payload 用 _build_fallback_quotes
        合成兜底行情,前端仍能拿到结构化 quotes。
        """
        mock_factory.get_data_with_fallback.return_value = {
            "status": "success",
            "data": [],
            "quotes": [],
            "source": "openstock",
            "endpoint": "quotes",
        }

        resp = auth_client.get("/api/v1/market/quotes?symbols=000001")

        assert resp.status_code == 200
        body = resp.json()
        payload = body["data"]
        assert payload["total"] == 1
        assert payload["quotes"][0]["symbol"] == "000001"
        # fallback 行情字段齐全
        for key in ("symbol", "price", "change", "change_percent", "volume"):
            assert key in payload["quotes"][0]

    def test_quotes_factory_exception_propagates_to_500(
        self,
        auth_client,
        patch_factory,
        mock_factory,
    ):
        """Factory 抛异常,路由层应包成 BusinessException → 500。"""
        mock_factory.get_data_with_fallback.side_effect = RuntimeError(
            "openstock primary and mock both failed",
        )

        resp = auth_client.get("/api/v1/market/quotes?symbols=000001")

        # 路由 except Exception → BusinessException(detail=..., status_code=500)
        assert resp.status_code in (500,)


# ---------------------------------------------------------------------------
# /kline 路由
# ---------------------------------------------------------------------------


class TestKlineRouteViaOpenStockFactory:
    """GET /api/v1/market/kline → factory primary + service fallback"""

    def test_kline_factory_success_returns_candles_without_service(
        self,
        auth_client,
        patch_factory,
        mock_factory,
        patch_circuit_breaker,
        patch_stock_search_service,
    ):
        """OpenStock factory 成功路径:candles 非空,直接返回,
        不应调用 service.get_a_stock_kline。
        """
        candles = [
            {"datetime": "2026-06-01", "open": 10.0, "high": 11.0, "low": 9.5, "close": 10.5, "volume": 1000},
            {"datetime": "2026-06-02", "open": 10.5, "high": 12.0, "low": 10.4, "close": 11.8, "volume": 2000},
        ]
        mock_factory.get_data_with_fallback.return_value = {
            "status": "success",
            "data": candles,
            "candles": candles,
            "source": "openstock",
            "endpoint": "klines",
        }

        resp = auth_client.get(
            "/api/v1/market/kline?stock_code=000001&period=daily",
        )

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["success"] is True
        assert body["symbol"] == "000001"
        assert body["period"] == "daily"
        assert body["source"] == "openstock"
        assert body["count"] == 2
        assert body["data"] == candles

        mock_factory.get_data_with_fallback.assert_awaited_once()
        call_args, call_kwargs = mock_factory.get_data_with_fallback.call_args
        assert call_args[0] == "openstock_market"
        assert call_args[1] == "klines"
        # 路由按位置传 3 参 (source_name, endpoint, params-dict)
        params = call_args[2]
        assert params["symbol"] == "000001"
        assert params["period"] == "daily"
        assert params["count"] == 60
        # 二级 fallback 未触发
        patch_stock_search_service.get_a_stock_kline.assert_not_called()
        patch_circuit_breaker.record_success.assert_called_once()

    def test_kline_factory_empty_candles_returns_empty_without_service_fallback(
        self,
        auth_client,
        patch_factory,
        mock_factory,
        patch_circuit_breaker,
        patch_stock_search_service,
    ):
        """OpenStock 返回空 candles 列表(停牌股票的合法空响应),
        路由应直接返回 count=0,不触发 akshare 二级 fallback。
        """
        mock_factory.get_data_with_fallback.return_value = {
            "status": "success",
            "data": [],
            "candles": [],
            "source": "openstock",
            "endpoint": "klines",
        }

        resp = auth_client.get(
            "/api/v1/market/kline?stock_code=000001&period=daily",
        )

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["success"] is True
        assert body["count"] == 0
        # 关键:不应触发 akshare fallback
        patch_stock_search_service.get_a_stock_kline.assert_not_called()
        patch_circuit_breaker.record_success.assert_called_once()

    def test_kline_factory_none_candles_triggers_service_fallback(
        self,
        auth_client,
        patch_factory,
        mock_factory,
        patch_circuit_breaker,
        patch_stock_search_service,
    ):
        """OpenStock 返回 None candles(真失败信号),路由应进入 fallback。"""
        mock_factory.get_data_with_fallback.return_value = {
            "status": "success",
            "data": None,
            "candles": None,
            "source": "openstock",
            "endpoint": "klines",
        }
        service_result = {
            "data": [
                {"date": "2026-06-01", "open": 10.0, "close": 10.5},
            ]
            * 20,
            "count": 20,
            "symbol": "000001",
        }
        patch_stock_search_service.get_a_stock_kline.return_value = service_result

        resp = auth_client.get(
            "/api/v1/market/kline?stock_code=000001&period=daily",
        )

        assert resp.status_code == 200, resp.text
        patch_stock_search_service.get_a_stock_kline.assert_called_once()

    def test_kline_factory_exception_triggers_service_fallback(
        self,
        auth_client,
        patch_factory,
        mock_factory,
        patch_circuit_breaker,
        patch_stock_search_service,
    ):
        """OpenStock factory 抛异常,路由 except 分支回退到 service。"""
        mock_factory.get_data_with_fallback.side_effect = RuntimeError(
            "OpenStock HTTP 502",
        )
        service_result = {
            "data": [
                {"date": "2026-06-01", "open": 10.0, "close": 10.5},
            ]
            * 20,
            "count": 20,
            "symbol": "000001",
        }
        patch_stock_search_service.get_a_stock_kline.return_value = service_result

        resp = auth_client.get(
            "/api/v1/market/kline?stock_code=000001&period=daily",
        )

        assert resp.status_code == 200, resp.text
        patch_stock_search_service.get_a_stock_kline.assert_called_once()
        patch_circuit_breaker.record_success.assert_called()

    def test_kline_both_factory_and_service_fail_returns_500(
        self,
        auth_client,
        patch_factory,
        mock_factory,
        patch_circuit_breaker,
        patch_stock_search_service,
    ):
        """OpenStock factory + akshare service 都失败 → 路由抛 BusinessException 500。"""
        mock_factory.get_data_with_fallback.side_effect = RuntimeError("primary down")
        patch_stock_search_service.get_a_stock_kline.side_effect = ConnectionError(
            "akshare offline",
        )

        resp = auth_client.get(
            "/api/v1/market/kline?stock_code=000001&period=daily",
        )

        assert resp.status_code in (500,)
        patch_circuit_breaker.record_failure.assert_called()

    def test_kline_invalid_period_returns_422(self, auth_client, patch_factory):
        """Period 校验失败(pattern mismatch)→ 422, 不应触碰 factory。"""
        resp = auth_client.get(
            "/api/v1/market/kline?stock_code=000001&period=hourly",
        )
        assert resp.status_code == 422

    def test_kline_start_date_derives_count_for_factory_call(
        self,
        auth_client,
        patch_factory,
        mock_factory,
        patch_circuit_breaker,
    ):
        """指定 start_date+end_date 时,路由按天数差推算 count 传给 factory。
        默认 count=60,但日期范围会让 count 接近天数差(为 daily)。
        """
        candles = [{"datetime": "2026-06-01", "open": 10.0, "close": 10.5}] * 30
        mock_factory.get_data_with_fallback.return_value = {
            "status": "success",
            "data": candles,
            "candles": candles,
            "source": "openstock",
            "endpoint": "klines",
        }

        # 30 天范围 → daily count 应 ≈ 30
        resp = auth_client.get(
            "/api/v1/market/kline?stock_code=000001&period=daily&start_date=2026-05-01&end_date=2026-05-31",
        )

        assert resp.status_code == 200, resp.text
        mock_factory.get_data_with_fallback.assert_awaited_once()
        call_args = mock_factory.get_data_with_fallback.call_args[0]
        params = call_args[2]
        assert params["symbol"] == "000001"
        assert params["count"] == 30  # 31 - 1 = 30 天

    def test_kline_default_count_is_60_when_no_start_date(
        self,
        auth_client,
        patch_factory,
        mock_factory,
        patch_circuit_breaker,
    ):
        """不传 start_date 时,count 默认 60。"""
        candles = [{"datetime": "2026-06-01", "open": 10.0, "close": 10.5}] * 60
        mock_factory.get_data_with_fallback.return_value = {
            "status": "success",
            "data": candles,
            "candles": candles,
            "source": "openstock",
            "endpoint": "klines",
        }

        resp = auth_client.get(
            "/api/v1/market/kline?stock_code=000001&period=daily",
        )

        assert resp.status_code == 200
        params = mock_factory.get_data_with_fallback.call_args[0][2]
        assert params["count"] == 60


# ---------------------------------------------------------------------------
# get_data_with_fallback 模块行为 (factory-level 契约验证)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_data_with_fallback_invokes_mock_when_primary_raises():
    """直接验证 DataSourceFactory.get_data_with_fallback 行为:
    primary 抛异常时跳到 {source}_mock。这是路由层依赖的契约。
    """
    from app.services.data_source_factory.data_source_factory import (
        DataSourceFactory,
    )

    factory = DataSourceFactory()

    primary = MagicMock()
    primary.get_data = AsyncMock(side_effect=RuntimeError("primary boom"))
    mock_src = MagicMock()
    mock_src.get_data = AsyncMock(
        return_value={"status": "success", "data": [], "quotes": []},
    )
    factory._data_sources = {
        "openstock_market": primary,
        "openstock_market_mock": mock_src,
    }
    factory._initialized = True

    result = await factory.get_data_with_fallback(
        "openstock_market",
        "quotes",
        {"symbols": "000001"},
    )

    assert result["status"] == "success"
    primary.get_data.assert_awaited_once()
    mock_src.get_data.assert_awaited_once_with(
        "quotes",
        {"symbols": "000001"},
    )


@pytest.mark.asyncio
async def test_get_data_with_fallback_no_mock_propagates_exception():
    """Primary 失败且无 {source}_mock 时,异常应向上抛。"""
    from app.services.data_source_factory.data_source_factory import (
        DataSourceFactory,
    )

    factory = DataSourceFactory()
    primary = MagicMock()
    primary.get_data = AsyncMock(side_effect=RuntimeError("primary boom"))
    factory._data_sources = {"openstock_market": primary}
    factory._initialized = True

    with pytest.raises(RuntimeError, match="primary boom"):
        await factory.get_data_with_fallback(
            "openstock_market",
            "quotes",
            {"symbols": "000001"},
        )
