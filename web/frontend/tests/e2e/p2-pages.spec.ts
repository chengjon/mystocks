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
    localStorage.setItem("auth_token", "p2-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  }, { user: E2E_USER })
}

async function mockCommonP2Apis(page: Page) {
  await page.route("**/api/v1/trade/positions**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          positions: [],
        },
        request_id: "p2-positions",
      }),
    })
  })

  await page.route("**/api/v1/announcement/list**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          announcements: [],
        },
        request_id: "p2-announcements",
      }),
    })
  })

  await page.route("**/api/announcement/list**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          announcements: [],
        },
        request_id: "p2-announcements",
      }),
    })
  })

  await page.route("**/api/health/detailed**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: [],
        request_id: "p2-health-detailed",
        process_time: "18ms",
      }),
    })
  })

  await page.route("**/api/health", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          status: "healthy",
          service: "mystocks-backend",
          version: "2.0.0",
        },
        request_id: "p2-health",
        process_time: "12ms",
      }),
    })
  })

  await page.route("**/api/v1/data-sources/config/**", async (route) => {
    const method = route.request().method()
    if (method === "PUT") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: { saved: true },
          request_id: "p2-config-save",
        }),
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: [],
        request_id: "p2-config",
      }),
    })
  })

  await page.route("**/api/v1/strategy/strategies**", async (route) => {
    await route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({
        success: false,
        message: "strategy optimization unavailable",
        request_id: "p2-strategy-opt-error",
      }),
    })
  })

  await page.route("**/api/api/v1/strategy/strategies**", async (route) => {
    await route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({
        success: false,
        message: "strategy optimization unavailable",
        request_id: "p2-strategy-opt-error",
      }),
    })
  })
}

test.describe("P2 Page Hardening", () => {
  test.beforeEach(async ({ page }) => {
    await seedAuth(page)
    await mockCommonP2Apis(page)
  })

  test("strategy gpu shows API-pending blocker shell", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/strategy/gpu`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".backtest-gpu-dashboard")).toBeVisible()
    await expect(page.locator(".analysis-blocker")).toContainText("GPU 接口真值待确认")
  })

  test("strategy optimization keeps empty contract state when API fails", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/strategy/opt`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".strategy-optimization")).toBeVisible()
    await expect(page.locator(".error-tip")).toContainText("获取策略优化数据失败")
    await expect(page.locator(".optimization-table")).toHaveCount(0)
    await expect(page.locator(".empty-state")).toContainText("暂无可优化策略")
  })

  test("strategy positions shows empty state under empty positions payload", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/strategy/pos`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".portfolio-monitor")).toBeVisible()
    await expect(page.locator(".portfolio-monitor__state")).toContainText("暂无持仓监控数据")
  })

  test("risk news shows explicit empty state under empty announcements payload", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/risk/news`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".announcement-monitor")).toBeVisible()
    await expect(page.locator(".announcement-monitor__state")).toContainText("暂无公告数据")
  })

  test("system config shows pending blocker while keeping shell available", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/system/config`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".system-settings-page")).toBeVisible()
    await expect(page.locator(".analysis-blocker")).toContainText("系统配置接口真值待确认")
  })

  test("system health shows error state when health endpoint fails", async ({ page }) => {
    await page.route("**/api/health", async (route) => {
      await route.fulfill({
        status: 503,
        contentType: "application/json",
        body: JSON.stringify({
          success: false,
          message: "service unavailable",
          request_id: "p2-health-error",
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/system/health`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".system-health-tab")).toBeVisible()
    await expect(page.locator(".system-health-state")).toContainText("无法连接到后端服务")
  })

  test("system api shows explicit empty state when metrics payload is empty", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/system/api`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".monitoring-dashboard")).toBeVisible()
    await expect(page.locator(".monitoring-dashboard__state")).toContainText("暂无接口监控数据")
  })

  test("system data shows empty state when data source config list is empty", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/system/data`, { waitUntil: "domcontentloaded" })
    await expect(page.locator(".data-management")).toBeVisible()
    await expect(page.locator(".data-management__state")).toContainText("暂无数据源配置")
  })
})
