<template>
  <div class="market-overview-container">
    <!-- 市场概览主容器 -->
    <div class="market-overview-header">
      <h2 class="market-overview-title">市场概览</h2>
      <div class="market-overview-actions">
        <button class="btn-primary" @click="refreshData">刷新数据</button>
        <button class="btn-secondary" @click="exportReport">导出报告</button>
      </div>
    </div>

    <!-- 市场指数卡片 -->
    <div class="market-indices-grid">
      <div class="card market-index-card" v-for="index in marketIndices" :key="index.code">
        <div class="card-header">
          <span class="index-name">{{ index.name }}</span>
          <span class="index-code">{{ index.code }}</span>
          <span class="index-value" :class="getIndexValueClass(index.change)">
            {{ formatValue(index.value) }}
          </span>
          <span class="index-change" :class="getChangeClass(index.change)">
            {{ formatChange(index.change) }}
          </span>
        </div>
        <div class="card-body">
          <div class="index-chart">
            <canvas :id="`chart-${index.code}`" :height="200"></canvas>
          </div>
          <div class="index-details">
            <div class="index-detail">
              <span class="detail-label">最高</span>
              <span class="detail-value">{{ formatValue(index.high) }}</span>
            </div>
            <div class="index-detail">
              <span class="detail-label">最低</span>
              <span class="detail-value">{{ formatValue(index.low) }}</span>
            </div>
            <div class="index-detail">
              <span class="detail-label">成交量</span>
              <span class="detail-value">{{ formatVolume(index.volume) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 市场统计卡片 -->
    <div class="market-stats-grid">
      <div class="card market-stat-card">
        <div class="card-header">
          <span class="stat-title">市场统计</span>
          <span class="stat-period">今日</span>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">总成交额</span>
              <span class="stat-value">{{ formatMoney(totalTurnover) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总成交量</span>
              <span class="stat-value">{{ formatVolume(totalVolume) }}</span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">上涨家数</span>
              <span class="stat-value">{{ stockUpCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">下跌家数</span>
              <span class="stat-value">{{ stockDownCount }}</span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">涨停家数</span>
              <span class="stat-value">{{ limitUpCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">跌停家数</span>
              <span class="stat-value">{{ limitDownCount }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card market-stat-card">
        <div class="card-header">
          <span class="stat-title">行业涨跌</span>
          <span class="stat-period">今日</span>
        </div>
        <div class="card-body">
          <div class="sector-list">
            <div class="sector-item" v-for="sector in topSectors" :key="sector.name">
              <span class="sector-name">{{ sector.name }}</span>
              <span class="sector-change" :class="getSectorChangeClass(sector.change)">
                {{ formatChange(sector.change) }}
              </span>
              <span class="sector-percentage">{{ sector.percentage }}%</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card market-stat-card">
        <div class="card-header">
          <span class="stat-title">热点概念</span>
          <span class="stat-period">今日</span>
        </div>
        <div class="card-body">
          <div class="concept-list">
            <div class="concept-item" v-for="concept in hotConcepts" :key="concept.name">
              <div class="concept-header">
                <span class="concept-name">{{ concept.name }}</span>
                <span class="concept-tag">{{ concept.tag }}</span>
              </div>
              <div class="concept-body">
                <div class="concept-stocks">
                  <span class="concept-stock" v-for="stock in concept.stocks.slice(0, 5)" :key="stock.code">
                    {{ stock.name }}
                  </span>
                  <span class="concept-more" v-if="concept.stocks.length > 5">...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 市场趋势卡片 -->
    <div class="market-trend-card">
      <div class="card-header">
        <span class="stat-title">市场趋势</span>
        <div class="trend-tabs">
          <button class="trend-tab" :class="{ active: trendPeriod === 'day' }" @click="setTrendPeriod('day')">日</button>
          <button class="trend-tab" :class="{ active: trendPeriod === 'week' }" @click="setTrendPeriod('week')">周</button>
          <button class="trend-tab" :class="{ active: trendPeriod === 'month' }" @click="setTrendPeriod('month')">月</button>
        </div>
      </div>
      <div class="card-body">
        <div class="trend-chart">
          <canvas id="marketTrendChart" :height="300"></canvas>
        </div>
        <div class="trend-summary">
          <div class="trend-metric">
            <span class="metric-label">上证指数</span>
            <span class="metric-value" :class="getTrendValueClass(marketTrend.shIndex)">
              {{ formatValue(marketTrend.shIndex) }}
            </span>
            <span class="metric-change" :class="getChangeClass(marketTrend.shIndexChange)">
              {{ formatChange(marketTrend.shIndexChange) }}
            </span>
          </div>
          <div class="trend-metric">
            <span class="metric-label">深证成指</span>
            <span class="metric-value" :class="getTrendValueClass(marketTrend.szIndex)">
              {{ formatValue(marketTrend.szIndex) }}
            </span>
            <span class="metric-change" :class="getChangeClass(marketTrend.szIndexChange)">
              {{ formatChange(marketTrend.szIndexChange) }}
            </span>
          </div>
          <div class="trend-metric">
            <span class="metric-label">创业板指</span>
            <span class="metric-value" :class="getTrendValueClass(marketTrend.cyIndex)">
              {{ formatValue(marketTrend.cyIndex) }}
            </span>
            <span class="metric-change" :class="getChangeClass(marketTrend.cyIndexChange)">
              {{ formatChange(marketTrend.cyIndexChange) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="market-overview-footer">
      <div class="quick-actions">
        <div class="quick-action-item" @click="gotoStockList">
          <span class="action-icon">📋</span>
          <span class="action-label">股票列表</span>
        </div>
        <div class="quick-action-item" @click="gotoWatchlist">
          <span class="action-icon">⭐</span>
          <span class="action-label">自选股</span>
        </div>
        <div class="quick-action-item" @click="gotoFundFlow">
          <span class="action-icon">💰</span>
          <span class="action-label">资金流向</span>
        </div>
        <div class="quick-action-item" @click="gotoRiskAnalysis">
          <span class="action-icon">📊</span>
          <span class="action-label">风险分析</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { useRouter } from 'vue-router'
import type { MarketIndex, MarketSector, HotConcept, MarketTrend } from '@/types/market'
import { getMarketIndices, getMarketTrend, getMarketStats } from '@/api/market'
import { formatValue, formatVolume, formatChange, formatMoney } from '@/utils/format'

const router = useRouter()
const marketStore = useMarketStore()

const marketIndices = ref<MarketIndex[]>([])
const marketTrend = ref<MarketTrend | null>(null)
const marketStats = ref({
  totalTurnover: 0,
  totalVolume: 0,
  stockUpCount: 0,
  stockDownCount: 0,
  limitUpCount: 0,
  limitDownCount: 0
})

const topSectors = ref<MarketSector[]>([])
const hotConcepts = ref<HotConcept[]>([])
const trendPeriod = ref<'day' | 'week' | 'month'>('day')

const loadMarketIndices = async () => {
  try {
    const response = await getMarketIndices()
    
    if (response.code === 200 && response.data) {
      marketIndices.value = response.data.data
      
      // 渲染图表
      marketStore.setMarketIndices(response.data.data)
      
      await initIndexCharts(response.data.data)
    } else {
      console.error('Failed to load market indices:', response.message)
    }
  } catch (error) {
    console.error('Error loading market indices:', error)
    throw error
  }
}

const initIndexCharts = async (indices: MarketIndex[]) => {
  try {
    // 初始化所有指数图表
    for (const index of indices) {
      const canvas = document.getElementById(`chart-${index.code}`)
      
      if (canvas) {
        await renderIndexChart(canvas, index.code)
      }
    }
  } catch (error) {
    console.error('Error initializing index charts:', error)
  }
}

const renderIndexChart = async (canvas: HTMLCanvasElement, indexCode: string) => {
  try {
    const response = await getMarketTrend(indexCode, trendPeriod.value)
    
    if (response.code === 200 && response.data) {
      const trendData = response.data.data
      
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // 绘制趋势线
      drawTrendLine(ctx, trendData.data, indexCode)
    } else {
      console.error('Failed to load market trend:', response.message)
    }
  } catch (error) {
    console.error('Error rendering index chart:', error)
  }
}

const drawTrendLine = (ctx: CanvasRenderingContext2D, data: any[], indexCode: string) => {
  const width = ctx.canvas.width
  const height = ctx.canvas.height
  
  const padding = 20
  const chartWidth = width - padding * 2
  const chartHeight = height - padding * 2
  
  ctx.strokeStyle = '#1a1a1a1a'
  ctx.lineWidth = 2
  ctx.beginPath()
  
  const values = data.map(d => d.value || d.close || 0)
  const max = Math.max(...values)
  const min = Math.min(...values)
  
  const stepX = chartWidth / (values.length - 1)
  const stepY = chartHeight / (max - min)
  
  ctx.moveTo(padding, padding + chartHeight - (values[0] - min) * stepY)
  
  for (let i = 1; i < values.length; i++) {
    const x = padding + i * stepX
    const y = padding + chartHeight - (values[i] - min) * stepY
    
    ctx.lineTo(x, y)
  }
  
  ctx.stroke()
  
  // 绘制填充区域
  ctx.fillStyle = 'rgba(26, 26, 26, 0.1)'
  ctx.fill()
  ctx.moveTo(padding, padding)
  ctx.lineTo(padding + chartWidth, padding)
  ctx.lineTo(padding + chartWidth, padding + chartHeight)
  ctx.lineTo(padding, padding + chartHeight)
  ctx.fill()
  
  // 绘制文字
  ctx.fillStyle = '#333'
  ctx.font = '14px Arial'
  ctx.textAlign = 'center'
  ctx.fillText(indexCode, padding + chartWidth / 2, padding + chartHeight / 2)
}

const loadMarketTrend = async () => {
  try {
    const shIndex = '000001'
    const szIndex = '399001'
    const cyIndex = '399006'
    
    const [shResponse, szResponse, cyResponse] = await Promise.all([
      getMarketTrend(shIndex, trendPeriod.value),
      getMarketTrend(szIndex, trendPeriod.value),
      getMarketTrend(cyIndex, trendPeriod.value)
    ])
    
    const shIndexData = shResponse.data.data
    const szIndexData = szResponse.data.data
    const cyIndexData = cyResponse.data.data
    
    marketTrend.value = {
      shIndex: {
        current: shIndexData.current || shIndexData.data?.[shIndexData.data.length - 1],
        change: shIndexData.change || 0,
        changePercent: shIndexData.changePercent || 0
      },
      szIndex: {
        current: szIndexData.current || szIndexData.data?.[szIndexData.data.length - 1],
        change: szIndexData.change || 0,
        changePercent: szIndexData.changePercent || 0
      },
      cyIndex: {
        current: cyIndexData.current || cyIndexData.data?.[cyIndexData.data.length - 1],
        change: cyIndexData.change || 0,
        changePercent: cyIndexData.changePercent || 0
      }
    }
    
    marketStore.setMarketTrend(marketTrend.value)
    
    // 渲染趋势图表
    const canvas = document.getElementById('marketTrendChart')
    
    if (canvas) {
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // 绘制三个指数的趋势
      drawTrendLine(ctx, shIndexData.data || [], '上证')
      drawTrendLine(ctx, szIndexData.data || [], '深证')
      drawTrendLine(ctx, cyIndexData.data || [], '创业板')
    }
  } catch (error) {
    console.error('Error loading market trend:', error)
    throw error
  }
}

const loadMarketStats = async () => {
  try {
    const response = await getMarketStats()
    
    if (response.code === 200 && response.data) {
      marketStats.value = response.data.data
      
      // 加载热门板块和概念
      await loadTopSectors()
      await loadHotConcepts()
    }
  } catch (error) {
    console.error('Error loading market stats:', error)
    throw error
  }
}

const loadTopSectors = async () => {
  try {
    const response = await getMarketStats()
    
    if (response.code === 200 && response.data) {
      topSectors.value = response.data.data.topSectors || []
    }
  } catch (error) {
    console.error('Error loading top sectors:', error)
    throw error
  }
}

const loadHotConcepts = async () => {
  try {
    const response = await getMarketStats()
    
    if (response.code === 200 && response.data) {
      hotConcepts.value = response.data.data.hotConcepts || []
    }
  } catch (error) {
    console.error('Error loading hot concepts:', error)
    throw error
  }
}

const refreshData = async () => {
  try {
    await Promise.all([
      loadMarketIndices(),
      loadMarketTrend(),
      loadMarketStats()
    ])
    
    console.log('Market data refreshed successfully')
  } catch (error) {
    console.error('Error refreshing market data:', error)
    throw error
  }
}

const exportReport = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      marketIndices: marketIndices.value,
      marketTrend: marketTrend.value,
      marketStats: marketStats.value,
      topSectors: topSectors.value,
      hotConcepts: hotConcepts.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `market_overview_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Market overview report exported')
  } catch (error) {
    console.error('Error exporting report:', error)
  }
}

const setTrendPeriod = (period: 'day' | 'week' | 'month') => {
  trendPeriod.value = period
  loadMarketTrend()
}

const gotoStockList = () => {
  router.push('/stocks')
}

const gotoWatchlist = () => {
  router.push('/watchlist')
}

const gotoFundFlow = () => {
  router.push('/fund-flow')
}

const gotoRiskAnalysis = () => {
  router.push('/risk-analysis')
}

const getIndexValueClass = (value: number) => {
  if (value > 0) {
    return 'value-positive'
  } else if (value < 0) {
    return 'value-negative'
  } else {
    return 'value-neutral'
  }
}

const getChangeClass = (change: number) => {
  if (change > 0) {
    return 'change-positive'
  } else if (change < 0) {
    return 'change-negative'
  } else {
    return 'change-neutral'
  }
}

const getTrendValueClass = (value: number) => {
  return getIndexValueClass(value)
}

const getSectorChangeClass = (change: number) => {
  return getChangeClass(change)
}

const formatValue = (value: number) => {
  return formatMoney(value)
}

const formatVolume = (volume: number) => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  } else {
    return volume.toLocaleString()
  }
}

const formatChange = (change: number) => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

const formatMoney = (value: number) => {
  if (value >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿'
  } else if (value >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  } else {
    return value.toFixed(2)
  }
}

onMounted(async () => {
  await Promise.all([
    loadMarketIndices(),
    loadMarketTrend(),
    loadMarketStats()
  ])
  
  console.log('MarketOverview component mounted')
})

onUnmounted(() => {
  console.log('MarketOverview component unmounted')
})
</script>

<style scoped lang="scss">
.market-overview-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.market-overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.market-overview-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.market-overview-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #1a1a1a1a;
  color: white;
}

.btn-primary:hover {
  background: #333;
}

.btn-secondary {
  background: transparent;
  color: #1a1a1a1a;
  border: 1px solid #1a1a1a1a;
}

.btn-secondary:hover {
  background: #f0f0f0;
}

.market-indices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.index-name,
.stat-title,
.sector-name,
.concept-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.index-code {
  font-size: 14px;
  color: #999;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.index-value {
  font-size: 24px;
  font-weight: bold;
  color: #1a1a1a1a;
}

.value-positive {
  color: #4caf50;
}

.value-negative {
  color: #f44336;
}

.value-neutral {
  color: #333;
}

.index-change {
  font-size: 16px;
  font-weight: 500;
  margin-left: auto;
}

.change-positive {
  color: #4caf50;
}

.change-negative {
  color: #f44336;
}

.change-neutral {
  color: #999;
}

.card-body {
  padding: 20px;
}

.index-chart {
  margin-bottom: 20px;
}

.index-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.index-detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 14px;
  color: #666;
}

.detail-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.market-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-period {
  font-size: 14px;
  color: #999;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #1a1a1a1a;
}

.market-trend-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.trend-tabs {
  display: flex;
  gap: 5px;
}

.trend-tab {
  padding: 8px 16px;
  border: 1px solid #f0f0f0;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  transition: all 0.3s;
}

.trend-tab:hover {
  background: #f5f7fa;
  color: #1a1a1a1a;
}

.trend-tab.active {
  background: #1a1a1a1a;
  color: white;
}

.trend-chart {
  margin-bottom: 20px;
}

.trend-summary {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.trend-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  color: #1a1a1a1a;
}

.metric-change {
  font-size: 14px;
  font-weight: 500;
  margin-left: 10px;
}

.quick-actions {
  display: flex;
  gap: 10px;
  padding: 20px;
  background: white;
  border-radius: 8px;
}

.quick-action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 15px 20px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-action-item:hover {
  background: #f5f7fa;
  transform: translateY(-2px);
}

.action-icon {
  font-size: 24px;
}

.action-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.sector-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sector-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.sector-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.sector-change {
  font-size: 14px;
  font-weight: 500;
  color: #999;
}

.sector-percentage {
  font-size: 12px;
  color: #999;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  min-width: 50px;
  text-align: center;
}

.concept-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.concept-item {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.concept-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.concept-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f5f7fa;
}

.concept-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.concept-tag {
  font-size: 12px;
  color: #1a1a1a1a;
  background: white;
  padding: 4px 8px;
  border-radius: 3px;
}

.concept-body {
  padding: 15px;
}

.concept-stocks {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 10px;
}

.concept-stock {
  font-size: 14px;
  color: #333;
  background: #f5f7fa;
  padding: 5px 10px;
  border-radius: 4px;
}

.concept-more {
  font-size: 14px;
  color: #999;
  font-weight: 500;
  align-self: center;
}

.market-overview-footer {
  display: flex;
  gap: 10px;
  padding: 20px;
  background: white;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .market-indices-grid,
  .market-stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-row {
    grid-template-columns: 1fr;
  }
  
  .trend-metric {
    flex-direction: column;
    gap: 5px;
  }
}
</style>
