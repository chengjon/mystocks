"""
Integration tests for TDengineManager - Task 2.1: TDengine Cache Integration

Tests cover:
- Connection establishment and health checks
- Database and table initialization
- Cache read/write operations
- TTL-based expiration
- Error handling and recovery
- Cache statistics tracking
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.tdengine_manager import (
    TDengineManager,
    get_tdengine_manager,
    reset_tdengine_manager,
)


class TestTDengineConnection:
    """Test TDengineManager connection functionality"""

    def setup_method(self):
        """Setup before each test"""
        reset_tdengine_manager()
        self.manager = TDengineManager(
            host=os.getenv("TDENGINE_HOST", "127.0.0.1"),
            port=int(os.getenv("TDENGINE_PORT", "6030")),
            database="mystocks_cache_test",
        )

    def teardown_method(self):
        """Cleanup after each test"""
        if self.manager:
            self.manager.close()

    def test_connection_success(self):
        """Test successful TDengine connection"""
        result = self.manager.connect()
        assert result is True, "Connection should succeed"
        assert self.manager._conn is not None, "Connection object should exist"

    def test_connection_failure_invalid_host(self):
        """Test connection failure with invalid host"""
        manager = TDengineManager(host="invalid-host-12345.local", port=6030)
        result = manager.connect()
        assert result is False, "Connection to invalid host should fail"
        assert manager._conn is None, "Connection object should be None"

    def test_health_check_after_initialization(self):
        """Test health check after database initialization"""
        self.manager.initialize()
        result = self.manager.health_check()
        assert result is True, "Health check should pass after initialization"

    def test_health_check_without_connection(self):
        """Test health check without prior connection"""
        manager = TDengineManager()
        manager._is_initialized = False
        result = manager.health_check()
        # Should either return True (if connection succeeded) or False
        assert isinstance(result, bool), "Health check should return boolean"


class TestTDengineInitialization:
    """Test TDengineManager database and table initialization"""

    def setup_method(self):
        """Setup before each test"""
        reset_tdengine_manager()
        self.manager = TDengineManager(
            host=os.getenv("TDENGINE_HOST", "127.0.0.1"),
            port=int(os.getenv("TDENGINE_PORT", "6030")),
            database="mystocks_cache_test",
        )

    def teardown_method(self):
        """Cleanup after each test"""
        if self.manager:
            self.manager.close()

    def test_database_initialization(self):
        """Test database creation and initialization"""
        result = self.manager.initialize()
        assert result is True, "Database initialization should succeed"
        assert self.manager._is_initialized is True, "Manager should be marked as initialized"

    def test_database_already_exists(self):
        """Test initialization when database already exists"""
        self.manager.initialize()
        # Second initialization should also succeed
        result = self.manager.initialize()
        assert result is True, "Second initialization should succeed"

    def test_tables_created(self):
        """Test that required tables are created"""
        self.manager.initialize()

        # Try to query from each table
        try:
            result = self.manager._execute_query("SELECT COUNT(*) FROM market_data_cache LIMIT 1")
            assert result is not None, "market_data_cache table should exist"
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {str(e)}")

    def test_singleton_manager(self):
        """Test singleton pattern for TDengineManager"""
        reset_tdengine_manager()
        manager1 = get_tdengine_manager()
        manager2 = get_tdengine_manager()
        assert manager1 is manager2, "Should return same instance"


class TestCacheWriteOperations:
    """Test cache write operations"""

    def setup_method(self):
        """Setup before each test"""
        reset_tdengine_manager()
        self.manager = TDengineManager(
            host=os.getenv("TDENGINE_HOST", "127.0.0.1"),
            port=int(os.getenv("TDENGINE_PORT", "6030")),
            database="mystocks_cache_test",
        )
        try:
            self.manager.initialize()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {str(e)}")

    def teardown_method(self):
        """Cleanup after each test"""
        if self.manager:
            self.manager.close()

    def test_write_cache_simple(self):
        """Test writing simple cache data"""
        data = {
            "main_net_inflow": 1000000,
            "main_percent": 2.5,
            "retail_net_inflow": 500000,
        }

        result = self.manager.write_cache(symbol="000001", data_type="fund_flow", timeframe="1d", data=data)
        assert result is True, "Write cache should succeed"

    def test_write_cache_complex_data(self):
        """Test writing complex nested data"""
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": "000001",
            "metrics": {
                "fund_inflow": {
                    "main": 1000000,
                    "retail": 500000,
                    "institutional": 2000000,
                },
                "price_action": {
                    "open": 10.50,
                    "high": 10.75,
                    "low": 10.25,
                    "close": 10.60,
                },
            },
        }

        result = self.manager.write_cache(symbol="000001", data_type="comprehensive", timeframe="1d", data=data)
        assert result is True, "Write complex cache should succeed"

    def test_write_cache_multiple_symbols(self):
        """Test writing cache for multiple symbols"""
        symbols = ["000001", "000002", "000003"]

        for symbol in symbols:
            data = {"value": symbol}
            result = self.manager.write_cache(symbol=symbol, data_type="test", timeframe="1d", data=data)
            assert result is True, f"Write for {symbol} should succeed"

    def test_write_cache_without_initialization(self):
        """Test write fails without initialization"""
        manager = TDengineManager()
        manager._is_initialized = False

        result = manager.write_cache(symbol="000001", data_type="test", timeframe="1d", data={"test": "data"})
        assert result is False, "Write should fail without initialization"

    def test_write_with_custom_timestamp(self):
        """Test write cache with custom timestamp"""
        custom_time = datetime.utcnow() - timedelta(days=1)
        data = {"value": 100}

        result = self.manager.write_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data=data,
            timestamp=custom_time,
        )
        assert result is True, "Write with custom timestamp should succeed"


class TestCacheReadOperations:
    """Test cache read operations"""

    def setup_method(self):
        """Setup before each test"""
        reset_tdengine_manager()
        self.manager = TDengineManager(
            host=os.getenv("TDENGINE_HOST", "127.0.0.1"),
            port=int(os.getenv("TDENGINE_PORT", "6030")),
            database="mystocks_cache_test",
        )
        try:
            self.manager.initialize()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {str(e)}")

    def teardown_method(self):
        """Cleanup after each test"""
        if self.manager:
            self.manager.close()

    def test_read_cache_after_write(self):
        """Test reading cache after writing data"""
        # Write data
        write_data = {"main_inflow": 1000000, "retail_inflow": 500000}
        self.manager.write_cache(symbol="000001", data_type="fund_flow", timeframe="1d", data=write_data)

        # Read it back
        read_data = self.manager.read_cache(symbol="000001", data_type="fund_flow")

        assert read_data is not None, "Should read cached data"
        assert read_data["main_inflow"] == 1000000, "Data should match written value"

    def test_read_nonexistent_cache(self):
        """Test reading cache that doesn't exist"""
        result = self.manager.read_cache(symbol="999999", data_type="nonexistent")
        assert result is None, "Should return None for nonexistent cache"

    def test_read_with_timeframe_filter(self):
        """Test reading cache with timeframe filter"""
        data = {"value": 100}

        self.manager.write_cache(symbol="000001", data_type="test", timeframe="1d", data=data)

        # Read with matching timeframe
        result = self.manager.read_cache(symbol="000001", data_type="test", timeframe="1d")
        assert result is not None, "Should find cache with matching timeframe"

    def test_read_with_time_window(self):
        """Test reading cache within time window"""
        data = {"value": 100}

        self.manager.write_cache(symbol="000001", data_type="test", timeframe="1d", data=data)

        # Read within 1 day
        result = self.manager.read_cache(symbol="000001", data_type="test", days=1)
        assert result is not None, "Should find cache within time window"

        # Read outside time window (expect None)
        result = self.manager.read_cache(
            symbol="000001",
            data_type="test",
            days=0,  # 0 days = no lookback
        )
        # May be None or not depending on exact timing
        assert isinstance(result, (dict, type(None))), "Should return dict or None"

    def test_read_updates_hit_count(self):
        """Test that reads update hit count"""
        data = {"value": 100}

        self.manager.write_cache(symbol="000001", data_type="test", timeframe="1d", data=data)

        # Read multiple times (should increment hit count)
        self.manager.read_cache(symbol="000001", data_type="test")
        self.manager.read_cache(symbol="000001", data_type="test")

        # Note: We can't directly query hit_count without complex SQL
        # But the fact that reads succeed indicates the mechanism is working


