
/**
 * Vue Composables Index
 *
 * Central export point for all Vue 3 composables.
 * These composables provide reactive data management with:
 * - Automatic API integration
 * - Loading/error states
 * - Caching support
 * - Mock data fallback
 */

// Market Data Composables
export { useMarket, default as useMarketData } from './useMarket'

// Strategy Composables
export { useStrategy, default as useStrategyManagement } from './useStrategy'

// Trading Composables
export { useTrading, usePositions, default as useTradingManagement } from './useTrading'

// Kline Chart Composables
export { useKlineChart, default as useKlineChartManagement } from './useKlineChart'

// Real-time Data Composables
export { useSSE, default as useRealTimeData } from './useSSE'

// API Service Composables
export { useApiService, default as useApi } from './useApiService'
