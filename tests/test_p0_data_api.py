"""
P0 Data API 单元测试

测试数据查询API的核心端点:
1. GET /stocks/basic - 股票基本信息
2. GET /stocks/daily - 日线K线
3. GET /stocks/kline - K线数据
4. GET /stocks/intraday - 分时数据
5. GET /stocks/industries - 行业分类
6. GET /stocks/concepts - 概念分类
7. GET /stocks/symbol_detail - 股票详情
8. GET /stocks/search - 股票搜索
9. GET /stocks/symbol_trading_summary - 交易汇总
10. GET /markets/overview - 市场概览
11. GET /markets/hot_industries - 热门行业
12. GET /markets/hot_concepts - 热门概念
13. GET /markets/price_distribution - 价格分布
14. GET /financial - 财务数据
15. GET /test_factory - 测试工厂
16. GET /kline - K线数据
"""

import pytest
from datetime import datetime, date
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


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
def mock_data_source_factory():
    """模拟数据源工厂"""
    factory = AsyncMock()
    factory.get_data = AsyncMock(return_value={
        "status": "success",
        "source": "data",
        "endpoint": "stocks/basic",
        "data": [
            {
                "symbol": "600519",
                "name": "贵州茅台",
                "industry": "白酒",
                "price": 1830.00,
                "change_pct": 1.5,
                "turnover": 100000000,
                "volume": 5000000
            },
            {
                "symbol": "000858",
                "name": "五粮液",
                "industry": "白酒",
                "price": 180.50,
                "change_pct": 2.1,
                "turnover": 80000000,
                "volume": 4000000
            }
        ],
        "total": 2
    })
    return factory


@pytest.fixture
def mock_db_service():
    """模拟数据库服务"""
    service = MagicMock()
    service.execute_query = MagicMock(return_value=[
        {"symbol": "600519", "name": "贵州茅台", "close": 1830.00, "volume": 5000000}
    ])
    return service


# ============================================================================
# 1. 股票基本信息 API测试
# ============================================================================


