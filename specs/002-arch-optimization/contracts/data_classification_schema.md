# API Contract: Data Classification Schema

**Feature**: Architecture Optimization for Quantitative Trading System
**Branch**: `002-arch-optimization`
**Date**: 2025-10-25
**Contract Type**: Data Classification System (Architectural Foundation)

## Overview

This contract defines the simplified 10-category data classification system that serves as the foundation for automatic database routing, caching strategy, and query optimization. The classification reduces complexity from 34 categories to 10 essential categories while maintaining full support for professional quantitative analysis.

## Design Principles

**1. Business-Oriented**: Classifications map to real-world trading scenarios, not technical storage details

**2. Mutually Exclusive**: Each data type belongs to exactly one classification

**3. Database-Agnostic at API Level**: Classification determines routing, but API users don't need to know target database

**4. Performance-Driven**: Classification influences caching strategy and query optimization

**5. Chinese Market Focus**: Explicit support for industry sectors, concept plates, capital flow, chip distribution

---

## DataClassification Enum

### Complete Definition

```python
from enum import Enum

class DataClassification(Enum):
    """
    Simplified 10-category data classification for MyStocks system.

    Each classification automatically determines:
    - Target database (TDengine or PostgreSQL)
    - Caching strategy (TTL, invalidation rules)
    - Query optimization hints
    - Storage optimization (compression, partitioning)
    """

    # ============================================================================
    # Category 1: High-Frequency Time-Series Data
    # ============================================================================

    HIGH_FREQUENCY = "high_frequency"
    """
    Ultra-high frequency tick and minute-level data.

    **Data Types**:
    - Tick data (Level-2 market data)
    - 1-minute K-lines
    - 5-minute K-lines
    - 15-minute K-lines
    - 30-minute K-lines
    - 60-minute K-lines
    - Real-time depth data (10-level bid/ask)

    **Target Database**: TDengine
    **Rationale**: 20:1 compression ratio, ultra-high write throughput (>1M rows/s)

    **Storage Strategy**:
    - Hot data: Recent 3 months in TDengine
    - Cold data: Older than 3 months archived to PostgreSQL

    **Cache Strategy**:
    - Real-time: TTL = 1 second
    - Minute bars (current day): TTL = 5 minutes
    - Historical: Cache indefinitely

    **Query Patterns**:
    - Recent data: Direct TDengine query (hot tier)
    - Historical data: PostgreSQL archive query (cold tier)
    - Cross-tier query: Automatic merge from both databases

    **Example Usage**:
    ```python
    # Tick data
    manager.save_data("600000", "tick", tick_df,
                     classification=DataClassification.HIGH_FREQUENCY)

    # 5-minute K-line
    manager.save_data("600000", "kline_5min", kline_df,
                     classification=DataClassification.HIGH_FREQUENCY)
    ```
    """

    # ============================================================================
    # Category 2: Historical K-Line Data
    # ============================================================================

    HISTORICAL_KLINE = "historical_kline"
    """
    Daily, weekly, monthly K-line data.

    **Data Types**:
    - Daily K-lines
    - Weekly K-lines
    - Monthly K-lines
    - Adjusted factors (复权因子)

    **Target Database**: PostgreSQL (with TimescaleDB extension)
    **Rationale**: Complex time-range queries, JOIN with other tables, TimescaleDB optimization

    **Storage Strategy**:
    - All data in PostgreSQL
    - TimescaleDB hypertable with automatic partitioning
    - Compression for data older than 1 year

    **Cache Strategy**:
    - Historical (>1 day old): Cache indefinitely (immutable)
    - Current day: TTL = 5 minutes (updates during trading)

    **Query Patterns**:
    - Date range queries with symbol filter
    - Multi-symbol batch queries
    - Technical indicator calculations

    **Example Usage**:
    ```python
    # Daily K-line
    manager.save_data("600000", "kline_daily", daily_df,
                     classification=DataClassification.HISTORICAL_KLINE)

    # Weekly K-line
    manager.save_data("600000", "kline_weekly", weekly_df,
                     classification=DataClassification.HISTORICAL_KLINE)
    ```
    """

    # ============================================================================
    # Category 3: Real-Time Market Snapshots
    # ============================================================================

    REALTIME_SNAPSHOT = "realtime_snapshot"
    """
    Current market snapshot data (all stocks at once).

    **Data Types**:
    - Real-time quotes snapshot (full market)
    - Market breadth indicators (涨跌家数, 涨停/跌停统计)
    - Sector performance snapshot
    - Market sentiment indicators

    **Target Database**: PostgreSQL
    **Rationale**: Medium update frequency, complex filtering queries

    **Storage Strategy**:
    - Store latest snapshot + historical snapshots
    - Retain 3 months of snapshots
    - Older snapshots aggregated to daily summary

    **Cache Strategy**:
    - TTL = 3 seconds for snapshot queries
    - Invalidate on market close

    **Query Patterns**:
    - Current market status: SELECT latest snapshot
    - Historical snapshots: Time-range query
    - Filtering: WHERE price_change > 5% (strong gainers)

    **Example Usage**:
    ```python
    # Full market snapshot
    manager.save_data("ALL", "market_snapshot", snapshot_df,
                     classification=DataClassification.REALTIME_SNAPSHOT)
    ```
    """

    # ============================================================================
    # Category 4: Industry & Sector Data
    # ============================================================================

    INDUSTRY_SECTOR = "industry_sector"
    """
    Industry classification and sector performance data.

    **Data Types**:
    - Industry classification (申万/证监会)
    - Stock-to-industry mapping (time-versioned)
    - Industry indices (sector K-lines)
    - Industry constituent stocks
    - Sector capital flow
    - Sector rotation signals

    **Target Database**: PostgreSQL
    **Rationale**: Complex JOIN queries, hierarchical data, frequent updates

    **Storage Strategy**:
    - Industry taxonomy: Hierarchical tables (level 1/2/3)
    - Stock mappings: Time-versioned (effective_date, end_date)
    - Industry indices: Time-series tables

    **Cache Strategy**:
    - Industry list: Cache indefinitely (rarely changes)
    - Stock mappings: TTL = 1 day (quarterly updates)
    - Industry indices: TTL = 5 minutes

    **Query Patterns**:
    - Sector rotation analysis: Compare industry indices
    - Stock screening: Filter by industry + other criteria
    - Constituent queries: Get all stocks in industry

    **Example Usage**:
    ```python
    # Industry classification
    manager.save_data("SW", "industry_list", industries_df,
                     classification=DataClassification.INDUSTRY_SECTOR)

    # Industry index K-line
    manager.save_data("SW_01", "industry_index", index_df,
                     classification=DataClassification.INDUSTRY_SECTOR)
    ```
    """

    # ============================================================================
    # Category 5: Concept & Theme Plates
    # ============================================================================

    CONCEPT_THEME = "concept_theme"
    """
    Chinese market concept/theme plate data.

    **Data Types**:
    - Concept definitions (新能源汽车, 芯片, etc.)
    - Stock-to-concept mapping (dynamic, changes frequently)
    - Concept indices
    - Concept heat rankings (热度排名)
    - Leading stocks in concepts

    **Target Database**: PostgreSQL
    **Rationale**: Frequent updates, complex queries, many-to-many relationships

    **Storage Strategy**:
    - Concept taxonomy: Concept list table
    - Stock mappings: Time-versioned (added_date, removed_date)
    - Concept indices: Time-series tables

    **Cache Strategy**:
    - Concept list: TTL = 1 hour (new concepts added frequently)
    - Stock mappings: TTL = 30 minutes (dynamic changes)
    - Concept indices: TTL = 5 minutes

    **Query Patterns**:
    - Hot concepts: Order by heat ranking
    - Concept analysis: Get all stocks + recent performance
    - Cross-concept analysis: Find stocks in multiple concepts

    **Example Usage**:
    ```python
    # Concept list
    manager.save_data("ALL", "concept_list", concepts_df,
                     classification=DataClassification.CONCEPT_THEME)

    # Concept constituent stocks
    manager.save_data("BK0001", "concept_stocks", stocks_df,
                     classification=DataClassification.CONCEPT_THEME)
    ```
    """

    # ============================================================================
    # Category 6: Financial & Fundamental Data
    # ============================================================================

    FINANCIAL_FUNDAMENTAL = "financial_fundamental"
    """
    Financial statements and fundamental data.

    **Data Types**:
    - Income statements (利润表)
    - Balance sheets (资产负债表)
    - Cash flow statements (现金流量表)
    - Financial ratios (PE, PB, ROE, etc.)
    - Earnings reports
    - Dividend data
    - Company profiles

    **Target Database**: PostgreSQL
    **Rationale**: Quarterly reporting, complex JOINs for screening

    **Storage Strategy**:
    - Financial statements: One table per statement type
    - Financial indicators: Normalized table with indicator columns
    - Historical revisions: Track restatements

    **Cache Strategy**:
    - TTL = 1 day (quarterly updates, rarely changes intra-day)
    - Invalidate on earnings release date

    **Query Patterns**:
    - Financial screening: WHERE roe > 15 AND pe < 20
    - Trend analysis: Compare quarters
    - Cross-sectional: Rank stocks by financial metrics

    **Example Usage**:
    ```python
    # Income statement
    manager.save_data("600000", "financial_income", income_df,
                     classification=DataClassification.FINANCIAL_FUNDAMENTAL)

    # Financial indicators
    manager.save_data("600000", "financial_indicators", indicators_df,
                     classification=DataClassification.FINANCIAL_FUNDAMENTAL)
    ```
    """

    # ============================================================================
    # Category 7: Capital Flow & Fund Tracking
    # ============================================================================

    CAPITAL_FLOW = "capital_flow"
    """
    Main fund flow and institutional money tracking.

    **Data Types**:
    - Stock-level capital flow (主力/散户/机构资金)
    - Super large/large/medium/small order flow (超大单/大单/中单/小单)
    - North-bound capital flow (北向资金)
    - Fund position changes
    - Industry/sector capital flow
    - Market-level capital flow aggregation

    **Target Database**: PostgreSQL
    **Rationale**: Daily updates, complex aggregations, time-series analysis

    **Storage Strategy**:
    - Stock-level: One row per stock per day
    - Market-level: Aggregated daily totals
    - North-bound: Separate table for HK → A-share flow

    **Cache Strategy**:
    - Current day: TTL = 5 minutes (updates during trading)
    - Historical: Cache indefinitely (immutable)

    **Query Patterns**:
    - Momentum analysis: WHERE main_fund_net > 0 ORDER BY amount DESC
    - Institution following: Track institutional flow trends
    - Market sentiment: Aggregate market-level flow

    **Example Usage**:
    ```python
    # Stock capital flow
    manager.save_data("600000", "capital_flow", flow_df,
                     classification=DataClassification.CAPITAL_FLOW)

    # North-bound flow
    manager.save_data("ALL", "north_bound_flow", northbound_df,
                     classification=DataClassification.CAPITAL_FLOW)
    ```
    """

    # ============================================================================
    # Category 8: Chip Distribution & Holder Analysis
    # ============================================================================

    CHIP_DISTRIBUTION = "chip_distribution"
    """
    Shareholder structure and chip concentration analysis.

    **Data Types**:
    - Top 10 shareholders (前十大股东)
    - Shareholder changes (股东变动)
    - Chip distribution by price level (筹码分布)
    - Holder concentration index (持股集中度)
    - Profit/loss ratio (获利盘比例)
    - Average holder cost (平均持股成本)

    **Target Database**: PostgreSQL
    **Rationale**: Quarterly reporting, complex calculations, historical tracking

    **Storage Strategy**:
    - Top shareholders: One row per shareholder per report period
    - Chip distribution: Price-level granularity (e.g., every 0.1 yuan)
    - Concentration metrics: Daily calculation

    **Cache Strategy**:
    - Shareholder data: TTL = 1 day (quarterly reports)
    - Chip distribution: TTL = 1 hour (daily recalculation)

    **Query Patterns**:
    - Control analysis: Track shareholder changes
    - Resistance levels: Identify price levels with high chip concentration
    - Profit analysis: Calculate profit ratio at current price

    **Example Usage**:
    ```python
    # Top shareholders
    manager.save_data("600000", "top_shareholders", shareholders_df,
                     classification=DataClassification.CHIP_DISTRIBUTION)

    # Chip distribution
    manager.save_data("600000", "chip_distribution", chip_df,
                     classification=DataClassification.CHIP_DISTRIBUTION)
    ```
    """

    # ============================================================================
    # Category 9: News & Announcements
    # ============================================================================

    NEWS_ANNOUNCEMENT = "news_announcement"
    """
    News, announcements, and research reports.

    **Data Types**:
    - Company announcements (公告)
    - News articles
    - Research reports metadata (研报)
    - Analyst ratings
    - Event calendar (earnings dates, shareholder meetings)

    **Target Database**: PostgreSQL
    **Rationale**: Text search, frequent inserts, metadata queries

    **Storage Strategy**:
    - Announcements: Full-text search indexing
    - News: Store title + summary + URL (not full text)
    - Reports: Metadata only (title, author, rating, date)

    **Cache Strategy**:
    - No caching (always fetch latest)
    - Or TTL = 10 minutes for aggregated views

    **Query Patterns**:
    - Recent announcements: ORDER BY publish_date DESC LIMIT 20
    - Full-text search: WHERE content @@ 'keyword'
    - Event calendar: WHERE event_date BETWEEN start AND end

    **Example Usage**:
    ```python
    # Company announcement
    manager.save_data("600000", "announcement", announcement_df,
                     classification=DataClassification.NEWS_ANNOUNCEMENT)

    # News articles
    manager.save_data("600000", "news", news_df,
                     classification=DataClassification.NEWS_ANNOUNCEMENT)
    ```
    """

    # ============================================================================
    # Category 10: Derived Indicators & Signals
    # ============================================================================

    DERIVED_INDICATOR = "derived_indicator"
    """
    Computed technical indicators and trading signals.

    **Data Types**:
    - Technical indicators (MA, MACD, RSI, BOLL, KDJ, etc.)
    - Quantitative factors (momentum, value, quality, etc.)
    - Trading signals (buy/sell/hold)
    - Model outputs (predictions, probabilities)
    - Backtesting results

    **Target Database**: PostgreSQL
    **Rationale**: Frequent updates, complex calculations, time-series analysis

    **Storage Strategy**:
    - Indicators: One row per symbol per day
    - Signals: Separate table with signal type + strength
    - Model outputs: JSON fields for flexible schema

    **Cache Strategy**:
    - Current day: TTL = 5 minutes (recalculate as price updates)
    - Historical: Cache indefinitely (recompute only if parameters change)

    **Query Patterns**:
    - Signal screening: WHERE signal = 'buy' AND strength > 0.7
    - Indicator filtering: WHERE ma5 > ma20 (golden cross)
    - Backtesting: Historical signal → actual returns

    **Example Usage**:
    ```python
    # Technical indicators
    manager.save_data("600000", "indicators", indicators_df,
                     classification=DataClassification.DERIVED_INDICATOR)

    # Trading signals
    manager.save_data("600000", "signals", signals_df,
                     classification=DataClassification.DERIVED_INDICATOR)
    ```
    """
```

