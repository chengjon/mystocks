"""
订阅存储服务 - Subscription Storage

Task 8: 实现灵活的用户订阅过滤系统

功能特性:
- 订阅和告警的持久化存储
- PostgreSQL后端支持
- 过滤条件版本控制
- 统计和分析查询

Author: Claude Code
Date: 2025-11-07
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from decimal import Decimal
import structlog
import psycopg2
from psycopg2.extras import execute_batch

from app.services.filter_service import (
    Subscription,
    FilterExpression,
    FilterCondition,
    FilterOperator,
    Alert,
    AlertPriority,
    AlertDeliveryMethod,
)

logger = structlog.get_logger()


class SubscriptionStorage:
    """订阅存储 - PostgreSQL后端"""

    # 表创建SQL
    CREATE_SUBSCRIPTIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS subscriptions (
        id VARCHAR(255) PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        priority VARCHAR(50) NOT NULL,
        enabled BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        match_count INTEGER DEFAULT 0,
        last_match_time TIMESTAMP,
        last_match_data JSONB,
        INDEX (user_id),
        INDEX (created_at)
    )
    """

    CREATE_FILTER_EXPRESSIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS filter_expressions (
        id VARCHAR(255) PRIMARY KEY,
        subscription_id VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        expression TEXT,
        logic VARCHAR(10) DEFAULT 'AND',
        enabled BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE,
        INDEX (subscription_id)
    )
    """

    CREATE_FILTER_CONDITIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS filter_conditions (
        id VARCHAR(255) PRIMARY KEY,
        expression_id VARCHAR(255) NOT NULL,
        field VARCHAR(255) NOT NULL,
        operator VARCHAR(50) NOT NULL,
        value JSONB,
        case_sensitive BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (expression_id) REFERENCES filter_expressions(id) ON DELETE CASCADE,
        INDEX (expression_id)
    )
    """

    CREATE_ALERTS_TABLE = """
    CREATE TABLE IF NOT EXISTS alerts (
        id VARCHAR(255) PRIMARY KEY,
        subscription_id VARCHAR(255) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        data JSONB,
        priority VARCHAR(50) NOT NULL,
        delivery_methods TEXT[],
        acknowledged BOOLEAN DEFAULT FALSE,
        delivered BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX (subscription_id),
        INDEX (timestamp),
        INDEX (created_at)
    )
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "password",
        database: str = "mystocks",
    ):
        """初始化订阅存储"""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

        # 指标
        self.subscriptions_created = 0
        self.subscriptions_deleted = 0
        self.alerts_created = 0
        self.last_error = None

        logger.info("✅ Subscription Storage initialized")

    def connect(self) -> bool:
        """连接到数据库"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            logger.info("✅ Connected to PostgreSQL")
            return True
        except Exception as e:
            logger.error("❌ Connection failed", error=str(e))
            self.last_error = str(e)
            return False

    def disconnect(self) -> None:
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("✅ Disconnected from PostgreSQL")

    def setup_tables(self) -> bool:
        """创建数据库表"""
        if not self.connection:
            logger.warning("⚠️ Not connected")
            return False

        try:
            cursor = self.connection.cursor()

            # 创建表
            for create_sql in [
                self.CREATE_SUBSCRIPTIONS_TABLE,
                self.CREATE_FILTER_EXPRESSIONS_TABLE,
                self.CREATE_FILTER_CONDITIONS_TABLE,
                self.CREATE_ALERTS_TABLE,
            ]:
                cursor.execute(create_sql)

            self.connection.commit()
            logger.info("✅ Tables created successfully")
            return True

        except Exception as e:
            logger.error("❌ Setup failed", error=str(e))
            self.last_error = str(e)
            return False

    def save_subscription(self, subscription: Subscription) -> bool:
        """保存订阅"""
        if not self.connection:
            logger.warning("⚠️ Not connected")
            return False

        try:
            cursor = self.connection.cursor()

            # 保存订阅
            cursor.execute(
                """
                INSERT INTO subscriptions
                (id, user_id, name, priority, enabled, created_at, updated_at,
                 match_count, last_match_time, last_match_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    priority = EXCLUDED.priority,
                    enabled = EXCLUDED.enabled,
                    updated_at = EXCLUDED.updated_at,
                    match_count = EXCLUDED.match_count,
                    last_match_time = EXCLUDED.last_match_time,
                    last_match_data = EXCLUDED.last_match_data
                """,
                (
                    subscription.id,
                    subscription.user_id,
                    subscription.name,
                    subscription.priority.value,
                    subscription.enabled,
                    subscription.created_at,
                    subscription.updated_at,
                    subscription.match_count,
                    subscription.last_match_time,
                    json.dumps(subscription.last_match_data),
                ),
            )

            # 保存过滤表达式
            filter_expr = subscription.filter_expr
            cursor.execute(
                """
                INSERT INTO filter_expressions
                (id, subscription_id, name, expression, logic, enabled, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    expression = EXCLUDED.expression,
                    logic = EXCLUDED.logic,
                    enabled = EXCLUDED.enabled
                """,
                (
                    filter_expr.id,
                    subscription.id,
                    filter_expr.name,
                    filter_expr.expression,
                    filter_expr.logic,
                    filter_expr.enabled,
                    filter_expr.created_at,
                ),
            )

            # 保存过滤条件
            for i, condition in enumerate(filter_expr.conditions):
                condition_id = f"{filter_expr.id}_cond_{i}"
                cursor.execute(
                    """
                    INSERT INTO filter_conditions
                    (id, expression_id, field, operator, value, case_sensitive)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        field = EXCLUDED.field,
                        operator = EXCLUDED.operator,
                        value = EXCLUDED.value,
                        case_sensitive = EXCLUDED.case_sensitive
                    """,
                    (
                        condition_id,
                        filter_expr.id,
                        condition.field,
                        condition.operator.value,
                        json.dumps(_serialize_value(condition.value)),
                        condition.case_sensitive,
                    ),
                )

            self.connection.commit()
            self.subscriptions_created += 1
            logger.info("✅ Subscription saved", subscription_id=subscription.id)
            return True

        except Exception as e:
            logger.error("❌ Save failed", error=str(e))
            self.last_error = str(e)
            return False

    def delete_subscription(self, subscription_id: str) -> bool:
        """删除订阅"""
        if not self.connection:
            logger.warning("⚠️ Not connected")
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM subscriptions WHERE id = %s", (subscription_id,)
            )
            self.connection.commit()
            self.subscriptions_deleted += 1
            logger.info("✅ Subscription deleted", subscription_id=subscription_id)
            return True

        except Exception as e:
            logger.error("❌ Delete failed", error=str(e))
            self.last_error = str(e)
            return False

    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """获取订阅"""
        if not self.connection:
            logger.warning("⚠️ Not connected")
            return None

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM subscriptions WHERE id = %s", (subscription_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "user_id": row[1],
                "name": row[2],
                "priority": row[3],
                "enabled": row[4],
                "created_at": row[5],
                "updated_at": row[6],
                "match_count": row[7],
                "last_match_time": row[8],
                "last_match_data": row[9],
            }

        except Exception as e:
            logger.error("❌ Get failed", error=str(e))
            self.last_error = str(e)
            return None

    def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户订阅列表"""
        if not self.connection:
            logger.warning("⚠️ Not connected")
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM subscriptions WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,),
            )
            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "user_id": row[1],
                    "name": row[2],
                    "priority": row[3],
                    "enabled": row[4],
                    "created_at": row[5],
                    "updated_at": row[6],
                    "match_count": row[7],
                    "last_match_time": row[8],
                    "last_match_data": row[9],
                }
                for row in rows
            ]

        except Exception as e:
            logger.error("❌ Get user subscriptions failed", error=str(e))
            self.last_error = str(e)
            return []

    def save_alert(self, alert: Alert) -> bool:
        """保存告警"""
        if not self.connection:
            logger.warning("⚠️ Not connected")
            return False

        try:
            cursor = self.connection.cursor()

            cursor.execute(
                """
                INSERT INTO alerts
                (id, subscription_id, timestamp, data, priority,
                 delivery_methods, acknowledged, delivered, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    alert.id,
                    alert.subscription_id,
                    alert.timestamp,
                    json.dumps(alert.data),
                    alert.priority.value,
                    list(alert.delivery_methods),
                    alert.acknowledged,
                    alert.delivered,
                    datetime.utcnow(),
                ),
            )

            self.connection.commit()
            self.alerts_created += 1
            logger.info("✅ Alert saved", alert_id=alert.id)
            return True

        except Exception as e:
            logger.error("❌ Alert save failed", error=str(e))
            self.last_error = str(e)
            return False

    def get_subscription_alerts(
        self,
        subscription_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """获取订阅的告警列表"""
        if not self.connection:
            logger.warning("⚠️ Not connected")
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT id, subscription_id, timestamp, data, priority,
                       delivery_methods, acknowledged, delivered
                FROM alerts
                WHERE subscription_id = %s
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
                """,
                (subscription_id, limit, offset),
            )
            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "subscription_id": row[1],
                    "timestamp": row[2],
                    "data": row[3],
                    "priority": row[4],
                    "delivery_methods": row[5],
                    "acknowledged": row[6],
                    "delivered": row[7],
                }
                for row in rows
            ]

        except Exception as e:
            logger.error("❌ Get alerts failed", error=str(e))
            self.last_error = str(e)
            return []

    def get_stats(self) -> Dict[str, Any]:
        """获取存储统计"""
        if not self.connection:
            return {"connected": False}

        try:
            cursor = self.connection.cursor()

            # 获取订阅计数
            cursor.execute("SELECT COUNT(*) FROM subscriptions")
            total_subscriptions = cursor.fetchone()[0]

            # 获取启用的订阅数
            cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE enabled = TRUE")
            enabled_subscriptions = cursor.fetchone()[0]

            # 获取告警计数
            cursor.execute("SELECT COUNT(*) FROM alerts")
            total_alerts = cursor.fetchone()[0]

            return {
                "connected": True,
                "total_subscriptions": total_subscriptions,
                "enabled_subscriptions": enabled_subscriptions,
                "total_alerts": total_alerts,
                "subscriptions_created": self.subscriptions_created,
                "subscriptions_deleted": self.subscriptions_deleted,
                "alerts_created": self.alerts_created,
            }

        except Exception as e:
            logger.error("❌ Get stats failed", error=str(e))
            return {"connected": False, "error": str(e)}


def _serialize_value(value: Any) -> Any:
    """序列化值为JSON兼容格式"""
    if isinstance(value, list):
        return [_serialize_value(v) for v in value]
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, (int, float, str, bool)):
        return value
    else:
        return str(value)


# 全局单例
_storage: Optional[SubscriptionStorage] = None


def get_subscription_storage() -> SubscriptionStorage:
    """获取订阅存储单例"""
    global _storage
    if _storage is None:
        _storage = SubscriptionStorage()
    return _storage


def reset_subscription_storage() -> None:
    """重置订阅存储单例（仅用于测试）"""
    global _storage
    _storage = None
