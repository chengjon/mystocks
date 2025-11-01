# Quickstart: Architecture Optimization Implementation

**Feature**: Architecture Optimization for Quantitative Trading System
**Branch**: `002-arch-optimization`
**Date**: 2025-10-25
**Target Audience**: Developers implementing this feature

## Overview

This guide provides step-by-step instructions for implementing the architecture optimization. The implementation is divided into 3 phases over 8 weeks:

- **Phase 0 (Week 1)**: Documentation & Database Migration
- **Phase 1 (Weeks 2-3)**: Adapter Consolidation
- **Phase 2 (Weeks 4-8)**: Core Refactoring & Testing

**Prerequisites**:
- Python 3.12 environment
- Git access to `002-arch-optimization` branch
- Access to TDengine and PostgreSQL databases
- Familiarity with pandas, sqlalchemy, pytest

---

## Phase 0: Documentation & Database Migration (Week 1)

### Step 1: Update Documentation (Days 1-2)

**Objective**: Align all documentation with 2-database architecture

**Files to Update**:
```bash
# 1. CLAUDE.md - Update database section
# OLD: "Week 3: simplified to 1 PostgreSQL database"
# NEW: "Week 3: simplified to 2 databases (TDengine + PostgreSQL)"

# 2. DATASOURCE_AND_DATABASE_ARCHITECTURE.md
# Update all architecture diagrams to show 2 databases

# 3. README.md
# Update system architecture overview

# 4. .env.example
# Remove MySQL_* and REDIS_* variables
# Keep only TDENGINE_* and POSTGRESQL_* variables
```

**Commands**:
```bash
# Create backup of current documentation
mkdir -p docs/backup_$(date +%Y%m%d)
cp CLAUDE.md DATASOURCE_AND_DATABASE_ARCHITECTURE.md README.md docs/backup_$(date +%Y%m%d)/

# Edit files (use your preferred editor)
vim CLAUDE.md
vim DATASOURCE_AND_DATABASE_ARCHITECTURE.md
vim README.md
vim .env.example

# Verify changes
git diff CLAUDE.md
git diff .env.example
```

### Step 2: Database Migration Script (Days 3-4)

**Objective**: Migrate MySQL data to PostgreSQL

**Create Migration Script** (`scripts/migrate_mysql_to_postgresql.py`):
```python
#!/usr/bin/env python3
"""
Migrate MySQL data to PostgreSQL

Usage:
    python scripts/migrate_mysql_to_postgresql.py --dry-run  # Preview only
    python scripts/migrate_mysql_to_postgresql.py            # Execute migration
"""

import argparse
import os
from typing import List, Tuple
import pandas as pd
from sqlalchemy import create_engine, inspect
from loguru import logger

# Configuration
MYSQL_URL = os.getenv("MYSQL_URL", "mysql+pymysql://user:pass@localhost/mystocks")
POSTGRESQL_URL = os.getenv("POSTGRESQL_URL", "postgresql://user:pass@localhost/mystocks")

# Tables to migrate
TABLES_TO_MIGRATE = [
    "symbols_info",
    "contract_info",
    "trade_calendar",
    "data_source_status",
    "task_schedules",
    "strategy_parameters",
    "system_config",
]

def backup_database(engine, backup_path: str):
    """Create backup of current PostgreSQL data"""
    logger.info(f"Creating backup at {backup_path}")
    # Implementation: pg_dump logic
    pass

def get_table_row_count(engine, table_name: str) -> int:
    """Get row count for a table"""
    with engine.connect() as conn:
        result = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        return result.scalar()

def migrate_table(mysql_engine, postgresql_engine, table_name: str, dry_run: bool) -> Tuple[int, int]:
    """
    Migrate single table from MySQL to PostgreSQL

    Returns:
        (rows_read, rows_written)
    """
    logger.info(f"Migrating table: {table_name}")

    # 1. Read from MySQL
    df = pd.read_sql_table(table_name, mysql_engine)
    rows_read = len(df)
    logger.info(f"  Read {rows_read} rows from MySQL")

    if dry_run:
        logger.info(f"  DRY RUN: Would write {rows_read} rows to PostgreSQL")
        return rows_read, 0

    # 2. Write to PostgreSQL
    df.to_sql(table_name, postgresql_engine, if_exists='append', index=False)
    rows_written = len(df)
    logger.info(f"  Wrote {rows_written} rows to PostgreSQL")

    # 3. Verify integrity
    pg_count = get_table_row_count(postgresql_engine, table_name)
    assert pg_count >= rows_written, f"Row count mismatch for {table_name}"

    return rows_read, rows_written

def main():
    parser = argparse.ArgumentParser(description="Migrate MySQL to PostgreSQL")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    # Connect to databases
    mysql_engine = create_engine(MYSQL_URL)
    postgresql_engine = create_engine(POSTGRESQL_URL)

    # Create backup
    if not args.dry_run:
        backup_database(postgresql_engine, f"/opt/claude/mystocks_backup/pre_migration_{date}.sql")

    # Migrate each table
    total_rows = 0
    for table in TABLES_TO_MIGRATE:
        try:
            rows_read, rows_written = migrate_table(mysql_engine, postgresql_engine, table, args.dry_run)
            total_rows += rows_read
        except Exception as e:
            logger.error(f"Failed to migrate {table}: {e}")
            raise

    logger.success(f"Migration complete! Total rows: {total_rows}")

if __name__ == "__main__":
    main()
```

