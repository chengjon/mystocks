"""
订阅存储服务测试

Tests for Subscription Storage

Task 8: 实现灵活的用户订阅过滤系统

Author: Claude Code
Date: 2025-11-07
"""

from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from app.services.filter_service import (
    FilterOperator,
    FilterCondition,
    FilterExpression,
    Subscription,
    Alert,
    AlertPriority,
    AlertDeliveryMethod,
)
from app.services.subscription_storage import (
    SubscriptionStorage,
    get_subscription_storage,
    reset_subscription_storage,
)


class TestSubscriptionStorageInitialization:
    """Test storage initialization"""

    def test_storage_creation(self):
        """Test storage object creation"""
        storage = SubscriptionStorage(
            host="localhost",
            port=5432,
            user="test",
            password="pass",
            database="testdb",
        )

        assert storage.host == "localhost"
        assert storage.port == 5432
        assert storage.user == "test"
        assert storage.password == "pass"
        assert storage.database == "testdb"
        assert storage.subscriptions_created == 0
        assert storage.alerts_created == 0

    def test_storage_singleton(self):
        """Test singleton pattern"""
        reset_subscription_storage()
        storage1 = get_subscription_storage()
        storage2 = get_subscription_storage()
        assert storage1 is storage2


class TestSubscriptionStorageConnection:
    """Test database connection"""

    def test_connection_failure(self):
        """Test connection failure handling"""
        storage = SubscriptionStorage()

        with patch("psycopg2.connect") as mock_connect:
            mock_connect.side_effect = Exception("Connection refused")
            result = storage.connect()

            assert result is False
            assert storage.last_error is not None

    def test_setup_tables_without_connection(self):
        """Test table setup without connection"""
        storage = SubscriptionStorage()
        storage.connection = None

        result = storage.setup_tables()
        assert result is False


class TestSubscriptionStorageSave:
    """Test subscription save operations"""

    def test_save_subscription_structure(self):
        """Test subscription save with proper structure"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            # Create filter expression with conditions
            expr = FilterExpression(id="expr_1", name="Test Filter", expression="", logic="AND")
            expr.add_condition(
                FilterCondition(
                    field="price",
                    operator=FilterOperator.GT,
                    value=100.0,
                )
            )

            # Create subscription
            sub = Subscription(
                id="sub_1",
                user_id="user_1",
                name="Test Sub",
                filter_expr=expr,
                priority=AlertPriority.HIGH,
            )

            result = storage.save_subscription(sub)

            assert result is True
            assert storage.subscriptions_created == 1
            # Verify execute was called for subscription, expression, and conditions
            assert mock_cursor.execute.call_count >= 3


class TestSubscriptionStorageDelete:
    """Test subscription delete operations"""

    def test_delete_subscription(self):
        """Test subscription deletion"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            result = storage.delete_subscription("sub_1")

            assert result is True
            assert storage.subscriptions_deleted == 1
            mock_cursor.execute.assert_called()

    def test_delete_subscription_without_connection(self):
        """Test delete without connection"""
        storage = SubscriptionStorage()
        storage.connection = None

        result = storage.delete_subscription("sub_1")
        assert result is False


class TestSubscriptionStorageGet:
    """Test subscription get operations"""

    def test_get_subscription_success(self):
        """Test getting a subscription"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            # Mock database row
            mock_row = (
                "sub_1",
                "user_1",
                "Test Sub",
                "high",
                True,
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
                5,
                datetime.now(timezone.utc),
                None,
            )
            mock_cursor.fetchone.return_value = mock_row

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            result = storage.get_subscription("sub_1")

            assert result is not None
            assert result["id"] == "sub_1"
            assert result["user_id"] == "user_1"
            assert result["name"] == "Test Sub"
            assert result["priority"] == "high"
            assert result["enabled"] is True

    def test_get_subscription_not_found(self):
        """Test getting non-existent subscription"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None
            mock_connect.return_value = mock_conn

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            result = storage.get_subscription("nonexistent")
            assert result is None

    def test_get_subscription_without_connection(self):
        """Test get without connection"""
        storage = SubscriptionStorage()
        storage.connection = None

        result = storage.get_subscription("sub_1")
        assert result is None


class TestSubscriptionStorageGetUserSubscriptions:
    """Test getting user subscriptions"""

    def test_get_user_subscriptions_multiple(self):
        """Test getting multiple subscriptions for a user"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            # Mock multiple rows
            mock_rows = [
                (
                    "sub_1",
                    "user_1",
                    "Sub1",
                    "high",
                    True,
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc),
                    5,
                    datetime.now(timezone.utc),
                    None,
                ),
                (
                    "sub_2",
                    "user_1",
                    "Sub2",
                    "medium",
                    True,
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc),
                    3,
                    datetime.now(timezone.utc),
                    None,
                ),
            ]
            mock_cursor.fetchall.return_value = mock_rows

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            results = storage.get_user_subscriptions("user_1")

            assert len(results) == 2
            assert results[0]["id"] == "sub_1"
            assert results[1]["id"] == "sub_2"

    def test_get_user_subscriptions_empty(self):
        """Test getting subscriptions when user has none"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = []
            mock_connect.return_value = mock_conn

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            results = storage.get_user_subscriptions("user_no_subs")
            assert len(results) == 0


