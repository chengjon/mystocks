<template>
  <div class="realtime-position-panel">
    <div class="panel-header">
      <h3>
        <el-icon><TrendCharts /></el-icon>
        实时持仓市值
      </h3>
      <div class="header-actions">
        <el-tag :type="connectionStatus === 'connected' ? 'success' : 'danger'" size="small">
          {{ connectionStatus === 'connected' ? '已连接' : '断开' }}
        </el-tag>
        <el-button size="small" @click="toggleAutoRefresh" :type="autoRefresh ? 'primary' : 'default'">
          {{ autoRefresh ? '自动刷新中' : '暂停刷新' }}
        </el-button>
      </div>
    </div>

    <div class="portfolio-summary" v-if="portfolioSnapshot">
      <div class="summary-item total-value">
        <span class="label">总市值</span>
        <span class="value" :class="getValueClass(portfolioSnapshot.total_market_value)">
          {{ formatCurrency(portfolioSnapshot.total_market_value) }}
        </span>
      </div>
      <div class="summary-item profit">
        <span class="label">总盈亏</span>
        <span class="value" :class="getProfitClass(portfolioSnapshot.total_profit)">
          {{ formatCurrency(portfolioSnapshot.total_profit) }}
          <small>({{ formatPercent(portfolioSnapshot.profit_ratio) }})</small>
        </span>
      </div>
      <div class="summary-item positions">
        <span class="label">持仓数</span>
        <span class="value">{{ portfolioSnapshot.position_count }}</span>
      </div>
      <div class="summary-item update-time">
        <span class="label">更新时间</span>
        <span class="value">{{ formatTime(portfolioSnapshot.last_update) }}</span>
      </div>
    </div>

    <el-table
      :data="positionList"
      class="realtime-position-table"
      :row-class-name="tableRowClassName"
      v-loading="loading"
    >
      <el-table-column prop="symbol" label="股票" width="100">
        <template #default="{ row }">
          <div class="symbol-cell">
            <span class="code">{{ row.symbol }}</span>
            <span class="name">{{ row.name || getStockName(row.symbol) }}</span>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="quantity" label="数量" width="100" align="right">
        <template #default="{ row }">
          {{ row.quantity.toLocaleString() }}
        </template>
      </el-table-column>

      <el-table-column label="成本价" width="100" align="right">
        <template #default="{ row }">
          {{ formatPrice(row.avg_price) }}
        </template>
      </el-table-column>

      <el-table-column label="市价" width="100" align="right">
        <template #default="{ row }">
          <span :class="getPriceClass(row)">
            {{ formatPrice(row.market_price) }}
          </span>
        </template>
      </el-table-column>

      <el-table-column label="市值" width="120" align="right">
        <template #default="{ row }">
          {{ formatCurrency(row.market_value) }}
        </template>
      </el-table-column>

      <el-table-column label="浮动盈亏" width="130" align="right">
        <template #default="{ row }">
          <span :class="getProfitClass(row.unrealized_profit)">
            {{ formatCurrency(row.unrealized_profit) }}
          </span>
        </template>
      </el-table-column>

      <el-table-column label="收益率" width="100" align="right">
        <template #default="{ row }">
          <span :class="getProfitClass(row.profit_ratio)">
            {{ formatPercent(row.profit_ratio) }}
          </span>
        </template>
      </el-table-column>

      <el-table-column label="涨跌幅" width="100" align="right">
        <template #default="{ row }">
          <span :class="getPriceChangeClass(row.price_change_percent)">
            {{ row.price_change_percent >= 0 ? '+' : '' }}{{ formatPercent(row.price_change_percent) }}
          </span>
        </template>
      </el-table-column>
    </el-table>

    <div class="panel-footer">
      <el-button size="small" @click="refreshData" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
      <el-button size="small" @click="exportData">
        <el-icon><Download /></el-icon>
        导出
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts, Refresh, Download } from '@element-plus/icons-vue'
import { useRealtimeMarket } from '@/services/realtimeMarket'

