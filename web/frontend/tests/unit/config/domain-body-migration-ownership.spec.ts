import { describe, expect, it } from 'vitest'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('domain body migration ownership', () => {
  it('owns the realtime page body in the market domain', () => {
    const canonicalSource = readSource('src/views/market/Realtime.vue')
    const legacySource = readSource('src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue')

    expect(existsSync(resolve(process.cwd(), 'src/views/market/marketRealtimeData.ts'))).toBe(true)
    expect(canonicalSource).toContain("from './marketRealtimeData'")
    expect(canonicalSource).not.toContain("@/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue")
    expect(legacySource).toContain("from '@/views/market/Realtime.vue'")
  })

  it('owns the technical page body in the market domain', () => {
    const canonicalSource = readSource('src/views/market/Technical.vue')
    const legacySource = readSource('src/views/artdeco-pages/market-tabs/MarketKLineTab.vue')

    expect(existsSync(resolve(process.cwd(), 'src/views/market/marketKlineData.ts'))).toBe(true)
    expect(canonicalSource).toContain("from './marketKlineData'")
    expect(canonicalSource).not.toContain("@/views/artdeco-pages/market-tabs/MarketKLineTab.vue")
    expect(legacySource).toContain("from '@/views/market/Technical.vue'")
  })

  it('owns the lhb page body in the market domain', () => {
    const canonicalSource = readSource('src/views/market/LHB.vue')
    const legacySource = readSource('src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue')

    expect(existsSync(resolve(process.cwd(), 'src/views/market/dragonTigerData.ts'))).toBe(true)
    expect(canonicalSource).toContain("from './dragonTigerData'")
    expect(canonicalSource).not.toContain("@/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue")
    expect(legacySource).toContain("from '@/views/market/LHB.vue'")
  })

  it('owns the industry page body in the data domain', () => {
    const canonicalSource = readSource('src/views/data/Industry.vue')
    const legacySource = readSource('src/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue')

    expect(existsSync(resolve(process.cwd(), 'src/views/data/industryAnalysisData.ts'))).toBe(true)
    expect(canonicalSource).toContain("from './industryAnalysisData'")
    expect(canonicalSource).not.toContain("@/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue")
    expect(legacySource).toContain("from '@/views/data/Industry.vue'")
  })

  it('owns the concept page body in the data domain', () => {
    const canonicalSource = readSource('src/views/data/Concepts.vue')
    const legacySource = readSource('src/views/artdeco-pages/market-tabs/MarketConceptTab.vue')

    expect(existsSync(resolve(process.cwd(), 'src/views/data/marketConceptData.ts'))).toBe(true)
    expect(canonicalSource).toContain("from './marketConceptData'")
    expect(canonicalSource).not.toContain("@/views/artdeco-pages/market-tabs/MarketConceptTab.vue")
    expect(legacySource).toContain("from '@/views/data/Concepts.vue'")
  })

  it('owns the fund flow page body in the data domain', () => {
    const canonicalSource = readSource('src/views/data/FundFlow.vue')
    const legacySource = readSource('src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue')

    expect(existsSync(resolve(process.cwd(), 'src/views/data/fundFlowPageData.ts'))).toBe(true)
    expect(canonicalSource).toContain("from './fundFlowPageData'")
    expect(canonicalSource).not.toContain("@/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue")
    expect(legacySource).toContain("from '@/views/data/FundFlow.vue'")
  })
})
