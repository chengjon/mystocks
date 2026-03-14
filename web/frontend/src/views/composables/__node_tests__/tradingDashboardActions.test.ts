import test from "node:test"
import assert from "node:assert/strict"

import { createTradingDashboardActions } from "../tradingDashboardActions.ts"

test("trading dashboard actions attach a fresh CSRF token for each write request", async () => {
  const calls: Array<{ method: string; url: string; headers?: Record<string, string>; data?: unknown }> = []
  let tokenCounter = 0

  const actions = createTradingDashboardActions({
    getCsrfToken: async () => {
      tokenCounter += 1
      return `token-${tokenCounter}`
    },
    post: async (url, data, config) => {
      calls.push({ method: "POST", url, data, headers: config?.headers as Record<string, string> | undefined })
      return {}
    },
    delete: async (url, config) => {
      calls.push({ method: "DELETE", url, headers: config?.headers as Record<string, string> | undefined })
      return {}
    },
  })

  await actions.startTradingSession()
  await actions.stopTradingSession()
  await actions.addStrategy("SVMTradingStrategy")
  await actions.removeStrategy("demo-momentum")

  assert.deepEqual(calls.map((item) => [item.method, item.url, item.headers?.["X-CSRF-Token"]]), [
    ["POST", "/api/trading/start", "token-1"],
    ["POST", "/api/trading/stop", "token-2"],
    ["POST", "/api/trading/strategies/add", "token-3"],
    ["DELETE", "/api/trading/strategies/demo-momentum", "token-4"],
  ])

  assert.deepEqual(calls[2]?.data, { strategy_name: "SVMTradingStrategy" })
})
