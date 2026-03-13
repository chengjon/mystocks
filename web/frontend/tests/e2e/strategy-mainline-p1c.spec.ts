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
    localStorage.setItem("auth_token", "p1c-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  }, { user: E2E_USER })
}

async function mockStrategies(page: Page) {
  const body = {
    success: true,
    data: [
      {
        strategy_id: 101,
        strategy_name: "Momentum Alpha",
        strategy_type: "momentum",
        status: "active",
        description: "alpha",
        updated_at: "2026-03-13T09:00:00Z",
        parameters: [
          { name: "lookback", value: 20, data_type: "number" },
          { name: "threshold", value: 1.5, data_type: "number" },
        ],
      },
      {
        strategy_id: 102,
        strategy_name: "Reversion Beta",
        strategy_type: "mean_reversion",
        status: "paused",
        description: "beta",
        updated_at: "2026-03-13T09:05:00Z",
        parameters: [
          { name: "window", value: 10, data_type: "number" },
        ],
      },
    ],
    request_id: "p1c-strategy-rid",
    process_time: "32ms",
  }

  await page.route("**/api/v1/strategy/strategies**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(body),
    })
  })

  await page.route("**/api/api/v1/strategy/strategies**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(body),
    })
  })
}

test.describe("P1-C Strategy Mainline", () => {
  test.beforeEach(async ({ page }) => {
    await seedAuth(page)
    await mockStrategies(page)
  })

  test("strategy repo loads and cross-tab links append strategyId", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".strategy-management")).toBeVisible()
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(2)

    await page.getByRole("button", { name: "参数" }).first().click()
    await page.waitForURL("**/strategy/parameters?strategyId=101", { timeout: 15000 })
  })

  test("strategy parameters page loads selected strategy context", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/strategy/parameters?strategyId=101`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".strategy-parameters-tab")).toBeVisible()
    await expect(page.locator(".strategy-card")).toContainText("Momentum Alpha")
    await expect(page.locator(".header-meta")).toContainText("SOURCE: REAL")
  })

  test("strategy backtest page loads workbench shell and context", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest?strategyId=101&quickRun=1`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".backtest-analysis-page")).toBeVisible()
    await expect(page.getByRole("button", { name: "执行中枢" })).toBeVisible()
    await expect(page.locator(".context-strip")).toContainText("ID 101")
  })
})
