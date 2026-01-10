<template>
  <div class="dashboard-container">

    <!-- Bloomberg-style Header -->
    <div class="dashboard-header">
      <div class="header-title-section">
        <div class="header-divider-left"></div>
        <div class="header-text">
          <h1 class="page-title">MARKET OVERVIEW</h1>
          <p class="page-subtitle">REAL-TIME MARKET INTELLIGENCE & PORTFOLIO MONITORING</p>
        </div>
        <div class="header-divider-right"></div>
      </div>
    </div>

    <!-- Bloomberg-style Stat Cards -->
    <div class="stats-grid">
      <BloombergStatCard
        label="TOTAL STOCKS"
        :value="5216"
        icon="data"
        format="number"
        :loading="loading"
      />

      <BloombergStatCard
        label="RISING"
        :value="2456"
        icon="trending-up"
        trend="up"
        format="number"
        :loading="loading"
      />

      <BloombergStatCard
        label="FALLING"
        :value="1892"
        icon="trending-down"
        trend="down"
        format="number"
        :loading="loading"
      />

      <BloombergStatCard
        label="UNCHANGED"
        :value="868"
        icon="chart"
        trend="neutral"
        format="number"
        :loading="loading"
      />
    </div>

    <!-- Main Grid -->
    <div class="main-grid">
      <!-- Market Heat Analysis Card -->
       <el-card class="bloomberg-card">
         <template #header>
           <div class="card-header">
             <span class="card-title">I. MARKET HEAT ANALYSIS</span>
             <el-button type="primary" size="small" @click="handleRetry" :loading="loading">
               REFRESH
             </el-button>
           </div>
         </template>

        <!-- Bloomberg-style Tabs -->
        <div class="bloomberg-tabs">
          <button
            v-for="tab in marketTabs"
            :key="tab.name"
            :class="['bloomberg-tab', { active: activeMarketTab === tab.name }]"
            @click="activeMarketTab = tab.name"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="chart-container">
          <div ref="marketHeatChartRef" class="chart"></div>
        </div>
      </el-card>

      <!-- Industry Capital Flow Card -->
       <el-card class="bloomberg-card">
         <template #header>
           <div class="card-header">
             <span class="card-title">II. INDUSTRY FLOW</span>
             <select v-model="industryStandard" @change="updateIndustryChart" class="bloomberg-select">
               <option value="csrc">CSRC</option>
               <option value="sw_l1">SW L1</option>
               <option value="sw_l2">SW L2</option>
             </select>
           </div>
         </template>
        <div ref="industryChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Sector Performance Card -->
     <el-card class="bloomberg-card">
       <template #header>
         <div class="card-header">
           <span class="card-title">III. SECTOR PERFORMANCE</span>
           <div class="card-actions">
             <el-button type="info" size="small" @click="handleRefresh">
               REFRESH
             </el-button>
             <el-button type="primary" size="small" @click="handleRetry" :loading="loading">
               RELOAD
             </el-button>
           </div>
         </div>
       </template>

      <!-- Bloomberg-style Tabs -->
      <div class="bloomberg-tabs">
        <button
          v-for="tab in sectorTabs"
          :key="tab.name"
          :class="['bloomberg-tab', { active: activeSectorTab === tab.name }]"
          @click="activeSectorTab = tab.name"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Bloomberg-style Table -->
      <el-table
        :data="getSectorData()"
        :loading="loading"
        class="bloomberg-table"
        stripe
        border
        max-height="400"
      >
        <el-table-column prop="symbol" label="CODE" width="120" />
        <el-table-column prop="name" label="NAME" width="180" />
        <el-table-column prop="price" label="PRICE" width="120" align="right">
          <template #default="{ row }">
            <span class="mono-text" :class="getChangeClass(row.change)">{{ row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="change" label="CHANGE %" width="120" align="right">
          <template #default="{ row }">
            <span class="mono-text" :class="getChangeClass(row.change)">
              {{ row.change >= 0 ? '+' : '' }}{{ row.change }}%
            </span>
          </template>
        </el-table-column>
        <!-- Dynamic columns based on active tab -->
        <el-table-column v-if="activeSectorTab === 'favorites'" prop="volume" label="VOLUME" width="120" align="right">
          <template #default="{ row }">
            <span class="mono-text">{{ row.volume }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="activeSectorTab === 'favorites'" prop="turnover" label="TURNOVER %" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-text">{{ row.turnover }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="activeSectorTab === 'favorites'" prop="industry" label="INDUSTRY" width="140" />
        <el-table-column v-if="activeSectorTab === 'strategy'" prop="strategy" label="STRATEGY" width="140" />
        <el-table-column v-if="activeSectorTab === 'strategy'" prop="score" label="SCORE" width="100" align="right">
          <template #default="{ row }">
            <span class="mono-text">{{ row.score }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="activeSectorTab === 'strategy'" prop="signal" label="SIGNAL" width="120">
          <template #default="{ row }">
            <el-tag :type="getSignalVariant(row.signal)" size="small">
              {{ row.signal }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="activeSectorTab === 'industry'" prop="industry" label="INDUSTRY" width="140" />
        <el-table-column v-if="activeSectorTab === 'industry'" prop="industryRank" label="RANK" width="100" align="right">
          <template #default="{ row }">
            <span class="mono-text">{{ row.industryRank }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="activeSectorTab === 'industry'" prop="marketCap" label="MARKET CAP (亿)" width="180" align="right">
          <template #default="{ row }">
            <span class="mono-text">{{ row.marketCap }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="activeSectorTab === 'concept'" label="CONCEPTS" width="300">
          <template #default="{ row }">
            <span v-for="concept in row.concepts" :key="concept" class="concept-tag">
              {{ concept }}
            </span>
          </template>
        </el-table-column>
        <el-table-column v-if="activeSectorTab === 'concept'" prop="conceptHeat" label="HEAT" width="100" align="right">
          <template #default="{ row }">
            <span class="mono-text">{{ row.conceptHeat }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'
import { ElCard, ElButton, ElTable, ElTableColumn, ElTag } from 'element-plus'
import BloombergStatCard from '@/components/BloombergStatCard.vue'


interface StockRow {
  symbol: string
  name: string
  price: string
  change: number
  volume?: string
  turnover?: string
  industry?: string
  strategy?: string
  score?: number
  signal?: string
  industryRank?: number
  marketCap?: number
  concepts?: string[]
  conceptHeat?: number
}

const loading = ref(false)
const activeMarketTab = ref('heat')
const activeSectorTab = ref('favorites')
const industryStandard = ref('csrc')

const marketTabs = [
  { name: 'heat', label: 'MARKET HEAT' },
  { name: 'leading', label: 'LEADING' },
  { name: 'distribution', label: 'DISTRIBUTION' },
  { name: 'capital', label: 'CAPITAL FLOW' }
]

const sectorTabs = [
  { name: 'favorites', label: 'FAVORITES' },
  { name: 'strategy', label: 'STRATEGY' },
  { name: 'industry', label: 'INDUSTRY' },
  { name: 'concept', label: 'CONCEPT' }
]

const favoriteStocks = ref<StockRow[]>([
  { symbol: '600519', name: '贵州茅台', price: '1678.50', change: 1.23, volume: '2.35万', turnover: '0.15' },
  { symbol: '000858', name: '五粮液', price: '156.78', change: -0.56, volume: '8.45万', turnover: '0.28' }
])

const strategyStocks = ref<StockRow[]>([
  { symbol: '600519', name: '贵州茅台', price: '1678.50', change: 1.23, strategy: 'MA Cross', score: 85, signal: '买入' },
  { symbol: '000858', name: '五粮液', price: '156.78', change: -0.56, strategy: 'RSI Rev', score: 72, signal: '持有' }
])

const industryStocks = ref<StockRow[]>([
  { symbol: '600519', name: '贵州茅台', price: '1678.50', change: 1.23, industry: '白酒', industryRank: 1, marketCap: 21000 },
  { symbol: '000858', name: '五粮液', price: '156.78', change: -0.56, industry: '白酒', industryRank: 2, marketCap: 6100 }
])

const conceptStocks = ref<StockRow[]>([
  { symbol: '600519', name: '贵州茅台', price: '1678.50', change: 1.23, concepts: ['白酒', '龙头'], conceptHeat: 95 },
  { symbol: '300750', name: '宁德时代', price: '198.50', change: 3.45, concepts: ['新能源', '锂电池'], conceptHeat: 88 }
])


const marketHeatChartRef = ref<HTMLElement>()
const industryChartRef = ref<HTMLElement>()

let marketHeatChart: ECharts | null = null
let industryChart: ECharts | null = null

const getSectorData = () => {
  switch (activeSectorTab.value) {
    case 'favorites': return favoriteStocks.value
    case 'strategy': return strategyStocks.value
    case 'industry': return industryStocks.value
    case 'concept': return conceptStocks.value
    default: return []
  }
}

const getChangeClass = (change: number) => change > 0 ? 'change-up' : change < 0 ? 'change-down' : ''
const getSignalVariant = (signal: string): 'success' | 'danger' | 'info' => {
  if (signal === '买入' || signal === 'BUY') return 'danger'
  if (signal === '卖出' || signal === 'SELL') return 'success'
  return 'info'
}

const updateIndustryChart = async () => {
  if (!industryChartRef.value) return
  if (industryChart) industryChart.dispose()
  industryChart = echarts.init(industryChartRef.value)

  const categories = ['银行', '地产', '医药', '食品', '电子', 'IT']
  const values = [120, -50, 80, 65, -30, 90]

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: '#0F1115',
      borderColor: '#0080FF',
      textStyle: { color: '#FFFFFF' }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#1E293B' } },
      axisLabel: { color: '#94A3B8', fontFamily: 'IBM Plex Sans' },
      splitLine: { lineStyle: { color: '#1E293B' } }
    },
    yAxis: {
      type: 'category',
      data: categories,
      axisLine: { lineStyle: { color: '#1E293B' } },
      axisLabel: { color: '#94A3B8', fontFamily: 'IBM Plex Sans' }
    },
    series: [{
      type: 'bar',
      data: values,
      itemStyle: {
        color: (p: { value: number }) => p.value > 0 ? '#FF3B30' : '#00E676'
      }
    }]
  }
  industryChart.setOption(option)
}

const updateMarketHeatChart = () => {
  if (!marketHeatChartRef.value) return
  if (marketHeatChart) marketHeatChart.dispose()
  marketHeatChart = echarts.init(marketHeatChartRef.value)

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#0F1115',
      borderColor: '#0080FF',
      textStyle: { color: '#FFFFFF' }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#1E293B' } },
      axisLabel: { color: '#94A3B8', fontFamily: 'IBM Plex Sans' },
      splitLine: { lineStyle: { color: '#1E293B' } }
    },
    yAxis: {
      type: 'category',
      data: ['上证', '深证', '创业板'],
      axisLine: { lineStyle: { color: '#1E293B' } },
      axisLabel: { color: '#94A3B8', fontFamily: 'IBM Plex Sans' }
    },
    series: [{
      type: 'bar',
      data: [3245, 10892, 2156],
      itemStyle: { color: '#0080FF' }
    }]
  }
  marketHeatChart.setOption(option)
}

const initCharts = async () => {
  await nextTick()
  updateMarketHeatChart()
  await updateIndustryChart()

  window.addEventListener('resize', () => {
    marketHeatChart?.resize()
    industryChart?.resize()
  })
}

const loadData = async () => {
  loading.value = true
  await new Promise(r => setTimeout(r, 500))
  loading.value = false
}

const handleRetry = async () => { await loadData() }
const handleRefresh = () => { loadData() }

onMounted(() => {
  initCharts()
  loadData()
})
</script>

<style scoped lang="scss">
@use 'sass:color';
@import '@/styles/theme-tokens.scss';

// ============================================
//   Bloomberg Terminal Style Dashboard
//   Phase 3.3: Design Token Migration
// ============================================

.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: var(--color-bg-primary);
  min-height: 100vh;
}

// Bloomberg-style Header
.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl) 0;
  border-bottom: 2px solid var(--color-border);
  margin-bottom: var(--spacing-lg);

  .header-title-section {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
  }

  .header-divider-left,
  .header-divider-right {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, var(--color-accent) 50%, transparent 100%);
  }

  .header-divider-left {
    max-width: 120px;
  }

  .header-divider-right {
    max-width: 120px;
  }

  .header-text {
    text-align: center;
  }

  .page-title {
    font-family: var(--font-family-sans);
    font-size: var(--font-size-3xl);
    font-weight: var(--font-weight-bold);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--color-accent);
    margin: 0 0 var(--spacing-sm) 0;
    line-height: var(--line-height-tight);
  }

  .page-subtitle {
    font-family: var(--font-family-sans);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--color-text-secondary);
    margin: 0;
  }
}

