# RQAlpha Quantitative Trading Framework Integration Research

**Document Version**: 1.0
**Date**: 2025-10-18
**Research Context**: Integrating backtesting capabilities into MyStocks system for strategy evaluation

---

## Executive Summary

### Recommended Approach: Hybrid Vectorized + Event-Driven Architecture

**Decision**: Implement a **two-tier backtesting system** combining:
1. **Primary**: Custom vectorized backtesting engine using pandas/NumPy for signal-based strategies
2. **Optional**: RQAlpha integration for event-driven validation of top-performing strategies

**Rationale**:
- MyStocks already has pre-computed signals (buy/sell dates) - vectorized approach is natural fit
- 12-75x faster performance for screening multiple strategies
- Direct integration with existing PostgreSQL/TDengine data infrastructure
- No dependency on external data bundle formats
- RQAlpha can be added later for realistic execution simulation

---

## Research Findings

### 1. RQAlpha Custom Data Bundle Creation

#### Overview
RQAlpha uses a bundle-based data architecture where market data is pre-processed into binary format for fast access during backtesting. The default bundle path is `~/.rqalpha/bundle/`.

#### Custom Data Source Implementation

**Method 1: Extend BaseDataSource (Recommended for MyStocks)**

```python
from rqalpha.data.base_data_source import BaseDataSource
import pandas as pd

class MyStocksDataSource(BaseDataSource):
    """
    Custom data source integrating with MyStocks PostgreSQL/TDengine databases
    """

    def __init__(self, postgres_access, tdengine_access):
        super(MyStocksDataSource, self).__init__()
        self.pg_access = postgres_access
        self.td_access = tdengine_access

    def get_bar(self, order_book_id, dt, frequency='1d'):
        """
        Retrieve single bar data for a specific instrument and datetime

        Returns: numpy array with OHLCV data
        """
        if frequency == '1d':
            # Query from PostgreSQL (daily data)
            query = """
                SELECT open, high, low, close, volume
                FROM daily_bars
                WHERE symbol = %s AND date = %s
            """
            result = self.pg_access.execute_query(query, (order_book_id, dt))
        else:
            # Query from TDengine (minute data)
            query = """
                SELECT open, high, low, close, volume
                FROM minute_bars
                WHERE symbol = %s AND ts = %s
            """
            result = self.td_access.execute_query(query, (order_book_id, dt))

        return self._convert_to_bar_array(result)

    def history_bars(self, order_book_id, bar_count, frequency, fields, dt):
        """
        Retrieve historical bars for backtesting

        Returns: numpy array or pandas DataFrame
        """
        end_date = dt

        if frequency == '1d':
            # PostgreSQL query for daily bars
            query = """
                SELECT ts, open, high, low, close, volume
                FROM daily_bars
                WHERE symbol = %s AND date <= %s
                ORDER BY date DESC
                LIMIT %s
            """
            df = self.pg_access.query_to_dataframe(
                query, (order_book_id, end_date, bar_count)
            )
        else:
            # TDengine query for minute bars
            query = """
                SELECT ts, open, high, low, close, volume
                FROM minute_bars
                WHERE symbol = ? AND ts <= ?
                ORDER BY ts DESC
                LIMIT ?
            """
            df = self.td_access.query_to_dataframe(
                query, (order_book_id, end_date, bar_count)
            )

        return df[fields].values if fields else df.values

    def get_trading_calendar(self):
        """
        Return trading calendar from MySQL reference data
        """
        query = "SELECT trade_date FROM trading_calendar WHERE is_open = 1"
        return self.mysql_access.query_to_list(query)

    def available_data_range(self, frequency):
        """
        Return date range of available data
        """
        if frequency == '1d':
            query = "SELECT MIN(date), MAX(date) FROM daily_bars"
            return self.pg_access.execute_query(query)
        else:
            query = "SELECT MIN(ts), MAX(ts) FROM minute_bars"
            return self.td_access.execute_query(query)
```

**Method 2: Binary Bundle Conversion (Not Recommended)**

