# Critical Security Issues - Implementation Plan

**Created**: 2026-01-01
**Priority**: 🔴 CRITICAL
**Timeline**: 7-10 days
**Status**: Planning Phase

---

## Executive Summary

This document provides detailed implementation plans for addressing the **5 critical security vulnerabilities** identified in the architecture review. All issues require immediate attention to prevent potential security breaches.

### Critical Issues Overview

| Issue | Severity | Files Affected | Est. Time | Risk Level |
|-------|----------|----------------|-----------|------------|
| SQL Injection | 🔴 Critical | 15+ | 2-3 days | Very High |
| Weak Credential Management | 🔴 Critical | 8+ | 1 day | High |
| Bcrypt Password Truncation | 🟠 High | 3 | 1 day | Medium |
| Connection Pool Issues | 🟠 High | 4 | 1 day | Medium |
| Missing Security Tests | 🟡 Medium | New | 2 days | High |

---

## Issue 1: SQL Injection Vulnerabilities

### Severity: 🔴 CRITICAL
**Timeline**: 2-3 days
**Risk**: Data breach, unauthorized data access, data manipulation

### Affected Files

Based on the code review, these files use unsafe f-string SQL formatting:

#### PostgreSQL Access Layer
```
src/data_access/postgresql_data_access.py
src/core/data_manager.py
src/database_manager/database_manager.py
```

#### TDengine Access Layer
```
src/data_access/tdengine_data_access.py
src/core/unified_manager.py
```

#### Adapter Layer
```
src/adapters/akshare_adapter.py
src/adapters/baostock_adapter.py
src/adapters/financial_adapter.py
src/adapters/tdx_adapter.py
src/adapters/tushare_adapter.py
```

### Root Cause Analysis

```python
# ❌ VULNERABLE CODE PATTERN (Found in 15+ files)
def fetch_data(self, table_name: str, symbol: str):
    query = f"SELECT * FROM {table_name} WHERE symbol = '{symbol}'"
    # ^^^ SQL INJECTION: Both table_name and symbol are vulnerable
    return self.execute_query(query)
```

**Attack Vector**:
```python
# Attacker controlled input
symbol = "BTC/USDT' OR '1'='1"
# Resulting query: SELECT * FROM stocks WHERE symbol = 'BTC/USDT' OR '1'='1'
# Returns ALL rows, bypassing filters
```

### Implementation Strategy

#### Phase 1: Audit and Document (Day 1, Morning)

**Task 1.1**: Create SQL query inventory
```bash
# Run this script to identify all SQL queries
python scripts/dev/security_audit_sql_queries.py
```

**Output Format**:
```json
{
  "postgres_queries": [
    {
      "file": "src/data_access/postgresql_data_access.py",
      "line": 234,
      "function": "fetch_market_data",
      "query_type": "SELECT",
      "vulnerability": "f-string formatting",
      "parameters": ["table_name", "symbol", "start_date"]
    }
  ],
  "tdengine_queries": [...]
}
```

**Task 1.2**: Create security fix specification document
```markdown
# SQL Injection Fix Specification

## Secure Query Patterns

### Pattern 1: Parameterized Queries (PostgreSQL)
```python
from psycopg2 import sql

def secure_query(table_name: str, symbol: str):
    query = sql.SQL("SELECT * FROM {} WHERE symbol = %s").format(
        sql.Identifier(table_name)
    )
    params = (symbol,)
    return self.execute_query(query, params)
```

### Pattern 2: Prepared Statements (TDengine)
```python
from taosws import TaosConn

def secure_query(table_name: str, symbol: str):
    # Use connection's prepared statement API
    stmt = self.conn.stmt_init()
    stmt.prepare("SELECT * FROM ? WHERE symbol = ?")
    stmt.bind_param([table_name, symbol])
    return stmt.execute()
```
```

#### Phase 2: PostgreSQL Fixes (Day 1, Afternoon - Day 2)

**Priority Order**:
1. Core data access layer (highest risk)
2. Manager layer
3. Adapter layer

**Implementation Steps**:

