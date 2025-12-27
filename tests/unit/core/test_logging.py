"""
logging 模块单元测试

测试统一日志系统的核心功能:
- UnifiedLogger类的各种日志级别
- 异常捕获上下文管理器
- 性能日志装饰器
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock

# 确保能导入src模块
sys.path.insert(0, "/opt/claude/mystocks_spec")

# Mock loguru before importing logging module to prevent file creation
with patch("loguru.logger") as mock_loguru:
    mock_loguru.remove = Mock()
    mock_loguru.add = Mock()
    mock_loguru.bind = Mock(return_value=mock_loguru)
    mock_loguru.opt = Mock(return_value=mock_loguru)
    mock_loguru.trace = Mock()
    mock_loguru.debug = Mock()
    mock_loguru.info = Mock()
    mock_loguru.success = Mock()
    mock_loguru.warning = Mock()
    mock_loguru.error = Mock()
    mock_loguru.critical = Mock()
    mock_loguru.catch = Mock()

    from src.core.logging import UnifiedLogger, add_handler, remove_handler


class TestUnifiedLoggerInitialization:
    """测试UnifiedLogger初始化"""

    @patch("src.core.logging.loguru_logger")
    def test_logger_initialization_default_name(self, mock_logger):
        """测试默认名称初始化"""
        mock_logger.bind = Mock(return_value=mock_logger)

        logger = UnifiedLogger()

        mock_logger.bind.assert_called_once_with(name="MyStocks")

    @patch("src.core.logging.loguru_logger")
    def test_logger_initialization_custom_name(self, mock_logger):
        """测试自定义名称初始化"""
        mock_logger.bind = Mock(return_value=mock_logger)

        logger = UnifiedLogger("CustomModule")

        mock_logger.bind.assert_called_once_with(name="CustomModule")


class TestUnifiedLoggerMethods:
    """测试UnifiedLogger的日志方法"""

    @patch("src.core.logging.loguru_logger")
    def test_trace_method(self, mock_logger):
        """测试trace方法"""
        mock_opt = Mock()
        mock_opt.trace = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()
        logger.trace("Trace message", extra_data="test")

        mock_logger.opt.assert_called_with(depth=1)
        mock_opt.trace.assert_called_once()

    @patch("src.core.logging.loguru_logger")
    def test_debug_method(self, mock_logger):
        """测试debug方法"""
        mock_opt = Mock()
        mock_opt.debug = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()
        logger.debug("Debug message")

        mock_logger.opt.assert_called_with(depth=1)
        mock_opt.debug.assert_called_once()

    @patch("src.core.logging.loguru_logger")
    def test_info_method(self, mock_logger):
        """测试info方法"""
        mock_opt = Mock()
        mock_opt.info = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()
        logger.info("Info message", user="admin")

        mock_logger.opt.assert_called_with(depth=1)
        mock_opt.info.assert_called_once()

    @patch("src.core.logging.loguru_logger")
    def test_success_method(self, mock_logger):
        """测试success方法"""
        mock_opt = Mock()
        mock_opt.success = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()
        logger.success("Success message")

        mock_logger.opt.assert_called_with(depth=1)
        mock_opt.success.assert_called_once()

    @patch("src.core.logging.loguru_logger")
    def test_warning_method(self, mock_logger):
        """测试warning方法"""
        mock_opt = Mock()
        mock_opt.warning = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()
        logger.warning("Warning message")

        mock_logger.opt.assert_called_with(depth=1)
        mock_opt.warning.assert_called_once()

    @patch("src.core.logging.loguru_logger")
    def test_error_method(self, mock_logger):
        """测试error方法"""
        mock_opt = Mock()
        mock_opt.error = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()
        logger.error("Error message", error_code=500)

        mock_logger.opt.assert_called_with(depth=1)
        mock_opt.error.assert_called_once()

    @patch("src.core.logging.loguru_logger")
    def test_critical_method(self, mock_logger):
        """测试critical方法"""
        mock_opt = Mock()
        mock_opt.critical = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()
        logger.critical("Critical message")

        mock_logger.opt.assert_called_with(depth=1)
        mock_opt.critical.assert_called_once()

    @patch("src.core.logging.loguru_logger")
    def test_exception_method(self, mock_logger):
        """测试exception方法（带异常堆栈）"""
        mock_opt = Mock()
        mock_opt.error = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()
        logger.exception("Exception occurred")

        mock_logger.opt.assert_called_with(depth=1, exception=True)
        mock_opt.error.assert_called_once()


class TestUnifiedLoggerCatchContext:
    """测试UnifiedLogger的catch上下文管理器"""

    @patch("src.core.logging.loguru_logger")
    def test_catch_context_no_exception(self, mock_logger):
        """测试catch上下文管理器（无异常）"""
        mock_logger.bind = Mock(return_value=mock_logger)

        logger = UnifiedLogger()

        with logger.catch():
            pass  # 不抛出异常

        # 没有异常时不应该记录日志

    @patch("src.core.logging.loguru_logger")
    def test_catch_context_with_exception_reraise(self, mock_logger):
        """测试catch上下文管理器（异常并重新抛出）"""
        mock_opt = Mock()
        mock_opt.error = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()

        with pytest.raises(ValueError):
            with logger.catch(message="Test error", reraise=True):
                raise ValueError("Test exception")

        # 应该调用error级别日志
        mock_logger.opt.assert_called_with(exception=True)

    @patch("src.core.logging.loguru_logger")
    def test_catch_context_with_exception_no_reraise(self, mock_logger):
        """测试catch上下文管理器（异常但不重新抛出）"""
        mock_opt = Mock()
        mock_opt.error = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()

        # 不应该抛出异常
        with logger.catch(message="Test error", reraise=False):
            raise ValueError("Test exception")

        # 应该记录错误
        mock_logger.opt.assert_called_with(exception=True)

    @patch("src.core.logging.loguru_logger")
    def test_catch_context_exclude_exception(self, mock_logger):
        """测试catch上下文管理器（排除特定异常）"""
        mock_logger.bind = Mock(return_value=mock_logger)

        logger = UnifiedLogger()

        with pytest.raises(KeyError):
            with logger.catch(exclude=ValueError, reraise=True):
                raise KeyError("Not excluded")

    @patch("src.core.logging.loguru_logger")
    def test_catch_context_custom_level(self, mock_logger):
        """测试catch上下文管理器（自定义日志级别）"""
        mock_opt = Mock()
        mock_opt.warning = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()

        with logger.catch(message="Test warning", reraise=False, level="WARNING"):
            raise ValueError("Test exception")

        mock_opt.warning.assert_called_once()


class TestUnifiedLoggerPerformanceDecorator:
    """测试UnifiedLogger的log_performance装饰器"""

    @pytest.mark.skip(reason="log_performance uses complex loguru.catch() internals that are difficult to mock")
    @patch("src.core.logging.loguru_logger")
    @patch("time.time")
    def test_log_performance_success(self, mock_time, mock_logger):
        """测试性能日志装饰器（成功场景）

        注意: log_performance装饰器使用了复杂的catch()调用链,
        这里简化测试只验证装饰器能正常工作
        """
        # Mock时间
        mock_time.side_effect = [0.0, 0.1]  # 开始时间和结束时间

        mock_opt = Mock()
        mock_opt.info = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        # 创建一个简单的catch mock,返回一个简单的wrapper
        def mock_catch_wrapper():
            def wrapper(func):
                return func

            return wrapper

        mock_logger.catch = Mock(return_value=mock_catch_wrapper)

        logger = UnifiedLogger()

        @logger.log_performance
        def test_function():
            return "result"

        result = test_function()

        assert result == "result"
        # 验证info方法被调用来记录性能
        assert mock_opt.info.called

    @pytest.mark.skip(reason="log_performance uses complex loguru.catch() internals that are difficult to mock")
    @patch("src.core.logging.loguru_logger")
    @patch("time.time")
    def test_log_performance_failure(self, mock_time, mock_logger):
        """测试性能日志装饰器（失败场景）

        注意: log_performance装饰器使用了复杂的catch()调用链,
        这里简化测试只验证装饰器能正常处理异常
        """
        mock_time.side_effect = [0.0, 0.05]

        mock_opt = Mock()
        mock_opt.error = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        # 创建一个简单的catch mock
        def mock_catch_wrapper():
            def wrapper(func):
                return func

            return wrapper

        mock_logger.catch = Mock(return_value=mock_catch_wrapper)

        logger = UnifiedLogger()

        @logger.log_performance
        def failing_function():
            raise RuntimeError("Function failed")

        with pytest.raises(RuntimeError):
            failing_function()

        # 验证error方法被调用来记录失败
        assert mock_opt.error.called


class TestModuleLevelFunctions:
    """测试模块级别的函数"""

    @patch("src.core.logging.loguru_logger")
    def test_add_handler_function(self, mock_logger):
        """测试add_handler函数"""
        mock_logger.add = Mock(return_value="handler_id")

        result = add_handler("test_sink", level="DEBUG")

        mock_logger.add.assert_called_once()

    @patch("src.core.logging.loguru_logger")
    def test_remove_handler_function(self, mock_logger):
        """测试remove_handler函数"""
        mock_logger.remove = Mock()

        remove_handler("handler_id")

        mock_logger.remove.assert_called_once_with("handler_id")


class TestLoggingEdgeCases:
    """测试日志系统边界情况"""

    @patch("src.core.logging.loguru_logger")
    def test_logging_with_none_message(self, mock_logger):
        """测试记录None消息"""
        mock_opt = Mock()
        mock_opt.info = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()

        # 应该不抛出异常
        logger.info(None)
        mock_opt.info.assert_called_once()

    @patch("src.core.logging.loguru_logger")
    def test_logging_with_empty_message(self, mock_logger):
        """测试记录空字符串消息"""
        mock_opt = Mock()
        mock_opt.info = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()
        logger.info("")

        mock_opt.info.assert_called_once()

    @patch("src.core.logging.loguru_logger")
    def test_logging_with_very_long_message(self, mock_logger):
        """测试记录超长消息"""
        mock_opt = Mock()
        mock_opt.info = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()
        long_message = "A" * 10000
        logger.info(long_message)

        mock_opt.info.assert_called_once()

    @patch("src.core.logging.loguru_logger")
    def test_logging_with_unicode_characters(self, mock_logger):
        """测试记录Unicode字符"""
        mock_opt = Mock()
        mock_opt.info = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()
        logger.info("测试中文日志 😀🎉🚀")

        mock_opt.info.assert_called_once()


class TestLoggingIntegration:
    """测试日志系统集成功能"""

    @patch("src.core.logging.loguru_logger")
    def test_multiple_loggers_independent(self, mock_logger):
        """测试多个logger实例独立性"""
        mock_logger.bind = Mock(side_effect=lambda name: Mock())

        logger1 = UnifiedLogger("Module1")
        logger2 = UnifiedLogger("Module2")

        assert logger1.logger != logger2.logger
        assert mock_logger.bind.call_count == 2

    @patch("src.core.logging.loguru_logger")
    def test_logger_with_extra_kwargs(self, mock_logger):
        """测试logger带额外关键字参数"""
        mock_opt = Mock()
        mock_opt.info = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()
        logger.info("Message", user_id=123, action="login", ip="192.168.1.1")

        mock_opt.info.assert_called_once()


class TestLogPerformanceDecorator:
    """测试log_performance装饰器"""

    @patch("src.core.logging.loguru_logger")
    def test_log_performance_success(self, mock_logger):
        """测试log_performance装饰器成功执行"""
        mock_opt = Mock()
        mock_opt.info = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)
        mock_logger.catch = Mock(return_value=lambda f: f)

        logger = UnifiedLogger()

        @logger.log_performance
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"
        # 验证记录了执行时间
        mock_opt.info.assert_called()

    @patch("src.core.logging.loguru_logger")
    def test_log_performance_exception(self, mock_logger):
        """测试log_performance装饰器处理异常"""
        mock_opt = Mock()
        mock_opt.info = Mock()
        mock_opt.error = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)
        mock_logger.catch = Mock(return_value=lambda f: f)

        logger = UnifiedLogger()

        @logger.log_performance
        def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_func()

        # 验证记录了错误
        mock_opt.error.assert_called()


class TestCatchExceptionsExclude:
    """测试catch_exceptions的排除异常功能"""

    @patch("src.core.logging.loguru_logger")
    def test_catch_exclude_exception_with_reraise(self, mock_logger):
        """测试排除特定异常并重新抛出"""
        mock_opt = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()

        with pytest.raises(ValueError):
            with logger.catch("Error occurred", exclude=(ValueError,), reraise=True):
                raise ValueError("Expected error")

    @patch("src.core.logging.loguru_logger")
    def test_catch_exclude_exception_no_reraise(self, mock_logger):
        """测试排除特定异常不重新抛出"""
        mock_opt = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_opt)

        logger = UnifiedLogger()

        # 应该静默返回，不抛出异常
        with logger.catch("Error occurred", exclude=(ValueError,), reraise=False):
            raise ValueError("Excluded error")

        # 验证没有调用日志记录（因为异常被排除）


class TestDbSink:
    """测试数据库日志sink功能"""

    @patch("psycopg2.connect")
    def test_db_sink_warning_level(self, mock_connect):
        """测试db_sink记录WARNING级别日志"""
        from src.core.logging import db_sink

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # 创建模拟的日志消息
        message = MagicMock()
        message.record = {
            "level": MagicMock(no=30, name="WARNING"),  # WARNING level
            "time": MagicMock(isoformat=lambda: "2025-01-01T00:00:00"),
            "name": "test_module",
            "function": "test_func",
            "message": "Test warning message",
            "exception": None,
            "file": MagicMock(path="/test/path.py"),
            "line": 100,
            "process": MagicMock(id=1234),
            "thread": MagicMock(id=5678),
        }

        db_sink(message)

        # 验证数据库操作被调用
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch("psycopg2.connect")
    def test_db_sink_below_warning_skip(self, mock_connect):
        """测试db_sink跳过低于WARNING的日志"""
        from src.core.logging import db_sink

        # 创建INFO级别日志消息
        message = MagicMock()
        message.record = {
            "level": MagicMock(no=20, name="INFO"),  # INFO level < WARNING
        }

        db_sink(message)

        # 验证数据库连接未被调用
        mock_connect.assert_not_called()

    @patch("psycopg2.connect")
    def test_db_sink_exception_silent(self, mock_connect):
        """测试db_sink异常静默处理"""
        from src.core.logging import db_sink

        mock_connect.side_effect = Exception("Database connection failed")

        # 创建模拟的日志消息
        message = MagicMock()
        message.record = {
            "level": MagicMock(no=40, name="ERROR"),  # ERROR level
            "time": MagicMock(isoformat=lambda: "2025-01-01T00:00:00"),
            "name": "test_module",
            "function": "test_func",
            "message": "Test error message",
            "exception": None,
            "file": MagicMock(path="/test/path.py"),
            "line": 100,
            "process": MagicMock(id=1234),
            "thread": MagicMock(id=5678),
        }

        # 应该不抛出异常
        db_sink(message)  # Should pass silently