---

## Classification-to-Database Mapping

### Routing Rules

```python
CLASSIFICATION_DB_MAPPING = {
    DataClassification.HIGH_FREQUENCY: "tdengine",
    DataClassification.HISTORICAL_KLINE: "postgresql",
    DataClassification.REALTIME_SNAPSHOT: "postgresql",
    DataClassification.INDUSTRY_SECTOR: "postgresql",
    DataClassification.CONCEPT_THEME: "postgresql",
    DataClassification.FINANCIAL_FUNDAMENTAL: "postgresql",
    DataClassification.CAPITAL_FLOW: "postgresql",
    DataClassification.CHIP_DISTRIBUTION: "postgresql",
    DataClassification.NEWS_ANNOUNCEMENT: "postgresql",
    DataClassification.DERIVED_INDICATOR: "postgresql",
}

def get_target_database(classification: DataClassification) -> str:
    """
    Get target database for a data classification.

    Performance: O(1) dict lookup (<1ms)

    Returns:
        "tdengine" or "postgresql"
    """
    return CLASSIFICATION_DB_MAPPING[classification]
```

### Decision Rationale

| Classification | Database | Rationale |
|---------------|----------|-----------|
| HIGH_FREQUENCY | TDengine | 20:1 compression, >1M writes/s, time-series optimized |
| HISTORICAL_KLINE | PostgreSQL | TimescaleDB extension, complex queries, JOINs |
| REALTIME_SNAPSHOT | PostgreSQL | Medium frequency, complex filtering |
| INDUSTRY_SECTOR | PostgreSQL | Hierarchical data, complex JOINs, frequent updates |
| CONCEPT_THEME | PostgreSQL | Many-to-many relationships, dynamic changes |
| FINANCIAL_FUNDAMENTAL | PostgreSQL | Quarterly updates, cross-sectional screening |
| CAPITAL_FLOW | PostgreSQL | Daily time-series, aggregations |
| CHIP_DISTRIBUTION | PostgreSQL | Complex calculations, historical tracking |
| NEWS_ANNOUNCEMENT | PostgreSQL | Full-text search, metadata queries |
| DERIVED_INDICATOR | PostgreSQL | Frequent updates, time-series + JOINs |

