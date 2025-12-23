"""
回测性能可视化 (Backtest Visualizer)

功能说明:
- 权益曲线图
- 回撤分析图
- 收益分布图
- 月度/年度收益表
- 综合性能仪表盘

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
from typing import Dict, Optional, Tuple
import logging


class BacktestVisualizer:
    """
    回测性能可视化器

    功能:
    - 生成权益曲线
    - 回撤分析
    - 收益分布
    - 性能仪表盘
    """

    def __init__(self, figsize: Tuple[int, int] = (14, 10)):
        """
        初始化可视化器

        参数:
            figsize: 默认图表大小
        """
        self.logger = logging.getLogger(f"{__name__}.BacktestVisualizer")
        self.logger.setLevel(logging.INFO)
        self.figsize = figsize

        # 设置中文字体（如果可用）
        plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

    def plot_equity_curve(
        self,
        equity_curve: pd.DataFrame,
        benchmark: Optional[pd.Series] = None,
        title: str = "权益曲线",
        show: bool = False,
        save_path: Optional[str] = None,
    ) -> None:
        """
        绘制权益曲线

        参数:
            equity_curve: 权益曲线DataFrame，包含'equity'列
            benchmark: 基准收益率（可选）
            title: 图表标题
            show: 是否显示图表
            save_path: 保存路径

        示例:
            >>> visualizer = BacktestVisualizer()
            >>> visualizer.plot_equity_curve(
            ...     equity_curve,
            ...     benchmark=benchmark_returns,
            ...     save_path="equity_curve.png"
            ... )
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # 绘制权益曲线
        ax.plot(
            equity_curve.index,
            equity_curve["equity"],
            label="Strategy",
            linewidth=2,
            color="blue",
        )

        # 绘制基准（如果提供）
        if benchmark is not None:
            # 将基准收益率转换为权益曲线
            initial_capital = equity_curve["equity"].iloc[0]
            benchmark_equity = initial_capital * (1 + benchmark).cumprod()
            ax.plot(
                benchmark_equity.index,
                benchmark_equity,
                label="Benchmark",
                linewidth=2,
                color="gray",
                alpha=0.7,
            )

        # 格式化
        ax.set_title(title, fontsize=16, fontweight="bold")
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Equity", fontsize=12)
        ax.legend(loc="best", fontsize=11)
        ax.grid(True, alpha=0.3)

        # 格式化日期
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        plt.xticks(rotation=45)

        plt.tight_layout()

        # 保存或显示
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            self.logger.info(f"权益曲线已保存: {save_path}")

        if show:
            plt.show()
        else:
            plt.close(fig)

    def plot_drawdown(
        self,
        equity_curve: pd.DataFrame,
        title: str = "回撤分析",
        show: bool = False,
        save_path: Optional[str] = None,
    ) -> None:
        """
        绘制回撤分析图

        参数:
            equity_curve: 权益曲线DataFrame
            title: 图表标题
            show: 是否显示图表
            save_path: 保存路径
        """
        # 计算回撤
        cummax = equity_curve["equity"].cummax()
        drawdown = (equity_curve["equity"] - cummax) / cummax

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, sharex=True)

        # 上图: 权益曲线 + 历史最高
        ax1.plot(
            equity_curve.index,
            equity_curve["equity"],
            label="Equity",
            linewidth=2,
            color="blue",
        )
        ax1.plot(
            equity_curve.index,
            cummax,
            label="Peak",
            linewidth=1,
            linestyle="--",
            color="red",
            alpha=0.7,
        )
        ax1.set_title(title, fontsize=16, fontweight="bold")
        ax1.set_ylabel("Equity", fontsize=12)
        ax1.legend(loc="best")
        ax1.grid(True, alpha=0.3)

        # 下图: 回撤
        ax2.fill_between(equity_curve.index, drawdown * 100, 0, color="red", alpha=0.3)
        ax2.plot(equity_curve.index, drawdown * 100, linewidth=1.5, color="darkred")
        ax2.set_xlabel("Date", fontsize=12)
        ax2.set_ylabel("Drawdown (%)", fontsize=12)
        ax2.grid(True, alpha=0.3)

        # 标记最大回撤
        max_dd_idx = drawdown.idxmin()
        max_dd_value = drawdown.min()
        ax2.scatter([max_dd_idx], [max_dd_value * 100], color="red", s=100, zorder=5)
        ax2.annotate(
            f"Max DD: {max_dd_value * 100:.2f}%",
            xy=(max_dd_idx, max_dd_value * 100),
            xytext=(10, 10),
            textcoords="offset points",
            fontsize=10,
            color="red",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

        # 格式化日期
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        plt.xticks(rotation=45)

        plt.tight_layout()

        # 保存或显示
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            self.logger.info(f"回撤图已保存: {save_path}")

        if show:
            plt.show()
        else:
            plt.close(fig)

    def plot_returns_distribution(
        self,
        daily_returns: pd.Series,
        title: str = "收益分布",
        show: bool = False,
        save_path: Optional[str] = None,
    ) -> None:
        """
        绘制收益分布图

        参数:
            daily_returns: 每日收益率
            title: 图表标题
            show: 是否显示图表
            save_path: 保存路径
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)

        # 左图: 直方图
        returns_pct = daily_returns.dropna() * 100
        ax1.hist(returns_pct, bins=50, color="skyblue", alpha=0.7, edgecolor="black")
        ax1.axvline(
            returns_pct.mean(),
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"Mean: {returns_pct.mean():.3f}%",
        )
        ax1.axvline(0, color="gray", linestyle="-", linewidth=1, alpha=0.5)
        ax1.set_title("Returns Distribution", fontsize=14, fontweight="bold")
        ax1.set_xlabel("Daily Returns (%)", fontsize=12)
        ax1.set_ylabel("Frequency", fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 右图: Q-Q图（正态性检验）
        from scipy import stats as sp_stats

        sp_stats.probplot(returns_pct, dist="norm", plot=ax2)
        ax2.set_title("Q-Q Plot (Normality Test)", fontsize=14, fontweight="bold")
        ax2.grid(True, alpha=0.3)

        plt.suptitle(title, fontsize=16, fontweight="bold", y=1.02)
        plt.tight_layout()

        # 保存或显示
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            self.logger.info(f"收益分布图已保存: {save_path}")

        if show:
            plt.show()
        else:
            plt.close(fig)

    def plot_monthly_returns(
        self,
        daily_returns: pd.Series,
        title: str = "月度收益热力图",
        show: bool = False,
        save_path: Optional[str] = None,
    ) -> None:
        """
        绘制月度收益热力图

        参数:
            daily_returns: 每日收益率
            title: 图表标题
            show: 是否显示图表
            save_path: 保存路径
        """
        # 计算月度收益
        monthly_returns = daily_returns.resample("ME").apply(
            lambda x: (1 + x).prod() - 1
        )

        # 创建年月矩阵
        monthly_df = pd.DataFrame(
            {
                "year": monthly_returns.index.year,
                "month": monthly_returns.index.month,
                "return": monthly_returns.values * 100,
            }
        )

        # Pivot表
        heatmap_data = monthly_df.pivot(index="year", columns="month", values="return")

        # 绘制热力图
        fig, ax = plt.subplots(figsize=(12, 6))

        # 创建颜色映射
        # pylint: disable=no-member
        cmap = plt.cm.RdYlGn
        im = ax.imshow(heatmap_data.values, cmap=cmap, aspect="auto", vmin=-10, vmax=10)

        # 设置刻度
        ax.set_xticks(np.arange(len(heatmap_data.columns)))
        ax.set_yticks(np.arange(len(heatmap_data.index)))

        # 月份标签（只显示实际存在的月份）
        month_labels = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        actual_month_labels = [month_labels[m - 1] for m in heatmap_data.columns]
        ax.set_xticklabels(actual_month_labels)
        ax.set_yticklabels(heatmap_data.index)

        # 在每个单元格中显示数值
        for i in range(len(heatmap_data.index)):
            for j in range(len(heatmap_data.columns)):
                value = heatmap_data.iloc[i, j]
                if not np.isnan(value):
                    text = ax.text(
                        j,
                        i,
                        f"{value:.1f}%",
                        ha="center",
                        va="center",
                        color="black" if abs(value) < 5 else "white",
                        fontsize=9,
                    )

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Monthly Return (%)", rotation=270, labelpad=20)

        ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Year", fontsize=12)

        plt.tight_layout()

        # 保存或显示
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            self.logger.info(f"月度收益图已保存: {save_path}")

        if show:
            plt.show()
        else:
            plt.close(fig)

    def plot_dashboard(
        self,
        result: Dict,
        title: str = "回测性能仪表盘",
        show: bool = False,
        save_path: Optional[str] = None,
    ) -> None:
        """
        绘制综合性能仪表盘

        参数:
            result: 回测结果字典，包含:
                   - backtest: 回测基础结果
                   - performance: 性能指标
                   - risk: 风险指标
            title: 图表标题
            show: 是否显示图表
            save_path: 保存路径

        示例:
            >>> from backtest.backtest_engine import BacktestEngine
            >>> engine = BacktestEngine()
            >>> result = engine.run(price_data, signals)
            >>> visualizer = BacktestVisualizer()
            >>> visualizer.plot_dashboard(result, save_path="dashboard.png")
        """
        # 提取数据
        equity_curve = result["backtest"]["equity_curve"]
        daily_returns = result["backtest"]["daily_returns"]
        metrics = result["metrics"]

        # 创建子图布局
        fig = plt.figure(figsize=(18, 12))
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

        # 1. 权益曲线（左上，跨2列）
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.plot(equity_curve.index, equity_curve["equity"], linewidth=2, color="blue")
        ax1.set_title("Equity Curve", fontsize=13, fontweight="bold")
        ax1.set_ylabel("Equity", fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

        # 2. 关键指标（右上）
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.axis("off")
        metrics_text = f"""
        PERFORMANCE METRICS
        {"=" * 30}
        Total Return:     {metrics.get("total_return", 0):.2%}
        Annual Return:    {metrics.get("annualized_return", 0):.2%}
        Sharpe Ratio:     {metrics.get("sharpe_ratio", 0):.3f}
        Max Drawdown:     {metrics.get("max_drawdown", 0):.2%}

        TRADE STATISTICS
        {"=" * 30}
        Total Trades:     {metrics.get("total_trades", 0)}
        Win Rate:         {metrics.get("win_rate", 0):.2%}
        Profit Factor:    {metrics.get("profit_factor", 0):.2f}
        Avg Holding:      {metrics.get("avg_holding_days", 0):.1f} days
        """
        ax2.text(
            0.1,
            0.9,
            metrics_text,
            transform=ax2.transAxes,
            fontsize=10,
            verticalalignment="top",
            family="monospace",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.3),
        )

        # 3. 回撤图（中间，跨3列）
        ax3 = fig.add_subplot(gs[1, :])
        cummax = equity_curve["equity"].cummax()
        drawdown = (equity_curve["equity"] - cummax) / cummax
        ax3.fill_between(equity_curve.index, drawdown * 100, 0, color="red", alpha=0.3)
        ax3.plot(equity_curve.index, drawdown * 100, linewidth=1.5, color="darkred")
        ax3.set_title("Drawdown", fontsize=13, fontweight="bold")
        ax3.set_ylabel("Drawdown (%)", fontsize=11)
        ax3.grid(True, alpha=0.3)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

        # 4. 收益分布（左下）
        ax4 = fig.add_subplot(gs[2, 0])
        returns_pct = daily_returns.dropna() * 100
        ax4.hist(returns_pct, bins=40, color="skyblue", alpha=0.7, edgecolor="black")
        ax4.axvline(returns_pct.mean(), color="red", linestyle="--", linewidth=2)
        ax4.axvline(0, color="gray", linestyle="-", linewidth=1, alpha=0.5)
        ax4.set_title("Returns Distribution", fontsize=13, fontweight="bold")
        ax4.set_xlabel("Daily Returns (%)", fontsize=10)
        ax4.set_ylabel("Frequency", fontsize=10)
        ax4.grid(True, alpha=0.3)

        # 5. 月度收益（中下）
        ax5 = fig.add_subplot(gs[2, 1])
        monthly_returns = (
            daily_returns.resample("ME").apply(lambda x: (1 + x).prod() - 1) * 100
        )
        colors = ["green" if x > 0 else "red" for x in monthly_returns]
        ax5.bar(range(len(monthly_returns)), monthly_returns, color=colors, alpha=0.7)
        ax5.axhline(0, color="black", linestyle="-", linewidth=1)
        ax5.set_title("Monthly Returns", fontsize=13, fontweight="bold")
        ax5.set_ylabel("Return (%)", fontsize=10)
        ax5.grid(True, alpha=0.3, axis="y")

        # 6. 滚动波动率（右下）
        ax6 = fig.add_subplot(gs[2, 2])
        rolling_vol = daily_returns.rolling(20).std() * np.sqrt(252) * 100
        ax6.plot(rolling_vol.index, rolling_vol, linewidth=1.5, color="purple")
        ax6.set_title("Rolling Volatility (20d)", fontsize=13, fontweight="bold")
        ax6.set_ylabel("Volatility (%)", fontsize=10)
        ax6.grid(True, alpha=0.3)
        ax6.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        plt.setp(ax6.xaxis.get_majorticklabels(), rotation=45)

        # 总标题
        fig.suptitle(title, fontsize=18, fontweight="bold", y=0.995)

        # 保存或显示
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            self.logger.info(f"仪表盘已保存: {save_path}")

        if show:
            plt.show()
        else:
            plt.close(fig)


if __name__ == "__main__":
    # 测试代码
    print("回测可视化测试")
    print("=" * 70)

    # 生成测试数据
    np.random.seed(42)
    n = 252
    dates = pd.date_range("2024-01-01", periods=n, freq="D")

    # 模拟权益曲线
    returns = np.random.randn(n) * 0.015 + 0.0005
    equity = 100000 * (1 + returns).cumprod()

    equity_curve = pd.DataFrame(
        {"equity": equity, "cash": 50000, "position": 500, "price": 100}, index=dates
    )

    daily_returns = pd.Series(returns, index=dates)

    # 创建可视化器
    visualizer = BacktestVisualizer()

    # 测试1: 权益曲线
    print("\n测试1: 生成权益曲线")
    visualizer.plot_equity_curve(
        equity_curve,
        title="Test Strategy - Equity Curve",
        save_path="temp/equity_curve.png",
    )
    print("✓ 权益曲线生成成功")

    # 测试2: 回撤图
    print("\n测试2: 生成回撤图")
    visualizer.plot_drawdown(
        equity_curve,
        title="Test Strategy - Drawdown Analysis",
        save_path="temp/drawdown.png",
    )
    print("✓ 回撤图生成成功")

    # 测试3: 收益分布
    print("\n测试3: 生成收益分布图")
    visualizer.plot_returns_distribution(
        daily_returns,
        title="Test Strategy - Returns Distribution",
        save_path="temp/returns_dist.png",
    )
    print("✓ 收益分布图生成成功")

    # 测试4: 月度收益
    print("\n测试4: 生成月度收益热力图")
    visualizer.plot_monthly_returns(
        daily_returns,
        title="Test Strategy - Monthly Returns",
        save_path="temp/monthly_returns.png",
    )
    print("✓ 月度收益图生成成功")

    # 测试5: 综合仪表盘
    print("\n测试5: 生成综合仪表盘")

    # 创建模拟回测结果
    mock_result = {
        "backtest": {
            "equity_curve": equity_curve,
            "daily_returns": daily_returns,
            "trades": [],
        },
        "performance": {},
        "metrics": {
            "total_return": 0.1105,
            "annualized_return": 0.1105,
            "sharpe_ratio": 0.563,
            "max_drawdown": 0.1353,
            "total_trades": 13,
            "win_rate": 0.3846,
            "profit_factor": 0.88,
            "avg_holding_days": 10.0,
        },
    }

    visualizer.plot_dashboard(
        mock_result,
        title="Test Strategy - Performance Dashboard",
        save_path="temp/dashboard.png",
    )
    print("✓ 综合仪表盘生成成功")

    print("\n" + "=" * 70)
    print("所有测试通过！")
    print("图表已保存到 temp/ 目录")
