"""
GPU加速风险计算器
GPU-Accelerated Risk Calculator

扩展现有的GPU引擎，支持风险指标的高性能计算。
复用现有的GPU基础设施和数据源。
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import time

from src.governance.risk_management.core import IRiskCalculator, StockRiskMetrics, PortfolioRiskMetrics

# 复用现有的GPU基础设施
try:
    from src.gpu.data_processor_factory import get_processor
    from src.monitoring.async_monitoring import MonitoringEventPublisher

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    get_processor = None
    MonitoringEventPublisher = None

# 风险监控缓存系统
try:
    from src.utils.cache_optimization_enhanced import get_enhanced_cache_manager

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    get_enhanced_cache_manager = None

logger = logging.getLogger(__name__)


class GPURiskCalculator(IRiskCalculator):
    """
    GPU加速风险计算器

    复用现有的GPU引擎，实现高性能的风险指标计算。
    支持个股风险、组合风险、相关性矩阵和VaR计算。
    """

    def __init__(self):
        self.gpu_processor = None
        self.event_publisher = None
        self.cache_manager = None
        self.risk_cache_stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_puts": 0,
            "avg_cache_time": 0.0,
            "total_cache_requests": 0,
        }
        self._initialize_components()

    def _initialize_components(self):
        """初始化GPU处理器、事件发布器和缓存管理器"""
        try:
            if GPU_AVAILABLE:
                # 复用现有的GPU处理器工厂
                self.gpu_processor = get_processor(gpu_enabled=True)
                logger.info("✅ GPU风险计算器初始化成功")

                # 初始化事件发布器用于异步写入
                if MonitoringEventPublisher:
                    self.event_publisher = MonitoringEventPublisher()
                    logger.info("✅ 风险事件发布器初始化成功")
            else:
                logger.warning("⚠️ GPU基础设施不可用，将使用CPU模式")

            # 初始化缓存管理器
            if CACHE_AVAILABLE:
                try:
                    self.cache_manager = get_enhanced_cache_manager()
                    logger.info("✅ 风险缓存管理器初始化成功")
                except Exception as e:
                    logger.warning(f"⚠️ 缓存管理器初始化失败: {e}")
                    self.cache_manager = None
            else:
                logger.warning("⚠️ 增强缓存系统不可用")
                self.cache_manager = None

        except Exception as e:
            logger.error(f"❌ GPU风险计算器初始化失败: {e}")
            self.gpu_processor = None
            self.cache_manager = None

    async def calculate_stock_risk(self, symbol: str, use_cache: bool = True) -> StockRiskMetrics:
        """
        计算个股风险指标 (支持缓存)

        使用GPU加速计算波动率、ATR、流动性等指标。
        支持智能缓存以提升性能。
        """
        cache_key = f"stock_risk:{symbol}"
        cache_start = time.time()

        # 检查缓存
        if use_cache and self.cache_manager:
            cached_result = await self._get_cached_risk_metrics(cache_key)
            if cached_result:
                self.risk_cache_stats["cache_hits"] += 1
                self._update_cache_stats(cache_start, hit=True)
                logger.debug(f"✅ 个股风险缓存命中: {symbol}")
                return cached_result

        self.risk_cache_stats["cache_misses"] += 1
        self._update_cache_stats(cache_start, hit=False)

        try:
            # 获取历史数据
            historical_data = await self._get_historical_data(symbol, days=60)

            # GPU并行计算各项指标
            tasks = [
                self._calculate_volatility_metrics(historical_data),
                self._calculate_liquidity_metrics(symbol, historical_data),
                self._calculate_technical_metrics(historical_data),
                self._calculate_overall_risk_score(historical_data),
            ]

            results = await asyncio.gather(*tasks)

            # 组装结果
            volatility_metrics, liquidity_metrics, technical_metrics, risk_score = results

            metrics = StockRiskMetrics(
                symbol=symbol,
                timestamp=datetime.now(),
                **volatility_metrics,
                **liquidity_metrics,
                **technical_metrics,
                **risk_score,
            )

            # 缓存结果
            if use_cache and self.cache_manager:
                await self._cache_risk_metrics(cache_key, metrics, ttl=300)  # 5分钟缓存

            # 异步发布风险指标事件
            await self._publish_risk_event("stock_risk_update", {"symbol": symbol, "metrics": metrics.__dict__})

            return metrics

        except Exception as e:
            logger.error(f"计算个股风险失败 {symbol}: {e}")
            # 返回默认指标
            return StockRiskMetrics(symbol=symbol, timestamp=datetime.now())

    async def calculate_portfolio_risk(self, portfolio_id: str) -> PortfolioRiskMetrics:
        """
        计算组合风险指标

        包括VaR、最大回撤、集中度分析等。
        """
        try:
            # 获取组合持仓数据
            positions = await self._get_portfolio_positions(portfolio_id)

            if not positions:
                # 发布空组合事件
                await self._publish_portfolio_event("portfolio_empty", portfolio_id, {"reason": "no_positions_found"})
                return PortfolioRiskMetrics(portfolio_id=portfolio_id, user_id="unknown", timestamp=datetime.now())

            # 提取股票列表和权重
            symbols = [p["symbol"] for p in positions]
            weights = np.array([p["weight"] for p in positions])

            # GPU并行计算基础风险指标
            tasks = [
                self._calculate_portfolio_var(symbols, weights),
                self._calculate_portfolio_drawdown(symbols, weights),
                self._calculate_portfolio_beta(symbols, weights),
            ]

            results = await asyncio.gather(*tasks)
            var_value, drawdown, beta = results

            # 计算夏普比率
            sharpe_ratio = await self._calculate_sharpe_ratio(symbols, weights)

            # 计算赫芬达尔指数和集中度指标
            hhi = sum([p["weight"] ** 2 for p in positions])
            top10_ratio = min(
                1.0, sum([p["weight"] for p in sorted(positions, key=lambda x: x["weight"], reverse=True)[:10]])
            )
            max_single_position = max([p["weight"] for p in positions])

            # 计算风险评分和等级
            risk_score = self._calculate_portfolio_risk_score(var_value, drawdown, hhi)
            risk_level = self._get_portfolio_risk_level(var_value, drawdown, hhi)

            metrics = PortfolioRiskMetrics(
                portfolio_id=portfolio_id,
                user_id=positions[0].get("user_id", "unknown"),
                timestamp=datetime.now(),
                var_1d_95=var_value,
                max_drawdown=drawdown,
                sharpe_ratio=sharpe_ratio,
                beta=beta,
                hhi=hhi,
                top10_ratio=top10_ratio,
                max_single_position=max_single_position,
                risk_score=risk_score,
                risk_level=risk_level,
            )

            # 发布组合风险计算完成事件
            await self._publish_portfolio_risk_event(portfolio_id, metrics)

            # 检查是否需要触发告警
            await self._check_portfolio_alerts(portfolio_id, metrics)

            return metrics

        except Exception as e:
            logger.error(f"计算组合风险失败 {portfolio_id}: {e}")
            # 发布计算失败事件
            await self._publish_portfolio_event(
                "portfolio_risk_calculation_failed", portfolio_id, {"error": str(e), "error_type": type(e).__name__}
            )
            return PortfolioRiskMetrics(portfolio_id=portfolio_id, user_id="unknown", timestamp=datetime.now())

    async def calculate_correlation_matrix(self, symbols: List[str]) -> np.ndarray:
        """
        计算相关性矩阵 (GPU加速)

        使用GPU计算股票收益率的相关性矩阵。
        """
        try:
            if not self.gpu_processor or len(symbols) < 2:
                return np.eye(len(symbols))

            # 获取历史收益率数据
            returns_data = await self._get_returns_data(symbols, days=60)

            if self.gpu_processor:
                # 使用GPU计算相关性矩阵
                correlation_matrix = await self._gpu_calculate_correlation(returns_data)
            else:
                # CPU后备方案
                correlation_matrix = np.corrcoef(returns_data.T)

            return correlation_matrix

        except Exception as e:
            logger.error(f"计算相关性矩阵失败: {e}")
            return np.eye(len(symbols))

    async def calculate_var(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        计算VaR (GPU加速)

        使用历史模拟法计算VaR。
        """
        try:
            if not self.gpu_processor or len(returns) < 30:
                # CPU后备方案：简单历史VaR
                sorted_returns = np.sort(returns)
                index = int((1 - confidence) * len(sorted_returns))
                return abs(sorted_returns[index])

            # GPU加速的历史模拟VaR
            var_value = await self._gpu_calculate_var(returns, confidence)
            return var_value

        except Exception as e:
            logger.error(f"计算VaR失败: {e}")
            # 返回保守的VaR估计
            return np.std(returns) * 2.0

    # 私有方法实现

    async def _get_historical_data(self, symbol: str, days: int) -> pd.DataFrame:
        """获取历史数据"""
        # 这里应该集成现有的数据源
        # 暂时返回模拟数据
        dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
        np.random.seed(42)
        data = {
            "date": dates,
            "close": 100 + np.cumsum(np.random.randn(days) * 2),
            "high": lambda df: df["close"] + abs(np.random.randn(days)),
            "low": lambda df: df["close"] - abs(np.random.randn(days)),
            "volume": np.random.randint(1000000, 10000000, days),
        }
        df = pd.DataFrame(data)
        df["high"] = df["close"] + abs(np.random.randn(days))
        df["low"] = df["close"] - abs(np.random.randn(days))
        return df

    async def _get_portfolio_positions(self, portfolio_id: str) -> List[Dict]:
        """获取组合持仓"""
        # 这里应该从数据库获取真实的持仓数据
        # 暂时返回模拟数据
        return [
            {"symbol": "000001", "weight": 0.3, "user_id": "test_user"},
            {"symbol": "000002", "weight": 0.25, "user_id": "test_user"},
            {"symbol": "600000", "weight": 0.2, "user_id": "test_user"},
            {"symbol": "600036", "weight": 0.15, "user_id": "test_user"},
            {"symbol": "000858", "weight": 0.1, "user_id": "test_user"},
        ]

    async def _get_returns_data(self, symbols: List[str], days: int) -> np.ndarray:
        """获取收益率数据"""
        np.random.seed(42)
        return np.random.randn(len(symbols), days) * 0.02

    async def _calculate_volatility_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """计算波动率指标"""
        try:
            # 计算20日波动率
            returns = data["close"].pct_change().dropna()
            volatility_20d = returns.tail(20).std() * np.sqrt(252)  # 年化波动率

            # 计算ATR(14)
            high_low = data["high"] - data["low"]
            high_close = (data["high"] - data["close"].shift(1)).abs()
            low_close = (data["low"] - data["close"].shift(1)).abs()
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr_14 = tr.rolling(14).mean().iloc[-1]

            # 计算波动率百分位数
            volatility_percentile = 50  # 暂时固定值

            return {
                "volatility_20d": float(volatility_20d),
                "atr_14": float(atr_14),
                "volatility_percentile": volatility_percentile,
            }
        except Exception as e:
            logger.error(f"计算波动率指标失败: {e}")
            return {"volatility_20d": 0.0, "atr_14": 0.0, "volatility_percentile": 50}

    async def _calculate_liquidity_metrics(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """计算流动性指标"""
        try:
            # 计算平均日成交量
            avg_daily_volume = data["volume"].tail(20).mean()

            # 计算换手率 (模拟值)
            turnover_rate = data["volume"].tail(1).iloc[0] / 1000000000  # 假设总股本10亿

            # 计算买卖价差 (模拟值)
            bid_ask_spread = 0.002  # 0.2%

            # 计算流动性评分 (0-100)
            liquidity_score = min(100, max(0, (avg_daily_volume / 10000000) * 50))

            return {
                "avg_daily_volume": float(avg_daily_volume),
                "bid_ask_spread": bid_ask_spread,
                "turnover_rate": float(turnover_rate),
                "liquidity_score": int(liquidity_score),
            }
        except Exception as e:
            logger.error(f"计算流动性指标失败 {symbol}: {e}")
            return {"avg_daily_volume": 0.0, "bid_ask_spread": 0.0, "turnover_rate": 0.0, "liquidity_score": 50}

    async def _calculate_technical_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """计算技术指标"""
        try:
            # 简化的技术指标计算
            ma_20 = data["close"].rolling(20).mean().iloc[-1]
            ma_60 = data["close"].rolling(60).mean().iloc[-1]
            current_price = data["close"].iloc[-1]

            # 判断趋势
            if current_price > ma_20 > ma_60:
                ma_trend = "bull"
            elif current_price < ma_20 < ma_60:
                ma_trend = "bear"
            else:
                ma_trend = "neutral"

            # MACD信号 (简化)
            macd_signal = "bullish" if ma_trend == "bull" else "bearish"

            # RSI (简化)
            rsi = 60.0  # 模拟值

            # 布林带位置 (简化)
            bollinger_position = "middle"

            return {
                "ma_trend": ma_trend,
                "macd_signal": macd_signal,
                "rsi": rsi,
                "bollinger_position": bollinger_position,
            }
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return {"ma_trend": "neutral", "macd_signal": "neutral", "rsi": 50.0, "bollinger_position": "middle"}

    async def _calculate_overall_risk_score(self, data: pd.DataFrame) -> Dict[str, Any]:
        """计算综合风险评分"""
        try:
            # 简化的风险评分算法
            # 这里应该综合各项指标计算总分
            risk_score = 45  # 模拟中等风险
            risk_level = "medium"

            return {"risk_score": risk_score, "risk_level": risk_level}
        except Exception as e:
            return {"risk_score": 50, "risk_level": "medium"}

    async def _calculate_portfolio_var(self, symbols: List[str], weights: np.ndarray) -> float:
        """计算组合VaR"""
        try:
            # 获取历史收益率数据
            returns_data = await self._get_returns_data(symbols, 252)  # 一年数据

            # 计算组合收益率
            portfolio_returns = np.dot(weights, returns_data)

            # 历史模拟VaR
            sorted_returns = np.sort(portfolio_returns)
            index = int(0.05 * len(sorted_returns))  # 95%置信度
            var_value = abs(sorted_returns[index])

            return float(var_value)
        except Exception as e:
            logger.error(f"计算组合VaR失败: {e}")
            return 0.05  # 5%的保守估计

    async def _calculate_portfolio_drawdown(self, symbols: List[str], weights: np.ndarray) -> float:
        """计算最大回撤"""
        try:
            returns_data = await self._get_returns_data(symbols, 252)
            portfolio_returns = np.dot(weights, returns_data)

            # 计算累积收益率
            cumulative = np.cumprod(1 + portfolio_returns)

            # 计算回撤
            peak = np.maximum.accumulate(cumulative)
            drawdown = (peak - cumulative) / peak
            max_drawdown = np.max(drawdown)

            return float(max_drawdown)
        except Exception as e:
            return 0.15  # 15%的保守估计

    async def _calculate_portfolio_concentration(self, positions: List[Dict]) -> Dict[str, float]:
        """计算集中度指标"""
        # 在组合风险计算中已经处理
        return {}

    async def _calculate_portfolio_beta(self, symbols: List[str], weights: np.ndarray) -> float:
        """计算组合Beta"""
        try:
            # 简化的Beta计算 (相对沪深300)
            # 实际应该使用真实的基准数据
            return 1.0  # 中性Beta
        except Exception as e:
            return 1.0

    async def _calculate_sharpe_ratio(self, symbols: List[str], weights: np.ndarray) -> float:
        """计算夏普比率"""
        try:
            returns_data = await self._get_returns_data(symbols, 252)
            portfolio_returns = np.dot(weights, returns_data)

            # 简化的夏普比率计算
            avg_return = np.mean(portfolio_returns)
            volatility = np.std(portfolio_returns)
            risk_free_rate = 0.03  # 3%

            if volatility > 0:
                sharpe = (avg_return - risk_free_rate) / volatility
                return float(sharpe)
            return 0.0
        except Exception as e:
            return 0.0

    def _calculate_portfolio_risk_score(self, var: float, drawdown: float, hhi: float) -> int:
        """计算组合风险评分"""
        # 简化的风险评分算法
        score = 50
        if var > 0.08:
            score += 20
        if drawdown > 0.20:
            score += 20
        if hhi > 0.3:
            score += 10
        return min(100, max(0, score))

    def _get_portfolio_risk_level(self, var: float, drawdown: float, hhi: float) -> str:
        """获取组合风险等级"""
        score = self._calculate_portfolio_risk_score(var, drawdown, hhi)
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        else:
            return "low"

    async def _gpu_calculate_correlation(self, returns_data: np.ndarray) -> np.ndarray:
        """GPU加速相关性计算"""
        if self.gpu_processor:
            # 这里应该调用GPU处理器的相关性计算方法
            # 暂时使用CPU计算作为后备
            return np.corrcoef(returns_data.T)
        return np.corrcoef(returns_data.T)

    async def _gpu_calculate_var(self, returns: np.ndarray, confidence: float) -> float:
        """GPU加速VaR计算"""
        if self.gpu_processor:
            # 这里应该调用GPU处理器的VaR计算方法
            # 暂时使用CPU计算作为后备
            sorted_returns = np.sort(returns)
            index = int((1 - confidence) * len(sorted_returns))
            return abs(sorted_returns[index])
        return abs(np.percentile(returns, (1 - confidence) * 100))

    async def _publish_risk_event(self, event_type: str, data: Dict[str, Any]):
        """发布风险事件到异步总线"""
        try:
            if self.event_publisher:
                event = {"event_type": event_type, "timestamp": datetime.now().isoformat(), "data": data}
                await self.event_publisher.publish_event(event)
        except Exception as e:
            logger.error(f"发布风险事件失败: {e}")

    async def _publish_portfolio_risk_event(self, portfolio_id: str, metrics: PortfolioRiskMetrics):
        """发布组合风险更新事件"""
        try:
            if self.event_publisher:
                event_data = {
                    "portfolio_id": portfolio_id,
                    "risk_metrics": {
                        "var_1d_95": metrics.var_1d_95,
                        "max_drawdown": metrics.max_drawdown,
                        "sharpe_ratio": metrics.sharpe_ratio,
                        "beta": metrics.beta,
                        "hhi": metrics.hhi,
                        "top10_ratio": metrics.top10_ratio,
                        "max_single_position": metrics.max_single_position,
                        "risk_score": metrics.risk_score,
                        "risk_level": metrics.risk_level,
                        "timestamp": metrics.timestamp.isoformat(),
                    },
                    "computation_mode": "gpu" if self.gpu_processor else "cpu",
                    "user_id": metrics.user_id,
                }

                await self._publish_risk_event("portfolio_risk_update", event_data)
                logger.debug(f"✅ 组合风险事件已发布: {portfolio_id}")
        except Exception as e:
            logger.error(f"发布组合风险事件失败 {portfolio_id}: {e}")

    async def _publish_portfolio_event(
        self, event_type: str, portfolio_id: str, additional_data: Dict[str, Any] = None
    ):
        """发布组合相关事件"""
        try:
            if self.event_publisher:
                event_data = {
                    "portfolio_id": portfolio_id,
                    "timestamp": datetime.now().isoformat(),
                }
                if additional_data:
                    event_data.update(additional_data)

                await self._publish_risk_event(event_type, event_data)
                logger.debug(f"✅ 组合事件已发布: {event_type} - {portfolio_id}")
        except Exception as e:
            logger.error(f"发布组合事件失败 {event_type} {portfolio_id}: {e}")

    async def _check_portfolio_alerts(self, portfolio_id: str, metrics: PortfolioRiskMetrics):
        """检查组合风险告警条件"""
        try:
            alerts = []

            # 高风险评分告警
            if metrics.risk_score >= 80:
                alerts.append(
                    {
                        "alert_type": "high_risk_score",
                        "severity": "critical",
                        "message": f"组合风险评分过高: {metrics.risk_score}",
                        "threshold": 80,
                        "current_value": metrics.risk_score,
                    }
                )

            # 高VaR告警
            if metrics.var_1d_95 >= 0.08:  # 8% VaR
                alerts.append(
                    {
                        "alert_type": "high_var",
                        "severity": "high",
                        "message": f"VaR值过高: {metrics.var_1d_95:.2%}",
                        "threshold": 0.08,
                        "current_value": metrics.var_1d_95,
                    }
                )

            # 高最大回撤告警
            if metrics.max_drawdown >= 0.15:  # 15% 回撤
                alerts.append(
                    {
                        "alert_type": "high_drawdown",
                        "severity": "high",
                        "message": f"最大回撤过高: {metrics.max_drawdown:.2%}",
                        "threshold": 0.15,
                        "current_value": metrics.max_drawdown,
                    }
                )

            # 高集中度告警
            if metrics.hhi >= 0.3:  # HHI > 0.3
                alerts.append(
                    {
                        "alert_type": "high_concentration",
                        "severity": "medium",
                        "message": f"组合集中度过高 (HHI: {metrics.hhi:.3f})",
                        "threshold": 0.3,
                        "current_value": metrics.hhi,
                    }
                )

            # 单一持仓过高告警
            if metrics.max_single_position >= 0.2:  # 20% 单一持仓
                alerts.append(
                    {
                        "alert_type": "high_single_position",
                        "severity": "medium",
                        "message": f"单一持仓占比过高: {metrics.max_single_position:.2%}",
                        "threshold": 0.2,
                        "current_value": metrics.max_single_position,
                    }
                )

            # 发布告警事件
            if alerts:
                await self._publish_risk_event(
                    "portfolio_risk_alerts",
                    {
                        "portfolio_id": portfolio_id,
                        "alerts": alerts,
                        "alert_count": len(alerts),
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                logger.info(f"⚠️ 发布组合风险告警: {portfolio_id} - {len(alerts)} 个告警")

        except Exception as e:
            logger.error(f"检查组合告警失败 {portfolio_id}: {e}")

    async def calculate_portfolio_concentration_analysis(self, portfolio_id: str) -> Dict[str, Any]:
        """计算组合集中度分析并发布事件"""
        try:
            # 获取持仓数据
            positions = await self._get_portfolio_positions(portfolio_id)
            if not positions:
                return {"error": "no_positions_found"}

            # 使用GPU引擎计算集中度
            if self.gpu_processor:
                concentration_results = await self.gpu_processor.calculate_portfolio_concentration_gpu(positions)
            else:
                # CPU后备方案
                concentration_results = self._calculate_concentration_cpu(positions)

            # 发布集中度分析事件
            await self._publish_risk_event(
                "portfolio_concentration_analysis",
                {
                    "portfolio_id": portfolio_id,
                    "concentration_results": concentration_results,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            logger.info(f"✅ 组合集中度分析完成并发布事件: {portfolio_id}")
            return concentration_results

        except Exception as e:
            logger.error(f"组合集中度分析失败 {portfolio_id}: {e}")
            await self._publish_risk_event(
                "portfolio_concentration_analysis_failed",
                {
                    "portfolio_id": portfolio_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            )
            return {"error": str(e)}

    def _calculate_concentration_cpu(self, positions: List[Dict]) -> Dict[str, Any]:
        """CPU后备方案计算集中度"""
        try:
            weights = np.array([p["weight"] for p in positions])

            # 计算HHI
            hhi = float(np.sum(weights**2))

            # 最大持仓
            max_single = float(np.max(weights))
            max_idx = np.argmax(weights)
            max_symbol = positions[max_idx]["symbol"]

            # 前10大占比
            if len(weights) <= 10:
                top10_ratio = 1.0
            else:
                sorted_weights = np.sort(weights)[::-1]
                top10_ratio = float(np.sum(sorted_weights[:10]))

            # 集中度评分
            concentration_score = self._calculate_concentration_score_cpu(hhi, max_single, top10_ratio)

            return {
                "hhi": hhi,
                "max_single_position": max_single,
                "max_single_symbol": max_symbol,
                "top10_ratio": top10_ratio,
                "concentration_score": concentration_score,
                "concentration_level": self._get_concentration_level_cpu(concentration_score),
                "computation_time": 0.0,
                "gpu_mode": False,
            }

        except Exception as e:
            logger.error(f"CPU集中度计算失败: {e}")
            return {
                "error": str(e),
                "hhi": 0.0,
                "max_single_position": 0.0,
                "top10_ratio": 0.0,
                "concentration_score": 0,
                "concentration_level": "unknown",
                "computation_time": 0.0,
                "gpu_mode": False,
            }

    def _calculate_concentration_score_cpu(self, hhi: float, max_single: float, top10_ratio: float) -> int:
        """CPU版本的集中度评分计算"""
        score = 0
        if hhi > 0.5:
            score += 40
        elif hhi > 0.25:
            score += 25
        elif hhi > 0.15:
            score += 10

        if max_single > 0.3:
            score += 30
        elif max_single > 0.2:
            score += 20
        elif max_single > 0.1:
            score += 10

        if top10_ratio > 0.8:
            score += 30
        elif top10_ratio > 0.6:
            score += 20
        elif top10_ratio > 0.4:
            score += 10

        return min(100, score)

    def _get_concentration_level_cpu(self, score: int) -> str:
        """CPU版本的集中度等级"""
        if score >= 80:
            return "highly_concentrated"
        elif score >= 60:
            return "moderately_concentrated"
        elif score >= 40:
            return "somewhat_concentrated"
        elif score >= 20:
            return "well_diversified"
        else:
            return "highly_diversified"

    # 风险监控缓存方法
    async def _get_cached_risk_metrics(self, cache_key: str) -> Optional[StockRiskMetrics]:
        """从缓存获取风险指标"""
        try:
            if not self.cache_manager:
                return None

            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                # 验证缓存数据的有效性
                if self._is_cache_data_valid(cached_data):
                    return cached_data
                else:
                    # 缓存数据过期，删除
                    await self.cache_manager.delete(cache_key)

            return None

        except Exception as e:
            logger.debug(f"缓存读取失败 {cache_key}: {e}")
            return None

    async def _cache_risk_metrics(self, cache_key: str, metrics: StockRiskMetrics, ttl: int = 300):
        """缓存风险指标"""
        try:
            if not self.cache_manager:
                return

            await self.cache_manager.put(cache_key, metrics, ttl=ttl)
            self.risk_cache_stats["cache_puts"] += 1

            logger.debug(f"✅ 风险指标已缓存: {cache_key} (TTL: {ttl}s)")

        except Exception as e:
            logger.debug(f"缓存写入失败 {cache_key}: {e}")

    def _is_cache_data_valid(self, cached_data: Any) -> bool:
        """验证缓存数据的有效性"""
        try:
            if not isinstance(cached_data, StockRiskMetrics):
                return False

            # 检查时间戳是否在合理范围内 (不超过1小时)
            age_seconds = (datetime.now() - cached_data.timestamp).total_seconds()
            return age_seconds < 3600  # 1小时

        except Exception:
            return False

    def _update_cache_stats(self, start_time: float, hit: bool):
        """更新缓存统计信息"""
        self.risk_cache_stats["total_cache_requests"] += 1

        access_time = time.time() - start_time
        self.risk_cache_stats["avg_cache_time"] = (
            (self.risk_cache_stats["avg_cache_time"] * (self.risk_cache_stats["total_cache_requests"] - 1))
            + access_time
        ) / self.risk_cache_stats["total_cache_requests"]

    async def get_risk_cache_performance(self) -> Dict[str, Any]:
        """获取风险缓存性能统计"""
        try:
            if not self.cache_manager:
                return {"cache_enabled": False}

            base_stats = self.cache_manager.get_comprehensive_stats()

            total_requests = self.risk_cache_stats["cache_hits"] + self.risk_cache_stats["cache_misses"]
            hit_rate = self.risk_cache_stats["cache_hits"] / total_requests * 100 if total_requests > 0 else 0

            return {
                "cache_enabled": True,
                "risk_cache_stats": {
                    "cache_hits": self.risk_cache_stats["cache_hits"],
                    "cache_misses": self.risk_cache_stats["cache_misses"],
                    "cache_puts": self.risk_cache_stats["cache_puts"],
                    "hit_rate_percent": hit_rate,
                    "avg_cache_access_time_ms": self.risk_cache_stats["avg_cache_time"] * 1000,
                    "total_cache_requests": self.risk_cache_stats["total_cache_requests"],
                },
                "multi_level_cache_stats": base_stats.get("cache_stats", {}),
                "optimization_suggestions": base_stats.get("optimization_suggestions", []),
            }

        except Exception as e:
            logger.error(f"获取缓存性能统计失败: {e}")
            return {"error": str(e), "cache_enabled": bool(self.cache_manager)}

    async def clear_risk_cache(self, pattern: Optional[str] = None):
        """清除风险缓存"""
        try:
            if not self.cache_manager:
                return

            if pattern:
                # 清除匹配模式的风险缓存
                await self.cache_manager.clear_pattern(f"*{pattern}*")
            else:
                # 清除所有风险相关缓存
                await self.cache_manager.clear_pattern("*risk*")
                await self.cache_manager.clear_pattern("*portfolio*")

            # 重置统计信息
            self.risk_cache_stats = {
                "cache_hits": 0,
                "cache_misses": 0,
                "cache_puts": 0,
                "avg_cache_time": 0.0,
                "total_cache_requests": 0,
            }

            logger.info("✅ 风险缓存已清除")

        except Exception as e:
            logger.error(f"清除风险缓存失败: {e}")

    async def warmup_risk_cache(self, symbols: List[str]):
        """预热风险缓存"""
        try:
            if not self.cache_manager:
                return

            logger.info(f"开始预热风险缓存，共 {len(symbols)} 个股票")

            # 并发预热风险计算
            tasks = []
            for symbol in symbols:
                task = asyncio.create_task(self.calculate_stock_risk(symbol, use_cache=False))
                tasks.append(task)

            # 等待所有预热完成
            await asyncio.gather(*tasks, return_exceptions=True)

            logger.info("✅ 风险缓存预热完成")

        except Exception as e:
            logger.error(f"风险缓存预热失败: {e}")

    async def monitor_risk_cache_health(self) -> Dict[str, Any]:
        """监控风险缓存健康状态"""
        try:
            if not self.cache_manager:
                return {"cache_enabled": False, "health_status": "disabled"}

            stats = await self.get_risk_cache_performance()

            # 健康检查标准
            hit_rate = stats.get("risk_cache_stats", {}).get("hit_rate_percent", 0)
            avg_access_time = stats.get("risk_cache_stats", {}).get("avg_cache_access_time_ms", 0)

            health_issues = []

            if hit_rate < 70:
                health_issues.append("缓存命中率偏低")
            if avg_access_time > 50:  # 超过50ms
                health_issues.append("缓存访问延迟过高")
            if (
                stats.get("risk_cache_stats", {}).get("cache_misses", 0)
                > stats.get("risk_cache_stats", {}).get("cache_hits", 0) * 2
            ):
                health_issues.append("缓存未命中率过高")

            health_status = "healthy" if not health_issues else "warning" if len(health_issues) == 1 else "critical"

            return {
                "cache_enabled": True,
                "health_status": health_status,
                "health_issues": health_issues,
                "performance_metrics": stats,
                "recommendations": self._generate_cache_recommendations(health_issues),
            }

        except Exception as e:
            logger.error(f"缓存健康监控失败: {e}")
            return {
                "cache_enabled": bool(self.cache_manager),
                "health_status": "error",
                "error": str(e),
            }

    def _generate_cache_recommendations(self, health_issues: List[str]) -> List[str]:
        """生成缓存优化建议"""
        recommendations = []

        for issue in health_issues:
            if "命中率偏低" in issue:
                recommendations.extend(
                    [
                        "考虑增加缓存TTL时间",
                        "检查数据访问模式，优化缓存键设计",
                        "启用预测性预加载功能",
                    ]
                )
            elif "访问延迟过高" in issue:
                recommendations.extend(
                    [
                        "检查Redis连接性能",
                        "考虑增加L1缓存大小",
                        "优化数据压缩策略",
                    ]
                )
            elif "未命中率过高" in issue:
                recommendations.extend(
                    [
                        "启用负缓存以减少无效查询",
                        "调整缓存失效策略",
                        "增加热点数据预加载",
                    ]
                )

        return recommendations


# 创建全局实例
_gpu_risk_calculator_instance: Optional[GPURiskCalculator] = None


def get_gpu_risk_calculator() -> GPURiskCalculator:
    """获取GPU风险计算器实例（单例模式）"""
    global _gpu_risk_calculator_instance
    if _gpu_risk_calculator_instance is None:
        _gpu_risk_calculator_instance = GPURiskCalculator()
    return _gpu_risk_calculator_instance
