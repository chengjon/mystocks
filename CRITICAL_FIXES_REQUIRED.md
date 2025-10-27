# Critical Fixes Required - Code Changes

**Generated**: 2025-10-27
**Status**: Ready to Apply
**Priority**: P1 CRITICAL

---

## Fix #1: Database.py SQL Column Name Error

**File**: `/opt/claude/mystocks_spec/web/backend/app/core/database.py`
**Lines**: 173-187
**Severity**: P1 CRITICAL
**Impact**: ALL daily kline queries fail with 500 error

### Current Code (BROKEN)

```python
def query_daily_kline(
    self, symbol: str, start_date: str, end_date: str
) -> pd.DataFrame:
    """查询日线数据"""
    try:
        if postgresql_access:
            filters = {
                "symbol": symbol,
                "date >= ": start_date,    # ❌ WRONG COLUMN NAME
                "date <= ": end_date,      # ❌ WRONG COLUMN NAME
            }
            return postgresql_access.query("daily_kline", filters=filters)
        else:
            # Direct PostgreSQL query
            with get_postgresql_session() as session:
                query = text(
                    """
                    SELECT date, open, high, low, close, volume, amount
                    FROM daily_kline
                    WHERE symbol = :symbol
                    AND date >= :start_date              # ❌ WRONG COLUMN NAME
                    AND date <= :end_date                # ❌ WRONG COLUMN NAME
                    ORDER BY date                         # ❌ WRONG COLUMN NAME
                    """
                )
                result = session.execute(
                    query,
                    {
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                )
                return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        logger.error(f"Failed to query daily kline: {e}")
        return pd.DataFrame()
```

### Required Fix (CORRECT)

```python
def query_daily_kline(
    self, symbol: str, start_date: str, end_date: str
) -> pd.DataFrame:
    """查询日线数据"""
    try:
        if postgresql_access:
            filters = {
                "symbol": symbol,
                "trade_date >= ": start_date,    # ✅ FIXED: Use trade_date
                "trade_date <= ": end_date,      # ✅ FIXED: Use trade_date
            }
            return postgresql_access.query("daily_kline", filters=filters)
        else:
            # Direct PostgreSQL query
            with get_postgresql_session() as session:
                query = text(
                    """
                    SELECT trade_date, open, high, low, close, volume, amount
                    FROM daily_kline
                    WHERE symbol = :symbol
                    AND trade_date >= :start_date              # ✅ FIXED: Use trade_date
                    AND trade_date <= :end_date                # ✅ FIXED: Use trade_date
                    ORDER BY trade_date                         # ✅ FIXED: Use trade_date
                    """
                )
                result = session.execute(
                    query,
                    {
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                )
                return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        logger.error(f"Failed to query daily kline: {e}")
        return pd.DataFrame()
```

### Changes Made

| Line | Old | New |
|------|-----|-----|
| 173 | `"date >= "` | `"trade_date >= "` |
| 174 | `"date <= "` | `"trade_date <= "` |
| 182 | `SELECT date, open,` | `SELECT trade_date, open,` |
| 184 | `AND date >= :start_date` | `AND trade_date >= :start_date` |
| 185 | `AND date <= :end_date` | `AND trade_date <= :end_date` |
| 187 | `ORDER BY date` | `ORDER BY trade_date` |

### Why This Breaks

**Database Schema**:
- PostgreSQL `daily_kline` table has column: `trade_date`
- NOT: `date`

**Error Message**:
```
ERROR: column "date" does not exist
```

**HTTP Response**:
```
500 Internal Server Error
```

**Affected Users**:
- All Dashboard queries fail
- All historical data queries fail
- Wencai historical data fails

---

## Fix #2: Add Safe ISO Format Conversion

**File**: `/opt/claude/mystocks_spec/web/backend/app/tasks/wencai_tasks.py`
**Location**: Top of file (after imports)
**Severity**: P2 WARNING
**Impact**: Prevents crashes when datetime is already a string

### Add Helper Function

Add this function at the top of the file after imports:

```python
# Helper function for safe datetime conversion
def safe_isoformat(dt):
    """
    Safely convert datetime to ISO format string

    Args:
        dt: datetime object, string, or None

    Returns:
        ISO format string or None

    Examples:
        >>> safe_isoformat(datetime.now())
        '2025-10-27T10:30:45.123456'
        >>> safe_isoformat('2025-10-27T10:30:45.123456')
        '2025-10-27T10:30:45.123456'
        >>> safe_isoformat(None)
        None
    """
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    if hasattr(dt, 'isoformat') and callable(dt.isoformat):
        return dt.isoformat()
    return str(dt)
```

### Update All Uses

**Find and replace** all instances of `.isoformat()` calls:

```python
# Old pattern:
'latest_fetch': latest_fetch.isoformat() if latest_fetch else None

# New pattern:
'latest_fetch': safe_isoformat(latest_fetch)
```

**Lines to update** (run this command to find all):
```bash
grep -n "\.isoformat()" /opt/claude/mystocks_spec/web/backend/app/tasks/wencai_tasks.py
```

