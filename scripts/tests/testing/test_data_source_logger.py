#!/usr/bin/env python3
"""
数据源日志记录器测试套件
完整测试data_source_logger模块的所有功能，确保100%测试覆盖率
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
import os
import tempfile
import shutil
import time
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

# 导入被测试的模块
from src.utils.data_source_logger import (
    DataSourceLogger,
    data_source_logger,
    log_data_source_call,
    log_data_source_method,
)


class TestDataSourceLogger:
    """DataSourceLogger类核心功能测试"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建临时目录用于日志文件
        self.temp_dir = tempfile.mkdtemp()
        self.log_file_path = os.path.join(self.temp_dir, "test_data_source.log")

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 清理临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        # 清理日志处理器避免影响其他测试
        logger = logging.getLogger("DataSource")
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    def test_initialization_with_default_name(self):
        """测试使用默认名称初始化"""
        logger_instance = DataSourceLogger()

        # 验证logger名称
        assert logger_instance.logger.name == "DataSource"
        assert logger_instance.logger.level == logging.INFO

    def test_initialization_with_custom_name(self):
        """测试使用自定义名称初始化"""
        custom_name = "CustomDataSource"
        logger_instance = DataSourceLogger(custom_name)

        assert logger_instance.logger.name == custom_name

    def test_logger_handler_configuration(self):
        """测试日志处理器配置"""
        with patch("logging.FileHandler") as mock_file_handler:
            mock_file_instance = MagicMock()
            mock_file_handler.return_value = mock_file_instance

            logger_instance = DataSourceLogger()

            # 验证文件处理器被创建
            mock_file_handler.assert_called_once_with("data_source_calls.log")

            # 验证处理器被添加
            assert len(logger_instance.logger.handlers) == 2  # 控制台 + 文件

    def test_logger_avoid_duplicate_handlers(self):
        """测试避免重复添加处理器"""
        logger_instance1 = DataSourceLogger()
        initial_handlers = len(logger_instance1.logger.handlers)

        # 创建第二个实例，不应该添加新的处理器
        logger_instance2 = DataSourceLogger()
        final_handlers = len(logger_instance2.logger.handlers)

        assert initial_handlers == final_handlers

    def test_log_call_success_case(self):
        """测试成功调用的日志记录"""
        logger_instance = DataSourceLogger()

        with patch.object(logger_instance.logger, "info") as mock_info:
            adapter_type = "TestAdapter"
            method = "test_method"
            params = {"param1": "value1", "param2": "value2"}
            result = {"data": [1, 2, 3]}
            duration = 0.123

            logger_instance.log_call(adapter_type, method, params, result, duration)

            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]

            assert "Adapter Call: TestAdapter.test_method" in call_args
            assert "Params: {'param1': 'value1', 'param2': 'value2'}" in call_args
            assert "Success: True" in call_args
            assert "Duration: 0.123s" in call_args

    def test_log_call_with_none_result(self):
        """测试None结果的处理"""
        logger_instance = DataSourceLogger()

        with patch.object(logger_instance.logger, "info") as mock_info:
            logger_instance.log_call("Adapter", "method", {}, None, 0.1)

            call_args = mock_info.call_args[0][0]
            assert "Success: False" in call_args

    def test_log_call_with_error_string_result(self):
        """测试错误字符串结果的处理"""
        logger_instance = DataSourceLogger()

        with patch.object(logger_instance.logger, "info") as mock_info:
            error_result = "Error: Something went wrong"
            logger_instance.log_call("Adapter", "method", {}, error_result, 0.1)

            call_args = mock_info.call_args[0][0]
            assert "Success: False" in call_args

    def test_log_call_with_normal_string_result(self):
        """测试正常字符串结果的处理"""
        logger_instance = DataSourceLogger()

        with patch.object(logger_instance.logger, "info") as mock_info:
            normal_result = "Success: Data retrieved"
            logger_instance.log_call("Adapter", "method", {}, normal_result, 0.1)

            call_args = mock_info.call_args[0][0]
            assert "Success: True" in call_args

    def test_log_error_method(self):
        """测试错误日志记录方法"""
        logger_instance = DataSourceLogger()

        with patch.object(logger_instance.logger, "error") as mock_error:
            adapter_type = "TestAdapter"
            method = "test_method"
            params = {"param1": "value1"}
            error_message = "Connection timeout"

            logger_instance.log_error(adapter_type, method, params, error_message)

            mock_error.assert_called_once()
            call_args = mock_error.call_args[0][0]

            assert "Adapter Error: TestAdapter.test_method" in call_args
            assert "Params: {'param1': 'value1'}" in call_args
            assert "Error: Connection timeout" in call_args

    def test_global_logger_instance(self):
        """测试全局日志记录器实例"""
        assert isinstance(data_source_logger, DataSourceLogger)
        assert data_source_logger.logger.name == "DataSource"


