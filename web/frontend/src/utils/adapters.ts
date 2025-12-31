
/**
 * Data Transformation Adapters
 *
 * This module provides adapters to transform API response data (DTOs)
 * into ViewModels that UI components can use directly.
 */

import type {
  MarketOverviewResponse,
  FundFlowResponse,
  KLineDataResponse,
  IndexData,
  SectorData,
  FundFlowItem,
  KLinePoint,
  StockSearchResult
} from '@/api/types/generated-types'

// ViewModel interfaces for UI consumption
export interface MarketOverviewVM {
  indices: IndexItemVM[]
  sectors: SectorItemVM[]
  marketSentiment: 'bullish' | 'bearish' | 'neutral'
  totalVolume: string
  lastUpdate: number
}

export interface IndexItemVM {
  name: string
  current: number
  change: number
  changePercent: string
  trend: 'up' | 'down' | 'flat'
  volume: string
}

export interface SectorItemVM {
  name: string
  changePercent: string
  stockCount: number
  leaderStock: string
  leaderChange: string
}

export interface FundFlowChartPoint {
  date: string
  mainInflow: number
  mainOutflow: number
  netInflow: number
  timestamp: number
}

export interface KLineChartData {
  categoryData: string[]
  values: number[][]
  volumes: number[]
}

export interface StockSearchVM {
  symbol: string
  name: string
  market: string
  current: number
  changePercent: string
  trend: 'up' | 'down' | 'flat'
}

export class DataAdapter {
  /**
   * Convert Market Overview API response to ViewModel
   * Note: Handles actual API response format where indices use 'indices' not 'marketIndex'
   */
  static toMarketOverviewVM(data: MarketOverviewResponse): MarketOverviewVM {
    // Handle indices - API uses 'indices' field with IndexQuote type
    const indices = (data.indices || []).map((item: any) => ({
      name: item.indexName || item.name || '',
      current: item.currentPrice || item.current || 0,
      change: item.change || 0,
      changePercent: this.formatPercent(item.changePercent || 0),
      trend: this.getTrend(item.change || 0),
      volume: this.formatVolume(item.volume || 0)
    }))

    // Handle sectors - API uses 'hotSectors' with HotSector type
    const sectors = (data.hotSectors || []).map((item: any) => ({
      name: item.sectorName || '',
      changePercent: this.formatPercent(item.changePercent || 0),
      stockCount: item.stockCount || 0,
      leaderStock: item.leadingStock || item.leaderStock || '',
      leaderChange: this.formatPercent(0) // API doesn't provide leaderChange
    }))

    // Determine market sentiment based on index performance
    const avgChange = indices.length > 0
      ? indices.reduce((sum, idx) => sum + idx.change, 0) / indices.length
      : 0
    let marketSentiment: 'bullish' | 'bearish' | 'neutral' = 'neutral'
    if (avgChange > 0.5) marketSentiment = 'bullish'
    else if (avgChange < -0.5) marketSentiment = 'bearish'

    return {
      indices,
      sectors,
      marketSentiment,
      totalVolume: this.formatVolume(0), // API doesn't provide totalVolume
      lastUpdate: Date.now()
    }
  }

  /**
   * Convert Fund Flow API response to chart data
   * Note: API uses different field names - mainNetInflow instead of mainInflow
   */
  static toFundFlowChartData(data: FundFlowResponse): FundFlowChartPoint[] {
    // Handle different API response formats
    const items = (data as any).items || (data as any).fundFlow || []

    return items.map((item: any) => ({
      date: item.tradeDate || '',
      mainInflow: this.convertToWan(item.mainNetInflow || item.mainInflow || 0),
      mainOutflow: Math.abs(this.convertToWan(item.mainNetInflow || 0)),
      netInflow: this.convertToWan(item.mainNetInflow || 0),
      timestamp: item.tradeDate ? new Date(item.tradeDate).getTime() : Date.now()
    }))
  }

  /**
   * Convert K-Line API response to chart data
   * Note: Handles actual API response format
   */
  static toKLineChartData(data: KLineDataResponse): KLineChartData {
    // Handle different response formats
    const points = (data as any).points ||
      (data as any).data ||
      (data as any).candles || []

    return {
      categoryData: points.map((p: any) => p.date || p.tradeDate || p[0] || ''),
      values: points.map((p: any) => {
        if (Array.isArray(p)) {
          return [p[1] || 0, p[2] || 0, p[3] || 0, p[4] || 0] // open, close, low, high
        }
        return [
          p.open || 0,
          p.close || 0,
          p.low || 0,
          p.high || 0
        ]
      }),
      volumes: points.map((p: any) => {
        if (Array.isArray(p)) return p[5] || 0 // volume is 6th element
        return p.volume || 0
      })
    }
  }

  /**
   * Convert Stock Search results to ViewModel
   */
  static toStockSearchVM(data: StockSearchResult[]): StockSearchVM[] {
    return data.map((item) => ({
      symbol: item.symbol || '',
      name: item.name || '',
      market: item.market || '',
      current: item.current || 0,
      changePercent: this.formatPercent(item.changePercent || 0),
      trend: this.getTrend(item.change || 0)
    }))
  }

  // Utility methods
  private static formatPercent(value: number): string {
    return `${(value * 100).toFixed(2)}%`
  }

  private static formatVolume(value: number): string {
    if (value >= 100000000) {
      return `${(value / 100000000).toFixed(2)}亿`
    } else if (value >= 10000) {
      return `${(value / 10000).toFixed(2)}万`
    }
    return value.toString()
  }

  private static convertToWan(value: number): number {
    return Math.round(value / 10000 * 100) / 100
  }

  private static getTrend(change: number): 'up' | 'down' | 'flat' {
    if (change > 0) return 'up'
    if (change < 0) return 'down'
    return 'flat'
  }

  /**
   * Format price with currency symbol
   */
  static formatPrice(price: number, currency: string = '¥'): string {
    return `${currency}${price.toFixed(2)}`
  }

  /**
   * Format number with thousand separator
   */
  static formatNumber(num: number): string {
    return num.toLocaleString('zh-CN')
  }

  /**
   * Format timestamp to human readable date
   */
  static formatDate(timestamp: number | string): string {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

export default DataAdapter
