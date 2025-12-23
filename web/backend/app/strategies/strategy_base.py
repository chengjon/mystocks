"""
策略基类和策略注册表

复用现有组件:
- indicator_calculator (161个TA-Lib指标) - EXISTING
- data_service (OHLCV数据加载) - EXISTING
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from enum import Enum
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class StrategyCategory(Enum):
    """策略分类"""

    TREND_FOLLOWING = "trend_following"  # 趋势跟踪
    MEAN_REVERSION = "mean_reversion"  # 均值回归
    BREAKOUT = "breakout"  # 突破策略
    VOLUME_BASED = "volume_based"  # 成交量策略


class StrategyBase(ABC):
    """
    策略基类

    所有策略必须继承此类并实现execute()方法
    """

    def __init__(
        self, strategy_id: str, name: str, description: str, category: StrategyCategory
    ):
        self.strategy_id = strategy_id
        self.name = name
        self.description = description
        self.category = category

    @abstractmethod
    def execute(
        self, symbol: str, start_date: str, end_date: str, parameters: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        执行策略生成交易信号

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            parameters: 策略参数

        Returns:
            pd.DataFrame: 信号DataFrame
                columns: ['date', 'signal', 'price', 'reason']
                signal: 1=买入, -1=卖出, 0=持有
        """
        pass

    def get_default_parameters(self) -> Dict[str, Any]:
        """获取默认参数"""
        return {}


class StrategyRegistry:
    """策略注册表 (单例模式)"""

    _instance = None
    _strategies: Dict[str, type[StrategyBase]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register_strategy(self, strategy_class: type[StrategyBase]):
        """注册策略"""
        strategy_instance = strategy_class()
        self._strategies[strategy_instance.strategy_id] = strategy_class
        logger.info(
            f"注册策略: {strategy_instance.strategy_id} - {strategy_instance.name}"
        )

    def get_strategy(self, strategy_id: str) -> Optional[StrategyBase]:
        """获取策略实例"""
        if strategy_id in self._strategies:
            return self._strategies[strategy_id]()
        return None

    def list_strategies(self) -> List[Dict[str, Any]]:
        """列出所有策略"""
        strategies = []
        for strategy_class in self._strategies.values():
            instance = strategy_class()
            strategies.append(
                {
                    "strategy_id": instance.strategy_id,
                    "name": instance.name,
                    "description": instance.description,
                    "category": instance.category.value,
                    "default_parameters": instance.get_default_parameters(),
                }
            )
        return strategies


# 全局注册表实例
_registry = None


def get_strategy_registry() -> StrategyRegistry:
    """获取策略注册表单例"""
    global _registry
    if _registry is None:
        _registry = StrategyRegistry()
    return _registry
