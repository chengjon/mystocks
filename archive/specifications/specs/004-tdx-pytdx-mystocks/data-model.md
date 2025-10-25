# Phase 1 Design: Data Model & Entities

**Feature**: TDX (pytdx) Data Source Adapter Integration
**Date**: 2025-10-15
**Status**: Design Complete

---

## Overview

This document defines the data entities and their relationships for the TDX data source adapter integration. The TdxDataSource adapter acts as a **data acquisition layer only** - it does not define new storage schemas or database tables. All data fetched from TDX servers is mapped to existing MyStocks data entities and routed to appropriate databases via the UnifiedManager.

**Key Principle**: Adapter is stateless and schema-agnostic. It transforms external TDX data formats into MyStocks standard formats, then delegates to existing storage infrastructure.

---

## Entity Catalog

### Entity 1: RealTimeQuote (实时行情)

**Source**: pytdx `get_security_quotes()` API
**Classification**: `DataClassification.REALTIME_QUOTES`
**Target Storage**: Redis (hot data cache)
**Update Frequency**: 3-5 seconds during market hours

#### Attributes

| Field | Type | Source Column (pytdx) | Description | Constraints |
|-------|------|---------------------|-------------|-------------|
| code | string | 'code' | 股票代码（6位数字） | NOT NULL, PK |
| name | string | 'name' | 股票名称 | |
| price | float | 'price' | 最新价 | >= 0 |
| pre_close | float | 'last_close' | 昨收价 | >= 0 |
| open | float | 'open' | 今开价 | >= 0 |
| high | float | 'high' | 最高价 | >= 0 |
| low | float | 'low' | 最低价 | >= 0 |
| volume | bigint | 'vol' | 成交量（手） | >= 0 |
| amount | float | 'amount' | 成交额（元） | >= 0 |
| bid1_price | float | 'bid1' | 买一价 | |
| bid1_volume | int | 'bid_vol1' | 买一量 | |
| ask1_price | float | 'ask1' | 卖一价 | |
| ask1_volume | int | 'ask_vol1' | 卖一量 | |
| timestamp | datetime | (system generated) | 查询时间戳 | NOT NULL |

#### Relationships
- **Many-to-One** with StockInfo (code → stock_code)
- Used by: Real-time monitoring systems, trading alerts

#### Data Flow
```
TDX Server → get_security_quotes() → TdxDataSource
  → ColumnMapper.to_english()
  → UnifiedManager.save_data_by_classification(REALTIME_QUOTES)
  → Redis (key: "quote:{code}", TTL: 60s)
```

---

### Entity 2: DailyKLine (日线K线)

**Source**: pytdx `get_security_bars(category=9)` API
**Classification**: `DataClassification.DAILY_KLINE`
**Target Storage**: PostgreSQL+TimescaleDB
**Update Frequency**: Daily after market close

#### Attributes

| Field | Type | Source Column (pytdx) | Description | Constraints |
|-------|------|---------------------|-------------|-------------|
| code | string | (parameter) | 股票代码 | NOT NULL, PK1 |
| date | date | 'datetime' | 交易日期 | NOT NULL, PK2 |
| open | float | 'open' | 开盘价 | >= 0 |
| high | float | 'high' | 最高价 | >= 0 |
| low | float | 'low' | 最低价 | >= 0 |
| close | float | 'close' | 收盘价 | >= 0 |
| volume | bigint | 'vol' | 成交量（手） | >= 0 |
| amount | float | 'amount' | 成交额（元） | >= 0 |

**Primary Key**: (code, date) - Composite key ensures unique daily records

#### Relationships
- **Many-to-One** with StockInfo (code → stock_code)
- Used by: Technical analysis, backtesting, historical charts

#### Data Flow
```
TDX Server → get_security_bars(9, market, code, start, count)
  → TdxDataSource.get_stock_daily()
  → ColumnMapper + normalize_date()
  → UnifiedManager.save_data_by_classification(DAILY_KLINE)
  → PostgreSQL+TimescaleDB (table: daily_klines, partitioned by date)
```

---

### Entity 3: MinuteKLine (分钟K线)

**Source**: pytdx `get_security_bars(category=4/5/6/7/8)` API
**Classification**: `DataClassification.MINUTE_KLINE`
**Target Storage**: TDengine
**Update Frequency**: Real-time during market hours

#### Attributes