**Execute Migration**:
```bash
# 1. Dry run first
python scripts/migrate_mysql_to_postgresql.py --dry-run

# 2. Review output, then execute
python scripts/migrate_mysql_to_postgresql.py

# 3. Verify migration
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', database='mystocks', user='user', password='pass')
cur = conn.cursor()
cur.execute(\"SELECT tablename FROM pg_tables WHERE schemaname='public'\")
print('PostgreSQL tables:', [row[0] for row in cur.fetchall()])
"
```

### Step 3: Remove Redis Dependencies (Day 5)

**Objective**: Remove Redis from codebase

**Files to Modify**:
```bash
# 1. Remove Redis imports and connections
grep -r "import redis" . --include="*.py"
grep -r "RedisAccess" . --include="*.py"

# 2. Comment out Redis-related code in:
#    - core.py (DataStorageStrategy)
#    - unified_manager.py (Redis connection)
#    - data_access.py (RedisDataAccess class)

# 3. Update requirements.txt
sed -i '/redis/d' requirements.txt

# 4. Update .env
# Remove REDIS_* variables
```

**Verification**:
```bash
# Ensure system still runs without Redis
python -c "from unified_manager import MyStocksUnifiedManager; mgr = MyStocksUnifiedManager(); print('OK')"
```

---

## Phase 1: Adapter Consolidation (Weeks 2-3)

### Step 4: Enhance AkShare Adapter (Week 2, Days 1-3)

**Objective**: Merge financial_adapter and customer_adapter into akshare_adapter

