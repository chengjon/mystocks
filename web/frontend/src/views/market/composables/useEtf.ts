import { ref, reactive, computed, onMounted, onUnmounted, type Ref } from 'vue'
import { TrendCharts, RefreshRight, Search } from '@element-plus/icons-vue'
import {
    ElCard,
    ElButton,
    ElTable,
    ElTableColumn,
    ElTabs,
    ElTabPane,
    ElInput,
    ElSelect,
    ElOption,
    ElTag,
    ElSwitch,
    ElMessage
} from 'element-plus'

// ETF data interface
interface ETFItem {
    code: string
    name: string
    price: number
    changePercent: number
    volume: number
    nav: number
    assets?: number
    trackingIndex?: string
    expenseRatio?: number
    dividendYield?: number
    change?: number
    premium?: number
    amount?: number
    type?: string
    status?: string
    [key: string]: unknown
}

export function useEtf() {

    // Reactive data
    const loading: Ref<boolean> = ref(false)
    const autoRefresh: Ref<boolean> = ref(false)
    const activeCategory: Ref<string> = ref('broad-market')
    const searchQuery: Ref<string> = ref('')
    const sortBy: Ref<string> = ref('changePercent')
    const refreshInterval: Ref<NodeJS.Timeout | null> = ref(null)

    // ETF Market Overview
    const etfMarketOverview = reactive({
        totalAssets: 2500000000000, // 2.5万亿
        totalProducts: 678,
        dailyVolume: 125000000000, // 1250亿
        avgChange: 0.85
    })

    // ETF Categories
    const etfCategories = [
        {
            key: 'broad-market',
            name: 'Broad Market ETFs',
            description: '跟踪主要市场指数的ETF产品',
            count: 156,
            avgVolume: 500000000
        },
        {
            key: 'sector-etfs',
            name: 'Sector ETFs',
            description: '跟踪特定行业板块的ETF产品',
            count: 234,
            avgVolume: 300000000
        },
        {
            key: 'bond-etfs',
            name: 'Bond ETFs',
            description: '跟踪债券市场的ETF产品',
            count: 98,
            avgVolume: 200000000
        },
        {
            key: 'international',
            name: 'International ETFs',
            description: '跟踪海外市场的ETF产品',
            count: 145,
            avgVolume: 150000000
        },
        {
            key: 'commodity-etfs',
            name: 'Commodity ETFs',
            description: '跟踪大宗商品的ETF产品',
            count: 45,
            avgVolume: 100000000
        }
    ]

    // ETF Data by Category
    const etfDataByCategory: Record<string, ETFItem[]> = {
        'broad-market': [
            {
                code: '159919',
                name: '沪深300ETF',
                type: 'Stock Index',
                price: 3.245,
                change: 0.025,
                changePercent: 0.78,
                volume: 125000000,
                amount: 405625000,
                premium: 0.12,
                nav: 3.241,
                status: 'trading'
            },
            {
                code: '159941',
                name: '纳指ETF',
                type: 'International',
                price: 2.856,
                change: -0.034,
                changePercent: -1.17,
                volume: 98000000,
                amount: 279888000,
                premium: -0.08,
                nav: 2.858,
                status: 'trading'
            },
            {
                code: '159915',
                name: '创业板ETF',
                type: 'Stock Index',
                price: 2.145,
                change: 0.018,
                changePercent: 0.85,
                volume: 156000000,
                amount: 334620000,
                premium: 0.15,
                nav: 2.142,
                status: 'trading'
            },
            {
                code: '159920',
                name: '恒生ETF',
                type: 'International',
                price: 2.967,
                change: 0.023,
                changePercent: 0.78,
                volume: 67000000,
                amount: 198789000,
                premium: 0.05,
                nav: 2.965,
                status: 'trading'
            },
            {
                code: '159922',
                name: '中证500ETF',
                type: 'Stock Index',
                price: 4.123,
                change: -0.012,
                changePercent: -0.29,
                volume: 89000000,
                amount: 366747000,
                premium: -0.03,
                nav: 4.124,
                status: 'trading'
            }
        ],
        'sector-etfs': [
            {
                code: '159915',
                name: '创业板ETF',
                type: 'Technology',
                price: 2.145,
                change: 0.018,
                changePercent: 0.85,
                volume: 156000000,
                amount: 334620000,
                premium: 0.15,
                nav: 2.142,
                status: 'trading'
            },
            {
                code: '159941',
                name: '新能源ETF',
                type: 'Energy',
                price: 0.856,
                change: -0.014,
                changePercent: -1.61,
                volume: 234000000,
                amount: 200504000,
                premium: -0.12,
                nav: 0.857,
                status: 'trading'
            },
            {
                code: '159919',
                name: '医药ETF',
                type: 'Healthcare',
                price: 0.945,
                change: 0.008,
                changePercent: 0.85,
                volume: 187000000,
                amount: 176715000,
                premium: 0.18,
                nav: 0.943,
                status: 'trading'
            },
            {
                code: '159920',
                name: '银行ETF',
                type: 'Financial',
                price: 0.967,
                change: 0.003,
                changePercent: 0.31,
                volume: 145000000,
                amount: 140215000,
                premium: 0.07,
                nav: 0.966,
                status: 'trading'
            },
            {
                code: '159922',
                name: '消费ETF',
                type: 'Consumer',
                price: 1.123,
                change: -0.005,
                changePercent: -0.44,
                volume: 98000000,
                amount: 110054000,
                premium: -0.02,
                nav: 1.123,
                status: 'trading'
            }
        ],
        'bond-etfs': [
            {
                code: '159901',
                name: '10年国债ETF',
                type: 'Government Bond',
                price: 1.056,
                change: 0.001,
                changePercent: 0.09,
                volume: 45000000,
                amount: 47520000,
                premium: 0.02,
                nav: 1.056,
                status: 'trading'
            },
            {
                code: '159902',
                name: '5年国债ETF',
                type: 'Government Bond',
                price: 1.034,
                change: 0.0,
                changePercent: 0.0,
                volume: 32000000,
                amount: 33088000,
                premium: 0.01,
                nav: 1.034,
                status: 'trading'
            },
            {
                code: '159903',
                name: '企业债ETF',
                type: 'Corporate Bond',
                price: 1.078,
                change: -0.001,
                changePercent: -0.09,
                volume: 28000000,
                amount: 30184000,
                premium: -0.03,
                nav: 1.078,
                status: 'trading'
            }
        ],
        international: [
            {
                code: '159941',
                name: '纳指ETF',
                type: 'US Market',
                price: 2.856,
                change: -0.034,
                changePercent: -1.17,
                volume: 98000000,
                amount: 279888000,
                premium: -0.08,
                nav: 2.858,
                status: 'trading'
            },
            {
                code: '159920',
                name: '恒生ETF',
                type: 'HK Market',
                price: 2.967,
                change: 0.023,
                changePercent: 0.78,
                volume: 67000000,
                amount: 198789000,
                premium: 0.05,
                nav: 2.965,
                status: 'trading'
            },
            {
                code: '159922',
                name: '日经ETF',
                type: 'Japan Market',
                price: 1.845,
                change: 0.015,
                changePercent: 0.82,
                volume: 45000000,
                amount: 82927500,
                premium: 0.12,
                nav: 1.843,
                status: 'trading'
            }
        ],
        'commodity-etfs': [
            {
                code: '159941',
                name: '黄金ETF',
                type: 'Gold',
                price: 3.456,
                change: 0.034,
                changePercent: 0.99,
                volume: 12000000,
                amount: 41472000,
                premium: 0.08,
                nav: 3.453,
                status: 'trading'
            },
            {
                code: '159915',
                name: '原油ETF',
                type: 'Oil',
                price: 2.145,
                change: -0.028,
                changePercent: -1.29,
                volume: 8500000,
                amount: 18232500,
                premium: -0.15,
                nav: 2.148,
                status: 'trading'
            }
        ]
    }

    // Top Performers
    const topGainers = ref([
        { code: '159941', name: '黄金ETF', changePercent: 2.34 },
        { code: '159915', name: '医药ETF', changePercent: 1.87 },
        { code: '159920', name: '新能源ETF', changePercent: 1.65 },
        { code: '159922', name: '消费ETF', changePercent: 1.43 },
        { code: '159919', name: '创业板ETF', changePercent: 1.21 }
    ])

    const topVolume = ref([
        { code: '159919', name: '沪深300ETF', volume: 125000000 },
        { code: '159915', name: '创业板ETF', volume: 98000000 },
        { code: '159941', name: '新能源ETF', volume: 87000000 },
        { code: '159920', name: '医药ETF', volume: 76000000 },
        { code: '159922', name: '消费ETF', volume: 65000000 }
    ])

    // Computed properties
    const currentETFs = computed(() => {
        return etfDataByCategory[activeCategory.value] || []
    })

    const filteredETFs = computed(() => {
        let etfs = [...currentETFs.value]

        // Apply search filter
        if (searchQuery.value) {
            etfs = etfs.filter(
                etf =>
                    etf.code.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                    etf.name.toLowerCase().includes(searchQuery.value.toLowerCase())
            )
        }

        // Apply sorting
        etfs.sort((a, b) => {
            switch (sortBy.value) {
                case 'name':
                    return a.name.localeCompare(b.name)
                case 'price':
                    return b.price - a.price
                case 'changePercent':
                    return b.changePercent - a.changePercent
                case 'volume':
                    return b.volume - a.volume
                default:
                    return 0
            }
        })

        return etfs
    })

    // Methods
    const refreshAllData = async (): Promise<void> => {
        loading.value = true
        try {
            await loadETFData()
            await loadTopPerformers()
            ElMessage.success('ETF data refreshed')
        } catch (error) {
            console.error('Failed to refresh ETF data:', error)
            ElMessage.error('Failed to refresh ETF data')
        } finally {
            loading.value = false
        }
    }

    const loadETFData = async (): Promise<void> => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500))

        // Update ETF data with random changes
        Object.keys(etfDataByCategory).forEach((category: string) => {
            etfDataByCategory[category].forEach((etf: ETFItem) => {
                const priceChange = (Math.random() - 0.5) * 0.1
                etf.price = parseFloat((etf.price + priceChange).toFixed(3))
                etf.change = parseFloat((etf.price - etf.nav).toFixed(3))
                etf.changePercent = parseFloat(((etf.change / etf.nav) * 100).toFixed(2))
                etf.premium = parseFloat(((etf.price / etf.nav - 1) * 100).toFixed(2))
            })
        })
    }

    const loadTopPerformers = async (): Promise<void> => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 300))

        // Update top performers
        topGainers.value.forEach(item => {
            const change = (Math.random() - 0.3) * 0.5
            item.changePercent = parseFloat((item.changePercent + change).toFixed(2))
        })

        topVolume.value.forEach(item => {
            const change = (Math.random() - 0.5) * 0.2
            item.volume = Math.round(item.volume * (1 + change))
        })
    }

    const changeCategory = (): void => {
        searchQuery.value = ''
        loadETFData()
    }

    const filterETFs = (): void => {
        // Filtering is handled by computed property
    }

    const sortETFs = (): void => {
        // Sorting is handled by computed property
    }

    const toggleAutoRefresh = (): void => {
        if (autoRefresh.value) {
            refreshInterval.value = setInterval(refreshAllData, 30000) // 30 seconds
            ElMessage.success('Auto refresh enabled')
        } else {
            if (refreshInterval.value) {
                clearInterval(refreshInterval.value)
                refreshInterval.value = null
            }
            ElMessage.info('Auto refresh disabled')
        }
    }

    const formatCurrency = (amount: number): string => {
        if (amount >= 1000000000000) {
            return (amount / 1000000000000).toFixed(2) + '万亿'
        } else if (amount >= 100000000) {
            return (amount / 100000000).toFixed(1) + '亿'
        } else if (amount >= 10000) {
            return (amount / 10000).toFixed(1) + '万'
        }
        return amount.toString()
    }

    const formatVolume = (volume: number): string => {
        if (volume >= 100000000) {
            return (volume / 100000000).toFixed(1) + '亿'
        } else if (volume >= 10000) {
            return (volume / 10000).toFixed(1) + '万'
        }
        return volume.toString()
    }

    const formatAmount = (amount: number): string => {
        if (amount >= 100000000) {
            return (amount / 100000000).toFixed(2) + '亿'
        } else if (amount >= 10000) {
            return (amount / 10000).toFixed(2) + '万'
        }
        return amount.toString()
    }

    // Lifecycle
    onMounted(async () => {
        await loadETFData()
        await loadTopPerformers()
    })

    onUnmounted(() => {
        if (refreshInterval.value) {
            clearInterval(refreshInterval.value)
        }
    })

  return {
    loading,
    autoRefresh,
    activeCategory,
    searchQuery,
    sortBy,
    refreshInterval,
    etfMarketOverview,
    etfCategories,
    etfDataByCategory,
    topGainers,
    topVolume,
    currentETFs,
    filteredETFs,
    refreshAllData,
    loadETFData,
    loadTopPerformers,
    changeCategory,
    filterETFs,
    sortETFs,
    toggleAutoRefresh,
    formatCurrency,
    formatVolume,
    formatAmount,
  }
}