| Field | Type | Source Column (pytdx) | Description | Constraints |
|-------|------|---------------------|-------------|-------------|
| code | string | (parameter) | 股票代码 | NOT NULL, PK1 |
| datetime | datetime | 'datetime' | 时间戳（精确到分钟） | NOT NULL, PK2 |
| period | string | (parameter) | K线周期（1min/5min/15min/30min/60min） | NOT NULL, PK3 |
| open | float | 'open' | 开盘价 | >= 0 |
| high | float | 'high' | 最高价 | >= 0 |
| low | float | 'low' | 最低价 | >= 0 |
| close | float | 'close' | 收盘价 | >= 0 |
| volume | bigint | 'vol' | 成交量（手） | >= 0 |
| amount | float | 'amount' | 成交额（元） | >= 0 |

**Primary Key**: (code, datetime, period) - Composite key with period dimension

**Category Mapping**:
- category=4 → period='1min'
- category=5 → period='5min'
- category=6 → period='15min'
- category=7 → period='30min'
- category=8 → period='60min'

#### Relationships
- **Many-to-One** with StockInfo (code → stock_code)
- Used by: Intraday analysis, high-frequency strategies

#### Data Flow
```
TDX Server → get_security_bars(4/5/6/7/8, market, code, start, count)
  → TdxDataSource (custom method, not IDataSource)
  → UnifiedManager.save_data_by_classification(MINUTE_KLINE)
  → TDengine (supertable: minute_klines, tags: {code, period})
```

---

### Entity 4: TickData (分笔成交)

**Source**: pytdx `get_transaction_data()` API
**Classification**: `DataClassification.TICK_DATA`
**Target Storage**: TDengine
**Update Frequency**: Real-time (millisecond level)

#### Attributes

| Field | Type | Source Column (pytdx) | Description | Constraints |
|-------|------|---------------------|-------------|-------------|
| code | string | (parameter) | 股票代码 | NOT NULL, PK1 |
| datetime | datetime | 'time' | 成交时间（精确到秒） | NOT NULL, PK2 |
| price | float | 'price' | 成交价 | >= 0 |
| volume | int | 'vol' | 成交量（手） | >= 0 |
| bs_flag | string | 'bs_flag' | 买卖方向 | 'BUY'/'SELL'/'NEUTRAL' |

**bs_flag Mapping**:
- 0 → 'SELL' (卖盘主动成交)
- 1 → 'BUY' (买盘主动成交)
- 2 → 'NEUTRAL' (中性盘)

#### Relationships
- **Many-to-One** with StockInfo (code → stock_code)
- Used by: Market microstructure analysis, order flow analysis

#### Data Flow
```
TDX Server → get_transaction_data(market, code, start, count)
  → TdxDataSource (custom method, not IDataSource)
  → UnifiedManager.save_data_by_classification(TICK_DATA)
  → TDengine (supertable: tick_data, tag: {code})
```

---

### Entity 5: FinancialInfo (财务信息)

**Source**: pytdx `get_finance_info()` API
**Classification**: `DataClassification.REFERENCE_FINANCIAL`
**Target Storage**: MySQL/MariaDB
**Update Frequency**: Quarterly/Annually

#### Attributes

| Field | Type | Source Column (pytdx) | Description | Constraints |
|-------|------|---------------------|-------------|-------------|
| code | string | (parameter) | 股票代码 | NOT NULL, PK1 |
| report_date | date | (derived from report_period) | 报告期 | NOT NULL, PK2 |
| pe_ratio | float | 'pe' | 市盈率 | |
| pb_ratio | float | 'pb' | 市净率 | |
| net_profit | float | 'lirun' | 净利润（万元） | |
| revenue | float | 'shouyi' | 营业收入（万元） | |
| roe | float | 'roe' | 净资产收益率(%) | |
| eps | float | 'mgsy' | 每股收益（元） | |
| total_share | bigint | 'zgb' | 总股本（万股） | |
| float_share | bigint | 'ltg' | 流通股本（万股） | |

**Primary Key**: (code, report_date)

#### Relationships
- **Many-to-One** with StockInfo (code → stock_code)
- Used by: Fundamental analysis, value investing strategies

#### Data Flow
```
TDX Server → get_finance_info(market, code)
  → TdxDataSource.get_financial_data()
  → Dict → pd.DataFrame conversion
  → UnifiedManager.save_data_by_classification(REFERENCE_FINANCIAL)
  → MySQL/MariaDB (table: financial_info)
```

---

### Entity 6: DividendRecord (除权除息记录)

**Source**: pytdx `get_xdxr_info()` API
**Classification**: `DataClassification.REFERENCE_DIVIDEND`
**Target Storage**: MySQL/MariaDB
**Update Frequency**: As announced

