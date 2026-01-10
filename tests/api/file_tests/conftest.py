# API File-Level Testing Fixtures

# Common test data for API file testing
import pytest
from pathlib import Path
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
    return {
        "market-data": {
            "openapi": "3.0.3",
            "info": {"title": "Market Data API", "version": "1.0.0"},
            "paths": {
                "/api/market/overview": {"get": {"responses": {"200": {"description": "Success"}}}},
                "/api/market/fund-flow": {"get": {"responses": {"200": {"description": "Success"}}}},
            },
        },
        "strategy-management": {
            "openapi": "3.0.3",
            "info": {"title": "Strategy Management API", "version": "1.0.0"},
            "paths": {
                "/api/strategies": {"get": {"responses": {"200": {"description": "Success"}}}},
                "/api/strategies/{id}": {"get": {"responses": {"200": {"description": "Success"}}}},
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
    from tests.api.file_tests import FileTestResult, TestStatus, TestPriority

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
