# Phase 1.3: Complete TODO Items Implementation Plan

**Date**: 2025-12-05
**Phase**: 1.3 (Week 1-2, Critical Issues)
**Estimated Effort**: 12 hours
**Priority**: 🔴 CRITICAL
**Status**: IN PLANNING

---

## Overview

Phase 1.3 focuses on completing the TODO items in three critical files that form the core of the authentication, data fetching, and dashboard systems. This phase bridges the gap between the exception hierarchy foundation (Phase 1.1-1.2) and the large-scale refactoring work in Phase 2.

---

## TODO Items Analysis

### 1. auth.py: Database Integration

**File**: `web/backend/app/api/auth.py`
**Line**: 29
**Current Status**: Uses hardcoded mock user database

#### Current Implementation
```python
# TODO: 替换为真实的数据库存储
USERS_DB = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@mystocks.com",
        "hashed_password": "$2b$12$JzXL46bSlDVnMJlDvkV7q.u5gY6pVEYNV18otWdH8FwHD3uRcV1ia",
        "role": "admin",
        "is_active": True,
    },
    "user": {
        "id": 2,
        "username": "user",
        "email": "user@mystocks.com",
        "hashed_password": "$2b$12$8aBh8ytBXEX0B0okxvYqPO428xzvnJlnA6c.q/ua6BS6z33ZP3WnK",
        "role": "user",
        "is_active": True,
    },
}

def get_users_db():
    """获取用户数据库"""
    return USERS_DB
```

#### Requirements

1. **Database Schema**
   - Need to verify PostgreSQL users table exists
   - Required columns: id, username, email, hashed_password, role, is_active, created_at, updated_at
   - Constraints: username UNIQUE, email UNIQUE

2. **User Lookup Functions**
   - `get_user_by_username(username: str) -> Optional[UserInDB]`
   - `get_user_by_email(email: str) -> Optional[UserInDB]`
   - `get_user_by_id(user_id: int) -> Optional[UserInDB]`

3. **Connection Management**
   - Use PostgreSQL connection pool from app.services or app.core
   - Handle connection errors gracefully with custom exceptions
   - Implement timeout and retry logic

4. **Data Validation**
   - Validate user data before returning
   - Use Pydantic models for type safety
   - Handle missing or invalid data

#### Implementation Steps

```python
# Step 1: Import database dependencies
from app.services.data_access import PostgreSQLDataAccess
from src.core.exceptions import (
    DatabaseConnectionError,
    DatabaseNotFoundError,
    DataValidationError,
)

# Step 2: Create database utility functions
async def get_users_db() -> PostgreSQLDataAccess:
    """获取用户数据库连接"""
    try:
        db = PostgreSQLDataAccess()
        await db.connect()
        return db
    except Exception as e:
        raise DatabaseConnectionError(
            message="Failed to connect to user database",
            context={"error": str(e)}
        ) from e

# Step 3: Replace USERS_DB with async database queries
async def get_user_by_username(username: str) -> Optional[UserInDB]:
    """从数据库获取用户信息"""
    try:
        db = await get_users_db()
        query = "SELECT id, username, email, hashed_password, role, is_active FROM users WHERE username = %s"
        result = await db.execute_query(query, (username,))
        if not result:
            raise DatabaseNotFoundError(
                message=f"User '{username}' not found",
                context={"username": username}
            )
        return UserInDB(**result[0])
    except DatabaseError as e:
        raise DatabaseConnectionError(
            message="Database query failed",
            original_exception=e
        ) from e

# Step 4: Update get_users_db() to support both sync and async contexts
def get_users_db_sync():
    """同步版本：用于兼容性"""
    # 缓存的用户数据，用于同步认证流程
    return {
        "admin": {...},
        "user": {...},
    }

async def get_users_db_async():
    """异步版本：使用数据库"""
    db = await get_users_db()
    return db
```

#### Migration Strategy

