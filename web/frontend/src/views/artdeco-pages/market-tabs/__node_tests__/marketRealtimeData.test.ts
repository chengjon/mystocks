import test from "node:test"
import assert from "node:assert/strict"

import { extractRealtimeMarketOverview } from "../marketRealtimeData.ts"

test("extractRealtimeMarketOverview reads rows from quote list payload", () => {
  const overview = extractRealtimeMarketOverview({
    quotes: [
      {
        symbol: "000001",
        name: "平安银行",
        price: 12.34,
        change_percent: 1.2,
        amount: 1200000000,
        volume: 1000000,
      },
      {
        symbol: "600519",
        name: "贵州茅台",
        price: 1850,
        change_percent: -0.5,
        amount: 980000000,
        volume: 500000,
      },
    ],
  })

  assert.equal(overview.indices.length, 2)
  assert.equal(overview.indices[0]?.name, "平安银行")
  assert.equal(overview.up_count, 1)
  assert.equal(overview.down_count, 1)
  assert.equal(overview.flat_count, 0)
})

test("extractRealtimeMarketOverview supports nested quotes.data payload", () => {
  const overview = extractRealtimeMarketOverview({
    quotes: {
      data: [
        {
          symbol: "000001",
          name: "平安银行",
          price: 12.34,
          change_percent: 0,
          amount: 1200000000,
          volume: 1000000,
        },
      ],
    },
  })

  assert.equal(overview.indices.length, 1)
  assert.equal(overview.flat_count, 1)
})
