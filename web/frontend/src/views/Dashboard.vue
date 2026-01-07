<template>
  <div class="dashboard">

    <div class="page-header">
      <div class="section-divider"></div>
      <h1 class="page-title">市场总览</h1>
      <p class="page-subtitle">实时市场智能与投资组合监控</p>
      <div class="section-divider"></div>
    </div>

    <div class="stats-grid">
      <el-card v-for="(stat, index) in stats" :key="stat.title" :hoverable="true" class="stat-card" @click="onStatHover(stat)">
        <div class="stat-content">
          <div class="stat-icon-wrapper">
            <div class="stat-icon" :style="{ borderColor: stat.color, background: stat.colorBg }">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                <path v-if="stat.icon === 'chart'" d="M3 3v18h18"></path>
                <path v-if="stat.icon === 'chart'" d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
                <polygon v-if="stat.icon === 'star'" points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                <line v-if="stat.icon === 'up'" x1="12" y1="19" x2="12" y2="5"></line>
                <polyline v-if="stat.icon === 'up'" points="5 12 12 5 19 12"></polyline>
                <line v-if="stat.icon === 'down'" x1="12" y1="5" x2="12" y2="19"></line>
                <polyline v-if="stat.icon === 'down'" points="19 12 12 19 5 12"></polyline>
              </svg>
            </div>
          </div>
          <div class="stat-info">
            <h3 class="stat-value text-gold">{{ stat.value }}</h3>
            <span class="stat-title">{{ stat.title }}</span>
            <span class="stat-trend" :class="stat.trendClass">{{ stat.trend }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <div class="main-grid">
      <el-card title="I. 市场热度分析" :hoverable="false">
        <template #header-actions>
          <el-button type="info" size="small" @click="handleRetry" :loading="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6M1 20v-6h6"></path>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
            刷新
          </el-button>
        </template>

        <div class="tabs">
          <button v-for="tab in marketTabs" :key="tab.name" :class="[tab, { active: activeMarketTab === tab.name }]" @click="activeMarketTab = tab.name">
            {{ tab.label }}
          </button>
        </div>

        <div class="chart-container">
          <div ref="marketHeatChartRef" class="chart"></div>
        </div>
      </el-card>

      <el-card title="II. 行业资金流向" :hoverable="false">
        <template #header-actions>
          <div class="select-sm">
            <select v-model="industryStandard" @change="updateIndustryChart">
              <option value="csrc">证监会</option>
              <option value="sw_l1">申万一级</option>
              <option value="sw_l2">申万二级</option>
            </select>
          </div>
        </template>
        <div ref="industryChartRef" class="chart"></div>
      </el-card>
    </div>

    <el-card title="III. 板块表现监控" :hoverable="false">
      <template #header-actions>
        <div class="card-actions">
          <el-button type="info" size="small" @click="handleRefresh">
            刷新数据
          </el-button>
          <el-button type="info" size="small" @click="handleRetry" :loading="loading">
            重新加载
          </el-button>
        </div>
      </template>

      <div class="tabs">
        <button v-for="tab in sectorTabs" :key="tab.name" :class="[tab, { active: activeSectorTab === tab.name }]" @click="activeSectorTab = tab.name">
          {{ tab.label }}
        </button>
      </div>

      <el-table
        :columns="getSectorColumns()"
        :data="getSectorData()"
        :max-height="400"
        :loading="loading"
      >
        <template #cell-price="{ row }">
          <span :class="getChangeClass(row.change)">{{ row.price }}</span>
        </template>
        <template #cell-change="{ row, value }">
          <span :class="getChangeClass(row.change)">{{ value >= 0 ? '+' : '' }}{{ value }}%</span>
        </template>
        <template #cell-signal="{ row }">
          <el-tag :text="row.signal" :type="getSignalVariant(row.signal)" size="small" />
        </template>
        <template #cell-concepts="{ row }">
          <span v-for="concept in row.concepts" :key="concept" class="concept-tag">{{ concept }}</span>
        </template>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'
import { ElCard } from 'element-plus'
import { ElButton } from 'element-plus'
import { ElTable, ElTableColumn } from 'element-plus'

interface StatItem {
  title: string
  value: string
  icon: string
  color: string
  colorBg: string
  trend: string
  trendClass: string
}

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

const stats = ref<StatItem[]>([
  { title: 'Total Stocks', value: '5216', icon: 'chart', color: '#D4AF37', colorBg: 'rgba(212, 175, 55, 0.3)', trend: '+0%', trendClass: '' },
  { title: 'Total Market Cap', value: '--', icon: 'chart', color: '#3D9970', colorBg: 'rgba(61, 153, 112, 0.3)', trend: '--', trendClass: 'data-rise' },
  { title: 'Rising', value: '2456', icon: 'up', color: '#C94042', colorBg: 'rgba(201, 64, 66, 0.3)', trend: '--', trendClass: 'data-rise' },
  { title: 'Falling', value: '1892', icon: 'down', color: '#00E676', colorBg: 'rgba(0, 230, 118, 0.3)', trend: '--', trendClass: 'data-fall' }
])

const marketTabs = [
  { name: 'heat', label: '市场热度' },
  { name: 'leading', label: '领涨板块' },
  { name: 'distribution', label: '价格分布' },
  { name: 'capital', label: '资金流向' }
]

const sectorTabs = [
  { name: 'favorites', label: '自选股票' },
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

const onStatHover = (stat: StatItem) => console.log('Hovering stat:', stat.title)

const getSectorColumns = () => {
  switch (activeSectorTab.value) {
    case 'favorites': return [
      { key: 'symbol', label: 'CODE' }, { key: 'name', label: 'NAME' },
      { key: 'price', label: 'PRICE' }, { key: 'change', label: 'CHANGE %' },
      { key: 'volume', label: 'VOLUME' }, { key: 'turnover', label: 'TURNOVER %' }, { key: 'industry', label: 'INDUSTRY' }
    ]
    case 'strategy': return [
      { key: 'symbol', label: 'CODE' }, { key: 'name', label: 'NAME' },
      { key: 'price', label: 'PRICE' }, { key: 'change', label: 'CHANGE %' },
      { key: 'strategy', label: 'STRATEGY' }, { key: 'score', label: 'SCORE' }, { key: 'signal', label: 'SIGNAL' }
    ]
    case 'industry': return [
      { key: 'symbol', label: 'CODE' }, { key: 'name', label: 'NAME' },
      { key: 'price', label: 'PRICE' }, { key: 'change', label: 'CHANGE %' },
      { key: 'industry', label: 'INDUSTRY' }, { key: 'industryRank', label: 'RANK' }, { key: 'marketCap', label: 'MARKET CAP (亿)' }
    ]
    case 'concept': return [
      { key: 'symbol', label: 'CODE' }, { key: 'name', label: 'NAME' },
      { key: 'price', label: 'PRICE' }, { key: 'change', label: 'CHANGE %' },
      { key: 'concepts', label: 'CONCEPTS' }, { key: 'conceptHeat', label: 'HEAT' }
    ]
    default: return []
  }
}

const getSectorData = () => {
  switch (activeSectorTab.value) {
    case 'favorites': return favoriteStocks.value
    case 'strategy': return strategyStocks.value
    case 'industry': return industryStocks.value
    case 'concept': return conceptStocks.value
    default: return []
  }
}

const getChangeClass = (change: number) => change > 0 ? 'data-rise' : change < 0 ? 'data-fall' : ''
const getSignalVariant = (signal: string): 'success' | 'danger' | 'info' => {
  if (signal === '买入') return 'danger'
  if (signal === '卖出') return 'success'
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
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: { type: 'value', axisLine: { lineStyle: { color: '#5C6B7F' } }, axisLabel: { color: '#8B9BB4' } },
    yAxis: { type: 'category', data: categories, axisLine: { lineStyle: { color: '#5C6B7F' } }, axisLabel: { color: '#8B9BB4' } },
    series: [{ type: 'bar', data: values, itemStyle: { color: (p) => p.value > 0 ? '#C94042' : '#3D9970' } }]
  }
  industryChart.setOption(option)
}

const updateMarketHeatChart = () => {
  if (!marketHeatChartRef.value) return
  if (marketHeatChart) marketHeatChart.dispose()
  marketHeatChart = echarts.init(marketHeatChartRef.value)

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', axisLine: { lineStyle: { color: '#5C6B7F' } }, axisLabel: { color: '#8B9BB4' } },
    yAxis: { type: 'category', data: ['上证', '深证', '创业板'], axisLine: { lineStyle: { color: '#5C6B7F' } }, axisLabel: { color: '#8B9BB4' } },
    series: [{ type: 'bar', data: [3245, 10892, 2156], itemStyle: { color: '#D4AF37' } }]
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

.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
  padding: var(--space-xl);
  background: var(--bg-primary);
  min-height: 100vh;
}

.background-pattern {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.03;
  background-image:
    repeating-linear-gradient(45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px);
}

.dashboard > * {
  position: relative;
  z-index: 1;
}

.page-header {
  text-align: center;
  padding: var(--space-2xl) 0;

  .section-divider {
    height: 1px;
    width: 120px;
    background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    margin: 0 auto;
  }

  .page-title {
    font-family: var(--font-display);
    color: var(--gold-primary);
    font-size: 2rem;
    font-weight: 600;
    margin: var(--space-md) 0;
    letter-spacing: 0.1em;
  }

  .page-subtitle {
    font-family: var(--font-body);
    color: var(--silver-muted);
    font-size: 1rem;
    margin: 0;
    text-transform: uppercase;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-lg);
}

.stat-card {
  cursor: pointer;
  transition: all var(--transition-slow);

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--glow-medium);
  }
}

