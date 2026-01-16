// Trading Store - Pinia状态管理 for ArtDeco量化交易管理中心
// 集成TradingApiManager，实现完整的状态管理和数据流转

import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import { tradingApiManager, type TradingApiManager } from '@/services/TradingApiManager'
import type {
    MarketOverview,
    TradingSignals,
    TradingHistory,
    PositionMonitorData,
    PerformanceAnalysis,
    StrategyManagementData,
    RiskMonitorData,
    AnnouncementMonitorData,
    RiskAlertsData,
    MonitoringDashboardData,
    SystemSettings,
    SystemHealth,
} from '@/services/TradingApiManager'

export interface TradingState {
    // 功能状态
    activeFunction: string
    expandedNodes: Set<string>
    loadingStates: Record<string, boolean>

    // 数据缓存
    cache: Map<string, CachedData>

    // 系统状态
    systemHealth: SystemHealth | null
    lastUpdateTime: string

    // 市场数据
    marketOverview: MarketOverview | null
    marketAnalysis: MarketAnalysis | null

    // 交易数据
    tradingSignals: TradingSignals | null
    tradingHistory: TradingHistory | null
    positionMonitor: PositionMonitorData | null
    performanceAnalysis: PerformanceAnalysis | null

    // 策略数据
    strategyManagement: StrategyManagementData | null
    backtestResults: BacktestResult[]
    optimizationTasks: OptimizationTask[]

    // 风险数据
    riskMonitor: RiskMonitorData | null
    announcementMonitor: AnnouncementMonitorData | null
    riskAlerts: RiskAlertsData | null

    // 系统数据
    monitoringDashboard: MonitoringDashboardData | null
    systemSettings: SystemSettings | null
    systemConfig: Record<string, any> | null
}

// 类型定义
interface MarketAnalysis {
    trend?: string
    sentiment?: number
    volatility?: number
    volume?: number
    [key: string]: any // 允许扩展属性
}

interface BacktestResult {
    id?: string
    strategyId?: string
    status?: 'pending' | 'running' | 'completed' | 'failed'
    result?: any
    error?: string
    startTime?: Date
    endTime?: Date
}

interface OptimizationTask {
    id?: string
    strategyId?: string
    status?: 'pending' | 'running' | 'completed' | 'failed'
    parameters?: Record<string, any>
    result?: any
    error?: string
    startTime?: Date
    endTime?: Date
}

interface TradingFilters {
    symbol?: string
    dateFrom?: string
    dateTo?: string
    status?: string
    [key: string]: any
}

interface HistoryFilters {
    symbol: string
    type: string
    dateRange: [Date, Date]
    status: string
}

interface RealtimeUpdate {
    type: string
    data: any
    timestamp: number
}

interface CachedData<T = any> {
    data: T
    timestamp: number
    ttl: number
}

