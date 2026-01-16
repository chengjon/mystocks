# Quickstart Guide: Fix 5 Critical Issues

**Feature**: Fix 5 Critical Issues in OpenStock Demo
**Branch**: `001-fix-5-critical`
**Date**: 2025-10-20

## Overview

This guide helps developers set up, implement, test, and deploy fixes for 5 critical OpenStock Demo issues.

**Estimated Time**: 2-3 hours (assuming familiarity with FastAPI and Vue 3)

---

## Prerequisites

### Required Knowledge
- Python 3.12+ and FastAPI framework
- PostgreSQL database operations
- Vue 3 Composition API
- Git version control

### Required Software
- Python 3.12+ with pip
- Node.js 20+ with npm
- PostgreSQL 14+ (running on localhost:5432)
- Git
- Modern web browser (Chrome/Firefox)

### Required Access
- Database credentials (in `.env` file)
- JWT authentication token (obtain via login)

---

## Quick Setup (5 minutes)

### 1. Switch to Feature Branch

```bash
cd /opt/claude/mystocks_spec
git checkout 001-fix-5-critical

# Verify you're on the correct branch
git branch --show-current
# Expected output: 001-fix-5-critical
```

### 2. Install Dependencies (if not already installed)

**Backend**:
```bash
cd web/backend
pip install -r requirements.txt

# Verify akshare is available (from root project)
python -c "import akshare; print(akshare.__version__)"
# Expected: 1.11.0 or higher
```

**Frontend** (if needed):
```bash
cd web/frontend
npm install
```

### 3. Verify Database Connection

```bash
cd web/backend

# Check .env file contains PostgreSQL credentials
cat .env | grep POSTGRESQL
# Expected output:
# POSTGRESQL_HOST=localhost
# POSTGRESQL_PORT=5432
# POSTGRESQL_USER=mystocks
# POSTGRESQL_PASSWORD=...
# POSTGRESQL_DATABASE=mystocks

# Test connection
psql -h localhost -U mystocks -d mystocks -c "SELECT version();"
# Should show PostgreSQL version without errors
```

---

## Implementation Steps

### Phase 1: Database Migration (15 minutes)

#### Step 1.1: Create Migration Script

Create file: `web/backend/migrations/001_watchlist_tables.sql`

```sql
-- Watchlist Tables Migration
-- Version: 1.0
-- Date: 2025-01-20

BEGIN;

-- Create watchlist_groups table
CREATE TABLE IF NOT EXISTS watchlist_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sort_order INTEGER DEFAULT 0,
    stock_count INTEGER DEFAULT 0,
    UNIQUE(user_id, group_name)
);

-- Create user_watchlist table
CREATE TABLE IF NOT EXISTS user_watchlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL REFERENCES watchlist_groups(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE(user_id, group_id, stock_code)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_watchlist_groups_user
    ON watchlist_groups(user_id);

CREATE INDEX IF NOT EXISTS idx_user_watchlist_user_group
    ON user_watchlist(user_id, group_id);

CREATE INDEX IF NOT EXISTS idx_user_watchlist_stock_code
    ON user_watchlist(stock_code);

-- Create trigger function for stock_count maintenance
CREATE OR REPLACE FUNCTION update_group_stock_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE watchlist_groups
        SET stock_count = stock_count + 1
        WHERE id = NEW.group_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE watchlist_groups
        SET stock_count = stock_count - 1
        WHERE id = OLD.group_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS trg_update_stock_count ON user_watchlist;
CREATE TRIGGER trg_update_stock_count
    AFTER INSERT OR DELETE ON user_watchlist
    FOR EACH ROW
    EXECUTE FUNCTION update_group_stock_count();

-- Insert default group for existing users
INSERT INTO watchlist_groups (user_id, group_name, created_at)
SELECT id, '默认分组', CURRENT_TIMESTAMP
FROM users
WHERE NOT EXISTS (
    SELECT 1 FROM watchlist_groups
    WHERE watchlist_groups.user_id = users.id
    AND watchlist_groups.group_name = '默认分组'
);

COMMIT;
```

#### Step 1.2: Run Migration

