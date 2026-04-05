import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import {
  HOME_ROUTE_NAME,
  HOME_ROUTE_PATH,
  LEGACY_HOME_ROUTE_PATH,
  normalizeLegacyHomeRedirect,
} from '@/router/homeRoute'

const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')

describe('dashboard route canonical truth', () => {
  it('keeps dashboard as the canonical home route constant', () => {
    expect(HOME_ROUTE_NAME).toBe('dashboard')
    expect(HOME_ROUTE_PATH).toBe('/dashboard')
    expect(LEGACY_HOME_ROUTE_PATH).toBe('/dealing-room')
  })

  it('normalizes legacy home redirects back to the canonical dashboard path', () => {
    expect(normalizeLegacyHomeRedirect('/dealing-room')).toBe('/dashboard')
    expect(normalizeLegacyHomeRedirect('/dealing-room?view=full#hero')).toBe('/dashboard?view=full#hero')
  })

  it('preserves a legacy dealing-room redirect in router truth', () => {
    expect(routerSource).toContain('path: LEGACY_HOME_ROUTE_PATH')
    expect(routerSource).toContain('redirect: HOME_ROUTE_PATH')
  })

  it('keeps trade-terminal semantics separate from dashboard truth', () => {
    expect(routerSource).toContain("name: 'trade-terminal'")
    expect(routerSource).toContain("component: () => import('@/views/TradingDashboard.vue')")
  })
})
