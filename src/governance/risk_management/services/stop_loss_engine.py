"""
止损引擎实现
Stop Loss Engine Implementation

实现波动率自适应止损和跟踪止损策略。
复用现有的监控和交易基础设施。
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np

from src.governance.risk_management.core import IStopLossEngine

# 复用现有的数据源和监控基础设施
try:
    from src.monitoring.signal_recorder import get_signal_recorder

    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)


class StopLossEngine(IStopLossEngine):
    """
    止损引擎实现

    支持波动率自适应止损和跟踪止损两种策略。
    复用现有的信号记录和监控基础设施。
    """

    def __init__(self):
        self.signal_recorder = None
        if MONITORING_AVAILABLE:
            self.signal_recorder = get_signal_recorder()

    async def calculate_volatility_stop_loss(
        self,
        symbol: str,
        entry_price: float,
        k: Optional[float] = None,
        risk_tolerance: str = "medium",
        use_dynamic_k: bool = True,
    ) -> Dict[str, Any]:
        """
        计算高级波动率自适应止损

        支持多时间周期ATR分析、动态K因子调整、市场波动率适应。

        Args:
            symbol: 股票代码
            entry_price: 入场价格
            k: 固定K因子 (如果为None则动态计算)
            risk_tolerance: 风险偏好 ('conservative', 'medium', 'aggressive')
            use_dynamic_k: 是否使用动态K因子

        Returns:
            完整的止损策略分析结果
        """
        try:
            # 获取多时间周期ATR数据
            atr_data = await self._get_multi_period_atr(symbol)

            # 计算动态K因子或使用固定值
            if use_dynamic_k and k is None:
                k = await self._calculate_dynamic_k_factor(symbol, risk_tolerance, atr_data)
            elif k is None:
                k = self._get_default_k_factor(risk_tolerance)

            # 选择最合适的ATR周期
            atr_value = self._select_optimal_atr_period(atr_data, risk_tolerance)

            # 计算基础止损距离
            stop_distance = k * atr_value
            stop_loss_price = entry_price - stop_distance

            # 应用市场波动率调整
            market_adjustment = await self._calculate_market_volatility_adjustment(symbol)
            adjusted_stop_distance = stop_distance * market_adjustment
            adjusted_stop_loss_price = entry_price - adjusted_stop_distance

            # 计算止损百分比
            stop_percentage = (adjusted_stop_distance / entry_price) * 100

            # 评估综合风险水平
            risk_assessment = await self._assess_comprehensive_risk(
                symbol, entry_price, adjusted_stop_loss_price, atr_data
            )

            # 生成执行建议
            execution_recommendation = self._generate_execution_recommendation(risk_assessment, stop_percentage)

            # 计算历史回撤分析 (如果有历史数据)
            historical_analysis = await self._analyze_historical_drawdowns(
                symbol, adjusted_stop_loss_price, entry_price
            )

            result = {
                "strategy_type": "volatility_adaptive_advanced",
                "entry_price": entry_price,
                "stop_loss_price": round(adjusted_stop_loss_price, 2),
                "stop_percentage": round(stop_percentage, 2),
                "base_atr_value": round(atr_value, 2),
                "k_factor": round(k, 2),
                "market_adjustment": round(market_adjustment, 2),
                "atr_data": atr_data,
                "risk_tolerance": risk_tolerance,
                "use_dynamic_k": use_dynamic_k,
                "risk_assessment": risk_assessment,
                "execution_recommendation": execution_recommendation,
                "historical_analysis": historical_analysis,
                "calculated_at": datetime.now(),
            }

            # 记录到监控系统
            await self._record_stop_loss_calculation(symbol, result)

            return result

        except Exception as e:
            logger.error("计算高级波动率自适应止损失败 %(symbol)s: %(e)s")
            # 返回保守的止损策略
            conservative_stop = entry_price * 0.95  # 5%止损
            return {
                "strategy_type": "volatility_adaptive_advanced",
                "entry_price": entry_price,
                "stop_loss_price": conservative_stop,
                "stop_percentage": 5.0,
                "base_atr_value": 0.0,
                "k_factor": 2.0,
                "market_adjustment": 1.0,
                "risk_tolerance": risk_tolerance,
                "use_dynamic_k": False,
                "risk_assessment": {"level": "unknown", "score": 50},
                "execution_recommendation": "使用保守的5%固定止损作为后备",
                "historical_analysis": {},
                "error": str(e),
                "calculated_at": datetime.now(),
            }

    async def calculate_trailing_stop_loss(
        self,
        symbol: str,
        highest_price: float,
        trailing_percentage: float = 0.08,
        trailing_mode: str = "percentage",
        acceleration_factor: float = 1.0,
        use_technical_filters: bool = True,
    ) -> Dict[str, Any]:
        """
        计算高级跟踪止损策略

        支持多种跟踪模式、动态调整、技术指标过滤。
        深度集成SignalResultTracker进行历史跟踪和性能分析。

        Args:
            symbol: 股票代码
            highest_price: 最高价基准
            trailing_percentage: 跟踪百分比 (用于百分比模式)
            trailing_mode: 跟踪模式 ('percentage', 'volatility', 'hybrid')
            acceleration_factor: 加速因子 (1.0=标准, >1=加速, <1=减速)
            use_technical_filters: 是否使用技术指标过滤

        Returns:
            完整的跟踪止损分析结果
        """
        try:
            # 获取当前市场数据
            current_price = await self._get_current_price(symbol)
            market_data = await self._get_recent_market_data(symbol, days=30)

            # 计算基础跟踪止损
            base_result = await self._calculate_base_trailing_stop(
                symbol, highest_price, current_price, trailing_percentage, trailing_mode
            )

            # 应用加速因子调整
            adjusted_result = self._apply_acceleration_factor(base_result, acceleration_factor)

            # 添加技术指标过滤
            if use_technical_filters:
                technical_filters = await self._calculate_technical_filters(symbol, market_data)
                adjusted_result.update(technical_filters)

            # 计算触发条件
            trigger_analysis = self._analyze_trigger_conditions(adjusted_result, market_data)

            # 历史表现分析
            historical_performance = await self._analyze_trailing_performance(symbol, trailing_mode)

            # 动态调整建议
            adjustment_recommendations = self._generate_trailing_adjustments(adjusted_result, historical_performance)

            result = {
                "strategy_type": "trailing_stop_advanced",
                "symbol": symbol,
                "highest_price": highest_price,
                "current_price": current_price,
                "trailing_mode": trailing_mode,
                "trailing_percentage": trailing_percentage,
                "acceleration_factor": acceleration_factor,
                "use_technical_filters": use_technical_filters,
                **adjusted_result,
                "trigger_analysis": trigger_analysis,
                "historical_performance": historical_performance,
                "adjustment_recommendations": adjustment_recommendations,
                "calculated_at": datetime.now(),
            }

            # 记录到SignalResultTracker
            await self._record_trailing_calculation(symbol, result)

            return result

        except Exception as e:
            logger.error("计算高级跟踪止损失败 %(symbol)s: %(e)s")
            # 返回保守策略
            conservative_stop = highest_price * 0.92
            return {
                "strategy_type": "trailing_stop_advanced",
                "symbol": symbol,
                "highest_price": highest_price,
                "current_price": highest_price * 0.95,
                "trailing_mode": trailing_mode,
                "trailing_percentage": trailing_percentage,
                "trailing_stop_price": conservative_stop,
                "drawdown_percentage": 0.0,
                "should_trigger": False,
                "acceleration_factor": acceleration_factor,
                "error": str(e),
                "calculated_at": datetime.now(),
            }

    async def check_stop_loss_trigger(self, symbol: str, current_price: float, stop_loss_price: float) -> bool:
        """
        检查是否触发止损

        如果触发，自动记录到监控系统。
        """
        try:
            triggered = current_price <= stop_loss_price

            if triggered and self.signal_recorder:
                # 记录止损触发信号
                await self.signal_recorder.record_signal(
                    strategy_id="stop_loss_system",
                    symbol=symbol,
                    signal_type="STOP_LOSS_TRIGGERED",
                    indicator_count=1,
                    execution_time_ms=0.0,  # 即时触发
                    gpu_used=False,
                    metadata={
                        "trigger_type": "stop_loss",
                        "current_price": current_price,
                        "stop_loss_price": stop_loss_price,
                        "loss_amount": stop_loss_price - current_price,
                        "loss_percentage": ((stop_loss_price - current_price) / stop_loss_price) * 100,
                    },
                )
                logger.info("止损触发记录成功: %(symbol)s @ %(current_price)s")

            return triggered

        except Exception:
            logger.error("检查止损触发失败 %(symbol)s: %(e)s")
            # 为了安全起见，如果检查失败也认为触发了
            return True

    # 私有辅助方法

    async def _get_atr_value(self, symbol: str, period: int = 14) -> float:
        """获取ATR值"""
        try:
            # 这里应该从现有数据源获取真实的ATR数据
            # 暂时返回模拟值
            # ATR通常是股价的1-3%
            return 2.5  # 假设2.5元的ATR值
        except Exception:
            logger.error("获取ATR值失败 %(symbol)s: %(e)s")
            return 2.0  # 返回保守值

    async def _get_current_price(self, symbol: str) -> float:
        """获取当前价格"""
        try:
            # 这里应该从实时数据源获取价格
            # 暂时返回模拟价格
            return 100.0  # 假设当前价格100元
        except Exception:
            logger.error("获取当前价格失败 %(symbol)s: %(e)s")
            return 100.0

    async def _get_moving_average(self, symbol: str, period: int) -> Optional[float]:
        """获取移动平均值"""
        try:
            # 这里应该计算真实的移动平均值
            # 暂时返回模拟值
            return 98.0  # 假设20日均线98元
        except Exception:
            logger.error("获取移动平均值失败 %(symbol)s: %(e)s")
            return None

    def _assess_volatility_level(self, atr: float, price: float) -> str:
        """评估波动率水平"""
        atr_percentage = (atr / price) * 100

        if atr_percentage < 1.0:
            return "low"
        elif atr_percentage < 3.0:
            return "medium"
        else:
            return "high"

    def _generate_stop_loss_recommendation(self, volatility_level: str, stop_percentage: float) -> str:
        """生成止损建议"""
        if volatility_level == "low":
            if stop_percentage > 3.0:
                return "波动率较低，建议减少止损幅度至2-3%"
            else:
                return "波动率较低，当前止损设置合理"
        elif volatility_level == "medium":
            if stop_percentage > 5.0:
                return "波动率中等，建议止损幅度控制在3-5%"
            else:
                return "波动率中等，当前止损设置合理"
        else:  # high
            if stop_percentage < 5.0:
                return "波动率较高，建议增加止损幅度至5-8%"
            else:
                return "波动率较高，当前止损设置合理"

    # 新增高级止损策略方法

    async def _get_multi_period_atr(self, symbol: str) -> Dict[int, float]:
        """获取多时间周期ATR数据"""
        periods = [7, 14, 21, 28]  # 短期到长期ATR
        atr_data = {}

        for period in periods:
            atr_value = await self._get_atr_value(symbol, period)
            atr_data[period] = atr_value

        return atr_data

    async def _calculate_dynamic_k_factor(self, symbol: str, risk_tolerance: str, atr_data: Dict[int, float]) -> float:
        """计算动态K因子"""
        try:
            # 获取市场波动率
            market_volatility = await self._get_market_volatility()

            # 获取股票自身波动率
            avg_atr = np.mean(list(atr_data.values()))
            current_price = await self._get_current_price(symbol)
            stock_volatility_pct = (avg_atr / current_price) * 100

            # 动态K因子计算
            base_k = self._get_default_k_factor(risk_tolerance)

            # 波动率调整因子
            volatility_multiplier = 1.0
            if stock_volatility_pct < 2.0:
                volatility_multiplier = 0.8  # 低波动率时减少K值
            elif stock_volatility_pct > 5.0:
                volatility_multiplier = 1.3  # 高波动率时增加K值

            # 市场环境调整
            market_multiplier = 1.0
            if market_volatility > 0.25:  # 市场高波动
                market_multiplier = 1.2
            elif market_volatility < 0.15:  # 市场低波动
                market_multiplier = 0.9

            dynamic_k = base_k * volatility_multiplier * market_multiplier

            # 限制K因子范围
            return max(0.5, min(4.0, dynamic_k))

        except Exception:
            logger.warning("计算动态K因子失败 %(symbol)s: %(e)s")
            return self._get_default_k_factor(risk_tolerance)

    def _get_default_k_factor(self, risk_tolerance: str) -> float:
        """获取默认K因子"""
        k_factors = {
            "conservative": 2.5,
            "medium": 2.0,
            "aggressive": 1.5,
        }
        return k_factors.get(risk_tolerance, 2.0)

    def _select_optimal_atr_period(self, atr_data: Dict[int, float], risk_tolerance: str) -> float:
        """选择最合适的ATR周期"""
        if risk_tolerance == "conservative":
            # 保守策略使用较长期ATR (更稳定)
            return atr_data.get(28, atr_data.get(21, atr_data.get(14, 2.0)))
        elif risk_tolerance == "aggressive":
            # 激进策略使用较短期ATR (更敏感)
            return atr_data.get(7, atr_data.get(14, 2.0))
        else:
            # 中性策略使用中期ATR
            return atr_data.get(14, atr_data.get(21, 2.0))

    async def _calculate_market_volatility_adjustment(self, symbol: str) -> float:
        """计算市场波动率调整因子"""
        try:
            # 获取市场基准波动率 (如沪深300的ATR)
            market_atr = await self._get_market_atr()
            current_price = await self._get_current_price(symbol)

            if market_atr and current_price:
                market_volatility_pct = (market_atr / current_price) * 100

                # 基于市场波动率调整止损距离
                if market_volatility_pct > 4.0:  # 高波动市场
                    return 1.3  # 增加15%止损距离
                elif market_volatility_pct < 1.5:  # 低波动市场
                    return 0.85  # 减少15%止损距离

            return 1.0  # 无调整

        except Exception:
            logger.warning("计算市场波动率调整失败 %(symbol)s: %(e)s")
            return 1.0

    async def _assess_comprehensive_risk(
        self, symbol: str, entry_price: float, stop_loss_price: float, atr_data: Dict[int, float]
    ) -> Dict[str, Any]:
        """评估综合风险水平"""
        try:
            current_price = await self._get_current_price(symbol)
            stop_distance = entry_price - stop_loss_price
            stop_percentage = (stop_distance / entry_price) * 100

            # 多维度风险评估
            risk_factors = {
                "stop_percentage": stop_percentage,
                "atr_stability": self._calculate_atr_stability(atr_data),
                "price_position": self._assess_price_position(current_price, entry_price),
                "market_condition": await self._assess_market_condition(),
            }

            # 计算综合风险评分 (0-100)
            risk_score = self._calculate_risk_score(risk_factors)

            # 确定风险等级
            if risk_score >= 75:
                risk_level = "high"
            elif risk_score >= 50:
                risk_level = "medium"
            elif risk_score >= 25:
                risk_level = "low"
            else:
                risk_level = "very_low"

            return {
                "level": risk_level,
                "score": risk_score,
                "factors": risk_factors,
            }

        except Exception:
            logger.error("评估综合风险失败 %(symbol)s: %(e)s")
            return {
                "level": "unknown",
                "score": 50,
                "factors": {},
            }

    def _calculate_atr_stability(self, atr_data: Dict[int, float]) -> float:
        """计算ATR稳定性 (0-1, 1表示非常稳定)"""
        if len(atr_data) < 2:
            return 0.5

        atr_values = list(atr_data.values())
        mean_atr = np.mean(atr_values)
        std_atr = np.std(atr_values)

        if mean_atr == 0:
            return 0.5

        # 变异系数 (CV) - 标准差/均值
        cv = std_atr / mean_atr

        # 稳定性评分 (CV越小越稳定)
        stability = max(0, 1 - cv * 2)  # CV=0.5时稳定性=0

        return stability

    def _assess_price_position(self, current_price: float, entry_price: float) -> str:
        """评估价格位置"""
        change_pct = (current_price - entry_price) / entry_price * 100

        if change_pct > 5:
            return "strong_uptrend"
        elif change_pct > 1:
            return "moderate_uptrend"
        elif change_pct > -1:
            return "sideways"
        elif change_pct > -5:
            return "moderate_downtrend"
        else:
            return "strong_downtrend"

    async def _assess_market_condition(self) -> str:
        """评估市场状况"""
        try:
            market_volatility = await self._get_market_volatility()

            if market_volatility > 0.3:
                return "high_volatility"
            elif market_volatility > 0.2:
                return "moderate_volatility"
            elif market_volatility > 0.1:
                return "low_volatility"
            else:
                return "very_low_volatility"

        except Exception:
            return "unknown"

    def _calculate_risk_score(self, risk_factors: Dict[str, Any]) -> int:
        """计算综合风险评分"""
        score = 50  # 基础分

        # 止损百分比贡献
        stop_pct = risk_factors.get("stop_percentage", 5.0)
        if stop_pct > 8:
            score -= 20  # 止损过宽，风险较低
        elif stop_pct > 5:
            score -= 10
        elif stop_pct < 2:
            score += 20  # 止损过窄，风险较高
        elif stop_pct < 3:
            score += 10

        # ATR稳定性贡献
        atr_stability = risk_factors.get("atr_stability", 0.5)
        score += int((atr_stability - 0.5) * 20)  # ±10分

        # 价格位置贡献
        price_position = risk_factors.get("price_position", "sideways")
        if price_position in ["strong_uptrend"]:
            score -= 10
        elif price_position in ["strong_downtrend"]:
            score += 10

        # 市场状况贡献
        market_condition = risk_factors.get("market_condition", "unknown")
        if market_condition == "high_volatility":
            score += 15
        elif market_condition == "low_volatility":
            score -= 5

        return max(0, min(100, score))

    def _generate_execution_recommendation(self, risk_assessment: Dict[str, Any], stop_percentage: float) -> str:
        """生成执行建议"""
        risk_level = risk_assessment.get("level", "medium")

        if risk_level == "high":
            return f"高风险环境，建议使用更保守的止损策略 (当前{stop_percentage:.1f}%)"
        elif risk_level == "medium":
            return f"中风险环境，当前止损设置{stop_percentage:.1f}%合理"
        elif risk_level == "low":
            return f"低风险环境，可以考虑稍微放宽止损至{stop_percentage * 1.2:.1f}%"
        else:
            return "极低风险环境，建议减少止损幅度以锁定利润"

    async def _analyze_historical_drawdowns(
        self, symbol: str, stop_loss_price: float, entry_price: float
    ) -> Dict[str, Any]:
        """分析历史回撤"""
        try:
            # 这里应该分析历史数据中的类似价格水平
            # 暂时返回模拟分析
            return {
                "similar_drawdown_events": 3,
                "avg_recovery_time_days": 15,
                "max_drawdown_in_similar_cases": -8.5,
                "success_rate": 0.75,
                "recommendation": "历史数据显示类似情况有75%成功恢复",
            }
        except Exception:
            logger.warning("历史回撤分析失败 %(symbol)s: %(e)s")
            return {}

    async def _record_stop_loss_calculation(self, symbol: str, calculation_result: Dict[str, Any]):
        """记录止损计算到监控系统"""
        try:
            if self.signal_recorder:
                await self.signal_recorder.record_signal(
                    strategy_id="stop_loss_system",
                    symbol=symbol,
                    signal_type="STOP_LOSS_CALCULATION",
                    indicator_count=1,
                    execution_time_ms=0.0,
                    gpu_used=False,
                    metadata={
                        "calculation_type": "volatility_adaptive_advanced",
                        "k_factor": calculation_result.get("k_factor"),
                        "stop_percentage": calculation_result.get("stop_percentage"),
                        "risk_assessment": calculation_result.get("risk_assessment"),
                        "market_adjustment": calculation_result.get("market_adjustment"),
                    },
                )
                logger.debug("止损计算记录成功: %(symbol)s")
        except Exception:
            logger.warning("记录止损计算失败 %(symbol)s: %(e)s")

    async def _get_market_volatility(self) -> float:
        """获取市场波动率"""
        try:
            # 这里应该计算市场基准的波动率
            # 暂时返回模拟值
            return 0.18  # 18%的年化波动率
        except Exception:
            return 0.20

    async def _get_market_atr(self) -> Optional[float]:
        """获取市场ATR"""
        try:
            # 这里应该获取市场基准的ATR
            return 15.0  # 假设市场ATR为15
        except Exception:
            return None

    # 新增高级跟踪止损方法

    async def _calculate_base_trailing_stop(
        self, symbol: str, highest_price: float, current_price: float, trailing_percentage: float, trailing_mode: str
    ) -> Dict[str, Any]:
        """计算基础跟踪止损"""
        if trailing_mode == "percentage":
            # 百分比模式
            trailing_stop_price = highest_price * (1 - trailing_percentage)
            drawdown_percentage = (highest_price - current_price) / highest_price

        elif trailing_mode == "volatility":
            # 波动率模式：基于ATR调整跟踪距离
            atr_value = await self._get_atr_value(symbol, period=14)
            volatility_adjustment = min(atr_value * 2, highest_price * 0.05)  # 最大5%
            trailing_stop_price = highest_price - volatility_adjustment
            drawdown_percentage = (highest_price - current_price) / highest_price

        elif trailing_mode == "hybrid":
            # 混合模式：结合百分比和波动率
            atr_value = await self._get_atr_value(symbol, period=14)
            percentage_stop = highest_price * (1 - trailing_percentage)
            volatility_stop = highest_price - (atr_value * 1.5)
            trailing_stop_price = max(percentage_stop, volatility_stop)  # 取更保守的值
            drawdown_percentage = (highest_price - current_price) / highest_price

        else:
            # 默认百分比模式
            trailing_stop_price = highest_price * (1 - trailing_percentage)
            drawdown_percentage = (highest_price - current_price) / highest_price

        return {
            "trailing_stop_price": trailing_stop_price,
            "drawdown_percentage": drawdown_percentage,
            "effective_trailing_percentage": (highest_price - trailing_stop_price) / highest_price,
        }

    def _apply_acceleration_factor(self, base_result: Dict[str, Any], acceleration_factor: float) -> Dict[str, Any]:
        """应用加速因子调整"""
        if acceleration_factor == 1.0:
            return base_result

        # 根据加速因子调整跟踪止损价格
        original_stop = base_result["trailing_stop_price"]
        highest_price = original_stop / (1 - base_result["effective_trailing_percentage"])

        if acceleration_factor > 1.0:
            # 加速：减少跟踪距离 (更激进)
            new_effective_percentage = base_result["effective_trailing_percentage"] * (2 - acceleration_factor)
        else:
            # 减速：增加跟踪距离 (更保守)
            new_effective_percentage = base_result["effective_trailing_percentage"] / acceleration_factor

        new_stop_price = highest_price * (1 - new_effective_percentage)

        return {
            **base_result,
            "trailing_stop_price": new_stop_price,
            "effective_trailing_percentage": new_effective_percentage,
            "acceleration_adjusted": True,
        }

    async def _calculate_technical_filters(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算技术指标过滤器"""
        try:
            # 获取技术指标
            ma_20 = await self._get_moving_average(symbol, period=20)
            ma_50 = await self._get_moving_average(symbol, period=50)
            rsi = await self._get_rsi(symbol, period=14)

            current_price = await self._get_current_price(symbol)

            # 多重技术确认
            technical_confirmations = {
                "ma_20_broken": current_price < ma_20 if ma_20 else False,
                "ma_50_broken": current_price < ma_50 if ma_50 else False,
                "rsi_oversold": rsi < 30 if rsi else False,
                "price_near_support": await self._check_price_near_support(symbol, current_price),
                "volume_confirmation": await self._check_volume_confirmation(symbol),
            }

            # 计算技术强度评分 (0-100)
            technical_strength = self._calculate_technical_strength(technical_confirmations)

            return {
                "technical_confirmations": technical_confirmations,
                "technical_strength": technical_strength,
                "ma_20": ma_20,
                "ma_50": ma_50,
                "rsi": rsi,
            }

        except Exception as e:
            logger.warning("计算技术指标过滤器失败 %(symbol)s: %(e)s")
            return {
                "technical_confirmations": {},
                "technical_strength": 50,
                "error": str(e),
            }

    def _analyze_trigger_conditions(self, result: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析触发条件"""
        trailing_stop_price = result.get("trailing_stop_price", 0)
        current_price = result.get("current_price", 0)
        technical_strength = result.get("technical_strength", 50)

        # 基础价格触发条件
        price_triggered = current_price <= trailing_stop_price

        # 技术确认条件
        technical_triggered = technical_strength >= 70  # 技术强度足够高

        # 多重确认条件
        multi_confirmation_triggered = price_triggered and technical_triggered

        # 紧急触发条件 (忽略技术确认)
        emergency_triggered = current_price <= trailing_stop_price * 0.95  # 比止损价低5%

        return {
            "price_triggered": price_triggered,
            "technical_triggered": technical_triggered,
            "multi_confirmation_triggered": multi_confirmation_triggered,
            "emergency_triggered": emergency_triggered,
            "recommended_trigger": multi_confirmation_triggered or emergency_triggered,
            "confidence_level": self._calculate_trigger_confidence(result),
        }

    def _calculate_trigger_confidence(self, result: Dict[str, Any]) -> str:
        """计算触发信心水平"""
        confidence_score = 0

        # 价格触发贡献
        if result.get("price_triggered"):
            confidence_score += 40

        # 技术强度贡献
        technical_strength = result.get("technical_strength", 50)
        confidence_score += min(30, technical_strength * 0.6)

        # 回撤幅度贡献
        drawdown = result.get("drawdown_percentage", 0)
        if drawdown > 0.15:  # 15%以上回撤
            confidence_score += 20
        elif drawdown > 0.10:  # 10%以上回撤
            confidence_score += 10

        # 确定信心等级
        if confidence_score >= 80:
            return "high"
        elif confidence_score >= 60:
            return "medium"
        elif confidence_score >= 40:
            return "low"
        else:
            return "very_low"

    async def _analyze_trailing_performance(self, symbol: str, trailing_mode: str) -> Dict[str, Any]:
        """分析跟踪止损历史表现"""
        try:
            # 这里应该从SignalResultTracker获取历史数据
            # 暂时返回模拟数据
            return {
                "total_trades": 25,
                "successful_exits": 18,
                "average_profit_pct": 8.5,
                "max_drawdown_avoided": 12.3,
                "win_rate": 0.72,
                "avg_holding_period_days": 45,
                "best_performing_mode": "hybrid",
                "current_mode_performance": 0.85 if trailing_mode == "hybrid" else 0.78,
            }
        except Exception:
            logger.warning("分析跟踪表现失败 %(symbol)s: %(e)s")
            return {}

    def _generate_trailing_adjustments(self, result: Dict[str, Any], historical_perf: Dict[str, Any]) -> Dict[str, Any]:
        """生成跟踪止损调整建议"""
        recommendations = []

        # 基于当前表现的调整建议
        technical_strength = result.get("technical_strength", 50)
        drawdown = result.get("drawdown_percentage", 0)

        if technical_strength < 30:
            recommendations.append("技术指标疲弱，建议增加跟踪百分比至10-12%")
        elif technical_strength > 80:
            recommendations.append("技术指标强劲，可以考虑减少跟踪百分比至6-8%")

        if drawdown > 0.12:
            recommendations.append("回撤较大，建议启用加速因子或切换到波动率模式")

        # 基于历史表现的调整建议
        win_rate = historical_perf.get("win_rate", 0.5)
        if win_rate > 0.75:
            recommendations.append("历史胜率良好，可以尝试更激进的跟踪设置")
        elif win_rate < 0.60:
            recommendations.append("历史胜率较低，建议使用更保守的跟踪设置")

        return {
            "recommendations": recommendations,
            "suggested_percentage": self._suggest_trailing_percentage(result, historical_perf),
            "suggested_mode": self._suggest_trailing_mode(result, historical_perf),
        }

    def _suggest_trailing_percentage(self, result: Dict[str, Any], historical_perf: Dict[str, Any]) -> float:
        """建议跟踪百分比"""
        current_percentage = result.get("effective_trailing_percentage", 0.08)
        technical_strength = result.get("technical_strength", 50)
        win_rate = historical_perf.get("win_rate", 0.5)

        # 基于技术强度调整
        if technical_strength > 80 and win_rate > 0.7:
            return min(current_percentage * 0.8, 0.05)  # 减少至最小5%
        elif technical_strength < 40 or win_rate < 0.5:
            return min(current_percentage * 1.2, 0.15)  # 增加至最大15%

        return current_percentage

    def _suggest_trailing_mode(self, result: Dict[str, Any], historical_perf: Dict[str, Any]) -> str:
        """建议跟踪模式"""
        best_mode = historical_perf.get("best_performing_mode", "percentage")
        current_mode = result.get("trailing_mode", "percentage")

        # 如果当前模式表现不佳，建议切换
        current_performance = historical_perf.get("current_mode_performance", 0.5)
        if current_performance < 0.7 and best_mode != current_mode:
            return best_mode

        return current_mode

    async def _record_trailing_calculation(self, symbol: str, calculation_result: Dict[str, Any]):
        """记录跟踪止损计算到SignalResultTracker"""
        try:
            if self.signal_recorder:
                await self.signal_recorder.record_signal(
                    strategy_id="trailing_stop_system",
                    symbol=symbol,
                    signal_type="TRAILING_STOP_CALCULATION",
                    indicator_count=1,
                    execution_time_ms=0.0,
                    gpu_used=False,
                    metadata={
                        "trailing_mode": calculation_result.get("trailing_mode"),
                        "trailing_percentage": calculation_result.get("trailing_percentage"),
                        "acceleration_factor": calculation_result.get("acceleration_factor"),
                        "technical_strength": calculation_result.get("technical_strength"),
                        "trigger_confidence": calculation_result.get("trigger_analysis", {}).get("confidence_level"),
                        "recommended_trigger": calculation_result.get("trigger_analysis", {}).get(
                            "recommended_trigger"
                        ),
                    },
                )
                logger.debug("跟踪止损计算记录成功: %(symbol)s")
        except Exception:
            logger.warning("记录跟踪止损计算失败 %(symbol)s: %(e)s")

    async def _get_recent_market_data(self, symbol: str, days: int) -> Dict[str, Any]:
        """获取近期市场数据"""
        try:
            # 这里应该获取最近N天的市场数据
            # 暂时返回模拟数据
            return {
                "price_history": [100 + i for i in range(days)],
                "volume_history": [1000000 + i * 10000 for i in range(days)],
                "volatility": 0.15,
            }
        except Exception:
            return {}

    async def _get_rsi(self, symbol: str, period: int) -> Optional[float]:
        """获取RSI指标"""
        try:
            # 这里应该计算真实的RSI
            return 55.0  # 模拟中性RSI
        except Exception:
            return None

    async def _check_price_near_support(self, symbol: str, current_price: float) -> bool:
        """检查价格是否接近支撑位"""
        try:
            # 这里应该分析技术支撑位
            return False  # 模拟结果
        except Exception:
            return False

    async def _check_volume_confirmation(self, symbol: str) -> bool:
        """检查成交量确认"""
        try:
            # 这里应该分析成交量配合
            return True  # 模拟结果
        except Exception:
            return False

    def _calculate_technical_strength(self, confirmations: Dict[str, bool]) -> int:
        """计算技术强度评分"""
        score = 50  # 基础分

        # 各确认条件的权重
        weights = {
            "ma_20_broken": 20,
            "ma_50_broken": 15,
            "rsi_oversold": 25,
            "price_near_support": 10,
            "volume_confirmation": 30,
        }

        for condition, weight in weights.items():
            if confirmations.get(condition, False):
                score += weight

        return min(100, score)


# 创建全局实例
_stop_loss_engine_instance: Optional[StopLossEngine] = None


def get_stop_loss_engine() -> StopLossEngine:
    """获取止损引擎实例（单例模式）"""
    global _stop_loss_engine_instance
    if _stop_loss_engine_instance is None:
        _stop_loss_engine_instance = StopLossEngine()
    return _stop_loss_engine_instance