RQAlpha 4.0.0 restructured bundle format to binary for performance. Converting PostgreSQL data to bundle format requires:
- Understanding proprietary binary format
- Pre-processing entire dataset
- Loses real-time data update capability
- Not suitable for MyStocks which emphasizes live data integration

**Pitfalls Identified**:
1. **Bundle Version Incompatibility**: RQAlpha 3.x bundles incompatible with 4.x+
2. **Data Format Mismatch**: Symbol naming conventions differ (e.g., '000001.XSHG' vs '000001')
3. **Performance Issues**: PostgreSQL time-series queries can be slow without TimescaleDB optimization
4. **Calendar Misalignment**: Trading calendar must exactly match or RQAlpha skips days
5. **Missing Data Handling**: RQAlpha expects complete data; gaps cause errors

---

### 2. Injecting Pre-Computed Signals into RQAlpha

#### Challenge
RQAlpha is designed as an **event-driven backtesting engine** where strategies generate signals in real-time during simulation. Injecting pre-computed signals conflicts with this architecture.

#### Solution Approaches

**Approach 1: Signal File Strategy (Hacky but Works)**

```python
from rqalpha import run_func
from rqalpha.api import *
import pandas as pd

# Load pre-computed signals
signals_df = pd.read_csv('precomputed_signals.csv')
signals_df['date'] = pd.to_datetime(signals_df['date'])
signals_dict = signals_df.set_index(['date', 'symbol'])['action'].to_dict()

def init(context):
    context.signals = signals_dict
    context.stocks = signals_df['symbol'].unique().tolist()

def handle_bar(context, bar_dict):
    current_date = context.now.date()

    for symbol in context.stocks:
        signal_key = (current_date, symbol)
        if signal_key in context.signals:
            action = context.signals[signal_key]

            if action == 'BUY':
                order_percent(symbol, 1.0 / len(context.stocks))
            elif action == 'SELL':
                order_target_percent(symbol, 0)

config = {
    "base": {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "accounts": {"stock": 100000}
    }
}

result = run_func(config=config, init=init, handle_bar=handle_bar)
```

**Approach 2: Custom Mod Extension**

Create an RQAlpha mod that intercepts the execution layer:

```python
# rqalpha_mod_signal_loader/__init__.py
from rqalpha.interface import AbstractMod
from rqalpha.events import EVENT

class SignalLoaderMod(AbstractMod):
    def __init__(self):
        self.signals = None

    def start_up(self, env, mod_config):
        # Load signals from database
        self.signals = self.load_signals_from_db()

        # Hook into bar event
        env.event_bus.add_listener(EVENT.BAR, self.on_bar)

    def on_bar(self, event):
        current_date = event.bar_dict.dt
        # Inject signals into trading context
        for symbol, action in self.signals.get(current_date, {}).items():
            if action == 'BUY':
                order_percent(symbol, 0.1)
```

**Recommendation**: Neither approach is ideal. RQAlpha is designed for **strategy development**, not **signal evaluation**. For MyStocks use case, a custom vectorized backtester is more appropriate.

---

### 3. Extracting Performance Metrics Programmatically

#### RQAlpha Results Structure

When using `run_func()`, RQAlpha returns a comprehensive results dictionary:

```python
from rqalpha import run_func
import pickle

# Run backtest
result = run_func(config=config, init=init, handle_bar=handle_bar)

# Save to pickle for later analysis
with open('backtest_result.pkl', 'wb') as f:
    pickle.dump(result, f)

# Or access directly
print(result.keys())
# dict_keys(['summary', 'stock_portfolios', 'total_portfolios',
#            'benchmark_portfolios', 'trades', 'stock_positions'])
```

#### Available Metrics

**summary** dictionary contains:

```python
{
    # Returns
    'total_returns': 0.2534,              # Total return
    'annualized_returns': 0.1876,         # Annualized return
    'benchmark_total_returns': 0.1543,
    'benchmark_annualized_returns': 0.1234,

    # Risk Metrics
    'sharpe': 1.82,                       # Sharpe ratio
    'max_drawdown': 0.1234,               # Maximum drawdown
    'downside_risk': 0.0876,              # Downside deviation
    'tracking_error': 0.0543,             # Tracking error vs benchmark
    'information_ratio': 0.87,            # Information ratio

    # Greek Metrics
    'alpha': 0.0543,                      # Alpha vs benchmark
    'beta': 0.95,                         # Beta vs benchmark

    # Trade Statistics
    'win_rate': 0.56,                     # Win rate
    'profit_loss_ratio': 1.8,             # Average win/loss ratio
    'total_trades': 143,                  # Number of trades

    # Additional Metrics
    'volatility': 0.1543,                 # Annualized volatility
    'sortino': 2.14,                      # Sortino ratio
    'calmar': 1.52,                       # Calmar ratio
}
```

#### Programmatic Extraction for Database Storage

```python
def extract_backtest_metrics(result_dict, strategy_id, db_manager):
    """
    Extract RQAlpha metrics and save to MyStocks database
    """
    summary = result_dict['summary']

    # Prepare metrics for database insertion
    metrics_record = {
        'strategy_id': strategy_id,
        'backtest_date': datetime.now(),
        'start_date': result_dict['config']['base']['start_date'],
        'end_date': result_dict['config']['base']['end_date'],

        # Performance Metrics
        'total_return': summary['total_returns'],
        'annual_return': summary['annualized_returns'],
        'sharpe_ratio': summary['sharpe'],
        'sortino_ratio': summary.get('sortino', None),
        'max_drawdown': summary['max_drawdown'],
        'calmar_ratio': summary.get('calmar', None),

        # Risk Metrics
        'volatility': summary['volatility'],
        'downside_risk': summary['downside_risk'],
        'beta': summary['beta'],
        'alpha': summary['alpha'],

        # Trade Statistics
        'total_trades': summary['total_trades'],
        'win_rate': summary['win_rate'],
        'profit_loss_ratio': summary['profit_loss_ratio'],
    }

    # Insert into PostgreSQL (Derived Data tier)
    db_manager.save_data_by_classification(
        data=pd.DataFrame([metrics_record]),
        classification=DataClassification.DERIVED_DATA,
        table_name='backtest_metrics'
    )

    # Extract trade details
    trades_df = pd.DataFrame(result_dict['trades'])
    trades_df['strategy_id'] = strategy_id

    # Save trades to PostgreSQL
    db_manager.save_data_by_classification(
        data=trades_df,
        classification=DataClassification.DERIVED_DATA,
        table_name='backtest_trades'
    )

    return metrics_record
```

#### Command-Line Results Export

```bash
# Run with pickle output
rqalpha run -f strategy.py -s 2024-01-01 -e 2024-12-31 -o result.pkl

# Run with CSV report
rqalpha run -f strategy.py -s 2024-01-01 -e 2024-12-31 --report backtest_report
```

---

### 4. Common Integration Pitfalls

#### Data-Related Pitfalls

1. **Symbol Format Mismatch**
   - RQAlpha expects: `000001.XSHG` (Shanghai), `000001.XSHE` (Shenzhen)
   - MyStocks may use: `000001`, `SH000001`, or other formats
   - **Solution**: Create symbol mapping layer

2. **Trading Calendar Discrepancies**
   - RQAlpha strictly validates trading days
   - Missing calendar dates cause backtest to skip those days silently
   - **Solution**: Ensure MySQL trading_calendar table is comprehensive

3. **Data Completeness**
   - RQAlpha expects no data gaps for subscribed instruments
   - Missing bars cause KeyError or return None
   - **Solution**: Implement forward-fill logic in custom DataSource

4. **Timestamp Timezone Issues**
   - RQAlpha assumes China timezone (UTC+8)
   - Database timestamps must align
   - **Solution**: Standardize all timestamps to UTC+8 in MyStocks

#### Performance Pitfalls

5. **Database Query Performance**
   - Each `history_bars()` call queries database
   - Without caching, backtests are extremely slow (10-100x slower than bundle)
   - **Solution**: Implement aggressive caching layer or pre-load data into memory

6. **PostgreSQL Time-Series Queries**
   - Standard PostgreSQL struggles with large time-series range queries
   - **Solution**: Use TimescaleDB hypertables (already in MyStocks architecture)

#### Architecture Pitfalls

