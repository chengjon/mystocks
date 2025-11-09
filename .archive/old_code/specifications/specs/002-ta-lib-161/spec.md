# Feature Specification: Technical Analysis with 161 Indicators

**Feature Branch**: `002-ta-lib-161`
**Created**: 2025-10-13
**Status**: Draft
**Input**: User description: "技术分析功能 - 基于TA-Lib实现161个技术指标的计算和可视化展示。前端使用Vue3+Element Plus+klinecharts展示K线图和技术指标叠加，后端使用FastAPI+TA-Lib进行指标计算。支持股票搜索、时间范围选择、多指标组合分析。指标分类包括：趋势指标(MA/EMA/MACD/ADX等)、动量指标(RSI/KDJ/CCI等)、波动率指标(ATR/BBANDS等)、成交量指标(OBV/AD等)和K线形态识别(CDL系列)。数据接口基于现有的GET /api/data/stocks/daily端点获取OHLCV数据。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Stock with Basic Trend Indicators (Priority: P1)

A trader opens the technical analysis page, searches for a stock (e.g., "600519"), selects a date range (last 3 months), and applies basic moving averages (MA5, MA10, MA20) to understand price trends. The K-line chart displays with the selected indicators overlaid, allowing quick identification of support/resistance levels.

**Why this priority**: This is the core MVP functionality that delivers immediate value. Users can perform basic technical analysis with the most commonly used indicators. Without this, the feature provides no value.

**Independent Test**: Can be fully tested by selecting a stock, choosing a date range, applying MA indicators, and verifying the chart displays correctly with indicator lines overlaid on price data.

**Acceptance Scenarios**:

1. **Given** user is on the technical analysis page, **When** user searches for "600519" and selects last 90 days with MA5/MA10/MA20 indicators, **Then** K-line chart displays with three moving average lines in different colors overlaid on candlesticks
2. **Given** chart is displayed with indicators, **When** user hovers over any data point, **Then** tooltip shows date, OHLC values, and all indicator values at that point
3. **Given** user has applied indicators, **When** user changes date range to last 6 months, **Then** chart refreshes with same indicators calculated for new time period
4. **Given** user searches for invalid stock code, **When** search is submitted, **Then** system shows friendly error message and suggests valid alternatives

---

### User Story 2 - Apply Momentum and Oscillator Indicators (Priority: P2)

A trader wants to identify overbought/oversold conditions using momentum indicators like RSI, KDJ, and CCI. They add these indicators to a separate panel below the main price chart, with horizontal reference lines (e.g., RSI 30/70 levels) to quickly spot trading signals.

**Why this priority**: Extends basic functionality with the second most common indicator category. Momentum indicators are essential for timing entries/exits but require the base charting from P1 to be useful.

**Independent Test**: After P1 is complete, can be tested by applying RSI/KDJ/CCI indicators and verifying they appear in separate panels below the main chart with correct scaling and reference lines.

**Acceptance Scenarios**:

1. **Given** stock chart is displayed, **When** user adds RSI(14) indicator, **Then** new panel appears below main chart showing RSI line with 30/70 reference lines
2. **Given** RSI panel is displayed, **When** RSI value crosses above 70, **Then** the crossing point is visually highlighted
3. **Given** user has multiple indicator panels, **When** user reorders panels by dragging, **Then** panels rearrange accordingly
4. **Given** user applies KDJ indicator, **When** chart updates, **Then** three lines (K, D, J) are displayed in different colors in a dedicated panel

---

### User Story 3 - Compare Multiple Stocks with Same Indicators (Priority: P3)

An analyst wants to compare the technical characteristics of multiple stocks (e.g., sector comparison). They open multiple charts side-by-side, apply the same set of indicators (MA20, RSI, MACD) to all charts, and synchronize the time range to identify relative strength across stocks.

**Why this priority**: Advanced feature for professional users. Requires both P1 and P2 to be functional and adds comparison capabilities that power users need but casual users can skip.