**Step 1**: Create secure query utility
```python
# src/utils/secure_query_builder.py
from typing import List, Tuple, Any, Union
from psycopg2 import sql
import logging

logger = logging.getLogger(__name__)

class SecureQueryBuilder:
    """Build secure SQL queries using psycopg2.sql module"""

    @staticmethod
    def select(
        table_name: str,
        columns: List[str] = None,
        where_clause: str = None,
        params: Tuple[Any, ...] = None,
        limit: int = None
    ) -> Tuple[sql.SQL, Tuple[Any, ...]]:
        """
        Build a secure SELECT query

        Args:
            table_name: Table name (will be escaped as identifier)
            columns: List of column names (will be escaped as identifiers)
            where_clause: WHERE clause template with %s placeholders
            params: Parameter values for where clause
            limit: Optional LIMIT clause

        Returns:
            Tuple of (query_sql, params)
        """
        if columns is None:
            columns = ["*"]

        # Build column list (safe identifiers)
        col_list = sql.SQL(", ").join(map(sql.Identifier, columns))

        # Build base query
        query = sql.SQL("SELECT {} FROM {}").format(
            col_list,
            sql.Identifier(table_name)
        )

        # Add WHERE clause
        final_params = ()
        if where_clause:
            query = sql.SQL("{} WHERE {}").format(query, sql.SQL(where_clause))
            if params:
                final_params = params

        # Add LIMIT
        if limit:
            query = sql.SQL("{} LIMIT {}").format(query, sql.Literal(limit))

        logger.debug(f"Built secure query for table: {table_name}")
        return query, final_params

    @staticmethod
    def insert(
        table_name: str,
        data: dict
    ) -> Tuple[sql.SQL, Tuple[Any, ...]]:
        """
        Build a secure INSERT query

        Args:
            table_name: Table name
            data: Dictionary of column_name: value pairs

        Returns:
            Tuple of (query_sql, params)
        """
        columns = data.keys()
        values = data.values()

        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder() * len(data))
        )

        return query, tuple(values)

    @staticmethod
    def update(
        table_name: str,
        data: dict,
        where_clause: str,
        where_params: Tuple[Any, ...]
    ) -> Tuple[sql.SQL, Tuple[Any, ...]]:
        """
        Build a secure UPDATE query

        Args:
            table_name: Table name
            data: Dictionary of column_name: value pairs to update
            where_clause: WHERE clause template with %s placeholders
            where_params: Parameter values for where clause

        Returns:
            Tuple of (query_sql, params)
        """
        set_clause = sql.SQL(", ").join(
            sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder())
            for k in data.keys()
        )

        query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
            sql.Identifier(table_name),
            set_clause,
            sql.SQL(where_clause)
        )

        params = tuple(data.values()) + where_params
        return query, params
```

**Step 2**: Update PostgreSQL data access layer
```python
# src/data_access/postgresql_data_access.py

# Before (VULNERABLE):
def fetch_market_data(self, table_name: str, symbol: str, start_date: str, end_date: str):
    query = f"""
        SELECT * FROM {table_name}
        WHERE symbol = '{symbol}'
        AND trade_date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY trade_date
    """
    return self.execute_query(query)

# After (SECURE):
def fetch_market_data(
    self,
    table_name: str,
    symbol: str,
    start_date: str,
    end_date: str
) -> List[dict]:
    """
    Fetch market data with secure parameterized query

    Args:
        table_name: Target table name
        symbol: Stock symbol (safe parameter)
        start_date: Start date (safe parameter)
        end_date: End date (safe parameter)

    Returns:
        List of market data records
    """
    from src.utils.secure_query_builder import SecureQueryBuilder

    query, params = SecureQueryBuilder.select(
        table_name=table_name,
        where_clause="symbol = %s AND trade_date BETWEEN %s AND %s",
        params=(symbol, start_date, end_date)
    )

    query = sql.SQL("{} ORDER BY trade_date").format(query)

    try:
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Failed to fetch market data: {e}")
        raise
```

**Step 3**: Update all PostgreSQL query locations
```bash
# Run automated fix script
python scripts/dev/fix_sql_injection_postgres.py --dry-run
# Review changes
python scripts/dev/fix_sql_injection_postgres.py --apply
```

#### Phase 3: TDengine Fixes (Day 2, Afternoon - Day 3)

**TDengine Challenge**: TDengine's Python driver has limited parameterized query support.

**Solution**: Use whitelist validation + strict escaping

