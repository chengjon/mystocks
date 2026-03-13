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
    localStorage.setItem("auth_token", "p1a-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  }, { user: E2E_USER })
}

test.describe("P1-A Market Data Pages", () => {
  test.beforeEach(async ({ page }) => {
    await seedAuth(page)
  })

  test("market lhb shows API-pending blocker shell", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/market/lhb`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".lhb-analysis-page")).toBeVisible()
    await expect(page.locator(".pending-state")).toContainText("API 真值待复核")
  })

  test("industry page shows empty state when sector flow API is empty", async ({ page }) => {
    await page.route("**/api/v2/market/sector/fund-flow**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: [],
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/data/industry`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".industry-analysis-page")).toBeVisible()
    await expect(page.locator(".empty-state")).toContainText("暂无板块数据")
  })

  test("concept page keeps real-mode empty state when hot concepts API is empty", async ({ page }) => {
    await page.route("**/api/data/markets/hot-concepts**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: [],
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/data/concept`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".market-concept-tab")).toBeVisible()
    await expect(page.locator(".empty-state")).toContainText("暂无概念板块数据")
  })

  test("fund-flow route can self-load and show empty state", async ({ page }) => {
    await page.route("**/api/akshare/market/fund-flow/hsgt-summary**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            hgt: { amount: 0, change: 0 },
            sgt: { amount: 0, change: 0 },
            northTotal: { amount: 0, monthly: 0 },
            mainForce: { amount: 0, percentage: 0 },
          },
        }),
      })
    })

    await page.route("**/api/akshare/market/fund-flow/big-deal**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: [],
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/data/fund-flow`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".fund-flow-route-page")).toBeVisible()
    await expect(page.locator(".empty-state")).toContainText("暂无资金流向数据")
  })

  test("indicator page shows pending blocker while editor upgrade is in progress", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/data/indicator`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".artdeco-data-analysis")).toBeVisible()
    await expect(page.locator(".analysis-blocker")).toContainText("指标接口真值待确认")
  })
})
