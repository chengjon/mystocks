# RQAlpha Backtesting Integration - Research Package

**Research Date**: 2025-10-18
**Status**: Complete - Ready for Implementation Decision

---

## Document Overview

This research package provides comprehensive analysis and implementation guidance for integrating backtesting capabilities into the MyStocks quantitative trading system.

### 📚 Document Structure

```
specs/009-integrate-quantitative-trading/
├── RQALPHA_INTEGRATION_RESEARCH.md          # Comprehensive research (30+ pages)
├── BACKTESTING_DECISION_SUMMARY.md          # Quick reference guide (5 pages)
├── BACKTESTING_IMPLEMENTATION_ROADMAP.md    # Implementation plan (15 pages)
└── BACKTESTING_RESEARCH_INDEX.md            # This file
```

---

## Quick Navigation

### 🎯 If you need to make a decision quickly
**Read**: `BACKTESTING_DECISION_SUMMARY.md`
- TL;DR recommendation
- Quick comparison table
- Effort estimates
- Next steps

### 🔬 If you need detailed technical analysis
**Read**: `RQALPHA_INTEGRATION_RESEARCH.md`
- Custom data bundle creation patterns
- Signal injection approaches
- Performance metrics extraction
- Common pitfalls and solutions
- Framework comparison (RQAlpha vs Backtrader vs Zipline vs VectorBT)
- Complete code examples

### 🛠️ If you're ready to implement
**Read**: `BACKTESTING_IMPLEMENTATION_ROADMAP.md`
- Week-by-week timeline
- Code structure and file locations
- Database schema
- API specifications
- Frontend components
- Requirements mapping to implementation

---

## Executive Summary

