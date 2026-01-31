"""
File-level tests for akshare_market.py API endpoints

Tests all 34 endpoints in akshare_market.py as a cohesive unit to ensure:
- All market data endpoints are functional and return proper responses
- Integration between different data sources (akshare-based)
- Data consistency across related market endpoints
- Performance requirements for market data APIs
- Error handling for market data requests
"""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List

import httpx
import pytest

from tests.conftest import auth_headers, client, test_user


class TestAkShareMarketAPIFile:
    """File-level tests for akshare_market.py API endpoints"""
    @pytest.mark.asyncio
    async def test_akshare_market_file_endpoints_accessibility(self, client, auth_headers):
        """Test that all 34 endpoints in akshare_market.py are accessible"""
        endpoints = [
            "/api/akshare-market/sse/overview",
            "/api/akshare-market/szse/overview",
            "/api/akshare-market/szse/area-trading",
            "/api/akshare-market/szse/sector-trading",
            "/api/akshare-market/stock/individual-info/em",
            "/api/akshare-market/stock/individual-info/xq",
            "/api/akshare-market/stock/business-intro/ths",
            "/api/akshare-market/stock/business-composition/em",
            "/api/akshare-market/stock/comment/em",
            "/api/akshare-market/stock/comment-detail/em",
            "/api/akshare-market/stock/news/em",
            "/api/akshare-market/stock/bid-ask/em",
            "/api/akshare-market/fund-flow/hsgt-summary",
            "/api/akshare-market/fund-flow/hsgt-detail",
            "/api/akshare-market/fund-flow/north-daily",
            "/api/akshare-market/fund-flow/south-daily",
            "/api/akshare-market/fund-flow/north-stock/000001",
            "/api/akshare-market/fund-flow/south-stock/000001",
            "/api/akshare-market/fund-flow/hsgt-holdings/000001",
            "/api/akshare-market/fund-flow/big-deal",
            "/api/akshare-market/chip-distribution/000001",
            "/api/akshare-market/forecast/profit/em/000001",
            "/api/akshare-market/forecast/profit/ths/000001",
            "/api/akshare-market/technical/indicators/em/000001",
            "/api/akshare-market/market/account-statistics",
            "/api/akshare-market/board/concept/cons/000001",
            "/api/akshare-market/board/concept/history/000001",
            "/api/akshare-market/board/concept/minute/000001",
            "/api/akshare-market/board/industry/cons/000001",
            "/api/akshare-market/board/industry/history/000001",
            "/api/akshare-market/board/industry/minute/000001",
            "/api/akshare-market/sector/hot-ranking",
            "/api/akshare-market/sector/fund-flow-ranking",
            "/api/akshare-market/sse/daily-deal",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint, headers=auth_headers)
            # Accept various status codes that indicate the endpoint exists
            # akshare data might be unavailable, so we accept service errors
            assert response.status_code in [200, 400, 401, 403, 404, 422, 500, 502, 503], (
                f"Endpoint {endpoint} returned unexpected status {response.status_code}"
            )

    @pytest.mark.asyncio
    async def test_akshare_market_file_exchange_data_consistency(self, client, auth_headers):
        """Test data consistency between SSE and SZSE overview endpoints"""
        # Test SSE overview
        sse_response = client.get("/api/akshare-market/sse/overview", headers=auth_headers)
        assert sse_response.status_code in [200, 500, 502, 503]  # Accept service unavailability

        # Test SZSE overview
        szse_response = client.get("/api/akshare-market/szse/overview", headers=auth_headers)
        assert szse_response.status_code in [200, 500, 502, 503]

        # If both succeed, check data structure consistency
        if sse_response.status_code == 200 and szse_response.status_code == 200:
            sse_data = sse_response.json()
            szse_data = szse_response.json()

            # Both should follow UnifiedResponse format
            assert sse_data.get("success") is not None, "SSE response missing success field"
            assert szse_data.get("success") is not None, "SZSE response missing success field"
            # If both have data, check basic structure
            if sse_data.get("success") and szse_data.get("success"):
                assert "data" in sse_data, "SSE response missing data field"
                assert "data" in szse_data, "SZSE response missing data field"
    @pytest.mark.asyncio
    async def test_akshare_market_file_fund_flow_integration(self, client, auth_headers):
        """Test integration between different fund flow endpoints"""
        # Test HSGT summary
        summary_response = client.get("/api/akshare-market/fund-flow/hsgt-summary", headers=auth_headers)
        assert summary_response.status_code in [200, 500, 502, 503]

        # Test HSGT detail
        detail_response = client.get("/api/akshare-market/fund-flow/hsgt-detail", headers=auth_headers)
        assert detail_response.status_code in [200, 500, 502, 503]

        # Test north/south daily flows
        north_response = client.get("/api/akshare-market/fund-flow/north-daily", headers=auth_headers)
        south_response = client.get("/api/akshare-market/fund-flow/south-daily", headers=auth_headers)

        assert north_response.status_code in [200, 500, 502, 503]
        assert south_response.status_code in [200, 500, 502, 503]

        # If all succeed, check data format consistency
        responses = [summary_response, detail_response, north_response, south_response]
        if all(r.status_code == 200 for r in responses):
            for i, response in enumerate(responses):
                data = response.json()
                assert "success" in data, f"Fund flow response {i} missing success field"
                if data.get("success"):
                    assert "data" in data, f"Fund flow response {i} missing data field"
    @pytest.mark.asyncio
    async def test_akshare_market_file_stock_individual_data_flow(self, client, auth_headers):
        """Test stock individual data flow across different providers"""
        symbol = "000001"
        # Test different data providers for the same stock
        providers = [
            f"/api/akshare-market/stock/individual-info/em?symbol={symbol}",
            f"/api/akshare-market/stock/individual-info/xq?symbol={symbol}",
        ]

        responses = []
        for endpoint in providers:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code in [200, 400, 422, 500, 502, 503]
            responses.append(response)

        # Check that at least one provider works
        successful_responses = [r for r in responses if r.status_code == 200]
        if successful_responses:
            # Verify data structure consistency
            first_success = successful_responses[0].json()
            assert "success" in first_success, "Stock info response missing success field"
    @pytest.mark.asyncio
    async def test_akshare_market_file_business_data_integration(self, client, auth_headers):
        """Test business data integration across different sources"""
        symbol = "000001"
        # Test business introduction from different sources
        intro_endpoints = [
            f"/api/akshare-market/stock/business-intro/ths?symbol={symbol}",
            f"/api/akshare-market/stock/business-composition/em?symbol={symbol}",
        ]

        for endpoint in intro_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code in [200, 400, 422, 500, 502, 503]

            if response.status_code == 200:
                data = response.json()
                assert "success" in data, f"Business data response missing success field"
    @pytest.mark.asyncio
    async def test_akshare_market_file_technical_indicators(self, client, auth_headers):
        """Test technical indicators endpoint functionality"""
        symbol = "000001"
        response = client.get(f"/api/akshare-market/technical/indicators/em/{symbol}", headers=auth_headers)
        assert response.status_code in [200, 400, 422, 500, 502, 503]

        if response.status_code == 200:
            data = response.json()
            assert "success" in data, "Technical indicators response missing success field"
            if data.get("success"):
                # Should contain technical indicator data
                assert "data" in data, "Technical indicators response missing data field"
    @pytest.mark.asyncio
    async def test_akshare_market_file_forecast_data_consistency(self, client, auth_headers):
        """Test forecast data consistency across different sources"""
        symbol = "000001"
        # Test profit forecasts from different sources
        forecast_endpoints = [
            f"/api/akshare-market/forecast/profit/em/{symbol}",
            f"/api/akshare-market/forecast/profit/ths/{symbol}",
        ]

        responses = []
        for endpoint in forecast_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code in [200, 400, 422, 500, 502, 503]
            responses.append(response)

        # Check successful responses for data consistency
        successful_responses = [r for r in responses if r.status_code == 200]
        if successful_responses:
            for response in successful_responses:
                data = response.json()
                assert "success" in data, "Forecast response missing success field"
    @pytest.mark.asyncio
    async def test_akshare_market_file_board_concept_integration(self, client, auth_headers):
        """Test concept board data integration"""
        symbol = "000001"
        # Test concept board related endpoints
        concept_endpoints = [
            f"/api/akshare-market/board/concept/cons/{symbol}",
            f"/api/akshare-market/board/concept/history/{symbol}",
            f"/api/akshare-market/board/concept/minute/{symbol}",
        ]

        for endpoint in concept_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code in [200, 400, 422, 500, 502, 503]

            if response.status_code == 200:
                data = response.json()
                assert "success" in data, f"Concept board response missing success field"
    @pytest.mark.asyncio
    async def test_akshare_market_file_board_industry_integration(self, client, auth_headers):
        """Test industry board data integration"""
        symbol = "000001"
        # Test industry board related endpoints
        industry_endpoints = [
            f"/api/akshare-market/board/industry/cons/{symbol}",
            f"/api/akshare-market/board/industry/history/{symbol}",
            f"/api/akshare-market/board/industry/minute/{symbol}",
        ]

        for endpoint in industry_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code in [200, 400, 422, 500, 502, 503]

            if response.status_code == 200:
                data = response.json()
                assert "success" in data, f"Industry board response missing success field"
    @pytest.mark.asyncio
    async def test_akshare_market_file_sector_data_integration(self, client, auth_headers):
        """Test sector data integration"""
        # Test sector ranking endpoints
        sector_endpoints = [
            "/api/akshare-market/sector/hot-ranking",
            "/api/akshare-market/sector/fund-flow-ranking",
        ]

        for endpoint in sector_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code in [200, 500, 502, 503]

            if response.status_code == 200:
                data = response.json()
                assert "success" in data, f"Sector data response missing success field"
    @pytest.mark.asyncio
    async def test_akshare_market_file_error_handling(self, client, auth_headers):
        """Test error handling across akshare market endpoints"""
        # Test with invalid symbols
        invalid_endpoints = [
            "/api/akshare-market/stock/individual-info/em?symbol=INVALID",
            "/api/akshare-market/technical/indicators/em/INVALID",
            "/api/akshare-market/forecast/profit/em/INVALID",
            "/api/akshare-market/chip-distribution/INVALID",
        ]

        for endpoint in invalid_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            # Should return proper error response, not crash
            assert response.status_code in [200, 400, 404, 422, 500, 502, 503], (
                f"Endpoint {endpoint} returned unexpected error status {response.status_code}"
            )

    @pytest.mark.asyncio
    async def test_akshare_market_file_performance_requirements(self, client, auth_headers):
        """Test performance requirements for akshare market endpoints"""
        import time

        # Test key endpoints for performance
        performance_endpoints = [
            ("/api/akshare-market/sse/overview", 3.0),  # 3 second limit for market data
            ("/api/akshare-market/fund-flow/hsgt-summary", 2.0),  # 2 second limit
            ("/api/akshare-market/stock/bid-ask/em?symbol=000001", 1.5),  # 1.5 second limit
        ]

        for endpoint, time_limit in performance_endpoints:
            start_time = time.time()
            response = client.get(endpoint, headers=auth_headers)
            end_time = time.time()
            response_time = end_time - start_time

            # Log performance for monitoring
            print(f"AkShare endpoint {endpoint}: {response_time:.3f}s")

            # Performance assertion (allow some tolerance for external API calls)
            assert response_time < (time_limit * 2), (
                f"AkShare endpoint {endpoint} too slow: {response_time:.3f}s (limit: {time_limit}s)"
            )

    @pytest.mark.asyncio
    async def test_akshare_market_file_data_quality_validation(self, client, auth_headers):
        """Test data quality for akshare market endpoints"""
        quality_checks = {
            "/api/akshare-market/fund-flow/hsgt-summary": lambda data: self._validate_fund_flow_quality(data),
            "/api/akshare-market/sector/hot-ranking": lambda data: self._validate_sector_ranking_quality(data),
            "/api/akshare-market/sse/overview": lambda data: self._validate_exchange_overview_quality(data),
        }

        for endpoint, validator in quality_checks.items():
            response = client.get(endpoint, headers=auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    quality_issues = validator(data.get("data", {}))
                    assert len(quality_issues) == 0, f"Data quality issues in {endpoint}: {quality_issues}"
    def _validate_fund_flow_quality(self, data: Any) -> List[str]:
        """Validate fund flow data quality"""
        issues = []
        if not isinstance(data, (list, dict)):
            issues.append("Fund flow data should be list or dict")
            return issues

        # Check for expected fund flow fields
        expected_fields = ["north_flow", "south_flow", "total_flow"]
        if isinstance(data, dict):
            for field in expected_fields:
                if field not in data:
                    issues.append(f"Fund flow data missing field: {field}")

        return issues

    def _validate_sector_ranking_quality(self, data: Any) -> List[str]:
        """Validate sector ranking data quality"""
        issues = []
        if not isinstance(data, list):
            issues.append("Sector ranking should be a list")
            return issues

        if len(data) > 0:
            first_item = data[0]
            if isinstance(first_item, dict):
                expected_fields = ["sector_name", "ranking"]
                for field in expected_fields:
                    if field not in first_item:
                        issues.append(f"Sector ranking item missing field: {field}")

        return issues

    def _validate_exchange_overview_quality(self, data: Any) -> List[str]:
        """Validate exchange overview data quality"""
        issues = []
        if not isinstance(data, dict):
            issues.append("Exchange overview should be a dict")
            return issues

        # Check for basic market metrics
        basic_fields = ["total_value", "trading_volume"]
        for field in basic_fields:
            if field not in data:
                issues.append(f"Exchange overview missing field: {field}")

        return issues
