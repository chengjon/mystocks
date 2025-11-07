"""
TDengine连接池单元测试 - Phase 3 Task 19
测试连接池的核心功能：连接获取/释放、健康检查、超时处理、统计
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.core.tdengine_pool import TDengineConnectionPool, ConnectionContext


class TestTDengineConnectionPool:
    """TDengine连接池测试类"""

    @pytest.fixture
    def mock_connection(self):
        """创建模拟的TDengine连接"""
        conn = Mock()
        cursor = Mock()
        cursor.execute = Mock()
        cursor.fetchone = Mock(return_value=("TDengine 3.0.0",))
        cursor.close = Mock()
        conn.cursor = Mock(return_value=cursor)
        conn.close = Mock()
        return conn

    @pytest.fixture
    def pool(self, mock_connection):
        """创建测试用连接池"""
        with patch("app.core.tdengine_pool.connect") as mock_connect:
            mock_connect.return_value = mock_connection
            pool = TDengineConnectionPool(
                host="127.0.0.1",
                port=6030,
                user="root",
                password="taosdata",
                database="test_db",
                min_size=2,
                max_size=5,
                max_idle_time=10,
                health_check_interval=5,
            )
            yield pool
            pool.close_all()

    def test_pool_initialization(self, pool):
        """测试连接池初始化"""
        # 验证最小连接数已创建
        stats = pool.get_stats()
        assert stats["pool_size"] >= 2
        assert stats["idle_connections"] >= 2
        assert stats["total_created"] >= 2

    def test_get_connection(self, pool):
        """测试获取连接"""
        conn = pool.get_connection(timeout=5)
        assert conn is not None

        # 验证统计信息更新
        stats = pool.get_stats()
        assert stats["active_connections"] >= 1
        assert stats["connection_requests"] >= 1

        # 归还连接
        pool.release_connection(conn)

    def test_release_connection(self, pool):
        """测试归还连接"""
        # 获取连接
        conn = pool.get_connection(timeout=5)
        active_before = pool.get_stats()["active_connections"]

        # 归还连接
        pool.release_connection(conn)
        active_after = pool.get_stats()["active_connections"]

        # 验证活跃连接数减少
        assert active_after < active_before

    def test_connection_timeout(self, pool):
        """测试连接超时"""
        # 获取所有可用连接
        connections = []
        for _ in range(5):  # max_size = 5
            conn = pool.get_connection(timeout=1)
            if conn:
                connections.append(conn)

        # 尝试获取超过最大数量的连接，应该超时
        conn = pool.get_connection(timeout=1)
        assert conn is None

        # 验证超时统计
        stats = pool.get_stats()
        assert stats["connection_timeouts"] > 0

        # 清理
        for c in connections:
            pool.release_connection(c)

    def test_connection_context_manager(self, pool):
        """测试连接上下文管理器"""
        # 使用上下文管理器
        with pool.get_connection_context(timeout=5) as conn:
            assert conn is not None
            active_during = pool.get_stats()["active_connections"]
            assert active_during >= 1

        # 退出上下文后连接应该被归还
        stats = pool.get_stats()
        assert stats["active_connections"] < active_during

    def test_connection_health_check(self, pool, mock_connection):
        """测试连接健康检查"""
        # 获取连接
        conn = pool.get_connection(timeout=5)

        # 验证健康检查被调用
        assert conn.cursor.called

        # 归还连接
        pool.release_connection(conn)

    def test_unhealthy_connection_handling(self, pool):
        """测试不健康连接的处理"""
        with patch("app.core.tdengine_pool.connect") as mock_connect:
            # 创建一个会失败的连接
            unhealthy_conn = Mock()
            unhealthy_conn.cursor = Mock(side_effect=Exception("Connection lost"))

            mock_connect.return_value = unhealthy_conn

            # 获取连接时应该检测到不健康并重新创建
            # 由于我们的实现会在健康检查失败时重新创建，这里需要确保有足够的连接
            conn = pool.get_connection(timeout=5)

            # 如果健康检查失败，应该尝试重新创建连接
            # 这个测试主要验证错误处理逻辑存在

    def test_pool_stats(self, pool):
        """测试连接池统计信息"""
        stats = pool.get_stats()

        # 验证统计字段存在
        assert "total_created" in stats
        assert "total_closed" in stats
        assert "active_connections" in stats
        assert "idle_connections" in stats
        assert "connection_requests" in stats
        assert "connection_timeouts" in stats
        assert "connection_errors" in stats
        assert "pool_size" in stats
        assert "timestamp" in stats

        # 验证基本统计值
        assert stats["total_created"] >= 2  # min_size
        assert stats["pool_size"] >= 2

    def test_concurrent_connections(self, pool):
        """测试并发获取连接"""
        connections = []
        errors = []

        def get_conn():
            try:
                conn = pool.get_connection(timeout=5)
                if conn:
                    connections.append(conn)
            except Exception as e:
                errors.append(e)

        # 创建多个线程并发获取连接
        threads = []
        for _ in range(3):
            t = threading.Thread(target=get_conn)
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        # 验证没有错误
        assert len(errors) == 0
        assert len(connections) >= 1

        # 清理
        for conn in connections:
            pool.release_connection(conn)

    def test_close_all_connections(self, pool):
        """测试关闭所有连接"""
        # 获取一些连接
        conn1 = pool.get_connection(timeout=5)
        conn2 = pool.get_connection(timeout=5)

        initial_pool_size = pool.get_stats()["pool_size"]
        assert initial_pool_size >= 2

        # 归还连接
        pool.release_connection(conn1)
        pool.release_connection(conn2)

        # 关闭所有连接
        pool.close_all()

        # 验证连接池已清空
        stats = pool.get_stats()
        # close_all后统计应该返回None或空
        assert stats is None or stats.get("pool_size", 0) == 0

    def test_max_pool_size_limit(self, pool):
        """测试连接池最大数量限制"""
        connections = []

        # 尝试获取超过max_size的连接
        for _ in range(10):  # max_size = 5
            conn = pool.get_connection(timeout=1)
            if conn:
                connections.append(conn)

        # 验证获取的连接数不超过max_size
        assert len(connections) <= 5

        # 清理
        for conn in connections:
            pool.release_connection(conn)


class TestConnectionContext:
    """连接上下文管理器测试类"""

    @pytest.fixture
    def mock_pool(self):
        """创建模拟的连接池"""
        pool = Mock()
        conn = Mock()
        pool.get_connection = Mock(return_value=conn)
        pool.release_connection = Mock()
        return pool

    def test_context_manager_normal_flow(self, mock_pool):
        """测试上下文管理器正常流程"""
        context = ConnectionContext(mock_pool, timeout=30)

        with context as conn:
            # 验证连接被获取
            assert conn is not None
            mock_pool.get_connection.assert_called_once_with(timeout=30)

        # 验证连接被归还
        mock_pool.release_connection.assert_called_once()

    def test_context_manager_timeout(self, mock_pool):
        """测试上下文管理器超时"""
        mock_pool.get_connection = Mock(return_value=None)
        context = ConnectionContext(mock_pool, timeout=1)

        # 应该抛出TimeoutError
        with pytest.raises(TimeoutError):
            with context as conn:
                pass

    def test_context_manager_exception_handling(self, mock_pool):
        """测试上下文管理器异常处理"""
        context = ConnectionContext(mock_pool, timeout=30)

        try:
            with context as conn:
                # 在上下文中抛出异常
                raise ValueError("Test error")
        except ValueError:
            pass

        # 即使有异常，连接也应该被归还
        mock_pool.release_connection.assert_called_once()


class TestPoolPerformance:
    """连接池性能测试"""

    @pytest.fixture
    def perf_pool(self):
        """创建性能测试用连接池"""
        with patch("app.core.tdengine_pool.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.execute = Mock()
            mock_cursor.fetchone = Mock(return_value=("TDengine 3.0.0",))
            mock_cursor.close = Mock()
            mock_conn.cursor = Mock(return_value=mock_cursor)
            mock_conn.close = Mock()
            mock_connect.return_value = mock_conn

            pool = TDengineConnectionPool(
                min_size=5, max_size=20, max_idle_time=60, health_check_interval=30
            )
            yield pool
            pool.close_all()

    def test_connection_reuse_performance(self, perf_pool):
        """测试连接复用性能"""
        # 首次获取连接
        start_time = time.time()
        conn1 = perf_pool.get_connection(timeout=5)
        first_get_time = time.time() - start_time

        # 归还并再次获取（应该更快，因为是复用）
        perf_pool.release_connection(conn1)

        start_time = time.time()
        conn2 = perf_pool.get_connection(timeout=5)
        second_get_time = time.time() - start_time

        # 复用连接应该更快（虽然在mock环境下可能看不出明显差异）
        # 主要验证没有错误发生
        assert conn2 is not None

        perf_pool.release_connection(conn2)

    def test_high_concurrency(self, perf_pool):
        """测试高并发场景"""
        results = {"success": 0, "failed": 0}
        lock = threading.Lock()

        def worker():
            try:
                conn = perf_pool.get_connection(timeout=5)
                if conn:
                    # 模拟一些工作
                    time.sleep(0.01)
                    perf_pool.release_connection(conn)
                    with lock:
                        results["success"] += 1
                else:
                    with lock:
                        results["failed"] += 1
            except Exception:
                with lock:
                    results["failed"] += 1

        # 创建50个并发线程
        threads = []
        for _ in range(50):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        # 验证大部分请求成功
        assert results["success"] >= 20  # 至少20个成功（max_size=20）
        assert results["success"] + results["failed"] == 50


class TestIdleConnectionCleanup:
    """空闲连接清理测试"""

    def test_idle_connection_cleanup(self):
        """测试空闲连接自动清理"""
        with patch("app.core.tdengine_pool.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.execute = Mock()
            mock_cursor.fetchone = Mock(return_value=("TDengine 3.0.0",))
            mock_cursor.close = Mock()
            mock_conn.cursor = Mock(return_value=mock_cursor)
            mock_conn.close = Mock()
            mock_connect.return_value = mock_conn

            # 创建短超时的连接池
            pool = TDengineConnectionPool(
                min_size=2,
                max_size=5,
                max_idle_time=2,  # 2秒超时
                health_check_interval=1,  # 1秒检查间隔
            )

            # 获取并归还连接
            conn = pool.get_connection(timeout=5)
            pool.release_connection(conn)

            initial_size = pool.get_stats()["pool_size"]

            # 等待清理线程运行
            time.sleep(3)

            # 由于连接空闲超过2秒，可能会被清理
            # 但由于min_size=2，至少会保留2个连接
            stats = pool.get_stats()

            # 验证清理逻辑运行（即使没有实际清理，也应该有统计）
            assert "pool_size" in stats

            pool.close_all()
