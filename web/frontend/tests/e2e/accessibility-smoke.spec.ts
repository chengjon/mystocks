import AxeBuilder from "@axe-core/playwright"
import { expect, test } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("./helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

async function stubReadinessProbe(page: Parameters<typeof test>[0]["page"]) {
  for (const endpoint of ["**/api/health/ready", "**/health/ready"]) {
    await page.route(endpoint, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          message: "system ready",
          request_id: "e2e-axe-ready",
          data: { status: "ready" },
        }),
      })
    })
  }
}

async function seedStrategySession(page: Parameters<typeof test>[0]["page"]) {
  await page.addInitScript(() => {
    const user = {
      id: 1,
      username: "e2e-admin",
      email: "e2e-admin@mystocks.local",
      role: "admin",
      permissions: ["*"],
    }
    localStorage.setItem("auth_token", "e2e-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  })

  await page.route("**/api/csrf-token", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: { csrf_token: "e2e-axe-csrf" },
      }),
    })
  })

  await page.route("**/api/v1/strategy/strategies**", async (route) => {
    await route.fulfill({
      status: 200,
      headers: {
        "content-type": "application/json",
        "x-request-id": "req-axe-strategy",
        "x-process-time": "18ms",
      },
      body: JSON.stringify({
        success: true,
        code: 200,
        message: "ok",
        data: {
          items: [
            {
              id: "1",
              strategy_id: "1",
              strategy_name: "Accessibility Strategy",
              strategy_type: "momentum",
              description: "axe smoke",
              status: "active",
              updated_at: "2026-03-22T00:00:00Z",
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
        },
        request_id: "req-axe-strategy",
        process_time: "18ms",
        timestamp: "2026-03-22T00:00:00Z",
      }),
    })
  })
}

async function seedRiskOverviewSession(page: Parameters<typeof test>[0]["page"]) {
  await page.addInitScript(() => {
    const user = {
      id: 1,
      username: "e2e-admin",
      email: "e2e-admin@mystocks.local",
      role: "admin",
      permissions: ["*"],
    }
    localStorage.setItem("auth_token", "e2e-risk-axe-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  })

  await page.route("**/api/csrf-token", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: { csrf_token: "e2e-risk-axe-csrf" },
      }),
    })
  })

  await page.route("**/api/v1/monitoring/alert-rules", async (route) => {
    await route.fulfill({
      status: 200,
      headers: {
        "content-type": "application/json",
        "x-request-id": "req-axe-risk",
      },
      body: JSON.stringify({
        success: true,
        code: 200,
        message: "ok",
        data: [
          {
            id: "rule-1",
            rule_name: "单票止损线",
            rule_type: "stop_loss",
            symbol: "600519",
            is_active: true,
            priority: 1,
          },
          {
            id: "rule-2",
            rule_name: "组合波动率约束",
            rule_type: "portfolio_volatility",
            symbol: "GLOBAL",
            is_active: true,
            priority: 2,
          },
        ],
        request_id: "req-axe-risk",
        timestamp: "2026-04-19T00:00:00Z",
      }),
    })
  })

  await page.route("**/api/v1/monitoring/alerts**", async (route) => {
    await route.fulfill({
      status: 200,
      headers: {
        "content-type": "application/json",
        "x-request-id": "req-axe-risk-alerts",
      },
      body: JSON.stringify({
        success: true,
        code: 200,
        message: "ok",
        data: [],
        request_id: "req-axe-risk-alerts",
        timestamp: "2026-04-19T00:00:00Z",
      }),
    })
  })
}

