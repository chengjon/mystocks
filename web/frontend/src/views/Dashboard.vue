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
            v-for="(tab, _idx) in marketTabs"
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
          v-for="(tab, _idx) in sectorTabs"
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
import { ref, onMounted, nextTick , onUnmounted } from 'vue'
import echarts from '@/utils/echarts'
import type { EChartsOption } from 'echarts'

// ECharts instance type
type ECharts = ReturnType<typeof echarts.init>

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

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})
</script>

<style scoped lang="scss">
@use "./styles/Dashboard.scss" as *;
</style>
