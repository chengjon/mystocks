import test from "node:test"
import assert from "node:assert/strict"
import { existsSync, readFileSync } from "node:fs"
import { resolve } from "node:path"

const riskTabsDir = resolve(import.meta.dirname, "..")

test("risk management helper module is present", () => {
  const helperPath = resolve(riskTabsDir, "riskManagementHelpers.ts")

  assert.equal(existsSync(helperPath), true)
  assert.match(readFileSync(helperPath, "utf8"), /export const riskPageConfig/)
})

test("risk management panel modules are present", () => {
  const overviewPanelPath = resolve(riskTabsDir, "ArtDecoRiskOverviewPanel.vue")
  const statsGridPath = resolve(riskTabsDir, "ArtDecoRiskStatsGrid.vue")
  const stockPanelPath = resolve(riskTabsDir, "ArtDecoRiskStockPanel.vue")

  assert.equal(existsSync(overviewPanelPath), true)
  assert.equal(existsSync(statsGridPath), true)
  assert.equal(existsSync(stockPanelPath), true)
})
