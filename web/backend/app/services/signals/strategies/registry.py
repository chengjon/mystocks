"""
Strategy Registry - 策略注册表

支持YAML和Python配置的信号策略管理系统：
- 策略注册和发现
- 参数验证
- 策略组合管理
- 运行时策略切换

作者: Claude Code (Sisyphus)
日期: 2026-01-14
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import yaml

from web.backend.app.services.signals.strategies.base_strategies import (
    BollingerBandsStrategy,
    MACDStrategy,
    RSIStrategy,
    SignalStrategy,
)

logger = logging.getLogger(__name__)


@dataclass
class StrategyDefinition:
    """策略定义"""

    name: str
    type: str  # 策略类名
    description: str = ""
    indicators: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 0  # 执行优先级


class StrategyRegistry:
    """
    策略注册表

    管理信号生成策略的注册、配置和生命周期
    """

    def __init__(self):
        """初始化策略注册表"""
        self.strategies: Dict[str, Type[SignalStrategy]] = {}
        self.definitions: Dict[str, StrategyDefinition] = {}
        self.instances: Dict[str, SignalStrategy] = {}

        # 注册内置策略
        self._register_builtin_strategies()

        logger.info("✅ Strategy Registry initialized")

    def _register_builtin_strategies(self):
        """注册内置策略"""
        # 创建默认参数
        default_params = {
            "rsi_strategy": {
                "oversold_level": 30,
                "overbought_level": 70,
                "risk_reward_ratio": 2.0,
                "stop_loss_percentage": 0.05,
            },
            "macd_strategy": {
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9,
                "risk_reward_ratio": 2.0,
                "stop_loss_percentage": 0.05,
            },
            "bbands_strategy": {
                "period": 20,
                "std_dev": 2.0,
                "risk_reward_ratio": 2.0,
                "stop_loss_percentage": 0.05,
            },
        }

        # 注册并创建实例
        self.register_and_create("rsi_strategy", RSIStrategy, default_params["rsi_strategy"])
        self.register_and_create("macd_strategy", MACDStrategy, default_params["macd_strategy"])
        self.register_and_create("bbands_strategy", BollingerBandsStrategy, default_params["bbands_strategy"])

        logger.info("Built-in strategies registered and instantiated")

    def register_strategy(self, name: str, strategy_class: Type[SignalStrategy]):
        """
        注册策略类

        Args:
            name: 策略名称
            strategy_class: 策略类
        """
        self.strategies[name] = strategy_class
        logger.debug("Strategy registered: %(name)s")

    def register_and_create(
        self,
        name: str,
        strategy_class: Type[SignalStrategy],
        parameters: Dict[str, Any],
    ):
        """
        注册策略类并创建实例

        Args:
            name: 策略名称
            strategy_class: 策略类
            parameters: 策略参数
        """
        self.register_strategy(name, strategy_class)
        try:
            instance = strategy_class(parameters)
            self.instances[name] = instance
            logger.debug("Strategy instance created: %(name)s")
        except Exception as e:
            logger.error("Failed to create strategy instance %(name)s: %(e)s")

    def load_from_yaml(self, yaml_path: str) -> List[str]:
        """
        从YAML文件加载策略定义

        Args:
            yaml_path: YAML文件路径

        Returns:
            加载的策略名称列表
        """
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            loaded_strategies = []

            if "strategies" in config:
                for strategy_config in config["strategies"]:
                    definition = StrategyDefinition(
                        name=strategy_config["name"],
                        type=strategy_config["type"],
                        description=strategy_config.get("description", ""),
                        indicators=strategy_config.get("indicators", []),
                        parameters=strategy_config.get("parameters", {}),
                        enabled=strategy_config.get("enabled", True),
                        priority=strategy_config.get("priority", 0),
                    )

                    self.definitions[definition.name] = definition
                    loaded_strategies.append(definition.name)

            logger.info("Loaded {len(loaded_strategies)} strategies from %(yaml_path)s")
            return loaded_strategies

        except Exception as e:
            logger.error("Error loading strategies from %(yaml_path)s: %(e)s")
            return []

    def load_from_directory(self, directory_path: str) -> List[str]:
        """
        从目录加载所有YAML策略文件

        Args:
            directory_path: 策略文件目录

        Returns:
            加载的策略名称列表
        """
        directory = Path(directory_path)
        if not directory.exists():
            logger.warning("Strategy directory not found: %(directory_path)s")
            return []

        all_strategies = []

        for yaml_file in directory.glob("*.yaml"):
            strategies = self.load_from_yaml(str(yaml_file))
            all_strategies.extend(strategies)

        for yaml_file in directory.glob("*.yml"):
            strategies = self.load_from_yaml(str(yaml_file))
            all_strategies.extend(strategies)

        logger.info("Loaded {len(all_strategies)} strategies from directory %(directory_path)s")
        return all_strategies

    def create_strategy(self, definition: StrategyDefinition) -> Optional[SignalStrategy]:
        """
        创建策略实例

        Args:
            definition: 策略定义

        Returns:
            策略实例
        """
        try:
            if not definition.enabled:
                logger.debug("Strategy {definition.name} is disabled")
                return None

            if definition.type not in self.strategies:
                logger.error("Strategy type not found: {definition.type}")
                return None

            strategy_class = self.strategies[definition.type]
            strategy_instance = strategy_class(definition.parameters)

            self.instances[definition.name] = strategy_instance
            logger.info("Strategy instance created: {definition.name}")

            return strategy_instance

        except Exception as e:
            logger.error("Error creating strategy {definition.name}: %(e)s")
            return None

    def get_strategy(self, name: str) -> Optional[SignalStrategy]:
        """
        获取策略实例

        Args:
            name: 策略名称

        Returns:
            策略实例
        """
        return self.instances.get(name)

    def get_all_strategies(self) -> List[SignalStrategy]:
        """
        获取所有活跃策略实例

        Returns:
            策略实例列表
        """
        return list(self.instances.values())

    def get_enabled_strategies(self) -> List[SignalStrategy]:
        """
        获取所有启用的策略实例

        Returns:
            启用的策略实例列表
        """
        enabled_strategies = []

        for name, instance in self.instances.items():
            definition = self.definitions.get(name)
            if definition and definition.enabled:
                enabled_strategies.append(instance)

        return enabled_strategies

    def enable_strategy(self, name: str) -> bool:
        """
        启用策略

        Args:
            name: 策略名称

        Returns:
            是否成功
        """
        if name in self.definitions:
            self.definitions[name].enabled = True
            logger.info("Strategy enabled: %(name)s")
            return True
        return False

    def disable_strategy(self, name: str) -> bool:
        """
        禁用策略

        Args:
            name: 策略名称

        Returns:
            是否成功
        """
        if name in self.definitions:
            self.definitions[name].enabled = False
            logger.info("Strategy disabled: %(name)s")
            return True
        return False

    def update_strategy_parameters(self, name: str, parameters: Dict[str, Any]) -> bool:
        """
        更新策略参数

        Args:
            name: 策略名称
            parameters: 新参数

        Returns:
            是否成功
        """
        try:
            if name in self.instances:
                # 重新创建策略实例
                definition = self.definitions.get(name)
                if definition:
                    definition.parameters.update(parameters)
                    new_instance = self.create_strategy(definition)
                    if new_instance:
                        logger.info("Strategy parameters updated: %(name)s")
                        return True
            return False

        except Exception as e:
            logger.error("Error updating strategy parameters: %(e)s")
            return False

    def get_strategy_stats(self) -> Dict[str, Any]:
        """获取策略统计信息"""
        total_definitions = len(self.definitions)
        total_instances = len(self.instances)
        enabled_count = sum(1 for d in self.definitions.values() if d.enabled)

        strategy_types = {}
        for definition in self.definitions.values():
            strategy_type = definition.type
            if strategy_type not in strategy_types:
                strategy_types[strategy_type] = 0
            strategy_types[strategy_type] += 1

        return {
            "total_definitions": total_definitions,
            "total_instances": total_instances,
            "enabled_strategies": enabled_count,
            "disabled_strategies": total_definitions - enabled_count,
            "strategy_types": strategy_types,
        }

    def save_to_yaml(self, yaml_path: str):
        """
        保存策略定义到YAML文件

        Args:
            yaml_path: 输出文件路径
        """
        try:
            strategies_config = {
                "strategies": [
                    {
                        "name": definition.name,
                        "type": definition.type,
                        "description": definition.description,
                        "indicators": definition.indicators,
                        "parameters": definition.parameters,
                        "enabled": definition.enabled,
                        "priority": definition.priority,
                    }
                    for definition in self.definitions.values()
                ]
            }

            with open(yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(strategies_config, f, default_flow_style=False, allow_unicode=True)

            logger.info("Strategies saved to %(yaml_path)s")

        except Exception as e:
            logger.error("Error saving strategies to %(yaml_path)s: %(e)s")

    def clear_cache(self):
        """清空缓存的实例"""
        self.instances.clear()
        logger.info("Strategy cache cleared")


# 全局策略注册表实例
_strategy_registry_instance: Optional[StrategyRegistry] = None


def get_strategy_registry() -> StrategyRegistry:
    """获取全局策略注册表实例"""
    global _strategy_registry_instance
    if _strategy_registry_instance is None:
        _strategy_registry_instance = StrategyRegistry()
    return _strategy_registry_instance


# 示例策略配置文件
DEFAULT_STRATEGY_CONFIG = """
strategies:
  - name: rsi_trend_following
    type: rsi_strategy
    description: "RSI趋势跟踪策略"
    indicators: ["rsi"]
    parameters:
      oversold_level: 30
      overbought_level: 70
      risk_reward_ratio: 2.0
      stop_loss_percentage: 0.05
    enabled: true
    priority: 10

  - name: macd_crossover
    type: macd_strategy
    description: "MACD交叉策略"
    indicators: ["macd"]
    parameters:
      fast_period: 12
      slow_period: 26
      signal_period: 9
      risk_reward_ratio: 2.5
      stop_loss_percentage: 0.03
    enabled: true
    priority: 20

  - name: bollinger_reversal
    type: bbands_strategy
    description: "布林带反转策略"
    indicators: ["bbands"]
    parameters:
      period: 20
      std_dev: 2.0
      risk_reward_ratio: 1.8
      stop_loss_percentage: 0.04
    enabled: true
    priority: 15
"""