**Create Enhanced Adapter** (`adapters/akshare_adapter_v2.py`):
```python
from typing import Optional, List
import pandas as pd
import akshare as ak

class AkShareAdapter:
    """Enhanced AkShare adapter with efinance and easyquotation integration"""

    def __init__(self, proxy=None, enable_efinance=True, enable_easyquotation=True):
        self.proxy = proxy
        self.efinance_enabled = enable_efinance
        self.easyquotation_enabled = enable_easyquotation

        # Initialize efinance and easyquotation if enabled
        if self.efinance_enabled:
            import efinance as ef
            self.efinance = ef

        if self.easyquotation_enabled:
            import easyquotation
            self.easyquotation = easyquotation.use('sina')

    # ========= Core Methods (from original akshare_adapter) =========

    def get_kline_data(self, symbol, period, start_date, end_date, adjust="qfq"):
        df = ak.stock_zh_a_hist(symbol=symbol, period=period,
                                start_date=start_date, end_date=end_date,
                                adjust=adjust)
        return df

    def get_realtime_quotes(self, symbols, fields=None):
        if self.easyquotation_enabled:
            # Use easyquotation for faster real-time quotes
            quotes = self.easyquotation.stocks(symbols)
            return pd.DataFrame(quotes).T
        else:
            # Fallback to akshare
            df = ak.stock_zh_a_spot_em()
            return df[df['代码'].isin(symbols)]

    # ========= Enhanced Methods (from financial_adapter) =========

    def get_financial_statements(self, symbol, statement_type, start_date, end_date):
        """Financial statements using efinance"""
        if not self.efinance_enabled:
            return None

        if statement_type == "income":
            df = self.efinance.stock.get_income_statement(symbol)
        elif statement_type == "balance":
            df = self.efinance.stock.get_balance_sheet(symbol)
        elif statement_type == "cashflow":
            df = self.efinance.stock.get_cash_flow(symbol)
        else:
            return None

        # Filter by date range
        df = df[(df['report_date'] >= start_date) & (df['report_date'] <= end_date)]
        return df

    def get_capital_flow(self, symbol, start_date, end_date):
        """Capital flow using efinance"""
        if self.efinance_enabled:
            df = self.efinance.stock.get_quote_history(symbol, beg=start_date, end=end_date)
            return df
        else:
            # Fallback to akshare
            df = ak.stock_individual_fund_flow(symbol=symbol, market="沪深A股")
            return df

    # ... implement other methods
```

**Testing**:
```python
# Test enhanced adapter
def test_akshare_adapter_v2():
    adapter = AkShareAdapter(enable_efinance=True, enable_easyquotation=True)

    # Test K-line (original functionality)
    df1 = adapter.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")
    assert df1 is not None

    # Test financial statements (merged from financial_adapter)
    df2 = adapter.get_financial_statements("600000", "income", "2023-01-01", "2023-12-31")
    assert df2 is not None

    # Test capital flow (merged from financial_adapter)
    df3 = adapter.get_capital_flow("600000", "2024-01-01", "2024-01-31")
    assert df3 is not None

    print("✓ All tests passed")
```

### Step 5: Implement Runtime Adapter Registration (Week 2, Days 4-5)

**Objective**: Add hot-plug capability to DataManager

**Modify `core.py`** (add DataManager class):
```python
from typing import Dict, Optional
from threading import RLock
import logging

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        self._adapters: Dict[str, 'IDataSource'] = {}
        self._adapter_lock = RLock()
        self._register_core_adapters()

    def _register_core_adapters(self):
        """Register core adapters at initialization"""
        from adapters.tdx_adapter import TDXAdapter
        from adapters.akshare_adapter_v2 import AkShareAdapter
        from adapters.byapi_adapter import ByapiAdapter

        self.register_adapter("tdx", TDXAdapter())
        self.register_adapter("akshare", AkShareAdapter())
        self.register_adapter("byapi", ByapiAdapter())
        logger.info("Core adapters registered")

    def register_adapter(self, name: str, adapter: 'IDataSource') -> bool:
        """Register adapter at runtime (hot-plug)"""
        with self._adapter_lock:
            if name in self._adapters:
                logger.warning(f"Adapter '{name}' already registered")
                return False

            self._adapters[name] = adapter
            logger.info(f"Adapter '{name}' registered successfully")
            return True

    def unregister_adapter(self, name: str) -> bool:
        """Unregister adapter at runtime (hot-unplug)"""
        with self._adapter_lock:
            if name not in self._adapters:
                logger.warning(f"Adapter '{name}' not found")
                return False

            # Prevent unregistering core adapters
            if name in ["tdx", "akshare", "byapi"]:
                logger.error(f"Cannot unregister core adapter '{name}'")
                return False

            del self._adapters[name]
            logger.info(f"Adapter '{name}' unregistered successfully")
            return True

    def list_adapters(self) -> List[str]:
        """List all registered adapter names"""
        with self._adapter_lock:
            return list(self._adapters.keys())

    def get_adapter(self, name: str) -> Optional['IDataSource']:
        """Get adapter instance by name"""
        with self._adapter_lock:
            return self._adapters.get(name)
```

