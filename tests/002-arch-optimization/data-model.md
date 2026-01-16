# Data Model: Architecture Optimization

**Feature**: Architecture Optimization for Quantitative Trading System
**Branch**: `002-arch-optimization`
**Date**: 2025-10-25
**Phase**: Phase 1 - Data Model & Entity Design

## Overview

This document defines the entities, relationships, and data structures for the optimized MyStocks architecture. The model supports a simplified 3-layer architecture with 10 data classifications, 2 databases (TDengine + PostgreSQL), and 3-4 core adapters.

---

## Core Entities

### 1. Data Classification (Enum)

**Purpose**: Simplified 10-category data classification system

**Entity Definition**:
```python
from enum import Enum

class DataClassification(Enum):
    """Simplified 10-category data classification"""

    # High-frequency time-series data → TDengine
    HIGH_FREQUENCY = "high_frequency"

    # Historical K-line data → PostgreSQL
    HISTORICAL_KLINE = "historical_kline"

    # Real-time market snapshots → PostgreSQL
    REALTIME_SNAPSHOT = "realtime_snapshot"

    # Industry & sector data → PostgreSQL
    INDUSTRY_SECTOR = "industry_sector"

    # Concept & theme plates → PostgreSQL
    CONCEPT_THEME = "concept_theme"

    # Financial & fundamental data → PostgreSQL
    FINANCIAL_FUNDAMENTAL = "financial_fundamental"

    # Capital flow & fund tracking → PostgreSQL
    CAPITAL_FLOW = "capital_flow"

    # Chip distribution & holder analysis → PostgreSQL
    CHIP_DISTRIBUTION = "chip_distribution"

    # News & announcements → PostgreSQL
    NEWS_ANNOUNCEMENT = "news_announcement"

    # Derived indicators & signals → PostgreSQL
    DERIVED_INDICATOR = "derived_indicator"
```

**Classification-to-Database Mapping**:
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
```

**Validation Rules**:
- All data must be assigned exactly one classification
- Classification determines target database automatically
- No manual database selection allowed (enforced by DataManager)

---

### 2. Adapter Registry Entry

**Purpose**: Runtime adapter registration/unregistration tracking

**Entity Definition**:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AdapterRegistryEntry:
    """Metadata for registered adapter"""

    name: str                           # Unique adapter identifier (e.g., "tdx", "akshare")
    adapter_type: str                   # Type: "core", "optional", "custom"
    registered_at: datetime             # Registration timestamp
    is_active: bool                     # Active status
    priority: int                       # Priority in fallback chain (lower = higher priority)
    source_type: str                    # "local" or "network"
    rate_limit: Optional[int] = None    # Requests per minute (None = unlimited)
    description: Optional[str] = None   # Human-readable description

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "adapter_type": self.adapter_type,
            "registered_at": self.registered_at.isoformat(),
            "is_active": self.is_active,
            "priority": self.priority,
            "source_type": self.source_type,
            "rate_limit": self.rate_limit,
            "description": self.description,
        }
```

**State Transitions**:
```
[Unregistered] --register()--> [Active] --unregister()--> [Unregistered]
                                  ^
                                  |
                         (automatic on system start
                          for core adapters)
```

**Relationships**:
- One-to-one with adapter instance (stored in DataManager._adapters dict)
- Referenced by cache-first retrieval strategy for priority ordering

---

### 3. Data Cache Entry (PostgreSQL Table)

**Purpose**: Intelligent cache layer for minimizing API calls

**Table Definition** (PostgreSQL):
```sql
CREATE TABLE data_cache (
    cache_id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    classification VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    data_hash VARCHAR(64),  -- SHA-256 hash for integrity check
    source_adapter VARCHAR(50),  -- Adapter that provided the data
    cached_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    data_size_kb INTEGER,
    is_complete BOOLEAN DEFAULT TRUE,  -- Whether date range is fully covered

    -- Index for fast lookups
    CONSTRAINT unique_cache_entry UNIQUE (symbol, data_type, start_date, end_date)
);

CREATE INDEX idx_data_cache_lookup ON data_cache (symbol, data_type, start_date, end_date);
CREATE INDEX idx_data_cache_classification ON data_cache (classification);
CREATE INDEX idx_data_cache_cached_at ON data_cache (cached_at);
```

