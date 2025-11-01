# Data Model: Technical Analysis Feature

**Date**: 2025-10-13
**Feature**: 002-ta-lib-161
**Purpose**: Define all data entities, relationships, validation rules, and state transitions

## Entity Overview

This feature introduces 4 primary entities and leverages 2 existing entities:

**New Entities**:
1. **IndicatorMetadata** - Registry of all 161 indicators with parameters and metadata
2. **IndicatorConfiguration** - User-saved indicator combinations and parameters
3. **IndicatorCalculationRequest** - Transient request data for calculations
4. **IndicatorCalculationResult** - Calculated indicator values with metadata

**Existing Entities** (from current system):
5. **Stock** - Stock basic information (code, name, market)
6. **DailyBar** - OHLCV daily market data

---

## Entity Definitions

### 1. IndicatorMetadata

**Description**: Static registry entry for each of the 161 technical indicators. Loaded at application startup and cached in memory.

**Attributes**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| abbreviation | string | Yes | Unique, uppercase, 2-10 chars | Indicator short name (e.g., "MA", "RSI") |
| name | string | Yes | 3-50 chars | Full indicator name (e.g., "Moving Average") |
| category | enum | Yes | trend, momentum, volatility, volume, candlestick | Indicator classification |
| panel_type | enum | Yes | overlay, oscillator | Where indicator displays |
| parameters | array | Yes | Min 0 params | List of configurable parameters |
| parameters[].name | string | Yes | 3-30 chars | Parameter name (e.g., "timeperiod") |
| parameters[].type | enum | Yes | int, float, string | Parameter data type |
| parameters[].default | any | Yes | Must match type | Default parameter value |
| parameters[].min | number | No | For int/float types | Minimum valid value |
| parameters[].max | number | No | For int/float types | Maximum valid value |
| parameters[].options | array | No | For string types | Allowed string values |
| outputs | array | Yes | Min 1 output | Names of output series (e.g., ["ma"] or ["macd", "signal", "hist"]) |
| min_data_points_formula | string | Yes | Lambda expression | Formula to calculate minimum required data points |
| reference_lines | array | No | For oscillators | Horizontal lines (e.g., [30, 70] for RSI) |
| description | string | No | Max 500 chars | Indicator explanation |

**Example Record** (MA):
```json
{
  "abbreviation": "MA",
  "name": "Moving Average",
  "category": "trend",
  "panel_type": "overlay",
  "parameters": [
    {
      "name": "timeperiod",
      "type": "int",
      "default": 20,
      "min": 2,
      "max": 200
    }
  ],
  "outputs": ["ma"],
  "min_data_points_formula": "params['timeperiod']",
  "reference_lines": null,
  "description": "Average price over N periods, smoothing price action."
}
```

**Example Record** (MACD):
```json
{
  "abbreviation": "MACD",
  "name": "Moving Average Convergence Divergence",
  "category": "trend",
  "panel_type": "oscillator",
  "parameters": [
    {
      "name": "fastperiod",
      "type": "int",
      "default": 12,
      "min": 2,
      "max": 100
    },
    {
      "name": "slowperiod",
      "type": "int",
      "default": 26,
      "min": 2,
      "max": 100
    },
    {
      "name": "signalperiod",
      "type": "int",
      "default": 9,
      "min": 2,
      "max": 100
    }
  ],
  "outputs": ["macd", "signal", "hist"],
  "min_data_points_formula": "params['slowperiod'] + params['signalperiod']",
  "reference_lines": [0],
  "description": "Trend-following momentum indicator showing relationship between two EMAs."
}
```

**Validation Rules**:
- `abbreviation` must be unique across all indicators
- `min_data_points_formula` must evaluate to positive integer
- For `panel_type` = "oscillator", `category` cannot be "trend" (exception: MACD)
- All parameter defaults must pass their own min/max constraints
- `outputs` array length must match TA-Lib function return signature

**Relationships**:
- One-to-Many with `IndicatorConfiguration.indicators[]` (metadata referenced by abbreviation)

---

### 2. IndicatorConfiguration

**Description**: User-saved combination of indicators and their parameters. Allows quick reapplication of favorite analysis setups.

**Storage**: MySQL `indicator_configurations` table (Meta Data classification per constitution)

