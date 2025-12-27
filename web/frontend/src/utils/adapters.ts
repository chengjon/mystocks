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
   */
  static toMarketOverviewVM(data: MarketOverviewResponse): MarketOverviewVM {
    const indices = data.marketIndex?.map((item: IndexData) => ({
      name: item.name || '',
      current: item.current || 0,
      change: item.change || 0,
      changePercent: this.formatPercent(item.changePercent || 0),
      trend: this.getTrend(item.change || 0),
      volume: this.formatVolume(item.volume || 0)
    })) || []

    const sectors = data.hotSectors?.map((item: SectorData) => ({
      name: item.sectorName || '',
      changePercent: this.formatPercent(item.changePercent || 0),
      stockCount: item.stockCount || 0,
      leaderStock: item.leaderStock || '',
      leaderChange: this.formatPercent(item.leaderChange || 0)
    })) || []

    // Determine market sentiment based on index performance
    const avgChange = indices.reduce((sum, idx) => sum + idx.change, 0) / indices.length
    let marketSentiment: 'bullish' | 'bearish' | 'neutral' = 'neutral'
    if (avgChange > 0.5) marketSentiment = 'bullish'
    else if (avgChange < -0.5) marketSentiment = 'bearish'

    return {
      indices,
      sectors,
      marketSentiment,
      totalVolume: this.formatVolume(data.totalVolume || 0),
      lastUpdate: Date.now()
    }
  }

  /**
   * Convert Fund Flow API response to chart data
   */
  static toFundFlowChartData(data: FundFlowResponse): FundFlowChartPoint[] {
    return data.items?.map((item: FundFlowItem) => ({
      date: item.tradeDate || '',
      mainInflow: this.convertToWan(item.mainInflow || 0),
      mainOutflow: Math.abs(this.convertToWan(item.mainOutflow || 0)),
      netInflow: this.convertToWan(item.netInflow || 0),
      timestamp: new Date(item.tradeDate || '').getTime()
    })) || []
  }

  /**
   * Convert K-Line API response to chart data
   */
  static toKLineChartData(data: KLineDataResponse): KLineChartData {
    const points = data.points || []

    return {
      categoryData: points.map((p: KLinePoint) => p.date || ''),
      values: points.map((p: KLinePoint) => [
        p.open || 0,
        p.close || 0,
        p.low || 0,
        p.high || 0
      ]),
      volumes: points.map((p: KLinePoint) => p.volume || 0)
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
