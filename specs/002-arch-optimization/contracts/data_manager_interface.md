# API Contract: DataManager Interface

**Feature**: Architecture Optimization for Quantitative Trading System
**Branch**: `002-arch-optimization`
**Date**: 2025-10-25
**Contract Type**: Data Manager Layer Interface (Layer 2)

## Overview

This contract defines the `DataManager` class interface, which serves as the core orchestration layer in the 3-layer architecture. DataManager handles:
- Data classification and routing
- Cache-first retrieval strategy
- Runtime adapter registration/unregistration
- Validation and deduplication
- Query optimization

## Design Principles

**1. Unified Entry Point**: All data operations go through UnifiedDataManager → DataManager

**2. Classification-Based Routing**: Automatic database selection based on data type

**3. Cache-First Strategy**: PostgreSQL cache → Local (TDX) → Network (AkShare → Baostock → Byapi)

**4. Runtime Flexibility**: Hot-plug adapter registration without restart

**5. Fail-Fast Validation**: Validate inputs before expensive operations

---

## DataManager Class Interface

### Class Definition

```python
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from threading import RLock
import pandas as pd
from enum import Enum

class DataManager:
    """
    Core data orchestration layer (Layer 2).

    Responsibilities:
    - Classification-based routing to databases
    - Cache-first data retrieval with fallback chain
    - Runtime adapter registration/unregistration
    - Input validation and data deduplication
    - Query performance optimization
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize DataManager with optional configuration.

        Args:
            config: Configuration dict with keys:
                   - 'cache_enabled': bool (default: True)
                   - 'cache_ttl': dict {data_type: seconds}
                   - 'adapter_priority': list [adapter_names]
                   - 'validation_strict': bool (default: True)

        Example:
            >>> manager = DataManager(config={
            ...     'cache_enabled': True,
            ...     'adapter_priority': ['postgresql_cache', 'tdx', 'akshare', 'baostock', 'byapi']
            ... })
        """
        ...

    # ============================================================================
    # Group 1: Adapter Management (Runtime Registration)
    # ============================================================================

    def register_adapter(self, name: str, adapter: 'IDataSource') -> bool:
        """
        Register a new adapter at runtime (hot-plug).

        Thread-safe operation using internal lock. Core adapters are
        pre-registered at initialization; custom adapters can be added
        dynamically.

        Args:
            name: Unique adapter identifier (e.g., "custom_scraper")
            adapter: Adapter instance implementing IDataSource protocol

        Returns:
            True if registration successful
            False if name already exists or adapter invalid

        Raises:
            ValueError: If adapter doesn't implement IDataSource protocol

        Example:
            >>> custom_adapter = CustomNewsScraperAdapter(url="...")
            >>> manager.register_adapter("custom_news", custom_adapter)
            True
        """
        ...

    def unregister_adapter(self, name: str) -> bool:
        """
        Unregister an adapter at runtime (hot-unplug).

        Thread-safe operation. Core adapters (tdx, akshare, byapi)
        cannot be unregistered.

        Args:
            name: Adapter identifier to remove

        Returns:
            True if unregistration successful
            False if adapter not found or is core adapter

        Example:
            >>> manager.unregister_adapter("custom_news")
            True
        """
        ...

    def list_adapters(self) -> List[Dict[str, any]]:
        """
        List all registered adapters with metadata.

        Returns:
            List of dicts containing:
            - name: str (adapter identifier)
            - type: str ("core", "optional", "custom")
            - priority: int (lower = higher priority)
            - source_type: str ("local" or "network")
            - rate_limit: Optional[int] (requests per minute)
            - is_active: bool

        Example:
            >>> manager.list_adapters()
            [
                {'name': 'tdx', 'type': 'core', 'priority': 1, 'source_type': 'local',
                 'rate_limit': None, 'is_active': True},
                {'name': 'akshare', 'type': 'core', 'priority': 2, 'source_type': 'network',
                 'rate_limit': None, 'is_active': True},
                ...
            ]
        """
        ...

    def get_adapter(self, name: str) -> Optional['IDataSource']:
        """
        Get adapter instance by name (for direct use if needed).

        Args:
            name: Adapter identifier

        Returns:
            Adapter instance or None if not found

        Example:
            >>> adapter = manager.get_adapter("akshare")
            >>> if adapter:
            ...     df = adapter.get_realtime_quotes(["600000"])
        """
        ...

    # ============================================================================
    # Group 2: Data Retrieval (Cache-First Strategy)
    # ============================================================================

    def get_kline_data(self,
                       symbol: str,
                       period: str,
                       start_date: str,
                       end_date: str,
                       adjust: str = "qfq") -> Optional[pd.DataFrame]:
        """
        Retrieve K-line data with cache-first strategy.

        Retrieval Priority:
        1. Check PostgreSQL cache (data_cache table)
        2. If miss, try TDX local source (if available)
        3. If miss, try network sources: AkShare → Baostock → Byapi
        4. Cache results for future queries

        Args:
            symbol: Stock code (e.g., "600000")
            period: K-line period ("tick", "1min", "5min", ... "daily", "weekly", "monthly")
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")
            adjust: Adjustment type ("qfq", "hfq", "")

        Returns:
            DataFrame with columns: date, open, high, low, close, volume, amount
            Or None if all sources failed

        Performance:
            - Cache hit: <10ms
            - TDX hit: ~20ms
            - Network hit: ~100-200ms

        Example:
            >>> df = manager.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")
            >>> if df is not None:
            ...     print(f"Retrieved {len(df)} records")
        """
        ...

    def get_realtime_quotes(self,
                            symbols: List[str],
                            fields: Optional[List[str]] = None) -> Optional[pd.DataFrame]:
        """
        Get real-time quotes with cache-first strategy.

        Cache TTL: 1 second for real-time data

        Args:
            symbols: List of stock codes (e.g., ["600000", "000001"])
            fields: Optional field filter

        Returns:
            DataFrame with columns: symbol, price, volume, amount, bid1, ask1, ...
            Or None if all sources failed

        Example:
            >>> df = manager.get_realtime_quotes(["600000", "000001"])
            >>> if df is not None:
            ...     for _, row in df.iterrows():
            ...         print(f"{row['symbol']}: {row['price']}")
        """
        ...

    def get_industry_data(self,
                          data_type: str,
                          **params) -> Optional[pd.DataFrame]:
        """
        Get industry/sector data with unified interface.

        Args:
            data_type: Data type
                      - "industry_list": Get industry classification list
                      - "stock_industry": Get industry for specific stock
                      - "industry_stocks": Get stocks in specific industry
                      - "industry_index": Get industry index K-line
            **params: Type-specific parameters
                     - industry_list: classification="SW"
                     - stock_industry: symbol="600000", classification="SW"
                     - industry_stocks: industry_code="SW_01"
                     - industry_index: industry_code="SW_01", start_date, end_date

        Returns:
            DataFrame with type-specific columns
            Or None if all sources failed

        Example:
            >>> df = manager.get_industry_data("industry_list", classification="SW")
            >>> df = manager.get_industry_data("stock_industry", symbol="600000", classification="SW")
        """
        ...

    def get_concept_data(self,
                         data_type: str,
                         **params) -> Optional[pd.DataFrame]:
        """
        Get concept/theme plate data with unified interface.

        Args:
            data_type: Data type
                      - "concept_list": Get all concepts
                      - "concept_stocks": Get stocks in concept
                      - "stock_concepts": Get concepts for stock
            **params: Type-specific parameters

        Returns:
            DataFrame with type-specific columns
            Or None if all sources failed
        """
        ...

    def get_capital_flow(self,
                         symbol: str,
                         start_date: str,
                         end_date: str) -> Optional[pd.DataFrame]:
        """
        Get capital flow data with cache-first strategy.

        Returns main fund flow, retail flow, institutional flow data.

        Args:
            symbol: Stock code (e.g., "600000")
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")

        Returns:
            DataFrame with columns: date, main_fund_net, retail_fund_net,
                                   institutional_fund_net, super_large_net, ...
            Or None if all sources failed
        """
        ...

    def get_chip_distribution(self,
                              symbol: str,
                              calc_date: str) -> Optional[pd.DataFrame]:
        """
        Get chip distribution data.

        Args:
            symbol: Stock code (e.g., "600000")
            calc_date: Calculation date (format: "YYYY-MM-DD")

        Returns:
            DataFrame with columns: price_level, chip_ratio, profit_ratio
            Or None if all sources failed
        """
        ...

    def get_financial_data(self,
                           symbol: str,
                           data_type: str,
                           start_date: str,
                           end_date: str) -> Optional[pd.DataFrame]:
        """
        Get financial/fundamental data with unified interface.

        Args:
            symbol: Stock code (e.g., "600000")
            data_type: Data type
                      - "income": Income statement
                      - "balance": Balance sheet
                      - "cashflow": Cash flow statement
                      - "indicators": Financial indicators/ratios
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")

        Returns:
            DataFrame with type-specific columns
            Or None if all sources failed
        """
        ...

    # ============================================================================
    # Group 3: Data Storage (Classification-Based Routing)
    # ============================================================================

    def save_data(self,
                  symbol: str,
                  data_type: str,
                  data: pd.DataFrame,
                  classification: Optional['DataClassification'] = None) -> bool:
        """
        Save data with automatic classification and routing.

        Routing Logic:
        1. Determine classification (auto-detect or use provided)
        2. Map classification to database (TDengine or PostgreSQL)
        3. Validate data schema
        4. Perform deduplication
        5. Save to target database
        6. Update cache metadata

        Args:
            symbol: Stock code (e.g., "600000")
            data_type: Data type identifier (e.g., "kline_daily", "tick")
            data: DataFrame to save
            classification: Optional explicit classification
                          (auto-detected from data_type if None)

        Returns:
            True if save successful
            False if validation failed or database error

        Example:
            >>> df = pd.DataFrame({
            ...     'date': ['2024-01-02', '2024-01-03'],
            ...     'open': [15.20, 15.35],
            ...     'close': [15.40, 15.50],
            ...     ...
            ... })
            >>> manager.save_data("600000", "kline_daily", df)
            True
        """
        ...

    def save_batch(self,
                   batch_data: List[Tuple[str, str, pd.DataFrame]]) -> Dict[str, bool]:
        """
        Save multiple datasets in batch with performance optimization.

        Args:
            batch_data: List of (symbol, data_type, dataframe) tuples

        Returns:
            Dict mapping (symbol, data_type) to success status

        Example:
            >>> batch = [
            ...     ("600000", "kline_daily", df1),
            ...     ("000001", "kline_daily", df2),
            ... ]
            >>> results = manager.save_batch(batch)
            >>> print(f"Saved {sum(results.values())} / {len(batch)} datasets")
        """
        ...

    # ============================================================================
    # Group 4: Cache Management
    # ============================================================================

    def get_cache_stats(self) -> Dict[str, any]:
        """
        Get cache performance statistics.

        Returns:
            Dict containing:
            - total_entries: int (number of cached entries)
            - hit_rate: float (percentage of cache hits)
            - avg_hit_latency_ms: float
            - avg_miss_latency_ms: float
            - cache_size_mb: float
            - oldest_entry: datetime
            - newest_entry: datetime

        Example:
            >>> stats = manager.get_cache_stats()
            >>> print(f"Cache hit rate: {stats['hit_rate']:.1f}%")
        """
        ...

    def clear_cache(self,
                    symbol: Optional[str] = None,
                    data_type: Optional[str] = None,
                    before_date: Optional[str] = None) -> int:
        """
        Clear cache entries with optional filters.

        Args:
            symbol: Optional symbol filter (None = all symbols)
            data_type: Optional data type filter (None = all types)
            before_date: Optional date filter (clear entries older than this)

        Returns:
            Number of cache entries cleared

        Example:
            >>> # Clear all cache
            >>> manager.clear_cache()
            1234

            >>> # Clear cache for specific symbol
            >>> manager.clear_cache(symbol="600000")
            45

            >>> # Clear old cache entries
            >>> manager.clear_cache(before_date="2023-01-01")
            567
        """
        ...

    def refresh_cache(self,
                      symbol: str,
                      data_type: str,
                      start_date: str,
                      end_date: str) -> bool:
        """
        Force refresh cache by re-fetching from adapters.

        Args:
            symbol: Stock code
            data_type: Data type identifier
            start_date: Start date
            end_date: End date

        Returns:
            True if refresh successful
            False if all adapters failed

        Example:
            >>> # Force refresh today's data
            >>> manager.refresh_cache("600000", "kline_daily", "2024-01-31", "2024-01-31")
        """
        ...

    # ============================================================================
    # Group 5: Query Optimization & Validation
    # ============================================================================

    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate stock symbol format.

        Args:
            symbol: Stock code to validate

        Returns:
            True if valid (pattern: ^[0-9]{6}$, prefix: 60/00/30)
            False otherwise

        Example:
            >>> manager.validate_symbol("600000")  # Valid
            True
            >>> manager.validate_symbol("1234")    # Invalid (too short)
            False
        """
        ...

    def validate_date_range(self, start_date: str, end_date: str) -> bool:
        """
        Validate date range format and consistency.

        Args:
            start_date: Start date (format: "YYYY-MM-DD")
            end_date: End date (format: "YYYY-MM-DD")

        Returns:
            True if valid (proper format, start ≤ end, not future dates)
            False otherwise

        Example:
            >>> manager.validate_date_range("2024-01-01", "2024-01-31")
            True
            >>> manager.validate_date_range("2024-02-01", "2024-01-01")  # end < start
            False
        """
        ...

    def optimize_query(self,
                       query_params: Dict) -> Dict:
        """
        Optimize query parameters for better performance.

        Optimizations:
        - Split large date ranges into chunks
        - Reorder batch queries by data locality
        - Suggest alternative period for better performance

        Args:
            query_params: Dict with keys: symbol, period, start_date, end_date

        Returns:
            Optimized query_params dict

        Example:
            >>> params = {
            ...     'symbol': '600000',
            ...     'period': '1min',
            ...     'start_date': '2020-01-01',  # 4 years ago
            ...     'end_date': '2024-01-31'
            ... }
            >>> optimized = manager.optimize_query(params)
            >>> # May suggest: split into monthly chunks, or use daily + resample
        """
        ...

    # ============================================================================
    # Group 6: System Status & Health
    # ============================================================================

    def get_adapter_health(self) -> Dict[str, Dict[str, any]]:
        """
        Check health status of all registered adapters.

        Returns:
            Dict mapping adapter_name to health info:
            - is_available: bool
            - last_success: datetime (last successful query)
            - last_failure: datetime (last failed query)
            - success_rate: float (percentage)
            - avg_latency_ms: float

        Example:
            >>> health = manager.get_adapter_health()
            >>> for name, info in health.items():
            ...     if not info['is_available']:
            ...         print(f"Adapter {name} is DOWN")
        """
        ...

    def get_performance_metrics(self) -> Dict[str, any]:
        """
        Get overall system performance metrics.

        Returns:
            Dict containing:
            - total_queries: int
            - cache_hit_rate: float
            - avg_query_latency_ms: float
            - p95_query_latency_ms: float
            - errors_last_hour: int
            - active_adapters: int

        Example:
            >>> metrics = manager.get_performance_metrics()
            >>> if metrics['p95_query_latency_ms'] > 100:
            ...     print("WARNING: Query latency degraded")
        """
        ...

    # ============================================================================
    # Group 7: Configuration Management
    # ============================================================================

    def update_config(self, config_updates: Dict) -> bool:
        """
        Update DataManager configuration at runtime.

        Args:
            config_updates: Dict with configuration keys to update

        Returns:
            True if update successful
            False if invalid configuration

        Example:
            >>> manager.update_config({
            ...     'cache_enabled': False,  # Disable caching
            ...     'adapter_priority': ['akshare', 'tdx', 'byapi']  # New priority
            ... })
        """
        ...

    def get_config(self) -> Dict:
        """
        Get current DataManager configuration.

        Returns:
            Complete configuration dict

        Example:
            >>> config = manager.get_config()
            >>> print(f"Cache enabled: {config['cache_enabled']}")
        """
        ...
```

