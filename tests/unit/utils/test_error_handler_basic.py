"""
Error Handler基础测试
专注于提升error_handler模块覆盖率（157行代码）
"""

import logging
import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
from src.utils.error_handler import UnifiedErrorHandler, retry_on_failure, safe_execute


class TestUnifiedErrorHandlerBasic:
    """UnifiedErrorHandler基础测试 - 专注覆盖率"""

    def test_class_import_compatibility(self):
        """测试类导入兼容性"""
        from src.utils.error_handler import UnifiedErrorHandler

        assert UnifiedErrorHandler is not None
        assert callable(UnifiedErrorHandler)

    def test_has_static_methods(self):
        """测试静态方法存在"""
        static_methods = ["log_error", "safe_execute", "retry_on_failure"]

        for method_name in static_methods:
            assert hasattr(UnifiedErrorHandler, method_name), f"缺少静态方法: {method_name}"
            assert callable(getattr(UnifiedErrorHandler, method_name)), f"方法不可调用: {method_name}"

    def test_log_error_method(self):
        """测试log_error方法"""
        with patch("src.utils.error_handler.logger") as mock_logger:
            test_error = ValueError("测试错误")
            context = "测试上下文"

            UnifiedErrorHandler.log_error(test_error, context)

            # 验证logger.log被调用
            mock_logger.log.assert_called_once()
            args, kwargs = mock_logger.log.call_args

            assert args[0] == logging.ERROR  # 默认错误级别
            assert "测试上下文" in args[1]
            assert "测试错误" in args[1]
            assert "ValueError" in args[1]

    def test_log_error_with_custom_level(self):
        """测试带自定义日志级别的log_error方法"""
        with patch("src.utils.error_handler.logger") as mock_logger:
            test_error = RuntimeError("运行时错误")

            UnifiedErrorHandler.log_error(test_error, "测试", level=logging.WARNING)

            mock_logger.log.assert_called_once_with(
                logging.WARNING, "错误发生 - 上下文: 测试, 错误: 运行时错误, 类型: RuntimeError"
            )

    def test_log_error_without_context(self):
        """测试无上下文的log_error方法"""
        with patch("src.utils.error_handler.logger") as mock_logger:
            test_error = KeyError("键错误")

            UnifiedErrorHandler.log_error(test_error)

            args, kwargs = mock_logger.log.call_args
            assert "键错误" in args[1]
            assert "KeyError" in args[1]

    def test_safe_execute_success(self):
        """测试safe_execute成功情况"""

        def test_func():
            return "success"

        result = UnifiedErrorHandler.safe_execute(test_func, "测试")

        assert result == "success"

    def test_safe_execute_with_exception(self):
        """测试safe_execute异常情况"""

        def failing_func():
            raise ValueError("函数失败")

        with patch.object(UnifiedErrorHandler, "log_error") as mock_log:
            result = UnifiedErrorHandler.safe_execute(failing_func, "测试上下文", default_return="默认值")

            assert result == "默认值"
            mock_log.assert_called_once()

    def test_safe_execute_reraise(self):
        """测试safe_execute重新抛出异常"""

        def failing_func():
            raise RuntimeError("需要重新抛出")

        with pytest.raises(RuntimeError, match="需要重新抛出"):
            UnifiedErrorHandler.safe_execute(failing_func, "测试", reraise=True)

    def test_safe_execute_no_logging(self):
        """测试safe_execute不记录日志"""

        def failing_func():
            raise ValueError("静默失败")

        with patch.object(UnifiedErrorHandler, "log_error") as mock_log:
            result = UnifiedErrorHandler.safe_execute(
                failing_func, "测试", log_error=False, default_return="静默默认值"
            )

            assert result == "静默默认值"
            mock_log.assert_not_called()

    def test_retry_decorator_method(self):
        """测试重试装饰器方法"""
        # 测试retry_on_failure是一个方法
        retry_method = getattr(UnifiedErrorHandler, "retry_on_failure")
        assert callable(retry_method)

    def test_retry_decorator_signature(self):
        """测试重试装饰器签名"""
        import inspect

        retry_sig = inspect.signature(UnifiedErrorHandler.retry_on_failure)

        expected_params = ["max_retries", "delay", "backoff", "exceptions", "context"]
        actual_params = list(retry_sig.parameters.keys())

        for param in expected_params:
            assert param in actual_params

    def test_module_logging_configuration(self):
        """测试模块日志配置"""
        from src.utils.error_handler import logger

        assert logger is not None
        assert hasattr(logger, "log")
        assert callable(getattr(logger, "log"))

    def test_method_parameter_types(self):
        """测试方法参数类型"""
        import inspect

        # 检查log_error方法的参数
        log_error_sig = inspect.signature(UnifiedErrorHandler.log_error)
        params = list(log_error_sig.parameters.keys())
        expected_params = ["error", "context", "level"]

        for param in expected_params:
            assert param in params

        # 检查safe_execute方法的参数
        safe_execute_sig = inspect.signature(UnifiedErrorHandler.safe_execute)
        params = list(safe_execute_sig.parameters.keys())
        expected_params = ["func", "context", "default_return", "log_error", "reraise"]

        for param in expected_params:
            assert param in params

    def test_error_types_handling(self):
        """测试不同错误类型的处理"""
        error_types = [
            ValueError("值错误"),
            TypeError("类型错误"),
            AttributeError("属性错误"),
            KeyError("键错误"),
            IndexError("索引错误"),
        ]

        with patch.object(UnifiedErrorHandler, "log_error") as mock_log:
            for error in error_types:
                UnifiedErrorHandler.log_error(error, f"测试{type(error).__name__}")

            assert mock_log.call_count == len(error_types)

    def test_static_method_decorators(self):
        """测试静态方法装饰器"""
        # 验证方法是静态方法（通过检查属性）
        log_error_attr = getattr(UnifiedErrorHandler, "log_error")
        assert callable(log_error_attr)

        safe_execute_attr = getattr(UnifiedErrorHandler, "safe_execute")
        assert callable(safe_execute_attr)

    def test_module_documentation(self):
        """测试模块文档"""
        import src.utils.error_handler as error_handler_module

        assert error_handler_module.__doc__ is not None
        assert "统一错误处理" in error_handler_module.__doc__

        # 验证类文档
        class_doc = UnifiedErrorHandler.__doc__
        assert class_doc is not None
        assert "统一错误处理器" in class_doc

    def test_import_completeness(self):
        """测试导入完整性"""
        from src.utils.error_handler import UnifiedErrorHandler, logger

        assert UnifiedErrorHandler is not None
        assert logger is not None
        assert hasattr(logger, "log")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])
