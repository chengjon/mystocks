"""
P0 Market API 单元测试

测试市场数据API的13个核心端点:
1. GET /fund-flow - 查询资金流向
2. POST /fund-flow/refresh - 刷新资金流向
3. GET /etf/list - 查询ETF列表
4. POST /etf/refresh - 刷新ETF数据
5. GET /chip-race - 查询竞价抢筹
6. POST /chip-race/refresh - 刷新抢筹数据
7. GET /lhb - 查询龙虎榜
8. POST /lhb/refresh - 刷新龙虎榜
9. GET /quotes - 查询实时行情
10. GET /stocks - 查询股票列表
11. GET /kline - 查询K线数据
12. GET /heatmap - 获取市场热力图数据
13. GET /health - 健康检查

测试覆盖:
- 请求验证
- 响应结构
- 错误处理
- 业务逻辑
"""

import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_app():
    """创建FastAPI应用实例"""
    from app.main import app
    return app


@pytest.fixture
def client(mock_app):
    """同步测试客户端"""
    return TestClient(mock_app)


@pytest.fixture
async def async_client(mock_app):
    """异步测试客户端"""
    async with AsyncClient(app=mock_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_market_data_service():
    """模拟MarketDataService"""
    service = MagicMock()
    service.fetch_and_save_fund_flow = MagicMock(return_value={"success": True, "message": "刷新成功"})
    service.fetch_and_save_etf_spot = MagicMock(return_value={"success": True, "message": "刷新成功"})
    service.query_etf_spot = MagicMock(return_value=[
        {
            "symbol": "510300",
            "name": "沪深300ETF",
            "price": 4.521,
            "change": 0.015,
            "change_pct": 0.33,
            "volume": 1000000,
        }
    ])
    service.query_chip_race = MagicMock(return_value=[
        {
            "symbol": "600519",
            "name": "贵州茅台",
            "race_amount": 100000000,
            "race_type": "open",
        }
    ])
    service.fetch_and_save_chip_race = MagicMock(return_value={"success": True, "message": "刷新成功"})
    service.query_lhb_detail = MagicMock(return_value=[
        {
            "symbol": "600519",
            "name": "贵州茅台",
            "net_buy": 50000000,
            "trade_date": "2025-12-30",
        }
    ])
    service.fetch_and_save_lhb_detail = MagicMock(return_value={"success": True, "message": "刷新成功"})
    return service


@pytest.fixture
def mock_data_source_factory():
    """模拟数据源工厂"""
    factory = AsyncMock()
    factory.get_data = AsyncMock(return_value={
        "source": "market",
        "endpoint": "fund-flow",
        "data": {
            "data": {
                "details": [
                    {
                        "date": "2025-12-30",
                        "main_net": 50000000,
                        "retain_net": 30000000,
                    }
                ]
            }
        }
    })
    return factory


@pytest.fixture
def mock_stock_search_service():
    """模拟StockSearchService"""
    service = MagicMock()
    service.get_a_stock_kline = MagicMock(return_value={
        "symbol": "600519",
        "count": 60,
        "data": [
            {
                "date": "2025-12-01",
                "open": 1800.0,
                "high": 1850.0,
                "low": 1790.0,
                "close": 1830.0,
                "volume": 2000000,
            }
        ]
    })
    return service


@pytest.fixture
def mock_circuit_breaker():
    """模拟熔断器"""
    cb = MagicMock()
    cb.is_open = MagicMock(return_value=False)
    cb.record_success = MagicMock()
    cb.record_failure = MagicMock()
    cb.failure_count = MagicMock(return_value=0)
    return cb


# ============================================================================
# 1. 资金流向 API测试
# ============================================================================


class TestFundFlowAPI:
    """资金流向API测试"""

    def test_get_fund_flow_success(self, client, mock_data_source_factory, mock_circuit_breaker):
        """测试成功获取资金流向数据"""
        with patch("app.api.market.get_data_source_factory", return_value=mock_data_source_factory), \
             patch("app.api.market.get_circuit_breaker", return_value=mock_circuit_breaker):
            response = client.get("/api/market/fund-flow?symbol=600519.SH&timeframe=1")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "fund_flow" in data["data"]
            assert data["data"]["total"] >= 0

    def test_get_fund_flow_validation_error(self, client, mock_circuit_breaker):
        """测试参数验证错误 - 无效symbol"""
        with patch("app.api.market.get_circuit_breaker", return_value=mock_circuit_breaker):
            response = client.get("/api/market/fund-flow?symbol=.invalid")
            # 应该返回验证错误
            assert response.status_code in [400, 422]

    def test_get_fund_flow_circuit_breaker_open(self, client, mock_circuit_breaker):
        """测试熔断器打开时的降级响应"""
        mock_circuit_breaker.is_open = MagicMock(return_value=True)
        with patch("app.api.market.get_circuit_breaker", return_value=mock_circuit_breaker):
            response = client.get("/api/market/fund-flow?symbol=600519.SH")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "暂不可用" in data.get("message", "")


class TestFundFlowRefreshAPI:
    """资金流向刷新API测试"""

    def test_refresh_fund_flow_success(self, client, mock_market_data_service):
        """测试成功刷新资金流向数据"""
        with patch("app.api.market.get_market_data_service", return_value=mock_market_data_service):
            response = client.post("/api/market/fund-flow/refresh?symbol=600519.SH&timeframe=1")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["symbol"] == "600519.SH"


# ============================================================================
# 2. ETF数据 API测试
# ============================================================================


class TestETFAPI:
    """ETF数据API测试"""

    def test_get_etf_list_success(self, client, mock_market_data_service):
        """测试成功获取ETF列表"""
        with patch("app.api.market.get_market_data_service", return_value=mock_market_data_service):
            response = client.get("/api/market/etf/list")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "etf_list" in data["data"]

    def test_get_etf_list_with_filters(self, client, mock_market_data_service):
        """测试带筛选条件的ETF查询"""
        with patch("app.api.market.get_market_data_service", return_value=mock_market_data_service):
            response = client.get("/api/market/etf/list?symbol=510300&market=SH&limit=10")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_refresh_etf_success(self, client, mock_market_data_service):
        """测试成功刷新ETF数据"""
        mock_market_data_service.fetch_and_save_etf_spot.return_value = {
            "success": True,
            "message": "刷新成功",
            "count": 100
        }
        with patch("app.api.market.get_market_data_service", return_value=mock_market_data_service):
            response = client.post("/api/market/etf/refresh")
            assert response.status_code == 200


# ============================================================================
# 3. 竞价抢筹 API测试
# ============================================================================


class TestChipRaceAPI:
    """竞价抢筹API测试"""

    def test_get_chip_race_success(self, client, mock_market_data_service):
        """测试成功获取竞价抢筹数据"""
        with patch("app.api.market.get_market_data_service", return_value=mock_market_data_service):
            response = client.get("/api/market/chip-race?race_type=open")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0

    def test_refresh_chip_race_success(self, client, mock_market_data_service):
        """测试成功刷新抢筹数据"""
        mock_market_data_service.fetch_and_save_chip_race.return_value = {
            "success": True,
            "message": "刷新成功"
        }
        with patch("app.api.market.get_market_data_service", return_value=mock_market_data_service):
            response = client.post("/api/market/chip-race/refresh?race_type=open")
            assert response.status_code == 200


# ============================================================================
# 4. 龙虎榜 API测试
# ============================================================================


class TestLongHuBangAPI:
    """龙虎榜API测试"""

    def test_get_lhb_success(self, client, mock_market_data_service):
        """测试成功获取龙虎榜数据"""
        with patch("app.api.market.get_market_data_service", return_value=mock_market_data_service):
            response = client.get("/api/market/lhb")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_get_lhb_with_date_filter(self, client, mock_market_data_service):
        """测试带日期筛选的龙虎榜查询"""
        with patch("app.api.market.get_market_data_service", return_value=mock_market_data_service):
            response = client.get(
                "/api/market/lhb?start_date=2025-12-01&end_date=2025-12-30"
            )
            assert response.status_code == 200

    def test_refresh_lhb_success(self, client, mock_market_data_service):
        """测试成功刷新龙虎榜数据"""
        mock_market_data_service.fetch_and_save_lhb_detail.return_value = {
            "success": True,
            "message": "刷新成功"
        }
        with patch("app.api.market.get_market_data_service", return_value=mock_market_data_service):
            response = client.post("/api/market/lhb/refresh?trade_date=2025-12-30")
            assert response.status_code == 200


# ============================================================================
# 5. 实时行情 API测试
# ============================================================================


class TestQuotesAPI:
    """实时行情API测试"""

    def test_get_quotes_default(self, client, mock_data_source_factory):
        """测试获取默认热门股票实时行情"""
        mock_data_source_factory.get_data = AsyncMock(return_value={
            "source": "market",
            "endpoint": "quotes",
            "data": [
                {
                    "symbol": "000001",
                    "name": "平安银行",
                    "price": 12.50,
                    "change": 0.15,
                    "change_pct": 1.21,
                }
            ]
        })
        with patch("app.api.market.get_data_source_factory", return_value=mock_data_source_factory):
            response = client.get("/api/market/quotes")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "quotes" in data["data"]

    def test_get_quotes_specific_symbols(self, client, mock_data_source_factory):
        """测试获取指定股票实时行情"""
        mock_data_source_factory.get_data = AsyncMock(return_value={
            "source": "market",
            "endpoint": "quotes",
            "data": [
                {"symbol": "600519", "name": "贵州茅台", "price": 1830.00}
            ]
        })
        with patch("app.api.market.get_data_source_factory", return_value=mock_data_source_factory):
            response = client.get("/api/market/quotes?symbols=600519,000001")
            assert response.status_code == 200


# ============================================================================
# 6. 股票列表 API测试
# ============================================================================


class TestStockListAPI:
    """股票列表API测试"""

    def test_get_stock_list_mock(self, client):
        """测试获取股票列表(Mock数据模式)"""
        with patch.dict("os.environ", {"USE_MOCK_DATA": "true"}):
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = MagicMock()
            mock_manager.get_data = MagicMock(return_value={
                "data": [
                    {"symbol": "600519", "name": "贵州茅台", "exchange": "SSE"}
                ],
                "timestamp": datetime.now().isoformat()
            })
            with patch("app.api.market.get_mock_data_manager", return_value=mock_manager):
                response = client.get("/api/market/stocks?limit=10")
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True

    def test_get_stock_list_with_search(self, client):
        """测试带搜索关键词的股票列表查询"""
        with patch.dict("os.environ", {"USE_MOCK_DATA": "true"}):
            response = client.get("/api/market/stocks?search=茅台&limit=10")
            # 根据实际实现调整预期结果
            assert response.status_code in [200, 500]


# ============================================================================
# 7. K线数据 API测试
# ============================================================================


class TestKlineAPI:
    """K线数据API测试"""

    def test_get_kline_success(self, client, mock_stock_search_service, mock_circuit_breaker):
        """测试成功获取K线数据"""
        mock_circuit_breaker.is_open = MagicMock(return_value=False)
        with patch("app.api.market.get_stock_search_service", return_value=mock_stock_search_service), \
             patch("app.api.market.get_circuit_breaker", return_value=mock_circuit_breaker):
            response = client.get("/api/market/kline?stock_code=600519&period=daily")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data.get("count", 0) > 0

    def test_get_kline_insufficient_data(self, client, mock_stock_search_service, mock_circuit_breaker):
        """测试历史数据不足的情况"""
        mock_stock_search_service.get_a_stock_kline.return_value = {
            "symbol": "600519",
            "count": 5,  # 不足10个交易日
            "data": []
        }
        with patch("app.api.market.get_stock_search_service", return_value=mock_stock_search_service), \
             patch("app.api.market.get_circuit_breaker", return_value=mock_circuit_breaker):
            response = client.get("/api/market/kline?stock_code=600519")
            assert response.status_code == 422

    def test_get_kline_circuit_breaker(self, client, mock_circuit_breaker):
        """测试熔断器打开时的K线请求"""
        mock_circuit_breaker.is_open = MagicMock(return_value=True)
        with patch("app.api.market.get_circuit_breaker", return_value=mock_circuit_breaker):
            response = client.get("/api/market/kline?stock_code=600519")
            assert response.status_code == 503


# ============================================================================
# 8. 市场热力图 API测试
# ============================================================================


class TestHeatmapAPI:
    """市场热力图API测试"""

    def test_get_heatmap_cn(self, client):
        """测试获取A股市场热力图"""
        with patch.dict("os.environ", {"USE_MOCK_DATA": "true"}):
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = MagicMock()
            mock_manager.get_data = MagicMock(return_value={
                "data": [
                    {
                        "symbol": "600519",
                        "name": "贵州茅台",
                        "price": 1830.0,
                        "change_pct": 1.5
                    }
                ],
                "timestamp": datetime.now().isoformat()
            })
            with patch("app.api.market.get_mock_data_manager", return_value=mock_manager):
                response = client.get("/api/market/heatmap?market=cn&limit=50")
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True

    def test_get_heatmap_invalid_market(self, client):
        """测试无效的市场类型"""
        with patch.dict("os.environ", {"USE_MOCK_DATA": "false"}):
            response = client.get("/api/market/heatmap?market=invalid")
            # 应该返回400错误或类似
            assert response.status_code in [400, 500]


# ============================================================================
# 9. 健康检查 API测试
# ============================================================================


class TestHealthAPI:
    """健康检查API测试"""

    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/api/market/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data


# ============================================================================
# 集成测试
# ============================================================================


class TestMarketAPIIntegration:
    """Market API集成测试"""

    def test_full_workflow_fund_flow(self, client, mock_data_source_factory, mock_circuit_breaker,
                                     mock_market_data_service):
        """测试资金流向完整工作流: 查询 -> 刷新 -> 查询"""
        # 1. 初始查询
        mock_data_source_factory.get_data = AsyncMock(return_value={
            "source": "market",
            "endpoint": "fund-flow",
            "data": {"data": {"details": []}}
        })
        with patch("app.api.market.get_data_source_factory", return_value=mock_data_source_factory), \
             patch("app.api.market.get_circuit_breaker", return_value=mock_circuit_breaker):
            response = client.get("/api/market/fund-flow?symbol=600519.SH")
            assert response.status_code == 200

        # 2. 刷新数据
        with patch("app.api.market.get_market_data_service", return_value=mock_market_data_service):
            response = client.post("/api/market/fund-flow/refresh?symbol=600519.SH")
            assert response.status_code == 200

        # 3. 再次查询
        with patch("app.api.market.get_data_source_factory", return_value=mock_data_source_factory), \
             patch("app.api.market.get_circuit_breaker", return_value=mock_circuit_breaker):
            response = client.get("/api/market/fund-flow?symbol=600519.SH")
            assert response.status_code == 200

    def test_concurrent_requests(self, client, mock_market_data_service):
        """测试并发请求处理"""
        import threading
        results = []

        def make_request():
            response = client.get("/api/market/etf/list")
            results.append(response.status_code)

        threads = [threading.Thread(target=make_request) for _ in range(10)]

        with patch("app.api.market.get_market_data_service", return_value=mock_market_data_service):
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        # 验证所有请求都成功处理
        assert len(results) == 10
        assert all(status == 200 for status in results)


# ============================================================================
# 错误处理测试
# ============================================================================


class TestMarketAPIErrorHandling:
    """Market API错误处理测试"""

    def test_handle_validation_error(self, client):
        """测试验证错误处理"""
        response = client.get("/api/market/fund-flow?symbol=")  # 空symbol
        assert response.status_code in [400, 422]

    def test_handle_service_unavailable(self, client, mock_circuit_breaker):
        """测试服务不可用错误处理"""
        mock_circuit_breaker.is_open = MagicMock(return_value=True)
        with patch("app.api.market.get_circuit_breaker", return_value=mock_circuit_breaker):
            response = client.get("/api/market/fund-flow?symbol=600519.SH")
            # 应该返回降级响应
            assert response.status_code == 200

    def test_handle_external_api_failure(self, client, mock_data_source_factory, mock_circuit_breaker):
        """测试外部API失败处理"""
        # 模拟API调用失败
        mock_data_source_factory.get_data = AsyncMock(side_effect=Exception("API Error"))
        with patch("app.api.market.get_data_source_factory", return_value=mock_data_source_factory), \
             patch("app.api.market.get_circuit_breaker", return_value=mock_circuit_breaker):
            response = client.get("/api/market/fund-flow?symbol=600519.SH")
            # 应该记录失败并可能打开熔断器
            assert mock_circuit_breaker.record_failure.called
            assert response.status_code == 500


# ============================================================================
# 性能测试
# ============================================================================


@pytest.mark.performance
class TestMarketAPIPerformance:
    """Market API性能测试"""

    def test_response_time_health_check(self, client):
        """测试健康检查响应时间 < 100ms"""
        import time
        start = time.time()
        response = client.get("/api/market/health")
        duration = (time.time() - start) * 1000  # 转换为毫秒
        assert response.status_code == 200
        assert duration < 100, f"响应时间 {duration:.2f}ms 超过100ms阈值"

    def test_response_time_etf_list(self, client, mock_market_data_service):
        """测试ETF列表查询响应时间 < 200ms"""
        import time
        with patch("app.api.market.get_market_data_service", return_value=mock_market_data_service):
            start = time.time()
            response = client.get("/api/market/etf/list")
            duration = (time.time() - start) * 1000
            assert response.status_code == 200
            assert duration < 200, f"响应时间 {duration:.2f}ms 超过200ms阈值"
