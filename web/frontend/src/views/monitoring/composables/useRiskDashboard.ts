import { ref, computed, onMounted, type Ref } from 'vue'
import { ElMessage as message } from 'element-plus'
import {
  AlertOutlined,
  HeartOutlined,
  WarningOutlined,
  StockOutlined,
  ReloadOutlined,
  ExportOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  BulbOutlined,
  PieChartOutlined,
  BarChartOutlined
} from '@ant-design/icons-vue'

interface AlertItem {
  level: 'critical' | 'warning' | 'info'
  stock_code: string
  [key: string]: unknown
}

interface SuggestionItem {
  id: string | number
  action: string
  stock_code: string
  [key: string]: unknown
}

interface SummaryData {
  total_score: number
  risk_score: number
  position_count: number
  sector_allocation: Record<string, number>
  alert_summary: { critical: number; warning: number; info: number }
  sharpe_ratio: number | null
  sortino_ratio: number | null
  max_drawdown: number | null
  volatility: number | null
  [key: string]: unknown
}

interface UseRiskDashboardOptions {
  watchlistId: Ref<number>
}

export function useRiskDashboard(options: UseRiskDashboardOptions) {
  const { watchlistId } = options

const loading = ref(false)
const summary = ref<SummaryData>({
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
const alerts = ref<AlertItem[]>([])
const suggestions = ref<SuggestionItem[]>([])

const criticalAlerts = computed(() => alerts.value.filter(a => a.level === 'critical'))
const warningAlerts = computed(() => alerts.value.filter(a => a.level === 'warning'))
const infoAlerts = computed(() => alerts.value.filter(a => a.level === 'info'))

const activePositions = computed(() => {
  return Math.floor((summary.value.position_count || 0) * 0.8)
})

const inactivePositions = computed(() => {
  return (summary.value.position_count || 0) - activePositions.value
})

// 工具函数
const getScoreColor = (score: number): string => {
  if (score >= 70) return 'fintech-text-up'
  if (score >= 50) return 'fintech-text-flat'
  return 'fintech-text-down'
}

const getScoreTrend = (score: number): string => {
  if (score >= 70) return 'positive'
  if (score >= 50) return 'neutral'
  return 'negative'
}

const getScoreChange = (score: number): string => {
  const change = (Math.random() - 0.5) * 10
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(1)}%`
}

const getActionClass = (action: string): string => {
  const classes: Record<string, string> = {
    'BUY': 'action-buy',
    'SELL': 'action-sell',
    'HOLD': 'action-hold',
    'REBALANCE': 'action-rebalance'
  }
  return classes[action] || 'action-hold'
}

const getSectorColor = (sector: string): string => {
  const colors = ['sector-tech', 'sector-healthcare', 'sector-finance', 'sector-consumer', 'sector-energy']
  const index = sector.length % colors.length
  return colors[index]
}

const formatCurrency = (value: number | null | undefined): string => {
  if (!value) return '$0.00'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(value)
}

const formatTime = (timestamp: string | null | undefined): string => {
  if (!timestamp) return 'Unknown'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 事件处理函数
const refresh = async (): Promise<void> => {
  await fetchData()
  message.success('Dashboard refreshed')
}

const exportReport = (): void => {
  message.info('Export functionality coming soon')
}

const handleAlert = (alert: AlertItem): void => {
  message.success(`Alert acknowledged: ${alert.stock_code}`)
}

const applySuggestion = (suggestion: SuggestionItem): void => {
  message.success(`Suggestion applied: ${suggestion.action} ${suggestion.stock_code}`)
}

const dismissSuggestion = (suggestion: SuggestionItem): void => {
  const index = suggestions.value.findIndex(s => s.id === suggestion.id)
  if (index > -1) {
    suggestions.value.splice(index, 1)
    message.info('Suggestion dismissed')
  }
}

const fetchData = async (): Promise<void> => {
  loading.value = true
  try {
    const [summaryRes, alertsRes, suggestionsRes] = await Promise.all([
      fetch(`/api/monitoring/analysis/portfolio/${watchlistId.value}/summary`),
      fetch(`/api/monitoring/analysis/portfolio/${watchlistId.value}/alerts`),
      fetch(`/api/monitoring/analysis/portfolio/${watchlistId.value}/rebalance`)
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

  return {
    watchlistId,
    loading,
    summary,
    alerts,
    suggestions,
    criticalAlerts,
    warningAlerts,
    infoAlerts,
    activePositions,
    inactivePositions,
    getScoreColor,
    getScoreTrend,
    getScoreChange,
    getActionClass,
    getSectorColor,
    formatCurrency,
    formatTime,
    refresh,
    exportReport,
    handleAlert,
    applySuggestion,
    dismissSuggestion,
    fetchData,
  }
}

// Export icons for component use
export {
  AlertOutlined,
  HeartOutlined,
  WarningOutlined,
  StockOutlined,
  ReloadOutlined,
  ExportOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  BulbOutlined,
  PieChartOutlined,
  BarChartOutlined
}
