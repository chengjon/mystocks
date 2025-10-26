# Implementation Plan: Market Data UI/UX Improvements

**Branch**: `004-ui-short-name` | **Date**: 2025-10-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ui-short-name/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements 5 UI/UX improvements to the market data pages:
1. **Fund Flow Page (P1)**: Add fixed table headers, pagination (10-100 items), zebra striping, industry name hyperlinks, and trend chart integration
2. **ETF & Dragon Tiger Pages (P2)**: Add fixed headers, pagination, and zebra striping for large datasets
3. **System Font Settings (P3)**: Global font size adjustment with 5 levels (12-20px), Typography font family, 1.5 line-height
4. **Wencai Filter (P3)**: Restore 9 default query presets (qs_1 to qs_9) with result panel integration
5. **Watchlist Restructure (P2)**: Rename "Stock Management" to "Watchlist", implement tab-based layout (User/System/Strategy/Monitor), fixed headers, group highlighting

**Technical Approach**: Pure frontend Vue 3 component enhancements using Element Plus UI library, ECharts for trend visualization, CSS position:sticky for fixed headers, and LocalStorage/backend for user preference persistence.

## Technical Context

**Language/Version**:
- Frontend: JavaScript/TypeScript with Vue 3 (Composition API)
- Backend: Python 3.11+ with FastAPI (minimal backend changes)

**Primary Dependencies**:
- **Frontend**: Vue 3.3+, Element Plus 2.4+, ECharts 5.4+, Pinia (state management), Vue Router
- **Backend**: FastAPI, PostgreSQL (psycopg2), existing market data APIs
- **Build Tools**: Vite 4+, TypeScript 5+

**Storage**:
- **User Preferences**: LocalStorage (primary) with optional backend persistence to PostgreSQL user_preferences table
- **Market Data**: Existing PostgreSQL database (no schema changes required)
- **Query Presets**: Configuration file or database table (qs_1 to qs_9 definitions)

**Testing**:
- **Frontend**: Vitest (unit tests), Playwright (E2E for user scenarios)
- **Backend**: pytest (if API enhancements needed)
- **Visual Testing**: Manual testing for UI/UX validation

**Target Platform**: Modern web browsers (Chrome 90+, Firefox 88+, Edge 90+, Safari 14+)

**Project Type**: Web application (existing frontend + backend structure)

**Performance Goals**:
- Trend chart update: <500ms after industry click (SC-001)
- Font size change: <200ms visual update (SC-003)
- Tab switching: <300ms (SC-005)
- Page load: <2s for ETF/Dragon Tiger with fixed headers (SC-004)
- Query result update: <1s for Wencai filter (SC-006)

**Constraints**:
- **Browser Compatibility**: Must support CSS position:sticky (no IE11 support required per spec)
- **Responsive Design**: Mobile devices (<768px) may use alternative fixed header implementation
- **Font Size Range**: 12px-20px only (prevent layout breakage)
- **Pagination Range**: 10-100 items per page (prevent performance issues)
- **No Backend Schema Changes**: Work with existing API responses
- **Backward Compatibility**: Existing features must continue to work

**Scale/Scope**:
- **Components Modified**: 5-7 Vue components (FundFlowPanel, ETFTable, LongHuBangTable, WencaiFilter, StockManagement, SystemSettings)
- **New Components**: 2-3 (TrendChart, FontSizeSetting, TabWatchlist)
- **API Endpoints**: 1 new endpoint (fund flow historical trend data), optional preferences API
- **User Base**: ~100-1000 users (internal/small-scale application)
- **Data Volume**: Up to 1000 items per page (ETF data), pagination mitigates performance impact

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### 1. Configuration-Driven Principle ✅ **PASS**

**Requirement**: System parameters must be configuration-managed, separating business logic from configuration data.

**Compliance**:
- ✅ Font size settings (5 levels) will be stored in user preferences (LocalStorage/backend)
- ✅ Pagination defaults (10-100 range) will be configurable
- ✅ Wencai query presets (qs_1 to qs_9) will be configuration-driven (JSON/YAML or database)
- ✅ Tab labels and watchlist groups configurable
- ✅ No hardcoded values in business logic

**Evidence**: FR-019 requires persistent user preferences; FR-021 requires preset query configuration

### 2. Data Classification Storage Principle ✅ **PASS**

**Requirement**: Choose optimal storage based on data characteristics and access patterns.

**Compliance**:
- ✅ **User Preferences** (font size, pagination) → LocalStorage (high-speed read/write, temporary) with optional PostgreSQL backup
- ✅ **Market Data** (fund flow, ETF, dragon tiger) → PostgreSQL (existing, no changes)
- ✅ **Query Presets** → Configuration file or PostgreSQL (reference data)
- ✅ No inappropriate storage choices

**Evidence**: Technical Context specifies LocalStorage for preferences, PostgreSQL for data

### 3. Layered Architecture Principle ✅ **PASS**

**Requirement**: Strict layer separation with single-direction dependencies.

**Compliance**:
- ✅ **Presentation Layer**: Vue components (FundFlowPanel, ETFTable, etc.)
- ✅ **Service Layer**: API calls via dataApi wrapper (existing)
- ✅ **Storage Layer**: PostgreSQL for data, LocalStorage for preferences
- ✅ No cross-layer dependencies (components → services → storage)

