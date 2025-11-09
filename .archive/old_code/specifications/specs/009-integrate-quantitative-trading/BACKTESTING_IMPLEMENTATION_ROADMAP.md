# Backtesting Implementation Roadmap

**Feature**: User Story 3 - Strategy Backtesting (Priority P3)
**Date**: 2025-10-18
**Status**: Research Complete - Implementation Plan

---

## Overview

This roadmap translates the RQAlpha integration research into a concrete implementation plan that fulfills the backtesting requirements defined in `spec.md` (FR-013 through FR-018).

---

## Implementation Decision

### Chosen Approach: **Hybrid Vectorized + Optional RQAlpha**

**Phase 1**: Build custom vectorized backtesting engine (Primary)
**Phase 2**: Add optional RQAlpha integration for validation (Future enhancement)

**Rationale**:
- Meets FR-015 performance requirement (3 years in <2 minutes)
- Natural fit for pre-computed strategy signals from User Story 2
- Direct integration with existing MyStocks data infrastructure
- Aligns with FR-017 (store results in PostgreSQL as derived data)

---

## Requirements Mapping

### How This Implementation Satisfies Functional Requirements

| Requirement | Implementation Approach | Technical Details |
|-------------|------------------------|-------------------|
| **FR-013**: Integrate backtesting engine | Custom vectorized engine + optional RQAlpha | `VectorizedBacktester` class in `/backtesting/` module |
| **FR-014**: Calculate performance metrics | Implement standard formulas in Python | Sharpe, Sortino, drawdown, win rate, profit factor |
| **FR-015**: Account for transaction costs | Configurable commission/slippage parameters | Default: 0.03% commission, 0.05% slippage |
| **FR-016**: Handle edge cases | Suspension detection, limit-up/down filtering | Check for consecutive missing data, validate price limits |
| **FR-017**: Store results in PostgreSQL | Use existing `DataClassification.DERIVED_DATA` | Tables: `backtest_metrics`, `backtest_trades` |
| **FR-018**: Generate trade-by-trade history | Extract individual trades from position changes | DataFrame with entry/exit dates, prices, P&L |

---

## Implementation Timeline

### Week 1: Core Vectorized Backtester

**Day 1-2: VectorizedBacktester Class**
```python
# File: /opt/claude/mystocks_spec/backtesting/vectorized_backtester.py

Tasks:
- Implement position calculation from signals
- Calculate returns with commission/slippage
- Generate equity curve
- Extract trade-by-trade details
```

**Day 3: Performance Metrics Calculation**
```python
# Add metrics methods to VectorizedBacktester

Tasks:
- Sharpe ratio (annualized)
- Sortino ratio (downside deviation)
- Maximum drawdown
- Calmar ratio
- Win rate and profit factor
```

**Day 4: Database Integration**
```python
# Connect to MyStocks unified manager

Tasks:
- Load price data from PostgreSQL daily_bars
- Save metrics to backtest_metrics table
- Save trades to backtest_trades table
- Use existing DataClassification framework
```

**Day 5: Testing and Documentation**
```
Tasks:
- Unit tests for metric calculations
- Integration test with real stock data
- Usage documentation with examples
- Performance validation (meet <2 min requirement)
```

---

### Week 2: API and Frontend Integration

**Day 1-2: RESTful API Endpoints**
```python
# File: /opt/claude/mystocks_spec/web/api/backtest_routes.py

Endpoints:
- POST /api/backtest/run
  {
    "strategy_id": "momentum_v1",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 100000,
    "commission": 0.0003
  }

- GET /api/backtest/results/{backtest_id}
  Returns: metrics, trades, equity_curve

- GET /api/backtest/compare
  Compare multiple backtests side-by-side
```

**Day 3: Vue.js Components**
```vue
<!-- File: /opt/claude/mystocks_spec/web/components/BacktestViewer.vue -->

Components:
- BacktestConfiguration.vue (input form)
- MetricsDisplay.vue (performance metrics cards)
- EquityCurve.vue (ECharts line chart)
- TradeHistory.vue (data table with filters)
```

