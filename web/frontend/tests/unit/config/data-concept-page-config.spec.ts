import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

import { getPageConfig, isStandardConfig } from '@/config/pageConfig'

describe('data-concept page config', () => {
  it('pins data-concept to the v2 sector fund-flow public contract', () => {
    const config = getPageConfig('data-concept')

    expect(config).toBeDefined()

    if (config && isStandardConfig(config)) {
      expect(config.routePath).toBe('concept')
      expect(config.apiEndpoint).toBe('/api/v2/market/sector/fund-flow?sector_type=概念')
      expect(config.component).toBe('MarketConceptTab.vue')
    }
  })

  it('keeps the generator mapping aligned with the same public contract', () => {
    const script = readFileSync(
      resolve(process.cwd(), '../../scripts/dev/tools/generate-page-config.js'),
      'utf8'
    )

    expect(script).toContain("'data-concept': { apiEndpoint: '/api/v2/market/sector/fund-flow?sector_type=概念'")
  })
})
