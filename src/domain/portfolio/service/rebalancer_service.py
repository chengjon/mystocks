"""
Rebalancer Service
再平衡服务

提供投资组合再平衡的领域逻辑。
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class RebalanceAction:
    """再平衡动作"""

    symbol: str
    action: str  # BUY, SELL, HOLD
    target_quantity: int
    current_quantity: int
    weight_diff: float  # 权重差异


class RebalancerService:
    """
    再平衡服务

    职责：
    - 计算目标权重和当前权重的差异
    - 生成再平衡动作列表
    - 支持等权重、市值权重等再平衡策略

    不变量：
    - 所有标的权重之和必须为1（或100%）
    - 再平衡动作不能导致现金为负
    """

    @staticmethod
    def calculate_equal_weights(symbols: List[str]) -> Dict[str, float]:
        """
        计算等权重配置

        Args:
            symbols: 标的列表

        Returns:
            标的 -> 权重映射（权重相等）
        """
        if not symbols:
            return {}

        weight = 1.0 / len(symbols)
        return {symbol: weight for symbol in symbols}

    @staticmethod
    def calculate_current_weights(
        symbols: List[str],
        quantities: List[int],
        prices: List[float],
        total_value: float,
    ) -> Dict[str, float]:
        """
        计算当前权重

        Args:
            symbols: 标的列表
            quantities: 持仓数量列表
            prices: 当前价格列表
            total_value: 总资产

        Returns:
            标的 -> 当前权重映射
        """
        if total_value == 0:
            return {symbol: 0.0 for symbol in symbols}

        weights = {}
        for symbol, quantity, price in zip(symbols, quantities, prices):
            market_value = quantity * price
            weights[symbol] = market_value / total_value

        return weights

    @staticmethod
    def generate_rebalance_actions(
        current_quantities: Dict[str, int],
        target_weights: Dict[str, float],
        current_prices: Dict[str, float],
        total_value: float,
        cash: float,
    ) -> Tuple[List[RebalanceAction], float]:
        """
        生成再平衡动作

        Args:
            current_quantities: 当前持仓数量（标的 -> 数量）
            target_weights: 目标权重（标的 -> 权重）
            current_prices: 当前价格（标的 -> 价格）
            total_value: 总资产
            cash: 可用现金

        Returns:
            (再平衡动作列表, 所需现金)
        """
        actions = []
        required_cash = 0.0

        for symbol, target_weight in target_weights.items():
            current_quantity = current_quantities.get(symbol, 0)
            current_price = current_prices.get(symbol, 0.0)

            if current_price == 0:
                continue

            # 计算目标市值
            target_value = total_value * target_weight
            target_quantity = int(target_value / current_price)

            # 计算权重差异
            current_value = current_quantity * current_price
            current_weight = current_value / total_value if total_value > 0 else 0.0
            weight_diff = target_weight - current_weight

            # 确定动作
            if target_quantity > current_quantity:
                # 需要买入
                action = "BUY"
                cost = (target_quantity - current_quantity) * current_price
                required_cash += cost
            elif target_quantity < current_quantity:
                # 需要卖出
                action = "SELL"
            else:
                # 持有
                action = "HOLD"

            actions.append(
                RebalanceAction(
                    symbol=symbol,
                    action=action,
                    target_quantity=target_quantity,
                    current_quantity=current_quantity,
                    weight_diff=weight_diff,
                )
            )

        return actions, required_cash

    @staticmethod
    def validate_rebalance_feasibility(
        required_cash: float,
        available_cash: float,
        tolerance: float = 0.05,
    ) -> bool:
        """
        验证再平衡可行性

        Args:
            required_cash: 所需现金
            available_cash: 可用现金
            tolerance: 容差比例（默认5%）

        Returns:
            是否可行
        """
        # 所需现金不能超过可用现金（考虑容差）
        return required_cash <= available_cash * (1.0 + tolerance)

    @staticmethod
    def prioritize_rebalance_actions(
        actions: List[RebalanceAction],
    ) -> List[RebalanceAction]:
        """
        优先排序再平衡动作

        优先级：
        1. 卖出动作（释放现金）
        2. 权重差异大的买入动作

        Args:
            actions: 再平衡动作列表

        Returns:
            排序后的再平衡动作列表
        """
        # 卖出动作优先
        sell_actions = [a for a in actions if a.action == "SELL"]
        buy_actions = [a for a in actions if a.action == "BUY"]
        hold_actions = [a for a in actions if a.action == "HOLD"]

        # 买入动作按权重差异降序排列
        buy_actions.sort(key=lambda a: abs(a.weight_diff), reverse=True)

        return sell_actions + buy_actions + hold_actions
