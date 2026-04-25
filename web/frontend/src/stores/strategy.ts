// Strategy Management Store - 标准化 Pinia API 模式
// 负责策略配置、回测结果、优化任务等策略相关数据

import { defineStore } from 'pinia'
import { reactive, watch } from 'vue'
import { PiniaStoreFactory } from '@/stores/storeFactory'
import { tradingApiManager } from '@/services/TradingApiManager'
import type { StrategyManagementData } from '@/services/TradingApiManager'

interface BacktestResult {
    id?: string
    strategyId?: string
    status?: 'pending' | 'running' | 'completed' | 'failed'
    result?: unknown
    error?: string
    startTime?: Date
    endTime?: Date
}

interface OptimizationTask {
    id?: string
    strategyId?: string
    status?: 'pending' | 'running' | 'completed' | 'failed'
    parameters?: Record<string, unknown>
    result?: unknown
    error?: string
    startTime?: Date
    endTime?: Date
}

interface StrategyState {
    strategyManagement: StrategyManagementData | null
    backtestResults: BacktestResult[]
    optimizationTasks: OptimizationTask[]
    lastUpdateTime: string
    loading: boolean
    error: string | null
    lastFetch: number | null
}

const useStrategyManagementApiStore = PiniaStoreFactory.createApiStore<StrategyManagementData>({
    id: 'strategy-management',
    endpoint: '/strategy/management',
    request: () => tradingApiManager.getStrategyManagement(),
    validate: (data: unknown): data is StrategyManagementData => {
        const value = data as Partial<StrategyManagementData> | null
        return !!value && Array.isArray(value.strategies) && Array.isArray(value.templates)
    },
    initialData: {
        strategies: [],
        templates: []
    }
})

export const useStrategyStore = defineStore('strategy', () => {
    const state = reactive<StrategyState>({
        strategyManagement: null,
        backtestResults: [],
        optimizationTasks: [],
        lastUpdateTime: new Date().toLocaleTimeString('zh-CN'),
        loading: false,
        error: null,
        lastFetch: null
    })
    const strategyManagementStore = useStrategyManagementApiStore()

    watch(
        () => strategyManagementStore.data,
        (value) => {
            state.strategyManagement = value
        },
        { immediate: true }
    )

    watch(
        () => strategyManagementStore.loading,
        (value) => {
            state.loading = value
        },
        { immediate: true }
    )

    watch(
        () => strategyManagementStore.error,
        (value) => {
            state.error = value
        },
        { immediate: true }
    )

    watch(
        () => strategyManagementStore.lastFetch,
        (value) => {
            state.lastFetch = value
            if (value) {
                state.lastUpdateTime = new Date(value).toLocaleTimeString('zh-CN')
            }
        },
        { immediate: true }
    )

    const loadStrategyManagement = async () => {
        await strategyManagementStore.fetch()
    }

    const addBacktestResult = (result: BacktestResult) => {
        state.backtestResults.push(result)
    }

    const addOptimizationTask = (task: OptimizationTask) => {
        state.optimizationTasks.push(task)
    }

    const clearBacktestResults = () => {
        state.backtestResults = []
    }

    const clearOptimizationTasks = () => {
        state.optimizationTasks = []
    }

    return {
        state,
        strategyManagementStore,
        loadStrategyManagement,
        addBacktestResult,
        addOptimizationTask,
        clearBacktestResults,
        clearOptimizationTasks
    }
})
