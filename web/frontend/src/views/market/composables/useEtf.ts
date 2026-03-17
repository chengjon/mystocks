import { ref, reactive, computed, onMounted, onUnmounted, type Ref } from 'vue'
import { ElMessage } from 'element-plus'

import {
    createEtfCategories,
    createEtfDataByCategory,
    createEtfMarketOverview,
    createTopGainers,
    createTopVolume,
    type ETFItem
} from './useEtf.data'

export function useEtf() {

    const loading: Ref<boolean> = ref(false)
    const autoRefresh: Ref<boolean> = ref(false)
    const activeCategory: Ref<string> = ref('broad-market')
    const searchQuery: Ref<string> = ref('')
    const sortBy: Ref<string> = ref('changePercent')
    const refreshInterval: Ref<NodeJS.Timeout | null> = ref(null)

    const etfMarketOverview = reactive(createEtfMarketOverview())
    const etfCategories = createEtfCategories()
    const etfDataByCategory: Record<string, ETFItem[]> = createEtfDataByCategory()
    const topGainers = ref(createTopGainers())
    const topVolume = ref(createTopVolume())

    const currentETFs = computed(() => {
        return etfDataByCategory[activeCategory.value] || []
    })

    const filteredETFs = computed(() => {
        let etfs = [...currentETFs.value]

        if (searchQuery.value) {
            etfs = etfs.filter(
                etf =>
                    etf.code.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                    etf.name.toLowerCase().includes(searchQuery.value.toLowerCase())
            )
        }

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
        await new Promise(resolve => setTimeout(resolve, 500))

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
        await new Promise(resolve => setTimeout(resolve, 300))

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
    }

    const sortETFs = (): void => {
    }

    const toggleAutoRefresh = (): void => {
        if (autoRefresh.value) {
            refreshInterval.value = setInterval(refreshAllData, 30000)
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
