import { ref, reactive, onMounted, type Ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, List, TrendCharts, Bell, DataLine, Tickets,
  Delete, InfoFilled, Warning, CircleCheck, CircleClose
} from '@element-plus/icons-vue'
import HealthRadarChart from '@/components/chart/HealthRadarChart.vue'

// Type definitions
interface Watchlist {
  id: number
  name: string
  watchlist_type: string
  total_score?: number
  stocks_count?: number
}

interface WatchlistStock {
  id: number
  stock_code: string
  entry_price: number
  entry_reason?: string
  stop_loss_price?: number
  target_price?: number
  weight: number
}

interface PortfolioSummary {
  total_score?: number
  position_count?: number
  [key: string]: unknown
}

interface RadarScores {
  trend: number
  technical: number
  momentum: number
  volatility: number
  risk: number
}

interface AlertItem {
  id: number
  type: string
  level: string
  message: string
  priority?: string
}

interface AlertSummary {
  critical: number
  warning: number
  info: number
}

interface StockForm {
  stock_code: string
  entry_price: number | null
  entry_reason: string | null
  stop_loss_price: number | null
  target_price: number | null
  weight: number
}

export function usePortfolioManagement() {

// State
const loading: Ref<boolean> = ref(false)
const activeTab: Ref<string> = ref('watchlists')

// Data
const watchlists: Ref<Watchlist[]> = ref([])
const selectedWatchlist: Ref<Watchlist | null> = ref(null)
const watchlistStocks: Ref<WatchlistStock[]> = ref([])
const portfolioSummary: Ref<PortfolioSummary> = ref({})
const radarScores: Ref<RadarScores> = ref({ trend: 50, technical: 50, momentum: 50, volatility: 50, risk: 50 })
const allAlerts: Ref<AlertItem[]> = ref([])
const alertSummary: Ref<AlertSummary> = ref({ critical: 0, warning: 0, info: 0 })
const rebalanceSuggestions: Ref<unknown[]> = ref([])

// Dialogs
const createDialogVisible: Ref<boolean> = ref(false)
const addStockDialogVisible: Ref<boolean> = ref(false)
const healthDetailVisible: Ref<boolean> = ref(false)
const editingWatchlist: Ref<Watchlist | null> = ref(null)
const currentStock: Ref<WatchlistStock | null> = ref(null)
const currentStockHealth: Ref<unknown> = ref(null)

// Forms
const watchlistForm = reactive({
  name: '',
  watchlist_type: 'manual'
})

const stockForm: StockForm = reactive({
  stock_code: '',
  entry_price: null,
  entry_reason: null,
  stop_loss_price: null,
  target_price: null,
  weight: 0.1
})

const riskTolerance = ref(50)

// API Base
const API_BASE = '/api/v1/monitoring'

// Load Functions
const loadWatchlists = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/watchlists?user_id=1`)
    const data = await res.json()
    if (data.success) {
      watchlists.value = data.data
      // Calculate portfolio summary
      if (data.data && data.data.length > 0) {
        const avgScore = data.data.reduce((sum: number, w: Watchlist) => sum + (w.total_score || 0), 0) / data.data.length
        portfolioSummary.value.total_score = avgScore
        portfolioSummary.value.position_count = data.data.reduce(
          (sum: number, w: Watchlist) => sum + (w.stocks_count || 0),
          0
        )
      }
    }
  } catch (error) {
    console.error('加载清单失败:', error)
    ElMessage.error('加载清单失败')
  } finally {
    loading.value = false
  }
}

const selectWatchlist = async (row: Watchlist): Promise<void> => {
  selectedWatchlist.value = row
  activeTab.value = 'analysis' // Switch to analysis tab to show radar chart
  await loadWatchlistDetails(row.id)
  await loadPortfolioAnalysis(row.id)
}

const loadWatchlistDetails = async (watchlistId: number): Promise<void> => {
  try {
    const res = await fetch(`${API_BASE}/watchlists/${watchlistId}/stocks`)
    const data = await res.json()
    if (data.success) {
      watchlistStocks.value = data.data
    }
  } catch (error) {
    console.error('加载持仓失败:', error)
  }
}

const loadPortfolioAnalysis = async (watchlistId: number): Promise<void> => {
  try {
    const [summaryRes, alertsRes, rebalanceRes] = await Promise.all([
      fetch(`${API_BASE}/analysis/portfolio/${watchlistId}/summary`),
      fetch(`${API_BASE}/analysis/portfolio/${watchlistId}/alerts`),
      fetch(`${API_BASE}/analysis/portfolio/${watchlistId}/rebalance`)
    ])

    const [summaryData, alertsData, rebalanceData] = await Promise.all([
      summaryRes.json(),
      alertsRes.json(),
      rebalanceRes.json()
    ])

    if (summaryData.success) {
      portfolioSummary.value = summaryData.data
      alertSummary.value = summaryData.data.alert_summary || { critical: 0, warning: 0, info: 0 }
    }

    if (alertsData.success) {
      allAlerts.value = alertsData.data || []
    }

    if (rebalanceData.success) {
      rebalanceSuggestions.value = rebalanceData.data || []
    }

    if (selectedWatchlist.value) {
      selectedWatchlist.value.total_score = summaryData.data?.total_score?.average
      selectedWatchlist.value.stocks_count = summaryData.data?.stocks_count
    }

    if (summaryData.data?.radar_averages) {
      radarScores.value = {
        trend: summaryData.data.radar_averages.trend || 50,
        technical: summaryData.data.radar_averages.technical || 50,
        momentum: summaryData.data.radar_averages.momentum || 50,
        volatility: summaryData.data.radar_averages.volatility || 50,
        risk: summaryData.data.radar_averages.risk || 50
      }
    }
  } catch (error) {
    console.error('加载组合分析失败:', error)
  }
}

// Watchlist CRUD
const showCreateWatchlist = () => {
  editingWatchlist.value = null
  watchlistForm.name = ''
  watchlistForm.watchlist_type = 'manual'
  riskTolerance.value = 50
  createDialogVisible.value = true
}

const handleCreateWatchlist = async () => {
  if (!watchlistForm.name) {
    ElMessage.warning('请输入清单名称')
    return
  }

  try {
    const url = editingWatchlist.value
      ? `${API_BASE}/watchlists/${editingWatchlist.value.id}`
      : `${API_BASE}/watchlists`
    const method = editingWatchlist.value ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(watchlistForm)
    })

    const data = await res.json()
    if (data.success) {
      ElMessage.success(editingWatchlist.value ? '更新成功' : '创建成功')
      createDialogVisible.value = false
      loadWatchlists()
    } else {
      ElMessage.error(data.message || '操作失败')
    }
  } catch (error) {
    console.error('保存清单失败:', error)
    ElMessage.error('操作失败')
  }
}

const deleteWatchlist = async (id: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确定删除此清单？', '提示', { type: 'warning' })
    const res = await fetch(`${API_BASE}/watchlists/${id}`, { method: 'DELETE' })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('删除成功')
      if (selectedWatchlist.value?.id === id) {
        selectedWatchlist.value = null
        watchlistStocks.value = []
        portfolioSummary.value = {}
      }
      loadWatchlists()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const manageStocks = (row: Watchlist): void => {
  selectWatchlist(row)
}

// Stock Management
const showAddStock = () => {
  if (!selectedWatchlist.value) {
    ElMessage.warning('请先选择一个清单')
    return
  }
  stockForm.stock_code = ''
  stockForm.entry_price = null
  stockForm.entry_reason = null
  stockForm.stop_loss_price = null
  stockForm.target_price = null
  stockForm.weight = 0.1
  addStockDialogVisible.value = true
}

const handleAddStock = async (): Promise<void> => {
  if (!stockForm.stock_code || !stockForm.entry_price) {
    ElMessage.warning('请填写股票代码和入库价格')
    return
  }

  if (!selectedWatchlist.value) {
    ElMessage.warning('请先选择一个清单')
    return
  }

  try {
    const res = await fetch(`${API_BASE}/watchlists/${selectedWatchlist.value.id}/stocks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(stockForm)
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('添加成功')
      addStockDialogVisible.value = false
      await loadWatchlistDetails(selectedWatchlist.value.id)
      await loadPortfolioAnalysis(selectedWatchlist.value.id)
    } else {
      ElMessage.error(data.message || '添加失败')
    }
  } catch (error) {
    console.error('添加股票失败:', error)
    ElMessage.error('添加失败')
  }
}

