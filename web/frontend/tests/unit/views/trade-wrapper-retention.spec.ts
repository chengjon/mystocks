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
    canonicalPath: 'src/views/trade/Signals.vue',
    legacyPath: 'src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue',
    legacyImportLine: "import TradeSignalsCanonicalPage from '@/views/trade/Signals.vue'",
    legacyRenderLine: '<TradeSignalsCanonicalPage v-bind="attrs" />',
    canonicalEvidence: [
      "import { useTradingSignalsStore } from '@/stores/apiStores'",
      "title=\"交易信号工作台\"",
      'tradingSignalsStore.refresh({ limit: 20 })'
    ]
  },
  {
    label: 'trade portfolio',
    canonicalPath: 'src/views/trade/Portfolio.vue',
    legacyPath: 'src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue',
    legacyImportLine: "import TradePortfolioCanonicalPage from '@/views/trade/Portfolio.vue'",
    legacyRenderLine: '<TradePortfolioCanonicalPage v-bind="attrs" />',
    canonicalEvidence: [
      "import { apiClient } from '@/api/apiClient'",
      "title=\"组合资产工作台\"",
      "apiClient.get('/v1/trade/positions')",
    ]
  },
  {
    label: 'trade history',
    canonicalPath: 'src/views/trade/History.vue',
    legacyPath: 'src/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue',
    legacyImportLine: "import TradeHistoryCanonicalPage from '@/views/trade/History.vue'",
    legacyRenderLine: '<TradeHistoryCanonicalPage v-bind="attrs" />',
    canonicalEvidence: [
      "import { apiClient } from '@/api/apiClient'",
      "title=\"交易历史工作台\"",
      "apiClient.get('/v1/trade/trades')",
    ]
  },
  {
    label: 'trade embedded position monitor',
    canonicalPath: 'src/views/trade/Center.vue',
    legacyPath: 'src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue',
    legacyImportLine: "import TradeCenterCanonicalPage from '@/views/trade/Center.vue'",
    legacyRenderLine: '<TradeCenterCanonicalPage v-bind="attrs" :positions="[]" />',
    canonicalEvidence: [
      "const isEmbedded = computed(() => {",
      "return Boolean(rawProps && 'positions' in rawProps)",
      "apiClient.get('/v1/trade/positions')"
    ]
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

  it('moves the canonical trade signals implementation into src/views/trade/Signals.vue and keeps the ArtDeco path as a legacy wrapper', () => {
    const canonicalSource = readSource(wrapperCases[1].canonicalPath)
    const legacySource = readSource(wrapperCases[1].legacyPath)
    const legacyFullPath = resolve(process.cwd(), wrapperCases[1].legacyPath)

    expect(existsSync(legacyFullPath)).toBe(true)
    for (const evidenceLine of wrapperCases[1].canonicalEvidence) {
      expect(canonicalSource).toContain(evidenceLine)
    }
    expect(legacySource).toContain(wrapperCases[1].legacyImportLine)
    expect(legacySource).toContain(wrapperCases[1].legacyRenderLine)
  })

  it('moves the canonical trade portfolio implementation into src/views/trade/Portfolio.vue and keeps the ArtDeco path as a legacy wrapper', () => {
    const canonicalSource = readSource(wrapperCases[2].canonicalPath)
    const legacySource = readSource(wrapperCases[2].legacyPath)
    const legacyFullPath = resolve(process.cwd(), wrapperCases[2].legacyPath)

    expect(existsSync(legacyFullPath)).toBe(true)
    for (const evidenceLine of wrapperCases[2].canonicalEvidence) {
      expect(canonicalSource).toContain(evidenceLine)
    }
    expect(legacySource).toContain(wrapperCases[2].legacyImportLine)
    expect(legacySource).toContain(wrapperCases[2].legacyRenderLine)
  })

  it('moves the canonical trade history implementation into src/views/trade/History.vue and keeps the ArtDeco path as a legacy wrapper', () => {
    const canonicalSource = readSource(wrapperCases[3].canonicalPath)
    const legacySource = readSource(wrapperCases[3].legacyPath)
    const legacyFullPath = resolve(process.cwd(), wrapperCases[3].legacyPath)

    expect(existsSync(legacyFullPath)).toBe(true)
    for (const evidenceLine of wrapperCases[3].canonicalEvidence) {
      expect(canonicalSource).toContain(evidenceLine)
    }
    expect(legacySource).toContain(wrapperCases[3].legacyImportLine)
    expect(legacySource).toContain(wrapperCases[3].legacyRenderLine)
  })

  it('keeps the embedded trade position monitor as a thin wrapper over src/views/trade/Center.vue instead of a placeholder fork', () => {
    const canonicalSource = readSource(wrapperCases[4].canonicalPath)
    const legacySource = readSource(wrapperCases[4].legacyPath)
    const legacyFullPath = resolve(process.cwd(), wrapperCases[4].legacyPath)

    expect(existsSync(legacyFullPath)).toBe(true)
    for (const evidenceLine of wrapperCases[4].canonicalEvidence) {
      expect(canonicalSource).toContain(evidenceLine)
    }
    expect(legacySource).toContain(wrapperCases[4].legacyImportLine)
    expect(legacySource).toContain(wrapperCases[4].legacyRenderLine)
    expect(legacySource).not.toContain('头寸监控主面板整理中')
  })
})
