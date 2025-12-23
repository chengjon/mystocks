# Code Consolidation Implementation Guide
## MyStocks Web Backend - Refactoring Strategy

---

## PHASE 1: QUICK WINS (Week 1-2)

### Task 1.1: Centralized Database Factory

**Create:** `/app/core/database_factory.py`

**Purpose:** Replace duplicated database connection code across 9+ services

**Current Duplication Locations:**
- `market_data_service.py` lines 32-56
- `market_data_service_v2.py` lines 31-48
- `watchlist_service.py` (repeated pattern)
- `announcement_service.py`
- `wencai_service.py`
- `monitoring_service.py`

**Implementation:**
```python
# New centralized factory
class DatabaseFactory:
    _engines = {}
    _sessions = {}

    @classmethod
    def get_postgresql_engine(cls):
        """Singleton pattern for PostgreSQL engine"""

    @classmethod
    def get_postgresql_session(cls):
        """Get or create session"""

    @classmethod
    def build_connection_url(cls, **override_params):
        """Build connection string with env vars"""
```

**Impact:**
- Reduces 150+ lines of duplication
- Centralizes connection pooling configuration
- Improves maintainability of database setup

**Files to Modify:**
- Create: `app/core/database_factory.py` (40 lines)
- Update: 9+ service files (remove __init__ duplications)

---

### Task 1.2: Service Factory Pattern

**Create:** `/app/core/service_factory.py`

**Purpose:** Replace 8+ instances of singleton service initialization

**Current Duplication Locations:**
- market_data_service.py: `_market_data_service = None; get_market_data_service()`
- email_notification_service.py: `_email_service = None; get_email_service()`
- watchlist_service.py, strategy_service.py, etc. (7 more)

**Implementation:**
```python
# Generic factory
class ServiceFactory:
    _instances = {}

    @classmethod
    def get_service(cls, service_class: Type[T]) -> T:
        """Generic singleton getter"""
        key = service_class.__name__
        if key not in cls._instances:
            cls._instances[key] = service_class()
        return cls._instances[key]

    @classmethod
    def reset_service(cls, service_class: Type[T]):
        """Reset singleton for testing"""
```

**Impact:**
- Reduces 80+ lines of duplication
- Standardizes service initialization
- Improves testability

**Files to Modify:**
- Create: `app/core/service_factory.py` (30 lines)
- Update: 8 service files (simplify get_* functions)

---

### Task 1.3: Environment Configuration Consolidation

**Extend:** `/app/core/config.py`

**Purpose:** Centralize all environment variable reading

**Current Duplication Locations:**
```python
# SMTP Config (2 locations)
- email_service.py
- email_notification_service.py

# PostgreSQL Config (9+ locations)
- market_data_service.py
- market_data_service_v2.py
- watchlist_service.py
- announcement_service.py
- etc.

# TQLEX Config
- tqlex_adapter.py
```

**Implementation:**
Add to `Settings` class in `config.py`:
```python
class Settings(BaseSettings):
    # SMTP Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True

    # TQLEX Configuration
    tqlex_token: Optional[str] = None
```

**Impact:**
- Reduces 120+ lines of duplication
- Centralized configuration management
- Easier environment variable updates

**Files to Modify:**
- Update: `app/core/config.py` (add 20 new settings)
- Update: 6+ service/adapter files (use config instead of os.getenv)

---

## PHASE 2: MEDIUM EFFORT (Week 3-4)

### Task 2.1: Merge Market Data Services

**Issue:** Two nearly identical services with different adapters
- `market_data_service.py` (uses Akshare)
- `market_data_service_v2.py` (uses EastMoney)

**Current Duplication:**
- `fetch_and_save_fund_flow()` - 60+ LOC each, 90% identical
- `query_fund_flow()` - similar
- `_build_db_url()` - identical
- Engine/session initialization - identical

**Strategy:**
1. Create unified `MarketDataService` with pluggable adapter
2. Move adapter-specific logic to adapter layer
3. Keep data layer logic in service

**Implementation:**
```python
# New unified service
class MarketDataService:
    def __init__(self, adapter_name: str = 'eastmoney'):
        self.adapter = self._load_adapter(adapter_name)
        self.db = DatabaseFactory.get_postgresql_session()

    def _load_adapter(self, name: str):
        if name == 'akshare':
            return get_akshare_extension()
        elif name == 'eastmoney':
            return get_eastmoney_adapter()
        else:
            raise ValueError(f"Unknown adapter: {name}")

    def fetch_and_save_fund_flow(self, symbol=None, timeframe="今日"):
        # Unified implementation
        data = self.adapter.get_stock_fund_flow(symbol, timeframe)
        # ... common database logic
```

**Impact:**
- Reduces 300+ lines of duplication
- Maintains dual-adapter capability
- Easier to add new adapters

