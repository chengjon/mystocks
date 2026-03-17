import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

import { getPageConfig, isStandardConfig } from '@/config/pageConfig'

describe('dashboard page config', () => {
  it('treats dashboard as a multi-endpoint aggregate page instead of a single-endpoint page', () => {
    const config = getPageConfig('dashboard')

    expect(config).toBeDefined()

    if (config && isStandardConfig(config)) {
      expect(config.routePath).toBe('dashboard')
      expect(config.apiEndpoint).toBeUndefined()
      expect(config.wsChannel).toBeUndefined()
      expect(config.component).toBe('ArtDecoDashboard.vue')
    }
  })

  it('removes the single-endpoint route metadata and generator mapping for dashboard', () => {
    const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')
    const generatorSource = readFileSync(
      resolve(process.cwd(), '../../scripts/dev/tools/generate-page-config.js'),
      'utf8'
    )

    expect(routerSource).not.toContain("api: '/api/dashboard/market-overview'")
    expect(generatorSource).not.toContain("'dashboard': { apiEndpoint: '/api/dashboard/market-overview'")
  })
})
