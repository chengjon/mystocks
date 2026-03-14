import test from "node:test"
import assert from "node:assert/strict"

import {
  normalizeDashboardFundFlow,
  normalizeDashboardIndustryFlow,
  normalizeDashboardMarketOverview,
  normalizeDashboardActiveStrategies,
  normalizeDashboardPositionRisk,
  normalizeDashboardStockFlowRanking,
  normalizeDashboardSystemHealth,
} from "../dashboardServiceData.ts"

test("normalizeDashboardMarketOverview unwraps nested quotes rows", () => {
  const rows = normalizeDashboardMarketOverview({
    data: {
      quotes: {
        data: [
          { symbol: "000001.SH", name: "上证指数", latest_price: 3250.12, change_percent: 1.23, volume: 1000 },
          { symbol: "399001.SZ", name: "深证成指", price: 10200.5, change: -0.56, amount: 2000 },
        ],
      },
    },
  })

  assert.deepEqual(rows, [
    { symbol: "000001.SH", name: "上证指数", latest_price: 3250.12, change_percent: 1.23, volume: 1000 },
    { symbol: "399001.SZ", name: "深证成指", latest_price: 10200.5, change_percent: -0.56, volume: 2000 },
  ])
})

test("normalizeDashboardFundFlow maps summary and big-deal payloads", () => {
  const result = normalizeDashboardFundFlow(
    {
      data: {
        data: [
          { 板块: "沪股通", 资金方向: "北向", 成交净买额: 1200000000, 指数涨跌幅: 1.2 },
          { 板块: "深股通", 资金方向: "北向", 成交净买额: -500000000, 指数涨跌幅: -0.2 },
        ],
      },
    },
    {
      data: {
        data: [
          { 成交额: 800000000, 大单性质: "买盘" },
          { 成交额: 300000000, 大单性质: "卖盘" },
        ],
      },
    },
  )

  assert.deepEqual(result, {
    hgt: { amount: 12, change: 1.2 },
    sgt: { amount: -5, change: -0.2 },
    northTotal: { amount: 7, monthly: 7 },
    mainForce: { amount: 5, percentage: 0.5 },
  })
})

test("normalizeDashboardIndustryFlow maps v2 sector rows", () => {
  const result = normalizeDashboardIndustryFlow({
    data: [
      { sector_name: "证券", change_percent: 2.56, main_net_inflow: 3200000000 },
      { name: "银行", change: "-1.23", amount: 4.5 },
    ],
  })

  assert.deepEqual(result, [
    { name: "证券", change: 2.56, amount: 32 },
    { name: "银行", change: -1.23, amount: 4.5 },
  ])
})

test("normalizeDashboardStockFlowRanking maps big-deal rows", () => {
  const result = normalizeDashboardStockFlowRanking({
    data: {
      data: [
        { symbol: "600519", 股票简称: "贵州茅台", 成交额: 1200000000, 大单性质: "买盘", 涨跌幅: 3.5 },
        { code: "000001", name: "平安银行", amount: 500000000, 大单性质: "卖盘", change: -0.8 },
      ],
    },
  })

  assert.deepEqual(result, [
    { code: "600519", name: "贵州茅台", amount: 12, change: 3.5 },
    { code: "000001", name: "平安银行", amount: -5, change: -0.8 },
  ])
})

test("normalizeDashboardPositionRisk aggregates positions payload", () => {
  const result = normalizeDashboardPositionRisk({
    data: {
      positions: [
        { market_value: 100000, unrealized_pnl: 5000, realized_pnl: 0, weight: 0.35 },
        { market_value: 50000, unrealized_pnl: -1000, realized_pnl: 200, weight: 0.15 },
      ],
      total_value: 150000,
    },
  })

  assert.deepEqual(result, {
    totalValue: 150000,
    totalPnL: 4200,
    pnlPercent: 2.8,
    maxDrawdown: 0,
    riskLevel: "medium",
    riskLevelText: "中风险",
  })
})

test("normalizeDashboardActiveStrategies unwraps list payload", () => {
  const result = normalizeDashboardActiveStrategies({
    data: {
      items: [
        { strategy_id: 1, strategy_name: "A", status: "active" },
        { strategy_id: 2, strategy_name: "B", status: "paused" },
      ],
    },
  })

  assert.deepEqual(result, [
    { strategy_id: 1, strategy_name: "A", status: "active" },
    { strategy_id: 2, strategy_name: "B", status: "paused" },
  ])
})

test("normalizeDashboardSystemHealth maps health response to monitor rows", () => {
  const result = normalizeDashboardSystemHealth({
    data: {
      service: "mystocks-web-api",
      status: "healthy",
      version: "1.0.0",
    },
  })

  assert.deepEqual(result, [
    { label: "服务状态", value: "HEALTHY", status: "good" },
    { label: "服务名称", value: "mystocks-web-api", status: "good" },
    { label: "版本", value: "1.0.0", status: "good" },
  ])
})
