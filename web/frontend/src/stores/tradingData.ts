// Trading Data Store - 专注于交易数据管理
// 负责交易信号、历史、持仓监控、绩效分析等交易相关数据

import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { tradingApiManager } from '@/services/TradingApiManager'
import type {
    TradingSignals,
    TradingHistory,
    PositionMonitorData,
    PerformanceAnalysis,
    HistoryFilters
} from '@/services/TradingApiManager'

interface TradingFilters {
    symbol?: string
    dateFrom?: string
    dateTo?: string
    status?: string
    [key: string]: any
}

interface TradingDataState {
    tradingSignals: TradingSignals | null
    tradingHistory: TradingHistory | null
    positionMonitor: PositionMonitorData | null
    performanceAnalysis: PerformanceAnalysis | null
    lastUpdateTime: string
}

export const useTradingDataStore = defineStore('tradingData', () => {
    const state = reactive<TradingDataState>({
        tradingSignals: null,
        tradingHistory: null,
        positionMonitor: null,
        performanceAnalysis: null,
        lastUpdateTime: new Date().toLocaleTimeString('zh-CN')
    })

    const loadTradingSignals = async (filters?: TradingFilters) => {
        const data = await tradingApiManager.getTradingSignals(filters)
        state.tradingSignals = data
        state.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')
    }

    const loadTradingHistory = async (filters: HistoryFilters = {}) => {
        const data = await tradingApiManager.getTradingHistory(filters)
        state.tradingHistory = data
        state.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')
    }

    const loadPositionMonitor = async () => {
        const data = await tradingApiManager.getPositionMonitor()
        state.positionMonitor = data
        state.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')
    }

    const loadPerformanceAnalysis = async () => {
        const data = await tradingApiManager.getPerformanceAnalysis()
        state.performanceAnalysis = data
        state.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')
    }

    return {
        state,
        loadTradingSignals,
        loadTradingHistory,
        loadPositionMonitor,
        loadPerformanceAnalysis
    }
})