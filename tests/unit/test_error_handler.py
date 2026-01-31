"""
统一错误处理工具测试文件
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest

from src.utils.error_handler import (
    DataError,
    UnifiedErrorHandler,
    retry_on_failure,
    safe_execute,
)


class TestUnifiedErrorHandler(unittest.TestCase):
    """统一错误处理器测试类"""

    def test_log_error(self):
        """测试错误日志记录"""
        # 这个测试主要是验证方法可以调用，实际日志输出需要查看日志文件
        try:
            raise ValueError("测试错误")
        except ValueError as e:
            UnifiedErrorHandler.log_error(e, "测试上下文")
            # 如果没有异常，说明方法可以正常调用
            self.assertTrue(True)

    def test_safe_execute_success(self):
        """测试安全执行成功情况"""

        def test_func():
            return "success"

        result = UnifiedErrorHandler.safe_execute(test_func, "测试成功执行")
        self.assertEqual(result, "success")

    def test_safe_execute_failure_with_default(self):
        """测试安全执行失败情况（返回默认值）"""

        def test_func():
            raise ValueError("测试异常")

        result = UnifiedErrorHandler.safe_execute(test_func, "测试失败执行", "default")
        self.assertEqual(result, "default")

    def test_safe_execute_failure_with_reraise(self):
        """测试安全执行失败情况（重新抛出异常）"""

        def test_func():
            raise ValueError("测试异常")

        with self.assertRaises(ValueError):
            UnifiedErrorHandler.safe_execute(test_func, "测试失败执行", reraise=True)

    def test_retry_on_failure_success(self):
        """测试重试成功"""
        call_count = 0

        @UnifiedErrorHandler.retry_on_failure(max_retries=3, delay=0.1, context="测试重试")
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("临时错误")
            return "success"

        result = test_func()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 2)  # 第一次失败，第二次成功

    def test_retry_on_failure_all_failures(self):
        """测试重试全部失败"""
        call_count = 0

        @UnifiedErrorHandler.retry_on_failure(max_retries=3, delay=0.1, context="测试重试")
        def test_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("持续错误")

        with self.assertRaises(ValueError):
            test_func()

        self.assertEqual(call_count, 3)  # 重试3次

    def test_retry_on_failure_specific_exceptions(self):
        """测试特定异常重试"""
        call_count = 0

        @UnifiedErrorHandler.retry_on_failure(
            max_retries=3, delay=0.1, exceptions=(ValueError,), context="测试特定异常"
        )
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("值错误")
            return "success"

        result = test_func()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 2)

    def test_convenience_functions(self):
        """测试便捷函数"""
        # 测试safe_execute便捷函数
        result = safe_execute(lambda: "test", "便捷函数测试", "default")
        self.assertEqual(result, "test")

        # 测试retry_on_failure便捷函数
        @retry_on_failure(max_retries=2, delay=0.1, context="便捷函数重试测试")
        def test_func():
            return "success"

        result = test_func()
        self.assertEqual(result, "success")


class TestCustomExceptions(unittest.TestCase):
    """自定义异常测试类"""

    def test_data_error(self):
        """测试数据错误异常"""
        with self.assertRaises(DataError):
            raise DataError("数据错误")

    def test_inheritance(self):
        """测试异常继承关系"""
        self.assertTrue(issubclass(DataError, Exception))


if __name__ == "__main__":
    unittest.main()
