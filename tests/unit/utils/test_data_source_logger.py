"""
Data Source Logger Test Suite
数据源日志记录测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.utils.data_source_logger (177行)
"""

import pytest
import logging
import time
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.utils.data_source_logger import (
    DataSourceLogger,
    data_source_logger,
    log_data_source_call,
    log_data_source_method,
)


class TestDataSourceLogger:
    """数据源日志记录器测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 清除日志记录
        self.log_records = []

        # 创建临时目录用于日志文件
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test_data_source.log")

        # 创建测试日志处理器
        self.test_handler = logging.Handler()
        self.test_handler.emit = self.capture_log

        # 获取测试logger并配置
        self.logger = logging.getLogger("test_data_source")
        self.logger.addHandler(self.test_handler)
        self.logger.setLevel(logging.INFO)

    def capture_log(self, record):
        """捕获日志记录"""
        self.log_records.append(record)

    def teardown_method(self):
        """每个测试方法后的清理"""
        self.logger.removeHandler(self.test_handler)
        self.log_records.clear()

        # 清理临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init_default_name(self):
        """测试默认名称初始化"""
        logger = DataSourceLogger()

        assert logger.logger.name == "DataSource"
        assert logger.logger.level == logging.INFO

    def test_init_custom_name(self):
        """测试自定义名称初始化"""
        logger = DataSourceLogger("CustomLogger")

        assert logger.logger.name == "CustomLogger"
        assert logger.logger.level == logging.INFO

    def test_init_avoids_duplicate_handlers(self):
        """测试避免重复添加处理器"""
        # 第一次创建
        logger1 = DataSourceLogger("test_no_duplicate")
        initial_handlers = len(logger1.logger.handlers)

        # 第二次创建同名logger
        logger2 = DataSourceLogger("test_no_duplicate")

        # 应该不会添加新的处理器
        assert len(logger2.logger.handlers) == initial_handlers

    @patch("logging.FileHandler")
    @patch("logging.StreamHandler")
    def test_init_handler_setup(self, mock_stream, mock_file):
        """测试处理器设置"""
        # Mock处理器实例
        mock_stream_handler = MagicMock()
        mock_file_handler = MagicMock()
        mock_stream.return_value = mock_stream_handler
        mock_file.return_value = mock_file_handler

        logger = DataSourceLogger("test_handler_setup")

        # 验证处理器被创建
        mock_stream.assert_called_once()
        mock_file.assert_called_once_with("data_source_calls.log")

        # 验证处理器被添加到logger
        assert mock_stream_handler in logger.logger.handlers
        assert mock_file_handler in logger.logger.handlers

    def test_log_call_success(self):
        """测试成功调用记录"""
        logger = DataSourceLogger("test_log_call")

        # 使用临时日志文件避免创建实际文件
        with patch("logging.FileHandler"):
            logger.log_call(
                adapter_type="TestAdapter",
                method="test_method",
                params={"symbol": "AAPL"},
                result={"data": [1, 2, 3]},
                duration=0.123,
            )

        # 验证调用成功（不会抛出异常）
        assert True

    def test_log_call_with_none_result(self):
        """测试None结果的处理"""
        logger = DataSourceLogger("test_log_none")

        with patch("logging.FileHandler"):
            logger.log_call(
                adapter_type="TestAdapter",
                method="test_method",
                params={},
                result=None,
                duration=0.456,
            )

        assert True

    def test_log_call_with_error_string(self):
        """测试错误字符串结果的处理"""
        logger = DataSourceLogger("test_log_error")

        with patch("logging.FileHandler"):
            logger.log_call(
                adapter_type="TestAdapter",
                method="test_method",
                params={},
                result="Error: something went wrong",
                duration=0.789,
            )

        assert True

    def test_log_call_with_normal_string(self):
        """测试普通字符串结果的处理"""
        logger = DataSourceLogger("test_log_string")

        with patch("logging.FileHandler"):
            logger.log_call(
                adapter_type="TestAdapter",
                method="test_method",
                params={},
                result="Success: data loaded",
                duration=0.234,
            )

        assert True

    def test_log_error(self):
        """测试错误记录"""
        logger = DataSourceLogger("test_log_error")

        with patch("logging.FileHandler"):
            logger.log_error(
                adapter_type="TestAdapter",
                method="test_method",
                params={"symbol": "GOOGL"},
                error="Connection timeout",
            )

        assert True

    def test_log_call_with_complex_params(self):
        """测试复杂参数的处理"""
        logger = DataSourceLogger("test_complex_params")

        complex_params = {
            "symbols": ["AAPL", "GOOGL", "MSFT"],
            "interval": "1m",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "options": {"adjust": "auto", "extended": True},
        }

        with patch("logging.FileHandler"):
            logger.log_call(
                adapter_type="ComplexAdapter",
                method="get_historical_data",
                params=complex_params,
                result={"status": "success", "count": 3000},
                duration=2.345,
            )

        assert True

    def test_log_call_with_various_durations(self):
        """测试不同持续时间的记录"""
        logger = DataSourceLogger("test_durations")

        durations = [0.001, 0.123, 1.456, 10.789, 0.0]

        with patch("logging.FileHandler"):
            for duration in durations:
                logger.log_call(
                    adapter_type="DurationTest",
                    method="test_method",
                    params={"duration": duration},
                    result=f"result_for_{duration}",
                    duration=duration,
                )

        assert True


class TestGlobalDataSourceLogger:
    """全局数据源日志记录器测试"""

    def test_global_logger_exists(self):
        """测试全局日志记录器存在"""
        assert data_source_logger is not None
        assert isinstance(data_source_logger, DataSourceLogger)
        assert data_source_logger.logger.name == "DataSource"

    def test_global_logger_functionality(self):
        """测试全局日志记录器功能"""
        with patch("logging.FileHandler"):
            # 测试日志记录功能正常工作
            data_source_logger.log_call(
                adapter_type="GlobalTest",
                method="test_method",
                params={"test": True},
                result={"success": True},
                duration=0.1,
            )

        assert True


class TestLogDataSourceCallDecorator:
    """数据源调用日志装饰器测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.log_records = []
        self.test_handler = logging.Handler()
        self.test_handler.emit = self.capture_log

        # 使用专用的测试logger
        self.logger = logging.getLogger("DataSource")
        self.logger.addHandler(self.test_handler)
        self.logger.setLevel(logging.INFO)

    def capture_log(self, record):
        """捕获日志记录"""
        self.log_records.append(record)

    def teardown_method(self):
        """每个测试方法后的清理"""
        self.logger.removeHandler(self.test_handler)
        self.log_records.clear()

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_decorator_successful_call(self, mock_logger):
        """测试装饰器成功调用"""
        # Mock日志记录器
        mock_logger.log_call = MagicMock()

        @log_data_source_call("TestAdapter")
        def test_function(self, param1, param2=None):
            return f"result_{param1}_{param2 or 'default'}"

        # 调用被装饰的函数
        result = test_function(None, "test_value", param2="extra")

        # 验证返回值正确
        assert result == "result_test_value_extra"

        # 验证日志记录被调用
        mock_logger.log_call.assert_called_once()
        call_args = mock_logger.log_call.call_args[1]

        assert call_args["adapter_type"] == "TestAdapter"
        assert call_args["method"] == "test_function"
        assert call_args["params"] == {
            "args": ("test_value",),
            "kwargs": {"param2": "extra"},
        }
        assert call_args["result"] == "result_test_value_extra"
        assert isinstance(call_args["duration"], float)

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_decorator_exception_handling(self, mock_logger):
        """测试装饰器异常处理"""
        # Mock日志记录器
        mock_logger.log_error = MagicMock()

        @log_data_source_call("ErrorTestAdapter")
        def failing_function(self, should_fail=True):
            if should_fail:
                raise ValueError("Test error")
            return "success"

        # 调用会失败的函数
        with pytest.raises(ValueError, match="Test error"):
            failing_function(None, should_fail=True)

        # 验证错误日志被记录
        mock_logger.log_error.assert_called_once()
        call_args = mock_logger.log_error.call_args[1]

        assert call_args["adapter_type"] == "ErrorTestAdapter"
        assert call_args["method"] == "failing_function"
        assert call_args["params"] == {"args": (), "kwargs": {"should_fail": True}}
        assert call_args["error"] == "Test error"

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_decorator_no_args_function(self, mock_logger):
        """测试装饰器处理无参数函数"""
        mock_logger.log_call = MagicMock()

        @log_data_source_call("NoArgsAdapter")
        def no_args_function(self):
            return "no_args_result"

        result = no_args_function(None)

        assert result == "no_args_result"
        mock_logger.log_call.assert_called_once()
        call_args = mock_logger.log_call.call_args[1]
        assert call_args["params"] == {"args": (), "kwargs": {}}

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_decorator_only_self_param(self, mock_logger):
        """测试装饰器处理只有self参数的函数"""
        mock_logger.log_call = MagicMock()

        @log_data_source_call("SelfOnlyAdapter")
        def self_only_function(self):
            return "self_only_result"

        result = self_only_function(None)

        assert result == "self_only_result"
        mock_logger.log_call.assert_called_once()
        call_args = mock_logger.log_call.call_args[1]
        assert call_args["params"] == {"args": (), "kwargs": {}}

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_decorator_preserves_function_metadata(self, mock_logger):
        """测试装饰器保留函数元数据"""
        mock_logger.log_call = MagicMock()

        @log_data_source_call("MetadataAdapter")
        def test_function(self, param1, param2):
            """测试函数文档字符串"""
            return f"result_{param1}_{param2}"

        # 验证函数元数据被保留
        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "测试函数文档字符串"

        # 调用函数确保正常工作
        result = test_function(None, "a", "b")
        assert result == "result_a_b"