```bash
cd /opt/claude/mystocks_spec/web/backend

# Run migration
psql -h localhost -U mystocks -d mystocks -f migrations/001_watchlist_tables.sql

# Expected output:
# BEGIN
# CREATE TABLE
# CREATE TABLE
# CREATE INDEX
# CREATE INDEX
# CREATE INDEX
# CREATE FUNCTION
# CREATE TRIGGER
# INSERT 0 1  (or more, depending on existing users)
# COMMIT
```

#### Step 1.3: Verify Tables Created

```bash
psql -h localhost -U mystocks -d mystocks -c "\dt watchlist*"

# Expected output:
#              List of relations
#  Schema |       Name        | Type  |  Owner
# --------+-------------------+-------+---------
#  public | watchlist_groups  | table | mystocks
#  public | user_watchlist    | table | mystocks

# Verify default groups created
psql -h localhost -U mystocks -d mystocks -c "SELECT user_id, group_name FROM watchlist_groups;"
# Should show "默认分组" for each existing user
```

---

### Phase 2: Backend Code Changes (30 minutes)

#### Step 2.1: Enhance Stock Code Normalization

Edit `web/backend/app/services/stock_search_service.py`:

```python
# Add this function near the top of the file
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
    import re

    # Remove whitespace
    code = code.strip().upper()

    # If already has exchange suffix, validate and return
    if re.match(r'^\d{6}\.(SH|SZ|HK)$', code):
        return code

    # Validate 6-digit code without suffix
    if not re.match(r'^\d{6}$', code):
        raise ValueError(f"Invalid stock code format: {code}. Expected 6 digits optionally followed by .SH/.SZ/.HK")

    # Auto-detect exchange for A-share
    if market in ["cn", "auto"]:
        first_digit = code[0]
        first_three = code[:3]

        # Shanghai Stock Exchange
        if first_three in ['600', '601', '603', '688']:
            return f"{code}.SH"
        elif first_digit == '6':
            return f"{code}.SH"

        # Shenzhen Stock Exchange
        elif first_three in ['000', '001', '002', '003', '300', '301']:
            return f"{code}.SZ"
        elif first_digit in ['0', '3']:
            return f"{code}.SZ"

    # H-share (Hong Kong)
    if market == "hk":
        return f"{code}.HK"

    # Default to Shanghai if ambiguous
    return f"{code}.SH"
```

Then update the `get_stock_quote()` method to use normalization:

```python
async def get_stock_quote(self, stock_code: str, market: str = "cn") -> Dict:
    """Fetch real-time quote for a stock"""
    try:
        # Normalize stock code
        normalized_code = normalize_stock_code(stock_code, market)

        # Remove exchange suffix for akshare (it expects 6 digits only)
        code_for_query = normalized_code.split('.')[0]

        # Fetch data from akshare
        df = ak.stock_zh_a_spot_em()
        quote = df[df['代码'] == code_for_query]

        if quote.empty:
            raise ValueError(f"Stock {normalized_code} not found")

        # Transform to response format
        row = quote.iloc[0]
        return {
            "symbol": normalized_code,
            "name": row.get('名称', ''),
            "current": float(row.get('最新价', 0)),
            "change": float(row.get('涨跌额', 0)),
            "change_percent": float(row.get('涨跌幅', 0)),
            "high": float(row.get('最高', 0)),
            "low": float(row.get('最低', 0)),
            "open": float(row.get('今开', 0)),
            "previous_close": float(row.get('昨收', 0)),
            "volume": int(row.get('成交量', 0)),
            "amount": float(row.get('成交额', 0)),
            "timestamp": int(datetime.now().timestamp()),
            "trading_status": "trading"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fetch quote for {stock_code}: {e}")
        raise HTTPException(status_code=500, detail="数据源暂时不可用，请稍后重试")
```

#### Step 2.2: Implement K-Line Endpoint

Edit `web/backend/app/api/market.py`, add this endpoint:

