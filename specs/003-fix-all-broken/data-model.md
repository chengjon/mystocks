# Data Model

**Feature**: Fix All Broken Web Features
**Branch**: `003-fix-all-broken`
**Date**: 2025-10-25

## Overview

This document defines the database schema for 5 tables being migrated from MySQL to PostgreSQL as part of fixing broken market data features.

---

## Table 1: fund_flow (资金流向)

**Purpose**: Track capital flow by industry sector and individual stocks

**Classification**: Market Data (Market Metadata)
**Database Target**: PostgreSQL
**Table Type**: Standard relational table

### Schema

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| trade_date | DATE | NOT NULL | Trading date |
| industry_code | VARCHAR(20) | NOT NULL | Industry classification code |
| industry_name | VARCHAR(100) | NOT NULL | Industry name (Chinese) |
| net_inflow | DECIMAL(18,2) | NOT NULL | Net capital inflow (亿元) |
| main_net_inflow | DECIMAL(18,2) | | Main force net inflow |
| retail_net_inflow | DECIMAL(18,2) | | Retail investor net inflow |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

### Indexes

```sql
CREATE INDEX idx_fund_flow_date ON fund_flow(trade_date DESC);
CREATE INDEX idx_fund_flow_industry ON fund_flow(industry_code);
CREATE INDEX idx_fund_flow_date_industry ON fund_flow(trade_date, industry_code);
```

### Business Rules

- `trade_date` must be a valid trading day (no weekends/holidays)
- `net_inflow` = `main_net_inflow` + `retail_net_inflow`
- Negative values indicate outflow

---

## Table 2: etf_data (ETF数据)

**Purpose**: Store ETF holdings, performance, and fund flow data

**Classification**: Market Data (Market Metadata)
**Database Target**: PostgreSQL
**Table Type**: Standard relational table

### Schema

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| etf_code | VARCHAR(20) | NOT NULL | ETF code (e.g., 510300) |
| etf_name | VARCHAR(100) | NOT NULL | ETF name |
| trade_date | DATE | NOT NULL | Trading date |
| nav | DECIMAL(10,4) | | Net asset value |
| close_price | DECIMAL(10,2) | | Closing price |
| volume | BIGINT | | Trading volume (shares) |
| turnover | DECIMAL(18,2) | | Turnover amount (元) |
| premium_rate | DECIMAL(6,2) | | Premium/discount rate (%) |
| pe_ratio | DECIMAL(10,2) | | P/E ratio |
| pb_ratio | DECIMAL(10,2) | | P/B ratio |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

### Indexes

```sql
CREATE INDEX idx_etf_code_date ON etf_data(etf_code, trade_date DESC);
CREATE INDEX idx_etf_date ON etf_data(trade_date DESC);
CREATE UNIQUE INDEX idx_etf_unique ON etf_data(etf_code, trade_date);
```

### Business Rules

- Each ETF code can only have one record per trading date
- `premium_rate` = (`close_price` - `nav`) / `nav` * 100
- Positive premium_rate indicates trading above NAV

---

## Table 3: dragon_tiger (龙虎榜)

**Purpose**: Dragon-Tiger List showing unusual trading activity

**Classification**: Market Data (Market Metadata)
**Database Target**: PostgreSQL
**Table Type**: Standard relational table

### Schema

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| stock_code | VARCHAR(20) | NOT NULL | Stock code |
| stock_name | VARCHAR(100) | NOT NULL | Stock name |
| trade_date | DATE | NOT NULL | Trading date |
| reason | VARCHAR(200) | | Reason for being on the list |
| close_price | DECIMAL(10,2) | | Closing price |
| change_pct | DECIMAL(6,2) | | Price change percentage |
| turnover | DECIMAL(18,2) | | Turnover amount (元) |
| buy_amount_top5 | DECIMAL(18,2) | | Top 5 buyers total (元) |
| sell_amount_top5 | DECIMAL(18,2) | | Top 5 sellers total (元) |
| net_amount | DECIMAL(18,2) | | Net buy/sell amount |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

### Indexes

```sql
CREATE INDEX idx_dragon_code_date ON dragon_tiger(stock_code, trade_date DESC);
CREATE INDEX idx_dragon_date ON dragon_tiger(trade_date DESC);
CREATE INDEX idx_dragon_net_amount ON dragon_tiger(net_amount DESC);
```

### Business Rules

- Only stocks with unusual trading activity appear on this list
- `net_amount` = `buy_amount_top5` - `sell_amount_top5`
- Positive net_amount indicates net buying by institutions

---

