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

  it('parses finite numeric strings across trade adapter view models', () => {
    const account = TradeAdapter.toAccountOverviewVM({
      totalAssets: '1000.5',
      availableCash: '400.25',
      totalMarketValue: '600.25',
      totalPositionValue: '600.25',
      todayPnL: '10.5',
      totalPnL: '25',
      assetAllocation: [
        { category: 'stock', value: '600.25', percentage: '60' }
      ]
    })

    expect(account).toMatchObject({
      totalAssets: 1000.5,
      availableCash: 400.25,
      totalMarketValue: 600.25,
      totalPositionValue: 600.25,
      todayPnL: 10.5,
      todayPnLPercent: '1.06%',
      totalPnL: 25,
      totalPnLPercent: '2.56%'
    })
    expect(account.assetAllocation[0]).toMatchObject({
      value: 600.25,
      percentage: '60.00%'
    })

    expect(TradeAdapter.toOrderVM([{
      order_id: 'o1',
      quantity: '100',
      price: '12.34',
      amount: '1234',
      filled_quantity: '40',
      filled_amount: '493.6',
      average_price: '12.34'
    }])[0]).toMatchObject({
      quantity: 100,
      price: 12.34,
      amount: 1234,
      filledQuantity: 40,
      filledAmount: 493.6,
      averagePrice: 12.34
    })

    expect(TradeAdapter.toPositionVM([{
      symbol: '600000',
      quantity: '100',
      avgPrice: '10',
      currentPrice: '12',
      costBasis: '1000',
      realizedPnL: '50',
      marketValue: '1200',
      marginUsed: '200',
      marginAvailable: '800'
    }])[0]).toMatchObject({
      quantity: 100,
      avgPrice: 10,
      currentPrice: 12,
      unrealizedPnL: 200,
      realizedPnL: 50,
      positionPnL: 250,
      marketValue: 1200,
      marginUsed: 200,
      marginAvailable: 800
    })

    expect(TradeAdapter.toTradeHistoryVM([{
      trade_id: 't1',
      trade_date: '2026-06-09',
      quantity: '50',
      price: '12.5',
      amount: '625',
      commission: '1.5'
    }])[0]).toMatchObject({
      totalTrades: 1,
      totalVolume: 625,
      totalCommission: 1.5
    })
  })

  it('rejects formatted and non-finite numeric strings at trade boundaries', () => {
    const account = TradeAdapter.toAccountOverviewVM({
      totalAssets: '',
      availableCash: '1,000',
      totalMarketValue: '12%',
      totalPositionValue: 'Infinity',
      todayPnL: 'NaN',
      totalPnL: 'not-a-number',
      assetAllocation: [
        { category: 'stock', value: '1,234', percentage: '12%' }
      ]
    })

    expect(account).toMatchObject({
      totalAssets: 0,
      availableCash: 0,
      totalMarketValue: 0,
      totalPositionValue: 0,
      todayPnL: 0,
      todayPnLPercent: '0.00%',
      totalPnL: 0,
      totalPnLPercent: '0.00%'
    })
    expect(account.assetAllocation[0]).toMatchObject({
      value: 0,
      percentage: '0.00%'
    })

    expect(TradeAdapter.toOrderVM([{
      quantity: '0x10',
      price: '12%',
      amount: '1,234',
      filled_quantity: 'Infinity',
      filled_amount: 'NaN',
      average_price: ''
    }])[0]).toMatchObject({
      quantity: 0,
      price: 0,
      amount: 0,
      filledQuantity: 0,
      filledAmount: 0,
      averagePrice: 0
    })
  })
})
