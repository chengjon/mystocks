# Subtask 2.2 Phase 3-4: Completion Plan

**Objective**: Complete Subtask 2.2 (Phases 3-4) - DataManager Integration + API Endpoints

**Timeline**: 4-5 hours
**Target Date**: 2025-11-06 (same session)

---

## Phase 3: DataManager Integration (2-3 hours)

### 3.1 Analyze Existing Code
- Read `web/backend/app/services/data_service.py`
- Read `web/backend/app/services/market_data_service.py`
- Understand current data fetching patterns
- Identify integration points for caching

### 3.2 Create Cache Integration Module
**File**: `web/backend/app/core/cache_integration.py`

Purpose: Utility functions for integrating cache with data services

```python
class CacheIntegration:
    """Cache integration utilities for data services"""

    @staticmethod
    def fetch_with_cache(symbol, data_type, fetch_fn, use_cache=True):
        """Cache-Aside read pattern"""
        # 1. Try cache
        # 2. If miss, fetch from source
        # 3. Write to cache
        # 4. Return data

    @staticmethod
    def save_with_cache(symbol, data_type, data, save_fn):
        """Cache-Aside write pattern"""
        # 1. Save to source
        # 2. Update cache
        # 3. Return result
```

### 3.3 Integrate CacheManager with Data Services
Modify:
- `web/backend/app/services/data_service.py`
- `web/backend/app/services/market_data_service.py`

Changes:
- Import `get_cache_manager()` and `CacheIntegration`
- Add `use_cache` parameter to fetch methods
- Implement Cache-Aside pattern in existing methods
- Add cache invalidation hooks on data updates

### 3.4 Phase 3 Testing
**File**: `web/backend/tests/test_cache_integration.py`

Test cases:
- Cache hit/miss scenarios
- Data consistency (cache vs source)
- Cache invalidation on updates
- Error handling and fallback
- Performance comparison (with/without cache)

---

## Phase 4: API Endpoints (1.5-2 hours)

### 4.1 Design Cache API Endpoints

```
GET    /api/cache/status              - Get cache statistics
GET    /api/cache/{symbol}/{type}     - Read cached data
POST   /api/cache/{symbol}/{type}     - Write/update cache
DELETE /api/cache/{symbol}             - Invalidate cache
DELETE /api/cache                      - Clear all cache
```

### 4.2 Create API Routes
**File**: `web/backend/app/api/cache.py`

Endpoints:
```python
@router.get("/cache/status")
async def get_cache_status():
    """Get cache statistics and hit rate"""

@router.get("/cache/{symbol}/{data_type}")
async def get_cached_data(symbol: str, data_type: str):
    """Retrieve cached data"""

@router.post("/cache/{symbol}/{data_type}")
async def update_cache(symbol: str, data_type: str, data: dict):
    """Update/write cache"""

@router.delete("/cache/{symbol}")
async def invalidate_symbol_cache(symbol: str):
    """Invalidate cache for symbol"""

@router.delete("/cache")
async def clear_all_cache():
    """Clear entire cache"""
```

### 4.3 Register Routes in Main App
Modify: `web/backend/app/main.py`
- Import cache router
- Register endpoints: `app.include_router(cache_router, prefix="/api")`

### 4.4 Phase 4 Testing
**File**: `web/backend/tests/test_cache_api.py`

Test cases:
- GET cache status
- GET cached data (hit/miss)
- POST cache update
- DELETE cache invalidation
- Error handling
- Authentication/authorization (if applicable)
- Performance under load

---

## Implementation Checklist

### Phase 3: DataManager Integration
- [ ] Read and analyze existing data services
- [ ] Create `cache_integration.py` utility module
- [ ] Modify `data_service.py` to use cache
- [ ] Modify `market_data_service.py` to use cache
- [ ] Create `test_cache_integration.py` with 10+ test cases
- [ ] Run and verify all tests
- [ ] Code review and formatting

### Phase 4: API Endpoints
- [ ] Create `api/cache.py` route file
- [ ] Implement 5 API endpoints
- [ ] Register routes in `main.py`
- [ ] Create `test_cache_api.py` with 10+ test cases
- [ ] Test with curl/Postman
- [ ] Performance testing
- [ ] Code review and formatting

### Final
- [ ] Run full test suite
- [ ] Verify cache hit rates
- [ ] Performance benchmarks
- [ ] Update documentation
- [ ] Git commit and push

---

## Files to Create/Modify

### New Files
1. `web/backend/app/core/cache_integration.py` (150+ lines)
2. `web/backend/tests/test_cache_integration.py` (250+ lines)
3. `web/backend/app/api/cache.py` (200+ lines)
4. `web/backend/tests/test_cache_api.py` (300+ lines)

### Modified Files
1. `web/backend/app/services/data_service.py` (+30 lines)
2. `web/backend/app/services/market_data_service.py` (+30 lines)
3. `web/backend/app/main.py` (+5 lines)
4. `web/backend/app/api/__init__.py` (if needed)

---

## Expected Outcomes

### After Phase 3:
- ✅ Data services integrated with cache
- ✅ Cache-Aside pattern implemented end-to-end
- ✅ 10+ integration tests passing
- ✅ Cache hit rates measured

### After Phase 4:
- ✅ 5 API endpoints functioning
- ✅ Full HTTP API for cache operations
- ✅ 10+ API tests passing
- ✅ Complete cache functionality available

### Final (After Both Phases):
- ✅ Subtask 2.2 100% complete
- ✅ Cache system production-ready
- ✅ 55+ total test cases (28 base + 27 integration/API)
- ✅ Full documentation
- ✅ Ready to unblock Tasks 2.3, 2.4, 5, and others

---

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Cache hit rate | ≥80% | ⏳ To measure |
| Read with cache hit | <5ms | ⏳ To verify |
| Write with cache | <10ms | ⏳ To verify |
| API response time | <100ms | ⏳ To verify |
| Batch operations | >100 ops/sec | ⏳ To verify |

---

## Success Criteria

- [x] Phase 1-2: CacheManager implementation ✅
- [ ] Phase 3: DataManager integration (starting)
- [ ] Phase 4: API endpoints (pending)
- [ ] All tests passing: 55+
- [ ] Performance targets met
- [ ] Full documentation complete
- [ ] Code review approved
- [ ] Production-ready

---

*Plan generated: 2025-11-06*
*Subtask 2.2 Target Completion: 2025-11-06 (same session)*
