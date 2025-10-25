# API Contract: IDataSource Adapter Interface

**Feature**: Architecture Optimization for Quantitative Trading System
**Branch**: `002-arch-optimization`
**Date**: 2025-10-25
**Contract Type**: Adapter Layer Interface (Layer 1)

## Overview

This contract defines the flexible `IDataSource` protocol for data source adapters. The protocol allows **partial implementation** - adapters only implement methods for data types they support, avoiding forced implementation of unsupported methods.

## Design Principles

**1. Flexibility Over Rigidity**: Adapters implement only what they support
- TDX adapter: Local data methods only (no financial statements)
- AkShare adapter: Comprehensive coverage
- Byapi adapter: Subset of methods with rate limits

**2. Protocol-Based Typing**: Python's Protocol instead of ABC for looser coupling

**3. Optional Methods**: All methods return `Optional[pd.DataFrame]` - None indicates unsupported

**4. Consistent Signatures**: Standard parameters across all methods

---

## IDataSource Protocol Definition

### Core Protocol

```python
from typing import Protocol, Optional, List
from datetime import date
import pandas as pd

class IDataSource(Protocol):
    """
    Flexible data source adapter protocol.

    Adapters implement only the methods they support. All methods return
    Optional[pd.DataFrame] - None indicates the adapter doesn't support this
    data type or the query failed.

    NO mandatory methods - adapters can implement any subset of methods.
    """

    # ============================================================================
    # Group 1: Market Data - Quotes & K-Lines
    # ============================================================================

    def get_realtime_quotes(self,
                            symbols: List[str],
                            fields: Optional[List[str]] = None) -> Optional[pd.DataFrame]:
        """
        Get real-time quotes for multiple symbols.

        Args:
            symbols: List of stock codes (e.g., ["600000", "000001"])
            fields: Optional field list (e.g., ["price", "volume", "bid1", "ask1"])
                    If None, return all available fields

        Returns:
            DataFrame with columns: symbol, price, volume, amount, bid1, ask1, ...
            Or None if adapter doesn't support real-time quotes

        Example:
            >>> adapter.get_realtime_quotes(["600000", "000001"])
               symbol   price   volume      amount  bid1  ask1  ...
            0  600000  15.23  1234567  1.88e+09  15.22  15.23
            1  000001  12.45   987654  1.23e+09  12.44  12.45
        """
        ...

    def get_kline_data(self,
                       symbol: str,
                       period: str,
                       start_date: str,
                       end_date: str,
                       adjust: str = "qfq") -> Optional[pd.DataFrame]:
        """
        Get K-line data for a symbol.

        Args:
            symbol: Stock code (e.g., "600000")
            period: K-line period
                    - "tick": Tick data (if supported)
                    - "1min", "5min", "15min", "30min", "60min": Minute bars
                    - "daily": Daily K-line
                    - "weekly": Weekly K-line
                    - "monthly": Monthly K-line
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")
            adjust: Adjustment type
                    - "qfq": Forward adjust (前复权)
                    - "hfq": Backward adjust (后复权)
                    - "": No adjustment

        Returns:
            DataFrame with columns: date, open, high, low, close, volume, amount
            Or None if adapter doesn't support this period or query failed

        Example:
            >>> adapter.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")
                   date   open   high    low  close    volume       amount
            0  2024-01-02  15.20  15.50  15.10  15.40  12345678  1.88e+09
            1  2024-01-03  15.35  15.60  15.25  15.50  10234567  1.57e+09
        """
        ...

    def get_tick_data(self,
                      symbol: str,
                      trade_date: str) -> Optional[pd.DataFrame]:
        """
        Get tick-level (Level-2) market data for a trading day.

        Args:
            symbol: Stock code (e.g., "600000")
            trade_date: Trading date (format: "YYYY-MM-DD")

        Returns:
            DataFrame with columns: time, price, volume, amount, bid1, ask1, ...
            Or None if adapter doesn't support tick data

        Example:
            >>> adapter.get_tick_data("600000", "2024-01-02")
                      time   price  volume    amount  bid1  ask1
            0  09:30:00.123  15.20    1000  15200.0  15.19  15.20
            1  09:30:01.456  15.21     500   7605.0  15.20  15.21
        """
        ...

    # ============================================================================
    # Group 2: Industry & Sector Data
    # ============================================================================

    def get_industry_list(self,
                          classification: str = "SW") -> Optional[pd.DataFrame]:
        """
        Get industry classification list.

        Args:
            classification: Classification system
                          - "SW": 申万行业分类
                          - "CSRC": 证监会行业分类

        Returns:
            DataFrame with columns: industry_code, industry_name, level, parent_code
            Or None if adapter doesn't support industry data

        Example:
            >>> adapter.get_industry_list("SW")
              industry_code industry_name  level parent_code
            0         SW_01        农林牧渔      1        None
            1         SW_02        采掘          2      SW_01
        """
        ...

    def get_stock_industry(self,
                           symbol: str,
                           classification: str = "SW") -> Optional[pd.DataFrame]:
        """
        Get industry classification for a stock.

        Args:
            symbol: Stock code (e.g., "600000")
            classification: Classification system ("SW" or "CSRC")

        Returns:
            DataFrame with columns: industry_code, industry_name, level
            Or None if adapter doesn't support industry data
        """
        ...

    def get_industry_stocks(self,
                            industry_code: str) -> Optional[pd.DataFrame]:
        """
        Get constituent stocks of an industry.

        Args:
            industry_code: Industry code (e.g., "SW_01")

        Returns:
            DataFrame with columns: symbol, name, weight
            Or None if adapter doesn't support industry data
        """
        ...

    def get_industry_index(self,
                           industry_code: str,
                           start_date: str,
                           end_date: str) -> Optional[pd.DataFrame]:
        """
        Get industry index K-line data.

        Args:
            industry_code: Industry code (e.g., "SW_01")
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")

        Returns:
            DataFrame with columns: date, index_value, pct_change, volume, amount
            Or None if adapter doesn't support industry index data
        """
        ...

    # ============================================================================
    # Group 3: Concept & Theme Plates
    # ============================================================================

    def get_concept_list(self) -> Optional[pd.DataFrame]:
        """
        Get concept plate list.

        Returns:
            DataFrame with columns: concept_code, concept_name, description
            Or None if adapter doesn't support concept data

        Example:
            >>> adapter.get_concept_list()
              concept_code    concept_name              description
            0    BK0001         新能源汽车       电动车及相关产业链
            1    BK0002         芯片          半导体芯片概念
        """
        ...

    def get_concept_stocks(self,
                           concept_code: str) -> Optional[pd.DataFrame]:
        """
        Get constituent stocks of a concept.

        Args:
            concept_code: Concept code (e.g., "BK0001")

        Returns:
            DataFrame with columns: symbol, name, reason (入选理由)
            Or None if adapter doesn't support concept data
        """
        ...

    def get_stock_concepts(self,
                           symbol: str) -> Optional[pd.DataFrame]:
        """
        Get all concepts that a stock belongs to.

        Args:
            symbol: Stock code (e.g., "600000")

        Returns:
            DataFrame with columns: concept_code, concept_name
            Or None if adapter doesn't support concept data
        """
        ...

    # ============================================================================
    # Group 4: Financial & Fundamental Data
    # ============================================================================

    def get_financial_statements(self,
                                  symbol: str,
                                  statement_type: str,
                                  start_date: str,
                                  end_date: str) -> Optional[pd.DataFrame]:
        """
        Get financial statements.

        Args:
            symbol: Stock code (e.g., "600000")
            statement_type: Statement type
                          - "income": Income statement (利润表)
                          - "balance": Balance sheet (资产负债表)
                          - "cashflow": Cash flow statement (现金流量表)
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")

        Returns:
            DataFrame with columns: report_date, [statement-specific fields]
            Or None if adapter doesn't support financial data

        Example (income statement):
            >>> adapter.get_financial_statements("600000", "income", "2023-01-01", "2023-12-31")
              report_date  revenue  operating_profit  net_profit
            0  2023-09-30  1.23e+11       2.34e+10    1.56e+10
            1  2023-06-30  8.45e+10       1.67e+10    1.12e+10
        """
        ...

    def get_financial_indicators(self,
                                  symbol: str,
                                  start_date: str,
                                  end_date: str) -> Optional[pd.DataFrame]:
        """
        Get financial indicators and ratios.

        Args:
            symbol: Stock code (e.g., "600000")
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")

        Returns:
            DataFrame with columns: report_date, eps, pe, pb, roe, ...
            Or None if adapter doesn't support indicator data
        """
        ...

    # ============================================================================
    # Group 5: Capital Flow & Fund Tracking
    # ============================================================================

    def get_capital_flow(self,
                         symbol: str,
                         start_date: str,
                         end_date: str) -> Optional[pd.DataFrame]:
        """
        Get capital flow data for a stock.

        Args:
            symbol: Stock code (e.g., "600000")
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")

        Returns:
            DataFrame with columns: date, main_fund_net, retail_fund_net,
                                   institutional_fund_net, super_large_net, ...
            Or None if adapter doesn't support capital flow data

        Example:
            >>> adapter.get_capital_flow("600000", "2024-01-01", "2024-01-31")
                   date  main_fund_net  retail_fund_net
            0  2024-01-02     1.23e+08       -5.67e+07
            1  2024-01-03    -2.34e+07        4.56e+07
        """
        ...

    def get_north_bound_flow(self,
                             start_date: str,
                             end_date: str) -> Optional[pd.DataFrame]:
        """
        Get north-bound capital flow (北向资金) data.

        Args:
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")

        Returns:
            DataFrame with columns: date, north_bound_net, sh_net, sz_net
            Or None if adapter doesn't support north-bound flow data
        """
        ...

    # ============================================================================
    # Group 6: Chip Distribution & Holder Analysis
    # ============================================================================

    def get_top_shareholders(self,
                             symbol: str,
                             report_date: str) -> Optional[pd.DataFrame]:
        """
        Get top 10 shareholders of a stock.

        Args:
            symbol: Stock code (e.g., "600000")
            report_date: Report date (format: "YYYY-MM-DD", typically quarter-end)

        Returns:
            DataFrame with columns: rank, shareholder_name, shares_held,
                                   holding_ratio, shareholder_type
            Or None if adapter doesn't support shareholder data

        Example:
            >>> adapter.get_top_shareholders("600000", "2023-12-31")
               rank shareholder_name  shares_held  holding_ratio shareholder_type
            0     1        中国XX基金     1.23e+09           15.6         机构
            1     2        XX社保基金     8.56e+08           10.8         机构
        """
        ...

    def get_chip_distribution(self,
                              symbol: str,
                              calc_date: str) -> Optional[pd.DataFrame]:
        """
        Get chip distribution by price level.

        Args:
            symbol: Stock code (e.g., "600000")
            calc_date: Calculation date (format: "YYYY-MM-DD")

        Returns:
            DataFrame with columns: price_level, chip_ratio, profit_ratio
            Or None if adapter doesn't support chip distribution data

        Example:
            >>> adapter.get_chip_distribution("600000", "2024-01-31")
               price_level  chip_ratio  profit_ratio
            0        15.00        8.5           45.2
            1        15.50       12.3           38.7
        """
        ...

    # ============================================================================
    # Group 7: News & Announcements
    # ============================================================================

    def get_stock_news(self,
                       symbol: str,
                       start_date: str,
                       end_date: str,
                       news_type: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Get stock-related news.

        Args:
            symbol: Stock code (e.g., "600000")
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")
            news_type: Optional news type filter
                      - "announcement": Official announcements (公告)
                      - "news": News articles
                      - "research": Research reports (研报)
                      - None: All types

        Returns:
            DataFrame with columns: date, title, content, source, url
            Or None if adapter doesn't support news data
        """
        ...

    # ============================================================================
    # Group 8: Derived Indicators
    # ============================================================================

    def get_technical_indicator(self,
                                 symbol: str,
                                 indicator_name: str,
                                 start_date: str,
                                 end_date: str,
                                 **params) -> Optional[pd.DataFrame]:
        """
        Get computed technical indicators.

        Args:
            symbol: Stock code (e.g., "600000")
            indicator_name: Indicator name (e.g., "MA", "MACD", "RSI", "BOLL")
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")
            **params: Indicator-specific parameters
                     - MA: period=5/10/20/60/120/250
                     - MACD: fast=12, slow=26, signal=9
                     - RSI: period=14
                     - BOLL: period=20, std=2

        Returns:
            DataFrame with columns: date, [indicator-specific fields]
            Or None if adapter doesn't support indicator calculation

        Example:
            >>> adapter.get_technical_indicator("600000", "MA", "2024-01-01", "2024-01-31", period=5)
                   date   close     ma5
            0  2024-01-02  15.20  15.18
            1  2024-01-03  15.30  15.22
        """
        ...

    # ============================================================================
    # Group 9: Metadata & System Info
    # ============================================================================

    def get_trade_calendar(self,
                           start_date: str,
                           end_date: str,
                           exchange: str = "SSE") -> Optional[pd.DataFrame]:
        """
        Get trading calendar (trading days vs non-trading days).

        Args:
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")
            exchange: Exchange code
                     - "SSE": Shanghai Stock Exchange (上交所)
                     - "SZSE": Shenzhen Stock Exchange (深交所)

        Returns:
            DataFrame with columns: date, is_trading_day
            Or None if adapter doesn't support calendar data

        Example:
            >>> adapter.get_trade_calendar("2024-01-01", "2024-01-07", "SSE")
                   date  is_trading_day
            0  2024-01-01           0  # New Year holiday
            1  2024-01-02           1
            2  2024-01-03           1
        """
        ...

    def get_stock_list(self,
                       exchange: Optional[str] = None,
                       status: str = "L") -> Optional[pd.DataFrame]:
        """
        Get list of all stocks.

        Args:
            exchange: Optional exchange filter
                     - "SH": Shanghai (沪市)
                     - "SZ": Shenzhen (深市)
                     - None: All exchanges
            status: Listing status
                   - "L": Listed (在市)
                   - "D": Delisted (退市)
                   - "P": Paused (停牌)

        Returns:
            DataFrame with columns: symbol, name, exchange, listing_date, ...
            Or None if adapter doesn't support stock list query

        Example:
            >>> adapter.get_stock_list(exchange="SH", status="L")
              symbol  name exchange  listing_date  ...
            0  600000  浦发银行     SH    1999-11-10
            1  600004  白云机场     SH    2003-02-27
        """
        ...

    # ============================================================================
    # Optional: Adapter Metadata
    # ============================================================================

    def get_supported_features(self) -> List[str]:
        """
        Get list of supported method names (optional introspection).

        Returns:
            List of method names this adapter implements

        Example:
            >>> adapter.get_supported_features()
            ['get_realtime_quotes', 'get_kline_data', 'get_capital_flow']
        """
        ...

    def get_rate_limit(self) -> Optional[int]:
        """
        Get adapter rate limit (requests per minute).

        Returns:
            Requests per minute limit, or None for unlimited

        Example:
            >>> adapter.get_rate_limit()
            300  # 300 requests per minute (byapi)
        """
        ...
```