**Attributes**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | integer | Yes | Auto-increment PK | Unique configuration identifier |
| user_id | integer | Yes | FK to users table | Owner of this configuration |
| name | string | Yes | 1-100 chars, unique per user | User-defined configuration name |
| indicators | JSON array | Yes | 1-10 indicators | Array of indicator specs |
| indicators[].abbreviation | string | Yes | Valid from registry | Indicator abbreviation |
| indicators[].parameters | object | Yes | Matches indicator schema | Parameter key-value pairs |
| created_at | timestamp | Yes | Auto-generated | Configuration creation time |
| updated_at | timestamp | Yes | Auto-updated | Last modification time |
| last_used_at | timestamp | No | Nullable | Last application timestamp |

**Example Record**:
```json
{
  "id": 42,
  "user_id": 123,
  "name": "日内交易设置",
  "indicators": [
    {
      "abbreviation": "MA",
      "parameters": {"timeperiod": 5}
    },
    {
      "abbreviation": "MA",
      "parameters": {"timeperiod": 10}
    },
    {
      "abbreviation": "RSI",
      "parameters": {"timeperiod": 14}
    },
    {
      "abbreviation": "MACD",
      "parameters": {
        "fastperiod": 12,
        "slowperiod": 26,
        "signalperiod": 9
      }
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-03-20T14:22:00Z",
  "last_used_at": "2024-03-20T14:22:00Z"
}
```

**Validation Rules**:
- `name` must be unique per user (composite unique constraint: `user_id` + `name`)
- `indicators` array length: 1 ≤ length ≤ 10
- Each indicator `abbreviation` must exist in `IndicatorMetadata` registry
- Each indicator `parameters` must validate against its metadata schema
- Cannot save configuration with duplicate indicator + parameters combination
- `last_used_at` auto-updates on configuration application

**Relationships**:
- Many-to-One with `User` (via `user_id`)
- References `IndicatorMetadata` registry (via `indicators[].abbreviation`)

**State Transitions**:
```
┌──────────┐  user creates    ┌──────────┐
│   null   │ ──────────────> │  active  │
└──────────┘                  └────┬─────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
              user modifies   user applies   user deletes
                    │              │              │
                    ▼              ▼              ▼
              ┌──────────┐   ┌──────────┐   ┌──────────┐
              │ updated  │   │  used    │   │ deleted  │
              │(new      │   │(last_used│   │(soft     │
              │updated_at│   │_at set)  │   │delete)   │
              └────┬─────┘   └──────────┘   └──────────┘
                   │
                   └────────────> active
```

**Indexes**:
- Primary: `id`
- Foreign: `user_id`
- Composite: (`user_id`, `name`) UNIQUE
- Performance: `last_used_at` DESC (for "recently used" queries)

---

### 3. IndicatorCalculationRequest

**Description**: Transient request payload for calculating indicators. Not persisted to database, only validated and processed.

**Lifecycle**: Request → Validation → Calculation → Response (in-memory only)

**Attributes**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| symbol | string | Yes | Valid stock code format | Stock identifier (e.g., "600519.SH") |
| start_date | date | Yes | ISO 8601 format, ≤ end_date | Analysis start date |
| end_date | date | Yes | ISO 8601 format, ≥ start_date, ≤ today | Analysis end date |
| indicators | array | Yes | 1-10 indicators | Indicators to calculate |
| indicators[].abbreviation | string | Yes | Valid from registry | Indicator abbreviation |
| indicators[].parameters | object | Yes | Matches indicator schema | Parameter key-value pairs |

**Example Payload**:
```json
{
  "symbol": "600519.SH",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "indicators": [
    {
      "abbreviation": "MA",
      "parameters": {"timeperiod": 20}
    },
    {
      "abbreviation": "RSI",
      "parameters": {"timeperiod": 14}
    },
    {
      "abbreviation": "MACD",
      "parameters": {
        "fastperiod": 12,
        "slowperiod": 26,
        "signalperiod": 9
      }
    }
  ]
}
```

**Validation Rules** (enforced in Pydantic schema):
- `symbol`: Must match pattern `^\d{6}\.(SH|SZ)$`
- `start_date`: Must be before `end_date`
- `end_date`: Cannot be in the future (≤ today)
- Date range: Cannot exceed 3650 days (10 years)
- `indicators` array: 1 ≤ length ≤ 10 (performance constraint)
- Each indicator must exist in registry
- Each parameter must satisfy type and range constraints
- Duplicate indicator + parameters combination triggers warning (allowed but redundant)

