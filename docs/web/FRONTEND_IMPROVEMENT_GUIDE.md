# MyStocks Frontend - Practical Improvement Guide

## Actionable Code Examples for Priority Improvements

---

## Table of Contents
1. [TypeScript Improvements](#1-typescript-improvements)
2. [Testing Examples](#2-testing-examples)
3. [Accessibility Fixes](#3-accessibility-fixes)
4. [State Management](#4-state-management)
5. [Performance Optimization](#5-performance-optimization)
6. [Component Best Practices](#6-component-best-practices)

---

## 1. TypeScript Improvements

### 1.1 Enable Strict Mode Incrementally

**Phase 1: Enable noImplicitAny**

Update `tsconfig.json`:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,        // Enable first
    "strictNullChecks": false,    // Keep disabled for now
    "strictFunctionTypes": false,
    "strictBindCallApply": false,
    "strictPropertyInitialization": false,
    "alwaysStrict": false
  }
}
```

**Fix common errors:**

Before:
```typescript
function updateChart(data) {  // Implicit any
  return data.map(item => item.value)
}
```

After:
```typescript
function updateChart(data: Array<{ value: number }>): number[] {
  return data.map(item => item.value)
}
```

**Phase 2: Enable strictNullChecks**

```typescript
// Before
function getPrice(stock: Stock): number {
  return stock.price  // Could be undefined
}

// After
function getPrice(stock: Stock): number {
  if (!stock.price) {
    throw new Error(`Price not available for ${stock.symbol}`)
  }
  return stock.price
}

// Or use optional chaining
function getPrice(stock: Stock): number | undefined {
  return stock?.price
}
```

### 1.2 Type-Safe Props with Composition API

**Before:**
```vue
<script setup>
const props = defineProps({
  title: String,
  count: Number,
  active: Boolean
})
</script>
```

**After:**
```vue
<script setup lang="ts">
interface Props {
  title: string
  count?: number  // Optional
  active: boolean
}

const props = withDefaults(defineProps<Props>(), {
  count: 0,
  active: false
})
</script>
```

### 1.3 Type-Safe Emits

**Before:**
```vue
<script setup>
const emit = defineEmits(['update', 'delete'])

function handleClick() {
  emit('update', 123)  // Wrong type, no error
}
</script>
```

**After:**
```vue
<script setup lang="ts">
interface Emits {
  (e: 'update', id: number): void
  (e: 'delete', id: number, reason: string): void
}

const emit = defineEmits<Emits>()

function handleClick() {
  emit('update', 123)  // Type-checked
}
</script>
```

### 1.4 Generic Components

**Create reusable typed components:**

```vue
<!-- DataTable.vue -->
<script setup lang="ts" generic="T extends { id: string | number }">
interface Props {
  data: T[]
  columns: Column<T>[]
  selectable?: boolean
}

interface Column<T> {
  key: keyof T
  label: string
  formatter?: (value: T[keyof T]) => string
}

const props = withDefaults(defineProps<Props<T>>(), {
  selectable: false
})

const emit = defineEmits<{
  (e: 'row-click', row: T): void
  (e: 'selection-change', selected: T[]): void
}>()
</script>
```

---

## 2. Testing Examples

### 2.1 Component Unit Test (Vitest)

**Test file: Dashboard.spec.ts**
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import Dashboard from '@/views/Dashboard.vue'
import { useMarket } from '@/composables/useMarket'

// Mock composable
vi.mock('@/composables/useMarket')

describe('Dashboard.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const mountDashboard = () => {
    return mount(Dashboard, {
      global: {
        plugins: [createPinia()],
        stubs: {
          'el-card': true,
          'el-row': true,
          'el-col': true,
          'smart-data-indicator': true
        }
      }
    })
  }

  it('renders page title and subtitle', () => {
    const wrapper = mountDashboard()
    expect(wrapper.find('.page-title').text()).toBe('仪表盘')
    expect(wrapper.find('.page-subtitle').text()).toBe('实时市场概览与投资组合监控')
  })

  it('displays 4 stat cards', () => {
    const wrapper = mountDashboard()
    const cards = wrapper.findAll('.stat-card')
    expect(cards).toHaveLength(4)
  })

  it('fetches market data on mount', async () => {
    const mockFetchMarketOverview = vi.fn()
    vi.mocked(useMarket).mockReturnValue({
      marketOverview: ref(null),
      fetchMarketOverview: mockFetchMarketOverview,
      loading: ref(false)
    } as any)

    mountDashboard()
    await flushPromises()

    expect(mockFetchMarketOverview).toHaveBeenCalledWith(true)
  })

  it('displays loading state correctly', () => {
    vi.mocked(useMarket).mockReturnValue({
      marketOverview: ref(null),
      fetchMarketOverview: vi.fn(),
      loading: ref(true)
    } as any)

    const wrapper = mountDashboard()
    expect(wrapper.find('.loading-indicator').exists()).toBe(true)
  })

  it('formats percentage changes correctly', async () => {
    vi.mocked(useMarket).mockReturnValue({
      marketOverview: ref({
        marketStats: {
          risingStocks: 1234,
          fallingStocks: 567,
          totalStocks: 2000
        }
      }),
      fetchMarketOverview: vi.fn(),
      loading: ref(false)
    } as any)

    const wrapper = mountDashboard()
    await flushPromises()

    const risingStocks = wrapper.find('[data-testid="rising-stocks"]')
    expect(risingStocks.text()).toContain('1234')
  })
})
```

### 2.2 Composable Test

**Test file: useMarket.spec.ts**
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useMarket } from '@/composables/useMarket'
import { marketApiService } from '@/api/services/marketService'
import { MarketAdapter } from '@/api/adapters/marketAdapter'

vi.mock('@/api/services/marketService')
vi.mock('@/api/adapters/marketAdapter')

describe('useMarket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Clear cache
    const cache = getCache('market-api')
    cache.clear()
  })

  it('fetches market overview successfully', async () => {
    const mockData = {
      success: true,
      data: {
        market_index: { '上证指数': 3200 },
        market_stats: {
          total_stocks: 5000,
          rising_stocks: 2500,
          falling_stocks: 2000
        }
      }
    }

    vi.mocked(marketApiService.getMarketOverview).mockResolvedValue(mockData)
    vi.mocked(MarketAdapter.adaptMarketOverview).mockReturnValue({
      marketIndex: { '上证指数': 3200 },
      marketStats: {
        totalStocks: 5000,
        risingStocks: 2500,
        fallingStocks: 2000
      }
    })

    const { fetchMarketOverview, marketOverview, error } = useMarket()

    await fetchMarketOverview()

    expect(marketOverview.value).toBeDefined()
    expect(marketOverview.value?.marketIndex).toEqual({ '上证指数': 3200 })
    expect(error.value).toBeNull()
  })

  it('uses cached data on second call', async () => {
    const mockData = { success: true, data: {} }
    vi.mocked(marketApiService.getMarketOverview).mockResolvedValue(mockData)
    vi.mocked(MarketAdapter.adaptMarketOverview).mockReturnValue({})

    const { fetchMarketOverview, marketOverview } = useMarket()

    // First call
    await fetchMarketOverview()
    expect(marketApiService.getMarketOverview).toHaveBeenCalledTimes(1)

    // Second call (should use cache)
    await fetchMarketOverview()
    expect(marketApiService.getMarketOverview).toHaveBeenCalledTimes(1) // No new call
  })

  it('handles API errors gracefully', async () => {
    vi.mocked(marketApiService.getMarketOverview).mockRejectedValue(
      new Error('Network error')
    )

    const { fetchMarketOverview, error } = useMarket()

    await fetchMarketOverview()

    expect(error.value).toContain('获取市场概览失败')
  })
})
```

### 2.3 E2E Test (Playwright)

**Test file: dashboard.spec.ts**
```typescript
import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard')
  })

  test('loads successfully', async ({ page }) => {
    await expect(page).toHaveTitle(/MyStocks/)
    await expect(page.locator('.page-title')).toContainText('仪表盘')
  })

  test('displays market statistics', async ({ page }) => {
    await page.waitForSelector('.stat-card')
    const cards = page.locator('.stat-card')
    await expect(cards).toHaveCount(4)

    await expect(cards.nth(0)).toContainText('总股票数')
    await expect(cards.nth(1)).toContainText('总市值')
  })

  test('navigates to market data page', async ({ page }) => {
    await page.click('text=资金流向')
    await expect(page).toHaveURL(/\/market-data\/fund-flow/)
  })

  test('refreshes data on button click', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("刷新")')
    await refreshButton.click()

    // Verify loading state
    await expect(page.locator('.loading-indicator')).toBeVisible()
    await expect(page.locator('.loading-indicator')).toBeHidden()
  })

  test('displays charts correctly', async ({ page }) => {
    await page.waitForSelector('[data-testid="market-heat-chart"]')

    const chart = page.locator('[data-testid="market-heat-chart"]')
    await expect(chart).toBeVisible()

    // Switch to different tab
    await page.click('text=领涨板块')
    await expect(page.locator('[data-testid="leading-sector-chart"]')).toBeVisible()
  })
})
```

---

## 3. Accessibility Fixes

### 3.1 Add ARIA Labels to Icon Buttons

**Before:**
```vue
<el-icon @click="toggleSidebar">
  <Fold />
