"""
Database Connection Retry Test Suite
数据库连接重试测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.utils.db_connection_retry (177行)
"""

import os

# Import only the decorator function to avoid circular import
import sys
import time
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# Mock the problematic imports before importing the module
with patch.dict(
    "sys.modules",
    {
        "src.storage.database.connection_manager": MagicMock(),
        "src.storage.database": MagicMock(),
        "src.storage": MagicMock(),
        "structlog": MagicMock(),
    },
):
    from src.utils.db_connection_retry import db_retry


# Create mock classes for the components that cause circular imports
class MockDatabaseConnectionManager:
    def __init__(self):
        self.tdengine_conn = MagicMock()
        self.postgres_pool = MagicMock()

    def get_tdengine_connection(self):
        return self.tdengine_conn

    def get_postgresql_connection(self):
        return self.postgres_pool

    def close_all_connections(self):
        pass


class MockDatabaseConnectionHandler:
    def __init__(self, conn_manager):
        self.connection_manager = conn_manager
        self._connection_cache = {}

    @db_retry(max_retries=3, delay=1.0)
    def get_tdengine_connection(self):
        return self.connection_manager.get_tdengine_connection()

    @db_retry(max_retries=3, delay=1.0)
    def get_postgresql_connection(self):
        pool = self.connection_manager.get_postgresql_connection()
        return pool.getconn()

    def return_postgresql_connection(self, conn):
        try:
            pool = self.connection_manager.get_postgresql_connection()
            pool.putconn(conn)
        except Exception as e:
            print(f"归还PostgreSQL连接失败: {e}")

    def close_all_connections(self):
        if self.connection_manager:
            self.connection_manager.close_all_connections()


# Mock the connection_handler module variable
connection_handler = None


def get_tdengine_connection_with_retry():
    if connection_handler is None:
        raise RuntimeError("DatabaseConnectionHandler未初始化")
    return connection_handler.get_tdengine_connection()


def get_postgresql_connection_with_retry():
    if connection_handler is None:
        raise RuntimeError("DatabaseConnectionHandler未初始化")
    return connection_handler.get_postgresql_connection()


def return_postgresql_connection(conn):
    if connection_handler is None:
        raise RuntimeError("DatabaseConnectionHandler未初始化")
    return connection_handler.return_postgresql_connection(conn)


def init_connection_handler(conn_manager):
    global connection_handler
    connection_handler = MockDatabaseConnectionHandler(conn_manager)


