import test from 'node:test'
import assert from 'node:assert/strict'

import { buildConceptRequest, extractConceptRows } from '../marketConceptData.ts'

test('buildConceptRequest targets sector fund-flow concept data', () => {
  assert.deepEqual(buildConceptRequest(), {
    path: '/v2/market/sector/fund-flow',
    params: {
      sector_type: '概念',
      timeframe: '今日',
      limit: 20,
    },
  })
})

test('extractConceptRows maps v2 sector fund-flow payload to concept rows', () => {
  const rows = extractConceptRows([
    {
      sector_name: '互联金融',
      change_percent: 1.75,
      main_net_inflow: 5900209920,
      leading_stock: '东方财富',
    },
  ])

  assert.equal(rows.length, 1)
  assert.equal(rows[0]?.name, '互联金融')
  assert.equal(rows[0]?.change_pct, 1.75)
  assert.equal(rows[0]?.main_inflow, '+59.0亿')
  assert.equal(rows[0]?.leader, '东方财富')
})