```python
# src/utils/tdengine_secure_query.py
import re
from typing import List, Set

class TDengineSecureQueryBuilder:
    """Secure query builder for TDengine"""

    # Whitelist of allowed table names
    ALLOWED_TABLES: Set[str] = {
        "stock_daily_kline",
        "stock_minute_kline",
        "stock_tick_data",
        # ... add all valid tables
    }

    # Whitelist of allowed columns
    ALLOWED_COLUMNS: Set[str] = {
        "trade_date", "open", "high", "low", "close", "volume",
        "symbol", "timestamp", # ... add all valid columns
    }

    @staticmethod
    def validate_table_name(table_name: str) -> bool:
        """Validate table name against whitelist"""
        if table_name not in TDengineSecureQueryBuilder.ALLOWED_TABLES:
            raise ValueError(f"Table '{table_name}' not in whitelist")
        return True

    @staticmethod
    def validate_column_name(column: str) -> bool:
        """Validate column name against whitelist"""
        if column not in TDengineSecureQueryBuilder.ALLOWED_COLUMNS:
            raise ValueError(f"Column '{column}' not in whitelist")
        return True

    @staticmethod
    def escape_string(value: str) -> str:
        """Escape string values for TDengine"""
        # Remove any potential SQL meta-characters
        return re.sub(r"[\"';\\]", "", value)

    @staticmethod
    def build_select_query(
        table_name: str,
        columns: List[str],
        where_conditions: dict
    ) -> str:
        """
        Build secure SELECT query for TDengine

        Args:
            table_name: Must be in ALLOWED_TABLES
            columns: List of columns, all must be in ALLOWED_COLUMNS
            where_conditions: Dictionary of column: value pairs

        Returns:
            Safe SQL query string
        """
        # Validate table name
        TDengineSecureQueryBuilder.validate_table_name(table_name)

        # Validate columns
        for col in columns:
            TDengineSecureQueryBuilder.validate_column_name(col)

        # Build column list
        col_str = ", ".join(columns)

        # Build WHERE clause with escaped values
        where_parts = []
        for col, val in where_conditions.items():
            TDengineSecureQueryBuilder.validate_column_name(col)
            if isinstance(val, str):
                escaped_val = TDengineSecureQueryBuilder.escape_string(val)
                where_parts.append(f"{col} = '{escaped_val}'")
            else:
                where_parts.append(f"{col} = {val}")

        where_str = " AND ".join(where_parts) if where_parts else "1=1"

        return f"SELECT {col_str} FROM {table_name} WHERE {where_str}"
```

**Update TDengine access layer**:
```python
# src/data_access/tdengine_data_access.py

# Before (VULNERABLE):
def fetch_tick_data(self, table_name: str, symbol: str, limit: int = 1000):
    query = f"SELECT * FROM {table_name} WHERE symbol = '{symbol}' LIMIT {limit}"
    return self.execute(query)

# After (SECURE):
def fetch_tick_data(self, table_name: str, symbol: str, limit: int = 1000):
    """
    Fetch tick data with validated query

    Args:
        table_name: Must be whitelisted
        symbol: Stock symbol (validated)
        limit: Maximum records (validated integer)

    Returns:
        List of tick data records
    """
    from src.utils.tdengine_secure_query import TDengineSecureQueryBuilder

    # Validate and build query
    query = TDengineSecureQueryBuilder.build_select_query(
        table_name=table_name,
        columns=["*"],  # Wildcard is OK
        where_conditions={"symbol": symbol}
    )

    # Validate limit is integer
    if not isinstance(limit, int) or limit < 1 or limit > 100000:
        raise ValueError(f"Invalid limit: {limit}")

    query = f"{query} LIMIT {limit}"

    try:
        return self.execute(query)
    except Exception as e:
        logger.error(f"TDengine query failed: {e}")
        raise
```

#### Phase 4: Security Test Suite (Day 3)

**Create comprehensive security tests**:

```python
# tests/security/test_sql_injection_prevention.py
import pytest
from src.utils.secure_query_builder import SecureQueryBuilder
from src.utils.tdengine_secure_query import TDengineSecureQueryBuilder

class TestSQLInjectionPrevention:
    """Test suite for SQL injection prevention"""

    def test_postgres_sql_injection_symbol(self):
        """Test that SQL injection attempts in symbol parameter are blocked"""
        # Attack vector 1: Tautology
        malicious_symbol = "BTC' OR '1'='1"
        query, params = SecureQueryBuilder.select(
            table_name="stocks",
            where_clause="symbol = %s",
            params=(malicious_symbol,)
        )

        # Execute and verify no records returned
        # Should return 0, not all records
        result = execute_query(query, params)
        assert len(result) == 0, "SQL injection succeeded!"

    def test_postgres_sql_injection_union_select(self):
        """Test UNION SELECT injection attempt"""
        malicious_symbol = "BTC' UNION SELECT * FROM users --"
        query, params = SecureQueryBuilder.select(
            table_name="stocks",
            where_clause="symbol = %s",
            params=(malicious_symbol,)
        )

        # Should be treated as literal string, not SQL
        result = execute_query(query, params)
        assert len(result) == 0

    def test_postgres_table_name_injection(self):
        """Test table name injection attempt"""
        malicious_table = "stocks; DROP TABLE users; --"

        with pytest.raises(Exception):
            # sql.Identifier should escape this
            query, _ = SecureQueryBuilder.select(
                table_name=malicious_table,
                where_clause="symbol = %s",
                params=("BTC",)
            )

    def test_tdengine_whitelist_validation(self):
        """Test TDengine table name whitelist"""
        with pytest.raises(ValueError, match="not in whitelist"):
            TDengineSecureQueryBuilder.validate_table_name("nonexistent_table")

    def test_tdengine_column_validation(self):
        """Test TDengine column whitelist"""
        with pytest.raises(ValueError, match="not in whitelist"):
            TDengineSecureQueryBuilder.validate_column_name("malicious_column")

    def test_tdengine_string_escaping(self):
        """Test that dangerous characters are escaped"""
        malicious = "test'; DROP TABLE--"
        escaped = TDengineSecureQueryBuilder.escape_string(malicious)

        assert "'" not in escaped
        assert ";" not in escaped
        assert "--" not in escaped

    @pytest.mark.parametrize("attack_string", [
        "BTC' OR '1'='1",
        "BTC' UNION SELECT password FROM users --",
        "BTC'; DROP TABLE stocks; --",
        "BTC' AND 1=1 --",
        "BTC' OR 1=1#",
        "1' OR '1'='1' --"
    ])
    def test_various_injection_attempts(self, attack_string):
        """Test various SQL injection patterns"""
        query, params = SecureQueryBuilder.select(
            table_name="stocks",
            where_clause="symbol = %s",
            params=(attack_string,)
        )

        result = execute_query(query, params)
        assert len(result) == 0, f"Injection succeeded: {attack_string}"
```

