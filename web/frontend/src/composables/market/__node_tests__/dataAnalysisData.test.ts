import test from 'node:test'
import assert from 'node:assert/strict'

import {
  buildDataAnalysisStats,
  extractDataAnalysisIndicators,
  toDataAnalysisResults,
} from '../dataAnalysisData.ts'

test('extractDataAnalysisIndicators normalizes registry payload', () => {
  const rows = extractDataAnalysisIndicators({
    total_count: 2,
    indicators: [
      {
        abbreviation: 'SMA',
        chinese_name: '简单移动平均线',
        full_name: 'Simple Moving Average',
        category: 'trend',
        panel_type: 'overlay',
        description: '趋势跟踪',
        parameters: [{ name: 'timeperiod', default: 20 }],
      },
      {
        abbreviation: 'RSI',
        chinese_name: '相对强弱指数',
        full_name: 'Relative Strength Index',
        category: 'momentum',
        panel_type: 'oscillator',
        description: '动量参考',
        parameters: [{ name: 'timeperiod', default: 14 }],
      },
    ],
  })

  assert.equal(rows.length, 2)
  assert.deepEqual(rows[0], {
    id: 1,
    name: '简单移动平均线',
    key: 'sma',
    category: 'trend',
    categoryLabel: '趋势',
    type: '主图',
    description: '趋势跟踪',
    params: [{ name: 'timeperiod', default: 20 }],
  })
  assert.equal(rows[1]?.type, '副图')
})

test('buildDataAnalysisStats reflects indicator inventory and screening result counts', () => {
  const stats = buildDataAnalysisStats({
    indicators: [{ id: 1 }, { id: 2 }, { id: 3 }],
    stockUniverseSize: 8,
    qualifiedStocks: 3,
    previousQualifiedStocks: 1,
    screeningTimes: 4,
    screeningExecuted: true,
  })

  assert.deepEqual(stats, {
    availableIndicators: 3,
    customIndicators: 0,
    screenedStocks: 8,
    screeningTimes: 4,
    qualifiedStocks: 3,
    qualifiedChange: 2,
  })
})

test('buildDataAnalysisStats keeps screening counts at zero before the user runs screening', () => {
  const stats = buildDataAnalysisStats({
    indicators: [{ id: 1 }, { id: 2 }],
    stockUniverseSize: 8,
    qualifiedStocks: 0,
    previousQualifiedStocks: 0,
    screeningTimes: 0,
    screeningExecuted: false,
  })

  assert.deepEqual(stats, {
    availableIndicators: 2,
    customIndicators: 0,
    screenedStocks: 0,
    screeningTimes: 0,
    qualifiedStocks: 0,
    qualifiedChange: 0,
  })
})

test('toDataAnalysisResults adapts screener rows for ArtDeco table', () => {
  const rows = toDataAnalysisResults([
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

  assert.deepEqual(rows, [
    {
      symbol: '600519',
      name: '贵州茅台',
      price: 1820.5,
      change: 1.86,
      volume: 1000000,
      amount: 1820500000,
      pe: 28.3,
      marketCap: 2300000000000,
    },
  ])
})
