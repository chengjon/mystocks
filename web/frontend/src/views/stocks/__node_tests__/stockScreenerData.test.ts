import test from 'node:test'
import assert from 'node:assert/strict'

import {
  extractStockScreenerRows,
  filterStockScreenerRows,
  resolveStocksBasicEndpoint,
} from '../stockScreenerData.ts'

test('extractStockScreenerRows normalizes stocks basic payload', () => {
  const rows = extractStockScreenerRows({
    success: true,
    data: [
      {
        symbol: '600519',
        name: '贵州茅台',
        price: 1820.5,
        change_pct: 1.86,
        volume: 1000000,
        turnover: 1820500000,
        pe: 28.3,
        market_cap: 2300000000000,
      },
    ],
  })

  assert.deepEqual(rows, [
    {
      symbol: '600519',
      name: '贵州茅台',
      price: 1820.5,
      changePercent: 1.86,
      volume: 1000000,
      amount: 1820500000,
      pe: 28.3,
      marketCap: 2300000000000,
    },
  ])
})

test('filterStockScreenerRows applies price and gainer filters', () => {
  const rows = [
    {
      symbol: '600519',
      name: '贵州茅台',
      price: 1820.5,
      changePercent: 1.86,
      volume: 1000000,
      amount: 1820500000,
      pe: 28.3,
      marketCap: 2300000000000,
    },
    {
      symbol: '000001',
      name: '平安银行',
      price: 12.8,
      changePercent: -0.52,
      volume: 15000000,
      amount: 192000000,
      pe: 8.5,
      marketCap: 232000000000,
    },
  ]

  const filtered = filterStockScreenerRows(rows, {
    priceMin: 10,
    priceMax: 100,
    peMin: undefined,
    peMax: undefined,
    volumeMin: undefined,
    volumeMax: undefined,
    amountMin: undefined,
    amountMax: undefined,
    changeType: 'negative',
    changePercentMin: undefined,
    changePercentMax: undefined,
    marketCapRange: 'small',
  })

  assert.deepEqual(filtered, [])

  const negativeRows = filterStockScreenerRows(rows, {
    priceMin: 10,
    priceMax: 20,
    peMin: undefined,
    peMax: undefined,
    volumeMin: undefined,
    volumeMax: undefined,
    amountMin: undefined,
    amountMax: undefined,
    changeType: 'negative',
    changePercentMin: -2,
    changePercentMax: 0,
    marketCapRange: 'any',
  })

  assert.deepEqual(negativeRows, [rows[1]])
})

test('resolveStocksBasicEndpoint supports both host and proxy api bases', () => {
  assert.equal(resolveStocksBasicEndpoint('/api'), '/api/v1/data/stocks/basic')
  assert.equal(resolveStocksBasicEndpoint('http://localhost:8888'), 'http://localhost:8888/api/v1/data/stocks/basic')
})
