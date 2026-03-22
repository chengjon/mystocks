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
          rise_fall_count: {
            rise: 2000,
            fall: 1500,
            flat: 1500
          },
          timestamp: '2025-01-02T09:30:00Z'
        }
      }

      const result = MarketAdapter.adaptMarketOverview(mockResponse)

      expect(result).toBeDefined()
      expect(result.price_distribution.total_stocks).toBe(5000)
      expect(result.price_distribution.up_stocks).toBe(2000)
      expect(result.price_distribution.down_stocks).toBe(1500)
      expect(result.timestamp).toBe('2025-01-02T09:30:00Z')
      expect(result.last_update).toBe('2025-01-02T09:30:00.000Z')
    })

    it('should handle empty market stats', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: {
          rise_fall_count: {}
        }
      }

      const result = MarketAdapter.adaptMarketOverview(mockResponse)

      expect(result).toBeDefined()
      expect(result.price_distribution.total_stocks).toBe(0)
    })

    it('should use default values for missing fields', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: {}
      }

      const result = MarketAdapter.adaptMarketOverview(mockResponse)

      expect(result).toBeDefined()
      expect(result.price_distribution).toBeDefined()
      expect(result.price_distribution.total_stocks).toBe(0)
    })
  })

  describe('adaptFundFlow', () => {
    it('should transform fund flow API response', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: {
          fund_flow: [
            {
              trade_date: '2025-01-02',
              super_large_net_inflow: 800000000,
              large_net_inflow: 300000000,
              medium_net_inflow: 200000000,
              small_net_inflow: 100000000
            }
          ]
        }
      }

      const result = MarketAdapter.adaptFundFlow(mockResponse)

      expect(result).toBeDefined()
      expect(result).toHaveLength(1)
      expect(result[0].date).toBe('2025-01-02')
      expect(result[0].main_force.inflow).toBe(800000000)
      expect(result[0].large_orders.inflow).toBe(300000000)
      expect(result[0].total_net_flow).toBe(1400000000)
    })

    it('should calculate totals correctly', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: {
          fund_flow: [
            {
              trade_date: '2025-01-02',
              super_large_net_inflow: 500000000,
              large_net_inflow: 200000000,
              medium_net_inflow: 100000000,
              small_net_inflow: 200000000
            }
          ]
        }
      }

      const result = MarketAdapter.adaptFundFlow(mockResponse)

      expect(result).toBeDefined()
      expect(result[0].total_net_flow).toBe(1000000000)
    })

    it('should handle empty items', () => {
      const mockResponse = {
        success: true,
        message: 'success',
        data: { fund_flow: [] }
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
      expect(result.values[0]).toEqual({
        open: 3000.00,
        close: 3010.00,
        low: 2990.00,
        high: 3020.00,
        volume: 50000000
      })
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
      market_status: 'sideways',
      market_phase: 'accumulation',
      indices: {
        shanghai: {
          code: '000001',
          name: '上证指数',
          current_price: 3000,
          change_amount: 10,
          change_percent: 0.3,
          volume: 1000000,
          amount: 10000000,
          open: 2990,
          high: 3010,
          low: 2980,
          close: 3000,
          prev_close: 2990
        },
        shenzhen: {
          code: '399001',
          name: '深证成指',
          current_price: 10000,
          change_amount: 20,
          change_percent: 0.2,
          volume: 1000000,
          amount: 10000000,
          open: 9980,
          high: 10020,
          low: 9970,
          close: 10000,
          prev_close: 9980
        },
        chiNext: {
          code: '399006',
          name: '创业板指',
          current_price: 2000,
          change_amount: 5,
          change_percent: 0.25,
          volume: 1000000,
          amount: 10000000,
          open: 1990,
          high: 2010,
          low: 1985,
          close: 2000,
          prev_close: 1995
        }
      },
      sentiment: {
        advance_decline_ratio: 1.2,
        up_down_volume_ratio: 1.1,
        new_highs_new_lows_ratio: 1.0
      },
      turnover: {
        total_value: 100000000,
        total_volume: 1000000,
        average_price: 10,
        turnover_rate: 1.2
      },
      price_distribution: {
        up_stocks: 2000,
        down_stocks: 1500,
        flat_stocks: 1500,
        limit_up: 10,
        limit_down: 5,
        total_stocks: 5000
      },
      sector_performance: [],
      hot_concepts: [],
      capital_flow: {
        northbound: { inflow: 0, outflow: 0, net_flow: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 }, net_flow_ratio: 0, large_order_ratio: 0 },
        southbound: { inflow: 0, outflow: 0, net_flow: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 }, net_flow_ratio: 0, large_order_ratio: 0 },
        institutional: { inflow: 0, outflow: 0, net_flow: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 }, net_flow_ratio: 0, large_order_ratio: 0 },
        retail: { inflow: 0, outflow: 0, net_flow: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 }, net_flow_ratio: 0, large_order_ratio: 0 },
        foreign: { inflow: 0, outflow: 0, net_flow: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 }, net_flow_ratio: 0, large_order_ratio: 0 }
      },
      technical_summary: {
        market_breadth: 0.5,
        momentum_index: 0.3
      },
      timestamp: new Date().toISOString(),
      last_update: new Date().toISOString(),
      market_session: 'open'
    }

    expect(MarketAdapter.validateMarketOverview(validData)).toBe(true)
  })

  it('should return false for missing marketStats', () => {
    const invalidData = {
      market_status: 'sideways',
      market_phase: 'accumulation',
      indices: undefined
    } as MarketOverviewVM

    expect(MarketAdapter.validateMarketOverview(invalidData)).toBe(false)
  })

  it('should return false for negative totalStocks', () => {
    const invalidData: MarketOverviewVM = {
      market_status: 'sideways',
      market_phase: 'accumulation',
      indices: {
        shanghai: {
          code: '000001',
          name: '上证指数',
          current_price: 3000,
          change_amount: 0,
          change_percent: 0,
          volume: 0,
          amount: 0,
          open: 3000,
          high: 3000,
          low: 3000,
          close: 3000,
          prev_close: 3000
        },
        shenzhen: {
          code: '399001',
          name: '深证成指',
          current_price: 10000,
          change_amount: 0,
          change_percent: 0,
          volume: 0,
          amount: 0,
          open: 10000,
          high: 10000,
          low: 10000,
          close: 10000,
          prev_close: 10000
        },
        chiNext: {
          code: '399006',
          name: '创业板指',
          current_price: 2000,
          change_amount: 0,
          change_percent: 0,
          volume: 0,
          amount: 0,
          open: 2000,
          high: 2000,
          low: 2000,
          close: 2000,
          prev_close: 2000
        }
      },
      sentiment: {
        advance_decline_ratio: 1,
        up_down_volume_ratio: 1,
        new_highs_new_lows_ratio: 1
      },
      turnover: {
        total_value: 0,
        total_volume: 0,
        average_price: 0,
        turnover_rate: 0
      },
      price_distribution: {
        up_stocks: 0,
        down_stocks: 0,
        flat_stocks: 0,
        limit_up: 0,
        limit_down: 0,
        total_stocks: -100
      },
      sector_performance: [],
      hot_concepts: [],
      capital_flow: {
        northbound: { inflow: 0, outflow: 0, net_flow: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 }, net_flow_ratio: 0, large_order_ratio: 0 },
        southbound: { inflow: 0, outflow: 0, net_flow: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 }, net_flow_ratio: 0, large_order_ratio: 0 },
        institutional: { inflow: 0, outflow: 0, net_flow: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 }, net_flow_ratio: 0, large_order_ratio: 0 },
        retail: { inflow: 0, outflow: 0, net_flow: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 }, net_flow_ratio: 0, large_order_ratio: 0 },
        foreign: { inflow: 0, outflow: 0, net_flow: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 }, net_flow_ratio: 0, large_order_ratio: 0 }
      },
      technical_summary: {
        market_breadth: 0,
        momentum_index: 0
      },
      timestamp: new Date().toISOString(),
      last_update: new Date().toISOString(),
      market_session: 'open'
    }

    expect(MarketAdapter.validateMarketOverview(invalidData)).toBe(false)
  })
})
