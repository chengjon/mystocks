import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

import { getPageConfig, isStandardConfig } from '@/config/pageConfig'

describe('market-lhb page config', () => {
  it('pins market-lhb to the v1 market lhb public root', () => {
    const config = getPageConfig('market-lhb')

    expect(config).toBeDefined()

    if (config && isStandardConfig(config)) {
      expect(config.routePath).toBe('lhb')
      expect(config.apiEndpoint).toBe('/api/v1/market/lhb')
      expect(config.wsChannel).toBeUndefined()
      expect(config.component).toBe('MarketDragonTigerPage.vue')
    }
  })

  it('keeps router and generator mappings aligned with the same public contract', () => {
    const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')
    const generatorSource = readFileSync(
      resolve(process.cwd(), '../../scripts/dev/tools/generate-page-config.js'),
      'utf8'
    )

    expect(routerSource).toContain("name: 'market-lhb'")
    expect(routerSource).toContain("component: () => import('@/views/market/MarketDragonTigerPage.vue')")
    expect(routerSource).toContain("api: '/api/v1/market/lhb'")
    expect(generatorSource).toContain("'market-lhb': { apiEndpoint: '/api/v1/market/lhb'")
  })
})
