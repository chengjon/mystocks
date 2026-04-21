import { PiniaStoreFactory, createMarketDataStore, createReferenceDataStore } from '@/stores/storeFactory'
import { frontendStorePolicies } from '@/stores/storePolicies'
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
  id: frontendStorePolicies.tradingSignals.capability,
  endpoint: '/api/trading/signals',
  method: 'GET',
  cache: frontendStorePolicies.tradingSignals.cache,
  loading: { enabled: true, key: frontendStorePolicies.tradingSignals.loadingKey },
  wsManager: tradingWebSocket,
  wsChannel: frontendStorePolicies.tradingSignals.realtime?.channel,
  updateInterval: frontendStorePolicies.tradingSignals.refresh.updateInterval,
})

// Create real-time risk alerts store
export const useRiskAlertsStore = PiniaStoreFactory.createRealtimeStore({
  id: frontendStorePolicies.riskAlerts.capability,
  endpoint: '/api/risk/alerts',
  method: 'GET',
  cache: frontendStorePolicies.riskAlerts.cache,
  loading: { enabled: true, key: frontendStorePolicies.riskAlerts.loadingKey },
  wsManager: riskWebSocket,
  wsChannel: frontendStorePolicies.riskAlerts.realtime?.channel,
  updateInterval: frontendStorePolicies.riskAlerts.refresh.updateInterval,
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
  id: frontendStorePolicies.userWatchlists.capability,
  endpoint: '/api/user/watchlists',
  cache: frontendStorePolicies.userWatchlists.cache,
  loading: { enabled: true, key: frontendStorePolicies.userWatchlists.loadingKey },
})

// Create technical indicators store
export const useTechnicalIndicatorsStore = PiniaStoreFactory.createApiStore({
  id: frontendStorePolicies.technicalIndicators.capability,
  endpoint: '/api/analysis/indicators',
  method: 'POST',
  cache: frontendStorePolicies.technicalIndicators.cache,
  loading: { enabled: true, key: frontendStorePolicies.technicalIndicators.loadingKey },
})

// Create paginated store for trading history
export const useTradingHistoryStore = PiniaStoreFactory.createPaginatedStore({
  id: 'trading-history',
  endpoint: '/api/trading/history',
  pageSize: 20,
  cache: { enabled: true, key: 'trading-history', ttl: 600000, strategy: 'memory' }, // 10 min
  loading: { enabled: true, key: 'trading-history-loading' },
})
