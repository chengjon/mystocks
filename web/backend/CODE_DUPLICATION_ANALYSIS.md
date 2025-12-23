# Code Duplication Analysis Report
## MyStocks Web Backend - Comprehensive Consolidation Opportunities

**Report Date:** 2025-11-06
**Codebase:** /opt/claude/mystocks_spec/web/backend
**Focus Areas:** API endpoints, services, database connections, error handling, adapters

---

## CRITICAL DUPLICATIONS (High Impact)

### 1. DATABASE CONNECTION PATTERNS (3+ Instances)

**Files Affected:**
- `/app/services/market_data_service.py` (lines 32-56)
- `/app/services/market_data_service_v2.py` (lines 31-48)
- `/app/services/watchlist_service.py` (multiple instances)
- `/app/services/announcement_service.py` (similar pattern)

**Duplication:**
```python
# Pattern 1: Database URL Building (REPEATED 3+ TIMES)
def _build_db_url(self) -> str:
    return (
        f"postgresql://{os.getenv('POSTGRESQL_USER')}:"
        f"{os.getenv('POSTGRESQL_PASSWORD')}@"
        f"{os.getenv('POSTGRESQL_HOST')}:"
        f"{os.getenv('POSTGRESQL_PORT')}/"
        f"{os.getenv('POSTGRESQL_DATABASE')}"
    )

# Pattern 2: Engine + Session Creation (REPEATED IN EVERY SERVICE)
def __init__(self):
    db_url = os.getenv('DATABASE_URL') or self._build_db_url()
    self.engine = create_engine(db_url, pool_pre_ping=True, echo=False)
    self.SessionLocal = sessionmaker(bind=self.engine)
```

**Consolidation Opportunity:**
Create `/app/core/database_factory.py` with centralized database connection management.

**Estimated LOC Reduction:** 150+ lines

---

### 2. SERVICE INITIALIZATION FACTORY PATTERN (8+ Instances)

**Files Affected:**
- `/app/services/market_data_service.py` (lines 165+)
- `/app/services/email_notification_service.py` (lines ~45+)
- `/app/services/tdx_service.py`
- `/app/services/watchlist_service.py`
- `/app/services/strategy_service.py`
- `/app/services/stock_search_service.py`
- `/app/services/tradingview_widget_service.py`
- `/app/services/data_service.py`

**Duplication Pattern:**
```python
# REPEATED 8+ TIMES IN DIFFERENT SERVICE FILES
_service_instance = None

def get_service() -> ServiceClass:
    global _service_instance
    if _service_instance is None:
        _service_instance = ServiceClass()
    return _service_instance
```

**Consolidation Opportunity:**
Create generic factory pattern in `/app/core/service_factory.py`

**Estimated LOC Reduction:** 80+ lines

---

### 3. ENVIRONMENT VARIABLE READING PATTERNS (10+ Instances)

**Files Affected:**
- `/app/services/market_data_service.py`
- `/app/services/market_data_service_v2.py`
- `/app/services/email_notification_service.py`
- `/app/services/email_service.py`
- `/app/services/watchlist_service.py`
- `/app/adapters/tqlex_adapter.py`

**Duplication:**
```python
# SMTP Configuration (REPEATED IN 2 EMAIL SERVICES)
self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
self.smtp_port = int(os.getenv('SMTP_PORT', 587))
self.username = os.getenv('SMTP_USERNAME', '')
self.password = os.getenv('SMTP_PASSWORD', '')
self.use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'

# PostgreSQL Configuration (REPEATED IN 9+ SERVICES)
'host': os.getenv('POSTGRESQL_HOST', 'localhost'),
'port': int(os.getenv('POSTGRESQL_PORT', 5432)),
'database': os.getenv('POSTGRESQL_DATABASE', 'mystocks'),
'user': os.getenv('POSTGRESQL_USER', 'postgres'),
'password': os.getenv('POSTGRESQL_PASSWORD', '')
```

