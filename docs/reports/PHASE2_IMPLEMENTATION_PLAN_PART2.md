# Phase 2 Implementation Plan - Part 2

## Overview
**Phase 2 Current Progress**: 4/11 tasks complete (36.4%)
**Last Completed**: Single-page TradingDecisionCenter.vue with 4-tab navigation
**Next Focus**: Portfolio tab integration + Wizard-style backtesting workflow

---

## Task Analysis

### Current State of TradingDecisionCenter.vue

**✅ Completed Features**:
1. Four-tab navigation structure (Overview, Positions, Orders, Portfolio)
2. Overview tab with market data panel and quick actions
3. Orders tab with order entry form and order history table
4. Portfolio tab with 5 Bloomberg-style stat cards

**❌ Issues Identified**:

1. **Import Errors** (Lines 311-318):
   ```typescript
   import {
     PortfolioOverview as PortfolioOverviewVue,
     PositionsTab as PositionsTabVue,
     OrdersTab as OrdersTabVue,
     PortfolioSummaryPanel as PortfolioSummaryPanelVue,
     MarketDataPanel as MarketDataPanelVue
   } from './decision-center/components'
   ```
   - Path `./decision-center/components` does NOT exist
   - These components need to be imported from existing paths

2. **Duplicate Code in Overview Tab** (Lines 38-52 and 54):
   - Market data panel code appears twice
   - Redundant template structure

3. **Missing Reactive Data**:
   - `marketTabs` undefined
   - `activeMarketTab` undefined
   - `orderForm` incomplete
   - `orderHistory` empty
   - `currentPrice` undefined

4. **TradingStats Hardcoded** (Lines 333-339):
   ```typescript
   const tradingStats = computed(() => ({
     totalPositions: 0,
     totalValue: 0,
     availableCash: 0,
     todayPnL: 0,
     unrealizedPnL: 0
   }))
   ```
   - Needs to fetch from Pinia stores
   - Missing fields: `totalAssets`, `positionValue`, `totalProfit`, `profitRate`

5. **Missing Handler Methods**:
   - `handleQuickBuy` undefined
   - `handleQuickSell` undefined
   - `handleSearchStock` undefined
   - `getStatusVariant` undefined

---

## Available Components & Stores

### 1. BloombergStatCard Component
**Path**: `web/frontend/src/components/BloombergStatCard.vue`
**Interface**:
```typescript
interface Props {
  label: string
  value: number | string
  icon?: 'wallet' | 'coin' | 'chart' | 'data' | 'trending-up' | 'trending-down'
  trend?: 'up' | 'down' | 'neutral'
  change?: number | null
  showChange?: boolean
  format?: 'currency' | 'percent' | 'number' | 'text'
  loading?: boolean
  showSparkline?: boolean
  sparklineData?: number[]
}
```

**Usage Example**:
```vue
<BloombergStatCard
  label="TOTAL ASSETS"
  :value="portfolio.total_assets"
  icon="wallet"
  trend="up"
  format="currency"
/>
```

### 2. PortfolioOverview Component
**Path**: `web/frontend/src/views/trade-management/components/PortfolioOverview.vue`
**Features**:
- Uses BloombergStatCard for 4 stats
- Exposes `setPortfolio(data)` method
- Reactive portfolio interface

**Portfolio Interface**:
```typescript
interface Portfolio {
  total_assets: number
  available_cash: number
  position_value: number
  total_profit: number
  profit_rate: number
}
```

### 3. Pinia Stores

#### trading.ts Store
**Path**: `web/frontend/src/stores/trading.ts`
**Available State**:
```typescript
interface TradingState {
  orders: TradeOrder[]
  currentSymbol: string
  isTradingEnabled: boolean
  systemStatus: string
  statusType: 'success' | 'warning' | 'error'
  apiStatus: 'online' | 'offline' | 'degraded'
  apiStatusText: string
  dataQualityStatus: 'good' | 'warning' | 'error'
  dataQualityScore: string
  systemLoadStatus: 'low' | 'medium' | 'high'
  systemLoadPercent: string
  version: string
  lastUpdateTime: string
}
```

