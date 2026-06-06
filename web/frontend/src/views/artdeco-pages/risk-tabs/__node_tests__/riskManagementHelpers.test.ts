import test from "node:test"
import assert from "node:assert/strict"

import {
  concentrationMetrics,
  createInitialRiskAlerts,
  createInitialRiskMetrics,
  formatRiskCurrencyNumber,
  getRiskLevelLabel,
  getRiskTabMeta,
  getStopStatusLabel,
  mergeRiskMetrics,
  riskPageConfig,
  riskTabs,
  sectorDistribution,
} from "../riskManagementHelpers.ts"

test("risk page defaults keep refreshable overview skeleton contract", () => {
  assert.equal(riskPageConfig.title, "风险管理中心")
  assert.equal(riskPageConfig.showRefresh, true)
  assert.equal(riskPageConfig.showTabs, true)
  assert.equal(riskPageConfig.cacheTime, 300000)
  assert.deepEqual(riskPageConfig.skeleton, { columns: 4, rows: 3 })
})

test("getRiskTabMeta resolves known tabs and falls back to overview", () => {
  assert.deepEqual(getRiskTabMeta("stock"), riskTabs[1])
  assert.deepEqual(getRiskTabMeta("missing"), riskTabs[0])
  assert.equal(riskTabs[0]?.key, "overview")
  assert.equal(riskTabs[1]?.key, "stock")
  assert.equal(riskTabs[1]?.description, "当前仅保留个股风险分析入口，个股级仓位、止损与波动联动待接入。")
  assert.equal(riskTabs[1]?.description.includes("可执行的个股风控动作"), false)
})

test("initial risk fixtures preserve expected alert and sector inventory", () => {
  const metrics = createInitialRiskMetrics()
  const alerts = createInitialRiskAlerts()

  assert.equal(metrics.totalAssets, 1250000)
  assert.equal(metrics.positionValue, 1150000)
  assert.equal(alerts.length, 4)
  assert.equal(alerts[0]?.riskLevel, "high")
  assert.equal(alerts[2]?.stopStatus, "triggered")
  assert.equal(alerts[0]?.policyReady, true)
  assert.equal(sectorDistribution.length, 5)
  assert.equal(concentrationMetrics.length, 4)
})

test("mergeRiskMetrics applies partial payload fields and ignores invalid input", () => {
  const current = createInitialRiskMetrics()

  assert.deepEqual(mergeRiskMetrics(current, null), current)
  assert.deepEqual(
    mergeRiskMetrics(current, {
      totalAssets: 2000000,
      volatility: 12.8,
    }),
    {
      ...current,
      totalAssets: 2000000,
      volatility: 12.8,
    },
  )
})

test("risk labels and currency formatting stay aligned with Chinese UI copy", () => {
  assert.equal(getRiskLevelLabel("high"), "高风险")
  assert.equal(getRiskLevelLabel("medium"), "中风险")
  assert.equal(getRiskLevelLabel("low"), "低风险")

  assert.equal(getStopStatusLabel("triggered"), "已触发")
  assert.equal(getStopStatusLabel("approaching"), "接近")
  assert.equal(getStopStatusLabel("normal"), "正常")
  assert.equal(getStopStatusLabel("unverified"), "未校验")

  assert.equal(formatRiskCurrencyNumber(1250000), "1,250,000")
})