---

## Usage Examples

### Example 1: Basic Data Retrieval

```python
# Initialize manager
manager = DataManager()

# Retrieve K-line data (cache-first)
df = manager.get_kline_data(
    symbol="600000",
    period="daily",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

if df is not None:
    print(f"Retrieved {len(df)} daily K-lines")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
else:
    print("All data sources failed")
```

### Example 2: Runtime Adapter Registration

```python
# Create custom adapter
custom_scraper = CustomNewsScraperAdapter(url="https://example.com")

# Register at runtime (hot-plug)
if manager.register_adapter("custom_news", custom_scraper):
    print("Custom adapter registered successfully")

    # Use immediately
    news_df = manager.get_industry_data(
        "news",
        industry_code="SW_01",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )

# Later: unregister when no longer needed
manager.unregister_adapter("custom_news")
```

### Example 3: Batch Data Saving

```python
# Prepare batch data
batch = []
for symbol in ["600000", "000001", "000002"]:
    df = fetch_kline_data(symbol)  # Your data fetching logic
    batch.append((symbol, "kline_daily", df))

# Save in batch (optimized for performance)
results = manager.save_batch(batch)

# Check results
success_count = sum(results.values())
print(f"Saved {success_count} / {len(batch)} datasets")

# Report failures
for (symbol, data_type), success in results.items():
    if not success:
        print(f"Failed to save {symbol} {data_type}")
```

