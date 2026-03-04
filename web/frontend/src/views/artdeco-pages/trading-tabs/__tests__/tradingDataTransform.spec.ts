import { describe, expect, it } from 'vitest'
import {
  extractPositionsPayload,
  extractTradesPayload,
  toTradingHistoryRows,
  toTradingPositionRows
} from '../tradingDataTransform'

describe('tradingDataTransform', () => {
  it('maps /v1/trade/positions payload to trading positions rows', () => {
    const payload = extractPositionsPayload({
      data: {
        positions: [
          {
            symbol: '600519.SH',
            symbol_name: '贵州茅台',
            quantity: 500,
            cost_price: 1650,
            current_price: 1750,
            market_value: 875000,
            profit_loss: 50000,
            profit_loss_percent: 6.06
          }
        ],
        total_market_value: 1025000
      }
    })

    expect(toTradingPositionRows(payload)).toEqual([
      {
        symbol: '600519.SH',
        name: '贵州茅台',
        shares: 500,
        avgCost: 1650,
        currentPrice: 1750,
        marketValue: 875000,
        pnl: 50000,
        pnlPercent: 6.06,
        positionPercent: 85.37
      }
    ])
  })

  it('maps /v1/trade/trades payload to trading history rows', () => {
    const payload = extractTradesPayload({
      data: {
        trades: [
          {
            trade_id: 'TRD001',
            symbol: '600519.SH',
            direction: 'buy',
            price: 1650,
            quantity: 500,
            amount: 825000,
            commission: 82.5,
            trade_time: '2026-03-03T10:00:00Z',
            trade_type: 'normal'
          }
        ]
      }
    })

    expect(toTradingHistoryRows(payload)).toEqual([
      {
        id: 'TRD001',
        time: '2026-03-03 10:00:00',
        symbol: '600519.SH',
        symbolName: '600519',
        type: 'buy',
        typeText: '买入',
        price: 1650,
        quantity: 500,
        amount: 825000,
        fee: 82.5,
        status: 'completed',
        statusText: '已成交'
      }
    ])
  })

  it('returns empty arrays for invalid payloads', () => {
    expect(toTradingPositionRows(extractPositionsPayload(null))).toEqual([])
    expect(toTradingHistoryRows(extractTradesPayload(undefined))).toEqual([])
  })
})
