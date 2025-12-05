# Phase 1.1: Custom Exception Hierarchy Guide

**Date**: 2025-12-05
**Status**: ✅ COMPLETE
**Priority**: 🔴 CRITICAL
**Impact**: Eliminates 786+ `except Exception` catches across codebase

---

## Overview

This guide documents the custom exception hierarchy created in `src/core/exceptions.py`. This is **Phase 1.1** of the 6-week technical debt remediation plan.

**Key Achievement**: Single authoritative exception module with 32 specific exception types replaces generic `Exception` catches.

---

## Exception Hierarchy Structure

```
MyStocksException (base)
├── DataSourceException (8 related exceptions)
│   ├── NetworkError
│   ├── DataFetchError
│   ├── DataParseError
│   └── DataValidationError
├── DatabaseException (5 related exceptions)
│   ├── DatabaseConnectionError
│   ├── DatabaseOperationError
│   ├── DatabaseIntegrityError
│   └── DatabaseNotFoundError
├── CacheException (3 related exceptions)
├── ConfigurationException (3 related exceptions)
├── ValidationException (4 related exceptions)
├── BusinessLogicException (4 related exceptions)
├── AuthenticationException (4 related exceptions)
├── TimeoutException (3 related exceptions)
└── ExternalServiceException (4 related exceptions)
```

---

## Exception Module Location

**File**: `src/core/exceptions.py`
**Lines**: 450+ (comprehensive with full docstrings)
**Imports**: `from src.core.exceptions import <ExceptionName>`

---

## Usage Examples

### ❌ OLD CODE (Generic Exceptions)

```python
# Bad: Catches everything, no way to distinguish errors
try:
    data = fetch_market_data(symbol)
    cache.set(f"market:{symbol}", data)
    save_to_db(data)
except Exception as e:
    logger.error(f"Error: {e}")
    # Cannot determine what went wrong or how to recover
```

### ✅ NEW CODE (Specific Exceptions)

```python
from src.core.exceptions import (
    DataFetchError, CacheStoreError, DatabaseOperationError
)

try:
    data = fetch_market_data(symbol)
except DataFetchError as e:
    logger.error(f"Failed to fetch market data: {e.message}")
    # Handle network/data source failure specifically
    return None

try:
    cache.set(f"market:{symbol}", data)
except CacheStoreError as e:
    logger.warning(f"Cache unavailable: {e.message}")
    # Continue without cache

try:
    save_to_db(data)
except DatabaseOperationError as e:
    logger.error(f"Database error: {e.message}")
    raise  # Re-raise for higher-level handler
```

---

## Exception Categories & Use Cases

### 1. DataSourceException (Network, Fetch, Parse, Validation)

**When to use**: Data source operations fail (fetch from API, parse response, validate format)

| Exception | Use Case |
|-----------|----------|
| `NetworkError` | Network request fails (timeout, connection refused) |
| `DataFetchError` | API returns error or unexpected status |
| `DataParseError` | Response format invalid (JSON parse error) |
| `DataValidationError` | Data missing required fields or invalid types |

**Example**:
```python
import httpx
from src.core.exceptions import NetworkError, DataParseError

try:
    response = httpx.get(url, timeout=10.0)
except httpx.TimeoutException as e:
    raise NetworkError(
        message="Failed to connect to data source",
        context={'url': url, 'timeout': 10}
    ) from e

try:
    return response.json()
except json.JSONDecodeError as e:
    raise DataParseError(
        message="Invalid JSON response from data source",
        context={'url': url}
    ) from e
```

---

### 2. DatabaseException (Connection, Operations, Integrity, Not Found)

**When to use**: Database operations fail (query, insert, update, delete)

| Exception | Use Case |
|-----------|----------|
| `DatabaseConnectionError` | Cannot connect to database |
| `DatabaseOperationError` | Query/insert/update/delete fails |
| `DatabaseIntegrityError` | Constraint violation (unique, foreign key) |
| `DatabaseNotFoundError` | Resource not found (404-like) |