**Entity Definition** (Python):
```python
from pydantic import BaseModel, Field
from datetime import date, datetime

class DataCacheEntry(BaseModel):
    """Metadata for cached data entry"""

    cache_id: Optional[int] = None
    symbol: str = Field(..., max_length=20, description="Stock code")
    data_type: str = Field(..., max_length=50, description="e.g., 'kline_daily', 'tick'")
    classification: str = Field(..., description="DataClassification enum value")
    start_date: date
    end_date: date
    data_hash: Optional[str] = Field(None, max_length=64)
    source_adapter: str = Field(..., max_length=50)
    cached_at: datetime = Field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    data_size_kb: Optional[int] = None
    is_complete: bool = True

    class Config:
        orm_mode = True
```

**Cache Invalidation Rules**:
| Data Type | Cache Duration | Invalidation Logic |
|-----------|----------------|-------------------|
| Historical (>1 day old) | Indefinite | Never expires (immutable) |
| Current Day | 5 minutes | Refresh if age > 300 seconds |
| Real-time | 1 second | Refresh if age > 1 second |

**Relationships**:
- Many-to-one with DataClassification (one classification, many cache entries)
- Referenced by cache-first retrieval strategy

---

### 4. Archival Job Record (PostgreSQL Table)

**Purpose**: Track TDengine→PostgreSQL archival operations

**Table Definition** (PostgreSQL):
```sql
CREATE TABLE archival_jobs (
    job_id BIGSERIAL PRIMARY KEY,
    job_date DATE NOT NULL,
    data_type VARCHAR(50) NOT NULL,  -- e.g., 'tick', 'minute_1', 'minute_5'
    cutoff_date DATE NOT NULL,  -- Data older than this archived
    records_archived BIGINT,
    records_deleted_from_tdengine BIGINT,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,  -- 'running', 'completed', 'failed', 'verified'
    error_message TEXT,
    integrity_check_passed BOOLEAN,

    CONSTRAINT unique_archival_job UNIQUE (job_date, data_type)
);

CREATE INDEX idx_archival_jobs_date ON archival_jobs (job_date);
CREATE INDEX idx_archival_jobs_status ON archival_jobs (status);
```

**Entity Definition** (Python):
```python
from enum import Enum

class ArchivalJobStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"

@dataclass
class ArchivalJobRecord:
    """Record of TDengine archival job"""

    job_id: Optional[int] = None
    job_date: date
    data_type: str
    cutoff_date: date
    records_archived: Optional[int] = None
    records_deleted_from_tdengine: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: ArchivalJobStatus = ArchivalJobStatus.RUNNING
    error_message: Optional[str] = None
    integrity_check_passed: Optional[bool] = None

    def mark_completed(self, records_archived: int, records_deleted: int, integrity_passed: bool):
        """Mark job as completed with results"""
        self.completed_at = datetime.now()
        self.records_archived = records_archived
        self.records_deleted_from_tdengine = records_deleted
        self.integrity_check_passed = integrity_passed
        self.status = ArchivalJobStatus.VERIFIED if integrity_passed else ArchivalJobStatus.COMPLETED

    def mark_failed(self, error: str):
        """Mark job as failed with error message"""
        self.completed_at = datetime.now()
        self.status = ArchivalJobStatus.FAILED
        self.error_message = error
```

**State Transitions**:
```
[Created] --start()--> [Running] --complete()--> [Completed] --verify()--> [Verified]
                          |
                          +--fail()--> [Failed]
```

---

### 5. High-Frequency Data (TDengine SuperTable)

**Purpose**: Store tick data and minute K-lines with optimal compression

**SuperTable Definition** (TDengine):
```sql
-- Super table for tick data
CREATE STABLE tick_data (
    ts TIMESTAMP,
    price FLOAT,
    volume BIGINT,
    amount DOUBLE,
    bid1 FLOAT,
    bid1_volume BIGINT,
    ask1 FLOAT,
    ask1_volume BIGINT,
    -- ... additional Level-2 fields
) TAGS (
    symbol VARCHAR(20),
    exchange VARCHAR(10)  -- 'SH' or 'SZ'
);

-- Super table for minute K-lines
CREATE STABLE minute_kline (
    ts TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    amount DOUBLE,
    period INT  -- 1, 5, 15, 30, 60 minutes
) TAGS (
    symbol VARCHAR(20),
    exchange VARCHAR(10)
);
```

