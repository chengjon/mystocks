# Research & Technology Decisions

**Feature**: Market Data UI/UX Improvements
**Date**: 2025-10-26
**Status**: Phase 0 Complete

---

## Overview

This document captures all technology decisions, best practices research, and integration patterns for implementing 5 UI/UX improvements to the market data pages. No critical unknowns were identified in Technical Context, but this research validates technology choices and documents implementation patterns.

---

## 1. ECharts Integration with Vue 3

### Decision

Use **Apache ECharts 5.4+** with **vue-echarts** wrapper for fund flow trend chart visualization.

### Rationale

1. **Existing Dependency**: ECharts already used in the project (confirmed in codebase)
2. **Performance**: Handles 1000+ data points smoothly (fund flow historical data)
3. **Vue 3 Compatibility**: Official vue-echarts@6.x supports Vue 3 Composition API
4. **Responsive**: Built-in resize handling for responsive layouts
5. **Customization**: Rich API for styling, tooltips, legends, and interactions

### Implementation Pattern

```vue
<script setup>
import { ref, computed, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// Register required components
use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const props = defineProps({
  industryName: String,
  trendData: Array
})

const chartOption = computed(() => ({
  title: { text: `${props.industryName} 资金流向趋势` },
  xAxis: { type: 'category', data: props.trendData.map(d => d.date) },
  yAxis: { type: 'value', name: '净流入(亿元)' },
  series: [{
    data: props.trendData.map(d => d.net_inflow),
    type: 'line',
    smooth: true,
    itemStyle: { color: '#409EFF' }
  }],
  tooltip: { trigger: 'axis' }
}))
</script>

<template>
  <v-chart :option="chartOption" autoresize style="height: 400px" />
</template>
```

### Alternatives Considered

- **Chart.js**: Simpler but less feature-rich, no built-in Chinese market data formatting
- **D3.js**: More powerful but steeper learning curve, more custom code required
- **Native Canvas/SVG**: Too low-level, no built-in interactivity

### Best Practices

1. **Lazy Loading**: Import only required chart types (LineChart for trend visualization)
2. **Tree Shaking**: Use ECharts "use" API to reduce bundle size by ~60%
3. **Responsive**: Use `autoresize` prop and container height in CSS (not inline pixels)
4. **Performance**: Debounce chart updates on rapid data changes (300ms)
5. **Accessibility**: Add aria-label to chart container describing data

---

## 2. CSS Fixed Table Headers (position: sticky)

### Decision

Use **CSS position: sticky** for fixed table headers across all market data tables.

### Rationale

1. **Browser Support**: 97%+ support in target browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
2. **Performance**: Native CSS, no JavaScript scroll listeners, 60fps smooth scrolling
3. **Simplicity**: No external libraries required, ~10 lines of CSS
4. **Element Plus Compatible**: Works seamlessly with `el-table` component
5. **No IE11 Requirement**: Per spec, IE11 not supported

### Implementation Pattern

```css
/* Global table sticky header styles */
.el-table .el-table__header-wrapper {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #f5f7fa; /* Match Element Plus default */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Subtle shadow when scrolling */
}

/* Mobile fallback (optional, for devices <768px) */
@media (max-width: 768px) {
  .el-table .el-table__header-wrapper {
    /* Alternative: Fixed positioning with calculated top offset */
    position: fixed;
    top: 60px; /* Account for mobile header height */
    left: 0;
    right: 0;
  }
}
```

### Element Plus Integration

```vue
<template>
  <el-table
    :data="tableData"
    stripe
    border
    height="calc(100vh - 200px)"  <!-- Fixed height required for sticky -->
    class="sticky-header-table"
  >
    <el-table-column prop="date" label="日期" width="120" fixed />
    <!-- More columns -->
  </el-table>
</template>

<style scoped>
.sticky-header-table :deep(.el-table__header-wrapper) {
  position: sticky;
  top: 0;
  z-index: 10;
}
</style>
```

### Alternatives Considered

- **JavaScript Scroll Listener**: More complex, performance overhead, unnecessary
- **Fixed Positioning**: Breaks horizontal scrolling, requires complex width calculations
- **Third-party Library** (e.g., react-sticky): Overkill for native CSS solution

### Best Practices

1. **Z-index Management**: Ensure header z-index (10) > body rows (1) but < modals/dropdowns (1000)
2. **Background Color**: Always set opaque background to prevent content bleeding through
3. **Box Shadow**: Add subtle shadow when scrolling past header for visual feedback
4. **Height Constraint**: Table must have explicit height (not auto) for sticky to work
5. **Testing**: Verify behavior with 100+ rows, rapid scrolling, and different viewport sizes

