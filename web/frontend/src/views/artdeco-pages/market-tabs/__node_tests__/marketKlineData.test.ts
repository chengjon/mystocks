import test from 'node:test'
import assert from 'node:assert/strict'

import { buildMarketKlineParams, extractKlineRows } from '../marketKlineData.ts'

test('buildMarketKlineParams uses stock_code for market kline requests', () => {
  assert.deepEqual(buildMarketKlineParams('000001'), {
    stock_code: '000001',
    period: 'daily',
    limit: 100,
  })
})

test('extractKlineRows supports exec-unwrapped array payload', () => {
  const rows = extractKlineRows([
    {
      date: '2026-03-13',
      open: 10,
      high: 12,
      low: 9,
      close: 11,
      volume: 1000,
    },
  ])

  assert.equal(rows.length, 1)
  assert.equal(rows[0]?.datetime, '2026-03-13')
  assert.equal(rows[0]?.close, 11)
})
