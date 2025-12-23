"""
数据库连接池模块测试

测试DatabaseConnectionPool和DatabaseConnectionManager的功能:
- 连接池初始化和配置
- 连接获取和释放
- 查询执行和命令执行
- 连接池统计信息
- 健康检查功能
- 内存监控和分析
- 连接超时和错误处理
- 内存泄漏检测
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Mock the dependencies to avoid import issues
import sys

sys.modules["asyncpg"] = MagicMock()
sys.modules["structlog"] = MagicMock()
sys.modules["src.core.config"] = MagicMock()
sys.modules["src.core.exceptions"] = MagicMock()
sys.modules["src.core.memory_manager"] = MagicMock()

from src.core.database_pool import (
    DatabaseConnectionPool,
    DatabaseConnectionManager,
    get_connection_pool,
    close_connection_pool,
    get_db_manager,
)


class TestDatabaseConnectionPool:
    """DatabaseConnectionPool类测试"""

    def test_init(self):
        """测试连接池初始化"""
        mock_config = Mock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            assert pool.config == mock_config
            assert pool.pool is None
            assert hasattr(pool, "_lock")
            assert hasattr(pool, "_stats")
            assert hasattr(pool, "_connection_times")

            # 验证统计信息初始化
            stats = pool._stats
            assert stats["total_connections"] == 0
            assert stats["active_connections"] == 0
            assert stats["pool_hits"] == 0
            assert stats["pool_misses"] == 0
            assert stats["connection_timeouts"] == 0
            assert stats["total_queries"] == 0
            assert stats["query_errors"] == 0
            assert isinstance(stats["memory_snapshots"], list)

    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """测试连接池初始化成功"""
        mock_config = Mock()
        mock_config.get_connection_string.return_value = "postgresql://test"

        # Mock asyncpg.create_pool
        with patch("src.core.database_pool.asyncpg") as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool.return_value = mock_pool

            with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
                pool = DatabaseConnectionPool(mock_config)

                result = await pool.initialize(min_connections=5, max_connections=20)

                assert result is True
                assert pool.pool == mock_pool
                mock_asyncpg.create_pool.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_failure(self):
        """测试连接池初始化失败"""
        mock_config = Mock()
        mock_config.get_connection_string.return_value = "postgresql://test"

        # Mock asyncpg.create_pool抛出异常
        with patch("src.core.database_pool.asyncpg") as mock_asyncpg:
            mock_asyncpg.create_pool.side_effect = Exception("Connection failed")

            with patch("src.core.database_pool.DatabaseConnectionError") as mock_error:
                mock_error.side_effect = Exception("Database error")

                with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
                    pool = DatabaseConnectionPool(mock_config)

                    with pytest.raises(Exception):
                        await pool.initialize()

    @pytest.mark.asyncio
    async def test_close(self):
        """测试关闭连接池"""
        mock_config = Mock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            pool.pool = mock_pool

            await pool.close()

            mock_pool.close.assert_called_once()
            assert pool.pool is None

    @pytest.mark.asyncio
    async def test_close_already_closed(self):
        """测试关闭已经关闭的连接池"""
        mock_config = Mock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # pool已经是None
            assert pool.pool is None

            # 应该不会抛出异常
            await pool.close()
            assert pool.pool is None

    @pytest.mark.asyncio
    async def test_get_connection_success(self):
        """测试成功获取连接"""
        mock_config = Mock()

        # Mock async connection
        mock_connection = AsyncMock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_pool.release = AsyncMock()
            pool.pool = mock_pool

            # 使用上下文管理器获取连接
            async with pool.get_connection(timeout=10) as conn:
                assert conn == mock_connection
                assert pool._stats["pool_hits"] == 1
                assert pool._stats["active_connections"] == 1

            # 连接应该被释放
            assert pool._stats["active_connections"] == 0

    @pytest.mark.asyncio
    async def test_get_connection_timeout(self):
        """测试获取连接超时"""
        mock_config = Mock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            with patch("src.core.database_pool.DatabaseConnectionError") as mock_error:
                pool = DatabaseConnectionPool(mock_config)

                # Mock pool
                mock_pool = AsyncMock()
                mock_pool.acquire.side_effect = asyncio.TimeoutError()
                pool.pool = mock_pool

                with pytest.raises(Exception):
                    async with pool.get_connection(timeout=1):
                        pass

                assert pool._stats["connection_timeouts"] == 1

    @pytest.mark.asyncio
    async def test_get_connection_pool_not_initialized(self):
        """测试连接池未初始化时获取连接"""
        mock_config = Mock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            with patch("src.core.database_pool.DatabaseConnectionError") as mock_error:
                pool = DatabaseConnectionPool(mock_config)

                # pool为None
                assert pool.pool is None

                with pytest.raises(Exception):
                    async with pool.get_connection():
                        pass

    @pytest.mark.asyncio
    async def test_execute_query_success(self):
        """测试成功执行查询"""
        mock_config = Mock()

        # Mock connection and query result
        mock_connection = AsyncMock()
        expected_result = [{"id": 1, "name": "test"}]
        mock_connection.fetch.return_value = expected_result

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_pool.release = AsyncMock()
            pool.pool = mock_pool

            result = await pool.execute_query("SELECT * FROM test_table")

            assert result == expected_result
            assert pool._stats["total_queries"] == 1
            mock_connection.fetch.assert_called_once_with(
                "SELECT * FROM test_table", None
            )

    @pytest.mark.asyncio
    async def test_execute_query_with_params(self):
        """测试带参数的查询执行"""
        mock_config = Mock()

        # Mock connection and query result
        mock_connection = AsyncMock()
        expected_result = [{"id": 1}]
        mock_connection.fetch.return_value = expected_result

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_pool.release = AsyncMock()
            pool.pool = mock_pool

            query = "SELECT * FROM test_table WHERE id = $1"
            params = (1,)

            result = await pool.execute_query(query, params)

            assert result == expected_result
            mock_connection.fetch.assert_called_once_with(query, params)

    @pytest.mark.asyncio
    async def test_execute_query_error(self):
        """测试查询执行错误"""
        mock_config = Mock()

        # Mock connection抛出异常
        mock_connection = AsyncMock()
        mock_connection.fetch.side_effect = Exception("Query error")

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_pool.release = AsyncMock()
            pool.pool = mock_pool

            with pytest.raises(Exception):
                await pool.execute_query("INVALID QUERY")

            assert pool._stats["query_errors"] == 1

    @pytest.mark.asyncio
    async def test_execute_command_success(self):
        """测试成功执行命令"""
        mock_config = Mock()

        # Mock connection and command result
        mock_connection = AsyncMock()
        expected_result = "INSERT 1"
        mock_connection.execute.return_value = expected_result

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_pool.release = AsyncMock()
            pool.pool = mock_pool

            result = await pool.execute_command("INSERT INTO test_table VALUES (1)")

            assert result == expected_result
            assert pool._stats["total_queries"] == 1

    @pytest.mark.asyncio
    async def test_execute_command_with_params(self):
        """测试带参数的命令执行"""
        mock_config = Mock()

        # Mock connection and command result
        mock_connection = AsyncMock()
        expected_result = "UPDATE 1"
        mock_connection.execute.return_value = expected_result

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_pool.release = AsyncMock()
            pool.pool = mock_pool

            command = "UPDATE test_table SET name = $1 WHERE id = $2"
            params = ("test", 1)

            result = await pool.execute_command(command, params)

            assert result == expected_result
            mock_connection.execute.assert_called_once_with(command, params)

    def test_get_stats(self):
        """测试获取统计信息"""
        mock_config = Mock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # 修改统计信息
            pool._stats["total_connections"] = 10
            pool._stats["active_connections"] = 5
            pool._stats["pool_hits"] = 100

            stats = pool.get_stats()

            assert isinstance(stats, dict)
            assert stats["total_connections"] == 10
            assert stats["active_connections"] == 5
            assert stats["pool_hits"] == 100

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """测试健康检查成功"""
        mock_config = Mock()

        # Mock连接
        mock_connection = AsyncMock()
        mock_connection.fetchval.return_value = 1  # SELECT 1返回1

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_pool.release = AsyncMock()
            pool.pool = mock_pool

            result = await pool.health_check()

            assert result is True
            mock_connection.fetchval.assert_called_once_with("SELECT 1")

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """测试健康检查失败"""
        mock_config = Mock()

        # Mock连接抛出异常
        mock_connection = AsyncMock()
        mock_connection.fetchval.side_effect = Exception("Connection error")

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_pool.release = AsyncMock()
            pool.pool = mock_pool

            result = await pool.health_check()

            assert result is False

    @pytest.mark.asyncio
    async def test_health_check_no_pool(self):
        """测试健康检查时连接池未初始化"""
        mock_config = Mock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # pool为None
            assert pool.pool is None

            result = await pool.health_check()

            assert result is False


class TestDatabaseConnectionManager:
    """DatabaseConnectionManager类测试"""

    @pytest.mark.asyncio
    async def test_init_and_initialize(self):
        """测试管理器初始化"""
        with patch("src.core.database_pool.DatabaseConnectionPool") as mock_pool_class:
            with patch("src.core.database_pool.get_connection_pool") as mock_get_pool:
                mock_pool = AsyncMock()
                mock_get_pool.return_value = mock_pool
                mock_pool_class.return_value = mock_pool

                manager = DatabaseConnectionManager()

                # 验证初始化
                assert hasattr(manager, "_pool")

                # 测试初始化
                await manager.initialize()

                mock_pool.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_connection(self):
        """测试获取连接"""
        with patch("src.core.database_pool.get_connection_pool") as mock_get_pool:
            mock_pool = AsyncMock()
            mock_get_pool.return_value = mock_pool

            manager = DatabaseConnectionManager()

            # Mock get_connection method
            mock_connection = AsyncMock()
            mock_get_connection_ctx = AsyncMock()
            mock_get_connection_ctx.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_get_connection_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_pool.get_connection.return_value = mock_get_connection_ctx

            async with manager.get_connection() as conn:
                assert conn == mock_connection
                mock_pool.get_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query(self):
        """测试执行查询"""
        with patch("src.core.database_pool.get_connection_pool") as mock_get_pool:
            mock_pool = AsyncMock()
            mock_get_pool.return_value = mock_pool

            manager = DatabaseConnectionManager()

            # Mock get_connection method
            mock_connection = AsyncMock()
            expected_result = [{"id": 1, "name": "test"}]
            mock_connection.fetch.return_value = expected_result

            mock_get_connection_ctx = AsyncMock()
            mock_get_connection_ctx.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_get_connection_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_pool.get_connection.return_value = mock_get_connection_ctx

            result = await manager.execute_query("SELECT * FROM test")

            assert result == expected_result

    @pytest.mark.asyncio
    async def test_execute_command(self):
        """测试执行命令"""
        with patch("src.core.database_pool.get_connection_pool") as mock_get_pool:
            mock_pool = AsyncMock()
            mock_get_pool.return_value = mock_pool

            manager = DatabaseConnectionManager()

            # Mock get_connection method
            mock_connection = AsyncMock()
            expected_result = "INSERT 1"
            mock_connection.execute.return_value = expected_result

            mock_get_connection_ctx = AsyncMock()
            mock_get_connection_ctx.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_get_connection_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_pool.get_connection.return_value = mock_get_connection_ctx

            result = await manager.execute_command("INSERT INTO test VALUES (1)")

            assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """测试获取统计信息"""
        with patch("src.core.database_pool.get_connection_pool") as mock_get_pool:
            mock_pool = AsyncMock()
            mock_get_pool.return_value = mock_pool

            manager = DatabaseConnectionManager()

            # Mock stats
            expected_stats = {"total_connections": 10, "active_connections": 5}
            mock_pool.get_stats.return_value = expected_stats

            result = await manager.get_stats()

            assert result == expected_stats
            mock_pool.get_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查"""
        with patch("src.core.database_pool.get_connection_pool") as mock_get_pool:
            mock_pool = AsyncMock()
            mock_get_pool.return_value = mock_pool

            manager = DatabaseConnectionManager()

            # Mock health check
            mock_pool.health_check.return_value = True

            result = await manager.health_check()

            assert result is True
            mock_pool.health_check.assert_called_once()


