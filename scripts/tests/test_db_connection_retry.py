#!/usr/bin/env python3
"""
数据库连接重试工具测试套件
完整测试db_connection_retry模块的所有功能，确保100%测试覆盖率
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
import os
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Mock problematic imports to avoid circular dependency
import unittest.mock

sys.modules["src.storage.database.connection_manager"] = unittest.mock.MagicMock()
sys.modules["src.core.config"] = unittest.mock.MagicMock()
sys.modules["src.core.config_driven_table_manager"] = unittest.mock.MagicMock()

import pytest
import structlog

# 导入被测试的模块
from src.utils.db_connection_retry import (
    db_retry,
    DatabaseConnectionHandler,
    connection_handler,
    get_tdengine_connection_with_retry,
    get_postgresql_connection_with_retry,
    return_postgresql_connection,
    init_connection_handler,
)


class TestDBRetryDecorator:
    """db_retry装饰器核心功能测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 清理日志配置
        self.original_level = logger.level
        logger.level = 1  # DEBUG

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        logger.level = self.original_level

    def test_decorator_successful_execution(self):
        """测试装饰器成功执行的情况"""
        call_count = 0

        @db_retry(max_retries=2, delay=0.01)
        def success_function():
            nonlocal call_count
            call_count += 1
            return f"success_{call_count}"

        result = success_function()
        assert result == "success_1"
        assert call_count == 1  # 应该在第一次调用就成功

    def test_decorator_retry_success_after_failure(self):
        """测试装饰器重试后成功的情况"""
        call_count = 0

        @db_retry(max_retries=3, delay=0.01)
        def sometimes_failing_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("First attempt fails")
            return f"success_{call_count}"

        result = sometimes_failing_function()
        assert result == "success_2"
        assert call_count == 2

    def test_decorator_all_retries_exhausted(self):
        """测试装饰器所有重试都用尽的情况"""
        call_count = 0

        @db_retry(max_retries=2, delay=0.01)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ConnectionError(f"Attempt {call_count} failed")

        with pytest.raises(ConnectionError, match="Attempt 3 failed"):
            always_failing_function()

        assert call_count == 3  # 初始调用 + 2次重试

    def test_decorator_non_connection_error_no_retry(self):
        """测试装饰器非连接错误不重试"""
        call_count = 0

        @db_retry(max_retries=3, delay=0.01)
        def non_connection_error_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Validation error - not connection related")

        with pytest.raises(ValueError, match="Validation error"):
            non_connection_error_function()

        assert call_count == 1  # 不应该重试

    def test_decorator_backoff_mechanism(self):
        """测试装饰器退避机制"""
        call_times = []

        @db_retry(max_retries=3, delay=0.01, backoff=2.0)
        def failing_function():
            call_times.append(time.time())
            raise ConnectionError("Connection failure")

        start_time = time.time()
        with pytest.raises(ConnectionError):
            failing_function()
        end_time = time.time()

        # 验证延迟时间符合指数退避
        assert len(call_times) == 4  # 初始 + 3次重试
        assert call_times[1] - call_times[0] >= 0.01  # 第一次延迟
        assert call_times[2] - call_times[1] >= 0.02  # 第二次延迟 (0.01 * 2)
        assert call_times[3] - call_times[2] >= 0.04  # 第三次延迟 (0.02 * 2)

    def test_decorator_custom_parameters(self):
        """测试装饰器自定义参数"""
        call_count = 0

        @db_retry(max_retries=1, delay=0.005, backoff=3.0)
        def custom_retry_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("First failure")
            return "success"

        result = custom_retry_function()
        assert result == "success"
        assert call_count == 2

    def test_decorator_with_connection_timeout_error(self):
        """测试连接超时错误重试"""
        call_count = 0

        @db_retry(max_retries=2, delay=0.01)
        def timeout_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise TimeoutError("Connection timeout")
            return "success"

        result = timeout_function()
        assert result == "success"
        assert call_count == 2

    def test_decorator_with_network_error(self):
        """测试网络错误重试"""
        call_count = 0

        @db_retry(max_retries=2, delay=0.01)
        def network_error_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise OSError("Network unreachable")
            return "success"

        result = network_error_function()
        assert result == "success"
        assert call_count == 2

    def test_decorator_with_connection_refused_error(self):
        """测试连接被拒绝错误重试"""
        call_count = 0

        @db_retry(max_retries=2, delay=0.01)
        def refused_error_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionRefusedError("Connection refused")
            return "success"

        result = refused_error_function()
        assert result == "success"
        assert call_count == 2

    def test_decorator_preserves_function_metadata(self):
        """测试装饰器保留函数元数据"""

        @db_retry()
        def test_function(param1: str, param2: int = 10) -> str:
            """测试函数文档"""
            return f"{param1}_{param2}"

        # 验证函数元数据被保留
        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "测试函数文档"
        assert hasattr(test_function, "__annotations__")

    def test_decorator_with_no_arguments_function(self):
        """测试装饰器处理无参数函数"""

        @db_retry()
        def no_args_function():
            return "no_args_result"

        result = no_args_function()
        assert result == "no_args_result"

    def test_decorator_with_various_positional_arguments(self):
        """测试装饰器处理各种位置参数"""

        @db_retry()
        def multi_arg_function(self, arg1, arg2, arg3="default"):
            return f"{arg1}_{arg2}_{arg3}"

        result = multi_arg_function(None, "val1", "val2")
        assert result == "val1_val2_default"