</el-icon>
```

**After:**
```vue
<button
  class="sidebar-toggle"
  aria-label="Toggle navigation menu"
  :aria-expanded="isCollapsed ? 'false' : 'true'"
  aria-controls="sidebar-menu"
  @click="toggleSidebar"
>
  <el-icon>
    <Fold v-if="!isCollapsed" />
    <Expand v-else />
  </el-icon>
</button>
```

### 3.2 Accessible Form Inputs

**Before:**
```vue
<el-input v-model="searchQuery" placeholder="搜索股票" />
```

**After:**
```vue
<div class="form-group">
  <label for="stock-search" class="visually-hidden">
    搜索股票代码或名称
  </label>
  <el-input
    id="stock-search"
    v-model="searchQuery"
    placeholder="输入股票代码或名称"
    aria-describedby="search-help"
  />
  <span id="search-help" class="help-text">
    支持拼音缩写，如 "zgpa" 表示 "中国平安"
  </span>
</div>
```

### 3.3 Accessible Charts (ECharts)

```vue
<template>
  <div>
    <div
      ref="chartRef"
      role="img"
      :aria-label="chartAriaLabel"
      tabindex="0"
      @keydown="handleChartKeydown"
    ></div>
    <!-- Screen reader only description -->
    <div class="sr-only" aria-live="polite">
      {{ chartDescription }}
    </div>
  </div>
