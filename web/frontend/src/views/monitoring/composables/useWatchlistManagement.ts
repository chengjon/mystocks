import { ref, reactive, computed, onMounted, type Ref } from 'vue'
import { ElMessage as message } from 'element-plus'
import {
  watchlistService,
  type AddWatchlistStockPayload,
  type CreateWatchlistPayload,
  type WatchlistRecord,
  type WatchlistStockRecord
} from '@/api/services/watchlistService'

type Watchlist = WatchlistRecord
type WatchlistStock = WatchlistStockRecord

interface WatchlistForm {
  name: string
  watchlist_type: string
  risk_profile: { risk_tolerance?: number }
}

interface StockFormType {
  stock_code: string
  entry_price: number | null
  entry_reason: string | null
  stop_loss_price: number | null
  target_price: number | null
  weight: number
}

export function useWatchlistManagement() {

const loading: Ref<boolean> = ref(false)
const watchlists: Ref<Watchlist[]> = ref([])
const watchlistStocks: Ref<WatchlistStock[]> = ref([])
const stockDrawerVisible: Ref<boolean> = ref(false)
const createModalVisible: Ref<boolean> = ref(false)
const addStockModalVisible: Ref<boolean> = ref(false)
const deleteConfirmVisible: Ref<boolean> = ref(false)
const currentWatchlist: Ref<Watchlist | null> = ref(null)
const editingWatchlist: Ref<Watchlist | null> = ref(null)
const portfolioToDelete: Ref<Watchlist | null> = ref(null)

const watchlistForm: WatchlistForm = reactive({
  name: '',
  watchlist_type: 'manual',
  risk_profile: {}
})

const stockForm: StockFormType = reactive({
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
  return watchlistStocks.value.reduce((sum, stock) => sum + (stock.alerts_count || 0), 0)
})

// 工具函数
const getTypeClass = (type: string): string => {
  const classes: Record<string, string> = {
    manual: 'type-manual',
    strategy: 'type-strategy',
    benchmark: 'type-benchmark'
  }
  return classes[type] || 'type-manual'
}

const getTypeText = (type: string): string => {
  const texts: Record<string, string> = {
    manual: 'MANUAL',
    strategy: 'STRATEGY',
    benchmark: 'BENCHMARK'
  }
  return texts[type] || type
}

const getPnlClass = (stock: WatchlistStock): string => {
  const current = stock.current_price || stock.entry_price || 0
  const entry = stock.entry_price || 0
  const pnl = ((current - entry) / entry) * 100
  return pnl >= 0 ? 'fintech-text-up' : 'fintech-text-down'
}

const getPnlPercent = (stock: WatchlistStock): string => {
  const current = stock.current_price || stock.entry_price || 0
  const entry = stock.entry_price || 0
  if (entry === 0) return '0.00%'
  const pnl = ((current - entry) / entry) * 100
  return `${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}%`
}

const getReasonClass = (reason: string | null | undefined): string => {
  const classes: Record<string, string> = {
    'macd_gold_cross': 'reason-technical',
    'rsi_oversold': 'reason-technical',
    'volume_breakout': 'reason-volume',
    'manual_pick': 'reason-manual',
    'value_investment': 'reason-value'
  }
  if (!reason) return 'reason-manual'
  return classes[reason] || 'reason-manual'
}

const getReasonText = (reason: string | null | undefined): string => {
  const texts: Record<string, string> = {
    'macd_gold_cross': 'MACD CROSS',
    'rsi_oversold': 'RSI OVERSOLD',
    'volume_breakout': 'VOL BREAKOUT',
    'manual_pick': 'MANUAL',
    'value_investment': 'VALUE'
  }
  if (!reason) return 'UNKNOWN'
  return texts[reason] || reason
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(value || 0)
}

const formatPrice = (price: number | undefined | null): string => {
  return price ? price.toFixed(2) : '-'
}

// 数据获取函数
const fetchWatchlists = async (): Promise<void> => {
  loading.value = true
  try {
    const response = await watchlistService.listWatchlists()
    if (response.success) {
      watchlists.value = response.data
    } else {
      message.error(response.message || '获取清单列表失败')
    }
  } catch (error) {
    console.error('获取清单列表失败:', error)
    message.error('获取清单列表失败')
  } finally {
    loading.value = false
  }
}

const fetchWatchlistStocks = async (watchlistId: number): Promise<void> => {
  try {
    const response = await watchlistService.listWatchlistStocks(watchlistId)
    if (response.success) {
      watchlistStocks.value = response.data
    }
  } catch (error) {
    console.error('获取股票列表失败:', error)
  }
}

const refreshData = async (): Promise<void> => {
  await fetchWatchlists()
  if (currentWatchlist.value) {
    await fetchWatchlistStocks(currentWatchlist.value.id)
  }
  message.success('数据已刷新')
}

// 事件处理函数
const handlePortfolioClick = (portfolio: Watchlist): void => {
  currentWatchlist.value = portfolio
  stockDrawerVisible.value = true
  fetchWatchlistStocks(portfolio.id)
}

const showCreateModal = (): void => {
  editingWatchlist.value = null
  watchlistForm.name = ''
  watchlistForm.watchlist_type = 'manual'
  riskTolerance.value = 50
  createModalVisible.value = true
}

const editWatchlist = (record: Watchlist): void => {
  editingWatchlist.value = record
  message.warning('编辑组合功能待接线，当前仅开放创建、删除与成分股管理')
}

const handleCreateOrUpdate = async (): Promise<void> => {
  if (editingWatchlist.value) {
    message.warning('编辑组合功能待接线，当前仅开放创建、删除与成分股管理')
    return
  }

  try {
    watchlistForm.risk_profile = { risk_tolerance: riskTolerance.value }
    const response = await watchlistService.createWatchlist({
      name: watchlistForm.name,
      watchlist_type: watchlistForm.watchlist_type,
      risk_profile: watchlistForm.risk_profile
    } satisfies CreateWatchlistPayload)

    if (response.success) {
      message.success('创建成功')
      createModalVisible.value = false
      await fetchWatchlists()
    } else {
      message.error(response.message || '操作失败')
    }
  } catch (error) {
    console.error('保存清单失败:', error)
    message.error('保存失败')
  }
}

const confirmDelete = (portfolio: Watchlist): void => {
  portfolioToDelete.value = portfolio
  deleteConfirmVisible.value = true
}

const deleteWatchlist = async (id: number): Promise<void> => {
  try {
    const response = await watchlistService.deleteWatchlist(id)
    if (response.success) {
      message.success('删除成功')
      deleteConfirmVisible.value = false
      portfolioToDelete.value = null
      await fetchWatchlists()
    } else {
      message.error(response.message || '删除失败')
    }
  } catch (error) {
    console.error('删除清单失败:', error)
    message.error('删除失败')
  }
}

const manageStocks = (record: Watchlist): void => {
  currentWatchlist.value = record
  stockDrawerVisible.value = true
  fetchWatchlistStocks(record.id)
}

const showAddStockModal = (): void => {
  stockForm.stock_code = ''
  stockForm.entry_price = null
  stockForm.entry_reason = null
  stockForm.stop_loss_price = null
  stockForm.target_price = null
  stockForm.weight = 0.1
  addStockModalVisible.value = true
}

const handleAddStock = async (): Promise<void> => {
  if (!currentWatchlist.value) return
  try {
    const response = await watchlistService.addStockToWatchlist(currentWatchlist.value.id, {
      stock_code: stockForm.stock_code,
      entry_price: stockForm.entry_price,
      entry_reason: stockForm.entry_reason,
      stop_loss_price: stockForm.stop_loss_price,
      target_price: stockForm.target_price,
      weight: stockForm.weight
    } satisfies AddWatchlistStockPayload)

    if (response.success) {
      message.success('添加成功')
      addStockModalVisible.value = false
      await fetchWatchlistStocks(currentWatchlist.value.id)
      await fetchWatchlists()
    } else {
      message.error(response.message || '添加失败')
    }
  } catch (error) {
    console.error('添加股票失败:', error)
    message.error('添加失败')
  }
}

const confirmRemoveStock = (stock: WatchlistStock): void => {
  removeStock(stock.stock_code)
}

const removeStock = async (stockCode: string): Promise<void> => {
  if (!currentWatchlist.value) return
  try {
    const response = await watchlistService.removeStockFromWatchlist(currentWatchlist.value.id, stockCode)
    if (response.success) {
      message.success('移除成功')
      await fetchWatchlistStocks(currentWatchlist.value.id)
      await fetchWatchlists()
    } else {
      message.error(response.message || '移除失败')
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
    totalPnL,
    winRate,
    activeAlerts,
    getTypeClass,
    getTypeText,
    getPnlClass,
    getPnlPercent,
    getReasonClass,
    getReasonText,
    formatCurrency,
    formatPrice,
    fetchWatchlists,
    fetchWatchlistStocks,
    refreshData,
    handlePortfolioClick,
    showCreateModal,
    editWatchlist,
    handleCreateOrUpdate,
    confirmDelete,
    deleteWatchlist,
    manageStocks,
    showAddStockModal,
    handleAddStock,
    confirmRemoveStock,
    removeStock,
  }
}
