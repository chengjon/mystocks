# Phase 2: Real Data Integration Implementation Plan

**Start Date**: 2026-01-02
**Status**: 🎯 **Ready to Begin**
**Prerequisites**: ✅ API Standardization Complete
**Approach**: Read-First, Low-Risk, High-Value

---

## Executive Summary

### Strategic Approach

Building on your excellent recommendation:
> "Start with the Read-Only modules as planned: Industry, Concept, and Stock List. These are low-risk and high-value for visual confirmation."

**Why This Order**:
1. **Read-Only** → Zero data corruption risk
2. **Simple Queries** → Easy to verify correctness
3. **Visual Feedback** → Immediate confirmation of success
4. **Building Blocks** → Foundation for complex modules

### Success Metrics

| Phase | Modules | Risk | Value | Timeline |
|-------|---------|------|-------|----------|
| 2.1 | Industry & Concept | 🟢 Low | 🔴 High | 2-3 hours |
| 2.2 | Stock List & Search | 🟢 Low | 🟡 Medium | 3-4 hours |
| 2.3 | K-Line Data | 🟡 Medium | 🔴 High | 4-6 hours |
| 2.4 | Real-time Quotes | 🟡 Medium | 🟡 Medium | 3-4 hours |

**Total Estimated Time**: 12-17 hours

---

## Phase 2.1: Industry & Concept Lists

### Objectives

- [ ] Verify industry/concept data exists in database
- [ ] Test API endpoints return real data
- [ ] Verify frontend displays industry list
- [ ] Test filter functionality
- [ ] Validate search features

### Database Verification

#### Step 1: Check Data Availability

```sql
-- Connect to PostgreSQL
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks

-- Check industries
SELECT COUNT(*) as total_industries
FROM stock_industries;

-- Expected: > 50 industries

-- Sample data
SELECT industry_name, COUNT(*) as stock_count
FROM stock_industries
GROUP BY industry_name
ORDER BY stock_count DESC
LIMIT 10;

-- Check concepts
SELECT COUNT(*) as total_concepts
FROM stock_concepts;

-- Expected: > 100 concepts

-- Sample concepts
SELECT concept_name, COUNT(*) as stock_count
FROM stock_concepts
GROUP BY concept_name
ORDER BY stock_count DESC
LIMIT 10;
```

#### Step 1.1: Data Integrity Checks (⭐ Gemini Review Feedback)

**Why This Matters**: Prevents frontend "blank" filters where stocks exist but don't appear under their listed industry.

```sql
-- Integrity Check 1: Ensure stocks reference valid industries
SELECT COUNT(*) as orphaned_stocks
FROM stocks_basic
WHERE industry NOT IN (SELECT industry_name FROM stock_industries);

-- Expected: 0 (no orphaned stocks)
-- If > 0: These stocks won't show in industry filters

-- Integrity Check 2: Industry coverage verification
SELECT
  i.industry_name,
  COUNT(sb.symbol) as stock_count,
  CASE WHEN COUNT(sb.symbol) = 0 THEN 'EMPTY' ELSE 'OK' END as status
FROM stock_industries i
LEFT JOIN stocks_basic sb ON i.industry_name = sb.industry
GROUP BY i.industry_name
HAVING COUNT(sb.symbol) = 0;  -- Find industries with no stocks

-- Expected: Empty result (all industries have stocks)
```

**If Orphaned Data Found**:
```sql
-- Option A: Fix industry names in stocks_basic
UPDATE stocks_basic sb
SET industry = (
  SELECT industry_name
  FROM stock_industries i
  WHERE sb.industry LIKE '%' || i.industry_name || '%'
  LIMIT 1
)
WHERE industry NOT IN (SELECT industry_name FROM stock_industries);

-- Option B: Create missing industry entries
INSERT INTO stock_industries (industry_name, industry_code)
SELECT DISTINCT
  sb.industry,
  'BK' || ROW_NUMBER() OVER (ORDER BY sb.industry)
FROM stocks_basic sb
WHERE sb.industry NOT IN (SELECT industry_name FROM stock_industries)
  AND sb.industry IS NOT NULL
  AND sb.industry != '';
```

**Success Criteria**:
- ✅ Industries exist (>50 records)
- ✅ Concepts exist (>100 records)
- ✅ Data looks correct (names are valid)
- ✅ **No orphaned stocks** (Gemini recommendation)