// Stats Grid
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;

  @media (max-width: 1440px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

// Main Grid
.main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;

  @media (max-width: 1440px) {
    grid-template-columns: 1fr;
  }
}

// Bloomberg Card
.bloomberg-card {
  background: linear-gradient(135deg, rgba(15, 17, 21, 0.8) 0%, rgba(30, 41, 59, 0.8) 100%);
  border: 1px solid rgba(247, 147, 26, 0.3);
  border-radius: 8px;

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(247, 147, 26, 0.3);

    .card-title {
      font-family: 'JetBrains Mono', monospace;
      font-size: 14px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: #F7931A;
    }

    .card-actions {
      display: flex;
      gap: 8px;
    }
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;

    .card-title {
      font-family: var(--font-family-sans);
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-semibold);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--color-accent);
    }

    .card-actions {
      display: flex;
      gap: 12px;
    }
  }
}

// Bloomberg-style Select
.bloomberg-select {
  padding: 6px 12px;
  background: rgba(15, 17, 21, 0.8);
  border: 1px solid rgba(247, 147, 26, 0.3);
  border-radius: 6px;
  color: #E5E7EB;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: #F7931A;
    box-shadow: 0 0 0 2px rgba(247, 147, 26, 0.2);
  }

  option {
    background: rgba(15, 17, 21, 0.8);
    color: #E5E7EB;
  }
}

