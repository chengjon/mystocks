import { describe, expect, it } from 'vitest'
import { extractIndustryFlowRows, toBoardRows, toRotationRows } from '../industryAnalysisData'

describe('industryAnalysisData', () => {
  it('extracts rows from direct array and nested containers', () => {
    const direct = extractIndustryFlowRows([{ name: '半导体' }])
    const nested = extractIndustryFlowRows({ items: [{ name: '人工智能' }] })

    expect(direct).toHaveLength(1)
    expect(nested).toHaveLength(1)
    expect(direct[0]?.name).toBe('半导体')
    expect(nested[0]?.name).toBe('人工智能')
  })

  it('maps raw rows to board rows with signed change and net inflow', () => {
    const rows = toBoardRows([{ rank: 1, name: 'AI算力', change: 2.5, amount: 200 }])

    expect(rows).toHaveLength(1)
    expect(rows[0]?.rank).toBe(1)
    expect(rows[0]?.name).toBe('AI算力')
    expect(rows[0]?.change).toBe('+2.50%')
    expect(rows[0]?.turnover).toBe(200)
    expect(rows[0]?.netInflow).toBe('+5.0')
  })

  it('maps v2 sector fund-flow fields to board rows', () => {
    const rows = toBoardRows([
      {
        rank: 1,
        sector_name: '证券',
        change_percent: 2.92,
        main_net_inflow: 3441226240,
        main_net_inflow_rate: 7.58
      } as any
    ])

    expect(rows).toHaveLength(1)
    expect(rows[0]?.name).toBe('证券')
    expect(rows[0]?.change).toBe('+2.92%')
    expect(rows[0]?.turnover).toBe(34.41)
    expect(rows[0]?.netInflow).toBe('+7.58%')
  })

  it('builds rotation rows from board rows without mock fallback', () => {
    const rotation = toRotationRows([
      { rank: 1, name: '半导体', change: '+2.10%', turnover: 310, netInflow: '+6.5' },
      { rank: 2, name: '算力', change: '+1.20%', turnover: 280, netInflow: '+3.1' }
    ])

    expect(rotation).toHaveLength(2)
    expect(rotation[0]?.window).toBe('近1日')
    expect(rotation[1]?.window).toBe('近3日')
    expect(rotation[0]?.flow).toBe(6.5)
  })
})