**Day 4-5: Integration with User Story 2**
```
Tasks:
- Connect to strategy signal output
- Automatic signal format conversion
- Backtest button in strategy results page
- Store backtest_id reference in strategy_signal table
```

---

### Week 3 (Optional): RQAlpha Integration for Validation

**Only implement if realistic execution simulation is critical**

**Day 1-2: Custom DataSource**
```python
# File: /opt/claude/mystocks_spec/backtesting/rqalpha_integration/mystocks_datasource.py

class MyStocksDataSource(BaseDataSource):
    def __init__(self, unified_manager):
        # Use existing PostgreSQL/TDengine access

    def history_bars(self, symbol, count, frequency, fields, dt):
        # Query with caching layer for performance
```

**Day 3-4: Signal Injection Strategy**
```python
# File: /opt/claude/mystocks_spec/backtesting/rqalpha_integration/signal_strategy.py

def init(context):
    context.signals = load_precomputed_signals(strategy_id)

def handle_bar(context, bar_dict):
    # Lookup signal for current date
    # Execute trades based on signals
```

**Day 5: Validation and Comparison**
```python
# Compare vectorized vs RQAlpha results
# Document execution slippage difference
# Calibrate vectorized assumptions
```

---

## Database Schema Implementation

### PostgreSQL Tables (Derived Data Tier)

```sql
-- Create tables for backtest results
-- Location: /opt/claude/mystocks_spec/db_manager/migrations/009_backtest_tables.sql

CREATE TABLE backtest_metrics (
    id SERIAL PRIMARY KEY,
    strategy_id VARCHAR(100) NOT NULL,
    backtest_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Configuration
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15, 2) NOT NULL,
    commission_rate DECIMAL(6, 5) DEFAULT 0.0003,
    slippage_rate DECIMAL(6, 5) DEFAULT 0.0005,

    -- Performance Metrics (FR-014)
    total_return DECIMAL(10, 6),
    annual_return DECIMAL(10, 6),
    sharpe_ratio DECIMAL(10, 4),
    sortino_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 6),
    calmar_ratio DECIMAL(10, 4),

    -- Trade Statistics
    total_trades INTEGER,
    win_rate DECIMAL(5, 4),
    profit_factor DECIMAL(10, 4),
    avg_win DECIMAL(10, 6),
    avg_loss DECIMAL(10, 6),

    -- Additional Metrics
    volatility DECIMAL(10, 6),
    downside_risk DECIMAL(10, 6),
    best_trade DECIMAL(10, 6),
    worst_trade DECIMAL(10, 6),
    avg_holding_days DECIMAL(8, 2),

    -- Framework metadata
    framework VARCHAR(50) DEFAULT 'vectorized',
    version VARCHAR(20),

    -- Indexes for performance
    INDEX idx_strategy_date (strategy_id, backtest_date),
    INDEX idx_sharpe (sharpe_ratio DESC),
    INDEX idx_return (annual_return DESC)
);

CREATE TABLE backtest_trades (
    id SERIAL PRIMARY KEY,
    backtest_id INTEGER NOT NULL REFERENCES backtest_metrics(id) ON DELETE CASCADE,
    strategy_id VARCHAR(100) NOT NULL,

    -- Trade details (FR-018)
    symbol VARCHAR(20) NOT NULL,
    entry_date DATE NOT NULL,
    exit_date DATE,
    entry_price DECIMAL(10, 4),
    exit_price DECIMAL(10, 4),
    quantity INTEGER,

    -- P&L breakdown
    gross_pnl DECIMAL(12, 4),
    commission DECIMAL(12, 4),
    slippage DECIMAL(12, 4),
    net_pnl DECIMAL(12, 4),
    pnl_percent DECIMAL(10, 6),

    -- Additional info
    duration_days INTEGER,
    exit_reason VARCHAR(50),  -- 'signal', 'suspension', 'forced'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_backtest (backtest_id),
    INDEX idx_strategy (strategy_id),
    INDEX idx_symbol_date (symbol, entry_date),
    INDEX idx_pnl (net_pnl DESC)
);

-- TimescaleDB optimization for time-series queries
SELECT create_hypertable('backtest_trades', 'entry_date');

-- Create view for quick performance overview
CREATE VIEW backtest_performance_summary AS
SELECT
    strategy_id,
    COUNT(*) as backtest_count,
    AVG(annual_return) as avg_annual_return,
    AVG(sharpe_ratio) as avg_sharpe,
    MAX(max_drawdown) as worst_drawdown,
    MAX(backtest_date) as last_backtest
FROM backtest_metrics
GROUP BY strategy_id;
```