#### Attributes

| Field | Type | Source Column (pytdx) | Description | Constraints |
|-------|------|---------------------|-------------|-------------|
| code | string | (parameter) | 股票代码 | NOT NULL, PK1 |
| ex_date | date | 'date' | 除权除息日 | NOT NULL, PK2 |
| category | string | 'category' | 类别 | 'DIVIDEND'/'BONUS'/'PLACEMENT' |
| dividend | float | 'fh' | 分红金额（每10股派现，元） | |
| bonus_ratio | float | 'fhbl' | 送股比例（每10股送股数） | |
| placement_ratio | float | 'pgbl' | 配股比例（每10股配股数） | |
| placement_price | float | 'pgjg' | 配股价格（元/股） | |

**category Mapping**:
- 1 → 'DIVIDEND' (分红)
- 2 → 'BONUS' (送股)
- 3 → 'PLACEMENT' (配股)

**Primary Key**: (code, ex_date)

#### Relationships
- **Many-to-One** with StockInfo (code → stock_code)
- Used by: Price adjustment, dividend yield analysis

#### Data Flow
```
TDX Server → get_xdxr_info(market, code)
  → TdxDataSource (custom method, not IDataSource)
  → UnifiedManager.save_data_by_classification(REFERENCE_DIVIDEND)
  → MySQL/MariaDB (table: dividend_records)
```

---

### Entity 7: SectorInfo (板块信息)

**Source**: pytdx `get_block_info()` API
**Classification**: `DataClassification.REFERENCE_SECTOR`
**Target Storage**: MySQL/MariaDB
**Update Frequency**: Daily/Weekly

#### Attributes

| Field | Type | Source Column (pytdx) | Description | Constraints |
|-------|------|---------------------|-------------|-------------|
| sector_code | string | 'code' | 板块代码 | NOT NULL, PK |
| sector_name | string | 'name' | 板块名称 | NOT NULL |
| sector_type | string | (derived) | 板块类型 | 'INDUSTRY'/'CONCEPT' |
| update_date | date | (system generated) | 更新日期 | NOT NULL |

#### Entity 7.1: SectorConstituent (板块成分股)

**Junction Entity** (Many-to-Many relationship)

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| sector_code | string | 板块代码 | NOT NULL, PK1, FK → SectorInfo |
| stock_code | string | 股票代码 | NOT NULL, PK2, FK → StockInfo |
| join_date | date | 加入日期 | |
| weight | float | 权重（如有） | |

**Primary Key**: (sector_code, stock_code)

#### Relationships
- **Many-to-Many** with StockInfo via SectorConstituent junction table
- Used by: Sector rotation analysis, thematic investing

#### Data Flow
```
TDX Server → get_block_info()
  → TdxDataSource (custom method, not IDataSource)
  → Parse sector list + constituents
  → UnifiedManager.save_data_by_classification(REFERENCE_SECTOR)
  → MySQL/MariaDB (tables: sector_info, sector_constituent)
```

---

### Entity 8: StockBasicInfo (股票基本信息)

**Source**: pytdx `get_company_info_content()` API (partial)
**Classification**: `DataClassification.REFERENCE_STOCK_INFO`
**Target Storage**: MySQL/MariaDB
**Update Frequency**: Static (rarely changes)

#### Attributes

| Field | Type | Source Column (pytdx) | Description | Constraints |
|-------|------|---------------------|-------------|-------------|
| code | string | (parameter) | 股票代码 | NOT NULL, PK |
| name | string | (parsed from content) | 股票名称 | |
| industry | string | (not available) | 所属行业 | NULL (stub) |
| list_date | date | (parsed from content) | 上市日期 | |
| total_share | bigint | (from get_finance_info) | 总股本（万股） | |
| float_share | bigint | (from get_finance_info) | 流通股本（万股） | |

**Note**: pytdx's `get_company_info_content()` returns unstructured text, not structured data. Most fields will return NULL or rely on alternative sources (e.g., `get_finance_info()` for share counts).

#### Relationships
- **One-to-Many** with DailyKLine, MinuteKLine, TickData, FinancialInfo, DividendRecord
- **Many-to-Many** with SectorInfo via SectorConstituent
- Used by: Stock selection, screening, metadata queries

