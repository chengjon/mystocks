import { describe, expect, it } from 'vitest'
import { getPageConfig, isRouteName } from '@/config/pageConfig'

describe('pageConfig home route', () => {
  it('recognizes dashboard as the canonical home route name', () => {
    expect(isRouteName('dashboard')).toBe(true)
  })

  it('does not expose dealing-room as a separate canonical page config route name', () => {
    expect(isRouteName('dealing-room')).toBe(false)
    expect(getPageConfig('dealing-room')).toBeUndefined()
  })

  it('returns dashboard config for the home route', () => {
    const config = getPageConfig('dashboard')

    expect(config).toBeDefined()
    expect(config?.routePath).toBe('dashboard')
    expect(config?.component).toBe('ArtDecoDashboard.vue')
  })
})
