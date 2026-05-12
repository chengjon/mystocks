import { describe, expect, it } from 'vitest'

import { hasRoutePermission } from '../utils.js'

describe('router utils authorization helpers', () => {
  it('should reject malformed user role payloads', () => {
    const route = {
      meta: {
        roles: ['admin'],
      },
    }

    expect(hasRoutePermission(route, 'admin')).toBe(false)
  })

  it('should reject malformed route role metadata without throwing', () => {
    const route = {
      meta: {
        roles: 'admin',
      },
    }

    expect(() => hasRoutePermission(route, ['admin'])).not.toThrow()
    expect(hasRoutePermission(route, ['admin'])).toBe(false)
  })
})
