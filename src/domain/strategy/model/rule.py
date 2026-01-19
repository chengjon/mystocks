"""
规则实体
Rule Entity

表示策略中的交易规则。
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Rule:
    """
    规则实体

    职责：
    - 定义交易规则逻辑
    - 判断指标值是否满足条件
    - 创建交易信号

    示例：
        Rule(indicator_name="RSI", operator=">", threshold=70, action=SELL)
        表示：当RSI指标大于70时，生成卖出信号
    """

    indicator_name: str
    operator: str  # '>', '<', '==', '>=', '<='
    threshold: float
    action: str  # 'BUY', 'SELL'

    def matches(self, indicators: Dict[str, Any]) -> bool:
        """
        判断指标值是否满足规则条件

        Args:
            indicators: 指标值字典 {indicator_name: value}

        Returns:
            bool: 是否满足条件
        """
        value = indicators.get(self.indicator_name)

        if value is None:
            return False

        if self.operator == ">":
            return value > self.threshold
        elif self.operator == "<":
            return value < self.threshold
        elif self.operator == ">=":
            return value >= self.threshold
        elif self.operator == "<=":
            return value <= self.threshold
        elif self.operator == "==":
            return value == self.threshold
        else:
            raise ValueError(f"Invalid operator: {self.operator}")

    def __str__(self) -> str:
        return f"Rule({self.indicator_name} {self.operator} {self.threshold} -> {self.action})"
