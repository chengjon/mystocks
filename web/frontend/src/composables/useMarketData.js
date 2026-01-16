/**
 * 市场数据 Composable - 演示统一API客户端的使用
 *
 * 特性:
 * - 使用统一API客户端进行数据获取
 * - 响应式加载状态管理
 * - 错误处理和用户反馈
 * - 自动缓存和重试
 */

import { ref, computed, onMounted } from 'vue'
import { dataApi } from '@/api'
import { useLoadingStore } from '@/stores/loading'
import { getUserFriendlyErrorMessage } from '@/api/unifiedApiClient'

export function useMarketData() {
    const loadingStore = useLoadingStore()

    // 响应式数据
    const marketOverview = ref(null)
    const stocksBasic = ref([])
    const stocksIndustries = ref([])
    const stocksConcepts = ref([])

    // 加载状态
    const loadingOverview = computed(() => loadingStore.isLoading('market-overview'))
    const loadingStocks = computed(() => loadingStore.isLoading('stocks-basic'))
    const loadingIndustries = computed(() => loadingStore.isLoading('stocks-industries'))
    const loadingConcepts = computed(() => loadingStore.isLoading('stocks-concepts'))

    // 错误状态
    const error = ref(null)

    // 获取市场概览数据
    const fetchMarketOverview = async (forceRefresh = false) => {
        error.value = null
        try {
            const response = await dataApi.getMarketOverview()

            if (response.success) {
                marketOverview.value = response.data
            } else {
                throw new Error(response.message || '获取市场概览失败')
            }
        } catch (err) {
            error.value = getUserFriendlyErrorMessage(err)
            console.error('获取市场概览失败:', err)
        }
    }

    // 获取基础股票数据
    const fetchStocksBasic = async (params = {}) => {
        error.value = null
        try {
            const response = await dataApi.getStocksBasic(params)

            if (response.success) {
                stocksBasic.value = response.data || []
            } else {
                throw new Error(response.message || '获取股票数据失败')
            }
        } catch (err) {
            error.value = getUserFriendlyErrorMessage(err)
            console.error('获取股票数据失败:', err)
        }
    }

    // 获取行业分类数据
    const fetchStocksIndustries = async () => {
        error.value = null
        try {
            const response = await dataApi.getStocksIndustries()

            if (response.success) {
                stocksIndustries.value = response.data || []
            } else {
                throw new Error(response.message || '获取行业数据失败')
            }
        } catch (err) {
            error.value = getUserFriendlyErrorMessage(err)
            console.error('获取行业数据失败:', err)
        }
    }

    // 获取概念分类数据
    const fetchStocksConcepts = async () => {
        error.value = null
        try {
            const response = await dataApi.getStocksConcepts()

            if (response.success) {
                stocksConcepts.value = response.data || []
            } else {
                throw new Error(response.message || '获取概念数据失败')
            }
        } catch (err) {
            error.value = getUserFriendlyErrorMessage(err)
            console.error('获取概念数据失败:', err)
        }
    }

    // 批量获取所有市场数据
    const fetchAllMarketData = async () => {
        await Promise.allSettled([
            fetchMarketOverview(),
            fetchStocksBasic(),
            fetchStocksIndustries(),
            fetchStocksConcepts()
        ])
    }

    // 刷新所有数据
    const refreshAllData = async () => {
        await fetchAllMarketData()
    }

    // 组件挂载时自动获取数据
    onMounted(() => {
        fetchAllMarketData()
    })

    return {
        // 数据
        marketOverview: readonly(marketOverview),
        stocksBasic: readonly(stocksBasic),
        stocksIndustries: readonly(stocksIndustries),
        stocksConcepts: readonly(stocksConcepts),

        // 加载状态
        loadingOverview,
        loadingStocks,
        loadingIndustries,
        loadingConcepts,

        // 是否有任何加载状态
        isLoading: computed(
            () => loadingOverview.value || loadingStocks.value || loadingIndustries.value || loadingConcepts.value
        ),

        // 错误状态
        error: readonly(error),

        // 方法
        fetchMarketOverview,
        fetchStocksBasic,
        fetchStocksIndustries,
        fetchStocksConcepts,
        fetchAllMarketData,
        refreshAllData
    }
}
