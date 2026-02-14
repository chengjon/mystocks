import { ref, reactive, computed, onMounted } from 'vue'
import {
import { ElMessage as message } from 'element-plus'

export function useWatchlistManagement() {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SettingOutlined,
  CloseOutlined,
  FolderOpenOutlined,
  StockOutlined,
  AlertOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue'

const loading = ref(false)
const watchlists = ref([])
const watchlistStocks = ref([])
const stockDrawerVisible = ref(false)
const createModalVisible = ref(false)
const addStockModalVisible = ref(false)
const deleteConfirmVisible = ref(false)
const currentWatchlist = ref(null)
const editingWatchlist = ref(null)
const portfolioToDelete = ref(null)

const watchlistForm = reactive({
  name: '',
  watchlist_type: 'manual',
  risk_profile: {}
})

const stockForm = reactive({
  stock_code: '',
  entry_price: null,
  entry_reason: null,
  stop_loss_price: null,
  target_price: null,
  weight: 0.1
})

const riskTolerance = ref(50)

// 计算属性
const totalStocks = computed(() => {
  return watchlists.value.reduce((sum, wl) => sum + (wl.stocks_count || 0), 0)
})

const totalValue = computed(() => {
  return watchlistStocks.value.reduce((sum, stock) => {
    const price = stock.current_price || stock.entry_price || 0
    return sum + (price * (stock.weight || 1))
  }, 0)
})

const totalPnL = computed(() => {
  return watchlistStocks.value.reduce((sum, stock) => {
    const current = stock.current_price || stock.entry_price || 0
    const entry = stock.entry_price || 0
    const pnl = (current - entry) * (stock.weight || 1)
    return sum + pnl
  }, 0)
})

const winRate = computed(() => {
  if (watchlistStocks.value.length === 0) return 0
  const winners = watchlistStocks.value.filter(stock => {
    const current = stock.current_price || stock.entry_price || 0
    const entry = stock.entry_price || 0
    return current > entry
  }).length
  return Math.round((winners / watchlistStocks.value.length) * 100)
})

const activeAlerts = computed(() => {
  // 计算活跃告警数量（模拟数据）
  return Math.floor(Math.random() * 5)
})

// 工具函数
const getTypeClass = (type) => {
  const classes = {
    manual: 'type-manual',
    strategy: 'type-strategy',
    benchmark: 'type-benchmark'
  }
  return classes[type] || 'type-manual'
}

const getTypeText = (type) => {
  const texts = {
    manual: 'MANUAL',
    strategy: 'STRATEGY',
    benchmark: 'BENCHMARK'
  }
  return texts[type] || type
}

const getPnlClass = (stock) => {
  const current = stock.current_price || stock.entry_price || 0
  const entry = stock.entry_price || 0
  const pnl = ((current - entry) / entry) * 100
  return pnl >= 0 ? 'fintech-text-up' : 'fintech-text-down'
}

const getPnlPercent = (stock) => {
  const current = stock.current_price || stock.entry_price || 0
  const entry = stock.entry_price || 0
  if (entry === 0) return '0.00%'
  const pnl = ((current - entry) / entry) * 100
  return `${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}%`
}

const getReasonClass = (reason) => {
  const classes = {
    'macd_gold_cross': 'reason-technical',
    'rsi_oversold': 'reason-technical',
    'volume_breakout': 'reason-volume',
    'manual_pick': 'reason-manual',
    'value_investment': 'reason-value'
  }
  return classes[reason] || 'reason-manual'
}

const getReasonText = (reason) => {
  const texts = {
    'macd_gold_cross': 'MACD CROSS',
    'rsi_oversold': 'RSI OVERSOLD',
    'volume_breakout': 'VOL BREAKOUT',
    'manual_pick': 'MANUAL',
    'value_investment': 'VALUE'
  }
  return texts[reason] || reason || 'UNKNOWN'
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(value || 0)
}

const formatPrice = (price) => {
  return price ? price.toFixed(2) : '-'
}

// 数据获取函数
const fetchWatchlists = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/monitoring/watchlists')
    const data = await res.json()
    if (data.success) {
      watchlists.value = data.data
    }
  } catch (error) {
    console.error('获取清单列表失败:', error)
    message.error('获取清单列表失败')
  } finally {
    loading.value = false
  }
}

const fetchWatchlistStocks = async (watchlistId) => {
  try {
    const res = await fetch(`/api/monitoring/watchlists/${watchlistId}/stocks`)
    const data = await res.json()
    if (data.success) {
      watchlistStocks.value = data.data
    }
  } catch (error) {
    console.error('获取股票列表失败:', error)
  }
}

const refreshData = async () => {
  await fetchWatchlists()
  if (currentWatchlist.value) {
    await fetchWatchlistStocks(currentWatchlist.value.id)
  }
  message.success('数据已刷新')
}