**Testing**:
```python
def test_runtime_registration():
    manager = DataManager()

    # List core adapters
    adapters = manager.list_adapters()
    assert "tdx" in adapters
    assert "akshare" in adapters
    assert "byapi" in adapters

    # Register custom adapter
    class CustomAdapter:
        def get_realtime_quotes(self, symbols, fields=None):
            return pd.DataFrame({'symbol': symbols, 'price': [100.0] * len(symbols)})

    assert manager.register_adapter("custom", CustomAdapter()) == True

    # Try to register duplicate
    assert manager.register_adapter("custom", CustomAdapter()) == False

    # Unregister custom adapter
    assert manager.unregister_adapter("custom") == True

    # Try to unregister core adapter (should fail)
    assert manager.unregister_adapter("tdx") == False

    print("✓ Runtime registration tests passed")
```

### Step 6: Deprecate Old Adapters (Week 3)

**Objective**: Mark old adapters as deprecated, redirect to new ones

**Add Deprecation Warnings**:
```python
# In adapters/financial_adapter.py
import warnings

class FinancialDataSource:
    def __init__(self):
        warnings.warn(
            "FinancialDataSource is deprecated. Use AkShareAdapter instead. "
            "This adapter will be removed in version 3.0.",
            DeprecationWarning,
            stacklevel=2
        )
        # Internally delegate to AkShareAdapter
        from adapters.akshare_adapter_v2 import AkShareAdapter
        self._delegate = AkShareAdapter(enable_efinance=True)

    def get_financial_statements(self, *args, **kwargs):
        return self._delegate.get_financial_statements(*args, **kwargs)
```

**Update Documentation**:
```markdown
# adapters/README.md

## Adapter Status (as of 2025-10-25)

**Active Adapters** (use these):
- `akshare_adapter_v2.py`: Core comprehensive adapter (recommended)
- `tdx_adapter.py`: Local high-speed data
- `byapi_adapter.py`: Alternative API source

**Deprecated Adapters** (will be removed in v3.0):
- `financial_adapter.py`: Use `akshare_adapter_v2` instead
- `customer_adapter.py`: Use `akshare_adapter_v2` instead
- `akshare_proxy_adapter.py`: Use `akshare_adapter_v2(proxy=...)` instead

**Removed Adapters** (no longer supported):
- `tushare_adapter.py`: Use AkShare or Tushare Pro directly
```

---

## Phase 2: Core Refactoring (Weeks 4-8)

### Step 7: Implement Simplified Classifications (Week 4)

**Objective**: Reduce from 34 to 10 classifications

**Update `core.py`**:
```python
# Replace old DataClassification enum with new simplified version
# (Use the enum definition from data_classification_schema.md)

from enum import Enum

class DataClassification(Enum):
    HIGH_FREQUENCY = "high_frequency"
    HISTORICAL_KLINE = "historical_kline"
    REALTIME_SNAPSHOT = "realtime_snapshot"
    INDUSTRY_SECTOR = "industry_sector"
    CONCEPT_THEME = "concept_theme"
    FINANCIAL_FUNDAMENTAL = "financial_fundamental"
    CAPITAL_FLOW = "capital_flow"
    CHIP_DISTRIBUTION = "chip_distribution"
    NEWS_ANNOUNCEMENT = "news_announcement"
    DERIVED_INDICATOR = "derived_indicator"

# Update mapping
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
    return CLASSIFICATION_DB_MAPPING[classification]
```

**Migration Mapping**:
```python
# Create migration helper
OLD_TO_NEW_CLASSIFICATION = {
    "tick_data": DataClassification.HIGH_FREQUENCY,
    "minute_kline": DataClassification.HIGH_FREQUENCY,
    "daily_kline": DataClassification.HISTORICAL_KLINE,
    "symbols_info": DataClassification.INDUSTRY_SECTOR,
    # ... map all 34 old classifications to 10 new ones
}

def migrate_classification(old_classification: str) -> DataClassification:
    return OLD_TO_NEW_CLASSIFICATION.get(
        old_classification,
        DataClassification.HISTORICAL_KLINE  # Default fallback
    )
```

