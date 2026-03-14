import test from "node:test"
import assert from "node:assert/strict"

import {
  extractMonitoringWatchlists,
  extractMonitoringWatchlistStocks,
  extractPortfolioMonitorRows,
  extractPortfolioMonitorStats,
} from "../stockManagementRouteData.ts"

test("extractMonitoringWatchlists maps monitoring watchlist summary rows for route tabs", () => {
  const rows = extractMonitoringWatchlists({
    data: [
      { id: 18, name: "成长股精选", stocks_count: 0 },
      { id: 16, name: "核心科技股", stocks_count: 2 },
    ],
  })

  assert.deepEqual(rows, [
    { id: "18", name: "成长股精选", stocks: [] },
    { id: "16", name: "核心科技股", stocks: [{}, {}] },
  ])
})

test("extractMonitoringWatchlistStocks maps watchlist stock rows for display table", () => {
  const rows = extractMonitoringWatchlistStocks({
    data: [
      { stock_code: "600519.SH", entry_price: 1650, weight: 0.4 },
      { stock_code: "000858.SZ", entry_price: 145, weight: 0.2 },
    ],
  })

  assert.deepEqual(rows, [
    {
      symbol: "600519.SH",
      name: "600519.SH",
      price: 1650,
      change: "--",
      volume: "--",
      weight: "40.00%",
    },
    {
      symbol: "000858.SZ",
      name: "000858.SZ",
      price: 145,
      change: "--",
      volume: "--",
      weight: "20.00%",
    },
  ])
})

test("extractPortfolioMonitorRows maps /v1/trade/positions payload to portfolio rows", () => {
  const rows = extractPortfolioMonitorRows({
    data: {
      positions: [
        {
          symbol: "600519.SH",
          symbol_name: "贵州茅台",
          quantity: 500,
          cost_price: "1650.00",
          current_price: "1750.00",
          profit_loss: "50000.00",
        },
      ],
    },
  })

  assert.deepEqual(rows, [
    {
      symbol: "600519.SH",
      name: "贵州茅台",
      quantity: 500,
      cost: 1650,
      price: 1750,
      pnl: 50000,
    },
  ])
})

test("extractPortfolioMonitorStats derives cards from /v1/trade/positions payload", () => {
  const stats = extractPortfolioMonitorStats({
    data: {
      positions: [
        { market_value: "875000.00" },
        { market_value: "150000.00" },
      ],
      total_market_value: "1025000.00",
      total_profit_loss: "55000.00",
      total_profit_loss_percent: 5.67,
    },
  })

  assert.deepEqual(stats, {
    totalAssets: "¥1,025,000",
    totalAssetsChange: 5.67,
    todayPnl: "+¥55,000",
    todayPnlChange: 5.67,
    positionCount: 2,
    positionCountLabel: "2 个",
    totalMarketValue: "¥1,025,000",
  })
})