---

## Code Structure

```
/opt/claude/mystocks_spec/
├── backtesting/
│   ├── __init__.py
│   ├── vectorized_backtester.py          # Core engine (Week 1)
│   ├── metrics_calculator.py             # Performance metrics
│   ├── trade_extractor.py                # Trade-by-trade analysis
│   ├── edge_case_handler.py              # Suspensions, delistings (FR-016)
│   │
│   ├── rqalpha_integration/              # Optional (Week 3)
│   │   ├── __init__.py
│   │   ├── mystocks_datasource.py
│   │   ├── signal_strategy.py
│   │   └── config_builder.py
│   │
│   └── tests/
│       ├── test_vectorized_backtester.py
│       ├── test_metrics_accuracy.py
│       └── test_edge_cases.py
│
├── web/
│   ├── api/
│   │   └── backtest_routes.py            # RESTful API (Week 2)
│   │
│   └── frontend/
│       └── components/
│           ├── BacktestConfiguration.vue
│           ├── MetricsDisplay.vue
│           ├── EquityCurve.vue
│           └── TradeHistory.vue
│
├── db_manager/
│   └── migrations/
│       └── 009_backtest_tables.sql       # Database schema
│
└── docs/
    └── backtesting/
        ├── user_guide.md
        ├── api_reference.md
        └── metrics_definitions.md
```

---

## Integration Points with Existing MyStocks Components

### 1. Data Access Layer
```python
# Use existing unified manager for data loading
from unified_manager import MyStocksUnifiedManager

manager = MyStocksUnifiedManager()

# Load price data from PostgreSQL (Derived Data tier)
price_data = manager.load_data_by_classification(
    classification=DataClassification.DERIVED_DATA,
    table_name='daily_bars',
    filters={'symbol': symbol, 'date_range': (start, end)}
)
```

### 2. Strategy Signal Integration
```python
# Connect to User Story 2 output
from screening.strategy_executor import StrategySignalLoader

signals = StrategySignalLoader.load_signals(strategy_id)
# signals DataFrame: [date, symbol, action]

# Pass to backtester
result = backtester.run_backtest(signals, price_data)
```

### 3. Monitoring Integration
```python
# Use existing monitoring infrastructure
from monitoring.performance_monitor import PerformanceMonitor

@PerformanceMonitor.track_operation('backtest_execution')
def run_backtest(signals, price_data):
    # Automatic logging to monitoring database
    pass
```

### 4. Task Scheduling
```python
# Use existing Celery infrastructure for automated backtests
from celery import shared_task

@shared_task
def scheduled_backtest(strategy_id):
    """
    Automated backtesting task triggered by schedule
    Integrates with existing task queue
    """
    pass
```

---

## Performance Validation Plan

### Meeting FR-015 Requirement: 3 years data in <2 minutes

**Test Configuration**:
- Historical data: 2021-01-01 to 2023-12-31
- Strategy: Simple MA crossover generating ~100 trades
- Stock universe: 1 stock (baseline), then 10 stocks (parallel processing)

