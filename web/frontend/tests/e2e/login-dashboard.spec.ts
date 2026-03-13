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

async function mockDashboardApis(page: Page) {
  await page.route("**/api/v1/market/quotes**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: [
          { symbol: "000001.SH", name: "上证指数", latest_price: 3321.08, change_percent: 0.65, volume: 128000000 },
          { symbol: "399001.SZ", name: "深证成指", latest_price: 10214.2, change_percent: 0.71, volume: 102000000 },
          { symbol: "399006.SZ", name: "创业板指", latest_price: 2018.45, change_percent: 1.12, volume: 88000000 },
        ],
      }),
    })
  })

  await page.route("**/api/akshare/market/fund-flow/hsgt-summary**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          hgt: { amount: 18.3, change: 2.1 },
          sgt: { amount: 12.8, change: 1.4 },
          northTotal: { amount: 31.1, monthly: 182.4 },
          mainForce: { amount: 26.6, percentage: 57.2 },
        },
      }),
    })
  })

  await page.route("**/api/v2/market/sector/fund-flow**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: [
          { name: "半导体", change: 2.8, amount: 15.6 },
          { name: "算力", change: 2.1, amount: 12.2 },
          { name: "证券", change: 1.4, amount: 9.7 },
        ],
      }),
    })
  })

  await page.route("**/api/akshare/market/fund-flow/big-deal**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: [
          { code: "600519", name: "贵州茅台", amount: 8.3, change: 1.2 },
          { code: "300750", name: "宁德时代", amount: 6.1, change: 0.8 },
        ],
      }),
    })
  })

  await page.route("**/api/strategy-mgmt/strategies**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: [{ id: 1 }, { id: 2 }, { id: 3 }],
      }),
    })
  })

  await page.route("**/api/v1/risk/position/assessment**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          totalValue: 1280000,
          totalPnL: 32580,
          pnlPercent: 2.54,
          maxDrawdown: 4.8,
          riskLevel: "medium",
          riskLevelText: "中等",
        },
      }),
    })
  })

  await page.route("**/api/system/health**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: [
          { label: "API", value: "128ms", status: "good" },
          { label: "CPU", value: "42%", status: "good" },
        ],
      }),
    })
  })

  await page.route("**/api/indicators/calculate/batch**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          "000001.SH": [
            { name: "RSI", value: "58.2", trend: "rise", signal: "偏强" },
            { name: "MACD", value: "0.84", trend: "rise", signal: "金叉" },
          ],
        },
      }),
    })
  })
}

test.describe("P0-B Login and Dashboard", () => {
  test("renders login shell and visible validation banner", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/login`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".login-shell")).toBeVisible()
    await expect(page.getByTestId("username-input")).toBeVisible()
    await expect(page.getByTestId("password-input")).toBeVisible()
    await expect(page.getByTestId("login-button")).toBeVisible()

    await page.getByTestId("login-button").click()
    await expect(page.locator(".login-alert")).toContainText("请输入用户名和密码")
  })

  test("stores auth session and redirects to dashboard after successful login", async ({ page }) => {
    await mockDashboardApis(page)

    await page.route("**/api/v1/auth/login", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            token: "e2e-login-token",
            token_type: "bearer",
            user: E2E_USER,
          },
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/login`, { waitUntil: "domcontentloaded" })
    await page.getByTestId("username-input").fill("admin")
    await page.getByTestId("password-input").fill("admin123")
    await page.getByTestId("login-button").click()

    await page.waitForURL("**/dashboard", { timeout: 15000 })
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page.locator(".artdeco-dashboard")).toBeVisible()

    const token = await page.evaluate(() => localStorage.getItem("auth_token"))
    const user = await page.evaluate(() => localStorage.getItem("auth_user"))
    expect(token).toBe("e2e-login-token")
    expect(user).toContain("admin")
  })

  test("renders dashboard shell and refresh entry with mocked data", async ({ page }) => {
    await page.addInitScript(({ user }) => {
      localStorage.setItem("auth_token", "dashboard-shell-token")
      localStorage.setItem("auth_user", JSON.stringify(user))
    }, { user: E2E_USER })

    await mockDashboardApis(page)

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".artdeco-dashboard")).toBeVisible()
    await expect(page.getByRole("button", { name: "刷新数据" })).toBeVisible()
    await expect(page.locator(".header-metrics")).toContainText("策略运行中")
  })
})
