# IDataSource Interface Contract

**Feature**: TDX Data Source Adapter
**Interface**: `interfaces.data_source.IDataSource`
**Implementation**: `adapters.tdx_adapter.TdxDataSource`
**Version**: 1.0

---

## Contract Overview

This document defines the interface contract for `TdxDataSource`, which must implement all 8 methods defined in the `IDataSource` abstract base class. The contract specifies input parameters, return types, error handling, and behavioral requirements.

**Contract Enforcement**:
- Python ABC (Abstract Base Class) enforces method signatures at runtime
- Type hints provide static type checking via mypy
- Unit tests (`test_tdx_contract.py`) verify compliance

---

## Method 1: get_stock_daily

### Signature
```python
def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame
```

### Purpose
Fetch daily OHLCV (Open, High, Low, Close, Volume) data for a given stock within a date range.

### Parameters
| Parameter | Type | Format | Required | Description |
|-----------|------|--------|----------|-------------|
| symbol | str | '600519' or '000001' | ✅ | 6-digit stock code |
| start_date | str | 'YYYY-MM-DD' | ✅ | Start date (inclusive) |
| end_date | str | 'YYYY-MM-DD' | ✅ | End date (inclusive) |

**Parameter Validation**:
- `symbol`: Must be 6-digit numeric string
- `start_date`, `end_date`: Must be valid dates, start_date ≤ end_date

### Returns
**Success**: pd.DataFrame with columns:
```python
['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
```

**Failure**: Empty pd.DataFrame (pd.DataFrame())

### Column Specifications
| Column | Type | Unit | Description |
|--------|------|------|-------------|
| date | datetime64 | YYYY-MM-DD | Trading date |
| open | float64 | CNY | Opening price |
| high | float64 | CNY | Highest price |
| low | float64 | CNY | Lowest price |
| close | float64 | CNY | Closing price |
| volume | int64 | Lots (100 shares) | Trading volume |
| amount | float64 | CNY | Trading amount |

### Error Handling
- **Network failure**: Log error, return empty DataFrame
- **Invalid symbol**: Log warning, return empty DataFrame
- **Invalid date format**: Normalize date first, if fails return empty DataFrame
- **No data available**: Return empty DataFrame (not an error)

### Example Usage
```python
adapter = TdxDataSource()
df = adapter.get_stock_daily('600519', '2024-01-01', '2024-12-31')

# Success case
assert not df.empty
assert len(df) > 0
assert 'date' in df.columns
assert df['date'].min() >= pd.Timestamp('2024-01-01')
assert df['date'].max() <= pd.Timestamp('2024-12-31')

# Failure case (invalid symbol)
df_empty = adapter.get_stock_daily('999999', '2024-01-01', '2024-12-31')
assert df_empty.empty
```

### Implementation Notes
- Call `pytdx.get_security_bars(category=9, market, code, start, count)`
- Handle pagination (max 800 records per request)
- Map Chinese column names to English using `ColumnMapper`
- Apply `normalize_date()` to all date strings

---

## Method 2: get_index_daily

### Signature
```python
def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame
```

### Purpose
Fetch daily data for stock indices (e.g., 000001.SH for SSE Composite Index).

### Parameters
Same as `get_stock_daily`

### Returns
Same DataFrame structure as `get_stock_daily`

### Differences from get_stock_daily
- Uses `pytdx.get_index_bars()` instead of `get_security_bars()`
- Index symbols may have different code ranges (e.g., '000001' for 深证成指)

### Example Usage
```python
# 上证指数
df = adapter.get_index_daily('000001', '2024-01-01', '2024-12-31')
assert not df.empty
assert 'close' in df.columns
```

---

## Method 3: get_stock_basic

### Signature
```python
def get_stock_basic(self, symbol: str) -> Dict
```

### Purpose
Fetch basic information about a stock (name, industry, listing date, etc.).

### Parameters
| Parameter | Type | Format | Required | Description |
|-----------|------|--------|----------|-------------|
| symbol | str | '600519' | ✅ | 6-digit stock code |

### Returns
**Success**: Dict with keys:
```python
{
    'code': str,           # Stock code
    'name': str,           # Stock name (Chinese)
    'industry': str,       # Industry classification (optional)
    'list_date': str,      # Listing date ('YYYY-MM-DD')
    'total_share': float,  # Total shares (10k shares)
    'float_share': float   # Float shares (10k shares)
}
```

