interface WatchlistLike {
  id?: unknown
  is_active?: unknown
}

interface WatchlistStockLike {
  stock_code?: unknown
  name?: unknown
  entry_price?: unknown
  stop_loss_price?: unknown
}

interface QuoteLike {
  symbol?: unknown
  name?: unknown
  current_price?: unknown
  price?: unknown
}

export interface StopLossRow {
  symbol: string
  name: string
  current_price: string
  stop_price: string
  distance: string
}

function toFiniteNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value
  }

  if (typeof value === "string" && value.trim()) {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : null
  }

  return null
}

function formatPrice(value: number | null): string {
  return value === null ? "--" : value.toFixed(2)
}

function formatDistance(currentPrice: number | null, stopPrice: number | null): string {
  if (currentPrice === null || stopPrice === null || stopPrice <= 0) {
    return "--"
  }

  return (((currentPrice - stopPrice) / stopPrice) * 100).toFixed(2)
}

function extractRows(payload: unknown, collectionKeys: string[]): Record<string, unknown>[] {
  if (Array.isArray(payload)) {
    return payload.filter((item): item is Record<string, unknown> => !!item && typeof item === "object")
  }

  if (!payload || typeof payload !== "object") {
    return []
  }

  const candidate = payload as Record<string, unknown>

  for (const key of collectionKeys) {
    const collection = candidate[key]
    if (Array.isArray(collection)) {
      return collection.filter((item): item is Record<string, unknown> => !!item && typeof item === "object")
    }
    if (collection && typeof collection === "object") {
      const nested = collection as Record<string, unknown>
      if (Array.isArray(nested.data)) {
        return nested.data.filter((item): item is Record<string, unknown> => !!item && typeof item === "object")
      }
      if (Array.isArray(nested.items)) {
        return nested.items.filter((item): item is Record<string, unknown> => !!item && typeof item === "object")
      }
    }
  }

  if (Array.isArray(candidate.data)) {
    return candidate.data.filter((item): item is Record<string, unknown> => !!item && typeof item === "object")
  }

  if (Array.isArray(candidate.items)) {
    return candidate.items.filter((item): item is Record<string, unknown> => !!item && typeof item === "object")
  }

  return []
}

function extractWatchlists(payload: unknown): WatchlistLike[] {
  return extractRows(payload, ["watchlists", "items", "data"]) as WatchlistLike[]
}

function extractWatchlistStocks(payload: unknown): WatchlistStockLike[] {
  return extractRows(payload, ["stocks", "items", "data"]) as WatchlistStockLike[]
}

function extractQuotes(payload: unknown): QuoteLike[] {
  return extractRows(payload, ["quotes", "items", "data"]) as QuoteLike[]
}

export function pickPrimaryStopLossWatchlist(payload: unknown): { id: number } | null {
  const watchlists = extractWatchlists(payload)
    .map((row) => ({
      id: toFiniteNumber(row.id),
      isActive: row.is_active !== false,
    }))
    .filter((row): row is { id: number; isActive: boolean } => row.id !== null)

  watchlists.sort((left, right) => Number(right.isActive) - Number(left.isActive))

  if (watchlists.length === 0) {
    return null
  }

  return { id: watchlists[0].id }
}

export function buildStopLossRows(stocksPayload: unknown, quotesPayload: unknown): StopLossRow[] {
  const stocks = extractWatchlistStocks(stocksPayload)
  const quoteMap = new Map<string, QuoteLike>()

  for (const quote of extractQuotes(quotesPayload)) {
    const symbol = typeof quote.symbol === "string" ? quote.symbol : ""
    if (symbol) {
      quoteMap.set(symbol, quote)
    }
  }

  return stocks.map((stock) => {
    const symbol = typeof stock.stock_code === "string" ? stock.stock_code : ""
    const quote = symbol ? quoteMap.get(symbol) : undefined
    const quoteName = typeof quote?.name === "string" ? quote.name : ""
    const isSyntheticQuote = quoteName === `股票${symbol}`
    const currentPrice = isSyntheticQuote
      ? toFiniteNumber(stock.entry_price ?? quote?.current_price ?? quote?.price)
      : toFiniteNumber(quote?.current_price ?? quote?.price ?? stock.entry_price)
    const stopPrice = toFiniteNumber(stock.stop_loss_price)

    return {
      symbol,
      name:
        (!isSyntheticQuote && typeof quote?.name === "string" && quote.name) ||
        (typeof stock.name === "string" && stock.name) ||
        symbol,
      current_price: formatPrice(currentPrice),
      stop_price: formatPrice(stopPrice),
      distance: formatDistance(currentPrice, stopPrice),
    }
  })
}