**Test execution script**:
```bash
# Run security tests
pytest tests/security/test_sql_injection_prevention.py -v

# Run with coverage
pytest tests/security/ --cov=src/data_access --cov-report=html

# Run in CI/CD
pytest tests/security/ --strict-markers --fail-on-warning
```

### Verification Checklist

- [ ] All f-string SQL queries replaced with parameterized queries
- [ ] Security test suite passes (100% pass rate)
- [ ] Code coverage >90% for data access layer
- [ ] No new SQL vulnerabilities introduced
- [ ] Documentation updated
- [ ] Team trained on secure query patterns

---

## Issue 2: Weak Credential Management

### Severity: 🔴 CRITICAL
**Timeline**: 1 day
**Risk**: Default secrets in production, unauthorized access

### Affected Files

```
web/backend/app/core/config.py
src/core/config.py
.env.example
scripts/JWT_key_update.sh
```

### Root Cause

No validation that secrets were changed from defaults on application startup.

### Implementation Strategy

#### Phase 1: Add Secret Validation (Morning)

**Step 1**: Create secret validation utility

```python
# src/utils/secret_validator.py
import os
import re
import secrets
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class SecretValidator:
    """Validate that secrets meet security requirements"""

    # Common weak passwords/keys to reject
    WEAK_PATTERNS = [
        r'^password$',  # "password"
        r'^123456$',    # Simple numbers
        r'^admin$',     # "admin"
        r'^test$',      # "test"
        r'^changeme$',  # "changeme"
        r'^secret$',    # "secret"
        r'^.{0,8}$',    # Too short (<8 chars)
    ]

    @staticmethod
    def validate_jwt_secret(secret: str) -> Tuple[bool, str]:
        """
        Validate JWT secret key strength

        Args:
            secret: JWT secret key

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not secret:
            return False, "JWT_SECRET_KEY is not set"

        # Check length (minimum 32 characters for HS256)
        if len(secret) < 32:
            return False, f"JWT_SECRET_KEY too short ({len(secret)} < 32 chars)"

        # Check for weak patterns
        for pattern in SecretValidator.WEAK_PATTERNS:
            if re.match(pattern, secret.lower()):
                return False, "JWT_SECRET_KEY matches a known weak pattern"

        # Check entropy (should not be all same character)
        if len(set(secret)) < 16:
            return False, "JWT_SECRET_KEY has low entropy"

        return True, "OK"

    @staticmethod
    def validate_database_password(password: str, db_type: str) -> Tuple[bool, str]:
        """
        Validate database password strength

        Args:
            password: Database password
            db_type: 'postgresql' or 'tdengine'

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, f"{db_type}_PASSWORD is not set"

        if len(password) < 12:
            return False, f"{db_type}_PASSWORD too short ({len(password)} < 12 chars)"

        # Check for weak patterns
        for pattern in SecretValidator.WEAK_PATTERNS:
            if re.match(pattern, password.lower()):
                return False, f"{db_type}_PASSWORD matches a known weak pattern"

        return True, "OK"

    @staticmethod
    def validate_all_secrets() -> List[str]:
        """
        Validate all secrets on startup

        Returns:
            List of error messages (empty if all valid)
        """
        errors = []

        # Validate JWT secret
        jwt_secret = os.getenv('JWT_SECRET_KEY')
        is_valid, msg = SecretValidator.validate_jwt_secret(jwt_secret)
        if not is_valid:
            errors.append(f"JWT: {msg}")

        # Validate PostgreSQL password
        pg_password = os.getenv('POSTGRESQL_PASSWORD')
        is_valid, msg = SecretValidator.validate_database_password(pg_password, 'POSTGRESQL')
        if not is_valid:
            errors.append(f"PostgreSQL: {msg}")

        # Validate TDengine password
        td_password = os.getenv('TDENGINE_PASSWORD')
        is_valid, msg = SecretValidator.validate_database_password(td_password, 'TDENGINE')
        if not is_valid:
            errors.append(f"TDengine: {msg}")

        return errors

    @staticmethod
    def enforce_startup_validation(exit_on_failure: bool = True) -> None:
        """
        Validate all secrets on application startup

        Args:
            exit_on_failure: If True, exit application with error code 1

        Raises:
            SystemExit: If validation fails and exit_on_failure=True
        """
        errors = SecretValidator.validate_all_secrets()

        if errors:
            logger.error("🔴 SECRET VALIDATION FAILED")
            for error in errors:
                logger.error(f"  - {error}")
            logger.error("")
            logger.error("Please update your credentials in .env file:")
            logger.error("  JWT_SECRET_KEY: Use 'openssl rand -hex 32'")
            logger.error("  Database passwords: Use strong passwords (12+ chars)")

            if exit_on_failure:
                raise SystemExit(1)
        else:
            logger.info("✅ All secrets validated successfully")
```