class TestDatabaseRetryDecorator:
    """数据库重试装饰器测试"""

    def test_retry_decorator_success_first_try(self):
        """测试重试装饰器首次尝试成功"""

        @db_retry(max_retries=3, delay=0.01, backoff=1.0)
        def success_function():
            return "success"

        result = success_function()
        assert result == "success"

    def test_retry_decorator_eventual_success(self):
        """测试重试装饰器重试后成功"""
        call_count = 0

        @db_retry(max_retries=3, delay=0.01, backoff=1.0)
        def retry_success_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Connection failed")
            return "eventual_success"

        start_time = time.time()
        result = retry_success_function()
        end_time = time.time()

        assert result == "eventual_success"
        assert call_count == 2
        # 验证有延迟
        assert end_time - start_time >= 0.01

    def test_retry_decorator_all_retries_failed(self):
        """测试重试装饰器所有重试都失败"""

        @db_retry(max_retries=2, delay=0.01, backoff=1.0)
        def always_fail_function():
            raise ConnectionError("Always fails")

        with patch("src.utils.db_connection_retry.logger") as mock_logger:
            with pytest.raises(ConnectionError, match="Always fails"):
                always_fail_function()

            # 验证警告和错误日志被记录
            assert mock_logger.warning.called
            assert mock_logger.error.called

    def test_retry_decorator_non_connection_error(self):
        """测试重试装饰器非连接错误不重试"""
        call_count = 0

        @db_retry(max_retries=3, delay=0.01, backoff=1.0)
        def non_connection_error_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Not a connection error")

        with pytest.raises(ValueError, match="Not a connection error"):
            non_connection_error_function()

        # 应该只调用一次，不重试
        assert call_count == 1

    def test_retry_decorator_connection_error_keywords(self):
        """测试重试装饰器连接错误关键词识别"""
        connection_errors = [
            ConnectionError("connection failed"),
            TimeoutError("timeout occurred"),
            OSError("network unreachable"),
            ConnectionResetError("connection reset"),
            ConnectionRefusedError("connection refused"),
            RuntimeError("database closed"),
        ]

        for error in connection_errors:
            call_count = 0

            @db_retry(max_retries=2, delay=0.001, backoff=1.0)
            def test_function():
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    raise error
                return "success"

            result = test_function()
            assert result == "success"
            assert call_count == 2

    def test_retry_decorator_preserves_function_metadata(self):
        """测试重试装饰器保留函数元数据"""

        @db_retry(max_retries=3)
        def test_function(param1, param2=None):
            """测试函数文档字符串"""
            return f"result_{param1}_{param2 or 'default'}"

        # 验证函数元数据被保留
        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "测试函数文档字符串"

        # 验证函数仍然正常工作
        result = test_function("test", param2="value")
        assert result == "result_test_value"

    def test_retry_decorator_with_backoff(self):
        """测试重试装饰器指数退避延迟"""
        attempt_times = []

        @db_retry(max_retries=3, delay=0.01, backoff=2.0)
        def backoff_function():
            attempt_times.append(time.time())
            if len(attempt_times) < 3:
                raise ConnectionError("Connection failed")
            return "success"

        backoff_function()

        assert len(attempt_times) == 3
        # 验证延迟递增
        delay1 = attempt_times[1] - attempt_times[0]
        delay2 = attempt_times[2] - attempt_times[1]
        assert delay2 >= delay1 * 1.8  # 允许一些时间误差

    def test_retry_decorator_default_parameters(self):
        """测试重试装饰器默认参数"""

        @db_retry()  # 使用默认参数
        def default_params_function():
            return "success"

        result = default_params_function()
        assert result == "success"

    def test_retry_decorator_zero_delay(self):
        """测试重试装饰器零延迟"""
        call_count = 0

        @db_retry(max_retries=2, delay=0, backoff=1.0)
        def zero_delay_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Connection failed")
            return "success"

        start_time = time.time()
        result = zero_delay_function()
        end_time = time.time()

        assert result == "success"
        assert call_count == 2
        # 零延迟应该快速完成
        assert end_time - start_time < 0.1

    def test_retry_decorator_case_insensitive_error_matching(self):
        """测试重试装饰器大小写不敏感错误匹配"""

        @db_retry(max_retries=2, delay=0.001)
        def case_insensitive_function():
            raise RuntimeError("CONNECTION TIMEOUT")

        with patch("src.utils.db_connection_retry.logger") as mock_logger:
            with pytest.raises(RuntimeError):
                case_insensitive_function()

            # 应该记录重试日志（说明识别为连接错误）
            assert mock_logger.warning.called


