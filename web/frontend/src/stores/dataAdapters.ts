import { createAdapter } from '@/utils/adapterUtils'

// Create data adapter for market quotes API response
export const marketQuotesAdapter = createAdapter({
  // Transform API response to standardized format
  transform: (apiData: any) => {
    if (!apiData || !Array.isArray(apiData)) return []

    return apiData.map((item: any) => ({
      symbol: item.symbol || item.code,
      name: item.name || item.symbol,
      price: parseFloat(item.price) || 0,
      change: parseFloat(item.change) || 0,
      changePercent: parseFloat(item.change_percent || item.changePercent) || 0,
      volume: parseInt(item.volume) || 0,
      amount: parseFloat(item.amount) || 0,
      high: parseFloat(item.high) || 0,
      low: parseFloat(item.low) || 0,
      open: parseFloat(item.open) || 0,
      close: parseFloat(item.close) || item.price || 0,
      timestamp: new Date(item.timestamp || Date.now()),
      market: item.market || 'unknown',
      status: item.status || 'active'
    }))
  },

  // Validate transformed data
  validate: (data: any[]) => {
    return data.every(item =>
      item.symbol &&
      typeof item.price === 'number' &&
      typeof item.change === 'number'
    )
  }
})

// Create data adapter for stock symbols reference data
export const stockSymbolsAdapter = createAdapter({
  transform: (apiData: any) => {
    if (!apiData || !Array.isArray(apiData)) return []

    return apiData.map((item: any) => ({
      symbol: item.symbol || item.code,
      name: item.name || item.symbol,
      exchange: item.exchange || 'UNKNOWN',
      sector: item.sector || item.industry || '其他',
      market: item.market || 'A股',
      status: item.status || 'active',
      listedDate: item.listed_date ? new Date(item.listed_date) : null,
      totalShares: parseFloat(item.total_shares) || null,
      circulatingShares: parseFloat(item.circulating_shares) || null
    }))
  },

  validate: (data: any[]) => {
    return data.every(item =>
      item.symbol &&
      item.name &&
      item.exchange
    )
  }
})

// Create data adapter for technical indicators
export const technicalIndicatorsAdapter = createAdapter({
  transform: (apiData: any) => {
    // Handle different API response formats
    const data = apiData.data || apiData.indicators || apiData

    if (!data) return null

    return {
      symbol: data.symbol || apiData.symbol,
      indicator: data.indicator || data.type,
      values: Array.isArray(data.values) ? data.values : [],
      timestamps: Array.isArray(data.timestamps) ? data.timestamps : [],
      params: data.params || {},
      metadata: {
        calculationTime: data.calculation_time || data.calcTime || 0,
        period: data.period || data.params?.period || 14,
        lastUpdated: new Date(data.last_updated || Date.now())
      }
    }
  },

  validate: (data: any) => {
    return data &&
           data.symbol &&
           data.indicator &&
           Array.isArray(data.values)
  }
})

// Create data adapter for trading history
export const tradingHistoryAdapter = createAdapter({
  transform: (apiData: any) => {
    if (!apiData || !Array.isArray(apiData)) return []

    return apiData.map((item: any) => ({
      id: item.id || item.order_id,
      symbol: item.symbol,
      type: item.type || item.order_type,
      side: item.side || (item.type === 'buy' ? 'buy' : 'sell'),
      quantity: parseInt(item.quantity) || 0,
      price: parseFloat(item.price) || 0,
      amount: parseFloat(item.amount) || (parseFloat(item.price) * parseInt(item.quantity)),
      status: item.status || 'unknown',
      timestamp: new Date(item.timestamp || item.created_at),
      fee: parseFloat(item.fee) || 0,
      exchange: item.exchange || 'unknown'
    }))
  },

  validate: (data: any[]) => {
    return data.every(item =>
      item.id &&
      item.symbol &&
      item.type &&
      typeof item.quantity === 'number' &&
      typeof item.price === 'number'
    )
  }
})