#### Data Flow
```
TDX Server → get_company_info_content() (limited data)
  → TdxDataSource.get_stock_basic() (partial implementation)
  → Returns Dict with limited fields (code, name only)
  → UnifiedManager.save_data_by_classification(REFERENCE_STOCK_INFO)
  → MySQL/MariaDB (table: stock_basic_info)
```

---

## Entity Relationship Diagram (ERD)

```
┌──────────────────┐
│  StockBasicInfo  │ (MySQL/MariaDB - Reference Data)
│  ────────────    │
│  - code (PK)     │
│  - name          │
│  - industry      │
│  - list_date     │
└────────┬─────────┘
         │ 1
         │
         │ N
    ┌────┴────┬─────────┬──────────┬───────────┬────────────┐
    │         │         │          │           │            │
┌───▼───┐ ┌──▼────┐ ┌──▼─────┐ ┌──▼──────┐ ┌──▼─────┐ ┌───▼──────┐
│Daily  │ │Minute │ │ Tick   │ │Financial│ │Dividend│ │ Sector   │
│KLine  │ │KLine  │ │ Data   │ │ Info    │ │ Record │ │Constituent│
│       │ │       │ │        │ │         │ │        │ │          │
│PG+TS  │ │TDeng. │ │TDeng.  │ │MySQL    │ │MySQL   │ │MySQL     │
└───────┘ └───────┘ └────────┘ └─────────┘ └────────┘ └─────┬────┘
                                                              │ N
                                                              │
                                                           ┌──▼──────┐
                                                           │ Sector  │
                                                           │  Info   │
                                                           │         │
┌──────────────┐                                           │ MySQL   │
│ RealTimeQuote│ (Redis - Hot Data Cache)                  └─────────┘
│ ──────────── │
│ - code       │ (Linked to StockBasicInfo but not enforced FK)
│ - price      │
│ - timestamp  │
└──────────────┘
```

**Key Relationships**:
- **StockBasicInfo** is the central entity (1 stock → N data records)
- **Time-series entities** (DailyKLine, MinuteKLine, TickData) stored in time-series databases
- **Reference entities** (FinancialInfo, DividendRecord, SectorInfo) stored in relational database
- **Hot data** (RealTimeQuote) cached in Redis with TTL

---

## Data Transformation Rules

### 1. Column Name Mapping

**Rule**: All Chinese column names from pytdx are mapped to English using `ColumnMapper.to_english()`

**Example Mappings**:
```python
'代码' → 'code'
'名称' → 'name'
'最新价' → 'price'
'昨收' → 'pre_close'
'开盘' → 'open'
'最高' → 'high'
'最低' → 'low'
'成交量' → 'volume'
'成交额' → 'amount'
'日期' → 'date'
'时间' → 'datetime'
```

### 2. Date Normalization

**Rule**: All date strings are normalized to ISO 8601 format using `normalize_date()`

**Transformations**:
```python
'20250115' → '2025-01-15'
'2025/01/15' → '2025-01-15'
'2025.01.15' → '2025-01-15'
```

### 3. Stock Code Formatting

**Rule**: Stock codes are formatted for TDX API using `format_stock_code_for_source(symbol, 'tdx')`

**Transformations**:
```python
'600519' → (1, '600519')  # 沪市
'000001' → (0, '000001')  # 深市
'300750' → (0, '300750')  # 创业板
```

**Market Identification Logic**:
```python
def get_market_code(symbol: str) -> int:
    """识别市场类型
    Returns: 0=深圳, 1=上海
    """
    if symbol.startswith(('000', '002', '300')):
        return 0  # 深交所
    elif symbol.startswith(('600', '601', '603', '688')):
        return 1  # 上交所
    else:
        raise ValueError(f"Unknown market for code: {symbol}")
```

### 4. Buy/Sell Flag Mapping

**Rule**: pytdx numeric flags mapped to semantic strings

```python
PYTDX_TO_STANDARD = {
    0: 'SELL',      # 卖盘主动
    1: 'BUY',       # 买盘主动
    2: 'NEUTRAL'    # 中性盘
}
```

### 5. Dividend Category Mapping

**Rule**: pytdx category codes mapped to strings

```python
PYTDX_CATEGORY = {
    1: 'DIVIDEND',    # 分红派息
    2: 'BONUS',       # 送股
    3: 'PLACEMENT'    # 配股
}
```

---

## Data Validation Rules

### Validation Layer 1: Adapter Level

**Applied Before**: Passing data to UnifiedManager

