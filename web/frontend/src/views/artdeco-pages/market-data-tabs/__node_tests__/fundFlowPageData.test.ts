import test from "node:test"
import assert from "node:assert/strict"

import { buildFundOverview, buildFundTrend, buildStockRanking } from "../fundFlowPageData.ts"

test("buildFundOverview maps沪股通/深股通/北向/大单净额", () => {
  const summary = {
    data: [
      { 交易日: "2026-03-13", 板块: "沪股通", 资金方向: "北向", 成交净买额: 10, 指数涨跌幅: 1.2 },
      { 交易日: "2026-03-13", 板块: "深股通", 资金方向: "北向", 成交净买额: 20, 指数涨跌幅: 0.8 },
    ],
  }
  const deals = {
    data: [
      { 成交额: 100000000, 大单性质: "买盘" },
      { 成交额: 30000000, 大单性质: "卖盘" },
    ],
  }

  const overview = buildFundOverview(summary, deals)

  assert.equal(overview.shanghai.amount, 10)
  assert.equal(overview.shenzhen.amount, 20)
  assert.equal(overview.north.amount, 30)
  assert.equal(overview.main.amount, 70000000)
})

test("buildFundTrend groups northbound values by trade date", () => {
  const trend = buildFundTrend({
    data: [
      { 交易日: "2026-03-12", 资金方向: "北向", 成交净买额: 10 },
      { 交易日: "2026-03-12", 资金方向: "南向", 成交净买额: 20 },
      { 交易日: "2026-03-13", 资金方向: "北向", 成交净买额: 30 },
    ],
  })

  assert.deepEqual(trend, [
    { date: "2026-03-12", value: 10 },
    { date: "2026-03-13", value: 30 },
  ])
})

test("buildStockRanking maps big-deal rows to ranking rows", () => {
  const ranking = buildStockRanking({
    data: [
      {
        symbol: 301308,
        股票简称: "江波龙",
        成交价格: 333,
        成交额: 213120000,
        大单性质: "买盘",
        涨跌幅: "4.39%",
      },
    ],
  })

  assert.equal(ranking.length, 1)
  assert.equal(ranking[0]?.name, "江波龙")
  assert.equal(ranking[0]?.code, "301308")
  assert.equal(ranking[0]?.price, 333)
  assert.equal(ranking[0]?.change, 4.39)
  assert.equal(ranking[0]?.inflow, "+2.13")
})
