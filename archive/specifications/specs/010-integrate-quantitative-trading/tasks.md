# Tasks: Quantitative Trading Integration

**Input**: Design documents from `/specs/010-integrate-quantitative-trading/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No test tasks included (tests not explicitly requested in spec)

**Organization**: Tasks are grouped by user story (P1-P5) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5, Setup, Foundation)
- Include exact file paths in descriptions

## Path Conventions
- **Project type**: Single Python project (monorepo extension)
- **Root**: `/opt/claude/mystocks_spec/`
- **New modules**: `strategy/`, `backtest/`, `indicators/`, `visualization/`
- **Modified**: `adapters/`, `table_config.yaml`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and database schema

### Environment & Dependencies

- [ ] **T001** [P] [Setup] Install TA-Lib 0.6.7 via pip: `pip install --upgrade TA-Lib==0.6.7` and verify with `python -c "import talib; print(talib.__version__)"`
- [ ] **T002** [P] [Setup] Install mplfinance: `pip install mplfinance==0.12.10b0` for K-line chart generation
- [ ] **T003** [P] [Setup] Install pytdx: `pip install pytdx==1.72` for TDX real-time quotes
- [ ] **T004** [P] [Setup] Install additional dependencies: `pip install scipy tqdm rich` for optimization and UI enhancements
- [ ] **T005** [Setup] Update `requirements.txt` or create if missing, adding all new dependencies with pinned versions

### Directory Structure

- [ ] **T006** [P] [Setup] Create `strategy/` directory with `__init__.py`, `base_strategy.py`, `strategy_executor.py`, `signal_manager.py`, `stock_screener.py`
- [ ] **T007** [P] [Setup] Create `strategy/templates/` directory with `__init__.py`, `momentum_template.py`, `mean_reversion_template.py`, `custom_template.py`
- [ ] **T008** [P] [Setup] Create `backtest/` directory with `__init__.py`, `vectorized_backtester.py`, `performance_metrics.py`, `risk_metrics.py`
- [ ] **T009** [P] [Setup] Create `indicators/` directory with `__init__.py`, `tdx_functions.py`, `talib_wrapper.py`, `custom_indicators.py`, `indicator_cache.py`
- [ ] **T010** [P] [Setup] Create `visualization/` directory with `__init__.py`, `kline_chart.py`, `signal_plot.py`, `backtest_plot.py`, `chart_config.py`
- [ ] **T011** [P] [Setup] Create `config/` directory (if not exists) and add `strategy_config.yaml` for strategy/backtest configuration
- [ ] **T012** [P] [Setup] Create `examples/` directory with placeholder files: `example_strategy_execution.py`, `example_backtest.py`, `example_visualization.py`
- [ ] **T013** [P] [Setup] Create `tests/` subdirectories: `tests/test_strategy_executor.py`, `tests/test_backtest_engine.py`, `tests/test_tdx_adapter.py`, `tests/test_indicators.py`, `tests/test_visualization.py`

### Database Schema

- [ ] **T014** [Foundation] Update `table_config.yaml` to add `strategy` table (MySQL) with columns: id, name, version, description, parameters (JSON), code_hash, created_at, updated_at, created_by, is_active, tags (JSON)
- [ ] **T015** [Foundation] Update `table_config.yaml` to add `strategy_signals` table (PostgreSQL) with columns: id, strategy_id, symbol, signal_date, signal_type, signal_strength, entry_price, indicators (JSONB), metadata (JSONB), created_at, plus indexes on (strategy_id, symbol, signal_date), (signal_date), (symbol, signal_date)
- [ ] **T016** [Foundation] Update `table_config.yaml` to add `backtest_results` table (PostgreSQL) with columns: id, strategy_id, start_date, end_date, initial_capital, final_capital, total_return, annualized_return, max_drawdown, sharpe_ratio, win_rate, total_trades, benchmark_return, commission_rate, slippage_rate, metrics_json (JSONB), equity_curve (JSONB), trade_log (JSONB), created_at, plus indexes on (strategy_id, start_date, end_date), (created_at)
- [ ] **T017** [Foundation] Update `table_config.yaml` to add `tdx_import_jobs` table (MySQL) with columns: id, job_type, market, start_time, end_time, status, total_files, processed_files, failed_files, total_records, error_log (JSON), import_config (JSON), created_by, plus indexes on (start_time), (status)
- [ ] **T018** [Foundation] Run `ConfigDrivenTableManager.batch_create_tables('table_config.yaml')` to create all new database tables in MySQL and PostgreSQL

### Environment Configuration

- [ ] **T019** [P] [Setup] Add TDX configuration to `.env` file: `TDX_DATA_PATH=/mnt/d/ProgramData/tdx_new/vipdoc`, `TDX_MARKETS=sh,sz,bj,cw,ds,ot`
- [ ] **T020** [P] [Setup] Add strategy configuration to `.env`: `STRATEGY_EXECUTION_TIMEOUT=600`, `STRATEGY_MAX_WORKERS=4`
- [ ] **T021** [P] [Setup] Add backtest configuration to `.env`: `BACKTEST_DEFAULT_CAPITAL=100000`, `BACKTEST_COMMISSION_RATE=0.0003`, `BACKTEST_SLIPPAGE_RATE=0.0001`, `BACKTEST_BENCHMARK=000300.XSHG`
- [ ] **T022** [P] [Setup] Add visualization configuration to `.env`: `CHART_DEFAULT_DPI=150`, `CHART_OUTPUT_DIR=/opt/claude/mystocks_spec/charts`
- [ ] **T023** [Setup] Create `config/strategy_config.yaml` with default strategy parameters, backtest settings, and TDX adapter configuration

**Checkpoint**: All dependencies installed, directories created, database tables ready, configuration files in place

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Technical Indicator Library (Prerequisite for US1, US5)

- [ ] **T024** [P] [Foundation] Implement `indicators/tdx_functions.py` with TDX-compatible functions: MA(), SMA(), HHV(), LLV(), COUNT(), EXIST(), CROSS(), BARSLAST(), REF() using numpy vectorization (FR-008)
- [ ] **T025** [P] [Foundation] Implement `indicators/talib_wrapper.py` with TALibIndicators class providing wrappers for RSI(), MACD(), BBANDS(), ATR() and other TA-Lib indicators (FR-009)
- [ ] **T026** [Foundation] Implement `indicators/indicator_cache.py` with IndicatorCache class for in-memory caching with TTL support, cache key generation from symbol+indicator+parameters (FR-011)
- [ ] **T027** [P] [Foundation] Implement `indicators/custom_indicators.py` with example custom indicator templates and documentation for user-defined indicators

### Base Strategy Class (Prerequisite for US1)

- [ ] **T028** [Foundation] Implement `strategy/base_strategy.py` with BaseStrategy abstract class defining `generate_signals(data: pd.DataFrame) -> pd.Series` and `filter_stocks(stock_pool: List[str]) -> List[str]` methods (FR-001)
- [ ] **T029** [Foundation] Add parameter validation, logging, and error handling to BaseStrategy class
- [ ] **T030** [P] [Foundation] Create example strategy templates in `strategy/templates/momentum_template.py` demonstrating MA crossover with RSI filter
- [ ] **T031** [P] [Foundation] Create example strategy template in `strategy/templates/mean_reversion_template.py` demonstrating Bollinger Band strategy

### Signal Management (Prerequisite for US1, US2)

- [ ] **T032** [Foundation] Implement `strategy/signal_manager.py` with SignalManager class for CRUD operations on strategy_signals table via UnifiedDataManager (FR-005, FR-035)
- [ ] **T033** [Foundation] Add methods to SignalManager: `save_signal()`, `batch_insert_signals()`, `get_signals()`, `delete_signals()` with proper error handling
- [ ] **T034** [Foundation] Implement signal validation logic in SignalManager: check signal_strength range [0, 1], entry_price > 0, signal_date is valid trading day

**Checkpoint**: Foundation ready - Technical indicators available, base strategy class functional, signal persistence working

---

## Phase 3: User Story 1 - Execute Custom Stock Screening Strategy (Priority: P1) 🎯 MVP

**Goal**: Enable traders to execute custom strategies against stock pools and generate buy/sell signals

**Independent Test**: Define a simple MA crossover strategy, execute against test pool of 10 stocks, verify signals are correctly generated and saved to PostgreSQL

### Stock Pool Filtering (US1 Prerequisite)

- [ ] **T035** [P] [US1] Implement `strategy/stock_screener.py` with StockScreener class for filtering excluded categories (ST stocks, specific industries, board types) from stock pool (FR-004)
- [ ] **T036** [US1] Add integration with TDX block files (block_gn.dat, tdxhy.cfg) to identify stocks to exclude based on concept/industry classifications
- [ ] **T037** [US1] Implement blacklist/whitelist support in StockScreener for user-defined exclusions

### Strategy Executor Core

- [ ] **T038** [US1] Implement `strategy/strategy_executor.py` with StrategyExecutor class constructor accepting UnifiedDataManager instance (FR-006)
- [ ] **T039** [US1] Implement `run_screening()` method with parameters: strategy, stock_pool, parallel, execution_mode ('fast'/'full'), start_date, end_date (FR-002, FR-003)
- [ ] **T040** [US1] Add fast mode logic to only process latest data point for quick screening (FR-002)
- [ ] **T041** [US1] Add full mode logic to process historical period and generate complete signal history (FR-002)
- [ ] **T042** [US1] Implement multi-process execution using `multiprocessing.Pool` with worker count from env config, distribute stocks across workers (FR-003)
- [ ] **T043** [US1] Add progress tracking with tqdm or rich progress bars showing stocks processed, signals found, elapsed time, ETA (FR-007)
- [ ] **T044** [US1] Implement error handling for individual stock failures - continue processing, collect errors, save successful signals (Acceptance Scenario 5)
- [ ] **T045** [US1] Add data retrieval logic using UnifiedDataManager.load_data_by_classification() for market data (FR-006)
- [ ] **T046** [US1] Implement indicator calculation caching during strategy execution to avoid redundant computation (FR-011)
- [ ] **T047** [US1] Add signal saving logic using SignalManager.batch_insert_signals() for performance (FR-005)
- [ ] **T048** [US1] Integrate with MonitoringDatabase to log strategy execution start, completion, duration, stocks processed, errors (FR-039, FR-040)

### Strategy Metadata Management

- [ ] **T049** [P] [US1] Implement strategy CRUD operations in `strategy/signal_manager.py` (or separate strategy_manager.py): create_strategy(), get_strategy(), update_strategy(), list_strategies(), delete_strategy() interacting with MySQL strategy table
- [ ] **T050** [US1] Add strategy code hash calculation using SHA-256 to detect strategy changes
- [ ] **T051** [US1] Implement strategy versioning logic - auto-increment version when parameters or code changes

### Example Implementation

- [ ] **T052** [P] [US1] Create `examples/example_strategy_execution.py` demonstrating complete workflow: load UnifiedManager, create strategy, execute screening, view results
- [ ] **T053** [P] [US1] Add documentation to example file explaining each step, parameters, expected output

**Checkpoint**: User Story 1 complete - Traders can execute custom strategies, see progress, get signals saved to database

---

## Phase 4: User Story 2 - Backtest Strategy Performance (Priority: P2)

**Goal**: Enable traders to backtest strategies against historical data and evaluate performance metrics

**Independent Test**: Run backtest on known historical period (e.g., 2020-2024) with simple buy-and-hold strategy, verify total return matches expected value within 0.1%

### Vectorized Backtest Engine

- [ ] **T054** [US2] Implement `backtest/vectorized_backtester.py` with VectorizedBacktester class constructor accepting signals_df, price_df, initial_capital, commission_rate, slippage_rate (research decision: custom vectorized, not RQAlpha)
- [ ] **T055** [US2] Implement `run()` method using vectorized pandas operations: calculate positions from buy/sell signals, compute price changes, strategy returns, equity curve (FR-016)
- [ ] **T056** [US2] Add transaction cost calculation: apply commission on each trade, apply slippage to entry/exit prices (FR-015, Acceptance Scenario 2)
- [ ] **T057** [US2] Implement trade extraction logic: identify entry/exit pairs, calculate hold period, profit/loss per trade, trade count (Acceptance Scenario 3)
- [ ] **T058** [US2] Add benchmark comparison: load benchmark data (000300.XSHG), calculate benchmark returns, compare with strategy (FR-018, Acceptance Scenario 5)

### Performance Metrics Calculation

- [ ] **T059** [P] [US2] Implement `backtest/performance_metrics.py` with PerformanceMetrics class to calculate: total_return, annualized_return, max_drawdown, win_rate (FR-016)
- [ ] **T060** [P] [US2] Implement `backtest/risk_metrics.py` with RiskMetrics class to calculate: Sharpe ratio, Sortino ratio, Calmar ratio, volatility, beta
- [ ] **T061** [US2] Add metric validation: ensure calculations match manual verification within 0.1% tolerance (SC-004)

### Backtest Result Persistence

- [ ] **T062** [US2] Implement `save_result()` method in VectorizedBacktester to save backtest data to PostgreSQL backtest_results table via UnifiedDataManager (FR-017)
- [ ] **T063** [US2] Format equity_curve and trade_log as JSONB for storage, include all required metrics in metrics_json field (FR-017)
- [ ] **T064** [US2] Add result retrieval methods: get_backtest_result(id), list_backtest_results(strategy_id), compare_backtest_results(ids)

### Data Preparation

- [ ] **T065** [US2] Implement data loading logic in VectorizedBacktester to query UnifiedDataManager for price data matching signal date range (FR-014 adapted - no RQAlpha bundle needed)
- [ ] **T066** [US2] Add forward adjustment handling: ensure price data uses forward-adjusted values to account for splits/dividends (FR-019)
- [ ] **T067** [US2] Implement edge case handling: skip stocks with insufficient data, handle halted stocks, respect position limits (FR-020)

### Equity Curve Visualization

- [ ] **T068** [P] [US2] Implement `backtest/backtest_plot.py` with functions to generate equity curve charts using mplfinance or matplotlib
- [ ] **T069** [US2] Add benchmark overlay to equity curve, highlight drawdown periods, show key metrics on chart

### Example Implementation

- [ ] **T070** [P] [US2] Create `examples/example_backtest.py` demonstrating complete backtest workflow: load signals, run backtest, display metrics, save results, generate chart
- [ ] **T071** [P] [US2] Add parameter optimization example showing how to run multiple backtests with different parameters (Acceptance Scenario 4)

**Checkpoint**: User Story 2 complete - Traders can backtest strategies, view performance metrics, compare with benchmark

---

## Phase 5: User Story 3 - Visualize Strategy Signals on K-Line Charts (Priority: P3)

**Goal**: Enable traders to visualize strategy signals overlaid on K-line charts with profit/loss color coding

**Independent Test**: Generate K-line chart for test stock with known signals, verify buy markers at bottom, sell markers at top, holding periods highlighted correctly

### K-Line Chart Generator

- [ ] **T072** [US3] Implement `visualization/kline_chart.py` with KLineChartGenerator class using mplfinance library (research decision: mplfinance instead of PyECharts)
- [ ] **T073** [US3] Implement `generate_chart()` method accepting symbol, start_date, end_date, strategy_id, show_signals, show_holding_periods, moving_averages, output_format, dpi (FR-021, FR-027)
- [ ] **T074** [US3] Add OHLCV data loading from UnifiedDataManager for specified symbol and date range (FR-027)
- [ ] **T075** [US3] Add signal loading from SignalManager for specified strategy and date range

### Signal Markers

- [ ] **T076** [US3] Implement buy signal markers using mplfinance `make_addplot()` with scatter type, green color, upward triangle marker at bottom of candles (FR-022, Acceptance Scenario 1)
- [ ] **T077** [US3] Implement sell signal markers using mplfinance `make_addplot()` with scatter type, red color, downward triangle marker at top of candles (FR-022, Acceptance Scenario 1)
- [ ] **T078** [P] [US3] Add tooltip/annotation support (if using Plotly optional mode) to show signal details on hover: date, price, strategy parameters (Acceptance Scenario 2)

### Holding Period Highlighting

- [ ] **T079** [US3] Implement holding period calculation: pair buy/sell signals, identify holding start/end dates
- [ ] **T080** [US3] Add profit/loss calculation for each holding period: compare exit price to entry price
- [ ] **T081** [US3] Implement holding period highlighting using fill_between with conditional colors: green for profit (exit > entry), red for loss (exit < entry) (FR-023, Acceptance Scenario 3)

### Additional Chart Features

- [ ] **T082** [P] [US3] Add moving average overlays using mplfinance addplot for MA-5, MA-20, MA-60 if requested (FR-024)
- [ ] **T083** [P] [US3] Add trend line support for manual/automatic trend line drawing (FR-024)
- [ ] **T084** [US3] Implement volume subplot display at bottom of chart (standard mplfinance feature)

### Chart Export

- [ ] **T085** [US3] Implement PNG export using mplfinance `savefig` parameter with configurable DPI from env (FR-025)
- [ ] **T086** [P] [US3] Implement JPG export option with quality parameter (FR-025)
- [ ] **T087** [P] [US3] Add optional Plotly implementation in separate module for interactive HTML export with zoom/pan (FR-026, Acceptance Scenario 4, 5)

### Chart Configuration

- [ ] **T088** [P] [US3] Implement `visualization/chart_config.py` with ChartConfiguration dataclass for chart styling: colors, fonts, figure size, title format
- [ ] **T089** [US3] Add preset themes: light mode, dark mode, print-friendly mode

### Example Implementation

- [ ] **T090** [P] [US3] Create `examples/example_visualization.py` demonstrating chart generation for multiple stocks with different strategies
- [ ] **T091** [P] [US3] Add batch chart generation example: loop through signal results, generate chart for each stock, save to output directory

**Checkpoint**: User Story 3 complete - Traders can visualize signals on K-line charts, see profit/loss periods, export charts

---

## Phase 6: User Story 4 - Import Data from Tongdaxin Software (Priority: P4)

**Goal**: Enable traders to import TDX local data files into MyStocks database

**Independent Test**: Point adapter to sample TDX directory, import 10 stocks, verify data matches TDX software display and is correctly stored in PostgreSQL

### TDX Binary File Parser

- [ ] **T092** [US4] Implement `adapters/tdx_adapter.py` with TDXDataAdapter class constructor accepting tdx_root path and UnifiedDataManager instance
- [ ] **T093** [US4] Implement `read_day_file()` method to parse TDX .day binary files: read 32-byte records, unpack using struct with format '<IIIIIfII', convert prices from int/1000 to float (FR-028)
- [ ] **T094** [US4] Add date parsing from YYYYMMDD int format to datetime, handle invalid dates
- [ ] **T095** [US4] Implement OHLCV DataFrame construction from parsed records with columns: date, open, high, low, close, volume, amount

### Financial Data Parser

- [ ] **T096** [P] [US4] Implement `read_financial_file()` method to parse TDX financial data files from cw/ directory using struct unpacking (FR-029)
- [ ] **T097** [P] [US4] Implement `read_equity_change_file()` method to parse dividend/split data from ds/ directory for forward adjustment calculations (FR-029)

### Forward Adjustment

- [ ] **T098** [US4] Implement `apply_forward_adjustment()` method to adjust historical prices using equity change data: calculate cumulative adjustment factors, apply to OHLC prices (FR-030)
- [ ] **T099** [US4] Add validation: compare adjusted prices to TDX software display to ensure correctness (Acceptance Scenario 2)

### Market Discovery & Import

- [ ] **T100** [US4] Implement `discover_stock_files()` method to auto-discover .day files in sh/, sz/, bj/ subdirectories under TDX_DATA_PATH from env config (FR-032, Acceptance Scenario 1)
- [ ] **T101** [US4] Implement `import_market_data()` method with parameters: market ('sh'/'sz'/'bj'/'all'), import_type ('full'/'incremental'), apply_adjustment (bool) (FR-032)
- [ ] **T102** [US4] Add incremental import logic: query PostgreSQL for latest date, only import records newer than latest date (FR-032, Acceptance Scenario 5)
- [ ] **T103** [US4] Implement full import logic: delete existing data for symbol, import all historical records from .day file
- [ ] **T104** [US4] Add multi-process import support: distribute files across workers for parallel processing (improve SC-006 target)

### Data Storage via Routing

- [ ] **T105** [US4] Integrate with UnifiedDataManager to save imported data: use save_data_by_classification() with DataClassification.MARKET_DATA for daily K-lines (FR-031)
- [ ] **T106** [US4] Route financial data to PostgreSQL using appropriate classification (reference data or derived data)
- [ ] **T107** [US4] Add data validation before storage: check for negative prices, zero volume days, date ordering

### Import Job Tracking

- [ ] **T108** [US4] Implement import job logging to tdx_import_jobs MySQL table: record start_time, status, total_files, processed_files, failed_files (FR-033)
- [ ] **T109** [US4] Add progress tracking callback to update job record during import: increment processed_files, log errors to error_log JSON field (Acceptance Scenario 3)
- [ ] **T110** [US4] Implement `get_import_status()` method to query job status by job_id

### Error Handling

- [ ] **T111** [US4] Add error handling for corrupted files: catch struct.error, log to job error_log, skip file and continue (FR-033, Edge Case 1)
- [ ] **T112** [US4] Add error handling for partial files: detect incomplete 32-byte records, process complete records only, warn user
- [ ] **T113** [US4] Add validation error reporting: collect all validation failures, save to error_log with file path and error details

### Example Implementation

- [ ] **T114** [P] [US4] Create command-line script `scripts/import_tdx_data.py` for running imports: parse arguments (market, type), execute import, display progress
- [ ] **T115** [P] [US4] Add example in `examples/` showing programmatic import usage with error handling

**Checkpoint**: User Story 4 complete - Traders can import TDX data, see progress, data correctly stored and adjusted

---

## Phase 7: User Story 5 - Calculate Technical Indicators (Priority: P5)

**Goal**: Provide comprehensive technical indicator library for strategy development

**Independent Test**: Calculate MA(20) on test data with known values, verify output matches expected values within floating-point tolerance

**NOTE**: Most of this was completed in Phase 2 (Foundation). These tasks are refinements and documentation.

### TDX Function Enhancements

- [ ] **T116** [P] [US5] Add additional TDX functions to `indicators/tdx_functions.py`: EVERY(), FILTER(), BARSSINCE(), SUM(), STD() for advanced strategies
- [ ] **T117** [P] [US5] Implement rolling window optimization for performance: use numpy stride tricks for vectorization (FR-010)
- [ ] **T118** [US5] Add TDX function testing: verify MA() output matches TDX software calculation exactly (Acceptance Scenario 2)

### TA-Lib Integration Enhancements

- [ ] **T119** [P] [US5] Add convenience wrappers in `indicators/talib_wrapper.py` for all commonly-used TA-Lib functions: STOCH, ADX, CCI, MFI, OBV
- [ ] **T120** [US5] Add parameter validation: check period > 0, arrays have sufficient length, handle NaN values gracefully (FR-012)

### Custom Indicator Support

- [ ] **T121** [P] [US5] Add documentation to `indicators/custom_indicators.py` explaining how to define custom indicators, provide template function signature
- [ ] **T122** [P] [US5] Create example custom indicators: momentum_oscillator(), custom_volatility(), sector_strength()
- [ ] **T123** [US5] Add custom indicator registration system: allow users to register functions, call by name in strategies (Acceptance Scenario 5)

### Indicator Caching Optimization

- [ ] **T124** [US5] Enhance `indicators/indicator_cache.py` with LRU eviction policy when cache size exceeds threshold
- [ ] **T125** [US5] Add cache hit/miss metrics logging to monitoring database for performance analysis
- [ ] **T126** [US5] Implement cache warming: pre-calculate common indicators for all stocks before strategy execution

### Performance Benchmarking

- [ ] **T127** [P] [US5] Create benchmark script comparing TA-Lib vs pandas rolling operations: measure 10x speedup requirement (SC-008)
- [ ] **T128** [US5] Profile indicator calculation with cProfile: identify bottlenecks, optimize hot paths

### Documentation

- [ ] **T129** [P] [US5] Document all TDX functions in `indicators/tdx_functions.py` with docstrings: parameters, return types, examples, TDX formula references
- [ ] **T130** [P] [US5] Document all TA-Lib wrappers in `indicators/talib_wrapper.py` with usage examples, parameter ranges, interpretation guidance
- [ ] **T131** [P] [US5] Create indicator reference guide in docs/: categorize by type (trend, momentum, volatility), provide usage recommendations

**Checkpoint**: User Story 5 complete - Comprehensive indicator library available with excellent performance and documentation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, final integration, documentation

### Integration & Validation

- [ ] **T132** [Polish] Run complete end-to-end workflow: import TDX data → execute strategy → backtest → visualize → verify all components integrate correctly
- [ ] **T133** [Polish] Validate all success criteria from spec.md: measure performance, verify accuracy, check error rates
- [ ] **T134** [Polish] Run `quickstart.md` validation: follow all steps in quickstart guide, ensure they work without errors

### Performance Optimization

- [ ] **T135** [P] [Polish] Profile strategy execution with 1000 stocks: identify bottlenecks, optimize to meet <10 minute target (SC-001)
- [ ] **T136** [P] [Polish] Profile backtest execution with 5-year data: optimize to meet <5 second target (research target, exceeds SC-003)
- [ ] **T137** [P] [Polish] Profile chart generation: optimize to meet <0.3 second target (research target, exceeds SC-005)
- [ ] **T138** [Polish] Optimize database queries: add missing indexes, use batch operations, reduce query count

### Documentation

- [ ] **T139** [P] [Polish] Update `CLAUDE.md` with quantitative trading feature overview, common commands, architecture notes
- [ ] **T140** [P] [Polish] Create user guide in `docs/quantitative_trading_guide.md`: strategy development, backtesting, visualization
- [ ] **T141** [P] [Polish] Document configuration options in `docs/configuration.md`: all .env variables, strategy_config.yaml structure
- [ ] **T142** [P] [Polish] Create troubleshooting guide in `docs/troubleshooting.md`: common errors, solutions, FAQs

### Code Quality

- [ ] **T143** [P] [Polish] Add type hints to all public functions and classes using Python 3.12 type annotation syntax
- [ ] **T144** [P] [Polish] Add docstrings to all modules, classes, and functions following Google or NumPy style
- [ ] **T145** [P] [Polish] Run linter (pylint/flake8) and fix all warnings
- [ ] **T146** [P] [Polish] Run formatter (black) on all new code for consistent style

### Error Handling & Logging

- [ ] **T147** [Polish] Review all exception handling: ensure proper error messages, clean up resources, log to monitoring database
- [ ] **T148** [Polish] Add structured logging with correlation IDs to trace operations across components
- [ ] **T149** [Polish] Implement graceful degradation: continue processing even if individual stocks fail, collect errors for review

### Security & Validation

- [ ] **T150** [P] [Polish] Validate all user inputs: strategy parameters, date ranges, file paths, prevent injection attacks
- [ ] **T151** [P] [Polish] Add rate limiting for API endpoints (if exposing via web API)
- [ ] **T152** [Polish] Review all database queries for SQL injection risks (should be minimal with ORM/parameterized queries)

### Example & Test Data

- [ ] **T153** [P] [Polish] Create sample TDX data files in `tests/fixtures/tdx_sample/` for testing import functionality
- [ ] **T154** [P] [Polish] Create sample strategy signals in `tests/fixtures/sample_signals.csv` for testing backtest
- [ ] **T155** [P] [Polish] Create expected backtest results in `tests/fixtures/expected_backtest.json` for validation

### Monitoring & Observability

- [ ] **T156** [Polish] Verify all operations logged to MonitoringDatabase: strategy executions, backtests, imports, errors
- [ ] **T157** [Polish] Add performance metrics tracking: execution time, throughput, error rate dashboards (if using Grafana)
- [ ] **T158** [Polish] Set up alerts for failures: strategy execution failures, backtest errors, import job failures

### Final Validation

- [ ] **T159** [Polish] Execute MVP test plan: run User Story 1 acceptance scenarios, verify all pass
- [ ] **T160** [Polish] Execute full test plan: run all user story acceptance scenarios (US1-US5), verify all pass
- [ ] **T161** [Polish] Performance benchmark: measure all success criteria, ensure all met or exceeded
- [ ] **T162** [Polish] User acceptance testing: have actual trader test complete workflow, collect feedback
- [ ] **T163** [Polish] Update CHANGELOG.md with feature release notes, breaking changes, migration guide

**Checkpoint**: Feature complete, tested, documented, ready for production deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
  - Completes with T001-T023 done
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
  - Completes with T024-T034 done
  - **⚠️ CRITICAL**: No user story work can begin until this phase is complete
- **User Story 1 (Phase 3)**: Depends on Foundational completion
  - Can start after T034 complete
  - Independent of US2, US3, US4, US5
- **User Story 2 (Phase 4)**: Depends on Foundational + US1 signal generation
  - Can start after T034 complete
  - Requires signals from US1 to backtest (but can use test data initially)
- **User Story 3 (Phase 5)**: Depends on Foundational + US1 signals
  - Can start after T034 complete
  - Requires signals from US1 to visualize (but can use test data initially)
- **User Story 4 (Phase 6)**: Depends on Foundational completion only
  - Can start after T034 complete
  - Independent of other user stories (provides alternative data source)
- **User Story 5 (Phase 7)**: Largely complete in Foundational phase
  - Refinements can happen anytime after T024-T027 complete
  - Independent of other user stories
- **Polish (Phase 8)**: Depends on desired user stories being complete
  - Minimum: After US1 complete for MVP polish
  - Full: After all US1-US5 complete

### User Story Dependencies

- **US1 → US2**: US1 generates signals needed for backtest (but US2 can use test signals initially)
- **US1 → US3**: US1 generates signals needed for visualization (but US3 can use test signals initially)
- **US4 → US1**: US4 imports data used by US1 (but US1 can use existing data initially)
- **Foundation → ALL**: All user stories depend on indicator library (T024-T027), base strategy (T028-T031), signal manager (T032-T034)

### Within Each User Story

**General Pattern**:
1. Prerequisites (models, data access)
2. Core implementation (main functionality)
3. Integration (connect to other components)
4. Examples (demonstrate usage)

**Specific Sequential Dependencies**:
- US1: T035-T037 (filtering) before T038-T048 (execution)
- US2: T054-T058 (engine) before T062-T064 (persistence)
- US3: T072-T075 (chart setup) before T076-T081 (signal rendering)
- US4: T092-T095 (parser) before T100-T104 (import), then T105-T107 (storage)

### Parallel Opportunities

**Within Setup (Phase 1)**:
- All dependency installs (T001-T004) can run in parallel
- All directory creation tasks (T006-T013) can run in parallel
- All env configuration tasks (T019-T022) can run in parallel

**Within Foundational (Phase 2)**:
- Indicator library tasks (T024-T025, T027) can run in parallel
- Strategy templates (T030-T031) can run in parallel after T028-T029

**Across User Stories** (if team has capacity):
- US1, US4, US5 can all start in parallel after Foundation complete
- US2, US3 can start slightly later (need test data from US1, but can use fixtures)

**Within Each User Story**:
- Tasks marked [P] in same phase can run in parallel
- Example: US3 tasks T076, T077, T078, T082, T083, T086, T087 all marked [P]

---

## Parallel Example: Phase 2 Foundation

```bash
# These can all launch together:
Task: "Implement indicators/tdx_functions.py with MA, SMA, HHV..."  (T024)
Task: "Implement indicators/talib_wrapper.py with TALibIndicators..." (T025)
Task: "Implement indicators/custom_indicators.py with templates..." (T027)