**Relationships**:
- Temporary association with `Stock` (via `symbol`)
- Triggers loading of `DailyBar` records for date range
- References `IndicatorMetadata` for validation

---

### 4. IndicatorCalculationResult

**Description**: Calculated indicator values along with metadata. Returned in API response and optionally cached.

**Lifecycle**: Calculation → Response → [Optional] Cache → Expiry

**Attributes**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| symbol | string | Yes | Stock code | Stock identifier |
| start_date | date | Yes | ISO 8601 | Date range start |
| end_date | date | Yes | ISO 8601 | Date range end |
| ohlcv | array | Yes | Min 1 record | OHLCV data for context |
| ohlcv[].date | date | Yes | ISO 8601 | Trading date |
| ohlcv[].open | float | Yes | > 0 | Opening price |
| ohlcv[].high | float | Yes | > 0, ≥ open, close | Highest price |
| ohlcv[].low | float | Yes | > 0, ≤ open, close | Lowest price |
| ohlcv[].close | float | Yes | > 0 | Closing price |
| ohlcv[].volume | integer | Yes | ≥ 0 | Trading volume |
| indicators | object | Yes | Keys = abbreviations | Calculated indicators map |
| indicators[key].values | array | Yes | Length = ohlcv length | Indicator values (null for insufficient data) |
| indicators[key].parameters | object | Yes | Applied parameters | Parameters used for calculation |
| indicators[key].panel_type | enum | Yes | overlay, oscillator | Display location |
| indicators[key].reference_lines | array | No | For oscillators | Horizontal reference lines |
| calculation_time_ms | integer | Yes | ≥ 0 | Calculation duration |
| data_points_count | integer | Yes | > 0 | Number of OHLCV records |
| cache_hit | boolean | Yes | true/false | Whether result from cache |

**Example Response**:
```json
{
  "symbol": "600519.SH",
  "start_date": "2024-01-01",
  "end_date": "2024-01-10",
  "ohlcv": [
    {"date": "2024-01-02", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.5, "volume": 10000},
    {"date": "2024-01-03", "open": 101.5, "high": 103.0, "low": 100.5, "close": 102.0, "volume": 12000},
    {"date": "2024-01-04", "open": 102.0, "high": 104.0, "low": 101.0, "close": 103.5, "volume": 15000}
  ],
  "indicators": {
    "MA": {
      "values": [null, null, 102.0, 102.5, 103.0],  // First 2 nulls (period=3)
      "parameters": {"timeperiod": 3},
      "panel_type": "overlay",
      "reference_lines": null
    },
    "RSI": {
      "values": [null, null, null, null, 65.3, 68.7],  // First 4 nulls (period=5)
      "parameters": {"timeperiod": 5},
      "panel_type": "oscillator",
      "reference_lines": [30, 70]
    }
  },
  "calculation_time_ms": 125,
  "data_points_count": 5,
  "cache_hit": false
}
```

**Validation Rules**:
- `ohlcv` array must be sorted by date ascending
- OHLC relationships: `low ≤ open, close ≤ high`
- `indicators` keys must match requested abbreviations
- Each indicator `values` array length must equal `ohlcv` array length
- Null values allowed in early periods (insufficient data for calculation)
- `calculation_time_ms` excludes network time (server-side only)

**Caching Strategy** (Redis):
- **Cache Key**: `indicator:{symbol}:{start_date}:{end_date}:{indicators_hash}`
  - Example: `indicator:600519.SH:2024-01-01:2024-12-31:md5(MA_20_RSI_14)`
- **Cache TTL**:
  - 3600s (1 hour) if `end_date` = today (data may update)
  - 86400s (24 hours) if `end_date` < today (historical data immutable)
- **Cache Invalidation**: Automatic expiry only (no manual invalidation)

**Relationships**:
- Associated with `Stock` (via `symbol`)
- Derived from `DailyBar` records
- References `IndicatorMetadata` for metadata fields

---

### 5. Stock (Existing Entity)

**Description**: Basic stock information from reference data. Used for symbol validation and stock search.

**Storage**: MySQL `stocks` table (Reference Data classification)

**Relevant Attributes**:

| Field | Type | Description |
|-------|------|-------------|
| code | string | Stock code (e.g., "600519") |
| exchange | string | Exchange (e.g., "SH", "SZ") |
| name | string | Stock name (e.g., "贵州茅台") |
| status | enum | Trading status (active, suspended, delisted) |

