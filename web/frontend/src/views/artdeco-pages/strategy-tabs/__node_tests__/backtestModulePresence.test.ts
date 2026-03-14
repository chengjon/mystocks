import test from "node:test"
import assert from "node:assert/strict"
import { existsSync, readFileSync } from "node:fs"
import { resolve } from "node:path"

const strategyTabsDir = resolve(import.meta.dirname, "..")

test("strategy backtest view model module is present", () => {
  const viewModelPath = resolve(strategyTabsDir, "backtestAnalysisViewModel.ts")

  assert.equal(existsSync(viewModelPath), true)
  assert.match(readFileSync(viewModelPath, "utf8"), /export function useBacktestAnalysisViewModel/)
})

test("strategy backtest helper module is present", () => {
  const helperPath = resolve(strategyTabsDir, "backtestAnalysisHelpers.ts")

  assert.equal(existsSync(helperPath), true)
  assert.match(readFileSync(helperPath, "utf8"), /export function createBacktestPayload/)
})