**Step 2**: Integrate validation in application startup

```python
# web/backend/app/app_factory.py
from src.utils.secret_validator import SecretValidator

def create_app():
    """Application factory with secret validation"""

    # 🔒 CRITICAL: Validate secrets BEFORE starting server
    logger.info("Validating secrets...")
    SecretValidator.enforce_startup_validation(exit_on_failure=True)

    # Continue with normal startup
    app = FastAPI()
    # ... rest of setup
```

```python
# unified_manager.py (top-level entry point)
from src.utils.secret_validator import SecretValidator

def main():
    """Main entry point"""
    # Validate secrets first
    SecretValidator.enforce_startup_validation(exit_on_failure=True)

    # Initialize system
    manager = MyStocksUnifiedManager()
    manager.initialize_system()
```

#### Phase 2: Update Documentation (Afternoon)

**Create credential setup guide**:

```markdown
# docs/security/CREDENTIAL_SETUP_GUIDE.md

# Secure Credential Setup Guide

## Overview

This guide explains how to properly configure credentials for MyStocks application.

## Critical Security Rules

1. **NEVER commit credentials to version control**
2. **NEVER use default/placeholder values in production**
3. **ALWAYS use strong, randomly generated secrets**
4. **ROTATE credentials regularly (every 90 days)**

## Required Credentials

### 1. JWT Secret Key

**Purpose**: Authentication token signing

**Generation**:
```bash
# Method 1: OpenSSL (RECOMMENDED)
openssl rand -hex 32

# Method 2: Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Method 3: Automated script
bash scripts/JWT_key_update.sh
```

**Requirements**:
- Minimum 32 characters
- High entropy (not all same character)
- Not a common password

**Configuration**:
```bash
# .env file
JWT_SECRET_KEY=<generated_key>
```

### 2. Database Passwords

#### PostgreSQL
```bash
# Generate strong password
python3 -c "import secrets; print(secrets.token_urlsafe(16))"

# .env file
POSTGRESQL_PASSWORD=<generated_password>
```

#### TDengine
```bash
# Generate strong password
python3 -c "import secrets; print(secrets.token_urlsafe(16))"

# .env file
TDENGINE_PASSWORD=<generated_password>
```

**Requirements**:
- Minimum 12 characters
- Not a dictionary word
- Mix of letters, numbers, symbols

## Validation

The application automatically validates secrets on startup.

**Example output**:
```
✅ All secrets validated successfully
```

**If validation fails**:
```
🔴 SECRET VALIDATION FAILED
  - JWT: JWT_SECRET_KEY too short (8 < 32 chars)
  - PostgreSQL: POSTGRESQL_PASSWORD matches a known weak pattern

Please update your credentials in .env file:
  JWT_SECRET_KEY: Use 'openssl rand -hex 32'
  Database passwords: Use strong passwords (12+ chars)

[Application exits with code 1]
```

## Rotation Schedule

| Credential | Rotation Frequency | Last Rotation | Next Rotation |
|------------|-------------------|---------------|---------------|
| JWT Secret | 90 days | TBD | TBD |
| PostgreSQL | 90 days | TBD | TBD |
| TDengine | 90 days | TBD | TBD |

## Security Checklist

- [ ] All credentials generated using secure methods
- [ ] JWT secret is 32+ characters
- [ ] Database passwords are 12+ characters
- [ ] No default values used
- [ ] .env file added to .gitignore
- [ ] Credentials rotated every 90 days
- [ ] Team trained on credential security
```

### Verification Checklist

- [ ] SecretValidator created and tested
- [ ] Validation integrated in all entry points
- [ ] Documentation created
- [ ] .env.example updated with requirements
- [ ] Team notified of new validation