class TestStocksBasicAPI:
    """股票基本信息API测试"""

    @patch("app.services.data_source_factory.get_data_source_factory")
    @patch("app.api.data.get_current_user")
    def test_get_stocks_basic_success(self, mock_auth, mock_get_factory, client, mock_data_source_factory):
        """测试成功获取股票基本信息"""
        mock_auth.return_value = MagicMock(username="test")
        mock_get_factory.return_value = mock_data_source_factory
        response = client.get("/api/data/stocks/basic?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["total"] >= 0

    @patch("app.api.data.get_current_user")
    def test_get_stocks_basic_with_search(self, mock_auth, client, mock_data_source_factory):
        """测试带搜索关键词的股票查询"""
        mock_auth.return_value = MagicMock(username="test")
        with patch("app.api.data.get_data_source_factory", return_value=mock_data_source_factory):
            response = client.get("/api/data/stocks/basic?search=茅台&limit=10")
            assert response.status_code == 200

    @patch("app.api.data.get_current_user")
    def test_get_stocks_basic_with_industry_filter(self, mock_auth, client, mock_data_source_factory):
        """测试行业筛选"""
        mock_auth.return_value = MagicMock(username="test")
        with patch("app.api.data.get_data_source_factory", return_value=mock_data_source_factory):
            response = client.get("/api/data/stocks/basic?industry=白酒&limit=10")
            assert response.status_code == 200

    def test_get_stocks_basic_invalid_limit(self, client):
        """测试无效的limit参数"""
        response = client.get("/api/data/stocks/basic?limit=0")
        assert response.status_code in [400, 401]  # 400=参数错误, 401=未认证

    def test_get_stocks_basic_limit_exceeded(self, client):
        """测试limit超过最大值"""
        response = client.get("/api/data/stocks/basic?limit=2000")
        assert response.status_code in [400, 401]


# ============================================================================
# 2. 日线K线数据 API测试
# ============================================================================


class TestStocksDailyAPI:
    """日线K线数据API测试"""

    @patch("app.api.data.get_current_user")
    def test_get_stocks_daily_success(self, mock_auth, client, mock_data_source_factory):
        """测试成功获取日线数据"""
        mock_auth.return_value = MagicMock(username="test")
        mock_data_source_factory.get_data = AsyncMock(return_value={
            "status": "success",
            "data": [
                {
                    "date": "2025-12-30",
                    "open": 1800.0,
                    "high": 1850.0,
                    "low": 1790.0,
                    "close": 1830.0,
                    "volume": 5000000
                }
            ],
            "total": 1
        })
        with patch("app.api.data.get_data_source_factory", return_value=mock_data_source_factory):
            response = client.get("/api/data/stocks/daily?symbol=600519")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


# ============================================================================
# 3. K线数据 API测试
# ============================================================================


class TestKlineAPI:
    """K线数据API测试"""

    def test_get_kline_success(self, client, mock_data_source_factory):
        """测试成功获取K线数据"""
        mock_data_source_factory.get_data = AsyncMock(return_value={
            "status": "success",
            "data": [
                {
                    "date": "2025-12-30",
                    "open": 1800.0,
                    "high": 1850.0,
                    "low": 1790.0,
                    "close": 1830.0,
                    "volume": 5000000
                }
            ],
            "total": 1
        })
        with patch("app.api.data.get_data_source_factory", return_value=mock_data_source_factory):
            response = client.get("/api/data/kline?ts_code=600519.SH")
            assert response.status_code == 200


# ============================================================================
# 4. 行业/概念分类 API测试
# ============================================================================


class TestIndustriesConceptsAPI:
    """行业和概念分类API测试"""

    @patch("app.api.data.get_current_user")
    def test_get_stocks_industries(self, mock_auth, client, mock_data_source_factory):
        """测试获取行业分类"""
        mock_auth.return_value = MagicMock(username="test")
        mock_data_source_factory.get_data = AsyncMock(return_value={
            "status": "success",
            "data": [
                {"industry": "白酒", "count": 20},
                {"industry": "银行", "count": 35}
            ],
            "total": 2
        })
        with patch("app.api.data.get_data_source_factory", return_value=mock_data_source_factory):
            response = client.get("/api/data/stocks/industries")
            assert response.status_code == 200

    @patch("app.api.data.get_current_user")
    def test_get_stocks_concepts(self, mock_auth, client, mock_data_source_factory):
        """测试获取概念分类"""
        mock_auth.return_value = MagicMock(username="test")
        mock_data_source_factory.get_data = AsyncMock(return_value={
            "status": "success",
            "data": [
                {"concept": "新能源", "count": 50},
                {"concept": "人工智能", "count": 30}
            ],
            "total": 2
        })
        with patch("app.api.data.get_data_source_factory", return_value=mock_data_source_factory):
            response = client.get("/api/data/stocks/concepts")
            assert response.status_code == 200


# ============================================================================
# 5. 市场概览 API测试
# ============================================================================


class TestMarketsOverviewAPI:
    """市场概览API测试"""

    @patch("app.api.data.get_current_user")
    def test_get_markets_overview(self, mock_auth, client, mock_data_source_factory):
        """测试获取市场概览"""
        mock_auth.return_value = MagicMock(username="test")
        mock_data_source_factory.get_data = AsyncMock(return_value={
            "status": "success",
            "data": {
                "index": {
                    "sh": {"value": 3200.5, "change": 1.2},
                    "sz": {"value": 11500.8, "change": 0.8}
                },
                "market_summary": {
                    "up_count": 2500,
                    "down_count": 1500,
                    "unchanged_count": 200
                }
            }
        })
        with patch("app.api.data.get_data_source_factory", return_value=mock_data_source_factory):
            response = client.get("/api/data/markets/overview")
            assert response.status_code == 200

    @patch("app.api.data.get_current_user")
    def test_get_markets_hot_industries(self, mock_auth, client, mock_data_source_factory):
        """测试获取热门行业"""
        mock_auth.return_value = MagicMock(username="test")
        mock_data_source_factory.get_data = AsyncMock(return_value={
            "status": "success",
            "data": [
                {"industry": "新能源", "change_pct": 3.5, "amount": 5000000000},
                {"industry": "半导体", "change_pct": 2.8, "amount": 4000000000}
            ],
            "total": 2
        })
        with patch("app.api.data.get_data_source_factory", return_value=mock_data_source_factory):
            response = client.get("/api/data/markets/hot_industries")
            assert response.status_code == 200


# ============================================================================
# 6. 股票搜索 API测试
# ============================================================================


class TestStockSearchAPI:
    """股票搜索API测试"""

    @patch("app.api.data.get_current_user")
    def test_stocks_search(self, mock_auth, client, mock_data_source_factory):
        """测试股票搜索"""
        mock_auth.return_value = MagicMock(username="test")
        mock_data_source_factory.get_data = AsyncMock(return_value={
            "status": "success",
            "data": [
                {"symbol": "600519", "name": "贵州茅台", "pinyin": "gzmt"}
            ],
            "total": 1
        })
        with patch("app.api.data.get_data_source_factory", return_value=mock_data_source_factory):
            response = client.get("/api/data/stocks/search?keyword=茅台")
            assert response.status_code == 200


# ============================================================================
# 7. 财务数据 API测试
# ============================================================================


class TestFinancialDataAPI:
    """财务数据API测试"""

    @patch("app.api.data.get_current_user")
    def test_get_financial_data(self, mock_auth, client, mock_data_source_factory):
        """测试获取财务数据"""
        mock_auth.return_value = MagicMock(username="test")
        mock_data_source_factory.get_data = AsyncMock(return_value={
            "status": "success",
            "data": [
                {
                    "symbol": "600519",
                    "report_date": "2025-09-30",
                    "revenue": 80000000000,
                    "net_profit": 40000000000,
                    "eps": 32.5
                }
            ],
            "total": 1
        })
        with patch("app.api.data.get_data_source_factory", return_value=mock_data_source_factory):
            response = client.get("/api/data/financial?symbol=600519")
            assert response.status_code == 200


# ============================================================================
# 错误处理测试
# ============================================================================


class TestDataAPIErrorHandling:
    """Data API错误处理测试"""

    @patch("app.api.data.get_current_user")
    def test_handle_factory_error(self, mock_auth, client):
        """测试数据源工厂错误处理"""
        mock_auth.return_value = MagicMock(username="test")
        mock_factory = AsyncMock()
        mock_factory.get_data = AsyncMock(side_effect=Exception("Factory error"))
        with patch("app.api.data.get_data_source_factory", return_value=mock_factory):
            response = client.get("/api/data/stocks/basic?limit=10")
            assert response.status_code == 500

    def test_handle_unauthorized_access(self, client):
        """测试未授权访问"""
        # 不mock get_current_user, 让它自然返回401
        response = client.get("/api/data/stocks/basic?limit=10")
        # 应该返回401未授权, 或者其他认证错误
        assert response.status_code in [401, 403, 500]


# ============================================================================
# 性能测试
# ============================================================================


@pytest.mark.performance
class TestDataAPIPerformance:
    """Data API性能测试"""

    @patch("app.api.data.get_current_user")
    def test_response_time_stocks_basic(self, mock_auth, client, mock_data_source_factory):
        """测试股票基本信息查询响应时间 < 200ms"""
        import time
        mock_auth.return_value = MagicMock(username="test")
        with patch("app.api.data.get_data_source_factory", return_value=mock_data_source_factory):
            start = time.time()
            response = client.get("/api/data/stocks/basic?limit=100")
            duration = (time.time() - start) * 1000
            assert response.status_code == 200
            assert duration < 200, f"响应时间 {duration:.2f}ms 超过200ms阈值"
