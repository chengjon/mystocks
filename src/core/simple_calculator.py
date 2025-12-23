#!/usr/bin/env python3
"""
简单计算器模块 - 用于测试源代码覆盖率
提供基本的数学运算功能，用于演示测试覆盖率
"""

import logging
from typing import List, Union, Optional, Dict, Any

logger = logging.getLogger(__name__)

# 类型别名定义
Number = Union[int, float]
OperationType = str
StatisticsDict = Dict[str, Any]


class SimpleCalculator:
    """简单计算器类"""

    def __init__(self) -> None:
        """
        初始化计算器
        """
        self.last_result: Optional[Number] = None
        self.operation_count: int = 0

    def add(self, a: Number, b: Number) -> Number:
        """
        加法运算

        Args:
            a: 第一个操作数
            b: 第二个操作数

        Returns:
            Number: 两个数的和
        """
        self.operation_count += 1
        result = a + b
        self.last_result = result
        logger.info("执行加法: %s + %s = %s", a, b, result)
        return result

    def subtract(self, a: Number, b: Number) -> Number:
        """
        减法运算

        Args:
            a: 被减数
            b: 减数

        Returns:
            Number: 两个数的差
        """
        self.operation_count += 1
        result = a - b
        self.last_result = result
        logger.info("执行减法: %s - %s = %s", a, b, result)
        return result

    def multiply(self, a: Number, b: Number) -> Number:
        """
        乘法运算

        Args:
            a: 第一个操作数
            b: 第二个操作数

        Returns:
            Number: 两个数的乘积
        """
        self.operation_count += 1
        result = a * b
        self.last_result = result
        logger.info("执行乘法: %s * %s = %s", a, b, result)
        return result

    def divide(self, a: Number, b: Number) -> Number:
        """
        除法运算

        Args:
            a: 被除数
            b: 除数

        Returns:
            Number: 两个数的商

        Raises:
            ValueError: 当除数为零时
        """
        self.operation_count += 1
        if b == 0:
            raise ValueError("除数不能为零")
        result = a / b
        self.last_result = result
        logger.info("执行除法: %s / %s = %s", a, b, result)
        return result

    def get_last_result(self) -> Optional[Number]:
        """
        获取最后一次计算结果

        Returns:
            Optional[Number]: 最后一次计算的结果，如果没有计算过则为None
        """
        return self.last_result

    def get_operation_count(self) -> int:
        """
        获取操作次数

        Returns:
            int: 已执行的操作次数
        """
        return self.operation_count

    def reset(self) -> None:
        """
        重置计算器状态
        """
        self.last_result = None
        self.operation_count = 0
        logger.info("计算器已重置")

    def calculate_average(self, numbers: List[Number]) -> float:
        """
        计算平均值

        Args:
            numbers: 数字列表

        Returns:
            float: 数字的平均值

        Raises:
            ValueError: 当列表为空时
        """
        if not numbers:
            raise ValueError("数字列表不能为空")
        self.operation_count += 1
        avg = sum(numbers) / len(numbers)
        self.last_result = avg
        logger.info("计算平均值: %s", avg)
        return avg

    def find_max(self, numbers: List[Number]) -> Number:
        """
        查找最大值

        Args:
            numbers: 数字列表

        Returns:
            Number: 列表中的最大值

        Raises:
            ValueError: 当列表为空时
        """
        if not numbers:
            raise ValueError("数字列表不能为空")
        self.operation_count += 1
        max_val = max(numbers)
        self.last_result = max_val
        logger.info("找到最大值: %s", max_val)
        return max_val

    def find_min(self, numbers: List[Number]) -> Number:
        """
        查找最小值

        Args:
            numbers: 数字列表

        Returns:
            Number: 列表中的最小值

        Raises:
            ValueError: 当列表为空时
        """
        if not numbers:
            raise ValueError("数字列表不能为空")
        self.operation_count += 1
        min_val = min(numbers)
        self.last_result = min_val
        logger.info("找到最小值: %s", min_val)
        return min_val

    def sum_list(self, numbers: List[Number]) -> Number:
        """
        计算列表总和

        Args:
            numbers: 数字列表

        Returns:
            Number: 列表元素的总和
        """
        self.operation_count += 1
        total = sum(numbers)
        self.last_result = total
        logger.info("计算列表总和: %s", total)
        return total

    def validate_input(self, value: Any) -> bool:
        """
        验证输入参数

        Args:
            value: 要验证的值

        Returns:
            bool: 如果是数字则返回True

        Raises:
            TypeError: 当输入不是数字时
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"输入必须是数字，得到: {type(value)}")
        return True

    def safe_divide(self, a: Number, b: Number) -> Number:
        """
        安全除法，返回默认值

        Args:
            a: 被除数
            b: 除数

        Returns:
            Number: 除法结果，如果除数为零则返回0
        """
        if b == 0:
            logger.warning("除数为零，返回默认值0")
            return 0
        return self.divide(a, b)

    def power(self, base: Number, exponent: Number) -> Number:
        """
        幂运算

        Args:
            base: 底数
            exponent: 指数

        Returns:
            Number: 幂运算结果
        """
        self.operation_count += 1
        result = base**exponent
        self.last_result = result
        logger.info("幂运算: %s^%s = %s", base, exponent, result)
        return result

    def get_statistics(self) -> StatisticsDict:
        """
        获取计算器统计信息

        Returns:
            StatisticsDict: 包含统计信息的字典
        """
        return {
            "last_result": self.last_result,
            "operation_count": self.operation_count,
            "is_first_operation": self.operation_count == 0,
        }


def create_calculator() -> SimpleCalculator:
    """
    工厂函数创建计算器实例

    Returns:
        SimpleCalculator: 新创建的计算器实例
    """
    return SimpleCalculator()


def perform_calculation_sequence(
    calculator: SimpleCalculator, operations: List[Dict[str, Any]]
) -> List[Number]:
    """
    执行一系列计算操作

    Args:
        calculator: 计算器实例
        operations: 操作列表，每个操作包含type和参数

    Returns:
        List[Number]: 计算结果列表

    Raises:
        ValueError: 当遇到不支持的操作类型时
    """
    results: List[Number] = []
    for op in operations:
        if op["type"] == "add":
            result = calculator.add(op["a"], op["b"])
        elif op["type"] == "subtract":
            result = calculator.subtract(op["a"], op["b"])
        elif op["type"] == "multiply":
            result = calculator.multiply(op["a"], op["b"])
        elif op["type"] == "divide":
            result = calculator.divide(op["a"], op["b"])
        else:
            raise ValueError(f"不支持的操作类型: {op['type']}")
        results.append(result)
    return results