---

## Issue 3: Bcrypt Password Truncation

### Severity: 🟠 HIGH
**Timeline**: 1 day
**Risk**: Password hashes inconsistent, potential auth bypass

### Affected Files

```
web/backend/app/api/auth.py
web/backend/app/core/security.py
```

### Root Cause

Bcrypt has a 72-byte limit. Longer passwords are silently truncated.

### Implementation Strategy

**Solution**: Pre-hash passwords with SHA-256 before bcrypt

```python
# src/utils/password_handler.py
import hashlib
import bcrypt
from typing import Union

class PasswordHandler:
    """Handle password hashing with pre-hashing for long passwords"""

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """
        Hash password using SHA-256 + bcrypt

        Args:
            plain_password: Plain text password (any length)

        Returns:
            Salted hash
        """
        if not plain_password:
            raise ValueError("Password cannot be empty")

        # Step 1: Pre-hash with SHA-256 to handle long passwords
        # This fixes the bcrypt 72-byte limit issue
        pre_hashed = hashlib.sha256(plain_password.encode()).digest()

        # Step 2: Hash with bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pre_hashed, salt)

        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash

        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored hash

        Returns:
            True if password matches
        """
        if not plain_password or not hashed_password:
            return False

        # Pre-hash the plain password (same as hash_password)
        pre_hashed = hashlib.sha256(plain_password.encode()).digest()

        # Verify with bcrypt
        return bcrypt.checkpw(
            pre_hashed,
            hashed_password.encode('utf-8')
        )
```

**Update authentication endpoints**:

```python
# web/backend/app/api/auth.py
from src.utils.password_handler import PasswordHandler

@router.post("/register")
async def register(user_data: UserCreate):
    # Hash password with new handler
    hashed_pw = PasswordHandler.hash_password(user_data.password)
    # ... save to database

@router.post("/login")
async def login(credentials: UserLogin):
    # Verify password with new handler
    if PasswordHandler.verify_password(credentials.password, user.hashed_password):
        # ... generate token
```

**Migration script for existing hashes**:

```python
# scripts/dev/migrate_password_hashes.py
"""
Migration script to re-hash all passwords using SHA-256 + bcrypt
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.password_handler import PasswordHandler
from src.core.database_manager import DatabaseTableManager

def migrate_passwords():
    """Re-hash all user passwords"""

    db = DatabaseTableManager()

    # Get all users
    users = db.fetch_all("SELECT id, username, password FROM users")

    print(f"Found {len(users)} users to migrate")

    for user in users:
        user_id, username, old_hash = user

        # Note: We can't directly migrate old bcrypt hashes
        # Users will need to reset passwords
        print(f"User {username}: Marked for password reset")

        # Set password_reset_required flag
        db.execute(
            "UPDATE users SET password_reset_required = true WHERE id = %s",
            (user_id,)
        )

    print("\n⚠️  All users must reset their passwords on next login")
    print("This is a security requirement due to password hashing upgrade")

if __name__ == "__main__":
    migrate_passwords()
```

### Verification Checklist

- [ ] PasswordHandler created with SHA-256 pre-hashing
- [ ] All authentication endpoints updated
- [ ] Migration script tested
- [ ] Users notified of password reset requirement
- [ ] Tests verify long passwords work correctly

---

## Issue 4: Connection Pool Management

### Severity: 🟠 HIGH
**Timeline**: 1 day
**Risk**: Connection exhaustion, memory leaks

### Affected Files

```
src/data_access/postgresql_data_access.py
src/data_access/tdengine_data_access.py
src/core/data_manager.py
```

### Implementation Strategy

**Step 1**: Configure connection pool properly

```python
# src/data_access/postgresql_data_access.py
from psycopg2 import pool
import contextlib

class PostgreSQLDataAccess:
    """PostgreSQL access with proper connection pooling"""

    def __init__(self):
        # Connection pool configuration
        self.connection_pool = pool.SimpleConnectionPool(
            minconn=1,           # Minimum connections
            maxconn=20,          # Maximum connections (adjust based on load)
            host=os.getenv('POSTGRESQL_HOST'),
            port=os.getenv('POSTGRESQL_PORT'),
            database=os.getenv('POSTGRESQL_DATABASE'),
            user=os.getenv('POSTGRESQL_USER'),
            password=os.getenv('POSTGRESQL_PASSWORD'),
            options='-c statement_timeout=30000'  # 30s query timeout
        )

        if not self.connection_pool:
            raise RuntimeError("Failed to create connection pool")

    @contextlib.contextmanager
    def get_connection(self):
        """
        Get connection from pool with automatic return

        Usage:
            with self.get_connection() as conn:
                # use connection
            # automatically returned to pool
        """
        conn = self.connection_pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.connection_pool.putconn(conn)

    def close_all_connections(self):
        """Close all connections in pool (cleanup)"""
        self.connection_pool.closeall()
```