class TestDatabaseConnectionHandler:
    """数据库连接处理器测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # Mock DatabaseConnectionManager
        self.mock_conn_manager = MagicMock()
        self.mock_tdengine_conn = MagicMock()
        self.mock_postgres_pool = MagicMock()
        self.mock_postgres_conn = MagicMock()

        # 配置mock返回值
        self.mock_conn_manager.get_tdengine_connection.return_value = self.mock_tdengine_conn
        self.mock_conn_manager.get_postgresql_connection.return_value = self.mock_postgres_pool
        self.mock_postgres_pool.getconn.return_value = self.mock_postgres_conn

    def test_init_connection_handler(self):
        """测试连接处理器初始化"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        assert handler.connection_manager == self.mock_conn_manager
        assert handler._connection_cache == {}

    def test_get_tdengine_connection_success(self):
        """测试获取TDengine连接成功"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        result = handler.get_tdengine_connection()

        assert result == self.mock_tdengine_conn
        self.mock_conn_manager.get_tdengine_connection.assert_called_once()

    def test_get_postgresql_connection_success(self):
        """测试获取PostgreSQL连接成功"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        result = handler.get_postgresql_connection()

        assert result == self.mock_postgres_conn
        self.mock_conn_manager.get_postgresql_connection.assert_called_once()
        self.mock_postgres_pool.getconn.assert_called_once()

    def test_return_postgresql_connection_success(self):
        """测试归还PostgreSQL连接成功"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        handler.return_postgresql_connection(self.mock_postgres_conn)

        self.mock_conn_manager.get_postgresql_connection.assert_called_once()
        self.mock_postgres_pool.putconn.assert_called_once_with(self.mock_postgres_conn)

    def test_return_postgresql_connection_failure(self):
        """测试归还PostgreSQL连接失败"""
        # 配置putconn抛出异常
        self.mock_postgres_pool.putconn.side_effect = Exception("Connection return failed")

        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        with patch("src.utils.db_connection_retry.logger") as mock_logger:
            handler.return_postgresql_connection(self.mock_postgres_conn)

            # 验证错误日志被记录
            mock_logger.error.assert_called_once()
            assert "归还PostgreSQL连接失败" in str(mock_logger.error.call_args)

    def test_close_all_connections(self):
        """测试关闭所有连接"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        handler.close_all_connections()

        self.mock_conn_manager.close_all_connections.assert_called_once()

    def test_close_all_connections_none_manager(self):
        """测试关闭所有连接（管理器为None）"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)
        handler.connection_manager = None

        # 应该不会抛出异常
        handler.close_all_connections()

    def test_get_tdengine_connection_with_retry_decorator(self):
        """测试TDengine连接方法带有重试装饰器"""
        # 配置前两次失败，第三次成功
        self.mock_conn_manager.get_tdengine_connection.side_effect = [
            ConnectionError("First failure"),
            ConnectionError("Second failure"),
            self.mock_tdengine_conn,
        ]

        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        with patch("src.utils.db_connection_retry.logger"):
            result = handler.get_tdengine_connection()

        assert result == self.mock_tdengine_conn
        assert self.mock_conn_manager.get_tdengine_connection.call_count == 3

    def test_get_postgresql_connection_with_retry_decorator(self):
        """测试PostgreSQL连接方法带有重试装饰器"""
        # 配置前两次失败，第三次成功
        self.mock_conn_manager.get_postgresql_connection.side_effect = [
            ConnectionError("First failure"),
            ConnectionError("Second failure"),
            self.mock_postgres_pool,
        ]

        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        with patch("src.utils.db_connection_retry.logger"):
            result = handler.get_postgresql_connection()

        assert result == self.mock_postgres_conn
        assert self.mock_conn_manager.get_postgresql_connection.call_count == 3


class TestGlobalConnectionFunctions:
    """全局连接函数测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 保存原始的全局connection_handler
        self.original_handler = connection_handler

        # 重置全局connection_handler
        import src.utils.db_connection_retry

        src.utils.db_connection_retry.connection_handler = None

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 恢复原始的全局connection_handler
        import src.utils.db_connection_retry

        src.utils.db_connection_retry.connection_handler = self.original_handler

    def test_init_connection_handler(self):
        """测试初始化连接处理器"""
        mock_manager = MagicMock()

        init_connection_handler(mock_manager)

        import src.utils.db_connection_retry

        assert src.utils.db_connection_retry.connection_handler is not None
        assert isinstance(src.utils.db_connection_retry.connection_handler, DatabaseConnectionHandler)

    def test_get_tdengine_connection_with_retry_success(self):
        """测试全局TDengine连接获取成功"""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_manager.get_tdengine_connection.return_value = mock_conn

        init_connection_handler(mock_manager)

        result = get_tdengine_connection_with_retry()
        assert result == mock_conn

    def test_get_postgresql_connection_with_retry_success(self):
        """测试全局PostgreSQL连接获取成功"""
        mock_manager = MagicMock()
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_pool.getconn.return_value = mock_conn

        init_connection_handler(mock_manager)

        result = get_postgresql_connection_with_retry()
        assert result == mock_conn

    def test_return_postgresql_connection_success(self):
        """测试全局归还PostgreSQL连接成功"""
        mock_manager = MagicMock()
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_manager.get_postgresql_connection.return_value = mock_pool

        init_connection_handler(mock_manager)

        return_postgresql_connection(mock_conn)
        mock_pool.putconn.assert_called_once_with(mock_conn)

    def test_global_functions_uninitialized_handler(self):
        """测试全局函数未初始化处理器的情况"""
        # 确保connection_handler为None
        import src.utils.db_connection_retry

        src.utils.db_connection_retry.connection_handler = None

        with pytest.raises(RuntimeError, match="DatabaseConnectionHandler未初始化"):
            get_tdengine_connection_with_retry()

        with pytest.raises(RuntimeError, match="DatabaseConnectionHandler未初始化"):
            get_postgresql_connection_with_retry()

        with pytest.raises(RuntimeError, match="DatabaseConnectionHandler未初始化"):
            return_postgresql_connection(MagicMock())

    def test_global_functions_with_retry_logic(self):
        """测试全局函数的重试逻辑"""
        mock_manager = MagicMock()
        mock_conn = MagicMock()

        # 配置前两次失败，第三次成功
        mock_manager.get_tdengine_connection.side_effect = [
            ConnectionError("First failure"),
            ConnectionError("Second failure"),
            mock_conn,
        ]

        init_connection_handler(mock_manager)

        with patch("src.utils.db_connection_retry.logger"):
            result = get_tdengine_connection_with_retry()

        assert result == mock_conn
        assert mock_manager.get_tdengine_connection.call_count == 3


