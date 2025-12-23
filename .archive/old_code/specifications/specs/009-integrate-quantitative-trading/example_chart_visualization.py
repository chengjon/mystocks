#!/usr/bin/env python3
"""
Example: Financial K-line Chart Visualization with Trading Signals

This example demonstrates the recommended approach using mplfinance
for creating backtest result charts with:
- Buy/sell signal markers
- Holding period highlighting (colored regions)
- Profit/loss color coding
- Trend lines

Usage:
    python example_chart_visualization.py

Requirements:
    pip install mplfinance pandas numpy yfinance
"""

import mplfinance as mpf
import pandas as pd
import numpy as np
from datetime import datetime

# Optional: Use yfinance to get real data
# Uncomment to use real data instead of synthetic
# import yfinance as yf


def generate_sample_data(days=365):
    """
    Generate sample OHLC data for demonstration.

    In production, replace this with real market data from your adapters.
    """
    dates = pd.date_range(end=datetime.now(), periods=days, freq="D")

    # Generate random walk price data
    np.random.seed(42)
    base_price = 100
    returns = np.random.randn(days) * 2
    close_prices = base_price + np.cumsum(returns)

    # Create OHLC data
    data = pd.DataFrame(
        {
            "Open": close_prices + np.random.randn(days) * 0.5,
            "High": close_prices + abs(np.random.randn(days)) * 1.5,
            "Low": close_prices - abs(np.random.randn(days)) * 1.5,
            "Close": close_prices,
            "Volume": np.random.randint(1000000, 5000000, days),
        },
        index=dates,
    )

    # Ensure High is highest and Low is lowest
    data["High"] = data[["Open", "High", "Close"]].max(axis=1)
    data["Low"] = data[["Open", "Low", "Close"]].min(axis=1)

    return data


def example_1_simple_signals(df):
    """
    Example 1: Simple chart with buy/sell signals only.
    """
    print("Generating Example 1: Simple Buy/Sell Signals...")

    # Create signal series (same index as df, filled with NaN)
    buy_signals = pd.Series(np.nan, index=df.index)
    sell_signals = pd.Series(np.nan, index=df.index)

    # Mark buy/sell points (position markers slightly below/above candles)
    buy_date = df.index[30]
    sell_date = df.index[90]

    buy_signals[buy_date] = df.loc[buy_date, "Low"] * 0.98
    sell_signals[sell_date] = df.loc[sell_date, "High"] * 1.02

    # Create marker plots
    apds = [
        mpf.make_addplot(
            buy_signals,
            type="scatter",
            markersize=200,
            marker="^",  # Triangle up
            color="green",
        ),
        mpf.make_addplot(
            sell_signals,
            type="scatter",
            markersize=200,
            marker="v",  # Triangle down
            color="red",
        ),
    ]

    # Plot and save
    mpf.plot(
        df,
        type="candle",
        style="charles",
        title="Example 1: Simple Buy/Sell Signals",
        ylabel="Price",
        volume=True,
        addplot=apds,
        savefig="example_1_simple_signals.png",
        figratio=(16, 9),
        figscale=1.2,
    )

    print("  Saved: example_1_simple_signals.png")


def example_2_colored_regions(df):
    """
    Example 2: Chart with holding period highlighted (profit/loss coloring).
    """
    print("Generating Example 2: Colored Holding Periods...")

    # Define trade
    buy_date = df.index[50]
    sell_date = df.index[120]
    entry_price = df.loc[buy_date, "Close"]
    exit_price = df.loc[sell_date, "Close"]

    # Determine profit or loss
    is_profit = exit_price > entry_price
    profit_pct = ((exit_price / entry_price) - 1) * 100
    color = "#93c47d" if is_profit else "#e06666"  # Green or Red

    # Create signals
    buy_signals = pd.Series(np.nan, index=df.index)
    sell_signals = pd.Series(np.nan, index=df.index)
    buy_signals[buy_date] = df.loc[buy_date, "Low"] * 0.98
    sell_signals[sell_date] = df.loc[sell_date, "High"] * 1.02

    # Create holding period mask
    holding_mask = pd.Series(False, index=df.index)
    holding_mask.loc[buy_date:sell_date] = True

    # Create plots
    apds = [
        mpf.make_addplot(
            buy_signals, type="scatter", markersize=200, marker="^", color="green"
        ),
        mpf.make_addplot(
            sell_signals, type="scatter", markersize=200, marker="v", color="red"
        ),
        # Colored region for holding period
        mpf.make_addplot(
            df["Close"],
            type="line",
            width=0,  # Invisible line
            fill_between=dict(
                y1=df["Low"].values,
                y2=df["High"].values,
                where=holding_mask.values,
                color=color,
                alpha=0.2,
                interpolate=True,
            ),
        ),
    ]

    # Plot with profit/loss in title
    result = "Profit" if is_profit else "Loss"
    mpf.plot(
        df,
        type="candle",
        style="charles",
        title=f"Example 2: Holding Period ({result}: {profit_pct:.2f}%)",
        ylabel="Price",
        volume=True,
        addplot=apds,
        savefig="example_2_colored_regions.png",
        figratio=(16, 9),
        figscale=1.2,
    )

    print(f"  Saved: example_2_colored_regions.png ({result}: {profit_pct:.2f}%)")