**Summary**: 1 TDengine (high-frequency only) + 9 PostgreSQL (everything else)

---

## Auto-Detection Rules

### Data Type → Classification Mapping

```python
AUTO_CLASSIFICATION_RULES = {
    # High-frequency patterns
    "tick": DataClassification.HIGH_FREQUENCY,
    "kline_1min": DataClassification.HIGH_FREQUENCY,
    "kline_5min": DataClassification.HIGH_FREQUENCY,
    "kline_15min": DataClassification.HIGH_FREQUENCY,
    "kline_30min": DataClassification.HIGH_FREQUENCY,
    "kline_60min": DataClassification.HIGH_FREQUENCY,

    # Historical K-line patterns
    "kline_daily": DataClassification.HISTORICAL_KLINE,
    "kline_weekly": DataClassification.HISTORICAL_KLINE,
    "kline_monthly": DataClassification.HISTORICAL_KLINE,

    # Real-time snapshot patterns
    "market_snapshot": DataClassification.REALTIME_SNAPSHOT,
    "market_breadth": DataClassification.REALTIME_SNAPSHOT,
    "realtime_quotes": DataClassification.REALTIME_SNAPSHOT,

    # Industry & sector patterns
    "industry_list": DataClassification.INDUSTRY_SECTOR,
    "industry_index": DataClassification.INDUSTRY_SECTOR,
    "stock_industry": DataClassification.INDUSTRY_SECTOR,

    # Concept patterns
    "concept_list": DataClassification.CONCEPT_THEME,
    "concept_stocks": DataClassification.CONCEPT_THEME,
    "stock_concepts": DataClassification.CONCEPT_THEME,

    # Financial patterns
    "financial_income": DataClassification.FINANCIAL_FUNDAMENTAL,
    "financial_balance": DataClassification.FINANCIAL_FUNDAMENTAL,
    "financial_cashflow": DataClassification.FINANCIAL_FUNDAMENTAL,
    "financial_indicators": DataClassification.FINANCIAL_FUNDAMENTAL,

    # Capital flow patterns
    "capital_flow": DataClassification.CAPITAL_FLOW,
    "north_bound_flow": DataClassification.CAPITAL_FLOW,

    # Chip distribution patterns
    "top_shareholders": DataClassification.CHIP_DISTRIBUTION,
    "chip_distribution": DataClassification.CHIP_DISTRIBUTION,

    # News patterns
    "announcement": DataClassification.NEWS_ANNOUNCEMENT,
    "news": DataClassification.NEWS_ANNOUNCEMENT,
    "research_report": DataClassification.NEWS_ANNOUNCEMENT,

    # Indicator patterns
    "indicators": DataClassification.DERIVED_INDICATOR,
    "signals": DataClassification.DERIVED_INDICATOR,
    "model_output": DataClassification.DERIVED_INDICATOR,
}

def auto_detect_classification(data_type: str) -> DataClassification:
    """
    Auto-detect classification from data_type string.

    Falls back to HISTORICAL_KLINE if no match found.

    Example:
        >>> auto_detect_classification("kline_daily")
        DataClassification.HISTORICAL_KLINE

        >>> auto_detect_classification("capital_flow")
        DataClassification.CAPITAL_FLOW
    """
    return AUTO_CLASSIFICATION_RULES.get(
        data_type,
        DataClassification.HISTORICAL_KLINE  # Default fallback
    )
```

