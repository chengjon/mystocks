import test from "node:test"
import assert from "node:assert/strict"

import { toRiskManagementAlerts, toRiskManagementMetrics } from "../riskManagementData.ts"

const positionsPayload = {
  data: {
    positions: [
      {
        symbol: "600519.SH",
        symbol_name: "贵州茅台",
        market_value: "875000.00",
        profit_loss_percent: 6.06,
      },
      {
        symbol: "000858.SZ",
        symbol_name: "五粮液",
        market_value: "150000.00",
        profit_loss_percent: 3.45,
      },
    ],
    total_market_value: "1025000.00",
    total_profit_loss: "55000.00",
    total_profit_loss_percent: 5.67,
  },
}

test("toRiskManagementMetrics maps trade positions payload into risk header metrics", () => {
  const metrics = toRiskManagementMetrics(positionsPayload)

  assert.deepEqual(metrics, {
    totalAssets: 1025000,
    totalAssetsChange: 5.67,
    todayProfit: 55000,
    todayProfitChange: 5.67,
    maxDrawdown: 0,
    sharpeRatio: 0,
    volatility: 0,
    beta: 1,
    sortinoRatio: 0,
    positionValue: 1025000,
  })
})

test("toRiskManagementAlerts derives alert rows from live positions", () => {
  const alerts = toRiskManagementAlerts(positionsPayload)

  assert.deepEqual(alerts, [
    {
      code: "600519.SH",
      name: "贵州茅台",
      riskLevel: "high",
      position: 85.37,
      stopStatus: "approaching",
      action: "减仓",
    },
    {
      code: "000858.SZ",
      name: "五粮液",
      riskLevel: "medium",
      position: 14.63,
      stopStatus: "normal",
      action: "监控",
    },
  ])
})

test("toRiskManagementAlerts returns empty list for invalid payloads", () => {
  assert.deepEqual(toRiskManagementAlerts(null), [])
})
