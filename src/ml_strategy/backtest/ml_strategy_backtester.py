#!/usr/bin/env python3
"""
ML策略回测集成器 (ML Strategy Backtesting Integrator)

功能说明:
- 将ML增强交易策略与向量化回测引擎集成
- 自动生成策略信号并执行回测
- 支持多策略对比和性能分析
- 生成详细的回测报告和可视化

集成流程:
1. 初始化ML策略和回测引擎
2. 生成策略信号
3. 执行向量化回测
4. 计算性能和风险指标
5. 生成对比报告

作者: MyStocks量化交易团队
创建时间: 2026-01-12
版本: 1.0.0
"""

import logging
import sys
from datetime import timedelta
from typing import Any, Dict, List, Optional

import pandas as pd

from src.ml_strategy.backtest.performance_metrics import PerformanceMetrics
from src.ml_strategy.backtest.risk_metrics import RiskMetrics
from src.ml_strategy.backtest.vectorized_backtester import BacktestConfig, VectorizedBacktester
from src.ml_strategy.strategy.ml_strategy_base import MLTradingStrategy

# 添加项目根目录到路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)


logger = logging.getLogger(__name__)


class MLStrategyBacktestConfig:
    """ML策略回测配置"""

    def __init__(
        self,
        backtest_config: Optional[BacktestConfig] = None,
        signal_column: str = "signal",
        confidence_column: str = "confidence",
        signal_mapping: Optional[Dict[int, str]] = None,
        min_confidence_threshold: float = 0.5,
        max_signals_per_day: int = 1,
        signal_cooldown_days: int = 1,
    ):
        self.backtest_config = backtest_config or BacktestConfig()
        self.signal_column = signal_column
        self.confidence_column = confidence_column
        self.signal_mapping = signal_mapping or {1: "buy", -1: "sell", 0: "hold"}
        self.min_confidence_threshold = min_confidence_threshold
        self.max_signals_per_day = max_signals_per_day
        self.signal_cooldown_days = signal_cooldown_days