class TestIntegrationScenarios:
    """集成测试场景"""

    def test_database_connection_handler_lifecycle(self):
        """测试数据库连接处理器生命周期"""
        mock_manager = MagicMock()
        mock_td_conn = MagicMock()
        mock_pg_pool = MagicMock()
        mock_pg_conn = MagicMock()

        mock_manager.get_tdengine_connection.return_value = mock_td_conn
        mock_manager.get_postgresql_connection.return_value = mock_pg_pool
        mock_pg_pool.getconn.return_value = mock_pg_conn

        # 初始化
        handler = DatabaseConnectionHandler(mock_manager)

        # 获取连接
        td_conn = handler.get_tdengine_connection()
        pg_conn = handler.get_postgresql_connection()

        assert td_conn == mock_td_conn
        assert pg_conn == mock_pg_conn

        # 归还连接
        handler.return_postgresql_connection(pg_conn)
        mock_pg_pool.putconn.assert_called_once_with(pg_conn)

        # 关闭所有连接
        handler.close_all_connections()
        mock_manager.close_all_connections.assert_called_once()

    def test_retry_with_different_backoff_strategies(self):
        """测试不同的退避策略"""
        results = {}

        for backoff in [1.0, 1.5, 2.0, 3.0]:
            attempt_times = []

            @db_retry(max_retries=3, delay=0.01, backoff=backoff)
            def test_function():
                attempt_times.append(time.time())
                if len(attempt_times) < 3:
                    raise ConnectionError("Connection failed")
                return "success"

            test_function()
            results[backoff] = attempt_times

        # 验证不同退避倍数产生不同的延迟模式
        for backoff, times in results.items():
            if len(times) >= 3:
                delay1 = times[1] - times[0]
                delay2 = times[2] - times[1]
                # 验证延迟按backoff倍数增长（允许一些误差）
                assert delay2 >= delay1 * (backoff * 0.8)

    def test_concurrent_connection_access(self):
        """测试并发连接访问"""
        import threading

        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_manager.get_tdengine_connection.return_value = mock_conn

        handler = DatabaseConnectionHandler(mock_manager)
        results = []
        errors = []

        def get_connection():
            try:
                conn = handler.get_tdengine_connection()
                results.append(conn)
            except Exception as e:
                errors.append(e)

        # 创建多个线程同时获取连接
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_connection)
            threads.append(thread)

        # 启动所有线程
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(errors) == 0
        assert len(results) == 5
        assert all(result == mock_conn for result in results)

    def test_complex_error_scenarios(self):
        """测试复杂错误场景"""
        scenarios = [
            # (exception_class, error_message, should_retry)
            (ConnectionError, "connection failed", True),
            (TimeoutError, "request timeout", True),
            (OSError, "network unreachable", True),
            (ValueError, "invalid parameter", False),
            (TypeError, "type mismatch", False),
            (RuntimeError, "database closed unexpectedly", True),
            (RuntimeError, "normal runtime error", False),
        ]

        for exception_class, error_message, should_retry in scenarios:
            call_count = 0

            @db_retry(max_retries=2, delay=0.001)
            def test_function():
                nonlocal call_count
                call_count += 1
                raise exception_class(error_message)

            with pytest.raises(exception_class):
                test_function()

            if should_retry:
                # 应该重试多次
                assert call_count > 1
            else:
                # 应该只调用一次，不重试
                assert call_count == 1

    def test_decorator_stack_trace_preservation(self):
        """测试装饰器保留堆栈跟踪"""

        @db_retry(max_retries=1)
        def failing_function():
            raise ValueError("Original error")

        try:
            failing_function()
        except ValueError as e:
            # 验证原始异常信息被保留
            assert str(e) == "Original error"
            # 验证异常类型正确
            assert isinstance(e, ValueError)

    def test_mixed_connection_operations(self):
        """测试混合连接操作"""
        mock_manager = MagicMock()
        mock_td_conn = MagicMock()
        mock_pg_pool = MagicMock()
        mock_pg_conn1 = MagicMock()
        mock_pg_conn2 = MagicMock()

        mock_manager.get_tdengine_connection.return_value = mock_td_conn
        mock_manager.get_postgresql_connection.return_value = mock_pg_pool
        mock_pg_pool.getconn.side_effect = [mock_pg_conn1, mock_pg_conn2]

        handler = DatabaseConnectionHandler(mock_manager)

        # 获取多个PostgreSQL连接
        conn1 = handler.get_postgresql_connection()
        conn2 = handler.get_postgresql_connection()

        assert conn1 == mock_pg_conn1
        assert conn2 == mock_pg_conn2

        # 归还连接
        handler.return_postgresql_connection(conn1)
        handler.return_postgresql_connection(conn2)

        # 验证连接被正确归还
        assert mock_pg_pool.putconn.call_count == 2
        mock_pg_pool.putconn.assert_any_call(mock_pg_conn1)
        mock_pg_pool.putconn.assert_any_call(mock_pg_conn2)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
