/**
 * Domain: Market Overview & Analysis (Simple API Wrapper)
 *
 * Provides lightweight market data access via the baseStore template pattern.
 * Responsible for: market overview, market analysis (technical/capital_flow/longhu_bang).
 * Consumers: overview widgets, simple dashboard cards.
 *
 * For enhanced market data with IndexedDB caching, offline support,
 * and web worker integration, see marketData.ts.
 */

// Market Data Store - 基于标准模板的市场数据管理
// 使用统一的Store模式和API调用规范

import { createBaseStore } from './baseStore'
import { tradingApiManager } from '@/services/TradingApiManager'
import type { MarketOverview } from '@/services/TradingApiManager'

interface MarketAnalysis {
  trend?: string
  sentiment?: number
  volatility?: number
  volume?: number
  lastUpdate?: string
  lastUpdateTime?: string
  [key: string]: unknown
}

interface _MarketData {
  marketOverview: MarketOverview | null
  marketAnalysis: MarketAnalysis | null
  lastUpdateTime?: string
}

// 使用标准Store模板
export const useMarketStore = createBaseStore('market', {
  marketOverview: null,
  marketAnalysis: null
})

// 扩展市场特定的Actions
export const useMarketStoreExtended = () => {
  const baseStore = useMarketStore()

  // 获取市场概览
  const fetchOverview = async (forceRefresh = false) => {
    return baseStore.executeApiCall(
      () => tradingApiManager.getMarketOverview(),
      {
        cacheKey: 'market-overview',
        forceRefresh,
        errorContext: 'Market Overview'
      }
    ).then(result => {
      // 更新最后更新时间（仅当result中有时）
      if (baseStore.state.data && result?.lastUpdate) {
        ;(baseStore.state.data as _MarketData).lastUpdateTime = result.lastUpdate
      }
      return result
    })
  }

  // 获取市场分析
  const fetchAnalysis = async (type: 'technical' | 'capital_flow' | 'longhu_bang' = 'technical', forceRefresh = false) => {
    return baseStore.executeApiCall(
      () => tradingApiManager.getMarketAnalysis(type),
      {
        cacheKey: `market-analysis-${type}`,
        forceRefresh,
        errorContext: 'Market Analysis'
      }
    ).then(result => {
      // 更新最后更新时间
      const resultData = result as MarketAnalysis | null
      if (baseStore.state.data && resultData?.lastUpdateTime) {
        ;(baseStore.state.data as _MarketData).lastUpdateTime = resultData.lastUpdateTime
      }
      return result
    })
  }

  // 刷新所有数据
  const refresh = async () => {
    await Promise.all([
      fetchOverview(true),
      fetchAnalysis('technical', true)
    ])
  }

  return {
    ...baseStore,
    fetchOverview,
    fetchAnalysis,
    refresh
  }
}
