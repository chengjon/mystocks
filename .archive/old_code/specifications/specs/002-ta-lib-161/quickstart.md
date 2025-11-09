# Quick Start Guide: Technical Analysis Feature

**Feature**: 002-ta-lib-161 - Technical Analysis with 161 Indicators
**For**: Developers implementing this feature
**Last Updated**: 2025-10-13

## Prerequisites

### Backend
- Python 3.11+
- TA-Lib 0.6.7 (verify: `python -c "import talib; print(talib.__version__)"`)
- FastAPI 0.104+
- Access to PostgreSQL (OHLCV data) and MySQL (configurations)
- Redis (optional, for caching)

### Frontend
- Node.js 18+ with bun package manager
- Vue 3.4+
- klinecharts 9.8+ (verify in `package.json`)
- Element Plus 2.4+

## Project Setup

### 1. Environment Configuration

Create or update `.env` file in project root:

```bash
# Database connections (existing)
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5438
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=c790414J
POSTGRESQL_DATABASE=mystocks_history

MYSQL_HOST=192.168.123.104
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=c790414J
MYSQL_DATABASE=mystocks_reference

# Redis (optional, for caching)
REDIS_HOST=192.168.123.104
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

### 2. Database Schema Setup

Add to `table_config.yaml`:

```yaml
tables:
  - name: indicator_configurations
    database: mysql
    classification: USER_CONFIG
    schema:
      columns:
        - name: id
          type: INT
          primary_key: true
          auto_increment: true
        - name: user_id
          type: INT
          nullable: false
        - name: name
          type: VARCHAR(100)
          nullable: false
        - name: indicators
          type: JSON
          nullable: false
        - name: created_at
          type: TIMESTAMP
          default: CURRENT_TIMESTAMP
        - name: updated_at
          type: TIMESTAMP
          default: CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        - name: last_used_at
          type: TIMESTAMP
          nullable: true
      indexes:
        - name: uk_user_name
          columns: [user_id, name]
          unique: true
        - name: idx_user_id
          columns: [user_id]
        - name: idx_last_used
          columns: [last_used_at]
      foreign_keys:
        - column: user_id
          references: users.id
          on_delete: CASCADE
```

Run table creation:
```bash
python -c "from core import ConfigDrivenTableManager; mgr = ConfigDrivenTableManager(); mgr.validate_all_table_structures()"
```

## Implementation Roadmap

Follow this order based on prioritized user stories:

### Phase 1: P1 - Basic Trend Indicators (MVP)

**Goal**: Users can view stock K-line charts with MA indicators

**Backend Tasks**:
1. Create `indicator_registry.py` with 161 indicators metadata
2. Create `indicator_calculator.py` with TA-Lib wrapper
3. Create `indicators.py` API endpoint: `POST /api/indicators/calculate`
4. Integrate with existing `GET /api/data/stocks/daily` for OHLCV data

**Frontend Tasks**:
1. Create `KLineChart.vue` component using klinecharts
2. Create `IndicatorSelector.vue` with trend indicators
3. Update `TechnicalAnalysis.vue` main view
4. Implement stock search and date range picker

**Test Command**:
```bash
# Backend
pytest web/backend/tests/test_indicators.py::test_calculate_ma

# Frontend
cd web/frontend && npm run test -- KLineChart.spec.ts
```

**Acceptance Criteria**:
- Chart displays in <3 seconds with MA(20)
- Hover tooltip shows OHLC + indicator values
- Date range change recalculates indicators

### Phase 2: P2 - Momentum Indicators

**Goal**: Add RSI, KDJ, CCI in separate oscillator panels

**Backend Tasks**:
1. Extend `indicator_calculator.py` with momentum category
2. Update response schema for multi-panel data

**Frontend Tasks**:
1. Create `IndicatorPanel.vue` for oscillator panels
2. Add momentum category to `IndicatorSelector.vue`
3. Implement reference lines (RSI 30/70, etc.)

**Test Command**:
```bash
curl -X POST http://localhost:8888/api/indicators/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "600519.SH",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "indicators": [
      {"abbreviation": "MA", "parameters": {"timeperiod": 20}},
      {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
    ]
  }'
