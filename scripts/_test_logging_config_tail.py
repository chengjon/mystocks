#!/usr/bin/env python3
"""Support tests extracted from `scripts/tests/test_logging_config.py`."""

import logging
import os
import sys
import tempfile
import time

from src.utils.logging_config import (
    ColoredFormatter,
    get_logger,
    log_debug,
    log_error,
    log_info,
    log_warning,
    setup_logging,
)


class TestPerformance:
    """性能测试类"""

    def test_colored_formatter_performance(self):
        """测试彩色格式化器性能"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Performance test message",
            args=(),
            exc_info=None,
        )

        iterations = 10000
        start_time = time.time()
        for _ in range(iterations):
            formatter.format(record)
        end_time = time.time()

        avg_time = (end_time - start_time) / iterations * 1000000
        assert avg_time < 100, f"彩色格式化平均耗时 {avg_time:.2f} 微秒，超过预期"

    def test_logging_functions_performance(self):
        """测试日志函数性能"""
        setup_logging(level="INFO")

        iterations = 100
        start_time = time.time()
        for i in range(iterations):
            log_info(f"Performance test message {i}")
        end_time = time.time()

        avg_time = (end_time - start_time) / iterations * 1000
        assert avg_time < 10, f"日志记录平均耗时 {avg_time:.2f} 毫秒，超过预期"

    def test_setup_logging_performance(self):
        """测试日志设置性能"""
        iterations = 100

        start_time = time.time()
        for _ in range(iterations):
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            setup_logging(level="INFO", use_colors=True)
        end_time = time.time()

        avg_time = (end_time - start_time) / iterations * 1000
        assert avg_time < 10, f"日志设置平均耗时 {avg_time:.2f} 毫秒，超过预期"


class TestIntegration:
    """集成测试类"""

    def test_end_to_end_logging_workflow(self):
        """测试端到端日志工作流程"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "integration_test.log")

            setup_logging(level="DEBUG", log_file=log_file, use_colors=True)

            logger = get_logger("integration_test")
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

            log_debug("Debug via convenience function")
            log_info("Info via convenience function")
            log_warning("Warning via convenience function")
            log_error("Error via convenience function")

            assert os.path.exists(log_file)
            with open(log_file, "r", encoding="utf-8") as file_handle:
                content = file_handle.read()
                assert "Debug message" in content
                assert "Info message" in content
                assert "Warning message" in content
                assert "Error message" in content

    def test_configuration_consistency_across_functions(self):
        """测试函数间配置一致性"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "consistency_test.log")
            setup_logging(level="WARNING", log_file=log_file, use_colors=False)

            logger = get_logger("consistency_test")
            assert logger.level == logging.NOTSET
            assert logger.isEnabledFor(logging.WARNING)
            assert not logger.isEnabledFor(logging.INFO)

            root_logger = logging.getLogger()
            assert len(root_logger.handlers) == 2
            assert root_logger.level == logging.WARNING

    def test_multiple_loggers_interaction(self):
        """测试多个logger交互"""
        setup_logging(level="INFO")

        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        logger3 = get_logger("sub.module3")

        assert logger1.parent is logging.getLogger()
        assert logger2.parent is logging.getLogger()
        assert logger3.parent is logging.getLogger()
        assert logger1.isEnabledFor(logging.INFO)
        assert logger2.isEnabledFor(logging.INFO)
        assert logger3.isEnabledFor(logging.INFO)

    def test_configuration_isolation(self):
        """测试配置隔离"""
        setup_logging(level="INFO", use_colors=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "isolation_test.log")
            setup_logging(level="DEBUG", log_file=log_file, use_colors=False)

            root_logger = logging.getLogger()
            assert len(root_logger.handlers) == 2
            assert root_logger.level == logging.DEBUG

    def test_real_world_usage_scenario(self):
        """测试真实使用场景"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "app.log")

            setup_logging(
                level=os.getenv("LOG_LEVEL", "INFO"),
                log_file=log_file,
                use_colors=sys.stdout.isatty(),
            )

            main_logger = get_logger("main")
            db_logger = get_logger("database")
            api_logger = get_logger("api")

            main_logger.info("Application started")
            db_logger.debug("Database connection established")
            api_logger.info("API server listening on port 8000")

            try:
                raise ValueError("Test exception")
            except ValueError as error:
                main_logger.error(f"Application error: {error}")
                log_error(f"Error via convenience function: {error}")

            with open(log_file, "r", encoding="utf-8") as file_handle:
                content = file_handle.read()
                assert "Application started" in content
                assert "API server listening" in content
                assert "Application error" in content
                assert "Error via convenience function" in content
