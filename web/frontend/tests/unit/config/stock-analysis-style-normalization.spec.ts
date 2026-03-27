import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('stock-analysis style normalization', () => {
  it('normalizes stock analysis tabs onto @use-based ArtDeco styles', () => {
    const files = [
      'src/views/stock-analysis/StockBacktestTab.vue',
      'src/views/stock-analysis/StockDataTab.vue',
      'src/views/stock-analysis/StockOverviewTab.vue',
      'src/views/stock-analysis/StockRealtimeTab.vue',
      'src/views/stock-analysis/StockStatusTab.vue',
      'src/views/stock-analysis/StockStrategyTab.vue',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
      expect(source).not.toContain("@import '@/styles/artdeco-tokens';")
    }
  })

  it('normalizes grid-aware stock analysis tabs onto @use-based grid styles', () => {
    const files = [
      'src/views/stock-analysis/StockOverviewTab.vue',
      'src/views/stock-analysis/StockRealtimeTab.vue',
      'src/views/stock-analysis/StockStrategyTab.vue',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).toContain("@use '@/styles/artdeco-grid.scss' as *;")
      expect(source).not.toContain("@import '@/styles/artdeco-grid';")
    }
  })
})
