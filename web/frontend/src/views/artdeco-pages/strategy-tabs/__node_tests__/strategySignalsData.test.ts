import test from "node:test"
import assert from "node:assert/strict"

import { createStrategySignalsFromResponse } from "../strategySignalsData.ts"

test("createStrategySignalsFromResponse preserves direct timestamps for cross-day ordering", () => {
  const rows = createStrategySignalsFromResponse({
    data: [
      {
        symbol: "600519",
        name: "贵州茅台",
        type: "BUY",
        price: 1688.2,
        time: "09:35:12",
        strategy: "Northbound Momentum",
        created_at: "2026-04-25T09:35:12Z",
      },
      {
        symbol: "300750",
        name: "宁德时代",
        type: "SELL",
        price: 212.6,
        time: "15:01:02",
        strategy: "Breakdown Guard",
        created_at: "2026-04-26T15:01:02Z",
      },
    ],
  })

  assert.equal(rows.length, 2)
  assert.equal(rows[0]?.sortTimestamp, Date.parse("2026-04-25T09:35:12Z"))
  assert.equal(rows[1]?.sortTimestamp, Date.parse("2026-04-26T15:01:02Z"))
  assert.ok((rows[1]?.sortTimestamp ?? 0) > (rows[0]?.sortTimestamp ?? 0))
})

test("createStrategySignalsFromResponse falls back to date plus time when direct timestamps are absent", () => {
  const rows = createStrategySignalsFromResponse({
    items: [
      {
        symbol: "002594",
        name: "比亚迪",
        type: "HOLD",
        price: 258.3,
        time: "14:20:30",
        date: "2026-04-24",
        strategy: "Range Guard",
      },
      {
        symbol: "000001",
        name: "平安银行",
        type: "BUY",
        price: 12.8,
        time: "--:--:--",
        strategy: "Fallback",
      },
    ],
  })

  assert.equal(rows[0]?.sortTimestamp, Date.parse("2026-04-24T14:20:30"))
  assert.equal(rows[1]?.sortTimestamp, null)
})

test("createStrategySignalsFromResponse preserves optional signal detail when the live payload provides it", () => {
  const rows = createStrategySignalsFromResponse({
    records: [
      {
        signal_id: "sig-001",
        symbol: "600519",
        name: "贵州茅台",
        type: "BUY",
        price: 1688.2,
        time: "09:35:12",
        strategy: "Momentum Alpha",
        confidence: 0.82,
        reason: "MACD金叉",
        strength: "strong",
      },
    ],
  })

  assert.equal(rows[0]?.signalId, "sig-001")
  assert.equal(rows[0]?.confidence, 0.82)
  assert.equal(rows[0]?.reason, "MACD金叉")
  assert.equal(rows[0]?.strength, "strong")
})