</template>

<script setup lang="ts">
const chartAriaLabel = computed(() => {
  return `上证指数走势图，当前点位 ${currentValue}，涨跌幅 ${changePercent}%`
})

const chartDescription = computed(() => {
  return `上证指数今日开盘 ${openPrice}，最高 ${highPrice}，最低 ${lowPrice}，收盘 ${closePrice}`
})

const handleChartKeydown = (event: KeyboardEvent) => {
  // Implement keyboard navigation for chart
  if (event.key === 'ArrowRight') {
    // Navigate to next data point
  } else if (event.key === 'ArrowLeft') {
    // Navigate to previous data point
  }
}
</script>
```

### 3.4 Color Contrast Fixes

**Current (fails WCAG):**
```scss
--color-text-secondary: #8b949e;  // Contrast: ~4.4:1 on dark background
```

**Fixed (passes WCAG AA):**
```scss
--color-text-secondary: #b0b6c0;  // Contrast: ~5.2:1 on dark background
```

**Visual hierarchy maintained with opacity:**
```scss
.text-primary {
  color: var(--color-text-primary);  // Full opacity
}

.text-secondary {
  color: var(--color-text-primary);
  opacity: 0.75;  // Better than dark color
}

.text-tertiary {
  color: var(--color-text-primary);
  opacity: 0.5;
}
```

### 3.5 Skip Navigation Link

```vue
<!-- App.vue -->
<template>
  <div id="app">
    <!-- Skip to main content (visible on focus) -->
    <a href="#main-content" class="skip-link">
      跳转到主要内容
    </a>

    <router-view />
  </div>