# After T028 completes, these can launch together:
Task: "Create momentum_template.py demonstrating MA crossover..." (T030)
Task: "Create mean_reversion_template.py demonstrating Bollinger Band..." (T031)
```

---

## Parallel Example: User Story 3

```bash
# These visualization tasks can all launch together (after T072-T075 complete):
Task: "Add tooltip/annotation support for signal details..." (T078)
Task: "Add moving average overlays using mplfinance..." (T082)
Task: "Add trend line support..." (T083)
Task: "Implement JPG export option..." (T086)
Task: "Add optional Plotly implementation..." (T087)
Task: "Implement chart_config.py with ChartConfiguration..." (T088)
Task: "Create examples/example_visualization.py..." (T090)
Task: "Add batch chart generation example..." (T091)
```

---

## Implementation Strategy

### MVP First (US1 Only) - Fastest Path to Value

**Recommended for solo developer or small team**:

1. **Week 1**: Complete Phase 1 (Setup) + Phase 2 (Foundation)
   - Days 1-2: T001-T023 (setup)
   - Days 3-5: T024-T034 (foundation)
2. **Week 2**: Complete Phase 3 (User Story 1)
   - Days 1-3: T035-T048 (strategy execution)
   - Days 4-5: T049-T053 (strategy management + examples)
3. **Week 3**: Polish MVP
   - Test, document, optimize US1
   - Deploy/demo to users
   - Collect feedback before building US2-US5

**Value Delivered**: Traders can execute custom strategies and generate signals - immediate productivity gain

### Incremental Delivery - Build Trust with Users

**Recommended for ongoing development**:

1. **Sprint 1** (2 weeks): Setup + Foundation + US1 → Deploy MVP
2. **Sprint 2** (2 weeks): US2 (Backtest) → Deploy backtesting capability
3. **Sprint 3** (1.5 weeks): US3 (Visualization) → Deploy chart generation
4. **Sprint 4** (1.5 weeks): US4 (TDX Import) → Deploy data import
5. **Sprint 5** (1 week): US5 refinements + Polish → Full feature complete

**Each sprint delivers working, testable increment**

### Parallel Team Strategy - Maximum Velocity

**Recommended for 3-4 developer team**:

1. **Sprint 1** (1 week): All devs collaborate on Setup + Foundation
   - Foundation is critical path, must be solid
2. **Sprint 2-3** (2 weeks): Split into parallel tracks
   - Dev A: US1 (Strategy Execution) - Most complex
   - Dev B: US4 (TDX Import) - Independent
   - Dev C: US5 (Indicator refinements) - Independent
3. **Sprint 4** (2 weeks): Next wave
   - Dev A: US2 (Backtest) - Depends on US1 signals
   - Dev B: US3 (Visualization) - Depends on US1 signals
   - Dev C: Polish & integration testing
4. **Sprint 5** (1 week): Final polish, full integration, deployment

**Benefits**: User stories complete in parallel, faster delivery

---

## Task Count Summary

- **Phase 1 (Setup)**: 23 tasks (T001-T023)
- **Phase 2 (Foundation)**: 11 tasks (T024-T034) - CRITICAL PATH
- **Phase 3 (US1 - Strategy Execution)**: 19 tasks (T035-T053) - MVP
- **Phase 4 (US2 - Backtest)**: 18 tasks (T054-T071)
- **Phase 5 (US3 - Visualization)**: 20 tasks (T072-T091)
- **Phase 6 (US4 - TDX Import)**: 24 tasks (T092-T115)
- **Phase 7 (US5 - Indicators)**: 16 tasks (T116-T131)
- **Phase 8 (Polish)**: 32 tasks (T132-T163)

**Total**: 163 tasks

**Parallel Tasks**: 68 tasks marked [P] (42% can run in parallel given dependencies met)

**MVP Scope** (minimum for production):
- Phase 1 + 2 + 3 = 53 tasks (1-3 weeks for experienced developer)

**Full Feature** (all user stories):
- All phases = 163 tasks (6-10 weeks for solo developer, 4-6 weeks for 3-dev team)

---

## Notes

- **[P] tasks** = Different files, no dependencies within phase - can run in parallel
- **[Story] labels** = Maps task to user story for traceability and independent testing
- **Foundation phase is CRITICAL** - No shortcuts, all user stories depend on it
- **Each user story should be independently completable** - Can stop after any US and have working feature
- **Commit after logical groups** - Don't commit half-complete features
- **Stop at checkpoints** - Validate story independently before moving forward
- **Use test fixtures** - Create sample data to test US2/US3 before US1 signals exist
- **Follow constitution** - All data operations via UnifiedDataManager, all monitoring to MonitoringDatabase
- **Performance matters** - Profile early, optimize hot paths, cache aggressively
- **Document as you go** - Docstrings, examples, troubleshooting tips save time later

---

## Success Validation Checklist

After implementation, verify these success criteria:

- [ ] **SC-001**: Execute strategy on 1000 stocks in <10 minutes ✓
- [ ] **SC-002**: Strategy signals 100% accurate vs manual calculation ✓
- [ ] **SC-003**: Backtest 5-year data in <5 seconds (exceeds <5 minute requirement) ✓
- [ ] **SC-004**: Backtest metrics <0.1% deviation from expected ✓
- [ ] **SC-005**: Chart renders in <0.3 seconds (exceeds <3 second requirement) ✓
- [ ] **SC-006**: TDX import 3000 files in <30 minutes ✓
- [ ] **SC-007**: Incremental TDX update in <2 minutes ✓
- [ ] **SC-008**: Indicators 10x faster than pandas ✓
- [ ] **SC-009**: 3 concurrent strategies without degradation ✓
- [ ] **SC-010**: 95% execution success rate ✓
- [ ] **SC-011**: Charts support zoom/pan smoothly ✓
- [ ] **SC-012**: Signal queries <1 second ✓

---

**Ready to implement!** Start with Phase 1 (Setup), then Phase 2 (Foundation), then pick a user story based on priority and team capacity.