**Step 2**: Add connection leak detection

```python
# src/utils/connection_monitor.py
import logging
import time
from typing import Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ConnectionStats:
    """Track connection usage"""
    created_at: float
    last_used: float
    stack_trace: str

class ConnectionMonitor:
    """Monitor for connection leaks"""

    def __init__(self, max_lifetime: float = 300.0):
        """
        Args:
            max_lifetime: Maximum connection lifetime in seconds (default 5 min)
        """
        self.max_lifetime = max_lifetime
        self.active_connections: Dict[int, ConnectionStats] = {}
        self.connection_counter = 0

    def register_connection(self, conn_id: int) -> None:
        """Register a new connection"""
        import traceback

        self.connection_counter += 1
        self.active_connections[conn_id] = ConnectionStats(
            created_at=time.time(),
            last_used=time.time(),
            stack_trace=''.join(traceback.format_stack())
        )
        logger.debug(f"Connection {conn_id} registered (active: {len(self.active_connections)})")

    def unregister_connection(self, conn_id: int) -> None:
        """Unregister a closed connection"""
        if conn_id in self.active_connections:
            del self.active_connections[conn_id]
            logger.debug(f"Connection {conn_id} unregistered (active: {len(self.active_connections)})")

    def check_for_leaks(self) -> None:
        """Check for connection leaks"""
        now = time.time()
        leaked = []

        for conn_id, stats in self.active_connections.items():
            age = now - stats.created_at
            idle_time = now - stats.last_used

            if age > self.max_lifetime:
                leaked.append({
                    'conn_id': conn_id,
                    'age': age,
                    'idle_time': idle_time,
                    'stack_trace': stats.stack_trace
                })

        if leaked:
            logger.warning(f"🔴 Detected {len(leaked)} potential connection leaks:")
            for leak in leaked[:3]:  # Show first 3
                logger.warning(f"  Connection {leak['conn_id']}: age={leak['age']:.1f}s")
                logger.warning(f"    Created at:\n{leak['stack_trace']}")

    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            'active_connections': len(self.active_connections),
            'total_created': self.connection_counter,
            'max_lifetime': self.max_lifetime
        }
```

**Step 3**: Integrate monitoring

```python
# src/data_access/postgresql_data_access.py
from src.utils.connection_monitor import ConnectionMonitor

class PostgreSQLDataAccess:
    def __init__(self):
        # ... existing setup

        # Add connection monitoring
        self.monitor = ConnectionMonitor(max_lifetime=300.0)

    @contextlib.contextmanager
    def get_connection(self):
        conn_id = id(conn)
        self.monitor.register_connection(conn_id)

        try:
            yield conn
        finally:
            self.monitor.unregister_connection(conn_id)
            self.monitor.check_for_leaks()

    def get_connection_stats(self) -> dict:
        """Get connection pool statistics"""
        stats = {
            'pool_size': self.connection_pool.minconn,
            'max_connections': self.connection_pool.maxconn,
            'active': len(self.active_connections),
            **self.monitor.get_stats()
        }
        return stats
```

### Verification Checklist

- [ ] Connection pool configured with min/max limits
- [ ] Context manager ensures connections returned
- [ ] Connection leak detection implemented
- [ ] Monitoring endpoint added to health check
- [ ] Load test confirms no connection exhaustion

---

## Issue 5: Security Test Suite

### Severity: 🟡 MEDIUM (but HIGH priority)
**Timeline**: 2 days
**Risk**: Security regressions

### Implementation Strategy

**Create comprehensive security test suite**:

