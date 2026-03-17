import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

import { getPageConfig, isStandardConfig } from '@/config/pageConfig'

describe('data-fund-flow page config', () => {
  it('pins data-fund-flow to the akshare fund-flow public root', () => {
    const config = getPageConfig('data-fund-flow')

    expect(config).toBeDefined()

    if (config && isStandardConfig(config)) {
      expect(config.routePath).toBe('fund-flow')
      expect(config.apiEndpoint).toBe('/api/akshare/market/fund-flow')
      expect(config.wsChannel).toBeUndefined()
      expect(config.component).toBe('DataFundFlowPage.vue')
    }
  })

  it('keeps router and generator mappings aligned with the same public contract', () => {
    const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')
    const generatorSource = readFileSync(
      resolve(process.cwd(), '../../scripts/dev/tools/generate-page-config.js'),
      'utf8'
    )

    expect(routerSource).toContain("name: 'data-fund-flow'")
    expect(routerSource).toContain("component: () => import('@/views/data/DataFundFlowPage.vue')")
    expect(routerSource).toContain("api: '/api/akshare/market/fund-flow'")
    expect(generatorSource).toContain("'data-fund-flow': { apiEndpoint: '/api/akshare/market/fund-flow'")
  })
})
