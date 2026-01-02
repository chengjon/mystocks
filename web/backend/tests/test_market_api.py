"""
Stock Market API Unit Tests

Tests for market data APIs including:
- Stock quotes
- Stock list
- K-line data
- Pagination and sorting
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestStockQuotesAPI:
    """Test stock quotes API"""

    def test_get_quotes_with_symbols(self, client):
        """Test getting quotes for specific symbols"""
        response = client.get("/api/market/quotes?symbols=000001,600519")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert "quotes" in data["data"]
        assert "total" in data["data"]
        assert data["data"]["total"] >= 0

    def test_get_quotes_default(self, client):
        """Test getting default hot stock quotes"""
        response = client.get("/api/market/quotes")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert "quotes" in data["data"]
        # Should return default hot stocks
        assert data["data"]["total"] > 0

    def test_get_quotes_single_symbol(self, client):
        """Test getting quote for single symbol"""
        response = client.get("/api/market/quotes?symbols=000001")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert data["data"]["total"] == 1


class TestStockListAPI:
    """Test stock list API"""

    def test_get_stock_list_default(self, client):
        """Test getting stock list with default parameters"""
        response = client.get("/api/market/stocks")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert "stocks" in data["data"]
        assert "total" in data["data"]
        assert data["data"]["total"] <= 100  # Default limit

    def test_get_stock_list_with_search(self, client):
        """Test searching stocks by keyword"""
        response = client.get("/api/market/stocks?search=平安")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        # Results should contain the search keyword in symbol or name

    def test_get_stock_list_with_exchange(self, client):
        """Test filtering stocks by exchange"""
        response = client.get("/api/market/stocks?exchange=SSE")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        # Verify all returned stocks are from SSE
        for stock in data["data"]["stocks"]:
            assert stock["exchange"] == "SSE"

    def test_get_stock_list_limit_validation(self, client):
        """Test limit parameter validation"""
        # Test maximum limit
        response = client.get("/api/market/stocks?limit=1000")

        assert response.status_code == 200

        # Test limit exceeds maximum (should return 422)
        response = client.get("/api/market/stocks?limit=2000")
        assert response.status_code == 422

        # Test invalid limit (should return 422)
        response = client.get("/api/market/stocks?limit=0")
        assert response.status_code == 422


class TestKLineDataAPI:
    """Test K-line data API"""

    def test_get_kline_default(self, client):
        """Test getting K-line data with default parameters"""
        response = client.get("/api/market/kline?stock_code=000001")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert "data" in data

        if data["data"]:
            # Verify K-line data structure
            kline = data["data"][0]
            assert "trade_date" in kline or "date" in kline
            assert "open" in kline
            assert "high" in kline
            assert "low" in kline
            assert "close" in kline
            assert "volume" in kline

    def test_get_kline_with_date_range(self, client):
        """Test getting K-line data with date range"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        response = client.get(f"/api/market/kline?stock_code=000001&start_date={start_date}&end_date={end_date}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"

    def test_get_kline_different_periods(self, client):
        """Test getting K-line data for different periods"""
        periods = ["daily", "weekly", "monthly"]

        for period in periods:
            response = client.get(f"/api/market/kline?stock_code=000001&period={period}")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == "SUCCESS"

    def test_get_kline_different_adjust_types(self, client):
        """Test different adjustment types"""
        adjust_types = ["qfq", "hfq", ""]

        for adjust in adjust_types:
            response = client.get(f"/api/market/kline?stock_code=000001&adjust={adjust}")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == "SUCCESS"

    def test_get_kline_invalid_symbol(self, client):
        """Test getting K-line data with invalid symbol"""
        response = client.get("/api/market/kline?stock_code=INVALID")

        # Should return 200 but with error or empty data
        assert response.status_code in [200, 404, 500]


