"""PostgreSQLRelationalDataSource 用户偏好方法集。"""

from __future__ import annotations

from typing import Any, Dict

from psycopg2 import sql

from .core import logger


class PostgreSQLRelationalDataSourcePreferencesMixin:
    """用户偏好查询与更新方法。"""

    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """获取用户偏好设置。"""
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            sql = """
                SELECT user_id, display_settings, notification_settings,
                       trading_settings, updated_at
                FROM user_preferences
                WHERE user_id = %s
            """
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()

            if not row:
                return {
                    "user_id": user_id,
                    "display_settings": {},
                    "notification_settings": {},
                    "trading_settings": {},
                    "updated_at": None,
                }

            result = {
                "user_id": row[0],
                "display_settings": row[1] or {},
                "notification_settings": row[2] or {},
                "trading_settings": row[3] or {},
                "updated_at": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else None,
            }

            cursor.close()
            self.pg_access._return_connection(conn)
            logger.info("获取用户偏好成功: user_id=%s", user_id)
            return result

        except Exception as e:
            logger.error("获取用户偏好失败: %s", e)
            raise

    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """更新用户偏好设置。"""
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            import json

            set_clauses = []
            params = []

            if "display_settings" in preferences:
                set_clauses.append(sql.SQL("display_settings = display_settings || %s::jsonb"))
                params.append(json.dumps(preferences["display_settings"]))
            if "notification_settings" in preferences:
                set_clauses.append(sql.SQL("notification_settings = notification_settings || %s::jsonb"))
                params.append(json.dumps(preferences["notification_settings"]))
            if "trading_settings" in preferences:
                set_clauses.append(sql.SQL("trading_settings = trading_settings || %s::jsonb"))
                params.append(json.dumps(preferences["trading_settings"]))

            if not set_clauses:
                return False

            set_clauses.append(sql.SQL("updated_at = CURRENT_TIMESTAMP"))
            params.append(user_id)

            upsert_sql = sql.SQL(
                """
                INSERT INTO user_preferences
                (user_id, display_settings, notification_settings, trading_settings, updated_at)
                VALUES (%s, '{{}}'::jsonb, '{{}}'::jsonb, '{{}}'::jsonb, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET {set_clauses}
                """
            ).format(set_clauses=sql.SQL(", ").join(set_clauses))

            insert_params = [user_id] + params
            cursor.execute(upsert_sql, tuple(insert_params))

            conn.commit()
            cursor.close()
            self.pg_access._return_connection(conn)
            logger.info("更新用户偏好成功: user_id=%s", user_id)
            return True

        except Exception as e:
            conn.rollback()
            logger.error("更新用户偏好失败: %s", e)
            raise