```

### Phase 3: P2 - Candlestick Pattern Detection

**Goal**: Automatically detect and mark CDL patterns on chart

**Backend Tasks**:
1. Implement all 61 CDL functions in registry
2. Add pattern detection logic to calculator
3. Return pattern markers in response

**Frontend Tasks**:
1. Render pattern icons on candles
2. Create pattern summary panel
3. Implement pattern filtering

### Phase 4: P3 - Configuration Persistence

**Goal**: Users can save and load indicator configurations

**Backend Tasks**:
1. Create `indicator_config.py` API endpoints (CRUD)
2. Implement MySQL storage with user_id isolation
3. Add `last_used_at` auto-update logic

**Frontend Tasks**:
1. Create `ConfigSaver.vue` dialog
2. Create `ConfigLoader.vue` dialog
3. Implement configuration list with sorting

**Test Command**:
```bash
# Save configuration
curl -X POST http://localhost:8888/api/indicators/configs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Setup",
    "indicators": [
      {"abbreviation": "MA", "parameters": {"timeperiod": 20}},
      {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
    ]
  }'

# List configurations
curl http://localhost:8888/api/indicators/configs \
  -H "Authorization: Bearer $TOKEN"
```

### Phase 5: P3 - Multi-Chart Comparison (Optional)

**Goal**: Compare multiple stocks side-by-side

**Frontend Tasks**:
1. Implement chart grid layout (2x2 or 1x4)
2. Synchronize zoom/pan across charts
3. "Apply to all" button for indicators

## Key Files to Modify

### Backend

| File | Purpose | Lines (est.) |
|------|---------|--------------|
| `web/backend/app/services/indicator_registry.py` | 161 indicators metadata | ~1500 |
| `web/backend/app/services/indicator_calculator.py` | TA-Lib wrapper service | ~500 |
| `web/backend/app/api/indicators.py` | Calculation API endpoints | ~300 |
| `web/backend/app/api/indicator_config.py` | Configuration CRUD endpoints | ~200 |
| `web/backend/app/models/indicator_config.py` | SQLAlchemy models | ~50 |
| `web/backend/app/schemas/indicator_request.py` | Pydantic request schemas | ~100 |
| `web/backend/app/schemas/indicator_response.py` | Pydantic response schemas | ~150 |

### Frontend

| File | Purpose | Lines (est.) |
|------|---------|--------------|
| `web/frontend/src/views/TechnicalAnalysis.vue` | Main feature page | ~400 |
| `web/frontend/src/components/chart/KLineChart.vue` | klinecharts integration | ~350 |
| `web/frontend/src/components/indicators/IndicatorSelector.vue` | Indicator picker UI | ~300 |
| `web/frontend/src/composables/useIndicators.ts` | Indicator state management | ~200 |
| `web/frontend/src/composables/useChart.ts` | Chart state management | ~250 |
| `web/frontend/src/services/indicatorService.ts` | API client | ~150 |

## Development Workflow

### 1. Start Development Servers

```bash
# Terminal 1: Backend (already running at port 8888)
cd web/backend
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload

# Terminal 2: Frontend (already running at port 3002)
cd web/frontend
npm run dev
```

### 2. Test Backend API

```bash
# Get indicator registry
curl http://localhost:8888/api/indicators/registry

# Calculate indicators (requires authentication)
curl -X POST http://localhost:8888/api/indicators/calculate \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### 3. Test Frontend

Open browser: `http://localhost:3002/technical-analysis`

## Common Pitfalls & Solutions

### Issue 1: "TA-Lib not found"

**Symptom**: `ModuleNotFoundError: No module named 'talib'`

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install -y libta-lib0-dev
pip install TA-Lib

# macOS
brew install ta-lib
pip install TA-Lib