```python
@router.get("/kline")
async def get_kline(
    stock_code: str = Query(..., description="Stock code with optional exchange suffix"),
    period: str = Query("daily", description="Period: daily, weekly, monthly"),
    adjust: str = Query("qfq", description="Adjustment: qfq, hfq, or empty string"),
    start_date: str = Query(None, description="Start date YYYY-MM-DD"),
    end_date: str = Query(None, description="End date YYYY-MM-DD"),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch K-line (candlestick) data for a stock
    """
    import akshare as ak
    import asyncio
    from datetime import datetime, timedelta

    # Validate period
    if period not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid period. Supported: daily, weekly, monthly")

    # Normalize stock code
    try:
        from app.services.stock_search_service import normalize_stock_code
        normalized_code = normalize_stock_code(stock_code, "cn")
        code_for_query = normalized_code.split('.')[0]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Set default date range if not provided
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    else:
        end_date = end_date.replace('-', '')

    if not start_date:
        start_dt = datetime.now() - timedelta(days=180)  # Default 6 months
        start_date = start_dt.strftime("%Y%m%d")
    else:
        start_date = start_date.replace('-', '')

    # Fetch K-line data in thread pool (akshare is synchronous)
    def fetch_kline():
        return ak.stock_zh_a_hist(
            symbol=code_for_query,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust if adjust else ""
        )

    try:
        loop = asyncio.get_event_loop()
        df = await loop.run_in_executor(None, fetch_kline)

        if df.empty:
            raise HTTPException(status_code=404, detail=f"No K-line data found for {normalized_code}")

        # Transform to response format
        data = []
        for _, row in df.iterrows():
            data.append({
                "date": row['日期'],
                "timestamp": int(datetime.strptime(row['日期'], "%Y-%m-%d").timestamp()),
                "open": float(row['开盘']),
                "high": float(row['最高']),
                "low": float(row['最低']),
                "close": float(row['收盘']),
                "volume": int(row['成交量']),
                "amount": float(row['成交额']),
                "amplitude": float(row.get('振幅', 0)),
                "change_percent": float(row.get('涨跌幅', 0))
            })

        # Get stock name (fetch from spot data)
        spot_df = ak.stock_zh_a_spot_em()
        stock_info = spot_df[spot_df['代码'] == code_for_query]
        stock_name = stock_info.iloc[0]['名称'] if not stock_info.empty else normalized_code

        return {
            "stock_code": normalized_code,
            "stock_name": stock_name,
            "period": period,
            "adjust": adjust,
            "data": data,
            "count": len(data)
        }

    except Exception as e:
        logger.error(f"Failed to fetch K-line for {stock_code}: {e}")
        raise HTTPException(status_code=500, detail="数据源暂时不可用，请稍后重试")
```

#### Step 2.3: Verify Watchlist API Routing

Check that `web/backend/app/main.py` includes watchlist router:

```python
from app.api import watchlist

app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])
```

If missing, add it.

---

### Phase 3: Frontend Changes (20 minutes)

#### Step 3.1: Add Test Button Handlers

Edit `web/frontend/src/views/OpenStockDemo.vue`, locate the test status section and add:

```vue
<script setup>
// Add reactive state for test results
const testStatus = ref({
  search: 'pending',
  quote: 'pending',
  news: 'pending',
  watchlist: 'pending',
  kline: 'pending'
});

const testErrors = ref({});

// Add test function
const testAPI = async (apiName) => {
  testStatus.value[apiName] = 'testing';
  testErrors.value[apiName] = null;

  try {
    let result;
    const token = getToken();

    switch (apiName) {
      case 'search':
        const searchRes = await fetch(`/api/stock-search/search?q=茅台&market=cn`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        result = await searchRes.json();
        break;

      case 'quote':
        const quoteRes = await fetch(`/api/stock-search/quote/600519?market=cn`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        result = await quoteRes.json();
        break;

      case 'news':
        const newsRes = await fetch(`/api/stock-search/news/600519?market=cn`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        result = await newsRes.json();
        break;

      case 'watchlist':
        const watchlistRes = await fetch(`/api/watchlist/groups`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        result = await watchlistRes.json();
        break;

      case 'kline':
        const klineRes = await fetch(`/api/market/kline?stock_code=600519&period=daily`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        result = await klineRes.json();
        break;
    }

    testStatus.value[apiName] = result && (Array.isArray(result) ? result.length > 0 : Object.keys(result).length > 0) ? 'pass' : 'fail';
  } catch (error) {
    testStatus.value[apiName] = 'fail';
    testErrors.value[apiName] = error.message;
  }
};
</script>

<template>
  <!-- In the test status table -->
  <el-table-column label="操作" width="120">
    <template #default="scope">
      <el-button
        size="small"
        :type="testStatus[scope.row.api] === 'pass' ? 'success' : 'primary'"
        :loading="testStatus[scope.row.api] === 'testing'"
        @click="testAPI(scope.row.api)"
      >
        <span v-if="testStatus[scope.row.api] === 'pass'">✓ Pass</span>
        <span v-else-if="testStatus[scope.row.api] === 'fail'">✗ Retry</span>
        <span v-else>Test</span>
      </el-button>
    </template>
  </el-table-column>

  <el-table-column label="Status" width="100">
    <template #default="scope">
      <el-tag
        :type="testStatus[scope.row.api] === 'pass' ? 'success' : testStatus[scope.row.api] === 'fail' ? 'danger' : 'info'"
      >
        {{ testStatus[scope.row.api] }}
      </el-tag>
    </template>
  </el-table-column>
</template>
```

