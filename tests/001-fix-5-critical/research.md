# Technical Research & Decisions

**Feature**: Fix 5 Critical Issues in OpenStock Demo
**Date**: 2025-10-20
**Phase**: 0 - Research & Analysis

## Overview

This document captures technical decisions, alternatives considered, and best practices for implementing fixes to 5 critical OpenStock Demo issues.

---

## 1. PostgreSQL Watchlist Schema Design

### Decision

Use simple relational schema with two tables:
- `watchlist_groups`: Stores user-defined groups for organizing stocks
- `user_watchlist`: Stores individual stock entries within groups

**Schema**:
```sql
CREATE TABLE watchlist_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sort_order INTEGER DEFAULT 0,
    stock_count INTEGER DEFAULT 0,
    UNIQUE(user_id, group_name)
);

CREATE TABLE user_watchlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL REFERENCES watchlist_groups(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE(user_id, group_id, stock_code)
);
```

### Rationale

1. **Foreign Key CASCADE**: When group deleted, all stocks in group automatically removed (prevents orphaned records)
2. **UNIQUE Constraints**: Prevent duplicate group names per user and duplicate stocks per group
3. **stock_count Denormalization**: Cache count for performance (avoid COUNT(*) queries), updated via triggers
4. **sort_order**: Allows user customization of group display order
5. **notes Field**: Enables users to annotate watchlist items

### Alternatives Considered

**Alternative 1**: Single table with NULL group_id for ungrouped stocks
- **Rejected**: Harder to ensure "default group" always exists; more NULL handling in queries

**Alternative 2**: Use JSONB column for flexible metadata
- **Rejected**: Loses relational integrity; harder to query and enforce constraints

**Alternative 3**: No foreign keys (application-level integrity)
- **Rejected**: Risk of orphaned records; violates database best practices

### Best Practices Applied

- PostgreSQL naming conventions (lowercase, underscores)
- Indexed foreign keys for join performance
- Timestamps for auditability (created_at, added_at)
- VARCHAR lengths match Chinese stock codes (6 digits + exchange suffix = ~10 chars, use 20 for safety)

---

## 2. Stock Code Normalization & Exchange Detection

### Decision

Implement auto-detection logic based on first digit of stock code:
- **600xxx, 601xxx, 603xxx, 688xxx** → Shanghai Stock Exchange (SH)
- **000xxx, 001xxx, 002xxx, 003xxx, 300xxx, 301xxx** → Shenzhen Stock Exchange (SZ)
- **6xxxxx** (other 6-prefix) → Shanghai Stock Exchange (SH)
- **0xxxxx, 3xxxxx** (other) → Shenzhen Stock Exchange (SZ)

**Function signature**:
```python
def normalize_stock_code(code: str, market: str = "cn") -> str:
    """
    Normalize stock code by adding exchange suffix if missing

    Args:
        code: 6-digit stock code (e.g., "600519" or "600519.SH")
        market: Market type ("cn" for A-share, "hk" for H-share)

    Returns:
        Normalized code with exchange suffix (e.g., "600519.SH")

    Raises:
        ValueError: If code format is invalid
    """
```

### Rationale

1. **Deterministic Logic**: First-digit rules cover 99% of A-share codes
2. **Backward Compatible**: Codes already with suffix pass through unchanged
3. **Validation**: Rejects invalid formats (non-numeric, wrong length)
4. **H-share Support**: Market parameter allows future HK stock handling

### Alternatives Considered

**Alternative 1**: Database lookup for every code
- **Rejected**: Requires maintaining stock universe table; adds latency; unnecessary for well-defined code ranges

**Alternative 2**: Ask user to always provide exchange suffix
- **Rejected**: Poor UX; OpenStock users expect automatic detection

**Alternative 3**: Try both exchanges on failure
- **Rejected**: Doubles API calls; adds latency; masks real errors

### Best Practices Applied

- Chinese Stock Market Standards (CSRC regulations)
- Fail-fast validation (raise ValueError early)
- Explicit rather than implicit (market parameter)

### Edge Cases Handled

- Codes with existing suffix → Return as-is (idempotent)
- Invalid length → Raise ValueError with clear message
- Non-numeric characters → Raise ValueError
- Empty/None input → Raise ValueError

---

## 3. AKShare API Integration Patterns

### Decision

Use AKShare library functions with standardized error handling:

**Real-Time Quotes**:
```python
import akshare as ak

def fetch_realtime_quote(stock_code: str) -> Dict:
    """Fetch real-time quote using akshare"""
    try:
        # akshare.stock_zh_a_spot_em() for A-share real-time data
        df = ak.stock_zh_a_spot_em()
        # Filter by normalized code
        quote = df[df['代码'] == stock_code.split('.')[0]]
        if quote.empty:
            raise ValueError(f"Stock {stock_code} not found")
        return quote.iloc[0].to_dict()
    except Exception as e:
        logger.error(f"AKShare quote fetch failed: {e}")
        raise
```

