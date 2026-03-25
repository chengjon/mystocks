# Implementation Plan: Quantitative Trading Integration

**Branch**: `010-integrate-quantitative-trading` | **Date**: 2025-10-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-integrate-quantitative-trading/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate comprehensive quantitative trading capabilities into MyStocks system, including: (1) Strategy engine with custom stock screening and multi-process execution, (2) Technical indicator library with TDX-compatible functions and TA-Lib integration, (3) RQAlpha-based backtesting system with performance metrics, (4) PyECharts K-line visualization with signal markers, (5) TDX local data adapter for Tongdaxin software integration, and (6) PostgreSQL-based strategy signal management. This enables traders to develop, test, visualize, and deploy quantitative trading strategies while leveraging MyStocks' existing 5-tier data architecture.

**Technical Approach**: Build application layer on top of existing MyStocks core infrastructure (UnifiedDataManager, 5-tier data classification). TDX adapter reads local binary files from `/mnt/d/ProgramData/tdx_new/vipdoc/{bj,cw,ds,ot,sh,sz}` directories and stores data using intelligent routing. Strategy engine retrieves data from databases (not files), executes strategies in parallel, and saves signals to PostgreSQL. Backtest engine prepares RQAlpha data bundles from databases, executes simulations, and stores results. Visualization module generates interactive charts from database data.

## Technical Context

**Language/Version**: Python 3.12 (aligned with existing MyStocks codebase)
**Primary Dependencies**:
- Existing: pandas 1.3+, numpy 1.21+, PyYAML 5.4+, pymysql, psycopg2-binary, taospy, redis, akshare
- New: PyECharts 1.9+, RQAlpha 5.0+, pytdx 1.72+, TA-Lib 0.4.24+, tqdm 4.62+, rich 12.0+

**Storage**:
- TDengine for market data (tick, minute bars) - existing infrastructure
- PostgreSQL+TimescaleDB for signals, backtest results, technical indicators - existing infrastructure
- MySQL/MariaDB for strategy metadata, configurations - existing infrastructure
- Redis for real-time caching (optional optimization) - existing infrastructure

**Testing**: pytest (existing framework) + RQAlpha built-in backtest validation

**Target Platform**: Linux server (Ubuntu 20.04+ / WSL2) - existing deployment environment

**Project Type**: Single Python project with modular architecture (extends existing MyStocks monorepo)

**Performance Goals**:
- Strategy execution: 1000 stocks in <10 minutes (multi-process)
- Backtest: 5-year daily data in <5 minutes
- Technical indicators: 10x faster than pandas rolling operations (numpy vectorization)
- Chart rendering: <3 seconds for 2 years daily data
- TDX import: 3000 stocks in <30 minutes (initial), <2 minutes (incremental)

**Constraints**:
- Must integrate with existing UnifiedDataManager (no direct database access)
- Must follow 5-tier data classification system (constitution requirement)
- Must use configuration-driven table management (table_config.yaml)
- Must log all operations to monitoring database (observability requirement)
- TDX data path: `/mnt/d/ProgramData/tdx_new/vipdoc/` with subdirectories `{bj,cw,ds,ot,sh,sz}` for different markets
- TA-Lib binary dependency requires system-level installation on Linux

**Scale/Scope**:
- Stock pool: 3000-5000 Chinese stocks
- Historical data: 10+ years daily data, 1+ year minute data
- Strategy complexity: Support 20-50 custom indicators per strategy
- Concurrent strategies: 3-5 strategies executing simultaneously
- Backtest scenarios: 100+ parameter combinations for optimization

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. 5-Tier Data Classification Compliance ✅

**Strategy Signals** (Derived Data - FR-035):
- Classification: Derived Data → PostgreSQL+TimescaleDB
- Rationale: Computed results from strategy logic, time-series nature
- Storage: `strategy_signals` table with date, symbol, signal type, strength
- **COMPLIANT**: Follows constitution principle for derived/computed data

**Backtest Results** (Derived Data - FR-036):
- Classification: Derived Data → PostgreSQL+TimescaleDB
- Rationale: Analytical results with time-series equity curves
- Storage: `backtest_results` table with JSONB for detailed metrics
- **COMPLIANT**: Mixed time-series + non-time-series structure fits PostgreSQL

**Technical Indicators** (Derived Data):
- Classification: Derived Data → PostgreSQL+TimescaleDB
- Rationale: Calculated metrics from price/volume data
- Storage: Cached in memory during execution, persistent storage optional
- **COMPLIANT**: Follows constitution for computed analytical data

**TDX Imported Market Data** (Market Data - FR-031):
- Classification: Market Data (daily/weekly/monthly K-lines) → PostgreSQL+TimescaleDB
- Rationale: Daily+ frequency data fits constitution's market data guidance
- Storage: Via UnifiedDataManager using intelligent routing
- **COMPLIANT**: TDX daily data routed to PostgreSQL per constitution (medium frequency)