---

## Cache Strategy Matrix

### Cache TTL by Classification

| Classification | Cache TTL | Invalidation Rule |
|---------------|-----------|-------------------|
| HIGH_FREQUENCY | 1 second (realtime)<br>5 minutes (current day)<br>Indefinite (historical) | Time-based |
| HISTORICAL_KLINE | 5 minutes (current day)<br>Indefinite (historical) | Immutability-based |
| REALTIME_SNAPSHOT | 3 seconds | Time-based |
| INDUSTRY_SECTOR | 1 day (mappings)<br>5 minutes (indices) | Event-based (quarterly reports) |
| CONCEPT_THEME | 30 minutes (mappings)<br>5 minutes (indices) | Frequency-based |
| FINANCIAL_FUNDAMENTAL | 1 day | Event-based (earnings release) |
| CAPITAL_FLOW | 5 minutes (current day)<br>Indefinite (historical) | Immutability-based |
| CHIP_DISTRIBUTION | 1 hour | Daily recalculation |
| NEWS_ANNOUNCEMENT | No cache (or 10 minutes) | Always fetch latest |
| DERIVED_INDICATOR | 5 minutes (current day)<br>Indefinite (historical) | Parameter-based |

---

## Validation Rules

### Per-Classification Validation

```python
VALIDATION_RULES = {
    DataClassification.HIGH_FREQUENCY: {
        "required_columns": ["ts", "price", "volume"],
        "timestamp_column": "ts",
        "frequency_check": "high",  # Expect many records per day
    },
    DataClassification.HISTORICAL_KLINE: {
        "required_columns": ["date", "open", "high", "low", "close", "volume"],
        "timestamp_column": "date",
        "price_validation": True,  # high >= max(open, close, low)
    },
    DataClassification.CAPITAL_FLOW: {
        "required_columns": ["date", "main_fund_net"],
        "timestamp_column": "date",
        "allow_negative": True,  # Net flow can be negative
    },
    # ... other classifications
}

def validate_data(classification: DataClassification,
                  df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
    """
    Validate DataFrame against classification rules.

    Returns:
        (is_valid, error_message)

    Example:
        >>> is_valid, error = validate_data(
        ...     DataClassification.HISTORICAL_KLINE,
        ...     kline_df
        ... )
        >>> if not is_valid:
        ...     print(f"Validation failed: {error}")
    """
    rules = VALIDATION_RULES[classification]

    # Check required columns
    missing_cols = set(rules["required_columns"]) - set(df.columns)
    if missing_cols:
        return False, f"Missing required columns: {missing_cols}"

    # Additional validation based on rules
    # ... (price validation, timestamp checks, etc.)

    return True, None
```

