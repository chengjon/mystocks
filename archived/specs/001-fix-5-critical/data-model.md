# Data Model

**Feature**: Fix 5 Critical Issues in OpenStock Demo
**Date**: 2025-10-20
**Phase**: 1 - Design

## Overview

This document defines the core entities for the OpenStock Demo watchlist and market data functionality. All entities follow PostgreSQL conventions and align with the project's data classification principles.

---

## Entity Definitions

### 1. WatchlistGroup

**Purpose**: User-created categories for organizing stocks in watchlists

**Classification**: Reference Data (Type 2) - Semi-static user preferences

**Storage**: PostgreSQL `watchlist_groups` table

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| user_id | INTEGER | NOT NULL | Owner of this group (references users.id) |
| group_name | VARCHAR(100) | NOT NULL | Display name (e.g., "科技股", "价值股") |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |
| sort_order | INTEGER | DEFAULT 0 | Display order (lower = earlier) |
| stock_count | INTEGER | DEFAULT 0 | Cached count of stocks in group |

**Unique Constraints**:
- (user_id, group_name) - Each user can only have one group with a given name

**Indexes**:
- PRIMARY KEY on id
- INDEX on (user_id) for user-scoped queries
- UNIQUE INDEX on (user_id, group_name)

**Relationships**:
- ONE-TO-MANY with WatchlistItem (one group contains many stocks)
- MANY-TO-ONE with User (many groups belong to one user)

**Validation Rules**:
1. group_name must be 1-100 characters
2. group_name cannot contain only whitespace
3. user_id must reference existing user
4. stock_count must be >= 0

**State Transitions**:
- **Created** → User creates new group (initial stock_count = 0)
- **Populated** → Stocks added (stock_count increments)
- **Modified** → Group name updated
- **Emptied** → All stocks removed (stock_count = 0)
- **Deleted** → Group deleted (CASCADE deletes all watchlist items)

**Business Rules**:
- System automatically creates "默认分组" (Default Group) for each new user
- Cannot delete default group if it contains stocks (must move stocks first)
- stock_count updated automatically via database triggers

---

### 2. WatchlistItem

**Purpose**: Individual stock entries within watchlist groups

**Classification**: Reference Data (Type 2) - User-managed stock selections

**Storage**: PostgreSQL `user_watchlist` table

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| user_id | INTEGER | NOT NULL | Owner (redundant with group, for query optimization) |
| group_id | INTEGER | NOT NULL, FOREIGN KEY → watchlist_groups(id) | Parent group |
| stock_code | VARCHAR(20) | NOT NULL | Normalized stock code (e.g., "600519.SH") |
| stock_name | VARCHAR(100) | NULL | Display name (e.g., "贵州茅台") |
| added_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When added to watchlist |
| notes | TEXT | NULL | User-defined notes/annotations |

**Unique Constraints**:
- (user_id, group_id, stock_code) - Stock can only appear once per group

**Indexes**:
- PRIMARY KEY on id
- INDEX on (user_id, group_id) for group-scoped queries
- INDEX on (stock_code) for reverse lookups ("which groups contain this stock?")
- UNIQUE INDEX on (user_id, group_id, stock_code)

**Relationships**:
- MANY-TO-ONE with WatchlistGroup (many items belong to one group)
- FOREIGN KEY CASCADE on group_id (deleting group deletes all items)

**Validation Rules**:
1. stock_code must match pattern: `^\d{6}(\.(SH|SZ|HK))?$`
2. stock_code automatically normalized with exchange suffix before insert
3. stock_name max 100 characters (Chinese characters supported)
4. group_id must reference existing watchlist_groups.id
5. user_id must match group's user_id (enforced by application logic)

**State Transitions**:
- **Added** → Stock added to group (triggers stock_count increment)
- **Annotated** → Notes field updated
- **Moved** → Stock moved to different group (delete + insert)
- **Removed** → Stock deleted from group (triggers stock_count decrement)

