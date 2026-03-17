import { describe, expect, it } from 'vitest'

import { ARTDECO_MENU_ITEMS, DEALING_ROOM_CONFIG, MENU_CONFIG_MAP } from '../../../src/layouts/MenuConfig'

describe('MenuConfig current contract', () => {
  it('exposes the seven current business domains', () => {
    expect(ARTDECO_MENU_ITEMS).toHaveLength(7)
    expect(ARTDECO_MENU_ITEMS.map(item => item.path)).toEqual([
      '/market',
      '/data',
      '/watchlist',
      '/strategy',
      '/trade',
      '/risk',
      '/system',
    ])
  })

  it('keeps all menu items on absolute paths with required display fields', () => {
    for (const domain of ARTDECO_MENU_ITEMS) {
      expect(domain.path.startsWith('/')).toBe(true)
      expect(domain.label).toBeTruthy()
      expect(domain.icon).toBeTruthy()
      expect(domain.businessKey).toBeTruthy()

      for (const child of domain.children ?? []) {
        expect(child.path.startsWith('/')).toBe(true)
        expect(child.label).toBeTruthy()
        expect(child.icon).toBeTruthy()
        expect(child.businessKey).toBeTruthy()
      }
    }
  })

  it('keeps the dealing room as a special non-sidebar route', () => {
    expect(DEALING_ROOM_CONFIG.path).toBe('/dashboard')
    expect(DEALING_ROOM_CONFIG.label).toBe('交易室')
    expect(DEALING_ROOM_CONFIG.apiEndpoint).toBeUndefined()
    expect(DEALING_ROOM_CONFIG.apiMethod).toBe('GET')
  })

  it('maps current ArtDeco layouts to the shared menu tree', () => {
    expect(Object.keys(MENU_CONFIG_MAP)).toEqual(['ArtDecoDashboard', 'ArtDecoEnhanced'])
    expect(MENU_CONFIG_MAP.ArtDecoDashboard).toBe(ARTDECO_MENU_ITEMS)
    expect(MENU_CONFIG_MAP.ArtDecoEnhanced).toBe(ARTDECO_MENU_ITEMS)
  })
})