**Evidence**: Vue components will use composables/services, not direct API calls

### 4. Smart Routing Principle ⚠️ **N/A - Frontend Feature**

**Requirement**: Auto-route data operations based on classification.

**Compliance**:
- ⚠️ This principle applies to backend data routing; this feature is primarily frontend UI/UX
- ✅ User preferences will be routed correctly (LocalStorage first, optional backend sync)

**Evidence**: No backend data routing changes required

### 5. Complete Observability Principle ⚠️ **PARTIAL**

**Requirement**: Performance monitoring, data quality, business metrics, audit logging.

**Compliance**:
- ✅ Frontend performance tracking (chart update times, page load metrics)
- ⚠️ User interaction logging (font changes, tab switches) - **should be added**
- ⚠️ Data quality monitoring for chart data - **should be added**
- ❌ No formal audit logging planned

**Action Required**: Add console logging for user preferences changes, track chart load failures

### 6. Security & Fault Tolerance Principle ✅ **PASS**

**Requirement**: Input validation, error handling, graceful degradation.

**Compliance**:
- ✅ Font size validation (12-20px range enforcement, FR-014)
- ✅ Pagination validation (10-100 range, FR-010)
- ✅ Null-safety checks for chart data (defensive programming)
- ✅ Graceful degradation (if chart fails, table still works)
- ✅ Fallback for position:sticky (mobile alternative)

**Evidence**: FR-014, FR-016, FR-020 specify validation and responsive behavior

---

### Overall Gate Status: ✅ **PASS WITH MINOR RECOMMENDATIONS**

**Summary**:
- 5/6 principles fully compliant
- 1 principle (Observability) partially compliant - recommend adding user interaction logging
- No blocking violations
- Proceed to Phase 0 research

**Recommendations**:
1. Add user interaction logging for font size changes, tab switches, pagination adjustments
2. Track chart load performance and failures
3. Consider optional backend sync for user preferences (already planned)

## Project Structure

### Documentation (this feature)

```
specs/004-ui-short-name/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (ECharts integration, CSS sticky, font best practices)
├── data-model.md        # Phase 1 output (user preferences entity)
├── quickstart.md        # Phase 1 output (how to test features)
├── contracts/           # Phase 1 output (optional API contracts)
├── checklists/
│   └── requirements.md  # Spec quality validation (completed)
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

**Web Application Structure**: This project follows Option 2 (frontend + backend)

```
web/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── market_v3.py         # Existing market data APIs
│   │   │   ├── dashboard.py         # Dashboard endpoints
│   │   │   └── preferences.py       # NEW: User preferences API (optional)
│   │   ├── models/
│   │   │   └── user_preferences.py  # NEW: Preferences model (optional)
│   │   └── main.py                  # FastAPI application
│   └── tests/
│       └── api/                     # API tests (if new endpoints added)
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── market/
    │   │   │   ├── FundFlowPanel.vue      # MODIFIED: Add pagination, fixed header, trend chart
    │   │   │   ├── FundFlowTrendChart.vue # NEW: Industry trend chart component
    │   │   │   ├── ETFTable.vue           # MODIFIED: Add pagination, fixed header
    │   │   │   ├── LongHuBangTable.vue    # MODIFIED: Add pagination, fixed header
    │   │   │   └── WencaiFilter.vue       # MODIFIED: Restore qs_1-qs_9 presets
    │   │   ├── stock/
    │   │   │   └── WatchlistTabs.vue      # NEW: Tab-based watchlist (replaces StockManagement)
    │   │   └── settings/
    │   │       └── FontSizeSetting.vue    # NEW: Global font size control
    │   ├── composables/
    │   │   ├── useUserPreferences.ts      # NEW: User preferences management
    │   │   └── usePagination.ts           # NEW: Reusable pagination logic
    │   ├── stores/
    │   │   └── preferences.ts             # NEW: Pinia store for user preferences
    │   ├── styles/
    │   │   ├── typography.css             # NEW: Font family and size variables
    │   │   └── table-common.css           # NEW: Shared fixed header, zebra stripe styles
    │   ├── utils/
    │   │   └── logger.ts                  # MODIFIED: Add user interaction logging
    │   ├── config/
    │   │   └── wencai-queries.json        # NEW: qs_1 to qs_9 query definitions
    │   └── views/
    │       ├── MarketData.vue             # MODIFIED: Use new components
    │       ├── Watchlist.vue              # RENAMED: From StockManagement.vue
    │       └── Settings.vue               # MODIFIED: Add font size setting
    └── tests/
        ├── unit/
        │   └── components/                # Component unit tests
        └── e2e/
            └── ui-ux-scenarios.spec.ts    # NEW: E2E tests for 5 user stories
```

**Structure Decision**:
- **Backend Changes**: Minimal (1 optional API endpoint for user preferences persistence)
- **Frontend Changes**: Moderate (5-7 modified components, 2-3 new components)
- **Shared Utilities**: New composables for pagination and preferences management
- **Configuration**: Wencai query presets in JSON file
- **Testing**: E2E tests for all 5 user stories (P1-P3)

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**Status**: ✅ **NO VIOLATIONS**

All constitution principles passed or are N/A. No complexity justifications required.

**Minor Recommendations** (not violations):
- Add user interaction logging for observability (already planned in implementation)
- Track chart load performance (part of performance monitoring requirements)