**Business Rules**:
- Same stock can exist in multiple groups (different (group_id, stock_code) combinations)
- stock_code stored with exchange suffix for unambiguous identification
- stock_name copied from search result when added (not updated automatically)

---

### 3. StockQuote

**Purpose**: Real-time market data for a single stock

**Classification**: Market Data (Type 1) - High-frequency, ephemeral

**Storage**: NOT PERSISTED (fetched on-demand from AKShare API)

**Attributes** (returned by API only):

| Field | Type | Description |
|-------|------|-------------|
| symbol | STRING | Stock code with exchange suffix (e.g., "600519.SH") |
| name | STRING | Stock name (e.g., "贵州茅台") |
| current | FLOAT | Current/latest price |
| change | FLOAT | Price change from previous close (absolute) |
| change_percent | FLOAT | Price change percentage |
| high | FLOAT | Day's highest price |
| low | FLOAT | Day's lowest price |
| open | FLOAT | Opening price |
| previous_close | FLOAT | Previous trading day's close price |
| volume | INTEGER | Trading volume (shares) |
| amount | FLOAT | Trading amount (RMB) |
| timestamp | INTEGER | Unix timestamp of quote (seconds since epoch) |
| trading_status | STRING | "trading" or "halted" or "closed" |

**Data Source**: AKShare `stock_zh_a_spot_em()` function

**Validation Rules**:
1. symbol must be valid A-share or H-share code
2. All price fields >= 0
3. timestamp within last 24 hours (for real-time quotes)
4. trading_status must be one of allowed values

**Refresh Rate**: On-demand (no automatic polling)

**Business Rules**:
- Quotes unavailable outside trading hours return previous close data
- If stock not found in AKShare, API returns 404 error
- No historical quotes stored (use K-line data for historical analysis)

---

### 4. KLineDataPoint

**Purpose**: Single candlestick (K-line) for historical price analysis

**Classification**: Market Data (Type 1) - Daily/minute OHLCV data

**Storage**: NOT PERSISTED (fetched on-demand from AKShare API)

**Attributes** (returned by API as array):

| Field | Type | Description |
|-------|------|-------------|
| date | STRING | Trading date in ISO format (e.g., "2025-01-15") |
| timestamp | INTEGER | Unix timestamp (for frontend charting) |
| open | FLOAT | Opening price |
| high | FLOAT | Highest price during period |
| low | FLOAT | Lowest price during period |
| close | FLOAT | Closing price |
| volume | INTEGER | Trading volume (shares) |
| amount | FLOAT | Trading amount (RMB) |
| amplitude | FLOAT | Price amplitude percentage (optional) |
| change_percent | FLOAT | Day-over-day change percentage (optional) |

**Data Source**: AKShare `stock_zh_a_hist()` function

**Supported Periods**:
- Daily (日K): Default, most common
- Weekly (周K): Aggregated weekly data
- Monthly (月K): Aggregated monthly data

**Adjustment Types**:
- qfq (前复权): Forward-adjusted (recommended default)
- hfq (后复权): Backward-adjusted
- (none): Unadjusted

**Validation Rules**:
1. date must be valid trading day (no weekends/holidays)
2. open, high, low, close must satisfy: low <= open, close <= high
3. high >= max(open, close), low <= min(open, close)
4. volume >= 0, amount >= 0

**Business Rules**:
- Default query returns last 60 trading days
- Maximum query range: 250 trading days (1 year)
- Data returned in descending date order (newest first)
- Suspended trading days omitted from results

---

## Entity Relationships Diagram