// 事件处理函数
const handlePortfolioClick = (portfolio) => {
  currentWatchlist.value = portfolio
  stockDrawerVisible.value = true
  fetchWatchlistStocks(portfolio.id)
}

const showCreateModal = () => {
  editingWatchlist.value = null
  watchlistForm.name = ''
  watchlistForm.watchlist_type = 'manual'
  riskTolerance.value = 50
  createModalVisible.value = true
}

const editWatchlist = (record) => {
  editingWatchlist.value = record
  watchlistForm.name = record.name
  watchlistForm.watchlist_type = record.watchlist_type
  riskTolerance.value = record.risk_profile?.risk_tolerance || 50
  createModalVisible.value = true
}

const handleCreateOrUpdate = async () => {
  try {
    watchlistForm.risk_profile = { risk_tolerance: riskTolerance.value }

    const url = editingWatchlist.value
      ? `/api/monitoring/watchlists/${editingWatchlist.value.id}`
      : '/api/monitoring/watchlists'

    const method = editingWatchlist.value ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(watchlistForm)
    })

    const data = await res.json()
    if (data.success) {
      message.success(editingWatchlist.value ? '更新成功' : '创建成功')
      createModalVisible.value = false
      await fetchWatchlists()
    } else {
      message.error(data.message || '操作失败')
    }
  } catch (error) {
    console.error('保存清单失败:', error)
    message.error('保存失败')
  }
}

const confirmDelete = (portfolio) => {
  portfolioToDelete.value = portfolio
  deleteConfirmVisible.value = true
}

const deleteWatchlist = async (id) => {
  try {
    const res = await fetch(`/api/monitoring/watchlists/${id}`, { method: 'DELETE' })
    const data = await res.json()
    if (data.success) {
      message.success('删除成功')
      deleteConfirmVisible.value = false
      portfolioToDelete.value = null
      await fetchWatchlists()
    } else {
      message.error(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除清单失败:', error)
    message.error('删除失败')
  }
}

const manageStocks = (record) => {
  currentWatchlist.value = record
  stockDrawerVisible.value = true
  fetchWatchlistStocks(record.id)
}

const showAddStockModal = () => {
  stockForm.stock_code = ''
  stockForm.entry_price = null
  stockForm.entry_reason = null
  stockForm.stop_loss_price = null
  stockForm.target_price = null
  stockForm.weight = 0.1
  addStockModalVisible.value = true
}

const handleAddStock = async () => {
  try {
    const res = await fetch(`/api/monitoring/watchlists/${currentWatchlist.value.id}/stocks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(stockForm)
    })

    const data = await res.json()
    if (data.success) {
      message.success('添加成功')
      addStockModalVisible.value = false
      await fetchWatchlistStocks(currentWatchlist.value.id)
      await fetchWatchlists()
    } else {
      message.error(data.message || '添加失败')
    }
  } catch (error) {
    console.error('添加股票失败:', error)
    message.error('添加失败')
  }
}

const confirmRemoveStock = (stock) => {
  // 简化版：直接删除
  removeStock(stock.id)
}

const removeStock = async (stockId) => {
  try {
    const res = await fetch(`/api/monitoring/watchlists/${currentWatchlist.value.id}/stocks/${stockId}`, {
      method: 'DELETE'
    })

    const data = await res.json()
    if (data.success) {
      message.success('移除成功')
      await fetchWatchlistStocks(currentWatchlist.value.id)
      await fetchWatchlists()
    } else {
      message.error(data.message || '移除失败')
    }
  } catch (error) {
    console.error('移除股票失败:', error)
    message.error('移除失败')
  }
}

onMounted(() => {
  fetchWatchlists()
})

  return {
    loading,
    watchlists,
    watchlistStocks,
    stockDrawerVisible,
    createModalVisible,
    addStockModalVisible,
    deleteConfirmVisible,
    currentWatchlist,
    editingWatchlist,
    portfolioToDelete,
    watchlistForm,
    stockForm,
    riskTolerance,
    totalStocks,
    totalValue,
    price,
    totalPnL,
    current,
    entry,
    pnl,
    winRate,
    winners,
    current,
    entry,
    activeAlerts,
    getTypeClass,
    classes,
    getTypeText,
    texts,
    getPnlClass,
    current,
    entry,
    pnl,
    getPnlPercent,
    current,
    entry,
    pnl,
    getReasonClass,
    classes,
    getReasonText,
    texts,
    formatCurrency,
    formatPrice,
    fetchWatchlists,
    res,
    data,
    fetchWatchlistStocks,
    res,
    data,
    refreshData,
    handlePortfolioClick,
    showCreateModal,
    editWatchlist,
    handleCreateOrUpdate,
    url,
    method,
    res,
    data,
    confirmDelete,
    deleteWatchlist,
    res,
    data,
    manageStocks,
    showAddStockModal,
    handleAddStock,
    res,
    data,
    confirmRemoveStock,
    removeStock,
    res,
    data,
  }
}