class TestSubscriptionStorageAlert:
    """Test alert save and retrieval"""

    def test_save_alert(self):
        """Test saving an alert"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            alert = Alert(
                id="alert_1",
                subscription_id="sub_1",
                timestamp=datetime.now(timezone.utc),
                data={"symbol": "600519", "price": 100.0},
                priority=AlertPriority.HIGH,
                delivery_methods={AlertDeliveryMethod.WEBSOCKET},
            )

            result = storage.save_alert(alert)

            assert result is True
            assert storage.alerts_created == 1
            mock_cursor.execute.assert_called()

    def test_get_subscription_alerts(self):
        """Test getting alerts for a subscription"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            # Mock alert rows
            mock_rows = [
                (
                    "alert_1",
                    "sub_1",
                    datetime.now(timezone.utc),
                    {"symbol": "600519"},
                    "high",
                    ["websocket"],
                    False,
                    True,
                ),
            ]
            mock_cursor.fetchall.return_value = mock_rows

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            results = storage.get_subscription_alerts("sub_1", limit=100)

            assert len(results) == 1
            assert results[0]["id"] == "alert_1"
            assert results[0]["priority"] == "high"

    def test_save_alert_without_connection(self):
        """Test save alert without connection"""
        storage = SubscriptionStorage()
        storage.connection = None

        alert = Alert(
            id="alert_1",
            subscription_id="sub_1",
            timestamp=datetime.now(timezone.utc),
            data={},
            priority=AlertPriority.HIGH,
            delivery_methods={AlertDeliveryMethod.WEBSOCKET},
        )

        result = storage.save_alert(alert)
        assert result is False


class TestSubscriptionStorageStats:
    """Test statistics"""

    def test_get_stats_connected(self):
        """Test getting stats when connected"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            # Mock count queries
            mock_cursor.fetchone.side_effect = [(10,), (8,), (50,)]

            storage = SubscriptionStorage()
            storage.connection = mock_conn
            storage.subscriptions_created = 10
            storage.subscriptions_deleted = 2
            storage.alerts_created = 50

            stats = storage.get_stats()

            assert stats["connected"] is True
            assert stats["total_subscriptions"] == 10
            assert stats["enabled_subscriptions"] == 8
            assert stats["total_alerts"] == 50
            assert stats["subscriptions_created"] == 10
            assert stats["subscriptions_deleted"] == 2
            assert stats["alerts_created"] == 50

    def test_get_stats_disconnected(self):
        """Test getting stats when disconnected"""
        storage = SubscriptionStorage()
        storage.connection = None

        stats = storage.get_stats()

        assert stats["connected"] is False

    def test_get_stats_error(self):
        """Test getting stats with error"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Query error")
            mock_connect.return_value = mock_conn

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            stats = storage.get_stats()

            assert stats["connected"] is False
            assert "error" in stats


class TestSubscriptionStorageErrorHandling:
    """Test error handling"""

    def test_save_subscription_database_error(self):
        """Test handling database error on save"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Database error")
            mock_connect.return_value = mock_conn

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            expr = FilterExpression(id="expr_1", name="Test", expression="")
            sub = Subscription(
                id="sub_1",
                user_id="user_1",
                name="Test",
                filter_expr=expr,
            )

            result = storage.save_subscription(sub)

            assert result is False
            assert storage.last_error is not None

    def test_get_user_subscriptions_error(self):
        """Test handling error on get user subscriptions"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Query error")
            mock_connect.return_value = mock_conn

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            results = storage.get_user_subscriptions("user_1")

            assert len(results) == 0
            assert storage.last_error is not None


class TestSubscriptionStorageIntegration:
    """Test integration scenarios"""

    def test_complete_workflow(self):
        """Test complete workflow: save, get, delete"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            # Create subscription
            expr = FilterExpression(id="expr_1", name="Test Filter", expression="", logic="AND")
            expr.add_condition(FilterCondition(field="price", operator=FilterOperator.GT, value=100.0))

            sub = Subscription(
                id="sub_1",
                user_id="user_1",
                name="Test Sub",
                filter_expr=expr,
                priority=AlertPriority.MEDIUM,
            )

            # Save
            assert storage.save_subscription(sub) is True
            assert storage.subscriptions_created == 1

            # Delete
            assert storage.delete_subscription("sub_1") is True
            assert storage.subscriptions_deleted == 1

    def test_multiple_conditions_save(self):
        """Test saving subscription with multiple conditions"""
        with patch("psycopg2.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            storage = SubscriptionStorage()
            storage.connection = mock_conn

            expr = FilterExpression(id="expr_1", name="Complex Filter", expression="", logic="AND")

            # Add multiple conditions
            expr.add_condition(FilterCondition(field="price", operator=FilterOperator.GT, value=100.0))
            expr.add_condition(FilterCondition(field="volume", operator=FilterOperator.LT, value=1000000))
            expr.add_condition(
                FilterCondition(
                    field="symbol",
                    operator=FilterOperator.IN,
                    value=["600519", "000001"],
                )
            )

            sub = Subscription(
                id="sub_1",
                user_id="user_1",
                name="Complex Sub",
                filter_expr=expr,
            )

            result = storage.save_subscription(sub)

            assert result is True
            # Should be called for: subscription, expression, condition 1, condition 2, condition 3
            assert mock_cursor.execute.call_count >= 5
