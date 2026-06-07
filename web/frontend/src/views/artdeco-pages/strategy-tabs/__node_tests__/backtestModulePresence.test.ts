import test from "node:test"
import assert from "node:assert/strict"
import { existsSync, readFileSync } from "node:fs"
import { resolve } from "node:path"

const strategyTabsDir = resolve(import.meta.dirname, "..")

test("strategy backtest view model module is present", () => {
  const viewModelPath = resolve(strategyTabsDir, "backtestAnalysisViewModel.ts")
  const source = readFileSync(viewModelPath, "utf8")

  assert.equal(existsSync(viewModelPath), true)
  assert.match(source, /export function useBacktestAnalysisViewModel/)
  assert.match(source, /function handleGenerateParameterSnapshot\(/)
  assert.match(source, /function handleInspectGpuAllocation\(/)
})

test("strategy backtest helper module is present", () => {
  const helperPath = resolve(strategyTabsDir, "backtestAnalysisHelpers.ts")

  assert.equal(existsSync(helperPath), true)
  assert.match(readFileSync(helperPath, "utf8"), /export function createBacktestPayload/)
})