---

## 3. Element Plus Pagination Best Practices

### Decision

Use **Element Plus Pagination** component with `hide-on-single-page` and configurable page size.

### Rationale

1. **Existing Dependency**: Element Plus already used throughout project
2. **Flexible Configuration**: Supports custom page sizes, total items, current page
3. **Auto-hide**: `hide-on-single-page` matches spec requirement (FR-003, FR-011)
4. **Accessibility**: Built-in keyboard navigation and ARIA labels
5. **Consistent UX**: Matches existing pagination patterns in application

### Implementation Pattern

```vue
<script setup>
import { ref, computed } from 'vue'

const currentPage = ref(1)
const pageSize = ref(20)
const totalItems = ref(0)

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return allData.value.slice(start, end)
})

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1 // Reset to first page on size change
  // Save preference
  localStorage.setItem('tablePageSize', newSize)
}

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
}
</script>

<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>数据表格</span>
        <el-select v-model="pageSize" @change="handleSizeChange" style="width: 120px">
          <el-option label="10 条/页" :value="10" />
          <el-option label="20 条/页" :value="20" />
          <el-option label="50 条/页" :value="50" />
          <el-option label="100 条/页" :value="100" />
        </el-select>
      </div>
    </template>

    <el-table :data="paginatedData" stripe border class="sticky-header-table">
      <!-- columns -->
    </el-table>

    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="totalItems"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      hide-on-single-page
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </el-card>
</template>
```

### Frontend vs Backend Pagination Decision

**Use Frontend Pagination** for:
- ✅ Fund Flow data (<300 records typically)
- ✅ Dragon Tiger data (<100 records per day)
- ✅ ETF data (<500 records)

**Rationale**: All market data tables have <1000 items, frontend pagination avoids extra API calls, improves responsiveness

**Use Backend Pagination** for:
- ⚠️ Historical data queries (>1000 records)
- ⚠️ User logs or audit trails (unbounded growth)

### Best Practices

1. **Persist Page Size**: Save user preference to LocalStorage (FR-019)
2. **Reset on Size Change**: Always reset to page 1 when changing page size (prevent empty pages)
3. **Auto-hide**: Use `hide-on-single-page` to reduce UI clutter for small datasets
4. **Layout Prop**: Include "total, sizes, prev, pager, next, jumper" for full functionality
5. **Accessibility**: Ensure pagination controls are keyboard-navigable and screen-reader friendly

---

## 4. Typography & Font Size System

### Decision

Implement **CSS Custom Properties (CSS Variables)** based font size system with 5 levels (12-20px).

### Rationale

1. **Dynamic Updates**: CSS variables update in real-time without page reload (FR-015)
2. **Cascade**: All child elements inherit font size automatically (FR-016 hierarchy)
3. **Browser Support**: 100% support in target browsers
4. **Performance**: No JavaScript DOM manipulation, pure CSS updates
5. **Maintainability**: Single source of truth for font sizes

### Implementation Pattern

**typography.css** (Global Stylesheet):
```css
:root {
  /* Font Size Levels (FR-014) */
  --font-size-extra-small: 12px;
  --font-size-small: 14px;
  --font-size-medium: 16px;
  --font-size-large: 18px;
  --font-size-extra-large: 20px;

  /* Current User Selection (default: medium) */
  --font-size-base: var(--font-size-medium);

  /* Font Hierarchy (FR-016) */
  --font-size-helper: calc(var(--font-size-base) - 2px);  /* 辅助文字 */
  --font-size-body: var(--font-size-base);                /* 正文 */
  --font-size-subtitle: calc(var(--font-size-base) + 2px);/* 小标题 */
  --font-size-title: calc(var(--font-size-base) + 4px);   /* 标题 */
  --font-size-heading: calc(var(--font-size-base) + 6px); /* 主标题 */

  /* Line Height (FR-017) */
  --line-height: 1.5;

  /* Font Family (FR-018) */
  --font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB",
                 "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}

/* Apply to body */
body {
  font-family: var(--font-family);
  font-size: var(--font-size-body);
  line-height: var(--line-height);
}

/* Typography Classes */
.text-helper { font-size: var(--font-size-helper); }
.text-body { font-size: var(--font-size-body); }
.text-subtitle { font-size: var(--font-size-subtitle); }
.text-title { font-size: var(--font-size-title); }
.text-heading { font-size: var(--font-size-heading); }
```