### API Endpoint Testing

#### Step 2: Test Backend API

```bash
# Set authentication token
export TOKEN="dev-mock-token-for-development"

# Test 1: Get industries
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/data/stocks/industries" | jq '.'
```

**Expected Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "industry_name": "银行",
      "industry_code": "BK0001",
      "description": "银行业"
    },
    ...
  ]
}
```

```bash
# Test 2: Get concepts
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/data/stocks/concepts" | jq '.'
```

**Success Criteria**:
- ✅ Returns 200 OK
- ✅ Response contains industry list
- ✅ Response contains concept list
- ✅ Data structure matches frontend expectations
- ✅ **All industries have stocks** (no empty filters)

### Frontend Integration Verification

#### Step 3: Browser Testing

```bash
# 1. Open frontend
open http://localhost:3020

# 2. Navigate to Market Data page
# URL: http://localhost:3020/market-data

# 3. Open DevTools (F12)
# 4. Go to Network tab
# 5. Look for API calls:
#    - GET /api/v1/data/stocks/industries
#    - GET /api/v1/data/stocks/concepts
```

**Expected Results**:
- ✅ Industry dropdown/selector populated
- ✅ Concept dropdown/selector populated
- ✅ Can filter by industry
- ✅ Can filter by concept
- ✅ UI displays correctly (no loading spinners forever)

### Troubleshooting Guide

#### Problem: API returns empty data

**Diagnosis**:
```bash
# Check database directly
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks \
  -c "SELECT COUNT(*) FROM stock_industries;"

# If 0: Data not populated
# If >0: API not connecting to database
```

**Solution**:
```python
# Check backend configuration
# File: web/backend/.env

POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5438
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=<correct_password>
POSTGRESQL_DATABASE=mystocks

# Restart backend
pm2 restart mystocks-backend
```

#### Problem: Frontend doesn't display data

**Diagnosis**:
```javascript
// Browser Console (F12)
// Check for:
// - API call was made (Network tab)
// - Response status (should be 200)
// - Response structure (matches frontend model?)
```

**Solution**:
```typescript
// Check frontend API adapter
// File: web/frontend/src/api/adapters/dataAdapter.ts

// Ensure response transformation matches actual API response
export function adaptIndustries(apiResponse: UnifiedResponse<Industry[]>) {
  return {
    industries: apiResponse.data.map(item => ({
      name: item.industry_name,  // ← Check field mapping
      code: item.industry_code,
      description: item.description
    }))
  }
}
```

---

## Phase 2.2: Stock List & Search

### Objectives

- [ ] Verify stock basic data exists
- [ ] Test paginated stock list API
- [ ] Implement/verify search functionality
- [ ] Test filter operations (by industry, concept)
- [ ] Validate pagination controls

### Database Verification

```sql
-- Check stock basic info
SELECT COUNT(*) as total_stocks
FROM stocks_basic;

-- Expected: > 3000 stocks

-- Sample data
SELECT symbol, name, industry, market
FROM stocks_basic
LIMIT 10;

-- Check by industry
SELECT industry, COUNT(*) as count
FROM stocks_basic
GROUP BY industry
ORDER BY count DESC
LIMIT 10;
```

### API Endpoint Testing

```bash
# Test 1: Get paginated stock list
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/data/stocks/basic?page=1&page_size=20" | jq '.'
```

**Expected Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "symbol": "000001",
        "name": "平安银行",
        "industry": "银行",
        "market": "深圳"
      }
      ...
    ],
    "total": 5234,
    "page": 1,
    "page_size": 20
  }
}
```

```bash
# Test 2: Search stocks
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/data/stocks/search?keyword=平安" | jq '.'
```

**Expected Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "symbol": "000001",
      "name": "平安银行",
      "match_score": 100
    }
  ]
}
```

### Frontend Integration

```javascript
// Test pagination in browser
// URL: http://localhost:3020/market-data/stocks

// 1. First page should load
// 2. Click "Next" button → Should load page 2
// 3. Search box → Type "平安" → Should filter results
// 4. Industry filter → Select "银行" → Should show only banks
```

### Performance Considerations

```sql
-- Check if pagination is efficient
EXPLAIN ANALYZE
SELECT * FROM stocks_basic
ORDER BY symbol
LIMIT 20 OFFSET 0;