**K-Line Data**:
```python
def fetch_kline_data(stock_code: str, period: str = "daily", adjust: str = "qfq") -> pd.DataFrame:
    """Fetch K-line data using akshare"""
    try:
        # akshare.stock_zh_a_hist() for historical data
        df = ak.stock_zh_a_hist(
            symbol=stock_code.split('.')[0],  # Remove exchange suffix
            period=period,  # daily, weekly, monthly
            adjust=adjust   # qfq (forward), hfq (backward), or "" (none)
        )
        return df
    except Exception as e:
        logger.error(f"AKShare kline fetch failed: {e}")
        raise
```

### Rationale

1. **AKShare Advantages**: Free, no API key required, covers Chinese markets comprehensively
2. **DataFrame Format**: Pandas integration simplifies data transformation
3. **Adjustment Options**: qfq (前复权) most common for price continuity
4. **Error Logging**: Captures failures for debugging

### Alternatives Considered

**Alternative 1**: TuShare API
- **Rejected**: Requires paid API token; rate limits; not installed in project

**Alternative 2**: Direct exchange APIs
- **Rejected**: Complex authentication; different formats per exchange; overkill for demo

**Alternative 3**: Cache market data in database
- **Rejected**: Out of scope for P0 fixes; adds storage complexity

### Best Practices Applied