7. **Event-Driven vs Signal-Based Mismatch**
   - RQAlpha designed for strategies that generate signals in real-time
   - Pre-computed signals require workarounds that feel unnatural
   - **Solution**: Consider vectorized backtesting instead

8. **Bundle Update Overhead**
   - If using binary bundles, must regenerate whenever data updated
   - Incompatible with real-time data ingestion workflow
   - **Solution**: Use custom DataSource, not bundles

9. **Version Lock-In**
   - RQAlpha 4.x made breaking changes to bundle format and API
   - Upgrading requires code refactoring
   - **Solution**: Pin RQAlpha version and isolate in separate environment

10. **Limited Documentation**
    - Most documentation in Chinese
    - BaseDataSource interface poorly documented
    - Community support declining as Ricequant moved to enterprise model
    - **Solution**: Budget extra time for trial-and-error implementation

---

### 5. Alternative Frameworks Comparison

#### Framework Matrix

| Feature | RQAlpha | Backtrader | Zipline | VectorBT | Custom Vectorized |
|---------|---------|------------|---------|----------|-------------------|
| **Chinese Market Support** | ★★★★★ | ★★☆☆☆ | ★☆☆☆☆ | ★★☆☆☆ | ★★★★★ (We control it) |
| **Active Maintenance (2025)** | ★★★☆☆ | ★★★★☆ | ★☆☆☆☆ | ★★★★★ | ★★★★★ |
| **Custom Data Integration** | ★★★☆☆ | ★★★★☆ | ★★☆☆☆ | ★★★★★ | ★★★★★ |
| **Pre-Computed Signals** | ★★☆☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★★★★ | ★★★★★ |
| **Performance Speed** | ★★★☆☆ | ★★☆☆☆ | ★☆☆☆☆ | ★★★★★ | ★★★★★ |
| **Execution Realism** | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★☆☆☆ | ★★☆☆☆ |
| **Learning Curve** | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★★★ |
| **Documentation Quality** | ★★☆☆☆ | ★★★★☆ | ★★★☆☆ | ★★★★★ | N/A |

#### Detailed Comparison

**RQAlpha**
- ✅ Native Chinese market support (A-shares, futures)
- ✅ Realistic event-driven simulation
- ✅ Built-in risk management
- ❌ Declining community support (Ricequant went enterprise-only)
- ❌ Poor fit for pre-computed signals
- ❌ Bundle format restricts real-time updates
- **Best for**: Developing new strategies with event-driven logic

**Backtrader**
- ✅ Mature, actively maintained
- ✅ Excellent documentation and community
- ✅ Flexible architecture
- ✅ Supports live trading with multiple brokers
- ❌ Not optimized for Chinese markets
- ❌ Slower than vectorized approaches
- ❌ Requires custom data feeds for A-shares
- **Best for**: Live trading automation, complex order logic

**Zipline (Deprecated)**
- ❌ No longer maintained (last release 2020)
- ❌ Python 3.5-3.6 only (requires forks for modern Python)
- ❌ No Chinese market support
- ❌ Bundle update complexity
- ❌ Not recommended for new projects in 2025
- **Best for**: Nothing (use alternatives)

**VectorBT**
- ✅ Blazing fast (12-75x faster than event-driven)
- ✅ Perfect for pre-computed signals
- ✅ Massive parameter optimization capabilities
- ✅ Excellent documentation
- ✅ Works directly with pandas DataFrames
- ❌ Less realistic execution simulation
- ❌ No built-in Chinese market features
- ❌ Not suitable for complex order logic
- **Best for**: Signal-based strategy screening, parameter optimization

**Custom Vectorized Backtester**
- ✅ Complete control over implementation
- ✅ Direct integration with MyStocks databases
- ✅ Optimized for MyStocks workflow
- ✅ No external dependencies or version lock-in
- ✅ Natural fit for pre-computed signals
- ❌ Must implement metrics calculations ourselves
- ❌ Less realistic execution modeling
- ❌ Initial development effort required
- **Best for**: MyStocks use case (signal evaluation from existing data)

---

## Recommended Implementation Strategy

### Phase 1: Custom Vectorized Backtester (Recommended First)

