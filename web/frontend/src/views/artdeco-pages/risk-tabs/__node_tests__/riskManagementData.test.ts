import test from "node:test"
import assert from "node:assert/strict"

import {
  toRiskManagementAlerts,
  toRiskManagementConcentrationMetrics,
  toRiskManagementMetrics,
  toRiskManagementSectorDistribution,
} from "../riskManagementData.ts"

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

test("toRiskManagementMetrics does not fabricate asset or daily change percentages from holdings-only payloads", () => {
  const metrics = toRiskManagementMetrics(positionsPayload)

  assert.deepEqual(metrics, {
    totalAssets: 1025000,
    totalAssetsChange: null,
    todayProfit: 55000,
    todayProfitChange: null,
    maxDrawdown: null,
    sharpeRatio: null,
    volatility: null,
    beta: null,
    sortinoRatio: null,
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
      stopStatus: "unverified",
      action: "待复核",
      policyReady: false,
    },
    {
      code: "000858.SZ",
      name: "五粮液",
      riskLevel: "medium",
      position: 14.63,
      stopStatus: "unverified",
      action: "待复核",
      policyReady: false,
    },
  ])
})

test("toRiskManagementAlerts returns empty list for invalid payloads", () => {
  assert.deepEqual(toRiskManagementAlerts(null), [])
})

test("toRiskManagementConcentrationMetrics derives live concentration rows instead of static defaults", () => {
  const metrics = toRiskManagementConcentrationMetrics(positionsPayload)

  assert.deepEqual(metrics, [
    { label: "前10大重仓股占比", current: 100, limit: null, variant: "gold" },
    { label: "单股最大仓位", current: 85.37, limit: null, variant: "warning" },
  ])
})

test("toRiskManagementSectorDistribution stays empty when the live positions payload has no sector fields", () => {
  assert.deepEqual(toRiskManagementSectorDistribution(positionsPayload), [])
})
