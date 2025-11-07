# MyStocks Web API - Architecture Analysis
## Current API Structure and Considerations for Task 11: API Gateway and Request Routing

**Analysis Date:** 2025-11-07  
**Backend Location:** `/opt/claude/mystocks_spec/web/backend`  
**Analysis Focus:** FastAPI setup, middleware chain, route organization, error handling

---

## Executive Summary

The MyStocks Web API is a comprehensive FastAPI-based system with:
- **24 API endpoints** organized across 24 router modules
- **3-layer middleware** for security, logging, and CSRF protection
- **Standardized error handling** with decorator patterns
- **Unified response formatting** across all endpoints
- **Service layer architecture** with 40+ business logic services

### Key Finding
The application is currently using **direct router inclusion** without an API Gateway layer. This is suitable for monolithic deployments but Task 11 should add gateway capabilities for:
- Route aggregation and versioning
- Request/response transformation
- Load balancing and circuit breaking
- API composition and microservice orchestration

---

## 1. FastAPI Application Structure

### Entry Point: `/app/main.py`

**File Size:** ~409 lines  
**Created:** Enhanced OpenAPI configuration  
**Lifespan Management:** Yes (startup/shutdown hooks)

```python
# Application initialization with context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: PostgreSQL, cache scheduler, Socket.IO
    # Shutdown: Cleanup, connection closure
    yield
    
# FastAPI app with enhanced OpenAPI config
app = FastAPI(
    title="MyStocks Web API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)
```

**Configuration Details:**
- **Title:** MyStocks Web API
- **Version:** 2.0.0
- **Documentation:** OpenAPI 3.0 compliant
- **Database:** PostgreSQL-only (Week 3 simplification, TDengine for time-series)
- **Authentication:** JWT + CSRF protection

---

## 2. Current Middleware Chain (3 Layers)

### Layer 1: CORS Middleware (First)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Purpose:** Enable cross-origin requests from development frontend servers

### Layer 2: CSRF Protection Middleware (Line 176)
```python
@app.middleware("http")
async def csrf_protection_middleware(request: Request, call_next):
    """Verify CSRF tokens for state-changing operations"""
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        exclude_paths = ["/api/csrf-token"]
        csrf_token = request.headers.get("x-csrf-token")
        
        if not csrf_token or not csrf_manager.validate_token(csrf_token):
            return JSONResponse(
                status_code=403,
                content={"error": "CSRF token missing or invalid"}
            )
    return await call_next(request)
```

**Security Mechanism:**
- Token generation: `csrf_manager.generate_token()` 
- Validation: One-time use + 3600s TTL
- Storage: In-memory (should use Redis in production)
- Exclusion: GET, HEAD, OPTIONS operations

### Layer 3: Request/Response Logging Middleware (Line 221)
```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with performance metrics"""
    start_time = time.time()
    
    logger.info(
        "HTTP request started",
        method=request.method,
        url=str(request.url),
        client_host=request.client.host,
    )
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        "HTTP request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=round(process_time, 3),
    )
    return response
```

**Metrics Captured:**
- Request method, URL, client IP
- Response status code
- Processing time (milliseconds)

---

## 3. Global Exception Handling