**Failure**: Empty dict ({})

### Implementation Status
**⚠️ Partial Support**: pytdx's `get_company_info_content()` returns unstructured text, not JSON.

**Current Implementation**:
- `code`: From parameter
- `name`: Extracted from API response
- `industry`: NULL (not available from pytdx)
- `list_date`: NULL (requires parsing)
- `total_share`, `float_share`: Fetched from `get_finance_info()`

### Example Usage
```python
info = adapter.get_stock_basic('600519')

# Minimal success case
assert info.get('code') == '600519'
assert info.get('name') is not None
assert len(info.get('name', '')) > 0

# Optional fields may be None
assert 'industry' in info  # Key exists but value may be None
```

---

## Method 4: get_index_components

### Signature
```python
def get_index_components(self, symbol: str) -> List[str]
```

### Purpose
Fetch list of constituent stocks for an index (e.g., 沪深300 components).

### Parameters
| Parameter | Type | Format | Required | Description |
|-----------|------|--------|----------|-------------|
| symbol | str | 'HS300' or '000300' | ✅ | Index identifier |

### Returns
**Success**: List of stock codes
```python
['600519', '000001', '600036', ...]
```

**Failure**: Empty list ([])

### Implementation Status
**⚠️ Limited Support**: pytdx provides `get_block_info()` for sector constituents, but may not cover all indices.

**Current Implementation**:
- Works for sector indices (industry, concept)
- May not work for composite indices (沪深300, 中证500)
- Returns empty list with warning if data unavailable

### Example Usage
```python
components = adapter.get_index_components('HS300')

# Success case
assert isinstance(components, list)
assert len(components) > 0
assert all(isinstance(code, str) for code in components)
assert all(len(code) == 6 for code in components)

# Failure case
components_empty = adapter.get_index_components('UNKNOWN_INDEX')
assert components_empty == []
```

---

## Method 5: get_real_time_data

### Signature
```python
def get_real_time_data(self, symbol: str) -> Union[Dict, str]
```

### Purpose
Fetch real-time market quote for a single stock.

### Parameters
| Parameter | Type | Format | Required | Description |
|-----------|------|--------|----------|-------------|
| symbol | str | '600519' | ✅ | 6-digit stock code |

### Returns
**Success**: Dict with keys:
```python
{
    'code': str,           # Stock code
    'name': str,           # Stock name
    'price': float,        # Current price
    'pre_close': float,    # Previous close
    'open': float,         # Today's open
    'high': float,         # Today's high
    'low': float,          # Today's low
    'volume': int,         # Volume (lots)
    'amount': float,       # Amount (CNY)
    'bid1': float,         # Bid price 1
    'bid1_volume': int,    # Bid volume 1
    'ask1': float,         # Ask price 1
    'ask1_volume': int,    # Ask volume 1
    'timestamp': str       # Query timestamp ('YYYY-MM-DD HH:MM:SS')
}
```

**Failure**: Error message string (str)

### Error Handling
**Return String on Error**:
- Network failure: "Network error: {error_message}"
- Invalid symbol: "Invalid symbol: {symbol}"
- TDX server unavailable: "TDX server unavailable"

### Example Usage
```python
quote = adapter.get_real_time_data('600519')

# Success case
assert isinstance(quote, dict)
assert quote['code'] == '600519'
assert quote['price'] > 0
assert 'timestamp' in quote

# Failure case
error_msg = adapter.get_real_time_data('INVALID')
assert isinstance(error_msg, str)
assert 'error' in error_msg.lower()
```

### Batch Query Extension (Non-IDataSource)
**Optional Method**: `get_real_time_data_batch(symbols: List[str]) -> pd.DataFrame`

```python
# Batch query for multiple stocks
df = adapter.get_real_time_data_batch(['600519', '000001', '600036'])
assert len(df) == 3
assert 'price' in df.columns
```

---

## Method 6: get_market_calendar

### Signature
```python
def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame
```

### Purpose
Fetch trading calendar (which days are trading days).

### Parameters
| Parameter | Type | Format | Required | Description |
|-----------|------|--------|----------|-------------|
| start_date | str | 'YYYY-MM-DD' | ✅ | Start date |
| end_date | str | 'YYYY-MM-DD' | ✅ | End date |

### Returns
**Expected** (if supported):
```python
# DataFrame with columns: ['date', 'is_open']
pd.DataFrame({
    'date': ['2024-01-01', '2024-01-02', ...],
    'is_open': [False, True, ...]  # False = holiday, True = trading day
})
```

