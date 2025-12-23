# Smart/Dumb Components Specification

## ADDED Requirements

### Requirement: Smart Component Definition

**Requirement**: Smart components (Views/Containers) MUST handle business logic and API calls.

#### Scenario: Smart Component Structure
**GIVEN** a page-level component
**WHEN** implementing it
**THEN** it MUST follow the smart component pattern:

```vue
<!-- Smart Component: MarketOverview.vue -->
<template>
  <div class="market-overview">
    <!-- Pass data to dumb components -->
    <MarketIndicesCard :data="marketData.indices" :loading="loading" />
    <FundFlowPanel :data="marketData.fundFlow" @refresh="handleRefresh" />
    <StockSearchBar @search="handleSearch" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { DataAdapter } from '@/utils/adapters'
import type { MarketOverviewVM } from '@/utils/adapters'

// Smart component characteristics:
// 1. Fetches data from API
// 2. Manages state
// 3. Handles business logic
// 4. Passes data to dumb components

const marketStore = useMarketStore()
const loading = ref(false)
const marketData = ref<MarketOverviewVM | null>(null)

// API calls
async function fetchMarketData() {
  loading.value = true
  try {
    const rawData = await marketStore.getMarketOverview()
    marketData.value = DataAdapter.toMarketOverviewVM(rawData)
  } catch (error) {
    console.error('Failed to fetch market data:', error)
  } finally {
    loading.value = false
  }
}

// Event handlers
function handleRefresh() {
  fetchMarketData()
}

function handleSearch(symbol: string) {
  // Handle search logic
}

onMounted(() => {
  fetchMarketData()
})
</script>
```

### Requirement: Dumb Component Definition

**Requirement**: Dumb components (UI Components) MUST only receive props and emit events.

#### Scenario: Dumb Component Structure
**GIVEN** a reusable UI component
**WHEN** implementing it
**THEN** it MUST follow the dumb component pattern:

```vue
<!-- Dumb Component: MarketIndicesCard.vue -->
<template>
  <el-card class="market-indices" :loading="loading">
    <template #header>
      <h3>大盘指数</h3>
    </template>

    <div class="indices-grid">
      <div
        v-for="index in data"
        :key="index.name"
        class="index-item"
        @click="$emit('index-click', index)"
      >
        <span class="name">{{ index.name }}</span>
        <span class="current">{{ index.current }}</span>
        <span :class="['change', index.trend]">
          {{ index.change > 0 ? '+' : '' }}{{ index.changePercent }}
        </span>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { IndexItemVM } from '@/utils/adapters'

// Dumb component characteristics:
// 1. Receives data through props
// 2. Emits events for user interactions
// 3. No API calls
// 4. No business logic

interface Props {
  data: IndexItemVM[]
  loading?: boolean
}

defineProps<Props>()

// Emit events
const emit = defineEmits<{
  'index-click': [index: IndexItemVM]
}>()
</script>

<style scoped>
/* Component-specific styles */
.index-item {
  cursor: pointer;
  transition: background-color 0.3s;
}

.change.up {
  color: #f56c6c;
}

.change.down {
  color: #67c23a;
}
</style>
```

### Requirement: Component Naming Convention

**Requirement**: Components MUST be named according to their type and purpose.

#### Scenario: Smart Component Naming
**GIVEN** a smart component (page/container)
**WHEN** naming it
**THEN** it SHOULD use descriptive names:
- `MarketOverview.vue` (not `Market.vue`)
- `StrategyManagement.vue` (not `Strategies.vue`)
- `TradeExecutionPanel.vue` (not `Trade.vue`)

#### Scenario: Dumb Component Naming
**GIVEN** a dumb component (reusable UI)
**WHEN** naming it
**THEN** it SHOULD describe its UI function:
- `KLineChart.vue` (not `StockChart.vue`)
- `OrderTable.vue` (not `Orders.vue`)
- `SearchBar.vue` (not `Search.vue`)

### Requirement: Props and Events Definition

**Requirement**: Component interfaces MUST be explicitly defined with TypeScript.

#### Scenario: Props Interface
**GIVEN** a component receives props
**WHEN** defining them
**THEN** use TypeScript interfaces:

```typescript
interface Props {
  // Primitive types with defaults
  title: string
  loading?: boolean

  // Object/Array types
  data: MarketData[]
  config: ChartConfig

  // Optional with constraints
  maxItems?: number
  theme?: 'light' | 'dark'
}

// Required props without defaults
const props = defineProps<Props>()
```