const removeStock = async (stockId: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确定移除此股票？', '提示', { type: 'warning' })
    if (!selectedWatchlist.value) return
    const res = await fetch(`${API_BASE}/watchlists/${selectedWatchlist.value.id}/stocks/${stockId}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('移除成功')
      await loadWatchlistDetails(selectedWatchlist.value.id)
      await loadPortfolioAnalysis(selectedWatchlist.value.id)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除失败')
    }
  }
}

// Health Calculation
const calculateHealth = async (stock: WatchlistStock): Promise<void> => {
  currentStock.value = stock
  try {
    const res = await fetch(`${API_BASE}/analysis/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        stock_code: stock.stock_code,
        close: stock.entry_price,
        market_regime: 'choppy'
      })
    })
    const data = await res.json()
    if (data.success) {
      currentStockHealth.value = data.data
      healthDetailVisible.value = true
    } else {
      ElMessage.error('计算失败')
    }
  } catch (error) {
    console.error('计算健康度失败:', error)
    ElMessage.error('计算失败')
  }
}

// Helper Functions
type PortfolioStatStateClass =
  | 'portfolio-stat--neutral'
  | 'portfolio-stat--info'
  | 'portfolio-stat--success'
  | 'portfolio-stat--warning'
  | 'portfolio-stat--danger'

