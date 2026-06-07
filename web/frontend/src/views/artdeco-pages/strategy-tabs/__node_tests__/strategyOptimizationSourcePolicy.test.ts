import test from "node:test"
import assert from "node:assert/strict"

import {
  canWritebackOptimizationRow,
  formatOptimizationSourceLabel,
  shouldUseOptimizationMockFallback,
} from "../strategyOptimizationSourcePolicy.ts"

test("optimization route pages do not silently fall back to mock rows", () => {
  assert.equal(shouldUseOptimizationMockFallback(false), false)
  assert.equal(shouldUseOptimizationMockFallback(true), true)
})

test("optimization writeback stays disabled unless the row source is real", () => {
  assert.equal(canWritebackOptimizationRow("real"), true)
  assert.equal(canWritebackOptimizationRow("mock"), false)
  assert.equal(canWritebackOptimizationRow("unavailable"), false)
})

test("optimization source labels distinguish degraded real pages from embedded mock fallback", () => {
  assert.equal(formatOptimizationSourceLabel("real"), "REAL")
  assert.equal(formatOptimizationSourceLabel("mock"), "EMBEDDED-MOCK")
  assert.equal(formatOptimizationSourceLabel("unavailable"), "REAL-OFFLINE")
})