def example_3_multiple_trades(df):
    """
    Example 3: Multiple trades with different profit/loss outcomes.
    """
    print("Generating Example 3: Multiple Trades...")

    # Define multiple trades
    trades = [
        {"entry": df.index[30], "exit": df.index[70]},  # Trade 1
        {"entry": df.index[90], "exit": df.index[130]},  # Trade 2
        {"entry": df.index[150], "exit": df.index[200]},  # Trade 3
    ]

    apds = []

    for i, trade in enumerate(trades, 1):
        entry_date = trade["entry"]
        exit_date = trade["exit"]
        entry_price = df.loc[entry_date, "Close"]
        exit_price = df.loc[exit_date, "Close"]

        # Determine profit/loss
        is_profit = exit_price > entry_price
        color = "#93c47d" if is_profit else "#e06666"

        # Add buy signal
        buy_signal = pd.Series(np.nan, index=df.index)
        buy_signal[entry_date] = df.loc[entry_date, "Low"] * 0.98
        apds.append(
            mpf.make_addplot(
                buy_signal, type="scatter", markersize=150, marker="^", color="green"
            )
        )

        # Add sell signal
        sell_signal = pd.Series(np.nan, index=df.index)
        sell_signal[exit_date] = df.loc[exit_date, "High"] * 1.02
        apds.append(
            mpf.make_addplot(
                sell_signal, type="scatter", markersize=150, marker="v", color="red"
            )
        )

        # Add colored holding period
        mask = pd.Series(False, index=df.index)
        mask.loc[entry_date:exit_date] = True

        apds.append(
            mpf.make_addplot(
                df["Close"],
                type="line",
                width=0,
                fill_between=dict(
                    y1=df["Low"].values,
                    y2=df["High"].values,
                    where=mask.values,
                    color=color,
                    alpha=0.2,
                ),
            )
        )

    # Plot
    mpf.plot(
        df,
        type="candle",
        style="charles",
        title="Example 3: Multiple Trading Periods",
        ylabel="Price",
        volume=True,
        addplot=apds,
        savefig="example_3_multiple_trades.png",
        figratio=(16, 9),
        figscale=1.2,
    )

    print(f"  Saved: example_3_multiple_trades.png ({len(trades)} trades)")


def example_4_with_trendlines(df):
    """
    Example 4: Chart with trend lines and support/resistance levels.
    """
    print("Generating Example 4: Trend Lines and Support/Resistance...")

    # Calculate simple moving averages as trend lines
    sma_20 = df["Close"].rolling(window=20).mean()
    sma_50 = df["Close"].rolling(window=50).mean()

    # Define support/resistance levels (example: horizontal lines)
    support_level = pd.Series(df["Close"].min() * 1.05, index=df.index)
    resistance_level = pd.Series(df["Close"].max() * 0.95, index=df.index)

    # Create plots
    apds = [
        # Moving averages
        mpf.make_addplot(sma_20, color="blue", width=1.5, label="SMA 20"),
        mpf.make_addplot(sma_50, color="orange", width=1.5, label="SMA 50"),
        # Support/Resistance
        mpf.make_addplot(
            support_level, color="green", width=1, linestyle="--", label="Support"
        ),
        mpf.make_addplot(
            resistance_level, color="red", width=1, linestyle="--", label="Resistance"
        ),
    ]

    # Plot
    mpf.plot(
        df,
        type="candle",
        style="charles",
        title="Example 4: Trend Lines and Support/Resistance",
        ylabel="Price",
        volume=True,
        addplot=apds,
        savefig="example_4_trendlines.png",
        figratio=(16, 9),
        figscale=1.2,
    )

    print("  Saved: example_4_trendlines.png")