**FontSizeSetting.vue** (Settings Component):
```vue
<script setup>
import { ref, onMounted } from 'vue'

const fontSizeLevels = [
  { label: 'Extra Small (12px)', value: '12px' },
  { label: 'Small (14px)', value: '14px' },
  { label: 'Medium (16px)', value: '16px' },
  { label: 'Large (18px)', value: '18px' },
  { label: 'Extra Large (20px)', value: '20px' }
]

const selectedSize = ref('16px')

const applyFontSize = (size) => {
  // Update CSS variable (FR-015: immediate visual update)
  document.documentElement.style.setProperty('--font-size-base', size)

  // Persist to LocalStorage (FR-019)
  localStorage.setItem('userFontSize', size)

  // Log user interaction (Observability)
  console.log('[User Preference] Font size changed to:', size)
}

const handleSizeChange = (size) => {
  selectedSize.value = size
  applyFontSize(size)
}

onMounted(() => {
  // Load saved preference (FR-019)
  const savedSize = localStorage.getItem('userFontSize')
  if (savedSize) {
    selectedSize.value = savedSize
    applyFontSize(savedSize)
  }
})
</script>

<template>
  <el-form-item label="字体大小">
    <el-radio-group v-model="selectedSize" @change="handleSizeChange">
      <el-radio-button
        v-for="level in fontSizeLevels"
        :key="level.value"
        :label="level.value"
      >
        {{ level.label }}
      </el-radio-button>
    </el-radio-group>
  </el-form-item>
</template>
```

### Alternatives Considered

- **SASS/LESS Variables**: Require recompilation, not runtime-configurable
- **JavaScript DOM Style Updates**: More complex, worse performance, requires traversal
- **Class Switching**: Would need 5x classes for every component, unmaintainable

### Best Practices

1. **Validation**: Clamp font size to 12-20px range to prevent layout breakage (FR-014)
2. **Responsive Breakpoints**: Optionally adjust --font-size-base at mobile breakpoints
3. **Element Plus Override**: Ensure CSS variables apply to Element Plus components via `::v-deep`
4. **Testing**: Verify all 5 levels at different viewport sizes (desktop, tablet, mobile)
5. **Accessibility**: Ensure all text remains readable at smallest (12px) and largest (20px) sizes

---

## 5. User Preferences Persistence Strategy

### Decision

Use **LocalStorage (primary) with optional backend sync** for user preferences.

### Rationale

1. **Immediate Persistence**: No API latency, instant save/load (FR-015, FR-019)
2. **Offline Support**: Works without backend connection
3. **Minimal Backend Changes**: Optional sync doesn't block feature delivery
4. **User Privacy**: Data stored locally, not on server (unless user opts in)
5. **Fallback**: If LocalStorage quota exceeded, gracefully degrade to session-only

### Implementation Pattern

**useUserPreferences.ts** (Composable):
```typescript
import { ref, watch } from 'vue'

export interface UserPreferences {
  fontSize: string
  pageSizeFundFlow: number
  pageSizeETF: number
  pageSizeDragonTiger: number
  lastWatchlistTab: string
  wencaiLastQuery: string | null
}

const defaultPreferences: UserPreferences = {
  fontSize: '16px',
  pageSizeFundFlow: 20,
  pageSizeETF: 20,
  pageSizeDragonTiger: 20,
  lastWatchlistTab: 'user',
  wencaiLastQuery: null
}

export function useUserPreferences() {
  const preferences = ref<UserPreferences>({ ...defaultPreferences })

  // Load from LocalStorage
  const loadPreferences = () => {
    try {
      const saved = localStorage.getItem('userPreferences')
      if (saved) {
        preferences.value = { ...defaultPreferences, ...JSON.parse(saved) }
      }
    } catch (error) {
      console.error('[Preferences] Failed to load:', error)
    }
  }

  // Save to LocalStorage
  const savePreferences = () => {
    try {
      localStorage.setItem('userPreferences', JSON.stringify(preferences.value))
      console.log('[Preferences] Saved:', preferences.value)
    } catch (error) {
      console.error('[Preferences] Failed to save:', error)
      // Fallback: If quota exceeded, use sessionStorage
      try {
        sessionStorage.setItem('userPreferences', JSON.stringify(preferences.value))
      } catch {}
    }
  }

  // Auto-save on changes (with debounce)
  let saveTimeout: number
  watch(preferences, () => {
    clearTimeout(saveTimeout)
    saveTimeout = setTimeout(savePreferences, 500)
  }, { deep: true })

  // Optional: Sync to backend
  const syncToBackend = async () => {
    try {
      await fetch('/api/user/preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(preferences.value)
      })
    } catch (error) {
      console.warn('[Preferences] Backend sync failed (non-critical):', error)
    }
  }

  loadPreferences()

  return {
    preferences,
    savePreferences,
    syncToBackend
  }
}
```