interface PositionSnapshot {
  position_id: string
  symbol: string
  quantity: number
  avg_price: number
  market_price: number
  market_value: number
  unrealized_profit: number
  profit_ratio: number
  price_change_percent: number
  name?: string
}

interface PortfolioSnapshot {
  portfolio_id: string
  total_market_value: number
  total_profit: number
  profit_ratio: number
  position_count: number
  last_update: string
  positions: Record<string, PositionSnapshot>
}

const props = defineProps<{
  portfolioId?: string
  autoConnect?: boolean
}>()

const emit = defineEmits(['update', 'error'])
const {
  connectionStatus,
  connectWebSocket: connectPortfolioWebSocket,
  disconnect: disconnectPortfolioWebSocket,
  getPortfolioMTM,
  on,
  off,
  requestSnapshot,
  subscribe,
  unsubscribe
} = useRealtimeMarket()

const loading = ref(false)
const autoRefresh = ref(true)
const portfolioSnapshot = ref<PortfolioSnapshot | null>(null)
const positionList = ref<PositionSnapshot[]>([])
const resolvedPortfolioId = computed(() => props.portfolioId || 'default')

let refreshInterval: number | null = null
const subscribedSymbols = new Set<string>()
let hasHandledConnectedHandshake = false
const stockNames: Record<string, string> = {
  '600519': '贵州茅台',
  '000001': '平安银行',
  '600036': '招商银行',
  '600000': '浦发银行',
}

const getTrackedSymbols = (items: PositionSnapshot[]) =>
  items
    .map((position) => String(position.symbol || '').trim())
    .filter((symbol) => symbol.length > 0)

const clearTrackedSubscriptions = () => {
  if (connectionStatus.value === 'connected') {
    subscribedSymbols.forEach((symbol) => {
      unsubscribe(symbol)
    })
  }
  subscribedSymbols.clear()
}

const syncTrackedSubscriptions = (items: PositionSnapshot[], options: { force?: boolean } = {}) => {
  if (connectionStatus.value !== 'connected') {
    return
  }

  const nextSymbols = new Set(getTrackedSymbols(items))

  if (options.force) {
    subscribedSymbols.clear()
    nextSymbols.forEach((symbol) => {
      subscribe(symbol)
      subscribedSymbols.add(symbol)
    })
    return
  }

  Array.from(subscribedSymbols).forEach((symbol) => {
    if (!nextSymbols.has(symbol)) {
      unsubscribe(symbol)
      subscribedSymbols.delete(symbol)
    }
  })

  nextSymbols.forEach((symbol) => {
    if (!subscribedSymbols.has(symbol)) {
      subscribe(symbol)
      subscribedSymbols.add(symbol)
    }
  })
}

const updateSnapshot = (snapshot: PortfolioSnapshot) => {
  portfolioSnapshot.value = snapshot
  positionList.value = Object.values(snapshot.positions || {})
  syncTrackedSubscriptions(positionList.value)
  emit('update', snapshot)
}

const getSnapshotFromPayload = (payload: unknown): PortfolioSnapshot | null => {
  const snapshot = (payload as { snapshot?: PortfolioSnapshot } | null)?.snapshot
  return snapshot ?? null
}

const handleRealtimePayload = (payload: unknown) => {
  const snapshot = getSnapshotFromPayload(payload)
  if (snapshot) {
    updateSnapshot(snapshot)
  }
}

const handleConnected = (payload?: unknown) => {
  const snapshot = getSnapshotFromPayload(payload)

  if (!hasHandledConnectedHandshake) {
    ElMessage.success('实时行情连接已建立')
    hasHandledConnectedHandshake = true

    if (snapshot) {
      updateSnapshot(snapshot)
      return
    }

    syncTrackedSubscriptions(positionList.value, { force: true })
    requestSnapshot()
    return
  }

  if (snapshot) {
    updateSnapshot(snapshot)
  }
}

const connectWebSocket = () => {
  hasHandledConnectedHandshake = false
  connectPortfolioWebSocket(resolvedPortfolioId.value)
}

