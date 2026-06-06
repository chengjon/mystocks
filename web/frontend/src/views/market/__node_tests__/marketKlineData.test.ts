import test from 'node:test'
import assert from 'node:assert/strict'

import { buildMarketKlineParams, extractKlineRows, toMarketKlineDataPoints } from '../marketKlineData.ts'

test('buildMarketKlineParams uses stock_code for market kline requests', () => {
  assert.deepEqual(buildMarketKlineParams('000001'), {
    stock_code: '000001',
    period: '1d',
    limit: 100,
  })
})

test('buildMarketKlineParams accepts explicit selector periods for market kline requests', () => {
  assert.deepEqual(buildMarketKlineParams('000001', '1w'), {
    stock_code: '000001',
    period: '1w',
    limit: 100,
  })
})

test('buildMarketKlineParams can add a refresh sequence to force observable refresh requests', () => {
  assert.deepEqual(buildMarketKlineParams('000001', '1d', 2), {
    stock_code: '000001',
    period: '1d',
    limit: 100,
    refresh_seq: 2,
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

test('toMarketKlineDataPoints maps table rows into chart points', () => {
  const points = toMarketKlineDataPoints([
    {
      datetime: '2026-04-03 15:00:00',
      open: 101,
      high: 106,
      low: 99,
      close: 104,
      volume: 560000,
    },
  ])

  assert.equal(points.length, 1)
  assert.equal(points[0]?.open, 101)
  assert.equal(points[0]?.close, 104)
  assert.equal(points[0]?.volume, 560000)
  assert.equal(typeof points[0]?.timestamp, 'number')
})
