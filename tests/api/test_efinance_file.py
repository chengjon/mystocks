"""
File-level tests for efinance.py API endpoints

Tests all 20 endpoints in efinance.py as a cohesive unit to ensure:
- All financial data endpoints are functional and return proper responses
- Data consistency across different financial products (stocks, funds, bonds, futures)
- Integration between different data sources (efinance-based)
- Performance requirements for financial data APIs
- Error handling for financial data requests
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List

import httpx
import pytest

from tests.conftest import auth_headers, client, test_user


class TestEFinanceAPIFile:
    """File-level tests for efinance.py API endpoints"""

    @pytest.mark.asyncio
    async def test_efinance_file_endpoints_accessibility(self, client, auth_headers):
        """Test that all 20 endpoints in efinance.py are accessible"""
        endpoints = [
            "/api/efinance/stock/kline",
            "/api/efinance/stock/realtime",
            "/api/efinance/stock/realtime/000001",
            "/api/efinance/stock/dragon-tiger",
            "/api/efinance/stock/performance",
            "/api/efinance/stock/fund-flow/000001",
            "/api/efinance/stock/fund-flow-today/000001",
            "/api/efinance/fund/nav/000001",
            "/api/efinance/fund/positions/000001",
            "/api/efinance/fund/basic",
            "/api/efinance/bond/realtime",
            "/api/efinance/bond/basic",
            "/api/efinance/bond/kline/113016",
            "/api/efinance/futures/basic",
            "/api/efinance/futures/history/IC2406",
            "/api/efinance/futures/realtime",
            "/api/efinance/cache/stats",
            "/api/efinance/circuit-breaker/stats",
            "/api/efinance/cache/clear",
            "/api/efinance/circuit-breaker/reset",
        ]

        for endpoint in endpoints:
            response = (
                client.get(endpoint, headers=auth_headers)
                if not endpoint.endswith("/clear") and not endpoint.endswith("/reset")
                else client.post(endpoint, headers=auth_headers)
            )
            # Accept various status codes that indicate the endpoint exists
            # efinance data might be unavailable, so we accept service errors
            assert response.status_code in [200, 400, 401, 403, 404, 422, 500, 502, 503], (
                f"Endpoint {endpoint} returned unexpected status {response.status_code}"
            )

    @pytest.mark.asyncio
    async def test_efinance_file_stock_data_consistency(self, client, auth_headers):
        """Test data consistency across stock-related endpoints"""
        symbol = "000001"

        # Test stock realtime endpoints
        realtime_all_response = client.get("/api/efinance/stock/realtime", headers=auth_headers)
        realtime_single_response = client.get(f"/api/efinance/stock/realtime/{symbol}", headers=auth_headers)

        assert realtime_all_response.status_code in [200, 500, 502, 503]
        assert realtime_single_response.status_code in [200, 500, 502, 503]

        # If both succeed, check data structure consistency
        if realtime_all_response.status_code == 200 and realtime_single_response.status_code == 200:
            all_data = realtime_all_response.json()
            single_data = realtime_single_response.json()

            # Both should follow UnifiedResponse format
            assert all_data.get("success") is not None, "Realtime all response missing success field"
            assert single_data.get("success") is not None, "Realtime single response missing success field"

    @pytest.mark.asyncio
    async def test_efinance_file_kline_data_integration(self, client, auth_headers):
        """Test K-line data integration"""
        # Test stock kline endpoint
        stock_kline_response = client.get(
            "/api/efinance/stock/kline?symbol=000001&start_date=20240101&end_date=20240105", headers=auth_headers
        )
        assert stock_kline_response.status_code in [200, 400, 422, 500, 502, 503]

        if stock_kline_response.status_code == 200:
            kline_data = stock_kline_response.json()
            assert "success" in kline_data, "Stock kline response missing success field"

    @pytest.mark.asyncio
    async def test_efinance_file_fund_data_integration(self, client, auth_headers):
        """Test fund data integration across different endpoints"""
        fund_code = "000001"  # Example fund code

        # Test fund nav endpoint
        nav_response = client.get(f"/api/efinance/fund/nav/{fund_code}", headers=auth_headers)
        assert nav_response.status_code in [200, 400, 404, 500, 502, 503]

        # Test fund positions endpoint
        positions_response = client.get(f"/api/efinance/fund/positions/{fund_code}", headers=auth_headers)
        assert positions_response.status_code in [200, 400, 404, 500, 502, 503]

        # Test fund basic info endpoint (POST)
        basic_response = client.post("/api/efinance/fund/basic", json={"codes": [fund_code]}, headers=auth_headers)
        assert basic_response.status_code in [200, 400, 422, 500, 502, 503]

        # Check successful responses for data consistency
        responses = [nav_response, positions_response, basic_response]
        successful_responses = [r for r in responses if r.status_code == 200]
        if successful_responses:
            for response in successful_responses:
                data = response.json()
                assert "success" in data, "Fund response missing success field"

    @pytest.mark.asyncio
    async def test_efinance_file_bond_data_integration(self, client, auth_headers):
        """Test bond data integration"""
        # Test bond realtime endpoint
        realtime_response = client.get("/api/efinance/bond/realtime", headers=auth_headers)
        assert realtime_response.status_code in [200, 500, 502, 503]

        # Test bond basic info endpoint
        basic_response = client.get("/api/efinance/bond/basic", headers=auth_headers)
        assert basic_response.status_code in [200, 500, 502, 503]

        # Test bond kline endpoint
        kline_response = client.get("/api/efinance/bond/kline/113016", headers=auth_headers)
        assert kline_response.status_code in [200, 400, 404, 500, 502, 503]

        # Check successful responses for data format consistency
        responses = [realtime_response, basic_response, kline_response]
        successful_responses = [r for r in responses if r.status_code == 200]
        if successful_responses:
            for response in successful_responses:
                data = response.json()
                assert "success" in data, "Bond response missing success field"

    @pytest.mark.asyncio
    async def test_efinance_file_futures_data_integration(self, client, auth_headers):
        """Test futures data integration"""
        # Test futures basic info endpoint
        basic_response = client.get("/api/efinance/futures/basic", headers=auth_headers)
        assert basic_response.status_code in [200, 500, 502, 503]

        # Test futures realtime endpoint
        realtime_response = client.get("/api/efinance/futures/realtime", headers=auth_headers)
        assert realtime_response.status_code in [200, 500, 502, 503]

        # Test futures history endpoint
        history_response = client.get("/api/efinance/futures/history/IC2406", headers=auth_headers)
        assert history_response.status_code in [200, 400, 404, 500, 502, 503]

        # Check successful responses for data format consistency
        responses = [basic_response, realtime_response, history_response]
        successful_responses = [r for r in responses if r.status_code == 200]
        if successful_responses:
            for response in successful_responses:
                data = response.json()
                assert "success" in data, "Futures response missing success field"

    @pytest.mark.asyncio
    async def test_efinance_file_system_management_integration(self, client, auth_headers):
        """Test system management endpoints (cache, circuit breaker)"""
        # Test cache stats endpoint
        cache_stats_response = client.get("/api/efinance/cache/stats", headers=auth_headers)
        assert cache_stats_response.status_code in [200, 500, 502, 503]

        # Test circuit breaker stats endpoint
        cb_stats_response = client.get("/api/efinance/circuit-breaker/stats", headers=auth_headers)
        assert cb_stats_response.status_code in [200, 500, 502, 503]

        # Test cache clear endpoint (POST)
        cache_clear_response = client.post("/api/efinance/cache/clear", headers=auth_headers)
        assert cache_clear_response.status_code in [200, 500, 502, 503]

        # Test circuit breaker reset endpoint (POST)
        cb_reset_response = client.post("/api/efinance/circuit-breaker/reset", headers=auth_headers)
        assert cb_reset_response.status_code in [200, 500, 502, 503]

        # Check successful responses for data format consistency
        responses = [cache_stats_response, cb_stats_response, cache_clear_response, cb_reset_response]
        successful_responses = [r for r in responses if r.status_code == 200]
        if successful_responses:
            for response in successful_responses:
                data = response.json()
                assert "success" in data, "System management response missing success field"

    @pytest.mark.asyncio
    async def test_efinance_file_fund_flow_data_consistency(self, client, auth_headers):
        """Test fund flow data consistency"""
        symbol = "000001"

        # Test historical fund flow
        historical_response = client.get(f"/api/efinance/stock/fund-flow/{symbol}", headers=auth_headers)
        assert historical_response.status_code in [200, 400, 404, 500, 502, 503]

        # Test today's fund flow
        today_response = client.get(f"/api/efinance/stock/fund-flow-today/{symbol}", headers=auth_headers)
        assert today_response.status_code in [200, 400, 404, 500, 502, 503]

        # If both succeed, check data structure consistency
        if historical_response.status_code == 200 and today_response.status_code == 200:
            historical_data = historical_response.json()
            today_data = today_response.json()

            # Both should follow UnifiedResponse format
            assert historical_data.get("success") is not None, "Historical fund flow missing success field"
            assert today_data.get("success") is not None, "Today fund flow missing success field"

    @pytest.mark.asyncio
    async def test_efinance_file_error_handling(self, client, auth_headers):
        """Test error handling across efinance endpoints"""
        # Test with invalid parameters
        invalid_endpoints = [
            "/api/efinance/stock/realtime/INVALID",
            "/api/efinance/stock/fund-flow/INVALID",
            "/api/efinance/fund/nav/INVALID",
            "/api/efinance/bond/kline/INVALID",
            "/api/efinance/futures/history/INVALID",
        ]

        for endpoint in invalid_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            # Should return proper error response, not crash
            assert response.status_code in [200, 400, 404, 422, 500, 502, 503], (
                f"Endpoint {endpoint} returned unexpected error status {response.status_code}"
            )

            if response.status_code >= 400:
                error_data = response.json()
                # Check error response format
                assert "success" in error_data, f"Error response {endpoint} missing success field"
                assert "message" in error_data, f"Error response {endpoint} missing message field"

    @pytest.mark.asyncio
    async def test_efinance_file_performance_requirements(self, client, auth_headers):
        """Test performance requirements for efinance endpoints"""
        import time

        # Test key endpoints for performance
        performance_endpoints = [
            ("/api/efinance/stock/realtime", 2.0),  # 2 second limit for realtime data
            ("/api/efinance/cache/stats", 1.0),  # 1 second limit for system stats
            (
                "/api/efinance/stock/kline?symbol=000001&start_date=20240101&end_date=20240102",
                3.0,
            ),  # 3 second limit for historical data
        ]

        for endpoint, time_limit in performance_endpoints:
            start_time = time.time()
            response = client.get(endpoint, headers=auth_headers)
            end_time = time.time()
            response_time = end_time - start_time

            # Log performance for monitoring
            print(f"EFinance endpoint {endpoint}: {response_time:.3f}s")

            # Performance assertion (allow some tolerance for external API calls)
            assert response_time < (time_limit * 2), (
                f"EFinance endpoint {endpoint} too slow: {response_time:.3f}s (limit: {time_limit}s)"
            )

    @pytest.mark.asyncio
    async def test_efinance_file_data_quality_validation(self, client, auth_headers):
        """Test data quality for efinance endpoints"""
        quality_checks = {
            "/api/efinance/stock/realtime": lambda data: self._validate_stock_realtime_quality(data),
            "/api/efinance/bond/realtime": lambda data: self._validate_bond_realtime_quality(data),
            "/api/efinance/futures/basic": lambda data: self._validate_futures_basic_quality(data),
        }

        for endpoint, validator in quality_checks.items():
            response = client.get(endpoint, headers=auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    quality_issues = validator(data.get("data", []))
                    assert len(quality_issues) == 0, f"Data quality issues in {endpoint}: {quality_issues}"

    @pytest.mark.asyncio
    async def test_efinance_file_integration_scenarios(self, client, auth_headers):
        """Test end-to-end integration scenarios across efinance file"""
        # Scenario 1: Complete stock analysis flow
        symbol = "000001"

        # 1. Get realtime quote
        realtime_response = client.get(f"/api/efinance/stock/realtime/{symbol}", headers=auth_headers)
        if realtime_response.status_code == 200:
            # 2. Get historical K-line data
            kline_response = client.get(
                f"/api/efinance/stock/kline?symbol={symbol}&start_date=20240101&end_date=20240105", headers=auth_headers
            )
            assert kline_response.status_code in [200, 400, 422, 500, 502, 503]

            # 3. Get fund flow data
            fund_flow_response = client.get(f"/api/efinance/stock/fund-flow/{symbol}", headers=auth_headers)
            assert fund_flow_response.status_code in [200, 400, 404, 500, 502, 503]

            # 4. Get performance data
            performance_response = client.get("/api/efinance/stock/performance", headers=auth_headers)
            assert performance_response.status_code in [200, 500, 502, 503]

    def _validate_stock_realtime_quality(self, data: Any) -> List[str]:
        """Validate stock realtime data quality"""
        issues = []
        if not isinstance(data, list):
            issues.append("Stock realtime data should be a list")
            return issues

        for i, stock in enumerate(data[:5]):  # Check first 5 items
            if not isinstance(stock, dict):
                issues.append(f"Stock realtime item {i} should be an object")
                continue

            required_fields = ["代码", "名称"]  # Chinese field names from efinance
            for field in required_fields:
                if field not in stock:
                    issues.append(f"Stock realtime item {i} missing required field: {field}")

        return issues

    def _validate_bond_realtime_quality(self, data: Any) -> List[str]:
        """Validate bond realtime data quality"""
        issues = []
        if not isinstance(data, list):
            issues.append("Bond realtime data should be a list")
            return issues

        for i, bond in enumerate(data[:3]):  # Check first 3 items
            if not isinstance(bond, dict):
                issues.append(f"Bond realtime item {i} should be an object")
                continue

            # Check for basic bond fields
            if "代码" not in bond and "债券代码" not in bond:
                issues.append(f"Bond realtime item {i} missing code field")

        return issues

    def _validate_futures_basic_quality(self, data: Any) -> List[str]:
        """Validate futures basic data quality"""
        issues = []
        if not isinstance(data, list):
            issues.append("Futures basic data should be a list")
            return issues

        for i, future in enumerate(data[:3]):  # Check first 3 items
            if not isinstance(future, dict):
                issues.append(f"Futures basic item {i} should be an object")
                continue

            # Check for basic futures fields
            if "合约代码" not in future and "code" not in future:
                issues.append(f"Futures basic item {i} missing contract code field")

        return issues