### Research Question
How to integrate RQAlpha quantitative trading framework into MyStocks for strategy backtesting with:
1. Custom data from PostgreSQL/TDengine (not RQAlpha's default bundles)
2. Pre-computed buy/sell signals (not event-driven strategy generation)
3. Programmatic metrics extraction for database storage

### Answer: Hybrid Approach Recommended

**Primary**: Build custom vectorized backtesting engine
**Optional**: Add RQAlpha integration for validation later

### Why Not Pure RQAlpha?

| Issue | Impact |
|-------|--------|
| Poor fit for pre-computed signals | Requires hacky workarounds |
| Bundle format restricts real-time updates | Conflicts with MyStocks architecture |
| 10-100x slower than vectorized | Fails performance requirements |
| Declining community support | Maintenance risk |
| Complex custom DataSource needed | 2-week integration vs 1-week vectorized |

### Why Vectorized Approach?

| Benefit | Value |
|---------|-------|
| Perfect for pre-computed signals | Natural fit for MyStocks use case |
| Direct database integration | No bundle conversion needed |
| 10-100x faster | Meets FR-015 requirement (<2 min) |
| Simple implementation | ~200 lines of code, 1-week effort |
| Full control | No external dependencies |

---

## Key Findings Summary

### 1. Custom Data Bundle Creation
- **Possible but Complex**: Requires implementing BaseDataSource interface
- **Performance Issue**: Database queries need aggressive caching layer
- **Bundle Format**: RQAlpha 4.x binary format is proprietary and restrictive
- **Recommendation**: Custom DataSource for RQAlpha, or skip RQAlpha entirely

### 2. Signal Injection
- **Architectural Mismatch**: RQAlpha designed for event-driven strategies, not signal evaluation
- **Workaround Exists**: Pre-load signals in init(), lookup in handle_bar()
- **Not Ideal**: Feels hacky, defeats purpose of event-driven framework
- **Recommendation**: Use vectorized approach for signal-based strategies

### 3. Metrics Extraction
- **Fully Supported**: run_func() returns comprehensive results dictionary
- **Programmatic Access**: result['summary'] contains all metrics (Sharpe, drawdown, etc.)
- **Database Storage**: Easy to extract and save to PostgreSQL
- **Trade Details**: result['trades'] provides complete trade history

### 4. Common Pitfalls
- Symbol format mismatches (000001 vs 000001.XSHG)
- Trading calendar discrepancies causing silent failures
- Performance degradation without caching layer
- Timezone issues (UTC+8 assumption)
- Bundle version incompatibilities (3.x vs 4.x)

### 5. Alternative Frameworks

**VectorBT** (Recommended Alternative):
- Blazing fast (12-75x faster than event-driven)
- Perfect for pre-computed signals
- Excellent documentation
- Active development
- Mature codebase

**Backtrader**:
- Mature and actively maintained
- Best for live trading integration
- Slower than vectorized approaches
- Not optimized for Chinese markets

**Zipline**:
- Deprecated, no longer maintained
- Not recommended for new projects in 2025

**Qlib** (Microsoft):
- AI/ML focused
- Enterprise-grade
- Overkill for simple signal backtesting
- Consider for future ML strategy development

---

## Decision Framework

### Choose Custom Vectorized If:
✅ You have pre-computed signals (YOUR CASE)
✅ You need 10-100x faster performance
✅ You want direct database integration
✅ You prefer no external dependencies
✅ Basic execution assumptions are acceptable

**Implementation Time**: 1 week

### Choose VectorBT If:
✅ Same as above
✅ You prefer mature library over custom code
✅ You want parameter optimization features

**Implementation Time**: 3-4 days

### Choose RQAlpha If:
✅ You need realistic execution simulation (partial fills, slippage)
✅ You plan to develop event-driven strategies (not just evaluate signals)
✅ You need Chinese market-specific features

**Implementation Time**: 2 weeks

### Choose Hybrid Approach If:
✅ You want best of both worlds
✅ Fast screening with vectorized
✅ Realistic validation with RQAlpha for top strategies

**Implementation Time**: 3 weeks (both systems)

---

## Implementation Estimates

| Approach | Core Dev | DB Integration | Testing | Total |
|----------|----------|----------------|---------|-------|
| Custom Vectorized | 2 days | 1 day | 1 day | 1 week |
| VectorBT Library | 1 day | 1 day | 1 day | 3-4 days |
| RQAlpha Integration | 4 days | 2 days | 2 days | 2 weeks |
| Hybrid (Both) | 6 days | 3 days | 3 days | 3 weeks |

---

## Recommended Next Steps

### Step 1: Review Documents
1. Read `BACKTESTING_DECISION_SUMMARY.md` (15 minutes)
2. Skim `RQALPHA_INTEGRATION_RESEARCH.md` for details (30 minutes)
3. Review `BACKTESTING_IMPLEMENTATION_ROADMAP.md` if proceeding (20 minutes)

### Step 2: Make Decision
Answer these questions:
- Do you need realistic execution simulation? (Yes → RQAlpha, No → Vectorized)
- Are you comfortable with external dependencies? (Yes → VectorBT, No → Custom)
- What's your timeline? (Urgent → VectorBT, Flexible → Custom/RQAlpha)

### Step 3: Validate with Prototype
- Build 2-day proof of concept
- Test with sample strategy signals
- Validate performance meets requirements
- Confirm metrics match manual calculations

### Step 4: Full Implementation
- Follow roadmap in `BACKTESTING_IMPLEMENTATION_ROADMAP.md`
- Create feature branch: `009-integrate-backtesting`
- Implement Week 1 deliverables
- Integrate with User Story 2 (strategy screening)

---

## Questions Resolved

✅ **How to create custom data bundles for RQAlpha?**
- Extend BaseDataSource, implement history_bars() and get_bar()
- Query PostgreSQL/TDengine directly
- Implement aggressive caching for performance

✅ **How to inject pre-computed signals?**
- Pre-load signals in init(), lookup in handle_bar()
- Or create custom mod that intercepts execution
- Better: use vectorized approach instead

✅ **Can RQAlpha metrics be extracted programmatically?**
- Yes, run_func() returns comprehensive dictionary
- result['summary'] contains all metrics
- result['trades'] provides trade history
- Easy to save to database

✅ **What are common pitfalls?**
- Symbol format mismatches
- Trading calendar discrepancies
- Database query performance
- Timezone issues
- Bundle version incompatibilities

✅ **Are there better alternatives?**
- VectorBT: Best for pre-computed signals (RECOMMENDED)
- Backtrader: Best for live trading
- Custom Vectorized: Best for full control
- RQAlpha: Best for event-driven Chinese market strategies

---

## Success Metrics

After implementation, you should achieve:

✅ Load signals and run backtest in <10 seconds (1-year, 50 stocks)
✅ Extract complete performance metrics (Sharpe, drawdown, win rate)
✅ Save results to PostgreSQL automatically
✅ Compare 100+ strategies in <5 minutes
✅ Integrate seamlessly with existing MyStocks data
✅ Meet all FR-013 through FR-018 requirements
✅ Satisfy SC-003 (3 years in <2 minutes)

---

## References

### Research Documents (This Package)
- `/specs/009-integrate-quantitative-trading/RQALPHA_INTEGRATION_RESEARCH.md`
- `/specs/009-integrate-quantitative-trading/BACKTESTING_DECISION_SUMMARY.md`
- `/specs/009-integrate-quantitative-trading/BACKTESTING_IMPLEMENTATION_ROADMAP.md`

### Feature Specification
- `/specs/009-integrate-quantitative-trading/spec.md` (User Story 3, FR-013 to FR-018)

### Related Research
- `/specs/009-integrate-quantitative-trading/CHART_VISUALIZATION_RESEARCH.md`
- `/specs/009-integrate-quantitative-trading/CHART_VISUALIZATION_QUICKREF.md`

### External Resources
- RQAlpha GitHub: https://github.com/ricequant/rqalpha
- VectorBT Docs: https://vectorbt.dev/
- Backtrader Docs: https://www.backtrader.com/

---

## Contact

For questions about this research:
- See individual documents for specific technical details
- Consult implementation roadmap for coding guidance
- Review decision summary for quick reference

---

**Document Status**: Research Complete
**Confidence Level**: High (based on extensive web research and framework comparison)
**Recommendation**: Proceed with Custom Vectorized or VectorBT approach
**Timeline**: Ready to start implementation immediately