**Retention Policy**:
- Hot data: Most recent 3 months in TDengine
- Cold data: Older than 3 months archived to PostgreSQL

**Entity Definition** (Python):
```python
@dataclass
class TickData:
    """Tick data entity"""
    ts: datetime
    symbol: str
    price: float
    volume: int
    amount: float
    bid1: float
    bid1_volume: int
    ask1: float
    ask1_volume: int

@dataclass
class MinuteKLine:
    """Minute K-line entity"""
    ts: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float
    period: int  # 1, 5, 15, 30, 60
```

---

### 6. Historical K-Line Data (PostgreSQL + TimescaleDB)

**Purpose**: Store daily/weekly/monthly K-lines with complex query support

**Table Definition** (PostgreSQL with TimescaleDB):
```sql
-- Convert to hypertable for time-series optimization
CREATE TABLE historical_kline (
    ts TIMESTAMP NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    period VARCHAR(20) NOT NULL,  -- 'daily', 'weekly', 'monthly'
    open NUMERIC(10, 2),
    high NUMERIC(10, 2),
    low NUMERIC(10, 2),
    close NUMERIC(10, 2),
    volume BIGINT,
    amount NUMERIC(20, 2),
    turnover_rate NUMERIC(10, 4),  -- 换手率
    pct_change NUMERIC(10, 4),  -- 涨跌幅
    adj_factor NUMERIC(15, 6),  -- 复权因子

    CONSTRAINT pk_historical_kline PRIMARY KEY (ts, symbol, period)
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('historical_kline', 'ts');

-- Indexes for common queries
CREATE INDEX idx_historical_symbol_ts ON historical_kline (symbol, ts DESC);
CREATE INDEX idx_historical_period ON historical_kline (period, ts DESC);
```

**Entity Definition** (Python):
```python
class HistoricalKLine(BaseModel):
    """Historical K-line data entity"""

    ts: datetime
    symbol: str = Field(..., max_length=20)
    exchange: str = Field(..., max_length=10)
    period: str = Field(..., description="'daily', 'weekly', 'monthly'")
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    amount: Decimal
    turnover_rate: Optional[Decimal] = None
    pct_change: Optional[Decimal] = None
    adj_factor: Optional[Decimal] = None

    class Config:
        orm_mode = True
```

---

### 7. Industry & Sector Data (PostgreSQL)

**Purpose**: Support sector rotation analysis and industry classification

**Table Definitions** (PostgreSQL):
```sql
-- Industry classification (申万/证监会)
CREATE TABLE industries (
    industry_id SERIAL PRIMARY KEY,
    industry_code VARCHAR(20) UNIQUE NOT NULL,
    industry_name VARCHAR(100) NOT NULL,
    classification_system VARCHAR(20) NOT NULL,  -- 'SW' (申万) or 'CSRC' (证监会)
    level INT NOT NULL,  -- 1 (一级行业), 2 (二级行业), 3 (三级行业)
    parent_industry_code VARCHAR(20),
    description TEXT,

    FOREIGN KEY (parent_industry_code) REFERENCES industries(industry_code)
);

-- Stock-to-industry mapping
CREATE TABLE stock_industries (
    mapping_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    industry_code VARCHAR(20) NOT NULL,
    effective_date DATE NOT NULL,
    end_date DATE,  -- NULL if still current
    is_primary BOOLEAN DEFAULT TRUE,  -- Primary vs secondary classification

    FOREIGN KEY (industry_code) REFERENCES industries(industry_code),
    CONSTRAINT unique_stock_industry UNIQUE (symbol, industry_code, effective_date)
);

-- Industry indices
CREATE TABLE industry_indices (
    index_id SERIAL PRIMARY KEY,
    industry_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    index_value NUMERIC(10, 2),
    pct_change NUMERIC(10, 4),
    volume BIGINT,
    amount NUMERIC(20, 2),

    FOREIGN KEY (industry_code) REFERENCES industries(industry_code),
    CONSTRAINT unique_industry_index UNIQUE (industry_code, trade_date)
);

CREATE INDEX idx_industry_indices_date ON industry_indices (trade_date DESC);
```

