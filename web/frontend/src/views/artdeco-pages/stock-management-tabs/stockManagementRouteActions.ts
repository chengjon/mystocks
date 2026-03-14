export interface WatchlistExportDocument {
  version: number
  activeWatchlistId: string
  watchlists: Array<{ id: string; name: string; stocks: unknown[] }>
  currentStocks: unknown[]
}

type Transport = {
  post: (url: string, data?: unknown) => Promise<unknown>
  delete: (url: string) => Promise<unknown>
}

export function createStockManagementRouteActions(transport: Transport) {
  return {
    async createWatchlist(name: string) {
      return transport.post('/v1/monitoring/watchlists', {
        name,
        watchlist_type: 'manual',
      })
    },
    async removeStock(watchlistId: string, symbol: string) {
      return transport.delete(`/v1/monitoring/watchlists/${watchlistId}/stocks/${symbol}`)
    },
  }
}

export function buildWatchlistExportDocument(
  watchlists: Array<{ id: string; name: string; stocks: unknown[] }>,
  activeWatchlistId: string,
  currentStocks: unknown[],
): WatchlistExportDocument {
  return {
    version: 1,
    activeWatchlistId,
    watchlists,
    currentStocks,
  }
}

export function parseWatchlistImportDocument(raw: string): WatchlistExportDocument {
  const parsed = JSON.parse(raw) as Partial<WatchlistExportDocument>
  return {
    version: 1,
    activeWatchlistId: typeof parsed.activeWatchlistId === 'string' ? parsed.activeWatchlistId : '',
    watchlists: Array.isArray(parsed.watchlists) ? parsed.watchlists : [],
    currentStocks: Array.isArray(parsed.currentStocks) ? parsed.currentStocks : [],
  }
}