### Step 8: Implement Cache-First Retrieval (Weeks 5-6)

**Objective**: Add PostgreSQL cache layer with fallback strategy

**Create `core.py` cache methods**:
```python
class DataManager:
    # ... (existing methods)

    def get_kline_data(self, symbol, period, start_date, end_date, adjust="qfq"):
        """Retrieve K-line with cache-first strategy"""
        data_type = f"kline_{period}"

        # Tier 1: Check PostgreSQL cache
        cached_data = self._query_cache(symbol, data_type, start_date, end_date)
        if cached_data is not None and self._is_cache_complete(cached_data, start_date, end_date):
            logger.info(f"Cache hit: {symbol} {data_type}")
            return cached_data

        # Tier 2: Try TDX local
        tdx_adapter = self.get_adapter("tdx")
        if tdx_adapter:
            try:
                data = tdx_adapter.get_kline_data(symbol, period, start_date, end_date, adjust)
                if data is not None:
                    self._update_cache(symbol, data_type, data)
                    return data
            except Exception as e:
                logger.warning(f"TDX failed: {e}")

        # Tier 3: Try network sources
        for adapter_name in ["akshare", "baostock", "byapi"]:
            adapter = self.get_adapter(adapter_name)
            if adapter:
                try:
                    data = adapter.get_kline_data(symbol, period, start_date, end_date, adjust)
                    if data is not None:
                        self._update_cache(symbol, data_type, data)
                        return data
                except Exception as e:
                    logger.warning(f"{adapter_name} failed: {e}")

        logger.error(f"All sources failed for {symbol} {data_type}")
        return None

    def _query_cache(self, symbol, data_type, start_date, end_date):
        """Query PostgreSQL cache"""
        # Implementation: SELECT from data_cache table
        pass

    def _update_cache(self, symbol, data_type, data):
        """Update PostgreSQL cache"""
        # Implementation: UPSERT to data_cache table
        pass

    def _is_cache_complete(self, cached_data, start_date, end_date):
        """Check if cache covers date range"""
        return (cached_data['date'].min() <= start_date and
                cached_data['date'].max() >= end_date)
```

### Step 9: Testing & Validation (Weeks 7-8)

**Objective**: Comprehensive testing of new architecture

**Create Test Suite** (`tests/test_architecture_optimization.py`):
```python
import pytest
from core import DataManager, DataClassification

@pytest.fixture
def manager():
    return DataManager()

def test_cache_first_retrieval(manager):
    # First call: cache miss
    df1 = manager.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")
    assert df1 is not None

    # Second call: cache hit (verify by checking logs or mocking)
    df2 = manager.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")
    assert df2 is not None
    assert df1.equals(df2)

def test_adapter_fallback(manager):
    # Simulate TDX failure, verify fallback to AkShare
    # (Use mocking to control adapter behavior)
    pass

def test_classification_routing(manager):
    # Verify each classification routes to correct database
    assert get_target_database(DataClassification.HIGH_FREQUENCY) == "tdengine"
    assert get_target_database(DataClassification.HISTORICAL_KLINE) == "postgresql"

def test_performance_targets(manager):
    import time

    # Cache hit latency <10ms
    start = time.time()
    df = manager.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")  # Cache hit
    latency = (time.time() - start) * 1000
    assert latency < 10, f"Cache hit too slow: {latency}ms"

# Run tests
pytest.main(["-v", "tests/test_architecture_optimization.py"])
```

---

## Common Issues & Troubleshooting

### Issue 1: Migration Verification Failed

**Symptom**: Row count mismatch after MySQL → PostgreSQL migration

