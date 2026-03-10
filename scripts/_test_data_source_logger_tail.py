#!/usr/bin/env python3
"""Support tests extracted from `scripts/tests/test_data_source_logger.py`."""

import logging
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.utils.data_source_logger import (
    DataSourceLogger,
    data_source_logger,
    log_data_source_call,
    log_data_source_method,
)


class CustomError(Exception):
    """自定义异常类用于测试"""


class TestIntegration:
    """集成测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

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

                result1 = function1(None, 5)
                result2 = function2(None, 7)

                assert result1 == 10
                assert result2 == 21
                mock_log_call.assert_called_once()
                mock_log_info.assert_called_once()

    def test_logger_instance_sharing(self):
        """测试日志记录器实例共享"""
        logger1 = DataSourceLogger("SharedLogger")
        logger2 = DataSourceLogger("SharedLogger")

        assert logger1.logger is logger2.logger
        assert logger1.logger.name == "SharedLogger"

    def test_global_logger_usage(self):
        """测试全局日志记录器使用"""
        with patch.object(data_source_logger, "log_call") as mock_log:

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

            mock_file_handler.assert_called_once_with("data_source_calls.log")
            assert mock_file_instance in logger_instance.logger.handlers

    def test_error_propagation_integration(self):
        """测试错误传播集成"""
        with patch.object(data_source_logger, "log_error") as mock_log_error:

            @log_data_source_call("ErrorTestAdapter")
            def error_propagation_function(self, should_error=True):
                if should_error:
                    raise CustomError("Test error propagation")
                return "success"

            with pytest.raises(CustomError, match="Test error propagation"):
                error_propagation_function(None, should_error=True)

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

        threads = []
        for i in range(10):
            thread = threading.Thread(target=concurrent_function, args=(None, i))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 10
        assert len(set(results)) == 10
        assert len(errors) == 0
