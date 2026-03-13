import { describe, expect, it } from 'vitest'
import {
  PAGE_CONFIG,
  TAB_CONFIGS,
  getPageConfig,
  getTabConfig,
  isMonolithicConfig,
  isRouteName,
  isStandardConfig,
} from '@/config/pageConfig'

describe('Page Configuration System', () => {
  describe('active ArtDeco route names', () => {
    it('recognizes current P0/P1 route names', () => {
      expect(isRouteName('dashboard')).toBe(true)
      expect(isRouteName('market-realtime')).toBe(true)
      expect(isRouteName('strategy-repo')).toBe(true)
      expect(isRouteName('trade-positions')).toBe(true)
      expect(isRouteName('risk-alerts')).toBe(true)
    })

    it('rejects legacy or out-of-scope route names', () => {
      expect(isRouteName('artdeco-market-data')).toBe(false)
      expect(isRouteName('qm-market-realtime')).toBe(false)
      expect(isRouteName('stock-graphics')).toBe(false)
      expect(isRouteName('not-found')).toBe(false)
    })
  })

  describe('standard page configurations', () => {
    it('returns the canonical dashboard config', () => {
      const config = getPageConfig('dashboard')

      expect(config).toBeDefined()
      expect(config?.type).toBe('page')
      expect(config?.routePath).toBe('dashboard')
      expect(config?.component).toBe('ArtDecoDashboard.vue')
      expect(config?.apiEndpoint).toBe('/api/v1/market/overview')
    })

    it('uses current router-or-plan API truth for verified pages', () => {
      expect(getPageConfig('market-realtime')?.apiEndpoint).toBe('/api/v1/market/quotes')
      expect(getPageConfig('market-technical')?.apiEndpoint).toBe('/api/v1/market/kline')
      expect(getPageConfig('data-industry')?.apiEndpoint).toBe('/api/akshare/market/boards')
      expect(getPageConfig('strategy-repo')?.apiEndpoint).toBe('/api/v1/strategy/strategies')
    })

    it('uses current route mapping for pending-but-active pages', () => {
      expect(getPageConfig('trade-positions')?.apiEndpoint).toBe('/api/v1/trade/positions')
      expect(getPageConfig('trade-portfolio')?.apiEndpoint).toBe('/api/v1/trade/positions')
      expect(getPageConfig('risk-overview')?.apiEndpoint).toBe('/api/v1/risk/*')
      expect(getPageConfig('system-config')?.apiEndpoint).toBe('/api/system/*')
    })

    it('keeps login reachable in page config', () => {
      const config = getPageConfig('login')

      expect(config).toBeDefined()
      expect(config?.type).toBe('page')
      expect(config?.component).toBe('Login.vue')
      expect(config?.apiEndpoint).toBe('/api/v1/auth/login')
      expect(config?.requiresAuth).toBe(false)
    })
  })

  describe('scope filtering', () => {
    it('excludes QuantMatrix, detail, and fallback routes from active page config', () => {
      expect(PAGE_CONFIG['qm-market-realtime']).toBeUndefined()
      expect(PAGE_CONFIG['stock-news']).toBeUndefined()
      expect(PAGE_CONFIG['not-found']).toBeUndefined()
    })
  })

  describe('tab helpers', () => {
    it('does not expose obsolete monolithic tabs for active ArtDeco routes', () => {
      const dashboardConfig = getPageConfig('dashboard')

      expect(dashboardConfig).toBeDefined()
      expect(isStandardConfig(dashboardConfig!)).toBe(true)
      expect(isMonolithicConfig(dashboardConfig!)).toBe(false)
      expect(getTabConfig('dashboard', 'overview')).toBeUndefined()
      expect(Object.keys(TAB_CONFIGS)).toHaveLength(0)
    })
  })
})
