"""
Instrument Pool Value Object
交易标的池值对象

表示策略可交易的金融标的集合。
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class AssetClass(Enum):
    """资产类别"""

    EQUITY = "equity"  # 股票
    FUTURES = "futures"  # 期货
    OPTIONS = "options"  # 期权
    FOREX = "forex"  # 外汇
    CRYPTO = "crypto"  # 加密货币
    ETF = "etf"  # ETF
    INDEX = "index"  # 指数


@dataclass(frozen=True)
class InstrumentPool:
    """
    交易标的池值对象

    职责：
    - 管理策略可交易的标的集合
    - 提供标的验证和过滤
    - 支持标的分组和分类

    不变性：
    - 一旦创建不可修改（frozen=True）
    - 标的列表唯一且有序
    """

    name: str  # 标的池名称，如 "A股主板", "美股科技股"
    symbols: frozenset[str]  # 标的代码集合（使用frozenset保证唯一性和不可变性）
    asset_class: AssetClass  # 资产类别
    description: str = ""  # 描述
    max_positions: int = 10  # 最大同时持仓数

    def __post_init__(self):
        """验证标的池"""
        if not self.symbols:
            raise ValueError("InstrumentPool cannot be empty")

        if self.max_positions <= 0:
            raise ValueError(f"max_positions must be positive, got {self.max_positions}")

        if len(self.symbols) > self.max_positions:
            raise ValueError(f"Pool size ({len(self.symbols)}) exceeds max_positions ({self.max_positions})")

    @property
    def size(self) -> int:
        """标的数量"""
        return len(self.symbols)

    def contains(self, symbol: str) -> bool:
        """检查标的是否在池中"""
        return symbol in self.symbols

    def get_symbols_list(self) -> List[str]:
        """获取标的列表（排序后）"""
        return sorted(self.symbols)

    @classmethod
    def from_list(
        cls,
        name: str,
        symbols: List[str],
        asset_class: AssetClass,
        description: str = "",
        max_positions: int = 10,
    ) -> "InstrumentPool":
        """
        从列表创建标的池

        Args:
            name: 标的池名称
            symbols: 标的代码列表
            asset_class: 资产类别
            description: 描述
            max_positions: 最大持仓数

        Returns:
            InstrumentPool实例
        """
        # 去重并转换为frozenset
        unique_symbols = frozenset(symbols)
        return cls(
            name=name,
            symbols=unique_symbols,
            asset_class=asset_class,
            description=description,
            max_positions=max_positions,
        )

    def __str__(self) -> str:
        return f"InstrumentPool(name={self.name}, size={self.size}, asset_class={self.asset_class.value})"