---

## Query Optimization Hints

### Per-Classification Hints

```python
QUERY_HINTS = {
    DataClassification.HIGH_FREQUENCY: {
        "prefer_recent": True,  # Recent data queries common
        "chunk_large_ranges": True,  # Split >30 days into chunks
        "use_hot_tier": True,  # Check TDengine hot tier first
    },
    DataClassification.HISTORICAL_KLINE: {
        "timescale_optimized": True,  # Use TimescaleDB functions
        "batch_symbols": True,  # Batch multi-symbol queries
    },
    DataClassification.CAPITAL_FLOW: {
        "aggregate_friendly": True,  # Common to aggregate by period
        "join_with_kline": True,  # Often joined with price data
    },
    # ... other classifications
}

def get_query_hints(classification: DataClassification) -> Dict[str, bool]:
    """Get query optimization hints for classification"""
    return QUERY_HINTS.get(classification, {})
```

---

## Migration from 34-Classification System

### Mapping Table

| Old Classification (34 categories) | New Classification (10 categories) |
|-----------------------------------|------------------------------------|
| TICK_DATA, DEPTH_DATA | HIGH_FREQUENCY |
| MINUTE_KLINE_1, MINUTE_KLINE_5, ... | HIGH_FREQUENCY |
| DAILY_KLINE, WEEKLY_KLINE, MONTHLY_KLINE | HISTORICAL_KLINE |
| REALTIME_QUOTES, MARKET_BREADTH | REALTIME_SNAPSHOT |
| SYMBOLS_INFO, CONTRACT_INFO, CONSTITUENT_INFO | INDUSTRY_SECTOR |
| (No equivalent in old system) | CONCEPT_THEME (NEW) |
| (No equivalent in old system) | CAPITAL_FLOW (NEW) |
| (No equivalent in old system) | CHIP_DISTRIBUTION (NEW) |
| TECHNICAL_INDICATORS, QUANTITATIVE_FACTORS | DERIVED_INDICATOR |
| (Others: merge or deprecate) | - |