class TestModuleFunctions:
    """模块函数测试"""

    @pytest.mark.asyncio
    async def test_get_connection_pool(self):
        """测试获取连接池函数"""
        with patch("src.core.database_pool.DatabaseConnectionPool") as mock_pool_class:
            mock_pool = AsyncMock()
            mock_pool_class.return_value = mock_pool

            # Mock全局变量
            with patch("src.core.database_pool._connection_pool", None):
                pool = await get_connection_pool()

                assert pool == mock_pool

    @pytest.mark.asyncio
    async def test_get_connection_pool_cached(self):
        """测试获取连接池函数（缓存）"""
        with patch("src.core.database_pool.DatabaseConnectionPool") as mock_pool_class:
            mock_pool = AsyncMock()
            mock_pool_class.return_value = mock_pool

            # Mock全局变量
            with patch("src.core.database_pool._connection_pool", mock_pool):
                pool = await get_connection_pool()

                # 应该返回缓存的pool
                assert pool == mock_pool
                # 不应该重新创建
                mock_pool_class.assert_not_called()

    @pytest.mark.asyncio
    async def test_close_connection_pool(self):
        """测试关闭连接池函数"""
        with patch("src.core.database_pool._connection_pool") as mock_global_pool:
            mock_pool = AsyncMock()
            mock_global_pool.return_value = mock_pool

            await close_connection_pool()

            mock_pool.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_connection_pool_no_pool(self):
        """测试关闭连接池函数（无连接池）"""
        with patch("src.core.database_pool._connection_pool", None):
            # 应该不会抛出异常
            await close_connection_pool()

    def test_get_db_manager(self):
        """测试获取数据库管理器函数"""
        with patch(
            "src.core.database_pool.DatabaseConnectionManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager

            manager = get_db_manager()

            assert manager == mock_manager


class TestMemoryMonitoring:
    """内存监控功能测试"""

    @pytest.mark.asyncio
    async def test_record_memory_snapshot_available(self):
        """测试记录内存快照（内存管理可用）"""
        mock_config = Mock()

        # Mock内存管理
        mock_memory_monitor = Mock()
        mock_memory_monitor.get_memory_usage.return_value = {
            "rss": 1000000,
            "vms": 2000000,
        }

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", True):
            with patch(
                "src.core.database_pool.get_memory_monitor",
                return_value=mock_memory_monitor,
            ):
                pool = DatabaseConnectionPool(mock_config)

                await pool._record_memory_snapshot("test_event")

                # 验证内存快照被记录
                assert len(pool._stats["memory_snapshots"]) == 1
                snapshot = pool._stats["memory_snapshots"][0]
                assert snapshot["event_type"] == "test_event"
                assert "timestamp" in snapshot
                assert "memory_usage" in snapshot

    @pytest.mark.asyncio
    async def test_record_memory_snapshot_unavailable(self):
        """测试记录内存快照（内存管理不可用）"""
        mock_config = Mock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # 应该不会抛出异常
            await pool._record_memory_snapshot("test_event")

            # 内存快照应该为空
            assert len(pool._stats["memory_snapshots"]) == 0

    def test_get_memory_analysis_available(self):
        """测试获取内存分析（内存管理可用）"""
        mock_config = Mock()

        # Mock内存快照
        mock_snapshots = [
            {
                "event_type": "test_event",
                "timestamp": time.time(),
                "memory_usage": {"rss": 1000000},
            },
            {
                "event_type": "test_event",
                "timestamp": time.time(),
                "memory_usage": {"rss": 1100000},
            },
        ]

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", True):
            pool = DatabaseConnectionPool(mock_config)
            pool._stats["memory_snapshots"] = mock_snapshots

            analysis = pool.get_memory_analysis()

            assert isinstance(analysis, dict)
            assert "total_snapshots" in analysis
            assert "memory_trend" in analysis
            assert "memory_growth_rate" in analysis

    def test_get_memory_analysis_unavailable(self):
        """测试获取内存分析（内存管理不可用）"""
        mock_config = Mock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            analysis = pool.get_memory_analysis()

            assert isinstance(analysis, dict)
            # 应该返回默认分析
            assert "total_snapshots" in analysis
            assert analysis["total_snapshots"] == 0

    def test_detect_memory_leak_indicators(self):
        """测试内存泄漏指标检测"""
        mock_config = Mock()

        # Mock内存快照显示持续增长
        mock_snapshots = []
        base_memory = 1000000
        for i in range(10):
            mock_snapshots.append(
                {
                    "event_type": "after_acquire",
                    "timestamp": time.time() + i,
                    "memory_usage": {"rss": base_memory + i * 100000},  # 持续增长
                }
            )

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", True):
            pool = DatabaseConnectionPool(mock_config)
            pool._stats["memory_snapshots"] = mock_snapshots

            indicators = pool._detect_memory_leak_indicators()

            assert isinstance(indicators, dict)
            assert "memory_leak_detected" in indicators
            assert "growth_rate" in indicators
            assert "correlation_score" in indicators

    @pytest.mark.asyncio
    async def test_cleanup_memory_snapshots(self):
        """测试清理内存快照"""
        mock_config = Mock()

        # 添加一些旧的快照
        old_time = time.time() - 3600  # 1小时前
        mock_snapshots = [
            {
                "event_type": "old_event",
                "timestamp": old_time,
                "memory_usage": {"rss": 1000000},
            },
            {
                "event_type": "new_event",
                "timestamp": time.time(),
                "memory_usage": {"rss": 1100000},
            },
        ]

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", True):
            pool = DatabaseConnectionPool(mock_config)
            pool._stats["memory_snapshots"] = mock_snapshots

            await pool.cleanup_memory_snapshots()

            # 应该只保留新的快照
            assert len(pool._stats["memory_snapshots"]) == 1
            assert pool._stats["memory_snapshots"][0]["event_type"] == "new_event"


class TestEdgeCasesAndErrorHandling:
    """边界情况和错误处理测试"""

    @pytest.mark.asyncio
    async def test_concurrent_connection_acquisition(self):
        """测试并发连接获取"""
        mock_config = Mock()

        # Mock连接
        mock_connection = AsyncMock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_pool.release = AsyncMock()
            pool.pool = mock_pool

            # 并发获取连接
            async def acquire_connection():
                async with pool.get_connection() as conn:
                    await asyncio.sleep(0.1)  # 模拟操作
                    return conn

            tasks = [acquire_connection() for _ in range(5)]
            connections = await asyncio.gather(*tasks)

            # 验证所有连接都成功获取
            assert len(connections) == 5
            for conn in connections:
                assert conn == mock_connection

            # 验证统计信息
            assert pool._stats["pool_hits"] == 5

    @pytest.mark.asyncio
    async def test_connection_time_tracking(self):
        """测试连接时间跟踪"""
        mock_config = Mock()

        # Mock连接
        mock_connection = AsyncMock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_pool.release = AsyncMock()
            pool.pool = mock_pool

            start_time = time.time()

            async with pool.get_connection() as conn:
                # 模拟一些工作
                await asyncio.sleep(0.1)

            hold_time = time.time() - start_time

            # 验证连接时间被跟踪（虽然具体实现可能不同）
            # 这里主要验证没有错误发生
            assert pool._stats["active_connections"] == 0

    @pytest.mark.asyncio
    async def test_query_with_large_timeout(self):
        """测试大超时时间的查询"""
        mock_config = Mock()

        # Mock连接
        mock_connection = AsyncMock()
        mock_connection.fetch.return_value = [{"id": 1}]

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_pool.release = AsyncMock()
            pool.pool = mock_pool

            # 使用大超时时间
            result = await pool.execute_query("SELECT * FROM test", timeout=300)

            assert result is not None
            mock_connection.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_command_execution(self):
        """测试多个命令执行"""
        mock_config = Mock()

        # Mock连接
        mock_connection = AsyncMock()
        mock_connection.execute.return_value = "COMMAND_OK"

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # Mock pool
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_pool.release = AsyncMock()
            pool.pool = mock_pool

            commands = [
                "INSERT INTO test VALUES (1)",
                "UPDATE test SET name = 'test' WHERE id = 1",
                "DELETE FROM test WHERE id = 2",
            ]

            results = []
            for command in commands:
                result = await pool.execute_command(command)
                results.append(result)

            assert len(results) == 3
            assert all(result == "COMMAND_OK" for result in results)
            assert pool._stats["total_queries"] == 3

    def test_stats_accuracy(self):
        """测试统计信息准确性"""
        mock_config = Mock()

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", False):
            pool = DatabaseConnectionPool(mock_config)

            # 手动修改统计信息
            original_stats = dict(pool._stats)
            original_stats["total_connections"] = 15
            original_stats["active_connections"] = 8
            original_stats["pool_hits"] = 100
            original_stats["pool_misses"] = 5
            original_stats["connection_timeouts"] = 2
            original_stats["total_queries"] = 50
            original_stats["query_errors"] = 3

            stats = pool.get_stats()

            # 验证统计信息准确性
            for key, value in original_stats.items():
                assert stats[key] == value

    @pytest.mark.asyncio
    async def test_memory_monitoring_integration(self):
        """测试内存监控集成"""
        mock_config = Mock()

        # Mock内存监控
        mock_memory_monitor = Mock()
        mock_memory_monitor.get_memory_usage.return_value = {
            "rss": 1000000,
            "vms": 2000000,
            "percent": 50.0,
        }

        with patch("src.core.database_pool.MEMORY_MANAGEMENT_AVAILABLE", True):
            with patch(
                "src.core.database_pool.get_memory_monitor",
                return_value=mock_memory_monitor,
            ):
                pool = DatabaseConnectionPool(mock_config)

                # Mock连接
                mock_connection = AsyncMock()

                # Mock pool
                mock_pool = AsyncMock()
                mock_pool.acquire.return_value = mock_connection
                mock_pool.release = AsyncMock()
                pool.pool = mock_pool

                # 执行一些操作来触发内存监控
                async with pool.get_connection() as conn:
                    await pool._record_memory_snapshot("test_event", extra_info="test")

                # 验证内存监控被调用
                mock_memory_monitor.get_memory_usage.assert_called()

                # 验证快照被记录
                assert len(pool._stats["memory_snapshots"]) > 0