class MLStrategyBacktester:
    """
    ML策略回测器 - 连接ML策略和回测引擎

    功能:
    - 执行ML策略的完整回测流程
    - 转换ML信号为回测兼容格式
    - 生成详细的性能和风险分析
    - 支持多策略对比
    """

    def __init__(self, config: Optional[MLStrategyBacktestConfig] = None):
        self.config = config or MLStrategyBacktestConfig()
        self.backtester = VectorizedBacktester(self.config.backtest_config)
        self.performance_metrics = PerformanceMetrics()
        self.risk_metrics = RiskMetrics()
        self.results_cache = {}

        logger.info("ML策略回测器初始化完成")

    async def run_strategy_backtest(
        self,
        strategy: MLTradingStrategy,
        price_data: pd.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        执行ML策略回测

        参数:
            strategy: ML交易策略实例
            price_data: 价格数据 (OHLCV)
            start_date: 开始日期 (可选)
            end_date: 结束日期 (可选)

        返回:
            完整的回测结果字典
        """
        try:
            logger.info("=" * 80)
            logger.info("开始ML策略回测: {strategy.name")
            logger.info("=" * 80)

            # 数据预处理
            backtest_data = self._prepare_price_data(price_data, start_date, end_date)

            # 生成ML策略信号
            signals_df = await self._generate_strategy_signals(strategy, backtest_data)

            # 调试: 检查原始信号分布
            if not signals_df.empty and self.config.signal_column in signals_df.columns:
                raw_signal_counts = signals_df[self.config.signal_column].value_counts()
                logger.info("原始信号分布: {raw_signal_counts.to_dict()")
                raw_buy_signals = (signals_df[self.config.signal_column] == 1).sum()
                raw_sell_signals = (signals_df[self.config.signal_column] == -1).sum()
                raw_hold_signals = (signals_df[self.config.signal_column] == 0).sum()
                logger.info("原始信号 - 买入: %(raw_buy_signals)s, 持有: %(raw_hold_signals)s, 卖出: %(raw_sell_signals)s")

                if self.config.confidence_column in signals_df.columns:
                    confidence_stats = signals_df[self.config.confidence_column].describe()
                    logger.info(
                        f"置信度统计: 均值={confidence_stats['mean']:.3f}, 最小={confidence_stats['min']:.3f}, 最大={confidence_stats['max']:.3f}"
                    )

            # 转换信号格式
            backtest_signals = self._convert_signals_for_backtest(signals_df)

            # 调试: 检查信号分布
            if not backtest_signals.empty:
                signal_counts = backtest_signals["signal"].value_counts()
                logger.info("转换后信号分布: {signal_counts.to_dict()")
                buy_signals = (backtest_signals["signal"] == "buy").sum()
                sell_signals = (backtest_signals["signal"] == "sell").sum()
                logger.info("买入信号: %(buy_signals)s, 卖出信号: %(sell_signals)s")

            # 执行回测
            backtest_result = self.backtester.run(backtest_data, backtest_signals)

            # 计算额外指标
            enhanced_result = await self._enhance_backtest_result(backtest_result, strategy, backtest_data, signals_df)

            # 缓存结果
            cache_key = f"{strategy.name}_{hash(str(backtest_data.values.tobytes()))}"
            self.results_cache[cache_key] = enhanced_result

            logger.info("=" * 80)
            logger.info("ML策略回测完成")
            logger.info("总收益率: {enhanced_result.get('summary', {}).get('total_return', 0):.2%")
            logger.info("夏普比率: {enhanced_result.get('performance_metrics', {}).get('sharpe_ratio', 0):.2f")
            logger.info("=" * 80)

            return enhanced_result

        except Exception:
            logger.error("ML策略回测失败: %(e)s")
            raise

    async def compare_strategies(
        self,
        strategies: List[MLTradingStrategy],
        price_data: pd.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        对比多个ML策略的性能

        参数:
            strategies: ML策略列表
            price_data: 价格数据
            start_date: 开始日期
            end_date: 结束日期

        返回:
            策略对比结果
        """
        try:
            logger.info("开始策略对比: {len(strategies)} 个策略")

            comparison_results = {}

            for strategy in strategies:
                try:
                    result = await self.run_strategy_backtest(strategy, price_data, start_date, end_date)
                    comparison_results[strategy.name] = result

                    logger.info("✓ {strategy.name} 回测完成")

                except Exception as e:
                    logger.error("❌ {strategy.name} 回测失败: %(e)s")
                    comparison_results[strategy.name] = {"error": str(e)}

            # 生成对比报告
            comparison_report = self._generate_comparison_report(comparison_results)

            return {
                "individual_results": comparison_results,
                "comparison_report": comparison_report,
                "strategies_tested": len(strategies),
                "successful_tests": len([r for r in comparison_results.values() if "error" not in r]),
            }

        except Exception:
            logger.error("策略对比失败: %(e)s")
            raise

    def _prepare_price_data(
        self,
        price_data: pd.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """准备价格数据"""
        df = price_data.copy()

        # 确保索引是DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        # 日期过滤
        if start_date:
            df = df[df.index >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df.index <= pd.to_datetime(end_date)]

        # 确保必要的列存在
        required_columns = ["open", "high", "low", "close"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"价格数据缺少必要列: {missing_columns}")

        # 填充缺失值
        df = df.ffill().bfill()

        logger.info("价格数据准备完成: {len(df)} 行, {len(df.columns)} 列")
        return df

    async def _generate_strategy_signals(
        self,
        strategy: MLTradingStrategy,
        price_data: pd.DataFrame,
    ) -> pd.DataFrame:
        """生成策略信号"""
        try:
            # 使用策略生成信号
            signals_df = await strategy.generate_signals(price_data)

            # 确保信号数据与价格数据对齐
            signals_df = signals_df.reindex(price_data.index)

            # 填充缺失信号为0 (持有)
            if self.config.signal_column in signals_df.columns:
                signals_df[self.config.signal_column] = signals_df[self.config.signal_column].fillna(0)
            else:
                signals_df[self.config.signal_column] = 0

            # 填充置信度
            if self.config.confidence_column not in signals_df.columns:
                signals_df[self.config.confidence_column] = 0.5
            else:
                signals_df[self.config.confidence_column] = signals_df[self.config.confidence_column].fillna(0.5)

            logger.info("策略信号生成完成: {len(signals_df)} 个信号")
            return signals_df

        except Exception:
            logger.error("信号生成失败: %(e)s")
            raise

    def _convert_signals_for_backtest(self, signals_df: pd.DataFrame) -> pd.DataFrame:
        """转换信号为回测引擎格式"""
        try:
            # 创建回测信号DataFrame
            backtest_signals = pd.DataFrame(index=signals_df.index)

            # 转换信号值
            signal_values = signals_df[self.config.signal_column]
            backtest_signals["signal"] = signal_values.map(self.config.signal_mapping).fillna("hold")

            # 添加信号强度 (如果有的话)
            if self.config.confidence_column in signals_df.columns:
                backtest_signals["strength"] = signals_df[self.config.confidence_column]
            else:
                backtest_signals["strength"] = 0.5

            # 应用信号过滤
            backtest_signals = self._apply_signal_filters(backtest_signals)

            logger.info("信号转换完成: {len(backtest_signals)} 个交易日")
            return backtest_signals

        except Exception:
            logger.error("信号转换失败: %(e)s")
            raise

    def _apply_signal_filters(self, signals_df: pd.DataFrame) -> pd.DataFrame:
        """应用信号过滤规则"""
        try:
            df = signals_df.copy()

            # 置信度过滤
            if self.config.min_confidence_threshold > 0:
                low_confidence = df["strength"] < self.config.min_confidence_threshold
                df.loc[low_confidence, "signal"] = "hold"

            # 每日最大信号数限制
            if self.config.max_signals_per_day > 0:
                # 按日期分组
                df["date_col"] = df.index.date
                df["signal_rank"] = df.groupby("date_col")["strength"].rank(ascending=False, method="first")
                too_many_signals = df["signal_rank"] > self.config.max_signals_per_day
                df.loc[too_many_signals, "signal"] = "hold"

            # 信号冷却期
            if self.config.signal_cooldown_days > 0:
                signal_mask = df["signal"] != "hold"
                signal_dates = df.index[signal_mask]

                for signal_date in signal_dates:
                    cooldown_start = signal_date + timedelta(days=1)
                    cooldown_end = signal_date + timedelta(days=self.config.signal_cooldown_days)

                    # 在冷却期内设置信号为hold
                    cooldown_mask = (df.index >= cooldown_start) & (df.index <= cooldown_end)
                    df.loc[cooldown_mask, "signal"] = "hold"

            # 清理临时列
            df = df.drop(columns=[col for col in ["date_col", "signal_rank"] if col in df.columns])

            return df

        except Exception:
            logger.warning("信号过滤应用失败，使用原始信号: %(e)s")
            return signals_df

    async def _enhance_backtest_result(
        self,
        backtest_result: Dict[str, Any],
        strategy: MLTradingStrategy,
        price_data: pd.DataFrame,
        signals_df: pd.DataFrame,
    ) -> Dict[str, Any]:
        """增强回测结果"""
        try:
            enhanced_result = backtest_result.copy()

            # 添加策略信息
            enhanced_result["strategy_info"] = strategy.get_strategy_info()

            # 添加信号统计
            signal_stats = self._calculate_signal_statistics(signals_df)
            enhanced_result["signal_statistics"] = signal_stats

            # 添加性能指标
            if "equity_curve" in backtest_result and "trades" in backtest_result:
                equity_curve = backtest_result["equity_curve"]
                trades = backtest_result.get("trades", [])
                summary = backtest_result.get("summary", {})

                # 计算日收益率
                daily_returns = equity_curve.pct_change().fillna(0)

                # 计算性能指标
                perf_metrics = self.performance_metrics.calculate_all_metrics(
                    equity_curve=equity_curve,
                    daily_returns=daily_returns,
                    trades=trades,
                    initial_capital=summary.get("initial_capital", 100000),
                    benchmark_returns=None,
                )
                enhanced_result["performance_metrics"] = perf_metrics

                # 添加风险指标
                # pylint: disable=no-member
                risk_metrics = self.risk_metrics.calculate_all_risk_metrics(
                    equity_curve=equity_curve,
                    returns=daily_returns,
                    trades=trades,
                    total_return=summary.get("total_return", 0),
                    max_drawdown=perf_metrics.get("max_drawdown", 0),
                    risk_free_rate=self.risk_metrics.risk_free_rate,
                )
                # pylint: enable=no-member
                enhanced_result["risk_metrics"] = risk_metrics

            # 添加市场基准对比 (如果有)
            benchmark_comparison = self._calculate_benchmark_comparison(backtest_result, price_data)
            enhanced_result["benchmark_comparison"] = benchmark_comparison

            return enhanced_result

        except Exception:
            logger.warning("回测结果增强失败: %(e)s")
            return backtest_result

    def _calculate_signal_statistics(self, signals_df: pd.DataFrame) -> Dict[str, Any]:
        """计算信号统计"""
        try:
            signal_counts = signals_df[self.config.signal_column].value_counts()
            confidence_stats = signals_df[self.config.confidence_column].describe()

            return {
                "total_signals": len(signals_df),
                "signal_distribution": signal_counts.to_dict(),
                "confidence_stats": confidence_stats.to_dict(),
                "avg_signals_per_day": len(signals_df[signals_df[self.config.signal_column] != 0]) / len(signals_df),
            }

        except Exception:
            logger.warning("信号统计计算失败: %(e)s")
            return {}

    def _calculate_benchmark_comparison(
        self,
        backtest_result: Dict[str, Any],
        price_data: pd.DataFrame,
    ) -> Dict[str, Any]:
        """计算基准对比"""
        try:
            if "equity_curve" not in backtest_result:
                return {}

            equity_curve = backtest_result["equity_curve"]

            # 计算买入持有策略
            initial_price = price_data["close"].iloc[0]
            final_price = price_data["close"].iloc[-1]
            buy_hold_return = (final_price - initial_price) / initial_price

            # 计算策略表现
            strategy_return = backtest_result["summary"]["total_return"]

            return {
                "buy_hold_return": buy_hold_return,
                "strategy_return": strategy_return,
                "outperformance": strategy_return - buy_hold_return,
                "outperformance_pct": (
                    (strategy_return - buy_hold_return) / abs(buy_hold_return) if buy_hold_return != 0 else 0
                ),
            }

        except Exception:
            logger.warning("基准对比计算失败: %(e)s")
            return {}

    def _generate_comparison_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成策略对比报告"""
        try:
            # 筛选成功的回测结果
            successful_results = {k: v for k, v in results.items() if "error" not in v}

            if not successful_results:
                return {"error": "没有成功的回测结果"}

            # 提取关键指标
            comparison_data = {}
            for name, result in successful_results.items():
                summary = result.get("summary", {})
                perf_metrics = result.get("performance_metrics", {})
                risk_metrics = result.get("risk_metrics", {})

                comparison_data[name] = {
                    "total_return": summary.get("total_return", 0),
                    "sharpe_ratio": perf_metrics.get("sharpe_ratio", 0),
                    "max_drawdown": risk_metrics.get("max_drawdown", 0),
                    "win_rate": perf_metrics.get("win_rate", 0),
                    "total_trades": summary.get("total_trades", 0),
                }

            # 计算排名
            rankings = {}
            for metric in ["total_return", "sharpe_ratio", "win_rate"]:
                sorted_strategies = sorted(comparison_data.items(), key=lambda x: x[1][metric], reverse=True)
                rankings[metric] = {name: rank + 1 for rank, (name, _) in enumerate(sorted_strategies)}

            return {
                "comparison_data": comparison_data,
                "rankings": rankings,
                "best_performers": {
                    "total_return": max(comparison_data.items(), key=lambda x: x[1]["total_return"])[0],
                    "sharpe_ratio": max(comparison_data.items(), key=lambda x: x[1]["sharpe_ratio"])[0],
                    "win_rate": max(comparison_data.items(), key=lambda x: x[1]["win_rate"])[0],
                },
                "strategies_compared": len(comparison_data),
            }

        except Exception as e:
            logger.error("对比报告生成失败: %(e)s")
            return {"error": str(e)}

    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """获取缓存的回测结果"""
        return self.results_cache.get(cache_key)

    def clear_cache(self):
        """清空结果缓存"""
        self.results_cache.clear()
        logger.info("回测结果缓存已清空")
