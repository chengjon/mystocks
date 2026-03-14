import test from "node:test"
import assert from "node:assert/strict"

import { supportsStrategyLifecycleAction } from "../strategyLifecycleAvailability.ts"

test("strategy lifecycle actions are currently unsupported", () => {
  assert.equal(supportsStrategyLifecycleAction("start"), false)
  assert.equal(supportsStrategyLifecycleAction("pause"), false)
  assert.equal(supportsStrategyLifecycleAction("resume"), false)
  assert.equal(supportsStrategyLifecycleAction("stop"), false)
})
