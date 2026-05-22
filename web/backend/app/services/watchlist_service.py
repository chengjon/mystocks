"""
自选股管理服务模块
基于 PostgreSQL 实现用户自选股列表的管理功能
迁移自 OpenStock 项目，适配 PostgreSQL 数据库
"""

import logging
import os
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import Request
import psycopg2
from psycopg2.extras import RealDictCursor

from web.backend.app.services._watchlist_group_queries import WatchlistGroupQueriesMixin

logger = logging.getLogger(__name__)


class WatchlistError(Exception):
    """自选股操作错误"""


def serialize_datetime(obj):
    """
    将datetime和date对象转换为ISO格式字符串

    Args:
        obj: 任意对象

    Returns:
        如果是datetime或date对象，返回ISO格式字符串；否则返回原对象
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    return obj


def serialize_row(row: dict) -> dict:
    """
    序列化数据库行，转换所有datetime对象为ISO格式字符串

    Args:
        row: 数据库查询结果行（字典）

    Returns:
        序列化后的字典
    """
    return {key: serialize_datetime(value) for key, value in row.items()}


class WatchlistService(WatchlistGroupQueriesMixin):
    """自选股管理服务"""

    @staticmethod
    def _log_database_error(action: str, error: Exception) -> None:
        logger.exception("%s: %s", action, error)

    @staticmethod
    def _log_warning(message: str, *args) -> None:
        logger.warning(message, *args)

    def __init__(self, db_config: Dict[str, str] = None):
        """
        初始化自选股管理服务

        Args:
            db_config: 数据库配置，如果未提供则从环境变量读取
        """
        if db_config:
            self.db_config = db_config
        else:
            self.db_config = {
                "host": os.getenv("POSTGRESQL_HOST", "localhost"),
                "port": int(os.getenv("POSTGRESQL_PORT", 5432)),
                "database": os.getenv("POSTGRESQL_DATABASE", "mystocks"),
                "user": os.getenv("POSTGRESQL_USER", "postgres"),
                "password": os.getenv("POSTGRESQL_PASSWORD", ""),
            }

        self._ensure_table_exists()

    def _get_connection(self):
        """
        获取数据库连接

        Returns:
            Connection: 数据库连接对象
        """
        try:
            return psycopg2.connect(**self.db_config)
        except psycopg2.Error as e:
            raise WatchlistError(f"数据库连接失败: {e}")

    def _ensure_table_exists(self):
        """确保自选股表和分组表存在"""
        create_table_sql = """
        -- 创建自选股分组表
        CREATE TABLE IF NOT EXISTS watchlist_groups (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            group_name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(user_id, group_name)
        );

        CREATE INDEX IF NOT EXISTS idx_groups_user_id ON watchlist_groups(user_id);

        -- 创建自选股表（带分组支持）
        CREATE TABLE IF NOT EXISTS user_watchlist (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            group_id INTEGER REFERENCES watchlist_groups(id) ON DELETE CASCADE,
            stock_code VARCHAR(20) NOT NULL,
            stock_name VARCHAR(100),


            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,

            UNIQUE(user_id, group_id, stock_code)
        );

        CREATE INDEX IF NOT EXISTS idx_watchlist_user_id ON user_watchlist(user_id);
        CREATE INDEX IF NOT EXISTS idx_watchlist_group_id ON user_watchlist(group_id);
        CREATE INDEX IF NOT EXISTS idx_watchlist_stock_code ON user_watchlist(stock_code);

        -- 为每个用户创建默认分组（如果不存在）
        INSERT INTO watchlist_groups (user_id, group_name)
        SELECT DISTINCT user_id, '默认分组'
        FROM user_watchlist
        WHERE user_id NOT IN (
            SELECT user_id FROM watchlist_groups WHERE group_name = '默认分组'
        )
        ON CONFLICT DO NOTHING;
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_table_sql)
                conn.commit()
        except psycopg2.Error as e:
            logger.warning("创建自选股表时警告: %s", e, exc_info=True)

    def add_to_watchlist(
        self,
        user_id: int,
        symbol: str,
        display_name: str = None,
        exchange: str = None,
        market: str = None,
        notes: str = None,
        group_id: int = None,
    ) -> bool:
        """
        添加股票到自选股列表

        Args:
            user_id: 用户ID
            symbol: 股票代码 (映射到 stock_code)
            display_name: 显示名称 (映射到 stock_name)
            exchange: 交易所 (已弃用，保留参数以兼容)
            market: 市场 (已弃用，保留参数以兼容)
            notes: 备注
            group_id: 分组ID，如果为None则添加到默认分组

        Returns:
            bool: 添加是否成功
        """
        # 参数映射：保持API兼容性
        stock_code = symbol
        stock_name = display_name

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # 如果未指定分组，获取或创建默认分组
                    if group_id is None:
                        cur.execute(
                            """
                            INSERT INTO watchlist_groups (user_id, group_name)
                            VALUES (%s, '默认分组')
                            ON CONFLICT (user_id, group_name) DO NOTHING
                            RETURNING id
                        """,
                            (user_id,),
                        )
                        result = cur.fetchone()

                        if result:
                            group_id = result[0]
                        else:
                            # 如果已存在，获取其ID
                            cur.execute(
                                """
                                SELECT id FROM watchlist_groups
                                WHERE user_id = %s AND group_name = '默认分组'
                            """,
                                (user_id,),
                            )
                            group_id = cur.fetchone()[0]

                    # 添加自选股
                    insert_sql = """
                    INSERT INTO user_watchlist
                    (user_id, group_id, stock_code, stock_name, notes, added_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, group_id, stock_code)
                    DO UPDATE SET
                        stock_name = EXCLUDED.stock_name,
                        notes = EXCLUDED.notes,
                        added_at = EXCLUDED.added_at
                    """
                    cur.execute(
                        insert_sql,
                        (
                            user_id,
                            group_id,
                            stock_code,
                            stock_name,
                            notes,
                            datetime.now(),
                        ),
                    )
                conn.commit()
                return True
        except psycopg2.Error as e:
            self._log_database_error("添加自选股时发生错误", e)
            return False

    def remove_from_watchlist(self, user_id: int, symbol: str) -> bool:
        """
        从自选股列表中删除股票

        Args:
            user_id: 用户ID
            symbol: 股票代码

        Returns:
            bool: 删除是否成功
        """
        stock_code = symbol  # 参数映射
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    delete_sql = """
                    DELETE FROM user_watchlist
                    WHERE user_id = %s AND stock_code = %s
                    """
                    cur.execute(delete_sql, (user_id, stock_code))
                    deleted_count = cur.rowcount
                conn.commit()
                return deleted_count > 0
        except psycopg2.Error as e:
            self._log_database_error("删除自选股时发生错误", e)
            return False

    def get_user_watchlist(self, user_id: int) -> List[Dict]:
        """
        获取用户的自选股列表

        Args:
            user_id: 用户ID

        Returns:
            List[Dict]: 自选股列表，每个元素包含股票信息
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    select_sql = """
                    SELECT
                        id, stock_code, stock_name,
                        added_at, notes
                    FROM user_watchlist
                    WHERE user_id = %s
                    ORDER BY added_at DESC
                    """
                    cur.execute(select_sql, (user_id,))
                    rows = cur.fetchall()

                    # 转换为列表，并序列化datetime对象
                    return [serialize_row(dict(row)) for row in rows]
        except psycopg2.Error as e:
            self._log_database_error("获取自选股列表时发生错误", e)
            return []

    def get_watchlist_symbols(self, user_id: int) -> List[str]:
        """
        获取用户的自选股代码列表

        Args:
            user_id: 用户ID

        Returns:
            List[str]: 股票代码列表
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    select_sql = """
                    SELECT stock_code
                    FROM user_watchlist
                    WHERE user_id = %s
                    ORDER BY added_at DESC
                    """
                    cur.execute(select_sql, (user_id,))
                    rows = cur.fetchall()
                    return [row[0] for row in rows]
        except psycopg2.Error as e:
            self._log_database_error("获取自选股代码列表时发生错误", e)
            return []

    def is_in_watchlist(self, user_id: int, symbol: str) -> bool:
        """
        检查股票是否在用户的自选股列表中

        Args:
            user_id: 用户ID
            symbol: 股票代码

        Returns:
            bool: 是否在自选股列表中
        """
        stock_code = symbol  # 参数映射
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    select_sql = """
                    SELECT 1 FROM user_watchlist
                    WHERE user_id = %s AND stock_code = %s
                    LIMIT 1
                    """
                    cur.execute(select_sql, (user_id, stock_code))
                    return cur.fetchone() is not None
        except psycopg2.Error as e:
            self._log_database_error("检查自选股时发生错误", e)
            return False

    def update_watchlist_notes(self, user_id: int, symbol: str, notes: str) -> bool:
        """
        更新自选股备注

        Args:
            user_id: 用户ID
            symbol: 股票代码
            notes: 备注内容

        Returns:
            bool: 更新是否成功
        """
        stock_code = symbol  # 参数映射
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    update_sql = """
                    UPDATE user_watchlist
                    SET notes = %s
                    WHERE user_id = %s AND stock_code = %s
                    """
                    cur.execute(update_sql, (notes, user_id, stock_code))
                    updated_count = cur.rowcount
                conn.commit()
                return updated_count > 0
        except psycopg2.Error as e:
            self._log_database_error("更新自选股备注时发生错误", e)
            return False

    def get_watchlist_count(self, user_id: int) -> int:
        """
        获取用户自选股数量

        Args:
            user_id: 用户ID

        Returns:
            int: 自选股数量
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    select_sql = """
                    SELECT COUNT(*) FROM user_watchlist
                    WHERE user_id = %s
                    """
                    cur.execute(select_sql, (user_id,))
                    result = cur.fetchone()
                    return result[0] if result else 0
        except psycopg2.Error as e:
            self._log_database_error("获取自选股数量时发生错误", e)
            return 0

    def clear_watchlist(self, user_id: int) -> bool:
        """
        清空用户的自选股列表

        Args:
            user_id: 用户ID

        Returns:
            bool: 清空是否成功
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    delete_sql = """
                    DELETE FROM user_watchlist
                    WHERE user_id = %s
                    """
                    cur.execute(delete_sql, (user_id,))
                conn.commit()
                return True
        except psycopg2.Error as e:
            self._log_database_error("清空自选股列表时发生错误", e)
            return False

    # ========== 分组管理功能 ==========

    def get_or_create_group(self, user_id: int, group_name: str) -> Optional[Dict]:
        """
        获取或创建分组（如果分组不存在则自动创建）

        Args:
            user_id: 用户ID
            group_name: 分组名称

        Returns:
            Optional[Dict]: 分组信息
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # 先尝试获取现有分组
                    cur.execute(
                        """
                        SELECT id, group_name, created_at
                        FROM watchlist_groups
                        WHERE user_id = %s AND group_name = %s
                    """,
                        (user_id, group_name),
                    )

                    result = cur.fetchone()
                    if result:
                        return serialize_row(dict(result))

                    # 如果不存在，创建新分组
                    cur.execute(
                        """
                        SELECT COALESCE(MAX(sort_order), -1) + 1 as next_order
                        FROM watchlist_groups
                        WHERE user_id = %s
                    """,
                        (user_id,),
                    )
                    next_order = cur.fetchone()["next_order"]

                    insert_sql = """
                    INSERT INTO watchlist_groups (user_id, group_name)
                    VALUES (%s, %s, %s)
                    RETURNING id, group_name, created_at
                    """
                    cur.execute(insert_sql, (user_id, group_name, next_order))
                    result = cur.fetchone()
                conn.commit()
                return serialize_row(dict(result)) if result else None
        except psycopg2.Error as e:
            raise WatchlistError(f"获取或创建分组失败: {str(e)}")

    def create_group(self, user_id: int, group_name: str) -> Optional[Dict]:
        """
        创建新分组

        Args:
            user_id: 用户ID
            group_name: 分组名称

        Returns:
            Optional[Dict]: 创建的分组信息，失败返回None

        Raises:
            WatchlistError: 当分组名称已存在或其他错误时抛出
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # 先检查分组是否已存在
                    cur.execute(
                        """
                        SELECT id FROM watchlist_groups
                        WHERE user_id = %s AND group_name = %s
                    """,
                        (user_id, group_name),
                    )

                    if cur.fetchone():
                        raise WatchlistError(f"分组名称 '{group_name}' 已存在")

                    # 获取当前最大排序号
                    cur.execute(
                        """
                        SELECT COALESCE(MAX(sort_order), -1) + 1 as next_order
                        FROM watchlist_groups
                        WHERE user_id = %s
                    """,
                        (user_id,),
                    )
                    next_order = cur.fetchone()["next_order"]

                    # 插入新分组
                    insert_sql = """
                    INSERT INTO watchlist_groups (user_id, group_name)
                    VALUES (%s, %s, %s)
                    RETURNING id, group_name, created_at
                    """
                    cur.execute(insert_sql, (user_id, group_name, next_order))
                    result = cur.fetchone()
                conn.commit()
                return serialize_row(dict(result)) if result else None
        except WatchlistError:
            raise  # 重新抛出自定义异常
        except psycopg2.IntegrityError as e:
            # UNIQUE 约束冲突
            if "unique" in str(e).lower():
                raise WatchlistError(f"分组名称 '{group_name}' 已存在")
            raise WatchlistError(f"数据库完整性错误: {str(e)}")
        except psycopg2.Error as e:
            raise WatchlistError(f"创建分组失败: {str(e)}")

    def update_group(self, user_id: int, group_id: int, group_name: str) -> bool:
        """
        更新分组名称

        Args:
            user_id: 用户ID
            group_id: 分组ID
            group_name: 新的分组名称

        Returns:
            bool: 更新是否成功
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    update_sql = """
                    UPDATE watchlist_groups
                    SET group_name = %s
                    WHERE id = %s AND user_id = %s
                    """
                    cur.execute(update_sql, (group_name, group_id, user_id))
                    updated_count = cur.rowcount
                conn.commit()
                return updated_count > 0
        except psycopg2.Error as e:
            self._log_database_error("更新分组时发生错误", e)
            return False

    def delete_group(self, user_id: int, group_id: int) -> bool:
        """
        删除分组（CASCADE会自动删除该分组下的所有自选股）

        Args:
            user_id: 用户ID
            group_id: 分组ID

        Returns:
            bool: 删除是否成功
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # 检查是否为默认分组
                    cur.execute(
                        """
                        SELECT group_name FROM watchlist_groups
                        WHERE id = %s AND user_id = %s
                    """,
                        (group_id, user_id),
                    )
                    result = cur.fetchone()

                    if not result:
                        return False

                    if result[0] == "默认分组":
                        self._log_warning("不能删除默认分组")
                        return False

                    # 删除分组
                    delete_sql = """
                    DELETE FROM watchlist_groups
                    WHERE id = %s AND user_id = %s
                    """
                    cur.execute(delete_sql, (group_id, user_id))
                    deleted_count = cur.rowcount
                conn.commit()
                return deleted_count > 0
        except psycopg2.Error as e:
            self._log_database_error("删除分组时发生错误", e)
            return False


# 创建全局实例
_watchlist_service = None
WATCHLIST_SERVICE_STATE_KEY = "watchlist_service"


def get_watchlist_service() -> WatchlistService:
    """
    获取自选股服务实例（单例模式）

    Returns:
        WatchlistService: 自选股服务实例
    """
    global _watchlist_service
    if _watchlist_service is None:
        _watchlist_service = WatchlistService()
    return _watchlist_service


def install_watchlist_service(app: Any, service: WatchlistService | None = None) -> WatchlistService:
    selected_service = service if service is not None else get_watchlist_service()
    setattr(app.state, WATCHLIST_SERVICE_STATE_KEY, selected_service)
    return selected_service


def get_watchlist_service_dependency(request: Request) -> WatchlistService:
    service = getattr(request.app.state, WATCHLIST_SERVICE_STATE_KEY, None)
    if service is None:
        service = install_watchlist_service(request.app)
    return service
