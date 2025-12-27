"""
OHLCV Storage Service Tests

Tests for PostgreSQL TimescaleDB integration for OHLCV bars

Task 7: 实现实时OHLCV柱线聚合与多时间周期支持

Author: Claude Code
Date: 2025-11-07
"""

from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime

from app.services.data_aggregation_service import OHLCV, Timeframe
from app.services.ohlcv_storage import (
    OHLCVStorage,
    get_ohlcv_storage,
    reset_ohlcv_storage,
)


class TestOHLCVStorageInitialization:
    """Test OHLCV Storage initialization"""

    def test_storage_creation(self):
        """Test storage object creation"""
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.return_value = MagicMock()
            storage = OHLCVStorage(host="localhost", port=5432)
            assert storage.host == "localhost"
            assert storage.port == 5432
            assert storage.bars_inserted == 0
            assert storage.insert_errors == 0

    def test_storage_with_custom_params(self):
        """Test storage with custom parameters"""
        storage = OHLCVStorage(host="192.168.1.1", port=5433, user="admin", database="testdb")
        assert storage.host == "192.168.1.1"
        assert storage.port == 5433
        assert storage.user == "admin"
        assert storage.database == "testdb"

    def test_storage_singleton(self):
        """Test singleton pattern"""
        reset_ohlcv_storage()
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.return_value = MagicMock()
            storage1 = get_ohlcv_storage()
            storage2 = get_ohlcv_storage()
            assert storage1 is storage2


class TestOHLCVStorageConnection:
    """Test database connection"""

    def test_connection_success(self):
        """Test successful connection"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            storage = OHLCVStorage()
            result = storage.connect()

            assert result is True
            assert storage.connection is not None
            mock_connect.assert_called_once()

    def test_connection_failure(self):
        """Test connection failure"""
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.side_effect = Exception("Connection refused")

            storage = OHLCVStorage()
            result = storage.connect()

            assert result is False
            assert storage.last_error is not None

    def test_disconnect(self):
        """Test disconnection"""
        with patch("psycopg2.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            storage = OHLCVStorage()
            storage.connect()
            storage.disconnect()

            mock_conn.close.assert_called_once()

    def test_setup_tables_creates_table(self):
        """Test table creation"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            storage = OHLCVStorage()
            storage.connect()

            # Verify execute was called for table creation
            assert mock_cursor.execute.called


class TestOHLCVStorageInsert:
    """Test OHLCV insertion"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_cursor = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    def test_insert_single_bar(self):
        """Test inserting a single bar"""
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.return_value = self.mock_conn

            storage = OHLCVStorage()
            storage.connect()

            bar = OHLCV(
                symbol="600519",
                timeframe=Timeframe.ONE_MINUTE,
                timestamp=1699000000000,
                open=Decimal("100.00"),
                high=Decimal("100.50"),
                low=Decimal("99.50"),
                close=Decimal("100.25"),
                volume=10000,
            )

            result = storage.insert_bar(bar)

            assert result is True
            assert storage.bars_inserted == 1
            self.mock_cursor.execute.assert_called()

    def test_insert_bar_database_error(self):
        """Test insert with database error"""
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.return_value = self.mock_conn
            self.mock_cursor.execute.side_effect = Exception("Database error")

            storage = OHLCVStorage()
            storage.connect()

            bar = OHLCV(
                symbol="600519",
                timeframe=Timeframe.ONE_MINUTE,
                timestamp=1699000000000,
                open=Decimal("100.00"),
                high=Decimal("100.50"),
                low=Decimal("99.50"),
                close=Decimal("100.25"),
                volume=10000,
            )

            result = storage.insert_bar(bar)

            assert result is False
            assert storage.insert_errors == 1
            assert storage.last_error is not None

    def test_insert_bar_no_connection(self):
        """Test insert without connection"""
        storage = OHLCVStorage()
        storage.connection = None

        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("100.00"),
            high=Decimal("100.50"),
            low=Decimal("99.50"),
            close=Decimal("100.25"),
            volume=10000,
        )

        result = storage.insert_bar(bar)
        assert result is False


class TestOHLCVStorageBatchInsert:
    """Test batch insertion"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_cursor = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    def test_batch_insert_multiple_bars(self):
        """Test inserting multiple bars"""
        with patch("psycopg2.connect") as mock_connect:
            with patch("app.services.ohlcv_storage.execute_batch") as mock_batch:
                mock_connect.return_value = self.mock_conn

                storage = OHLCVStorage()
                storage.connect()

                bars = [
                    OHLCV(
                        symbol="600519",
                        timeframe=Timeframe.ONE_MINUTE,
                        timestamp=1699000000000 + i * 60000,
                        open=Decimal("100.00"),
                        high=Decimal("100.50"),
                        low=Decimal("99.50"),
                        close=Decimal("100.25"),
                        volume=10000,
                    )
                    for i in range(5)
                ]

                count = storage.insert_bars_batch(bars)

                assert count == 5
                assert storage.bars_inserted == 5
                mock_batch.assert_called_once()

    def test_batch_insert_empty_list(self):
        """Test batch insert with empty list"""
        storage = OHLCVStorage()
        storage.connection = None

        count = storage.insert_bars_batch([])
        assert count == 0

    def test_batch_insert_error(self):
        """Test batch insert with error"""
        with patch("psycopg2.connect") as mock_connect:
            with patch("app.services.ohlcv_storage.execute_batch") as mock_batch:
                mock_connect.return_value = self.mock_conn
                mock_batch.side_effect = Exception("Batch error")

                storage = OHLCVStorage()
                storage.connect()

                bars = [
                    OHLCV(
                        symbol="600519",
                        timeframe=Timeframe.ONE_MINUTE,
                        timestamp=1699000000000,
                        open=Decimal("100.00"),
                        high=Decimal("100.50"),
                        low=Decimal("99.50"),
                        close=Decimal("100.25"),
                        volume=10000,
                    )
                ]

                count = storage.insert_bars_batch(bars)

                assert count == 0
                assert storage.insert_errors == 1