---

## Usage Examples

### Example 1: Core Adapter (AkShare) - Full Implementation

```python
class AkShareAdapter:
    """Comprehensive adapter - implements most methods"""

    def __init__(self, proxy=None):
        self.proxy = proxy

    def get_realtime_quotes(self, symbols, fields=None):
        # Implement using akshare.stock_zh_a_spot_em()
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        # Filter to requested symbols
        return df[df['代码'].isin(symbols)]

    def get_kline_data(self, symbol, period, start_date, end_date, adjust="qfq"):
        # Implement using akshare.stock_zh_a_hist()
        import akshare as ak
        df = ak.stock_zh_a_hist(symbol=symbol, period=period,
                                start_date=start_date, end_date=end_date,
                                adjust=adjust)
        return df

    def get_capital_flow(self, symbol, start_date, end_date):
        # Implement using akshare.stock_individual_fund_flow()
        import akshare as ak
        df = ak.stock_individual_fund_flow(symbol=symbol,
                                           start_date=start_date,
                                           end_date=end_date)
        return df

    # ... implements 20+ more methods
```

### Example 2: Local Adapter (TDX) - Partial Implementation

```python
class TDXAdapter:
    """Local data adapter - implements subset of methods"""

    def __init__(self, tdx_path="/mnt/d/ProgramData/tdx_new"):
        self.tdx_path = tdx_path

    def get_realtime_quotes(self, symbols, fields=None):
        # Implement using local TDX cache files
        # Read from TDX real-time data buffer
        return self._read_tdx_realtime(symbols)

    def get_kline_data(self, symbol, period, start_date, end_date, adjust=""):
        # Implement using local .day / .lc1 files
        if period == "daily":
            return self._read_day_file(symbol, start_date, end_date)
        elif period in ["1min", "5min"]:
            return self._read_lc1_file(symbol, period, start_date, end_date)
        else:
            return None  # TDX doesn't support this period

    # Does NOT implement: get_capital_flow, get_financial_statements, etc.
    # These return None when called, indicating unsupported
```