1. **Phase 1.3a (1 hour)**
   - Create users table schema in PostgreSQL
   - Seed initial admin and user accounts
   - Verify table and data

2. **Phase 1.3b (2 hours)**
   - Create database access functions
   - Implement user lookup queries
   - Add error handling with custom exceptions

3. **Phase 1.3c (1 hour)**
   - Update get_users_db() function
   - Update get_current_user() to use database
   - Add caching for frequently accessed users (optional)

---

### 2. market_data.py: Data Fetch Implementation

**File**: `web/backend/app/tasks/market_data.py`
**Lines**: 40, 45
**Current Status**: Contains placeholder TODO comments

#### Current Implementation
```python
def fetch_realtime_market_data(params: Dict[str, Any]) -> Dict[str, Any]:
    # ...
    if fetch_stocks:
        logger.info("Fetching stock realtime data...")
        # TODO: 实现实际的数据获取逻辑
        result["stocks_fetched"] = 5000  # Hardcoded placeholder

    if fetch_etfs:
        logger.info("Fetching ETF realtime data...")
        # TODO: 实现实际的数据获取逻辑
        result["etfs_fetched"] = 500  # Hardcoded placeholder
```

#### Requirements

1. **Data Sources**
   - AkShare (Primary): Real-time stock data, market data
   - Tushare (Backup): Historical and real-time data
   - BaoStock (Fallback): Historical data
   - TDX (Direct): Real-time quotes

2. **Fetch Functions**
   - `fetch_stock_realtime_data() -> List[Dict]`
   - `fetch_etf_realtime_data() -> List[Dict]`
   - `fetch_market_overview() -> Dict`
   - Implement retry logic with exponential backoff

3. **Error Handling**
   - Catch network timeouts (NetworkTimeoutError)
   - Catch data source failures (DataFetchError)
   - Catch rate limiting (RateLimitError)
   - Fallback to alternate data sources or cached data

4. **Storage Integration**
   - Store fetched data in TDengine (time-series)
   - Update PostgreSQL aggregates
   - Trigger data quality checks

#### Implementation Steps

