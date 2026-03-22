import test from "node:test"
import assert from "node:assert/strict"

import { supportsStrategyLifecycleAction } from "../strategyLifecycleAvailability.ts"

test("strategy lifecycle actions are enabled for the current strategy management UI", () => {
  assert.equal(supportsStrategyLifecycleAction("start"), true)
  assert.equal(supportsStrategyLifecycleAction("pause"), true)
  assert.equal(supportsStrategyLifecycleAction("resume"), true)
  assert.equal(supportsStrategyLifecycleAction("stop"), true)
})