| Validation | Rule | Action on Failure |
|-----------|------|-------------------|
| Non-null PK | code, date/datetime must exist | Log error, return empty DataFrame |
| Positive prices | price, open, high, low, close >= 0 | Log warning, set to NaN |
| Volume range | volume >= 0 | Log warning, set to 0 |
| Date format | date matches YYYY-MM-DD | Normalize or reject |
| OHLC logic | high >= max(open, close, low) | Log warning, keep data |

**Implementation**:
```python
def _validate_kline_data(df: pd.DataFrame) -> pd.DataFrame:
    """验证K线数据完整性"""
    # 1. 检查必需列
    required_cols = ['code', 'date', 'open', 'high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in required_cols):
        logger.error(f"Missing required columns")
        return pd.DataFrame()

    # 2. 检查价格非负
    price_cols = ['open', 'high', 'low', 'close']
    for col in price_cols:
        if (df[col] < 0).any():
            logger.warning(f"Negative values found in {col}")
            df[col] = df[col].clip(lower=0)

    # 3. 检查OHLC逻辑
    invalid_rows = df[df['high'] < df[['open', 'close', 'low']].max(axis=1)]
    if not invalid_rows.empty:
        logger.warning(f"OHLC logic violation in {len(invalid_rows)} rows")

    return df
```

### Validation Layer 2: Storage Level

**Applied By**: DataQualityMonitor (automatic)

| Check | Threshold | Action on Failure |
|-------|-----------|-------------------|
| Completeness | > 99.9% of expected records exist | Alert via AlertManager |
| Freshness | Data updated within expected window | Alert if stale |
| Duplication | No duplicate (code, date) keys | Reject duplicates |

---

## Storage Schema Mapping

### Schema 1: PostgreSQL+TimescaleDB (Daily K-lines)

**Table**: `daily_klines`
**Hypertable**: Partitioned by `date` (monthly chunks)

```sql
CREATE TABLE daily_klines (
    code VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open NUMERIC(10, 2),
    high NUMERIC(10, 2),
    low NUMERIC(10, 2),
    close NUMERIC(10, 2),
    volume BIGINT,
    amount NUMERIC(20, 2),
    PRIMARY KEY (code, date)
);

SELECT create_hypertable('daily_klines', 'date', chunk_time_interval => INTERVAL '1 month');
CREATE INDEX idx_daily_klines_code ON daily_klines(code, date DESC);
```

### Schema 2: TDengine (Minute K-lines)

**Supertable**: `minute_klines`
**Tags**: code, period

```sql
CREATE STABLE minute_klines (
    ts TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    amount DOUBLE
) TAGS (
    code NCHAR(10),
    period NCHAR(10)
);
```

**Subtables** (auto-created):
- `minute_klines_600519_1min`
- `minute_klines_600519_5min`
- ...

### Schema 3: MySQL/MariaDB (Financial Info)

**Table**: `financial_info`

```sql
CREATE TABLE financial_info (
    code VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    pe_ratio DECIMAL(10, 2),
    pb_ratio DECIMAL(10, 2),
    net_profit DECIMAL(15, 2),
    revenue DECIMAL(15, 2),
    roe DECIMAL(5, 2),
    eps DECIMAL(10, 2),
    total_share BIGINT,
    float_share BIGINT,
    PRIMARY KEY (code, report_date),
    INDEX idx_report_date (report_date DESC)
);
```

### Schema 4: Redis (Real-time Quotes)

**Key Pattern**: `quote:{code}`
**Value**: JSON string
**TTL**: 60 seconds

```python
# Example Redis entry
key = "quote:600519"
value = json.dumps({
    "code": "600519",
    "name": "贵州茅台",
    "price": 1856.00,
    "pre_close": 1850.00,
    "volume": 1234567,
    "timestamp": "2025-01-15T14:30:00"
})
redis.setex(key, 60, value)  # 60秒TTL
```

---

## Data Flow Sequence Diagrams

### Sequence 1: Get Daily K-line Data