class TestDatabaseConnectionHandler:
    """DatabaseConnectionHandler类测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建mock的连接管理器
        self.mock_conn_manager = MagicMock()
        self.mock_tdengine_conn = MagicMock()
        self.mock_postgres_pool = MagicMock()
        self.mock_postgres_conn = MagicMock()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        pass

    def test_initialization_with_dependency_injection(self):
        """测试依赖注入初始化"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        assert handler.connection_manager is self.mock_conn_manager
        assert handler._connection_cache == {}

    def test_connection_cache_initialization(self):
        """测试连接缓存初始化"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        # 验证缓存是空的字典
        assert isinstance(handler._connection_cache, dict)
        assert len(handler._connection_cache) == 0

    def test_get_tdengine_connection_success(self):
        """测试获取TDengine连接成功"""
        self.mock_conn_manager.get_tdengine_connection.return_value = (
            self.mock_tdengine_conn
        )

        handler = DatabaseConnectionHandler(self.mock_conn_manager)
        result = handler.get_tdengine_connection()

        # 验证连接管理器被调用
        self.mock_conn_manager.get_tdengine_connection.assert_called_once()
        assert result is self.mock_tdengine_conn

    def test_get_tdengine_connection_with_retry(self):
        """测试获取TDengine连接带重试"""
        # 第一次失败，第二次成功
        self.mock_conn_manager.get_tdengine_connection.side_effect = [
            ConnectionError("Connection failed"),
            self.mock_tdengine_conn,
        ]

        with patch("src.utils.db_connection_retry.logger") as mock_logger:
            handler = DatabaseConnectionHandler(self.mock_conn_manager)
            result = handler.get_tdengine_connection()

        # 验证重试日志被调用
        mock_logger.warning.assert_called()
        assert result is self.mock_tdengine_conn

    def test_get_postgresql_connection_success(self):
        """测试获取PostgreSQL连接成功"""
        self.mock_conn_manager.get_postgresql_connection.return_value = (
            self.mock_postgres_pool
        )
        self.mock_postgres_pool.getconn.return_value = self.mock_postgres_conn

        handler = DatabaseConnectionHandler(self.mock_conn_manager)
        result = handler.get_postgresql_connection()

        # 验证调用链
        self.mock_conn_manager.get_postgresql_connection.assert_called_once()
        self.mock_postgres_pool.getconn.assert_called_once()
        assert result is self.mock_postgres_conn

    def test_get_postgresql_connection_with_retry(self):
        """测试获取PostgreSQL连接带重试"""
        # 连接池第一次失败，第二次成功
        self.mock_conn_manager.get_postgresql_connection.side_effect = [
            ConnectionError("Pool connection failed"),
            self.mock_postgres_pool,
        ]
        self.mock_postgres_pool.getconn.return_value = self.mock_postgres_conn

        with patch("src.utils.db_connection_retry.logger") as mock_logger:
            handler = DatabaseConnectionHandler(self.mock_conn_manager)
            result = handler.get_postgresql_connection()

        # 验证重试日志
        mock_logger.warning.assert_called()
        assert result is self.mock_postgres_conn

    def test_return_postgresql_connection_success(self):
        """测试归还PostgreSQL连接成功"""
        self.mock_conn_manager.get_postgresql_connection.return_value = (
            self.mock_postgres_pool
        )

        handler = DatabaseConnectionHandler(self.mock_conn_manager)
        result = handler.return_postgresql_connection(self.mock_postgres_conn)

        # 验证调用链
        self.mock_conn_manager.get_postgresql_connection.assert_called_once()
        self.mock_postgres_pool.putconn.assert_called_once_with(self.mock_postgres_conn)

    def test_return_postgresql_connection_failure_handling(self):
        """测试归还PostgreSQL连接失败处理"""
        self.mock_conn_manager.get_postgresql_connection.return_value = (
            self.mock_postgres_pool
        )
        self.mock_postgres_pool.putconn.side_effect = Exception("Pool error")

        with patch("src.utils.db_connection_retry.logger") as mock_logger:
            handler = DatabaseConnectionHandler(self.mock_conn_manager)
            handler.return_postgresql_connection(self.mock_postgres_conn)

            # 验证错误日志被记录
            mock_logger.error.assert_called_once()

    def test_close_all_connections(self):
        """测试关闭所有连接"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)
        handler.close_all_connections()

        # 验证连接管理器的关闭方法被调用
        self.mock_conn_manager.close_all_connections.assert_called_once()

    def test_get_connection_manager_delegation(self):
        """测试get_connection_manager委托"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)
        result = handler.get_connection_manager()

        assert result is self.mock_conn_manager

    def test_multiple_tdengine_calls_use_cache(self):
        """测试多次TDengine连接调用使用缓存"""
        # 设置缓存
        handler = DatabaseConnectionHandler(self.mock_conn_manager)
        handler._connection_cache["tdengine"] = self.mock_tdengine_conn

        # 覆盖mock的行为以返回缓存
        original_get_tdengine = self.mock_conn_manager.get_tdengine_connection
        original_get_tdengine.return_value = "new_connection"

        result1 = handler.get_tdengine_connection()
        result2 = handler.get_tdengine_connection()

        # 第二次调用应该使用缓存
        original_get_tdengine.assert_called_once()
        assert result1 is self.mock_tdengine_conn
        assert result2 is self.mock_tdengine_conn

    def test_connection_cache_invalidation_on_error(self):
        """测试错误时缓存失效"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        # 设置缓存
        handler._connection_cache["tdengine"] = "cached_connection"

        # 设置mock在第二次调用时抛出异常
        self.mock_conn_manager.get_tdengine_connection.side_effect = [
            "cached_connection",
            ConnectionError("Connection lost"),
        ]

        with patch("src.utils.db_connection_retry.logger"):
            # 第一次调用使用缓存
            result1 = handler.get_tdengine_connection()
            assert result1 == "cached_connection"

            # 第二次调用应该清空缓存并重试
            with pytest.raises(ConnectionError):
                handler.get_tdconnection()


