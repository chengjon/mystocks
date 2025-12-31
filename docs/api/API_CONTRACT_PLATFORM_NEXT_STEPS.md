# API Contract Platform - Status & Enhanced Action Plan

**Document Version**: 2.0
**Last Updated**: 2025-12-30
**Status**: Ready for Implementation

---

## 📚 Background & Context

For complete context on the platform setup and error fixes, see:
- **Deployment Report**: `docs/api/API_CONTRACT_PLATFORM_DEPLOYMENT_REPORT.md` - Detailed error fixes and platform setup
- **Integration Strategy**: `docs/api/API_WEB_INTEGRATION_STRATEGY.md` - Complete frontend integration guide

---

## ✅ Completed Actions (P0 Priorities)

### 1. CLI Tool Bug Fix

**Issue**: The `api-contract-sync list` command failed with:
```
AttributeError: 'list' object has no attribute 'get'
```

**Root Cause**: CLI expected dictionary (UnifiedResponse) but API returned list.

**Fix Applied**:
- Updated `scripts/cli/api_contract_sync.py` line 227
- Added robust handling for both list and UnifiedResponse formats
- Added defensive programming: check `isinstance(result, list)` before processing

**Status**: ✅ **Fixed & Verified**

**Verification**:
```bash
python3 scripts/cli/api_contract_sync.py list --name market-data
# Now works correctly
```

---

### 2. TypeScript Type Generation

**Goal**: Generate TypeScript definitions from the `market-data` OpenAPI contract.

**Action Executed**:
```bash
cd web/frontend
npx openapi-typescript ../docs/api/openapi/market-data-api.yaml -o src/types/market-data-api.ts
```

**Result**: Created `web/frontend/src/types/market-data-api.ts` with:
- ✅ All 6 API endpoint types
- ✅ Request/response interfaces
- ✅ Full type safety with generics
- ✅ Properly nested schemas

**Status**: ✅ **Completed**

**Quality Metrics**:
- Type definitions: 15+ interfaces
- Endpoints covered: 6/6 (100%)
- Compilation: ✅ No errors

---

## 🚀 P1 Action Plan: Frontend Integration

**Objective**: Connect the Frontend Dashboard to the new Contract-Based API architecture.

**Total Estimated Time**: ~2 hours
**Dependencies**: Backend API running → TypeScript types → Service → Adapter → Composable → Dashboard

