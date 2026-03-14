import test from "node:test"
import assert from "node:assert/strict"

import { extractDragonTigerRows } from "../dragonTigerData.ts"

test("extractDragonTigerRows maps v2 lhb payload into table rows", () => {
  const rows = extractDragonTigerRows([
    {
      trade_date: "2026-03-13",
      symbol: "000001",
      name: "平安银行",
      reason: "普通席位买入",
      buy_amount: 100000000,
      sell_amount: 20000000,
      net_amount: 80000000,
      turnover_rate: 12.3456,
      institution_buy: 0,
      institution_sell: 0,
    },
  ])

  assert.equal(rows.length, 1)
  assert.equal(rows[0]?.tradeDate, "2026-03-13")
  assert.equal(rows[0]?.stockInfo, "平安银行 (000001)")
  assert.equal(rows[0]?.buyAmount, "+1.00亿")
  assert.equal(rows[0]?.netBuy, "+0.80亿")
  assert.equal(rows[0]?.turnoverRate, "12.35%")
})

test("extractDragonTigerRows filters by sell and institution modes", () => {
  const payload = [
    {
      trade_date: "2026-03-13",
      symbol: "000001",
      name: "平安银行",
      reason: "普通席位买入",
      buy_amount: 100000000,
      sell_amount: 20000000,
      net_amount: 80000000,
      turnover_rate: 12.3,
      institution_buy: 0,
      institution_sell: 0,
    },
    {
      trade_date: "2026-03-13",
      symbol: "000002",
      name: "万科A",
      reason: "3家机构卖出",
      buy_amount: 10000000,
      sell_amount: 60000000,
      net_amount: -50000000,
      turnover_rate: 8.2,
      institution_buy: 0,
      institution_sell: 1,
    },
  ]

  assert.equal(extractDragonTigerRows(payload, "sell").length, 1)
  assert.equal(extractDragonTigerRows(payload, "institution").length, 1)
})