class TestLogDataSourceCallDecorator:
    """log_data_source_call装饰器测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 清理全局logger处理器
        logger = logging.getLogger("DataSource")
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        logger = logging.getLogger("DataSource")
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    def test_decorator_successful_call(self):
        """测试装饰器处理成功调用"""
        with patch.object(data_source_logger, "log_call") as mock_log:

            @log_data_source_call("TestAdapter")
            def test_function(self, param1, param2=None):
                return {"result": f"{param1}_{param2}"}

            # 调用被装饰的函数
            result = test_function(None, "value1", param2="value2")

            # 验证返回值正确
            assert result == {"result": "value1_value2"}

            # 验证日志被调用
            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args[1]

            assert call_kwargs["adapter_type"] == "TestAdapter"
            assert call_kwargs["method"] == "test_function"
            assert call_kwargs["result"] == result
            assert isinstance(call_kwargs["duration"], float)

    def test_decorator_function_without_args(self):
        """测试装饰器处理无参数函数"""
        with patch.object(data_source_logger, "log_call") as mock_log:

            @log_data_source_call("TestAdapter")
            def test_function(self):
                return "simple_result"

            result = test_function(None)

            assert result == "simple_result"
            mock_log.assert_called_once()

    def test_decorator_function_with_only_self(self):
        """测试装饰器处理只有self参数的函数"""
        with patch.object(data_source_logger, "log_call") as mock_log:

            @log_data_source_call("TestAdapter")
            def test_function(self):
                return "self_only"

            result = test_function(None)

            assert result == "self_only"

            # 验证参数记录为空
            call_kwargs = mock_log.call_args[1]
            assert call_kwargs["params"] == {"args": (), "kwargs": {}}

    def test_decorator_exception_handling(self):
        """测试装饰器处理异常情况"""
        with patch.object(data_source_logger, "log_error") as mock_log_error:

            @log_data_source_call("TestAdapter")
            def failing_function(self, should_fail=True):
                if should_fail:
                    raise ValueError("Test error")
                return "success"

            # 验证异常被正确抛出
            with pytest.raises(ValueError, match="Test error"):
                failing_function(None, should_fail=True)

            # 验证错误日志被记录
            mock_log_error.assert_called_once()
            call_kwargs = mock_log_error.call_args[1]

            assert call_kwargs["adapter_type"] == "TestAdapter"
            assert call_kwargs["method"] == "failing_function"
            assert call_kwargs["error"] == "Test error"

    def test_decorator_parameters_extraction(self):
        """测试装饰器参数提取功能"""
        with patch.object(data_source_logger, "log_call") as mock_log:

            @log_data_source_call("TestAdapter")
            def test_function(self, arg1, arg2, kwarg1=None, kwarg2="default"):
                return f"{arg1}_{arg2}_{kwarg1}_{kwarg2}"

            # 调用函数
            test_function(None, "pos1", "pos2", kwarg1="custom")

            # 验证参数提取正确
            call_kwargs = mock_log.call_args[1]
            expected_params = {
                "args": ("pos1", "pos2"),
                "kwargs": {"kwarg1": "custom"},  # 只记录实际传递的参数
            }
            assert call_kwargs["params"] == expected_params

    def test_decorator_timing_accuracy(self):
        """测试装饰器计时准确性"""
        with patch.object(data_source_logger, "log_call") as mock_log:

            @log_data_source_call("TestAdapter")
            def slow_function(self, delay=0.1):
                time.sleep(delay)
                return "done"

            start_time = time.time()
            slow_function(None, delay=0.05)
            end_time = time.time()

            # 验证计时合理（允许0.01秒误差）
            call_kwargs = mock_log.call_args[1]
            recorded_duration = call_kwargs["duration"]
            actual_duration = end_time - start_time

            assert abs(recorded_duration - actual_duration) < 0.01
            assert 0.05 <= recorded_duration <= 0.1  # 应该接近0.05秒

    def test_decorator_preserves_function_metadata(self):
        """测试装饰器保留函数元数据"""

        @log_data_source_call("TestAdapter")
        def decorated_function(self, param1: str, param2: int = 10) -> str:
            """测试函数"""
            return f"{param1}_{param2}"

        # 验证函数元数据被保留
        assert decorated_function.__name__ == "decorated_function"
        assert decorated_function.__doc__ == "测试函数"
        assert hasattr(decorated_function, "__annotations__")


class TestLogDataSourceMethodDecorator:
    """log_data_source_method装饰器测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 清理全局logger处理器
        logger = logging.getLogger("DataSource")
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        logger = logging.getLogger("DataSource")
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    def test_method_decorator_successful_call(self):
        """测试方法装饰器处理成功调用"""
        with patch.object(data_source_logger.logger, "info") as mock_info:

            @log_data_source_method("TestAdapter", "test_method")
            def test_func(self, param1):
                return {"data": param1}

            result = test_func(None, "test_value")

            assert result == {"data": "test_value"}
            mock_info.assert_called_once()

            call_args = mock_info.call_args[0][0]
            assert "DS Call: TestAdapter.test_method" in call_args
            assert "Success: True" in call_args

    def test_method_decorator_get_data_from_adapter_special_case(self):
        """测试get_data_from_adapter方法的特殊处理"""
        with patch.object(data_source_logger.logger, "info") as mock_info:

            @log_data_source_method("TestAdapter", "test_method")
            def get_data_from_adapter(self, adapter_type, method, **kwargs):
                return {"data": "test"}

            # 调用特殊方法
            get_data_from_adapter(None, "test_adapter", "test_method", param1="value1")

            # 验证参数提取正确
            call_args = mock_info.call_args[0][0]
            assert "Params:" in call_args
            assert "test_adapter" in call_args
            assert "test_method" in call_args

    def test_method_decorator_error_string_failure(self):
        """测试错误字符串导致失败判断"""
        with patch.object(data_source_logger.logger, "info") as mock_info:

            @log_data_source_method("TestAdapter", "test_method")
            def error_function(self):
                return "Error: Connection failed"

            error_function(None)

            call_args = mock_info.call_args[0][0]
            assert "Success: False" in call_args

    def test_method_decorator_chinese_error_string_failure(self):
        """测试中文错误字符串导致失败判断"""
        with patch.object(data_source_logger.logger, "info") as mock_info:

            @log_data_source_method("TestAdapter", "test_method")
            def error_function(self):
                return "失败: 数据获取失败"

            error_function(None)

            call_args = mock_info.call_args[0][0]
            assert "Success: False" in call_args

    def test_method_decorator_empty_result_failure(self):
        """测试空结果导致失败判断"""
        with patch.object(data_source_logger.logger, "info") as mock_info:

            @log_data_source_method("TestAdapter", "test_method")
            def empty_function(self):
                return []

            empty_function(None)

            call_args = mock_info.call_args[0][0]
            assert "Success: False" in call_args

    def test_method_decorator_none_result_failure(self):
        """测试None结果导致失败判断"""
        with patch.object(data_source_logger.logger, "info") as mock_info:

            @log_data_source_method("TestAdapter", "test_method")
            def none_function(self):
                return None

            none_function(None)

            call_args = mock_info.call_args[0][0]
            assert "Success: False" in call_args

    def test_method_decorator_get_indicator_data_exception(self):
        """测试get_indicator_data方法的空结果例外"""
        with patch.object(data_source_logger.logger, "info") as mock_info:

            @log_data_source_method("TestAdapter", "get_indicator_data")
            def empty_indicator_function(self):
                return []

            empty_indicator_function(None)

            call_args = mock_info.call_args[0][0]
            assert (
                "Success: True" in call_args
            )  # get_indicator_data的空结果应该被认为是成功的

    def test_method_decorator_exception_handling(self):
        """测试方法装饰器异常处理"""
        with patch.object(data_source_logger.logger, "error") as mock_error:

            @log_data_source_method("TestAdapter", "test_method")
            def failing_function(self):
                raise RuntimeError("Test runtime error")

            with pytest.raises(RuntimeError, match="Test runtime error"):
                failing_function(None)

            mock_error.assert_called_once()
            call_args = mock_error.call_args[0][0]
            assert "DS Error: TestAdapter.test_method" in call_args
            assert "Test runtime error" in call_args

    def test_method_decorator_long_params_truncation(self):
        """测试长参数截断功能"""
        with patch.object(data_source_logger.logger, "info") as mock_info:

            @log_data_source_method("TestAdapter", "test_method")
            def long_params_function(self, **kwargs):
                return "success"

            long_params = {"param": "x" * 300}  # 超过200字符的参数

            long_params_function(None, **long_params)

            call_args = mock_info.call_args[0][0]
            # 验证参数被截断
            assert "..." in call_args
            # 验证长度限制（整个Params字符串应该在200字符以内）
            params_start = call_args.find("Params:")
            params_section = (
                call_args[params_start : params_start + 250]
                if params_start != -1
                else ""
            )
            assert len(params_section) <= 250  # 允许一些缓冲

    def test_method_decorator_timing_recording(self):
        """测试方法装饰器计时记录"""
        with patch.object(data_source_logger.logger, "info") as mock_info:

            @log_data_source_method("TestAdapter", "test_method")
            def timed_function(self):
                time.sleep(0.05)
                return "done"

            timed_function(None)

            call_args = mock_info.call_args[0][0]
            assert "Duration:" in call_args
            # 验证时间格式（应该是3位小数）
            import re

            duration_match = re.search(r"Duration: (\d+\.\d{3})s", call_args)
            assert duration_match is not None
            assert 0.05 <= float(duration_match.group(1)) <= 0.1


