import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

import { getPageConfig, isStandardConfig } from '@/config/pageConfig'

describe('watchlist-manage page config', () => {
  it('pins watchlist-manage to the v1 monitoring watchlists public root', () => {
    const config = getPageConfig('watchlist-manage')

    expect(config).toBeDefined()

    if (config && isStandardConfig(config)) {
      expect(config.routePath).toBe('manage')
      expect(config.apiEndpoint).toBe('/api/v1/monitoring/watchlists')
      expect(config.wsChannel).toBeUndefined()
      expect(config.component).toBe('WatchlistManagement.vue')
    }
  })

  it('keeps router and generator mappings aligned with the same public contract', () => {
    const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')
    const generatorSource = readFileSync(
      resolve(process.cwd(), '../../scripts/dev/tools/generate-page-config.js'),
      'utf8'
    )

    expect(routerSource).toContain("name: 'watchlist-manage'")
    expect(routerSource).toContain("component: () => import('@/views/monitoring/WatchlistManagement.vue')")
    expect(routerSource).toContain("api: '/api/v1/monitoring/watchlists'")
    expect(generatorSource).toContain("'watchlist-manage': { apiEndpoint: '/api/v1/monitoring/watchlists'")
  })
})
