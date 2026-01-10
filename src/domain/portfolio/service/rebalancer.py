"""
Rebalancer Domain Service
投资组合再平衡服务
"""
from typing import Dict, List, Any
from ..model.portfolio import Portfolio
from src.domain.trading.value_objects import OrderSide

# 简单的 DTO，用于描述再平衡建议
from dataclasses import dataclass

@dataclass
class RebalanceOrderRequest:
    symbol: str
    side: OrderSide
    quantity: int
    target_weight: float
    current_weight: float

class RebalancerService:
    """
    再平衡服务
    根据目标权重，计算需要买卖的订单
    """
    
    def calculate_rebalance_orders(
        self, 
        portfolio: Portfolio, 
        target_weights: Dict[str, float]
    ) -> List[RebalanceOrderRequest]:
        """
        计算调仓指令
        
        Args:
            portfolio: 当前投资组合
            target_weights: 目标权重字典 {symbol: weight} (weight: 0.0 - 1.0)
            
        Returns:
            List[RebalanceOrderRequest]: 建议的订单列表
        """
        # 1. 计算当前总资产 (使用持仓中已更新的 current_price)
        perf = portfolio.calculate_performance()
        total_assets = perf.total_value
        
        requests = []
        
        # 2. 遍历目标权重
        for symbol, target_weight in target_weights.items():
            target_value = total_assets * target_weight
            
            # 获取当前持仓
            current_pos = portfolio.positions.get(symbol)
            current_price = current_pos.current_price if current_pos else 0.0
            
            # 如果没有当前价格（例如新股），无法计算数量，跳过或报错
            if current_price <= 0:
                # 实际场景可能需要调用 MarketData Context 获取价格
                # 这里假设 Portfolio 已经更新了最新价格
                continue
                
            current_value = current_pos.market_value if current_pos else 0.0
            current_weight = current_value / total_assets if total_assets > 0 else 0.0
            
            diff_value = target_value - current_value
            
            # 忽略过小的变动 (例如小于 100 元)
            if abs(diff_value) < 100:
                continue
                
            quantity = int(abs(diff_value) / current_price)
            # 向下取整到 100 的倍数 (A股手数)
            quantity = (quantity // 100) * 100
            
            if quantity == 0:
                continue
                
            side = OrderSide.BUY if diff_value > 0 else OrderSide.SELL
            
            requests.append(RebalanceOrderRequest(
                symbol=symbol,
                side=side,
                quantity=quantity,
                target_weight=target_weight,
                current_weight=current_weight
            ))
            
        return requests
