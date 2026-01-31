"""
回测引擎主接口 (Backtest Engine)

功能说明:
- 整合向量化回测器、性能指标、风险指标
- 提供统一的回测接口
- 支持单股票和批量回测
- 自动生成完整的回测报告

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import logging
from typing import Dict, Optional

import numpy as np
import pandas as pd

# 导入本地模块
try:
    from .performance_metrics import PerformanceMetrics
    from .risk_metrics import RiskMetrics
    from .vectorized_backtester import BacktestConfig, VectorizedBacktester
except ImportError:
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from backtest.performance_metrics import PerformanceMetrics
    from backtest.risk_metrics import RiskMetrics
    from backtest.vectorized_backtester import BacktestConfig, VectorizedBacktester


class BacktestEngine:
    """
    回测引擎 - 策略回测的统一接口

    功能:
    - 执行向量化回测
    - 计算性能和风险指标
    - 生成完整回测报告
    - 支持基准比较
    """

    def __init__(self, config: Optional[BacktestConfig] = None, risk_free_rate: float = 0.03):
        """
        初始化回测引擎

        参数:
            config: 回测配置
            risk_free_rate: 无风险利率（年化）
        """
        self.config = config or BacktestConfig()
        self.risk_free_rate = risk_free_rate

        # 组件
        self.backtester = VectorizedBacktester(self.config)
        self.perf_metrics = PerformanceMetrics(risk_free_rate)
        self.risk_metrics = RiskMetrics()

        # 日志
        self.logger = logging.getLogger(f"{__name__}.BacktestEngine")
        self.logger.setLevel(logging.INFO)

        # 结果
        self.last_result = None

    def run(
        self,
        price_data: pd.DataFrame,
        signals: pd.DataFrame,
        benchmark_returns: Optional[pd.Series] = None,
    ) -> Dict:
        """
        执行回测

        参数:
            price_data: 价格数据 (open, high, low, close, volume)
            signals: 信号数据 (signal, strength)
            benchmark_returns: 基准收益率（可选）

        返回:
            dict: 完整回测结果
                - backtest: 回测基础结果
                - performance: 性能指标
                - risk: 风险指标
                - report: 文字报告

        示例:
            >>> engine = BacktestEngine()
            >>> result = engine.run(price_data, signals)
            >>> print(result['report'])
        """
        self.logger.info("开始执行回测")

        # 1. 执行向量化回测
        backtest_result = self.backtester.run(price_data, signals)

        # 2. 计算性能指标
        perf_metrics = self.perf_metrics.calculate_all_metrics(
            equity_curve=backtest_result["equity_curve"],
            daily_returns=backtest_result["daily_returns"],
            trades=backtest_result["trades"],
            initial_capital=self.config.initial_capital,
            benchmark_returns=benchmark_returns,
        )

        # 3. 计算风险指标
        risk_metrics_dict = self.risk_metrics.calculate_all_risk_metrics(
            equity_curve=backtest_result["equity_curve"],
            returns=backtest_result["daily_returns"],
            trades=backtest_result["trades"],
            total_return=perf_metrics["total_return"],
            max_drawdown=perf_metrics["max_drawdown"],
            risk_free_rate=self.risk_free_rate,
        )

        # 4. 合并所有指标
        all_metrics = {**perf_metrics, **risk_metrics_dict}

        # 5. 生成报告
        perf_report = self.perf_metrics.generate_report(perf_metrics)
        risk_report = self.risk_metrics.generate_risk_report(risk_metrics_dict)
        full_report = f"{perf_report}\n\n{risk_report}"

        # 6. 构建完整结果
        result = {
            "backtest": backtest_result,
            "performance": perf_metrics,
            "risk": risk_metrics_dict,
            "metrics": all_metrics,
            "report": full_report,
            "config": self.config,
        }

        self.last_result = result
        self.logger.info("回测执行完成")

        return result

    def get_trades_df(self) -> pd.DataFrame:
        """获取交易记录DataFrame"""
        return self.backtester.get_trades_df()

    def get_equity_curve(self) -> pd.DataFrame:
        """获取权益曲线"""
        if self.last_result:
            return self.last_result["backtest"]["equity_curve"]
        return pd.DataFrame()

    def get_daily_returns(self) -> pd.Series:
        """获取每日收益率"""
        if self.last_result:
            return self.last_result["backtest"]["daily_returns"]
        return pd.Series()

    def save_result(self, filepath: str):
        """
        保存回测结果

        参数:
            filepath: 保存路径
        """
        if not self.last_result:
            self.logger.warning("没有可保存的回测结果")
            return

        # 保存交易记录
        trades_df = self.get_trades_df()
        if not trades_df.empty:
            trades_df.to_csv(f"{filepath}_trades.csv", index=False)

        # 保存权益曲线
        equity_curve = self.get_equity_curve()
        if not equity_curve.empty:
            equity_curve.to_csv(f"{filepath}_equity.csv")

        # 保存报告
        with open(f"{filepath}_report.txt", "w", encoding="utf-8") as f:
            f.write(self.last_result["report"])

        self.logger.info("回测结果已保存到 %s", filepath)


if __name__ == "__main__":
    # 测试代码
    print("回测引擎测试")
    print("=" * 70)

    # 生成测试数据
    np.random.seed(42)
    test_n = 100
    test_dates = pd.date_range("2024-01-01", periods=test_n, freq="D")

    # 价格数据
    test_close_prices = 100 + np.cumsum(np.random.randn(test_n) * 0.5 + 0.02)
    test_price_data = pd.DataFrame(
        {
            "open": test_close_prices + np.random.randn(test_n) * 0.5,
            "high": test_close_prices + np.abs(np.random.randn(test_n)),
            "low": test_close_prices - np.abs(np.random.randn(test_n)),
            "close": test_close_prices,
            "volume": np.random.uniform(1000000, 10000000, test_n),
        },
        index=test_dates,
    )

    # 信号数据（简单策略：每20天买入，10天后卖出）
    test_signals = pd.DataFrame(index=test_dates)
    test_signals["signal"] = None
    test_signals["strength"] = 0.0

    for i in range(0, test_n, 20):
        if i < test_n:
            test_signals.iloc[i] = ["buy", 0.8]
        if i + 10 < test_n:
            test_signals.iloc[i + 10] = ["sell", 0.8]

    # 创建回测配置
    test_config = BacktestConfig(
        initial_capital=100000,
        commission_rate=0.0003,
        slippage_rate=0.0001,
        stamp_tax_rate=0.001,
    )

    # 运行回测
    test_engine = BacktestEngine(config=test_config, risk_free_rate=0.03)
    test_result = test_engine.run(test_price_data, test_signals)

    # 打印报告
    print(test_result["report"])

    # 显示一些关键指标
    print("\n关键指标摘要:")
    print(f"  总收益率: {test_result['metrics']['total_return']:.2%}")
    print(f"  年化收益率: {test_result['metrics']['annualized_return']:.2%}")
    print(f"  夏普比率: {test_result['metrics']['sharpe_ratio']:.3f}")
    print(f"  最大回撤: {test_result['metrics']['max_drawdown']:.2%}")
    print(f"  胜率: {test_result['metrics']['win_rate']:.2%}")

    print("\n测试通过！")