**Files to Modify:**
- Merge: `market_data_service.py` + `market_data_service_v2.py` → single file
- Keep both: `eastmoney_adapter.py` and `akshare_extension.py`
- Update: API endpoints to use merged service

**Testing Considerations:**
- Create tests for both adapter paths
- Ensure backward compatibility with existing API calls

---

### Task 2.2: Consolidate Email Services

**Issue:** Two email services with overlapping functionality
- `email_service.py`
- `email_notification_service.py`

**Current Duplication:**
- SMTP configuration reading (repeated)
- send() method (90% identical)
- Error handling (identical patterns)
- try/except blocks (repeated)

**Strategy:**
1. Keep `EmailService` as core implementation
2. Convert `EmailNotificationService` to facade/configuration wrapper
3. Consolidate SMTP configuration to config.py

**Implementation:**
```python
# Unified EmailService
class EmailService:
    def __init__(self, config: Optional[EmailConfig] = None):
        # Use config.py or provided config
        self.config = config or EmailConfig.from_settings(settings)
        self.smtp_client = self._create_smtp_client()

    def send(self, to: str, subject: str, body: str) -> bool:
        """Unified send implementation"""
```

**Impact:**
- Reduces 150+ lines of duplication
- Simplifies email functionality
- Easier to test and maintain

**Files to Modify:**
- Consolidate: `email_service.py` + `email_notification_service.py`
- Delete: `email_notification_service.py` (or convert to thin wrapper)
- Update: API endpoints using email service
- Extend: `app/core/config.py` with email config

---

### Task 2.3: Unified Exception Handlers

**Create:** `/app/core/exception_handlers.py`

**Purpose:** Replace 100+ instances of try/except error handling

**Current Duplication Pattern:**
```python
# Found 100+ times in API endpoints
try:
    result = service.fetch_data(...)
    return {...}
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

**Implementation:**
```python
# Exception handler decorator
def handle_api_exception(default_status_code: int = 500):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ValidationError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except NotFoundError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                logger.error(f"API error in {func.__name__}: {e}")
                raise HTTPException(status_code=default_status_code, detail=str(e))
        return wrapper
    return decorator

# Usage in endpoints
@router.get("/data")
@handle_api_exception()
async def get_data(...):
    return service.fetch_data(...)  # No try/except needed
```

**Impact:**
- Reduces 200+ lines of error handling code
- Centralized error handling logic
- Consistent error responses across API
- Easier to add custom exception types

**Files to Modify:**
- Create: `app/core/exception_handlers.py` (60 lines)
- Update: 20+ API endpoint files (remove try/except blocks)

---

## PHASE 3: LARGER REFACTORING (Week 5-6)

### Task 3.1: Standardize Logging

**Issue:** Inconsistent logging across codebase
- Some files use: `logging.getLogger(__name__)`
- Others use: `structlog.get_logger()`
- Inconsistent log levels and message formats

**Current Locations:**
- Core: `structlog` (risk_management.py, secure_config.py)
- Services: mix of `logging` and `structlog`
- Adapters: mostly `logging`

**Strategy:**
1. Standardize on single approach (recommend `structlog` for structured logging)
2. Create `/app/core/logging_config.py`
3. Configure logger across entire application

**Implementation:**
```python
# Create centralized logging setup
import structlog

def setup_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# In every service/adapter
logger = structlog.get_logger(__name__)
logger.info("operation_name", entity_id=123, status="success")
```

**Impact:**
- Reduces 50+ lines of logger setup
- Consistent structured logging
- Better log parsing and monitoring
- Easier debugging and tracing

**Files to Modify:**
- Create: `app/core/logging_config.py` (50 lines)
- Update: `app/main.py` (call setup_logging on startup)
- Update: All service files (use consistent logger)

---

### Task 3.2: Adapter Factory Consolidation

**Issue:** 6+ adapters with duplicated factory/initialization patterns

**Current Duplication Locations:**
```python
# Found in: eastmoney_adapter.py, tqlex_adapter.py, wencai_adapter.py, cninfo_adapter.py
def get_adapter() -> AdapterClass:
    try:
        return AdapterClass()
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        raise
```

**Strategy:**
1. Create centralized adapter registry in `AdapterFactory`
2. Move error handling and initialization logic to factory
3. Reduce duplication in individual adapter files

**Implementation:**
```python
# Central adapter factory
class AdapterFactory:
    _adapters = {}

    @classmethod
    def register_adapter(cls, name: str, adapter_class: Type):
        cls._adapters[name] = adapter_class

    @classmethod
    def get_adapter(cls, name: str, **config):
        try:
            adapter_class = cls._adapters[name]
            return adapter_class(**config)
        except KeyError:
            raise ValueError(f"Adapter {name} not found")
        except Exception as e:
            logger.error(f"Failed to initialize adapter {name}", error=str(e))
            raise

    @classmethod
    def get_all_adapters(cls):
        return {name: cls.get_adapter(name) for name in cls._adapters}