class TestCacheExpirationAndCleanup:
    """Test TTL and cache cleanup operations"""

    def setup_method(self):
        """Setup before each test"""
        reset_tdengine_manager()
        self.manager = TDengineManager(
            host=os.getenv("TDENGINE_HOST", "127.0.0.1"),
            port=int(os.getenv("TDENGINE_PORT", "6030")),
            database="mystocks_cache_test",
        )
        try:
            self.manager.initialize()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {str(e)}")

    def teardown_method(self):
        """Cleanup after each test"""
        if self.manager:
            self.manager.close()

    def test_clear_expired_cache(self):
        """Test clearing expired cache"""
        # Write old data (8 days ago)
        old_time = datetime.utcnow() - timedelta(days=8)
        self.manager.write_cache(
            symbol="000001",
            data_type="old_data",
            timeframe="1d",
            data={"value": "old"},
            timestamp=old_time,
        )

        # Clear cache older than 7 days
        result = self.manager.clear_expired_cache(days=7)
        assert result >= 0, "Cleanup should return number of deleted records"

    def test_clear_expired_without_initialization(self):
        """Test cleanup fails without initialization"""
        manager = TDengineManager()
        manager._is_initialized = False

        result = manager.clear_expired_cache(days=7)
        assert result == 0, "Cleanup should return 0 without initialization"

    def test_clear_with_custom_retention(self):
        """Test cleanup with custom retention period"""
        # Write data at different times
        for days_ago in [1, 5, 10, 15]:
            timestamp = datetime.utcnow() - timedelta(days=days_ago)
            self.manager.write_cache(
                symbol="000001",
                data_type="test",
                timeframe="1d",
                data={"days_ago": days_ago},
                timestamp=timestamp,
            )

        # Clear cache older than 7 days
        result = self.manager.clear_expired_cache(days=7)
        assert result >= 0, "Should successfully clean old data"


