import { describe, expect, it } from 'vitest'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

const wrapperCases = [
  {
    label: 'trade center',
    canonicalPath: 'src/views/trade/Center.vue',
    legacyPath: 'src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue',
    legacyImportLine: "import TradeCenterCanonicalPage from '@/views/trade/Center.vue'",
    legacyRenderLine: '<TradeCenterCanonicalPage v-bind="attrs" />',
    canonicalEvidence: [
      "import { apiClient } from '@/api/apiClient'",
      "title=\"持仓工作台\"",
      "apiClient.get('/v1/trade/positions')"
    ]
  },
  {
    label: 'trade signals',
    wrapperPath: 'src/views/trade/Signals.vue',
    implementationPath: 'src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue',
    importLine: "import TradeSignalsPage from '@/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue'",
    renderLine: '<TradeSignalsPage v-bind="attrs" />'
  },
  {
    label: 'trade portfolio',
    wrapperPath: 'src/views/trade/Portfolio.vue',
    implementationPath: 'src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue',
    importLine: "import TradePortfolioPage from '@/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue'",
    renderLine: '<TradePortfolioPage v-bind="attrs" />'
  },
  {
    label: 'trade history',
    wrapperPath: 'src/views/trade/History.vue',
    implementationPath: 'src/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue',
    importLine: "import TradeHistoryPage from '@/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue'",
    renderLine: '<TradeHistoryPage v-bind="attrs" />'
  }
] as const

describe('trade wrapper retention', () => {
  it('moves the canonical trade center implementation into src/views/trade/Center.vue and keeps the ArtDeco path as a legacy wrapper', () => {
    const canonicalSource = readSource(wrapperCases[0].canonicalPath)
    const legacySource = readSource(wrapperCases[0].legacyPath)
    const legacyFullPath = resolve(process.cwd(), wrapperCases[0].legacyPath)

    expect(existsSync(legacyFullPath)).toBe(true)
    for (const evidenceLine of wrapperCases[0].canonicalEvidence) {
      expect(canonicalSource).toContain(evidenceLine)
    }
    expect(legacySource).toContain(wrapperCases[0].legacyImportLine)
    expect(legacySource).toContain(wrapperCases[0].legacyRenderLine)
  })

  for (const wrapperCase of wrapperCases.slice(1)) {
    it(`keeps the canonical ${wrapperCase.label} wrapper pointed at its ArtDeco implementation`, () => {
      const wrapperSource = readSource(wrapperCase.wrapperPath)
      const implementationFullPath = resolve(process.cwd(), wrapperCase.implementationPath)

      expect(existsSync(implementationFullPath)).toBe(true)
      expect(wrapperSource).toContain(wrapperCase.importLine)
      expect(wrapperSource).toContain(wrapperCase.renderLine)
    })
  }
})