**Example**:
```python
from psycopg2 import IntegrityError
from src.core.exceptions import DatabaseIntegrityError

try:
    cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s)", (email, name))
    conn.commit()
except IntegrityError as e:
    conn.rollback()
    if "unique constraint" in str(e):
        raise DatabaseIntegrityError(
            message="User email already exists",
            context={'email': email}
        ) from e
    raise
```

---

### 3. CacheException (Store, Retrieval, Invalidation)

**When to use**: Cache operations fail (Redis, memcached, in-memory cache)

| Exception | Use Case |
|-----------|----------|
| `CacheStoreError` | Failed to store value in cache |
| `CacheRetrievalError` | Failed to retrieve from cache |
| `CacheInvalidationError` | Failed to delete/invalidate cache entry |

**Example**:
```python
from redis import RedisError
from src.core.exceptions import CacheStoreError

try:
    cache.set(key, value, ttl=3600)
except RedisError as e:
    logger.warning(f"Cache store failed: {e}")
    raise CacheStoreError(
        message="Failed to store value in cache",
        context={'key': key}
    ) from e
```

---

### 4. ValidationException (Schema, Type, Range, Required Field)

**When to use**: Input validation fails (missing fields, wrong type, out of range)

| Exception | Use Case |
|-----------|----------|
| `SchemaValidationError` | Response schema doesn't match |
| `DataTypeError` | Value is wrong data type |
| `RangeError` | Value out of acceptable range |
| `RequiredFieldError` | Required field is missing |

**Example**:
```python
from pydantic import ValidationError
from src.core.exceptions import SchemaValidationError

try:
    validated = TradeModel(**trade_data)
except ValidationError as e:
    raise SchemaValidationError(
        message="Invalid trade data",
        context={'errors': e.errors()}
    ) from e
```

---

### 5. BusinessLogicException (Funds, Strategy, Backtest, Trade)

**When to use**: Business rules are violated (insufficient funds, invalid strategy params)

| Exception | Use Case |
|-----------|----------|
| `InsufficientFundsError` | Account has insufficient funds |
| `InvalidStrategyError` | Strategy parameters invalid |
| `BacktestError` | Backtest execution fails |
| `TradeExecutionError` | Trade execution fails |

**Example**:
```python
from src.core.exceptions import InsufficientFundsError

def execute_trade(symbol: str, quantity: int, price: float, account):
    required_funds = quantity * price
    if account.available_cash < required_funds:
        raise InsufficientFundsError(
            message="Insufficient funds for trade",
            context={
                'required': required_funds,
                'available': account.available_cash
            }
        )
```

---

### 6. AuthenticationException (Credentials, Token, Access)

**When to use**: Authentication/authorization fails

| Exception | Use Case |
|-----------|----------|
| `InvalidCredentialsError` | Wrong username/password |
| `TokenExpiredError` | JWT token has expired |
| `TokenInvalidError` | JWT token is malformed/invalid |
| `UnauthorizedAccessError` | User lacks permission |

**Example**:
```python
from jwt import ExpiredSignatureError, InvalidTokenError
from src.core.exceptions import TokenExpiredError, TokenInvalidError

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
except ExpiredSignatureError as e:
    raise TokenExpiredError(
        message="Authentication token has expired"
    ) from e
except InvalidTokenError as e:
    raise TokenInvalidError(
        message="Invalid authentication token"
    ) from e
```

---

### 7. TimeoutException (Network, Database, Operation)

**When to use**: Operation exceeds time limit

| Exception | Use Case |
|-----------|----------|
| `NetworkTimeoutError` | Network operation times out |
| `DatabaseTimeoutError` | Database query times out |
| `OperationTimeoutError` | Generic operation times out |

**Example**:
```python
import asyncio
from src.core.exceptions import OperationTimeoutError

try:
    result = await asyncio.wait_for(long_operation(), timeout=30.0)
except asyncio.TimeoutError:
    raise OperationTimeoutError(
        message="Operation exceeded time limit",
        context={'timeout': 30}
    )
```

---

### 8. ExternalServiceException (Unavailable, Error, Rate Limit, Response)