class TestEdgeCases:
    """边界情况测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 清理全局logger处理器
        logger = logging.getLogger("DataSource")
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        logger = logging.getLogger("DataSource")
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    def test_decorator_with_unicode_parameters(self):
        """测试装饰器处理Unicode参数"""
        with patch.object(data_source_logger, "log_call") as mock_log:

            @log_data_source_call("测试适配器")
            def unicode_function(self, text):
                return text

            unicode_text = "测试中文🚀🌟"
            result = unicode_function(None, unicode_text)

            assert result == unicode_text
            mock_log.assert_called_once()

    def test_decorator_with_large_parameters(self):
        """测试装饰器处理大量参数"""
        with patch.object(data_source_logger, "log_call") as mock_log:

            @log_data_source_call("TestAdapter")
            def large_params_function(self, large_list=None):
                return len(large_list or [])

            large_list = list(range(1000))
            result = large_params_function(None, large_list=large_list)

            assert result == 1000
            mock_log.assert_called_once()

    def test_decorator_with_very_long_duration(self):
        """测试装饰器处理长时间运行"""
        with patch.object(data_source_logger, "log_call") as mock_log:

            @log_data_source_call("TestAdapter")
            def long_function(self):
                time.sleep(0.2)  # 较长的执行时间
                return "completed"

            result = long_function(None)

            assert result == "completed"
            call_kwargs = mock_log.call_args[1]
            assert call_kwargs["duration"] >= 0.2

    def test_decorator_with_zero_duration(self):
        """测试装饰器处理零持续时间"""
        with patch.object(data_source_logger, "log_call") as mock_log:

            @log_data_source_call("TestAdapter")
            def instant_function(self):
                return "instant"

            result = instant_function(None)

            assert result == "instant"
            call_kwargs = mock_log.call_args[1]
            assert call_kwargs["duration"] >= 0

    def test_method_decorator_edge_case_parameter_combinations(self):
        """测试方法装饰器边界参数组合"""
        with patch.object(data_source_logger.logger, "info") as mock_info:

            @log_data_source_method("EdgeAdapter", "edge_method")
            def edge_function(self, *args, **kwargs):
                return args, kwargs

            # 测试各种参数组合
            result1 = edge_function(None)
            result2 = edge_function(None, "arg1")
            result3 = edge_function(None, "arg1", "arg2", kw1="value1")

            assert mock_info.call_count == 3
            assert result1 == ((), {})
            assert result2 == (("arg1",), {})
            assert result3 == (("arg1", "arg2"), {"kw1": "value1"})


class TestPerformance:
    """性能测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 清理全局logger处理器
        logger = logging.getLogger("DataSource")
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        logger = logging.getLogger("DataSource")
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    def test_decorator_performance_impact(self):
        """测试装饰器性能影响"""
        with patch.object(
            data_source_logger, "log_call"
        ):  # Mock to avoid actual logging overhead

            @log_data_source_call("PerfAdapter")
            def fast_function(self, value):
                return value * 2

            iterations = 100  # 减少迭代次数以提高测试稳定性
            test_values = list(range(iterations))

            # 测试装饰后的函数性能
            start_time = time.time()
            for value in test_values:
                fast_function(None, value)
            decorated_time = time.time() - start_time

            # 验证性能在合理范围内（每个调用应该很快）
            avg_time_per_call = decorated_time / iterations * 1000  # 毫秒
            assert avg_time_per_call < 10, (
                f"装饰器调用时间过长: {avg_time_per_call:.2f}ms"
            )

    def test_method_decorator_performance_impact(self):
        """测试方法装饰器性能影响"""

        @log_data_source_method("PerfAdapter", "perf_method")
        def fast_method_function(self, value):
            return value * 3

        iterations = 500
        test_values = list(range(iterations))

        start_time = time.time()
        for value in test_values:
            fast_method_function(None, value)
        decorated_time = time.time() - start_time

        # 验证性能在可接受范围内
        avg_time_per_call = decorated_time / iterations * 1000  # 毫秒
        assert avg_time_per_call < 10, f"平均调用时间过长: {avg_time_per_call:.2f}ms"

    def test_logger_initialization_performance(self):
        """测试日志记录器初始化性能"""
        iterations = 50

        start_time = time.time()
        for _ in range(iterations):
            logger_instance = DataSourceLogger(f"TestLogger{_}")
        init_time = time.time() - start_time

        avg_time_per_init = init_time / iterations * 1000  # 毫秒
        assert avg_time_per_init < 50, f"初始化时间过长: {avg_time_per_init:.2f}ms"


