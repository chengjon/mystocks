// Strategy Management Store - 专注于策略管理
// 负责策略配置、回测结果、优化任务等策略相关数据

import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { tradingApiManager } from '@/services/TradingApiManager'
import type { StrategyManagementData } from '@/services/TradingApiManager'

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

interface StrategyState {
    strategyManagement: StrategyManagementData | null
    backtestResults: BacktestResult[]
    optimizationTasks: OptimizationTask[]
    lastUpdateTime: string
}

export const useStrategyStore = defineStore('strategy', () => {
    const state = reactive<StrategyState>({
        strategyManagement: null,
        backtestResults: [],
        optimizationTasks: [],
        lastUpdateTime: new Date().toLocaleTimeString('zh-CN')
    })

    const loadStrategyManagement = async () => {
        const data = await tradingApiManager.getStrategyManagement()
        state.strategyManagement = data
        state.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')
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
        loadStrategyManagement,
        addBacktestResult,
        addOptimizationTask,
        clearBacktestResults,
        clearOptimizationTasks
    }
})