### Implementation Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│                   Prerequisites                             │
│  ✓ Backend API running (http://localhost:8000)             │
│  ✓ TypeScript types generated (market-data-api.ts)          │
│  ✓ Frontend dev server ready (http://localhost:3020)        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Service Layer (~30 min)                             │
│  Create: web/frontend/src/services/api/marketService.ts      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Adapter Layer (~20 min)                             │
│  Create: web/frontend/src/services/adapters/marketAdapter.ts│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Composable (~30 min)                                │
│  Create: web/frontend/src/composables/useMarketData.ts      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Dashboard Integration (~40 min)                      │
│  Update: web/frontend/src/views/Dashboard.vue               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📖 Available TypeScript Types

**Generated File**: `web/frontend/src/types/market-data-api.ts`

### Core Type Definitions

```typescript
// API Response Wrapper
export interface APIResponse<T> {
  success: boolean;
  code: number;
  message: string;
  data: T;
  request_id: string;
  timestamp: string;
}

// Domain Models
export interface MarketOverviewData {
  market_index: Record<string, number>;
  turnover_rate: number;
  up_down_ratio: number;
  limit_up_count: number;
  limit_down_count: number;
}

export interface FundFlowData {
  main_net_inflow: number;
  main_net_inflow_rate: number;
  retail_net_inflow: number;
  institutional_net_inflow: number;
  timeframe: string;
}

export interface KlineData {
  symbol: string;
  interval: string;
  data: Array<{
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
}

export interface ETFData {
  etf_list: Array<{
    symbol: string;
    name: string;
    price: number;
    change_rate: number;
  }>;
}

export interface LonghubangData {
  date: string;
  items: Array<{
    symbol: string;
    name: string;
    buy_amount: number;
    sell_amount: number;
    net_amount: number;
  }>;
}

export interface ChipRaceData {
  date: string;
  data: Array<{
    symbol: string;
    price: number;
    volume: number;
    amount: number;
  }>;
}
```

### Usage Example

```typescript
import type { MarketOverviewData, APIResponse } from '@/types/market-data-api';

// Type-safe API call
const response: APIResponse<MarketOverviewData> = await marketService.getMarketOverview();

// TypeScript will validate:
// - response.data exists
// - response.data has correct MarketOverviewData structure
// - All required fields are present
```

---

## 🔨 Detailed Implementation Steps

### Step 1: Create Service Layer (~30 minutes)

**File**: `web/frontend/src/services/api/marketService.ts`

**Description**: A typed API client using the generated TypeScript interfaces.

**Key Features**:
- Strictly typed return values matching `MarketDataAPI`
- Axios interceptors for error handling
- Environment-based configuration
- Request/response logging

**Success Criteria**:
- ✅ All 6 market-data endpoints implemented
- ✅ TypeScript compilation passes without errors
- ✅ Axios interceptors configured for error handling
- ✅ Base URL configurable via environment variable
- ✅ Proper error type handling
- **Verification**: `npm run type-check` passes

**Implementation Outline**:
```typescript
import axios from 'axios';
import type {
  MarketOverviewData,
  FundFlowData,
  KlineData,
  ETFData,
  LonghubangData,
  ChipRaceData,
  APIResponse
} from '@/types/market-data-api';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class MarketApiService {
  private client = axios.create({
    baseURL: API_BASE,
    timeout: 10000,
  });

  constructor() {
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('[API Error]', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  async getMarketOverview(): Promise<MarketOverviewData> {
    const response = await this.client.get<APIResponse<MarketOverviewData>>(
      '/api/market/overview'
    );
    return response.data.data;
  }

  async getFundFlow(timeframe: string = '1d'): Promise<FundFlowData> {
    const response = await this.client.get<APIResponse<FundFlowData>>(
      '/api/market/fund-flow',
      { params: { timeframe } }
    );
    return response.data.data;
  }

  // ... 4 more methods
}

export const marketService = new MarketApiService();
```

**Testing**:
```bash
# TypeScript compilation check
cd web/frontend
npm run type-check

# Manual browser console test
import { marketService } from '@/services/api/marketService';
marketService.getMarketOverview().then(data => console.log('✅ API works:', data));
```

---

### Step 2: Create Adapter Layer (~20 minutes)

**File**: `web/frontend/src/services/adapters/marketAdapter.ts`

**Description**: A transformation layer to convert API responses into UI-friendly formats.

**Key Features**:
- Null-safety and default value handling
- Data formatting for display
- Fallback to mock data if API fails
- Type guards for runtime validation

**Success Criteria**:
- ✅ Adapter handles null/undefined API responses
- ✅ Default values prevent UI crashes
- ✅ Data formatting (numbers, dates, percentages)
- ✅ Mock data fallback implemented
- ✅ Type guards validate data structure
- **Verification**: Unit tests cover null cases

**Implementation Outline**:
```typescript
import type {
  MarketOverviewData,
  FundFlowData,
  KlineData
} from '@/types/market-data-api';

// Mock data fallbacks (import from existing mock files)
import { mockMarketOverview } from '@/mock/marketData';

export class MarketDataAdapter {
  /**
   * Adapt market overview with null-safety
   */
  static adaptMarketOverview(
    apiData: MarketOverviewData | null,
    mockFallback?: MarketOverviewData
  ): MarketOverviewData {
    if (!apiData || Object.keys(apiData).length === 0) {
      console.warn('[MarketAdapter] API data empty, using fallback');
      return mockFallback || mockMarketOverview;
    }

    return {
      market_index: apiData.market_index || {},
      turnover_rate: apiData.turnover_rate || 0,
      up_down_ratio: apiData.up_down_ratio || 0,
      limit_up_count: apiData.limit_up_count || 0,
      limit_down_count: apiData.limit_down_count || 0,
    };
  }

  /**
   * Format percentage for display
   */
  static formatPercentage(value: number, decimals: number = 2): string {
    if (isNaN(value)) return '0.00%';
    return `${(value * 100).toFixed(decimals)}%`;
  }

  /**
   * Format large numbers (e.g., 1234567 → 1.23M)
   */
  static formatNumber(value: number): string {
    if (isNaN(value)) return '0';
    if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
    if (value >= 1_000) return `${(value / 1_000).toFixed(2)}K`;
    return value.toString();
  }

  // ... more adapters
}
```

**Testing**:
```typescript
// Test null handling
const emptyData = null;
const adapted = MarketDataAdapter.adaptMarketOverview(emptyData);
console.assert(adapted.market_index !== undefined, '✅ Null-safety works');
```

---

### Step 3: Create Composable (~30 minutes)

**File**: `web/frontend/src/composables/useMarketData.ts`

**Description**: A Vue 3 Composition API hook for managing market data state.

**Key Features**:
- Encapsulated loading, error, and data state management
- Reactive computed properties
- Automatic refetch on interval (optional)
- Caching to reduce API calls

**Success Criteria**:
- ✅ Loading state managed correctly
- ✅ Error state captured and exposed
- ✅ Data is reactive (Vue ref/computed)
- ✅ Composable can be reused across components
- ✅ Optional auto-refresh functionality
- **Verification**: Integration test in Vue DevTools

**Implementation Outline**:
```typescript
import { ref, computed, onMounted } from 'vue';
import { marketService } from '@/services/api/marketService';
import { MarketDataAdapter } from '@/services/adapters/marketAdapter';
import type { MarketOverviewData } from '@/types/market-data-api';

export function useMarketData(autoRefresh = false, refreshInterval = 30000) {
  // State
  const overview = ref<MarketOverviewData | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  let refreshTimer: NodeJS.Timeout | null = null;

  // Computed properties
  const marketIndices = computed(() => overview.value?.market_index || {});
  const turnoverRate = computed(() => overview.value?.turnover_rate || 0);
  const formattedTurnoverRate = computed(() =>
    MarketDataAdapter.formatPercentage(turnoverRate.value)
  );

  // Actions
  const fetchMarketOverview = async (forceRefresh = false) => {
    // Prevent duplicate calls
    if (loading.value && !forceRefresh) return;

    loading.value = true;
    error.value = null;

    try {
      const apiData = await marketService.getMarketOverview();
      overview.value = MarketDataAdapter.adaptMarketOverview(apiData);
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取数据失败';
      console.error('[useMarketData] Failed to fetch overview:', err);
    } finally {
      loading.value = false;
    }
  };

  const startAutoRefresh = () => {
    if (refreshTimer) clearInterval(refreshTimer);
    refreshTimer = setInterval(() => {
      fetchMarketOverview(true);
    }, refreshInterval);
  };

  const stopAutoRefresh = () => {
    if (refreshTimer) {
      clearInterval(refreshTimer);
      refreshTimer = null;
    }
  };

  // Lifecycle
  onMounted(() => {
    fetchMarketOverview();
    if (autoRefresh) {
      startAutoRefresh();
    }
  });

  onUnmounted(() => {
    stopAutoRefresh();
  });

  return {
    // State
    overview,
    loading,
    error,
    // Computed
    marketIndices,
    turnoverRate,
    formattedTurnoverRate,
    // Actions
    fetchMarketOverview,
    startAutoRefresh,
    stopAutoRefresh,
  };
}
```

**Testing**:
```vue
<script setup lang="ts">
import { useMarketData } from '@/composables/useMarketData';

const {
  overview,
  loading,
  error,
  fetchMarketOverview,
} = useMarketData();

// Test in Vue DevTools console
window.__MARKET_DATA__ = { overview, loading, error, fetchMarketOverview };
</script>
```

---

### Step 4: Dashboard Integration (~40 minutes)

**File**: `web/frontend/src/views/Dashboard.vue`

**Description**: Refactor the main dashboard to use the new `useMarketData` composable.

**Key Features**:
- Replace legacy `dataApi` calls with contract-driven flow
- Display loading, error, and empty states
- Show real-time market data with proper formatting
- Add error boundary for graceful degradation

**Success Criteria**:
- ✅ Dashboard loads without console errors
- ✅ Market overview data displays correctly
- ✅ Loading states show during API calls
- ✅ Error states display user-friendly messages
- ✅ Empty states handled gracefully
- ✅ Legacy `dataApi` calls removed
- **Verification**: Manual test in browser + Vue DevTools

**Implementation Outline**:
```vue
<script setup lang="ts">
import { onMounted } from 'vue';
import { useMarketData } from '@/composables/useMarketData';

const {
  overview,
  loading,
  error,
  marketIndices,
  formattedTurnoverRate,
  fetchMarketOverview,
} = useMarketData(autoRefresh = true);

onMounted(() => {
  console.log('[Dashboard] Mounted, fetching data...');
});
</script>

<template>
  <div class="dashboard">
    <!-- Loading State -->
    <div v-if="loading" class="state loading">
      <div class="spinner"></div>
      <p>加载市场数据中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="state error">
      <h3>⚠️ 数据加载失败</h3>
      <p>{{ error }}</p>
      <button @click="fetchMarketOverview(true)">重试</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="!overview" class="state empty">
      <p>暂无市场数据</p>
    </div>

    <!-- Data Display -->
    <div v-else class="market-overview">
      <h2>市场概览</h2>

      <!-- Market Indices -->
      <section class="indices">
        <h3>主要指数</h3>
        <div class="index-grid">
          <div
            v-for="(value, key) in marketIndices"
            :key="key"
            class="index-item"
          >
            <span class="label">{{ key }}:</span>
            <span class="value">{{ value?.toFixed(2) || '---' }}</span>
          </div>
        </div>
      </section>

      <!-- Statistics -->
      <section class="statistics">
        <div class="stat-card">
          <label>换手率</label>
          <span class="value">{{ formattedTurnoverRate }}</span>
        </div>

        <div class="stat-card">
          <label>涨跌比</label>
          <span class="value">{{ overview?.up_down_ratio?.toFixed(2) || '---' }}</span>
        </div>

        <div class="stat-card">
          <label>涨停数</label>
          <span class="value up">{{ overview?.limit_up_count || 0 }}</span>
        </div>

        <div class="stat-card">
          <label>跌停数</label>
          <span class="value down">{{ overview?.limit_down_count || 0 }}</span>
        </div>
      </section>

      <!-- Last Update -->
      <p class="last-update">
        最后更新: {{ new Date().toLocaleTimeString() }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.state {
  padding: 2rem;
  text-align: center;
}

.loading .spinner {
  /* ... */
}

.error {
  color: #e74c3c;
}

.error button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.index-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.index-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.value.up {
  color: #e74c3c;
}

.value.down {
  color: #27ae60;
}
</style>
```

---

## 🧪 Testing Strategy

### Step 1: Service Layer Testing

```bash
# TypeScript compilation
cd web/frontend
npm run type-check

# Expected: No errors
# ✓ All imports resolve correctly
# ✓ Type annotations match generated types
```

**Manual Browser Console Test**:
```javascript
// Open browser console (F12) on http://localhost:3020
import { marketService } from '@/services/api/marketService';
marketService.getMarketOverview().then(data => {
  console.log('✅ API Response:', data);
  console.assert(data.market_index !== undefined, 'Market data exists');
});
```

---

### Step 2: Adapter Testing

```typescript
// Test null-safety
const testCases = [
  { input: null, expected: 'fallback_data' },
  { input: { market_index: {} }, expected: 'defaults_applied' },
  { input: undefined, expected: 'fallback_data' },
];

testCases.forEach(({ input, expected }) => {
  const result = MarketDataAdapter.adaptMarketOverview(input);
  console.assert(result !== null, `${expected}: ✅ No crashes`);
});
```

---

### Step 4: Dashboard Integration Testing

**Verification Checklist**:
- [ ] Dashboard loads at http://localhost:3020 without errors
- [ ] Console shows no TypeScript errors
- [ ] Network tab shows API call to `/api/market/overview`
- [ ] API returns 200 with data
- [ ] Market indices display with correct values
- [ ] Loading spinner shows before data arrives
- [ ] Error state shows if API fails (test by stopping backend)
- [ ] Refresh happens every 30 seconds (if auto-refresh enabled)

**Load Backend**:
```bash
# Ensure backend is running
curl http://localhost:8000/health
# Expected: {"success":true,...}
```

**Start Frontend**:
```bash
cd web/frontend
npm run dev
# Navigate to http://localhost:3020
```

**Test Scenarios**:
1. **Normal Flow**: Dashboard loads → Loading state → Data displays → Auto-refresh works
2. **Error Handling**: Stop backend → Error message appears → Click retry → Backend restarts → Data loads
3. **Edge Cases**: Refresh page quickly → Multiple requests → No duplicate calls (debouncing)

---

## ⚠️ Risk Mitigation

### Potential Risks & Mitigation Strategies

| Risk | Probability | Impact | Mitigation Strategy | Contingency Plan |
|------|-------------|--------|---------------------|------------------|
| **CORS errors on API calls** | Medium | High | • Verify backend CORS config includes frontend origin<br>• Set `Access-Control-Allow-Origin: http://localhost:3020`<br>• Configure credentials if needed | • Temporarily disable CORS in dev<br>• Use proxy in vite.config.js |
| **TypeScript type mismatches** | Low | Medium | • Use strict type checking<br>• Enable `noImplicitAny` in tsconfig.json<br>• Fix types in generation step | • Use `// @ts-ignore` temporarily<br>• File issue with type generation tool |
| **Network errors during dev** | Low | Low | • Implement retry logic in service<br>• Add timeout handling<br>• Show user-friendly error messages | • Fall back to mock data automatically<br>• Add offline detection |
| **Component re-render issues** | Low | Medium | • Use `shallowRef` for large objects<br>• Implement proper memoization<br>• Optimize computed properties | • Simplify component structure<br>• Debug with Vue DevTools performance tab |
| **API contract changes** | Medium | Medium | • Version contracts properly<br>• Document breaking changes<br>• Update types on contract change | • Pin specific contract version<br>• Run contract diff tool |
| **Environment variable issues** | Low | High | • Document all required env vars<br>• Provide `.env.example` template<br>• Validate on startup | • Use sensible defaults<br>• Show clear error if missing |
| **Mock data outdated** | Medium | Low | • Keep mock data in sync with API<br>• Add validation scripts<br>• Document mock data format | • Use API data directly<br>• Update mock when contract changes |

---

## 📅 P2 Action Plan: Expansion (Upcoming)

### 1. Trade Module Repair
**Priority**: Medium
**Estimated Time**: 2-3 hours
**Dependencies**: None

**Tasks**:
- Fix generic typing issues in `APIResponse`
- Re-enable trade module in `app/main.py`
- Verify trade endpoints work correctly
- Add trade contract to platform

### 2. Contract Expansion
**Priority**: High
**Estimated Time**: 1-2 hours per API module
**Dependencies**: Trade module fixed

**Tasks**:
- Register `technical-analysis` API (6 endpoints)
- Register `strategy-management` API (8 endpoints)
- Register `trading` API (after repair)
- Generate TypeScript types for all contracts
- Update CLI documentation

### 3. CI/CD Automation
**Priority**: Low
**Estimated Time**: 3-4 hours
**Dependencies**: Contract expansion in progress

**Tasks**:
- Implement Git pre-commit hook for type generation
- Add contract validation to CI pipeline
- Automatic contract versioning on merge
- Deploy documentation updates

---

## 📊 Progress Tracking

### Overall Status

- [x] P0: Platform Setup (100% - Completed)
- [ ] P1: Frontend Integration (0% - In Progress)
  - [ ] Step 1: Service Layer
  - [ ] Step 2: Adapter Layer
  - [ ] Step 3: Composable
  - [ ] Step 4: Dashboard Integration
- [ ] P2: Expansion (0% - Pending)

### Time Tracking

| Phase | Estimated | Actual | Status |
|-------|-----------|--------|--------|
| P0 | 4 hours | 5 hours | ✅ Complete |
| P1 | 2 hours | TBD | 🔄 In Progress |
| P2 | 6-9 hours | TBD | ⏳ Pending |

---

## 🎯 Success Criteria for P1 Completion

The P1 phase will be considered successful when:

1. ✅ **All TypeScript compiles** - `npm run type-check` passes with zero errors
2. ✅ **Dashboard displays live data** - Market overview shows real values from backend API
3. ✅ **Error handling works** - Stopping backend shows user-friendly error message
4. ✅ **Loading states work** - Spinner shows during data fetch
5. ✅ **Auto-refresh functions** - Data updates every 30 seconds automatically
6. ✅ **No legacy code remains** - Old `dataApi` calls removed from Dashboard

---

## 🚀 Ready to Start

**Prerequisites Verified**:
- ✅ Backend API running: `http://localhost:8000`
- ✅ Contract registered: `market-data v1.0.0`
- ✅ TypeScript types generated: `market-data-api.ts`
- ✅ Frontend dev server ready: `npm run dev`

**Question**: Shall I proceed with **Step 1: Creating the marketService.ts**?

---

**Document Authors**: Main CLI + User
**Last Review**: 2025-12-30
**Next Review**: After P1 completion
