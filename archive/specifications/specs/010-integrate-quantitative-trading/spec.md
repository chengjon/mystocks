# Feature Specification: Quantitative Trading Integration

**Feature Branch**: `010-integrate-quantitative-trading`
**Created**: 2025-10-18
**Status**: Draft
**Input**: User description: "Integrate quantitative trading capabilities: strategy engine with custom stock screening strategies, technical indicator library (TDX functions and TA-Lib), multi-process strategy executor, RQAlpha-based backtesting system with performance metrics, PyECharts K-line visualization with buy/sell signal markers, TDX local data adapter for reading Tongdaxin software data files, and strategy signal management with PostgreSQL storage"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Execute Custom Stock Screening Strategy (Priority: P1)

A quantitative trader wants to execute their custom stock screening strategy against a pool of stocks to identify trading opportunities based on technical indicators and market conditions.

**Why this priority**: This is the core MVP functionality - without the ability to execute strategies and generate signals, all other features have no value. This delivers immediate value by automating the stock screening process.

**Independent Test**: Can be fully tested by defining a simple moving average crossover strategy, executing it against a test stock pool, and verifying that buy/sell signals are correctly generated and stored.

**Acceptance Scenarios**:

1. **Given** a trader has defined a custom strategy with technical indicators, **When** they execute the strategy against a stock pool of 100 stocks, **Then** the system generates buy/sell signals for stocks meeting the criteria within 5 minutes
2. **Given** strategy execution is in progress, **When** the trader monitors progress, **Then** they see real-time progress updates showing stocks processed and signals found
3. **Given** strategy execution completes, **When** the trader views results, **Then** they see a list of stocks with signal types (buy/sell), signal strength, and timestamp
4. **Given** multiple strategies are defined, **When** the trader selects a specific strategy to execute, **Then** only that strategy runs against the stock pool
5. **Given** a strategy execution fails on specific stocks, **When** reviewing results, **Then** the trader sees error details for failed stocks while successful signals are still saved

---

### User Story 2 - Backtest Strategy Performance (Priority: P2)

A quantitative trader wants to backtest their strategy against historical data to evaluate performance metrics before deploying it with real capital.

**Why this priority**: Backtesting is essential for validating strategies before live trading. This prevents capital loss from unproven strategies and builds trader confidence.

**Independent Test**: Can be tested by running a backtest on a known historical period with a simple strategy, then verifying that performance metrics (returns, drawdown, Sharpe ratio) are accurately calculated and match expected values.

**Acceptance Scenarios**:

1. **Given** a trader has generated strategy signals for a historical period, **When** they run a backtest with 100,000 initial capital, **Then** the system simulates trades and generates a performance report showing total return, annualized return, max drawdown, and Sharpe ratio
2. **Given** backtest is configured with commission and slippage parameters, **When** the backtest executes, **Then** all simulated trades include realistic transaction costs
3. **Given** a backtest completes successfully, **When** the trader views results, **Then** they see a detailed trade log showing entry/exit dates, prices, quantities, and P&L for each trade
4. **Given** multiple backtests are run with different parameters, **When** comparing results, **Then** the trader can view side-by-side comparison of performance metrics
5. **Given** a benchmark index is specified, **When** backtest completes, **Then** the results include comparative performance against the benchmark

---

### User Story 3 - Visualize Strategy Signals on K-Line Charts (Priority: P3)

A quantitative trader wants to visualize their strategy signals overlaid on stock K-line charts to understand the market context of buy/sell decisions.

**Why this priority**: Visualization helps traders understand why their strategy generated signals at specific points, enabling strategy refinement and building intuition about market patterns.

**Independent Test**: Can be tested by generating a K-line chart for a stock with known buy/sell signals, then verifying that signals are correctly marked on the chart with proper colors, holding period highlighting, and profit/loss indication.

**Acceptance Scenarios**:

1. **Given** a stock has generated buy/sell signals, **When** the trader requests a K-line chart, **Then** the chart displays candlesticks with buy signals marked at the bottom and sell signals at the top
2. **Given** a K-line chart is displayed, **When** the trader hovers over a signal marker, **Then** they see detailed information including signal date, price, and strategy parameters
3. **Given** multiple buy/sell signal pairs exist, **When** viewing the chart, **Then** holding periods are highlighted with green for profitable trades and red for losses
4. **Given** the chart has hundreds of data points, **When** the trader zooms or pans, **Then** the chart responds smoothly with interactive controls
5. **Given** chart is generated, **When** the trader exports it, **Then** they can save it as an interactive HTML file or static image

---

### User Story 4 - Import Data from Tongdaxin Software (Priority: P4)

A quantitative trader using Tongdaxin (TDX) desktop software wants to import their local market data files into the system to leverage existing data without re-downloading from APIs.

**Why this priority**: Many Chinese traders already use Tongdaxin and have comprehensive local data. This integration provides an alternative data source and reduces dependency on network APIs.

**Independent Test**: Can be tested by pointing the adapter to a sample TDX installation directory, importing daily bar data and financial data, then verifying the imported data matches TDX software displays and is correctly stored in the database.

**Acceptance Scenarios**:

1. **Given** a trader has Tongdaxin software installed with downloaded data, **When** they configure the TDX data path, **Then** the system automatically discovers available stock data files
2. **Given** TDX data files are discovered, **When** the trader initiates import, **Then** the system reads .day files, applies forward adjustment for splits/dividends, and stores processed data
3. **Given** import is in progress, **When** monitoring progress, **Then** the trader sees how many stocks have been processed and estimated time remaining
4. **Given** financial data and equity change data exist in TDX format, **When** importing, **Then** the system also imports these datasets and links them to corresponding stocks
5. **Given** daily updates are needed, **When** the trader runs incremental import, **Then** only new data since last import is processed, saving time

---

### User Story 5 - Calculate Technical Indicators (Priority: P5)

A quantitative trader wants to use technical indicators (moving averages, RSI, MACD, etc.) in their strategy logic to make trading decisions based on market momentum and trends.

**Why this priority**: Technical indicators are foundational building blocks for most quantitative strategies. This enables traders to express complex trading logic using standard financial analysis tools.

**Independent Test**: Can be tested by calculating a simple moving average on test data with known values, verifying the calculation matches expected results, then testing indicator composition in a strategy.

**Acceptance Scenarios**:

1. **Given** a trader is writing a strategy, **When** they call MA(close, 20), **Then** the system calculates a 20-period moving average using vectorized computation
2. **Given** TDX-style functions are available (MA, SMA, HHV, LLV, CROSS, etc.), **When** the trader uses them in strategy code, **Then** they produce identical results to Tongdaxin software calculations
3. **Given** TA-Lib indicators are also available, **When** the trader prefers standard technical analysis, **Then** they can use indicators like RSI, MACD, Bollinger Bands
4. **Given** indicators are calculated, **When** strategy execution processes thousands of stocks, **Then** calculations leverage numpy vectorization for performance
5. **Given** custom indicators are needed, **When** the trader defines a new indicator function, **Then** they can reuse it across multiple strategies

---

### Edge Cases

- What happens when a TDX data file is corrupted or partially written (e.g., during market hours)?
- How does the system handle stocks with insufficient historical data for indicator calculation (e.g., newly listed stocks)?
- What occurs when strategy execution encounters a stock with no trading volume on signal date?
- How are corporate actions (splits, mergers, delistings) handled during backtesting?
- What happens when multiple strategies generate conflicting signals for the same stock on the same day?
- How does the system handle timezone differences between market data and strategy execution time?
- What occurs when backtest period spans dates where some stocks didn't exist yet?
- How are dividends and distributions accounted for in backtest returns?
- What happens when a strategy tries to buy a stock that is halted or suspended?
- How does the system handle memory constraints when processing strategies across 5000+ stocks?

## Requirements *(mandatory)*

### Functional Requirements

**Strategy Engine**

- **FR-001**: System MUST provide a base strategy class that users can inherit from to define custom stock screening logic
- **FR-002**: System MUST support strategy execution in both fast mode (current day only) and full mode (historical period)
- **FR-003**: System MUST execute strategies across stock pools using multi-process parallelization to improve performance
- **FR-004**: System MUST filter out excluded stock categories (ST stocks, specific industries, specific board types) before strategy execution
- **FR-005**: System MUST save generated buy/sell signals with timestamp, stock symbol, signal type, signal strength, and strategy name
- **FR-006**: System MUST retrieve stock data from the unified data manager rather than directly from files
- **FR-007**: System MUST provide progress tracking showing stocks processed, signals found, and estimated completion time

**Technical Indicator Library**

- **FR-008**: System MUST provide TDX-compatible functions including MA, SMA, HHV, LLV, COUNT, EXIST, CROSS, BARSLAST, REF
- **FR-009**: System MUST integrate TA-Lib library for standard technical indicators (RSI, MACD, Bollinger Bands, ATR, etc.)
- **FR-010**: System MUST perform indicator calculations using numpy vectorization for performance on large datasets
- **FR-011**: System MUST cache calculated indicator values to avoid redundant computation during strategy execution
- **FR-012**: System MUST handle edge cases where insufficient data exists for indicator calculation (return NaN or skip stock)

**Backtesting System**

- **FR-013**: System MUST integrate with RQAlpha framework to execute strategy backtests
- **FR-014**: System MUST prepare data bundles for RQAlpha from the unified data manager's database rather than external sources
- **FR-015**: System MUST support configurable backtest parameters including initial capital, commission rate, slippage, and benchmark index
- **FR-016**: System MUST generate performance metrics including total return, annualized return, maximum drawdown, Sharpe ratio, and win rate
- **FR-017**: System MUST save backtest results to PostgreSQL database with full trade log and performance metrics in JSONB format
- **FR-018**: System MUST generate equity curve charts comparing strategy performance against benchmark
- **FR-019**: System MUST handle corporate actions during backtest period using forward-adjusted price data
- **FR-020**: System MUST respect trading rules (no buying halted stocks, handling position limits, etc.)

**Visualization Module**