**Actual (TDX)**: Empty DataFrame

### Implementation Status
**❌ Not Supported**: pytdx does not provide trading calendar API.

**Stub Implementation**:
```python
def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
    self.logger.warning("get_market_calendar not supported by TDX adapter")
    return pd.DataFrame()
```

### Example Usage
```python
df = adapter.get_market_calendar('2024-01-01', '2024-12-31')

# Always returns empty
assert df.empty

# Use alternative data source (e.g., akshare)
akshare_adapter = AkshareDataSource()
df = akshare_adapter.get_market_calendar('2024-01-01', '2024-12-31')
assert not df.empty
```

---

## Method 7: get_financial_data

### Signature
```python
def get_financial_data(self, symbol: str, period: str = 'quarter') -> pd.DataFrame
```

### Purpose
Fetch financial statements and indicators for a stock.

### Parameters
| Parameter | Type | Values | Required | Description |
|-----------|------|--------|----------|-------------|
| symbol | str | '600519' | ✅ | 6-digit stock code |
| period | str | 'quarter' or 'annual' | ❌ (default: 'quarter') | Report period type |

### Returns
**Success**: pd.DataFrame with columns:
```python
['date', 'revenue', 'net_profit', 'eps', 'roe', 'pe', 'pb', 'total_share', 'float_share']
```

**Failure**: Empty DataFrame

### Column Specifications
| Column | Type | Unit | Description |
|--------|------|------|-------------|
| date | datetime64 | YYYY-MM-DD | Report date |
| revenue | float64 | 万元 (10k CNY) | Operating revenue |
| net_profit | float64 | 万元 (10k CNY) | Net profit |
| eps | float64 | CNY | Earnings per share |
| roe | float64 | % | Return on equity |
| pe | float64 | Ratio | Price-to-earnings ratio |
| pb | float64 | Ratio | Price-to-book ratio |
| total_share | int64 | 万股 (10k shares) | Total share capital |
| float_share | int64 | 万股 (10k shares) | Float share capital |

### Implementation Notes
- Call `pytdx.get_finance_info(market, code)`
- pytdx returns single snapshot (latest quarter), not historical time series
- `period` parameter ignored (pytdx limitation)

### Example Usage
```python
df = adapter.get_financial_data('600519', period='quarter')

# Success case
assert not df.empty
assert 'revenue' in df.columns
assert 'net_profit' in df.columns
assert df['pe'].iloc[0] > 0
```

---

## Method 8: get_news_data

### Signature
```python
def get_news_data(self, symbol: str, limit: int = 20) -> List[Dict]
```

### Purpose
Fetch news articles related to a stock.

### Parameters
| Parameter | Type | Range | Required | Description |
|-----------|------|-------|----------|-------------|
| symbol | str | '600519' | ✅ | 6-digit stock code |
| limit | int | 1-100 | ❌ (default: 20) | Max number of articles |

### Returns
**Expected** (if supported):
```python
[
    {
        'title': str,          # Article title
        'content': str,        # Article content (summary)
        'publish_time': str,   # Publish time ('YYYY-MM-DD HH:MM:SS')
        'source': str          # News source
    },
    ...
]
```

**Actual (TDX)**: Empty list ([])

### Implementation Status
**❌ Not Supported**: pytdx does not provide news API.

**Stub Implementation**:
```python
def get_news_data(self, symbol: str, limit: int = 20) -> List[Dict]:
    self.logger.warning("get_news_data not supported by TDX adapter")
    return []
```

### Example Usage
```python
news = adapter.get_news_data('600519', limit=10)

# Always returns empty
assert news == []

# Use alternative data source
akshare_adapter = AkshareDataSource()
news = akshare_adapter.get_news_data('600519', limit=10)
assert len(news) > 0
```

---

## Contract Compliance Summary

| Method | Support Level | pytdx API | Notes |
|--------|--------------|-----------|-------|
| get_stock_daily | ✅ Full | get_security_bars(9) | Pagination required |
| get_index_daily | ✅ Full | get_index_bars(9) | Works for all indices |
| get_stock_basic | ⚠️ Partial | get_company_info_content() | Unstructured text, limited fields |
| get_index_components | ⚠️ Limited | get_block_info() | Works for sectors, not all indices |
| get_real_time_data | ✅ Full | get_security_quotes() | Supports batch extension |
| get_market_calendar | ❌ Stub | N/A | Returns empty DataFrame |
| get_financial_data | ⚠️ Limited | get_finance_info() | Latest snapshot only |
| get_news_data | ❌ Stub | N/A | Returns empty list |

