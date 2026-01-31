"""
Test Utilities and Fixtures for File-Level API Testing

This module provides comprehensive testing utilities, fixtures, and helpers
for file-level API testing of FastAPI applications.

Features:
- Test data factories and fixtures
- API client utilities with authentication
- Database isolation and cleanup
- Test configuration management
- Parallel test execution helpers

Author: MyStocks Testing Team
Date: 2026-01-10
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import yaml
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Import project modules
from src.core import DataClassification
from src.data_access import PostgreSQLDataAccess, TDengineDataAccess


# Test Configuration Management
class TestConfig:
    """Centralized test configuration management"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "tests/file_level/config/test_config.yaml"
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load test configuration from file"""
        if not Path(self.config_file).exists():
            return self._get_default_config()

        with open(self.config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default test configuration"""
        return {
            "api": {"base_url": "http://localhost:8000", "timeout": 30, "auth_token": None},
            "database": {
                "test_database_url": "postgresql://test:test@localhost:5438/mystocks_test",
                "tdengine_url": "taos://root:taosdata@localhost:6030/mystocks_test",
            },
            "parallel": {"max_workers": 4, "worker_timeout": 60},
            "data": {"fixtures_dir": "tests/file_level/fixtures", "cleanup_after_test": True},
            "reporting": {"save_results": True, "report_format": "json", "include_timings": True},
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self) -> None:
        """Save configuration to file"""
        os.makedirs(Path(self.config_file).parent, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(self._config, f, default_flow_style=False)


# Test Data Factories
class TestDataFactory:
    """Factory for generating test data"""

    @staticmethod
    def create_market_data(
        symbol: str = "600000", price: float = 10.50, volume: int = 1000000, timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create sample market data"""
        if timestamp is None:
            timestamp = datetime.now()

        return {
            "symbol": symbol,
            "price": price,
            "volume": volume,
            "timestamp": timestamp.isoformat(),
            "change_percent": 2.5,
            "high": price * 1.05,
            "low": price * 0.95,
            "open": price * 0.98,
            "close": price,
        }

    @staticmethod
    def create_user_data(
        user_id: str = "test_user_001", username: str = "testuser", email: str = "test@example.com", role: str = "user"
    ) -> Dict[str, Any]:
        """Create sample user data"""
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "role": role,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
        }

    @staticmethod
    def create_technical_indicators(
        symbol: str = "600000", rsi: float = 65.5, macd: float = 0.25, signal: float = 0.15
    ) -> Dict[str, Any]:
        """Create sample technical indicators data"""
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "indicators": {
                "rsi": rsi,
                "macd": macd,
                "macd_signal": signal,
                "macd_histogram": macd - signal,
                "sma_20": 10.25,
                "sma_50": 10.15,
                "ema_12": 10.30,
                "ema_26": 10.20,
                "bollinger_upper": 10.60,
                "bollinger_lower": 9.90,
                "stochastic_k": 75.5,
                "stochastic_d": 72.3,
            },
        }

    @staticmethod
    def create_bulk_market_data(symbols: List[str], count_per_symbol: int = 10) -> List[Dict[str, Any]]:
        """Create bulk market data for multiple symbols"""
        data = []
        base_time = datetime.now() - timedelta(days=30)

        for symbol in symbols:
            for i in range(count_per_symbol):
                timestamp = base_time + timedelta(days=i)
                price = 10.0 + (i * 0.1) + (hash(symbol) % 100) * 0.01

                data.append(
                    TestDataFactory.create_market_data(
                        symbol=symbol, price=price, volume=100000 + (i * 10000), timestamp=timestamp
                    )
                )

        return data


# Database Fixtures
@pytest.fixture(scope="session")
def test_config():
    """Global test configuration fixture"""
    return TestConfig()


@pytest.fixture(scope="session")
async def test_db_engine(test_config):
    """Test database engine fixture"""
    # Use PostgreSQL for test data
    database_url = test_config.get("database.test_database_url")
    if not database_url:
        pytest.skip("Test database URL not configured")

    # Create async engine
    engine = create_async_engine(database_url, echo=False, future=True)

    # Create test tables
    from src.data_access.postgresql_access import PostgreSQLDataAccess

    data_access = PostgreSQLDataAccess()

    try:
        # Initialize test database
        await data_access.initialize_database(engine)
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine):
    """Database session fixture for tests"""
    async_session = sessionmaker(test_db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
def mock_tdengine():
    """Mock TDengine for testing"""
    mock = MagicMock(spec=TDengineDataAccess)
    mock.save_data = AsyncMock(return_value=True)
    mock.load_data = AsyncMock(return_value=[])
    mock.initialize_database = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_postgresql():
    """Mock PostgreSQL for testing"""
    mock = MagicMock(spec=PostgreSQLDataAccess)
    mock.save_data = AsyncMock(return_value=True)
    mock.load_data = AsyncMock(return_value=[])
    mock.initialize_database = AsyncMock(return_value=True)
    return mock


# API Client Fixtures
@pytest.fixture
async def api_client(test_config):
    """Async API client for testing"""
    base_url = test_config.get("api.base_url", "http://localhost:8000")
    timeout = test_config.get("api.timeout", 30)

    async with httpx.AsyncClient(
        base_url=base_url, timeout=timeout, headers={"Content-Type": "application/json"}
    ) as client:
        yield client


@pytest.fixture
def sync_api_client(test_config):
    """Synchronous API client for testing"""
    from fastapi.testclient import TestClient

    # Import the FastAPI app
    try:
        from web.backend.app.main import app

        client = TestClient(app)
        yield client
    except ImportError:
        pytest.skip("FastAPI app not available for testing")


@pytest.fixture
def auth_headers(test_config):
    """Authentication headers for API testing"""
    token = test_config.get("api.auth_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.fixture
def authenticated_client(sync_api_client, auth_headers):
    """Authenticated test client"""
    sync_api_client.headers.update(auth_headers)
    return sync_api_client


# Test Data Fixtures
@pytest.fixture
def sample_market_data():
    """Sample market data fixture"""
    return TestDataFactory.create_market_data()


@pytest.fixture
def sample_user_data():
    """Sample user data fixture"""
    return TestDataFactory.create_user_data()


@pytest.fixture
def sample_technical_indicators():
    """Sample technical indicators fixture"""
    return TestDataFactory.create_technical_indicators()


@pytest.fixture
def bulk_market_data():
    """Bulk market data fixture"""
    return TestDataFactory.create_bulk_market_data(symbols=["600000", "600519", "000001"], count_per_symbol=5)


@pytest.fixture
def test_data_factory():
    """Test data factory fixture"""
    return TestDataFactory()


# Utility Functions
def load_test_fixture(fixture_name: str, fixture_dir: str = "tests/file_level/fixtures") -> Dict[str, Any]:
    """
    Load test fixture from file

    Args:
        fixture_name: Name of fixture file (without extension)
        fixture_dir: Directory containing fixtures

    Returns:
        Fixture data as dictionary
    """
    fixture_path = Path(fixture_dir) / f"{fixture_name}.json"

    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture file not found: {fixture_path}")

    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_test_fixture(data: Dict[str, Any], fixture_name: str, fixture_dir: str = "tests/file_level/fixtures") -> None:
    """
    Save test fixture to file

    Args:
        data: Data to save
        fixture_name: Name of fixture file (without extension)
        fixture_dir: Directory containing fixtures
    """
    fixture_path = Path(fixture_dir) / f"{fixture_name}.json"
    fixture_path.parent.mkdir(parents=True, exist_ok=True)

    with open(fixture_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def cleanup_test_data(test_db_session, tables: Optional[List[str]] = None) -> None:
    """
    Clean up test data from database

    Args:
        test_db_session: Database session
        tables: List of tables to clean (if None, clean all test tables)
    """
    if tables is None:
        tables = ["market_data_test", "user_data_test", "technical_indicators_test"]

    for table in tables:
        try:
            test_db_session.execute(f"DELETE FROM {table}")
            test_db_session.commit()
        except Exception:
            # Ignore cleanup errors
            test_db_session.rollback()
            pass


def assert_api_response_format(response_data: Dict[str, Any], required_fields: Optional[List[str]] = None) -> None:
    """
    Assert that API response follows standard format

    Args:
        response_data: API response data
        required_fields: List of required fields in response
    """
    # Check for standard response structure
    assert isinstance(response_data, dict), "Response must be a dictionary"

    # Check for common response fields
    if "success" in response_data:
        assert isinstance(response_data["success"], bool), "Success field must be boolean"

    if "data" in response_data:
        # Data can be dict, list, or primitive
        pass

    if "message" in response_data:
        assert isinstance(response_data["message"], str), "Message field must be string"

    if "error" in response_data:
        assert isinstance(response_data["error"], str), "Error field must be string"

    # Check required fields
    if required_fields:
        for field in required_fields:
            assert field in response_data, f"Required field '{field}' missing from response"


def assert_market_data_format(data: Dict[str, Any]) -> None:
    """
    Assert that market data follows expected format

    Args:
        data: Market data dictionary
    """
    required_fields = ["symbol", "price", "volume", "timestamp"]
    assert_api_response_format(data, required_fields)

    # Type checks
    assert isinstance(data["symbol"], str), "Symbol must be string"
    assert isinstance(data["price"], (int, float)), "Price must be numeric"
    assert isinstance(data["volume"], int), "Volume must be integer"
    assert isinstance(data["timestamp"], str), "Timestamp must be string"

    # Value checks
    assert len(data["symbol"]) > 0, "Symbol cannot be empty"
    assert data["price"] > 0, "Price must be positive"
    assert data["volume"] >= 0, "Volume must be non-negative"


def assert_user_data_format(data: Dict[str, Any]) -> None:
    """
    Assert that user data follows expected format

    Args:
        data: User data dictionary
    """
    required_fields = ["id", "username", "email", "role"]
    assert_api_response_format(data, required_fields)

    # Type checks
    assert isinstance(data["id"], str), "ID must be string"
    assert isinstance(data["username"], str), "Username must be string"
    assert isinstance(data["email"], str), "Email must be string"
    assert isinstance(data["role"], str), "Role must be string"

    # Value checks
    assert len(data["username"]) > 0, "Username cannot be empty"
    assert "@" in data["email"], "Email must contain @ symbol"
    assert data["role"] in ["admin", "user", "analyst"], f"Invalid role: {data['role']}"


# Parallel Test Execution Helpers
class ParallelTestRunner:
    """Helper for running tests in parallel"""

    def __init__(self, max_workers: int = 4, timeout: int = 60):
        self.max_workers = max_workers
        self.timeout = timeout

    async def run_tests_parallel(self, test_functions: List[Callable], *args, **kwargs) -> List[Any]:
        """
        Run test functions in parallel

        Args:
            test_functions: List of async test functions
            *args, **kwargs: Arguments to pass to test functions

        Returns:
            List of test results
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        async def run_single_test(test_func):
            """Run a single test function"""
            try:
                if asyncio.iscoroutinefunction(test_func):
                    return await test_func(*args, **kwargs)
                else:
                    # Run sync function in thread pool
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, test_func, *args, **kwargs)
            except Exception as e:
                return {"error": str(e), "test": test_func.__name__}

        # Run tests in parallel with limited concurrency
        semaphore = asyncio.Semaphore(self.max_workers)
        results = []

        async def run_with_semaphore(test_func):
            async with semaphore:
                return await run_single_test(test_func)

        tasks = [run_with_semaphore(test_func) for test_func in test_functions]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return results

    def run_sync_tests_parallel(self, test_functions: List[Callable], *args, **kwargs) -> List[Any]:
        """
        Run synchronous test functions in parallel

        Args:
            test_functions: List of sync test functions
            *args, **kwargs: Arguments to pass to test functions

        Returns:
            List of test results
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all test tasks
            future_to_test = {
                executor.submit(test_func, *args, **kwargs): test_func.__name__ for test_func in test_functions
            }

            # Collect results as they complete
            for future in as_completed(future_to_test):
                test_name = future_to_test[future]
                try:
                    result = future.result(timeout=self.timeout)
                    results.append({"test": test_name, "result": result})
                except Exception as e:
                    results.append({"test": test_name, "error": str(e)})

        return results


# Test Configuration Fixtures
@pytest.fixture
def parallel_runner(test_config):
    """Parallel test runner fixture"""
    max_workers = test_config.get("parallel.max_workers", 4)
    timeout = test_config.get("parallel.worker_timeout", 60)
    return ParallelTestRunner(max_workers=max_workers, timeout=timeout)


@pytest.fixture
def test_data_dir(test_config):
    """Test data directory fixture"""
    data_dir = test_config.get("data.fixtures_dir", "tests/file_level/fixtures")
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    return Path(data_dir)


@pytest.fixture
def report_dir(test_config):
    """Test report directory fixture"""
    report_dir = test_config.get("reporting.report_dir", "tests/file_level/reports")
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    return Path(report_dir)


# Performance Testing Utilities
class PerformanceTester:
    """Helper for performance testing"""

    def __init__(self, client):
        self.client = client
        self.results = []

    def measure_response_time(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Measure response time for an API call

        Args:
            method: HTTP method (GET, POST, etc.)
            url: API endpoint URL
            **kwargs: Additional arguments for the request

        Returns:
            Dictionary with timing and response data
        """
        import time

        start_time = time.time()

        try:
            if method.upper() == "GET":
                response = self.client.get(url, **kwargs)
            elif method.upper() == "POST":
                response = self.client.post(url, **kwargs)
            elif method.upper() == "PUT":
                response = self.client.put(url, **kwargs)
            elif method.upper() == "DELETE":
                response = self.client.delete(url, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            end_time = time.time()
            response_time = end_time - start_time

            result = {
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code < 400,
                "response_size": len(response.content) if hasattr(response, "content") else 0,
            }

            self.results.append(result)
            return result

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time

            result = {
                "method": method,
                "url": url,
                "status_code": None,
                "response_time": response_time,
                "success": False,
                "error": str(e),
            }

            self.results.append(result)
            return result

    def get_average_response_time(self) -> float:
        """Get average response time across all measurements"""
        if not self.results:
            return 0.0

        successful_results = [r for r in self.results if r.get("success", False)]
        if not successful_results:
            return 0.0

        total_time = sum(r["response_time"] for r in successful_results)
        return total_time / len(successful_results)

    def get_success_rate(self) -> float:
        """Get success rate across all measurements"""
        if not self.results:
            return 0.0

        successful_count = sum(1 for r in self.results if r.get("success", False))
        return successful_count / len(self.results) * 100

    def reset(self):
        """Reset performance measurements"""
        self.results = []


@pytest.fixture
def performance_tester(sync_api_client):
    """Performance tester fixture"""
    return PerformanceTester(sync_api_client)
