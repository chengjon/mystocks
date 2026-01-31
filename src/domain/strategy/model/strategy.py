"""
策略聚合根
Strategy Aggregate Root

表示交易策略的核心领域对象，管理规则集合并生成交易信号。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from ...trading.model.order import Order
from ...trading.value_objects.order_side import OrderSide
from ..value_objects.strategy_id import StrategyId
from .rule import Rule
from .signal import Signal


@dataclass
class Strategy:
    """
    策略聚合根

    职责：
    - 管理规则集合
    - 维护策略状态
    - 执行信号生成逻辑

    不变式（Invariants）:
    - 策略必须有唯一的ID
    - 策略名称不能为空
    - 规则之间不能有冲突（由业务逻辑保证）
    """

    id: StrategyId
    name: str
    description: str
    rules: List[Rule] = field(default_factory=list)
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, name: str, description: str = "") -> "Strategy":
        """
        创建新策略

        Args:
            name: 策略名称
            description: 策略描述

        Returns:
            Strategy: 新策略实例
        """
        if not name or not name.strip():
            raise ValueError("Strategy name cannot be empty")

        return cls(
            id=StrategyId.generate(), name=name.strip(), description=description.strip(), rules=[], is_active=False
        )

    def add_rule(self, rule: Rule) -> None:
        """
        添加规则

        Args:
            rule: 规则实例

        Raises:
            ValueError: 如果规则冲突
        """
        # 简单验证：同一指标不能有相同操作符和阈值
        for existing_rule in self.rules:
            if (
                existing_rule.indicator_name == rule.indicator_name
                and existing_rule.operator == rule.operator
                and existing_rule.threshold == rule.threshold
                and existing_rule.action == rule.action
            ):
                raise ValueError(f"Duplicate rule: {rule}")

        self.rules.append(rule)
        self.updated_at = datetime.now()

    def activate(self) -> None:
        """激活策略"""
        if not self.rules:
            raise ValueError("Cannot activate strategy without rules")

        self.is_active = True
        self.updated_at = datetime.now()

    def deactivate(self) -> None:
        """停用策略"""
        self.is_active = False
        self.updated_at = datetime.now()

    def execute(self, market_data: Dict[str, Any]) -> List[Signal]:
        """
        执行策略，生成交易信号

        Args:
            market_data: 市场数据字典，必须包含：
                - 'symbol': 标的代码
                - 'price': 当前价格
                - 'indicators': 指标值字典

        Returns:
            List[Signal]: 信号列表

        示例输入：
            market_data = {
                'symbol': '000001.SZ',
                'price': 10.5,
                'indicators': {'RSI': 75.0, 'MACD': 0.5}
            }
        """
        if not self.is_active:
            return []

        # 验证输入数据
        if "symbol" not in market_data:
            raise ValueError("market_data must contain 'symbol'")
        if "price" not in market_data:
            raise ValueError("market_data must contain 'price'")
        if "indicators" not in market_data:
            raise ValueError("market_data must contain 'indicators'")

        symbol = market_data["symbol"]
        price = market_data["price"]
        indicators = market_data["indicators"]

        signals = []

        # 遍历所有规则
        for rule in self.rules:
            try:
                if rule.matches(indicators):
                    # 创建信号
                    side = OrderSide.from_string(rule.action)
                    signal = Signal(
                        signal_id=f"{self.id.value}_{symbol}_{datetime.now().timestamp()}",
                        strategy_id=self.id,
                        symbol=symbol,
                        side=side,
                        price=price,
                        quantity=100,  # Phase 0 简化：固定数量
                        confidence=1.0,
                        reason=f"Rule triggered: {rule}",
                    )
                    signals.append(signal)
            except Exception as e:
                # 记录错误但继续处理其他规则
                print(f"Error executing rule {rule}: {e}")

        return signals

    def convert_signals_to_orders(self, signals: List[Signal]) -> List[Order]:
        """
        将信号转换为订单（Prototype阶段简化实现）

        Args:
            signals: 信号列表

        Returns:
            List[Order]: 订单列表
        """
        orders = []
        for signal in signals:
            order = Order.create(symbol=signal.symbol, quantity=signal.quantity, price=signal.price, side=signal.side)
            order.submit()  # 自动提交订单
            orders.append(order)
        return orders

    @property
    def rule_count(self) -> int:
        """规则数量"""
        return len(self.rules)

    def __str__(self) -> str:
        return f"Strategy(id={self.id}, " f"name={self.name}, " f"rules={self.rule_count}, " f"active={self.is_active})"