### Example 3: Custom Scraper Adapter - Single Method

```python
class CustomNewsScraperAdapter:
    """Custom adapter - implements only news scraping"""

    def __init__(self, url):
        self.url = url

    def get_stock_news(self, symbol, start_date, end_date, news_type=None):
        # Custom scraping logic
        news_data = self._scrape_news(symbol, start_date, end_date)
        return news_data

    # Does NOT implement any other methods
    # All other method calls return None
```

---

## Error Handling Contract

### Return Value Semantics

**Success**: Return `pd.DataFrame` with expected columns

**Unsupported Feature**: Return `None`
- Adapter doesn't implement this method
- DataManager tries next adapter in priority chain

**Query Failed**: Return `None` + log warning
- Network error
- API rate limit exceeded
- Invalid parameters

**Empty Result**: Return empty `pd.DataFrame` (not None)
- Query succeeded but no data matches criteria
- E.g., query for non-trading days returns empty DataFrame

### Exception Handling

Adapters SHOULD catch exceptions internally and return None instead of raising:

```python
def get_kline_data(self, symbol, period, start_date, end_date, adjust="qfq"):
    try:
        # Fetch data logic
        data = fetch_from_api(...)
        return data
    except NetworkError as e:
        logger.warning(f"Network error fetching {symbol}: {e}")
        return None
    except APIError as e:
        logger.warning(f"API error fetching {symbol}: {e}")
        return None
```