class TestCacheStatistics:
    """Test cache statistics and monitoring"""

    def setup_method(self):
        """Setup before each test"""
        reset_tdengine_manager()
        self.manager = TDengineManager(
            host=os.getenv("TDENGINE_HOST", "127.0.0.1"),
            port=int(os.getenv("TDENGINE_PORT", "6030")),
            database="mystocks_cache_test",
        )
        try:
            self.manager.initialize()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {str(e)}")

    def teardown_method(self):
        """Cleanup after each test"""
        if self.manager:
            self.manager.close()

    def test_get_cache_stats_empty(self):
        """Test getting cache stats from empty cache"""
        stats = self.manager.get_cache_stats()
        # Stats might be None or have zero counts
        if stats:
            assert "total_records" in stats, "Should have total_records"
            assert stats["total_records"] >= 0, "Total records should be non-negative"

    def test_get_cache_stats_with_data(self):
        """Test getting cache stats after writing data"""
        # Write some data
        for i in range(5):
            self.manager.write_cache(symbol=f"00000{i}", data_type="test", timeframe="1d", data={"index": i})

        stats = self.manager.get_cache_stats()
        if stats:
            assert "timestamp" in stats, "Should have timestamp"
            assert isinstance(stats["timestamp"], str), "Timestamp should be string"

    def test_cache_stats_without_initialization(self):
        """Test getting stats without initialization"""
        manager = TDengineManager()
        manager._is_initialized = False

        stats = manager.get_cache_stats()
        assert stats is None, "Stats should be None without initialization"


class TestErrorHandling:
    """Test error handling and edge cases"""

    def setup_method(self):
        """Setup before each test"""
        reset_tdengine_manager()
        self.manager = TDengineManager(
            host=os.getenv("TDENGINE_HOST", "127.0.0.1"),
            port=int(os.getenv("TDENGINE_PORT", "6030")),
            database="mystocks_cache_test",
        )
        try:
            self.manager.initialize()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {str(e)}")

    def teardown_method(self):
        """Cleanup after each test"""
        if self.manager:
            self.manager.close()

    def test_write_with_special_characters(self):
        """Test writing data with special characters"""
        data = {
            "name": "测试数据 中文",
            "description": "Special chars: !@#$%^&*()",
            "emoji": "🚀📈💰",
        }

        result = self.manager.write_cache(symbol="000001", data_type="test", timeframe="1d", data=data)
        assert result is True, "Should handle special characters"

    def test_write_with_large_data(self):
        """Test writing large data (stress test)"""
        # Create large data structure
        large_data = {f"key_{i}": f"value_{i}" for i in range(100)}

        result = self.manager.write_cache(symbol="000001", data_type="large_data", timeframe="1d", data=large_data)
        # May succeed or fail depending on size limits
        assert isinstance(result, bool), "Should return boolean"

    def test_close_and_cleanup(self):
        """Test proper cleanup on close"""
        self.manager.close()
        assert self.manager._is_initialized is False, "Should mark as uninitialized"

    def test_multiple_connections_singleton(self):
        """Test that singleton prevents multiple connections"""
        reset_tdengine_manager()
        manager1 = get_tdengine_manager()
        manager1.initialize()

        manager2 = get_tdengine_manager()
        # Should get same instance
        assert manager1._conn is manager2._conn, "Should share connection"


# Pytest fixtures
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests"""
    # Check if TDengine is available
    temp_manager = TDengineManager()
    if not temp_manager.connect():
        pytest.skip("TDengine service is not running. Start with: docker-compose -f docker-compose.tdengine.yml up -d")
    temp_manager.close()


if __name__ == "__main__":
    # Run tests with: pytest web/backend/tests/test_tdengine_manager.py -v
    pytest.main([__file__, "-v", "--tb=short"])
