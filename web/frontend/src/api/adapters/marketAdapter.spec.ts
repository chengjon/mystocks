/**
 * MarketAdapter Unit Tests
 *
 * Tests data transformation between API responses and frontend models.
 */

import { describe, it, expect } from 'vitest'
import { MarketAdapter } from './marketAdapter'
import type { MarketOverviewVM, FundFlowChartPoint } from '../types/market'

describe('MarketAdapter', () => {
  describe('adaptMarketOverview', () => {
    it('should transform API response to ViewModel', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: {
          marketStats: {
            totalStocks: 5000,
            risingStocks: 2000,
            fallingStocks: 1500,
            avgChangePercent: 0.5
          },
          topEtfs: [
            {
              symbol: '510300.SH',
              name: '沪深300ETF',
              latestPrice: 5.5,
              changePercent: 1.2,
              volume: 10000000
            }
          ],
          chipRaces: [],
          longHuBang: [],
          timestamp: Date.now()
        }
      }

      const result = MarketAdapter.adaptMarketOverview(mockResponse)

      expect(result).toBeDefined()
      expect(result.marketStats.totalStocks).toBe(5000)
      expect(result.marketStats.risingStocks).toBe(2000)
      expect(result.marketStats.avgChangePercent).toBe(0.5)
      expect(result.topEtfs).toHaveLength(1)
      expect(result.topEtfs[0].symbol).toBe('510300.SH')
    })

    it('should handle empty market stats', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: {
          marketStats: {},
          topEtfs: [],
          chipRaces: [],
          longHuBang: []
        }
      }

      const result = MarketAdapter.adaptMarketOverview(mockResponse)

      expect(result).toBeDefined()
      expect(result.marketStats.totalStocks).toBe(0)
      expect(result.topEtfs).toHaveLength(0)
    })

    it('should use default values for missing fields', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: {}
      }

      const result = MarketAdapter.adaptMarketOverview(mockResponse)

      expect(result).toBeDefined()
      expect(result.marketStats).toBeDefined()
      expect(result.marketStats.totalStocks).toBe(0)
    })
  })

  describe('adaptFundFlow', () => {
    it('should transform fund flow API response', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: {
          fundFlow: [
            {
              tradeDate: '2025-01-02',
              mainNetInflow: 1500000000,
              superLargeNetInflow: 800000000,
              largeNetInflow: 300000000
            }
          ]
        }
      }

      const result = MarketAdapter.adaptFundFlow(mockResponse)

      expect(result).toBeDefined()
      expect(result).toHaveLength(1)
      expect(result[0].date).toBe('2025-01-02')
      expect(result[0].mainInflow).toBe(800000000)
      expect(result[0].mainOutflow).toBe(300000000)
    })

    it('should calculate totals correctly', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: {
          fundFlow: [
            {
              tradeDate: '2025-01-02',
              mainNetInflow: 1000000000,
              superLargeNetInflow: 500000000,
              largeNetInflow: 200000000
            }
          ]
        }
      }

      const result = MarketAdapter.adaptFundFlow(mockResponse)

      expect(result).toBeDefined()
      expect(result[0].netInflow).toBe(1000000000)
    })

    it('should handle empty items', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: { fundFlow: [] }
      }

      const result = MarketAdapter.adaptFundFlow(mockResponse)

      expect(result).toHaveLength(0)
    })
  })

  describe('adaptKLineData', () => {
    it('should transform K-line API response', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: {
          symbol: '000001.SH',
          period: '1d',
          data: [
            {
              datetime: '2025-01-02',
              open: 3000.00,
              close: 3010.00,
              low: 2990.00,
              high: 3020.00,
              volume: 50000000
            }
          ],
          count: 1
        }
      }

      const result = MarketAdapter.adaptKLineData(mockResponse)

      expect(result).toBeDefined()
      expect(result.categoryData).toHaveLength(1)
      expect(result.categoryData[0]).toBe('2025-01-02')
      expect(result.values).toHaveLength(1)
      expect(result.values[0]).toEqual([3000.00, 3010.00, 2990.00, 3020.00])
      expect(result.volumes).toEqual([50000000])
    })

    it('should handle empty candles', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: {
          symbol: '000001.SH',
          period: '1d',
          data: [],
          count: 0
        }
      }

      const result = MarketAdapter.adaptKLineData(mockResponse)

      expect(result).toBeDefined()
      expect(result.categoryData).toHaveLength(0)
      expect(result.values).toHaveLength(0)
      expect(result.volumes).toHaveLength(0)
    })

    it('should use default values for missing fields', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: {}
      }

      const result = MarketAdapter.adaptKLineData(mockResponse)

      expect(result).toBeDefined()
      expect(result.categoryData).toEqual([])
      expect(result.values).toEqual([])
      expect(result.volumes).toEqual([])
    })
  })
})

describe('validateMarketOverview', () => {
  it('should return true for valid data', () => {
    const validData: MarketOverviewVM = {
      marketStats: {
        totalStocks: 5000,
        risingStocks: 2000,
        fallingStocks: 1500,
        avgChangePercent: 0.5
      },
      topEtfs: [],
      chipRaces: [],
      longHuBang: [],
      lastUpdate: new Date()
    }

    expect(MarketAdapter.validateMarketOverview(validData)).toBe(true)
  })

  it('should return false for missing marketStats', () => {
    const invalidData = {
      topEtfs: [],
      chipRaces: [],
      longHuBang: [],
      lastUpdate: new Date()
    } as MarketOverviewVM

    expect(MarketAdapter.validateMarketOverview(invalidData)).toBe(false)
  })

  it('should return false for negative totalStocks', () => {
    const invalidData: MarketOverviewVM = {
      marketStats: {
        totalStocks: -100,
        risingStocks: 0,
        fallingStocks: 0,
        avgChangePercent: 0
      },
      topEtfs: [],
      chipRaces: [],
      longHuBang: [],
      lastUpdate: new Date()
    }

    expect(MarketAdapter.validateMarketOverview(invalidData)).toBe(false)
  })
})