#### tradingData.ts Store
**Path**: `web/frontend/src/stores/tradingData.ts`
**Available State**:
```typescript
interface TradingDataState {
  tradingSignals: TradingSignals | null
  tradingHistory: TradingHistory | null
  positionMonitor: PositionMonitorData | null
  performanceAnalysis: PerformanceAnalysis | null
  lastUpdateTime: string
}
```

**Actions**:
- `loadTradingSignals(filters)`
- `loadTradingHistory(filters)`
- `loadPositionMonitor()`
- `loadPerformanceAnalysis()`

### 4. MarketDataView Component
**Path**: `web/frontend/src/views/market/MarketDataView.vue`
**Features**:
- Tab navigation (Fund Flow, ETF Data, Chip Race, LongHuBang)
- Real-time data display
- ArtDeco styling

---

## Implementation Plan

### Task 1: Fix TradingDecisionCenter.vue Issues (p2-4 completion)

**Priority**: HIGH
**Estimated Time**: 2 hours

#### 1.1 Fix Component Imports

**Change**:
```typescript
// ❌ Remove these imports (lines 311-318)
// import {
//   PortfolioOverview as PortfolioOverviewVue,
//   PositionsTab as PositionsTabVue,
//   OrdersTab as OrdersTabVue,
//   PortfolioSummaryPanel as PortfolioSummaryPanelVue,
//   MarketDataPanel as MarketDataPanelVue
// } from './decision-center/components'

// ✅ Import from existing paths
import BloombergStatCard from '@/components/BloombergStatCard.vue'
import MarketDataView from '@/views/market/MarketDataView.vue'
// Note: PositionsPanel needs to be created or imported from existing path
```

#### 1.2 Remove Duplicate Market Data Code

**Change**:
```vue
<!-- ❌ Remove lines 38-52 (duplicate market data panel) -->

<!-- ✅ Keep only one instance at line 54 -->
<div ref="marketDataRef" class="chart-container">
  <MarketDataView />
</div>
```

#### 1.3 Add Missing Reactive Data

**Add to `<script setup>`**:
```typescript
// Order form reactive data
const orderForm = reactive({
  symbol: '',
  orderType: 'market' as 'market' | 'limit',
  quantity: 100
})

// Order history data
const orderHistory = ref<Order[]>([
  {
    id: '1',
    symbol: '600000',
    name: '浦发银行',
    orderType: '市价单',
    quantity: 1000,
    price: 10.50,
    status: 'filled',
    time: '2025-01-25 10:30:00'
  }
])

// Current price
const currentPrice = computed(() => {
  // TODO: Fetch from API or store
  return '10.50'
})

// Market tabs
const marketTabs = [
  { name: 'fund-flow', label: '资金流向' },
  { name: 'etf-data', label: 'ETF行情' },
  { name: 'chip-race', label: '竞价抢筹' },
  { name: 'longhubang', label: '龙虎榜' }
]
const activeMarketTab = ref('fund-flow')
```

#### 1.4 Implement TradingStats Computed from Pinia Stores

**Change**:
```typescript
// ❌ Remove hardcoded stats (lines 333-339)
// const tradingStats = computed(() => ({ ... }))

// ✅ Import and use Pinia stores
import { useTradingDataStore } from '@/stores/tradingData'

const tradingDataStore = useTradingDataStore()

// Computed trading stats from store
const tradingStats = computed(() => {
  const perf = tradingDataStore.state.performanceAnalysis
  const pos = tradingDataStore.state.positionMonitor

  return {
    totalAssets: pos?.total_assets || 0,
    availableCash: pos?.available_cash || 0,
    positionValue: pos?.position_value || 0,
    totalProfit: perf?.total_profit || 0,
    profitRate: perf?.profit_rate || 0
  }
})
```

