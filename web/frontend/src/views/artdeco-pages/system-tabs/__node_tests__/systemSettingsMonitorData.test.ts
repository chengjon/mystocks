import test from "node:test"
import assert from "node:assert/strict"

import { normalizeSystemSettingsMonitorRows } from "../systemSettingsMonitorData.ts"

test("normalizeSystemSettingsMonitorRows maps detailed health warning payload to table rows", () => {
  const rows = normalizeSystemSettingsMonitorRows({
    data: {
      status: "warning",
      output: "[健康] API端点正常: /api/health\n[健康] API端点正常: /api/v1/market/quotes\n[警告] 前端服务异常",
      error: "tee: read-only file system",
    },
  })

  assert.deepEqual(rows, [
    { endpoint: "/api/health", qps: "-", p95: "-", errorRate: "0.00%" },
    { endpoint: "/api/v1/market/quotes", qps: "-", p95: "-", errorRate: "0.00%" },
  ])
})

test("normalizeSystemSettingsMonitorRows maps system health object payload to a summary row", () => {
  const rows = normalizeSystemSettingsMonitorRows({
    data: {
      service: "mystocks-web-api",
      status: "healthy",
      version: "1.0.0",
    },
  })

  assert.deepEqual(rows, [
    { endpoint: "mystocks-web-api", qps: "-", p95: "-", errorRate: "0.00%" },
  ])
})

test("normalizeSystemSettingsMonitorRows maps slim /api/health payload to a summary row", () => {
  const rows = normalizeSystemSettingsMonitorRows({
    status: "healthy",
    timestamp: 1773407019.1638122,
    version: "1.0.0",
  })

  assert.deepEqual(rows, [
    { endpoint: "/api/health", qps: "-", p95: "-", errorRate: "0.00%" },
  ])
})

test("normalizeSystemSettingsMonitorRows prefers explicit api metrics arrays when present", () => {
  const rows = normalizeSystemSettingsMonitorRows({
    data: {
      apis: [
        { endpoint: "/api/v1/trade/signals", qps: 12.345, p95_ms: 218.4, error_rate: 0.64 },
      ],
    },
  })

  assert.deepEqual(rows, [
    { endpoint: "/api/v1/trade/signals", qps: 12.35, p95: 218.4, errorRate: "0.64%" },
  ])
})