---

## Testing (30 minutes)

### Manual Testing Checklist

#### Test 1: Database Tables
```bash
# Verify tables exist
psql -h localhost -U mystocks -d mystocks -c "\dt watchlist*"

# Check default groups
psql -h localhost -U mystocks -d mystocks -c "SELECT * FROM watchlist_groups;"
```
✅ Expected: Two tables listed, default groups present

#### Test 2: Watchlist Group Management
1. Login to frontend: http://localhost:3000/login
2. Navigate to: http://localhost:3000/openstock-demo
3. Click "自选股管理" tab
4. Click "新建分组"
5. Enter name "测试分组", click OK
6. ✅ Expected: New group appears in list, stock_count = 0

#### Test 3: Add Stock to Watchlist
1. In "股票搜索" tab, search for "茅台"
2. Click "加入自选" on first result
3. Select group "测试分组"
4. ✅ Expected: Success message, stock appears in group

#### Test 4: Real-Time Quote with Auto-Detection
```bash
# Test without suffix (should auto-detect)
curl -X GET "http://localhost:8000/api/stock-search/quote/300892?market=cn" \
  -H "Authorization: Bearer <YOUR_TOKEN>"

# ✅ Expected: 200 OK with symbol="300892.SZ"
```

#### Test 5: K-Line Chart
1. In frontend, click "K线图表" tab
2. Enter stock code "600519"
3. Click "加载图表"
4. ✅ Expected: Chart displays with candlesticks and volume bars

#### Test 6: Test Buttons
1. Click "测试状态" tab
2. Click "Test" button for each API
3. ✅ Expected: All tests show "✓ Pass" status

### Automated Testing

Run backend tests:
```bash
cd /opt/claude/mystocks_spec/web/backend
pytest tests/test_watchlist_api.py -v
pytest tests/test_stock_search.py -v
pytest tests/test_market_api.py -v
```

---

## Troubleshooting

### Issue: Migration fails with "relation already exists"

**Solution**: Tables already created. Verify with `\dt watchlist*` in psql. If structure is correct, proceed.

### Issue: "未找到股票报价" for valid stock code

**Cause**: AKShare data not available or stock code invalid

**Solution**:
1. Verify stock code exists on exchange
2. Try with explicit suffix (e.g., "600519.SH")
3. Check akshare status: `python -c "import akshare as ak; print(ak.stock_zh_a_spot_em().head())"`

### Issue: K-line endpoint returns 404

**Cause**: Endpoint not registered in FastAPI router

**Solution**: Verify `app/api/market.py` is imported in `main.py` and router is included

### Issue: Frontend test buttons not working

**Cause**: Token expired or not logged in

**Solution**:
1. Check browser console for errors
2. Verify token in localStorage: `localStorage.getItem('token')`
3. Re-login if token missing

---

## Deployment Checklist

Before merging to main:

- [ ] All database migrations run successfully
- [ ] Backend tests pass (watchlist, quote, kline)
- [ ] Frontend manual tests complete
- [ ] No console errors in browser
- [ ] All 5 test buttons show "Pass"
- [ ] Code reviewed by team member
- [ ] Documentation updated (if needed)

---

## Next Steps

After completing this quickstart:

1. Run `/speckit.tasks` to generate implementation tasks
2. Execute tasks in priority order (P0 first)
3. Create pull request when all tasks complete
4. Deploy to production after approval

---

## Support

For issues:
- **Database**: Check PostgreSQL logs, verify credentials
- **Backend**: Check uvicorn logs (`/opt/claude/mystocks_spec/web/backend`)
- **Frontend**: Check browser console, network tab
- **AKShare**: Check library status and version

**Time to Complete**: Approximately 2-3 hours for full implementation and testing.