**Solution**:
```bash
# Check source and target row counts
python -c "
import pymysql, psycopg2

# MySQL
mysql_conn = pymysql.connect(host='localhost', user='user', password='pass', database='mystocks')
mysql_cur = mysql_conn.cursor()
mysql_cur.execute('SELECT COUNT(*) FROM symbols_info')
mysql_count = mysql_cur.fetchone()[0]

# PostgreSQL
pg_conn = psycopg2.connect(host='localhost', user='user', password='pass', database='mystocks')
pg_cur = pg_conn.cursor()
pg_cur.execute('SELECT COUNT(*) FROM symbols_info')
pg_count = pg_cur.fetchone()[0]

print(f'MySQL: {mysql_count}, PostgreSQL: {pg_count}')
"

# If mismatch, re-run migration with --verbose flag
python scripts/migrate_mysql_to_postgresql.py --verbose --table symbols_info
```

### Issue 2: Adapter Registration Thread Safety

**Symptom**: "Adapter already registered" errors in multi-threaded environment

**Solution**: Ensure all adapter registration happens during initialization, not in request handlers:
```python
# WRONG: Registering in request handler
def handle_request():
    manager.register_adapter("custom", CustomAdapter())  # Not thread-safe

# CORRECT: Register during initialization
manager = DataManager()
manager.register_adapter("custom", CustomAdapter())  # Thread-safe

# Then use in request handlers
def handle_request():
    adapter = manager.get_adapter("custom")  # Read-only, thread-safe
```

### Issue 3: Cache Hit Rate Lower Than Expected

**Symptom**: Cache hit rate <50% (target: >90%)

**Diagnosis**:
```python
# Check cache statistics
stats = manager.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']:.1f}%")
print(f"Cache entries: {stats['total_entries']}")

# Check cache TTL configuration
config = manager.get_config()
print(f"Cache TTL: {config['cache_ttl']}")
```

**Solutions**:
- Increase cache TTL for historical data
- Pre-populate cache with common queries
- Check if cache invalidation is too aggressive

---

## Performance Benchmarks

### Target Latencies

| Operation | Target | How to Measure |
|-----------|--------|----------------|
| Cache hit | <10ms | `time.time()` around query call |
| TDX hit | <20ms | Same |
| Network hit | <200ms | Same |

### Benchmarking Script

```python
import time
import pandas as pd

def benchmark_query_latency(manager, iterations=100):
    latencies = []

    for i in range(iterations):
        start = time.time()
        df = manager.get_kline_data("600000", "daily", "2024-01-01", "2024-01-31")
        latency = (time.time() - start) * 1000
        latencies.append(latency)

    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

    print(f"Average latency: {avg_latency:.1f}ms")
    print(f"P95 latency: {p95_latency:.1f}ms")

    # Verify targets
    assert avg_latency < 80, f"Average latency too high: {avg_latency}ms"
    assert p95_latency < 120, f"P95 latency too high: {p95_latency}ms"

# Run benchmark
manager = DataManager()
benchmark_query_latency(manager)
```

---

## Next Steps

After completing this implementation:

1. **Run Full Test Suite**: `pytest tests/ -v --cov=. --cov-report=html`
2. **Performance Validation**: Verify <80ms average latency target
3. **Code Review**: Use `code-reviewer` agent for quality check
4. **Documentation Update**: Ensure all docs reflect new architecture
5. **Team Training**: Conduct walkthrough session (aim for 6-hour onboarding)
6. **Production Deployment**: Gradual rollout with monitoring

---

## Additional Resources

- **Research Document**: [research.md](./research.md) - Architectural decisions and rationale
- **Data Model**: [data-model.md](./data-model.md) - Entity definitions and relationships
- **API Contracts**: [contracts/](./contracts/) - Interface specifications
- **Specification**: [spec.md](./spec.md) - Complete feature requirements

For questions or issues, refer to these documents or consult the original first-principles analysis at `/opt/claude/mystocks_spec/DATASOURCE_ARCHITECTURE_FIRST_PRINCIPLES_ANALYSIS.md`.