# Verify installation
python -c "import talib; print(talib.get_functions())"
```

### Issue 2: "Insufficient data points"

**Symptom**: API returns HTTP 422 with error_code "INSUFFICIENT_DATA"

**Solution**:
- Ensure date range provides enough data points for indicator
- Example: MA(200) requires at least 200 trading days
- Check `min_data_points_formula` in indicator metadata

### Issue 3: klinecharts chart not rendering

**Symptom**: Empty chart container in frontend

**Solution**:
```typescript
// Ensure container has explicit height
<div id="chart-container" style="height: 600px; width: 100%;"></div>

// Dispose chart on unmount
onUnmounted(() => {
  if (chartInstance.value) {
    dispose(chartInstance.value)
  }
})
```

### Issue 4: CORS errors in development

**Symptom**: `Access to fetch blocked by CORS policy`

**Solution**: Verify `web/backend/app/main.py` includes port 3002:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002"],  # Add this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Optimization Tips

### Backend
- Use NumPy arrays directly (avoid Python loops)
- Batch calculate all indicators in single pass over data
- Enable Redis caching for repeated requests
- Profile with `@profile` decorator for hot paths

### Frontend
- Lazy load chart component (`const KLineChart = defineAsyncComponent(...)`)
- Debounce parameter updates (300ms delay)
- Use virtual scrolling for >2000 candles
- Implement request cancellation for rapid date range changes

## Debugging Tools

### Backend
```python
# Add to indicator_calculator.py for profiling
import time

start = time.time()
result = talib.SMA(close_prices, timeperiod=20)
print(f"MA(20) calculation: {(time.time() - start) * 1000}ms")
```

### Frontend
```typescript
// Vue DevTools: Inspect component state
import { devtools } from 'vue'

// Performance measurement
console.time('indicator-calculation')
await indicatorService.calculate(request)
console.timeEnd('indicator-calculation')
```

## Testing Strategy

### Backend Tests
```bash
# Run all indicator tests
pytest web/backend/tests/test_indicators.py -v

# Run specific test
pytest web/backend/tests/test_indicators.py::test_calculate_ma -v

# Performance test
pytest web/backend/tests/test_indicator_performance.py::test_10_indicators_1year -v --benchmark
```

### Frontend Tests
```bash
cd web/frontend

# Run all tests
npm run test

# Run specific component test
npm run test -- KLineChart.spec.ts

# Run with coverage
npm run test:coverage
```

## Next Steps

After completing Phase 1 (P1 - Basic Trend Indicators):

1. Run acceptance tests from spec.md
2. Update checklist: `specs/002-ta-lib-161/checklists/requirements.md`
3. Proceed to Phase 2 (P2 - Momentum Indicators)
4. Document any architectural decisions in `research.md`

## Support & Resources

- **TA-Lib Documentation**: https://ta-lib.org/
- **klinecharts Documentation**: https://klinecharts.com/en-US/docs/
- **FastAPI Documentation**: https://fastapi.tianggu.com/
- **Vue 3 Documentation**: https://vuejs.org/

## Quick Reference: Common TA-Lib Functions

```python
# Trend Indicators
talib.SMA(close, timeperiod=20)  # Simple Moving Average
talib.EMA(close, timeperiod=20)  # Exponential Moving Average
talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

# Momentum Indicators
talib.RSI(close, timeperiod=14)  # Relative Strength Index
talib.CCI(high, low, close, timeperiod=14)  # Commodity Channel Index
talib.STOCH(high, low, close, fastk_period=5, slowk_period=3, slowd_period=3)  # KDJ

# Volatility Indicators
talib.ATR(high, low, close, timeperiod=14)  # Average True Range
talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)  # Bollinger Bands

# Volume Indicators
talib.OBV(close, volume)  # On Balance Volume
talib.AD(high, low, close, volume)  # Accumulation/Distribution

# Candlestick Patterns
talib.CDLDOJI(open, high, low, close)  # Doji
talib.CDLHAMMER(open, high, low, close)  # Hammer
talib.CDLENGULFING(open, high, low, close)  # Engulfing Pattern
```

All functions return NumPy arrays with NaN for insufficient data periods.
