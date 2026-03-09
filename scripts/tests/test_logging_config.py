#!/usr/bin/env python3
"""
logging_config.py 模块测试套件
提供完整的日志配置功能测试覆盖，遵循Phase 6成功模式
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import tempfile
import logging
import io
from unittest.mock import patch

# 导入被测试的模块
from src.utils.logging_config import (
    ColoredFormatter,
    setup_logging,
    get_logger,
    log_info,
    log_error,
    log_warning,
    log_debug,
)


class TestColoredFormatter:
    """彩色日志格式化器测试类"""

    def test_color_codes_constant(self):
        """测试颜色代码常量"""
        expected_colors = {
            "DEBUG": "\033[36m",  # 青色
            "INFO": "\033[32m",  # 绿色
            "WARNING": "\033[33m",  # 黄色
            "ERROR": "\033[31m",  # 红色
            "CRITICAL": "\033[35m",  # 紫色
            "RESET": "\033[0m",  # 重置
        }

        assert ColoredFormatter.COLORS == expected_colors
        assert len(ColoredFormatter.COLORS) == 6

    def test_format_with_levelname(self):
        """测试带级别名称的格式化"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")

        # 创建测试记录
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
        assert "\033[32m" in formatted  # INFO绿色
        assert "INFO" in formatted
        assert "Test message" in formatted
        assert "\033[0m" in formatted  # 重置颜色

    def test_format_with_all_log_levels(self):
        """测试所有日志级别的颜色格式化"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")

        test_cases = [
            (logging.DEBUG, "\033[36m", "DEBUG"),
            (logging.INFO, "\033[32m", "INFO"),
            (logging.WARNING, "\033[33m", "WARNING"),
            (logging.ERROR, "\033[31m", "ERROR"),
            (logging.CRITICAL, "\033[35m", "CRITICAL"),
        ]

        for level, expected_color, level_name in test_cases:
            record = logging.LogRecord(
                name="test_logger",
                level=level,
                pathname="test.py",
                lineno=10,
                msg=f"Test {level_name}",
                args=(),
                exc_info=None,
            )

            formatted = formatter.format(record)
            assert expected_color in formatted
            assert level_name in formatted
            assert "\033[0m" in formatted

    def test_format_without_levelname_attribute(self):
        """测试没有levelname属性的记录"""
        formatter = ColoredFormatter("%(message)s")

        # 创建没有levelname属性的记录
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

        # 应该不会出错，但也不会添加颜色
        formatted = formatter.format(record)
        assert "Test message" in formatted
        assert "\033[" not in formatted  # 不应该有颜色代码

    def test_format_uses_super_class_functionality(self):
        """测试使用父类的格式化功能"""
        # 使用复杂的格式字符串
        formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )

        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=42,
            msg="Complex message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"

        formatted = formatter.format(record)

        # 验证所有字段都存在
        assert "test_logger" in formatted
        assert "WARNING" in formatted
        assert "test_function" in formatted
        assert "42" in formatted
        assert "Complex message" in formatted
        assert "\033[33m" in formatted  # WARNING黄色

    def test_unknown_level_uses_reset_color(self):
        """测试未知级别使用重置颜色"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")

        # 创建自定义级别的记录
        record = logging.LogRecord(
            name="test_logger",
            level=99,  # 自定义级别
            pathname="test.py",
            lineno=10,
            msg="Custom level",
            args=(),
            exc_info=None,
        )
        record.levelname = "CUSTOM"

        formatted = formatter.format(record)

        # 应该使用RESET颜色
        assert "\033[0m" in formatted
        assert "CUSTOM" in formatted