### Example 4: Cache Management

```python
# Check cache statistics
stats = manager.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.1f}%")
print(f"Cache size: {stats['cache_size_mb']:.1f} MB")

# Clear old cache entries (older than 3 months)
cutoff_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
cleared = manager.clear_cache(before_date=cutoff_date)
print(f"Cleared {cleared} old cache entries")

# Force refresh specific data
manager.refresh_cache("600000", "kline_daily", "2024-01-31", "2024-01-31")
```

### Example 5: Health Monitoring

```python
# Check adapter health
health = manager.get_adapter_health()
for adapter_name, info in health.items():
    status = "UP" if info['is_available'] else "DOWN"
    print(f"{adapter_name}: {status} (success rate: {info['success_rate']:.1f}%)")

# Get performance metrics
metrics = manager.get_performance_metrics()
if metrics['p95_query_latency_ms'] > 100:
    print("⚠️  WARNING: Query latency degraded")
    print(f"P95 latency: {metrics['p95_query_latency_ms']:.0f}ms")
```

---

## Error Handling

### Return Value Semantics

**Success**: Return `pd.DataFrame` or `True`

**All Sources Failed**: Return `None` or `False`
- Cache miss AND all adapters returned None
- Logged as warning with failure details

**Validation Failed**: Return `None` or `False`
- Invalid symbol format
- Invalid date range
- Logged as warning

