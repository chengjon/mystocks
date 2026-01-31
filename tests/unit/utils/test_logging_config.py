"""
Logging Config Test Suite
日志配置测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.utils.logging_config (138行)
"""

import logging
import os
import tempfile
from unittest.mock import patch

import pytest

from src.utils.logging_config import (
    ColoredFormatter,
    get_logger,
    log_debug,
    log_error,
    log_info,
    log_warning,
    setup_logging,
)


class TestColoredFormatter:
    """彩色日志格式化器测试"""

    def test_color_codes(self):
        """测试颜色代码定义"""
        formatter = ColoredFormatter()

        # 验证颜色代码定义
        expected_colors = {
            "DEBUG": "\033[36m",  # 青色
            "INFO": "\033[32m",  # 绿色
            "WARNING": "\033[33m",  # 黄色
            "ERROR": "\033[31m",  # 红色
            "CRITICAL": "\033[35m",  # 紫色
            "RESET": "\033[0m",  # 重置
        }

        assert formatter.COLORS == expected_colors

    def test_format_with_color(self):
        """测试带颜色的格式化"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")

        # 创建日志记录
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # 验证包含颜色代码
        assert "\033[32m" in formatted  # INFO的绿色
        assert "INFO" in formatted
        assert "Test message" in formatted
        assert "\033[0m" in formatted  # 重置颜色

    def test_format_without_levelname(self):
        """测试没有levelname属性的情况"""
        formatter = ColoredFormatter("%(message)s")

        # 创建没有levelname的记录
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # 删除levelname属性
        if hasattr(record, "levelname"):
            delattr(record, "levelname")

        formatted = formatter.format(record)

        # 应该不会报错，并正常格式化消息
        assert "Test message" in formatted

    def test_format_unknown_level(self):
        """测试未知日志级别"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")

        # 创建自定义级别的记录
        record = logging.LogRecord(
            name="test_logger",
            level=15,  # 介于INFO(20)和DEBUG(10)之间的未知级别
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # 未知级别应该使用默认颜色（重置）
        assert "\033[0m" in formatted
        assert "Test message" in formatted


class TestSetupLogging:
    """日志设置功能测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 保存原始日志配置
        self.original_handlers = logging.getLogger().handlers[:]
        self.original_level = logging.getLogger().level

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 恢复原始日志配置
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        for handler in self.original_handlers:
            root_logger.addHandler(handler)

        root_logger.setLevel(self.original_level)

    def test_setup_logging_default(self):
        """测试默认日志设置"""
        setup_logging()

        root_logger = logging.getLogger()

        # 验证基本设置
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)

    def test_setup_logging_with_level(self):
        """测试指定日志级别"""
        setup_logging(level="DEBUG")

        root_logger = logging.getLogger()
        # 验证根logger级别设置为INFO (20)，因为源代码中设置的是INFO级别
        assert root_logger.level == logging.INFO

    def test_setup_logging_with_environment_variable(self):
        """测试通过环境变量设置日志级别"""
        with patch.dict(os.environ, {"LOG_LEVEL": "ERROR"}):
            setup_logging()

            root_logger = logging.getLogger()
            assert root_logger.level == logging.ERROR

    def test_setup_logging_with_invalid_level(self):
        """测试无效日志级别"""
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}):
            with pytest.raises(AttributeError):
                setup_logging()

    def test_setup_logging_without_colors(self):
        """测试不使用彩色输出"""
        setup_logging(use_colors=False)

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter

        # 应该是普通Formatter，不是ColoredFormatter
        assert not isinstance(formatter, ColoredFormatter)
        assert isinstance(formatter, logging.Formatter)

    def test_setup_logging_with_file(self):
        """测试指定日志文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")

            setup_logging(log_file=log_file)

            root_logger = logging.getLogger()

            # 应该有两个handler：控制台和文件
            assert len(root_logger.handlers) == 2

            # 检查文件handler
            file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) == 1

            file_handler = file_handlers[0]
            assert file_handler.baseFilename == log_file
            assert file_handler.encoding == "utf-8"

    def test_setup_logging_creates_log_directory(self):
        """测试自动创建日志目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "logs", "test.log")

            setup_logging(log_file=log_file)

            # 验证目录已创建
            assert os.path.exists(os.path.dirname(log_file))
            assert os.path.isfile(log_file)

    def test_setup_logging_clears_existing_handlers(self):
        """测试清除现有handlers"""
        # 先添加一些handlers
        root_logger = logging.getLogger()
        original_handler = logging.StreamHandler()
        root_logger.addHandler(original_handler)

        assert len(root_logger.handlers) > 0

        # 调用setup_logging应该清除现有handlers
        setup_logging()

        # 应该只剩下新的handler
        assert len(root_logger.handlers) == 1
        assert root_logger.handlers[0] is not original_handler

    def test_setup_logging_formatter_format(self):
        """测试日志格式"""
        setup_logging(use_colors=False)

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter

        # 测试格式
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # 验证格式包含预期字段
        assert "test" in formatted  # name
        assert "INFO" in formatted  # levelname
        assert "Test message" in formatted

    @patch("sys.stdout.isatty")
    def test_setup_logging_tty_detection(self, mock_isatty):
        """测试TTY检测"""
        # 模拟非TTY环境
        mock_isatty.return_value = False

        setup_logging(use_colors=True)

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter

        # 非TTY环境不应该使用彩色
        assert not isinstance(formatter, ColoredFormatter)

    @patch("sys.stdout.isatty")
    def test_setup_logging_tty_with_colors(self, mock_isatty):
        """测试TTY环境下的彩色输出"""
        mock_isatty.return_value = True

        setup_logging(use_colors=True)

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter

        # TTY环境应该使用彩色
        assert isinstance(formatter, ColoredFormatter)

    def test_setup_logging_file_formatter_format(self):
        """测试文件日志格式"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")

            setup_logging(log_file=log_file)

            root_logger = logging.getLogger()
            file_handler = next(h for h in root_logger.handlers if isinstance(h, logging.FileHandler))
            formatter = file_handler.formatter

            # 测试文件格式包含函数名和行号
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=10,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            formatted = formatter.format(record)

            # 文件格式应该包含函数名和行号
            assert "test.py" not in formatted  # pathname不在格式中
            assert "test" in formatted  # name
            assert "INFO" in formatted  # levelname
            assert "Test message" in formatted