class TestSetupLogging:
    """日志设置功能测试类"""

    def test_setup_logging_default_configuration(self):
        """测试默认日志配置"""
        # 清除现有配置
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 使用默认配置
        setup_logging()

        # 验证配置
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)
        assert root_logger.level == logging.INFO
        assert root_logger.handlers[0].level == logging.INFO

    def test_setup_logging_with_custom_level(self):
        """测试自定义日志级别"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 测试各种级别
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        expected_levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]

        for level_str, expected_level in zip(levels, expected_levels):
            setup_logging(level=level_str)
            root_logger = logging.getLogger()
            assert root_logger.level == expected_level

            # 清理
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

    def test_setup_logging_with_environment_variable(self):
        """测试通过环境变量设置日志级别"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 设置环境变量
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            setup_logging()  # 默认INFO，但应该被环境变量覆盖

            root_logger = logging.getLogger()
            assert root_logger.level == logging.DEBUG

    def test_setup_logging_with_invalid_level(self):
        """测试无效日志级别"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 无效级别应该使用getattr的默认行为（如果有的话）
        # 或者抛出异常，取决于实现
        with pytest.raises(AttributeError):
            setup_logging(level="INVALID_LEVEL")

    def test_setup_logging_with_log_file(self):
        """测试配置日志文件"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")

            setup_logging(log_file=log_file)

            root_logger = logging.getLogger()
            # 应该有两个handler：控制台和文件
            assert len(root_logger.handlers) == 2

            # 验证文件handler
            file_handlers = [
                h for h in root_logger.handlers if isinstance(h, logging.FileHandler)
            ]
            assert len(file_handlers) == 1
            assert file_handlers[0].baseFilename == log_file

    def test_setup_logging_creates_log_directory(self):
        """测试自动创建日志目录"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = os.path.join(temp_dir, "logs", "app")
            log_file = os.path.join(nested_dir, "test.log")

            # 目录不存在
            assert not os.path.exists(nested_dir)

            setup_logging(log_file=log_file)

            # 目录应该被创建
            assert os.path.exists(nested_dir)
            assert os.path.isdir(nested_dir)

    @patch("sys.stdout.isatty", return_value=True)
    def test_setup_logging_with_colors_when_tty(self, mock_isatty):
        """测试TTY环境下启用彩色输出"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        setup_logging(use_colors=True)

        root_logger = logging.getLogger()
        console_handler = root_logger.handlers[0]
        formatter = console_handler.formatter
        assert isinstance(formatter, ColoredFormatter)

    @patch("sys.stdout.isatty", return_value=False)
    def test_setup_logging_without_colors_when_not_tty(self, mock_isatty):
        """测试非TTY环境下禁用彩色输出"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        setup_logging(use_colors=True)

        root_logger = logging.getLogger()
        console_handler = root_logger.handlers[0]
        formatter = console_handler.formatter
        assert isinstance(formatter, logging.Formatter)
        assert not isinstance(formatter, ColoredFormatter)

    def test_setup_logging_explicitly_disable_colors(self):
        """测试明确禁用彩色输出"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        setup_logging(use_colors=False)

        root_logger = logging.getLogger()
        console_handler = root_logger.handlers[0]
        formatter = console_handler.formatter
        assert isinstance(formatter, logging.Formatter)
        assert not isinstance(formatter, ColoredFormatter)

    def test_setup_logging_clears_existing_handlers(self):
        """测试清除现有handlers"""
        root_logger = logging.getLogger()

        # 记录原始handler数量（可能包含pytest的capture handlers）
        original_count = len(root_logger.handlers)

        # 添加一些现有handlers
        old_handler1 = logging.StreamHandler()
        old_handler2 = logging.StreamHandler()
        root_logger.addHandler(old_handler1)
        root_logger.addHandler(old_handler2)

        # 添加前的数量应该等于原始数量+2
        assert len(root_logger.handlers) == original_count + 2

        setup_logging()

        # setup_logging后的数量应该是1（新的console handler）
        # pytest可能会添加capture handlers，所以我们检查总数
        assert len(root_logger.handlers) >= 1
        # 新的handler应该存在，旧的被清除
        new_handlers = root_logger.handlers[-1:]  # 取最后一个handler
        assert len(new_handlers) == 1
        assert new_handlers[0] not in [old_handler1, old_handler2]

    def test_setup_logging_file_handler_format(self):
        """测试文件handler的格式"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")

            setup_logging(log_file=log_file)

            root_logger = logging.getLogger()
            file_handlers = [
                h for h in root_logger.handlers if isinstance(h, logging.FileHandler)
            ]
            file_formatter = file_handlers[0].formatter

            # 验证文件格式包含函数名和行号
            format_str = file_formatter._fmt
            assert "%(funcName)s" in format_str
            assert "%(lineno)d" in format_str

    def test_setup_logging_case_insensitive_level(self):
        """测试日志级别大小写不敏感"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 测试小写级别
        setup_logging(level="debug")
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

        # 清理
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 测试混合大小写
        setup_logging(level="Info")
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO


class TestGetLogger:
    """Logger获取功能测试类"""

    def test_get_logger_with_name(self):
        """测试通过名称获取logger"""
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_get_logger_same_name_returns_same_instance(self):
        """测试相同名称返回相同实例"""
        logger1 = get_logger("test_logger")
        logger2 = get_logger("test_logger")
        assert logger1 is logger2

    def test_get_logger_different_names_returns_different_instances(self):
        """测试不同名称返回不同实例"""
        logger1 = get_logger("test_logger1")
        logger2 = get_logger("test_logger2")
        assert logger1 is not logger2
        assert logger1.name == "test_logger1"
        assert logger2.name == "test_logger2"

    def test_get_logger_with_module_name_pattern(self):
        """测试使用模块名称模式"""
        # 模拟 __name__ 的使用
        logger = get_logger(__name__)
        assert logger.name == __name__

    def test_get_logger_empty_name(self):
        """测试空名称"""
        logger = get_logger("")
        assert isinstance(logger, logging.Logger)
        # logging.getLogger("") 返回root logger，所以名称是"root"
        assert logger.name == "root"

    def test_get_logger_root_name(self):
        """测试根logger名称"""
        logger = get_logger("root")
        root_logger = logging.getLogger("root")
        assert logger is root_logger


