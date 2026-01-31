#!/usr/bin/env python3
"""
简单计算器单元测试 - 演示实际源代码覆盖率
"""

import os
import sys

import pytest

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.simple_calculator import (
    SimpleCalculator,
    create_calculator,
    perform_calculation_sequence,
)


class TestSimpleCalculator:
    """简单计算器测试类"""

    @pytest.fixture
    def calculator(self):
        """创建计算器实例"""
        return SimpleCalculator()

    def test_calculator_initialization(self, calculator):
        """测试计算器初始化"""
        assert calculator.last_result is None
        assert calculator.operation_count == 0

    def test_add_operation(self, calculator):
        """测试加法运算"""
        result = calculator.add(2, 3)
        assert result == 5
        assert calculator.last_result == 5
        assert calculator.operation_count == 1

    def test_subtract_operation(self, calculator):
        """测试减法运算"""
        result = calculator.subtract(5, 3)
        assert result == 2
        assert calculator.last_result == 2
        assert calculator.operation_count == 1

    def test_multiply_operation(self, calculator):
        """测试乘法运算"""
        result = calculator.multiply(4, 3)
        assert result == 12
        assert calculator.last_result == 12
        assert calculator.operation_count == 1

    def test_divide_operation(self, calculator):
        """测试除法运算"""
        result = calculator.divide(6, 3)
        assert result == 2.0
        assert calculator.last_result == 2.0
        assert calculator.operation_count == 1

    def test_divide_by_zero(self, calculator):
        """测试除零错误"""
        with pytest.raises(ValueError, match="除数不能为零"):
            calculator.divide(5, 0)

    def test_get_last_result(self, calculator):
        """测试获取最后一次结果"""
        calculator.add(2, 3)
        assert calculator.get_last_result() == 5

        calculator.reset()
        assert calculator.get_last_result() is None

    def test_get_operation_count(self, calculator):
        """测试获取操作次数"""
        assert calculator.get_operation_count() == 0

        calculator.add(2, 3)
        assert calculator.get_operation_count() == 1

        calculator.subtract(5, 3)
        assert calculator.get_operation_count() == 2

    def test_reset(self, calculator):
        """测试重置功能"""
        calculator.add(2, 3)
        calculator.subtract(5, 3)

        assert calculator.last_result == 2
        assert calculator.operation_count == 2

        calculator.reset()

        assert calculator.last_result is None
        assert calculator.operation_count == 0

    def test_calculate_average(self, calculator):
        """测试计算平均值"""
        numbers = [1, 2, 3, 4, 5]
        result = calculator.calculate_average(numbers)
        assert result == 3.0
        assert calculator.last_result == 3.0
        assert calculator.operation_count == 1

    def test_calculate_average_empty_list(self, calculator):
        """测试空列表平均值"""
        with pytest.raises(ValueError, match="数字列表不能为空"):
            calculator.calculate_average([])

    def test_find_max(self, calculator):
        """测试查找最大值"""
        numbers = [1, 3, 2, 5, 4]
        result = calculator.find_max(numbers)
        assert result == 5
        assert calculator.last_result == 5
        assert calculator.operation_count == 1

    def test_find_max_empty_list(self, calculator):
        """测试空列表最大值"""
        with pytest.raises(ValueError, match="数字列表不能为空"):
            calculator.find_max([])

    def test_find_min(self, calculator):
        """测试查找最小值"""
        numbers = [3, 1, 4, 2, 5]
        result = calculator.find_min(numbers)
        assert result == 1
        assert calculator.last_result == 1
        assert calculator.operation_count == 1

    def test_find_min_empty_list(self, calculator):
        """测试空列表最小值"""
        with pytest.raises(ValueError, match="数字列表不能为空"):
            calculator.find_min([])

    def test_sum_list(self, calculator):
        """测试列表求和"""
        numbers = [1, 2, 3, 4, 5]
        result = calculator.sum_list(numbers)
        assert result == 15
        assert calculator.last_result == 15
        assert calculator.operation_count == 1

    def test_validate_input(self, calculator):
        """测试输入验证"""
        # 有效输入
        assert calculator.validate_input(5) is True
        assert calculator.validate_input(5.5) is True

        # 无效输入
        with pytest.raises(TypeError, match="输入必须是数字"):
            calculator.validate_input("hello")

        with pytest.raises(TypeError, match="输入必须是数字"):
            calculator.validate_input([1, 2, 3])

    def test_safe_divide(self, calculator):
        """测试安全除法"""
        # 正常除法
        result = calculator.safe_divide(6, 3)
        assert result == 2.0

        # 除零情况
        result = calculator.safe_divide(6, 0)
        assert result == 0

    def test_power(self, calculator):
        """测试幂运算"""
        result = calculator.power(2, 3)
        assert result == 8
        assert calculator.last_result == 8
        assert calculator.operation_count == 1

        result = calculator.power(5, 2)
        assert result == 25
        assert calculator.last_result == 25

    def test_get_statistics(self, calculator):
        """测试获取统计信息"""
        # 初始状态
        stats = calculator.get_statistics()
        assert stats["last_result"] is None
        assert stats["operation_count"] == 0
        assert stats["is_first_operation"] is True

        # 执行操作后
        calculator.add(2, 3)
        stats = calculator.get_statistics()
        assert stats["last_result"] == 5
        assert stats["operation_count"] == 1
        assert stats["is_first_operation"] is False

    def test_multiple_operations(self, calculator):
        """测试多个连续操作"""
        # 2 + 3 = 5
        calculator.add(2, 3)
        assert calculator.last_result == 5

        # 5 * 2 = 10
        calculator.multiply(calculator.last_result, 2)
        assert calculator.last_result == 10

        # 10 - 3 = 7
        calculator.subtract(calculator.last_result, 3)
        assert calculator.last_result == 7

        # 7 / 2 = 3.5
        calculator.divide(calculator.last_result, 2)
        assert calculator.last_result == 3.5

        assert calculator.operation_count == 4

    def test_float_operations(self, calculator):
        """测试浮点数运算"""
        result = calculator.add(1.5, 2.3)
        assert abs(result - 3.8) < 1e-10

        result = calculator.divide(5, 2)
        assert result == 2.5

    def test_negative_numbers(self, calculator):
        """测试负数运算"""
        result = calculator.add(-2, 3)
        assert result == 1

        result = calculator.subtract(2, -3)
        assert result == 5

        result = calculator.multiply(-2, -3)
        assert result == 6

        result = calculator.divide(-6, 3)
        assert result == -2.0


class TestCalculatorUtilityFunctions:
    """测试计算器工具函数"""

    def test_create_calculator(self):
        """测试工厂函数"""
        calc = create_calculator()
        assert isinstance(calc, SimpleCalculator)
        assert calc.operation_count == 0
        assert calc.last_result is None

    def test_perform_calculation_sequence(self):
        """测试计算序列执行"""
        calc = SimpleCalculator()
        operations = [
            {"type": "add", "a": 2, "b": 3},
            {"type": "subtract", "a": 10, "b": 5},
            {"type": "multiply", "a": 4, "b": 3},
            {"type": "divide", "a": 12, "b": 4},
        ]

        results = perform_calculation_sequence(calc, operations)

        expected_results = [5, 5, 12, 3.0]
        assert results == expected_results
        assert calc.operation_count == 4
        assert calc.last_result == 3.0

    def test_perform_calculation_sequence_invalid_operation(self):
        """测试无效操作类型"""
        calc = SimpleCalculator()
        operations = [
            {"type": "add", "a": 2, "b": 3},
            {"type": "invalid_operation", "a": 1, "b": 2},
        ]

        with pytest.raises(ValueError, match="不支持的操作类型: invalid_operation"):
            perform_calculation_sequence(calc, operations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