const disconnectWebSocket = () => {
  hasHandledConnectedHandshake = false
  clearTrackedSubscriptions()
  disconnectPortfolioWebSocket()
}

const refreshData = async () => {
  loading.value = true
  try {
    const snapshot = await getPortfolioMTM(resolvedPortfolioId.value)
    if (snapshot) {
      updateSnapshot(snapshot as PortfolioSnapshot)
    } else {
      ElMessage.error('刷新数据失败')
    }
  } catch (error) {
    console.error('Failed to refresh data:', error)
    ElMessage.error('刷新数据失败')
  } finally {
    loading.value = false
  }
}

const startAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  refreshInterval = window.setInterval(() => {
    if (autoRefresh.value && connectionStatus.value !== 'connected') {
      refreshData()
    }
  }, 5000)
}

const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
}

const exportData = () => {
  if (!portfolioSnapshot.value) {
    ElMessage.warning('没有可导出的数据')
    return
  }

  const headers = ['股票', '数量', '成本价', '市价', '市值', '浮动盈亏', '收益率', '涨跌幅']
  const rows = positionList.value.map(p => [
    p.symbol,
    p.quantity,
    p.avg_price.toFixed(2),
    p.market_price.toFixed(2),
    p.market_value.toFixed(2),
    p.unrealized_profit.toFixed(2),
    p.profit_ratio.toFixed(2) + '%',
    (p.price_change_percent >= 0 ? '+' : '') + p.price_change_percent.toFixed(2) + '%'
  ])

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `portfolio_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()

  ElMessage.success('导出成功')
}

const formatCurrency = (value: number) => {
  if (Math.abs(value) >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toFixed(2)
}

const formatPrice = (value: number) => {
  return value.toFixed(2)
}

const formatPercent = (value: number) => {
  return (value >= 0 ? '+' : '') + value.toFixed(2) + '%'
}

const formatTime = (timeStr: string) => {
  if (!timeStr) return '--'
  const date = new Date(timeStr)
  return date.toLocaleTimeString('zh-CN', { hour12: false })
}

const getStockName = (symbol: string) => {
  return stockNames[symbol] || symbol
}

const getValueClass = (value: number) => {
  return value >= 0 ? 'positive' : 'negative'
}

const getProfitClass = (value: number | undefined) => {
  if (value === undefined || value === null) return ''
  return value > 0 ? 'profit-up' : value < 0 ? 'profit-down' : ''
}

const getPriceClass = (row: PositionSnapshot) => {
  if (row.price_change_percent > 0) return 'price-up'
  if (row.price_change_percent < 0) return 'price-down'
  return ''
}

const getPriceChangeClass = (value: number) => {
  if (value > 0) return 'change-up'
  if (value < 0) return 'change-down'
  return ''
}

const tableRowClassName = ({ row }: { row: PositionSnapshot }) => {
  if (row.unrealized_profit > 0) return 'profit-row'
  if (row.unrealized_profit < 0) return 'loss-row'
  return ''
}

watch(() => props.portfolioId, () => {
  disconnectWebSocket()
  if (props.autoConnect !== false) {
    connectWebSocket()
  }
  void refreshData()
})

watch(connectionStatus, (status) => {
  if (status === 'error') {
    emit('error', new Error('portfolio realtime connection error'))
  }
  if (status !== 'connected') {
    hasHandledConnectedHandshake = false
    subscribedSymbols.clear()
  }
})

onMounted(() => {
  on('connected', handleConnected)
  on('portfolio_update', handleRealtimePayload)
  on('snapshot', handleRealtimePayload)

  if (props.autoConnect !== false) {
    connectWebSocket()
    startAutoRefresh()
  }
  refreshData()
})

onUnmounted(() => {
  off('connected', handleConnected)
  off('portfolio_update', handleRealtimePayload)
  off('snapshot', handleRealtimePayload)
  disconnectWebSocket()
  stopAutoRefresh()
})

defineExpose({
  refreshData,
  connectWebSocket,
  disconnectWebSocket
})
</script>

<style scoped lang="scss">
@use "./styles/RealtimePositionPanel.scss" as *;
</style>