**Independent Test**: Can be tested by opening 2-4 stock charts simultaneously, applying identical indicator sets, and verifying synchronized scrolling and time range selection works across all charts.

**Acceptance Scenarios**:

1. **Given** user has one chart displayed, **When** user clicks "Add comparison chart" and selects another stock, **Then** second chart appears side-by-side with same time range
2. **Given** multiple charts are displayed, **When** user scrolls or zooms one chart, **Then** all charts synchronize their time range and zoom level
3. **Given** user applies indicator set to first chart, **When** user clicks "Apply to all charts", **Then** all comparison charts display the same indicators
4. **Given** 4 charts are displayed, **When** user changes time range on any chart, **Then** all charts update to match the new time range

---

### User Story 4 - Save and Load Indicator Configurations (Priority: P3)

A trader has developed a preferred set of indicators for different analysis types (e.g., "Day Trading Setup", "Long-term Trend", "Breakout Scanner"). They want to save these configurations and quickly apply them to any stock without reconfiguring indicators each time.

**Why this priority**: Quality-of-life improvement that enhances productivity for frequent users. Depends on P1 and P2 being stable and provides value primarily to power users who analyze many stocks daily.

**Independent Test**: Can be tested by creating a custom indicator configuration, saving it with a name, closing the session, reopening, and verifying the saved configuration can be loaded and applied to any stock.

**Acceptance Scenarios**:

1. **Given** user has configured 5 indicators on a chart, **When** user clicks "Save configuration" and names it "My Setup", **Then** configuration is saved and appears in saved configurations list
2. **Given** user opens a different stock, **When** user selects "My Setup" from saved configurations, **Then** all 5 indicators are applied automatically
3. **Given** user has 10 saved configurations, **When** user views configuration list, **Then** each configuration shows name, indicator count, and last used date
4. **Given** user wants to modify a saved configuration, **When** user loads it, changes indicators, and saves with same name, **Then** configuration is updated

---

### User Story 5 - Identify Candlestick Patterns Automatically (Priority: P2)

A trader analyzing potential reversal points wants the system to automatically detect and highlight candlestick patterns (e.g., Doji, Hammer, Engulfing patterns) on the chart. Pattern detections are marked with icons and labels, and a summary panel lists all detected patterns with dates and pattern confidence.

**Why this priority**: Highly valuable for pattern-based traders and differentiates the feature from basic charting tools. Can be implemented independently after P1 since pattern detection is a separate analysis layer.

**Independent Test**: Can be tested by loading a stock with known candlestick patterns, enabling pattern detection, and verifying the system correctly identifies and marks patterns with appropriate labels and confidence scores.

**Acceptance Scenarios**:

1. **Given** chart is displayed, **When** user enables "Candlestick Pattern Detection", **Then** all detected patterns are marked with icons on relevant candles
2. **Given** patterns are detected, **When** user clicks on a pattern icon, **Then** tooltip shows pattern name, type (bullish/bearish), and confidence score
3. **Given** multiple patterns are detected, **When** user views pattern summary panel, **Then** panel lists all patterns chronologically with dates and pattern types
4. **Given** user filters patterns by type, **When** filter is applied (e.g., "only bullish patterns"), **Then** chart and summary panel show only matching patterns

---

### Edge Cases

- What happens when user selects a date range with insufficient data points for indicator calculation (e.g., MA200 but only 50 days of data)?
  - System should show warning message and suggest minimum data requirements for selected indicators
- How does system handle stocks with missing trading days (holidays, suspensions)?
  - System should skip missing days in calculation and display gaps in the chart appropriately
- What happens when user applies too many indicators causing performance degradation?
  - System should limit maximum concurrent indicators (e.g., 10) and show warning when limit is reached
- How does system handle real-time data updates during active trading hours?
  - Assumed: Feature works with historical data only; real-time updates are out of scope for this feature