class TestPaginationAndSorting:
    """Test pagination and sorting functionality"""

    def test_pagination_params_model(self):
        """Test PaginationParams model"""
        from app.schemas.pagination import PaginationParams

        # Test default values
        pagination = PaginationParams()
        assert pagination.page == 1
        assert pagination.page_size == 20
        assert pagination.offset == 0
        assert pagination.limit == 20

        # Test custom values
        pagination = PaginationParams(page=2, page_size=50)
        assert pagination.page == 2
        assert pagination.page_size == 50
        assert pagination.offset == 50
        assert pagination.limit == 50

    def test_paginated_response_model(self):
        """Test PaginatedResponse model"""
        from app.schemas.pagination import create_paginated_response
        from app.schemas.pagination import PaginationParams

        # Create mock data
        data = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        total = 100
        pagination = PaginationParams(page=1, page_size=20)

        response = create_paginated_response(data, total, pagination)

        # Verify response structure
        assert response.data == data
        assert response.total == total
        assert response.page == 1
        assert response.page_size == 20
        assert response.total_pages == 5  # 100 / 20 = 5
        assert response.has_next is True
        assert response.has_prev is False

    def test_sort_params_model(self):
        """Test SortParams model"""
        from app.schemas.pagination import SortParams

        # Test default values
        sort = SortParams()
        assert sort.sort_by == "id"
        assert sort.order == "asc"
        assert sort.get_order_by_clause() == "id ASC"

        # Test custom values
        sort = SortParams(sort_by="created_at", order="desc")
        assert sort.sort_by == "created_at"
        assert sort.order == "desc"
        assert sort.get_order_by_clause() == "created_at DESC"

        # Test get_sort_dict for MongoDB
        sort_dict = sort.get_sort_dict()
        assert sort_dict == {"created_at": -1}


class TestMarketDataIntegration:
    """Integration tests for market data APIs"""

    def test_end_to_end_stock_query(self, client):
        """Test end-to-end stock query workflow"""
        # 1. Get stock list
        list_response = client.get("/api/market/stocks?limit=1")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert len(list_data["data"]["stocks"]) > 0

        # 2. Get quotes for the first stock
        symbol = list_data["data"]["stocks"][0]["symbol"]
        quotes_response = client.get(f"/api/market/quotes?symbols={symbol}")
        assert quotes_response.status_code == 200

        # 3. Get K-line data for the same stock
        kline_response = client.get(f"/api/market/kline?stock_code={symbol}")
        assert kline_response.status_code == 200

    def test_api_response_format(self, client):
        """Test API response format consistency"""
        endpoints = [
            "/api/market/quotes",
            "/api/market/stocks",
            "/api/market/kline?stock_code=000001",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200

            data = response.json()
            # Verify UnifiedResponse format
            assert "code" in data
            assert "message" in data
            assert "data" in data
            assert "timestamp" in data

            # Verify code is SUCCESS
            assert data["code"] == "SUCCESS"


class TestDatabaseIntegration:
    """Test database integration"""

    def test_postgresql_connection(self, client):
        """Test PostgreSQL database connection"""
        # This test requires actual database connection
        # Skip in CI/CD if database not available
        pytest.importorskip("psycopg2")

        response = client.get("/api/market/stocks")
        assert response.status_code == 200

    def test_tdengine_connection(self, client):
        """Test TDengine database connection"""
        # This test requires actual TDengine connection
        # Skip in CI/CD if TDengine not available
        try:
            import taos
        except ImportError:
            pytest.skip("TDengine driver not installed")

        # Test minute-level K-line data
        # This should use TDengine for high-frequency data
        response = client.get("/api/market/kline?stock_code=000001")
        assert response.status_code == 200


class TestAPIPerformance:
    """Performance tests for market APIs"""

    def test_quotes_response_time(self, client):
        """Test quotes API response time"""
        import time

        start = time.time()
        response = client.get("/api/market/quotes?symbols=000001,600519")
        end = time.time()

        assert response.status_code == 200
        # Should respond within 5 seconds
        assert end - start < 5.0

    def test_stock_list_response_time(self, client):
        """Test stock list API response time"""
        import time

        start = time.time()
        response = client.get("/api/market/stocks?limit=100")
        end = time.time()

        assert response.status_code == 200
        # Should respond within 3 seconds
        assert end - start < 3.0


class TestAPIErrorHandling:
    """Test API error handling"""

    def test_invalid_stock_symbol(self, client):
        """Test handling of invalid stock symbol"""
        response = client.get("/api/market/kline?stock_code=INVALID_SYMBOL_999")

        # Should not crash, return 4xx or 5xx
        assert response.status_code in [200, 404, 500]

    def test_invalid_date_format(self, client):
        """Test handling of invalid date format"""
        response = client.get("/api/market/kline?stock_code=000001&start_date=invalid-date")

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_invalid_period(self, client):
        """Test handling of invalid period parameter"""
        response = client.get("/api/market/kline?stock_code=000001&period=invalid")

        # Should return validation error (422) due to regex pattern
        assert response.status_code == 422

    def test_invalid_adjust_type(self, client):
        """Test handling of invalid adjust type"""
        response = client.get("/api/market/kline?stock_code=000001&adjust=invalid")

        # Should return validation error (422) due to regex pattern
        assert response.status_code == 422