**Expected Performance**:
```
Single stock:
- Load data from PostgreSQL: 2 seconds
- Calculate positions: 0.5 seconds
- Calculate returns: 0.3 seconds
- Extract trades: 1 second
- Calculate metrics: 0.2 seconds
Total: ~4 seconds (well under 2 minutes)

10 stocks parallel:
- Load data: 5 seconds
- Vectorized calculation: 2 seconds
- Trade extraction: 8 seconds
Total: ~15 seconds (still under 2 minutes)
```

**Optimization Strategies**:
1. Use TimescaleDB chunk pruning for fast range queries
2. Cache indicator calculations if reused across backtests
3. Parallelize trade extraction across symbols
4. Use NumPy vectorized operations instead of loops

---

## Edge Case Handling (FR-016)

### Stock Suspensions
```python
def handle_suspension(self, price_data, max_suspension_days=5):
    """
    Detect suspensions (missing price data for consecutive days)
    Auto-exit positions after max_suspension_days
    """
    is_suspended = price_data.isnull()
    consecutive_suspensions = (
        is_suspended
        .groupby((is_suspended != is_suspended.shift()).cumsum())
        .cumsum()
    )

    # Force exit when suspension exceeds threshold
    force_exit = consecutive_suspensions > max_suspension_days
    return force_exit
```

### Limit Up/Down Detection
```python
def detect_limit_moves(self, price_data, limit_pct=0.10):
    """
    Detect limit-up/down days (10% for main board, 20% for ChiNext)
    Mark trades as potentially unfillable
    """
    daily_returns = price_data.pct_change()
    limit_up = daily_returns >= limit_pct
    limit_down = daily_returns <= -limit_pct

    return limit_up, limit_down
```

### Delisting Handling
```python
def handle_delisting(self, symbol, price_data):
    """
    Check for delisting events
    Force exit all positions at last available price
    """
    last_trade_date = price_data.index[-1]

    # Query reference data for delisting status
    delisting_info = self.get_delisting_info(symbol)

    if delisting_info and delisting_info.date <= last_trade_date:
        return True, delisting_info.date, delisting_info.final_price

    return False, None, None
```

---

## Success Criteria Validation

### How Implementation Satisfies Success Criteria

| Success Criterion | Validation Method | Expected Result |
|-------------------|-------------------|-----------------|
| **SC-003**: 3 years in <2 min | Performance test with timer | <2 min for 100 trades |
| **SC-009**: 95% accuracy vs manual | Compare against Excel calculations | <0.1% difference |
| **SC-010**: 20 concurrent users | Load test with pytest-benchmark | No degradation |

### Test Cases

```python
# tests/test_backtester_accuracy.py

def test_sharpe_ratio_accuracy():
    """
    Verify Sharpe ratio matches manual calculation
    Tolerance: 0.001 (0.1%)
    """
    result = backtester.run_backtest(test_signals, test_data)
    manual_sharpe = calculate_sharpe_manually(test_data)

    assert abs(result.sharpe_ratio - manual_sharpe) < 0.001

def test_max_drawdown_accuracy():
    """
    Verify max drawdown matches manual calculation
    Tolerance: 0.0001 (0.01%)
    """
    result = backtester.run_backtest(test_signals, test_data)
    manual_dd = calculate_drawdown_manually(equity_curve)

    assert abs(result.max_drawdown - manual_dd) < 0.0001

def test_commission_accuracy():
    """
    Verify commission calculation is correct
    Test: 10 trades with 0.03% commission
    """
    result = backtester.run_backtest(test_signals, test_data, commission=0.0003)
    expected_commission = calculate_expected_commission(test_signals)

    assert abs(result.total_commission - expected_commission) < 0.01
```

---

## API Specification

### POST /api/backtest/run

**Request**:
```json
{
  "strategy_id": "momentum_v1",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000,
  "commission_rate": 0.0003,
  "slippage_rate": 0.0005,
  "benchmark": "000300.XSHG"
}
```