**Usage in Feature**:
- Validate `symbol` in calculation requests
- Power stock search autocomplete in UI
- Filter to active stocks only (exclude suspended/delisted)

---

### 6. DailyBar (Existing Entity)

**Description**: Daily OHLCV market data. Source data for indicator calculations.

**Storage**: PostgreSQL `daily_bars` table (Market Data classification)

**Relevant Attributes**:

| Field | Type | Description |
|-------|------|-------------|
| symbol | string | Stock identifier (e.g., "600519.SH") |
| date | date | Trading date |
| open | float | Opening price |
| high | float | Highest price |
| low | float | Lowest price |
| close | float | Closing price |
| volume | integer | Trading volume |
| amount | float | Trading amount |

**Usage in Feature**:
- Load via existing `GET /api/data/stocks/daily` endpoint
- Transform to NumPy arrays for TA-Lib input
- Return in `IndicatorCalculationResult.ohlcv` for chart rendering

**Data Quality Requirements**:
- No missing dates in range (gaps indicate holidays/suspensions)
- OHLC relationships enforced: `low ≤ open, close ≤ high`
- Volume ≥ 0 (zero volume allowed for suspended days)

---

## Entity Relationships Diagram

```
┌─────────────────────┐
│  IndicatorMetadata  │◄──────────────────┐
│  (Static Registry)  │                   │
│  • 161 indicators   │                   │
│  • Parameters       │                   │
│  • Metadata         │                   │
└─────────────────────┘                   │
         ▲                                │
         │ references                     │ references
         │ (via abbreviation)             │ (via abbreviation)
         │                                │
┌────────┴────────────────┐     ┌─────────┴─────────────────┐
│ IndicatorConfiguration  │     │ IndicatorCalculationRequest│
│ (User-Saved)            │     │ (Transient)                │
│ • user_id               │     │ • symbol                   │
│ • name                  │     │ • date range               │
│ • indicators[]          │     │ • indicators[]             │
└─────────────────────────┘     └────────┬───────────────────┘
         │                               │
         │                               │ triggers
         │ owned by                      │ calculation
         │                               │
         ▼                               ▼
┌─────────────────────┐     ┌───────────────────────────────┐
│       User          │     │ IndicatorCalculationResult    │
│  (Existing)         │     │ (Response + Cache)            │
└─────────────────────┘     │ • ohlcv[]                     │
                             │ • indicators{}                │
         ┌───────────────────┤ • calculation_time_ms        │
         │ validates          └────────┬──────────────────────┘
         │ symbol                      │
         │                             │ includes
         ▼                             │ ohlcv data
┌─────────────────────┐                │
│       Stock         │                │
│  (Existing)         │                │
│  • code             │                │
│  • exchange         │                │
│  • name             │                │
└─────────────────────┘                │
         │                             │
         │ has many                    │
         │ daily bars                  │
         ▼                             │
┌─────────────────────┐                │
│     DailyBar        │◄───────────────┘
│  (Existing)         │     sources
│  • symbol           │     data from
│  • date             │
│  • OHLC             │
│  • volume           │
└─────────────────────┘
```

---

## Data Flow

### Flow 1: User Calculates Indicators

```
1. User Input (Frontend)
   ├─ Select stock: "600519.SH"
   ├─ Select date range: 2024-01-01 to 2024-12-31
   └─ Add indicators: MA(20), RSI(14)

2. Create IndicatorCalculationRequest
   └─ Validate against schema (Pydantic)

3. Load Stock Data
   ├─ Query DailyBar table for symbol + date range
   ├─ Transform to NumPy arrays
   └─ Validate data completeness

4. Check Cache (optional)
   ├─ Generate cache key from request
   ├─ Lookup in Redis
   └─ If hit: return cached result

5. Calculate Indicators
   ├─ For each requested indicator:
   │  ├─ Load metadata from IndicatorMetadata registry
   │  ├─ Validate min_data_points requirement
   │  ├─ Call TA-Lib function with NumPy arrays
   │  └─ Handle NaN values for early periods
   └─ Aggregate all results

6. Create IndicatorCalculationResult
   ├─ Include OHLCV data
   ├─ Include indicator values
   ├─ Record calculation time
   └─ Mark cache_hit status

7. Cache Result (optional)
   ├─ Serialize result to JSON
   ├─ Store in Redis with TTL
   └─ Log cache write

8. Return Response
   └─ Send JSON to frontend
```

### Flow 2: User Saves Configuration

