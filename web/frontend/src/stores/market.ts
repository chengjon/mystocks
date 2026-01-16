// Market Data Store - 专注于市场数据管理
// 负责市场总览、市场分析等市场相关数据

import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { tradingApiManager } from '@/services/TradingApiManager'
import type { MarketOverview } from '@/services/TradingApiManager'
import { validateMarketState, validateInDevelopment, MarketStateSchema } from '@/utils/validation'

interface MarketAnalysis {
    trend?: string
    sentiment?: number
    volatility?: number
    volume?: number
    [key: string]: any
}

interface MarketState {
    marketOverview: MarketOverview | null
    marketAnalysis: MarketAnalysis | null
    lastUpdateTime: string
}

export const useMarketStore = defineStore('market', () => {
    const state = reactive<MarketState>({
        marketOverview: null,
        marketAnalysis: null,
        lastUpdateTime: new Date().toLocaleTimeString('zh-CN')
    })

    const loadMarketOverview = async () => {
        const data = await tradingApiManager.getMarketOverview()
        state.marketOverview = data
        state.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')

        // 运行时验证
        validateInDevelopment(state, MarketStateSchema, 'MarketStore.loadMarketOverview')
    }

    const loadMarketAnalysis = async () => {
        // 假设有一个获取市场分析的API
        // const data = await tradingApiManager.getMarketAnalysis()
        // state.marketAnalysis = data
    }

    return {
        state,
        loadMarketOverview,
        loadMarketAnalysis
    }
})