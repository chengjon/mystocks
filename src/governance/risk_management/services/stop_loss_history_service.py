"""
止损策略历史记录和分析服务
Stop Loss Strategy Historical Records and Analysis Service

跟踪和分析止损策略的历史表现，提供策略优化建议。
复用现有的监控和数据存储基础设施。
"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np

# 复用现有的监控基础设施
try:
    from src.monitoring.signal_recorder import get_signal_recorder

    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class StopLossRecord:
    """止损记录"""

    record_id: str
    symbol: str
    position_id: str
    strategy_type: str  # 'volatility_adaptive' or 'trailing_stop'
    entry_price: float
    stop_loss_price: float
    exit_price: Optional[float]
    quantity: int
    entry_time: datetime
    exit_time: Optional[datetime]
    pnl_amount: Optional[float]
    pnl_percentage: Optional[float]
    trigger_reason: str  # 'stop_loss_triggered', 'manual_exit', 'take_profit', etc.
    market_conditions: Dict[str, Any]  # 市场环境数据
    strategy_params: Dict[str, Any]  # 策略参数

    @property
    def holding_period_days(self) -> Optional[float]:
        """持有期天数"""
        if self.exit_time and self.entry_time:
            return (self.exit_time - self.entry_time).total_seconds() / (24 * 3600)
        return None

    @property
    def was_profitable(self) -> Optional[bool]:
        """是否盈利"""
        if self.pnl_amount is not None:
            return self.pnl_amount > 0
        return None


class StopLossHistoryService:
    """
    止损策略历史记录和分析服务

    跟踪所有止损策略的执行历史，提供详细的性能分析和优化建议。
    支持策略回测和参数优化。
    """

    def __init__(self):
        self.signal_recorder = get_signal_recorder() if MONITORING_AVAILABLE else None

        # 内存缓存的历史记录
        self.records_cache: Dict[str, StopLossRecord] = {}
        self.records_by_symbol: Dict[str, List[StopLossRecord]] = defaultdict(list)
        self.records_by_strategy: Dict[str, List[StopLossRecord]] = defaultdict(list)

        # 分析缓存
        self.analysis_cache: Dict[str, Any] = {}
        self.cache_expiry = timedelta(hours=1)

        logger.info("✅ 止损历史分析服务初始化完成")

    async def record_stop_loss_execution(
        self,
        symbol: str,
        position_id: str,
        strategy_type: str,
        entry_price: float,
        stop_loss_price: float,
        exit_price: float,
        quantity: int,
        entry_time: datetime,
        exit_time: datetime,
        trigger_reason: str,
        strategy_params: Dict[str, Any] = None,
        market_conditions: Dict[str, Any] = None,
    ) -> str:
        """
        记录止损执行

        Args:
            symbol: 股票代码
            position_id: 持仓ID
            strategy_type: 策略类型
            entry_price: 入场价格
            stop_loss_price: 止损价格
            exit_price: 退出价格
            quantity: 数量
            entry_time: 入场时间
            exit_time: 退出时间
            trigger_reason: 触发原因
            strategy_params: 策略参数
            market_conditions: 市场条件

        Returns:
            记录ID
        """
        try:
            # 计算PnL
            pnl_amount = (exit_price - entry_price) * quantity
            pnl_percentage = ((exit_price - entry_price) / entry_price) * 100

            # 创建记录
            record_id = f"sl_{symbol}_{position_id}_{exit_time.strftime('%Y%m%d_%H%M%S')}"

            record = StopLossRecord(
                record_id=record_id,
                symbol=symbol,
                position_id=position_id,
                strategy_type=strategy_type,
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                exit_price=exit_price,
                quantity=quantity,
                entry_time=entry_time,
                exit_time=exit_time,
                pnl_amount=pnl_amount,
                pnl_percentage=pnl_percentage,
                trigger_reason=trigger_reason,
                market_conditions=market_conditions or {},
                strategy_params=strategy_params or {},
            )

            # 添加到缓存
            self.records_cache[record_id] = record
            self.records_by_symbol[symbol].append(record)
            self.records_by_strategy[strategy_type].append(record)

            # 记录到监控系统
            await self._record_to_monitoring_system(record)

            logger.info("✅ 止损执行记录成功: %(record_id)s %(symbol)s PnL: {pnl_percentage:.2f}%")

            # 清除分析缓存
            self.analysis_cache.clear()

            return record_id

        except Exception as e:
            logger.error("记录止损执行失败 %(symbol)s %(position_id)s: %(e)s")
            raise

    async def get_strategy_performance(
        self,
        strategy_type: Optional[str] = None,
        symbol: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        获取策略性能分析

        Args:
            strategy_type: 策略类型过滤
            symbol: 股票代码过滤
            date_from: 开始日期
            date_to: 结束日期

        Returns:
            性能分析结果
        """
        try:
            cache_key = f"perf_{strategy_type}_{symbol}_{date_from}_{date_to}"
            if cache_key in self.analysis_cache:
                cached_result = self.analysis_cache[cache_key]
                if datetime.now() - cached_result["generated_at"] < self.cache_expiry:
                    return cached_result

            # 过滤记录
            filtered_records = self._filter_records(strategy_type, symbol, date_from, date_to)

            if not filtered_records:
                return {
                    "total_trades": 0,
                    "message": "无符合条件的记录",
                    "generated_at": datetime.now(),
                }

            # 计算基础指标
            total_trades = len(filtered_records)
            profitable_trades = [r for r in filtered_records if r.was_profitable]
            losing_trades = [r for r in filtered_records if r.was_profitable is False]

            win_rate = len(profitable_trades) / total_trades if total_trades > 0 else 0

            # PnL分析
            total_pnl = sum(r.pnl_amount for r in filtered_records if r.pnl_amount)
            avg_pnl = total_pnl / total_trades if total_trades > 0 else 0

            profitable_pnl = [r.pnl_amount for r in profitable_trades if r.pnl_amount]
            losing_pnl = [r.pnl_amount for r in losing_trades if r.pnl_amount]

            avg_win = np.mean(profitable_pnl) if profitable_pnl else 0
            avg_loss = np.mean(losing_pnl) if losing_pnl else 0

            # 持有期分析
            holding_periods = [r.holding_period_days for r in filtered_records if r.holding_period_days]
            avg_holding_period = np.mean(holding_periods) if holding_periods else 0

            # 最大回撤和最大盈利
            pnl_values = [r.pnl_amount for r in filtered_records if r.pnl_amount]
            max_profit = max(pnl_values) if pnl_values else 0
            max_loss = min(pnl_values) if pnl_values else 0

            # 风险调整指标
            if avg_loss != 0:
                profit_factor = abs(sum(profitable_pnl) / sum(losing_pnl)) if losing_pnl else float("inf")
                win_loss_ratio = avg_win / abs(avg_loss) if avg_loss != 0 else float("inf")
            else:
                profit_factor = float("inf")
                win_loss_ratio = float("inf")

            # 月度表现
            monthly_performance = self._calculate_monthly_performance(filtered_records)

            result = {
                "total_trades": total_trades,
                "win_rate": win_rate,
                "total_pnl": total_pnl,
                "avg_pnl": avg_pnl,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "max_profit": max_profit,
                "max_loss": max_loss,
                "profit_factor": profit_factor,
                "win_loss_ratio": win_loss_ratio,
                "avg_holding_period_days": avg_holding_period,
                "monthly_performance": monthly_performance,
                "filters": {
                    "strategy_type": strategy_type,
                    "symbol": symbol,
                    "date_from": date_from,
                    "date_to": date_to,
                },
                "generated_at": datetime.now(),
            }

            # 缓存结果
            self.analysis_cache[cache_key] = result

            return result

        except Exception as e:
            logger.error("获取策略性能分析失败: %(e)s")
            return {
                "error": str(e),
                "total_trades": 0,
                "generated_at": datetime.now(),
            }

    async def get_strategy_recommendations(self, strategy_type: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        获取策略优化建议

        Args:
            strategy_type: 策略类型
            symbol: 股票代码 (可选)

        Returns:
            优化建议
        """
        try:
            # 获取历史表现
            performance = await self.get_strategy_performance(strategy_type, symbol)

            if performance["total_trades"] == 0:
                return {
                    "recommendations": ["无足够的历史数据进行分析"],
                    "confidence": "low",
                    "generated_at": datetime.now(),
                }

            recommendations = []

            # 胜率分析
            win_rate = performance["win_rate"]
            if win_rate > 0.7:
                recommendations.append("策略胜率良好，可以考虑增加仓位")
            elif win_rate < 0.5:
                recommendations.append("策略胜率偏低，建议调整参数或更换策略")
            else:
                recommendations.append("策略胜率中等，可以继续使用")

            # 盈亏比分析
            win_loss_ratio = performance["win_loss_ratio"]
            if win_loss_ratio > 3:
                recommendations.append("盈亏比较好，建议保持当前止损设置")
            elif win_loss_ratio < 1.5:
                recommendations.append("盈亏比较低，建议放宽止损以提高胜率")

            # 持有期分析
            avg_holding = performance["avg_holding_period_days"]
            if avg_holding < 1:
                recommendations.append("平均持有期较短，适合日内交易")
            elif avg_holding > 30:
                recommendations.append("平均持有期较长，适合长期投资")

            # 利润因子分析
            profit_factor = performance["profit_factor"]
            if profit_factor > 2:
                recommendations.append("利润因子优秀，策略表现非常好")
            elif profit_factor < 1.5:
                recommendations.append("利润因子一般，建议优化入场时机")

            # 基于策略类型的特殊建议
            if strategy_type == "volatility_adaptive":
                recommendations.extend(self._get_volatility_adaptive_recommendations(performance))
            elif strategy_type == "trailing_stop":
                recommendations.extend(self._get_trailing_stop_recommendations(performance))

            return {
                "recommendations": recommendations,
                "performance_summary": {
                    "win_rate": win_rate,
                    "profit_factor": profit_factor,
                    "avg_holding_period": avg_holding,
                    "total_trades": performance["total_trades"],
                },
                "confidence": "high" if performance["total_trades"] > 10 else "medium",
                "generated_at": datetime.now(),
            }

        except Exception as e:
            logger.error("获取策略建议失败 %(strategy_type)s: %(e)s")
            return {
                "error": str(e),
                "recommendations": ["无法生成建议"],
                "confidence": "low",
                "generated_at": datetime.now(),
            }

    async def backtest_strategy(
        self,
        strategy_type: str,
        symbol: str,
        historical_prices: List[float],
        entry_signals: List[bool],
        strategy_params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        回测止损策略

        Args:
            strategy_type: 策略类型
            symbol: 股票代码
            historical_prices: 历史价格序列
            entry_signals: 入场信号序列
            strategy_params: 策略参数

        Returns:
            回测结果
        """
        try:
            if not strategy_params:
                strategy_params = {}

            trades = []
            current_position = None

            for i, (price, entry_signal) in enumerate(zip(historical_prices, entry_signals)):
                if entry_signal and current_position is None:
                    # 开仓
                    current_position = {
                        "entry_price": price,
                        "entry_index": i,
                        "quantity": 1,  # 简化假设
                    }

                elif current_position is not None:
                    # 检查是否应该止损
                    should_exit = await self._simulate_stop_loss_check(
                        strategy_type, symbol, current_position["entry_price"], price, strategy_params
                    )

                    if should_exit:
                        # 平仓
                        exit_price = price
                        pnl_amount = (exit_price - current_position["entry_price"]) * current_position["quantity"]
                        pnl_percentage = (
                            (exit_price - current_position["entry_price"]) / current_position["entry_price"]
                        ) * 100

                        trades.append(
                            {
                                "entry_price": current_position["entry_price"],
                                "exit_price": exit_price,
                                "pnl_amount": pnl_amount,
                                "pnl_percentage": pnl_percentage,
                                "holding_period": i - current_position["entry_index"],
                            }
                        )

                        current_position = None

            # 计算回测统计
            if trades:
                pnl_values = [t["pnl_amount"] for t in trades]
                win_rate = len([t for t in trades if t["pnl_amount"] > 0]) / len(trades)

                return {
                    "total_trades": len(trades),
                    "win_rate": win_rate,
                    "total_pnl": sum(pnl_values),
                    "avg_pnl": np.mean(pnl_values),
                    "max_profit": max(pnl_values),
                    "max_loss": min(pnl_values),
                    "sharpe_ratio": self._calculate_sharpe_ratio(pnl_values),
                    "trades": trades,
                }
            else:
                return {
                    "total_trades": 0,
                    "message": "回测期间无交易",
                }

        except Exception as e:
            logger.error("策略回测失败 %(strategy_type)s %(symbol)s: %(e)s")
            return {"error": str(e)}

    def get_records_summary(self) -> Dict[str, Any]:
        """获取记录汇总统计"""
        try:
            total_records = len(self.records_cache)
            symbols_count = len(self.records_by_symbol)
            strategies_count = len(self.records_by_strategy)

            # 按策略类型统计
            strategy_stats = {}
            for strategy, records in self.records_by_strategy.items():
                profitable = [r for r in records if r.was_profitable]
                win_rate = len(profitable) / len(records) if records else 0
                total_pnl = sum(r.pnl_amount for r in records if r.pnl_amount)

                strategy_stats[strategy] = {
                    "total_trades": len(records),
                    "win_rate": win_rate,
                    "total_pnl": total_pnl,
                }

            return {
                "total_records": total_records,
                "unique_symbols": symbols_count,
                "unique_strategies": strategies_count,
                "strategy_stats": strategy_stats,
                "generated_at": datetime.now(),
            }

        except Exception as e:
            logger.error("获取记录汇总失败: %(e)s")
            return {"error": str(e)}

    # 私有方法

    def _filter_records(
        self,
        strategy_type: Optional[str],
        symbol: Optional[str],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> List[StopLossRecord]:
        """过滤记录"""
        records = list(self.records_cache.values())

        if strategy_type:
            records = [r for r in records if r.strategy_type == strategy_type]

        if symbol:
            records = [r for r in records if r.symbol == symbol]

        if date_from:
            records = [r for r in records if r.entry_time >= date_from]

        if date_to:
            records = [r for r in records if r.exit_time and r.exit_time <= date_to]

        return records

    def _calculate_monthly_performance(self, records: List[StopLossRecord]) -> Dict[str, Any]:
        """计算月度表现"""
        monthly_stats = defaultdict(lambda: {"trades": 0, "pnl": 0.0, "wins": 0})

        for record in records:
            if record.exit_time:
                month_key = record.exit_time.strftime("%Y-%m")
                monthly_stats[month_key]["trades"] += 1
                if record.pnl_amount:
                    monthly_stats[month_key]["pnl"] += record.pnl_amount
                if record.was_profitable:
                    monthly_stats[month_key]["wins"] += 1

        # 计算胜率和月度PnL
        result = {}
        for month, stats in monthly_stats.items():
            win_rate = stats["wins"] / stats["trades"] if stats["trades"] > 0 else 0
            result[month] = {
                "trades": stats["trades"],
                "pnl": stats["pnl"],
                "win_rate": win_rate,
            }

        return dict(result)

    def _calculate_sharpe_ratio(self, pnl_values: List[float]) -> float:
        """计算夏普比率"""
        if len(pnl_values) < 2:
            return 0.0

        returns = np.array(pnl_values)
        avg_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return float("inf") if avg_return > 0 else float("-inf")

        # 简化的夏普比率计算 (假设无风险利率为0)
        return avg_return / std_return

    def _get_volatility_adaptive_recommendations(self, performance: Dict[str, Any]) -> List[str]:
        """波动率自适应策略的特殊建议"""
        recommendations = []

        win_rate = performance.get("win_rate", 0)
        avg_holding = performance.get("avg_holding_period_days", 0)

        if win_rate < 0.6 and avg_holding < 5:
            recommendations.append("胜率偏低且持有期短，建议增加ATR倍数以减少止损触发")
        elif win_rate > 0.75:
            recommendations.append("胜率良好，可以尝试减少ATR倍数以提高盈利")

        return recommendations

    def _get_trailing_stop_recommendations(self, performance: Dict[str, Any]) -> List[str]:
        """跟踪止损策略的特殊建议"""
        recommendations = []

        win_rate = performance.get("win_rate", 0)
        avg_holding = performance.get("avg_holding_period_days", 0)

        if win_rate > 0.8 and avg_holding > 20:
            recommendations.append("胜率高且持有期长，适合使用跟踪止损保护利润")
        elif win_rate < 0.5:
            recommendations.append("胜率偏低，建议减少跟踪百分比或结合其他过滤条件")

        return recommendations

    async def _record_to_monitoring_system(self, record: StopLossRecord):
        """记录到监控系统"""
        try:
            if self.signal_recorder:
                await self.signal_recorder.record_signal(
                    strategy_id="stop_loss_history",
                    symbol=record.symbol,
                    signal_type="STOP_LOSS_RECORD",
                    indicator_count=1,
                    execution_time_ms=0.0,
                    gpu_used=False,
                    metadata={
                        "record_id": record.record_id,
                        "position_id": record.position_id,
                        "strategy_type": record.strategy_type,
                        "pnl_amount": record.pnl_amount,
                        "pnl_percentage": record.pnl_percentage,
                        "trigger_reason": record.trigger_reason,
                        "holding_period_days": record.holding_period_days,
                    },
                )
        except Exception as e:
            logger.warning("记录到监控系统失败 {record.record_id}: %(e)s")

    async def _simulate_stop_loss_check(
        self, strategy_type: str, symbol: str, entry_price: float, current_price: float, strategy_params: Dict[str, Any]
    ) -> bool:
        """模拟止损检查"""
        try:
            from src.governance.risk_management.services.stop_loss_engine import get_stop_loss_engine

            stop_loss_engine = get_stop_loss_engine()

            if strategy_type == "volatility_adaptive":
                # 简化的波动率止损检查
                stop_result = await stop_loss_engine.calculate_volatility_stop_loss(symbol, entry_price)
                stop_price = stop_result.get("stop_loss_price", entry_price * 0.95)
                return current_price <= stop_price

            elif strategy_type == "trailing_stop":
                # 简化的跟踪止损检查
                trailing_result = await stop_loss_engine.calculate_trailing_stop_loss(
                    symbol, entry_price, trailing_percentage=strategy_params.get("trailing_percentage", 0.08)
                )
                return trailing_result.get("should_trigger", False)

            return False

        except Exception as e:
            logger.warning("模拟止损检查失败 %(strategy_type)s %(symbol)s: %(e)s")
            return False


# 创建全局实例
_stop_loss_history_service: Optional[StopLossHistoryService] = None


def get_stop_loss_history_service() -> StopLossHistoryService:
    """获取止损历史分析服务实例（单例模式）"""
    global _stop_loss_history_service
    if _stop_loss_history_service is None:
        _stop_loss_history_service = StopLossHistoryService()
    return _stop_loss_history_service
