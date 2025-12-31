"""
TDengine Cache Manager - 时序数据库缓存管理
Task 2.1: TDengine 缓存集成 - 搭建 TDengine 服务
Phase 3 Task 19: 集成连接池优化

实现 TDengine 连接管理、表创建、数据读写等基础功能。

Features:
- TDengine 连接池管理（Phase 3优化：连接复用、健康检查、监控）
- 自动表创建和初始化
- 缓存数据读写接口
- 连接健康检查
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import structlog

# 支持从脚本导入：尝试相对导入
try:
    from app.core.tdengine_pool import TDengineConnectionPool
except (ImportError, ModuleNotFoundError):
    # 作为备选方案，如果失败则尝试从当前目录导入
    from .tdengine_pool import TDengineConnectionPool

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
        min_pool_size: int = 5,
        max_pool_size: int = 20,
    ):
        """
        初始化 TDengine 管理器（Phase 3优化：连接池支持）

        Args:
            host: TDengine 服务器地址
            port: TDengine 服务器端口
            user: 数据库用户名
            password: 数据库密码
            database: 缓存数据库名
            precision: 时间精度 (ms/us/ns)
            min_pool_size: 最小连接池大小（Phase 3新增）
            max_pool_size: 最大连接池大小（Phase 3新增）
        """
        self.host = host or os.getenv("TDENGINE_HOST", "127.0.0.1")
        self.port = port or int(os.getenv("TDENGINE_PORT", "6030"))
        self.user = user or os.getenv("TDENGINE_USER", "root")
        self.password = password or os.getenv("TDENGINE_PASSWORD", "taosdata")
        self.database = database or os.getenv("TDENGINE_DATABASE", "mystocks_cache")
        self.precision = precision

        # Phase 3: 连接池替代单连接
        self._pool: Optional[TDengineConnectionPool] = None
        self._is_initialized = False

        # 连接池配置
        self._min_pool_size = min_pool_size
        self._max_pool_size = max_pool_size

        logger.info(
            "🔧 初始化 TDengine 管理器（Phase 3连接池优化）",
            host=self.host,
            port=self.port,
            database=self.database,
            pool_size=f"{min_pool_size}-{max_pool_size}",
        )

    def connect(self) -> bool:
        """
        初始化 TDengine 连接池（Phase 3优化）

        Returns:
            True if connection pool initialization successful
        """
        try:
            # Phase 3: 创建连接池替代单连接
            self._pool = TDengineConnectionPool(
                host=self.host or "localhost",
                port=self.port,
                user=self.user,
                password=self.password,
                database=None,  # 初始不指定数据库，在initialize中切换
                min_size=self._min_pool_size,
                max_size=self._max_pool_size,
                max_idle_time=600,  # 10分钟空闲超时
                health_check_interval=60,  # 60秒健康检查间隔
            )
            logger.info(
                "✅ TDengine连接池已初始化",
                host=self.host,
                pool_size=f"{self._min_pool_size}-{self._max_pool_size}",
            )
            return True

        except Exception as e:
            logger.error("❌ 初始化TDengine连接池失败", error=str(e))
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

            # 标记为已初始化（这样后续的_execute会执行USE语句）
            self._is_initialized = True

            # 创建缓存表
            self._create_cache_tables()

            logger.info("✅ TDengine 数据库初始化完成", database=self.database)
            return True

        except Exception as e:
            logger.error("❌ 数据库初始化失败", error=str(e))
            self._is_initialized = False  # 初始化失败则重置状态
            return False

    def _create_database(self):
        """创建缓存数据库"""
        try:
            # TDengine 3.x compatible syntax (simplified)
            self._execute(
                f"CREATE DATABASE IF NOT EXISTS {self.database} "
                f"KEEP 3650 "  # Keep data for 10 years
                f"PRECISION 'ms'"  # Millisecond precision
            )
            logger.info("✅ 数据库已创建", database=self.database)
        except Exception as e:
            logger.error("❌ 创建数据库失败", error=str(e))
            raise

    def _create_cache_tables(self):
        """创建缓存表 (TDengine 3.x compatible)"""
        try:
            # 创建市场数据缓存超表 (stable)
            self._execute(
                """
                CREATE STABLE IF NOT EXISTS market_data_cache (
                    ts TIMESTAMP,
                    data NCHAR(1024),
                    hit_count BIGINT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                ) TAGS (
                    symbol VARCHAR(10),
                    data_type VARCHAR(20),
                    timeframe VARCHAR(10)
                )
            """
            )
            logger.info("✅ 缓存超表已创建: market_data_cache")

            # 创建缓存统计表 (普通表)
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

            # 创建热点数据超表
            self._execute(
                """
                CREATE STABLE IF NOT EXISTS hot_symbols (
                    ts TIMESTAMP,
                    access_count BIGINT,
                    last_access TIMESTAMP
                ) TAGS (symbol VARCHAR(10))
            """
            )
            logger.info("✅ 热点超表已创建: hot_symbols")

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
        写入缓存数据 (自动创建子表)

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

            # 生成子表名
            table_name = f"cache_{symbol}_{data_type.lower().replace('-', '_')}"

            # TDengine 3.x: 使用 USING 语法自动创建子表
            sql = f"""
                INSERT INTO {table_name} USING market_data_cache TAGS ('{symbol}', '{data_type}', '{timeframe}')
                VALUES (
                    '{ts.isoformat()}',
                    '{data_json}',
                    0,
                    '{datetime.utcnow().isoformat()}',
                    '{datetime.utcnow().isoformat()}'
                )
            """

            self._execute(sql)
            logger.debug("✅ 数据已写入", symbol=symbol, data_type=data_type)
            return True

        except Exception as e:
            logger.error("❌ 写入缓存失败", symbol=symbol, data_type=data_type, error=str(e))
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

                logger.debug("✅ 读取缓存成功", symbol=symbol, data_type=data_type)
                return data
            else:
                logger.debug("⚠️ 缓存不存在", symbol=symbol, data_type=data_type)
                return None

        except Exception as e:
            logger.error("❌ 读取缓存失败", symbol=symbol, data_type=data_type, error=str(e))
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
        健康检查（Phase 3优化：检查连接池状态）

        Returns:
            True if health check passed
        """
        try:
            if not self._pool:
                return self.connect()

            # Phase 3: 从连接池获取连接进行健康检查
            with self._pool.get_connection_context(timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT SERVER_VERSION()")
                cursor.close()

            # 记录连接池统计信息
            stats = self._pool.get_stats()
            logger.debug(
                "✅ 健康检查通过",
                pool_size=stats.get("pool_size"),
                active=stats.get("active_connections"),
                idle=stats.get("idle_connections"),
            )
            return True

        except Exception as e:
            logger.warning("⚠️ 健康检查失败", error=str(e))
            return False

    def _execute(self, sql: str) -> bool:
        """
        执行 SQL 语句（Phase 3优化：使用连接池）
        """
        if not self._pool:
            raise RuntimeError("连接池未初始化")

        try:
            # Phase 3: 从连接池获取连接
            with self._pool.get_connection_context() as conn:
                cursor = conn.cursor()

                # 如果SQL不是CREATE DATABASE，需要先USE数据库
                if self._is_initialized and not sql.upper().startswith("CREATE DATABASE"):
                    cursor.execute(f"USE {self.database}")

                cursor.execute(sql)
                cursor.close()
            return True
        except Exception as e:
            logger.error("❌ SQL 执行失败", sql=sql, error=str(e))
            raise

    def _execute_query(self, sql: str) -> Optional[List[Tuple]]:
        """
        执行查询 SQL（Phase 3优化：使用连接池）
        """
        if not self._pool:
            raise RuntimeError("连接池未初始化")

        try:
            # Phase 3: 从连接池获取连接
            with self._pool.get_connection_context() as conn:
                cursor = conn.cursor()

                # 确保选择了正确的数据库
                if self._is_initialized:
                    cursor.execute(f"USE {self.database}")

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
        """
        关闭连接池（Phase 3优化：关闭所有连接）
        """
        if self._pool:
            self._pool.close_all()
            self._pool = None
            logger.info("✅ TDengine 连接池已关闭")
            self._is_initialized = False

    def get_pool_stats(self) -> Optional[Dict[str, Any]]:
        """
        获取连接池统计信息（Phase 3新增）

        Returns:
            连接池统计字典，包含活跃连接数、空闲连接数、请求次数等
        """
        if not self._pool:
            return None

        return self._pool.get_stats()


# 全局单例
_tdengine_manager: Optional[TDengineManager] = None


def get_tdengine_manager() -> Optional[TDengineManager]:
    """获取 TDengine 管理器单例 (快速失败版本)"""
    global _tdengine_manager

    if _tdengine_manager is None:
        # 检查环境变量，如果禁用了TDengine，快速返回None
        import os

        if os.getenv("TDENGINE_DISABLED", "false").lower() == "true":
            logger.warning("⚠️ TDengine已禁用 (TDENGINE_DISABLED=true)")
            return None

        _tdengine_manager = TDengineManager()

        # 只尝试一次初始化，不进行重试
        try:
            if not _tdengine_manager.initialize():
                logger.warning("⚠️ TDengine初始化失败 - 系统将在无TDengine模式下运行")
                _tdengine_manager = None
        except Exception as e:
            logger.error(f"❌ TDengine初始化异常: {e} - 系统将在无TDengine模式下运行")
            _tdengine_manager = None

    return _tdengine_manager


def reset_tdengine_manager():
    """重置 TDengine 管理器（用于测试）"""
    global _tdengine_manager
    if _tdengine_manager:
        _tdengine_manager.close()
    _tdengine_manager = None
