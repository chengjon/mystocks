# Research & Technical Decisions
**Feature**: Fix All Broken Web Features
**Branch**: `003-fix-all-broken`
**Date**: 2025-10-25

## Overview

This document consolidates all technical research and decision-making for fixing 35 broken features in the MyStocks web application. All decisions are based on the comprehensive code review report and existing codebase analysis.

---

## Research Topic 1: Database Migration Strategy (MySQL → PostgreSQL)

### Problem Statement

Five market data tables currently depend on MySQL but need to migrate to PostgreSQL to complete the Week 3 database simplification initiative:
1. `fund_flow` (资金流向)
2. `etf_data` (ETF数据)
3. `dragon_tiger` (龙虎榜)
4. `chip_race` (竞价抢筹)
5. `indicator_configs` (指标配置)

### Options Evaluated

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **A. Manual SQL Migration** | Simple, direct control | Breaks configuration-driven architecture, error-prone | ❌ Rejected |
| **B. Update table_config.yaml + ConfigDrivenTableManager** | Follows architecture principles, versioned, auditable | Requires config validation | ✅ **SELECTED** |
| **C. Keep MySQL** | No migration effort | Violates dual-database architecture, adds complexity | ❌ Rejected |

### Decision: Option B - Configuration-Driven Migration

**Rationale**:
- Complies with constitution's "配置驱动原则" (Configuration-Driven Principle)
- Ensures single source of truth for schema definitions
- Provides automatic rollback capability via Git
- Maintains consistency across dev/test/prod environments

**Implementation**:
1. Add 5 table definitions to `table_config.yaml`
2. Mark database_target as "postgresql"
3. Use `ConfigDrivenTableManager.batch_create_tables()`
4. Export existing MySQL data → Import to PostgreSQL
5. Update API endpoints to use PostgreSQL connections

**Data Preservation**:
- MySQL data exported as JSON/CSV before migration
- Import validation with row count verification
- Fallback plan: Keep MySQL read-only for 2 weeks post-migration

---

## Research Topic 2: E2E Testing Tool Selection

### Problem Statement

Need automated browser testing for:
- Dashboard real data display
- Market data panel interactions
- Authentication flows
- Error handling scenarios

### Options Evaluated

| Tool | Pros | Cons | Decision |
|------|------|------|----------|
| **Puppeteer MCP** | MCP integration, headless Chrome control | Node-focused | ⚠️  Available |
| **Playwright MCP** | Cross-browser, modern API, MCP integration | Heavier setup | ⚠️  Available |
| **chrome-devtools-mcp** | Direct DevTools integration, lightweight | Chrome-only | ✅ **PREFERRED** |

### Decision: chrome-devtools-mcp (Primary) with Playwright (Fallback)

**Rationale**:
- chrome-devtools-mcp provides direct access to Chrome DevTools Protocol
- MCP integration allows AI-driven test execution
- Lightweight and fast for rapid iteration
- Playwright available if cross-browser testing needed later

**Test Strategy**:
1. **Unit Tests** (70%): Jest/Vitest for component logic
2. **Integration Tests** (20%): API endpoint validation with pytest
3. **E2E Tests** (10%): chrome-devtools-mcp for critical user flows

**Critical E2E Scenarios**:
- Login → Dashboard (real data) → Refresh
- Navigate to Market Data → Load Dragon-Tiger List
- Create indicator → Save → Retrieve from database
- Session timeout → Auto-refresh → Continue work

---

## Research Topic 3: Error Handling Pattern

### Problem Statement

Current errors are user-hostile:
- "NameError: name 'db_service' is not defined"
- MySQL connection errors shown to end users
- "undefined is not a function" in frontend

### Options Evaluated

| Pattern | Pros | Cons | Decision |
|---------|------|------|----------|
| **A. Catch-all try/except** | Simple | Hides root causes, hard to debug | ❌ Rejected |
| **B. Structured error classes + user messages** | Clean separation, debuggable | More code | ✅ **SELECTED** |
| **C. Status code only** | RESTful | Poor user experience | ❌ Rejected |