</template>

<style>
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary);
  color: white;
  padding: 8px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
</style>
```

---

## 4. State Management

### 4.1 Create Market Store

**File: stores/market.ts**
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { marketApiService } from '@/api/services/marketService'
import { MarketAdapter } from '@/api/adapters/marketAdapter'
import type { MarketOverviewVM } from '@/api/types/market'

export const useMarketStore = defineStore('market', () => {
  // State
  const overview = ref<MarketOverviewVM | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetchTime = ref<number | null>(null)

  // Getters
  const marketIndex = computed(() => overview.value?.marketIndex || {})
  const marketStats = computed(() => overview.value?.marketStats || null)
  const isStale = computed(() => {
    if (!lastFetchTime.value) return true
    const age = Date.now() - lastFetchTime.value
    return age > 5 * 60 * 1000  // 5 minutes
  })

  // Actions
  async function fetchOverview(forceRefresh = false) {
    // Return cached data if fresh
    if (!forceRefresh && overview.value && !isStale.value) {
      return overview.value
    }

    loading.value = true
    error.value = null

    try {
      const response = await marketApiService.getMarketOverview()
      const vm = MarketAdapter.adaptMarketOverview(response)

      overview.value = vm
      lastFetchTime.value = Date.now()

      return vm
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearOverview() {
    overview.value = null
    lastFetchTime.value = null
  }

  return {
    // State
    overview,
    loading,
    error,
    lastFetchTime,

    // Getters
    marketIndex,
    marketStats,
    isStale,

    // Actions
    fetchOverview,
    clearOverview
  }
})
```

### 4.2 Create UI Store

**File: stores/ui.ts**
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export type Theme = 'light' | 'dark'

export const useUIStore = defineStore('ui', () => {
  // Sidebar state
  const sidebarCollapsed = ref(false)
  const sidebarMobileOpen = ref(false)

  // Theme
  const theme = ref<Theme>('dark')

  // Notifications
  const notifications = ref<Notification[]>([])

  // Loading states
  const globalLoading = ref(false)
  const loadingMessage = ref('')

  // Actions
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setSidebarCollapsed(collapsed: boolean) {
    sidebarCollapsed.value = collapsed
  }

  function toggleMobileSidebar() {
    sidebarMobileOpen.value = !sidebarMobileOpen.value
  }

  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }

  function addNotification(notification: Notification) {
    notifications.value.push({
      ...notification,
      id: Date.now(),
      timestamp: new Date()
    })

    // Auto-remove after 5 seconds
    setTimeout(() => {
      removeNotification(notification.id!)
    }, 5000)
  }

  function removeNotification(id: number) {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  function setGlobalLoading(loading: boolean, message = '') {
    globalLoading.value = loading
    loadingMessage.value = message
  }

  // Initialize theme from localStorage
  function initTheme() {
    const savedTheme = localStorage.getItem('theme') as Theme | null
    if (savedTheme) {
      setTheme(savedTheme)
    }
  }

  return {
    // State
    sidebarCollapsed,
    sidebarMobileOpen,
    theme,
    notifications,
    globalLoading,
    loadingMessage,

    // Actions
    toggleSidebar,
    setSidebarCollapsed,
    toggleMobileSidebar,
    setTheme,
    addNotification,
    removeNotification,
    setGlobalLoading,
    initTheme
  }
})
```

### 4.3 Use Stores in Components

**Before (component-level state):**
```vue
<script setup>
const isCollapsed = ref(false)
const username = ref('Admin')