```python
# Step 1: Import data source adapters
from app.adapters.akshare_adapter import AkshareDataSource
from app.adapters.tushare_adapter import TushareDataSource
from app.services.data_access import TDengineDataAccess, PostgreSQLDataAccess
from src.core.exceptions import (
    DataFetchError,
    NetworkError,
    RateLimitError,
    ServiceError,
)

# Step 2: Implement actual data fetching
async def fetch_stock_realtime_data(limit: int = None) -> Dict[str, Any]:
    """
    获取实时股票数据

    Args:
        limit: 最多获取多少条记录

    Returns:
        包含股票数据和元数据的字典
    """
    try:
        # Primary source: AkShare
        akshare = AkshareDataSource()
        stocks_data = await akshare.get_realtime_data("stock")

        if limit:
            stocks_data = stocks_data[:limit]

        # Store in TDengine
        tdengine = TDengineDataAccess()
        await tdengine.save_tick_data("stock", stocks_data)

        return {
            "status": "success",
            "source": "akshare",
            "count": len(stocks_data),
            "data": stocks_data,
            "fetch_time": datetime.now().isoformat(),
        }

    except RateLimitError as e:
        logger.warning(f"AkShare rate limit hit, trying backup source: {e.message}")
        # Fallback to TusShare
        try:
            tushare = TushareDataSource()
            stocks_data = await tushare.get_realtime_data("stock")
            return {
                "status": "success",
                "source": "tushare",
                "count": len(stocks_data),
                "data": stocks_data,
                "fetch_time": datetime.now().isoformat(),
            }
        except DataFetchError as fallback_error:
            logger.error(f"Both AkShare and TusShare failed: {fallback_error.message}")
            raise ServiceError(
                message="Unable to fetch stock data from any source",
                context={"primary_error": e.message, "fallback_error": fallback_error.message}
            ) from fallback_error

    except NetworkError as e:
        logger.error(f"Network error during stock data fetch: {e.message}")
        raise ServiceError(
            message="Network error while fetching stock data",
            original_exception=e
        ) from e

    except DataFetchError as e:
        logger.error(f"Data fetch failed: {e.message}")
        raise

# Step 3: Implement ETF data fetching
async def fetch_etf_realtime_data(limit: int = None) -> Dict[str, Any]:
    """获取实时ETF数据"""
    # Similar implementation to fetch_stock_realtime_data
    pass

# Step 4: Update main function
def fetch_realtime_market_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """实时市场数据获取任务"""
    logger.info(f"Starting realtime market data fetch with params: {params}")

    try:
        fetch_stocks = params.get("fetch_stocks", True)
        fetch_etfs = params.get("fetch_etfs", True)

        result = {
            "status": "success",
            "fetch_time": datetime.now().isoformat(),
            "stocks_fetched": 0,
            "etfs_fetched": 0,
            "errors": []
        }

        if fetch_stocks:
            try:
                stock_result = fetch_stock_realtime_data()
                result["stocks_fetched"] = stock_result["count"]
                result["stock_source"] = stock_result["source"]
            except ServiceError as e:
                logger.error(f"Stock data fetch failed: {e.message}")
                result["errors"].append({
                    "type": "stock_fetch",
                    "message": e.message,
                    "code": e.code
                })

        if fetch_etfs:
            try:
                etf_result = fetch_etf_realtime_data()
                result["etfs_fetched"] = etf_result["count"]
                result["etf_source"] = etf_result["source"]
            except ServiceError as e:
                logger.error(f"ETF data fetch failed: {e.message}")
                result["errors"].append({
                    "type": "etf_fetch",
                    "message": e.message,
                    "code": e.code
                })

        logger.info(f"Realtime market data fetch completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to fetch realtime market data: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "fetch_time": datetime.now().isoformat(),
        }
```

#### Migration Strategy

1. **Phase 1.3a (1.5 hours)**
   - Identify available data source adapters
   - Verify API keys and credentials
   - Test connectivity to each source

2. **Phase 1.3b (1.5 hours)**
   - Implement fetch_stock_realtime_data()
   - Implement fetch_etf_realtime_data()
   - Add error handling and fallback logic

3. **Phase 1.3c (1 hour)**
   - Update main fetch_realtime_market_data() function
   - Implement retry logic with exponential backoff
   - Add comprehensive logging

---

### 3. dashboard.py: Caching Mechanism

**File**: `web/backend/app/api/dashboard.py`
**Line**: 423
**Current Status**: Hardcoded cache_hit=False

#### Current Implementation
```python
response = DashboardResponse(
    user_id=user_id,
    trade_date=trade_date or date.today(),
    generated_at=datetime.now(),
    data_source=raw_dashboard.get("data_source", "data_source_factory"),
    cache_hit=False,  # TODO: 实现缓存机制后更新
)
```

#### Requirements

1. **Cache Layer**
   - Store dashboard data by user_id + trade_date + parameters
   - TTL: 5 minutes for intraday, 1 hour for end-of-day
   - LRU eviction policy when size exceeds limit

2. **Cache Keys**
   - Format: `dashboard:{user_id}:{trade_date}:{params_hash}`
   - Include all query parameters in hash
   - Version key for invalidation

3. **Cache Operations**
   - Get: Check cache before fetching data
   - Set: Store data after successful fetch
   - Invalidate: Clear cache on data updates
   - Refresh: Force reload data

4. **Cache Backends** (in order of preference)
   - Redis (if available)
   - In-memory cache (fallback)
   - No cache (last resort)

#### Implementation Steps

