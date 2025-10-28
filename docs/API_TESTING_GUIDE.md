# MyStocks API Testing Guide

## API Endpoint Testing

### Testing UnifiedManager API

The `MyStocksUnifiedManager` provides the primary API for data operations:

```python
from unified_manager import MyStocksUnifiedManager
from core.data_classification import DataClassification
import pandas as pd

manager = MyStocksUnifiedManager()

# 1. Save data by classification
df = pd.DataFrame({
    'ts': pd.date_range('2025-01-01', periods=100, freq='1s'),
    'price': [10.5 + i*0.01 for i in range(100)],
    'volume': [1000 * (i+1) for i in range(100)],
})

result = manager.save_data_by_classification(
    DataClassification.TICK_DATA,
    df,
    "tick_600000"
)
assert result is True

# 2. Load data by classification
df_loaded = manager.load_data_by_classification(
    DataClassification.DAILY_KLINE,
    "daily_kline",
    filters={
        'start_time': '2024-01-01',
        'end_time': '2024-12-31',
    }
)
assert df_loaded is not None

# 3. Get routing information
routing_info = manager.get_routing_info(DataClassification.TICK_DATA)
assert routing_info['target_db'] == 'tdengine'
assert routing_info['retention_days'] == 30
```

### Testing Data Classification System

The data classification system determines which database to use:

```python
from core.data_classification import DataClassification, DatabaseTarget
from core.data_manager import DataManager

manager = DataManager()

# Test routing for all data types
routing_map = {
    DataClassification.TICK_DATA: DatabaseTarget.TDENGINE,
    DataClassification.MINUTE_KLINE: DatabaseTarget.TDENGINE,
    DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,
    DataClassification.SYMBOLS_INFO: DatabaseTarget.POSTGRESQL,
    DataClassification.TECHNICAL_INDICATORS: DatabaseTarget.POSTGRESQL,
    DataClassification.TRADE_CALENDAR: DatabaseTarget.POSTGRESQL,
    DataClassification.INDUSTRY_CLASS: DatabaseTarget.POSTGRESQL,
    DataClassification.ORDER_RECORDS: DatabaseTarget.POSTGRESQL,
}

for classification, expected_db in routing_map.items():
    target = manager.get_target_database(classification)
    assert target == expected_db, f"Classification {classification} routing failed"
```

### Testing Data Access Layer APIs

#### TDengineDataAccess API

```python
from data_access.tdengine_access import TDengineDataAccess
import pandas as pd
from datetime import datetime

access = TDengineDataAccess()

# 1. Create super table (time-series data)
schema = {
    'ts': 'TIMESTAMP',
    'price': 'FLOAT',
    'volume': 'INT',
}
tags = {
    'symbol': 'BINARY(20)',
    'exchange': 'BINARY(10)',
}
access.create_stable('tick_data', schema, tags)

# 2. Insert batch data
df = pd.DataFrame({
    'ts': pd.date_range('2025-01-01', periods=1000, freq='1s'),
    'price': [10.0 + i*0.01 for i in range(1000)],
    'volume': [1000 * (i+1) for i in range(1000)],
})
rows_inserted = access.insert_dataframe('tick_data_600000', df)
assert rows_inserted == 1000

# 3. Query by time range
start_time = datetime(2025, 1, 1, 9, 30)
end_time = datetime(2025, 1, 1, 15, 0)
result_df = access.query_by_time_range('tick_data_600000', start_time, end_time)
assert len(result_df) > 0

# 4. Aggregate to K-line
kline_df = access.aggregate_to_kline(
    'tick_data_600000',
    start_time,
    end_time,
    interval='5m'
)
assert 'open' in kline_df.columns
assert 'high' in kline_df.columns
assert 'low' in kline_df.columns
assert 'close' in kline_df.columns

# 5. Delete old data
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
deleted = access.delete_by_time_range('tick_data_600000', start_date, end_date)
assert deleted > 0
```

#### PostgreSQLDataAccess API

```python
from data_access.postgresql_access import PostgreSQLDataAccess
import pandas as pd

access = PostgreSQLDataAccess()

# 1. Create regular table
schema = {
    'symbol': 'VARCHAR(20)',
    'date': 'DATE',
    'open': 'DECIMAL(10,2)',
    'high': 'DECIMAL(10,2)',
    'low': 'DECIMAL(10,2)',
    'close': 'DECIMAL(10,2)',
    'volume': 'BIGINT',
}
access.create_table('daily_kline', schema, primary_key='symbol, date')

# 2. Create hypertable for time-series (optional)
access.create_hypertable('daily_kline_ts', time_column='date')

# 3. Insert data
df = pd.DataFrame({
    'symbol': ['600000.SH'] * 100,
    'date': pd.date_range('2024-01-01', periods=100, freq='D'),
    'open': [10.0 + i*0.1 for i in range(100)],
    'high': [10.5 + i*0.1 for i in range(100)],
    'low': [9.5 + i*0.1 for i in range(100)],
    'close': [10.2 + i*0.1 for i in range(100)],
    'volume': [1000000 * (i+1) for i in range(100)],
})
rows = access.insert_dataframe('daily_kline', df)
assert rows == 100

# 4. Upsert (insert or update)
conflict_columns = ['symbol', 'date']
rows = access.upsert_dataframe('daily_kline', df, conflict_columns=conflict_columns)
assert rows >= 100

# 5. Query with filter
result_df = access.query(
    'daily_kline',
    columns=['symbol', 'date', 'close'],
    where="symbol = '600000.SH' AND date >= '2024-06-01'"
)
assert result_df['symbol'].unique()[0] == '600000.SH'

# 6. Query by time range
from datetime import datetime
result_df = access.query_by_time_range(
    'daily_kline',
    'date',
    datetime(2024, 1, 1),
    datetime(2024, 12, 31)
)
assert len(result_df) == 100

# 7. Execute custom SQL
result_df = access.execute_sql(
    "SELECT symbol, AVG(close) as avg_price FROM daily_kline WHERE date >= %s GROUP BY symbol",
    params=('2024-01-01',)
)
assert 'avg_price' in result_df.columns

# 8. Delete data
deleted = access.delete('daily_kline', "date < '2020-01-01'")
print(f"Deleted {deleted} rows")
```

