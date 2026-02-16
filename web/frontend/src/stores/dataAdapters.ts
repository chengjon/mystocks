import { createAdapter } from '@/utils/adapterUtils'

// Type definitions for API response items
interface MarketQuoteItem {
  symbol?: string
  code?: string
  name?: string
  price?: string | number
  change?: string | number
  change_percent?: string | number
  changePercent?: string | number
  volume?: string | number
  amount?: string | number
  high?: string | number
  low?: string | number
  open?: string | number
  close?: string | number
  timestamp?: string | number
  market?: string
  status?: string
}

interface StockSymbolItem {
  symbol?: string
  code?: string
  name?: string
  exchange?: string
  sector?: string
  industry?: string
  market?: string
  status?: string
  listed_date?: string
  total_shares?: string | number
  circulating_shares?: string | number
}

interface TechnicalIndicatorData {
  symbol?: string
  indicator?: string
  type?: string
  values?: unknown[]
  timestamps?: unknown[]
  params?: Record<string, unknown>
  calculation_time?: number
  calcTime?: number
  period?: number
  last_updated?: string | number
}

interface TradingHistoryItem {
  id?: string
  order_id?: string
  symbol?: string
  type?: string
  order_type?: string
  side?: string
  quantity?: string | number
  price?: string | number
  amount?: string | number
  status?: string
  timestamp?: string | number
  created_at?: string | number
  fee?: string | number
  exchange?: string
}

// Create data adapter for market quotes API response
export const marketQuotesAdapter = createAdapter({
  // Transform API response to standardized format
  transform: (apiData: unknown) => {
    if (!apiData || !Array.isArray(apiData)) return []

    return (apiData as MarketQuoteItem[]).map((item: MarketQuoteItem) => ({
      symbol: item.symbol || item.code || '',
      name: item.name || item.symbol || '',
      price: parseFloat(String(item.price)) || 0,
      change: parseFloat(String(item.change)) || 0,
      changePercent: parseFloat(String(item.change_percent || item.changePercent)) || 0,
      volume: parseInt(String(item.volume)) || 0,
      amount: parseFloat(String(item.amount)) || 0,
      high: parseFloat(String(item.high)) || 0,
      low: parseFloat(String(item.low)) || 0,
      open: parseFloat(String(item.open)) || 0,
      close: parseFloat(String(item.close || item.price)) || 0,
      timestamp: new Date(item.timestamp || Date.now()),
      market: item.market || 'unknown',
      status: item.status || 'active'
    }))
  },

  // Validate transformed data
  validate: (data: unknown[]) => {
    return data.every((item: unknown) => {
      const d = item as { symbol?: string; price?: number; change?: number }
      return d.symbol && typeof d.price === 'number' && typeof d.change === 'number'
    })
  }
})

// Create data adapter for stock symbols reference data
export const stockSymbolsAdapter = createAdapter({
  transform: (apiData: unknown) => {
    if (!apiData || !Array.isArray(apiData)) return []

    return (apiData as StockSymbolItem[]).map((item: StockSymbolItem) => ({
      symbol: item.symbol || item.code || '',
      name: item.name || item.symbol || '',
      exchange: item.exchange || 'UNKNOWN',
      sector: item.sector || item.industry || '其他',
      market: item.market || 'A股',
      status: item.status || 'active',
      listedDate: item.listed_date ? new Date(item.listed_date) : null,
      totalShares: parseFloat(String(item.total_shares)) || null,
      circulatingShares: parseFloat(String(item.circulating_shares)) || null
    }))
  },

  validate: (data: unknown[]) => {
    return data.every((item: unknown) => {
      const d = item as { symbol?: string; name?: string; exchange?: string }
      return d.symbol && d.name && d.exchange
    })
  }
})

// Create data adapter for technical indicators
export const technicalIndicatorsAdapter = createAdapter({
  transform: (apiData: unknown) => {
    if (!apiData) return null

    const raw = apiData as Record<string, unknown>
    // Handle different API response formats
    const data = (raw.data || raw.indicators || apiData) as TechnicalIndicatorData

    if (!data) return null

    return {
      symbol: data.symbol || (raw.symbol as string) || '',
      indicator: data.indicator || data.type || '',
      values: Array.isArray(data.values) ? data.values : [],
      timestamps: Array.isArray(data.timestamps) ? data.timestamps : [],
      params: data.params || {},
      metadata: {
        calculationTime: data.calculation_time || data.calcTime || 0,
        period: data.period || (data.params?.period as number) || 14,
        lastUpdated: new Date(data.last_updated || Date.now())
      }
    }
  },

  validate: (data: unknown) => {
    if (!data) return false
    const d = data as { symbol?: string; indicator?: string; values?: unknown[] }
    return !!(d.symbol && d.indicator && Array.isArray(d.values))
  }
})

// Create data adapter for trading history
export const tradingHistoryAdapter = createAdapter({
  transform: (apiData: unknown) => {
    if (!apiData || !Array.isArray(apiData)) return []

    return (apiData as TradingHistoryItem[]).map((item: TradingHistoryItem) => ({
      id: item.id || item.order_id || '',
      symbol: item.symbol || '',
      type: item.type || item.order_type || '',
      side: item.side || (item.type === 'buy' ? 'buy' : 'sell'),
      quantity: parseInt(String(item.quantity)) || 0,
      price: parseFloat(String(item.price)) || 0,
      amount: parseFloat(String(item.amount)) || (parseFloat(String(item.price)) * parseInt(String(item.quantity))),
      status: item.status || 'unknown',
      timestamp: new Date(item.timestamp || item.created_at || Date.now()),
      fee: parseFloat(String(item.fee)) || 0,
      exchange: item.exchange || 'unknown'
    }))
  },

  validate: (data: unknown[]) => {
    return data.every((item: unknown) => {
      const d = item as { id?: string; symbol?: string; type?: string; quantity?: number; price?: number }
      return d.id && d.symbol && d.type && typeof d.quantity === 'number' && typeof d.price === 'number'
    })
  }
})