**System Error**: Raise exception (rare)
- Database connection failure
- Configuration error
- Memory exhaustion

### Exception Types

```python
class DataManagerError(Exception):
    """Base exception for DataManager errors"""
    pass

class ValidationError(DataManagerError):
    """Input validation failed"""
    pass

class AdapterRegistrationError(DataManagerError):
    """Adapter registration/unregistration failed"""
    pass

class DatabaseError(DataManagerError):
    """Database operation failed"""
    pass
```

---

## Performance Guarantees

### Latency Targets

| Operation | Target Latency | Notes |
|-----------|---------------|-------|
| Cache hit | <10ms | PostgreSQL query only |
| TDX hit | <20ms | Local file read + cache update |
| Network hit | <200ms | API call + cache update |
| Batch save (10k records) | <2s | Bulk insert optimization |

### Throughput Targets

| Operation | Target Throughput | Notes |
|-----------|------------------|-------|
| Query operations | >1000 req/s | With 90% cache hit rate |
| Save operations | >500 writes/s | Batch mode |

---

## Thread Safety

**Thread-Safe Operations**:
- `register_adapter()` - Uses internal RLock
- `unregister_adapter()` - Uses internal RLock
- `get_*()` methods - Read-only, inherently thread-safe
- `save_*()` methods - Database-level locking

