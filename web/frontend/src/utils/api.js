// Trade APIs wrapper
export default {
  // Portfolio endpoints
  getPortfolio() {
    return fetch('/api/trade/portfolio').then(r => r.json())
  },

  getPositions() {
    return fetch('/api/trade/positions').then(r => r.json())
  },

  getTrades(page = 1, pageSize = 20, filters = {}) {
    const params = new URLSearchParams({
      page,
      page_size: pageSize,
      ...filters
    })
    return fetch(`/api/trade/trades?${params}`).then(r => r.json())
  },

  getStatistics() {
    return fetch('/api/trade/statistics').then(r => r.json())
  },

  // Trade execution
  executeTrade(tradeData) {
    return fetch('/api/trade/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(tradeData)
    }).then(r => r.json())
  },

  // Trade management
  cancelTrade(tradeId) {
    return fetch(`/api/trade/${tradeId}`, {
      method: 'DELETE'
    }).then(r => r.json())
  }
}