**Expected changes**:
- Line 392: `latest_fetch.isoformat()` → `safe_isoformat(latest_fetch)`
- Any other `.isoformat()` calls in the file

---

## Fix #3: Add Authentication Check in Dashboard.vue

**File**: `/opt/claude/mystocks_spec/web/frontend/src/views/Dashboard.vue`
**Location**: Around line 245-260 (loadDashboardData function)
**Severity**: P2 HIGH
**Impact**: Better error messages for authentication failures

### Current Code

```javascript
const loadDashboardData = async () => {
  try {
    const data = await dataApi.getDashboardSummary()

    if (data.success) {
      favoriteStocks.value = data.favorites || []
      strategyStocks.value = data.strategyStocks || []
      industryStocks.value = data.industryStocks || []

      if (data.fundFlow) {
        fundFlowData.value = data.fundFlow
      }
    }
  } catch (error) {
    console.error('Dashboard data load error:', error)
    handleApiError(error)
  }
}
```

### Required Update

```javascript
const loadDashboardData = async () => {
  // Check authentication first
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.error('请先登录 (Please log in first)')
    await router.push('/login')
    return
  }

  try {
    const data = await dataApi.getDashboardSummary()

    if (data.success) {
      favoriteStocks.value = data.favorites || []
      strategyStocks.value = data.strategyStocks || []
      industryStocks.value = data.industryStocks || []

      if (data.fundFlow) {
        fundFlowData.value = data.fundFlow
      }
    }
  } catch (error) {
    console.error('Dashboard data load error:', error)

    // Better error handling for 401
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录 (Session expired, please log in again)')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      await router.push('/login')
    } else {
      handleApiError(error)
    }
  }
}
```

### Changes Made

1. Add token check before API call
2. Add specific 401 error handling
3. Clear localStorage on authentication failure
4. Redirect to login page
5. Show user-friendly error messages

---

## Testing After Fixes

### Test 1: Database Query

```bash
# Connect to PostgreSQL and run:
psql -h localhost -U mystocks_user -d mystocks

# Test the query:
SELECT trade_date, open, high, low, close, volume, amount
FROM daily_kline
WHERE symbol = '000001'
AND trade_date >= '2025-01-01'
AND trade_date <= '2025-12-31'
ORDER BY trade_date
LIMIT 5;

# Should return data, not error
```

### Test 2: Backend API

```bash
# 1. Login to get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 2. Call Dashboard API with token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data/dashboard/summary | jq .

# Should return 200 OK with data
```

### Test 3: Frontend

```bash
# 1. Clear all caches
cd /opt/claude/mystocks_spec/web/frontend
pkill -f "vite"
rm -rf node_modules/.vite
npm install
npm run dev

# 2. Hard refresh browser (Ctrl+Shift+R)

# 3. Open DevTools (F12)

# 4. Check Console for no errors:
# - No "Can't get DOM width" errors
# - No Vue Props warnings
# - No "Not authenticated" errors

# 5. Verify Dashboard loads with data
```

### Test 4: Error Handling

```bash
# Try without token:
curl http://localhost:8000/api/data/dashboard/summary

# Should return 401 Unauthorized
# NOT 500 Internal Server Error
```

---

## Validation Checklist

After applying all fixes:

- [ ] database.py updated with trade_date (6 changes)
- [ ] wencai_tasks.py has safe_isoformat() helper
- [ ] All .isoformat() calls replaced with safe_isoformat()
- [ ] Dashboard.vue has authentication check
- [ ] Backend service starts without errors
- [ ] PostgreSQL connects successfully
- [ ] Frontend dev server starts successfully
- [ ] Browser hard refresh shows no cache
- [ ] Dashboard API returns 200 (not 500)
- [ ] Login redirects work correctly
- [ ] All charts render without DOM errors
- [ ] No Vue Props warnings in console
- [ ] No SQL column errors in backend logs

---

## Summary of Changes

### Files to Modify: 2

1. **Backend**: `/opt/claude/mystocks_spec/web/backend/app/core/database.py`
   - 6 line changes (date → trade_date)

2. **Backend**: `/opt/claude/mystocks_spec/web/backend/app/tasks/wencai_tasks.py`
   - Add safe_isoformat() function
   - Replace .isoformat() calls

3. **Frontend**: `/opt/claude/mystocks_spec/web/frontend/src/views/Dashboard.vue`
   - Add authentication check in loadDashboardData()
   - Better error handling for 401

### Total Changes: ~25 lines of code
### Estimated Time: 30 minutes
### Impact: Fixes P1 critical issues

---

## Git Commit Message

```
fix(backend): Fix critical SQL column name errors in daily kline queries

- Fix database.py: Replace 'date' with 'trade_date' (6 occurrences)
  This fixes "column 'date' does not exist" errors causing 500 responses

- Add safe_isoformat() helper in wencai_tasks.py
  Prevents crashes when datetime is already a string

- Improve authentication error handling in Dashboard.vue
  Better error messages and redirect to login on 401

Fixes: P1 API 500 errors, P2 authentication handling
```

---

**Status**: Ready to implement
**Approver**: Code Review Team
**Date**: 2025-10-27