def example_5_complete_backtest(df):
    """
    Example 5: Complete backtest visualization combining all features.
    """
    print("Generating Example 5: Complete Backtest Report...")

    # Simulate backtest results
    trades = [
        {"entry": df.index[40], "exit": df.index[80]},
        {"entry": df.index[100], "exit": df.index[140]},
        {"entry": df.index[160], "exit": df.index[220]},
    ]

    # Calculate overall performance
    total_pnl = 0
    winning_trades = 0

    apds = []

    for trade in trades:
        entry_date = trade["entry"]
        exit_date = trade["exit"]
        entry_price = df.loc[entry_date, "Close"]
        exit_price = df.loc[exit_date, "Close"]

        pnl = ((exit_price / entry_price) - 1) * 100
        total_pnl += pnl

        if pnl > 0:
            winning_trades += 1

        is_profit = exit_price > entry_price
        color = "#93c47d" if is_profit else "#e06666"

        # Signals
        buy_signal = pd.Series(np.nan, index=df.index)
        sell_signal = pd.Series(np.nan, index=df.index)
        buy_signal[entry_date] = df.loc[entry_date, "Low"] * 0.98
        sell_signal[exit_date] = df.loc[exit_date, "High"] * 1.02

        apds.extend(
            [
                mpf.make_addplot(
                    buy_signal,
                    type="scatter",
                    markersize=150,
                    marker="^",
                    color="green",
                ),
                mpf.make_addplot(
                    sell_signal, type="scatter", markersize=150, marker="v", color="red"
                ),
            ]
        )

        # Colored region
        mask = pd.Series(False, index=df.index)
        mask.loc[entry_date:exit_date] = True

        apds.append(
            mpf.make_addplot(
                df["Close"],
                type="line",
                width=0,
                fill_between=dict(
                    y1=df["Low"].values,
                    y2=df["High"].values,
                    where=mask.values,
                    color=color,
                    alpha=0.2,
                ),
            )
        )

    # Add moving averages
    sma_20 = df["Close"].rolling(window=20).mean()
    apds.append(mpf.make_addplot(sma_20, color="purple", width=1))

    # Calculate statistics
    win_rate = (winning_trades / len(trades)) * 100 if trades else 0

    # Plot with statistics in title
    title = (
        f"Example 5: Complete Backtest Report\n"
        f"Trades: {len(trades)} | Win Rate: {win_rate:.1f}% | "
        f"Total P/L: {total_pnl:.2f}%"
    )

    mpf.plot(
        df,
        type="candle",
        style="charles",
        title=title,
        ylabel="Price",
        volume=True,
        addplot=apds,
        savefig="example_5_complete_backtest.png",
        figratio=(16, 9),
        figscale=1.5,
    )

    print("  Saved: example_5_complete_backtest.png")
    print(
        f"  Statistics: {len(trades)} trades, {win_rate:.1f}% win rate, "
        f"{total_pnl:.2f}% total P/L"
    )


def example_6_high_resolution_export(df):
    """
    Example 6: High-resolution export for documentation.
    """
    print("Generating Example 6: High-Resolution Export...")

    # Simple chart for high-res export
    buy_signals = pd.Series(np.nan, index=df.index)
    sell_signals = pd.Series(np.nan, index=df.index)
    buy_signals[df.index[50]] = df.loc[df.index[50], "Low"] * 0.98
    sell_signals[df.index[100]] = df.loc[df.index[100], "High"] * 1.02

    apds = [
        mpf.make_addplot(
            buy_signals, type="scatter", markersize=200, marker="^", color="green"
        ),
        mpf.make_addplot(
            sell_signals, type="scatter", markersize=200, marker="v", color="red"
        ),
    ]

    # Export at high resolution (300 DPI)
    mpf.plot(
        df,
        type="candle",
        style="charles",
        title="Example 6: High-Resolution Export (300 DPI)",
        ylabel="Price",
        volume=True,
        addplot=apds,
        savefig=dict(
            fname="example_6_high_resolution.png", dpi=300, bbox_inches="tight"
        ),
        figratio=(16, 9),
        figscale=1.5,
    )

    print("  Saved: example_6_high_resolution.png (300 DPI)")


def main():
    """
    Run all examples.
    """
    print("\n" + "=" * 70)
    print("Financial K-line Chart Visualization Examples")
    print("Using: mplfinance (Recommended Library)")
    print("=" * 70 + "\n")

    # Generate sample data
    print("Generating sample OHLC data (365 days)...")
    df = generate_sample_data(days=365)
    print(f"  Data shape: {df.shape}")
    print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
    print()

    # Run examples
    try:
        example_1_simple_signals(df)
        example_2_colored_regions(df)
        example_3_multiple_trades(df)
        example_4_with_trendlines(df)
        example_5_complete_backtest(df)
        example_6_high_resolution_export(df)

        print("\n" + "=" * 70)
        print("All examples generated successfully!")
        print("=" * 70 + "\n")

        print("Generated files:")
        print("  - example_1_simple_signals.png")
        print("  - example_2_colored_regions.png")
        print("  - example_3_multiple_trades.png")
        print("  - example_4_trendlines.png")
        print("  - example_5_complete_backtest.png")
        print("  - example_6_high_resolution.png (300 DPI)")
        print()

        print("Next steps:")
        print("  1. Review the generated charts")
        print("  2. Adapt the code patterns for your backtesting system")
        print("  3. Integrate with MyStocks quantitative trading module")
        print()

    except Exception as e:
        print(f"\nError generating examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