function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
}
</script>
```

**After (using stores):**
```vue
<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'

const uiStore = useUIStore()
const authStore = useAuthStore()

// Use storeToRefs to keep reactivity
const { sidebarCollapsed, theme } = storeToRefs(uiStore)
const { username } = storeToRefs(authStore)

// Actions can be destructured directly
const { toggleSidebar, setTheme } = uiStore
</script>
```

---

## 5. Performance Optimization

### 5.1 Manual Chunk Splitting

**Update vite.config.ts:**
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],

  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vue ecosystem
          'vue-vendor': ['vue', 'vue-router', 'pinia'],

          // UI library
          'element-plus': ['element-plus'],
          'element-icons': ['@element-plus/icons-vue'],

          // Charts (lazy load)
          'charts-core': ['echarts/core'],
          'charts-charts': ['echarts/charts'],
          'charts-components': ['echarts/components'],
          'klinecharts': ['klinecharts'],

          // Utilities
          'utils': ['axios', 'dayjs', 'lodash-es', 'technicalindicators']
        }
      }
    },

    // Optimize chunk size warning threshold
    chunkSizeWarningLimit: 500
  }
})
```

### 5.2 Lazy Load Charts

**Before:**
```typescript
import * as echarts from 'echarts'  // Loads all charts (~500KB)
```

**After:**
```typescript
// Lazy load specific chart types
import type { EChartsOption } from 'echarts'
import { useAsyncData } from '@vueuse/core'

const loadECharts = async () => {
  const [
    { init },
    { BarChart, LineChart },
    { TitleComponent, TooltipComponent, GridComponent }
  ] = await Promise.all([
    import('echarts/core'),
    import('echarts/charts'),
    import('echarts/components')
  ])

  return { init, BarChart, LineChart, TitleComponent, TooltipComponent, GridComponent }
}

// In component
const { data: echarts, pending: loadingCharts } = useAsyncData(loadECharts)
```

### 5.3 Optimize Element Plus Imports

**Before:**
```typescript
import ElementPlus from 'element-plus'
app.use(ElementPlus)  // Imports entire library
```

**After (auto-import with unplugin-vue-components):**
```typescript
// vite.config.ts
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    Components({
      resolvers: [ElementPlusResolver()]
    })
  ]
})

// No need to import ElementPlus in main.js
// Components are auto-imported and tree-shaken
```

### 5.4 Virtual Scrolling for Large Lists

**Use el-table with virtual scrolling:**
```vue
<template>
  <el-table
    :data="largeDataList"
    height="600"
    :virtual-scroll="true"
    :row-height="50"
  >
    <el-table-column prop="symbol" label="代码" width="100" />
    <el-table-column prop="name" label="名称" width="120" />
    <!-- ... -->
  </el-table>
</template>
```

### 5.5 Image Optimization

```vue
<script setup lang="ts">
// Lazy load images
const imageLoaded = ref(false)

function handleImageLoad() {
  imageLoaded.value = true
}
</script>

<template>
  <img
    :src="imageSrc"
    :alt="imageAlt"
    loading="lazy"
    @load="handleImageLoad"
    :class="{ loaded: imageLoaded }"
  />
</template>

<style scoped>
img {
  opacity: 0;
  transition: opacity 0.3s;
}

img.loaded {
  opacity: 1;
}
</style>
```

---

## 6. Component Best Practices

### 6.1 Single Responsibility Principle

**Before (large component):**
```vue
<!-- Dashboard.vue - 547 lines, does too much -->
<script setup>
// Handles data fetching
// Handles chart rendering
// Handles table display
// Handles user interactions
// Handles error states
</script>
```