```
1. User Input (Frontend)
   ├─ Name: "日内交易设置"
   └─ Current indicators: [MA(5), MA(10), RSI(14)]

2. Create IndicatorConfiguration
   ├─ Populate user_id from auth context
   ├─ Populate indicators array
   └─ Validate against schema

3. Check Duplicate Name
   ├─ Query MySQL for (user_id, name)
   └─ If exists: return HTTP 409 Conflict

4. Save to Database
   ├─ INSERT into indicator_configurations
   ├─ Set created_at, updated_at
   └─ Return generated id

5. Return Response
   └─ Send saved configuration with id
```

### Flow 3: User Applies Saved Configuration

```
1. User Input (Frontend)
   └─ Select configuration: id=42

2. Load Configuration
   ├─ Query MySQL by id and user_id
   └─ Validate ownership

3. Update last_used_at
   └─ UPDATE indicator_configurations SET last_used_at = NOW()

4. Extract Indicators
   └─ Parse indicators JSON array

5. Trigger Calculation (Flow 1)
   ├─ Use current symbol and date range
   ├─ Apply saved indicators and parameters
   └─ Return calculation result

6. Update UI
   ├─ Populate indicator selector with saved indicators
   └─ Render chart with calculated results
```

---

## Validation Matrix

| Validation Type | Layer | Enforced By | Error Code |
|-----------------|-------|-------------|------------|
| Symbol format | Request | Pydantic regex | 400 |
| Symbol exists | Request | Database lookup | 404 |
| Date range order | Request | Pydantic validator | 400 |
| Date range length | Request | Pydantic validator | 400 |
| Indicator abbreviation | Request | Registry lookup | 400 |
| Parameter types | Request | Pydantic schema | 422 |
| Parameter ranges | Request | Pydantic validator | 422 |
| Indicators count (1-10) | Request | Pydantic validator | 400 |
| Min data points | Calculation | Pre-calculation check | 422 |
| Data completeness | Calculation | OHLCV validation | 422 |
| OHLC relationships | Calculation | Data quality check | 500 |
| Configuration name uniqueness | Save | Database constraint | 409 |
| Configuration ownership | Load | Authorization check | 403 |

---

## Performance Considerations

### Data Volume Estimates

| Entity | Records | Growth Rate | Storage Size |
|--------|---------|-------------|--------------|
| IndicatorMetadata | 161 | Static | ~100KB (in-memory) |
| IndicatorConfiguration | ~50 per user × 1000 users = 50K | Linear with users | ~5MB |
| DailyBar (per stock) | ~250/year × 10 years = 2500 | 250/year | ~125KB/stock |
| IndicatorCalculationResult (cached) | Variable | LRU eviction | ~1MB/result × 1000 cache = 1GB Redis |

### Query Optimization

**Critical Queries**:

1. **Load OHLCV for calculation** (hot path):
   ```sql
   SELECT date, open, high, low, close, volume
   FROM daily_bars
   WHERE symbol = ? AND date BETWEEN ? AND ?
   ORDER BY date ASC
   ```
   - **Index**: (`symbol`, `date`) composite
   - **Expected rows**: 250-2500
   - **Target latency**: <50ms

2. **Load user configurations**:
   ```sql
   SELECT id, name, indicators, last_used_at
   FROM indicator_configurations
   WHERE user_id = ?
   ORDER BY last_used_at DESC NULLS LAST
   LIMIT 50
   ```
   - **Index**: (`user_id`, `last_used_at`)
   - **Expected rows**: <50
   - **Target latency**: <20ms

3. **Check configuration name uniqueness**:
   ```sql
   SELECT COUNT(*)
   FROM indicator_configurations
   WHERE user_id = ? AND name = ?
   ```
   - **Index**: (`user_id`, `name`) unique
   - **Expected rows**: 0 or 1
   - **Target latency**: <10ms

---

## Security & Privacy

### Data Isolation

- **IndicatorConfiguration**: Strictly filtered by `user_id` (no cross-user access)
- **IndicatorCalculationResult**: No user data stored (transient + cache only)
- **Cache keys**: Do not include user_id (results are user-agnostic)

### Sensitive Data

- **No PII**: Feature does not store personal information
- **Stock symbols**: Public data, no privacy concerns
- **Indicator parameters**: Public knowledge, no confidentiality

### Authorization

