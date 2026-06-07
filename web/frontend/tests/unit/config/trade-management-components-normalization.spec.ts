import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('trade-management component normalization', () => {
  it('degrades orphan trade-management components to honest static shells', () => {
    const source = readSource('src/views/trade-management/components/PortfolioOverview.vue')
    const positions = readSource('src/views/trade-management/components/PositionsTab.vue')
    const statistics = readSource('src/views/trade-management/components/StatisticsTab.vue')
    const history = readSource('src/views/trade-management/components/TradeHistoryTab.vue')
    const dialog = readSource('src/views/trade-management/components/TradeDialog.vue')

    for (const sourceText of [source, positions, statistics, history, dialog]) {
      expect(sourceText).toContain('legacy-static-shell')
      expect(sourceText).toContain('未接入 canonical verified truth')
      expect(sourceText).not.toContain("from '@/api/trade'")
      expect(sourceText).not.toContain('tradeApi.')
      expect(sourceText).not.toContain('console.error')
    }

    expect(source).not.toContain('total_assets: 1000000')
    expect(source).not.toContain('<ArtDecoStatCard')

    expect(positions).not.toContain('PING AN BANK')
    expect(positions).not.toContain('handleQuickSell')
    expect(positions).not.toContain('POSITION DATA REFRESHED')

    expect(statistics).not.toContain('echarts.init')
    expect(statistics).not.toContain('NO POSITION')
    expect(statistics).not.toContain('startDate.setDate')

    expect(history).not.toContain('getTradeHistory')
    expect(history).not.toContain('FAILED TO LOAD TRADE HISTORY')
    expect(history).not.toContain('TOTAL: {{ pagination.total }} RECORDS')

    expect(dialog).not.toContain('createOrder')
    expect(dialog).not.toContain('ORDER SUBMITTED')
    expect(dialog).not.toContain('TRADE FAILED')
  })
})