- **FR-021**: System MUST generate interactive K-line charts using PyECharts library
- **FR-022**: System MUST mark buy signals at chart bottom and sell signals at chart top with distinct visual markers
- **FR-023**: System MUST highlight holding periods between buy/sell pairs with color coding (green for profit, red for loss)
- **FR-024**: System MUST overlay trend lines and support/resistance levels on charts when requested
- **FR-025**: System MUST support chart export as both interactive HTML and static image formats
- **FR-026**: System MUST provide zoom, pan, and tooltip interactions on charts
- **FR-027**: System MUST retrieve chart data from database rather than CSV files

**TDX Data Adapter**

- **FR-028**: System MUST read Tongdaxin .day binary files and convert to standard OHLCV format
- **FR-029**: System MUST read Tongdaxin financial data files and equity change data files
- **FR-030**: System MUST apply forward adjustment calculations using equity change data to match TDX software display
- **FR-031**: System MUST store imported TDX data into appropriate databases using the 5-tier classification system (market data → TDengine, financial data → PostgreSQL, etc.)
- **FR-032**: System MUST support incremental updates to only import new data since last import
- **FR-033**: System MUST handle data validation and error reporting for corrupted TDX files
- **FR-034**: System MUST integrate with pytdx library to fetch real-time quotes when needed

**Data Management Integration**

- **FR-035**: System MUST store strategy signals in PostgreSQL as derived data classification
- **FR-036**: System MUST store backtest results in PostgreSQL with JSONB column for detailed metrics
- **FR-037**: System MUST create appropriate table structures in table_config.yaml for new data entities
- **FR-038**: System MUST leverage the unified data manager for all data retrieval operations
- **FR-039**: System MUST log all strategy executions and backtests to the monitoring database
- **FR-040**: System MUST track performance metrics for strategy execution (execution time, stocks processed per second, etc.)

### Key Entities

- **Strategy**: Represents a custom stock screening algorithm with parameters, entry/exit logic, and metadata (name, version, creation date)
- **Signal**: Represents a buy or sell signal generated by a strategy for a specific stock on a specific date, including signal strength and strategy identifier
- **Backtest Result**: Represents the outcome of a historical strategy backtest, including performance metrics (returns, drawdown, Sharpe ratio), trade log, and equity curve data
- **Technical Indicator**: Represents a calculated technical analysis metric (moving average, momentum, volatility) derived from price/volume data
- **TDX Data Import Job**: Represents an import operation from Tongdaxin local files, tracking import progress, files processed, and errors encountered
- **Chart Configuration**: Represents visualization settings for K-line charts, including date range, indicators to overlay, and signal markers to display

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Traders can define and execute a custom strategy against 1000 stocks in under 10 minutes using multi-process execution
- **SC-002**: Strategy signals are generated with 100% accuracy compared to manual calculation for test cases
- **SC-003**: Backtest execution completes for a 5-year historical period with daily data in under 5 minutes
- **SC-004**: Backtest performance metrics match manual calculation with less than 0.1% deviation
- **SC-005**: K-line charts with signal markers render in under 3 seconds for 2 years of daily data
- **SC-006**: TDX data import processes 3000 stock files in under 30 minutes on initial full import
- **SC-007**: Incremental TDX data updates complete in under 2 minutes for daily market close data
- **SC-008**: Technical indicator calculations perform at least 10x faster than pandas rolling operations using numpy vectorization
- **SC-009**: System handles concurrent execution of 3 different strategies without performance degradation
- **SC-010**: 95% of strategy executions complete without errors or crashes
- **SC-011**: All generated charts are interactive and support zoom/pan operations smoothly
- **SC-012**: Strategy results stored in database are queryable with response time under 1 second for historical signal lookups

## Assumptions

- Traders using this feature have basic Python programming knowledge to write strategy logic
- Tongdaxin software data is already downloaded and available locally for TDX adapter users
- PostgreSQL database has sufficient storage for historical signals (estimated 1GB per year for 3000 stocks)
- TDengine is the primary storage for market data as per existing MyStocks architecture
- RQAlpha framework is compatible with data provided by the unified data manager
- PyECharts library supports the chart customization requirements (buy/sell markers, holding period highlights)
- Multi-process execution is available (system has at least 4 CPU cores)
- Network access is available for pytdx real-time quote functionality
- Users understand basic quantitative trading concepts (backtesting, Sharpe ratio, drawdown)

## Dependencies

- Existing MyStocks unified data manager must be operational
- PostgreSQL database must be configured and accessible
- TDengine database must be configured for market data storage
- Python environment must support new dependencies: PyECharts, RQAlpha, pytdx, TA-Lib
- For TDX adapter: Tongdaxin software installation directory must be accessible to the system
- Table configuration must be updated to include new entity tables (strategy_signals, backtest_results)

## Out of Scope

- Real-time automated trading execution (this feature only generates signals, not executes trades)
- Machine learning-based strategy optimization
- Portfolio optimization and position sizing algorithms
- Risk management modules (stop-loss, position limits)
- Multi-asset backtesting (only stocks, no futures/options/forex)
- Paper trading or simulated trading environment
- Mobile app visualization
- Real-time streaming market data processing
- Integration with brokerage APIs for order placement
- Advanced backtesting features like slippage modeling based on order book depth
