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
    request_id: "req-risk-pnl-default",
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
    localStorage.setItem("auth_token", "e2e-risk-pnl-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  })
}

async function mockRiskPnlApis(page: Parameters<typeof test>[0]["page"]) {
  await page.route(/https?:\/\/[^/]+\/api\/.*/, async (route) => {
    const url = new URL(route.request().url())

    if (url.pathname === "/api/health/ready") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            { status: "ready" },
            { request_id: "req-risk-pnl-ready", message: "system ready" },
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
              csrf_token: "e2e-risk-pnl-csrf",
              token_type: "bearer",
              expires_in: 3600,
            },
            { request_id: "req-risk-pnl-csrf" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/v1/data/markets/overview" || url.pathname === "/api/v1/market/overview") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            { up_count: 1888, down_count: 1024, turnover: 8234 },
            { request_id: "req-risk-pnl-market-overview" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/v1/trade/positions") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-risk-pnl-positions",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              positions: [
                {
                  symbol: "600519",
                  symbol_name: "贵州茅台",
                  market_value: 202584,
                  profit_loss_percent: -0.69,
                },
                {
                  symbol: "300750",
                  symbol_name: "宁德时代",
                  market_value: 170080,
                  profit_loss_percent: 1.24,
                },
              ],
              total_market_value: 372664,
              total_profit_loss: 6844,
              total_profit_loss_percent: 1.84,
            },
            { request_id: "req-risk-pnl-positions" },
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

test.describe("Risk PnL E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
    await mockRiskPnlApis(page)
  })

  test("loads portfolio shell, top positions, and honest pending rebalance policy state", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/risk/pnl`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { level: 1, name: "组合资产工作台" })).toBeVisible()
    await expect(page.getByRole("button", { name: "刷新资产" })).toBeVisible()
    await expect(page.locator(".stats-strip")).toContainText("总资产")
    await expect(page.locator(".stats-strip")).toContainText("持仓数量")
    await expect(page.locator(".stats-strip")).toContainText("再平衡建议待接入")
    await expect(page.locator(".positions-grid .position-item")).toHaveCount(2)
    await expect(page.locator(".portfolio-overview-tab")).toContainText("Top Positions")
    await expect(page.locator(".portfolio-overview-tab")).toContainText("贵州茅台")
    await expect(page.locator(".rebalance-section")).toContainText("再平衡策略待接入")
    await expect(page.locator(".rebalance-section")).not.toContainText("目标 25%")
    await expect(page.locator(".rebalance-section")).not.toContainText("建议减仓约")

    await page.getByRole("button", { name: "刷新资产" }).click()
    await expect(page.getByRole("heading", { level: 1, name: "组合资产工作台" })).toBeVisible()
  })
})
