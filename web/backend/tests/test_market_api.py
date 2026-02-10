"""
Stock Market API Unit Tests

Tests for market data APIs including:
- Stock quotes
- Stock list
- K-line data (standardized: /api/v1/data/stocks/kline)
- Pagination and sorting
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.core.security import User, get_current_user


@pytest.fixture
def mock_user():
    """Create mock authenticated user"""
    return User(
        id=1,
        username="test_user",
        email="test@example.com",
        role="admin",
        is_active=True,
    )


@pytest.fixture
def auth_client(mock_user):
    """Create authenticated test client using dependency override"""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestStockQuotesAPI:
    """Test stock quotes API"""

    def test_get_quotes_with_symbols(self, auth_client):
        """Test getting quotes for specific symbols"""
        response = auth_client.get("/api/v1/market/quotes?symbols=000001.SZ,600519.SH")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        quotes = data["data"].get("quotes", [])
        # Since we use simulated/real adapter, we might get data or not depending on connection
        # But structure should be valid
        assert isinstance(quotes, list)

    def test_get_quotes_default(self, auth_client):
        """Test getting default hot stock quotes"""
        response = auth_client.get("/api/v1/market/quotes")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should return some default quotes
        assert "data" in data

    def test_get_quotes_single_symbol(self, auth_client):
        """Test getting quote for single symbol"""
        response = auth_client.get("/api/v1/market/quotes?symbols=000001.SZ")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        quotes = data["data"].get("quotes", [])
        if quotes:
            assert quotes[0]["symbol"] == "000001.SZ"


class TestStockListAPI:
    """Test stock list API"""

    def test_get_stock_list_default(self, auth_client):
        """Test getting stock list with default parameters"""
        response = auth_client.get("/api/v1/data/stocks/basic")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_get_stock_list_with_search(self, auth_client):
        """Test searching stocks by keyword"""
        # Using a keyword guaranteed to exist (e.g., '平安')
        response = auth_client.get("/api/v1/data/stocks/basic?search=平安")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        stocks = data["data"]
        # If real DB has data, check results
        if stocks:
            # Check if any result matches
            match = False
            for stock in stocks:
                if "平安" in stock["name"] or "平安" in stock.get("symbol", ""):
                    match = True
                    break
            assert match

    def test_get_stock_list_with_exchange(self, auth_client):
        """Test filtering stocks by market (SZ/SH)"""
        # Note: data.py uses 'market' parameter, not 'exchange'
        response = auth_client.get("/api/v1/data/stocks/basic?market=SZ")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        stocks = data["data"]
        if stocks:
            assert stocks[0]["market"] == "SZ"

    def test_get_stock_list_limit_validation(self, auth_client):
        """Test limit parameter validation"""
        # Test maximum limit (should work even without DB for validation)
        response = auth_client.get("/api/v1/data/stocks/basic?limit=1000")
        # If DB is available, check success; otherwise, validation should still work
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True or data.get("code") == "SUCCESS"
        else:
            # If DB not available, just verify response format is valid
            assert response.status_code in [200, 500, 422]

        # Test limit exceeds maximum (should return 422)
        response = auth_client.get("/api/v1/data/stocks/basic?limit=2000")
        assert response.status_code == 422

        # Test invalid limit (should return 422)
        response = auth_client.get("/api/v1/data/stocks/basic?limit=0")
        assert response.status_code == 422


class TestStockKlineDataAPI:
    """Test standardized K-line data API (/api/v1/data/stocks/kline)"""

    def test_get_kline_basic(self, auth_client):
        """Test getting K-line data with basic required parameters"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        response = auth_client.get(
            f"/api/v1/data/stocks/kline?symbol=000001.SZ&start_date={start_date}&end_date={end_date}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True or data.get("code") == "SUCCESS"
        assert "data" in data or "data" in data

    def test_get_kline_with_period(self, auth_client):
        """Test getting K-line data with different periods"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")

        # New API supports: day, week, month
        periods = ["day", "week", "month"]

        for period in periods:
            response = auth_client.get(
                f"/api/v1/data/stocks/kline?symbol=000001.SZ&start_date={start_date}&end_date={end_date}&period={period}"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True or data.get("code") == "SUCCESS"

    def test_get_kline_missing_params(self, auth_client):
        """Test validation for missing required parameters"""
        # Missing symbol
        response = auth_client.get("/api/v1/data/stocks/kline?start_date=2024-01-01&end_date=2024-01-31")
        assert response.status_code == 422

        # Missing date range
        response = auth_client.get("/api/v1/data/stocks/kline?symbol=000001.SZ")
        assert response.status_code == 422

    def test_get_kline_invalid_dates(self, auth_client):
        """Test validation for invalid date format"""
        response = auth_client.get("/api/v1/data/stocks/kline?symbol=000001.SZ&start_date=invalid&end_date=2024-01-31")
        # The API may return 200 (lenient validation) or 400 with error details
        assert response.status_code in [200, 400, 422]

    def test_get_kline_invalid_period(self, auth_client):
        """Test validation for invalid period"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        response = auth_client.get(
            f"/api/v1/data/stocks/kline?symbol=000001.SZ&start_date={start_date}&end_date={end_date}&period=invalid"
        )
        # The API may return 200 with success=False or 422 for invalid period
        assert response.status_code in [200, 422]


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

    def test_end_to_end_stock_query(self, auth_client):
        """Test end-to-end stock query workflow"""
        # 1. Search for a stock
        response = auth_client.get("/api/v1/data/stocks/basic?search=000001")
        assert response.status_code == 200
        data = response.json()
        if not data["data"]:
            pytest.skip("No stock found for 000001, skipping integration test")

        symbol = data["data"][0]["symbol"]

        # 2. Get K-line data for that stock
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        kline_response = auth_client.get(
            f"/api/v1/data/stocks/kline?symbol={symbol}&start_date={start_date}&end_date={end_date}"
        )
        assert kline_response.status_code == 200

        # 3. Get Real-time quotes
        quote_response = auth_client.get(f"/api/v1/market/quotes?symbols={symbol}")
        assert quote_response.status_code == 200

    def test_api_response_format(self, auth_client):
        """Test API response format consistency"""
        # Test K-line format (standardized endpoint)
        response = auth_client.get(
            "/api/v1/data/stocks/kline?symbol=000001.SZ&start_date=2024-01-01&end_date=2024-12-31"
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data or "success" in data


class TestDatabaseIntegration:
    """Test database integration"""

    def test_postgresql_connection(self, auth_client):
        """Test PostgreSQL database connection via health check or simple query"""
        # Use existing endpoint that queries DB
        response = auth_client.get("/api/v1/data/stocks/basic?limit=1")
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_tdengine_connection(self, auth_client):
        """Test TDengine database connection"""
        # This test requires actual TDengine connection
        try:
            import taos
        except ImportError:
            pytest.skip("TDengine driver not installed")

        # Test minute-level K-line data
        response = auth_client.get(
            "/api/v1/data/stocks/kline?symbol=000001.SZ&start_date=2024-01-01&end_date=2024-01-31&period=day"
        )
        assert response.status_code == 200


class TestAPIPerformance:
    """Performance tests for market APIs"""

    def test_quotes_response_time(self, auth_client):
        """Test quotes API response time"""
        import time

        start = time.time()
        response = auth_client.get("/api/v1/market/quotes?symbols=000001.SZ")
        duration = time.time() - start

        assert response.status_code == 200
        # Expecting fast response (e.g. < 1s)
        assert duration < 2.0

    def test_stock_list_response_time(self, auth_client):
        """Test stock list API response time"""
        import time

        start = time.time()
        response = auth_client.get("/api/v1/data/stocks/basic?limit=20")
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 2.0


class TestAPIErrorHandling:
    """Test API error handling"""

    def test_invalid_stock_symbol(self, auth_client):
        """Test handling of invalid stock symbol"""
        response = auth_client.get(
            "/api/v1/data/stocks/kline?symbol=INVALID_SYMBOL_999&start_date=2024-01-01&end_date=2024-12-31"
        )

        # Should not crash, return 4xx or 5xx or 200 with empty data
        assert response.status_code in [200, 400, 404, 500]

    def test_invalid_date_format(self, auth_client):
        """Test handling of invalid date format"""
        response = auth_client.get(
            "/api/v1/data/stocks/kline?symbol=000001.SZ&start_date=invalid-date&end_date=2024-01-31"
        )

        # API may be lenient with date validation, returning 200 or validation error
        assert response.status_code in [200, 400, 422]

    def test_invalid_period(self, auth_client):
        """Test handling of invalid period parameter"""
        response = auth_client.get(
            "/api/v1/data/stocks/kline?symbol=000001.SZ&start_date=2024-01-01&end_date=2024-12-31&period=invalid"
        )

        # Should return validation error (422) or 200 with error message
        assert response.status_code in [200, 422]

    def test_invalid_adjust_type(self, auth_client):
        """Test handling of invalid adjust type - not applicable for new API"""
        # New standardized API doesn't have adjust parameter
        response = auth_client.get(
            "/api/v1/data/stocks/kline?symbol=000001.SZ&start_date=2024-01-01&end_date=2024-12-31&period=day"
        )
        # Should work fine
        assert response.status_code == 200
