import test from "node:test"
import assert from "node:assert/strict"

import {
  buildWatchlistExportDocument,
  createStockManagementRouteActions,
  parseWatchlistImportDocument,
} from "../stockManagementRouteActions.ts"

test("stock management route actions call monitoring watchlist endpoints", async () => {
  const calls: Array<{ method: string; url: string; data?: unknown }> = []
  const actions = createStockManagementRouteActions({
    post: async (url, data) => {
      calls.push({ method: "POST", url, data })
      return { data: { id: 77, name: "新清单" } }
    },
    delete: async (url) => {
      calls.push({ method: "DELETE", url })
      return {}
    },
  })

  await actions.createWatchlist("新清单")
  await actions.removeStock("18", "600519.SH")

  assert.deepEqual(calls, [
    {
      method: "POST",
      url: "/v1/monitoring/watchlists",
      data: { name: "新清单", watchlist_type: "manual" },
    },
    {
      method: "DELETE",
      url: "/v1/monitoring/watchlists/18/stocks/600519.SH",
    },
  ])
})

test("buildWatchlistExportDocument includes active watchlist and stocks", () => {
  const doc = buildWatchlistExportDocument(
    [
      { id: "18", name: "成长股精选", stocks: [{}, {}] },
      { id: "16", name: "核心科技股", stocks: [] },
    ],
    "18",
    [{ symbol: "600519.SH", name: "贵州茅台", price: 1650 }],
  )

  assert.equal(doc.version, 1)
  assert.equal(doc.activeWatchlistId, "18")
  assert.equal(doc.watchlists.length, 2)
  assert.equal(doc.currentStocks[0]?.symbol, "600519.SH")
})

test("parseWatchlistImportDocument restores watchlists and stocks from exported JSON", () => {
  const parsed = parseWatchlistImportDocument(
    JSON.stringify({
      version: 1,
      activeWatchlistId: "18",
      watchlists: [{ id: "18", name: "成长股精选", stocks: [{}, {}] }],
      currentStocks: [{ symbol: "600519.SH", name: "贵州茅台" }],
    }),
  )

  assert.equal(parsed.activeWatchlistId, "18")
  assert.equal(parsed.watchlists.length, 1)
  assert.equal(parsed.currentStocks[0]?.symbol, "600519.SH")
})