```
┌──────────────────┐
│      User        │
│  (existing)      │
└────────┬─────────┘
         │
         │ 1:N (owns)
         │
         ▼
┌──────────────────┐
│ WatchlistGroup   │
│ ───────────────  │
│ id (PK)          │
│ user_id (FK)     │
│ group_name       │
│ created_at       │
│ sort_order       │
│ stock_count      │
└────────┬─────────┘
         │
         │ 1:N (contains)
         │ CASCADE DELETE
         │
         ▼
┌──────────────────┐
│ WatchlistItem    │
│ ───────────────  │
│ id (PK)          │
│ user_id          │
│ group_id (FK)    │◄──────────┐
│ stock_code       │           │
│ stock_name       │           │
│ added_at         │           │
│ notes            │           │
└──────────────────┘           │
                               │
                               │ references (lookup)
                               │
                               │
         ┌─────────────────────┴──────────────────┐
         │                                        │
         ▼                                        ▼
┌──────────────────┐                    ┌──────────────────┐
│  StockQuote      │                    │ KLineDataPoint   │
│  (ephemeral)     │                    │  (ephemeral)     │
│ ───────────────  │                    │ ───────────────  │
│ symbol           │                    │ date             │
│ name             │                    │ timestamp        │
│ current          │                    │ open             │
│ change           │                    │ high             │
│ ...              │                    │ low              │
│                  │                    │ close            │
│ Source: AKShare  │                    │ volume           │
│ API              │                    │                  │
└──────────────────┘                    │ Source: AKShare  │
                                        │ API              │
                                        └──────────────────┘
```

**Key Points**:
1. User → WatchlistGroup: One user can create many groups
2. WatchlistGroup → WatchlistItem: One group contains many stocks (CASCADE DELETE)
3. WatchlistItem.stock_code → StockQuote/KLine: Lookup relationship (no FK, external data)
4. StockQuote and KLineDataPoint not persisted (always fresh from AKShare)

---

## Data Lifecycle

### WatchlistGroup Lifecycle

1. **Creation**: User clicks "New Group" → `INSERT INTO watchlist_groups`
2. **Population**: User adds stocks → `INSERT INTO user_watchlist` → Trigger updates `stock_count`
3. **Modification**: User renames group → `UPDATE watchlist_groups SET group_name`
4. **Deletion**: User deletes group → `DELETE FROM watchlist_groups` → CASCADE deletes all items

### WatchlistItem Lifecycle

1. **Addition**: User clicks "Add to Watchlist" → Stock code normalized → `INSERT INTO user_watchlist`
2. **Annotation**: User edits notes → `UPDATE user_watchlist SET notes`
3. **Movement**: User moves to different group → `DELETE` + `INSERT` (transactional)
4. **Removal**: User removes stock → `DELETE FROM user_watchlist` → Trigger decrements `stock_count`

### StockQuote Lifecycle

1. **Request**: User enters stock code → API normalizes code → Calls AKShare
2. **Response**: AKShare returns DataFrame → Transformed to JSON → Returned to frontend
3. **Discard**: No persistence (ephemeral data)

### KLineDataPoint Lifecycle

1. **Request**: User clicks "Load Chart" → API validates stock code → Calls AKShare with date range
2. **Response**: AKShare returns DataFrame → Transformed to JSON array → Returned to frontend
3. **Rendering**: Frontend passes to ECharts candlestick component
4. **Discard**: No persistence (ephemeral data)

---

## Data Volume Estimates

| Entity | Expected Volume | Growth Rate | Retention |
|--------|-----------------|-------------|-----------|
| WatchlistGroup | 10-50 per user | Slow (1-2/month) | Indefinite |
| WatchlistItem | 10-100 per user | Medium (5-10/month) | Indefinite |
| StockQuote | N/A (not stored) | N/A | Ephemeral |
| KLineDataPoint | N/A (not stored) | N/A | Ephemeral |

**Assumptions**:
- 10 concurrent users for demo
- Average 5 watchlist groups per user
- Average 20 stocks per user across all groups
- Total database rows: ~500 (manageable)

---

## Data Integrity Rules

### Database-Level Constraints

1. **Foreign Keys**:
   - `user_watchlist.group_id` → `watchlist_groups.id` (CASCADE DELETE)

2. **Unique Constraints**:
   - `watchlist_groups`: (user_id, group_name)
   - `user_watchlist`: (user_id, group_id, stock_code)

3. **Check Constraints** (if implemented):
   - `watchlist_groups.stock_count >= 0`
   - `watchlist_groups.group_name != ''` (not empty string)