-- If slow, add indexes:
CREATE INDEX IF NOT EXISTS idx_stocks_basic_symbol
ON stocks_basic(symbol);

CREATE INDEX IF NOT EXISTS idx_stocks_basic_industry
ON stocks_basic(industry);
```

---

## Phase 2.3: K-Line Data (The Big Win!)

### ⭐ Performance & Security Considerations (Gemini Review Feedback)

**Before Testing - Add Performance Guards**:

**Backend API Safety Limits**:
```python
# File: web/backend/app/api/market.py

from fastapi import Query
from datetime import datetime, timedelta

@router.get("/kline")
async def get_kline(
    symbol: str = Query(..., description="股票代码", min_length=6, max_length=6),
    period: str = Query("daily", description="周期"),
    adjust: str = Query("qfq", description="复权类型"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    limit: int = Query(1000, ge=1, le=5000, description="最大返回数据点数")
):
    """
    获取K线数据，带性能防护（防止前端卡死）
    """
    # Safety: Default date range if not specified (last 2 years)
    if not start_date:
        start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    # Safety: Enforce maximum limit
    # - Default: 1000 points (~2 years of daily data)
    # - Maximum: 5000 points (~13 years, for weekly/monthly)
    data = await fetch_kline_data(
        symbol=symbol,
        period=period,
        adjust=adjust,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )

    if len(data) > limit:
        data = data[-limit:]  # Return most recent data

    return create_success_response(data=data)
```

**Frontend Optimization**:
```typescript
// File: web/frontend/src/components/charts/KlineChart.vue

import { downsampleKlineData } from '@/utils/chart-utils'

// Chart component optimization
async function loadKlineData(params: KlineParams) {
  const response = await marketApi.getKline(params)
  let klines = response.data.klines

  // ⭐ Performance: Downsample if too many points
  if (klines.length > 2000) {
    console.warn(`Large dataset: ${klines.length} points, downsampling to 1000`)
    klines = downsampleKlineData(klines, 1000)
  }

  // Render chart with optimized data
  renderChart(klines)
}

// Downsample utility (preserve OHLC accuracy)
function downsampleKlineData(klines: KlineData[], targetSize: number): KlineData[] {
  if (klines.length <= targetSize) return klines

  const step = Math.floor(klines.length / targetSize)
  const downsampled = []

  for (let i = 0; i < klines.length; i += step) {
    const chunk = klines.slice(i, i + step)
    downsampled.push({
      date: chunk[0].date,  // First point
      open: chunk[0].open,
      high: Math.max(...chunk.map(k => k.high)),
      low: Math.min(...chunk.map(k => k.low)),
      close: chunk[chunk.length - 1].close,  // Last point
      volume: chunk.reduce((sum, k) => sum + k.volume, 0)
    })
  }

  return downsampled
}
```

### Objectives

- [ ] Verify K-line data exists for sample stocks
- [ ] Test K-line API with **performance guards**
- [ ] Verify frontend chart displays correctly with **downsampling**
- [ ] Test different periods (daily, weekly, monthly)
- [ ] Test adjust types (qfq, hfq, none)
- [ ] Verify **no timeout issues** with large datasets

### Database Verification

```sql
-- Check K-line data availability
SELECT
  symbol,
  COUNT(*) as data_points,
  MIN(date) as earliest_date,
  MAX(date) as latest_date
FROM stock_daily_klines
WHERE symbol IN ('000001', '000002', '600000')
GROUP BY symbol;

-- Expected: Each symbol has > 200 data points
-- Time range: At least 1 year of data

-- Sample K-line data
SELECT date, open, high, low, close, volume, amount
FROM stock_daily_klines
WHERE symbol = '000001'
ORDER BY date DESC
LIMIT 10;
```

**Success Criteria**:
- ✅ At least 3 stocks have K-line data
- ✅ Time span: > 200 trading days
- ✅ Data quality: OHLCV values look reasonable

### API Endpoint Testing

```bash
# Test 1: Basic K-line request
curl "http://localhost:8000/api/v1/market/kline?symbol=000001&period=daily&adjust=qfq" | jq '.'
```

**Expected Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "symbol": "000001",
    "period": "daily",
    "adjust": "qfq",
    "klines": [
      {
        "date": "2025-12-31",
        "open": 13.20,
        "high": 13.35,
        "low": 13.15,
        "close": 13.30,
        "volume": 1234567,
        "amount": 16456789.00
      }
      ...
    ]
  }
}
```

```bash
# Test 2: With date range and limit
curl "http://localhost:8000/api/v1/market/kline?symbol=000001&period=daily&start_date=2024-01-01&end_date=2025-12-31&limit=1000" | jq '.data | length'

# Expected: ~250 trading days (1 year)
# Performance: Response time < 500ms
```

```bash
# Test 3: Performance guard (no limit specified)
curl "http://localhost:8000/api/v1/market/kline?symbol=000001&period=daily" | jq '.data | length'

# Expected: Max 1000 points (default limit enforced)
# Prevents: "SELECT *" that returns 10,000+ points
```

```bash
# Test 3: Different adjust types
curl "http://localhost:8000/api/v1/market/kline?symbol=000001&period=daily&adjust=hfq" | jq '.data.klines[0]'

# Expected: Adjusted close price different from raw
```

### Frontend Integration

```javascript
// Test in browser
// URL: http://localhost:3020/market/technical-analysis

// 1. Enter stock code: 000001
// 2. Select period: Daily (default)
// 3. Click "Load Chart" button

// Expected:
// - Candlestick chart displays
// - Volume bars show at bottom
// - Can zoom in/out
// - Can crosshair to see OHLCV values
// - MA lines overlay (if configured)
```

### K-Line Chart Components

**Frontend Chart Verification**:
- [ ] Chart loads without errors
- [ ] Candlesticks display OHLC data
- [ ] Volume bars display at bottom
- [ ] X-axis shows dates
- [ ] Y-axis shows price scale
- [ ] Tooltip shows details on hover
- [ ] Zoom/pan functionality works

**Common Issues & Solutions**:

#### Issue 1: Chart doesn't display

**Check**:
```javascript
// Browser Console (F12)
// Look for:
// - "Failed to fetch" errors
// - "Cannot read property of undefined"
// - Chart library errors
```

**Verify API Response**:
```bash
# Test API directly
curl "http://localhost:8000/api/v1/market/kline?symbol=000001&period=daily" | jq '.data.klines | length'

# If 0: No data in database
# If >0: Check frontend data transformation
```

#### Issue 2: Data format mismatch

**Frontend expects** (from generated-types.ts):
```typescript
interface KlineData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
}
```

**Verify transformation**:
```typescript
// File: web/frontend/src/api/adapters/marketAdapter.ts

export function adaptKlineData(apiResponse: UnifiedResponse): KlineData[] {
  return apiResponse.data.klines.map(k => ({
    date: k.date,           // ← Check field names match
    open: Number(k.open),    // ← Check type conversion
    high: Number(k.high),
    low: Number(k.low),
    close: Number(k.close),
    volume: Number(k.volume),
    amount: Number(k.amount)
  }))
}
```

---

## Phase 2.4: Real-time Quotes (Optional)

### Objectives

- [ ] Verify real-time quote data source
- [ ] Test quote API endpoint
- [ ] Implement quote refresh mechanism
- [ ] Test WebSocket connection (if applicable)

### Database/Source Verification

```bash
# Check if real-time data source is available
# Options:
# 1. TDengine (real-time tick data)
# 2. API data source (sina/eastmoney)
# 3. Mock data for development
```

### API Testing

```bash
# Test real-time quotes
curl "http://localhost:8000/api/v1/market/quotes?symbols=000001,000002,600000" | jq '.'
```

**Expected Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "symbol": "000001",
      "name": "平安银行",
      "price": 13.30,
      "change": 0.10,
      "change_percent": 0.76,
      "volume": 1234567,
      "amount": 16456789.00,
      "timestamp": "2026-01-02T08:30:00"
    }
  ]
}
```

---

## Risk Management

### Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Database empty | Low | High | Verify data exists before API testing |
| API returns 500 | Low | Medium | Check backend logs, add error handling |
| Frontend crashes | Low | Medium | Test in browser incrementally |
| Performance issues | Medium | Medium | Add indexes, optimize queries |
| Data quality issues | Low | Low | Validate data samples before integration |

### Rollback Plan

If Phase 2 encounters critical issues:

1. **Immediate Rollback**: Switch back to Mock mode
   ```bash
   # In web/backend/.env
   USE_MOCK_DATA=true

   pm2 restart mystocks-backend
   ```

2. **Partial Rollback**: Keep working modules, rollback problematic ones
   - Example: If K-line fails, keep Industry/Concept working
   - Document what works and what doesn't

3. **Issue Escalation**: Create bug report
   ```bash
   # Use BUG登记 command
   # Document issue, attach logs, request help
   ```

---

## Success Criteria

### Phase Completion Checklist

#### Phase 2.1: Industry & Concept ✅
- [ ] API returns real industry data
- [ ] API returns real concept data
- [ ] Frontend displays industry list
- [ ] Frontend displays concept list
- [ ] Filters work correctly
- [ ] Search functionality works
- [ ] No console errors

#### Phase 2.2: Stock List ✅
- [ ] API returns paginated stock list
- [ ] Pagination controls work
- [ ] Search returns correct results
- [ ] Filters by industry work
- [ ] Filters by concept work
- [ ] Performance acceptable (< 1s per page)

#### Phase 2.3: K-Line Data ✅
- [ ] API returns K-line data for test stocks
- [ ] Chart displays correctly
- [ ] Multiple periods work (daily/weekly/monthly)
- [ ] Adjust types work (qfq/hfq/none)
- [ ] Date range filtering works
- [ ] Zoom/pan works smoothly
- [ ] No data corruption visible

#### Phase 2.4: Real-time Quotes ✅
- [ ] Quote API returns current prices
- [ ] Auto-refresh works
- [ ] Multiple stocks supported
- [ ] Performance acceptable

---

## Testing Strategy

### Unit Tests (Backend)

```python
# tests/integration/test_industry_api.py

