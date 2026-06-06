import test from 'node:test'
import assert from 'node:assert/strict'

import { extractDataSourceConfigItems } from '../dataManagementData.ts'

test('extractDataSourceConfigItems supports endpoints payload', () => {
  const items = extractDataSourceConfigItems({
    endpoints: [
      {
        endpoint_name: 'akshare.stock_zh_a_hist',
        source_name: 'akshare',
        status: 'active',
        url: 'https://ak.example/api',
      },
    ],
  })

  assert.deepEqual(items, [
    {
      endpointName: 'akshare.stock_zh_a_hist',
      name: 'akshare',
      enabled: true,
      endpoint: 'https://ak.example/api',
      status: 'active',
    },
  ])
})

test('extractDataSourceConfigItems maps non-active status to disabled', () => {
  const items = extractDataSourceConfigItems({
    endpoints: [
      {
        endpoint_name: 'tushare.stock_basic',
        source_name: 'tushare',
        status: 'maintenance',
        url: 'https://ts.example/api',
      },
    ],
  })

  assert.deepEqual(items, [
    {
      endpointName: 'tushare.stock_basic',
      name: 'tushare',
      enabled: false,
      endpoint: 'https://ts.example/api',
      status: 'maintenance',
    },
  ])
})

test('extractDataSourceConfigItems prefers endpoint description and endpoint name when the live payload has no url field', () => {
  const items = extractDataSourceConfigItems({
    endpoints: [
      {
        endpoint_name: 'akshare.stock_lhb_detail_em',
        description: 'AKShare龙虎榜详情数据',
        source_name: 'akshare',
        status: 'active',
      },
    ],
  })

  assert.deepEqual(items, [
    {
      endpointName: 'akshare.stock_lhb_detail_em',
      name: 'AKShare龙虎榜详情数据',
      enabled: true,
      endpoint: 'akshare.stock_lhb_detail_em',
      status: 'active',
    },
  ])
})