// Bloomberg-style Tabs
.bloomberg-tabs {
  display: flex;
  gap: 2px;
  border-bottom: 2px solid var(--color-border);
  margin-bottom: var(--spacing-lg);
}

.bloomberg-tab {
  display: flex;
  align-items: center;
  padding: var(--spacing-md) 20px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--color-text-secondary);
  font-family: var(--font-family-sans);
  font-size: var(--font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-fast) ease;

  &:hover {
    color: var(--color-accent);
    background: var(--color-accent-alpha-90);
  }

  &.active {
    color: var(--color-accent);
    border-bottom-color: var(--color-accent);
    background: var(--color-accent-alpha-90);
  }
}

// Chart Container
.chart-container {
  min-height: 350px;
  padding: 20px 0;
}

.chart {
  height: 350px;
  width: 100%;
}

// Bloomberg Table Styling
.bloomberg-table {
  background: transparent !important;

  :deep(.el-table__header-wrapper) {
    background: var(--color-bg-primary);
    border-bottom: 2px solid var(--color-border);

    th {
      background: var(--color-bg-primary) !important;
      border-bottom: 1px solid var(--color-border);
      color: var(--color-text-secondary);
      font-family: var(--font-family-sans);
      font-size: var(--font-size-xs);
      font-weight: var(--font-weight-semibold);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      padding: var(--spacing-md) 0;
    }
  }

  :deep(.el-table__body-wrapper) {
    background: transparent;

    tr {
      background: transparent !important;
      transition: background var(--transition-fast) ease;

      &:hover {
        background: var(--color-accent-alpha-90) !important;
      }

      td {
        border-bottom: 1px solid var(--color-border);
        color: var(--color-text-secondary);
        font-family: var(--font-family-mono);
        font-size: var(--font-size-sm);
        padding: var(--spacing-md) 0;
      }
    }
  }

  .mono-text {
    font-family: var(--font-family-mono);
    font-size: var(--font-size-sm);
    color: var(--color-text-primary);
  }
}

