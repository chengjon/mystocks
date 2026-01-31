<template>
  <div class="trading-overview-container">
    <!-- 交易概览主容器 -->
    <div class="trading-overview-header">
      <h2 class="trading-overview-title">交易概览</h2>
      <div class="trading-overview-actions">
        <button class="btn-primary" @click="refreshTrading">刷新交易</button>
        <button class="btn-secondary" @click="placeOrder">下单</button>
        <button class="btn-secondary" @click="exportTrading">导出记录</button>
      </div>
    </div>

    <!-- 交易统计卡片 -->
    <div class="trading-stats-grid">
      <div class="card stat-card">
        <div class="card-header">
          <span class="stat-title">交易统计</span>
          <span class="stat-period">今日</span>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">总交易笔数</span>
              <span class="stat-value">{{ totalTrades }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总交易金额</span>
              <span class="stat-value">{{ formatMoney(totalAmount) }}</span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">总盈亏</span>
              <span class="stat-value" :class="getPnLClass(totalPnL)">
                {{ formatMoney(totalPnL) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">胜率</span>
              <span class="stat-value" :class="getWinRateClass(winRate)">
                {{ winRate }}%
              </span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">平均交易额</span>
              <span class="stat-value">{{ formatMoney(avgTradeAmount) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">盈亏比例</span>
              <span class="stat-value" :class="getPnLClass(pnLPercent)">
                {{ formatPercent(pnLPercent) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="card-header">
          <span class="stat-title">持仓统计</span>
          <span class="stat-period">当前</span>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">总持仓</span>
              <span class="stat-value">{{ formatMoney(totalPositions) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">持仓数量</span>
              <span class="stat-value">{{ positionCount }}只</span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">持仓盈亏</span>
              <span class="stat-value" :class="getPnLClass(positionPnL)">
                {{ formatMoney(positionPnL) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">持仓比例</span>
              <span class="stat-value">{{ formatPercent(positionPercent) }}</span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">最大持仓</span>
              <span class="stat-value">{{ formatMoney(maxPosition) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">最小持仓</span>
              <span class="stat-value">{{ formatMoney(minPosition) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="card-header">
          <span class="stat-title">订单统计</span>
          <span class="stat-period">当前</span>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">待成交</span>
              <span class="stat-value">{{ pendingOrders }}单</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">部分成交</span>
              <span class="stat-value">{{ partialOrders }}单</span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">全部成交</span>
              <span class="stat-value">{{ filledOrders }}单</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">已取消</span>
              <span class="stat-value">{{ cancelledOrders }}单</span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">买入订单</span>
              <span class="stat-value">{{ buyOrders }}单</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">卖出订单</span>
              <span class="stat-value">{{ sellOrders }}单</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="card-header">
          <span class="stat-title">资金统计</span>
          <span class="stat-period">当前</span>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">可用资金</span>
              <span class="stat-value">{{ formatMoney(availableFunds) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">冻结资金</span>
              <span class="stat-value">{{ formatMoney(frozenFunds) }}</span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">总资金</span>
              <span class="stat-value">{{ formatMoney(totalFunds) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">资金比例</span>
              <span class="stat-value">{{ formatPercent(fundsPercent) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 最新交易 -->
    <div class="recent-trades-section">
      <div class="card trades-card">
        <div class="card-header">
          <h3>最新交易</h3>
          <div class="trades-actions">
            <select v-model="tradeTypeFilter" class="filter-select">
              <option value="all">全部类型</option>
              <option value="buy">买入</option>
              <option value="sell">卖出</option>
            </select>
            <button class="btn-secondary" @click="exportTrades">导出</button>
          </div>
        </div>
        <div class="card-body">
          <table class="trades-table">
            <thead>
              <tr>
                <th>股票</th>
                <th>类型</th>
                <th>价格</th>
                <th>数量</th>
                <th>金额</th>
                <th>时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="trade in recentTrades" :key="trade.id" class="trade-row">
                <td class="trade-stock">{{ trade.stockName }}</td>
                <td class="trade-type" :class="getTradeTypeClass(trade.type)">
                  {{ getTradeTypeName(trade.type) }}
                </td>
                <td class="trade-price">{{ formatPrice(trade.price) }}</td>
                <td class="trade-quantity">{{ trade.quantity }}</td>
                <td class="trade-amount">{{ formatMoney(trade.amount) }}</td>
                <td class="trade-time">{{ formatTime(trade.createdAt) }}</td>
              </tr>
            </tbody>
          </table>
          <div class="view-more">
            <button class="btn-secondary" @click="viewAllTrades">
              查看全部交易 ({{ totalTradesCount }}笔)
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 挂仓列表 -->
    <div class="positions-list-section">
      <div class="card positions-card">
        <div class="card-header">
          <h3>持仓列表</h3>
          <div class="positions-actions">
            <select v-model="positionsSort" class="sort-select">
              <option value="marketValue">按市值</option>
              <option value="pnl">按盈亏</option>
              <option value="quantity">按数量</option>
            </select>
            <button class="btn-secondary" @click="exportPositions">导出</button>
          </div>
        </div>
        <div class="card-body">
          <table class="positions-table">
            <thead>
              <tr>
                <th>股票</th>
                <th>数量</th>
                <th>成本价</th>
                <th>当前价</th>
                <th>市值</th>
                <th>盈亏</th>
                <th>盈亏比例</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="position in sortedPositions" :key="position.stockCode">
                <td class="position-stock">{{ position.stockName }}</td>
                <td class="position-quantity">{{ position.quantity }}</td>
                <td class="position-cost">{{ formatPrice(position.costPrice) }}</td>
                <td class="position-current" :class="getPriceClass(position.currentPrice - position.costPrice)">
                  {{ formatPrice(position.currentPrice) }}
                </td>
                <td class="position-value">{{ formatMoney(position.marketValue) }}</td>
                <td class="position-pnl" :class="getPnLClass(position.pnl)">
                  {{ formatMoney(position.pnl) }}
                </td>
                <td class="position-pnl-percent" :class="getPnLClass(position.pnlPercent)">
                  {{ formatPercent(position.pnlPercent) }}
                </td>
              </tr>
            </tbody>
          </table>
          <div class="view-more">
            <button class="btn-secondary" @click="viewAllPositions">
              查看全部持仓 ({{ positionCount }}只)
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 订单列表 -->
    <div class="orders-list-section">
      <div class="card orders-card">
        <div class="card-header">
          <h3>订单列表</h3>
          <div class="orders-actions">
            <select v-model="orderStatusFilter" class="filter-select">
              <option value="all">全部状态</option>
              <option value="pending">待成交</option>
              <option value="partial">部分成交</option>
              <option value="filled">全部成交</option>
              <option value="cancelled">已取消</option>
            </select>
            <button class="btn-secondary" @click="exportOrders">导出</button>
          </div>
        </div>
        <div class="card-body">
          <table class="orders-table">
            <thead>
              <tr>
                <th>股票</th>
                <th>类型</th>
                <th>价格</th>
                <th>数量</th>
                <th>已成交</th>
                <th>状态</th>
                <th>时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in filteredOrders" :key="order.id">
                <td class="order-stock">{{ order.stockName }}</td>
                <td class="order-type" :class="getTradeTypeClass(order.type)">
                  {{ getTradeTypeName(order.type) }}
                </td>
                <td class="order-price">{{ formatPrice(order.price) }}</td>
                <td class="order-quantity">{{ order.quantity }}</td>
                <td class="order-filled">{{ order.filledQuantity }}</td>
                <td class="order-status" :class="getStatusClass(order.status)">
                  {{ getStatusName(order.status) }}
                </td>
                <td class="order-time">{{ formatTime(order.createdAt) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions-section">
      <div class="card actions-card">
        <div class="card-header">
          <h3>快捷操作</h3>
        </div>
        <div class="card-body">
          <div class="actions-grid">
            <div class="action-item" @click="gotoPositions">
              <span class="action-icon">📋</span>
              <span class="action-label">持仓管理</span>
            </div>
            <div class="action-item" @click="gotoOrders">
              <span class="action-icon">📤</span>
              <span class="action-label">订单管理</span>
            </div>
            <div class="action-item" @click="gotoTrades">
              <span class="action-icon">📜</span>
              <span class="action-label">交易历史</span>
            </div>
            <div class="action-item" @click="gotoAnalysis">
              <span class="action-icon">📊</span>
              <span class="action-label">交易分析</span>
            </div>
            <div class="action-item" @click="gotoRisk">
              <span class="action-icon">⚠️</span>
              <span class="action-label">风险控制</span>
            </div>
            <div class="action-item" @click="gotoSettings">
              <span class="action-icon">⚙️</span>
              <span class="action-label">交易设置</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载交易概览...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTradingStore } from '@/stores/trading'
import { useRouter } from 'vue-router'
import type { Trade, Position, Order, TradingStats } from '@/types/trading'
import { getTradingOverview, getRecentTrades, getPositions, getOrders } from '@/api/trading'
import { formatMoney, formatPrice, formatPercent, formatTime } from '@/utils/format'

const router = useRouter()
const tradingStore = useTradingStore()

const totalTrades = ref<number>(0)
const totalAmount = ref<number>(0)
const totalPnL = ref<number>(0)
const winRate = ref<number>(0)
const avgTradeAmount = ref<number>(0)
const pnLPercent = ref<number>(0)

const totalPositions = ref<number>(0)
const positionCount = ref<number>(0)
const positionPnL = ref<number>(0)
const positionPercent = ref<number>(0)
const maxPosition = ref<number>(0)
const minPosition = ref<number>(0)

const pendingOrders = ref<number>(0)
const partialOrders = ref<number>(0)
const filledOrders = ref<number>(0)
const cancelledOrders = ref<number>(0)
const buyOrders = ref<number>(0)
const sellOrders = ref<number>(0)

const availableFunds = ref<number>(0)
const frozenFunds = ref<number>(0)
const totalFunds = ref<number>(0)
const fundsPercent = ref<number>(0)

const recentTrades = ref<Trade[]>([])
const allPositions = ref<Position[]>([])
const allOrders = ref<Order[]>([])

const tradeTypeFilter = ref<'all' | 'buy' | 'sell'>('all')
const positionsSort = ref<'marketValue' | 'pnl' | 'quantity'>('marketValue')
const orderStatusFilter = ref<'all' | 'pending' | 'partial' | 'filled' | 'cancelled'>('all')

const totalTradesCount = ref<number>(0)
const isLoading = ref<boolean>(false)

const sortedPositions = computed(() => {
  let sorted = allPositions.value
  
  if (positionsSort.value === 'marketValue') {
    sorted = [...sorted].sort((a, b) => b.marketValue - a.marketValue)
  } else if (positionsSort.value === 'pnl') {
    sorted = [...sorted].sort((a, b) => b.pnl - a.pnl)
  } else if (positionsSort.value === 'quantity') {
    sorted = [...sorted].sort((a, b) => b.quantity - a.quantity)
  }
  
  return sorted.slice(0, 10)
})

const filteredOrders = computed(() => {
  let filtered = allOrders.value
  
  if (orderStatusFilter.value !== 'all') {
    filtered = filtered.filter(order => order.status === orderStatusFilter.value)
  }
  
  return filtered
})

const refreshTrading = async () => {
  try {
    isLoading.value = true
    await Promise.all([
      loadTradingStats(),
      loadRecentTrades(),
      loadPositions(),
      loadOrders()
    ])
  } catch (error) {
    console.error('Error refreshing trading:', error)
  } finally {
    isLoading.value = false
  }
}

const loadTradingStats = async () => {
  try {
    const response = await getTradingOverview()
    
    if (response.code === 200 && response.data) {
      const stats = response.data.data
      
      totalTrades.value = stats.totalTrades
      totalAmount.value = stats.totalAmount
      totalPnL.value = stats.totalPnL
      winRate.value = stats.winRate
      avgTradeAmount.value = stats.avgTradeAmount
      pnLPercent.value = stats.pnlPercent
      
      totalPositions.value = stats.totalPositions
      positionCount.value = stats.positionCount
      positionPnL.value = stats.positionPnL
      positionPercent.value = stats.positionPercent
      maxPosition.value = stats.maxPosition
      minPosition.value = stats.minPosition
      
      pendingOrders.value = stats.pendingOrders
      partialOrders.value = stats.partialOrders
      filledOrders.value = stats.filledOrders
      cancelledOrders.value = stats.cancelledOrders
      buyOrders.value = stats.buyOrders
      sellOrders.value = stats.sellOrders
      
      availableFunds.value = stats.availableFunds
      frozenFunds.value = stats.frozenFunds
      totalFunds.value = stats.totalFunds
      fundsPercent.value = stats.fundsPercent
      
      totalTradesCount.value = stats.totalTradesCount
    } else {
      console.error('Failed to load trading stats:', response.message)
    }
  } catch (error) {
    console.error('Error loading trading stats:', error)
    throw error
  }
}

const loadRecentTrades = async () => {
  try {
    const response = await getRecentTrades()
    
    if (response.code === 200 && response.data) {
      recentTrades.value = response.data.data
    } else {
      console.error('Failed to load recent trades:', response.message)
    }
  } catch (error) {
    console.error('Error loading recent trades:', error)
    throw error
  }
}

const loadPositions = async () => {
  try {
    const response = await getPositions()
    
    if (response.code === 200 && response.data) {
      allPositions.value = response.data.data
    } else {
      console.error('Failed to load positions:', response.message)
    }
  } catch (error) {
    console.error('Error loading positions:', error)
    throw error
  }
}

const loadOrders = async () => {
  try {
    const response = await getOrders()
    
    if (response.code === 200 && response.data) {
      allOrders.value = response.data.data
    } else {
      console.error('Failed to load orders:', response.message)
    }
  } catch (error) {
    console.error('Error loading orders:', error)
    throw error
  }
}

const placeOrder = () => {
  router.push('/orders/place')
}

const exportTrading = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      stats: {
        totalTrades: totalTrades.value,
        totalAmount: totalAmount.value,
        totalPnL: totalPnL.value,
        winRate: winRate.value,
        avgTradeAmount: avgTradeAmount.value,
        pnLPercent: pnLPercent.value
      },
      recentTrades: recentTrades.value,
      allPositions: allPositions.value,
      allOrders: allOrders.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `trading_overview_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Trading overview exported')
  } catch (error) {
    console.error('Error exporting trading:', error)
  }
}

const exportTrades = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      filter: {
        tradeType: tradeTypeFilter.value
      },
      data: recentTrades.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `recent_trades_${tradeTypeFilter.value}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Recent trades exported')
  } catch (error) {
    console.error('Error exporting trades:', error)
  }
}

const viewAllTrades = () => {
  router.push('/trades')
}

const exportPositions = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      sort: {
        positionsSort: positionsSort.value
      },
      data: sortedPositions.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `positions_${positionsSort.value}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Positions exported')
  } catch (error) {
    console.error('Error exporting positions:', error)
  }
}

const viewAllPositions = () => {
  router.push('/positions')
}

const exportOrders = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      filter: {
        status: orderStatusFilter.value
      },
      data: filteredOrders.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `orders_${orderStatusFilter.value}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Orders exported')
  } catch (error) {
    console.error('Error exporting orders:', error)
  }
}

const gotoPositions = () => {
  router.push('/positions')
}

const gotoOrders = () => {
  router.push('/orders')
}

const gotoTrades = () => {
  router.push('/trades')
}

const gotoAnalysis = () => {
  router.push('/analysis')
}

const gotoRisk = () => {
  router.push('/risk')
}

const gotoSettings = () => {
  router.push('/settings')
}

const getPnLClass = (pnl: number) => {
  if (pnl > 0) return 'pnl-positive'
  if (pnl < 0) return 'pnl-negative'
  return 'pnl-neutral'
}

const getWinRateClass = (winRate: number) => {
  if (winRate >= 60) return 'winrate-good'
  if (winRate >= 40) return 'winrate-fair'
  return 'winrate-poor'
}

const getTradeTypeClass = (type: string) => {
  if (type === 'buy') return 'type-buy'
  if (type === 'sell') return 'type-sell'
  return 'type-unknown'
}

const getTradeTypeName = (type: string) => {
  const names = {
    buy: '买入',
    sell: '卖出',
    unknown: '未知'
  }
  return names[type] || '未知'
}

const getPriceClass = (price: number) => {
  if (price > 0) return 'price-up'
  if (price < 0) return 'price-down'
  return 'price-neutral'
}

const getStatusClass = (status: string) => {
  if (status === 'filled') return 'status-filled'
  if (status === 'cancelled') return 'status-cancelled'
  if (status === 'pending') return 'status-pending'
  if (status === 'partial') return 'status-partial'
  return 'status-unknown'
}

const getStatusName = (status: string) => {
  const names = {
    filled: '已成交',
    cancelled: '已取消',
    pending: '待成交',
    partial: '部分成交',
    unknown: '未知'
  }
  return names[status] || '未知'
}

const formatMoney = (value: number) => {
  if (value >= 100000000) return (value / 100000000).toFixed(2) + '亿'
  if (value >= 10000) return (value / 10000).toFixed(2) + '万'
  return value.toFixed(2)
}

const formatPrice = (price: number) => {
  if (price >= 1000) return (price / 1000).toFixed(2)
  return price.toFixed(2)
}

const formatPercent = (percent: number) => {
  return percent.toFixed(2) + '%'
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

onMounted(async () => {
  await refreshTrading()
  console.log('TradingOverview component mounted')
})
</script>

<style scoped lang="scss">
.trading-overview-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.trading-overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.trading-overview-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.trading-overview-actions {
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
  background: #dc2626;
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

.trading-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.stat-period {
  font-size: 14px;
  color: #999;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.card-body {
  padding: 20px;
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
  color: #999;
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.stat-value.pnl-positive {
  color: #ef4444;
}

.stat-value.pnl-negative {
  color: #22c55e;
}

.stat-value.winrate-good {
  color: #4caf50;
}

.stat-value.winrate-fair {
  color: #ffc107;
}

.stat-value.winrate-poor {
  color: #f44336;
}

.recent-trades-section {
  margin-bottom: 20px;
}

.trades-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.trades-card .card-header {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.trades-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.trades-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-select,
.sort-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.1);
  color: white;
  cursor: pointer;
}

.trades-card .card-header .btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: white;
}

.trades-card .card-header .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.trades-table {
  width: 100%;
  border-collapse: collapse;
}

.trades-table th,
.trades-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.trades-table th {
  background: #f9f9f9;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.trades-table tbody tr:hover {
  background: #f5f7fa;
}

.trade-row {
  cursor: pointer;
}

.trade-stock {
  font-weight: bold;
  color: #333;
}

.trade-type {
  font-weight: 500;
}

.trade-type.type-buy {
  color: #ef4444;
}

.trade-type.type-sell {
  color: #22c55e;
}

.trade-price {
  font-weight: 500;
  color: #333;
}

.trade-quantity {
  color: #666;
}

.trade-amount {
  font-weight: 500;
  color: #333;
}

.trade-time {
  font-size: 14px;
  color: #999;
}

.view-more {
  padding: 20px;
  text-align: center;
}

.view-more .btn-secondary {
  background: white;
  color: #ef4444;
  border: 1px solid #ef4444;
}

.view-more .btn-secondary:hover {
  background: #f0f0f0;
  border-color: #ef4444;
}

.positions-list-section {
  margin-bottom: 20px;
}

.positions-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.positions-card .card-header {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.positions-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.positions-card .card-header .btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: white;
}

.positions-card .card-header .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.positions-table {
  width: 100%;
  border-collapse: collapse;
}

.positions-table th {
  background: #f9f9f9;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.positions-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.positions-table tbody tr:hover {
  background: #f5f7fa;
}

.position-stock {
  font-weight: bold;
  color: #333;
}

.position-quantity,
.position-cost,
.position-current,
.position-value,
.position-pnl,
.position-pnl-percent {
  font-size: 14px;
  color: #666;
}

.position-current.price-up {
  color: #ef4444;
  font-weight: bold;
}

.position-current.price-down {
  color: #22c55e;
  font-weight: bold;
}

.position-pnl.pnl-positive {
  color: #ef4444;
  font-weight: bold;
}

.position-pnl.pnl-negative {
  color: #22c55e;
  font-weight: bold;
}

.position-pnl-percent.pnl-positive {
  color: #ef4444;
}

.position-pnl-percent.pnl-negative {
  color: #22c55e;
}

.orders-list-section {
  margin-bottom: 20px;
}

.orders-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.orders-card .card-header {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.orders-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.orders-card .card-header .btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: white;
}

.orders-card .card-header .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
}

.orders-table th {
  background: #f9f9f9;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.orders-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.orders-table tbody tr:hover {
  background: #f5f7fa;
}

.order-stock {
  font-weight: bold;
  color: #333;
}

.order-type.type-buy {
  color: #ef4444;
}

.order-type.type-sell {
  color: #22c55e;
}

.order-price,
.order-quantity,
.order-filled,
.order-status,
.order-time {
  font-size: 14px;
  color: #666;
}

.order-status.status-filled {
  color: #4caf50;
  font-weight: bold;
}

.order-status.status-cancelled {
  color: #f44336;
  font-weight: bold;
}

.order-status.status-pending {
  color: #ffc107;
  font-weight: bold;
}

.order-status.status-partial {
  color: #ff9800;
  font-weight: bold;
}

.quick-actions-section {
  margin-bottom: 20px;
}

.actions-card {
  background: white;
  border-radius: 8px;
}

.actions-card .card-header {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.actions-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.action-item {
  padding: 20px;
  background: #f5f7fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.action-item:hover {
  background: #e0e0e0;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.action-label {
  font-size: 16px;
  font-weight: bold;
  color: #333;
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
  .trading-stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
