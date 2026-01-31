"""
止损执行服务
Stop Loss Execution Service

将止损引擎集成到现有的交易监控框架中，实现自动止损执行。
复用现有的订单管理系统和监控基础设施。
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from src.application.dto.trading_dto import CreateOrderRequest
from src.application.trading.order_mgmt_service import OrderManagementService
from src.governance.risk_management.services.stop_loss_engine import get_stop_loss_engine

# 复用现有的监控基础设施
try:
    from src.monitoring.signal_recorder import get_signal_recorder

    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class StopLossPosition:
    """止损持仓信息"""

    symbol: str
    position_id: str
    entry_price: float
    current_quantity: int
    stop_loss_price: float
    stop_loss_type: str  # 'volatility_adaptive' or 'trailing_stop'
    highest_price: Optional[float] = None  # 用于跟踪止损
    last_check_time: datetime = None
    is_active: bool = True

    def update_highest_price(self, current_price: float):
        """更新最高价（用于跟踪止损）"""
        if self.highest_price is None or current_price > self.highest_price:
            self.highest_price = current_price

    def should_check_stop_loss(self, current_price: float) -> bool:
        """判断是否需要检查止损"""
        if not self.is_active:
            return False

        # 如果是跟踪止损，需要更新最高价
        if self.stop_loss_type == "trailing_stop" and self.highest_price is None:
            self.highest_price = self.entry_price

        return True


class StopLossExecutionService:
    """
    止损执行服务

    集成止损引擎到交易监控框架，实现自动止损执行。
    支持波动率自适应止损和跟踪止损两种策略。
    """

    def __init__(self, order_service: OrderManagementService):
        self.order_service = order_service
        self.stop_loss_engine = get_stop_loss_engine()
        self.signal_recorder = get_signal_recorder() if MONITORING_AVAILABLE else None

        # 持仓监控列表
        self.monitored_positions: Dict[str, StopLossPosition] = {}

        # 执行统计
        self.execution_stats = {
            "total_positions_monitored": 0,
            "stop_loss_triggered": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_pnl_protected": 0.0,
        }

        logger.info("✅ 止损执行服务初始化完成")

    async def add_position_monitoring(
        self,
        symbol: str,
        position_id: str,
        entry_price: float,
        quantity: int,
        stop_loss_type: str = "volatility_adaptive",
        custom_stop_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        添加持仓到止损监控

        Args:
            symbol: 股票代码
            position_id: 持仓ID
            entry_price: 入场价格
            quantity: 持仓数量
            stop_loss_type: 止损类型 ('volatility_adaptive' or 'trailing_stop')
            custom_stop_price: 自定义止损价 (可选)

        Returns:
            监控设置结果
        """
        try:
            # 计算止损价格
            if custom_stop_price:
                stop_loss_price = custom_stop_price
                stop_loss_config = {"custom": True}
            else:
                stop_loss_config = await self._calculate_stop_loss_price(symbol, entry_price, stop_loss_type)
                stop_loss_price = stop_loss_config.get("stop_loss_price", entry_price * 0.95)

            # 创建监控持仓
            position = StopLossPosition(
                symbol=symbol,
                position_id=position_id,
                entry_price=entry_price,
                current_quantity=quantity,
                stop_loss_price=stop_loss_price,
                stop_loss_type=stop_loss_type,
                highest_price=entry_price if stop_loss_type == "trailing_stop" else None,
                last_check_time=datetime.now(),
                is_active=True,
            )

            # 添加到监控列表
            self.monitored_positions[position_id] = position
            self.execution_stats["total_positions_monitored"] += 1

            # 记录到监控系统
            await self._record_position_added(position, stop_loss_config)

            logger.info("✅ 添加止损监控: %(symbol)s %(position_id)s @ %(stop_loss_price)s")

            return {
                "success": True,
                "position_id": position_id,
                "stop_loss_price": stop_loss_price,
                "stop_loss_type": stop_loss_type,
                "monitoring_active": True,
            }

        except Exception as e:
            logger.error("添加止损监控失败 %(symbol)s %(position_id)s: %(e)s")
            return {
                "success": False,
                "error": str(e),
                "position_id": position_id,
            }

    async def update_position_price(self, position_id: str, current_price: float) -> Dict[str, Any]:
        """
        更新持仓价格并检查止损

        Args:
            position_id: 持仓ID
            current_price: 当前价格

        Returns:
            检查结果
        """
        try:
            if position_id not in self.monitored_positions:
                return {"found": False, "position_id": position_id}

            position = self.monitored_positions[position_id]

            if not position.should_check_stop_loss(current_price):
                return {"checked": False, "reason": "position_inactive"}

            # 更新跟踪止损的最高价
            if position.stop_loss_type == "trailing_stop":
                position.update_highest_price(current_price)

                # 重新计算跟踪止损价格
                trailing_result = await self.stop_loss_engine.calculate_trailing_stop_loss(
                    symbol=position.symbol,
                    highest_price=position.highest_price,
                    trailing_percentage=0.08,  # 默认8%
                )

                if trailing_result.get("strategy_type") == "trailing_stop_advanced":
                    position.stop_loss_price = trailing_result["trailing_stop_price"]

            # 检查是否触发止损
            stop_loss_triggered = await self.stop_loss_engine.check_stop_loss_trigger(
                symbol=position.symbol,
                current_price=current_price,
                stop_loss_price=position.stop_loss_price,
            )

            position.last_check_time = datetime.now()

            if stop_loss_triggered:
                # 执行止损
                execution_result = await self._execute_stop_loss_order(position, current_price)
                self.execution_stats["stop_loss_triggered"] += 1

                if execution_result["success"]:
                    self.execution_stats["successful_executions"] += 1
                    # 移除监控
                    position.is_active = False

                return {
                    "checked": True,
                    "stop_loss_triggered": True,
                    "execution_result": execution_result,
                    "position_id": position_id,
                }
            else:
                return {
                    "checked": True,
                    "stop_loss_triggered": False,
                    "current_price": current_price,
                    "stop_loss_price": position.stop_loss_price,
                    "distance_to_stop": ((current_price - position.stop_loss_price) / position.stop_loss_price) * 100,
                    "position_id": position_id,
                }

        except Exception as e:
            logger.error("更新持仓价格失败 %(position_id)s: %(e)s")
            return {
                "checked": False,
                "error": str(e),
                "position_id": position_id,
            }

    async def remove_position_monitoring(self, position_id: str) -> bool:
        """
        移除持仓止损监控

        Args:
            position_id: 持仓ID

        Returns:
            是否成功移除
        """
        try:
            if position_id in self.monitored_positions:
                position = self.monitored_positions[position_id]
                position.is_active = False

                # 记录到监控系统
                await self._record_position_removed(position, "manual_removal")

                del self.monitored_positions[position_id]
                logger.info("✅ 移除止损监控: %(position_id)s")
                return True
            else:
                return False

        except Exception as e:
            logger.error("移除止损监控失败 %(position_id)s: %(e)s")
            return False

    async def get_monitoring_status(self, position_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取监控状态

        Args:
            position_id: 特定持仓ID (可选)

        Returns:
            监控状态信息
        """
        try:
            if position_id:
                position = self.monitored_positions.get(position_id)
                if not position:
                    return {"found": False, "position_id": position_id}

                return {
                    "found": True,
                    "position_id": position_id,
                    "symbol": position.symbol,
                    "entry_price": position.entry_price,
                    "stop_loss_price": position.stop_loss_price,
                    "stop_loss_type": position.stop_loss_type,
                    "highest_price": position.highest_price,
                    "is_active": position.is_active,
                    "last_check_time": position.last_check_time,
                    "time_since_last_check": (
                        (datetime.now() - position.last_check_time).total_seconds()
                        if position.last_check_time
                        else None
                    ),
                }
            else:
                # 返回所有监控持仓的概览
                active_positions = [p for p in self.monitored_positions.values() if p.is_active]
                inactive_positions = [p for p in self.monitored_positions.values() if not p.is_active]

                return {
                    "total_positions": len(self.monitored_positions),
                    "active_positions": len(active_positions),
                    "inactive_positions": len(inactive_positions),
                    "execution_stats": self.execution_stats,
                    "positions": [
                        {
                            "position_id": p.position_id,
                            "symbol": p.symbol,
                            "stop_loss_type": p.stop_loss_type,
                            "is_active": p.is_active,
                        }
                        for p in self.monitored_positions.values()
                    ],
                }

        except Exception as e:
            logger.error("获取监控状态失败: %(e)s")
            return {"error": str(e)}

    async def batch_update_prices(self, price_updates: Dict[str, float]) -> Dict[str, Any]:
        """
        批量更新价格并检查止损

        Args:
            price_updates: {symbol: current_price} 字典

        Returns:
            批量检查结果
        """
        try:
            results = []
            triggered_positions = []

            for position in self.monitored_positions.values():
                if not position.is_active:
                    continue

                symbol = position.symbol
                if symbol in price_updates:
                    current_price = price_updates[symbol]

                    # 更新价格并检查止损
                    check_result = await self.update_position_price(position.position_id, current_price)
                    results.append(check_result)

                    if check_result.get("stop_loss_triggered"):
                        triggered_positions.append(position.position_id)

            return {
                "total_checked": len(results),
                "triggered_count": len(triggered_positions),
                "triggered_positions": triggered_positions,
                "results": results,
            }

        except Exception as e:
            logger.error("批量更新价格失败: %(e)s")
            return {"error": str(e), "total_checked": 0}

    # 私有方法

    async def _calculate_stop_loss_price(self, symbol: str, entry_price: float, stop_loss_type: str) -> Dict[str, Any]:
        """计算止损价格"""
        try:
            if stop_loss_type == "volatility_adaptive":
                result = await self.stop_loss_engine.calculate_volatility_stop_loss(symbol, entry_price)
                return {
                    "stop_loss_price": result.get("stop_loss_price"),
                    "strategy_details": result,
                }
            elif stop_loss_type == "trailing_stop":
                # 跟踪止损初始设置为5%回撤
                return {
                    "stop_loss_price": entry_price * 0.95,
                    "initial_trailing_setup": True,
                }
            else:
                # 默认保守止损
                return {
                    "stop_loss_price": entry_price * 0.95,
                    "fallback": True,
                }

        except Exception as e:
            logger.warning("计算止损价格失败 %(symbol)s: %(e)s")
            return {
                "stop_loss_price": entry_price * 0.95,
                "fallback": True,
                "error": str(e),
            }

    async def _execute_stop_loss_order(self, position: StopLossPosition, current_price: float) -> Dict[str, Any]:
        """执行止损订单"""
        try:
            # 计算损失金额
            loss_amount = (position.stop_loss_price - position.entry_price) * position.current_quantity
            loss_percentage = ((position.stop_loss_price - position.entry_price) / position.entry_price) * 100

            # 创建市价卖出订单 (假设做空止损)
            order_request = CreateOrderRequest(
                symbol=position.symbol,
                quantity=position.current_quantity,
                side="sell",  # 假设止损都是卖出
                order_type="market",
                price=None,  # 市价单
            )

            # 执行订单
            order_response = self.order_service.place_order(order_request)

            # 更新统计
            self.execution_stats["total_pnl_protected"] += abs(loss_amount)

            # 记录到监控系统
            await self._record_stop_loss_execution(position, order_response, loss_amount, loss_percentage)

            logger.info("✅ 止损订单执行成功: {position.symbol} {position.position_id} 损失: {loss_percentage:.2f}%")

            return {
                "success": True,
                "order_id": order_response.order_id,
                "loss_amount": loss_amount,
                "loss_percentage": loss_percentage,
                "execution_price": current_price,
                "position_id": position.position_id,
            }

        except Exception as e:
            logger.error("执行止损订单失败 {position.symbol} {position.position_id}: %(e)s")
            self.execution_stats["failed_executions"] += 1

            return {
                "success": False,
                "error": str(e),
                "position_id": position.position_id,
            }

    async def _record_position_added(self, position: StopLossPosition, config: Dict[str, Any]):
        """记录持仓添加事件"""
        try:
            if self.signal_recorder:
                await self.signal_recorder.record_signal(
                    strategy_id="stop_loss_execution",
                    symbol=position.symbol,
                    signal_type="STOP_LOSS_MONITORING_ADDED",
                    indicator_count=1,
                    execution_time_ms=0.0,
                    gpu_used=False,
                    metadata={
                        "position_id": position.position_id,
                        "entry_price": position.entry_price,
                        "stop_loss_price": position.stop_loss_price,
                        "stop_loss_type": position.stop_loss_type,
                        "quantity": position.current_quantity,
                        "config": config,
                    },
                )
        except Exception as e:
            logger.warning("记录持仓添加失败 {position.position_id}: %(e)s")

    async def _record_position_removed(self, position: StopLossPosition, reason: str):
        """记录持仓移除事件"""
        try:
            if self.signal_recorder:
                await self.signal_recorder.record_signal(
                    strategy_id="stop_loss_execution",
                    symbol=position.symbol,
                    signal_type="STOP_LOSS_MONITORING_REMOVED",
                    indicator_count=1,
                    execution_time_ms=0.0,
                    gpu_used=False,
                    metadata={
                        "position_id": position.position_id,
                        "reason": reason,
                        "final_stop_loss_price": position.stop_loss_price,
                        "highest_price": position.highest_price,
                    },
                )
        except Exception as e:
            logger.warning("记录持仓移除失败 {position.position_id}: %(e)s")

    async def _record_stop_loss_execution(
        self, position: StopLossPosition, order_response: Any, loss_amount: float, loss_percentage: float
    ):
        """记录止损执行事件"""
        try:
            if self.signal_recorder:
                await self.signal_recorder.record_signal(
                    strategy_id="stop_loss_execution",
                    symbol=position.symbol,
                    signal_type="STOP_LOSS_EXECUTED",
                    indicator_count=1,
                    execution_time_ms=0.0,
                    gpu_used=False,
                    metadata={
                        "position_id": position.position_id,
                        "order_id": getattr(order_response, "order_id", None),
                        "entry_price": position.entry_price,
                        "stop_loss_price": position.stop_loss_price,
                        "execution_price": position.stop_loss_price,
                        "loss_amount": loss_amount,
                        "loss_percentage": loss_percentage,
                        "stop_loss_type": position.stop_loss_type,
                        "highest_price": position.highest_price,
                    },
                )
        except Exception as e:
            logger.warning("记录止损执行失败 {position.position_id}: %(e)s")


# 创建全局实例
_stop_loss_execution_service: Optional[StopLossExecutionService] = None


def get_stop_loss_execution_service(order_service: Optional[OrderManagementService] = None) -> StopLossExecutionService:
    """获取止损执行服务实例（单例模式）"""
    global _stop_loss_execution_service
    if _stop_loss_execution_service is None and order_service is not None:
        _stop_loss_execution_service = StopLossExecutionService(order_service)
    return _stop_loss_execution_service