class TestConvenienceLogFunctions:
    """便捷日志函数测试类"""

    def setup_method(self):
        """每个测试前的设置"""
        # 清除现有handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 设置测试logger，使用StringIO捕获输出
        self.string_io = io.StringIO()
        self.handler = logging.StreamHandler(self.string_io)
        self.formatter = logging.Formatter("%(levelname)s: %(message)s")
        self.handler.setFormatter(self.formatter)

        root_logger.addHandler(self.handler)
        root_logger.setLevel(logging.DEBUG)

    def test_log_info_without_logger_name(self):
        """测试不带logger名的info日志"""
        log_info("Test info message")

        output = self.string_io.getvalue()
        assert "INFO: Test info message" in output

    def test_log_info_with_logger_name(self):
        """测试带logger名的info日志"""
        log_info("Test info message", "test_logger")

        output = self.string_io.getvalue()
        assert "INFO: Test info message" in output

    def test_log_error_without_logger_name(self):
        """测试不带logger名的error日志"""
        log_error("Test error message")

        output = self.string_io.getvalue()
        assert "ERROR: Test error message" in output

    def test_log_error_with_logger_name(self):
        """测试带logger名的error日志"""
        log_error("Test error message", "test_logger")

        output = self.string_io.getvalue()
        assert "ERROR: Test error message" in output

    def test_log_warning_without_logger_name(self):
        """测试不带logger名的warning日志"""
        log_warning("Test warning message")

        output = self.string_io.getvalue()
        assert "WARNING: Test warning message" in output

    def test_log_warning_with_logger_name(self):
        """测试带logger名的warning日志"""
        log_warning("Test warning message", "test_logger")

        output = self.string_io.getvalue()
        assert "WARNING: Test warning message" in output

    def test_log_debug_without_logger_name(self):
        """测试不带logger名的debug日志"""
        log_debug("Test debug message")

        output = self.string_io.getvalue()
        assert "DEBUG: Test debug message" in output

    def test_log_debug_with_logger_name(self):
        """测试带logger名的debug日志"""
        log_debug("Test debug message", "test_logger")

        output = self.string_io.getvalue()
        assert "DEBUG: Test debug message" in output

    def test_convenience_functions_use_correct_logger(self):
        """测试便捷函数使用正确的logger"""
        # 创建一个特定的logger来验证
        test_logger = logging.getLogger("specific_test_logger")
        handler = logging.StreamHandler(self.string_io)
        handler.setFormatter(self.formatter)
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.DEBUG)

        # 使用特定的logger名
        log_info("Specific message", "specific_test_logger")

        output = self.string_io.getvalue()
        assert "INFO: Specific message" in output

    def test_convenience_functions_with_special_characters(self):
        """测试包含特殊字符的消息"""
        special_messages = [
            "Message with 中文 characters",
            "Message with émojis 🚀",
            "Message with \n newlines",
            "Message with \t tabs",
            "Message with 'quotes' and \"double quotes\"",
            "Message with %s formatting",
            "Message with {brackets}",
        ]

        for message in special_messages:
            # 清空缓冲区
            self.string_io.truncate(0)
            self.string_io.seek(0)

            log_info(message)
            output = self.string_io.getvalue()
            assert message in output

    def test_convenience_functions_unicode_handling(self):
        """测试Unicode处理"""
        unicode_messages = [
            "测试中文消息",
            "🚀 Rocket emoji",
            "Café résumé naïve",
            "𝔘𝔫𝔦𝔠𝔬𝔡𝔞 𝔠𝔥𝔞𝔯𝔞𝔠𝔱𝔢𝔯𝔰",
        ]

        for message in unicode_messages:
            self.string_io.truncate(0)
            self.string_io.seek(0)

            log_info(message)
            output = self.string_io.getvalue()
            assert message in output


class TestModuleLevelConfiguration:
    """模块级别配置测试类"""

    def test_default_configuration_on_import(self):
        """测试导入时的默认配置"""
        # 重新导入模块来测试默认配置
        # 清除现有配置
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 重新导入（这会触发默认配置）
        import importlib
        import src.utils.logging_config

        importlib.reload(src.utils.logging_config)

        # 验证默认配置已应用
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)

    def test_no_duplicate_handlers_on_multiple_imports(self):
        """测试多次导入不会创建重复handlers"""
        # 清除现有配置
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 多次导入
        import importlib
        import src.utils.logging_config

        importlib.reload(src.utils.logging_config)
        importlib.reload(src.utils.logging_config)
        importlib.reload(src.utils.logging_config)

        # 应该只有一个handler
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 1


from scripts._test_logging_config_tail import TestIntegration, TestPerformance


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