**Strategy Metadata** (Meta Data - FR-037):
- Classification: Meta Data → MySQL/MariaDB
- Rationale: Strategy parameters, versions, configurations
- Storage: `strategy_config` table defined in table_config.yaml
- **COMPLIANT**: Configuration-type data follows meta data classification

### II. Configuration-Driven Design Compliance ✅

**Table Definitions** (FR-037):
- Requirement: Add `strategy_signals`, `backtest_results`, `strategy_config`, `tdx_import_jobs` to table_config.yaml
- Approach: All table schemas defined in YAML, created via ConfigDrivenTableManager
- **COMPLIANT**: No manual schema modifications, all config-driven

**System Configuration**:
- TDX paths, backtest defaults, indicator parameters defined in `strategy_config.yaml` or .env
- No hardcoded paths except in development documentation
- **COMPLIANT**: Follows configuration-driven principle

### III. Intelligent Auto-Routing Compliance ✅

**Data Retrieval** (FR-006, FR-038):
- Requirement: Strategy engine must use UnifiedDataManager, not direct file access
- Implementation: All data access via `load_data_by_classification()` methods
- **COMPLIANT**: No direct database or file access in strategy execution

**Data Storage** (FR-035, FR-036):
- Requirement: Signals and results use `save_data_by_classification()`
- Implementation: DataClassification.DERIVED_DATA triggers PostgreSQL routing
- **COMPLIANT**: Auto-routing based on classification enum

### IV. Multi-Database Coordination Compliance ✅

**Database Specialization**:
- TDengine: Not used in this feature (existing market data already stored)
- PostgreSQL: Strategy signals, backtest results, indicators (time-series analysis)
- MySQL: Strategy configs, metadata (ACID compliance)
- Redis: Optional caching for hot indicators (future optimization)
- **COMPLIANT**: Each database used according to technical strengths

### V. Complete Observability Compliance ✅ (FR-039, FR-040)

**Monitoring Integration**:
- All strategy executions logged to MonitoringDatabase
- Performance metrics tracked (execution time, stocks/sec)
- Data quality checks for signal completeness
- Alert on strategy failures or slow backtests
- **COMPLIANT**: Full monitoring integration required

### VI. Unified Access Interface Compliance ✅ (FR-006, FR-038)

**Data Access**:
- All operations through MyStocksUnifiedManager
- Strategy engine receives UnifiedManager instance in constructor
- Backtest engine receives UnifiedManager instance in constructor
- Visualization module receives UnifiedManager instance in constructor
- **COMPLIANT**: No direct database access outside data access layer

### VII. Security-First Compliance ✅

**Credentials**:
- TDX path configurable via environment variable TDX_DATA_PATH
- RQAlpha data bundle path via RQALPHA_DATA_PATH
- All database credentials via existing .env pattern
- No credentials in source code
- **COMPLIANT**: Environment variable driven configuration

**GATE RESULT**: ✅ **PASSED** - No constitution violations. All requirements align with established principles.

## Project Structure

### Documentation (this feature)