#### 1.5 Implement Handler Methods

**Add to `<script setup>`**:
```typescript
// Order actions
const handleQuickBuy = () => {
  if (!orderForm.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }
  ElMessage.info(`买入 ${orderForm.quantity} 股 ${orderForm.symbol}`)
  // TODO: Call trading API
}

const handleQuickSell = () => {
  if (!orderForm.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }
  ElMessage.info(`卖出 ${orderForm.quantity} 股 ${orderForm.symbol}`)
  // TODO: Call trading API
}

const handleSearchStock = async () => {
  ElMessage.info(`搜索股票: ${orderForm.symbol}`)
  // TODO: Call API to fetch stock info
}

const getStatusVariant = (status: string) => {
  const statusMap: Record<string, string> = {
    'filled': 'success',
    'pending': 'warning',
    'cancelled': 'info'
  }
  return statusMap[status] || 'info'
}
```

#### 1.6 Load Performance Data on Mount

**Add to `onMounted`**:
```typescript
onMounted(async () => {
  initMarketDataChart()

  // Load performance data from store
  await tradingDataStore.loadPerformanceAnalysis()
  await tradingDataStore.loadPositionMonitor()
})
```

---

### Task 2: Implement Wizard-Style Backtesting Workflow (p2-5)

**Priority**: HIGH
**Estimated Time**: 6-8 hours
**New File**: `web/frontend/src/views/BacktestWizard.vue`

#### 2.1 Wizard Component Structure