- What happens when indicator calculation fails (e.g., division by zero, invalid data)?
  - System should show indicator-specific error message and continue displaying other indicators successfully
- How does system handle very long date ranges (e.g., 10 years of daily data)?
  - System should implement pagination or data windowing, loading data progressively as user scrolls

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to search for stocks by code or name with autocomplete suggestions
- **FR-002**: System MUST support date range selection with preset options (1M, 3M, 6M, 1Y, YTD, All) and custom range picker
- **FR-003**: System MUST display K-line chart with OHLC candlesticks and volume bars
- **FR-004**: System MUST provide categorized indicator library with 5 categories: Trend, Momentum, Volatility, Volume, Candlestick Patterns
- **FR-005**: System MUST calculate and display all indicators in the Trend category: MA (multiple periods), EMA (multiple periods), MACD, ADX, SAR, BBANDS, TEMA, TRIMA, WMA, KAMA, MAMA, T3
- **FR-006**: System MUST calculate and display all indicators in the Momentum category: RSI, KDJ, CCI, MFI, STOCH, STOCHF, STOCHRSI, WILLR, ROC, CMO, AROON, AROONOSC, MOM, BOP, PPO, TRIX, ULTOSC, DX, PLUS_DI, MINUS_DI, ADX, ADXR
- **FR-007**: System MUST calculate and display all indicators in the Volatility category: ATR, NATR, TRANGE, BBANDS (width and %B)
- **FR-008**: System MUST calculate and display all indicators in the Volume category: OBV, AD, ADOSC, MFI
- **FR-009**: System MUST detect and display all candlestick patterns in the Candlestick category: all CDL series patterns (61+ patterns including Doji, Hammer, Engulfing, Harami, Morning Star, Evening Star, etc.)
- **FR-010**: System MUST allow users to add multiple indicators simultaneously to the chart
- **FR-011**: System MUST display overlay indicators (MA, EMA, BBANDS) directly on the price chart
- **FR-012**: System MUST display oscillator indicators (RSI, KDJ, MACD) in separate panels below the price chart
- **FR-013**: System MUST allow users to customize indicator parameters (e.g., MA period, RSI period) before applying
- **FR-014**: System MUST show indicator values in tooltip when hovering over any data point
- **FR-015**: System MUST provide zoom and pan controls for chart navigation
- **FR-016**: System MUST allow users to remove individual indicators from the chart
- **FR-017**: System MUST persist selected stock and indicators during user session
- **FR-018**: System MUST display loading indicator while fetching data or calculating indicators
- **FR-019**: System MUST show clear error messages when data retrieval or calculation fails
- **FR-020**: System MUST display indicator legends with color coding matching chart lines
- **FR-021**: System MUST allow users to toggle indicator visibility without removing them
- **FR-022**: System MUST support exporting chart as image (PNG/JPG) with indicators included
- **FR-023**: System MUST validate date range ensuring start date is before end date
- **FR-024**: System MUST show indicator calculation warnings when insufficient data points exist
- **FR-025**: System MUST retrieve OHLCV data from existing data interface (GET /api/data/stocks/daily endpoint)
- **FR-026**: System MUST provide indicator abbreviation names as feature identifiers (e.g., "MA", "RSI", "MACD")
- **FR-027**: System MUST limit maximum concurrent indicators to 10 to ensure performance
- **FR-028**: System MUST support saving indicator configurations with user-defined names
- **FR-029**: System MUST support loading and applying saved indicator configurations to any stock
- **FR-030**: System MUST list all saved configurations with metadata (name, indicator count, last used date)

### Key Entities