- **API endpoints**: Require valid JWT token (user_id extracted from token)
- **Configuration CRUD**: Validate ownership before read/update/delete
- **Stock data access**: No additional authorization (public market data)

---

## Data Retention

### Persistent Data

- **IndicatorConfiguration**: Retain indefinitely (user-controlled deletion)
  - Soft delete: Add `deleted_at` column for accidental deletion recovery (30-day retention)

### Transient Data

- **IndicatorCalculationRequest**: Not stored (request-scoped only)
- **IndicatorCalculationResult**: Cached with TTL, then evicted automatically

### Backup & Recovery

- **IndicatorConfiguration table**: Included in daily MySQL backup
- **Recovery process**: Standard MySQL restore procedure
- **Export functionality**: Users can export configurations as JSON (manual backup)

---

## Migration Strategy

### Phase 1: Database Schema

1. Create `indicator_configurations` table in MySQL
   ```sql
   CREATE TABLE indicator_configurations (
       id INT AUTO_INCREMENT PRIMARY KEY,
       user_id INT NOT NULL,
       name VARCHAR(100) NOT NULL,
       indicators JSON NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
       last_used_at TIMESTAMP NULL,
       UNIQUE KEY uk_user_name (user_id, name),
       KEY idx_user_id (user_id),
       KEY idx_last_used (last_used_at),
       FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
   ```

2. Add to `table_config.yaml` (configuration-driven management)

### Phase 2: Indicator Registry Initialization

1. Load 161 indicators from TA-Lib at application startup
2. Populate `IndicatorMetadata` in-memory registry
3. Expose via `GET /api/indicators/registry` endpoint

### Phase 3: Redis Cache Setup (Optional)

1. Configure Redis connection in `.env`
2. Set eviction policy: `maxmemory-policy allkeys-lru`
3. Allocate 1GB memory for indicator cache

---

## Testing Data

### Test Datasets

**Indicator Metadata (Sample)**:
- MA, EMA, SMA, WMA (trend overlays)
- RSI, KDJ, CCI, STOCH (momentum oscillators)
- MACD (trend oscillator)
- ATR, BBANDS (volatility indicators)
- OBV, AD (volume indicators)
- CDLDOJI, CDLHAMMER (candlestick patterns)

**Mock OHLCV Data**:
- Symbol: "600000.SH" (test stock)
- Date range: 2024-01-01 to 2024-12-31 (252 trading days)
- Price range: 100-110 (realistic volatility)
- Volume range: 10000-50000

**Mock User Configurations**:
- User 1: "Day Trading" (MA5, MA10, RSI14)
- User 1: "Swing Trading" (MA20, MA50, MACD)
- User 2: "Momentum Analysis" (RSI, KDJ, CCI)

### Edge Cases for Testing

1. **Insufficient data points**: Request MA(200) with only 50 days of data
2. **Empty date range**: start_date = end_date
3. **Holiday gaps**: Date range includes non-trading days
4. **Suspended stock**: Symbol with zero volume days
5. **Maximum indicators**: Request all 10 allowed indicators
6. **Duplicate indicators**: Request MA(20) twice
7. **Invalid parameters**: timeperiod = -1, timeperiod = 1000
8. **Non-existent symbol**: "999999.SH"
9. **Future dates**: end_date = tomorrow
10. **Configuration name collision**: Save with existing name

---

## Appendix: Full Indicator Registry Structure

The complete 161-indicator registry follows this JSON schema:

```typescript
type IndicatorRegistry = Record<string, {
  abbreviation: string
  name: string
  category: 'trend' | 'momentum' | 'volatility' | 'volume' | 'candlestick'
  panel_type: 'overlay' | 'oscillator'
  parameters: Array<{
    name: string
    type: 'int' | 'float' | 'string'
    default: any
    min?: number
    max?: number
    options?: string[]
  }>
  outputs: string[]
  min_data_points_formula: string
  reference_lines?: number[]
  description?: string
}>
```

**Category Distribution**:
- Trend: 32 indicators (MA, EMA, MACD, ADX, SAR, etc.)
- Momentum: 38 indicators (RSI, KDJ, CCI, STOCH, ROC, etc.)
- Volatility: 7 indicators (ATR, NATR, TRANGE, BBANDS variants)
- Volume: 4 indicators (OBV, AD, ADOSC, MFI)
- Candlestick: 61 pattern recognition functions (CDL series)

Full registry will be generated programmatically from TA-Lib introspection and stored in `backend/app/services/indicator_registry.py`.