DataManager interprets `None` as "try next adapter" and continues with fallback chain.

---

## Validation Requirements

### Input Validation

Adapters SHOULD validate inputs before making API calls:

**Symbol Format**:
- Pattern: `^[0-9]{6}$` (6 digits)
- Valid prefixes: 60xxxx (SH), 00xxxx (SZ), 30xxxx (GEM)

**Date Format**:
- Pattern: `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` (YYYY-MM-DD)
- start_date ≤ end_date
- No future dates for historical data

**Period Values**:
- Valid: "tick", "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
- Invalid periods return None

### Output Validation

Adapters SHOULD return DataFrames with consistent column names:

**Standard Column Names** (per method):
- `get_realtime_quotes`: symbol, price, volume, amount, bid1, ask1
- `get_kline_data`: date, open, high, low, close, volume, amount
- `get_capital_flow`: date, main_fund_net, retail_fund_net, institutional_fund_net

DataManager performs additional validation before caching.

---

## Performance Guidelines

**1. Batch Operations**: Prefer batch queries over individual queries
- `get_realtime_quotes(symbols=["600000", "000001"])` instead of 2 calls

**2. Caching**: Adapters MAY implement internal caching
- Cache immutable historical data
- Respect cache TTL for real-time data

**3. Rate Limiting**: Adapters MUST respect API rate limits
- Implement exponential backoff on rate limit errors
- Return None instead of blocking indefinitely