## Error Handling Tests

### Testing Connection Failures

```python
def test_connection_failure_recovery():
    """Test system recovers from connection failures"""
    manager = MyStocksUnifiedManager()

    # Simulate connection failure
    with patch.object(
        manager._data_manager,
        "save_data",
        side_effect=ConnectionError("Database unavailable")
    ):
        try:
            manager.save_data_by_classification(
                DataClassification.TICK_DATA,
                test_df,
                "tick_600000"
            )
        except ConnectionError:
            # Expected - system properly reports connection error
            print("Connection error detected and reported")
```

### Testing Timeout Handling

```python
def test_timeout_handling():
    """Test system handles timeout gracefully"""
    manager = MyStocksUnifiedManager()

    with patch.object(
        manager._data_manager,
        "save_data",
        side_effect=TimeoutError("Query timeout")
    ):
        try:
            manager.save_data_by_classification(...)
        except TimeoutError:
            # Expected - timeout properly reported
            print("Timeout detected and reported")
```

## Integration Tests

### Testing Multi-Database Operations

```python
def test_multi_database_operations():
    """Test simultaneous operations on multiple databases"""
    manager = MyStocksUnifiedManager()

    # Prepare test data for different databases
    tick_data = pd.DataFrame({...})  # For TDengine
    daily_data = pd.DataFrame({...})  # For PostgreSQL

    # Save to TDengine
    result1 = manager.save_data_by_classification(
        DataClassification.TICK_DATA,
        tick_data,
        "tick_600000"
    )
    assert result1 is True

    # Save to PostgreSQL
    result2 = manager.save_data_by_classification(
        DataClassification.DAILY_KLINE,
        daily_data,
        "daily_kline"
    )
    assert result2 is True

    # Verify both databases received data
    target1 = manager.get_routing_info(DataClassification.TICK_DATA)['target_db']
    target2 = manager.get_routing_info(DataClassification.DAILY_KLINE)['target_db']

    assert target1 == 'tdengine'
    assert target2 == 'postgresql'
```

### Testing Data Consistency

```python
def test_data_consistency():
    """Verify data remains consistent across operations"""
    manager = MyStocksUnifiedManager()

    # Original data
    original_df = pd.DataFrame({
        'symbol': ['600000.SH'] * 50,
        'trade_date': pd.date_range('2024-01-01', periods=50),
        'close': [10.0 + i*0.1 for i in range(50)],
        'volume': [1000000 * (i+1) for i in range(50)],
    })

    # Save data
    manager.save_data_by_classification(
        DataClassification.DAILY_KLINE,
        original_df,
        "daily_kline"
    )

    # Load data back
    loaded_df = manager.load_data_by_classification(
        DataClassification.DAILY_KLINE,
        "daily_kline"
    )

    # Verify consistency
    assert len(loaded_df) == len(original_df)
    assert list(loaded_df.columns) == list(original_df.columns)
    assert (loaded_df['symbol'] == original_df['symbol']).all()
```

## Performance Testing

### Testing Throughput

```python
import time

def test_data_throughput():
    """Test maximum data throughput"""
    manager = MyStocksUnifiedManager()

    # Generate large dataset
    df = pd.DataFrame({
        'ts': pd.date_range('2025-01-01', periods=100000, freq='100ms'),
        'price': np.random.uniform(10, 20, 100000),
        'volume': np.random.randint(100, 1000, 100000),
    })

    start = time.time()
    result = manager.save_data_by_classification(
        DataClassification.TICK_DATA,
        df,
        "tick_600000"
    )
    elapsed = time.time() - start

    throughput = len(df) / elapsed
    print(f"Throughput: {throughput:.0f} rows/second")

    assert throughput > 100000  # Target: 100K+ rows/sec
```

### Testing Latency

```python
import time

def test_routing_latency():
    """Test routing latency is sub-millisecond"""
    manager = DataManager()

    latencies = []
    for _ in range(1000):
        start = time.perf_counter()
        target = manager.get_target_database(DataClassification.TICK_DATA)
        elapsed = time.perf_counter() - start
        latencies.append(elapsed)

    avg_latency_us = (np.mean(latencies) * 1000000)
    print(f"Average routing latency: {avg_latency_us:.2f} microseconds")

    assert avg_latency_us < 1  # Target: < 1 microsecond
```

## Best Practices

1. **Always use test fixtures** - Avoid recreating test data
2. **Mock external dependencies** - Don't rely on real databases
3. **Test error paths** - Include failure scenarios
4. **Measure performance** - Use timing to detect regressions
5. **Document test cases** - Clear docstrings for maintainability
6. **Keep tests independent** - Avoid test interdependencies
7. **Use parameterization** - Test multiple cases efficiently

## Debugging Tests

### Enable verbose output

```bash
pytest tests/ -v -s  # -s shows print statements
```

### Run specific test with debugging

```bash
pytest tests/unit/test_data_manager.py::TestDataManagerRouting::test_tick_data_routes_to_tdengine -v -s
```

### Use breakpoints (if using PyCharm/VSCode)

```python
def test_something():
    breakpoint()  # Execution stops here
    # Continue debugging
```

---

**Last Updated**: 2025-10-28
**Status**: Complete
