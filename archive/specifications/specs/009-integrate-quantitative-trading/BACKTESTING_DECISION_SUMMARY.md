# Backtesting Framework Decision Summary

**Date**: 2025-10-18
**Status**: Research Complete - Awaiting Decision

---

## TL;DR - Recommended Approach

### Build Custom Vectorized Backtester (1 week effort)

**Why**:
- Perfect fit for pre-computed signals
- 10-100x faster than RQAlpha
- Direct PostgreSQL/TDengine integration
- No external dependencies or bundle formats
- ~200 lines of code vs 2-week RQAlpha integration

**Alternative**: Use VectorBT library (same benefits, mature codebase)

---

## Quick Comparison Table

| Criteria | Custom Vectorized | RQAlpha | VectorBT | Backtrader |
|----------|-------------------|---------|----------|------------|
| Speed | ★★★★★ (Fast) | ★★★☆☆ (Medium) | ★★★★★ (Fast) | ★★☆☆☆ (Slow) |
| Pre-computed Signals | ★★★★★ (Perfect) | ★★☆☆☆ (Hacky) | ★★★★★ (Perfect) | ★★★☆☆ (OK) |
| MyStocks Integration | ★★★★★ (Native) | ★★★☆☆ (Custom DS) | ★★★★☆ (Easy) | ★★★☆☆ (Custom) |
| Chinese Markets | ★★★★★ (We control) | ★★★★★ (Native) | ★★☆☆☆ (Generic) | ★★☆☆☆ (Generic) |
| Execution Realism | ★★☆☆☆ (Basic) | ★★★★☆ (Good) | ★★☆☆☆ (Basic) | ★★★★★ (Excellent) |
| Maintenance | ★★★★★ (We own it) | ★★★☆☆ (Declining) | ★★★★★ (Active) | ★★★★☆ (Active) |
| Implementation Time | 1 week | 2 weeks | 3 days | 1.5 weeks |

---

## Decision Framework

### Choose Custom Vectorized Backtester If:
- ✅ You have pre-computed buy/sell signals (YOUR CASE)
- ✅ You need to evaluate 100s of strategies quickly
- ✅ You want direct database integration
- ✅ You prefer no external dependencies
- ✅ Basic execution assumptions are acceptable (market orders, no slippage modeling)

### Choose VectorBT Library If:
- ✅ Same as above, but you prefer mature library over custom code
- ✅ You want advanced features like parameter optimization
- ✅ You don't mind adding a dependency

### Choose RQAlpha If:
- ✅ You need realistic execution simulation (partial fills, slippage)
- ✅ You plan to develop event-driven strategies (not just evaluate signals)
- ✅ You need Chinese market-specific features (futures, margin)
- ✅ You're OK with 2-week integration effort

### Choose Backtrader If:
- ✅ You need live trading integration
- ✅ You want maximum execution realism
- ✅ Chinese market features not required

---

## Recommended Implementation Plan

### Phase 1: Vectorized Backtester (Week 1)
```
Day 1-2: Implement VectorizedBacktester class
Day 3: Add database integration (save metrics to PostgreSQL)
Day 4: Testing with sample signals
Day 5: Documentation and examples
```

**Deliverables**:
- `/backtesting/vectorized_backtester.py`
- Database tables: `backtest_metrics`, `backtest_trades`
- Example usage scripts
- Performance metrics extraction

### Phase 2: Integration (Week 2)
```
Day 1-2: Connect to strategy signal pipeline
Day 3: Batch backtesting for multiple strategies
Day 4-5: Performance comparison and validation
```

### Phase 3 (Optional): RQAlpha Validation
```
Only if needed for realistic execution validation
Estimated: 2 additional weeks
```

---

## Code Snippet: Quick Start

### Option A: Custom Implementation