### Decision: Option B - Structured Error Handling

**Implementation**:

**Backend** (Python/FastAPI):
```python
# Define error classes
class UserFriendlyError(Exception):
    def __init__(self, user_message: str, technical_details: str):
        self.user_message = user_message
        self.technical_details = technical_details

# Global exception handler
@app.exception_handler(Exception)
async def handle_errors(request, exc):
    logger.error(f"Error: {exc}", exc_info=True)  # Log technical details

    if isinstance(exc, UserFriendlyError):
        return JSONResponse({
            "error": exc.user_message,
            "request_id": request_id
        }, status_code=500)

    return JSONResponse({
        "error": "An unexpected error occurred. Please try again.",
        "request_id": request_id
    }, status_code=500)
```

**Frontend** (Vue/Axios):
```javascript
// Axios interceptor
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.data?.error) {
      // Show user-friendly message
      ElMessage.error(error.response.data.error)
    } else {
      // Generic fallback
      ElMessage.error('Network error. Please check your connection.')
    }
    return Promise.reject(error)
  }
)
```

**User Messages Map**:
- Database connection failed → "Unable to load data. Please try again in a moment."
- db_service undefined → "Data service temporarily unavailable. Our team has been notified."
- Session expired → "Your session has expired. Please log in again."

---

## Research Topic 4: Authentication Token Refresh Strategy

### Problem Statement

Users experience unexpected logouts due to:
- No automatic token refresh
- Short token expiration (30 minutes)
- Poor session state management

### Options Evaluated

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **A. Long-lived tokens** | No refresh needed | Security risk | ❌ Rejected |
| **B. Refresh token pattern** | Industry standard, secure | Complex implementation | ✅ **SELECTED** |
| **C. Session extension on activity** | User-friendly | Doesn't scale with stateless auth | ❌ Rejected |

### Decision: Option B - Refresh Token Pattern with Auto-Renewal

**Implementation**:

**Backend**:
```python
@router.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    # Validate refresh token
    payload = verify_refresh_token(refresh_token)

    # Generate new access token
    new_access_token = create_access_token(
        data={"sub": payload["sub"]},
        expires_delta=timedelta(minutes=30)
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": 1800
    }
```

**Frontend** (Pinia store):
```javascript
export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null,
    refreshToken: null,
    tokenExpiresAt: null
  }),

  actions: {
    async refreshAccessToken() {
      try {
        const response = await axios.post('/api/auth/refresh', {
          refresh_token: this.refreshToken
        })

        this.accessToken = response.data.access_token
        this.tokenExpiresAt = Date.now() + (response.data.expires_in * 1000)

        // Schedule next refresh (5 minutes before expiration)
        this.scheduleTokenRefresh()
      } catch (error) {
        // Refresh failed, redirect to login
        this.logout()
        router.push('/login')
      }
    },

    scheduleTokenRefresh() {
      const timeUntilRefresh = this.tokenExpiresAt - Date.now() - (5 * 60 * 1000)
      setTimeout(() => this.refreshAccessToken(), timeUntilRefresh)
    }
  }
})
```

**Token Lifetimes**:
- Access token: 30 minutes
- Refresh token: 7 days
- Auto-refresh: 5 minutes before expiration

---

## Research Topic 5: Placeholder Page Strategy

### Problem Statement

Four major pages are empty placeholders:
- Market.vue
- BacktestAnalysis.vue
- RiskMonitor.vue
- RealTimeMonitor.vue

### Options Evaluated

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **A. Implement all features** | Complete product | Scope creep, 64-104 hours | ❌ Out of scope |
| **B. Remove routes entirely** | Clean codebase | Poor UX (404 errors) | ❌ Rejected |
| **C. Keep pages with clear "Coming Soon" UI** | Honest, good UX | Pages remain incomplete | ✅ **SELECTED** |

### Decision: Option C - Professional Placeholder Pages

