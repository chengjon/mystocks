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
    localStorage.setItem("auth_token", "p1e-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  }, { user: E2E_USER })
}

test.describe("P1-E Watchlist and Trade Edge Pages", () => {
  test.beforeEach(async ({ page }) => {
    await seedAuth(page)

    await page.route("**/api/watchlist**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: [],
          request_id: "p1e-watchlist",
        }),
      })
    })

    await page.route("**/api/v1/trade/trades**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            trades: [],
          },
          request_id: "p1e-trades",
        }),
      })
    })
  })

  test("watchlist manage shows empty state under empty watchlist payload", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/watchlist/manage`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".watchlist-manager-page")).toBeVisible()
    await expect(page.locator(".empty-state")).toContainText("暂无自选组合")
  })

  test("watchlist screener shows API-pending blocker shell", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/watchlist/screener`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".screener-shell")).toBeVisible()
    await expect(page.locator(".analysis-blocker")).toContainText("选股接口真值待确认")
  })

  test("trade terminal keeps dashboard shell available", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/trade/terminal`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".trading-dashboard")).toBeVisible()
    await expect(page.getByRole("button", { name: "刷新数据" })).toBeVisible()
  })

  test("trade history shows empty state when trade history payload is empty", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/trade/history`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".artdeco-trading-history")).toBeVisible()
    await expect(page.locator(".artdeco-trading-history__state")).toContainText("暂无交易历史数据")
  })
})