**Not Thread-Safe**:
- `update_config()` - Should be called during initialization only

---

## Testing Contract

### Unit Tests

```python
def test_cache_first_retrieval():
    manager = DataManager()

    # First call: cache miss, fetch from adapter
    df1 = manager.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")
    assert df1 is not None

    # Second call: cache hit, no adapter call
    with mock.patch.object(manager, '_query_adapters') as mock_adapters:
        df2 = manager.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")
        mock_adapters.assert_not_called()  # Cache hit, adapters not called
        assert df1.equals(df2)

def test_adapter_fallback_chain():
    manager = DataManager()
    manager.register_adapter("tdx", FailingAdapter())  # Always returns None
    manager.register_adapter("akshare", SucceedingAdapter())

    df = manager.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")
    assert df is not None  # Fallback to akshare succeeded
```

### Integration Tests

```python
def test_end_to_end_data_flow():
    manager = DataManager()

    # Save data
    df_original = create_test_kline_data()
    success = manager.save_data("600000", "kline_daily", df_original)
    assert success

    # Retrieve data (should hit cache)
    df_retrieved = manager.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")
    assert df_retrieved is not None
    assert len(df_retrieved) == len(df_original)

    # Verify cache was used
    stats = manager.get_cache_stats()
    assert stats['hit_rate'] > 0
```

---

## Versioning

**Version**: 1.0 (Initial release)

**Backward Compatibility**:
- Method signatures stable (parameters, return types)
- Configuration keys may be added (not removed)
- Internal implementation may change (cache strategy, routing logic)

---

## Conclusion

The DataManager interface provides:

1. **Unified API**: Single entry point for all data operations
2. **Intelligent Caching**: Cache-first strategy with 90%+ hit rate
3. **Runtime Flexibility**: Hot-plug adapter registration
4. **High Performance**: <80ms average query latency
5. **Production-Ready**: Error handling, monitoring, thread safety

Ready to proceed to Data Classification Schema contract.