- **Stock**: Represents a tradeable security with attributes including stock code, name, market, and associated price history
- **Price Data**: Time-series data containing date, open, high, low, close, volume, and amount for each trading day
- **Indicator**: A calculated technical analysis metric with attributes including type (overlay/oscillator), category (trend/momentum/volatility/volume/pattern), name, parameters, and calculated values
- **Indicator Configuration**: A saved set of indicators with their parameters, associated with a user-defined name and metadata (created date, last used date)
- **Chart**: The visual representation combining price data, selected indicators, and user interaction state (zoom level, selected date range, visible panels)
- **Candlestick Pattern**: A detected formation in price data with attributes including pattern type, date, direction (bullish/bearish), and confidence score

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can select a stock and apply basic trend indicators (MA5, MA10, MA20) with chart displayed in under 3 seconds
- **SC-002**: System successfully calculates and displays at least 150 of the 161 available indicators without errors
- **SC-003**: Users can apply up to 10 indicators simultaneously without noticeable performance degradation (chart interaction remains under 100ms response time)
- **SC-004**: 90% of users successfully complete their first technical analysis (select stock, apply indicators, view chart) within 5 minutes without assistance
- **SC-005**: System correctly identifies and displays at least 50 candlestick patterns with visual markers on the chart
- **SC-006**: Chart rendering and indicator calculation completes within 2 seconds for date ranges up to 1 year of daily data
- **SC-007**: Users can customize indicator parameters and see updated calculations within 1 second
- **SC-008**: System provides clear error messages for 100% of failure scenarios (invalid stock, insufficient data, calculation errors) with actionable guidance
- **SC-009**: Saved indicator configurations can be applied to any stock and load within 1 second
- **SC-010**: Chart zoom and pan interactions respond instantly (under 50ms) even with 10 indicators displayed
- **SC-011**: Exported chart images include all active indicators with clear legends and maintain visual quality (minimum 1200x800 resolution)
- **SC-012**: System handles stocks with up to 10 years of daily data (approximately 2500 data points) without performance issues

### Assumptions

- Users have basic understanding of technical analysis concepts and indicator meanings
- Historical stock data is available through existing data interface with consistent OHLCV format
- Indicator calculations are performed server-side to maintain consistency and reduce client-side processing load
- Chart library (klinecharts) supports required visualization features including multiple panels and indicator overlays
- Users access the feature through modern web browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
- Network latency between client and server is reasonable (under 500ms for typical requests)
- Stock data quality is sufficient for indicator calculations (no excessive missing data or anomalies)
- Users primarily analyze daily timeframe data; intraday data (minute/tick) is out of scope for initial release
- Real-time data updates during trading hours are out of scope; feature focuses on historical analysis
- Authentication and authorization are handled by existing system; technical analysis respects existing user permissions
- Data retention follows existing system policies; technical analysis does not introduce new data storage requirements
- Performance targets assume standard hardware (quad-core CPU, 8GB RAM, modern GPU) and stable network connection

### Dependencies

- Existing data API endpoint (GET /api/data/stocks/daily) must provide reliable OHLCV data
- Stock search functionality must integrate with existing stock listing database
- User session management must be in place to support configuration persistence
- Chart export functionality depends on browser canvas API support

### Scope Boundaries

**In Scope:**
- 161 technical indicators from TA-Lib library organized in 5 categories
- K-line chart visualization with candlesticks and volume bars
- Interactive chart with zoom, pan, and hover interactions
- Multiple indicator panels for oscillators
- Indicator parameter customization
- Save and load indicator configurations
- Chart export as image
- Candlestick pattern detection and visualization
- Date range selection and validation
- Error handling and user guidance
- Daily timeframe analysis

**Out of Scope:**
- Real-time data streaming and live updates during trading hours
- Intraday timeframes (minute, tick, second bars)
- Custom indicator creation or scripting
- Backtesting functionality (covered by separate feature)
- Alert creation based on indicator conditions
- Social features (sharing analysis, commenting)
- Mobile app version (web interface only)
- Multi-chart workspace with more than 4 simultaneous charts
- Advanced drawing tools (trendlines, fibonacci, etc.)
- Market scanning or screening based on indicators
- Portfolio-level technical analysis
- Integration with trading execution (place orders from chart)