def test_get_industries():
    """Test industry API returns real data"""
    response = client.get("/api/v1/data/stocks/industries")
    assert response.status_code == 200
    data = response.json()
    assert len(data['data']) > 50  # At least 50 industries
    assert '银行' in [i['industry_name'] for i in data['data']]

def test_get_concepts():
    """Test concept API returns real data"""
    response = client.get("/api/v1/data/stocks/concepts")
    assert response.status_code == 200
    data = response.json()
    assert len(data['data']) > 100  # At least 100 concepts
```

### Integration Tests (Frontend)

```typescript
// tests/e2e/real-data-integration.spec.ts

test('should display real industry data', async ({ page }) => {
  await page.goto('/market-data')

  // Wait for industry dropdown to populate
  await page.waitForSelector('[data-test="industry-dropdown"]')

  // Select an industry
  await page.selectOption('[data-test="industry-dropdown"]', '银行')

  // Verify stocks are filtered
  const stocks = await page.locator('[data-test="stock-list-item"]').all()
  expect(stocks.length).toBeGreaterThan(0)
})

test('should display K-line chart with real data', async ({ page }) => {
  await page.goto('/market/technical-analysis')

  // Enter stock code
  await page.fill('[data-test="stock-input"]', '000001')
  await page.click('[data-test="load-chart-button"]')

  // Wait for chart to load
  await page.waitForSelector('[data-test="kline-chart"]', { timeout: 10000 })

  // Verify chart has data
  const canvas = await page.locator('canvas')
  expect(canvas).toBeVisible()
})
```

### Manual Testing Checklist

**Browser Testing**:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)

**Functionality Testing**:
- [ ] All filters work
- [ ] Pagination works
- [ ] Search returns results
- [ ] Charts display data
- [ ] No console errors
- [ ] No network errors

---

## Documentation

### Update Documentation

After each phase, update:

1. **API Documentation**
   ```bash
   # Regenerate OpenAPI docs
   python scripts/generate_openapi.py
   ```

2. **Developer Guides**
   - Update `docs/guides/MOCK_REAL_DATA_SWITCHING_GUIDE.md`
   - Add troubleshooting sections

3. **Test Reports**
   - Document what works
   - Document what doesn't
   - Attach screenshots of working features

### Create Phase 2 Completion Report

When Phase 2 is complete:

```bash
# Create report
cat > docs/reports/PHASE_2_REAL_DATA_INTEGRATION_COMPLETION.md << EOF
# Phase 2: Real Data Integration - Completion Report

