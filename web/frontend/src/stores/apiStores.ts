import { PiniaStoreFactory, createMarketDataStore, createReferenceDataStore } from '@/stores/storeFactory'
import { frontendStorePolicies } from '@/stores/storePolicies'
import { apiClient } from '@/api/apiClient'
import { tradingWebSocket, riskWebSocket } from '@/utils/webSocketManager'
import {
  extractMonitoringWatchlists,
  extractMonitoringWatchlistStocks,
} from '@/views/artdeco-pages/stock-management-tabs/stockManagementRouteData'

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

// Create monitoring watchlists store
export const useWatchlistsStore = PiniaStoreFactory.createApiStore({
  id: frontendStorePolicies.monitoringWatchlists.capability,
  endpoint: '/v1/monitoring/watchlists',
  cache: frontendStorePolicies.monitoringWatchlists.cache,
  loading: { enabled: true, key: frontendStorePolicies.monitoringWatchlists.loadingKey },
  request: () => apiClient.get('/v1/monitoring/watchlists'),
  transform: extractMonitoringWatchlists,
})

// Create watchlist stock details store with watchlist-aware cache keys
export const useWatchlistStocksStore = PiniaStoreFactory.createApiStore({
  id: frontendStorePolicies.monitoringWatchlistStocks.capability,
  endpoint: '/v1/monitoring/watchlists/:watchlistId/stocks',
  cache: frontendStorePolicies.monitoringWatchlistStocks.cache,
  loading: { enabled: true, key: frontendStorePolicies.monitoringWatchlistStocks.loadingKey },
  request: (params) => {
    const watchlistId = typeof (params as { watchlistId?: unknown } | undefined)?.watchlistId === 'string'
      ? (params as { watchlistId: string }).watchlistId
      : ''
    if (!watchlistId) {
      throw new Error('watchlistId is required')
    }
    return apiClient.get(`/v1/monitoring/watchlists/${watchlistId}/stocks`)
  },
  transform: extractMonitoringWatchlistStocks,
})

export function createMonitoringWatchlistActions() {
  return {
    createWatchlist(name: string) {
      return apiClient.post('/v1/monitoring/watchlists', {
        name,
        watchlist_type: 'manual',
      })
    },
    deleteWatchlist(watchlistId: string) {
      return apiClient.delete(`/v1/monitoring/watchlists/${watchlistId}`)
    },
    addStock(
      watchlistId: string,
      stock: string | {
        stock_code: string
        entry_price?: number | null
        entry_reason?: string | null
        stop_loss_price?: number | null
        target_price?: number | null
        weight?: number
      },
    ) {
      const payload = typeof stock === 'string' ? { stock_code: stock } : stock
      return apiClient.post(`/v1/monitoring/watchlists/${watchlistId}/stocks`, payload)
    },
    removeStock(watchlistId: string, symbol: string) {
      return apiClient.delete(`/v1/monitoring/watchlists/${watchlistId}/stocks/${symbol}`)
    },
  }
}

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
