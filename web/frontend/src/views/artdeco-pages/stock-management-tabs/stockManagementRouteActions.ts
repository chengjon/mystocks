export interface WatchlistExportDocument {
  version: number
  activeWatchlistId: string
  watchlists: Array<{ id: string; name: string; stocks: unknown[] }>
  currentStocks: unknown[]
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
