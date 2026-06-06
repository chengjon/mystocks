import test from "node:test"
import assert from "node:assert/strict"

import { buildStopLossRows, pickPrimaryStopLossWatchlist } from "../stopLossMonitorData.ts"

test("pickPrimaryStopLossWatchlist prefers active watchlists", () => {
  const selected = pickPrimaryStopLossWatchlist([
    { id: 2, name: "观察池", is_active: false },
    { id: 1, name: "核心止损监控", is_active: true },
  ])

  assert.equal(selected?.id, 1)
})

test("buildStopLossRows merges watchlist stocks with quotes payload", () => {
  const rows = buildStopLossRows(
    [
      {
        stock_code: "000001",
        entry_price: 12.4,
        stop_loss_price: 11.5,
      },
      {
        stock_code: "600519",
        entry_price: 1820,
        stop_loss_price: 1750,
      },
    ],
    {
      quotes: [
        {
          symbol: "000001",
          name: "平安银行",
          current_price: 12.8,
        },
        {
          symbol: "600519",
          name: "贵州茅台",
          price: 1850,
        },
      ],
    },
  )

  assert.equal(rows.length, 2)
  assert.equal(rows[0]?.name, "平安银行")
  assert.equal(rows[0]?.current_price, "12.80")
  assert.equal(rows[0]?.stop_price, "11.50")
  assert.equal(rows[0]?.distance, "11.30")
  assert.equal(rows[1]?.name, "贵州茅台")
})

test("buildStopLossRows falls back to entry price when quote payload is missing", () => {
  const rows = buildStopLossRows(
    [
      {
        stock_code: "300750",
        entry_price: 210.35,
        stop_loss_price: 198.0,
      },
    ],
    { quotes: [] },
  )

  assert.equal(rows.length, 1)
  assert.equal(rows[0]?.symbol, "300750")
  assert.equal(rows[0]?.name, "300750")
  assert.equal(rows[0]?.current_price, "210.35")
  assert.equal(rows[0]?.distance, "6.24")
})

test("buildStopLossRows ignores synthetic quote prices when entry price is available", () => {
  const rows = buildStopLossRows(
    [
      {
        stock_code: "600519",
        entry_price: 1820,
        stop_loss_price: 1750,
      },
    ],
    {
      quotes: [
        {
          symbol: "600519",
          name: "股票600519",
          price: 19.35,
        },
      ],
    },
  )

  assert.equal(rows[0]?.name, "600519")
  assert.equal(rows[0]?.current_price, "1820.00")
  assert.equal(rows[0]?.distance, "4.00")
})

test("buildStopLossRows marks rows without stop-loss policy as pending instead of pretending they are actively monitored", () => {
  const rows = buildStopLossRows(
    [
      {
        stock_code: "600519",
        stock_name: "贵州茅台",
        entry_price: 1820,
      },
    ],
    {
      quotes: [
        {
          symbol: "600519",
          name: "贵州茅台",
          current_price: 1805,
        },
      ],
    },
  )

  assert.equal(rows.length, 1)
  assert.equal(rows[0]?.symbol, "600519")
  assert.equal(rows[0]?.stop_price, "待接入")
  assert.equal(rows[0]?.distance, "待接入")
  assert.equal(rows[0]?.hasStopLossPolicy, false)
  assert.equal(rows[0]?.distanceValue, null)
})
