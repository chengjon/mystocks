import { describe, expect, it } from 'vitest'
import { TradeAdapter } from '@/utils/trade-adapters'

describe('TradeAdapter utils', () => {
  it('keeps empty account payloads inside default view-model boundaries', () => {
    expect(TradeAdapter.toAccountOverviewVM(null)).toMatchObject({
      totalAssets: 0,
      availableCash: 0,
      totalMarketValue: 0,
      totalPositionValue: 0,
      todayPnL: 0,
      todayPnLPercent: '0.00%',
      totalPnL: 0,
      totalPnLPercent: '0.00%',
      currency: 'CNY',
      assetAllocation: []
    })
  })

  it('returns empty collections for invalid trade payload boundaries', () => {
    expect(TradeAdapter.toOrderVM(null)).toEqual([])
    expect(TradeAdapter.toPositionVM(undefined)).toEqual([])
    expect(TradeAdapter.toTradeHistoryVM({ items: [] })).toEqual([])
  })
})
