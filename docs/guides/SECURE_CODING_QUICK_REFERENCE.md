# Secure Coding Quick Reference

**Purpose**: Quick reference for secure coding patterns in MyStocks project

---

## 🚨 Critical Rules

### 1. NEVER Use f-strings for SQL Queries

```python
# ❌ WRONG - SQL Injection Vulnerability
query = f"SELECT * FROM {table_name} WHERE symbol = '{symbol}'"

# ✅ CORRECT - Parameterized Query (PostgreSQL)
from psycopg2 import sql
query = sql.SQL("SELECT * FROM {} WHERE symbol = %s").format(
    sql.Identifier(table_name)
)
params = (symbol,)

# ✅ CORRECT - Whitelist Validation (TDengine)
TDengineSecureQueryBuilder.validate_table_name(table_name)
query = TDengineSecureQueryBuilder.build_select_query(
    table_name=table_name,
    columns=["*"],
    where_conditions={"symbol": symbol}
)
```

### 2. ALWAYS Validate Secrets on Startup

```python
# ✅ CORRECT - Validate before starting
from src.utils.secret_validator import SecretValidator

def create_app():
    SecretValidator.enforce_startup_validation(exit_on_failure=True)
    # Continue with app startup
```

### 3. ALWAYS Pre-hash Long Passwords

```python
# ✅ CORRECT - SHA-256 then bcrypt
from src.utils.password_handler import PasswordHandler

hashed = PasswordHandler.hash_password(plain_password)
is_valid = PasswordHandler.verify_password(plain_password, hashed)
```

### 4. ALWAYS Use Connection Pools Properly

```python
# ✅ CORRECT - Context manager ensures return
with self.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(query, params)
# Connection automatically returned to pool
```

---

## 📋 Secure Patterns Library

### PostgreSQL Queries

```python
from src.utils.secure_query_builder import SecureQueryBuilder

# SELECT
query, params = SecureQueryBuilder.select(
    table_name="stocks",
    columns=["symbol", "close", "volume"],
    where_clause="trade_date BETWEEN %s AND %s",
    params=(start_date, end_date),
    limit=1000
)

# INSERT
data = {"symbol": "AAPL", "close": 150.0, "volume": 1000000}
query, params = SecureQueryBuilder.insert("stocks", data)

# UPDATE
query, params = SecureQueryBuilder.update(
    table_name="stocks",
    data={"close": 151.0},
    where_clause="symbol = %s",
    where_params=("AAPL",)
)
```

### TDengine Queries

```python
from src.utils.tdengine_secure_query import TDengineSecureQueryBuilder

# SELECT with whitelist validation
query = TDengineSecureQueryBuilder.build_select_query(
    table_name="stock_daily_kline",  # Must be in whitelist
    columns=["trade_date", "close"],  # All must be in whitelist
    where_conditions={"symbol": "AAPL"}
)

# Execute with limit (validated)
result = conn.execute(f"{query} LIMIT 1000")
```

### Input Validation

```python
from src.utils.input_validator import InputValidator

# Validate stock symbol
symbol = user_input.upper()
if not InputValidator.is_valid_symbol(symbol):
    raise ValueError(f"Invalid symbol: {symbol}")

# Validate date range
if not InputValidator.is_valid_date_range(start, end):
    raise ValueError("Invalid date range")

# Validate numeric input
if not InputValidator.is_positive_integer(limit):
    raise ValueError("Limit must be positive integer")
```

---

## 🔒 Security Best Practices

### Password Storage

```python
# ✅ CORRECT
from src.utils.password_handler import PasswordHandler

# Registration
hashed_pw = PasswordHandler.hash_password(user_password)
save_to_database(username, hashed_pw)

# Login
if PasswordHandler.verify_password(login_password, stored_hash):
    # Generate JWT token
```

### JWT Token Generation

```python
# ✅ CORRECT - Use validated secret
from src.core.config import get_settings

settings = get_settings()  # Includes secret validation
secret = settings.JWT_SECRET_KEY  # Guaranteed to be strong

token = jwt.encode(payload, secret, algorithm="HS256")
```

### API Authentication

```python
# ✅ CORRECT - Verify JWT signature
from src.core.security import verify_token

token = request.headers.get("Authorization")
payload = verify_token(token)  # Raises exception if invalid

# Now safe to use payload
user_id = payload["user_id"]
```

---

## 🧪 Testing Security

### SQL Injection Tests

```python
def test_sql_injection_prevention():
    # Attack vectors to test
    attack_strings = [
        "BTC' OR '1'='1",
        "BTC' UNION SELECT * FROM users --",
        "BTC'; DROP TABLE stocks; --",
    ]

    for attack in attack_strings:
        result = fetch_data("stocks", symbol=attack)
        assert len(result) == 0, f"Injection succeeded: {attack}"
```

### Secret Validation Tests