Build a lightweight vectorized backtesting engine optimized for MyStocks:

```python
# /opt/claude/mystocks_spec/backtesting/vectorized_backtester.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class BacktestResult:
    """Backtest performance metrics"""
    total_return: float
    annual_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    win_rate: float
    total_trades: int

    equity_curve: pd.Series
    trades: pd.DataFrame

    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage"""
        return {
            'total_return': self.total_return,
            'annual_return': self.annual_return,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'max_drawdown': self.max_drawdown,
            'calmar_ratio': self.calmar_ratio,
            'win_rate': self.win_rate,
            'total_trades': self.total_trades,
        }


class VectorizedBacktester:
    """
    Vectorized backtesting engine for signal-based strategies

    Advantages:
    - 10-100x faster than event-driven for signal evaluation
    - Direct integration with PostgreSQL/TDengine data
    - No external dependencies or bundle formats
    - Natural fit for pre-computed signals
    """

    def __init__(self, data_manager, initial_capital: float = 100000):
        """
        Args:
            data_manager: MyStocksUnifiedManager instance
            initial_capital: Starting portfolio value
        """
        self.data_manager = data_manager
        self.initial_capital = initial_capital

    def load_price_data(self, symbols: List[str], start_date: str,
                       end_date: str) -> pd.DataFrame:
        """
        Load price data from PostgreSQL daily_bars table

        Returns: MultiIndex DataFrame (date, symbol) with OHLCV columns
        """
        query = """
            SELECT date, symbol, open, high, low, close, volume
            FROM daily_bars
            WHERE symbol IN %(symbols)s
              AND date BETWEEN %(start_date)s AND %(end_date)s
            ORDER BY date, symbol
        """

        df = self.data_manager.postgres_access.query_to_dataframe(
            query,
            {'symbols': tuple(symbols), 'start_date': start_date, 'end_date': end_date}
        )

        return df.set_index(['date', 'symbol'])

    def run_backtest(self, signals: pd.DataFrame, price_data: pd.DataFrame,
                     commission: float = 0.0003) -> BacktestResult:
        """
        Run vectorized backtest with pre-computed signals

        Args:
            signals: DataFrame with columns [date, symbol, action]
                     action in ['BUY', 'SELL', 'HOLD']
            price_data: MultiIndex DataFrame (date, symbol) with price data
            commission: Commission rate (default 0.03%)

        Returns: BacktestResult with performance metrics
        """
        # Align signals and prices
        signals_pivot = signals.pivot(index='date', columns='symbol', values='action')
        prices = price_data['close'].unstack('symbol')

        # Calculate positions (1 = long, 0 = flat)
        positions = (signals_pivot == 'BUY').astype(int)
        positions = positions.reindex(prices.index).fillna(method='ffill').fillna(0)

        # Calculate position changes (trades)
        trades = positions.diff().fillna(positions.iloc[0])

        # Calculate returns
        returns = prices.pct_change()

        # Strategy returns (position * return)
        strategy_returns = (positions.shift(1) * returns).sum(axis=1)

        # Apply commission on trades
        commission_costs = trades.abs().sum(axis=1) * commission
        strategy_returns = strategy_returns - commission_costs

        # Calculate equity curve
        equity_curve = (1 + strategy_returns).cumprod() * self.initial_capital

        # Calculate metrics
        total_return = (equity_curve.iloc[-1] / self.initial_capital) - 1
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        annual_return = (1 + total_return) ** (365 / days) - 1

        sharpe = self._calculate_sharpe(strategy_returns)
        sortino = self._calculate_sortino(strategy_returns)
        max_dd = self._calculate_max_drawdown(equity_curve)
        calmar = annual_return / max_dd if max_dd != 0 else np.nan

        # Trade statistics
        trade_list = self._extract_trades(trades, prices, signals)
        win_rate = (trade_list['pnl'] > 0).mean() if len(trade_list) > 0 else 0

        return BacktestResult(
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown=max_dd,
            calmar_ratio=calmar,
            win_rate=win_rate,
            total_trades=len(trade_list),
            equity_curve=equity_curve,
            trades=trade_list
        )

    def _calculate_sharpe(self, returns: pd.Series, risk_free_rate: float = 0.03) -> float:
        """Calculate annualized Sharpe ratio"""
        excess_returns = returns - risk_free_rate / 252
        if excess_returns.std() == 0:
            return 0
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    def _calculate_sortino(self, returns: pd.Series, risk_free_rate: float = 0.03) -> float:
        """Calculate annualized Sortino ratio"""
        excess_returns = returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        if downside_returns.std() == 0:
            return 0
        return np.sqrt(252) * excess_returns.mean() / downside_returns.std()

    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown"""
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max
        return abs(drawdown.min())

    def _extract_trades(self, trades: pd.DataFrame, prices: pd.DataFrame,
                       signals: pd.DataFrame) -> pd.DataFrame:
        """Extract individual trade details for analysis"""
        trade_list = []

        for symbol in trades.columns:
            symbol_trades = trades[symbol]
            buys = symbol_trades[symbol_trades > 0]
            sells = symbol_trades[symbol_trades < 0]

            for buy_date in buys.index:
                # Find next sell
                future_sells = sells[sells.index > buy_date]
                if len(future_sells) > 0:
                    sell_date = future_sells.index[0]
                    buy_price = prices.loc[buy_date, symbol]
                    sell_price = prices.loc[sell_date, symbol]
                    pnl = (sell_price - buy_price) / buy_price

                    trade_list.append({
                        'symbol': symbol,
                        'entry_date': buy_date,
                        'exit_date': sell_date,
                        'entry_price': buy_price,
                        'exit_price': sell_price,
                        'pnl': pnl,
                        'duration': (sell_date - buy_date).days
                    })

        return pd.DataFrame(trade_list)

    def save_results_to_database(self, result: BacktestResult, strategy_id: str):
        """Save backtest results to PostgreSQL"""
        # Save summary metrics
        metrics_df = pd.DataFrame([{
            'strategy_id': strategy_id,
            'backtest_date': pd.Timestamp.now(),
            **result.to_dict()
        }])

        self.data_manager.save_data_by_classification(
            data=metrics_df,
            classification=DataClassification.DERIVED_DATA,
            table_name='backtest_metrics'
        )

        # Save trade details
        if len(result.trades) > 0:
            result.trades['strategy_id'] = strategy_id
            self.data_manager.save_data_by_classification(
                data=result.trades,
                classification=DataClassification.DERIVED_DATA,
                table_name='backtest_trades'
            )
```