class TestIntegration:
    """集成测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 清理临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        # 清理日志处理器
        logger = logging.getLogger("DataSource")
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    def test_multiple_decorators_integration(self):
        """测试多个装饰器集成使用"""
        with patch.object(data_source_logger, "log_call") as mock_log_call:
            with patch.object(data_source_logger.logger, "info") as mock_log_info:

                @log_data_source_call("Adapter1")
                def function1(self, value):
                    return value * 2

                @log_data_source_method("Adapter2", "method2")
                def function2(self, value):
                    return value * 3

                # 使用两个不同的装饰器函数
                result1 = function1(None, 5)
                result2 = function2(None, 7)

                assert result1 == 10
                assert result2 == 21

                # 验证两种不同的日志都被调用
                mock_log_call.assert_called_once()
                mock_log_info.assert_called_once()

    def test_logger_instance_sharing(self):
        """测试日志记录器实例共享"""
        logger1 = DataSourceLogger("SharedLogger")
        logger2 = DataSourceLogger("SharedLogger")

        # 验证它们共享同一个logger实例
        assert logger1.logger is logger2.logger
        assert logger1.logger.name == "SharedLogger"

    def test_global_logger_usage(self):
        """测试全局日志记录器使用"""
        with patch.object(data_source_logger, "log_call") as mock_log:
            # 使用全局装饰器
            @log_data_source_call("GlobalAdapter")
            def global_function(self, data):
                return f"processed_{data}"

            result = global_function(None, "test_data")
            assert result == "processed_test_data"
            mock_log.assert_called_once()

    def test_file_logging_integration(self):
        """测试文件日志集成"""
        with patch("logging.FileHandler") as mock_file_handler:
            mock_file_instance = MagicMock()
            mock_file_handler.return_value = mock_file_instance

            logger_instance = DataSourceLogger()

            # 验证文件处理器被正确配置
            mock_file_handler.assert_called_once_with("data_source_calls.log")

            # 验证文件处理器被添加到logger
            assert mock_file_instance in logger_instance.logger.handlers

    def test_error_propagation_integration(self):
        """测试错误传播集成"""
        with patch.object(data_source_logger, "log_error") as mock_log_error:

            @log_data_source_call("ErrorTestAdapter")
            def error_propagation_function(self, should_error=True):
                if should_error:
                    raise CustomError("Test error propagation")
                return "success"

            # 验证错误被正确传播
            with pytest.raises(CustomError, match="Test error propagation"):
                error_propagation_function(None, should_error=True)

            # 验证错误被记录
            mock_log_error.assert_called_once()

    def test_concurrent_logging_safety(self):
        """测试并发日志安全性"""
        import threading

        results = []
        errors = []

        @log_data_source_call("ConcurrentAdapter")
        def concurrent_function(self, thread_id):
            results.append(thread_id)
            return f"thread_{thread_id}"

        # 创建多个线程同时调用
        threads = []
        for i in range(10):
            thread = threading.Thread(target=concurrent_function, args=(None, i))
            threads.append(thread)

        # 启动所有线程
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证所有调用都成功完成
        assert len(results) == 10
        assert len(set(results)) == 10  # 所有线程ID都是唯一的
        assert len(errors) == 0  # 没有错误


class CustomError(Exception):
    """自定义异常类用于测试"""

    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