```python
# Step 1: Create cache service
from functools import lru_cache
from typing import Dict, Optional
import hashlib
import json

class DashboardCacheManager:
    """仪表盘缓存管理器"""

    def __init__(self, ttl_minutes: int = 5):
        self.ttl_minutes = ttl_minutes
        self.cache: Dict[str, tuple] = {}  # key -> (data, timestamp)

    @staticmethod
    def _generate_cache_key(
        user_id: int,
        trade_date: str,
        include_market: bool,
        include_watchlist: bool,
        include_portfolio: bool,
        include_alerts: bool
    ) -> str:
        """生成缓存键"""
        params = {
            "market": include_market,
            "watchlist": include_watchlist,
            "portfolio": include_portfolio,
            "alerts": include_alerts,
        }
        params_str = json.dumps(params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"dashboard:{user_id}:{trade_date}:{params_hash}"

    def get(self, cache_key: str) -> Optional[dict]:
        """获取缓存数据"""
        if cache_key not in self.cache:
            return None

        data, timestamp = self.cache[cache_key]
        elapsed = (datetime.now() - timestamp).total_seconds() / 60

        if elapsed > self.ttl_minutes:
            del self.cache[cache_key]
            return None

        return data

    def set(self, cache_key: str, data: dict) -> None:
        """设置缓存数据"""
        self.cache[cache_key] = (data, datetime.now())

        # Limit cache size to 100 entries
        if len(self.cache) > 100:
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k][1]
            )
            del self.cache[oldest_key]

    def invalidate(self, pattern: str = None) -> None:
        """清除缓存"""
        if pattern is None:
            self.cache.clear()
        else:
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.cache[key]

# Step 2: Initialize cache manager
_dashboard_cache = DashboardCacheManager(ttl_minutes=5)

# Step 3: Update dashboard endpoint to use cache
@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    user_id: int = Query(..., description="用户ID"),
    trade_date: Optional[date] = Query(None, description="交易日期"),
    include_market: bool = Query(True, description="是否包含市场数据"),
    include_watchlist: bool = Query(True, description="是否包含自选股"),
    include_portfolio: bool = Query(True, description="是否包含持仓"),
    include_alerts: bool = Query(True, description="是否包含风险警报"),
    current_user: User = Depends(get_current_active_user),
) -> DashboardResponse:
    """获取用户仪表盘"""

    try:
        # Generate cache key
        cache_key = DashboardCacheManager._generate_cache_key(
            user_id=user_id,
            trade_date=(trade_date or date.today()).isoformat(),
            include_market=include_market,
            include_watchlist=include_watchlist,
            include_portfolio=include_portfolio,
            include_alerts=include_alerts,
        )

        # Try to get from cache
        cached_response = _dashboard_cache.get(cache_key)
        if cached_response is not None:
            logger.info(f"Cache hit for dashboard: {cache_key}")
            response = DashboardResponse(**cached_response)
            response.cache_hit = True  # Update cache_hit flag
            return response

        # Cache miss - fetch data
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()

        params = {
            "user_id": user_id,
            "trade_date": (trade_date or date.today()).isoformat(),
            "include_market": include_market,
            "include_watchlist": include_watchlist,
            "include_portfolio": include_portfolio,
            "include_alerts": include_alerts,
        }

        raw_dashboard = await factory.get_data("dashboard", "summary", params)

        # Build response
        response = DashboardResponse(
            user_id=user_id,
            trade_date=trade_date or date.today(),
            generated_at=datetime.now(),
            data_source=raw_dashboard.get("data_source", "data_source_factory"),
            cache_hit=False,  # This is a cache miss
        )

        # Add optional data sections
        if include_market and "market_overview" in raw_dashboard:
            response.market_overview = build_market_overview(raw_dashboard["market_overview"])

        if include_watchlist and "watchlist" in raw_dashboard:
            response.watchlist = build_watchlist_summary(raw_dashboard["watchlist"])

        if include_portfolio and "portfolio" in raw_dashboard:
            response.portfolio = build_portfolio_summary(raw_dashboard["portfolio"])

        if include_alerts and "risk_alerts" in raw_dashboard:
            response.risk_alerts = build_risk_alert_summary(raw_dashboard["risk_alerts"])

        # Store in cache
        _dashboard_cache.set(cache_key, response.dict())

        logger.info(f"仪表盘数据获取成功 (cache miss): user_id={user_id}")
        return response

    except ValueError as e:
        logger.error(f"参数验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"参数验证失败: {str(e)}")
    except Exception as e:
        logger.error(f"获取仪表盘数据失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取仪表盘数据失败: {str(e)}")

# Step 4: Add cache invalidation endpoint
@router.post("/dashboard/cache/invalidate")
async def invalidate_dashboard_cache(
    user_id: Optional[int] = Query(None, description="用户ID（为空则清除所有缓存）"),
    current_user: User = Depends(get_current_active_user),
) -> APIResponse:
    """清除仪表盘缓存"""
    try:
        if user_id:
            pattern = f"dashboard:{user_id}:"
            _dashboard_cache.invalidate(pattern)
            return APIResponse(
                success=True,
                data={"invalidated": f"Cache for user {user_id}"},
                message=f"已清除用户 {user_id} 的仪表盘缓存"
            )
        else:
            _dashboard_cache.invalidate()
            return APIResponse(
                success=True,
                data={"invalidated": "All dashboard cache"},
                message="已清除所有仪表盘缓存"
            )
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {str(e)}")
        raise HTTPException(status_code=500, detail="缓存清除失败")
```