**Consolidation Opportunity:**
Already partially done in `/app/core/config.py` - extend with more env var groups.

**Estimated LOC Reduction:** 120+ lines

---

### 4. ERROR HANDLING & RESPONSE FORMATTING (805+ Occurrences)

**Files Affected:** All API files in `/app/api/`
- `/app/api/risk_management.py` (38 try/except blocks)
- `/app/api/data.py` (23 try/except blocks)
- `/app/api/strategy.py` (18 try/except blocks)
- `/app/api/market.py` (44 try/except blocks)
- `/app/api/monitoring.py` (65 try/except blocks)
- And 15+ more API files

**Duplication Pattern:**
```python
# PATTERN 1: Generic Exception to HTTPException (REPEATED 100+ TIMES)
try:
    result = service.fetch_data(...)
    return {...}
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# PATTERN 2: Success/Failure Response Format (REPEATED 50+ TIMES)
return {
    "success": True,
    "data": result_data,
    "message": "Operation successful",
    "timestamp": datetime.now().isoformat()
}
```

**Consolidation Opportunity:**
Create `/app/core/exception_handlers.py` and response wrapper middleware.

**Estimated LOC Reduction:** 200+ lines

---

## SIGNIFICANT DUPLICATIONS (Medium Impact)

### 5. MARKET DATA SERVICE VERSIONS (2 Parallel Implementations)

**Files Affected:**
- `/app/services/market_data_service.py` (uses Akshare)
- `/app/services/market_data_service_v2.py` (uses EastMoney)

**Issue:** Both services implement nearly identical business logic with different adapters:
- `fetch_and_save_fund_flow()` - 60+ LOC each, 90% identical
- `query_fund_flow()` - similar implementation
- Database session management - duplicated
- Error handling - identical patterns

**Functions Duplicated:**
- fetch_and_save_* (Fund Flow, ETF, Chip Race, LHB)
- query_* methods
- _build_db_url() and engine initialization

**Consolidation Opportunity:**
Merge into single service with adapter pattern: `MarketDataService(adapter='akshare')` vs `MarketDataService(adapter='eastmoney')`

**Estimated LOC Reduction:** 300+ lines

---

### 6. EMAIL SERVICE DUPLICATION

**Files Affected:**
- `/app/services/email_service.py`
- `/app/services/email_notification_service.py`

**Issue:** Two separate email services with overlapping functionality:
- Both read SMTP configuration from environment
- Both implement send() logic with identical patterns
- Both have try/except blocks for email sending
- Slight variations in parameter handling

**Consolidation Opportunity:**
Merge into single `EmailService` with configuration management.

**Estimated LOC Reduction:** 150+ lines

---

### 7. ADAPTER INITIALIZATION & ERROR HANDLING (8+ Adapters)

**Files Affected:**
- `/app/adapters/base.py`
- `/app/adapters/eastmoney_adapter.py`
- `/app/adapters/eastmoney_enhanced.py`
- `/app/adapters/akshare_extension.py`
- `/app/adapters/tqlex_adapter.py`
- `/app/adapters/wencai_adapter.py`
- `/app/adapters/cninfo_adapter.py`

**Duplication Pattern:**
```python
# FACTORY FUNCTION (REPEATED IN 6 ADAPTERS)
def get_adapter() -> AdapterClass:
    try:
        return AdapterClass()
    except Exception as e:
        logger.error(f"Failed to initialize {adapter_name}: {e}")
        raise

# VALIDATION (REPEATED IN MULTIPLE ADAPTERS)
if not data or data.empty:
    return {"success": False, "message": "No data retrieved"}
```

**Consolidation Opportunity:**
Create centralized adapter factory with unified error handling.

**Estimated LOC Reduction:** 100+ lines

---

### 8. LOGGING PATTERNS (Inconsistent Implementation)

**Files Affected:** All service files
- Logger creation: Multiple patterns (`logging.getLogger(__name__)` vs `structlog.get_logger()`)
- Logging statements: Similar message patterns repeated
- Log levels: Inconsistent usage