async function seedTradeTerminalSession(page: Parameters<typeof test>[0]["page"]) {
  let tradingRunning = false

  await page.addInitScript(() => {
    const user = {
      id: 1,
      username: "e2e-admin",
      email: "e2e-admin@mystocks.local",
      role: "admin",
      permissions: ["*"],
    }
    localStorage.setItem("auth_token", "e2e-trade-axe-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  })

  await page.route("**/api/csrf-token", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: { csrf_token: "e2e-trade-axe-csrf" },
      }),
    })
  })

  await page.route("**/api/trading/status", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        code: 200,
        message: "ok",
        data: tradingRunning
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
        request_id: "req-axe-trade-status",
        timestamp: "2026-04-19T00:00:00Z",
      }),
    })
  })

  await page.route("**/api/trading/strategies/performance", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        code: 200,
        message: "ok",
        data: [
          {
            id: "strategy-1",
            strategy_name: "Accessibility Momentum",
            status: tradingRunning ? "active" : "idle",
            performance_metrics: {
              pnl: 12890.4,
              win_rate: 0.67,
            },
          },
        ],
        request_id: "req-axe-trade-strategy",
        timestamp: "2026-04-19T00:00:00Z",
      }),
    })
  })

  await page.route("**/api/trading/market/snapshot", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        code: 200,
        message: "ok",
        data: {
          timestamp: "2026-04-19T09:30:00Z",
          data: {
            SH000001: { price: 3321.08, change: 21.16, change_percent: 0.64 },
            SZ399001: { price: 10214.2, change: 72.44, change_percent: 0.71 },
          },
        },
        request_id: "req-axe-trade-market",
        timestamp: "2026-04-19T00:00:00Z",
      }),
    })
  })

  await page.route("**/api/trading/risk/metrics", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        code: 200,
        message: "ok",
        data: {
          risk_status: tradingRunning ? "normal" : "warning",
          current_drawdown: tradingRunning ? 0.018 : 0,
          daily_pnl: tradingRunning ? 3450.5 : 0,
          active_positions: tradingRunning ? 2 : 0,
          last_updated: "2026-04-19T09:30:00Z",
        },
        request_id: "req-axe-trade-risk",
        timestamp: "2026-04-19T00:00:00Z",
      }),
    })
  })
}

function expectNoSeriousViolations(results: Awaited<ReturnType<AxeBuilder["analyze"]>>) {
  const blockingViolations = results.violations.filter((violation) =>
    ["serious", "critical"].includes(violation.impact ?? ""),
  )

  expect(
    blockingViolations.map((violation) => ({
      id: violation.id,
      impact: violation.impact,
      nodes: violation.nodes.length,
    })),
  ).toEqual([])
}

test.describe("Accessibility smoke", () => {
  test("login page has no serious accessibility violations", async ({ page }) => {
    await stubReadinessProbe(page)
    await page.goto(`${FRONTEND_BASE_URL}/login`, { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("heading", { name: "LOGIN" })).toBeVisible()

    const results = await new AxeBuilder({ page })
      .disableRules(["color-contrast"])
      .analyze()
    expectNoSeriousViolations(results)
  })

  test("strategy repository page has no serious accessibility violations", async ({ page }) => {
    await stubReadinessProbe(page)
    await seedStrategySession(page)
    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`, { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("heading", { level: 1, name: "策略仓库工作台" })).toBeVisible()

    const results = await new AxeBuilder({ page })
      .include("main")
      .disableRules(["color-contrast"])
      .analyze()
    expectNoSeriousViolations(results)
  })

  test("risk overview page has no serious accessibility violations", async ({ page }) => {
    await stubReadinessProbe(page)
    await seedRiskOverviewSession(page)
    await page.goto(`${FRONTEND_BASE_URL}/risk/overview`, { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("heading", { level: 1, name: "风险概览工作台" })).toBeVisible()

    const results = await new AxeBuilder({ page })
      .include("main")
      .disableRules(["color-contrast"])
      .analyze()
    expectNoSeriousViolations(results)
  })

  test("trade terminal page has no serious accessibility violations", async ({ page }) => {
    await stubReadinessProbe(page)
    await seedTradeTerminalSession(page)
    await page.goto(`${FRONTEND_BASE_URL}/trade/terminal`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".page-title")).toContainText("实时交易监控仪表板")

    const results = await new AxeBuilder({ page })
      .include("main")
      .disableRules(["color-contrast"])
      .analyze()
    expectNoSeriousViolations(results)
  })
})
