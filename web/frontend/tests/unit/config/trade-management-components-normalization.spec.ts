import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('trade-management component normalization', () => {
  it('moves PortfolioOverview onto ArtDeco stat cards', () => {
    const source = readSource('src/views/trade-management/components/PortfolioOverview.vue')
    expect(source).toContain("import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'")
    expect(source).toContain('<ArtDecoStatCard')
    expect(source).not.toContain('BloombergStatCard')
    expect(source).toContain('const formatCurrency = (value: number) =>')
  })

  it('keeps PositionsTab, StatisticsTab, and TradeDialog on tokenized layout values', () => {
    const positions = readSource('src/views/trade-management/components/PositionsTab.vue')
    const statistics = readSource('src/views/trade-management/components/StatisticsTab.vue')
    const dialog = readSource('src/views/trade-management/components/TradeDialog.vue')

    expect(positions).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
    expect(positions).toContain('var(--artdeco-border-default)')
    expect(positions).not.toContain('#1E293B')

    expect(statistics).toContain('const chartHeight =')
    expect(statistics).toContain('getCssVar')
    expect(statistics).toContain("@use '@/styles/artdeco-tokens.scss' as *;")

    expect(dialog).toContain("const dialogWidth = 'calc((var(--artdeco-spacing-20) * 7) + var(--artdeco-spacing-10))'")
    expect(dialog).toContain("const labelWidth = 'calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-10))'")
    expect(dialog).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
  })
})