```python
from backtesting.vectorized_backtester import VectorizedBacktester
from unified_manager import MyStocksUnifiedManager

# Initialize
manager = MyStocksUnifiedManager()
backtester = VectorizedBacktester(manager, initial_capital=100000)

# Load signals (from database or CSV)
signals = pd.read_csv('signals.csv')  # columns: date, symbol, action

# Load price data from PostgreSQL
price_data = backtester.load_price_data(
    symbols=signals['symbol'].unique(),
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# Run backtest
result = backtester.run_backtest(signals, price_data)

# Results
print(f"Sharpe: {result.sharpe_ratio:.2f}")
print(f"Max DD: {result.max_drawdown:.2%}")

# Save to database
backtester.save_results_to_database(result, 'momentum_v1')
```

### Option B: VectorBT Library

```python
import vectorbt as vbt

# Load from MyStocks database
df = load_from_postgres(symbols, start, end)

# Define signals
entries = signals['action'] == 'BUY'
exits = signals['action'] == 'SELL'

# Run backtest
pf = vbt.Portfolio.from_signals(df['close'], entries, exits, fees=0.0003)

# Extract metrics
metrics = {
    'sharpe': pf.sharpe_ratio(),
    'max_dd': pf.max_drawdown(),
    'total_return': pf.total_return()
}
```

---

## Effort Estimates

| Task | Custom Vectorized | RQAlpha | VectorBT |
|------|-------------------|---------|----------|
| Core Implementation | 2 days | 4 days | 1 day |
| Database Integration | 1 day | 2 days | 1 day |
| Testing | 1 day | 2 days | 1 day |
| Documentation | 1 day | 1 day | 0.5 days |
| **Total** | **5 days** | **9 days** | **3.5 days** |

---

## Key Risks and Mitigations

### Custom Vectorized Approach
**Risk**: Less realistic execution assumptions
**Mitigation**: Good enough for signal screening; can add RQAlpha later for top strategies

**Risk**: Must implement metrics ourselves
**Mitigation**: Standard formulas (Sharpe, Sortino, etc.) are well-documented

### RQAlpha Approach
**Risk**: Poor fit for pre-computed signals (requires workarounds)
**Mitigation**: Use vectorized for screening, RQAlpha for validation only

**Risk**: Performance issues with database queries
**Mitigation**: Implement aggressive caching layer

### VectorBT Approach
**Risk**: External dependency
**Mitigation**: Mature library with active development, low risk

---

## Success Metrics

After implementation, you should be able to:

1. ✅ Load pre-computed signals from database/CSV
2. ✅ Run backtest in <10 seconds for 1-year period, 50 stocks
3. ✅ Extract performance metrics (Sharpe, drawdown, win rate, etc.)
4. ✅ Save results to PostgreSQL `backtest_metrics` table
5. ✅ Compare 100+ strategies in <5 minutes
6. ✅ Integrate with existing MyStocks data infrastructure

---

## Questions to Resolve

Before proceeding, clarify:

1. **Execution Realism**: Do you need detailed slippage/commission modeling, or are basic assumptions OK?
   - If basic OK → Vectorized approach
   - If need realistic → RQAlpha or Backtrader

2. **Strategy Development**: Will you develop new event-driven strategies, or just evaluate pre-computed signals?
   - If just signals → Vectorized approach
   - If new strategies → RQAlpha or Backtrader

3. **Time Constraints**: How quickly do you need this implemented?
   - If urgent (1 week) → VectorBT or Custom Vectorized
   - If flexible (2+ weeks) → RQAlpha + Vectorized hybrid

4. **Dependencies**: Are you comfortable with external libraries (VectorBT), or prefer pure in-house code?
   - If in-house preferred → Custom Vectorized
   - If libraries OK → VectorBT

---

## Next Steps

1. **Review** this research with stakeholders
2. **Decide** on approach based on questions above
3. **Prototype** (2-3 days) with sample data to validate approach
4. **Implement** full solution (see timeline above)
5. **Validate** results against known strategies
6. **Document** usage patterns for team

---

## Contacts and Resources

- **Full Research Document**: `/specs/009-integrate-quantitative-trading/RQALPHA_INTEGRATION_RESEARCH.md`
- **Example Code**: See research document appendices
- **Database Schema**: See research document appendix

---

**Recommendation**: Start with Custom Vectorized Backtester or VectorBT. Both are fast, fit your use case perfectly, and can be implemented in <1 week. Add RQAlpha later only if realistic execution validation becomes critical.
