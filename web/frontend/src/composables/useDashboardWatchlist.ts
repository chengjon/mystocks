import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  createMonitoringWatchlistActions,
  useWatchlistsStore,
  useWatchlistStocksStore,
} from '@/stores/apiStores'

interface StockData {
  symbol: string
  name: string
  price: number
  change: number
  volume?: number
  turnover?: number
  industry?: string
}

export function useDashboardWatchlist() {
  const watchlistsStore = useWatchlistsStore()
  const watchlistStocksStore = useWatchlistStocksStore()
  const watchlistActions = createMonitoringWatchlistActions()
  const showAddDialog = ref(false)
  const addForm = ref({
    symbol: '',
    display_name: ''
  })
  const actionPending = ref(false)
  const activeWatchlistId = ref('')

  const loading = computed(() => watchlistsStore.loading || watchlistStocksStore.loading || actionPending.value)
  const watchlistStocks = computed<StockData[]>(() => {
    const rows = (watchlistStocksStore.data as Array<Record<string, unknown>> | null) ?? []
    return rows.map((item) => ({
      symbol: String(item.symbol ?? ''),
      name: String(item.name ?? item.symbol ?? ''),
      price: Number(item.price ?? 0),
      change: Number.parseFloat(String(item.change ?? '0').replace('%', '')) || 0,
      volume: 0,
    }))
  })

  const loadWatchlist = async (): Promise<void> => {
    try {
      await watchlistsStore.refresh()
      const watchlists = (watchlistsStore.data as Array<{ id: string }> | null) ?? []
      activeWatchlistId.value = watchlists[0]?.id || ''

      if (!activeWatchlistId.value) {
        watchlistStocksStore.clear()
        return
      }

      await watchlistStocksStore.refresh({ watchlistId: activeWatchlistId.value })
    } catch (error) {
      console.error('加载自选股失败:', error)
      ElMessage.error('加载自选股失败')
    }
  }

  const handleAddToWatchlist = () => {
    addForm.value = {
      symbol: '',
      display_name: ''
    }
    showAddDialog.value = true
  }

  const confirmAddToWatchlist = async () => {
    if (!addForm.value.symbol) {
      ElMessage.warning('请输入股票代码')
      return
    }

    actionPending.value = true
    try {
      if (!activeWatchlistId.value) {
        await watchlistActions.createWatchlist('仪表盘自选')
        await watchlistsStore.refresh()
        const watchlists = (watchlistsStore.data as Array<{ id: string }> | null) ?? []
        activeWatchlistId.value = watchlists[0]?.id || ''
      } else {
        await watchlistsStore.refresh()
      }

      if (!activeWatchlistId.value) {
        ElMessage.error('缺少可用自选清单')
        return
      }

      await watchlistActions.addStock(activeWatchlistId.value, addForm.value.symbol.toUpperCase())
      ElMessage.success('添加自选股成功')
      showAddDialog.value = false
      await loadWatchlist()
    } catch (error) {
      console.error('添加自选股失败:', error)
      ElMessage.error('添加自选股失败')
    } finally {
      actionPending.value = false
    }
  }

  const removeFromWatchlist = async (symbol: string): Promise<void> => {
    if (!activeWatchlistId.value) {
      ElMessage.error('缺少可用自选清单')
      return
    }

    actionPending.value = true
    try {
      await watchlistActions.removeStock(activeWatchlistId.value, symbol)
      ElMessage.success('移除自选股成功')
      await loadWatchlist()
    } catch (error) {
      console.error('移除自选股失败:', error)
      ElMessage.error('移除自选股失败')
    } finally {
      actionPending.value = false
    }
  }

  return {
    loading,
    watchlistStocks,
    showAddDialog,
    addForm,
    loadWatchlist,
    handleAddToWatchlist,
    confirmAddToWatchlist,
    removeFromWatchlist
  }
}