**Entity Definitions** (Python):
```python
class Industry(BaseModel):
    industry_id: Optional[int] = None
    industry_code: str = Field(..., max_length=20)
    industry_name: str = Field(..., max_length=100)
    classification_system: str = Field(..., pattern="^(SW|CSRC)$")
    level: int = Field(..., ge=1, le=3)
    parent_industry_code: Optional[str] = None
    description: Optional[str] = None

class StockIndustryMapping(BaseModel):
    mapping_id: Optional[int] = None
    symbol: str = Field(..., max_length=20)
    industry_code: str = Field(..., max_length=20)
    effective_date: date
    end_date: Optional[date] = None
    is_primary: bool = True
```

---

### 8. Concept & Theme Plates (PostgreSQL)

**Purpose**: Support Chinese market concept speculation analysis

**Table Definitions** (PostgreSQL):
```sql
-- Concept definitions
CREATE TABLE concepts (
    concept_id SERIAL PRIMARY KEY,
    concept_code VARCHAR(50) UNIQUE NOT NULL,
    concept_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Stock-to-concept mapping
CREATE TABLE stock_concepts (
    mapping_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    concept_code VARCHAR(50) NOT NULL,
    added_date DATE NOT NULL,
    removed_date DATE,  -- NULL if still in concept

    FOREIGN KEY (concept_code) REFERENCES concepts(concept_code),
    CONSTRAINT unique_stock_concept UNIQUE (symbol, concept_code, added_date)
);

-- Concept indices
CREATE TABLE concept_indices (
    index_id SERIAL PRIMARY KEY,
    concept_code VARCHAR(50) NOT NULL,
    trade_date DATE NOT NULL,
    index_value NUMERIC(10, 2),
    pct_change NUMERIC(10, 4),
    leading_stocks TEXT[],  -- Array of top performing symbols

    FOREIGN KEY (concept_code) REFERENCES concepts(concept_code),
    CONSTRAINT unique_concept_index UNIQUE (concept_code, trade_date)
);
```

**Entity Definitions** (Python):
```python
class Concept(BaseModel):
    concept_id: Optional[int] = None
    concept_code: str = Field(..., max_length=50)
    concept_name: str = Field(..., max_length=100)
    description: Optional[str] = None
    created_date: Optional[date] = None
    is_active: bool = True

class StockConceptMapping(BaseModel):
    mapping_id: Optional[int] = None
    symbol: str = Field(..., max_length=20)
    concept_code: str = Field(..., max_length=50)
    added_date: date
    removed_date: Optional[date] = None
```

---

### 9. Capital Flow Data (PostgreSQL)

**Purpose**: Track main fund flow and institutional money movements

**Table Definitions** (PostgreSQL):
```sql
-- Stock-level capital flow
CREATE TABLE capital_flow (
    flow_id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    main_fund_net NUMERIC(20, 2),  -- 主力资金净流入 (main fund net inflow)
    retail_fund_net NUMERIC(20, 2),  -- 散户资金净流入
    institutional_fund_net NUMERIC(20, 2),  -- 机构资金净流入
    super_large_net NUMERIC(20, 2),  -- 超大单净流入
    large_net NUMERIC(20, 2),  -- 大单净流入
    medium_net NUMERIC(20, 2),  -- 中单净流入
    small_net NUMERIC(20, 2),  -- 小单净流入
    north_bound_net NUMERIC(20, 2),  -- 北向资金净流入

    CONSTRAINT unique_capital_flow UNIQUE (symbol, trade_date)
);

CREATE INDEX idx_capital_flow_date ON capital_flow (trade_date DESC);
CREATE INDEX idx_capital_flow_symbol ON capital_flow (symbol, trade_date DESC);

-- Market-level capital flow aggregation
CREATE TABLE market_capital_flow (
    flow_id SERIAL PRIMARY KEY,
    trade_date DATE NOT NULL UNIQUE,
    total_main_fund_net NUMERIC(30, 2),
    total_north_bound_net NUMERIC(30, 2),
    market_type VARCHAR(20) NOT NULL  -- 'SH', 'SZ', 'ALL'
);
```

