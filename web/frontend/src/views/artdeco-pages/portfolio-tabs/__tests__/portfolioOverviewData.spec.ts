import { describe, expect, it } from 'vitest'
import {
  extractTradePositionsPayload,
  toPortfolioOverviewData
} from '../portfolioOverviewData'

describe('portfolioOverviewData', () => {
  it('maps trade positions payload to portfolio overview data', () => {
    const payload = extractTradePositionsPayload({
      positions: [
        {
          symbol: '600519.SH',
          symbol_name: '贵州茅台',
          market_value: 875000,
          profit_loss_percent: 6.06
        },
        {
          symbol: '000858.SZ',
          symbol_name: '五粮液',
          market_value: 150000,
          profit_loss_percent: 3.45
        }
      ],
      total_market_value: 1025000,
      total_profit_loss: 55000,
      total_profit_loss_percent: 5.67
    })

    expect(toPortfolioOverviewData(payload)).toEqual({
      total_assets: 1025000,
      today_pnl: 55000,
      today_pnl_pct: 5.67,
      positions: [
        { symbol: '600519.SH', name: '贵州茅台', market_value: 875000, pnl_pct: 6.06 },
        { symbol: '000858.SZ', name: '五粮液', market_value: 150000, pnl_pct: 3.45 }
      ]
    })
  })

  it('falls back to derived totals when totals are missing', () => {
    const payload = extractTradePositionsPayload({
      data: {
        positions: [
          {
            symbol: '600000.SH',
            symbol_name: '浦发银行',
            market_value: '12000.5',
            profit_loss_percent: '-1.5'
          }
        ]
      }
    })

    expect(toPortfolioOverviewData(payload)).toEqual({
      total_assets: 12000.5,
      today_pnl: 0,
      today_pnl_pct: 0,
      positions: [{ symbol: '600000.SH', name: '浦发银行', market_value: 12000.5, pnl_pct: -1.5 }]
    })
  })

  it('returns empty portfolio when payload is invalid', () => {
    expect(toPortfolioOverviewData(extractTradePositionsPayload(null))).toEqual({
      total_assets: 0,
      today_pnl: 0,
      today_pnl_pct: 0,
      positions: []
    })
  })
})