### LocalStorage vs Backend Trade-offs

| Aspect | LocalStorage | Backend Persistence |
|--------|-------------|---------------------|
| **Latency** | <1ms | 50-200ms |
| **Multi-device** | ❌ Device-specific | ✅ Syncs across devices |
| **Offline** | ✅ Works offline | ❌ Requires connection |
| **Storage Limit** | ~5-10MB | Unlimited |
| **Privacy** | ✅ Local only | ⚠️ Server has access |
| **Complexity** | Simple | Requires API + DB schema |

**Decision**: Start with LocalStorage, add backend sync as optional enhancement (FR-019 doesn't specify multi-device sync)

### Alternatives Considered

- **Cookies**: 4KB limit too small for multiple preferences
- **IndexedDB**: Overkill for simple key-value preferences
- **Backend-only**: Adds latency, requires authentication, unnecessary complexity

### Best Practices

1. **Debounce Saves**: Wait 500ms after last change before saving (prevent excessive writes)
2. **Merge Defaults**: Always merge with default preferences to handle new settings
3. **Error Handling**: Gracefully handle quota exceeded, parse errors, corrupted data
4. **Versioning**: Include schema version in saved data for future migration compatibility
5. **Logging**: Log all preference changes for debugging and observability

---

## 6. Wencai Query Presets Configuration

### Decision

Use **JSON configuration file** (`wencai-queries.json`) for qs_1 to qs_9 query definitions.

### Rationale

1. **Configuration-Driven**: Follows constitution principle (no hardcoded queries)
2. **Easy Updates**: Product team can update queries without code changes
3. **Version Control**: Query changes tracked in git history
4. **No Database Schema**: Avoids adding new tables for simple configuration
5. **Build-time Validation**: Can validate JSON schema during build

### Implementation Pattern

**wencai-queries.json** (Configuration File):
```json
{
  "version": "1.0",
  "queries": [
    {
      "id": "qs_1",
      "name": "市值大于100亿的科技股",
      "description": "筛选市值100亿以上的科技行业股票",
      "conditions": {
        "market_cap_min": 10000000000,
        "industry": "科技",
        "order_by": "market_cap desc"
      }
    },
    {
      "id": "qs_2",
      "name": "连续3天上涨的股票",
      "description": "查找最近3个交易日持续上涨的股票",
      "conditions": {
        "consecutive_up_days": 3,
        "order_by": "change_percent desc"
      }
    },
    {
      "id": "qs_3",
      "name": "成交量放大200%以上",
      "description": "今日成交量相比5日均量放大2倍以上",
      "conditions": {
        "volume_ratio_min": 2.0,
        "order_by": "volume_ratio desc"
      }
    }
    // ... qs_4 through qs_9
  ]
}
```

**WencaiFilter.vue** (Component):
```vue
<script setup>
import { ref, onMounted } from 'vue'
import wencaiQueries from '@/config/wencai-queries.json'

const queries = ref(wencaiQueries.queries)
const queryResults = ref([])
const loading = ref(false)

const executeQuery = async (query) => {
  loading.value = true
  try {
    const response = await fetch('/api/wencai/filter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(query.conditions)
    })
    queryResults.value = await response.json()

    // Log user interaction
    console.log('[Wencai] Query executed:', query.id)
  } catch (error) {
    console.error('[Wencai] Query failed:', error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-card>
    <template #header>查询列表 - 默认查询</template>

    <el-row :gutter="12">
      <el-col
        v-for="query in queries"
        :key="query.id"
        :span="8"
      >
        <el-card
          shadow="hover"
          @click="executeQuery(query)"
          class="query-card"
        >
          <h4>{{ query.name }}</h4>
          <p>{{ query.description }}</p>
        </el-card>
      </el-col>
    </el-row>

    <el-divider />

    <div v-if="queryResults.length > 0">
      <h3>查询结果</h3>
      <el-table :data="queryResults" stripe border>
        <!-- columns -->
      </el-table>
    </div>
  </el-card>
</template>
```

### Alternatives Considered

- **Database Table**: Overkill for 9 static queries, adds schema complexity
- **Hardcoded in Component**: Violates configuration-driven principle, hard to update
- **Environment Variables**: Limited structure, not suitable for nested objects

### Best Practices

1. **Schema Validation**: Validate JSON against schema during build (Vite plugin)
2. **Versioning**: Include version field for future query structure migrations
3. **Documentation**: Each query must have name, description, conditions
4. **Extensibility**: Design schema to support custom user queries in future (v2)
5. **Hot Reload**: In dev mode, watch JSON file for changes and reload

---

## 7. Watchlist Tab State Management

### Decision

Use **Vue Router query parameters** + **LocalStorage** for tab state persistence.

### Rationale

1. **URL Sharing**: Users can share specific tab URLs (`/watchlist?tab=strategy`)
2. **Browser Navigation**: Back/forward buttons work correctly
3. **Persistence**: Last selected tab remembered via LocalStorage (FR-030)
4. **Simplicity**: No global state management needed, Vue Router built-in
5. **Accessibility**: Screen readers announce route changes

### Implementation Pattern

```vue
<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const activeTab = ref('user') // Default: 用户自选

const tabs = [
  { name: 'user', label: '用户自选' },
  { name: 'system', label: '系统自选' },
  { name: 'strategy', label: '策略自选' },
  { name: 'monitor', label: '监控列表' }
]

const handleTabChange = (tabName) => {
  activeTab.value = tabName

  // Update URL query parameter
  router.push({ query: { tab: tabName } })

  // Save to LocalStorage (FR-030)
  localStorage.setItem('lastWatchlistTab', tabName)

  // Log interaction
  console.log('[Watchlist] Tab changed to:', tabName)
}

onMounted(() => {
  // Priority 1: URL query parameter
  if (route.query.tab) {
    activeTab.value = route.query.tab
  }
  // Priority 2: LocalStorage
  else {
    const lastTab = localStorage.getItem('lastWatchlistTab')
    if (lastTab) {
      activeTab.value = lastTab
      router.replace({ query: { tab: lastTab } })
    }
  }
})

// Watch route changes (browser back/forward)
watch(() => route.query.tab, (newTab) => {
  if (newTab) {
    activeTab.value = newTab
  }
})
</script>

<template>
  <el-tabs v-model="activeTab" @tab-change="handleTabChange">
    <el-tab-pane
      v-for="tab in tabs"
      :key="tab.name"
      :label="tab.label"
      :name="tab.name"
    >
      <WatchlistTable :group="tab.name" />
    </el-tab-pane>
  </el-tabs>
</template>
```

### Alternatives Considered

- **Pinia Store Only**: Doesn't persist across sessions, no URL sharing
- **LocalStorage Only**: Breaks browser navigation, can't share URLs
- **Hash-based Routing**: Works but query params more semantic

### Best Practices

1. **Default Tab**: Always show "用户自选" first (FR-027)
2. **Invalid Tab Handling**: If URL has invalid tab, fallback to default + replace URL
3. **Loading States**: Show skeleton while tab data loads
4. **Accessibility**: Use semantic HTML `<nav>` + ARIA roles for tab navigation
5. **Performance**: Lazy load tab content only when activated (not all 4 tabs upfront)

---

## Summary of Technology Stack

| Feature Area | Technology | Version | Rationale |
|--------------|-----------|---------|-----------|
| **Frontend Framework** | Vue 3 | 3.3+ | Existing stack, Composition API |
| **UI Library** | Element Plus | 2.4+ | Existing stack, comprehensive components |
| **Chart Library** | ECharts | 5.4+ | Existing stack, performance, customization |
| **State Management** | Pinia | 2.x | Vue 3 official state management |
| **Routing** | Vue Router | 4.x | Tab state, URL sharing |
| **Build Tool** | Vite | 4+ | Fast HMR, modern features |
| **Testing** | Vitest + Playwright | Latest | Unit + E2E coverage |
| **Persistence** | LocalStorage | Browser API | User preferences, immediate persistence |
| **Styling** | CSS Variables | Browser API | Dynamic font sizing, theming |
| **Backend** | FastAPI | Existing | Minimal changes, optional endpoints |

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| **Performance**: Large datasets (1000+ rows) | Frontend pagination, virtualization if needed |
| **Browser Compatibility**: position:sticky | Target modern browsers only, mobile fallback |
| **Font Size**: Layout breakage at extremes | Validation (12-20px), responsive testing |
| **LocalStorage Quota**: Exceeded limit | Graceful degradation to sessionStorage |
| **ECharts Bundle Size**: >300KB | Tree-shaking, lazy loading, only import used charts |
| **Chart Load Failures**: API errors | Defensive programming, fallback to table-only view |

---

## Next Steps

1. ✅ **Research Complete**: All technology decisions documented
2. **Proceed to Phase 1**: Generate data-model.md, contracts/, quickstart.md
3. **Update Agent Context**: Run agent context update script
4. **Generate Tasks**: Execute `/speckit.tasks` command

**Research Status**: ✅ **COMPLETE** - No blocking unknowns, all decisions documented
