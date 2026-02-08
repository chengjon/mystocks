<template>
  <div class="technical-signals-container">
    <!-- 技术信号主容器 -->
    <div class="signals-header">
      <h2 class="signals-title">技术信号</h2>
      <div class="signals-actions">
        <button class="btn-primary" @click="refreshSignals">刷新信号</button>
        <button class="btn-secondary" @click="addCustomSignal">自定义信号</button>
        <button class="btn-secondary" @click="exportSignals">导出信号</button>
      </div>
    </div>

    <!-- 信号筛选面板 -->
    <div class="signals-filter-section">
      <div class="filter-card">
        <div class="filter-header">
          <h3>信号筛选</h3>
          <button class="close-btn" @click="toggleFilter">×</button>
        </div>
        <div class="filter-body">
          <div class="filter-row">
            <div class="filter-item">
              <span class="filter-label">信号类型</span>
              <select v-model="filters.signalType" class="filter-select">
                <option value="all">全部</option>
                <option value="buy">买入信号</option>
                <option value="sell">卖出信号</option>
                <option value="hold">持有信号</option>
              </select>
            </div>
            <div class="filter-item">
              <span class="filter-label">时间周期</span>
              <select v-model="filters.timePeriod" class="filter-select">
                <option value="day">日</option>
                <option value="week">周</option>
                <option value="month">月</option>
              </select>
            </div>
          </div>
          <div class="filter-row">
            <div class="filter-item">
              <span class="filter-label">强度</span>
              <select v-model="filters.strength" class="filter-select">
                <option value="all">全部</option>
                <option value="strong">强</option>
                <option value="medium">中</option>
                <option value="weak">弱</option>
              </select>
            </div>
            <div class="filter-item">
              <span class="filter-label">指标</span>
              <select v-model="filters.indicator" class="filter-select">
                <option value="all">全部</option>
                <option value="MA">移动平均</option>
                <option value="EMA">指数平均</option>
                <option value="MACD">MACD</option>
                <option value="RSI">RSI</option>
                <option value="BOLLINGER">布林带</option>
                <option value="KDJ">KDJ</option>
              </select>
            </div>
          </div>
          <div class="filter-actions">
            <button class="btn-primary" @click="applyFilters">应用筛选</button>
            <button class="btn-secondary" @click="resetFilters">重置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 信号列表 -->
    <div class="signals-list">
      <div class="card signal-card" v-for="signal in signals" :key="signal.id">
        <div class="card-header" :class="getSignalTypeClass(signal.signalType)">
          <span class="signal-name">{{ signal.stockName }}</span>
          <span class="signal-code">{{ signal.stockCode }}</span>
          <span class="signal-type">{{ getSignalTypeName(signal.signalType) }}</span>
          <span class="signal-strength" :class="getStrengthClass(signal.strength)">
            {{ getStrengthName(signal.strength) }}
          </span>
        </div>
        <div class="card-body">
          <div class="signal-details">
            <div class="detail-row">
              <span class="detail-label">指标</span>
              <span class="detail-value">{{ signal.indicator }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">周期</span>
              <span class="detail-value">{{ signal.timePeriod }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">价格</span>
              <span class="detail-value" :class="getValueClass(signal.price)">
                {{ formatValue(signal.price) }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">触发时间</span>
              <span class="detail-value">{{ formatTime(signal.triggerTime) }}</span>
            </div>
          </div>
          <div class="signal-chart">
            <canvas :id="`signal-chart-${signal.id}`" :height="150"></canvas>
          </div>
          <div class="signal-actions">
            <div class="action-buttons">
              <button class="btn-action" @click="viewSignalDetail(signal)">
                <span class="action-icon">📊</span>
                <span class="action-label">查看详情</span>
              </button>
              <button class="btn-action" @click="addToWatchlist(signal)" :class="{ added: signal.inWatchlist }">
                <span class="action-icon">{{ signal.inWatchlist ? '⭐' : '☆' }}</span>
                <span class="action-label">{{ signal.inWatchlist ? '已添加' : '添加自选' }}</span>
              </button>
              <button class="btn-action" @click="createOrder(signal)">
                <span class="action-icon">💱</span>
                <span class="action-label">创建订单</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 信号统计 -->
    <div class="signals-stats-section">
      <div class="card stats-card">
        <div class="card-header">
          <h3>信号统计</h3>
          <div class="stats-actions">
            <select v-model="statsPeriod" class="period-select">
              <option value="day">日</option>
              <option value="week">周</option>
              <option value="month">月</option>
            </select>
            <button class="btn-secondary" @click="refreshStats">刷新</button>
          </div>
        </div>
        <div class="card-body">
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">总信号</span>
              <span class="stat-value">{{ stats.totalSignals }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">买入信号</span>
              <span class="stat-value buy">{{ stats.buySignals }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">卖出信号</span>
              <span class="stat-value sell">{{ stats.sellSignals }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">成功率</span>
              <span class="stat-value" :class="getSuccessRateClass(stats.successRate)">
                {{ stats.successRate }}%
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均盈亏</span>
              <span class="stat-value" :class="getProfitLossClass(stats.avgProfitLoss)">
                {{ stats.avgProfitLoss }}%
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">最大盈利</span>
              <span class="stat-value profit">{{ stats.maxProfit }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-value loss">{{ stats.maxLoss }}%</span>
              <span class="stat-label">最大亏损</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 信号详情模态框 -->
    <div class="modal" v-if="showSignalDetail" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>信号详情</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-section">
            <div class="detail-section-title">基本信息</div>
            <div class="detail-section-body">
              <div class="detail-row">
                <span class="detail-label">股票名称</span>
                <span class="detail-value">{{ selectedSignal.stockName }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">股票代码</span>
                <span class="detail-value">{{ selectedSignal.stockCode }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">信号类型</span>
                <span class="detail-value" :class="getSignalTypeClass(selectedSignal.signalType)">
                  {{ getSignalTypeName(selectedSignal.signalType) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">信号强度</span>
                <span class="detail-value" :class="getStrengthClass(selectedSignal.strength)">
                  {{ getStrengthName(selectedSignal.strength) }}
                </span>
              </div>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">指标详情</div>
            <div class="detail-section-body">
              <div class="detail-row">
                <span class="detail-label">使用指标</span>
                <span class="detail-value">{{ selectedSignal.indicator }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">周期</span>
                <span class="detail-value">{{ selectedSignal.timePeriod }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">参数1</span>
                <span class="detail-value">{{ selectedSignal.param1 }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">参数2</span>
                <span class="detail-value">{{ selectedSignal.param2 }}</span>
              </div>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">信号详情</div>
            <div class="detail-section-body">
              <div class="detail-row">
                <span class="detail-label">触发价格</span>
                <span class="detail-value" :class="getValueClass(selectedSignal.price)">
                  {{ formatValue(selectedSignal.price) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">触发时间</span>
                <span class="detail-value">{{ formatTime(selectedSignal.triggerTime) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">状态</span>
                <span class="detail-value" :class="getStatusClass(selectedSignal.status)">
                  {{ selectedSignal.status }}
                </span>
              </div>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">历史表现</div>
            <div class="detail-section-body">
              <div class="detail-row">
                <span class="detail-label">历史成功率</span>
                <span class="detail-value">{{ selectedSignal.historicalSuccessRate }}%</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">历史平均盈亏</span>
                <span class="detail-value">{{ selectedSignal.historicalAvgProfitLoss }}%</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">历史最大盈利</span>
                <span class="detail-value profit">{{ selectedSignal.historicalMaxProfit }}%</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">历史最大亏损</span>
                <span class="detail-value loss">{{ selectedSignal.historicalMaxLoss }}%</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="createOrderFromDetail">创建订单</button>
          <button class="btn-secondary" @click="closeModal">关闭</button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载技术信号...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { useRouter } from 'vue-router'
import type { TechnicalSignal, SignalStats, SignalFilters } from '@/types/market'
import { getTechnicalSignals, getSignalStats, addToWatchlist, createOrderFromSignal } from '@/api/market'
import { formatValue, formatTime, getSignalTypeName, getStrengthName } from '@/utils/format'

const router = useRouter()
const marketStore = useMarketStore()

const signals = ref<TechnicalSignal[]>([])
const selectedSignal = ref<TechnicalSignal>({})
const showSignalDetail = ref<boolean>(false)
const stats = ref<SignalStats>({
  totalSignals: 0,
  buySignals: 0,
  sellSignals: 0,
  successRate: 0,
  avgProfitLoss: 0,
  maxProfit: 0,
  maxLoss: 0
})
const statsPeriod = ref<'day' | 'week' | 'month'>('day')
const isLoading = ref<boolean>(false)

const filters = reactive<SignalFilters>({
  signalType: 'all',
  timePeriod: 'all',
  strength: 'all',
  indicator: 'all'
})

const refreshSignals = async () => {
  try {
    isLoading.value = true
    const response = await getTechnicalSignals(filters)
    
    if (response.code === 200 && response.data) {
      signals.value = response.data.data
      await renderAllSignalCharts(response.data.data)
      await refreshSignalStats()
    } else {
      console.error('Failed to load technical signals:', response.message)
    }
  } catch (error) {
    console.error('Error loading technical signals:', error)
  } finally {
    isLoading.value = false
  }
}

const renderAllSignalCharts = async (signals: TechnicalSignal[]) => {
  for (const signal of signals) {
    const canvas = document.getElementById(`signal-chart-${signal.id}`)
    if (canvas) {
      await renderSignalChart(canvas, signal)
    }
  }
}

const renderSignalChart = async (canvas: HTMLCanvasElement, signal: TechnicalSignal) => {
  try {
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 10
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    if (signal.chartData && signal.chartData.length > 0) {
      const values = signal.chartData
      const max = Math.max(...values)
      const min = Math.min(...values)
      const range = max - min
      
      if (range === 0) {
        return
      }
      
      const stepX = chartWidth / (values.length - 1)
      const stepY = chartHeight / range
      
      ctx.strokeStyle = signal.signalType === 'buy' ? '#ef4444' : '#22c55e'
      ctx.lineWidth = 2
      ctx.beginPath()
      
      for (let i = 0; i < values.length; i++) {
        const x = padding + i * stepX
        const normalizedValue = (values[i] - min) / range
        const y = padding + chartHeight / 2 - (normalizedValue - 0.5) * chartHeight / 2
        
        ctx.moveTo(x, y)
        ctx.lineTo(x, y)
      }
      
      ctx.stroke()
      
      ctx.fillStyle = signal.signalType === 'buy' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(34, 197, 94, 0.1)'
      ctx.fill()
      ctx.moveTo(padding, padding)
      ctx.lineTo(padding + chartWidth, padding)
      ctx.lineTo(padding + chartWidth, padding + chartHeight)
      ctx.lineTo(padding, padding + chartHeight)
      ctx.fill()
    }
  } catch (error) {
    console.error('Error rendering signal chart:', error)
  }
}

const refreshSignalStats = async () => {
  try {
    const response = await getSignalStats(statsPeriod.value)
    
    if (response.code === 200 && response.data) {
      stats.value = response.data.data
    } else {
      console.error('Failed to load signal stats:', response.message)
    }
  } catch (error) {
    console.error('Error loading signal stats:', error)
  }
}

const toggleFilter = () => {
  const filterPanel = document.querySelector('.signals-filter-section')
  if (filterPanel) {
    filterPanel.classList.toggle('hidden')
  }
}

const applyFilters = async () => {
  await refreshSignals()
}

const resetFilters = () => {
  filters.signalType = 'all'
  filters.timePeriod = 'all'
  filters.strength = 'all'
  filters.indicator = 'all'
  applyFilters()
  toggleFilter()
}

const viewSignalDetail = (signal: TechnicalSignal) => {
  selectedSignal.value = signal
  showSignalDetail.value = true
}

const closeModal = () => {
  showSignalDetail.value = false
}

const addCustomSignal = () => {
  router.push('/signals/custom')
}

const exportSignals = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      filters: {
        signalType: filters.signalType,
        timePeriod: filters.timePeriod,
        strength: filters.strength,
        indicator: filters.indicator
      },
      signals: signals.value,
      stats: stats.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `technical_signals_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Technical signals exported')
  } catch (error) {
    console.error('Error exporting signals:', error)
  }
}

const addToWatchlist = async (signal: TechnicalSignal) => {
  try {
    if (signal.inWatchlist) {
      return
    }
    
    const response = await addToWatchlist({
      stockCode: signal.stockCode,
      stockName: signal.stockName
    })
    
    if (response.code === 200) {
      signal.inWatchlist = true
      console.log('Signal added to watchlist')
    } else {
      console.error('Failed to add to watchlist:', response.message)
    }
  } catch (error) {
    console.error('Error adding to watchlist:', error)
  }
}

const createOrder = async (signal: TechnicalSignal) => {
  try {
    router.push('/orders/create', {
      state: {
        signalId: signal.id,
        stockCode: signal.stockCode,
        stockName: signal.stockName,
        signalType: signal.signalType
      }
    })
  } catch (error) {
    console.error('Error creating order:', error)
  }
}

const createOrderFromDetail = async () => {
  await createOrder(selectedSignal.value)
}

const getSignalTypeClass = (signalType: string) => {
  if (signalType === 'buy') return 'type-buy'
  if (signalType === 'sell') return 'type-sell'
  if (signalType === 'hold') return 'type-hold'
  return 'type-unknown'
}

const getStrengthClass = (strength: string) => {
  if (strength === 'strong') return 'strength-strong'
  if (strength === 'medium') return 'strength-medium'
  if (strength === 'weak') return 'strength-weak'
  return 'strength-unknown'
}

const getValueClass = (value: number) => {
  if (value > 0) return 'value-positive'
  if (value < 0) return 'value-negative'
  return 'value-neutral'
}

const getStatusClass = (status: string) => {
  if (status === 'active') return 'status-active'
  if (status === 'completed') return 'status-completed'
  if (status === 'cancelled') return 'status-cancelled'
  return 'status-unknown'
}

const getSuccessRateClass = (rate: number) => {
  if (rate >= 80) return 'rate-excellent'
  if (rate >= 60) return 'rate-good'
  if (rate >= 40) return 'rate-fair'
  return 'rate-poor'
}

const getProfitLossClass = (profitLoss: number) => {
  if (profitLoss >= 10) return 'profit-loss-excellent'
  if (profitLoss >= 0) return 'profit-loss-good'
  if (profitLoss >= -10) return 'profit-loss-fair'
  return 'profit-loss-poor'
}

const formatValue = (value: number) => {
  if (value >= 1000) return (value / 1000).toFixed(2)
  return value.toFixed(2)
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

onMounted(async () => {
  await refreshSignals()
  console.log('TechnicalSignals component mounted')
})
</script>

<style scoped lang="scss">
.technical-signals-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.signals-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.signals-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.signals-actions {
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
  background: #ef4444;
  color: white;
}

.btn-primary:hover {
  background: #dc3545;
}

.btn-secondary {
  background: transparent;
  color: #ef4444;
  border: 1px solid #ef4444;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #ef4444;
}

.signals-filter-section {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 400px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.filter-card {
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #ef4444 0%, #dc3545 100%);
  color: white;
}

.filter-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
}

.close-btn:hover {
  transform: scale(1.1);
}

.filter-body {
  padding: 20px;
  overflow-y: auto;
}

.filter-row {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.filter-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.filter-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #ef4444;
}

.filter-actions {
  display: flex;
  gap: 10px;
}

.signals-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.signal-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header.type-buy {
  background: linear-gradient(135deg, #ef4444 0%, #dc3545 100%);
}

.card-header.type-sell {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.card-header.type-hold {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
}

.card-header.type-unknown {
  background: linear-gradient(135deg, #e0e0e0 0%, #9e9e9e 100%);
}

.signal-name {
  font-size: 18px;
  font-weight: bold;
  color: white;
  flex: 1;
}

.signal-code {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: 10px;
}

.signal-type {
  font-size: 14px;
  color: white;
  font-weight: 500;
  margin-left: 10px;
}

.signal-strength {
  font-size: 14px;
  color: white;
  font-weight: 500;
  margin-left: 10px;
}

.signal-strength.strength-strong {
  color: rgba(255, 255, 255, 1);
}

.signal-strength.strength-medium {
  color: rgba(255, 255, 255, 0.9);
}

.signal-strength.strength-weak {
  color: rgba(255, 255, 255, 0.7);
}

.card-body {
  padding: 20px;
}

.signal-details {
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.detail-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
  flex: 1;
}

.detail-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.detail-value.value-positive {
  color: #ef4444;
}

.detail-value.value-negative {
  color: #22c55e;
}

.signal-chart {
  margin-bottom: 20px;
}

.signal-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.btn-action {
  padding: 10px 20px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-action:hover {
  border-color: #ef4444;
  transform: translateY(-2px);
}

.btn-action.added {
  background: #fff7e6;
  border-color: #ffc107;
}

.action-icon {
  font-size: 20px;
}

.action-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.signals-stats-section {
  margin-bottom: 20px;
}

.stats-card {
  background: white;
  border-radius: 8px;
}

.stats-card .card-header {
  background: linear-gradient(135deg, #ef4444 0%, #dc3545 100%);
  color: white;
}

.stats-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.stats-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.stats-card .card-header .btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: white;
}

.stats-card .card-header .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-item {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
  display: block;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.stat-value.buy {
  color: #ef4444;
}

.stat-value.sell {
  color: #22c55e;
}

.stat-value.rate-excellent {
  color: #4caf50;
}

.stat-value.rate-good {
  color: #81c784;
}

.stat-value.rate-fair {
  color: #ffc107;
}

.stat-value.rate-poor {
  color: #f44336;
}

.stat-value.profit {
  color: #4caf50;
}

.stat-value.loss {
  color: #f44336;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 600px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #ef4444 0%, #dc3545 100%);
  color: white;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.modal-header .close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
}

.modal-header .close-btn:hover {
  transform: scale(1.1);
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ef4444;
}

.detail-section-body {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.detail-section-body .detail-row {
  margin-bottom: 10px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  background: #f5f7fa;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #ef4444;
  border-top-color: transparent;
  border-right-color: #ef4444;
  border-bottom-color: #ef4444;
  border-left-color: #ef4444;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: white;
  font-size: 16px;
  font-weight: 500;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .signals-list {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