class TestOHLCVStorageQuery:
    """Test query operations"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_cursor = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    def test_query_bars_success(self):
        """Test successful query"""
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.return_value = self.mock_conn

            # Mock query result
            mock_row = (
                "600519",
                "1m",
                1699000000000,
                100.00,
                100.50,
                99.50,
                100.25,
                10000,
                10,
                True,
                datetime.utcnow(),
            )
            self.mock_cursor.fetchall.return_value = [mock_row]

            storage = OHLCVStorage()
            storage.connect()

            bars = storage.query_bars(
                symbol="600519",
                timeframe=Timeframe.ONE_MINUTE,
                start_timestamp=1699000000000,
                end_timestamp=1699010000000,
            )

            assert len(bars) == 1
            assert bars[0]["symbol"] == "600519"
            assert bars[0]["close"] == Decimal("100.25")

    def test_query_bars_empty_result(self):
        """Test query with no results"""
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.return_value = self.mock_conn
            self.mock_cursor.fetchall.return_value = []

            storage = OHLCVStorage()
            storage.connect()

            bars = storage.query_bars(
                symbol="nonexistent",
                timeframe=Timeframe.ONE_MINUTE,
                start_timestamp=1699000000000,
                end_timestamp=1699010000000,
            )

            assert len(bars) == 0

    def test_query_bars_no_connection(self):
        """Test query without connection"""
        storage = OHLCVStorage()
        storage.connection = None

        bars = storage.query_bars(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            start_timestamp=1699000000000,
            end_timestamp=1699010000000,
        )

        assert len(bars) == 0

    def test_query_bars_database_error(self):
        """Test query with database error"""
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.return_value = self.mock_conn
            self.mock_cursor.execute.side_effect = Exception("Query error")

            storage = OHLCVStorage()
            storage.connect()

            bars = storage.query_bars(
                symbol="600519",
                timeframe=Timeframe.ONE_MINUTE,
                start_timestamp=1699000000000,
                end_timestamp=1699010000000,
            )

            assert len(bars) == 0
            assert storage.last_error is not None


class TestOHLCVStorageGetLatest:
    """Test getting latest bar"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_cursor = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    def test_get_latest_bar_success(self):
        """Test getting latest bar"""
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.return_value = self.mock_conn

            mock_row = (
                "600519",
                "1m",
                1699000000000,
                100.00,
                100.50,
                99.50,
                100.25,
                10000,
                10,
                True,
                datetime.utcnow(),
            )
            self.mock_cursor.fetchone.return_value = mock_row

            storage = OHLCVStorage()
            storage.connect()

            bar = storage.get_latest_bar(symbol="600519", timeframe=Timeframe.ONE_MINUTE)

            assert bar is not None
            assert bar["symbol"] == "600519"
            assert bar["close"] == Decimal("100.25")

    def test_get_latest_bar_not_found(self):
        """Test getting latest bar when none exists"""
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.return_value = self.mock_conn
            self.mock_cursor.fetchone.return_value = None

            storage = OHLCVStorage()
            storage.connect()

            bar = storage.get_latest_bar(symbol="nonexistent", timeframe=Timeframe.ONE_MINUTE)

            assert bar is None

    def test_get_latest_bar_no_connection(self):
        """Test getting latest bar without connection"""
        storage = OHLCVStorage()
        storage.connection = None

        bar = storage.get_latest_bar(symbol="600519", timeframe=Timeframe.ONE_MINUTE)

        assert bar is None


class TestOHLCVStorageStats:
    """Test statistics"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_cursor = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    def test_get_stats_with_connection(self):
        """Test getting stats with active connection"""
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.return_value = self.mock_conn

            # Mock stats queries - each query returns a tuple
            self.mock_cursor.fetchone.side_effect = [(1000,), (10,), ("1.5 MB",)]

            storage = OHLCVStorage()
            storage.connect()
            storage.bars_inserted = 500

            stats = storage.get_stats()

            assert stats["connected"] is True
            assert stats["total_bars"] == 1000
            assert stats["total_symbols"] == 10
            assert stats["table_size"] == "1.5 MB"
            assert stats["bars_inserted"] == 500

    def test_get_stats_no_connection(self):
        """Test getting stats without connection"""
        storage = OHLCVStorage()
        storage.connection = None
        storage.bars_inserted = 100

        stats = storage.get_stats()

        assert stats["connected"] is False
        assert stats["bars_inserted"] == 100

    def test_get_stats_database_error(self):
        """Test getting stats with database error"""
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.return_value = self.mock_conn
            self.mock_cursor.execute.side_effect = Exception("Stats error")

            storage = OHLCVStorage()
            storage.connect()

            stats = storage.get_stats()

            assert stats["connected"] is False
            assert "error" in stats
