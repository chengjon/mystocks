/**
 * Enhanced Market Data Store with IndexedDB Integration
 * Implements intelligent caching strategy: IndexedDB → Network → Fallback
 */

import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import { indexedDB } from '@/utils/indexedDB'
import { tradingApiManager } from '@/services/TradingApiManager'
import { workersManager } from '@/utils/workersManager'
import type { MarketOverview } from '@/services/TradingApiManager'
import type { MarketData } from '@/utils/indexedDB'
import type { TechnicalIndicatorResult } from '@/utils/workersManager'

interface MarketAnalysis {
    trend?: string
    sentiment?: number
    volatility?: number
    volume?: number
    [key: string]: any
}

interface CacheMetadata {
    lastFetchTime: number
    expiresAt: number
    isStale: boolean
    source: 'indexeddb' | 'network' | 'cache'
}

interface MarketState {
    marketOverview: MarketOverview | null
    marketAnalysis: MarketAnalysis | null
    lastUpdateTime: string
    cacheMetadata: CacheMetadata | null
    isOnline: boolean
    syncStatus: 'idle' | 'syncing' | 'error'
}

export const useMarketDataStore = defineStore('marketData', () => {
    const state = reactive<MarketState>({
        marketOverview: null,
        marketAnalysis: null,
        lastUpdateTime: new Date().toLocaleTimeString('zh-CN'),
        cacheMetadata: null,
        isOnline: navigator.onLine,
        syncStatus: 'idle'
    })

    // Computed properties
    const isCacheValid = computed(() => {
        if (!state.cacheMetadata) return false
        return Date.now() < state.cacheMetadata.expiresAt && !state.cacheMetadata.isStale
    })

    const cacheAge = computed(() => {
        if (!state.cacheMetadata) return null
        return Date.now() - state.cacheMetadata.lastFetchTime
    })

    const canUseCache = computed(() => {
        return indexedDB && state.isOnline
    })

    // Online/offline detection
    const updateOnlineStatus = () => {
        state.isOnline = navigator.onLine
    }

    window.addEventListener('online', updateOnlineStatus)
    window.addEventListener('offline', updateOnlineStatus)

    // ============ Core Data Loading Functions ============

    /**
     * Load market overview with intelligent caching
     * Strategy: IndexedDB → Network → Fallback
     */
    const loadMarketOverview = async (forceRefresh: boolean = false) => {
        state.syncStatus = 'syncing'

        try {
            let data: MarketOverview | null = null
            let source: 'indexeddb' | 'network' | 'cache' = 'network'

            // Strategy 1: Try IndexedDB cache first (unless force refresh)
            if (!forceRefresh && canUseCache.value) {
                try {
                    const cachedData = await indexedDB.getCache<MarketOverview>('market_overview')
                    if (cachedData && isCacheValid.value) {
                        data = cachedData
                        source = 'indexeddb'
                        console.log('📦 Loaded market overview from IndexedDB cache')
                    }
                } catch (error) {
                    console.warn('⚠️ IndexedDB cache read failed:', error)
                }
            }

            // Strategy 2: Fetch from network if no valid cache or force refresh
            if (!data || forceRefresh) {
                try {
                    data = await tradingApiManager.getMarketOverview()
                    source = 'network'
                    console.log('🌐 Fetched market overview from network')

                    // Cache the fresh data
                    if (canUseCache.value && data) {
                        await indexedDB.setCache('market_overview', data, 300) // 5 minutes TTL
                        console.log('💾 Cached market overview to IndexedDB')
                    }
                } catch (error) {
                    console.warn('❌ Network fetch failed:', error)

                    // Strategy 3: Use stale cache as fallback
                    if (!data && canUseCache.value) {
                        try {
                            const staleData = await indexedDB.getCache<MarketOverview>('market_overview')
                            if (staleData) {
                                data = staleData
                                source = 'cache'
                                console.log('📋 Using stale cache as fallback')
                            }
                        } catch (staleError) {
                            console.warn('⚠️ Stale cache fallback failed:', staleError)
                        }
                    }
                }
            }

            // Update state
            if (data) {
                state.marketOverview = data
                state.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')
                state.cacheMetadata = {
                    lastFetchTime: Date.now(),
                    expiresAt: Date.now() + (5 * 60 * 1000), // 5 minutes
                    isStale: source === 'cache',
                    source
                }
            }

            state.syncStatus = 'idle'

        } catch (error) {
            console.error('❌ Market overview loading failed:', error)
            state.syncStatus = 'error'
        }
    }

    /**
     * Load market analysis data
     */
    const loadMarketAnalysis = async (forceRefresh: boolean = false) => {
        state.syncStatus = 'syncing'

        try {
            // Similar caching strategy for market analysis
            let data: MarketAnalysis | null = null

            // Try IndexedDB cache first
            if (!forceRefresh && canUseCache.value) {
                data = await indexedDB.getCache<MarketAnalysis>('market_analysis')
            }

            // Fetch from network if needed
            if (!data || forceRefresh) {
                // For now, generate mock analysis data
                // In real implementation, this would call an API
                data = {
                    trend: 'bullish',
                    sentiment: 0.75,
                    volatility: 0.23,
                    volume: 1250000000
                }

                // Cache the data
                if (canUseCache.value) {
                    await indexedDB.setCache('market_analysis', data, 600) // 10 minutes TTL
                }
            }

            state.marketAnalysis = data
            state.syncStatus = 'idle'

        } catch (error) {
            console.error('❌ Market analysis loading failed:', error)
            state.syncStatus = 'error'
        }
    }

    // ============ Stock-Specific Data Functions ============

    /**
     * Load stock data for a specific symbol
     */
    const loadStockData = async (symbol: string, forceRefresh: boolean = false) => {
        try {
            let stockData: MarketData | null = null

            // Try IndexedDB first
            if (!forceRefresh && canUseCache.value) {
                stockData = await indexedDB.getMarketData(symbol)
            }

            // Fetch from network if needed
            if (!stockData || forceRefresh) {
                // In real implementation, this would call an API
                // For now, create mock data
                const mockData: MarketData = {
                    symbol,
                    timestamp: Date.now(),
                    price: Math.random() * 100 + 50,
                    volume: Math.floor(Math.random() * 1000000),
                    high: Math.random() * 100 + 55,
                    low: Math.random() * 100 + 45,
                    open: Math.random() * 100 + 50,
                    close: Math.random() * 100 + 50
                }

                stockData = mockData

                // Cache to IndexedDB
                if (canUseCache.value) {
                    await indexedDB.saveMarketData(stockData)
                }
            }

            return stockData

        } catch (error) {
            console.error(`❌ Failed to load stock data for ${symbol}:`, error)
            return null
        }
    }

    /**
     * Load technical indicators for a symbol using Web Workers
     */
    const loadTechnicalIndicators = async (symbol: string, indicator: string, params: Record<string, any> = {}) => {
        try {
            const cacheKey = `indicator_${symbol}_${indicator}_${JSON.stringify(params)}`

            // Try cache first
            if (canUseCache.value) {
                const cached = await indexedDB.getCache<TechnicalIndicatorResult>(`indicator_${cacheKey}`)
                if (cached) {
                    console.log(`📦 Loaded ${indicator} for ${symbol} from IndexedDB cache`)
                    return cached
                }
            }

            // Get historical data for calculation
            const historicalData = await getHistoricalDataForIndicator(symbol, indicator, params)
            if (!historicalData || historicalData.length === 0) {
                throw new Error(`No historical data available for ${symbol}`)
            }

            console.log(`🔢 Calculating ${indicator} for ${symbol} using Web Worker...`)

            // Calculate indicators using Web Worker
            const result: TechnicalIndicatorResult = await workersManager.calculateIndicator(
                indicator,
                historicalData,
                params,
                symbol
            )

            console.log(`✅ Successfully calculated ${indicator} for ${symbol} (${result.metadata.calculationTime}ms)`)

            // Cache result
            if (canUseCache.value) {
                await indexedDB.setCache(cacheKey, result, 1800) // 30 minutes

                // Convert TechnicalIndicatorResult to TechnicalIndicator format for storage
                const indicatorData = {
                    symbol: result.symbol,
                    indicator: result.indicator,
                    params: params || {},
                    values: result.data as number[],
                    timestamp: result.metadata.timestamp
                }
                await indexedDB.saveTechnicalIndicator(indicatorData)
                console.log(`💾 Cached ${indicator} result for ${symbol}`)
            }

            return result

        } catch (error) {
            console.error(`❌ Failed to load technical indicators for ${symbol}:`, error)
            return null
        }
    }

    /**
     * Get historical data required for indicator calculation
     */
    const getHistoricalDataForIndicator = async (
        symbol: string,
        indicator: string,
        params: Record<string, any>
    ): Promise<any[]> => {
        // Determine required data points based on indicator and parameters
        const period = params.period || getDefaultPeriodForIndicator(indicator)

        // Get extra data for warmup periods (typically 50% more than needed)
        const requiredPoints = Math.max(period * 1.5, 100)

        try {
            // Try to get from IndexedDB cache first
            if (canUseCache.value) {
                // Get all market data and filter by symbol
                const allMarketData = await indexedDB.getAllMarketData()
                const symbolData = allMarketData
                    .filter(d => d.symbol === symbol)
                    .sort((a, b) => a.timestamp - b.timestamp)
                    .slice(-requiredPoints) // Get the most recent N points

                if (symbolData && symbolData.length >= period) {
                    console.log(`📊 Using cached historical data for ${symbol} (${symbolData.length} points)`)
                    return symbolData
                }
            }

            // If no cached data, we need to fetch from network
            // This is a placeholder - in real implementation, this would call an API
            console.warn(`⚠️ No cached historical data for ${symbol}, using mock data for demonstration`)

            // Generate mock historical data for demonstration
            const mockData = Array.from({ length: requiredPoints }, (_, i) => {
                const open = 100 + Math.random() * 20
                const close = 100 + Math.random() * 20
                return {
                    timestamp: Date.now() - (requiredPoints - i) * 24 * 60 * 60 * 1000, // Daily data
                    symbol,
                    open,
                    high: Math.max(open, close) + Math.random() * 5,
                    low: Math.min(open, close) - Math.random() * 5,
                    close,
                    price: close, // Add price field (using close as price)
                    volume: Math.floor(Math.random() * 1000000)
                }
            }).sort((a, b) => a.timestamp - b.timestamp)

            // Cache the mock data for future use
            if (canUseCache.value) {
                for (const dataPoint of mockData) {
                    await indexedDB.saveMarketData(dataPoint)
                }
            }

            return mockData

        } catch (error) {
            console.error(`❌ Failed to get historical data for ${symbol}:`, error)
            return []
        }
    }

    /**
     * Get default period for indicator type
     */
    const getDefaultPeriodForIndicator = (indicator: string): number => {
        const defaults: Record<string, number> = {
            'SMA': 20,
            'EMA': 20,
            'RSI': 14,
            'MACD': 26, // Uses 26 for main period
            'BBANDS': 20,
            'STOCH': 14,
            'WILLIAMS_R': 14,
            'ATR': 14
        }
        return defaults[indicator.toUpperCase()] || 14
    }

    // ============ Utility Functions ============

    /**
     * Refresh all cached data
     */
    const refreshAllData = async () => {
        await Promise.all([
            loadMarketOverview(true),
            loadMarketAnalysis(true)
        ])
    }

    /**
     * Clear all cached data
     */
    const clearCache = async () => {
        try {
            await indexedDB.clearAllData()
            state.marketOverview = null
            state.marketAnalysis = null
            state.cacheMetadata = null
            console.log('🗑️ All cached market data cleared')
        } catch (error) {
            console.error('❌ Failed to clear cache:', error)
        }
    }

    /**
     * Get cache statistics
     */
    const getCacheStats = async () => {
        try {
            const stats = await indexedDB.getStats()
            return {
                indexeddb: stats,
                store: {
                    marketOverview: !!state.marketOverview,
                    marketAnalysis: !!state.marketAnalysis,
                    cacheAge: cacheAge.value,
                    isCacheValid: isCacheValid.value
                }
            }
        } catch (error) {
            console.error('❌ Failed to get cache stats:', error)
            return null
        }
    }

    // ============ Initialization ============

    // Auto-load data on store creation
    setTimeout(() => {
        loadMarketOverview()
        loadMarketAnalysis()
    }, 100)

    return {
        // State
        state,
        isCacheValid,
        cacheAge,
        canUseCache,

        // Core functions
        loadMarketOverview,
        loadMarketAnalysis,
        loadStockData,
        loadTechnicalIndicators,

        // Utility functions
        refreshAllData,
        clearCache,
        getCacheStats,
        getHistoricalDataForIndicator,
        getDefaultPeriodForIndicator,

        // Online status
        updateOnlineStatus
    }
})