# Chart Visualization Quick Reference

**TL;DR**: Use **mplfinance** for backtesting charts. Use **Plotly** for interactive dashboards.

---

## Decision Matrix

| Requirement | mplfinance | Plotly | PyECharts |
|-------------|-----------|--------|-----------|
| Custom mark areas (date ranges) | ✅ Best | ✅ Good | ⚠️ Complex |
| Buy/sell signal markers | ✅ Best | ✅ Good | ✅ Good |
| Profit/loss color coding | ✅ Best | ✅ Good | ✅ Good |
| PNG/JPG export | ✅ Native | ⚠️ Requires kaleido | ⚠️ Requires Node.js |
| Interactive (zoom/hover) | ❌ Static | ✅ Best | ✅ Good |
| Performance (500-1000 points) | ✅ Best | ✅ Good | ✅ Good |
| Code simplicity | ✅ Best | ⭐⭐⭐ | ⭐⭐ |
| **TOTAL SCORE** | 🏆 **Winner** | 🥈 Runner-up | 🥉 Third |

---

## When to Use What

### Use mplfinance when:
- Generating backtest result charts
- Need static images (PNG/JPG) for reports
- Batch generating 10-1000+ charts
- Want minimal code and fast results
- Creating documentation/presentations

### Use Plotly when:
- Building interactive web dashboards
- Need zoom, pan, hover capabilities
- Client-facing web applications
- Exploratory data analysis in Jupyter
- Real-time strategy monitoring

### DON'T use PyECharts for:
- Quantitative trading backtesting
- Batch chart generation
- Projects without Node.js infrastructure

---

## Installation

```bash
# Required for backtesting
pip install mplfinance pandas numpy

# Optional for interactive dashboards
pip install plotly kaleido
```

---

## Minimal Code Examples

### mplfinance (Recommended)

```python
import mplfinance as mpf
import pandas as pd
import numpy as np

# Prepare signals
buy_signals = pd.Series(np.nan, index=df.index)
sell_signals = pd.Series(np.nan, index=df.index)
buy_signals['2024-01-15'] = df.loc['2024-01-15', 'Low'] * 0.98
sell_signals['2024-03-20'] = df.loc['2024-03-20', 'High'] * 1.02

# Create markers
apds = [
    mpf.make_addplot(buy_signals, type='scatter', markersize=200, marker='^', color='green'),
    mpf.make_addplot(sell_signals, type='scatter', markersize=200, marker='v', color='red')
]

# Plot and save
mpf.plot(df, type='candle', addplot=apds, volume=True, savefig='backtest.png')
```

### Colored Region (Profit/Loss)

```python
# Create holding period mask
mask = pd.Series(False, index=df.index)
mask.loc['2024-01-15':'2024-03-20'] = True

# Determine profit/loss color
entry = df.loc['2024-01-15', 'Close']
exit = df.loc['2024-03-20', 'Close']
color = '#93c47d' if exit > entry else '#e06666'  # Green or Red

# Add fill
fill_plot = mpf.make_addplot(
    df['Close'], type='line', width=0,
    fill_between=dict(
        y1=df['Low'].values,
        y2=df['High'].values,
        where=mask.values,
        color=color,
        alpha=0.2
    )
)

apds.append(fill_plot)
mpf.plot(df, type='candle', addplot=apds, volume=True, savefig='backtest.png')
```

### Plotly (Interactive Alternative)

```python
import plotly.graph_objects as go

fig = go.Figure(data=[
    go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close']
    )
])

# Add buy signal
fig.add_trace(go.Scatter(
    x=['2024-01-15'],
    y=[df.loc['2024-01-15', 'Low'] * 0.98],
    mode='markers',
    marker=dict(symbol='triangle-up', size=15, color='green'),
    name='Buy'
))

# Add colored region
fig.add_vrect(
    x0='2024-01-15', x1='2024-03-20',
    fillcolor='rgba(147, 196, 125, 0.3)',
    layer='below', line_width=0
)

fig.write_html('interactive.html')
```

---

## Key Parameters Reference

### mplfinance.make_addplot()

```python
mpf.make_addplot(
    data,                    # pd.Series with same index as df
    type='scatter',          # 'scatter' for markers, 'line' for lines
    markersize=200,          # Marker size
    marker='^',              # '^' up, 'v' down, 'o' circle
    color='green',           # Marker/line color
    fill_between=dict(       # For colored regions
        y1=lower_bound,
        y2=upper_bound,
        where=boolean_mask,
        color='#93c47d',
        alpha=0.2
    )
)
```

### mplfinance.plot()

```python
mpf.plot(
    df,                      # OHLC DataFrame with DatetimeIndex
    type='candle',           # 'candle' or 'ohlc'
    style='charles',         # 'charles', 'yahoo', 'binance'
    volume=True,             # Show volume bars
    addplot=apds,            # List of make_addplot objects
    savefig='chart.png',     # Output path
    figratio=(16, 9),        # Aspect ratio
    figscale=1.2            # Scale factor
)
```

---

## Common Patterns

### Pattern 1: Multiple Trades

