import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('stocks orphan page static shell truth', () => {
  it('degrades retired stocks child pages to static shells without mock selector or refresh truth', () => {
    const activity = readSource('src/views/stocks/Activity.vue')
    const concept = readSource('src/views/stocks/Concept.vue')
    const industry = readSource('src/views/stocks/Industry.vue')
    const watchlist = readSource('src/views/stocks/Watchlist.vue')

    for (const source of [activity, concept, industry, watchlist]) {
      expect(source).toContain('legacy-static-shell')
      expect(source).toContain('未接入 canonical verified truth')
      expect(source).not.toContain('ElMessage.success')
      expect(source).not.toContain('setTimeout')
      expect(source).not.toContain('Math.random')
      expect(source).not.toContain('000001')
      expect(source).not.toContain('平安银行')
    }

    expect(activity).not.toContain('Activity data refreshed')
    expect(concept).not.toContain('CONCEPT STOCK POOLS')
    expect(concept).not.toContain('selectedConcept')
    expect(industry).not.toContain('INDUSTRY STOCK POOLS')
    expect(industry).not.toContain('selectedIndustry')
    expect(watchlist).not.toContain('WATCHLIST MANAGEMENT')
    expect(watchlist).not.toContain('filteredStocks')
    expect(watchlist).not.toContain('toggleFavorite')
  })
})