**Entity Definition** (Python):
```python
class CapitalFlow(BaseModel):
    flow_id: Optional[int] = None
    symbol: str = Field(..., max_length=20)
    trade_date: date
    main_fund_net: Optional[Decimal] = None
    retail_fund_net: Optional[Decimal] = None
    institutional_fund_net: Optional[Decimal] = None
    super_large_net: Optional[Decimal] = None
    large_net: Optional[Decimal] = None
    medium_net: Optional[Decimal] = None
    small_net: Optional[Decimal] = None
    north_bound_net: Optional[Decimal] = None
```

---

### 10. Chip Distribution Data (PostgreSQL)

**Purpose**: Support shareholder structure and chip concentration analysis

**Table Definitions** (PostgreSQL):
```sql
-- Top shareholders
CREATE TABLE top_shareholders (
    record_id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    report_date DATE NOT NULL,
    shareholder_rank INT NOT NULL,  -- 1-10
    shareholder_name VARCHAR(200),
    shares_held BIGINT,
    holding_ratio NUMERIC(10, 4),  -- Percentage
    shareholder_type VARCHAR(50),  -- 'institution', 'individual', 'fund', etc.

    CONSTRAINT unique_shareholder UNIQUE (symbol, report_date, shareholder_rank)
);

-- Chip distribution by price level
CREATE TABLE chip_distribution (
    dist_id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    calc_date DATE NOT NULL,
    price_level NUMERIC(10, 2) NOT NULL,  -- Price point
    chip_ratio NUMERIC(10, 4),  -- Percentage of chips at this price
    profit_ratio NUMERIC(10, 4),  -- Percentage of chips in profit
    concentration_ratio NUMERIC(10, 4),  -- Chip concentration index

    CONSTRAINT unique_chip_dist UNIQUE (symbol, calc_date, price_level)
);

CREATE INDEX idx_chip_dist_symbol_date ON chip_distribution (symbol, calc_date DESC);
```

**Entity Definitions** (Python):
```python
class TopShareholder(BaseModel):
    record_id: Optional[int] = None
    symbol: str = Field(..., max_length=20)
    report_date: date
    shareholder_rank: int = Field(..., ge=1, le=10)
    shareholder_name: Optional[str] = Field(None, max_length=200)
    shares_held: Optional[int] = None
    holding_ratio: Optional[Decimal] = None
    shareholder_type: Optional[str] = Field(None, max_length=50)

class ChipDistribution(BaseModel):
    dist_id: Optional[int] = None
    symbol: str = Field(..., max_length=20)
    calc_date: date
    price_level: Decimal
    chip_ratio: Optional[Decimal] = None
    profit_ratio: Optional[Decimal] = None
    concentration_ratio: Optional[Decimal] = None
```

---

## Entity Relationships

### Relationship Diagram

```
┌─────────────────────────┐
│ DataClassification      │
│ (Enum)                  │
└────────┬────────────────┘
         │ determines
         │ routing
         ▼
┌─────────────────────────┐      ┌──────────────────────┐
│ DataCacheEntry          │◄─────┤ AdapterRegistry      │
│ (PostgreSQL)            │ from │ (Runtime)            │
└─────────────────────────┘      └──────────────────────┘
         │
         │ tracks
         │ cached data
         ▼
┌─────────────────────────┐      ┌──────────────────────┐
│ HighFrequencyData       │      │ HistoricalKLine      │
│ (TDengine)              │──────┤ (PostgreSQL)         │
└─────────────────────────┘      └──────────────────────┘
         │                                │
         │ archived to                    │
         │ after 3 months                 │
         ▼                                │
┌─────────────────────────┐              │
│ ArchivalJobRecord       │              │
│ (PostgreSQL)            │              │
└─────────────────────────┘              │
                                          │
                    ┌─────────────────────┴──────────────────┐
                    │                                         │
                    ▼                                         ▼
         ┌──────────────────────┐              ┌──────────────────────┐
         │ Industry & Sector    │              │ Concept & Theme      │
         │ (PostgreSQL)         │              │ (PostgreSQL)         │
         └──────────────────────┘              └──────────────────────┘
                    │                                         │
                    │ supports                                │
                    ▼                                         ▼
         ┌──────────────────────┐              ┌──────────────────────┐
         │ CapitalFlow          │              │ ChipDistribution     │
         │ (PostgreSQL)         │              │ (PostgreSQL)         │
         └──────────────────────┘              └──────────────────────┘
```

