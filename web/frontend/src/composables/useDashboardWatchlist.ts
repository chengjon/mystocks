import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { apiClient } from '@/api/apiClient'
import type { WatchlistItem } from '@/api/types/common'

interface StockData {
  symbol: string
  name: string
  price: number
  change: number
  volume?: number
  turnover?: number
  industry?: string
}

// Watchlist API wrapper
const watchlistApi = {
  getWatchlist: () => apiClient.get('/api/watchlist'),
  addToWatchlist: (data: { symbol: string; display_name?: string }) => apiClient.post('/api/watchlist', data),
  removeFromWatchlist: (symbol: string) => apiClient.delete(`/api/watchlist/${symbol}`)
}

export function useDashboardWatchlist() {
  const loading = ref(false)
  const watchlistStocks = ref<StockData[]>([])
  const showAddDialog = ref(false)
  const addForm = ref({
    symbol: '',
    display_name: ''
  })

  const loadWatchlist = async (): Promise<void> => {
    loading.value = true
    try {
      const response = await watchlistApi.getWatchlist()
      const apiResponse = response as { success?: boolean; data?: { items?: WatchlistItem[] } | WatchlistItem[]; message?: string }
      if (apiResponse?.success && apiResponse.data) {
        const items = (apiResponse.data as { items?: WatchlistItem[] }).items || apiResponse.data as WatchlistItem[]
        const data: WatchlistItem[] = Array.isArray(items) ? items : []
        watchlistStocks.value = data.map((item: WatchlistItem): StockData => ({
          symbol: item.symbol || '',
          name: item.name || item.symbol || '',
          price: item.current_price || 0,
          change: item.change_percent || 0,
          volume: 0
        }))
      } else {
        ElMessage.error(apiResponse?.message || '加载自选股失败')
        watchlistStocks.value = []
      }
    } catch (error) {
      console.error('加载自选股失败:', error)
      ElMessage.error('加载自选股失败')
      watchlistStocks.value = []
    } finally {
      loading.value = false
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

    loading.value = true
    try {
      const response = await watchlistApi.addToWatchlist({
        symbol: addForm.value.symbol.toUpperCase(),
        display_name: addForm.value.display_name
      })

      const apiResponse = response.data as { success?: boolean; message?: string }
      if (apiResponse?.success) {
        ElMessage.success('添加自选股成功')
        showAddDialog.value = false
        await loadWatchlist()
      } else {
        ElMessage.error(apiResponse?.message || '添加自选股失败')
      }
    } catch (error) {
      console.error('添加自选股失败:', error)
      ElMessage.error('添加自选股失败')
    } finally {
      loading.value = false
    }
  }

  const removeFromWatchlist = async (symbol: string): Promise<void> => {
    loading.value = true
    try {
      const response = await watchlistApi.removeFromWatchlist(symbol)
      const apiResponse = response.data as { success?: boolean; message?: string }
      if (apiResponse?.success) {
        ElMessage.success('移除自选股成功')
        await loadWatchlist()
      } else {
        ElMessage.error(apiResponse?.message || '移除自选股失败')
      }
    } catch (error) {
      console.error('移除自选股失败:', error)
      ElMessage.error('移除自选股失败')
    } finally {
      loading.value = false
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