**After (split responsibilities):**
```vue
<!-- Dashboard.vue - orchestration only -->
<template>
  <DashboardHeader />
  <StatsCards :stats="stats" />
  <MarketCharts :data="marketData" />
  <StockTables :stocks="stocks" />
</template>

<script setup lang="ts">
import { useMarketStore } from '@/stores/market'
import DashboardHeader from './DashboardHeader.vue'
import StatsCards from './StatsCards.vue'
import MarketCharts from './MarketCharts.vue'
import StockTables from './StockTables.vue'

const marketStore = useMarketStore()
const { stats, marketData, stocks } = storeToRefs(marketStore)

onMounted(() => {
  marketStore.fetchOverview()
})
</script>
```

### 6.2 Composables for Reusable Logic

**Extract common logic:**
```typescript
// composables/useChartData.ts
export function useChartData<T>(
  fetchData: () => Promise<T>,
  options?: {
    autoFetch?: boolean
    refreshInterval?: number
  }
) {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetch = async () => {
    loading.value = true
    error.value = null

    try {
      data.value = await fetchData()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    if (options?.autoFetch) {
      fetch()
    }

    if (options?.refreshInterval) {
      setInterval(fetch, options.refreshInterval)
    }
  })

  return {
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),
    fetch
  }
}
```

**Use in components:**
```vue
<script setup lang="ts">
import { useChartData } from '@/composables/useChartData'
import { marketApiService } from '@/api/services/marketService'

const { data: fundFlowData, loading, fetch } = useChartData(
  () => marketApiService.getFundFlow({ symbol: '000001' }),
  { autoFetch: true, refreshInterval: 30000 }
)
</script>
```

### 6.3 Provide/Inject for Deep Props

**Parent component:**
```vue
<script setup lang="ts">
import { provide } from 'vue'

const theme = ref('dark')
const updateTheme = (newTheme: string) => {
  theme.value = newTheme
}

provide('theme', {
  theme: readonly(theme),
  updateTheme
})
</script>
```

**Child component (any depth):**
```vue
<script setup lang="ts">
import { inject } from 'vue'

const { theme, updateTheme } = inject('theme')!
</script>
```

### 6.4 Component Props Validation

```vue
<script setup lang="ts">
interface StockListItem {
  symbol: string
  name: string
  price: number
  change: number
}

interface Props {
  stocks: StockListItem[]
  maxItems?: number
  showChange?: boolean
  sortable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  maxItems: 50,
  showChange: true,
  sortable: false
})

// Emit events
interface Emits {
  (e: 'row-click', stock: StockListItem): void
  (e: 'sort', column: keyof StockListItem): void
}

const emit = defineEmits<Emits>()

// Watch for changes
watch(() => props.stocks.length, (newLength) => {
  console.log(`Stock list has ${newLength} items`)
})
</script>
```

---

## Quick Wins (1-2 hours each)

1. **Add loading skeletons** - Replace spinners with skeleton screens
2. **Fix color contrast** - Update secondary text color
3. **Add ARIA labels** - Label all icon buttons
4. **Enable 1 strict flag** - Start with `noImplicitAny`
5. **Write 5 component tests** - Start with Dashboard, Market, Strategy
6. **Create 1 store** - Start with UI store for sidebar/theme
7. **Add error boundary** - Global error handler
8. **Optimize 1 chunk** - Split Element Plus icons

---

## Implementation Checklist

### Week 1
- [ ] Enable TypeScript `noImplicitAny`
- [ ] Write 20 component tests
- [ ] Add ARIA labels to all icon buttons
- [ ] Create UI store

### Week 2
- [ ] Enable TypeScript `strictNullChecks`
- [ ] Write 20 more component tests
- [ ] Fix color contrast issues
- [ ] Create market store

### Week 3
- [ ] Implement manual chunk splitting
- [ ] Add E2E tests for critical paths
- [ ] Implement error boundaries
- [ ] Performance audit and optimization

---

**Last Updated:** 2025-12-30
**For:** MyStocks Frontend Development Team
**Version:** 1.0