export const useTradingStore = defineStore('trading', () => {
    // 状态
    const state = reactive<TradingState>({
        activeFunction: 'market-overview',
        expandedNodes: new Set(['market-overview', 'trading-management']),
        loadingStates: {},
        cache: new Map(),
        systemHealth: null,
        lastUpdateTime: new Date().toLocaleTimeString('zh-CN'),
        marketOverview: null,
        marketAnalysis: null,
        tradingSignals: null,
        tradingHistory: null,
        positionMonitor: null,
        performanceAnalysis: null,
        strategyManagement: null,
        backtestResults: [],
        optimizationTasks: [],
        riskMonitor: null,
        announcementMonitor: null,
        riskAlerts: null,
        monitoringDashboard: null,
        systemSettings: null,
        systemConfig: null
    })

    // 计算属性
    const isLoading = computed(() => {
        return Object.values(state.loadingStates).some(loading => loading)
    })

    const hasValidCache = computed(() => (key: string, maxAge: number = 300000): boolean => {
        const cached = state.cache.get(key)
        if (!cached) return false
        return Date.now() - cached.timestamp < maxAge
    })

    const systemConfig = computed(() => state.systemConfig)

    // 功能切换
    const switchActiveFunction = (functionKey: string) => {
        state.activeFunction = functionKey
        // 自动加载对应数据
        loadFunctionData(functionKey)
    }

    const toggleNodeExpansion = (nodeKey: string) => {
        if (state.expandedNodes.has(nodeKey)) {
            state.expandedNodes.delete(nodeKey)
        } else {
            state.expandedNodes.add(nodeKey)
        }
    }

    // 数据加载方法
    const loadFunctionData = async (functionKey: string) => {
        const loadingKey = `load_${functionKey}`
        state.loadingStates[loadingKey] = true

        try {
            switch (functionKey) {
                case 'market-overview':
                    await loadMarketOverview()
                    break
                case 'trading-signals':
                    await loadTradingSignals()
                    break
                case 'trading-history':
                    await loadTradingHistory()
                    break
                case 'position-monitor':
                    await loadPositionMonitor()
                    break
                case 'performance-analysis':
                    await loadPerformanceAnalysis()
                    break
                case 'strategy-management':
                    await loadStrategyManagement()
                    break
                case 'risk-monitor':
                    await loadRiskMonitor()
                    break
                case 'monitoring-dashboard':
                    await loadMonitoringDashboard()
                    break
                default:
                    console.warn(`Unknown function key: ${functionKey}`)
            }
        } catch (error) {
            console.error(`Failed to load data for ${functionKey}:`, error)
        } finally {
            state.loadingStates[loadingKey] = false
        }
    }

    // 市场总览数据
    const loadMarketOverview = async () => {
        const cacheKey = 'market_overview'
        if (hasValidCache.value(cacheKey)) {
            state.marketOverview = state.cache.get(cacheKey)!.data
            return
        }

        const data = await tradingApiManager.getMarketOverview()
        state.marketOverview = data
        cacheData(cacheKey, data)
    }

    // 交易信号数据
    const loadTradingSignals = async (filters?: TradingFilters) => {
        const data = await tradingApiManager.getTradingSignals(filters)
        state.tradingSignals = data
    }

    // 交易历史数据
    const loadTradingHistory = async (filters?: TradingFilters) => {
        const historyFilters: HistoryFilters = filters ? {
            symbol: filters.symbol || '',
            type: filters.status || '',
            dateRange: filters.dateFrom && filters.dateTo ? [new Date(filters.dateFrom), new Date(filters.dateTo)] : [new Date(), new Date()],
            status: filters.status || ''
        } : { symbol: '', type: '', dateRange: [new Date(), new Date()], status: '' }
        const data = await tradingApiManager.getTradingHistory(historyFilters)
        state.tradingHistory = data
    }

    // 持仓监控数据
    const loadPositionMonitor = async () => {
        const data = await tradingApiManager.getPositionMonitor()
        state.positionMonitor = data
    }

    // 绩效分析数据
    const loadPerformanceAnalysis = async () => {
        const data = await tradingApiManager.getPerformanceAnalysis()
        state.performanceAnalysis = data
    }

    // 策略管理数据
    const loadStrategyManagement = async () => {
        const data = await tradingApiManager.getStrategyManagement()
        state.strategyManagement = data
    }

    // 风险监控数据
    const loadRiskMonitor = async () => {
        const data = await tradingApiManager.getRiskMonitor()
        state.riskMonitor = data
    }

    // 监控面板数据
    const loadMonitoringDashboard = async () => {
        const data = await tradingApiManager.getMonitoringDashboard()
        state.monitoringDashboard = data
    }

    // 系统设置数据
    const loadSystemSettings = async () => {
        const data = await tradingApiManager.getSystemSettings()
        state.systemSettings = data
    }

    // 缓存管理
    const cacheData = <T>(key: string, data: T, ttl: number = 300000): void => {
        state.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl
        } as CachedData<T>)
    }

    const getCachedData = <T>(key: string): T | null => {
        const cached = state.cache.get(key)
        if (!cached) return null

        if (Date.now() - cached.timestamp > cached.ttl) {
            state.cache.delete(key)
            return null
        }

        return cached.data
    }

    const clearCache = (key?: string) => {
        if (key) {
            state.cache.delete(key)
        } else {
            state.cache.clear()
        }
    }

    // 批量刷新
    const refreshAllData = async () => {
        state.loadingStates['refresh_all'] = true
        try {
            await tradingApiManager.refreshAllData()

            // 重新加载当前功能的数据
            await loadFunctionData(state.activeFunction)

            // 更新最后刷新时间
            state.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')
        } catch (error) {
            console.error('Failed to refresh all data:', error)
            throw error
        } finally {
            state.loadingStates['refresh_all'] = false
        }
    }

    // 系统健康检查
    const checkSystemHealth = async () => {
        try {
            const health = await tradingApiManager.getSystemHealth()
            state.systemHealth = health
            return health
        } catch (error) {
            console.error('Failed to check system health:', error)
            state.systemHealth = {
                api: 'degraded',
                data: 'degraded',
                monitoring: 'degraded',
                overall: 'degraded'
            }
            throw error
        }
    }

    // 实时更新设置
    const setupRealtimeUpdates = (updates: any[]) => {
        return tradingApiManager.setupRealtimeUpdates(updates)
    }

    // 初始化
    const initialize = async () => {
        await checkSystemHealth()
        await loadMarketOverview() // 默认加载市场概览
    }

    return {
        // 状态
        state,
        isLoading,
        systemConfig,

        // 方法
        switchActiveFunction,
        toggleNodeExpansion,
        loadFunctionData,
        refreshAllData,
        checkSystemHealth,
        setupRealtimeUpdates,
        initialize,

        // 缓存管理
        cacheData,
        getCachedData,
        clearCache,

        // 数据加载
        loadMarketOverview,
        loadTradingSignals,
        loadTradingHistory,
        loadPositionMonitor,
        loadPerformanceAnalysis,
        loadStrategyManagement,
        loadRiskMonitor,
        loadMonitoringDashboard,
        loadSystemSettings
    }
})
