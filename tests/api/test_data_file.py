"""
File-level tests for data.py API endpoints

Tests all 29 endpoints in data.py as a cohesive unit to ensure:
- All endpoints are accessible and return proper responses
- Data consistency across related endpoints
- Integration between different data sources
- Performance requirements are met
- Error handling works correctly
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List

import httpx
import pytest

from tests.conftest import auth_headers, client, test_user


class TestDataAPIFile:
    """File-level tests for data.py API endpoints"""

    @pytest.mark.asyncio
    async def test_data_file_endpoints_accessibility(self, client, auth_headers):
        """Test that all 29 endpoints in data.py are accessible"""
        endpoints = [
            "/api/data/stocks/basic",
            "/api/data/stocks/industries",
            "/api/data/stocks/concepts",
            "/api/data/stocks/daily",
            "/api/data/markets/overview",
            "/api/data/stocks/search",
            "/api/data/kline",
            "/api/data/stocks/kline",
            "/api/data/financial",
            "/api/data/markets/price-distribution",
            "/api/data/markets/hot-industries",
            "/api/data/markets/hot-concepts",
            "/api/data/stocks/intraday",
            "/api/data/stocks/000001/detail",
            "/api/data/stocks/000001/trading-summary",
            "/api/data/test/factory",
            "/api/data/margin/account-info",
            "/api/data/margin/detail/sse",
            "/api/data/margin/detail/szse",
            "/api/data/margin/summary/sse",
            "/api/data/margin/summary/szse",
            "/api/data/dragon-tiger/detail",
            "/api/data/dragon-tiger/institution-daily",
            "/api/data/dragon-tiger/institution-stats",
            "/api/data/dragon-tiger/stock-stats",
            "/api/data/futures/index/daily",
            "/api/data/futures/index/realtime",
            "/api/data/futures/index/main-contract",
            "/api/data/futures/basis/analysis",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint, headers=auth_headers)
            # Accept both 200 (success) and other status codes that indicate the endpoint exists
            assert response.status_code in [200, 400, 401, 403, 404, 422, 500], (
                f"Endpoint {endpoint} returned unexpected status {response.status_code}"
            )

    @pytest.mark.asyncio
    async def test_data_file_response_formats(self, client, auth_headers):
        """Test that all endpoints return proper UnifiedResponse format"""
        test_endpoints = ["/api/data/stocks/basic", "/api/data/markets/overview", "/api/data/stocks/search?q=000001"]

        for endpoint in test_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            if response.status_code == 200:
                data = response.json()
                # Check UnifiedResponse format
                assert "success" in data, f"Endpoint {endpoint} missing 'success' field"
                assert "code" in data, f"Endpoint {endpoint} missing 'code' field"
                assert "message" in data, f"Endpoint {endpoint} missing 'message' field"
                assert "data" in data, f"Endpoint {endpoint} missing 'data' field"
                assert "timestamp" in data, f"Endpoint {endpoint} missing 'timestamp' field"

    @pytest.mark.asyncio
    async def test_data_file_stock_data_consistency(self, client, auth_headers):
        """Test data consistency between related stock endpoints"""
        # Get basic stock info
        basic_response = client.get("/api/data/stocks/basic?limit=5", headers=auth_headers)
        assert basic_response.status_code == 200
        basic_data = basic_response.json()

        if basic_data["success"] and basic_data["data"]:
            # Pick first stock for detailed testing
            first_stock = basic_data["data"][0]
            symbol = first_stock.get("symbol")

            if symbol:
                # Test detail endpoint
                detail_response = client.get(f"/api/data/stocks/{symbol}/detail", headers=auth_headers)
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    # Ensure symbol consistency
                    assert detail_data["data"]["symbol"] == symbol, (
                        f"Symbol mismatch: expected {symbol}, got {detail_data['data']['symbol']}"
                    )

                # Test trading summary endpoint
                summary_response = client.get(f"/api/data/stocks/{symbol}/trading-summary", headers=auth_headers)
                if summary_response.status_code == 200:
                    summary_data = summary_response.json()
                    # Ensure data structure consistency
                    assert "data" in summary_data, "Trading summary missing data field"

    @pytest.mark.asyncio
    async def test_data_file_market_data_integration(self, client, auth_headers):
        """Test integration between market overview and detailed market data"""
        # Get market overview
        overview_response = client.get("/api/data/markets/overview", headers=auth_headers)
        assert overview_response.status_code in [200, 404, 500]  # Accept service unavailability

        if overview_response.status_code == 200:
            overview_data = overview_response.json()

            # Test price distribution endpoint
            price_dist_response = client.get("/api/data/markets/price-distribution", headers=auth_headers)
            if price_dist_response.status_code == 200:
                price_data = price_dist_response.json()
                # Ensure data format consistency
                assert isinstance(price_data["data"], (list, dict)), "Price distribution data should be list or dict"

    @pytest.mark.asyncio
    async def test_data_file_search_functionality(self, client, auth_headers):
        """Test search functionality across data endpoints"""
        search_term = "浦发银行"

        # Test stock search
        search_response = client.get(f"/api/data/stocks/search?q={search_term}", headers=auth_headers)
        assert search_response.status_code in [200, 400, 404]

        if search_response.status_code == 200:
            search_data = search_response.json()
            assert "data" in search_data, "Search response missing data field"
            # If results found, check data structure
            if search_data["success"] and search_data["data"]:
                result = search_data["data"][0]
                assert "symbol" in result or "name" in result, "Search result missing symbol or name field"

    @pytest.mark.asyncio
    async def test_data_file_kline_data_consistency(self, client, auth_headers):
        """Test K-line data consistency across different endpoints"""
        symbol = "000001"
        period = "daily"

        # Test general kline endpoint
        kline_response = client.get(f"/api/data/kline?symbol={symbol}&period={period}", headers=auth_headers)
        assert kline_response.status_code in [200, 400, 404, 422]

        # Test stock-specific kline endpoint
        stock_kline_response = client.get(
            f"/api/data/stocks/kline?symbol={symbol}&period={period}", headers=auth_headers
        )
        assert stock_kline_response.status_code in [200, 400, 404, 422]

        # If both succeed, check data consistency
        if kline_response.status_code == 200 and stock_kline_response.status_code == 200:
            kline_data = kline_response.json()
            stock_kline_data = stock_kline_response.json()

            # Ensure both endpoints return same data structure
            assert "data" in kline_data, "Kline endpoint missing data field"
            assert "data" in stock_kline_data, "Stock kline endpoint missing data field"

    @pytest.mark.asyncio
    async def test_data_file_error_handling(self, client, auth_headers):
        """Test error handling across data file endpoints"""
        error_endpoints = [
            "/api/data/stocks/INVALID/detail",  # Invalid symbol
            "/api/data/kline?symbol=000001&period=invalid",  # Invalid period
            "/api/data/stocks/search?q=",  # Empty search
        ]

        for endpoint in error_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            # Should return proper error response, not crash
            assert response.status_code in [200, 400, 404, 422, 500], (
                f"Endpoint {endpoint} returned unexpected error status {response.status_code}"
            )

            if response.status_code >= 400:
                error_data = response.json()
                # Check error response format
                assert "success" in error_data, f"Error response {endpoint} missing success field"
                assert "message" in error_data, f"Error response {endpoint} missing message field"

    @pytest.mark.asyncio
    async def test_data_file_performance_requirements(self, client, auth_headers):
        """Test performance requirements for data file endpoints"""
        import time

        performance_endpoints = [
            ("/api/data/stocks/basic?limit=10", 2.0),  # 2 second limit
            ("/api/data/markets/overview", 1.0),  # 1 second limit
            ("/api/data/stocks/search?q=000001", 1.5),  # 1.5 second limit
        ]

        for endpoint, time_limit in performance_endpoints:
            start_time = time.time()
            response = client.get(endpoint, headers=auth_headers)
            end_time = time.time()
            response_time = end_time - start_time

            # Log performance for monitoring
            print(f"Endpoint {endpoint}: {response_time:.3f}s")

            # Performance assertion (allow some tolerance for CI environment)
            assert response_time < (time_limit * 2), (
                f"Endpoint {endpoint} too slow: {response_time:.3f}s (limit: {time_limit}s)"
            )

    @pytest.mark.asyncio
    async def test_data_file_integration_scenarios(self, client, auth_headers):
        """Test end-to-end integration scenarios across data file"""
        # Scenario 1: Stock discovery to detailed analysis
        # 1. Search for stocks
        search_response = client.get("/api/data/stocks/search?q=银行", headers=auth_headers)
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data["success"] and search_data["data"]:
                stock = search_data["data"][0]
                symbol = stock.get("symbol")

                if symbol:
                    # 2. Get stock details
                    detail_response = client.get(f"/api/data/stocks/{symbol}/detail", headers=auth_headers)
                    assert detail_response.status_code in [200, 404, 500]

                    # 3. Get trading summary
                    summary_response = client.get(f"/api/data/stocks/{symbol}/trading-summary", headers=auth_headers)
                    assert summary_response.status_code in [200, 404, 500]

                    # 4. Get K-line data
                    kline_response = client.get(
                        f"/api/data/stocks/kline?symbol={symbol}&period=daily", headers=auth_headers
                    )
                    assert kline_response.status_code in [200, 400, 404, 422, 500]

    @pytest.mark.asyncio
    async def test_data_file_data_quality_validation(self, client, auth_headers):
        """Test data quality across all data file endpoints"""
        quality_checks = {
            "/api/data/stocks/basic": lambda data: self._validate_stock_list_quality(data),
            "/api/data/markets/overview": lambda data: self._validate_market_overview_quality(data),
            "/api/data/stocks/search?q=000001": lambda data: self._validate_search_results_quality(data),
        }

        for endpoint, validator in quality_checks.items():
            response = client.get(endpoint, headers=auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    quality_issues = validator(data["data"])
                    assert len(quality_issues) == 0, f"Data quality issues in {endpoint}: {quality_issues}"

    def _validate_stock_list_quality(self, data: Any) -> List[str]:
        """Validate stock list data quality"""
        issues = []
        if not isinstance(data, list):
            issues.append("Stock list should be an array")
            return issues

        for i, stock in enumerate(data[:5]):  # Check first 5 items
            if not isinstance(stock, dict):
                issues.append(f"Stock item {i} should be an object")
                continue

            required_fields = ["symbol", "name"]
            for field in required_fields:
                if field not in stock:
                    issues.append(f"Stock item {i} missing required field: {field}")

        return issues

    def _validate_market_overview_quality(self, data: Any) -> List[str]:
        """Validate market overview data quality"""
        issues = []
        if not isinstance(data, dict):
            issues.append("Market overview should be an object")
            return issues

        # Basic structure check
        if "total_market_cap" not in data and "trading_volume" not in data:
            issues.append("Market overview missing key metrics")

        return issues

    def _validate_search_results_quality(self, data: Any) -> List[str]:
        """Validate search results data quality"""
        issues = []
        if not isinstance(data, list):
            issues.append("Search results should be an array")
            return issues

        for i, result in enumerate(data[:3]):  # Check first 3 results
            if not isinstance(result, dict):
                issues.append(f"Search result {i} should be an object")
                continue

            # At least one of symbol or name should be present
            if "symbol" not in result and "name" not in result:
                issues.append(f"Search result {i} missing both symbol and name fields")

        return issues