```
User → TdxDataSource.get_stock_daily('600519', '2024-01-01', '2024-12-31')
  │
  ├─> format_stock_code_for_source('600519', 'tdx') → (1, '600519')
  ├─> normalize_date('2024-01-01') → '2024-01-01'
  │
  ├─> TdxHq_API.connect('101.227.73.20', 7709)
  │
  ├─> Calculate: total_bars = days_between(start, end)
  ├─> Loop: for start_pos in range(0, total_bars, 800):
  │     ├─> get_security_bars(9, 1, '600519', start_pos, 800)
  │     └─> Append to result list
  │
  ├─> TdxHq_API.disconnect()
  │
  ├─> Concatenate all DataFrames
  ├─> ColumnMapper.to_english(df)
  ├─> _validate_kline_data(df)
  │
  └─> return df (standardized)

User → UnifiedManager.save_data_by_classification(df, DAILY_KLINE)
  │
  ├─> DataStorageStrategy.get_target_database(DAILY_KLINE) → PostgreSQL+TimescaleDB
  │
  ├─> PostgreSQLDataAccess.batch_insert(df, table='daily_klines')
  │
  ├─> MonitoringDatabase.log_operation(
  │     source='tdx',
  │     operation='save_daily_kline',
  │     records=len(df),
  │     duration=elapsed_ms
  │   )
  │
  └─> DataQualityMonitor.check_completeness(table='daily_klines', code='600519')
```

### Sequence 2: Get Real-time Quotes (Batch)

```
User → TdxDataSource.get_real_time_data(['600519', '000001', '300750'])
  │
  ├─> Convert codes to market tuples:
  │     [(1, '600519'), (0, '000001'), (0, '300750')]
  │
  ├─> TdxHq_API.connect('101.227.73.20', 7709)
  │
  ├─> get_security_quotes(market_tuples)
  │
  ├─> TdxHq_API.disconnect()
  │
  ├─> ColumnMapper.to_english(df)
  │
  └─> return df (3 rows)

User → UnifiedManager.save_data_by_classification(df, REALTIME_QUOTES)
  │
  ├─> DataStorageStrategy.get_target_database(REALTIME_QUOTES) → Redis
  │
  ├─> RedisDataAccess.set_with_ttl(
  │     key='quote:600519',
  │     value=json.dumps(row1),
  │     ttl=60
  │   )
  │   (Repeat for all rows)
  │
  └─> MonitoringDatabase.log_operation(...)
```

---

## Data Lifecycle Management

### Hot Data (Redis)

**Entity**: RealTimeQuote
**Retention**: 60 seconds TTL
**Cleanup**: Automatic (Redis TTL expiration)

### Warm Data (TDengine)

**Entities**: MinuteKLine, TickData
**Retention**: 90 days (configurable)
**Cleanup**: Manual TTL policy

```sql
-- TDengine retention policy
ALTER DATABASE mystocks_timeseries KEEP 90;
```

### Cold Data (PostgreSQL)

**Entities**: DailyKLine
**Retention**: Unlimited (historical archive)
**Cleanup**: None (or manual archival to object storage after 10 years)

### Reference Data (MySQL)

**Entities**: FinancialInfo, DividendRecord, SectorInfo, StockBasicInfo
**Retention**: Unlimited
**Cleanup**: None (audit trail required)

---

## Design Decisions

### Decision 1: No New Tables Created by Adapter

**Rationale**: TdxDataSource is a **data source**, not a storage layer. All storage schemas are defined by existing `table_config.yaml`. Adapter only maps external data to internal entities.

**Impact**: Simplifies adapter implementation, ensures consistency with existing data model.

### Decision 2: Stub Implementation for Unsupported Methods

**Rationale**: IDataSource interface requires 8 methods, but pytdx only supports 6 directly. Rather than violating the interface contract, stub implementations return empty results with warning logs.

**Methods Affected**:
- `get_market_calendar()` → Returns empty DataFrame
- `get_news_data()` → Returns empty List

**Alternative**: Application code can use other data sources (akshare) for these methods.

### Decision 3: Composite Primary Keys for Time-series Data

**Rationale**: (code, date) or (code, datetime, period) ensures uniqueness and supports efficient range queries.

**Impact**: Prevents duplicate data, enables time-series database optimizations (partitioning, indexing).

### Decision 4: Classification-Based Routing

**Rationale**: Adapter does not specify target database. DataStorageStrategy determines optimal storage based on data characteristics.

**Impact**: Allows seamless database migration/replacement without modifying adapter code.

---

## Phase 1 Design Completion

**Status**: ✅ Data model design complete

**Deliverables**:
- [x] 8 entity definitions with attributes and constraints
- [x] Entity relationships and ERD
- [x] Data transformation rules
- [x] Validation rules (2 layers)
- [x] Storage schema mappings (4 databases)
- [x] Data flow sequence diagrams
- [x] Data lifecycle management policies
- [x] Design decisions documented

**Next Steps**:
- → Create API contracts (contracts/ directory)
- → Create quickstart guide (quickstart.md)
- → Generate implementation tasks (/speckit.tasks)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-15
**Approved By**: Constitution Check (data classification compliant)
