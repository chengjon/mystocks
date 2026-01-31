import { PiniaStoreFactory, createMarketDataStore, createReferenceDataStore } from '@/stores/storeFactory'
import { tradingWebSocket, riskWebSocket } from '@/utils/webSocketManager'

// Factory-created stores using PiniaStoreFactory for standardized API data management
// These complement the existing complex stores with simple, consistent patterns

// Create market data store for real-time quotes using factory
export const useMarketQuotesStore = createMarketDataStore(
  'market-quotes',
  '/api/market/quotes'
)

// Create real-time trading signals store
export const useTradingSignalsStore = PiniaStoreFactory.createRealtimeStore({
  id: 'trading-signals',
  endpoint: '/api/trading/signals',
  method: 'GET',
  cache: { enabled: true, key: 'trading-signals', ttl: 60000, strategy: 'memory' }, // 1 min
  loading: { enabled: true, key: 'trading-signals-loading' },
  wsManager: tradingWebSocket,
  wsChannel: 'trading-signals',
  updateInterval: 10000, // 10 seconds polling fallback
})

// Create real-time risk alerts store
export const useRiskAlertsStore = PiniaStoreFactory.createRealtimeStore({
  id: 'risk-alerts',
  endpoint: '/api/risk/alerts',
  method: 'GET',
  cache: { enabled: true, key: 'risk-alerts', ttl: 30000, strategy: 'memory' }, // 30 sec
  loading: { enabled: true, key: 'risk-alerts-loading' },
  wsManager: riskWebSocket,
  wsChannel: 'risk-alerts',
  updateInterval: 15000, // 15 seconds polling fallback
})

// Create reference data store for stock symbols
export const useStockSymbolsStore = createReferenceDataStore(
  'stock-symbols',
  '/api/market/symbols'
)

// Create reference data store for market sectors
export const useMarketSectorsStore = createReferenceDataStore(
  'market-sectors',
  '/api/market/sectors'
)

// Create user data store for watchlists
export const useWatchlistsStore = PiniaStoreFactory.createApiStore({
  id: 'user-watchlists',
  endpoint: '/api/user/watchlists',
  cache: { enabled: true, key: 'user-watchlists', ttl: 1800000, strategy: 'sessionStorage' }, // 30 min
  loading: { enabled: true, key: 'watchlists-loading' },
})

// Create technical indicators store
export const useTechnicalIndicatorsStore = PiniaStoreFactory.createApiStore({
  id: 'technical-indicators',
  endpoint: '/api/analysis/indicators',
  method: 'POST',
  cache: { enabled: true, key: 'technical-indicators', ttl: 300000, strategy: 'memory' }, // 5 min
  loading: { enabled: true, key: 'indicators-loading' },
})

// Create paginated store for trading history
export const useTradingHistoryStore = PiniaStoreFactory.createPaginatedStore({
  id: 'trading-history',
  endpoint: '/api/trading/history',
  pageSize: 20,
  cache: { enabled: true, key: 'trading-history', ttl: 600000, strategy: 'memory' }, // 10 min
  loading: { enabled: true, key: 'trading-history-loading' },
})