```vue
<template>
  <div class="backtest-wizard layout-compact">
    <!-- ArtDeco Header -->
    <div class="wizard-header">
      <h1 class="page-title">STRATEGY BACKTESTING WIZARD</h1>
      <p class="page-subtitle">向导式策略回测流程</p>
    </div>

    <!-- Progress Indicator -->
    <div class="wizard-progress">
      <div
        v-for="(step, index) in wizardSteps"
        :key="step.id"
        :class="['step-item', { active: currentStep === index, completed: currentStep > index }]"
      >
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-label">{{ step.label }}</div>
      </div>
    </div>

    <!-- Step Content -->
    <div class="wizard-content">
      <!-- Step 1: Select Strategy Template -->
      <div v-if="currentStep === 0" class="step-content">
        <ArtDecoCardCompact>
          <template #header>
            <h3>选择策略模板</h3>
          </template>
          <div class="strategy-grid">
            <div
              v-for="template in strategyTemplates"
              :key="template.id"
              :class="['strategy-card', { selected: selectedStrategy === template.id }]"
              @click="selectStrategy(template.id)"
            >
              <div class="strategy-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="strategy-info">
                <div class="strategy-name">{{ template.name }}</div>
                <div class="strategy-desc">{{ template.description }}</div>
              </div>
            </div>
          </div>
        </ArtDecoCardCompact>
      </div>

      <!-- Step 2: Configure Parameters -->
      <div v-if="currentStep === 1" class="step-content">
        <ArtDecoCardCompact>
          <template #header>
            <h3>配置回测参数</h3>
          </template>
          <div class="parameter-form">
            <!-- Strategy Parameters -->
            <div class="form-section">
              <h4>策略参数</h4>
              <div class="form-row">
                <el-form-item label="短期MA周期">
                  <el-input-number v-model="backtestParams.shortMA" :min="1" :max="100" />
                </el-form-item>
                <el-form-item label="长期MA周期">
                  <el-input-number v-model="backtestParams.longMA" :min="1" :max="200" />
                </el-form-item>
              </div>
            </div>

            <!-- Time Period -->
            <div class="form-section">
              <h4>回测周期</h4>
              <el-date-picker
                v-model="backtestParams.startDate"
                type="date"
                placeholder="开始日期"
              />
              <el-date-picker
                v-model="backtestParams.endDate"
                type="date"
                placeholder="结束日期"
              />
            </div>

            <!-- Symbols -->
            <div class="form-section">
              <h4>股票代码</h4>
              <el-input
                v-model="backtestParams.symbols"
                placeholder="股票代码，用逗号分隔（如：600000,000001）"
              />
            </div>
          </div>
        </ArtDecoCardCompact>
      </div>

      <!-- Step 3: Review and Run -->
      <div v-if="currentStep === 2" class="step-content">
        <ArtDecoCardCompact>
          <template #header>
            <h3>确认回测配置</h3>
          </template>
          <div class="review-content">
            <div class="review-item">
              <span class="review-label">策略模板：</span>
              <span class="review-value">{{ getSelectedStrategyName() }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">短期MA周期：</span>
              <span class="review-value">{{ backtestParams.shortMA }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">长期MA周期：</span>
              <span class="review-value">{{ backtestParams.longMA }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">开始日期：</span>
              <span class="review-value">{{ formatDate(backtestParams.startDate) }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">结束日期：</span>
              <span class="review-value">{{ formatDate(backtestParams.endDate) }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">股票代码：</span>
              <span class="review-value">{{ backtestParams.symbols }}</span>
            </div>
          </div>
        </ArtDecoCardCompact>
      </div>

      <!-- Step 4: Results -->
      <div v-if="currentStep === 3" class="step-content">
        <ArtDecoCardCompact>
          <template #header>
            <h3>回测结果</h3>
          </template>
          <div class="results-content">
            <!-- Metrics -->
            <div class="results-metrics">
              <div class="metric-card">
                <div class="metric-label">总收益率</div>
                <div class="metric-value change-up">{{ backtestResults.totalReturn }}%</div>
              </div>
              <div class="metric-card">
                <div class="metric-label">夏普比率</div>
                <div class="metric-value">{{ backtestResults.sharpeRatio }}</div>
              </div>
              <div class="metric-card">
                <div class="metric-label">最大回撤</div>
                <div class="metric-value change-down">{{ backtestResults.maxDrawdown }}%</div>
              </div>
              <div class="metric-card">
                <div class="metric-label">胜率</div>
                <div class="metric-value">{{ backtestResults.winRate }}%</div>
              </div>
            </div>

            <!-- Chart -->
            <div ref="backtestChartRef" class="backtest-chart"></div>
          </div>
        </ArtDecoCardCompact>
      </div>
    </div>

    <!-- Navigation Buttons -->
    <div class="wizard-navigation">
      <el-button
        v-if="currentStep > 0"
        @click="prevStep"
        class="artdeco-gold-cta"
        plain
      >
        上一步
      </el-button>
      <el-button
        v-if="currentStep < 3"
        @click="nextStep"
        class="artdeco-gold-cta"
        :disabled="!canProceed"
      >
        {{ currentStep === 2 ? '开始回测' : '下一步' }}
      </el-button>
      <el-button
        v-if="currentStep === 3"
        @click="resetWizard"
        class="artdeco-gold-cta"
        plain
      >
        重新开始
      </el-button>
    </div>
  </div>
</template>
```

#### 2.2 Script Setup

