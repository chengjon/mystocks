import test from "node:test"
import assert from "node:assert/strict"

import {
  buildWatchlistExportDocument,
  parseWatchlistImportDocument,
} from "../stockManagementRouteActions.ts"

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