### Relationship Details

**1. Classification → Database Routing**:
- Type: One-to-one (each classification maps to one database)
- Cardinality: 10 classifications → 2 databases (1 TDengine, 9 PostgreSQL)
- Enforcement: Dict-based mapping, no manual override allowed

**2. Adapter Registry → Cache Entry**:
- Type: Many-to-many (one adapter can populate multiple cache entries, one cache entry tracks source adapter)
- Cardinality: 3-4 adapters → N cache entries
- Enforcement: Foreign key `source_adapter` in `data_cache` table

**3. TDengine → PostgreSQL Archival**:
- Type: One-way migration (hot data archived to cold storage)
- Trigger: Daily job at 00:30, archives data >3 months old
- Tracking: `archival_jobs` table records all migration operations

**4. Stock → Industry Mapping**:
- Type: Many-to-many (one stock can belong to multiple industries, one industry contains many stocks)
- Cardinality: ~5,000 stocks × ~100 industries
- Time-versioned: `effective_date` and `end_date` track historical changes

**5. Stock → Concept Mapping**:
- Type: Many-to-many (one stock can belong to multiple concepts, one concept contains many stocks)
- Cardinality: ~5,000 stocks × ~300 concepts
- Time-versioned: `added_date` and `removed_date` track dynamic changes

**6. Capital Flow → Stock/Industry/Concept**:
- Type: One-to-many (one stock/industry/concept has many daily capital flow records)
- Aggregation: Stock-level → Industry-level → Market-level
- Time-series: Daily granularity

**7. Chip Distribution → Stock**:
- Type: One-to-many (one stock has many chip distribution snapshots)
- Granularity: By price level (e.g., every 0.1 yuan)
- Calculation: Updated daily based on transaction data

---

## Data Flow Patterns

### Pattern 1: Cache-First Retrieval

```
User Request
    │
    ▼
┌─────────────────────┐
│ UnifiedDataManager  │
│ (Entry Point)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ DataManager         │
│ (Layer 2)           │
└──────────┬──────────┘
           │
           ├──[1]──► Check PostgreSQL Cache (data_cache table)
           │         │
           │         ▼
           │    ┌─────────┐   Hit: Return cached data
           │    │ Cache?  ├───Yes──────────────────┐
           │    └────┬────┘                        │
           │         │ Miss                        │
           │         ▼                             │
           ├──[2]──► Try TDX Local Source         │
           │         │                             │
           │         ▼                             │
           │    ┌─────────┐   Hit: Cache + Return │
           │    │Available├───Yes─────────────┐   │
           │    └────┬────┘                    │   │
           │         │ No/Fail                 │   │
           │         ▼                         │   │
           └──[3]──► Try Network Sources       │   │
                     (AkShare→Baostock→Byapi)  │   │
                     │                         │   │
                     ▼                         │   │
                ┌─────────┐   Hit: Cache + Return │
                │Success? ├───Yes─────────────┴───┘
                └────┬────┘                        │
                     │ All Fail                    │
                     ▼                             │
                Return None                        │
                                                   ▼
                                            Return Data to User
```

### Pattern 2: Tiered Storage Archival

```
Daily Job (00:30)
    │
    ▼
┌────────────────────────┐
│ ArchivalJobRecord      │
│ Status: Running        │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│ Query TDengine         │
│ SELECT WHERE ts < (NOW() - 90 days) │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│ Batch Insert to        │
│ PostgreSQL (chunks of  │
│ 10,000 records)        │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│ Verify Integrity       │
│ (count check, hash)    │
└──────────┬─────────────┘
           │
           ├─Yes──► Delete from TDengine
           │         │
           │         ▼
           │    ┌─────────────────────┐
           │    │ ArchivalJobRecord   │
           │    │ Status: Verified    │
           │    └─────────────────────┘
           │
           └─No───► Abort Deletion
                    │
                    ▼
               ┌─────────────────────┐
               │ ArchivalJobRecord   │
               │ Status: Failed      │
               └─────────────────────┘
```