```typescript
<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { artDecoTheme } from '@/utils/echarts'
import ArtDecoCardCompact from '@/components/artdeco/base/ArtDecoCardCompact.vue'

// Wizard steps
const wizardSteps = [
  { id: 'select', label: '选择策略' },
  { id: 'configure', label: '配置参数' },
  { id: 'review', label: '确认配置' },
  { id: 'results', label: '查看结果' }
]

const currentStep = ref(0)
const selectedStrategy = ref('')

// Strategy templates
interface StrategyTemplate {
  id: string
  name: string
  description: string
  defaultParams: Record<string, any>
}

const strategyTemplates: StrategyTemplate[] = [
  {
    id: 'ma_cross',
    name: '均线交叉策略',
    description: '基于短期和长期均线的交叉信号进行买卖',
    defaultParams: { shortMA: 5, longMA: 20 }
  },
  {
    id: 'rsi',
    name: 'RSI策略',
    description: '基于相对强弱指标的买卖信号',
    defaultParams: { rsiPeriod: 14, overbought: 70, oversold: 30 }
  },
  {
    id: 'bollinger',
    name: '布林带策略',
    description: '基于价格与布林带的关系进行交易',
    defaultParams: { period: 20, stdDev: 2 }
  },
  {
    id: 'volume',
    name: '量价策略',
    description: '结合成交量和价格变化进行交易',
    defaultParams: { volumeThreshold: 1.5, priceChange: 2 }
  }
]

// Backtest parameters
const backtestParams = ref({
  shortMA: 5,
  longMA: 20,
  startDate: new Date('2024-01-01'),
  endDate: new Date(),
  symbols: '600000'
})

// Backtest results
const backtestResults = ref({
  totalReturn: 15.5,
  sharpeRatio: 1.8,
  maxDrawdown: -8.5,
  winRate: 62.5
})

// Chart reference
const backtestChartRef = ref<HTMLElement>()
let backtestChart: any = null

// Computed: can proceed to next step
const canProceed = computed(() => {
  if (currentStep.value === 0) {
    return selectedStrategy.value !== ''
  }
  if (currentStep.value === 1) {
    return backtestParams.value.startDate && backtestParams.value.endDate
  }
  if (currentStep.value === 2) {
    return true
  }
  return false
})

// Actions
const selectStrategy = (strategyId: string) => {
  selectedStrategy.value = strategyId
  const template = strategyTemplates.find(t => t.id === strategyId)
  if (template) {
    backtestParams.value = {
      ...backtestParams.value,
      ...template.defaultParams
    }
  }
}

const nextStep = async () => {
  if (currentStep.value === 2) {
    // Run backtest
    ElMessage.info('正在运行回测...')
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate
    ElMessage.success('回测完成')
  }
  currentStep.value++
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const resetWizard = () => {
  currentStep.value = 0
  selectedStrategy.value = ''
}

const getSelectedStrategyName = () => {
  const template = strategyTemplates.find(t => t.id === selectedStrategy.value)
  return template ? template.name : ''
}

const formatDate = (date: Date) => {
  return date.toLocaleDateString('zh-CN')
}

const initBacktestChart = () => {
  if (backtestChartRef.value) {
    backtestChart = echarts.init(backtestChartRef.value, artDecoTheme)
    const option = {
      backgroundColor: 'transparent',
      xAxis: {
        type: 'category',
        data: ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05']
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [{
        type: 'line',
        name: '累计收益率',
        data: [0, 5, 8, 12, 15.5],
        lineStyle: {
          width: 2,
          color: '#D4AF37'
        },
        areaStyle: {
          color: 'rgba(212, 175, 55, 0.1)'
        }
      }]
    }
    backtestChart.setOption(option)
  }
}

onMounted(() => {
  if (currentStep.value === 3) {
    initBacktestChart()
  }
})

onBeforeUnmount(() => {
  if (backtestChart) {
    backtestChart.dispose()
  }
})
</script>
```

#### 2.3 Styling