# Register adapters
AdapterFactory.register_adapter('akshare', AkshareDataSource)
AdapterFactory.register_adapter('eastmoney', EastMoneyAdapter)
AdapterFactory.register_adapter('tqlex', TqlexDataSource)
```

**Impact:**
- Reduces 100+ lines of duplication
- Centralized adapter discovery
- Easier to add/remove adapters
- Consistent error handling

**Files to Modify:**
- Create: `app/adapters/adapter_factory.py` (80 lines)
- Update: Each adapter file (remove get_* function)
- Update: Services using adapters (use factory instead)

---

### Task 3.3: Response Schema Standardization

**Issue:** 35+ instances of manual response dict construction

**Current Duplication:**
```python
# Pattern 1 (20+ times)
return {
    "success": True,
    "data": result_data,
    "total": len(result_data),
    "timestamp": datetime.now().isoformat()
}

# Pattern 2 (15+ times)
return {
    "success": result.get('success', False),
    "data": result.get('data'),
    "message": result.get('message'),
    "timestamp": datetime.now().isoformat()
}
```

**Strategy:**
1. Create response schema classes with Pydantic
2. Replace manual dict construction with schema serialization
3. Add response middleware for automatic wrapping

**Implementation:**
```python
# Response schemas
class SuccessResponse(BaseModel):
    success: bool = True
    data: Any
    total: Optional[int] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Usage in endpoints
@router.get("/data")
async def get_data(...) -> SuccessResponse:
    data = service.fetch_data(...)
    return SuccessResponse(data=data, total=len(data))
```

**Impact:**
- Reduces 80+ lines of manual response construction
- Automatic response validation
- Consistent response structure across API
- Better API documentation (OpenAPI/Swagger)

**Files to Modify:**
- Create: `app/schemas/response.py` (50 lines)
- Update: All API endpoint files (use response schemas)

---

## VALIDATION PATTERNS CONSOLIDATION

**Create:** `/app/core/validators.py`

**Consolidate 3+ instances of:**

```python
# Current duplications
# Location 1: data.py
if not symbol:
    raise HTTPException(status_code=400, detail="股票代码不能为空")

# Location 2: market.py
if not symbol:
    raise HTTPException(status_code=400, detail="股票代码不能为空")

# Location 3: technical_analysis.py
if not symbol:
    raise HTTPException(status_code=400, detail="股票代码不能为空")
```

**Consolidation:**
```python
# validators.py
class StockValidator:
    @staticmethod
    def validate_symbol(symbol: Optional[str]) -> str:
        if not symbol:
            raise ValidationError("股票代码不能为空")
        # Additional validation
        return symbol

    @staticmethod
    def validate_date_range(start_date, end_date, default_days=90):
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=default_days)).strftime('%Y-%m-%d')
        return start_date, end_date
```

**Impact:**
- Reduces 60+ lines
- Reusable validation logic
- Consistent validation across endpoints

---

## IMPLEMENTATION TIMELINE

### Week 1-2 (Phase 1)
- Day 1-2: Implement database factory
- Day 3-4: Implement service factory
- Day 5-7: Extend config.py with env vars
- Day 8-10: Testing and validation

### Week 3-4 (Phase 2)
- Day 1-4: Merge market data services
- Day 5-7: Consolidate email services
- Day 8-10: Add exception handlers
- Day 11-14: Testing and migration

### Week 5-6 (Phase 3)
- Day 1-3: Standardize logging
- Day 4-7: Adapter factory consolidation
- Day 8-10: Response schema standardization
- Day 11-12: Validation consolidation
- Day 13-14: Final testing and documentation

---

## ROLLOUT STRATEGY

### Backward Compatibility
- Keep old get_*_service() functions as thin wrappers during transition
- Gradually migrate endpoints to new patterns
- Add deprecation warnings to old patterns

### Testing
- Add unit tests for new factory patterns
- Test database connection pooling
- Validate error responses match old format
- Performance testing on consolidated code

### Documentation
- Update architecture diagram
- Document new factory patterns
- Update contributor guide
- Create migration guide for developers

---

## RISK MITIGATION

### Risks & Mitigations:
1. **Breaking changes in API responses**
   - Mitigation: Implement response wrapper that maintains old format
   - Gradual rollout with feature flags

2. **Database connection issues**
   - Mitigation: Add comprehensive logging to factory
   - Connection pool monitoring

3. **Service initialization order**
   - Mitigation: Factory handles lazy initialization
   - Clear dependency documentation

---

## SUCCESS METRICS

### Code Quality:
- Duplicate LOC: 600-800 → 0-50 lines
- Files affected: 35 → 20
- Function complexity reduction: 30-40%

### Maintainability:
- Time to add new adapter: 50% reduction
- Service initialization: 70% less code
- Error handling: 80% less boilerplate

### Performance:
- Database connection pool efficiency: +20%
- Service initialization time: -15%
- No regression in API response times