**Date**: 2026-01-XX
**Status**: ✅ Complete

## Completed Modules
- [x] Industry & Concept Lists
- [x] Stock List & Search
- [x] K-Line Data
- [x] Real-time Quotes

## Test Results
- API Tests: ✅ All passing
- Frontend Tests: ✅ All passing
- E2E Tests: ✅ All passing

## Performance Metrics
- Average response time: < 200ms
- Database query time: < 100ms
- Frontend render time: < 500ms

## Known Issues
(If any)

## Next Steps
- Phase 3: Advanced features
EOF
```

---

## Timeline Estimate

### Phase 2.1: Industry & Concept (2-3 hours)
- Database verification: 30 min
- API testing: 30 min
- Frontend integration: 1 hour
- Buffer/troubleshooting: 1 hour

### Phase 2.2: Stock List (3-4 hours)
- Database verification: 30 min
- API testing: 30 min
- Search functionality: 1 hour
- Filter operations: 1 hour
- Performance optimization: 1 hour

### Phase 2.3: K-Line Data (4-6 hours)
- Database verification: 30 min
- API testing: 30 min
- Chart integration: 2 hours
- Multiple periods/adjust types: 1 hour
- Performance optimization: 1-2 hours

### Phase 2.4: Real-time Quotes (3-4 hours)
- Data source setup: 1 hour
- API implementation: 1 hour
- Frontend refresh mechanism: 1 hour
- Testing: 1 hour

**Total: 12-17 hours** (1.5-2 work days)

---

## Conclusion

### Key Success Factors

1. **Start Simple**: Read-only modules first
2. **Verify Incrementally**: Test each step before proceeding
3. **Document Everything**: Keep records of what works
4. **Have Rollback Plan**: Know how to revert if needed

### Next Steps After Phase 2

1. ✅ **Phase 2 Complete**: All basic real data working
2. 🎯 **Phase 3**: Advanced features
   - Technical indicators
   - Backtesting with real data
   - Strategy execution
3. 📊 **Phase 4**: Optimization
   - Performance tuning
   - Caching strategies
   - Database optimization

---

**Plan Created**: 2026-01-02
**Status**: 🎯 **Ready to Execute**
**Confidence**: **High** (Low-risk, incremental approach)
**First Phase**: Industry & Concept Lists (2-3 hours)

**Your Recommendation**: ✅ **Perfect! Start with Industry & Concept, build confidence, then tackle K-Line.**

---

## Data Source Mode Clarification (⭐ Gemini Review Feedback)

### Strict Binary Switch vs Hybrid Mode

**Gemini's Recommendation**:
> "Clarify if we are supporting a mixed state (e.g., Real stock list but Mock K-lines) or if it's strictly one or the other. A strict binary switch is recommended for Phase 2 to reduce complexity."

### Decision: Strict Binary Switch ✅

**Configuration Design**:
```python
# File: web/backend/app/config.py

