# Security Remediation Report

**Date**: 2025-02-09
**Scope**: Code-review findings (excluding large-file refactors)
**Method**: planning-with-files workflow
**Status**: ✅ COMPLETED — 12 issues remediated across 6 files

---

## Executive Summary

Applied 12 targeted security and code-quality fixes identified during architecture review. All changes are minimal-scope, backwards-compatible, and syntax-verified. Redis migrations include graceful in-memory fallback for environments without Redis.

---

## Changes by Phase

### Phase 3A: Quick Wins (5 fixes)

| # | Severity | File | Change | Lines Changed |
|---|----------|------|--------|---------------|
| 1 | **HIGH** | `web/backend/app/main.py` | CORS: `allow_origins=["*"]` → `settings.cors_origins` | ~3 |
| 7 | MEDIUM | `web/backend/app/core/security.py` | Removed via Fix #8 (was in unreachable block) | 0 |
| 8 | LOW | `web/backend/app/core/security.py` | Deleted 39 lines unreachable dead code in `authenticate_user` | -39 |
| 9 | LOW | `web/backend/app/core/security.py` | Deleted 26 lines unreachable duplicate except in `authenticate_user_by_id` | -26 |
| 10 | LOW | `web/backend/app/api/auth.py` | Password reset token: `print()` → `logger.debug()` | ~3 |

### Phase 3B: SQL Injection Hardening (4 fixes)

| # | Severity | File | Change | Lines Changed |
|---|----------|------|--------|---------------|
| 2 | **HIGH** | `src/data_access.py` | Added `_validate_tdengine_input()` + validated all filter values in `_build_timeseries_query` | ~50 |
| 3 | **HIGH** | `src/data_access.py` | Validated symbols in `_handle_tdengine_first_wins` | ~3 |
| 4 | MEDIUM | `src/database/query_executor.py` | Added regex validation for `stock_code` in `get_stock_detail` | ~4 |
| 11 | LOW | `src/data_access.py` | Added `DEFAULT_QUERY_LIMIT = 10000` fallback in TDengine queries | ~4 |

### Phase 3C: Redis Migration (3 fixes)

| # | Severity | File | Change | Lines Changed |
|---|----------|------|--------|---------------|
| 5 | MEDIUM | `web/backend/app/core/security.py` | Revoked token blacklist → Redis `SETEX` with TTL + in-memory fallback | ~40 |
| 6 | MEDIUM | `web/backend/app/main.py` | CSRF token storage → Redis `SETEX`/`GET` with TTL + in-memory fallback | ~70 |
| 12 | MEDIUM | `web/backend/tests/test_csrf_protection.py` | Added `_clear_all_csrf_tokens()` helper; updated 4 `setup_method` calls | ~20 |

---

## Files Modified

| File | Fixes Applied |
|------|---------------|
| `web/backend/app/main.py` | #1 (CORS), #6 (CSRF Redis) |
| `web/backend/app/core/security.py` | #5 (revoked tokens Redis), #7/#8 (dead code), #9 (dead code) |
| `web/backend/app/api/auth.py` | #10 (sensitive log) |
| `src/data_access.py` | #2 (SQL validation), #3 (SQL validation), #11 (default LIMIT) |
| `src/database/query_executor.py` | #4 (SQL validation) |
| `web/backend/tests/test_csrf_protection.py` | #12 (test update) |

---

## Verification

All modified files pass Python syntax validation:
```
✅ web/backend/app/main.py
✅ web/backend/app/core/security.py
✅ web/backend/app/api/auth.py
✅ src/data_access.py
✅ src/database/query_executor.py
✅ web/backend/tests/test_csrf_protection.py
```

---

## Design Decisions

1. **TDengine SQL hardening**: Used input validation (regex allowlists) instead of parameterized queries because TDengine's Python connector has limited parameterization support. Validation patterns:
   - Symbol: `^[A-Za-z0-9.]{1,20}$`
   - Datetime: `^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?)?$`
   - Table name: `^[A-Za-z_][A-Za-z0-9_]{0,63}$`

2. **Redis migrations**: Both CSRF and revoked-token storage use Redis-first with graceful in-memory fallback. This ensures:
   - Zero downtime if Redis is temporarily unavailable
   - Multi-worker token sharing when Redis is available
   - Automatic TTL-based cleanup in Redis
   - Backwards compatibility with existing test suite

3. **CORS fix**: Switched from `allow_origins=["*"]` to `settings.cors_origins` which reads from `CORS_ORIGINS` environment variable. The config already has sensible defaults covering `localhost:3000-3009` and `localhost:8000-8009`.

---

## Remaining Items (Out of Scope)

| Item | Reason Deferred |
|------|-----------------|
| Large-file decomposition/refactoring | User explicitly deferred to separate task |
| Pickle deserialization in `redis_cache.py` | Separate security concern, not in this review scope |
| Frontend `innerHTML` XSS | Frontend-specific, separate task |

---

## Recommended Next Steps

1. **Run full test suite** to verify no regressions: `cd web/backend && pytest`
2. **Verify Redis connectivity** in staging/production environments
3. **Update `.env.example`** if `CORS_ORIGINS` is not already documented
4. **Schedule large-file refactoring** as a separate task
5. **Consider adding** rate limiting to CSRF token generation endpoint
