import { describe, expect, it } from 'vitest'

import {
  PAGE_CONFIG,
  getPageConfig,
  getTabConfig,
  getTabsForComponent,
  isMonolithicConfig,
  isRouteName,
  isStandardConfig,
} from '../../../src/config/pageConfig'

describe('pageConfig current contract', () => {
  describe('route guards', () => {
    it('accepts current route names and rejects retired legacy route names', () => {
      expect(isRouteName('dashboard')).toBe(true)
      expect(isRouteName('market-realtime')).toBe(true)
      expect(isRouteName('data-fund-flow')).toBe(true)
      expect(isRouteName('strategy-repo')).toBe(true)

      expect(isRouteName('market-fund-flow')).toBe(false)
      expect(isRouteName('stock-management')).toBe(false)
      expect(isRouteName('artdeco-market-data')).toBe(false)
      expect(isRouteName('artdeco-stock-management')).toBe(false)
      expect(isRouteName('invalid-route')).toBe(false)
    })
  })

  describe('page lookups', () => {
    it('returns current standard page config for dashboard', () => {
      const config = getPageConfig('dashboard')

      expect(config).toBeDefined()
      expect(config && isStandardConfig(config)).toBe(true)
      expect(config?.type).toBe('page')
      expect(config?.routePath).toBe('dashboard')
      expect(config?.apiEndpoint).toBeUndefined()
      expect(config?.component).toBe('ArtDecoDashboard.vue')
    })

    it('returns current standard page config for market realtime', () => {
      const config = getPageConfig('market-realtime')

      expect(config).toBeDefined()
      expect(config && isStandardConfig(config)).toBe(true)
      expect(config?.type).toBe('page')
      expect(config?.routePath).toBe('realtime')
      expect(config?.apiEndpoint).toBe('/api/market/realtime')
      expect(config?.wsChannel).toBe('market:realtime')
      expect(config?.component).toBe('Realtime.vue')
    })

    it('returns current standard page config for market technical and lhb using canonical domain filenames', () => {
      const technicalConfig = getPageConfig('market-technical')
      const lhbConfig = getPageConfig('market-lhb')

      expect(technicalConfig?.component).toBe('Technical.vue')
      expect(lhbConfig?.component).toBe('LHB.vue')
    })

    it('returns current standard page config for data routes using canonical domain filenames', () => {
      const industryConfig = getPageConfig('data-industry')
      const conceptConfig = getPageConfig('data-concept')
      const fundFlowConfig = getPageConfig('data-fund-flow')
      const indicatorConfig = getPageConfig('data-indicator')

      expect(industryConfig?.component).toBe('Industry.vue')
      expect(conceptConfig?.component).toBe('Concepts.vue')
      expect(fundFlowConfig?.component).toBe('FundFlow.vue')
      expect(indicatorConfig?.component).toBe('Advanced.vue')
    })

    it('returns current standard page config for strategy routes using canonical domain filenames', () => {
      const repoConfig = getPageConfig('strategy-repo')
      const parametersConfig = getPageConfig('strategy-parameters')
      const backtestConfig = getPageConfig('strategy-backtest')
      const optimizationConfig = getPageConfig('strategy-opt')

      expect(repoConfig?.component).toBe('List.vue')
      expect(parametersConfig?.component).toBe('Parameters.vue')
      expect(backtestConfig?.component).toBe('Backtest.vue')
      expect(optimizationConfig?.component).toBe('Optimization.vue')
    })

    it('returns current standard page config for trade routes using canonical domain filenames', () => {
      const positionsConfig = getPageConfig('trade-positions')
      const signalsConfig = getPageConfig('trade-signals')
      const portfolioConfig = getPageConfig('trade-portfolio')
      const historyConfig = getPageConfig('trade-history')

      expect(positionsConfig?.component).toBe('Center.vue')
      expect(signalsConfig?.component).toBe('Signals.vue')
      expect(portfolioConfig?.component).toBe('Portfolio.vue')
      expect(historyConfig?.component).toBe('History.vue')
    })

    it('returns current standard page config for approved risk routes using canonical domain filenames', () => {
      const overviewConfig = getPageConfig('risk-overview')
      const stopLossConfig = getPageConfig('risk-stop-loss')
      const alertsConfig = getPageConfig('risk-alerts')
      const newsConfig = getPageConfig('risk-news')

      expect(overviewConfig?.component).toBe('Overview.vue')
      expect(stopLossConfig?.component).toBe('StopLoss.vue')
      expect(alertsConfig?.component).toBe('Alerts.vue')
      expect(newsConfig?.component).toBe('News.vue')
    })

    it('returns current standard page config for system routes using canonical domain filenames', () => {
      const configConfig = getPageConfig('system-config')
      const healthConfig = getPageConfig('system-health')
      const apiConfig = getPageConfig('system-api')
      const resourcesConfig = getPageConfig('system-resources')
      const dataConfig = getPageConfig('system-data')

      expect(configConfig?.component).toBe('Settings.vue')
      expect(configConfig?.apiEndpoint).toBe('/health/detailed')
      expect(configConfig?.wsChannel).toBeUndefined()
      expect(healthConfig?.component).toBe('Health.vue')
      expect(healthConfig?.apiEndpoint).toBe('/health')
      expect(healthConfig?.wsChannel).toBeUndefined()
      expect(apiConfig?.component).toBe('API.vue')
      expect(apiConfig?.apiEndpoint).toBe('/health')
      expect(apiConfig?.wsChannel).toBeUndefined()
      expect(resourcesConfig?.component).toBe('Resources.vue')
      expect(resourcesConfig?.apiEndpoint).toBe('/api/v1/system/resources')
      expect(resourcesConfig?.wsChannel).toBeUndefined()
      expect(dataConfig?.component).toBe('DataSource.vue')
      expect(dataConfig?.apiEndpoint).toBe('/v1/data-sources/config/')
      expect(dataConfig?.wsChannel).toBeUndefined()
    })

    it('does not expose retired legacy keys in PAGE_CONFIG', () => {
      expect(PAGE_CONFIG['artdeco-market-data']).toBeUndefined()
      expect(PAGE_CONFIG['artdeco-stock-management']).toBeUndefined()
      expect(PAGE_CONFIG['artdeco-trading-management']).toBeUndefined()
      expect(PAGE_CONFIG['market-fund-flow']).toBeUndefined()
    })
  })

  describe('tab lookups', () => {
    it('returns undefined for standard routes, invalid tabs, and invalid routes', () => {
      expect(getTabConfig('dashboard', 'overview')).toBeUndefined()
      expect(getTabConfig('market-realtime', 'nonexistent-tab')).toBeUndefined()
      expect(getTabConfig('invalid-route', 'fund-flow')).toBeUndefined()
    })

    it('returns no generated tabs for the current split-page components', () => {
      const marketTabs = getTabsForComponent('Realtime.vue')
      const technicalTabs = getTabsForComponent('Technical.vue')

      expect(marketTabs).toEqual([])
      expect(technicalTabs).toEqual([])
      expect(getTabsForComponent('UnknownComponent.vue')).toEqual([])
    })
  })
})