**4. Timeout**: Network calls SHOULD have reasonable timeouts (10-30 seconds)

---

## Testing Contract

### Unit Tests

Each adapter implementation SHOULD provide unit tests:

```python
def test_get_kline_data_success():
    adapter = AkShareAdapter()
    df = adapter.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")

    assert df is not None
    assert not df.empty
    assert "date" in df.columns
    assert "close" in df.columns

def test_get_kline_data_unsupported_period():
    adapter = TDXAdapter()
    df = adapter.get_kline_data("600000", "monthly", "2024-01-01", "2024-01-31")

    assert df is None  # TDX doesn't support monthly
```

### Integration Tests

DataManager integration tests verify adapter fallback chain:

```python
def test_cache_first_retrieval():
    manager = DataManager()
    manager.register_adapter("tdx", TDXAdapter())
    manager.register_adapter("akshare", AkShareAdapter())

    # First call: cache miss, try TDX → AkShare
    df1 = manager.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")
    assert df1 is not None

    # Second call: cache hit, no adapter calls
    df2 = manager.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")
    assert df2 is not None
    assert df1.equals(df2)
```

---

## Versioning & Backward Compatibility

**Version**: 1.0 (Initial release)

**Backward Compatibility Promise**:
- Method signatures will not change (parameters, return types)
- New methods may be added in future versions
- Existing methods may be marked deprecated but not removed

**Migration Path**:
- Adapters implementing deprecated methods will receive warnings
- 6-month deprecation period before removal

---

## Conclusion

This flexible IDataSource protocol enables:

1. **Partial Implementation**: Adapters implement only what they support
2. **Type Safety**: Protocol-based typing without ABC rigidity
3. **Clear Contracts**: Standard signatures across all adapters
4. **Graceful Degradation**: None return triggers fallback to next adapter
5. **Extensibility**: Custom adapters can implement any subset of methods

Ready to proceed to DataManager interface contract.
