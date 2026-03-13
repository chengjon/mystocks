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
    localStorage.setItem("auth_token", "p1d-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  }, { user: E2E_USER })
}

async function mockRiskApis(page: Page) {
  await page.route("**/api/v1/monitoring/alert-rules**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: [],
        request_id: "p1d-risk-rules",
      }),
    })
  })

  await page.route("**/api/v1/monitoring/alerts**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: [],
        request_id: "p1d-risk-alerts",
      }),
    })
  })

  await page.route("**/api/v1/monitoring/watchlists**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        items: [],
        request_id: "p1d-risk-watchlists",
      }),
    })
  })
}

test.describe("P1-D Risk Mainline", () => {
  test.beforeEach(async ({ page }) => {
    await seedAuth(page)
    await mockRiskApis(page)
  })

  test("risk management container loads overview shell", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/risk/management`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".artdeco-page-template")).toBeVisible()
    await expect(page.locator(".custom-tabs")).toBeVisible()
    await expect(page.locator(".risk-overview-panel")).toContainText("风险预警列表")
  })

  test("risk overview page keeps summary shell with empty rules list", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/risk/overview`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".risk-overview-tab")).toBeVisible()
    await expect(page.locator(".stats-grid")).toBeVisible()
    await expect(page.locator(".tab-panel")).toBeVisible()
  })

  test("risk stop-loss page shows empty state on empty watchlists", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/risk/stop-loss`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".stop-loss-monitor-tab")).toBeVisible()
    await expect(page.locator(".state-panel")).toContainText("暂无止损监控数据")
  })

  test("risk alerts page renders empty tables under real-mode empty payload", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/risk/alerts`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".risk-alerts")).toBeVisible()
    await expect(page.locator(".table-card")).toHaveCount(2)
  })
})