.stat-content {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) 0;
}

.stat-icon-wrapper {
  .stat-icon {
    width: 56px;
    height: 56px;
    border: 2px solid var(--gold-dim);
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.stat-info {
  flex: 1;

  .stat-value {
    font-family: var(--font-display);
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0 0 var(--space-xs) 0;
    line-height: 1.2;

    &.text-gold { color: var(--gold-primary); }
  }

  .stat-title {
    display: block;
    font-size: 0.875rem;
    color: var(--silver-text);
    margin-bottom: var(--space-xs);
  }

  .stat-trend {
    font-size: 0.875rem;
    font-weight: 600;
    font-family: var(--font-display);

    &.data-rise { color: var(--rise); }
    &.data-fall { color: var(--fall); }
  }
}

.main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-lg);
}

.chart-container {
  min-height: 350px;
}

.chart {
  height: 350px;
  width: 100%;
}

.tabs {
  display: flex;
  gap: 2px;
  border-bottom: 1px solid var(--gold-dim);
  margin-bottom: var(--space-lg);
}

.tab {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--silver-muted);
  font-family: var(--font-display);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: var(--tracking-tight);
  cursor: pointer;
  transition: all var(--transition-base);

  &:hover {
    color: var(--gold-primary);
    background: rgba(212, 175, 55, 0.05);
  }

  &.active {
    color: var(--gold-primary);
    border-bottom-color: var(--gold-primary);
    background: rgba(212, 175, 55, 0.08);
  }
}

.card-actions {
  display: flex;
  gap: var(--space-sm);
}

.select-sm {
  position: relative;

  select {
    padding: var(--space-xs) var(--space-md);
    background: var(--bg-primary);
    border: 1px solid var(--gold-dim);
    color: var(--silver-text);
    font-family: var(--font-body);
    font-size: 0.75rem;
    cursor: pointer;

    &:focus {
      outline: none;
      border-color: var(--gold-primary);
    }
  }
}

.concept-tag {
  display: inline-block;
  padding: 2px 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  font-family: var(--font-body);
  font-size: 0.75rem;
  color: var(--silver-text);
  margin-right: 4px;
  margin-bottom: 4px;
}

.data-rise { color: var(--rise); font-weight: 600; }
.data-fall { color: var(--fall); font-weight: 600; }

@media (max-width: 1440px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .main-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
  .dashboard { padding: var(--space-md); gap: var(--space-md); }
}
</style>
