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
      style="width: 100%"
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

const loading = ref(false)
const connectionStatus = ref('disconnected')
const autoRefresh = ref(true)
const portfolioSnapshot = ref<PortfolioSnapshot | null>(null)
const positionList = ref<PositionSnapshot[]>([])
const ws = ref<WebSocket | null>(null)
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 5
const reconnectDelay = 3000

let refreshInterval: number | null = null
const stockNames: Record<string, string> = {
  '600519': '贵州茅台',
  '000001': '平安银行',
  '600036': '招商银行',
  '600000': '浦发银行',
}

const connectWebSocket = () => {
  if (ws.value?.readyState === WebSocket.OPEN) {
    return
  }

  const wsUrl = `ws://${window.location.host}/api/ws/portfolio?portfolio_id=${props.portfolioId || 'default'}`

  try {
    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      connectionStatus.value = 'connected'
      reconnectAttempts.value = 0
      ElMessage.success('实时行情连接已建立')
      subscribeToPositions()
    }

    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.value.onclose = () => {
      connectionStatus.value = 'disconnected'
      if (reconnectAttempts.value < maxReconnectAttempts) {
        setTimeout(() => {
          reconnectAttempts.value++
          connectWebSocket()
        }, reconnectDelay)
      }
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error)
      connectionStatus.value = 'error'
      emit('error', error)
    }
  } catch (error) {
    console.error('Failed to connect WebSocket:', error)
  }
}

const handleWebSocketMessage = (data: any) => {
  if (data.action === 'connected') {
    if (data.snapshot) {
      updateSnapshot(data.snapshot)
    }
  } else if (data.action === 'portfolio_update') {
    if (data.snapshot) {
      updateSnapshot(data.snapshot)
    }
  } else if (data.action === 'snapshot') {
    if (data.snapshot) {
      updateSnapshot(data.snapshot)
    }
  } else if (data.action === 'pong') {
    console.log('Pong received')
  }
}

const updateSnapshot = (snapshot: PortfolioSnapshot) => {
  portfolioSnapshot.value = snapshot
  positionList.value = Object.values(snapshot.positions || {})
  emit('update', snapshot)
}

const subscribeToPositions = () => {
  if (ws.value?.readyState === WebSocket.OPEN) {
    const symbols = positionList.value.map(p => p.symbol)
    ws.value.send(JSON.stringify({
      action: 'subscribe_all',
      symbols
    }))
  }
}

const disconnectWebSocket = () => {
  if (ws.value) {
    ws.value.close()
    ws.value = null
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    const response = await fetch(`/api/mtm/portfolio/${props.portfolioId || 'default'}`)
    const data = await response.json()
    if (data.success && data.data) {
      updateSnapshot(data.data)
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
  if (ws.value?.readyState === WebSocket.OPEN) {
    disconnectWebSocket()
    connectWebSocket()
  }
})

onMounted(() => {
  if (props.autoConnect !== false) {
    connectWebSocket()
    startAutoRefresh()
  }
  refreshData()
})

onUnmounted(() => {
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
.realtime-position-panel {
  background: #fff;
  border-radius: 8px;
  padding: 16px;

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #eee;

    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }

    .header-actions {
      display: flex;
      gap: 8px;
    }
  }

  .portfolio-summary {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 16px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 8px;

    .summary-item {
      text-align: center;

      .label {
        display: block;
        font-size: 12px;
        color: #909399;
        margin-bottom: 4px;
      }

      .value {
        font-size: 20px;
        font-weight: 600;

        small {
          font-size: 12px;
          font-weight: normal;
        }

        &.positive { color: #67c23a; }
        &.negative { color: #f56c6c; }
      }

      &.total-value .value {
        font-size: 24px;
      }

      &.profit .value {
        &.profit-up { color: #67c23a; }
        &.profit-down { color: #f56c6c; }
      }
    }
  }

  .symbol-cell {
    .code {
      display: block;
      font-weight: 600;
      color: #303133;
    }

    .name {
      font-size: 12px;
      color: #909399;
    }
  }

  .price-up { color: #f56c6c; }
  .price-down { color: #67c23a; }
  .change-up { color: #f56c6c; }
  .change-down { color: #67c23a; }

  .profit-up { color: #67c23a; }
  .profit-down { color: #f56c6c; }

  :deep(.profit-row) {
    background-color: rgba(103, 194, 58, 0.05);
  }

  :deep(.loss-row) {
    background-color: rgba(245, 108, 108, 0.05);
  }

  .panel-footer {
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
}
</style>