### Location: `app/main.py` (Line 249)

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions"""
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": str(id(request)),
        },
    )
```

### Specialized Exception Decorators: `/app/core/exception_handlers.py`

#### 1. **@handle_exceptions** (Lines 43-206)
Universal exception handler for both async and sync functions

```python
@handle_exceptions(include_traceback=False, default_status=500)
async def my_endpoint():
    return await fetch_data()
```

**Handles:**
- `HTTPException` → Re-raises to preserve status codes
- `ValueError` → 400 Validation Error
- `KeyError` → 400 Missing Required Parameter
- `PermissionError` → 403 Permission Denied
- `Exception` → 500 Internal Server Error

#### 2. **@handle_validation_errors** (Lines 209-250)
Specialized for validation-heavy endpoints

**Catches:**
- ValueError, KeyError → 400
- Other exceptions → Logged as warnings, re-raised

#### 3. **@handle_database_errors** (Lines 253-311)
Specialized for database operations

**Catches Database Keywords:**
- "database", "connection", "query", "sql" → 503 Service Unavailable
- Other errors → Re-raised

---

## 4. Route Organization (24 API Modules)

### Directory Structure
```
/app/api/
├── auth.py                    # Authentication (JWT, login)
├── data.py                    # Stock data queries
├── system.py                  # System health, adapters
├── indicators.py              # Technical indicators (TA-Lib)
├── market.py                  # Market data (fund flow, ETF, chip race)
├── market_v2.py              # East Money direct API
├── tdx.py                     # Tencent data integration
├── metrics.py                 # Prometheus metrics
├── cache.py                   # Cache management & monitoring
├── tasks.py                   # Task management
├── wencai.py                  # Wencai stock screening
├── stock_search.py            # Stock search & filtering
├── watchlist.py              # Watchlist management
├── tradingview.py            # TradingView widgets
├── notification.py            # Email notifications
├── ml.py                      # ML predictions
├── strategy.py                # Strategy screening
├── monitoring.py              # Real-time monitoring
├── technical_analysis.py      # Enhanced technical analysis
├── multi_source.py            # Multi-source data management
├── announcement.py            # Announcement monitoring
├── strategy_management.py     # Strategy CRUD ops
├── risk_management.py         # Risk management
└── sse_endpoints.py           # Server-Sent Events (real-time push)
```

### Router Registration Pattern (Lines 342-401)

```python
# 24 include_router calls with various prefix patterns

# Pattern 1: With custom prefix
app.include_router(
    data.router, 
    prefix="/api/data", 
    tags=["data"]
)

# Pattern 2: Prefix already included in router
app.include_router(
    market.router,  # Already has "/api/market" prefix
    tags=["market"]
)

# Pattern 3: Custom prefix for specific modules
app.include_router(
    indicators.router, 
    prefix="/api/indicators", 
    tags=["indicators"]
)
```

### API Endpoint Examples

#### Example 1: Market Data Routes (`/app/api/market.py`)
```python
router = APIRouter(prefix="/api/market", tags=["市场数据"])

@router.get("/fund-flow", response_model=List[FundFlowResponse])
@cache_response("fund_flow", ttl=300)
async def get_fund_flow(
    symbol: str = Query(...),
    timeframe: str = Query(default="1"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: MarketDataService = Depends(get_market_data_service)
):
    """Query fund flow with 5-minute cache"""
    results = service.query_fund_flow(symbol, timeframe, start_date, end_date)
    return [FundFlowResponse.model_validate(r) for r in results]
```

#### Example 2: Authentication Routes (`/app/api/auth.py`)
```python
@router.post("/login", response_model=Token)
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...)
) -> Dict[str, Any]:
    """User login endpoint with JWT token generation"""
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Generate JWT token...
```

---

## 5. Request/Response Handling Patterns

### A. Standardized Response Schemas (`/app/core/response_schemas.py`)

**Purpose:** Eliminate 80+ lines of duplicate response formatting across endpoints

#### APIResponse Builder Class
```python
class APIResponse:
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation successful",
        code: int = 200,
    ) -> Dict[str, Any]:
        return {
            "status": "success",
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def error(
        error: str,
        message: str = "An error occurred",
        code: int = 500,
        details: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        return {
            "status": "error",
            "code": code,
            "error": error,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
        }

    @staticmethod
    def validation_error(
        message: str = "Validation failed",
        errors: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        # Returns 400 error with field-level validation details
        
    @staticmethod
    def not_found(
        resource: str = "Resource",
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Returns 404 error with resource info
```

**Usage Examples:**
```python
# Successful response
return APIResponse.success(data=results, message="Data retrieved")

# Error response
return APIResponse.error(error="Invalid Input", code=400)

# Validation error
return APIResponse.validation_error(
    message="Input validation failed",
    errors={"symbol": "Invalid stock code"}
)

# Not found
return APIResponse.not_found(resource="User", message="User ID 123 not found")
```

### B. Dependency Injection Pattern

**Service Injection:**
```python
from app.services.market_data_service import get_market_data_service

@router.get("/fund-flow")
async def get_fund_flow(
    service: MarketDataService = Depends(get_market_data_service)
):
    """Service injected via Depends()"""
    return service.query_fund_flow(...)

# Service factory function
def get_market_data_service() -> MarketDataService:
    return MarketDataService(db_service=get_db_service())
```

**Authentication Injection:**
```python
from app.core.security import get_current_user, User

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    """User automatically verified before execution"""
    return {"user": current_user.username}
```

### C. Caching Decorator Pattern

**Location:** `/app/core/cache_utils.py` (Lines 120+)

```python
@cache_response(cache_type: str, ttl: Optional[int] = None, skip_cache: bool = False)
async def endpoint():
    """Automatically cache response based on query parameters"""
    pass

# Usage examples:
@router.get("/fund-flow")
@cache_response("fund_flow", ttl=300)  # 5-minute cache
async def get_fund_flow(...):
    ...

@router.get("/etf/list")
@cache_response("etf_spot", ttl=60)    # 1-minute cache
async def get_etf_list(...):
    ...

@router.get("/lhb")
@cache_response("lhb", ttl=86400)      # 24-hour cache
async def get_lhb_data(...):
    ...
```

**CacheManager Strategy Presets:**
| Cache Type | TTL | Use Case |
|-----------|-----|----------|
| stocks_basic | 3600s | Stock metadata |
| daily_kline | 1800s | Daily OHLCV data |
| fund_flow | 300s | Intraday fund flow |
| etf_spot | 60s | Real-time ETF prices |
| chip_race | 300s | Chip trading data |
| lhb | 86400s | Dragon-Tiger board |
| wencai_results | 1800s | Stock screening |
| real_time_quotes | 10s | Real-time quotes |
| financial_report | 7200s | Financial statements |

### D. Query Parameter Validation

**Pydantic Integration:**
```python
@router.get("/stocks/daily")
async def get_daily_kline(
    symbol: str = Query(..., description="Stock code, e.g., 000001.SZ"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=5000, description="Result limit"),
):
    """
    ge=1, le=5000: Range validation
    ...: Required field
    None: Optional field
    description: OpenAPI documentation
    """
```

---

## 6. Service Layer Architecture (40+ Services)

### Services Directory: `/app/services/`

| Service | Purpose | Lines |
|---------|---------|-------|
| data_service.py | Data querying & integration | 16.7k |
| market_data_service.py | Market data operations | 31.4k |
| market_data_service_v2.py | East Money API | 22.3k |
| indicator_registry.py | TA-Lib indicators metadata | 21.2k |
| technical_analysis_service.py | Technical indicators | 22.1k |
| watchlist_service.py | Watchlist CRUD | 25.3k |
| strategy_service.py | Strategy management | 14.8k |
| monitoring_service.py | Real-time monitoring | 24.9k |
| task_manager.py | Async task execution | 13.2k |
| stock_search_service.py | Stock search & filtering | 28.6k |
| email_service.py | Email notifications | 12.5k |
| filter_service.py | Advanced filtering | 17.5k |
| room_socketio_adapter.py | Socket.IO integration | 17.4k |
| room_management.py | Room lifecycle mgmt | 10.8k |
| subscription_storage.py | Subscription persistence | 16.9k |

---

## 7. Database Layer Integration

### Current Architecture: Dual-Database (Week 3)

```
MyStocksUnifiedManager (Unified Entry Point)
├── TDengineDataAccess (High-frequency time-series)
│   └── market_data DB (tick_data, minute_data supertables)
│
└── PostgreSQLDataAccess (All other data + TimescaleDB)
    └── mystocks DB (daily_kline, reference data, metadata)
```

### Database Connection Management (`/app/core/database.py`)

```python
# Connection pooling via SQLAlchemy
engine = get_postgresql_engine()  # With connection pooling

# Lifespan hook verifies connectivity
with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    logger.info("Database verified", version=result.fetchone()[0])
```

---

## 8. OpenAPI/Swagger Configuration

### Location: `/app/openapi_config.py` (~400 lines)

**Features:**
- 15+ API tag definitions with descriptions
- Common response examples
- Security scheme definitions
- Custom Swagger UI parameters

**API Tags Defined:**
```python
OPENAPI_TAGS = [
    {"name": "auth", "description": "Authentication & authorization"},
    {"name": "data", "description": "Stock data queries"},
    {"name": "market", "description": "Market data & real-time quotes"},
    {"name": "indicators", "description": "Technical analysis indicators"},
    {"name": "machine-learning", "description": "ML models & predictions"},
    # ... 10 more tags
]
```

---

## 9. Security Implementation

### CSRF Protection
- **Token Management:** `/app/main.py` lines 37-80
- **Middleware:** `/app/main.py` lines 176-217
- **Endpoint:** `/api/csrf-token` (GET) - Generate new token
- **Validation:** Required header `x-csrf-token` for PUT/POST/PATCH/DELETE
- **Expiry:** 3600 seconds (1 hour)
- **One-time Use:** Tokens marked as used after validation

### JWT Authentication
- **Library:** PyJWT
- **Algorithm:** HS256 (configurable)
- **Location:** `/app/core/security.py`
- **Token Structure:** 
  ```python
  {
    "sub": username,
    "user_id": 1,
    "role": "admin|user",
    "exp": expiration_timestamp
  }
  ```
- **Extraction:** Bearer token from `Authorization` header
- **Dependency Injection:** `get_current_user()` dependency

### Built-in Users (Test)
```python
USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@mystocks.com",
        "role": "admin",
        "hashed_password": "$2b$12$JzXL46..."  # admin123
    },
    "user": {
        "username": "user",
        "email": "user@mystocks.com",
        "role": "user",
        "hashed_password": "$2b$12$8aBh8y..."  # user123
    }
}
```

---

## 10. Health Check & Status Endpoints

### 1. Basic Health Check
```
GET /health
Response:
{
    "status": "healthy",
    "timestamp": 1698888000.123,
    "service": "mystocks-web-api"
}
```

### 2. System Health Details
```
GET /api/system/health
Response:
{
    "status": "healthy",
    "timestamp": "2025-11-07T...",
    "databases": {
        "mysql": "healthy",
        "postgresql": "healthy",
        "tdengine": "unknown",
        "redis": "healthy"
    },
    "service": "mystocks-web-api",
    "version": "2.1.0"
}
```

### 3. Adapter Health
```
GET /api/system/adapters/health
Response:
{
    "akshare": {
        "status": "healthy",
        "last_check": "2025-11-07T..."
    },
    "tdx": {
        "status": "healthy",
        "last_check": "2025-11-07T..."
    },
    "financial": {
        "status": "healthy",
        "last_check": "2025-11-07T..."
    }
}
```

### 4. Socket.IO Status
```
GET /api/socketio-status
Response:
{
    "status": "active",
    "service": "Socket.IO",
    "statistics": {
        "connected_clients": 42,
        "active_rooms": 15,
        "messages_sent": 1250,
        "messages_received": 3421
    },
    "timestamp": 1698888000.123
}
```

---

## 11. Current Limitations & Gaps

### What's Missing for Task 11: API Gateway

| Requirement | Current State | Needed for Gateway |
|-------------|--------------|-------------------|
| **Request routing** | Direct router inclusion | Smart routing rules (versioning, path rewriting) |
| **Route versioning** | No versioning (v1 implicit) | /api/v1/, /api/v2/ support |
| **Request transformation** | Per-endpoint | Centralized request/response transformation |
| **Rate limiting** | None implemented | Token bucket or sliding window |
| **Circuit breaking** | None | Fail gracefully with fallback responses |
| **Request aggregation** | None | Combine multiple endpoint calls |
| **Load balancing** | None (single instance) | Round-robin or weighted balancing |
| **API composition** | Static routes | Dynamic route composition |
| **Request correlation** | request_id in errors | Global correlation ID header |
| **Service discovery** | Hardcoded services | Dynamic service registration |

### Current Strengths to Preserve

✅ Excellent middleware chain (CORS, CSRF, logging)  
✅ Unified exception handling (decorators)  
✅ Standardized response formatting  
✅ Service layer abstraction  
✅ Comprehensive OpenAPI documentation  
✅ JWT + CSRF security  
✅ Dependency injection pattern  
✅ Built-in caching strategy  

---

## 12. Recommendations for Task 11: API Gateway Implementation

### Architecture Options

#### Option A: FastAPI Middleware-Based Gateway (Recommended)
```python
# Create /app/gateway/request_router.py
class APIGateway:
    """FastAPI middleware-based API gateway"""
    
    def __init__(self):
        self.routes_config = {}  # Load from YAML
        self.transformers = {}    # Request/response transformers
        self.rate_limiter = RateLimiter()
        self.circuit_breakers = {}
    
    async def route_request(self, request: Request):
        """Central routing logic"""
        # 1. Extract version from path or header
        # 2. Validate rate limits
        # 3. Apply request transformation
        # 4. Route to appropriate backend service
        # 5. Apply response transformation
        # 6. Return response
```

#### Option B: Separate Gateway Service (Kong, AWS API Gateway)
- Deploy gateway layer separately
- Proxy to FastAPI backend
- Requires Docker orchestration

### Recommended Implementation Steps

1. **Create Gateway Module** (`/app/gateway/`)
   - `request_router.py` - Routing logic
   - `request_transformer.py` - Request/response transformation
   - `rate_limiter.py` - Token bucket implementation
   - `circuit_breaker.py` - Fail-safe circuit breaking
   - `gateway_config.yaml` - Route definitions

2. **Add Gateway Middleware** (in `main.py`)
   ```python
   @app.middleware("http")
   async def gateway_middleware(request: Request, call_next):
       # Apply gateway logic before route handling
       pass
   ```

3. **Route Configuration Schema**
   ```yaml
   routes:
     - path: "/api/v1/data/*"
       upstream: "/api/data"
       version: "1.0"
       rate_limit: 100/minute
       timeout: 30s
       
     - path: "/api/v2/data/*"
       upstream: "/api/data"
       version: "2.0"
       transformers:
         - snake_case_to_camelCase
       rate_limit: 500/minute
   ```

4. **Request Correlation**
   ```python
   # Add X-Request-ID header handling
   @app.middleware("http")
   async def correlation_middleware(request: Request, call_next):
       request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
       # Pass through entire request chain
   ```

5. **Testing**
   - Add tests for route resolution
   - Test rate limiting
   - Test request/response transformation
   - Test circuit breaking

---

## Appendix A: Complete Router Import List

```python
from app.api import (
    data,                    # /api/data - Stock data queries
    auth,                    # /api/auth - Authentication
    system,                  # /api/system - System management
    indicators,              # /api/indicators - Technical indicators
    market,                  # /api/market - Market data
    tdx,                     # /api/tdx - Tencent data
    metrics,                 # /api/metrics - Prometheus
    tasks,                   # /api/tasks - Task management
    wencai,                  # /api/market/wencai - Stock screening
    stock_search,            # /api/stock-search - Search
    watchlist,               # /api/watchlist - Watchlist
    tradingview,             # /api/tradingview - TradingView
    notification,            # /api/notification - Emails
    ml,                      # /api/ml - Machine learning
    market_v2,               # /api/market-v2 - East Money API
    strategy,                # /api/strategy - Strategy screening
    monitoring,              # /api/monitoring - Real-time monitoring
    technical_analysis,      # /api/technical-analysis - Analysis
    multi_source,            # /api/multi-source - Data sources
    announcement,            # /api/announcement - Announcements
    strategy_management,     # /api/strategy-mgmt - Strategy CRUD
    risk_management,         # /api/risk-mgmt - Risk management
    sse_endpoints,           # /api/sse - Server-Sent Events
    cache,                   # /api/cache - Cache management
)
```

---

## Appendix B: Database Tables Schema References

### PostgreSQL Tables (via MyStocksUnifiedManager)
- **daily_kline** - Daily OHLCV data (TimescaleDB hypertable)
- **stock_basic** - Stock metadata
- **fund_flow** - Fund flow statistics
- **etf_spot** - ETF real-time data
- **chip_race** - Chip trading data
- **lhb** (龙虎榜) - Dragon-Tiger board
- **financial_reports** - Financial statements
- **watchlist** - User watchlists
- **strategies** - Trading strategies
- **monitoring_alerts** - Monitoring alerts

### TDengine Tables (Supertables)
- **tick_data** - Tick-level market data (high-frequency)
- **minute_data** - Minute-level market data (high-frequency)

---

**End of Analysis**