- Asyncio-compatible wrappers (run akshare in thread pool if needed)
- Timeout handling (default 10 seconds for external calls)
- Graceful degradation (return error message, don't crash)

### Performance Considerations

- AKShare queries typically complete in 1-3 seconds
- K-line data size: ~60 trading days × 9 fields × 8 bytes = ~4 KB (well within limits)
- No caching needed for demo (acceptable latency)

---

## 4. FastAPI Async Patterns for External APIs

### Decision

Use `asyncio.to_thread()` to wrap synchronous AKShare calls in async endpoints:

```python
from fastapi import APIRouter
import asyncio

@router.get("/api/market/kline")
async def get_kline(stock_code: str, period: str = "daily"):
    """Async endpoint wrapping synchronous akshare call"""
    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(
        None,  # Use default executor
        fetch_kline_data,  # Synchronous function
        stock_code,
        period
    )
    return df.to_dict(orient="records")
```

### Rationale

1. **Non-Blocking**: Prevents blocking FastAPI event loop during I/O
2. **Compatibility**: AKShare is synchronous (no async support)
3. **Simple**: `run_in_executor()` is standard Python pattern
4. **Scalable**: Thread pool handles multiple concurrent requests

### Alternatives Considered

**Alternative 1**: Keep endpoints synchronous (def instead of async def)
- **Rejected**: Blocks event loop; reduces server throughput; bad practice for I/O-bound operations

**Alternative 2**: Use httpx for direct HTTP calls to data sources
- **Rejected**: Loses AKShare abstraction; need to reimplement parsing logic

**Alternative 3**: Celery background tasks
- **Rejected**: Overkill for demo; adds Redis dependency; increases deployment complexity

### Best Practices Applied

- FastAPI async/await conventions
- Thread pool for CPU-bound/sync operations
- Timeout handling (via asyncio.wait_for if needed)

---

## 5. ECharts K-Line Chart Configuration

### Decision

Use ECharts candlestick series with Chinese market conventions:

```javascript
const option = {
  xAxis: {
    type: 'category',
    data: dates,  // ['2025-01-01', '2025-01-02', ...]
    axisLabel: {
      formatter: (value) => value.slice(5)  // Show MM-DD only
    }
  },
  yAxis: { type: 'value', scale: true },
  series: [
    {
      type: 'candlestick',
      data: klineData,  // [[open, close, low, high], ...]
      itemStyle: {
        color: '#ef5350',      // Red for rising (Chinese convention)
        color0: '#26a69a',     // Green for falling (Chinese convention)
        borderColor: '#ef5350',
        borderColor0: '#26a69a'
      }
    },
    {
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: volumeData,  // [volume1, volume2, ...]
      itemStyle: {
        color: (params) => params.data >= prevVolume ? '#ef5350' : '#26a69a'
      }
    }
  ]
};
```

### Rationale

1. **Chinese Convention**: Red = rising, Green = falling (opposite of Western markets)
2. **Dual Y-Axis**: Price on primary, volume on secondary axis
3. **Date Formatting**: MM-DD format for space efficiency
4. **Interactive**: ECharts provides built-in zoom, tooltip, data view

### Alternatives Considered

**Alternative 1**: TradingView widget
- **Rejected**: Requires external account; limited customization; overkill for basic charts

**Alternative 2**: Lightweight Charts library
- **Rejected**: Less feature-rich; requires manual volume integration

**Alternative 3**: D3.js custom implementation
- **Rejected**: High development cost; ECharts provides everything needed

### Best Practices Applied

- Responsive design (chart resizes with container)
- Lazy loading (only fetch data when tab activated)
- Error states (show message if data fetch fails)

---

## 6. Frontend Test Button Implementation

### Decision

Add test button handlers in `OpenStockDemo.vue` that execute actual API calls with sample data:

```vue
<script setup>
const testAPI = async (apiName) => {
  testStatus[apiName] = 'testing';
  try {
    let result;
    switch (apiName) {
      case 'search':
        result = await searchStocks('茅台', 'cn');
        break;
      case 'quote':
        result = await getStockQuote('600519', 'cn');
        break;
      case 'news':
        result = await getStockNews('600519', 'cn');
        break;
      case 'watchlist':
        result = await getWatchlistGroups();
        break;
      case 'kline':
        result = await getKlineData('600519', 'daily');
        break;
    }
    testStatus[apiName] = result ? 'pass' : 'fail';
    testResults[apiName] = result;
  } catch (error) {
    testStatus[apiName] = 'fail';
    testErrors[apiName] = error.message;
  }
};
</script>
```

### Rationale

1. **Real Tests**: Execute actual API calls (not mocks)
2. **Sample Data**: Use well-known stocks (贵州茅台 600519) for reliability
3. **Status Indicators**: Visual feedback (pending/testing/pass/fail)
4. **Error Display**: Show error messages for debugging

### Alternatives Considered

**Alternative 1**: Mock API responses
- **Rejected**: Doesn't verify real backend connectivity

**Alternative 2**: Separate test page
- **Rejected**: Splits functionality; users want inline testing

**Alternative 3**: Automated tests only (no UI)
- **Rejected**: Not user-visible; doesn't meet requirement for "Test" buttons in UI

### Best Practices Applied

- Vue 3 Composition API (reactive refs)
- Try-catch error handling
- Loading states (prevent double-clicks)
- Clear visual indicators (✓ Pass, ✗ Fail)

---

## 7. Migration Script Execution Strategy

### Decision

Use simple SQL script executed via psql command:

```bash
psql -h localhost -U mystocks -d mystocks -f migrations/001_watchlist_tables.sql
```

**Migration file structure**:
```sql
-- migrations/001_watchlist_tables.sql
BEGIN;

-- Create tables
CREATE TABLE IF NOT EXISTS watchlist_groups (...);
CREATE TABLE IF NOT EXISTS user_watchlist (...);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_watchlist_groups_user ...;
CREATE INDEX IF NOT EXISTS idx_user_watchlist_user_group ...;

-- Create trigger for stock_count maintenance
CREATE OR REPLACE FUNCTION update_group_stock_count() ...;
CREATE TRIGGER trg_update_stock_count ...;

-- Insert default group for existing users
INSERT INTO watchlist_groups (user_id, group_name, created_at)
SELECT id, '默认分组', CURRENT_TIMESTAMP
FROM users
ON CONFLICT (user_id, group_name) DO NOTHING;

COMMIT;
```

### Rationale

1. **Simplicity**: No ORM migration framework needed for 2 tables
2. **Idempotent**: `IF NOT EXISTS` and `ON CONFLICT` allow re-running
3. **Transactional**: BEGIN/COMMIT ensures atomicity
4. **Default Data**: Creates "默认分组" for existing users

### Alternatives Considered

**Alternative 1**: Alembic migration framework
- **Rejected**: Overkill for simple schema; adds dependency; requires setup

**Alternative 2**: Python script with psycopg2
- **Rejected**: More code; less transparent than SQL

**Alternative 3**: Manual execution via pgAdmin/DBeaver
- **Rejected**: Not repeatable; no version control integration

### Best Practices Applied

- Version-numbered migrations (001_*, 002_*, etc.)
- BEGIN/COMMIT transactions
- IF NOT EXISTS for idempotency
- Comments documenting purpose

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Database Schema** | Two tables with foreign key cascade | Referential integrity, automatic cleanup |
| **Stock Code Logic** | First-digit pattern matching | Deterministic, fast, 99% coverage |
| **Market Data API** | AKShare library | Free, comprehensive, no auth required |
| **Async Pattern** | asyncio.to_thread() wrapper | Non-blocking I/O without rewriting akshare |
| **Chart Library** | ECharts candlestick | Feature-rich, Chinese conventions built-in |
| **Test Buttons** | Real API calls with sample data | Verifies actual functionality |
| **Migration** | Plain SQL script via psql | Simple, transparent, version-controlled |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| AKShare API changes | Medium | High | Version pin akshare; add error handling |
| Invalid stock codes from users | High | Low | Validate format; clear error messages |
| PostgreSQL performance (large watchlists) | Low | Medium | Indexes on foreign keys; tested < 100 items |
| Frontend state management bugs | Medium | Low | Vue DevTools debugging; comprehensive testing |
| Migration conflicts (existing data) | Low | High | ON CONFLICT clauses; test on staging first |

---

## Next Steps (Phase 1)

1. Create data-model.md defining entities
2. Generate API contracts in contracts/ directory
3. Write quickstart.md for developer onboarding
4. Update agent context with technical stack details