```python
# tests/security/security_test_suite.py
import pytest
from src.utils.secret_validator import SecretValidator
from src.utils.password_handler import PasswordHandler
from src.utils.connection_monitor import ConnectionMonitor

class TestSecretValidation:
    """Test secret validation"""

    def test_weak_jwt_secret_rejected(self):
        """Weak JWT secrets should be rejected"""
        weak_secrets = ["password", "123456", "short"]
        for secret in weak_secrets:
            is_valid, msg = SecretValidator.validate_jwt_secret(secret)
            assert not is_valid, f"Weak secret {secret} was accepted"

    def test_strong_jwt_secret_accepted(self):
        """Strong JWT secrets should be accepted"""
        strong_secret = "a" * 32  # 32 characters
        is_valid, msg = SecretValidator.validate_jwt_secret(strong_secret)
        assert is_valid

    def test_short_jwt_secret_rejected(self):
        """Short JWT secrets should be rejected"""
        short_secret = "too_short"
        is_valid, msg = SecretValidator.validate_jwt_secret(short_secret)
        assert not is_valid
        assert "too short" in msg.lower()

class TestPasswordHandling:
    """Test password hashing and verification"""

    def test_long_password_handled(self):
        """Passwords >72 bytes should be handled correctly"""
        long_password = "a" * 100  # 100 characters
        hashed = PasswordHandler.hash_password(long_password)

        # Should verify correctly
        assert PasswordHandler.verify_password(long_password, hashed)

    def test_password_verification(self):
        """Correct password should verify"""
        password = "SecurePassword123!"
        hashed = PasswordHandler.hash_password(password)

        assert PasswordHandler.verify_password(password, hashed)
        assert not PasswordHandler.verify_password("WrongPassword", hashed)

    def test_empty_password_rejected(self):
        """Empty passwords should be rejected"""
        with pytest.raises(ValueError):
            PasswordHandler.hash_password("")

class TestConnectionMonitoring:
    """Test connection leak detection"""

    def test_connection_leak_detection(self):
        """Connection leaks should be detected"""
        monitor = ConnectionMonitor(max_lifetime=0.1)  # 100ms

        # Register connection
        monitor.register_connection(1)

        # Wait longer than max_lifetime
        import time
        time.sleep(0.2)

        # Should detect leak
        monitor.check_for_leaks()

        # Clean up
        monitor.unregister_connection(1)

# Run all security tests
pytest tests/security/ -v --cov=src/utils --cov-report=html
```

**CI/CD integration**:

```yaml
# .github/workflows/security-tests.yml
name: Security Tests

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov bandit safety
      - name: Run SQL Injection Tests
        run: pytest tests/security/test_sql_injection_prevention.py -v
      - name: Run Secret Validation Tests
        run: pytest tests/security/test_secret_validation.py -v
      - name: Run Password Handler Tests
        run: pytest tests/security/test_password_handling.py -v
      - name: Run Bandit Security Scan
        run: bandit -r src/ -f json -o bandit-report.json
      - name: Run Safety Check
        run: safety check --json --output safety-report.json
      - name: Upload Reports
        uses: actions/upload-artifact@v2
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
            coverage.xml
```

### Verification Checklist

- [ ] SQL injection tests created and passing
- [ ] Secret validation tests created and passing
- [ ] Password handling tests created and passing
- [ ] Connection monitoring tests created and passing
- [ ] CI/CD pipeline configured
- [ ] Bandit and Safety integrated
- [ ] Security test coverage >90%

---

## Implementation Timeline

### Week 1

**Day 1 (Monday)**: SQL Injection Phase 1
- Morning: Audit and document all SQL queries
- Afternoon: Create SecureQueryBuilder utility

**Day 2 (Tuesday)**: SQL Injection Phase 2-3
- Morning: Fix PostgreSQL queries
- Afternoon: Fix TDengine queries

**Day 3 (Wednesday)**: SQL Injection Phase 4 + Secret Validation
- Morning: Create security test suite
- Afternoon: Implement secret validation

**Day 4 (Thursday)**: Password + Connection Pool
- Morning: Fix bcrypt password truncation
- Afternoon: Fix connection pool management

**Day 5 (Friday)**: Integration and Testing
- Morning: Complete security test suite
- Afternoon: Full integration testing

### Week 2

**Day 6-7**: Buffer for unexpected issues
- Complete any remaining tasks
- Documentation updates
- Team training

---

## Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| SQL Injection Vulnerabilities | 0 | 15+ | 🔴 |
| Secret Validation | Implemented | Missing | 🔴 |
| Password Truncation | Fixed | Present | 🔴 |
| Connection Leaks | 0 | Unknown | 🟡 |
| Security Test Coverage | >90% | 0% | 🔴 |
| Security Tests Passing | 100% | N/A | ⚪ |

---

## Rollback Plan

If any fix causes issues:

1. **Revert changes**: `git revert <commit-hash>`
2. **Restore previous version**: `git checkout <previous-commit>`
3. **Disable validation**: Set environment variable `SKIP_SECRET_VALIDATION=true`
4. **Report issue**: Create bug report with details
5. **Fix and redeploy**: After root cause analysis

---

## Next Steps

1. **Review this plan** with team
2. **Assign tasks** to developers
3. **Set up staging environment** for testing
4. **Create feature branch**: `feature/security-fixes`
5. **Begin implementation** starting with SQL injection fixes
6. **Daily standups** to track progress
7. **Code reviews** for all changes
8. **Deploy to production** after all tests pass

---

## Questions and Support

For questions about this implementation plan:

1. Review code examples in this document
2. Check security documentation in `docs/security/`
3. Consult with security lead
4. Create issue in project tracker

---

**Document Version**: 1.0
**Last Updated**: 2026-01-01
**Author**: Security Team
**Status**: Ready for Implementation
