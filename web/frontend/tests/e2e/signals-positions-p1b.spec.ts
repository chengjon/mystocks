import { expect, test, type Page } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("./helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

const E2E_USER = {
  id: 1,
  username: "admin",
  email: "admin@example.com",
  role: "admin",
  permissions: ["*"],
}

async function seedAuth(page: Page) {
  await page.addInitScript(({ user }) => {
    localStorage.setItem("auth_token", "p1b-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  }, { user: E2E_USER })
}

async function mockSignals(page: Page, items: unknown[]) {
  await page.route("**/api/v1/trade/signals**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: items,
        request_id: "p1b-signals-rid",
        process_time: "42.0",
      }),
    })
  })
}

async function mockPositions(page: Page, positions: unknown[]) {
  await page.route("**/api/v1/trade/positions**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          positions,
          total_market_value: positions.reduce((sum, item) => sum + Number((item as { market_value?: number }).market_value ?? 0), 0),
          total_profit_loss: 3200,
          total_profit_loss_percent: 2.6,
        },
        request_id: "p1b-positions-rid",
      }),
    })
  })
}

test.describe("P1-B Signals and Positions", () => {
  test.beforeEach(async ({ page }) => {
    await seedAuth(page)
  })

  test("watchlist and strategy signals keep shared real-mode empty state", async ({ page }) => {
    await mockSignals(page, [])

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/signals`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".strategy-signals-tab")).toBeVisible()
    await expect(page.locator(".empty-state")).toContainText("当前暂无策略信号")

    await page.goto(`${FRONTEND_BASE_URL}/strategy/signals`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".strategy-signals-tab")).toBeVisible()
    await expect(page.locator(".empty-state")).toContainText("当前暂无策略信号")
  })

  test("trade signals renders shared signal list with shared transform", async ({ page }) => {
    await mockSignals(page, [
      { symbol: "600519.SH", name: "贵州茅台", type: "BUY", price: 1688.5, time: "09:35:00", strategy: "趋势突破" },
      { symbol: "000001.SZ", name: "平安银行", type: "SELL", price: 12.35, time: "10:15:00", strategy: "资金异动" },
    ])

    await page.goto(`${FRONTEND_BASE_URL}/trade/signals`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".signals-view")).toBeVisible()
    await expect(page.locator(".artdeco-trading-signals__row")).toHaveCount(2)
    await expect(page.locator(".signals-count")).toContainText("2 条信号")
  })

  test("trade positions shows empty state under empty positions payload", async ({ page }) => {
    await mockPositions(page, [])

    await page.goto(`${FRONTEND_BASE_URL}/trade/positions`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".artdeco-trading-positions")).toBeVisible()
    await expect(page.locator(".artdeco-trading-positions__state")).toContainText("当前暂无持仓数据")
  })

  test("trade portfolio and risk pnl share portfolio empty state", async ({ page }) => {
    await mockPositions(page, [])

    await page.goto(`${FRONTEND_BASE_URL}/trade/portfolio`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".portfolio-overview-tab")).toBeVisible()
    await expect(page.locator(".state-panel")).toContainText("当前暂无持仓透视数据")

    await page.goto(`${FRONTEND_BASE_URL}/risk/pnl`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".portfolio-overview-tab")).toBeVisible()
    await expect(page.locator(".state-panel")).toContainText("当前暂无持仓透视数据")
  })

  test("trade portfolio and trade positions render real positions from shared endpoint", async ({ page }) => {
    await mockPositions(page, [
      {
        symbol: "600519.SH",
        symbol_name: "贵州茅台",
        quantity: 120,
        cost_price: 1580,
        current_price: 1688.5,
        market_value: 202620,
        profit_loss: 13020,
        profit_loss_percent: 6.87,
      },
      {
        symbol: "000001.SZ",
        symbol_name: "平安银行",
        quantity: 5000,
        cost_price: 11.8,
        current_price: 12.35,
        market_value: 61750,
        profit_loss: 2750,
        profit_loss_percent: 4.66,
      },
    ])

    await page.goto(`${FRONTEND_BASE_URL}/trade/positions`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".artdeco-trading-positions__row")).toHaveCount(2)

    await page.goto(`${FRONTEND_BASE_URL}/trade/portfolio`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".positions-grid .position-item")).toHaveCount(2)
  })
})
