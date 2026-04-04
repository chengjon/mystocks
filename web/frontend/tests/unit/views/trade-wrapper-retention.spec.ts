import { describe, expect, it } from 'vitest'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

const wrapperCases = [
  {
    label: 'trade center',
    wrapperPath: 'src/views/trade/Center.vue',
    implementationPath: 'src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue',
    importLine: "import TradeCenterPage from '@/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue'",
    renderLine: '<TradeCenterPage v-bind="attrs" />'
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
  for (const wrapperCase of wrapperCases) {
    it(`keeps the canonical ${wrapperCase.label} wrapper pointed at its ArtDeco implementation`, () => {
      const wrapperSource = readSource(wrapperCase.wrapperPath)
      const implementationFullPath = resolve(process.cwd(), wrapperCase.implementationPath)

      expect(existsSync(implementationFullPath)).toBe(true)
      expect(wrapperSource).toContain(wrapperCase.importLine)
      expect(wrapperSource).toContain(wrapperCase.renderLine)
    })
  }
})
