"""
TDengine Cache Manager - 时序数据库缓存管理
Task 2.1: TDengine 缓存集成 - 搭建 TDengine 服务

实现 TDengine 连接管理、表创建、数据读写等基础功能。

Features:
- TDengine 连接池管理
- 自动表创建和初始化
- 缓存数据读写接口
- 连接健康检查
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import structlog
from taos import connect
from taos.error import ProgrammingError

logger = structlog.get_logger()


class TDengineManager:
    """
    TDengine 时序数据库管理器

    负责：
    - 数据库连接管理
    - 缓存表创建和管理
    - 缓存数据读写操作
    - 连接健康检查

    Usage:
        ```python
        tdengine = TDengineManager()

        # 初始化数据库
        tdengine.initialize()

        # 写入缓存数据
        tdengine.write_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"main_net_inflow": 1000000}
        )

        # 读取缓存数据
        data = tdengine.read_cache(
            symbol="000001",
            data_type="fund_flow"
        )
        ```
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 6030,
        user: str = "root",
        password: str = "taosdata",
        database: str = "mystocks_cache",
        precision: str = "ms",
    ):
        """
        初始化 TDengine 管理器

        Args:
            host: TDengine 服务器地址
            port: TDengine 服务器端口
            user: 数据库用户名
            password: 数据库密码
            database: 缓存数据库名
            precision: 时间精度 (ms/us/ns)
        """
        self.host = host or os.getenv("TDENGINE_HOST", "127.0.0.1")
        self.port = port or int(os.getenv("TDENGINE_PORT", "6030"))
        self.user = user or os.getenv("TDENGINE_USER", "root")
        self.password = password or os.getenv("TDENGINE_PASSWORD", "taosdata")
        self.database = database or os.getenv("TDENGINE_DATABASE", "mystocks_cache")
        self.precision = precision

        self._conn = None
        self._is_initialized = False

        logger.info(
            "🔧 初始化 TDengine 管理器",
            host=self.host,
            port=self.port,
            database=self.database,
        )

    def connect(self) -> bool:
        """
        连接到 TDengine 服务器

        Returns:
            True if connection successful
        """
        try:
            self._conn = connect(
                host=self.host, port=self.port, user=self.user, password=self.password
            )
            logger.info("✅ 已连接到 TDengine", host=self.host)
            return True

        except Exception as e:
            logger.error("❌ 连接 TDengine 失败", error=str(e))
            return False

    def initialize(self) -> bool:
        """
        初始化数据库和表结构

        Returns:
            True if initialization successful
        """
        if not self.connect():
            return False

        try:
            # 创建数据库
            self._create_database()

            # 切换到目标数据库
            self._execute(f"USE {self.database}")

            # 创建缓存表
            self._create_cache_tables()

            self._is_initialized = True
            logger.info("✅ TDengine 数据库初始化完成", database=self.database)
            return True

        except Exception as e:
            logger.error("❌ 数据库初始化失败", error=str(e))
            return False

    def _create_database(self):
        """创建缓存数据库"""
        try:
            self._execute(
                f"CREATE DATABASE IF NOT EXISTS {self.database} "
                f"KEEP 2147483647 BUFFER 256 PAGES 256 MINROWS 100 MAXROWS 4096 "
                f"FSYNC 3000 COMP 2 PRECISION 'ms' REPLICATIONS 1 STRICT OFF"
            )
            logger.info("✅ 数据库已创建", database=self.database)
        except Exception as e:
            logger.error("❌ 创建数据库失败", error=str(e))
            raise

    def _create_cache_tables(self):
        """创建缓存表"""
        try:
            # 创建市场数据缓存超表
            self._execute(
                """
                CREATE TABLE IF NOT EXISTS market_data_cache (
                    ts TIMESTAMP,
                    symbol VARCHAR(10),
                    data_type VARCHAR(20),
                    timeframe VARCHAR(10),
                    data NCHAR(1024),
                    hit_count BIGINT DEFAULT 0,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                ) TAGS (symbol VARCHAR(10), data_type VARCHAR(20))
            """
            )
            logger.info("✅ 缓存表已创建: market_data_cache")

            # 创建缓存统计表
            self._execute(
                """
                CREATE TABLE IF NOT EXISTS cache_stats (
                    ts TIMESTAMP,
                    total_requests BIGINT,
                    cache_hits BIGINT,
                    cache_misses BIGINT,
                    hit_rate FLOAT
                )
            """
            )
            logger.info("✅ 统计表已创建: cache_stats")

            # 创建热点数据表
            self._execute(
                """
                CREATE TABLE IF NOT EXISTS hot_symbols (
                    ts TIMESTAMP,
                    symbol VARCHAR(10),
                    access_count BIGINT,
                    last_access TIMESTAMP
                ) TAGS (symbol VARCHAR(10))
            """
            )
            logger.info("✅ 热点表已创建: hot_symbols")

        except Exception as e:
            logger.error("❌ 创建表失败", error=str(e))
            raise

    def write_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        写入缓存数据

        Args:
            symbol: 股票代码
            data_type: 数据类型 (fund_flow, etf, chip_race, etc.)
            timeframe: 时间维度 (1d, 3d, 5d, 10d)
            data: 数据字典
            timestamp: 时间戳 (默认当前时间)

        Returns:
            True if write successful
        """
        if not self._is_initialized:
            logger.warning("❌ 数据库未初始化")
            return False

        try:
            ts = timestamp or datetime.utcnow()
            data_json = json.dumps(data, ensure_ascii=False)

            # 生成表名 (用于子表)
            table_name = f"cache_{symbol}_{data_type.lower()}"

            # 使用 INSERT 插入数据
            sql = f"""
                INSERT INTO {table_name} VALUES (
                    '{ts.isoformat()}',
                    '{symbol}',
                    '{data_type}',
                    '{timeframe}',
                    '{data_json}',
                    0,
                    '{datetime.utcnow().isoformat()}',
                    '{datetime.utcnow().isoformat()}'
                ) TAGS ('{symbol}', '{data_type}')
            """

            self._execute(sql)
            logger.debug(f"✅ 数据已写入", symbol=symbol, data_type=data_type)
            return True

        except Exception as e:
            logger.error(
                "❌ 写入缓存失败", symbol=symbol, data_type=data_type, error=str(e)
            )
            return False

    def read_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: Optional[str] = None,
        days: int = 1,
    ) -> Optional[Dict[str, Any]]:
        """
        读取缓存数据

        Args:
            symbol: 股票代码
            data_type: 数据类型
            timeframe: 时间维度 (可选)
            days: 回溯天数

        Returns:
            缓存数据字典，如果不存在返回 None
        """
        if not self._is_initialized:
            logger.warning("❌ 数据库未初始化")
            return None

        try:
            # 生成查询 SQL
            where_clause = f"symbol = '{symbol}' AND data_type = '{data_type}'"

            if timeframe:
                where_clause += f" AND timeframe = '{timeframe}'"

            # 添加时间范围条件
            start_time = (datetime.utcnow() - timedelta(days=days)).isoformat()
            where_clause += f" AND ts >= '{start_time}'"

            sql = f"""
                SELECT data, updated_at
                FROM market_data_cache
                WHERE {where_clause}
                ORDER BY ts DESC
                LIMIT 1
            """

            result = self._execute_query(sql)

            if result and len(result) > 0:
                data_str, updated_at = result[0]
                data = json.loads(data_str)

                # 更新命中次数
                self._update_hit_count(symbol, data_type)

                logger.debug(f"✅ 读取缓存成功", symbol=symbol, data_type=data_type)
                return data
            else:
                logger.debug(f"⚠️ 缓存不存在", symbol=symbol, data_type=data_type)
                return None

        except Exception as e:
            logger.error(
                "❌ 读取缓存失败", symbol=symbol, data_type=data_type, error=str(e)
            )
            return None

    def clear_expired_cache(self, days: int = 7) -> int:
        """
        清理过期缓存（超过指定天数）

        Args:
            days: 保留天数

        Returns:
            删除的记录数
        """
        if not self._is_initialized:
            return 0

        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            sql = f"""
                DELETE FROM market_data_cache
                WHERE ts < '{cutoff_date}'
            """

            self._execute(sql)
            logger.info(f"✅ 已清理过期缓存 (保留 {days} 天)")
            return 1

        except Exception as e:
            logger.error("❌ 清理缓存失败", error=str(e))
            return 0

    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """
        获取缓存统计信息

        Returns:
            缓存统计字典
        """
        if not self._is_initialized:
            return None

        try:
            sql = """
                SELECT COUNT(*) as total_records,
                       COUNT(DISTINCT symbol) as unique_symbols
                FROM market_data_cache
            """

            result = self._execute_query(sql)

            if result:
                total_records, unique_symbols = result[0]
                return {
                    "total_records": total_records,
                    "unique_symbols": unique_symbols,
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error("❌ 获取统计信息失败", error=str(e))

        return None

    def health_check(self) -> bool:
        """
        健康检查

        Returns:
            True if health check passed
        """
        try:
            if not self._conn:
                return self.connect()

            # 执行简单查询测试连接
            self._execute("SELECT DATABASE()")
            logger.debug("✅ 健康检查通过")
            return True

        except Exception as e:
            logger.warning("⚠️ 健康检查失败", error=str(e))
            return False

    def _execute(self, sql: str) -> bool:
        """执行 SQL 语句"""
        try:
            cursor = self._conn.cursor()
            cursor.execute(sql)
            cursor.close()
            return True
        except Exception as e:
            logger.error("❌ SQL 执行失败", sql=sql, error=str(e))
            raise

    def _execute_query(self, sql: str) -> Optional[List[Tuple]]:
        """执行查询 SQL"""
        try:
            cursor = self._conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            logger.error("❌ SQL 查询失败", sql=sql, error=str(e))
            return None

    def _update_hit_count(self, symbol: str, data_type: str):
        """更新命中次数"""
        try:
            sql = f"""
                UPDATE market_data_cache
                SET hit_count = hit_count + 1,
                    updated_at = '{datetime.utcnow().isoformat()}'
                WHERE symbol = '{symbol}' AND data_type = '{data_type}'
            """
            self._execute(sql)
        except Exception as e:
            logger.debug(f"更新命中次数失败: {str(e)}")

    def close(self):
        """关闭数据库连接"""
        if self._conn:
            self._conn.close()
            logger.info("✅ TDengine 连接已关闭")
            self._is_initialized = False


# 全局单例
_tdengine_manager: Optional[TDengineManager] = None


def get_tdengine_manager() -> TDengineManager:
    """获取 TDengine 管理器单例"""
    global _tdengine_manager

    if _tdengine_manager is None:
        _tdengine_manager = TDengineManager()
        if not _tdengine_manager.initialize():
            logger.error("❌ 无法初始化 TDengine 管理器")

    return _tdengine_manager


def reset_tdengine_manager():
    """重置 TDengine 管理器（用于测试）"""
    global _tdengine_manager
    if _tdengine_manager:
        _tdengine_manager.close()
    _tdengine_manager = None
