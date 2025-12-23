"""
Strategy Factory

策略工厂 - 统一创建和管理策略实例
"""

from typing import Dict, Any, Type, List, Optional
import logging

from app.backtest.strategies.base import BaseStrategy
from app.backtest.strategies.momentum import MomentumStrategy
from app.backtest.strategies.mean_reversion import MeanReversionStrategy
from app.backtest.strategies.breakout import BreakoutStrategy
from app.backtest.strategies.grid import GridStrategy
from app.backtest.strategies.dual_ma import DualMAStrategy
from app.backtest.strategies.turtle import TurtleStrategy
from app.backtest.strategies.macd import MACDStrategy
from app.backtest.strategies.bollinger_breakout import BollingerBreakoutStrategy
from app.backtest.strategies.kdj import KDJStrategy
from app.backtest.strategies.cci import CCIStrategy
from app.backtest.strategies.adx import ADXStrategy
from app.backtest.strategies.sar import SARStrategy

logger = logging.getLogger(__name__)


class StrategyFactory:
    """
    策略工厂

    负责策略的注册、创建和管理
    """

    # 策略注册表
    _strategies: Dict[str, Type[BaseStrategy]] = {}

    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[BaseStrategy]):
        """
        注册策略

        Args:
            name: 策略名称
            strategy_class: 策略类
        """
        cls._strategies[name] = strategy_class
        logger.info(f"策略已注册: {name} -> {strategy_class.__name__}")

    @classmethod
    def create_strategy(
        cls, strategy_type: str, parameters: Dict[str, Any] = None
    ) -> BaseStrategy:
        """
        创建策略实例

        Args:
            strategy_type: 策略类型
            parameters: 策略参数

        Returns:
            策略实例

        Raises:
            ValueError: 如果策略类型不存在
        """
        if strategy_type not in cls._strategies:
            raise ValueError(
                f"未知的策略类型: {strategy_type}. "
                f"可用策略: {list(cls._strategies.keys())}"
            )

        strategy_class = cls._strategies[strategy_type]
        strategy = strategy_class(parameters=parameters)

        logger.info(
            f"策略实例已创建: {strategy_type} with {len(parameters or {})} parameters"
        )
        return strategy

    @classmethod
    def get_available_strategies(cls) -> List[Dict[str, Any]]:
        """
        获取所有可用策略列表

        Returns:
            策略信息列表
        """
        strategies = []
        for name, strategy_class in cls._strategies.items():
            # 创建临时实例以获取信息
            temp_instance = strategy_class()
            info = temp_instance.get_info()
            info["type"] = name

            strategies.append(info)

        return strategies

    @classmethod
    def get_strategy_info(cls, strategy_type: str) -> Optional[Dict[str, Any]]:
        """
        获取特定策略的详细信息

        Args:
            strategy_type: 策略类型

        Returns:
            策略信息字典，如果策略不存在则返回None
        """
        if strategy_type not in cls._strategies:
            return None

        strategy_class = cls._strategies[strategy_type]
        temp_instance = strategy_class()
        info = temp_instance.get_info()
        info["type"] = strategy_type

        return info

    @classmethod
    def get_default_parameters(cls, strategy_type: str) -> Optional[Dict[str, Any]]:
        """
        获取策略的默认参数

        Args:
            strategy_type: 策略类型

        Returns:
            默认参数字典
        """
        if strategy_type not in cls._strategies:
            return None

        strategy_class = cls._strategies[strategy_type]
        return strategy_class.get_default_parameters()

    @classmethod
    def validate_parameters(
        cls, strategy_type: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        验证策略参数

        Args:
            strategy_type: 策略类型
            parameters: 参数字典

        Returns:
            (是否有效, 错误消息)
        """
        if strategy_type not in cls._strategies:
            return False, f"未知的策略类型: {strategy_type}"

        strategy_class = cls._strategies[strategy_type]
        schema = strategy_class.get_parameter_schema()
        defaults = strategy_class.get_default_parameters()

        # 检查必需参数
        for param_def in schema:
            param_name = param_def["name"]
            if param_name not in parameters and param_name not in defaults:
                return False, f"缺少必需参数: {param_name}"

            # 类型和范围检查
            if param_name in parameters:
                value = parameters[param_name]
                param_type = param_def.get("type")

                if param_type == "int" and not isinstance(value, int):
                    return False, f"参数 {param_name} 应该是整数"
                elif param_type == "float" and not isinstance(value, (int, float)):
                    return False, f"参数 {param_name} 应该是浮点数"

                # 范围检查
                if "min" in param_def and value < param_def["min"]:
                    return False, f"参数 {param_name} 不能小于 {param_def['min']}"
                if "max" in param_def and value > param_def["max"]:
                    return False, f"参数 {param_name} 不能大于 {param_def['max']}"

        return True, None


# 自动注册所有预置策略

# 原有4个策略
StrategyFactory.register_strategy("momentum", MomentumStrategy)
StrategyFactory.register_strategy("mean_reversion", MeanReversionStrategy)
StrategyFactory.register_strategy("breakout", BreakoutStrategy)
StrategyFactory.register_strategy("grid", GridStrategy)

# 第一批新增策略 (4个)
StrategyFactory.register_strategy("dual_ma", DualMAStrategy)
StrategyFactory.register_strategy("turtle", TurtleStrategy)
StrategyFactory.register_strategy("macd", MACDStrategy)
StrategyFactory.register_strategy("bollinger_breakout", BollingerBreakoutStrategy)

# 第二批新增策略 (4个技术指标策略)
StrategyFactory.register_strategy("kdj", KDJStrategy)
StrategyFactory.register_strategy("cci", CCIStrategy)
StrategyFactory.register_strategy("adx", ADXStrategy)
StrategyFactory.register_strategy("sar", SARStrategy)

logger.info(f"策略工厂初始化完成，已注册 {len(StrategyFactory._strategies)} 个策略")
