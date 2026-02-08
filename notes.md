# Notes: Security and Data-Access Remediation

## Sources

### Source 1: Existing review context and prior file reads
- URL: local repository files
- Key points:
  - Redis infrastructure exists and is reusable: `web/backend/app/core/redis_client.py`
  - Redis service wrappers exist: `web/backend/app/services/redis/redis_cache.py`, `web/backend/app/services/redis/redis_lock.py`
  - CSRF tests currently depend on in-memory token map internals and likely require test adjustment.

### Source 2: Target files from prior architecture review
- URL: local repository files
- Key points:
  - SQL query construction risk areas were previously identified in `src/data_access.py` and `src/database/query_executor.py`.
  - Security/config risks were previously identified in `web/backend/app/main.py` and `web/backend/app/core/security.py`.

---

## Precise Issue Map (file:line)

### 1. CORS + Credentials Mismatch (HIGH)
- **File**: `web/backend/app/main.py:291-298`
- **Issue**: `allow_origins=["*"]` combined with `allow_credentials=True` — browsers will reject credentialed requests with wildcard origin. Also a security anti-pattern.
- **Fix**: Replace `allow_origins=["*"]` with `allow_origins=settings.cors_origins` (the commented-out line 294 already has the correct code).

### 2. SQL Injection — TDengine `_build_timeseries_query` (HIGH)
- **File**: `src/data_access.py:579-627`
- **Issue**: String interpolation for `symbol`, `start_time`, `end_time`, `date_range` values directly into SQL. Lines 597-614 use f-string `'{value}'` patterns.
- **Note**: TDengine driver may not support `%s` parameterization the same way. Minimum fix: validate/sanitize inputs against allowlist patterns (e.g., stock symbol regex `^[A-Z0-9.]{1,20}$`, ISO date format).

### 3. SQL Injection — TDengine `_handle_tdengine_first_wins` (HIGH)
- **File**: `src/data_access.py:374-388`
- **Issue**: `symbols_str = "','".join(symbols)` then interpolated into SQL. Same f-string pattern.
- **Fix**: Same sanitization approach as #2.

### 4. SQL Injection — `query_executor.py` `get_stock_detail` (MEDIUM)
- **File**: `src/database/query_executor.py:90`
- **Issue**: `query = f"SELECT * FROM stock_details WHERE symbol = '{stock_code}'"` — direct string interpolation.
- **Note**: Currently this is a mock executor (returns hardcoded data, `_execute_query` doesn't hit real DB). Risk is LOW now but HIGH if connected to real DB later.
- **Fix**: Parameterize or add input validation.

### 5. In-Memory Revoked Token Set (MEDIUM)
- **File**: `web/backend/app/core/security.py:127-138`
- **Issue**: `_revoked_tokens = set()` — lost on restart, not shared across workers.
- **Fix**: Migrate to Redis using existing `redis_client.py` singleton. Use `SADD`/`SISMEMBER` with TTL matching token expiry.

### 6. In-Memory CSRF Token Storage (MEDIUM)
- **File**: `web/backend/app/main.py:55-99`
- **Issue**: `self.tokens = {}` — same restart/multi-worker problem as #5.
- **Fix**: Migrate to Redis. Use `HSET`/`HGET` with TTL. Keep same public API (`generate_token`, `validate_token`, `cleanup_expired_tokens`).
- **Test Impact**: `web/backend/tests/test_csrf_protection.py` — 10+ direct accesses to `csrf_manager.tokens` dict (lines 32, 41, 87, 106, 110, 119, 127, 136, 137, 145, 146, 390, 411, 557). Must update tests to use public API or mock Redis.

### 7. Sensitive Data in Logs (MEDIUM)
- **File**: `web/backend/app/core/security.py:226-227`
- **Issue**: `print(f"[Mock Auth] Input password: {password}")` and `print(f"[Mock Auth] Stored hash: {user_in_db.hashed_password}")` — plaintext password and hash logged.
- **Fix**: Remove these two print statements entirely.

### 8. Unreachable Dead Code (LOW)
- **File**: `web/backend/app/core/security.py:193-231`
- **Issue**: Code after `return _authenticate_with_mock(username, password)` on line 191 is unreachable. Lines 193-231 contain a second fallback block with hardcoded passwords that can never execute.
- **Fix**: Delete the unreachable block (lines 193-231).

### 9. Duplicate `except` / Unreachable Code in `authenticate_user_by_id` (LOW)
- **File**: `web/backend/app/core/security.py:252-281`
- **Issue**: First `except` on line 252 catches `Exception`, then has unreachable mock_users code after `return None` (line 255). Second `except Exception` on line 278 is also unreachable.
- **Fix**: Remove the dead code block (lines 256-281), keep only the first except with `return None`.

### 10. Password Reset Token Logged (LOW)
- **File**: `web/backend/app/api/auth.py:559`
- **Issue**: `print(f"Password reset token for {user.email}: {reset_token}")` — reset token in logs.
- **Fix**: Replace with `logger.debug(...)` or remove entirely.

### 11. No Default LIMIT on TDengine Queries (LOW)
- **File**: `src/data_access.py:622-627`
- **Issue**: `_build_timeseries_query` only adds LIMIT if explicitly passed in kwargs. No default cap.
- **Fix**: Add `DEFAULT_QUERY_LIMIT = 10000` fallback when no limit specified.

---

## Existing Secure Patterns to Reuse

### PostgreSQL Parameterized Queries (ALREADY DONE)
- `src/data_access.py:1129-1340` — `_build_analytical_query` uses `%s` placeholders, table whitelist, ORDER BY column whitelist. **Excellent pattern.**
- `src/data_access.py:1342-1385` — `_build_delete_query` same pattern.
- `src/data_access.py:1094-1127` — `_execute_update` uses `%s` parameterization.

### Redis Singleton
- `web/backend/app/core/redis_client.py` — `RedisManager` singleton with connection pool, health check, context manager. Ready to use.

### Config-Driven CORS
- `web/backend/app/core/config.py:69-77` — `cors_origins` property already parses `CORS_ORIGINS` env var into list. Just needs to be uncommented in `main.py`.

---

## Minimal Patch Scope

| # | File | Change | Risk |
|---|------|--------|------|
| 1 | `web/backend/app/main.py:293` | Uncomment `settings.cors_origins`, remove `["*"]` | LOW |
| 2 | `src/data_access.py:579-627` | Add input sanitization for TDengine query builder | MED |
| 3 | `src/data_access.py:374-388` | Add input sanitization for first_wins symbols | MED |
| 4 | `src/database/query_executor.py:90` | Parameterize stock_code in query | LOW |
| 5 | `web/backend/app/core/security.py:127-138` | Migrate revoked tokens to Redis | MED |
| 6 | `web/backend/app/main.py:55-99` | Migrate CSRF tokens to Redis | MED |
| 7 | `web/backend/app/core/security.py:226-227` | Remove password/hash logging | LOW |
| 8 | `web/backend/app/core/security.py:193-231` | Delete unreachable code block | LOW |
| 9 | `web/backend/app/core/security.py:252-281` | Delete unreachable duplicate except | LOW |
| 10 | `web/backend/app/api/auth.py:559` | Remove/downgrade reset token log | LOW |
| 11 | `src/data_access.py:622` | Add default LIMIT fallback | LOW |
| 12 | `web/backend/tests/test_csrf_protection.py` | Update tests for Redis-backed CSRF | MED |

## Out of Scope
- Large-file decomposition/refactor tasks explicitly deferred by user.
- Pickle deserialization in `redis_cache.py` (separate concern).
- Frontend `innerHTML` XSS (separate concern).