#### Scenario: Events Interface
**GIVEN** a component emits events
**WHEN** defining them
**THEN** use TypeScript emits:

```typescript
// Named tuple syntax for type-safe events
const emit = defineEmits<{
  // Simple event
  'refresh': []

  // Event with payload
  'item-click': [item: MarketItemVM]

  // Event with multiple payloads
  'filter-change': [filter: FilterOptions, page: number]

  // Async event
  'async-action': [callback: (result: boolean) => void]
}>()
```

### Requirement: State Management Rules

**Requirement**: Smart components SHOULD use Pinia for shared state.

#### Scenario: State Management
**GIVEN** shared application state
**WHEN** accessing it
**THEN** use Pinia stores:

```typescript
// In smart component
import { useMarketStore } from '@/stores/market'
import { useUserStore } from '@/stores/user'

const marketStore = useMarketStore()
const userStore = useUserStore()

// Reactive state
const { marketData, isLoading } = storeToRefs(marketStore)

// Actions
async function refreshData() {
  await marketStore.fetchMarketData()
}

// Computed
const filteredData = computed(() => {
  return marketStore.data.filter(item =>
    userStore.favoriteStocks.includes(item.symbol)
  )
})
```

### Requirement: Dependency Injection

**Requirement**: Smart components SHOULD receive dependencies through composition.

#### Scenario: Service Injection
**GIVEN** a component needs external services
**WHEN** implementing it
**THEN** use composition functions:

```typescript
// composables/useMarketData.ts
export function useMarketData() {
  const marketStore = useMarketStore()
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchMarketData() {
    loading.value = true
    error.value = null

    try {
      await marketStore.fetchMarketData()
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  return {
    // Reactive state
    marketData: computed(() => marketStore.marketData),
    isLoading: readonly(loading),
    error: readonly(error),

    // Actions
    fetchMarketData
  }
}

// In component
<script setup lang="ts">
const { marketData, isLoading, fetchMarketData } = useMarketData()
</script>
```

### Requirement: Component Communication

**Requirement**: Components MUST communicate through props, events, or shared stores.

#### Scenario: Parent-Child Communication
**GIVEN** parent and child components
**WHEN** they need to communicate
**THEN** use props and events:

```vue
<!-- Parent -->
<template>
  <ChildComponent
    :data="parentData"
    :config="childConfig"
    @child-event="handleChildEvent"
    @update:value="handleValueUpdate"
  />
</template>

<!-- Child -->
<script setup lang="ts">
const props = defineProps<{
  data: any[]
  config: object
}>()

const emit = defineEmits<{
  'child-event': [payload: any]
  'update:value': [value: string]
}>()

function notifyParent() {
  emit('child-event', { /* data */ })
}
</script>
```

#### Scenario: Cross-Component Communication
**GIVEN** components that are not parent-child
**WHEN** they need to share state
**THEN** use Pinia stores or event bus:

```typescript
// Store for shared state
export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: [] as NotificationVM[]
  }),

  actions: {
    addNotification(notification: NotificationVM) {
      this.notifications.push(notification)
    },

    clearNotifications() {
      this.notifications = []
    }
  }
})
```

### Requirement: Component Testing Strategy

**Requirement**: Smart and dumb components MUST have appropriate test coverage.

#### Scenario: Smart Component Testing
**GIVEN** a smart component
**WHEN** testing it
**THEN** test:
- API calls and mocked responses
- State management
- Event handling
- Integration with stores

#### Scenario: Dumb Component Testing
**GIVEN** a dumb component
**WHEN** testing it
**THEN** test:
- Props rendering
- Event emission
- Visual output
- Edge cases with different props

```typescript
// Dumb component test
describe('MarketIndicesCard', () => {
  it('renders index data correctly', () => {
    const mockData = [
      { name: '上证指数', current: 3000, change: 1.5, trend: 'up' }
    ]

    const wrapper = mount(MarketIndicesCard, {
      props: { data: mockData }
    })

    expect(wrapper.text()).toContain('上证指数')
    expect(wrapper.text()).toContain('3000')
    expect(wrapper.find('.change.up').exists()).toBe(true)
  })

  it('emits index-click event', async () => {
    const wrapper = mount(MarketIndicesCard, {
      props: { data: mockData }
    })

    await wrapper.find('.index-item').trigger('click')

    expect(wrapper.emitted('index-click')).toBeTruthy()
    expect(wrapper.emitted('index-click')[0]).toEqual([mockData[0]])
  })
})
```