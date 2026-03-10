import { describe, expect, it } from 'vitest'
import router from '@/router/index'

describe('home route compatibility', () => {
  it('keeps a legacy /dealing-room redirect to /dashboard', () => {
    const legacyRoute = router.getRoutes().find((route) => route.path === '/dealing-room')

    expect(legacyRoute).toBeDefined()
    expect(legacyRoute?.redirect).toBe('/dashboard')
  })
})
