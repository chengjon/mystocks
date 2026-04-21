import { expect, test } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("./helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

function buildUnifiedResponse<T>(data: T, overrides?: Partial<Record<string, unknown>>) {
  return {
    success: true,
    code: 200,
    message: "ok",
    data,
    timestamp: "2026-04-19T00:00:00Z",
    request_id: "req-trade-terminal-default",
    ...(overrides ?? {}),
  }
}

async function setupAuthenticatedSession(page: Parameters<typeof test>[0]["page"]) {
  await page.addInitScript(() => {
    const user = {
      id: 1,
      username: "e2e-admin",
      email: "e2e-admin@mystocks.local",
      role: "admin",
      permissions: ["*"],
    }
    localStorage.setItem("auth_token", "e2e-trade-terminal-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  })
}

async function mockTradeTerminalApis(page: Parameters<typeof test>[0]["page"]) {
  let tradingRunning = false

  await page.route(/https?:\/\/[^/]+\/api\/.*/, async (route) => {
    const request = route.request()
    const url = new URL(request.url())

    if (url.pathname === "/api/health/ready") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            { status: "ready" },
            { request_id: "req-trade-terminal-ready", message: "system ready" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/csrf-token") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              csrf_token: "e2e-trade-terminal-csrf",
              token_type: "bearer",
              expires_in: 3600,
            },
            { request_id: "req-trade-terminal-csrf" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/trading/status") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-trade-terminal-status",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            tradingRunning
              ? {
                  session_id: "mock-session-running",
                  is_running: true,
                  current_drawdown: 0.018,
                  daily_pnl: 3450.5,
                  total_pnl: 12890.4,
                  active_positions: 2,
                  win_rate: 0.67,
                }
              : {
                  session_id: "mock-session-idle",
                  is_running: false,
                  current_drawdown: 0,
                  daily_pnl: 0,
                  total_pnl: 0,
                  active_positions: 0,
                  win_rate: 0,
                },
            { request_id: "req-trade-terminal-status" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/trading/strategies/performance") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-trade-terminal-strategies",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            [
              {
                id: "strategy-1",
                strategy_name: "Momentum Alpha",
                status: tradingRunning ? "active" : "idle",
                performance_metrics: {
                  pnl: 12890.4,
                  win_rate: 0.67,
                },
              },
            ],
            { request_id: "req-trade-terminal-strategies" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/trading/market/snapshot") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              timestamp: "2026-04-19T09:30:00Z",
              data: {
                SH000001: { price: 3321.08, change: 21.16, change_percent: 0.64 },
                SZ399001: { price: 10214.2, change: 72.44, change_percent: 0.71 },
              },
            },
            { request_id: "req-trade-terminal-market" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/trading/risk/metrics") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              risk_status: tradingRunning ? "normal" : "warning",
              current_drawdown: tradingRunning ? 0.018 : 0,
              daily_pnl: tradingRunning ? 3450.5 : 0,
              active_positions: tradingRunning ? 2 : 0,
              last_updated: "2026-04-19T09:30:00Z",
            },
            { request_id: "req-trade-terminal-risk" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/trading/start" && request.method() === "POST") {
      tradingRunning = true
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            { status: "running" },
            { request_id: "req-trade-terminal-start" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/trading/stop" && request.method() === "POST") {
      tradingRunning = false
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            { status: "stopped" },
            { request_id: "req-trade-terminal-stop" },
          ),
        ),
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(buildUnifiedResponse([])),
    })
  })
}

test.describe("Trade Terminal E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
    await mockTradeTerminalApis(page)
  })

  test("loads trading dashboard shell and supports start action", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/trade/terminal`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".page-title")).toContainText("实时交易监控仪表板")
    await expect(page.getByRole("button", { name: "刷新数据" })).toBeVisible()
    await expect(page.locator(".strategy-performance")).toContainText("Momentum Alpha")
    await expect(page.locator(".risk-panel")).toContainText("风险监控")

    await page.getByRole("button", { name: "启动交易" }).click()
    await expect(page.getByRole("button", { name: "停止交易" })).toBeVisible()
    await expect(page.locator(".trading-details")).toContainText("mock-session-running")
    await expect(page.locator(".trading-details")).toContainText("运行中")
  })
})