class TestLogDataSourceMethodDecorator:
    """数据源方法日志装饰器测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.log_records = []
        self.test_handler = logging.Handler()
        self.test_handler.emit = self.capture_log

        self.logger = logging.getLogger("DataSource")
        self.logger.addHandler(self.test_handler)
        self.logger.setLevel(logging.INFO)

    def capture_log(self, record):
        """捕获日志记录"""
        self.log_records.append(record)

    def teardown_method(self):
        """每个测试方法后的清理"""
        self.logger.removeHandler(self.test_handler)
        self.log_records.clear()

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_method_decorator_success(self, mock_logger):
        """测试方法装饰器成功调用"""
        mock_logger_instance = MagicMock()
        mock_logger.logger = MagicMock()
        mock_logger_instance.logger = mock_logger.logger
        mock_logger.logger.info = MagicMock()

        with patch("src.utils.data_source_logger.data_source_logger", mock_logger_instance):

            @log_data_source_method("TestAdapter", "test_method")
            def regular_function(self, *args, **kwargs):
                return {"data": [1, 2, 3]}

            result = regular_function(None, symbol="AAPL")

            assert result == {"data": [1, 2, 3]}
            mock_logger.logger.info.assert_called_once()

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_method_decorator_exception(self, mock_logger):
        """测试方法装饰器异常处理"""
        mock_logger_instance = MagicMock()
        mock_logger.logger = MagicMock()
        mock_logger_instance.logger = mock_logger.logger
        mock_logger.logger.error = MagicMock()

        with patch("src.utils.data_source_logger.data_source_logger", mock_logger_instance):

            @log_data_source_method("ErrorAdapter", "error_method")
            def error_function(self, should_fail=True):
                if should_fail:
                    raise RuntimeError("Test runtime error")
                return "success"

            with pytest.raises(RuntimeError, match="Test runtime error"):
                error_function(None, should_fail=True)

            mock_logger.logger.error.assert_called_once()

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_method_decorator_get_data_from_adapter(self, mock_logger):
        """测试方法装饰器处理get_data_from_adapter函数"""
        mock_logger_instance = MagicMock()
        mock_logger.logger = MagicMock()
        mock_logger_instance.logger = mock_logger.logger
        mock_logger.logger.info = MagicMock()

        with patch("src.utils.data_source_logger.data_source_logger", mock_logger_instance):

            @log_data_source_method("DataAdapter", "fetch_data")
            def get_data_from_adapter(self, adapter_type, method, **kwargs):
                return f"data_{adapter_type}_{method}"

            result = get_data_from_adapter(None, "TestType", "TestMethod", param="value")

            assert result == "data_TestType_TestMethod"
            mock_logger.logger.info.assert_called_once()

            # 验证参数格式
            call_args = mock_logger.logger.info.call_args[0][0]
            assert "DataAdapter.fetch_data" in call_args
            assert "Success: True" in call_args
            assert "Duration:" in call_args
            assert "Params:" in call_args

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_method_decorator_failure_detection(self, mock_logger):
        """测试方法装饰器失败检测"""
        mock_logger_instance = MagicMock()
        mock_logger.logger = MagicMock()
        mock_logger_instance.logger = mock_logger.logger
        mock_logger.logger.info = MagicMock()

        with patch("src.utils.data_source_logger.data_source_logger", mock_logger_instance):

            @log_data_source_method("FailAdapter", "test_fail")
            def failing_function(self):
                return "Error: network failure"

            result = failing_function(None)

            assert result == "Error: network failure"

            # 验证记录为失败
            call_args = mock_logger.logger.info.call_args[0][0]
            assert "Success: False" in call_args

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_method_decorator_empty_result(self, mock_logger):
        """测试方法装饰器空结果处理"""
        mock_logger_instance = MagicMock()
        mock_logger.logger = MagicMock()
        mock_logger_instance.logger = mock_logger.logger
        mock_logger.logger.info = MagicMock()

        with patch("src.utils.data_source_logger.data_source_logger", mock_logger_instance):

            @log_data_source_method("EmptyAdapter", "test_empty")
            def empty_function(self):
                return []

            result = empty_function(None)

            assert result == []

            # 空结果应该被记录为失败（除了get_indicator_data）
            call_args = mock_logger.logger.info.call_args[0][0]
            assert "Success: False" in call_args

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_method_decorator_empty_indicator_data(self, mock_logger):
        """测试方法装饰器空指标数据处理"""
        mock_logger_instance = MagicMock()
        mock_logger.logger = MagicMock()
        mock_logger_instance.logger = mock_logger.logger
        mock_logger.logger.info = MagicMock()

        with patch("src.utils.data_source_logger.data_source_logger", mock_logger_instance):

            @log_data_source_method("IndicatorAdapter", "get_indicator_data")
            def empty_indicator_function(self):
                return []

            result = empty_indicator_function(None)

            assert result == []

            # get_indicator_data的空结果应该被记录为成功
            call_args = mock_logger.logger.info.call_args[0][0]
            assert "Success: True" in call_args

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_method_decorator_none_result(self, mock_logger):
        """测试方法装饰器None结果处理"""
        mock_logger_instance = MagicMock()
        mock_logger.logger = MagicMock()
        mock_logger_instance.logger = mock_logger.logger
        mock_logger.logger.info = MagicMock()

        with patch("src.utils.data_source_logger.data_source_logger", mock_logger_instance):

            @log_data_source_method("NoneAdapter", "test_none")
            def none_function(self):
                return None

            result = none_function(None)

            assert result is None

            # None结果应该被记录为失败
            call_args = mock_logger.logger.info.call_args[0][0]
            assert "Success: False" in call_args

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_method_decorator_chinese_error_message(self, mock_logger):
        """测试方法装饰器中文错误消息处理"""
        mock_logger_instance = MagicMock()
        mock_logger.logger = MagicMock()
        mock_logger_instance.logger = mock_logger.logger
        mock_logger.logger.info = MagicMock()

        with patch("src.utils.data_source_logger.data_source_logger", mock_logger_instance):

            @log_data_source_method("ChineseAdapter", "test_chinese")
            def chinese_error_function(self):
                return "失败: 数据加载失败"

            result = chinese_error_function(None)

            assert result == "失败: 数据加载失败"

            # 中文失败消息应该被记录为失败
            call_args = mock_logger.logger.info.call_args[0][0]
            assert "Success: False" in call_args

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_method_decorator_long_params_truncation(self, mock_logger):
        """测试方法装饰器长参数截断"""
        mock_logger_instance = MagicMock()
        mock_logger.logger = MagicMock()
        mock_logger_instance.logger = mock_logger.logger
        mock_logger.logger.info = MagicMock()

        with patch("src.utils.data_source_logger.data_source_logger", mock_logger_instance):

            @log_data_source_method("LongParamsAdapter", "test_long")
            def long_params_function(self, long_string):
                return "success"

            # 创建一个很长的参数字符串
            long_param = "x" * 300  # 300个字符

            result = long_params_function(None, long_param)

            assert result == "success"

            # 验证参数被截断
            call_args = mock_logger.logger.info.call_args[0][0]
            assert "..." in call_args  # 应该包含截断标记


class TestDataSourceLoggerIntegration:
    """数据源日志记录器集成测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.log_records = []
        self.test_handler = logging.Handler()
        self.test_handler.emit = self.capture_log

        self.logger = logging.getLogger("DataSource")
        self.logger.addHandler(self.test_handler)
        self.logger.setLevel(logging.INFO)

    def capture_log(self, record):
        """捕获日志记录"""
        self.log_records.append(record)

    def teardown_method(self):
        """每个测试方法后的清理"""
        self.logger.removeHandler(self.test_handler)
        self.log_records.clear()

    @patch("src.utils.data_source_logger.data_source_logger")
    def test_both_decorators_working_together(self, mock_logger):
        """测试两个装饰器协同工作"""
        mock_logger_instance = MagicMock()
        mock_logger.log_call = MagicMock()
        mock_logger.log_error = MagicMock()
        mock_logger_instance.log_call = mock_logger.log_call
        mock_logger_instance.log_error = mock_logger.log_error

        with patch("src.utils.data_source_logger.data_source_logger", mock_logger_instance):

            @log_data_source_call("OuterAdapter")
            @log_data_source_method("InnerAdapter", "nested_method")
            def nested_function(self, param):
                return f"nested_result_{param}"

            result = nested_function(None, "test")

            assert result == "nested_result_test"

            # 验证外层装饰器被调用
            mock_logger.log_call.assert_called_once()

    def test_multiple_concurrent_calls(self):
        """测试多个并发调用"""
        import threading

        results = []
        errors = []

        def logging_function(param):
            try:
                with patch("src.utils.data_source_logger.data_source_logger") as mock_logger:
                    mock_logger.log_call = MagicMock()

                    @log_data_source_call("ConcurrentAdapter")
                    def test_func(self, p):
                        time.sleep(0.01)  # 模拟短暂延迟
                        return f"result_{p}"

                    result = test_func(None, param)
                    results.append(result)
            except Exception as e:
                errors.append(e)

        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=logging_function, args=(i,))
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
        assert all(result.startswith("result_") for result in results)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