**Usage Example**:

```python
from backtesting.vectorized_backtester import VectorizedBacktester
from unified_manager import MyStocksUnifiedManager

# Initialize
manager = MyStocksUnifiedManager()
backtester = VectorizedBacktester(manager, initial_capital=100000)

# Load pre-computed signals from database or CSV
signals = pd.read_csv('strategy_signals.csv')
# signals columns: [date, symbol, action]

# Load price data
symbols = signals['symbol'].unique().tolist()
price_data = backtester.load_price_data(
    symbols=symbols,
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# Run backtest
result = backtester.run_backtest(signals, price_data, commission=0.0003)

# Display results
print(f"Total Return: {result.total_return:.2%}")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
print(f"Max Drawdown: {result.max_drawdown:.2%}")
print(f"Win Rate: {result.win_rate:.2%}")

# Save to database
backtester.save_results_to_database(result, strategy_id='momentum_v1')
```

### Phase 2: Optional RQAlpha Integration (Future Enhancement)

If more realistic execution simulation is needed later:

1. **Install RQAlpha**:
   ```bash
   pip install rqalpha
   ```

2. **Create Custom DataSource Mod**:
   ```bash
   mkdir -p rqalpha_mod_mystocks_data
   # Implement BaseDataSource as shown in Section 1
   ```

3. **Use for Top-Performing Strategies Only**:
   - Screen 100s of strategies with vectorized backtester
   - Validate top 10 with RQAlpha for realistic execution
   - Compare results to understand vectorized approximation error

---

## Code Patterns Summary

### Pattern 1: Direct PostgreSQL/TDengine Integration (Recommended)