**Response**:
```json
{
  "backtest_id": 12345,
  "status": "completed",
  "execution_time": "3.2s",
  "metrics": {
    "total_return": 0.2534,
    "annual_return": 0.2534,
    "sharpe_ratio": 1.82,
    "sortino_ratio": 2.14,
    "max_drawdown": 0.1234,
    "calmar_ratio": 2.06,
    "total_trades": 43,
    "win_rate": 0.5814
  },
  "equity_curve": [
    {"date": "2024-01-01", "value": 100000},
    {"date": "2024-01-02", "value": 100523},
    ...
  ],
  "trade_summary": {
    "total_trades": 43,
    "winning_trades": 25,
    "losing_trades": 18,
    "avg_win": 0.0543,
    "avg_loss": -0.0234
  }
}
```

### GET /api/backtest/results/{backtest_id}

**Response**: Same as POST response above

### GET /api/backtest/trades/{backtest_id}

**Response**:
```json
{
  "backtest_id": 12345,
  "trades": [
    {
      "id": 1,
      "symbol": "000001.XSHE",
      "entry_date": "2024-01-05",
      "entry_price": 12.34,
      "exit_date": "2024-01-15",
      "exit_price": 13.45,
      "quantity": 1000,
      "gross_pnl": 1110.00,
      "commission": 7.41,
      "net_pnl": 1102.59,
      "pnl_percent": 0.0899,
      "duration_days": 10,
      "exit_reason": "signal"
    },
    ...
  ],
  "total_count": 43
}
```

---

## Frontend Components Specification

### BacktestConfiguration.vue

```vue
<template>
  <el-form :model="config" label-width="120px">
    <el-form-item label="Strategy">
      <el-select v-model="config.strategy_id">
        <el-option v-for="s in strategies" :value="s.id" :label="s.name"/>
      </el-select>
    </el-form-item>

    <el-form-item label="Date Range">
      <el-date-picker v-model="config.dateRange" type="daterange"/>
    </el-form-item>

    <el-form-item label="Initial Capital">
      <el-input-number v-model="config.initial_capital" :min="10000"/>
    </el-form-item>

    <el-form-item label="Commission">
      <el-input-number v-model="config.commission_rate" :step="0.0001" :precision="4"/>
    </el-form-item>

    <el-button type="primary" @click="runBacktest">Run Backtest</el-button>
  </el-form>
</template>
```

### MetricsDisplay.vue

```vue
<template>
  <el-row :gutter="20">
    <el-col :span="6">
      <el-statistic title="Total Return" :value="metrics.total_return" :precision="2" suffix="%"/>
    </el-col>
    <el-col :span="6">
      <el-statistic title="Sharpe Ratio" :value="metrics.sharpe_ratio" :precision="2"/>
    </el-col>
    <el-col :span="6">
      <el-statistic title="Max Drawdown" :value="metrics.max_drawdown" :precision="2" suffix="%"/>
    </el-col>
    <el-col :span="6">
      <el-statistic title="Win Rate" :value="metrics.win_rate" :precision="2" suffix="%"/>
    </el-col>
  </el-row>
</template>
```

### EquityCurve.vue

```vue
<template>
  <div ref="chartContainer" style="width: 100%; height: 400px;"></div>
</template>

<script setup>
import * as echarts from 'echarts';

const initChart = () => {
  const chart = echarts.init(chartContainer.value);

  chart.setOption({
    title: { text: 'Equity Curve' },
    xAxis: { type: 'time' },
    yAxis: { type: 'value' },
    series: [
      {
        name: 'Portfolio Value',
        type: 'line',
        data: equityCurve.value,
        smooth: true
      },
      {
        name: 'Benchmark',
        type: 'line',
        data: benchmarkCurve.value,
        lineStyle: { type: 'dashed' }
      }
    ],
    tooltip: { trigger: 'axis' }
  });
};
</script>
```

---

## Documentation Deliverables

### 1. User Guide (`docs/backtesting/user_guide.md`)

**Contents**:
- Quick start: Running your first backtest
- Understanding performance metrics
- Interpreting results
- Common pitfalls and best practices
- Edge case handling

### 2. API Reference (`docs/backtesting/api_reference.md`)