4. **Triggers**:
   - Update `watchlist_groups.stock_count` on INSERT/DELETE in `user_watchlist`

### Application-Level Validation

1. **Stock Code Format**: Validate pattern `^\d{6}(\.(SH|SZ|HK))?$` before database insert
2. **Group Name Length**: 1-100 characters after trimming whitespace
3. **User Ownership**: Verify `user_id` matches authenticated user before operations
4. **Default Group Protection**: Prevent deletion if group_name = "默认分组" and stock_count > 0

---

## Performance Considerations

### Indexing Strategy

- **watchlist_groups**: Index on `user_id` for user-scoped queries
- **user_watchlist**: Composite index on `(user_id, group_id)` for group listings
- **user_watchlist**: Single index on `stock_code` for reverse lookups

### Query Patterns

1. **Get all groups for user**: `SELECT * FROM watchlist_groups WHERE user_id = ? ORDER BY sort_order`
2. **Get stocks in group**: `SELECT * FROM user_watchlist WHERE group_id = ? ORDER BY added_at DESC`
3. **Check if stock in watchlist**: `SELECT EXISTS(SELECT 1 FROM user_watchlist WHERE user_id = ? AND stock_code = ?)`
4. **Get stock count per group**: Cached in `stock_count` column (no aggregation needed)

### Caching Strategy

- **watchlist_groups**: No caching needed (small dataset, infrequent changes)
- **user_watchlist**: No caching needed (user-specific data)
- **StockQuote**: Consider 30-second TTL cache if multiple users query same stock
- **KLineDataPoint**: Consider daily cache keyed by (stock_code, period, adjust)

---

## Security & Privacy

1. **Row-Level Security**: All queries filter by `user_id = current_authenticated_user_id`
2. **No Sensitive Data**: Watchlist data is not sensitive (publicly available stock codes)
3. **Notes Privacy**: User notes are private (never shared between users)
4. **SQL Injection Prevention**: All queries use parameterized statements

---

## Migration Considerations

### Initial Migration (001_watchlist_tables.sql)

1. Create `watchlist_groups` table
2. Create `user_watchlist` table with foreign key
3. Create indexes
4. Create trigger for `stock_count` maintenance
5. Insert "默认分组" for all existing users

### Future Enhancements (out of scope)

- Add `is_default` boolean to `watchlist_groups` (currently identified by name)
- Add `color` VARCHAR(7) to `watchlist_groups` for UI customization
- Add `alert_threshold` to `user_watchlist` for price alerts
- Add `last_viewed_at` to `user_watchlist` for sorting

---

## Appendix: Sample Data

### Sample WatchlistGroup

```json
{
  "id": 1,
  "user_id": 1,
  "group_name": "科技股",
  "created_at": "2025-01-15T10:30:00Z",
  "sort_order": 0,
  "stock_count": 5
}
```

### Sample WatchlistItem

```json
{
  "id": 101,
  "user_id": 1,
  "group_id": 1,
  "stock_code": "600519.SH",
  "stock_name": "贵州茅台",
  "added_at": "2025-01-15T11:00:00Z",
  "notes": "白酒龙头，长期持有"
}
```

### Sample StockQuote

```json
{
  "symbol": "600519.SH",
  "name": "贵州茅台",
  "current": 1850.50,
  "change": 25.30,
  "change_percent": 1.39,
  "high": 1865.00,
  "low": 1840.00,
  "open": 1845.00,
  "previous_close": 1825.20,
  "volume": 2500000,
  "amount": 4625000000,
  "timestamp": 1737025200,
  "trading_status": "trading"
}
```

### Sample KLineDataPoint

```json
{
  "date": "2025-01-15",
  "timestamp": 1737000000,
  "open": 1845.00,
  "high": 1865.00,
  "low": 1840.00,
  "close": 1850.50,
  "volume": 2500000,
  "amount": 4625000000,
  "amplitude": 1.37,
  "change_percent": 1.39
}
```