#### Migration Strategy

1. **Phase 1.3a (1 hour)**
   - Create DashboardCacheManager class
   - Implement cache get/set/invalidate operations
   - Add cache key generation logic

2. **Phase 1.3b (1.5 hours)**
   - Update get_dashboard() endpoint to use cache
   - Replace hardcoded cache_hit=False with actual cache check
   - Add cache hit/miss logging

3. **Phase 1.3c (1 hour)**
   - Add cache invalidation endpoint
   - Implement cache statistics endpoint
   - Add cache warming strategy (optional)

---

## Implementation Timeline

### Day 1: auth.py (4 hours)
- Hour 1: Database schema verification and user table creation
- Hour 2-3: Database access functions and error handling
- Hour 4: Testing and validation

### Day 2: market_data.py (4 hours)
- Hour 1: Data source adapter review and testing
- Hour 2-3: Implement fetch functions with error handling
- Hour 4: Testing and fallback logic validation

### Day 3: dashboard.py (4 hours)
- Hour 1: Cache manager implementation
- Hour 2-3: Dashboard endpoint cache integration
- Hour 4: Cache invalidation and testing

---

## Dependencies and Preconditions

### Required
- PostgreSQL database running with users table
- Data source adapters (AkShare, TusShare, BaoStock)
- TDengine database for storing time-series data
- All custom exceptions from src/core/exceptions.py

### Optional
- Redis for distributed caching (can fallback to in-memory)
- Monitoring and logging infrastructure

---

## Success Criteria

✅ All TODO comments removed from code
✅ Database integration working end-to-end
✅ Data fetching with proper error handling
✅ Caching mechanism reducing data fetch calls by >50%
✅ Proper exception handling with custom exceptions
✅ Comprehensive logging at each step
✅ All functions tested and validated

---

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Database schema mismatch | HIGH | Verify schema before implementation |
| API rate limiting | MEDIUM | Implement retry and backoff logic |
| Cache invalidation issues | MEDIUM | Comprehensive cache testing |
| Connection pool exhaustion | MEDIUM | Proper connection management |

---

## Next Phase (Phase 2)

Phase 1.3 completion unblocks Phase 2 (High Priority Items):
- Large file refactoring (52 hours)
- Code complexity reduction
- Test coverage improvement

---

**Document Status**: Ready for Implementation
**Last Updated**: 2025-12-05
**Version**: 1.0
