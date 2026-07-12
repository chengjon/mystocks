"""自选股分组查询与视图方法。
"""

from datetime import date, datetime
from typing import Dict, List

import psycopg2
from psycopg2.extras import RealDictCursor


def _serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    return obj


def _serialize_row(row: dict) -> dict:
    return {key: _serialize_datetime(value) for key, value in row.items()}


class WatchlistGroupQueriesMixin:
    """自选股分组查询相关方法集。"""

    def get_user_groups(self, user_id: int) -> List[Dict]:
        """获取用户的所有分组

        Args:
            user_id: 用户ID

        Returns:
            List[Dict]: 分组列表

        """
        try:
            with self._get_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
                select_sql = """
                    SELECT id, group_name, created_at,
                           (SELECT COUNT(*) FROM user_watchlist WHERE group_id = watchlist_groups.id) as stock_count
                    FROM watchlist_groups
                    WHERE user_id = %s
                    ORDER BY sort_order, id
                    """
                cur.execute(select_sql, (user_id,))
                rows = cur.fetchall()
                return [_serialize_row(dict(row)) for row in rows]
        except psycopg2.Error as error:
            self._log_database_error("获取用户分组时发生错误", error)
            return []

    def get_watchlist_by_group(self, user_id: int, group_id: int) -> List[Dict]:
        """获取指定分组的自选股列表

        Args:
            user_id: 用户ID
            group_id: 分组ID

        Returns:
            List[Dict]: 自选股列表

        """
        try:
            with self._get_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
                select_sql = """
                    SELECT
                        id, stock_code, stock_name,
                        added_at, notes
                    FROM user_watchlist
                    WHERE user_id = %s AND group_id = %s
                    ORDER BY added_at DESC
                    """
                cur.execute(select_sql, (user_id, group_id))
                rows = cur.fetchall()
                return [_serialize_row(dict(row)) for row in rows]
        except psycopg2.Error as error:
            self._log_database_error("获取分组自选股时发生错误", error)
            return []

    def move_stock_to_group(self, user_id: int, symbol: str, from_group_id: int, to_group_id: int) -> bool:
        """将股票从一个分组移动到另一个分组

        Args:
            user_id: 用户ID
            symbol: 股票代码
            from_group_id: 原分组ID
            to_group_id: 目标分组ID

        Returns:
            bool: 移动是否成功

        """
        stock_code = symbol
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT 1 FROM watchlist_groups
                        WHERE id = %s AND user_id = %s
                    """,
                        (to_group_id, user_id),
                    )

                    if not cur.fetchone():
                        self._log_warning("目标分组 %s 不存在", to_group_id)
                        return False

                    update_sql = """
                    UPDATE user_watchlist
                    SET group_id = %s
                    WHERE user_id = %s AND stock_code = %s AND group_id = %s
                    """
                    cur.execute(update_sql, (to_group_id, user_id, stock_code, from_group_id))
                    updated_count = cur.rowcount
                conn.commit()
                return updated_count > 0
        except psycopg2.Error as error:
            self._log_database_error("移动股票时发生错误", error)
            return False

    def get_watchlist_with_groups(self, user_id: int) -> Dict:
        """获取用户的所有分组及其自选股（分组视图）

        Args:
            user_id: 用户ID

        Returns:
            Dict: 包含所有分组和自选股的字典

        """
        try:
            groups = self.get_user_groups(user_id)
            result = {"groups": []}

            for group in groups:
                group_data = {
                    "id": group["id"],
                    "name": group["group_name"],
                    "stock_count": group["stock_count"],
                    "created_at": group["created_at"],
                    "sort_order": group["sort_order"],
                    "stocks": self.get_watchlist_by_group(user_id, group["id"]),
                }
                result["groups"].append(group_data)

            return result
        except Exception as error:
            self._log_database_error("获取分组视图时发生错误", error)
            return {"groups": []}
