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

async function mockTradeTerminalApis(
  page: Parameters<typeof test>[0]["page"],
  mode: "live-shell" | "lightweight-demo" | "risk-refresh-fail" | "status-refresh-fail" | "market-refresh-fail" | "strategy-refresh-fail" = "live-shell",
) {
  let tradingRunning = false
  let tradingStatusRequestCount = 0
  let strategyRequestCount = 0
  let marketRequestCount = 0
  let riskRequestCount = 0

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
      tradingStatusRequestCount += 1

      if (mode === "status-refresh-fail" && tradingStatusRequestCount > 2) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            code: 500,
            message: "trading status unavailable",
            request_id: "req-trade-terminal-status-fail",
          }),
        })
        return
      }

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
              : mode === "lightweight-demo"
                ? {
                    session_id: null,
                    is_running: false,
                    current_drawdown: 0,
                    daily_pnl: 0,
                    total_pnl: 0,
                    active_positions: 0,
                    win_rate: 0,
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
      strategyRequestCount += 1

      if (mode === "strategy-refresh-fail" && strategyRequestCount > 1) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            code: 500,
            message: "strategy performance unavailable",
            request_id: "req-trade-terminal-strategies-fail",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-trade-terminal-strategies",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            [
              mode === "lightweight-demo" && !tradingRunning
                ? {
                    id: "demo-momentum",
                    strategy_name: "Demo Momentum",
                    status: "idle",
                    performance_metrics: {
                      pnl: 0,
                      win_rate: 0,
                    },
                  }
                : {
                    id: "strategy-1",
                    strategy_name: "Momentum Alpha",
                    status: tradingRunning ? "active" : "idle",
                    performance_metrics: {
                      pnl: 12890.4,
                      win_rate: 0.67,
                    },
                  },
              ...(mode === "lightweight-demo" && !tradingRunning
                ? []
                : [
                    {
                      id: "strategy-2",
                      strategy_name: "Mean Reversion",
                      status: "idle",
                      performance_metrics: {
                        pnl: 4120.2,
                        win_rate: 0.51,
                      },
                    },
                  ]),
            ],
            { request_id: "req-trade-terminal-strategies" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/trading/market/snapshot") {
      marketRequestCount += 1

      if (mode === "market-refresh-fail" && marketRequestCount > 1) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            code: 500,
            message: "market snapshot unavailable",
            request_id: "req-trade-terminal-market-fail",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            mode === "lightweight-demo" && !tradingRunning
              ? {
                  timestamp: "2026-04-19T09:30:00Z",
                  market_status: "open",
                  data: {
                    "000001.SH": { price: 12.5, change: 0.08, change_percent: 0.64 },
                  },
                }
              : {
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
      riskRequestCount += 1

      // Allow the initial idle snapshot and the post-start verified snapshot
      // to land before the explicit refresh degrades the risk slice.
      if (mode === "risk-refresh-fail" && riskRequestCount > 2) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            code: 500,
            message: "risk metrics unavailable",
            request_id: "req-trade-terminal-risk-fail",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            mode === "lightweight-demo" && !tradingRunning
              ? {
                  risk_status: "normal",
                  current_drawdown: 0,
                  daily_pnl: 0,
                  active_positions: 0,
                  last_updated: "2026-04-19T09:30:00Z",
                }
              : {
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
  test.use({ serviceWorkers: "block" })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
  })

  test("loads trading dashboard shell and supports start action", async ({ page }) => {
    await mockTradeTerminalApis(page)

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

  test("degrades lightweight runtime availability payloads to pending runtime copy", async ({ page }) => {
    await mockTradeTerminalApis(page, "lightweight-demo")

    await page.goto(`${FRONTEND_BASE_URL}/trade/terminal`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".runtime-alert")).toContainText("当前展示轻量运行时占位数据")
    await expect(page.locator(".status-overview")).toContainText("总盈亏")
    await expect(page.locator(".status-overview")).toContainText("待接入")
    await expect(page.locator(".trading-details")).toContainText("会话ID")
    await expect(page.locator(".trading-details")).toContainText("轻量占位")
    await expect(page.locator(".trading-details")).toContainText("运行状态")
    await expect(page.locator(".trading-details")).toContainText("待接入")
    await expect(page.locator(".market-snapshot")).toContainText("轻量样例")
    await expect(page.locator(".market-snapshot")).toContainText("当前市场快照来自轻量运行时样例")
    await expect(page.locator(".risk-panel")).toContainText("风险监控")
    await expect(page.locator(".risk-panel")).toContainText("待接入")
    await page.getByRole("button", { name: "风险报告" }).click()
    await expect(page.locator(".risk-report")).toContainText("当前仅展示轻量运行时占位数据，实盘风控建议待接入。")
    await expect(page.locator(".risk-report")).not.toContainText("系统运行正常，继续监控")
  })

  test("retains the last verified risk panel snapshot when a later risk refresh fails", async ({ page }) => {
    await mockTradeTerminalApis(page, "risk-refresh-fail")

    const initialStrategyResponse = page.waitForResponse((response) => {
      return response.url().includes("/api/trading/strategies/performance") && response.status() === 200
    })
    const initialRiskResponse = page.waitForResponse((response) => {
      return response.url().includes("/api/trading/risk/metrics") && response.status() === 200
    })
    await page.goto(`${FRONTEND_BASE_URL}/trade/terminal`, { waitUntil: "domcontentloaded" })

    await initialStrategyResponse
    await initialRiskResponse
    await expect(page.locator(".strategy-performance")).toContainText("Momentum Alpha")
    await expect(page.locator(".risk-panel")).toContainText("¥0.00")
    await expect(page.locator(".risk-panel")).toContainText("0 个")

    const postStartRiskResponse = page.waitForResponse((response) => {
      return response.url().includes("/api/trading/risk/metrics") && response.status() === 200
    })
    await page.getByRole("button", { name: "启动交易" }).click()
    await postStartRiskResponse
    await expect(page.locator(".risk-panel")).toContainText("¥3,450.50")
    await expect(page.locator(".risk-panel")).toContainText("2 个")
    await expect(page.locator(".risk-panel")).toContainText("1.80%")

    const degradedRiskResponse = page.waitForResponse((response) => {
      return response.url().includes("/api/trading/risk/metrics") && response.status() === 500
    })
    await page.getByRole("button", { name: "刷新数据" }).click()
    await degradedRiskResponse

    await expect(page.locator(".el-message").filter({ hasText: "数据刷新完成，但部分模块降级：风险指标" })).toBeVisible()
    await expect(page.locator(".runtime-alert")).toContainText("风险指标")
    await expect(page.locator(".risk-panel")).toContainText("¥3,450.50")
    await expect(page.locator(".risk-panel")).toContainText("2 个")
    await expect(page.locator(".risk-panel")).toContainText("1.80%")
    await expect(page.locator(".risk-panel")).not.toContainText("未知")
  })

  test("retains the last verified trading session snapshot when a later status refresh fails", async ({ page }) => {
    await mockTradeTerminalApis(page, "status-refresh-fail")

    await page.goto(`${FRONTEND_BASE_URL}/trade/terminal`, { waitUntil: "domcontentloaded" })

    await page.getByRole("button", { name: "启动交易" }).click()
    await expect(page.locator(".trading-details")).toContainText("mock-session-running")
    await expect(page.locator(".status-overview")).toContainText("¥12,890.40")
    await expect(page.locator(".status-overview")).toContainText("67.00%")
    await expect(page.locator(".status-overview")).toContainText("1.80%")

    await page.getByRole("button", { name: "刷新数据" }).click()

    await expect(page.locator(".runtime-alert")).toContainText("交易状态")
    await expect(page.locator(".trading-details")).toContainText("mock-session-running")
    await expect(page.locator(".trading-details")).toContainText("运行中")
    await expect(page.locator(".status-overview")).toContainText("¥12,890.40")
    await expect(page.locator(".status-overview")).toContainText("67.00%")
    await expect(page.locator(".status-overview")).toContainText("1.80%")
    await expect(page.locator(".trading-details")).not.toContainText("fallback-offline")
  })

  test("retains the last verified market snapshot when a later market refresh fails", async ({ page }) => {
    await mockTradeTerminalApis(page, "market-refresh-fail")

    await page.goto(`${FRONTEND_BASE_URL}/trade/terminal`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".market-snapshot")).toContainText("SH000001")
    await expect(page.locator(".market-snapshot")).toContainText("SZ399001")
    await expect(page.locator(".market-snapshot")).toContainText("¥3,321.08")

    await page.getByRole("button", { name: "刷新数据" }).click()

    await expect(page.locator(".runtime-alert")).toContainText("市场快照")
    await expect(page.locator(".market-snapshot")).toContainText("SH000001")
    await expect(page.locator(".market-snapshot")).toContainText("SZ399001")
    await expect(page.locator(".market-snapshot")).toContainText("¥3,321.08")
    await expect(page.locator(".market-snapshot")).not.toContainText("暂无市场数据")
  })

  test("retains the last verified strategy rows when a later strategy refresh fails", async ({ page }) => {
    await mockTradeTerminalApis(page, "strategy-refresh-fail")

    await page.goto(`${FRONTEND_BASE_URL}/trade/terminal`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".strategy-performance")).toContainText("Momentum Alpha")
    await expect(page.locator(".strategy-performance")).toContainText("Mean Reversion")

    await page.getByRole("button", { name: "刷新数据" }).click()

    await expect(page.locator(".runtime-alert")).toContainText("策略绩效")
    await expect(page.locator(".strategy-performance")).toContainText("Momentum Alpha")
    await expect(page.locator(".strategy-performance")).toContainText("Mean Reversion")
    await expect(page.locator(".strategy-performance")).not.toContainText("暂无数据")
  })
})
