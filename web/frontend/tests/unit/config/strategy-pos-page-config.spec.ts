import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

import { getPageConfig, isStandardConfig } from '@/config/pageConfig'

describe('strategy-pos page config', () => {
  it('pins strategy-pos to the v1 trade positions public root', () => {
    const config = getPageConfig('strategy-pos')

    expect(config).toBeDefined()

    if (config && isStandardConfig(config)) {
      expect(config.routePath).toBe('pos')
      expect(config.apiEndpoint).toBe('/api/v1/trade/positions')
      expect(config.wsChannel).toBeUndefined()
      expect(config.component).toBe('StrategyPositionPage.vue')
    }
  })

  it('keeps router and generator mappings aligned with the same public contract', () => {
    const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')
    const generatorSource = readFileSync(
      resolve(process.cwd(), '../../scripts/dev/tools/generate-page-config.js'),
      'utf8'
    )

    expect(routerSource).toContain("name: 'strategy-pos'")
    expect(routerSource).toContain("component: () => import('@/views/strategy/StrategyPositionPage.vue')")
    expect(routerSource).toContain("api: '/api/v1/trade/positions'")
    expect(generatorSource).toContain("'strategy-pos': { apiEndpoint: '/api/v1/trade/positions'")
  })
})
