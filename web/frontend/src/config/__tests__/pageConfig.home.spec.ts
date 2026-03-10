import { describe, expect, it } from 'vitest'
import { getPageConfig, isRouteName } from '@/config/pageConfig'

describe('pageConfig home route', () => {
  it('recognizes dashboard as the canonical home route name', () => {
    expect(isRouteName('dashboard')).toBe(true)
  })

  it('returns dashboard config for the home route', () => {
    const config = getPageConfig('dashboard')

    expect(config).toBeDefined()
    expect(config?.routePath).toBe('dashboard')
    expect(config?.component).toBe('ArtDecoDashboard.vue')
  })
})
