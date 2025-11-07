# MyStocks Web API - Quick Reference

## Key Statistics
- **FastAPI Version:** 0.104+
- **Total Router Modules:** 24
- **Service Layer Files:** 40+
- **Middleware Layers:** 3
- **Exception Handlers:** 3 (global + decorators)
- **Database Type:** PostgreSQL + TDengine (dual-database)
- **Authentication:** JWT + CSRF
- **API Documentation:** OpenAPI 3.0 (Swagger + ReDoc)

## Quick File Locations

| Purpose | File Path |
|---------|-----------|
| Main App Entry | `/app/main.py` (409 lines) |
| Response Schemas | `/app/core/response_schemas.py` |
| Exception Handlers | `/app/core/exception_handlers.py` |
| Security/Auth | `/app/core/security.py` |
| Cache Utilities | `/app/core/cache_utils.py` |
| OpenAPI Config | `/app/openapi_config.py` (400 lines) |
| API Routes | `/app/api/` (24 files) |
| Business Logic | `/app/services/` (40+ files) |
| Database Layer | `/app/core/database.py` |

## Middleware Chain (Execution Order)

1. **CORS Middleware** - Allow cross-origin requests
2. **CSRF Protection** - Verify x-csrf-token header
3. **Request Logging** - Log HTTP method, URL, client, duration

## API Endpoints Summary

| Module | Routes | Purpose |
|--------|--------|---------|
| auth.py | `/api/auth/login` | JWT authentication |
| data.py | `/api/data/stocks/*` | Stock data queries |
| market.py | `/api/market/*` | Fund flow, ETF, chip race |
| indicators.py | `/api/indicators/*` | Technical indicators (TA-Lib) |
| cache.py | `/api/cache/*` | Cache management & stats |
| system.py | `/api/system/*` | Health checks, adapters |
| strategy.py | `/api/strategy/*` | Stock strategy screening |
| monitoring.py | `/api/monitoring/*` | Real-time alerts |
| sse_endpoints.py | `/api/sse/*` | Server-Sent Events push |
| (+ 15 more) | `/api/*` | Various specializations |

## Exception Handling

**Global Handler** (`app/main.py:249`)
- Catches all unhandled exceptions → 500 error

**Decorator Handlers** (`app/core/exception_handlers.py`)
- `@handle_exceptions` - Universal handler (async/sync)
- `@handle_validation_errors` - Validation only (ValueError, KeyError)
- `@handle_database_errors` - Database errors only

## Key Classes & Functions

### Response Building
```python
from app.core.response_schemas import APIResponse

APIResponse.success(data=results)
APIResponse.error(error="BadRequest", code=400)
APIResponse.validation_error(errors=field_errors)
APIResponse.not_found(resource="User")
```

### Dependency Injection
```python
from app.core.security import get_current_user, User
from app.services.market_data_service import get_market_data_service

@router.get("/data")
async def endpoint(
    current_user: User = Depends(get_current_user),
    service = Depends(get_market_data_service)
):
    pass
```

### Caching
```python
from app.core.cache_utils import cache_response

@router.get("/fund-flow")
@cache_response("fund_flow", ttl=300)
async def get_fund_flow(...):
    pass
```

### Exception Handling
```python
from app.core.exception_handlers import handle_exceptions

@router.get("/data")
@handle_exceptions(include_traceback=False)
async def get_data():
    pass
```

## Important Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Basic health check |
| `/api/csrf-token` | GET | Get new CSRF token |
| `/api/system/health` | GET | Detailed system health |
| `/api/system/adapters/health` | GET | Adapter status |
| `/api/socketio-status` | GET | WebSocket server status |
| `/api/docs` | GET | Swagger UI documentation |
| `/api/redoc` | GET | ReDoc documentation |

## Security

### CSRF Protection
- **Endpoint:** `GET /api/csrf-token` → Returns token
- **Required Header:** `x-csrf-token`
- **Methods Protected:** POST, PUT, PATCH, DELETE
- **Expiry:** 3600 seconds (1 hour)
- **One-time Use:** Yes

### JWT Authentication
- **Token Type:** Bearer
- **Algorithm:** HS256
- **Header:** `Authorization: Bearer <token>`
- **Claims:** sub (username), user_id, role, exp

### Test Credentials
```
admin / admin123   → Role: admin
user / user123     → Role: user
```

## Database Architecture

```
PostgreSQL Database (Primary)
├── daily_kline         (TimescaleDB hypertable)
├── stock_basic         (Metadata)
├── fund_flow          (Fund statistics)
├── etf_spot           (ETF real-time)
├── chip_race          (Chip data)
├── watchlist          (User watchlists)
├── strategies         (Trading strategies)
└── ... (reference & metadata tables)

TDengine Database (Time-series)
├── tick_data          (High-frequency ticks)
└── minute_data        (Minute-level data)
```

## Router Registration Pattern

```python
# In main.py:
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(market.router, tags=["market"])  # Prefix already in router
```

## Cache Strategy

| Cache Type | TTL | Use Case |
|-----------|-----|----------|
| stocks_basic | 3600s | Stock metadata |
| daily_kline | 1800s | Daily OHLCV |
| fund_flow | 300s | Fund flow |
| etf_spot | 60s | ETF quotes |
| chip_race | 300s | Chip data |
| lhb | 86400s | Dragon-Tiger |
| financial_report | 7200s | Financial data |

## Task 11 Considerations

### Missing Gateway Features
- Route versioning (/api/v1/, /api/v2/)
- Request/response transformation
- Rate limiting
- Circuit breaking
- Request aggregation
- Request correlation ID

### Recommended Implementation
- Create `/app/gateway/` module
- Add gateway middleware to main.py
- Implement rate limiter (token bucket)
- Implement circuit breaker pattern
- Add request transformation layer
- Create gateway_config.yaml

---

**For comprehensive analysis, see: API_ARCHITECTURE_ANALYSIS.md**