**New Categories**:
- CONCEPT_THEME: Chinese market specific
- CAPITAL_FLOW: Professional quant analysis requirement
- CHIP_DISTRIBUTION: Shareholder analysis requirement

---

## Testing Contract

### Classification Tests

```python
def test_classification_mapping():
    # Test all classifications have database mapping
    for classification in DataClassification:
        db = get_target_database(classification)
        assert db in ["tdengine", "postgresql"]

def test_auto_detection():
    # Test auto-detection rules
    assert auto_detect_classification("kline_daily") == DataClassification.HISTORICAL_KLINE
    assert auto_detect_classification("capital_flow") == DataClassification.CAPITAL_FLOW

def test_validation_rules():
    # Test validation for each classification
    df = create_test_kline_data()
    is_valid, error = validate_data(DataClassification.HISTORICAL_KLINE, df)
    assert is_valid, f"Validation failed: {error}"
```

---

## Versioning

**Version**: 1.0 (Initial release with 10 classifications)

**Future Extensions**:
- Classification may be extended (new categories added)
- Existing classifications will NOT be removed
- Routing rules may be optimized but API remains stable

---

## Conclusion

This 10-category classification system provides:

1. **Simplicity**: 10 categories vs 34 (71% reduction)
2. **Clarity**: Business-oriented, mutually exclusive classifications
3. **Performance**: O(1) routing, optimized caching per classification
4. **Chinese Market Focus**: Explicit support for industry/sector/concept/capital/chip
5. **Professional Analysis**: All quantitative trading scenarios covered

Ready to proceed to quickstart.md implementation guide.
