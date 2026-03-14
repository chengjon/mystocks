import test from 'node:test'
import assert from 'node:assert/strict'

import { toBoardRows, toRotationRows } from '../industryAnalysisData.ts'

test('toBoardRows supports v2 sector fund-flow fields', () => {
  const rows = toBoardRows([
    {
      rank: 1,
      sector_name: '证券',
      change_percent: 2.92,
      main_net_inflow: 3441226240,
      main_net_inflow_rate: 7.58,
    } as never,
  ])

  assert.equal(rows.length, 1)
  assert.equal(rows[0]?.name, '证券')
  assert.equal(rows[0]?.change, '+2.92%')
  assert.equal(rows[0]?.turnover, 34.41)
  assert.equal(rows[0]?.netInflow, '+7.58%')
})

test('toRotationRows uses board turnover as flow amount', () => {
  const rows = toRotationRows([
    { rank: 1, name: '证券', change: '+2.92%', turnover: 34.41, netInflow: '+7.58%' },
  ])

  assert.equal(rows.length, 1)
  assert.equal(rows[0]?.flow, 34.41)
})