from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings with STRICT binary mode"""

    # ⭐ STRICT: No hybrid mode - either ALL Mock or ALL Real
    USE_MOCK_DATA: bool = Field(
        default=False,
        description=(
            "STRICT BINARY SWITCH: "
            "true = Mock mode (all endpoints return mock data) "
            "false = Real database mode (all endpoints use real data) "
            "No hybrid/mixed mode allowed in Phase 2."
        )
    )

    # Database configuration (required when USE_MOCK_DATA=false)
    POSTGRESQL_HOST: str
    POSTGRESQL_PORT: int
    POSTGRESQL_USER: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_DATABASE: str

    class Config:
        env_file = ".env"
        case_sensitive = True

# Settings instance
settings = Settings()
```

### Why Strict Binary? (Gemini's Rationale)

1. **Simpler Debugging**:
   - ✅ Problem is either "mock data wrong" OR "database/API wrong"
   - ❌ Hybrid mode: Is the bug in Mock layer OR Real layer? Harder to isolate

2. **Clear Test Coverage**:
   - ✅ Test with Mock: Fast, predictable, no database dependency
   - ✅ Test with Real: Full integration, real data scenarios
   - ❌ Hybrid: Need to test Mock→Real transitions (more test cases)

3. **Performance Predictability**:
   - ✅ Mock mode: Consistent response times
   - ✅ Real mode: Known database query patterns
   - ❌ Hybrid: Unpredictable performance (some fast, some slow)

4. **Deployment Safety**:
   - ✅ Mock for development/testing (zero database dependency)
   - ✅ Real for staging/production (full data)
   - ❌ Hybrid: Risk of deploying wrong mix to production

### Configuration Enforcement

**Environment Variable Validation**:
```python
# File: web/backend/app/main.py

from fastapi import FastAPI, HTTPException
from app.config import settings

app = FastAPI()

@app.on_event("startup")
async def validate_configuration():
    """Validate configuration BEFORE server starts"""

    # Check 1: Mock mode is explicit
    if settings.USE_MOCK_DATA is None:
        raise ValueError(
            "USE_MOCK_DATA must be explicitly set to true or false. "
            "No hybrid mode allowed."
        )

    # Check 2: Database connectivity when Real mode
    if not settings.USE_MOCK_DATA:
        try:
            # Test database connection
            conn = await get_database_connection()
            await conn.execute("SELECT 1")
            await conn.close()
            print("✅ Database connection verified")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("❌ Cannot start server in Real mode without database")
            print("💡 Set USE_MOCK_DATA=true for development without database")
            raise SystemExit(1)  # Prevent PM2 restart loop
    else:
        print("✅ Mock mode enabled - database not required")

# Startup log
print(f"🚀 Starting server in {'MOCK' if settings.USE_MOCK_DATA else 'REAL'} mode")
```

### Frontend Configuration Handling

**Frontend Must Match Backend Mode**:
```typescript
// File: web/frontend/src/config/index.ts

export const config = {
  // ⚠️ IMPORTANT: Must match backend USE_MOCK_DATA setting
  USE_MOCK_DATA: import.meta.env.VITE_USE_MOCK_DATA === 'true',

  // Validation warning in development
  validate() {
    if (import.meta.env.DEV) {
      const backendMode = this.USE_MOCK_DATA ? 'MOCK' : 'REAL'
      console.warn(`⚠️ Frontend in ${backendMode} mode`)
      console.warn(`⚠️ Backend MUST also have USE_MOCK_DATA=${this.USE_MOCK_DATA}`)
      console.warn(`⚠️ Mismatch will cause API failures!`)
    }
  }
}

// Validate on import
config.validate()
```

### Testing Both Modes

**Mock Mode Tests** (Fast, No Database):
```bash
# Set environment
export USE_MOCK_DATA=true

# Start backend
pm2 restart mystocks-backend

# Run tests
pytest tests/integration/test_industry_api.py \
  --test-mode=mock \
  -v

# Expected: All tests pass, no database dependency
# Time: < 10 seconds
```

**Real Mode Tests** (Full Integration):
```bash
# Set environment
export USE_MOCK_DATA=false
export POSTGRESQL_HOST=192.168.123.104
export POSTGRESQL_PASSWORD=<correct_password>

# Start backend
pm2 restart mystocks-backend

# Run tests
pytest tests/integration/test_industry_api.py \
  --test-mode=real \
  -v

# Expected: All tests pass with real database
# Time: ~30 seconds (database queries)
```

### Configuration Examples

**Development Mode** (Mock):
```bash
# File: web/backend/.env.development
USE_MOCK_DATA=true

# Database not required (all fields can be dummy)
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=dummy
POSTGRESQL_PASSWORD=dummy
POSTGRESQL_DATABASE=dummy
```

**Production Mode** (Real):
```bash
# File: web/backend/.env.production
USE_MOCK_DATA=false

# Real database credentials REQUIRED
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5438
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=<secure_password>
POSTGRESQL_DATABASE=mystocks
```

### Phase 2 Compliance

**For Phase 2 Implementation**:
- ✅ Use **strict binary switch** (no hybrid mode)
- ✅ Document which mode was used for testing
- ✅ Validate database connectivity before enabling Real mode
- ✅ Add startup checks to prevent PM2 restart loops
- ✅ Frontend configuration must match backend

**Success Criteria**:
- ✅ Mock mode: All tests pass in < 10 seconds
- ✅ Real mode: All tests pass with real database
- ✅ No hybrid mode: Configuration is binary (true/false only)
- ✅ Safe startup: Validates database before starting server

---

**Next Action**: Execute Phase 2.1 (Industry & Concept Lists) today! 🚀
