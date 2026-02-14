import { ref, onMounted, reactive, watch } from 'vue'
import { dashboardService } from '@/services/dashboardService'
import { ElMessage } from 'element-plus'
import { Document, Money, PieChart, Grid } from '@element-plus/icons-vue'
import { useDashboardCharts } from '@/composables/useDashboardCharts'
import { useDashboardWatchlist } from '@/composables/useDashboardWatchlist'
interface StockData {
interface StrategyStock {
interface StatItem {

export function useEnhancedDashboard() {

  symbol: string
  name: string
  price: number
  change: number
  volume?: number
  turnover?: number
  industry?: string
}

  symbol: string
  name: string
  price: number
  change: number
  strategy: string
  score: number
  signal: string
}

  title: string
  value: string
  icon: unknown
  color: string
  trend: string
  trendClass: string
}

const loading = reactive({
  main: false,
  overview: false
})

const activeMarketTab = ref('heat')
const activeSectorTab = ref('favorites')
const industryStandard = ref('csrc')

const {
  priceDistributionData,
  priceDistributionOptions,
  marketHeatData,
  marketHeatOptions,
  leadingSectorData,
  leadingSectorOptions,
  capitalFlowData,
  capitalFlowOptions,
  capitalFlowData2,
  capitalFlowOptions2,
  industryData,
  industryOptions,
  priceDistributionChartRef,
  marketHeatChartRef,
  leadingSectorChartRef,
  capitalFlowChartRef,
  capitalFlowChartRef2,
  industryChartRef,
  updatePriceDistributionChart,
  initCharts
} = useDashboardCharts(industryStandard)

const {
  loading: watchlistLoading,
  watchlistStocks,
  showAddDialog,
  addForm,
  loadWatchlist,
  handleAddToWatchlist,
  confirmAddToWatchlist,
  removeFromWatchlist
} = useDashboardWatchlist()

const stats = ref<StatItem[]>([
  { title: '总股票数', value: '0', icon: Document, color: '#409EFF', trend: '+0%', trendClass: 'neutral' },
  { title: '总市值', value: '0', icon: Money, color: '#67C23A', trend: '+0%', trendClass: 'up' },
  { title: '市场分布', value: '0', icon: PieChart, color: '#E6A23C', trend: '+0%', trendClass: 'up' },
  { title: '行业分布', value: '0', icon: Grid, color: '#F56C6C', trend: '+0%', trendClass: 'down' }
])

const hotIndustries = ref<Array<{ industry_name: string; avg_change: number; stock_count: number }>>([])
const hotConcepts = ref<Array<{ concept_name: string; avg_change: number; stock_count: number }>>([])
const favoriteStocks = ref<StockData[]>([])
const strategyStocks = ref<StrategyStock[]>([])

const getIconComponent = (iconComponent: unknown): unknown => iconComponent

const getColorType = (color: string): string => {
  if (color === '#67C23A') return 'green'
  if (color === '#F56C6C') return 'red'
  if (color === '#E6A23C') return 'orange'
  if (color === '#409EFF') return 'blue'
  return 'gold'
}

const getPriceChangeClass = (change: number): string => {
  if (change > 0) return 'text-red'
  if (change < 0) return 'text-green'
  return ''
}

const formatPriceChange = (change: number | undefined | null): string => {
  if (change === undefined || change === null) return '--'
  return `${change > 0 ? '+' : ''}${change}%`
}

const getSignalTagType = (signal: string): 'danger' | 'success' | 'info' => {
  if (signal === '买入') return 'danger'
  if (signal === '卖出') return 'success'
  return 'info'
}

const loadMarketOverview = async () => {
  loading.overview = true
  try {
    const response = await dashboardService.getMarketOverview()

    if (response.success && response.data) {
      const marketData = response.data

      const marketStats = marketData.market_stats
      stats.value[0].value = marketStats?.total_stocks?.toString() || '0'
      stats.value[1].value = marketStats?.avg_change_percent?.toFixed(2) || '0.00'
      stats.value[2].value = `${marketStats?.rising_stocks || 0}涨 / ${marketStats?.falling_stocks || 0}跌`
      stats.value[3].value = '加载中...'
    } else {
      ElMessage.error(response.message || '加载市场概览失败')
    }

    await loadPriceDistribution()

    await Promise.all([
      loadHotIndustries(),
      loadHotConcepts()
    ])
  } catch (error) {
    console.error('加载市场概览失败:', error)
    ElMessage.error('加载市场概览失败')
  } finally {
    loading.overview = false
  }
}

const loadPriceDistribution = async () => {
  try {
    const response = await dashboardService.getPriceDistribution()
    if (response.success && response.data) {
      updatePriceDistributionChart(response.data)
    } else {
      ElMessage.error(response.message || '加载涨跌分布失败')
    }
  } catch (error) {
    console.error('加载涨跌分布失败:', error)
    ElMessage.error('加载涨跌分布失败')
  }
}

const loadHotIndustries = async () => {
  try {
    const response = await dashboardService.getHotIndustries()
    if (response.success && response.data) {
      hotIndustries.value = response.data as Array<{ industry_name: string; avg_change: number; stock_count: number }>
    } else {
      ElMessage.error(response.message || '加载热门行业失败')
    }
  } catch (error) {
    console.error('加载热门行业失败:', error)
    ElMessage.error('加载热门行业失败')
  }
}

const loadHotConcepts = async () => {
  try {
    const response = await dashboardService.getHotConcepts()
    if (response.success && response.data) {
      // IndustryConceptData 使用 industry_name 字段（包括行业和概念）
      hotConcepts.value = response.data.map(item => ({
        concept_name: item.industry_name,
        avg_change: item.avg_change,
        stock_count: item.stock_count
      }))
    } else {
      ElMessage.error(response.message || '加载热门概念失败')
    }
  } catch (error) {
    console.error('加载热门概念失败:', error)
    ElMessage.error('加载热门概念失败')
  }
}

const loadFavoriteStocks = async () => {
  try {
    const response = await dashboardService.getMarketOverview()
    if (response.success && response.data && response.data.top_etfs) {
      favoriteStocks.value = response.data.top_etfs.slice(0, 5).map((item: unknown): StockData => ({
        symbol: (item as Record<string, unknown>).symbol as string || 'ETF',
        name: (item as Record<string, unknown>).name as string || 'ETF基金',
        price: (item as Record<string, unknown>).latest_price as number || 0,
        change: (item as Record<string, unknown>).change_percent as number || 0,
        volume: (item as Record<string, unknown>).volume as number || 0,
        turnover: (item as Record<string, unknown>).turnover_rate as number || 0,
        industry: 'ETF'
      }))
    } else {
      ElMessage.error(response.message || '加载自选股失败')
    }
  } catch (error) {
    console.error('加载自选股失败:', error)
    ElMessage.error('加载自选股失败')
  }
}

const loadStrategyStocks = async () => {
  try {
    const response = await dashboardService.getMarketHeatChartData()
    if (response.success && response.data) {
      strategyStocks.value = response.data.map((item: unknown): StrategyStock => ({
        symbol: (item as Record<string, unknown>).name as string,
        name: (item as Record<string, unknown>).name as string,
        price: 0,
        change: 0,
        strategy: '未知策略',
        score: (item as Record<string, unknown>).value as number,
        signal: (item as Record<string, unknown>).value as number > 80 ? '买入' : ((item as Record<string, unknown>).value as number < 70 ? '卖出' : '持有')
      }))
    } else {
      ElMessage.error(response.message || '加载策略选股失败')
    }
  } catch (error) {
    console.error('加载策略选股失败:', error)
    ElMessage.error('加载策略选股失败')
  }
}

const handleRetry = async () => {
  try {
    await loadData()
    ElMessage.success('数据已刷新')
  } catch (_error) {
    ElMessage.error('刷新失败，请稍后重试')
  }
}

const handleRefresh = () => {
  ElMessage.success('数据已刷新')
  loadData()
}

const loadData = async () => {
  loading.main = true
  try {
    await Promise.all([
      loadMarketOverview(),
      loadFavoriteStocks(),
      loadStrategyStocks(),
      loadWatchlist()
    ])
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.main = false
  }
}

watch(industryStandard, async () => {
  await initCharts()
})

onMounted(() => {
  initCharts()
  loadData()
})

  return {
    loading,
    activeMarketTab,
    activeSectorTab,
    industryStandard,
    stats,
    hotIndustries,
    hotConcepts,
    favoriteStocks,
    strategyStocks,
    getIconComponent,
    getColorType,
    getPriceChangeClass,
    formatPriceChange,
    getSignalTagType,
    loadMarketOverview,
    response,
    marketData,
    marketStats,
    loadPriceDistribution,
    response,
    loadHotIndustries,
    response,
    loadHotConcepts,
    response,
    loadFavoriteStocks,
    response,
    loadStrategyStocks,
    response,
    handleRetry,
    handleRefresh,
    loadData,
  }
}