### Pattern 3: Runtime Adapter Registration

```
User Action: Register Custom Adapter
    │
    ▼
┌───────────────────────────┐
│ DataManager.register_adapter() │
│ (name, adapter_instance)  │
└──────────┬────────────────┘
           │
           ▼
┌───────────────────────────┐
│ Validate Adapter          │
│ (IDataSource protocol check) │
└──────────┬────────────────┘
           │
           ├─Valid──► Add to _adapters dict
           │          │
           │          ▼
           │     ┌─────────────────────┐
           │     │ AdapterRegistryEntry│
           │     │ is_active = True    │
           │     └─────────────────────┘
           │          │
           │          ▼
           │     Available for use in
           │     cache-first retrieval
           │
           └─Invalid──► Return False
                       │
                       ▼
                  Log warning + reject
```

---

## Validation Rules

### Data Integrity Constraints

**1. Stock Symbol Format**:
- Pattern: `^[0-9]{6}$` (6 digits)
- Valid prefixes: 60xxxx (SH), 00xxxx (SZ), 30xxxx (GEM)
- Validation: Before database insertion

**2. Date Range Consistency**:
- start_date ≤ end_date in all queries
- Trade dates must be valid trading days (check against trade_calendar)
- Future dates rejected for historical data queries

**3. Price Data Constraints**:
- open, high, low, close > 0
- high ≥ max(open, close, low)
- low ≤ min(open, close, high)
- volume ≥ 0, amount ≥ 0

**4. Classification Uniqueness**:
- One classification per data type (enforced by enum)
- No overlapping classifications allowed

**5. Cache Completeness**:
- is_complete flag tracks whether date range is fully covered
- Partial cache hits trigger complementary adapter queries

**6. Archival Job Integrity**:
- Verify record count match before deletion from TDengine
- SHA-256 hash check for data integrity
- Abort if verification fails (no data loss)

---

## Performance Considerations

### Indexing Strategy

**PostgreSQL Indexes**:
- Composite index: (symbol, trade_date) for time-series queries
- Classification index for routing efficiency
- Cache lookup index: (symbol, data_type, start_date, end_date)

**TDengine Optimization**:
- TAGS (symbol, exchange) for automatic partitioning
- Time-based partitioning by default
- 20:1 compression ratio reduces storage cost

### Query Optimization Patterns

**1. Range Queries**:
```sql
-- Use index on (symbol, trade_date)
SELECT * FROM historical_kline
WHERE symbol = '600000' AND ts BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY ts DESC;
```

**2. Aggregation Queries**:
```sql
-- Use TimescaleDB time_bucket for aggregations
SELECT time_bucket('1 day', ts) AS day, AVG(close) AS avg_close
FROM historical_kline
WHERE symbol = '600000' AND ts > NOW() - INTERVAL '30 days'
GROUP BY day;
```

**3. Cache Lookup**:
```sql
-- Use unique constraint index
SELECT * FROM data_cache
WHERE symbol = '600000'
  AND data_type = 'kline_daily'
  AND start_date <= '2024-01-01'
  AND end_date >= '2024-12-31'
  AND is_complete = TRUE
LIMIT 1;
```

---

## Conclusion

This data model provides a comprehensive foundation for the optimized MyStocks architecture:

- **10 Simplified Classifications**: Clear, business-oriented categorization
- **2-Database Strategy**: TDengine for high-frequency, PostgreSQL for everything else
- **Intelligent Caching**: Minimizes API calls, optimizes performance
- **Tiered Storage**: Cost-effective archival with data integrity
- **Professional Analysis Support**: Explicit entities for industry/sector/concept/capital/chip
- **Runtime Flexibility**: Hot-plug adapter registration capability

Ready to proceed to API contracts definition (contracts/ directory).