```python
# Vectorized approach - works directly with MyStocks data
class VectorizedBacktester:
    def load_data_from_postgres(self, symbols, start, end):
        query = "SELECT * FROM daily_bars WHERE ..."
        return self.postgres_access.query_to_dataframe(query)

    def run_backtest(self, signals, price_data):
        # Vectorized calculation using pandas/numpy
        positions = self.calculate_positions(signals)
        returns = self.calculate_returns(positions, price_data)
        metrics = self.calculate_metrics(returns)
        return metrics
```

### Pattern 2: RQAlpha Custom DataSource (If Event-Driven Needed)

```python
# Event-driven approach - wraps MyStocks data for RQAlpha
class MyStocksDataSource(BaseDataSource):
    def history_bars(self, symbol, bar_count, frequency, fields, dt):
        # Query from PostgreSQL/TDengine
        # Cache aggressively to avoid performance issues
        return self._query_with_cache(symbol, bar_count, dt)
```

### Pattern 3: Hybrid Approach (Best of Both Worlds)

```python
# Use vectorized for screening, RQAlpha for validation
def evaluate_strategy(signals, strategy_id):
    # Phase 1: Quick screening with vectorized
    vbt_result = vectorized_backtester.run_backtest(signals, price_data)

    if vbt_result.sharpe_ratio > 1.5:  # Promising strategy
        # Phase 2: Validate with event-driven simulation
        rqa_result = rqalpha_backtester.run_backtest(strategy_config)

        # Compare results
        execution_slippage = vbt_result.total_return - rqa_result.total_return
        logger.info(f"Vectorized approximation error: {execution_slippage:.2%}")

    return vbt_result
```

---

## Alternative Frameworks Worth Considering

### VectorBT (Highly Recommended as Alternative)

If you prefer a mature library over custom implementation:

```python
import vectorbt as vbt
import pandas as pd

# Load data from MyStocks
price_data = load_from_postgres(symbols, start_date, end_date)

# Define signals from pre-computed data
entries = signals['action'] == 'BUY'
exits = signals['action'] == 'SELL'

# Run backtest
portfolio = vbt.Portfolio.from_signals(
    price_data['close'],
    entries,
    exits,
    init_cash=100000,
    fees=0.0003
)

# Extract metrics
print(f"Total Return: {portfolio.total_return()}")
print(f"Sharpe Ratio: {portfolio.sharpe_ratio()}")
print(f"Max Drawdown: {portfolio.max_drawdown()}")

# Save to database
metrics = {
    'total_return': portfolio.total_return(),
    'sharpe': portfolio.sharpe_ratio(),
    'max_dd': portfolio.max_drawdown(),
    # ... more metrics
}
save_to_database(metrics, 'strategy_v1')
```

**Pros**:
- 10-100x faster than RQAlpha
- Perfect for pre-computed signals
- Excellent documentation
- Active development

**Cons**:
- Requires `vectorbt` dependency
- Less realistic execution simulation

### Qlib (Microsoft - Advanced ML Focus)

If machine learning strategy development is future goal:

```python
from qlib.backtest import backtest
from qlib.contrib.strategy import TopkDropoutStrategy

# Qlib is more complex but offers:
# - ML model integration
# - Factor library
# - Advanced portfolio optimization
# - Production-ready infrastructure
```

**Pros**:
- Enterprise-grade
- ML/AI focused
- Excellent for factor research

**Cons**:
- Steeper learning curve
- Heavier infrastructure requirements
- Overkill for simple signal backtesting

---

## Final Recommendations

### For MyStocks Integration: Implement Custom Vectorized Backtester

**Reasons**:
1. ✅ **Perfect fit**: Pre-computed signals are natural for vectorized approach
2. ✅ **Performance**: 10-100x faster than event-driven for signal evaluation
3. ✅ **Integration**: Direct PostgreSQL/TDengine access, no bundle conversion
4. ✅ **Control**: Full control over metrics calculation and database storage
5. ✅ **Simplicity**: ~200 lines of code vs complex RQAlpha setup
6. ✅ **Maintenance**: No external dependencies to version-lock or break

**Development Effort**:
- 2-3 days for basic implementation
- 1-2 days for database integration and testing
- Total: ~1 week

