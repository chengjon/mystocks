export interface StorePolicy {
  capability: string
  owner: string
  sourceOfTruth: 'api' | 'realtime' | 'hybrid'
  cache: {
    enabled: boolean
    key?: string
    ttl: number
    strategy: 'memory' | 'sessionStorage' | 'localStorage'
  }
  loadingKey: string
  refresh: {
    updateInterval?: number
    forceRefreshAllowed: boolean
    staleAfterMs: number
  }
  realtime?: {
    channel: string
    transport: 'websocket'
  }
}

export const frontendStorePolicies = {
  tradingSignals: {
    capability: 'trading-signals',
    owner: 'frontend-platform',
    sourceOfTruth: 'hybrid',
    cache: { enabled: true, key: 'trading-signals', ttl: 60000, strategy: 'memory' },
    loadingKey: 'trading-signals-loading',
    refresh: { updateInterval: 10000, forceRefreshAllowed: true, staleAfterMs: 60000 },
    realtime: { channel: 'trading-signals', transport: 'websocket' },
  },
  riskAlerts: {
    capability: 'risk-alerts',
    owner: 'frontend-platform',
    sourceOfTruth: 'hybrid',
    cache: { enabled: true, key: 'risk-alerts', ttl: 30000, strategy: 'memory' },
    loadingKey: 'risk-alerts-loading',
    refresh: { updateInterval: 15000, forceRefreshAllowed: true, staleAfterMs: 30000 },
    realtime: { channel: 'risk-alerts', transport: 'websocket' },
  },
  technicalIndicators: {
    capability: 'technical-indicators',
    owner: 'frontend-platform',
    sourceOfTruth: 'api',
    cache: { enabled: true, key: 'technical-indicators', ttl: 300000, strategy: 'memory' },
    loadingKey: 'indicators-loading',
    refresh: { forceRefreshAllowed: true, staleAfterMs: 300000 },
  },
  monitoringWatchlists: {
    capability: 'monitoring-watchlists',
    owner: 'frontend-platform',
    sourceOfTruth: 'api',
    cache: { enabled: true, key: 'monitoring-watchlists', ttl: 1800000, strategy: 'sessionStorage' },
    loadingKey: 'watchlists-loading',
    refresh: { forceRefreshAllowed: true, staleAfterMs: 1800000 },
  },
  monitoringWatchlistStocks: {
    capability: 'monitoring-watchlist-stocks',
    owner: 'frontend-platform',
    sourceOfTruth: 'api',
    cache: { enabled: true, ttl: 300000, strategy: 'memory' },
    loadingKey: 'watchlist-stocks-loading',
    refresh: { forceRefreshAllowed: true, staleAfterMs: 300000 },
  },
} as const
