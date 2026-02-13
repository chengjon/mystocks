# API File-Level Testing Fixtures

# Common test data for API file testing
from pathlib import Path

import pytest

from tests.api.file_tests import FileTestRunner, TestDataManager


@pytest.fixture(scope="session")
def test_runner():
    """Global file test runner instance"""
    return FileTestRunner(max_workers=4)  # Reduced for testing


@pytest.fixture(scope="session")
def data_manager():
    """Test data manager instance"""
    return TestDataManager(Path(__file__).parent)


@pytest.fixture
def api_test_fixtures():
    """Common API test fixtures"""
    return {
        "base_url": "http://localhost:8000",
        "test_timeout": 30,
        "retry_attempts": 3,
        "mock_enabled": True,
        "contract_validation": True,
    }


@pytest.fixture
def mock_responses():
    """Mock API responses for testing"""
    return {
        "market_overview": {
            "success": True,
            "data": {"total_stocks": 5000, "up_count": 2800, "down_count": 2100, "flat_count": 100},
        },
        "strategy_list": {
            "success": True,
            "data": {"strategies": [{"id": "strat_1", "name": "Test Strategy", "status": "active"}]},
        },
        "error_response": {"success": False, "code": 500, "message": "Internal server error", "data": None},
    }


@pytest.fixture
def contract_specs():
    """OpenAPI contract specifications for testing"""
    _ok = {"get": {"responses": {"200": {"description": "Success"}}}}
    _post = {"post": {"responses": {"200": {"description": "Success"}}}}
    _put = {"put": {"responses": {"200": {"description": "Success"}}}}
    _del = {"delete": {"responses": {"200": {"description": "Success"}}}}

    return {
        "market-data": {
            "openapi": "3.0.3",
            "info": {"title": "Market Data API", "version": "1.0.0"},
            "paths": {
                "/api/market/overview": _ok,
                "/api/market/fund-flow": _ok,
                "/api/market/kline": _ok,
                "/api/market/realtime": _ok,
                "/api/market/stock-list": _ok,
                "/api/market/search": _ok,
            },
        },
        "strategy-management": {
            "openapi": "3.0.3",
            "info": {"title": "Strategy Management API", "version": "1.0.0"},
            "paths": {
                "/api/strategies": _ok,
                "/api/strategies/{id}": _ok,
                "/api/strategies/create": _post,
                "/api/strategies/{id}/update": _put,
                "/api/strategies/{id}/delete": _del,
                "/api/strategies/{id}/backtest": _post,
                "/api/strategies/{id}/activate": _put,
                "/api/strategies/{id}/deactivate": _put,
                "/api/strategies/{id}/clone": _post,
                "/api/models/train": _post,
                "/api/models/{id}": _ok,
            },
        },
        "risk-management": {
            "openapi": "3.0.3",
            "info": {"title": "Risk Management API", "version": "1.0.0"},
            "paths": {
                "/var-cvar": _ok,
                "/beta": _ok,
                "/dashboard": _ok,
                "/alerts": _ok,
                "/alerts/{id}": _ok,
                "/alerts/{id}/acknowledge": _put,
                "/portfolio-risk": _ok,
                "/portfolio-risk/summary": _ok,
                "/portfolio-risk/history": _ok,
                "/stress-test": _post,
                "/stress-test/scenarios": _ok,
                "/risk-limits": _ok,
                "/risk-limits/update": _put,
                "/risk-metrics": _ok,
                "/risk-metrics/realtime": _ok,
                "/risk-report": _ok,
                "/risk-report/generate": _post,
                "/stop-loss/rules": _ok,
                "/stop-loss/rules/create": _post,
                "/stop-loss/rules/{id}": _ok,
                "/stop-loss/rules/{id}/update": _put,
                "/stop-loss/rules/{id}/delete": _del,
                "/stop-loss/triggers": _ok,
                "/position-sizing": _ok,
                "/position-sizing/calculate": _post,
                "/drawdown": _ok,
                "/drawdown/max": _ok,
                "/sharpe-ratio": _ok,
                "/sortino-ratio": _ok,
                "/volatility": _ok,
                "/correlation": _ok,
                "/exposure": _ok,
                "/exposure/sector": _ok,
                "/margin": _ok,
                "/margin/requirements": _ok,
                "/risk-settings": _ok,
                "/risk-settings/update": _put,
            },
        },
        "trading": {
            "openapi": "3.0.3",
            "info": {"title": "Trading API", "version": "1.0.0"},
            "paths": {
                "/api/trade/orders": _ok,
                "/api/trade/orders/create": _post,
                "/api/trade/orders/{id}": _ok,
                "/api/trade/orders/{id}/cancel": _put,
                "/api/trade/positions": _ok,
                "/api/trade/portfolio": _ok,
                "/api/trade/history": _ok,
                "/api/trade/balance": _ok,
                "/api/trade/trades": _ok,
                "/api/trade/trades/{id}": _ok,
            },
        },
    }


# Test utilities
def assert_file_test_result(result, expected_status="passed", min_success_rate=80.0):
    """Assert file test result meets expectations"""
    assert result.status.value == expected_status
    assert result.success_rate >= min_success_rate
    assert result.coverage_rate >= 70.0  # Minimum coverage requirement
    assert len(result.errors) == 0


def create_mock_file_result(file_path, endpoint_count=10, passed_ratio=0.9):
    """Create mock file test result for testing"""
    from tests.api.file_tests import FileTestResult, TestPriority, TestStatus

    passed = int(endpoint_count * passed_ratio)
    failed = endpoint_count - passed

    return FileTestResult(
        file_path=file_path,
        file_name=Path(file_path).name,
        priority=TestPriority.P1_CORE,
        endpoint_count=endpoint_count,
        status=TestStatus.PASSED if passed > failed else TestStatus.FAILED,
        duration=1.5,
        passed_endpoints=passed,
        failed_endpoints=failed,
        skipped_endpoints=0,
    )