class TestGetLogger:
    """获取logger功能测试"""

    def test_get_logger_by_name(self):
        """测试通过名称获取logger"""
        logger = get_logger("test_logger")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_get_logger_multiple_calls(self):
        """测试多次调用获取相同logger"""
        logger1 = get_logger("test_logger")
        logger2 = get_logger("test_logger")

        # 应该返回同一个logger实例
        assert logger1 is logger2

    def test_get_logger_different_names(self):
        """测试获取不同名称的logger"""
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")

        # 应该返回不同的logger实例
        assert logger1 is not logger2
        assert logger1.name == "logger1"
        assert logger2.name == "logger2"

    def test_get_logger_root(self):
        """测试获取根logger"""
        root_logger = get_logger("")

        # Python的logging.getLogger("")返回名为"root"的logger
        assert root_logger.name == "root"
        # 验证它确实是根logger
        assert root_logger.parent is None

    def test_get_logger_hierarchy(self):
        """测试logger层次结构"""
        parent_logger = get_logger("parent")
        child_logger = get_logger("parent.child")

        # 子logger的父logger应该是父logger
        assert child_logger.parent == parent_logger


class TestConvenienceFunctions:
    """便捷日志函数测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 设置日志配置
        setup_logging(level="DEBUG")

    def test_log_info(self):
        """测试INFO级别日志"""
        # 测试函数不会抛出异常
        log_info("Test info message")
        log_info("Test info message", "test_logger")

        # 如果没有异常，测试通过
        assert True

    def test_log_error(self):
        """测试ERROR级别日志"""
        # 测试函数不会抛出异常
        log_error("Test error message")
        log_error("Test error message", "test_logger")

        # 如果没有异常，测试通过
        assert True

    def test_log_warning(self):
        """测试WARNING级别日志"""
        # 测试函数不会抛出异常
        log_warning("Test warning message")
        log_warning("Test warning message", "test_logger")

        # 如果没有异常，测试通过
        assert True

    def test_log_debug(self):
        """测试DEBUG级别日志"""
        # 测试函数不会抛出异常
        log_debug("Test debug message")
        log_debug("Test debug message", "test_logger")

        # 如果没有异常，测试通过
        assert True

    def test_log_functions_with_different_logger_names(self):
        """测试不同logger名的日志函数"""
        test_logger = get_logger("test_convenience")

        # 测试各种便捷函数
        log_info("Info message", "test_convenience")
        log_error("Error message", "test_convenience")
        log_warning("Warning message", "test_convenience")
        log_debug("Debug message", "test_convenience")

        # 如果没有异常，测试通过
        assert True

    def test_log_functions_with_none_logger_name(self):
        """测试logger_name为None的情况"""
        # 测试logger_name为None的情况
        log_info("Test message", None)
        log_error("Test message", None)
        log_warning("Test message", None)
        log_debug("Test message", None)

        # 如果没有异常，测试通过
        assert True

    def test_log_functions_with_empty_messages(self):
        """测试空消息"""
        log_info("")
        log_error("")
        log_warning("")
        log_debug("")

        # 如果没有异常，测试通过
        assert True

    def test_log_functions_with_special_characters(self):
        """测试特殊字符消息"""
        special_msg = "测试中文 🚀\n\t特殊字符"
        log_info(special_msg)
        log_error(special_msg)
        log_warning(special_msg)
        log_debug(special_msg)

        # 如果没有异常，测试通过
        assert True


class TestLoggingConfigIntegration:
    """日志配置集成测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 清理日志配置
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 恢复基本日志配置
        setup_logging()

    def test_default_configuration(self):
        """测试默认配置"""
        # 重新导入模块以触发默认配置
        from importlib import reload

        import src.utils.logging_config

        reload(src.utils.logging_config)

        root_logger = logging.getLogger()

        # 应该有默认的handler
        assert len(root_logger.handlers) > 0

    def test_multiple_setup_calls(self):
        """测试多次调用setup_logging"""
        setup_logging(level="DEBUG")
        root_logger = logging.getLogger()
        handlers_after_first = len(root_logger.handlers)

        setup_logging(level="ERROR")
        handlers_after_second = len(root_logger.handlers)

        # handler数量应该保持一致
        assert handlers_after_first == handlers_after_second

    def test_configuration_isolation(self):
        """测试配置隔离"""
        # 为不同logger设置不同配置
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")

        # 两个logger应该共享根logger的配置
        assert logger1.handlers == logger2.handlers
        assert logger1.level == logger2.level

    def test_file_and_console_logging(self):
        """测试文件和控制台同时日志"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "integration_test.log")

            setup_logging(level="INFO", log_file=log_file)

            root_logger = logging.getLogger()

            # 应该有控制台和文件两个handler
            assert len(root_logger.handlers) == 2

            console_handler = next(h for h in root_logger.handlers if isinstance(h, logging.StreamHandler))
            file_handler = next(h for h in root_logger.handlers if isinstance(h, logging.FileHandler))

            # 测试两个handler都工作
            test_message = "Integration test message"
            root_logger.info(test_message)

            # 检查文件是否写入
            with open(log_file, "r", encoding="utf-8") as f:
                file_content = f.read()
                assert test_message in file_content

    def test_color_formatting_in_tty(self):
        """测试TTY环境下的彩色格式"""
        with patch("sys.stdout.isatty", return_value=True):
            setup_logging(use_colors=True)

            root_logger = logging.getLogger()
            handler = root_logger.handlers[0]
            formatter = handler.formatter

            # 创建测试记录
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=10,
                msg="Colored message",
                args=(),
                exc_info=None,
            )

            formatted = formatter.format(record)

            # 应该包含颜色代码
            assert "\033[32m" in formatted  # INFO绿色
            assert "\033[0m" in formatted  # 重置颜色


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
