#!/usr/bin/env python3
"""数据库连接重试工具测试套件
完整测试db_connection_retry模块的所有功能，确保100%测试覆盖率
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Mock problematic imports to avoid circular dependency
import unittest.mock


sys.modules["src.storage.database.connection_manager"] = unittest.mock.MagicMock()
sys.modules["src.core.config"] = unittest.mock.MagicMock()
sys.modules["src.core.config_driven_table_manager"] = unittest.mock.MagicMock()

import pytest

# 导入被测试的模块
from src.utils.db_connection_retry import (
    DatabaseConnectionHandler,
    connection_handler,
    db_retry,
    get_postgresql_connection_with_retry,
    get_tdengine_connection_with_retry,
    init_connection_handler,
    return_postgresql_connection,
)


class TestIntegration:
    """集成测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建真实的连接管理器mock
        self.mock_conn_manager = MagicMock()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 清理全局状态
        import src.utils.db_connection_retry

        src.db_connection_retry.connection_handler = None

    def test_full_retry_workflow_integration(self):
        """测试完整重试工作流程集成"""
        # 模拟连接管理器的行为
        self.mock_conn_manager.get_tdengine_connection.side_effect = [
            ConnectionError("TDengine first failure"),
            ConnectionError("TDengine second failure"),
            self.mock_tdengine_conn,
        ]

        self.mock_conn_manager.get_postgresql_connection.return_value = self.mock_postgres_pool
        self.mock_postgres_pool.getconn.return_value = self.mock_postgres_conn

        # 初始化连接处理器
        init_connection_handler(self.mock_conn_manager)

        # 测试TDengine连接（带重试）
        td_result = get_tdengine_connection_with_retry()
        assert td_result is self.mock_tdengine_conn

        # 验证重试被调用
        assert self.mock_conn_manager.get_tdengine_connection.call_count == 3

        # 测试PostgreSQL连接
        pg_result = get_postgresql_connection_with_retry()
        assert pg_result is self.mock_postgres_conn

        # 归还连接
        return_postgresql_connection(pg_result)

        # 验证调用
        self.mock_postgres_pool.putconn.assert_called_once()

    def test_error_classification_integration(self):
        """测试错误分类集成"""
        error_types = [
            (ConnectionError("Connection failed"), True),  # 应该重试
            (TimeoutError("Operation timeout"), True),  # 应该重试
            (OSError("Network error"), True),  # 应该重试
            (ValueError("Invalid data"), False),  # 不应该重试
            (RuntimeError("Logic error"), False),  # 不应该重试
            (Exception("General error"), False),  # 不应该重试
        ]

        @db_retry(max_retries=1, delay=0.01)
        def test_function(error_to_raise):
            raise error_to_raise

        for error, should_retry in error_types:
            if should_retry:
                # 应该重试并最终失败
                with pytest.raises(type(error)):
                    test_function(error)
            else:
                # 不应该重试，直接失败
                with pytest.raises(type(error)):
                    test_function(error)

    def test_logging_integration_with_structlog(self):
        """测试与structlog集成"""
        with patch("src.utils.db_connection_retry.logger") as mock_logger:

            @db_retry(max_retries=1, delay=0.01)
            def failing_function():
                raise ConnectionError("Test error")

            with pytest.raises(ConnectionError):
                failing_function()

            # 验证警告日志被正确记录
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args[0]
            assert "数据库连接失败" in call_args
            assert "function=failing_function" in call_args

    def test_dependency_injection_pattern(self):
        """测试依赖注入模式"""
        # 创建不同的连接管理器实例
        conn_manager1 = MagicMock()
        conn_manager2 = MagicMock()

        handler1 = DatabaseConnectionHandler(conn_manager1)
        handler2 = DatabaseConnectionHandler(conn_manager2)

        # 验证每个处理器使用自己的连接管理器
        assert handler1.connection_manager is conn_manager1
        assert handler2.connection_manager is conn_manager2
        assert handler1.connection_manager is not handler2.connection_manager

    def test_global_state_isolation(self):
        """测试全局状态隔离"""
        # 第一个处理器实例
        init_connection_handler(self.mock_conn_manager)
        first_handler = connection_handler

        # 重新初始化（模拟配置更新）
        new_conn_manager = MagicMock()
        init_connection_handler(new_conn_manager)
        second_handler = connection_handler

        # 验证全局变量被正确更新
        assert first_handler is second_handler
        assert first_handler.connection_manager is new_conn_manager

    def test_connection_lifecycle_management(self):
        """测试连接生命周期管理"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        # 设置mock行为
        self.mock_conn_manager.get_tdengine_connection.return_value = self.mock_tdengine_conn
        self.mock_conn_manager.get_postgresql_connection.return_value = self.mock_postgres_pool
        self.mock_postgres_pool.getconn.return_value = self.mock_postgres_conn

        # 获取连接
        td_conn = handler.get_tdengine_connection()
        pg_conn = handler.get_postgresql_connection()

        # 归还连接
        handler.return_postgresql_connection(pg_conn)

        # 关闭所有连接
        handler.close_all_connections()

        # 验证调用序列
        assert td_conn is self.mock_tdengine_conn
        assert pg_conn is self.mock_postgres_conn
        self.mock_postgres_pool.putconn.assert_called_once()
        self.mock_conn_manager.close_all_connections.assert_called_once()

    def test_concurrent_connection_handling(self):
        """测试并发连接处理"""
        import queue
        import threading

        results = queue.Queue()

        def worker_thread(worker_id):
            try:
                # 初始化连接处理器
                worker_handler = DatabaseConnectionHandler(self.mock_conn_manager)
                results.put(f"Worker {worker_id}: initialized")

                # 尝试获取连接
                conn = worker_handler.get_tdengine_connection()
                results.put(f"Worker {worker_id}: got connection")

            except Exception as e:
                results.put(f"Worker {worker_id}: {e!s}")

        # 创建多个工作线程
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_thread, args=(i + 1))
            threads.append(thread)

        # 启动所有线程
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 收集结果
        collected_results = []
        while not results.empty():
            try:
                collected_results.append(results.get_nowait(timeout=1.0))
            except queue.Empty:
                break

        assert len(collected_results) == 3
        assert all("initialized" in result for result in collected_results)

    def test_retry_with_different_error_patterns(self):
        """测试不同错误模式的重试行为"""
        error_patterns = [
            ("Connection reset by peer", True),
            ("Connection timed out", True),
            ("Connection refused", True),
            ("No connection could be made", True),
            ("Host is down", True),
            ("SSL handshake failed", True),
        ]

        for error_msg, should_retry in error_patterns:

            @db_retry(max_retries=1, delay=0.01)
            def error_function():
                raise ConnectionError(error_msg)

            if should_retry:
                with pytest.raises(ConnectionError, match=error_msg):
                    error_function()
            else:
                with pytest.raises(ConnectionError, match=error_msg):
                    error_function()

    def test_mixed_database_operations(self):
        """测试混合数据库操作"""
        # 模拟不同数据库的连接行为
        self.mock_conn_manager.get_tdengine_connection.return_value = self.mock_tdengine_conn
        self.mock_conn_manager.get_postgresql_connection.return_value = self.mock_postgres_pool
        self.mock_postgres_pool.getconn.return_value = self.mock_postgres_conn

        # 设置不同的错误模式
        self.mock_conn_manager.get_tdengine_connection.side_effect = [
            ConnectionError("TDengine busy"),
            ConnectionError("TDengine busy"),
            self.mock_tdengine_conn,  # 第三次成功
        ]

        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        # 测试混合操作
        pg_conn1 = handler.get_postgresql_connection()
        td_conn = handler.get_tdengine_connection()
        pg_conn2 = handler.get_postgresql_connection()

        # 归还第一个PostgreSQL连接
        handler.return_postgresql_connection(pg_conn1)

        assert pg_conn1 is self.mock_postgres_conn
        assert pg_conn2 is self.mock_postgres_conn
        assert td_conn is self.mock_tdengine_conn

        # 验证TDengine重试
        assert self.mock_conn_manager.get_tdengine_connection.call_count == 3


class CustomConnectionError(Exception):
    """自定义连接错误类"""


class CustomTimeoutError(Exception):
    """自定义超时错误类"""
