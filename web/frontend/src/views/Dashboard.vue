<template>
  <div class="web3-dashboard">
    <!-- Page header with gradient text -->
    <div class="web3-page-header">
      <h1 class="web3-page-title">
        <span class="gradient-text">MARKET OVERVIEW</span>
      </h1>
      <p class="web3-page-subtitle">REAL-TIME MARKET INTELLIGENCE & PORTFOLIO MONITORING</p>
      <div class="header-actions">
        <SmartDataIndicator ref="dataIndicator" />
      </div>
    </div>

    <!-- Stats cards with Web3 design -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" v-for="(stat, index) in stats" :key="stat.title">
        <Web3Card class="stat-card" hoverable @click="onStatHover(stat)">
          <div class="stat-content">
            <div class="stat-icon-wrapper">
              <div class="stat-icon" :style="{ backgroundColor: stat.color }">
                <el-icon :size="24"><component :is="stat.icon" /></el-icon>
              </div>
            </div>
            <div class="stat-info">
              <h3 class="stat-value gradient-text">{{ stat.value }}</h3>
              <span class="stat-title">{{ stat.title }}</span>
              <span class="stat-trend" :class="stat.trendClass">
                {{ stat.trend }}
              </span>
            </div>
          </div>
        </Web3Card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :md="16">
        <Web3Card title="I. MARKET HEAT MAP" hoverable>
          <template #header>
            <div class="flex-between">
              <span class="web3-section-title">I. MARKET HEAT MAP</span>
              <Web3Button variant="outline" size="sm" @click="handleRetry" :loading="loading">
                RETRY
              </Web3Button>
            </div>
          </template>
          <el-tabs v-model="activeMarketTab" class="web3-tabs market-tabs">
            <el-tab-pane label="MARKET HEAT" name="heat">
              <div ref="marketHeatChartRef" class="web3-chart-container"></div>
            </el-tab-pane>
            <el-tab-pane label="LEADING SECTORS" name="leading">
              <div ref="leadingSectorChartRef" class="web3-chart-container"></div>
            </el-tab-pane>
            <el-tab-pane label="PRICE DISTRIBUTION" name="distribution">
              <div ref="priceDistributionChartRef" class="web3-chart-container"></div>
            </el-tab-pane>
            <el-tab-pane label="CAPITAL FLOW" name="capital">
              <div ref="capitalFlowChartRef" class="web3-chart-container"></div>
            </el-tab-pane>
          </el-tabs>
        </Web3Card>
      </el-col>

      <el-col :xs="24" :md="8">
        <Web3Card title="II. CAPITAL FLOW" hoverable>
          <template #header>
            <div class="flex-between">
              <span class="web3-section-title">II. CAPITAL FLOW</span>
              <el-select v-model="industryStandard" size="small" style="width: 140px" @change="updateIndustryChart">
                <el-option label="CSRC" value="csrc" />
                <el-option label="SW L1" value="sw_l1" />
                <el-option label="SW L2" value="sw_l2" />
              </el-select>
            </div>
          </template>
          <div ref="industryChartRef" class="web3-chart-container"></div>
        </Web3Card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="sectors-row">
      <el-col :span="24">
        <Web3Card title="III. SECTOR PERFORMANCE" hoverable>
          <template #header>
            <div class="flex-between">
              <span class="web3-section-title">III. SECTOR PERFORMANCE</span>
              <div class="card-actions">
                <Web3Button variant="outline" size="sm" @click="handleRefresh">
                  REFRESH
                </Web3Button>
                <Web3Button variant="outline" size="sm" @click="handleRetry" :loading="loading">
                  RETRY
                </Web3Button>
              </div>
            </div>
          </template>
          <el-tabs v-model="activeSectorTab" class="web3-tabs sector-tabs">
            <el-tab-pane label="FAVORITES" name="favorites">
              <el-table :data="favoriteStocks" v-loading="loading" max-height="400" class="web3-table">
                <el-table-column prop="symbol" label="CODE" width="100" />
                <el-table-column prop="name" label="NAME" width="120" />
                <el-table-column prop="price" label="PRICE" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-up' : row.change < 0 ? 'text-down' : ''">
                      {{ row.price }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="change" label="CHANGE %" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-up' : row.change < 0 ? 'text-down' : ''">
                      {{ row.change > 0 ? '+' : '' }}{{ row.change }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="volume" label="VOLUME" width="120" align="right" />
                <el-table-column prop="turnover" label="TURNOVER %" width="100" align="right">
                  <template #default="{ row }">{{ row.turnover }}%</template>
                </el-table-column>
                <el-table-column prop="industry" label="INDUSTRY" />
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="STRATEGY" name="strategy">
              <el-table :data="strategyStocks" v-loading="loading" max-height="400" class="web3-table">
                <el-table-column prop="symbol" label="CODE" width="100" />
                <el-table-column prop="name" label="NAME" width="120" />
                <el-table-column prop="price" label="PRICE" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-up' : row.change < 0 ? 'text-down' : ''">
                      {{ row.price }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="change" label="CHANGE %" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-up' : row.change < 0 ? 'text-down' : ''">
                      {{ row.change > 0 ? '+' : '' }}{{ row.change }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="strategy" label="STRATEGY" width="120" />
                <el-table-column prop="score" label="SCORE" width="80" align="right" />
                <el-table-column prop="signal" label="SIGNAL" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.signal === '买入' ? 'danger' : row.signal === '卖出' ? 'success' : 'info'" size="small">
                      {{ row.signal }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="INDUSTRY" name="industry">
              <el-table :data="industryStocks" v-loading="loading" max-height="400" class="web3-table">
                <el-table-column prop="symbol" label="CODE" width="100" />
                <el-table-column prop="name" label="NAME" width="120" />
                <el-table-column prop="price" label="PRICE" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-up' : row.change < 0 ? 'text-down' : ''">
                      {{ row.price }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="change" label="CHANGE %" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-up' : row.change < 0 ? 'text-down' : ''">
                      {{ row.change > 0 ? '+' : '' }}{{ row.change }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="industry" label="INDUSTRY" width="120" />
                <el-table-column prop="industryRank" label="RANK" width="100" align="center" />
                <el-table-column prop="marketCap" label="MARKET CAP (亿)" width="140" align="right" />
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="CONCEPT" name="concept">
              <el-table :data="conceptStocks" v-loading="loading" max-height="400" class="web3-table">
                <el-table-column prop="symbol" label="CODE" width="100" />
                <el-table-column prop="name" label="NAME" width="120" />
                <el-table-column prop="price" label="PRICE" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-up' : row.change < 0 ? 'text-down' : ''">
                      {{ row.price }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="change" label="CHANGE %" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-up' : row.change < 0 ? 'text-down' : ''">
                      {{ row.change > 0 ? '+' : '' }}{{ row.change }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="concepts" label="CONCEPTS" min-width="200">
                  <template #default="{ row }">
                    <el-tag v-for="concept in row.concepts" :key="concept" size="small" style="margin-right: 5px">
                      {{ concept }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="conceptHeat" label="HEAT" width="100" align="right" />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </Web3Card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck

import { ref, onMounted, nextTick, watch, type Ref } from 'vue'
import { dataApi } from '@/api'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'
import { ElMessage } from 'element-plus'
import SmartDataIndicator from '@/components/common/SmartDataIndicator.vue'
import type { MarketOverviewVM, MarketStats } from '@/api/types/market'
import { Web3Card, Web3Button } from '@/components/web3'

// ============================================
//   TYPE DEFINITIONS - 类型定义
// ============================================

interface StatItem {
  title: string
  value: string
  icon: string
  color: string
  trend: string
  trendClass: 'up' | 'down' | 'neutral'
}

interface StockTableRow {
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

type ChartRef = Ref<HTMLDivElement | null>

// ============================================
//   COMPOSABLES - 可组合函数
// ============================================

const { marketOverview, loading: marketLoading, fetchMarketOverview } = useMarket({ autoFetch: false })
const loading = computed(() => marketLoading.value)

// ============================================
//   REACTIVE STATE - 响应式状态
// ============================================

const activeMarketTab: Ref<string> = ref('heat')
const activeSectorTab: Ref<string> = ref('favorites')
const industryStandard: Ref<string> = ref('csrc')

// Chart references
const marketHeatChartRef: ChartRef = ref(null)
const leadingSectorChartRef: ChartRef = ref(null)
const priceDistributionChartRef: ChartRef = ref(null)
const capitalFlowChartRef: ChartRef = ref(null)
const industryChartRef: ChartRef = ref(null)

// Data arrays
const favoriteStocks: Ref<StockTableRow[]> = ref([])
const strategyStocks: Ref<StockTableRow[]> = ref([])
const industryStocks: Ref<StockTableRow[]> = ref([])
const conceptStocks: Ref<StockTableRow[]> = ref([])

const stats: Ref<StatItem[]> = ref([
  { title: 'Total Stocks', value: '0', icon: 'Document', color: '#409EFF', trend: '+0%', trendClass: 'neutral' },
  { title: 'Total Market Cap', value: '--', icon: 'Money', color: '#67C23A', trend: '--', trendClass: 'up' },
  { title: 'Rising', value: '0', icon: 'Top', color: '#F7931A', trend: '--', trendClass: 'up' },
  { title: 'Falling', value: '0', icon: 'Bottom', color: '#00E676', trend: '--', trendClass: 'down' }
])

// Chart instances
let marketHeatChart: ECharts | null = null
let leadingSectorChart: ECharts | null = null
let priceDistributionChart: ECharts | null = null
let capitalFlowChart: ECharts | null = null
let industryChart: ECharts | null = null

// ============================================
//   UTILITY FUNCTIONS - 工具函数
// ============================================

const onStatHover = (stat: StatItem): void => {
  console.log('Hovering stat:', stat.title)
}

// ============================================
//   CHART FUNCTIONS - 图表函数
// ============================================

const updateIndustryChart = async (): Promise<void> => {
  if (!industryChartRef.value) return
  if (industryChart) industryChart.dispose()
  industryChart = echarts.init(industryChartRef.value)

  try {
    const mockData = {
      categories: ['BANKING', 'REAL ESTATE', 'PHARMA', 'FOOD & BEV', 'ELECTRONICS', 'IT', 'MACHINERY', 'CHEMICAL', 'AUTO', 'APPLIANCES'],
      values: [120, -50, 80, 65, -30, 90, 45, -20, 70, 55]
    }

    const option: EChartsOption = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: 'rgba(3, 3, 4, 0.95)',
        borderColor: '#F7931A',
        textStyle: { color: '#E5E7EB' }
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: {
        type: 'value',
        name: 'CAPITAL FLOW (100M)',
        nameTextStyle: { color: '#9CA3AF' },
        axisLine: { lineStyle: { color: '#374151' } },
        axisLabel: { color: '#9CA3AF' }
      },
      yAxis: {
        type: 'category',
        data: mockData.categories,
        axisLine: { lineStyle: { color: '#374151' } },
        axisLabel: { color: '#9CA3AF' }
      },
      series: [{
        name: 'CAPITAL FLOW',
        type: 'bar',
        data: mockData.values,
        itemStyle: {
          color: (params: any) => params.value > 0 ? '#F7931A' : '#00E676'
        }
      }]
    }
    industryChart.setOption(option)
  } catch (error) {
    console.error('Failed to load industry capital flow data:', error)
  }
}

const updateMarketHeatChart = (marketIndex?: { [key: string]: number }): void => {
  if (!marketHeatChartRef.value) return

  if (marketHeatChart) marketHeatChart.dispose()
  marketHeatChart = echarts.init(marketHeatChartRef.value)

  const data = marketIndex ? Object.keys(marketIndex).map(key => ({
    name: key,
    value: marketIndex[key]
  })) : []

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(3, 3, 4, 0.95)',
      borderColor: '#F7931A',
      textStyle: { color: '#E5E7EB' }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      name: 'INDEX POINT',
      nameTextStyle: { color: '#9CA3AF' },
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#9CA3AF' }
    },
    yAxis: {
      type: 'category',
      data: data.map(d => d.name),
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#9CA3AF' }
    },
    series: [{
      name: 'MARKET INDEX',
      type: 'bar',
      data: data.map(d => d.value),
      itemStyle: { color: '#F7931A' }
    }]
  }
  marketHeatChart.setOption(option)
}

const updatePriceDistributionChart = (stats: MarketStats): void => {
  if (!priceDistributionChartRef.value) return

  if (priceDistributionChart) priceDistributionChart.dispose()
  priceDistributionChart = echarts.init(priceDistributionChartRef.value)

  const data = [
    { name: 'RISING', value: stats.risingStocks, itemStyle: { color: '#F7931A' } },
    { name: 'FALLING', value: stats.fallingStocks, itemStyle: { color: '#00E676' } },
    { name: 'FLAT', value: stats.totalStocks - stats.risingStocks - stats.fallingStocks, itemStyle: { color: '#6B7280' } }
  ]

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} STOCKS ({d}%)',
      backgroundColor: 'rgba(3, 3, 4, 0.95)',
      borderColor: '#F7931A',
      textStyle: { color: '#E5E7EB' }
    },
    legend: {
      bottom: '5%',
      left: 'center',
      textStyle: { color: '#E5E7EB' }
    },
    series: [{
      name: 'PRICE DISTRIBUTION',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      data: data,
      label: {
        show: true,
        formatter: '{b}\n{c} STOCKS',
        color: '#E5E7EB'
      }
    }]
  }
  priceDistributionChart.setOption(option)
}

const initCharts = async (): Promise<void> => {
  await nextTick()
  if (marketOverview.value) {
    updateMarketHeatChart(marketOverview.value.marketIndex)
    updatePriceDistributionChart(marketOverview.value.marketStats)
  }
  await updateIndustryChart()

  window.addEventListener('resize', () => {
    marketHeatChart?.resize()
    leadingSectorChart?.resize()
    priceDistributionChart?.resize()
    capitalFlowChart?.resize()
    industryChart?.resize()
  })
}

// ============================================
//   WATCHERS - 监听器
// ============================================

watch(activeMarketTab, async () => {
  await nextTick()
  switch (activeMarketTab.value) {
    case 'heat': marketHeatChart?.resize(); break
    case 'leading': leadingSectorChart?.resize(); break
    case 'distribution': priceDistributionChart?.resize(); break
    case 'capital': capitalFlowChart?.resize(); break
  }
})

watch(marketOverview, (newVal) => {
  if (newVal) {
    stats.value[0].value = newVal.marketStats.totalStocks.toString()
    stats.value[2].value = newVal.marketStats.risingStocks.toString()
    stats.value[3].value = newVal.marketStats.fallingStocks.toString()

    updateMarketHeatChart(newVal.marketIndex)
    updatePriceDistributionChart(newVal.marketStats)
  }
})

// ============================================
//   DATA LOADING - 数据加载
// ============================================

const loadData = async (): Promise<void> => {
  try {
    await fetchMarketOverview(true)
    if (!marketOverview.value) {
      throw new Error('No data received')
    }
  } catch (error) {
    console.error('Failed to load data:', error)
    ElMessage.error('FAILED TO LOAD DATA')
  }
}

const handleRetry = async (): Promise<void> => {
  await loadData()
}

const handleRefresh = (): void => {
  loadData()
}

// ============================================
//   LIFECYCLE - 生命周期
// ============================================

onMounted(() => {
  initCharts()
  loadData()
})
</script>

<style scoped lang="scss">
@import '@/styles/web3-tokens.scss';
@import '@/styles/web3-global.scss';

.web3-dashboard {
  @include web3-grid-bg;
  min-height: 100vh;
  padding: var(--web3-spacing-6);

  .web3-page-header {
    text-align: center;
    padding: var(--web3-spacing-10) 0;
    margin-bottom: var(--web3-spacing-8);

    .web3-page-title {
      font-family: var(--web3-font-heading);
      font-size: var(--web3-text-4xl);
      font-weight: var(--web3-weight-bold);
      margin: 0 0 var(--web3-spacing-3) 0;
      line-height: var(--web3-leading-tight);

      .gradient-text {
        background: var(--web3-gradient-orange);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }

    .web3-page-subtitle {
      font-family: var(--web3-font-body);
      font-size: var(--web3-text-sm);
      color: var(--web3-fg-muted);
      text-transform: uppercase;
      letter-spacing: var(--web3-tracking-wide);
      margin: 0;
    }

    .header-actions {
      margin-top: var(--web3-spacing-4);
    }
  }

  .stats-row {
    margin-bottom: var(--web3-spacing-6);

    .stat-card {
      cursor: pointer;

      .stat-content {
        display: flex;
        align-items: center;
        gap: var(--web3-spacing-4);
        padding: var(--web3-spacing-4) 0;

        .stat-icon-wrapper {
          .stat-icon {
            width: 56px;
            height: 56px;
            border-radius: var(--web3-radius-lg);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
          }
        }

        .stat-info {
          flex: 1;

          .stat-value {
            font-size: var(--web3-text-3xl);
            font-weight: var(--web3-weight-bold);
            margin: 0 0 var(--web3-spacing-1) 0;
            font-family: var(--web3-font-mono);

            &.gradient-text {
              background: var(--web3-gradient-orange);
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
              background-clip: text;
            }
          }

          .stat-title {
            display: block;
            font-size: var(--web3-text-xs);
            text-transform: uppercase;
            letter-spacing: var(--web3-tracking-wide);
            color: var(--web3-fg-muted);
            margin-bottom: var(--web3-spacing-1);
          }

          .stat-trend {
            font-size: var(--web3-text-xs);
            font-family: var(--web3-font-mono);

            &.up {
              color: #F7931A;
            }

            &.down {
              color: #00E676;
            }

            &.neutral {
              color: var(--web3-fg-muted);
            }
          }
        }
      }
    }
  }

  .charts-row,
  .sectors-row {
    margin-bottom: var(--web3-spacing-6);
  }

  .web3-section-title {
    font-family: var(--web3-font-heading);
    font-size: var(--web3-text-lg);
    font-weight: var(--web3-weight-semibold);
    color: var(--web3-fg-primary);
    text-transform: uppercase;
    letter-spacing: var(--web3-tracking-wide);
  }

  .web3-chart-container {
    height: 350px;
    width: 100%;
  }

  .web3-table {
    :deep(.el-table__header) {
      th {
        background: rgba(255, 255, 255, 0.02) !important;
        color: var(--web3-fg-secondary) !important;
        font-family: var(--web3-font-heading);
        font-weight: var(--web3-weight-semibold);
        text-transform: uppercase;
        border-bottom: 1px solid var(--web3-border-subtle) !important;
      }
    }

    :deep(.el-table__body) {
      tr {
        background: transparent !important;
        transition: background var(--web3-duration-fast);

        &:hover {
          background: rgba(247, 147, 26, 0.05) !important;
        }

        td {
          border-bottom: 1px solid var(--web3-border-subtle) !important;
          color: var(--web3-fg-primary);
        }
      }
    }
  }

  .text-up {
    color: #F7931A !important;
    font-weight: var(--web3-weight-semibold);
  }

  .text-down {
    color: #00E676 !important;
    font-weight: var(--web3-weight-semibold);
  }

  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .card-actions {
    display: flex;
    gap: var(--web3-spacing-2);
  }
}
</style>