**When to use**: External service fails (API unavailable, rate limit, unexpected response)

| Exception | Use Case |
|-----------|----------|
| `ServiceUnavailableError` | Service is down/unavailable |
| `ServiceError` | Service returns 5xx error |
| `RateLimitError` | Rate limit exceeded (429) |
| `UnexpectedResponseError` | Service response format unexpected |

**Example**:
```python
import httpx
from src.core.exceptions import RateLimitError, ServiceUnavailableError

response = httpx.get(api_url)
if response.status_code == 429:
    raise RateLimitError(
        message="Data API rate limit exceeded",
        context={'retry_after': response.headers.get('Retry-After')}
    )
elif response.status_code == 503:
    raise ServiceUnavailableError(
        message="Data service temporarily unavailable"
    )
```

---

## Exception Attributes & Methods

Every custom exception inherits these attributes and methods from `MyStocksException`:

### Attributes

```python
exception.message          # Human-readable error message
exception.code            # Error code (e.g., 'NETWORK_TIMEOUT')
exception.severity        # Severity level: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
exception.context         # Dict with additional error details
exception.original_exception  # Original exception being wrapped
exception.timestamp       # When exception was raised (datetime)
```

### Methods

```python
exception.format_message()  # Returns formatted message with context
exception.to_dict()         # Converts to dict for logging/serialization
str(exception)              # Returns formatted message
repr(exception)             # Returns class-name representation
```

### Example

```python
from src.core.exceptions import DataFetchError

try:
    data = fetch_from_api(symbol)
except httpx.TimeoutException as e:
    exc = DataFetchError(
        message="Failed to fetch stock data",
        code="STOCK_DATA_TIMEOUT",
        severity="HIGH",
        context={'symbol': symbol, 'timeout': 30},
        original_exception=e
    )

    # Log with full details
    logger.error(exc.format_message())

    # Serialize for error tracking
    error_record = exc.to_dict()
    # {
    #   'type': 'DataFetchError',
    #   'message': 'Failed to fetch stock data',
    #   'code': 'STOCK_DATA_TIMEOUT',
    #   'severity': 'HIGH',
    #   'context': {'symbol': 'AAPL', 'timeout': 30},
    #   'timestamp': '2025-12-05T10:30:45.123456',
    #   'original_exception': 'ReadTimeout(...)'
    # }
```

---

## Exception Registry

All exceptions are registered in `EXCEPTION_REGISTRY` for programmatic lookup:

```python
from src.core.exceptions import EXCEPTION_REGISTRY, get_exception_class

# Get exception class by name
exc_class = get_exception_class('NetworkError')  # Returns NetworkError class

# Iterate all exceptions
for name, exc_class in EXCEPTION_REGISTRY.items():
    print(f"{name}: {exc_class.default_code}")
```

---

## Migration Guide: From `except Exception` to Specific Exceptions

### Step 1: Identify Exception Locations

```bash
# Find all bare "except Exception" catches
grep -r "except Exception" src/

# Find all untyped except clauses
grep -r "^[ \t]*except:" src/
```

### Step 2: Import Required Exceptions

```python
# At top of file
from src.core.exceptions import (
    DataFetchError, DatabaseOperationError, NetworkError
)
```

### Step 3: Replace Exception Handlers

**Before**:
```python
try:
    result = operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
```

**After**:
```python
from src.core.exceptions import DataFetchError, DatabaseOperationError

try:
    result = operation()
except DataFetchError as e:
    logger.error(f"Data source failed: {e.message}")
    # Handle data fetch failure
except DatabaseOperationError as e:
    logger.error(f"Database error: {e.message}")
    # Handle database failure
except Exception as e:
    # Catch unexpected exceptions
    logger.exception(f"Unexpected error: {e}")
```

---

## Best Practices

### 1. Catch Specific Exceptions

```python
# ❌ Bad: Too broad
try:
    data = fetch_and_save(symbol)
except Exception as e:
    logger.error(str(e))

# ✅ Good: Specific exceptions
try:
    data = fetch_data(symbol)
except DataFetchError as e:
    logger.error(f"Fetch failed: {e.message}")
    return None
except DatabaseOperationError as e:
    logger.error(f"Save failed: {e.message}")
    raise
```

