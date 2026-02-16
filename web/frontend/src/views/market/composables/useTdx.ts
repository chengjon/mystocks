import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { Connection, RefreshRight, Timer, DataLine, Search } from '@element-plus/icons-vue'
import {
    ElCard,
    ElButton,
    ElInput,
    ElSelect,
    ElOption,
    ElDatePicker,
    ElTag,
    ElEmpty,
    ElMessage
} from 'element-plus'

interface TdxQuote {
    code: string
    name: string
    price: number
    change: number
    change_pct: number
    open: number
    pre_close: number
    high: number
    low: number
    volume: number
    amount: number
    ask1: number
    ask1_volume: number
    bid1: number
    bid1_volume: number
    status: 'trading' | 'closed'
}

export function useTdx() {

    // Reactive data
    const loading = ref(false)
    const quoteLoading = ref(false)
    const chartLoading = ref(false)
    const searchSymbol = ref('600519')
    const selectedPeriod = ref('1d')
    const chartHeight = ref('400px')
    const lastUpdate = ref('')

    // Connection status
    const connectionStatus = ref<'connecting' | 'connected' | 'disconnected'>('connecting')
    const responseTime = ref(0)
    const activeSessions = ref(0)

    // Server information
    const primaryServer = ref('202.108.253.132:7709')
    const backupServers = ref(['202.108.253.133:7709', '202.108.253.134:7709', '61.152.107.141:7709'])

    // Current quote data
    const currentQuote = ref<TdxQuote | null>(null)

    // Chart date range
    const chartDateRange = ref([
        new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
        new Date().toISOString().split('T')[0]
    ])

    // Methods
    const refreshAllData = async (): Promise<void> => {
        loading.value = true
        try {
            await Promise.all([checkConnectionStatus(), fetchQuote()])
            updateLastUpdateTime()
            ElMessage.success('All data refreshed')
        } catch (error) {
            console.error('Failed to refresh all data:', error)
            ElMessage.error('Failed to refresh data')
        } finally {
            loading.value = false
        }
    }

    const checkConnectionStatus = async (): Promise<void> => {
        try {
            // TODO: Replace with actual TDX connection check API
            // const response = await axios.get('/api/tdx/health')

            // Simulate connection check
            await new Promise(resolve => setTimeout(resolve, 500))

            connectionStatus.value = 'connected'
            responseTime.value = Math.floor(Math.random() * 100) + 50 // 50-150ms
            activeSessions.value = Math.floor(Math.random() * 10) + 1 // 1-10 sessions
        } catch (error) {
            connectionStatus.value = 'disconnected'
            console.error('Connection check failed:', error)
        }
    }

    const fetchQuote = async (): Promise<void> => {
        if (!searchSymbol.value) {
            ElMessage.warning('Please enter a stock symbol')
            return
        }

        quoteLoading.value = true
        try {
            // TODO: Replace with actual TDX quote API
            // const response = await axios.get(`/api/tdx/quote/${searchSymbol.value}`)

            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 300))

            // Mock quote data
            currentQuote.value = {
                code: searchSymbol.value,
                name: searchSymbol.value === '600519' ? '贵州茅台' : 'Sample Stock',
                price: 1850 + Math.random() * 100,
                change: (Math.random() - 0.5) * 20,
                change_pct: (Math.random() - 0.5) * 2,
                open: 1830 + Math.random() * 20,
                pre_close: 1840 + Math.random() * 20,
                high: 1860 + Math.random() * 40,
                low: 1820 + Math.random() * 20,
                volume: Math.floor(Math.random() * 1000000) + 100000,
                amount: Math.floor(Math.random() * 100000000) + 10000000,
                ask1: 1850 + Math.random() * 100 + 0.01,
                ask1_volume: Math.floor(Math.random() * 1000) + 100,
                bid1: 1850 + Math.random() * 100 - 0.01,
                bid1_volume: Math.floor(Math.random() * 1000) + 100,
                status: 'trading'
            }

            updateLastUpdateTime()
        } catch (error) {
            console.error('Failed to fetch quote:', error)
            ElMessage.error('Failed to fetch quote data')
        } finally {
            quoteLoading.value = false
        }
    }

    const changePeriod = (): void => {
        // TODO: Update chart with new period
        loadChartData()
    }

    const changeDateRange = (): void => {
        // TODO: Update chart with new date range
        loadChartData()
    }

    const loadChartData = async (): Promise<void> => {
        if (!searchSymbol.value) return

        chartLoading.value = true
        try {
            // TODO: Implement chart data loading
            // const response = await axios.get('/api/tdx/kline', {
            //   params: {
            //     symbol: searchSymbol.value,
            //     period: selectedPeriod.value,
            //     start_date: chartDateRange.value[0],
            //     end_date: chartDateRange.value[1]
            //   }
            // })

            await new Promise(resolve => setTimeout(resolve, 500))
            // Mock chart loading
        } catch (error) {
            console.error('Failed to load chart data:', error)
        } finally {
            chartLoading.value = false
        }
    }

    const updateLastUpdateTime = (): void => {
        const now = new Date()
        lastUpdate.value = now.toLocaleString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    const getPriceClass = (changePct: number): string => {
        if (changePct > 0) return 'positive'
        if (changePct < 0) return 'negative'
        return 'neutral'
    }

    const formatChange = (change: number): string => {
        if (!change) return '--'
        return (change > 0 ? '+' : '') + change.toFixed(2)
    }

    const formatChangePct = (changePct: number): string => {
        if (!changePct) return '--'
        return (changePct > 0 ? '+' : '') + changePct.toFixed(2) + '%'
    }

    const formatVolume = (volume: number, compact: boolean = false): string => {
        if (!volume) return '--'

        if (compact) {
            if (volume >= 10000) {
                return (volume / 10000).toFixed(1) + '万'
            }
            return volume.toString()
        }

        if (volume >= 100000000) {
            return (volume / 100000000).toFixed(1) + '亿'
        } else if (volume >= 10000) {
            return (volume / 10000).toFixed(1) + '万'
        }
        return volume.toString()
    }

    const formatAmount = (amount: number): string => {
        if (!amount) return '--'

        if (amount >= 100000000) {
            return (amount / 100000000).toFixed(2) + '亿'
        } else if (amount >= 10000) {
            return (amount / 10000).toFixed(2) + '万'
        }
        return amount.toString()
    }

    // Lifecycle
    onMounted(async () => {
        await checkConnectionStatus()
        if (searchSymbol.value) {
            await fetchQuote()
        }
    })

  return {
    loading,
    quoteLoading,
    chartLoading,
    searchSymbol,
    selectedPeriod,
    chartHeight,
    lastUpdate,
    connectionStatus,
    responseTime,
    activeSessions,
    primaryServer,
    backupServers,
    currentQuote,
    chartDateRange,
    refreshAllData,
    checkConnectionStatus,
    fetchQuote,
    changePeriod,
    changeDateRange,
    loadChartData,
    updateLastUpdateTime,
    getPriceClass,
    formatChange,
    formatChangePct,
    formatVolume,
    formatAmount,
  }
}