```
specs/010-integrate-quantitative-trading/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (next)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── strategy_api.yaml         # Strategy execution contracts
│   ├── backtest_api.yaml         # Backtest execution contracts
│   ├── visualization_api.yaml    # Chart generation contracts
│   └── tdx_adapter_api.yaml      # TDX import contracts
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```
mystocks_spec/
├── strategy/                      # NEW - Strategy engine module
│   ├── __init__.py
│   ├── base_strategy.py          # Base strategy class for inheritance
│   ├── strategy_executor.py      # Multi-process execution engine
│   ├── signal_manager.py         # Signal persistence and retrieval
│   ├── stock_screener.py         # Stock pool filtering logic
│   └── templates/
│       ├── momentum_template.py  # Example momentum strategy
│       ├── mean_reversion_template.py
│       └── custom_template.py    # Blank template for users
│
├── backtest/                      # NEW - Backtesting module
│   ├── __init__.py
│   ├── rqalpha_adapter.py        # RQAlpha integration layer
│   ├── backtest_engine.py        # Main backtest execution
│   ├── data_bundle_builder.py   # Convert DB data → RQAlpha format
│   ├── performance_metrics.py    # Metrics calculation
│   └── risk_metrics.py           # Risk analysis (Sharpe, drawdown, etc.)
│
├── indicators/                    # NEW - Technical indicator library
│   ├── __init__.py
│   ├── tdx_functions.py          # TDX-compatible functions (MA, SMA, etc.)
│   ├── talib_wrapper.py          # TA-Lib integration wrapper
│   ├── custom_indicators.py      # User-defined indicator templates
│   └── indicator_cache.py        # Caching layer for performance
│
├── visualization/                 # NEW - Chart generation module
│   ├── __init__.py
│   ├── kline_chart.py            # K-line chart with PyECharts
│   ├── signal_plot.py            # Buy/sell signal markers
│   ├── backtest_plot.py          # Equity curve and performance charts
│   └── chart_config.py           # Chart styling and configuration
│
├── adapters/
│   ├── tdx_adapter.py            # NEW - Tongdaxin data adapter
│   │                              # Reads from /mnt/d/ProgramData/tdx_new/vipdoc/
│   │                              # Subdirs: bj, cw, ds, ot, sh, sz
│   ├── akshare_adapter.py        # EXISTING
│   └── ...                        # EXISTING adapters
│
├── core.py                        # EXISTING - Extend DataClassification if needed
├── unified_manager.py             # EXISTING - No changes needed
├── data_access.py                 # EXISTING - No changes needed
├── db_manager/                    # EXISTING - No changes needed
├── monitoring/                    # EXISTING - No changes needed
│
├── config/
│   └── strategy_config.yaml      # NEW - Strategy/backtest configuration
│
├── table_config.yaml              # MODIFY - Add new tables
│
├── tests/
│   ├── test_strategy_executor.py # NEW - Strategy execution tests
│   ├── test_backtest_engine.py   # NEW - Backtest validation tests
│   ├── test_tdx_adapter.py       # NEW - TDX import tests
│   ├── test_indicators.py        # NEW - Indicator calculation tests
│   └── test_visualization.py     # NEW - Chart generation tests
│
└── examples/
    ├── example_strategy_execution.py    # NEW - Strategy usage example
    ├── example_backtest.py              # NEW - Backtest usage example
    └── example_visualization.py         # NEW - Chart usage example
```

**Structure Decision**: Single Python project structure (Option 1) with new top-level modules (`strategy/`, `backtest/`, `indicators/`, `visualization/`) integrated into existing MyStocks monorepo. This approach:
- Maintains consistency with existing architecture
- Allows direct access to UnifiedDataManager and core infrastructure
- Simplifies dependency management and deployment
- Enables code reuse across modules (e.g., indicators used by both strategy and backtest)

**TDX Data Path Configuration**:
- System configured to read from `/mnt/d/ProgramData/tdx_new/vipdoc/`
- Market subdirectories mapped as:
  - `sh/` - Shanghai Stock Exchange
  - `sz/` - Shenzhen Stock Exchange
  - `bj/` - Beijing Stock Exchange
  - `cw/` - Financial data files
  - `ds/` - Dividend/split data
  - `ot/` - Other data types
- Adapter auto-discovers `.day` files and processes all markets

## Complexity Tracking

*No constitution violations - this section intentionally empty.*

All design decisions comply with MyStocks constitution principles. The feature integrates cleanly into existing 5-tier data architecture without requiring exceptions or workarounds.

---

## Planning Phase Completion

**Status**: ✅ **COMPLETED**

**Date**: 2025-10-18

**Artifacts Generated**:

1. ✅ `plan.md` - Implementation plan with technical context and constitution check
2. ✅ `research.md` - Technology research covering RQAlpha, TA-Lib, and visualization libraries
3. ✅ `data-model.md` - Complete entity definitions with database schemas
4. ✅ `contracts/strategy_api.yaml` - Strategy execution API specification
5. ✅ `quickstart.md` - Developer onboarding guide with examples
6. ✅ `checklists/requirements.md` - Specification quality checklist (from /speckit.specify)

**Constitution Re-Check**: ✅ **PASSED** (all 7 principles compliant)

**Key Decisions**:
- Use **Custom Vectorized Backtester** instead of RQAlpha (10-100x faster for pre-computed signals)
- Upgrade to **TA-Lib 0.6.7** (binary wheels eliminate compilation issues)
- Use **mplfinance** for primary charts (simpler, faster than PyECharts)
- TDX data path: `/mnt/d/ProgramData/tdx_new/vipdoc/{bj,cw,ds,ot,sh,sz}`

**Performance Targets Enhanced**:
- Backtest: 5-year data in <5 **seconds** (was <5 minutes, 60x better)
- Chart generation: <0.3 seconds (was <3 seconds, 10x faster)
- Strategy execution: 1000 stocks in <10 minutes ✅

**Next Phase**: Run `/speckit.tasks` to generate implementation tasks breakdown

---

## Implementation Readiness Checklist

- [x] Technical context defined
- [x] All technology unknowns researched
- [x] Constitution compliance verified (no violations)
- [x] Data model designed with database schemas
- [x] API contracts specified
- [x] Developer quickstart guide created
- [x] Agent context updated
- [ ] Tasks breakdown (run `/speckit.tasks`)
- [ ] Implementation begins

**Ready to Proceed**: ✅ Yes - All planning artifacts complete