```scss
<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.backtest-wizard {
  min-height: 100vh;
  padding: var(--artdeco-spacing-4);
  background-color: var(--artdeco-bg-global);
}

.wizard-header {
  text-align: center;
  padding: var(--artdeco-spacing-4) 0;
  border-bottom: 2px solid var(--artdeco-border-gold);
  margin-bottom: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-elevated);

  .page-title {
    font-family: var(--font-display);
    font-weight: 700;
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0 0 var(--artdeco-spacing-2) 0;
    font-size: var(--artdeco-text-3xl);
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-fg-muted);
    margin: 0;
  }
}

.wizard-progress {
  display: flex;
  justify-content: center;
  gap: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-4);
  border-bottom: 1px solid var(--artdeco-border-default);

  .step-item {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-2);

    .step-number {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: var(--artdeco-bg-elevated);
      border: 2px solid var(--artdeco-border-default);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-display);
      font-weight: 700;
      color: var(--artdeco-fg-muted);
      transition: all var(--artdeco-transition-base);
    }

    .step-label {
      font-family: var(--font-body);
      font-size: var(--artdeco-text-sm);
      color: var(--artdeco-fg-muted);
    }

    &.active {
      .step-number {
        background: var(--artdeco-gold-primary);
        border-color: var(--artdeco-border-gold);
        color: var(--artdeco-bg-global);
      }

      .step-label {
        color: var(--artdeco-gold-primary);
        font-weight: 600;
      }
    }

    &.completed {
      .step-number {
        background: var(--artdeco-eco-green);
        border-color: var(--artdeco-eco-green);
        color: white;
      }
    }
  }
}

.wizard-content {
  min-height: 500px;
  padding: var(--artdeco-spacing-4);
}

.wizard-navigation {
  display: flex;
  justify-content: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-4);
  border-top: 1px solid var(--artdeco-border-default);
}

// Strategy Grid
.strategy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--artdeco-spacing-3);
}

.strategy-card {
  padding: var(--artdeco-spacing-3);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  cursor: pointer;
  transition: all var(--artdeco-transition-base);

  &:hover {
    border-color: var(--artdeco-border-gold);
    box-shadow: var(--artdeco-shadow-md), var(--artdeco-glow-subtle);
    transform: translateY(-4px);
  }

  &.selected {
    border-color: var(--artdeco-border-gold);
    background: rgba(212, 175, 55, 0.05);
  }

  .strategy-icon {
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    margin-bottom: var(--artdeco-spacing-2);
  }

  .strategy-name {
    font-family: var(--font-display);
    font-weight: 600;
    color: var(--artdeco-fg-default);
    margin-bottom: var(--artdeco-spacing-1);
  }

  .strategy-desc {
    font-family: var(--font-body);
    font-size: var(--artdeco-text-compact-sm);
    color: var(--artdeco-fg-muted);
  }
}

// Parameter Form
.parameter-form {
  .form-section {
    margin-bottom: var(--artdeco-spacing-4);

    h4 {
      font-family: var(--font-display);
      font-weight: 600;
      color: var(--artdeco-gold-primary);
      margin-bottom: var(--artdeco-spacing-2);
    }

    .form-row {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: var(--artdeco-spacing-3);
    }
  }
}

// Review Content
.review-content {
  .review-item {
    display: flex;
    justify-content: space-between;
    padding: var(--artdeco-spacing-2) 0;
    border-bottom: 1px solid var(--artdeco-border-subtle);

    .review-label {
      font-family: var(--font-body);
      color: var(--artdeco-fg-muted);
    }

    .review-value {
      font-family: var(--font-display);
      font-weight: 600;
      color: var(--artdeco-fg-default);
    }
  }
}

// Results Metrics
.results-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-spacing-3);
  margin-bottom: var(--artdeco-spacing-4);
}

.metric-card {
  text-align: center;

  .metric-label {
    font-family: var(--font-body);
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-fg-muted);
    margin-bottom: var(--artdeco-spacing-1);
  }

  .metric-value {
    font-family: var(--font-display);
    font-size: var(--artdeco-text-2xl);
    font-weight: 700;
    color: var(--artdeco-fg-default);

    &.change-up {
      color: var(--artdeco-eco-green);
    }

    &.change-down {
      color: var(--artdeco-alert-red);
    }
  }
}

.backtest-chart {
  min-height: 400px;
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  padding: var(--artdeco-spacing-3);
}
</style>
```

---

## Task Breakdown & Timeline

### Immediate Tasks (This Week)