// Concept Tags
.concept-tag {
  display: inline-block;
  padding: 4px var(--spacing-sm);
  background: var(--color-accent-alpha-90);
  border: 1px solid var(--color-accent-alpha-70);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-sans);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-accent);
  margin-right: 6px;
  margin-bottom: 6px;
}

// Change Classes (Stock Colors - Red Up Green Down for China)
.change-up {
  color: var(--color-stock-down) !important;
  font-weight: var(--font-weight-semibold);
}

.change-down {
  color: var(--color-stock-up) !important;
  font-weight: var(--font-weight-semibold);
}

// Responsive Design (Desktop-only as per project requirements)
@media (max-width: 1440px) {
  .dashboard-container {
    padding: 20px;
    gap: 20px;
  }

  .dashboard-header {
    padding: var(--spacing-lg) 0;

    .header-title-section {
      flex-direction: column;
      gap: var(--spacing-md);
    }

    .header-divider-left,
    .header-divider-right {
      max-width: 80px;
    }

    .page-title {
      font-size: var(--font-size-2xl);
    }
  }

  .main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  // NOTE: Mobile styles kept for compatibility but not actively maintained
  .dashboard-container {
    padding: var(--spacing-md);
    gap: var(--spacing-md);
  }

  .dashboard-header {
    padding: 20px 0;

    .header-divider-left,
    .header-divider-right {
      display: none;
    }

    .page-title {
      font-size: var(--font-size-xl);
    }

    .page-subtitle {
      font-size: var(--font-size-xs);
    }
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