**Contents**:
- Endpoint specifications
- Request/response schemas
- Authentication requirements
- Rate limits and quotas
- Error codes and troubleshooting

### 3. Metrics Definitions (`docs/backtesting/metrics_definitions.md`)

**Contents**:
- Sharpe ratio formula and interpretation
- Sortino ratio vs Sharpe ratio
- Maximum drawdown calculation
- Win rate and profit factor
- When to use which metric

---

## Rollout Plan

### Phase 1: Alpha Testing (Week 1-2)
- Internal testing with 5 pre-defined strategies
- Validate against manual Excel calculations
- Performance benchmarking
- Bug fixes and optimization

### Phase 2: Beta Testing (Week 3)
- Release to 10 power users
- Collect feedback on UI/UX
- Validate edge case handling
- Documentation refinement

### Phase 3: Production Release (Week 4)
- Gradual rollout to all users
- Monitor performance and errors
- Support documentation and training materials
- Announce in release notes

---

## Maintenance and Future Enhancements

### Immediate Post-Launch
- Monitor backtest execution times
- Track metric calculation accuracy
- Collect user feedback on missing features

### Future Enhancements (Post-P3)
1. **Parameter Optimization**: Grid search for optimal indicator parameters
2. **Walk-Forward Analysis**: Rolling window backtests for robustness testing
3. **Monte Carlo Simulation**: Stress testing with randomized scenarios
4. **RQAlpha Integration**: Add event-driven validation for top strategies
5. **Multi-Strategy Portfolios**: Combine multiple strategies with allocation weights

---

## Risk Mitigation

### Technical Risks

**Risk**: Backtest results differ from manual calculations
- **Mitigation**: Comprehensive unit tests, manual validation for test cases
- **Validation**: SC-009 requires 95% accuracy within 0.1%

**Risk**: Performance degradation with large datasets
- **Mitigation**: Implement caching, parallel processing, TimescaleDB optimization
- **Validation**: SC-003 requires <2 minutes for 3 years

**Risk**: Edge cases cause backtest failures
- **Mitigation**: Robust error handling, clear user messages, graceful degradation
- **Validation**: Test suite covering suspensions, delistings, limit moves

### User Experience Risks

**Risk**: Users misinterpret backtest results
- **Mitigation**: Prominent disclaimers, educational tooltips, metric definitions
- **Documentation**: Comprehensive user guide with best practices

**Risk**: Unrealistic expectations from backtests
- **Mitigation**: Display conservative slippage/commission assumptions, show statistical significance
- **UI Enhancement**: Warning badges for strategies with <100 trades or <1 year data

---

## Dependencies and Blockers

### Prerequisites
- ✅ User Story 2 (Strategy Screening) must be complete to provide signal input
- ✅ PostgreSQL daily_bars table populated with historical data
- ✅ Trading calendar table accurate for date range calculations

### External Dependencies
- **RQAlpha** (optional Phase 2): Version 4.5+ compatible with Python 3.10+
- **NumPy/Pandas**: Already installed, no issues
- **TimescaleDB**: Already configured, ready for hypertables

### No Blockers Identified
All required infrastructure exists in MyStocks. Implementation can start immediately.

---

## Summary

**Recommended Implementation**: Custom Vectorized Backtester
**Timeline**: 2-3 weeks (3 weeks if adding RQAlpha)
**Effort**: Medium complexity, high value
**Risk**: Low - proven approach with clear requirements

**Next Steps**:
1. Review and approve this roadmap
2. Create feature branch `009-integrate-backtesting`
3. Begin Week 1 implementation: VectorizedBacktester class
4. Set up database tables
5. Implement API endpoints
6. Build frontend components

---

**References**:
- Research Document: `/specs/009-integrate-quantitative-trading/RQALPHA_INTEGRATION_RESEARCH.md`
- Decision Summary: `/specs/009-integrate-quantitative-trading/BACKTESTING_DECISION_SUMMARY.md`
- Feature Spec: `/specs/009-integrate-quantitative-trading/spec.md`