```python
def test_weak_secrets_rejected():
    weak_secrets = ["password", "123456", "short"]

    for secret in weak_secrets:
        is_valid, msg = SecretValidator.validate_jwt_secret(secret)
        assert not is_valid
```

---

## 📊 Monitoring

### Connection Pool Monitoring

```python
# Get connection statistics
stats = postgres_access.get_connection_stats()
print(f"Active connections: {stats['active']}")
print(f"Total created: {stats['total_created']}")

# Check for leaks
monitor.check_for_leaks()
```

### Security Event Logging

```python
import logging

logger = logging.getLogger(__name__)

# Log security events
logger.warning("Failed login attempt", extra={
    "username": username,
    "ip_address": request.remote_addr,
    "timestamp": datetime.now()
})

logger.error("SQL injection attempt blocked", extra={
    "attack_string": input_string,
    "stack_trace": traceback.format_stack()
})
```

---

## 🚨 Common Mistakes

### ❌ Mistake 1: String Concatenation

```python
# WRONG
query = "SELECT * FROM " + table_name + " WHERE id = " + str(id)
```

### ❌ Mistake 2: Format Strings

```python
# WRONG
query = "SELECT * FROM {} WHERE symbol = '{}'".format(table, symbol)
```

### ❌ Mistake 3: f-strings (Most Common)

```python
# WRONG
query = f"SELECT * FROM {table} WHERE symbol = '{symbol}'"
```

### ❌ Mistake 4: Skipping Validation

```python
# WRONG - Trusting user input
def fetch_data(symbol, table, limit):
    return db.query(f"SELECT * FROM {table} WHERE symbol = '{symbol}' LIMIT {limit}")
```

---

## ✅ Correct Examples

### Example 1: Secure API Endpoint

```python
from fastapi import APIRouter, HTTPException, Depends
from src.utils.secure_query_builder import SecureQueryBuilder
from src.core.security import get_current_user

router = APIRouter()

@router.get("/api/stocks/{symbol}")
async def get_stock_data(
    symbol: str,
    start_date: str,
    end_date: str,
    limit: int = 1000,
    current_user = Depends(get_current_user)
):
    """Secure endpoint with validated inputs"""

    # Validate inputs
    if len(symbol) > 20:
        raise HTTPException(status_code=400, detail="Invalid symbol")

    if limit < 1 or limit > 10000:
        raise HTTPException(status_code=400, detail="Invalid limit")

    # Build secure query
    query, params = SecureQueryBuilder.select(
        table_name="stock_daily_kline",
        columns=["trade_date", "open", "high", "low", "close", "volume"],
        where_clause="symbol = %s AND trade_date BETWEEN %s AND %s",
        params=(symbol, start_date, end_date),
        limit=limit
    )

    # Execute safely
    try:
        results = db.execute(query, params)
        return {"data": results}
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
```

### Example 2: Secure Authentication

```python
from src.utils.password_handler import PasswordHandler
from src.utils.secret_validator import SecretValidator
import jwt

@router.post("/auth/login")
async def login(credentials: UserLogin):
    """Secure login endpoint"""

    # Validate secrets already done on startup
    # (SecretValidator.enforce_startup_validation() in app_factory.py)

    # Fetch user with secure query
    query, params = SecureQueryBuilder.select(
        table_name="users",
        where_clause="username = %s",
        params=(credentials.username,)
    )

    user = db.execute(query, params)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password (handles long passwords correctly)
    if not PasswordHandler.verify_password(
        credentials.password,
        user["hashed_password"]
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate JWT with validated secret
    from src.core.config import get_settings
    settings = get_settings()

    token = jwt.encode(
        {"sub": user["username"], "exp": datetime.now() + timedelta(hours=24)},
        settings.JWT_SECRET_KEY,  # Already validated on startup
        algorithm="HS256"
    )

    return {"access_token": token}
```

---

## 🎯 Checklist for New Code

Before committing new code, verify:

- [ ] No f-strings for SQL queries
- [ ] All user inputs validated
- [ ] Parameterized queries used everywhere
- [ ] Secrets validated on startup
- [ ] Passwords use PasswordHandler
- [ ] Connection pools used correctly
- [ ] Error handling doesn't leak info
- [ ] Security tests added
- [ ] Code reviewed by security lead

---

## 📚 Additional Resources

### Internal Documentation
- `SECURITY_FIX_IMPLEMENTATION_PLAN.md` - Detailed fix strategies
- `CREDENTIAL_SETUP_GUIDE.md` - Secret management
- `SQL_INJECTION_FIX_SPEC.md` - Secure query patterns

### External Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [psycopg2.sql Documentation](https://www.psycopg.org/docs/sql.html)

---

**Version**: 1.0
**Last Updated**: 2026-01-01
**Maintainer**: Security Team

**Remember**: When in doubt, ask the security lead BEFORE committing!