**Examples:**
```python
# Pattern 1: Standard logging (Used in most services)
logger = logging.getLogger(__name__)
logger.info(f"Task {task_id} scheduled successfully")

# Pattern 2: Structlog (Used in some core files)
logger = structlog.get_logger()
logger.info("PostgreSQL engine created", database=settings.postgresql_database)
```

**Consolidation Opportunity:**
Standardize on single logging approach with consistent patterns.

**Estimated LOC Reduction:** 50+ lines

---

## MODERATE DUPLICATIONS (Low-Medium Impact)

### 9. DATA VALIDATION PATTERNS

**Files Affected:**
- `/app/api/data.py` (parameter validation)
- `/app/api/market.py` (parameter validation)
- `/app/api/technical_analysis.py` (parameter validation)

**Duplication:**
```python
# STOCK CODE VALIDATION (REPEATED 3+ TIMES)
if not symbol:
    raise HTTPException(status_code=400, detail="股票代码不能为空")

# DATE RANGE VALIDATION (REPEATED 4+ TIMES)
if not end_date:
    end_date = datetime.now().strftime('%Y-%m-%d')
if not start_date:
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
```

**Consolidation Opportunity:**
Create `/app/core/validators.py` with reusable validation functions.

**Estimated LOC Reduction:** 60+ lines

---

### 10. CACHE KEY GENERATION & TTL MANAGEMENT

**Files Affected:**
- `/app/api/market.py` (multiple cache decorators)
- `/app/api/data.py` (cache key construction)
- `/app/core/cache_utils.py` (centralized but not fully utilized)

**Issue:** Cache strategy partially centralized in `CacheManager` but not consistently used.

**Consolidation Opportunity:**
Expand `/app/core/cache_utils.py` and create unified caching strategy.

**Estimated LOC Reduction:** 40+ lines

---

### 11. API RESPONSE WRAPPER PATTERNS

**Files Affected:** All API endpoint files

**Duplication:**
```python
# RESPONSE WRAPPER 1 (USED 20+ TIMES)
return {
    "success": True,
    "data": result_data,
    "total": len(result_data),
    "timestamp": datetime.now().isoformat()
}

# RESPONSE WRAPPER 2 (USED 15+ TIMES - WITH MESSAGE)
return {
    "success": result.get('success', False),
    "data": result.get('data'),
    "message": result.get('message'),
    "timestamp": datetime.now().isoformat()
}
```

**Consolidation Opportunity:**
Create response schema classes with automatic serialization.

**Estimated LOC Reduction:** 80+ lines

---

## CONSOLIDATION ROADMAP

### Phase 1 (Quick Wins - 20% effort, 30% impact)
1. Create centralized database factory
2. Create service factory pattern
3. Standardize environment variable handling

### Phase 2 (Medium Effort - 40% effort, 50% impact)
4. Merge market_data_service v1 & v2
5. Consolidate email services
6. Create unified exception handlers

### Phase 3 (Larger Refactoring - 40% effort, 20% impact)
7. Standardize logging approach
8. Consolidate adapter factories
9. Create response wrapper schemas

---

## SUMMARY STATISTICS

**Total Code Duplication Impact:**
- Estimated duplicate LOC: 600-800 lines
- Number of duplication patterns: 11 major categories
- Files affected: 35+ Python files
- Consolidation potential: 30-40% code reduction in services layer

**High Priority Files (Most Duplication):**
1. `/app/services/` - 250+ duplicate lines
2. `/app/api/` - 200+ duplicate error handlers
3. `/app/adapters/` - 100+ duplicate patterns
4. `/app/core/` - Opportunities to extend existing utilities

**Recommended Consolidation Order:**
1. Database connections (affects 9+ services)
2. Service factories (affects 8+ services)
3. Error handling (affects 20+ endpoints)
4. Market data services (massive duplication)
5. Email services (straightforward merge)
