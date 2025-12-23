"""
K线图和信号可视化 (Chart Generator)

功能说明:
- 生成专业K线图（使用mplfinance）
- 标记买卖信号
- 叠加技术指标
- 支持多种图表样式

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import pandas as pd
import numpy as np
import mplfinance as mpf
from typing import Dict, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import logging


class ChartStyle:
    """图表样式配置"""

    # 预定义样式
    CLASSIC = "charles"  # 经典黑底绿涨红跌
    YAHOO = "yahoo"  # Yahoo Finance风格
    BINANCE = "binance"  # 币安风格
    NIGHTCLOUDS = "nightclouds"  # 夜云风格
    SAS = "sas"  # SAS风格

    # 中国股市风格（红涨绿跌）
    CHINA = mpf.make_marketcolors(
        up="red", down="green", edge="inherit", wick="inherit", volume="in", alpha=0.9
    )

    @staticmethod
    def get_china_style():
        """获取中国风格（红涨绿跌）"""
        mc = ChartStyle.CHINA
        return mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle="-",
            y_on_right=True,
            rc={"font.family": "sans-serif"},
        )


class ChartGenerator:
    """
    K线图生成器

    功能:
    - 生成K线图
    - 标记交易信号
    - 叠加技术指标
    - 自定义样式
    """

    def __init__(self, style: str = "china"):
        """
        初始化图表生成器

        参数:
            style: 图表样式，可选值:
                  - 'china': 中国风格（红涨绿跌）
                  - 'charles': 经典风格
                  - 'yahoo': Yahoo风格
                  - 'binance': 币安风格
        """
        self.logger = logging.getLogger(f"{__name__}.ChartGenerator")
        self.logger.setLevel(logging.INFO)

        # 设置样式
        if style == "china":
            self.style = ChartStyle.get_china_style()
        else:
            self.style = style

    def plot_kline(
        self,
        data: pd.DataFrame,
        title: str = "K线图",
        volume: bool = True,
        show: bool = False,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 8),
    ) -> None:
        """
        绘制基础K线图

        参数:
            data: K线数据，必须包含 open, high, low, close, volume
                  index必须是DatetimeIndex
            title: 图表标题
            volume: 是否显示成交量
            show: 是否显示图表
            save_path: 保存路径（可选）
            figsize: 图表大小

        示例:
            >>> generator = ChartGenerator()
            >>> generator.plot_kline(price_data, title="平安银行", save_path="kline.png")
        """
        # 验证数据
        self._validate_kline_data(data)

        # 绘制K线图
        kwargs = {
            "type": "candle",
            "style": self.style,
            "title": title,
            "ylabel": "价格",
            "volume": volume,
            "figsize": figsize,
            "returnfig": True,
        }

        fig, axes = mpf.plot(data, **kwargs)

        # 保存或显示
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            self.logger.info(f"图表已保存: {save_path}")

        if show:
            plt.show()
        else:
            plt.close(fig)

    def plot_with_signals(
        self,
        data: pd.DataFrame,
        signals: pd.DataFrame,
        title: str = "K线图 + 信号",
        volume: bool = True,
        show: bool = False,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (14, 10),
    ) -> None:
        """
        绘制带交易信号的K线图

        参数:
            data: K线数据
            signals: 信号数据，包含 signal ('buy'/'sell'), entry_price
            title: 图表标题
            volume: 是否显示成交量
            show: 是否显示图表
            save_path: 保存路径
            figsize: 图表大小

        示例:
            >>> generator = ChartGenerator()
            >>> generator.plot_with_signals(
            ...     price_data, signals,
            ...     title="动量策略信号",
            ...     save_path="signals.png"
            ... )
        """
        # 验证数据
        self._validate_kline_data(data)

        # 提取买卖信号
        buy_signals = signals[signals["signal"] == "buy"]
        sell_signals = signals[signals["signal"] == "sell"]

        # 准备标记点
        buy_markers = []
        sell_markers = []

        for idx in buy_signals.index:
            if idx in data.index:
                price = buy_signals.loc[idx, "entry_price"]
                buy_markers.append((idx, price))

        for idx in sell_signals.index:
            if idx in data.index:
                price = sell_signals.loc[idx, "entry_price"]
                sell_markers.append((idx, price))

        # 准备addplot（标记点）
        apds = []

        if buy_markers:
            buy_df = pd.DataFrame(buy_markers, columns=["date", "price"])
            buy_df = buy_df.set_index("date")
            buy_df = buy_df.reindex(data.index)

            apds.append(
                mpf.make_addplot(
                    buy_df["price"],
                    type="scatter",
                    markersize=100,
                    marker="^",
                    color="red",
                    panel=0,
                )
            )

        if sell_markers:
            sell_df = pd.DataFrame(sell_markers, columns=["date", "price"])
            sell_df = sell_df.set_index("date")
            sell_df = sell_df.reindex(data.index)

            apds.append(
                mpf.make_addplot(
                    sell_df["price"],
                    type="scatter",
                    markersize=100,
                    marker="v",
                    color="green",
                    panel=0,
                )
            )

        # 绘制K线图
        kwargs = {
            "type": "candle",
            "style": self.style,
            "title": title,
            "ylabel": "价格",
            "volume": volume,
            "figsize": figsize,
            "returnfig": True,
        }

        # 只在有addplot时才添加该参数
        if apds:
            kwargs["addplot"] = apds

        fig, axes = mpf.plot(data, **kwargs)

        # 添加图例
        if buy_markers or sell_markers:
            ax = axes[0]
            legend_elements = []

            if buy_markers:
                legend_elements.append(
                    mpatches.Patch(color="red", label=f"买入 ({len(buy_markers)})")
                )

            if sell_markers:
                legend_elements.append(
                    mpatches.Patch(color="green", label=f"卖出 ({len(sell_markers)})")
                )

            ax.legend(handles=legend_elements, loc="upper left")

        # 保存或显示
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            self.logger.info(f"信号图表已保存: {save_path}")

        if show:
            plt.show()
        else:
            plt.close(fig)

    def plot_with_indicators(
        self,
        data: pd.DataFrame,
        indicators: Dict[str, pd.Series],
        title: str = "K线图 + 指标",
        volume: bool = True,
        show: bool = False,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (14, 10),
    ) -> None:
        """
        绘制带技术指标的K线图

        参数:
            data: K线数据
            indicators: 指标字典，格式: {'指标名': Series}
                       支持主图指标（MA, BOLL等）和副图指标（MACD, RSI等）
            title: 图表标题
            volume: 是否显示成交量
            show: 是否显示图表
            save_path: 保存路径
            figsize: 图表大小

        示例:
            >>> indicators = {
            ...     'MA5': ma5_series,
            ...     'MA20': ma20_series,
            ...     'RSI': rsi_series
            ... }
            >>> generator.plot_with_indicators(
            ...     price_data, indicators,
            ...     save_path="indicators.png"
            ... )
        """
        # 验证数据
        self._validate_kline_data(data)

        # 分类指标（主图 vs 副图）
        main_indicators = {}  # 价格叠加指标
        sub_indicators = {}  # 副图指标

        # 副图指标列表（在0-100范围的指标）
        sub_indicator_names = ["RSI", "KDJ", "CCI", "WR"]

        for name, series in indicators.items():
            # 判断是否为副图指标
            is_sub = any(sub_name in name.upper() for sub_name in sub_indicator_names)

            if is_sub:
                sub_indicators[name] = series
            else:
                main_indicators[name] = series

        # 准备addplot
        apds = []

        # 主图指标（叠加在K线上）
        colors = ["blue", "orange", "purple", "brown", "pink"]
        for idx, (name, series) in enumerate(main_indicators.items()):
            color = colors[idx % len(colors)]
            apds.append(
                mpf.make_addplot(series, panel=0, color=color, width=1.5, label=name)
            )

        # 副图指标
        panel_num = 2 if volume else 1  # volume占用panel 1
        for name, series in sub_indicators.items():
            apds.append(
                mpf.make_addplot(series, panel=panel_num, color="blue", ylabel=name)
            )
            panel_num += 1

        # 绘制K线图
        kwargs = {
            "type": "candle",
            "style": self.style,
            "title": title,
            "ylabel": "价格",
            "volume": volume,
            "figsize": figsize,
            "returnfig": True,
        }

        # 只在有addplot时才添加该参数
        if apds:
            kwargs["addplot"] = apds

        fig, axes = mpf.plot(data, **kwargs)

        # 保存或显示
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            self.logger.info(f"指标图表已保存: {save_path}")

        if show:
            plt.show()
        else:
            plt.close(fig)

    def plot_complete(
        self,
        data: pd.DataFrame,
        signals: Optional[pd.DataFrame] = None,
        indicators: Optional[Dict[str, pd.Series]] = None,
        title: str = "完整K线图",
        volume: bool = True,
        show: bool = False,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (16, 12),
    ) -> None:
        """
        绘制完整图表（K线 + 信号 + 指标）

        参数:
            data: K线数据
            signals: 信号数据（可选）
            indicators: 指标字典（可选）
            title: 图表标题
            volume: 是否显示成交量
            show: 是否显示图表
            save_path: 保存路径
            figsize: 图表大小

        示例:
            >>> generator.plot_complete(
            ...     price_data,
            ...     signals=signals,
            ...     indicators={'MA5': ma5, 'MA20': ma20, 'RSI': rsi},
            ...     title="动量策略完整分析",
            ...     save_path="complete.png"
            ... )
        """
        # 验证数据
        self._validate_kline_data(data)

        apds = []

        # 1. 添加技术指标
        if indicators:
            # 分类指标
            main_indicators = {}
            sub_indicators = {}
            sub_indicator_names = ["RSI", "KDJ", "CCI", "WR", "MACD"]

            for name, series in indicators.items():
                is_sub = any(
                    sub_name in name.upper() for sub_name in sub_indicator_names
                )
                if is_sub:
                    sub_indicators[name] = series
                else:
                    main_indicators[name] = series

            # 主图指标
            colors = ["blue", "orange", "purple", "brown", "pink"]
            for idx, (name, series) in enumerate(main_indicators.items()):
                color = colors[idx % len(colors)]
                apds.append(mpf.make_addplot(series, panel=0, color=color, width=1.5))

            # 副图指标
            panel_num = 2 if volume else 1
            for name, series in sub_indicators.items():
                apds.append(
                    mpf.make_addplot(series, panel=panel_num, color="blue", ylabel=name)
                )
                panel_num += 1

        # 2. 添加交易信号
        if signals is not None:
            buy_signals = signals[signals["signal"] == "buy"]
            sell_signals = signals[signals["signal"] == "sell"]

            # 买入标记
            if not buy_signals.empty:
                buy_df = pd.DataFrame(
                    {"price": buy_signals["entry_price"]}, index=buy_signals.index
                )
                buy_df = buy_df.reindex(data.index)

                apds.append(
                    mpf.make_addplot(
                        buy_df["price"],
                        type="scatter",
                        markersize=120,
                        marker="^",
                        color="red",
                        panel=0,
                    )
                )

            # 卖出标记
            if not sell_signals.empty:
                sell_df = pd.DataFrame(
                    {"price": sell_signals["entry_price"]}, index=sell_signals.index
                )
                sell_df = sell_df.reindex(data.index)

                apds.append(
                    mpf.make_addplot(
                        sell_df["price"],
                        type="scatter",
                        markersize=120,
                        marker="v",
                        color="green",
                        panel=0,
                    )
                )

        # 绘制K线图
        kwargs = {
            "type": "candle",
            "style": self.style,
            "title": title,
            "ylabel": "价格",
            "volume": volume,
            "figsize": figsize,
            "returnfig": True,
        }

        # 只在有addplot时才添加该参数
        if apds:
            kwargs["addplot"] = apds

        fig, axes = mpf.plot(data, **kwargs)

        # 保存或显示
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            self.logger.info(f"完整图表已保存: {save_path}")

        if show:
            plt.show()
        else:
            plt.close(fig)

    def _validate_kline_data(self, data: pd.DataFrame):
        """验证K线数据格式"""
        required_cols = ["open", "high", "low", "close"]
        missing_cols = [col for col in required_cols if col not in data.columns]

        if missing_cols:
            raise ValueError(f"K线数据缺少必需列: {missing_cols}")

        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("K线数据的索引必须是DatetimeIndex")


if __name__ == "__main__":
    # 测试代码
    print("K线图生成器测试")
    print("=" * 70)

    # 生成测试数据
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2024-01-01", periods=n, freq="D")

    # 价格数据
    close_prices = 100 + np.cumsum(np.random.randn(n) * 0.5 + 0.02)
    price_data = pd.DataFrame(
        {
            "open": close_prices + np.random.randn(n) * 0.5,
            "high": close_prices + np.abs(np.random.randn(n)),
            "low": close_prices - np.abs(np.random.randn(n)),
            "close": close_prices,
            "volume": np.random.uniform(1000000, 10000000, n),
        },
        index=dates,
    )

    # 创建生成器
    generator = ChartGenerator(style="china")

    # 测试1: 基础K线图
    print("\n测试1: 生成基础K线图")
    generator.plot_kline(
        price_data, title="测试股票 - K线图", save_path="temp/test_kline.png"
    )
    print("✓ 基础K线图生成成功")

    # 测试2: 带信号的K线图
    print("\n测试2: 生成带信号的K线图")
    signals = pd.DataFrame(index=dates)
    signals["signal"] = None
    signals["entry_price"] = price_data["close"].values

    # 添加一些信号
    for i in range(0, n, 20):
        if i < n:
            signals.loc[signals.index[i], "signal"] = "buy"
        if i + 10 < n:
            signals.loc[signals.index[i + 10], "signal"] = "sell"

    generator.plot_with_signals(
        price_data,
        signals,
        title="测试股票 - K线图 + 交易信号",
        save_path="temp/test_signals.png",
    )
    print("✓ 信号图表生成成功")

    # 测试3: 带指标的K线图
    print("\n测试3: 生成带指标的K线图")

    # 简单移动平均
    ma5 = price_data["close"].rolling(5).mean()
    ma20 = price_data["close"].rolling(20).mean()

    # 模拟RSI
    rsi = pd.Series(50 + np.random.randn(n) * 10, index=dates)
    rsi = rsi.clip(0, 100)

    indicators = {"MA5": ma5, "MA20": ma20, "RSI": rsi}

    generator.plot_with_indicators(
        price_data,
        indicators,
        title="测试股票 - K线图 + 技术指标",
        save_path="temp/test_indicators.png",
    )
    print("✓ 指标图表生成成功")

    # 测试4: 完整图表
    print("\n测试4: 生成完整图表")
    generator.plot_complete(
        price_data,
        signals=signals,
        indicators=indicators,
        title="测试股票 - 完整分析图",
        save_path="temp/test_complete.png",
    )
    print("✓ 完整图表生成成功")

    print("\n" + "=" * 70)
    print("所有测试通过！")
    print("图表已保存到 temp/ 目录")