| Task | Priority | Est. Time | Status |
|------|----------|------------|--------|
| **p2-4.1**: Fix TradingDecisionCenter.vue imports | HIGH | 0.5h | ⏳ Pending |
| **p2-4.2**: Remove duplicate market data code | HIGH | 0.5h | ⏳ Pending |
| **p2-4.3**: Add missing reactive data | HIGH | 1h | ⏳ Pending |
| **p2-4.4**: Implement tradingStats from Pinia | HIGH | 1h | ⏳ Pending |
| **p2-4.5**: Implement handler methods | HIGH | 1h | ⏳ Pending |
| **p2-4.6**: Load performance data on mount | HIGH | 0.5h | ⏳ Pending |

**Subtotal**: 4.5 hours

### Next Week Tasks

| Task | Priority | Est. Time | Status |
|------|----------|------------|--------|
| **p2-5**: Create BacktestWizard.vue component | HIGH | 6-8h | ⏳ Pending |
| **p2-6**: Add parameter comparison feature | MEDIUM | 4-6h | ⏳ Pending |
| **p2-7**: Create strategy templates library | MEDIUM | 3-4h | ⏳ Pending |
| **p2-8**: Implement collapsible sidebar | MEDIUM | 4-6h | ⏳ Pending |

**Subtotal**: 17-24 hours

### Future Tasks (Week 3-4)

| Task | Priority | Est. Time | Status |
|------|----------|------------|--------|
| **p2-9**: Add ArtDeco gold dividers to sidebar | LOW | 2-3h | ⏳ Pending |
| **p2-10**: Apply ArtDeco theme to chart components | LOW | 2-3h | ⏳ Pending |
| **p2-11**: Update OpenSpec tasks.md | LOW | 1h | ⏳ Pending |

**Subtotal**: 5-7 hours

**Total Phase 2 Estimated Time**: 26.5-35.5 hours (3-4 days)

---

## Dependencies & Integration Points

### API Endpoints Needed

1. **Trading API**:
   - `POST /api/trading/order` - Create new order
   - `GET /api/trading/orders` - Get order history
   - `GET /api/trading/positions` - Get current positions
   - `GET /api/trading/portfolio` - Get portfolio summary

2. **Backtest API**:
   - `POST /api/backtest/run` - Run backtest
   - `GET /api/backtest/results/{id}` - Get backtest results
   - `GET /api/backtest/compare` - Compare multiple backtests

### Pinia Store Integration

1. **trading.ts Store**:
   - Already has `orders` state
   - Need to add: `positions`, `portfolio` state
   - Need to add: `createOrder`, `getOrders`, `getPositions`, `getPortfolio` actions

2. **tradingData.ts Store**:
   - Already has `performanceAnalysis` state
   - Already has `loadPerformanceAnalysis()` action
   - ✅ Ready to use for Portfolio tab

---

## ArtDeco V3.0 Compliance Checklist

For all new code, ensure:

- [x] **Gold CTA Buttons**: Use `class="artdeco-gold-cta"` for primary actions
- [x] **Typography**: Cinzel for headers, Barlow for body, JetBrains Mono for numbers
- [x] **Colors**: A股 convention (GREEN=↑, RED=↓), gold accents
- [x] **Spacing**: Use `var(--artdeco-spacing-*)` tokens
- [x] **Borders**: Use `var(--artdeco-border-gold)` for active states
- [x] **Animations**: Hover effects with `--artdeco-glow-subtle`
- [x] **Charts**: Apply `artDecoTheme` to all ECharts instances
- [x] **Tables**: Bloomberg Terminal 32px row height

---

## Next Steps (Priority Order)

1. **Fix TradingDecisionCenter.vue** (p2-4 completion):
   - Correct component imports
   - Remove duplicate code
   - Add reactive data and handlers
   - Integrate Pinia stores

2. **Create BacktestWizard.vue** (p2-5):
   - 4-step wizard UI
   - Strategy template selection
   - Parameter configuration form
   - Results display with metrics

3. **Test & Verify**:
   - Run TypeScript checks
   - Test all interactive features
   - Verify ArtDeco V3.0 compliance
   - Check Pinia store integration

---

**Document Version**: 1.0
**Last Updated**: 2026-01-25
**Status**: Ready for implementation review