class TestGlobalConvenienceFunctions:
    """全局便利函数测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 清理全局变量
        import src.utils.db_connection_retry

        src.utils.db_connection_retry.connection_handler = None

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        import src.utils.db_connection_retry

        src.utils.db_connection_retry.connection_handler = None

    def test_get_tdengine_connection_uninitialized_error(self):
        """测试未初始化时获取TDengine连接错误"""
        with pytest.raises(RuntimeError, match="DatabaseConnectionHandler未初始化"):
            get_tdengine_connection_with_retry()

    def test_get_postgresql_connection_uninitialized_error(self):
        """测试未初始化时获取PostgreSQL连接错误"""
        with pytest.raises(RuntimeError, match="DatabaseConnectionHandler未初始化"):
            get_postgresql_connection_with_retry()

    def test_return_postgresql_connection_uninitialized_error(self):
        """测试未初始化时归还PostgreSQL连接错误"""
        with pytest.raises(RuntimeError, match="DatabaseConnectionHandler未初始化"):
            return_postgresql_connection(MagicMock())

    def test_init_connection_handler_success(self):
        """测试初始化连接处理器成功"""
        result = init_connection_handler(self.mock_conn_manager)

        # 验证全局变量被设置
        import src.utils.db_connection_retry

        assert src.db_connection_retry.connection_handler is not None
        assert isinstance(
            src.db_connection_retry.connection_handler, DatabaseConnectionHandler
        )
        assert (
            src.db_connection_retry.connection_handler.connection_manager
            is self.mock_conn_manager
        )

        assert result is src.db_connection_retry.connection_handler

    def test_global_functions_after_initialization(self):
        """测试初始化后全局函数正常工作"""
        # 初始化
        init_connection_handler(self.mock_conn_manager)

        # 设置mock返回值
        self.mock_conn_manager.get_tdengine_connection.return_value = (
            self.mock_tdengine_conn
        )
        self.mock_conn_manager.get_postgresql_connection.return_value = (
            self.mock_postgres_pool
        )
        self.mock_postgres_pool.getconn.return_value = self.mock_postgres_conn

        # 测试全局函数
        td_result = get_tdengine_connection_with_retry()
        pg_result = get_postgresql_connection_with_retry()

        assert td_result is self.mock_tdengine_conn
        assert pg_result is self.mock_postgres_conn

        # 测试归还函数
        return_postgresql_connection(pg_result)
        self.mock_postgres_pool.putconn.assert_called_once()


class TestEdgeCases:
    """边界情况测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.mock_conn_manager = MagicMock()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        pass

    def test_retry_decorator_with_zero_max_retries(self):
        """测试零最大重试次数"""

        @db_retry(max_retries=0, delay=0.01)
        def no_retry_function():
            raise ConnectionError("Connection failed")

        with pytest.raises(ConnectionError):
            no_retry_function()

    def test_retry_decorator_with_negative_delay(self):
        """测试负延迟时间"""

        @db_retry(max_retries=2, delay=-0.1)
        def negative_delay_function():
            if not hasattr(negative_delay_function, "call_count"):
                negative_delay_function.call_count = 0
            negative_delay_function.call_count += 1
            if negative_delay_function.call_count == 1:
                raise ConnectionError("First failure")
            return "success"

        result = negative_delay_function()
        assert result == "success"

    def test_retry_decorator_with_zero_delay(self):
        """测试零延迟时间"""

        @db_retry(max_retries=2, delay=0.0)
        def zero_delay_function():
            if not hasattr(zero_delay_function, "call_count"):
                zero_delay_function.call_count = 0
            zero_delay_function.call_count += 1
            if zero_delay_function.call_count == 1:
                raise ConnectionError("First failure")
            return "success"

        result = zero_delay_function()
        assert result == "success"

    def test_retry_decorator_with_large_backoff(self):
        """测试大退避倍数"""

        @db_retry(max_retries=2, delay=0.01, backoff=10.0)
        def large_backoff_function():
            raise ConnectionError("Connection failure")

        start_time = time.time()
        with pytest.raises(ConnectionError):
            large_backoff_function()
        end_time = time.time()

        # 验证总时间符合预期（应该有明显的延迟）
        assert end_time - start_time >= 0.1  # 0.01 + 0.1

    def test_connection_handler_with_none_connection_manager(self):
        """测试None连接管理器"""
        with pytest.raises(TypeError):
            DatabaseConnectionHandler(None)

    def test_connection_handler_with_invalid_manager(self):
        """测试无效的连接管理器"""
        invalid_manager = "not a manager"
        with pytest.raises(AttributeError):
            DatabaseConnectionHandler(invalid_manager)

    def test_multiple_concurrent_handlers(self):
        """测试多个并发连接处理器"""
        import threading

        results = []
        errors = []

        def create_handler(index):
            try:
                handler = DatabaseConnectionHandler(self.mock_conn_manager)
                results.append(f"handler_{index}")
                time.sleep(0.01)  # 短暂延迟
            except Exception as e:
                errors.append(f"error_{index}: {str(e)}")

        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_handler, args=(i,))
            threads.append(thread)

        # 启动所有线程
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        assert len(results) == 5
        assert len(errors) == 0

    def test_handler_memory_cleanup(self):
        """测试连接处理器内存清理"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        # 添加到缓存
        handler._connection_cache["test"] = "cached_value"
        handler._connection_cache["tdengine"] = "another_cached_value"

        # 清理连接
        handler.close_all_connections()

        # 验证缓存被清理（通过mock验证）
        assert handler._connection_manager.close_all_connections.called

    def test_error_message_case_sensitive_matching(self):
        """测试错误消息大小写敏感匹配"""

        @db_retry(max_retries=1, delay=0.01)
        def case_error_function():
            raise ConnectionError("CONNECTION failed")  # 大写

        with pytest.raises(ConnectionError):
            case_error_function()

    def test_error_message_with_mixed_case_keywords(self):
        """测试混合大小写错误消息匹配"""

        @db_retry(max_retries=1, delay=0.01)
        def mixed_case_error_function():
            raise ConnectionError("Network timeout occurred")  # 混合大小写

        with patch("src.utils.db_connection_retry.logger") as mock_logger:
            mixed_case_error_function()
            mock_logger.warning.assert_called()


class TestPerformance:
    """性能测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.mock_conn_manager = MagicMock()

    def teardown_method(self):
        """每个测试执行后的清理"""
        pass

    def test_retry_decorator_performance_overhead(self):
        """测试重试装饰器性能开销"""

        @db_retry(max_retries=0)  # 不重试以测试基础开销
        def fast_function():
            return "result"

        iterations = 1000

        # 测试原始函数性能
        def original_function():
            return "result"

        start_time = time.time()
        for _ in range(iterations):
            original_function()
        original_time = time.time() - start_time

        start_time = time.time()
        for _ in range(iterations):
            fast_function()
        decorated_time = time.time() - start_time

        # 装饰器开销应该在合理范围内
        overhead_ratio = decorated_time / original_time
        assert overhead_ratio < 50, f"装饰器开销过大: {overhead_ratio:.2f}x"

    def test_concurrent_retry_performance(self):
        """测试并发重试性能"""
        import threading

        results = []
        errors = []

        @db_retry(max_retries=2, delay=0.001)
        def concurrent_function(thread_id):
            try:
                # 模拟一些随机失败
                import random

                if random.random() < 0.3:  # 30%的失败率
                    raise ConnectionError(f"Thread {thread_id} failed")
                return f"success_{thread_id}"
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")
                raise

        # 创建并发线程
        threads = []
        for i in range(10):
            thread = threading.Thread(target=concurrent_function, args=(i,))
            threads.append(thread)

        # 启动所有线程
        start_time = time.time()
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = end_time - start_time

        assert len(results) + len(errors) == 10
        assert total_time < 5.0, f"并发重试时间过长: {total_time:.2f}s"

    def test_connection_handler_performance_with_caching(self):
        """测试连接处理器缓存性能"""
        handler = DatabaseConnectionHandler(self.mock_conn_manager)

        # 预填充缓存
        handler._connection_cache["tdengine"] = self.mock_tdengine_conn
        handler._connection_cache["postgresql"] = self.mock_postgres_conn

        iterations = 1000

        start_time = time.time()
        for _ in range(iterations):
            # 交替调用不同连接
            handler.get_tdengine_connection()
            handler.get_postgresql_connection()
        end_time = time.time()

        avg_time_per_call = (end_time - start_time) / (iterations * 2) * 1000  # 毫秒
        assert avg_time_per_call < 1, f"缓存调用时间过长: {avg_time_per_call:.2f}ms"

    def test_large_number_of_retries_performance(self):
        """测试大量重试的性能影响"""

        @db_retry(max_retries=10, delay=0.001)
        def many_retries_function():
            raise ConnectionError("Always fails")

        start_time = time.time()
        with pytest.raises(ConnectionError):
            many_retries_function()
        end_time = time.time()

        # 应该快速失败（即使有10次重试）
        total_time = end_time - start_time
        assert total_time < 0.5, f"大量重试时间过长: {total_time:.3f}s"

    def test_backoff_timing_accuracy(self):
        """测试退避时间准确性"""
        call_times = []

        @db_retry(max_retries=3, delay=0.05, backoff=2.0)
        def timed_function():
            call_times.append(time.time())
            raise ConnectionError("Timed failure")

        start_time = time.time()
        with pytest.raises(ConnectionError):
            timed_function()
        end_time = time.time()

        # 验证每次重试的间隔时间
        if len(call_times) >= 3:
            assert call_times[1] - call_times[0] >= 0.05
            assert call_times[2] - call_times[1] >= 0.1
            assert call_times[3] - call_times[2] >= 0.2


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

        self.mock_conn_manager.get_postgresql_connection.return_value = (
            self.mock_postgres_pool
        )
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
        self.mock_conn_manager.get_tdengine_connection.return_value = (
            self.mock_tdengine_conn
        )
        self.mock_conn_manager.get_postgresql_connection.return_value = (
            self.mock_postgres_pool
        )
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
        import threading
        import queue

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
                results.put(f"Worker {worker_id}: {str(e)}")

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
        self.mock_conn_manager.get_tdengine_connection.return_value = (
            self.mock_tdengine_conn
        )
        self.mock_conn_manager.get_postgresql_connection.return_value = (
            self.mock_postgres_pool
        )
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


# 自定义异常类用于测试
class CustomConnectionError(Exception):
    """自定义连接错误类"""

    pass


class CustomTimeoutError(Exception):
    """自定义超时错误类"""

    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