const getHealthStateClass = (score: number | undefined): PortfolioStatStateClass => {
  if (!score) return 'portfolio-stat--neutral'
  if (score >= 70) return 'portfolio-stat--success'
  if (score >= 50) return 'portfolio-stat--warning'
  return 'portfolio-stat--danger'
}

const getRiskStateClass = (score: number | undefined): PortfolioStatStateClass => {
  if (!score) return 'portfolio-stat--neutral'
  if (score >= 70) return 'portfolio-stat--danger'
  if (score >= 50) return 'portfolio-stat--warning'
  return 'portfolio-stat--success'
}

const getAlertStateClass = (): PortfolioStatStateClass => {
  const total = alertSummary.value.critical + alertSummary.value.warning + alertSummary.value.info
  if (alertSummary.value.critical > 0) return 'portfolio-stat--danger'
  if (total > 0) return 'portfolio-stat--warning'
  return 'portfolio-stat--success'
}

const getTypeTagType = (type: string): string => {
  const types: Record<string, string> = { manual: '', strategy: 'success', benchmark: 'info' }
  return types[type] || ''
}

const getTypeText = (type: string): string => {
  const texts: Record<string, string> = { manual: '手动', strategy: '策略', benchmark: '基准' }
  return texts[type] || type
}

const getScoreClass = (score: number | undefined): string => {
  if (!score) return ''
  if (score >= 70) return 'score-excellent'
  if (score >= 50) return 'score-good'
  return 'score-fair'
}

const getProgressColor = (score: number): string => {
  if (score >= 70) return 'var(--color-success)'
  if (score >= 50) return 'var(--color-warning)'
  return 'var(--color-danger)'
}

const getPriorityTagType = (priority: string): string => {
  const types: Record<string, string> = { critical: 'danger', high: 'warning', medium: '' }
  return types[priority] || ''
}

const getAlertType = (level: string): string => {
  const types: Record<string, string> = { critical: 'error', warning: 'warning', info: 'info' }
  return types[level] || 'info'
}

const getAlertTypeText = (type: string): string => {
  const texts: Record<string, string> = {
    stop_loss: '止损触发',
    profit_target: '止盈目标',
    weight_drift: '权重偏离'
  }
  return texts[type] || type
}

const getHealthResultIcon = (score: number | undefined): typeof CircleCheck | undefined => {
  if (!score) return undefined
  if (score >= 70) return CircleCheck
  if (score >= 50) return Warning
  return undefined
}

const getScoresTableData = () => {
  const labels: Record<string, string> = { trend: '趋势', technical: '技术', momentum: '动量', volatility: '波动', risk: '风险' }
  return Object.entries(radarScores.value).map(([key, value]) => ({
    label: labels[key] || key,
    score: value
  }))
}

onMounted(() => {
  loadWatchlists()
})

  return {
    loading,
    activeTab,
    watchlists,
    selectedWatchlist,
    watchlistStocks,
    portfolioSummary,
    radarScores,
    allAlerts,
    alertSummary,
    rebalanceSuggestions,
    createDialogVisible,
    addStockDialogVisible,
    healthDetailVisible,
    editingWatchlist,
    currentStock,
    currentStockHealth,
    watchlistForm,
    stockForm,
    riskTolerance,
    API_BASE,
    loadWatchlists,
    selectWatchlist,
    loadWatchlistDetails,
    loadPortfolioAnalysis,
    showCreateWatchlist,
    handleCreateWatchlist,
    deleteWatchlist,
    manageStocks,
    showAddStock,
    handleAddStock,
    removeStock,
    calculateHealth,
    getHealthStateClass,
    getRiskStateClass,
    getAlertStateClass,
    getTypeTagType,
    getTypeText,
    getScoreClass,
    getProgressColor,
    getPriorityTagType,
    getAlertType,
    getAlertTypeText,
    getHealthResultIcon,
    getScoresTableData,
    Plus,
    List,
    TrendCharts,
    Bell,
    DataLine,
    Tickets,
    Delete,
    InfoFilled,
    Warning,
    CircleCheck,
    CircleClose,
    HealthRadarChart,
  }
}