**Implementation**:

```vue
<template>
  <div class="placeholder-page">
    <el-empty description="This feature is coming soon">
      <template #image>
        <i class="el-icon-box" style="font-size: 100px; color: #909399"></i>
      </template>

      <template #description>
        <h2>{{ featureName }} - Coming Soon</h2>
        <p>This feature is currently under development.</p>
        <p>In the meantime, try these alternatives:</p>
      </template>

      <el-button type="primary" @click="navigateToAlternative">
        {{ alternativeFeature }}
      </el-button>
    </el-empty>
  </div>
</template>
```

**Alternative Workflows**:
- Market.vue → MarketData.vue (working market panels)
- BacktestAnalysis.vue → StrategyManagement.vue (strategy results)
- RiskMonitor.vue → RealTimeMonitor.vue (real-time metrics)
- RealTimeMonitor.vue → Dashboard.vue (overview metrics)

**Navigation Menu Updates**:
- Add badge: `<el-badge value="Soon" type="info">`
- Grey out menu items
- Show tooltip: "Coming in next release"

---

## Research Topic 6: db_service Implementation Pattern

### Problem Statement

`app/api/data.py` references `db_service` which doesn't exist in `app/core/database.py`, causing `NameError`.

### Options Evaluated

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **A. Create db_service singleton** | Quick fix | Doesn't follow existing patterns | ❌ Rejected |
| **B. Use MyStocksUnifiedManager** | Architecture-compliant | Requires refactoring | ✅ **SELECTED** |
| **C. Direct database access** | Simple | Breaks layered architecture | ❌ Rejected |

### Decision: Option B - Integrate MyStocksUnifiedManager

**Rationale**:
- `MyStocksUnifiedManager` is the existing unified data access layer
- Provides automatic routing between PostgreSQL and TDengine
- Includes built-in caching and monitoring integration
- Follows established architecture patterns

**Implementation**:

```python
# app/core/database.py
from core.unified_manager import MyStocksUnifiedManager

# Create singleton instance
_unified_manager = None

def get_unified_manager() -> MyStocksUnifiedManager:
    global _unified_manager
    if _unified_manager is None:
        _unified_manager = MyStocksUnifiedManager(enable_cache=True)
    return _unified_manager

# For backwards compatibility
db_service = get_unified_manager()
```

**Usage in APIs**:
```python
# app/api/data.py
from app.core.database import get_unified_manager

@router.get("/stocks/basic")
async def get_stocks_basic():
    manager = get_unified_manager()
    stocks = manager.load_data(
        classification=DataClassification.REFERENCE_DATA,
        table_name="stocks_basic"
    )
    return stocks.to_dict('records')
```

---

## Key Technology Decisions Summary

| Decision Area | Choice | Justification |
|---------------|--------|---------------|
| **Database Migration** | Configuration-driven (table_config.yaml) | Architecture compliance, auditability |
| **E2E Testing** | chrome-devtools-mcp | MCP integration, lightweight, AI-driven |
| **Error Handling** | Structured errors + user messages | User experience + debuggability |
| **Token Refresh** | Refresh token pattern | Security + seamless UX |
| **Placeholder Pages** | "Coming Soon" UI + alternatives | Honest communication, good UX |
| **db_service Fix** | MyStocksUnifiedManager integration | Architecture compliance |

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Data loss during migration** | Low | High | Export backup, row count validation, 2-week fallback period |
| **Token refresh bugs** | Medium | Medium | Comprehensive E2E tests, manual QA before deployment |
| **E2E test flakiness** | Medium | Low | Retry mechanism, stable selectors, wait strategies |
| **Breaking working features** | Low | High | Follow code modification rules, regression test suite |

---

## References

- [Comprehensive Code Review Report](../../COMPREHENSIVE_CODE_REVIEW_REPORT.md)
- [Code Modification Rules](../../代码修改规则-new.md)
- [Project Constitution](../../.specify/memory/constitution.md)
- [Feature Specification](./spec.md)