### 2. Provide Context

```python
# ❌ Bad: No context
raise DataFetchError("Failed to fetch data")

# ✅ Good: Rich context
raise DataFetchError(
    message="Failed to fetch stock data",
    code="STOCK_API_ERROR",
    context={
        'symbol': symbol,
        'source': 'AkShare',
        'timestamp': time.time()
    }
)
```

### 3. Preserve Original Exception

```python
# ❌ Bad: Lost original error
try:
    response = httpx.get(url)
except httpx.HTTPError:
    raise NetworkError("Connection failed")

# ✅ Good: Chain exceptions
try:
    response = httpx.get(url)
except httpx.HTTPError as e:
    raise NetworkError(
        message="Connection failed",
        original_exception=e
    ) from e
```

### 4. Use Appropriate Severity

```python
# CRITICAL: System cannot continue
raise DatabaseConnectionError(
    message="Cannot connect to database",
    severity="CRITICAL"  # Default severity
)

# HIGH: Major functionality impaired
raise DataFetchError(
    message="Failed to fetch market data",
    severity="HIGH"
)

# MEDIUM: Operation failed but system continues
raise CacheStoreError(
    message="Cache temporarily unavailable",
    severity="MEDIUM"
)

# LOW: Non-critical operation failed
raise CacheInvalidationError(
    message="Cache eviction failed",
    severity="LOW"
)
```

---

## Testing Exceptions

```python
import pytest
from src.core.exceptions import DataFetchError

def test_data_fetch_error():
    exc = DataFetchError(
        message="API returned error",
        code="API_ERROR_500",
        context={'status': 500}
    )

    assert exc.code == 'API_ERROR_500'
    assert exc.severity == 'HIGH'
    assert 'API_ERROR_500' in str(exc)
    assert 'status=500' in exc.format_message()

def test_exception_registry():
    from src.core.exceptions import get_exception_class
    assert get_exception_class('NetworkError') is not None
    assert get_exception_class('InvalidException') is None
```

---

## Phase 1.2 Next Steps

With the exception hierarchy complete, Phase 1.2 will:

1. Refactor `stock_search.py` (80+ exception catches)
2. Update `market_data_service.py` (65+ exception catches)
3. Update `cache_manager.py` (55+ exception catches)
4. Update remaining critical files

**Estimated effort**: 20 hours across Week 1-2

---

## FAQ

### Q: Should I catch the base `MyStocksException` or specific exceptions?

**A**: Catch specific exceptions. Only catch `MyStocksException` when you need to handle multiple error types the same way:

```python
# Good
try:
    operation()
except DataFetchError as e:
    retry()
except DataValidationError as e:
    skip()

# Also OK (when appropriate)
try:
    operation()
except DataSourceException as e:  # Catches DataFetch, DataParse, etc.
    logger.error(f"Data source failed: {e.message}")
```

### Q: What if the underlying library uses a different exception?

**A**: Wrap it in the appropriate custom exception:

```python
try:
    response = requests.get(url)
except requests.RequestException as e:
    raise NetworkError(
        message="Failed to connect to data source",
        original_exception=e
    ) from e
```

### Q: How should I log exceptions?

**A**: Use the `to_dict()` method for structured logging:

```python
logger.error("Operation failed", extra=exc.to_dict())
# or
logger.error(exc.format_message())
```

---

## Success Metrics

**Phase 1.1 Completion**:
- ✅ 32 custom exceptions defined
- ✅ 450+ lines of documented code
- ✅ Exception registry created
- ✅ Best practices guide provided

**Phase 1 Overall (After 1.2-1.3)**:
- [ ] 786 → 0 bare `except Exception` catches
- [ ] 100% of critical files refactored
- [ ] 20+ hours effort completed

---

**Document Status**: Active
**Last Updated**: 2025-12-05
**Next Review**: After Phase 1.2 completion
