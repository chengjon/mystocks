"""
策略ID值对象
Strategy ID Value Object

表示策略的唯一标识符。
"""

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class StrategyId:
    """
    策略ID值对象

    职责：
    - 确保策略ID的类型安全
    - 提供ID验证和生成

    Attributes:
        value: ID值（字符串）
    """

    value: str

    @classmethod
    def generate(cls) -> "StrategyId":
        """生成新的策略ID"""
        return cls(value=str(uuid4()))

    @classmethod
    def from_string(cls, value: str) -> "StrategyId":
        """从字符串创建策略ID"""
        if not value or not value.strip():
            raise ValueError("Strategy ID cannot be empty")
        return cls(value=value.strip())

    def __str__(self) -> str:
        return self.value