## Table 4: chip_race (竞价抢筹)

**Purpose**: Auction bidding data showing capital competition for stocks

**Classification**: Market Data (Market Metadata)
**Database Target**: PostgreSQL
**Table Type**: Standard relational table

### Schema

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| stock_code | VARCHAR(20) | NOT NULL | Stock code |
| stock_name | VARCHAR(100) | NOT NULL | Stock name |
| trade_date | DATE | NOT NULL | Trading date |
| auction_type | VARCHAR(20) | NOT NULL | Auction type (开盘/收盘) |
| auction_price | DECIMAL(10,2) | | Auction price |
| auction_volume | BIGINT | | Auction volume (shares) |
| auction_turnover | DECIMAL(18,2) | | Auction turnover (元) |
| price_change_pct | DECIMAL(6,2) | | Price change vs previous close |
| turnover_rate | DECIMAL(6,2) | | Turnover rate (%) |
| intensity_score | DECIMAL(10,2) | | Bidding intensity score |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

### Indexes

```sql
CREATE INDEX idx_chip_code_date ON chip_race(stock_code, trade_date DESC);
CREATE INDEX idx_chip_date_type ON chip_race(trade_date DESC, auction_type);
CREATE INDEX idx_chip_intensity ON chip_race(intensity_score DESC);
```

### Business Rules

- `auction_type` must be either '开盘' (open) or '收盘' (close)
- `intensity_score` calculated based on price change, volume, and turnover rate
- High intensity score indicates strong capital competition

---

## Table 5: indicator_configs (指标配置)

**Purpose**: Store user-defined technical indicator configurations

**Classification**: Derived Data (Configuration)
**Database Target**: PostgreSQL
**Table Type**: Standard relational table

### Schema

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| user_id | INTEGER | NOT NULL | User who created the config |
| indicator_name | VARCHAR(100) | NOT NULL | Indicator name (e.g., MACD, RSI) |
| display_name | VARCHAR(200) | | Custom display name |
| parameters | JSONB | NOT NULL | Indicator parameters as JSON |
| description | TEXT | | User notes about this configuration |
| is_public | BOOLEAN | DEFAULT FALSE | Whether shared with other users |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

### Indexes

```sql
CREATE INDEX idx_indicator_user ON indicator_configs(user_id);
CREATE INDEX idx_indicator_name ON indicator_configs(indicator_name);
CREATE INDEX idx_indicator_public ON indicator_configs(is_public) WHERE is_public = TRUE;
```

### Business Rules

- Each user can have multiple configurations for the same indicator
- `parameters` JSONB must contain valid indicator parameters
- Public configurations can be viewed by all users but only modified by creator

### Example Parameters (JSONB)

```json
{
  "indicator_type": "MACD",
  "fast_period": 12,
  "slow_period": 26,
  "signal_period": 9,
  "price_type": "close",
  "visualization": {
    "color_fast": "#FF0000",
    "color_slow": "#0000FF",
    "color_signal": "#00FF00"
  }
}
```

---

## Migration Checklist

### Pre-Migration

- [ ] Export all 5 tables from MySQL to JSON/CSV
- [ ] Record row counts for validation
- [ ] Update `table_config.yaml` with PostgreSQL definitions
- [ ] Test table creation in development environment

### Migration Execution

- [ ] Create tables in PostgreSQL using `ConfigDrivenTableManager`
- [ ] Import data from backup files
- [ ] Verify row counts match original
- [ ] Create all indexes
- [ ] Update API endpoints to use PostgreSQL connections

### Post-Migration Validation

- [ ] Query sample data from each table
- [ ] Test all 4 market data panels in frontend
- [ ] Test indicator configuration save/load
- [ ] Run integration tests
- [ ] Monitor for 2 weeks before decommissioning MySQL tables

---

## Database Configuration Updates

Add to `table_config.yaml`:

```yaml
- table_name: fund_flow
  database_target: postgresql
  classification: market_metadata
  columns:
    - name: id
      type: SERIAL
      constraints: [PRIMARY_KEY]
    # ... (full schema as above)

- table_name: etf_data
  database_target: postgresql
  # ... (full schema as above)

# ... (remaining 3 tables)
```

---

## Entity Relationships

```
User (existing)
  ↓ 1:N
indicator_configs

(Market Data Tables - Independent)
fund_flow      ← industry-level aggregation
etf_data       ← ETF-specific data
dragon_tiger   ← unusual trading activity
chip_race      ← auction bidding data
```

**Note**: These tables are primarily for read/display purposes and don't have foreign key relationships to other tables in the system.