```python
trades = [
    {'entry': '2024-01-15', 'exit': '2024-02-10', 'profit': True},
    {'entry': '2024-03-01', 'exit': '2024-03-25', 'profit': False}
]

apds = []
for trade in trades:
    # Add buy marker
    buy = pd.Series(np.nan, index=df.index)
    buy[trade['entry']] = df.loc[trade['entry'], 'Low'] * 0.98
    apds.append(mpf.make_addplot(buy, type='scatter', markersize=200, marker='^', color='green'))

    # Add sell marker
    sell = pd.Series(np.nan, index=df.index)
    sell[trade['exit']] = df.loc[trade['exit'], 'High'] * 1.02
    apds.append(mpf.make_addplot(sell, type='scatter', markersize=200, marker='v', color='red'))

    # Add colored region
    mask = pd.Series(False, index=df.index)
    mask.loc[trade['entry']:trade['exit']] = True
    color = '#93c47d' if trade['profit'] else '#e06666'

    apds.append(mpf.make_addplot(
        df['Close'], type='line', width=0,
        fill_between=dict(y1=df['Low'].values, y2=df['High'].values,
                         where=mask.values, color=color, alpha=0.2)
    ))

mpf.plot(df, type='candle', addplot=apds, volume=True, savefig='multi_trade.png')
```

### Pattern 2: Trend Lines

```python
# Create trend line series (same index as df)
support = pd.Series(index=df.index)
resistance = pd.Series(index=df.index)

# Define trend lines (example: linear)
support.loc['2024-01-01':'2024-12-31'] = np.linspace(95, 105, len(support))
resistance.loc['2024-01-01':'2024-12-31'] = np.linspace(105, 115, len(resistance))

apds = [
    mpf.make_addplot(support, color='blue', width=1.5, linestyle='--'),
    mpf.make_addplot(resistance, color='red', width=1.5, linestyle='--')
]

mpf.plot(df, type='candle', addplot=apds, volume=True)
```

---

## Color Scheme

### Standard Colors

```python
# Profit/Loss
PROFIT_COLOR = '#93c47d'      # Green
LOSS_COLOR = '#e06666'        # Red

# Signals
BUY_COLOR = 'green'           # Buy marker
SELL_COLOR = 'red'            # Sell marker

# Trend Lines
SUPPORT_COLOR = 'blue'        # Support level
RESISTANCE_COLOR = 'red'      # Resistance level

# Opacity
REGION_ALPHA = 0.2            # Background regions
MARKER_ALPHA = 1.0            # Fully opaque markers
```

---

## Performance Tips

### For Batch Generation (100+ charts)

```python
# Use matplotlib's non-interactive backend
import matplotlib
matplotlib.use('Agg')
import mplfinance as mpf

# Generate charts in loop
for symbol in symbols:
    df = get_data(symbol)
    mpf.plot(df, type='candle', savefig=f'{symbol}_chart.png')
```

### For Large Datasets (10,000+ points)

```python
# Option 1: Resample to lower frequency
df_weekly = df.resample('W').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
})

# Option 2: Use date range slicing
recent_df = df.last('365D')  # Last year only
```

---

## Export Settings

### High-Quality Images

```python
mpf.plot(
    df,
    type='candle',
    savefig=dict(
        fname='chart.png',
        dpi=300,              # High resolution
        bbox_inches='tight'   # No whitespace
    )
)
```

### Different Formats

```python
# PNG (default)
mpf.plot(df, type='candle', savefig='chart.png')

# JPG
mpf.plot(df, type='candle', savefig='chart.jpg')

# SVG (vector, scalable)
mpf.plot(df, type='candle', savefig='chart.svg')

# PDF
mpf.plot(df, type='candle', savefig='chart.pdf')
```

---

## Troubleshooting

### Issue: Markers not showing

**Solution**: Ensure signal series has same index as df
```python
# Wrong
buy_signals = pd.Series([np.nan, 100, np.nan])

# Correct
buy_signals = pd.Series(np.nan, index=df.index)
buy_signals['2024-01-15'] = 100
```

### Issue: Fill area not appearing

**Solution**: Check boolean mask length
```python
# Verify mask length matches df
assert len(mask) == len(df), f"Mask length {len(mask)} != df length {len(df)}"
```

### Issue: Dates not aligning

**Solution**: Ensure df has DatetimeIndex
```python
# Convert to datetime if needed
df.index = pd.to_datetime(df.index)
```

---

## Next Steps

1. Install mplfinance: `pip install mplfinance`
2. Test with sample data (see examples above)
3. Integrate with backtest results
4. Create reusable chart templates
5. (Optional) Add Plotly for interactive features

---

## Resources

- Full research: See `CHART_VISUALIZATION_RESEARCH.md`
- mplfinance docs: https://github.com/matplotlib/mplfinance
- mplfinance examples: https://github.com/matplotlib/mplfinance/tree/master/examples
- Plotly candlestick: https://plotly.com/python/candlestick-charts/

---

**Last Updated**: 2025-10-18
**Status**: Ready for Implementation
