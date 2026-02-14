import { ref, computed, onMounted } from 'vue'
import {
import { ElMessage as message } from 'element-plus'

export function useRiskDashboard() {
  AlertOutlined,
  HeartOutlined,
  WarningOutlined,
  StockOutlined,
  ReloadOutlined,
  ExportOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  BulbOutlined,
  // BalanceOutlined,  // Not available in @ant-design/icons-vue
  PieChartOutlined,
  BarChartOutlined
} from '@ant-design/icons-vue'

const props = defineProps({
  watchlistId: {
    type: Number,
    required: true
  }
})

const loading = ref(false)
const summary = ref({
  total_score: 0,
  risk_score: 50,
  position_count: 0,
  sector_allocation: {},
  alert_summary: { critical: 0, warning: 0, info: 0 },
  sharpe_ratio: null,
  sortino_ratio: null,
  max_drawdown: null,
  volatility: null
})
const alerts = ref([])
const suggestions = ref([])

const criticalAlerts = computed(() => alerts.value.filter(a => a.level === 'critical'))
const warningAlerts = computed(() => alerts.value.filter(a => a.level === 'warning'))
const infoAlerts = computed(() => alerts.value.filter(a => a.level === 'info'))

const activePositions = computed(() => {
  // 模拟数据：假设80%的持仓是活跃的
  return Math.floor((summary.value.position_count || 0) * 0.8)
})

const inactivePositions = computed(() => {
  return (summary.value.position_count || 0) - activePositions.value
})

// 工具函数
const _getScoreColor = (score) => {
  if (score >= 70) return 'fintech-text-up'
  if (score >= 50) return 'fintech-text-flat'
  return 'fintech-text-down'
}

const getScoreTrend = (score) => {
  if (score >= 70) return 'positive'
  if (score >= 50) return 'neutral'
  return 'negative'
}

const getScoreChange = (score) => {
  // 模拟趋势数据
  const change = (Math.random() - 0.5) * 10
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(1)}%`
}

const getActionClass = (action) => {
  const classes = {
    'BUY': 'action-buy',
    'SELL': 'action-sell',
    'HOLD': 'action-hold',
    'REBALANCE': 'action-rebalance'
  }
  return classes[action] || 'action-hold'
}

const getSectorColor = (sector) => {
  // 根据行业返回不同的颜色类
  const colors = ['sector-tech', 'sector-healthcare', 'sector-finance', 'sector-consumer', 'sector-energy']
  const index = sector.length % colors.length
  return colors[index]
}

const formatCurrency = (value) => {
  if (!value) return '$0.00'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(value)
}

const formatTime = (timestamp) => {
  if (!timestamp) return 'Unknown'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 事件处理函数
const refresh = async () => {
  await fetchData()
  message.success('Dashboard refreshed')
}

const exportReport = () => {
  // 模拟导出功能
  message.info('Export functionality coming soon')
}

const handleAlert = (alert) => {
  // 处理告警
  message.success(`Alert acknowledged: ${alert.stock_code}`)
}

const applySuggestion = (suggestion) => {
  // 应用建议
  message.success(`Suggestion applied: ${suggestion.action} ${suggestion.stock_code}`)
}

const dismissSuggestion = (suggestion) => {
  // 忽略建议
  const index = suggestions.value.findIndex(s => s.id === suggestion.id)
  if (index > -1) {
    suggestions.value.splice(index, 1)
    message.info('Suggestion dismissed')
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const [summaryRes, alertsRes, suggestionsRes] = await Promise.all([
      fetch(`/api/monitoring/analysis/portfolio/${props.watchlistId}/summary`),
      fetch(`/api/monitoring/analysis/portfolio/${props.watchlistId}/alerts`),
      fetch(`/api/monitoring/analysis/portfolio/${props.watchlistId}/rebalance`)
    ])

    if (summaryRes.ok) {
      const data = await summaryRes.json()
      if (data.success) {
        summary.value = { ...summary.value, ...data.data }
      }
    }

    if (alertsRes.ok) {
      const data = await alertsRes.json()
      if (data.success) {
        alerts.value = data.data
      }
    }

    if (suggestionsRes.ok) {
      const data = await suggestionsRes.json()
      if (data.success) {
        suggestions.value = data.data
      }
    }
  } catch (error) {
    console.error('获取数据失败:', error)
    message.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

defineExpose({
  refresh: fetchData
})

  return {
    props,
    loading,
    summary,
    alerts,
    suggestions,
    criticalAlerts,
    warningAlerts,
    infoAlerts,
    activePositions,
    inactivePositions,
    _getScoreColor,
    getScoreTrend,
    getScoreChange,
    change,
    sign,
    getActionClass,
    classes,
    getSectorColor,
    colors,
    index,
    formatCurrency,
    formatTime,
    date,
    refresh,
    exportReport,
    handleAlert,
    applySuggestion,
    dismissSuggestion,
    index,
    fetchData,
    data,
    data,
    data,
  }
}