**Compliance Score**: 6/8 full or partial support (75%)

---

## Type Checking

### mypy Configuration
```ini
[mypy]
python_version = 3.11
strict = True
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### Expected mypy Output
```bash
$ mypy adapters/tdx_adapter.py
Success: no issues found in 1 source file
```

---

## Contract Testing

### Test Suite: test_tdx_contract.py

#### Test 1: Interface Implementation
```python
def test_implements_all_methods():
    """Verify TdxDataSource implements all 8 IDataSource methods"""
    from interfaces.data_source import IDataSource
    from adapters.tdx_adapter import TdxDataSource

    assert issubclass(TdxDataSource, IDataSource)

    required_methods = [
        'get_stock_daily',
        'get_index_daily',
        'get_stock_basic',
        'get_index_components',
        'get_real_time_data',
        'get_market_calendar',
        'get_financial_data',
        'get_news_data'
    ]

    adapter = TdxDataSource()
    for method in required_methods:
        assert hasattr(adapter, method)
        assert callable(getattr(adapter, method))
```

#### Test 2: Return Types
```python
def test_return_types():
    """Verify all methods return correct types"""
    adapter = TdxDataSource()

    # DataFrame methods
    df = adapter.get_stock_daily('600519', '2024-01-01', '2024-01-31')
    assert isinstance(df, pd.DataFrame)

    df = adapter.get_index_daily('000001', '2024-01-01', '2024-01-31')
    assert isinstance(df, pd.DataFrame)

    df = adapter.get_market_calendar('2024-01-01', '2024-12-31')
    assert isinstance(df, pd.DataFrame)

    df = adapter.get_financial_data('600519')
    assert isinstance(df, pd.DataFrame)

    # Dict/str method
    result = adapter.get_real_time_data('600519')
    assert isinstance(result, (dict, str))

    # List method
    news = adapter.get_news_data('600519')
    assert isinstance(news, list)

    # Dict method
    info = adapter.get_stock_basic('600519')
    assert isinstance(info, dict)

    # List method
    components = adapter.get_index_components('HS300')
    assert isinstance(components, list)
```

#### Test 3: Error Handling
```python
def test_no_exceptions_raised():
    """Verify errors return empty results, not exceptions"""
    adapter = TdxDataSource()

    # All methods should handle errors gracefully
    df = adapter.get_stock_daily('INVALID', '2024-01-01', '2024-01-31')
    assert df.empty  # Not raising exception

    info = adapter.get_stock_basic('999999')
    assert info == {}  # Not raising exception

    components = adapter.get_index_components('UNKNOWN')
    assert components == []  # Not raising exception
```

---

## Contract Violations

### Violation: Method Not Implemented
**Detection**: Python ABC raises `TypeError` at instantiation
```python
>>> adapter = IncompleteAdapter()
TypeError: Can't instantiate abstract class IncompleteAdapter with abstract methods get_stock_daily
```

### Violation: Wrong Return Type
**Detection**: Type checker (mypy) or runtime assertion
```python
# mypy error
error: Incompatible return value type (got "str", expected "DataFrame")

# Runtime assertion
assert isinstance(df, pd.DataFrame), f"Expected DataFrame, got {type(df)}"
```

### Violation: Missing Columns
**Detection**: Unit test assertion
```python
df = adapter.get_stock_daily('600519', '2024-01-01', '2024-01-31')
required_cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
assert all(col in df.columns for col in required_cols), f"Missing columns: {set(required_cols) - set(df.columns)}"
```

---

## Contract Evolution

### Version Compatibility
- **v1.0**: Initial contract (current)
- **v2.0** (planned): Add async methods (`async def get_stock_daily_async(...)`)

### Deprecation Policy
- If method signature changes, old signature deprecated for 2 versions
- Use `@deprecated` decorator with migration guide
- Example:
  ```python
  from typing import deprecated

  @deprecated("Use get_stock_daily_v2() instead")
  def get_stock_daily(self, symbol: str, start_date: str, end_date: str):
      return self.get_stock_daily_v2(symbol, start_date, end_date)
  ```

---

**Contract Version**: 1.0
**Last Updated**: 2025-10-15
**Next Review**: Upon interface changes or TDX API updates