**Alternative**: If you prefer not to build custom, use **VectorBT** library (similar benefits, mature codebase)

### When to Consider RQAlpha

Only add RQAlpha integration if:
1. ❗ You need realistic execution simulation (partial fills, slippage modeling)
2. ❗ You plan to develop new event-driven strategies (not just evaluate signals)
3. ❗ You need to validate vectorized results against event-driven baseline

**Development Effort**:
- 3-5 days for BaseDataSource implementation
- 2-3 days for caching layer (required for acceptable performance)
- 1-2 days for integration testing
- Total: ~2 weeks

### Hybrid Approach (Recommended for Production)

1. **Phase 1** (Week 1): Implement vectorized backtester for fast signal evaluation
2. **Phase 2** (Week 2-3): Add database tables for backtest results storage
3. **Phase 3** (Week 4): Integration with strategy generation pipeline
4. **Phase 4** (Optional, Future): Add RQAlpha for top-performing strategy validation

---

## Appendix: Database Schema for Backtest Results

```sql
-- PostgreSQL schema for backtest metrics (Derived Data tier)

CREATE TABLE backtest_metrics (
    id SERIAL PRIMARY KEY,
    strategy_id VARCHAR(100) NOT NULL,
    backtest_date TIMESTAMP NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    -- Performance Metrics
    total_return DECIMAL(10, 6),
    annual_return DECIMAL(10, 6),
    sharpe_ratio DECIMAL(10, 4),
    sortino_ratio DECIMAL(10, 4),
    calmar_ratio DECIMAL(10, 4),

    -- Risk Metrics
    max_drawdown DECIMAL(10, 6),
    volatility DECIMAL(10, 6),
    downside_risk DECIMAL(10, 6),

    -- Trade Statistics
    total_trades INTEGER,
    win_rate DECIMAL(5, 4),
    avg_trade_return DECIMAL(10, 6),

    -- Configuration
    initial_capital DECIMAL(15, 2),
    commission_rate DECIMAL(6, 5),

    -- Metadata
    framework VARCHAR(50),  -- 'vectorized', 'rqalpha', 'vectorbt'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_strategy_date (strategy_id, backtest_date),
    INDEX idx_sharpe (sharpe_ratio DESC)
);

CREATE TABLE backtest_trades (
    id SERIAL PRIMARY KEY,
    strategy_id VARCHAR(100) NOT NULL,
    backtest_id INTEGER REFERENCES backtest_metrics(id),

    symbol VARCHAR(20) NOT NULL,
    entry_date DATE NOT NULL,
    exit_date DATE,
    entry_price DECIMAL(10, 4),
    exit_price DECIMAL(10, 4),
    quantity INTEGER,

    pnl DECIMAL(10, 6),
    pnl_percent DECIMAL(10, 6),
    duration_days INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_strategy (strategy_id),
    INDEX idx_symbol_date (symbol, entry_date)
);

-- TimescaleDB: Convert to hypertable for time-series optimization
SELECT create_hypertable('backtest_trades', 'entry_date');
```

---

## References and Resources

### RQAlpha Resources
- **GitHub**: https://github.com/ricequant/rqalpha
- **Documentation** (Chinese): https://rqalpha.readthedocs.io/
- **Code Examples**: https://www.programcreek.com/python/example/117541/rqalpha.data.base_data_source.BaseDataSource

### VectorBT Resources
- **Website**: https://vectorbt.dev/
- **GitHub**: https://github.com/polakowo/vectorbt
- **Documentation**: Excellent English documentation with examples

### General Backtesting Resources
- **Comparison Article**: "Battle-Tested Backtesters: Comparing VectorBT, Zipline, and Backtrader"
- **Speed Comparison**: "Why Backtests Run Fast or Slow" (QuantRocket blog)
- **Vectorized vs Event-Driven**: https://www.marketcalls.in/system-trading/comparision-of-event-driven-backtesting-vs-vectorized-backtesting.html

---

**Document Status**: Research Complete
**Next Steps**: Review findings with team, decide on implementation approach
**Estimated Implementation**: 1 week (vectorized) or 2 weeks (RQAlpha + vectorized)
